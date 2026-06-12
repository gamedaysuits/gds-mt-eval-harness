#!/usr/bin/env python3
"""Generate the public community-compute sweep queue.

Reads three sources of truth and emits ``cli/website/static/queue.json``,
the artifact behind champollion.dev/queue.json and the /contribute page:

  1. ``arena/datasets/registry.json`` — which dev-split corpora are open
     for community runs. Only corpora that are hosted in the public
     harness mirror (``access: "local"``, ``segment: "development"``) and
     carry a redistributable license (CC-BY family, non-NC) are queued.
     NC-licensed (EdTeKLA) and quarantined corpora are excluded — see
     docs/LICENSING.md (NC content stays out of open contribution lanes).
  2. ``arena/eval/logs/sweep_manifest.json`` — the validated model lineup
     and observed per-run costs from the 2026-06-11 baseline sweep.
     Cost estimates are either the *observed* cost for that exact
     (corpus, model) pair, or an extrapolation from the model's average
     cost per entry across the sweep (``est_basis`` says which).
  3. The public leaderboard REST endpoint (read-only anon key, same as
     cli/website/src/pages/leaderboard.js) — already-covered
     (dataset, model, condition) combos are dropped from the queue.

No claim-locking by design: run-card fingerprints make duplicate runs
harmless (identical fingerprints dedupe on publish; non-identical
duplicates are legitimate replications). "Pick any open item" is correct.

Usage:
  python3 scripts/generate_sweep_queue.py [--output ../cli/website/static/queue.json]
      [--offline]   # skip the leaderboard coverage query
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ARENA = Path(__file__).resolve().parent.parent
MONOREPO = ARENA.parent
REGISTRY = ARENA / "datasets" / "registry.json"
MANIFEST = ARENA / "eval" / "logs" / "sweep_manifest.json"
CARDS_DIR = MONOREPO / "cli" / "shared" / "language-cards"
DEFAULT_OUTPUT = MONOREPO / "cli" / "website" / "static" / "queue.json"

# Public, read-only Supabase config — identical to leaderboard.js.
# RLS restricts the anon key to SELECT; this script never writes.
SUPABASE_URL = "https://sjdomynysdljkbemupqa.supabase.co"
SUPABASE_ANON_KEY = "sb_publishable_bV6CFNFnzxhQI0wlBx2J0A_5Vm5gFBp"

# Raw-file base of the public harness mirror (arena/ subtree).
MIRROR_RAW = (
    "https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main"
)

CONDITIONS = ("naive", "coached")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def model_short(slug: str) -> str:
    """Normalize a model slug for coverage comparison.

    The leaderboard stores both full slugs ("anthropic/claude-sonnet-4.6")
    and short names ("claude-sonnet-4.6") depending on how the run was
    configured, so compare on the post-vendor segment, lowercased.
    """
    return slug.split("/")[-1].strip().lower()


def queue_corpora(registry: dict) -> list[dict]:
    """Select corpora eligible for the public queue.

    Eligible = dev-split, hosted in the public mirror, non-NC license.
    Everything else (fetch-from-source NC corpora, quarantined sets,
    local-only gold standards) stays out of the open contribution lane.
    """
    out = []
    for ds in registry.get("datasets", []):
        if ds.get("access") != "local":
            continue
        if ds.get("segment") != "development":
            continue
        license_str = (ds.get("license") or "").upper()
        if "NC" in license_str:  # non-commercial lane — not queued
            continue
        if ds.get("quarantine"):
            continue
        path = ds.get("path")
        if not path:
            continue
        out.append(ds)
    return out


def target_lang_name(iso3: str) -> str | None:
    card = CARDS_DIR / f"{iso3}.json"
    if not card.exists():
        return None
    try:
        return json.loads(card.read_text(encoding="utf-8")).get("name")
    except json.JSONDecodeError:
        return None


def fetch_coverage() -> tuple[set[tuple[str, str, str]], int]:
    """Fetch (dataset_token, model_short, condition) combos already on the
    public leaderboard. Returns (combos, row_count).

    dataset_token is matched loosely: both the registry id and the corpus
    file stem are tokens, because publish.py resolves dataset_id from
    either an explicit id or the corpus file basename.
    """
    url = (
        f"{SUPABASE_URL}/rest/v1/run_cards"
        "?select=dataset_id,model_slug,condition"
        "&trust=neq.disqualified&limit=10000"
    )
    req = urllib.request.Request(
        url,
        headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        rows = json.loads(resp.read())
    combos = set()
    for row in rows:
        ds = (row.get("dataset_id") or "").strip().lower()
        model = model_short(row.get("model_slug") or "")
        cond = (row.get("condition") or "").strip().lower()
        # Coaching runs publish condition labels like "coached-v1" or a
        # method-card class like "coached-llm" — normalize to "coached".
        if "coach" in cond:
            cond = "coached"
        combos.add((ds, model, cond))
    return combos, len(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default=str(DEFAULT_OUTPUT))
    ap.add_argument(
        "--offline",
        action="store_true",
        help="Skip the leaderboard coverage query (treat everything as open)",
    )
    args = ap.parse_args()

    registry = load_json(REGISTRY)
    manifest = load_json(MANIFEST)

    corpora = queue_corpora(registry)
    lineup = [m["slug"] for m in manifest.get("lineup", [])]
    if not lineup:
        print("No validated model lineup in sweep manifest — aborting.")
        return 1

    # ---- Cost model from the sweep manifest -----------------------------
    # Per-(corpus_stem, model) observed costs; per-model avg cost/entry.
    size_by_stem = {
        Path(ds["path"]).stem: ds.get("size") for ds in corpora
    }
    observed: dict[tuple[str, str], float] = {}
    per_entry_samples: dict[str, list[float]] = {}
    sweep_total = 0.0
    sweep_ok = 0
    for run in manifest.get("runs", []):
        sweep_total += run.get("cost", 0.0)
        if not run.get("ok"):
            continue
        sweep_ok += 1
        stem, model, cost = run["corpus"], run["model"], run.get("cost", 0.0)
        observed[(stem, model)] = cost
        size = size_by_stem.get(stem)
        if size and cost > 0:
            per_entry_samples.setdefault(model, []).append(cost / size)
    avg_per_entry = {
        m: sum(v) / len(v) for m, v in per_entry_samples.items() if v
    }

    # ---- Coverage from the public leaderboard ---------------------------
    coverage: set[tuple[str, str, str]] = set()
    leaderboard_rows = 0
    coverage_note = "offline (coverage query skipped — all combos listed)"
    if not args.offline:
        try:
            coverage, leaderboard_rows = fetch_coverage()
            coverage_note = (
                f"queried public run_cards (read-only) at generation time; "
                f"{leaderboard_rows} rows on the board"
            )
        except Exception as exc:  # noqa: BLE001 — degrade to full queue
            coverage_note = f"coverage query failed ({exc}); all combos listed"

    # ---- Build items -----------------------------------------------------
    # Priority: uncovered language pairs first, lower-resource first
    # (corpus size ascending is the proxy: a thinner public corpus pool
    # generally means a lower-resourced pair), naive before coached,
    # then cheapest model first so the entry cost stays low.
    covered_pairs = set()
    for ds in corpora:
        stem = Path(ds["path"]).stem
        tokens = {stem.lower(), ds["id"].lower()}
        for token, _m, _c in coverage:
            if token in tokens:
                covered_pairs.add(ds["id"])

    items = []
    skipped_no_card = []
    for ds in sorted(corpora, key=lambda d: (d.get("size") or 0, d["id"])):
        stem = Path(ds["path"]).stem
        pair = ds["language_pair"]
        src, tgt = pair["source"], pair["target"]
        lang = target_lang_name(tgt)
        if not lang:
            skipped_no_card.append(ds["id"])
            continue
        corpus_url = f"{MIRROR_RAW}/datasets/{ds['path']}"
        for cond in CONDITIONS:
            for slug in lineup:
                ds_tokens = {stem.lower(), ds["id"].lower()}
                ms = model_short(slug)
                if any((t, ms, cond) in coverage for t in ds_tokens):
                    continue
                cost = observed.get((stem, slug))
                if cost is not None and cond == "naive":
                    est, basis = round(cost, 4), "observed (baseline sweep manifest)"
                elif avg_per_entry.get(slug) and ds.get("size"):
                    est = round(avg_per_entry[slug] * ds["size"], 4)
                    basis = (
                        "extrapolated: sweep avg cost/entry for this model "
                        "x corpus entry count (naive condition; coached runs "
                        "add system-prompt tokens, expect slightly more)"
                    )
                else:
                    est, basis = None, "no sweep data for this model"
                run_cmd = (
                    f"curl -fsSLO {corpus_url} && "
                    f"mt-eval run --corpus {stem}.json "
                    f'--model {slug} --target-lang "{lang}"'
                )
                if cond == "coached":
                    run_cmd += " --coaching-file YOUR_COACHING.txt"
                items.append(
                    {
                        "id": f"{stem}__{slug.replace('/', '_')}__{cond}",
                        "language_pair": f"{src}>{tgt}",
                        "target_language": lang,
                        "corpus_id": ds["id"],
                        "corpus_file": f"datasets/{ds['path']}",
                        "corpus_url": corpus_url,
                        "corpus_license": ds.get("license"),
                        "entry_count": ds.get("size"),
                        "model": slug,
                        "condition": cond,
                        "est_cost_usd": est,
                        "est_basis": basis,
                        "pair_covered_on_leaderboard": ds["id"] in covered_pairs,
                        "run_command": run_cmd,
                    }
                )

    def sort_key(it):
        return (
            it["pair_covered_on_leaderboard"],          # empty squares first
            it["entry_count"] or 10**9,                  # low-resource proxy
            it["condition"] != "naive",                  # naive before coached
            it["est_cost_usd"] if it["est_cost_usd"] is not None else 10**9,
            it["id"],
        )

    items.sort(key=sort_key)
    for rank, it in enumerate(items, start=1):
        it["priority"] = rank
        # keep priority near the front of the object for readability
        it_reordered = {"priority": it["priority"], **{k: v for k, v in it.items() if k != "priority"}}
        items[rank - 1] = it_reordered

    queue = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "generator": "arena/scripts/generate_sweep_queue.py",
            "open_items": len(items),
            "corpora": len({it["corpus_id"] for it in items}),
            "models": lineup,
            "conditions": list(CONDITIONS),
            "coverage_source": coverage_note,
            "cost_basis": (
                "Cost estimates come from the 2026-06 baseline sweep manifest "
                f"(arena/eval/logs/sweep_manifest.json: {sweep_ok} successful "
                f"runs, ${sweep_total:.2f} total). 'observed' = exact cost of "
                "the same corpus x model naive run; 'extrapolated' = that "
                "model's sweep-average cost per entry x corpus entry count. "
                "Your cost varies with provider pricing at run time."
            ),
            "how_to_run": (
                "Install: curl -fsSL champollion.dev/harness | bash ; set "
                "OPENROUTER_API_KEY; then paste any item's run_command. "
                "Coached items: write your own coaching file first — see "
                "https://mtevalarena.org/docs/tutorials/coached-llm-prompting"
            ),
            "how_to_publish": (
                "mt-eval publish <report.json> — sign in via OAuth when "
                "prompted. Community submissions land at the "
                "'self-benchmarked' trust tier with your name attached; "
                "that is the trust model working as designed."
            ),
            "dedupe_note": (
                "No claim-locking: pick any open item. Run-card fingerprints "
                "(SHA-256 of dataset hash + model + condition + system prompt) "
                "deduplicate identical runs on publish, and independent "
                "replications of the same item are scientifically useful, "
                "not wasted."
            ),
            "license_note": (
                "Queued corpora are CC-BY family (Tatoeba-derived) and "
                "carry do_not_train: true — they are evaluation sets, not "
                "training data. NC-licensed and quarantined corpora are "
                "excluded from this queue."
            ),
        },
        "items": items,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(queue, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"queue: {len(items)} open items -> {out}")
    print(f"  corpora: {queue['metadata']['corpora']}  models: {len(lineup)}  conditions: {CONDITIONS}")
    print(f"  coverage: {coverage_note}")
    if skipped_no_card:
        print(f"  skipped (no language card name): {', '.join(skipped_no_card)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
