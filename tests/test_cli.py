"""
Tests for mt_eval_harness.cli — CLI argument parsing and command dispatch.

Covers:
    - Parser construction and subcommand registration
    - Argument parsing for every subcommand
    - args_to_config() conversion
    - cmd_list() output
    - cmd_export() dispatch
    - Default (no subcommand) behavior
    - Branding verification
"""

import sys
from io import StringIO
from unittest.mock import patch, MagicMock

import pytest

from mt_eval_harness.cli import (
    build_parser,
    args_to_config,
    cmd_list,
)
from mt_eval_harness.config import (
    RunConfig,
    DEFAULT_MODEL,
    MODEL_REGISTRY,
)


# ---------------------------------------------------------------------------
# Parser construction
# ---------------------------------------------------------------------------

class TestParserConstruction:
    """Verify the argument parser registers all subcommands."""

    def test_parser_builds(self):
        parser = build_parser()
        assert parser.prog == "mt-eval"

    def test_has_run_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "test.json"])
        assert args.command == "run"

    def test_has_test_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["test", "log.json"])
        assert args.command == "test"

    def test_has_compare_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["compare", "a.json", "b.json"])
        assert args.command == "compare"

    def test_has_dashboard_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["dashboard", "logs/"])
        assert args.command == "dashboard"

    def test_has_list_subcommand(self):
        parser = build_parser()
        args = parser.parse_args(["list", "models"])
        assert args.command == "list"
        assert args.what == "models"

    def test_has_export_subcommand(self):
        parser = build_parser()
        args = parser.parse_args([
            "export",
            "--report", "report.json",
            "--name", "test-plugin",
            "--type", "llm",
            "--locales", "fr",
        ])
        assert args.command == "export"


# ---------------------------------------------------------------------------
# Run argument parsing
# ---------------------------------------------------------------------------

class TestRunArgParsing:
    """Verify run arguments parse correctly."""

    def test_defaults(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "test.json"])
        assert args.model == DEFAULT_MODEL
        assert args.dataset == "all"
        assert args.batch_size == 1
        assert args.temperature == 0.0

    def test_model_override(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "x.json", "-m", "claude-opus-4.6"])
        assert args.model == "claude-opus-4.6"

    def test_batch_size(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "x.json", "-b", "5"])
        assert args.batch_size == 5

    def test_tools_flag(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "x.json", "--tools"])
        assert args.tools is True

    def test_ids_parsing(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "x.json", "--ids", "0,1,5,10"])
        assert args.ids == "0,1,5,10"

    def test_custom_fields(self):
        parser = build_parser()
        args = parser.parse_args([
            "run", "--corpus", "x.json",
            "--source-field", "english",
            "--target-field", "cree_sro",
        ])
        assert args.source_field == "english"
        assert args.target_field == "cree_sro"

    def test_dry_run_flag(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "x.json", "--dry-run"])
        assert args.dry_run is True

    def test_no_cache_flag(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "x.json", "--no-cache"])
        assert args.no_cache is True

    def test_hooks_string(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "x.json", "--hooks", "fst_gate,normalize"])
        assert args.hooks == "fst_gate,normalize"


# ---------------------------------------------------------------------------
# Dashboard argument parsing
# ---------------------------------------------------------------------------

class TestDashboardArgParsing:
    """Verify dashboard arguments parse correctly."""

    def test_basic_dashboard(self):
        parser = build_parser()
        args = parser.parse_args(["dashboard", "logs/"])
        assert args.command == "dashboard"
        assert args.log_paths == ["logs/"]

    def test_dashboard_output(self):
        parser = build_parser()
        args = parser.parse_args(["dashboard", "logs/", "-o", "out.html"])
        assert args.output == "out.html"

    def test_dashboard_watch(self):
        parser = build_parser()
        args = parser.parse_args(["dashboard", "logs/", "--watch"])
        assert args.watch is True

    def test_dashboard_interval(self):
        parser = build_parser()
        args = parser.parse_args(["dashboard", "logs/", "--interval", "10"])
        assert args.interval == 10.0

    def test_multiple_log_paths(self):
        parser = build_parser()
        args = parser.parse_args(["dashboard", "logs/dir1", "logs/dir2", "extra.json"])
        assert len(args.log_paths) == 3


# ---------------------------------------------------------------------------
# Export argument parsing
# ---------------------------------------------------------------------------

