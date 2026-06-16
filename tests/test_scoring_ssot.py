"""
Test that scoring.py stays in sync with SCORING_SPEC.md.

This test suite validates the SSOT chain:
    SCORING_SPEC.md (human-readable spec)
        → scoring.py (code mirror)
        → this test (validates alignment)

If these tests fail, it means scoring.py has drifted from the spec.
Update scoring.py to match SCORING_SPEC.md, then re-run.
"""

import math

from mt_eval_harness.scoring import (
    NORMALIZATIONS,
    QUALITY_TIERS,
    WEIGHTS_WITH_FST,
    WEIGHTS_WITHOUT_FST,
    classify_quality_tier,
    compute_composite_score,
    cost_adjusted_score,
    normalize_metric,
)


# ---------------------------------------------------------------------------
# §4.3 Weight table invariants
# ---------------------------------------------------------------------------

class TestWeightTables:
    """Validate weight tables match SCORING_SPEC §4.3."""

    def test_profile_a_weights_sum_to_one(self):
        """Profile A (with FST) weights must sum to exactly 1.0."""
        total = sum(WEIGHTS_WITH_FST.values())
        assert round(total, 10) == 1.0, (
            f"Profile A weights sum to {total}, expected 1.0. "
            f"Update scoring.py to match SCORING_SPEC §4.3."
        )

    def test_profile_b_weights_sum_to_one(self):
        """Profile B (without FST) weights must sum to exactly 1.0."""
        total = sum(WEIGHTS_WITHOUT_FST.values())
        assert round(total, 10) == 1.0, (
            f"Profile B weights sum to {total}, expected 1.0. "
            f"Update scoring.py to match SCORING_SPEC §4.3."
        )

    def test_profile_a_has_9_metrics(self):
        """SCORING_SPEC §4.3 Profile A defines exactly 9 metrics."""
        assert len(WEIGHTS_WITH_FST) == 9, (
            f"Profile A has {len(WEIGHTS_WITH_FST)} metrics, expected 9. "
            f"Check SCORING_SPEC §4.3."
        )

    def test_profile_b_has_8_metrics(self):
        """SCORING_SPEC §4.3 Profile B defines exactly 8 metrics."""
        assert len(WEIGHTS_WITHOUT_FST) == 8, (
            f"Profile B has {len(WEIGHTS_WITHOUT_FST)} metrics, expected 8. "
            f"Check SCORING_SPEC §4.3."
        )

    def test_profile_a_contains_fst_metrics(self):
        """Profile A must include FST-specific structural metrics."""
        assert "fst_acceptance_rate" in WEIGHTS_WITH_FST
        assert "morphological_accuracy" in WEIGHTS_WITH_FST

    def test_profile_b_excludes_fst_metrics(self):
        """Profile B must NOT include FST-specific metrics."""
        assert "fst_acceptance_rate" not in WEIGHTS_WITHOUT_FST
        assert "morphological_accuracy" not in WEIGHTS_WITHOUT_FST

    def test_all_weights_are_positive(self):
        """All weights must be positive (no zero-weight metrics in the table)."""
        for name, w in WEIGHTS_WITH_FST.items():
            assert w > 0, f"Profile A metric '{name}' has non-positive weight {w}"
        for name, w in WEIGHTS_WITHOUT_FST.items():
            assert w > 0, f"Profile B metric '{name}' has non-positive weight {w}"

    def test_profile_a_structural_metrics_carry_40_percent(self):
        """SCORING_SPEC §4.3: FST + morphological accuracy = 40% in Profile A."""
        structural = (
            WEIGHTS_WITH_FST.get("fst_acceptance_rate", 0)
            + WEIGHTS_WITH_FST.get("morphological_accuracy", 0)
        )
        assert round(structural, 10) == 0.40, (
            f"Structural metrics carry {structural}, expected 0.40. "
            f"Check SCORING_SPEC §4.3 Profile A."
        )

    def test_profile_a_specific_weights(self):
        """Validate each Profile A weight matches SCORING_SPEC §4.3."""
        expected = {
            "fst_acceptance_rate": 0.25,
            "morphological_accuracy": 0.15,
            "chrf_plus_plus": 0.15,
            "semantic_score": 0.15,
            "equivalent_match_rate": 0.10,
            "code_switching_rate": 0.05,
            "terminology_adherence": 0.05,
            "hallucination_rate": 0.05,
            "exact_match_rate": 0.05,
        }
        assert WEIGHTS_WITH_FST == expected, (
            f"Profile A weights differ from SCORING_SPEC §4.3.\n"
            f"  Expected: {expected}\n"
            f"  Got:      {dict(WEIGHTS_WITH_FST)}"
        )

    def test_profile_b_specific_weights(self):
        """Validate each Profile B weight matches SCORING_SPEC §4.3."""
        expected = {
            "semantic_score": 0.25,
            "chrf_plus_plus": 0.25,
            "equivalent_match_rate": 0.15,
            "exact_match_rate": 0.10,
            "code_switching_rate": 0.10,
            "terminology_adherence": 0.05,
            "hallucination_rate": 0.05,
            "orthographic_accuracy": 0.05,
        }
        assert WEIGHTS_WITHOUT_FST == expected, (
            f"Profile B weights differ from SCORING_SPEC §4.3.\n"
            f"  Expected: {expected}\n"
            f"  Got:      {dict(WEIGHTS_WITHOUT_FST)}"
        )


