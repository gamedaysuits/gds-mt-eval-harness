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
# Language pair helpers
# ---------------------------------------------------------------------------

# ISO 639-3 shortcodes for common language names.
# Used to build compact pair codes like "en>crk" for the leaderboard.
#
# WHY THE NORMALIZATION:
#   The harness target_lang field often contains parenthetical annotations
#   like "Plains Cree (nêhiyawêwin, SRO)" or "French (Canada)". We strip
#   these before lookup so "Plains Cree (anything)" → "plains cree" → "crk".
_LANG_CODES = {
    "english": "en",
    "plains cree": "crk",
    "plains cree (sro)": "crk",
    "plains cree (nêhiyawêwin, sro)": "crk",
    "french": "fr",
    "french (canada)": "fr-ca",
    "spanish": "es",
    "german": "de",
    "japanese": "ja",
    "chinese": "zh",
    "arabic": "ar",
    "korean": "ko",
    "portuguese": "pt",
    "dutch": "nl",
    "vietnamese": "vi",
    "filipino": "fil",
}


def _normalize_lang_name(name: str) -> str:
    """Normalize a language name for lookup.

    Strips parenthetical annotations and extra whitespace:
        "Plains Cree (nêhiyawêwin, SRO)" → "plains cree"
    Also tries the full string (lowered) first for exact matches.
    """
    return name.strip().lower()


def _build_language_pair(config: dict) -> str:
    """Build a compact language pair string like 'en>crk' from config."""
    src = config.get("source_lang", "English").strip()
    tgt = config.get("target_lang", "").strip()

    src_lower = _normalize_lang_name(src)
    tgt_lower = _normalize_lang_name(tgt)

    # Try exact match first, then strip parenthetical and retry
    src_code = _LANG_CODES.get(src_lower)
    if src_code is None:
        src_base = src_lower.split("(")[0].strip()
        src_code = _LANG_CODES.get(src_base, src[:3].lower())

    tgt_code = _LANG_CODES.get(tgt_lower)
    if tgt_code is None:
        tgt_base = tgt_lower.split("(")[0].strip()
        tgt_code = _LANG_CODES.get(tgt_base, tgt[:3].lower())

    return f"{src_code}>{tgt_code}" if tgt_code else f"{src_code}>?"


# ---------------------------------------------------------------------------
# Git provenance
# ---------------------------------------------------------------------------

def _detect_git_provenance() -> dict | None:
    """Auto-detect git repo URL and commit hash.

    Runs from the harness's own directory. Returns None if git is
    unavailable or we're not inside a git repo.
    """
    import subprocess

    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if commit.returncode != 0:
            return None

        repo = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5,
        )

        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
        )

        return {
            "type": "git",
            "commit": commit.stdout.strip(),
            "repo": repo.stdout.strip() if repo.returncode == 0 else None,
            "dirty": bool(dirty.stdout.strip()) if dirty.returncode == 0 else None,
        }
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # git not installed or timed out
        return None


# ---------------------------------------------------------------------------
# Composite score — imports from scoring.py (code mirror of SCORING_SPEC §4)
# ---------------------------------------------------------------------------
# Weight tables, normalization rules, tier thresholds, and composite logic
# live in scoring.py — the single code authority that mirrors SCORING_SPEC.md.
# publish.py consumes these; it does not define its own.

from mt_eval_harness.scoring import (
    compute_composite_score,
    classify_quality_tier,
    cost_adjusted_score,
)


# ---------------------------------------------------------------------------
# Run Card assembly
# ---------------------------------------------------------------------------

