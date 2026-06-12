"""
Semantic Validator — Fully deterministic lemma-level translation quality assessment.

Validates non-exact-match translations through a three-step process that
requires ZERO Cree knowledge and ZERO API calls:

  1. FST ANALYZE both pipeline output and textbook reference → extract lemmas
  2. DICTIONARY LOOKUP → get English gloss for each lemma
  3. CONTENT-WORD OVERLAP → compare glosses using spaCy lemmatization

The core insight: if the pipeline chose lemma A (gloss: "s/he writes on a
typewriter") and the reference used lemma B (gloss: "s/he writes"), we extract
content words from both glosses ({write} and {write}) and check overlap.
Shared content words = same semantic field = valid alternate translation.

No shared content words = different concept = genuinely wrong lemma choice.

Verdict categories (reformed):
  EXACT_MATCH      — byte-for-byte identical to reference
  VALID            — identical lemma sets, just inflection/order difference
  GRAMMAR_ISSUES   — correct lemma inventory but sentence-level grammar
                     checker found structural issues (agreement, animacy,
                     verb form) — NOT about word sequence
  PARTIAL          — some correct lemmas, but others missing or wrong
  INCOMPLETE       — pipeline compressed the translation (missing content)
  WRONG            — genuinely wrong lemma choices, no semantic overlap
  NO_OUTPUT        — pipeline produced nothing

Usage:
    python eval/semantic_validator.py eval/logs/benchmark/decomposed_*.json
    python eval/semantic_validator.py --threshold 0.0 FILE.json   # strict: any overlap
"""

# NOTE: The verdict formerly known as 'WRONG_ORDER' was renamed to 'GRAMMAR_ISSUES'
# (2026-06-07) because it was misleading. This verdict fires when the pipeline's
# sentence-level grammar checker (Step 5.5) flags structural problems (agreement,
# animacy, verb form) — it does NOT penalize word sequence. Cree has pragmatically
# free word order (Wolfart 1973 §3.2); linear token order is never evaluated.

import argparse
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import spacy

# LYSS eval_standards imports — decoupled from crk-translate
from mt_eval_harness.eval_standards.crk.fst_adapter import FSTAnalyzer
from mt_eval_harness.eval_standards.crk.convention_normalizer import ConventionNormalizer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# spaCy model with word vectors (needed for lemmatization, not similarity)
NLP_MODEL = "en_core_web_md"

RESULTS_DIR = Path(__file__).parent / "logs" / "semantic_validation"

# Preverb prefixes to strip when extracting base lemmas from FST analyses
PREVERB_PREFIXES = [
    "PV/ki+", "PV/ka+", "PV/e+", "PV/wi+", "PV/pe+",
    "PV/nitawi+", "PV/ati+", "PV/ohci+", "PV/kaa+",
    "PV/nohte+", "PV/poni+", "PV/sipwe+", "PV/koci+",
    "PV/kakwe+", "PV/maci+", "PV/papa+", "PV/wani+",
    "RdplW+", "RdplS+", "IC+",
]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class LemmaInfo:
    """A lemma extracted from FST analysis with its dictionary gloss."""
    lemma: str
    gloss: str
    full_analysis: str
    source_word: str


@dataclass
class LemmaPairVerdict:
    """Judgment on a single differing lemma pair."""
    pred_lemma: str
    pred_gloss: str
    ref_lemma: str
    ref_gloss: str
    shared_content_words: list[str]
    verdict: str  # EQUIVALENT / WRONG / NO_GLOSS


@dataclass
class EntryValidation:
    """Complete validation result for one translation entry."""
    english: str
    predicted: str
    reference: str
    verdict: str = ""
    pred_lemmas: list[LemmaInfo] = field(default_factory=list)
    ref_lemmas: list[LemmaInfo] = field(default_factory=list)
    shared_lemma_names: list[str] = field(default_factory=list)
    pair_verdicts: list[LemmaPairVerdict] = field(default_factory=list)
    notes: str = ""
    sentence_check: dict | None = None
    """Sentence-level grammar check results from pipeline Step 5.5."""


# ---------------------------------------------------------------------------
# NLP: content word extraction
# ---------------------------------------------------------------------------

def load_nlp():
    """Load the spaCy model for English lemmatization."""
    return spacy.load(NLP_MODEL)


