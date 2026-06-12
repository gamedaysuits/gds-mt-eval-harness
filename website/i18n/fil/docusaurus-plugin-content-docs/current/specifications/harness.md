---
sidebar_position: 2
title: "Eval Harness v2.0"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "What the harness metrics feed into"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: Translate 30 Languages"
    to: https://champollion.dev/docs/tutorials/translate-30-languages
    kind: champollion
    note: "Use the harness to audit registers in production"
---
# Eval Harness v2.0

> **Buod para sa Ehekutibo.** Sinasaklaw ng pahinang ito ang pag-install, pag-configure, at paggamit ng MT evaluation harness — ang tool na nagbe-benchmark ng mga paraan ng pagsasalin laban sa mga standardized corpus at lumilikha ng mga scored run card. Para sa mga kanonikal na depinisyon ng metrics, schema, at protocol ng evaluation, tingnan ang [Espesipikasyon ng Benchmark](/docs/specifications/benchmark).

Pinapatakbo ng harness ang mga eksperimento sa pagsasalin at lumilikha ito ng mga run card. Pinangangasiwaan nito ang prompt construction, API calls, scoring, at result serialization — ibinibigay ninyo ang dataset at ang model.

## Pag-install

**Mga kinakailangan:** Python 3.10+

```bash
pip install sacrebleu aiohttp
```

I-clone ang repository ng harness:

```bash
git clone https://github.com/gamedaysuits/arena.git
cd arena
```

## Paggamit

```bash
mt-eval run --corpus path/to/dataset.json
```

Pinapatakbo nito ang bawat entry sa corpus sa pamamagitan ng naka-configure na model (o method plugin), binibigyan ng score ang mga output, at nagsusulat ng run card JSON file sa output directory.

## Mga CLI Flag

### `mt-eval run`

