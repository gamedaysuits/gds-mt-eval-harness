---
sidebar_position: 3
title: "Evaluatiedatasets"
related:
  - label: "Corpus Design Framework"
    to: /docs/specifications/corpus-design
    kind: spec
    note: "How evaluation corpora are constructed"
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "Build a corpus for your language"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
---
# Evaluatiedatasets

> **Samenvatting.** Deze pagina beschrijft de evaluatiedatasets die beschikbaar zijn voor benchmarking, inclusief het schema voor corpusinvoer, moeilijkheidsgraden (1–5) en herkomstvereisten. Momenteel beschikbaar: EDTeKLA Dev v1 (Plains Cree, 548 invoer in totaal: 486 leerboek + 62 goudstandaard) en FLORES+ Devtest (39 talen, 1.012 invoer per taal).

Datasets zijn de vaste doelbestanden waarop de harness wordt uitgevoerd. Elke dataset is een JSON-bestand met bron→doelparen en goudstandaardreferenties. De harness beoordeelt modeluitvoer aan de hand van deze referenties — deze worden nooit gewijzigd.

:::danger TRAIN NIET op evaluatiedata

⚠️ **Deze datasets zijn uitsluitend bedoeld voor evaluatie.** Methoden die zijn getraind, verfijnd, few-shot-geprompt of op een andere manier blootgesteld aan evaluatiedata produceren kunstmatig verhoogde scores en worden **gediskwalificeerd van het leaderboard.**

Gebruik afzonderlijke corpora voor training. Evaluatiesets mogen tijdens de ontwikkeling niet door uw model worden gezien.
:::

---

## Datasetformaat

Elke dataset volgt hetzelfde JSON-schema:

```json
{
  "dataset": {
    "id": "dataset-slug",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "description": "Human-readable description of the dataset",
    "source_language": "en",
    "target_language": "crk",
    "created": "2025-05-01",
    "license": "CC-BY-NC-4.0",
    "provenance": ["gold_standard", "textbook"]
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "tânisi",
      "difficulty": 1,
      "provenance": "gold_standard",
      "register": "conversational",
      "context": "greeting",
      "notes": "Common greeting, SRO orthography"
    }
  ]
}
```

:::info Canoniek schema
De [Benchmark Specification](/docs/specifications/benchmark) definieert het canonieke corpus- en invoerschema. Deze pagina documenteert beschikbare datasets en hoe u nieuwe kunt aanmaken.
:::

### Bovenste niveau `dataset` blok

| Veld | Type | Beschrijving |
|-------|------|-------------|
| `id` | `string` | Unieke dataset-identifier (gebruikt in run cards en leaderboard) |
| `version` | `string` | Semantische versie. Het verhogen hiervan maakt eerdere run card-vergelijkingen ongeldig |
| `language_pair` | `string` | Weergavelabel (bijv. `EN→CRK`) |
| `description` | `string` | Optioneel. Leesbare samenvatting |
| `source_language` | `string` | BCP 47-code voor de brontaal |
| `target_language` | `string` | BCP 47-code voor de doeltaal |
| `created` | `string` | ISO 8601-aanmaakdatum |
| `license` | `string` | SPDX-licentie-identifier |
| `provenance` | `string[]` | Lijst van herkomsttags die in invoer worden gebruikt |

### Invoervelden

| Veld | Type | Vereist | Beschrijving |
|-------|------|----------|-------------|
| `id` | `integer` | ✅ | Unieke invoer-identifier binnen het corpus |
| `source` | `string` | ✅ | De te vertalen brontekst |
| `reference` | `string` | ✅ | De goudstandaard referentievertaling |
| `difficulty` | `integer` | ✅ | Moeilijkheidsgraad 1–5 (zie hieronder) |
| `provenance` | `string` | ✅ | Herkomst van deze invoer (bijv. `gold_standard`, `textbook`, `elicited`) |
| `register` | `string` | ✅ | Register/formaliteitsniveau (bijv. `conversational`, `formal`, `ceremonial`) |
| `context` | `string` | ✅ | Communicatieve functie (bijv. `greeting`, `declaration`, `instruction`) |
| `notes` | `string` | ❌ | Optionele context voor menselijke beoordelaars |
| `morphological_analysis` | `string` | ❌ | Morfologische goudstandaardanalyse |
| `variant_class` | `string` | ❌ | Klasselabel dat acceptabele vertaalvarianten groepeert |

---

## Beschikbare datasets

### EDTeKLA Development Set v1

