"""
Language Card Index — Single source of truth for all language metadata.

Python equivalent of cli/lib/registers.js. Loads language card JSON files
from cli/shared/language-cards/ and builds lookup indexes for:
    - code → card (primary ISO 639-3 codes)
    - alias → code (ISO 639-1 codes, legacy codes, regional variants)
    - name → code (human-readable language names, case-insensitive)

ALL language resolution in the Python harness goes through this module.
No hardcoded language maps anywhere else. If you find one, delete it
and route through here instead.

Architecture mirrors registers.js:
    1. _ensure_loaded() scans all card JSON files once on first access
    2. Builds _cards, _aliases, _name_index dictionaries
    3. resolve_code() follows the same chain: direct → alias → base locale
    4. resolve_name() provides fuzzy name-to-code lookup
    5. get_card() returns full card with 'extends' inheritance resolved

Performance:
    Loading 7,928 cards takes ~200ms on a modern machine. This happens
    once per process. All subsequent lookups are O(1) dict access.

ADDING A NEW LANGUAGE:
    Just create the language card JSON file. This module will pick it up
    automatically — no code changes needed.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Internal state — populated lazily by _ensure_loaded()
# ---------------------------------------------------------------------------

# Primary card registry: ISO 639-3 code → raw card dict
_cards: dict[str, dict[str, Any]] = {}

# Parent/genus/family cards: code → raw card dict
# e.g., "genus-cree", "family-algonquian"
_parent_cards: dict[str, dict[str, Any]] = {}

# Alias → primary code. Built from each card's 'aliases' field.
# e.g., "fr" → "fra", "no" → "nob", "iw" → "heb"
_aliases: dict[str, str] = {}

# Lowercase language name → primary code. Built from each card's 'name' field.
# e.g., "french" → "fra", "plains cree" → "crk"
_name_index: dict[str, str] = {}

# Resolved (inheritance-merged) card cache
_resolved_cache: dict[str, dict[str, Any]] = {}

# Load guard — ensures we only scan the filesystem once
_loaded: bool = False

# Discovered cards directory path (cached after first find)
_cards_dir: Path | None = None


# ---------------------------------------------------------------------------
# Cards directory discovery
# ---------------------------------------------------------------------------

def _find_cards_dir() -> Path | None:
    """Auto-detect the language cards directory.

    Search strategy:
        1. Walk up from this file's location to find the monorepo root,
           then check cli/shared/language-cards/
        2. Walk up from CWD (handles running from any subdirectory)
        3. npm install fallback: node_modules/champollion/shared/language-cards/

    Returns None if not found — caller should log a warning.
    """
    # Strategy 1: Relative to this file (most reliable in monorepo)
    # This file: <monorepo>/arena/mt_eval_harness/language_cards.py
    # Cards:     <monorepo>/cli/shared/language-cards/
    this_dir = Path(__file__).resolve().parent          # mt_eval_harness/
    arena_dir = this_dir.parent                         # arena/
    monorepo_root = arena_dir.parent                    # Champollion/

    candidate = monorepo_root / "cli" / "shared" / "language-cards"
    if candidate.is_dir():
        return candidate

    # Strategy 2: Walk up from CWD
    cwd = Path.cwd()
    check = cwd
    for _ in range(10):
        for sub in [
            check / "cli" / "shared" / "language-cards",
            check / "shared" / "language-cards",
        ]:
            if sub.is_dir():
                return sub
        check = check.parent

    # Strategy 3: npm install fallback
    npm_path = cwd / "node_modules" / "champollion" / "shared" / "language-cards"
    if npm_path.is_dir():
        return npm_path

    return None


# ---------------------------------------------------------------------------
# Lazy loading
# ---------------------------------------------------------------------------

def _ensure_loaded() -> None:
    """Load all language card JSON files on first access. Idempotent.

    Scans the cards directory recursively, building three indexes:
        _cards:      code → card (primary ISO 639-3 codes)
        _aliases:    alias → code (from card 'aliases' field + iso639_1)
        _name_index: lowercase name → code (from card 'name' field)

    Parent/genus/family cards go into _parent_cards for inheritance.
    """
    global _loaded, _cards_dir
    if _loaded:
        return

    _cards_dir = _find_cards_dir()
    if _cards_dir is None:
        logger.warning(
            "Language cards directory not found. "
            "Language resolution will return codes as-is. "
            "Expected at: <monorepo>/cli/shared/language-cards/"
        )
        _loaded = True
        return

    card_count = 0
    alias_count = 0

    for p in _cards_dir.rglob("*.json"):
        try:
            card = json.loads(p.read_text(encoding="utf-8"))
            code = card.get("code")
            if not code:
                continue

            # Parent/genus/family cards go into separate registry
            is_parent = (
                "genera" in p.parts
                or code.startswith("family-")
                or code.startswith("genus-")
                or code.startswith("macrolanguage-")
            )

            if is_parent:
                _parent_cards[code] = card
            else:
                _cards[code] = card
                card_count += 1

                # Build alias index from card's 'aliases' field
                for alias in card.get("aliases", []):
                    _aliases[alias] = code
                    alias_count += 1

                # Also index iso639_1 as an alias if present and not
                # already the primary code
                iso1 = card.get("iso639_1")
                if iso1 and iso1 != code and iso1 not in _aliases:
                    _aliases[iso1] = code
                    alias_count += 1

                # Build name index (case-insensitive)
                name = card.get("name", "")
                if name:
                    _name_index[name.lower()] = code

        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load language card %s: %s", p, e)

    _loaded = True
    logger.debug(
        "Language card index: %d cards, %d aliases, %d parent cards from %s",
        card_count, alias_count, len(_parent_cards), _cards_dir,
    )


# ---------------------------------------------------------------------------
# Public API — Code Resolution
# ---------------------------------------------------------------------------

def resolve_code(code: str) -> str:
    """Resolve any language code/alias to its canonical ISO 639-3 code.

    Resolution chain (mirrors JS resolveCode() in registers.js):
        1. Direct match: 'fra' → 'fra' (already canonical)
        2. Alias match:  'fr'  → 'fra' (from card aliases field)
        3. Base locale:  'fr-CA' → 'fr' → 'fra' (strip region subtag)
        4. No match:     returns the input unchanged

    Args:
        code: Language code, alias, or regional variant to resolve.

    Returns:
        Canonical ISO 639-3 code, or the input code if no resolution found.
    """
    _ensure_loaded()

    # Direct match — already canonical
    if code in _cards:
        return code

    # Alias match
    if code in _aliases:
        return _aliases[code]

    # Base locale fallback: "fr-CA" → try "fra-CA" (resolved base + region),
    # then "fr" → "fra" (base only)
    if "-" in code:
        parts = code.split("-", 1)
        base = parts[0]
        region = parts[1]

        # Try resolving the base and recombining: "fr-CA" → "fra-CA"
        resolved_base = None
        if base in _cards:
            resolved_base = base
        elif base in _aliases:
            resolved_base = _aliases[base]

        if resolved_base:
            regional = f"{resolved_base}-{region}"
            if regional in _cards:
                return regional
            # Regional variant not found — fall back to base language
            return resolved_base

    # No resolution found — return as-is
    return code


def resolve_name(name: str) -> str | None:
    """Resolve a human-readable language name to its ISO 639-3 code.

    Case-insensitive lookup against all loaded language card names.
    Also handles parenthetical suffixes: "Plains Cree (nêhiyawêwin, SRO)"
    will try "plains cree (nêhiyawêwin, sro)" first, then "plains cree".

    Args:
        name: Human-readable language name.

    Returns:
        ISO 639-3 code, or None if no match found.
    """
    _ensure_loaded()

    lower = name.strip().lower()

    # Direct name match
    if lower in _name_index:
        return _name_index[lower]

    # Try stripping parenthetical suffix:
    # "Plains Cree (nêhiyawêwin, SRO)" → "plains cree"
    if "(" in lower:
        base_name = lower.split("(")[0].strip()
        if base_name in _name_index:
            return _name_index[base_name]

    return None


# ---------------------------------------------------------------------------
# Public API — Card Access
# ---------------------------------------------------------------------------

def _resolve_card_with_inheritance(code: str) -> dict[str, Any] | None:
    """Resolve a card with its full extends inheritance chain.

    Recursively merges parent cards (genus → family → card) following
    the 'extends' field. Caches resolved cards for performance.
    """
    if code in _resolved_cache:
        return _resolved_cache[code]

    # Find the raw card (could be in _cards or _parent_cards)
    raw = _cards.get(code) or _parent_cards.get(code)
    if raw is None:
        return None

    resolved = dict(raw)

    # Resolve inheritance
    parent_code = raw.get("extends")
    if parent_code:
        parent_card = _resolve_card_with_inheritance(parent_code)
        if parent_card:
            resolved = _deep_merge(parent_card, resolved)
        else:
            logger.warning(
                "Language card '%s' extends unknown card '%s'.",
                code, parent_code,
            )

    _resolved_cache[code] = resolved
    return resolved


def _deep_merge(parent: dict, child: dict) -> dict:
    """Deep merge two card dicts (child overrides parent).

    Semantics match the JS _deepMerge() in registers.js:
        - null/None in child → inherit from parent
        - objects merge recursively
        - arrays in child replace parent arrays entirely
        - Identity fields (code, extends, aliases, iso639_1, iso639_3)
          always use child's value
    """
    _IDENTITY_FIELDS = {"code", "extends", "_migration", "aliases", "iso639_1", "iso639_3"}
    merged = dict(parent)

    for key, value in child.items():
        # Identity fields: always use child's value
        if key in _IDENTITY_FIELDS:
            merged[key] = value
            continue

        # None in child means "inherit from parent"
        if value is None:
            continue

        # Recursive merge for nested dicts (not lists)
        if (
            isinstance(value, dict)
            and key in merged
            and isinstance(merged[key], dict)
        ):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value

    return merged


def get_card(code: str) -> dict[str, Any] | None:
    """Get the full language card for a code, with inheritance resolved.

    Follows aliases and resolves the 'extends' chain. Returns None if
    no card exists for this language.

    Args:
        code: Language code, alias, or regional variant.

    Returns:
        Complete language card dict with parent fields merged, or None.
    """
    _ensure_loaded()
    resolved = resolve_code(code)
    return _resolve_card_with_inheritance(resolved)


def get_name(code: str) -> str | None:
    """Get the human-readable display name for a language code.

    Args:
        code: Language code, alias, or regional variant.

    Returns:
        Language name (e.g., "French", "Plains Cree"), or None.
    """
    card = get_card(code)
    return card.get("name") if card else None


def get_all_codes() -> list[str]:
    """Get all primary language codes (not aliases).

    Returns:
        List of ISO 639-3 codes for all loaded cards.
    """
    _ensure_loaded()
    return list(_cards.keys())


def get_cards_dir() -> Path | None:
    """Get the discovered language cards directory path.

    Returns None if cards haven't been loaded or directory wasn't found.
    """
    _ensure_loaded()
    return _cards_dir


# ---------------------------------------------------------------------------
# Public API — Metric Model Support
#
# These functions query the 'metricModelSupport' field on language cards.
# They replace the hardcoded _XLMR_HIGH_RESOURCE and _AFRICOMET_LANGUAGES
# sets that previously lived in metrics_comet.py. The SSOT is now the
# language card JSON files, enriched by enrich-metric-model-support.mjs.
# ---------------------------------------------------------------------------

def is_xlmr_high_resource(code: str) -> bool:
    """Check if a language has high XLM-R representation.

    Languages with high XLM-R representation produce more reliable COMET
    scores. Languages NOT in this set may have noisier COMET scores due
    to weaker XLM-R embeddings.

    Source: XLM-R paper (Conneau et al., 2020) — top-100 languages
    by CommonCrawl training data volume.

    Args:
        code: Language code (any format — resolved via resolve_code).

    Returns:
        True if the language is in XLM-R's top tier.
    """
    card = get_card(code)
    if card is None:
        return False

    mms = card.get("metricModelSupport")
    if mms is None:
        return False

    xlmr = mms.get("xlmr")
    return isinstance(xlmr, dict) and xlmr.get("tier") == "high"


def has_africomet(code: str) -> bool:
    """Check if a language has AfriCOMET training data.

    Languages with AfriCOMET support get better evaluation scores
    from masakhane/africomet-mtl than from default wmt22-comet-da,
    because AfriCOMET was trained with human judgments for these
    specific languages.

    Source: Wan et al. (2022) + Masakhane evaluation datasets.

    Args:
        code: Language code (any format — resolved via resolve_code).

    Returns:
        True if AfriCOMET was trained with human judgment data
        for this language.
    """
    card = get_card(code)
    if card is None:
        return False

    mms = card.get("metricModelSupport")
    if mms is None:
        return False

    africomet = mms.get("africomet")
    return isinstance(africomet, dict) and africomet.get("supported") is True


def get_metric_model_for(code: str) -> str | None:
    """Get the recommended COMET model for a language, if any.

    Checks the language card's metricModelSupport field for
    language-specific model recommendations.

    Args:
        code: Language code (any format — resolved via resolve_code).

    Returns:
        Model identifier string (e.g., "masakhane/africomet-mtl")
        if a specialized model is recommended, or None to use the
        default COMET model.
    """
    card = get_card(code)
    if card is None:
        return None

    mms = card.get("metricModelSupport")
    if mms is None:
        return None

    # AfriCOMET takes priority (it's a specialized model)
    africomet = mms.get("africomet")
    if isinstance(africomet, dict) and africomet.get("supported"):
        return africomet.get("model")

    # Future: check for IndicCOMET, etc.

    return None


# ---------------------------------------------------------------------------
# Public API — FST Install Info
#
# These functions query the 'resources.fsts[0].install' field on language
# cards.  They replace the hardcoded GIELLALT_FST_REGISTRY that previously
# lived in plugins/fst_installer.py.  The SSOT is now the language card
# JSON files, enriched in Phase 4 of the SSOT migration.
# ---------------------------------------------------------------------------

def get_fst_install_info(code: str) -> dict[str, Any] | None:
    """Get FST install metadata for a language, if any.

    Reads the first entry in ``resources.fsts[]`` and returns its
    ``install`` sub-object.  Returns None if the card doesn't exist,
    has no ``resources.fsts``, or has no ``install`` block.

    The returned dict has the shape::

        {
            "repo":          "giellalt/lang-crk",
            "releaseTag":    "fst-v2021.7.8",       # optional
            "assetPattern":  "plains-cree-fsts-",    # optional
            "bundlePattern": "no.divvun...",          # optional (divvun-macos-pkg)
            "format":        "legacy-zip",
            "maturity":      "production"             # optional
        }

    Args:
        code: Language code (any format — resolved via resolve_code).

    Returns:
        Install metadata dict, or None if no FST install info exists.
    """
    card = get_card(code)
    if card is None:
        return None

    resources = card.get("resources")
    if not resources or not isinstance(resources, dict):
        return None

    fsts = resources.get("fsts")
    if not fsts or not isinstance(fsts, list) or len(fsts) == 0:
        return None

    install = fsts[0].get("install")
    if not install or not isinstance(install, dict):
        return None

    return install


# ---------------------------------------------------------------------------
# Public API — Eval Pack Requirements
#
# Eval packs declare the Python dependencies, FST requirements, and
# post-install steps needed to evaluate a specific language. The SSOT
# is the `evalPack` field on each language card. The harness reads this
# generically — no language-specific code needed.
# ---------------------------------------------------------------------------

def get_eval_pack(code: str) -> dict[str, Any] | None:
    """Get eval pack requirements for a language, if any.

    Reads the ``evalPack`` field from the language card. Returns None if
    the card doesn't exist or has no eval pack defined.

    The returned dict has the shape::

        {
            "pythonDeps": {
                "pyhfst": "pyhfst>=1.4",
                "requests": "requests>=2.28"
            },
            "postInstall": [
                {"command": "spacy download en_core_web_md", "label": "..."}
            ],
            "requiresFst": true,
            "description": "Human-readable description"
        }

    Args:
        code: Language code (any format — resolved via resolve_code).

    Returns:
        Eval pack dict, or None if no eval pack is defined.
    """
    card = get_card(code)
    if card is None:
        return None
    return card.get("evalPack")


def get_eval_metrics(code: str) -> dict[str, Any] | None:
    """Get language-specific evaluation metrics declared on the card.

    Reads the ``evalMetrics`` field from the language card. Returns None if
    the card doesn't exist or has no eval metrics defined.

    The returned dict maps metric short names to their declarations::

        {
            "lyss-eq": {
                "module": "eval_standards.crk.metrics",
                "class": "CrkLinterMetric",
                "description": "LYSS deterministic variant-class equivalence linter"
            },
            "lyss-sem": {
                "module": "eval_standards.crk.metrics",
                "class": "CrkSemanticMetric",
                "dependencies": ["spacy>=3.7"],
                "spacy_models": ["en_core_web_md"],
                "description": "LYSS FST-based semantic validator"
            }
        }

    The harness uses this to load evaluation metrics from the
    eval_standards package via importlib — no hardcoded language
    knowledge needed.

    Args:
        code: Language code (any format — resolved via resolve_code).

    Returns:
        Dict of metric declarations, or None if no eval metrics defined.
    """
    card = get_card(code)
    if card is None:
        return None
    return card.get("evalMetrics")
