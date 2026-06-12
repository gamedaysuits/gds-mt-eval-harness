#!/usr/bin/env python3
"""Generate the public community-compute sweep queue.

Reads three sources of truth and emits ``cli/website/static/queue.json``,
the artifact behind champollion.dev/queue.json and the /contribute page:

  1. ``arena/datasets/registry.json`` — which dev-split corpora are open
     for community runs. Two kinds qualify, both requiring
     ``segment: "development"``, a redistributable license (CC-BY
     family, non-NC), and no quarantine flag:
       - ``access: "local"`` corpora hosted in the public harness
         mirror (fetched with curl in the run command);
       - ``access: "fetch-from-source"`` corpora with a
         ``source_export`` block (the Tatoeba mesh corpora) — never
         hosted by us; the harness rebuilds them locally from the
         pinned upstream export when ``mt-eval run --yes`` finds the
         corpus path missing, then verifies the registry sha256.
     NC-licensed (EdTeKLA) corpora are excluded either way — see the
     project licensing policy (NC content stays out of open
     contribution lanes).
  2. ``arena/eval/logs/sweep_manifest.json`` — the validated model lineup
     and observed per-run costs from the 2026-06-11 baseline sweep.
     Cost estimates are either the *observed* cost for that exact
     (corpus, model) pair, or an extrapolation from the model's average
     cost per entry across the sweep (``est_basis`` says which).
  3. The public leaderboard REST endpoint (read-only anon key, same as
     cli/website/src/pages/leaderboard.js) — already-covered
     (dataset, model, condition) combos are dropped from the queue.

Priority model (mesh-chaining v1)
---------------------------------
The mission is "every language into every language by measured
individual pair chains": an unbenchmarked pair is served by chaining
benchmarked edges, so a queue item's value is how much its language
pair shortens chains across the whole benchmark graph — not how big
its corpus is. Items are ranked by, in order:

  1. **Uncovered pairs first** — language pairs with no leaderboard
     coverage at all come before replications/extensions of covered
     pairs.
  2. **Chaining value** (descending) — the gain in *global efficiency*
     (mean over ordered language pairs of 1/d(u,v), 1/inf = 0) when the
     item's pair edge is added to the graph of currently covered pairs.
     Efficiency is used instead of raw average path length because it
     is well-defined on disconnected graphs: edges that join components
     — the highest-value chaining edges — rank first instead of
     dividing by infinity. Identical definition as
     ``corpora_builder.probe_tatoeba.graph_efficiency``; a parity test
     in arena/tests keeps the two in lockstep.
  3. **Corpus size** (ascending) — the low-resource-first proxy,
     demoted from primary criterion to tiebreak within equal chaining
     value.
  4. Naive before coached, then cheapest model first, then item id.

With ``--offline`` (or a failed coverage query) the covered graph is
empty, so every pair's chaining gain is the identical component-join
value and ordering degrades gracefully to the size/cost tiebreakers.

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
import os
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
# Env-overridable (MT_EVAL_SUPABASE_URL / MT_EVAL_SUPABASE_ANON_KEY) so the
# queue can be regenerated against a staging branch during end-to-end tests.
SUPABASE_URL = os.environ.get(
    "MT_EVAL_SUPABASE_URL", "https://sjdomynysdljkbemupqa.supabase.co"
)
SUPABASE_ANON_KEY = os.environ.get(
    "MT_EVAL_SUPABASE_ANON_KEY", "sb_publishable_bV6CFNFnzxhQI0wlBx2J0A_5Vm5gFBp"
)

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

    Eligible = dev-split, non-NC license, and obtainable by a
    contributor: either hosted in the public mirror (``access:
    "local"``) or rebuildable from a pinned upstream export
    (``access: "fetch-from-source"`` with a ``source_export`` block —
    the harness fetch-on-miss path). Everything else (NC corpora,
    quarantined sets, local-only gold standards) stays out of the open
    contribution lane.
    """
    out = []
    for ds in registry.get("datasets", []):
        access = ds.get("access")
        if access == "fetch-from-source":
            if not isinstance(ds.get("source_export"), dict):
                continue  # no public rebuild recipe (e.g. EdTeKLA cards)
        elif access != "local":
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


def graph_efficiency(nodes: list[str], edges: set[frozenset]) -> float:
    """Global efficiency of an undirected graph via per-node BFS.

    Mean over ordered node pairs of 1/d(u,v), with 1/inf = 0 — defined
    even on disconnected graphs. Mirror of
    ``corpora_builder.probe_tatoeba.graph_efficiency`` (kept duplicated
    so this script stays stdlib-only; parity-tested in arena/tests).
    """
    from collections import deque

    adj: dict[str, set] = {n: set() for n in nodes}
    for e in edges:
        pair = tuple(e)
        if len(pair) != 2:
            continue
        a, b = pair
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)

    n = len(nodes)
    if n < 2:
        return 0.0
    total = 0.0
    for start in nodes:
        dist = {start: 0}
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1
                    queue.append(v)
        total += sum(1.0 / d for node, d in dist.items() if node != start)
    return total / (n * (n - 1))