De eerste evaluatiedataset, opgebouwd voor Engels→Plains Cree (SRO)-vertaling. Gemaakt door de [EdTeKLA-onderzoeksgroep](https://spaces.facsci.ualberta.ca/edtekla/) aan de University of Alberta.

| Eigenschap | Waarde |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Versie** | `1.0` |
| **Taalpaar** | EN → CRK (Plains Cree, SRO-orthografie) |
| **Aantal invoer** | 548 in totaal (486 leerboek + 62 goudstandaard). Het canonieke dev-corpus is `textbook_dev.json` (436 invoer — de volledige leerboek-dev-splitsing van 486 in totaal: 436 dev + 50 achtergehouden test) |
| **Verdeling moeilijkheidsgraad** | Eenvoudig, Gemiddeld, Moeilijk |
| **Herkomst** | `gold_standard` (geverifieerd door sprekers), `textbook` (gepubliceerd educatief materiaal) |
| **Licentie** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |

**Wat het test:**

- Basisbegroetingen en veelgebruikte uitdrukkingen
- Naamwoordsanimasie en obviatie
- Werkwoordsvervoeging over personen en tijden
- Locatieve constructies
- Possessieve paradigma's
- Complexe zinsstructuren

:::tip Corpusstructuur
De volledige EdTeKLA-collectie bevat 548 gecureerde invoer: 486 uit het leerboekencorpus (436 dev + 50 achtergehouden) en 62 uit de itwêwina-goudstandaard. Het canonieke dev-corpus is `textbook_dev.json` met 436 invoer — de volledige leerboek-dev-splitsing. Elke invoer is geverifieerd door vloeiende sprekers of afkomstig uit gepubliceerde Cree-taalleerboeken. Een kleinere, hoogwaardige dataset met geverifieerde goudstandaarden is nuttiger dan een grote, ruisrijke — zeker voor een taal met weinig middelen waarbij "bijna correcte" vertalingen vaak morfologisch ongeldig zijn.
:::

---

## Een nieuwe dataset aanmaken

Om een dataset aan te maken voor een nieuw taalpaar of domein:

### 1. Structureer de JSON

Volg het schema uit [Datasetformaat](#dataset-format). Elke invoer moet `source`, `reference`, `difficulty`, `provenance`, `register` en `context` bevatten.

### 2. Wijs een unieke ID toe

Gebruik een beschrijvende slug: `{project}-{split}-v{version}` (bijv. `edtekla-dev-v1`, `quechua-test-v1`).

### 3. Verifieer goudstandaarden

Elke `reference`-waarde moet worden geverifieerd door een vloeiende spreker of afkomstig zijn uit een gepubliceerde, peer-reviewed bron. Door machines gegenereerde referenties ondermijnen het doel van evaluatie.

### 4. Stel moeilijkheidsgraden in

Wijs aan elke invoer een geheel getal als moeilijkheidsniveau toe:

| Graad | Beschrijving | Voorbeelden |
|------|-------------|----------|
| 1 — Basiswoordenschat | Losse woorden, veelgebruikte begroetingen, getallen | "hello" → "tânisi" |
| 2 — Eenvoudige zinnen | Onderwerp-werkwoord of SVO, tegenwoordige tijd | "I see the dog" |
| 3 — Gemiddelde complexiteit | Verleden/toekomstige tijd, possessieven, animasie | "I saw his dog yesterday" |
| 4 — Complexe morfologie | Obviatie, passieve vorm, conjunctvolgorde | "the woman whose son went to the store" |
| 5 — Gevorderd | Meerdere bijzinnen, formeel register, ceremonieel, idiomatisch | Volledige alinea met registerpassende toon |

### 5. Tag de herkomst

Elke invoer moet aangeven waar deze vandaan komt. Veelgebruikte tags:

- `gold_standard` — Geverifieerd door vloeiende sprekers
- `textbook` — Afkomstig uit gepubliceerd educatief materiaal
- `elicited` — Geproduceerd via gestructureerde elicitatiesessies
- `corpus` — Geëxtraheerd uit een parallel corpus

### 6. Valideer het bestand

Voer de harness uit op uw dataset met een willekeurig model om te controleren of de JSON correct is opgemaakt en alle vereiste velden aanwezig zijn:

```bash
python eval/baseline_experiment.py --dataset path/to/your-dataset.json
```

De harness geeft een foutmelding bij ontbrekende velden, dubbele indices of schemaschendingen.

### 7. Dien in voor opname

Open een pull request in de [eval harness-repository](https://github.com/gamedaysuits/arena) met uw datasetbestand in de map `data/`. Voeg documentatie toe over uw verificatiemethodologie en herkomstbronnen.

---

## FLORES+ Devtest

Een breedomvattende meertalige benchmark, onderhouden door het [Open Language Data Initiative (OLDI)](https://huggingface.co/datasets/openlanguagedata/flores_plus). Gebruikt voor de multi-model frontierbenchmark van champollion.

| Eigenschap | Waarde |
|----------|-------|
| **ID** | `flores-plus-devtest` |
| **Taalparen** | EN → 39 talen (alle bij champollion geregistreerde natuurlijke talen) |
| **Aantal invoer** | 1.012 zinnen per taal |
| **Licentie** | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| **Bron** | Oorspronkelijk Meta FLORES-200, nu onderhouden door OLDI |
| **Locatie** | Vooraf geëxtraheerde fixtures op `test/benchmark/fixtures/` in de hoofdrepository van champollion |

:::danger Uitsluitend voor evaluatie
FLORES+ is uitsluitend bedoeld voor evaluatie. De samenstellers verzoeken uitdrukkelijk dat het **niet als trainingsdata wordt gebruikt**. Zorg ervoor dat de inhoud ervan is uitgesloten van alle trainingscorpora.
:::

---

## Zie ook

- [MT Evaluation](/docs/leaderboard/rules) — overzicht van het evaluatieraamwerk en het leaderboard
- [Eval Harness](/docs/specifications/harness) — hoe u evaluaties uitvoert op deze datasets
- [Run Card Specification](/docs/specifications/run-card) — het JSON-schema voor het vastleggen van resultaten
- [Method Leaderboard](https://champollion.dev/leaderboard) — live benchmarkscores
- [EdTeKLA Project](https://spaces.facsci.ualberta.ca/edtekla/) — de onderzoeksgroep van de University of Alberta achter de Cree-dataset