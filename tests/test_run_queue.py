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


# ---------------------------------------------------------------------------
# New tests for the execution-loop improvements (timeout, signal, budget
# guard, sequential auto-detection, --stop-on-failure wiring).
#
# These tests run the full run_from_args path with --no-publish and --yes
# to bypass auth and confirmation. A mock_provider fixture stubs out the
# provider subsystem so no real API calls are made.
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_provider(monkeypatch):
    """Stub provider detection/loading so execution tests skip auth."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test-fake")

    class _FakeProvider:
        def load_api_key(self):
            pass

    monkeypatch.setattr(
        "mt_eval_harness.providers.get_provider",
        lambda name: _FakeProvider(),
    )


def _make_queue_file(tmp_path, items):
    """Write a minimal queue.json and return its path."""
    qfile = tmp_path / "queue.json"
    qfile.write_text(json.dumps({"items": items}), encoding="utf-8")
    return str(qfile)


class TestTimeoutFlagParsing:
    """--timeout flag is accepted and parsed correctly."""

    def test_timeout_default(self):
        from mt_eval_harness.cli import build_parser

        args = build_parser().parse_args(["queue", "--budget", "2"])
        assert args.timeout == 300

    def test_timeout_explicit(self):
        from mt_eval_harness.cli import build_parser

        args = build_parser().parse_args(
            ["queue", "--budget", "2", "--timeout", "60"]
        )
        assert args.timeout == 60

    def test_jobs_default_is_none(self):
        from mt_eval_harness.cli import build_parser

        args = build_parser().parse_args(["queue", "--budget", "2"])
        # Default is None (auto-detect sequential vs. concurrent)
        assert args.jobs is None


class TestTimeoutHandling:
    """Per-item timeout kills hung subprocesses and reports them."""

    def test_timeout_kills_hung_item(self, tmp_path, mock_provider, capsys):
        from mt_eval_harness.cli import build_parser
        from mt_eval_harness.queue_runner import run_from_args

        qfile = _make_queue_file(tmp_path, [{
            "id": "slow", "condition": "naive", "est_cost_usd": 0.01,
            "language_pair": "eng>xxx", "model": "test/model",
            "run_command": "sleep 60",
        }])
        args = build_parser().parse_args([
            "queue", "--top", "1", "--yes", "--no-publish",
            "--queue", qfile, "--timeout", "2",
        ])
        rc = run_from_args(args)
        out = capsys.readouterr().out
        assert "timed out" in out
        assert rc == 1  # timeout is a non-zero exit


class TestStopOnFailureWiring:
    """--stop-on-failure now actually halts the batch (was a dead flag)."""

    def test_stop_on_failure_halts_batch(
        self, tmp_path, mock_provider, capsys
    ):
        from mt_eval_harness.cli import build_parser
        from mt_eval_harness.queue_runner import run_from_args

        items = [
            {"id": "fail1", "condition": "naive", "est_cost_usd": 0.01,
             "language_pair": "eng>aaa", "model": "m",
             "run_command": "exit 1"},
            {"id": "ok1", "condition": "naive", "est_cost_usd": 0.01,
             "language_pair": "eng>bbb", "model": "m",
             "run_command": "echo ok"},
        ]
        qfile = _make_queue_file(tmp_path, items)
        args = build_parser().parse_args([
            "queue", "--top", "2", "--yes", "--no-publish",
            "--stop-on-failure",
            "--queue", qfile, "--timeout", "5",
        ])
        rc = run_from_args(args)
        out = capsys.readouterr().out
        # The flag should print its halt message
        assert "--stop-on-failure" in out
        # Only 1 item should have run (the failing one) because
        # ≤3 items runs sequentially and first failure halts.
        assert "eng>aaa" in out
        assert rc == 1


class TestSequentialSmallBatch:
    """≤3 items run sequentially by default; --jobs overrides."""

    def test_three_items_run_sequential(
        self, tmp_path, mock_provider, capsys
    ):
        from mt_eval_harness.cli import build_parser
        from mt_eval_harness.queue_runner import run_from_args

        items = [
            {"id": f"i{i}", "condition": "naive", "est_cost_usd": 0.01,
             "language_pair": f"eng>x{i}x", "model": "m",
             "run_command": "true"}
            for i in range(3)
        ]
        qfile = _make_queue_file(tmp_path, items)
        args = build_parser().parse_args([
            "queue", "--top", "3", "--yes", "--no-publish",
            "--queue", qfile, "--timeout", "5",
        ])
        run_from_args(args)
        out = capsys.readouterr().out
        assert "sequential" in out

    def test_jobs_explicit_overrides_sequential(
        self, tmp_path, mock_provider, capsys
    ):
        from mt_eval_harness.cli import build_parser
        from mt_eval_harness.queue_runner import run_from_args

        items = [
            {"id": f"i{i}", "condition": "naive", "est_cost_usd": 0.01,
             "language_pair": f"eng>x{i}x", "model": "m",
             "run_command": "true"}
            for i in range(3)
        ]
        qfile = _make_queue_file(tmp_path, items)
        args = build_parser().parse_args([
            "queue", "--top", "3", "--yes", "--no-publish",
            "--queue", qfile, "--timeout", "5", "--jobs", "4",
        ])
        run_from_args(args)
        out = capsys.readouterr().out
        assert "4 concurrent" in out

    def test_four_items_default_concurrent(
        self, tmp_path, mock_provider, capsys
    ):
        from mt_eval_harness.cli import build_parser
        from mt_eval_harness.queue_runner import run_from_args

        items = [
            {"id": f"i{i}", "condition": "naive", "est_cost_usd": 0.01,
             "language_pair": f"eng>x{i}x", "model": "m",
             "run_command": "true"}
            for i in range(4)
        ]
        qfile = _make_queue_file(tmp_path, items)
        args = build_parser().parse_args([
            "queue", "--top", "4", "--yes", "--no-publish",
            "--queue", qfile, "--timeout", "5",
        ])
        run_from_args(args)
        out = capsys.readouterr().out
        # 4 items → should NOT be sequential
        assert "sequential" not in out
        assert "concurrent" in out


class TestBudgetPreDispatch:
    """Budget guard prevents over-spending during execution.

    select_items() filters by estimated cost during selection. The
    pre-dispatch guard in the execution loop catches the case where
    actual costs (which may differ from estimates) push past the budget.
    We test the full pipeline here: selection + execution.
    """

    def test_budget_guard_shown_in_output(
        self, tmp_path, mock_provider, capsys
    ):
        from mt_eval_harness.cli import build_parser
        from mt_eval_harness.queue_runner import run_from_args

        items = [
            {"id": "cheap", "condition": "naive", "est_cost_usd": 0.02,
             "language_pair": "eng>aaa", "model": "m",
             "run_command": "true"},
        ]
        qfile = _make_queue_file(tmp_path, items)
        args = build_parser().parse_args([
            "queue", "--budget", "0.05", "--yes", "--no-publish",
            "--queue", qfile, "--timeout", "5",
        ])
        rc = run_from_args(args)
        out = capsys.readouterr().out
        # Budget cap is shown in the plan
        assert "Budget cap: $0.05" in out
        # Item ran successfully
        assert "eng>aaa" in out
        assert rc == 0

    def test_select_items_filters_expensive_before_dispatch(self):
        """Items that exceed budget are never dispatched."""
        queue = {"items": [
            {"id": "cheap", "condition": "naive", "est_cost_usd": 0.02,
             "language_pair": "eng>aaa", "model": "m",
             "run_command": "true"},
            {"id": "pricey", "condition": "naive", "est_cost_usd": 0.50,
             "language_pair": "eng>bbb", "model": "m",
             "run_command": "true"},
            {"id": "cheap2", "condition": "naive", "est_cost_usd": 0.02,
             "language_pair": "eng>ccc", "model": "m",
             "run_command": "true"},
        ]}
        selected, skipped = select_items(queue, budget=0.05)
        ids = [i["id"] for i in selected]
        # Expensive item filtered during selection
        assert "pricey" not in ids
        assert "cheap" in ids
        assert "cheap2" in ids
        # Verify reason
        assert ("pricey", "would exceed budget") in skipped


# ---------------------------------------------------------------------------
# Publish-reliability hardening (the curl champollion.dev/give path).
#
# These cover the three failure modes that previously kept the headline
# `--budget 2` flow from reliably publishing:
#   1. child run subprocesses inheriting the tty and hanging on their own
#      publish prompt  → fixed with stdin=DEVNULL
#   2. publish_to_supabase raising SystemExit (4xx / integrity / retries)
#      aborting the whole batch → fixed with _auto_publish swallowing it
#   3. concurrent items cross-matching reports in a shared output dir →
#      fixed with a per-item --output-dir and _find_report_in_dir
# ---------------------------------------------------------------------------


class TestAutoPublish:
    """_auto_publish must NEVER let a publish failure escape (except Ctrl+C)."""

    def test_swallows_systemexit_returns_false(self, monkeypatch, capsys):
        from mt_eval_harness import queue_runner

        def boom(*a, **k):
            raise SystemExit(1)   # what publish does on a 4xx / integrity fail

        monkeypatch.setattr(
            "mt_eval_harness.publish.publish_to_supabase", boom
        )
        ok = queue_runner._auto_publish("/tmp/x_report.json", "eng>zul")
        assert ok is False
        out = capsys.readouterr().out
        assert "Publish failed" in out
        # Tells the contributor exactly how to recover their paid run.
        assert "mt-eval publish /tmp/x_report.json" in out

    def test_swallows_generic_exception_returns_false(self, monkeypatch):
        from mt_eval_harness import queue_runner

        def boom(*a, **k):
            raise RuntimeError("network down")

        monkeypatch.setattr(
            "mt_eval_harness.publish.publish_to_supabase", boom
        )
        assert queue_runner._auto_publish("/tmp/x_report.json") is False

    def test_returns_true_on_success(self, monkeypatch):
        from mt_eval_harness import queue_runner
        monkeypatch.setattr(
            "mt_eval_harness.publish.publish_to_supabase",
            lambda *a, **k: {"id": "x"},
        )
        assert queue_runner._auto_publish("/tmp/x_report.json") is True

    def test_keyboardinterrupt_propagates(self, monkeypatch):
        """Ctrl+C must still interrupt — it is NOT a publish failure."""
        from mt_eval_harness import queue_runner

        def boom(*a, **k):
            raise KeyboardInterrupt

        monkeypatch.setattr(
            "mt_eval_harness.publish.publish_to_supabase", boom
        )
        with pytest.raises(KeyboardInterrupt):
            queue_runner._auto_publish("/tmp/x_report.json")


class TestFindReportInDir:
    """_find_report_in_dir reads exactly one item's isolated output."""

    def test_missing_dir_returns_none(self, tmp_path):
        from mt_eval_harness.queue_runner import _find_report_in_dir
        assert _find_report_in_dir(tmp_path / "nope") is None

    def test_empty_dir_returns_none(self, tmp_path):
        from mt_eval_harness.queue_runner import _find_report_in_dir
        assert _find_report_in_dir(tmp_path) is None

    def test_finds_the_report(self, tmp_path):
        from mt_eval_harness.queue_runner import _find_report_in_dir
        (tmp_path / "run_123_report.json").write_text("{}", encoding="utf-8")
        found = _find_report_in_dir(tmp_path)
        assert found is not None and found.name == "run_123_report.json"


