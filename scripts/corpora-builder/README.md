# Champollion Corpora Builder

Multi-source corpus construction tooling for the [MT Eval Arena](../../README.md).

## What This Is

The corpora builder imports **human-authored parallel text** from public sources (Tatoeba, OPUS, custom CSVs), classifies each entry by domain and difficulty, then outputs a structured corpus JSON file ready for evaluation in the MT Eval Arena.

**No synthetic data.** Every entry traces back to a human-authored source with full provenance.

## Location

This package lives in the Champollion monorepo at:

```
champollion/arena/scripts/corpora-builder/
```

It mirrors to its own standalone repository: [`champollion-corpora-builder`](https://github.com/gamedaysuits/champollion-corpora-builder).

## Installation

```bash
# From this directory
pip install -e ".[dev]"
```

## Usage

```bash
# Build a 200-entry English→French corpus from Tatoeba
python -m corpora_builder \
  --source tatoeba \
  --source-lang eng \
  --target-lang fra \
  --max-entries 200 \
  --output output.json

# Build from an OPUS sub-corpus
python -m corpora_builder \
  --source opus \
  --source-lang eng \
  --target-lang deu \
  --opus-corpus GNOME \
  --max-entries 200 \
  --output output.json

# Build from a custom CSV file
python -m corpora_builder \
  --source csv \
  --source-lang eng \
  --target-lang crk \
  --csv-file my_data.csv \
  --max-entries 100 \
  --output output.json
```

Or use the installed entry point:

```bash
build-corpus --source tatoeba --source-lang eng --target-lang fra --max-entries 200 --output output.json
```

### License Confirmation

When downloading from an external source (Tatoeba, OPUS), the CLI prompts the user to confirm they accept the license terms **before** any data is downloaded.  This ensures compliance and avoids redistribution concerns — **we distribute build scripts, not data**.

```bash
# Interactive prompt (default)
python -m corpora_builder --source tatoeba --source-lang eng --target-lang fra --output output.json

# Skip prompt for CI/automation
python -m corpora_builder --source tatoeba --source-lang eng --target-lang fra --output output.json --yes
```

### Probe Tatoeba

Before building corpora for many languages, probe Tatoeba to find which pairs have downloadable data:

```bash
# Probe using champollion language cards
python -m corpora_builder.probe_tatoeba \
  --language-cards-dir cli/shared/language-cards \
  --output probe_results.json

# Probe specific languages
python -m corpora_builder.probe_tatoeba \
  --langs eng fra deu jpn crk
```

### Batch Build

Build development corpora for **all viable Tatoeba pairs** at once.  One license confirmation covers the entire batch:

```bash
python -m corpora_builder.build_dev_corpora \
  --language-cards-dir cli/shared/language-cards \
  --output-dir arena/datasets/curated \
  --registry arena/datasets/registry.json \
  --max-entries 200 \
  --yes  # skip prompt for automation
```

The batch builder:
1. Probes Tatoeba for all pair combinations
2. Shows one license confirmation (Tatoeba CC-BY-2.0)
3. Downloads, parses, enriches, and samples each viable pair
4. Skips pairs below 30 entries (too small for meaningful evaluation)
5. Updates the corpus registry with all built corpora

## Domain Taxonomy

Every entry is classified into one of 16 domains:

| Code | Domain | Description |
|------|--------|-------------|
| `ui` | User Interface | Software menus, buttons, dialogs, settings |
| `legal` | Legal | Contracts, statutes, court proceedings |
| `medical` | Medical | Clinical notes, prescriptions, diagnoses |
| `financial` | Financial | Banking, accounting, investments |
| `edu` | Education | Academic, classroom, curriculum |
| `ecommerce` | E-Commerce | Product listings, orders, reviews |
| `marketing` | Marketing | Campaigns, branding, audience engagement |
| `gov` | Government | Policy, legislation, public services |
| `scientific` | Scientific | Research papers, methodology, experiments |
| `religious` | Religious | Scripture, worship, ceremony |
| `support` | Customer Support | Tickets, troubleshooting, FAQs |
| `subtitles` | Subtitles | Film/TV dialogue, stage directions |
| `news` | News | Journalism, press releases, reporting |
| `literary` | Literary | Fiction, poetry, narrative prose |
| `conv` | Conversational | Casual dialogue, chat, everyday speech |
| `tech` | Technical | APIs, infrastructure, protocols |

## Difficulty Tiers

Each entry is assigned a difficulty tier (1–5) based on sentence length, clause count, and vocabulary complexity:

| Tier | Word Count | Description |
|------|-----------|-------------|
| 1 | 1–5 | Basic vocabulary, labels |
| 2 | 6–10 | Simple sentences |
| 3 | 11–18 | Moderate complexity |
| 4 | 19–30 | Complex, multi-clause |
| 5 | 31+ | Advanced, dense sentences |

## Human-Authored Only

This tool **only** imports human-authored parallel text. Sources must provide:

- Provenance metadata (who created it, under what license)
- A verifiable URL or identifier
- Evidence of human authorship (e.g., Tatoeba contributors, published translations)

Machine-generated, back-translated, or synthetic data is explicitly excluded. The purpose is to build evaluation corpora that measure how well MT systems translate *real human language*, not how well they reproduce other machines' output.

## Python API

Adapters conform to the `SourceAdapter` ABC. All adapters have a `fetch(source_lang, target_lang, **kwargs)` method:

```python
from corpora_builder.adapters.tatoeba_adapter import TatoebaAdapter
from corpora_builder.adapters.opus_adapter import OpusAdapter

# Tatoeba — requires either file_path or download_url
adapter = TatoebaAdapter()
entries = adapter.fetch("eng", "fra", file_path="tatoeba_eng_fra.tsv")

# OPUS — requires corpus_name, file_path, and license_id
adapter = OpusAdapter()
entries = adapter.fetch(
    "eng", "deu",
    corpus_name="Europarl",
    file_path="europarl_en_de.tmx",
    license_id="CC-BY-SA-4.0",
)
```

## Validation

`CorpusEntry` validates at construction time (fail-loud, no silent defaults):

- **`domain`** must be one of the 16 valid domain codes
- **`difficulty`** must be 1–5
- **`id`**, **`source`**, **`reference`**, **`register`** must be non-empty strings

Invalid entries raise `ValueError` immediately — they never enter the corpus silently.

Adapters also validate loudly:
- **Tatoeba**: Any malformed TSV row (wrong column count) raises `ValueError` after parsing completes
- **OPUS**: Missing `corpus_name`, `file_path`, or `license_id` raises `ValueError`

## License

Apache 2.0
