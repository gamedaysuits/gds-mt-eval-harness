"""
Tests for mt_eval_harness.publish — run card assembly and Supabase upsert.

Covers:
    - Fingerprint hash stability (same inputs → same hash/UUID,
      changed corpus sha256 → different hash/UUID)
    - assemble_run_card() with a minimal valid TestReport + RunLog pair
    - validate_row() — required NOT NULL field checking before upsert
    - _upsert_with_retry() — exponential backoff on 5xx/network errors,
      immediate failure on 4xx
"""

import io
import json
import urllib.error
import urllib.request

import pytest

from mt_eval_harness import publish
from mt_eval_harness.publish import (
    assemble_run_card,
    validate_row,
    _lookup_corpus_license,
    _upsert_with_retry,
    OPTIONAL_NULLABLE_FIELDS,
    REQUIRED_ROW_FIELDS,
    UPSERT_MAX_ATTEMPTS,
)


# ---------------------------------------------------------------------------
# Fixtures: minimal RunLog + TestReport pair on disk
# ---------------------------------------------------------------------------

def _make_run_log(
    corpus_sha256: str = "a" * 64,
    dataset_id: str = "test_dataset",
) -> dict:
    """Create a minimal RunLog dict matching what assemble_run_card reads."""
    return {
        "run_id": "test_run_001",
        "harness_version": "9.0.0",
        "timestamp_start": "2026-01-01T00:00:00Z",
        "elapsed_s": 12.5,
        "total_cost_usd": 0.01,
        "cache_hits": 0,
        "config": {
            "model": "test-provider/test-model",
            "prompt_version": "v1",
            "temperature": 0.0,
            "max_tokens": 1024,
            "batch_size": 25,
            "dataset_id": dataset_id,
            "source_lang": "English",
            "target_lang": "French",
            "tools_enabled": False,
        },
        "provenance": {
            "corpus_sha256": corpus_sha256,
            "system_prompt_sha256": "b" * 64,
            "system_prompt_used": "Translate the following.",
            "dataset_meta": {"version": "1.0"},
        },
        "results": [
            {
                "id": 0,
                "source": "Hello.",
                "expected": "Bonjour.",
                "predicted": "Bonjour.",
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 100, "completion_tokens": 10},
                "error": None,
            },
            {
                "id": 1,
                "source": "Thank you.",
                "expected": "Merci.",
                "predicted": "Merci beaucoup.",
                "latency_s": 0.3,
                "usage": {"prompt_tokens": 80, "completion_tokens": 8},
                "error": None,
            },
        ],
    }


def _make_report(source_log_path: str) -> dict:
    """Create a minimal TestReport dict matching what assemble_run_card reads."""
    return {
        "source_log": source_log_path,
        "overall": {
            "total_entries": 2,
            "evaluated": 2,
            "exact_match_count": 1,
            "exact_match_rate": 0.5,
            "corpus_chrf": 55.0,
            "corpus_bleu": 30.0,
            "corpus_ter": 40.0,
            "avg_length_ratio": 1.1,
            "error_count": 0,
            "plugin_metrics": {},
        },
        "by_difficulty": {},
        "by_domain": {},
        "by_segment": {},
        "entries": [],
    }


