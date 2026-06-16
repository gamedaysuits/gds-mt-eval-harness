"""Tests for statistical significance testing via paired bootstrap."""

import pytest
from mt_eval_harness.significance import (
    SignificanceResult,
    paired_bootstrap,
    exact_match_rate,
    corpus_chrf,
    corpus_bleu,
    run_significance_tests,
    format_significance_table,
)


# ---------------------------------------------------------------------------
# Fixtures: mock entry dicts matching TestReport format
# ---------------------------------------------------------------------------

def _make_entry(id: int, expected: str, predicted: str,
                exact_match: bool = False, error: str = None) -> dict:
    """Create a minimal entry dict matching TestReport format."""
    return {
        "id": id,
        "source": f"source_{id}",
        "expected": expected,
        "predicted": predicted,
        "exact_match": exact_match,
        "chrf_score": 0.0,
        "bleu_score": 0.0,
        "error": error,
        "plugin_metrics": {},
    }


def _make_perfect_entries(n: int = 50) -> list[dict]:
    """Create entries where all predictions exactly match expected."""
    return [
        _make_entry(i, f"word_{i}", f"word_{i}", exact_match=True)
        for i in range(n)
    ]


def _make_failing_entries(n: int = 50) -> list[dict]:
    """Create entries where all predictions are wrong."""
    return [
        _make_entry(i, f"word_{i}", f"wrong_{i}", exact_match=False)
        for i in range(n)
    ]


def _make_report(entries: list[dict]) -> dict:
    """Wrap entries in a minimal TestReport structure."""
    return {
        "run_id": "test-run",
        "overall": {
            "total_entries": len(entries),
            "evaluated": len([e for e in entries if not e.get("error")]),
        },
        "entries": entries,
    }


# ---------------------------------------------------------------------------
# Test: deterministic with seed
# ---------------------------------------------------------------------------

class TestDeterminism:
    """Same inputs + same seed = same p-value, every time."""

    def test_same_seed_same_result(self):
        a = _make_perfect_entries(30)
        b = _make_failing_entries(30)

        r1 = paired_bootstrap(a, b, exact_match_rate, seed=42, metric_name="em")
        r2 = paired_bootstrap(a, b, exact_match_rate, seed=42, metric_name="em")

        assert r1.p_value == r2.p_value
        assert r1.delta == r2.delta
        assert r1.ci_lower == r2.ci_lower
        assert r1.ci_upper == r2.ci_upper

    def test_different_seed_may_differ(self):
        a = _make_perfect_entries(30)
        b = _make_failing_entries(30)

        r1 = paired_bootstrap(a, b, exact_match_rate, seed=42, metric_name="em")
        r2 = paired_bootstrap(a, b, exact_match_rate, seed=99, metric_name="em")

        # With 100% vs 0% match, both seeds should agree on significance
        assert r1.significant == r2.significant


# ---------------------------------------------------------------------------
# Test: identical scores → p_value = 1.0
# ---------------------------------------------------------------------------

class TestIdenticalSystems:
    """Two identical result sets → p_value = 1.0."""

    def test_identical_entries(self):
        entries = _make_perfect_entries(50)
        result = paired_bootstrap(
            entries, entries, exact_match_rate,
            n_bootstrap=500, metric_name="em"
        )
        assert result.p_value == 1.0
        assert result.significant is False
        assert result.winner is None
        assert result.delta == 0.0


# ---------------------------------------------------------------------------
# Test: clearly significant difference
# ---------------------------------------------------------------------------

class TestClearlySignificant:
    """One system is clearly better → p_value ≈ 0.0."""

    def test_perfect_vs_failing(self):
        a = _make_perfect_entries(50)
        b = _make_failing_entries(50)

        result = paired_bootstrap(
            a, b, exact_match_rate,
            n_bootstrap=1000, metric_name="em"
        )
        assert result.p_value < 0.01
        assert result.significant is True
        assert result.winner == "A"
        assert result.delta > 0.9  # Should be ~1.0

    def test_failing_vs_perfect(self):
        a = _make_failing_entries(50)
        b = _make_perfect_entries(50)

        result = paired_bootstrap(
            a, b, exact_match_rate,
            n_bootstrap=1000, metric_name="em"
        )
        assert result.p_value < 0.01
        assert result.significant is True
        assert result.winner == "B"
        assert result.delta < -0.9


# ---------------------------------------------------------------------------
# Test: mismatched entries
# ---------------------------------------------------------------------------

