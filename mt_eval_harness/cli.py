"""
CLI Entry Point — Command-line interface for mt-eval-harness.

Provides a clean CLI that maps arguments to RunConfig fields.
Every config parameter is exposed as a CLI flag.

The 'export' subcommand packages completed evaluations as champollion
method plugins (method.json + coaching data).

┌──────────────────────────────────────────────────────────────┐
│  DEFAULT BEHAVIOR — The harness is "fast by default":           │
│    batch_size=25, max_tokens=32768, concurrency=8, cache=on    │
│                                                                │
│  For multi-model runs, pass comma-separated models:            │
│    mt-eval run --corpus data.json -m model1,model2,model3      │
│  All models run in parallel via asyncio.gather.                │
└──────────────────────────────────────────────────────────────┘

Usage examples:
    # Basic run with optimal defaults (batch=25, cache=on, tokens=32k)
    mt-eval run --corpus data/corpus.json

    # Multi-model parallel run
    mt-eval run --corpus data/corpus.json -m gemini-3.1-pro,claude-opus-4.7,gpt-5.5

    # Gold standard segment only
    mt-eval run --corpus data/corpus.json --dataset gold_standard

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

    # Export a TestReport as a champollion method plugin
    mt-eval export --report eval/logs/report.json --name crk-v1 --type llm-coached --locales crk

    # List models with live OpenRouter catalog
    mt-eval list models --live
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

from mt_eval_harness.config import (
    RunConfig,
    DEFAULT_MODEL,
    DEFAULT_BATCH_SIZE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_CONCURRENCY,
    DEFAULT_CACHE_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_MAX_TOOL_ROUNDS,
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
            "  queue            Run the top of the community compute queue\n"
            "  test             Analyze a completed run log\n"
            "  publish          Submit a TestReport to the leaderboard\n"
            "  compare          Compare multiple run logs\n"
            "  dashboard        Generate interactive HTML dashboard\n"
            "  list             List available models, prompts, datasets\n"
            "  setup            Install optional dependencies (COMET, FST)\n"
            "  export           Package a TestReport as a champollion method plugin\n"
            "  export-config    Generate a champollion.config.json snippet from a TestReport\n"
            "  generate-plugin  Alias for 'export'\n"
            "  card               Pretty-print a human-readable run card\n"
            "  contest          Manage evaluation contests (create, submit, list)\n"
            "  logout           Remove stored auth credentials\n"
        ),
    )

    sub = parser.add_subparsers(dest="command", help="Subcommand")

    # --- CARD command ---
    card_p = sub.add_parser("card", help="Pretty-print a human-readable run card")
    card_p.add_argument("log_paths", nargs="+", help="Run log JSON file(s) to render")

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
    test_p.add_argument(
        "--no-ci",
        action="store_true",
        help="Skip bootstrap confidence interval computation (faster)",
    )
    test_p.add_argument(
        "--n-bootstrap-ci",
        type=int,
        default=1000,
        help="Number of bootstrap iterations for CIs. Default: 1000 "
             "(matches SacreBLEU/WMT convention). Higher = more precise but slower.",
    )
    test_p.add_argument(
        "--skip-fst",
        action="store_true",
        help="Skip FST quality gate. Runs eval without morphological validation "
             "even if an FST is available for the target language. Use in CI or "
             "when FST install is not possible.",
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

    # --- QUEUE command ---
    queue_p = sub.add_parser(
        "queue",
        help="Run the top of the community compute queue with your own key",
        description=(
            "Execute open items from the public queue "
            "(champollion.dev/queue.json), which is ranked by expected "
            "chain value — mesh improvement per estimated dollar. Items "
            "run in queue order; the plan and estimated spend are shown "
            "and confirmed before anything is executed. Results are "
            "auto-published after each run (pass --no-publish to skip)."
        ),
    )
    from mt_eval_harness.queue_runner import add_queue_arguments
    add_queue_arguments(queue_p)

    # --- PUBLISH command ---
    pub_p = sub.add_parser(
        "publish",
        help="Submit a TestReport to the leaderboard",
    )
    pub_p.add_argument(
        "report_path",
        help="Path to a TestReport JSON file (output of 'mt-eval test')",
    )
    pub_p.add_argument(
        "--method-card",
        help="Path to a method card JSON file to attach to the submission",
    )
    pub_p.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompt (required for scripted/batch publishing)",
    )

    # --- CONTEST command ---
    contest_p = sub.add_parser(
        "contest",
        help="Manage evaluation contests (create, submit, list)",
    )
    contest_sub = contest_p.add_subparsers(
        dest="contest_command",
        help="Contest subcommand",
    )

    # contest create
    cc = contest_sub.add_parser("create", help="Create a new evaluation contest")
    cc.add_argument("--name", required=True, help="Contest name (e.g. 'EN→CRK Open')")
    cc.add_argument(
        "--corpus", required=True,
        help="Corpus file or dataset ID to evaluate against",
    )
    cc.add_argument(
        "--language-pair", required=True,
        help="Language pair (e.g. 'en>crk', 'es>que')",
    )
    cc.add_argument(
        "--visibility", choices=["public", "private", "team"],
        default="public",
        help="Access mode. public: anyone; private: visible but scores hidden; "
             "team: invite-only. Default: public",
    )
    cc.add_argument(
        "--teams",
        help="Comma-separated team slugs (required for --visibility team)",
    )
    cc.add_argument(
        "--description", default="",
        help="Human-readable contest description",
    )

    # contest submit
    cs = contest_sub.add_parser("submit", help="Submit a run to a contest")
    cs.add_argument(
        "--contest", required=True,
        help="Contest slug (e.g. 'en-crk-open-2026')",
    )
    cs.add_argument(
        "--run", required=True,
        help="Path to TestReport JSON or a run_card_id",
    )
    cs.add_argument("--team", help="Team attribution")
    cs.add_argument("--notes", default="", help="Submission notes")

    # contest list
    cl = contest_sub.add_parser("list", help="List active contests")
    cl.add_argument(
        "--status", choices=["open", "closed", "all"], default="open",
        help="Filter by status. Default: open",
    )
    cl.add_argument(
        "--language-pair",
        help="Filter by language pair (e.g. 'en>crk')",
    )

    # contest submissions (view submissions for a contest)
    csub = contest_sub.add_parser(
        "submissions", help="List submissions for a contest",
    )
    csub.add_argument("contest_id", help="Contest slug")

    # --- LOGOUT command ---
    sub.add_parser(
        "logout",
        help="Remove stored authentication credentials",
    )

    # --- SETUP command ---
    setup_p = sub.add_parser(
        "setup",
        help="Install optional dependencies (COMET neural metric, FST runtime)",
    )
    setup_p.add_argument(
        "--all",
        action="store_true",
        help="Install all optional dependencies without prompts",
    )
    setup_p.add_argument(
        "--comet",
        action="store_true",
        help="Install COMET neural metric (unbabel-comet)",
    )
    setup_p.add_argument(
        "--fst",
        action="store_true",
        help="Install FST runtime (pyhfst) for morphological validation",
    )
    setup_p.add_argument(
        "--status",
        action="store_true",
        help="Show what's currently installed",
    )
    setup_p.add_argument(
        "--lang",
        metavar="CODE",
        help="Install eval pack for a specific language (e.g., --lang crk, --lang sme)",
    )

    # --- EXPORT command ---
    export_p = sub.add_parser(
        "export",
        help="Package a TestReport as a champollion method plugin",
    )
    _add_export_args(export_p)

    # --- GENERATE-PLUGIN alias (maps to export) ---
    gp_p = sub.add_parser(
        "generate-plugin",
        help="Alias for 'export' — package a TestReport as a champollion method plugin",
    )
    _add_export_args(gp_p)

    # --- EXPORT-CONFIG command ---
    ec_p = sub.add_parser(
        "export-config",
        help="Generate a champollion.config.json snippet from a TestReport",
    )
    ec_p.add_argument(
        "--report",
        required=True,
        help="Path to a TestReport JSON file (output of 'mt-eval test')",
    )
    ec_p.add_argument(
        "--target-lang-code",
        required=True,
        help="BCP-47 language code (e.g., 'crk', 'fr')",
    )
    ec_p.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)",
    )

    return parser


def _add_run_args(parser: argparse.ArgumentParser):
    """Add run-specific arguments to a parser."""
    # Corpus (required for run)
    parser.add_argument(
        "--corpus",
        help="Path to corpus file (.json, .jsonl, or .tsv). "
             "For parallel text files (FLORES+, WMT, NTREX), use "
             "--source-file and --reference-file instead.",
    )
    parser.add_argument(
        "--source-file",
        help="Path to source text file (one sentence per line). "
             "Use with --reference-file for parallel text corpora.",
    )
    parser.add_argument(
        "--reference-file",
        help="Path to reference text file (aligned by line number). "
             "Use with --source-file for parallel text corpora.",
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
        default="reference",
        help="Field name for reference translation in corpus. Default: reference",
    )

    # Language pair — used in prompts and run cards
    parser.add_argument(
        "--source-lang",
        default="",
        help="Source language name (auto-detected from config if empty)",
    )
    parser.add_argument(
        "--target-lang",
        default="",
        help="Target language name (used in prompt). e.g. 'Plains Cree (nêhiyawêwin, SRO)'",
    )

    # Model
    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        help=f"Model short name, full OpenRouter ID, or comma-separated list "
             f"for parallel multi-model runs. Default: {DEFAULT_MODEL}. "
             f"Shortcuts: {', '.join(sorted(MODEL_REGISTRY.keys()))}",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=f"Max tokens per API call. Default: {DEFAULT_MAX_TOKENS} "
             f"(generous headroom — translation outputs are short, "
             f"unused tokens cost nothing).",
    )

    # API provider
    parser.add_argument(
        "--provider",
        default="openrouter",
        choices=["openrouter", "openai", "anthropic", "gemini"],
        help="LLM API provider. 'openrouter' (default) proxies any model. "
             "Direct providers call vendor APIs without a proxy.",
    )

    # Tools
    parser.add_argument(
        "--tools",
        action="store_true",
        help="Enable tool-calling (batch_size auto-overrides to 1)",
    )
    parser.add_argument(
        "--tools-list",
        help="Comma-separated tool names (requires --tools)",
    )
    parser.add_argument(
        "--max-tool-rounds",
        type=int,
        default=DEFAULT_MAX_TOOL_ROUNDS,
        help=f"Max tool-calling rounds per entry. Default: {DEFAULT_MAX_TOOL_ROUNDS}",
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
        help="Disable caching (re-run all entries). NOT recommended.",
    )
    parser.add_argument(
        "--cache-dir",
        default=DEFAULT_CACHE_DIR,
        help=f"Cache directory. Default: {DEFAULT_CACHE_DIR}",
    )

    # Batching
    parser.add_argument(
        "-b", "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Entries per API call. Default: {DEFAULT_BATCH_SIZE} "
             f"(25× fewer API calls than batch_size=1). "
             f"Auto-overrides to 1 when --tools is set.",
    )

    # Concurrency
    parser.add_argument(
        "-c", "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Parallel API calls per model. Default: {DEFAULT_CONCURRENCY}. "
             f"For multi-model parallelism, pass multiple models with -m.",
    )

    # Prompt / Coaching
    # Coaching prompts are free text — the full text is recorded in the
    # run card for reproducibility. There are no named prompt versions.
    parser.add_argument(
        "-p", "--prompt",
        default="naive",
        help="System prompt version. Built-in: naive, custom. "
             "Use --coaching-file for custom coaching prompts. Default: naive",
    )
    parser.add_argument(
        "--coaching-file",
        help="Path to coaching prompt text file. The full text is recorded "
             "in the run card for reproducibility, and the run's condition "
             "is labelled 'coached' unless --prompt is set explicitly.",
    )
    parser.add_argument(
        "--coaching",
        help="Inline coaching text (for short prompts). Mutually exclusive "
             "with --coaching-file.",
    )
    parser.add_argument(
        "--custom-prompt",
        help=argparse.SUPPRESS,  # DEPRECATED: hidden, use --coaching-file
    )

    # Writing style
    parser.add_argument(
        "--style-profile",
        help="Path to a style profile JSON for brand voice analysis. "
             "Enables writing style consistency metrics (informational, "
             "not in composite score). See docs for format.",
    )

    # Output
    parser.add_argument(
        "-o", "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory for RunLog. Default: {DEFAULT_OUTPUT_DIR}",
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
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompts (e.g. accept the upstream data "
             "license when a missing corpus is fetched from source). "
             "Required for non-interactive/CI runs that trigger a fetch.",
    )

    # Method card
    parser.add_argument(
        "--method-card",
        help="Path to a method card JSON file (see docs/method-card-spec.md). "
             "Embeds the method description in the run card for leaderboard display.",
    )

    # Method plugin
    parser.add_argument(
        "--method",
        help="Path to a method plugin directory containing method.json + Python "
             "module. When set, the harness delegates translation to the plugin. "
             "Model, prompt, batch size, and tool flags are ignored.",
    )

    # FST retry
    parser.add_argument(
        "--fst-retries",
        type=int,
        default=0,
        help="Number of times to retry translations that fail FST validation. "
             "Default: 0 (score-only, no retry). Works with the default LLM method "
             "only — custom method plugins handle their own retries.",
    )

    # Champollion config interop
    parser.add_argument(
        "--champollion-config",
        help="Path to champollion.config.json. Enables --prompt champollion "
             "with production-identical register, gender guidance, and promptContext.",
    )
    parser.add_argument(
        "--champollion-cards-dir",
        help="Path to language-cards directory (default: auto-detect from "
             "monorepo layout or node_modules/champollion/).",
    )
    parser.add_argument(
        "--target-lang-code",
        default="",
        help="BCP-47 language code for target language (e.g., 'fr', 'de', 'crk'). "
             "Required when using --champollion-config.",
    )
    parser.add_argument(
        "--skip-fst",
        action="store_true",
        help="Skip FST quality gate. Runs eval without morphological validation "
             "even if an FST is available for the target language.",
    )


def args_to_config(args) -> RunConfig:
    """Convert parsed CLI args to a RunConfig."""
    entry_ids = None
    if hasattr(args, "ids") and args.ids:
        # Corpus ids are ints in some corpora (EdTeKLA) and strings in
        # others (Tatoeba: 'tatoeba_2289') — accept both. The loader
        # matches string-normalized, so the int/str distinction here is
        # cosmetic.
        entry_ids = [
            int(x.strip()) if x.strip().lstrip("-").isdigit() else x.strip()
            for x in args.ids.split(",")
        ]

    tools_list = None
    if hasattr(args, "tools_list") and args.tools_list:
        tools_list = [t.strip() for t in args.tools_list.split(",")]

    post_hooks = []
    if hasattr(args, "hooks") and args.hooks:
        post_hooks = [h.strip() for h in args.hooks.split(",")]

    # Resolve coaching file path.
    # --coaching-file is the modern flag; --custom-prompt is the deprecated alias.
    # If both are provided, --coaching-file wins.
    coaching_file = getattr(args, "coaching_file", None)
    custom_prompt = getattr(args, "custom_prompt", None)
    if coaching_file is None and custom_prompt is not None:
        # Backward compat: treat --custom-prompt as --coaching-file
        coaching_file = custom_prompt

    # If --coaching (inline text) is provided, write it to a temp file
    # so it flows through the same coaching_file path.
    coaching_inline = getattr(args, "coaching", None)
    if coaching_inline and coaching_file is None:
        import tempfile
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, prefix="coaching_"
        )
        tmp.write(coaching_inline)
        tmp.close()
        coaching_file = tmp.name

    # Condition label: coaching replaces the naive system prompt at runtime
    # (runner.load_system_prompt gives coaching_file precedence), so a run
    # with coaching but the default -p would otherwise be recorded — and
    # published — as condition "naive". Relabel it "coached" unless the user
    # explicitly chose a prompt version.
    prompt_version = args.prompt if hasattr(args, "prompt") else "naive"
    if coaching_file and prompt_version == "naive":
        prompt_version = "coached"

    return RunConfig(
        dataset=args.dataset,
        entry_ids=entry_ids,
        corpus_path=args.corpus if hasattr(args, "corpus") else None,
        source_file=args.source_file if hasattr(args, "source_file") else None,
        reference_file=args.reference_file if hasattr(args, "reference_file") else None,
        source_field=args.source_field if hasattr(args, "source_field") else "source",
        target_field=args.target_field if hasattr(args, "target_field") else "reference",
        source_lang=args.source_lang if hasattr(args, "source_lang") else "English",
        target_lang=args.target_lang if hasattr(args, "target_lang") else "",
        model=args.model,
        max_tokens=args.max_tokens,
        provider=getattr(args, "provider", "openrouter"),
        tools_enabled=args.tools if hasattr(args, "tools") else False,
        tools_list=tools_list,
        max_tool_rounds=args.max_tool_rounds if hasattr(args, "max_tool_rounds") else DEFAULT_MAX_TOOL_ROUNDS,
        cache_enabled=not (args.no_cache if hasattr(args, "no_cache") else False),
        cache_dir=args.cache_dir if hasattr(args, "cache_dir") else DEFAULT_CACHE_DIR,
        batch_size=args.batch_size if hasattr(args, "batch_size") else DEFAULT_BATCH_SIZE,
        concurrency=args.concurrency if hasattr(args, "concurrency") else DEFAULT_CONCURRENCY,
        prompt_version=prompt_version,
        custom_prompt_path=custom_prompt,  # Legacy field
        coaching_file=coaching_file,
        style_profile=getattr(args, "style_profile", None),
        post_hooks=post_hooks,
        fst_retries=getattr(args, "fst_retries", 0),
        output_dir=args.output_dir if hasattr(args, "output_dir") else DEFAULT_OUTPUT_DIR,
        run_name=args.name if hasattr(args, "name") else None,
        temperature=args.temperature if hasattr(args, "temperature") else 0.0,
        dry_run=args.dry_run if hasattr(args, "dry_run") else False,
        assume_yes=getattr(args, "yes", False),
        method_path=getattr(args, "method", None),
        champollion_config_path=args.champollion_config if hasattr(args, "champollion_config") else None,
        champollion_cards_dir=args.champollion_cards_dir if hasattr(args, "champollion_cards_dir") else None,
        target_lang_code=args.target_lang_code if hasattr(args, "target_lang_code") else "",
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
        print("\nPrompt options:")
        print("  naive    Minimal translation instruction (default)")
        print("  custom   Load from a .txt file (DEPRECATED — use --coaching-file)")
        print("  champollion  Production-identical prompt from champollion.config.json")
        print("           (requires --champollion-config and --target-lang-code)")
        print("\n  Coaching prompts (recommended):")
        print("    --coaching-file path.txt   Load coaching prompt from file")
        print("    --coaching 'text'          Inline coaching text (short prompts)")
        print("\n  The full coaching text is recorded in the run card for reproducibility,")
        print("  and the run's condition is labelled 'coached' automatically (override")
        print("  with an explicit --prompt).")

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
        help="Method type (must match champollion's valid types)",
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
        help="Path to coaching data directory to bundle (e.g., '.champollion/coaching')",
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


# ---------------------------------------------------------------------------
# Publish prompt — shared by run and test commands
# ---------------------------------------------------------------------------

def _prompt_publish(report_path) -> None:
    """Offer to publish a report to the arena leaderboard.

    Only prompts in interactive mode (TTY stdin). In non-interactive
    environments (piped stdin, CI), silently skips with a hint.
    """
    from pathlib import Path
    report_path = Path(report_path)
    if not report_path.exists():
        return

    if not sys.stdin.isatty():
        # Non-interactive — just print the command for reference
        print(f"  → To publish: mt-eval publish {report_path.name}")
        return

    print()
    try:
        answer = input("  → Publish this run to the arena? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if answer in ("y", "yes"):
        try:
            from mt_eval_harness.publish import publish_to_supabase
            publish_to_supabase(str(report_path), auto_confirm=True)
        except Exception as e:
            print(f"  ✗ Publish failed: {e}")
            print(f"  → Retry with: mt-eval publish {report_path.name}")


def main():
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args.what, live=getattr(args, "live", False))
        return

    if args.command == "card":
        from mt_eval_harness.run_card import render_run_card
        from pathlib import Path
        for filepath in args.log_paths:
            path = Path(filepath)
            if path.name.endswith("_report.json"):
                continue  # Skip report files — auto-detected from run log
            if not path.exists():
                print(f"  ✗ File not found: {filepath}", file=sys.stderr)
                continue
            print(render_run_card(path))
        return

    if args.command == "test":
        from mt_eval_harness.tester import run_test
        from mt_eval_harness.plugin_discovery import discover_metric_plugins
        from pathlib import Path
        import json

        # Load the run log to detect target language for plugin auto-discovery
        log_path = Path(args.log_path)
        log_data = json.loads(log_path.read_text(encoding="utf-8"))
        metric_plugins = discover_metric_plugins(
            log_data.get("config", {}),
            skip_fst=getattr(args, "skip_fst", False),
            method_dir=log_data.get("config", {}).get("method_path"),
        )

        run_test(
            args.log_path,
            args.output,
            metric_plugins=metric_plugins or None,
            compute_ci=not getattr(args, "no_ci", False),
            n_bootstrap_ci=getattr(args, "n_bootstrap_ci", 1000),
        )

        # Auto-print the run card after scoring
        report_path = log_path.with_name(log_path.stem + "_report.json")
        try:
            from mt_eval_harness.run_card import render_run_card
            print(render_run_card(log_path, report_path))
        except Exception as e:
            logger.warning("Failed to render run card: %s", e)

        # Offer to publish to the arena (interactive only)
        _prompt_publish(report_path)
        return

    if args.command == "queue":
        from mt_eval_harness.queue_runner import run_from_args
        sys.exit(run_from_args(args))

    if args.command == "publish":
        from mt_eval_harness.publish import publish_to_supabase
        publish_to_supabase(
            args.report_path,
            method_card_path=getattr(args, "method_card", None),
            auto_confirm=getattr(args, "yes", False),
        )
        return

    if args.command == "contest":
        from mt_eval_harness.contest import (
            create_contest, submit_to_contest,
            list_contests, list_submissions,
            resolve_run_card_id,
        )

        if args.contest_command == "create":
            teams = None
            if getattr(args, "teams", None):
                teams = [t.strip() for t in args.teams.split(",")]
            create_contest(
                name=args.name,
                corpus_id=args.corpus,
                language_pair=getattr(args, "language_pair", "en>crk"),
                visibility=args.visibility,
                teams=teams,
                description=getattr(args, "description", ""),
            )
        elif args.contest_command == "submit":
            run_card_id = resolve_run_card_id(args.run)
            submit_to_contest(
                contest_id=args.contest,
                run_card_id=run_card_id,
                team=getattr(args, "team", None),
                notes=getattr(args, "notes", ""),
            )
        elif args.contest_command == "list":
            list_contests(
                status=getattr(args, "status", "open"),
                language_pair=getattr(args, "language_pair", None),
            )
        elif args.contest_command == "submissions":
            list_submissions(args.contest_id)
        else:
            # No subcommand — show usage
            print("Usage: mt-eval contest {create,submit,list,submissions}")
            print("Run 'mt-eval contest --help' for details.")
        return

    if args.command == "logout":
        from mt_eval_harness.auth import logout
        logout()
        return

    if args.command == "setup":
        from mt_eval_harness.setup_wizard import run_setup
        run_setup(
            install_all=getattr(args, "all", False),
            comet_only=getattr(args, "comet", False),
            fst_only=getattr(args, "fst", False),
            lang_code=getattr(args, "lang", None),
            status_only=getattr(args, "status", False),
        )
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

    if args.command == "export-config":
        from mt_eval_harness.config_exporter import cmd_export_config
        cmd_export_config(args)
        return

    # Default: run
    config = args_to_config(args)

    # Tool-calling needs a ToolProvider registered programmatically
    # (mt_eval_harness.plugins.tools.ToolProvider); nothing ships one in
    # plain CLI runs, so fail here with instructions instead of a
    # ValueError traceback deep in strategy resolution.
    if getattr(config, "tools_enabled", False) and args.command == "run":
        sys.exit(
            "  --tools requires a ToolProvider plugin registered via the "
            "programmatic API\n  (execute_run(..., tool_provider=...)); the "
            "CLI ships none yet. Use --method\n  <plugin-dir> for method "
            "plugins, or run without --tools."
        )

    if not config.corpus_path and not (config.source_file and config.reference_file):
        print("ERROR: --corpus or (--source-file + --reference-file) is required.")
        print("  Usage: mt-eval run --corpus <path>                          (JSON/JSONL/TSV)")
        print("         mt-eval run --source-file <src> --reference-file <ref> (parallel text)")
        sys.exit(1)

    # Auto-set --prompt champollion when --champollion-config is provided
    # and no explicit --prompt was given by the user.
    if config.champollion_config_path and config.prompt_version == "naive":
        config.prompt_version = "champollion"

    # --- "Test What You Ship" mode ---
    # When --champollion-config is provided, import ALL production config
    # as defaults (model, temperature, batchSize, coaching). Explicit CLI
    # flags still override. This ensures eval uses the same settings as
    # production unless the user says otherwise.
    if config.champollion_config_path and config.target_lang_code:
        from mt_eval_harness.champollion_config import load_champollion_config
        rc = load_champollion_config(
            config.champollion_config_path,
            config.target_lang_code,
            cards_dir=config.champollion_cards_dir,
        )

        imported_fields = []

        # Import model if user didn't explicitly set --model
        # (argparse default is DEFAULT_MODEL)
        if config.model == DEFAULT_MODEL and rc.model:
            config.model = rc.model
            imported_fields.append(f"model={rc.model}")

        # Import temperature if user didn't explicitly set --temperature
        # (argparse default is 0.0 for deterministic scoring)
        if config.temperature == 0.0 and rc.temperature is not None:
            config.temperature = rc.temperature
            imported_fields.append(f"temperature={rc.temperature}")
        elif rc.temperature is not None and rc.temperature != config.temperature:
            # User explicitly set a different temperature — warn about divergence
            print(
                f"  ℹ Production temperature={rc.temperature}, "
                f"harness using temperature={config.temperature}. "
                f"Pass --temperature {rc.temperature} for production-identical output."
            )

        # Import batch_size if user didn't explicitly set --batch-size
        if config.batch_size == DEFAULT_BATCH_SIZE and rc.batch_size:
            config.batch_size = rc.batch_size
            imported_fields.append(f"batchSize={rc.batch_size}")

        # Import coaching prompt if user didn't provide one
        if not config.coaching_file and rc.coaching_prompt:
            config.coaching_file = rc.coaching_file
            imported_fields.append("coachingFile")

        if imported_fields:
            print(f"  ℹ Imported from champollion.config.json: {', '.join(imported_fields)}")

    # Register the ChampollionPromptProvider when champollion config is active
    prompt_providers = None
    if config.champollion_config_path:
        from mt_eval_harness.plugins.champollion_prompts import ChampollionPromptProvider
        prompt_providers = [ChampollionPromptProvider()]

    # --- Multi-model support ---
    # Detect comma-separated models and fan out to execute_multi_run()
    # so each model gets its own aiohttp session and rate-limit semaphore.
    try:
        model_str = config.model
        if "," in model_str:
            from mt_eval_harness.runner import execute_multi_run
            from mt_eval_harness.config import MODEL_REGISTRY, fuzzy_resolve_model
            from dataclasses import replace

            model_slugs = [m.strip() for m in model_str.split(",") if m.strip()]
            configs = []
            for slug in model_slugs:
                # Resolve short names through the registry, then fuzzy match
                resolved = MODEL_REGISTRY.get(slug, slug)
                if "/" not in resolved and slug not in MODEL_REGISTRY:
                    fuzzy = fuzzy_resolve_model(slug)
                    if fuzzy:
                        print(f"  ℹ Resolved '{slug}' → '{fuzzy}' (fuzzy match)")
                        resolved = fuzzy
                    else:
                        print(f"  ERROR: Unknown model '{slug}'. "
                              f"Available shortcuts: {', '.join(sorted(MODEL_REGISTRY.keys()))}. "
                              f"Or pass a full OpenRouter model ID (e.g. 'anthropic/claude-sonnet-4').")
                        sys.exit(1)
                model_config = replace(config, model=resolved)
                configs.append(model_config)

            print(f"\n  Multi-model run: {len(configs)} models")
            for c in configs:
                print(f"    • {c.model} → {c.model_id}")

            asyncio.run(execute_multi_run(configs, prompt_providers=prompt_providers))
        else:
            from mt_eval_harness.runner import execute_run
            asyncio.run(execute_run(config, prompt_providers=prompt_providers))

    except (RuntimeError, ValueError) as exc:
        # Clean exit for expected failures: auth errors (401/402/403),
        # missing corpora/builders, invalid model IDs, etc.
        # No traceback — just the error message and a hint.
        sys.stdout.flush()
        print(f"\n  ✗ {exc}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n  Cancelled.")
        sys.exit(130)


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
