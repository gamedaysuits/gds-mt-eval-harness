"""Tests for the queue runner (mt_eval_harness.queue_runner).

Covers top-N / budget selection, the `mt-eval queue` CLI wiring, and
the scripts/run_queue.py wrapper's backwards-compatible surface.

SSOT: The TestSharedSelectionVectors class at the bottom imports
scenarios from shared/queue-selection-vectors.json — the same file
consumed by mcp-server/test/tools.test.js. If you change selection
behavior, update the vectors and both suites must pass.
"""

from __future__ import annotations

import importlib.util
import json
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


class TestReportHelpers:
    """Verify _read_report_cost and _read_report_chrf extract correctly."""

    def test_read_cost_from_valid_report(self, tmp_path):
        from mt_eval_harness.queue_runner import _read_report_cost
        import json

        report = {"overall": {"total_cost_usd": 0.0342, "avg_chrf": 62.3}}
        rpath = tmp_path / "run_20260614_report.json"
        rpath.write_text(json.dumps(report), encoding="utf-8")
        assert _read_report_cost(rpath) == pytest.approx(0.0342)

    def test_read_cost_missing_field(self, tmp_path):
        from mt_eval_harness.queue_runner import _read_report_cost
        import json

        report = {"overall": {"avg_chrf": 62.3}}
        rpath = tmp_path / "run_missing_report.json"
        rpath.write_text(json.dumps(report), encoding="utf-8")
        assert _read_report_cost(rpath) == 0.0

    def test_read_cost_invalid_json(self, tmp_path):
        from mt_eval_harness.queue_runner import _read_report_cost

        rpath = tmp_path / "run_bad_report.json"
        rpath.write_text("not json", encoding="utf-8")
        assert _read_report_cost(rpath) == 0.0

    def test_read_cost_nonexistent_file(self, tmp_path):
        from mt_eval_harness.queue_runner import _read_report_cost

        rpath = tmp_path / "nonexistent.json"
        assert _read_report_cost(rpath) == 0.0

    def test_read_chrf_from_valid_report(self, tmp_path):
        from mt_eval_harness.queue_runner import _read_report_chrf
        import json

        report = {"overall": {"avg_chrf": 58.7}}
        rpath = tmp_path / "run_chrf_report.json"
        rpath.write_text(json.dumps(report), encoding="utf-8")
        assert _read_report_chrf(rpath) == pytest.approx(58.7)

    def test_read_chrf_missing(self, tmp_path):
        from mt_eval_harness.queue_runner import _read_report_chrf
        import json

        report = {"overall": {}}
        rpath = tmp_path / "run_nochrf_report.json"
        rpath.write_text(json.dumps(report), encoding="utf-8")
        assert _read_report_chrf(rpath) is None


class TestNoPublishFlag:
    """--no-publish flag parsing and wiring."""

    def test_no_publish_flag_parses(self):
        from mt_eval_harness.cli import build_parser

        args = build_parser().parse_args(
            ["queue", "--top", "3", "--no-publish"]
        )
        assert args.no_publish is True

    def test_no_publish_default_is_false(self):
        from mt_eval_harness.cli import build_parser

        args = build_parser().parse_args(["queue", "--top", "3"])
        assert args.no_publish is False

    def test_dry_run_with_no_publish(self, tmp_path, capsys):
        from mt_eval_harness.cli import build_parser
        from mt_eval_harness.queue_runner import run_from_args
        import json

        qfile = tmp_path / "queue.json"
        qfile.write_text(json.dumps(_queue()), encoding="utf-8")
        args = build_parser().parse_args(
            ["queue", "--budget", "0.10", "--dry-run",
             "--no-publish", "--queue", str(qfile)]
        )
        assert run_from_args(args) == 0
        out = capsys.readouterr().out
        assert "--dry-run: nothing executed." in out


class TestBudgetGuardDisplay:
    """Budget mode shows the cap and guard warning in the plan output."""

    def test_budget_cap_shown_in_plan(self, tmp_path, capsys):
        from mt_eval_harness.cli import build_parser
        from mt_eval_harness.queue_runner import run_from_args
        import json

        qfile = tmp_path / "queue.json"
        qfile.write_text(json.dumps(_queue()), encoding="utf-8")
        args = build_parser().parse_args(
            ["queue", "--budget", "0.10", "--dry-run", "--queue", str(qfile)]
        )
        run_from_args(args)
        out = capsys.readouterr().out
        # The plan should mention the budget cap
        assert "Budget cap: $0.10" in out
        # Should mention the budget guard behavior
        assert "stop early" in out


