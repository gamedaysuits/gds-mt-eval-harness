---
sidebar_position: 3
title: "Evaluationsdatensätze"
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
# Evaluierungsdatensätze

> **Zusammenfassung.** Diese Seite beschreibt die für das Benchmarking verfügbaren Evaluierungsdatensätze, einschließlich des Schemas für Korpuseinträge, der Schwierigkeitsstufen (1–5) und der Anforderungen an die Provenienz. Aktuell verfügbar: EDTeKLA Dev v1 (Plains Cree, 548 Einträge insgesamt: 486 Lehrbuch + 62 Goldstandard) und FLORES+ Devtest (39 Sprachen, je 1.012 Einträge).

Datensätze sind die festen Ziele, gegen die das Harness läuft. Jeder Datensatz ist eine JSON-Datei, die Quell→Ziel-Paare mit Goldstandard-Referenzen enthält. Das Harness bewertet die Modellausgaben anhand dieser Referenzen — es verändert sie niemals.

:::danger TRAINIEREN SIE NICHT mit Evaluierungsdaten

⚠️ **Diese Datensätze dienen ausschließlich der Evaluierung.** Methoden, die mit Evaluierungsdaten trainiert, feinabgestimmt, mittels Few-Shot-Prompting eingesetzt oder anderweitig mit ihnen in Berührung gekommen sind, erzeugen künstlich überhöhte Werte und werden **von der Bestenliste ausgeschlossen.**

Verwenden Sie für das Training separate Korpora. Evaluierungssätze müssen während der Entwicklung für Ihr Modell ungesehen bleiben.
:::

---

## Datensatzformat

Jeder Datensatz folgt demselben JSON-Schema:

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

:::info Kanonisches Schema
Die [Benchmark-Spezifikation](/docs/specifications/benchmark) definiert das kanonische Korpus- und Eintragsschema. Diese Seite dokumentiert die verfügbaren Datensätze und wie neue erstellt werden.
:::

### Übergeordneter `dataset`-Block

| Feld | Typ | Beschreibung |
|-------|------|-------------|
| `id` | `string` | Eindeutige Datensatzkennung (verwendet in Run Cards und Bestenliste) |
| `version` | `string` | Semantische Version. Eine Erhöhung dieses Werts macht frühere Run-Card-Vergleiche ungültig |
| `language_pair` | `string` | Anzeigebezeichnung (z. B. `EN→CRK`) |
| `description` | `string` | Optional. Menschenlesbare Zusammenfassung |
| `source_language` | `string` | BCP-47-Quellsprachencode |
| `target_language` | `string` | BCP-47-Zielsprachencode |
| `created` | `string` | ISO-8601-Erstellungsdatum |
| `license` | `string` | SPDX-Lizenzkennung |
| `provenance` | `string[]` | Liste der über die Einträge hinweg verwendeten Provenienz-Tags |

### Eintragsfelder

| Feld | Typ | Erforderlich | Beschreibung |
|-------|------|----------|-------------|
| `id` | `integer` | ✅ | Eindeutige Eintragskennung innerhalb des Korpus |
| `source` | `string` | ✅ | Der zu übersetzende Quelltext |
| `reference` | `string` | ✅ | Die Goldstandard-Referenzübersetzung |
| `difficulty` | `integer` | ✅ | Schwierigkeitsstufe 1–5 (siehe unten) |
| `provenance` | `string` | ✅ | Herkunft dieses Eintrags (z. B. `gold_standard`, `textbook`, `elicited`) |
| `register` | `string` | ✅ | Register-/Formalitätsstufe (z. B. `conversational`, `formal`, `ceremonial`) |
| `context` | `string` | ✅ | Kommunikative Funktion (z. B. `greeting`, `declaration`, `instruction`) |
| `notes` | `string` | ❌ | Optionaler Kontext für menschliche Prüfer |
| `morphological_analysis` | `string` | ❌ | Goldstandard-Aufschlüsselung der Morphologie |
| `variant_class` | `string` | ❌ | Klassenbezeichnung zur Gruppierung akzeptabler Übersetzungsvarianten |

---

## Verfügbare Datensätze

### EDTeKLA Development Set v1

