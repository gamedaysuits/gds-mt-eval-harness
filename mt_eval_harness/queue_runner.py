"""
Queue Runner — execute the top of the community compute queue.

The public queue (champollion.dev/queue.json) is ranked by expected
chain value: mesh improvement per estimated dollar (normative spec:
specifications/queue-construction on the arena site). This module turns
"contribute compute" into one command:

    mt-eval queue --budget 2.50       # run from the top until ~$2.50
                                      # of estimated spend
    mt-eval queue --top 5             # run the 5 best open items
    mt-eval queue --top 3 --dry-run   # show the plan, run nothing

Selection rules:
  - Items are taken in queue order — the ranking IS the priority
    model; the runner never re-sorts.
  - ``--budget X`` walks from the top keeping a running total of
    ``est_cost_usd`` within X; items with no estimate are skipped
    in budget mode (unknown is never treated as free). An item is
    only selected if its estimated cost fits ENTIRELY within the
    remaining budget — no partial runs.
  - ``--top N`` takes the first N runnable items.
  - Coached items are skipped unless ``--include-coached`` AND
    ``--coaching-file`` are given — a coached run without YOUR
    coaching file is meaningless. The file you provide replaces the
    placeholder in the item's run_command.

Budget guard:
  After each completed run, actual cost is read from the report
  JSON. Before starting the next item, the runner checks whether
  ``actual_spend_so_far + est_next_item > budget``. If actual
  costs are tracking higher than estimated, the batch stops early
  rather than exceeding the stated budget. Contributors are never
  charged more than they agreed to.

Safety:
  - Prints the full plan with estimated spend and asks for
    confirmation before spending anything (``--yes`` skips, for cron).
  - Refuses to start without a valid API key for the selected
    provider (auto-detected or specified with ``--provider``).
  - A failing item does not stop the batch by default (each item is
    independent evidence); ``--stop-on-failure`` makes it strict.

Publishing:
  Results are auto-published to the leaderboard after each
  successful run. Pass ``--no-publish`` to skip auto-publishing
  (you can always publish manually later with ``mt-eval publish``).
  OAuth authentication is established once at the start of the
  batch — before any tokens are spent.
"""

from __future__ import annotations

import argparse
import glob
import json
import logging
import math
import os
import random
import re
import shlex
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_QUEUE_URL = "https://champollion.dev/queue.json"
COACHING_PLACEHOLDER = "YOUR_COACHING.txt"

# Default report output directory (must match config.DEFAULT_OUTPUT_DIR)
DEFAULT_OUTPUT_DIR = "eval/logs/harness"

# Maps provider names to the environment variable that holds the API key.
# These match the providers in mt_eval_harness.providers.registry.
PROVIDER_KEY_MAP: dict[str, str] = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai":     "OPENAI_API_KEY",
    "anthropic":  "ANTHROPIC_API_KEY",
    "gemini":     "GOOGLE_API_KEY",
}


def detect_provider() -> str | None:
    """Auto-detect the best available provider by scanning for API keys.

    Checks environment variables in priority order. Returns the
    provider name string (e.g. 'openrouter') or None if no key is
    found anywhere.

    Priority order: openrouter first (it proxies all models), then
    direct providers in alphabetical order.
    """
    for provider_name, env_var in PROVIDER_KEY_MAP.items():
        if os.environ.get(env_var):
            return provider_name

    # Also check .env/.env.local files via dotenv
    try:
        from dotenv import dotenv_values, find_dotenv
        for filename in (".env.local", ".env"):
            env_path = find_dotenv(filename=filename, usecwd=True)
            if env_path:
                values = dotenv_values(env_path)
                for provider_name, env_var in PROVIDER_KEY_MAP.items():
                    if values.get(env_var):
                        return provider_name
    except ImportError:
        pass

    return None


def load_queue(source: str) -> dict:
    """Load queue JSON from an http(s) URL or a local file path."""
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source, timeout=30) as resp:
            return json.loads(resp.read())
    return json.loads(Path(source).read_text(encoding="utf-8"))


# Anti-collision: when many contributors run the donate/budget flow at the
# same moment, a strict "take the top N" hands every worker the identical
# items — N independent runs of the same (model, corpus) pair, N× the donated
# spend for one leaderboard row. Spreading selection with a priority-weighted
# random order keeps high-value items running most often while making it
# vanishingly unlikely that 1,000 simultaneous workers pile onto the same
# item. Replication stays possible (it is scientifically useful); a
# 100×-the-same-item dogpile does not.
#
# SPREAD_DECAY sets how fast selection probability falls with queue rank: an
# item at rank r is weighted exp(-r / SPREAD_DECAY). Larger = flatter = wider
# fan-out (less dogpile) at the cost of a gentler priority tilt.
#
# Tuned empirically against the REAL queue (variable item cost), NOT a uniform-
# cost toy: at the default donate budget ($2) a worker takes ~30 items, and the
# earlier value 300.0 piled the busiest item onto ~40% of 1,000 simultaneous
# workers — cheap top-ranked items get packed into nearly everyone's budget.
# 750.0 cuts that to ~14% while preserving the priority tilt (rank-0 still
# ~3.3x a deep-tail item; exp(900/750)≈3.32 > the 3x floor the tilt test
# guards). The residual ~12-14% is harmless and intentional: identical runs
# dedupe on publish (same fingerprint UUID, immutable row), and event-driven
# queue regen drops a pair shortly after the first publish so later workers
# don't repeat it. Flatter decay barely helps (a cheap-item floor ~12% that
# decay alone can't break) and erodes the tilt. See test_queue_spread.py.
SPREAD_DECAY = 750.0


