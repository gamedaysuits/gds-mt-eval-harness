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
    build_reference_index,
    build_verdict,
    recompute_corpus_chrf,
    verify_against_corpus,
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


# Corpus-anchored verification (red-team R1 fix A): score predicted vs the
# CANONICAL sha-pinned reference and reject tampered stored `expected`.

CANONICAL = [
    {"source": "the cat sat on the mat", "reference": "le chat etait assis sur le tapis"},
    {"source": "a dog ran in the park", "reference": "un chien a couru dans le parc"},
    {"source": "she sells sea shells", "reference": "elle vend des coquillages"},
]


def _anchored(pairs):
    """pairs: (source, predicted, stored_expected)."""
    return [{"source": s, "predicted": p, "expected": e} for s, p, e in pairs]


class TestCorpusAnchored:
    def test_reference_index_maps_source_to_reference(self):
        idx = build_reference_index(CANONICAL)
        assert idx["the cat sat on the mat"] == "le chat etait assis sur le tapis"
        assert len(idx) == 3

    def test_ambiguous_source_is_dropped(self):
        idx = build_reference_index(CANONICAL + [
            {"source": "the cat sat on the mat", "reference": "DIFFERENT"},
        ])
        assert "the cat sat on the mat" not in idx  # conflicting refs -> not anchorable

    def test_faithful_run_verifies_against_canonical(self):
        idx = build_reference_index(CANONICAL)
        # predicted == canonical reference; stored expected == canonical too.
        entries = _anchored([(c["source"], c["reference"], c["reference"]) for c in CANONICAL])
        v = verify_against_corpus("c1", reported_chrf=100.0, entries=entries, reference_index=idx)
        assert v.ok is True
        assert v.recomputed_chrf > 99.0
        assert v.details["n_tampered"] == 0

    def test_tampered_stored_expected_is_rejected(self):
        idx = build_reference_index(CANONICAL)
        # Attacker stored a fake gold ("expected") that matches their prediction,
        # but it differs from the registered corpus reference.
        entries = _anchored([
            ("the cat sat on the mat", "MY FAKE PERFECT", "MY FAKE PERFECT"),
            ("a dog ran in the park", c2 := "un chien a couru dans le parc", c2),
            ("she sells sea shells", c3 := "elle vend des coquillages", c3),
        ])
        v = verify_against_corpus("c2", reported_chrf=100.0, entries=entries, reference_index=idx)
        assert v.ok is False
        assert "TAMPERED" in v.reason
        assert v.details["n_tampered"] == 1

    def test_garbage_predicted_mismatches_canonical(self):
        idx = build_reference_index(CANONICAL)
        # Honest references stored, but predictions are garbage and the claim is high.
        entries = _anchored([(c["source"], "zzzz qqqq", c["reference"]) for c in CANONICAL])
        v = verify_against_corpus("c3", reported_chrf=95.0, entries=entries, reference_index=idx)
        assert v.ok is False
        assert "MISMATCH" in v.reason

    def test_unmatched_sources_cannot_anchor(self):
        idx = build_reference_index(CANONICAL)
        entries = _anchored([("a sentence not in the corpus", "whatever", "whatever")])
        v = verify_against_corpus("c4", reported_chrf=100.0, entries=entries, reference_index=idx)
        assert v.ok is False
        assert "anchor" in v.reason.lower()
        assert v.details["n_unmatched"] == 1

    def test_residual_hole_copying_public_reference_scores_high(self):
        # Documented honestly: on a PUBLIC corpus, copying the real reference as
        # the "translation" still scores ~100. This needs the sandboxed gold-tier
        # re-run; verify_against_corpus is NOT claimed to catch it.
        idx = build_reference_index(CANONICAL)
        entries = _anchored([(c["source"], c["reference"], c["reference"]) for c in CANONICAL])
        v = verify_against_corpus("c5", reported_chrf=100.0, entries=entries, reference_index=idx)
        assert v.ok is True  # known residual — see module docstring + gold tier
