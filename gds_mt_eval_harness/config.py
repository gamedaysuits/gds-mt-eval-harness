"""
Run Harness Configuration — All configurable knobs in one place.

Every parameter that affects a harness run is defined here as a typed
dataclass field. The config is serialized into every RunLog for full
reproducibility — any logged result can be exactly reproduced by
loading its config snapshot.

The TranslationProcess protocol defines the plugin interface: any
callable that takes structured input and returns structured output
can be registered as a translation method.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Model registry — maps short names to OpenRouter model IDs
# ---------------------------------------------------------------------------
# This is a convenience lookup. You can always pass a full OpenRouter
# model ID directly (e.g. "anthropic/claude-opus-4.6").

MODEL_REGISTRY: dict[str, str] = {
    # Anthropic
    "claude-opus-4.7":   "anthropic/claude-opus-4.7",
    "claude-opus-4.6":   "anthropic/claude-opus-4.6",
    "claude-sonnet-4":   "anthropic/claude-sonnet-4",
    # Google
    "gemini-3.1-pro":    "google/gemini-3.1-pro-preview",
    "gemini-2.5-flash":  "google/gemini-2.5-flash",
    "gemini-3-flash":    "google/gemini-3-flash-preview",
    # OpenAI
    "gpt-5.5":           "openai/gpt-5.5",
    # DeepSeek
    "deepseek-v4-pro":   "deepseek/deepseek-v4-pro",
    "deepseek-r1":       "deepseek/deepseek-r1-0528",
}

DEFAULT_MODEL = "gemini-3.1-pro"

# Models that reject temperature=0 (require 0.01 minimum)
NEEDS_NONZERO_TEMP: set[str] = {
    "anthropic/claude-opus-4.7",
    "anthropic/claude-opus-4.6",
    "anthropic/claude-opus-4.5",
    "anthropic/claude-opus-4.1",
    "anthropic/claude-opus-4",
    "anthropic/claude-sonnet-4",
    "deepseek/deepseek-v4-pro",
    "deepseek/deepseek-r1",
    "deepseek/deepseek-r1-0528",
}


# ---------------------------------------------------------------------------
# Plugin protocol — any translation process implements this
# ---------------------------------------------------------------------------

@runtime_checkable
class TranslationProcess(Protocol):
    """Protocol for pluggable translation methods.

    Any translation pipeline that implements this interface can be
    registered with the Run Harness for standardized evaluation.

    The process receives a batch of entries (even if batch_size=1)
    and returns one result dict per entry.

    Why a protocol instead of a base class:
        Structural typing — existing pipelines don't need to inherit
        from anything. If it has the right method signature, it works.
    """

    async def translate(
        self,
        entries: list[dict],
        config: "RunConfig",
    ) -> list[dict]:
        """Translate a batch of entries.

        Args:
            entries: List of dicts with at least 'english' and 'id' keys.
                     ('english' is the source text key by convention —
                      adjust for your language pair.)
            config: The full run configuration for context.

        Returns:
            List of result dicts, one per entry, each containing at minimum:
                - id: int — entry ID from the corpus
                - predicted: str — the translated text
                - latency_s: float — time taken in seconds
                - usage: dict — token usage (prompt_tokens, completion_tokens)
                - error: str | None — error message if failed
                - tool_calls: list[dict] — tool call log (empty if no tools)
                - tool_call_count: int — total tool calls made
                - metadata: dict — any process-specific metadata
        """
        ...


# ---------------------------------------------------------------------------
# Run configuration
# ---------------------------------------------------------------------------

@dataclass
class RunConfig:
    """Complete configuration for a single harness run.

    Every knob that affects execution is captured here. The full config
    is serialized into the RunLog so any result can be reproduced exactly.
    """

    # --- Dataset selection ---
    # "all" = full corpus, or segment name, or "0-61" range
    dataset: str = "all"
    # Explicit entry IDs override dataset if provided
    entry_ids: list[int] | None = None

    # --- Corpus ---
    # Path to the master corpus JSON file. This is the single ordered
    # file containing all evaluation entries.
    corpus_path: str | None = None

    # --- Source / target field names ---
    # Override these for non-English source languages
    source_field: str = "english"  # The field name for source text in corpus
    target_field: str = "cree_sro"  # The field name for reference translation

    # --- Segment names ---
    # The valid segment names in your corpus (for dataset filtering)
    segment_names: list[str] = field(default_factory=lambda: [
        "gold_standard", "textbook_sample", "phase1_test", "textbook_remainder",
    ])

    # --- Model ---
    model: str = DEFAULT_MODEL  # Short name, resolved via MODEL_REGISTRY
    max_tokens: int = 13680     # Per user spec; reasoning models need headroom

    # --- Tool calling ---
    # Individual toggles for each tool (None = all available tools)
    tools_enabled: bool = False
    # List of individual tool names to enable, e.g. ["fst_validate", "fst_generate"]
    # None means all tools. Only used when tools_enabled is True.
    tools_list: list[str] | None = None
    max_tool_rounds: int = 8    # Safety cap on tool-calling rounds per entry

    # --- Caching ---
    cache_enabled: bool = True
    cache_dir: str = "eval/cache/harness"

    # --- Batching ---
    # Entries per API call. 1 = individual, >1 = numbered list format.
    # Tool-calling requires batch_size=1 (enforced at validation time).
    batch_size: int = 1

    # --- Concurrency ---
    # Number of parallel API calls. The harness will handle rate limit
    # backoff automatically; set this to whatever the provider allows.
    concurrency: int = 8

    # --- System prompt ---
    # Built-in versions: "naive", "custom"
    # Language-specific versions register via PromptProvider plugins
    prompt_version: str = "naive"
    custom_prompt_path: str | None = None  # Path to custom .txt file

    # --- Post-translation hooks ---
    # List of hook names to apply (e.g. ["fst_gate"])
    # Hooks are registered externally via PostTranslationHook plugins
    post_hooks: list[str] = field(default_factory=list)

    # --- Output ---
    output_dir: str = "eval/logs/harness"
    run_name: str | None = None  # Optional human-readable label

    # --- Misc ---
    temperature: float = 0.0   # 0 for determinism
    dry_run: bool = False      # Validate config without API calls

    # --- Process plugin ---
    # If set, uses a custom TranslationProcess instead of the built-in
    # LLM caller. The process_name is logged for identification.
    process_name: str | None = None

    def validate(self, prompt_versions: list[str] | None = None) -> list[str]:
        """Validate configuration, return list of error messages.

        Args:
            prompt_versions: Available prompt version names (built-in +
                registered plugins). If None, only validates "naive" and "custom".
        """
        errors = []

        # Model resolution — allow both short names and full IDs
        # (full IDs just pass through)
        if self.model not in MODEL_REGISTRY and "/" not in self.model:
            errors.append(
                f"Unknown model '{self.model}'. "
                f"Available: {', '.join(sorted(MODEL_REGISTRY.keys()))}. "
                f"Or pass a full OpenRouter model ID (e.g. 'anthropic/claude-sonnet-4')."
            )

        # Tool-calling requires batch_size=1
        if self.tools_enabled and self.batch_size > 1:
            errors.append(
                f"Tool-calling requires batch_size=1, got {self.batch_size}. "
                f"Each tool-calling entry needs its own conversation loop."
            )

        # Prompt version validation
        available = prompt_versions or ["naive", "custom"]
        if self.prompt_version not in available:
            errors.append(
                f"Unknown prompt_version '{self.prompt_version}'. "
                f"Available: {', '.join(available)}"
            )

        # Custom prompt file must exist
        if self.prompt_version == "custom":
            if not self.custom_prompt_path:
                errors.append("prompt_version='custom' requires custom_prompt_path")
            elif not Path(self.custom_prompt_path).exists():
                errors.append(f"Custom prompt file not found: {self.custom_prompt_path}")

        # Corpus path validation
        if self.corpus_path and not Path(self.corpus_path).exists():
            errors.append(f"Corpus file not found: {self.corpus_path}")

        # Positive integers
        if self.batch_size < 1:
            errors.append(f"batch_size must be >= 1, got {self.batch_size}")
        if self.concurrency < 1:
            errors.append(f"concurrency must be >= 1, got {self.concurrency}")
        if self.max_tokens < 100:
            errors.append(f"max_tokens must be >= 100, got {self.max_tokens}")

        return errors

    @property
    def model_id(self) -> str:
        """Resolve short model name to full OpenRouter model ID."""
        return MODEL_REGISTRY.get(self.model, self.model)

    @property
    def effective_temperature(self) -> float:
        """Return temperature, adjusted for models that reject exactly 0."""
        if self.temperature == 0 and self.model_id in NEEDS_NONZERO_TEMP:
            return 0.01
        return self.temperature

    def config_hash(self) -> str:
        """Deterministic hash of the config for cache keying.

        Excludes output_dir, run_name, dry_run, and corpus_path since
        they don't affect the actual translation results.
        """
        # Build a dict of only the fields that affect output
        relevant = {
            "model": self.model_id,
            "max_tokens": self.max_tokens,
            "tools_enabled": self.tools_enabled,
            "tools_list": sorted(self.tools_list) if self.tools_list else None,
            "batch_size": self.batch_size,
            "prompt_version": self.prompt_version,
            "post_hooks": sorted(self.post_hooks),
            "temperature": self.effective_temperature,
            "process_name": self.process_name,
        }
        raw = json.dumps(relevant, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    def to_dict(self) -> dict:
        """Serialize config to dict for JSON storage."""
        d = asdict(self)
        # Add computed fields for convenience
        d["_model_id"] = self.model_id
        d["_effective_temperature"] = self.effective_temperature
        d["_config_hash"] = self.config_hash()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RunConfig":
        """Deserialize config from dict (e.g., loaded from a RunLog)."""
        # Strip computed fields
        d = {k: v for k, v in d.items() if not k.startswith("_")}
        # Strip any fields not in the dataclass (forward compatibility)
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        d = {k: v for k, v in d.items() if k in valid_fields}
        return cls(**d)
