#!/usr/bin/env python3
"""Batch-publish every completed harness report to the STAGING leaderboard.

Globs arena/eval/logs/harness/run_*_report.json and pushes each one through
the harness's real publish pipeline (mt_eval_harness.publish.publish_to_supabase)
with auto_confirm=True — full run card, per-entry records, and dataset upsert.

Idempotent: run cards upsert on their fingerprint-derived UUID and entries
upsert on (run_card_id, entry_id), so re-running after a sweep finishes is
safe — already-published runs are simply refreshed.

Staging targeting
-----------------
The harness's Supabase endpoint is env-overridable (mt_eval_harness/auth.py):
    MT_EVAL_SUPABASE_URL       — project URL
    MT_EVAL_SUPABASE_ANON_KEY  — anon/publishable key
    MT_EVAL_TOKEN_PATH         — session token file (auth.json shape)

This script defaults all three to the STAGING branch (xhvqqnxtvgggzcweofrp)
and the staging-bot session at ~/.mt-eval/auth.staging.json, and refuses to
run against the production project as a guard rail. Export the env vars
before invoking to point elsewhere (but never at production from here).

Usage:
    python3 arena/scripts/publish_all_reports.py            # publish all
    python3 arena/scripts/publish_all_reports.py --dry-run  # list only

Re-running for late sweep reports: just invoke the script again — new
run_*_report.json files are picked up automatically and previously
published runs are idempotently upserted.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path

ARENA_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ARENA_ROOT / "eval" / "logs" / "harness"

STAGING_URL = "https://xhvqqnxtvgggzcweofrp.supabase.co"
STAGING_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhodnFxbnh0dmdnZ3pjd2VvZnJwIiwicm9sZSI6"
    "ImFub24iLCJpYXQiOjE3ODExNjg0OTUsImV4cCI6MjA5Njc0NDQ5NX0."
    "wHmDxvpUuKYfBjhS1Ahq4KxM_gFcIsEIZL-4Lp9PRCs"
)
STAGING_TOKEN_PATH = str(Path.home() / ".mt-eval" / "auth.staging.json")

PROD_REF = "sjdomynysdljkbemupqa"

# --- Configure the harness endpoint BEFORE importing mt_eval_harness ---
# auth.py reads these at import time.
os.environ.setdefault("MT_EVAL_SUPABASE_URL", STAGING_URL)
os.environ.setdefault("MT_EVAL_SUPABASE_ANON_KEY", STAGING_ANON_KEY)
os.environ.setdefault("MT_EVAL_TOKEN_PATH", STAGING_TOKEN_PATH)

if PROD_REF in os.environ["MT_EVAL_SUPABASE_URL"]:
    sys.exit(
        "Refusing to run: MT_EVAL_SUPABASE_URL points at the PRODUCTION "
        "project. This script is for staging publishes only."
    )

sys.path.insert(0, str(ARENA_ROOT))

from mt_eval_harness.publish import (  # noqa: E402
    assemble_run_card,
    publish_to_supabase,
)


def _card_exists(card_id: str) -> bool:
    """Check whether a run card id is already on the leaderboard.

    The run_cards table has INSERT-only RLS (no UPDATE policy), so
    re-publishing an existing card 403s. Idempotency is achieved by
    skipping cards whose fingerprint-derived UUID already exists.
    """
    import urllib.request

    url = (
        f"{os.environ['MT_EVAL_SUPABASE_URL']}/rest/v1/run_cards"
        f"?id=eq.{card_id}&select=id"
    )
    req = urllib.request.Request(
        url, headers={"apikey": os.environ["MT_EVAL_SUPABASE_ANON_KEY"]}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return bool(json.loads(resp.read()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run", action="store_true",
        help="List the reports that would be published, then exit.",
    )
    parser.add_argument(
        "--reports-dir", default=str(REPORTS_DIR),
        help=f"Directory to glob for run_*_report.json (default: {REPORTS_DIR})",
    )
    args = parser.parse_args()

    reports = sorted(Path(args.reports_dir).glob("run_*_report.json"))
    if not reports:
        print(f"No reports found in {args.reports_dir}")
        return 1

    print(f"Found {len(reports)} report(s) in {args.reports_dir}")
    print(f"Target: {os.environ['MT_EVAL_SUPABASE_URL']}")
    print(f"Token:  {os.environ['MT_EVAL_TOKEN_PATH']}")

    if args.dry_run:
        for r in reports:
            print(f"  would publish: {r.name}")
        return 0

    results: list[tuple[str, str, str]] = []  # (name, status, detail)
    for report in reports:
        print(f"\n{'#' * 70}\n# {report.name}\n{'#' * 70}")
        try:
            entry_count = len(
                json.loads(report.read_text(encoding="utf-8")).get("entries", [])
            )
        except (json.JSONDecodeError, OSError) as exc:
            results.append((report.name, "SKIPPED", f"unreadable report: {exc}"))
            print(f"  ⚠ Skipping unreadable report: {exc}")
            continue

        try:
            _, card_id, _ = assemble_run_card(str(report))
            if _card_exists(card_id):
                results.append(
                    (report.name, "SKIPPED",
                     f"already published (card {card_id[:8]}…)")
                )
                print(f"  ↷ Already published as {card_id} — skipping.")
                continue
            publish_to_supabase(str(report), auto_confirm=True)
            results.append((report.name, "OK", f"{entry_count} entries"))
        except SystemExit as exc:
            # publish_to_supabase raises SystemExit on validation/auth/HTTP
            # failure. Log and continue with the remaining reports.
            results.append((report.name, "FAILED", f"SystemExit({exc.code})"))
        except Exception as exc:  # noqa: BLE001 — batch runner, keep going
            traceback.print_exc()
            results.append((report.name, "FAILED", str(exc)[:200]))

    print(f"\n{'=' * 70}\nSummary ({len(results)} report(s))\n{'=' * 70}")
    failed = skipped = 0
    for name, status, detail in results:
        marker = "✅" if status == "OK" else ("⚠" if status == "SKIPPED" else "❌")
        if status == "FAILED":
            failed += 1
        elif status == "SKIPPED":
            skipped += 1
        print(f"  {marker} {status:<8} {name}  ({detail})")
    print(
        f"\n  {len(results) - failed - skipped} published, "
        f"{skipped} skipped (already published/unreadable), {failed} failed"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
