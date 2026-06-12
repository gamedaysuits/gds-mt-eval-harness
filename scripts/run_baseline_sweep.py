#!/usr/bin/env python3
"""Baseline sweep driver: run the mt-eval harness across all curated corpora × a model lineup.

Design requirements (founder, 2026-06-11):
- Validate every model slug against the OpenRouter /models API before spending
  anything; record a pricing snapshot + timestamp per model (models drift).
- Hard budget ceiling with an early-stop checkpoint (default stop at 80%).
- Resume-safe: skips (corpus, model) pairs whose report JSON already exists.
- No publishing — runs accumulate locally in eval/logs/harness/; publishing to
  the staging branch is a separate, reviewed step.

Usage:
  python3 scripts/run_baseline_sweep.py --models google/gemini-3.5-flash \
      --budget 2500 [--corpora-dir datasets/curated] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ARENA = Path(__file__).resolve().parent.parent
CARDS_DIR = ARENA.parent / "cli" / "shared" / "language-cards"
LOGS_DIR = ARENA / "eval" / "logs" / "harness"
MANIFEST = ARENA / "eval" / "logs" / "sweep_manifest.json"
OPENROUTER_MODELS = "https://openrouter.ai/api/v1/models"


def fetch_models() -> dict:
    with urllib.request.urlopen(OPENROUTER_MODELS, timeout=30) as resp:
        data = json.loads(resp.read())
    return {m["id"]: m for m in data["data"]}


def target_lang_name(iso3: str) -> str | None:
    card = CARDS_DIR / f"{iso3}.json"
    if not card.exists():
        return None
    data = json.loads(card.read_text())
    return data.get("name")


def corpus_meta(path: Path) -> tuple[str, int] | None:
    """Return (target_iso3, entry_count) from a curated corpus filename + content."""
    m = re.match(r"^[a-z]{3}-([a-z]{3})-dev-v\d+\.json$", path.name)
    if not m:
        return None
    data = json.loads(path.read_text())
    count = data.get("entry_count") or len(data.get("entries", []))
    return m.group(1), count


def existing_report(corpus: Path, slug: str) -> bool:
    """A (corpus, model) pair is done if a report referencing both exists."""
    token = slug.split("/")[-1].replace("-", "").replace(".", "")
    stem = corpus.stem.replace("-", "")
    for report in LOGS_DIR.glob("run_*_report.json"):
        try:
            rc = json.loads(report.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        cfg = rc.get("config", rc)
        model = str(cfg.get("model", "")) + str(rc.get("model_slug", ""))
        corpus_ref = str(cfg.get("corpus", "")) + str(rc.get("corpus_path", ""))
        if slug in model or token in model.replace("-", "").replace(".", ""):
            if corpus.stem in corpus_ref or stem in corpus_ref.replace("-", ""):
                return True
    return False


def run_cost_from_output(text: str) -> float:
    m = re.search(r"Total cost\s+\$([0-9.]+)", text)
    return float(m.group(1)) if m else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True, help="OpenRouter slugs")
    ap.add_argument("--budget", type=float, default=2500.0)
    ap.add_argument("--stop-fraction", type=float, default=0.8,
                    help="Stop and report at this fraction of budget")
    ap.add_argument("--corpora-dir", default="datasets/curated")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--parallel", type=int, default=6,
                    help="Concurrent harness runs (each run is itself 8-way concurrent)")
    args = ap.parse_args()

    models = fetch_models()
    snapshot_ts = datetime.now(timezone.utc).isoformat()
    lineup = []
    for slug in args.models:
        if slug not in models:
            print(f"  ✗ SKIPPING {slug} — not on OpenRouter as of {snapshot_ts}")
            continue
        pricing = models[slug].get("pricing", {})
        lineup.append({"slug": slug, "pricing": pricing, "validated_at": snapshot_ts})
        print(f"  ✓ {slug}  in:{pricing.get('prompt')}  out:{pricing.get('completion')}")
    if not lineup:
        print("No valid models — aborting.")
        return 1

    corpora = sorted((ARENA / args.corpora_dir).glob("*-dev-v*.json"))
    print(f"\n{len(corpora)} corpora × {len(lineup)} models, budget ${args.budget:.2f} "
          f"(stop at {args.stop_fraction:.0%})\n")

    manifest = {"started": snapshot_ts, "budget": args.budget, "lineup": lineup, "runs": []}
    if MANIFEST.exists():
        prior = json.loads(MANIFEST.read_text())
        manifest["runs"] = prior.get("runs", [])
    spent = sum(r.get("cost", 0.0) for r in manifest["runs"])

    # Build the work queue up front. The manifest is the authoritative record
    # of completed (corpus, model) pairs — filename-based report matching
    # proved unreliable (44 duplicate re-runs on 2026-06-11).
    completed = {(r["corpus"], r["model"]) for r in manifest["runs"] if r.get("ok")}
    queue: list[tuple[Path, str, str, int]] = []
    for model in lineup:
        slug = model["slug"]
        for corpus in corpora:
            meta = corpus_meta(corpus)
            if meta is None:
                continue
            iso3, count = meta
            lang = target_lang_name(iso3)
            if not lang:
                print(f"  ? no language card name for {iso3}, skipping {corpus.name}")
                continue
            if (corpus.stem, slug) in completed:
                print(f"  = done already (manifest): {corpus.stem} × {slug}")
                continue
            queue.append((corpus, slug, lang, count))

    print(f"\n{len(queue)} runs queued, {args.parallel} parallel workers\n")
    if args.dry_run:
        for corpus, slug, lang, count in queue:
            print(f"→ would run {corpus.stem} ({count} entries, {lang}) × {slug}")
        return 0

    lock = threading.Lock()
    state = {"spent": spent, "stopped": False}
    # Stagger launches: run IDs are second-granular timestamps; simultaneous
    # starts of the same model+condition would collide on the log filename.
    launch_gate = threading.Lock()

    def worker(item: tuple[Path, str, str, int]) -> None:
        corpus, slug, lang, count = item
        with lock:
            if state["stopped"]:
                return
            if state["spent"] >= args.budget * args.stop_fraction:
                state["stopped"] = True
                print(f"\nBUDGET CHECKPOINT: ${state['spent']:.2f} "
                      f"≥ {args.stop_fraction:.0%} of ${args.budget:.2f}. Stopping queue.")
                return
        with launch_gate:
            time.sleep(1.2)
            proc = subprocess.Popen(
                [sys.executable, "-m", "mt_eval_harness.cli", "run",
                 "--corpus", str(corpus), "--model", slug, "--target-lang", lang],
                cwd=ARENA, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL, text=True)
        print(f"→ {corpus.stem} ({count} entries, {lang}) × {slug}")
        try:
            stdout, stderr = proc.communicate(timeout=3600)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
        cost = run_cost_from_output(stdout)
        ok = proc.returncode == 0
        with lock:
            state["spent"] += cost
            manifest["runs"].append({
                "corpus": corpus.stem, "model": slug, "lang": lang,
                "cost": cost, "ok": ok, "ts": datetime.now(timezone.utc).isoformat(),
            })
            MANIFEST.write_text(json.dumps(manifest, indent=2))
            tail = stdout.strip().splitlines()[-1] if stdout.strip() else ""
            print(f"  {'✓' if ok else '✗'} {corpus.stem} × {slug}  ${cost:.4f}  "
                  f"[total ${state['spent']:.2f}]  {tail[:60]}")
            if not ok:
                err = (stderr or stdout).strip().splitlines()
                print("    " + "\n    ".join(err[-5:]))

    with ThreadPoolExecutor(max_workers=max(1, args.parallel)) as pool:
        futures = [pool.submit(worker, item) for item in queue]
        for f in as_completed(futures):
            f.result()

    with lock:
        MANIFEST.write_text(json.dumps(manifest, indent=2))
        print(f"\nSweep {'stopped at budget checkpoint' if state['stopped'] else 'complete'}. "
              f"Total spent this manifest: ${state['spent']:.2f}")
        return 2 if state["stopped"] else 0


if __name__ == "__main__":
    sys.exit(main())
