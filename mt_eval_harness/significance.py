"""
Statistical significance testing via paired bootstrap resampling.

Standard method used by WMT shared tasks, SacreBLEU, and MT-Lens.
Compares two runs on the same corpus to determine if the performance
difference is statistically significant.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from sacrebleu.metrics import CHRF, BLEU


@dataclass
class SignificanceResult:
    """Result of a paired bootstrap significance test."""
    metric_name: str           # e.g., "corpus_chrf", "exact_match_rate"
    system_a_score: float      # Score for system A
    system_b_score: float      # Score for system B
    delta: float               # A - B
    p_value: float             # Two-sided p-value
    n_bootstrap: int           # Number of bootstrap iterations
    confidence_level: float    # 1 - alpha
    significant: bool          # p_value < alpha
    winner: str | None         # "A", "B", or None if not significant
    ci_lower: float            # Lower bound of 95% CI on the delta
    ci_upper: float            # Upper bound of 95% CI on the delta


def paired_bootstrap(
    entries_a: list[dict],
    entries_b: list[dict],
    metric_fn: callable,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 12345,
    metric_name: str = "metric",
) -> SignificanceResult:
    """Run paired bootstrap resampling significance test.

    Args:
        entries_a: Per-entry results from system A (from TestReport["entries"])
        entries_b: Per-entry results from system B (must be same length, same IDs)
        metric_fn: Function(list[dict]) -> float that computes the corpus-level
                   metric from a list of entry dicts.
        n_bootstrap: Number of bootstrap iterations (1000 is standard)
        alpha: Significance level (0.05 = 95% confidence)
        seed: RNG seed for reproducibility (12345 matches SacreBLEU default)
        metric_name: Human-readable name for the metric being tested

    Returns:
        SignificanceResult with all fields populated.

    Raises:
        ValueError: If entries_a and entries_b have different lengths or IDs.
    """
    # Validate inputs
    if len(entries_a) != len(entries_b):
        raise ValueError(
            f"Entry count mismatch: A has {len(entries_a)}, B has {len(entries_b)}"
        )

    if not entries_a:
        return SignificanceResult(
            metric_name=metric_name,
            system_a_score=0.0,
            system_b_score=0.0,
            delta=0.0,
            p_value=1.0,
            n_bootstrap=n_bootstrap,
            confidence_level=1.0 - alpha,
            significant=False,
            winner=None,
            ci_lower=0.0,
            ci_upper=0.0,
        )

    # Validate matching IDs
    ids_a = [e.get("id") for e in entries_a]
    ids_b = [e.get("id") for e in entries_b]
    if ids_a != ids_b:
        raise ValueError(
            "Entry IDs do not match between systems A and B. "
            "Both must be evaluated on the same entries in the same order."
        )

    n = len(entries_a)

    # Compute actual scores
    score_a = metric_fn(entries_a)
    score_b = metric_fn(entries_b)
    actual_delta = score_a - score_b

    # Bootstrap resampling
    rng = random.Random(seed)
    bootstrap_deltas = []
    opposite_count = 0

    for _ in range(n_bootstrap):
        # Sample indices with replacement
        indices = [rng.randint(0, n - 1) for _ in range(n)]

        # Build bootstrap samples
        sample_a = [entries_a[i] for i in indices]
        sample_b = [entries_b[i] for i in indices]

        # Compute metric on bootstrap samples
        boot_score_a = metric_fn(sample_a)
        boot_score_b = metric_fn(sample_b)
        boot_delta = boot_score_a - boot_score_b

        bootstrap_deltas.append(boot_delta)

        # Count opposite-sign deltas for p-value
        # If actual_delta > 0, count boot_delta <= 0 (and vice versa)
        if actual_delta > 0 and boot_delta <= 0:
            opposite_count += 1
        elif actual_delta < 0 and boot_delta >= 0:
            opposite_count += 1
        elif actual_delta == 0:
            # If no actual difference, every bootstrap is "opposite" → p=1.0
            opposite_count += 1

    p_value = opposite_count / n_bootstrap

    # Confidence interval on the delta
    bootstrap_deltas.sort()
    ci_lower_idx = int(n_bootstrap * (alpha / 2))
    ci_upper_idx = int(n_bootstrap * (1 - alpha / 2)) - 1
    ci_lower = bootstrap_deltas[ci_lower_idx]
    ci_upper = bootstrap_deltas[ci_upper_idx]

    significant = p_value < alpha
    if significant:
        winner = "A" if actual_delta > 0 else "B"
    else:
        winner = None

    return SignificanceResult(
        metric_name=metric_name,
        system_a_score=round(score_a, 4),
        system_b_score=round(score_b, 4),
        delta=round(actual_delta, 4),
        p_value=round(p_value, 4),
        n_bootstrap=n_bootstrap,
        confidence_level=round(1.0 - alpha, 2),
        significant=significant,
        winner=winner,
        ci_lower=round(ci_lower, 4),
        ci_upper=round(ci_upper, 4),
    )


# ---------------------------------------------------------------------------
# Built-in metric functions
# ---------------------------------------------------------------------------

def exact_match_rate(entries: list[dict]) -> float:
    """Compute exact match rate from a list of entry dicts."""
    non_error = [e for e in entries if not e.get("error")]
    if not non_error:
        return 0.0
    exact = sum(1 for e in non_error if e.get("exact_match"))
    return exact / len(non_error)


def corpus_chrf(entries: list[dict]) -> float:
    """Compute corpus-level chrF++ from a list of entry dicts."""
    chrf = CHRF(word_order=2)
    refs = [e["expected"] for e in entries if e.get("expected", "").strip()]
    hyps = [e["predicted"] if e.get("predicted", "").strip() else "EMPTY"
            for e in entries if e.get("expected", "").strip()]
    if not refs:
        return 0.0
    return chrf.corpus_score(hyps, [refs]).score


def corpus_bleu(entries: list[dict]) -> float:
    """Compute corpus-level BLEU from a list of entry dicts."""
    bleu = BLEU()
    refs = [e["expected"] for e in entries if e.get("expected", "").strip()]
    hyps = [e["predicted"] if e.get("predicted", "").strip() else "EMPTY"
            for e in entries if e.get("expected", "").strip()]
    if not refs:
        return 0.0
    return bleu.corpus_score(hyps, [refs]).score


def fst_acceptance_rate(entries: list[dict]) -> float:
    """Compute FST acceptance rate from a list of entry dicts.

    Each entry may have FST validity data under plugin_metrics, stored
    under 'giellalt_fst_validity' (current) or 'crk_fst_validity' (legacy).
    The value is a float 0.0–1.0 representing the proportion of FST-valid
    words in that entry's output. We average these across entries that have
    FST data and are not errors.

    Returns 0.0 if no entries have FST data. This function is designed
    for bootstrap resampling — it can be called on any subset of entries.
    """
    fst_values = []
    for entry in entries:
        if entry.get("error"):
            continue
        plugin_metrics = entry.get("plugin_metrics", {})
        if not isinstance(plugin_metrics, dict):
            continue
        # Check both current and legacy FST plugin keys
        fst_data = plugin_metrics.get("giellalt_fst_validity") or plugin_metrics.get("crk_fst_validity", {})
        if not isinstance(fst_data, dict):
            continue
        fst_val = fst_data.get("fst_validity")
        if isinstance(fst_val, (int, float)):
            fst_values.append(float(fst_val))
    if not fst_values:
        return 0.0
    return sum(fst_values) / len(fst_values)


def composite_score(entries: list[dict]) -> float:
    """Compute composite score from a list of entry dicts.

    For bootstrap resampling, we need to recompute all component metrics
    on the resampled entries and then call compute_composite_score() from
    scoring.py with the recomputed values.

    This ensures the bootstrap correctly captures the variance in the
    composite, including the correlation structure between its components.

    Returns 0.0 if no composite can be computed (e.g., no valid entries).
    """
    # Import here to avoid circular imports at module level.
    # scoring.py does not import significance.py.
    from mt_eval_harness.scoring import compute_composite_score

    non_error = [e for e in entries if not e.get("error")]
    if not non_error:
        return 0.0

    # Recompute component metrics on this (possibly resampled) entry set.
    # chrF++ in native sacrebleu scale (0–100); scoring.py normalizes it.
    chrf_val = corpus_chrf(non_error)
    em_val = exact_match_rate(non_error)
    fst_val = fst_acceptance_rate(non_error)

    # Determine whether FST data is present in this sample
    # Check both current (giellalt_fst_validity) and legacy (crk_fst_validity) keys
    has_fst = any(
        isinstance(
            e.get("plugin_metrics", {}).get("giellalt_fst_validity")
            or e.get("plugin_metrics", {}).get("crk_fst_validity", {}),
            dict,
        )
        and isinstance(
            (e.get("plugin_metrics", {}).get("giellalt_fst_validity")
             or e.get("plugin_metrics", {}).get("crk_fst_validity", {})
             ).get("fst_validity"),
            (int, float),
        )
        for e in non_error
    )

    # Build the scores dict expected by compute_composite_score.
    # Only include metrics that are actually available in the entries.
    scores = {
        "chrf_plus_plus": chrf_val,
        "exact_match_rate": em_val,
    }
    if has_fst:
        scores["fst_acceptance_rate"] = fst_val

    result = compute_composite_score(scores, has_fst=has_fst)
    # compute_composite_score returns None if no metrics are available
    return result if result is not None else 0.0


# ---------------------------------------------------------------------------
# Convenience: run all standard significance tests
# ---------------------------------------------------------------------------

def run_significance_tests(
    report_a: dict,
    report_b: dict,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 12345,
) -> list[SignificanceResult]:
    """Run paired bootstrap significance tests on all standard metrics.

    Compares two TestReport dicts on exact_match_rate, corpus_chrf, and
    corpus_bleu. Also tests any plugin metrics that appear in BOTH reports.

    Args:
        report_a: First TestReport dict
        report_b: Second TestReport dict
        n_bootstrap: Number of bootstrap iterations
        alpha: Significance level
        seed: RNG seed for reproducibility

    Returns:
        List of SignificanceResult, one per metric tested.
    """
    entries_a = report_a.get("entries", [])
    entries_b = report_b.get("entries", [])

    # Align entries by ID — only test on the intersection
    ids_a = {e["id"]: e for e in entries_a}
    ids_b = {e["id"]: e for e in entries_b}
    common_ids = sorted(set(ids_a.keys()) & set(ids_b.keys()))

    if len(common_ids) < len(entries_a) or len(common_ids) < len(entries_b):
        excluded_a = len(entries_a) - len(common_ids)
        excluded_b = len(entries_b) - len(common_ids)
        if excluded_a or excluded_b:
            print(f"  NOTE: Testing on {len(common_ids)} common entries "
                  f"(excluded {excluded_a} from A, {excluded_b} from B)")

    if len(common_ids) < 10:
        print(f"  ⚠️  WARNING: Only {len(common_ids)} common entries — "
              f"significance tests may be unreliable with so few entries.")

    aligned_a = [ids_a[eid] for eid in common_ids]
    aligned_b = [ids_b[eid] for eid in common_ids]

    results = []

    # Standard metrics
    for metric_fn, name in [
        (corpus_chrf, "corpus_chrf"),
        (exact_match_rate, "exact_match_rate"),
        (corpus_bleu, "corpus_bleu"),
    ]:
        result = paired_bootstrap(
            aligned_a, aligned_b,
            metric_fn=metric_fn,
            n_bootstrap=n_bootstrap,
            alpha=alpha,
            seed=seed,
            metric_name=name,
        )
        results.append(result)

    # Plugin metrics — test any numeric plugin metrics present in both reports
    plugins_a = report_a.get("overall", {}).get("plugin_metrics", {})
    plugins_b = report_b.get("overall", {}).get("plugin_metrics", {})
    common_plugins = set(plugins_a.keys()) & set(plugins_b.keys())

    for plugin_name in sorted(common_plugins):
        pa = plugins_a[plugin_name]
        pb = plugins_b[plugin_name]
        if not isinstance(pa, dict) or not isinstance(pb, dict):
            continue
        # Find numeric keys common to both
        common_keys = set(pa.keys()) & set(pb.keys())
        for key in sorted(common_keys):
            if not isinstance(pa[key], (int, float)) or not isinstance(pb[key], (int, float)):
                continue

            # Build a metric function that extracts this plugin metric per-entry
            def _make_plugin_fn(pname, pkey):
                def fn(entries):
                    vals = []
                    for e in entries:
                        pm = e.get("plugin_metrics", {})
                        if isinstance(pm, dict) and pname in pm:
                            pd = pm[pname]
                            if isinstance(pd, dict) and pkey in pd:
                                v = pd[pkey]
                                if isinstance(v, (int, float)):
                                    vals.append(v)
                    return sum(vals) / len(vals) if vals else 0.0
                return fn

            metric_fn = _make_plugin_fn(plugin_name, key)
            result = paired_bootstrap(
                aligned_a, aligned_b,
                metric_fn=metric_fn,
                n_bootstrap=n_bootstrap,
                alpha=alpha,
                seed=seed,
                metric_name=f"{plugin_name}.{key}",
            )
            results.append(result)

    return results


def format_significance_table(results: list[SignificanceResult]) -> str:
    """Format significance results as a human-readable table."""
    lines = [
        "",
        "  Significance Tests (paired bootstrap, "
        f"n={results[0].n_bootstrap if results else '?'}, "
        f"α={1 - results[0].confidence_level if results else '?'}):",
        "",
        f"  {'Metric':<25s} {'A':>8s} {'B':>8s} {'Δ':>8s} {'p-value':>8s} {'Sig?':>5s}",
        f"  {'-'*25} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*5}",
    ]
    for r in results:
        sig_marker = "Yes *" if r.significant else "No"
        delta_str = f"{'+' if r.delta >= 0 else ''}{r.delta:.2f}"
        lines.append(
            f"  {r.metric_name:<25s} "
            f"{r.system_a_score:>8.2f} "
            f"{r.system_b_score:>8.2f} "
            f"{delta_str:>8s} "
            f"{r.p_value:>8.3f} "
            f"{sig_marker:>5s}"
        )
    lines.append("")
    return "\n".join(lines)