class TestSubprocessIsolation:
    """Children get DEVNULL stdin and a unique --output-dir."""

    def test_devnull_stdin_and_isolated_output_dir(
        self, tmp_path, mock_provider, monkeypatch
    ):
        from mt_eval_harness import queue_runner
        from mt_eval_harness.cli import build_parser

        captured = []

        class _FakeProc:
            returncode = 0

            def communicate(self, timeout=None):
                return ("", None)

            def kill(self):
                pass

        def spy(cmd, **kwargs):
            captured.append((cmd, kwargs))
            return _FakeProc()

        monkeypatch.setattr(queue_runner.subprocess, "Popen", spy)

        item = {
            "id": "eng-zul-dev-v1__m__naive", "condition": "naive",
            "est_cost_usd": 0.01, "language_pair": "eng>zul", "model": "m",
            "run_command": "mt-eval run --corpus x.json --model m --yes",
        }
        qfile = _make_queue_file(tmp_path, [item])
        args = build_parser().parse_args([
            "queue", "--top", "1", "--yes", "--no-publish",
            "--queue", qfile, "--timeout", "5",
        ])
        queue_runner.run_from_args(args)

        assert captured, "Popen was never called"
        cmd, kwargs = captured[0]
        # (1) the child must not be able to read our terminal
        assert kwargs.get("stdin") is queue_runner.subprocess.DEVNULL
        # (3) each item runs in its own report dir
        assert "--output-dir" in cmd


