"""
Unit tests for corpora_builder.contamination.

Covers the three behaviors the checker's correctness rests on:
    1. Text normalization equivalences (NFC, casefold, whitespace,
       terminal punctuation) — if these are wrong, real duplicates
       slip through.
    2. Exact-pair vs source-only detection — source-only findings must
       capture same-source-different-reference leakage *without*
       double-reporting exact duplicates.
    3. Severity assignment — sealed×public must be CRITICAL,
       sealed×sealed WARNING, dev×dev INFO, and cross-language
       source-only overlap downgraded to INFO.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

import pytest

from corpora_builder.contamination import (
    SEVERITY_CRITICAL,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    canonical_segment,
    check_corpora,
    normalize_text,
    pair_fingerprint,
    render_markdown,
    source_fingerprint,
)


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

class TestNormalizeText:
    def test_nfc_equivalence(self):
        # "ê" composed (U+00EA) vs decomposed (e + U+0302) — common in
        # Plains Cree SRO files produced by different tools.
        composed = "nêhiyawêwin"
        decomposed = unicodedata.normalize("NFD", composed)
        assert composed != decomposed  # sanity: inputs really differ
        assert normalize_text(composed) == normalize_text(decomposed)

    def test_casefold(self):
        assert normalize_text("Hello World") == normalize_text("hello world")
        # Casefold (not just lower): German eszett.
        assert normalize_text("STRASSE") == normalize_text("straße")

    def test_whitespace_collapse(self):
        assert normalize_text("  hello \t  world \n") == "hello world"

    def test_terminal_punctuation_stripped(self):
        assert normalize_text("Come.") == normalize_text("Come")
        assert normalize_text("Come!?") == normalize_text("Come")
        assert normalize_text("Come…") == normalize_text("Come")  # ellipsis

    def test_internal_punctuation_preserved(self):
        assert normalize_text("don't stop") != normalize_text("dont stop")
        assert normalize_text("a, b") != normalize_text("a b")

    def test_combined_equivalence(self):
        assert normalize_text("  I  SEE Him.  ") == "i see him"


# ---------------------------------------------------------------------------
# Fingerprints
# ---------------------------------------------------------------------------

class TestFingerprints:
    def test_pair_fingerprint_matches_normalized_equivalents(self):
        assert pair_fingerprint("Come.", "âstam") == \
            pair_fingerprint("  come ", "Âstam!")

    def test_pair_fingerprint_differs_on_reference(self):
        assert pair_fingerprint("Come", "âstam") != \
            pair_fingerprint("Come", "pê-itohte")

    def test_source_fingerprint_ignores_reference(self):
        assert source_fingerprint("Come.") == source_fingerprint("come")

    def test_tab_separator_is_unambiguous(self):
        # ("a b", "c") must never collide with ("a", "b c").
        assert pair_fingerprint("a b", "c") != pair_fingerprint("a", "b c")


# ---------------------------------------------------------------------------
# Segment canonicalization
# ---------------------------------------------------------------------------

class TestCanonicalSegment:
    @pytest.mark.parametrize("raw,expected", [
        ("gold_standard", "gold_standard"),
        ("edtekla_gold62_seed42", "gold_standard"),
        ("held_out", "held_out"),
        ("holdout", "held_out"),
        ("textbook_test", "held_out"),
        ("phase1_test_90", "held_out"),
        ("development", "development"),
        ("textbook_dev_436", "development"),
        ("textbook_remainder", "development"),
        ("textbook_sample", "development"),
        # "minus holdout" names are the complement of the holdout —
        # development data, not holdout data.
        ("full_minus_holdout", "development"),
        ("", "unknown"),
        (None, "unknown"),
        ("registry", "unknown"),
    ])
    def test_mapping(self, raw, expected):
        assert canonical_segment(raw) == expected


# ---------------------------------------------------------------------------
# End-to-end detection and severity
# ---------------------------------------------------------------------------

def _write_corpus(path: Path, segment: str, entries: list[dict],
                  lang_pair: dict | None = None) -> Path:
    """Write a minimal canonical-schema corpus file for the checker."""
    data = {
        "corpus_id": path.stem,
        "segment": segment,
        "entries": entries,
    }
    if lang_pair is not None:
        data["language_pair"] = lang_pair
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


def _entry(eid, source, reference, **extra):
    return {"id": eid, "source": source, "reference": reference, **extra}


class TestCheckCorpora:
    def test_exact_pair_sealed_vs_dev_is_critical(self, tmp_path):
        _write_corpus(tmp_path / "gold_standard.json", "gold_standard", [
            _entry(0, "I see him", "niwâpamâw"),
            _entry(1, "unique sealed sentence", "ref-a"),
        ])
        _write_corpus(tmp_path / "some_dev.json", "development", [
            # Same pair modulo normalization (case + terminal punct).
            _entry(10, "i see HIM.", "Niwâpamâw"),
            _entry(11, "unique dev sentence", "ref-b"),
        ])
        report = check_corpora([tmp_path])

        critical = [f for f in report["findings"]
                    if f["severity"] == SEVERITY_CRITICAL]
        assert len(critical) == 1
        finding = critical[0]
        assert finding["kind"] == "exact_pair"
        assert finding["count"] == 1
        # Sealed side is always listed first.
        assert finding["segment_a"] == "gold_standard"
        assert finding["segment_b"] == "development"
        assert finding["examples"] == [["0", "10"]]
        assert "CONTAMINATION FOUND" in report["verdict"]

    def test_source_only_detected_separately(self, tmp_path):
        _write_corpus(tmp_path / "held_out.json", "held_out", [
            _entry(0, "Now", "mêkwâc"),
        ])
        _write_corpus(tmp_path / "dev_set.json", "development", [
            # Same source, DIFFERENT reference — pair fingerprints
            # differ, source fingerprints match.
            _entry(5, "now!", "an entirely different translation"),
        ])
        report = check_corpora([tmp_path])

        kinds = {f["kind"]: f for f in report["findings"]}
        assert "exact_pair" not in kinds
        assert kinds["source_only"]["severity"] == SEVERITY_CRITICAL
        assert kinds["source_only"]["count"] == 1

    def test_exact_pair_not_double_reported_as_source_only(self, tmp_path):
        _write_corpus(tmp_path / "held_out.json", "held_out", [
            _entry(0, "Come", "âstam"),
        ])
        _write_corpus(tmp_path / "dev_set.json", "development", [
            _entry(1, "Come", "âstam"),
        ])
        report = check_corpora([tmp_path])

        kinds = [f["kind"] for f in report["findings"]]
        assert kinds == ["exact_pair"]

    def test_dev_dev_overlap_is_info(self, tmp_path):
        entries = [_entry(0, "shared sentence", "shared reference")]
        _write_corpus(tmp_path / "dev_one.json", "development", entries)
        _write_corpus(tmp_path / "dev_two.json", "development", entries)
        report = check_corpora([tmp_path])

        assert report["summary"][SEVERITY_CRITICAL] == 0
        assert report["summary"][SEVERITY_INFO] == 1
        assert report["verdict"] == "No held-out contamination found."

    def test_sealed_sealed_overlap_is_warning(self, tmp_path):
        entries = [_entry(0, "sealed sentence", "sealed reference")]
        _write_corpus(tmp_path / "gold_standard.json", "gold_standard", entries)
        _write_corpus(tmp_path / "held_out.json", "held_out", entries)
        report = check_corpora([tmp_path])

        assert report["summary"][SEVERITY_WARNING] == 1
        assert report["summary"][SEVERITY_CRITICAL] == 0

    def test_cross_language_source_only_downgraded_to_info(self, tmp_path):
        _write_corpus(
            tmp_path / "gold_standard.json", "gold_standard",
            [_entry(0, "Tom is here", "crk ref")],
            lang_pair={"source": "eng", "target": "crk"},
        )
        _write_corpus(
            tmp_path / "hau_dev.json", "development",
            [_entry(1, "Tom is here", "hau ref")],
            lang_pair={"source": "eng", "target": "hau"},
        )
        report = check_corpora([tmp_path])

        assert report["summary"][SEVERITY_CRITICAL] == 0
        info = [f for f in report["findings"]
                if f["severity"] == SEVERITY_INFO]
        assert len(info) == 1
        assert info[0]["kind"] == "source_only"
        assert "language pairs" in info[0]["note"]

    def test_per_entry_segment_overrides_file_segment(self, tmp_path):
        # A "development" master file containing entries tagged
        # gold_standard per-entry: those entries must be sealed.
        _write_corpus(tmp_path / "master_corpus.json", "development", [
            _entry(0, "gold sentence", "gold ref", segment="gold_standard"),
        ])
        _write_corpus(tmp_path / "dev_only.json", "development", [
            _entry(9, "gold sentence", "gold ref"),
        ])
        report = check_corpora([tmp_path])

        assert report["summary"][SEVERITY_CRITICAL] == 1

    def test_plain_list_file_is_loaded(self, tmp_path):
        (tmp_path / "old_dev_list.json").write_text(json.dumps([
            _entry(0, "list sentence", "list ref"),
        ]), encoding="utf-8")
        _write_corpus(tmp_path / "held_out.json", "held_out", [
            _entry(1, "list sentence", "list ref"),
        ])
        report = check_corpora([tmp_path])

        assert report["total_entries"] == 2
        assert report["summary"][SEVERITY_CRITICAL] == 1

    def test_unusable_file_is_skipped_not_fatal(self, tmp_path):
        (tmp_path / "notes.json").write_text('{"metadata": {}}',
                                             encoding="utf-8")
        (tmp_path / "broken.json").write_text("{not json",
                                              encoding="utf-8")
        _write_corpus(tmp_path / "dev.json", "development", [
            _entry(0, "fine", "ref"),
        ])
        report = check_corpora([tmp_path])

        assert len(report["skipped"]) == 2
        assert len(report["files"]) == 1


# ---------------------------------------------------------------------------
# Markdown report hygiene
# ---------------------------------------------------------------------------

class TestRenderMarkdown:
    def test_report_never_contains_sentence_text(self, tmp_path):
        sealed_text = "TOP-SECRET-HELD-OUT-SENTENCE"
        sealed_ref = "TOP-SECRET-REFERENCE"
        _write_corpus(tmp_path / "held_out.json", "held_out", [
            _entry(0, sealed_text, sealed_ref),
        ])
        _write_corpus(tmp_path / "dev.json", "development", [
            _entry(1, sealed_text, sealed_ref),
        ])
        report = check_corpora([tmp_path])
        markdown = render_markdown(report)

        assert sealed_text not in markdown
        assert sealed_ref not in markdown
        assert sealed_text.lower() not in markdown.lower()
        assert "CRITICAL" in markdown

    def test_examples_capped_at_twenty(self, tmp_path):
        shared = [_entry(i, f"sentence number {i}", f"ref {i}")
                  for i in range(30)]
        _write_corpus(tmp_path / "held_out.json", "held_out", shared)
        _write_corpus(tmp_path / "dev.json", "development", shared)
        report = check_corpora([tmp_path])

        critical = [f for f in report["findings"]
                    if f["severity"] == SEVERITY_CRITICAL]
        assert critical[0]["count"] == 30
        assert len(critical[0]["examples"]) == 20
        assert "and 10 more" in render_markdown(report)
