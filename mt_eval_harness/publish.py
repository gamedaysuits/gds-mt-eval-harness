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
import time
import urllib.error
import urllib.parse
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
# Language pair helpers — uses language_cards SSOT
# ---------------------------------------------------------------------------
#
# Previously contained a hardcoded 17-entry _LANG_CODES dict that could
# only resolve names for a handful of languages. Deleted in v8 — all
# resolution now goes through language_cards which indexes all 7,928 cards.

from mt_eval_harness.language_cards import (
    resolve_code as _lc_resolve_code,
    resolve_name as _lc_resolve_name,
)


def _resolve_lang_to_code(name_or_code: str) -> str:
    """Resolve a language name or code to its ISO 639-3 code.

    Tries multiple strategies via the language_cards SSOT:
        1. Direct code/alias resolution (e.g., "fr" → "fra", "crk" → "crk")
        2. Name resolution (e.g., "French" → "fra", "Plains Cree" → "crk")
        3. Name with parenthetical stripped (e.g., "French (Canada)" → "fra")
        4. Fallback: first 3 chars lowered

    This replaces the old hardcoded _LANG_CODES dict.
    """
    cleaned = name_or_code.strip()
    if not cleaned:
        return "?"

    # Try as code/alias first
    resolved = _lc_resolve_code(cleaned)
    if resolved != cleaned:
        return resolved

    # Try as name
    code = _lc_resolve_name(cleaned)
    if code:
        return code

    # Try stripping parenthetical annotation:
    # "Plains Cree (nêhiyawêwin, SRO)" → "Plains Cree"
    if "(" in cleaned:
        base_name = cleaned.split("(")[0].strip()
        code = _lc_resolve_name(base_name)
        if code:
            return code
        # Also try the base as a code
        resolved = _lc_resolve_code(base_name)
        if resolved != base_name:
            return resolved

    # If it's already a short code-like string, return as-is
    if len(cleaned) <= 3 and cleaned.isalpha():
        return cleaned.lower()

    # Last resort: first 3 chars
    return cleaned[:3].lower()


def _load_corpus_self_meta(config: dict) -> dict:
    """Read self-describing metadata from the run's corpus file, if present.

    Curated corpora built by champollion-corpora-builder embed their own
    identity: top-level corpus_id, language_pair (with ISO 639-3 codes),
    version, and provenance.license. For a pip-installed harness this is
    the only reliable metadata source — the datasets registry and the
    language-cards SSOT are monorepo files, not package data — so corpus
    self-metadata is preferred when resolving dataset ids, language pairs,
    and corpus licenses.

    Returns {} when the corpus file is missing or unreadable (publish may
    run from a different cwd than the run; that must never block it).
    """
    corpus_path = config.get("corpus_path") or ""
    if not corpus_path:
        return {}
    path = Path(corpus_path)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _build_language_pair(config: dict, corpus_meta: dict | None = None) -> str:
    """Build a compact language pair string like 'eng>crk'.

    Prefers the ISO 639-3 codes embedded in the corpus file itself
    (authoritative, and immune to name-resolution fallbacks like
    "Igbo"[:3] → "igb", which is Ebira's code). Falls back to resolving
    the configured language names via the language-cards SSOT.
    """
    pair = (corpus_meta or {}).get("language_pair") or {}
    src_code = (pair.get("source") or "").strip().lower()
    tgt_code = (pair.get("target") or "").strip().lower()
    if src_code and tgt_code:
        return f"{src_code}>{tgt_code}"

    src = config.get("source_lang", "").strip()
    tgt = config.get("target_lang", "").strip()

    src_code = _resolve_lang_to_code(src) if src else "?"
    tgt_code = _resolve_lang_to_code(tgt) if tgt else "?"

    return f"{src_code}>{tgt_code}"


# ---------------------------------------------------------------------------
# Corpus license passthrough — datasets registry lookup
# ---------------------------------------------------------------------------

def _lookup_registry_entry(dataset_id: str) -> dict | None:
    """Look up a dataset's full entry in the datasets registry.

    Matches by dataset id or alias. Returns the raw registry entry dict,
    or None when the dataset is not registered (or the registry is missing —
    e.g. a standalone pip install without the bundled registry).
    """
    if not dataset_id:
        return None

    from mt_eval_harness.config import load_registry

    try:
        registry = load_registry()
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    for entry in registry.get("datasets", []):
        if entry.get("id") == dataset_id or dataset_id in entry.get("aliases", []):
            return entry

    return None


