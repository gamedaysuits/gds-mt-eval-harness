---
sidebar_position: 5
title: "Bewertungsspezifikation"
slug: '/specifications/scoring'
related:
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
    note: "When a score difference actually means something"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
    note: "The tool that computes these metrics"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "These scores, live"
---
# Bewertungsspezifikation

> **Zusammenfassung für die Geschäftsleitung.** Dies ist die zentrale, verbindliche Referenz für sämtliche Bewertungsmetriken, die zusammengesetzte Bewertung, die Qualitätsstufen und die Kostenanalyse im Champollion-MT-Bewertungsökosystem. Die sprachspezifischen Bewertungsmetriken — FST-morphologische Validität, Linter-Äquivalenzklassen und deterministische semantische Validierung — werden gemeinsam als **LYSS** (Linguistically-informed Yield & Structural Scoring) bezeichnet. Jede vom Harness berechnete Metrik, jede Gewichtung in der zusammengesetzten Formel und jeder Schwellenwert einer Stufe ist hier — und ausschließlich hier — definiert. Code, Dokumentation und Datenbankschemata leiten sich aus diesem Dokument ab. Bei Widersprüchen ist dieses Dokument maßgeblich.
>
> **Geltungsbereich.** Dieses Dokument definiert, *was* wir messen und *wie wir es bewerten*. Es definiert nicht das Run-Card-Schema (siehe BENCHMARK_SPEC §3), das Benchmark-Protokoll (BENCHMARK_SPEC §6) oder die Leaderboard-Regeln (siehe Arena-Dokumentation). Jene Dokumente verweisen für Metrikdefinitionen und Bewertungslogik auf dieses Dokument.
>
> Zuletzt aktualisiert: 2026-06-07

---

## 1. Bewertungsphilosophie

### 1.1 Microeval-Philosophie

> *"Wenn wir uns nur auf das konzentrieren, was generalisiert, werden wir unweigerlich vergessen, wo es das nicht tut — und diese Sprachen und all ihr Wissen und ihre Weisheit verlieren."*

Dieses Projekt praktiziert **Microeval-Entwicklung**: den Aufbau von Bewertungsmetriken, die mit den besten verfügbaren linguistischen Werkzeugen auf bestimmte Sprachen zugeschnitten sind — endliche Automaten (finite-state transducers), zweisprachige Wörterbücher, morphologische Analysatoren, von Linguisten kuratierte Äquivalenzregeln. Dies ist das Gegenteil des vorherrschenden Paradigmas in der MT-Bewertung, das universelle Metriken anstrebt, die sprachübergreifend funktionieren. Universelle Metriken sind wertvoll, aber sie sind genau dort am schwächsten, wo sie am dringendsten benötigt werden: für Sprachen mit komplexer Morphologie, begrenzten Trainingsdaten und ohne Vertretung in den Trainingsdatensätzen neuronaler Metriken.

Wir machen bei der maschinellen Übersetzung vieler Sprachen der Welt nicht nur deshalb keine Fortschritte, weil uns Korpora fehlen, sondern weil **wir nicht einmal wissen, wie Fortschritt aussieht** — uns fehlen die automatisierten Bewertungswerkzeuge, um zu messen, ob ein Übersetzungssystem besser wird. LYSS ist unser Versuch, diese Werkzeuge Sprache für Sprache aufzubauen, unter Nutzung aller verfügbaren linguistischen Ressourcen.

### 1.2 Automatisierte Metriken sind Näherungswerte

Jede hier definierte Metrik wird maschinell berechnet. Sie sind nützlich für rasche Iteration, systematischen Vergleich und das Erkennen von Regressionen. Sie sind **kein Ersatz für menschliches Urteilsvermögen**. Die Qualitätsstufen in §5 sind heuristische Bezeichnungen — nur menschliche Überprüfung kann die tatsächliche Verwendbarkeit bestätigen.

### 1.3 Mehrsignal-Design

Keine einzelne Metrik erfasst die Übersetzungsqualität. Eine Übersetzung kann eine perfekte chrF++-Überlappung aufweisen, aber die morphologische Validierung nicht bestehen. Sie kann FST-Prüfungen bestehen, aber die falsche Bedeutung tragen. Sie kann semantisch korrekt sein, aber stilistisch fremd für die Zielsprache. Die zusammengesetzte Bewertung in §4 aggregiert mehrere unabhängige Signale, von denen jedes eine andere Qualitätsdimension erfasst.

### 1.4 Erweiterbarkeit

Dieser Metrikbestand ist nicht abgeschlossen. Neue Sprachen bringen neue Anforderungen mit sich: Tongenauigkeit für Tonsprachen, diakritische Präzision für semitische Schriften, Silbenschriftkorrektheit für Cree. Die Architektur (MetricPlugin-Protokoll, gewichtete Zusammensetzung mit Neunormalisierung) ist darauf ausgelegt, dass Metriken hinzugefügt werden können, ohne bestehende Bewertungen zu beeinträchtigen. Sprachspezifische Metriken (z. B. der Linter und semantische Validator von CRK) werden auf Sprachkarten unter `evalMetrics` deklariert und aus `eval_standards/` geladen — das Harness wird ausschließlich mit generischen Verhaltensmetriken ausgeliefert (Code-Switching, Halluzination, Terminologie).

### 1.5 Drei Dimensionen der Bewertung

Jede Run Card misst drei unabhängige Dimensionen:

```
Quality   — How good is the translation?   (composite score, §4)
Cost      — How much does it cost?          (cost metrics, §6)
Speed     — How fast does it run?           (speed metrics, §7)
```

Dies sind unabhängige Achsen. Eine Methode kann hochwertig, aber teuer sein, schnell, aber ungenau, oder eine beliebige Kombination davon. Das Leaderboard ermöglicht die Sortierung nach jeder Dimension. Die kostenbereinigte Bewertung (§6.3) ist die einzige Metrik, die Dimensionen kombiniert.

### 1.6 Validierungsstatus

Jede Metrik in dieser Spezifikation hat einen **Validierungsstatus**, der sich von ihrem Implementierungsstatus (§3) unterscheidet. Der Implementierungsstatus verfolgt, ob Code existiert. Der Validierungsstatus verfolgt, ob nachgewiesen wurde, dass die Metrik mit menschlichen Qualitätsurteilen korreliert.

| Validierungsstufe | Bedeutung | Aktuelle Metriken |
|------------------|---------|----------------|
| **✅ Extern validiert** | Veröffentlichte Studien zur Korrelation mit menschlichem Urteil existieren (WMT, wissenschaftliche Arbeiten) | `chrf_plus_plus`, `bleu`, `comet_score` |
| **⚡ Näherungsvalidiert** | Validiert für ressourcenreiche Sprachen; nicht validiert für unsere LRL-Zielsprachen | `comet_score` (validiert für EU-Sprachpaare, nicht für CRK) |
| **🔶 Engineering-Heuristik** | Aus linguistischen Prinzipien oder beobachteten Fehlermodi entworfen; keine Daten zur Korrelation mit menschlichem Urteil | `fst_acceptance_rate`, `equivalent_match_rate`, `semantic_score`, `code_switching_rate`, `hallucination_rate`, `terminology_adherence` |
| **🔲 Nicht validiert** | Noch nicht an Daten getestet | `morphological_accuracy`, `orthographic_accuracy`, `consistency_score` |

