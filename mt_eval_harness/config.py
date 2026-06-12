"""
Run Harness Configuration — All configurable knobs in one place.

Every parameter that affects a harness run is defined here as a typed
dataclass field. The config is serialized into every RunLog for full
reproducibility — any logged result can be exactly reproduced by
loading its config snapshot.

The TranslationMethod protocol defines the plugin interface: any
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
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


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


# ---------------------------------------------------------------------------
# Eval pack dependency gate
# ---------------------------------------------------------------------------
#
# The eval pack gate prevents evaluation against a dataset whose target
# language requires tools that aren't installed. It reads requirements
# from the language card's `evalPack` field — no language-specific code.
#
# Adding eval pack support for a new language = editing ONE JSON file
# (the language card). The harness checks it generically.


def _check_eval_pack(dataset_entry: dict) -> None:
    """Verify that eval pack dependencies for a dataset's target language
    are installed.

    Reads the target language from the dataset's ``language_pair.target``,
    looks up the language card, and checks its ``evalPack`` requirements.
    If dependencies are missing, raises a RuntimeError with a clear
    message telling the user exactly which command to run.

    This is fully data-driven — the language card is the SSOT. No
    language-specific code exists in this function.
    """
    # Determine the target language from the dataset entry
    lang_pair = dataset_entry.get("language_pair", {})
    target_code = lang_pair.get("target")
    if not target_code:
        return  # No target language declared — skip check

    # Look up the language card's eval pack requirements
    from mt_eval_harness.language_cards import get_eval_pack, get_name
    pack = get_eval_pack(target_code)
    if not pack:
        return  # No eval pack for this language — proceed

    missing = []

    # Check Python dependencies declared in the eval pack
    for import_name, pip_spec in pack.get("pythonDeps", {}).items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(f"{pip_spec} ({import_name})")

    # Check FST files if required
    if pack.get("requiresFst"):
        from mt_eval_harness.plugins.fst_installer import is_fst_installed
        if not is_fst_installed(target_code):
            lang_name = get_name(target_code) or target_code
            missing.append(f"FST morphological analyzer ({lang_name})")

    if not missing:
        return  # Everything installed — proceed

    dataset_id = dataset_entry["id"]
    lang_name = get_name(target_code) or target_code
    setup_cmd = f"mt-eval setup --lang {target_code}"
    missing_str = "\n".join(f"    ✗ {m}" for m in missing)

    raise RuntimeError(
        f"\n"
        f"  ┌──────────────────────────────────────────────────────────┐\n"
        f"  │  EVAL PACK REQUIRED: {lang_name:<36} │\n"
        f"  │                                                          │\n"
        f"  │  Dataset '{dataset_id}' targets {target_code.upper()} which requires     │\n"
        f"  │  evaluation tools that are not yet installed.             │\n"
        f"  └──────────────────────────────────────────────────────────┘\n"
        f"\n"
        f"  Missing:\n"
        f"{missing_str}\n"
        f"\n"
        f"  To install everything at once:\n"
        f"    {setup_cmd}\n"
    )




def resolve_dataset(id_or_path: str, registry_path: Path | None = None) -> Path:
    """Resolve a dataset identifier to a local file path.

    Accepts either:
        - A filesystem path (absolute or relative) → returned directly
        - A registry dataset ID (e.g. 'edtekla-dev-v1') → looked up in
          the registry. Resolution chain:
            1. local_path → resolved relative to monorepo root
            2. url → downloaded and cached
            3. Neither → error with instructions

    Args:
        id_or_path: Filesystem path or registry dataset ID.
        registry_path: Optional override for the registry file location.

    Returns:
        Path to the local dataset JSON file.

    Raises:
        FileNotFoundError: If the path doesn't exist and the ID isn't in the registry.
        ValueError: If the registry entry has no download URL or local path.
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

    # Match by ID or alias
    match = next((d for d in datasets if d["id"] == id_or_path), None)
    if not match:
        # Check aliases — datasets can declare alternative names
        # (e.g., "edtekla-full" → "edtekla-textbook")
        match = next(
            (d for d in datasets
             if id_or_path in d.get("aliases", [])),
            None,
        )

    if not match:
        # No exact match or alias — suggest closest with fuzzy matching
        import difflib
        all_ids = [d["id"] for d in datasets]
        # Also include aliases for matching
        all_searchable = list(all_ids)
        for d in datasets:
            all_searchable.extend(d.get("aliases", []))
        close = difflib.get_close_matches(id_or_path, all_searchable, n=5, cutoff=0.4)
        if close:
            suggestions = ", ".join(close)
            raise FileNotFoundError(
                f"Dataset '{id_or_path}' not found in registry. "
                f"Did you mean: {suggestions}? "
                f"Or provide a local file path."
            )
        # No close match — show a truncated list
        shown = all_ids[:10]
        suffix = f" (and {len(all_ids) - 10} more)" if len(all_ids) > 10 else ""
        raise FileNotFoundError(
            f"Dataset '{id_or_path}' not found in registry. "
            f"Available: {', '.join(shown)}{suffix}. "
            f"Or provide a local file path."
        )

    # --- Eval pack dependency gate ---
    # Datasets can declare `eval_pack` (e.g., "crk") to require specific
    # evaluation dependencies. This ensures nobody runs CRK evaluation
    # without the FST, linter, and other required tools installed.
    _check_eval_pack(match)

    # Check for a local_path (relative to monorepo root)
    local_path = match.get("local_path")
    if local_path:
        # Resolve relative to the monorepo root (parent of arena/)
        monorepo_root = _PACKAGE_DIR.parent.parent
        resolved = monorepo_root / local_path
        if resolved.exists():
            return resolved
        # Local path declared but file not found — fall through to URL/error
        logger.debug(
            "local_path '%s' for dataset '%s' resolved to '%s' but not found",
            local_path, id_or_path, resolved,
        )

    url = match.get("url")
    if not url:
        # Private dataset — no URL available
        access = match.get("access", "unknown")
        notes = match.get("notes", "")
        hint = f"\n  local_path: {local_path}" if local_path else ""
        raise ValueError(
            f"Dataset '{id_or_path}' is {access} and has no download URL.{hint}\n"
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
        f"  {'ID':25s} {'Name':35s} {'Pair':10s} {'Size':>5s} {'Avail':5s}",
        f"  {'-'*25} {'-'*35} {'-'*10} {'-'*5} {'-'*5}",
    ]

    monorepo_root = _PACKAGE_DIR.parent.parent

    for d in datasets:
        pair_info = d.get("language_pair", {})
        pair = f"{pair_info.get('source', '?')}→{pair_info.get('target', '?')}"

        # Check if the dataset is locally available
        local_path = d.get("local_path")
        avail = ""
        if local_path:
            resolved = monorepo_root / local_path
            avail = "✓" if resolved.exists() else "✗"
        elif d.get("url"):
            avail = "↓"  # downloadable

        lines.append(
            f"  {d['id']:25s} {d.get('name', ''):35s} {pair:10s} "
            f"{d.get('size', '?'):>5} {avail:5s}"
        )

    lines.append("")
    lines.append("  Avail: ✓ = local  ↓ = downloadable  ✗ = path not found  (blank) = private")
    lines.append("")
    lines.append("  Use: mt-eval run --corpus <dataset-id>       (resolves from registry)")
    lines.append("       mt-eval run --corpus <local_path.json>  (direct file path)")
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
# Model aliases — maps short names to OpenRouter model IDs
# ---------------------------------------------------------------------------
# Loaded from shared/model-aliases.json (shared with the CLI) so both
# tools accept the same short names. Falls back to a hardcoded dict
# when running outside the monorepo (standalone pip install).
#
# You can always pass a full OpenRouter model ID directly
# (e.g. "anthropic/claude-sonnet-4"). The alias file is just convenience.

