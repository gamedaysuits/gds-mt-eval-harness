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