def extract_content_words(nlp, text: str) -> set[str]:
    """Extract meaningful content-word lemmas from English text.

    Keeps nouns, verbs, adjectives, adverbs. Drops pronouns, determiners,
    auxiliaries, stop words. Returns lowercased lemmas.
    """
    doc = nlp(text.lower())
    content = set()
    for token in doc:
        if token.pos_ in ("NOUN", "VERB", "ADJ", "ADV") and not token.is_stop:
            content.add(token.lemma_)
    return content


# ---------------------------------------------------------------------------
# Dictionary loader
# ---------------------------------------------------------------------------

def load_gloss_map() -> dict[str, str]:
    """Load lemma → English gloss mapping from the Wolvengrey dictionary."""
    dict_path = Path(__file__).parent / "data" / "lemmas.json"
    with open(dict_path) as f:
        db = json.load(f)

    gloss_map = {}
    for category in ["verbs", "nouns", "particles", "pronouns"]:
        if category in db:
            for lemma, info in db[category].items():
                if isinstance(info, dict) and "gloss" in info:
                    gloss_map[lemma] = info["gloss"]
    return gloss_map


# ---------------------------------------------------------------------------
# FST analysis helpers
# ---------------------------------------------------------------------------

def extract_base_lemma(analysis: str) -> str:
    """Extract root lemma from FST analysis string, stripping preverbs."""
    base = analysis
    for pv in PREVERB_PREFIXES:
        base = base.replace(pv, "")
    return base.split("+")[0]


def analyze_sentence(
    gen: FSTAnalyzer,
    sentence: str,
    gloss_map: dict[str, str],
) -> tuple[bool, list[LemmaInfo]]:
    """FST-analyze every word in a Cree sentence, return lemma info.

    Returns (all_words_analyzable, lemma_info_list).
    """
    words = sentence.strip().split()
    all_ok = True
    lemmas = []

    for w in words:
        if not w.strip():
            continue
        result = gen.analyze(w)
        if result.success and result.analyses:
            best = result.analyses[0]
            lemma = extract_base_lemma(best)
            gloss = gloss_map.get(lemma, "")
            lemmas.append(LemmaInfo(
                lemma=lemma, gloss=gloss,
                full_analysis=best, source_word=w,
            ))
        else:
            all_ok = False
            lemmas.append(LemmaInfo(
                lemma=w, gloss="[FST UNKNOWN]",
                full_analysis="", source_word=w,
            ))

    return all_ok, lemmas


# ---------------------------------------------------------------------------
# Morphological word counting (P0 fix)
# ---------------------------------------------------------------------------

def _count_morphological_words(text: str) -> int:
    """Count morphological units, splitting hyphenated preverb-verb fusions.

    The FST produces preverb-fused surface forms per ALTLab standard
    (e.g. nikî-wâpahtên, nika-nitawi-sêsâwipahtân), while textbook
    references use space-separated convention (nikî wâpahtên).
    Both are valid SRO — the word-count ratio should not penalize
    the pipeline for following the FST authority.

    Splits each whitespace token on hyphens to count morphological
    units rather than typographic words.
    """
    count = 0
    for word in text.strip().split():
        # Each hyphen-separated segment is a morphological unit
        # e.g. nika-nitawi-sêsâwipahtân → 3 units
        parts = word.split("-")
        count += len(parts)
    return count


# ---------------------------------------------------------------------------
# Lemma normalization (P1 fix)
# ---------------------------------------------------------------------------

# Common SRO diacritic/spelling alternations that don't change meaning.
# Used to unify lemma sets before comparison.
_LEMMA_NORMALIZATIONS = [
    # Vowel length variants
    ("kîkwâya", "kîkwaya"),
    ("awîna", "awêna"),
    ("tâniwê", "tânité"),
    ("tâniwâ", "tânité"),
    # ê → ê with alternate accent rendering
]


def _normalize_lemma(lemma: str) -> str:
    """Normalize a Cree lemma to a canonical form for fairer comparison.

    Handles dialectal variants and common SRO alternations that
    represent the same lexeme with different orthographic conventions.
    """
    normalized = lemma.lower().strip()
    # Apply known equivalences — map all variants to one canonical form
    for a, b in _LEMMA_NORMALIZATIONS:
        if normalized == a:
            normalized = b
            break
        if normalized == b:
            # Already canonical
            break
    return normalized


