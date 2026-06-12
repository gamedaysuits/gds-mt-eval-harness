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

> **Zusammenfassung.** Diese Seite spezifiziert das `TranslationMethod`-Protokoll, das alle Arena-Methoden implementieren müssen, die sechs Methodenklassen (`raw-llm`, `coached-llm`, `pipeline`, `custom-plugin`, `api`, `human`), das Methoden-Plugin-Format sowie die **Abhängigkeitsklassen** (S/O/A1/A2/X), die bestimmen, ob eine Methode in der Evaluierungs-Sandbox ausgeführt werden kann und für Preise infrage kommt. Jeder Ansatz, der dieses Protokoll implementiert, kann einem Benchmark unterzogen werden; wovon er abhängt, bestimmt, wo er antreten kann.

Das Eval-Harness und champollion teilen ein gemeinsames Konzept der **Übersetzungsmethode**. Eine Methode ist jedes Verfahren, das Quelltext entgegennimmt und übersetzten Text erzeugt — sei es ein direkter LLM-Aufruf, eine mehrstufige Pipeline, eine Drittanbieter-API oder ein menschlicher Übersetzer.

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
| **Zweck** | Batch-Evaluierung mit Bewertung | Live-Lokalisierung in Dev/CI |
| **Ausgabe** | Run Card mit Metriken | Übersetzte Locale-Dateien |

Eine Methode, die beide Systeme unterstützt, stellt zwei Einstiegspunkte bereit — einen für jede Sprachlaufzeit. Die **Method Card** ist das Bindeglied: Sie beschreibt die Methode in einem Format, das beide Systeme verstehen.

## Method Card {#method-card}

Eine Method Card beschreibt, *was* eine Übersetzungsmethode ist, ohne proprietäre Details wie den vollständigen System-Prompt preiszugeben. Sie beantwortet:

- Welche Methodenklasse ist dies? (raw LLM, coached LLM, Pipeline, API usw.)
- Welche Werkzeuge verwendet sie? (FST-Analyzer, Wörterbuch usw.)
- Ist die Implementierung Open Source?
- Welche Sprachpaare unterstützt sie?

