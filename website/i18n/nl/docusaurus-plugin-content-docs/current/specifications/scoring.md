---
sidebar_position: 5
title: "Scoringsspecificatie"
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
# Scoringsspecificatie

> **Samenvatting voor leidinggevenden.** Dit is de enige gezaghebbende bron voor alle evaluatiemetrieken, samengestelde scores, kwaliteitsniveaus en kostenanalyse binnen het Champollion MT-evaluatie-ecosysteem. De taalspecifieke evaluatiemetrieken — FST-morfologische validiteit, linter-equivalentieklassen en deterministische semantische validatie — worden gezamenlijk aangeduid als **LYSS** (Linguistically-informed Yield & Structural Scoring). Elke metriek die door het harnas wordt berekend, elk gewicht in de samengestelde formule en elke niveaudrempel is hier gedefinieerd — en uitsluitend hier. Code, documentatie en databaseschema's zijn afgeleid van dit document. Bij tegenstrijdigheden is dit document gezaghebbend.
>
> **Reikwijdte.** Dit document definieert *wat* we meten en *hoe we scoren*. Het definieert niet het run card-schema (zie BENCHMARK_SPEC §3), het benchmarkprotocol (BENCHMARK_SPEC §6) of de leaderboard-regels (zie arena-documentatie). Die documenten verwijzen naar dit document voor metriekdefinities en scoringslogica.
>
> Laatst bijgewerkt: 2026-06-07

---

## 1. Scoringsfilosofie

### 1.1 Microeval-filosofie

> *"If we only focus on what generalizes, we will inevitably forget about where it doesn't — and lose these languages and all their knowledge and wisdom."*

Dit project hanteert **microeval-ontwikkeling**: het bouwen van evaluatiemetrieken die zijn afgestemd op specifieke talen, met gebruikmaking van de beste beschikbare linguïstische hulpmiddelen — eindige-toestandstransducers, tweetalige woordenboeken, morfologische analysatoren en door taalkundigen samengestelde equivalentieregels. Dit staat tegenover het dominante paradigma in MT-evaluatie, dat streeft naar universele metrieken die voor alle talen werken. Universele metrieken zijn waardevol, maar ze zijn het zwakst precies waar ze het meest nodig zijn: voor talen met complexe morfologie, beperkte trainingsdata en geen vertegenwoordiging in trainingssets voor neurale metrieken.

We boeken niet alleen onvoldoende vooruitgang in machinevertaling voor veel talen in de wereld omdat we corpora missen, maar ook omdat **we niet eens weten hoe vooruitgang eruitziet** — we missen de geautomatiseerde evaluatietools om te meten of een vertaalsysteem verbetert. LYSS is onze poging om die tools te bouwen, taal voor taal, met gebruikmaking van alle beschikbare linguïstische bronnen.

### 1.2 Geautomatiseerde metrieken zijn benaderingen

Elke metriek die hier is gedefinieerd, wordt door een machine berekend. Ze zijn nuttig voor snelle iteratie, systematische vergelijking en het detecteren van regressies. Ze zijn **geen vervanging voor menselijk oordeel**. De kwaliteitsniveaus in §5 zijn heuristische labels — alleen menselijke beoordeling kan de werkelijke bruikbaarheid bevestigen.

### 1.3 Multi-signaalontwerp

Geen enkele metriek geeft een volledig beeld van vertaalkwaliteit. Een vertaling kan een perfecte chrF++-overlap hebben maar morfologische validatie niet doorstaan. Ze kan FST-controles doorstaan maar de verkeerde betekenis dragen. Ze kan semantisch nauwkeurig zijn maar stilistisch vreemd aanvoelen in de doeltaal. De samengestelde score in §4 aggregeert meerdere onafhankelijke signalen, elk gericht op een andere dimensie van kwaliteit.

### 1.4 Uitbreidbaarheid

Deze metriekinventaris is niet gesloten. Nieuwe talen brengen nieuwe vereisten met zich mee: toonnauwkeurigheid voor toontalen, diacritische precisie voor Semitische schriften, lettergreepnauwkeurigheid voor Cree. De architectuur (MetricPlugin-protocol, gewogen samengestelde score met hernormalisatie) is ontworpen zodat metrieken kunnen worden toegevoegd zonder bestaande scores te verstoren. Taalspecifieke metrieken (bijv. de linter en semantische validator van CRK) worden gedeclareerd op taalkaarten onder `evalMetrics` en geladen vanuit `eval_standards/` — het harnas wordt geleverd met uitsluitend generieke gedragsmetrieken (code-switching, hallucinatie, terminologie).

### 1.5 Drie dimensies van evaluatie

Elke run card meet drie onafhankelijke dimensies:

```
Quality   — How good is the translation?   (composite score, §4)
Cost      — How much does it cost?          (cost metrics, §6)
Speed     — How fast does it run?           (speed metrics, §7)
```

Dit zijn onafhankelijke assen. Een methode kan van hoge kwaliteit maar duur zijn, snel maar onnauwkeurig, of een willekeurige combinatie. Het leaderboard maakt sorteren op elke dimensie mogelijk. De kostengewogen score (§6.3) is de enige metriek die dimensies combineert.

### 1.6 Validatiestatus

Elke metriek in deze specificatie heeft een **validatiestatus** die losstaat van de implementatiestatus (§3). De implementatiestatus geeft aan of er code bestaat. De validatiestatus geeft aan of is aangetoond dat de metriek correleert met menselijke kwaliteitsoordelen.

| Validatieniveau | Betekenis | Huidige metrieken |
|-----------------|-----------|-------------------|
| **✅ Extern gevalideerd** | Er bestaan gepubliceerde studies naar correlatie met menselijke oordelen (WMT, academische publicaties) | `chrf_plus_plus`, `bleu`, `comet_score` |
| **⚡ Proxy-gevalideerd** | Gevalideerd voor talen met veel bronnen; niet gevalideerd voor onze doeltalen met weinig bronnen | `comet_score` (gevalideerd voor EU-taalparen, niet voor CRK) |
| **🔶 Technische heuristiek** | Ontworpen op basis van linguïstische principes of waargenomen faalpatronen; geen gegevens over correlatie met menselijke oordelen | `fst_acceptance_rate`, `equivalent_match_rate`, `semantic_score`, `code_switching_rate`, `hallucination_rate`, `terminology_adherence` |
| **🔲 Niet gevalideerd** | Nog niet getest op enige data | `morphological_accuracy`, `orthographic_accuracy`, `consistency_score` |

