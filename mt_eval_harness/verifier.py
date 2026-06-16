"""
Server-side score verifier — the un-fakeable floor for the leaderboard.

THE PROBLEM. Every leaderboard row is submitted by a contributor who runs the
open-source harness on their own machine and self-reports the scores. The DB
range-checks them (migration 023) and binds them to a sha-pinned corpus
(verify_corpus_integrity + the sha-parity trigger), but nothing re-derives the
numbers. A determined, authenticated contributor can hand-craft an internally
consistent report with inflated metrics and publish it at trust='unverified'.

THE FIX (this module). Re-score the run SERVER-SIDE against the CANONICAL,
sha-pinned corpus — not the submitter's own stored references. verify_against_corpus
loads the registered corpus by dataset_id (datasets.sha256 is curator-owned and
trigger-enforced — migration 026), maps each entry to its REAL reference by source
text, then (a) flags any stored `expected` altered from the gold (tampering) and
(b) re-scores `predicted` against the real reference with the same metric the
harness uses (sacrebleu chrF++). A run is promoted to trust='verified' — the only
tier the leaderboard ranks / awards — ONLY when it reproduces against the
registered corpus with zero tampered references. A run that cannot be anchored
(corpus unfetchable) stays unverified rather than trusting submitter data.

WHAT THIS CATCHES: editing the reported scores (recompute won't match) AND
fabricating the reference side (stored `expected` won't match the registered
corpus). For a sealed / held-out test set whose references aren't public, it also
stops fabricated outputs outright — there is nothing to copy.

WHAT THIS DOES NOT CATCH (documented honestly): for a PUBLIC corpus, a
contributor who copies the real reference verbatim as their "translation" scores
high. Catching that needs re-RUNNING the model server-side (sandboxed execution)
— the "gold/reproduced" tier, reserved for top/prize entries because it costs
real API spend. See `docs/VERIFICATION.md` (to author) for the verification ladder.

(recompute_corpus_chrf / build_verdict remain as the weaker self-rescore — a
diagnostic that still flags hand-edited scores when the corpus can't be loaded.)

USAGE (maintainer / CI, needs the service_role key — never shipped to clients):
    MT_EVAL_SUPABASE_SERVICE_KEY=... python -m mt_eval_harness.verifier --all-unverified
    MT_EVAL_SUPABASE_SERVICE_KEY=... python -m mt_eval_harness.verifier --card-id <uuid>

The pure core (recompute_corpus_chrf / build_verdict) has no network or DB
dependency and is unit-tested in arena/tests/test_verifier.py.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# Tolerances. chrF++ is a 0–100 score; sacrebleu is deterministic, so a faithful
# re-score should match to within rounding. We allow a small band for harness
# version differences in tokenization/normalization.
CHRF_TOLERANCE = 1.0          # absolute chrF++ points
MIN_ENTRIES_TO_VERIFY = 1     # never "verify" a vacuous run


@dataclass
class Verdict:
    card_id: str
    ok: bool                       # True => promote to 'verified'
    reason: str
    reported_chrf: float | None = None
    recomputed_chrf: float | None = None
    n_entries: int = 0
    details: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "card_id": self.card_id,
            "ok": self.ok,
            "reason": self.reason,
            "reported_chrf": self.reported_chrf,
            "recomputed_chrf": self.recomputed_chrf,
            "n_entries": self.n_entries,
            **({"details": self.details} if self.details else {}),
        }


# ---------------------------------------------------------------------------
# Pure core — no network, no DB. Unit-tested.
# ---------------------------------------------------------------------------

def recompute_corpus_chrf(entries: list[dict]) -> tuple[float | None, int]:
    """Recompute corpus chrF++ from stored per-entry outputs.

    Mirrors the harness scorer (tester.py: ``CHRF(word_order=2)`` == chrF++).
    Each entry must carry the model output (``predicted``) and the reference
    (``expected``). Entries with no reference are skipped (can't be scored);
    a missing/empty prediction scores as an empty hypothesis (correctly bad),
    which is exactly how the original run treated an errored entry.

    Returns (corpus_chrf_or_None, n_scored). None when there is nothing to
    score (so the caller can refuse to "verify" a vacuous run).
    """
    from sacrebleu.metrics import CHRF

    hyps: list[str] = []
    refs: list[str] = []
    for e in entries:
        expected = e.get("expected")
        if expected is None or str(expected).strip() == "":
            continue  # no reference -> not scoreable
        predicted = e.get("predicted")
        if predicted is None:
            predicted = e.get("raw_predicted") or ""
        hyps.append(str(predicted))
        refs.append(str(expected))

    if not hyps:
        return None, 0

    chrf = CHRF(word_order=2)  # chrF++
    score = chrf.corpus_score(hyps, [refs]).score  # 0..100
    return float(score), len(hyps)


def build_verdict(
    card_id: str,
    reported_chrf: float | None,
    entries: list[dict],
    *,
    chrf_tolerance: float = CHRF_TOLERANCE,
) -> Verdict:
    """Compare the contributor's claimed chrF++ to a server-side re-score.

    The decision is intentionally conservative: anything we cannot confirm
    stays UNverified (ok=False). We only return ok=True when we recomputed a
    real score from real outputs and it matches the claim within tolerance.
    """
    recomputed, n = recompute_corpus_chrf(entries)

    if n < MIN_ENTRIES_TO_VERIFY or recomputed is None:
        return Verdict(card_id, False, "no scoreable entries (cannot verify)",
                       reported_chrf, recomputed, n)

    if reported_chrf is None:
        return Verdict(card_id, False, "run reports no chrF++ to verify against",
                       reported_chrf, recomputed, n)

    delta = abs(recomputed - reported_chrf)
    if delta <= chrf_tolerance:
        return Verdict(card_id, True,
                       f"re-scored chrF++ {recomputed:.2f} matches reported "
                       f"{reported_chrf:.2f} (Δ{delta:.2f} ≤ {chrf_tolerance})",
                       reported_chrf, recomputed, n)
    return Verdict(card_id, False,
                   f"MISMATCH: re-scored chrF++ {recomputed:.2f} vs reported "
                   f"{reported_chrf:.2f} (Δ{delta:.2f} > {chrf_tolerance}) — "
                   f"the claimed score is not reproducible from the submitted "
                   f"outputs",
                   reported_chrf, recomputed, n, {"delta": delta})


# ---------------------------------------------------------------------------
# Corpus-anchored verification — the STRONGER check (red-team R1, fix A).
#
# recompute_corpus_chrf above re-scores predicted vs the submitter's STORED
# expected — but both are submitter-controlled, so a contributor who stores
# predicted==expected gets chrF++ 100. The functions below instead score
# predicted against the CANONICAL reference loaded from the sha-pinned corpus
# (datasets.sha256 is curator-owned and trigger-enforced, migration 026), and
# flag any entry whose stored `expected` differs from the canonical gold
# (tampering). A run is only "verified" when it reproduces against the REAL
# registered corpus. (The residual hole — copying a PUBLIC reference verbatim
# as the "translation" — still needs sandboxed model re-execution, the
# "gold/reproduced" tier; documented, not claimed closed here.)
# ---------------------------------------------------------------------------

def _norm(s: object) -> str:
    """Whitespace-normalize for source matching / reference tamper comparison."""
    return " ".join(str(s).split()) if s is not None else ""


def build_reference_index(canonical_entries: list[dict]) -> dict[str, str]:
    """Map normalized source text -> canonical reference from a loaded corpus.

    Sources that appear with conflicting references are dropped (can't be
    disambiguated by source text alone, so they're not anchorable).
    """
    idx: dict[str, str] = {}
    ambiguous: set[str] = set()
    for e in canonical_entries:
        src = _norm(e.get("source"))
        ref = e.get("reference")
        if not src or ref is None:
            continue
        ref = str(ref)
        if src in idx and idx[src] != ref:
            ambiguous.add(src)
        else:
            idx[src] = ref
    for s in ambiguous:
        idx.pop(s, None)
    return idx


def verify_against_corpus(
    card_id: str,
    reported_chrf: float | None,
    entries: list[dict],
    reference_index: dict[str, str],
    *,
    chrf_tolerance: float = CHRF_TOLERANCE,
) -> Verdict:
    """Score `predicted` against the CANONICAL sha-pinned reference and tamper-
    check the stored `expected`. Promotes only a run that reproduces against the
    real corpus with zero tampered references.
    """
    from sacrebleu.metrics import CHRF

    hyps: list[str] = []
    refs: list[str] = []
    n_tampered = 0
    n_unmatched = 0
    for e in entries:
        canonical = reference_index.get(_norm(e.get("source")))
        if canonical is None:
            n_unmatched += 1
            continue
        stored = e.get("expected")
        if stored is not None and str(stored).strip() and _norm(stored) != _norm(canonical):
            n_tampered += 1
        predicted = e.get("predicted")
        if predicted is None:
            predicted = e.get("raw_predicted") or ""
        hyps.append(str(predicted))
        refs.append(canonical)

    details = {"n_tampered": n_tampered, "n_unmatched": n_unmatched, "anchored": True}

    if not hyps:
        return Verdict(card_id, False,
                       "no entries matched the sha-pinned corpus by source "
                       "(cannot anchor to the registered corpus)",
                       reported_chrf, None, 0, details)

    recomputed = float(CHRF(word_order=2).corpus_score(hyps, [refs]).score)

    if n_tampered > 0:
        return Verdict(card_id, False,
                       f"TAMPERED: {n_tampered} stored reference(s) differ from the "
                       f"registered corpus — the submitted gold answers were altered",
                       reported_chrf, recomputed, len(hyps), details)

    if reported_chrf is None:
        return Verdict(card_id, False, "run reports no chrF++ to verify against",
                       reported_chrf, recomputed, len(hyps), details)

    delta = abs(recomputed - reported_chrf)
    if delta <= chrf_tolerance:
        return Verdict(card_id, True,
                       f"re-scored chrF++ {recomputed:.2f} against the registered "
                       f"corpus matches reported {reported_chrf:.2f} "
                       f"(Δ{delta:.2f} ≤ {chrf_tolerance}; {n_unmatched} unmatched)",
                       reported_chrf, recomputed, len(hyps), details)
    return Verdict(card_id, False,
                   f"MISMATCH vs canonical corpus: re-scored chrF++ {recomputed:.2f} "
                   f"vs reported {reported_chrf:.2f} (Δ{delta:.2f} > {chrf_tolerance}) — "
                   f"not reproducible against the real references",
                   reported_chrf, recomputed, len(hyps), {**details, "delta": delta})


def load_canonical_references(dataset_id: str | None, *, assume_yes: bool = True) -> dict[str, str] | None:
    """Fetch the sha-pinned corpus for ``dataset_id`` and return source->reference.

    Resolves the dataset in the registry, builds/fetches it (sha-verified by
    corpus_fetch), and loads it through the same loader the harness scores with.
    Returns None when the dataset is unregistered or the corpus cannot be built
    or fetched — in which case the caller leaves the run unverified (it cannot be
    anchored to the registered corpus, so it must not rank).
    """
    if not dataset_id:
        return None
    try:
        from mt_eval_harness import config as _cfg
        from mt_eval_harness.config import RunConfig
        from mt_eval_harness.corpus_loader import load_corpus
        from mt_eval_harness import corpus_fetch

        registry = _cfg.load_registry()
        entry = next(
            (d for d in registry.get("datasets", []) if d.get("id") == dataset_id),
            None,
        )
        if entry is None or "source_export" not in entry:
            return None
        built = corpus_fetch.fetch_corpus_from_registry_entry(entry, assume_yes=assume_yes)
        canonical_entries, _ = load_corpus(RunConfig(corpus_path=str(built)))
        return build_reference_index(canonical_entries)
    except Exception as exc:  # network / build / parse failure → not anchorable
        logger.warning("Could not load canonical refs for %s: %s", dataset_id, exc)
        return None


# ---------------------------------------------------------------------------
# DB driver — service_role only. Not unit-tested (needs the secret + network).
# ---------------------------------------------------------------------------

def _supabase_cfg() -> tuple[str, str]:
    url = os.environ.get("MT_EVAL_SUPABASE_URL",
                         "https://sjdomynysdljkbemupqa.supabase.co")
    key = os.environ.get("MT_EVAL_SUPABASE_SERVICE_KEY")
    if not key:
        print("error: MT_EVAL_SUPABASE_SERVICE_KEY is required (service_role "
              "key — maintainer only; never commit or ship it).",
              file=sys.stderr)
        raise SystemExit(2)
    return url.rstrip("/"), key


def _get(url: str, key: str, path: str) -> list[dict]:
    req = urllib.request.Request(
        f"{url}/rest/v1/{path}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _patch_trust(url: str, key: str, card_id: str, trust: str) -> None:
    body = json.dumps({"trust": trust}).encode()
    req = urllib.request.Request(
        f"{url}/rest/v1/run_cards?id=eq.{card_id}",
        data=body,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def verify_card(url: str, key: str, card: dict, *, apply: bool) -> Verdict:
    """Re-score a card against the sha-pinned corpus and (optionally) set trust.

    Promotion to 'verified' requires anchoring to the REAL registered corpus
    (verify_against_corpus scores predicted vs the canonical references and
    rejects any tampered stored `expected`). If the corpus can't be loaded the
    run stays unverified — but a self-inconsistent score (the easy forgery:
    predicted vs the submitter's OWN stored expected) is still flagged.
    """
    card_id = card["id"]
    entries = _get(url, key,
                   f"run_card_entries?run_card_id=eq.{card_id}"
                   f"&select=source,expected,predicted,raw_predicted&limit=100000")
    reported = card.get("chrf_plus_plus")

    refs = load_canonical_references(card.get("dataset_id"))
    if refs:
        verdict = verify_against_corpus(card_id, reported, entries, refs)
    else:
        # Not anchorable to the registered corpus → cannot grant 'verified'.
        # Still run the weaker self-rescore to catch a hand-edited score.
        self_v = build_verdict(card_id, reported, entries)
        if self_v.ok:
            verdict = Verdict(card_id, False,
                              "self-consistent but NOT corpus-anchored "
                              "(registered corpus unavailable) — left unverified",
                              reported, self_v.recomputed_chrf, self_v.n_entries,
                              {"anchored": False})
        else:
            verdict = self_v  # MISMATCH / unscoreable carry through

    if apply:
        # Promote only a corpus-anchored pass. Flag a proven fabrication
        # (self-rescore MISMATCH) or a TAMPERED reference as disqualified.
        if verdict.ok:
            _patch_trust(url, key, card_id, "verified")
        elif "MISMATCH" in verdict.reason or "TAMPERED" in verdict.reason:
            _patch_trust(url, key, card_id, "disqualified")
    return verdict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mt-eval-verifier",
        description="Re-score leaderboard runs from their stored outputs and "
                    "promote reproducible ones to trust='verified'.",
    )
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--card-id", help="Verify a single run_card by id.")
    g.add_argument("--all-unverified", action="store_true",
                   help="Verify every run currently at trust='unverified'.")
    parser.add_argument("--apply", action="store_true",
                        help="Write the trust tier back to the DB (default: "
                             "dry-run, report only).")
    parser.add_argument("--limit", type=int, default=5000,
                        help="Max cards to process in --all-unverified mode.")
    args = parser.parse_args(argv)

    url, key = _supabase_cfg()

    if args.card_id:
        cards = _get(url, key,
                     f"run_cards?id=eq.{args.card_id}&select=id,dataset_id,chrf_plus_plus,trust")
    else:
        cards = _get(url, key,
                     f"run_cards?trust=eq.unverified&select=id,dataset_id,chrf_plus_plus,trust"
                     f"&limit={args.limit}")

    if not cards:
        print("No matching run cards.")
        return 0

    passed = mism = skipped = 0
    for card in cards:
        v = verify_card(url, key, card, apply=args.apply)
        tag = "✓ VERIFIED" if v.ok else ("✗ MISMATCH" if "MISMATCH" in v.reason
                                         else "· skipped")
        if v.ok:
            passed += 1
        elif "MISMATCH" in v.reason:
            mism += 1
        else:
            skipped += 1
        print(f"  {tag}  {v.card_id}  {v.reason}")

    mode = "applied" if args.apply else "dry-run (use --apply to write)"
    print(f"\n{len(cards)} cards: {passed} verified, {mism} mismatched, "
          f"{skipped} unscoreable — {mode}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
