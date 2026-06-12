---
sidebar_position: 2
title: "FAQ"
related:
  - label: "How It Works"
    to: /docs/how-it-works
    kind: doc
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Glossary"
    to: https://champollion.dev/glossary
    kind: glossary
    note: "Plain-language definitions for every technical term"
---
# Häufig gestellte Fragen

> **Zusammenfassung.** Antworten auf häufige Fragen zur MT Eval Arena — wie die Bewertung funktioniert, was zur Disqualifikation führt, wie mit Sprachen ohne FSTs umzugehen ist, Empfehlungen zu Modellen und Parametern sowie der Einreichungsprozess.

---

## Bewertung & Metriken

### Welche Metriken berechnet das Harness?

Das Harness berechnet fünf Metriken für Plains Cree (die aktuelle Benchmark-Sprache). Drei sind sprachunabhängig und funktionieren für jede Sprache; zwei stützen sich derzeit auf CRK-spezifische Plugins und werden verallgemeinert, sobald wir auf weitere Sprachen ausweiten.

| Metrik | Skala | Was sie misst | Status |
|--------|-------|-----------------|--------|
| **chrF++** | 0–100 | Überlappung von Zeichen-n-Grammen zwischen vorhergesagten und Referenzübersetzungen. Beste Oberflächenmetrik für morphologisch reiche Sprachen. Verwendet die native Bewertung von sacrebleu. | ✅ Alle Sprachen |
| **Exact match** | 0.0–1.0 | Anteil der Einträge, bei denen die Vorhersage nach Normalisierung exakt mit der Referenz übereinstimmt. | ✅ Alle Sprachen |
| **FST acceptance** | 0.0–1.0 | Anteil der Ausgabewörter, die von einem endlichen Zustandstransduktor (morphologischer Analysator) akzeptiert werden. Wird nur berechnet, wenn eine FST-Binärdatei bereitgestellt wird. | ✅ Alle Sprachen mit FST |
| **Equivalent match** | 0.0–1.0 | Anteil der Einträge, die mit der Referenz oder einer akzeptablen Variante übereinstimmen — unter Berücksichtigung von Wortstellung, orthografischer Konvention und dialektalen Unterschieden. | ⚡ CRK (wird verallgemeinert) |
| **Semantic score** | 0.0–1.0 | Bewertung der Bedeutungserhaltung — wie gut erfasst die Übersetzung die beabsichtigte Bedeutung unabhängig von der Oberflächenform? | ⚡ CRK (wird verallgemeinert) |