class TestBatchSurvivesPublishFailure:
    """A publish that raises SystemExit must NOT abort the rest of the batch."""

    def test_systemexit_publish_does_not_abort_batch(
        self, tmp_path, mock_provider, monkeypatch, capsys
    ):
        from mt_eval_harness import queue_runner
        from mt_eval_harness.cli import build_parser

        out_root = tmp_path / "out"
        monkeypatch.setattr(queue_runner, "DEFAULT_OUTPUT_DIR", str(out_root))

        # Auth is required on the publish path — stub it so no OAuth happens.
        monkeypatch.setattr(
            "mt_eval_harness.auth.get_session",
            lambda: {"access_token": "x", "user": {}},
        )
        monkeypatch.setattr(
            "mt_eval_harness.auth.get_submitter_name", lambda s: "tester"
        )
        # Every publish explodes with SystemExit — the dangerous case.
        monkeypatch.setattr(
            "mt_eval_harness.publish.publish_to_supabase",
            lambda *a, **k: (_ for _ in ()).throw(SystemExit(1)),
        )

        report = json.dumps({"overall": {"total_cost_usd": 0.01,
                                         "avg_chrf": 50.0}})
        items = []
        for idx, (iid, pair) in enumerate(
            [("itemA", "eng>zul"), ("itemB", "eng>hau")], 1
        ):
            d = out_root / "queue" / f"{idx:03d}_{iid}"
            cmd = (f"mkdir -p '{d}' && printf '%s' '{report}' "
                   f"> '{d}/run_{iid}_report.json'")
            items.append({
                "id": iid, "condition": "naive", "est_cost_usd": 0.01,
                "language_pair": pair, "model": "m", "run_command": cmd,
            })
        qfile = _make_queue_file(tmp_path, items)

        # 2 items → sequential → deterministic ordering.
        args = build_parser().parse_args([
            "queue", "--top", "2", "--yes",
            "--queue", qfile, "--timeout", "10",
        ])

        # The whole point: this returns an int, it does NOT raise SystemExit.
        rc = queue_runner.run_from_args(args)
        assert isinstance(rc, int)

        out = capsys.readouterr().out
        # Both items ran...
        assert "eng>zul" in out and "eng>hau" in out
        # ...were honestly reported as NOT published...
        assert "NOT published" in out
        assert "0/2 published" in out
        # ...and the contributor is told how to recover their paid runs.
        assert "mt-eval publish" in out