| Flag | Kinakailangan | Default | Paglalarawan |
|------|----------|---------|-------------|
| `--corpus` | ✅ | — | Path papunta sa corpus file (`.json`, `.jsonl`, `.tsv`) |
| `--source-file` / `--reference-file` | — | — | Parallel text files (FLORES+, WMT format) |
| `-m, --model` | — | `gemini-pro` | Model slug (maikling pangalan o buong OpenRouter ID). Nire-resolve sa pamamagitan ng `shared/model-aliases.json`. Pinaghihiwalay ng comma para sa mga multi-model run |
| `-d, --dataset` | — | `all` | Dataset filter: `all`, pangalan ng segment, o ID range |
| `--ids` | — | — | Mga entry ID na pinaghihiwalay ng comma upang i-evaluate |
| `--source-lang` | — | `English` | Pangalan ng source language |
| `--target-lang` | — | — | Pangalan ng target language |
| `-p, --prompt` | — | `naive` | Bersyon ng prompt (`naive`, `custom`, `champollion`) |
| `--coaching-file` | — | — | Path papunta sa coaching prompt text file |
| `--coaching` | — | — | Inline coaching text (quoted string) |
| `--method` | — | — | Path papunta sa method plugin directory (naglalaman ng `method.json` + Python module) |
| `--method-card` | — | — | Path papunta sa method card JSON para sa leaderboard metadata |
| `--fst-retries` | — | `0` | Bilang ng mga FST retry attempt (default LLM method lamang) |
| `--skip-fst` | — | `false` | Laktawan nang buo ang FST quality gate |
| `--tools` | — | `false` | I-enable ang tool-calling mode |
| `--tools-list` | — | — | Mga pangalan ng tool na pinaghihiwalay ng comma |
| `--max-tool-rounds` | — | `8` | Pinakamataas na tool-calling rounds bawat entry |
| `--hooks` | — | — | Mga pangalan ng post-translation hook |
| `--style-profile` | — | — | Path papunta sa style profile JSON. Ini-enable ang writing-style consistency metrics (impormatibo — hindi kailanman bahagi ng composite score; tingnan ang [§ Writing-style at register metrics](#writing-style-and-register-metrics-informational)) |
| `-b, --batch-size` | — | `25` | Mga entry bawat API call |
| `-c, --concurrency` | — | `8` | Mga parallel API call |
| `--max-tokens` | — | `32768` | Max tokens bawat API call |
| `--temperature` | — | `0.0` | Sampling temperature (0.0 = deterministic) |
| `--no-cache` | — | `false` | I-disable ang response caching |
| `--cache-dir` | — | `eval/cache/harness` | Path ng cache directory |
| `-o, --output-dir` | — | `eval/logs/harness` | Output directory para sa mga run card at log |
| `-n, --name` | — | — | Run name na madaling basahin ng tao |
| `--dry-run` | — | `false` | I-validate ang configuration nang hindi gumagawa ng API calls |
| `--champollion-config` | — | — | Path papunta sa `champollion.config.json` |
| `--champollion-cards-dir` | — | — | Language cards directory |
| `--target-lang-code` | — | — | BCP-47 language code |

### Iba Pang Subcommands

| Subcommand | Paglalarawan |
|------------|-------------|
| `mt-eval test <log_path>` | Suriin ang isang nakumpletong run log |
| `mt-eval publish <report_path>` | Magsumite ng run card sa leaderboard |
| `mt-eval compare <logs...>` | Paghambingin ang maraming run nang magkakatabi |
| `mt-eval dashboard <logs...>` | Bumuo ng HTML dashboard mula sa mga run log |
| `mt-eval list models\|prompts\|datasets` | Ilista ang mga available na resource |
| `mt-eval export` | I-package ang kasalukuyang setup bilang champollion method plugin |
| `mt-eval export-config` | I-export ang na-resolve na MethodConfig (lahat ng 8 kanonikal na field) bilang JSON |

### Mga Halimbawa

```bash
# Run with defaults (gemini-pro alias → google/gemini-3.1-pro-preview, naive prompt)
mt-eval run --corpus data/edtekla-dev-v1.json

# Coached experiment with coaching file
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model google/gemini-3.1-pro \
  --coaching-file prompts/crk-coaching-v8.txt \
  --temperature 0.0

# Run a custom method plugin with FST retries
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --method ./methods/fst-gated-pipeline \
  --fst-retries 3
```

---

## Schema ng Run Card

Ang bawat eksperimento ay lumilikha ng **run card** — isang self-contained JSON document. Ang top-level structure:

```json
{
  "run_id": "uuid-v4",
  "harness_version": "2.0",
  "model_slug": "google/gemini-3.1-pro",
  "model_id": "gemini-3.1-pro-001",
  "condition": "baseline",
  "timestamp": "2026-06-01T03:22:41Z",
  "elapsed_seconds": 142.7,
  "dataset": { ... },
  "config": { ... },
  "method_card": { ... },
  "system_prompt_sha256": "abc123...",
  "system_prompt_used": "You are a translator...",
  "fingerprint": { ... },
  "scores": { ... },
  "totals": { ... },
  "environment": { ... },
  "results": [ ... ],
  "run_card_hash": "sha256-of-entire-card"
}
```

Tingnan ang [Espesipikasyon ng Run Card](/docs/specifications/run-card) para sa buong schema na may dokumentasyon para sa bawat field.

:::info Awtoritatibong Schema
Ang [Espesipikasyon ng Benchmark](/docs/specifications/benchmark) ang iisang source of truth para sa schema ng run card. Para sa mga depinisyon ng metric, composite weights, at quality tiers, tingnan ang [Espesipikasyon sa Scoring](/docs/specifications/scoring). Idinodokumento ng pahinang ito kung paano gamitin ang harness; ang mga spec ang nagtatakda kung ano ang kahulugan ng mga output.
:::

### Mahahalagang Block

**`dataset`** — Tinutukoy kung aling dataset ang ginamit, kabilang ang content hash nito upang maiugnay ang mga resulta sa isang partikular na bersyon:

```json
// Example using master_corpus.json (62 gold + 342 textbook = 404)
{
  "id": "edtekla-dev-v1",
  "version": "1.0",
  "language_pair": "EN→CRK",
  "sha256": "...",
  "entry_count": 404
}
```

**`scores`** — Aggregate metrics para sa run:

```json
// Counts reflect the dataset used (here: master_corpus.json, 404 entries)
{
  "total": 404,
  "exact_matches": 12,
  "exact_match_rate": 0.0968,
  "fst_accepted": 87,
  "fst_acceptance_rate": 0.7016,
  "chrf_plus_plus": 42.31,
  "errors": 0,
  "avg_latency_seconds": 1.15,
  "median_latency_seconds": 1.02,
  "p95_latency_seconds": 2.34,
  "by_difficulty": { ... },
  "by_provenance": { ... }
}
```

**`totals`** — Pagsubaybay sa token usage at cost:

```json
{
  "prompt_tokens": 48200,
  "completion_tokens": 3100,
  "reasoning_tokens": 0,
  "cached_tokens": 12000,
  "total_cost_usd": 0.42,
  "cost_per_entry_usd": 0.0034,
  "reasoning_ratio": 0.0
}
```

---

## Writing-style at register metrics (impormatibo)

Maaaring i-evaluate ng harness kung tumutugma ang mga pagsasalin sa target na **register** at **writing style**, sa pamamagitan ng `WritingStyleConsistency` metric plugin (`mt_eval_harness/plugins/writing_style.py`). Maaaring tama sa lingguwistikong antas ang isang pagsasalin ngunit mali ang register — impormal na phrasing sa legal na dokumento, formal boilerplate sa marketing copy — at hindi ito mapapansin ng string metrics. Napapansin ito ng mga metric na ito.

**Ano ang sinusukat (bawat entry):**

| Metric | Sukatan | Kahulugan |
|--------|-------|---------|
| `style_register_match` | boolean | Tumutugma ba ang output sa inaasahang register? Ang target ay nagmumula sa `register` field ng corpus entry (tingnan ang [Benchmark Spec §2.6](/docs/specifications/benchmark)) o mula sa isang style profile |
| `style_sentence_length_ratio` | float | Hinulaang vs reference na average sentence length (1.0 = tugma; divergence = style drift) |
| `style_formality_score` | 0.0–1.0 | Presensya ng mga formal/informal marker (T–V pronouns, contractions, …) gamit ang per-language marker resources |

**Aggregate:** `style_consistency_rate` — ang fraction ng mga entry na walang natukoy na register mismatch.

Mag-enable ng custom target gamit ang `--style-profile path/to/profile.json` (hal. isang brand-voice profile); kung wala nito, bumabalik ang plugin sa `register` metadata ng bawat corpus entry kung naroroon.

:::caution Matapat na saklaw
Ang mga metric na ito ay **impormatibo lamang** — hindi kailanman bahagi ang mga ito ng composite score, at marker-based ang formality detection (isang heuristic), hindi isang learned judgment. Ituring ang mga ito bilang drift detector para sa pagsunod sa register, hindi bilang hatol sa kalidad ng style.
:::

---

## Fingerprint vs Run Card Hash

Lumilikha ang harness ng dalawang magkaibang hash. Magkaiba ang layunin ng mga ito:

### Fingerprint

Sinasagot ng **fingerprint** ang: *"Maaari bang ma-reproduce ang run na ito?"*

Iha-hash nito ang kombinasyon ng mga input na nagtatakda sa experiment configuration — hindi ang mga output:

- Dataset SHA-256
- Model slug
- Condition label
- System prompt SHA-256
- Temperature
- Harness version

Dalawang run na may magkaparehong fingerprint ang gumamit ng parehong setup. Dapat maihambing ang kanilang mga resulta (maliban sa API non-determinism).

### Run Card Hash

Sinasagot ng **run card hash** ang: *"Nabago ba nang hindi awtorisado ang partikular na result file na ito?"*

Ito ang SHA-256 ng buong run card JSON (hindi kasama ang mismong `run_card_hash` field). Kung may magbago sa anumang field — isang score, isang timestamp, isang output — masisira ang hash.

:::info Kailan gagamitin ang alin
Gamitin ang **fingerprint** upang i-group ang mga maihahambing na run (parehong eksperimento, magkaibang execution). Gamitin ang **run card hash** upang beripikahin ang integridad ng isang partikular na result file.
:::

---

## Pag-publish sa Leaderboard

Pagkatapos makumpleto ang isang run, gamitin ang `mt-eval publish` upang isumite ang run card:

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

Kung walang ibinigay na `--method-card` habang pinapatakbo ang run, inilulunsad ng `mt-eval publish` ang isang interactive wizard (`method_card_wizard.py`) na gagabay sa inyo sa paglalarawan ng inyong method (pangalan, class, mga tool na ginamit, atbp.). Ini-embed ang output ng wizard sa run card bago isumite.

### Manwal na pagsusumite

Sine-save ang mga run card bilang JSON files sa output directory. Maaari rin ninyong isumite ang anumang run card file sa pamamagitan ng leaderboard UI sa [/leaderboard](https://champollion.dev/leaderboard), o sa pamamagitan ng API:

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning Validation ng Leaderboard
Bine-validate ng leaderboard ang mga isinumiteng run card laban sa dataset registry. Tinatanggihan ang mga submission na tumutukoy sa hindi kilalang mga dataset, o may sirang `run_card_hash`.
:::

:::danger HUWAG MAG-TRAIN sa evaluation data
Kung nakita na ng inyong method ang evaluation dataset sa panahon ng development — bilang training data, few-shot examples, dictionary entries, o prompt engineering material — ang inyong submission ay **madidiskuwalipika**. Tingnan ang [MT Evaluation](/docs/leaderboard/rules) para sa kung ano ang bumubuo sa mabuti vs. masamang method.
:::

---

## Tingnan Din

- [MT Evaluation](/docs/leaderboard/rules) — overview, value proposition ng leaderboard, at gabay sa mabuti/masamang method
- [Evaluation Datasets](/docs/leaderboard/datasets) — dataset format, EDTeKLA, FLORES+
- [Espesipikasyon ng Run Card](/docs/specifications/run-card) — ang buong JSON schema
- [Pagbuo ng Method](/docs/specifications/methods) — ang method interface para sa paglikha ng mga method na maaaring i-evaluate
- [Method Leaderboard](https://champollion.dev/leaderboard) — mga live benchmark score
- [Espesipikasyon ng Benchmark](/docs/specifications/benchmark) — evaluation protocol, corpus format, schema ng run card
- [Espesipikasyon sa Scoring](/docs/specifications/scoring) — SSOT para sa metrics, composite weights, at quality tiers