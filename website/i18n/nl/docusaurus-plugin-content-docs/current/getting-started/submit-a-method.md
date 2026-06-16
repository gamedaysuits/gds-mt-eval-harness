---
sidebar_position: 1
title: "Een methode indienen"
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
# Een Methode Indienen

> **Samenvatting.** Een stapsgewijze quickstart voor het indienen van uw eerste benchmark-run op het leaderboard. Kloon de harness, voer deze uit tegen een dataset, bekijk uw run card en dien in. Duurt 10 minuten als u een API-sleutel heeft.

Deze handleiding begeleidt u bij het indienen van uw eerste benchmark-run op het MT Eval Arena-leaderboard.

---

## Vereisten

- **Python 3.10+**
- **Een OpenRouter API-sleutel** (of equivalent voor uw modelprovider)
- **Een vertaalmethode** — alles wat vertalingen produceert vanuit een brontekst

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## Stap 1: Voer de Harness Uit

De harness beoordeelt uw methode aan de hand van een gestandaardiseerde dataset:

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| Vlag | Functie |
|---|---|
| `--corpus` | Pad naar het evaluatiecorpus (`.json`, `.jsonl`, `.tsv`) |
| `--model` | Model-slug — korte alias (bijv. `gemini-pro`) of volledig OpenRouter-ID |
| `--condition` | Label voor uw methode (verschijnt op het leaderboard) |
| `--temperature` | Samplingtemperatuur (lager = meer deterministisch) |
| `--fst-retries` | Optioneel: aantal FST-pogingen bij herstart |
| `--submit` | Dien de run card automatisch in op het leaderboard |

De harness produceert een **run card** — een op zichzelf staand JSON-bestand met uw scores, de dataset-hash, de model-slug en een cryptografische vingerafdruk die de resultaten koppelt aan de exacte experimentconfiguratie.

---

## Stap 2: Bekijk Uw Run Card

Run cards worden opgeslagen in `results/`. Controleer de uwe vóór het indienen:

```bash
cat results/your-run-card.json | python -m json.tool
```

Belangrijke velden om te controleren:
- `scores.chrf_plus_plus` — uw primaire kwaliteitsmetriek
- `scores.exact_match_rate` — aandeel perfecte vertalingen
- `scores.fst_acceptance_rate` — morfologische geldigheid (indien FST werd gebruikt)
- `totals.total_cost_usd` — de kosten van de run
- `fingerprint` — de reproduceerbaarheidshash van het experiment

Zie de [Run Card-specificatie](/docs/specifications/run-card) voor het volledige schema.

---

## Stap 3: Indienen

### Automatisch indienen

Als u `--submit` heeft meegegeven bij het uitvoeren van de harness, is uw run card al geüpload.

### Handmatig indienen

Dien een run card in via de API:

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

Of upload via de [Leaderboard UI](https://champollion.dev/leaderboard).

---

## Wat Gebeurt Er Vervolgens

1. Uw inzending wordt gevalideerd (dataset-hash, integriteit van de run card)
2. Resultaten verschijnen op het leaderboard als **Zelf-gebenchmarkt** (vertrouwensniveau 1)
3. Voor de status **GDS Geverifieerd** dient u uw methode in als installeerbare plugin, zodat beheerders uw resultaten kunnen reproduceren
4. Voor methoden voor inheemse talen: als uw methode de top bereikt, wordt het proces voor [eigendomsoverdracht](/docs/sovereignty/ownership-transfer) gestart

---

## Zie Ook

- [Harness-gebruik](/docs/specifications/harness) — volledige CLI-referentie
- [Leaderboard-regels](/docs/leaderboard/rules) — indieningscriteria en anti-misbruikbeleid
- [Een Methode Bouwen](/docs/specifications/methods) — het TranslationMethod-protocol
- [Datasets](/docs/leaderboard/datasets) — beschikbare evaluatiedatasets