class TestSelectItemsBudgetEdgeCases:
    """Additional budget selection edge cases for the no-partial-run guarantee."""

    def test_single_item_exceeds_budget(self):
        """An item that costs more than the entire budget is skipped."""
        queue = {"items": [
            {"id": "x", "condition": "naive", "est_cost_usd": 5.00,
             "language_pair": "eng>fao", "model": "m1", "run_command": "true"},
        ]}
        selected, skipped = select_items(queue, budget=2.00)
        assert selected == []
        assert len(skipped) == 1
        assert skipped[0][1] == "would exceed budget"

    def test_no_partial_selection(self):
        """Items are only selected if they fit ENTIRELY within budget."""
        queue = {"items": [
            {"id": "a", "condition": "naive", "est_cost_usd": 1.50,
             "language_pair": "eng>fao", "model": "m1", "run_command": "true"},
            {"id": "b", "condition": "naive", "est_cost_usd": 1.50,
             "language_pair": "eng>crk", "model": "m1", "run_command": "true"},
        ]}
        # Budget is $2 — only the first item fits (1.50 <= 2.00),
        # the second would push to $3.00 which exceeds.
        selected, skipped = select_items(queue, budget=2.00)
        assert [i["id"] for i in selected] == ["a"]
        assert ("b", "would exceed budget") in skipped

    def test_cheaper_item_after_expensive_one(self):
        """A cheap item after an unaffordable one still gets selected."""
        queue = {"items": [
            {"id": "a", "condition": "naive", "est_cost_usd": 0.10,
             "language_pair": "eng>fao", "model": "m1", "run_command": "true"},
            {"id": "b", "condition": "naive", "est_cost_usd": 5.00,
             "language_pair": "eng>crk", "model": "m1", "run_command": "true"},
            {"id": "c", "condition": "naive", "est_cost_usd": 0.05,
             "language_pair": "deu>dan", "model": "m1", "run_command": "true"},
        ]}
        selected, _ = select_items(queue, budget=0.20)
        # a (0.10) fits, b (5.00) skipped, c (0.05) still fits
        assert [i["id"] for i in selected] == ["a", "c"]


class TestProviderSupport:
    """Multi-provider support: detection, CLI flag, and command injection."""

    def test_provider_key_map_covers_registry(self):
        """PROVIDER_KEY_MAP must have an entry for every registered provider."""
        from mt_eval_harness.queue_runner import PROVIDER_KEY_MAP
        from mt_eval_harness.providers.registry import PROVIDER_REGISTRY
        for name in PROVIDER_REGISTRY:
            assert name in PROVIDER_KEY_MAP, (
                f"Provider '{name}' is in PROVIDER_REGISTRY but not in "
                f"PROVIDER_KEY_MAP — the queue runner can't find its key"
            )

    def test_detect_provider_finds_openrouter(self, monkeypatch):
        from mt_eval_harness.queue_runner import detect_provider
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
        assert detect_provider() == "openrouter"

    def test_detect_provider_finds_anthropic(self, monkeypatch):
        from mt_eval_harness.queue_runner import detect_provider
        # Clear all other keys first
        for var in ("OPENROUTER_API_KEY", "OPENAI_API_KEY",
                     "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"):
            monkeypatch.delenv(var, raising=False)
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        assert detect_provider() == "anthropic"

    def test_detect_provider_prefers_openrouter(self, monkeypatch):
        """When multiple keys exist, openrouter wins (it proxies all models)."""
        from mt_eval_harness.queue_runner import detect_provider
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test")
        assert detect_provider() == "openrouter"

    def test_detect_provider_returns_none_when_empty(self, monkeypatch, tmp_path):
        from mt_eval_harness.queue_runner import detect_provider
        for var in ("OPENROUTER_API_KEY", "OPENAI_API_KEY",
                     "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"):
            monkeypatch.delenv(var, raising=False)
        # Run from an empty dir so dotenv doesn't find the repo's .env.local
        monkeypatch.chdir(tmp_path)
        assert detect_provider() is None

    def test_provider_flag_parses(self):
        from mt_eval_harness.cli import build_parser
        args = build_parser().parse_args(
            ["queue", "--budget", "2", "--provider", "anthropic"]
        )
        assert args.provider == "anthropic"

    def test_provider_flag_default_is_none(self):
        from mt_eval_harness.cli import build_parser
        args = build_parser().parse_args(["queue", "--budget", "2"])
        assert args.provider is None

    def test_invalid_provider_rejected(self):
        from mt_eval_harness.cli import build_parser
        with pytest.raises(SystemExit):
            build_parser().parse_args(
                ["queue", "--budget", "2", "--provider", "deepl"]
            )


