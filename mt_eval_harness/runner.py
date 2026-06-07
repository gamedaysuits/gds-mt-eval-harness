"""
Run Harness — Core execution engine for translation experiments.

This is the orchestrator that ties together:
    - Dataset loading (JSON, JSONL, TSV, parallel text — via corpus_loader)
    - System prompt loading (built-in + plugin providers, including champollion interop)
    - Strategy resolution (single, batch, tool-call, plugin process)
    - Pipeline shared concerns (enrichment, RunLog, progress)

The runner delegates actual translation to strategy modules
(mt_eval_harness.strategies), keeping this file focused on
orchestration and coordination.

┌──────────────────────────────────────────────────────────────┐
│  HOW TO RUN MULTI-MODEL BENCHMARKS:                            │
│                                                                │
│  Use execute_multi_run(configs) — NOT a for-loop over           │
│  execute_run(). Each model gets its own aiohttp session and     │
│  semaphore, so different providers don't compete for rate       │
│  limits. A 14-model benchmark runs in ~15 minutes parallel     │
│  vs ~3.5 hours sequential.                                     │
│                                                                │
│  Defaults come from HARNESS_DEFAULTS in config.py.             │
│  batch_size=25, max_tokens=32768, concurrency=8, cache=on.     │
└──────────────────────────────────────────────────────────────┘

Design decisions:
    - Strategies are resolved via a factory, not if/elif dispatch.
      Each mode is independently testable and extensible.
    - Process plugins are first-class: the built-in LLM caller is
      just the default strategy. Any pipeline can register via the
      TranslationMethod protocol for identical evaluation.
    - All errors are captured (never thrown) so a partial run still
      produces usable data.
    - Progress reporting uses simple print() — no dependency on
      rich/tqdm to keep the harness zero-dependency beyond aiohttp.
    - Language-specific logic (prompts, tools, post-processing hooks)
      is injected via plugin protocols, not imported directly.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiohttp

from mt_eval_harness.config import RunConfig, TranslationMethod
from mt_eval_harness.cache import ResultCache
from mt_eval_harness.api import load_api_key, call_openrouter, fetch_pricing
from mt_eval_harness.strategies import resolve_strategy
from mt_eval_harness.pipeline import (
    enrich_results,
    build_run_log,
    write_run_log,
)


# ---------------------------------------------------------------------------
# Dataset loading — delegated to corpus_loader for multi-format support
# ---------------------------------------------------------------------------

from mt_eval_harness.corpus_loader import load_corpus  # noqa: F401

# load_corpus(config) is now imported from corpus_loader.py.
# It supports: harness JSON, JSONL, TSV, and parallel text files.
# See corpus_loader.py for format detection and normalization logic.


# Minimal default prompt — projects should register their own via PromptProvider.
# Accepts target_lang to tell the model WHAT language to translate into.
# Without a target language, models guess based on vibes — which leads to
# Japanese, Spanish, or "please specify the target language" responses.
DEFAULT_NAIVE_PROMPT_TEMPLATE = (
    "You are a translator. Translate the given {source_lang} text to {target_lang}. "
    "Output ONLY the translation, nothing else. No explanations, no notes."
)

# Legacy fallback for callers that don't set target_lang
DEFAULT_NAIVE_PROMPT_GENERIC = (
    "You are a translator. Translate the given text to the target language. "
    "Output ONLY the translation, nothing else. No explanations, no notes."
)


def build_naive_prompt(config: RunConfig) -> str:
    """Build the naive system prompt, interpolating language pair if set.

    If config.target_lang is set, produces a specific prompt like:
        "Translate the given English text to Plains Cree (nêhiyawêwin, SRO)."
    If not set, falls back to the generic "target language" wording.
    """
    if config.target_lang:
        source = config.source_lang or "source"
        return DEFAULT_NAIVE_PROMPT_TEMPLATE.format(
            source_lang=source,
            target_lang=config.target_lang,
        )
    return DEFAULT_NAIVE_PROMPT_GENERIC


def load_system_prompt(
    config: RunConfig,
    prompt_providers: list | None = None,
) -> str:
    """Load the system prompt based on config.prompt_version.

    Checks built-in versions first, then falls through to registered
    plugin providers.
    """
    version = config.prompt_version

    # Built-in: naive
    if version == "naive":
        return build_naive_prompt(config)

    # Built-in: custom file (legacy — use coaching_file instead)
    if version == "custom":
        path = Path(config.custom_prompt_path or config.coaching_file)
        return path.read_text(encoding="utf-8")

    # Coaching file takes precedence over prompt_version
    # (coaching_file is the modern replacement for custom_prompt_path)
    if config.coaching_file and version == "naive":
        path = Path(config.coaching_file)
        if path.exists():
            return path.read_text(encoding="utf-8")
        raise ValueError(
            f"Coaching file not found: {config.coaching_file}"
        )

    # Plugin providers
    if prompt_providers:
        for provider in prompt_providers:
            if version in provider.list_versions():
                return provider.load(version, config)

    raise ValueError(
        f"Unknown prompt version: '{version}'. "
        f"Built-in: naive, custom. "
        f"Register a PromptProvider plugin for custom versions."
    )



# ---------------------------------------------------------------------------
# Main execution engine
# ---------------------------------------------------------------------------

async def execute_run(
    config: RunConfig,
    method: TranslationMethod | None = None,
    prompt_providers: list | None = None,
    tool_provider: Any | None = None,
    post_hooks: list | None = None,
    metric_plugins: list | None = None,
) -> dict:
    """Execute a full harness run.

    This is the main entry point. It:
        1. Validates config
        2. Loads corpus + system prompt
        3. Resolves the correct execution strategy
        4. Delegates translation to the strategy
        5. Enriches results with corpus metadata + costs
        6. Writes the RunLog to disk

    Args:
        config: Full run configuration.
        method: Optional custom TranslationMethod plugin.
                If None, uses built-in LLM translation.
                Can also be loaded from config.method_path.
        prompt_providers: Optional list of PromptProvider plugins
                          for custom system prompt versions.
        tool_provider: Optional ToolProvider plugin for tool-calling.
        post_hooks: Optional list of PostTranslationHook plugins.
        metric_plugins: Reserved for future use (passed to tester).

    Returns:
        The complete RunLog dict (also written to disk).
    """
    # --- Validate ---
    available_prompts = ["naive", "custom"]
    if prompt_providers:
        for pp in prompt_providers:
            available_prompts.extend(pp.list_versions())

    errors = config.validate(prompt_versions=available_prompts)
    if errors:
        for e in errors:
            print(f"  CONFIG ERROR: {e}")
        raise ValueError(f"Invalid config: {'; '.join(errors)}")

    print("=" * 60)
    print("MT Eval Harness — Run Execution")
    print("=" * 60)
    print(f"  Model:       {config.model} → {config.model_id}")
    print(f"  Prompt:      {config.prompt_version}")
    print(f"  Temperature: {config.effective_temperature}")
    print(f"  Dataset:     {config.dataset}")
    print(f"  Batch size:  {config.batch_size}")
    print(f"  Max tokens:  {config.max_tokens}")
    print(f"  Concurrency: {config.concurrency}")
    print(f"  Tools:       {'enabled' if config.tools_enabled else 'disabled'}")
    if config.tools_enabled and config.tools_list:
        print(f"  Tool list:   {', '.join(config.tools_list)}")
    print(f"  Hooks:       {', '.join(config.post_hooks) if config.post_hooks else 'none'}")
    print(f"  Cache:       {'enabled' if config.cache_enabled else 'disabled'}")

    if config.dry_run:
        print("\n  DRY RUN — validating config only, no API calls")
        corpus, _ = load_corpus(config)
        print(f"  Would process {len(corpus)} entries")
        return {"dry_run": True, "entry_count": len(corpus)}

    # --- Load ---
    api_key = load_api_key()
    corpus, dataset_meta = load_corpus(config)
    print(f"\n  Loaded {len(corpus)} entries")

    # --- Corpus SHA-256 for reproducibility (BENCHMARK_SPEC §3.3) ---
    # Hash the corpus file so run cards can pin results to a specific
    # dataset version. If the corpus changes, the hash changes, and
    # old run cards are flagged as non-comparable.
    corpus_sha256 = ""
    if config.corpus_path and Path(config.corpus_path).exists():
        corpus_sha256 = hashlib.sha256(
            Path(config.corpus_path).read_bytes()
        ).hexdigest()

    # --- Post-load validation ---
    # Catch field name mismatches before burning money on API calls.
    ref_count = sum(1 for e in corpus if e.get(config.target_field))
    if ref_count == 0:
        print(
            f"\n  ❌ ERROR: No entries have a '{config.target_field}' field."
            f"\n  Your corpus uses different field names."
            f"\n  Available fields: {sorted(corpus[0].keys())}"
            f"\n  Set --target-field to the correct field name, or fix the corpus."
        )
        raise SystemExit(1)
    elif ref_count < len(corpus):
        print(f"  ⚠ WARNING: {len(corpus) - ref_count}/{len(corpus)} entries "
              f"are missing the '{config.target_field}' field.")

    # Check for missing IDs — required for result tracking
    id_count = sum(1 for e in corpus if "id" in e)
    if id_count == 0:
        print(
            f"\n  ❌ ERROR: No entries have an 'id' field."
            f"\n  Add sequential IDs to your corpus entries."
        )
        raise SystemExit(1)

    # Target language is required — without it, models guess (often
    # incorrectly) and the entire run is wasted money.
    # Checked here (after load_corpus) because corpus metadata may
    # auto-populate target_lang during loading.
    if not config.target_lang.strip():
        print(
            "\n  ❌ ERROR: target_lang is required."
            "\n  Set --target-lang 'Plains Cree (SRO)' or similar."
            "\n  Without it, the model guesses the target language "
            "and usually gets it wrong."
        )
        raise SystemExit(1)

    # --- Load method plugin if specified ---
    # config.method_path takes precedence over the method parameter.
    # When a method is loaded, the harness delegates translation to it
    # and the system prompt / batching / tools are irrelevant.
    if config.method_path and method is None:
        from mt_eval_harness.method_loader import load_method
        method = load_method(config.method_path)
        print(f"  Method:      {method.name} (from {config.method_path})")
        card = method.method_card()
        if card:
            print(f"  Method ID:   {card.get('method_id', 'unknown')}")
            print(f"  Method class: {card.get('class', 'unknown')}")

    # --- System prompt capture (BENCHMARK_SPEC §3.2) ---
    # The full prompt text and its SHA-256 are stored in the RunLog
    # for reproducibility. Two runs with different prompts will have
    # different hashes, even if all other config is identical.
    system_prompt = ""
    system_prompt_sha256 = ""
    if method is None:
        system_prompt = load_system_prompt(config, prompt_providers)
        system_prompt_sha256 = hashlib.sha256(
            system_prompt.encode("utf-8")
        ).hexdigest()
        print(f"  System prompt: {len(system_prompt):,} chars (sha256: {system_prompt_sha256[:12]}...)")

    # --- Resolve hooks ---
    active_hooks = []
    if post_hooks and config.post_hooks:
        hook_map = {h.name: h for h in post_hooks}
        for hook_name in config.post_hooks:
            if hook_name in hook_map:
                active_hooks.append(hook_map[hook_name])
            else:
                print(f"  WARNING: Hook '{hook_name}' not found in registered hooks")

    # --- Resolve strategy ---
    strategy = resolve_strategy(config, method, tool_provider)
    strategy_name = type(strategy).__name__
    print(f"  Strategy:    {strategy_name}")

    # --- Execute ---
    semaphore = asyncio.Semaphore(config.concurrency)
    cache = ResultCache(config)
    cache_stats = cache.stats()
    print(f"  Cache: {cache_stats.get('total_files', 0)} existing entries")

    timestamp_start = datetime.now(timezone.utc).isoformat()
    run_start = time.monotonic()

    async with aiohttp.ClientSession() as session:
        pricing = await fetch_pricing(session, api_key)

        # All strategies return (results, cache_hits)
        results, cache_hits = await strategy.execute(
            entries=corpus,
            config=config,
            session=session,
            api_key=api_key,
            semaphore=semaphore,
            system_prompt=system_prompt,
            hooks=active_hooks,
            cache=cache,
        )

    elapsed = time.monotonic() - run_start

    # --- Enrich + Build RunLog ---
    enriched, total_cost = enrich_results(results, corpus, config, pricing)

    # Collect method card if a method plugin was used
    method_card_data = None
    if method is not None and hasattr(method, "method_card"):
        method_card_data = method.method_card()

    # Collect coaching prompt text for provenance
    coaching_text = None
    coaching_sha = None
    if config.coaching_file:
        try:
            coaching_text = Path(config.coaching_file).read_text(encoding="utf-8")
            coaching_sha = hashlib.sha256(coaching_text.encode("utf-8")).hexdigest()
        except FileNotFoundError:
            pass  # Already loaded via system_prompt path

    run_id = _build_run_id(config)
    run_log = build_run_log(
        config=config,
        enriched_results=enriched,
        run_id=run_id,
        timestamp_start=timestamp_start,
        elapsed_s=elapsed,
        cache_hits=cache_hits,
        total_cost=total_cost,
        system_prompt=system_prompt,
        system_prompt_sha256=system_prompt_sha256,
        corpus_sha256=corpus_sha256,
        dataset_meta=dataset_meta,
        method_card=method_card_data,
        coaching_prompt=coaching_text,
        coaching_prompt_sha256=coaching_sha,
    )

    output_path = write_run_log(run_log, config.output_dir)

    print(f"\n{'=' * 60}")
    print(f"  Run complete: {run_id}")
    print(f"  Entries:      {len(enriched)}")
    print(f"  Cache hits:   {cache_hits}")
    print(f"  Elapsed:      {elapsed:.1f}s")
    print(f"  Total cost:   ${total_cost:.4f}")
    print(f"  Run log:      {output_path}")
    print("=" * 60)

    # --- Auto-score ---
    # Score the run immediately so users don't need a separate
    # 'mt-eval test' step. The report is written alongside the run log.
    from mt_eval_harness.tester import analyze_run_log
    from mt_eval_harness.plugin_discovery import discover_metric_plugins

    # Auto-discover language-specific metric plugins (e.g. GiellaLT FST).
    # We use skip_fst=True here because the translation has already completed —
    # blocking AFTER spending API credits would be a terrible UX. The FST gate
    # fires properly when the user runs 'mt-eval test' separately. During auto-
    # score, we just include whatever plugins are already installed.
    metric_plugins = discover_metric_plugins(
        run_log.get("config", {}),
        skip_fst=True,
    )

    report_path = output_path.with_name(output_path.stem + "_report.json")
    report = analyze_run_log(
        run_log,
        output_path=report_path,
        metric_plugins=metric_plugins or None,
    )

    return run_log


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_run_id(config: RunConfig) -> str:
    """Build a human-readable run ID from config."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    # Sanitize model name: full slugs like "google/gemini-3.1-pro-preview"
    # contain slashes that would create nested directories in the run log path
    model_short = config.model.replace("/", "_").replace("-", "").replace(".", "")
    prompt = config.prompt_version.replace(".", "")

    parts = [f"run_{ts}_{model_short}_{prompt}_{config.dataset}"]

    if config.tools_enabled:
        parts.append("tools")
    if config.post_hooks:
        parts.append("hooks")
    if config.batch_size > 1:
        parts.append(f"b{config.batch_size}")
    if config.run_name:
        parts.append(config.run_name)

    return "_".join(parts)


