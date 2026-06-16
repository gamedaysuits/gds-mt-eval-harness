---
sidebar_position: 3
title: "Mga Dataset para sa Ebalwasyon"
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
# Mga Dataset sa Evaluation

> **Executive Summary.** Inilalarawan ng pahinang ito ang mga evaluation dataset na available para sa benchmarking, kabilang ang corpus entry schema, mga difficulty tier (1–5), at mga kinakailangan sa provenance. Kasalukuyang available: EDTeKLA Dev v1 (Plains Cree, 548 kabuuang entry: 486 textbook + 62 gold standard) at FLORES+ Devtest (39 wika, tig-1,012 entry bawat isa).

Ang mga dataset ang mga nakapirming target na pinapatakbo ng harness. Bawat dataset ay isang JSON file na naglalaman ng mga pares na source→target na may gold-standard references. Sine-score ng harness ang mga output ng model laban sa mga reference na ito — hindi nito kailanman binabago ang mga ito.

:::danger HUWAG MAG-TRAIN sa evaluation data

⚠️ **Ang mga dataset na ito ay para lamang sa evaluation.** Ang mga method na na-train, na-fine-tune, na-few-shot-prompt, o sa anumang paraan ay nalantad sa evaluation data ay magbubunga ng artipisyal na pinataas na score at **madidisqualify mula sa leaderboard.**

Gumamit ng hiwalay na corpora para sa training. Dapat manatiling hindi nakikita ng inyong model ang mga evaluation set habang nagde-develop.
:::

---

## Format ng Dataset

Sinusunod ng bawat dataset ang parehong JSON schema:

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

:::info Kanonikal na Schema
Itinatakda ng [Benchmark Specification](/docs/specifications/benchmark) ang kanonikal na corpus at entry schema. Idinodokumento ng pahinang ito ang mga available na dataset at kung paano gumawa ng mga bago.
:::

### Bloke ng Top-Level `dataset`

| Patlang | Uri | Paglalarawan |
|-------|------|-------------|
| `id` | `string` | Natatanging identifier ng dataset (ginagamit sa mga run card at leaderboard) |
| `version` | `string` | Semantic version. Ang pag-increment nito ay nagpapawalang-bisa sa mga naunang paghahambing ng run card |
| `language_pair` | `string` | Display label (hal., `EN→CRK`) |
| `description` | `string` | Opsyonal. Buod na nababasa ng tao |
| `source_language` | `string` | BCP 47 source language code |
| `target_language` | `string` | BCP 47 target language code |
| `created` | `string` | ISO 8601 creation date |
| `license` | `string` | SPDX license identifier |
| `provenance` | `string[]` | Listahan ng mga provenance tag na ginagamit sa mga entry |

### Mga Patlang ng Entry

| Patlang | Uri | Kinakailangan | Paglalarawan |
|-------|------|----------|-------------|
| `id` | `integer` | ✅ | Natatanging identifier ng entry sa loob ng corpus |
| `source` | `string` | ✅ | Ang source text na isasalin |
| `reference` | `string` | ✅ | Ang gold-standard reference translation |
| `difficulty` | `integer` | ✅ | Difficulty tier 1–5 (tingnan sa ibaba) |
| `provenance` | `string` | ✅ | Pinagmulan ng entry na ito (hal., `gold_standard`, `textbook`, `elicited`) |
| `register` | `string` | ✅ | Antas ng register/formality (hal., `conversational`, `formal`, `ceremonial`) |
| `context` | `string` | ✅ | Komunikatibong tungkulin (hal., `greeting`, `declaration`, `instruction`) |
| `notes` | `string` | ❌ | Opsyonal na context para sa mga human reviewer |
| `morphological_analysis` | `string` | ❌ | Gold-standard morphological breakdown |
| `variant_class` | `string` | ❌ | Class label na nagpapangkat ng mga katanggap-tanggap na variant ng salin |

---

## Mga Available na Dataset

### EDTeKLA Development Set v1