> **Was dies in der Praxis bedeutet.** Die zusammengesetzte Bewertung (§4) aggregiert Metriken aller Validierungsstufen. Dies ist eine bewusste Designentscheidung: Wir sind der Ansicht, dass eine strukturell begründete Engineering-Heuristik (FST-Akzeptanz) für polysynthetische Sprachen aussagekräftiger ist als eine neuronale Metrik, die nur an europäischen Sprachpaaren validiert wurde (COMET). Wir haben dies jedoch nicht bewiesen. Die zusammengesetzte Bewertung sollte als **Engineering-Schätzung** behandelt werden, nicht als validierte Qualitätsmessung, bis Studien zur Korrelation mit menschlichem Urteil für jede Zielsprache abgeschlossen sind.
>
> **Erforderliche Validierungsexperimente** (siehe `mt-evaluation-landscape.md` §6 und `speaker-validation.md`):
> 1. Studie zur Korrelation mit menschlichem Urteil: 200+ Satzpaare, bewertet von 3+ zweisprachigen Sprechern
> 2. Messung der Falschablehnungsrate (false rejection rate) des FST an einem repräsentativen Korpus
> 3. Portierung auf eine zweite Sprache (Nordsamisch) zur Prüfung der Generalisierung
> 4. Direkter Vergleich mit COMET an denselben Daten


---

## 2. Metrikbestand {#2-metric-inventory}

Die Metriken sind in vier Kategorien gegliedert. Jede Metrik hat einen Implementierungsstatus, eine Skala und eine Ebene (pro Eintrag, auf Korpusebene oder beides).

### 2.1 Oberflächenmetriken

Oberflächenmetriken vergleichen die vorhergesagte Übersetzung mit der Referenzübersetzung auf Zeichenkettenebene. Sie erfordern keine linguistischen Werkzeuge — nur einen Zeichenkettenvergleich.

| ID | Metrik | Status | Skala | Ebene | Implementierung |
|----|--------|--------|-------|-------|---------------|
| `exact_match_rate` | Exact Match | ✅ Implementiert | 0.0–1.0 | Beide | Binär: stimmt predicted == reference? Korpusrate = Treffer / Gesamt. |
| `equivalent_match_rate` | Equivalent Match | ⚡ Teilweise | 0.0–1.0 | Beide | Stimmt die vorhergesagte Ausgabe mit einer akzeptierten Variante überein? Für CRK: implementiert über die `CrkLinterMetric` des CRK-Bewertungsstandards (in `eval_standards/crk/`) mittels deterministischer Variantenklassenregeln (Wortstellung, Orthografie, optionale Partikel, Lemmasynonym, progressive Mehrdeutigkeit). Wird automatisch über die `evalMetrics`-Deklaration der CRK-Sprachkarte geladen. Generische sprachübergreifende Implementierung erfordert pro Eintrag `variants[]` im Korpus. |
| `chrf_plus_plus` | chrF++ | ✅ Implementiert | 0–100 | Beide | Zeichen-n-Gramm-F-Wert (sacrebleu). Robust gegenüber morphologischer Variation. Die primäre Oberflächenmetrik für agglutinierende/polysynthetische Sprachen. Pro Eintrag wird `sentence_chrf` verwendet; auf Korpusebene `corpus_chrf`. |
| `bleu` | BLEU | ✅ Implementiert | 0–100 | Korpus | Wortbasierte n-Gramm-Präzision (sacrebleu). **Von der Zusammensetzung ausgeschlossen** — die wortbasierte Bewertung bestraft morphologische Variation in unangemessener Weise. Wird zur Kompatibilität mit der MT-Literatur berechnet und ausgewiesen. |
| `ter` | Translation Edit Rate | ✅ Implementiert | 0–∞ (niedriger ist besser) | Beide | Minimale Editierdistanz zwischen predicted und reference, normalisiert nach Referenzlänge (sacrebleu `corpus_ter`). Wird neben chrF++ und BLEU berechnet. Von der Zusammensetzung ausgeschlossen — korreliert mit chrF++, sodass die Aufnahme beider die Oberflächenähnlichkeit doppelt zählen würde. |
| `length_ratio` | Length Ratio | ✅ Implementiert | 0–∞ (1.0 ist ideal) | Beide | `len(predicted) / len(reference)` in Zeichen. Erkennt Trunkierung (<0,5) und Inflation/Halluzination (>2,0). Auf Korpusebene über die Einträge gemittelt. |

### 2.2 Strukturmetriken

Strukturmetriken validieren die linguistische Wohlgeformtheit der Übersetzung. Sie erfordern sprachspezifische Werkzeuge (FST-Analysatoren, morphologische Parser) und sind die stärksten Signale für morphologisch reiche Sprachen.

| ID | Metrik | Status | Skala | Ebene | Implementierung |
|----|--------|--------|-------|-------|---------------|
| `fst_acceptance_rate` | FST Acceptance | ✅ Implementiert | 0.0–1.0 | Beide | Anteil der Ausgabewörter, die von einem endlichen Automaten (GiellaLT) akzeptiert werden. Ein Wort ist „gültig", wenn der FST mindestens eine morphologische Analyse zurückgibt. Verfügbar für jede Sprache mit einem GiellaLT-`.hfstol`-Analysator. |
| `morphological_accuracy` | Morphological Accuracy | 🔲 Geplant | 0.0–1.0 | Beide | Ein Wort kann FST-gültig sein, aber die falsche Flexion aufweisen (richtige Wurzel, falsches Suffix). Diese Metrik vergleicht die FST-Analyse des vorhergesagten Wortes mit den erwarteten morphologischen Merkmalen. Erfordert morphologische Annotationen pro Eintrag im Korpus. |
| `orthographic_accuracy` | Orthographic Accuracy | 🔲 Geplant | 0.0–1.0 | Beide | Validiert schriftspezifische Korrektheit: SRO-Makron-/Zirkumflexverwendung für Cree, diakritische Zeichen für Inuktitut, Vokallängenmarkierungen für Ojibwe. Sprachspezifische Regelsätze. |

> **Warum Strukturmetriken wichtig sind.** Metas OMT-1600 — das größte je veröffentlichte MT-System (1.600 Sprachen) — wertet mit ChrF++, xCOMET, MetricX und BLASER 3 aus. Keine davon validiert die morphologische Korrektheit. ChrF++ misst die Zeichen-n-Gramm-Überlappung: Es belohnt Zeichenketten, die *aussehen* wie die Zielsprache. Für polysynthetische Sprachen bedeutet dies, dass ein morphologisch ungültiges Wort, das viele Zeichen mit der Referenz teilt, gut abschneidet. Unsere FST-Akzeptanzmetrik ist ein binärer Strukturtest: Das Wort ist entweder eine gültige Form in der Sprache oder nicht. Kein anderes MT-Bewertungsframework bietet dies in diesem Umfang.

### 2.3 Semantische Metriken

Semantische Metriken messen die Bedeutungserhaltung mithilfe von Embeddings oder erlernten Modellen. Sie erfassen Übersetzungen, die sich oberflächlich unterscheiden, aber bedeutungsgleich sind, und kennzeichnen Übersetzungen, die oberflächlich ähnlich, aber semantisch falsch sind.

| ID | Metrik | Status | Skala | Ebene | Implementierung |
|----|--------|--------|-------|-------|---------------|
| `semantic_score` | Semantic Similarity | ⚡ Teilweise | 0.0–1.0 | Beide | CRK: verdiktgewichtete Bewertung aus dem `CrkSemanticMetric` des CRK-Bewertungsstandards (in `eval_standards/crk/`, Näherung). Universell: Kosinusähnlichkeit von Satz-Embeddings (Quelle + predicted gegenüber Quelle + reference). Modell noch festzulegen — muss ressourcenarme Sprachen unterstützen, was die meisten englischzentrierten Embedding-Modelle ausschließt. |
| `comet_score` | COMET | ✅ Implementiert | ~0.0–1.0 | Beide | Erlernte MT-Bewertungsmetrik (Unbabel). Auf menschlichen Qualitätsurteilen trainiert. **Von der Zusammensetzung ausgeschlossen** — die Trainingsdaten sind zugunsten ressourcenreicher europäischer Sprachen verzerrt; Bewertungen für LRLs sind unzuverlässig. Wird berechnet, wenn `unbabel-comet` installiert ist. Wird mit einem Warnhinweis für ressourcenarme Sprachen ausgewiesen. Für 35 afrikanische Sprachen wählt das Harness automatisch AfriCOMET (`masakhane/africomet-mtl`) über `resolve_comet_model()`, das für diese Sprachen eine bessere Korrelation mit menschlichem Urteil aufweist. |