def assemble_run_card(
    report_path: str | Path,
    method_card_path: str | Path | None = None,
) -> tuple[dict, str, str]:
    """Assemble a complete run card from a TestReport + its source RunLog.

    The run card is the atomic unit of evaluation defined in BENCHMARK_SPEC
    §3. It records the complete configuration, scores, cost, and speed of
    a single evaluation run: one method, one model, one configuration,
    one dataset.

    This function merges data from two sources:
        - The RunLog (raw results + config + provenance)
        - The TestReport (scored analysis: chrF++, BLEU, exact match, etc.)

    And computes:
        - Composite score (§4.2 weighted average)
        - Quality tier (§5 threshold classification)
        - Token aggregates (from per-entry usage data)
        - Latency percentiles (median, p95)
        - Fingerprint hash (§3.8 reproducibility identifier)
        - Run card hash (§3.9 tamper seal)

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

    # Provenance block (from runs using the updated pipeline.py).
    # Falls back to empty dict for legacy RunLogs that predate provenance.
    provenance = run_log.get("provenance", {})
    dataset_meta = provenance.get("dataset_meta", {})

    # Load method card if provided
    method_card = None
    if method_card_path:
        mc_path = Path(method_card_path)
        if not mc_path.exists():
            raise FileNotFoundError(f"Method card not found: {mc_path}")
        method_card = json.loads(mc_path.read_text(encoding="utf-8"))

    # -------------------------------------------------------------------
    # Token aggregation from per-entry usage data (§3.5)
    # -------------------------------------------------------------------
    results = run_log.get("results", [])

    prompt_tokens = 0
    completion_tokens = 0
    reasoning_tokens = 0
    cached_tokens = 0

    for r in results:
        usage = r.get("usage", {})
        prompt_tokens += usage.get("prompt_tokens", 0)
        completion_tokens += usage.get("completion_tokens", 0)
        # reasoning_tokens is nested under completion_tokens_details
        # in the OpenRouter response format
        ct_details = usage.get("completion_tokens_details", {})
        reasoning_tokens += ct_details.get("reasoning_tokens", 0)
        pt_details = usage.get("prompt_tokens_details", {})
        cached_tokens += pt_details.get("cached_tokens", 0)

    # -------------------------------------------------------------------
    # Latency percentiles (§3.6)
    # -------------------------------------------------------------------
    latencies = sorted(
        r.get("latency_s", 0)
        for r in results
        if not r.get("error")
    )
    n_latencies = len(latencies)

    avg_latency = round(sum(latencies) / n_latencies, 3) if n_latencies else None
    median_latency = round(
        latencies[n_latencies // 2], 3
    ) if n_latencies else None
    p95_latency = round(
        latencies[min(int(n_latencies * 0.95), n_latencies - 1)], 3
    ) if n_latencies else None

    # -------------------------------------------------------------------
    # FST acceptance — merge from plugin metrics or standalone FST report
    # -------------------------------------------------------------------
    plugin_metrics = overall.get("plugin_metrics", {})

    # Check TestReport plugin metrics first (integrated FST plugin)
    fst_acceptance_rate = None
    fst_accepted_count = None

    # Check multiple plugin names — the FST plugin was originally CRK-specific
    # (crk_fst_validity) but is now generic (giellalt_fst_validity) for all
    # languages with GiellaLT transducers.
    for fst_key in ("giellalt_fst_validity", "crk_fst_validity", "fst_analyzer"):
        fst_data = plugin_metrics.get(fst_key, {})
        if fst_data and not fst_data.get("error"):
            # giellalt_fst_validity and crk_fst_validity use avg_fst_validity;
            # legacy fst_analyzer uses acceptance_rate
            fst_acceptance_rate = (
                fst_data.get("avg_fst_validity")
                or fst_data.get("acceptance_rate")
            )
            fst_accepted_count = fst_data.get("accepted")
            break

    # If no FST data in TestReport, check for standalone _fst.json file
    # alongside the report (produced by crk-translate eval scripts)
    if fst_acceptance_rate is None:
        fst_report_path = report_path.with_name(
            report_path.stem.replace("_report", "_fst") + ".json"
        )
        if fst_report_path.exists():
            try:
                fst_report = json.loads(
                    fst_report_path.read_text(encoding="utf-8")
                )
                fst_acceptance_rate = fst_report.get(
                    "fst_overall_acceptance_rate"
                )
                fst_accepted_count = fst_report.get("fst_total_accepted")
            except (json.JSONDecodeError, KeyError):
                pass  # Malformed FST report — skip silently

    has_fst = fst_acceptance_rate is not None

    # -------------------------------------------------------------------
    # Extract equivalent_match_rate from CrkLinterMetric plugin (§4.2)
    #
    # CrkLinterMetric (crk_linter) computes per-entry variant-class
    # analysis and aggregates to an equivalent_match_rate: the fraction
    # of entries that are exact OR acceptable-variant matches.
    # When available, this replaces the generic null placeholder.
    # -------------------------------------------------------------------
    equivalent_match_rate = None
    equivalent_match_count = None

    linter_data = plugin_metrics.get("crk_linter", {})
    if linter_data and not linter_data.get("error"):
        equivalent_match_rate = linter_data.get("equivalent_match_rate")
        # Derive count from rate × total entries for the scores block
        if equivalent_match_rate is not None:
            evaluated = overall.get("evaluated", 0)
            equivalent_match_count = round(equivalent_match_rate * evaluated)

    # -------------------------------------------------------------------
    # Extract semantic_score from CrkSemanticMetric plugin (§4.2)
    #
    # CrkSemanticMetric (crk_semantic) produces per-entry verdicts:
    #   EXACT_MATCH, VALID, GRAMMAR_ISSUES, PARTIAL, INCOMPLETE, WRONG,
    #   NO_OUTPUT, ERROR
    #
    # We derive a numeric 0.0–1.0 semantic score by assigning each
    # verdict a weight reflecting semantic fidelity:
    #   EXACT_MATCH  → 1.0  (identical output)
    #   VALID        → 1.0  (correct lemmas, inflection/order variation)
    #   GRAMMAR_ISSUES  → 0.7  (right lemmas, structural grammar issues)
    #   PARTIAL      → 0.4  (some correct, some missing/wrong)
    #   INCOMPLETE   → 0.3  (compressed — missing content)
    #   WRONG        → 0.0  (genuinely incorrect lemma choices)
    #   NO_OUTPUT    → 0.0  (nothing generated)
    #   ERROR        → 0.0  (validation itself failed)
    #
    # These weights reflect the semantic validator's design: VALID means
    # identical lemma sets (only inflection differs), GRAMMAR_ISSUES means
    # correct lemmas but sentence-level grammar issues, PARTIAL means
    # mixed results. The weights are conservative — community review
    # remains the ultimate arbiter.
    # -------------------------------------------------------------------
    semantic_score = None

    _SEMANTIC_VERDICT_WEIGHTS = {
        "EXACT_MATCH": 1.0,
        "VALID": 1.0,
        "GRAMMAR_ISSUES": 0.7,
        "PARTIAL": 0.4,
        "INCOMPLETE": 0.3,
        "WRONG": 0.0,
        "NO_OUTPUT": 0.0,
        "ERROR": 0.0,
    }

    semantic_data = plugin_metrics.get("crk_semantic", {})
    if semantic_data and not semantic_data.get("error"):
        verdict_counts = semantic_data.get("semantic_verdict_counts", {})
        if verdict_counts:
            total_judged = sum(verdict_counts.values())
            if total_judged > 0:
                weighted_sum = sum(
                    count * _SEMANTIC_VERDICT_WEIGHTS.get(verdict, 0.0)
                    for verdict, count in verdict_counts.items()
                )
                semantic_score = round(weighted_sum / total_judged, 4)

    # -------------------------------------------------------------------
    # Extract behavioral metrics from plugin aggregates
    #
    # These are computed by language-agnostic plugins (CodeSwitching,
    # Hallucination, Terminology) and need to be fed into the composite.
    # scoring.py handles the inversion (1 - rate) for code_switching and
    # hallucination, so we pass raw rates here.
    # -------------------------------------------------------------------
    code_switching_rate = None
    cs_data = plugin_metrics.get("code_switching", {})
    if cs_data and not cs_data.get("error"):
        code_switching_rate = cs_data.get("avg_code_switching_rate")

    hallucination_rate = None
    hall_data = plugin_metrics.get("hallucination", {})
    if hall_data and not hall_data.get("error"):
        hallucination_rate = hall_data.get("avg_hallucination_rate")

    terminology_adherence = None
    term_data = plugin_metrics.get("terminology", {})
    if term_data and not term_data.get("error"):
        terminology_adherence = term_data.get("avg_terminology_adherence")

    # -------------------------------------------------------------------
    # Composite score (SCORING_SPEC §4)
    # -------------------------------------------------------------------
    # Build a dict of available metrics in their NATIVE scales.
    # scoring.py handles normalization (chrF++ ÷ 100, inversions)
    # internally — we pass raw values here.
    corpus_chrf = overall.get("corpus_chrf")
    composite_inputs = {
        # chrF++ in sacrebleu native 0–100 scale; scoring.py normalizes
        "chrf_plus_plus": corpus_chrf,
        "exact_match_rate": overall.get("exact_match_rate"),
        "fst_acceptance_rate": fst_acceptance_rate,
        # LYSS-eq: wired from CrkLinterMetric when available, else None
        "equivalent_match_rate": equivalent_match_rate,
        # LYSS-sem: wired from CrkSemanticMetric when available, else None
        "semantic_score": semantic_score,
        # Behavioral metrics — wired from plugin aggregates
        "code_switching_rate": code_switching_rate,
        "hallucination_rate": hallucination_rate,
        "terminology_adherence": terminology_adherence,
        # Planned — requires per-entry gold-standard morphological annotations
        "morphological_accuracy": None,
    }

    composite = compute_composite_score(composite_inputs, has_fst=has_fst)
    quality_tier = classify_quality_tier(composite)

    # -------------------------------------------------------------------
    # Cost
    # -------------------------------------------------------------------
    total_cost_usd = run_log.get("total_cost_usd", 0)
    entry_count = overall.get("total_entries", 0)
    cost_per_entry = round(
        total_cost_usd / entry_count, 6
    ) if entry_count else None

    # -------------------------------------------------------------------
    # Assemble the run card (BENCHMARK_SPEC §3)
    # -------------------------------------------------------------------

    # Detect git provenance from the harness repo
    git_provenance = _detect_git_provenance()

    run_card = {
        # §3.1 Top-level
        "run_id": run_log.get("run_id", ""),
        "harness_version": run_log.get("harness_version", ""),
        "timestamp": run_log.get("timestamp_start", ""),
        "elapsed_seconds": run_log.get("elapsed_s"),

        # §3.2 Method configuration
        # All parameters that could affect translation quality are recorded
        # here so that published results can be fully understood and compared.
        "model_slug": config.get("model", ""),
        "model_id": config.get("_model_id", config.get("model", "")),
        "condition": config.get("prompt_version", ""),
        "temperature": config.get("_effective_temperature",
                                  config.get("temperature", 0)),
        "max_tokens": config.get("max_tokens"),
        "system_prompt_sha256": provenance.get("system_prompt_sha256", ""),
        "system_prompt_used": provenance.get("system_prompt_used", ""),
        "coaching_data_sha256": None,  # populated when coaching is used
        "fst_version": None,  # populated when FST plugin is registered
        "tools_enabled": config.get("tools_enabled", False),
        "batch_size": config.get("batch_size", 25),
        "concurrency": config.get("concurrency"),

        # §3.3 Dataset reference
        "dataset": {
            "id": config.get("dataset_id", "") or config.get("dataset", ""),
            "version": dataset_meta.get("version", None),
            "language_pair": _build_language_pair(config),
            "source_lang": config.get("source_lang", ""),
            "target_lang": config.get("target_lang", ""),
            "sha256": provenance.get("corpus_sha256", ""),
            "entry_count": entry_count,
        },

        # §3.4 Scores (quality) — all automated metrics, see §1.1
        "scores": {
            "total": entry_count,
            "evaluated": overall.get("evaluated", 0),
            "exact_matches": overall.get("exact_match_count", 0),
            "exact_match_rate": overall.get("exact_match_rate", 0),
            # Wired from CrkLinterMetric: exact OR acceptable-variant matches
            "equivalent_matches": equivalent_match_count,
            "equivalent_match_rate": equivalent_match_rate,
            "fst_accepted": fst_accepted_count,
            "fst_acceptance_rate": fst_acceptance_rate,
            "morphological_accuracy": None,      # 🔲 planned — requires gold annotations
            "chrf_plus_plus": corpus_chrf,
            # Wired from CrkSemanticMetric: weighted verdict score (0.0–1.0)
            "semantic_score": semantic_score,
            "composite": composite,
            "quality_tier": quality_tier,
            "errors": overall.get("error_count", 0),
            "by_difficulty": report.get("by_difficulty", {}),
            "by_domain": report.get("by_domain", {}),
            "by_provenance": {},                 # not yet tracked
            # Latency stats (§3.6)
            "avg_latency_seconds": avg_latency,
            "median_latency_seconds": median_latency,
            "p95_latency_seconds": p95_latency,
        },

        # §3.5 Totals (cost)
        "totals": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "reasoning_tokens": reasoning_tokens,
            "cached_tokens": cached_tokens,
            "total_cost_usd": total_cost_usd,
            "cost_per_entry_usd": cost_per_entry,
        },

        # Additional context
        "cache_hits": run_log.get("cache_hits", 0),
        "by_segment": report.get("by_segment", {}),
        "provenance": git_provenance,
        "method_card": method_card,

        # §3.7 Canonical MethodConfig — the exact config shape used by
        # champollion.config.json, method.json, and export-config.
        # Leaderboard --install reads this block directly so the installed
        # plugin uses the exact same config that produced these results.
        "method_config": {
            "model": config.get("_model_id", config.get("model", "")),
            "temperature": config.get("_effective_temperature",
                                      config.get("temperature", 0)),
            "batchSize": config.get("batch_size", 25),
            "register": provenance.get("register_used", None),
            "coachingFile": config.get("coaching_file", None),
            "coachingPrompt": None,  # Resolved at runtime — not persisted
            "promptContext": provenance.get("prompt_context_used", None),
            "qualityTier": quality_tier,
        },

        # Additional scores not in spec but useful
        "corpus_bleu": overall.get("corpus_bleu"),
    }

    # Add COMET score if computed
    if overall.get("comet_score") is not None:
        run_card["scores"]["comet_score"] = overall["comet_score"]
        run_card["scores"]["comet_model"] = overall.get("comet_model", "")
        run_card["scores"]["comet_low_resource_warning"] = overall.get(
            "comet_low_resource_warning", False
        )
    else:
        run_card["scores"]["comet_score"] = None

    # Add bootstrap confidence intervals if computed
    cis = overall.get("confidence_intervals", {})
    if cis:
        run_card["scores"]["confidence_intervals"] = cis

    # -------------------------------------------------------------------
    # Fingerprint — deterministic identity for deduplication (§3.8)
    #
    # Per BENCHMARK_SPEC §3.8, the fingerprint is the SHA-256 of:
    #   dataset.sha256 + model_slug + condition + system_prompt_sha256
    #   + temperature + harness_version
    #
    # Two runs with identical fingerprints used the same experimental
    # setup. Differences are due to API non-determinism or provider
    # model updates.
    # -------------------------------------------------------------------
    # batch_size and tools_enabled are included because they materially
    # affect output quality — a batch_size=25 run produces different
    # translations than batch_size=1, and tool-augmented runs use a
    # fundamentally different prompting strategy.
    fingerprint_components = {
        "dataset_sha256": run_card["dataset"]["sha256"],
        "model_slug": run_card["model_slug"],
        "condition": run_card["condition"],
        "system_prompt_sha256": run_card["system_prompt_sha256"],
        "temperature": run_card["temperature"],
        "batch_size": run_card["batch_size"],
        "tools_enabled": run_card["tools_enabled"],
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

    # -------------------------------------------------------------------
    # Run card hash — tamper seal (§3.9)
    # Computed AFTER fingerprint is set but BEFORE the hash field itself.
    # -------------------------------------------------------------------
    run_card["run_card_hash"] = ""  # placeholder so JSON structure is stable
    card_json = json.dumps(run_card, sort_keys=True, ensure_ascii=False)
    run_card["run_card_hash"] = hashlib.sha256(card_json.encode()).hexdigest()

    # -------------------------------------------------------------------
    # Deterministic UUID — derived from the fingerprint hash.
    # Same experiment always gets the same UUID → upsert deduplicates.
    # -------------------------------------------------------------------
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
    auto_confirm: bool = False,
) -> dict:
    """Authenticate, assemble a run card, and publish to the leaderboard.

    This is the main entry point for the 'mt-eval publish' command.

    Args:
        report_path: Path to the TestReport JSON file.
        method_card_path: Optional path to a method card JSON file.
        auto_confirm: If True, skip the confirmation prompt (for
                      scripted/batch publishing via --yes).

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

    # --- Method card wizard ---
    # If no method card was provided and we're interactive, offer the wizard.
    # The wizard creates a method card dict that gets embedded in the run card.
    if method_card_path is None and not auto_confirm:
        if "method_card" not in run_card or run_card.get("method_card") is None:
            print("\n  No method card attached to this run.")
            offer = input("  Create one now? [Y/n] ").strip().lower()
            if not offer or offer == "y":
                from mt_eval_harness.method_card_wizard import run_wizard
                card = run_wizard(submitter=submitter)
                if card:
                    run_card["method_card"] = card
                    run_card["condition"] = card.get("class", run_card.get("condition", "unknown"))

    scores = run_card["scores"]
    dataset = run_card["dataset"]
    totals = run_card["totals"]

    # --- Build the Supabase row ---
    # Percentages: the leaderboard displays these as "X%" so we store 0–100
    exact_match_pct = _to_percentage(scores["exact_match_rate"])
    fst_pct = None
    if scores.get("fst_acceptance_rate") is not None:
        fst_pct = _to_percentage(scores["fst_acceptance_rate"])

    # Extract CIs from the run card scores (added by tester.py)
    cis = scores.get("confidence_intervals", {})

    row = {
        "id": card_id,
        "submitter": submitter,
        "affirmation": (
            f"Results generated by mt-eval harness v{run_card['harness_version']} "
            f"and submitted by {submitter} via CLI."
        ),
        # Trust tiers: self-benchmarked, gds-verified, community-validated
        # CLI submissions are always self-benchmarked; elevated tiers are
        # granted through manual review.
        "trust": "self-benchmarked",
        "model_slug": run_card["model_slug"],
        "condition": run_card["condition"],
        "dataset_id": dataset["id"],
        "language_pair": dataset.get("language_pair", "en>crk"),
        "harness_version": run_card["harness_version"],
        "chrf_plus_plus": scores.get("chrf_plus_plus"),
        "corpus_bleu": run_card.get("corpus_bleu"),
        "exact_match_rate": exact_match_pct,
        "fst_acceptance_rate": fst_pct,
        # Equivalent match rate — from CrkLinterMetric (nullable)
        "equivalent_match_rate": (
            _to_percentage(scores["equivalent_match_rate"])
            if scores.get("equivalent_match_rate") is not None else None
        ),
        # Semantic score — from CrkSemanticMetric (nullable, 0.0–1.0)
        "semantic_score": scores.get("semantic_score"),
        # Composite score and quality tier (§4.2, §5)
        "composite_score": scores.get("composite"),
        "quality_tier": scores.get("quality_tier"),
        # COMET — nullable, None if unbabel-comet is not installed
        "comet_score": scores.get("comet_score"),
        # Confidence intervals — nullable numeric fields
        "chrf_ci_lower": cis.get("corpus_chrf", {}).get("ci_lower") if cis else None,
        "chrf_ci_upper": cis.get("corpus_chrf", {}).get("ci_upper") if cis else None,
        "exact_match_ci_lower": cis.get("exact_match_rate", {}).get("ci_lower") if cis else None,
        "exact_match_ci_upper": cis.get("exact_match_rate", {}).get("ci_upper") if cis else None,
        "fst_ci_lower": cis.get("fst_acceptance_rate", {}).get("ci_lower") if cis else None,
        "fst_ci_upper": cis.get("fst_acceptance_rate", {}).get("ci_upper") if cis else None,
        "composite_ci_lower": cis.get("composite_score", {}).get("ci_lower") if cis else None,
        "composite_ci_upper": cis.get("composite_score", {}).get("ci_upper") if cis else None,
        # Cost + timing
        "total_cost_usd": totals["total_cost_usd"],
        "cost_per_entry_usd": totals.get("cost_per_entry_usd"),
        "elapsed_seconds": run_card.get("elapsed_seconds"),
        "avg_latency_seconds": scores.get("avg_latency_seconds"),
        "corpus_size": scores.get("total"),
        # Full run card JSON — the complete record
        "run_card": run_card,
        "fingerprint_hash": fingerprint_hash,
        "api_provider": "openrouter",
        "run_timestamp": run_card.get("timestamp"),
        # Quality-affecting parameters as top-level columns for
        # leaderboard filtering and sorting. These are also in
        # the run_card JSON but top-level columns enable SQL queries.
        "batch_size": run_card.get("batch_size"),
        "temperature": run_card.get("temperature"),
        "max_tokens": run_card.get("max_tokens"),
    }

    # --- Preview ---
    print(f"\n  Submitter:     {submitter}")
    print(f"  Model:         {run_card['model_slug']}")
    print(f"  Condition:     {run_card['condition']}")
    print(f"  Batch size:    {run_card.get('batch_size', '?')}")
    print(f"  Temperature:   {run_card.get('temperature', '?')}")
    print(f"  Max tokens:    {run_card.get('max_tokens', '?')}")
    print(f"  Dataset:       {dataset['id']} ({scores.get('total', '?')} entries)")
    # Show entry count — entries will be stored individually in run_card_entries
    report_data = json.loads(Path(report_path).read_text(encoding="utf-8"))
    entry_count = len(report_data.get("entries", []))
    if entry_count:
        print(f"  Entries:       {entry_count} (will be stored individually)")
    print(f"  chrF++:        {scores.get('chrf_plus_plus', 'N/A')}")
    if cis and cis.get("corpus_chrf"):
        ci = cis["corpus_chrf"]
        print(f"    95% CI:      [{ci['ci_lower']:.1f} – {ci['ci_upper']:.1f}]")
    print(f"  BLEU:          {run_card.get('corpus_bleu', 'N/A')}")
    if scores.get("comet_score") is not None:
        warning = " ⚠️  low-resource" if scores.get("comet_low_resource_warning") else ""
        print(f"  COMET:         {scores['comet_score']:.4f}{warning}")
    print(f"  Exact Match:   {exact_match_pct}%")
    if scores.get("equivalent_match_rate") is not None:
        equiv_pct = _to_percentage(scores["equivalent_match_rate"])
        print(f"  Equiv Match:   {equiv_pct}%")
    if fst_pct is not None:
        print(f"  FST Accept:    {fst_pct}%")
    if scores.get("semantic_score") is not None:
        print(f"  Semantic:      {scores['semantic_score']:.4f}")
    composite = scores.get("composite")
    if composite is not None:
        print(f"  Composite:     {composite:.4f} ({scores.get('quality_tier', 'unscored')})")
    print(f"  Cost:          ${totals['total_cost_usd']:.4f}")
    if totals.get("cost_per_entry_usd"):
        print(f"  Cost/entry:    ${totals['cost_per_entry_usd']:.6f}")
    print(f"  Fingerprint:   {fingerprint_hash[:16]}...")
    print(f"  UUID:          {card_id}")

    # --- Confirm ---
    if auto_confirm:
        print("\n  Auto-confirmed (--yes)")
    else:
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

    # --- Publish per-entry data ---
    # Load entries from the report and batch-insert into run_card_entries.
    # This enables per-entry drill-down on the leaderboard website.
    report_data = json.loads(Path(report_path).read_text(encoding="utf-8"))
    entries = report_data.get("entries", [])

    if entries:
        print(f"  Publishing {len(entries)} per-entry results...")
        _publish_entries(
            card_id=card_id,
            entries=entries,
            access_token=access_token,
        )
    else:
        print("  ℹ No per-entry data found in report (entries list empty)")

    print(f"     https://mtevalarena.org/leaderboard")
    print("=" * 60)

    return result