class TestExportArgParsing:
    """Verify export subcommand parsing."""

    def test_required_args(self):
        parser = build_parser()
        args = parser.parse_args([
            "export",
            "--report", "report.json",
            "--name", "crk-coached-v1",
            "--type", "llm-coached",
            "--locales", "crk",
        ])
        assert args.report == "report.json"
        assert args.name == "crk-coached-v1"
        assert args.type == "llm-coached"
        assert args.locales == "crk"

    def test_optional_args(self):
        parser = build_parser()
        args = parser.parse_args([
            "export",
            "--report", "r.json",
            "--name", "test",
            "--type", "llm",
            "--locales", "fr",
            "--author", "Test Author",
            "--description", "A test plugin",
            "--version", "2.0.0",
        ])
        assert args.author == "Test Author"
        assert args.description == "A test plugin"
        assert args.plugin_version == "2.0.0"

    def test_commercial_ready_flag(self):
        parser = build_parser()
        args = parser.parse_args([
            "export",
            "--report", "r.json",
            "--name", "test",
            "--type", "llm",
            "--locales", "fr",
            "--commercial-ready",
        ])
        assert args.commercial_ready is True

    def test_commercial_ready_default(self):
        parser = build_parser()
        args = parser.parse_args([
            "export",
            "--report", "r.json",
            "--name", "test",
            "--type", "llm",
            "--locales", "fr",
        ])
        assert args.commercial_ready is False

    def test_author_default_neutral(self):
        """Default author should be empty (not GDS-branded)."""
        parser = build_parser()
        args = parser.parse_args([
            "export",
            "--report", "r.json",
            "--name", "test",
            "--type", "llm",
            "--locales", "fr",
        ])
        assert args.author == ""
        assert "gds" not in args.author.lower()


# ---------------------------------------------------------------------------
# args_to_config() conversion
# ---------------------------------------------------------------------------

class TestArgsToConfig:
    """Verify CLI args correctly map to RunConfig fields."""

    def test_basic_conversion(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "test.json"])
        config = args_to_config(args)

        assert isinstance(config, RunConfig)
        assert config.corpus_path == "test.json"
        assert config.model == DEFAULT_MODEL
        assert config.dataset == "all"

    def test_entry_ids_parsed(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "x.json", "--ids", "0,5,10"])
        config = args_to_config(args)

        assert config.entry_ids == [0, 5, 10]

    def test_tools_list_parsed(self):
        parser = build_parser()
        args = parser.parse_args([
            "run", "--corpus", "x.json",
            "--tools", "--tools-list", "fst_validate,fst_generate",
        ])
        config = args_to_config(args)

        assert config.tools_enabled is True
        assert config.tools_list == ["fst_validate", "fst_generate"]

    def test_post_hooks_parsed(self):
        parser = build_parser()
        args = parser.parse_args([
            "run", "--corpus", "x.json",
            "--hooks", "fst_gate,normalize",
        ])
        config = args_to_config(args)

        assert config.post_hooks == ["fst_gate", "normalize"]

    def test_no_cache_maps(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "x.json", "--no-cache"])
        config = args_to_config(args)

        assert config.cache_enabled is False

    def test_temperature_maps(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "x.json", "--temperature", "0.5"])
        config = args_to_config(args)

        assert config.temperature == 0.5

    def test_run_name_maps(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "x.json", "-n", "Baseline FST"])
        config = args_to_config(args)

        assert config.run_name == "Baseline FST"

    def test_prompt_version_maps(self):
        parser = build_parser()
        args = parser.parse_args(["run", "--corpus", "x.json", "-p", "custom", "--custom-prompt", "p.txt"])
        config = args_to_config(args)

        assert config.prompt_version == "custom"
        assert config.custom_prompt_path == "p.txt"


# ---------------------------------------------------------------------------
# cmd_list() output
# ---------------------------------------------------------------------------

class TestCmdList:
    """Verify the list subcommand output."""

    def test_list_models_shows_all_registry_entries(self, capsys):
        cmd_list("models")
        out = capsys.readouterr().out

        for short_name in MODEL_REGISTRY:
            assert short_name in out, f"Model '{short_name}' not in list output"

    def test_list_models_marks_default(self, capsys):
        cmd_list("models")
        out = capsys.readouterr().out

        assert "(default)" in out
        assert DEFAULT_MODEL in out

    def test_list_models_mentions_openrouter(self, capsys):
        cmd_list("models")
        out = capsys.readouterr().out

        assert "OpenRouter" in out

    def test_list_prompts(self, capsys):
        cmd_list("prompts")
        out = capsys.readouterr().out

        assert "naive" in out
        assert "custom" in out

    def test_list_no_gds_branding(self, capsys):
        """list output should be free of GDS branding."""
        cmd_list("models")
        out_models = capsys.readouterr().out.lower()

        cmd_list("prompts")
        out_prompts = capsys.readouterr().out.lower()

        combined = out_models + out_prompts
        assert "gds" not in combined
        assert "game day" not in combined