def _write_pair(
    tmp_path,
    name: str,
    corpus_sha256: str = "a" * 64,
    dataset_id: str = "test_dataset",
):
    """Write a RunLog + TestReport pair to disk; return the report path."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    run_log_path = tmp_path / f"{name}.json"
    run_log_path.write_text(
        json.dumps(_make_run_log(corpus_sha256, dataset_id)), encoding="utf-8"
    )
    report_path = tmp_path / f"{name}_report.json"
    report_path.write_text(
        json.dumps(_make_report(str(run_log_path))), encoding="utf-8"
    )
    return report_path


@pytest.fixture(autouse=True)
def no_git_provenance(monkeypatch):
    """Make assembly deterministic and fast — skip git subprocess calls."""
    monkeypatch.setattr(publish, "_detect_git_provenance", lambda: None)


# ---------------------------------------------------------------------------
# assemble_run_card — minimal valid report
# ---------------------------------------------------------------------------

class TestAssembleRunCard:
    """Assembly from a minimal RunLog + TestReport pair."""

    def test_returns_card_uuid_and_fingerprint(self, tmp_path):
        report_path = _write_pair(tmp_path, "run1")
        run_card, card_id, fingerprint_hash = assemble_run_card(report_path)

        assert isinstance(run_card, dict)
        assert len(fingerprint_hash) == 64  # SHA-256 hex
        # card_id is a valid UUID string
        import uuid as uuid_mod
        assert str(uuid_mod.UUID(card_id)) == card_id

    def test_card_core_fields(self, tmp_path):
        report_path = _write_pair(tmp_path, "run1")
        run_card, _, _ = assemble_run_card(report_path)

        assert run_card["run_id"] == "test_run_001"
        assert run_card["harness_version"] == "9.0.0"
        assert run_card["model_slug"] == "test-provider/test-model"
        assert run_card["condition"] == "v1"
        assert run_card["dataset"]["id"] == "test_dataset"
        assert run_card["dataset"]["language_pair"] == "eng>fra"
        assert run_card["dataset"]["sha256"] == "a" * 64

    def test_token_aggregation(self, tmp_path):
        report_path = _write_pair(tmp_path, "run1")
        run_card, _, _ = assemble_run_card(report_path)

        assert run_card["totals"]["prompt_tokens"] == 180
        assert run_card["totals"]["completion_tokens"] == 18
        assert run_card["totals"]["total_cost_usd"] == 0.01

    def test_scores_block(self, tmp_path):
        report_path = _write_pair(tmp_path, "run1")
        run_card, _, _ = assemble_run_card(report_path)

        scores = run_card["scores"]
        assert scores["exact_match_rate"] == 0.5
        assert scores["chrf_plus_plus"] == 55.0
        assert scores["composite"] is not None
        assert scores["avg_latency_seconds"] == 0.4

    def test_run_card_hash_is_set(self, tmp_path):
        report_path = _write_pair(tmp_path, "run1")
        run_card, _, _ = assemble_run_card(report_path)
        assert len(run_card["run_card_hash"]) == 64

    def test_missing_run_log_raises(self, tmp_path):
        report_path = tmp_path / "orphan_report.json"
        report_path.write_text(
            json.dumps(_make_report(str(tmp_path / "nonexistent.json"))),
            encoding="utf-8",
        )
        with pytest.raises(FileNotFoundError):
            assemble_run_card(report_path)


# ---------------------------------------------------------------------------
# Corpus license passthrough (migration 015)
# ---------------------------------------------------------------------------

class TestCorpusLicensePassthrough:
    """corpus_license/corpus_attribution from arena/datasets/registry.json."""

    def test_registered_dataset_embeds_license(self, tmp_path, capsys):
        # 'tatoeba-eng-haw-dev' is a registered dataset (CC-BY-2.0, Tatoeba)
        report_path = _write_pair(
            tmp_path, "run1", dataset_id="tatoeba-eng-haw-dev"
        )
        run_card, _, _ = assemble_run_card(report_path)

        assert run_card["corpus_license"] == "CC-BY-2.0"
        assert "Tatoeba" in run_card["corpus_attribution"]
        # No registry warning for registered datasets
        assert "not in the" not in capsys.readouterr().out

    def test_registered_alias_resolves(self, tmp_path):
        # 'edtekla-dev' is an alias of 'edtekla-dev-v1' in the registry
        report_path = _write_pair(tmp_path, "run1", dataset_id="edtekla-dev")
        run_card, _, _ = assemble_run_card(report_path)

        assert run_card["corpus_license"] == "CC BY-NC-SA 4.0"
        assert "University of Alberta" in run_card["corpus_attribution"]

    def test_unregistered_dataset_nulls_and_warns(self, tmp_path, capsys):
        report_path = _write_pair(tmp_path, "run1", dataset_id="test_dataset")
        run_card, _, _ = assemble_run_card(report_path)

        assert run_card["corpus_license"] is None
        assert run_card["corpus_attribution"] is None
        out = capsys.readouterr().out
        assert "test_dataset" in out
        assert "registry" in out

    def test_lookup_unknown_id_returns_none(self):
        assert _lookup_corpus_license("definitely-not-a-dataset") is None

    def test_lookup_empty_id_returns_none(self):
        assert _lookup_corpus_license("") is None

    def test_lookup_registered_id(self):
        info = _lookup_corpus_license("tatoeba-eng-haw-dev")
        assert info == {
            "license": "CC-BY-2.0",
            "attribution": "Tatoeba (https://tatoeba.org)",
        }


# ---------------------------------------------------------------------------
# Dataset id resolution (corpus_path → registry id fallback)
# ---------------------------------------------------------------------------

class TestResolveDatasetId:
    """_resolve_dataset_id(): explicit id > corpus_path match > legacy filter."""

    def test_explicit_dataset_id_wins(self):
        config = {
            "dataset_id": "my-explicit-id",
            "corpus_path": "/tmp/eng-ceb-dev-v1.json",
            "dataset": "all",
        }
        assert publish._resolve_dataset_id(config) == "my-explicit-id"

    def test_corpus_path_basename_resolves_registry_id(self):
        # curated/eng-ceb-dev-v1.json is the registered path of
        # 'tatoeba-eng-ceb-dev'; any absolute prefix should still match.
        config = {
            "dataset_id": "",
            "corpus_path": "/anywhere/datasets/curated/eng-ceb-dev-v1.json",
            "dataset": "all",
        }
        assert publish._resolve_dataset_id(config) == "tatoeba-eng-ceb-dev"

    def test_corpus_stem_matches_alias(self):
        # 'master_corpus' is an alias of 'crk-master-corpus' so local-only
        # corpora without a registered path still resolve.
        config = {
            "dataset_id": "",
            "corpus_path": "/somewhere/master_corpus.json",
            "dataset": "all",
        }
        assert publish._resolve_dataset_id(config) == "crk-master-corpus"

    def test_unknown_corpus_falls_back_to_legacy_filter(self):
        config = {
            "dataset_id": "",
            "corpus_path": "/tmp/some-ad-hoc-corpus.json",
            "dataset": "all",
        }
        assert publish._resolve_dataset_id(config) == "all"

    def test_no_corpus_path_falls_back_to_legacy_filter(self):
        config = {"dataset_id": "", "corpus_path": None, "dataset": "dev"}
        assert publish._resolve_dataset_id(config) == "dev"


# ---------------------------------------------------------------------------
# Fingerprint stability
# ---------------------------------------------------------------------------

class TestFingerprintStability:
    """Same inputs → same fingerprint/UUID; changed inputs → different."""

    def test_same_inputs_same_fingerprint(self, tmp_path):
        report_a = _write_pair(tmp_path / "a", "run1")
        report_b = _write_pair(tmp_path / "b", "run1")

        _, id_a, fp_a = assemble_run_card(report_a)
        _, id_b, fp_b = assemble_run_card(report_b)

        assert fp_a == fp_b
        assert id_a == id_b

    def test_repeated_assembly_is_deterministic(self, tmp_path):
        report_path = _write_pair(tmp_path, "run1")
        _, id_1, fp_1 = assemble_run_card(report_path)
        _, id_2, fp_2 = assemble_run_card(report_path)
        assert fp_1 == fp_2
        assert id_1 == id_2

    def test_changed_corpus_sha_changes_fingerprint(self, tmp_path):
        report_a = _write_pair(tmp_path / "a", "run1", corpus_sha256="a" * 64)
        report_b = _write_pair(tmp_path / "b", "run1", corpus_sha256="c" * 64)

        _, id_a, fp_a = assemble_run_card(report_a)
        _, id_b, fp_b = assemble_run_card(report_b)

        assert fp_a != fp_b
        assert id_a != id_b

    def test_fingerprint_components_recorded(self, tmp_path):
        report_path = _write_pair(tmp_path, "run1")
        run_card, _, fp = assemble_run_card(report_path)

        components = run_card["fingerprint"]["components"]
        assert components["dataset_sha256"] == "a" * 64
        assert components["model_slug"] == "test-provider/test-model"
        assert run_card["fingerprint"]["hash"] == fp


# ---------------------------------------------------------------------------
# Coached-condition derivation + coaching_data_sha256
# ---------------------------------------------------------------------------

def _write_coached_pair(
    tmp_path,
    name: str,
    prompt_version: str = "naive",
    coaching_prompt: str | None = "Translate formally. Glossary: dog -> atim.",
    coaching_sha: str | None = "c" * 64,
):
    """Write a RunLog + TestReport pair with coaching provenance."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    run_log = _make_run_log()
    run_log["config"]["prompt_version"] = prompt_version
    if coaching_prompt is not None:
        run_log["provenance"]["coaching_prompt"] = coaching_prompt
        run_log["provenance"]["coaching_prompt_sha256"] = coaching_sha
    run_log_path = tmp_path / f"{name}.json"
    run_log_path.write_text(json.dumps(run_log), encoding="utf-8")
    report_path = tmp_path / f"{name}_report.json"
    report_path.write_text(
        json.dumps(_make_report(str(run_log_path))), encoding="utf-8"
    )
    return report_path