def chaining_gains(
    corpora: list[dict],
    covered_pair_ids: set,
) -> dict[str, float]:
    """Chaining value per corpus id against the covered-pair graph.

    Nodes are every language appearing in an eligible corpus; edges are
    the pairs of corpora already covered on the leaderboard. A corpus's
    chaining value is the global-efficiency gain from adding its pair
    edge — 0.0 when the edge is already covered (replications add no
    new chaining).
    """
    nodes = sorted({
        lang
        for ds in corpora
        for lang in (ds["language_pair"]["source"],
                     ds["language_pair"]["target"])
    })
    covered_edges = {
        frozenset((ds["language_pair"]["source"],
                   ds["language_pair"]["target"]))
        for ds in corpora
        if ds["id"] in covered_pair_ids
    }
    baseline = graph_efficiency(nodes, covered_edges)

    gains: dict[str, float] = {}
    for ds in corpora:
        edge = frozenset((ds["language_pair"]["source"],
                          ds["language_pair"]["target"]))
        if edge in covered_edges:
            gains[ds["id"]] = 0.0
        else:
            gains[ds["id"]] = (
                graph_efficiency(nodes, covered_edges | {edge}) - baseline
            )
    return gains


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
    # Priority: mesh-chaining v1 (see module docstring) — uncovered
    # language pairs first, then chaining value (global-efficiency gain
    # on the covered-pair graph) descending, with corpus size demoted to
    # a low-resource tiebreaker, naive before coached, cheapest model
    # first so the entry cost stays low.
    covered_pairs = set()
    for ds in corpora:
        stem = Path(ds["path"]).stem
        tokens = {stem.lower(), ds["id"].lower()}
        for token, _m, _c in coverage:
            if token in tokens:
                covered_pairs.add(ds["id"])

    gains = chaining_gains(corpora, covered_pairs)

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
        is_fetch = ds.get("access") == "fetch-from-source"
        corpus_url = (
            None if is_fetch else f"{MIRROR_RAW}/datasets/{ds['path']}"
        )
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
                if is_fetch:
                    # Not hosted by us: run from an arena checkout and the
                    # harness rebuilds the corpus from the pinned upstream
                    # export on first use (--yes accepts the CC-BY terms),
                    # verifying the registry sha256.
                    run_cmd = (
                        f"mt-eval run --corpus datasets/{ds['path']} "
                        f'--model {slug} --target-lang "{lang}" --yes'
                    )
                else:
                    run_cmd = (
                        f"curl -fsSLO {corpus_url} && "
                        f"mt-eval run --corpus {stem}.json "
                        f'--model {slug} --target-lang "{lang}"'
                    )
                if cond == "coached":
                    run_cmd += " --coaching-file YOUR_COACHING.txt"
                item = {
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
                    "chaining_gain": round(gains.get(ds["id"], 0.0), 6),
                    "run_command": run_cmd,
                }
                if is_fetch:
                    item["corpus_fetch"] = (
                        "fetch-from-source: corpus is not hosted in the "
                        "mirror; mt-eval builds it locally from the pinned "
                        "Tatoeba Challenge export and verifies the registry "
                        "sha256 (run from an arena checkout)"
                    )
                    item["source_export_url"] = (
                        ds.get("source_export") or {}
                    ).get("url")
                items.append(item)

    def sort_key(it):
        return (
            it["pair_covered_on_leaderboard"],          # empty squares first
            -it["chaining_gain"],                        # mesh value first
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
            "priority_model": (
                "mesh-chaining v1: uncovered pairs first, then chaining "
                "value (global-efficiency gain of the item's language-pair "
                "edge on the covered-pair graph) descending, then corpus "
                "size ascending (low-resource tiebreak), naive before "
                "coached, cheapest model first. Chaining value reflects the "
                "mission: every language into every language by measured "
                "pair chains — items that shorten chains between "
                "benchmarked languages outrank bigger corpora."
            ),
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
                "Items with corpus_fetch are not hosted anywhere by us: "
                "run them from your arena checkout and the harness "
                "downloads the pinned Tatoeba Challenge export (~169 MB, "
                "cached once for all pairs), rebuilds the corpus locally, "
                "and verifies its sha256 against the registry. "
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
