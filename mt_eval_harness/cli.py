"""
CLI Entry Point — Command-line interface for mt-eval-harness.

Provides a clean CLI that maps arguments to RunConfig fields.
Every config parameter is exposed as a CLI flag.

The 'export' subcommand packages completed evaluations as rosetta
method plugins (method.json + coaching data).

Usage examples:
    # Basic run with defaults
    mt-eval run --corpus data/corpus.json

    # Gold standard segment only
    mt-eval run --corpus data/corpus.json --dataset gold_standard

    # Batch mode, different model
    mt-eval run --corpus data/corpus.json --model claude-sonnet-4 --batch-size 5

    # Specific entries only
    mt-eval run --corpus data/corpus.json --ids 0,1,2,3,4

    # Dry run to validate config
    mt-eval run --corpus data/corpus.json --dry-run

    # Run the test harness on a completed run
    mt-eval test logs/run_20260509_*.json

    # Compare two runs
    mt-eval compare log1.json log2.json

    # Generate dashboard HTML
    mt-eval dashboard logs/run_*.json

    # List available models or datasets
    mt-eval list models
    mt-eval list datasets

    # Export a TestReport as a rosetta method plugin
    mt-eval export --report eval/logs/report.json --name crk-v1 --type llm-coached --locales crk

    # Same thing using the generate-plugin alias
    mt-eval generate-plugin --report eval/logs/report.json --name crk-v1 --type llm --locales crk

    # List models with live OpenRouter catalog
    mt-eval list models --live
"""

import argparse
import asyncio
import os
import sys