def _spread_order(
    items: list[dict],
    rng: "random.Random",
    decay: float = SPREAD_DECAY,
) -> list[dict]:
    """Return a priority-weighted random permutation of ``items``.

    Uses the Efraimidis–Spirakis weighted-sampling key: each item at rank
    ``r`` (its position in the priority ranking) gets a sort key
    ``rng.random() ** (1 / weight)`` with ``weight = exp(-r / decay)``, and
    items are ordered by that key descending. Higher-priority (lower-rank)
    items tend to land at the front — so they run most often — but every item
    has a chance to surface early, so simultaneous workers fan out across the
    whole queue instead of all taking the same prefix.
    """
    if decay <= 0 or len(items) <= 1:
        return list(items)
    keyed: list[tuple[float, int, dict]] = []
    for rank, item in enumerate(items):
        weight = math.exp(-rank / decay)
        # rng.random() in [0,1); with weight>0 the key is well-defined. A
        # draw of exactly 0.0 yields key 0.0 (sorts last), which is fine.
        key = rng.random() ** (1.0 / weight)
        keyed.append((key, rank, item))
    # Highest key first; rank breaks ties deterministically.
    keyed.sort(key=lambda t: (-t[0], t[1]))
    return [item for _key, _rank, item in keyed]


def select_items(
    queue: dict,
    *,
    top: int | None = None,
    budget: float | None = None,
    include_coached: bool = False,
    spread: bool = False,
    rng: "random.Random | None" = None,
    decay: float = SPREAD_DECAY,
) -> tuple[list[dict], list[tuple[str, str]]]:
    """Pick items from the top of the ranking.

    Returns (selected, skipped) where skipped is [(item id, reason)].
    Exactly one of top/budget must be set (validated by the CLI layer).

    Budget mode guarantees:
      - An item is selected only if its estimated cost fits entirely
        within the remaining budget (no partial runs).
      - Items with no cost estimate are skipped (unknown ≠ free).
      - Items that would push cumulative estimated cost over the budget
        are skipped, but scanning continues — a cheaper item further
        down may still fit.

    Anti-collision: with ``spread=True`` the candidate order is a
    priority-weighted random permutation (see ``_spread_order``) before
    selection, so simultaneous workers do not all pick the same top items.
    Default is ``spread=False`` (deterministic top-order, which the shared
    selection vectors and the JS port rely on) — the CLI turns spread on for
    the ``--budget`` donate flow. Pass ``rng`` (a ``random.Random``) for
    reproducible selection.

    SSOT: This is the canonical implementation. A JS port exists at
    mcp-server/src/tools/queue.js (filterQueue). Both are tested
    against shared/queue-selection-vectors.json — if you change
    behavior here, update the vectors and run both test suites.
    """
    items = list(queue.get("items", []))
    if spread:
        items = _spread_order(items, rng or random.Random(), decay)

    selected: list[dict] = []
    skipped: list[tuple[str, str]] = []
    spend = 0.0
    for item in items:
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


def _extract_error_hint(output: str) -> str:
    """Pull the one-line useful error from subprocess output.

    When ``mt-eval run`` fails, it may emit a multi-line traceback.
    Instead of showing all of that to the user, we extract the
    meaningful line — the RuntimeError message, the "✗" line from
    the clean handler, or the first HTTP error code.
    """
    if not output:
        return ""

    # cli.py's clean handler prints "  ✗ <message>"
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("✗ "):
            return stripped[2:].strip()

    # Look for RuntimeError/ValueError messages (the raise line)
    for line in reversed(output.splitlines()):
        stripped = line.strip()
        if stripped.startswith("RuntimeError:") or stripped.startswith("ValueError:"):
            # Strip the exception class prefix
            _, _, msg = stripped.partition(":")
            return msg.strip()[:160]

    # Look for HTTP error codes in the output
    for pattern in ("HTTP 401", "HTTP 402", "HTTP 403", "HTTP 404", "HTTP 400"):
        if pattern in output:
            # Find the line containing it
            for line in output.splitlines():
                if pattern in line:
                    return line.strip()[:160]

    # Last resort: the last non-empty line (usually the error)
    for line in reversed(output.splitlines()):
        stripped = line.strip()
        if stripped and not stripped.startswith("File ") and not stripped.startswith("at "):
            return stripped[:160]

    return ""