# ---------------------------------------------------------------------------
# §4.2 Normalization
# ---------------------------------------------------------------------------

class TestNormalization:
    """Validate normalization rules match SCORING_SPEC §4.2."""

    def test_chrf_divided_by_100(self):
        """chrF++ native 0–100 scale → 0.0–1.0."""
        assert normalize_metric("chrf_plus_plus", 100.0) == 1.0
        assert normalize_metric("chrf_plus_plus", 0.0) == 0.0
        assert normalize_metric("chrf_plus_plus", 72.5) == 0.725

    def test_code_switching_inverted(self):
        """Code-switching rate: 0% = perfect (1.0), 100% = worst (0.0)."""
        assert normalize_metric("code_switching_rate", 0.0) == 1.0
        assert normalize_metric("code_switching_rate", 1.0) == 0.0
        assert normalize_metric("code_switching_rate", 0.1) == 0.9

    def test_hallucination_inverted(self):
        """Hallucination rate: 0% = perfect (1.0), 100% = worst (0.0)."""
        assert normalize_metric("hallucination_rate", 0.0) == 1.0
        assert normalize_metric("hallucination_rate", 1.0) == 0.0

    def test_passthrough_metrics(self):
        """Metrics already on 0.0–1.0 scale pass through unchanged."""
        passthrough = [
            "exact_match_rate", "equivalent_match_rate",
            "fst_acceptance_rate", "morphological_accuracy",
            "semantic_score", "terminology_adherence",
            "orthographic_accuracy",
        ]
        for metric in passthrough:
            assert normalize_metric(metric, 0.75) == 0.75, (
                f"{metric} should pass through unchanged"
            )


# ---------------------------------------------------------------------------
# §5.1 Quality tier thresholds
# ---------------------------------------------------------------------------

class TestQualityTiers:
    """Validate tier thresholds match SCORING_SPEC §5.1."""

    def test_tier_count(self):
        """SCORING_SPEC §5.1 defines exactly 5 tiers."""
        assert len(QUALITY_TIERS) == 5

    def test_tier_thresholds(self):
        """Validate exact threshold values from SCORING_SPEC §5.1."""
        expected = [
            (0.85, "fluent"),
            (0.70, "deployable"),
            (0.50, "functional"),
            (0.30, "emerging"),
            (0.00, "baseline"),
        ]
        assert QUALITY_TIERS == expected

    def test_classification_boundary_fluent(self):
        assert classify_quality_tier(0.85) == "fluent"
        assert classify_quality_tier(0.95) == "fluent"
        assert classify_quality_tier(1.0) == "fluent"

    def test_classification_boundary_deployable(self):
        assert classify_quality_tier(0.70) == "deployable"
        assert classify_quality_tier(0.84) == "deployable"

    def test_classification_boundary_functional(self):
        assert classify_quality_tier(0.50) == "functional"
        assert classify_quality_tier(0.69) == "functional"

    def test_classification_boundary_emerging(self):
        assert classify_quality_tier(0.30) == "emerging"
        assert classify_quality_tier(0.49) == "emerging"

    def test_classification_boundary_baseline(self):
        assert classify_quality_tier(0.0) == "baseline"
        assert classify_quality_tier(0.29) == "baseline"

    def test_classification_none(self):
        assert classify_quality_tier(None) == "unscored"