Ang unang evaluation dataset, na binuo para sa pagsasaling English→Plains Cree (SRO). Nilikha ng [EdTeKLA research group](https://spaces.facsci.ualberta.ca/edtekla/) sa University of Alberta.

| Property | Value |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Bersyon** | `1.0` |
| **Pares ng wika** | EN → CRK (Plains Cree, SRO orthography) |
| **Bilang ng entry** | 548 kabuuan (486 textbook + 62 gold standard). Ang kanonikal na dev corpus ay `textbook_dev.json` (436 entry — ang buong textbook dev split mula sa 486 kabuuan: 436 dev + 50 held-out test) |
| **Distribusyon ng difficulty** | Madali, Katamtaman, Mahirap |
| **Provenance** | `gold_standard` (na-verify ng mga speaker), `textbook` (nailathalang educational materials) |
| **License** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |

**Ano ang sinusuri nito:**

- Mga pangunahing pagbati at karaniwang parirala
- Noun animacy at obviation
- Verb conjugation sa iba’t ibang person at tense
- Mga locative construction
- Possessive paradigms
- Mga kumplikadong istruktura ng pangungusap

:::tip Istruktura ng Corpus
Ang buong koleksyon ng EdTeKLA ay may 548 curated entry: 486 mula sa textbook corpus (436 dev + 50 held-out) at 62 mula sa itwêwina gold standard. Ang kanonikal na dev corpus ay `textbook_dev.json` na may 436 entry — ang buong textbook dev split. Bawat entry ay na-verify ng mga fluent speaker o kinuha mula sa nailathalang Cree language textbooks. Mas kapaki-pakinabang ang mas maliit at mataas ang kalidad na dataset na may na-verify na gold standards kaysa sa malaki ngunit maingay na dataset — lalo na para sa low-resource language kung saan ang mga saling "close enough" ay madalas na morphologically invalid.
:::

---

## Paglikha ng Bagong Dataset

Upang lumikha ng dataset para sa bagong pares ng wika o domain:

### 1. Istruktura ang JSON

Sundin ang schema sa [Format ng Dataset](#dataset-format). Bawat entry ay dapat may `source`, `reference`, `difficulty`, `provenance`, `register`, at `context`.

### 2. Magtalaga ng natatanging ID

Gumamit ng deskriptibong slug: `{project}-{split}-v{version}` (hal., `edtekla-dev-v1`, `quechua-test-v1`).

### 3. I-verify ang mga gold standard

Bawat value ng `reference` ay dapat ma-verify ng fluent speaker o makuha mula sa nailathala at peer-reviewed na resource. Sinisira ng machine-generated references ang layunin ng evaluation.

### 4. Itakda ang mga difficulty tier

Magtalaga sa bawat entry ng integer difficulty level:

| Tier | Paglalarawan | Mga Halimbawa |
|------|-------------|----------|
| 1 — Basic vocabulary | Mga iisang salita, karaniwang pagbati, numero | "hello" → "tânisi" |
| 2 — Simple sentences | Subject-verb o SVO, present tense | "I see the dog" |
| 3 — Moderate complexity | Past/future tense, possessives, animacy | "I saw his dog yesterday" |
| 4 — Complex morphology | Obviation, passive voice, conjunct order | "the woman whose son went to the store" |
| 5 — Advanced | Multi-clause, formal register, ceremonial, idiomatic | Buong talata na may register-appropriate na tono |

### 5. Lagyan ng tag ang provenance

Dapat ipahiwatig ng bawat entry kung saan ito nagmula. Mga karaniwang tag:

- `gold_standard` — Na-verify ng mga fluent speaker
- `textbook` — Mula sa nailathalang educational materials
- `elicited` — Ginawa sa pamamagitan ng structured elicitation sessions
- `corpus` — Kinuha mula sa parallel corpus

### 6. I-validate ang file

Patakbuhin ang harness laban sa inyong dataset gamit ang anumang model upang i-verify na maayos ang pagkaka-format ng JSON at naroroon ang lahat ng kinakailangang patlang:

```bash
python eval/baseline_experiment.py --dataset path/to/your-dataset.json
```

Mag-e-error ang harness kapag may kulang na mga patlang, duplicate indices, o mga paglabag sa schema.

### 7. Isumite para maisama

Magbukas ng pull request laban sa [eval harness repository](https://github.com/gamedaysuits/arena) kasama ang inyong dataset file sa directory na `data/`. Isama ang dokumentasyon ng inyong verification methodology at mga provenance source.

---

## FLORES+ Devtest

Isang broad-coverage multilingual benchmark na pinapanatili ng [Open Language Data Initiative (OLDI)](https://huggingface.co/datasets/openlanguagedata/flores_plus). Ginagamit para sa multi-model frontier benchmark ng champollion.

| Property | Value |
|----------|-------|
| **ID** | `flores-plus-devtest` |
| **Mga pares ng wika** | EN → 39 wika (lahat ng natural language na nakarehistro sa champollion) |
| **Bilang ng entry** | 1,012 pangungusap bawat wika |
| **License** | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| **Source** | Orihinal na Meta FLORES-200, ngayon ay pinapanatili ng OLDI |
| **Lokasyon** | Mga pre-extracted fixture sa `test/benchmark/fixtures/` sa main champollion repo |

:::danger Para lamang sa evaluation
Ang FLORES+ ay inilaan lamang para sa evaluation. Tahasang hinihiling ng mga curator na **huwag itong gamitin bilang training data**. Tiyaking hindi kasama ang nilalaman nito sa anumang training corpora.
:::

---

## Tingnan Din

- [MT Evaluation](/docs/leaderboard/rules) — pangkalahatang-ideya ng evaluation framework at leaderboard
- [Eval Harness](/docs/specifications/harness) — kung paano magpatakbo ng evaluations laban sa mga dataset na ito
- [Run Card Specification](/docs/specifications/run-card) — ang JSON schema para sa pagtatala ng mga resulta
- [Method Leaderboard](https://champollion.dev/leaderboard) — mga live na benchmark score
- [EdTeKLA Project](https://spaces.facsci.ualberta.ca/edtekla/) — ang research group ng University of Alberta sa likod ng Cree dataset