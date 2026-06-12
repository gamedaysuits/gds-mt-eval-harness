#!/usr/bin/env python3
"""Run the top of the community-compute queue with your own API key.

The queue (champollion.dev/queue.json) is ranked by expected chain
value — mesh improvement per estimated dollar (see the queue
construction spec). This runner takes the top of that ranking and
executes the items' published ``run_command``s one by one, so
"contribute compute" becomes a single command:

    python3 scripts/run_queue.py --top 5            # run the 5 best items
    python3 scripts/run_queue.py --budget 2.50      # run from the top until
                                                    # ~$2.50 of estimated spend
    python3 scripts/run_queue.py --top 3 --dry-run  # show the plan only

Selection rules:
  - Items are taken in queue order (the ECV ranking) — no re-sorting.
  - ``--top N`` takes the first N runnable items; ``--budget X`` takes
    items from the top while the running total of ``est_cost_usd``
    stays within X (items with no cost estimate are skipped in budget
    mode, counted as $0.00 never — unknown != free).
  - Coached items are skipped unless ``--include-coached`` AND
    ``--coaching-file`` are given: a coached run without YOUR coaching
    file is meaningless (the placeholder in the run_command is
    substituted with the file you provide).

Safety:
  - Prints the full plan with estimated total spend and asks for
    confirmation before spending anything (``--yes`` skips, for cron).
  - Refuses to start without OPENROUTER_API_KEY in the environment.
  - Estimates are estimates: actual cost depends on provider pricing
    at run time. Each item's est_basis says where its number came from.
  - A failing item does not stop the batch by default (the next item
    is independent evidence); ``--stop-on-failure`` makes it strict.

Publishing afterwards stays explicit and under your name:
``mt-eval publish <report.json>`` per the contributing-compute guide.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

DEFAULT_QUEUE_URL = "https://champollion.dev/queue.json"
COACHING_PLACEHOLDER = "YOUR_COACHING.txt"


def load_queue(source: str) -> dict:
    """Load queue JSON from an http(s) URL or a local file path."""
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source, timeout=30) as resp:
            return json.loads(resp.read())
    return json.loads(Path(source).read_text(encoding="utf-8"))


def select_items(
    queue: dict,
    *,
    top: int | None = None,
    budget: float | None = None,
    include_coached: bool = False,
) -> tuple[list[dict], list[tuple[str, str]]]:
    """Pick items from the top of the ranking.

    Returns (selected, skipped) where skipped is [(item id, reason)].
    Exactly one of top/budget must be set (validated by the CLI).
    """
    selected: list[dict] = []
    skipped: list[tuple[str, str]] = []
    spend = 0.0
    for item in queue.get("items", []):
        if top is not None and len(selected) >= top:
            break
        if item.get("condition") == "coached" and not include_coached:
            skipped.append((item["id"], "coached (no --include-coached)"))
            continue
        est = item.get("est_cost_usd")
        if budget is not None:
            if est is None:
                skipped.append((item["id"], "no cost estimate (budget mode)"))
                continue
            if spend + est > budget:
                # Keep scanning: a cheaper item further down may still fit.
                skipped.append((item["id"], "would exceed budget"))
                continue
            spend += est
        selected.append(item)
    return selected, skipped


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--top", type=int, metavar="N",
                       help="Run the first N runnable items.")
    group.add_argument("--budget", type=float, metavar="USD",
                       help="Run items from the top while estimated "
                            "spend stays within this amount.")
    ap.add_argument("--queue", default=DEFAULT_QUEUE_URL,
                    help="Queue URL or local path (default: %(default)s)")
    ap.add_argument("--include-coached", action="store_true",
                    help="Allow coached items (requires --coaching-file).")
    ap.add_argument("--coaching-file", default=None,
                    help="Your coaching file, substituted into coached "
                         "items' run commands.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Print the plan and exit without running anything.")
    ap.add_argument("--stop-on-failure", action="store_true",
                    help="Abort the batch on the first failing item.")
    ap.add_argument("--yes", "-y", action="store_true",
                    help="Skip the confirmation prompt (cron use).")
    args = ap.parse_args()

    if args.top is not None and args.top <= 0:
        ap.error("--top must be a positive integer")
    if args.budget is not None and args.budget <= 0:
        ap.error("--budget must be a positive amount")
    if args.include_coached and not args.coaching_file:
        ap.error("--include-coached requires --coaching-file")
    if args.coaching_file and not Path(args.coaching_file).is_file():
        ap.error(f"coaching file not found: {args.coaching_file}")

    queue = load_queue(args.queue)
    selected, skipped = select_items(
        queue,
        top=args.top,
        budget=args.budget,
        include_coached=args.include_coached,
    )
    if not selected:
        print("No runnable items matched the selection.")
        for item_id, reason in skipped[:10]:
            print(f"  skipped {item_id}: {reason}")
        return 1

    est_known = [i["est_cost_usd"] for i in selected
                 if i.get("est_cost_usd") is not None]
    total_est = sum(est_known)
    print(f"Plan: {len(selected)} item(s) from the top of the queue "
          f"({queue.get('metadata', {}).get('priority_model', '')[:60]}…)")
    for i, item in enumerate(selected, 1):
        est = item.get("est_cost_usd")
        est_str = f"${est:.4f}" if est is not None else "cost unknown"
        print(f"  {i:>2}. {item['language_pair']:<10} {item['model']:<36} "
              f"{item['condition']:<8} {est_str}")
    unknown = len(selected) - len(est_known)
    print(f"Estimated spend: ${total_est:.4f}"
          + (f" + {unknown} item(s) with unknown cost" if unknown else ""))
    print("Estimates come from the queue's est_basis fields; actual cost "
          "depends on provider pricing at run time.")

    if args.dry_run:
        print("\n--dry-run: nothing executed.")
        return 0

    if not os.environ.get("OPENROUTER_API_KEY"):
        print("\nOPENROUTER_API_KEY is not set — refusing to start. "
              "Export your key first.", file=sys.stderr)
        return 1

    if not args.yes:
        try:
            answer = input("\nProceed and spend your tokens? [y/N]: ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return 1
        if answer.strip().lower() not in ("y", "yes"):
            print("Cancelled.")
            return 1

    failures = 0
    for i, item in enumerate(selected, 1):
        cmd = item["run_command"]
        if args.coaching_file:
            cmd = cmd.replace(COACHING_PLACEHOLDER, args.coaching_file)
        print(f"\n=== [{i}/{len(selected)}] {item['id']}\n$ {cmd}")
        proc = subprocess.run(cmd, shell=True)
        if proc.returncode != 0:
            failures += 1
            print(f"!!! item failed with exit code {proc.returncode}")
            if args.stop_on_failure:
                break

    print(f"\nDone: {len(selected) - failures}/{len(selected)} succeeded.")
    print("Publish your reports with: mt-eval publish <report.json>")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
