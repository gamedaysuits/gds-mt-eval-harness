"""
Scoring — Code mirror of SCORING_SPEC.md (the SSOT for all scoring logic).

This module is the single code authority for:
    - Composite weight tables (SCORING_SPEC §4.3)
    - Input normalization rules (SCORING_SPEC §4.2)
    - Quality tier thresholds (SCORING_SPEC §5.1)
    - Cost-adjusted score formula (SCORING_SPEC §6.3)

Design contract:
    - SCORING_SPEC.md is the SSOT. This module mirrors it in code.
    - When SCORING_SPEC.md changes, update this file to match.
    - test_scoring_ssot.py validates alignment between this file and the spec.
    - No other module should define weights, tiers, or composite logic.
      publish.py, tester.py, and any future consumers import from here.

Why a separate module (not inline in publish.py):
    - Single code location for scoring constants → no duplication drift.
    - Testable in isolation (weight sums, tier boundary checks).
    - SCORING_SPEC §10.2 explicitly defines this file as the code mirror.
"""

from __future__ import annotations

import math


# ---------------------------------------------------------------------------
# §4.3 Profile A — Languages WITH FST Coverage
# ---------------------------------------------------------------------------
# Structural metrics carry 40% (FST 0.25 + morphological 0.15), reflecting
# the primacy of morphological correctness for polysynthetic/agglutinative
# languages.
#
# Source: SCORING_SPEC.md §4.3 "Profile A: Languages WITH FST Coverage"

WEIGHTS_WITH_FST: dict[str, float] = {
    "fst_acceptance_rate":      0.25,
    "morphological_accuracy":   0.15,
    "chrf_plus_plus":           0.15,
    "semantic_score":           0.15,
    "equivalent_match_rate":    0.10,
    "code_switching_rate":      0.05,
    "terminology_adherence":    0.05,
    "hallucination_rate":       0.05,
    "exact_match_rate":         0.05,
}

# ---------------------------------------------------------------------------
# §4.3 Profile B — Languages WITHOUT FST Coverage
# ---------------------------------------------------------------------------
# Without structural validation, semantic and surface metrics carry equal
# weight. orthographic_accuracy fills part of the gap left by absent FST.
#
# Source: SCORING_SPEC.md §4.3 "Profile B: Languages WITHOUT FST Coverage"

WEIGHTS_WITHOUT_FST: dict[str, float] = {
    "semantic_score":           0.25,
    "chrf_plus_plus":           0.25,
    "equivalent_match_rate":    0.15,
    "exact_match_rate":         0.10,
    "code_switching_rate":      0.10,
    "terminology_adherence":    0.05,
    "hallucination_rate":       0.05,
    "orthographic_accuracy":    0.05,
}


# ---------------------------------------------------------------------------
# §4.2 Input Normalization
# ---------------------------------------------------------------------------
# Before entering the composite formula, all metrics must be on a 0.0–1.0
# scale where 1.0 = perfect. Most metrics are already normalized; these are
# the exceptions that need transformation.
#
# Source: SCORING_SPEC.md §4.2 "Input Normalization"

def normalize_metric(metric_name: str, raw_value: float) -> float:
    """Normalize a metric value to 0.0–1.0 scale for composite calculation.

    Applies the normalization rules from SCORING_SPEC §4.2:
        - chrf_plus_plus: divide by 100 (sacrebleu native scale is 0–100)
        - code_switching_rate: invert (0% code-switching = 1.0)
        - hallucination_rate: invert (0% hallucination = 1.0)
        - All others: already 0.0–1.0, pass through unchanged.

    Args:
        metric_name: The metric identifier (must match weight table keys).
        raw_value: The raw metric value.

    Returns:
        Normalized value on 0.0–1.0 scale where 1.0 = perfect.
    """
    if metric_name == "chrf_plus_plus":
        return raw_value / 100.0
    elif metric_name in ("code_switching_rate", "hallucination_rate"):
        # Inverted: 0% bad behavior = 1.0 (perfect)
        return 1.0 - raw_value
    else:
        # exact_match_rate, equivalent_match_rate, fst_acceptance_rate,
        # morphological_accuracy, semantic_score, terminology_adherence,
        # orthographic_accuracy — all already 0.0–1.0
        return raw_value


# Metrics that need normalization, for documentation and testing purposes.
# Maps metric_name → description of normalization applied.
NORMALIZATIONS: dict[str, str] = {
    "chrf_plus_plus":       "Divide by 100 (sacrebleu native scale)",
    "code_switching_rate":  "Invert: 1.0 - value (lower is better)",
    "hallucination_rate":   "Invert: 1.0 - value (lower is better)",
}


