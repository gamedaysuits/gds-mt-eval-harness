"""Tests for COMET metric integration.

These tests validate the guard logic and interface contract of
metrics_comet.py. Tests that require the actual COMET model
(~2.3 GB download) are marked @pytest.mark.slow and skipped
in standard CI runs.

Run the full suite (including slow tests) with:
    pytest tests/test_comet.py -v -m "not slow"
    pytest tests/test_comet.py -v               # includes slow tests
"""

import pytest
from unittest.mock import patch, MagicMock
from mt_eval_harness.metrics_comet import (
    HAS_COMET,
    DEFAULT_COMET_MODEL,
    COMETResult,
    compute_comet,
    corpus_comet,
    _XLMR_HIGH_RESOURCE,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_entry(id: int, source: str, expected: str, predicted: str,
                error: str = None) -> dict:
    """Create a minimal entry dict matching TestReport format."""
    return {
        "id": id,
        "source": source,
        "expected": expected,
        "predicted": predicted,
        "exact_match": expected == predicted,
        "error": error,
    }


def _make_valid_entries(n: int = 10) -> list[dict]:
    """Create entries with source, expected, and predicted fields."""
    return [
        _make_entry(
            i,
            source=f"Hello world {i}",
            expected=f"Bonjour le monde {i}",
            predicted=f"Bonjour le monde {i}",
        )
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Test: COMET availability detection
# ---------------------------------------------------------------------------

class TestCOMETAvailability:
    """Verify the import guard works correctly."""

    def test_has_comet_is_bool(self):
        assert isinstance(HAS_COMET, bool)

    def test_default_model_constant(self):
        assert DEFAULT_COMET_MODEL == "Unbabel/wmt22-comet-da"


# ---------------------------------------------------------------------------
# Test: COMETResult dataclass
# ---------------------------------------------------------------------------

class TestCOMETResult:
    """Verify the result dataclass."""

    def test_fields(self):
        r = COMETResult(
            corpus_score=0.85,
            per_entry_scores=[0.8, 0.9],
            model_name="test-model",
            n_entries=2,
            target_lang="fr",
            low_resource_warning=False,
        )
        assert r.corpus_score == 0.85
        assert len(r.per_entry_scores) == 2
        assert r.low_resource_warning is False


# ---------------------------------------------------------------------------
# Test: low-resource language detection
# ---------------------------------------------------------------------------

class TestLowResourceDetection:
    """Verify XLM-R coverage table logic."""

    def test_high_resource_languages_present(self):
        for lang in ["en", "fr", "de", "es", "zh", "ja", "ko", "ar", "ru"]:
            assert lang in _XLMR_HIGH_RESOURCE, f"{lang} should be high-resource"

    def test_low_resource_not_present(self):
        # Plains Cree is not in XLM-R top tier
        assert "crk" not in _XLMR_HIGH_RESOURCE


# ---------------------------------------------------------------------------
# Test: compute_comet with mocked model
# ---------------------------------------------------------------------------

class TestComputeCOMETMocked:
    """Test compute_comet logic using a mocked COMET model."""

    @pytest.fixture(autouse=True)
    def _reset_cache(self):
        """Reset module-level model cache between tests."""
        import mt_eval_harness.metrics_comet as mc
        mc._cached_model = None
        mc._cached_model_name = None
        yield
        mc._cached_model = None
        mc._cached_model_name = None

    def test_returns_none_when_comet_unavailable(self):
        """If HAS_COMET is False, compute_comet returns None."""
        with patch("mt_eval_harness.metrics_comet.HAS_COMET", False):
            result = compute_comet(_make_valid_entries())
            assert result is None

    def test_returns_none_for_empty_entries(self):
        """No valid entries → returns None."""
        if not HAS_COMET:
            pytest.skip("COMET not installed")

        entries = [
            _make_entry(0, "", "", "", error="fail"),
            _make_entry(1, "", "", "", error="fail"),
        ]
        with patch("mt_eval_harness.metrics_comet._load_model") as mock_load:
            result = compute_comet(entries)
            assert result is None
            mock_load.assert_not_called()

    def test_returns_none_for_empty_predictions(self):
        """Entries with empty predictions are skipped."""
        if not HAS_COMET:
            pytest.skip("COMET not installed")

        entries = [
            _make_entry(0, "hello", "bonjour", ""),
        ]
        with patch("mt_eval_harness.metrics_comet._load_model") as mock_load:
            result = compute_comet(entries)
            assert result is None


# ---------------------------------------------------------------------------
# Test: corpus_comet metric function
# ---------------------------------------------------------------------------

class TestCorpusCOMETMetricFn:
    """Test the significance-compatible metric function."""

    def test_returns_zero_when_unavailable(self):
        with patch("mt_eval_harness.metrics_comet.HAS_COMET", False):
            score = corpus_comet([])
            assert score == 0.0

    def test_returns_zero_for_empty(self):
        with patch("mt_eval_harness.metrics_comet.HAS_COMET", False):
            score = corpus_comet(_make_valid_entries())
            assert score == 0.0


# ---------------------------------------------------------------------------
# Test: model caching
# ---------------------------------------------------------------------------

class TestModelCaching:
    """Verify that model loading is cached correctly."""

    @pytest.fixture(autouse=True)
    def _reset_cache(self):
        import mt_eval_harness.metrics_comet as mc
        mc._cached_model = None
        mc._cached_model_name = None
        yield
        mc._cached_model = None
        mc._cached_model_name = None

    def test_cache_set_after_load(self):
        """After a successful load, the cache should be populated."""
        import mt_eval_harness.metrics_comet as mc

        mock_model = MagicMock()

        # Patch at the function level since comet may not be installed
        # and download_model/load_from_checkpoint won't be module attrs
        original_has = mc.HAS_COMET
        mc.HAS_COMET = True

        try:
            with patch.dict("sys.modules", {"comet": MagicMock()}):
                # Manually mock the functions used inside _load_model
                import types
                mc.download_model = MagicMock(return_value="/fake/path")
                mc.load_from_checkpoint = MagicMock(return_value=mock_model)

                model = mc._load_model("test-model")

                assert model is mock_model
                assert mc._cached_model is mock_model
                assert mc._cached_model_name == "test-model"
        finally:
            mc.HAS_COMET = original_has
            # Clean up injected attributes
            if hasattr(mc, "download_model") and isinstance(mc.download_model, MagicMock):
                delattr(mc, "download_model")
            if hasattr(mc, "load_from_checkpoint") and isinstance(mc.load_from_checkpoint, MagicMock):
                delattr(mc, "load_from_checkpoint")

    def test_cache_reused_on_second_call(self):
        """Second call with same model name should not re-download."""
        import mt_eval_harness.metrics_comet as mc

        mock_model = MagicMock()
        mc._cached_model = mock_model
        mc._cached_model_name = "test-model"

        # When the cache hits, _load_model returns immediately without
        # calling download_model at all, so no patching needed.
        model = mc._load_model("test-model")
        assert model is mock_model

    def test_cache_invalidated_on_model_change(self):
        """Different model name should trigger a new download."""
        import mt_eval_harness.metrics_comet as mc

        old_model = MagicMock()
        mc._cached_model = old_model
        mc._cached_model_name = "old-model"

        new_model = MagicMock()
        original_has = mc.HAS_COMET
        mc.HAS_COMET = True

        try:
            mc.download_model = MagicMock(return_value="/fake")
            mc.load_from_checkpoint = MagicMock(return_value=new_model)

            model = mc._load_model("new-model")
            assert model is new_model
            assert mc._cached_model_name == "new-model"
        finally:
            mc.HAS_COMET = original_has
            if hasattr(mc, "download_model") and isinstance(mc.download_model, MagicMock):
                delattr(mc, "download_model")
            if hasattr(mc, "load_from_checkpoint") and isinstance(mc.load_from_checkpoint, MagicMock):
                delattr(mc, "load_from_checkpoint")
