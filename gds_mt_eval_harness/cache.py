"""
Deterministic File Cache — Cache translation results to avoid re-running.

Caching strategy:
    - batch_size=1: cache key = hash(config_hash + source_text)
    - batch_size>1: cache key = hash(config_hash + sorted batch source texts)

Cache files are plain JSON, one per cached result. The cache directory
is organized by config hash to prevent cross-contamination between
different configurations.

Design decisions:
    - File-per-entry (not SQLite) for easy inspection and git-friendliness
    - Config hash isolation: changing any relevant config parameter
      (model, prompt, tools, temperature) invalidates all prior cache
    - Human-readable filenames for debugging
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gds_mt_eval_harness.config import RunConfig


class ResultCache:
    """File-based deterministic cache for translation results.

    Each unique (config + input) combination maps to exactly one
    cached result file. The config_hash ensures that changing any
    parameter that affects output (model, prompt, tools, etc.)
    automatically creates a new cache namespace.
    """

    def __init__(self, config: "RunConfig"):
        self.enabled = config.cache_enabled
        self.config_hash = config.config_hash()
        # Organize cache by config hash to prevent cross-contamination
        self.cache_dir = Path(config.cache_dir) / self.config_hash
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _entry_key(self, source_text: str) -> str:
        """Generate cache key for a single entry."""
        raw = f"{self.config_hash}|{source_text.strip()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _batch_key(self, source_texts: list[str]) -> str:
        """Generate cache key for a batch of entries.

        The key incorporates all texts in their batch order so that
        the same entries in a different order produce a different key.
        This is intentional: batch composition affects the API response
        (the model sees all entries together in a numbered list).
        """
        combined = "|".join(t.strip() for t in source_texts)
        raw = f"{self.config_hash}|batch|{combined}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, source_text: str) -> dict | None:
        """Load a cached single-entry result, or None if not cached."""
        if not self.enabled:
            return None
        key = self._entry_key(source_text)
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return data.get("result")
            except (json.JSONDecodeError, KeyError):
                return None
        return None

    def put(self, source_text: str, result: dict) -> None:
        """Cache a single-entry result."""
        if not self.enabled:
            return
        key = self._entry_key(source_text)
        path = self.cache_dir / f"{key}.json"
        payload = {
            "config_hash": self.config_hash,
            "source_text": source_text,
            "result": result,
            "cached_at": datetime.now(timezone.utc).isoformat(),
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_batch(self, source_texts: list[str]) -> list[dict] | None:
        """Load cached batch results, or None if any entry is missing."""
        if not self.enabled:
            return None
        key = self._batch_key(source_texts)
        path = self.cache_dir / f"batch_{key}.json"
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                results = data.get("results", [])
                if len(results) == len(source_texts):
                    return results
            except (json.JSONDecodeError, KeyError):
                pass
        return None

    def put_batch(self, source_texts: list[str], results: list[dict]) -> None:
        """Cache a batch of results."""
        if not self.enabled:
            return
        if len(source_texts) != len(results):
            return  # Safety: don't cache mismatched batches
        key = self._batch_key(source_texts)
        path = self.cache_dir / f"batch_{key}.json"
        payload = {
            "config_hash": self.config_hash,
            "batch_size": len(source_texts),
            "source_texts": source_texts,
            "results": results,
            "cached_at": datetime.now(timezone.utc).isoformat(),
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def stats(self) -> dict:
        """Return cache statistics for the current config namespace."""
        if not self.enabled or not self.cache_dir.exists():
            return {"enabled": self.enabled, "entries": 0, "batches": 0}

        files = list(self.cache_dir.glob("*.json"))
        entries = sum(1 for f in files if not f.name.startswith("batch_"))
        batches = sum(1 for f in files if f.name.startswith("batch_"))
        return {
            "enabled": True,
            "config_hash": self.config_hash,
            "cache_dir": str(self.cache_dir),
            "entries": entries,
            "batches": batches,
            "total_files": len(files),
        }