> **Wat dit in de praktijk betekent.** De samengestelde score (§4) aggregeert metrieken op alle validatieniveaus. Dit is een bewuste ontwerpkeuze: wij zijn van mening dat een structureel onderbouwde technische heuristiek (FST-acceptatie) informatiever is voor polysynthetische talen dan een neurale metriek die uitsluitend is gevalideerd op Europese taalparen (COMET). Maar dit hebben we niet bewezen. De samengestelde score dient te worden beschouwd als een **technische schatting**, niet als een gevalideerde kwaliteitsmeting, totdat er voor elke doeltaal studies naar correlatie met menselijke oordelen zijn voltooid.
>
> **Vereiste validatie-experimenten** (zie `mt-evaluation-landscape.md` §6 en `speaker-validation.md`):
> 1. Studie naar correlatie met menselijke oordelen: 200+ zinsparen beoordeeld door 3+ tweetalige sprekers
> 2. Meting van de FST-fout-afwijzingsgraad op een representatief corpus
> 3. Implementatie voor een tweede taal (Noord-Sámi) om generaliseerbaarheid te testen
> 4. Directe vergelijking met COMET op dezelfde data


---

## 2. Metriekinventaris

Metrieken zijn ingedeeld in vier categorieën. Elke metriek heeft een implementatiestatus, een schaal en een niveau (per invoer, corpusniveau of beide).

### 2.1 Oppervlaktemetrieken

Oppervlaktemetrieken vergelijken de voorspelde vertaling met de referentievertaling op tekenreeksniveau. Ze vereisen geen linguïstische hulpmiddelen — alleen tekenreeksvergelijking.

| ID | Metriek | Status | Schaal | Niveau | Implementatie |
|----|---------|--------|--------|--------|---------------|
| `exact_match_rate` | Exacte overeenkomst | ✅ Geïmplementeerd | 0,0–1,0 | Beide | Binair: is de voorspelling gelijk aan de referentie? Corpuspercentage = overeenkomsten / totaal. |
| `equivalent_match_rate` | Equivalente overeenkomst | ⚡ Gedeeltelijk | 0,0–1,0 | Beide | Komt de voorspelde uitvoer overeen met een geaccepteerde variant? Voor CRK: geïmplementeerd via de `CrkLinterMetric` van de CRK-evalstandaard (in `eval_standards/crk/`) met behulp van deterministische variantklasseregels (woordvolgorde, orthografisch, optioneel partikel, lemmasynoniem, progressieve ambiguïteit). Automatisch geladen via de `evalMetrics`-declaratie van de CRK-taalkaart. Generieke taaloverschrijdende implementatie vereist `variants[]` per invoer in het corpus. |
| `chrf_plus_plus` | chrF++ | ✅ Geïmplementeerd | 0–100 | Beide | Karakter-n-gram F-score (sacrebleu). Robuust voor morfologische variatie. De primaire oppervlaktemetriek voor agglutinerende/polysynthetische talen. Per invoer gebruikt `sentence_chrf`; corpus gebruikt `corpus_chrf`. |
| `bleu` | BLEU | ✅ Geïmplementeerd | 0–100 | Corpus | Woordniveau n-gram precisie (sacrebleu). **Uitgesloten van samengestelde score** — scoring op woordniveau bestraft morfologische variatie onterecht. Berekend en gerapporteerd voor compatibiliteit met MT-literatuur. |
| `ter` | Translation Edit Rate | ✅ Geïmplementeerd | 0–∞ (lager is beter) | Beide | Minimale bewerkingsafstand tussen voorspelling en referentie, genormaliseerd naar referentielengte (sacrebleu `corpus_ter`). Berekend naast chrF++ en BLEU. Uitgesloten van samengestelde score — correleert met chrF++ voor de meeste toepassingen, zodat het opnemen van beide oppervlaktegelijkenis dubbel zou tellen. |
| `length_ratio` | Lengteratio | ✅ Geïmplementeerd | 0–∞ (1,0 is ideaal) | Beide | `len(predicted) / len(reference)` in tekens. Detecteert afkapping (<0,5) en opblazing/hallucinatie (>2,0). Gemiddeld over invoeren op corpusniveau. |

### 2.2 Structurele metrieken

Structurele metrieken valideren de linguïstische welgevormdheid van de vertaling. Ze vereisen taalspecifieke hulpmiddelen (FST-analysatoren, morfologische parsers) en zijn de sterkste signalen voor morfologisch rijke talen.

| ID | Metriek | Status | Schaal | Niveau | Implementatie |
|----|---------|--------|--------|--------|---------------|
| `fst_acceptance_rate` | FST-acceptatie | ✅ Geïmplementeerd | 0,0–1,0 | Beide | Aandeel uitvoerwoorden dat wordt geaccepteerd door een eindige-toestandstransducer (GiellaLT). Een woord is "geldig" als de FST ten minste één morfologische analyse retourneert. Beschikbaar voor elke taal met een GiellaLT `.hfstol`-analysator. |
| `morphological_accuracy` | Morfologische nauwkeurigheid | 🔲 Gepland | 0,0–1,0 | Beide | Een woord kan FST-geldig zijn maar de verkeerde verbuiging hebben (juiste stam, verkeerd achtervoegsel). Deze metriek vergelijkt de FST-analyse van het voorspelde woord met de verwachte morfologische kenmerken. Vereist morfologische annotaties per invoer in het corpus. |
| `orthographic_accuracy` | Orthografische nauwkeurigheid | 🔲 Gepland | 0,0–1,0 | Beide | Valideert schriftspecifieke correctheid: SRO-macron/circumflexgebruik voor Cree, diacritische tekens voor Inuktitut, klinkerlengtemarkeringen voor Ojibwe. Regelsets per taal. |

> **Waarom structurele metrieken van belang zijn.** Meta's OMT-1600 — het grootste ooit gepubliceerde MT-systeem (1.600 talen) — evalueert met ChrF++, xCOMET, MetricX en BLASER 3. Geen van deze valideert morfologische correctheid. ChrF++ meet karakter-n-gram-overlap: het beloont tekenreeksen die eruitzien als de doeltaal. Voor polysynthetische talen betekent dit dat een morfologisch ongeldig woord dat veel tekens deelt met de referentie een hoge score behaalt. Onze FST-acceptatiemetriek is een binaire structurele test: het woord is ofwel een geldige vorm in de taal, of het is dat niet. Geen enkel ander MT-evaluatieraamwerk biedt dit op schaal.

### 2.3 Semantische metrieken

Semantische metrieken meten betekenisbehoud met behulp van inbeddingen of aangeleerde modellen. Ze detecteren vertalingen die oppervlakkig verschillen maar betekenisovereenkomstig zijn, en markeren vertalingen die oppervlakkig gelijkend zijn maar semantisch onjuist.

