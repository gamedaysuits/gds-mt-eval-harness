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

> **Samenvatting.** Deze pagina behandelt de installatie, configuratie en het gebruik van de MT-evaluatieharness — het hulpmiddel dat vertaalmethoden benchmarkt aan de hand van gestandaardiseerde corpora en gescoorde run cards produceert. Voor canonieke definities van metrische waarden, schema's en het evaluatieprotocol, zie de [Benchmark Specification](/docs/specifications/benchmark).

De harness voert vertaalexperimenten uit en produceert run cards. De harness verzorgt de opbouw van prompts, API-aanroepen, scoring en serialisatie van resultaten — u levert de dataset en het model.

## Installatie

**Vereisten:** Python 3.10+

```bash
pip install sacrebleu aiohttp
```

Kloon de harness-repository:

```bash
git clone https://github.com/gamedaysuits/arena.git
cd arena
```

## Gebruik

```bash
mt-eval run --corpus path/to/dataset.json
```

Dit verwerkt elk item in het corpus via het geconfigureerde model (of de methode-plugin), scoort de uitvoer en schrijft een run card JSON-bestand naar de uitvoermap.

## CLI-vlaggen

### `mt-eval run`

| Vlag | Vereist | Standaard | Beschrijving |
|------|---------|-----------|--------------|
| `--corpus` | ✅ | — | Pad naar corpusbestand (`.json`, `.jsonl`, `.tsv`) |
| `--source-file` / `--reference-file` | — | — | Parallelle tekstbestanden (FLORES+, WMT-formaat) |
| `-m, --model` | — | `gemini-pro` | Model-slug (korte naam of volledig OpenRouter-ID). Wordt omgezet via `shared/model-aliases.json`. Door komma's gescheiden voor runs met meerdere modellen |
| `-d, --dataset` | — | `all` | Datasetfilter: `all`, segmentnaam of ID-bereik |
| `--ids` | — | — | Door komma's gescheiden item-ID's om te evalueren |
| `--source-lang` | — | `English` | Naam van de brontaal |
| `--target-lang` | — | — | Naam van de doeltaal |
| `-p, --prompt` | — | `naive` | Promptversie (`naive`, `custom`, `champollion`) |
| `--coaching-file` | — | — | Pad naar tekstbestand met coaching-prompt |
| `--coaching` | — | — | Inline coaching-tekst (geciteerde tekenreeks) |
| `--method` | — | — | Pad naar map met methode-plugin (bevat `method.json` + Python-module) |
| `--method-card` | — | — | Pad naar methode card JSON voor leaderboard-metadata |
| `--fst-retries` | — | `0` | Aantal FST-herpogingen (alleen standaard LLM-methode) |
| `--skip-fst` | — | `false` | FST-kwaliteitspoort volledig overslaan |
| `--tools` | — | `false` | Modus voor tool-aanroepen inschakelen |
| `--tools-list` | — | — | Door komma's gescheiden toolnamen |
| `--max-tool-rounds` | — | `8` | Maximum aantal tool-aanroepronden per item |
| `--hooks` | — | — | Namen van post-vertaalhooks |
| `--style-profile` | — | — | Pad naar een stijlprofiel JSON. Schakelt metrische waarden voor schrijfstijlconsistentie in (informatief — nooit onderdeel van de composite score; zie [§ Schrijfstijl- en registermetrische waarden](#writing-style-and-register-metrics-informational)) |
| `-b, --batch-size` | — | `25` | Items per API-aanroep |
| `-c, --concurrency` | — | `8` | Parallelle API-aanroepen |
| `--max-tokens` | — | `32768` | Maximum aantal tokens per API-aanroep |
| `--temperature` | — | `0.0` | Bemonsteringstemperatuur (0.0 = deterministisch) |
| `--no-cache` | — | `false` | Responscaching uitschakelen |
| `--cache-dir` | — | `eval/cache/harness` | Pad naar cachemap |
| `-o, --output-dir` | — | `eval/logs/harness` | Uitvoermap voor run cards en logbestanden |
| `-n, --name` | — | — | Leesbare naam voor de run |
| `--dry-run` | — | `false` | Configuratie valideren zonder API-aanroepen te doen |
| `--champollion-config` | — | — | Pad naar `champollion.config.json` |
| `--champollion-cards-dir` | — | — | Map met taalkaarten |
| `--target-lang-code` | — | — | BCP-47-taalcode |

### Overige subcommando's

| Subcommando | Beschrijving |
|-------------|--------------|
| `mt-eval test <log_path>` | Een voltooide run-log analyseren |
| `mt-eval publish <report_path>` | Een run card indienen bij het leaderboard |
| `mt-eval compare <logs...>` | Meerdere runs naast elkaar vergelijken |
| `mt-eval dashboard <logs...>` | Een HTML-dashboard genereren vanuit run-logs |
| `mt-eval list models\|prompts\|datasets` | Beschikbare resources weergeven |
| `mt-eval export` | De huidige configuratie verpakken als een champollion-methode-plugin |
| `mt-eval export-config` | De omgezette MethodConfig (alle 8 canonieke velden) exporteren als JSON |

### Voorbeelden

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

## Run Card-schema

Elk experiment produceert een **run card** — een op zichzelf staand JSON-document. De structuur op het hoogste niveau:

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

Zie de [Run Card Specification](/docs/specifications/run-card) voor het volledige schema met elk veld gedocumenteerd.

:::info Gezaghebbend schema
De [Benchmark Specification](/docs/specifications/benchmark) is de enige bron van waarheid voor het run card-schema. Voor metrische definities, composite-gewichten en kwaliteitsniveaus, zie de [Scoring Specification](/docs/specifications/scoring). Deze pagina documenteert het gebruik van de harness; de specificaties definiëren wat de uitvoer betekent.
:::

### Belangrijke blokken

**`dataset`** — Identificeert welke dataset is gebruikt, inclusief de content-hash zodat resultaten aan een specifieke versie zijn gekoppeld:

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

**`scores`** — Geaggregeerde metrische waarden voor de run:

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

**`totals`** — Bijhouden van tokengebruik en kosten:

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

## Schrijfstijl- en registermetrische waarden (informatief)

De harness kan evalueren of vertalingen overeenkomen met een doelgericht **register** en een bepaalde **schrijfstijl**, via de `WritingStyleConsistency`-metrische plugin (`mt_eval_harness/plugins/writing_style.py`). Een vertaling kan taalkundig correct zijn maar in het verkeerde register staan — informele formuleringen in een juridisch document, formele standaardtekst in marketingmateriaal — en tekenreeksmetrische waarden zullen dit niet opmerken. Deze metrische waarden wel.

**Wat er wordt gemeten (per item):**

| Metrische waarde | Schaal | Betekenis |
|-----------------|--------|-----------|
| `style_register_match` | booleaans | Komt de uitvoer overeen met het verwachte register? Het doel is afkomstig uit het veld `register` van het corpusitem (zie [Benchmark Spec §2.6](/docs/specifications/benchmark)) of uit een stijlprofiel |
| `style_sentence_length_ratio` | float | Voorspelde versus referentie gemiddelde zinslengte (1.0 = overeenkomst; afwijking = stijldrift) |
| `style_formality_score` | 0.0–1.0 | Aanwezigheid van formele/informele markers (T–V-voornaamwoorden, samentrekkingen, …) met behulp van taalspecifieke markerresources |

**Geaggregeerd:** `style_consistency_rate` — het aandeel items zonder gedetecteerde registermismatch.

Schakel een aangepast doel in met `--style-profile path/to/profile.json` (bijv. een merkstemprofiel); zonder dit valt de plugin terug op de `register`-metadata van elk corpusitem, indien aanwezig.

:::caution Eerlijke afbakening
Deze metrische waarden zijn **uitsluitend informatief** — ze maken nooit deel uit van de composite score, en de formaliteitsdetectie is op markers gebaseerd (een heuristiek), geen aangeleerd oordeel. Beschouw ze als een driftdetector voor registerconformiteit, niet als een uitspraak over stijlkwaliteit.
:::

---

## Vingerafdruk versus run card-hash

De harness produceert twee afzonderlijke hashes. Ze dienen verschillende doeleinden:

### Vingerafdruk

De **vingerafdruk** beantwoordt de vraag: *"Kan deze run worden gereproduceerd?"*

De vingerafdruk hasht de combinatie van invoergegevens die de experimentconfiguratie definiëren — niet de uitvoer:

- Dataset SHA-256
- Model-slug
- Conditielabel
- Systeem-prompt SHA-256
- Temperatuur
- Harness-versie

Twee runs met identieke vingerafdrukken hebben dezelfde configuratie gebruikt. Hun resultaten zouden vergelijkbaar moeten zijn (met uitzondering van API-niet-determinisme).

### Run card-hash

De **run card-hash** beantwoordt de vraag: *"Is dit specifieke resultaatbestand gemanipuleerd?"*

Het is de SHA-256 van het volledige run card JSON-bestand (exclusief het veld `run_card_hash` zelf). Als een veld wijzigt — een score, een tijdstempel, een enkele uitvoer — is de hash ongeldig.

:::info Wanneer welke te gebruiken
Gebruik de **vingerafdruk** om vergelijkbare runs te groeperen (hetzelfde experiment, verschillende uitvoeringen). Gebruik de **run card-hash** om de integriteit van een specifiek resultaatbestand te verifiëren.
:::

---

## Publiceren naar het leaderboard

Na het voltooien van een run gebruikt u `mt-eval publish` om de run card in te dienen:

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

Als er tijdens de run geen `--method-card` is opgegeven, start `mt-eval publish` een interactieve wizard (`method_card_wizard.py`) die u begeleidt bij het beschrijven van uw methode (naam, klasse, gebruikte tools, enz.). De uitvoer van de wizard wordt in de run card ingesloten vóór indiening.

### Handmatige indiening

Run cards worden opgeslagen als JSON-bestanden in de uitvoermap. U kunt ook elk run card-bestand indienen via de leaderboard-gebruikersinterface op [/leaderboard](https://champollion.dev/leaderboard), of via de API:

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning Leaderboard-validatie
Het leaderboard valideert ingediende run cards aan de hand van het datasetregister. Inzendingen die verwijzen naar onbekende datasets, of met een ongeldige `run_card_hash`, worden afgewezen.
:::

:::danger GEBRUIK GEEN evaluatiedata voor training
Als uw methode de evaluatiedataset tijdens de ontwikkeling heeft gezien — als trainingsdata, few-shot-voorbeelden, woordenboekitems of promptengineeringmateriaal — wordt uw inzending **gediskwalificeerd**. Zie [MT Evaluation](/docs/leaderboard/rules) voor wat een goede versus slechte methode inhoudt.
:::

---

## Zie ook

- [MT Evaluation](/docs/leaderboard/rules) — overzicht, de meerwaarde van het leaderboard en richtlijnen voor goede en slechte methoden
- [Evaluation Datasets](/docs/leaderboard/datasets) — datasetformaat, EDTeKLA, FLORES+
- [Run Card Specification](/docs/specifications/run-card) — het volledige JSON-schema
- [Building a Method](/docs/specifications/methods) — de methode-interface voor het maken van evalueerbare methoden
- [Method Leaderboard](https://champollion.dev/leaderboard) — live benchmarkscores
- [Benchmark Specification](/docs/specifications/benchmark) — evaluatieprotocol, corpusformaat, run card-schema
- [Scoring Specification](/docs/specifications/scoring) — SSOT voor metrische waarden, composite-gewichten en kwaliteitsniveaus