def _load_model_aliases() -> dict[str, str]:
    """Load model aliases from the shared JSON file.

    Search order:
      1. shared/model-aliases.json relative to the monorepo root
         (detected by walking up from this file's directory)
      2. Hardcoded fallback for standalone installs

    Returns:
        Dict mapping short names → full OpenRouter model IDs.
    """
    # Walk up from this package to find the monorepo shared/ directory
    check = _PACKAGE_DIR
    for _ in range(6):
        candidate = check / "shared" / "model-aliases.json"
        if candidate.exists():
            try:
                aliases = json.loads(candidate.read_text(encoding="utf-8"))
                # Strip non-alias keys (like _comment)
                return {k: v for k, v in aliases.items() if not k.startswith("_")}
            except Exception as e:
                logger.debug(
                    "Failed to load model aliases from %s: %s", candidate, e
                )
                break
        check = check.parent

    # Fallback: hardcoded aliases for standalone installs
    return {
        "gemini-flash":  "google/gemini-3.5-flash",
        "gemini-pro":    "google/gemini-3.1-pro-preview",
        "claude-sonnet": "anthropic/claude-sonnet-4",
        "gpt":           "openai/gpt-5.5",
        # Extended aliases for backward compatibility
        "claude-opus-4.7":   "anthropic/claude-opus-4.7",
        "claude-opus-4.6":   "anthropic/claude-opus-4.6",
        "claude-sonnet-4.6": "anthropic/claude-sonnet-4.6",
        "claude-sonnet-4":   "anthropic/claude-sonnet-4",
        "gemini-3.5-flash":  "google/gemini-3.5-flash",
        "gemini-3.1-pro":    "google/gemini-3.1-pro-preview",
        "gemini-3-flash":    "google/gemini-3-flash-preview",
        "gemini-2.5-flash":  "google/gemini-2.5-flash",
        "gpt-5.5":           "openai/gpt-5.5",
        "deepseek-v4-pro":   "deepseek/deepseek-v4-pro",
        "deepseek-r1":       "deepseek/deepseek-r1-0528",
        "qwen3-235b":        "qwen/qwen3-235b-a22b",
    }


