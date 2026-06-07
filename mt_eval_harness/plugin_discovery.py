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

BEHAVIORAL PLUGINS (language-agnostic):
    Three behavioral metric plugins are loaded for ALL language pairs:
    - CodeSwitchingPlugin: detects source-language word leakage (e.g. English
      words in Cree output). Auto-detects target script.
    - HallucinationPlugin: detects fabricated content via length ratio,
      repetition, entity preservation, and echo detection heuristics.
    - TerminologyPlugin: measures adherence to prescribed vocabulary when a
      glossary is provided in config. Returns null metrics without a glossary
      (harmlessly excluded from composite via re-normalization).

    Scoring weights reference these metrics (code_switching_rate, hallucination_rate,
    terminology_adherence), so they must be loaded for the composite to include them.

DESIGN DECISIONS:
    - The FST gate applies only to languages in GIELLALT_FST_REGISTRY.
      Languages without known FSTs proceed normally without any gate.
    - Language-specific LYSS plugins (linters, semantic validators) are
      loaded when a matching language is detected. Currently supported:
        * CRK (Plains Cree): CrkLinterMetric (LYSS-eq), CrkSemanticMetric (LYSS-sem)
      These plugins live in crk-translate/eval/harness_plugins/ and are
      imported conditionally to avoid hard dependencies.
    - Behavioral plugins load unconditionally — they're stdlib-only,
      language-agnostic, and zero-config.
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
    # Polysynthetic / morphologically-complex
    "cree": "crk",
    "plains cree": "crk",
    "nêhiyawêwin": "crk",
    "quechua": "que",
    "cusco quechua": "que",
    # Sámi family
    "northern sámi": "sme",
    "davvisámegiella": "sme",
    "southern sámi": "sma",
    "lule sámi": "smj",
    "inari sámi": "smn",
    "skolt sámi": "sms",
    # Other FST-supported
    "finnish": "fin",
    "inuktitut": "iku",
    "norwegian bokmål": "nob",
    "basque": "eus",
    "amharic": "amh",
    "welsh": "cym",
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
# Behavioral plugins (language-agnostic — apply to all language pairs)
# ---------------------------------------------------------------------------

def _load_code_switching() -> object:
    """Load CodeSwitchingPlugin.

    This plugin SHIPS WITH the harness — it is not an optional external
    dependency. If it fails to import, something is broken and we must
    crash loudly rather than silently omitting it from scoring.
    """
    from mt_eval_harness.plugins.code_switching import CodeSwitchingPlugin
    return CodeSwitchingPlugin()


def _load_hallucination() -> object:
    """Load HallucinationPlugin.

    This plugin SHIPS WITH the harness — it is not an optional external
    dependency. If it fails to import, something is broken and we must
    crash loudly.
    """
    from mt_eval_harness.plugins.hallucination import HallucinationPlugin
    return HallucinationPlugin()


