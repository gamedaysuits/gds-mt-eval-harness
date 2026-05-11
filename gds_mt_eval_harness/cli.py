"""
CLI Entry Point — Command-line interface for gds-mt-eval-harness.

Provides a clean CLI that maps arguments to RunConfig fields.
Every config parameter is exposed as a CLI flag.

Usage examples:
    # Basic run with defaults
    gds-mt-eval run --corpus data/corpus.json

    # Gold standard segment only
    gds-mt-eval run --corpus data/corpus.json --dataset gold_standard

    # Batch mode, different model
    gds-mt-eval run --corpus data/corpus.json --model claude-sonnet-4 --batch-size 5

    # Specific entries only
    gds-mt-eval run --corpus data/corpus.json --ids 0,1,2,3,4

    # Dry run to validate config
    gds-mt-eval run --corpus data/corpus.json --dry-run

    # Run the test harness on a completed run
    gds-mt-eval test logs/run_20260509_*.json

    # Compare two runs
    gds-mt-eval compare log1.json log2.json

    # Generate dashboard HTML
    gds-mt-eval dashboard logs/run_*.json

    # List available models
    gds-mt-eval list models
"""

import argparse
import asyncio
import os
import sys

from gds_mt_eval_harness.config import (
    RunConfig,
    DEFAULT_MODEL,
    MODEL_REGISTRY,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all harness options."""
    parser = argparse.ArgumentParser(
        prog="gds-mt-eval",
        description="GDS MT Eval Harness — Execute and evaluate translation experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "SUBCOMMANDS:\n"
            "  run       Execute a translation run (default)\n"
            "  test      Analyze a completed run log\n"
            "  compare   Compare multiple run logs\n"
            "  dashboard Generate interactive HTML dashboard\n"
            "  list      List available models, prompts, datasets\n"
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
        choices=["models", "prompts"],
        help="What to list",
    )

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
        default="english",
        help="Field name for source text in corpus. Default: english",
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
        source_field=args.source_field if hasattr(args, "source_field") else "english",
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


def cmd_list(what: str):
    """Handle the 'list' subcommand."""
    if what == "models":
        print("\nAvailable models:")
        for short, full in sorted(MODEL_REGISTRY.items()):
            default = " (default)" if short == DEFAULT_MODEL else ""
            print(f"  {short:25s} → {full}{default}")
        print("\n  You can also pass any full OpenRouter model ID directly.")

    elif what == "prompts":
        print("\nBuilt-in prompt versions:")
        print("  naive    Minimal translation instruction")
        print("  custom   Load from a .txt file (--custom-prompt)")
        print("\n  Register PromptProvider plugins for language-specific prompts.")


def main():
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args.what)
        return

    if args.command == "test":
        from gds_mt_eval_harness.tester import run_test
        run_test(args.log_path, args.output)
        return

    if args.command == "compare":
        from gds_mt_eval_harness.compare import run_compare
        run_compare(args.log_paths, args.output)
        return

    if args.command == "dashboard":
        if getattr(args, "watch", False):
            # Watch mode — poll directory and regenerate on changes
            from gds_mt_eval_harness.watch import watch
            # For watch mode, use first path as directory
            watch(args.log_paths[0], args.output, args.interval)
            return

        from gds_mt_eval_harness.dashboard import load_reports, generate
        reports = load_reports(args.log_paths)
        if not reports:
            print("No report files found.")
            sys.exit(1)
        out = generate(reports, args.output)
        print(f"  Dashboard written to: {out}")
        print(f"  Open in browser: file://{os.path.abspath(out)}")
        return

    # Default: run
    config = args_to_config(args)

    if not config.corpus_path:
        print("ERROR: --corpus is required for the run command.")
        print("  Usage: gds-mt-eval run --corpus <path_to_corpus.json>")
        sys.exit(1)

    from gds_mt_eval_harness.runner import execute_run
    asyncio.run(execute_run(config))


if __name__ == "__main__":
    main()
