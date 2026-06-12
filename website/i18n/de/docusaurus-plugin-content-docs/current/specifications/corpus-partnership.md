---
sidebar_position: 9
title: "Strategie für Korpus-Partnerschaften"
slug: '/specifications/corpus-partnership'
---
# Strategie für Korpus-Partnerschaften: Aufbau von Evaluationskorpora über akademische linguistische Fachbereiche

> **Zweck.** Dieses Dokument beschreibt den vollständigen Arbeitsablauf zum Aufbau eines Korpus für die Evaluation maschineller Übersetzung im Rahmen einer Partnerschaft mit einem linguistischen Fachbereich. Es behandelt, was wir vom Fachbereich erwarten, wie das Korpus aufgebaut sein muss, wie es kryptografisch versiegelt wird, wie die Evaluation in der Sandbox funktioniert und was der Fachbereich im Gegenzug erhält. Dies ist das Dokument, das Sie zu einem Treffen mit einem potenziellen akademischen Partner mitbringen.
>
> **Zielgruppe.** Fachbereichsleitungen, Hauptforschende (Principal Investigators), Forschungskoordinatorinnen und -koordinatoren sowie Leiterinnen und Leiter von Sprachprogrammen für indigene Sprachen an Universitäten mit aktiven Programmen zur Sprachdokumentation oder NLP.
>
> **Begleitdokumente:**
> - [Speaker Validation Protocol](/docs/specifications/speaker-validation) — die Anfrage an zweisprachige Sprecherinnen und Sprecher, bestehende Übersetzungen zu *markieren* (Qualitätsbewertung, Linter-Validierung, FST-Überprüfung)
> - [Benchmark Specification](/docs/specifications/benchmark) — die vollständige technische Spezifikation für Korpora, Run Cards und Evaluationsprotokolle
> - [Data Sovereignty](/docs/sovereignty/data-sovereignty) — OCAP®, CARE und warum die Übertragung von Eigentumsrechten von Bedeutung ist
>
> Zuletzt aktualisiert: 2026-06-07

---

## 1. Was diese Partnerschaft hervorbringt

Ein **versiegeltes Evaluationskorpus**: eine kuratierte Sammlung paralleler Textpaare (Ausgangssprache → Zielsprache), die zur Referenzgrundlage (Ground Truth) für die Messung der Qualität maschineller Übersetzung wird. Methoden werden in einer Sandbox an diesem Korpus getestet — die Entwicklerinnen und Entwickler sehen die Testdaten niemals.

Die Partnerschaft bringt drei Artefakte hervor:

| Artefakt | Was es ist | Wer es kontrolliert |
|----------|-----------|-----------------|
| **Entwicklungskorpus** | 100–200+ öffentliche parallele Textpaare für die Methodenentwicklung | Offen veröffentlicht (CC BY-NC-SA 4.0 oder gleichwertig) |
| **Goldstandard-Testsatz** | 50–150 geheime parallele Textpaare für die offizielle Evaluation | Community-Governance-Organisation (kryptografisch versiegelt) |
| **Diagnostische Test-Suite** | 10–50 gezielte kontrastive Paare zur Prüfung spezifischer linguistischer Phänomene | Offen veröffentlicht |

