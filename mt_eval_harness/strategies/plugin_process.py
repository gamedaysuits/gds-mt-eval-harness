"""
Plugin Process Strategy -- Delegate to a TranslationProcess plugin.

This is the thinnest strategy. It simply calls the plugin's
translate() method and wraps the results. Custom pipelines
(e.g., FST-gated coached translation) implement the TranslationProcess
protocol and get evaluated identically to the built-in strategies.

Extracted from runner.py lines 515-523 (the if process is not None
branch of the original God Function).
"""
from __future__ import annotations

from mt_eval_harness.config import RunConfig, TranslationProcess
from mt_eval_harness.pipeline import report_progress


def _chunk(items: list, size: int) -> list[list]:
    """Split a list into chunks of the given size."""
    return [items[i:i + size] for i in range(0, len(items), size)]


class PluginProcessStrategy:
    """Delegate translation to a custom TranslationProcess plugin.

    The plugin handles all API calls, tool usage, and post-processing
    internally. This strategy just manages batching and progress.
    """

    def __init__(self, process: TranslationProcess):
        self._process = process

    async def execute(
        self,
        entries: list[dict],
        config: RunConfig,
        **kwargs,
    ) -> tuple[list[dict], int]:
        """Execute plugin process translation for all entries.

        The plugin's translate() method receives batches of entries
        and returns one result dict per entry.

        Returns:
            Tuple of (results list, cache_hits count).
            Cache hits is always 0 — plugins manage their own caching.
        """
        total = len(entries)
        done_count = 0
        all_results = []

        batches = _chunk(entries, config.batch_size)
        for batch in batches:
            results = await self._process.translate(batch, config)
            all_results.extend(results)
            done_count += len(batch)
            report_progress(done_count, total)

        return all_results, 0
