"""Tests for scripts/run_queue.py — top-N / budget selection from the queue."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "run_queue.py"


@pytest.fixture(scope="module")
def rq():
    spec = importlib.util.spec_from_file_location("run_queue", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _queue():
    return {"items": [
        {"id": "a", "condition": "naive", "est_cost_usd": 0.01,
         "language_pair": "eng>fao", "model": "m1", "run_command": "true"},
        {"id": "b", "condition": "coached", "est_cost_usd": 0.01,
         "language_pair": "eng>fao", "model": "m1", "run_command": "true"},
        {"id": "c", "condition": "naive", "est_cost_usd": 0.50,
         "language_pair": "nld>dan", "model": "m2", "run_command": "true"},
        {"id": "d", "condition": "naive", "est_cost_usd": None,
         "language_pair": "spa>cat", "model": "m3", "run_command": "true"},
        {"id": "e", "condition": "naive", "est_cost_usd": 0.02,
         "language_pair": "deu>dan", "model": "m1", "run_command": "true"},
    ]}


class TestSelectItems:
    def test_top_n_skips_coached_by_default(self, rq):
        selected, skipped = rq.select_items(_queue(), top=3)
        assert [i["id"] for i in selected] == ["a", "c", "d"]
        assert ("b", "coached (no --include-coached)") in skipped

    def test_top_n_includes_coached_when_asked(self, rq):
        selected, _ = rq.select_items(_queue(), top=2, include_coached=True)
        assert [i["id"] for i in selected] == ["a", "b"]

    def test_budget_takes_from_top_within_budget(self, rq):
        # $0.10: a (0.01) fits, c (0.50) would exceed, d unknown-cost
        # skipped, e (0.02) still fits — unknown is never treated as free.
        selected, skipped = rq.select_items(_queue(), budget=0.10)
        assert [i["id"] for i in selected] == ["a", "e"]
        reasons = dict(skipped)
        assert reasons["c"] == "would exceed budget"
        assert reasons["d"] == "no cost estimate (budget mode)"

    def test_budget_exact_fit(self, rq):
        selected, _ = rq.select_items(_queue(), budget=0.51)
        assert [i["id"] for i in selected] == ["a", "c"]

    def test_queue_order_is_respected(self, rq):
        # selection never re-sorts: ranking IS the priority model
        selected, _ = rq.select_items(_queue(), top=10)
        ids = [i["id"] for i in selected]
        assert ids == sorted(ids, key=lambda x: ["a", "c", "d", "e"].index(x))

    def test_empty_queue(self, rq):
        selected, skipped = rq.select_items({"items": []}, top=5)
        assert selected == [] and skipped == []
