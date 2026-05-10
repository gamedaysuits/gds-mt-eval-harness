# GDS MT Eval Harness — Researcher's Guide

## TL;DR (Non-Technical Quick Start)

**What is this?** A tool that tests how well a machine translation system works. You give it sentence pairs (source + correct translation), it runs your translation method, and tells you how accurate it is.

**What do I need?**
1. An OpenRouter API key (free to sign up, pay-per-use)
2. A JSON file with your test sentences
3. Python 3.11+

**How fast can I get results?**

```bash
pip install git+https://github.com/gamedaysuits/gds-mt-eval-harness.git
export OPENROUTER_API_KEY=sk-or-v1-your-key-here

gds-mt-eval run \
  --corpus my_sentences.json \
  --source-field english \
  --target-field french \
  --model gemini-3.1-pro

gds-mt-eval test logs/run_*.json
gds-mt-eval dashboard logs/*_report.json -o results.html
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
12. [Troubleshooting](#12-troubleshooting)

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
  (LLM / plugin)                (exact, chrF++, BLEU, plugins)
```

**Run Harness** — Translates entries. Handles model selection, prompting, batching, caching, concurrency, tool-calling, and post-translation hooks. Outputs a `RunLog.json`.

**Test Harness** — Analyzes a RunLog offline. Computes built-in metrics (exact match, chrF++, BLEU) plus any registered MetricPlugin results. Outputs a `TestReport.json`.

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
pip install git+https://github.com/gamedaysuits/gds-mt-eval-harness.git
```

### With metrics support (chrF++, BLEU)

```bash
pip install "gds-mt-eval-harness[metrics] @ git+https://github.com/gamedaysuits/gds-mt-eval-harness.git"
```

### For development

```bash
git clone https://github.com/gamedaysuits/gds-mt-eval-harness.git
cd gds-mt-eval-harness
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
- `sacrebleu` (optional, for chrF++/BLEU — installed with `[metrics]`)

---

## 3. Corpus Format

Your corpus is a JSON array of objects. The only **required** field is `id` (integer). All other fields are configurable.

### Minimal corpus

```json
[
  {"id": 0, "english": "Hello.", "french": "Bonjour."},
  {"id": 1, "english": "Thank you.", "french": "Merci."}
]
```

### Full-featured corpus

```json
[
  {
    "id": 0,
    "english": "I see a dog.",
    "cree_sro": "niwâpahtên atim.",
    "segment": "gold_standard",
    "difficulty": 1,
    "source": "Wolvengrey (2001)",
    "notes": "Basic transitive sentence"
  }
]
```

### Field mapping

Use `--source-field` and `--target-field` to tell the harness which columns contain your source text and reference translations:

```bash
# English → French
gds-mt-eval run --corpus data.json --source-field english --target-field french

# Spanish → Quechua
gds-mt-eval run --corpus data.json --source-field spanish --target-field quechua
```

### Optional fields used by the harness

| Field | Type | Purpose |
|---|---|---|
| `segment` | string | Groups entries for per-segment metric breakdown |
| `difficulty` | int | Groups entries for per-difficulty breakdown |

Any additional fields are preserved in the RunLog and accessible to plugins.

### Building a corpus

Structure your entries in a deliberate order:

1. **Gold standard** — Expert-verified reference pairs
2. **Textbook samples** — From pedagogical materials
3. **Phase 1 test** — Initial development test set
4. **Remainder** — Everything else

Keep **50 entries as holdouts** (not in the corpus) for final validation.

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
| `corpus_path` | `--corpus` | `None` | Path to corpus JSON file (required) |
| `source_field` | `--source-field` | `"english"` | Field name for source text |
| `target_field` | `--target-field` | `"cree_sro"` | Field name for reference translation |

### Model

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `model` | `--model`, `-m` | `"gemini-3.1-pro"` | Model short name or full OpenRouter ID |
| `max_tokens` | `--max-tokens` | `13680` | Max tokens per API call |
| `temperature` | `--temperature` | `0.0` | Sampling temperature (0 = deterministic) |

### Execution

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `batch_size` | `--batch-size`, `-b` | `1` | Entries per API call |
| `concurrency` | `--concurrency`, `-c` | `8` | Parallel API calls |
| `cache_enabled` | `--no-cache` | `True` | Enable/disable result caching |
| `cache_dir` | `--cache-dir` | `"eval/cache/harness"` | Cache directory path |

### Tool-Calling

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `tools_enabled` | `--tools` | `False` | Enable tool-calling mode |
| `tools_list` | `--tools-list` | `None` | Comma-separated tool names (None = all) |
| `max_tool_rounds` | `--max-tool-rounds` | `8` | Max tool-call rounds per entry |

### Prompts

| Parameter | CLI Flag | Default | Description |
|---|---|---|---|
| `prompt_version` | `--prompt`, `-p` | `"naive"` | Prompt version. Built-in: `naive`, `custom` |
| `custom_prompt_path` | `--custom-prompt` | `None` | Path to .txt file (with `--prompt custom`) |

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

### `gds-mt-eval run`

Execute a translation run.

```bash
gds-mt-eval run --corpus data/corpus.json [options]
```

### `gds-mt-eval test`

Analyze a completed RunLog.

```bash
gds-mt-eval test path/to/run_log.json [-o output.json]
```

### `gds-mt-eval compare`

Compare multiple TestReports side by side.

```bash
gds-mt-eval compare report1.json report2.json [-o comparison.json]
```

### `gds-mt-eval dashboard`

Generate an interactive HTML dashboard.

```bash
gds-mt-eval dashboard report1.json report2.json -o dashboard.html
```

