---
sidebar_position: 9
title: "Strategie für Korpus-Partnerschaften"
slug: '/specifications/corpus-partnership'
---
# Strategie für Korpus-Partnerschaften: Aufbau von Evaluationskorpora über akademische Linguistikinstitute

> **Zweck.** Dieses Dokument beschreibt den vollständigen Arbeitsablauf für den Aufbau eines Evaluationskorpus für die maschinelle Übersetzung im Rahmen einer Partnerschaft mit einem Linguistikinstitut. Es behandelt, was das Institut liefern soll, wie das Korpus beschaffen sein muss, wie es kryptografisch versiegelt wird, wie die Sandbox-Evaluation funktioniert und welchen Gegenwert das Institut erhält. Dies ist das Dokument, das Sie zu einem Treffen mit einem potenziellen akademischen Partner mitbringen.
>
> **Zielgruppe.** Institutsleitungen, leitende Forschende, Forschungskoordinatorinnen und -koordinatoren sowie Leiterinnen und Leiter von Programmen für indigene Sprachen an Universitäten mit aktiven Programmen zur Sprachdokumentation oder im Bereich NLP.
>
> **Begleitende Dokumente:**
> - [Protokoll zur Sprechervalidierung](/docs/specifications/speaker-validation) — die Anfrage an zweisprachige Sprechende, bestehende Übersetzungen zu *markieren* (Qualitätsbewertung, Linter-Validierung, FST-Überprüfung)
> - [Benchmark-Spezifikation](/docs/specifications/benchmark) — die vollständige technische Spezifikation für Korpora, Run Cards und Evaluationsprotokolle
> - [Datensouveränität](/docs/sovereignty/data-sovereignty) — OCAP®, CARE und warum die Eigentumsübertragung von Bedeutung ist
>
> Zuletzt aktualisiert: 2026-06-07

---

## 1. Was diese Partnerschaft hervorbringt

Ein **versiegeltes Evaluationskorpus**: eine kuratierte Sammlung paralleler Textpaare (Ausgangssprache → Zielsprache), die zur Referenzgrundlage (Ground Truth) für die Messung der Qualität maschineller Übersetzung wird. Methoden werden in einer Sandbox gegen dieses Korpus getestet — Entwicklerinnen und Entwickler bekommen die Testdaten niemals zu sehen.

Die Partnerschaft bringt drei Artefakte hervor:

| Artefakt | Was es ist | Wer es kontrolliert |
|----------|-----------|-----------------|
| **Entwicklungskorpus** | 100–200+ öffentliche parallele Textpaare für die Methodenentwicklung | Offen veröffentlicht (CC BY-NC-SA 4.0 oder gleichwertig) |
| **Goldstandard-Testset** | 50–150 geheime parallele Textpaare für die offizielle Evaluation | Community-Governance-Organisation (kryptografisch versiegelt) |
| **Diagnostische Testsuite** | 10–50 gezielte kontrastive Paare, die spezifische linguistische Phänomene prüfen | Offen veröffentlicht |

