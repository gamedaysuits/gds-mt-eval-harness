"""Tests for the Tatoeba Challenge adapter and the mesh probe extensions.

Everything runs offline: archives are synthetic tars built in tmp_path,
the release index is a fixture string, and downloads are monkeypatched.
"""

from __future__ import annotations

import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest

from corpora_builder.adapters.tatoeba_challenge_adapter import (
    DEFAULT_RECIPE,
    RELEASE,
    build_corpus_file,
    ensure_test_tar,
    extract_pair_rows,
    iso_pair_key,
    list_tar_pairs,
    release_pair_key,
    rows_to_raw_entries,
)
from corpora_builder.probe_tatoeba import (
    DEFAULT_SURVIVAL,
    FLOOR_N,
    PREFERRED_N,
    calibrate_survival,
    chaining_gain,
    graph_efficiency,
    language_presence,
    mesh_report,
    parse_release_index,
    probe_pairs_via_index,
)


# ---------------------------------------------------------------------------
# Fixtures — synthetic consolidated tar + release index
# ---------------------------------------------------------------------------

AAA_BBB_LINES = [
    # straightforward rows in pair-dir order
    "aaa\tbbb\tone two three four\tuno dos tres cuatro",
    "aaa\tbbb\tfive six seven eight nine\tcinco seis siete ocho nueve",
    # script-tagged variety codes must match after stripping
    "aaa_Latn\tbbb\tten eleven twelve more\tdiez once doce mas",
    # duplicate (dropped), identical pair (dropped), short (filtered later)
    "aaa\tbbb\tone two three four\tuno dos tres cuatro",
    "aaa\tbbb\tsame text\tsame text",
    "aaa\tbbb\thi\thola",
]

# A "no whitespace words" source language (CJK-like): every sentence is
# one token, so the word window starves and the char window must apply.
CCC_DDD_LINES = [
    f"ccc\tddd\t{'句' * (10 + i)}\ttranslated sentence number {i}"
    for i in range(6)
]


def _make_tar(path: Path, members: dict[str, list[str]]) -> Path:
    with tarfile.open(path, "w") as tf:
        for pair, lines in members.items():
            data = ("\n".join(lines) + "\n").encode("utf-8")
            info = tarfile.TarInfo(
                name=f"data/test-{RELEASE}/{pair}/test.txt"
            )
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return path


@pytest.fixture
def tar_path(tmp_path):
    return _make_tar(
        tmp_path / f"test-{RELEASE}.tar",
        {"aaa-bbb": AAA_BBB_LINES, "ccc-ddd": CCC_DDD_LINES},
    )


INDEX_FIXTURE = """\
# langpair\tsource-lang\ttarget-lang\ttest-size\ttest-source\ttest-target\tdev-size\tdev-source\tdev-target\ttrain-size\ttrain-source\ttrain-target
aaa-bbb\tAaa\tBbb\t400\t1600\t1700\t\t\t\t90000\t900000\t950000\t
aaa-ccc\tAaa\tCcc\t120\t500\t520\t10\t40\t41\t1000\t10000\t10100\t
bbb-ccc\tBbb\tCcc\t30\t100\t102\t\t\t\t\t\t\t
aaa-ddd\tAaa\tDdd\t\t\t\t\t\t\t500\t5000\t5100\t
"""


@pytest.fixture
def index(tmp_path):
    p = tmp_path / "released-bitexts.txt"
    p.write_text(INDEX_FIXTURE, encoding="utf-8")
    return parse_release_index(p)


# ---------------------------------------------------------------------------
# Archive handling
# ---------------------------------------------------------------------------

