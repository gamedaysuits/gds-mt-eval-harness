---
sidebar_position: 5
title: "Eine ressourcenarme Sprache unterstützen"
related:
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "The first step for an uncovered language"
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
  - label: "Plains Cree, the trading card"
    to: https://champollion.dev/trading-cards?q=crk
    kind: card
    note: "The proof-of-concept language, as a card"
---
# Unterstützung einer ressourcenarmen Sprache

> **Zusammenfassung.** Ein umfassender Leitfaden zum Aufbau maschineller Übersetzung für ressourcenarme und polysynthetische Sprachen. Behandelt werden die Gründe für die Schwierigkeit dieser Sprachen (morphologische Komplexität, spärliche Daten, Halluzination), vorhandene rechnergestützte Ressourcen (ALTLab FST, GiellaLT, Apertium, UniMorph, EdTeKLA), über 10 Lösungsstrategien, das champollion-Coaching-System und der Evaluationszyklus. Beginnen Sie hier, wenn Sie eine Methode für eine unterversorgte Sprache beitragen möchten.

:::info Status: In aktiver Entwicklung
Die Unterstützung für Plains Cree (nêhiyawêwin) befindet sich derzeit in Entwicklung. Die hier beschriebenen Werkzeuge, das Evaluations-Harness und das Leaderboard sind real und bereits heute nutzbar, doch die Cree-Übersetzungspipeline wurde noch nicht veröffentlicht. Sobald dies geschieht, wird sie als Vorlage für weitere polysynthetische und ressourcenarme Sprachen mit FST-Infrastruktur dienen.
:::

## Das ungelöste Problem

Google Translate unterstützt ~130 Sprachen. Metas OMT-1600 (März 2026) beansprucht eine Abdeckung von 1.600 Sprachen — das größte je veröffentlichte MT-System. Doch für die ~1.300 Sprachen in ihren niedrigsten Ressourcenstufen liegt die Qualität unter den nutzbaren Schwellenwerten, die Trainingsdaten werden von Bibeltexten dominiert, die Modellgewichte stehen nicht zum Herunterladen zur Verfügung, und es gibt kein unabhängiges Evaluations- oder Community-Governance-Framework. Für die verbleibenden ~5.400 Sprachen erzeugt kein vortrainiertes Modell überhaupt eine Ausgabe.

Die Landschaft hat sich erheblich verändert — die großen Technologiekonzerne investieren nun in die Abdeckung ressourcenarmer Sprachen. Doch Abdeckung bedeutet nicht Qualität, und Qualität ohne unabhängige Verifizierung bedeutet kein Vertrauen. Ressourcenarme Sprachen benötigen mehr als ein Modell, das vorgibt, sie abzudecken — sie benötigen eine unabhängige Evaluation mit morphologischer Validierung, von der Community kuratierte Korpora und eine die Souveränität respektierende Governance.

**champollion wurde entwickelt, um dies zu ändern.**

