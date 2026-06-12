---
sidebar_position: 1
title: "Magsumite ng Pamamaraan"
related:
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
    note: "The contract your method implements"
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
    note: "What every published run must disclose"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
    note: "The fastest first method to submit"
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
---
# Magsumite ng Pamamaraan

> **Ehekutibong Buod.** Isang sunod-sunod na mabilisang panimula para sa pagsusumite ng inyong unang benchmark run sa leaderboard. I-clone ang harness, patakbuhin ito laban sa isang dataset, suriin ang inyong run card, at isumite. Aabutin ito ng 10 minuto kung mayroon kayong API key.

Ginagabayan kayo ng gabay na ito sa pagsusumite ng inyong unang benchmark run sa MT Eval Arena leaderboard.

---

## Mga Kinakailangan

- **Python 3.10+**
- **Isang OpenRouter API key** (o katumbas para sa inyong model provider)
- **Isang pamamaraan ng pagsasalin** — anumang gumagawa ng mga pagsasalin mula sa source text

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## Hakbang 1: Patakbuhin ang Harness

Sinusukat ng harness ang inyong pamamaraan laban sa isang estandardisadong dataset:

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| Flag | Ginagawa Nito |
|---|---|
| `--corpus` | Path patungo sa evaluation corpus (`.json`, `.jsonl`, `.tsv`) |
| `--model` | Model slug — maikling alias (hal. `gemini-pro`) o buong OpenRouter ID |
| `--condition` | Label para sa inyong pamamaraan (lumalabas sa leaderboard) |
| `--temperature` | Sampling temperature (mas mababa = mas deterministiko) |
| `--fst-retries` | Opsyonal: bilang ng mga pagtatangkang ulitin ng FST |
| `--submit` | Awtomatikong isumite ang run card sa leaderboard |

Gumagawa ang harness ng isang **run card** — isang nagsasariling JSON file na may inyong mga score, dataset hash, model slug, at kriptograpikong fingerprint na nag-uugnay ng mga resulta sa eksaktong configuration ng eksperimento.

---

## Hakbang 2: Suriin ang Inyong Run Card

Sine-save ang mga run card sa `results/`. Suriin ang sa inyo bago magsumite:

```bash
cat results/your-run-card.json | python -m json.tool
```

Mahahalagang field na dapat suriin:
- `scores.chrf_plus_plus` — ang inyong pangunahing quality metric
- `scores.exact_match_rate` — proporsyon ng mga perpektong pagsasalin
- `scores.fst_acceptance_rate` — morphological validity (kung ginamit ang FST)
- `totals.total_cost_usd` — gastos ng run
- `fingerprint` — reproducibility hash ng eksperimento

Tingnan ang [Run Card Specification](/docs/specifications/run-card) para sa kumpletong schema.

---

## Hakbang 3: Isumite

### Awtomatikong pagsusumite

Kung ipinasa ninyo ang `--submit` nang patakbuhin ang harness, na-upload na ang inyong run card.

### Manwal na pagsusumite

Isumite ang anumang run card sa pamamagitan ng API:

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

O mag-upload sa pamamagitan ng [Leaderboard UI](https://champollion.dev/leaderboard).

---

## Ano ang Susunod na Mangyayari

1. Vine-validate ang inyong pagsusumite (dataset hash, integridad ng run card)
2. Lumalabas ang mga resulta sa leaderboard bilang **Self-benchmarked** (trust tier 1)
3. Upang makakuha ng status na **GDS Verified**, isumite ang inyong pamamaraan bilang installable plugin upang magawang i-reproduce ng mga maintainer ang inyong mga resulta
4. Para sa mga pamamaraan para sa mga katutubong wika: kung umabot sa tuktok ang inyong pamamaraan, magsisimula ang proseso ng [paglilipat ng pagmamay-ari](/docs/sovereignty/ownership-transfer)

---

## Tingnan Din

- [Paggamit ng Harness](/docs/specifications/harness) — kumpletong CLI reference
- [Mga Panuntunan ng Leaderboard](/docs/leaderboard/rules) — pamantayan sa pagsusumite at mga patakaran laban sa gaming
- [Pagbuo ng Pamamaraan](/docs/specifications/methods) — ang TranslationMethod protocol
- [Mga Dataset](/docs/leaderboard/datasets) — mga available na evaluation dataset