Das vollständige JSON-Schema finden Sie in der [Method-Card-Spezifikation](/docs/specifications/methods#method-card).

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

Das Feld `dependency_class` fasst zusammen, was die Methode zur Ausführung und Übertragung benötigt — siehe [Methodengültigkeit und Abhängigkeitsklassen](#method-validity-and-dependency-classes) weiter unten.

### Methodenklassen

| Klasse | Beschreibung |
|-------|-------------|
| `raw-llm` | Direkter LLM-Aufruf mit minimaler Anweisung |
| `coached-llm` | LLM mit strukturiertem Prompt, Beispielen, Einschränkungen |
| `pipeline` | Mehrstufige Pipeline mit deterministischen Komponenten |
| `custom-plugin` | Externer Prozess, der das `TranslationMethod`-Protokoll implementiert |
| `api` | Drittanbieter-Übersetzungs-API (Google Translate, DeepL usw.) |
| `human` | Menschliche Übersetzung (zur Festlegung von Baselines) |

## Methodengültigkeit und Abhängigkeitsklassen {#method-validity-and-dependency-classes}

Eine Methode ist nur so ausführbar und nur so übertragbar wie ihre am wenigsten verfügbare Abhängigkeit. Zwei Arena-Mechanismen hängen davon ab, genau zu wissen, was eine Methode benötigt:

1. **Sandbox-Evaluierung** ([Benchmark-Spezifikation §8.2](/docs/specifications/benchmark)) — offizielle Goldstandard-Bewertungen stammen aus einer Sandbox, deren Netzwerkrichtlinie **standardmäßig auf Verweigern (default-deny)** eingestellt ist. Eine Methode, die stillschweigend einen externen Dienst voraussetzt, kann keine offizielle Bewertung erzeugen.
2. **Preisübertragung** ([Preis-Spezifikation](/docs/specifications/prizes)) — preisgekrönte Methoden gehen an die Governance-Organisation der Sprachgemeinschaft über. Eine Methode, die Inhalte bündelt, zu deren Einbindung der Einreichende nicht berechtigt war, kann nicht rechtmäßig übertragen werden. Der Einreichende muss die Rechte an allem im Paket besitzen (oder ihm müssen diese eingeräumt worden sein).

Um beide Prüfungen mechanisch statt ad hoc zu gestalten, deklariert jede Methode eine **Abhängigkeitsklasse**, die aus einem **Abhängigkeitsmanifest** in `method.json` abgeleitet wird.

> **Hinweis zur Benennung.** Die *Methodenklasse* (§oben: `raw-llm`, `pipeline`, …) beschreibt, *wie eine Methode übersetzt*. Die *Abhängigkeitsklasse* (dieser Abschnitt) beschreibt, *was eine Methode zur Ausführung und Übertragung benötigt*. Es handelt sich um unabhängige Achsen: Eine `pipeline`-Methode kann jeder beliebigen Abhängigkeitsklasse angehören.

### Die fünf Abhängigkeitsklassen

| Klasse | Name | Definition | In Sandbox ausführbar? | Preisberechtigt? |
|-------|------|-----------|-------------------|-----------------|
| **S** | Self-contained | Sämtlicher Code, alle Daten, Modelle und Gewichte werden innerhalb des Methodenverzeichnisses ausgeliefert, unter Lizenzen, die Weiterverbreitung und Community-Übertragung erlauben. | ✅ Ja, unverändert | ✅ Ja |
| **O** | Open external | Hängt von extern gehosteten Artefakten unter offenen Lizenzen ab, die eine Weiterverbreitung erlauben (einschließlich Copyleft-Lizenzen wie AGPL) — z. B. einem FST, das zur Installationszeit heruntergeladen wird. | ✅ Ja — Artefakte werden gepinnt und **in die Einreichung gespiegelt** | ✅ Ja, unter Bedingungen der Lizenzkompatibilität: Copyleft-Bedingungen bleiben über die Übertragung hinweg erhalten, und die Community erhält dieselben Rechte, die die Lizenz jedem einräumt |
| **A1** | API-dependent, substitutable | Erfordert LLM-Inferenz zur Laufzeit, wobei das Modell **austauschbare Konfiguration** ist — jedes hinreichend leistungsfähige Modell kann eingesetzt werden. Der Wert der Methode liegt in ihren Prompts, Coaching-Daten und im Code, nicht im Modell eines einzelnen Anbieters. | ⚠️ Nur über das **LLM-Gateway**, das die Sandbox-Spezifikation definiert (🔲 geplant — siehe unten) | ⚠️ Bedingt — siehe unten |
| **A2** | API-dependent, non-substitutable | Erfordert Laufzeitaufrufe an eine externe Daten- oder Dienst-API, die nicht gespiegelt oder ersetzt werden kann — typischerweise, weil der bereitgestellte Inhalt proprietär oder unlizenziert ist (z. B. eine Wörterbuch-API, deren zugrunde liegendes Wörterbuch über keine öffentliche Lizenz verfügt). | ❌ Nein — die Abhängigkeit kann ohne Erlaubnis des Rechteinhabers nicht in der Sandbox existieren | ❌ Nicht, bis der Rechteinhaber die Aufnahme in die Sandbox **und** Übertragungsberechtigungen gewährt. Auf der offenen Bestenliste (Entwicklungssegment) mit einer sichtbaren **„external dependency"**-Kennzeichnung zulässig |
| **X** | Closed | Bündelt Inhalte, zu deren Weiterverbreitung der Einreichende nicht berechtigt ist — unlizenzierte Datensätze, gescrapte proprietäre Inhalte, lizenzinkompatible Komponenten. | ❌ | ❌ In jeder Bahn unzulässig. Das Bündeln von Inhalten ohne Rechte ist eine Lizenzverletzung, unabhängig davon, wo die Methode ausgeführt wird |

**Effektive Klasse.** Die Abhängigkeitsklasse einer Methode ist die *restriktivste* Klasse unter all ihren deklarierten Abhängigkeiten, in der Reihenfolge S < O < A1 < A2 < X. Ein einziges unlizenziertes Wörterbuch macht aus einer ansonsten in sich geschlossenen Pipeline eine Klasse-A2-Methode (bei Zugriff zur Laufzeit) oder eine Klasse-X-Methode (bei Bündelung ohne Rechte).

### Die A1/A2-Unterscheidung: Austauschbarkeit

Die meisten Methoden rufen LLMs auf. Die Arena gibt nicht vor, dass dem nicht so wäre — aber sie unterscheidet zwei sehr unterschiedliche Arten von API-Abhängigkeit:

- **A1 (austauschbar):** Die API stellt Standard-LLM-Inferenz bereit. Der Modellbezeichner ist Konfiguration: Die Methode muss durchgängig gegen jeden kompatiblen Inferenz-Endpunkt funktionieren, einschließlich eines von der Community gehosteten Open-Weight-Modells. Die Ausgabequalität kann zwischen Modellen variieren — das ist das Risiko des Entwicklers, und offizielle Bewertungen sind an das gepinnte Modell gebunden, das in der Evaluierung verwendet wird. Eine Methode, die von **anbieterseitigem Zustand** abhängt (ein nur beim Anbieter gehostetes Fine-Tune, anbieterseitige Dateispeicher, anbieterspezifische Assistenten), ist *nicht* austauschbar: Dieser Zustand kann nicht ausgetauscht werden, sodass die Abhängigkeit A2 ist, es sei denn, die zugrunde liegenden Gewichte oder Daten sind in der Einreichung enthalten.
- **A2 (nicht austauschbar):** Die API stellt etwas Einzigartiges bereit — typischerweise proprietäre oder unlizenzierte Daten. Kein alternativer Endpunkt kann dies bereitstellen, und der Inhalt kann ohne Erlaubnis des Rechteinhabers nicht in die Sandbox gespiegelt werden. Die Methode funktioniert auf der offenen Bestenliste (gekennzeichnet), kann jedoch keine offiziellen Sandbox-Bewertungen erzeugen oder für Preise infrage kommen, bis entsprechende Berechtigungen vorliegen.

**Was eine A1-Preisübertragung tatsächlich vermittelt.** Die Community erhält nicht das Modell — niemand kann die Gewichte von Anthropic, Google oder OpenAI übertragen. Die Übertragung umfasst das vollständige Rezept *rund um* das Modell: alle Prompts, Coaching-Daten, Pipeline-Code, Wiederholungslogik, Konfiguration und dokumentierten Modellanforderungen. Da das Modell konstruktionsbedingt austauschbar ist, kann die Community die übertragene Methode auf jeden beliebigen Anbieter ausrichten — oder auf ein Open-Weight-Modell auf eigener Hardware — ohne Beteiligung des Entwicklers. Das Rezept ist im Besitz; der Motor ist gemietet und ersetzbar.

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
| `id` | ✅ | Stabiler Bezeichner für die Abhängigkeit |
| `kind` | ✅ | `data`, `model`, `software` oder `service` |
| `license` | ✅ | SPDX-Bezeichner, `proprietary` oder `none`. `none` bedeutet, dass keine öffentliche Lizenz existiert — wird als „alle Rechte vorbehalten" behandelt |
| `access` | ✅ | `bundled` (wird im Methodenverzeichnis ausgeliefert), `mirrored` (zur Installationszeit abgerufen, gepinnt, in die Einreichung eingebunden), `gateway` (LLM-Inferenz zur Laufzeit über das Evaluierungs-Gateway), `external-api` (jeder andere Netzwerkaufruf zur Laufzeit) |
| `source` | ✅ | Kanonische URL oder `provider:slug`-Bezeichner |
| `pin` | für `mirrored` | Version, Commit oder Inhalts-Hash, der das exakte Artefakt pinnt |
| `substitutable` | für `gateway`/`external-api` | Ob ein beliebiger kompatibler Endpunkt diese Abhängigkeit bereitstellen kann |
| `redistributable` | ✅ | Ob die Lizenz die Weiterverbreitung des Artefakts erlaubt |
| `transferable` | ✅ | Ob das Artefakt (oder Rechte daran) im Rahmen der Preisübertragungsbedingungen an eine Community übertragen werden kann |
| `notes` | ❌ | Freiform-Kontext |

**Klassenableitung.** Jede Abhängigkeit trägt eine Klasse bei; die `dependency_class` der Methode ist die restriktivste:

| Abhängigkeitsprofil | Trägt bei |
|--------------------|-------------|
| `bundled` + Lizenz erlaubt Weiterverbreitung und Übertragung | S |
| `mirrored` + offene Lizenz, die Weiterverbreitung erlaubt (Copyleft eingeschlossen) | O |
| `gateway` + `substitutable: true` (LLM-Inferenz) | A1 |
| `external-api` oder `gateway` mit `substitutable: false` | A2 |
| `bundled` + `license: none` oder weiterverbreitungsinkompatible Lizenz | X |

Die deklarierte `dependency_class` muss mit der Klasse übereinstimmen, die das Harness aus dem Manifest ableitet. Eine Abweichung ist ein Validierungsfehler.

Eine Methode mit **keinen** externen Abhängigkeiten deklariert `"dependency_class": "S"` und `"dependencies": []`. Das leere Array ist eine affirmative Aussage, die wie jede andere geprüft wird.

### Wie die Gültigkeit überprüft wird

Drei Ebenen, vom günstigsten zum verbindlichsten:

1. **Manifest-Prüfung.** Das Harness leitet die effektive Klasse aus dem Manifest ab und weist Abweichungen zurück. Prüfer gleichen jede deklarierte Abhängigkeit mit ihrer angegebenen Lizenz und Quelle ab — eine als `redistributable: true` deklarierte Abhängigkeit, deren Upstream-Lizenz etwas anderes besagt, besteht die Prüfung nicht.
2. **Statische Analyse.** Eingereichter Code wird auf Netzwerkaufrufe, dynamische Downloads und Dateisystemzugriffe untersucht, die das Manifest nicht berücksichtigt. Eine bei der Prüfung gefundene *nicht deklarierte* Abhängigkeit ist ein Ablehnungsgrund, unabhängig davon, welche Klasse sie gewesen wäre — das Manifest muss vollständig sein, nicht nur korrekt.
3. **Sandbox-Netzwerkrichtlinie.** Die Sandbox-Spezifikation erfordert **standardmäßiges Verweigern des ausgehenden Datenverkehrs (default-deny egress)**: Methoden-Container erhalten keinen Netzwerkzugriff, es sei denn, ein Pfad ist explizit auf der Allowlist eingetragen. Der einzige ausgehende Pfad, den die Spezifikation definiert, ist das **LLM-Gateway** — ein Inferenz-Proxy, der von der Evaluierungsinfrastruktur betrieben wird, auf eine explizite Allowlist gepinnter Modelle beschränkt ist und bei dem jede Anfrage und Antwort für eine nachträgliche Prüfung protokolliert wird. Alles, was nicht auf der Allowlist steht, scheitert auf der Netzwerkebene, nicht auf der Richtlinienebene. Die Netzwerkrichtlinie und das Gateway-Design finden Sie in der [Benchmark-Spezifikation §8.6](/docs/specifications/benchmark).

> 🔲 **Geplant.** Die Sandbox und ihr LLM-Gateway sind spezifiziert, aber noch nicht implementiert. Bis das Gateway betriebsbereit ist, können nur Methoden der Klassen S und O in der Sandbox evaluiert werden; Methoden der Klasse A1 sind *grundsätzlich* preisberechtigt, können jedoch noch keine offiziellen Goldstandard-Bewertungen erzeugen. Diese Seite beschreibt, was die Spezifikation erfordert, nicht das, was derzeit ausgeführt wird.

### Bestenlisten-Anzeige

- Die Bestenliste zeigt die Abhängigkeitsklasse jeder Methode neben ihrem Methodenklassen-Badge an.
- Methoden der Klasse A2 auf der offenen Bestenliste tragen eine sichtbare **„external dependency"**-Kennzeichnung: Ihre Bewertungen hängen von einem Drittanbieterdienst ab, der sich ändern oder verschwinden kann, und sie sind derzeit nicht preisberechtigt.
- Methoden der Klasse X werden nicht aufgeführt.

## Eval-Harness: TranslationMethod-Protokoll {#eval-harness-translationmethod-protocol}

Das Eval-Harness verwendet Pythons strukturelle Typisierung (`Protocol`) für Plugins. Jede Klasse mit der richtigen Methodensignatur funktioniert — keine Vererbung erforderlich:

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

Vollständige Dokumentation einschließlich Wrapper-Beispielen für Nicht-Python-Methoden finden Sie im [Plugin-Protokoll](/docs/specifications/methods#eval-harness-translationmethod-protocol).

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

Die champollion-seitige Schnittstelle finden Sie in der [Plugin-Spezifikation](https://champollion.dev/docs/reference/plugin-spec).

## Bestenlisten-Integration

Wenn eine Method Card an einen Lauf angehängt wird (über `--method-card`), wird sie in die Run Card eingebettet und auf der Bestenliste angezeigt:

```bash
# Run with method card attached
mt-eval run \
  --method path/to/my-method \
  --corpus data/edtekla-dev-v1.json \
  --method-card method_card.json

# Publish to the leaderboard
mt-eval publish eval/logs/harness/your-run-card.json
```

Wurde keine `--method-card` bereitgestellt, startet `mt-eval publish` einen interaktiven Assistenten, der Sie durch die Beschreibung Ihrer Methode führt.

Die Bestenliste zeigt:
- **Klassen-Badge** — visuelle Anzeige (z. B. „pipeline", „coached-llm")
- **Abhängigkeitsklasse** — S/O/A1/A2 (siehe [Methodengültigkeit und Abhängigkeitsklassen](#method-validity-and-dependency-classes)); A2-Methoden tragen eine „external dependency"-Kennzeichnung
- **Methodenname** — aus der Method Card
- **Verwendete Werkzeuge** — aus der Method Card aufgelistet
- **Open-Source-Indikator**

Wenn keine Method Card angehängt ist, zeigt die Bestenliste die harness-native Konfiguration an (Modell, Prompt-Version, Temperatur, aktivierte Werkzeuge).

:::danger NICHT mit Evaluierungsdaten TRAINIEREN
Methoden, deren Entwicklungsprozess Kontakt mit dem Evaluierungsdatensatz beinhaltete — als Trainingsdaten, Few-Shot-Beispiele, Wörterbucheinträge oder Material zur Prompt-Optimierung — werden von der Bestenliste **disqualifiziert**. Was eine gute von einer schlechten Methode unterscheidet, erfahren Sie unter [MT-Evaluierung](/docs/leaderboard/rules).
:::

---

## Siehe auch

- [MT-Evaluierung](/docs/leaderboard/rules) — Überblick, Bestenlisten-Wert und Leitfaden für gute/schlechte Methoden
- [Eval-Harness](/docs/specifications/harness) — wie Evaluierungen ausgeführt werden
- [Evaluierungsdatensätze](/docs/leaderboard/datasets) — verfügbare Datensätze (EDTeKLA, FLORES+)
- [Run-Card-Spezifikation](/docs/specifications/run-card) — das Run-Card-JSON-Schema
- [Plugin-Spezifikation](https://champollion.dev/docs/reference/plugin-spec) — champollion-seitige Plugin-Schnittstelle
- [Methoden-Bestenliste](https://champollion.dev/leaderboard) — Live-Benchmark-Bewertungen
- [Benchmark-Spezifikation](/docs/specifications/benchmark) — Evaluierungsprotokoll, Korpusformat, Run-Card-Schema
- [Scoring-Spezifikation](/docs/specifications/scoring) — SSOT für Metriken, zusammengesetzte Gewichtungen und Qualitätsstufen