Das [Method Leaderboard](https://champollion.dev/leaderboard) ist eine offene Herausforderung: Entwickeln Sie die beste Übersetzungsmethode für eine unterversorgte Sprache, belegen Sie sie mit einer reproduzierbaren Evaluation und beanspruchen Sie die Spitzenwertung. Jeder weltweit kann beitragen — Linguisten, ML-Forscher, Sprachmitarbeiter aus Communitys, Studierende, Hobbyisten. Das Problem ist ungelöst. Die Infrastruktur ist vorhanden. Das Leaderboard wartet.

---

## Warum dies schwierig ist: Polysynthetische Morphologie

Die meisten kommerziellen MT-Systeme wurden für Sprachen wie Englisch, Französisch und Chinesisch konzipiert — Sprachen, in denen Wörter relativ kurz sind und Sätze aus diskreten Tokens aufgebaut werden. Doch viele indigene Sprachen, darunter Plains Cree, sind **polysynthetisch**: Ein einzelnes Wort kann das ausdrücken, was im Englischen einen ganzen Satz erfordert.

### Das Cree-Beispiel

Betrachten Sie das Plains-Cree-Wort:

> **ê-kî-nitawi-kîskinwahamâkosiyân**
> *„als ich zur Schule ging“*

Das ist **ein Wort**. Es kodiert Tempus (Vergangenheit), Richtung (hingehen), den Wortstamm (lernen), Genus Verbi (Passiv/Reflexiv) und Person (erste Person Singular). Ein überwiegend mit Englisch trainiertes LLM hat keinerlei Intuition für diese Art morphologischer Dichte.

Die Herausforderungen häufen sich:

| Herausforderung | Was sie bedeutet |
|-----------|--------------|
| **Morphologische Komplexität** | Ein einzelner Verbstamm kann durch Präfigierung, Suffigierung und Zirkumfigierung Tausende gültiger flektierter Formen erzeugen |
| **Belebt/unbelebt-Unterscheidung** | Substantive sind grammatisch belebt oder unbelebt — dies wirkt sich auf Verbkonjugation, Demonstrativa und Pluralbildung aus. Die Klassifizierung folgt nicht immer der biologischen Belebtheit (*askiy* „Erde“ ist belebt; *maskisin* „Schuh“ ist ebenfalls belebt) |
| **Obviation** | Drittpersonen-Referenzen werden nach Nähe/Salienz geordnet. Die Unterscheidung zwischen „proximat“ und „obviativ“ hat kein englisches Äquivalent |
| **Spärliche Trainingsdaten** | LLMs haben sehr wenig Plains-Cree-Text gesehen. Was sie gesehen haben, vermischt möglicherweise Dialekte (Y-Dialekt, TH-Dialekt) oder Orthographien (SRO vs. Syllabics) |
| **Schwache kommerzielle Baseline** | OMT-1600 umfasst CRK in der R1-Stufe (Very Low Resource) mit Bibeltext-Domänentraining und standardmäßiger BPE-Tokenisierung. Google Translate unterstützt Cree nicht. Eine unabhängige Evaluation mit morphologischen Metriken macht diese Baselines erst aussagekräftig. |

Die Übersetzung polysynthetischer Sprachen bleibt ein **offenes Forschungsproblem** — OMT-1600 umfasst polysynthetische Sprachen, verwendet jedoch standardmäßige BPE-Tokenisierung (256K-Vokabular) ohne morphologisches Bewusstsein, was bedeutet, dass kompositionelle Wörter in bedeutungslose Byte-Fragmente zerlegt werden.

---

## Vorarbeiten: Wie man dieses Problem bisher angegangen ist

### Das ALTLab FST

Die bedeutendste rechnergestützte Ressource für Plains Cree ist der **Finite-State-Transducer (FST)**, der vom [Alberta Language Technology Lab (ALTLab)](https://altlab.artsrn.ualberta.ca/) an der University of Alberta in Zusammenarbeit mit [Giellatekno](https://giellatekno.uit.no/) an der UiT The Arctic University of Norway entwickelt wurde.

Das ALTLab FST ist ein **morphologischer Analysator und Generator**: Bei einem gegebenen flektierten Cree-Wort kann es dieses in seinen Wortstamm und seine grammatischen Tags zerlegen, und bei einem gegebenen Wortstamm samt Tags kann es die korrekte flektierte Form erzeugen. Dies ist deterministisch — kein neuronales Netz, keine Halluzination, keine Wahrscheinlichkeit. Wenn das FST ein Wort akzeptiert, ist dieses Wort morphologisch gültig.

Aus diesem Grund verfolgt das champollion-Leaderboard die **FST Acceptance Rate** als Metrik. Eine Übersetzungsmethode, die Wörter erzeugt, die das FST ablehnt, produziert morphologisch ungültiges Cree — unabhängig davon, was der chrF++-Wert besagt.

**Wichtige ALTLab-Ressourcen:**
- [itwêwina](https://itwewina.altlab.app/) — ein intelligentes Plains-Cree–Englisch-Wörterbuch, betrieben durch das FST
- [Morphodict](https://github.com/UAlbertaALTLab/morphodict) — quelloffene, morphologisch bewusste Wörterbuchplattform
- [crk-db](https://github.com/UAlbertaALTLab/crk-db) — lexikalische Datenbank für Plains Cree
- [21st Century Tools for Indigenous Languages](https://21c.tools/) — der umfassendere Projektkontext

### Globale FST- und Morphologie-Register

Plains Cree ist nicht die einzige Sprache mit hochwertiger FST-Infrastruktur. Wenn Sie Übersetzungspipelines für andere ressourcenarme oder morphologisch komplexe Sprachen entwickeln möchten, können Sie auf diese etablierten globalen Hubs zurückgreifen:

* **[GiellaLT / Giellatekno](https://giellalt.github.io/) (UiT The Arctic University of Norway):** Das größte Repository quelloffener morphologischer FST-Analysatoren und -Generatoren, das über 100 Sprachen abdeckt. Schwerpunkte sind die samischen Sprachen (`sme`, `smj`, `sma` usw.), die uralischen Sprachen (Komi, Erzya, Udmurtisch usw.) und weitere Minderheiten-/indigene Sprachen. Sie hosten öffentliche verarbeitete Textkorpora (`corpus-xxx`) in ihrer [GitHub Organization](https://github.com/giellalt/).
* **[The Apertium Project](https://www.apertium.org/):** Eine quelloffene, regelbasierte Plattform für maschinelle Übersetzung. Apertium pflegt hochoptimierte morphologische FST-Analysatoren (unter Verwendung von `lttoolbox` und `hfst`) und zweisprachige Wörterbücher für Dutzende von Sprachen, darunter eine große Reihe von Turksprachen (Kasachisch, Tatarisch, Kirgisisch usw.) und europäische Minderheitensprachen. Alle Ressourcen sind öffentlich auf [Apertiums GitHub](https://github.com/apertium) verfügbar.
* **[UniMorph (Universal Morphology)](https://unimorph.github.io/):** Ein kollaboratives Projekt, das standardisierte morphologische Paradigmen für über 150 Sprachen bereitstellt. Der Datensatz wird auf Hugging Face unter [unimorph/universal_morphologies](https://huggingface.co/datasets/unimorph/universal_morphologies) gehostet. Falls für eine Sprache kein kompiliertes FST-Binary verfügbar ist, können die UniMorph-Tabellen als statisches Datenbank-Lookup-Gate verwendet werden.
* **[National Research Council Canada (NRC)](https://nrc-digital-repository.canada.ca/):** Bietet Werkzeuge für kanadische indigene Sprachen, darunter den morphologischen FST-Analysator **Uqailaut** für Inuktitut und das umfangreiche **Nunavut Hansard Parallel Corpus** (1,3 Mio. ausgerichtete englisch-inuktitutische Satzpaare).

### Das EdTeKLA-Korpus

Die [EdTeKLA-Forschungsgruppe](https://spaces.facsci.ualberta.ca/edtekla/) (ebenfalls an der UAlberta) hat ein Plains-Cree-Sprachkorpus aus Bildungsmaterialien, Audiotranskriptionen und Community-Quellen zusammengestellt. Der champollion-Evaluationsdatensatz [EDTeKLA Dev v1](/docs/leaderboard/datasets) ist aus dieser Arbeit abgeleitet und unter [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) lizenziert.

### Weitere Ansätze, die ausprobiert wurden oder ausprobiert werden könnten

Das Leaderboard ist methodenunabhängig. Hier sind Strategien, die für ressourcenarme MT erforscht oder vorgeschlagen wurden und von denen jede eingereicht werden könnte:

| Ansatz | Funktionsweise | Vorteile | Nachteile |
|----------|-------------|------|------|
| **[Coached LLM prompting](/docs/tutorials/coached-llm-prompting)** | Einspeisung von Grammatikregeln, Wörterbüchern und Beispielpaaren in den System-Prompt | Schnelle Iteration, kein Training erforderlich | Qualitätsgrenze durch das Grundwissen des LLM beschränkt |
| **[Few-shot prompting](/docs/tutorials/few-shot-prompting)** | Verifizierte Übersetzungen als kontextbezogene Beispiele einbeziehen | Gut für konsistenten Stil | Kleines Kontextfenster; Beispiele dürfen NICHT aus den Evaluationsdaten stammen |
| **[FST-gated pipeline](/docs/tutorials/fst-gated-pipeline)** | LLM generiert → FST validiert → lehnt ungültige Morphologie ab und versucht es erneut | Garantiert morphologische Gültigkeit | Erfordert FST-Infrastruktur; Wiederholungsschleifen erhöhen Latenz und Kosten |
| **[Dictionary lookup + LLM](/docs/tutorials/dictionary-augmented-llm)** | Bekannte Begriffe aus einem zweisprachigen Wörterbuch erzwingen, den Rest dem LLM überlassen | Reduziert Halluzination bei bekannten Begriffen | Wörterbuchabdeckung ist immer unvollständig |
| **[Fine-tuned model](/docs/tutorials/fine-tuned-model)** | Feinabstimmung eines offenen Modells (Llama, Mistral) auf Paralleltext — nur nicht auf den Evaluationsdaten | Potenziell höchste Qualität | Erfordert ein Parallelkorpus (knapp); teuer; Overfitting-Risiko |
| **[Chained models](/docs/tutorials/chained-models)** | Modell A erzeugt Rohübersetzung → Modell B nachbearbeitet → Modell C bewertet | Kann Spezialistenstärken kombinieren | Komplex; langsam; teuer |
| **[Rule-based + LLM hybrid](/docs/tutorials/rule-based-hybrid)** | Linguistische Regeln für bekannte Muster, LLM für alles andere | Präzise dort, wo Regeln greifen | Erfordert tiefgehende linguistische Expertise |
| **[Back-translation augmentation](/docs/tutorials/back-translation)** | Synthetische Paralleldaten durch Übersetzung Cree→Englisch erzeugen und dann auf der Umkehrung trainieren | Erweitert Trainingsdaten kostengünstig | Verstärkt bestehende Modellfehler |
| **[Evolutionary approach](/docs/tutorials/evolutionary-approach)** | Kandidatenübersetzungen erzeugen, bewerten, die besten Performer mutieren, wiederholen | Kann neuartige Lösungen entdecken; parallelisierbar | Rechenintensiv; benötigt eine gute Fitnessfunktion |
| **[Partial translation](/docs/tutorials/partial-translation)** | Manuell eine repräsentative Stichprobe übersetzen, nachweisen, dass Ihre Methode Ihrem Stil entspricht, dann den Rest automatisch übersetzen | Verbindet menschliche Qualität mit maschineller Skalierung | Erfordert anfänglichen menschlichen Aufwand |
| **Manuelle JSON-/Prüfungsbewertung** | Eine Datensatz-JSON-Datei von Hand erstellen, um Studierendenantworten in einer Sprachprüfung zu testen, oder eine Reihe menschlicher Übersetzungen gegen einen Goldstandard bewerten | Kein ML erforderlich; geeignet für Bildung und QA | Nicht skalierbar für laufenden Übersetzungsbedarf |

### Es ist nur JSON

Das Harness nimmt JSON entgegen und gibt bewertetes JSON aus. Das [Datensatzformat](/docs/leaderboard/datasets) ist einfach:

```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

Sie können dies von Hand erstellen. Sie können es aus einer Tabellenkalkulation exportieren. Sie können es aus einem Korpus generieren. Ein Sprachlehrer könnte es zur Bewertung von Studierendenübersetzungen verwenden. Eine Übersetzungsagentur könnte es zum Benchmarking von Freiberuflern nutzen. Ein Forschungslabor könnte es zum Vergleich von Modellarchitekturen einsetzen. Dem Harness ist es gleichgültig, woher das JSON stammt — es bewertet es einfach.

Und da das Produktions-Deployment-Framework dieselbe Plugin-Schnittstelle nutzt, lässt sich eine Methode, die im Harness gut abschneidet, mit einer einzigen Konfigurationsänderung auf Ihrer Website bereitstellen. **Beweisen Sie es und setzen Sie es ein.**

Die Möglichkeiten sind wahrhaft grenzenlos. **Wenn Sie eine Idee haben, setzen Sie sie um, führen Sie das Harness aus und reichen Sie Ihre Scores ein.**

---

## Wie champollion ins Bild passt

champollion stellt die Infrastrukturschicht bereit — die Methode bringen Sie mit.

### Das Coaching-System

Die `llm-coached`-Methode von champollion ermöglicht es Ihnen, linguistisches Wissen direkt in den LLM-Prompt einzuspeisen:

```json title=".champollion/coaching/crk.json"
{
  "grammar_rules": [
    "Plains Cree is polysynthetic — a single word can express what English needs a full sentence for",
    "Animate/inanimate noun distinction affects verb conjugation, demonstratives, and pluralization",
    "Use SRO (Standard Roman Orthography) as the working script — syllabic conversion is handled by the deterministic converter",
    "Obviation: when two third-person referents appear, the less salient one takes obviative marking (-a suffix on nouns, -iyiwa on verbs)"
  ],
  "dictionary": {
    "home": "kīwēwin",
    "settings": "isi-nākatohkēwin",
    "search": "nānātawāpahtam",
    "welcome": "tānisi",
    "dashboard": "kīskinwahamākēwin-māsinahikan"
  },
  "style_notes": "Use formal register appropriate for educational and community contexts. Preserve English technical terms in parentheses when no Cree equivalent exists or is widely accepted."
}
```

Die Coaching-Daten werden in jeden LLM-Prompt für das `en:crk`-Sprachpaar eingespeist und geben dem Modell einen strukturierten linguistischen Kontext, den es andernfalls nicht hätte. Die vollständige Spezifikation finden Sie unter [Coaching Data](https://champollion.dev/docs/concepts/coaching-data).

### Register

Das Register ist Teil des System-Prompts, der Ton, Formalität und orthographische Konventionen steuert. champollion wird mit einem Plains-Cree-Register ausgeliefert:

```
nêhiyawêwin (Plains Cree). Use SRO (Standard Roman Orthography) as the working
script. Output will be converted to Syllabics via deterministic converter.
Professional register appropriate for educational and community contexts.
```

Sie können dies in Ihrer Konfiguration überschreiben, um mit verschiedenen Prompting-Strategien zu experimentieren:

```json title="champollion.config.json"
{
  "languages": {
    "crk": {
      "register": "Casual Plains Cree (Y-dialect). Use SRO. Prefer everyday vocabulary over formal or archaic terms. Address the reader directly."
    }
  }
}
```

Unterschiedliche Register erzeugen unterschiedliche Übersetzungsstile — und unterschiedliche Scores auf dem Leaderboard. Jede Einreichung erfasst das exakte verwendete Register und den System-Prompt (als SHA-256-Hash in der [Run Card](/docs/specifications/run-card)), sodass Experimente reproduzierbar sind.

### Schriftkonvertierung

Plains Cree wird in zwei Schriftsystemen geschrieben: **Standard Roman Orthography (SRO)** und **Canadian Aboriginal Syllabics**. Die champollion-Pipeline:

1. Das LLM übersetzt in SRO (lateinbasiert, womit LLMs besser umgehen können)
2. Das Qualitäts-Gate validiert die SRO-Ausgabe
3. Ein deterministischer Konverter transformiert SRO → Syllabics
4. Der konvertierte Text wird auf die Festplatte geschrieben

Der Konverter verarbeitet alle SRO-Diakritika (ê, î, ô, â für lange Vokale) und ordnet sie den korrekten Silbenzeichen zu. Technische Details finden Sie unter [Script Converters](https://champollion.dev/docs/concepts/script-converters).

### Der Evaluationszyklus

Das [Eval-Harness](/docs/specifications/harness) führt Ihre Methode gegen den Evaluationsdatensatz aus und erzeugt eine bewertete [Run Card](/docs/specifications/run-card):

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install -e .

# Run a baseline experiment
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v7

# Run with FST validation (if you have an FST binary)
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --fst-analyzer ./bin/crk-analyzer \
  --condition fst-gated-v1
```

Das `--condition`-Flag ist eine von Ihnen gewählte Kennzeichnung. Sie erscheint auf dem Leaderboard, sodass andere sehen können, welche Prompt-Strategie Sie verwendet haben. Das Harness erfasst den vollständigen System-Prompt in der Run Card, sodass Ihr genauer Ansatz reproduzierbar ist.

:::tip Experimentieren Sie frei, reichen Sie Ihr Bestes ein
Das Harness ist auf schnelle Iteration ausgelegt. Führen Sie Dutzende von Experimenten mit verschiedenen Modellen, Coaching-Daten, Registern und Bedingungen durch. Reichen Sie erst dann beim Leaderboard ein, wenn Sie etwas haben, auf das Sie stolz sind.
:::

---

## OCAP-Prinzipien

champollion ist darauf ausgelegt, die Datensouveränität indigener Völker zu unterstützen. Die [OCAP-Prinzipien](https://fnigc.ca/ocap-training/) (Ownership, Control, Access, Possession) leiten unseren Umgang mit Sprachtechnologie für indigene Gemeinschaften:

| Prinzip | Wie champollion es unterstützt |
|-----------|------------------------|
| **Ownership** | Sprachgemeinschaften besitzen ihre linguistischen Daten. champollion meldet sich niemals nach Hause und übermittelt keine Daten an unsere Server |
| **Control** | Die [API-Methode](https://champollion.dev/docs/guides/serving-a-method) ermöglicht es Gemeinschaften, ihre eigene Übersetzungspipeline zu hosten — wir stellen die Schnittstelle bereit, sie kontrollieren die Implementierung |
| **Access** | Gemeinschaften entscheiden, wer ihre Methode nutzen darf. Die API kann hinter einer Authentifizierung abgesichert werden |
| **Possession** | Alle Übersetzungsdaten verbleiben im Dateisystem Ihres Projekts. Das [Provenienzsystem](https://champollion.dev/docs/concepts/security) verfolgt, woher jede Übersetzung stammt |

Die Plugin-Architektur bedeutet, dass eine Gemeinschaft eine Methode entwickeln kann, die heiliges oder eingeschränktes Wissen intern einbindet, nur die Übersetzungs-API offenlegt und die volle Kontrolle über ihre linguistischen Ressourcen behält.

---

## Die Vision: Was als Nächstes kommt

Plains Cree ist das erste Ziel. Sobald die Pipeline validiert ist und die Gemeinschaft mit der Qualität zufrieden ist, lässt sich dieselbe Architektur auf andere polysynthetische Sprachen mit FST-Infrastruktur ausweiten:

- **Andere Algonkin-Sprachen**: Woods Cree, Swampy Cree, Ojibwe, Blackfoot
- **Inuit-Sprachen**: Inuktitut, Inuinnaqtun (die ebenfalls Silbenschriften verwenden)
- **Andere Sprachfamilien**: Jede Sprache mit einem FST-Analysator kann die FST-gated Pipeline nutzen

Das Leaderboard ist auf Sprachpaare ausgerichtet. Sobald neue Evaluationsdatensätze von Sprachgemeinschaften beigetragen werden, öffnen sich automatisch neue Leaderboard-Tracks.

**Dies ist eine offene Einladung.** Wenn Sie mit einer ressourcenarmen Sprache arbeiten — als Forscher, als Mitglied einer Gemeinschaft, als Studierender oder einfach als jemand, dem es am Herzen liegt — gibt Ihnen champollion die Werkzeuge an die Hand, um etwas Reales zu schaffen, es ehrlich zu messen und es mit der Welt zu teilen. Das [Method Leaderboard](https://champollion.dev/leaderboard) wartet auf Ihre Einreichung.

---

## Siehe auch

- **[Method Leaderboard](https://champollion.dev/leaderboard)** — reichen Sie Ihre Scores ein und sehen Sie, wie Methoden im Vergleich abschneiden
- **[MT Evaluation](/docs/leaderboard/rules)** — was eine gute Methode ausmacht, was zur Disqualifikation führt
- **[Eval Harness](/docs/specifications/harness)** — wie man Experimente durchführt
- **[Evaluation Datasets](/docs/leaderboard/datasets)** — EDTeKLA Dev v1 und FLORES+
- **[Coaching Data](https://champollion.dev/docs/concepts/coaching-data)** — wie man linguistisches Wissen für das LLM strukturiert
- **[Script Converters](https://champollion.dev/docs/concepts/script-converters)** — die SRO→Syllabics-Pipeline
- **[Serving a Method via API](https://champollion.dev/docs/guides/serving-a-method)** — Hosting einer community-kontrollierten Übersetzung
- **[ALTLab](https://altlab.artsrn.ualberta.ca/)** — das Alberta Language Technology Lab
- **[EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/)** — die Forschungsgruppe Educational Technology, Knowledge & Language
- **[itwêwina dictionary](https://itwewina.altlab.app/)** — FST-gestütztes Plains-Cree–Englisch-Wörterbuch