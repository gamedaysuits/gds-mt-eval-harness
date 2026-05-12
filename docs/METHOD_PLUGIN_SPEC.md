# i18n-rosetta Method Plugin Specification

> **Version**: 1.0  
> **Audience**: gds-mt-eval-harness development team  
> **Purpose**: Defines the output format the eval harness must produce for a tested translation method to plug into i18n-rosetta as a consumable method with verified quality metrics.

---

## Overview

i18n-rosetta uses a **pluggable method system**. Each language pair can use a different translation method (LLM, coached, script-converter, etc.). Methods are registered in `lib/translate.js` and resolved per-pair via `lib/pairs.js`.

The eval harness's job is to **develop, test, and export** translation methods. i18n-rosetta's job is to **consume and execute** them. The harness never runs inside rosetta.

### Data flow

```
┌─────────────────────┐         method.json          ┌──────────────────┐
│  gds-mt-eval-harness │  ───────────────────────►   │   i18n-rosetta   │
│  (Research tool)      │   + coaching/<locale>.json  │  (Developer tool) │
│  Python / standalone  │                             │  Node.js / npm    │
└─────────────────────┘                              └──────────────────┘
```

---

## Method Plugin Format

A method plugin is a single JSON file (`method.json`) with optional coaching data files. The harness exports this; rosetta reads it.

### `method.json` — Required

```json
{
  "name": "french-formal-v1",
  "type": "llm-coached",
  "version": "1.0.0",
  "description": "Formally-tuned French with terminology enforcement and grammar coaching",
  "author": "GDS Research",

  "config": {
    "model": "openai/gpt-4o-mini",
    "register": "formal",
    "batchSize": 30,
    "temperature": 0.2
  },

  "locales": ["fr"],

  "benchmarks": {
    "fr": {
      "date": "2026-05-11T00:00:00Z",
      "corpus_size": 500,
      "exact_match_rate": 0.42,
      "corpus_chrf": 72.3,
      "corpus_bleu": 45.1,
      "model": "openai/gpt-4o-mini",
      "harness_version": "1.0.0"
    }
  },

  "provenance": {
    "resources": [
      {
        "name": "User-provided coaching data",
        "license": "project-local",
        "type": "dictionary/grammar"
      }
    ],
    "commercialReady": true,
    "flags": []
  },

  "coaching": {
    "dir": "coaching"
  }
}
```

### Field Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✅ | Unique method identifier (kebab-case) |
| `type` | string | ✅ | Rosetta method type to use. One of: `llm`, `llm-coached`, `script-converter` |
| `version` | string | ✅ | Semver version of this method export |
| `description` | string | ✅ | Human-readable description |
| `author` | string | ✅ | Who developed/tested this method |
| `config.model` | string | ✅ | OpenRouter model identifier |
| `config.register` | string | ✅ | Target language register/tone |
| `config.batchSize` | number | — | Keys per API batch (default: 30) |
| `config.temperature` | number | — | LLM temperature (default: 0.3) |
| `locales` | string[] | ✅ | Which locale codes this method targets |
| `benchmarks` | object | ✅ | Per-locale benchmark results (see below) |
| `provenance` | object | ✅ | Licensing and resource dependencies |
| `coaching.dir` | string | — | Relative path to coaching data directory |

### Benchmark Object (per locale)

| Field | Type | Required | Description |
|---|---|---|---|
| `date` | string | ✅ | ISO 8601 timestamp of the benchmark run |
| `corpus_size` | number | ✅ | Number of entries evaluated |
| `exact_match_rate` | number | ✅ | 0.0–1.0, proportion of exact matches |
| `corpus_chrf` | number | — | chrF++ score (0–100) |
| `corpus_bleu` | number | — | BLEU score (0–100) |
| `model` | string | ✅ | Model used during eval |
| `harness_version` | string | ✅ | Version of gds-mt-eval-harness used |

---

## Coaching Data Format

If `type` is `llm-coached`, the plugin should include coaching data files in the `coaching/` subdirectory (or wherever `coaching.dir` points).

### `coaching/<locale>.json`

```json
{
  "grammar_rules": [
    "French adjectives agree in gender and number with the noun they modify",
    "Use 'vous' for formal contexts, 'tu' for informal"
  ],
  "dictionary": {
    "dashboard": "tableau de bord",
    "deployment": "déploiement",
    "settings": "paramètres"
  },
  "style_notes": "Prefer active voice. Avoid anglicisms where a native French term exists. Use inclusive language."
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `grammar_rules` | string[] | — | Rules injected into every LLM prompt for this locale |
| `dictionary` | object | — | Term → translation map. Matched terms are injected as required terminology. |
| `style_notes` | string | — | Freeform style instructions appended to the prompt |

---

## Directory Structure (what the harness exports)

```
french-formal-v1/
  method.json                 # Method manifest with benchmarks
  coaching/
    fr.json                   # Coaching data for French
```

For multi-locale methods:

```
european-formal-v2/
  method.json                 # locales: ["fr", "de", "es", "it"]
  coaching/
    fr.json
    de.json
    es.json
    it.json
```

---

## How Rosetta Consumes This

### Installation

The developer drops the exported directory into `.rosetta/methods/`:

```
my-project/
  .rosetta/
    methods/
      french-formal-v1/
        method.json
        coaching/
          fr.json
    coaching/                 # User's own ad-hoc coaching data (optional)
      crk.json
  locales/
    en.json
    fr.json
```

### Config

In `i18n-rosetta.config.json`, the developer references the method by name:

```json
{
  "pairs": {
    "en→fr": {
      "method": "llm-coached",
      "methodPlugin": "french-formal-v1"
    }
  }
}
```

### Runtime

1. Rosetta reads `method.json` from `.rosetta/methods/french-formal-v1/`
2. Loads coaching data from the plugin's `coaching/` directory
3. Uses the `config` block for model/register/temperature
4. The `benchmarks` block is displayed in `rosetta status` output
5. The `provenance` block is displayed in `rosetta provenance` output

---

## Quality Tiers (for reference)

The harness team should understand how rosetta classifies methods:

| Tier | Method Type | Description |
|---|---|---|
| `standard` | `llm` | Direct LLM prompting, no post-processing |
| `high` | `llm-coached` | LLM + grammar/dictionary coaching |
| `research` | `fst-gated` | LLM + deterministic morphological gate |
| `verified` | `human-review` | LLM draft flagged for human review |

The `type` field in `method.json` determines which tier is applied automatically.

---

## What NOT to Include

- ❌ No Python code or harness dependencies
- ❌ No raw corpus data or run logs
- ❌ No API keys or credentials
- ❌ No harness configuration
- ❌ No internal prompt templates (those live in rosetta's method implementations)

The plugin is **data only**: configuration, coaching content, and benchmark results.