class TestArchive:
    def test_list_tar_pairs(self, tar_path):
        assert list_tar_pairs(tar_path) == {"aaa-bbb", "ccc-ddd"}

    def test_extract_pair_rows(self, tar_path):
        rows = extract_pair_rows(tar_path, "aaa-bbb")
        assert len(rows) == len(AAA_BBB_LINES)
        assert rows[0] == ("aaa", "bbb", "one two three four",
                           "uno dos tres cuatro")

    def test_extract_missing_pair_raises(self, tar_path):
        with pytest.raises(FileNotFoundError, match="zzz-zzz"):
            extract_pair_rows(tar_path, "zzz-zzz")

    def test_ensure_test_tar_cache_hit_verifies(self, tar_path):
        sha = hashlib.sha256(tar_path.read_bytes()).hexdigest()
        got = ensure_test_tar(
            tar_path.parent,
            url=f"https://example.com/{tar_path.name}",
            expected_sha256=sha,
            auto_yes=True,
        )
        assert got == tar_path

    def test_ensure_test_tar_redownloads_on_mismatch(
        self, tar_path, monkeypatch,
    ):
        good_bytes = tar_path.read_bytes()
        sha = hashlib.sha256(good_bytes).hexdigest()
        tar_path.write_bytes(b"corrupted cache")

        class FakeResponse:
            def raise_for_status(self):
                pass

            def iter_content(self, chunk_size):
                yield good_bytes

        monkeypatch.setattr(
            "corpora_builder.adapters.tatoeba_challenge_adapter."
            "requests.get",
            lambda url, stream, timeout: FakeResponse(),
        )
        got = ensure_test_tar(
            tar_path.parent,
            url=f"https://example.com/{tar_path.name}",
            expected_sha256=sha,
            auto_yes=True,
        )
        assert hashlib.sha256(got.read_bytes()).hexdigest() == sha


# ---------------------------------------------------------------------------
# Release-code mapping (zho ↔ cmn)
# ---------------------------------------------------------------------------

class TestReleaseCodeMap:
    def test_pair_key_roundtrip(self):
        assert release_pair_key("cmn", "deu") == "deu-zho"
        assert iso_pair_key("deu-zho") == "cmn-deu"

    def test_unmapped_codes_pass_through(self):
        assert release_pair_key("aaa", "bbb") == "aaa-bbb"
        assert iso_pair_key("aaa-bbb") == "aaa-bbb"
        # macro codes are deliberately NOT mapped (taxonomy decision)
        assert iso_pair_key("eng-hbs") == "eng-hbs"
        assert iso_pair_key("eng-msa") == "eng-msa"

    def test_index_keys_normalised(self, tmp_path):
        p = tmp_path / "idx.txt"
        p.write_text(
            "deu-zho\tGerman\tChinese\t4985\t1\t1\t\t\t\t9\t1\t1\t\n",
            encoding="utf-8",
        )
        index = parse_release_index(p)
        assert "cmn-deu" in index and "deu-zho" not in index

    def test_build_resolves_release_spelled_member(self, tmp_path):
        # member dir uses the release spelling; build asks for cmn
        tar = _make_tar(tmp_path / f"test-{RELEASE}.tar", {
            "deu-zho": [
                "deu\tcmn_Hans\tdrei worte hier jetzt\t现在这里三个词",
                "deu\tcmn_Hant\tvier andere worte hier\t這裡四個其他詞",
                "deu\tyue_Hans\tnicht mandarin worte hier\t不是普通话",
            ],
        })
        sha = hashlib.sha256(tar.read_bytes()).hexdigest()
        built = build_corpus_file(
            tmp_path / "out.json",
            source_lang="deu", target_lang="cmn",
            cache_dir=tar.parent,
            tar_url=f"https://example.com/{tar.name}",
            tar_sha256=sha, auto_yes=True,
        )
        corpus = json.loads(built.read_text(encoding="utf-8"))
        # cmn_Hans + cmn_Hant match; the yue row is a different language
        assert corpus["entry_count"] == 2
        assert corpus["language_pair"] == {"source": "deu", "target": "cmn"}


# ---------------------------------------------------------------------------
# Orientation
# ---------------------------------------------------------------------------

class TestOrientation:
    ROWS = [
        ("aaa", "bbb", "src text here", "trg text here"),
        ("aaa_Latn", "bbb", "tagged src words", "tagged trg words"),
    ]

    def test_forward_direction(self):
        entries = rows_to_raw_entries(self.ROWS, "aaa", "bbb")
        assert [e.source_text for e in entries] == [
            "src text here", "tagged src words",
        ]

    def test_reverse_direction_swaps(self):
        entries = rows_to_raw_entries(self.ROWS, "bbb", "aaa")
        assert [e.source_text for e in entries] == [
            "trg text here", "tagged trg words",
        ]
        assert entries[0].metadata["source_lang"] == "bbb"

    def test_dedup_and_junk_filtering(self, tar_path):
        rows = extract_pair_rows(tar_path, "aaa-bbb")
        entries = rows_to_raw_entries(rows, "aaa", "bbb")
        # 6 lines: dup dropped, identical-pair dropped → 4 distinct
        assert len(entries) == 4
        ids = [e.source_id for e in entries]
        assert len(set(ids)) == len(ids), "content-hash ids must be unique"

    def test_no_matching_rows_raises(self):
        with pytest.raises(ValueError, match="No rows matched"):
            rows_to_raw_entries(self.ROWS, "xxx", "yyy")

    def test_variety_filter(self):
        entries = rows_to_raw_entries(
            self.ROWS, "aaa", "bbb", variety_filter="aaa_Latn",
        )
        assert [e.source_text for e in entries] == ["tagged src words"]