def _prompt_reenter_key(env_var: str) -> str | None:
    """Prompt the user to paste a new API key after a failure.

    Returns the new key string, or None if the user declines/cancels.
    Persists the key to .env.local so future runs don't need to ask.
    """
    print(f"  Paste your {env_var} below (or press Enter to stop):")
    try:
        key = input("  → ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n  Cancelled.")
        return None

    if not key:
        return None

    # Persist to .env.local so the user doesn't have to do this again
    env_file = Path.home() / ".env.local"
    try:
        existing = env_file.read_text() if env_file.exists() else ""
        lines = existing.splitlines()
        # Replace existing line or append
        replaced = False
        new_lines = []
        for line in lines:
            if line.startswith(f"{env_var}="):
                new_lines.append(f"{env_var}={key}")
                replaced = True
            else:
                new_lines.append(line)
        if not replaced:
            new_lines.append(f"{env_var}={key}")
        env_file.write_text("\n".join(new_lines) + "\n")
        env_file.chmod(0o600)
        print(f"  ✓ Saved to {env_file} (chmod 600)")
    except OSError as e:
        # Non-fatal — we still have it in the environment for this session
        logger.warning("Could not persist key to %s: %s", env_file, e)

    return key


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
    parser.add_argument("--provider", default=None,
                        choices=list(PROVIDER_KEY_MAP.keys()),
                        help="LLM API provider. Auto-detected from your "
                             "environment if not specified. "
                             "(%(choices)s)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the plan and exit without running "
                             "anything.")
    parser.add_argument("--stop-on-failure", action="store_true",
                        help="Abort the batch on the first failing item.")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Skip the confirmation prompt (cron use).")
    parser.add_argument("--no-publish", action="store_true",
                        help="Skip auto-publishing after each run. Results "
                             "can still be published manually later with "
                             "'mt-eval publish'.")
    parser.add_argument("--jobs", "-j", type=int, default=None, metavar="N",
                         help="Number of queue items to run concurrently "
                              "(default: 8, or 1 for ≤3 items). Higher "
                              "values finish faster but may hit API rate "
                              "limits.")
    parser.add_argument("--timeout", type=int, default=300, metavar="SECS",
                         help="Per-item timeout in seconds (default: 300). "
                              "Items exceeding this are killed and skipped.")
    spread_group = parser.add_mutually_exclusive_group()
    spread_group.add_argument(
        "--spread", dest="spread", action="store_true", default=None,
        help="Spread selection across a priority band so simultaneous "
             "contributors don't all run the same items (default for "
             "--budget, the donate flow).")
    spread_group.add_argument(
        "--no-spread", dest="spread", action="store_false",
        help="Disable anti-collision spread; take items in strict queue "
             "order (default for --top).")
    parser.add_argument("--spread-seed", type=int, default=None, metavar="N",
                        help="Seed the spread RNG for reproducible selection "
                             "(testing/debugging).")


# ---------------------------------------------------------------------------
# Post-run helpers
# ---------------------------------------------------------------------------