class TestClassifyFailure:
    """_classify_failure: rate-limit/timeout must NOT read as a bad key."""

    @pytest.mark.parametrize("status,hint,expected", [
        ("timeout", "",                              "transient"),
        ("failed",  "HTTP 429: rate limit exceeded", "transient"),
        ("failed",  "rate_limit reached",            "transient"),
        ("failed",  "503 Service Unavailable",       "transient"),
        ("failed",  "connection reset by peer",      "transient"),
        ("failed",  "HTTP 401: invalid api key",     "auth"),
        ("failed",  "403 Forbidden",                 "auth"),
        ("failed",  "User not found.",               "auth"),
        ("failed",  "something exploded",            "other"),
        # A 429 body that also mentions a key is STILL a rate limit.
        ("failed",  "429: too many requests for this api key", "transient"),
    ])
    def test_classification(self, status, hint, expected):
        from mt_eval_harness.queue_runner import _classify_failure
        assert _classify_failure(status, hint) == expected


class TestCircuitBreakerClassification:
    """Auth failures offer key re-entry; transient ones never stall."""

    def test_transient_failures_do_not_prompt_for_key(
        self, tmp_path, mock_provider, monkeypatch, capsys
    ):
        from mt_eval_harness import queue_runner
        from mt_eval_harness.cli import build_parser

        prompted = []
        monkeypatch.setattr(
            queue_runner, "_prompt_reenter_key",
            lambda ev: prompted.append(ev) or None,
        )

        items = [
            {"id": f"t{i}", "condition": "naive", "est_cost_usd": 0.01,
             "language_pair": f"eng>x{i}", "model": "m",
             "run_command": "echo 'HTTP 429: rate limit exceeded'; exit 1"}
            for i in range(6)
        ]
        qfile = _make_queue_file(tmp_path, items)
        args = build_parser().parse_args([
            "queue", "--top", "6", "--yes", "--no-publish",
            "--queue", qfile, "--timeout", "5",
        ])
        queue_runner.run_from_args(args)
        out = capsys.readouterr().out

        # The key-re-entry prompt must NEVER fire for rate limits.
        assert prompted == []
        # The user is told it's transient, not an auth problem.
        assert "not an auth" in out.lower()

    def test_auth_failures_prompt_for_key(
        self, tmp_path, mock_provider, monkeypatch, capsys
    ):
        from mt_eval_harness import queue_runner
        from mt_eval_harness.cli import build_parser

        prompted = []
        # Decline re-entry (return None) so the batch then stops.
        monkeypatch.setattr(
            queue_runner, "_prompt_reenter_key",
            lambda ev: prompted.append(ev) or None,
        )

        items = [
            {"id": f"a{i}", "condition": "naive", "est_cost_usd": 0.01,
             "language_pair": f"eng>y{i}", "model": "m",
             "run_command": "echo 'HTTP 401: invalid api key'; exit 1"}
            for i in range(3)
        ]
        qfile = _make_queue_file(tmp_path, items)
        args = build_parser().parse_args([
            "queue", "--top", "3", "--yes", "--no-publish",
            "--queue", qfile, "--timeout", "5",
        ])
        queue_runner.run_from_args(args)

        # 3 consecutive auth failures → exactly the case that SHOULD prompt.
        assert prompted, "auth failures should have offered key re-entry"


