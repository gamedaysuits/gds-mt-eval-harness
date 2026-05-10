# gds-mt-eval-harness

**A configurable, language-agnostic evaluation harness for machine translation pipelines.**

Run any translation method — LLM prompting, rule-based systems, custom agent pipelines — through a standardized evaluation framework to get research-grade, reproducible metrics.

## What It Does

```
┌─────────────┐     ┌───────────────┐     ┌──────────────┐     ┌────────────┐
│  Your Corpus │────▶│  Run Harness  │────▶│  Test Harness │────▶│  Dashboard │
│  (JSON)      │     │  (translate)  │     │  (evaluate)   │     │  (HTML)    │
└─────────────┘     └───────────────┘     └──────────────┘     └────────────┘
```

- **Run Harness**: Executes translations with configurable model, prompt, batching, caching, tool-calling, and concurrency.
- **Test Harness**: Computes exact match, chrF++, BLEU, and any custom metrics via plugins.
- **Dashboard**: Generates a zero-dependency interactive HTML report.

## Quick Start

```bash
# Install
pip install git+https://github.com/gamedaysuits/gds-mt-eval-harness.git

# Set your API key
export OPENROUTER_API_KEY=sk-or-v1-...

# Run a basic evaluation
gds-mt-eval run --corpus data/my_corpus.json --source-field english --target-field french

# Analyze results
gds-mt-eval test logs/run_*.json

# Generate dashboard
gds-mt-eval dashboard logs/run_*_report.json
```

## Plugin Architecture

The harness is generic. Language-specific logic plugs in through four protocols:

| Protocol | Purpose | Example |
|---|---|---|
| `MetricPlugin` | Custom evaluation metrics | FST validity, morphological linting |
| `PromptProvider` | Language-specific system prompts | Grammar-coached Cree prompts |
| `PostTranslationHook` | Post-processing / corrective loops | FST-gated re-prompting |
| `ToolProvider` | LLM tool-calling integrations | Morphological analyzer tools |

See `examples/custom_pipeline/` for a complete plugin example.

## Corpus Format

Your corpus is a JSON array. Required fields: `id` (int). Everything else is configurable:

```json
[
  {"id": 0, "english": "I see a dog.", "cree_sro": "niwâpahtên atim.", "segment": "basic", "difficulty": 1},
  {"id": 1, "english": "She is running.", "cree_sro": "pimipahtâw.", "segment": "basic", "difficulty": 1}
]
```

Configure `--source-field` and `--target-field` to match your column names.

## Documentation

📖 **[GUIDE.md](GUIDE.md)** — Full researcher's guide with configuration reference, plugin development, and workflow examples.

## License

Apache-2.0 — see [LICENSE](LICENSE).

You can freely use this in commercial and academic projects. Build proprietary translation pipelines on top of it.