> **Warum COMET von der Zusammensetzung ausgeschlossen ist.** COMET wird auf WMT-Daten zur menschlichen Bewertung trainiert, bei denen es sich überwiegend um ressourcenreiche europäische Sprachpaare handelt. Bei der Anwendung auf Plains Cree oder andere LRLs haben die internen Repräsentationen des Modells keinerlei Berührung mit diesen Sprachen — es extrapoliert aus Sprachen mit grundlegend anderen morphologischen Systemen. Die Bewertungen sind weiterhin richtungsweisend nützlich (höheres COMET ≈ generell flüssiger klingende Ausgabe), aber die absoluten Werte sind nicht kalibriert. Wir weisen COMET zur Transparenz aus, lassen es aber die zusammengesetzte Bewertung nicht beeinflussen, bis wir es für jede Zielsprache gegen menschliche Urteile validieren können.

> **AfriCOMET für afrikanische Sprachen.** Jede Sprachkarte hat ein `metricModelSupport`-Feld (siehe Sprachkartenspezifikation §9), das angibt, welche spezialisierten COMET-Modelle für diese Sprache trainiert sind. Für 35 afrikanische Sprachen (yor, hau, ibo, amh, swa usw.) deklariert die Karte AfriCOMET (`masakhane/africomet-mtl`) — ein COMET-Modell, das von der Masakhane-Community auf menschlichen MT-Urteilen für afrikanische Sprachen feinabgestimmt wurde. Das Harness wählt das empfohlene Modell automatisch über `resolve_comet_model()` aus, das aus den Sprachkarten liest, dies kann jedoch mit `--comet-model` überschrieben werden. Das Hinzufügen neuer Sprach→Modell-Zuordnungen erfolgt durch Anreicherung der Sprachkarte (nicht durch Bearbeitung von Python-Code).

### 2.4 Verhaltensmetriken

Verhaltensmetriken erkennen spezifische Fehlermodi in der Übersetzungsausgabe. Sie messen die Qualität nicht direkt — sie erkennen Probleme.

| ID | Metrik | Status | Skala | Ebene | Implementierung |
|----|--------|--------|-------|-------|---------------|
| `code_switching_rate` | Code-Switching Rate | ✅ Implementiert | 0.0–1.0 (niedriger ist besser) | Beide | Anteil der Ausgabewörter, die in der Quellsprache (in der Regel Englisch) vorliegen. Erkannt über Unicode-Schriftanalyse und/oder eine Wortliste der Quellsprache. Sehr häufiger LLM-Fehlermodus: Das Modell fügt englische Wörter ein, wenn es das zielsprachliche Äquivalent nicht kennt. |
| `hallucination_rate` | Hallucination Rate | ✅ Implementiert | 0.0–1.0 (niedriger ist besser) | Beide | Anteil des Ausgabeinhalts, der keinem Quellinhalt entspricht. Erkannt über Wortausrichtung oder sprachübergreifende Embedding-Überlappung. Erfasst, wenn das Modell plausibel klingende, aber erfundene Übersetzungen generiert. |
| `terminology_adherence` | Terminology Adherence | ✅ Implementiert | 0.0–1.0 | Beide | Für angeleitete (coached) Methoden: Anteil der vorgeschriebenen Terminologiebegriffe, die in der Ausgabe erscheinen. Erfordert Coaching-Wörterbuchdaten. Misst, ob das Modell das von Experten bereitgestellte Vokabular einhält. |
| `consistency_score` | Cross-Entry Consistency | 🔲 Geplant | 0.0–1.0 | Nur Korpus | Übersetzt das Modell denselben Quellbegriff über alle Einträge hinweg gleich? Geringe Konsistenz deutet darauf hin, dass das Modell rät, anstatt erlernte Muster anzuwenden. Erfordert wiederholte Begriffe über die Korpuseinträge hinweg. |

### 2.5 Konformitätsmetriken

Konformitätsmetriken validieren, dass Übersetzungen die strukturelle Integrität wahren — Platzhalter, Formatierung und typografische Konventionen. Sie sind Qualitätstor-Prüfungen, keine Qualitätsbewertungen.

| ID | Metrik | Status | Skala | Ebene | Implementierung |
|----|--------|--------|-------|-------|---------------|
| `compliance_index` | Double-Pass Compliance | ✅ Implementiert | 0.0–1.0 | Beide | Gewichtete Zusammensetzung: 60 % Variablenintegrität (sind `{placeholder}`-Variablen erhalten?) + 20 % Anführungszeichen-Konformität (korrekte Anführungszeichen je Sprachkarte) + 20 % Groß-/Kleinschreibungs-Konformität (kein Durchsickern lateinischer Buchstaben für Sprachen ohne Groß-/Kleinschreibung). Wird sowohl auf der Rohausgabe als auch auf der nachverarbeiteten Ausgabe berechnet. Über `DoublePassCompliancePlugin`. |
| `repair_effectiveness` | Repair Effectiveness | ✅ Implementiert | 0.0–1.0 | Korpus | Anteil der Konformitätsverstöße, die durch Nachübersetzungs-Hooks automatisch behoben wurden. Misst, wie stark das Qualitätstor die Rohausgabe verbessert hat. |

> **Warum Konformität nicht in der Zusammensetzung enthalten ist.** Konformitätsmetriken messen die strukturelle Erhaltung (Platzhalter, Anführungszeichen), nicht die Übersetzungsqualität. Eine Übersetzung kann linguistisch perfekt sein, die Konformität aber nicht bestehen, weil sie eine `{name}`-Variable weggelassen hat. Dies sind Qualitätstore — sie verhindern, dass schlechte Ausgaben ausgeliefert werden, aber sie bewerten nicht die Übersetzungsqualität.

---

## 3. Metrikstatusstufen

Jede Metrik in §2 fällt in eine von vier Implementierungsstufen:

| Stufe | Bedeutung | Run-Card-Verhalten |
|------|---------|-------------------|
| **✅ Implementiert** | Code existiert, getestet, liefert heute Werte in Run Cards | Numerischer Wert in der Run Card |
| **⚡ Teilweise** | Sprachspezifische Näherung existiert (z. B. CRK), aber die universelle Implementierung steht aus | Numerischer Wert, wenn die Näherung greift, sonst `null` |
| **🔲 Geplant** | Spezifiziert, aber noch nicht implementiert | `null` in der Run Card (Feld vorhanden, Wert fehlt) |
| **💡 Vorgeschlagen** | In Diskussion, noch nicht spezifiziert | Nicht in der Run Card |

Eine Metrik wechselt von Geplant → Teilweise, wenn:
1. Eine sprachspezifische Implementierung zusammengeführt und getestet wurde
2. Sie Werte für mindestens ein Sprachpaar liefert
3. Die universelle Implementierung weiterhin aussteht (dokumentiert in dieser Spezifikation)

Eine Metrik wechselt von Teilweise → Implementiert, wenn:
1. Eine sprachunabhängige Implementierung zusammengeführt und getestet wurde
2. Sie Werte für jedes beliebige Sprachpaar ohne sprachspezifische Plugins liefert
3. Dieses Dokument aktualisiert wird, um den Status ✅ widerzuspiegeln

Eine Metrik wechselt von Geplant → Implementiert, wenn:
1. Die Implementierung zusammengeführt und getestet wurde
2. Sie an mindestens einem realen Bewertungslauf validiert wurde
3. Dieses Dokument mit ihren Implementierungsdetails aktualisiert wird

Eine Metrik wechselt von Vorgeschlagen → Geplant, wenn:
1. Ihre Definition, Skala und Berechnungsmethode vereinbart sind
2. Sie diesem Dokument mit dem Status `🔲 Planned` hinzugefügt wird
3. Ein Null-Platzhalter dem Run-Card-Schema hinzugefügt wird