class TestMismatchedEntries:
    """Mismatched IDs should raise ValueError."""

    def test_different_lengths(self):
        a = _make_perfect_entries(10)
        b = _make_perfect_entries(20)

        with pytest.raises(ValueError, match="Entry count mismatch"):
            paired_bootstrap(a, b, exact_match_rate, metric_name="em")

    def test_different_ids(self):
        a = [_make_entry(i, f"w_{i}", f"w_{i}", True) for i in range(10)]
        b = [_make_entry(i + 100, f"w_{i}", f"w_{i}", True) for i in range(10)]

        with pytest.raises(ValueError, match="Entry IDs do not match"):
            paired_bootstrap(a, b, exact_match_rate, metric_name="em")


# ---------------------------------------------------------------------------
# Test: empty inputs
# ---------------------------------------------------------------------------

class TestEmptyInputs:
    """Empty inputs should handle gracefully."""

    def test_empty_entries(self):
        result = paired_bootstrap([], [], exact_match_rate, metric_name="em")
        assert result.p_value == 1.0
        assert result.significant is False


# ---------------------------------------------------------------------------
# Test: metric functions
# ---------------------------------------------------------------------------

class TestMetricFunctions:
    """Test the built-in metric functions."""

    def test_exact_match_rate_all_match(self):
        entries = _make_perfect_entries(10)
        assert exact_match_rate(entries) == 1.0

    def test_exact_match_rate_none_match(self):
        entries = _make_failing_entries(10)
        assert exact_match_rate(entries) == 0.0

    def test_exact_match_rate_with_errors(self):
        entries = [
            _make_entry(0, "a", "a", True),
            _make_entry(1, "b", "b", True),
            _make_entry(2, "c", "wrong", False, error="API error"),
        ]
        # Error entries are excluded: 2 matches / 2 non-error = 1.0
        assert exact_match_rate(entries) == 1.0

    def test_corpus_chrf_identical(self):
        entries = _make_perfect_entries(5)
        score = corpus_chrf(entries)
        assert score == 100.0  # Perfect match → chrF++ = 100

    def test_corpus_bleu_identical(self):
        # BLEU requires multi-word sentences due to 4-gram matching
        entries = [
            _make_entry(i, f"the quick brown fox jumps {i}",
                        f"the quick brown fox jumps {i}", exact_match=True)
            for i in range(10)
        ]
        score = corpus_bleu(entries)
        assert score > 90.0  # Near-perfect match on multi-word sentences


# ---------------------------------------------------------------------------
# Test: run_significance_tests
# ---------------------------------------------------------------------------

class TestRunSignificanceTests:
    """Test the convenience function that runs all standard tests."""

    def test_returns_three_standard_metrics(self):
        a = _make_report(_make_perfect_entries(20))
        b = _make_report(_make_failing_entries(20))

        results = run_significance_tests(a, b, n_bootstrap=100)
        metric_names = [r.metric_name for r in results]

        assert "corpus_chrf" in metric_names
        assert "exact_match_rate" in metric_names
        assert "corpus_bleu" in metric_names

    def test_handles_partial_overlap(self):
        # A has entries 0-9, B has entries 5-14
        a_entries = [_make_entry(i, f"w_{i}", f"w_{i}", True) for i in range(10)]
        b_entries = [_make_entry(i, f"w_{i}", f"wrong_{i}", False) for i in range(5, 15)]
        a = _make_report(a_entries)
        b = _make_report(b_entries)

        results = run_significance_tests(a, b, n_bootstrap=100)
        assert len(results) >= 3  # Should still run on intersection


# ---------------------------------------------------------------------------
# Test: format_significance_table
# ---------------------------------------------------------------------------

class TestFormatTable:
    """Test the human-readable table formatter."""

    def test_format_produces_string(self):
        a = _make_perfect_entries(20)
        b = _make_failing_entries(20)
        result = paired_bootstrap(a, b, exact_match_rate, metric_name="em")
        table = format_significance_table([result])
        assert isinstance(table, str)
        assert "em" in table
        assert "p-value" in table


# ---------------------------------------------------------------------------
# Test: SignificanceResult dataclass
# ---------------------------------------------------------------------------

class TestSignificanceResult:
    """Test the dataclass."""

    def test_fields(self):
        r = SignificanceResult(
            metric_name="test",
            system_a_score=1.0,
            system_b_score=0.5,
            delta=0.5,
            p_value=0.01,
            n_bootstrap=1000,
            confidence_level=0.95,
            significant=True,
            winner="A",
            ci_lower=0.2,
            ci_upper=0.8,
        )
        assert r.metric_name == "test"
        assert r.significant is True
        assert r.winner == "A"
