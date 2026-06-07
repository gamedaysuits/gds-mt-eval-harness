# MT Eval Harness

> Most translation tools evaluate Google Translate and DeepL.
> This harness exists for the languages they leave unverified.

**MT Eval Harness** is an open-source evaluation framework for developing, benchmarking, and deploying novel machine translation methods — especially for low-resource languages where commercial tools either don't exist or claim coverage that hasn't been independently validated.

Anyone who speaks both languages can contribute a translation method. Prove it works, export it, deploy it.

---

## Why This Exists

There are ~7,000 living languages. Meta's OMT-1600 claims translation coverage for 1,600 of them — but for the ~1,300 at their lowest resource tiers, quality is below usable thresholds and the model weights are not currently available. For the remaining ~5,400, translation technology doesn't exist at all. Independent evaluation infrastructure is the missing piece.

This harness provides the infrastructure to **crowdsource** that work:

1. **Develop** a translation method — an LLM prompt, a coached pipeline, a deterministic process, or any combination
2. **Benchmark** it against a reference corpus with standardized metrics (chrF++, exact match, code-switching detection, hallucination detection, terminology adherence, FST acceptance for morphologically-rich languages)
3. **Export** validated methods as [champollion](https://github.com/gamedaysuits/champollion) plugins
4. **Deploy** to production websites via champollion's translation CLI

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Develop   │───▶│  Benchmark  │───▶│   Export     │───▶│   Deploy    │
│  method.py  │    │ mt-eval run │    │ mt-eval      │    │ champollion│
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

# Use a standard parallel text corpus (FLORES+, WMT, NTREX)
mt-eval run \
  --source-file flores200/dev/eng_Latn.dev \
  --reference-file flores200/dev/fra_Latn.dev \
  --target-lang French

# Create a contest — public or private
mt-eval contest create --name "EN→CRK Open" \
  --corpus edtekla-v1.json --visibility public

# Use your champollion.config.json for production-identical prompts
mt-eval run --corpus data/corpus.json \
  --champollion-config champollion.config.json \
  --target-lang-code fr

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
| **Export to production** | Direct champollion plugin export | Evaluation only |
| **Crowdsource-ready** | Prove your method is better, share it | Researcher-only |
| **Model-agnostic** | Any OpenRouter model (100+) | Single-vendor |
| **Fast by default** | batch=25, cache=on, parallel multi-model | Manual optimization |
| **COMET with bootstrap CIs** | Cached per-entry bootstrap — no redundant neural inference | CIs rarely computed |
| **AfriCOMET auto-selection** | Auto-selects `masakhane/africomet-mtl` for 35 African languages | One model fits all |
| **Per-difficulty-tier analysis** | Metrics + CIs per translation difficulty level (Tier 1–5) | Corpus-level only |
| **Contest infrastructure** | Public, private, or team contests with blind evaluation | No contest support |
| **Writing style benchmarking** | Custom style metrics + brand voice prompt tuning | Quality metrics only |

## Core Architecture

```
mt_eval_harness/
├── runner.py              # Orchestrator — strategy-based execution
├── corpus_loader.py       # Multi-format dataset loading (JSON/JSONL/TSV/parallel text)
├── champollion_config.py      # champollion config reader + prompt builder
├── pipeline.py            # Shared: cache, hooks, enrichment, logging
├── strategies/            # Execution backends
│   ├── single.py          # One entry per API call
│   ├── batch.py           # Multiple entries per call
│   ├── tool_call.py       # Multi-round tool-calling
│   └── method_strategy.py # Custom TranslationMethod plugins
├── tester.py              # Offline metric computation
├── exporter.py            # champollion plugin packaging
├── api.py                 # OpenRouter HTTP client
├── cache.py               # Deterministic result caching
├── config.py              # Typed configuration + protocols
├── cli.py                 # Command-line interface
├── dashboard.py           # Interactive HTML report generator
└── plugins/               # Extension protocols
    ├── prompts.py          # PromptProvider
    ├── champollion_prompts.py  # ChampollionPromptProvider (built-in champollion interop)
    ├── metrics.py          # MetricPlugin
    ├── hooks.py            # PostTranslationHook
    └── tools.py            # ToolProvider
```

## Extending the Harness

The harness exposes four plugin protocols. If your class has the right method signatures, it works — no inheritance required.

```python
from mt_eval_harness.config import TranslationMethod

class MyTranslationPipeline:
    """Custom pipeline — implements TranslationMethod protocol."""

    async def translate(self, entries: list[dict], config) -> list[dict]:
        # Your translation logic here
        return [{"id": e["id"], "predicted": "..."} for e in entries]
```

See [GUIDE.md](GUIDE.md) for full plugin documentation.

## Installation

```bash
# Install the harness
pip install mt-eval-harness

# Interactive setup — installs optional deps with explanations
mt-eval setup

# Or install everything at once, no prompts
mt-eval setup --all

# Check what's installed
mt-eval setup --status
```

**Requirements:** Python 3.11+ · `OPENROUTER_API_KEY` environment variable

> **Ship lean, install on consent.** The harness core has minimal dependencies. Optional capabilities (COMET neural metric, FST morphological validation) install interactively via `mt-eval setup` — or on-the-fly when the harness detects they'd improve your eval. You never need to know specific pip commands.

<details>
<summary>Manual pip install (if you prefer)</summary>

```bash
pip install mt-eval-harness[comet]   # COMET neural metric + AfriCOMET
pip install mt-eval-harness[fst]     # FST morphological validation
pip install -e ".[dev]"              # Development
```
</details>

## Documentation

- **[GUIDE.md](GUIDE.md)** — Full user guide and API reference
- **[CHANGELOG.md](CHANGELOG.md)** — Versioned change log
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Development standards and contribution workflow
- **[Plugin Specification](../cli/website/docs/reference/plugin-spec.md)** — champollion plugin specification
- **[Scoring Specification](website/docs/specifications/scoring.md)** — SSOT for metrics, composite weights, quality tiers

## Contests & Leaderboards

The Arena supports structured evaluation contests — from open research bounties to private team benchmarks:

```bash
# Create a public contest with a prize
mt-eval contest create --name "EN→CRK Open" \
  --corpus edtekla-v1.json --visibility public

# Create a private contest for blind team evaluation
mt-eval contest create --name "Q3 DE Compliance" \
  --corpus de_compliance.json --visibility private \
  --teams "berlin,vienna,zurich,munich"

# Submit a run to a contest
mt-eval contest submit --contest "EN→CRK Open" \
  --run eval/logs/run_fst-nmt-v3.json

# List active contests
mt-eval contest list
```

Visibility modes: `public` (anyone), `private` (invite-only, blind), `team` (org-scoped). See [GUIDE.md § 14](GUIDE.md#14-contests--leaderboards) for full contest documentation.

## Currently In Development

We're actively using this harness to develop and evaluate Plains Cree (crk) translation methods — including our own FST-gated pipeline and external systems like Meta's OMT-1600 (which includes CRK at R1 tier). The harness provides independent evaluation with morphological validation that standard metrics cannot.

## License

Apache 2.0
