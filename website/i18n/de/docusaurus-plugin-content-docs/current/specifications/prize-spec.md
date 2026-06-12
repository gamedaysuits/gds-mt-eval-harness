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

> **Zweck.** Dieses Dokument definiert die Struktur des Preispools, die Schwellenbedingungen, das Antragsverfahren und die Regeln für die MT Eval Arena. Es legt exakt fest, was „zur maschinellen Übersetzung fähig" in messbaren Begriffen bedeutet und unter welchen Bedingungen Preisgelder freigegeben werden. Dieses Dokument verweist auf SCORING_SPEC für Metrikdefinitionen und auf BENCHMARK_SPEC für das Evaluierungsprotokoll – es dupliziert diese nicht.
>
> **Status:** LIVE. Der Founder's Prize (§2.1) ist finanziert und aktiv.
>
> Zuletzt aktualisiert: 2026-06-04

---

## 1. Philosophie

### 1.1 Preise belohnen Durchbrüche, nicht Teilnahme

Preisgelder werden nur dann freigegeben, wenn eine Methode nachweislich einen definierten Fähigkeitsschwellenwert erreicht. Es gibt keine Teilnahmepreise, keine Auszeichnungen für Zweitplatzierte und keine Trostpreise. Wenn niemand die Hürde überwindet, wird niemand bezahlt. Dies ist beabsichtigt – es bedeutet, dass Sponsoren nur für Ergebnisse zahlen, die tatsächlich funktionieren.

### 1.2 Community-Validierung ist nicht verhandelbar

Automatisierte Metriken sind Näherungswerte (SCORING_SPEC §1.1). Eine Methode kann bei chrF++ und FST-Akzeptanz gut abschneiden und dennoch Ausgaben produzieren, die kein Sprecher akzeptieren würde. **Jeder Preisanspruch erfordert eine Community-Validierung** – zweisprachige Sprecher müssen bestätigen, dass die Ausgabe verwendbar ist. Dies ist das Gate für die menschliche Validierung (BENCHMARK_SPEC §7).

### 1.3 Die Eigentumsübertragung ist Teil der Vereinbarung

Methoden, die einen Preis beanspruchen, unterliegen der Eigentumsübertragungsklausel (BENCHMARK_SPEC §8.3). Der Entwickler behält die Rechte auf Namensnennung und Veröffentlichung. Die Governance-Organisation erhält das Recht, die Methode für ihre Sprache zu nutzen, zu modifizieren, zu verbreiten und zu monetarisieren. Dies ist keine Strafe – es ist der eigentliche Sinn. Preisgelder finanzieren die Schaffung von Technologie, die der Sprachgemeinschaft gehört.

### 1.4 Manipulationsschutz

Preisschwellen werden gegen eine **Goldstandard-Evaluierung** definiert (geheimer Testdatensatz, ausgeführt von der Governance-Organisation in der Sandbox). Entwickler sehen die Testdaten niemals. Dies wird architektonisch durchgesetzt – es handelt sich nicht um eine Richtlinie, die auf Ehrlichkeit beruht. Siehe BENCHMARK_SPEC §8.2.

### 1.5 Korpuslizenzierung: Nicht-kommerzielle Korpora bleiben außerhalb der Preisspur

Einige Korpora, die während der Methodenentwicklung verwendet werden, tragen nicht-kommerzielle Lizenzen – zum Beispiel ist das EdTeKLA Cree Language Textbook-Korpus mit **CC BY-NC-SA 4.0** lizenziert. Diese Korpora sind **ausschließlich der Forschungs-/Entwicklungsspur vorbehalten**:

1. **Goldstandard-Korpora für Preise dürfen keine NC-lizenzierten Korpusinhalte einbetten.** Goldstandard-Testsegmente sind von der Gemeinschaft in Auftrag gegebene Originale (siehe Corpus Partnership Strategy) – von Menschen für den Preis verfasst, mit von Anfang an geklärten Rechten für Evaluierung und kommerziellen Einsatz.
2. **Eine Methode, die einen Preis beansprucht, darf keine NC-lizenzierten Korpusinhalte einbetten** (z. B. als Coaching-Daten, eingebettete Beispiele oder Nachschlagetabellen). Die übertragene Methode ist für den kommerziellen Einsatz durch die Governance-Organisation vorgesehen (BENCHMARK_SPEC §8.3, Method Submission Agreement §6); NC-lizenzierte Inhalte darin würden diesen Einsatz beeinträchtigen.
3. **Entwickler dürfen NC-lizenzierte Korpora frei zur Entwicklung und Selbstevaluierung verwenden** – genau dafür ist die Entwicklungsspur gedacht. Die Einschränkung betrifft das, was eingereicht und was eingesetzt wird, nicht die Art und Weise, wie ein Entwickler lernt.

### 1.6 Abhängigkeitsklassen bestimmen die Preisberechtigung

Sämtliche Preisevaluierung findet in einer Sandbox statt (§1.4), und preisgekrönte Methoden werden an die Governance-Organisation übertragen (§1.3). Beide Tatsachen erlegen dieselbe Einschränkung auf: **Alles, wovon eine Methode abhängt, muss etwas sein, das der Entwickler das Recht hat, in die Sandbox einzubringen und an die Gemeinschaft weiterzugeben.** Jede Einreichung deklariert eine Abhängigkeitsklasse – definiert in der [Method-Interface-Spezifikation](/docs/specifications/methods#method-validity-and-dependency-classes), mit Zulässigkeitsbedingungen im Method Submission Agreement §2.6 – und die Berechtigung richtet sich nach der Klasse:

| Abhängigkeitsklasse | Preisberechtigt? | Bedingungen |
|------------------|----------------|------------|
| **S** – eigenständig | ✅ Ja | Keine über die Schwellenbedingungen in §2 hinaus |
| **O** – offen extern (z. B. AGPL-FST, bei Einreichung gespiegelt) | ✅ Ja | Artefakte fixiert und in die Einreichung eingebunden (vendored); Lizenzen erlauben die Weitergabe an die Gemeinschaft; Copyleft-Bedingungen bleiben erhalten (die Gemeinschaft erhält dieselben Rechte, die die Lizenz allen gewährt) |
| **A1** – substituierbare LLM-Inferenz | ⚠️ Bedingt | Modell deklariert, fixiert und substituierbar (muss gegen ein von der Gemeinschaft gehostetes Open-Weight-Modell laufen); Evaluierung über das Sandbox-LLM-Gateway geleitet (🔲 geplant – A1-Methoden können keine Goldstandard-Bewertungen erzeugen, bis das Gateway betriebsbereit ist); die Übertragung umfasst das vollständige Rezept (Prompts, Coaching, Code), nicht das Modell |
| **A2** – nicht-substituierbare externe Daten-/Dienst-API | ❌ Noch nicht | Nicht berechtigt, bis der Rechteinhaber die Erlaubnis zur Sandbox-Einbindung und Übertragung erteilt. Auf der offenen Bestenliste mit sichtbarer „external dependency"-Kennzeichnung zulässig |
| **X** – gebündelte Inhalte ohne Rechte | ❌ Niemals | In jeder Spur unzulässig |

Die Klasse einer Methode ist die restriktivste Klasse unter ihren deklarierten Abhängigkeiten. Nicht deklarierte Abhängigkeiten jeglicher Klasse führen zum Ausschluss (§5).

---

## 2. Aktive Preispools

### 2.1 Der Founder's Prize — EN→Plains Cree (nêhiyawêwin)

| Feld | Wert |
|-------|-------|
| **Preispool** | **10.000 CAD** |
| **Sprachpaar** | Englisch → Plains Cree (EN→CRK) |
| **Finanziert von** | Gründer des Champollion-Projekts |
| **Status** | **AKTIV** – nimmt Einreichungen an |
| **Öffnet** | Sobald Goldstandard-Korpus + Governance-Organisation vorhanden sind |
| **Läuft ab** | Kein Ablaufdatum. Der Preis bleibt aktiv, bis er beansprucht oder ausdrücklich zurückgezogen wird. |

#### Schwellenbedingungen

Eine Methode beansprucht den Founder's Prize, indem sie **ALLE** der folgenden Bedingungen gleichzeitig erfüllt:

| # | Bedingung | Metrik | Schwellenwert | Begründung |
|---|-----------|--------|-----------|-----------|
| 1 | **Composite score** | `composite` (SCORING_SPEC §4) | **≥ 0.80** | Zwischen Deployable (0.70) und Fluent (0.85). Erfordert hohe Qualität über alle Metrikdimensionen hinweg – nicht nur morphologische Gültigkeit. |
| 2 | **FST-Akzeptanz** | `fst_acceptance_rate` (SCORING_SPEC §2.2) | **≥ 0.99 (99 %+)** | Praktisch alle Ausgabewörter müssen morphologisch gültige Formen sein, die vom GiellaLT-FST erkannt werden. Die 1-%-Toleranz berücksichtigt Sonderfälle (Eigennamen, Neologismen, Lehnwörter), die der FST legitimerweise nicht abdecken kann. Dies ist das maßgebliche Qualitätsgate für polysynthetische MT – wenn der FST mehr als 1 % der Wörter zurückweist, produziert die Methode Formen, die in der Sprache nicht existieren. Der gesamte Sinn dieses Preises besteht darin, ein System zu erwerben, das nichts entstellt. |
| 3 | **chrF++** | `chrf_plus_plus` (SCORING_SPEC §2.1) | **≥ 55.0** | Die Zeichen-n-Gramm-Überlappung muss 55 auf der Skala von 0–100 übersteigen. Stellt eine oberflächliche Ähnlichkeit mit den Referenzübersetzungen sicher, nicht nur morphologische Gültigkeit. |
| 4 | **Community-Validierung** | Menschliche Überprüfung (BENCHMARK_SPEC §7) | **≥ 70 % „acceptable" oder „excellent"** | Eine geschichtete Stichprobe von Ausgaben (≥30 Einträge über die Schwierigkeitsstufen 2–5) wird von ≥2 zweisprachigen CRK-Sprechern überprüft. Mindestens 70 % der überprüften Einträge müssen eine Bewertung „acceptable" oder „excellent" erhalten. |
| 5 | **Goldstandard-Evaluierung** | Sandbox-Ausführung (BENCHMARK_SPEC §8.2) | **Erforderlich** | Alle automatisierten Metriken müssen gegen das `gold_standard`-Korpussegment berechnet werden, ausgeführt von der Governance-Organisation in einer Sandbox-Umgebung. Bewertungen aus dem Entwicklungsdatensatz zählen nicht. |
| 6 | **Reproduzierbarkeit** | Fingerprint-Übereinstimmung (BENCHMARK_SPEC §3.8) | **±2 %** | Die Governance-Organisation muss in der Lage sein, die Methode erneut auszuführen und Bewertungen innerhalb von ±2 % der eingereichten Run Card zu erzielen. |

> **Warum 99+% FST?** Das zentrale Problem bei der maschinellen Übersetzung polysynthetischer Sprachen ist die Halluzination – LLMs produzieren Zeichenketten, die *aussehen* wie die Zielsprache, aber morphologisch ungültig sind. Eine Methode, die 95 % gültige Ausgabe produziert, hat immer noch 5 % erfundene Wörter – inakzeptables Rauschen für jeden produktiven Einsatz. Der Schwellenwert von 99 %+ verlangt nahezu null Halluzination, lässt aber den seltenen Sonderfall zu (einen Eigennamen, den der FST nicht kennt, einen legitimen Neologismus). Wenn eine Methode keine FST-Akzeptanz von 99 %+ erreichen kann, hat sie das Problem nicht gelöst.
>
> **Warum 0.80 composite?** Dieser Wert liegt zwischen Deployable (0.70) und Fluent (0.85). Eine Methode bei 0.80 mit einer FST-Akzeptanz von 99 %+ produziert Ausgaben, bei denen praktisch jedes Wort ein echtes Cree-Wort ist *und* die Gesamtqualität der Übersetzung über die Oberflächen-, Struktur- und Bedeutungsdimensionen hinweg hoch ist. Das Gate für die Community-Validierung (Bedingung #4) stellt sicher, dass es sich nicht nur um Metrikmanipulation handelt – Sprecher müssen bestätigen, dass die Ausgabe tatsächlich verwendbar ist.

#### Was dieser Schwellenwert in der Praxis bedeutet

Bei einem Composite-Wert von ≥ 0.80 mit FST ≥ 0.99 und chrF++ ≥ 55 würde ein zweisprachiger Sprecher typischerweise Folgendes sehen:

- **Praktisch jedes** Ausgabewort ist ein echtes Cree-Wort (der FST validiert 99 %+ – nahezu null halluzinierte Formen)
- Wesentliche grammatische Kategorien (Person, Numerus, Tempus) sind in den meisten Einträgen korrekt
- Die Wortstellung ist im Allgemeinen natürlich
- Die Bedeutung bleibt zuverlässig erhalten
- Verbleibende Fehler sind echte Sprachfehler (falsche Flexion, fehlerhafte Obviation, Animatheitsdiskrepanzen) – keine erfundenen Wörter
- Ein fließend Sprechender könnte die Ausgabe als hochwertigen Entwurf verwenden und sie deutlich schneller korrigieren als von Grund auf zu übersetzen

Dies ist ein System, das **die Sprache nicht entstellt.** Es mag nicht perfekt sein, aber jedes Wort, das es produziert, ist ein echtes Wort. Das ist die Mindesthürde für eine respektvolle maschinelle Übersetzung einer polysynthetischen Sprache.

---

## 3. Antragsverfahren für Preise

### 3.1 Einreichung

1. Der Entwickler reicht seine vollständige, ausführbare Methode bei der Governance-Organisation ein:
   - Den gesamten Quellcode
   - Alle Abhängigkeiten (Coaching-Daten, Wörterbücher, FST-Konfigurationen, Prompts)
   - Installations- und Ausführungsanweisungen
   - Eine README, die den Ansatz der Methode beschreibt
   - Eine Run Card aus dem Entwicklungsdatensatz mit ungefähren Bewertungen (zur Vorabprüfung)

2. Der Entwickler unterzeichnet die Teilnahmebedingungen, einschließlich:
   - Eigentumsübertragungsklausel (BENCHMARK_SPEC §8.3)
   - Erklärung, keine Evaluierungsdaten zum Training verwendet zu haben
   - Zusicherung der Reproduzierbarkeit

### 3.2 Evaluierung

1. Die Governance-Organisation installiert und führt die Methode in einem Sandbox-Harness gegen das `gold_standard`-Korpus aus
2. Automatisierte Metriken werden berechnet (composite, FST, chrF++ usw.)
3. Wenn die automatisierten Schwellenwerte erfüllt sind (Bedingungen 1–3), geht die Governance-Organisation zur Community-Überprüfung über
4. Wenn die automatisierten Schwellenwerte NICHT erfüllt sind, erhält der Entwickler Bewertungen und Rückmeldungen. Es wird keine Community-Überprüfung ausgelöst.

### 3.3 Community-Überprüfung

1. Eine geschichtete Stichprobe von Ausgaben (≥30 Einträge, abdeckend die Schwierigkeitsstufen 2–5) wird zweisprachigen Sprechern vorgelegt
2. Mindestens 2 unabhängige Prüfer bewerten jeden Eintrag
3. Bewertungsskala: **reject** / **gist** / **acceptable** / **excellent**
4. Wenn ≥70 % der Einträge von beiden Prüfern „acceptable" oder „excellent" erhalten, ist die Community-Validierung bestanden

### 3.4 Auszahlung

1. Alle 6 Bedingungen sind erfüllt
2. Die Governance-Organisation bestätigt das Ergebnis
3. Der Preis wird innerhalb von 30 Tagen nach Bestätigung ausgezahlt
4. Das Eigentum an der Methode wird gemäß BENCHMARK_SPEC §8.3 übertragen
5. Das Ergebnis wird auf der Bestenliste mit der Verifizierungsstufe „Community Validated" veröffentlicht

### 3.5 Mehrfache Einreichungen

- Derselbe Entwickler / dasselbe Team darf mehrfach einreichen
- Jede Einreichung wird unabhängig evaluiert
- Wird eine Methode verbessert und erneut eingereicht, zählt nur die neueste Run Card
- Der Preis wird an die **erste** Methode vergeben, die alle Schwellenwerte überwindet – er wird nicht aufgeteilt

### 3.6 Team-Einreichungen

- Teams und Elder-Youth-Paare sind berechtigt
- Die Verteilung des Preises innerhalb eines Teams liegt in der Verantwortung des Teams
- Alle Teammitglieder müssen die Teilnahmebedingungen unterzeichnen
- Die Namensnennung auf der Bestenliste führt alle Teammitglieder auf

---

## 4. Künftige Preispools

Der Founder's Prize ist der Ausgangspunkt. Weitere Preispools werden von Sponsoren finanziert. Jeder neue Preispool wird als neuer Unterabschnitt von §2 dokumentiert, mit jeweils eigenen:

- Preisbetrag und Währung
- Sprachpaar
- Sponsorennennung
- Schwellenbedingungen (die vom Founder's Prize abweichen können)
- Ablaufdatum (falls vorhanden)
- Etwaige Sonderbedingungen

### 4.1 Sponsor-Preisvorlage

Sponsoren finanzieren Preispools in beliebiger Höhe. Vorgeschlagene Stufen:

| Stufe | Betrag | Vorgeschlagener Schwellenwert |
|------|--------|---------------------|
| **Seed** | 5.000–15.000 $ | Deployable (composite ≥ 0.70) + Community-Validierung |
| **Breakthrough** | 25.000–50.000 $ | Fluent (composite ≥ 0.85) + Community-Validierung |
| **Grand Prize** | 100.000 $+ | Fluent + Mehrregister-Abdeckung + Einsatzintegration |

Sponsoren können auch Folgendes finanzieren:
- **Verbesserungsprämien** – feste Zahlung für jede Verbesserung von chrF++ um 5 Punkte gegenüber dem aktuellen Bestwert
- **Registerpreise** – separate Auszeichnungen für bestimmte Register (formell, zeremoniell, bildungsbezogen)
- **Geschwindigkeitspreise** – beste kostenbereinigte Bewertung (SCORING_SPEC §6.3)

### 4.2 Treuhandverwaltung des Preispools

Alle Preisgelder werden treuhänderisch verwahrt (verwaltet durch das Projekt oder einen benannten Treuhänder), bis die Schwellenbedingungen erfüllt sind. Läuft ein Preis ab, ohne beansprucht zu werden, werden die Mittel an den Sponsor zurückgegeben oder nach Ermessen des Sponsors einem neuen Preispool zugeführt.

---

## 5. Disqualifikation

Eine Einreichung wird disqualifiziert, wenn:

1. **Training mit Evaluierungsdaten.** Die Methode wurde Einträgen des `gold_standard`- oder `held_out`-Korpus ausgesetzt. (Architektonisch durch Sandbox-Ausführung verhindert – wird jedoch Hinweise auf eine Kontamination gefunden, wird das Ergebnis annulliert.)
2. **Nicht reproduzierbar.** Die Governance-Organisation kann die Bewertungen nicht innerhalb von ±2 % reproduzieren.
3. **Nicht deklarierte oder nicht berechtigte Abhängigkeiten.** Die Methode benötigt zur Laufzeit Zugriff auf externe Dienste über das hinaus, was ihr Abhängigkeitsmanifest deklariert, oder ihre effektive Abhängigkeitsklasse ist A2 oder X (§1.6). Deklarierte LLM-Inferenz der Klasse A1, die über das Evaluierungs-Gateway geleitet wird, ist zulässig; jede andere Netzwerkabhängigkeit zur Laufzeit – sowie jede nicht deklarierte Abhängigkeit jeglicher Klasse – führt zur Disqualifikation.
4. **Teilnahmebedingungen nicht unterzeichnet.** Alle Teammitglieder müssen der Eigentumsübertragung zustimmen.
5. **Manipulation festgestellt.** Die Ausgabe ist für die Metrik statt für die Übersetzungsqualität optimiert (durch Community-Überprüfung und/oder Manipulationsschutzprüfungen gemäß BENCHMARK_SPEC §9.3 erkannt).

---

## 6. Beziehung zu anderen Spezifikationen

| Dieses Dokument | Verweist auf | Für |
|--------------|-----------|-----|
| §2 Schwellenbedingungen | SCORING_SPEC §4 (composite), §2.1–2.2 (Metriken), §5 (Stufen) | Metrikdefinitionen und Skala |
| §2 Community-Validierung | BENCHMARK_SPEC §7 | Protokoll der menschlichen Überprüfung |
| §3 Sandbox-Ausführung | BENCHMARK_SPEC §8.2 | Souveränitätsmechanismus |
| §3 Eigentumsübertragung | BENCHMARK_SPEC §8.3 | Bedingungen der IP-Übertragung |
| §1.6 Abhängigkeitsklassen | Method-Interface-Spezifikation; Method Submission Agreement §2.6; BENCHMARK_SPEC §8.6 | Klassendefinitionen, Zulässigkeitsbedingungen, Sandbox-Netzwerkrichtlinie |
| §4 kostenbereinigte Preise | SCORING_SPEC §6.3 | Kostenbereinigte Formel |

---

## 7. Code-Spezifikations-Synchronisation

### 7.1 Kanonische Quelle

Dieses Dokument (`arena/website/docs/specifications/prize-spec.md`) ist die kanonische Quelle für:
- Preispool-Definitionen (§2)
- Schwellenbedingungen (§2.x)
- Antragsverfahren (§3)
- Disqualifikationsregeln (§5)

### 7.2 Implementierungsanforderungen

Wenn ein Preispool aktiviert wird:
1. Die Benutzeroberfläche der Bestenliste muss aktive Preise und ihre Schwellenbedingungen anzeigen
2. Run Cards, die die automatisierten Schwellenwerte erfüllen (Bedingungen 1–3), müssen für die Community-Überprüfung gekennzeichnet werden
3. Das Feld `quality_tier` im Run-Card-Schema erfasst bereits die Stufe („deployable", „fluent")
4. Es sind keine neuen Codeänderungen am Harness erforderlich – die Preisspezifikation ist eine Richtlinienebene oberhalb des bestehenden Scorings

---

*Preisstrukturen müssen mit den Bedingungen der Eigentumsübertragung vereinbar sein. Der Gewinner kann den Preis beanspruchen, aber die Methode wird zum Eigentum der Governance-Organisation, wenn sie die Deployable-Stufe erreicht. Dies ist beabsichtigt – der Preis finanziert die Schaffung von Technologie, die der Sprachgemeinschaft gehört.*