def _find_latest_report(item: dict) -> Path | None:
    """Find the most recent report file matching a queue item.

    The ``mt-eval run`` command writes reports to eval/logs/harness/
    with the naming convention ``run_<timestamp>_report.json``. We
    match on the corpus stem and model slug found inside the report to
    avoid picking up an unrelated report.
    """
    output_dir = Path(DEFAULT_OUTPUT_DIR)
    if not output_dir.is_dir():
        return None

    # Build expected identifiers from the queue item to match
    # against report contents.
    item_corpus = item.get("corpus_stem", "")
    item_model = item.get("model", "")

    # Get all report files sorted by modification time (newest first)
    reports = sorted(
        output_dir.glob("run_*_report.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    for report_path in reports[:10]:  # Only check recent reports
        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        # Match by corpus filename and model slug
        config = data.get("config", {})
        report_corpus = Path(config.get("corpus_path", "")).stem
        report_model = config.get("model", "")

        # The queue item's corpus_stem is derived from the corpus filename
        # (e.g., "eng-crk-dev-v1") and the model slug matches the full
        # OpenRouter path (e.g., "anthropic/claude-haiku-4.5").
        if item_corpus and item_corpus in report_corpus:
            if item_model and item_model in report_model:
                return report_path
        # Fallback: just return the newest report if it was created
        # within the last 60 seconds (the run just finished)
        import time
        if time.time() - report_path.stat().st_mtime < 60:
            return report_path

    return None


def _read_report_cost(report_path: Path) -> float:
    """Extract actual cost from a TestReport JSON.

    Returns 0.0 if the file can't be read or lacks cost data.
    """
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
        return float(data.get("overall", {}).get("total_cost_usd", 0.0))
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return 0.0


def _read_report_chrf(report_path: Path) -> float | None:
    """Extract chrF++ score from a TestReport JSON."""
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
        return data.get("overall", {}).get("avg_chrf")
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return None


def _find_report_in_dir(report_dir: str | Path) -> Path | None:
    """Find the report this item wrote to its OWN isolated output dir.

    Each queue item runs with a unique ``--output-dir`` (see the pre-build
    loop), so its directory contains exactly one ``*_report.json``. This is
    collision-free under concurrency, unlike the shared-dir, newest-wins
    heuristic in ``_find_latest_report`` (which cross-matches when several
    items finish within the same 60-second window).
    """
    d = Path(report_dir)
    if not d.is_dir():
        return None
    reports = sorted(
        d.glob("*_report.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return reports[0] if reports else None


def _auto_publish(report_path: str, label: str = "") -> bool:
    """Publish one report, swallowing EVERY failure mode. Returns success.

    ``publish_to_supabase`` raises ``SystemExit`` on a 4xx response, a failed
    integrity gate, a row-validation failure, or after exhausting its upload
    retries. ``SystemExit`` derives from ``BaseException``, so a bare
    ``except Exception`` does NOT catch it — which means, before this helper,
    a single bad publish would unwind the whole batch loop: every remaining
    paid item skipped, no end-of-run summary, the contributor's compute
    silently lost. This helper guarantees that can never happen. It returns
    True on success and False on any failure, and only ever re-raises
    KeyboardInterrupt (so Ctrl+C still works).
    """
    try:
        from mt_eval_harness.publish import publish_to_supabase
        publish_to_supabase(report_path, auto_confirm=True)
        return True
    except KeyboardInterrupt:
        raise
    except (Exception, SystemExit) as exc:
        where = f" for {label}" if label else ""
        print(f"    ⚠ Publish failed{where}: {exc}")
        print(f"    → Re-publish later with: mt-eval publish {report_path}")
        return False


# Markers used to tell a genuine auth/key problem (worth re-entering a key)
# apart from a transient rate-limit / timeout / provider blip (back off and
# keep going — do NOT stall the batch on a misleading "bad key" prompt).
_TRANSIENT_MARKERS = (
    "429", "rate limit", "rate_limit", "too many requests", "overloaded",
    "500", "502", "503", "504", "529", "timeout", "timed out",
    "temporarily", "connection", "network", "econnreset",
)
_AUTH_MARKERS = (
    "401", "403", "invalid api key", "invalid_api_key", "user not found",
    "no auth credentials", "unauthorized", "permission denied",
)


def _classify_failure(status: str, error_hint: str) -> str:
    """Bucket a failed/timed-out item: 'auth' | 'transient' | 'other'.

    The circuit breaker uses this so a burst of 429s or timeouts does NOT
    masquerade as a bad API key and stall the batch on a terminal prompt.
    Only genuine auth failures (401/403/invalid key) earn a key-re-entry
    offer; transient failures are absorbed and the batch keeps moving.

    Transient markers are checked first because some rate-limit response
    bodies also mention the word "key" — a 429 is a rate limit, not an auth
    problem, no matter what else is in the message.
    """
    if status == "timeout":
        return "transient"
    h = (error_hint or "").lower()
    if any(m in h for m in _TRANSIENT_MARKERS):
        return "transient"
    if any(m in h for m in _AUTH_MARKERS):
        return "auth"
    return "other"


# ---------------------------------------------------------------------------
# Coverage skip — don't re-run combos already on the leaderboard
# ---------------------------------------------------------------------------

def _fetch_published_combos() -> set | None:
    """Return {(dataset_id, model_slug, condition)} already on the leaderboard.

    Lets the queue skip combos a contributor (or another worker) has already
    completed, so donated compute moves THROUGH the lineup instead of re-running
    covered work. The match key is exact registry/slug strings — the queue
    item's (corpus_id, model, condition) equals the run_card's
    (dataset_id, model_slug, condition); no language-pair format ambiguity.

    Best-effort + read-only (anon, public SELECT). Returns None on ANY failure
    so the caller runs the full queue rather than blocking. Disable with
    MT_EVAL_NO_COVERAGE_SKIP=1.
    """
    if os.environ.get("MT_EVAL_NO_COVERAGE_SKIP", "").lower() in ("1", "true", "yes"):
        return None
    try:
        from mt_eval_harness.auth import SUPABASE_URL, SUPABASE_ANON_KEY
    except Exception:
        return None
    combos: set = set()
    page = 1000
    offset = 0
    try:
        while True:
            url = (f"{SUPABASE_URL}/rest/v1/run_cards"
                   f"?select=dataset_id,model_slug,condition&trust=neq.disqualified"
                   f"&limit={page}&offset={offset}&order=id.asc")
            req = urllib.request.Request(url, headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                rows = json.loads(resp.read())
            for r in rows:
                combos.add((r.get("dataset_id"), r.get("model_slug"), r.get("condition")))
            if not isinstance(rows, list) or len(rows) < page:
                break
            offset += page
        return combos
    except Exception as e:  # network / parse / unreachable → don't filter
        logger.debug("coverage-skip: could not fetch published combos: %s", e)
        return None


def _drop_covered(items: list, covered: set) -> list:
    """Drop queue items whose (corpus_id, model, condition) is already on the
    leaderboard. Pure (no I/O) so it's unit-tested. Items missing any of the
    three keys simply won't match a covered tuple, so they're kept (safe)."""
    return [
        it for it in items
        if (it.get("corpus_id"), it.get("model"), it.get("condition")) not in covered
    ]


# ---------------------------------------------------------------------------
# Main execution loop
# ---------------------------------------------------------------------------

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

    no_publish = getattr(args, "no_publish", False)

    queue = load_queue(args.queue)
    # Coverage skip: drop combos already completed on the leaderboard so donated
    # compute proceeds through the lineup instead of re-running covered work.
    # The spread (below) handles intra-batch diversity; this handles combos
    # already published (by you on a prior run, or another worker). Best-effort —
    # on any fetch failure the full queue runs. Pairs with the nightly queue
    # regen, which refreshes the priority ranking.
    _covered = _fetch_published_combos()
    if _covered:
        _items = queue.get("items", [])
        queue["items"] = _drop_covered(_items, _covered)
        _dropped = len(_items) - len(queue["items"])
        if _dropped:
            print(f"  Coverage skip: {_dropped} combo(s) already on the leaderboard — running the rest.")
    # Anti-collision: spread defaults ON for the --budget donate flow (many
    # contributors run simultaneously and don't care which items they get) and
    # OFF for an explicit --top (the user asked for the best N specifically).
    spread = getattr(args, "spread", None)
    if spread is None:
        spread = args.budget is not None
    spread_seed = getattr(args, "spread_seed", None)
    rng = random.Random(spread_seed) if spread else None
    selected, skipped = select_items(
        queue,
        top=args.top,
        budget=args.budget,
        include_coached=args.include_coached,
        spread=spread,
        rng=rng,
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
    if args.budget is not None:
        print(f"Budget cap: ${args.budget:.2f} — the runner will stop early "
              "if actual costs exceed estimates.")
    if len(selected) > 20:
        print(f"\n  ⚠ Large batch: this will run {len(selected)} benchmarks "
              f"and make many API calls.")
        print("    It can take a while. Cap it with --top N (e.g. --top 10) "
              "or a smaller --budget;")
        print("    Ctrl+C stops safely and keeps everything already published.")
    if not no_publish:
        print("Results will be auto-published after each run.")

    if args.dry_run:
        print("\n--dry-run: nothing executed.")
        return 0

    # --- Step 1: Authenticate for publishing (before spending tokens) ---
    # The session is cached to ~/.mt-eval/auth.json, so subsequent
    # publish_to_supabase calls reuse it without re-prompting.
    if not no_publish:
        print("\n" + "=" * 60)
        print("Step 1: Sign in (your runs will be attributed to you)")
        print("=" * 60)
        try:
            from mt_eval_harness.auth import get_session, get_submitter_name
            session = get_session()
            submitter = get_submitter_name(session)
            print(f"  ✓ Authenticated as {submitter}")
        except SystemExit:
            print("\n  Authentication is required to publish results.",
                  file=sys.stderr)
            print("  Re-run with --no-publish to skip, or sign in above.",
                  file=sys.stderr)
            return 1

    # --- Step 2: Resolve provider and verify API key ---
    print(f"\n{'=' * 60}")
    print("Step 2: API key")
    print("=" * 60)
    provider_name = getattr(args, "provider", None)
    if not provider_name:
        provider_name = detect_provider()
    if not provider_name:
        available = ", ".join(PROVIDER_KEY_MAP.values())
        print(f"\nNo API key found. Set one of: {available}",
              file=sys.stderr)
        print("  Or pass --provider explicitly.", file=sys.stderr)
        return 1
    try:
        from mt_eval_harness.providers import get_provider
        provider = get_provider(provider_name)
        provider.load_api_key()
        env_var = PROVIDER_KEY_MAP[provider_name]
        print(f"  ✓ {env_var} found (provider: {provider_name})")
    except Exception:
        env_var = PROVIDER_KEY_MAP.get(provider_name, "API_KEY")
        print(f"\n{env_var} not found (environment or .env/"
              ".env.local) — refusing to start.", file=sys.stderr)
        return 1

    # --- Step 3: Confirm spend ---
    if not args.yes:
        try:
            answer = input("\nProceed and spend your tokens? [y/N]: ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")
            return 1
        if answer.strip().lower() not in ("y", "yes"):
            print("Cancelled.")
            return 1

    # --- Step 4: Execute items ---
    #
    # Concurrency strategy:
    #   - ≤3 items: sequential (jobs=1) for immediate per-item feedback,
    #     matching the typical --budget 2 scenario. The user sees each
    #     run start and finish before the next begins.
    #   - >3 items: concurrent (default 8) for throughput.
    #   - --jobs always overrides when explicitly set.
    #
    # Safety:
    #   - Per-item timeout (default 300s) kills hung subprocesses.
    #   - Ctrl+C sets auth_abort; in-flight runs finish (tokens already
    #     spent), but no new items start. Second Ctrl+C force-kills.
    #   - Budget guard checks BEFORE dispatching each new item, not
    #     just after completions — prevents over-spending in concurrent
    #     mode.
    #   - 3 consecutive failures offer key re-entry instead of silently
    #     stopping.

    jobs_explicit = getattr(args, "jobs", None) is not None
    # Default concurrency. Direct providers (anthropic/openai/gemini) have far
    # tighter rate limits than OpenRouter's pooled proxy, so a large `give`
    # batch hammered at 8× would 429-storm. Be gentler when off OpenRouter.
    default_jobs = 8 if provider_name == "openrouter" else 4
    jobs = getattr(args, "jobs", None) or default_jobs
    item_timeout = getattr(args, "timeout", 300) or 300
    stop_on_failure = getattr(args, "stop_on_failure", False)

    # Sequential-first for small batches
    if len(selected) <= 3 and not jobs_explicit:
        jobs = 1

    mode_label = "sequential" if jobs == 1 else f"{jobs} concurrent"
    print(f"\n{'=' * 60}")
    print(f"Running {len(selected)} benchmark{'s' if len(selected) != 1 else ''}"
          f" ({mode_label})")
    print("=" * 60)
    print(f"  Per-item timeout: {item_timeout}s")
    print(f"  Press Ctrl+C to stop safely — completed runs are already published.")
    print()

    # Pre-build commands for each item.
    #
    # Each item gets its OWN report output dir (--output-dir) so the runner
    # reads back exactly that item's report — never a concurrent sibling's.
    # Without isolation, discovery falls back to "newest *_report.json in the
    # shared dir", which cross-matches under concurrency (the default for >3
    # items) — mis-attributing cost/score and, worse, leaving some results
    # unpublished while others publish twice. Reports land under
    # eval/logs/harness/queue/ so they survive for manual `mt-eval publish`.
    for index, item in enumerate(selected, 1):
        cmd = item["run_command"]
        if args.coaching_file:
            cmd = cmd.replace(COACHING_PLACEHOLDER, args.coaching_file)
        if provider_name != "openrouter" and "--provider" not in cmd:
            cmd = cmd.replace("mt-eval run",
                              f"mt-eval run --provider {provider_name}")
        # Isolate this item's report output, unless the command already pins
        # its own output dir (then fall back to heuristic discovery).
        if "--output-dir" in cmd or " -o " in cmd:
            item["_report_dir"] = None
        else:
            safe_id = re.sub(r"[^A-Za-z0-9._-]", "_",
                             str(item.get("id", f"item{index}")))
            report_dir = (Path(DEFAULT_OUTPUT_DIR) / "queue"
                          / f"{index:03d}_{safe_id}")
            item["_report_dir"] = str(report_dir)
            cmd = cmd.replace(
                "mt-eval run",
                f"mt-eval run --output-dir {shlex.quote(str(report_dir))}",
                1,
            )
        item["_cmd"] = cmd

    import threading
    from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

    # Shared state — protected by a lock for the few mutable counters.
    lock = threading.Lock()
    completed = []          # [(item, report_path, actual_cost, chrf)]
    failed_items = []       # [(item, error_hint)]
    timed_out_items = []    # [(item, timeout_seconds)]
    done_count = 0
    total_items = len(selected)
    actual_spend = 0.0
    budget = args.budget

    # auth_abort: set on signal, consecutive failures, budget exceeded,
    # or --stop-on-failure. Workers check before starting a subprocess.
    auth_abort = threading.Event()

    # Track running Popen objects so a second Ctrl+C can force-kill them.
    running_procs: set[subprocess.Popen] = set()
    proc_lock = threading.Lock()

    # --- Signal handling: graceful two-stage Ctrl+C ---
    interrupt_count = [0]
    original_sigint = signal.getsignal(signal.SIGINT)

    def _handle_sigint(signum, frame):
        interrupt_count[0] += 1
        if interrupt_count[0] == 1:
            print("\n")
            print("  Stopping gracefully — waiting for in-flight runs "
                  "to finish...")
            print("  (Completed runs are already published. "
                  "Press Ctrl+C again to force-kill.)")
            auth_abort.set()
        else:
            print("\n  Force-killing all running processes...")
            with proc_lock:
                for proc in list(running_procs):
                    try:
                        proc.kill()
                    except OSError:
                        pass
            signal.signal(signal.SIGINT, original_sigint)
            raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _handle_sigint)

    def _run_one(item: dict, index: int) -> dict:
        """Run a single queue item in a thread. Returns a result dict.

        Uses Popen + communicate(timeout=) so hung API calls are killed
        after item_timeout seconds instead of blocking the thread forever.
        """
        nonlocal done_count

        if auth_abort.is_set():
            return {"item": item, "status": "skipped", "index": index}

        cmd = item["_cmd"]

        # Start the subprocess and track it for force-kill.
        # stdin=DEVNULL is critical: the runner owns ALL terminal I/O. Each
        # `mt-eval run` child otherwise inherits our tty (the give flow runs
        # `mt-eval queue ... < /dev/tty`) and blocks forever on its own
        # end-of-run "Publish this run? [y/N]" prompt — whose text is hidden
        # inside our captured stdout pipe — until the per-item timeout kills
        # it. With DEVNULL the child sees a non-interactive stdin and skips
        # that prompt; the runner publishes instead.
        proc = subprocess.Popen(
            cmd, shell=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True,
        )
        with proc_lock:
            running_procs.add(proc)

        try:
            stdout, _ = proc.communicate(timeout=item_timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, _ = proc.communicate()
            with proc_lock:
                running_procs.discard(proc)
            with lock:
                done_count += 1
            return {
                "item": item, "status": "timeout",
                "output": stdout or "",
                "index": index,
                "timeout_seconds": item_timeout,
            }

        with proc_lock:
            running_procs.discard(proc)

        # Read this item's report from its OWN isolated output dir, so a
        # concurrent sibling's report can never be mistaken for ours.
        report_dir = item.get("_report_dir")
        if report_dir:
            report_path = _find_report_in_dir(report_dir)
        else:
            report_path = _find_latest_report(item)
        item_cost = 0.0
        item_chrf = None
        if report_path:
            item_cost = _read_report_cost(report_path)
            item_chrf = _read_report_chrf(report_path)

        with lock:
            done_count += 1

        if proc.returncode != 0:
            error_hint = _extract_error_hint(stdout or "")
            return {
                "item": item, "status": "failed",
                "error": error_hint, "output": stdout or "",
                "index": index,
            }

        return {
            "item": item, "status": "ok",
            "report_path": report_path,
            "cost": item_cost, "chrf": item_chrf,
            "index": index,
        }

    # --- Execution loop: incremental dispatch + heartbeat ---
    #
    # Items are submitted one-at-a-time (up to `jobs` concurrent).
    # Before each new submission the budget guard checks whether the
    # next item's estimated cost still fits. A 15-second heartbeat
    # reassures the user that work is happening during long runs.

    consecutive_failures = 0
    consecutive_auth_failures = 0   # only real 401/403/invalid-key failures
    transient_notice_shown = False  # show the rate-limit hint at most once
    pending = list(enumerate(selected, 1))  # [(1-based index, item)]
    active_futures: dict = {}               # {future: (index, item)}
    start_time = time.time()

    try:
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            while pending or active_futures:
                # Fill slots up to `jobs`, checking budget before each
                while pending and len(active_futures) < jobs:
                    if auth_abort.is_set():
                        break
                    idx, item = pending[0]
                    # Pre-dispatch budget guard
                    if budget is not None:
                        est = item.get("est_cost_usd", 0) or 0
                        if actual_spend + est > budget:
                            pending.pop(0)
                            pair = item.get("language_pair", "???")
                            print(f"  ⊘ {pair:<10} skipped "
                                  f"(${est:.4f} would exceed remaining "
                                  f"budget)")
                            continue
                    pending.pop(0)
                    future = pool.submit(_run_one, item, idx)
                    active_futures[future] = (idx, item)

                if not active_futures:
                    break

                # Wait for the next completion OR a 15-second heartbeat
                done_set, _ = wait(
                    active_futures,
                    return_when=FIRST_COMPLETED,
                    timeout=15,
                )

                if not done_set:
                    # Heartbeat: reassure the user something is happening
                    elapsed = int(time.time() - start_time)
                    with lock:
                        current = done_count
                    in_flight = len(active_futures)
                    print(f"  ⏳ {elapsed}s elapsed — {in_flight} in flight, "
                          f"{current}/{total_items} done...")
                    continue

                for future in done_set:
                    idx, item = active_futures.pop(future)
                    try:
                        result = future.result()
                    except Exception as exc:
                        # Defensive: _run_one catches internally, but
                        # guard against unexpected threading errors.
                        result = {
                            "item": item, "status": "failed",
                            "error": str(exc), "index": idx,
                        }

                    pair = item.get("language_pair", "???")

                    if result["status"] == "skipped":
                        continue

                    # Progress bar
                    with lock:
                        current = done_count
                    pct = current / total_items
                    bar_w = 25
                    filled = int(bar_w * pct)
                    bar = "█" * filled + "░" * (bar_w - filled)

                    if result["status"] == "ok":
                        consecutive_failures = 0
                        consecutive_auth_failures = 0
                        cost = result["cost"]
                        chrf = result["chrf"]
                        actual_spend += cost
                        chrf_str = (f"chrF++ {chrf:.1f}"
                                    if chrf is not None else "—")
                        cost_str = f"${cost:.4f}" if cost > 0 else "—"
                        print(f"  {bar} {current}/{total_items}  "
                              f"✓ {pair:<10} {chrf_str:<14} {cost_str}")

                        # Auto-publish via _auto_publish, which can never
                        # raise (it swallows SystemExit too) — so one bad
                        # publish cannot abort the rest of the batch. Track
                        # the real outcome so the summary reports honestly.
                        rpath = result.get("report_path")
                        published = False
                        if no_publish:
                            published = False
                        elif rpath:
                            published = _auto_publish(str(rpath), pair)
                        else:
                            print(f"    ⚠ {pair}: run finished but no report "
                                  f"was found — cannot publish.")

                        completed.append((item, rpath, cost, chrf, published))

                    elif result["status"] == "timeout":
                        consecutive_failures += 1
                        consecutive_auth_failures = 0  # a timeout is not auth
                        t = result.get("timeout_seconds", item_timeout)
                        print(f"  {bar} {current}/{total_items}  "
                              f"⏱ {pair:<10} timed out after {t}s")
                        timed_out_items.append((item, t))

                    elif result["status"] == "failed":
                        consecutive_failures += 1
                        error_hint = result.get("error", "")
                        if _classify_failure("failed", error_hint) == "auth":
                            consecutive_auth_failures += 1
                        else:
                            consecutive_auth_failures = 0
                        print(f"  {bar} {current}/{total_items}  "
                              f"✗ {pair:<10} {error_hint[:80]}")
                        failed_items.append((item, error_hint))

                    # --stop-on-failure: halt on any failure or timeout
                    if (stop_on_failure
                            and result["status"] in
                            ("failed", "timeout")):
                        auth_abort.set()
                        print(f"\n  --stop-on-failure: halting "
                              f"after {pair}.")
                        for f in active_futures:
                            f.cancel()
                        break

                    # Circuit breaker. Distinguish a genuine auth/key problem
                    # (offer key re-entry) from a transient rate-limit/timeout
                    # storm (back off and keep going). Never stall the batch on
                    # a misleading "bad key" prompt the contributor may not be
                    # around to answer.
                    if (consecutive_auth_failures >= 3
                            and not auth_abort.is_set()):
                        ev = PROVIDER_KEY_MAP.get(
                            provider_name, "API_KEY"
                        )
                        print(
                            f"\n  {consecutive_auth_failures} consecutive auth "
                            f"failures (401/403) — your {ev} looks invalid or "
                            f"unauthorized."
                        )
                        new_key = _prompt_reenter_key(ev)
                        if new_key:
                            os.environ[ev] = new_key
                            consecutive_failures = 0
                            consecutive_auth_failures = 0
                            print("  ✓ Key updated — resuming.")
                        else:
                            auth_abort.set()
                            print("  Stopping remaining items.")
                            for f in active_futures:
                                f.cancel()
                            break
                    elif (consecutive_failures >= 5
                            and not transient_notice_shown
                            and not auth_abort.is_set()):
                        # Transient failures (rate limits / timeouts / provider
                        # blips), not an auth problem. Inform once and keep
                        # going — completed runs are already published, so we
                        # never throw progress away by stalling for input.
                        transient_notice_shown = True
                        print(
                            "\n  ⚠ Several failures in a row (rate limits, "
                            "timeouts, or provider errors) — not an auth "
                            "problem."
                        )
                        print(
                            "    Completed runs are already published. "
                            "Continuing — if this keeps up, re-run later or "
                            "with --jobs 2 / --timeout 600."
                        )

                    # Post-completion budget guard
                    if (budget is not None
                            and actual_spend > budget):
                        print(
                            f"\n  Budget guard: ${actual_spend:.4f} "
                            f"spent, exceeding ${budget:.2f} budget."
                        )
                        auth_abort.set()
                        for f in active_futures:
                            f.cancel()
                        break

    except KeyboardInterrupt:
        # Second Ctrl+C — signal handler already killed subprocesses
        pass
    finally:
        signal.signal(signal.SIGINT, original_sigint)

    # --- Step 5: Summary ---
    failures = len(failed_items)
    timeouts = len(timed_out_items)
    succeeded = len(completed)
    total_run = succeeded + failures + timeouts
    print(f"\n{'=' * 60}")

    if completed:
        published_count = sum(1 for *_rest, pub in completed if pub)
        publish_failed = [
            (item, rpath)
            for item, rpath, _cost, _chrf, pub in completed
            if not no_publish and not pub
        ]

        # Mesh highlight: only the pairs we actually published.
        pairs_lit = []
        for item, _rpath, _cost, _chrf, pub in completed:
            if not no_publish and not pub:
                continue
            pair = item.get("language_pair", "")
            if pair and pair not in pairs_lit:
                pairs_lit.append(pair)

        print(f"  🎉 You contributed {succeeded} "
              f"run{'s' if succeeded != 1 else ''} "
              f"to the translation mesh!")
        if not no_publish:
            print(f"     {published_count}/{succeeded} published to the "
                  f"leaderboard.")
        print()
        for item, rpath, cost, chrf, pub in completed:
            pair = item.get("language_pair", "???")
            chrf_str = (f"chrF++ {chrf:.1f}"
                        if chrf is not None else "—")
            if no_publish:
                status = "local only"
            elif pub:
                status = "published"
            else:
                status = "NOT published"
            print(f"    {pair:<10} {chrf_str:<14} "
                  f"${cost:.4f}  ({status})")

        print(f"\n  Total cost: ${actual_spend:.4f}"
              + (f"  (budget: ${budget:.2f})" if budget else ""))

        if publish_failed:
            print(f"\n  ⚠ {len(publish_failed)} result(s) ran but did not "
                  f"publish. Your compute was not wasted — the reports are")
            print("  saved locally; publish them any time with:")
            for _item, rpath in publish_failed:
                if rpath:
                    print(f"      mt-eval publish {rpath}")

        if not no_publish and pairs_lit:
            hl = ",".join(pairs_lit)
            print(f"\n  See your edges: "
                  f"https://champollion.dev/mesh?hl={hl}")
            print("  The mesh regenerates every few minutes — your "
                  "edges")
            print("  will light up shortly.")
    else:
        print(f"  No runs completed successfully "
              f"({failures} failed, {timeouts} timed out).")

    if timeouts:
        print(f"\n  ⏱ {timeouts} item(s) timed out "
              f"(>{item_timeout}s). Try --timeout N to adjust.")

    if failures:
        print(f"\n  ⚠ {failures}/{total_run} item(s) failed.")

    if interrupt_count[0] > 0:
        print(f"\n  Stopped by user signal — {len(pending)} "
              f"item(s) were not started.")

    print("=" * 60)

    return 0 if failures == 0 and timeouts == 0 else 1

