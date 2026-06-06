"""
Run Harness Configuration — All configurable knobs in one place.

Every parameter that affects a harness run is defined here as a typed
dataclass field. The config is serialized into every RunLog for full
reproducibility — any logged result can be exactly reproduced by
loading its config snapshot.

The TranslationProcess protocol defines the plugin interface: any
callable that takes structured input and returns structured output
can be registered as a translation method.

┌──────────────────────────────────────────────────────────────────┐
│  PERFORMANCE DEFAULTS — "Fast by default, safe by design"       │
│                                                                  │
│  The harness ships with aggressive defaults because:             │
│    • batch_size=25 cuts API calls by 25×                         │
│    • max_tokens=32768 eliminates truncation risk entirely        │
│    • concurrency=8 maximizes throughput per model                │
│    • cache=on prevents redundant API calls                       │
│                                                                  │
│  For multi-model runs, use execute_multi_run() to run all        │
│  models in parallel. Each gets its own session and semaphore.    │
│                                                                  │
│  All defaults are defined as constants below (search for         │
│  HARNESS_DEFAULTS). Change them in ONE place.                    │
└──────────────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Dataset registry — discover and resolve evaluation datasets
# ---------------------------------------------------------------------------

# Path to the bundled registry file (relative to package root)
_PACKAGE_DIR = Path(__file__).parent
_REGISTRY_PATH = _PACKAGE_DIR.parent / "datasets" / "registry.json"


def load_registry(registry_path: Path | None = None) -> dict:
    """Load the dataset registry from disk.

    Args:
        registry_path: Path to registry.json. Defaults to the bundled
            registry shipped with the harness package.

    Returns:
        Parsed registry dict with 'registry_version' and 'datasets' keys.

    Raises:
        FileNotFoundError: If the registry file does not exist.
    """
    path = registry_path or _REGISTRY_PATH
    if not path.exists():
        raise FileNotFoundError(f"Dataset registry not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_dataset(id_or_path: str, registry_path: Path | None = None) -> Path:
    """Resolve a dataset identifier to a local file path.

    Accepts either:
        - A filesystem path (absolute or relative) → returned directly
        - A registry dataset ID (e.g. 'edtekla-dev-v1') → looked up in
          the registry. If the registry entry has a URL, the dataset is
          downloaded and cached. If url is null, raises with instructions.

    Args:
        id_or_path: Filesystem path or registry dataset ID.
        registry_path: Optional override for the registry file location.

    Returns:
        Path to the local dataset JSON file.

    Raises:
        FileNotFoundError: If the path doesn't exist and the ID isn't in the registry.
        ValueError: If the registry entry has no download URL (private dataset).
    """
    # First, check if it's a path that exists
    candidate = Path(id_or_path)
    if candidate.exists():
        return candidate

    # Not a local path — try the registry
    try:
        registry = load_registry(registry_path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"'{id_or_path}' is not a local file and no dataset registry "
            f"was found. Provide a valid file path or install the registry."
        )

    datasets = registry.get("datasets", [])
    match = next((d for d in datasets if d["id"] == id_or_path), None)
    if not match:
        available = ", ".join(d["id"] for d in datasets) or "(none)"
        raise FileNotFoundError(
            f"Dataset '{id_or_path}' not found in registry. "
            f"Available: {available}. Or provide a local file path."
        )

    url = match.get("url")
    if not url:
        # Private dataset — no URL available
        access = match.get("access", "unknown")
        notes = match.get("notes", "")
        raise ValueError(
            f"Dataset '{id_or_path}' is {access} and has no download URL.\n"
            f"  {notes}\n"
            f"  Provide the local path with --corpus instead."
        )

    # URL is set — download and cache
    cache_dir = Path.home() / ".cache" / "gds-mt-eval" / "datasets"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Use sha256 of URL as cache filename
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    cached = cache_dir / f"{match['id']}_{url_hash}.json"

    if cached.exists():
        return cached

    # Download synchronously (simple, no async needed for a single file)
    import urllib.request
    print(f"  📥 Downloading dataset '{match['id']}' from {url}...")
    urllib.request.urlretrieve(url, cached)

    # Verify sha256 if provided
    expected_hash = match.get("sha256")
    if expected_hash:
        actual_hash = hashlib.sha256(cached.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            cached.unlink()
            raise ValueError(
                f"SHA-256 mismatch for '{match['id']}':\n"
                f"  Expected: {expected_hash}\n"
                f"  Got:      {actual_hash}\n"
                f"  The cached file has been deleted. Try again or report this."
            )

    print(f"  📦 Cached to {cached}")
    return cached


def format_registry_table(registry_path: Path | None = None) -> str:
    """Format the dataset registry as a human-readable table.

    Returns:
        Formatted string with dataset info, suitable for terminal output.
    """
    registry = load_registry(registry_path)
    datasets = registry.get("datasets", [])

    if not datasets:
        return "  No datasets registered."

    # Column widths
    lines = [
        "",
        "  Available Evaluation Datasets:",
        "",
        f"  {'ID':25s} {'Name':35s} {'Pair':10s} {'Size':>5s} {'Access':8s}",
        f"  {'-'*25} {'-'*35} {'-'*10} {'-'*5} {'-'*8}",
    ]
    for d in datasets:
        pair_info = d.get("language_pair", {})
        pair = f"{pair_info.get('source', '?')}→{pair_info.get('target', '?')}"
        lines.append(
            f"  {d['id']:25s} {d.get('name', ''):35s} {pair:10s} "
            f"{d.get('size', '?'):>5} {d.get('access', '?'):8s}"
        )

    lines.append("")
    lines.append("  Use: mt-eval run --corpus <local_path.json>")
    lines.append("  Or:  mt-eval run --corpus <dataset-id>  (if URL is set in registry)")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Method card — author-provided method description
# ---------------------------------------------------------------------------

# Valid method classes (must match the schema in docs/method-card-spec.md)
VALID_METHOD_CLASSES = frozenset({
    "raw-llm", "coached-llm", "pipeline", "custom-plugin", "api", "human",
})


def load_method_card(path: str | Path) -> dict:
    """Load and validate a method card JSON file.

    Args:
        path: Path to the method card JSON file.

    Returns:
        Validated method card dict.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        ValueError: If required fields are missing or invalid.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Method card not found: {path}")

    card = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_method_card(card)
    if errors:
        raise ValueError(
            f"Invalid method card ({path}):\n" +
            "\n".join(f"  - {e}" for e in errors)
        )
    return card


