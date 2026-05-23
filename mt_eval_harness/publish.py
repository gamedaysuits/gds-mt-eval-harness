"""
Publish — Assemble run cards from TestReports and submit to the leaderboard.

This is the final step in the eval pipeline:
    mt-eval run   →  RunLog      (raw translations)
    mt-eval test  →  TestReport  (scored results)
    mt-eval publish → Supabase   (leaderboard entry)

The publish command:
    1. Reads a TestReport JSON and its source RunLog
    2. Assembles a Run Card (config + scores + provenance)
    3. Computes a fingerprint hash (deterministic identity)
    4. Computes a run_card_hash (tamper seal)
    5. Derives a deterministic UUID from the fingerprint
    6. Authenticates via OAuth (GitHub or Google)
    7. Upserts the row to Supabase (deduplicated by fingerprint)
"""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from mt_eval_harness.auth import (
    SUPABASE_URL,
    SUPABASE_ANON_KEY,
    get_session,
    get_submitter_name,
)


# ---------------------------------------------------------------------------
# Run Card assembly
# ---------------------------------------------------------------------------

# ISO 639-3 shortcodes for common language names.
# Used to build compact pair codes like "en>crk" for the leaderboard.
_LANG_CODES = {
    "english": "en",
    "plains cree": "crk",
    "plains cree (sro)": "crk",
    "french": "fr",
    "spanish": "es",
    "german": "de",
}


def _build_language_pair(config: dict) -> str:
    """Build a compact language pair string like 'en>crk' from config."""
    src = config.get("source_lang", "English").strip()
    tgt = config.get("target_lang", "").strip()

    src_code = _LANG_CODES.get(src.lower(), src[:3].lower())
    tgt_code = _LANG_CODES.get(tgt.lower(), tgt[:3].lower())

    return f"{src_code}>{tgt_code}" if tgt_code else f"{src_code}>?"

