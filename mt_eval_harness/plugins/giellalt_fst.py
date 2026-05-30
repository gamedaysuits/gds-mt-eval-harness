"""
GiellaLT FST Metric — Generic morphological validity checker for any
language with a GiellaLT finite-state transducer.

This plugin satisfies the MetricPlugin protocol (name, compute, aggregate)
and works with any language whose .hfstol analyzer is installed locally.

HOW IT WORKS:
    For each predicted translation, the plugin:
    1. Tokenizes the output into words (whitespace split)
    2. Runs each word through the FST analyzer
    3. A word is "valid" if the analyzer returns at least one analysis
    4. Reports per-entry validity rate and corpus-level average

WHY THIS MATTERS:
    For polysynthetic languages like Plains Cree, a single misplaced
    morpheme makes a word form invalid. chrF++ and BLEU can't catch
    this — they measure surface character overlap, not morphological
    well-formedness. The FST is ground truth for word validity.

RELATIONSHIP TO CrkFSTMetric:
    This generic plugin supersedes CrkFSTMetric for evaluation purposes.
    CrkFSTMetric used CrkGenerator (which wraps pyhfst with hardcoded
    CRK paths). This plugin uses pyhfst directly with configurable paths,
    making it language-agnostic while producing identical results for CRK.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class GiellaLTFSTMetric:
    """Generic FST morphological validity checker.

    Wraps pyhfst to analyze words through a GiellaLT FST transducer.
    Works for any language that has .hfstol files installed locally.

    Produces:
        Per-entry:
            - fst_total_words (int): Total words in predicted output
            - fst_valid_words (int): Words recognized by FST
            - fst_validity_rate (float): Valid / total
            - fst_invalid_words (list[str]): Words NOT recognized

        Aggregate:
            - avg_fst_validity (float): Mean validity rate across entries
            - total_words_checked (int): Total words checked
            - total_valid_words (int): Total valid words
            - corpus_validity_rate (float): Overall valid/total ratio
    """

    name = "giellalt_fst_validity"

    def __init__(self, lang_code: str, fst_dir: Path):
        """Initialize with a language code and FST directory.

        Args:
            lang_code: ISO 639-3 code (e.g. "crk", "sme")
            fst_dir: Path to directory containing .hfstol files
        """
        self.lang_code = lang_code
        self._fst_dir = fst_dir
        self._analyzer = None

    def _load_analyzer(self):
        """Lazy-load the FST analyzer transducer."""
        if self._analyzer is not None:
            return self._analyzer

        from mt_eval_harness.plugins.fst_installer import find_analyzer_hfstol

        analyzer_path = find_analyzer_hfstol(self._fst_dir)
        if analyzer_path is None:
            raise FileNotFoundError(
                f"No analyzer .hfstol found in {self._fst_dir}"
            )

        try:
            import pyhfst
        except ImportError:
            raise ImportError(
                "pyhfst is required for FST validation. "
                "Install with: pip install pyhfst"
            )

        input_stream = pyhfst.HfstInputStream(str(analyzer_path))
        self._analyzer = input_stream.read()
        logger.info("Loaded FST analyzer: %s", analyzer_path.name)
        return self._analyzer

    def _analyze_word(self, word: str) -> bool:
        """Check if a word is recognized by the FST analyzer.

        Returns True if the FST returns at least one analysis.
        """
        analyzer = self._load_analyzer()
        try:
            results = analyzer.lookup(word)
            return len(results) > 0
        except Exception:
            return False

    def compute(self, entry: dict) -> dict:
        """Check FST validity for each word in the prediction.

        Follows the MetricPlugin protocol:
            entry must have a "predicted" key with the translation string.
        """
        predicted = entry.get("predicted", "").strip()

        if not predicted:
            return {
                "fst_total_words": 0,
                "fst_valid_words": 0,
                "fst_validity_rate": 0.0,
                "fst_invalid_words": [],
            }

        words = predicted.split()
        total = len(words)
        valid = 0
        invalid_words = []

        for word in words:
            # Strip punctuation from word edges before analysis.
            # FSTs expect clean word forms without trailing periods, commas, etc.
            clean = word.strip(".,;:!?\"'()[]{}—–-")
            if not clean:
                # Pure punctuation — skip (don't count as invalid)
                total -= 1
                continue

            if self._analyze_word(clean):
                valid += 1
            else:
                invalid_words.append(clean)

        return {
            "fst_total_words": total,
            "fst_valid_words": valid,
            "fst_validity_rate": valid / max(total, 1),
            "fst_invalid_words": invalid_words,
        }

    def aggregate(self, entry_results: list[dict]) -> dict:
        """Compute corpus-level FST validity statistics.

        Reports both micro-average (corpus-wide word ratio) and
        macro-average (mean of per-entry rates).
        """
        if not entry_results:
            return {
                "avg_fst_validity": 0.0,
                "total_words_checked": 0,
                "total_valid_words": 0,
                "corpus_validity_rate": 0.0,
            }

        # Macro-average: mean of per-entry validity rates
        rates = [r["fst_validity_rate"] for r in entry_results]
        avg_validity = sum(rates) / len(rates)

        # Micro-average: total valid / total words across all entries
        total_words = sum(r["fst_total_words"] for r in entry_results)
        total_valid = sum(r["fst_valid_words"] for r in entry_results)
        corpus_rate = total_valid / max(total_words, 1)

        return {
            "avg_fst_validity": avg_validity,
            "total_words_checked": total_words,
            "total_valid_words": total_valid,
            "corpus_validity_rate": corpus_rate,
        }