def _load_terminology(config: dict) -> object:
    """Load TerminologyPlugin with glossary from config.

    This plugin SHIPS WITH the harness — it is not an optional external
    dependency. If it fails to import, something is broken and we must
    crash loudly.

    If no glossary is provided in the config, the plugin still loads but
    returns None for all terminology metrics — scoring.py treats None as
    "metric unavailable" and excludes it from composite re-normalization.
    This means loading it without a glossary is harmless.
    """
    from mt_eval_harness.plugins.terminology import TerminologyPlugin
    glossary = config.get("glossary")
    return TerminologyPlugin(glossary=glossary)


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
        logger.warning(
            "Could not detect target language from config keys "
            "'target_lang', 'target_language', or 'language_pair'. "
            "No language-specific plugins will be loaded. "
            "Config keys present: %s",
            list(config.keys()),
        )
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

    # --- Language-specific LYSS plugins ---
    # These provide linguistically-informed metrics that go beyond surface
    # comparison. They are loaded conditionally based on target language.
    # Each plugin lazy-initializes its heavy resources on first use.
    #
    # LYSS-eq (CrkLinterMetric): deterministic variant-class equivalence
    # LYSS-sem (CrkSemanticMetric): FST lemma + dictionary + spaCy overlap

    if lang_code == "crk":
        # The CRK LYSS plugins live in crk-translate/eval/harness_plugins/,
        # which is a separate subtree from arena/mt_eval_harness/. We need
        # to add crk-translate/ to sys.path so `from eval.harness_plugins`
        # resolves. This follows the same pattern as method_loader.py
        # (lines 119-131) which adds plugin directories to sys.path.
        import sys
        from pathlib import Path

        # Detect monorepo root: plugin_discovery.py lives at
        # <monorepo>/arena/mt_eval_harness/plugin_discovery.py
        # so monorepo root is 2 levels up from this file's directory.
        _this_dir = Path(__file__).resolve().parent        # mt_eval_harness/
        _arena_dir = _this_dir.parent                      # arena/
        _monorepo_root = _arena_dir.parent                 # Champollion/
        _crk_dir = _monorepo_root / "crk-translate"

        _crk_path_added = False
        if _crk_dir.is_dir():
            crk_dir_str = str(_crk_dir)
            if crk_dir_str not in sys.path:
                sys.path.insert(0, crk_dir_str)
                _crk_path_added = True
                logger.debug("Added %s to sys.path for CRK plugin imports", crk_dir_str)
        else:
            logger.warning(
                "crk-translate directory not found at %s. "
                "CRK-specific LYSS plugins will not be loaded.", _crk_dir
            )

        try:
            from eval.harness_plugins.metrics import CrkLinterMetric
            plugins.append(CrkLinterMetric())
            print("  LYSS-eq: loaded (CrkLinterMetric — variant-class equivalence)")
        except ImportError as e:
            logger.warning(
                "CrkLinterMetric not available (import error: %s). "
                "equivalent_match_rate will be null in composite.", e
            )

        try:
            from eval.harness_plugins.metrics import CrkSemanticMetric

            # Probe whether LYSS-sem's runtime dependencies are available.
            # CrkSemanticMetric lazy-loads spaCy + en_core_web_md + CrkGenerator
            # on first compute(). If spaCy isn't installed, every entry gets
            # verdict=ERROR and semantic_score is null. Better to tell the
            # user upfront and offer to install, like the FST prompt does.
            _sem_ready = True
            try:
                import spacy
                spacy.load("en_core_web_md")
            except ImportError:
                _sem_ready = False
                _missing = "spaCy"
            except OSError:
                # spaCy installed but model not downloaded
                _sem_ready = False
                _missing = "spaCy English model (en_core_web_md)"

            if _sem_ready:
                plugins.append(CrkSemanticMetric())
                print("  LYSS-sem: loaded (CrkSemanticMetric — semantic validation)")
            else:
                # Prompt for CRK eval pack install (parallels FST prompt)
                print(f"  LYSS-sem: {_missing} not found.")
                _installed = False
                if sys.stdin.isatty():
                    print()
                    print("  ┌─────────────────────────────────────────────────────────────┐")
                    print("  │  CRK Eval Pack — Semantic Validation Dependencies           │")
                    print("  │                                                             │")
                    print("  │  LYSS-sem validates meaning preservation by comparing       │")
                    print("  │  FST lemma glosses via English content-word overlap.         │")
                    print("  │  It requires:                                               │")
                    print("  │    • spaCy (NLP library for English lemmatization)           │")
                    print("  │    • en_core_web_md model (~40 MB download)                 │")
                    print("  │                                                             │")
                    print("  │  Without this, semantic_score will be null in the composite. │")
                    print("  └─────────────────────────────────────────────────────────────┘")
                    print()
                    try:
                        answer = input("  Install CRK eval pack now? [y/N]: ").strip().lower()
                        if answer in ("y", "yes"):
                            import subprocess
                            print("  Installing spaCy...")
                            subprocess.check_call(
                                [sys.executable, "-m", "pip", "install", "spacy>=3.5"],
                                stdout=subprocess.DEVNULL,
                            )
                            print("  Downloading en_core_web_md model...")
                            subprocess.check_call(
                                [sys.executable, "-m", "spacy", "download", "en_core_web_md"],
                                stdout=subprocess.DEVNULL,
                            )
                            # Re-import after install
                            import importlib
                            import spacy
                            importlib.reload(spacy)
                            plugins.append(CrkSemanticMetric())
                            print("  ✓ CRK eval pack installed. LYSS-sem active.")
                            _installed = True
                    except (EOFError, KeyboardInterrupt):
                        print()
                    except Exception as e:
                        print(f"  ✗ CRK eval pack install failed: {e}")

                if not _installed:
                    print("  LYSS-sem: skipped (semantic_score will be null in composite)")
                    logger.warning(
                        "CrkSemanticMetric loaded but %s is missing. "
                        "Run: pip install spacy && python -m spacy download en_core_web_md",
                        _missing,
                    )

        except ImportError as e:
            logger.warning(
                "CrkSemanticMetric not available (import error: %s). "
                "semantic_score will be null in composite.", e
            )

    # --- Behavioral plugins (language-agnostic, always loaded) ---
    # These detect specific failure modes in translation output.
    # They apply to all language pairs — no language-specific tools needed.
    # Scoring weights reference these metrics (code_switching_rate: 0.05–0.10,
    # hallucination_rate: 0.05, terminology_adherence: 0.05), so they must
    # be loaded for the composite to include them.

    cs_plugin = _load_code_switching()
    plugins.append(cs_plugin)
    print("  Code-switching: loaded (CodeSwitchingPlugin — source-language leakage)")

    hall_plugin = _load_hallucination()
    plugins.append(hall_plugin)
    print("  Hallucination: loaded (HallucinationPlugin — fabricated content)")

    term_plugin = _load_terminology(config)
    plugins.append(term_plugin)
    glossary_status = "with glossary" if config.get("glossary") else "no glossary (metric inactive)"
    print(f"  Terminology: loaded (TerminologyPlugin — {glossary_status})")

    if plugins:
        print(f"  Auto-discovered {len(plugins)} metric plugin(s) for {lang_code}")

    return plugins
