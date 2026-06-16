"""
CRK Metric Plugins — LYSS evaluation standards for Plains Cree.

These are harness-level evaluation metrics, loaded via the language
card's evalMetrics declaration. They apply to ALL CRK translations
regardless of which method produced them.

Each plugin satisfies the MetricPlugin protocol:
    - name: str
    - compute(entry: dict) -> dict
    - aggregate(entry_results: list[dict]) -> dict

ARCHITECTURAL NOTE:
    These metrics were extracted from crk-translate/method_plugin/metrics.py
    to establish proper separation between evaluation standards (referee)
    and translation methods (contestants). The language card (crk.json)
    declares these metrics via evalMetrics, and plugin_discovery.py loads
    them generically — no hardcoded language knowledge in the harness.

WHAT'S NOT HERE:
    CrkFSTMetric is gone — it's superseded by the harness's generic
    GiellaLTFSTMetric (plugins/giellalt_fst.py), which does the same
    word-level FST validity checking for ANY language, not just CRK.
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CrkLinterMetric — Wraps linter.py's lint_translation()
# ---------------------------------------------------------------------------

class CrkLinterMetric:
    """Deterministic variant-class linter for Plains Cree translations.

    Detects known acceptable variant classes (word order, orthographic,
    optional particle, lemma synonym, progressive ambiguity, inclusive/
    exclusive) between a candidate and reference translation.

    Produces:
        Per-entry:
            - equivalent_match (bool): True if all differences are acceptable
            - variant_classes (list[str]): Detected variant class names
            - lint_verdict (str): EXACT | EQUIVALENT | MISS

        Aggregate:
            - equivalent_match_rate (float): Fraction of entries that are
              exact OR equivalent matches
            - variant_class_counts (dict): Count of each variant class
    """

    name = "crk_linter"

    def compute(self, entry: dict) -> dict:
        """Run the linter on a single entry."""
        from mt_eval_harness.eval_standards.crk.linter import lint_translation

        predicted = entry.get("predicted", "").strip()
        expected = entry.get("expected", "").strip()

        if not predicted or not expected:
            return {
                "equivalent_match": False,
                "variant_classes": [],
                "lint_verdict": "NO_OUTPUT" if not predicted else "MISS",
            }

        result = lint_translation(expected, predicted)

        return {
            "equivalent_match": result.equivalent_match,
            "variant_classes": result.variant_names,
            "lint_verdict": result.verdict,
        }

    # Display metadata for the run-card renderer. The generic renderer
    # (run_card.py) shows any equivalence-linter plugin from these fields;
    # Cree-specific labels live HERE, in the LYSS lane, never in the
    # language-agnostic renderer (founder rule: Cree is not special-cased
    # outside crk-translate and its custom linters).
    DISPLAY_NAME = "LYSS Equivalence Linter"
    VARIANT_LABELS = {
        "LONG_VOWEL_MACRON": "Long vowel diacritics (ā↔â)",
        "ORTHOGRAPHIC": "Preverb spacing (ê wâp↔ê-wâp)",
        "WORD_ORDER": "Word order permutation",
        "OPTIONAL_PARTICLE": "Optional particle (ispîhk…)",
        "LEMMA_SYNONYM": "Lemma synonym",
        "INCLUSIVE_EXCLUSIVE": "Inclusive/exclusive 'we'",
        "PROGRESSIVE_AMBIGUITY": "Progressive aspect (ati-)",
    }

    def aggregate(self, entry_results: list[dict]) -> dict:
        """Compute corpus-level linter aggregates."""
        total = len(entry_results)
        base = {
            "is_equivalence_linter": True,
            "display_name": self.DISPLAY_NAME,
            "variant_labels": self.VARIANT_LABELS,
        }
        if total == 0:
            return {**base, "equivalent_match_rate": 0.0, "variant_class_counts": {}}

        equiv_count = sum(1 for r in entry_results if r.get("equivalent_match"))

        # Count variant class occurrences across all entries
        class_counts: dict[str, int] = {}
        for r in entry_results:
            for vc in r.get("variant_classes", []):
                class_counts[vc] = class_counts.get(vc, 0) + 1

        return {
            **base,
            "equivalent_match_rate": equiv_count / total,
            "variant_class_counts": class_counts,
        }


# ---------------------------------------------------------------------------
# CrkSemanticMetric — Wraps semantic_validator.py's validate_entry()
# ---------------------------------------------------------------------------

class CrkSemanticMetric:
    """Deterministic semantic validator using FST lemma extraction +
    dictionary glosses + spaCy content-word overlap.

    Produces:
        Per-entry:
            - semantic_verdict (str): EXACT_MATCH | VALID | GRAMMAR_ISSUES |
              PARTIAL | INCOMPLETE | WRONG | NO_OUTPUT

        Aggregate:
            - semantic_verdict_counts (dict): Count of each verdict category
    """

    name = "crk_semantic"

    def __init__(self):
        self._generator: Optional[object] = None
        self._gloss_map: Optional[dict] = None
        self._nlp = None

    def _init_resources(self):
        """Lazy-init all heavy resources."""
        if self._generator is None:
            from mt_eval_harness.eval_standards.crk.fst_adapter import FSTAnalyzer
            self._generator = FSTAnalyzer(lang_code="crk")

        if self._gloss_map is None:
            from mt_eval_harness.eval_standards.crk.semantic_validator import load_gloss_map
            self._gloss_map = load_gloss_map()

        if self._nlp is None:
            from mt_eval_harness.eval_standards.crk.semantic_validator import load_nlp
            self._nlp = load_nlp()

    def compute(self, entry: dict) -> dict:
        """Run semantic validation on a single entry."""
        from mt_eval_harness.eval_standards.crk.semantic_validator import validate_entry

        self._init_resources()

        try:
            validation = validate_entry(
                entry, self._generator, self._gloss_map, self._nlp
            )
            return {"semantic_verdict": validation.verdict}
        except Exception as e:
            logger.warning("Semantic validation failed: %s", e)
            return {"semantic_verdict": "ERROR", "semantic_error": str(e)}

    def aggregate(self, entry_results: list[dict]) -> dict:
        """Count verdicts across all entries."""
        counts: dict[str, int] = {}
        for r in entry_results:
            verdict = r.get("semantic_verdict", "UNKNOWN")
            counts[verdict] = counts.get(verdict, 0) + 1
        return {"semantic_verdict_counts": counts}