| ID | Metriek | Status | Schaal | Niveau | Implementatie |
|----|---------|--------|--------|--------|---------------|
| `semantic_score` | Semantische gelijkenis | ⚡ Gedeeltelijk | 0,0–1,0 | Beide | CRK: verdictgewogen score van de `CrkSemanticMetric` van de CRK-evalstandaard (in `eval_standards/crk/`, proxy). Universeel: cosinusgelijkenis van zinsinbeddingen (bron + voorspelling vs. bron + referentie). Model nog te bepalen — moet talen met weinig bronnen ondersteunen, wat de meeste Engelstalige inbeddingsmodellen uitsluit. |
| `comet_score` | COMET | ✅ Geïmplementeerd | ~0,0–1,0 | Beide | Aangeleerde MT-evaluatiemetriek (Unbabel). Getraind op menselijke kwaliteitsoordelen. **Uitgesloten van samengestelde score** — trainingsdata is bevooroordeeld ten gunste van Europese talen met veel bronnen; scores voor talen met weinig bronnen zijn onbetrouwbaar. Berekend wanneer `unbabel-comet` is geïnstalleerd. Gerapporteerd met een waarschuwingsvlag voor talen met weinig bronnen. Voor 35 Afrikaanse talen selecteert het harnas automatisch AfriCOMET (`masakhane/africomet-mtl`) via `resolve_comet_model()`, dat een betere correlatie met menselijke oordelen heeft voor die talen. |

> **Waarom COMET is uitgesloten van de samengestelde score.** COMET is getraind op WMT-menselijke evaluatiedata, die overwegend bestaat uit Europese taalparen met veel bronnen. Wanneer toegepast op Plains Cree of andere talen met weinig bronnen, heeft het model geen blootstelling gehad aan die talen in zijn interne representaties — het extrapoleert vanuit talen met fundamenteel andere morfologische systemen. De scores zijn nog steeds richtinggevend nuttig (hogere COMET ≈ vloeiender klinkende uitvoer in het algemeen), maar de absolute waarden zijn niet gekalibreerd. We rapporteren COMET voor transparantie, maar laten het de samengestelde score niet beïnvloeden totdat we het kunnen valideren aan de hand van menselijke oordelen voor elke doeltaal.

> **AfriCOMET voor Afrikaanse talen.** Elke taalkaart heeft een `metricModelSupport`-veld (zie taalkaartspecificatie §9) dat aangeeft welke gespecialiseerde COMET-modellen zijn getraind voor die taal. Voor 35 Afrikaanse talen (yor, hau, ibo, amh, swa, enz.) declareert de kaart AfriCOMET (`masakhane/africomet-mtl`) — een COMET-model dat is verfijnd op menselijke oordelen over Afrikaanse MT door de Masakhane-gemeenschap. Het harnas selecteert automatisch het aanbevolen model via `resolve_comet_model()` dat taalkaarten leest, maar dit kan worden overschreven met `--comet-model`. Het toevoegen van nieuwe taal→model-koppelingen gebeurt door de taalkaart te verrijken (niet door Python-code te bewerken).

### 2.4 Gedragsmetrieken

Gedragsmetrieken detecteren specifieke faalpatronen in vertaaluitvoer. Ze meten kwaliteit niet direct — ze detecteren problemen.

| ID | Metriek | Status | Schaal | Niveau | Implementatie |
|----|---------|--------|--------|--------|---------------|
| `code_switching_rate` | Code-switching-percentage | ✅ Geïmplementeerd | 0,0–1,0 (lager is beter) | Beide | Aandeel uitvoerwoorden dat in de brontaal staat (doorgaans Engels). Gedetecteerd via Unicode-scriptanalyse en/of een woordenlijst van de brontaal. Zeer veelvoorkomend faalpatroon bij grote taalmodellen: het model voegt Engelse woorden in wanneer het het equivalent in de doeltaal niet kent. |
| `hallucination_rate` | Hallucinatiepercentage | ✅ Geïmplementeerd | 0,0–1,0 (lager is beter) | Beide | Aandeel uitvoerinhoud zonder overeenkomstige broninhoud. Gedetecteerd via woorduitlijning of taaloverschrijdende inbeddingsoverlap. Detecteert het genereren van aannemelijk klinkende maar verzonnen vertalingen door het model. |
| `terminology_adherence` | Terminologienaleving | ✅ Geïmplementeerd | 0,0–1,0 | Beide | Voor begeleide methoden: aandeel voorgeschreven terminologietermen dat in de uitvoer voorkomt. Vereist coachingwoordenboekdata. Meet of het model door experts aangeleverd vocabulaire respecteert. |
| `consistency_score` | Consistentie over invoeren | 🔲 Gepland | 0,0–1,0 | Alleen corpus | Vertaalt het model dezelfde bronterm op dezelfde manier over invoeren heen? Lage consistentie suggereert dat het model raadt in plaats van aangeleerde patronen toe te passen. Vereist herhaalde termen over corpusinvoeren. |

### 2.5 Nalevingsmetrieken

Nalevingsmetrieken valideren dat vertalingen structurele integriteit bewaren — plaatshouders, opmaak en typografische conventies. Het zijn kwaliteitspoortcontroles, geen kwaliteitsscores.

| ID | Metriek | Status | Schaal | Niveau | Implementatie |
|----|---------|--------|--------|--------|---------------|
| `compliance_index` | Dubbele-doorgang-naleving | ✅ Geïmplementeerd | 0,0–1,0 | Beide | Gewogen samengestelde score: 60% variabele integriteit (zijn `{placeholder}`-variabelen bewaard?) + 20% aanhalingstekennaleving (correcte aanhalingstekens per taalkaart) + 20% hoofdletternaleving (geen Latijns letterlek voor talen zonder hoofdletteronderscheid). Berekend op zowel ruwe als nabewerkte uitvoer. Via `DoublePassCompliancePlugin`. |
| `repair_effectiveness` | Hersteleffectiviteit | ✅ Geïmplementeerd | 0,0–1,0 | Corpus | Aandeel nalevingsschendingen dat automatisch is hersteld door hooks na vertaling. Meet hoeveel de kwaliteitspoort de ruwe uitvoer heeft verbeterd. |

> **Waarom naleving niet in de samengestelde score zit.** Nalevingsmetrieken meten structuurbehoud (plaatshouders, aanhalingstekens), niet vertaalkwaliteit. Een vertaling kan linguïstisch perfect zijn maar toch de nalevingscontrole niet doorstaan omdat een `{name}`-variabele is weggevallen. Dit zijn kwaliteitspoorten — ze blokkeren slechte uitvoer van verzending, maar ze rangschikken vertaalkwaliteit niet.

---

## 3. Metriekstatustiers

Elke metriek in §2 valt in een van vier implementatietiers:

| Tier | Betekenis | Gedrag run card |
|------|-----------|-----------------|
| **✅ Geïmplementeerd** | Code bestaat, getest, produceert vandaag waarden in run cards | Numerieke waarde in run card |
| **⚡ Gedeeltelijk** | Taalspecifieke proxy bestaat (bijv. CRK) maar universele implementatie is in behandeling | Numerieke waarde wanneer proxy van toepassing is, `null` anders |
| **🔲 Gepland** | Gespecificeerd maar nog niet geïmplementeerd | `null` in run card (veld aanwezig, waarde afwezig) |
| **💡 Voorgesteld** | Onder bespreking, nog niet gespecificeerd | Niet in run card |

Een metriek gaat van Gepland → Gedeeltelijk wanneer:
1. Een taalspecifieke implementatie is samengevoegd en getest
2. Ze waarden produceert voor ten minste één taalpaar
3. De universele implementatie in behandeling blijft (gedocumenteerd in deze specificatie)

Een metriek gaat van Gedeeltelijk → Geïmplementeerd wanneer:
1. Een taalonafhankelijke implementatie is samengevoegd en getest
2. Ze waarden produceert voor elk taalpaar zonder taalspecifieke plugins
3. Dit document is bijgewerkt om de ✅-status te weerspiegelen

Een metriek gaat van Gepland → Geïmplementeerd wanneer:
1. De implementatie is samengevoegd en getest
2. Ze is gevalideerd op ten minste één echte evaluatierun
3. Dit document is bijgewerkt met de implementatiedetails

Een metriek gaat van Voorgesteld → Gepland wanneer:
1. De definitie, schaal en berekeningsmethode zijn overeengekomen
2. Ze aan dit document is toegevoegd met een `🔲 Planned`-status
3. Een nulplaatshouder is toegevoegd aan het run card-schema

---

## 4. Samengestelde score

### 4.1 Formule

De samengestelde score is een gewogen gemiddelde van alle *beschikbare* metrieken, hernormaliseerd zodat de gewichten van beschikbare metrieken optellen tot 1,0:

```
composite = Σ (weight_i × value_i)    for all available metrics
             ─────────────────────
             Σ weight_i               (re-normalization denominator)
```

Een metriek is "beschikbaar" als de waarde in de run card een getal is (niet `null`). Wanneer een metriek niet beschikbaar is — omdat de taal geen FST heeft, of omdat een metriek nog niet is geïmplementeerd — wordt het gewicht proportioneel herverdeeld over de overige metrieken.

**Dit betekent dat de samengestelde score altijd vergelijkbaar is binnen een run:** ze gebruikt welke metrieken ook beschikbaar zijn en normaliseert dienovereenkomstig. Vergelijking tussen runs is geldig wanneer runs dezelfde set beschikbare metrieken gebruiken.

> [!WARNING]
> **Vergelijkbaarheid tussen runs.** Bij het vergelijken van runs met verschillende metriekbeschikbaarheid (bijv. één run heeft FST-scores, een andere niet), zijn de samengestelde scores **niet direct vergelijkbaar**. Een samengestelde score van 0,72 berekend uit 5 metrieken bevat meer informatie dan een samengestelde score van 0,72 berekend uit 2 metrieken. Het leaderboard toont een waarschuwing wanneer de metriekdekking verschilt tussen vergeleken runs. Gebruik voor rigoureuze vergelijking gepaarde bootstrap-significantietests (§8.2) op uitsluitend gedeelde metrieken.

### 4.2 Invoernormalisatie

Voordat metrieken de samengestelde formule ingaan, moeten ze allemaal op een **0,0–1,0-schaal** staan waarbij 1,0 = perfect:

| Metriek | Oorspronkelijke schaal | Normalisatie |
|---------|----------------------|--------------|
| `exact_match_rate` | 0,0–1,0 | Geen (al genormaliseerd) |
| `equivalent_match_rate` | 0,0–1,0 | Geen |
| `fst_acceptance_rate` | 0,0–1,0 | Geen |
| `morphological_accuracy` | 0,0–1,0 | Geen |
| `chrf_plus_plus` | 0–100 | **Delen door 100** |
| `semantic_score` | 0,0–1,0 | Geen |
| `code_switching_rate` | 0,0–1,0 (lager = beter) | **`1.0 - value`** (inverteren: 0% code-switching = 1,0) |
| `hallucination_rate` | 0,0–1,0 (lager = beter) | **`1.0 - value`** (inverteren) |
| `terminology_adherence` | 0,0–1,0 | Geen |

Metrieken die zijn uitgesloten van de samengestelde score (`bleu`, `comet_score`, `ter`, `length_ratio`, `consistency_score`) worden voor dit doel niet genormaliseerd.

### 4.3 Gewichtstabellen

#### Profiel A: Talen MET FST-dekking

Voor talen die beschikken over een GiellaLT eindige-toestandstransducer. Structurele metrieken dragen 40% van de samengestelde score (FST 0,25 + morfologische nauwkeurigheid 0,15), wat de primaire rol van morfologische correctheid voor polysynthetische/agglutinerende talen weerspiegelt.

| Metriek | Doelgewicht | Motivering |
|---------|------------|------------|
| `fst_acceptance_rate` | **0,25** | Hoogste gewicht. Als de FST een woord afwijst, is het geen geldige vorm in de taal — ongeacht wat andere metrieken aangeven. Binair, structureel onderbouwd. |
| `morphological_accuracy` | **0,15** | Een woord kan FST-geldig zijn maar morfologisch onjuist (juiste stam, verkeerde verbuiging). Samen met FST dragen structurele metrieken 40%. |
| `chrf_plus_plus` | **0,15** | Karakter-n-gram-overlap: de beste oppervlakteproxy voor polysynthetische talen. Gaat beter om met agglutinerende morfologie dan metrieken op woordniveau. |
| `semantic_score` | **0,15** | Betekenisbehoud wanneer de oppervlaktevorm afwijkt. Detecteert semantisch onjuiste vertalingen die structurele controles doorstaan. |
| `equivalent_match_rate` | **0,10** | Beloont aanvaardbare varianten, niet alleen de ene referentievertaling. Belangrijk voor talen met flexibele woordvolgorde. |
| `code_switching_rate` | **0,05** | Bestraft lek van de brontaal. Geïnverteerd: 0% code-switching = 1,0. |
| `terminology_adherence` | **0,05** | Beloont begeleide methoden die voorgeschreven vocabulaire respecteren. Alleen actief wanneer coachingdata aanwezig is. |
| `hallucination_rate` | **0,05** | Bestraft verzonnen inhoud. Geïnverteerd: 0% hallucinatie = 1,0. |
| `exact_match_rate` | **0,05** | Laagste gewicht. Te strikt voor polysynthetische talen — er bestaan meerdere correcte vertalingen. Behouden als plafondcontrole. |

