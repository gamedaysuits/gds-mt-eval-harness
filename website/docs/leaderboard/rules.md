---
sidebar_position: 1
title: MT Evaluation
---

# MT Evaluation

> **Executive Summary.** This page defines the leaderboard submission criteria, scoring metrics (chrF++, FST acceptance, exact match, equivalent match, semantic score), anti-gaming policies, verification tiers, and the submission workflow. Methods that have been exposed to evaluation data are disqualified.

champollion includes a machine translation evaluation framework designed for **reproducible benchmarking** of translation methods — especially for low-resource and Indigenous languages where standard MT benchmarks don't exist and quality claims are hard to verify.

---

## The Leaderboard

The centerpiece is the **[Method Leaderboard](https://champollion.dev/leaderboard)** — a live, Supabase-backed scoreboard where researchers and community members submit and compare translation methods with fingerprinted, reproducible evaluation.

Every submission includes:

- **Fingerprinted pipeline** — tied to a specific Git commit and config hash, so results trace back to the exact code that produced them
- **Versioned dataset** — content-hashed and versioned; scores are only comparable within the same dataset version
- **Standardised metrics** — all scoring is computed by the shared evaluation harness, eliminating implementation differences
- **Trust tiers** — self-benchmarked, GDS Verified, or Community Validated
- **Cost tracking** — API cost per submission, so cost–quality tradeoffs are transparent

The leaderboard currently tracks five metrics. Three work for any language; two are available for Plains Cree and will be generalized as we expand:

| Metric | Type | What It Measures |
|--------|------|------------------|
| **chrF++** | Character n-gram F-score | Primary quality metric — correlates well with human judgement, especially for morphologically rich languages |
| **Exact Match** | Proportion of perfect matches | Strict accuracy — how often is the translation exactly the gold standard? |
| **FST Acceptance** | Morphological gate pass rate | For methods with finite-state transducer verification — what proportion of outputs are morphologically valid? |
| **Equivalent Match** | Acceptable variant rate | Fraction matching the reference or an acceptable variant (word order, orthographic convention). Currently CRK; generalizing. |
| **Semantic Score** | Semantic fidelity | Meaning preservation — does the translation capture the intended meaning regardless of surface form? Currently CRK; generalizing. |

:::info Full Metric Suite
The [Scoring Specification](/docs/specifications/scoring) defines the complete 19-metric inventory across 5 categories, composite score formula, weight tables, and quality tier thresholds.
:::

**[→ View the leaderboard](https://champollion.dev/leaderboard)**

---

## Available Datasets

### EDTeKLA Development Set v1

The first evaluation dataset, built for English→Plains Cree (SRO) translation. Created by the [EdTeKLA research group](https://spaces.facsci.ualberta.ca/edtekla/) at the University of Alberta.

| Property | Value |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Language pair** | EN → CRK (Plains Cree, SRO orthography) |
| **Entry count** | 124 |
| **License** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| **Provenance** | `gold_standard` (verified by speakers), `textbook` (published educational materials) |

### FLORES+ Devtest — Development Use Only

> [!WARNING]
> **FLORES+ is available for development and debugging but is NOT used for official leaderboard evaluation.** FLORES+ (originally Meta FLORES-200) is a widely public benchmark dataset that frontier LLMs have almost certainly been trained on. Scores against FLORES+ do not reliably reflect real-world translation quality for LLM-based methods. Non-LLM methods (FST, rule-based, fine-tuned NMT) are less affected but FLORES+ scores are still not published to the leaderboard.

FLORES+ fixtures remain available in `test/benchmark/fixtures/` for pipeline smoke testing, cross-language validation, and development use. Official evaluation uses custom corpora built from human-authored text not publicly available in parallel form.

See [Evaluation Datasets](/docs/leaderboard/datasets) for the full dataset schema, difficulty tiers, and how to create your own.

:::danger DO NOT TRAIN on evaluation data

**These datasets are evaluation-only.** Methods trained, fine-tuned, few-shot-prompted, or otherwise exposed to evaluation data will produce artificially inflated scores and will be **disqualified from the leaderboard.**

This is not a suggestion — it is the single most important rule of evaluation integrity. Use separate corpora for training. Evaluation sets must remain unseen by your model during development.

If you are using coaching data or few-shot examples, those must come from **completely separate sources**. If in doubt, don't include it.
:::

:::warning LLM non-determinism

LLM outputs are non-deterministic. Scores represent point-in-time measurements under specific model versions and API configurations. Model providers may update weights, decoding strategies, or safety filters at any time, which can cause score drift between runs. The leaderboard records the exact model slug and timestamp for every submission.
:::

---

## What Makes a Good Method

Not all methods are created equal. Here's what separates rigorous work from inflated scores.

### Characteristics of a strong method

- **Clean separation of train and eval data** — your method has never seen the evaluation set during development, tuning, prompt engineering, or few-shot example selection
- **Reproducible** — someone else can clone your repo, run the harness, and get the same scores (within LLM non-determinism bounds)
- **Documented** — your [method card](/docs/specifications/methods) describes what your method does, what tools it uses, and what its limitations are
- **Honest about scope** — if your method only works for one language pair, say so; if it degrades on certain morphological patterns, document that
- **Community-aware** — for Indigenous languages, your method respects data sovereignty. You've consulted with language communities or used only openly licensed data

### Red flags (what gets disqualified)

| Red Flag | Why It's a Problem |
|----------|--------------------|
| Training on eval data | Defeats the purpose of evaluation entirely. Inflated scores mislead everyone. |
| Cherry-picking results | Running 10 times and submitting the best run without disclosing the others |
| Undisclosed post-processing | Manually fixing outputs before scoring |
| Contaminated coaching data | Using eval set examples as few-shot prompts or dictionary entries |
| Claiming commercial readiness without provenance | If your method uses CC BY-NC-SA data, it's not commercially ready |

### Verification tiers

Verification tiers describe **who validated the result** — separate from the quality tiers (Baseline → Fluent) defined in the [Scoring Specification, §5](/docs/specifications/scoring#5-quality-tiers), which describe what the automated composite score means.

| Tier | Meaning | How to Get It |
|------|---------|--------------|
| **Self-benchmarked** | You ran the harness yourself and submitted results | Open a PR with your run card |
| **GDS Verified** | The champollion maintainers reproduced your results | Submit your method as an installable plugin |
| **Community Validated** | Governance org ran against gold-standard + community review | Submit method code to governance org |

---

## How to Submit

1. **Build your method** — see [Building a Method](/docs/specifications/methods) for the method interface
2. **Run the harness** — see [Eval Harness](/docs/specifications/harness) for setup and usage
3. **Generate a run card** — the harness produces a JSON run card with your scores, fingerprint, and metadata
4. **Open a PR** — submit your run card to the [eval harness repository](https://github.com/gamedaysuits/arena)
5. **Appear on the leaderboard** — once merged, your results appear on the [Method Leaderboard](https://champollion.dev/leaderboard)

---

## Future Directions

- **Comprehensive model comparison runs** — systematic evaluation of frontier models (GPT-4o, Claude, Gemini, etc.) across champollion languages using custom evaluation corpora (not public benchmarks)
- **More language pairs** — Quechua, Inuktitut, and other low-resource languages as community-verified datasets become available
- **Dataset import** — tooling to convert external evaluation datasets (WMT, Tatoeba, etc.) into the champollion evaluation format
- **Automated re-runs** — detecting model version changes and re-running benchmarks to track score drift

---

## See Also

- **[Method Leaderboard](https://champollion.dev/leaderboard)** — live scores and submissions
- **[Eval Harness](/docs/specifications/harness)** — how to run evaluations
- **[Evaluation Datasets](/docs/leaderboard/datasets)** — dataset format and available datasets
- **[Building a Method](/docs/specifications/methods)** — the method interface specification
- **[Run Card Specification](/docs/specifications/run-card)** — the run card JSON schema
- **[Benchmark Specification](/docs/specifications/benchmark)** — evaluation protocol, corpus format, sovereignty
- **[Scoring Specification](/docs/specifications/scoring)** — SSOT for metrics, composite weights, and quality tiers