---

## 4. Zusammengesetzte Bewertung {#4-composite-score}

### 4.1 Formel

Die zusammengesetzte Bewertung ist ein gewichteter Mittelwert aller *verfügbaren* Metriken, neunormalisiert, sodass sich die Gewichtungen der verfügbaren Metriken auf 1,0 summieren:

```
composite = Σ (weight_i × value_i)    for all available metrics
             ─────────────────────
             Σ weight_i               (re-normalization denominator)
```

Eine Metrik ist „verfügbar", wenn ihr Wert in der Run Card eine Zahl ist (nicht `null`). Wenn eine Metrik nicht verfügbar ist — weil die Sprache keinen FST hat oder weil eine Metrik noch nicht implementiert ist — wird ihre Gewichtung proportional auf die verbleibenden Metriken umverteilt.

**Dies bedeutet, dass die Zusammensetzung innerhalb eines Laufs stets vergleichbar ist:** Sie verwendet alle verfügbaren Metriken und normalisiert entsprechend. Ein laufübergreifender Vergleich ist gültig, wenn die Läufe dieselbe Menge verfügbarer Metriken verwenden.

> [!WARNING]
> **Laufübergreifende Vergleichbarkeit.** Beim Vergleich von Läufen mit unterschiedlicher Metrikverfügbarkeit (z. B. ein Lauf hat FST-Bewertungen, ein anderer nicht) sind die zusammengesetzten Bewertungen **nicht direkt vergleichbar**. Eine aus 5 Metriken berechnete Zusammensetzung von 0,72 trägt mehr Information als eine aus 2 Metriken berechnete Zusammensetzung von 0,72. Das Leaderboard zeigt eine Warnung an, wenn sich die Metrikabdeckung zwischen verglichenen Läufen unterscheidet. Für einen rigorosen Vergleich verwenden Sie gepaarte Bootstrap-Signifikanztests (§8.2) ausschließlich auf gemeinsamen Metriken.

### 4.2 Eingangsnormalisierung

Bevor sie in die Zusammensetzungsformel eingehen, müssen alle Metriken auf einer **Skala von 0,0–1,0** liegen, wobei 1,0 = perfekt:

| Metrik | Native Skala | Normalisierung |
|--------|-------------|---------------|
| `exact_match_rate` | 0.0–1.0 | Keine (bereits normalisiert) |
| `equivalent_match_rate` | 0.0–1.0 | Keine |
| `fst_acceptance_rate` | 0.0–1.0 | Keine |
| `morphological_accuracy` | 0.0–1.0 | Keine |
| `chrf_plus_plus` | 0–100 | **Durch 100 teilen** |
| `semantic_score` | 0.0–1.0 | Keine |
| `code_switching_rate` | 0.0–1.0 (niedriger = besser) | **`1.0 - value`** (invertieren: 0 % Code-Switching = 1,0) |
| `hallucination_rate` | 0.0–1.0 (niedriger = besser) | **`1.0 - value`** (invertieren) |
| `terminology_adherence` | 0.0–1.0 | Keine |

Metriken, die von der Zusammensetzung ausgeschlossen sind (`bleu`, `comet_score`, `ter`, `length_ratio`, `consistency_score`), werden zu diesem Zweck nicht normalisiert.

### 4.3 Gewichtungstabellen {#43-weight-tables}

#### Profil A: Sprachen MIT FST-Abdeckung

Für Sprachen, für die ein endlicher Automat von GiellaLT verfügbar ist. Strukturmetriken tragen 40 % der Zusammensetzung (FST 0,25 + morphologische Genauigkeit 0,15) und spiegeln den Vorrang der morphologischen Korrektheit für polysynthetische/agglutinierende Sprachen wider.

| Metrik | Zielgewichtung | Begründung |
|--------|--------------|-----------|
| `fst_acceptance_rate` | **0.25** | Höchste Gewichtung. Wenn der FST ein Wort ablehnt, ist es keine gültige Form in der Sprache — unabhängig davon, was andere Metriken sagen. Binär, strukturell begründet. |
| `morphological_accuracy` | **0.15** | Ein Wort kann FST-gültig, aber morphologisch falsch sein (richtige Wurzel, falsche Flexion). Zusammen mit FST tragen die Strukturmetriken 40 %. |
| `chrf_plus_plus` | **0.15** | Zeichen-n-Gramm-Überlappung: die beste oberflächliche Näherung für polysynthetische Sprachen. Bewältigt agglutinierende Morphologie besser als wortbasierte Metriken. |
| `semantic_score` | **0.15** | Bedeutungserhaltung bei abweichender Oberflächenform. Erfasst semantisch falsche Übersetzungen, die Strukturprüfungen bestehen. |
| `equivalent_match_rate` | **0.10** | Belohnt akzeptable Varianten, nicht nur die eine Referenzübersetzung. Wichtig für Sprachen mit flexibler Wortstellung. |
| `code_switching_rate` | **0.05** | Bestraft Durchsickern der Quellsprache. Invertiert: 0 % Code-Switching = 1,0. |
| `terminology_adherence` | **0.05** | Belohnt angeleitete Methoden, die das vorgeschriebene Vokabular einhalten. Nur aktiv, wenn Coaching-Daten vorhanden sind. |
| `hallucination_rate` | **0.05** | Bestraft erfundene Inhalte. Invertiert: 0 % Halluzination = 1,0. |
| `exact_match_rate` | **0.05** | Niedrigste Gewichtung. Zu streng für polysynthetische Sprachen — es existieren mehrere korrekte Übersetzungen. Beibehalten als Obergrenzenprüfung. |

> **Gesamt: 1,00.** Wenn Metriken nicht verfügbar sind, werden ihre Gewichtungen proportional auf die verfügbaren Metriken umverteilt. Derzeit ist `morphological_accuracy` (Gewichtung 0,15) die einzige Metrik von Profil A, die noch nicht berechnet wird — sie erfordert morphologische Goldstandard-Annotationen pro Eintrag. Bei Fehlen dieser Metrik werden die verbleibenden 8 Metriken (Gesamtgewichtung 0,85) jeweils mit 1/0,85 ≈ 1,176 skaliert. Zum Beispiel:
> - FST: 0,25/0,85 = 0,294
> - chrF++: 0,15/0,85 = 0,176
> - semantic: 0,15/0,85 = 0,176

#### Profil B: Sprachen OHNE FST-Abdeckung

Für Sprachen ohne morphologische Validierungswerkzeuge. Semantische und Oberflächenmetriken tragen gleiches Gewicht.

| Metrik | Zielgewichtung | Begründung |
|--------|--------------|-----------|
| `semantic_score` | **0.25** | Ohne strukturelle Validierung ist die Bedeutungserhaltung das stärkste verfügbare Signal. |
| `chrf_plus_plus` | **0.25** | Ohne FST wird die Überlappung auf Zeichenebene zur primären Oberflächenprüfung. |
| `equivalent_match_rate` | **0.15** | Variantenabgleich bietet eine strukturierte Qualitätsbeurteilung, ohne morphologische Werkzeuge zu erfordern. |
| `exact_match_rate` | **0.10** | Ohne FST trägt Exact Match mehr Gewicht als einzige Näherung für strukturelle Validierung. |
| `code_switching_rate` | **0.10** | Das Durchsickern der Quellsprache ist von größerer Bedeutung, wenn kein FST vorhanden ist, um schlechte Ausgaben zu erfassen. |
| `terminology_adherence` | **0.05** | Konformität mit dem angeleiteten Vokabular. |
| `hallucination_rate` | **0.05** | Erkennung erfundener Inhalte. |
| `orthographic_accuracy` | **0.05** | Schriftspezifische Korrektheit füllt einen Teil der durch das fehlende FST entstandenen Lücke. |