def _resolve_dataset_id(config: dict, corpus_meta: dict | None = None) -> str:
    """Resolve the registry dataset id for a run's corpus.

    Older RunLogs record only the segment filter in config["dataset"]
    (e.g. "all", "dev") and leave config["dataset_id"] empty, so run
    cards historically published with a meaningless dataset id. When no
    explicit dataset_id is set, fall back to matching the corpus file's
    basename against the registry entries' path/local_path so the run
    card references the real dataset (and inherits its license).

    Resolution order:
        1. config["dataset_id"] (explicit — always wins)
        2. the corpus file's own top-level "corpus_id" (self-describing
           curated corpora — works for pip installs with no registry)
        3. registry entry whose path/local_path basename matches
           config["corpus_path"]'s basename
        4. the corpus file's stem (still queue-matchable)
        5. config["dataset"] (legacy segment-filter fallback)
    """
    explicit = config.get("dataset_id", "")
    if explicit:
        return explicit

    self_id = ((corpus_meta or {}).get("corpus_id") or "").strip()
    if self_id:
        return self_id

    corpus_path = config.get("corpus_path") or ""
    if corpus_path:
        from mt_eval_harness.config import load_registry

        basename = Path(corpus_path).name
        try:
            registry = load_registry()
        except (FileNotFoundError, json.JSONDecodeError):
            registry = {}
        stem = Path(corpus_path).stem
        for entry in registry.get("datasets", []):
            for key in ("path", "local_path"):
                entry_path = entry.get(key)
                if entry_path and Path(entry_path).name == basename:
                    return entry["id"]
            # Fallback: corpus filename stem matches the id or an alias
            # (covers local-only corpora with no registered path).
            if stem == entry.get("id") or stem in entry.get("aliases", []):
                return entry["id"]
        # No registry match (e.g. pip install with no bundled registry):
        # the corpus file stem is still meaningful and queue-matchable —
        # never publish the segment filter ("all"/"dev") as a dataset id.
        if stem:
            return stem

    return config.get("dataset", "")