# ---------------------------------------------------------------------------
# §5.1 Quality Tier Thresholds
# ---------------------------------------------------------------------------
# Evaluated top-down, first match wins.
# These are heuristic labels on automated scores — not validated quality
# judgments. Only human review can confirm actual usability.
#
# Source: SCORING_SPEC.md §5.1 "Tier Thresholds (Machine-Readable)"

QUALITY_TIERS: list[tuple[float, str]] = [
    (0.85, "fluent"),
    (0.70, "deployable"),
    (0.50, "functional"),
    (0.30, "emerging"),
    (0.00, "baseline"),
]


# ---------------------------------------------------------------------------
# Composite score — SCORING_SPEC §4.1
# ---------------------------------------------------------------------------

def compute_composite_score(
    scores: dict[str, float | None],
    has_fst: bool,
) -> float | None:
    """Compute the weighted composite score per SCORING_SPEC §4.

    The composite is a weighted average of all *available* metrics,
    re-normalized so the weights of available metrics sum to 1.0.
    Metrics are normalized to 0.0–1.0 scale before weighting.

    Args:
        scores: Dict mapping metric names to values. Keys should match
            the weight table names. Values can be None (metric unavailable)
            or numeric. chrF++ should be in its NATIVE scale (0–100) —
            normalization is applied here.
        has_fst: Whether FST coverage is available for this language.
            Selects Profile A (True) or Profile B (False) weights.

    Returns:
        Composite score 0.0–1.0, or None if no metrics are available.
    """
    weights = WEIGHTS_WITH_FST if has_fst else WEIGHTS_WITHOUT_FST

    # Collect (metric_name, normalized_value, weight) for available metrics.
    # A metric is "available" if its value is a number (not None).
    available: list[tuple[str, float, float]] = []
    for metric_name, weight in weights.items():
        raw_value = scores.get(metric_name)
        if raw_value is not None and isinstance(raw_value, (int, float)):
            normalized = normalize_metric(metric_name, raw_value)
            available.append((metric_name, normalized, weight))

    if not available:
        return None

    # Re-normalize weights to sum to 1.0 over available metrics
    total_weight = sum(w for _, _, w in available)
    if total_weight == 0:
        return None

    composite = sum(
        (w / total_weight) * v for _, v, w in available
    )
    return round(composite, 4)


def classify_quality_tier(composite: float | None) -> str:
    """Map a composite score to a quality tier per SCORING_SPEC §5.1.

    Evaluated top-down: first threshold the composite meets or exceeds
    determines the tier. Returns "unscored" if composite is None.

    These are heuristic labels on automated scores — not validated
    quality judgments. Only human review can confirm actual usability.
    No method can claim Deployable or above without community review.
    """
    if composite is None:
        return "unscored"

    for threshold, tier_name in QUALITY_TIERS:
        if composite >= threshold:
            return tier_name

    # Should not reach here if QUALITY_TIERS includes 0.00,
    # but defensive fallback.
    return "baseline"


# ---------------------------------------------------------------------------
# §6.3 Cost-adjusted score
# ---------------------------------------------------------------------------

def cost_adjusted_score(
    composite: float | None,
    cost_per_entry_usd: float | None,
) -> float | None:
    """Compute cost-adjusted score per SCORING_SPEC §6.3.

    Formula:
        cost_adjusted = composite / log2(1 + cost_per_entry_usd × 1000)

    This rewards methods that achieve good scores efficiently.
    Uses cost_per_entry (not per-token) because the cost-adjusted score
    is always computed within a single benchmark (same corpus).

    At very low cost ($0.001/entry), log2(1 + 1) = 1.0, so
    cost_adjusted ≈ composite. The penalty only kicks in meaningfully
    above ~$0.001/entry.

    Returns None if composite or cost is unavailable, or if cost is zero
    (the formula is undefined when cost produces log2(1) = 0).
    """
    if composite is None or cost_per_entry_usd is None:
        return None
    if cost_per_entry_usd <= 0:
        # At zero cost, no penalty — return composite directly.
        # This avoids log2(1) = 0 division issues.
        return round(composite, 4)

    denominator = math.log2(1.0 + cost_per_entry_usd * 1000.0)
    if denominator == 0:
        return round(composite, 4)

    return round(composite / denominator, 4)