# ---------------------------------------------------------------------------
# §4.1 Composite score computation
# ---------------------------------------------------------------------------

class TestCompositeScore:
    """Validate composite score computation matches SCORING_SPEC §4.1."""

    def test_no_metrics_returns_none(self):
        """Empty input → None (no composite possible)."""
        assert compute_composite_score({}, has_fst=True) is None

    def test_all_none_returns_none(self):
        """All metrics None → None."""
        scores = {k: None for k in WEIGHTS_WITH_FST}
        assert compute_composite_score(scores, has_fst=True) is None

    def test_single_metric_equals_that_metric(self):
        """With one metric, composite = that metric's normalized value."""
        # chrF++ 80.0 → normalized 0.8. Only metric → composite = 0.8
        result = compute_composite_score(
            {"chrf_plus_plus": 80.0}, has_fst=True
        )
        assert result == 0.8

    def test_renormalization_with_partial_metrics(self):
        """Re-normalization: effective weights must sum to 1.0 over available."""
        # Profile A: FST=0.25, chrF=0.15, EM=0.05 → sum=0.45
        # Effective: FST=0.5556, chrF=0.3333, EM=0.1111
        scores = {
            "fst_acceptance_rate": 1.0,  # already normalized
            "chrf_plus_plus": 80.0,      # → 0.8 after normalization
            "exact_match_rate": 0.6,     # already normalized
        }
        result = compute_composite_score(scores, has_fst=True)
        # Expected: 0.5556*1.0 + 0.3333*0.8 + 0.1111*0.6 = 0.8889
        assert result == 0.8889

    def test_profile_b_selection(self):
        """has_fst=False selects Profile B weights."""
        scores = {
            "chrf_plus_plus": 80.0,      # → 0.8
            "exact_match_rate": 0.6,
        }
        result = compute_composite_score(scores, has_fst=False)
        # Profile B: chrF=0.25, EM=0.10 → sum=0.35
        # Effective: chrF=0.7143, EM=0.2857
        # Expected: 0.7143*0.8 + 0.2857*0.6 = 0.7429
        expected = round(
            (0.25 / 0.35) * 0.8 + (0.10 / 0.35) * 0.6,
            4
        )
        assert result == expected

    def test_perfect_scores_all_metrics(self):
        """All metrics at perfect → composite = 1.0."""
        scores = {
            "fst_acceptance_rate": 1.0,
            "morphological_accuracy": 1.0,
            "chrf_plus_plus": 100.0,       # normalized to 1.0
            "semantic_score": 1.0,
            "equivalent_match_rate": 1.0,
            "code_switching_rate": 0.0,     # inverted to 1.0
            "terminology_adherence": 1.0,
            "hallucination_rate": 0.0,      # inverted to 1.0
            "exact_match_rate": 1.0,
        }
        result = compute_composite_score(scores, has_fst=True)
        assert result == 1.0


# ---------------------------------------------------------------------------
# §6.3 Cost-adjusted score
# ---------------------------------------------------------------------------

class TestCostAdjustedScore:
    """Validate cost-adjusted formula matches SCORING_SPEC §6.3."""

    def test_zero_cost_returns_composite(self):
        """At zero cost, no penalty — returns composite as-is."""
        assert cost_adjusted_score(0.75, 0.0) == 0.75

    def test_none_composite_returns_none(self):
        assert cost_adjusted_score(None, 0.01) is None

    def test_none_cost_returns_none(self):
        assert cost_adjusted_score(0.75, None) is None

    def test_formula_at_known_value(self):
        """Verify: cost_adjusted = composite / log2(1 + cost × 1000)."""
        composite = 0.75
        cost = 0.01
        expected = composite / math.log2(1.0 + cost * 1000.0)
        assert cost_adjusted_score(composite, cost) == round(expected, 4)

    def test_low_cost_minimal_penalty(self):
        """At $0.001/entry, log2(1+1)=1.0, so cost_adjusted ≈ composite."""
        result = cost_adjusted_score(0.80, 0.001)
        assert result == 0.80