# ---------------------------------------------------------------------------
# Deterministic builds
# ---------------------------------------------------------------------------

class TestBuildCorpusFile:
    def _build(self, tar_path, tmp_path, name="out.json", **recipe_over):
        sha = hashlib.sha256(tar_path.read_bytes()).hexdigest()
        return build_corpus_file(
            tmp_path / name,
            source_lang="aaa",
            target_lang="bbb",
            cache_dir=tar_path.parent,
            recipe={**recipe_over} or None,
            tar_url=f"https://example.com/{tar_path.name}",
            tar_sha256=sha,
            auto_yes=True,
        )

    def test_build_is_byte_deterministic(self, tar_path, tmp_path):
        a = self._build(tar_path, tmp_path, "a.json")
        b = self._build(tar_path, tmp_path, "b.json")
        assert a.read_bytes() == b.read_bytes()

    def test_word_window_filters_short_entries(self, tar_path, tmp_path):
        built = json.loads(
            self._build(tar_path, tmp_path).read_text(encoding="utf-8")
        )
        # "hi" (1 word) is outside the 3–50 word window; 3 survive
        assert built["entry_count"] == 3
        assert built["language_pair"] == {"source": "aaa", "target": "bbb"}
        assert built["created"] == DEFAULT_RECIPE["created"]
        assert built["provenance"]["length_unit"] == "words"

    def test_char_window_for_wordless_source(self, tar_path, tmp_path):
        sha = hashlib.sha256(tar_path.read_bytes()).hexdigest()
        # word window rejects every one-token CJK-like source line
        with pytest.raises(ValueError, match="word-count window"):
            build_corpus_file(
                tmp_path / "words.json",
                source_lang="ccc", target_lang="ddd",
                cache_dir=tar_path.parent,
                tar_url=f"https://example.com/{tar_path.name}",
                tar_sha256=sha, auto_yes=True,
            )
        built_path = build_corpus_file(
            tmp_path / "chars.json",
            source_lang="ccc", target_lang="ddd",
            cache_dir=tar_path.parent,
            recipe={"length_unit": "chars"},
            tar_url=f"https://example.com/{tar_path.name}",
            tar_sha256=sha, auto_yes=True,
        )
        built = json.loads(built_path.read_text(encoding="utf-8"))
        assert built["entry_count"] == 6
        assert built["provenance"]["length_unit"] == "chars"

    def test_non_test_split_rejected(self, tar_path, tmp_path):
        with pytest.raises(ValueError, match="test splits only"):
            self._build(tar_path, tmp_path, split="train")

    def test_unknown_length_unit_rejected(self, tar_path, tmp_path):
        with pytest.raises(ValueError, match="length_unit"):
            self._build(tar_path, tmp_path, length_unit="syllables")


# ---------------------------------------------------------------------------
# Index probe
# ---------------------------------------------------------------------------

class TestIndexProbe:
    def test_parse_release_index(self, index):
        assert index["aaa-bbb"]["test_size"] == 400
        assert index["aaa-ccc"]["dev_size"] == 10
        assert index["aaa-ddd"]["test_size"] == 0  # empty cell

    def test_probe_tiers(self, index):
        probes = {p.pair: p for p in probe_pairs_via_index(
            ["aaa", "bbb", "ccc", "ddd"], index, survival=0.5,
        )}
        assert probes["aaa-bbb"].est_usable == 200
        assert probes["aaa-bbb"].tier == "preferred"
        assert probes["aaa-ccc"].tier == "floor"        # 120*0.5 = 60
        assert probes["bbb-ccc"].tier == "below-floor"  # 30*0.5 = 15
        assert "aaa-ddd" not in probes                  # no test split

    def test_available_pairs_gate(self, index):
        probes = probe_pairs_via_index(
            ["aaa", "bbb", "ccc"], index, available_pairs={"aaa-bbb"},
        )
        assert [p.pair for p in probes] == ["aaa-bbb"]

    def test_calibrate_survival(self, index):
        datasets = [
            {  # 100 built of 400 raw → 0.25
                "access": "local", "source": "Tatoeba (...)", "size": 100,
                "language_pair": {"source": "aaa", "target": "bbb"},
            },
            {  # train-fallback build (size > test count) — excluded
                "access": "local", "source": "Tatoeba (...)", "size": 90,
                "language_pair": {"source": "bbb", "target": "ccc"},
            },
            {  # capped build — excluded
                "access": "local", "source": "Tatoeba (...)", "size": 200,
                "language_pair": {"source": "aaa", "target": "ccc"},
            },
        ]
        assert calibrate_survival(datasets, index) == pytest.approx(0.25)
        assert calibrate_survival([], index) is None

    def test_language_presence(self, index):
        presence = language_presence(index)
        # aaa: 400+90000 + 120+1000 + 0+500 = 92020
        assert presence["aaa"] == 92020