class TestCoachedCondition:
    """Coached runs publish as condition 'coached', not 'naive'."""

    def test_naive_with_coaching_relabelled_coached(self, tmp_path):
        # Legacy run log: coaching recorded in provenance but config still
        # says prompt_version="naive".
        report_path = _write_coached_pair(tmp_path, "run1")
        run_card, _, _ = assemble_run_card(report_path)
        assert run_card["condition"] == "coached"

    def test_coached_prompt_version_passes_through(self, tmp_path):
        # Run logs from the fixed CLI already carry prompt_version="coached".
        report_path = _write_coached_pair(
            tmp_path, "run1", prompt_version="coached"
        )
        run_card, _, _ = assemble_run_card(report_path)
        assert run_card["condition"] == "coached"

    def test_explicit_condition_not_relabelled(self, tmp_path):
        # A user-chosen prompt version is preserved even with coaching
        # in provenance (e.g. champollion-config runs).
        report_path = _write_coached_pair(
            tmp_path, "run1", prompt_version="champollion"
        )
        run_card, _, _ = assemble_run_card(report_path)
        assert run_card["condition"] == "champollion"

    def test_no_coaching_stays_naive(self, tmp_path):
        report_path = _write_coached_pair(
            tmp_path, "run1", coaching_prompt=None
        )
        run_card, _, _ = assemble_run_card(report_path)
        assert run_card["condition"] == "naive"
        assert run_card["coaching_data_sha256"] is None

    def test_coaching_data_sha256_populated(self, tmp_path):
        report_path = _write_coached_pair(tmp_path, "run1")
        run_card, _, _ = assemble_run_card(report_path)
        assert run_card["coaching_data_sha256"] == "c" * 64

    def test_empty_coaching_sha_normalized_to_none(self, tmp_path):
        # build_run_log writes "" when the sha is missing — the run card
        # field is nullable, so normalize to None.
        report_path = _write_coached_pair(tmp_path, "run1", coaching_sha="")
        run_card, _, _ = assemble_run_card(report_path)
        assert run_card["coaching_data_sha256"] is None

    def test_relabel_changes_fingerprint_vs_naive(self, tmp_path):
        # condition feeds the fingerprint (§3.8): a coached run must not
        # dedupe against a true naive baseline.
        report_naive = _write_coached_pair(
            tmp_path / "a", "run1", coaching_prompt=None
        )
        report_coached = _write_coached_pair(tmp_path / "b", "run1")

        _, id_naive, fp_naive = assemble_run_card(report_naive)
        _, id_coached, fp_coached = assemble_run_card(report_coached)

        assert fp_naive != fp_coached
        assert id_naive != id_coached
        # ...and the relabelled condition is what lands in the components.
        card, _, _ = assemble_run_card(report_coached)
        assert card["fingerprint"]["components"]["condition"] == "coached"