def assemble_run_card(
    report_path: str | Path,
    method_card_path: str | Path | None = None,
) -> tuple[dict, str, str]:
    """Assemble a complete run card from a TestReport + its source RunLog.

    Args:
        report_path: Path to the TestReport JSON.
        method_card_path: Optional path to a method card JSON.

    Returns:
        (run_card, deterministic_uuid, fingerprint_hash) tuple.

    Raises:
        FileNotFoundError if the report or its source RunLog is missing.
    """
    report_path = Path(report_path)
    report = json.loads(report_path.read_text(encoding="utf-8"))

    # Load the source RunLog.
    # First try the path recorded in the report, then fall back to
    # deriving it from the report filename (foo_report.json → foo.json).
    source_log_path = None
    if report.get("source_log"):
        candidate = Path(report["source_log"])
        if candidate.exists():
            source_log_path = candidate

    if source_log_path is None:
        # Convention: report is <run_id>_report.json, run log is <run_id>.json
        inferred = report_path.with_name(
            report_path.stem.replace("_report", "") + ".json"
        )
        if inferred.exists():
            source_log_path = inferred

    if source_log_path is None:
        raise FileNotFoundError(
            f"Source RunLog not found.\n"
            f"  Tried: {report.get('source_log', '(not set)')}\n"
            f"  And:   {report_path.stem.replace('_report', '')}.json"
        )

    run_log = json.loads(source_log_path.read_text(encoding="utf-8"))
    config = run_log.get("config", {})
    overall = report.get("overall", {})

    # Load method card if provided
    method_card = None
    if method_card_path:
        mc_path = Path(method_card_path)
        if not mc_path.exists():
            raise FileNotFoundError(f"Method card not found: {mc_path}")
        method_card = json.loads(mc_path.read_text(encoding="utf-8"))

    # -----------------------------------------------------------------------
    # Assemble the run card
    # -----------------------------------------------------------------------
    run_card = {
        "run_id": run_log.get("run_id", ""),
        "harness_version": run_log.get("harness_version", ""),
        "model_slug": config.get("model", ""),
        "model_id": config.get("_model_id", config.get("model", "")),
        "condition": config.get("prompt_version", ""),
        "timestamp": run_log.get("timestamp_start", ""),
        "elapsed_seconds": run_log.get("elapsed_s"),
        "dataset": {
            # Prefer dataset_id (metadata label) over dataset (filter)
            "id": config.get("dataset_id", "") or config.get("dataset", ""),
            "language_pair": _build_language_pair(config),
            "entry_count": overall.get("total_entries", 0),
        },
        "config": {
            "api_provider": "openrouter",
            "temperature": config.get("temperature", 0.3),
            "max_tokens": config.get("max_tokens", 4096),
            "batch_size": config.get("batch_size", 25),
            "concurrency": config.get("concurrency", 5),
            "cache_enabled": config.get("cache_enabled", True),
            "tools_enabled": config.get("tools_enabled", False),
        },
        "scores": {
            "total": overall.get("total_entries", 0),
            "evaluated": overall.get("evaluated", 0),
            "exact_matches": overall.get("exact_match_count", 0),
            # exact_match_rate is 0.0–1.0 in the TestReport
            "exact_match_rate": overall.get("exact_match_rate", 0),
            "corpus_chrf": overall.get("corpus_chrf", 0),
            "corpus_bleu": overall.get("corpus_bleu", 0),
            "avg_chrf": overall.get("avg_chrf", 0),
            "errors": overall.get("error_count", 0),
        },
        "cost": {
            "total_usd": run_log.get("total_cost_usd", 0),
        },
        "method_card": method_card,
        "by_segment": report.get("by_segment", {}),
        "by_difficulty": report.get("by_difficulty", {}),
    }

    # Add FST acceptance rate if the plugin ran
    plugin_metrics = overall.get("plugin_metrics", {})
    fst_data = plugin_metrics.get("fst_analyzer", {})
    if fst_data and not fst_data.get("error"):
        run_card["scores"]["fst_accepted"] = fst_data.get("accepted", 0)
        run_card["scores"]["fst_acceptance_rate"] = fst_data.get(
            "acceptance_rate", 0
        )

    # -----------------------------------------------------------------------
    # Fingerprint — deterministic identity for deduplication
    # Two runs with the same fingerprint are the "same experiment."
    # -----------------------------------------------------------------------
    fingerprint_components = {
        "model_slug": run_card["model_slug"],
        "condition": run_card["condition"],
        "dataset_id": run_card["dataset"]["id"],
        "temperature": run_card["config"]["temperature"],
        "harness_version": run_card["harness_version"],
    }

    fp_json = json.dumps(
        fingerprint_components, sort_keys=True, ensure_ascii=False
    )
    fingerprint_hash = hashlib.sha256(fp_json.encode()).hexdigest()

    run_card["fingerprint"] = {
        "hash": fingerprint_hash,
        "components": fingerprint_components,
    }

    # -----------------------------------------------------------------------
    # Run card hash — tamper seal
    # Computed AFTER fingerprint is set but BEFORE the hash field itself.
    # -----------------------------------------------------------------------
    run_card["run_card_hash"] = ""  # placeholder so JSON structure is stable
    card_json = json.dumps(run_card, sort_keys=True, ensure_ascii=False)
    run_card["run_card_hash"] = hashlib.sha256(card_json.encode()).hexdigest()

    # -----------------------------------------------------------------------
    # Deterministic UUID — derived from the fingerprint hash
    # Same experiment always gets the same UUID → upsert deduplicates
    # -----------------------------------------------------------------------
    card_id = str(uuid.uuid5(uuid.NAMESPACE_URL, fingerprint_hash))

    return run_card, card_id, fingerprint_hash


# ---------------------------------------------------------------------------
# Supabase upsert
# ---------------------------------------------------------------------------

def _to_percentage(rate: float) -> float:
    """Convert a 0.0–1.0 rate to a 0–100 percentage for display.

    Handles the case where the rate is already in percentage form
    (i.e., > 1.0) by returning it as-is.
    """
    if rate > 1.0:
        return round(rate, 1)
    return round(rate * 100, 1)