# ---------------------------------------------------------------------------
# Graph math
# ---------------------------------------------------------------------------

class TestGraphMath:
    def test_path_graph_efficiency(self):
        nodes = ["a", "b", "c"]
        edges = {frozenset(("a", "b")), frozenset(("b", "c"))}
        # d(a,b)=1 d(b,c)=1 d(a,c)=2 → mean of 1,1,1,1,.5,.5 = 5/6
        assert graph_efficiency(nodes, edges) == pytest.approx(5 / 6)

    def test_closing_the_triangle(self):
        nodes = ["a", "b", "c"]
        edges = {frozenset(("a", "b")), frozenset(("b", "c"))}
        gain = chaining_gain(nodes, edges, ("a", "c"))
        assert gain == pytest.approx(1 - 5 / 6)

    def test_component_join_outranks_shortcut(self):
        # star a-b, a-c plus isolated pair d-e
        nodes = ["a", "b", "c", "d", "e"]
        edges = {frozenset(("a", "b")), frozenset(("a", "c")),
                 frozenset(("d", "e"))}
        join = chaining_gain(nodes, edges, ("a", "d"))
        shortcut = chaining_gain(nodes, edges, ("b", "c"))
        assert join > shortcut > 0

    def test_disconnected_graph_is_defined(self):
        assert graph_efficiency(["a", "b"], set()) == 0.0


# ---------------------------------------------------------------------------
# Mesh report
# ---------------------------------------------------------------------------

class TestMeshReport:
    @pytest.fixture
    def registry(self, tmp_path):
        reg = {
            "registry_version": "1.0.0",
            "datasets": [
                {
                    "id": "tatoeba-aaa-bbb-dev", "access": "local",
                    "source": "Tatoeba (...)", "size": 100,
                    "language_pair": {"source": "aaa", "target": "bbb"},
                },
                {
                    "id": "tatoeba-aaa-ccc-dev", "access": "local",
                    "source": "Tatoeba (...)", "size": 60,
                    "language_pair": {"source": "aaa", "target": "ccc"},
                },
            ],
        }
        p = tmp_path / "registry.json"
        p.write_text(json.dumps(reg), encoding="utf-8")
        return p

    @pytest.fixture
    def cards_dir(self, tmp_path):
        d = tmp_path / "cards"
        d.mkdir()
        fams = {"aaa": "Fam-One", "bbb": "Fam-One", "ccc": "Fam-Two"}
        for code, fam in fams.items():
            (d / f"{code}.json").write_text(json.dumps({
                "code": code, "classification": {"family": fam},
            }), encoding="utf-8")
        return d

    def test_candidates_and_direction(self, registry, cards_dir, index):
        report = mesh_report(registry, cards_dir, index)
        assert report["lit_languages"] == ["aaa", "bbb", "ccc"]
        cands = {c["pair"]: c for c in report["candidates"]}
        # the only lit-lit pair without a corpus
        assert set(cands) == {"bbb-ccc"}
        cand = cands["bbb-ccc"]
        assert cand["bridges_families"] is True
        # bbb has the larger Tatoeba presence (aaa-bbb is the giant pair)
        assert cand["direction"] == "bbb>ccc"
        assert cand["chaining_gain"] > 0

    def test_hub_candidates(self, registry, cards_dir, index):
        report = mesh_report(
            registry, cards_dir, index, survival=1.0,
        )
        hubs = {h["language"]: h for h in report["hub_candidates"]}
        # ddd is unlit and has no test split anywhere → not a hub;
        # with survival=1.0, bbb-ccc (30) is below floor → no entries
        # other than... aaa/bbb/ccc are lit, so no hubs at all here.
        assert "ddd" not in hubs
