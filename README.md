# MT Eval Harness

> Most translation tools evaluate Google Translate and DeepL.
> This harness exists for the languages they ignore.

**MT Eval Harness** is an open-source evaluation framework for developing, benchmarking, and deploying novel machine translation methods — especially for low-resource languages where commercial tools don't exist.

Anyone who speaks both languages can contribute a translation method. Prove it works, export it, deploy it.

---

## Why This Exists

There are ~7,000 living languages. Fewer than 200 have any MT support. For the other 6,800, translation technology doesn't exist — and it won't come from Google.

This harness provides the infrastructure to **crowdsource** that work:

1. **Develop** a translation method — an LLM prompt, a coached pipeline, a deterministic process, or any combination
2. **Benchmark** it against a reference corpus with standardized metrics (chrF++, BLEU, exact match)
3. **Export** validated methods as [i18n-rosetta](https://github.com/gamedaysuits/i18n-rosetta) plugins
4. **Deploy** to production websites via rosetta's translation CLI

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Develop   │───▶│  Benchmark  │───▶│   Export     │───▶│   Deploy    │
│  method.py  │    │ mt-eval run │    │ mt-eval      │    │ i18n-rosetta│
│             │    │ mt-eval test│    │   export     │    │   translate │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Quick Start

```bash
# Install
pip install mt-eval-harness

# Set your API key (supports OpenRouter — any model)
export OPENROUTER_API_KEY=sk-or-...

# Run a translation experiment with optimal defaults
# (batch_size=25, max_tokens=32768, concurrency=8, cache=on)
mt-eval run --corpus data/corpus.json --model gemini-3.1-pro

# Multi-model parallel run — all models execute simultaneously
mt-eval run --corpus data/corpus.json \
  -m gemini-3.1-pro,claude-opus-4.7,gpt-5.5,deepseek-v4-pro

# Analyze the results
mt-eval test eval/logs/run_*.json

# Generate a comparison dashboard
mt-eval dashboard eval/logs/*.json
```

## Performance Defaults

> **The harness is "fast by default, safe by design."**
> Do NOT lower these values unless you have a specific reason.

All defaults are defined as `HARNESS_DEFAULTS` constants in [`config.py`](mt_eval_harness/config.py). Change them in **one place** and they propagate everywhere.

| Setting | Default | Why |
|---|---|---|
| `batch_size` | **25** | Groups entries into numbered-list prompts. 25× fewer API calls. Proven reliable across all frontier models. Tool-calling auto-overrides to 1. |
| `max_tokens` | **32768** | Generous headroom eliminates truncation risk. Translation outputs are short (1-30 words), so unused tokens cost nothing. |
| `concurrency` | **8** | Parallel batch calls within a single model. Bounded by `asyncio.Semaphore` for rate limit safety. |
| `cache_enabled` | **True** | File-backed cache prevents redundant API calls. Keyed on model + prompt + temperature + language pair. Almost never a reason to disable. |
| `temperature` | **0.0** | Deterministic output for reproducibility. |

### Multi-Model Parallelism

For benchmarks, use `execute_multi_run()` — **not** a for-loop over `execute_run()`:

```python
from mt_eval_harness.runner import execute_multi_run
from mt_eval_harness.config import RunConfig

configs = [
    RunConfig(model="google/gemini-3.1-pro-preview", corpus_path="data.json", ...),
    RunConfig(model="anthropic/claude-opus-4.7", corpus_path="data.json", ...),
    RunConfig(model="openai/gpt-5.5", corpus_path="data.json", ...),
]

# All models run in parallel — wall-clock = slowest single model
results = await execute_multi_run(configs)
```

Each model gets its own aiohttp session and semaphore. A 14-model benchmark runs in **~15 minutes parallel** vs ~3.5 hours sequential.

## What Makes This Different

| Feature | MT Eval Harness | Other MT Eval Tools |
|---|---|---|
| **Language-agnostic** | Any pair, any script | Hardcoded for major languages |
| **Plugin architecture** | Bring your own methods, metrics, tools | Fixed evaluation pipeline |
| **Export to production** | Direct rosetta plugin export | Evaluation only |
| **Crowdsource-ready** | Prove your method is better, share it | Researcher-only |
| **Model-agnostic** | Any OpenRouter model (100+) | Single-vendor |
| **Fast by default** | batch=25, cache=on, parallel multi-model | Manual optimization |

## Core Architecture

```
mt_eval_harness/
├── runner.py              # Orchestrator — strategy-based execution
├── pipeline.py            # Shared: cache, hooks, enrichment, logging
├── strategies/            # Execution backends
│   ├── single.py          # One entry per API call
│   ├── batch.py           # Multiple entries per call
│   ├── tool_call.py       # Multi-round tool-calling
│   └── plugin_process.py  # Custom TranslationProcess plugins
├── tester.py              # Offline metric computation
├── exporter.py            # i18n-rosetta plugin packaging
├── api.py                 # OpenRouter HTTP client
├── cache.py               # Deterministic result caching
├── config.py              # Typed configuration + protocols
├── cli.py                 # Command-line interface
├── dashboard.py           # Interactive HTML report generator
└── plugins/               # Extension protocols
    ├── prompts.py          # PromptProvider
    ├── metrics.py          # MetricPlugin
    ├── hooks.py            # PostTranslationHook
    └── tools.py            # ToolProvider
```

## Extending the Harness

The harness exposes four plugin protocols. If your class has the right method signatures, it works — no inheritance required.

```python
from mt_eval_harness.config import TranslationProcess

class MyTranslationPipeline:
    """Custom pipeline — implements TranslationProcess protocol."""

    async def translate(self, entries: list[dict], config) -> list[dict]:
        # Your translation logic here
        return [{"id": e["id"], "predicted": "..."} for e in entries]
```

See [GUIDE.md](GUIDE.md) for full plugin documentation.

## Installation

```bash
# Basic (aiohttp + dotenv only)
pip install mt-eval-harness

# With metric computation (sacrebleu)
pip install mt-eval-harness[metrics]

# Development
pip install -e ".[dev]"
```

**Requirements:** Python 3.11+ · `OPENROUTER_API_KEY` environment variable

## Documentation

- **[GUIDE.md](GUIDE.md)** — Full user guide and API reference
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Development standards and contribution workflow
- **[docs/METHOD_PLUGIN_SPEC.md](docs/METHOD_PLUGIN_SPEC.md)** — i18n-rosetta plugin specification

## Currently In Development

We're actively using this harness to develop a Plains Cree (crk) translation method — the first sentence-level English-to-Plains Cree MT system. The method isn't production-ready yet, but the harness is.

## License

Apache 2.0