class TestExtractErrorHint:
    """_extract_error_hint pulls one-liners from noisy subprocess output."""

    def test_empty_output(self):
        from mt_eval_harness.queue_runner import _extract_error_hint
        assert _extract_error_hint("") == ""

    def test_extracts_clean_cli_error(self):
        from mt_eval_harness.queue_runner import _extract_error_hint
        output = (
            "some setup output\n"
            "  Provider: openrouter\n"
            "\n"
            "  ✗ First batch failed for all 25 entries (HTTP 401: "
            '{"error":{"message":"User not found."}})'
        )
        result = _extract_error_hint(output)
        assert "First batch failed" in result
        assert "HTTP 401" in result

    def test_extracts_runtime_error(self):
        from mt_eval_harness.queue_runner import _extract_error_hint
        output = (
            "Traceback (most recent call last):\n"
            '  File "/path/to/runner.py", line 370, in execute_run\n'
            "    results = await strategy.execute(\n"
            "RuntimeError: First batch failed for all 25 entries "
            "(HTTP 401: bad key)\n"
        )
        result = _extract_error_hint(output)
        assert "First batch failed" in result

    def test_extracts_http_401(self):
        from mt_eval_harness.queue_runner import _extract_error_hint
        output = "blah blah\nHTTP 401: Unauthorized\nmore stuff\n"
        result = _extract_error_hint(output)
        assert "HTTP 401" in result

    def test_skips_traceback_lines(self):
        from mt_eval_harness.queue_runner import _extract_error_hint
        output = (
            'File "/path/to/something.py", line 42\n'
            "    at async something\n"
            "The actual error message\n"
        )
        result = _extract_error_hint(output)
        assert result == "The actual error message"


VECTORS_FILE = (
    Path(__file__).resolve().parent.parent.parent
    / "shared" / "queue-selection-vectors.json"
)


class TestSharedSelectionVectors:
    """Run every scenario from the shared test vectors.

    These vectors are the SSOT contract between the Python select_items
    (canonical) and the JS filterQueue (MCP server port). If a scenario
    fails here, the fix belongs in select_items or in the vectors —
    never silently change the vectors to match a JS-only change.
    """

    @pytest.fixture(scope="class")
    def vectors(self):
        assert VECTORS_FILE.exists(), (
            f"Shared test vectors not found: {VECTORS_FILE}\n"
            "Run from the repo root, or check that shared/ exists."
        )
        return json.loads(VECTORS_FILE.read_text(encoding="utf-8"))

    def test_vectors_file_is_valid(self, vectors):
        """Sanity: the vectors file has the expected structure."""
        assert "items" in vectors
        assert "scenarios" in vectors
        assert len(vectors["scenarios"]) >= 5, "Expected at least 5 scenarios"

    @pytest.mark.parametrize(
        "scenario_index",
        range(8),  # update if you add scenarios
        ids=lambda i: f"scenario_{i}",
    )
    def test_scenario(self, vectors, scenario_index):
        if scenario_index >= len(vectors["scenarios"]):
            pytest.skip("scenario index out of range")

        scenario = vectors["scenarios"][scenario_index]
        items = scenario["override_items"] if "override_items" in scenario else vectors["items"]
        params = scenario["params"]

        queue = {"items": items}
        selected, _ = select_items(
            queue,
            top=params.get("top"),
            budget=params.get("budget"),
            include_coached=params.get("include_coached", False),
        )
        ids = [it["id"] for it in selected]
        assert ids == scenario["expected_ids"], (
            f"Scenario \"{scenario['name']}\": "
            f"expected {scenario['expected_ids']} got {ids}"
        )
