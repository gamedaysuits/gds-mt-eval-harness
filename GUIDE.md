# GDS MT Eval Harness — Researcher's Guide

## TL;DR (Non-Technical Quick Start)

**What is this?** A tool that tests how well a machine translation system works. You give it sentence pairs (source + correct translation), it runs your translation method, and tells you how accurate it is.

**What do I need?**
1. An OpenRouter API key (free to sign up, pay-per-use)
2. A JSON file with your test sentences
3. Python 3.11+

**How fast can I get results?**

```bash
pip install git+https://github.com/gamedaysuits/mt-eval-harness.git
export OPENROUTER_API_KEY=sk-or-v1-your-key-here

mt-eval run \
  --corpus my_sentences.json \
  --source-field english \
  --target-field french \
  --model gemini-3.1-pro

mt-eval test logs/run_*.json
mt-eval dashboard logs/*_report.json -o results.html
```

Open `results.html` in your browser. Done. You have exact match rates, chrF++ scores, per-segment breakdowns, and a searchable entry explorer.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Installation](#2-installation)
3. [Corpus Format](#3-corpus-format)
4. [Configuration Reference](#4-configuration-reference)
5. [CLI Reference](#5-cli-reference)
6. [Workflow Examples](#6-workflow-examples)
7. [Plugin Development](#7-plugin-development)
8. [Dashboard](#8-dashboard)
9. [Caching Strategy](#9-caching-strategy)
10. [Cost Management](#10-cost-management)
11. [Integration Guide](#11-integration-guide)
12. [Champollion Plugin Export](#12-champollion-plugin-export)
13. [Troubleshooting](#13-troubleshooting)
14. [Contests & Leaderboards](#14-contests--leaderboards)
15. [Writing Style Benchmarking](#15-writing-style-benchmarking)
16. [How to Set a Baseline](#16-how-to-set-a-baseline)

---

## 1. Architecture Overview

The harness has two independent components connected by a JSON file:

```
                    RunLog.json
                   ┌──────────┐
 ┌──────────────┐  │          │  ┌──────────────┐  ┌──────────────┐
 │  Run Harness │─▶│  Results │─▶│ Test Harness │─▶│  Dashboard   │
 │  (runner.py) │  │  + Config│  │ (tester.py)  │  │  (HTML)      │
 └──────────────┘  │  + Usage │  └──────────────┘  └──────────────┘
       │           └──────────┘         │
       │                                │
       ▼                                ▼
   Translation                     Metric Computation
   (LLM / plugin)                (exact, chrF++, BLEU, COMET,
                                  bootstrap CIs, plugins)
```

**Run Harness** — Translates entries. Handles model selection, prompting, batching, caching, concurrency, tool-calling, and post-translation hooks. Outputs a `RunLog.json`.

**Test Harness** — Analyzes a RunLog offline. Computes built-in metrics (exact match, chrF++, BLEU, COMET) plus bootstrap 95% confidence intervals on all corpus-level metrics. Also runs any registered MetricPlugin. Outputs a `TestReport.json`.

**Dashboard** — Generates a self-contained HTML file from one or more TestReports. Zero external dependencies — just open in a browser.

**Compare** — Side-by-side comparison of multiple TestReports showing regressions and improvements per entry.

### Plugin Architecture

Language-specific logic is injected via four protocol interfaces:

| Protocol | When Called | Purpose |
|---|---|---|
| `PromptProvider` | Before translation | Supply language-specific system prompts |
| `ToolProvider` | During translation | Provide tools for LLM tool-calling |
| `PostTranslationHook` | After each translation | Corrective loops, validation, enrichment |
| `MetricPlugin` | During test analysis | Custom evaluation metrics |

All four are optional. The harness works out of the box with built-in defaults.

---

## 2. Installation

### From Git (recommended)

```bash
pip install git+https://github.com/gamedaysuits/mt-eval-harness.git
```

### With metrics support (chrF++, BLEU)

```bash
pip install "mt-eval-harness[metrics] @ git+https://github.com/gamedaysuits/mt-eval-harness.git"
```

### For development

```bash
git clone https://github.com/gamedaysuits/mt-eval-harness.git
cd mt-eval-harness
pip install -e ".[all]"
```

### Environment Setup

```bash
cp .env.example .env
# Edit .env and set your OPENROUTER_API_KEY
```

Or export directly:

```bash
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Requirements

- Python 3.11+
- `aiohttp` (installed automatically)
- `python-dotenv` (installed automatically)
- `sacrebleu` (installed automatically — provides chrF++/BLEU)

### Optional: COMET neural metric

COMET provides the best correlation with human quality judgments (WMT 2022 primary metric). It requires PyTorch and a ~2.3 GB model download:

```bash
pip install mt-eval-harness[comet]
```

When installed, COMET scores are automatically computed during `mt-eval test`. No flag required. The model downloads on first use.

> **Low-resource languages:** COMET uses XLM-R embeddings trained on ~100 languages. For languages like Plains Cree (crk) that are underrepresented in XLM-R training data, COMET scores are still computed but the harness emits a warning that scores should be interpreted as relative ranking signals, not absolute quality measures.

---

## 3. Corpus Format

The harness supports four corpus formats, auto-detected by file extension.

### Format 1: Harness JSON (`.json`) — Default

A JSON array of objects. The only **required** field is `id` (integer). All other fields are configurable.

#### Minimal corpus

```json
[
  {"id": 0, "source": "Hello.", "target": "Bonjour."},
  {"id": 1, "source": "Thank you.", "target": "Merci."}
]
```

#### Full-featured corpus (wrapped format)

```json
{
  "dataset": {
    "id": "edtekla-dev-v1",
    "name": "EDTeKLA Development Set",
    "language_pair": { "source": "en", "target": "crk", "target_name": "Plains Cree" }
  },
  "entries": [
    {
      "id": 0,
      "source": "I see a dog.",
      "reference": "niwâpahtên atim.",
      "segment": "gold_standard",
      "difficulty": 1
    }
  ]
}
```

> **Note:** Use `--source-field` and `--target-field` to tell the harness which JSON keys contain your source text and reference translations (e.g., `--source-field english --target-field french`).

### Format 2: JSONL (`.jsonl`) — HuggingFace style

One JSON object per line. Common in HuggingFace datasets and NLP pipelines.

```jsonl
{"source": "Hello.", "reference": "Bonjour."}
{"source": "Thank you.", "reference": "Merci."}
```

```bash
mt-eval run --corpus data/french_eval.jsonl --target-lang French
```

### Format 3: TSV (`.tsv` / `.tab`) — Tab-separated

Tab-separated columns. If the first row contains `source` and `reference` (case-insensitive), it's treated as a header.

```tsv
source	reference
Hello.	Bonjour.
Thank you.	Merci.
```

Without headers, column 0 = source, column 1 = reference:

```tsv
Hello.	Bonjour.
Thank you.	Merci.
```

```bash
mt-eval run --corpus data/french_eval.tsv --target-lang French
```

### Format 4: Parallel Text — FLORES+, WMT, NTREX

Two aligned text files (one sentence per line). This is the standard format for most MT evaluation corpora.

```bash
# Source file (eng_Latn.dev)
Hello.
Thank you.

# Reference file (fra_Latn.dev)
Bonjour.
Merci.
```

Both files must have identical line counts. Use `--source-file` and `--reference-file`:

```bash
mt-eval run \
  --source-file flores200/dev/eng_Latn.dev \
  --reference-file flores200/dev/fra_Latn.dev \
  --target-lang French
```

### Auto-ID assignment

All formats get sequential 0-indexed `id` fields if not already present. This is required for result tracking, caching, and the entry explorer.

### Optional fields used by the harness

| Field | Type | Purpose |
|---|---|---|
| `segment` | string | Groups entries for per-segment metric breakdown |
| `difficulty` | int | Groups entries for per-difficulty breakdown |

Any additional fields are preserved in the RunLog and accessible to plugins.

---

## 4. Configuration Reference

Every parameter that affects a run is captured in `RunConfig`. The full config is serialized into every RunLog for reproducibility.

### Dataset Selection

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `dataset` | `--dataset`, `-d` | `"all"` | Which entries to use. Options: `"all"`, a segment name, an ID range (`"0-61"`), or a single ID |
| `entry_ids` | `--ids` | `None` | Comma-separated entry IDs (overrides dataset) |

### Corpus

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `corpus_path` | `--corpus` | `None` | Path to corpus file (`.json`, `.jsonl`, or `.tsv`) |
| `source_file` | `--source-file` | `None` | Path to source text file (parallel text mode) |
| `reference_file` | `--reference-file` | `None` | Path to reference text file (parallel text mode) |
| `source_field` | `--source-field` | `"source"` | Field name for source text |
| `target_field` | `--target-field` | `"target"` | Field name for reference translation |

> **Note:** Use either `--corpus` (single file: JSON/JSONL/TSV) or `--source-file` + `--reference-file` (parallel text). Not both.

### Model

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `model` | `--model`, `-m` | `"gemini-3.1-pro"` | Model short name, full OpenRouter ID, or comma-separated list for parallel multi-model runs |
| `max_tokens` | `--max-tokens` | `32768` | Max tokens per API call. Set high to eliminate truncation risk; unused tokens cost nothing |
| `temperature` | `--temperature` | `0.0` | Sampling temperature (0 = deterministic) |

### Execution

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `batch_size` | `--batch-size`, `-b` | `25` | Entries per API call. 25× fewer calls. Auto-overrides to 1 when tools enabled |
| `concurrency` | `--concurrency`, `-c` | `8` | Parallel API calls per model. For multi-model parallelism, use `execute_multi_run()` |
| `cache_enabled` | `--no-cache` | `True` | Enable/disable result caching. Almost never disable this |
| `cache_dir` | `--cache-dir` | `"eval/cache/harness"` | Cache directory path |

> **⚠️ These defaults are intentionally aggressive.**
> All defaults are defined as `HARNESS_DEFAULTS` constants in `config.py`.
> Change them in ONE place. Do NOT lower them without a specific reason.

### Tool-Calling

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `tools_enabled` | `--tools` | `False` | Enable tool-calling mode |
| `tools_list` | `--tools-list` | `None` | Comma-separated tool names (None = all) |
| `max_tool_rounds` | `--max-tool-rounds` | `8` | Max tool-call rounds per entry |

### Prompts

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `prompt_version` | `--prompt`, `-p` | `"naive"` | Prompt version. Built-in: `naive`, `custom`, `champollion` |
| `custom_prompt_path` | `--custom-prompt` | `None` | Path to .txt file (with `--prompt custom`) |

### Champollion Config Interop

These flags enable config interchangeability with the production `champollion` CLI. When `--champollion-config` is provided, the harness reads your `champollion.config.json` and builds production-identical prompts with the correct register, gender guidance, and prompt context.

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `champollion_config_path` | `--champollion-config` | `None` | Path to `champollion.config.json` |
| `champollion_cards_dir` | `--champollion-cards-dir` | auto-detect | Path to language-cards directory |
| `target_lang_code` | `--target-lang-code` | `""` | BCP-47 code for target language (e.g., `"fr"`, `"crk"`) |

> **Auto-set behavior:** When `--champollion-config` is provided without an explicit `--prompt`, the prompt version automatically sets to `champollion`. The target language name is auto-populated from the language card.

### Post-Translation Hooks

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `post_hooks` | `--hooks` | `[]` | Comma-separated hook names to apply |

### Output

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `output_dir` | `--output-dir`, `-o` | `"eval/logs/harness"` | Output directory |
| `run_name` | `--name`, `-n` | `None` | Human-readable label for the run |
| `dry_run` | `--dry-run` | `False` | Validate config without API calls |

---

## 5. CLI Reference

### `mt-eval run`

Execute a translation run. Defaults are optimized for throughput — see Section 4 for the full config table.

```bash
# Basic (optimal defaults: batch=25, tokens=32k, cache=on)
mt-eval run --corpus data/corpus.json

# Multi-model parallel run (recommended for benchmarks)
mt-eval run --corpus data/corpus.json \
  -m gemini-3.1-pro,claude-opus-4.7,gpt-5.5

# Parallel text corpus (FLORES+, WMT, NTREX)
mt-eval run \
  --source-file flores200/dev/eng_Latn.dev \
  --reference-file flores200/dev/fra_Latn.dev \
  --target-lang French

# JSONL or TSV corpus
mt-eval run --corpus data/eval.jsonl --target-lang French
mt-eval run --corpus data/eval.tsv --target-lang French

# With champollion config (production-identical prompts)
mt-eval run --corpus data/corpus.json \
  --champollion-config champollion.config.json \
  --target-lang-code fr

# With target language (critical for low-resource languages)
mt-eval run --corpus data/corpus.json \
  --target-lang "Plains Cree (nêhiyawêwin, SRO)"

# Tool-calling mode (batch_size auto-overrides to 1)
mt-eval run --corpus data/corpus.json --tools

# Dry run (validate config, no API calls)
mt-eval run --corpus data/corpus.json --dry-run
```

Key flags:

| Flag | Default | Notes |
|---|---|---|
| `-m, --model` | `gemini-3.1-pro` | Comma-separated for parallel multi-model |
| `--corpus` | — | `.json`, `.jsonl`, or `.tsv` |
| `--source-file` / `--reference-file` | — | Parallel text files (alternative to --corpus) |
| `--champollion-config` | — | Path to `champollion.config.json` (auto-sets `--prompt champollion`) |
| `--target-lang-code` | `""` | BCP-47 code, required with `--champollion-config` |
| `-b, --batch-size` | `25` | Auto-overrides to 1 with `--tools` |
| `--max-tokens` | `32768` | Generous headroom, no truncation |
| `-c, --concurrency` | `8` | Per-model parallel batches |
| `--no-cache` | off | Almost never use this |
| `--target-lang` | `""` | Set this for non-obvious target languages |

### `mt-eval test`

Analyze a completed RunLog. Computes exact match, chrF++, BLEU, COMET (if installed), and bootstrap 95% confidence intervals.

```bash
# Basic
mt-eval test path/to/run_log.json [-o output.json]

# Skip confidence interval computation (faster)
mt-eval test path/to/run_log.json --no-ci

# Custom bootstrap iterations (default: 1000)
mt-eval test path/to/run_log.json --n-bootstrap-ci 2000
```

| Flag | Default | Notes |
|---|---|---|
| `--no-ci` | off | Skip bootstrap CI computation (saves ~1-2s) |
| `--n-bootstrap-ci` | `1000` | Bootstrap iterations. Matches SacreBLEU/WMT convention |

Example output with CIs:

```
============================================================
TEST REPORT SUMMARY
============================================================

  Total entries:    404
  Errors:           0
  Evaluated:        404

  Exact match:      78/404 (19.3%)
  Miss:             326/404 (80.7%)

  Corpus chrF++:    42.96  [40.1 – 45.8]
  Corpus BLEU:      11.30  [9.2 – 13.4]
  COMET:            0.7234
  Exact match CI:   [14.5 – 24.2%]

  Total cost:       $0.0312
  Avg latency:      1.2s
============================================================
```

### `mt-eval compare`

Compare multiple TestReports side by side.

```bash
mt-eval compare report1.json report2.json [-o comparison.json]
```

### `mt-eval dashboard`

Generate an interactive HTML dashboard.

```bash
mt-eval dashboard report1.json report2.json -o dashboard.html
```

### `mt-eval list`

List available resources.

```bash
mt-eval list models          # Show registry shortcuts
mt-eval list models --live   # Fetch live catalog from OpenRouter
mt-eval list prompts         # Show available prompt versions
mt-eval list datasets        # Show registered evaluation datasets
```

---

## 6. Workflow Examples

### Basic: Test a model on your data

```bash
# 1. Run translation
mt-eval run \
  --corpus data/test_set.json \
  --source-field source \
  --target-field reference \
  --model gemini-3.1-pro \
  --prompt naive

# 2. Analyze
mt-eval test eval/logs/harness/run_*.json

# 3. Dashboard
mt-eval dashboard eval/logs/harness/*_report.json -o report.html
```

### Model comparison: Gemini vs Claude vs GPT

Use comma-separated models for parallel execution (recommended):

```bash
# All three models run simultaneously — wall-clock = slowest single model
mt-eval run \
  --corpus data/test_set.json \
  -m gemini-3.1-pro,claude-sonnet-4,gpt-5.5 \
  --name "model_comparison"

# Analyze all
for f in eval/logs/harness/run_*.json; do
  mt-eval test "$f"
done

# Compare
mt-eval dashboard eval/logs/harness/*_report.json -o comparison.html
```

### Batching: The default is already optimal

Batch size defaults to 25 (entries per API call). This is 25× cheaper than `batch_size=1` with negligible accuracy difference across all tested frontier models.

```bash
# Override to 1 only if you need per-entry isolation for debugging
mt-eval run \
  --corpus data/test_set.json \
  --batch-size 1 \
  --name "single_entry_debug"
```

### Custom prompt: Load from file

```bash
echo "You are an expert French translator..." > my_prompt.txt

mt-eval run \
  --corpus data/test_set.json \
  --prompt custom \
  --custom-prompt my_prompt.txt
```

---

## 7. Plugin Development

### MetricPlugin — Custom evaluation metrics

```python
from mt_eval_harness.plugins.metrics import MetricPlugin

class WordCountMetric:
    """Count words in predicted vs reference."""
    name = "word_count"

    def compute(self, entry: dict) -> dict:
        pred_words = len(entry["predicted"].split())
        ref_words = len(entry["expected"].split())
        return {
            "pred_word_count": pred_words,
            "ref_word_count": ref_words,
            "word_count_diff": pred_words - ref_words,
        }

    def aggregate(self, entry_results: list[dict]) -> dict:
        diffs = [r["word_count_diff"] for r in entry_results if "error" not in r]
        return {
            "avg_word_count_diff": sum(diffs) / max(len(diffs), 1),
        }

# Usage:
from mt_eval_harness.tester import analyze_run
report = analyze_run("run_log.json", metric_plugins=[WordCountMetric()])
```

> [!NOTE]
> The `entry` dict passed to `compute()` contains a `raw_predicted` key (the raw LLM response before any post-translation hooks ran) alongside `predicted` (the final output after hooks). This enables double-pass compliance plugins (like the built-in `DoublePassCompliancePlugin` which is automatically loaded when a language card with rules is detected) to calculate the corrective/repair impact of post-processing pipeline steps.

### PromptProvider — Language-specific prompts

```python
from mt_eval_harness.plugins.prompts import PromptProvider

class FrenchPrompts:
    def list_versions(self) -> list[str]:
        return ["fr_basic", "fr_formal"]

    def load(self, version, config):
        if version == "fr_basic":
            return "Translate English to French. Output only the translation."
        elif version == "fr_formal":
            return "You are a professional French translator. Use formal register..."

# Usage:
from mt_eval_harness.runner import execute_run
await execute_run(config, prompt_providers=[FrenchPrompts()])
```

### Built-in: ChampollionPromptProvider

The harness ships with a built-in `ChampollionPromptProvider` that reads your `champollion.config.json` and builds production-identical system prompts. This enables config interchangeability — one config file works in both tools.

```bash
# CLI: auto-registered when --champollion-config is provided
mt-eval run --corpus data.json \
  --champollion-config champollion.config.json \
  --target-lang-code fr
```

```python
# Programmatic: register explicitly
from mt_eval_harness.plugins.champollion_prompts import ChampollionPromptProvider
from mt_eval_harness.config import RunConfig

config = RunConfig(
    corpus_path="data/corpus.json",
    champollion_config_path="champollion.config.json",
    target_lang_code="fr",
    prompt_version="champollion",
)
await execute_run(config, prompt_providers=[ChampollionPromptProvider()])
```

The provider reads the language card JSON files directly (no Node.js dependency) and resolves:
- **Register preset** — from `languages.{code}` in the config, or the card's default
- **Gender guidance** — from the language card's `gender.inclusiveGuidance`
- **Prompt context** — from the config's top-level `promptContext`

The output is character-for-character identical to production `buildSystemMessage()` in `lib/methods/llm.js`.

### PostTranslationHook — Corrective loops

```python
from mt_eval_harness.plugins.hooks import PostTranslationHook

class SpellCheckHook:
    name = "spell_check"

    async def process(self, entry, result, config, api_fn=None):
        predicted = result["predicted"]
        # Run your spell checker
        corrected = my_spell_checker(predicted)
        result["predicted"] = corrected
        result["metadata"]["spell_corrections"] = corrected != predicted
        return result

# Usage:
config.post_hooks = ["spell_check"]
await execute_run(config, post_hooks=[SpellCheckHook()])
```

### ToolProvider — LLM tool-calling

```python
from mt_eval_harness.plugins.tools import ToolProvider

class DictionaryTools:
    def get_schemas(self, config):
        return [{
            "type": "function",
            "function": {
                "name": "lookup_word",
                "description": "Look up a word in the dictionary",
                "parameters": {
                    "type": "object",
                    "properties": {"word": {"type": "string"}},
                    "required": ["word"],
                },
            },
        }]

    async def execute(self, name, arguments):
        return {"definition": my_dictionary.lookup(arguments["word"])}

    def list_available(self):
        return ["lookup_word"]

# Usage:
config.tools_enabled = True
await execute_run(config, tool_provider=DictionaryTools())
```

---

## 8. Dashboard

The dashboard is a self-contained HTML file. No CDN, no framework, no build step. Open it in any browser, share it by email, commit it to git.

Features:
- Overall metric cards (exact match, chrF++, BLEU, cost)
- Run comparison table (when multiple reports loaded)
- Per-segment breakdown
- Per-difficulty breakdown
- Searchable entry explorer with full drill-down
- Plugin metric display

```bash
mt-eval dashboard report1.json report2.json -o results.html
open results.html
```

---

## 9. Caching Strategy

The harness caches translation results to avoid re-running identical queries.

### How it works

- **Cache key** = `hash(config_hash + source_text)`
- **Config hash** includes: model, prompt, tools, temperature, hooks
- Changing any of these creates a new cache namespace
- Cache files are plain JSON, one per entry — human-inspectable

### Single vs batch caching

| Mode | Cache granularity |
|---|---|
| `batch_size=1` | One cache file per entry |
| `batch_size>1` | One cache file per batch (batch composition matters) |

### Cache invalidation

Change any config parameter that affects translation output and the cache auto-invalidates. To force a fresh run:

```bash
mt-eval run --no-cache ...
```

---

## 10. Cost Management

The harness pulls live pricing from OpenRouter and calculates per-entry and total costs.

### Cost optimization tips

1. **Start small**: Test on 5-10 entries first (`--ids 0,1,2,3,4`)
2. **Use caching**: Cached results cost $0 on re-runs (default: on)
3. **Keep batch_size=25**: Already the default — 25× cheaper than batch_size=1
4. **Use Flash models for iteration**: `--model gemini-3-flash` for prompt development
5. **Reserve Pro models for final benchmarks**: `--model gemini-3.1-pro` for publication
6. **Run models in parallel**: Use comma-separated `-m` for multi-model — same wall-clock time as a single model

### Dry run

Validate your config without any API calls:

```bash
mt-eval run --corpus data.json --dry-run
```

---

## 11. Integration Guide

### Installing in another project

```bash
# In your project's requirements.txt or pyproject.toml:
pip install git+https://github.com/gamedaysuits/mt-eval-harness.git
```

### Programmatic usage — single model

```python
import asyncio
from mt_eval_harness.config import RunConfig
from mt_eval_harness.runner import execute_run
from mt_eval_harness.tester import analyze_run

async def evaluate():
    config = RunConfig(
        corpus_path="data/corpus.json",
        source_field="source",
        target_field="target",
        model="gemini-3.1-pro",
        # Defaults are already optimal:
        # batch_size=25, max_tokens=32768, concurrency=8, cache=on
    )
    run_log = await execute_run(config)

    # Analyze the run
    from pathlib import Path
    log_files = list(Path(config.output_dir).glob("*.json"))
    report = analyze_run(log_files[-1])
    return report

asyncio.run(evaluate())
```

### Programmatic usage — multi-model parallel (recommended for benchmarks)

```python
import asyncio
from mt_eval_harness.config import RunConfig
from mt_eval_harness.runner import execute_multi_run

async def benchmark():
    # Create one config per model — all other settings shared
    models = ["gemini-3.1-pro", "claude-opus-4.7", "gpt-5.5", "deepseek-v4-pro"]
    configs = [
        RunConfig(
            corpus_path="data/corpus.json",
            model=m,
            target_lang="Plains Cree (nêhiyawêwin, SRO)",
        )
        for m in models
    ]

    # All models run in parallel — wall-clock = slowest single model
    results = await execute_multi_run(configs)
    return results

asyncio.run(benchmark())
```

### Wrapping an existing pipeline

Implement the `TranslationProcess` protocol:

```python
class MyPipeline:
    async def translate(self, entries, config):
        results = []
        for entry in entries:
            # Your translation logic here
            translation = await my_translate(entry[config.source_field])
            results.append({
                "id": entry["id"],
                "predicted": translation,
                "latency_s": 0.5,
                "usage": {},
                "error": None,
                "tool_calls": [],
                "tool_call_count": 0,
                "metadata": {},
            })
        return results

# Evaluate it:
await execute_run(config, process=MyPipeline())
```

---

## 12. Champollion Plugin Export

The harness can package a completed evaluation as a **method plugin** for
[champollion](https://github.com/gamedaysuits/champollion). This bridges
the gap between research (harness) and production (champollion).

### What gets exported

The export produces a directory with this structure:

```
<plugin-name>/
  method.json             # Manifest: name, type, config, benchmarks, provenance
  coaching/
    <locale>.json          # Optional: grammar rules, dictionary, style notes
```

This is strictly **data-only output**. The export NEVER includes:
- Python source code
- API keys or environment variables
- Harness configuration (prompts, tools, hooks)
- RunLog entries or raw translations

### CLI usage

```bash
# 1. Run your translation experiment
mt-eval run --corpus data/corpus.json --model gemini-3.1-pro

# 2. Analyze the results
mt-eval test eval/logs/harness/run_*.json

# 3. Export as a champollion plugin
mt-eval export \
  --report eval/logs/harness/run_*_report.json \
  --name crk-coached-v1 \
  --type llm-coached \
  --locales crk \
  --description "Plains Cree with grammar coaching and FST validation" \
  --register "Standard written register (SRO)" \
  --coaching-dir .champollion/coaching \
  --output-dir ./exported_plugins
```

### Programmatic usage

```python
from mt_eval_harness import ExportConfig, export_plugin

config = ExportConfig(
    name="crk-coached-v1",
    method_type="llm-coached",
    locales=["crk"],
    description="Plains Cree with grammar coaching",
    coaching_dir=".champollion/coaching",
    output_dir="./exported_plugins",
)

plugin_dir = export_plugin("eval/logs/harness/my_report.json", config)
```

### Installing the plugin in champollion

Copy the exported directory into your champollion project:

```bash
cp -r ./exported_plugins/crk-coached-v1 <project>/.champollion/methods/
```

Then reference it in `champollion.config.json`:

```json
{
  "pairs": {
    "en→crk": {
      "methodPlugin": "crk-coached-v1"
    }
  }
}
```

### Provenance and licensing

Exported plugins default to `commercialReady: false` with a `"license-unclear"`
flag. Plugins can bundle coaching data, FST gate configs, decomposition
pipelines, and other resources whose licensing status the exporter cannot
determine automatically.

When a method's licensing has been verified and it's ready for distribution
(published to an API endpoint or as a remotely installable plugin), set the
flag explicitly:

```bash
mt-eval export ... --commercial-ready
```

This clears the `"license-unclear"` flag and marks the plugin as ready
to publish.

### Benchmarks

The export includes ALL metrics from the TestReport in the benchmarks block:
- Standard: `exact_match_rate`, `corpus_chrf`, `corpus_bleu`
- Neural: `comet_score` (if `unbabel-comet` was installed during evaluation)
- Statistical: `confidence_intervals` (bootstrap 95% CIs for all corpus metrics)
- Plugin-specific: any custom metrics from harness plugins (e.g., FST validity)

Champollion ignores unknown metric fields, so this is strictly additive.

---

## 13. Troubleshooting

### "OPENROUTER_API_KEY not found"

```bash
export OPENROUTER_API_KEY=sk-or-v1-your-key
# Or create a .env file in your working directory
```

### "Corpus not found"

The `--corpus` flag requires a path to a `.json`, `.jsonl`, or `.tsv` file. For parallel text files, use `--source-file` and `--reference-file` instead.

### "sacrebleu not installed"

chrF++ and BLEU scores require sacrebleu (installed as a core dependency):

```bash
pip install sacrebleu>=2.3
```

### COMET not computing scores

COMET requires an optional heavy dependency (PyTorch + ~2.3 GB model):

```bash
pip install mt-eval-harness[comet]
```

If COMET is not installed, the harness prints `COMET: Not installed (pip install unbabel-comet)` and continues without it. COMET scores will be `null` in the TestReport.

### Rate limiting (429 errors)

The harness automatically retries with exponential backoff. If you're still hitting limits:
- Reduce `--concurrency` (try 2-4)
- Add a delay between batches

### Cache not working

- Check that `--no-cache` isn't set
- Verify the cache directory is writable
- Changing ANY config parameter that affects output creates a new cache namespace

### "Unknown model"

Either use a short name from `mt-eval list models` or pass the full OpenRouter model ID:

```bash
mt-eval run --model anthropic/claude-sonnet-4 ...
```

---

## 14. Contests & Leaderboards

The Arena supports structured evaluation contests — open bounties or private benchmarks where participants submit translation methods and are ranked against a withheld evaluation set.

### Creating a Contest

```bash
# Public contest — anyone can submit
mt-eval contest create \
  --name "EN→CRK Open Challenge" \
  --corpus edtekla-v1.json \
  --visibility public \
  --primary-metric chrf \
  --deadline 2026-09-30

# Private contest — invite-only, blind evaluation
mt-eval contest create \
  --name "Q3 DE Compliance" \
  --corpus de_compliance_500.json \
  --visibility private \
  --teams "berlin,vienna,zurich,munich"

# Team contest — scoped to an organization
mt-eval contest create \
  --name "ACME Localization Shootout" \
  --corpus acme_test_set.json \
  --visibility team \
  --org acme-corp
```

### Visibility Modes

| Mode | Who Can Submit | Who Sees Scores | Use Case |
|---|---|---|---|
| `public` | Anyone | Everyone | Open research challenges, crowdsourced MT |
| `private` | Invited teams only | Only contest creator (until closed) | Internal benchmarking, blind evaluation |
| `team` | Org members only | Org members | Company-wide translation method comparison |

### How Submissions Are Verified

Every submission generates a **cryptographic run card** — a tamper-proof record of:
- Exact model configuration used
- Prompt text (hashed)
- Corpus version and entry IDs
- Timestamp and API call logs

The withheld evaluation set is never exposed to participants. Submissions are evaluated server-side against the withheld split. If the submission's output distribution matches a known reference set (e.g., someone submitted the test answers), the integrity check fails and the submission is rejected.

### Leaderboard Mechanics

- **Primary metric**: Configurable per contest. Default: chrF++
- **Tiebreakers**: BLEU → COMET → submission timestamp (earlier wins)
- **Rejected submissions**: Shown with strikethrough and a red ✕ (public shaming is intentional — it deters cheating)

### Prize Distribution

Prizes are set by the contest creator and held in escrow (or simply stated as bounties for community contests). When the contest closes:
1. All submissions are re-evaluated against the full withheld set
2. Final rankings are published
3. Prize is awarded to the top-ranked verified submission

### CLI Reference

```bash
mt-eval contest create   # Create a new contest
mt-eval contest list     # List active contests
mt-eval contest submit   # Submit a run to a contest
mt-eval contest close    # Close a contest and finalize rankings
mt-eval contest export   # Export contest results as JSON
```

---

## 15. Writing Style Benchmarking

The harness isn't just for low-resource languages — it's for anyone who cares about translation quality enough to measure it. A common use case: finding which model best matches your brand's translation voice.

### Custom Prompt for Brand Voice

Create a prompt file that encodes your brand's translation style:

```text
# brand_voice.txt
You are translating marketing copy for a design agency. The tone is:
- Casual and playful, never corporate
- Short, punchy sentences
- Contractions are encouraged (don't, won't, it's)
- Avoid formal register (no "kindly", "please be advised", "we would like to inform you")
- Match the energy of the source — if it's excited, be excited
```

### Style Alignment Metric Plugin

Build a custom MetricPlugin that scores how well each translation matches your brand voice:

```python
from mt_eval_harness.plugins.metrics import MetricPlugin

class BrandAlignmentMetric:
    """Score translations against a brand style guide."""
    name = "brand_alignment"

    def __init__(self, style_rules: list[str]):
        self.rules = style_rules

    def compute(self, entry: dict) -> dict:
        predicted = entry["predicted"]
        score = 0
        checks = {}
        # Example: check for casual contractions
        if any(c in predicted for c in ["don't", "won't", "it's", "can't"]):
            score += 25
            checks["contractions"] = True
        # Example: penalize formal language
        if any(f in predicted.lower() for f in ["kindly", "please be advised", "we would like"]):
            score -= 30
            checks["formal_detected"] = True
        # ... more rules
        return {"brand_score": score, "checks": checks}

    def aggregate(self, entry_results: list[dict]) -> dict:
        scores = [r["brand_score"] for r in entry_results if "brand_score" in r]
        return {"avg_brand_score": sum(scores) / max(len(scores), 1)}
```

### Model Comparison Workflow

```bash
# Run 5 models in parallel with your brand prompt
mt-eval run --corpus brand_samples.json \
  -m gemini-3.1-pro,claude-sonnet-4,gpt-5.5,mistral-large,deepseek-v4 \
  --custom-prompt brand_voice.txt \
  --name "brand_voice_benchmark"

# Analyze with your custom metric
mt-eval test eval/logs/harness/run_*.json \
  --plugin brand_alignment.py

# Compare results side by side
mt-eval dashboard eval/logs/harness/*_report.json \
  -o brand_comparison.html
```

### Exporting the Winner

Once you've identified the best model + prompt combination:

```bash
# Export as an champollion production config
mt-eval export \
  --run eval/logs/harness/run_mistral_large_*.json \
  --format champollion-config \
  -o champollion.config.json
```

This generates a production-ready champollion config with the winning model, prompt, and all quality gates pre-configured.

---

## 16. How to Set a Baseline

When you select a language pair on the Arena and see "No baseline established," here's how to be the first person to set one.

### Prerequisites

```bash
# Install the harness
pip install mt-eval-harness

# Set your API key (supports OpenRouter — any model)
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### Step 1: Prepare Your Corpus

You need a parallel text corpus — source sentences with reference translations. This can be:

- A JSON file with `source` and `reference` fields
- A pair of aligned text files (one sentence per line)
- A TSV with source/reference columns

```json
[
  {"id": 0, "source": "Hello.", "reference": "Bonjour."},
  {"id": 1, "source": "Thank you.", "reference": "Merci."}
]
```

For indigenous and low-resource languages, community-validated corpora are essential. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on corpus preparation and OCAP principles.

### Step 2: Run a Baseline Experiment

```bash
# Basic baseline with a frontier model
mt-eval run \
  --corpus data/my_corpus.json \
  --target-lang "Target Language Name" \
  --model gemini-3.1-pro \
  --name "baseline-v1"

# With a champollion config for production-identical prompts
mt-eval run \
  --corpus data/my_corpus.json \
  --champollion-config champollion.config.json \
  --target-lang-code tl \
  --name "baseline-champollion-v1"
```

### Step 3: Analyze the Results

```bash
mt-eval test eval/logs/harness/run_baseline-v1_*.json
```

This gives you chrF++, BLEU, exact match rate, and confidence intervals — the baseline that all future submissions will be measured against.

### Step 4: Submit to the Arena

```bash
mt-eval contest submit \
  --contest "EN→TL Open Challenge" \
  --run eval/logs/harness/run_baseline-v1_*.json
```

Your submission is verified against the withheld evaluation set and ranked on the leaderboard. Congratulations — you just established the frontier.

### Step 5: Iterate

Now beat your own baseline:

```bash
# Try multiple models in parallel
mt-eval run --corpus data/my_corpus.json \
  -m gemini-3.1-pro,claude-sonnet-4,gpt-5.5 \
  --target-lang "Target Language Name"

# Compare results
mt-eval dashboard eval/logs/harness/*_report.json -o comparison.html
```

### Agent Workflow

If you're using an AI coding agent, you can direct it to set a baseline with this prompt:

> "Use mt-eval-harness to establish a baseline for EN→[TARGET]. Install it with `pip install mt-eval-harness`, prepare a corpus, and run an initial benchmark with at least 3 models."

The agent will handle installation, corpus preparation, multi-model runs, and result analysis — you just review the dashboard.

---

*Licensed under Apache-2.0. See [LICENSE](LICENSE) for details.*

