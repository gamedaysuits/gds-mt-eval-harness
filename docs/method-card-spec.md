# Method Card Specification

A **method card** describes a translation method for the leaderboard without
revealing proprietary implementation details. It answers *"what is this
method?"* — not *"what is the exact prompt?"*

## Relationship to Run Cards

```
Run Card (produced by the harness)
├── config          ← Harness-native: model, temperature, batch_size, ...
├── scores          ← Computed metrics: chrF++, exact match, BLEU, ...
├── method_card     ← Author-provided: this spec (optional)
├── fingerprint     ← Deterministic hash of config + process
└── entries         ← Per-entry results
```

The **run card** is the complete record of a single evaluation run.
The **method card** is an optional, run-independent description of the
approach used. When provided via `--method-card`, it is embedded in the
run card and displayed on the leaderboard.

When no method card is provided, the leaderboard shows harness-native
config fields (model, condition, temperature, tools) — these are always
published automatically.

## Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["method_id", "name", "class"],
  "properties": {
    "method_id": {
      "type": "string",
      "pattern": "^[a-z0-9][a-z0-9-]*$",
      "description": "Unique identifier in kebab-case (e.g., 'coached-crk-v6')"
    },
    "name": {
      "type": "string",
      "description": "Human-readable display name (e.g., 'FST-Gated Coached Translation')"
    },
    "class": {
      "type": "string",
      "enum": ["raw-llm", "coached-llm", "pipeline", "custom-plugin", "api", "human"],
      "description": "Broad category of the translation method"
    },
    "description": {
      "type": "string",
      "description": "1-3 sentence summary of how the method works"
    },
    "author": {
      "type": "string",
      "description": "Person or organization that created the method"
    },
    "tools_used": {
      "type": "array",
      "items": {"type": "string"},
      "description": "External tools or resources used (e.g., 'FST morphological analyzer', 'dictionary lookup')"
    },
    "open_source": {
      "type": "boolean",
      "default": false,
      "description": "Whether the full implementation is publicly available"
    },
    "prompt_published": {
      "type": "boolean",
      "default": false,
      "description": "Whether the system prompt is published"
    },
    "repo_url": {
      "type": "string",
      "format": "uri",
      "description": "URL to the method's source code (if open source)"
    },
    "supported_pairs": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Language pairs this method supports (e.g., ['eng>crk', 'eng>oji'])"
    }
  }
}
```

## Class Descriptions

| Class | Description | Example |
|-------|-------------|---------|
| `raw-llm` | Direct LLM call with minimal instruction | "Translate to Cree" prompt |
| `coached-llm` | LLM with structured prompt, examples, constraints | Few-shot with grammar rules |
| `pipeline` | Multi-stage pipeline with deterministic components | Decompose → translate → FST validate |
| `custom-plugin` | External process implementing `TranslationProcess` | User's custom translation system |
| `api` | Third-party translation API | Google Translate, DeepL |
| `human` | Human translation (for establishing baselines) | Expert linguist translation |

## Usage

### Providing a method card

Create a JSON file matching the schema above:

```json
{
  "method_id": "fst-gated-v8",
  "name": "FST-Gated Coached Translation v8",
  "class": "pipeline",
  "description": "LLM translation with morphological validation. Failed words are retried with FST feedback until all output is morphologically valid.",
  "author": "Curtis Forbes",
  "tools_used": ["HFST morphological analyzer", "Wolvengrey dictionary"],
  "open_source": false,
  "prompt_published": false,
  "supported_pairs": ["eng>crk"]
}
```

### Attaching to a run

```bash
# Via the eval harness CLI
mt-eval run --corpus data/corpus.json --method-card method_card.json

# Via baseline_experiment.py
python eval/baseline_experiment.py --method-card method_card.json
```

### What appears on the leaderboard

When a method card is attached to a submitted run:

- **Class badge** — visual indicator (e.g., "pipeline", "coached-llm")
- **Method name** — from `name` field
- **Description** — from `description` field
- **Tools** — listed from `tools_used`
- **Open source indicator** — icon/badge

When NO method card is attached:

- **Class** — inferred as "raw-llm" or "coached-llm" based on condition
- **Method name** — auto-generated from `model_slug + condition`
- **Config details** — model, temperature, batch size, tools enabled

## Validation Rules

1. `method_id` must be kebab-case, alphanumeric + hyphens only
2. `name` is required and non-empty
3. `class` must be one of the enum values
4. All other fields are optional
5. The method card does NOT affect the run card hash (it's metadata, not config)