# ---------------------------------------------------------------------------
# Branding — whole module
# ---------------------------------------------------------------------------

class TestCLIBranding:
    """Verify the CLI module is free of legacy branding."""

    def test_description_neutral(self):
        parser = build_parser()
        assert "gds" not in parser.description.lower()

    def test_epilog_neutral(self):
        parser = build_parser()
        assert "gds" not in parser.epilog.lower()

    def test_prog_name(self):
        parser = build_parser()
        assert parser.prog == "mt-eval"


# ---------------------------------------------------------------------------
# Compare argument parsing
# ---------------------------------------------------------------------------

class TestCompareArgParsing:
    """Verify compare subcommand parsing."""

    def test_two_paths_required(self):
        parser = build_parser()
        args = parser.parse_args(["compare", "a.json", "b.json"])
        assert args.log_paths == ["a.json", "b.json"]

    def test_compare_output(self):
        parser = build_parser()
        args = parser.parse_args(["compare", "a.json", "b.json", "-o", "cmp.json"])
        assert args.output == "cmp.json"

    def test_many_paths(self):
        parser = build_parser()
        args = parser.parse_args(["compare", "a.json", "b.json", "c.json", "d.json"])
        assert len(args.log_paths) == 4


# ---------------------------------------------------------------------------
# Test subcommand parsing
# ---------------------------------------------------------------------------

class TestTestArgParsing:
    """Verify test subcommand parsing."""

    def test_log_path_positional(self):
        parser = build_parser()
        args = parser.parse_args(["test", "run_log.json"])
        assert args.log_path == "run_log.json"

    def test_test_output(self):
        parser = build_parser()
        args = parser.parse_args(["test", "run.json", "-o", "report.json"])
        assert args.output == "report.json"


# ---------------------------------------------------------------------------
# generate-plugin alias (Phase 4)
# ---------------------------------------------------------------------------

class TestGeneratePluginAlias:
    """Verify the 'generate-plugin' subcommand maps to export."""

    def test_generate_plugin_parses(self):
        parser = build_parser()
        args = parser.parse_args([
            "generate-plugin",
            "--report", "report.json",
            "--name", "crk-v1",
            "--type", "llm",
            "--locales", "crk",
        ])
        assert args.command == "generate-plugin"
        assert args.report == "report.json"
        assert args.name == "crk-v1"

    def test_generate_plugin_has_all_export_args(self):
        """generate-plugin should support all the same args as export."""
        parser = build_parser()
        args = parser.parse_args([
            "generate-plugin",
            "--report", "r.json",
            "--name", "test",
            "--type", "llm-coached",
            "--locales", "crk,fr",
            "--author", "Test Author",
            "--description", "Test plugin",
            "--version", "2.0.0",
            "--coaching-dir", "/some/dir",
            "--commercial-ready",
        ])
        assert args.type == "llm-coached"
        assert args.locales == "crk,fr"
        assert args.author == "Test Author"
        assert args.plugin_version == "2.0.0"
        assert args.commercial_ready is True


# ---------------------------------------------------------------------------
# --live flag for model discovery (Phase 4)
# ---------------------------------------------------------------------------

