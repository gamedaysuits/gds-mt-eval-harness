"""Tests for scripts/generate_sweep_queue.py — mesh-chaining queue priority.

The script is stdlib-only and not a package; it is imported here via
importlib so its eligibility and graph functions can be tested directly.
Includes the parity test pinning its graph_efficiency against the
corpora-builder implementation (the two are deliberately duplicated so
the script stays dependency-free — this test is what keeps them honest).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ARENA_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ARENA_ROOT / "scripts" / "generate_sweep_queue.py"
CORPORA_BUILDER = ARENA_ROOT / "scripts" / "corpora-builder"


@pytest.fixture(scope="module")
def queue_mod():
    spec = importlib.util.spec_from_file_location(
        "generate_sweep_queue", SCRIPT,
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------

def _ds(**over):
    base = {
        "id": "tatoeba-aaa-bbb-dev",
        "access": "local",
        "segment": "development",
        "license": "CC-BY-2.0",
        "path": "curated/aaa-bbb-dev-v1.json",
        "size": 100,
        "language_pair": {"source": "aaa", "target": "bbb"},
    }
    base.update(over)
    return base


class TestQueueCorpora:
    def test_local_dev_corpus_eligible(self, queue_mod):
        assert queue_mod.queue_corpora({"datasets": [_ds()]}) != []

    def test_fetch_from_source_with_export_eligible(self, queue_mod):
        ds = _ds(access="fetch-from-source",
                 source_export={"builder": "tatoeba-challenge"})
        assert queue_mod.queue_corpora({"datasets": [ds]}) != []

    def test_fetch_from_source_without_export_excluded(self, queue_mod):
        ds = _ds(access="fetch-from-source")
        assert queue_mod.queue_corpora({"datasets": [ds]}) == []

    def test_nc_license_excluded_even_with_export(self, queue_mod):
        ds = _ds(access="fetch-from-source",
                 license="CC BY-NC-SA 4.0",
                 source_export={"builder": "edtekla"})
        assert queue_mod.queue_corpora({"datasets": [ds]}) == []

    def test_quarantined_excluded(self, queue_mod):
        assert queue_mod.queue_corpora(
            {"datasets": [_ds(quarantine=True)]}
        ) == []

    def test_non_development_excluded(self, queue_mod):
        assert queue_mod.queue_corpora(
            {"datasets": [_ds(segment=None)]}
        ) == []

    def test_local_only_excluded(self, queue_mod):
        assert queue_mod.queue_corpora(
            {"datasets": [_ds(access="local-only")]}
        ) == []


# ---------------------------------------------------------------------------
# Chaining priority
# ---------------------------------------------------------------------------

class TestChainingGains:
    def _corpora(self):
        """Hub eng-{aaa,bbb} plus isolated pair ccc-ddd.

        With eng-aaa and eng-bbb covered, the corpus closing aaa-bbb is
        a shortcut inside the main component, while ccc-ddd joins a
        disconnected component — the join must outrank the shortcut.
        """
        return [
            _ds(id="cov-a", path="curated/cov-a.json",
                language_pair={"source": "eng", "target": "aaa"}),
            _ds(id="cov-b", path="curated/cov-b.json",
                language_pair={"source": "eng", "target": "bbb"}),
            _ds(id="shortcut", path="curated/shortcut.json",
                language_pair={"source": "aaa", "target": "bbb"}),
            _ds(id="join", path="curated/join.json",
                language_pair={"source": "ccc", "target": "ddd"}),
        ]

    def test_covered_edges_gain_zero(self, queue_mod):
        gains = queue_mod.chaining_gains(self._corpora(), {"cov-a", "cov-b"})
        assert gains["cov-a"] == 0.0
        assert gains["cov-b"] == 0.0

    def test_component_join_outranks_shortcut(self, queue_mod):
        gains = queue_mod.chaining_gains(self._corpora(), {"cov-a", "cov-b"})
        assert gains["join"] > gains["shortcut"] > 0.0

    def test_offline_empty_coverage_degrades_uniformly(self, queue_mod):
        gains = queue_mod.chaining_gains(self._corpora(), set())
        # every edge is the first edge of an empty graph → equal value,
        # ordering falls through to the size/cost tiebreakers
        assert len({round(g, 12) for g in gains.values()}) == 1

    def test_exact_efficiency_value(self, queue_mod):
        nodes = ["a", "b", "c"]
        edges = {frozenset(("a", "b")), frozenset(("b", "c"))}
        assert queue_mod.graph_efficiency(nodes, edges) == pytest.approx(5 / 6)


# ---------------------------------------------------------------------------
# Expected-chain-value v2 (spec: specifications/queue-construction.md)
# ---------------------------------------------------------------------------

class TestChainMatrix:
    def test_known_path_graph(self, queue_mod):
        strengths = {frozenset(("a", "b")): 0.8, frozenset(("b", "c")): 0.5}
        Q = queue_mod.build_chain_matrix(["a", "b", "c"], strengths, lam=0.9)
        assert Q["a"]["a"] == 1.0
        assert Q["a"]["b"] == pytest.approx(0.8)
        # two hops: one junction discount — 0.9 · 0.8 · 0.5
        assert Q["a"]["c"] == pytest.approx(0.9 * 0.8 * 0.5)

    def test_disconnected_is_zero(self, queue_mod):
        Q = queue_mod.build_chain_matrix(
            ["a", "b", "c"], {frozenset(("a", "b")): 0.8}, lam=0.9,
        )
        assert Q["a"]["c"] == 0.0

    def test_best_path_wins_over_more_hops(self, queue_mod):
        # a-b-c chain (0.9·0.9·0.9 = 0.729) vs direct a-c at 0.7
        strengths = {
            frozenset(("a", "b")): 0.9,
            frozenset(("b", "c")): 0.9,
            frozenset(("a", "c")): 0.7,
        }
        Q = queue_mod.build_chain_matrix(["a", "b", "c"], strengths, lam=0.9)
        assert Q["a"]["c"] == pytest.approx(0.9 * 0.9 * 0.9)


class TestSingleEdgeGain:
    def _phi(self, queue_mod, nodes, strengths, lam):
        Q = queue_mod.build_chain_matrix(nodes, strengths, lam=lam)
        n = len(nodes)
        return sum(Q[u][v] for u in nodes for v in nodes if u != v) / (n * (n - 1))

    @pytest.mark.parametrize("upgrade,s_new", [
        (("a", "c"), 0.6),    # new edge inside a component
        (("c", "d"), 0.5),    # component join
        (("a", "b"), 0.95),   # upgrade of an existing edge
    ])
    def test_closed_form_matches_rebuild(self, queue_mod, upgrade, s_new):
        nodes = ["a", "b", "c", "d", "e"]
        strengths = {
            frozenset(("a", "b")): 0.8,
            frozenset(("b", "c")): 0.6,
            frozenset(("d", "e")): 0.7,
        }
        lam = 0.9
        Q = queue_mod.build_chain_matrix(nodes, strengths, lam=lam)
        gain = queue_mod.single_edge_gain(
            nodes, Q, upgrade[0], upgrade[1], s_new, lam=lam,
        )
        upgraded = dict(strengths)
        key = frozenset(upgrade)
        upgraded[key] = max(upgraded.get(key, 0.0), s_new)
        rebuilt = (
            self._phi(queue_mod, nodes, upgraded, lam)
            - self._phi(queue_mod, nodes, strengths, lam)
        )
        assert gain == pytest.approx(rebuilt, abs=1e-12)

    def test_junction_discount_rewards_direct_measurement(self, queue_mod):
        # Chain a-b-c composes to 0.8·0.8 = 0.64; with λ = 0.9 the
        # estimated chain is 0.576, so a measured direct 0.6 adds value.
        # With λ = 1 the chain (0.64) already beats 0.6 — no value.
        nodes = ["a", "b", "c"]
        strengths = {frozenset(("a", "b")): 0.8, frozenset(("b", "c")): 0.8}
        Q9 = queue_mod.build_chain_matrix(nodes, strengths, lam=0.9)
        Q1 = queue_mod.build_chain_matrix(nodes, strengths, lam=1.0)
        assert queue_mod.single_edge_gain(nodes, Q9, "a", "c", 0.6, lam=0.9) > 0
        assert queue_mod.single_edge_gain(nodes, Q1, "a", "c", 0.6, lam=1.0) == 0

    def test_weaker_prediction_adds_nothing(self, queue_mod):
        nodes = ["a", "b"]
        strengths = {frozenset(("a", "b")): 0.7}
        Q = queue_mod.build_chain_matrix(nodes, strengths, lam=0.9)
        assert queue_mod.single_edge_gain(nodes, Q, "a", "b", 0.5, lam=0.9) == 0.0


def _results(*rows):
    return [
        {"token": t, "model": m, "condition": c, "strength": s}
        for t, m, c, s in rows
    ]


def _datasets():
    return [
        _ds(id="ds-ab", path="curated/ab.json",
            language_pair={"source": "aaa", "target": "bbb"}),
        _ds(id="ds-ac", path="curated/ac.json",
            language_pair={"source": "aaa", "target": "ccc"}),
        # NC corpus: not queueable, but its results are still evidence.
        _ds(id="ds-nc", path="curated/nc.json",
            license="CC BY-NC-SA 4.0",
            language_pair={"source": "aaa", "target": "ddd"}),
    ]


class TestEvidence:
    def test_edge_strength_is_max_and_nc_counts(self, queue_mod):
        ev = queue_mod.build_evidence(_datasets(), _results(
            ("ds-ab", "m1", "naive", 0.5),
            ("ds-ab", "m2", "naive", 0.7),
            ("ds-nc", "m1", "naive", 0.9),
        ))
        assert ev["edge_strength"][frozenset(("aaa", "bbb"))] == 0.7
        assert ev["edge_strength"][frozenset(("aaa", "ddd"))] == 0.9
        assert ev["n_results"] == 3

    def test_model_offsets_two_way(self, queue_mod):
        # m2 beats m1 by 0.2 on the only shared pair.
        ev = queue_mod.build_evidence(_datasets(), _results(
            ("ds-ab", "m1", "naive", 0.5),
            ("ds-ab", "m2", "naive", 0.7),
        ))
        assert sum(ev["model_deltas"]["m2"]) == pytest.approx(0.2)
        assert sum(ev["model_deltas"]["m1"]) == pytest.approx(-0.2)

    def test_condition_deltas_stay_local(self, queue_mod):
        ev = queue_mod.build_evidence(_datasets(), _results(
            ("ds-ab", "m1", "naive", 0.5),
            ("ds-ab", "m1", "coached", 0.6),
        ))
        e = frozenset(("aaa", "bbb"))
        assert ev["cond_deltas_pair"][e] == [pytest.approx(0.1)]
        assert ev["cond_deltas_target"]["bbb"] == [pytest.approx(0.1)]
        assert "ccc" not in ev["cond_deltas_target"]


class TestPredictStrength:
    def _ev(self, queue_mod, rows):
        return queue_mod.build_evidence(_datasets(), _results(*rows))

    def test_backoff_chain(self, queue_mod):
        ev = self._ev(queue_mod, [("ds-ab", "m1", "naive", 0.6)])
        # pair evidence exists for aaa>bbb
        p = queue_mod.predict_strength(("aaa", "bbb"), "mX", "naive", ev)
        assert p["prior_basis"] == "pair" and p["pair_prior"] == 0.6
        # aaa>ccc: no pair or target evidence → source-language mean
        p = queue_mod.predict_strength(("aaa", "ccc"), "mX", "naive", ev)
        assert p["prior_basis"] == "source-language"
        # zzz>yyy: nothing matches → global mean of all results
        p = queue_mod.predict_strength(("zzz", "yyy"), "mX", "naive", ev)
        assert p["prior_basis"] == "global"
        # no results at all → documented default
        empty = queue_mod.build_evidence(_datasets(), [])
        p = queue_mod.predict_strength(("zzz", "yyy"), "mX", "naive", empty)
        assert p["prior_basis"] == "default"
        assert p["pair_prior"] == queue_mod.S0_FALLBACK

    def test_bonus_decays_with_observations(self, queue_mod):
        rows = [("ds-ab", "m1", "naive", 0.6)] * 9
        ev = self._ev(queue_mod, rows)
        seen = queue_mod.predict_strength(("aaa", "bbb"), "m1", "naive", ev)
        unseen = queue_mod.predict_strength(("aaa", "bbb"), "mX", "naive", ev)
        assert unseen["exploration_bonus"] > seen["exploration_bonus"] > 0

    def test_prediction_capped(self, queue_mod):
        ev = self._ev(queue_mod, [("ds-ab", "m1", "naive", 0.94)])
        p = queue_mod.predict_strength(("aaa", "bbb"), "mX", "naive", ev)
        assert p["predicted_strength"] <= queue_mod.S_CAP


# ---------------------------------------------------------------------------
# Full-board pagination
# ---------------------------------------------------------------------------

class TestFetchPagination:
    def test_reads_every_page_of_a_large_board(self, queue_mod, monkeypatch):
        """A board larger than one page must be read completely.

        Supabase caps single responses; the fetch must keep paging until
        a short page arrives, not trust one capped GET.
        """
        import io

        board = [
            {"dataset_id": f"ds-{i}", "model_slug": "m", "condition": "naive",
             "chrf_plus_plus": 50.0}
            for i in range(2501)
        ]
        requested_offsets = []

        def fake_urlopen(req, timeout=None):
            from urllib.parse import parse_qs, urlparse
            qs = parse_qs(urlparse(req.full_url).query)
            offset = int(qs["offset"][0])
            limit = int(qs["limit"][0])
            requested_offsets.append(offset)
            page = board[offset:offset + limit]

            class FakeResp(io.BytesIO):
                def __enter__(self):
                    return self

                def __exit__(self, *a):
                    return False

            import json as _json
            return FakeResp(_json.dumps(page).encode())

        monkeypatch.setattr(
            queue_mod.urllib.request, "urlopen", fake_urlopen,
        )
        rows = queue_mod._fetch_run_rows(page_size=1000)
        assert len(rows) == 2501
        assert requested_offsets == [0, 1000, 2000]

    def test_single_short_page_stops_immediately(self, queue_mod, monkeypatch):
        import io
        import json as _json

        def fake_urlopen(req, timeout=None):
            class FakeResp(io.BytesIO):
                def __enter__(self):
                    return self

                def __exit__(self, *a):
                    return False

            return FakeResp(_json.dumps([{"dataset_id": "x"}]).encode())

        monkeypatch.setattr(
            queue_mod.urllib.request, "urlopen", fake_urlopen,
        )
        assert len(queue_mod._fetch_run_rows(page_size=1000)) == 1


# ---------------------------------------------------------------------------
# Parity with the corpora-builder implementation
# ---------------------------------------------------------------------------

class TestEfficiencyParity:
    def test_matches_corpora_builder_on_fixture_graphs(self, queue_mod):
        if str(CORPORA_BUILDER) not in sys.path:
            sys.path.insert(0, str(CORPORA_BUILDER))
        from corpora_builder.probe_tatoeba import (
            graph_efficiency as builder_eff,
        )

        graphs = [
            (["a", "b"], set()),
            (["a", "b", "c"],
             {frozenset(("a", "b")), frozenset(("b", "c"))}),
            (["a", "b", "c", "d", "e"],
             {frozenset(("a", "b")), frozenset(("a", "c")),
              frozenset(("d", "e"))}),
            (list("abcdef"),
             {frozenset(p) for p in
              [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"),
               ("e", "f"), ("f", "a")]}),
        ]
        for nodes, edges in graphs:
            assert queue_mod.graph_efficiency(nodes, edges) == pytest.approx(
                builder_eff(nodes, edges)
            ), f"implementations diverged on {nodes} / {edges}"
