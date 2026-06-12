# MT Eval Harness — Quick Start

> Run your first translation evaluation in under 5 minutes.

---

## Prerequisites

- **Python 3.11+**
- **API key**: `export OPENROUTER_API_KEY=sk-or-...`

## 1. Install

```bash
cd arena
pip install -e .
```

## 2. Setup (per language)

Each language has an **eval pack** — the set of tools needed for accurate
evaluation. The harness won't let you run without them.

### Plains Cree (crk)

```bash
# One command installs: pyhfst, spaCy, en_core_web_md model,
# requests, and downloads the ALTlab FST morphological analyzer.
mt-eval setup --lang crk
```

### All other languages

Most languages only need the base install. If a dataset requires
extra dependencies, the harness reads the language card and tells
you exactly what to run — e.g., `mt-eval setup --lang sme` for
Northern Sámi.

## 3. Run an evaluation

```bash
# Evaluate a single model against the CRK textbook corpus
mt-eval run --corpus edtekla-textbook -m claude-sonnet -n my-first-run

# The harness will:
# 1. Validate your config
# 2. Check eval pack dependencies
# 3. Run translations (batched, cached, parallelized)
# 4. Score with all metrics (chrF++, BLEU, LYSS, FST validity)
# 5. Print a human-readable run card
# 6. Ask if you want to publish to the arena
```

### Common model shortcuts

| Shortcut | Model |
|----------|-------|
| `claude-sonnet` | anthropic/claude-sonnet-4 |
| `gemini-pro` | google/gemini-2.5-pro-preview |
| `gemini-flash` | google/gemini-2.5-flash-preview |
| `gpt` | openai/gpt-4.1 |

Or pass any full [OpenRouter model ID](https://openrouter.ai/models):

```bash
mt-eval run --corpus edtekla-textbook -m anthropic/claude-fable-5
```

### Multi-model comparison

```bash
mt-eval run --corpus edtekla-textbook \
  -m claude-sonnet,gemini-pro,gpt -n model-comparison
```

All models run in parallel.

## 4. Analyze an existing run

```bash
# Re-score a previous run (auto-prints the run card)
mt-eval test eval/logs/harness/run_*.json

# View the run card for a completed run
mt-eval card eval/logs/harness/run_*.json

# Compare multiple runs
mt-eval compare eval/logs/harness/*_report.json

# Generate an interactive HTML dashboard
mt-eval dashboard eval/logs/harness/*_report.json
```

## 5. Publish to the arena

After any run or test, the harness asks:

```
  → Publish this run to the arena? [y/N]:
```

Or publish manually:

```bash
mt-eval publish eval/logs/harness/run_*_report.json
```

---

## What the run card looks like

```
┌──────────────────────────────────────────────────────────────────────┐
│                      MT EVAL HARNESS — RUN CARD                      │
├──────────────────────────────────────────────────────────────────────┤
│ Model                  anthropic/claude-fable-5                      │
│ Target language        crk                                           │
│ Entries                436            Errors        0                │
├──────────────────────────────────────────────────────────────────────┤
│ SCORES                                                               │
│ chrF++                 49.4  [47.5 – 51.3]                          │
│ BLEU                   5.0   [3.3 – 6.8]                            │
│ Exact match            16/436 (3.7%)                                │
├──────────────────────────────────────────────────────────────────────┤
│ LYSS EQUIVALENCE LINTER                                              │
│ Equivalent match       104/436 (23.9%)                               │
│   ├ Exact              16/436 (3.7%)                                 │
│   └ Near-miss          87/436 (20.2%)                                │
├──────────────────────────────────────────────────────────────────────┤
│ FST MORPHOLOGICAL VALIDITY                                           │
│ Word validity          1144/1381 (82.8%)                             │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### "EVAL PACK REQUIRED: Plains Cree"

You tried to run against a CRK dataset without installing the CRK eval pack.

```bash
mt-eval setup --lang crk
```

### "Dataset not found"

The harness will suggest the closest match. Common aliases:

| You typed | Resolves to |
|-----------|-------------|
| `edtekla-full` | `edtekla-textbook` |
| `edtekla` | `edtekla-textbook` |
| `edtekla-dev` | `edtekla-dev-v1` |
| `crk-dev` | `edtekla-dev-v1` |

### "Unknown model"

Pass the full OpenRouter model ID:

```bash
mt-eval run --corpus edtekla-textbook -m anthropic/claude-fable-5
```

---

## For AI Agents

If you are an AI agent running this harness:

1. **Setup**: Run `mt-eval setup --lang crk` before any CRK evaluation
2. **Run**: `mt-eval run --corpus edtekla-textbook -m <model> -n <name>`
3. **Results**: The run card prints automatically after scoring
4. **FST downloads**: Auto-consent in non-interactive mode (no TTY prompt)
5. **Publish**: Pass `--yes` to auto-confirm: `mt-eval publish --yes <report>`

The harness is designed to fail fast with clear error messages.
If a dependency is missing, it tells you exactly what to install.