def validate_method_card(card: dict) -> list[str]:
    """Validate a method card dict against the schema.

    Args:
        card: Method card dictionary to validate.

    Returns:
        List of error messages (empty if valid).
    """
    errors = []

    # Required fields
    for required in ("method_id", "name", "class"):
        if required not in card:
            errors.append(f"Missing required field: '{required}'")

    # method_id format
    method_id = card.get("method_id", "")
    if method_id:
        import re
        if not re.match(r"^[a-z0-9][a-z0-9-]*$", method_id):
            errors.append(
                f"method_id '{method_id}' must be kebab-case "
                f"(lowercase alphanumeric + hyphens, starting with a letter or digit)"
            )

    # class enum
    method_class = card.get("class", "")
    if method_class and method_class not in VALID_METHOD_CLASSES:
        errors.append(
            f"Invalid class '{method_class}'. "
            f"Must be one of: {', '.join(sorted(VALID_METHOD_CLASSES))}"
        )

    # Type checks for optional fields
    if "tools_used" in card and not isinstance(card["tools_used"], list):
        errors.append("'tools_used' must be an array of strings")

    if "supported_pairs" in card and not isinstance(card["supported_pairs"], list):
        errors.append("'supported_pairs' must be an array of strings")

    for bool_field in ("open_source", "prompt_published"):
        if bool_field in card and not isinstance(card[bool_field], bool):
            errors.append(f"'{bool_field}' must be a boolean")

    return errors


# ===========================================================================
# HARNESS_DEFAULTS — Single source of truth for all default values.
#
# Change a default here and it propagates to RunConfig, CLI, docs, and
# scripts. No need to hunt across files. Agents: USE THESE, don't
# override them unless you have a specific reason.
# ===========================================================================

# Batching: entries per API call. 25 is proven reliable across all frontier
# models. Cuts API calls by 25×. Tool-calling auto-overrides to 1.
DEFAULT_BATCH_SIZE = 25

# Max tokens: generous headroom prevents truncation. Translation outputs
# are short (1-30 words typically), so unused tokens cost nothing.
# Set high to eliminate any risk of null/truncated output.
DEFAULT_MAX_TOKENS = 32768

