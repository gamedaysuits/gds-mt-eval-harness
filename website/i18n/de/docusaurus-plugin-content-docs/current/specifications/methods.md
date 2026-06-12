---
sidebar_position: 4
title: "Methodenschnittstelle"
related:
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
    note: "Put this interface on the leaderboard"
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
    note: "A full method, built end-to-end"
---
# Gemeinsame Methodenschnittstelle

> **Zusammenfassung.** Diese Seite spezifiziert das `TranslationMethod`-Protokoll, das alle Arena-Methoden implementieren müssen, die sechs Methodenklassen (`raw-llm`, `coached-llm`, `pipeline`, `custom-plugin`, `api`, `human`), das Methoden-Plugin-Format sowie die **Abhängigkeitsklassen** (S/O/A1/A2/X), die bestimmen, ob eine Methode in der Evaluations-Sandbox ausgeführt werden und sich für Preise qualifizieren kann. Jeder Ansatz, der dieses Protokoll implementiert, kann einem Benchmark unterzogen werden; wovon er abhängt, bestimmt, wo er antreten kann.

Das Eval-Harness und champollion teilen ein gemeinsames Konzept der **Übersetzungsmethode**. Eine Methode ist jedes Verfahren, das Quelltext entgegennimmt und übersetzten Text erzeugt – sei es ein direkter LLM-Aufruf, eine mehrstufige Pipeline, eine Drittanbieter-API oder eine menschliche Übersetzerin bzw. ein menschlicher Übersetzer.

## Architektur

```
Method Plugin (v2 Spec)
├── method.json           ← Manifest (name, class, entry_point, dependencies, metadata)
├── method_card.json      ← Leaderboard description (what, not how)
├── pipeline.py           ← Python module implementing TranslationMethod
└── (optional helpers)    ← Additional Python modules
```

Geladen über `--method path/to/dir`. Das Harness erkennt nichts automatisch.

## Zwei Systeme, eine Schnittstelle

| | Eval-Harness | champollion |
|---|---|---|
| **Sprache** | Python | Node.js |
| **Einstiegspunkt** | `translate.py` | `translate.js` |
| **Schnittstelle** | `TranslationMethod`-Protokoll | `methodPlugin`-Konfiguration |
| **Zweck** | Batch-Evaluation mit Bewertung | Live-Lokalisierung in Dev/CI |
| **Ausgabe** | Run-Card mit Metriken | Übersetzte Locale-Dateien |

Eine Methode, die beide Systeme unterstützt, stellt zwei Einstiegspunkte bereit – einen für jede Sprachlaufzeitumgebung. Die **Methodenkarte** ist die Brücke: Sie beschreibt die Methode in einem Format, das beide Systeme verstehen.

## Methodenkarte

Eine Methodenkarte beschreibt, *was* eine Übersetzungsmethode ist, ohne proprietäre Details wie den vollständigen Systemprompt preiszugeben. Sie beantwortet folgende Fragen:

- Welcher Methodenklasse gehört dies an? (Raw-LLM, Coached-LLM, Pipeline, API usw.)
- Welche Werkzeuge verwendet sie? (FST-Analysetool, Wörterbuch usw.)
- Ist die Implementierung quelloffen?
- Welche Sprachpaare unterstützt sie?

