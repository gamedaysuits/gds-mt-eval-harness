---
sidebar_position: 7
title: "Corpus Design Framework"
---
# Framework für das Design von Evaluationskorpora

> **Version:** 1.0  
> **Status:** Entwurf  
> **Zweck:** Eine systematische Methodik zur Erstellung von Evaluationskorpora, die valide, zuverlässige und linguistisch aussagekräftige Bewertungen der Übersetzungsqualität liefern. Dies ist die maßgebliche Referenz dafür, wie Champollion-Evaluationsdatensätze konzipiert, erstellt und gepflegt werden.

---

## 1. Designprinzipien

### 1.1 — Warum keine öffentlichen Benchmarks?

Öffentliche Parallelkorpora (FLORES+, Tatoeba, WMT-Testsets, OPUS) stehen für Entwicklung und Debugging zur Verfügung, sind jedoch **von der offiziellen Leaderboard-Evaluation ausgeschlossen**. Der Grund ist einfach:

**Kontamination.** Frontier-LLMs werden auf enormen Web-Scrapes trainiert. Jeder Paralleltext, der öffentlich existiert hat — insbesondere in kuratierten, vielzitierten Benchmark-Datensätzen — befindet sich wahrscheinlich in deren Trainingsdaten. Wenn Sie GPT-4o auf FLORES+ evaluieren und es 85 chrF++ erzielt, können Sie nicht zwischen „das Modell ist gut im Übersetzen" und „das Modell hat sich diese spezifischen Satzpaare eingeprägt" unterscheiden. Dies ist keine theoretische Sorge — [die Forschung hat](https://arxiv.org/abs/2311.04850) messbare Kontaminationseffekte auf MT-Benchmarks nachgewiesen.

Für Champollion ist dies besonders relevant, weil:
- Unser Leaderboard primär LLM-basierte Methoden vergleicht
- Unser Nutzenversprechen eine *ehrliche, rigorose Evaluation* ist
- Unsere Zielnutzer (Sprachgemeinschaften) anhand dieser Werte Einsatzentscheidungen treffen

### 1.2 — Kernanforderungen

Jedes Champollion-Evaluationskorpus muss Folgendes erfüllen:

| Anforderung | Begründung |
|-------------|-----------|
| **Von Menschen verfasst** | Keine synthetischen Daten. Sämtlicher Quelltext und alle Referenzübersetzungen müssen von Menschen verfasst werden. LLMs dürfen bei der Ausrichtung und Formatierung unterstützen, jedoch niemals Inhalte generieren. |
| **Nicht öffentlich in paralleler Form verfügbar** | Der Quelltext kann öffentlich sein; die Referenzübersetzungen können öffentlich sein; aber die spezifische *Paarung* darf nicht als herunterladbares Parallelkorpus existieren. |
| **Mit Herkunftsnachweis** | Jeder Eintrag muss eine dokumentierte Herkunft besitzen: Quelldokument, Übersetzer, Lizenz, Datum. |
| **Linguistisch fundiert** | Die Abdeckung muss von typologischen Merkmalen geleitet werden, nicht von zufälliger Stichprobenentnahme. |
| **Domänenstratifiziert** | Die Einträge müssen definierte Textdomänen mit kontrollierter Repräsentation abdecken. |
| **Schwierigkeitsgestuft** | Die Einträge müssen anhand der strukturellen Komplexität Schwierigkeitsstufen (1–5) zugeordnet werden. |
| **Versionskontrolliert** | Korpusversionen werden inhaltsgehasht. Werte sind nur innerhalb derselben Version vergleichbar. |
| **Von der Gemeinschaft überprüfbar** | Referenzübersetzungen müssen von Mitgliedern der Sprachgemeinschaft überprüfbar sein. |

---

## 2. Auswahl des Quelltexts

### 2.1 — Domänentaxonomie

Champollion evaluiert Übersetzungen für **praktische Einsatzkontexte**, nicht für akademische Übungen. Die Domänentaxonomie spiegelt reale Texttypen wider, denen Übersetzungsnutzer begegnen:

| Domäne | Code | Beschreibung | Beispielquellen |
|--------|------|-------------|-----------------|
| **Software-UI** | `ui` | Schaltflächenbeschriftungen, Menüpunkte, Fehlermeldungen, Tooltips, Onboarding-Abläufe | Open-Source-App-Strings, Dokumentationsportale |
| **Amtlich/Administrativ** | `admin` | Behördendokumente, rechtliche Hinweise, Formulare, Grundsatzerklärungen | Öffentliche Behördenpublikationen, kommunale Dokumente |
| **Bildung** | `edu` | Lehrbuchinhalte, Unterrichtsmaterialien, instruktive Texte | Veröffentlichte Bildungsmaterialien, Lehrleitfäden |
| **Erzählend/Literarisch** | `lit` | Geschichten, kulturelle Texte, Transkriptionen mündlicher Überlieferungen | Veröffentlichte Bücher, Kulturarchive (mit Genehmigung) |
| **Konversationell** | `conv` | Dialoge, chatähnliche Austausche, informelle schriftliche Kommunikation | Veröffentlichte Dialogkorpora, Drehbücher, Interviewtranskripte |
| **Technisch** | `tech` | API-Dokumentation, README-Dateien, technische Spezifikationen | Open-Source-Projektdokumentation |
| **Gesundheit/Medizin** | `health` | Patientenorientierte medizinische Informationen, Public-Health-Kommunikation | Behördliche Gesundheitspublikationen |
| **Nachrichten/Journalistisch** | `news` | Nachrichtenartikel, Pressemitteilungen, Tagesgeschehen | Gemeinschaftszeitungen, indigene Medienorgane |

### 2.2 — Domänenverteilung

Ein Standard-Evaluationskorpus sollte folgende Verteilung anstreben. Die genauen Prozentsätze können je nach Sprachpaar variieren, abhängig davon, welche Texttypen für die Zielgemeinschaft am relevantesten sind:

| Domäne | Zielwert % | Begründung |
|--------|----------|-----------|
| Software-UI | 25% | Primärer Einsatzkontext für Nutzer der champollion-CLI |
| Amtlich/Administrativ | 15% | Übersetzungen mit hohem Risiko und rechtlichen Implikationen |
| Bildung | 15% | Kernanwendungsfall für die Sprachrevitalisierung |
| Erzählend/Literarisch | 10% | Prüft kulturelle Nuancen und literarisches Register |
| Konversationell | 10% | Prüft informelles Register und natürliche Sprachmuster |
| Technisch | 10% | Prüft Präzision und Terminologiekonsistenz |
| Gesundheit/Medizin | 10% | Hohes Risiko, prüft domänenspezifisches Vokabular |
| Nachrichten/Journalistisch | 5% | Prüft zeitgenössisches Vokabular und neutrales Register |

### 2.3 — Auswahlkriterien für Quelltexte

Bei der Auswahl von Quelltexten für ein neues Korpus:

1. **Lizenzkompatibilität.** Der Quelltext muss unter einer Lizenz stehen, die die Verwendung in einem Evaluationskorpus erlaubt. Bevorzugen Sie CC BY, CC BY-SA oder Public Domain. Dokumentieren Sie die Lizenz.

2. **Aktualität.** Bevorzugen Sie Texte, die innerhalb der letzten 10 Jahre veröffentlicht wurden. Sprache entwickelt sich — insbesondere das Vokabular rund um Technologie, Verwaltung und Medizin.

3. **Registervielfalt.** Suchen Sie innerhalb jeder Domäne Texte unterschiedlicher Formalitätsgrade. Eine behördliche Pressemitteilung (formal) und ein behördlicher Social-Media-Beitrag (informell) gehören beide zur Domäne `admin`, weisen jedoch unterschiedliche Register auf.

4. **Kulturelle Relevanz.** Priorisieren Sie für indigene und Minderheitensprachen Texte, die für die Gemeinschaft von Bedeutung sind — Dokumente zur Landbewirtschaftung, Bildungsmaterialien in der Sprache, Texte zur Kulturbewahrung — gegenüber Texten, die zufällig in paralleler Form existieren.

5. **Keine maschinell übersetzten Quellen.** Wenn ein „paralleles" Dokument erstellt wurde, indem das Original durch Google Translate geleitet und anschließend nachbearbeitet wurde, ist es als Referenzübersetzung NICHT akzeptabel. Die Referenz muss eine unabhängige menschliche Übersetzung sein.

---

## 3. System der Schwierigkeitsstufen

### 3.1 — Definitionen der Stufen

Jeder Eintrag wird einer Schwierigkeitsstufe (1–5) zugeordnet, basierend auf der strukturellen Komplexität des *Quelltexts*, nicht auf der Übersetzungsschwierigkeit (die je nach Methode variiert).

| Stufe | Bezeichnung | Strukturelle Merkmale |
|------|-------|---------------------------|
| 1 | **Elementar** | Einfache Sätze. Einzelner Satzteil. Präsens. Gebräuchliches Vokabular. Keine Idiome. Keine eingebetteten Strukturen. |
| 2 | **Mittel** | Zusammengesetzte Sätze. Zwei durch Konjunktion verbundene Satzteile. Vergangenheits-/Zukunftsform. Etwas Domänenvokabular. |
| 3 | **Fortgeschritten** | Komplexe Sätze. Nebensätze, Relativsätze. Gemischte Zeitformen. Domänenspezifische Terminologie. Passiv. |
| 4 | **Experte** | Mehrere eingebettete Satzteile. Rechtliches/technisches Register. Konditionalstrukturen. Abstrakte Konzepte. Kulturelle Bezüge. |
| 5 | **Extrem** | Dichte Prosa mit mehreren gleichzeitigen Herausforderungen: verschachtelte Unterordnung, mehrdeutige Pronominalbezüge, kulturelle Idiome, gemischtes Register, seltenes Vokabular. |

### 3.2 — Linguistisch fundierte Schwierigkeitsfaktoren

Über die strukturelle Komplexität hinaus wird die Schwierigkeit durch die **typologische Distanz** zwischen Quell- und Zielsprache moduliert. Diese Faktoren werden aus den typologischen Merkmalen von WALS und den Klassifikationsdaten der Sprachkarte abgeleitet:

| Faktor | Geringe Schwierigkeit | Hohe Schwierigkeit |
|--------|---------------|-----------------|
| **Wortstellung** | Gleiche Grundordnung (z. B. SVO→SVO) | Unterschiedliche Grundordnung (z. B. SVO→SOV) |
| **Morphologischer Typ** | Ähnlicher Typ (z. B. analytisch→analytisch) | Unterschiedlicher Typ (z. B. analytisch→polysynthetisch) |
| **Grammatisches Genus** | Gleiches System oder kein Genus | Quelle hat kein Genus, Ziel hat komplexes Genus |
| **Honorativ/Register** | Keine Registermarkierung | Ziel hat komplexes Registersystem (z. B. Japanisch, Koreanisch) |
| **Schrift** | Gleiche Schrift | Unterschiedliche Schrift (Transliteration erforderlich) |
| **Belebtheit** | Keine Belebtheitsunterscheidung | Ziel hat belebtheitsbasierte Kongruenz (z. B. Cree) |
| **Evidentialität** | Keine Evidentialität | Ziel markiert die Informationsquelle grammatikalisch |

### 3.3 — Verteilung der Stufen

Ein Standardkorpus sollte ungefähr Folgendes aufweisen:

| Stufe | Zielwert % | Begründung |
|------|----------|-----------|
| 1 | 15% | Etabliert eine Grundlinie — selbst schlechte Methoden sollten diese bewältigen |
| 2 | 25% | Alltägliche praktische Übersetzung |
| 3 | 30% | Hier werden Qualitätsunterschiede zwischen Methoden sichtbar |
| 4 | 20% | Trennt gute Methoden von hervorragenden |
| 5 | 10% | Obergrenzentest — nur sehr wenige Methoden werden diese gut bewältigen |

---

## 4. Qualität der Referenzübersetzungen

### 4.1 — Anforderungen an Übersetzer

Referenzübersetzungen müssen von Menschen erstellt werden, die:

1. **Fließende Sprecher** der Zielsprache (L1 oder gleichwertig) sind
2. **Literat** in sowohl Quell- als auch Zielsprache sind
3. **Domänenkundig** für die Domäne des Textes sind (ein medizinischer Übersetzer für Gesundheitstexte usw.)
4. **Unabhängig** sind — der Übersetzer darf während der Übersetzung keinen Zugriff auf irgendeine MT-Ausgabe für denselben Text haben

### 4.2 — Übersetzungsbriefing

Jeder Übersetzer erhält ein Briefing, das Folgendes umfasst:

- Das zu verwendende **Register** (formal, konversationell usw.)
- Die **Zielgruppe** (Allgemeinheit, Fachleute, Kinder usw.)
- Etwaige **Terminologiekonventionen**, die spezifisch für die Sprachgemeinschaft sind
- Eine ausdrückliche Anweisung: „Übersetzen Sie die Bedeutung, nicht die Worte. Eine natürlich klingende Übersetzung ist wertvoller als eine wörtliche."

### 4.3 — Qualitätssicherung

1. **Doppelte Übersetzung.** Idealerweise besitzt jeder Eintrag zwei unabhängige Referenzübersetzungen von verschiedenen Übersetzern. Wo dies nicht durchführbar ist, priorisieren Sie die doppelte Übersetzung für die Stufen 4–5.

2. **Überprüfung durch die Gemeinschaft.** Referenzübersetzungen sollten von mindestens einem zusätzlichen Sprecher überprüft werden, der die Übersetzung nicht erstellt hat.

3. **Akzeptable Varianten.** Dokumentieren Sie für jede Referenz bekannte akzeptable Varianten (Wortstellung, orthografische Konventionen, dialektale Formen). Diese fließen in die Metrik `equivalent_match_rate` ein.

### 4.4 — Was eine schlechte Referenz ausmacht

| Problem | Warum es die Evaluation ungültig macht |
|---------|------------------------------|
| Maschinell übersetzt und anschließend nachbearbeitet | Die Nachbearbeitung bewahrt die MT-Struktur; benachteiligt Methoden, die natürlichere Übersetzungen erzeugen |
| Von einem Lernenden statt einem fließenden Sprecher übersetzt | Die Referenz kann Fehler enthalten, die eine korrekte MT-Ausgabe benachteiligen |
| Übermäßig wörtlich | Natürliche Übersetzungen schneiden gegenüber wörtlichen Referenzen schlecht ab |
| Einzige gültige Interpretation für mehrdeutige Quelle | Benachteiligt gültige alternative Interpretationen |

---

## 5. Kontaminationsvermeidung

### 5.1 — Das Bedrohungsmodell der Kontamination

| Bedrohung | Beschreibung | Gegenmaßnahme |
|--------|-------------|------------|
| **Überschneidung mit Trainingsdaten** | LLMs, die auf dem Parallelkorpus trainiert wurden | Das Parallelkorpus nicht öffentlich veröffentlichen |
| **Few-Shot-Leckage** | Der Methodenautor verwendet Evaluationseinträge als Few-Shot-Beispiele | Fingerprint-Prüfung: Einträge im Prompt werden erkannt und markiert |
| **Indirekte Kontamination** | Quelltext existiert in LLM-Trainingsdaten (einsprachig) | Akzeptabel — einsprachiger Quelltext ist zu erwarten. Die *Paarung* muss neuartig sein. |
| **Crowd-Kontamination** | Gemeinschaftsprüfer teilen Einträge öffentlich | Lizenzbedingungen untersagen die Weiterverbreitung des Parallelkorpus |

### 5.2 — Geheimhaltungsstufen des Korpus

| Stufe | Sichtbarkeit | Verwendung |
|------|-----------|-----|
| **Öffentliches Entwicklungsset** | Vollständig öffentlich | Methodenentwicklung, Debugging, Regressionstests. Werte werden NICHT auf dem Leaderboard veröffentlicht. |
| **Zurückgehaltenes Evaluationsset** | Quelltext sichtbar, Referenzen geheim | Offizielle Leaderboard-Evaluation. Methoden erhalten Quelltext und geben Übersetzungen zurück; die Bewertung erfolgt serverseitig. Referenzen werden der Methode niemals offengelegt. |
| **Goldstandard-Set** | Vollständig geheim, von der Gemeinschaft kontrolliert | Von der Gemeinschaft validierte Evaluation. Verwaltet von der Governance-Organisation. Verwendet für die Verifizierungsstufe „Community Validated". |

### 5.3 — Rotationsrichtlinie

Evaluationskorpora sollten regelmäßig **rotiert** werden:

1. Nachdem ein Korpus 12 Monate in Verwendung war, beginnen Sie mit der Erstellung eines Ersatzes
2. Versetzen Sie das alte Korpus in den Status „Entwicklungsset" (öffentlich)
3. Befördern Sie das neue Korpus zum „zurückgehaltenen Evaluationsset"
4. Dies verhindert eine schleichende Kontamination durch iterative Optimierung gegen ein festes Ziel

---

## 6. Workflow zur Korpuserstellung

### 6.1 — Schritt-für-Schritt-Prozess

```
Step 1: Language Pair Selection
    └─ Identify target language, read language card
    └─ Review typological features (WALS), contact influences, scripts
    └─ Identify which difficulty factors apply

Step 2: Source Text Curation
    └─ Identify candidate source documents per domain
    └─ Verify licenses
    └─ Extract candidate sentences/segments
    └─ Classify by domain and preliminary difficulty tier

Step 3: Segment Selection
    └─ Sample segments to match domain distribution (§2.2)
    └─ Sample segments to match difficulty distribution (§3.3)
    └─ Ensure linguistic phenomenon coverage (§6.2)
    └─ Target minimum corpus size (§6.3)

Step 4: Reference Translation
    └─ Assign segments to qualified translators
    └─ Provide translation brief
    └─ Collect translations
    └─ Dual-translate Tier 4–5 entries

Step 5: Quality Assurance
    └─ Community review of references
    └─ Document acceptable variants
    └─ Flag and resolve disagreements

Step 6: Metadata & Packaging
    └─ Assign final difficulty tiers
    └─ Add provenance metadata per entry
    └─ Content-hash the corpus for versioning
    └─ Package as corpus JSON per harness spec

Step 7: Registration
    └─ Register in Supabase datasets table
    └─ Add to ATTRIBUTION.md if new sources used
    └─ Document in arena website
```

### 6.2 — Abdeckung linguistischer Phänomene

Jedes Korpus sollte Einträge enthalten, die spezifische linguistische Phänomene testen, die für das Sprachpaar relevant sind. Diese werden aus den Feldern `linguisticChallenges` und `contactInfluences` der Sprachkarte abgeleitet:

**Universelle Phänomene (alle Sprachpaare):**
- Pronomenauflösung (mehrdeutige Antezedenzien)
- Negation (einfach, doppelt, Skopus)
- Quantoren (alle, einige, keine, die meisten)
- Temporale Ausdrücke (relative Daten, Zeitspannen)
- Eigennamen (Personen, Orte, Organisationen)
- Zahlen und Maßangaben
- Listen und Aufzählungen

**Paarspezifische Phänomene (aus der Sprachkarte):**
- Für polysynthetische Zielsprachen: komplexe Verbmorphologie, Inkorporation
- Für genusmarkierende Zielsprachen: Genuskongruenz, neutrale/inklusive Referenz
- Für SOV-Zielsprachen: satzfinale Verben, Postpositionen
- Für Tonsprachen: tonabhängige Bedeutungsunterscheidungen
- Für honorativmarkierende Sprachen: Registermarker, sozialer Kontext
- Für Kontaktsprachen: Code-Switching-Grenzen, Integration von Lehnwörtern

### 6.3 — Mindestkorpusgröße

Statistische Zuverlässigkeit erfordert eine Mindestanzahl an Einträgen. Diese basieren auf den Anforderungen für gepaarte Bootstrap-Konfidenzintervalle (aus `significance.py`):

| Zweck | Mindesteinträge | Empfohlen |
|---------|-----------------|-------------|
| Entwicklungsset | 50 | 100–200 |
| Zurückgehaltenes Evaluationsset | 100 | 200–500 |
| Goldstandard-Set | 200 | 500+ |
| Mindestwert pro Domäne | 10 | 25+ |
| Mindestwert pro Stufe | 10 | 20+ |

**Warum mindestens 100 für die Evaluation?** Mit weniger als ~100 Einträgen können gepaarte Bootstrap-Signifikanztests (1.000 Resamples) Unterschiede, die kleiner als ~5 chrF++-Punkte sind, nicht zuverlässig erkennen. Mit 200+ Einträgen können wir Unterschiede von ~2 Punkten bei p<0,05 erkennen.

---

## 7. Korpus-JSON-Format

Jeder Korpuseintrag folgt der Harness-Spezifikation:

```json
{
  "id": "edtekla-dev-v1-042",
  "source": "The school board will meet on Tuesday to discuss the new curriculum.",
  "reference": "ᑭᓯᑭᓄᐦᐊᒫᑐᐏᓐ ᑲ ᐃᔑ ᐱᒥᐸᔨᐦᑕᐦᒃ ᑭᔅᑭᓄᐦᐊᒫᑐᐏᓇ ᐁ ᐃᔑ ᒫᒥᑐᓀᔨᐦᑕᐦᒃ ᐅᔥᑭ ᑭᔅᑭᓄᐦᐊᒫᑫᐏᓂᔭ ᓂᔓ ᑭᔑᑲᐤ",
  "acceptable_variants": [
    "ᑭᔅᑭᓄᐦᐊᒫᑐᐏᓐ ᓂᔓ ᑭᔑᑲᐤ ᑲ ᐃᔑ ᒫᒥᑐᓀᔨᐦᑕᐦᒃ ᐅᔥᑭ ᑭᔅᑭᓄᐦᐊᒫᑫᐏᓂᔭ"
  ],
  "domain": "edu",
  "difficulty": 3,
  "phenomena": ["temporal_expression", "named_entity", "future_tense"],
  "provenance": {
    "source_doc": "EdTeKLA Module 4, Unit 7",
    "source_license": "CC BY-NC-SA 4.0",
    "translator": "anonymous-speaker-001",
    "translator_qualification": "L1 Plains Cree, certified translator",
    "translation_date": "2025-11-15",
    "reviewer": "anonymous-speaker-002",
    "review_date": "2025-12-01"
  }
}
```

---

## 8. Anti-Gaming-Maßnahmen

### 8.1 — Korpusintegrität

| Maßnahme | Implementierung |
|---------|----------------|
| **Inhaltshashing** | Korpusversion = SHA-256 der sortierten Eintrags-IDs + Referenzen. Jede Änderung erzeugt eine neue Version. |
| **Eintragsfingerprinting** | Jeder Eintrag besitzt eine inhaltsabgeleitete ID. Wenn jemand Ergebnisse gegen ein modifiziertes Korpus einreicht, stimmt der Fingerprint nicht überein. |
| **Durchsetzung der Zurückhaltung** | Bei der offiziellen Evaluation erhalten Methoden NUR Quelltext. Referenzen werden niemals offengelegt. Die Bewertung erfolgt serverseitig. |
| **Rotationsplan** | Korpora rotieren jährlich, um eine langfristige Optimierung gegen ein festes Ziel zu verhindern. |

### 8.2 — Integrität der Einreichung

| Maßnahme | Implementierung |
|---------|----------------|
| **Deterministischer Fingerprint** | Die Run-Konfiguration (Modell, Temperatur, Prompt, Korpusversion) wird gehasht. Identische Konfigurationen erzeugen identische Fingerprints. |
| **Cherry-Pick-Erkennung** | Einreichende müssen alle Durchläufe offenlegen, nicht nur den besten. Mehrere Einreichungen mit demselben Fingerprint werden markiert. |
| **Kontaminationsprüfung** | Wenn Evaluationseinträge wortwörtlich im Prompt oder in den Coaching-Daten der Methode erscheinen, wird die Einreichung disqualifiziert. |

---

## 9. Bestehende Korpora

### 9.1 — EDTeKLA Development Set v1

| Eigenschaft | Wert |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Paar** | EN → CRK (Plains Cree, SRO) |
| **Einträge** | 404 (`master_corpus.json`: 62 Gold + 342 Lehrbuch); 548 insgesamt verfügbar |
| **Domänen** | Bildung (100%) |
| **Stufen** | 1–5 (Verteilung pro Eintragsaudit noch festzulegen) |
| **Lizenz** | CC BY-NC-SA 4.0 |
| **Status** | Entwicklungsset (öffentlich) |

**Einschränkungen:** Einzelne Domäne (nur Bildung). Keine Domänenstratifizierung. Stufenzuordnungen müssen möglicherweise auditiert werden. Die geringe Korpusgröße begrenzt die statistische Aussagekraft für Signifikanztests.

### 9.2 — Geplante Korpora

| Korpus | Paar | Status | Eigentümer |
|--------|------|--------|-------|
| EN → TL (Filipino) benutzerdefiniertes Korpus | EN → TL | Geplant | Projekteigentümer |
| EN → CRK zurückgehaltenes Set | EN → CRK | Zukünftig (benötigt Gemeinschaftspartner) | Gemeinschafts-Governance-Organisation |

---

## 10. Integration der Sprachkarte

Das Korpus-Framework integriert sich mit dem Sprachkartensystem:

1. **Die Domänenauswahl** wird durch die `linguisticChallenges` der Karte informiert — wenn eine Sprache einzigartige Herausforderungen aufweist (Polysynthese, Ton, Belebtheit), muss das Korpus Einträge enthalten, die diese testen.

2. **Die Schwierigkeitskalibrierung** verwendet die `classification` der Karte — die typologische Distanz zwischen Quell- und Zielfamilien beeinflusst, was als „schwierig" gilt.

3. **Die Registerabdeckung** verwendet die `registers` der Karte — wenn eine Sprache definierte Register besitzt (formal-filipino, taglish-professional, taglish-casual), sollte das Korpus Einträge auf jeder Registerebene enthalten.

4. **Das Testen des Kontakteinflusses** verwendet die `contactInfluences` der Karte — für Sprachen mit starken Entlehnungsschichten (Filipino: Spanisch + Englisch + Arabisch) sollten Einträge enthalten sein, die testen, ob Methoden Lehnwörter korrekt handhaben oder sie über-übersetzen.

5. **Die Schrifthandhabung** verwendet die `scripts[]` der Karte — für mehrschriftige Sprachen (Serbisch: Kyrillisch + Lateinisch) sollten Einträge enthalten sein, die die korrekte Schriftauswahl testen.

---

## Referenzen

- **Champollion Scoring Specification** — definiert alle Metriken, Composite-Gewichtungen, Qualitätsstufen
- **Champollion Benchmark Specification** — Evaluationsprotokoll, Korpusformat, Datensouveränität
- **WALS** (World Atlas of Language Structures) — Datenbank typologischer Merkmale
- **Glottolog** — maßgebliche Referenz für die Sprachklassifikation
- **ISO 639-3** — Standard zur Sprachidentifikation
- **EdTeKLA** — Quelle des ersten Evaluationskorpus

---

*Dieses Dokument ist eine lebende Spezifikation. Aktualisieren Sie es, wenn neue Korpora erstellt und Erkenntnisse gewonnen werden.*