Das Entwicklungskorpus ermöglicht es jeder Person, Übersetzungsmethoden zu entwickeln. Der Goldstandard-Satz stellt sicher, dass diese Methoden ehrlich getestet werden. Die diagnostische Suite deckt spezifische Fehlerarten auf (z. B. „Kann dieses System Obviation verarbeiten?").

---

## 2. Was der Fachbereich tun muss

### Phase 1: Korpus-Design (2–4 Wochen, Arbeitszeit der Forschenden)

**Leitung:** PI oder Postdoc mit Fachkenntnissen in der Zielsprache.

1. **Auswahl der Domänen des Ausgangsmaterials.** Wählen Sie 4–6 reale Domänen aus, in denen Übersetzung von der Sprachgemeinschaft tatsächlich benötigt wird. Unsere Taxonomie unterstützt 16 Domänen (siehe Benchmark Spec §2.7):

   | Priorität | Domäne | Begründung |
   |----------|--------|-----|
   | 🔴 Hoch | `edu` — Educational | Lehrbücher, Lehrpläne — unmittelbarer Bedarf der Gemeinschaft |
   | 🔴 Hoch | `gov` — Government | Dokumente des Band Council, politische Maßnahmen — praktischer täglicher Bedarf |
   | 🔴 Hoch | `medical` — Health | Aufnahmeformulare für Kliniken, Gesundheitsinformationen — sicherheitskritisch |
   | 🟡 Mittel | `conv` — Conversational | Alltagssprache — etabliert eine grundlegende Sprachfertigkeit |
   | 🟡 Mittel | `legal` — Legal | Rechtsdokumente, Verträge — Bedeutung für die Gemeinschaft |
   | 🟢 Niedriger | `literary` — Literary/Cultural | Geschichten, mündliche Überlieferungen — kulturelle Bewahrung |

2. **Erstellen Sie ein Korpus-Design-Dokument**, das Folgendes festlegt:
   - Zielgröße pro Segment (development, gold_standard, diagnostic)
   - Verteilung der Schwierigkeitsstufen (siehe §3.3 unten)
   - Register- und Domänenabdeckung
   - Auswahlkriterien für Ausgangssätze (kein synthetischer Text, nicht ausschließlich biblische Texte)
   - Rekrutierungsplan für Sprecherinnen und Sprecher

3. **Reichen Sie das Design bei uns zur Überprüfung ein.** Wir validieren es anhand des Korpus-Schemas (Benchmark Spec §2) und geben innerhalb einer Woche Rückmeldung.

### Phase 2: Erstellung der Ausgangssätze (4–8 Wochen, Arbeitszeit der Sprecherinnen und Sprecher)

**Leitung:** Forschungskoordination in Zusammenarbeit mit zweisprachigen Sprecherinnen und Sprechern.

1. **Generieren oder wählen Sie Ausgangssätze aus** über die geplanten Domänen und Schwierigkeitsstufen hinweg. Quellen können sein:
   - Bestehende veröffentlichte zweisprachige Materialien (Lehrbücher, Regierungsdokumente)
   - Neu elizitierte Sätze, die zur Abdeckung spezifischer linguistischer Phänomene konzipiert sind
   - Adaptiert aus realen Dokumenten (Tagesordnungen des Band Council, Klinikformulare, Bildungsmaterialien)

2. **Jeder Ausgangssatz muss Folgendes aufweisen:**
   - Domänen-Tag (aus der Taxonomie mit 16 Codes)
   - Register-Tag (conversational, formal, technical, ceremonial, educational)
   - Kontext-Tag (greeting, declaration, question, instruction, narrative, label, error)
   - Geschätzte Schwierigkeitsstufe (1–5, siehe §3.3)
   - Provenienz-Tag (textbook, elicited, corpus, gold_standard)

3. **Übersetzen Sie jeden Ausgangssatz** in die Zielsprache, durchgeführt von zweisprachigen Sprecherinnen und Sprechern. Mehrere Referenzübersetzungen pro Eintrag sind wertvoll, aber nicht erforderlich.

4. **Optional können Sie eine morphologische Analyse hinzufügen** für jede Referenzübersetzung:
   - Interlinearglossierung (Aufschlüsselung Morphem für Morphem)
   - FST-Tag-Zeichenkette (sofern ein FST für die Sprache existiert)
   - Anmerkungen der Übersetzenden zu dialektalen Varianten, Mehrdeutigkeit oder kulturellem Kontext

### Phase 3: Qualitätssicherung (2–4 Wochen)

**Leitung:** Linguistin oder Linguist mit Fachkenntnissen in der Zielsprache.

1. **Gegenüberprüfung (Cross-Review).** Jede Übersetzung sollte von mindestens einer weiteren zweisprachigen Person überprüft werden, die nicht die ursprüngliche Übersetzung erstellt hat. Die überprüfende Person prüft:
   - Ist die Übersetzung korrekt?
   - Klingt sie natürlich?
   - Ist die Schwierigkeitsbewertung korrekt?
   - Gibt es akzeptable Varianten, die vermerkt werden sollten?

2. **Durchlauf durch unseren Schema-Validator.** Wir stellen ein Skript bereit, das das Korpus anhand des Eintragsschemas validiert (Benchmark Spec §2.2). Es prüft:
   - Vorhandensein der erforderlichen Felder
   - Gültigkeit der Domänencodes
   - Schwierigkeitsstufen sind ganze Zahlen von 1–5
   - Keine doppelten IDs
   - Zeichenkodierung (UTF-8 NFC-Normalisierung)

3. **Sofern ein FST für die Sprache existiert,** lassen Sie die Referenzübersetzungen durch dieses laufen. Jedes Wort in der Referenz sollte FST-gültig sein. Wörter, die es nicht sind (Lehnwörter, Neologismen, Eigennamen), sollten in einer Positivliste (Allowlist) dokumentiert werden.

### Phase 4: Segmentierung und Versiegelung (1 Woche, unsere Entwicklungsarbeit)

**Leitung:** Champollion-Team, mit Überprüfung durch den Fachbereich.

1. **Stratifizierte Aufteilung.** Wir teilen das Korpus mittels deterministischer Zufallsstichproben in Segmente auf (Seed dokumentiert, reproduzierbar):

   | Segment | Zielgröße | Zugriff |
   |---------|------------|--------|
   | `development` | 60 % der Einträge (mind. 100) | Öffentlich |
   | `gold_standard` | 30 % der Einträge (mind. 50) | Geheim, versiegelt |
   | `held_out` | 10 % der Einträge (mind. 10) | Geheim, versiegelt, bis zur Aktivierung nie verwendet |

   Die Aufteilung bewahrt die Verteilung der Schwierigkeitsstufen (stratifizierte Stichprobe), sodass jedes Segment eine proportionale Repräsentation über alle Stufen hinweg aufweist.

2. **Kryptografische Versiegelung** der Segmente gold_standard und held_out:

   ```
   1. SHA-256 hash of each entry (source + reference + metadata)
   2. SHA-256 hash of the complete segment file
   3. Segment file encrypted with AES-256-GCM
   4. Encryption key split using Shamir Secret Sharing (2-of-3 threshold)
   5. Key shares distributed to:
        - Share 1: Community governance organization
        - Share 2: Academic department partner
        - Share 3: Champollion project (escrow)
   6. Hash manifest published to a public commit (proves the corpus existed
      at a specific time without revealing its contents)
   ```

3. **Das Segment development** wird in das öffentliche Repository übernommen und mit vollständiger Lizenzierung veröffentlicht.

4. **Das Segment diagnostic** ist ebenfalls öffentlich — es prüft spezifische linguistische Phänomene (siehe §3.4).

### Phase 5: Integration und Launch (1–2 Wochen, unsere Entwicklungsarbeit)

1. **Konfiguration des Harness.** Wir fügen die Sprache zum Evaluations-Harness hinzu:
   - Sprachkarte erstellt oder verifiziert
   - Korpus im Datensatz-Register registriert
   - LYSS-Metriken konfiguriert (LYSS-fst, sofern FST verfügbar, LYSS-eq, sofern Linter-Regeln existieren)
   - Standard-Scoring-Profil ausgewählt (Profil A, sofern FST verfügbar, andernfalls Profil B)

2. **Baseline-Benchmark.** Wir führen einen Durchlauf mit 12 Modellen gegen das Segment development durch, um die Bestenliste mit initialen Werten zu befüllen.

3. **Öffentliche Ankündigung.** Die Sprache erscheint auf der Arena-Bestenliste mit einem Live-Benchmark für das Segment development. Der Fachbereich wird als Korpus-Partner genannt.

---

## 3. Wie das Korpus aufgebaut sein muss

### 3.1 Format

Jede Korpus-Datei ist ein JSON-Dokument, das dem Schema in Benchmark Spec §2.1–§2.2 folgt:

```json
{
  "dataset": {
    "id": "crk-ualberta-v1",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "source_language": "en",
    "target_language": "crk",
    "created": "2026-09-15",
    "license": "CC-BY-NC-SA-4.0",
    "provenance": ["textbook", "elicited", "gold_standard"]
  },
  "entries": [
    {
      "id": 1,
      "source": "I see the dog",
      "reference": "niwâpamâw atim",
      "segment": "development",
      "difficulty": 2,
      "provenance": "textbook",
      "register": "conversational",
      "context": "declaration",
      "domain": "edu",
      "morphological_analysis": "ni-wâpam-âw atim | 1sg-see.TA-3sg.DIR dog.AN",
      "notes": "Animate noun (atim); direct form because speaker is proximate"
    }
  ]
}
```

### 3.2 Mindestgrößenanforderungen

| Segment | Mindestanzahl Einträge | Empfohlen |
|---------|----------------|-------------|
| `development` | 100 | 200–300 |
| `gold_standard` | 50 | 100–150 |
| `diagnostic` | 10 | 30–50 |
| `held_out` | 10 | 20–30 |
| **Gesamt** | **170** | **350–530** |

### 3.3 Schwierigkeitsverteilung

Das Korpus muss Einträge über alle fünf Schwierigkeitsstufen hinweg enthalten, gewichtet zugunsten der Stufen 2–4:

| Stufe | Beschreibung | Zielverteilung |
|------|-------------|-------------------|
| 1 — Grundwortschatz | Einzelne Wörter, gängige Grüße, Zahlen | 10–15 % |
| 2 — Einfache Sätze | SVO, Präsens | 25–30 % |
| 3 — Mittlere Komplexität | Vergangenheits-/Zukunftsform, Possessive, Belebtheit | 30–35 % |
| 4 — Komplexe Morphologie | Obviation, Passiv, Konjunktordnung, Relativsätze | 15–20 % |
| 5 — Fortgeschritten | Mehrgliedrige Sätze, formales Register, zeremoniell, idiomatisch | 5–10 % |

### 3.4 Diagnostische Test-Suite

Das Segment diagnostic prüft spezifische linguistische Phänomene mithilfe **kontrastiver Paare**: eine korrekte Übersetzung und eine minimal abweichende inkorrekte Übersetzung. Wenn die Metrik eines Systems die korrekte Variante höher bewertet, gilt der Test als bestanden.

Bei polysynthetischen Sprachen sollte die diagnostische Suite Folgendes anvisieren:

| Phänomen | Beispiel (Cree) | Was es prüft |
|-----------|----------------|--------------|
| **Belebtheitskongruenz** | atim (AN) vs. maskisin (IN) — unterschiedliche Verbformen | Weiß das System, welche Nomen belebt sind? |
| **Obviation** | Proximate vs. obviative dritte Person | Verfolgt es die Hierarchie der dritten Person? |
| **Inversmarkierung** | Direkte vs. inverse Verbformen | Bewältigt es Patiens-überrangt-Agens? |
| **Konjunkt/Independent** | Verbordnung in Haupt- vs. Nebensatz | Verwendet es das richtige Verbparadigma? |
| **Inklusiv/Exklusiv** | „Wir (einschließlich dir)" vs. „Wir (ausschließlich dir)" | Unterscheidet es die Formen der ersten Person Plural? |

Für andere Sprachfamilien identifizieren Sie die 3–5 diagnostisch aussagekräftigsten Phänomene, die kompetente von inkompetenter Übersetzung unterscheiden. Die linguistische Fachkenntnis des Fachbereichs ist hier unerlässlich — dies sind die Tests, die nur eine Fachperson zu schreiben wüsste.

### 3.5 Was wir NICHT wünschen

| Anti-Muster | Begründung |
|-------------|-----|
| **Ausschließlich biblische Texte** | Archaisches Register, liturgischer Wortschatz, formelhafte Struktur. OMT-1600 hat 1.560 Sprachen auf diese Weise evaluiert — wir vermeiden dies bewusst. |
| **Synthetische Evaluationspaare** | Durch LLM generierte Referenzen unterlaufen den Zweck der Evaluation. Die Referenz muss von Menschen verfasst sein. |
| **Korpora mit nur einem Register** | Alles formal oder alles umgangssprachlich. Reale Übersetzung umfasst mehrere Register. |
| **Nur Schwierigkeitsstufe 1** | Einzelne Wörter und Grüße prüfen keine Übersetzung — sie prüfen das Nachschlagen von Vokabeln. |
| **Maschinell übersetzte Referenzen** | Die Verwendung von Google-Translate-Ausgaben als „Referenz" ist zirkulär. |
| **Sätze ohne Kontext-Tag** | Wir müssen die kommunikative Funktion für die diagnostische Analyse kennen. |

---

## 4. Kryptografische Versiegelung und Sandbox-Tests

### 4.1 Warum den Testsatz versiegeln?

Herkömmliche ML-Benchmarks veröffentlichen Testsätze offen. Nach der Veröffentlichung werden moderne LLMs irgendwann darauf trainieren (absichtlich oder durch Web-Scraping), wodurch die Werte unzuverlässig werden. Bei Daten indigener Sprachen besteht eine zusätzliche Sorge: Veröffentlichte linguistische Daten können ohne Zustimmung der Gemeinschaft verwendet werden.

Die Versiegelung gewährleistet:
- **Integrität des Testsatzes:** Methoden können nicht zu Daten überangepasst werden (Overfitting), die sie nie gesehen haben
- **Datensouveränität:** Die Gemeinschaft kontrolliert, wer gegen ihre Daten evaluiert
- **Dauerhafte Aktualität:** Der Testsatz wird niemals kontaminiert

### 4.2 Wie Sandbox-Tests funktionieren

```
Developer workflow:
  1. Developer builds a translation method using the PUBLIC development corpus
  2. Developer tests locally against the development segment (unlimited, self-serve)
  3. When ready, developer submits their complete method (code + config + coaching data)
  4. Governance org installs the method in the evaluation sandbox
  5. Sandbox runs the method against the SEALED gold-standard test set
  6. Only scores are returned to the developer
  7. Developer never sees the source sentences or reference translations

The sandbox:
  - Runs on governance-controlled infrastructure
  - Has selective network access (LLM APIs only, no exfiltration)
  - Produces a tamper-proof run card (SHA-256 hash of all inputs and outputs)
  - Logs all execution for audit purposes
  - Can be inspected by the governance org at any time
```

### 4.3 Schlüsselverwaltung

Der Verschlüsselungsschlüssel für den versiegelten Testsatz wird mittels Shamir Secret Sharing mit einem Schwellenwert von 2 von 3 aufgeteilt:

| Inhaber des Anteils | Rolle | Widerrufsbefugnis |
|-------------|------|-----------------|
| **Community-Governance-Organisation** | Hauptverwahrer | Kann den Evaluationszugriff einseitig widerrufen |
| **Akademischer Fachbereichspartner** | Mitverwahrer | Kann an der Schlüsselrekonstruktion teilnehmen |
| **Champollion-Projekt** | Treuhand | Kann nicht allein auf Daten zugreifen; gewährleistet Kontinuität, falls andere Parteien nicht verfügbar werden |

Beliebige 2 von 3 Anteilen rekonstruieren den Schlüssel. Das bedeutet:
- Die Gemeinschaft + der Fachbereich können ohne Champollion auf die Daten zugreifen
- Die Gemeinschaft + Champollion können ohne den Fachbereich auf die Daten zugreifen
- Champollion allein kann NIEMALS auf die Daten zugreifen

### 4.4 Hash-Manifeste

Wenn das Korpus versiegelt wird, wird ein **Hash-Manifest** in einem öffentlichen Git-Commit veröffentlicht:

```json
{
  "corpus_id": "crk-ualberta-v1",
  "seal_date": "2026-09-15T00:00:00Z",
  "segments": {
    "development": {
      "entry_count": 200,
      "sha256": "a3f7c...",
      "access": "public"
    },
    "gold_standard": {
      "entry_count": 100,
      "sha256": "b8d2e...",
      "access": "sealed",
      "key_scheme": "shamir-2-of-3"
    },
    "held_out": {
      "entry_count": 20,
      "sha256": "c9e4f...",
      "access": "sealed",
      "key_scheme": "shamir-2-of-3"
    },
    "diagnostic": {
      "entry_count": 30,
      "sha256": "d1a3b...",
      "access": "public"
    }
  },
  "total_entries": 350,
  "manifest_sha256": "e2b5c..."
}
```

Dies belegt:
- Das Korpus existierte zu einem bestimmten Zeitpunkt
- Es hat eine bekannte Größe und Struktur
- Jede Änderung an den versiegelten Segmenten würde die Hash-Kette zerstören
- Die Gemeinschaft kann überprüfen, dass ihre Daten nicht manipuliert wurden

---

## 5. Was der Fachbereich erhält

### 5.1 Forschungsinfrastruktur

| Ressource | Beschreibung |
|-------|------------|
| **Evaluations-Harness** | Ein funktionierendes, getestetes Evaluations-Framework für ihre Sprache — spart Monate an Werkzeugentwicklung |
| **LYSS-Metriken** | Sprachspezifische Evaluationsmetriken (LYSS-fst, LYSS-eq, LYSS-sem), konfiguriert für ihre Sprache — sofern FST- und Wörterbuchressourcen existieren |
| **Bestenliste** | Eine öffentliche, live aktualisierte Bestenliste, die den Stand der Technik für ihr Sprachpaar zeigt |
| **Baseline-Benchmark** | Durchlauf mit 12 Modellen, der sofortige, publizierbare Baselines liefert |
| **Diagnostische Test-Suite** | Gezielte Tests für spezifische linguistische Phänomene — wiederverwendbar für andere Evaluationen |

### 5.2 Publikationen

Die Korpus-Erstellung und die Evaluationsergebnisse unterstützen mehrere Publikationen:

| Beitrag | Veranstaltung | Rolle des Fachbereichs |
|-------|-------|-----------------|
| Methodik der Korpus-Erstellung | LREC, ComputEL | Hauptautor oder Mitautor |
| Baseline-Evaluationsergebnisse | ACL, EMNLP | Mitautor |
| Validierung der LYSS-Metrik | WMT Metrics Shared Task | Mitautor |
| Design der diagnostischen Test-Suite | SIGMORPHON, NAACL | Hauptautor oder Mitautor |
| Sprachspezifische NLP-Ressourcen | Sprachspezifische Veranstaltungen | Hauptautor |

### 5.3 Positionierung für Förderanträge

Die Partnerschaft liefert konkrete Ergebnisse für Förderanträge:

- „Open-Source-Evaluationsinfrastruktur für [Sprache] MT" — nachweisbares Ergebnis
- „Kryptografische Datensouveränität für indigene linguistische Daten" — neuartig, publizierbar
- „Community-gesteuerter Benchmark mit Live-Bestenliste" — fortlaufende Wirkungskennzahl
- „Unabhängige Evaluation von OMT-1600 / Google Translate für [Sprache]" — aktuell, hohe Sichtbarkeit

### 5.4 Wirkung auf die Gemeinschaft

- Die Sprachgemeinschaft erhält eine **unabhängige Evaluationskapazität** — sie kann beurteilen, ob ein beliebiges MT-System (Google, Meta oder maßgeschneidert) für ihre Sprache tatsächlich funktioniert
- Die Gemeinschaft **kontrolliert die Testdaten** über die kryptografische Schlüsselverwahrung
- Jede über den Benchmark nachgewiesene Methode **überträgt die Eigentumsrechte** an die Gemeinschaft (siehe Benchmark Spec §8.3)
- Einnahmen aus eingesetzten Methoden fließen an die Gemeinschaft (Aufteilung 90/10)

### 5.5 Was es den Fachbereich kostet

| Komponente | Geschätzte Kosten | Wer zahlt |
|-----------|---------------|----------|
| Arbeitszeit PI/Postdoc (Design, Aufsicht) | ~40 Stunden | Fachbereich (oder durch Förderung finanziert) |
| Vergütung der Sprecherinnen und Sprecher (Übersetzung) | 2.500–6.000 $ | Durch Förderung oder durch Champollion finanziert |
| Vergütung der Sprecherinnen und Sprecher (Überprüfung) | 500–1.500 $ | Durch Förderung oder durch Champollion finanziert |
| Arbeitszeit der Forschungskoordination | ~20 Stunden | Fachbereich |
| **Entwicklung, Infrastruktur, Harness** | **0 $** | **Champollion-Projekt** |

Wir stellen die gesamte Entwicklung, die Harness-Konfiguration, die Einrichtung der LYSS-Metriken, die Integration der Bestenliste sowie die laufende Infrastruktur kostenlos für den Fachbereich bereit. Der Beitrag des Fachbereichs besteht in linguistischer Fachkenntnis und dem Zugang zu Sprecherinnen und Sprechern.

---

## 6. Zeitplan

| Phase | Dauer | Zentraler Meilenstein |
|-------|----------|--------------|
| 1: Korpus-Design | 2–4 Wochen | Design-Dokument genehmigt |
| 2: Ausgangssätze + Übersetzung | 4–8 Wochen | Rohkorpus fertiggestellt |
| 3: Qualitätssicherung | 2–4 Wochen | Gegengeprüft, schemavalidiert |
| 4: Versiegelung | 1 Woche | Goldstandard versiegelt, Hash-Manifest veröffentlicht |
| 5: Integration | 1–2 Wochen | Sprache live auf der Bestenliste mit Baselines |
| **Gesamt** | **10–19 Wochen** | **Live-Bestenliste mit versiegelter Evaluation** |

---

## 7. Wie Sie loslegen

1. **Kontaktieren Sie uns** — [Projekt-E-Mail/Kontakt]. Wir vereinbaren ein 30-minütiges Gespräch, um Ihre Sprache, verfügbare Ressourcen und die Logistik der Partnerschaft zu besprechen.

2. **Wir stellen bereit:**
   - Dieses Dokument
   - Das Korpus-Schema und die Validierungswerkzeuge
   - Beispiele aus unserem bestehenden Cree-Korpus (CRK)
   - Eine Vorlage für ein Korpus-Design-Konzept

3. **Sie stellen bereit:**
   - Eine PI oder einen Postdoc zur Leitung der linguistischen Arbeit
   - Zugang zu zweisprachigen Sprecherinnen und Sprechern (oder einen Plan zu deren Rekrutierung)
   - Informationen über verfügbare Ressourcen (FST, Wörterbuch, bestehende Korpora)
   - Institutionelle Genehmigung für die Datenverwaltung (OCAP®-Konformität oder gleichwertig)

4. **Wir gestalten das Korpus gemeinsam** — Domänenauswahl, Schwierigkeitsverteilung, diagnostische Tests, Zeitplan und Budget.

5. **Die Arbeit beginnt.** Wir tauschen uns wöchentlich aus. Der Fachbereich hat volle Autonomie über linguistische Entscheidungen; wir übernehmen die gesamte Entwicklung.

---

## 8. Häufig gestellte Fragen

### „Wir haben bereits ein paralleles Korpus. Können wir es verwenden?"

Ja — sofern das Korpus eine klare Provenienz aufweist, von Menschen verfasst ist und die Lizenz die Verwendung in der Evaluation gestattet. Wir helfen Ihnen, es an unser Schema anzupassen, fehlende Metadaten zu ergänzen und es zu integrieren. Bestehende Korpora können den Zeitplan erheblich beschleunigen (Phase 2 überspringen oder auf eine Lückenfüllung reduzieren).

### „Wir haben kein FST für unsere Sprache."

Das ist in Ordnung. LYSS-fst (morphologische Gültigkeit) erfordert ein FST, aber das Harness funktioniert auch ohne dieses unter Verwendung der Gewichte von Profil B (chrF++, BLEU, COMET, Verhaltensmetriken). Sofern ein GiellaLT-FST für eine verwandte Sprache existiert, können wir es möglicherweise anpassen. Andernfalls ermöglicht das Korpus dennoch eine wertvolle Evaluation — nur eben ohne die morphologische Gültigkeitsschranke.

### „Unsere Sprecherinnen und Sprecher verwenden eine nicht-lateinische Schrift."

Vollständig unterstützt. Das Korpus-Schema verarbeitet jede Unicode-Schrift. Wir haben es für SRO (Standard Roman Orthography) und Silbenschrift für Cree konzipiert, aber dieselbe Infrastruktur funktioniert für Devanagari, arabische Schrift, CJK, Äthiopisch oder jedes andere Schriftsystem.

### „Wie steht es um Dialektvariation?"

Taggen Sie sie. Das Schema für Korpus-Einträge enthält ein Feld `notes` für dialektale Informationen. Falls mehrere Dialekte vertreten sind, dokumentieren Sie diese. Die Äquivalenzklassen des Linters (LYSS-eq) können so konfiguriert werden, dass sie dialektale Varianten als gleichwertig akzeptieren. Die diagnostische Test-Suite kann dialektspezifische Kontraste enthalten.

### „Wem gehört das Korpus?"

Der Sprachgemeinschaft, über die Governance-Organisation. Der Fachbereich wird als Forschungspartner genannt. Champollion hält einen Treuhand-Schlüsselanteil für die betriebliche Kontinuität, kann jedoch nicht allein auf die versiegelten Daten zugreifen. Das Segment development wird unter einer von der Gemeinschaft festgelegten Creative-Commons-Lizenz veröffentlicht.

### „Was, wenn wir aufhören möchten?"

Die Gemeinschaft kann den Evaluationszugriff jederzeit widerrufen, indem sie sich weigert, den Verschlüsselungsschlüssel zu rekonstruieren. Die versiegelten Daten werden niemals offengelegt. Das bereits veröffentlichte Segment development bleibt unter seiner Lizenz öffentlich. Die Forschungsergebnisse des Fachbereichs (Publikationen, Präsentationen) verbleiben unabhängig davon bei diesem.

### „Was, wenn die Governance-Organisation noch nicht existiert?"

Wir können mit den Phasen 1–3 (Korpus-Design, Erstellung, QS) ohne eine Governance-Organisation beginnen. Die Versiegelung (Phase 4) erfordert die Benennung eines Schlüsselverwahrers. In der Zwischenzeit kann der Fachbereich neben dem Champollion-Projekt als Mitverwahrer fungieren, mit dem Verständnis, dass die Verwahrung an die Community-Governance-Organisation übergeht, sobald eine solche etabliert ist.

---

## Anhang: Tagging vs. Korpus-Erstellung

Dieses Dokument behandelt die **Korpus-Erstellung** — das Erstellen der parallelen Textpaare, welche die Referenzgrundlage (Ground Truth) der Evaluation bilden. Das Tagging (morphologische Annotation, Interlinearglossierung, FST-Tag-Zeichenketten) ist eine separate Tätigkeit, die das Korpus anreichert, aber für eine grundlegende Evaluation nicht erforderlich ist.

| Tätigkeit | Erforderlich? | Was sie ermöglicht |
|----------|-----------|-----------------|
| **Korpus-Erstellung** (dieses Dokument) | ✅ Erforderlich | Grundlegende Evaluation: chrF++, exakte Übereinstimmung, COMET, Verhaltensmetriken |
| **FST-Abdeckungsprüfung** | 🟡 Optional | LYSS-fst Metrik für morphologische Gültigkeit |
| **Morphologische Annotation** | 🟡 Optional | `morphological_accuracy` Metrik (Scoring Spec §2.2) |
| **Linter-Äquivalenzregeln** | 🟡 Optional | LYSS-eq Metrik für äquivalente Übereinstimmung |
| **Semantische Validator-Regeln** | 🟡 Optional | LYSS-sem Metrik für semantische Validierung |
| **Qualitätsbewertungen durch Sprecherinnen und Sprecher** | Separate Tätigkeit | Metrik-Validierung (siehe [Speaker Validation Protocol](/docs/specifications/speaker-validation)) |

Das Tagging und die Validierung durch Sprecherinnen und Sprecher werden in separaten Dokumenten behandelt und können parallel zur oder nach der Korpus-Erstellung erfolgen.