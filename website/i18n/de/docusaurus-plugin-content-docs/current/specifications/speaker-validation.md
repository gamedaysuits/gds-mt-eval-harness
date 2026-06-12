---
sidebar_position: 8
title: "Sprecher:innen-Validierungsprotokoll"
slug: '/specifications/speaker-validation'
---
# Protokoll zur Validierung durch Sprecher

> **Zweck.** Dieses Dokument legt genau fest, was wir von zweisprachigen Cree-Englisch-Sprechern benötigen, um die LYSS-Bewertungsmetriken zu validieren. Ohne diese Validierung sind unsere automatisierten Bewertungen technische Schätzungen und keine nachgewiesenen Qualitätsmessungen. Dies ist die mit Abstand wichtigste Lücke im Projekt.
>
> **Zielgruppe.** Gemeinschaftspartner, potenzielle Mitwirkende, Gutachter von Fördermitteln und das Projektteam.
>
> Zuletzt aktualisiert: 2026-06-07

---

## 1. Warum wir Sprecher benötigen

Das LYSS-Bewertungsframework (Linguistically-informed Yield & Structural Scoring) berechnet automatisierte Qualitätsbewertungen für Übersetzungen vom Englischen ins Plains Cree. Es verwendet drei zentrale Signale:

- **LYSS-fst**: Enthält die Ausgabe gültige Cree-Wörter? (geprüft durch den GiellaLT-Finite-State-Transducer)
- **LYSS-eq**: Ist die Ausgabe eine zulässige Variante der Referenzübersetzung? (geprüft durch die Äquivalenzklassen des Linters)
- **LYSS-sem**: Bewahrt die Ausgabe die Bedeutung des Quelltextes? (geprüft durch den semantischen Validator)

Diese Metriken erzeugen Zahlen. **Wir wissen nicht, ob diese Zahlen eine Bedeutung haben.** Der FST kann gültige Wörter ablehnen, die er nicht erkennt (Lehnwörter, Neologismen, Eigennamen). Der Linter übersieht möglicherweise gültige Äquivalenzen oder akzeptiert ungültige. Der semantische Validator beurteilt die Bedeutung möglicherweise falsch. Solange zweisprachige Sprecher uns nicht mitteilen, ob unsere automatisierten Bewertungen mit ihrem menschlichen Urteil über die Übersetzungsqualität übereinstimmen, raten wir nur.

Jede bedeutende MT-Bewertungsmetrik (BLEU, COMET, chrF++) wurde validiert, indem automatisierte Bewertungen mit Tausenden von menschlichen Qualitätsbeurteilungen verglichen wurden. Wir benötigen dasselbe – in kleinerem Umfang, da unsere Ressourcen begrenzt sind, aber mit derselben Strenge.

---

## 2. Was wir benötigen: Drei Aufgaben

### Aufgabe A: Bewertung der Übersetzungsqualität (Primär – insgesamt ~8 Stunden)

**Was:** Bewertung von 200 maschinell erzeugten Übersetzungen vom Englischen ins Cree auf zwei Skalen.

**Wer:** 3 oder mehr zweisprachige Plains-Cree-Englisch-Sprecher mit Lesefertigkeit in SRO (Standard Roman Orthography).

**Wie es funktioniert:**

1. Wir stellen eine Tabelle oder ein Webformular mit 200 Zeilen bereit. Jede Zeile enthält:
   - den englischen Quellsatz
   - eine maschinell erzeugte Cree-Übersetzung
   - (optional) eine Cree-Referenzübersetzung zum Vergleich