# Shared normalizer instance
_convention_normalizer = ConventionNormalizer()


# ---------------------------------------------------------------------------
# Structural word detection (P3 expanded)
# ---------------------------------------------------------------------------

# Grammatical/structural lemmas: negators, question particles, locatives,
# demonstratives, existential verbs, conjunctions, discourse particles.
# These are syntactic scaffolding — adding or omitting them reflects
# construction choice, not semantic error.
_STRUCTURAL_LEMMAS = {
    # Negators
    "namôya", "êkâ", "môya", "môy", "namôy", "êkâwiya",
    # Question particles
    "cî",
    # Conjunctions / discourse particles
    "êkwa", "mâka", "mîna", "ahpô", "piko",
    # Discourse / pragmatic particles (P3 expansion)
    # These mark emphasis, deixis, or pragmatic focus. Their presence
    # or absence changes naturalness/fluency, not semantic content.
    "ôma", "ici", "aniki", "ana", "awa", "ôki", "anihi",
    "kiyânaw", "kiyawâw",
    # Temporal / adverbial particles
    "ispîhk", "sêmâk", "âsay", "mêkwâc", "wîpac", "wîpacêas",
    "kêtisk", "nâkê",
    # Locatives / demonstratives
    "anita", "êkota", "nêtê", "ôta", "anima",
    # Existential / positional verbs (used to express "is/are there")
    "apiw", "ayâw", "astêw", "itastêw",
    # Temporal
    "anohc", "wêskacês",
    # Pronouns / personal reference
    "niya", "kiya", "wiya",
}

# FST tag patterns that indicate structural/grammatical word classes
_STRUCTURAL_TAG_PATTERNS = ["+Ipc", "+Pron", "+Dem"]


def _is_structural_word(li: LemmaInfo) -> bool:
    """Check if a lemma is a structural/grammatical word.

    Uses two signals:
      1. Known structural lemma set (negators, particles, etc.)
      2. FST tag patterns indicating grammatical word classes
    """
    if li.lemma in _STRUCTURAL_LEMMAS:
        return True
    # Also check the normalized form
    if _normalize_lemma(li.lemma) in _STRUCTURAL_LEMMAS:
        return True
    for pattern in _STRUCTURAL_TAG_PATTERNS:
        if pattern in li.full_analysis:
            return True
    return False


# ---------------------------------------------------------------------------
# Core validation logic — fully deterministic, no API calls
# ---------------------------------------------------------------------------

