"""
Server-side score verifier — the un-fakeable floor for the leaderboard.

THE PROBLEM. Every leaderboard row is submitted by a contributor who runs the
open-source harness on their own machine and self-reports the scores. The DB
range-checks them (migration 023) and binds them to a sha-pinned corpus
(verify_corpus_integrity + the sha-parity trigger), but nothing re-derives the
numbers. A determined, authenticated contributor can hand-craft an internally
consistent report with inflated metrics and publish it at trust='unverified'.

THE FIX (this module). Re-score the run SERVER-SIDE from the per-entry model
OUTPUTS that are already stored in run_card_entries (`predicted` vs
`expected`), using the same open-source metric the harness uses (sacrebleu
chrF++), and the canonical composite from scoring.py. If the recomputed
aggregate matches what the contributor claimed (within tolerance), the run is
promoted to trust='verified' — the only tier the leaderboard ranks / awards.
If it does NOT match, the claim was fabricated and the run is flagged.

WHAT THIS CATCHES: a contributor editing the reported scores (the easy, common
forgery) — the recomputed chrF++ from their own submitted outputs won't match
their inflated claim.

WHAT THIS DOES NOT CATCH (documented honestly): a contributor who fabricates
the OUTPUT TEXT itself (writes fake "perfect" translations equal to the
reference). Re-scoring fabricated-but-perfect text yields a high score. Catching
that requires re-RUNNING the model server-side (sandboxed execution) — the
"gold/reproduced" tier, reserved for top/prize entries because it costs real
API spend. See `docs/VERIFICATION.md` (to author) for the verification ladder.

USAGE (maintainer / CI, needs the service_role key — never shipped to clients):
    MT_EVAL_SUPABASE_SERVICE_KEY=... python -m mt_eval_harness.verifier --all-unverified
    MT_EVAL_SUPABASE_SERVICE_KEY=... python -m mt_eval_harness.verifier --card-id <uuid>

The pure core (recompute_corpus_chrf / build_verdict) has no network or DB
dependency and is unit-tested in arena/tests/test_verifier.py.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field


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
    """Fetch a card's entries, re-score, and (optionally) set its trust tier."""
    card_id = card["id"]
    entries = _get(url, key,
                   f"run_card_entries?run_card_id=eq.{card_id}"
                   f"&select=expected,predicted,raw_predicted&limit=100000")
    verdict = build_verdict(card_id, card.get("chrf_plus_plus"), entries)
    if apply:
        # Promote on pass; flag a proven fabrication as disqualified. A run we
        # simply can't score yet (ok=False, no mismatch) is left untouched.
        if verdict.ok:
            _patch_trust(url, key, card_id, "verified")
        elif "MISMATCH" in verdict.reason:
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
                     f"run_cards?id=eq.{args.card_id}&select=id,chrf_plus_plus,trust")
    else:
        cards = _get(url, key,
                     f"run_cards?trust=eq.unverified&select=id,chrf_plus_plus,trust"
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