> **Totaal: 1,00.** Wanneer metrieken niet beschikbaar zijn, worden hun gewichten proportioneel herverdeeld over beschikbare metrieken. Momenteel is `morphological_accuracy` (gewicht 0,15) de enige Profiel A-metriek die nog niet wordt berekend — ze vereist goudstandaard morfologische annotaties per invoer. Met deze metriek afwezig worden de overige 8 metrieken (totaalgewicht 0,85) elk geschaald met 1/0,85 ≈ 1,176. Bijvoorbeeld:
> - FST: 0,25/0,85 = 0,294
> - chrF++: 0,15/0,85 = 0,176
> - semantisch: 0,15/0,85 = 0,176

#### Profiel B: Talen ZONDER FST-dekking

Voor talen zonder morfologische validatietools. Semantische en oppervlaktemetrieken dragen een gelijk gewicht.

| Metriek | Doelgewicht | Motivering |
|---------|------------|------------|
| `semantic_score` | **0,25** | Zonder structurele validatie is betekenisbehoud het sterkste beschikbare signaal. |
| `chrf_plus_plus` | **0,25** | Zonder FST wordt overlap op tekenniveau de primaire oppervlaktecontrole. |
| `equivalent_match_rate` | **0,15** | Variantmatching biedt gestructureerde kwaliteitsbeoordeling zonder morfologische tools. |
| `exact_match_rate` | **0,10** | Zonder FST draagt exacte overeenkomst meer gewicht als de enige proxy voor structurele validatie. |
| `code_switching_rate` | **0,10** | Lek van de brontaal is belangrijker wanneer er geen FST is om slechte uitvoer te detecteren. |
| `terminology_adherence` | **0,05** | Naleving van begeleid vocabulaire. |
| `hallucination_rate` | **0,05** | Detectie van verzonnen inhoud. |
| `orthographic_accuracy` | **0,05** | Schriftspecifieke correctheid vult een deel van de leemte die door de afwezige FST is ontstaan. |

> **Totaal: 1,00.** `orthographic_accuracy` (gewicht 0,05) is gepland maar wordt nog niet berekend. Met deze metriek afwezig worden de overige 7 metrieken (totaalgewicht 0,95) geschaald met 1/0,95 ≈ 1,053 — een verwaarloosbare impact op de samengestelde score.

> **Opmerking over gewichtsontwikkeling.** Deze gewichten zijn voorlopig en zullen worden geijkt naarmate er meer menselijke validatiedata beschikbaar komt. Het langetermijndoel is om gewichten empirisch af te leiden: welke geautomatiseerde metrieken voorspellen menselijke kwaliteitsoordelen het best voor elke taalfamilie?

### 4.4 Een nieuwe metriek toevoegen aan de samengestelde score

Om een nieuwe metriek aan de samengestelde score toe te voegen:

1. **Definieer ze** in §2 met status `🔲 Planned`, inclusief schaal, niveau en berekeningsmethode.
2. **Implementeer ze** als een MetricPlugin (of in `tester.py` voor kernmetrieken).
3. **Voeg een nulplaatshouder toe** in het scores-blok van de run card.
4. **Wijs een doelgewicht toe** in §4.3 door bestaande gewichten naar beneden bij te stellen. Gewichten moeten optellen tot 1,00.
5. **Werk BENCHMARK_SPEC.md §3 bij** als het run card-schema wijzigt.
6. **Werk `scoring.py`** gewichtstabellen bij (de code moet dit document weerspiegelen).
7. **Voer een validatiebenchmark uit** om te bevestigen dat de metriek zinvolle waarden produceert op echte data.
8. **Werk dit document bij** om de status te wijzigen van `🔲` naar `✅`.

---

## 5. Kwaliteitsniveaus

Deze niveaus zijn heuristische labels op geautomatiseerde samengestelde scores. Ze beschrijven wat de scores in de praktijk doorgaans betekenen, op basis van menselijke beoordeling van uitvoer op elk niveau. **Het zijn geen gevalideerde kwaliteitsoordelen** — alleen menselijke beoordeling kan de werkelijke bruikbaarheid bevestigen.