def validate_entry(
    entry: dict,
    gen: FSTAnalyzer,
    gloss_map: dict[str, str],
    nlp,
) -> EntryValidation:
    """Validate a single translation entry. Fully offline."""
    english = entry.get("english", "")
    predicted = entry.get("predicted", "").strip()
    reference = entry.get("expected", "").strip()

    result = EntryValidation(english=english, predicted=predicted, reference=reference)

    # --- Exact match: trivially valid ---
    if predicted == reference:
        result.verdict = "EXACT_MATCH"
        return result

    # --- No output: skip ---
    if not predicted:
        result.verdict = "NO_OUTPUT"
        return result

    # --- FST decomposition ---
    pred_ok, result.pred_lemmas = analyze_sentence(gen, predicted, gloss_map)
    ref_ok, result.ref_lemmas = analyze_sentence(gen, reference, gloss_map)

    # Build unique lemma sets (excluding FST unknowns)
    # P1: Normalize lemmas before comparison to handle diacritic variants
    pred_raw_set = {li.lemma for li in result.pred_lemmas if li.gloss != "[FST UNKNOWN]"}
    ref_raw_set = {li.lemma for li in result.ref_lemmas if li.gloss != "[FST UNKNOWN]"}

    # Build normalized→raw mapping for later lookup
    pred_norm_map = {_normalize_lemma(l): l for l in pred_raw_set}
    ref_norm_map = {_normalize_lemma(l): l for l in ref_raw_set}

    pred_set = set(pred_norm_map.keys())
    ref_set = set(ref_norm_map.keys())

    result.shared_lemma_names = sorted(pred_set & ref_set)
    pred_only = pred_set - ref_set
    ref_only = ref_set - pred_set

    # --- Same lemma set: valid (just inflection / word-order difference) ---
    if not pred_only and not ref_only:
        # Check if there are sentence-level grammar errors despite correct lemmas
        sentence_check = entry.get("sentence_check", None)
        result.sentence_check = sentence_check
        has_grammar_errors = (
            sentence_check is not None
            and len(sentence_check.get("errors", [])) > 0
        )
        # P0: Use morphological word count (splits hyphens) for fair comparison
        pred_wc = _count_morphological_words(predicted)
        ref_wc = _count_morphological_words(reference)
        is_compressed = (pred_wc / ref_wc < 0.5) if ref_wc >= 3 else False

        if is_compressed:
            result.verdict = "INCOMPLETE"
            result.notes = (
                f"Same lemma set but word count compressed "
                f"({pred_wc} vs {ref_wc} morphological words)"
            )
        elif has_grammar_errors:
            # Correct lemmas but sentence-level grammar checker found
            # structural issues (agreement, animacy, verb form) — not
            # about word sequence (Cree has free word order).
            result.verdict = "GRAMMAR_ISSUES"
            result.notes = (
                "Identical lemma sets but sentence-level grammar issues "
                "(agreement/animacy/verb form): "
                + "; ".join(sentence_check.get("errors", []))
            )
        else:
            result.verdict = "VALID"
            result.notes = "Identical lemma sets — differences are inflection or word order only."
        return result

    # --- Compare differing lemmas via English gloss content words ---
    # Build lookup for quick access
    # Map normalized lemma back to LemmaInfo for gloss lookup
    pred_gloss_by_lemma = {
        _normalize_lemma(li.lemma): li
        for li in result.pred_lemmas
        if _normalize_lemma(li.lemma) in pred_only
    }
    ref_gloss_by_lemma = {
        _normalize_lemma(li.lemma): li
        for li in result.ref_lemmas
        if _normalize_lemma(li.lemma) in ref_only
    }

    pred_only_list = sorted(pred_only)
    ref_only_list = sorted(ref_only)

    # For each pipeline-only lemma, check if its gloss overlaps with
    # any reference-only lemma's gloss (they could be synonyms).
    has_wrong = False
    all_matched = True

    # Pair up: for each pred-only lemma, try to find a matching ref-only lemma
    used_refs = set()

    for pl in pred_only_list:
        pred_li = pred_gloss_by_lemma.get(pl)
        if not pred_li or not pred_li.gloss:
            # No gloss available — can't judge
            result.pair_verdicts.append(LemmaPairVerdict(
                pred_lemma=pl, pred_gloss="",
                ref_lemma="?", ref_gloss="",
                shared_content_words=[], verdict="NO_GLOSS",
            ))
            continue

        pred_content = extract_content_words(nlp, pred_li.gloss)
        best_match = None
        best_overlap = set()

        # Check against all unused ref-only lemmas
        for rl in ref_only_list:
            if rl in used_refs:
                continue
            ref_li = ref_gloss_by_lemma.get(rl)
            if not ref_li or not ref_li.gloss or ref_li.gloss == "[FST UNKNOWN]":
                continue

            ref_content = extract_content_words(nlp, ref_li.gloss)
            overlap = pred_content & ref_content

            if len(overlap) > len(best_overlap):
                best_match = ref_li
                best_overlap = overlap

        if best_match and best_overlap:
            # Found a semantic match — these are equivalent word choices
            used_refs.add(best_match.lemma)
            result.pair_verdicts.append(LemmaPairVerdict(
                pred_lemma=pl, pred_gloss=pred_li.gloss[:120],
                ref_lemma=best_match.lemma, ref_gloss=best_match.gloss[:120],
                shared_content_words=sorted(best_overlap),
                verdict="EQUIVALENT",
            ))
        else:
            # No gloss overlap with any reference lemma — but this may still
            # be a valid addition rather than a wrong word choice.
            #
            # Three checks before calling it WRONG:
            #   1. Does the gloss relate to the English source?
            #   2. Is this a structural/grammatical word?  (negators, question
            #      markers, locatives, existential verbs are syntactic scaffolding
            #      that different Cree constructions require)
            #   3. Does the FST analysis reveal it's a grammatical category
            #      that serves structural rather than semantic purpose?

            source_content = extract_content_words(nlp, english)
            source_overlap = pred_content & source_content

            # Check if the word's FST analysis indicates a structural role
            is_structural = _is_structural_word(pred_li)

            if source_overlap:
                # The pipeline's word relates to the source even if the
                # reference didn't use it — mark as acceptable, not wrong
                result.pair_verdicts.append(LemmaPairVerdict(
                    pred_lemma=pl, pred_gloss=pred_li.gloss[:120],
                    ref_lemma="(no match)", ref_gloss="",
                    shared_content_words=sorted(source_overlap),
                    verdict="ADDED_VALID",
                ))
            elif is_structural:
                # Structural/grammatical addition — different construction,
                # not a meaning error (e.g. adding a negator, question marker,
                # or existential verb that the reference expressed differently)
                result.pair_verdicts.append(LemmaPairVerdict(
                    pred_lemma=pl, pred_gloss=pred_li.gloss[:120],
                    ref_lemma="(structural)", ref_gloss="",
                    shared_content_words=[], verdict="ADDED_STRUCTURAL",
                ))
            else:
                has_wrong = True
                result.pair_verdicts.append(LemmaPairVerdict(
                    pred_lemma=pl, pred_gloss=pred_li.gloss[:120],
                    ref_lemma="(no match)", ref_gloss="",
                    shared_content_words=[], verdict="WRONG",
                ))

    # Check for reference lemmas the pipeline completely missed
    for rl in ref_only_list:
        if rl in used_refs:
            continue
        ref_li = ref_gloss_by_lemma.get(rl)
        if not ref_li or ref_li.gloss == "[FST UNKNOWN]":
            continue
        # Pipeline omitted a concept the reference expressed
        result.pair_verdicts.append(LemmaPairVerdict(
            pred_lemma="(omitted)", pred_gloss="",
            ref_lemma=rl, ref_gloss=ref_li.gloss[:120] if ref_li.gloss else "",
            shared_content_words=[], verdict="OMITTED",
        ))

    # --- Overall verdict ---
    verdicts = [pv.verdict for pv in result.pair_verdicts]
    non_gloss_verdicts = [v for v in verdicts if v != "NO_GLOSS"]

    # Count how many content lemmas are in each category
    n_equivalent = verdicts.count("EQUIVALENT") + verdicts.count("ADDED_VALID")
    n_structural = verdicts.count("ADDED_STRUCTURAL")
    n_wrong = verdicts.count("WRONG")
    n_omitted = verdicts.count("OMITTED")

    # --- Word-count completeness check (P0 fix: morphological counting) ---
    # If the pipeline output has significantly fewer morphological words
    # than the reference, it compressed the translation.
    # Uses _count_morphological_words() which splits hyphens to avoid
    # false positives from FST-standard preverb-verb fusion.
    pred_word_count = _count_morphological_words(predicted)
    ref_word_count = _count_morphological_words(reference)
    word_ratio = pred_word_count / ref_word_count if ref_word_count > 0 else 1.0
    is_compressed = word_ratio < 0.5 and ref_word_count >= 3

    # --- P3: Classify omissions as structural vs content ---
    # If every omitted lemma is structural (discourse particles, demonstratives,
    # temporal markers), the translation is semantically complete — it just
    # uses a different construction that doesn't require those particles.
    n_omitted_structural = 0
    n_omitted_content = 0
    for pv in result.pair_verdicts:
        if pv.verdict == "OMITTED":
            # Look up the omitted ref lemma in our structural set
            ref_li_match = ref_gloss_by_lemma.get(pv.ref_lemma)
            if ref_li_match and _is_structural_word(ref_li_match):
                n_omitted_structural += 1
            elif pv.ref_lemma in _STRUCTURAL_LEMMAS:
                # Direct lemma match (no LemmaInfo needed)
                n_omitted_structural += 1
            elif _normalize_lemma(pv.ref_lemma) in _STRUCTURAL_LEMMAS:
                n_omitted_structural += 1
            else:
                n_omitted_content += 1

    # All omissions are structural? Not a real incompleteness.
    all_omitted_are_structural = (n_omitted > 0 and n_omitted_content == 0)

    # --- Sentence-level grammar issues ---
    # Pull in sentence_check data if available (from pipeline Step 5.5)
    sentence_check = entry.get("sentence_check", None)
    result.sentence_check = sentence_check
    has_grammar_errors = (
        sentence_check is not None
        and len(sentence_check.get("errors", [])) > 0
    )

    # --- Verdict assignment (strict, no permissive ACCEPTABLE bucket) ---
    if "WRONG" in verdicts:
        result.verdict = "WRONG"
    elif is_compressed and not all_omitted_are_structural:
        # Pipeline compressed the translation — missing content
        result.verdict = "INCOMPLETE"
        result.notes = (
            f"Word count ratio {word_ratio:.2f} "
            f"({pred_word_count} vs {ref_word_count} morphological words)"
        )
    elif n_omitted > 0 and n_wrong == 0:
        # P3: If all omitted lemmas are structural, treat as VALID
        if all_omitted_are_structural:
            if has_grammar_errors:
                # Correct lemmas but sentence-level grammar checker found
                # structural issues (agreement, animacy, verb form) — not
                # about word sequence (Cree has free word order).
                result.verdict = "GRAMMAR_ISSUES"
                result.notes = (
                    f"{n_omitted} structural word(s) omitted (tolerable), "
                    "but sentence-level grammar issues "
                    "(agreement/animacy/verb form): "
                    + "; ".join(sentence_check.get("errors", []))
                )
            else:
                result.verdict = "VALID"
                result.notes = (
                    f"{n_omitted_structural} structural/discourse word(s) omitted "
                    f"(tolerable — different construction, same meaning)"
                )
        elif n_equivalent > 0:
            result.verdict = "PARTIAL"
            result.notes = (
                f"{n_omitted_content} content lemma(s) omitted, "
                f"{n_omitted_structural} structural omitted (tolerable), "
                f"{n_equivalent} correct"
            )
        else:
            result.verdict = "INCOMPLETE"
            result.notes = (
                f"{n_omitted_content} content lemma(s) omitted, "
                f"{n_omitted_structural} structural omitted (tolerable), "
                "none matched"
            )
    elif all(v in ("EQUIVALENT", "ADDED_VALID", "ADDED_STRUCTURAL")
             for v in non_gloss_verdicts):
        # All lemma differences are semantically valid
        if has_grammar_errors:
            # Correct lemmas but sentence-level grammar checker found
            # structural issues (agreement, animacy, verb form) — not
            # about word sequence (Cree has free word order).
            result.verdict = "GRAMMAR_ISSUES"
            result.notes = (
                "Correct lemma inventory but sentence-level grammar issues "
                "(agreement/animacy/verb form): "
                + "; ".join(sentence_check.get("errors", []))
            )
        else:
            result.verdict = "VALID"
    else:
        # Catch-all: some issues but not cleanly categorized
        result.verdict = "PARTIAL"
        result.notes = f"Mixed verdicts: {', '.join(non_gloss_verdicts)}"

    return result


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------

