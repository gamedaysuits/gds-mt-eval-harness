"""
Pipeline — Shared concerns for all execution strategies.

This module extracts the cross-cutting logic that was previously
duplicated across all four branches of the God Function in runner.py:
    - Post-translation hook application
    - Result enrichment (corpus metadata + cost estimation)
    - RunLog assembly and disk write
    - Progress reporting

Why a separate module instead of a base class:
    Strategies have different concurrency patterns (gather vs sequential),
    so inheritance would force awkward template-method contortions.
    Composition is cleaner — strategies call these functions explicitly.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mt_eval_harness import __version__
from mt_eval_harness.config import RunConfig
from mt_eval_harness.api import estimate_cost


# ---------------------------------------------------------------------------
# Post-translation hook application
# ---------------------------------------------------------------------------

async def apply_hooks(
    entry: dict,
    result: dict,
    hooks: list,
    config: RunConfig,
    api_fn: Any | None = None,
) -> dict:
    """Apply registered post-translation hooks to a single result.

    Hooks run in registration order. If the result has an error,
    hooks are skipped — corrupted data shouldn't be post-processed.

    Args:
        entry: The original corpus entry.
        result: The translation result dict.
        hooks: List of PostTranslationHook plugins.
        config: Run configuration.
        api_fn: Optional API function for hooks that need LLM calls
                (e.g., grammar verification hooks).

    Returns:
        The (potentially modified) result dict.
    """
    if result.get("error"):
        return result

    for hook in hooks:
        result = await hook.process(entry, result, config, api_fn=api_fn)

    return result


# ---------------------------------------------------------------------------
# Result enrichment — merge corpus metadata + cost estimation
# ---------------------------------------------------------------------------

def enrich_results(
    results: list[dict],
    corpus: list[dict],
    config: RunConfig,
    pricing: dict | None = None,
) -> tuple[list[dict], float]:
    """Enrich raw results with corpus metadata and cost estimates.

    Each result gets merged with its corresponding corpus entry to
    produce the full schema that tester.py and the dashboard expect.

    Args:
        results: Raw translation results from a strategy.
        corpus: The full corpus entries (for source/expected/segment).
        config: Run configuration (for field name mapping).
        pricing: OpenRouter pricing data for cost estimation.

    Returns:
        Tuple of (enriched results list, total cost in USD).
    """
    corpus_by_id = {e["id"]: e for e in corpus}
    enriched = []
    total_cost = 0.0

    for result in results:
        entry = corpus_by_id.get(result["id"], {})
        entry_cost = estimate_cost(
            result.get("usage", {}),
            config.model_id,
            pricing,
        )
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

    return enriched, round(total_cost, 4)


# ---------------------------------------------------------------------------
# RunLog assembly
# ---------------------------------------------------------------------------

def build_run_log(
    config: RunConfig,
    enriched_results: list[dict],
    run_id: str,
    timestamp_start: str,
    elapsed_s: float,
    cache_hits: int,
    total_cost: float,
) -> dict:
    """Assemble the complete RunLog dict.

    The RunLog is the primary output artifact — it contains everything
    needed to reproduce and analyze the run. The config snapshot ensures
    any logged result can be exactly reproduced.
    """
    return {
        "harness_version": __version__,
        "run_id": run_id,
        "config": config.to_dict(),
        "timestamp_start": timestamp_start,
        "timestamp_end": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(elapsed_s, 1),
        "total_entries": len(enriched_results),
        "cache_hits": cache_hits,
        "total_cost_usd": total_cost,
        "results": enriched_results,
    }


def write_run_log(run_log: dict, output_dir: str) -> Path:
    """Write the RunLog to disk as JSON.

    Creates the output directory if it doesn't exist.

    Returns:
        The path to the written file.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{run_log['run_id']}.json"
    output_path.write_text(
        json.dumps(run_log, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path


# ---------------------------------------------------------------------------
# Progress reporting
# ---------------------------------------------------------------------------

def report_progress(done: int, total: int) -> None:
    """Print progress every 10% or when done.

    Uses simple print() — no dependency on rich/tqdm to keep
    the harness zero-dependency beyond aiohttp.
    """
    if total == 0:
        return
    step = max(1, total // 10)
    if done % step == 0 or done == total:
        pct = round(done / total * 100)
        print(f"  Progress: {done}/{total} ({pct}%)")
