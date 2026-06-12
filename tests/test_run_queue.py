"""Tests for the queue runner (mt_eval_harness.queue_runner).

Covers top-N / budget selection, the `mt-eval queue` CLI wiring, and
the scripts/run_queue.py wrapper's backwards-compatible surface.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from mt_eval_harness.queue_runner import select_items

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "run_queue.py"


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
    def test_top_n_skips_coached_by_default(self):
        selected, skipped = select_items(_queue(), top=3)
        assert [i["id"] for i in selected] == ["a", "c", "d"]
        assert ("b", "coached (no --include-coached)") in skipped

    def test_top_n_includes_coached_when_asked(self):
        selected, _ = select_items(_queue(), top=2, include_coached=True)
        assert [i["id"] for i in selected] == ["a", "b"]

    def test_budget_takes_from_top_within_budget(self):
        # $0.10: a (0.01) fits, c (0.50) would exceed, d unknown-cost
        # skipped, e (0.02) still fits — unknown is never treated as free.
        selected, skipped = select_items(_queue(), budget=0.10)
        assert [i["id"] for i in selected] == ["a", "e"]
        reasons = dict(skipped)
        assert reasons["c"] == "would exceed budget"
        assert reasons["d"] == "no cost estimate (budget mode)"

    def test_budget_exact_fit(self):
        selected, _ = select_items(_queue(), budget=0.51)
        assert [i["id"] for i in selected] == ["a", "c"]

    def test_queue_order_is_respected(self):
        # selection never re-sorts: ranking IS the priority model
        selected, _ = select_items(_queue(), top=10)
        ids = [i["id"] for i in selected]
        assert ids == sorted(ids, key=lambda x: ["a", "c", "d", "e"].index(x))

    def test_empty_queue(self):
        selected, skipped = select_items({"items": []}, top=5)
        assert selected == [] and skipped == []


class TestCliWiring:
    """`mt-eval queue` must parse the runner's flags and dispatch."""

    def test_queue_subcommand_parses(self):
        from mt_eval_harness.cli import build_parser

        args = build_parser().parse_args(
            ["queue", "--top", "3", "--dry-run"]
        )
        assert args.command == "queue"
        assert args.top == 3
        assert args.budget is None
        assert args.dry_run is True
        assert args.queue.endswith("/queue.json")

    def test_budget_flag_parses(self):
        from mt_eval_harness.cli import build_parser

        args = build_parser().parse_args(["queue", "--budget", "2.50"])
        assert args.budget == pytest.approx(2.50)
        assert args.top is None

    def test_top_and_budget_are_exclusive(self):
        from mt_eval_harness.cli import build_parser

        with pytest.raises(SystemExit):
            build_parser().parse_args(
                ["queue", "--top", "2", "--budget", "1.0"]
            )

    def test_dry_run_executes_nothing(self, tmp_path, capsys):
        from mt_eval_harness.cli import build_parser
        from mt_eval_harness.queue_runner import run_from_args

        qfile = tmp_path / "queue.json"
        import json
        qfile.write_text(json.dumps(_queue()), encoding="utf-8")
        args = build_parser().parse_args(
            ["queue", "--top", "2", "--dry-run", "--queue", str(qfile)]
        )
        assert run_from_args(args) == 0
        out = capsys.readouterr().out
        assert "--dry-run: nothing executed." in out
        assert "eng>fao" in out

    def test_invalid_top_rejected(self, capsys):
        from mt_eval_harness.cli import build_parser
        from mt_eval_harness.queue_runner import run_from_args

        args = build_parser().parse_args(["queue", "--top", "0"])
        assert run_from_args(args) == 2


class TestScriptWrapper:
    """scripts/run_queue.py keeps the documented standalone surface."""

    def test_wrapper_reexports_selection(self):
        spec = importlib.util.spec_from_file_location("run_queue", SCRIPT)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        selected, _ = mod.select_items(_queue(), top=1)
        assert [i["id"] for i in selected] == ["a"]
        assert mod.DEFAULT_QUEUE_URL.startswith("https://")
