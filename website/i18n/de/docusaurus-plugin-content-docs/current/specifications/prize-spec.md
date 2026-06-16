---
sidebar_position: 8
title: "Preisspezifikation"
slug: '/specifications/prizes'
related:
  - label: "How Speakers Get Paid"
    to: /docs/perspectives/how-speakers-get-paid
    kind: position
    note: "The plain-language version of these numbers"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
---
# Preisspezifikation

> **Zweck.** Dieses Dokument definiert die Struktur des Preispools, die Schwellenbedingungen, den Antragsprozess sowie die Regeln für die MT Eval Arena. Es legt exakt fest, was „maschinelle Übersetzungsfähigkeit" in messbaren Begriffen bedeutet und unter welchen Bedingungen Preisgelder freigegeben werden. Dieses Dokument verweist für Metrikdefinitionen auf SCORING_SPEC und für das Evaluationsprotokoll auf BENCHMARK_SPEC — es dupliziert diese nicht.
>
> **Status:** LIVE. Der Founder's Prize (§2.1) ist finanziert und aktiv.
>
> Zuletzt aktualisiert: 2026-06-04

---

## 1. Philosophie

### 1.1 Preise belohnen Durchbrüche, nicht Teilnahme

Preisgelder werden nur dann freigegeben, wenn eine Methode nachweislich eine definierte Fähigkeitsschwelle erreicht. Es gibt keine Teilnahmepreise, keine Auszeichnungen für Zweitplatzierte und keine Trostpreise. Wenn niemand die Hürde überwindet, wird niemand bezahlt. Dies ist beabsichtigt — es bedeutet, dass Sponsoren nur für Ergebnisse zahlen, die tatsächlich funktionieren.

### 1.2 Community-Validierung ist nicht verhandelbar

Automatisierte Metriken sind Stellvertreter (SCORING_SPEC §1.1). Eine Methode kann bei chrF++ und FST-Akzeptanz gut abschneiden und dennoch Ausgaben erzeugen, die kein Sprecher akzeptieren würde. **Jeder Preisantrag erfordert eine Community-Validierung** — zweisprachige Sprecher müssen bestätigen, dass die Ausgabe brauchbar ist. Dies ist das Tor zur menschlichen Validierung (BENCHMARK_SPEC §7).

### 1.3 Eigentumsübertragung ist Teil der Vereinbarung

Methoden, die einen Preis beanspruchen, unterliegen der Klausel zur Eigentumsübertragung (BENCHMARK_SPEC §8.3). Der Entwickler behält die Rechte auf Namensnennung und Veröffentlichung. Die Governance-Organisation erhält das Recht, die Methode für ihre Sprache zu nutzen, zu modifizieren, zu verbreiten und zu monetarisieren. Dies ist keine Strafe — es ist der eigentliche Zweck. Preisgelder finanzieren die Erstellung von Technologie, die der Sprachgemeinschaft gehört.

### 1.4 Anti-Gaming

Preisschwellen werden gegen eine **Goldstandard-Evaluation** definiert (geheimer Testdatensatz, ausgeführt von der Governance-Organisation in einer Sandbox). Entwickler sehen die Testdaten niemals. Dies ist architektonisch durchgesetzt — keine Richtlinie, die sich auf Ehrlichkeit verlässt. Siehe BENCHMARK_SPEC §8.2.

### 1.5 Korpuslizenzierung: Nicht-kommerzielle Korpora bleiben außerhalb der Preisspur

Einige Korpora, die während der Methodenentwicklung verwendet werden, tragen nicht-kommerzielle Lizenzen — beispielsweise unterliegt das EdTeKLA Cree Language Textbook corpus der Lizenz **CC BY-NC-SA 4.0**. Diese Korpora sind **ausschließlich für die Forschungs-/Entwicklungsspur bestimmt**:

1. **Goldstandard-Korpora für Preise dürfen keine NC-lizenzierten Korpusinhalte einbetten.** Goldstandard-Testsegmente sind von der Gemeinschaft in Auftrag gegebene Originale (siehe Corpus Partnership Strategy) — von Menschen für den Preis verfasst, mit von Anfang an geklärten Rechten für Evaluation und kommerziellen Einsatz.
2. **Eine Methode, die einen Preis beansprucht, darf keine NC-lizenzierten Korpusinhalte einbetten** (z. B. als Coaching-Daten, eingebettete Beispiele oder Nachschlagetabellen). Die übertragene Methode ist für den kommerziellen Einsatz durch die Governance-Organisation bestimmt (BENCHMARK_SPEC §8.3, Method Submission Agreement §6); NC-lizenzierte Inhalte darin würden diesen Einsatz vergiften.
3. **Entwickler dürfen NC-lizenzierte Korpora frei verwenden, um zu entwickeln und sich selbst zu evaluieren** — genau dafür ist die Entwicklungsspur da. Die Beschränkung gilt für das, was eingereicht und was eingesetzt wird, nicht dafür, wie ein Entwickler lernt.

### 1.6 Abhängigkeitsklassen steuern die Preisberechtigung

Die gesamte Preisevaluation findet in einer Sandbox statt (§1.4), und preisgekrönte Methoden werden an die Governance-Organisation übertragen (§1.3). Beide Tatsachen erlegen dieselbe Beschränkung auf: **Alles, wovon eine Methode abhängt, muss etwas sein, das der Entwickler das Recht hat, in die Sandbox einzubringen und an die Gemeinschaft zu übermitteln.** Jede Einreichung deklariert eine Abhängigkeitsklasse — definiert in der [Method Interface spec](/docs/specifications/methods#method-validity-and-dependency-classes), mit Zulässigkeitsbedingungen im Method Submission Agreement §2.6 — und die Berechtigung richtet sich nach der Klasse:

| Abhängigkeitsklasse | Preisberechtigt? | Bedingungen |
|------------------|----------------|------------|
| **S** — eigenständig | ✅ Ja | Keine über die Schwellenbedingungen in §2 hinaus |
| **O** — offen extern (z. B. AGPL FST, bei Einreichung gespiegelt) | ✅ Ja | Artefakte fixiert und in die Einreichung eingebunden; Lizenzen erlauben Übertragung an die Gemeinschaft; Copyleft-Bedingungen bewahrt (die Gemeinschaft erhält dieselben Rechte, die die Lizenz allen gewährt) |
| **A1** — substituierbare LLM-Inferenz | ⚠️ Bedingt | Modell deklariert, fixiert und substituierbar (muss gegen ein von der Gemeinschaft gehostetes Open-Weight-Modell laufen); Evaluation über das Sandbox-LLM-Gateway geleitet (🔲 geplant — A1-Methoden können keine Goldstandard-Scores erzeugen, bis das Gateway betriebsbereit ist); die Übertragung übermittelt das vollständige Rezept (Prompts, Coaching, Code), nicht das Modell |
| **A2** — nicht-substituierbare externe Daten-/Service-API | ❌ Noch nicht | Nicht berechtigt, bis der Rechteinhaber Sandbox-Einbindung und Übertragungsberechtigungen erteilt. Auf dem offenen Leaderboard mit einer sichtbaren Markierung „external dependency" erlaubt |
| **X** — gebündelte Inhalte ohne Rechte | ❌ Niemals | In jeder Spur unzulässig |

Die Klasse einer Methode ist die restriktivste Klasse unter ihren deklarierten Abhängigkeiten. Nicht deklarierte Abhängigkeiten jeglicher Klasse führen zur Disqualifikation (§5).

---

## 2. Aktive Preispools

### 2.1 Der Founder's Prize — EN→Plains Cree (nêhiyawêwin)

| Feld | Wert |
|-------|-------|
| **Preispool** | **10.000 CAD** |
| **Sprachpaar** | English → Plains Cree (EN→CRK) |
| **Finanziert von** | Gründer des Champollion-Projekts |
| **Status** | **AKTIV** — nimmt Einreichungen entgegen |
| **Eröffnet** | Sobald Goldstandard-Korpus + Governance-Organisation vorhanden sind |
| **Läuft ab** | Kein Ablaufdatum. Der Preis bleibt aktiv, bis er beansprucht oder ausdrücklich zurückgezogen wird. |

#### Schwellenbedingungen

Eine Methode beansprucht den Founder's Prize, indem sie **ALLE** der folgenden Bedingungen gleichzeitig erfüllt:

| # | Bedingung | Metrik | Schwelle | Begründung |
|---|-----------|--------|-----------|-----------|
| 1 | **Composite Score** | `composite` (SCORING_SPEC §4) | **≥ 0.80** | Zwischen Deployable (0.70) und Fluent (0.85). Erfordert hohe Qualität über alle Metrikdimensionen hinweg — nicht nur morphologische Gültigkeit. |
| 2 | **FST-Akzeptanz** | `fst_acceptance_rate` (SCORING_SPEC §2.2) | **≥ 0.99 (99%+)** | Praktisch alle Ausgabewörter müssen morphologisch gültige Formen sein, die vom GiellaLT FST erkannt werden. Die Toleranz von 1 % berücksichtigt Randfälle (Eigennamen, Neologismen, Lehnwörter), die der FST möglicherweise legitimerweise nicht abdeckt. Dies ist das maßgebende Qualitätstor für polysynthetische MT — wenn der FST mehr als 1 % der Wörter ablehnt, erzeugt die Methode Formen, die in der Sprache nicht existieren. Der gesamte Sinn dieses Preises besteht darin, ein System zu erwerben, das nichts verstümmelt. |
| 3 | **chrF++** | `chrf_plus_plus` (SCORING_SPEC §2.1) | **≥ 55.0** | Die Überlappung von Zeichen-n-Grammen muss auf der Skala von 0–100 den Wert 55 überschreiten. Stellt eine oberflächliche Ähnlichkeit mit Referenzübersetzungen sicher, nicht nur morphologische Gültigkeit. |
| 4 | **Community-Validierung** | Menschliche Begutachtung (BENCHMARK_SPEC §7) | **≥ 70 % „acceptable" oder „excellent"** | Eine stratifizierte Stichprobe von Ausgaben (≥30 Einträge über die Schwierigkeitsstufen 2–5) wird von ≥2 zweisprachigen CRK-Sprechern begutachtet. Mindestens 70 % der begutachteten Einträge müssen die Bewertung „acceptable" oder „excellent" erhalten. |
| 5 | **Goldstandard-Evaluation** | Sandbox-Ausführung (BENCHMARK_SPEC §8.2) | **Erforderlich** | Alle automatisierten Metriken müssen gegen das Korpussegment `gold_standard` berechnet werden, ausgeführt von der Governance-Organisation in einer Sandbox-Umgebung. Scores aus dem Entwicklungsdatensatz zählen nicht. |
| 6 | **Reproduzierbarkeit** | Fingerprint-Übereinstimmung (BENCHMARK_SPEC §3.8) | **±2 %** | Die Governance-Organisation muss in der Lage sein, die Methode erneut auszuführen und Scores innerhalb von ±2 % der eingereichten Run Card zu erzielen. |

> **Warum 99+% FST?** Das zentrale Problem bei der maschinellen Übersetzung polysynthetischer Sprachen ist Halluzination — LLMs erzeugen Zeichenketten, die *aussehen* wie die Zielsprache, aber morphologisch ungültig sind. Eine Methode, die zu 95 % gültige Ausgaben erzeugt, hat immer noch 5 % erfundene Wörter — inakzeptables Rauschen für jeden Produktionseinsatz. Die Schwelle von 99+% verlangt nahezu null Halluzination und lässt dabei den seltenen Randfall zu (einen Eigennamen, den der FST nicht kennt, einen legitimen Neologismus). Wenn eine Methode keine FST-Akzeptanz von 99+% erreichen kann, hat sie das Problem nicht gelöst.
>
> **Warum 0.80 Composite?** Dieser Wert liegt zwischen Deployable (0.70) und Fluent (0.85). Eine Methode bei 0.80 mit einer FST-Akzeptanz von 99+% erzeugt Ausgaben, in denen praktisch jedes Wort ein echtes Cree-Wort ist *und* die Gesamtqualität der Übersetzung über die oberflächlichen, strukturellen und semantischen Dimensionen hinweg hoch ist. Das Tor zur Community-Validierung (Bedingung #4) stellt sicher, dass dies nicht nur Metrik-Gaming ist — Sprecher müssen bestätigen, dass die Ausgabe tatsächlich brauchbar ist.

#### Was diese Schwelle in der Praxis bedeutet

Bei Composite ≥ 0.80 mit FST ≥ 0.99 und chrF++ ≥ 55 würde ein zweisprachiger Sprecher typischerweise Folgendes sehen:

- **Praktisch jedes** Ausgabewort ist ein echtes Cree-Wort (FST validiert 99+% — nahezu null halluzinierte Formen)
- Die wesentlichen grammatikalischen Kategorien (Person, Numerus, Tempus) sind in den meisten Einträgen korrekt
- Die Wortreihenfolge ist im Allgemeinen natürlich
- Die Bedeutung bleibt zuverlässig erhalten
- Verbleibende Fehler sind Fehler innerhalb der realen Sprache (falsche Flexion, inkorrekte Obviation, Belebtheitsabweichungen) — keine erfundenen Wörter
- Ein fließender Sprecher könnte die Ausgabe als hochwertigen Entwurf verwenden und ihn deutlich schneller korrigieren, als ihn von Grund auf zu übersetzen

Dies ist ein System, das **die Sprache nicht verstümmelt.** Es mag nicht perfekt sein, aber jedes Wort, das es erzeugt, ist ein echtes Wort. Das ist die Mindesthürde für eine respektvolle maschinelle Übersetzung einer polysynthetischen Sprache.

---

## 3. Preisantragsprozess

### 3.1 Einreichung

1. Der Entwickler reicht seine vollständige, ausführbare Methode bei der Governance-Organisation ein:
   - Den gesamten Quellcode
   - Alle Abhängigkeiten (Coaching-Daten, Wörterbücher, FST-Konfigurationen, Prompts)
   - Installations- und Ausführungsanweisungen
   - Eine README, die den Ansatz der Methode beschreibt
   - Eine Run Card aus dem Entwicklungsdatensatz, die ungefähre Scores zeigt (zur Vorprüfung)

2. Der Entwickler unterzeichnet die Teilnahmebedingungen, einschließlich:
   - Klausel zur Eigentumsübertragung (BENCHMARK_SPEC §8.3)
   - Erklärung über das Nicht-Training auf Evaluationsdaten
   - Verpflichtung zur Reproduzierbarkeit

### 3.2 Evaluation

1. Die Governance-Organisation installiert und führt die Methode in einer Sandbox-Umgebung gegen das Korpus `gold_standard` aus
2. Automatisierte Metriken werden berechnet (Composite, FST, chrF++ usw.)
3. Wenn die automatisierten Schwellen erfüllt sind (Bedingungen 1–3), geht die Governance-Organisation zur Community-Begutachtung über
4. Wenn die automatisierten Schwellen NICHT erfüllt sind, erhält der Entwickler Scores und Feedback. Es wird keine Community-Begutachtung ausgelöst.

### 3.3 Community-Begutachtung

1. Eine stratifizierte Stichprobe von Ausgaben (≥30 Einträge, die die Schwierigkeitsstufen 2–5 abdecken) wird zweisprachigen Sprechern vorgelegt
2. Mindestens 2 unabhängige Gutachter bewerten jeden Eintrag
3. Bewertungsskala: **reject** / **gist** / **acceptable** / **excellent**
4. Wenn ≥70 % der Einträge von beiden Gutachtern „acceptable" oder „excellent" erhalten, ist die Community-Validierung bestanden

### 3.4 Auszahlung

1. Alle 6 Bedingungen sind erfüllt
2. Die Governance-Organisation bestätigt das Ergebnis
3. Der Preis wird innerhalb von 30 Tagen nach der Bestätigung ausgezahlt
4. Das Eigentum an der Methode wird gemäß BENCHMARK_SPEC §8.3 übertragen
5. Das Ergebnis wird auf dem Leaderboard mit der Verifizierungsstufe „Community Validated" veröffentlicht

### 3.5 Mehrfacheinreichungen

- Derselbe Entwickler/dasselbe Team darf mehrfach einreichen
- Jede Einreichung wird unabhängig evaluiert
- Wenn eine Methode verbessert und erneut eingereicht wird, zählt nur die neueste Run Card
- Der Preis wird der **ersten** Methode zuerkannt, die alle Schwellen überwindet — er wird nicht geteilt

### 3.6 Teameinreichungen

- Teams sowie Paare aus Ältesten und Jugendlichen sind teilnahmeberechtigt
- Die Verteilung des Preises innerhalb eines Teams liegt in der Verantwortung des Teams
- Alle Teammitglieder müssen die Teilnahmebedingungen unterzeichnen
- Die Namensnennung auf dem Leaderboard listet alle Teammitglieder auf

---

## 4. Künftige Preispools {#4-future-prize-pools}

Der Founder's Prize ist die Saat. Zusätzliche Preispools werden von Sponsoren finanziert. Jeder neue Preispool wird als neuer Unterabschnitt von §2 mit eigenen Angaben dokumentiert:

- Preisbetrag und Währung
- Sprachpaar
- Sponsoren-Namensnennung
- Schwellenbedingungen (die vom Founder's Prize abweichen können)
- Ablaufdatum (falls vorhanden)
- Etwaige Sonderbedingungen

### 4.1 Vorlage für Sponsorenpreise

Sponsoren finanzieren Preispools in beliebiger Höhe. Empfohlene Stufen:

| Stufe | Betrag | Empfohlene Schwelle |
|------|--------|---------------------|
| **Seed** | 5.000–15.000 $ | Deployable (Composite ≥ 0.70) + Community-Validierung |
| **Breakthrough** | 25.000–50.000 $ | Fluent (Composite ≥ 0.85) + Community-Validierung |
| **Grand Prize** | 100.000 $+ | Fluent + Mehrregister-Abdeckung + Deployment-Integration |

Sponsoren können außerdem finanzieren:
- **Verbesserungsprämien** — feste Zahlung für jede Verbesserung um 5 Punkte bei chrF++ gegenüber dem aktuellen Bestwert
- **Registerpreise** — gesonderte Auszeichnungen für bestimmte Register (formell, zeremoniell, bildungsbezogen)
- **Geschwindigkeitspreise** — bester kostenbereinigter Score (SCORING_SPEC §6.3)

### 4.2 Treuhand für Preispools

Alle Preisgelder werden treuhänderisch verwahrt (verwaltet durch das Projekt oder einen benannten Treuhänder), bis die Schwellenbedingungen erfüllt sind. Wenn ein Preis abläuft, ohne beansprucht worden zu sein, werden die Mittel an den Sponsor zurückerstattet oder nach Ermessen des Sponsors in einen neuen Preispool umgeleitet.

---

## 5. Disqualifikation

Eine Einreichung wird disqualifiziert, wenn:

1. **Training auf Evaluationsdaten.** Die Methode wurde Einträgen des Korpus `gold_standard` oder `held_out` ausgesetzt. (Architektonisch durch die Sandbox-Ausführung verhindert — wenn jedoch Belege für eine Kontamination gefunden werden, wird das Ergebnis annulliert.)
2. **Nicht reproduzierbar.** Die Governance-Organisation kann die Scores nicht innerhalb von ±2 % reproduzieren.
3. **Nicht deklarierte oder nicht zulässige Abhängigkeiten.** Die Methode erfordert Laufzeitzugriff auf externe Dienste, der über das hinausgeht, was ihr Abhängigkeitsmanifest deklariert, oder ihre effektive Abhängigkeitsklasse ist A2 oder X (§1.6). Deklarierte LLM-Inferenz der Klasse A1, die über das Evaluations-Gateway geleitet wird, ist zulässig; jede andere Laufzeit-Netzwerkabhängigkeit — sowie jede nicht deklarierte Abhängigkeit jeglicher Klasse — führt zur Disqualifikation.
4. **Teilnahmebedingungen nicht unterzeichnet.** Alle Teammitglieder müssen der Eigentumsübertragung zustimmen.
5. **Gaming festgestellt.** Die Ausgabe ist auf die Metrik optimiert statt auf die Übersetzungsqualität (erkannt durch Community-Begutachtung und/oder Anti-Gaming-Prüfungen gemäß BENCHMARK_SPEC §9.3).

---

## 6. Beziehung zu anderen Spezifikationen

| Dieses Dokument | Verweist auf | Für |
|--------------|-----------|-----|
| §2 Schwellenbedingungen | SCORING_SPEC §4 (Composite), §2.1–2.2 (Metriken), §5 (Stufen) | Metrikdefinitionen und Skala |
| §2 Community-Validierung | BENCHMARK_SPEC §7 | Protokoll zur menschlichen Begutachtung |
| §3 Sandbox-Ausführung | BENCHMARK_SPEC §8.2 | Souveränitätsmechanismus |
| §3 Eigentumsübertragung | BENCHMARK_SPEC §8.3 | Bedingungen zur Übertragung geistigen Eigentums |
| §1.6 Abhängigkeitsklassen | Method Interface spec; Method Submission Agreement §2.6; BENCHMARK_SPEC §8.6 | Klassendefinitionen, Zulässigkeitsbedingungen, Sandbox-Netzwerkrichtlinie |
| §4 kostenbereinigte Preise | SCORING_SPEC §6.3 | Kostenbereinigte Formel |

---

## 7. Synchronisierung von Code und Spezifikation

### 7.1 Kanonische Quelle

Dieses Dokument (`arena/website/docs/specifications/prize-spec.md`) ist die kanonische Quelle für:
- Definitionen von Preispools (§2)
- Schwellenbedingungen (§2.x)
- Antragsprozess (§3)
- Disqualifikationsregeln (§5)

### 7.2 Implementierungsanforderungen

Wenn ein Preispool aktiviert wird:
1. Die Leaderboard-UI muss aktive Preise und ihre Schwellenbedingungen anzeigen
2. Run Cards, die die automatisierten Schwellen (Bedingungen 1–3) erfüllen, müssen für die Community-Begutachtung markiert werden
3. Das Feld `quality_tier` im Run-Card-Schema erfasst die Stufe bereits („deployable", „fluent")
4. Es sind keine neuen Code-Änderungen am Harness erforderlich — die Preisspezifikation ist eine Richtlinienebene auf der bestehenden Bewertung

---

*Preisstrukturen müssen mit den Bedingungen zur Eigentumsübertragung kompatibel sein. Der Gewinner kann den Preis beanspruchen, doch die Methode wird zum Eigentum der Governance-Organisation, wenn sie die Deployable-Stufe erreicht. Dies ist beabsichtigt — der Preis finanziert die Erstellung von Technologie, die der Sprachgemeinschaft gehört.*