class TestDefaultConcurrencyByProvider:
    """Direct providers default to gentler concurrency than OpenRouter."""

    def _run(self, tmp_path, monkeypatch, provider, env_var, n=5):
        from mt_eval_harness.cli import build_parser
        from mt_eval_harness.queue_runner import run_from_args

        for var in ("OPENROUTER_API_KEY", "OPENAI_API_KEY",
                    "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"):
            monkeypatch.delenv(var, raising=False)
        monkeypatch.setenv(env_var, "sk-test")

        class _FakeProvider:
            def load_api_key(self):
                pass

        monkeypatch.setattr(
            "mt_eval_harness.providers.get_provider",
            lambda name: _FakeProvider(),
        )
        items = [
            {"id": f"i{i}", "condition": "naive", "est_cost_usd": 0.01,
             "language_pair": f"eng>x{i}", "model": "m",
             "run_command": "true"}
            for i in range(n)
        ]
        qfile = _make_queue_file(tmp_path, items)
        args = build_parser().parse_args([
            "queue", "--top", str(n), "--yes", "--no-publish",
            "--provider", provider, "--queue", qfile, "--timeout", "5",
        ])
        run_from_args(args)

    def test_openrouter_defaults_to_8(self, tmp_path, monkeypatch, capsys):
        self._run(tmp_path, monkeypatch, "openrouter", "OPENROUTER_API_KEY")
        assert "8 concurrent" in capsys.readouterr().out

    def test_direct_provider_defaults_to_4(self, tmp_path, monkeypatch, capsys):
        self._run(tmp_path, monkeypatch, "anthropic", "ANTHROPIC_API_KEY")
        assert "4 concurrent" in capsys.readouterr().out
