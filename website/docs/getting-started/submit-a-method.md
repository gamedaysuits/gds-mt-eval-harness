---
sidebar_position: 1
title: Submit a Method
related:
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
    note: "The contract your method implements"
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
    note: "What every published run must disclose"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
    note: "The fastest first method to submit"
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
---

# Submit a Method

> **Executive Summary.** A step-by-step quickstart for submitting your first benchmark run to the leaderboard. Clone the harness, run it against a dataset, review your run card, and submit. Takes 10 minutes if you have an API key.

This guide walks you through submitting your first benchmark run to the MT Eval Arena leaderboard.

---

## Prerequisites

- **Python 3.10+**
- **An OpenRouter API key** (or equivalent for your model provider)
- **A translation method** — anything that produces translations from a source text

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## Step 1: Run the Harness

The harness scores your method against a standardized dataset:

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| Flag | What It Does |
|---|---|
| `--corpus` | Path to the evaluation corpus (`.json`, `.jsonl`, `.tsv`) |
| `--model` | Model slug — short alias (e.g. `gemini-pro`) or full OpenRouter ID |
| `--condition` | Label for your method (appears on leaderboard) |
| `--temperature` | Sampling temperature (lower = more deterministic) |
| `--fst-retries` | Optional: number of FST retry attempts |
| `--submit` | Auto-submit the run card to the leaderboard |

The harness produces a **run card** — a self-contained JSON file with your scores, the dataset hash, the model slug, and a cryptographic fingerprint tying results to the exact experiment configuration.

---

## Step 2: Review Your Run Card

Run cards are saved to `results/`. Inspect yours before submitting:

```bash
cat results/your-run-card.json | python -m json.tool
```

Key fields to check:
- `scores.chrf_plus_plus` — your primary quality metric
- `scores.exact_match_rate` — proportion of perfect translations
- `scores.fst_acceptance_rate` — morphological validity (if FST was used)
- `totals.total_cost_usd` — what the run cost
- `fingerprint` — the experiment's reproducibility hash

See the [Run Card Specification](/docs/specifications/run-card) for the full schema.

---

## Step 3: Submit

### Automatic submission

If you passed `--submit` when running the harness, your run card was already uploaded.

### Manual submission

Submit any run card via the API:

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

Or upload through the [Leaderboard UI](https://champollion.dev/leaderboard).

---

## What Happens Next

1. Your submission is validated (dataset hash, run card integrity)
2. Results appear on the leaderboard as **Self-benchmarked** (trust tier 1)
3. To get **GDS Verified** status, submit your method as an installable plugin so maintainers can reproduce your results
4. For Indigenous language methods: if your method reaches the top, the [ownership transfer](/docs/sovereignty/ownership-transfer) process begins

---

## See Also

- [Harness Usage](/docs/specifications/harness) — full CLI reference
- [Leaderboard Rules](/docs/leaderboard/rules) — submission criteria and anti-gaming policies
- [Building a Method](/docs/specifications/methods) — the TranslationMethod protocol
- [Datasets](/docs/leaderboard/datasets) — available evaluation datasets