### `gds-mt-eval list`

List available resources.

```bash
gds-mt-eval list models    # Show available model shortcuts
gds-mt-eval list prompts   # Show available prompt versions
```

---

## 6. Workflow Examples

### Basic: Test a model on your data

```bash
# 1. Run translation
gds-mt-eval run \
  --corpus data/test_set.json \
  --source-field source \
  --target-field reference \
  --model gemini-3.1-pro \
  --prompt naive

# 2. Analyze
gds-mt-eval test eval/logs/harness/run_*.json

# 3. Dashboard
gds-mt-eval dashboard eval/logs/harness/*_report.json -o report.html
```

### Model comparison: Gemini vs Claude vs GPT

```bash
for model in gemini-3.1-pro claude-sonnet-4 gpt-5.5; do
  gds-mt-eval run \
    --corpus data/test_set.json \
    --model $model \
    --name "${model}_comparison"
done

# Analyze all
for f in eval/logs/harness/run_*.json; do
  gds-mt-eval test "$f"
done

# Compare
gds-mt-eval dashboard eval/logs/harness/*_report.json -o comparison.html
```

### Batching: Cost optimization

```bash
# Batch 5 entries per call (cheaper, slightly less accurate)
gds-mt-eval run \
  --corpus data/test_set.json \
  --batch-size 5 \
  --name "batch5"

# Compare against single-entry baseline
gds-mt-eval compare eval/logs/harness/*single*_report.json eval/logs/harness/*batch5*_report.json
```

### Custom prompt: Load from file

```bash
echo "You are an expert French translator..." > my_prompt.txt

gds-mt-eval run \
  --corpus data/test_set.json \
  --prompt custom \
  --custom-prompt my_prompt.txt
```

---

## 7. Plugin Development

### MetricPlugin — Custom evaluation metrics

```python
from gds_mt_eval_harness.plugins.metrics import MetricPlugin

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
from gds_mt_eval_harness.tester import analyze_run
report = analyze_run("run_log.json", metric_plugins=[WordCountMetric()])
```

### PromptProvider — Language-specific prompts

```python
from gds_mt_eval_harness.plugins.prompts import PromptProvider

class FrenchPrompts:
    def list_versions(self) -> list[str]:
        return ["fr_basic", "fr_formal"]

    def load(self, version, config):
        if version == "fr_basic":
            return "Translate English to French. Output only the translation."
        elif version == "fr_formal":
            return "You are a professional French translator. Use formal register..."

# Usage:
from gds_mt_eval_harness.runner import execute_run
await execute_run(config, prompt_providers=[FrenchPrompts()])
```

### PostTranslationHook — Corrective loops

```python
from gds_mt_eval_harness.plugins.hooks import PostTranslationHook

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
from gds_mt_eval_harness.plugins.tools import ToolProvider

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
gds-mt-eval dashboard report1.json report2.json -o results.html
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
gds-mt-eval run --no-cache ...
```

---

## 10. Cost Management

The harness pulls live pricing from OpenRouter and calculates per-entry and total costs.

### Cost optimization tips

1. **Start small**: Test on 5-10 entries first (`--ids 0,1,2,3,4`)
2. **Use caching**: Cached results cost $0 on re-runs
3. **Batch when possible**: `--batch-size 5` is roughly 5x cheaper per entry
4. **Use Flash models for iteration**: `--model gemini-3-flash` for prompt development
5. **Reserve Pro models for final benchmarks**: `--model gemini-3.1-pro` for publication

### Dry run

Validate your config without any API calls:

```bash
gds-mt-eval run --corpus data.json --dry-run
```

---

## 11. Integration Guide

### Installing in another project

```bash
# In your project's requirements.txt or pyproject.toml:
pip install git+https://github.com/gamedaysuits/gds-mt-eval-harness.git
```

### Programmatic usage

```python
import asyncio
from gds_mt_eval_harness.config import RunConfig
from gds_mt_eval_harness.runner import execute_run
from gds_mt_eval_harness.tester import analyze_run

async def evaluate():
    config = RunConfig(
        corpus_path="data/corpus.json",
        source_field="english",
        target_field="target_language",
        model="gemini-3.1-pro",
    )
    run_log = await execute_run(config)

    # Analyze the run
    from pathlib import Path
    log_files = list(Path(config.output_dir).glob("*.json"))
    report = analyze_run(log_files[-1])
    return report

asyncio.run(evaluate())
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

## 12. Troubleshooting

### "OPENROUTER_API_KEY not found"

```bash
export OPENROUTER_API_KEY=sk-or-v1-your-key
# Or create a .env file in your working directory
```

### "Corpus not found"

The `--corpus` flag requires an absolute or relative path to a JSON file.

### "sacrebleu not installed"

chrF++ and BLEU scores require the optional `sacrebleu` dependency:

```bash
pip install "gds-mt-eval-harness[metrics] @ git+https://github.com/gamedaysuits/gds-mt-eval-harness.git"
```

### Rate limiting (429 errors)

The harness automatically retries with exponential backoff. If you're still hitting limits:
- Reduce `--concurrency` (try 2-4)
- Add a delay between batches

### Cache not working

- Check that `--no-cache` isn't set
- Verify the cache directory is writable
- Changing ANY config parameter that affects output creates a new cache namespace

### "Unknown model"

Either use a short name from `gds-mt-eval list models` or pass the full OpenRouter model ID:

```bash
gds-mt-eval run --model anthropic/claude-sonnet-4 ...
```

---

*Licensed under Apache-2.0. See [LICENSE](LICENSE) for details.*
