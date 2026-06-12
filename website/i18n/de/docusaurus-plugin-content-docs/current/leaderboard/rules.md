---
sidebar_position: 1
title: "MT-Evaluation"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "How the composite score is computed"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Evaluation Datasets"
    to: /docs/leaderboard/datasets
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "The rules, applied"
---
# MT Evaluation

> **Executive Summary.** Diese Seite definiert die Einreichungskriterien für das Leaderboard, die Bewertungsmetriken (chrF++, FST acceptance, exact match, equivalent match, semantic score), die Anti-Gaming-Richtlinien, die Verifizierungsstufen und den Einreichungsworkflow. Methoden, die mit Evaluierungsdaten in Berührung gekommen sind, werden disqualifiziert.

champollion umfasst ein Framework zur Evaluierung maschineller Übersetzung, das für das **reproduzierbare Benchmarking** von Übersetzungsmethoden konzipiert ist — insbesondere für ressourcenarme und indigene Sprachen, für die es keine standardisierten MT-Benchmarks gibt und für die Qualitätsbehauptungen schwer zu überprüfen sind.

---

## Das Leaderboard

Das Herzstück ist das **[Method Leaderboard](https://champollion.dev/leaderboard)** — eine Live-Bestenliste auf Basis von Supabase, auf der Forschende und Mitglieder der Community Übersetzungsmethoden mit fingerprinted, reproduzierbarer Evaluierung einreichen und vergleichen.

Jede Einreichung umfasst:

- **Fingerprinted Pipeline** — gebunden an einen bestimmten Git-Commit und Config-Hash, sodass sich die Ergebnisse exakt auf den Code zurückführen lassen, der sie erzeugt hat
- **Versionierter Datensatz** — content-gehasht und versioniert; Bewertungen sind nur innerhalb derselben Datensatzversion vergleichbar
- **Standardisierte Metriken** — die gesamte Bewertung wird durch das gemeinsame Evaluierungs-Harness berechnet, wodurch Unterschiede in der Implementierung ausgeschlossen werden
- **Vertrauensstufen** — self-benchmarked, GDS Verified oder Community Validated
- **Kostenverfolgung** — API-Kosten pro Einreichung, sodass Kosten-Qualitäts-Abwägungen transparent sind

Das Leaderboard erfasst derzeit fünf Metriken. Drei funktionieren für jede Sprache; zwei sind für Plains Cree verfügbar und werden mit unserer Erweiterung verallgemeinert:

| Metrik | Typ | Was sie misst |
|--------|------|------------------|
| **chrF++** | Zeichen-n-Gramm-F-Score | Primäre Qualitätsmetrik — korreliert gut mit menschlicher Bewertung, insbesondere bei morphologisch reichen Sprachen |
| **Exact Match** | Anteil perfekter Übereinstimmungen | Strikte Genauigkeit — wie oft entspricht die Übersetzung exakt dem Goldstandard? |
| **FST Acceptance** | Bestehensrate des morphologischen Gatters | Für Methoden mit Verifizierung durch Finite-State-Transducer — welcher Anteil der Ausgaben ist morphologisch gültig? |
| **Equivalent Match** | Rate akzeptabler Varianten | Anteil, der mit der Referenz oder einer akzeptablen Variante übereinstimmt (Wortstellung, orthografische Konvention). Derzeit CRK; wird verallgemeinert. |
| **Semantic Score** | Semantische Treue | Bedeutungserhalt — erfasst die Übersetzung die beabsichtigte Bedeutung unabhängig von der Oberflächenform? Derzeit CRK; wird verallgemeinert. |

:::info Full Metric Suite
Die [Scoring Specification](/docs/specifications/scoring) definiert das vollständige Inventar von 19 Metriken über 5 Kategorien hinweg, die Formel des composite score, die Gewichtungstabellen und die Schwellenwerte der Qualitätsstufen.
:::

**[→ Das Leaderboard ansehen](https://champollion.dev/leaderboard)**

---

## Verfügbare Datensätze

### EDTeKLA Development Set v1

Der erste Evaluierungsdatensatz, erstellt für die Übersetzung Englisch→Plains Cree (SRO). Erstellt von der [EdTeKLA research group](https://spaces.facsci.ualberta.ca/edtekla/) an der University of Alberta.

| Eigenschaft | Wert |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Sprachpaar** | EN → CRK (Plains Cree, SRO-Orthografie) |
| **Anzahl der Einträge** | 404 (`master_corpus.json`: 62 gold + 342 textbook); 548 insgesamt verfügbar |
| **Lizenz** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| **Herkunft** | `gold_standard` (von Sprechenden verifiziert), `textbook` (veröffentlichte Lehrmaterialien) |

### FLORES+ Devtest — Nur zur Entwicklungsnutzung

> [!WARNING]
> **FLORES+ ist für Entwicklung und Debugging verfügbar, wird jedoch NICHT für die offizielle Leaderboard-Evaluierung verwendet.** FLORES+ (ursprünglich Meta FLORES-200) ist ein weit verbreiteter öffentlicher Benchmark-Datensatz, auf dem Frontier-LLMs mit ziemlicher Sicherheit trainiert wurden. Bewertungen gegen FLORES+ spiegeln die reale Übersetzungsqualität für LLM-basierte Methoden nicht zuverlässig wider. Nicht-LLM-Methoden (FST, regelbasiert, fine-tuned NMT) sind weniger betroffen, doch FLORES+-Bewertungen werden dennoch nicht auf dem Leaderboard veröffentlicht.

FLORES+-Fixtures bleiben in `test/benchmark/fixtures/` verfügbar für Pipeline-Smoke-Tests, sprachübergreifende Validierung und Entwicklungsnutzung. Die offizielle Evaluierung verwendet maßgeschneiderte Korpora, die aus von Menschen verfassten Texten erstellt wurden, welche nicht öffentlich in paralleler Form verfügbar sind.

Siehe [Evaluation Datasets](/docs/leaderboard/datasets) für das vollständige Datensatzschema, die Schwierigkeitsstufen und Hinweise zur Erstellung eigener Datensätze.

:::danger TRAINIEREN SIE NICHT mit Evaluierungsdaten

**Diese Datensätze sind ausschließlich zur Evaluierung bestimmt.** Methoden, die mit Evaluierungsdaten trainiert, fine-tuned, few-shot-prompted oder anderweitig in Berührung gebracht wurden, erzeugen künstlich überhöhte Bewertungen und werden **vom Leaderboard disqualifiziert.**

Dies ist keine Empfehlung — es ist die wichtigste einzelne Regel der Evaluierungsintegrität. Verwenden Sie separate Korpora für das Training. Evaluierungssätze müssen während der Entwicklung für Ihr Modell ungesehen bleiben.

Wenn Sie Coaching-Daten oder Few-Shot-Beispiele verwenden, müssen diese aus **vollständig getrennten Quellen** stammen. Im Zweifelsfall beziehen Sie sie nicht ein.
:::

:::warning LLM-Nichtdeterminismus

LLM-Ausgaben sind nichtdeterministisch. Bewertungen stellen zeitpunktbezogene Messungen unter bestimmten Modellversionen und API-Konfigurationen dar. Modellanbieter können Gewichte, Decodierungsstrategien oder Sicherheitsfilter jederzeit aktualisieren, was zu einer Bewertungsdrift zwischen Durchläufen führen kann. Das Leaderboard erfasst den exakten Model-Slug und Zeitstempel für jede Einreichung.
:::

---

## Was eine gute Methode ausmacht

Nicht alle Methoden sind gleich. Hier ist, was rigorose Arbeit von überhöhten Bewertungen unterscheidet.

### Merkmale einer starken Methode

- **Saubere Trennung von Trainings- und Evaluierungsdaten** — Ihre Methode hat den Evaluierungssatz während der Entwicklung, Abstimmung, des Prompt-Engineering oder der Auswahl von Few-Shot-Beispielen nie gesehen
- **Reproduzierbar** — jemand anderes kann Ihr Repository klonen, das Harness ausführen und dieselben Bewertungen erhalten (innerhalb der Grenzen des LLM-Nichtdeterminismus)
- **Dokumentiert** — Ihre [method card](/docs/specifications/methods) beschreibt, was Ihre Methode tut, welche Werkzeuge sie verwendet und welche Einschränkungen sie hat
- **Ehrlich hinsichtlich des Umfangs** — wenn Ihre Methode nur für ein Sprachpaar funktioniert, geben Sie dies an; wenn sie bei bestimmten morphologischen Mustern an Qualität verliert, dokumentieren Sie dies
- **Community-bewusst** — bei indigenen Sprachen respektiert Ihre Methode die Datensouveränität. Sie haben Sprachgemeinschaften konsultiert oder ausschließlich offen lizenzierte Daten verwendet

### Warnsignale (was zur Disqualifikation führt)

| Warnsignal | Warum es ein Problem ist |
|----------|--------------------|
| Training mit Evaluierungsdaten | Untergräbt den Zweck der Evaluierung vollständig. Überhöhte Bewertungen führen alle in die Irre. |
| Cherry-Picking von Ergebnissen | 10-maliges Ausführen und Einreichen des besten Durchlaufs, ohne die anderen offenzulegen |
| Nicht offengelegte Nachbearbeitung | Manuelles Korrigieren von Ausgaben vor der Bewertung |
| Kontaminierte Coaching-Daten | Verwendung von Beispielen aus dem Evaluierungssatz als Few-Shot-Prompts oder Wörterbucheinträge |
| Behauptung kommerzieller Einsatzbereitschaft ohne Herkunftsnachweis | Wenn Ihre Methode CC BY-NC-SA-Daten verwendet, ist sie nicht kommerziell einsatzbereit |

### Verifizierungsstufen

Verifizierungsstufen beschreiben, **wer das Ergebnis validiert hat** — getrennt von den Qualitätsstufen (Baseline → Fluent), die in der [Scoring Specification, §5](/docs/specifications/scoring#5-quality-tiers) definiert sind und beschreiben, was der automatisierte composite score bedeutet.

| Stufe | Bedeutung | Wie man sie erhält |
|------|---------|--------------|
| **Self-benchmarked** | Sie haben das Harness selbst ausgeführt und Ergebnisse eingereicht | Öffnen Sie einen PR mit Ihrer run card |
| **GDS Verified** | Die champollion-Maintainer haben Ihre Ergebnisse reproduziert | Reichen Sie Ihre Methode als installierbares Plugin ein |
| **Community Validated** | Governance-Organisation hat gegen Goldstandard + Community-Review ausgeführt | Reichen Sie den Methodencode bei der Governance-Organisation ein |

---

## So reichen Sie ein

1. **Erstellen Sie Ihre Methode** — siehe [Building a Method](/docs/specifications/methods) für die Methodenschnittstelle
2. **Führen Sie das Harness aus** — siehe [Eval Harness](/docs/specifications/harness) für Einrichtung und Verwendung
3. **Erzeugen Sie eine run card** — das Harness erstellt eine JSON-run-card mit Ihren Bewertungen, dem Fingerprint und den Metadaten
4. **Öffnen Sie einen PR** — reichen Sie Ihre run card im [eval harness repository](https://github.com/gamedaysuits/arena) ein
5. **Erscheinen Sie auf dem Leaderboard** — nach dem Merge erscheinen Ihre Ergebnisse auf dem [Method Leaderboard](https://champollion.dev/leaderboard)

---

## Zukünftige Ausrichtungen

- **Umfassende Modellvergleichsdurchläufe** — systematische Evaluierung von Frontier-Modellen (GPT-4o, Claude, Gemini usw.) über champollion-Sprachen hinweg unter Verwendung maßgeschneiderter Evaluierungskorpora (keine öffentlichen Benchmarks)
- **Mehr Sprachpaare** — Quechua, Inuktitut und andere ressourcenarme Sprachen, sobald von der Community verifizierte Datensätze verfügbar werden
- **Datensatzimport** — Werkzeuge zur Konvertierung externer Evaluierungsdatensätze (WMT, Tatoeba usw.) in das champollion-Evaluierungsformat
- **Automatisierte erneute Durchläufe** — Erkennung von Änderungen der Modellversion und erneutes Ausführen von Benchmarks zur Verfolgung der Bewertungsdrift

---

## Siehe auch

- **[Method Leaderboard](https://champollion.dev/leaderboard)** — Live-Bewertungen und Einreichungen
- **[Eval Harness](/docs/specifications/harness)** — wie man Evaluierungen ausführt
- **[Evaluation Datasets](/docs/leaderboard/datasets)** — Datensatzformat und verfügbare Datensätze
- **[Building a Method](/docs/specifications/methods)** — die Spezifikation der Methodenschnittstelle
- **[Run Card Specification](/docs/specifications/run-card)** — das JSON-Schema der run card
- **[Benchmark Specification](/docs/specifications/benchmark)** — Evaluierungsprotokoll, Korpusformat, Souveränität
- **[Scoring Specification](/docs/specifications/scoring)** — SSOT für Metriken, composite-Gewichtungen und Qualitätsstufen