from mt_eval_harness.config import (
    RunConfig,
    DEFAULT_MODEL,
    MODEL_REGISTRY,
    format_registry_table,
    load_method_card,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all harness options."""
    parser = argparse.ArgumentParser(
        prog="mt-eval",
        description="MT Eval Harness — Execute and evaluate translation experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "SUBCOMMANDS:\n"
            "  run              Execute a translation run (default)\n"
            "  test             Analyze a completed run log\n"
            "  compare          Compare multiple run logs\n"
            "  dashboard        Generate interactive HTML dashboard\n"
            "  list             List available models, prompts, datasets\n"
            "  export           Package a TestReport as a rosetta method plugin\n"
            "  generate-plugin  Alias for 'export'\n"
        ),
    )

    sub = parser.add_subparsers(dest="command", help="Subcommand")

    # --- RUN command ---
    run_p = sub.add_parser("run", help="Execute a translation run")
    _add_run_args(run_p)

    # Default command (no subcommand = run)
    _add_run_args(parser)

    # --- TEST command ---
    test_p = sub.add_parser("test", help="Analyze a completed run log")
    test_p.add_argument("log_path", help="Path to RunLog JSON file")
    test_p.add_argument(
        "-o", "--output",
        help="Output path for test report (default: alongside log file)",
    )

    # --- COMPARE command ---
    cmp_p = sub.add_parser("compare", help="Compare multiple run logs")
    cmp_p.add_argument("log_paths", nargs="+", help="Paths to RunLog JSON files")
    cmp_p.add_argument(
        "-o", "--output",
        help="Output path for comparison report",
    )
    cmp_p.add_argument(
        "--significance",
        action="store_true",
        help="Run paired bootstrap significance tests between runs",
    )
    cmp_p.add_argument(
        "--n-bootstrap",
        type=int,
        default=1000,
        help="Number of bootstrap iterations for significance testing. Default: 1000",
    )

    # --- DASHBOARD command ---
    dash_p = sub.add_parser("dashboard", help="Generate interactive HTML dashboard")
    dash_p.add_argument("log_paths", nargs="+", help="Paths to RunLog JSON files or directories")
    dash_p.add_argument(
        "-o", "--output",
        default="dashboard_output.html",
        help="Output HTML file path",
    )
    dash_p.add_argument(
        "--watch",
        action="store_true",
        help="Watch directory for new/changed reports and auto-regenerate",
    )
    dash_p.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Watch polling interval in seconds. Default: 5",
    )

    # --- LIST command ---
    list_p = sub.add_parser("list", help="List available models, prompts, datasets")
    list_p.add_argument(
        "what",
        choices=["models", "prompts", "datasets"],
        help="What to list",
    )
    list_p.add_argument(
        "--live",
        action="store_true",
        help="Fetch live model catalog from OpenRouter (requires API key)",
    )

    # --- EXPORT command ---
    export_p = sub.add_parser(
        "export",
        help="Package a TestReport as a rosetta method plugin",
    )
    _add_export_args(export_p)

    # --- GENERATE-PLUGIN alias (maps to export) ---
    gp_p = sub.add_parser(
        "generate-plugin",
        help="Alias for 'export' — package a TestReport as a rosetta method plugin",
    )
    _add_export_args(gp_p)

    return parser


def _add_run_args(parser: argparse.ArgumentParser):
    """Add run-specific arguments to a parser."""
    # Corpus (required for run)
    parser.add_argument(
        "--corpus",
        help="Path to the corpus JSON file (required for run)",
    )

    # Dataset
    parser.add_argument(
        "-d", "--dataset",
        default="all",
        help="Dataset filter. Options: 'all', segment name, ID range ('0-61'), "
             "or single ID. Default: all",
    )
    parser.add_argument(
        "--ids",
        help="Comma-separated entry IDs to evaluate (overrides --dataset)",
    )

    # Source/target fields
    parser.add_argument(
        "--source-field",
        default="source",
        help="Field name for source text in corpus. Default: source",
    )
    parser.add_argument(
        "--target-field",
        default="target",
        help="Field name for reference translation in corpus. Default: target",
    )

    # Model
    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        help=f"Model short name or full OpenRouter ID. Default: {DEFAULT_MODEL}. "
             f"Available shortcuts: {', '.join(sorted(MODEL_REGISTRY.keys()))}",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=13680,
        help="Max tokens per API call. Default: 13680",
    )

    # Tools
    parser.add_argument(
        "--tools",
        action="store_true",
        help="Enable tool-calling (requires batch_size=1)",
    )
    parser.add_argument(
        "--tools-list",
        help="Comma-separated tool names (requires --tools)",
    )
    parser.add_argument(
        "--max-tool-rounds",
        type=int,
        default=8,
        help="Max tool-calling rounds per entry. Default: 8",
    )

    # Post-hooks
    parser.add_argument(
        "--hooks",
        help="Comma-separated post-translation hook names to apply",
    )

    # Caching
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching (re-run all entries)",
    )
    parser.add_argument(
        "--cache-dir",
        default="eval/cache/harness",
        help="Cache directory. Default: eval/cache/harness",
    )

    # Batching
    parser.add_argument(
        "-b", "--batch-size",
        type=int,
        default=1,
        help="Entries per API call. Default: 1",
    )

    # Concurrency
    parser.add_argument(
        "-c", "--concurrency",
        type=int,
        default=8,
        help="Parallel API calls. Default: 8",
    )

    # Prompt
    parser.add_argument(
        "-p", "--prompt",
        default="naive",
        help="System prompt version. Built-in: naive, custom. "
             "Plugin versions registered via PromptProvider. Default: naive",
    )
    parser.add_argument(
        "--custom-prompt",
        help="Path to custom system prompt .txt file (use with --prompt custom)",
    )

    # Output
    parser.add_argument(
        "-o", "--output-dir",
        default="eval/logs/harness",
        help="Output directory for RunLog. Default: eval/logs/harness",
    )
    parser.add_argument(
        "-n", "--name",
        help="Human-readable run name (appended to run ID)",
    )

    # Misc
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature. Default: 0.0 (deterministic)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config without making API calls",
    )

    # Method card
    parser.add_argument(
        "--method-card",
        help="Path to a method card JSON file (see docs/method-card-spec.md). "
             "Embeds the method description in the run card for leaderboard display.",
    )


def args_to_config(args) -> RunConfig:
    """Convert parsed CLI args to a RunConfig."""
    entry_ids = None
    if hasattr(args, "ids") and args.ids:
        entry_ids = [int(x.strip()) for x in args.ids.split(",")]

    tools_list = None
    if hasattr(args, "tools_list") and args.tools_list:
        tools_list = [t.strip() for t in args.tools_list.split(",")]

    post_hooks = []
    if hasattr(args, "hooks") and args.hooks:
        post_hooks = [h.strip() for h in args.hooks.split(",")]

    return RunConfig(
        dataset=args.dataset,
        entry_ids=entry_ids,
        corpus_path=args.corpus if hasattr(args, "corpus") else None,
        source_field=args.source_field if hasattr(args, "source_field") else "source",
        target_field=args.target_field if hasattr(args, "target_field") else "target",
        model=args.model,
        max_tokens=args.max_tokens,
        tools_enabled=args.tools if hasattr(args, "tools") else False,
        tools_list=tools_list,
        max_tool_rounds=args.max_tool_rounds if hasattr(args, "max_tool_rounds") else 8,
        cache_enabled=not (args.no_cache if hasattr(args, "no_cache") else False),
        cache_dir=args.cache_dir if hasattr(args, "cache_dir") else "eval/cache/harness",
        batch_size=args.batch_size if hasattr(args, "batch_size") else 1,
        concurrency=args.concurrency if hasattr(args, "concurrency") else 8,
        prompt_version=args.prompt if hasattr(args, "prompt") else "naive",
        custom_prompt_path=args.custom_prompt if hasattr(args, "custom_prompt") else None,
        post_hooks=post_hooks,
        output_dir=args.output_dir if hasattr(args, "output_dir") else "eval/logs/harness",
        run_name=args.name if hasattr(args, "name") else None,
        temperature=args.temperature if hasattr(args, "temperature") else 0.0,
        dry_run=args.dry_run if hasattr(args, "dry_run") else False,
    )


def cmd_list(what: str, live: bool = False):
    """Handle the 'list' subcommand."""
    if what == "models":
        print("\nAvailable models (registry shortcuts):")
        for short, full in sorted(MODEL_REGISTRY.items()):
            default = " (default)" if short == DEFAULT_MODEL else ""
            print(f"  {short:25s} → {full}{default}")
        print("\n  You can also pass any full OpenRouter model ID directly.")

        if live:
            cmd_list_live()

    elif what == "prompts":
        print("\nBuilt-in prompt versions:")
        print("  naive    Minimal translation instruction")
        print("  custom   Load from a .txt file (--custom-prompt)")
        print("\n  Register PromptProvider plugins for language-specific prompts.")

    elif what == "datasets":
        print(format_registry_table())


def cmd_list_live():
    """Fetch and display live model catalog from OpenRouter.

    Queries the OpenRouter /api/v1/models endpoint and displays
    all available models with their pricing. Requires an API key
    (via OPENROUTER_API_KEY env var or .env file).
    """
    import asyncio

    try:
        import aiohttp
    except ImportError:
        print("\n  aiohttp is required for live model listing.")
        print("  Install: pip install aiohttp")
        return

    from mt_eval_harness.api import load_api_key, OPENROUTER_MODELS_URL

    try:
        api_key = load_api_key()
    except RuntimeError as e:
        print(f"\n  Cannot fetch live models: {e}")
        return

    async def _fetch():
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                OPENROUTER_MODELS_URL,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    print(f"\n  OpenRouter API returned {resp.status}")
                    return
                data = await resp.json()
                models = data.get("data", [])

                # Filter to text-capable models, sort by ID
                text_models = [
                    m for m in models
                    if "text" in str(m.get("architecture", {}).get("modality", ""))
                    or "chat" in str(m.get("architecture", {}).get("modality", ""))
                    or not m.get("architecture", {}).get("modality")  # Permissive fallback
                ]
                text_models.sort(key=lambda m: m.get("id", ""))

                print(f"\n  Live catalog — {len(text_models)} models available on OpenRouter:")
                print(f"  {'Model ID':55s} {'Input $/1M':>10s} {'Output $/1M':>11s}")
                print(f"  {'-'*55} {'-'*10} {'-'*11}")

                for m in text_models:
                    mid = m.get("id", "?")
                    pricing = m.get("pricing", {})
                    try:
                        inp = float(pricing.get("prompt", "0")) * 1_000_000
                        out = float(pricing.get("completion", "0")) * 1_000_000
                        print(f"  {mid:55s} ${inp:>8.2f} ${out:>9.2f}")
                    except (ValueError, TypeError):
                        print(f"  {mid:55s} {'?':>10s} {'?':>11s}")

                print(f"\n  Pass any model ID above with: mt-eval run -m <model-id>")

    asyncio.run(_fetch())


def _add_export_args(parser: argparse.ArgumentParser):
    """Add export-specific arguments to the export subcommand parser."""
    # Required
    parser.add_argument(
        "--report",
        required=True,
        help="Path to TestReport JSON file (from 'mt-eval test')",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Plugin name in kebab-case (e.g., 'crk-coached-v1')",
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=["llm", "llm-coached", "api", "google-translate"],
        help="Method type (must match rosetta's valid types)",
    )
    parser.add_argument(
        "--locales",
        required=True,
        help="Comma-separated target locale codes (e.g., 'crk' or 'fr,de,es')",
    )

    # Optional
    parser.add_argument(
        "--description",
        default="",
        help="Human-readable plugin description",
    )
    parser.add_argument(
        "--author",
        default="",
        help="Plugin author (e.g., 'Your Name or Org')",
    )
    parser.add_argument(
        "--register",
        default="",
        help="Target language register/tone (e.g., 'Standard written register')",
    )
    parser.add_argument(
        "--coaching-dir",
        help="Path to coaching data directory to bundle (e.g., '.rosetta/coaching')",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default=".",
        help="Output directory for the plugin. Default: current directory",
    )
    parser.add_argument(
        "--version",
        dest="plugin_version",
        default="1.0.0",
        help="Semver version string. Default: '1.0.0'",
    )
    parser.add_argument(
        "--commercial-ready",
        action="store_true",
        help=(
            "Mark this plugin as licensed and cleared for publishing. "
            "Default: false (license-unclear). Set when the method's "
            "resources have been verified for commercial distribution."
        ),
    )


def cmd_export(args):
    """Handle the 'export' subcommand."""
    from mt_eval_harness.exporter import ExportConfig, export_plugin

    locales = [l.strip() for l in args.locales.split(",")]

    config = ExportConfig(
        name=args.name,
        method_type=args.type,
        locales=locales,
        version=args.plugin_version,
        description=args.description,
        author=args.author,
        register=args.register,
        coaching_dir=args.coaching_dir,
        output_dir=args.output_dir,
        commercial_ready=args.commercial_ready,
    )

    try:
        export_plugin(args.report, config)
    except (FileNotFoundError, ValueError) as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def main():
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args.what, live=getattr(args, "live", False))
        return

    if args.command == "test":
        from mt_eval_harness.tester import run_test
        run_test(args.log_path, args.output)
        return

    if args.command == "compare":
        from mt_eval_harness.compare import run_compare
        run_compare(
            args.log_paths,
            args.output,
            significance=getattr(args, "significance", False),
            n_bootstrap=getattr(args, "n_bootstrap", 1000),
        )
        return

    if args.command == "dashboard":
        if getattr(args, "watch", False):
            # Watch mode — poll directory and regenerate on changes
            from mt_eval_harness.watch import watch
            # For watch mode, use first path as directory
            watch(args.log_paths[0], args.output, args.interval)
            return

        from mt_eval_harness.dashboard import load_reports, generate
        reports = load_reports(args.log_paths)
        if not reports:
            print("No report files found.")
            sys.exit(1)
        out = generate(reports, args.output)
        print(f"  Dashboard written to: {out}")
        print(f"  Open in browser: file://{os.path.abspath(out)}")
        return

    if args.command in ("export", "generate-plugin"):
        cmd_export(args)
        return

    # Default: run
    config = args_to_config(args)

    if not config.corpus_path:
        print("ERROR: --corpus is required for the run command.")
        print("  Usage: mt-eval run --corpus <path_to_corpus.json>")
        sys.exit(1)

    from mt_eval_harness.runner import execute_run
    asyncio.run(execute_run(config))


if __name__ == "__main__":
    main()


def generate_plugin():
    """Standalone entry point for the 'generate-plugin' command.

    Injects 'generate-plugin' as the subcommand so users can invoke
    this as a bare shell command: `generate-plugin --report ...`
    instead of `mt-eval generate-plugin --report ...`.
    """
    sys.argv = ["mt-eval", "generate-plugin"] + sys.argv[1:]
    main()
