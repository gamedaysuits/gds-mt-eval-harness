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

> **Buod para sa Ehekutibo.** Saklaw ng pahinang ito ang pag-install, pagsasaayos, at paggamit ng MT evaluation harness — ang tool na nagbe-benchmark ng mga pamamaraan ng pagsasalin laban sa mga pamantayang corpus at gumagawa ng mga scored run card. Para sa mga kanonikal na depinisyon ng mga metric, schema, at protocol ng pagsusuri, tingnan ang [Benchmark Specification](/docs/specifications/benchmark).

Pinapatakbo ng harness ang mga eksperimento sa pagsasalin at gumagawa ito ng mga run card. Pinangangasiwaan nito ang pagbuo ng prompt, mga API call, scoring, at serialization ng resulta — ibinibigay ninyo ang dataset at ang model.

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

Pinapatakbo nito ang bawat entry sa corpus sa pamamagitan ng naka-configure na model (o method plugin), nagbibigay ng score sa mga output, at nagsusulat ng run card JSON file sa output directory.

## Mga CLI Flag

### `mt-eval run`

| Flag | Kinakailangan | Default | Paglalarawan |
|------|----------|---------|-------------|
| `--corpus` | ✅ | — | Path papunta sa corpus file (`.json`, `.jsonl`, `.tsv`) |
| `--source-file` / `--reference-file` | — | — | Mga parallel text file (FLORES+, WMT format) |
| `-m, --model` | — | `gemini-pro` | Model slug (maikling pangalan o buong OpenRouter ID). Nire-resolve sa pamamagitan ng `shared/model-aliases.json`. Pinaghihiwalay ng kuwit para sa mga multi-model run |
| `-d, --dataset` | — | `all` | Dataset filter: `all`, pangalan ng segment, o saklaw ng ID |
| `--ids` | — | — | Mga entry ID na pinaghihiwalay ng kuwit upang suriin |
| `--source-lang` | — | `English` | Pangalan ng source language |
| `--target-lang` | — | — | Pangalan ng target language |
| `-p, --prompt` | — | `naive` | Bersyon ng prompt (`naive`, `custom`, `champollion`) |
| `--coaching-file` | — | — | Path papunta sa coaching prompt text file |
| `--coaching` | — | — | Inline coaching text (quoted string) |
| `--method` | — | — | Path papunta sa method plugin directory (naglalaman ng `method.json` + Python module) |
| `--method-card` | — | — | Path papunta sa method card JSON para sa leaderboard metadata |
| `--fst-retries` | — | `0` | Bilang ng mga pagtatangkang FST retry (default na LLM method lamang) |
| `--skip-fst` | — | `false` | Laktawan nang buo ang FST quality gate |
| `--tools` | — | `false` | Paganahin ang tool-calling mode |
| `--tools-list` | — | — | Mga pangalan ng tool na pinaghihiwalay ng kuwit |
| `--max-tool-rounds` | — | `8` | Pinakamataas na bilang ng tool-calling rounds kada entry |
| `--hooks` | — | — | Mga pangalan ng post-translation hook |
| `--style-profile` | — | — | Path papunta sa isang style profile JSON. Pinapagana ang mga metric para sa consistency ng writing style (impormatibo — kailanman ay hindi bahagi ng composite score; tingnan ang [§ Mga metric ng estilo ng pagsulat at rehistro](#writing-style-and-register-metrics-informational)) |
| `-b, --batch-size` | — | `25` | Mga entry kada API call |
| `-c, --concurrency` | — | `8` | Mga parallel API call |
| `--max-tokens` | — | `32768` | Pinakamataas na tokens kada API call |
| `--temperature` | — | `0.0` | Sampling temperature (0.0 = deterministic) |
| `--no-cache` | — | `false` | I-disable ang response caching |
| `--cache-dir` | — | `eval/cache/harness` | Path ng cache directory |
| `-o, --output-dir` | — | `eval/logs/harness` | Output directory para sa mga run card at log |
| `-n, --name` | — | — | Run name na madaling basahin ng tao |
| `--dry-run` | — | `false` | I-validate ang configuration nang hindi gumagawa ng mga API call |
| `--champollion-config` | — | — | Path papunta sa `champollion.config.json` |
| `--champollion-cards-dir` | — | — | Directory ng mga language card |
| `--target-lang-code` | — | — | BCP-47 language code |

### Iba Pang Subcommand

| Subcommand | Paglalarawan |
|------------|-------------|
| `mt-eval test <log_path>` | Suriin ang isang nakumpletong run log |
| `mt-eval publish <report_path>` | Magsumite ng run card sa leaderboard |
| `mt-eval compare <logs...>` | Ihambing ang maraming run nang magkatabi |
| `mt-eval dashboard <logs...>` | Bumuo ng HTML dashboard mula sa mga run log |
| `mt-eval list models\|prompts\|datasets` | Ilista ang mga available na resource |
| `mt-eval export` | I-package ang kasalukuyang setup bilang champollion method plugin |
| `mt-eval export-config` | I-export ang resolved MethodConfig (lahat ng 8 kanonikal na field) bilang JSON |

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

## Run Card Schema

Bawat eksperimento ay gumagawa ng **run card** — isang self-contained na JSON document. Ang top-level structure:

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

Tingnan ang [Run Card Specification](/docs/specifications/run-card) para sa buong schema na may dokumentasyon para sa bawat field.

:::info Awtoritatibong Schema
Ang [Benchmark Specification](/docs/specifications/benchmark) ang nag-iisang source of truth para sa run card schema. Para sa mga depinisyon ng metric, composite weights, at quality tiers, tingnan ang [Scoring Specification](/docs/specifications/scoring). Idinodokumento ng pahinang ito kung paano gamitin ang harness; tinutukoy ng mga spec kung ano ang ibig sabihin ng mga output.
:::

### Mahahalagang Block

**`dataset`** — Tinutukoy kung aling dataset ang ginamit, kabilang ang content hash nito upang maikabit ang mga resulta sa isang partikular na bersyon:

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

**`scores`** — Mga aggregate metric para sa run:

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

**`totals`** — Pagsubaybay sa paggamit ng token at gastos:

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

## Mga metric ng estilo ng pagsulat at rehistro (impormatibo)

Maaaring suriin ng harness kung tumutugma ang mga pagsasalin sa target na **rehistro** at **writing style**, sa pamamagitan ng `WritingStyleConsistency` metric plugin (`mt_eval_harness/plugins/writing_style.py`). Maaaring tama ang isang pagsasalin sa aspektong lingguwistiko ngunit nasa maling rehistro — impormal na pananalita sa isang legal na dokumento, pormal na boilerplate sa marketing copy — at hindi ito mapapansin ng mga string metric. Napapansin ito ng mga metric na ito.

**Ano ang sinusukat (kada entry):**

| Metric | Scale | Kahulugan |
|--------|-------|---------|
| `style_register_match` | boolean | Tumutugma ba ang output sa inaasahang rehistro? Nagmumula ang target sa field na `register` ng corpus entry (tingnan ang [Benchmark Spec §2.6](/docs/specifications/benchmark)) o mula sa isang style profile |
| `style_sentence_length_ratio` | float | Predicted vs reference average sentence length (1.0 = tugma; divergence = style drift) |
| `style_formality_score` | 0.0–1.0 | Presensya ng mga pormal/impormal na marker (T–V pronouns, contractions, …) gamit ang per-language marker resources |

**Aggregate:** `style_consistency_rate` — ang fraction ng mga entry na walang natukoy na register mismatch.

Paganahin ang custom target gamit ang `--style-profile path/to/profile.json` (hal. isang brand-voice profile); kung wala nito, babalik ang plugin sa metadata na `register` ng bawat corpus entry kung naroroon.

:::caution Matapat na saklaw
Ang mga metric na ito ay **impormatibo lamang** — kailanman ay hindi sila bahagi ng composite score, at ang formality detection ay marker-based (isang heuristic), hindi isang learned judgment. Ituring ang mga ito bilang drift detector para sa pagsunod sa rehistro, hindi bilang hatol sa kalidad ng estilo.
:::

---

## Fingerprint vs Run Card Hash {#fingerprint-vs-run-card-hash}

Gumagawa ang harness ng dalawang magkahiwalay na hash. Magkaiba ang layunin ng mga ito:

### Fingerprint

Sinasagot ng **fingerprint** ang: *"Maaari bang ma-reproduce ang run na ito?"*

Hina-hash nito ang kombinasyon ng mga input na tumutukoy sa configuration ng eksperimento — hindi ang mga output:

- Dataset SHA-256
- Model slug
- Condition label
- System prompt SHA-256
- Temperature
- Bersyon ng harness

Dalawang run na may magkaparehong fingerprint ang gumamit ng parehong setup. Dapat maihambing ang kanilang mga resulta (maliban sa API non-determinism).

### Run Card Hash

Sinasagot ng **run card hash** ang: *"Nabago ba nang hindi awtorisado ang partikular na result file na ito?"*

Ito ang SHA-256 ng buong run card JSON (hindi kasama ang field na `run_card_hash` mismo). Kung may magbago sa alinmang field — isang score, isang timestamp, isang output — masisira ang hash.

:::info Kailan gagamitin ang alin
Gamitin ang **fingerprint** upang ipangkat ang mga maihahambing na run (parehong eksperimento, magkakaibang execution). Gamitin ang **run card hash** upang i-verify ang integridad ng isang partikular na result file.
:::

---

## Pag-publish sa Leaderboard

Pagkatapos makumpleto ang isang run, gamitin ang `mt-eval publish` upang isumite ang run card:

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

Kung walang ibinigay na `--method-card` sa panahon ng run, maglulunsad ang `mt-eval publish` ng interactive wizard (`method_card_wizard.py`) na gagabay sa inyo sa paglalarawan ng inyong method (pangalan, klase, mga tool na ginamit, atbp.). Isinasama ang output ng wizard sa run card bago isumite.

### Manu-manong pagsusumite

Sine-save ang mga run card bilang mga JSON file sa output directory. Maaari rin ninyong isumite ang anumang run card file sa pamamagitan ng leaderboard UI sa [/leaderboard](https://champollion.dev/leaderboard), o sa pamamagitan ng API:

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning Pag-validate ng leaderboard
Vina-validate ng leaderboard ang mga isinumiteng run card laban sa dataset registry. Tinatanggihan ang mga submission na tumutukoy sa mga hindi kilalang dataset, o may sirang `run_card_hash`.
:::

:::danger HUWAG MAG-TRAIN sa evaluation data
Kung nakita na ng inyong method ang evaluation dataset sa panahon ng development — bilang training data, few-shot examples, dictionary entries, o prompt engineering material — ang inyong submission ay **madidisqualify**. Tingnan ang [MT Evaluation](/docs/leaderboard/rules) para sa kung ano ang bumubuo sa mabuti vs. masamang method.
:::

---

## Tingnan Din

- [MT Evaluation](/docs/leaderboard/rules) — pangkalahatang-ideya, value proposition ng leaderboard, at gabay sa mabuti/masamang method
- [Evaluation Datasets](/docs/leaderboard/datasets) — dataset format, EDTeKLA, FLORES+
- [Run Card Specification](/docs/specifications/run-card) — ang buong JSON schema
- [Building a Method](/docs/specifications/methods) — ang method interface para sa paglikha ng mga method na maaaring suriin
- [Method Leaderboard](https://champollion.dev/leaderboard) — mga live benchmark score
- [Benchmark Specification](/docs/specifications/benchmark) — evaluation protocol, corpus format, run card schema
- [Scoring Specification](/docs/specifications/scoring) — SSOT para sa mga metric, composite weights, at quality tiers