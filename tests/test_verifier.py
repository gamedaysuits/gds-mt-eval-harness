"""Server-side re-score verifier — the un-fakeable floor.

These tests pin the property that matters: a contributor cannot inflate a
leaderboard score, because the server re-derives chrF++ from the run's own
stored outputs (predicted vs expected) and refuses to promote a claim it can't
reproduce.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sacrebleu")  # harness dep; skip cleanly if not installed

from mt_eval_harness.verifier import (
    build_verdict,
    recompute_corpus_chrf,
)


def _entries(pairs):
    """pairs: list of (predicted, expected)."""
    return [{"predicted": p, "expected": e} for p, e in pairs]


FAITHFUL = _entries([
    ("the cat sat on the mat", "the cat sat on the mat"),
    ("a dog ran in the park", "a dog ran in the park"),
    ("she sells sea shells", "she sells sea shells"),
])

GARBAGE = _entries([
    ("zzzz qqqq", "the cat sat on the mat"),
    ("wxyz vbnm", "a dog ran in the park"),
    ("0000 1111", "she sells sea shells"),
])


class TestRecompute:
    def test_identical_outputs_score_near_100(self):
        chrf, n = recompute_corpus_chrf(FAITHFUL)
        assert n == 3
        assert chrf is not None and chrf > 99.0

    def test_garbage_outputs_score_low(self):
        chrf, n = recompute_corpus_chrf(GARBAGE)
        assert n == 3
        assert chrf is not None and chrf < 50.0

    def test_no_references_is_unscoreable(self):
        chrf, n = recompute_corpus_chrf([{"predicted": "x", "expected": ""}])
        assert chrf is None and n == 0

    def test_missing_prediction_counts_as_empty(self):
        # An errored entry (no prediction) must NOT be silently dropped — it
        # scores as an empty hypothesis (bad), matching the original run.
        chrf, n = recompute_corpus_chrf([{"expected": "the cat sat on the mat"}])
        assert n == 1
        assert chrf is not None and chrf < 50.0


class TestVerdict:
    def test_faithful_claim_is_verified(self):
        v = build_verdict("card-1", reported_chrf=100.0, entries=FAITHFUL)
        assert v.ok is True
        assert v.recomputed_chrf > 99.0

    def test_inflated_claim_is_caught(self):
        # Contributor claims chrF++ 95 but their own outputs are garbage.
        v = build_verdict("card-2", reported_chrf=95.0, entries=GARBAGE)
        assert v.ok is False
        assert "MISMATCH" in v.reason

    def test_small_difference_within_tolerance_passes(self):
        chrf, _ = recompute_corpus_chrf(FAITHFUL)
        v = build_verdict("card-3", reported_chrf=chrf - 0.4, entries=FAITHFUL)
        assert v.ok is True

    def test_difference_beyond_tolerance_fails(self):
        chrf, _ = recompute_corpus_chrf(FAITHFUL)
        v = build_verdict("card-4", reported_chrf=chrf - 5.0, entries=FAITHFUL)
        assert v.ok is False
        assert "MISMATCH" in v.reason

    def test_vacuous_run_is_not_verified(self):
        v = build_verdict("card-5", reported_chrf=100.0, entries=[])
        assert v.ok is False
        assert "MISMATCH" not in v.reason  # unscoreable, not a fabrication

    def test_missing_reported_score_is_not_verified(self):
        v = build_verdict("card-6", reported_chrf=None, entries=FAITHFUL)
        assert v.ok is False