> [!IMPORTANT]
> **Geautomatiseerde niveaus zijn voorlopig.** Deze labels zijn nominaties voor beoordeling, geen kwaliteitsverklaringen. Een methode die "Inzetbaar" bereikt op geautomatiseerde metrieken is een kandidaat voor gemeenschapsevaluatie — niet een product om te verzenden. Alleen menselijke beoordeling door tweetalige sprekers kan de werkelijke bruikbaarheid bevestigen (zie [BENCHMARK_SPEC §7](/docs/specifications/benchmark#7-human-validation)). Geen enkele methode kan aanspraak maken op Inzetbaar of hoger zonder gemeenschapsbeoordeling die bevestigt dat sprekers de uitvoer bruikbaar vinden. Niveaudrempels kunnen per taal verschillen naarmate er meer menselijke validatiedata beschikbaar komt.

| Niveau | Samengesteld bereik | Wat een spreker doorgaans ziet |
|--------|--------------------|---------------------------------|
| **Basislijn** | 0,00–0,30 | Ruwe uitvoer van een groot taalmodel zonder taalspecifieke ondersteuning. Morfologie is grotendeels gehallusineerd. |
| **Opkomend** | 0,30–0,50 | Enkele correcte patronen verschijnen. Coaching helpt, maar de uitvoer is niet betrouwbaar. |
| **Functioneel** | 0,50–0,70 | Uitvoer is herkenbaar voor een spreker. Grote grammaticale categorieën zijn doorgaans correct. Frequente morfologische fouten. |
| **Inzetbaar** | 0,70–0,85 | Geschikt voor conceptvertaling met menselijke beoordeling. De meeste morfologie is correct. |
| **Vloeiend** | 0,85–1,00 | Benadert competente menselijke vertaling. Fouten zijn zeldzaam en gering. |

Deze niveaus zijn voorlopig. Ze zullen worden geijkt naarmate er meer menselijke validatiedata beschikbaar komt en we leren waar de drempel "een spreker vindt dit nuttig" werkelijk ligt voor elke taal. Geen enkele methode kan aanspraak maken op **Inzetbaar** of hoger zonder gemeenschapsbeoordeling die bevestigt dat tweetalige sprekers de uitvoer bruikbaar vinden.

### 5.1 Niveaudrempels (machineleesbaar)

Voor code-implementaties zijn de drempels (van boven naar beneden geëvalueerd, eerste overeenkomst wint):

```
composite >= 0.85  →  "fluent"
composite >= 0.70  →  "deployable"
composite >= 0.50  →  "functional"
composite >= 0.30  →  "emerging"
composite >= 0.00  →  "baseline"
composite is null  →  "unscored"
```

---

## 6. Kostenmetrieken

Kostenmetrieken meten de financiële efficiëntie van een vertaalmethode. Ze worden apart van kwaliteit gerapporteerd — kosten beïnvloeden de samengestelde score niet (behalve in de kostengewogen secundaire rangschikking).

### 6.1 Tokenmetrieken

| ID | Metriek | Berekening |
|----|---------|------------|
| `prompt_tokens` | Totaal invoertokens | Som van `usage.prompt_tokens` over alle API-aanroepen |
| `completion_tokens` | Totaal uitvoertokens | Som van `usage.completion_tokens` |
| `reasoning_tokens` | Chain-of-thought-tokens | Som van `usage.completion_tokens_details.reasoning_tokens` (0 voor de meeste modellen) |
| `cached_tokens` | Door provider gecachede tokens | Som van `usage.prompt_tokens_details.cached_tokens` |
| `total_tokens` | Totaal verbruikte tokens | `prompt_tokens + completion_tokens` |
| `tokens_per_entry` | Gemiddeld aantal tokens per vertaling | ✅ `total_tokens / entry_count` |

### 6.2 Kostenmetrieken

| ID | Metriek | Berekening | Toepassing |
|----|---------|------------|------------|
| `total_cost_usd` | Totale runkosten | Door provider gerapporteerde prijzen × tokenaantallen | "Hoeveel heeft deze benchmark gekost?" |
| `cost_per_entry_usd` | Kosten per corpusinvoer | `total_cost_usd / entry_count` | Methoden vergelijken op hetzelfde corpus |
| `cost_per_1k_tokens` | Kosten per 1.000 tokens | ✅ `total_cost_usd / total_tokens × 1000` | Universele LLM-efficiëntie — vergelijkbaar over corpora heen |
| `cost_per_source_char` | Kosten per bronteken | `total_cost_usd / total_source_chars` | Vergelijkbaar over talen heen met verschillende tokenisatie |

> **Waarom meerdere kostenmetrieken?** Een "invoer" varieert in lengte — een uitdrukking van 3 woorden kost minder dan een alinea. `cost_per_entry_usd` is nuttig voor het vergelijken van methoden op *hetzelfde* corpus (dezelfde invoeren = dezelfde lengten = eerlijke vergelijking). `cost_per_1k_tokens` is de standaard LLM-efficiëntiemetriek, vergelijkbaar *over* corpora heen. `cost_per_source_char` normaliseert voor tokenisatieverschillen — dezelfde zin kan in een verschillend aantal tokens worden omgezet afhankelijk van het vocabulaire van het model.

### 6.3 Kostengewogen score

Voor methoden die gebruikmaken van betaalde API's berekenen we een secundaire rangschikking:

```
cost_adjusted = composite / log2(1 + cost_per_entry_usd × 1000)
```

Dit beloont methoden die goede scores efficiënt behalen. Het gebruikt `cost_per_entry_usd` (niet per token) omdat de kostengewogen score altijd wordt berekend binnen één enkele benchmark (hetzelfde corpus), waardoor vergelijking per invoer eerlijk is.

De kostengewogen score is een **secundaire rangschikking** — het primaire leaderboard rangschikt op samengestelde score. Het beantwoordt een andere vraag: "welke methode levert de beste resultaten bij een gegeven budget?"

---

## 7. Snelheidsmetrieken

Snelheidsmetrieken meten de latentie en doorvoer van een vertaalmethode. Net als kosten beïnvloeden snelheid de samengestelde score niet.

| ID | Metriek | Berekening | Niveau |
|----|---------|------------|--------|
| `elapsed_seconds` | Wandkloktijd van de run | `time_end - time_start` | Run |
| `avg_latency_seconds` | Gemiddelde latentie per invoer | `Σ latency_s / n_entries` | Corpus |
| `median_latency_seconds` | Mediane latentie per invoer | 50e percentiel van `latency_s` | Corpus |
| `p95_latency_seconds` | 95e-percentiellatentie | 95e percentiel van `latency_s` | Corpus |
| `tokens_per_second` | Doorvoer | `total_tokens / elapsed_seconds` | Run |
| `entries_per_minute` | Vertaalsnelheid | `entry_count / (elapsed_seconds / 60)` | Run |

---

## 8. Betrouwbaarheid en significantie

### 8.1 Bootstrap-betrouwbaarheidsintervallen

Alle sleutelmetrieken ondersteunen bootstrap-betrouwbaarheidsintervallen (percentielmethode, n=1000 hersteekproeven, α=0,05):

| Metriek | BI gerapporteerd |
|---------|-----------------|
| `chrf_plus_plus` | ✅ `chrf_ci_lower`, `chrf_ci_upper` |
| `exact_match_rate` | ✅ `exact_match_ci_lower`, `exact_match_ci_upper` |
| `fst_acceptance_rate` | ✅ `fst_ci_lower`, `fst_ci_upper` (alleen berekend wanneer FST-data beschikbaar is) |
| `comet_score` | ✅ `comet_ci_lower`, `comet_ci_upper` (bootstrap op basis van gecachede scores per invoer — geen redundante neurale inferentie) |
| `composite` | ✅ `composite_ci_lower`, `composite_ci_upper` (berekend wanneer chrF++ en exact_match beschikbaar zijn) |
| BI per niveau | ✅ `confidence_intervals_by_tier` — chrF++- en exact_match-BI's per moeilijkheidsgraad (Tier 1-5) |

### 8.2 Gepaarde bootstrap-significantietests

Voor het vergelijken van twee methoden berekent het harnas gepaarde bootstrap-hersteekproeftests:

```
H₀: The two methods perform equally on this corpus.
H₁: One method is significantly better.
```

Als de p-waarde < 0,05 en het betrouwbaarheidsinterval van het verschil nul uitsluit, is het verschil statistisch significant op het 95%-niveau.

---

## 9. Run card-scoresschema

Dit gedeelte definieert de hiërarchische structuur van het `scores`-blok in een run card. Dit schema is afgeleid van de metrieken die zijn gedefinieerd in §2–§7 en moet gesynchroniseerd worden gehouden.

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

> **Schemageschiedenis.** Eerdere conceptversies van de specificatie stelden afzonderlijke `cost`-, `speed`- en `tokens`-blokken voor. Deze zijn samengevoegd tot respectievelijk `scores` en `totals` voor de eenvoud. Snelheidsmetrieken (`tokens_per_second`, `entries_per_minute`, latenties) bevinden zich in `scores`; tokenaantallen en kostencijfers bevinden zich in `totals`.

### 9.1 Schema–databasekoppeling

De run card JSON wordt in zijn geheel opgeslagen als een `jsonb`-kolom in Supabase. Sleutelmetrieken worden ook gedenormaliseerd in kolommen op het hoogste niveau voor sorteer-/filterprestaties:

| Run card-veld | Supabase-kolom | Type | Index |
|--------------|----------------|------|-------|
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
| *(volledige kaart)* | `run_card` | `jsonb` | — |

Wanneer nieuwe metrieken worden geïmplementeerd, dient de bijbehorende kolom te worden toegevoegd via een genummerde migratie in `arena/migrations/`.

---

## 10. Code–specificatiesynchronisatie

### 10.1 Gezaghebbende bron

Dit document (`arena/website/docs/specifications/scoring.md`) is de gezaghebbende bron voor:
- Metriekdefinities (§2)
- Samengestelde gewichtstabellen (§4.3)
- Kwaliteitsniveaudrempels (§5.1)
- Kostenmetriekformules (§6.2)
- Run card-scoresschema (§9)

### 10.2 Codespiegeling

Het bestand `arena/mt_eval_harness/scoring.py` spiegelt de gewichtstabellen en niveaudrempels uit dit document. Het is de **code-implementatie** van §4.3 en §5.1. Wanneer dit document wordt bijgewerkt:

1. Werk `scoring.py` bij om overeen te komen
2. Voer `pytest tests/test_scoring_ssot.py` uit om uitlijning te valideren
3. Werk FAQ en websitedocumentatie bij die de gewichten samenvatten

### 10.3 Documenten die naar deze specificatie verwijzen

| Document | Waarnaar het verwijst | Hoe gesynchroniseerd te houden |
|----------|----------------------|-------------------------------|
| `arena/website/docs/specifications/benchmark-spec.md` §4–§5 | Samengestelde formule, gewichtstabellen, niveaudrempels | Kruisverwijzing naar dit document; tabellen niet dupliceren |
| `website/docs/getting-started/faq.md` | Vereenvoudigde gewichtssamenvatting | Moet overeenkomen met §4.3; terugkoppelen naar dit document |
| `arena/website/docs/how-it-works.md` | Inzetbaar-drempel | Moet overeenkomen met §5 |
| `publish.py` via `scoring.py` | Gewichtsdicts + niveaufunctie | Geautomatiseerde test valideert overeenkomst |

---

## Bijlage A: Metrieken NIET in de samengestelde score (en waarom)

| Metriek | Reden voor uitsluiting |
|---------|------------------------|
| **BLEU** | Scoring op woordniveau bestraft morfologische variatie in polysynthetische talen. Een kleine verbuigingsverschil (correcte betekenis, iets ander achtervoegsel) telt als een volledige misser. chrF++ gaat hier beter mee om op tekenniveau. |
| **COMET** | Getraind op WMT-data (Europese taalparen met veel bronnen). Scores voor talen met weinig bronnen zijn onbetrouwbaar — het model extrapoleert vanuit talen met andere morfologische systemen. Gerapporteerd voor transparantie, niet voor scoring. |
| **TER** | Bewerkingsafstand correleert met chrF++ voor de meeste toepassingen. Het opnemen van beide zou oppervlaktegelijkenis dubbel tellen. TER wordt gerapporteerd ter referentie. |
| **Lengteratio** | Een diagnostisch hulpmiddel, geen kwaliteitssignaal. Een ratio van 1,02 en een ratio van 0,98 zijn beide prima. Alleen extreme waarden duiden op problemen. |
| **Consistentiescore** | Alleen op corpusniveau — geen waarde per invoer om te aggregeren. Bovendien is enige inconsistentie legitiem (hetzelfde Engelse woord → verschillende vertalingen in de doeltaal afhankelijk van de context). |
| **Nalevingsindex** | Kwaliteitspoort, geen kwaliteitssignaal. Meet structuurbehoud (plaatshouders, aanhalingstekens), niet vertaalnauwkeurigheid. |

## Bijlage B: LYSS — Taalspecifieke metriekimplementaties

Het **LYSS**-raamwerk (Linguistically-informed Yield & Structural Scoring) biedt taalspecifieke metrieken die verder gaan dan oppervlakkige tekenreeksvergelijking. LYSS heeft drie kerncomponenten:

- **LYSS-fst** — Morfologische geldigheid (`fst_acceptance_rate`): Is elk woord een geldige vorm in de doeltaal?
- **LYSS-eq** — Linguïstische equivalentie (`equivalent_match_rate`): Is de uitvoer een aanvaardbare variant van de referentie?
- **LYSS-sem** — Semantische validatie (`semantic_score`): Behoudt de uitvoer de bronbetekenis?

> **Validatiestatus: 🔶 Technische heuristiek.** LYSS-metrieken zijn NIET gevalideerd aan de hand van menselijke kwaliteitsoordelen. Ze zijn ontworpen op basis van linguïstische principes (FST's, woordenboeken, grammaticaregels opgesteld door taalkundigen van UAlberta ALTLab), maar de correlatie tussen LYSS-scores en werkelijke vertaalkwaliteit is niet gemeten. Zie het [Sprekervalidatieprotocol](/docs/specifications/speaker-validation) voor de vereiste validatie-experimenten.

| Taal | Plugin | Locatie | LYSS-component | Metrieksleutel | Opmerkingen |
|------|--------|---------|----------------|----------------|-------------|
| CRK (Plains Cree) | `CrkLinterMetric` | `eval_standards/crk/metrics.py` | **LYSS-eq** | `equivalent_match_rate` | Deterministische variantklasseregels: woordvolgorde, orthografisch, optioneel partikel, lemmasynoniem, progressieve ambiguïteit, inclusief/exclusief. Produceert per invoer `lint_verdict` (EXACT/EQUIVALENT/MISS/NO_OUTPUT). |
| CRK | `CrkSemanticMetric` | `eval_standards/crk/metrics.py` | **LYSS-sem** | `semantic_score` | Deterministisch: FST-lemma-extractie + woordenboekglossen + spaCy inhoudswoordoverlap. Produceert verdicts (EXACT_MATCH/VALID/GRAMMAR_ISSUES/PARTIAL/INCOMPLETE/WRONG/NO_OUTPUT). |
| GiellaLT-talen | `GiellaLTFSTMetric` | `plugins/giellalt_fst.py` | **LYSS-fst** | `fst_acceptance_rate` | Generiek: werkt voor CRK, SME, SMA, SMJ, SMN, SMS, FIN, NOB, IKU — elke taal met een `.hfstol`-analysator. |

> **Architectuurnotitie (juni 2026).** Taalspecifieke LYSS-metrieken worden nu gedeclareerd op de taalkaart onder `evalMetrics` en geladen vanuit `eval_standards/<lang>/` door `plugin_discovery.py`. Het zijn **evaluatiestandaarden** (scheidsrechter), geen methode-pluginmetrieken (deelnemer). Dit betekent dat elke vertaalmethode gericht op CRK automatisch wordt gescoord door LYSS — er is geen methodespecifieke configuratie nodig. `CrkFSTMetric` is verwijderd; de functionaliteit ervan wordt volledig gedekt door de generieke `GiellaLTFSTMetric`.

## Bijlage C: Metrieken in overweging

Dit zijn ideeën die worden geëvalueerd maar nog niet voldoende zijn gespecificeerd voor §2:

| Idee | Wat het zou meten | Belemmeringen |
|------|------------------|---------------|
| Vloeiendheid (LM-perplexiteit) | Is de uitvoer goed geformuleerde proza in de doeltaal? | Vereist een doeltaal-LM. Er bestaan geen goede modellen voor de meeste talen met weinig bronnen. |
| Registerovereenkomst | Komt de vertaling overeen met het verwachte formaliteitsniveau? | Vereist sociolinguïstische classificatoren. Onderzoeksprobleem. |
| Culturele gepastheid | Worden culturele verwijzingen correct behandeld? | Kan niet worden geautomatiseerd — vereist inherent menselijke beoordeling. |
| Discourssamenhang | Vormen opeenvolgende vertalingen een samenhangend geheel? | Vereist evaluatie op documentniveau, niet op zinsniveau. |

---

## Referenties

Academische publicaties, tools en taalbronnen waarnaar in deze specificatie wordt verwezen.

### Oppervlaktemetrieken

1. Popović, M. (2017). "chrF++: words helping character n-grams." *Proceedings of the Second Conference on Machine Translation (WMT 2017)*, pp. 612–618. Kopenhagen, Denemarken.

2. Papineni, K., Roukos, S., Ward, T., & Zhu, W.-J. (2002). "BLEU: a method for automatic evaluation of machine translation." *Proceedings of the 40th Annual Meeting of the Association for Computational Linguistics (ACL 2002)*, pp. 311–318. Philadelphia, PA.

3. Post, M. (2018). "A Call for Clarity in Reporting BLEU Scores." *Proceedings of the Third Conference on Machine Translation (WMT 2018)*, pp. 186–191. België, Brussel. Referentie-implementatie: [sacrebleu](https://github.com/mjpost/sacrebleu).

4. Snover, M., Dorr, B., Schwartz, R., Micciulla, L., & Makhoul, J. (2006). "A Study of Translation Edit Rate with Targeted Human Annotation." *Proceedings of the 7th Conference of the Association for Machine Translation in the Americas (AMTA 2006)*, pp. 223–231. Cambridge, MA.

### Neurale metrieken

5. Rei, R., Stewart, C., Farinha, A. C., & Lavie, A. (2020). "COMET: A Neural Framework for MT Evaluation." *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP 2020)*, pp. 2685–2702. Online.

6. Juraska, J., Finkelstein, M., Deutsch, D., Siddhant, A., Miber, D., & Markl, A. (2023). "MetricX-23: The Google Submission to the WMT 2023 Metrics Shared Task." *Proceedings of the Eighth Conference on Machine Translation (WMT 2023)*. Singapore.

7. Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2020). "BERTScore: Evaluating Text Generation with BERT." *Proceedings of the Eighth International Conference on Learning Representations (ICLR 2020)*. Addis Abeba, Ethiopië.

8. Sellam, T., Das, D., & Parikh, A. (2020). "BLEURT: Learning Robust Metrics for Text Generation." *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020)*, pp. 7881–7892. Online.

### Morfologische en linguïstische tools

9. Lindén, K., Silfverberg, M., Axelson, E., Hardwick, S., & Pirinen, T. (2011). "HFST—Framework for Compiling and Applying Morphologies." *Systems and Frameworks for Computational Morphology (SFCM 2011)*, Communications in Computer and Information Science, vol. 100, pp. 67–85. Springer, Berlijn, Heidelberg.

10. Sánchez-Cartagena, V. M., & Toral, A. (2024). "MorphEval: Automatic Evaluation of Morphological Capabilities of Machine Translation Systems." *Machine Translation*, vol. 38, pp. 1–28.

### Foutclassificatie en diagnostische evaluatie

11. Popović, M. (2011). "Hjerson: An Open Source Tool for Automatic Error Classification of Machine Translation Output." *The Prague Bulletin of Mathematical Linguistics*, no. 96, pp. 59–68.

12. Dreyer, M. & Marcu, D. (2012). "HyTER: Meaning-Equivalent Semantics for Translation Evaluation." *Proceedings of the 2012 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2012)*, pp. 162–171. Montreal, Canada.

