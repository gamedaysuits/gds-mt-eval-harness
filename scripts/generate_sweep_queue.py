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

Priority model (expected-chain-value v2)
----------------------------------------
Normative definition, philosophy, defaults, and citations live in the
public spec — arena/website/docs/specifications/queue-construction.md
(https://mtevalarena.org/docs/specifications/queue-construction). The
implementation here mirrors it exactly; a summary:

The mission is "every language into every language by measured
individual pair chains". The benchmark's value therefore lives in its
*quality-weighted graph*: each measured language pair carries an edge
strength s(e) = best published corpus-level chrF++ / 100, an estimated
chain between two languages composes multiplicatively along a path
with a per-junction discount λ (pivoting loses fidelity: Utiyama &
Isahara 2007; Wu & Wang 2007; Fan et al. 2021), and the mesh objective
is the quality-weighted global efficiency

    Φ = mean over ordered language pairs (u,v) of Q(u,v),
    Q(u,v) = max over paths P of  λ^(|P|-1) · Π_{e in P} s(e)

(the Latora–Marchiori 2001 efficiency construction with the 1/d kernel
replaced by multiplicative chain fidelity; v1's unweighted 1/d ranking
was the binary ancestor of this). Each open queue item — one
(corpus, model, condition) run nobody has published — is valued by the
mesh improvement it is expected to buy per dollar:

    ECV(item) = ΔΦ(item) / max(est_cost, COST_FLOOR)
    ΔΦ = Φ after raising the item's pair edge to max(s(e), ŝ) − Φ now

where ŝ is a transparent prediction with an optimism bonus
(UCB1-shaped, Auer et al. 2002): pair prior (hierarchical back-off:
pair mean → target-language mean → source-language mean → global mean
→ 0.5) + model offset + condition offset + κ·sqrt(2·ln(1+N)/(1+n)).
ΔΦ uses the exact single-edge closed form
Q'(u,v) = max(Q(u,v), E(u,a)·s'·E(b,v), E(u,b)·s'·E(a,v)) with
E(x,y) = λ·Q(x,y) for x≠y and E(x,x) = 1. Ranking by marginal value
per cost is the greedy rule for budgeted coverage-style maximization
(Nemhauser et al. 1978; Khuller, Moss & Naor 1999) — see the spec for
why and for the honesty limits of each ingredient.

Ties break: naive before coached, cheaper first, then item id.
Unmeasured pairs dominate naturally (s(e)=0 makes ΔΦ large) — there is
no longer a hard "uncovered first" gate; a covered pair outranks an
uncovered one only when the formula says the upgrade genuinely buys
more mesh per dollar. Every item exposes its full formula breakdown
(edge_strength, pair_prior, model_offset, condition_offset,
exploration_bonus, predicted_strength, expected_mesh_gain,
ecv_per_usd) so any ranking can be re-derived by hand.

With ``--offline`` (or a failed query) there are no results: all edge
strengths are 0, predictions collapse to the 0.5 prior, and the
ranking degrades to structural chain value per dollar — v1 behavior.
The legacy v1 field ``chaining_gain`` (binary-efficiency gain) is kept
on every item for continuity and parity testing.

No claim-locking by design: run-card fingerprints make duplicate runs
harmless (identical fingerprints dedupe on publish; non-identical
duplicates are legitimate replications). "Pick any open item" is correct.

Usage:
  python3 scripts/generate_sweep_queue.py [--output ../cli/website/static/queue.json]
      [--offline]        # skip the leaderboard query (structural ranking)
      [--lam 0.9]        # chain junction discount λ
      [--kappa 0.05]     # exploration bonus scale κ
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

# ---- Expected-chain-value v2 parameters -----------------------------------
# Normative home: arena/website/docs/specifications/queue-construction.md §4.
# Change them there first; the queue metadata echoes the values used.

#: Chain junction discount λ: an estimated h-hop chain is worth
#: λ^(h-1)·Π s(e). Direct measurement always beats a product-equal
#: estimated chain because pivoting loses fidelity beyond what edge
#: scores compose to (Utiyama & Isahara 2007; Wu & Wang 2007; Fan et
#: al. 2021 measure direct-vs-pivot gaps; the ~10% per-junction haircut
#: is our calibration choice, revisited as chain triangles get measured).
LAMBDA = 0.9

#: Exploration bonus scale κ, in strength units (chrF/100). 0.05 = the
#: ~5-chrF noise floor below which differences are noise on n<100
#: corpora (fair-scoring policy §5 / corpus-design §6.3) — optimism
#: never exceeds what the measurement could distinguish anyway, scaled
#: by the UCB1 schedule (Auer, Cesa-Bianchi & Fischer 2002).
KAPPA = 0.05

#: Predictions are capped here — no estimated edge may claim
#: near-perfect fidelity it hasn't demonstrated.
S_CAP = 0.95

#: Uninformed pair prior when there are no results at all (observed
#: global mean is preferred whenever any result exists; 429 live runs
#: averaged ≈ 0.54 at v2 ship time).
S0_FALLBACK = 0.5

#: Floor for the cost denominator (USD) — keeps near-free runs from
#: claiming unbounded value per dollar.
COST_FLOOR = 0.01


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


#: Rows per page when reading the leaderboard. Supabase/PostgREST caps
#: single responses (commonly at 1,000 rows) regardless of the limit
#: parameter, so the board MUST be read in pages — a single capped GET
#: would silently rank the queue on a truncated scoreboard once the
#: board outgrows the cap.
FETCH_PAGE_SIZE = 1000


def _fetch_run_rows(page_size: int = FETCH_PAGE_SIZE) -> list[dict]:
    """Read the ENTIRE leaderboard, page by page.

    Pages are ordered by the primary key so pagination is stable while
    rows are being inserted concurrently (an unordered offset walk can
    skip or duplicate rows between pages).
    """
    rows: list[dict] = []
    offset = 0
    while True:
        url = (
            f"{SUPABASE_URL}/rest/v1/run_cards"
            "?select=dataset_id,model_slug,condition,chrf_plus_plus,submitted_at"
            "&trust=neq.disqualified&order=id.asc"
            f"&limit={page_size}&offset={offset}"
        )
        req = urllib.request.Request(
            url,
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            page = json.loads(resp.read())
        rows.extend(page)
        if len(page) < page_size:
            return rows
        offset += page_size


def fetch_results() -> tuple[set[tuple[str, str, str]], list[dict]]:
    """Fetch ALL published runs: coverage combos + scored result rows.

    Returns (combos, results):
      combos  — (dataset_token, model_short, condition) already on the
                board (dataset_token matched loosely against registry id
                and corpus file stem, because publish.py resolves
                dataset_id from either).
      results — [{token, model, condition, strength}] for rows carrying
                a corpus-level chrF++ (the canonical published number,
                fair-scoring policy §4); strength = chrf/100 ∈ [0,1].

    The whole board is paged in (see _fetch_run_rows) — the formula's
    contract is "every published, non-disqualified run is evidence",
    at any board size.
    """
    rows = _fetch_run_rows()
    combos = set()
    results = []
    for row in rows:
        ds = (row.get("dataset_id") or "").strip().lower()
        model = model_short(row.get("model_slug") or "")
        cond = (row.get("condition") or "").strip().lower()
        # Coaching runs publish condition labels like "coached-v1" or a
        # method-card class like "coached-llm" — normalize to "coached".
        if "coach" in cond:
            cond = "coached"
        combos.add((ds, model, cond))
        chrf = row.get("chrf_plus_plus")
        if chrf is not None and 0 <= chrf <= 100:
            results.append({
                "token": ds,
                "model": model,
                "condition": cond,
                "strength": chrf / 100.0,
                "submitted_at": row.get("submitted_at"),
            })
    return combos, results


# ---------------------------------------------------------------------------
# Expected-chain-value v2 — evidence, chain matrix, marginal gain, prediction
# (normative spec: arena/website/docs/specifications/queue-construction.md)
# ---------------------------------------------------------------------------

def build_evidence(datasets: list[dict], results: list[dict]) -> dict:
    """Aggregate published results into the quantities the formula needs.

    ``datasets`` should be the FULL registry list, not just
    queue-eligible corpora: results published on NC or restricted
    corpora (e.g. the EdTeKLA eng→crk runs) are still legitimate
    measurements of their language pair. Eligibility gates what the
    queue can ask contributors to run — never what the mesh is allowed
    to know.

    Returns a dict with:
      edge_strength   {frozenset pair: max strength}      — s(e)
      pair_scores     {frozenset pair: [strengths]}       — back-off lvl 1
      target_scores   {lang: [strengths]}                 — back-off lvl 2
      source_scores   {lang: [strengths]}                 — back-off lvl 3
      all_scores      [strengths]                         — back-off lvl 4
      cell_counts     {(pair, model): n}                  — bonus n
      model_deltas    {model: [s − pair-mean-of-others]}  — β̂ inputs
      cond_deltas_pair    {pair: [coached − naive, same (pair, model)]}
      cond_deltas_target  {target lang: [same deltas]}
      n_results       int
    """
    token_pair: dict[str, tuple[str, str]] = {}
    for ds in datasets:
        lp = ds.get("language_pair")
        if not lp:
            continue
        pair = (lp["source"], lp["target"])
        token_pair[ds["id"].lower()] = pair
        if ds.get("path"):
            token_pair[Path(ds["path"]).stem.lower()] = pair

    pair_scores: dict[frozenset, list[float]] = {}
    target_scores: dict[str, list[float]] = {}
    source_scores: dict[str, list[float]] = {}
    all_scores: list[float] = []
    cell_counts: dict[tuple[frozenset, str], int] = {}
    by_pair_model: dict[tuple[frozenset, str], list[float]] = {}
    by_pair_model_cond: dict[tuple[frozenset, str, str], list[float]] = {}

    for r in results:
        pair = token_pair.get(r["token"])
        if pair is None:
            continue  # row predates the registry or uses a legacy id
        src, tgt = pair
        e = frozenset(pair)
        s = r["strength"]
        pair_scores.setdefault(e, []).append(s)
        target_scores.setdefault(tgt, []).append(s)
        source_scores.setdefault(src, []).append(s)
        all_scores.append(s)
        cell = (e, r["model"])
        cell_counts[cell] = cell_counts.get(cell, 0) + 1
        by_pair_model.setdefault(cell, []).append(s)
        by_pair_model_cond.setdefault(
            (e, r["model"], r["condition"]), []
        ).append(s)

    # Model offsets: how a model does relative to the other models on the
    # same pair, averaged over pairs where a comparison exists (a plain
    # two-way main-effects decomposition — no opaque fitting).
    model_deltas: dict[str, list[float]] = {}
    pairs_models: dict[frozenset, dict[str, float]] = {}
    for (e, m), scores in by_pair_model.items():
        pairs_models.setdefault(e, {})[m] = sum(scores) / len(scores)
    for e, per_model in pairs_models.items():
        if len(per_model) < 2:
            continue
        for m, mean_m in per_model.items():
            others = [v for mm, v in per_model.items() if mm != m]
            model_deltas.setdefault(m, []).append(
                mean_m - sum(others) / len(others)
            )

    # Condition offset: coached − naive on the same (pair, model).
    # Kept at pair/target-language level only — coaching gains do NOT
    # generalize globally (the large eng→crk FST-coached uplift says
    # nothing about coaching Faroese), and on unscored pairs the
    # baseline-first convention should hold.
    cond_deltas_pair: dict[frozenset, list[float]] = {}
    cond_deltas_target: dict[str, list[float]] = {}
    pair_target = {}
    for ds in datasets:
        lp = ds.get("language_pair")
        if lp:
            pair_target[frozenset((lp["source"], lp["target"]))] = lp["target"]
    for (e, m, cond), scores in by_pair_model_cond.items():
        if cond != "coached":
            continue
        naive = by_pair_model_cond.get((e, m, "naive"))
        if naive:
            delta = sum(scores) / len(scores) - sum(naive) / len(naive)
            cond_deltas_pair.setdefault(e, []).append(delta)
            tgt = pair_target.get(e)
            if tgt:
                cond_deltas_target.setdefault(tgt, []).append(delta)

    return {
        "edge_strength": {e: max(v) for e, v in pair_scores.items()},
        "pair_scores": pair_scores,
        "target_scores": target_scores,
        "source_scores": source_scores,
        "all_scores": all_scores,
        "cell_counts": cell_counts,
        "model_deltas": model_deltas,
        "cond_deltas_pair": cond_deltas_pair,
        "cond_deltas_target": cond_deltas_target,
        "n_results": len(all_scores),
    }


def build_chain_matrix(
    nodes: list[str],
    edge_strength: dict[frozenset, float],
    lam: float = LAMBDA,
) -> dict[str, dict[str, float]]:
    """All-pairs best-chain strengths Q(u,v) = max_P λ^(|P|-1)·Π s(e).

    Computed exactly as shortest paths under w(e) = −ln(λ·s(e)) ≥ 0
    (Dijkstra), then Q = exp(−d)/λ for u≠v and Q(u,u) = 1. λ·s ≤ 1
    keeps weights non-negative, so Dijkstra applies.
    """
    import heapq
    import math

    adj: dict[str, list[tuple[str, float]]] = {u: [] for u in nodes}
    for e, s in edge_strength.items():
        if s <= 0:
            continue
        pair = tuple(e)
        if len(pair) != 2:
            continue
        a, b = pair
        if a in adj and b in adj:
            w = -math.log(lam * min(s, 1.0))
            adj[a].append((b, w))
            adj[b].append((a, w))

    Q: dict[str, dict[str, float]] = {}
    for src in nodes:
        dist = {src: 0.0}
        heap = [(0.0, src)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist.get(u, float("inf")):
                continue
            for v, w in adj[u]:
                nd = d + w
                if nd < dist.get(v, float("inf")) - 1e-15:
                    dist[v] = nd
                    heapq.heappush(heap, (nd, v))
        row = {}
        for v in nodes:
            if v == src:
                row[v] = 1.0
            elif v in dist:
                row[v] = math.exp(-dist[v]) / lam
            else:
                row[v] = 0.0
        Q[src] = row
    return Q


def single_edge_gain(
    nodes: list[str],
    Q: dict[str, dict[str, float]],
    a: str,
    b: str,
    s_new: float,
    lam: float = LAMBDA,
) -> float:
    """Exact ΔΦ from raising edge (a,b) to strength s_new.

    A best chain in the upgraded graph either ignores the new edge or
    uses it exactly once (multiplicative weights ≤ 1 make repeat use
    dominated), so:

        Q'(u,v) = max(Q(u,v), E(u,a)·s_new·E(b,v), E(u,b)·s_new·E(a,v))

    with E(x,y) = λ·Q(x,y) for x≠y (a junction is crossed to continue
    the chain) and E(x,x) = 1 (the chain starts/ends at the new edge).
    ΔΦ is the mean increase over ordered pairs.
    """
    if s_new <= 0 or a not in Q or b not in Q:
        return 0.0
    n = len(nodes)
    if n < 2:
        return 0.0

    def E(x: str, y: str) -> float:
        return 1.0 if x == y else lam * Q[x][y]

    total = 0.0
    for u in nodes:
        Eua, Eub = E(u, a), E(u, b)
        Qu = Q[u]
        for v in nodes:
            if u == v:
                continue
            cand = s_new * max(Eua * E(b, v), Eub * E(a, v))
            cur = Qu[v]
            if cand > cur:
                total += cand - cur
    return total / (n * (n - 1))


def predict_strength(
    pair: tuple[str, str],
    model: str,
    condition: str,
    evidence: dict,
    *,
    kappa: float = KAPPA,
) -> dict:
    """Transparent score prediction for an unrun (pair, model, condition).

    ŝ = clip(pair_prior + model_offset + condition_offset + bonus,
             0, S_CAP), with every component returned for display.

    pair_prior: hierarchical back-off — mean of published strengths on
    this pair, else on this target language, else on this source
    language, else globally, else S0_FALLBACK. model_offset /
    condition_offset: mean observed deltas (0 without evidence). bonus:
    κ·sqrt(2·ln(1+N)/(1+n)) — the UCB1 schedule (Auer et al. 2002) with
    n = published runs on this (pair, model); we borrow the optimism
    schedule, not the regret theorem.
    """
    import math

    e = frozenset(pair)
    src, tgt = pair

    def _mean(xs: list[float] | None) -> float | None:
        return sum(xs) / len(xs) if xs else None

    for level, value in (
        ("pair", _mean(evidence["pair_scores"].get(e))),
        ("target-language", _mean(evidence["target_scores"].get(tgt))),
        ("source-language", _mean(evidence["source_scores"].get(src))),
        ("global", _mean(evidence["all_scores"])),
        ("default", S0_FALLBACK),
    ):
        if value is not None:
            prior, prior_basis = value, level
            break

    deltas = evidence["model_deltas"].get(model)
    model_offset = sum(deltas) / len(deltas) if deltas else 0.0
    cond_offset = 0.0
    if condition == "coached":
        local = (
            evidence["cond_deltas_pair"].get(e)
            or evidence["cond_deltas_target"].get(tgt)
        )
        if local:
            cond_offset = sum(local) / len(local)

    n_cell = evidence["cell_counts"].get((e, model), 0)
    n_total = evidence["n_results"]
    bonus = kappa * math.sqrt(
        2.0 * math.log(1.0 + n_total) / (1.0 + n_cell)
    ) if n_total > 0 else 0.0

    predicted = max(0.0, min(
        S_CAP, prior + model_offset + cond_offset + bonus,
    ))
    return {
        "pair_prior": round(prior, 4),
        "prior_basis": prior_basis,
        "model_offset": round(model_offset, 4),
        "condition_offset": round(cond_offset, 4),
        "exploration_bonus": round(bonus, 4),
        "predicted_strength": round(predicted, 4),
    }


#: chrF++ display bands for the public mesh visualization (champollion.dev/mesh).
#: Band edges in chrF++ points: <40 red, 40–55 orange, 55–70 yellow,
#: 70–80 green, 80–90 blue, 90+ white.
MESH_BANDS = [40, 55, 70, 80, 90]


def build_mesh_snapshot(
    corpora: list[dict],
    evidence: dict,
    results: list[dict],
    registry: dict,
    *,
    phi_current: float,
) -> dict:
    """Assemble the mesh visualization artifact (static/mesh.json).

    The artifact answers "how did the mesh get filled, and how strong is
    it?": one node per language (with language-card coordinates for the
    geographic layout), one edge per registered language pair, and for
    measured edges the full time-ordered run history so the page can
    replay growth. Edge ``size`` is the largest registered corpus on the
    pair (the visualization maps it to stroke thickness).
    """
    # token → (pair, size) over the full registry; pair-level max size.
    token_pair: dict[str, tuple[str, str]] = {}
    pair_size: dict[frozenset, int] = {}
    pair_status: dict[frozenset, str] = {}
    for ds in registry.get("datasets", []):
        lp = ds.get("language_pair")
        if not lp:
            continue
        pair = (lp["source"], lp["target"])
        e = frozenset(pair)
        token_pair[ds["id"].lower()] = pair
        if ds.get("path"):
            token_pair[Path(ds["path"]).stem.lower()] = pair
        pair_size[e] = max(pair_size.get(e, 0), ds.get("size") or 0)
        pair_status.setdefault(e, "registered")

    # Per-edge run history, time-ordered.
    edge_runs: dict[frozenset, list[tuple[str, float]]] = {}
    for r in results:
        pair = token_pair.get(r["token"])
        if pair is None or not r.get("submitted_at"):
            continue
        e = frozenset(pair)
        edge_runs.setdefault(e, []).append(
            (r["submitted_at"], round(r["strength"] * 100, 2))
        )
    for runs in edge_runs.values():
        runs.sort()

    # Nodes: every language in any registered pair, with card coordinates.
    langs = sorted({lang for e in pair_size for lang in e})
    nodes = []
    for lang in langs:
        card_path = CARDS_DIR / f"{lang}.json"
        name, lat, lng, family = lang, None, None, None
        if card_path.exists():
            try:
                card = json.loads(card_path.read_text(encoding="utf-8"))
                name = card.get("name") or lang
                coords = card.get("coordinates") or {}
                lat, lng = coords.get("lat"), coords.get("lng")
                family = (card.get("classification") or {}).get("family")
            except json.JSONDecodeError:
                pass
        nodes.append({
            "id": lang, "name": name, "lat": lat, "lng": lng,
            "family": family,
        })

    edges = []
    for e in sorted(pair_size, key=lambda x: tuple(sorted(x))):
        a, b = sorted(e)
        runs = edge_runs.get(e, [])
        edges.append({
            "a": a,
            "b": b,
            "size": pair_size[e],
            "status": "measured" if runs else "registered",
            "best_chrf": max((c for _t, c in runs), default=None),
            "runs": [[t, c] for t, c in runs],
        })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "arena/scripts/generate_sweep_queue.py",
        "formula_version": "ecv-v2",
        "phi_current": round(phi_current, 6),
        "bands_chrf": MESH_BANDS,
        "band_note": (
            "chrF++ display bands: <40 red, 40-55 orange, 55-70 yellow, "
            "70-80 green, 80-90 blue, 90+ white. Edge thickness scales "
            "with the largest registered corpus on the pair. Development-"
            "set readings — see /docs (scores are baselines, not "
            "capability claims)."
        ),
        "nodes": nodes,
        "edges": edges,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default=str(DEFAULT_OUTPUT))
    ap.add_argument(
        "--mesh-output",
        default=None,
        help="Where to write the mesh visualization artifact "
             "(default: mesh.json next to --output).",
    )
    ap.add_argument(
        "--offline",
        action="store_true",
        help="Skip the leaderboard coverage query (treat everything as open)",
    )
    ap.add_argument(
        "--lam", type=float, default=LAMBDA,
        help="Chain junction discount λ (spec §4; default %(default)s)",
    )
    ap.add_argument(
        "--kappa", type=float, default=KAPPA,
        help="Exploration bonus scale κ (spec §4; default %(default)s)",
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

    # ---- Results from the public leaderboard -----------------------------
    coverage: set[tuple[str, str, str]] = set()
    results: list[dict] = []
    coverage_note = "offline (leaderboard query skipped — structural ranking)"
    if not args.offline:
        try:
            coverage, results = fetch_results()
            coverage_note = (
                f"queried public run_cards (read-only) at generation time; "
                f"{len(results)} scored runs on the board"
            )
        except Exception as exc:  # noqa: BLE001 — degrade to full queue
            coverage_note = f"leaderboard query failed ({exc}); structural ranking"

    # ---- Build items: expected-chain-value v2 ----------------------------
    # (normative spec: arena/website/docs/specifications/queue-construction.md)
    covered_pairs = set()
    for ds in corpora:
        stem = Path(ds["path"]).stem
        tokens = {stem.lower(), ds["id"].lower()}
        for token, _m, _c in coverage:
            if token in tokens:
                covered_pairs.add(ds["id"])

    gains = chaining_gains(corpora, covered_pairs)  # legacy v1 field

    # Evidence maps results through the FULL registry (NC/restricted
    # corpora produce knowledge even though they are not queueable).
    evidence = build_evidence(registry.get("datasets", []), results)
    # Graph nodes: languages the queue can act on, plus languages with
    # published evidence — their chain values respond to queue items
    # even when no item targets their own edges directly.
    nodes = sorted(
        {
            lang
            for ds in corpora
            for lang in (ds["language_pair"]["source"],
                         ds["language_pair"]["target"])
        }
        | {lang for e in evidence["edge_strength"] for lang in e}
    )
    Q = build_chain_matrix(nodes, evidence["edge_strength"], lam=args.lam)
    n_nodes = len(nodes)
    phi_now = (
        sum(Q[u][v] for u in nodes for v in nodes if u != v)
        / (n_nodes * (n_nodes - 1))
    ) if n_nodes > 1 else 0.0
    # ΔΦ depends only on (edge, upgraded strength) — memoize across the
    # per-model/per-condition item loop.
    gain_cache: dict[tuple[frozenset, float], float] = {}

    # Cost fallback chain for the ECV denominator: observed/extrapolated
    # estimate → global median estimate → COST_FLOOR.
    all_per_entry = [c for v in per_entry_samples.values() for c in v]
    median_per_entry = (
        sorted(all_per_entry)[len(all_per_entry) // 2]
        if all_per_entry else None
    )

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
                    # Use the registry id, not a repo-relative path: the
                    # documented contributor flow runs from a scratch dir,
                    # where 'datasets/...' resolves to nothing (verified
                    # 2026-06-12). The harness resolves ids via the
                    # registry -> local file -> fetch-from-source chain.
                    run_cmd = (
                        f"mt-eval run --corpus {ds['id']} "
                        f'--model {slug} --target-lang "{lang}" --yes'
                    )
                else:
                    # --yes also covers eval-pack auto-install (FST
                    # languages) for downloaded-file runs.
                    run_cmd = (
                        f"curl -fsSLO {corpus_url} && "
                        f"mt-eval run --corpus {stem}.json "
                        f'--model {slug} --target-lang "{lang}" --yes'
                    )
                if cond == "coached":
                    run_cmd += " --coaching-file YOUR_COACHING.txt"

                # ---- Expected-chain-value v2 (spec §3) -------------------
                edge = frozenset((src, tgt))
                s_cur = evidence["edge_strength"].get(edge, 0.0)
                pred = predict_strength(
                    (src, tgt), ms, cond, evidence, kappa=args.kappa,
                )
                s_new = max(s_cur, pred["predicted_strength"])
                cache_key = (edge, round(s_new, 6))
                if cache_key not in gain_cache:
                    gain_cache[cache_key] = single_edge_gain(
                        nodes, Q, src, tgt, s_new, lam=args.lam,
                    )
                mesh_gain = gain_cache[cache_key]
                if est is not None:
                    cost_for_value = max(est, COST_FLOOR)
                elif median_per_entry and ds.get("size"):
                    cost_for_value = max(
                        median_per_entry * ds["size"], COST_FLOOR,
                    )
                else:
                    cost_for_value = COST_FLOOR
                ecv = mesh_gain / cost_for_value

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
                    # Full formula breakdown (spec §3) — every ranking is
                    # re-derivable by hand from these fields.
                    "edge_strength": round(s_cur, 4),
                    "pair_prior": pred["pair_prior"],
                    "prior_basis": pred["prior_basis"],
                    "model_offset": pred["model_offset"],
                    "condition_offset": pred["condition_offset"],
                    "exploration_bonus": pred["exploration_bonus"],
                    "predicted_strength": pred["predicted_strength"],
                    "expected_mesh_gain": round(mesh_gain, 8),
                    "ecv_per_usd": round(ecv, 8),
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
            -it["ecv_per_usd"],                          # mesh value per $
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
                "expected-chain-value v2: items are ranked by "
                "ECV = ΔΦ / cost — the expected gain in quality-weighted "
                "mesh efficiency Φ from publishing this run, per estimated "
                "dollar. Φ averages, over all ordered language pairs, the "
                "best chain strength Q(u,v) = max over paths of "
                "λ^(hops−1)·Π(chrF++/100 per edge). Each item's "
                "predicted score is pair prior + model offset + condition "
                "offset + UCB exploration bonus, and every component is "
                "published on the item so the ranking can be re-derived "
                "by hand. Normative definition, philosophy, and citations: "
                "https://mtevalarena.org/docs/specifications/"
                "queue-construction"
            ),
            "priority_parameters": {
                "formula_version": "ecv-v2",
                "lambda_junction_discount": args.lam,
                "kappa_exploration_scale": args.kappa,
                "strength_cap": S_CAP,
                "cost_floor_usd": COST_FLOOR,
                "prior_fallback": S0_FALLBACK,
                "phi_current": round(phi_now, 6),
                "scored_runs_used": evidence["n_results"],
                "scored_edges": len(evidence["edge_strength"]),
                "languages_in_graph": n_nodes,
            },
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