# ---------------------------------------------------------------------------
# Row validation
# ---------------------------------------------------------------------------

def _make_valid_row() -> dict:
    """A row carrying every required NOT NULL field."""
    return {
        "id": "8a32a432-1111-5222-8333-444455556666",
        "submitter": "tester@example.com",
        "affirmation": "Results generated by mt-eval harness v9.0.0.",
        "trust": "unverified",
        "model_slug": "test-provider/test-model",
        "condition": "v1",
        "dataset_id": "test_dataset",
        "language_pair": "eng>fra",
        "harness_version": "9.0.0",
        "run_card": {"run_id": "test_run_001"},
        "fingerprint_hash": "a" * 64,
    }


class TestValidateRow:
    """validate_row() flags missing/empty required NOT NULL fields."""

    def test_complete_row_passes(self):
        assert validate_row(_make_valid_row()) == []

    def test_missing_field_is_reported(self):
        row = _make_valid_row()
        del row["model_slug"]
        assert validate_row(row) == ["model_slug"]

    def test_none_field_is_reported(self):
        row = _make_valid_row()
        row["dataset_id"] = None
        assert validate_row(row) == ["dataset_id"]

    def test_empty_string_is_reported(self):
        row = _make_valid_row()
        row["harness_version"] = ""
        row["language_pair"] = "   "
        problems = validate_row(row)
        assert "harness_version" in problems
        assert "language_pair" in problems

    def test_empty_run_card_dict_is_reported(self):
        row = _make_valid_row()
        row["run_card"] = {}
        assert validate_row(row) == ["run_card"]

    def test_multiple_missing_fields_all_listed(self):
        row = _make_valid_row()
        del row["id"]
        del row["submitter"]
        row["trust"] = ""
        problems = validate_row(row)
        assert set(problems) >= {"id", "submitter", "trust"}

    def test_empty_condition_allowed_but_none_rejected(self):
        # condition is NOT NULL in the schema, but an empty string is a
        # legitimate value for runs without a prompt_version.
        row = _make_valid_row()
        row["condition"] = ""
        assert validate_row(row) == []
        row["condition"] = None
        assert validate_row(row) == ["condition"]

    def test_all_required_fields_checked(self):
        # Every field in REQUIRED_ROW_FIELDS is enforced when absent.
        empty_problems = validate_row({})
        for field in REQUIRED_ROW_FIELDS:
            assert field in empty_problems

    def test_null_corpus_license_is_optional(self):
        # corpus_license/corpus_attribution are nullable (migration 015):
        # None values must never block a publish (unregistered datasets).
        row = _make_valid_row()
        row["corpus_license"] = None
        row["corpus_attribution"] = None
        assert validate_row(row) == []

    def test_missing_corpus_license_is_optional(self):
        # Entirely absent is also fine — older rows predate migration 015.
        row = _make_valid_row()
        assert "corpus_license" not in row
        assert validate_row(row) == []

    def test_optional_fields_never_required(self):
        # Guard against someone adding these to the required tuples later.
        for field in OPTIONAL_NULLABLE_FIELDS:
            assert field not in REQUIRED_ROW_FIELDS
            assert field not in publish.REQUIRED_NOT_NULL_FIELDS
        assert "corpus_license" not in validate_row({})


