---
sidebar_position: 1
title: "MT-evaluatie"
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
# MT Evaluatie

> **Samenvatting.** Deze pagina definieert de inzendinscriteria voor het leaderboard, scoringsmetrieken (chrF++, FST-acceptatie, exacte overeenkomst, equivalente overeenkomst, semantische score), anti-manipulatiebeleid, verificatieniveaus en de inzendingsworkflow. Methoden die zijn blootgesteld aan evaluatiedata worden gediskwalificeerd.

champollion bevat een raamwerk voor machinevertaalevaluatie, ontworpen voor **reproduceerbare benchmarking** van vertaalmethoden — met name voor talen met weinig bronmateriaal en inheemse talen waarvoor standaard MT-benchmarks ontbreken en kwaliteitsclaims moeilijk te verifiëren zijn.

---

## Het Leaderboard

Het centrale onderdeel is het **[Methode-leaderboard](https://champollion.dev/leaderboard)** — een live, op Supabase gebaseerd scorebord waarop onderzoekers en gemeenschapsleden vertaalmethoden indienen en vergelijken met vingerafdruk-gebaseerde, reproduceerbare evaluatie.

Elke inzending bevat:

- **Vingerafdruk-pipeline** — gekoppeld aan een specifieke Git-commit en configuratiehash, zodat resultaten herleidbaar zijn tot de exacte code die ze heeft gegenereerd
- **Versioned dataset** — inhoudelijk gehasht en voorzien van versienummering; scores zijn alleen vergelijkbaar binnen dezelfde datasetversie
- **Gestandaardiseerde metrieken** — alle scoring wordt berekend door het gedeelde evaluatieraamwerk, waardoor implementatieverschillen worden geëlimineerd
- **Vertrouwensniveaus** — zelf-gebenchmarkt, GDS Verified of Community Validated
- **Kostenbeheer** — API-kosten per inzending, zodat de afweging tussen kosten en kwaliteit transparant is

Het leaderboard volgt momenteel vijf metrieken. Drie werken voor elke taal; twee zijn beschikbaar voor Plains Cree en worden gegeneraliseerd naarmate we uitbreiden:

| Metriek | Type | Wat het meet |
|---------|------|--------------|
| **chrF++** | Karakter-n-gram F-score | Primaire kwaliteitsmetriek — correleert goed met menselijk oordeel, met name voor morfologisch rijke talen |
| **Exact Match** | Aandeel perfecte overeenkomsten | Strikte nauwkeurigheid — hoe vaak is de vertaling exact gelijk aan de gouden standaard? |
| **FST Acceptance** | Morfologische gate-slagingspercentage | Voor methoden met verificatie via eindige-toestandstransducers — welk aandeel van de uitvoer is morfologisch geldig? |
| **Equivalent Match** | Acceptabele variantpercentage | Fractie die overeenkomt met de referentie of een acceptabele variant (woordvolgorde, orthografische conventie). Momenteel CRK; wordt gegeneraliseerd. |
| **Semantic Score** | Semantische getrouwheid | Betekenisbehoud — legt de vertaling de beoogde betekenis vast, ongeacht de oppervlaktevorm? Momenteel CRK; wordt gegeneraliseerd. |

:::info Volledige metriekenset
De [Scoringsspecificatie](/docs/specifications/scoring) definieert de volledige inventaris van 19 metrieken verdeeld over 5 categorieën, de formule voor de samengestelde score, gewichtstabellen en drempelwaarden voor kwaliteitsniveaus.
:::

**[→ Bekijk het leaderboard](https://champollion.dev/leaderboard)**

---

## Beschikbare Datasets

### EDTeKLA Development Set v1

De eerste evaluatiedataset, opgebouwd voor Engels→Plains Cree (SRO)-vertaling. Gemaakt door de [EdTeKLA-onderzoeksgroep](https://spaces.facsci.ualberta.ca/edtekla/) aan de University of Alberta.

| Eigenschap | Waarde |
|------------|--------|
| **ID** | `edtekla-dev-v1` |
| **Taalpaar** | EN → CRK (Plains Cree, SRO-orthografie) |
| **Aantal items** | 404 (`master_corpus.json`: 62 gouden standaard + 342 leerboek); 548 totaal beschikbaar |
| **Licentie** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| **Herkomst** | `gold_standard` (geverifieerd door sprekers), `textbook` (gepubliceerd educatief materiaal) |

### FLORES+ Devtest — Uitsluitend voor Ontwikkelingsgebruik

> [!WARNING]
> **FLORES+ is beschikbaar voor ontwikkeling en foutopsporing, maar wordt NIET gebruikt voor officiële leaderboard-evaluatie.** FLORES+ (oorspronkelijk Meta FLORES-200) is een breed openbaar beschikbare benchmarkdataset waarop frontier-LLM's vrijwel zeker zijn getraind. Scores op basis van FLORES+ weerspiegelen de werkelijke vertaalkwaliteit voor op LLM gebaseerde methoden niet betrouwbaar. Niet-LLM-methoden (FST, regelgebaseerd, fijnafgesteld NMT) zijn minder gevoelig, maar FLORES+-scores worden desondanks niet gepubliceerd op het leaderboard.

FLORES+-fixtures blijven beschikbaar in `test/benchmark/fixtures/` voor pipeline-rooktests, taaloverschrijdende validatie en ontwikkelingsgebruik. Officiële evaluatie maakt gebruik van aangepaste corpora opgebouwd uit door mensen geschreven tekst die niet openbaar beschikbaar is in parallelle vorm.

Zie [Evaluatiedatasets](/docs/leaderboard/datasets) voor het volledige datasetschema, moeilijkheidsgraden en instructies voor het aanmaken van uw eigen dataset.

:::danger TRAIN NIET op evaluatiedata

**Deze datasets zijn uitsluitend bedoeld voor evaluatie.** Methoden die zijn getraind, fijnafgesteld, via few-shot-prompting of anderszins blootgesteld aan evaluatiedata produceren kunstmatig opgeblazen scores en worden **gediskwalificeerd van het leaderboard.**

Dit is geen aanbeveling — het is de belangrijkste regel voor de integriteit van de evaluatie. Gebruik afzonderlijke corpora voor training. Evaluatiesets mogen tijdens de ontwikkeling niet door uw model zijn gezien.

Als u coachingdata of few-shot-voorbeelden gebruikt, moeten deze afkomstig zijn uit **volledig afzonderlijke bronnen**. Twijfelt u? Neem het dan niet op.
:::

:::warning Niet-determinisme van LLM's

LLM-uitvoer is niet-deterministisch. Scores vertegenwoordigen momentopnamen onder specifieke modelversies en API-configuraties. Modelaanbieders kunnen op elk moment gewichten, decoderingsstrategieën of veiligheidsfilters bijwerken, wat scoredrift tussen uitvoeringen kan veroorzaken. Het leaderboard registreert de exacte model-slug en tijdstempel voor elke inzending.
:::

---

## Wat een Goede Methode Kenmerkt

Niet alle methoden zijn gelijkwaardig. Dit is wat rigoureus werk onderscheidt van opgeblazen scores.

### Kenmerken van een sterke methode

- **Strikte scheiding van trainings- en evaluatiedata** — uw methode heeft de evaluatieset nooit gezien tijdens ontwikkeling, afstemming, prompt-engineering of selectie van few-shot-voorbeelden
- **Reproduceerbaar** — iemand anders kan uw repository klonen, het raamwerk uitvoeren en dezelfde scores verkrijgen (binnen de grenzen van LLM-niet-determinisme)
- **Gedocumenteerd** — uw [methodekaart](/docs/specifications/methods) beschrijft wat uw methode doet, welke hulpmiddelen zij gebruikt en wat haar beperkingen zijn
- **Eerlijk over reikwijdte** — als uw methode alleen werkt voor één taalpaar, vermeld dat dan; als zij verslechtert bij bepaalde morfologische patronen, documenteer dat dan
- **Gemeenschapsbewust** — voor inheemse talen respecteert uw methode de datasouvereiniteit. U heeft overleg gepleegd met taalgemeenschappen of uitsluitend openlijk gelicentieerde data gebruikt

### Waarschuwingssignalen (wat leidt tot diskwalificatie)

| Waarschuwingssignaal | Waarom het een probleem is |
|----------------------|---------------------------|
| Trainen op evaluatiedata | Ondermijnt het doel van evaluatie volledig. Opgeblazen scores misleiden iedereen. |
| Selectief rapporteren van resultaten | 10 keer uitvoeren en de beste run indienen zonder de overige te vermelden |
| Niet-gedeclareerde nabewerking | Uitvoer handmatig corrigeren vóór scoring |
| Gecontamineerde coachingdata | Evaluatiesetvoorbeelden gebruiken als few-shot-prompts of woordenboekitems |
| Commerciële gereedheid claimen zonder herkomstvermelding | Als uw methode CC BY-NC-SA-data gebruikt, is zij niet commercieel gereed |

### Verificatieniveaus

Verificatieniveaus beschrijven **wie het resultaat heeft gevalideerd** — los van de kwaliteitsniveaus (Baseline → Fluent) die zijn gedefinieerd in de [Scoringsspecificatie, §5](/docs/specifications/scoring#5-quality-tiers), welke beschrijven wat de geautomatiseerde samengestelde score betekent.

| Niveau | Betekenis | Hoe te verkrijgen |
|--------|-----------|-------------------|
| **Self-benchmarked** | U heeft het raamwerk zelf uitgevoerd en de resultaten ingediend | Open een PR met uw run card |
| **GDS Verified** | De champollion-beheerders hebben uw resultaten gereproduceerd | Dien uw methode in als installeerbare plugin |
| **Community Validated** | De governance-organisatie heeft uitgevoerd tegen de gouden standaard + gemeenschapsreview | Dien de methodecode in bij de governance-organisatie |

---

## Hoe in te Dienen

1. **Bouw uw methode** — zie [Een methode bouwen](/docs/specifications/methods) voor de methode-interface
2. **Voer het raamwerk uit** — zie [Eval Harness](/docs/specifications/harness) voor installatie en gebruik
3. **Genereer een run card** — het raamwerk produceert een JSON-run card met uw scores, vingerafdruk en metadata
4. **Open een PR** — dien uw run card in bij de [eval harness-repository](https://github.com/gamedaysuits/arena)
5. **Verschijn op het leaderboard** — zodra samengevoegd, verschijnen uw resultaten op het [Methode-leaderboard](https://champollion.dev/leaderboard)

---

## Toekomstige Richtingen

- **Uitgebreide modelvergelij­kingsruns** — systematische evaluatie van frontier-modellen (GPT-4o, Claude, Gemini, enz.) voor champollion-talen met behulp van aangepaste evaluatiecorpora (geen openbare benchmarks)
- **Meer taalparen** — Quechua, Inuktitut en andere talen met weinig bronmateriaal naarmate door de gemeenschap geverifieerde datasets beschikbaar komen
- **Dataset-import** — hulpmiddelen om externe evaluatiedatasets (WMT, Tatoeba, enz.) te converteren naar het champollion-evaluatieformaat
- **Geautomatiseerde heruitvoeringen** — detectie van modelversiewijzigingen en heruitvoering van benchmarks om scoredrift bij te houden

---

## Zie Ook

- **[Methode-leaderboard](https://champollion.dev/leaderboard)** — live scores en inzendingen
- **[Eval Harness](/docs/specifications/harness)** — hoe evaluaties uit te voeren
- **[Evaluatiedatasets](/docs/leaderboard/datasets)** — datasetformaat en beschikbare datasets
- **[Een methode bouwen](/docs/specifications/methods)** — de specificatie van de methode-interface
- **[Run Card-specificatie](/docs/specifications/run-card)** — het JSON-schema van de run card
- **[Benchmarkspecificatie](/docs/specifications/benchmark)** — evaluatieprotocol, corpusformaat, souvereiniteit
- **[Scoringsspecificatie](/docs/specifications/scoring)** — SSOT voor metrieken, samengestelde gewichten en kwaliteitsniveaus