# ---------------------------------------------------------------------------
# Multi-model parallel execution
# ---------------------------------------------------------------------------

async def execute_multi_run(
    configs: list[RunConfig],
) -> list[dict | None]:
    """Execute multiple model runs in parallel.

    THIS IS THE RECOMMENDED WAY TO RUN MULTI-MODEL BENCHMARKS.

    Each config gets its own aiohttp session and concurrency semaphore,
    so models on different providers (Google, Anthropic, OpenAI, etc.)
    don't compete for rate limits. Wall-clock time = slowest single
    model, not sum of all models.

    Example:
        configs = [
            RunConfig(model="google/gemini-3.1-pro-preview", ...),
            RunConfig(model="anthropic/claude-opus-4.7", ...),
            RunConfig(model="openai/gpt-5.5", ...),
        ]
        results = await execute_multi_run(configs)
        # results: [RunLog_dict, RunLog_dict, RunLog_dict]

    Args:
        configs: List of RunConfig objects, typically one per model.
                 All other config fields (corpus, batch_size, etc.)
                 can vary per model if needed.

    Returns:
        List of RunLog dicts, one per config. Failed runs return None.
        Order matches the input configs list.
    """
    async def _safe_run(config: RunConfig) -> dict | None:
        """Execute a single model, catching exceptions to avoid
        killing the entire parallel batch on one failure."""
        try:
            return await execute_run(config)
        except Exception as exc:
            model_label = config.model_id
            print(f"\n  ERROR [{model_label}]: {exc}")
            return None

    print(f"\n  Launching {len(configs)} models in parallel...")
    return await asyncio.gather(*[_safe_run(c) for c in configs])