def _publish_entries(
    card_id: str,
    entries: list[dict],
    access_token: str,
) -> None:
    """Batch-insert per-entry results into run_card_entries.

    Uses Supabase's upsert (ON CONFLICT) so re-publishes are idempotent.
    Entries are sent in batches of 50 to avoid request size limits.

    Args:
        card_id: The run_card ID (foreign key).
        entries: List of entry dicts from the TestReport.
        access_token: Supabase JWT for authenticated writes.
    """
    BATCH_SIZE = 50

    # Transform report entries into run_card_entries rows
    rows = []
    for entry in entries:
        row = {
            "run_card_id": card_id,
            "entry_id": str(entry.get("id", "")),
            "source": entry.get("source", ""),
            "expected": entry.get("expected", ""),
            "raw_predicted": entry.get("raw_predicted"),
            "predicted": entry.get("predicted", ""),
            "segment": entry.get("segment", ""),
            "difficulty": entry.get("difficulty"),
            "domain": entry.get("domain", ""),
            "exact_match": bool(entry.get("exact_match", False)),
            "chrf_score": entry.get("chrf_score"),
            "bleu_score": entry.get("bleu_score"),
            "latency_s": entry.get("latency_s"),
            "cost_usd": entry.get("cost_usd"),
            "tool_call_count": entry.get("tool_call_count", 0),
            "error": entry.get("error"),
            "plugin_metrics": entry.get("plugin_metrics", {}),
        }
        rows.append(row)

    # Batch insert — send rows in chunks to avoid payload limits
    total_inserted = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        data = json.dumps(batch).encode()

        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/run_card_entries",
            data=data,
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                # Upsert on (run_card_id, entry_id) for idempotent re-publishes
                "Prefer": "resolution=merge-duplicates",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp.read()  # Consume response
            total_inserted += len(batch)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode()
            # Warn but don't fail — the run_card is already published.
            # Per-entry data is secondary; we can retry later.
            print(
                f"  ⚠ Entry batch {i // BATCH_SIZE + 1} failed "
                f"({exc.code}): {body[:200]}"
            )

    if total_inserted > 0:
        print(f"  ✅ {total_inserted}/{len(rows)} entries published")

