"""
Plains Cree (CRK) Evaluation Standards — LYSS

LYSS (Linguistic Yield Scoring System) provides deterministic,
morphology-aware evaluation for Plains Cree translations.

Components:
    linter.py              — LYSS-eq: variant-class equivalence detector
    semantic_validator.py  — LYSS-sem: FST + gloss + spaCy semantic validator
    convention_normalizer.py — SRO orthographic convention normalizer
    fst_adapter.py         — Thin pyhfst adapter (replaces CrkGenerator)
    metrics.py             — MetricPlugin wrappers for harness integration
    data/lemmas.json       — CRK dictionary glosses (5MB)

These modules were extracted from crk-translate/eval/ to establish
proper separation between evaluation standards (referee) and
translation methods (contestants).
"""
