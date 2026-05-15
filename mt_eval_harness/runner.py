"""
Run Harness — Core execution engine for translation experiments.

This is the orchestrator that ties together:
    - Dataset loading (any JSON corpus)
    - System prompt loading (built-in + plugin providers)
    - Strategy resolution (single, batch, tool-call, plugin process)
    - Pipeline shared concerns (enrichment, RunLog, progress)

The runner delegates actual translation to strategy modules
(mt_eval_harness.strategies), keeping this file focused on
orchestration and coordination.

Design decisions:
    - Strategies are resolved via a factory, not if/elif dispatch.
      Each mode is independently testable and extensible.
    - Process plugins are first-class: the built-in LLM caller is
      just the default strategy. Any pipeline can register via the
      TranslationProcess protocol for identical evaluation.
    - All errors are captured (never thrown) so a partial run still
      produces usable data.
    - Progress reporting uses simple print() — no dependency on
      rich/tqdm to keep the harness zero-dependency beyond aiohttp.
    - Language-specific logic (prompts, tools, post-processing hooks)
      is injected via plugin protocols, not imported directly.
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import aiohttp

from mt_eval_harness.config import RunConfig, TranslationProcess
from mt_eval_harness.cache import ResultCache
from mt_eval_harness.api import load_api_key, call_openrouter, fetch_pricing
from mt_eval_harness.strategies import resolve_strategy
from mt_eval_harness.pipeline import (
    enrich_results,
    build_run_log,
    write_run_log,
)


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------

def load_corpus(config: RunConfig) -> list[dict]:
    """Load entries from a corpus JSON file, filtered by config.dataset.

    Supports:
        - "all": Full corpus (default)
        - Segment name: any value in config.segment_names
        - ID range: "0-61" (inclusive)
        - Explicit IDs via config.entry_ids
    """
    if not config.corpus_path:
        raise FileNotFoundError(
            "No corpus_path specified. Set --corpus <path> or config.corpus_path."
        )

    corpus_path = Path(config.corpus_path)
    if not corpus_path.exists():
        raise FileNotFoundError(f"Corpus not found: {corpus_path}")

    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))

    # Auto-detect segment names from corpus if not explicitly configured.
    # This makes the harness zero-config for new language pairs — just
    # point it at a corpus and it discovers the available segments.
    segment_names = config.segment_names
    if not segment_names:
        segment_names = sorted({
            e.get("segment", "") for e in corpus if e.get("segment")
        })
        if segment_names:
            print(f"  Auto-detected segments: {', '.join(segment_names)}")

    # Explicit entry IDs take precedence
    if config.entry_ids is not None:
        id_set = set(config.entry_ids)
        filtered = [e for e in corpus if e["id"] in id_set]
        if len(filtered) != len(id_set):
            found = {e["id"] for e in filtered}
            missing = id_set - found
            print(f"  WARNING: {len(missing)} entry IDs not found: {sorted(missing)[:10]}")
        return filtered

    dataset = config.dataset.strip().lower()

    if dataset == "all":
        return corpus

    # Check for segment name (uses auto-detected names if config was empty)
    if dataset in segment_names:
        return [e for e in corpus if e.get("segment") == dataset]

    # Check for ID range (e.g., "0-61")
    if "-" in dataset:
        try:
            start, end = dataset.split("-")
            start, end = int(start), int(end)
            return [e for e in corpus if start <= e["id"] <= end]
        except (ValueError, IndexError):
            pass

    # Check for single ID
    try:
        single_id = int(dataset)
        return [e for e in corpus if e["id"] == single_id]
    except ValueError:
        pass

    available = ', '.join(segment_names) if segment_names else 'none detected'
    raise ValueError(
        f"Unknown dataset filter: '{config.dataset}'. "
        f"Use 'all', a segment name ({available}), "
        f"an ID range ('0-61'), or a single ID."
    )


# ---------------------------------------------------------------------------
# Prompt loading — built-in + plugin providers
# ---------------------------------------------------------------------------

# Minimal default prompt — projects should register their own via PromptProvider
DEFAULT_NAIVE_PROMPT = (
    "You are a translator. Translate the given text to the target language. "
    "Output ONLY the translation, nothing else. No explanations, no notes."
)


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
        return DEFAULT_NAIVE_PROMPT

    # Built-in: custom file
    if version == "custom":
        path = Path(config.custom_prompt_path)
        return path.read_text(encoding="utf-8")

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
    process: TranslationProcess | None = None,
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
        process: Optional custom TranslationProcess plugin.
                 If None, uses built-in LLM translation.
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
    print(f"  Dataset:     {config.dataset}")
    print(f"  Batch size:  {config.batch_size}")
    print(f"  Concurrency: {config.concurrency}")
    print(f"  Tools:       {'enabled' if config.tools_enabled else 'disabled'}")
    if config.tools_enabled and config.tools_list:
        print(f"  Tool list:   {', '.join(config.tools_list)}")
    print(f"  Hooks:       {', '.join(config.post_hooks) if config.post_hooks else 'none'}")
    print(f"  Cache:       {'enabled' if config.cache_enabled else 'disabled'}")

    if config.dry_run:
        print("\n  DRY RUN — validating config only, no API calls")
        corpus = load_corpus(config)
        print(f"  Would process {len(corpus)} entries")
        return {"dry_run": True, "entry_count": len(corpus)}

    # --- Load ---
    api_key = load_api_key()
    corpus = load_corpus(config)
    print(f"\n  Loaded {len(corpus)} entries")

    system_prompt = ""
    if process is None:
        system_prompt = load_system_prompt(config, prompt_providers)
        print(f"  System prompt: {len(system_prompt):,} chars")

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
    strategy = resolve_strategy(config, process, tool_provider)
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

    run_id = _build_run_id(config)
    run_log = build_run_log(
        config=config,
        enriched_results=enriched,
        run_id=run_id,
        timestamp_start=timestamp_start,
        elapsed_s=elapsed,
        cache_hits=cache_hits,
        total_cost=total_cost,
    )

    output_path = write_run_log(run_log, config.output_dir)

    print(f"\n{'=' * 60}")
    print(f"  Run complete: {run_id}")
    print(f"  Entries:      {len(enriched)}")
    print(f"  Cache hits:   {cache_hits}")
    print(f"  Elapsed:      {elapsed:.1f}s")
    print(f"  Total cost:   ${total_cost:.4f}")
    print(f"  Output:       {output_path}")
    print("=" * 60)

    return run_log


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_run_id(config: RunConfig) -> str:
    """Build a human-readable run ID from config."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    model_short = config.model.replace("-", "").replace(".", "")
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