# Concurrency: parallel batch calls within a single model run.
# Bounded by asyncio.Semaphore. 8 is safe for all providers.
# For multi-model parallelism, use execute_multi_run() instead.
DEFAULT_CONCURRENCY = 8

# Caching: file-backed, keyed on model + prompt + temperature + lang pair.
# Prevents re-calling the API for already-translated entries.
# There is almost never a reason to turn this off.
DEFAULT_CACHE_ENABLED = True
DEFAULT_CACHE_DIR = "eval/cache/harness"

# Temperature: 0 for deterministic output. Recorded in run cards.
DEFAULT_TEMPERATURE = 0.0

# Output directory for RunLog JSON files.
DEFAULT_OUTPUT_DIR = "eval/logs/harness"

# Tool-calling safety cap: max rounds per entry before giving up.
DEFAULT_MAX_TOOL_ROUNDS = 8


# ---------------------------------------------------------------------------
# Model registry — maps short names to OpenRouter model IDs
# ---------------------------------------------------------------------------
# This is a convenience lookup. You can always pass a full OpenRouter
# model ID directly (e.g. "anthropic/claude-opus-4.6").

MODEL_REGISTRY: dict[str, str] = {
    # Anthropic
    "claude-opus-4.7":   "anthropic/claude-opus-4.7",
    "claude-opus-4.6":   "anthropic/claude-opus-4.6",
    "claude-sonnet-4.6": "anthropic/claude-sonnet-4.6",
    "claude-sonnet-4":   "anthropic/claude-sonnet-4",
    # Google
    "gemini-3.5-flash":  "google/gemini-3.5-flash",
    "gemini-3.1-pro":    "google/gemini-3.1-pro-preview",
    "gemini-3-flash":    "google/gemini-3-flash-preview",
    "gemini-2.5-flash":  "google/gemini-2.5-flash",
    # OpenAI
    "gpt-5.5":           "openai/gpt-5.5",
    # DeepSeek
    "deepseek-v4-pro":   "deepseek/deepseek-v4-pro",
    "deepseek-r1":       "deepseek/deepseek-r1-0528",
    # Qwen
    "qwen3-235b":        "qwen/qwen3-235b-a22b",
}

DEFAULT_MODEL = "gemini-3.1-pro"