class TestListLiveFlag:
    """Verify the --live flag on 'list models'."""

    def test_live_flag_parses(self):
        parser = build_parser()
        args = parser.parse_args(["list", "models", "--live"])
        assert args.live is True

    def test_live_flag_default_false(self):
        parser = build_parser()
        args = parser.parse_args(["list", "models"])
        assert args.live is False

    def test_live_not_available_on_prompts(self):
        """--live is on the list parser, but only useful for models."""
        parser = build_parser()
        args = parser.parse_args(["list", "prompts", "--live"])
        # Parses without error, but live is only used for models
        assert args.live is True

    def test_cmd_list_without_live(self, capsys):
        """Non-live list should work normally."""
        cmd_list("models", live=False)
        out = capsys.readouterr().out
        # Should show registry but NOT attempt OpenRouter fetch
        assert "registry shortcuts" in out.lower()

    def test_cmd_list_with_live_no_key(self, capsys, monkeypatch):
        """Live mode gracefully handles missing API key — real error path."""
        # Remove the env var to simulate no key
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        # Also remove any .env fallback by patching dotenv at the import site
        from unittest.mock import patch
        with patch("dotenv.find_dotenv", return_value=""):
            cmd_list("models", live=True)

        out = capsys.readouterr().out
        assert "cannot fetch" in out.lower() or "api" in out.lower()

    def test_cmd_list_live_formats_table(self, capsys, monkeypatch):
        """Live listing formats model data into a readable table.

        Mocks only the HTTP transport (aiohttp session) — all filtering,
        sorting, and formatting logic runs for real.
        """
        import asyncio
        from unittest.mock import patch, AsyncMock, MagicMock

        # Set a fake API key so load_api_key doesn't fail
        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-123")

        # Build a fake API response with realistic model structure
        fake_models = {
            "data": [
                {
                    "id": "anthropic/claude-sonnet-4",
                    "architecture": {"modality": "text->text"},
                    "pricing": {"prompt": "0.000003", "completion": "0.000015"},
                },
                {
                    "id": "google/gemini-2.5-flash",
                    "architecture": {"modality": "text->text"},
                    "pricing": {"prompt": "0.0000001", "completion": "0.0000004"},
                },
                {
                    "id": "stability/stable-diffusion",
                    "architecture": {"modality": "text->image"},
                    "pricing": {"prompt": "0.000001", "completion": "0"},
                },
            ]
        }

        # Create a mock response that behaves like aiohttp's response
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=fake_models)
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)

        # Create a mock session
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_resp)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            from mt_eval_harness.cli import cmd_list_live
            cmd_list_live()

        out = capsys.readouterr().out
        # Should contain the text-capable models (claude, gemini)
        assert "anthropic/claude-sonnet-4" in out
        assert "google/gemini-2.5-flash" in out
        # Should show pricing columns
        assert "Input $/1M" in out
        assert "Output $/1M" in out

    def test_cmd_list_live_handles_non_200(self, capsys, monkeypatch):
        """Non-200 API responses are reported, not crashed on."""
        import asyncio
        from unittest.mock import patch, AsyncMock, MagicMock

        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-123")

        mock_resp = AsyncMock()
        mock_resp.status = 403
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_resp)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            from mt_eval_harness.cli import cmd_list_live
            cmd_list_live()

        out = capsys.readouterr().out
        assert "403" in out

    def test_cmd_list_live_handles_bad_pricing(self, capsys, monkeypatch):
        """Models with unparseable pricing show '?' instead of crashing."""
        import asyncio
        from unittest.mock import patch, AsyncMock, MagicMock

        monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test-123")

        fake_models = {
            "data": [
                {
                    "id": "test/bad-pricing-model",
                    "architecture": {"modality": "text->text"},
                    "pricing": {"prompt": "not-a-number", "completion": "nope"},
                },
            ]
        }

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=fake_models)
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=False)

        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_resp)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            from mt_eval_harness.cli import cmd_list_live
            cmd_list_live()

        out = capsys.readouterr().out
        assert "test/bad-pricing-model" in out
        assert "?" in out


# ---------------------------------------------------------------------------
# generate_plugin() standalone entry point (Phase 4)
# ---------------------------------------------------------------------------

class TestGeneratePluginEntryPoint:
    """Test the standalone generate_plugin() entry point."""

    def test_injects_subcommand(self, monkeypatch):
        """generate_plugin() rewrites sys.argv to inject 'generate-plugin' subcommand.

        We verify the sys.argv transformation by checking what the parser sees.
        Mock only the final cmd_export to avoid needing a real report file.
        """
        import sys
        from unittest.mock import patch

        # Simulate: `generate-plugin --report r.json --name test --type llm --locales crk`
        monkeypatch.setattr(
            sys, "argv",
            ["generate-plugin", "--report", "r.json", "--name", "test", "--type", "llm", "--locales", "crk"],
        )

        from mt_eval_harness.cli import generate_plugin
        with patch("mt_eval_harness.cli.cmd_export") as mock_export:
            generate_plugin()

        # cmd_export should have been called with the parsed args
        mock_export.assert_called_once()
        call_args = mock_export.call_args[0][0]  # First positional arg
        assert call_args.command == "generate-plugin"
        assert call_args.report == "r.json"
        assert call_args.name == "test"