Weitere Metriken sind geplant: **morphologische Genauigkeit**, **Code-Switching-Erkennung**, **Terminologietreue** und **Halluzinationserkennung**. Siehe [Scoring Specification §2](/docs/specifications/scoring#2-metric-inventory) für das vollständige Inventar mit 19 Metriken.

### Wie wird der composite score berechnet?

Der composite score ist ein gewichteter Durchschnitt der verfügbaren Metriken, normalisiert auf eine Skala von 0.0–1.0. Die Gewichtungen sind in zwei Profilen definiert:

- **Profile A** (Sprachen mit FST): 9 Metriken, strukturelle Metriken (FST + morphologische Genauigkeit) tragen 40 % der Gesamtgewichtung
- **Profile B** (Sprachen ohne FST): 8 Metriken, Semantik und chrF++ tragen die gleiche höchste Gewichtung

Wenn eine Metrik nicht verfügbar ist, wird ihre Gewichtung proportional auf die verbleibenden Metriken umverteilt. Das bedeutet, dass Benchmarks in einem frühen Stadium (bei denen nur chrF++ und Exact match verfügbar sind) dennoch gültige composite scores erzeugen — die effektiven Gewichtungen spiegeln lediglich wider, was verfügbar ist.

**Die vollständigen Gewichtungstabellen, Normalisierungsregeln und die Begründung für Ausschlüsse finden Sie in der [Scoring Specification §4](/docs/specifications/scoring#4-composite-score).** Der Harness-Code spiegelt diese Tabellen in `mt_eval_harness/scoring.py` wider. chrF++ wird vor der Gewichtung durch 100 dividiert, um es zu normalisieren; Code-Switching- und Halluzinationsraten werden invertiert (niedriger = besser).

### Was sind Qualitätsstufen?

Qualitätsstufen sind heuristische Bezeichnungen, die bestimmten Bereichen des composite score zugeordnet sind. Sie helfen dabei, zu vermitteln, was eine Bewertung praktisch *bedeutet*:

| Stufe | Bereich des composite score | Interpretation |
|------|----------------|----------------|
| **Baseline** | 0.00 – 0.30 | Unterhalb der brauchbaren Qualität. Die Methode bedarf erheblicher Verbesserung. |
| **Emerging** | 0.30 – 0.50 | Vielversprechend. Einige Übersetzungen sind korrekt, aber inkonsistent. |
| **Functional** | 0.50 – 0.70 | Mit menschlicher Überprüfung als Referenz nutzbar. Nicht für unüberprüften Einsatz geeignet. |
| **Deployable** | 0.70 – 0.85 | Bereit für den Produktiveinsatz mit regelmäßiger Überprüfung. Löst die Berechtigung zur Eigentumsübertragung aus. |
| **Fluent** | 0.85 – 1.00 | Nahezu muttersprachliche Qualität. Geeignet für unbeaufsichtigten Einsatz. |

### Was ist der Unterschied zwischen Qualitätsstufen und Verifizierungsstufen?

**Qualitätsstufen** beschreiben, *was die automatisierte Bewertung bedeutet* (Baseline → Fluent). **Verifizierungsstufen** beschreiben, *wer das Ergebnis validiert hat*:

| Verifizierungsstufe | Was sie bedeutet |
|-------------------|---------------|
| **Self-benchmarked** | Der Einreichende hat das Harness selbst ausgeführt. Die Bewertungen sind plausibel, aber unverifiziert. |
| **GDS Verified** | Ein Maintainer hat das Ergebnis anhand der eingereichten Methodenkonfiguration reproduziert. |
| **Community Validated** | Zweisprachige Sprecher haben die Übersetzungen überprüft und die Qualität bestätigt. |

Eine Methode kann die Qualität "Deployable", aber nur die Verifizierung "Self-benchmarked" aufweisen — das heißt, die Bewertung sieht hervorragend aus, aber niemand hat sie unabhängig bestätigt.

---

## Einreichung & Disqualifikation

### Was führt zur Disqualifikation meiner Einreichung?

Ihre Einreichung wird abgelehnt oder markiert, wenn:

1. **Ihre Methode den Evaluierungsdaten ausgesetzt war.** Wenn Sie Einträge aus dem Evaluierungsdatensatz zum Trainieren, Feintuning, Few-Shot-Prompting oder anderweitig verwendet haben, sind Ihre Bewertungen künstlich überhöht. Dies schließt die Verwendung der Referenzübersetzungen in Ihrem Prompt ein.
2. **Ihre Run Card die Integritätsprüfungen nicht besteht.** Der Fingerabdruck muss mit der Konfiguration übereinstimmen. Manipulierte Run Cards werden abgelehnt.
3. **Ihre Methode das TranslationMethod-Protokoll nicht implementiert.** Das Harness erwartet `translate(entries, config) → results`. Benutzerdefinierte Integrationen, die das Harness umgehen, werden nicht akzeptiert.

### Kann ich mehrmals einreichen?

Ja. Das Leaderboard erfasst alle Einreichungen. Sie können iterieren — Dutzende von Experimenten durchführen und nur Ihr bestes Ergebnis einreichen. Jede Einreichung erfasst einen eindeutigen Fingerabdruck, sodass keine Unklarheit darüber besteht, welcher Lauf welche Bewertung erzeugt hat.

### Wie lasse ich meine Bewertung verifizieren?

1. **Self-benchmarked (automatisch):** Jede Einreichung beginnt hier.
2. **GDS Verified:** Reichen Sie Ihre Methode als reproduzierbares Paket ein (Code + Konfiguration + Coaching-Daten). Ein Maintainer führt sie gegen denselben Datensatz erneut aus und bestätigt, dass die Bewertungen übereinstimmen.
3. **Community Validated:** Für indigene Sprachen müssen zweisprachige Sprecher eine Stichprobe der Übersetzungen überprüfen. Dies kann nicht automatisiert werden — es erfordert die Einbindung der Gemeinschaft.

### Ist die Einreichungs-API aktiv?

Noch nicht. Der Endpunkt `https://mtevalarena.org/api/leaderboard/submit` ist eine Zielvorstellung. Aktuelle Einreichungen sollten per Pull Request an das [Eval-Harness-Repository](https://github.com/gamedaysuits/arena) mit Ihrer Run-Card-JSON im Verzeichnis `results/` erfolgen.

---

## Modelle & Parameter

### Welches Modell sollte ich verwenden?

Es gibt kein einzelnes bestes Modell — es hängt vom Sprachpaar, Ihrem Budget und Ihrem Ansatz ab. Allgemeine Hinweise:

| Sprachtyp | Empfohlener Ausgangspunkt | Warum |
|---------------|---------------------------|-----|
| **Ressourcenreich** (Französisch, Spanisch, Japanisch) | `google/gemini-2.5-flash` oder `gpt-4o-mini` | Schnell, günstig, starke Baseline |
| **Ressourcenarm mit gewisser LLM-Abdeckung** (Quechua, Yoruba) | `google/gemini-2.5-pro` oder `anthropic/claude-sonnet-4` | Größere Modelle verfügen über besseres latentes Wissen |
| **Polysynthetisch / sehr ressourcenarm** (Plains Cree, Inuktitut) | `google/gemini-2.5-pro` mit Coaching | Coaching-Daten sind wichtiger als die Modellwahl. OMT-1600 umfasst einige polysynthetische Sprachen (z. B. CRK auf R1-Stufe), jedoch mit standardmäßiger BPE-Tokenisierung — benchmarken Sie es in der Arena als Baseline. |

Das Eval-Harness verwendet OpenRouter, sodass jedes auf OpenRouter verfügbare Modell gebenchmarkt werden kann. Führen Sie `champollion models --method llm` aus, um die verfügbaren Modelle anzuzeigen.

### Welche Temperatur sollte ich verwenden?

Niedriger ist für Übersetzungen im Allgemeinen besser:

| Temperatur | Wirkung | Empfohlen für |
|-------------|--------|-----------------|
| **0.0 – 0.2** | Hochgradig deterministisch, konsistente Ausgabe | Produktionsmethoden, finale Benchmarks |
| **0.3 – 0.5** | Gewisse Variation, gelegentlich kreativer | Erkundung, frühe Iteration |
| **0.6+** | Hohe Variation, unvorhersehbar | Nicht für MT-Benchmarking empfohlen |

Die Temperatur wird in der Run Card erfasst, sodass unterschiedliche Temperaturen unterschiedliche Fingerabdrücke erzeugen — sie werden als unterschiedliche Experimente behandelt.

### Helfen Coaching-Daten?

Ja, erheblich — für ressourcenarme Sprachen. Coaching-Daten (Grammatikregeln, Wörterbucheinträge, Stilhinweise) werden in den System-Prompt des LLM eingespeist. Für Plains Cree übertreffen gecoachte Methoden bei polysynthetischen Sprachen durchgängig reine LLM-Methoden, da Allzweck-LLMs nur begrenzte polysynthetische Exposition und kein morphologisches Bewusstsein aufweisen. Selbst OMT-1600, das speziell für CRK trainiert wurde, verwendet eine standardmäßige BPE-Tokenisierung, die polysynthetische Morphologie strukturell nicht abbilden kann. Die Coaching-Daten liefern den sprachlichen Kontext, der dem Modell fehlt.

Bei ressourcenreichen Sprachen (Französisch, Spanisch) hat Coaching weniger Einfluss, da das Modell bereits über solides Grundwissen verfügt.

Siehe [Coaching Data](https://champollion.dev/docs/concepts/coaching-data) für die vollständige Spezifikation.

---

## FST & Morphologische Validierung

### Was ist, wenn es für meine Sprache keinen FST gibt?

Viele Sprachen verfügen nicht über einen endlichen Zustandstransduktor. Das ist in Ordnung — das Harness funktioniert auch ohne. Der composite score verwendet die Gewichtungen von Profile B (siehe [Scoring Specification §4.3](/docs/specifications/scoring#43-weight-tables)), die das Gewicht auf semantische und Oberflächenmetriken verlagern. FST acceptance wird in der Run Card als `null` markiert.

Die wichtigsten Registries für bestehende FSTs:

| Registry | Abdeckung | URL |
|----------|----------|-----|
| **GiellaLT** | Sámi, Cree, Inuktitut und andere arktische/subarktische Sprachen | [giellalt.uit.no](https://giellalt.uit.no/) |
| **ALTLab** | Plains Cree, Woods Cree, Ojibwe | [altlab.artsrn.ualberta.ca](https://altlab.artsrn.ualberta.ca/) |
| **Apertium** | ~60 Sprachpaare, überwiegend europäisch | [apertium.org](https://apertium.org/) |
| **UniMorph** | Morphologische Paradigmen für mehr als 150 Sprachen | [unimorph.github.io](https://unimorph.github.io/) |

### Kann ich einen FST erstellen?

Ja, aber es ist nicht trivial. Ein FST kodiert die morphologischen Regeln einer Sprache — alle gültigen Wortformen. Die Erstellung erfordert tiefgehende sprachwissenschaftliche Kenntnisse der Sprache. Wenn Sie Zugang zu einer morphologischen Grammatik haben (z. B. von einer linguistischen Fakultät), kann diese mit Werkzeugen wie [HFST](https://hfst.github.io/) oder [Foma](https://fomafst.github.io/) zu einem FST kompiliert werden.

### Wie funktioniert das FST-Gating in der Praxis?

Die FST-gegatete Pipeline funktioniert folgendermaßen:

1. Das LLM generiert eine Übersetzung
2. Jedes Wort in der Ausgabe wird gegen den FST geprüft
3. Vom FST abgelehnte Wörter werden als morphologisch ungültig markiert
4. Die Methode kann mit Rückmeldung erneut versuchen ("das Wort X ist nicht gültig, versuchen Sie es erneut")
5. Nach den erneuten Versuchen werden verbleibende ungültige Wörter protokolliert

Die FST-Akzeptanzrate misst, wie viele Wörter die Validierung bestehen. Siehe das [FST-Gated Pipeline Tutorial](/docs/tutorials/fst-gated-pipeline) für ein vollständig durchgearbeitetes Beispiel.

---

## Daten & Datensätze

### Kann ich einen Datensatz für eine neue Sprache beisteuern?

Ja. Mindestanforderungen aus [Benchmark Specification §11](/docs/specifications/benchmark#11-extending-to-new-languages):

- **50 Goldstandard-Einträge** (Quelle + verifizierte Referenzübersetzung)
- **30 Entwicklungseinträge** (können sich bei kleinen Korpora mit dem Goldstandard überschneiden)
- **Einwilligung der Gemeinschaft** (für indigene Sprachen ausdrückliche Autorisierung durch ein Governance-Gremium)
- **Provenienzdokumentation** (woher die Daten stammen, welche Lizenz gilt)

Neue Datensätze eröffnen automatisch neue Leaderboard-Tracks. Siehe [For Language Communities](/docs/community/for-language-communities) für den Leitfaden für Beitragende.

### In welchem Format sollte mein Datensatz vorliegen?

JSON mit den kanonischen Feldnamen:

```json
{
  "name": "my-language-dev-v1",
  "language_pair": "en-xxx",
  "segment": "development",
  "version": "1.0",
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "[translation in target language]",
      "difficulty": 1,
      "domain": "general"
    }
  ]
}
```

Siehe [Datasets](/docs/leaderboard/datasets) für das vollständige Schema und die Definitionen der Schwierigkeitsstufen.

---

## Souveränität & Eigentum

### Wem gehört eine für eine indigene Sprache entwickelte Methode?

Für indigene Sprachen lösen Methoden, die die Stufe Deployable erreichen (composite score ≥ 0.70) UND die Validierung durch die Gemeinschaft bestehen, den Prozess der [Eigentumsübertragung](/docs/sovereignty/ownership-transfer) aus. Das Eigentum am Code geht vom Forschenden auf die Governance-Organisation der Sprachgemeinschaft über.

Der Forschende behält:
- Veröffentlichungsrechte (wissenschaftliche Arbeiten über die Methode)
- Anerkennung auf dem Leaderboard
- Das Recht, dieselben *Techniken* auf andere Sprachen anzuwenden

Die Governance-Organisation erhält:
- Vollständiges Eigentum am Methodencode und an den Coaching-Daten
- Kontrolle über den Einsatz (wann, wo, wie)
- Einnahmen aus der API-Nutzung (90 % Gemeinschaft, 10 % Infrastruktur)

### Kann ich champollion ohne jegliche Souveränitätsbedenken für nicht-indigene Sprachen verwenden?

Ja. Für Standardsprachen (Französisch, Japanisch, Spanisch usw.) bestehen keine Souveränitätserwägungen. Verwenden Sie champollion ganz normal — übersetzen, synchronisieren und veröffentlichen Sie nach Belieben. Das Souveränitätsframework gilt speziell für indigene und gemeinschaftlich verwaltete Sprachen, bei denen Grundsätze der Datenverwaltung (OCAP®, CARE, Te Mana Raraunga) besondere Berücksichtigung erfordern.

---

## Siehe auch

- **[How It Works](https://champollion.dev/how-it-works)** — die vollständige Erläuterung der Lösung
- **[Scoring Specification](/docs/specifications/scoring)** — die SSOT für die gesamte Bewertungslogik (Metriken, Gewichtungen, Stufen)
- **[Benchmark Specification](/docs/specifications/benchmark)** — Evaluierungsprotokoll, Korpusformat, Souveränität
- **[Submit a Method](/docs/getting-started/submit-a-method)** — Schritt-für-Schritt-Schnellstart
- **[Leaderboard Rules](/docs/leaderboard/rules)** — Einreichungskriterien
- **[Data Sovereignty](/docs/sovereignty/data-sovereignty)** — OCAP®, CARE und ethische Verpflichtungen