> **Gesamt: 1,00.** `orthographic_accuracy` (Gewichtung 0,05) ist geplant, wird aber noch nicht berechnet. Bei dessen Fehlen werden die verbleibenden 7 Metriken (Gesamtgewichtung 0,95) mit 1/0,95 ≈ 1,053 skaliert — eine vernachlässigbare Auswirkung auf die Zusammensetzung.

> **Hinweis zur Entwicklung der Gewichtungen.** Diese Gewichtungen sind vorläufig und werden neu kalibriert, sobald sich menschliche Validierungsdaten ansammeln. Das langfristige Ziel ist die empirische Ableitung der Gewichtungen: Welche automatisierten Metriken sagen die menschlichen Qualitätsurteile für jede Sprachfamilie am besten voraus?

### 4.4 Hinzufügen einer neuen Metrik zur Zusammensetzung

So fügen Sie der Zusammensetzung eine neue Metrik hinzu:

1. **Definieren Sie sie** in §2 mit dem Status `🔲 Planned`, einschließlich Skala, Ebene und Berechnungsmethode.
2. **Implementieren Sie sie** als MetricPlugin (oder in `tester.py` für Kernmetriken).
3. **Fügen Sie einen Null-Platzhalter** im Bewertungsblock der Run Card hinzu.
4. **Weisen Sie ihr eine Zielgewichtung** in §4.3 zu, indem Sie bestehende Gewichtungen nach unten anpassen. Die Gewichtungen müssen sich auf 1,00 summieren.
5. **Aktualisieren Sie BENCHMARK_SPEC.md** §3, wenn sich das Run-Card-Schema ändert.
6. **Aktualisieren Sie die Gewichtungstabellen von `scoring.py`** (der Code muss dieses Dokument widerspiegeln).
7. **Führen Sie einen Validierungs-Benchmark durch**, um zu bestätigen, dass die Metrik auf realen Daten sinnvolle Werte liefert.
8. **Aktualisieren Sie dieses Dokument**, um den Status von `🔲` auf `✅` zu ändern.

---

## 5. Qualitätsstufen {#5-quality-tiers}

Diese Stufen sind heuristische Bezeichnungen für automatisierte zusammengesetzte Bewertungen. Sie beschreiben, was die Bewertungen in der Praxis tendenziell bedeuten, basierend auf der menschlichen Überprüfung von Ausgaben auf jeder Stufe. **Sie sind keine validierten Qualitätsurteile** — nur menschliche Überprüfung kann die tatsächliche Verwendbarkeit bestätigen.

> [!IMPORTANT]
> **Automatisierte Stufen sind vorläufig.** Diese Bezeichnungen sind Nominierungen zur Überprüfung, keine Qualitätserklärungen. Eine Methode, die auf automatisierten Metriken die Stufe „Einsatzbereit" (Deployable) erreicht, ist ein Kandidat für die Community-Bewertung — kein auslieferungsfertiges Produkt. Nur menschliche Überprüfung durch zweisprachige Sprecher kann die tatsächliche Verwendbarkeit bestätigen (siehe [BENCHMARK_SPEC §7](/docs/specifications/benchmark#7-human-validation)). Keine Methode kann „Einsatzbereit" oder höher beanspruchen, ohne dass eine Community-Überprüfung bestätigt, dass Sprecher die Ausgabe für verwendbar halten. Die Stufengrenzen können sich zwischen den Sprachen unterscheiden, sobald sich menschliche Validierungsdaten ansammeln.

| Stufe | Zusammensetzungsbereich | Was ein Sprecher typischerweise sieht |
|------|----------------|-------------------------------|
| **Baseline** | 0.00–0.30 | Rohe LLM-Ausgabe ohne sprachspezifische Unterstützung. Die Morphologie ist überwiegend halluziniert. |
| **Emerging** | 0.30–0.50 | Einige korrekte Muster treten auf. Das Coaching hilft, aber die Ausgabe ist nicht zuverlässig. |
| **Functional** | 0.50–0.70 | Die Ausgabe ist für einen Sprecher erkennbar. Wichtige grammatische Kategorien meist korrekt. Häufige morphologische Fehler. |
| **Deployable** | 0.70–0.85 | Geeignet für Rohübersetzungen mit menschlicher Überprüfung. Die meiste Morphologie ist korrekt. |
| **Fluent** | 0.85–1.00 | Nähert sich kompetenter menschlicher Übersetzung. Fehler sind selten und geringfügig. |

Diese Stufen sind vorläufig. Sie werden neu kalibriert, sobald sich menschliche Validierungsdaten ansammeln und wir lernen, wo der Schwellenwert „ein Sprecher findet dies nützlich" für jede Sprache tatsächlich liegt. Keine Methode kann **Deployable** oder höher beanspruchen, ohne dass eine Community-Überprüfung bestätigt, dass zweisprachige Sprecher die Ausgabe für verwendbar halten.

### 5.1 Stufenschwellenwerte (maschinenlesbar)

Für Code-Implementierungen lauten die Schwellenwerte (von oben nach unten ausgewertet, erster Treffer gewinnt):

```
composite >= 0.85  →  "fluent"
composite >= 0.70  →  "deployable"
composite >= 0.50  →  "functional"
composite >= 0.30  →  "emerging"
composite >= 0.00  →  "baseline"
composite is null  →  "unscored"
```

---

## 6. Kostenmetriken

Kostenmetriken messen die finanzielle Effizienz einer Übersetzungsmethode. Sie werden getrennt von der Qualität ausgewiesen — die Kosten beeinflussen die zusammengesetzte Bewertung nicht (außer in der kostenbereinigten Sekundärrangfolge).

### 6.1 Token-Metriken

| ID | Metrik | Berechnung |
|----|--------|-------------|
| `prompt_tokens` | Eingabe-Token gesamt | Summe von `usage.prompt_tokens` über alle API-Aufrufe |
| `completion_tokens` | Ausgabe-Token gesamt | Summe von `usage.completion_tokens` |
| `reasoning_tokens` | Chain-of-Thought-Token | Summe von `usage.completion_tokens_details.reasoning_tokens` (0 für die meisten Modelle) |
| `cached_tokens` | Vom Anbieter zwischengespeicherte Token | Summe von `usage.prompt_tokens_details.cached_tokens` |
| `total_tokens` | Verbrauchte Token gesamt | `prompt_tokens + completion_tokens` |
| `tokens_per_entry` | Durchschnittliche Token pro Übersetzung | ✅ `total_tokens / entry_count` |

### 6.2 Kostenmetriken

| ID | Metrik | Berechnung | Anwendungsfall |
|----|--------|-------------|----------|
| `total_cost_usd` | Gesamtkosten des Laufs | Vom Anbieter ausgewiesene Preise × Token-Anzahl | „Wie viel hat dieser Benchmark gekostet?" |
| `cost_per_entry_usd` | Kosten pro Korpuseintrag | `total_cost_usd / entry_count` | Vergleich von Methoden auf demselben Korpus |
| `cost_per_1k_tokens` | Kosten pro 1.000 Token | ✅ `total_cost_usd / total_tokens × 1000` | Universelle LLM-Effizienz — korpusübergreifend vergleichbar |
| `cost_per_source_char` | Kosten pro Quellzeichen | `total_cost_usd / total_source_chars` | Vergleichbar über Sprachen mit unterschiedlicher Tokenisierung hinweg |

> **Warum mehrere Kostenmetriken?** Ein „Eintrag" variiert in der Länge — eine Phrase aus 3 Wörtern kostet weniger als ein Absatz. `cost_per_entry_usd` ist nützlich für den Vergleich von Methoden auf *demselben* Korpus (gleiche Einträge = gleiche Längen = fairer Vergleich). `cost_per_1k_tokens` ist die standardmäßige LLM-Effizienzmetrik, *korpusübergreifend* vergleichbar. `cost_per_source_char` normalisiert für Tokenisierungsunterschiede — derselbe Satz kann je nach Vokabular des Modells in unterschiedlich viele Token zerlegt werden.