MODEL_REGISTRY: dict[str, str] = _load_model_aliases()


def fuzzy_resolve_model(name: str) -> str | None:
    """Try to resolve a partial model name to a full OpenRouter slug.

    Resolution chain:
        1. Exact match in MODEL_REGISTRY → return the full slug
        2. Name already contains "/" → assume it's a full slug, return as-is
        3. Check known vendor prefixes (anthropic, google, openai, etc.)
           and try "{vendor}/{name}" as a plausible OpenRouter slug
        4. Check if the name is a substring of any registry value
           (handles e.g. 'fable-5' matching 'anthropic/claude-fable-5')

    This avoids requiring a live OpenRouter API call for common cases.
    Returns None if no match can be inferred.
    """
    # 1. Exact registry match
    if name in MODEL_REGISTRY:
        return MODEL_REGISTRY[name]

    # 2. Already a full slug (contains vendor prefix)
    if "/" in name:
        return name

    # 3. Known vendor prefix heuristics
    # Map common model name prefixes → vendor namespace on OpenRouter
    _VENDOR_PREFIXES = {
        "claude":    "anthropic",
        "gemini":    "google",
        "gpt":       "openai",
        "o1":        "openai",
        "o3":        "openai",
        "o4":        "openai",
        "deepseek":  "deepseek",
        "qwen":      "qwen",
        "llama":     "meta-llama",
        "mistral":   "mistralai",
        "command":   "cohere",
        "glm":       "z-ai",
    }

    name_lower = name.lower()
    for prefix, vendor in _VENDOR_PREFIXES.items():
        if name_lower.startswith(prefix):
            candidate = f"{vendor}/{name}"
            logger.info(
                "Fuzzy model match: '%s' → '%s' (inferred from '%s' prefix)",
                name, candidate, prefix,
            )
            return candidate

    # 4. Substring match against registry values
    # Handles cases like 'fable-5' appearing in 'anthropic/claude-fable-5'
    for alias, full_slug in MODEL_REGISTRY.items():
        if name_lower in full_slug.lower():
            logger.info(
                "Fuzzy model match: '%s' → '%s' (substring of '%s')",
                name, full_slug, alias,
            )
            return full_slug

    return None


DEFAULT_MODEL = "gemini-pro"

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
# Plugin protocol — any translation method implements this
# ---------------------------------------------------------------------------