# ---------------------------------------------------------------------------
# Retry logic — _upsert_with_retry with urllib mocked
# ---------------------------------------------------------------------------

class _FakeResponse:
    """Minimal context-manager response standing in for urlopen's return."""

    def __init__(self, body: bytes = b'[{"id": "row-1"}]'):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self._body


def _http_error(code: int, body: bytes = b'{"message": "boom"}'):
    return urllib.error.HTTPError(
        url="https://example.supabase.co/rest/v1/run_cards",
        code=code,
        msg="error",
        hdrs=None,
        fp=io.BytesIO(body),
    )


def _make_request() -> urllib.request.Request:
    return urllib.request.Request(
        "https://example.supabase.co/rest/v1/run_cards",
        data=b"{}",
        method="POST",
    )


@pytest.fixture
def no_sleep(monkeypatch):
    """Record backoff delays instead of actually sleeping."""
    delays = []
    monkeypatch.setattr(publish.time, "sleep", delays.append)
    return delays


class TestUpsertRetry:
    """Retry on 5xx/network errors with backoff; fail fast on 4xx."""

    def test_success_first_try(self, monkeypatch, no_sleep, capsys):
        calls = []

        def fake_urlopen(req, timeout=None):
            calls.append(req)
            return _FakeResponse()

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        result = _upsert_with_retry(_make_request())

        assert result == [{"id": "row-1"}]
        assert len(calls) == 1
        assert no_sleep == []

    def test_5xx_then_success_succeeds(self, monkeypatch, no_sleep, capsys):
        attempts = []

        def fake_urlopen(req, timeout=None):
            attempts.append(1)
            if len(attempts) == 1:
                raise _http_error(500)
            return _FakeResponse()

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        result = _upsert_with_retry(_make_request())

        assert result == [{"id": "row-1"}]
        assert len(attempts) == 2
        assert no_sleep == [1]  # one backoff of 1s before the retry

    def test_two_5xx_then_success_backs_off_exponentially(
        self, monkeypatch, no_sleep, capsys
    ):
        attempts = []

        def fake_urlopen(req, timeout=None):
            attempts.append(1)
            if len(attempts) <= 2:
                raise _http_error(503)
            return _FakeResponse()

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        result = _upsert_with_retry(_make_request())

        assert result == [{"id": "row-1"}]
        assert len(attempts) == 3
        assert no_sleep == [1, 2]

    def test_4xx_fails_immediately_no_retry(self, monkeypatch, no_sleep, capsys):
        attempts = []

        def fake_urlopen(req, timeout=None):
            attempts.append(1)
            raise _http_error(403, body=b'{"message": "RLS violation"}')

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        with pytest.raises(SystemExit) as exc_info:
            _upsert_with_retry(_make_request())

        assert exc_info.value.code == 1
        assert len(attempts) == 1  # no retries on client errors
        assert no_sleep == []
        # Response body is shown to the user
        out = capsys.readouterr().out
        assert "403" in out
        assert "RLS violation" in out

    def test_network_error_then_success(self, monkeypatch, no_sleep, capsys):
        attempts = []

        def fake_urlopen(req, timeout=None):
            attempts.append(1)
            if len(attempts) == 1:
                raise urllib.error.URLError("connection refused")
            return _FakeResponse()

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        result = _upsert_with_retry(_make_request())

        assert result == [{"id": "row-1"}]
        assert len(attempts) == 2

    def test_timeout_is_retried(self, monkeypatch, no_sleep, capsys):
        attempts = []

        def fake_urlopen(req, timeout=None):
            attempts.append(1)
            if len(attempts) == 1:
                raise TimeoutError("timed out")
            return _FakeResponse()

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        result = _upsert_with_retry(_make_request())

        assert result == [{"id": "row-1"}]
        assert len(attempts) == 2

    def test_persistent_5xx_exhausts_attempts(self, monkeypatch, no_sleep, capsys):
        attempts = []

        def fake_urlopen(req, timeout=None):
            attempts.append(1)
            raise _http_error(500)

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        with pytest.raises(SystemExit) as exc_info:
            _upsert_with_retry(_make_request())

        assert exc_info.value.code == 1
        assert len(attempts) == UPSERT_MAX_ATTEMPTS
        assert no_sleep == [1, 2]  # no sleep after the final attempt

    def test_persistent_network_error_exhausts_attempts(
        self, monkeypatch, no_sleep, capsys
    ):
        attempts = []

        def fake_urlopen(req, timeout=None):
            attempts.append(1)
            raise urllib.error.URLError("no route to host")

        monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
        with pytest.raises(SystemExit):
            _upsert_with_retry(_make_request())

        assert len(attempts) == UPSERT_MAX_ATTEMPTS
