"""
Champollion Config Reader — Load champollion.config.json for harness use.

Reads the production champollion config and language card files to
extract register, gender guidance, and prompt context for a specific
target language. This enables config interchangeability between the
production CLI and the evaluation harness.

The reader accesses language card JSON files directly from the filesystem
(no Node.js dependency). In a monorepo layout, the cards live at
`shared/language-cards/`. For standalone usage, they'd be at
`node_modules/champollion/shared/language-cards/`.

Usage:
    rc = load_champollion_config("champollion.config.json", "fr", cards_dir="shared/language-cards/")
    print(rc.register)         # "Use casual tu-form..."
    print(rc.gender_guidance)  # "Use écriture épicène..."
    print(rc.prompt_context)   # "This is a messaging app..."
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Language code aliases — mirrors lib/registers.js resolveCode()
# ---------------------------------------------------------------------------

# Common aliases that map non-canonical codes to their canonical form.
# This is the same mapping as resolveCode() in registers.js.
CODE_ALIASES: dict[str, str] = {
    "no": "nb",       # Norwegian → Bokmål
    "iw": "he",       # Legacy Hebrew
    "in": "id",       # Legacy Indonesian
    "ji": "yi",       # Legacy Yiddish
    "jw": "jv",       # Legacy Javanese
    "mo": "ro",       # Moldavian → Romanian
    "sh": "sr",       # Serbo-Croatian → Serbian
    "tl": "fil",      # Tagalog → Filipino (note: we have a card for "tl")
}

# Region fallbacks: pt-PT → pt, es-MX → es, fr-CA → fr, zh-TW → zh
# These are checked if no exact card match exists.


def resolve_code(code: str) -> str:
    """Resolve a language code to its canonical form.

    Mirrors the resolveCode() function in lib/registers.js:
    1. Check direct alias mapping
    2. Try base language (strip region subtag)
    3. Return as-is if no resolution found
    """
    if code in CODE_ALIASES:
        return CODE_ALIASES[code]
    return code


# ---------------------------------------------------------------------------
# Language card reader
# ---------------------------------------------------------------------------

def _find_cards_dir() -> Path | None:
    """Auto-detect the language cards directory.

    Search order:
    1. Monorepo layout: look for shared/language-cards/ relative to CWD
       walking up the tree (handles being run from any subdirectory)
    2. npm install: look for node_modules/champollion/shared/language-cards/

    Returns None if not found (caller should raise with a helpful message).
    """
    cwd = Path.cwd()

    # Walk up from CWD looking for the monorepo marker
    check = cwd
    for _ in range(10):  # Don't walk up more than 10 levels
        candidate = check / "shared" / "language-cards"
        if candidate.is_dir():
            return candidate
        # Also check if we're inside the harness looking at a sibling
        sibling = check.parent / "shared" / "language-cards"
        if sibling.is_dir():
            return sibling
        check = check.parent

    # npm fallback
    npm_path = cwd / "node_modules" / "champollion" / "shared" / "language-cards"
    if npm_path.is_dir():
        return npm_path

    return None


def load_language_card(code: str, cards_dir: Path) -> dict | None:
    """Load a single language card JSON file, recursively resolving extends parent cards.

    Scans the cards_dir recursively, indexing all cards by their 'code' property,
    then resolves aliases, base language fallbacks, and the extends hierarchy.
    """
    if not cards_dir.is_dir():
        return None

    all_cards = {}
    aliases = {}

    for p in cards_dir.rglob("*.json"):
        try:
            card = json.loads(p.read_text(encoding="utf-8"))
            card_code = card.get("code")
            if card_code:
                all_cards[card_code] = card
                for alias in card.get("aliases", []):
                    aliases[alias] = card_code
        except Exception as e:
            print(f"[WARN] Failed to parse card file {p}: {e}")

    resolved_cards = {}

    def resolve_card(c_code: str, visited=None) -> dict | None:
        if visited is None:
            visited = set()
        if c_code in visited:
            print(f"[WARN] Circular dependency detected for card code '{c_code}'")
            return None
        visited.add(c_code)

        if c_code in resolved_cards:
            return resolved_cards[c_code]

        # Try direct match in scanned cards
        card = all_cards.get(c_code)
        if not card:
            # Try alias resolution
            canonical = aliases.get(c_code)
            if not canonical:
                canonical = resolve_code(c_code)
            if canonical in all_cards:
                card = all_cards.get(canonical)
            elif "-" in c_code:
                # Try base language (strip region subtag)
                base = c_code.split("-")[0]
                card = all_cards.get(base)

        if not card:
            return None

        import copy
        card_copy = copy.deepcopy(card)

        # Resolve extends
        parent_code = card_copy.get("extends")
        if parent_code:
            parent_card = resolve_card(parent_code, visited)
            if parent_card:
                card_copy = deep_merge_cards(parent_card, card_copy)
            else:
                print(f"[WARN] Language card '{c_code}' extends unknown card '{parent_code}'.")

        resolved_cards[c_code] = card_copy
        return card_copy

    return resolve_card(code)


def deep_merge_cards(parent: dict, child: dict) -> dict:
    """Deep merge two dictionaries, child keys override parent keys."""
    merged = parent.copy()
    for key, value in child.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = deep_merge_cards(merged[key], value)
        else:
            merged[key] = value
    return merged


def _get_register_from_card(card: dict, preset_key: str | None = None) -> str:
    """Extract register prompt text from a language card.

    If preset_key is provided, looks up that specific preset.
    Otherwise uses the card's default (from formality.default or first key).

    Mirrors getRegister() in lib/registers.js.

    Card structure:
        card.registers = {
            "formal-vous": { "label": "...", "prompt": "Use vous-form...", ... },
            "casual-tu":   { "label": "...", "prompt": "Use tu-form...", ... }
        }
        card.formality.default = "formal-vous"  (optional)
    """
    registers = card.get("registers", {})
    if not registers:
        return preset_key or "Professional register."

    # No user override — use card's default preset
    if not preset_key:
        formality = card.get("formality", {})
        default_key = formality.get("default") or next(iter(registers), None)
        if default_key and default_key in registers:
            return registers[default_key].get("prompt", "Professional register.")
        return "Professional register."

    # Check if it's a preset name
    if preset_key in registers:
        return registers[preset_key].get("prompt", "Professional register.")

    # Not a preset name — treat as custom register text (pass-through)
    return preset_key


def _get_gender_guidance(card: dict) -> str | None:
    """Extract gender guidance from a language card.

    Mirrors getGenderGuidance() in lib/registers.js.
    """
    gender = card.get("gender", {})
    guidance = gender.get("inclusiveGuidance")
    if guidance and isinstance(guidance, str) and len(guidance) > 10:
        return guidance
    return None


# ---------------------------------------------------------------------------
# Config reader
# ---------------------------------------------------------------------------

@dataclass
class ChampollionPromptConfig:
    """Prompt configuration extracted from champollion.config.json.

    Contains everything needed to build a production-identical system
    prompt for a specific target language.
    """
    target_lang_name: str        # Human-readable name, e.g., "French"
    target_lang_code: str        # BCP-47 code, e.g., "fr"
    register: str                # Full register text for prompt injection
    gender_guidance: str | None  # Per-language gender guidance, or None
    prompt_context: str | None   # Global context string from config


def load_champollion_config(
    config_path: str | Path,
    target_lang_code: str,
    cards_dir: str | Path | None = None,
) -> ChampollionPromptConfig:
    """Load a champollion.config.json and extract prompt config for a target language.

    This is the bridge between the champollion config format and the harness.
    It reads the same config file that the production CLI reads, and
    extracts the register, gender guidance, and prompt context for the
    specified target language.

    Args:
        config_path: Path to champollion.config.json.
        target_lang_code: BCP-47 code for the target language (e.g., "fr").
        cards_dir: Path to language-cards directory. If None, auto-detects
            from monorepo layout or npm install.

    Returns:
        ChampollionPromptConfig with all fields populated.

    Raises:
        FileNotFoundError: If config or cards directory not found.
        ValueError: If target language has no card.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Champollion config not found: {config_path}")

    champollion_config = json.loads(config_path.read_text(encoding="utf-8"))

    # Resolve cards directory
    if cards_dir:
        cards_dir = Path(cards_dir)
    else:
        cards_dir = _find_cards_dir()

    if not cards_dir or not cards_dir.is_dir():
        raise FileNotFoundError(
            f"Language cards directory not found. "
            f"Set --champollion-cards-dir to the path containing language card JSON files "
            f"(e.g., shared/language-cards/ in the champollion repo)."
        )

    # Load the language card for the target
    card = load_language_card(target_lang_code, cards_dir)
    if not card:
        raise ValueError(
            f"No language card found for '{target_lang_code}' in {cards_dir}. "
            f"Available: {', '.join(p.stem for p in sorted(cards_dir.glob('*.json')))}"
        )

    # Resolve register preset override from config.
    #
    # The production config supports two entry points for register overrides:
    #
    # 1. "languages" block (simple mode):
    #    "languages": { "fr": "casual-tu" }
    #    "languages": { "fr": { "register": "casual-tu" } }
    #    "languages": ["fr", "de"]  (no override, uses card default)
    #
    # 2. "pairs" block (advanced mode — most common in real configs):
    #    "pairs": { "en:fr": { "register": "casual-tu" } }
    #
    # We check both, with languages taking precedence (mirrors the JS
    # resolution order in pairs.js where languages are applied first,
    # then pairs override).
    preset_override = None
    source_locale = champollion_config.get("sourceLocale", "en")
    canonical = resolve_code(target_lang_code)

    # Check "languages" block first
    languages = champollion_config.get("languages", {})
    if isinstance(languages, dict) and languages:
        lang_config = languages.get(target_lang_code) or languages.get(canonical)
        if isinstance(lang_config, str):
            preset_override = lang_config
        elif isinstance(lang_config, dict) and "register" in lang_config:
            preset_override = lang_config["register"]
    elif isinstance(languages, list):
        pass  # Array form: ["fr", "de"] — no register override

    # Check "pairs" block if languages didn't specify a register
    if not preset_override:
        pairs = champollion_config.get("pairs", {})
        if isinstance(pairs, dict):
            # Try common pair key formats: "en:fr", "en→fr"
            pair_key = f"{source_locale}:{target_lang_code}"
            pair_config = pairs.get(pair_key)
            if pair_config is None:
                pair_key = f"{source_locale}:{canonical}"
                pair_config = pairs.get(pair_key)
            if pair_config is None:
                # Try arrow format
                pair_key = f"{source_locale}→{target_lang_code}"
                pair_config = pairs.get(pair_key)
            if pair_config is None:
                pair_key = f"{source_locale}→{canonical}"
                pair_config = pairs.get(pair_key)

            if isinstance(pair_config, dict) and "register" in pair_config:
                preset_override = pair_config["register"]

    # Also check top-level registerPreset as a global default
    if not preset_override:
        preset_override = champollion_config.get("registerPreset")

    # Build the config
    register = _get_register_from_card(card, preset_override)
    gender_guidance = _get_gender_guidance(card)
    prompt_context = champollion_config.get("promptContext")

    # Language name from card
    lang_name = card.get("name", target_lang_code)

    return ChampollionPromptConfig(
        target_lang_name=lang_name,
        target_lang_code=target_lang_code,
        register=register,
        gender_guidance=gender_guidance,
        prompt_context=prompt_context,
    )