13. Reiter, E. & Belz, A. (2009). "An Investigation into the Validity of Some Metrics for Automatically Evaluating Natural Language Generation Systems." *Computational Linguistics*, vol. 35, no. 4, pp. 529–558. (Verwant werk over op kenmerken gebaseerde evaluatiemetrieken, waaronder FUSE.)

### Hallucinatiedetectie

14. Raunak, V., Menezes, A., & Junczys-Dowmunt, M. (2021). "The Curious Case of Hallucinations in Neural Machine Translation." *Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2021)*, pp. 1172–1183. Online.

15. Guerreiro, N. M., Voita, E., & Martins, A. F. T. (2023). "Looking for a Needle in a Haystack: A Comprehensive Study of Hallucinations in Neural Machine Translation." *Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2023)*, pp. 1059–1075. Dubrovnik, Kroatië.

### Cree-taalbronnen

16. Wolfart, H. C. (1973). "Plains Cree: A Grammatical Study." *Transactions of the American Philosophical Society*, vol. 63, no. 5, pp. 1–90.

17. Wolvengrey, A. (2001). *nêhiyawêwin: itwêwina / Cree: Words.* Canadian Plains Research Center, University of Regina.

### Gegevensbeheer

18. First Nations Information Governance Centre. "The First Nations Principles of OCAP®." [https://fnigc.ca/ocap-training/](https://fnigc.ca/ocap-training/). (OCAP® is een geregistreerd handelsmerk van het First Nations Information Governance Centre.)

19. Carroll, S. R., Garba, I., Figueroa-Rodríguez, O. L., Holbrook, J., Lovett, R., Materechera, S., Parsons, M., Raseroka, K., Rodriguez-Lonebear, D., Rowe, R., Sara, R., Walker, J. D., Anderson, J., & Hudson, M. (2020). "The CARE Principles for Indigenous Data Governance." *Data Science Journal*, vol. 19, no. 1, p. 43.