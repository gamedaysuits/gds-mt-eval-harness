"""
Test Harness — Deterministic metric analyzer for RunLog files.

Takes a RunLog JSON from the Run Harness and computes:
    - Exact match rate (string equality after normalization)
    - chrF++ score (via sacrebleu)
    - BLEU score (via sacrebleu)
    - COMET score (via unbabel-comet, if installed)
    - Bootstrap 95% confidence intervals on all corpus metrics
    - Plugin metrics (via MetricPlugin protocol)
    - Per-segment breakdown
    - Per-difficulty breakdown
    - Error rate and error categorization
    - Token/cost aggregates

Design decisions:
    - This module is OFFLINE — it never makes API calls. All analysis
      is deterministic and reproducible from the logged predictions.
    - Language-specific metrics (FST validity, morphological linting,
      semantic validation) are registered as MetricPlugin instances,
      NOT hardcoded into this module.
    - Dependencies: sacrebleu. COMET optional but recommended.
    - Output is a TestReport JSON file alongside the RunLog.
"""

from __future__ import annotations

import json
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from sacrebleu.metrics import CHRF, BLEU


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class EntryMetrics:
    """Per-entry analysis results."""
    id: int = 0
    source: str = ""   # Source text (matches runner.py enrichment key)
    expected: str = ""  # Reference translation
    raw_predicted: str = "" # Raw model output before hooks
    predicted: str = "" # Model output
    segment: str = ""
    difficulty: int = 0
    domain: str = ""

    # Core metrics (built-in)
    exact_match: bool = False
    chrf_score: float = 0.0
    bleu_score: float = 0.0

    # From RunLog
    latency_s: float = 0.0
    cost_usd: float = 0.0
    tool_call_count: int = 0
    error: str | None = None

    # Plugin metrics get merged here
    plugin_metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class SegmentMetrics:
    """Aggregate metrics for a dataset segment or difficulty level."""
    name: str = ""
    count: int = 0
    exact_match_count: int = 0
    miss_count: int = 0
    error_count: int = 0

    # Averages
    avg_chrf: float = 0.0
    avg_bleu: float = 0.0
    avg_latency_s: float = 0.0
    total_cost_usd: float = 0.0

    # Plugin aggregate metrics
    plugin_aggregates: dict[str, Any] = field(default_factory=dict)

    @property
    def exact_match_rate(self) -> float:
        return self.exact_match_count / self.count if self.count else 0.0

    @property
    def error_rate(self) -> float:
        return self.error_count / self.count if self.count else 0.0