# ---------------------------------------------------------------------------
# Prompt builder — Python port of buildSystemMessage() from llm.js
# ---------------------------------------------------------------------------
#
# This MUST produce identical output to the JS function in:
#   lib/methods/llm.js → buildSystemMessage(langConfig)
#
# The JS function accepts { name, register, genderGuidance?, promptContext? }
# and returns a system prompt string. This Python function takes a
# ChampollionPromptConfig (same fields, different names) and returns the
# same string.
#
# SYNC NOTE: If the JS prompt template changes, update this function
# and verify with the parity test.
# ---------------------------------------------------------------------------

def build_champollion_system_prompt(rc: ChampollionPromptConfig) -> str:
    """Build a system prompt identical to production buildSystemMessage().

    This is a direct port of the JS function. The output must be
    character-for-character identical for the same inputs.

    Args:
        rc: ChampollionPromptConfig extracted from a champollion config + card.

    Returns:
        System prompt string, ready for LLM API call.
    """
    # Gender guidance: use language-specific guidance from card when available,
    # otherwise fall back to a generic rule.
    if rc.gender_guidance:
        gender_rule = f"- Gender: {rc.gender_guidance}"
    else:
        gender_rule = (
            f"- When gender is ambiguous, prefer gender-neutral forms "
            f"or the most inclusive option available in {rc.target_lang_name}."
        )

    # Optional prompt context block
    if rc.prompt_context:
        context_block = f"\nContext: {rc.prompt_context}\n"
    else:
        context_block = ""

    return (
        f"You are translating UI strings for a web/mobile application "
        f"from English to {rc.target_lang_name}.\n"
        f"{context_block}\n"
        f"Register/tone: {rc.register}\n"
        f"\n"
        f"Rules:\n"
        f"- Translate ONLY the values, keep the keys exactly as-is.\n"
        f"- Proper nouns (product names, company names, place names) "
        f"should NOT be translated.\n"
        f"- Technical terms and role descriptions that are industry-standard "
        f"should stay in English.\n"
        f"{gender_rule}\n"
        f"- Respect the UI element type: button labels should be concise, "
        f"descriptions can be natural-length, error messages should be clear "
        f"and direct.\n"
        f"- Return ONLY valid JSON, no markdown fences, no explanation."
    )
