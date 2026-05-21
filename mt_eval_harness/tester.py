"""
Test Harness — Deterministic metric analyzer for RunLog files.

Takes a RunLog JSON from the Run Harness and computes:
    - Exact match rate (string equality after normalization)
    - chrF++ score (via sacrebleu, optional)
    - BLEU score (via sacrebleu, optional)
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
    - Dependencies: sacrebleu. Everything else is plugin.
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
    predicted: str = "" # Model output
    segment: str = ""
    difficulty: int = 0

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
) -> dict:
    """Analyze a RunLog and produce a TestReport.

    Args:
        log_path: Path to the RunLog JSON file.
        output_path: Optional output path for the TestReport.
                     Defaults to log_path with _report.json suffix.
        metric_plugins: Optional list of MetricPlugin instances.
                        Each plugin's compute() is called per entry,
                        and aggregate() is called for overall metrics.

    Returns:
        Complete TestReport dict.
    """
    log_path = Path(log_path)
    if not log_path.exists():
        raise FileNotFoundError(f"RunLog not found: {log_path}")

    run_log = json.loads(log_path.read_text(encoding="utf-8"))
    results = run_log.get("results", [])

    if not results:
        print("  WARNING: RunLog contains no results")
        return {"error": "No results in RunLog"}

    print(f"  Analyzing {len(results)} entries from {log_path.name}")

    # Setup sacrebleu metrics if available
    chrf_metric = CHRF(word_order=2)
    bleu_metric = BLEU()

    plugins = metric_plugins or []
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
            predicted=r.get("predicted", ""),
            segment=r.get("segment", ""),
            difficulty=r.get("difficulty", 0),
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
        "source_log": str(log_path),
        "run_id": run_log.get("run_id", "unknown"),
        "config": run_log.get("config", {}),
        "overall": overall,
        "by_segment": {k: asdict(v) for k, v in segments.items()},
        "by_difficulty": {str(k): asdict(v) for k, v in sorted(difficulties.items())},
        "entries": [asdict(em) for em in entry_metrics],
    }

    # --- Write output ---
    if output_path is None:
        output_path = log_path.with_name(log_path.stem + "_report.json")
    else:
        output_path = Path(output_path)

    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # --- Print summary ---
    _print_summary(overall, segments, difficulties, output_path)

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
    output_path: Path,
):
    """Print human-readable summary to console."""
    print("\n" + "=" * 60)
    print("TEST REPORT SUMMARY")
    print("=" * 60)

    n = overall["evaluated"]
    print(f"\n  Total entries:    {overall['total_entries']}")
    print(f"  Errors:           {overall['error_count']}")
    print(f"  Evaluated:        {n}")
    print(f"\n  Exact match:      {overall['exact_match_count']}/{n} "
          f"({overall['exact_match_rate']:.1%})")
    print(f"  Miss:             {overall['miss_count']}/{n} "
          f"({overall['miss_rate']:.1%})")

    if "corpus_chrf" in overall:
        print(f"\n  Corpus chrF++:    {overall['corpus_chrf']:.1f}")
    if "corpus_bleu" in overall:
        print(f"  Corpus BLEU:      {overall['corpus_bleu']:.1f}")

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

    print(f"\n  Report written to: {output_path}")
    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------

def run_test(
    log_path: str,
    output_path: str | None = None,
    metric_plugins: list | None = None,
):
    """CLI entry point for the test subcommand."""
    analyze_run(log_path, output_path, metric_plugins=metric_plugins)