@runtime_checkable
class TranslationMethod(Protocol):
    """Protocol for pluggable translation methods.

    A method is a black box: source text in, translation out. The harness
    doesn't care what happens inside — it scores the output. Methods can be:
        - A custom multi-stage pipeline (decomp-recomp, backtranslation)
        - A fine-tuned model endpoint
        - A traditional MT system (Moses, Apertium)
        - A commercial API wrapper (Google Translate, DeepL)
        - Anything that produces translations

    The method receives a batch of entries (even if batch_size=1)
    and returns one result dict per entry.

    Why a protocol instead of a base class:
        Structural typing — existing pipelines don't need to inherit
        from anything. If it has the right method signature, it works.
    """

    @property
    def name(self) -> str:
        """Human-readable method name for run IDs and logs."""
        ...

    def method_card(self) -> dict | None:
        """Return method metadata for provenance tracking.

        The method card is embedded in the RunLog and published run card
        so results can be attributed to a specific method configuration.

        Returns None if the method doesn't provide a card (e.g., the
        built-in default LLM method — its provenance is captured via
        model, coaching prompt, temperature, etc.).

        Typical fields:
            name, method_id, class, author, description,
            tools_used, supported_pairs
        """
        ...

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
    # "naive" = minimal instruction ("translate X to Y")
    # "custom" = load from custom_prompt_path (deprecated, use coaching_file)
    # Coaching prompts are free text — the full text is recorded in the
    # run card for reproducibility. There are no named prompt versions.
    prompt_version: str = "naive"
    custom_prompt_path: str | None = None  # DEPRECATED: use coaching_file
    coaching_file: str | None = None  # Path to coaching prompt text file
    style_profile: str | None = None  # Path to style profile JSON (informational metrics)

    # --- Post-translation hooks ---
    # List of hook names to apply (e.g. ["fst_gate"])
    # Hooks are registered externally via PostTranslationHook plugins
    post_hooks: list[str] = field(default_factory=list)

    # --- FST retry ---
    # Number of times to retry a translation that fails FST validation.
    # 0 = score-only (no retry). Works with the default LLM method only;
    # custom method plugins handle their own retry logic internally.
    fst_retries: int = 0

    # --- Output ---
    output_dir: str = DEFAULT_OUTPUT_DIR
    run_name: str | None = None  # Optional human-readable label

    # --- Misc ---
    temperature: float = DEFAULT_TEMPERATURE
    dry_run: bool = False      # Validate config without API calls
    # Skip interactive confirmation prompts (--yes). Required for
    # fetch-from-source corpus builds in CI/scripted runs: accepting
    # the upstream data license non-interactively.
    assume_yes: bool = False

    # --- Method plugin ---
    # Path to a method plugin directory containing method.json + Python
    # module. When set, the harness delegates translation to the plugin
    # instead of using the built-in LLM caller. The method is a black box:
    # source text in, translation out. The harness just scores the output.
    method_path: str | None = None
    # Legacy alias for process_name — kept for backward compatibility
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

        # Model resolution — allow short names, full IDs, and fuzzy matches.
        # Full IDs (containing "/") pass through. Short names are looked up
        # in MODEL_REGISTRY. Unrecognized names get fuzzy-matched via
        # vendor prefix heuristics before erroring.
        if self.model not in MODEL_REGISTRY and "/" not in self.model:
            resolved = fuzzy_resolve_model(self.model)
            if resolved:
                import sys
                print(
                    f"  ℹ Resolved '{self.model}' → '{resolved}' (fuzzy match)",
                    file=sys.stderr,
                )
                self.model = resolved
            else:
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
        available = prompt_versions or ["naive", "custom", "coached"]
        if self.prompt_version not in available:
            errors.append(
                f"Unknown prompt_version '{self.prompt_version}'. "
                f"Available: {', '.join(available)}"
            )

        # "coached" is the auto-derived label for runs where a coaching
        # prompt replaces the naive one — it is meaningless without one.
        if self.prompt_version == "coached":
            if not (self.coaching_file or self.custom_prompt_path):
                errors.append(
                    "prompt_version='coached' requires --coaching-file or "
                    "--coaching (it is auto-set when coaching is provided)."
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

        # Corpus path validation — try registry resolution for non-path IDs.
        # Users can pass either a filesystem path or a registry dataset ID
        # (e.g. 'edtekla-dev-v1'). If the raw path doesn't exist, try
        # resolving it through the dataset registry before erroring.
        if self.corpus_path and not Path(self.corpus_path).exists():
            try:
                resolved_path = resolve_dataset(self.corpus_path)
                self.corpus_path = str(resolved_path)
            except (FileNotFoundError, ValueError) as e:
                # Fetch-from-source fallback: if a corpora card with a
                # `source` block matches this path, the corpus can be
                # rebuilt from the upstream repo at load time. Don't
                # error here — corpus_loader performs the fetch (with a
                # license prompt, or automatically with --yes/CI).
                from mt_eval_harness.corpus_fetch import find_card_for_corpus
                if find_card_for_corpus(self.corpus_path) is None:
                    errors.append(
                        f"Corpus file not found: {self.corpus_path} ({e})"
                    )

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
            # Coaching prompt content hash — different coaching files should
            # produce different cache keys. We hash the content, not the path,
            # so identical prompts in different files still share cache.
            "coaching_sha": self._coaching_content_hash(),
            # FST retry count affects the final translation output (retried
            # translations may differ from first-pass ones).
            "fst_retries": self.fst_retries,
        }
        raw = json.dumps(relevant, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    def _coaching_content_hash(self) -> str | None:
        """Hash the coaching file content for cache keying.

        Returns None if no coaching file is set, so the cache key
        doesn't change for non-coached runs.
        """
        path = self.coaching_file or self.custom_prompt_path
        if not path:
            return None
        try:
            content = Path(path).read_bytes()
            return hashlib.sha256(content).hexdigest()[:12]
        except (FileNotFoundError, OSError):
            # If the file doesn't exist, include the path as a fallback
            # so different missing paths don't share cache keys.
            return hashlib.sha256(path.encode()).hexdigest()[:12]

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
