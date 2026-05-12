"""
Run Harness — Core execution engine for translation experiments.

This is the central orchestrator that ties together:
    - Dataset loading (any JSON corpus)
    - System prompt loading (built-in + plugin providers)
    - Batching and concurrency control
    - Caching layer
    - Built-in LLM translation (single + batched)
    - Tool-calling integration (via ToolProvider plugins)
    - Post-translation hooks (via PostTranslationHook plugins)
    - Custom process plugins (TranslationProcess protocol)

The runner produces a standardized RunLog JSON file that the test
harness can consume for metric computation.

Design decisions:
    - Process plugins are first-class: the built-in LLM caller is
      just the default process. Any pipeline can register via the
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

from gds_mt_eval_harness import __version__
from gds_mt_eval_harness.config import RunConfig, TranslationProcess
from gds_mt_eval_harness.cache import ResultCache
from gds_mt_eval_harness.api import (
    load_api_key,
    call_openrouter,
    build_system_message,
    clean_response,
    parse_numbered_response,
    fetch_pricing,
    estimate_cost,
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
# Built-in translation processes
# ---------------------------------------------------------------------------

async def _translate_single(
    session: aiohttp.ClientSession,
    entry: dict,
    config: RunConfig,
    system_prompt: str,
    api_key: str,
    semaphore: asyncio.Semaphore,
) -> dict:
    """Translate a single entry using direct LLM call (no tools)."""
    source_text = entry.get(config.source_field, "")
    messages = [
        build_system_message(system_prompt),
        {"role": "user", "content": source_text},
    ]

    result = await call_openrouter(
        session=session,
        messages=messages,
        model_id=config.model_id,
        api_key=api_key,
        semaphore=semaphore,
        max_tokens=config.max_tokens,
        temperature=config.effective_temperature,
    )

    return {
        "id": entry["id"],
        "predicted": clean_response(result["content"]) if result["content"] else "",
        "latency_s": result["latency_s"],
        "usage": result["usage"],
        "tool_calls": [],
        "tool_call_count": 0,
        "error": result["error"],
        "metadata": {},
    }


async def _translate_batch(
    session: aiohttp.ClientSession,
    entries: list[dict],
    config: RunConfig,
    system_prompt: str,
    api_key: str,
    semaphore: asyncio.Semaphore,
) -> list[dict]:
    """Translate a batch of entries in one API call using numbered list format."""
    n = len(entries)
    source_texts = [e.get(config.source_field, "") for e in entries]

    numbered = "\n".join(f"{i+1}. {s}" for i, s in enumerate(source_texts))
    user_msg = (
        f"Translate each of these {n} phrases to the target language.\n\n"
        f"{numbered}\n\n"
        f"Reply with EXACTLY {n} numbered lines. Each line: just the number "
        f"and the translation. No explanations, no extra text."
    )

    messages = [
        build_system_message(system_prompt),
        {"role": "user", "content": user_msg},
    ]

    result = await call_openrouter(
        session=session,
        messages=messages,
        model_id=config.model_id,
        api_key=api_key,
        semaphore=semaphore,
        max_tokens=config.max_tokens,
        temperature=config.effective_temperature,
    )

    if result["error"]:
        return [
            {
                "id": e["id"],
                "predicted": f"[ERROR: {result['error']}]",
                "latency_s": round(result["latency_s"] / n, 3),
                "usage": result["usage"],
                "tool_calls": [],
                "tool_call_count": 0,
                "error": result["error"],
                "metadata": {"batch_index": i},
            }
            for i, e in enumerate(entries)
        ]

    translations = parse_numbered_response(result["content"], n)
    per_latency = round(result["latency_s"] / n, 3)

    return [
        {
            "id": entries[i]["id"],
            "predicted": clean_response(translations[i]),
            "latency_s": per_latency,
            "usage": result["usage"],
            "tool_calls": [],
            "tool_call_count": 0,
            "error": None,
            "metadata": {"batch_index": i},
        }
        for i in range(n)
    ]


async def _translate_with_tools(
    session: aiohttp.ClientSession,
    entry: dict,
    config: RunConfig,
    system_prompt: str,
    api_key: str,
    semaphore: asyncio.Semaphore,
    tool_provider,
) -> dict:
    """Translate a single entry with tool-calling enabled.

    Uses the registered ToolProvider to get schemas and execute tool calls.
    """
    # Import here to avoid circular — tool loop lives in this module
    from gds_mt_eval_harness.api import call_openrouter as api_call

    tool_schemas = tool_provider.get_schemas(config)
    source_text = entry.get(config.source_field, "")

    user_msg = (
        f"Translate this text to the target language:\n\n"
        f"{source_text}\n\n"
        f"Use your tools to verify your work. Output ONLY the translation."
    )

    messages = [
        build_system_message(system_prompt),
        {"role": "user", "content": user_msg},
    ]

    # Multi-round tool-calling loop
    total_latency = 0.0
    total_usage: dict[str, int] = {}
    all_tool_calls = []
    tool_call_count = 0

    for round_num in range(config.max_tool_rounds):
        result = await api_call(
            session=session,
            messages=messages,
            model_id=config.model_id,
            api_key=api_key,
            semaphore=semaphore,
            max_tokens=config.max_tokens,
            temperature=config.effective_temperature,
            tools=tool_schemas if round_num == 0 or tool_call_count > 0 else None,
        )

        total_latency += result.get("latency_s", 0)
        if result.get("usage"):
            for k, v in result["usage"].items():
                total_usage[k] = total_usage.get(k, 0) + v

        if result.get("error"):
            return {
                "id": entry["id"],
                "predicted": "",
                "latency_s": total_latency,
                "usage": total_usage,
                "tool_calls": all_tool_calls,
                "tool_call_count": tool_call_count,
                "error": result["error"],
                "metadata": {},
            }

        # Check if model made tool calls
        tool_calls_in_response = result.get("tool_calls", [])
        if not tool_calls_in_response:
            # No tool calls — model produced final answer
            return {
                "id": entry["id"],
                "predicted": clean_response(result["content"]) if result["content"] else "",
                "latency_s": total_latency,
                "usage": total_usage,
                "tool_calls": all_tool_calls,
                "tool_call_count": tool_call_count,
                "error": None,
                "metadata": {},
            }

        # Execute each tool call
        # Add assistant message with tool calls
        messages.append({
            "role": "assistant",
            "content": result.get("content", ""),
            "tool_calls": tool_calls_in_response,
        })

        for tc in tool_calls_in_response:
            fn_name = tc["function"]["name"]
            try:
                fn_args = json.loads(tc["function"]["arguments"])
            except (json.JSONDecodeError, KeyError):
                fn_args = {}

            tool_result = await tool_provider.execute(fn_name, fn_args)
            tool_call_count += 1
            all_tool_calls.append({
                "round": round_num,
                "name": fn_name,
                "arguments": fn_args,
                "result": str(tool_result)[:500],  # Truncate for log size
            })

            # Add tool response to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tc.get("id", ""),
                "content": json.dumps(tool_result, default=str),
            })

    # Exhausted max rounds
    return {
        "id": entry["id"],
        "predicted": clean_response(result.get("content", "")) if result.get("content") else "",
        "latency_s": total_latency,
        "usage": total_usage,
        "tool_calls": all_tool_calls,
        "tool_call_count": tool_call_count,
        "error": None,
        "metadata": {"max_tool_rounds_reached": True},
    }


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
        2. Loads corpus
        3. Loads system prompt (built-in or plugin)
        4. Creates batches
        5. Executes translation (built-in or plugin process)
        6. Applies post-translation hooks if registered
        7. Estimates costs
        8. Writes RunLog JSON

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
    # Build list of available prompt versions for validation
    available_prompts = ["naive", "custom"]
    if prompt_providers:
        for pp in prompt_providers:
            available_prompts.extend(pp.list_versions())

    # --- Validate ---
    errors = config.validate(prompt_versions=available_prompts)
    if errors:
        for e in errors:
            print(f"  CONFIG ERROR: {e}")
        raise ValueError(f"Invalid config: {'; '.join(errors)}")

    print("=" * 60)
    print("GDS MT Eval Harness — Run Execution")
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

    # --- Resolve post-translation hooks ---
    active_hooks = []
    if post_hooks and config.post_hooks:
        hook_map = {h.name: h for h in post_hooks}
        for hook_name in config.post_hooks:
            if hook_name in hook_map:
                active_hooks.append(hook_map[hook_name])
            else:
                print(f"  WARNING: Hook '{hook_name}' not found in registered hooks")

    # --- Setup ---
    semaphore = asyncio.Semaphore(config.concurrency)
    cache = ResultCache(config)
    cache_stats = cache.stats()
    print(f"  Cache: {cache_stats.get('total_files', 0)} existing entries")

    timestamp_start = datetime.now(timezone.utc).isoformat()
    run_start = time.monotonic()
    total_entries = len(corpus)
    done_count = 0
    cache_hits = 0
    all_results = []

    async with aiohttp.ClientSession() as session:
        pricing = await fetch_pricing(session, api_key)

        if process is not None:
            # --- Plugin process mode ---
            print(f"\n  Running custom process: {config.process_name or 'unnamed'}")
            batches = _chunk(corpus, config.batch_size)
            for batch in batches:
                results = await process.translate(batch, config)
                all_results.extend(results)
                done_count += len(batch)
                _report_progress(done_count, total_entries)

        elif config.tools_enabled:
            # --- Tool-calling mode (batch_size must be 1) ---
            if not tool_provider:
                raise ValueError(
                    "Tool-calling enabled but no ToolProvider registered. "
                    "Pass a ToolProvider plugin to execute_run()."
                )
            print(f"\n  Tool-calling mode: processing {total_entries} entries individually")

            async def _process_entry_tools(entry):
                nonlocal done_count, cache_hits
                source_text = entry.get(config.source_field, "")

                cached = cache.get(source_text)
                if cached is not None:
                    cache_hits += 1
                    done_count += 1
                    _report_progress(done_count, total_entries)
                    cached["id"] = entry["id"]
                    return cached

                result = await _translate_with_tools(
                    session, entry, config, system_prompt,
                    api_key, semaphore, tool_provider,
                )

                # Apply post-translation hooks
                for hook in active_hooks:
                    if not result.get("error"):
                        result = await hook.process(
                            entry, result, config,
                            api_fn=lambda **kw: call_openrouter(session=session, **kw),
                        )

                cache.put(source_text, result)
                done_count += 1
                _report_progress(done_count, total_entries)
                return result

            tasks = [_process_entry_tools(e) for e in corpus]
            all_results = await asyncio.gather(*tasks)

        elif config.batch_size > 1:
            # --- Batched mode ---
            batches = _chunk(corpus, config.batch_size)
            print(f"\n  Batched mode: {len(batches)} batches of up to {config.batch_size}")

            for batch in batches:
                source_texts = [
                    e.get(config.source_field, "")
                    for e in batch
                ]

                cached = cache.get_batch(source_texts)
                if cached is not None:
                    cache_hits += len(batch)
                    all_results.extend(cached)
                    done_count += len(batch)
                    _report_progress(done_count, total_entries)
                    continue

                results = await _translate_batch(
                    session, batch, config, system_prompt, api_key, semaphore,
                )

                # Apply post-translation hooks to each entry
                for hook in active_hooks:
                    hooked = []
                    for entry, result in zip(batch, results):
                        if not result.get("error"):
                            result = await hook.process(
                                entry, result, config,
                                api_fn=lambda **kw: call_openrouter(session=session, **kw),
                            )
                        hooked.append(result)
                    results = hooked

                cache.put_batch(source_texts, results)
                all_results.extend(results)
                done_count += len(batch)
                _report_progress(done_count, total_entries)

        else:
            # --- Single-entry mode (batch_size=1, no tools) ---
            print(f"\n  Single-entry mode: processing {total_entries} entries")

            async def _process_entry_single(entry):
                nonlocal done_count, cache_hits
                source_text = entry.get(config.source_field, "")

                cached = cache.get(source_text)
                if cached is not None:
                    cache_hits += 1
                    done_count += 1
                    _report_progress(done_count, total_entries)
                    cached["id"] = entry["id"]
                    return cached

                result = await _translate_single(
                    session, entry, config, system_prompt, api_key, semaphore,
                )

                # Apply post-translation hooks
                for hook in active_hooks:
                    if not result.get("error"):
                        result = await hook.process(
                            entry, result, config,
                            api_fn=lambda **kw: call_openrouter(session=session, **kw),
                        )

                cache.put(source_text, result)
                done_count += 1
                _report_progress(done_count, total_entries)
                return result

            tasks = [_process_entry_single(e) for e in corpus]
            all_results = await asyncio.gather(*tasks)

    elapsed = time.monotonic() - run_start

    # --- Enrich results with corpus metadata + cost ---
    corpus_by_id = {e["id"]: e for e in corpus}
    enriched = []
    total_cost = 0.0
    for result in all_results:
        entry = corpus_by_id.get(result["id"], {})
        entry_cost = estimate_cost(result.get("usage", {}), config.model_id, pricing)
        total_cost += entry_cost

        enriched.append({
            "id": result["id"],
            "source": entry.get(config.source_field, ""),
            "expected": entry.get(config.target_field, ""),
            "predicted": result.get("predicted", ""),
            "segment": entry.get("segment", ""),
            "difficulty": entry.get("difficulty", 0),
            "latency_s": result.get("latency_s", 0),
            "usage": result.get("usage", {}),
            "cost_usd": entry_cost,
            "tool_calls": result.get("tool_calls", []),
            "tool_call_count": result.get("tool_call_count", 0),
            "error": result.get("error"),
            "metadata": result.get("metadata", {}),
        })

    # --- Build RunLog ---
    run_id = _build_run_id(config)
    run_log = {
        "harness_version": __version__,
        "run_id": run_id,
        "config": config.to_dict(),
        "timestamp_start": timestamp_start,
        "timestamp_end": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(elapsed, 1),
        "total_entries": total_entries,
        "cache_hits": cache_hits,
        "total_cost_usd": round(total_cost, 4),
        "results": enriched,
    }

    # --- Write output ---
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{run_id}.json"
    output_path.write_text(
        json.dumps(run_log, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n{'=' * 60}")
    print(f"  Run complete: {run_id}")
    print(f"  Entries:      {total_entries}")
    print(f"  Cache hits:   {cache_hits}")
    print(f"  Elapsed:      {elapsed:.1f}s")
    print(f"  Total cost:   ${total_cost:.4f}")
    print(f"  Output:       {output_path}")
    print("=" * 60)

    return run_log


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _chunk(items: list, size: int) -> list[list]:
    """Split a list into chunks of the given size."""
    return [items[i:i + size] for i in range(0, len(items), size)]


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


def _report_progress(done: int, total: int) -> None:
    """Print progress every 10% or when done."""
    step = max(1, total // 10)
    if done % step == 0 or done == total:
        pct = round(done / total * 100)
        print(f"  Progress: {done}/{total} ({pct}%)")