Das Entwicklungskorpus ermöglicht es jedem, Übersetzungsmethoden zu entwickeln. Das Goldstandard-Set stellt sicher, dass diese Methoden ehrlich getestet werden. Die diagnostische Suite erfasst spezifische Fehlerarten (z. B. „Kann dieses System Obviation verarbeiten?").

---

## 2. Was das Institut tun muss

### Phase 1: Korpusgestaltung (2–4 Wochen, Forschungszeit)

**Leitung:** Leitende(r) Forschende(r) oder Postdoc mit Fachkenntnis der Zielsprache.

1. **Auswahl der Domänen des Ausgangsmaterials.** Wählen Sie 4–6 reale Domänen, in denen die Übersetzung von der Sprachgemeinschaft tatsächlich benötigt wird. Unsere Taxonomie unterstützt 16 Domänen (siehe Benchmark-Spezifikation §2.7):

   | Priorität | Domäne | Begründung |
   |----------|--------|-----|
   | 🔴 Hoch | `edu` — Bildung | Lehrbücher, Lehrpläne — unmittelbarer Bedarf der Gemeinschaft |
   | 🔴 Hoch | `gov` — Verwaltung | Dokumente des Band Council, Richtlinien — praktischer täglicher Bedarf |
   | 🔴 Hoch | `medical` — Gesundheit | Aufnahmeformulare von Kliniken, Gesundheitsinformationen — sicherheitskritisch |
   | 🟡 Mittel | `conv` — Konversation | Alltagssprache — etabliert eine grundlegende Sprachgewandtheit |
   | 🟡 Mittel | `legal` — Recht | Rechtsdokumente, Verträge — Bedeutung für die Gemeinschaft |
   | 🟢 Niedriger | `literary` — Literatur/Kultur | Erzählungen, mündliche Überlieferungen — kulturelle Bewahrung |

2. **Erstellen Sie ein Dokument zur Korpusgestaltung**, das Folgendes spezifiziert:
   - Zielgröße pro Segment (development, gold_standard, diagnostic)
   - Verteilung der Schwierigkeitsstufen (siehe §3.3 unten)
   - Register- und Domänenabdeckung
   - Auswahlkriterien für Ausgangssätze (kein synthetischer Text, nicht ausschließlich Bibeltext)
   - Plan zur Anwerbung von Sprechenden

3. **Reichen Sie die Gestaltung bei uns zur Prüfung ein.** Wir validieren sie gegen das Korpusschema (Benchmark-Spezifikation §2) und geben innerhalb einer Woche Rückmeldung.

### Phase 2: Erstellung der Ausgangssätze (4–8 Wochen, Sprecherzeit)

**Leitung:** Forschungskoordination in Zusammenarbeit mit zweisprachigen Sprechenden.

1. **Generieren oder wählen Sie Ausgangssätze** über die geplanten Domänen und Schwierigkeitsstufen hinweg. Quellen können sein:
   - Bestehende veröffentlichte zweisprachige Materialien (Lehrbücher, Verwaltungsdokumente)
   - Neu elizitierte Sätze, die gezielt spezifische linguistische Phänomene abdecken
   - Adaptionen aus realen Dokumenten (Tagesordnungen des Band Council, Klinikformulare, Bildungsmaterialien)

2. **Jeder Ausgangssatz muss Folgendes aufweisen:**
   - Domänen-Tag (aus der Taxonomie mit 16 Codes)
   - Register-Tag (conversational, formal, technical, ceremonial, educational)
   - Kontext-Tag (greeting, declaration, question, instruction, narrative, label, error)
   - Geschätzte Schwierigkeitsstufe (1–5, siehe §3.3)
   - Provenienz-Tag (textbook, elicited, corpus, gold_standard)

3. **Übersetzen Sie jeden Ausgangssatz** in die Zielsprache, durchgeführt von zweisprachigen Sprechenden. Mehrere Referenzübersetzungen pro Eintrag sind wertvoll, aber nicht erforderlich.

4. **Optional können Sie eine morphologische Analyse hinzufügen** für jede Referenzübersetzung:
   - Interlineare Glossierung (morphemweise Aufschlüsselung)
   - FST-Tag-Zeichenkette (sofern ein FST für die Sprache existiert)
   - Anmerkungen der Übersetzenden zu dialektalen Varianten, Mehrdeutigkeit oder kulturellem Kontext

### Phase 3: Qualitätssicherung (2–4 Wochen)

**Leitung:** Linguist(in) mit Fachkenntnis der Zielsprache.

1. **Gegenprüfung.** Jede Übersetzung sollte von mindestens einer weiteren zweisprachigen Person überprüft werden, die nicht die ursprüngliche Übersetzung erstellt hat. Die prüfende Person prüft:
   - Ist die Übersetzung korrekt?
   - Klingt sie natürlich?
   - Ist die Schwierigkeitsbewertung korrekt?
   - Gibt es akzeptable Varianten, die angemerkt werden sollten?

2. **Durchlauf durch unseren Schema-Validator.** Wir stellen ein Skript bereit, das das Korpus gegen das Eintragsschema validiert (Benchmark-Spezifikation §2.2). Es prüft:
   - Vorhandensein erforderlicher Felder
   - Gültigkeit der Domänencodes
   - Schwierigkeitsstufen als Ganzzahlen 1–5
   - Keine doppelten IDs
   - Zeichenkodierung (UTF-8 NFC-Normalisierung)

3. **Sofern ein FST für die Sprache existiert,** lassen Sie die Referenzübersetzungen durch dieses laufen. Jedes Wort in der Referenz sollte FST-gültig sein. Wörter, die es nicht sind (Lehnwörter, Neologismen, Eigennamen), sollten in einer Positivliste dokumentiert werden.

### Phase 4: Segmentierung und Versiegelung (1 Woche, unsere Entwicklung)

**Leitung:** Champollion-Team, mit Prüfung durch das Institut.

1. **Stratifizierte Aufteilung.** Wir teilen das Korpus mittels deterministischer Zufallsstichprobe in Segmente auf (Seed dokumentiert, reproduzierbar):

   | Segment | Zielgröße | Zugriff |
   |---------|------------|--------|
   | `development` | 60 % der Einträge (mind. 100) | Öffentlich |
   | `gold_standard` | 30 % der Einträge (mind. 50) | Geheim, versiegelt |
   | `held_out` | 10 % der Einträge (mind. 10) | Geheim, versiegelt, bis zur Aktivierung niemals verwendet |

   Die Aufteilung erhält die Verteilung der Schwierigkeitsstufen (stratifizierte Stichprobe), sodass jedes Segment eine proportionale Repräsentation über die Stufen hinweg aufweist.

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

3. **Das Entwicklungssegment** wird in das öffentliche Repository übernommen und mit vollständiger Lizenzierung veröffentlicht.

4. **Das diagnostische Segment** ist ebenfalls öffentlich — es prüft spezifische linguistische Phänomene (siehe §3.4).

### Phase 5: Integration und Launch (1–2 Wochen, unsere Entwicklung)

1. **Konfiguration des Harness.** Wir fügen die Sprache dem Evaluations-Harness hinzu:
   - Sprachkarte erstellt oder verifiziert
   - Korpus im Datensatz-Register registriert
   - LYSS-Metriken konfiguriert (LYSS-fst, sofern FST verfügbar, LYSS-eq, sofern Linter-Regeln existieren)
   - Standard-Bewertungsprofil ausgewählt (Profil A, sofern FST verfügbar, andernfalls Profil B)

2. **Baseline-Benchmark.** Wir führen einen Durchlauf mit 12 Modellen gegen das Entwicklungssegment durch, um die Rangliste mit ersten Werten zu füllen.

3. **Öffentliche Ankündigung.** Die Sprache erscheint in der Arena-Rangliste mit einem aktuellen Benchmark des Entwicklungssegments. Das Institut wird als Korpus-Partner genannt.

---

## 3. Wie das Korpus beschaffen sein muss

### 3.1 Format

Jede Korpusdatei ist ein JSON-Dokument, das dem Schema in Benchmark-Spezifikation §2.1–§2.2 folgt:

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

### 3.2 Mindestanforderungen an die Größe

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
| 1 — Grundwortschatz | Einzelne Wörter, gebräuchliche Begrüßungen, Zahlen | 10–15 % |
| 2 — Einfache Sätze | SVO, Präsens | 25–30 % |
| 3 — Mittlere Komplexität | Vergangenheits-/Zukunftsform, Possessive, Belebtheit | 30–35 % |
| 4 — Komplexe Morphologie | Obviation, Passiv, Konjunktordnung, Relativsätze | 15–20 % |
| 5 — Fortgeschritten | Mehrsätzig, formales Register, zeremoniell, idiomatisch | 5–10 % |

### 3.4 Diagnostische Testsuite

Das diagnostische Segment prüft spezifische linguistische Phänomene mithilfe **kontrastiver Paare**: eine korrekte Übersetzung und eine minimal abweichende inkorrekte Übersetzung. Wenn die Metrik eines Systems die korrekte höher bewertet, ist der Test bestanden.

Für polysynthetische Sprachen sollte die diagnostische Suite Folgendes anvisieren:

| Phänomen | Beispiel (Cree) | Was es prüft |
|-----------|----------------|--------------|
| **Belebtheitskongruenz** | atim (AN) vs. maskisin (IN) — unterschiedliche Verbformen | Weiß das System, welche Nomina belebt sind? |
| **Obviation** | Proximate vs. obviative dritte Person | Verfolgt es die Hierarchie der dritten Person? |
| **Inversmarkierung** | Direkte vs. inverse Verbformen | Verarbeitet es den Fall „Patiens übertrifft Agens"? |
| **Konjunkt/Independent** | Verbordnung von Hauptsatz vs. Nebensatz | Verwendet es das richtige Verbparadigma? |
| **Inklusiv/Exklusiv** | „Wir (einschließlich dir)" vs. „Wir (ausschließlich dir)" | Unterscheidet es die Formen der ersten Person Plural? |

Identifizieren Sie für andere Sprachfamilien die 3–5 diagnostisch aussagekräftigsten Phänomene, die kompetente von inkompetenter Übersetzung unterscheiden. Die linguistische Fachkenntnis des Instituts ist hier von wesentlicher Bedeutung — es sind genau jene Tests, die nur ein Fachmensch zu schreiben weiß.

### 3.5 Was wir NICHT wünschen

| Anti-Muster | Begründung |
|-------------|-----|
| **Ausschließlich Bibeltext** | Archaisches Register, liturgisches Vokabular, formelhafte Struktur. OMT-1600 hat 1.560 Sprachen auf diese Weise evaluiert — wir vermeiden dies bewusst. |
| **Synthetische Evaluationspaare** | Von LLMs generierte Referenzen vereiteln den Zweck der Evaluation. Die Referenz muss von Menschen verfasst sein. |
| **Einregister-Korpora** | Durchgehend formal oder durchgehend konversationell. Reale Übersetzung umfasst mehrere Register. |
| **Ausschließlich Schwierigkeitsstufe 1** | Einzelne Wörter und Begrüßungen prüfen nicht die Übersetzung — sie prüfen das Nachschlagen von Vokabular. |
| **Maschinell übersetzte Referenzen** | Die Verwendung der Ausgabe von Google Translate als „Referenz" ist zirkulär. |
| **Sätze ohne Kontext-Tag** | Wir müssen die kommunikative Funktion für die diagnostische Analyse kennen. |

---

## 4. Kryptografische Versiegelung und Sandbox-Tests {#4-cryptographic-sealing-and-sandbox-testing}

### 4.1 Warum das Testset versiegeln?

Konventionelle ML-Benchmarks veröffentlichen Testsets offen. Nach der Veröffentlichung werden Frontier-LLMs früher oder später darauf trainiert (absichtlich oder durch Web-Scraping), was die Werte unzuverlässig macht. Bei Daten indigener Sprachen besteht eine zusätzliche Sorge: Veröffentlichte linguistische Daten können ohne Zustimmung der Gemeinschaft verwendet werden.

Die Versiegelung gewährleistet:
- **Integrität des Testsets:** Methoden können sich nicht an Daten überanpassen, die sie nie gesehen haben
- **Datensouveränität:** Die Gemeinschaft kontrolliert, wer gegen ihre Daten evaluiert
- **Dauerhafte Aktualität:** Das Testset wird niemals kontaminiert

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

Der Verschlüsselungsschlüssel für das versiegelte Testset wird mittels Shamir Secret Sharing mit einem Schwellenwert von 2-aus-3 aufgeteilt:

| Schlüsselinhaber | Rolle | Widerrufsbefugnis |
|-------------|------|-----------------|
| **Community-Governance-Organisation** | Primärer Verwahrer | Kann den Evaluationszugriff einseitig widerrufen |
| **Akademisches Institut als Partner** | Mitverwahrer | Kann an der Schlüsselrekonstruktion mitwirken |
| **Champollion-Projekt** | Treuhand | Kann nicht allein auf Daten zugreifen; gewährleistet Kontinuität, falls andere Parteien nicht verfügbar werden |

Jeweils 2 von 3 Anteilen rekonstruieren den Schlüssel. Das bedeutet:
- Die Gemeinschaft + das Institut können ohne Champollion auf die Daten zugreifen
- Die Gemeinschaft + Champollion können ohne das Institut auf die Daten zugreifen
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
- Das Korpus existierte zu einem bestimmten Datum
- Es hat eine bekannte Größe und Struktur
- Jede Änderung an den versiegelten Segmenten würde die Hash-Kette brechen
- Die Gemeinschaft kann verifizieren, dass ihre Daten nicht manipuliert wurden

---

## 5. Was das Institut erhält

### 5.1 Forschungsinfrastruktur

| Asset | Beschreibung |
|-------|------------|
| **Evaluations-Harness** | Ein funktionierendes, getestetes Evaluations-Framework für ihre Sprache — erspart Monate des Werkzeugbaus |
| **LYSS-Metriken** | Sprachspezifische Evaluationsmetriken (LYSS-fst, LYSS-eq, LYSS-sem), konfiguriert für ihre Sprache — sofern FST- und Wörterbuchressourcen vorhanden sind |
| **Rangliste** | Eine öffentliche, aktuelle Rangliste, die den Stand der Technik für ihr Sprachpaar zeigt |
| **Baseline-Benchmark** | Durchlauf mit 12 Modellen, der unmittelbare, veröffentlichbare Baselines liefert |
| **Diagnostische Testsuite** | Gezielte Tests für spezifische linguistische Phänomene — wiederverwendbar für andere Evaluationen |

### 5.2 Publikationen

Die Korpuskonstruktion und die Evaluationsergebnisse unterstützen mehrere Publikationen:

| Beitrag | Veranstaltung | Rolle des Instituts |
|-------|-------|-----------------|
| Methodik der Korpuskonstruktion | LREC, ComputEL | Erst- oder Mitautorschaft |
| Ergebnisse der Baseline-Evaluation | ACL, EMNLP | Mitautorschaft |
| Validierung der LYSS-Metrik | WMT Metrics Shared Task | Mitautorschaft |
| Gestaltung der diagnostischen Testsuite | SIGMORPHON, NAACL | Erst- oder Mitautorschaft |
| Sprachspezifische NLP-Ressourcen | Sprachspezifische Veranstaltungen | Erstautorschaft |

### 5.3 Positionierung für Förderanträge

Die Partnerschaft liefert konkrete Ergebnisse für Förderanträge:

- „Open-Source-Evaluationsinfrastruktur für die MT von [Sprache]" — nachweisbares Liefergebnis
- „Kryptografische Datensouveränität für indigene linguistische Daten" — neuartig, veröffentlichbar
- „Community-verwalteter Benchmark mit aktueller Rangliste" — fortlaufende Wirkungskennzahl
- „Unabhängige Evaluation von OMT-1600 / Google Translate für [Sprache]" — zeitgemäß, von hoher Sichtbarkeit

### 5.4 Wirkung für die Gemeinschaft

- Die Sprachgemeinschaft erhält eine **unabhängige Evaluationsfähigkeit** — sie kann beurteilen, ob ein beliebiges MT-System (Google, Meta oder ein individuelles) für ihre Sprache tatsächlich funktioniert
- Die Gemeinschaft **kontrolliert die Testdaten** über die kryptografische Schlüsselverwahrung
- Methoden, die durch den Benchmark belegt werden, **übertragen das Eigentum** an die Gemeinschaft (siehe Benchmark-Spezifikation §8.3)
- Einnahmen aus eingesetzten Methoden fließen an die Gemeinschaft (Aufteilung 90/10)

### 5.5 Was es das Institut kostet

| Komponente | Geschätzte Kosten | Wer zahlt |
|-----------|---------------|----------|
| Zeit der/des leitenden Forschenden/Postdocs (Gestaltung, Aufsicht) | ca. 40 Stunden | Institut (oder fördermittelfinanziert) |
| Vergütung der Sprechenden (Übersetzung) | 2.500–6.000 $ | Fördermittel- oder Champollion-finanziert |
| Vergütung der Sprechenden (Überprüfung) | 500–1.500 $ | Fördermittel- oder Champollion-finanziert |
| Zeit der Forschungskoordination | ca. 20 Stunden | Institut |
| **Entwicklung, Infrastruktur, Harness** | **0 $** | **Champollion-Projekt** |

Wir stellen die gesamte Entwicklung, Harness-Konfiguration, Einrichtung der LYSS-Metriken, Integration in die Rangliste und die laufende Infrastruktur ohne Kosten für das Institut bereit. Der Beitrag des Instituts besteht in linguistischer Fachkenntnis und dem Zugang zu Sprechenden.

---

## 6. Zeitplan

| Phase | Dauer | Wichtiger Meilenstein |
|-------|----------|--------------|
| 1: Korpusgestaltung | 2–4 Wochen | Gestaltungsdokument genehmigt |
| 2: Ausgangssätze + Übersetzung | 4–8 Wochen | Rohkorpus fertiggestellt |
| 3: Qualitätssicherung | 2–4 Wochen | Gegengeprüft, schema-validiert |
| 4: Versiegelung | 1 Woche | Goldstandard versiegelt, Hash-Manifest veröffentlicht |
| 5: Integration | 1–2 Wochen | Sprache live auf der Rangliste mit Baselines |
| **Gesamt** | **10–19 Wochen** | **Aktuelle Rangliste mit versiegelter Evaluation** |

---

## 7. Wie Sie beginnen {#7-how-to-get-started}

1. **Kontaktieren Sie uns** — [Projekt-E-Mail/Kontakt]. Wir vereinbaren ein 30-minütiges Gespräch, um Ihre Sprache, verfügbare Ressourcen und die Logistik der Partnerschaft zu erörtern.

2. **Wir stellen bereit:**
   - Dieses Dokument
   - Das Korpusschema und die Validierungswerkzeuge
   - Beispiele aus unserem bestehenden Cree-Korpus (CRK)
   - Eine Entwurfsvorlage für die Korpusgestaltung

3. **Sie stellen bereit:**
   - Eine(n) leitende(n) Forschende(n) oder Postdoc zur Leitung der linguistischen Arbeit
   - Zugang zu zweisprachigen Sprechenden (oder einen Plan, sie anzuwerben)
   - Informationen über verfügbare Ressourcen (FST, Wörterbuch, bestehende Korpora)
   - Institutionelle Genehmigung für die Datenverwaltung (OCAP®-Konformität oder gleichwertig)

4. **Wir gestalten das Korpus gemeinsam** — Domänenauswahl, Schwierigkeitsverteilung, diagnostische Tests, Zeitplan und Budget.

5. **Die Arbeit beginnt.** Wir stimmen uns wöchentlich ab. Das Institut hat volle Autonomie über linguistische Entscheidungen; wir übernehmen die gesamte Entwicklung.

---

## 8. Häufig gestellte Fragen

### „Wir haben bereits ein paralleles Korpus. Können wir es verwenden?"

Ja — sofern das Korpus eine klare Provenienz aufweist, von Menschen verfasst ist und die Lizenz die Nutzung zur Evaluation gestattet. Wir helfen Ihnen, es an unser Schema anzupassen, fehlende Metadaten zu ergänzen und es zu integrieren. Bestehende Korpora können den Zeitplan erheblich beschleunigen (Phase 2 entfällt oder wird auf eine Lückenfüllung reduziert).

### „Wir haben kein FST für unsere Sprache."

Das ist kein Problem. LYSS-fst (morphologische Gültigkeit) erfordert ein FST, aber das Harness funktioniert auch ohne unter Verwendung der Gewichtungen von Profil B (chrF++, BLEU, COMET, Verhaltensmetriken). Sofern ein GiellaLT-FST für eine verwandte Sprache existiert, können wir es möglicherweise anpassen. Andernfalls ermöglicht das Korpus dennoch eine wertvolle Evaluation — lediglich ohne das Gate der morphologischen Gültigkeit.

### „Unsere Sprechenden verwenden eine nicht-lateinische Schrift."

Vollständig unterstützt. Das Korpusschema verarbeitet jede Unicode-Schrift. Wir haben für SRO (Standard Roman Orthography) und Silbenschrift für Cree konzipiert, aber dieselbe Infrastruktur funktioniert für Devanagari, arabische Schrift, CJK, Äthiopisch oder jedes andere Schriftsystem.

### „Was ist mit Dialektvariation?"

Taggen Sie sie. Das Schema des Korpuseintrags enthält ein Feld `notes` für dialektale Informationen. Sind mehrere Dialekte vertreten, dokumentieren Sie sie. Die Äquivalenzklassen des Linters (LYSS-eq) können so konfiguriert werden, dass sie dialektale Varianten als gleichwertig akzeptieren. Die diagnostische Testsuite kann dialektspezifische Kontraste enthalten.

### „Wem gehört das Korpus?"

Der Sprachgemeinschaft, über die Governance-Organisation. Das Institut wird als Forschungspartner genannt. Champollion hält einen Treuhand-Schlüsselanteil zur betrieblichen Kontinuität, kann aber nicht allein auf die versiegelten Daten zugreifen. Das Entwicklungssegment wird unter einer von der Gemeinschaft festgelegten Creative-Commons-Lizenz veröffentlicht.

### „Was, wenn wir aufhören möchten?"

Die Gemeinschaft kann den Evaluationszugriff jederzeit widerrufen, indem sie sich weigert, den Verschlüsselungsschlüssel zu rekonstruieren. Die versiegelten Daten werden niemals offengelegt. Das bereits veröffentlichte Entwicklungssegment bleibt unter seiner Lizenz öffentlich. Die Forschungsergebnisse des Instituts (Publikationen, Präsentationen) bleiben unabhängig davon in seinem Besitz.

### „Was, wenn die Governance-Organisation noch nicht existiert?"

Wir können mit den Phasen 1–3 (Korpusgestaltung, -erstellung, QS) ohne eine Governance-Organisation beginnen. Die Versiegelung (Phase 4) erfordert die Benennung eines Schlüsselverwahrers. In der Zwischenzeit kann das Institut als Mitverwahrer neben dem Champollion-Projekt fungieren, mit dem Verständnis, dass die Verwahrung an die Community-Governance-Organisation übergeht, sobald eine solche eingerichtet ist.

---

## Anhang: Tagging vs. Korpuskonstruktion

Dieses Dokument behandelt die **Korpuskonstruktion** — die Erstellung der parallelen Textpaare, die die Referenzgrundlage der Evaluation bilden. Tagging (morphologische Annotation, interlineare Glossierung, FST-Tag-Zeichenketten) ist eine separate Tätigkeit, die das Korpus anreichert, aber für die grundlegende Evaluation nicht erforderlich ist.

| Tätigkeit | Erforderlich? | Was sie ermöglicht |
|----------|-----------|-----------------|
| **Korpuskonstruktion** (dieses Dokument) | ✅ Erforderlich | Grundlegende Evaluation: chrF++, exakte Übereinstimmung, COMET, Verhaltensmetriken |
| **FST-Abdeckungsprüfung** | 🟡 Optional | Metrik der morphologischen Gültigkeit LYSS-fst |
| **Morphologische Annotation** | 🟡 Optional | Metrik `morphological_accuracy` (Scoring-Spezifikation §2.2) |
| **Linter-Äquivalenzregeln** | 🟡 Optional | Metrik der äquivalenten Übereinstimmung LYSS-eq |
| **Regeln des semantischen Validators** | 🟡 Optional | Metrik der semantischen Validierung LYSS-sem |
| **Qualitätsbewertungen durch Sprechende** | Separate Tätigkeit | Metrikvalidierung (siehe [Protokoll zur Sprechervalidierung](/docs/specifications/speaker-validation)) |

Tagging und Sprechervalidierung werden in separaten Dokumenten behandelt und können parallel zur oder nach der Korpuskonstruktion erfolgen.