Siehe die [Methodenkarten-Spezifikation](/docs/specifications/methods#method-card) für das vollständige JSON-Schema.

### Beispiel

```json
{
  "method_id": "fst-gated-v8",
  "name": "FST-Gated Coached Translation v8",
  "class": "pipeline",
  "description": "LLM translation with morphological validation. Failed words are retried with FST feedback.",
  "author": "Curtis Forbes",
  "tools_used": ["HFST morphological analyzer", "Wolvengrey dictionary"],
  "open_source": false,
  "dependency_class": "A2",
  "supported_pairs": ["eng>crk"]
}
```

Das Feld `dependency_class` fasst zusammen, was die Methode zur Ausführung und Übertragung benötigt – siehe [Methodengültigkeit und Abhängigkeitsklassen](#method-validity-and-dependency-classes) weiter unten.

### Methodenklassen

| Klasse | Beschreibung |
|-------|-------------|
| `raw-llm` | Direkter LLM-Aufruf mit minimaler Anweisung |
| `coached-llm` | LLM mit strukturiertem Prompt, Beispielen, Beschränkungen |
| `pipeline` | Mehrstufige Pipeline mit deterministischen Komponenten |
| `custom-plugin` | Externer Prozess, der das `TranslationMethod`-Protokoll implementiert |
| `api` | Drittanbieter-Übersetzungs-API (Google Translate, DeepL usw.) |
| `human` | Menschliche Übersetzung (zur Festlegung von Baselines) |

## Methodengültigkeit und Abhängigkeitsklassen

Eine Methode ist nur so ausführbar und nur so übertragbar wie ihre am wenigsten verfügbare Abhängigkeit. Zwei Arena-Mechanismen sind darauf angewiesen, genau zu wissen, was eine Methode benötigt:

1. **Sandbox-Evaluation** ([Benchmark-Spezifikation §8.2](/docs/specifications/benchmark)) – offizielle Goldstandard-Bewertungen stammen aus einer Sandbox, deren Netzwerkrichtlinie **standardmäßig verweigernd** (default-deny) ist. Eine Methode, die stillschweigend einen externen Dienst erfordert, kann keine offizielle Bewertung erzeugen.
2. **Preisübertragung** ([Preis-Spezifikation](/docs/specifications/prizes)) – preisgekrönte Methoden werden an die Governance-Organisation der Sprachgemeinschaft übertragen. Eine Methode, die Inhalte bündelt, zu deren Aufnahme die einreichende Person nicht berechtigt war, kann nicht rechtmäßig übertragen werden. Die einreichende Person muss die Rechte an allem im Paket besitzen (oder erhalten).

Um beide Prüfungen mechanisch statt ad hoc zu gestalten, deklariert jede Methode eine **Abhängigkeitsklasse**, die aus einem **Abhängigkeitsmanifest** in `method.json` abgeleitet wird.

> **Hinweis zur Benennung.** *Methodenklasse* (siehe oben: `raw-llm`, `pipeline`, …) beschreibt, *wie eine Methode übersetzt*. *Abhängigkeitsklasse* (dieser Abschnitt) beschreibt, *was eine Methode zur Ausführung und Übertragung benötigt*. Es handelt sich um unabhängige Achsen: Eine `pipeline`-Methode kann jeder beliebigen Abhängigkeitsklasse angehören.

### Die fünf Abhängigkeitsklassen

| Klasse | Name | Definition | Sandbox-ausführbar? | Preisberechtigt? |
|-------|------|-----------|-------------------|-----------------|
| **S** | Eigenständig | Sämtlicher Code, alle Daten, Modelle und Gewichte werden innerhalb des Methodenverzeichnisses ausgeliefert, unter Lizenzen, die Weiterverbreitung und Übertragung an die Gemeinschaft erlauben. | ✅ Ja, unverändert | ✅ Ja |
| **O** | Offen extern | Hängt von extern gehosteten Artefakten unter offenen Lizenzen ab, die Weiterverbreitung erlauben (einschließlich Copyleft-Lizenzen wie AGPL) – z. B. ein FST, der zur Installationszeit heruntergeladen wird. | ✅ Ja – Artefakte werden gepinnt und **in die Einreichung gespiegelt** | ✅ Ja, unter Bedingungen zur Lizenzkompatibilität: Copyleft-Bedingungen bleiben durch die Übertragung hinweg erhalten, und die Gemeinschaft erhält dieselben Rechte, die die Lizenz allen gewährt |
| **A1** | API-abhängig, ersetzbar | Erfordert LLM-Inferenz zur Laufzeit, wobei das Modell **ersetzbare Konfiguration** ist – jedes hinreichend leistungsfähige Modell kann eingesetzt werden. Der Wert der Methode liegt in ihren Prompts, Coaching-Daten und ihrem Code, nicht im Modell eines einzelnen Anbieters. | ⚠️ Nur über das **LLM-Gateway**, das die Sandbox-Spezifikation definiert (🔲 geplant – siehe unten) | ⚠️ Bedingt – siehe unten |
| **A2** | API-abhängig, nicht ersetzbar | Erfordert Laufzeitaufrufe an eine externe Daten- oder Dienst-API, die nicht gespiegelt oder ersetzt werden kann – typischerweise, weil der bereitgestellte Inhalt proprietär oder unlizenziert ist (z. B. eine Wörterbuch-API, deren zugrunde liegendes Wörterbuch keine öffentliche Lizenz besitzt). | ❌ Nein – die Abhängigkeit kann in der Sandbox ohne die Erlaubnis der Rechteinhaberin bzw. des Rechteinhabers nicht existieren | ❌ Nicht, bis die Rechteinhaberin bzw. der Rechteinhaber die Sandbox-Aufnahme **und** Übertragungsberechtigungen gewährt. Zulässig auf der offenen Bestenliste (Entwicklungssegment) mit einem sichtbaren **„externe Abhängigkeit“**-Kennzeichen |
| **X** | Geschlossen | Bündelt Inhalte, zu deren Weiterverbreitung die einreichende Person nicht berechtigt ist – unlizenzierte Datensätze, gescrapte proprietäre Inhalte, lizenzinkompatible Komponenten. | ❌ | ❌ In jeder Bahn unzulässig. Das Bündeln von Inhalten ohne Rechte ist ein Lizenzverstoß, unabhängig davon, wo die Methode läuft |

**Effektive Klasse.** Die Abhängigkeitsklasse einer Methode ist die *restriktivste* Klasse unter all ihren deklarierten Abhängigkeiten, in der Reihenfolge S < O < A1 < A2 < X. Ein einziges unlizenziertes Wörterbuch macht eine ansonsten eigenständige Pipeline zur Klasse A2 (bei Zugriff zur Laufzeit) oder zur Klasse X (bei Bündelung ohne Rechte).

### Die A1/A2-Unterscheidung: Ersetzbarkeit

Die meisten Methoden rufen LLMs auf. Die Arena tut nicht so, als wäre dem nicht so – doch sie unterscheidet zwei sehr verschiedene Arten von API-Abhängigkeit:

- **A1 (ersetzbar):** Die API stellt LLM-Inferenz als Standardware bereit. Die Modellkennung ist Konfiguration: Die Methode muss durchgängig gegen jeden kompatiblen Inferenz-Endpunkt laufen, einschließlich eines von der Gemeinschaft gehosteten Open-Weight-Modells. Die Ausgabequalität kann zwischen Modellen variieren – das ist das Risiko der Entwicklerin bzw. des Entwicklers, und offizielle Bewertungen sind an das in der Evaluation verwendete, gepinnte Modell gebunden. Eine Methode, die von **anbieterseitigem Zustand** abhängt (ein nur beim Anbieter gehostetes Fine-Tune, anbieterseitige Dateispeicher, anbieterspezifische Assistenten), ist *nicht* ersetzbar: Dieser Zustand lässt sich nicht austauschen, sodass die Abhängigkeit A2 ist, sofern nicht die zugrunde liegenden Gewichte oder Daten in der Einreichung enthalten sind.
- **A2 (nicht ersetzbar):** Die API stellt etwas Einzigartiges bereit – typischerweise proprietäre oder unlizenzierte Daten. Kein alternativer Endpunkt kann dies bereitstellen, und der Inhalt kann ohne die Erlaubnis der Rechteinhaberin bzw. des Rechteinhabers nicht in die Sandbox gespiegelt werden. Die Methode funktioniert auf der offenen Bestenliste (gekennzeichnet), kann jedoch keine offiziellen Sandbox-Bewertungen erzeugen oder sich für Preise qualifizieren, bis entsprechende Berechtigungen vorliegen.

**Was eine A1-Preisübertragung tatsächlich vermittelt.** Die Gemeinschaft erhält nicht das Modell – niemand kann die Gewichte von Anthropic, Google oder OpenAI übertragen. Die Übertragung umfasst das vollständige Rezept *rund um* das Modell: alle Prompts, Coaching-Daten, den Pipeline-Code, die Wiederholungslogik, die Konfiguration und die dokumentierten Modellanforderungen. Da das Modell konstruktionsbedingt ersetzbar ist, kann die Gemeinschaft die übertragene Methode auf jeden beliebigen Anbieter ihrer Wahl ausrichten – oder auf ein Open-Weight-Modell auf eigener Hardware – ohne Beteiligung der Entwicklerin bzw. des Entwicklers. Das Rezept gehört einem; die Maschine ist gemietet und austauschbar.

### Abhängigkeitsmanifest (`method.json`)

Jede Methode deklariert ihre Abhängigkeiten im `method.json`-Manifest. Jeder Eintrag erfasst, was das Artefakt ist, woher es stammt, welche Lizenz es abdeckt und wie die Methode darauf zugreift:

```json
{
  "name": "FST-Gated Coached Translation v8",
  "method_id": "fst-gated-v8",
  "class": "pipeline",
  "entry_point": "pipeline:PipelineMethod",
  "supported_pairs": ["eng>crk"],
  "dependency_class": "A2",
  "dependencies": [
    {
      "id": "giellalt-lang-crk-fst",
      "kind": "software",
      "license": "AGPL-3.0-or-later",
      "access": "mirrored",
      "source": "https://github.com/giellalt/lang-crk",
      "pin": "sha256:3f1a…",
      "redistributable": true,
      "transferable": true
    },
    {
      "id": "llm-inference",
      "kind": "model",
      "license": "proprietary",
      "access": "gateway",
      "source": "openrouter:google/gemini-2.5-flash",
      "substitutable": true,
      "redistributable": false,
      "transferable": false,
      "notes": "Any compatible chat-completions endpoint works; the model slug is configuration."
    },
    {
      "id": "crk-dictionary-api",
      "kind": "service",
      "license": "none",
      "access": "external-api",
      "source": "https://itwewina.altlab.app/",
      "redistributable": false,
      "transferable": false,
      "notes": "Dictionary content has no public license; runtime lookups only. Class A2 until the rights holders grant permission."
    }
  ]
}
```

| Feld | Erforderlich | Beschreibung |
|-------|----------|-------------|
| `id` | ✅ | Stabile Kennung für die Abhängigkeit |
| `kind` | ✅ | `data`, `model`, `software` oder `service` |
| `license` | ✅ | SPDX-Kennung, `proprietary` oder `none`. `none` bedeutet, dass keine öffentliche Lizenz existiert – wird als „alle Rechte vorbehalten“ behandelt |
| `access` | ✅ | `bundled` (wird im Methodenverzeichnis ausgeliefert), `mirrored` (zur Installationszeit abgerufen, gepinnt, in die Einreichung eingebunden), `gateway` (LLM-Inferenz zur Laufzeit über das Evaluations-Gateway), `external-api` (jeder andere Netzwerkaufruf zur Laufzeit) |
| `source` | ✅ | Kanonische URL oder `provider:slug`-Kennung |
| `pin` | für `mirrored` | Version, Commit oder Content-Hash, der das exakte Artefakt pinnt |
| `substitutable` | für `gateway`/`external-api` | Ob ein beliebiger kompatibler Endpunkt diese Abhängigkeit bereitstellen kann |
| `redistributable` | ✅ | Ob die Lizenz die Weiterverbreitung des Artefakts erlaubt |
| `transferable` | ✅ | Ob das Artefakt (oder die Rechte daran) im Rahmen der Preisübertragungsbedingungen an eine Gemeinschaft übertragen werden kann |
| `notes` | ❌ | Freier Kontext |

**Klassenableitung.** Jede Abhängigkeit trägt eine Klasse bei; die `dependency_class` der Methode ist die restriktivste:

| Abhängigkeitsprofil | Trägt bei |
|--------------------|-------------|
| `bundled` + Lizenz erlaubt Weiterverbreitung und Übertragung | S |
| `mirrored` + offene Lizenz, die Weiterverbreitung erlaubt (Copyleft eingeschlossen) | O |
| `gateway` + `substitutable: true` (LLM-Inferenz) | A1 |
| `external-api` oder `gateway` mit `substitutable: false` | A2 |
| `bundled` + `license: none` oder mit Weiterverbreitung inkompatible Lizenz | X |

Die deklarierte `dependency_class` muss der Klasse entsprechen, die das Harness aus dem Manifest ableitet. Eine Diskrepanz ist ein Validierungsfehler.

Eine Methode **ohne** externe Abhängigkeiten deklariert `"dependency_class": "S"` und `"dependencies": []`. Das leere Array ist eine affirmative Aussage, die wie jede andere geprüft wird.

### Wie die Gültigkeit verifiziert wird

Drei Ebenen, von der günstigsten zur maßgeblichsten:

1. **Manifest-Prüfung.** Das Harness leitet die effektive Klasse aus dem Manifest ab und weist Diskrepanzen zurück. Prüfende vergleichen jede deklarierte Abhängigkeit mit ihrer angegebenen Lizenz und Quelle – eine als `redistributable: true` deklarierte Abhängigkeit, deren Upstream-Lizenz etwas anderes besagt, besteht die Prüfung nicht.
2. **Statische Analyse.** Eingereichter Code wird auf Netzwerkaufrufe, dynamische Downloads und Dateisystemzugriffe gescannt, die das Manifest nicht berücksichtigt. Eine in der Prüfung gefundene *nicht deklarierte* Abhängigkeit ist ein Ablehnungsgrund, unabhängig davon, welcher Klasse sie angehört hätte – das Manifest muss vollständig sein, nicht nur korrekt.
3. **Sandbox-Netzwerkrichtlinie.** Die Sandbox-Spezifikation erfordert **standardmäßig verweigernden Egress** (default-deny): Methoden-Container erhalten keinen Netzwerkzugriff, sofern nicht ein Pfad explizit auf die Zulassungsliste gesetzt wird. Der einzige Egress-Pfad, den die Spezifikation definiert, ist das **LLM-Gateway** – ein Inferenz-Proxy, der von der Evaluationsinfrastruktur betrieben wird, beschränkt auf eine explizite Zulassungsliste gepinnter Modelle, wobei jede Anfrage und Antwort für die Nachprüfung nach dem Lauf protokolliert wird. Alles, was nicht auf der Zulassungsliste steht, scheitert auf der Netzwerkebene, nicht auf der Richtlinienebene. Siehe [Benchmark-Spezifikation §8.6](/docs/specifications/benchmark) für die Netzwerkrichtlinie und das Gateway-Design.

> 🔲 **Geplant.** Die Sandbox und ihr LLM-Gateway sind spezifiziert, aber noch nicht gebaut. Bis das Gateway betriebsbereit ist, können nur Methoden der Klasse S und der Klasse O in der Sandbox evaluiert werden; Methoden der Klasse A1 sind *grundsätzlich* preisberechtigt, können aber noch keine offiziellen Goldstandard-Bewertungen erzeugen. Diese Seite beschreibt, was die Spezifikation erfordert, nicht, was derzeit läuft.

### Anzeige auf der Bestenliste

- Die Bestenliste zeigt die Abhängigkeitsklasse jeder Methode neben ihrem Methodenklassen-Abzeichen an.
- Methoden der Klasse A2 auf der offenen Bestenliste tragen ein sichtbares **„externe Abhängigkeit“**-Kennzeichen: Ihre Bewertungen hängen von einem Drittanbieterdienst ab, der sich ändern oder verschwinden kann, und sie sind derzeit nicht preisberechtigt.
- Methoden der Klasse X werden nicht gelistet.

## Eval-Harness: TranslationMethod-Protokoll

Das Eval-Harness verwendet Pythons strukturelle Typisierung (`Protocol`) für Plugins. Jede Klasse mit der richtigen Methodensignatur funktioniert – keine Vererbung erforderlich:

```python
class MyMethod:
    async def translate(self, entries: list[dict], config: RunConfig) -> list[dict]:
        results = []
        for entry in entries:
            translation = await self.do_translation(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translation,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "error": None,
                "tool_calls": [],
                "tool_call_count": 0,
                "metadata": {},
            })
        return results
```

Siehe das [Plugin-Protokoll](/docs/specifications/methods#eval-harness-translationmethod-protocol) für die vollständige Dokumentation, einschließlich Wrapper-Beispielen für Nicht-Python-Methoden.

## champollion: methodPlugin-Konfiguration

In champollion werden Methoden pro Sprachpaar in `champollion.config.json` registriert:

```json
{
  "version": 3,
  "pairs": {
    "en:crk": {
      "methodPlugin": "crk-coached-v1"
    }
  }
}
```

Siehe die [Plugin-Spezifikation](https://champollion.dev/docs/reference/plugin-spec) für die champollion-seitige Schnittstelle.

## Bestenlisten-Integration

Wenn eine Methodenkarte an einen Lauf angehängt wird (über `--method-card`), wird sie in die Run-Card eingebettet und auf der Bestenliste angezeigt:

```bash
# Run with method card attached
mt-eval run \
  --method path/to/my-method \
  --corpus data/edtekla-dev-v1.json \
  --method-card method_card.json

# Publish to the leaderboard
mt-eval publish eval/logs/harness/your-run-card.json
```

Wenn keine `--method-card` angegeben wurde, startet `mt-eval publish` einen interaktiven Assistenten, der Sie durch die Beschreibung Ihrer Methode führt.

Die Bestenliste zeigt:
- **Klassen-Abzeichen** – visuelle Anzeige (z. B. „pipeline“, „coached-llm“)
- **Abhängigkeitsklasse** – S/O/A1/A2 (siehe [Methodengültigkeit und Abhängigkeitsklassen](#method-validity-and-dependency-classes)); A2-Methoden tragen ein „externe Abhängigkeit“-Kennzeichen
- **Methodenname** – aus der Methodenkarte
- **Verwendete Werkzeuge** – aus der Methodenkarte aufgelistet
- **Open-Source-Indikator**

Wenn keine Methodenkarte angehängt ist, zeigt die Bestenliste die harness-native Konfiguration an (Modell, Prompt-Version, Temperatur, aktivierte Werkzeuge).

:::danger KEIN TRAINING mit Evaluationsdaten
Methoden, deren Entwicklungsprozess eine Berührung mit dem Evaluationsdatensatz beinhaltete – als Trainingsdaten, Few-Shot-Beispiele, Wörterbucheinträge oder Material zum Prompt-Tuning –, werden von der Bestenliste **disqualifiziert**. Siehe [MT-Evaluation](/docs/leaderboard/rules) dazu, was eine gute Methode von einer schlechten unterscheidet.
:::

---

## Siehe auch

- [MT-Evaluation](/docs/leaderboard/rules) – Überblick, Bestenlisten-Wert und Leitfaden zu guten/schlechten Methoden
- [Eval-Harness](/docs/specifications/harness) – wie Evaluationen durchgeführt werden
- [Evaluationsdatensätze](/docs/leaderboard/datasets) – verfügbare Datensätze (EDTeKLA, FLORES+)
- [Run-Card-Spezifikation](/docs/specifications/run-card) – das JSON-Schema der Run-Card
- [Plugin-Spezifikation](https://champollion.dev/docs/reference/plugin-spec) – champollion-seitige Plugin-Schnittstelle
- [Methoden-Bestenliste](https://champollion.dev/leaderboard) – Live-Benchmark-Bewertungen
- [Benchmark-Spezifikation](/docs/specifications/benchmark) – Evaluationsprotokoll, Korpusformat, Run-Card-Schema
- [Scoring-Spezifikation](/docs/specifications/scoring) – SSOT für Metriken, Composite-Gewichtungen und Qualitätsstufen