def _lookup_corpus_license(dataset_id: str) -> dict | None:
    """Look up a dataset's license + attribution in the datasets registry.

    The registry (arena/datasets/registry.json, bundled with the harness)
    records a `license` (SPDX-ish string) and `source` (attribution) for
    every registered evaluation corpus. Run cards embed these so every
    leaderboard row carries its corpus license obligations — part of the
    project's line-level license tracking policy.

    Matches by dataset id or alias. Returns:
        {"license": str | None, "attribution": str | None} on a registry hit,
        None when the dataset is not registered (or the registry is missing —
        e.g. a standalone pip install without the bundled registry).
    """
    entry = _lookup_registry_entry(dataset_id)
    if entry is None:
        return None
    return {
        "license": entry.get("license"),
        "attribution": entry.get("source"),
    }


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

    # Vacuous runs (every entry errored) score nothing — their 0.0 rates are
    # computed over zero evaluated entries. Refuse to mint a card for one.
    if overall.get("evaluated", 0) == 0:
        raise ValueError(
            f"Refusing to assemble a run card for {report_path}: evaluated=0 "
            f"({overall.get('error_count', '?')}/{overall.get('total_entries', '?')} "
            "entries errored). Re-run the evaluation; vacuous runs are never "
            "publishable."
        )

    # Provenance block (from runs using the updated pipeline.py).
    # Falls back to empty dict for legacy RunLogs that predate provenance.
    provenance = run_log.get("provenance", {})
    dataset_meta = provenance.get("dataset_meta", {})
    # Self-describing metadata from the corpus file itself (corpus_id,
    # ISO-coded language_pair, provenance.license). Empty dict when the
    # corpus file isn't reachable from the publish cwd.
    corpus_meta = _load_corpus_self_meta(config)

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

    # giellalt_fst_validity is the canonical FST metric key.
    # Also check legacy fst_analyzer for pre-plugin standalone reports.
    for fst_key in ("giellalt_fst_validity", "fst_analyzer"):
        fst_data = plugin_metrics.get(fst_key, {})
        if fst_data and not fst_data.get("error"):
            # GiellaLT and CRK FST use 'avg_fst_validity';
            # legacy fst_analyzer uses 'acceptance_rate'.
            # Explicit None checks — 0.0 is a valid value (all words invalid)
            # and must NOT fall through to the legacy key.
            rate = fst_data.get("avg_fst_validity")
            if rate is None:
                rate = fst_data.get("acceptance_rate")
            fst_acceptance_rate = rate
            # GiellaLTFSTMetric uses 'total_valid_words';
            # legacy fst_analyzer uses 'accepted'
            count = fst_data.get("total_valid_words")
            if count is None:
                count = fst_data.get("accepted")
            fst_accepted_count = count
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
            except (json.JSONDecodeError, KeyError) as exc:
                # WARNING: This switches composite scoring to Profile B
                # (no-FST weights) because fst_acceptance_rate stays None.
                print(
                    f"  ⚠ FST report at {fst_report_path} is malformed "
                    f"({exc}). Composite will use no-FST weights."
                )

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

    # Writing style (informational only — NOT in composite)
    style_consistency_rate = None
    ws_data = plugin_metrics.get("writing_style", {})
    if ws_data and not ws_data.get("error"):
        style_consistency_rate = ws_data.get("style_consistency_rate")

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
    # Cost-adjusted score (SCORING_SPEC §6.3)
    # Rewards methods that achieve good composite scores efficiently.
    # -------------------------------------------------------------------
    cas = cost_adjusted_score(composite, cost_per_entry)

    # -------------------------------------------------------------------
    # Assemble the run card (BENCHMARK_SPEC §3)
    # -------------------------------------------------------------------

    # Detect git provenance from the harness repo
    git_provenance = _detect_git_provenance()

    # Condition label (§3.2). The CLI now derives prompt_version="coached"
    # when coaching is supplied with the default --prompt, but run logs
    # produced before that change (or by direct API use) still say "naive"
    # even though a coaching prompt replaced the naive system prompt at
    # runtime. Relabel from provenance so the published condition reflects
    # what actually ran. Explicit non-default labels are preserved.
    condition = config.get("prompt_version", "")
    if condition == "naive" and provenance.get("coaching_prompt"):
        condition = "coached"

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
        "condition": condition,
        "temperature": config.get("_effective_temperature",
                                  config.get("temperature", 0)),
        "max_tokens": config.get("max_tokens"),
        "system_prompt_sha256": provenance.get("system_prompt_sha256", ""),
        "system_prompt_used": provenance.get("system_prompt_used", ""),
        "coaching_data_sha256": provenance.get("coaching_prompt_sha256") or None,
        "fst_version": None,  # populated when FST plugin is registered
        "tools_enabled": config.get("tools_enabled", False),
        "batch_size": config.get("batch_size", 25),
        "concurrency": config.get("concurrency"),

        # §3.3 Dataset reference
        "dataset": {
            "id": _resolve_dataset_id(config, corpus_meta),
            "version": dataset_meta.get("version")
                or corpus_meta.get("version"),
            "language_pair": _build_language_pair(config, corpus_meta),
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
            # TER: Translation Edit Rate (sacrebleu) — lower is better.
            # Excluded from composite (Appendix A: correlates with chrF++,
            # including both would double-count surface similarity).
            "ter": overall.get("corpus_ter"),
            # Length ratio: avg(len(predicted) / len(expected)) across entries.
            # Diagnostic, not a quality signal — ideal is 1.0.
            "length_ratio": overall.get("avg_length_ratio"),
            # Wired from CrkSemanticMetric: weighted verdict score (0.0–1.0)
            "semantic_score": semantic_score,
            # §2.4 Behavioral metrics — raw rates, always persisted.
            # These feed into composite scoring (scoring.py handles inversion)
            # and must be stored for retroactive rescoring.
            "code_switching_rate": code_switching_rate,
            "hallucination_rate": hallucination_rate,
            "terminology_adherence": terminology_adherence,
            # §2.5 Writing style (informational — NOT in composite)
            "style_consistency_rate": style_consistency_rate,
            "composite": composite,
            "cost_adjusted": cas,
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
            # Original price of cache-hit entries — total_cost_usd is the
            # ACTUAL spend of this run (founder decision 2026-06-12:
            # cached runs report accurately, original price alongside).
            "cached_cost_usd": run_log.get("cached_cost_usd", 0),
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

    # -------------------------------------------------------------------
    # Corpus license passthrough (project licensing policy)
    #
    # Embed the corpus license + attribution from the datasets registry
    # so every published run carries its license obligations. Nullable —
    # unregistered datasets publish fine, with a warning, so ad-hoc
    # corpora (--corpus path/to/file.json) are not blocked.
    # -------------------------------------------------------------------
    license_info = _lookup_corpus_license(run_card["dataset"]["id"])
    if license_info is None and corpus_meta:
        # Registry unavailable or dataset unregistered (typical for a
        # pip-installed harness) — fall back to the license the corpus
        # file carries in its own provenance block.
        corpus_prov = corpus_meta.get("provenance") or {}
        self_license = (corpus_prov.get("license") or "").strip()
        if self_license:
            attribution = (corpus_prov.get("source_url") or "").strip()
            license_info = {
                "license": self_license,
                "attribution": attribution or None,
            }
    if license_info is None:
        run_card["corpus_license"] = None
        run_card["corpus_attribution"] = None
        print(
            f"  ⚠ Dataset '{run_card['dataset']['id']}' is not in the "
            f"datasets registry — corpus_license/corpus_attribution will "
            f"be null. Register it in arena/datasets/registry.json to "
            f"track license obligations."
        )
    else:
        run_card["corpus_license"] = license_info["license"]
        run_card["corpus_attribution"] = license_info["attribution"]

    # -------------------------------------------------------------------
    # Throughput / speed metrics (SCORING_SPEC §7)
    #
    # These are derived from existing RunLog fields. They are NOT in the
    # composite — they measure speed, not quality.
    # -------------------------------------------------------------------
    elapsed_s = run_log.get("elapsed_s")
    total_tokens = prompt_tokens + completion_tokens

    tokens_per_second = None
    if elapsed_s and elapsed_s > 0 and total_tokens > 0:
        tokens_per_second = round(total_tokens / elapsed_s, 2)

    entries_per_minute = None
    if elapsed_s and elapsed_s > 0 and entry_count > 0:
        entries_per_minute = round(entry_count / (elapsed_s / 60), 2)

    # cost_per_source_char: normalize cost by total source characters.
    # Comparable across languages with different tokenization.
    total_source_chars = sum(
        len(r.get("source", "")) for r in results
    )
    cost_per_source_char = None
    if total_source_chars > 0 and total_cost_usd > 0:
        cost_per_source_char = round(
            total_cost_usd / total_source_chars, 8
        )

    # tokens_per_entry: average token consumption per corpus entry.
    # Useful for comparing model verbosity across methods.
    tokens_per_entry = None
    if entry_count > 0 and total_tokens > 0:
        tokens_per_entry = round(total_tokens / entry_count, 2)

    # cost_per_1k_tokens: normalize cost by token volume.
    # Comparable across providers with different pricing models.
    cost_per_1k_tokens = None
    if total_tokens > 0 and total_cost_usd > 0:
        cost_per_1k_tokens = round(
            total_cost_usd / total_tokens * 1000, 6
        )

    run_card["scores"]["tokens_per_second"] = tokens_per_second
    run_card["scores"]["entries_per_minute"] = entries_per_minute
    run_card["totals"]["cost_per_source_char"] = cost_per_source_char
    run_card["totals"]["tokens_per_entry"] = tokens_per_entry
    run_card["totals"]["cost_per_1k_tokens"] = cost_per_1k_tokens

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
    #
    # NOTE: condition is the DERIVED label (coached runs whose config
    # still says "naive" are relabelled "coached" above), so a legacy
    # coached run log republished after that change fingerprints as
    # "coached" — a different hash/UUID than its original "naive"-labelled
    # publish. This is intentional: the old label misrepresented the
    # setup. True naive baselines are unaffected.
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
    if rate is None:
        return None
    if rate > 1.0:
        return round(rate, 1)
    return round(rate * 100, 1)



def _extract_lyss_verdicts(plugin_metrics: dict | None) -> dict:
    """Extract per-entry LYSS verdicts from plugin_metrics for SQL columns.

    Maps each plugin's per-entry output key to the denormalized column
    defined in migration 006 (run_card_entries table). Returns only
    non-None values to avoid overwriting NULLs with explicit None
    (Supabase treats them differently).

    Plugin key mapping:
        giellalt_fst_validity.fst_validity_rate → fst_valid (bool)
        crk_linter.equivalent_match → equivalent_match (bool)
        crk_semantic.semantic_verdict → semantic_verdict (str)
        code_switching.code_switching_rate → code_switching_detected (bool)
        hallucination.hallucination_rate → hallucination_detected (bool)
    """
    if not plugin_metrics:
        return {}

    verdicts = {}

    # Helper: safely get a plugin result as dict, skipping non-dict values
    # (e.g., an error string stored by a failed plugin run).
    def _get_dict(key: str) -> dict:
        val = plugin_metrics.get(key)
        return val if isinstance(val, dict) else {}

    # FST validity: rate == 1.0 means all words valid.
    # giellalt_fst_validity is the sole canonical FST metric key.
    fst = _get_dict("giellalt_fst_validity")
    if "fst_validity_rate" in fst:
        verdicts["fst_valid"] = fst["fst_validity_rate"] == 1.0

    # Linter equivalence: direct boolean from CrkLinterMetric
    linter = _get_dict("crk_linter")
    if "equivalent_match" in linter:
        verdicts["equivalent_match"] = bool(linter["equivalent_match"])

    # Semantic verdict: string from CrkSemanticMetric
    semantic = _get_dict("crk_semantic")
    if "semantic_verdict" in semantic:
        verdicts["semantic_verdict"] = semantic["semantic_verdict"]

    # Code-switching: any rate > 0 means switching detected
    cs = _get_dict("code_switching")
    if "code_switching_rate" in cs:
        verdicts["code_switching_detected"] = cs["code_switching_rate"] > 0

    # Hallucination: any rate > 0 means hallucination detected
    hall = _get_dict("hallucination")
    if "hallucination_rate" in hall:
        verdicts["hallucination_detected"] = hall["hallucination_rate"] > 0

    return verdicts


# ---------------------------------------------------------------------------
# Row validation — required NOT NULL columns (see DATABASE_SCHEMA.md)
# ---------------------------------------------------------------------------

# Columns that are NOT NULL in run_cards with no DB default, and that must
# carry a real (non-empty) value for the row to make sense on the leaderboard.
REQUIRED_ROW_FIELDS = (
    "id",
    "submitter",
    "affirmation",
    "trust",
    "model_slug",
    "dataset_id",
    "language_pair",
    "harness_version",
    "run_card",
    "fingerprint_hash",
)

# NOT NULL columns where an empty string is technically valid (e.g. a run
# without a prompt_version has condition "") — only None/missing is an error.
REQUIRED_NOT_NULL_FIELDS = (
    "condition",
)

# Nullable columns that are explicitly OPTIONAL: a None value must never
# block a publish. corpus_license/corpus_attribution (migration 015) are
# null for datasets missing from arena/datasets/registry.json — assembly
# prints a warning instead of failing, so ad-hoc corpora stay publishable.
OPTIONAL_NULLABLE_FIELDS = (
    "corpus_license",
    "corpus_attribution",
)


def validate_row(row: dict) -> list[str]:
    """Check a Supabase run_cards row for required NOT NULL fields.

    Returns a list of field names that are missing, None, or empty
    (empty string / empty dict). An empty list means the row is valid.

    This guards against posting rows that the DB would reject (NOT NULL
    violations) or that would render as blank leaderboard entries.
    """
    problems = []

    for field in REQUIRED_ROW_FIELDS:
        value = row.get(field)
        if value is None:
            problems.append(field)
        elif isinstance(value, str) and not value.strip():
            problems.append(field)
        elif isinstance(value, dict) and not value:
            problems.append(field)

    for field in REQUIRED_NOT_NULL_FIELDS:
        if row.get(field) is None:
            problems.append(field)

    # OPTIONAL_NULLABLE_FIELDS are deliberately NOT checked: a null
    # corpus_license/corpus_attribution is valid (unregistered dataset)
    # and must not block the publish.

    return problems


# ---------------------------------------------------------------------------
# Resilient POST — retry with exponential backoff
# ---------------------------------------------------------------------------

# 3 attempts with 1s/2s/4s exponential backoff between retries.
UPSERT_MAX_ATTEMPTS = 3
UPSERT_BACKOFF_S = (1, 2, 4)


def _upsert_with_retry(
    req: urllib.request.Request,
    timeout: int = 15,
    max_attempts: int = UPSERT_MAX_ATTEMPTS,
) -> dict:
    """POST a prepared request to Supabase, retrying transient failures.

    Retries on HTTP 5xx and network-level errors (URLError, timeouts)
    with exponential backoff. 4xx responses are real errors (bad payload,
    auth, RLS rejection) — those fail immediately with the response body.

    Args:
        req: A fully-prepared urllib Request (headers + body set).
        timeout: Per-attempt socket timeout in seconds.
        max_attempts: Total number of attempts (including the first).

    Returns:
        The parsed JSON response body.

    Raises:
        SystemExit on a 4xx response or after all attempts are exhausted.
    """
    last_error = "unknown error"

    for attempt in range(1, max_attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode()
            if exc.code < 500:
                # Client error — retrying won't help. Show the body so the
                # user can see what Supabase rejected (RLS, schema, auth).
                print(f"\n  ❌ Publish failed ({exc.code}): {body}")
                raise SystemExit(1)
            last_error = f"HTTP {exc.code}: {body[:200]}"
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            # Network-level failure: DNS, connection refused, timeout.
            last_error = f"network error: {exc}"

        if attempt < max_attempts:
            delay = UPSERT_BACKOFF_S[min(attempt - 1, len(UPSERT_BACKOFF_S) - 1)]
            print(
                f"  ⚠ Attempt {attempt}/{max_attempts} failed "
                f"({last_error}). Retrying in {delay}s..."
            )
            time.sleep(delay)

    print(f"\n  ❌ Publish failed after {max_attempts} attempts ({last_error})")
    raise SystemExit(1)


def _fetch_existing_card(card_id: str) -> dict | None:
    """Return the existing run_cards row for this id, or None.

    Read-only anon GET — run_cards SELECT is public. Network errors are
    treated as "not found" so a flaky pre-flight never blocks a publish;
    the upsert itself remains the authoritative gate.
    """
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/run_cards"
        f"?id=eq.{urllib.parse.quote(card_id)}"
        "&select=id,submitter,submitted_at,trust",
        headers={"apikey": SUPABASE_ANON_KEY},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            rows = json.loads(resp.read())
            return rows[0] if rows else None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None


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
        # Trust tier: CLI submissions are always 'unverified'.
        # The DB enforces CHECK(trust IN ('unverified','verified','disqualified'))
        # and the INSERT RLS requires trust='unverified'. Elevated tiers
        # are granted via admin dashboard using service_role key.
        "trust": "unverified",
        "model_slug": run_card["model_slug"],
        "condition": run_card["condition"],
        "dataset_id": dataset["id"],
        "language_pair": dataset.get("language_pair", "unknown>unknown"),
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
        # Method class from method card (raw-llm, coached-llm, pipeline, etc.)
        "method_class": (run_card.get("method_card") or {}).get("class"),
        # New surface metrics — TER and length ratio
        "ter": scores.get("ter"),
        "length_ratio": scores.get("length_ratio"),
        # Throughput metrics
        "tokens_per_second": scores.get("tokens_per_second"),
        "entries_per_minute": scores.get("entries_per_minute"),
        "cost_per_source_char": totals.get("cost_per_source_char"),
        # Latency statistics — top-level columns for leaderboard sorting.
        # These exist in the run_card JSON scores block but also need
        # to be top-level for SQL queries (CLI migration 20260528024953).
        "median_latency_seconds": scores.get("median_latency_seconds"),
        "p95_latency_seconds": scores.get("p95_latency_seconds"),
        # Token efficiency metrics (SCORING_SPEC §6.1, §6.2)
        "tokens_per_entry": totals.get("tokens_per_entry"),
        "cost_per_1k_tokens": totals.get("cost_per_1k_tokens"),
        # §2.4 Behavioral metrics — top-level columns for SQL queryability.
        # Stored as raw rates (0.0–1.0), not percentages.
        "code_switching_rate": scores.get("code_switching_rate"),
        "hallucination_rate": scores.get("hallucination_rate"),
        "terminology_adherence": scores.get("terminology_adherence"),
        # §2.5 Writing style (informational only — not in composite)
        "style_consistency_rate": scores.get("style_consistency_rate"),
        # Corpus license passthrough (migration 015) — nullable TEXT columns.
        # Sourced from arena/datasets/registry.json at assembly time; null
        # for unregistered datasets (a warning was printed during assembly).
        "corpus_license": run_card.get("corpus_license"),
        "corpus_attribution": run_card.get("corpus_attribution"),
    }

    # --- Preview ---
    print(f"\n  Submitter:     {submitter}")
    print(f"  Model:         {run_card['model_slug']}")
    print(f"  Condition:     {run_card['condition']}")
    print(f"  Batch size:    {run_card.get('batch_size', '?')}")
    print(f"  Temperature:   {run_card.get('temperature', '?')}")
    print(f"  Max tokens:    {run_card.get('max_tokens', '?')}")
    print(f"  Dataset:       {dataset['id']} ({scores.get('total', '?')} entries)")
    if run_card.get("corpus_license"):
        print(f"  License:       {run_card['corpus_license']}")
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
    if scores.get("ter") is not None:
        print(f"  TER:           {scores['ter']:.2f}")
    if scores.get("length_ratio") is not None:
        print(f"  Length Ratio:  {scores['length_ratio']:.4f}")
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
    cost_adj = scores.get("cost_adjusted")
    if cost_adj is not None:
        print(f"  Cost-adjusted: {cost_adj:.4f}")
    print(f"  Cost:          ${totals['total_cost_usd']:.4f}")
    if totals.get("cost_per_entry_usd"):
        print(f"  Cost/entry:    ${totals['cost_per_entry_usd']:.6f}")
    if totals.get("cost_per_source_char"):
        print(f"  Cost/src char: ${totals['cost_per_source_char']:.8f}")
    if scores.get("tokens_per_second") is not None:
        print(f"  Tokens/sec:    {scores['tokens_per_second']:.1f}")
    if scores.get("entries_per_minute") is not None:
        print(f"  Entries/min:   {scores['entries_per_minute']:.1f}")
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

    # --- Validate before posting ---
    # Catch rows the DB would reject (NOT NULL violations) before we
    # spend a network round-trip — and before partial publishes happen.
    problems = validate_row(row)
    if problems:
        print("\n  ❌ Run card is incomplete — missing or empty required fields:")
        for field in problems:
            print(f"       - {field}")
        print("  Nothing was published. Fix the report/run log and retry.")
        raise SystemExit(1)

    # --- Duplicate pre-flight ---
    # The card id is a deterministic UUID over the experiment fingerprint,
    # and submissions are immutable by design: migration 019 removed the
    # UPDATE policy on run_cards, so an upsert that hits an existing row is
    # rejected by RLS with an opaque 403 ("USING expression"). Check first
    # and explain, instead of failing.
    existing = _fetch_existing_card(card_id)
    if existing is not None:
        print(
            "\n  ✓ This exact experiment is already on the leaderboard "
            "(submissions are immutable):"
        )
        print(f"      id:           {card_id}")
        print(f"      submitter:    {existing.get('submitter', '?')}")
        print(f"      submitted at: {existing.get('submitted_at', '?')}")
        print(
            "    Nothing to publish. Run the experiment with a different "
            "model/corpus/condition,\n    or contact a moderator if this "
            "card needs correction."
        )
        return existing

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

    result = _upsert_with_retry(req, timeout=15)

    print(f"\n  ✅ Published to leaderboard!")

    # --- Upsert dataset metadata ---
    # Populate the datasets table organically — every publish writes the
    # corpus metadata so the leaderboard can filter by language pair
    # without digging into the run_card JSONB blob.
    #
    # SCHEMA NOTE: The live datasets table was created by CLI migration
    # 20260528024953 (with version NOT NULL, segment CHECK, scalar domain).
    # Arena migration 011 adds difficulty_min/max, domains[], segments[],
    # updated_at. This upsert is compatible with BOTH pre-011 and post-011
    # schemas because PostgREST ignores unknown columns in the payload.
    dataset = run_card.get("dataset", {})
    dataset_id = dataset.get("id", "")

    # Load report data from disk (needed for dataset metadata and per-entry publishing)
    report_data = json.loads(Path(report_path).read_text(encoding="utf-8"))

    if dataset_id:
        # Extract corpus metadata from the loaded report
        by_difficulty = report_data.get("by_difficulty", {})
        difficulty_levels = [
            int(k) for k in by_difficulty.keys() if k.isdigit()
        ] if by_difficulty else []
        by_domain = report_data.get("by_domain", {})
        by_segment = report_data.get("by_segment", {})

        # PostgREST TEXT[] format: {"val1","val2"} not ["val1","val2"]
        # json.dumps converts Python lists to JSON arrays, which PostgREST
        # accepts for TEXT[] columns when Content-Type is application/json.
        domain_list = list(by_domain.keys()) if by_domain else []
        segment_list = list(by_segment.keys()) if by_segment else []

        # Enrich with license/attribution metadata from the bundled
        # datasets registry (arena/datasets/registry.json) when the
        # dataset is registered — keeps the datasets table's license
        # obligations in sync with the run_cards corpus_license column.
        registry_entry = _lookup_registry_entry(dataset_id) or {}

        dataset_row = {
            "id": dataset_id,
            "name": registry_entry.get("name") or dataset_id,
            # version is NOT NULL in the CLI schema (until migration 011
            # relaxes it), so we must provide a fallback.
            "version": dataset.get("version")
                or registry_entry.get("version")
                or "unknown",
            "source_language": dataset.get("source_lang", "en"),
            "target_language": dataset.get("target_lang", ""),
            "language_pair": dataset.get("language_pair", ""),
            "entry_count": dataset.get("entry_count")
                or registry_entry.get("size"),
            "sha256": dataset.get("sha256", ""),
            # License + attribution from the registry (nullable TEXT columns;
            # PostgREST ignores them on schemas that predate the columns).
            "license": registry_entry.get("license"),
            "source": registry_entry.get("source"),
            "domain": registry_entry.get("domain"),
            "notes": registry_entry.get("notes"),
            # Arena-specific columns (added by migration 011).
            # PostgREST silently ignores unknown columns, so this is
            # safe to send even before 011 is applied.
            "difficulty_min": min(difficulty_levels) if difficulty_levels else None,
            "difficulty_max": max(difficulty_levels) if difficulty_levels else None,
            "domains": domain_list,
            "segments": segment_list,
        }
        try:
            ds_data = json.dumps(dataset_row).encode()
            ds_req = urllib.request.Request(
                f"{SUPABASE_URL}/rest/v1/datasets",
                data=ds_data,
                headers={
                    "apikey": SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates",
                },
                method="POST",
            )
            with urllib.request.urlopen(ds_req, timeout=10) as ds_resp:
                ds_resp.read()
            print(f"  ✅ Dataset '{dataset_id}' registered")
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
            # Non-fatal — the datasets table is secondary metadata.
            # The run_card (primary) is already published.
            err_detail = ""
            if hasattr(e, "read"):
                err_detail = f": {e.read().decode()[:200]}"
            print(f"  ⚠ Dataset upsert skipped ({e}{err_detail})")

    # --- Publish per-entry data ---
    # Load entries from the report and batch-insert into run_card_entries.
    # This enables per-entry drill-down on the leaderboard website.
    # (report_data already loaded above)
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
            # Per-entry LYSS verdicts — denormalized from plugin_metrics
            # for SQL-level filtering without JSONB path queries.
            # These columns mirror migration 006 additions to run_card_entries.
            **_extract_lyss_verdicts(entry.get("plugin_metrics", {})),
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
        except (urllib.error.URLError, OSError) as exc:
            # Network-level failure (DNS, connection refused, timeout).
            # Don't crash — the run_card is already published and the
            # entries can be re-published via `mt-eval publish --force`.
            print(
                f"  ⚠ Entry batch {i // BATCH_SIZE + 1} failed "
                f"(network error): {exc}"
            )

    if total_inserted > 0:
        print(f"  ✅ {total_inserted}/{len(rows)} entries published")
    elif rows:
        print(
            f"  ⚠ All {len(rows)} entries failed to publish. "
            f"Re-run with `mt-eval publish --force` to retry."
        )