# ---------------------------------------------------------------------------
# String normalization for exact match comparison
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Normalize text for exact match comparison.

    Applies Unicode NFC normalization, case folding, and whitespace
    normalization. This ensures that trivial formatting differences
    don't produce false negatives.
    """
    text = unicodedata.normalize("NFC", text)
    text = text.strip().lower()
    text = " ".join(text.split())  # Collapse whitespace
    return text


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------

def analyze_run(
    log_path: str | Path,
    output_path: str | None = None,
    metric_plugins: list | None = None,
    compute_ci: bool = True,
    n_bootstrap_ci: int = 1000,
) -> dict:
    """Analyze a RunLog file and produce a TestReport.

    Args:
        log_path: Path to the RunLog JSON file.
        output_path: Optional output path for the TestReport.
                     Defaults to log_path with _report.json suffix.
        metric_plugins: Optional list of MetricPlugin instances.
        compute_ci: If True, compute bootstrap 95% confidence intervals
                    on corpus-level metrics. Default: True.
        n_bootstrap_ci: Number of bootstrap iterations for CI. Default: 1000
                        (matches SacreBLEU/WMT convention).

    Returns:
        Complete TestReport dict.
    """
    log_path = Path(log_path)
    if not log_path.exists():
        raise FileNotFoundError(f"RunLog not found: {log_path}")

    run_log = json.loads(log_path.read_text(encoding="utf-8"))

    if output_path is None:
        output_path = log_path.with_name(log_path.stem + "_report.json")

    return _analyze(
        run_log,
        output_path=output_path,
        metric_plugins=metric_plugins,
        compute_ci=compute_ci,
        n_bootstrap_ci=n_bootstrap_ci,
    )


def analyze_run_log(
    run_log: dict,
    output_path: str | Path | None = None,
    metric_plugins: list | None = None,
    compute_ci: bool = True,
    n_bootstrap_ci: int = 1000,
) -> dict:
    """Analyze an in-memory RunLog dict and produce a TestReport.

    Called automatically at the end of execute_run() so users
    don't need a separate 'mt-eval test' step.

    Args:
        run_log: The RunLog dict (as returned by build_run_log).
        output_path: Optional output path for the TestReport.
        metric_plugins: Optional list of MetricPlugin instances.
        compute_ci: If True, compute bootstrap 95% CIs. Default: True.
        n_bootstrap_ci: Number of bootstrap iterations for CI. Default: 1000.

    Returns:
        Complete TestReport dict.
    """
    return _analyze(
        run_log,
        output_path=output_path,
        metric_plugins=metric_plugins,
        compute_ci=compute_ci,
        n_bootstrap_ci=n_bootstrap_ci,
    )


def _analyze(
    run_log: dict,
    output_path: str | Path | None = None,
    metric_plugins: list | None = None,
    compute_ci: bool = True,
    n_bootstrap_ci: int = 1000,
) -> dict:
    """Core analysis logic shared by file-based and in-memory entry points."""
    results = run_log.get("results", [])

    if not results:
        print("  WARNING: RunLog contains no results")
        return {"error": "No results in RunLog"}

    print(f"  Analyzing {len(results)} entries")

    # Setup sacrebleu metrics if available
    chrf_metric = CHRF(word_order=2)
    bleu_metric = BLEU()

    plugins = metric_plugins or []

    # Auto-load DoublePassCompliancePlugin if language card is found
    config_dict = run_log.get("config", {})
    target_code = config_dict.get("target_lang_code")
    cards_dir = config_dict.get("champollion_cards_dir")

    if target_code:
        try:
            from mt_eval_harness.champollion_config import load_language_card, _find_cards_dir

            resolved_cards_dir = Path(cards_dir) if cards_dir else _find_cards_dir()
            if resolved_cards_dir and resolved_cards_dir.is_dir():
                card = load_language_card(target_code, resolved_cards_dir)
                if card and card.get("rules"):
                    from mt_eval_harness.plugins.double_pass_compliance import DoublePassCompliancePlugin
                    # Avoid adding it twice
                    if not any(isinstance(p, DoublePassCompliancePlugin) for p in plugins):
                        plugins.append(DoublePassCompliancePlugin(card))
        except Exception as e:
            print(f"  WARNING: Failed to auto-load compliance plugin: {e}")

    if plugins:
        print(f"  Active plugins: {', '.join(p.name for p in plugins)}")


    # --- Per-entry analysis ---
    entry_metrics: list[EntryMetrics] = []
    # Collect plugin results for aggregation
    plugin_entry_results: dict[str, list[dict]] = {p.name: [] for p in plugins}

    for r in results:
        em = EntryMetrics(
            id=r["id"],
            source=r.get("source", ""),
            expected=r.get("expected", ""),
            raw_predicted=r.get("raw_predicted", r.get("predicted", "")),
            predicted=r.get("predicted", ""),
            segment=r.get("segment", ""),
            difficulty=r.get("difficulty", 0),
            domain=r.get("domain", ""),
            latency_s=r.get("latency_s", 0),
            cost_usd=r.get("cost_usd", 0),
            tool_call_count=r.get("tool_call_count", 0),
            error=r.get("error"),
        )

        expected_norm = normalize_text(em.expected)
        predicted_norm = normalize_text(em.predicted)

        if em.error:
            entry_metrics.append(em)
            continue

        # --- Exact match ---
        em.exact_match = (expected_norm == predicted_norm) and bool(predicted_norm)

        # --- chrF++ ---
        if em.expected and em.predicted:
            try:
                em.chrf_score = chrf_metric.corpus_score(
                    [em.predicted], [[em.expected]]
                ).score
            except Exception:
                em.chrf_score = 0.0

        # --- BLEU ---
        if em.expected and em.predicted:
            try:
                em.bleu_score = bleu_metric.corpus_score(
                    [em.predicted], [[em.expected]]
                ).score
            except Exception:
                em.bleu_score = 0.0

        # --- Plugin metrics ---
        entry_dict = {
            "id": em.id,
            "source": em.source,
            "expected": em.expected,
            "raw_predicted": em.raw_predicted,
            "predicted": em.predicted,
            "segment": em.segment,
            "difficulty": em.difficulty,
        }
        for plugin in plugins:
            try:
                plugin_result = plugin.compute(entry_dict)
                em.plugin_metrics[plugin.name] = plugin_result
                plugin_entry_results[plugin.name].append(plugin_result)
            except Exception as exc:
                em.plugin_metrics[plugin.name] = {"error": str(exc)}
                plugin_entry_results[plugin.name].append({"error": str(exc)})

        entry_metrics.append(em)

    # --- Aggregate by segment ---
    segments = _aggregate_segment_metrics(entry_metrics)

    # --- Aggregate by difficulty ---
    difficulties = _aggregate_difficulty_metrics(entry_metrics)

    # --- Aggregate by domain ---
    domains = _aggregate_domain_metrics(entry_metrics)

    # --- Overall metrics ---
    overall = _compute_overall(entry_metrics)

    # --- Corpus-level chrF++ and BLEU ---
    all_preds = [em.predicted for em in entry_metrics if not em.error]
    all_refs = [em.expected for em in entry_metrics if not em.error]
    if all_preds and all_refs:
        try:
            overall["corpus_chrf"] = round(
                chrf_metric.corpus_score(all_preds, [all_refs]).score, 2
            )
        except Exception:
            pass

    all_preds = [em.predicted for em in entry_metrics if not em.error]
    all_refs = [em.expected for em in entry_metrics if not em.error]
    if all_preds and all_refs:
        try:
            overall["corpus_bleu"] = round(
                bleu_metric.corpus_score(all_preds, [all_refs]).score, 2
            )
        except Exception:
            pass

    # --- COMET scoring (neural metric) ---
    # COMET runs on non-error entries with source, expected, and predicted.
    # It's a heavy operation (loads ~2.3 GB model) but provides the best
    # correlation with human quality judgments for high-resource languages.
    # For African languages, we auto-select AfriCOMET (masakhane/africomet-mtl)
    # which provides better correlation with human judgments for those languages.
    from mt_eval_harness.metrics_comet import compute_comet, HAS_COMET, resolve_comet_model

    comet_result = None
    if HAS_COMET:
        # Resolve the best COMET model for this target language.
        # AfriCOMET auto-selects for African languages in the registry.
        # CLI --comet-model override can be passed via config.
        explicit_model = config_dict.get("comet_model") if config_dict else None
        resolved_model = resolve_comet_model(
            target_lang=target_code or "",
            explicit_model=explicit_model,
        )

        comet_entries = [
            {
                "source": em.source,
                "expected": em.expected,
                "predicted": em.predicted,
                "error": em.error,
            }
            for em in entry_metrics
        ]
        comet_result = compute_comet(
            comet_entries,
            target_lang=target_code or "",
            model_name=resolved_model,
        )
        if comet_result:
            overall["comet_score"] = comet_result.corpus_score
            overall["comet_model"] = comet_result.model_name
            overall["comet_low_resource_warning"] = comet_result.low_resource_warning
    else:
        # COMET not installed — offer to install it right here
        from mt_eval_harness.setup_wizard import prompt_comet_install
        if prompt_comet_install():
            # COMET was just installed — re-import and run it
            from mt_eval_harness.metrics_comet import compute_comet, HAS_COMET, resolve_comet_model
            if HAS_COMET:
                explicit_model = config_dict.get("comet_model") if config_dict else None
                resolved_model = resolve_comet_model(
                    target_lang=target_code or "",
                    explicit_model=explicit_model,
                )
                comet_entries = [
                    {
                        "source": em.source,
                        "expected": em.expected,
                        "predicted": em.predicted,
                        "error": em.error,
                    }
                    for em in entry_metrics
                ]
                comet_result = compute_comet(
                    comet_entries,
                    target_lang=target_code or "",
                    model_name=resolved_model,
                )
                if comet_result:
                    overall["comet_score"] = comet_result.corpus_score
                    overall["comet_model"] = comet_result.model_name
                    overall["comet_low_resource_warning"] = comet_result.low_resource_warning
        if overall.get("comet_score") is None:
            overall["comet_score"] = None

    # --- Bootstrap confidence intervals ---
    # Compute 95% CIs on corpus-level metrics. Uses the same bootstrap
    # methodology as SacreBLEU and WMT shared tasks (see confidence.py
    # module header for full justification).
    if compute_ci:
        from mt_eval_harness.confidence import compute_all_cis

        # Build entry dicts in the format expected by significance.py
        # metric functions (source, expected, predicted, error, exact_match).
        # Also include per-entry COMET scores (pre-computed above) so that
        # confidence.py can bootstrap from cached values without re-running
        # neural inference on each of the 1000 bootstrap iterations.
        ci_entries = []
        comet_idx = 0
        for em in entry_metrics:
            entry = {
                "source": em.source,
                "expected": em.expected,
                "predicted": em.predicted,
                "error": em.error,
                "exact_match": em.exact_match,
                "plugin_metrics": em.plugin_metrics,
            }
            # Inject pre-computed COMET score for this entry (non-error only)
            if comet_result and comet_result.per_entry_scores and not em.error:
                if comet_idx < len(comet_result.per_entry_scores):
                    entry["comet_score"] = comet_result.per_entry_scores[comet_idx]
                    comet_idx += 1
            ci_entries.append(entry)

        cis = compute_all_cis(
            ci_entries,
            n_bootstrap=n_bootstrap_ci,
        )
        if cis:
            overall["confidence_intervals"] = cis
            print(f"  Bootstrap CIs: computed (n_bootstrap={n_bootstrap_ci})")

        # Per-tier CIs — group entries by difficulty and compute CIs per group
        from mt_eval_harness.confidence import compute_per_tier_cis

        # Inject difficulty field into CI entries (it wasn't included above
        # because compute_all_cis doesn't need it, but per-tier does)
        for ci_entry, em in zip(ci_entries, entry_metrics):
            ci_entry["difficulty"] = em.difficulty

        tier_cis = compute_per_tier_cis(
            ci_entries,
            n_bootstrap=n_bootstrap_ci,
        )
        if tier_cis:
            overall["confidence_intervals_by_tier"] = {
                str(k): v for k, v in tier_cis.items()
            }
            print(f"  Per-tier CIs: {len(tier_cis)} tiers")

    # --- Plugin aggregates ---
    plugin_overall = {}
    for plugin in plugins:
        try:
            agg = plugin.aggregate(plugin_entry_results[plugin.name])
            if agg:
                plugin_overall[plugin.name] = agg
        except Exception as exc:
            plugin_overall[plugin.name] = {"error": str(exc)}

    if plugin_overall:
        overall["plugin_metrics"] = plugin_overall

    # --- Build report ---
    report = {
        "run_id": run_log.get("run_id", "unknown"),
        "config": run_log.get("config", {}),
        "overall": overall,
        "by_segment": {k: asdict(v) for k, v in segments.items()},
        "by_difficulty": {str(k): asdict(v) for k, v in sorted(difficulties.items())},
        "by_domain": {k: asdict(v) for k, v in sorted(domains.items())},
        "entries": [asdict(em) for em in entry_metrics],
    }

    # Include per-entry COMET scores if computed
    if comet_result and comet_result.per_entry_scores:
        # Map COMET scores back to non-error entries
        comet_idx = 0
        for entry in report["entries"]:
            if not entry.get("error") and comet_idx < len(comet_result.per_entry_scores):
                entry["comet_score"] = comet_result.per_entry_scores[comet_idx]
                comet_idx += 1

    # --- Write output ---
    if output_path is not None:
        output_path = Path(output_path)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # --- Print summary ---
    _print_summary(overall, segments, difficulties, domains, output_path,
                    config=run_log.get("config"))

    return report


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def _aggregate_segment_metrics(entries: list[EntryMetrics]) -> dict[str, SegmentMetrics]:
    """Group entries by segment and compute aggregates."""
    groups: dict[str, list[EntryMetrics]] = defaultdict(list)
    for em in entries:
        groups[em.segment or "unknown"].append(em)

    result = {}
    for key, items in groups.items():
        result[key] = _aggregate_group(str(key), items)
    return result


def _aggregate_difficulty_metrics(entries: list[EntryMetrics]) -> dict[int, SegmentMetrics]:
    """Group entries by difficulty level and compute aggregates."""
    groups: dict[int, list[EntryMetrics]] = defaultdict(list)
    for em in entries:
        groups[em.difficulty].append(em)

    result = {}
    for key, items in groups.items():
        result[key] = _aggregate_group(f"difficulty_{key}", items)
    return result


def _aggregate_domain_metrics(entries: list[EntryMetrics]) -> dict[str, SegmentMetrics]:
    """Group entries by domain and compute aggregates.

    Entries without a domain field go into the '' (empty string) group.
    No silent fallback — missing domain stays empty, not a default code.
    """
    groups: dict[str, list[EntryMetrics]] = defaultdict(list)
    for em in entries:
        groups[em.domain].append(em)

    result = {}
    for key, items in groups.items():
        result[key] = _aggregate_group(key or "(no domain)", items)
    return result


def _aggregate_group(name: str, items: list[EntryMetrics]) -> SegmentMetrics:
    """Compute aggregate metrics for a group of entries."""
    sm = SegmentMetrics(name=name, count=len(items))

    chrf_sum = 0.0
    bleu_sum = 0.0
    latency_sum = 0.0
    non_error_count = 0

    for em in items:
        if em.error:
            sm.error_count += 1
            continue

        non_error_count += 1
        latency_sum += em.latency_s
        sm.total_cost_usd += em.cost_usd

        if em.exact_match:
            sm.exact_match_count += 1
        else:
            sm.miss_count += 1

        chrf_sum += em.chrf_score
        bleu_sum += em.bleu_score

    if non_error_count > 0:
        sm.avg_chrf = round(chrf_sum / non_error_count, 2)
        sm.avg_bleu = round(bleu_sum / non_error_count, 2)
        sm.avg_latency_s = round(latency_sum / non_error_count, 3)

    sm.total_cost_usd = round(sm.total_cost_usd, 4)
    return sm


def _compute_overall(entries: list[EntryMetrics]) -> dict:
    """Compute overall aggregate metrics."""
    total = len(entries)
    errors = sum(1 for em in entries if em.error)
    non_error = [em for em in entries if not em.error]
    n = len(non_error)

    exact = sum(1 for em in non_error if em.exact_match)

    overall = {
        "total_entries": total,
        "error_count": errors,
        "evaluated": n,
        "exact_match_count": exact,
        "exact_match_rate": round(exact / n, 4) if n else 0.0,
        "miss_count": n - exact,
        "miss_rate": round((n - exact) / n, 4) if n else 0.0,
    }

    if n:
        overall["avg_chrf"] = round(sum(em.chrf_score for em in non_error) / n, 2)
        overall["avg_bleu"] = round(sum(em.bleu_score for em in non_error) / n, 2)
        overall["avg_latency_s"] = round(
            sum(em.latency_s for em in non_error) / n, 3
        )
        overall["total_cost_usd"] = round(
            sum(em.cost_usd for em in non_error), 4
        )
        overall["total_tool_calls"] = sum(em.tool_call_count for em in non_error)

    return overall


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _print_summary(
    overall: dict,
    segments: dict,
    difficulties: dict,
    domains: dict,
    output_path: Path,
    config: dict | None = None,
):
    """Print human-readable summary to console.

    Args:
        config: Optional run config dict. When present, quality-affecting
                parameters are printed at the top of the summary so users
                can verify what settings produced these scores.
    """
    print("\n" + "=" * 60)
    print("TEST REPORT SUMMARY")
    print("=" * 60)

    # Surface quality-affecting parameters at the top of every report
    # so there's never ambiguity about what produced these scores.
    if config:
        model = config.get("model", config.get("_model_id", "unknown"))
        print(f"\n  Model:         {model}")
        print(f"  Batch size:    {config.get('batch_size', '?')}")
        print(f"  Temperature:   {config.get('_effective_temperature', config.get('temperature', '?'))}")
        print(f"  Prompt:        {config.get('prompt_version', '?')}")
        print(f"  Max tokens:    {config.get('max_tokens', '?')}")
        tgt = config.get("target_lang", "")
        src = config.get("source_lang", "")
        if tgt:
            print(f"  Target lang:   {tgt}")
        if src:
            print(f"  Source lang:   {src}")

    n = overall["evaluated"]
    print(f"\n  Total entries:    {overall['total_entries']}")
    print(f"  Errors:           {overall['error_count']}")
    print(f"  Evaluated:        {n}")
    print(f"\n  Exact match:      {overall['exact_match_count']}/{n} "
          f"({overall['exact_match_rate']:.1%})")
    print(f"  Miss:             {overall['miss_count']}/{n} "
          f"({overall['miss_rate']:.1%})")

    # --- Corpus metrics with optional CIs ---
    cis = overall.get("confidence_intervals", {})

    if "corpus_chrf" in overall:
        ci = cis.get("corpus_chrf")
        if ci:
            print(f"\n  Corpus chrF++:    {overall['corpus_chrf']:.1f}  "
                  f"[{ci['ci_lower']:.1f} – {ci['ci_upper']:.1f}]")
        else:
            print(f"\n  Corpus chrF++:    {overall['corpus_chrf']:.1f}")

    if "corpus_bleu" in overall:
        ci = cis.get("corpus_bleu")
        if ci:
            print(f"  Corpus BLEU:      {overall['corpus_bleu']:.1f}  "
                  f"[{ci['ci_lower']:.1f} – {ci['ci_upper']:.1f}]")
        else:
            print(f"  Corpus BLEU:      {overall['corpus_bleu']:.1f}")

    if overall.get("comet_score") is not None:
        comet = overall["comet_score"]
        warning = " ⚠️ low-resource" if overall.get("comet_low_resource_warning") else ""
        ci = cis.get("comet")
        if ci:
            print(f"  COMET:            {comet:.4f}  "
                  f"[{ci['ci_lower']:.4f} – {ci['ci_upper']:.4f}]{warning}")
        else:
            print(f"  COMET:            {comet:.4f}{warning}")

    if "exact_match_rate" in overall and cis.get("exact_match_rate"):
        ci = cis["exact_match_rate"]
        print(f"  Exact match CI:   [{ci['ci_lower']*100:.1f} – {ci['ci_upper']*100:.1f}%]")

    if overall.get("total_cost_usd"):
        print(f"\n  Total cost:       ${overall['total_cost_usd']:.4f}")
    if overall.get("avg_latency_s"):
        print(f"  Avg latency:      {overall['avg_latency_s']:.1f}s")

    # Per-segment
    if len(segments) > 1:
        print(f"\n  {'Segment':<25s} {'Exact':>7s} {'chrF++':>7s}")
        print(f"  {'-'*25} {'-----':>7s} {'------':>7s}")
        for name, sm in sorted(segments.items()):
            print(
                f"  {name:<25s} "
                f"{sm.exact_match_rate:>6.1%} "
                f"{sm.avg_chrf:>7.1f}"
            )

    # Per-domain
    if len(domains) > 1:
        print(f"\n  {'Domain':<25s} {'Count':>6s} {'Exact':>7s} {'chrF++':>7s}")
        print(f"  {'-'*25} {'-----':>6s} {'-----':>7s} {'------':>7s}")
        for name, sm in sorted(domains.items()):
            print(
                f"  {(name or '(no domain)'):<25s} "
                f"{sm.count:>6d} "
                f"{sm.exact_match_rate:>6.1%} "
                f"{sm.avg_chrf:>7.1f}"
            )

    # Per-difficulty — shows how quality varies by translation complexity.
    # Difficulty levels are assigned by the corpus builder based on
    # word count, clause count, and average word length.
    DIFFICULTY_LABELS = {
        0: "Unrated",
        1: "Easy (Tier 1)",
        2: "Medium (Tier 2)",
        3: "Hard (Tier 3)",
        4: "Very Hard (Tier 4)",
        5: "Expert (Tier 5)",
    }
    # Only display if there are multiple difficulty levels
    # (a single level means the corpus has no difficulty annotations)
    if len(difficulties) > 1:
        # Check if per-tier CIs are available
        tier_cis = overall.get("confidence_intervals_by_tier", {})

        header = f"\n  {'Difficulty':<25s} {'Count':>6s} {'Exact':>7s} {'chrF++':>7s} {'BLEU':>7s}"
        if tier_cis:
            header += f"  {'chrF++ CI':>17s}"
        print(header)

        sep = f"  {'-'*25} {'-----':>6s} {'-----':>7s} {'------':>7s} {'----':>7s}"
        if tier_cis:
            sep += f"  {'-'*17}"
        print(sep)

        for level, sm in sorted(difficulties.items()):
            label = DIFFICULTY_LABELS.get(level, f"Tier {level}")
            line = (
                f"  {label:<25s} "
                f"{sm.count:>6d} "
                f"{sm.exact_match_rate:>6.1%} "
                f"{sm.avg_chrf:>7.1f} "
                f"{sm.avg_bleu:>7.1f}"
            )
            # Append CI if available for this tier
            tier_ci = tier_cis.get(str(level), {}).get("corpus_chrf")
            if tier_ci:
                line += f"  [{tier_ci['ci_lower']:.1f} – {tier_ci['ci_upper']:.1f}]"
            print(line)

    # Plugin metrics
    if "plugin_metrics" in overall:
        print(f"\n  Plugin Metrics:")
        for pname, pdata in overall["plugin_metrics"].items():
            print(f"    [{pname}]")
            if isinstance(pdata, dict):
                for k, v in pdata.items():
                    if isinstance(v, float):
                        print(f"      {k}: {v:.4f}")
                    else:
                        print(f"      {k}: {v}")

    if output_path:
        print(f"\n  Report:       {output_path}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------

def run_test(
    log_path: str,
    output_path: str | None = None,
    metric_plugins: list | None = None,
    compute_ci: bool = True,
    n_bootstrap_ci: int = 1000,
):
    """CLI entry point for the test subcommand."""
    analyze_run(
        log_path,
        output_path,
        metric_plugins=metric_plugins,
        compute_ci=compute_ci,
        n_bootstrap_ci=n_bootstrap_ci,
    )