def publish_to_supabase(
    report_path: str | Path,
    method_card_path: str | Path | None = None,
) -> dict:
    """Authenticate, assemble a run card, and publish to the leaderboard.

    This is the main entry point for the 'mt-eval publish' command.

    Args:
        report_path: Path to the TestReport JSON file.
        method_card_path: Optional path to a method card JSON file.

    Returns:
        The upserted Supabase row as a dict.

    Raises:
        SystemExit on auth failure or Supabase errors.
    """
    # --- Authenticate ---
    print("=" * 60)
    print("MT Eval Harness — Publish to Leaderboard")
    print("=" * 60)

    session = get_session()
    access_token = session["access_token"]
    submitter = get_submitter_name(session)

    # --- Assemble run card ---
    print("\n  Assembling run card...")
    run_card, card_id, fingerprint_hash = assemble_run_card(
        report_path, method_card_path
    )

    scores = run_card["scores"]
    dataset = run_card["dataset"]

    # --- Build the Supabase row ---
    # Percentages: the leaderboard displays these as "X%" so we store 0–100
    exact_match_pct = _to_percentage(scores["exact_match_rate"])
    fst_pct = None
    if "fst_acceptance_rate" in scores:
        fst_pct = _to_percentage(scores["fst_acceptance_rate"])

    row = {
        "id": card_id,
        "submitter": submitter,
        "affirmation": (
            f"Results generated by mt-eval harness v{run_card['harness_version']} "
            f"and submitted by {submitter} via CLI."
        ),
        # The run_cards_trust_check constraint currently only accepts
        # 'verified'. The three-tier system (self-benchmarked, gds-verified,
        # community-validated) needs a Supabase-side constraint update.
        "trust": "verified",
        "model_slug": run_card["model_slug"],
        "condition": run_card["condition"],
        "dataset_id": dataset["id"],
        "language_pair": dataset.get("language_pair", "en>crk"),
        "harness_version": run_card["harness_version"],
        "chrf_plus_plus": scores.get("corpus_chrf"),
        "exact_match_rate": exact_match_pct,
        "fst_acceptance_rate": fst_pct,
        "total_cost_usd": run_card["cost"]["total_usd"],
        "elapsed_seconds": run_card.get("elapsed_seconds"),
        "corpus_size": scores.get("total"),
        "run_card": run_card,
        "fingerprint_hash": fingerprint_hash,
        "run_timestamp": run_card.get("timestamp"),
    }

    # --- Preview ---
    print(f"\n  Submitter:     {submitter}")
    print(f"  Model:         {run_card['model_slug']}")
    print(f"  Condition:     {run_card['condition']}")
    print(f"  Dataset:       {dataset['id']} ({scores.get('total', '?')} entries)")
    print(f"  chrF++:        {scores.get('corpus_chrf', 'N/A')}")
    print(f"  Exact Match:   {exact_match_pct}%")
    if fst_pct is not None:
        print(f"  FST Accept:    {fst_pct}%")
    print(f"  Cost:          ${run_card['cost']['total_usd']:.4f}")
    print(f"  Fingerprint:   {fingerprint_hash[:16]}...")
    print(f"  UUID:          {card_id}")

    # --- Confirm ---
    confirm = input("\n  Publish these results? [Y/n] ").strip().lower()
    if confirm and confirm != "y":
        print("  Cancelled.")
        raise SystemExit(0)

    # --- Upsert ---
    print("\n  Publishing...")
    data = json.dumps(row).encode()
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/run_cards",
        data=data,
        headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            # Upsert: if a row with the same id exists, update it.
            # This handles re-runs of the same experiment gracefully.
            "Prefer": "resolution=merge-duplicates,return=representation",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        print(f"\n  ❌ Publish failed ({exc.code}): {body}")
        raise SystemExit(1)

    print(f"\n  ✅ Published to leaderboard!")
    print(f"     https://i18n-rosetta.com/leaderboard")
    print("=" * 60)

    return result