### 6.3 Kostenbereinigte Bewertung

Für Methoden, die kostenpflichtige APIs verwenden, berechnen wir eine Sekundärrangfolge:

```
cost_adjusted = composite / log2(1 + cost_per_entry_usd × 1000)
```

Dies belohnt Methoden, die effizient gute Bewertungen erzielen. Sie verwendet `cost_per_entry_usd` (nicht pro Token), da die kostenbereinigte Bewertung stets innerhalb eines einzelnen Benchmarks (gleicher Korpus) berechnet wird, was den Vergleich pro Eintrag fair macht.

Die kostenbereinigte Bewertung ist eine **Sekundärrangfolge** — das primäre Leaderboard ordnet nach der zusammengesetzten Bewertung. Sie beantwortet eine andere Frage: „Welche Methode liefert bei gegebenem Budget die besten Ergebnisse?"

---

## 7. Geschwindigkeitsmetriken

Geschwindigkeitsmetriken messen die Latenz und den Durchsatz einer Übersetzungsmethode. Wie die Kosten beeinflusst die Geschwindigkeit die zusammengesetzte Bewertung nicht.

| ID | Metrik | Berechnung | Ebene |
|----|--------|-------------|-------|
| `elapsed_seconds` | Laufdauer (Echtzeit) | `time_end - time_start` | Lauf |
| `avg_latency_seconds` | Mittlere Latenz pro Eintrag | `Σ latency_s / n_entries` | Korpus |
| `median_latency_seconds` | Median-Latenz pro Eintrag | 50. Perzentil von `latency_s` | Korpus |
| `p95_latency_seconds` | 95.-Perzentil-Latenz | 95. Perzentil von `latency_s` | Korpus |
| `tokens_per_second` | Durchsatz | `total_tokens / elapsed_seconds` | Lauf |
| `entries_per_minute` | Übersetzungsrate | `entry_count / (elapsed_seconds / 60)` | Lauf |

---

## 8. Konfidenz und Signifikanz

### 8.1 Bootstrap-Konfidenzintervalle

Alle Schlüsselmetriken unterstützen Bootstrap-Konfidenzintervalle (Perzentilmethode, n=1000 Resamples, α=0,05):

| Metrik | Ausgewiesenes KI |
|--------|------------|
| `chrf_plus_plus` | ✅ `chrf_ci_lower`, `chrf_ci_upper` |
| `exact_match_rate` | ✅ `exact_match_ci_lower`, `exact_match_ci_upper` |
| `fst_acceptance_rate` | ✅ `fst_ci_lower`, `fst_ci_upper` (nur berechnet, wenn FST-Daten vorhanden sind) |
| `comet_score` | ✅ `comet_ci_lower`, `comet_ci_upper` (aus zwischengespeicherten Bewertungen pro Eintrag gebootstrappt — keine redundante neuronale Inferenz) |
| `composite` | ✅ `composite_ci_lower`, `composite_ci_upper` (berechnet, wenn chrF++ und exact_match verfügbar sind) |
| KIs pro Stufe | ✅ `confidence_intervals_by_tier` — chrF++- und exact_match-KIs je Schwierigkeitsstufe (Tier 1-5) |

### 8.2 Gepaarte Bootstrap-Signifikanztests

Zum Vergleich zweier Methoden berechnet das Harness gepaarte Bootstrap-Resampling-Tests:

```
H₀: The two methods perform equally on this corpus.
H₁: One method is significantly better.
```

Wenn der p-Wert < 0,05 ist und das Konfidenzintervall der Differenz die Null ausschließt, ist die Differenz auf dem 95-%-Niveau statistisch signifikant.

---

## 9. Run-Card-Bewertungsschema

Dieser Abschnitt definiert die hierarchische Struktur des `scores`-Blocks in einer Run Card. Dieses Schema leitet sich aus den in §2–§7 definierten Metriken ab und muss synchron gehalten werden.

```jsonc
{
  "scores": {
    // §2.1 Surface metrics
    "exact_match_rate":       0.6613,       // 0.0–1.0
    "exact_matches":          41,           // count
    "equivalent_match_rate":  0.7258,       // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "equivalent_matches":     45,           // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "chrf_plus_plus":         80.65,        // 0–100 (sacrebleu native scale)
    "bleu":                   54.78,        // 0–100, NOT in composite
    "ter":                    42.3,         // ✅ implemented, 0–∞ (lower=better)
    "length_ratio":           1.03,         // ✅ implemented, ideal=1.0

    // §2.2 Structural metrics
    "fst_acceptance_rate":    1.0,          // 0.0–1.0
    "fst_accepted":           74,           // count
    "morphological_accuracy": null,         // 🔲 planned
    "orthographic_accuracy":  null,         // 🔲 planned

    // §2.3 Semantic metrics
    "semantic_score":         0.6842,       // ⚡ partial (CRK: eval_standards/crk CrkSemanticMetric)
    "comet_score":            null,         // nullable, NOT in composite
    "comet_model":            "",           // model ID used for COMET

    // §2.4 Behavioral metrics
    "code_switching_rate":    0.03,         // ✅ implemented (lower=better)
    "hallucination_rate":     0.01,         // ✅ implemented (lower=better)
    "terminology_adherence":  null,         // ✅ implemented (null when no glossary)
    "consistency_score":      null,         // 🔲 planned

    // §4 Composite
    "composite":              0.8988,       // 0.0–1.0
    "quality_tier":           "fluent",     // §5 tier label
    "cost_adjusted":          null,         // §6.3 secondary ranking

    // §7 Speed metrics (merged into scores block)
    "tokens_per_second":      4462.5,       // ✅ total_tokens / elapsed
    "entries_per_minute":     82.30,        // ✅ entry_count / (elapsed/60)
    "avg_latency_seconds":    0.234,
    "median_latency_seconds": 0.190,
    "p95_latency_seconds":    0.415,

    // §8.1 Confidence intervals
    "confidence_intervals": {
      "chrf_plus_plus":     { "ci_lower": 78.2, "ci_upper": 83.1 },
      "exact_match_rate":   { "ci_lower": 0.54, "ci_upper": 0.78 },
      "corpus_comet":       { "ci_lower": 0.71, "ci_upper": 0.76 }
    },
    "confidence_intervals_by_tier": {
      "1": { "corpus_chrf": { "ci_lower": 68.1, "ci_upper": 76.5 } },
      "3": { "corpus_chrf": { "ci_lower": 36.2, "ci_upper": 47.0 } }
    },

    // Breakdowns
    "by_difficulty":          {},           // scores grouped by difficulty tier
    "by_provenance":          {},           // scores grouped by entry provenance

    // Counts
    "total":                  62,
    "evaluated":              62,
    "errors":                 0
  },

  "totals": {
    // §6.1 Token metrics
    "prompt_tokens":          13985,
    "completion_tokens":      187822,
    "reasoning_tokens":       175726,
    "cached_tokens":          0,
    // §6.2 Cost metrics
    "total_cost_usd":         1.7114,
    "cost_per_entry_usd":     0.027603,
    "cost_per_source_char":   null          // 🔲 needs source char counting
  }
}
```

> **Schemaverlauf.** Frühere Spezifikationsentwürfe schlugen separate `cost`-, `speed`- und `tokens`-Blöcke vor. Diese wurden der Einfachheit halber zu `scores` bzw. `totals` zusammengeführt. Geschwindigkeitsmetriken (`tokens_per_second`, `entries_per_minute`, Latenzen) befinden sich in `scores`; Token-Anzahlen und Kostenkennzahlen befinden sich in `totals`.

### 9.1 Schema-Datenbank-Zuordnung

Die Run-Card-JSON wird vollständig als `jsonb`-Spalte in Supabase gespeichert. Schlüsselmetriken werden außerdem zur Sortier-/Filterleistung in Spalten der obersten Ebene denormalisiert:

| Run-Card-Feld | Supabase-Spalte | Typ | Index |
|---------------|----------------|------|-------|
| `scores.composite` | `composite_score` | `real` | `idx_composite` |
| `scores.quality_tier` | `quality_tier` | `text` | — |
| `scores.chrf_plus_plus` | `chrf_plus_plus` | `real` | `idx_leaderboard` |
| `scores.exact_match_rate` | `exact_match_rate` | `real` | — |
| `scores.fst_acceptance_rate` | `fst_acceptance_rate` | `real` | — |
| `scores.bleu` | `corpus_bleu` | `real` | — |
| `scores.comet_score` | `comet_score` | `real` | — |
| `totals.total_cost_usd` | `total_cost_usd` | `real` | — |
| `totals.cost_per_entry_usd` | `cost_per_entry_usd` | `real` | — |
| `totals.cost_per_source_char` | `cost_per_source_char` | `real` | — |
| `scores.avg_latency_seconds` | `avg_latency_seconds` | `real` | — |
| `model_slug` | `model_slug` | `text` | `idx_model` |
| `condition` | `condition` | `text` | — |
| `dataset.id` | `dataset_id` | `text` | `idx_leaderboard` |
| `dataset.language_pair` | `language_pair` | `text` | — |
| `fingerprint.hash` | `fingerprint_hash` | `text` | `idx_fingerprint` |
| `scores.equivalent_match_rate` | `equivalent_match_rate` | `real` | — |
| `scores.semantic_score` | `semantic_score` | `real` | — |
| `scores.ter` | `ter` | `real` | — |
| `scores.length_ratio` | `length_ratio` | `real` | — |
| `scores.code_switching_rate` | `code_switching_rate` | `real` | — |
| `scores.hallucination_rate` | `hallucination_rate` | `real` | — |
| `scores.terminology_adherence` | `terminology_adherence` | `real` | — |
| `scores.tokens_per_second` | `tokens_per_second` | `real` | — |
| `scores.entries_per_minute` | `entries_per_minute` | `real` | — |
| `elapsed_seconds` | `elapsed_seconds` | `real` | — |
| *(vollständige Karte)* | `run_card` | `jsonb` | — |

Wenn neue Metriken implementiert werden, sollte die entsprechende Spalte über eine nummerierte Migration in `arena/migrations/` hinzugefügt werden.

---

## 10. Code-Spezifikations-Synchronisierung

### 10.1 Kanonische Quelle

Dieses Dokument (`arena/website/docs/specifications/scoring.md`) ist die kanonische Quelle für:
- Metrikdefinitionen (§2)
- Zusammengesetzte Gewichtungstabellen (§4.3)
- Schwellenwerte der Qualitätsstufen (§5.1)
- Kostenmetrikformeln (§6.2)
- Run-Card-Bewertungsschema (§9)

### 10.2 Code-Spiegelung

Die Datei `arena/mt_eval_harness/scoring.py` spiegelt die Gewichtungstabellen und Stufenschwellenwerte aus diesem Dokument. Sie ist die **Code-Implementierung** von §4.3 und §5.1. Wenn dieses Dokument aktualisiert wird:

1. Aktualisieren Sie `scoring.py` entsprechend
2. Führen Sie `pytest tests/test_scoring_ssot.py` aus, um die Übereinstimmung zu validieren
3. Aktualisieren Sie FAQ und Website-Dokumentation, die die Gewichtungen zusammenfassen

### 10.3 Dokumente, die auf diese Spezifikation verweisen

| Dokument | Worauf es verweist | Wie es synchron gehalten wird |
|----------|-------------------|---------------------|
| `arena/website/docs/specifications/benchmark-spec.md` §4–§5 | Zusammensetzungsformel, Gewichtungstabellen, Stufenschwellenwerte | Verweisen Sie auf dieses Dokument; duplizieren Sie keine Tabellen |
| `website/docs/getting-started/faq.md` | Vereinfachte Gewichtungszusammenfassung | Muss mit §4.3 übereinstimmen; verlinken Sie zurück auf dieses Dokument |
| `arena/website/docs/how-it-works.md` | Deployable-Schwellenwert | Muss mit §5 übereinstimmen |
| `publish.py` über `scoring.py` | Gewichtungs-Dicts + Stufenfunktion | Ein automatisierter Test validiert die Übereinstimmung |

---

## Anhang A: Metriken, die NICHT in der Zusammensetzung enthalten sind (und warum)

| Metrik | Grund für den Ausschluss |
|--------|-------------|
| **BLEU** | Die wortbasierte Bewertung bestraft morphologische Variation in polysynthetischen Sprachen. Ein geringfügiger Flexionsunterschied (korrekte Bedeutung, leicht abweichendes Suffix) zählt als vollständiger Fehlschlag. chrF++ bewältigt dies auf Zeichenebene besser. |
| **COMET** | Auf WMT-Daten trainiert (ressourcenreiche europäische Sprachpaare). Bewertungen für LRLs sind unzuverlässig — das Modell extrapoliert aus Sprachen mit anderen morphologischen Systemen. Zur Transparenz ausgewiesen, nicht zur Bewertung. |
| **TER** | Die Editierdistanz korreliert für die meisten Anwendungsfälle mit chrF++. Die Aufnahme beider würde die Oberflächenähnlichkeit doppelt zählen. TER wird als Referenz ausgewiesen. |
| **Length Ratio** | Ein Diagnosewert, kein Qualitätssignal. Ein Verhältnis von 1,02 und ein Verhältnis von 0,98 sind beide in Ordnung. Nur extreme Werte deuten auf Probleme hin. |
| **Consistency Score** | Nur auf Korpusebene — kein Wert pro Eintrag zum Aggregieren. Zudem ist eine gewisse Inkonsistenz legitim (dasselbe englische Wort → unterschiedliche zielsprachliche Übersetzungen je nach Kontext). |
| **Compliance Index** | Qualitätstor, kein Qualitätssignal. Misst die strukturelle Erhaltung (Platzhalter, Anführungszeichen), nicht die Übersetzungsgenauigkeit. |

## Anhang B: LYSS — Sprachspezifische Metrikimplementierungen

Das **LYSS**-Framework (Linguistically-informed Yield & Structural Scoring) stellt sprachspezifische Metriken bereit, die über den oberflächlichen Zeichenkettenvergleich hinausgehen. LYSS hat drei Kernkomponenten:

- **LYSS-fst** — Morphologische Validität (`fst_acceptance_rate`): Ist jedes Wort eine gültige Form in der Zielsprache?
- **LYSS-eq** — Linguistische Äquivalenz (`equivalent_match_rate`): Ist die Ausgabe eine akzeptable Variante der Referenz?
- **LYSS-sem** — Semantische Validierung (`semantic_score`): Erhält die Ausgabe die Quellbedeutung?

> **Validierungsstatus: 🔶 Engineering-Heuristik.** LYSS-Metriken wurden NICHT gegen menschliche Qualitätsurteile validiert. Sie sind aus linguistischen Prinzipien entworfen (FSTs, Wörterbücher, von Linguisten am UAlberta ALTLab erstellte Grammatikregeln), aber die Korrelation zwischen LYSS-Bewertungen und tatsächlicher Übersetzungsqualität wurde nicht gemessen. Siehe das [Speaker-Validierungsprotokoll](/docs/specifications/speaker-validation) für die erforderlichen Validierungsexperimente.

