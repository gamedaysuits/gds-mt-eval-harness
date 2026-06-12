"""
Unit tests for corpora_builder.adapters.edtekla_adapter.

All tests run offline: parsing/normalization/split logic is exercised
with fixture snippets, and the download path is tested with mocked
network calls. The deterministic seed-42 split is verified for
shape/disjointness here; the full entry-for-entry equivalence with the
published 436-entry dev corpus is verified against the live repo during
builds (see adapter module docstring), not in unit tests.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest

from corpora_builder.adapters.edtekla_adapter import (
    DEFAULT_REF,
    EdTeKLAAdapter,
    build_dev_corpus,
    classify_difficulty,
    deduplicate_pairs,
    fetch_textbook_files,
    is_valid_pair,
    normalize_english,
    normalize_sro,
    parse_textbook,
    raw_file_url,
    split_dev_holdout,
    to_harness_entries,
    write_corpus_json,
)


# ---------------------------------------------------------------------------
# Fixture snippets (synthetic, in the EdTeKLA file style — tokenized
# punctuation on the English side, SRO with punctuation on the Cree side)
# ---------------------------------------------------------------------------

EN_LINES = [
    "come",                       # L1 — single word
    "i see him .",                # L2 — tokenized period
    "",                           # L3 — empty (skipped)
    "tânisi",                     # L4 — Cree on the EN side (skipped)
    "where are they ?",           # L5 — question
    "come",                       # L6 — duplicate of L1
    "heading",                    # L7 — identical EN/CR (skipped)
]

CR_LINES = [
    "âstam.",
    "niwâpamâw",
    "",
    "tânisi",
    "tâniwêhkâk?",
    "âstam!",
    "heading",
]


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

class TestNormalizeSro:
    def test_strips_sentence_punctuation(self):
        assert normalize_sro("âstam.") == "âstam"
        assert normalize_sro("tâniwêhkâk?") == "tâniwêhkâk"

    def test_nfc_composition(self):
        import unicodedata
        decomposed = unicodedata.normalize("NFD", "nêhiyawêwin")
        assert normalize_sro(decomposed) == "nêhiyawêwin"

    def test_collapses_whitespace(self):
        assert normalize_sro("  êkwa   mîna  ") == "êkwa mîna"


class TestNormalizeEnglish:
    def test_detokenizes_punctuation(self):
        assert normalize_english("hello , how are you ?") == "Hello, how are you?"

    def test_capitalizes_first_letter(self):
        assert normalize_english("eat !") == "Eat!"

    def test_space_before_apostrophe_removed(self):
        assert normalize_english("john 's dog") == "John's dog"


# ---------------------------------------------------------------------------
# Validation and dedup
# ---------------------------------------------------------------------------

class TestIsValidPair:
    def test_empty_rejected(self):
        assert is_valid_pair("", "âstam") == (False, "empty")
        assert is_valid_pair("Come", "") == (False, "empty")

    def test_identical_rejected(self):
        assert is_valid_pair("Heading", "heading") == (False, "identical")

    def test_english_with_sro_rejected(self):
        valid, reason = is_valid_pair("tânisi", "tânisi kiya")
        assert not valid
        assert reason == "english_contains_sro"

    def test_valid_pair_accepted(self):
        assert is_valid_pair("Come", "âstam") == (True, "")


class TestDeduplicatePairs:
    def test_keeps_first_and_records_duplicate_lines(self):
        pairs = [
            {"english": "Come", "cree_sro": "âstam", "source_line": 1},
            {"english": "come", "cree_sro": "ÂSTAM", "source_line": 6},
        ]
        deduped = deduplicate_pairs(pairs)
        assert len(deduped) == 1
        assert deduped[0]["source_line"] == 1
        assert deduped[0]["duplicate_lines"] == [6]


# ---------------------------------------------------------------------------
# Difficulty classification
# ---------------------------------------------------------------------------

class TestClassifyDifficulty:
    def test_single_word_is_l1(self):
        assert classify_difficulty("Come", "âstam") == 1

    def test_short_phrase_is_l2(self):
        assert classify_difficulty("I see him", "niwâpamâw") == 2

    def test_possessive_is_l3(self):
        assert classify_difficulty("My dog is black", "nitêm kaskitêwâw") == 3

    def test_demonstrative_is_l4(self):
        assert classify_difficulty("These books are red", "ôhi masinahikana") == 4

    def test_conditional_is_l5(self):
        assert classify_difficulty(
            "If it rains, we will stay home", "kîspin kimowahki"
        ) == 5

    def test_conjunct_marker_is_l4(self):
        assert classify_difficulty("She is eating", "ê-mîcisot") != 1
        assert classify_difficulty("Eating now", "ê mîcisot mêkwâc") == 4


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

class TestParseTextbook:
    def test_parses_filters_and_dedups(self):
        pairs = parse_textbook(EN_LINES, CR_LINES)
        # L1 valid, L2 valid, L3 empty, L4 EN-side SRO, L5 valid,
        # L6 dup of L1, L7 identical → 3 unique pairs.
        assert len(pairs) == 3
        assert pairs[0]["english"] == "Come"
        assert pairs[0]["cree_sro"] == "âstam"
        assert pairs[0]["source"] == "EdTeKLA/CreeLanguageTextbook:L1"
        assert pairs[0]["duplicate_lines"] == [6]
        assert pairs[1]["english"] == "I see him."
        assert pairs[2]["english"] == "Where are they?"
        assert pairs[2]["source_line"] == 5

    def test_line_count_mismatch_truncates(self):
        pairs = parse_textbook(["come", "go ."], ["âstam"])
        assert len(pairs) == 1

    def test_difficulty_and_notes_assigned(self):
        pairs = parse_textbook(["come"], ["âstam."])
        assert pairs[0]["difficulty"] == 1
        assert pairs[0]["notes"] == "Textbook L1"


# ---------------------------------------------------------------------------
# Deterministic split
# ---------------------------------------------------------------------------

def _synthetic_pairs(n: int) -> list[dict]:
    pairs = []
    for i in range(n):
        pairs.append({
            "english": f"Sentence number {i}",
            "cree_sro": f"crk {i}",
            "source": f"EdTeKLA/CreeLanguageTextbook:L{i + 1}",
            "source_line": i + 1,
            "difficulty": (i % 5) + 1,
            "lemma": "",
            "fst_tags": "",
            "notes": f"Textbook L{(i % 5) + 1}",
        })
    return pairs


class TestSplitDevHoldout:
    def test_split_is_deterministic(self):
        pairs = _synthetic_pairs(486)
        dev1, hold1 = split_dev_holdout(pairs)
        dev2, hold2 = split_dev_holdout(pairs)
        assert dev1 == dev2
        assert hold1 == hold2

    def test_split_sizes_and_disjointness(self):
        pairs = _synthetic_pairs(486)
        dev, hold = split_dev_holdout(pairs)
        assert len(hold) == 50
        assert len(dev) == 436
        dev_keys = {p["source_line"] for p in dev}
        hold_keys = {p["source_line"] for p in hold}
        assert not dev_keys & hold_keys
        assert len(dev_keys | hold_keys) == 486

    def test_stratification_covers_all_tiers(self):
        pairs = _synthetic_pairs(486)
        _dev, hold = split_dev_holdout(pairs)
        assert {p["difficulty"] for p in hold} == {1, 2, 3, 4, 5}

    def test_seed_change_changes_split(self):
        pairs = _synthetic_pairs(486)
        _, hold_a = split_dev_holdout(pairs, seed=42)
        _, hold_b = split_dev_holdout(pairs, seed=43)
        assert ({p["source_line"] for p in hold_a}
                != {p["source_line"] for p in hold_b})


# ---------------------------------------------------------------------------
# Harness format
# ---------------------------------------------------------------------------

class TestHarnessFormat:
    def test_to_harness_entries_shape(self):
        pairs = parse_textbook(EN_LINES, CR_LINES)
        entries = to_harness_entries(pairs)
        assert [e["id"] for e in entries] == [0, 1, 2]
        first = entries[0]
        assert first["source"] == "Come"
        assert first["reference"] == "âstam"
        assert first["provenance"] == "EdTeKLA/CreeLanguageTextbook:L1"
        assert first["metadata"]["source_line"] == 1
        assert set(first) == {
            "id", "source", "reference", "difficulty", "provenance",
            "metadata",
        }

    def test_build_dev_corpus_wrapper(self):
        pairs = _synthetic_pairs(486)
        en = [p["english"].lower() for p in pairs]
        cr = [p["cree_sro"] for p in pairs]
        corpus = build_dev_corpus(en, cr)
        assert corpus["dataset"]["name"] == "edtekla-dev-v1"
        assert corpus["language_pair"]["source"] == "eng"
        assert corpus["language_pair"]["target"] == "crk"
        assert all("reference" in e for e in corpus["entries"])

    def test_write_corpus_json_no_trailing_newline(self, tmp_path):
        corpus = {"dataset": {}, "entries": []}
        out = write_corpus_json(corpus, tmp_path / "c.json")
        raw = out.read_bytes()
        assert not raw.endswith(b"\n")
        assert json.loads(raw) == corpus


# ---------------------------------------------------------------------------
# Adapter fetch() — offline path
# ---------------------------------------------------------------------------

class TestAdapterFetchOffline:
    def _write_fixture_files(self, tmp_path: Path) -> tuple[Path, Path]:
        en = tmp_path / "en.txt"
        cr = tmp_path / "cr.txt"
        en.write_text("\n".join(EN_LINES), encoding="utf-8")
        cr.write_text("\n".join(CR_LINES), encoding="utf-8")
        return en, cr

    def test_fetch_from_local_files(self, tmp_path):
        en, cr = self._write_fixture_files(tmp_path)
        adapter = EdTeKLAAdapter()
        entries = adapter.fetch("eng", "crk", en_path=en, cr_path=cr)
        assert len(entries) == 3
        assert entries[0].source_text == "Come"
        assert entries[0].target_text == "âstam"
        assert entries[0].source_id == "L1"
        prov = entries[0].metadata["provenance"]
        assert prov["source_name"] == "edtekla"
        assert prov["license"] == "CC-BY-NC-SA-4.0"
        assert entries[0].metadata["duplicate_lines"] == [6]

    def test_rejects_unsupported_pair(self):
        adapter = EdTeKLAAdapter()
        with pytest.raises(ValueError, match="only supports eng→crk"):
            adapter.fetch("eng", "fra", en_path="a", cr_path="b")

    def test_rejects_partial_local_paths(self):
        adapter = EdTeKLAAdapter()
        with pytest.raises(ValueError, match="both en_path and cr_path"):
            adapter.fetch("eng", "crk", en_path="only_en.txt")

    def test_requires_cache_dir_for_download(self):
        adapter = EdTeKLAAdapter()
        with pytest.raises(ValueError, match="cache_dir"):
            adapter.fetch("eng", "crk")

    def test_missing_local_file_raises(self, tmp_path):
        adapter = EdTeKLAAdapter()
        with pytest.raises(FileNotFoundError):
            adapter.fetch(
                "eng", "crk",
                en_path=tmp_path / "missing_en.txt",
                cr_path=tmp_path / "missing_cr.txt",
            )


# ---------------------------------------------------------------------------
# Download path — network mocked
# ---------------------------------------------------------------------------

def _fake_urlopen_factory(payloads: dict[str, str]):
    """Build a urlopen replacement serving canned text by URL."""
    class _Resp:
        def __init__(self, data: bytes):
            self._data = data

        def read(self) -> bytes:
            return self._data

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(url, timeout=60):
        for key, text in payloads.items():
            if key in url:
                return _Resp(text.encode("utf-8"))
        raise AssertionError(f"Unexpected URL: {url}")

    return fake_urlopen


class TestFetchTextbookFiles:
    PAYLOADS = {
        "CreeLanguageTextbook_en.txt": "\n".join(EN_LINES),
        "CreeLanguageTextbook_cr.txt": "\n".join(CR_LINES),
    }

    def test_downloads_with_license_acceptance(self, tmp_path):
        with mock.patch(
            "corpora_builder.adapters.edtekla_adapter.urlopen",
            _fake_urlopen_factory(self.PAYLOADS),
        ):
            en, cr = fetch_textbook_files(
                tmp_path, ref="abc123", auto_yes=True,
            )
        assert en.read_text(encoding="utf-8") == "\n".join(EN_LINES)
        assert cr.read_text(encoding="utf-8") == "\n".join(CR_LINES)
        # Files cached under the ref directory
        assert en.parent.name == "abc123"

    def test_license_declined_raises(self, tmp_path):
        with mock.patch(
            "corpora_builder.adapters.edtekla_adapter.confirm_download",
            return_value=False,
        ):
            with pytest.raises(PermissionError, match="declined"):
                fetch_textbook_files(tmp_path, ref="abc123")

    def test_cached_files_skip_prompt_and_network(self, tmp_path):
        ref_dir = tmp_path / DEFAULT_REF
        ref_dir.mkdir(parents=True)
        (ref_dir / "CreeLanguageTextbook_en.txt").write_text("come")
        (ref_dir / "CreeLanguageTextbook_cr.txt").write_text("âstam")
        with mock.patch(
            "corpora_builder.adapters.edtekla_adapter.confirm_download",
        ) as prompt, mock.patch(
            "corpora_builder.adapters.edtekla_adapter.urlopen",
        ) as net:
            en, cr = fetch_textbook_files(tmp_path)
        prompt.assert_not_called()
        net.assert_not_called()
        assert en.exists() and cr.exists()

    def test_offline_error_is_clear(self, tmp_path):
        from urllib.error import URLError

        def offline(url, timeout=60):
            raise URLError("no network")

        with mock.patch(
            "corpora_builder.adapters.edtekla_adapter.urlopen", offline,
        ):
            with pytest.raises(ConnectionError, match="network"):
                fetch_textbook_files(tmp_path, ref="abc123", auto_yes=True)

    def test_raw_file_url_pins_ref(self):
        url = raw_file_url("CreeLanguageTextbook_en.txt", "deadbeef")
        assert "/deadbeef/" in url
        assert url.endswith("CreeLanguageTextbook_en.txt")


class TestAdapterFetchDownload:
    def test_fetch_via_mocked_download(self, tmp_path):
        with mock.patch(
            "corpora_builder.adapters.edtekla_adapter.urlopen",
            _fake_urlopen_factory(TestFetchTextbookFiles.PAYLOADS),
        ):
            adapter = EdTeKLAAdapter()
            entries = adapter.fetch(
                "eng", "crk",
                cache_dir=tmp_path, ref="abc123", auto_yes=True,
            )
        assert len(entries) == 3
        assert entries[-1].source_text == "Where are they?"