def validate_benchmark(benchmark_path: Path) -> dict:
    """Validate all entries in a benchmark JSON file. Fully offline."""
    with open(benchmark_path) as f:
        data = json.load(f)

    entries = data.get("entries", [])
    model_name = data.get("model", benchmark_path.stem)

    logger.info("Validating %d entries from %s", len(entries), benchmark_path.name)

    gen = FSTAnalyzer(lang_code="crk")
    gloss_map = load_gloss_map()
    nlp = load_nlp()
    logger.info("Dictionary: %d lemmas | spaCy: %s loaded", len(gloss_map), NLP_MODEL)

    results = [validate_entry(e, gen, gloss_map, nlp) for e in entries]

    # --- Aggregate ---
    counts = {}
    for r in results:
        counts[r.verdict] = counts.get(r.verdict, 0) + 1

    total = len(results)
    exact = counts.get("EXACT_MATCH", 0)
    valid = counts.get("VALID", 0)
    grammar_issues = counts.get("GRAMMAR_ISSUES", 0)
    partial = counts.get("PARTIAL", 0)
    incomplete = counts.get("INCOMPLETE", 0)
    wrong = counts.get("WRONG", 0)
    no_output = counts.get("NO_OUTPUT", 0)

    # Strict accuracy: only EXACT_MATCH + VALID count as correct
    # This is the "honest" number that reflects real linguistic fluency.
    strictly_correct = exact + valid
    # Lenient accuracy: includes GRAMMAR_ISSUES and PARTIAL (right idea, imperfect form)
    leniently_correct = strictly_correct + grammar_issues + partial
    judged = total - no_output

    report = {
        "benchmark_file": str(benchmark_path.name),
        "model": model_name,
        "method": "deterministic (FST analyzer + dictionary gloss + spaCy content-word overlap)",
        "total_entries": total,
        "verdict_counts": counts,
        "metrics": {
            "exact_match_rate": round(exact / total, 4) if total else 0,
            "strict_accuracy": round(strictly_correct / total, 4) if total else 0,
            "lenient_accuracy": round(leniently_correct / total, 4) if total else 0,
            "strict_accuracy_of_judged": round(
                strictly_correct / judged, 4
            ) if judged else 0,
            "confirmed_wrong_rate": round(wrong / total, 4) if total else 0,
            "incomplete_rate": round(incomplete / total, 4) if total else 0,
        },
        "entries": [],
    }

    for r in results:
        entry_detail = {
            "english": r.english,
            "predicted": r.predicted,
            "reference": r.reference,
            "verdict": r.verdict,
        }
        if r.pair_verdicts:
            entry_detail["lemma_diffs"] = [
                {
                    "pred": f"{pv.pred_lemma} = \"{pv.pred_gloss}\"",
                    "ref": f"{pv.ref_lemma} = \"{pv.ref_gloss}\"",
                    "shared_words": pv.shared_content_words,
                    "verdict": pv.verdict,
                }
                for pv in r.pair_verdicts
            ]
        if r.notes:
            entry_detail["notes"] = r.notes
        report["entries"].append(entry_detail)

    return report


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_report(report: dict):
    """Print a human-readable summary."""
    counts = report["verdict_counts"]
    metrics = report["metrics"]
    total = report["total_entries"]

    print(f"\n{'='*70}")
    print(f"SEMANTIC VALIDATION: {report['benchmark_file']}")
    print(f"Model: {report['model']}")
    print(f"Method: {report['method']}")
    print(f"{'='*70}\n")

    print(f"  Total entries:            {total}")
    for verdict in [
        "EXACT_MATCH", "VALID", "GRAMMAR_ISSUES",
        "PARTIAL", "INCOMPLETE", "WRONG", "NO_OUTPUT",
    ]:
        c = counts.get(verdict, 0)
        print(f"  {verdict:<24} {c:>4} ({c/total*100:>5.1f}%)")
    print()
    print(f"  ── Accuracy Metrics ──────────────────────────")
    print(f"  Strict accuracy:      {metrics['strict_accuracy']*100:.1f}%")
    print(f"    (Exact + Valid only — real linguistic fluency)")
    print(f"  Lenient accuracy:     {metrics['lenient_accuracy']*100:.1f}%")
    print(f"    (+ Grammar_Issues + Partial — right idea, imperfect form)")
    print(f"  Confirmed wrong:      {metrics['confirmed_wrong_rate']*100:.1f}%")
    print(f"  Incomplete:           {metrics['incomplete_rate']*100:.1f}%")
    print()

    # Show WRONG entries
    wrong_entries = [e for e in report["entries"] if e["verdict"] == "WRONG"]
    if wrong_entries:
        print(f"  ── Wrong Translations ({len(wrong_entries)} total) ─────────────")
        for e in wrong_entries[:15]:
            print(f"\n    EN: \"{e['english'][:70]}\"")
            print(f"    Pred: {e['predicted'][:70]}")
            print(f"    Ref:  {e['reference'][:70]}")
            for d in e.get("lemma_diffs", []):
                if d["verdict"] == "WRONG":
                    print(f"      ✗ Pipeline: {d['pred'][:60]}")
                    print(f"        Expected: {d['ref'][:60]}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Deterministic semantic validation of Cree translation benchmarks"
    )
    parser.add_argument("files", nargs="+", help="Benchmark JSON file(s) to validate")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    for filepath in args.files:
        path = Path(filepath)
        if not path.exists():
            logger.error("File not found: %s", path)
            continue

        report = validate_benchmark(path)
        print_report(report)

        # Save detailed report
        out_name = f"semantic_{path.stem}.json"
        out_path = RESULTS_DIR / out_name
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info("Report saved to %s", out_path)


if __name__ == "__main__":
    main()