| Sprache | Plugin | Speicherort | LYSS-Komponente | Metrikschlüssel | Hinweise |
|----------|--------|----------|----------------|------------|-------|
| CRK (Plains Cree) | `CrkLinterMetric` | `eval_standards/crk/metrics.py` | **LYSS-eq** | `equivalent_match_rate` | Deterministische Variantenklassenregeln: Wortstellung, Orthografie, optionale Partikel, Lemmasynonym, progressive Mehrdeutigkeit, inklusiv/exklusiv. Erzeugt pro Eintrag `lint_verdict` (EXACT/EQUIVALENT/MISS/NO_OUTPUT). |
| CRK | `CrkSemanticMetric` | `eval_standards/crk/metrics.py` | **LYSS-sem** | `semantic_score` | Deterministisch: FST-Lemmaextraktion + Wörterbuchglossen + spaCy-Inhaltswortüberlappung. Erzeugt Verdikte (EXACT_MATCH/VALID/GRAMMAR_ISSUES/PARTIAL/INCOMPLETE/WRONG/NO_OUTPUT). |
| GiellaLT-Sprachen | `GiellaLTFSTMetric` | `plugins/giellalt_fst.py` | **LYSS-fst** | `fst_acceptance_rate` | Generisch: funktioniert für CRK, SME, SMA, SMJ, SMN, SMS, FIN, NOB, IKU — jede Sprache mit einem `.hfstol`-Analysator. |

> **Architekturhinweis (Juni 2026).** Sprachspezifische LYSS-Metriken werden nun auf der Sprachkarte unter `evalMetrics` deklariert und von `plugin_discovery.py` aus `eval_standards/<lang>/` geladen. Es handelt sich um **Bewertungsstandards** (Schiedsrichter), nicht um Methoden-Plugin-Metriken (Wettbewerber). Dies bedeutet, dass jede Übersetzungsmethode mit Zielsprache CRK automatisch von LYSS bewertet wird — keine methodenspezifische Konfiguration erforderlich. `CrkFSTMetric` wurde entfernt; seine Funktionalität wird vollständig vom generischen `GiellaLTFSTMetric` abgedeckt.

## Anhang C: In Betracht gezogene Metriken

Dies sind Ideen, die geprüft, aber noch nicht ausreichend für §2 spezifiziert sind:

| Idee | Was sie messen würde | Hindernisse |
|------|----------------------|----------|
| Flüssigkeit (LM-Perplexität) | Ist die Ausgabe wohlgeformte Prosa in der Zielsprache? | Erfordert ein zielsprachliches LM. Für die meisten LRLs existieren keine guten Modelle. |
| Registerabgleich | Entspricht die Übersetzung der erwarteten Formalitätsebene? | Erfordert soziolinguistische Klassifikatoren. Forschungsproblem. |
| Kulturelle Angemessenheit | Werden kulturelle Bezüge korrekt behandelt? | Kann nicht automatisiert werden — erfordert von Natur aus menschliche Überprüfung. |
| Diskurskohärenz | Bilden aufeinanderfolgende Übersetzungen eine kohärente Passage? | Erfordert eine Bewertung auf Dokumentebene, nicht auf Satzebene. |

---

## Literaturverzeichnis

Wissenschaftliche Arbeiten, Werkzeuge und Sprachressourcen, die in dieser Spezifikation zitiert werden.

### Oberflächenmetriken

1. Popović, M. (2017). "chrF++: words helping character n-grams." *Proceedings of the Second Conference on Machine Translation (WMT 2017)*, pp. 612–618. Copenhagen, Denmark.

2. Papineni, K., Roukos, S., Ward, T., & Zhu, W.-J. (2002). "BLEU: a method for automatic evaluation of machine translation." *Proceedings of the 40th Annual Meeting of the Association for Computational Linguistics (ACL 2002)*, pp. 311–318. Philadelphia, PA.

3. Post, M. (2018). "A Call for Clarity in Reporting BLEU Scores." *Proceedings of the Third Conference on Machine Translation (WMT 2018)*, pp. 186–191. Belgium, Brussels. Referenzimplementierung: [sacrebleu](https://github.com/mjpost/sacrebleu).

4. Snover, M., Dorr, B., Schwartz, R., Micciulla, L., & Makhoul, J. (2006). "A Study of Translation Edit Rate with Targeted Human Annotation." *Proceedings of the 7th Conference of the Association for Machine Translation in the Americas (AMTA 2006)*, pp. 223–231. Cambridge, MA.

### Neuronale Metriken

5. Rei, R., Stewart, C., Farinha, A. C., & Lavie, A. (2020). "COMET: A Neural Framework for MT Evaluation." *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP 2020)*, pp. 2685–2702. Online.

6. Juraska, J., Finkelstein, M., Deutsch, D., Siddhant, A., Miber, D., & Markl, A. (2023). "MetricX-23: The Google Submission to the WMT 2023 Metrics Shared Task." *Proceedings of the Eighth Conference on Machine Translation (WMT 2023)*. Singapore.

7. Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2020). "BERTScore: Evaluating Text Generation with BERT." *Proceedings of the Eighth International Conference on Learning Representations (ICLR 2020)*. Addis Ababa, Ethiopia.

8. Sellam, T., Das, D., & Parikh, A. (2020). "BLEURT: Learning Robust Metrics for Text Generation." *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020)*, pp. 7881–7892. Online.

### Morphologische und linguistische Werkzeuge

9. Lindén, K., Silfverberg, M., Axelson, E., Hardwick, S., & Pirinen, T. (2011). "HFST—Framework for Compiling and Applying Morphologies." *Systems and Frameworks for Computational Morphology (SFCM 2011)*, Communications in Computer and Information Science, vol. 100, pp. 67–85. Springer, Berlin, Heidelberg.

10. Sánchez-Cartagena, V. M., & Toral, A. (2024). "MorphEval: Automatic Evaluation of Morphological Capabilities of Machine Translation Systems." *Machine Translation*, vol. 38, pp. 1–28.

### Fehlerklassifikation und diagnostische Bewertung

11. Popović, M. (2011). "Hjerson: An Open Source Tool for Automatic Error Classification of Machine Translation Output." *The Prague Bulletin of Mathematical Linguistics*, no. 96, pp. 59–68.

12. Dreyer, M. & Marcu, D. (2012). "HyTER: Meaning-Equivalent Semantics for Translation Evaluation." *Proceedings of the 2012 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2012)*, pp. 162–171. Montréal, Canada.

13. Reiter, E. & Belz, A. (2009). "An Investigation into the Validity of Some Metrics for Automatically Evaluating Natural Language Generation Systems." *Computational Linguistics*, vol. 35, no. 4, pp. 529–558. (Verwandte Arbeit zu merkmalsbasierten Bewertungsmetriken, einschließlich FUSE.)

### Halluzinationserkennung

14. Raunak, V., Menezes, A., & Junczys-Dowmunt, M. (2021). "The Curious Case of Hallucinations in Neural Machine Translation." *Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2021)*, pp. 1172–1183. Online.

15. Guerreiro, N. M., Voita, E., & Martins, A. F. T. (2023). "Looking for a Needle in a Haystack: A Comprehensive Study of Hallucinations in Neural Machine Translation." *Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2023)*, pp. 1059–1075. Dubrovnik, Croatia.

### Cree-Sprachressourcen

16. Wolfart, H. C. (1973). "Plains Cree: A Grammatical Study." *Transactions of the American Philosophical Society*, vol. 63, no. 5, pp. 1–90.

17. Wolvengrey, A. (2001). *nêhiyawêwin: itwêwina / Cree: Words.* Canadian Plains Research Center, University of Regina.

### Daten-Governance

18. First Nations Information Governance Centre. "The First Nations Principles of OCAP®." [https://fnigc.ca/ocap-training/](https://fnigc.ca/ocap-training/). (OCAP® ist eine eingetragene Marke des First Nations Information Governance Centre.)

19. Carroll, S. R., Garba, I., Figueroa-Rodríguez, O. L., Holbrook, J., Lovett, R., Materechera, S., Parsons, M., Raseroka, K., Rodriguez-Lonebear, D., Rowe, R., Sara, R., Walker, J. D., Anderson, J., & Hudson, M. (2020). "The CARE Principles for Indigenous Data Governance." *Data Science Journal*, vol. 19, no. 1, p. 43.