2. Für jede Übersetzung bewertet der Sprecher zwei Aspekte:

   **Adäquatheit** (sagt sie das Richtige aus?):
   | Score | Label | Bedeutung |
   |-------|-------|---------|
   | 1 | None | Die Übersetzung hat nichts mit dem Quelltext zu tun |
   | 2 | Little | Einige Wörter stimmen überein, aber die Gesamtbedeutung ist falsch |
   | 3 | Much | Die Kernbedeutung ist vorhanden, aber wichtige Teile fehlen oder sind falsch |
   | 4 | Most | Fast alles ist korrekt, geringfügige Bedeutungslücken |
   | 5 | All | Die Übersetzung vermittelt die Bedeutung des Quelltextes vollständig |

   **Flüssigkeit** (klingt es wie echtes Cree?):
   | Score | Label | Bedeutung |
   |-------|-------|---------|
   | 1 | Incomprehensible | Dies ist kein Cree |
   | 2 | Disfluent | Einzelne Wörter könnten Cree sein, aber der Satz ist fehlerhaft |
   | 3 | Non-native | Verständlich, aber eindeutig nicht so, wie ein Cree-Sprecher es sagen würde |
   | 4 | Good | Natürlich klingend mit geringfügiger Ungelenkheit |
   | 5 | Flawless | Ein Cree-Sprecher hätte dies schreiben können |

3. Optional kann der Sprecher eine Freitextnotiz hinzufügen, die seine Bewertung erläutert (z. B. „falsche belebte/unbelebte Kongruenz beim Verb“, „dies ist th-Dialekt, aber ich bewerte auf Grundlage des y-Dialekts“).

**Zeitschätzung:** ~2,5 Minuten pro Übersetzung × 200 Übersetzungen = ~8 Stunden. Kann auf mehrere Sitzungen aufgeteilt werden (z. B. 4 × 2-stündige Sitzungen über 2 Wochen).

**Vergütung:** 50–65 CAD/Stunde (entsprechend den Sprechervergütungssätzen gemäß BENCHMARK_SPEC §10.3). Gesamtbetrag pro Sprecher: 400–520 CAD. Für 3 Sprecher: **1.200–1.560 CAD**.

**Was wir damit tun:** Wir berechnen die Korrelation zwischen unseren automatisierten LYSS-Bewertungen und den Sprecherbewertungen. Wenn LYSS-fst mit den Flüssigkeitsbewertungen und LYSS-sem mit den Adäquatheitsbewertungen korreliert, sind die Metriken validiert. Andernfalls wissen wir, wo wir nachbessern müssen.

---

### Aufgabe B: Validierung der Linter-Äquivalenz (~2 Stunden)

**Was:** Überprüfung von 50 Paaren von Cree-Übersetzungen, die unser Linter als „äquivalent“ klassifiziert, und Mitteilung, ob sie tatsächlich dasselbe bedeuten.

**Wer:** 1–2 zweisprachige Sprecher (können dieselben Sprecher wie in Aufgabe A sein).

**Wie es funktioniert:**

1. Wir stellen 50 Paare bereit. Jedes Paar enthält:
   - den englischen Quelltext
   - Übersetzung A (die Referenz)
   - Übersetzung B (eine Variante, die unser Linter als äquivalent bezeichnet)
   - den Äquivalenzgrund (z. B. „Wortstellungspermutation“, „orthografische Variante“, „optionale Partikel entfernt“)

2. Für jedes Paar beantwortet der Sprecher:
   - **Gleiche Bedeutung?** Ja / Nein / Kontextabhängig
   - **Beide natürlich?** Ja / A ist besser / B ist besser / Keine ist natürlich
   - **Anmerkungen** (optionaler Freitext)

**Zeitschätzung:** ~2 Minuten pro Paar × 50 Paare = ~2 Stunden.

**Vergütung:** 50–65 CAD/Stunde × 2 Stunden = **100–130 CAD pro Sprecher**.

**Was wir damit tun:** Wir berechnen die Präzision jeder Äquivalenzklasse. Wenn Sprecher sagen, dass 90 % der „Wortstellungs“-Äquivalenzen tatsächlich äquivalent sind, ist diese Klasse validiert. Wenn sie sagen, dass 40 % der „Lemma-Synonym“-Äquivalenzen falsch sind, wissen wir, dass wir diese Klasse korrigieren oder entfernen müssen.

---

