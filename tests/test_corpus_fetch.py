"""Tests for fetch-from-source corpus resolution (corpus_fetch.py).

Covers:
    - corpora-card matching for missing corpus paths
    - fetch orchestration with a mocked builder (no network)
    - sha256 verification of built corpora
    - non-interactive behavior (--yes / CI env / declined prompt)
    - corpus_loader integration (fetch-on-miss)
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest import mock

import pytest

from mt_eval_harness import corpus_fetch
from mt_eval_harness.corpus_fetch import (
    fetch_corpus_from_card,
    find_card_for_corpus,
    find_corpora_cards_dir,
    try_fetch_missing_corpus,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

BUILT_CORPUS = {
    "dataset": {"name": "test-fetch-v1"},
    "entries": [
        {"id": 0, "source": "Come", "reference": "âstam"},
    ],
    "language_pair": {"source": "eng", "target": "crk"},
}

BUILT_BYTES = json.dumps(BUILT_CORPUS, indent=2, ensure_ascii=False).encode()
BUILT_SHA256 = hashlib.sha256(BUILT_BYTES).hexdigest()


def _make_card(sha256: str | None = BUILT_SHA256) -> dict:
    return {
        "id": "eval-test-fetch-v1",
        "type": "eval",
        "dev": {
            "size": 1,
            "sizeUnit": "entries",
            "dataFile": "curated/test-fetch-v1.json",
            "format": "harness-json",
        },
        "source": {
            "publisher": "Test",
            "url": "https://example.com/repo",
            "repo_url": "https://example.com/repo",
            "ref": "abc123",
            "builder": "testbuilder",
            "sha256": sha256,
            "license": "CC-BY-NC-SA-4.0",
            "license_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        },
    }


@pytest.fixture
def cards_dir(tmp_path):
    d = tmp_path / "corpora-cards"
    d.mkdir()
    (d / "eval-test-fetch-v1.json").write_text(
        json.dumps(_make_card()), encoding="utf-8"
    )
    # A non-fetchable card (no source.repo_url/builder) — must be ignored.
    (d / "eval-no-source.json").write_text(json.dumps({
        "id": "eval-no-source",
        "dev": {"dataFile": "curated/no-source.json"},
        "source": {"publisher": "X", "url": None},
    }), encoding="utf-8")
    return d


@pytest.fixture
def fake_builder(tmp_path, monkeypatch):
    """Install a mock builder that writes BUILT_CORPUS to dest."""
    calls = []

    def build(card, dest, *, assume_yes):
        calls.append({"card": card["id"], "dest": dest, "assume_yes": assume_yes})
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(BUILT_BYTES)
        return dest

    monkeypatch.setitem(corpus_fetch.BUILDERS, "testbuilder", build)
    return calls


@pytest.fixture
def cache_dir(tmp_path, monkeypatch):
    cache = tmp_path / ".cache"
    monkeypatch.setattr(corpus_fetch, "CACHE_DIR", cache)
    return cache


# ---------------------------------------------------------------------------
# Cards directory resolution
# ---------------------------------------------------------------------------

class TestFindCorporaCardsDir:
    def test_finds_monorepo_cards_dir(self):
        # In the monorepo checkout, cli/shared/corpora-cards exists.
        found = find_corpora_cards_dir()
        assert found is not None
        assert found.name == "corpora-cards"
        assert (found / "eval-eng-crk-edtekla-dev-v1.json").exists()


# ---------------------------------------------------------------------------
# Card matching
# ---------------------------------------------------------------------------

class TestFindCardForCorpus:
    def test_suffix_match(self, cards_dir):
        match = find_card_for_corpus(
            "/abs/path/arena/datasets/curated/test-fetch-v1.json",
            cards_dir=cards_dir,
        )
        assert match is not None
        card, data_file = match
        assert card["id"] == "eval-test-fetch-v1"
        assert data_file == "curated/test-fetch-v1.json"

    def test_filename_fallback_match(self, cards_dir):
        match = find_card_for_corpus(
            "somewhere/else/test-fetch-v1.json", cards_dir=cards_dir,
        )
        assert match is not None
        assert match[0]["id"] == "eval-test-fetch-v1"

    def test_no_match_returns_none(self, cards_dir):
        assert find_card_for_corpus(
            "curated/unknown.json", cards_dir=cards_dir,
        ) is None

    def test_card_without_source_block_not_fetchable(self, cards_dir):
        assert find_card_for_corpus(
            "curated/no-source.json", cards_dir=cards_dir,
        ) is None

    def test_missing_cards_dir_returns_none(self, tmp_path):
        assert find_card_for_corpus(
            "curated/test-fetch-v1.json",
            cards_dir=None if False else tmp_path / "nope",
        ) is None


# ---------------------------------------------------------------------------
# Fetch orchestration (mocked builder)
# ---------------------------------------------------------------------------

class TestFetchCorpusFromCard:
    def test_builds_into_cache_and_verifies(self, fake_builder, cache_dir):
        card = _make_card()
        built = fetch_corpus_from_card(
            card, "curated/test-fetch-v1.json", assume_yes=True,
        )
        assert built == cache_dir / "curated/test-fetch-v1.json"
        assert json.loads(built.read_text(encoding="utf-8")) == BUILT_CORPUS
        assert fake_builder[0]["card"] == "eval-test-fetch-v1"

    def test_sha256_mismatch_deletes_and_raises(self, cache_dir, monkeypatch):
        def bad_build(card, dest, *, assume_yes):
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(b"corrupted output")
            return dest

        monkeypatch.setitem(corpus_fetch.BUILDERS, "testbuilder", bad_build)
        card = _make_card()
        with pytest.raises(ValueError, match="SHA-256 mismatch"):
            fetch_corpus_from_card(
                card, "curated/test-fetch-v1.json", assume_yes=True,
            )
        assert not (cache_dir / "curated/test-fetch-v1.json").exists()

    def test_no_sha256_skips_verification(self, fake_builder, cache_dir):
        card = _make_card(sha256=None)
        built = fetch_corpus_from_card(
            card, "curated/test-fetch-v1.json", assume_yes=True,
        )
        assert built.exists()

    def test_cached_verified_build_skips_rebuild(self, fake_builder, cache_dir):
        card = _make_card()
        dest = cache_dir / "curated/test-fetch-v1.json"
        dest.parent.mkdir(parents=True)
        dest.write_bytes(BUILT_BYTES)
        built = fetch_corpus_from_card(
            card, "curated/test-fetch-v1.json", assume_yes=True,
        )
        assert built == dest
        assert fake_builder == []  # builder never invoked

    def test_unknown_builder_raises(self, cache_dir):
        card = _make_card()
        card["source"]["builder"] = "does-not-exist"
        with pytest.raises(RuntimeError, match="unknown builder"):
            fetch_corpus_from_card(
                card, "curated/test-fetch-v1.json", assume_yes=True,
            )

    def test_non_interactive_without_yes_raises(
        self, fake_builder, cache_dir, monkeypatch,
    ):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.setattr(
            corpus_fetch, "_non_interactive", lambda: True,
        )
        with pytest.raises(RuntimeError, match="--yes"):
            fetch_corpus_from_card(
                _make_card(), "curated/test-fetch-v1.json", assume_yes=False,
            )

    def test_ci_env_proceeds_without_prompt(
        self, fake_builder, cache_dir, monkeypatch,
    ):
        monkeypatch.setenv("CI", "true")
        built = fetch_corpus_from_card(
            _make_card(), "curated/test-fetch-v1.json", assume_yes=False,
        )
        assert built.exists()

    def test_declined_prompt_raises(self, fake_builder, cache_dir, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.setattr(corpus_fetch, "_non_interactive", lambda: False)
        with mock.patch("builtins.input", return_value="n"):
            with pytest.raises(RuntimeError, match="declined"):
                fetch_corpus_from_card(
                    _make_card(), "curated/test-fetch-v1.json",
                    assume_yes=False,
                )

    def test_accepted_prompt_builds(self, fake_builder, cache_dir, monkeypatch):
        monkeypatch.delenv("CI", raising=False)
        monkeypatch.setattr(corpus_fetch, "_non_interactive", lambda: False)
        with mock.patch("builtins.input", return_value="y"):
            built = fetch_corpus_from_card(
                _make_card(), "curated/test-fetch-v1.json", assume_yes=False,
            )
        assert built.exists()


# ---------------------------------------------------------------------------
# try_fetch_missing_corpus
# ---------------------------------------------------------------------------

class TestTryFetchMissingCorpus:
    def test_returns_none_without_matching_card(self, cards_dir):
        assert try_fetch_missing_corpus(
            "curated/never-heard-of-it.json",
            assume_yes=True, cards_dir=cards_dir,
        ) is None

    def test_fetches_for_matching_card(
        self, cards_dir, fake_builder, cache_dir,
    ):
        built = try_fetch_missing_corpus(
            "arena/datasets/curated/test-fetch-v1.json",
            assume_yes=True, cards_dir=cards_dir,
        )
        assert built is not None
        assert built.exists()


# ---------------------------------------------------------------------------
# corpus_loader integration
# ---------------------------------------------------------------------------

class TestLoaderFetchOnMiss:
    def test_load_corpus_fetches_missing_file(
        self, cards_dir, fake_builder, cache_dir, monkeypatch, tmp_path,
    ):
        from mt_eval_harness.config import RunConfig
        from mt_eval_harness.corpus_loader import load_corpus

        # Point the default cards-dir resolution at the fixture dir.
        monkeypatch.setattr(
            corpus_fetch, "find_corpora_cards_dir", lambda: cards_dir,
        )

        missing = tmp_path / "datasets" / "curated" / "test-fetch-v1.json"
        config = RunConfig(corpus_path=str(missing), assume_yes=True)
        entries, meta = load_corpus(config)
        assert len(entries) == 1
        assert entries[0]["source"] == "Come"
        assert config.corpus_path.endswith("curated/test-fetch-v1.json")
        assert Path(config.corpus_path).is_relative_to(cache_dir)

    def test_load_corpus_still_errors_without_card(
        self, cards_dir, cache_dir, monkeypatch, tmp_path,
    ):
        from mt_eval_harness.config import RunConfig
        from mt_eval_harness.corpus_loader import load_corpus

        monkeypatch.setattr(
            corpus_fetch, "find_corpora_cards_dir", lambda: cards_dir,
        )
        config = RunConfig(corpus_path=str(tmp_path / "nope.json"))
        with pytest.raises(FileNotFoundError, match="Corpus not found"):
            load_corpus(config)
