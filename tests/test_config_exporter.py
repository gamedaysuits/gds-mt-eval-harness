"""
Tests for config_exporter — mt-eval export-config.

The regression these tests guard: TestReport JSONs store the composite
score at overall.confidence_intervals.composite_score.score, never at
overall.composite_score, and store no quality_tier at all. The exporter
used to read the top-level keys and so always emitted null for both.
"""

import json

import pytest

from mt_eval_harness.config_exporter import (
    _CLI_METHODS,
    _resolve_default_method,
    _extract_composite_score,
    export_champollion_config,
)
from mt_eval_harness.scoring import classify_quality_tier


def make_report(overall: dict, config_extra: dict | None = None) -> dict:
    """A minimal TestReport with the given `overall` block."""
    config = {
        "model": "claude-sonnet-4-6",
        "temperature": 0.3,
        "batch_size": 25,
        "target_lang": "Plains Cree",
    }
    if config_extra:
        config.update(config_extra)
    return {
        "config": config,
        "overall": overall,
        "timestamp": "2026-06-11T00:00:00Z",
    }


def export(tmp_path, overall: dict, config_extra: dict | None = None) -> dict:
    report_path = tmp_path / "report.json"
    report_path.write_text(
        json.dumps(make_report(overall, config_extra)), encoding="utf-8"
    )
    return export_champollion_config(
        report_path=report_path,
        target_lang_code="crk",
        output_path=tmp_path / "snippet.json",
    )


# ---------------------------------------------------------------------------
# _extract_composite_score
# ---------------------------------------------------------------------------

class TestExtractCompositeScore:
    def test_reads_from_confidence_intervals_block(self):
        # The shape TestReports actually write
        overall = {
            "confidence_intervals": {
                "composite_score": {
                    "metric_name": "composite_score",
                    "score": 0.4546,
                    "ci_lower": 0.4236,
                    "ci_upper": 0.4859,
                },
            },
        }
        assert _extract_composite_score(overall) == 0.4546

    def test_falls_back_to_top_level_key(self):
        # Forward compat: a future format may store it at the top level
        assert _extract_composite_score({"composite_score": 0.71}) == 0.71

    def test_ci_block_wins_over_top_level(self):
        overall = {
            "composite_score": 0.10,
            "confidence_intervals": {"composite_score": {"score": 0.45}},
        }
        assert _extract_composite_score(overall) == 0.45

    def test_missing_everywhere_is_none(self):
        assert _extract_composite_score({}) is None
        assert _extract_composite_score({"confidence_intervals": {}}) is None
        assert _extract_composite_score(
            {"confidence_intervals": {"composite_score": {}}}
        ) is None

    def test_null_ci_block_is_tolerated(self):
        assert _extract_composite_score({"confidence_intervals": None}) is None


# ---------------------------------------------------------------------------
# export_champollion_config — _benchmark_summary
# ---------------------------------------------------------------------------

class TestBenchmarkSummary:
    def test_composite_and_tier_from_real_report_shape(self, tmp_path):
        snippet = export(tmp_path, {
            "total_entries": 200,
            "exact_match_rate": 0.12,
            "corpus_chrf": 38.5,
            "confidence_intervals": {
                "composite_score": {"score": 0.4546},
            },
        })
        summary = snippet["_benchmark_summary"]
        assert summary["composite_score"] == 0.4546
        assert summary["quality_tier"] == classify_quality_tier(0.4546)
        assert summary["quality_tier"] != "unscored"
        assert summary["corpus_size"] == 200
        assert summary["exact_match_rate"] == 0.12
        assert summary["chrf_plus_plus"] == 38.5

    def test_no_composite_emits_null_not_unscored(self, tmp_path):
        snippet = export(tmp_path, {"total_entries": 200})
        summary = snippet["_benchmark_summary"]
        assert summary["composite_score"] is None
        assert summary["quality_tier"] is None

    def test_explicit_report_tier_is_preferred(self, tmp_path):
        # Forward compat: an explicit overall.quality_tier wins over derivation
        snippet = export(tmp_path, {
            "quality_tier": "deployable",
            "confidence_intervals": {"composite_score": {"score": 0.31}},
        })
        assert snippet["_benchmark_summary"]["quality_tier"] == "deployable"

    def test_written_snippet_matches_return_value(self, tmp_path):
        snippet = export(tmp_path, {
            "confidence_intervals": {"composite_score": {"score": 0.4546}},
        })
        on_disk = json.loads((tmp_path / "snippet.json").read_text(encoding="utf-8"))
        assert on_disk["_benchmark_summary"] == snippet["_benchmark_summary"]


# ---------------------------------------------------------------------------
# defaultMethod mapping — pre-launch audit blocking #1
#
# The harness prompt_version vocabulary (naive | coached | custom |
# champollion) is NOT the CLI method vocabulary. A raw passthrough wrote a
# config the CLI rejects with "Unknown translation method". Every exported
# defaultMethod must be a valid CLI method.
# ---------------------------------------------------------------------------

class TestDefaultMethodMapping:
    @pytest.mark.parametrize("prompt_version,expected", [
        ("naive", "llm"),
        ("coached", "llm-coached"),
        ("custom", "llm-coached"),
        ("champollion", "llm-coached"),
    ])
    def test_resolver_maps_to_valid_cli_method(self, prompt_version, expected):
        method, _note = _resolve_default_method(prompt_version)
        assert method == expected
        assert method in _CLI_METHODS

    def test_resolver_defaults_none_to_llm(self):
        method, note = _resolve_default_method(None)
        assert method == "llm"
        assert note is None

    def test_non_portable_versions_carry_a_note(self):
        for pv in ("custom", "champollion"):
            _method, note = _resolve_default_method(pv)
            assert note and pv in note

    def test_unknown_prompt_version_raises(self):
        with pytest.raises(ValueError):
            _resolve_default_method("totally-made-up")

    @pytest.mark.parametrize("prompt_version", [
        "naive", "coached", "custom", "champollion",
    ])
    def test_exported_default_method_is_cli_valid(self, tmp_path, prompt_version):
        snippet = export(
            tmp_path,
            {"confidence_intervals": {"composite_score": {"score": 0.4}}},
            config_extra={"prompt_version": prompt_version},
        )
        # The crash this guards: defaultMethod must be a CLI method, never
        # a raw harness prompt_version (none of which are CLI methods).
        assert snippet["defaultMethod"] in _CLI_METHODS
        assert snippet["defaultMethod"] != prompt_version

    def test_champollion_export_annotates_method_note(self, tmp_path):
        snippet = export(
            tmp_path,
            {"confidence_intervals": {"composite_score": {"score": 0.4}}},
            config_extra={"prompt_version": "champollion"},
        )
        assert snippet["defaultMethod"] == "llm-coached"
        assert "_method_note" in snippet

    def test_non_english_source_emits_input_locale(self, tmp_path):
        snippet = export(
            tmp_path,
            {"confidence_intervals": {"composite_score": {"score": 0.4}}},
            config_extra={"prompt_version": "naive", "source_lang_code": "fra"},
        )
        assert snippet["inputLocale"] == "fra"
        assert "fra:crk" in snippet["pairs"]

    def test_english_source_omits_input_locale(self, tmp_path):
        snippet = export(
            tmp_path,
            {"confidence_intervals": {"composite_score": {"score": 0.4}}},
            config_extra={"prompt_version": "naive"},
        )
        assert "inputLocale" not in snippet
