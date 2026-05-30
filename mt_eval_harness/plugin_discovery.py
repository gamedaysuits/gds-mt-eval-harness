"""
Plugin auto-discovery — Automatically register metric plugins based on target language.

WHY THIS MODULE EXISTS:
    The harness ships with generic metrics (chrF++, BLEU, exact match). But for
    specific languages, we have domain-specific validators — most importantly the
    GiellaLT FST morphological checker, which verifies whether each output word
    is a valid form in the target language.

    Rather than forcing users to manually specify plugins on every run, this
    module auto-detects which plugins are available based on the target language.

FST QUALITY GATE:
    For languages that have a GiellaLT FST listed in the FST registry, the FST
    is REQUIRED for evaluations. If it's not installed, the harness will:
    1. Prompt the user to download and install it
    2. If user consents → auto-install and proceed
    3. If user declines → ABORT the eval (unless --skip-fst is set)

    This ensures that polysynthetic and low-resource language evals always
    include morphological validation — the most important quality signal
    for these languages.

DESIGN DECISIONS:
    - The FST gate applies only to languages in GIELLALT_FST_REGISTRY.
      Languages without known FSTs proceed normally without any gate.
    - CRK-specific plugins (linter, semantic) remain as additional
      language-specific enrichments on top of the generic FST plugin.
    - The --skip-fst flag exists for CI/automation where interactive
      prompts aren't possible, but it logs a clear warning.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

# Maps common language names/patterns to ISO 639-3 codes
# Used to resolve the target_lang field (which can be a human-readable name
# like "Plains Cree (nêhiyawêwin, SRO)") to a code we can look up.
_LANG_NAME_TO_CODE = {
    "cree": "crk",
    "plains cree": "crk",
    "nêhiyawêwin": "crk",
    "northern sámi": "sme",
    "davvisámegiella": "sme",
    "southern sámi": "sma",
    "lule sámi": "smj",
    "inari sámi": "smn",
    "skolt sámi": "sms",
    "finnish": "fin",
    "inuktitut": "iku",
    "norwegian bokmål": "nob",
}


def _detect_lang_code(config: dict) -> str | None:
    """Extract the ISO 639-3 language code from the run config.

    Checks target_lang, target_language, and language_pair fields.
    Returns None if the language can't be identified.
    """
    target = (
        config.get("target_lang", "")
        or config.get("target_language", "")
        or ""
    ).strip()

    if not target:
        # Try language_pair field (e.g. "en>crk" or "en-crk")
        pair = config.get("language_pair", "")
        if pair:
            # Extract target from pair — it's the second part
            for sep in [">", "-", "_"]:
                if sep in pair:
                    target = pair.split(sep)[-1].strip()
                    break

    if not target:
        return None

    target_lower = target.lower()

    # Direct 3-letter code match (e.g. "crk")
    if len(target) == 3 and target.isalpha():
        return target.lower()

    # Name-based lookup
    for pattern, code in _LANG_NAME_TO_CODE.items():
        if pattern in target_lower:
            return code

    return None


def _detect_lang_name(config: dict) -> str:
    """Extract a human-readable language name from the config."""
    return (
        config.get("target_lang", "")
        or config.get("target_language", "")
        or "Unknown"
    )


# ---------------------------------------------------------------------------
# CRK-specific plugin loading (linter, semantic — language-specific by nature)
# ---------------------------------------------------------------------------

def _try_load_crk_linter() -> object | None:
    """Attempt to load CrkLinterMetric. Returns the plugin instance or None."""
    try:
        from eval.harness_plugins.metrics import CrkLinterMetric
        return CrkLinterMetric()
    except ImportError:
        logger.debug("CrkLinterMetric not importable")
        return None
    except Exception as e:
        logger.debug("CrkLinterMetric failed to initialize: %s", e)
        return None


def _try_load_crk_semantic() -> object | None:
    """Attempt to load CrkSemanticMetric. Returns the plugin instance or None."""
    try:
        from eval.harness_plugins.metrics import CrkSemanticMetric
        return CrkSemanticMetric()
    except ImportError:
        logger.debug("CrkSemanticMetric not importable")
        return None
    except Exception as e:
        logger.debug("CrkSemanticMetric failed to initialize: %s", e)
        return None


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def discover_metric_plugins(
    config: dict,
    skip_fst: bool = False,
) -> list:
    """Auto-discover metric plugins appropriate for the target language.

    This is the main entry point for plugin auto-discovery. It:
        1. Detects the target language from the config dict
        2. Checks if the language has a known GiellaLT FST
        3. Enforces the FST quality gate (prompt → install → or abort)
        4. Loads any additional language-specific plugins

    Args:
        config: Dict containing at least 'target_lang' or 'target_language'.
                Can be a RunConfig.__dict__, a run_log['config'], or similar.
        skip_fst: If True, skip the FST gate (for --skip-fst flag).

    Returns:
        List of MetricPlugin instances (may be empty).

    Raises:
        SystemExit: If the FST is required but user declines to install
                    and skip_fst is False.
    """
    plugins = []

    lang_code = _detect_lang_code(config)
    lang_name = _detect_lang_name(config)

    if lang_code is None:
        return plugins

    # --- FST quality gate ---
    from mt_eval_harness.plugins.fst_installer import (
        GIELLALT_FST_REGISTRY,
        ensure_fst_available,
    )

    if lang_code in GIELLALT_FST_REGISTRY:
        fst_dir = ensure_fst_available(
            lang_code, lang_name, skip_fst=skip_fst
        )

        if fst_dir is not None:
            # FST is installed — create the metric plugin
            from mt_eval_harness.plugins.giellalt_fst import GiellaLTFSTMetric
            fst_plugin = GiellaLTFSTMetric(lang_code=lang_code, fst_dir=fst_dir)
            plugins.append(fst_plugin)
            print(f"  FST metric: registered (GiellaLTFSTMetric for {lang_code})")
        elif not skip_fst:
            # FST is required but not available — abort
            entry = GIELLALT_FST_REGISTRY[lang_code]
            print()
            print(f"  ✗ Evaluation aborted.")
            print(f"    {entry['name']} ({lang_code}) requires FST validation.")
            print(f"    Use --skip-fst to run without morphological checking.")
            raise SystemExit(1)

    # --- CRK-specific plugins (in addition to the generic FST) ---
    if lang_code == "crk":
        linter = _try_load_crk_linter()
        if linter:
            plugins.append(linter)
            print("  Linter: loaded (CrkLinterMetric — variant-class detection)")
        else:
            print("  ℹ CRK Linter: not available (install crk-translate package)")

        semantic = _try_load_crk_semantic()
        if semantic:
            plugins.append(semantic)
            print("  Semantic: loaded (CrkSemanticMetric — semantic validation)")

    if plugins:
        print(f"  Auto-discovered {len(plugins)} metric plugin(s) for {lang_code}")

    return plugins
