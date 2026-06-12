---
sidebar_position: 4
title: 'Contributing Compute'
description: 'Donate your tokens: run open benchmark sweeps from the public queue with your own API key and publish the results.'
related:
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
  - label: "Cookbook: Coached LLM Prompting"
    to: /docs/tutorials/coached-llm-prompting
    kind: cookbook
  - label: "Cookbook: FST-Gated Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "Method Interface & Dependency Classes"
    to: /docs/specifications/methods
    kind: spec
  - label: "Leaderboard Rules & Trust Tiers"
    to: /docs/leaderboard/rules
    kind: guide
---

# Contributing Compute

> **The idea:** the leaderboard has empty squares — (language pair, model, condition) combinations nobody has measured. We maintain a public queue of them. You run items with your own API key, publish the reports, and the map fills in. "Donating tokens" is a real, citable contribution to low-resource MT evaluation.

## The queue

The live queue is published at [champollion.dev/queue.json](https://champollion.dev/queue.json), and there's a zero-install terminal viewer:

```bash
curl -fsSL champollion.dev/queue | bash
```

The viewer only *displays* open items and their exact `mt-eval run` commands — it never executes anything or spends your tokens. Each item carries:

- `run_command` — copy-paste ready (fetches the corpus, runs the harness)
- `est_cost_usd` and `est_basis` — either the **observed** cost of our own baseline run of the same (corpus, model), or an **extrapolation** from that model's sweep-average cost per entry × the corpus entry count. The basis is stated per item; your actual cost depends on provider pricing at run time.
- `priority` — uncovered language pairs first, lowest-resource pairs first (corpus size is the proxy), naive before coached, cheapest model first.

**No claim-locking — pick any open item.** Two people running the same item is harmless by design: every run card is fingerprinted (SHA-256 over dataset hash + model + condition + system prompt, [Benchmark Spec §3.8](/docs/specifications/benchmark)), so identical runs deduplicate on publish, and independent replications of the same configuration are useful evidence, not waste.

Queued corpora are dev-split, CC-BY-family (Tatoeba-derived), and flagged `do_not_train` — they are evaluation sets, not training data. Non-commercially-licensed and quarantined corpora are excluded from the open queue.

## Setup (once)

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### Which provider key?

The harness routes **all** model calls through [OpenRouter](https://openrouter.ai/keys). One `OPENROUTER_API_KEY` reaches every model in the queue lineup — Anthropic Claude, OpenAI GPT, and Google Gemini models alike — and the harness's cost tracking and pricing snapshots come from the same OpenRouter metadata, so reported run cost matches what your key was billed.

If your credits live with Anthropic, OpenAI, or Google directly: the harness does **not** currently accept direct provider keys. The run-card schema reserves an `api_provider` field for the day it does, but today every harness run is an OpenRouter run. Creating an OpenRouter account and funding it (or attaching your own provider account where OpenRouter supports that) is the supported path.

### The agent fast path

If you work with Claude Code or another coding agent, the whole contribution is one prompt:

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## Tier 1 — Run a benchmark

Every queue item's `run_command` is self-contained. A typical one:

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

The run prints its total cost and writes a run log plus a scored report to `eval/logs/`. Then publish:

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

Publishing signs you in via OAuth (your name becomes the leaderboard attribution) and upserts the run card. Community submissions land at the **self-benchmarked** trust tier — plainly labeled as "submitted by the person who ran it." That's not a demotion; it's the trust model working. The run card carries everything needed for anyone to re-run your exact configuration: dataset hash, model, condition, the full system prompt, and cost. Elevated tiers (verification, community validation) are granted by review — see [Leaderboard Rules](/docs/leaderboard/rules).

## Tier 2 — Craft coached prompts

The harness has first-class support for **coaching**: replace the naive system prompt with one that carries real linguistic knowledge. Pass `--coaching-file` (or `--coaching "inline text"` for short prompts) and the harness uses your text as the system prompt, records the **full text plus its SHA-256** in the run log's provenance block, and labels the run's condition **`coached`** (unless you set `--prompt` explicitly) — so prompt craft is a reproducible, attributable experiment, two different coaching files can never be confused with each other, and coached runs are never mistaken for naive baselines on the leaderboard.

A worked example for Faroese, using typology facts and glossary entries from the language's [public language card](https://champollion.dev/languages):

```text title="coaching-fao.txt"
You are translating Danish into Faroese (føroyskt).

Grammar notes:
- Faroese is a North Germanic V2 language: the finite verb is the second
  constituent of a main clause.
- Nouns inflect for case (nominative, accusative, dative, genitive),
  gender (masculine, feminine, neuter), and number. Make adjectives and
  determiners agree.
- The skerping pattern applies before -gv/-ggj sequences; preserve
  standard orthography including ð (which is silent).

Glossary (use these exact equivalents):
- language -> mál
- island -> oyggj
- weather -> veður

Style: plain register, modern standard orthography. Output only the
Faroese translation, no commentary.
```

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/dan-fao-dev-v1.json
mt-eval run --corpus dan-fao-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Faroese" \
  --coaching-file coaching-fao.txt
```

(Write your own coaching content — the facts above illustrate the *shape*: a few high-impact grammar rules, a small glossary of terms the model gets wrong, a register instruction. Language cards at [champollion.dev/languages](https://champollion.dev/languages) cite typology sources you can draw from.)

Compare against the naive baseline with `mt-eval compare <naive_log> <coached_log>`, iterate, and publish your best run. The run publishes with condition `coached` automatically; if you want the leaderboard to show a named method instead of the generic label, attach a method card when you publish (the publish flow offers a wizard). Beating the naive baseline on a low-resource pair with nothing but prompt engineering is a genuine, publishable finding — see the full [Coached LLM Prompting cookbook](/docs/tutorials/coached-llm-prompting) for design guidance.

## Tier 3 — Build a method

The most ambitious contribution: implement the `TranslationMethod` protocol (`translate(entries, config)`) and benchmark an actual system, not a prompt. The harness runs it via `--method <plugin-dir>` and embeds your method card in the run card. Patterns with worked cookbooks:

- **[FST-gated pipelines](/docs/tutorials/fst-gated-pipeline)** — every candidate word is checked by a morphological analyzer; the LLM regenerates until the gate passes. Semi-deterministic, morphology-guaranteed output.
- **[Dictionary-augmented generation](/docs/tutorials/dictionary-augmented-llm)** — look up source terms in a bilingual lexicon at translation time and constrain the output.
- [Chained models](/docs/tutorials/chained-models), [few-shot retrieval](/docs/tutorials/few-shot-prompting), [back-translation](/docs/tutorials/back-translation), [rule-based hybrids](/docs/tutorials/rule-based-hybrid)…

Methods declare a **dependency class** (S/O/A1/A2/X — see [the methods spec](/docs/specifications/methods#method-validity-and-dependency-classes)) describing what they need to run and transfer: a self-contained pipeline is Class S; one that calls a licensed dictionary API at runtime is A2. Declare honestly — the class determines where your method can compete, and manifests are audited.

## Why this matters beyond the leaderboard

Every published run is independent evidence about MT quality for a language pair that commercial providers don't measure. The queue doubles as a public record of *demand*: which pairs the community considers worth measuring, what coverage costs at current API prices, and how far donated compute stretches. When we ask funding agencies to underwrite systematic sweeps, this queue and its fill-rate are the demand evidence.
