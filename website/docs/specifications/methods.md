---
sidebar_position: 4
title: Method Interface
---

# Shared Method Interface

> **Executive Summary.** This page specifies the `TranslationMethod` protocol that all Arena methods must implement, the six method classes (`raw-llm`, `coached-llm`, `pipeline`, `custom-plugin`, `api`, `human`), and the method plugin format. Any approach that implements this protocol can be benchmarked.

The eval harness and champollion share a common concept of **translation method**. A method is any procedure that takes source text and produces translated text — whether it's a direct LLM call, a multi-stage pipeline, a third-party API, or a human translator.

## Architecture

```
Method Plugin (v2 Spec)
├── method.json           ← Manifest (name, class, entry_point, metadata)
├── method_card.json      ← Leaderboard description (what, not how)
├── pipeline.py           ← Python module implementing TranslationMethod
└── (optional helpers)    ← Additional Python modules
```

Loaded via `--method path/to/dir`. The harness discovers nothing automatically.

## Two Systems, One Interface

| | Eval Harness | champollion |
|---|---|---|
| **Language** | Python | Node.js |
| **Entry point** | `translate.py` | `translate.js` |
| **Interface** | `TranslationMethod` protocol | `methodPlugin` config |
| **Purpose** | Batch evaluation with scoring | Live localization in dev/CI |
| **Output** | Run card with metrics | Translated locale files |

A method that supports both systems provides two entry points — one for each language runtime. The **method card** is the bridge: it describes the method in a format both systems understand.

## Method Card

A method card describes *what* a translation method is without revealing proprietary details like the full system prompt. It answers:

- What class of method is this? (raw LLM, coached LLM, pipeline, API, etc.)
- What tools does it use? (FST analyzer, dictionary, etc.)
- Is the implementation open source?
- What language pairs does it support?

See the [Method Card Spec](/docs/specifications/methods#method-card) for the full JSON schema.

### Example

```json
{
  "method_id": "fst-gated-v8",
  "name": "FST-Gated Coached Translation v8",
  "class": "pipeline",
  "description": "LLM translation with morphological validation. Failed words are retried with FST feedback.",
  "author": "Curtis Forbes",
  "tools_used": ["HFST morphological analyzer", "Wolvengrey dictionary"],
  "open_source": false,
  "supported_pairs": ["eng>crk"]
}
```

### Method Classes

| Class | Description |
|-------|-------------|
| `raw-llm` | Direct LLM call with minimal instruction |
| `coached-llm` | LLM with structured prompt, examples, constraints |
| `pipeline` | Multi-stage pipeline with deterministic components |
| `custom-plugin` | External process implementing the `TranslationMethod` protocol |
| `api` | Third-party translation API (Google Translate, DeepL, etc.) |
| `human` | Human translation (for establishing baselines) |

## Eval Harness: TranslationMethod Protocol

The eval harness uses Python's structural typing (`Protocol`) for plugins. Any class with the right method signature works — no inheritance required:

```python
class MyMethod:
    async def translate(self, entries: list[dict], config: RunConfig) -> list[dict]:
        results = []
        for entry in entries:
            translation = await self.do_translation(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translation,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "error": None,
                "tool_calls": [],
                "tool_call_count": 0,
                "metadata": {},
            })
        return results
```

See the [Plugin Protocol](/docs/specifications/methods#eval-harness-translationmethod-protocol) for complete documentation including wrapper examples for non-Python methods.

## champollion: methodPlugin Config

In champollion, methods are registered per language pair in `champollion.config.json`:

```json
{
  "version": 3,
  "pairs": {
    "en:crk": {
      "methodPlugin": "crk-coached-v1"
    }
  }
}
```

See the [Plugin Spec](https://champollion.dev/docs/reference/plugin-spec) for the champollion-side interface.

## Leaderboard Integration

When a method card is attached to a run (via `--method-card`), it's embedded in the run card and displayed on the leaderboard:

```bash
# Run with method card attached
mt-eval run \
  --method path/to/my-method \
  --corpus data/edtekla-dev-v1.json \
  --method-card method_card.json

# Publish to the leaderboard
mt-eval publish eval/logs/harness/your-run-card.json
```

If no `--method-card` was provided, `mt-eval publish` launches an interactive wizard that walks you through describing your method.

The leaderboard shows:
- **Class badge** — visual indicator (e.g., "pipeline", "coached-llm")
- **Method name** — from the method card
- **Tools used** — listed from the method card
- **Open source indicator**

When no method card is attached, the leaderboard shows harness-native configuration (model, prompt version, temperature, tools enabled).

:::danger DO NOT TRAIN on evaluation data
Methods whose development process included exposure to the evaluation dataset — as training data, few-shot examples, dictionary entries, or prompt tuning material — will be **disqualified** from the leaderboard. See [MT Evaluation](/docs/leaderboard/rules) for what distinguishes a good method from a bad one.
:::

---

## See Also

- [MT Evaluation](/docs/leaderboard/rules) — overview, leaderboard value, and good/bad method guidance
- [Eval Harness](/docs/specifications/harness) — how to run evaluations
- [Evaluation Datasets](/docs/leaderboard/datasets) — available datasets (EDTeKLA, FLORES+)
- [Run Card Specification](/docs/specifications/run-card) — the run card JSON schema
- [Plugin Spec](https://champollion.dev/docs/reference/plugin-spec) — champollion-side plugin interface
- [Method Leaderboard](https://champollion.dev/leaderboard) — live benchmark scores
- [Benchmark Specification](/docs/specifications/benchmark) — evaluation protocol, corpus format, run card schema
- [Scoring Specification](/docs/specifications/scoring) — SSOT for metrics, composite weights, and quality tiers