# Models that reject temperature=0 (require 0.01 minimum)
NEEDS_NONZERO_TEMP: set[str] = {
    "anthropic/claude-opus-4.7",
    "anthropic/claude-opus-4.6",
    "anthropic/claude-opus-4.5",
    "anthropic/claude-opus-4.1",
    "anthropic/claude-opus-4",
    "anthropic/claude-sonnet-4.6",
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
            entries: List of dicts with at least the source field and 'id' keys.
                     (The source text key is determined by config.source_field,
                      which defaults to 'source'.)
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

    ┌──────────────────────────────────────────────────────────────┐
    │  DEFAULTS ARE INTENTIONALLY AGGRESSIVE                      │
    │                                                              │
    │  • batch_size  = 25     → 25× fewer API calls               │
    │  • max_tokens  = 32768  → zero truncation risk               │
    │  • concurrency = 8      → parallel batches per model         │
    │  • cache       = on     → no redundant API calls             │
    │                                                              │
    │  These defaults come from HARNESS_DEFAULTS constants above.  │
    │  Do NOT lower them without a specific reason.                │
    │                                                              │
    │  For multi-model runs, use execute_multi_run() to run all    │
    │  models in parallel — each gets its own session/semaphore.   │
    │  DO NOT loop sequentially over execute_run().                │
    └──────────────────────────────────────────────────────────────┘
    """

    # --- Dataset selection ---
    # "all" = full corpus, or segment name, or "0-61" range
    dataset: str = "all"
    # Human-readable dataset ID for run cards and the leaderboard.
    # Auto-populated from corpus metadata if not set explicitly.
    dataset_id: str = ""
    # Explicit entry IDs override dataset if provided
    entry_ids: list[int] | None = None

    # --- Corpus ---
    # Path to the corpus file. Supports multiple formats:
    #   .json  — Harness JSON (wrapped or flat list)
    #   .jsonl — One JSON object per line (HuggingFace style)
    #   .tsv   — Tab-separated (source<tab>reference per line)
    # For parallel text files, use source_file + reference_file instead.
    corpus_path: str | None = None

    # --- Parallel text mode ---
    # For FLORES+, WMT, NTREX, and other standard MT corpora that ship
    # as aligned text files (one sentence per line).
    source_file: str | None = None     # --source-file path
    reference_file: str | None = None  # --reference-file path

    # --- Source / target field names ---
    # These map to the JSON keys in your corpus file.
    source_field: str = "source"       # The field name for source text in corpus
    target_field: str = "reference"    # The field name for gold-standard translation

    # --- Language pair ---
    # Human-readable language names used in prompts and run cards.
    # The naive prompt interpolates target_lang to tell the model WHAT
    # language to translate into. Without this, models guess randomly.
    source_lang: str = "English"
    target_lang: str = ""  # e.g. "Plains Cree (nêhiyawêwin, SRO)"

    # --- Segment names ---
    # The valid segment names in your corpus (for dataset filtering).
    # Leave empty to auto-detect from the corpus at load time.
    segment_names: list[str] = field(default_factory=list)

    # --- Model ---
    model: str = DEFAULT_MODEL  # Short name, resolved via MODEL_REGISTRY
    max_tokens: int = DEFAULT_MAX_TOKENS

    # --- Tool calling ---
    # Individual toggles for each tool (None = all available tools)
    tools_enabled: bool = False
    # List of individual tool names to enable, e.g. ["fst_validate", "fst_generate"]
    # None means all tools. Only used when tools_enabled is True.
    tools_list: list[str] | None = None
    max_tool_rounds: int = DEFAULT_MAX_TOOL_ROUNDS

    # --- Caching ---
    cache_enabled: bool = DEFAULT_CACHE_ENABLED
    cache_dir: str = DEFAULT_CACHE_DIR

    # --- Batching ---
    # Entries per API call. >1 = numbered list format.
    # Tool-calling auto-overrides to 1 (each entry needs its own
    # conversation loop). See validate() for the override logic.
    batch_size: int = DEFAULT_BATCH_SIZE

    # --- Concurrency ---
    # Number of parallel API calls within a single model run.
    # Bounded by asyncio.Semaphore for rate limit safety.
    # For multi-model parallelism, use execute_multi_run().
    concurrency: int = DEFAULT_CONCURRENCY

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
    output_dir: str = DEFAULT_OUTPUT_DIR
    run_name: str | None = None  # Optional human-readable label

    # --- Misc ---
    temperature: float = DEFAULT_TEMPERATURE
    dry_run: bool = False      # Validate config without API calls

    # --- Process plugin ---
    # If set, uses a custom TranslationProcess instead of the built-in
    # LLM caller. The process_name is logged for identification.
    process_name: str | None = None

    # --- Champollion config interop ---
    # Enables config interchangeability with champollion production CLI.
    # When set, --prompt champollion uses the config to build production-
    # identical prompts with register, gender guidance, and promptContext.
    champollion_config_path: str | None = None   # --champollion-config path
    champollion_cards_dir: str | None = None     # --champollion-cards-dir path
    target_lang_code: str = ""               # --target-lang-code (e.g., "fr")

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

        # Tool-calling requires batch_size=1 — auto-override with warning
        # instead of erroring, so the default batch_size=25 doesn't block
        # tool-calling runs.
        if self.tools_enabled and self.batch_size > 1:
            import sys
            print(
                f"  ⚠ batch_size={self.batch_size} auto-overridden to 1 "
                f"(tool-calling requires individual entry conversations)",
                file=sys.stderr,
            )
            self.batch_size = 1

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

        # Champollion config validation
        if self.prompt_version == "champollion" or self.champollion_config_path:
            if self.champollion_config_path and not Path(self.champollion_config_path).exists():
                errors.append(f"Champollion config not found: {self.champollion_config_path}")
            if self.champollion_config_path and not self.target_lang_code:
                errors.append(
                    "--champollion-config requires --target-lang-code. "
                    "Provide the BCP-47 code for the target language (e.g., 'fr', 'de', 'crk')."
                )
            if self.prompt_version == "champollion" and not self.champollion_config_path:
                errors.append(
                    "--prompt champollion requires --champollion-config. "
                    "Provide the path to your champollion.config.json."
                )

        # Parallel text: both files must be provided together
        if self.source_file and not self.reference_file:
            errors.append("--source-file requires --reference-file.")
        if self.reference_file and not self.source_file:
            errors.append("--reference-file requires --source-file.")

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
            # Language pair affects prompts, so it must affect cache keys.
            # Otherwise switching target_lang would serve stale translations.
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
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