### Aufgabe C: Überprüfung von FST-Falschablehnungen (~1,5 Stunden)

**Was:** Überprüfung von 100 Cree-Wörtern, die der FST-Analyzer ablehnt (als ungültige Cree-Wörter einstuft), und Mitteilung, ob sie tatsächlich gültig sind.

**Wer:** 1 zweisprachiger Sprecher mit fundierten Kenntnissen des Cree-Wortschatzes.

**Wie es funktioniert:**

1. Wir führen den FST-Analyzer auf unserem EDTeKLA-Goldstandard-Korpus mit 436 Einträgen aus und sammeln jedes Wort, das er ablehnt.
2. Wir legen dem Sprecher bis zu 100 abgelehnte Wörter mit ihrem Satzkontext vor.
3. Für jedes Wort beantwortet der Sprecher:
   - **Ist dies ein gültiges Cree-Wort?** Ja / Nein / Unsicher
   - **Falls ja, welche Art?** Etabliertes Wort / Lehnwort / Name / Dialektform / Neologismus / Sonstiges
   - **Anmerkungen** (optional)

**Zeitschätzung:** ~1 Minute pro Wort × 100 Wörter = ~1,5 Stunden.

**Vergütung:** 50–65 CAD/Stunde × 1,5 Stunden = **75–100 CAD**.

**Was wir damit tun:** Wir berechnen die Falschablehnungsrate des FST. Wenn der FST 50 Wörter ablehnt und Sprecher sagen, dass 30 davon gültig sind, beträgt die Falschablehnungsrate 60 % – unzulässig hoch, was eine Positivliste für Lehnwörter/Ausnahmen erfordert. Wenn Sprecher sagen, dass nur 5 gültig sind, beträgt die Falschablehnungsrate 10 % – die Metrik ist zuverlässig.

---

## 3. Gesamter Sprecheraufwand

| Aufgabe | Benötigte Sprecher | Stunden pro Sprecher | Kosten pro Sprecher | Gesamtkosten |
|------|----------------|-------------------|-----------------|------------|
| A: Qualitätsbewertung | 3 | ~8 Stunden | 400–520 $ | 1.200–1.560 $ |
| B: Linter-Validierung | 2 | ~2 Stunden | 100–130 $ | 200–260 $ |
| C: FST-Überprüfung | 1 | ~1,5 Stunden | 75–100 $ | 75–100 $ |
| **Gesamt** | **3 Sprecher** | **~11,5 Stunden (max. pro Sprecher)** | **575–750 $ (max.)** | **1.475–1.920 $** |

Wenn dieselben 3 Sprecher alle Aufgaben übernehmen: **~11,5 Stunden je Person über 2–4 Wochen, 575–750 $ je Person**.

Ein einzelner Sprecher, der nur Aufgabe A übernimmt, würde **~8 Stunden über 2 Wochen für 400–520 $** aufwenden.

---

## 4. Qualifikationen der Sprecher

**Erforderlich:**
- Zweisprachigkeit in Plains Cree und Englisch
- Lesefertigkeit in SRO (Standard Roman Orthography)
- Sicherheit bei der Bewertung von Übersetzungen auf einer strukturierten Skala

**Bevorzugt:**
- Erfahrung mit dem y-Dialekt (dem Dialekt, der in unserem Referenzkorpus von EDTeKLA verwendet wird)
- Lehr- oder Übersetzungserfahrung (liefert ein kalibriertes Qualitätsurteil)
- Vertrautheit mit verschiedenen Registern (formell, lehrbezogen, umgangssprachlich)

**Nicht erforderlich:**
- Technische oder NLP-Kenntnisse (wir stellen alle Werkzeuge und den Kontext bereit)
- Computerkenntnisse (die Bewertungsoberfläche wird eine einfache Tabelle oder ein Webformular sein)
- Frühere Beteiligung am Champollion-Projekt

---

## 5. Datenverwaltung

Alle Beiträge von Sprechern unterliegen den OCAP®-orientierten Datenrichtlinien des Projekts:

- **Eigentum:** Die Qualitätsbewertungen der Sprecher bleiben ihr geistiger Beitrag. Sie werden in jeder Veröffentlichung namentlich (oder nach ihrer Wahl anonym) genannt.
- **Kontrolle:** Sprecher können ihre Bewertungen jederzeit zurückziehen. Ein Widerruf entfernt ihre Daten aus allen Analysen.
- **Zugriff:** Bewertungsdaten werden auf einer Infrastruktur gespeichert, die von der Governance-Organisation der Gemeinschaft (sobald eingerichtet) kontrolliert wird, oder auf der vom Sprecher bevorzugten Plattform.
- **Besitz:** Rohbewertungsdaten werden niemals veröffentlicht. In Veröffentlichungen erscheinen nur aggregierte Statistiken (Korrelationen, Übereinstimmung zwischen den Annotatoren).
- **Vergütung:** Sprecher werden für ihre Zeit bezahlt, unabhängig davon, ob wir ihre Bewertungen verwenden. Die Zahlung ist nicht an Ergebnisse gebunden.

---

## 6. Was Sprecher erhalten

Über die Vergütung hinaus:

- **Mitautorschaft** an jeder Veröffentlichung, die ihre Bewertungen verwendet (sofern gewünscht)
- **Danksagung** in der gesamten Projektdokumentation
- **Frühzeitiger Zugang** zu den Bewertungswerkzeugen und -ergebnissen
- **Mitsprache** bei der Verwendung der Metriken – wenn ein Sprecher sagt: „Ihr Linter liegt bei X falsch“, korrigieren wir den Linter
- **Vetorecht** bei der Veröffentlichung von Ergebnissen, die sie als problematisch empfinden

---

## 7. So beginnen Sie

Wenn Sie ein zweisprachiger Cree-Englisch-Sprecher sind und teilnehmen möchten, oder wenn Sie jemanden kennen, der dies tun könnte:

1. **Kontaktieren Sie uns** unter [project email/contact] – keine Verpflichtung erforderlich, nur ein Gespräch
2. **Wir erklären die Aufgaben** in einfacher Sprache (ohne Fachjargon)
3. **Sie wählen die Aufgaben aus**, an denen Sie interessiert sind (A, B, C oder eine beliebige Kombination)
4. **Wir vereinbaren einen Zeitplan**, der für Sie passt (2-Stunden-Blöcke, flexible Terminierung)
5. **Sie bewerten Übersetzungen** über eine Tabelle oder ein Webformular – von überall aus, zu Ihrer eigenen Zeit
6. **Wir zahlen umgehend** – innerhalb von 2 Wochen nach Abschluss jedes Aufgabenblocks

---

## 8. Was danach geschieht

Mit den Validierungsdaten der Sprecher können wir:

1. **Die Metrik-Korrelationen veröffentlichen** – um nachzuweisen (oder zu widerlegen), dass LYSS-Bewertungen das menschliche Urteil widerspiegeln
2. **Die Metriken neu kalibrieren** – durch Anpassung von Gewichtungen, Schwellenwerten und Äquivalenzklassen auf Grundlage des Sprecher-Feedbacks
3. **Den Linter korrigieren** – durch Entfernen falscher Äquivalenzen und Hinzufügen fehlender
4. **Die FST-Positivliste korrigieren** – durch Hinzufügen gültiger Wörter, die der FST fälschlicherweise ablehnt
5. **Bei einem akademischen Forum einreichen** – mit Sprechern als Mitautoren, wodurch LYSS als validierte Metrik für die MT-Bewertung polysynthetischer Sprachen etabliert wird

Ohne Sprechervalidierung bleibt LYSS ein technisches Werkzeug. Mit ihr wird LYSS zu einer wissenschaftlich fundierten Bewertungsmetrik. Das ist der Unterschied zwischen „wir haben etwas gebaut“ und „wir haben bewiesen, dass es funktioniert“.