Der erste Evaluierungsdatensatz, erstellt für die Übersetzung Englisch→Plains Cree (SRO). Erstellt von der [EdTeKLA-Forschungsgruppe](https://spaces.facsci.ualberta.ca/edtekla/) an der University of Alberta.

| Eigenschaft | Wert |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Version** | `1.0` |
| **Sprachpaar** | EN → CRK (Plains Cree, SRO-Orthografie) |
| **Anzahl der Einträge** | 548 insgesamt (486 Lehrbuch + 62 Goldstandard). Das kanonische Dev-Korpus ist `textbook_dev.json` (436 Einträge — der vollständige Lehrbuch-Dev-Split von insgesamt 486: 436 Dev + 50 zurückgehaltener Test) |
| **Schwierigkeitsverteilung** | Easy, Medium, Hard |
| **Provenienz** | `gold_standard` (von Sprechern verifiziert), `textbook` (veröffentlichte Lehrmaterialien) |
| **Lizenz** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |

**Was geprüft wird:**

- Grundlegende Begrüßungen und gängige Phrasen
- Nomen-Belebtheit und Obviation
- Verbkonjugation über Personen und Zeitformen hinweg
- Lokativkonstruktionen
- Possessivparadigmen
- Komplexe Satzstrukturen

:::tip Korpusstruktur
Die vollständige EdTeKLA-Sammlung umfasst 548 kuratierte Einträge: 486 aus dem Lehrbuchkorpus (436 Dev + 50 zurückgehalten) und 62 aus dem itwêwina-Goldstandard. Das kanonische Dev-Korpus ist `textbook_dev.json` mit 436 Einträgen — der vollständige Lehrbuch-Dev-Split. Jeder Eintrag wurde von fließend sprechenden Personen verifiziert oder aus veröffentlichten Cree-Sprachlehrbüchern bezogen. Ein kleinerer, hochwertiger Datensatz mit verifizierten Goldstandards ist nützlicher als ein großer, verrauschter — insbesondere für eine ressourcenarme Sprache, in der „ausreichend nahe" Übersetzungen oft morphologisch ungültig sind.
:::

---

## Erstellung eines neuen Datensatzes

So erstellen Sie einen Datensatz für ein neues Sprachpaar oder eine neue Domäne:

### 1. Strukturieren Sie das JSON

Folgen Sie dem Schema [Datensatzformat](#dataset-format). Jeder Eintrag muss `source`, `reference`, `difficulty`, `provenance`, `register` und `context` enthalten.

### 2. Weisen Sie eine eindeutige ID zu

Verwenden Sie einen beschreibenden Slug: `{project}-{split}-v{version}` (z. B. `edtekla-dev-v1`, `quechua-test-v1`).

### 3. Verifizieren Sie die Goldstandards

Jeder `reference`-Wert muss von einer fließend sprechenden Person verifiziert oder aus einer veröffentlichten, von Fachleuten begutachteten Quelle bezogen werden. Maschinell erzeugte Referenzen verfehlen den Zweck der Evaluierung.

### 4. Legen Sie Schwierigkeitsstufen fest

Weisen Sie jedem Eintrag eine ganzzahlige Schwierigkeitsstufe zu:

| Stufe | Beschreibung | Beispiele |
|------|-------------|----------|
| 1 — Grundwortschatz | Einzelne Wörter, gängige Begrüßungen, Zahlen | „hello" → „tânisi" |
| 2 — Einfache Sätze | Subjekt-Verb oder SVO, Präsens | „I see the dog" |
| 3 — Mittlere Komplexität | Vergangenheit/Zukunft, Possessive, Belebtheit | „I saw his dog yesterday" |
| 4 — Komplexe Morphologie | Obviation, Passiv, Konjunktordnung | „the woman whose son went to the store" |
| 5 — Fortgeschritten | Mehrgliedrig, formelles Register, zeremoniell, idiomatisch | Vollständiger Absatz mit registergerechtem Ton |

### 5. Kennzeichnen Sie die Provenienz

Jeder Eintrag sollte angeben, woher er stammt. Gängige Tags:

- `gold_standard` — Von fließend sprechenden Personen verifiziert
- `textbook` — Aus veröffentlichten Lehrmaterialien
- `elicited` — Durch strukturierte Erhebungssitzungen erstellt
- `corpus` — Aus einem Parallelkorpus extrahiert

### 6. Validieren Sie die Datei

Führen Sie das Harness mit einem beliebigen Modell gegen Ihren Datensatz aus, um zu überprüfen, ob das JSON wohlgeformt ist und alle erforderlichen Felder vorhanden sind:

```bash
python eval/baseline_experiment.py --dataset path/to/your-dataset.json
```

Das Harness gibt bei fehlenden Feldern, doppelten Indizes oder Schemaverstößen einen Fehler aus.

### 7. Reichen Sie ihn zur Aufnahme ein

Öffnen Sie einen Pull Request gegen das [Eval-Harness-Repository](https://github.com/gamedaysuits/arena) mit Ihrer Datensatzdatei im Verzeichnis `data/`. Fügen Sie eine Dokumentation Ihrer Verifizierungsmethodik und Provenienzquellen bei.

---

## FLORES+ Devtest

Ein breit angelegter mehrsprachiger Benchmark, der von der [Open Language Data Initiative (OLDI)](https://huggingface.co/datasets/openlanguagedata/flores_plus) gepflegt wird. Wird für Champollions Multi-Model-Frontier-Benchmark verwendet.

| Eigenschaft | Wert |
|----------|-------|
| **ID** | `flores-plus-devtest` |
| **Sprachpaare** | EN → 39 Sprachen (alle bei champollion registrierten natürlichen Sprachen) |
| **Anzahl der Einträge** | 1.012 Sätze pro Sprache |
| **Lizenz** | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| **Quelle** | Ursprünglich Meta FLORES-200, jetzt von OLDI gepflegt |
| **Speicherort** | Vorextrahierte Fixtures unter `test/benchmark/fixtures/` im Haupt-Repo von champollion |

:::danger Nur zur Evaluierung
FLORES+ ist ausschließlich zur Evaluierung gedacht. Die Kuratoren bitten ausdrücklich darum, es **nicht als Trainingsdaten zu verwenden**. Stellen Sie sicher, dass seine Inhalte aus allen Trainingskorpora ausgeschlossen werden.
:::

---

## Siehe auch

- [MT-Evaluierung](/docs/leaderboard/rules) — Überblick über das Evaluierungsframework und die Bestenliste
- [Eval Harness](/docs/specifications/harness) — wie Sie Evaluierungen gegen diese Datensätze ausführen
- [Run-Card-Spezifikation](/docs/specifications/run-card) — das JSON-Schema zur Erfassung von Ergebnissen
- [Methoden-Bestenliste](https://champollion.dev/leaderboard) — Live-Benchmark-Werte
- [EdTeKLA-Projekt](https://spaces.facsci.ualberta.ca/edtekla/) — die Forschungsgruppe der University of Alberta hinter dem Cree-Datensatz