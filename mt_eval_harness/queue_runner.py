"""
Queue Runner — execute the top of the community compute queue.

The public queue (champollion.dev/queue.json) is ranked by expected
chain value: mesh improvement per estimated dollar (normative spec:
specifications/queue-construction on the arena site). This module turns
"contribute compute" into one command:

    mt-eval queue --top 5             # run the 5 best open items
    mt-eval queue --budget 2.50       # run from the top until ~$2.50
                                      # of estimated spend
    mt-eval queue --top 3 --dry-run   # show the plan, run nothing

Selection rules:
  - Items are taken in queue order — the ranking IS the priority
    model; the runner never re-sorts.
  - ``--top N`` takes the first N runnable items. ``--budget X`` walks
    from the top keeping a running total of ``est_cost_usd`` within X;
    items with no estimate are skipped in budget mode (unknown is
    never treated as free).
  - Coached items are skipped unless ``--include-coached`` AND
    ``--coaching-file`` are given — a coached run without YOUR
    coaching file is meaningless. The file you provide replaces the
    placeholder in the item's run_command.

Safety:
  - Prints the full plan with estimated spend and asks for
    confirmation before spending anything (``--yes`` skips, for cron).
  - Refuses to start without OPENROUTER_API_KEY in the environment.
  - A failing item does not stop the batch by default (each item is
    independent evidence); ``--stop-on-failure`` makes it strict.

Publishing afterwards stays explicit and under your name:
``mt-eval publish <report.json>``.
"""

from __future__ import annotations

import argparse
import json
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
    Exactly one of top/budget must be set (validated by the CLI layer).
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


def add_queue_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach the queue-runner flags (shared by `mt-eval queue` and the
    standalone scripts/run_queue.py)."""
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--top", type=int, metavar="N",
                       help="Run the first N runnable items.")
    group.add_argument("--budget", type=float, metavar="USD",
                       help="Run items from the top while estimated "
                            "spend stays within this amount.")
    parser.add_argument("--queue", default=DEFAULT_QUEUE_URL,
                        help="Queue URL or local path (default: %(default)s)")
    parser.add_argument("--include-coached", action="store_true",
                        help="Allow coached items (requires --coaching-file).")
    parser.add_argument("--coaching-file", default=None,
                        help="Your coaching file, substituted into coached "
                             "items' run commands.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the plan and exit without running "
                             "anything.")
    parser.add_argument("--stop-on-failure", action="store_true",
                        help="Abort the batch on the first failing item.")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Skip the confirmation prompt (cron use).")


def run_from_args(args: argparse.Namespace) -> int:
    """Execute the queue command for parsed arguments. Returns exit code."""
    if args.top is not None and args.top <= 0:
        print("--top must be a positive integer", file=sys.stderr)
        return 2
    if args.budget is not None and args.budget <= 0:
        print("--budget must be a positive amount", file=sys.stderr)
        return 2
    if args.include_coached and not args.coaching_file:
        print("--include-coached requires --coaching-file", file=sys.stderr)
        return 2
    if args.coaching_file and not Path(args.coaching_file).is_file():
        print(f"coaching file not found: {args.coaching_file}",
              file=sys.stderr)
        return 2

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
    model_line = (queue.get("metadata", {})
                  .get("priority_model", ""))[:60]
    print(f"Plan: {len(selected)} item(s) from the top of the queue "
          f"({model_line}…)")
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

    # Same key resolution as every other harness command (env var, then
    # .env.local / .env upward from CWD) — `mt-eval queue` must work
    # wherever `mt-eval run` works.
    try:
        from mt_eval_harness.api import load_api_key
        load_api_key()
    except Exception:
        print("\nOPENROUTER_API_KEY not found (environment or .env/"
              ".env.local) — refusing to start.", file=sys.stderr)
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
