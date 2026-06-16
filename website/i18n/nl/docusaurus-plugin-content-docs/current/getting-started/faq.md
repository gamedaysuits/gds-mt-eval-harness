---
sidebar_position: 2
title: "FAQ"
related:
  - label: "How It Works"
    to: /docs/how-it-works
    kind: doc
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Glossary"
    to: https://champollion.dev/glossary
    kind: glossary
    note: "Plain-language definitions for every technical term"
---
# Veelgestelde vragen

> **Samenvatting.** Antwoorden op veelgestelde vragen over de MT Eval Arena — hoe scoring werkt, wat tot diskwalificatie leidt, hoe om te gaan met talen zonder FST's, aanbevelingen voor modellen en parameters, en het indieningsproces.

---

## Scoring & Metrics

### Welke metrics berekent de harness?

De harness berekent vijf metrics voor Plains Cree (de huidige benchmarktaal). Drie zijn taalonafhankelijk en werken voor elke taal; twee zijn momenteel afhankelijk van CRK-specifieke plugins en worden gegeneraliseerd naarmate we uitbreiden naar meer talen.

| Metric | Schaal | Wat het meet | Status |
|--------|-------|-----------------|--------|
| **chrF++** | 0–100 | Overlapping van karakter-n-grammen tussen voorspelde en referentievertaling. Beste oppervlaktemetric voor morfologisch rijke talen. Gebruikt de native scoring van sacrebleu. | ✅ Alle talen |
| **Exact match** | 0.0–1.0 | Aandeel van vermeldingen waarbij de voorspelling na normalisatie exact overeenkomt met de referentie. | ✅ Alle talen |
| **FST acceptance** | 0.0–1.0 | Aandeel van uitvoerwoorden dat wordt geaccepteerd door een finite-state transducer (morfologische analysator). Wordt alleen berekend wanneer een FST-binair bestand is opgegeven. | ✅ Alle talen met FST |
| **Equivalent match** | 0.0–1.0 | Fractie van vermeldingen die overeenkomen met de referentie of een aanvaardbare variant — rekening houdend met woordvolgorde, orthografische conventies en dialectale verschillen. | ⚡ CRK (wordt gegeneraliseerd) |
| **Semantic score** | 0.0–1.0 | Score voor betekenisbehoud — in hoeverre legt de vertaling de beoogde betekenis vast, ongeacht de oppervlaktevorm? | ⚡ CRK (wordt gegeneraliseerd) |

Aanvullende metrics zijn gepland: **morphological accuracy**, **code-switching detection**, **terminology adherence** en **hallucination detection**. Zie [Scoring Specification §2](/docs/specifications/scoring#2-metric-inventory) voor de volledige inventaris van 19 metrics.

### Hoe wordt de composite score berekend?

De composite is een gewogen gemiddelde van beschikbare metrics, genormaliseerd naar een schaal van 0.0–1.0. Gewichten zijn gedefinieerd in twee profielen:

- **Profiel A** (talen met FST): 9 metrics, structurele metrics (FST + morfologische nauwkeurigheid) dragen 40% bij aan het samengestelde gewicht
- **Profiel B** (talen zonder FST): 8 metrics, semantische metrics en chrF++ dragen een gelijk topgewicht

Wanneer een metric niet beschikbaar is, wordt het gewicht ervan proportioneel herverdeeld over de overige metrics. Dit betekent dat benchmarks in een vroeg stadium (met alleen chrF++ en exact match beschikbaar) nog steeds geldige composites opleveren — de effectieve gewichten weerspiegelen simpelweg wat beschikbaar is.

**De volledige gewichtstabellen, normalisatieregels en uitsluitingsrationale staan in [Scoring Specification §4](/docs/specifications/scoring#4-composite-score).** De harness-code weerspiegelt deze tabellen in `mt_eval_harness/scoring.py`. chrF++ wordt genormaliseerd door te delen door 100 vóór weging; code-switching- en hallucinatiepercentages worden omgekeerd (lager = beter).

### Wat zijn kwaliteitsniveaus?

Kwaliteitsniveaus zijn heuristische labels die worden gekoppeld aan bereiken van de composite score. Ze helpen te communiceren wat een score *praktisch betekent*:

| Niveau | Composite-bereik | Interpretatie |
|------|----------------|----------------|
| **Baseline** | 0.00 – 0.30 | Onder bruikbare kwaliteit. Methode vereist aanzienlijke verbetering. |
| **Emerging** | 0.30 – 0.50 | Veelbelovend. Sommige vertalingen zijn correct, maar inconsistent. |
| **Functional** | 0.50 – 0.70 | Bruikbaar als referentie met menselijke beoordeling. Niet geschikt voor inzet zonder beoordeling. |
| **Deployable** | 0.70 – 0.85 | Gereed voor productiegebruik met periodieke beoordeling. Activeert de geschiktheid voor eigendomsoverdracht. |
| **Fluent** | 0.85 – 1.00 | Bijna-moedertaalkwaliteit. Geschikt voor inzet zonder toezicht. |

### Wat is het verschil tussen kwaliteitsniveaus en verificatieniveaus?

**Kwaliteitsniveaus** beschrijven *wat de geautomatiseerde score betekent* (Baseline → Fluent). **Verificatieniveaus** beschrijven *wie het resultaat heeft gevalideerd*:

| Verificatieniveau | Betekenis |
|-------------------|---------------|
| **Self-benchmarked** | De indiener heeft de harness zelf uitgevoerd. Scores zijn plausibel maar niet geverifieerd. |
| **GDS Verified** | Een beheerder heeft het resultaat gereproduceerd met behulp van de ingediende methodeconfiguratie. |
| **Community Validated** | Tweetalige sprekers hebben de vertalingen beoordeeld en de kwaliteit bevestigd. |

Een methode kan "Deployable"-kwaliteit hebben maar slechts "Self-benchmarked"-verificatie — wat betekent dat de score er goed uitziet, maar dat niemand dit onafhankelijk heeft bevestigd.

---

## Indiening & Diskwalificatie

### Wat leidt tot diskwalificatie van mijn indiening?

Uw indiening wordt afgewezen of gemarkeerd als:

1. **Uw methode is blootgesteld aan evaluatiedata.** Als u vermeldingen uit de evaluatiedataset hebt gebruikt voor training, fine-tuning, few-shot-prompting of anderszins, zijn uw scores kunstmatig verhoogd. Dit omvat het gebruik van de referentievertalingen in uw prompt.
2. **Uw run card slaagt niet voor integriteitschecks.** De vingerafdruk moet overeenkomen met de configuratie. Gemanipuleerde run cards worden afgewezen.
3. **Uw methode implementeert het TranslationMethod-protocol niet.** De harness verwacht `translate(entries, config) → results`. Aangepaste integraties die de harness omzeilen, worden niet geaccepteerd.

### Kan ik meerdere keren indienen?

Ja. Het leaderboard houdt alle indieningen bij. U kunt itereren — tientallen experimenten uitvoeren en alleen uw beste indienen. Elke indiening registreert een unieke vingerafdruk, zodat er geen onduidelijkheid bestaat over welke run welke score heeft opgeleverd.

### Hoe laat ik mijn score verifiëren?

1. **Self-benchmarked (automatisch):** Elke indiening begint hier.
2. **GDS Verified:** Dien uw methode in als een reproduceerbaar pakket (code + configuratie + coachingdata). Een beheerder voert het opnieuw uit op dezelfde dataset en bevestigt dat de scores overeenkomen.
3. **Community Validated:** Voor inheemse talen vereist dit dat tweetalige sprekers een steekproef van vertalingen beoordelen. Dit kan niet worden geautomatiseerd — het vereist betrokkenheid van de gemeenschap.

### Is de indiening-API live?

Nog niet. Het `https://mtevalarena.org/api/leaderboard/submit`-eindpunt is aspirationeel. Huidige indieningen moeten worden gedaan via een pull request naar de [eval harness-repo](https://github.com/gamedaysuits/arena) met uw run card JSON in de map `results/`.

---

## Modellen & Parameters

### Welk model moet ik gebruiken?

Er is geen enkel beste model — het hangt af van het taalpaar, uw budget en uw aanpak. Algemene richtlijnen:

| Taaltype | Aanbevolen startpunt | Waarom |
|---------------|---------------------------|-----|
| **Hoog-resourc** (Frans, Spaans, Japans) | `google/gemini-2.5-flash` of `gpt-4o-mini` | Snel, goedkoop, sterke baseline |
| **Laag-resourc met enige LLM-dekking** (Quechua, Yoruba) | `google/gemini-2.5-pro` of `anthropic/claude-sonnet-4` | Grotere modellen hebben betere latente kennis |
| **Polysynthetisch / zeer laag-resourc** (Plains Cree, Inuktitut) | `google/gemini-2.5-pro` met coaching | Coachingdata is belangrijker dan modelkeuze. OMT-1600 omvat enkele polysynthetische talen (bijv. CRK op R1-niveau), maar met standaard BPE-tokenisatie — benchmark het als baseline in de Arena. |

De eval harness gebruikt OpenRouter, zodat elk model dat beschikbaar is op OpenRouter kan worden gebenchmarkt. Voer `champollion models --method llm` uit om beschikbare modellen te bekijken.

### Welke temperatuur moet ik gebruiken?

Lager is over het algemeen beter voor vertaling:

| Temperatuur | Effect | Aanbevolen voor |
|-------------|--------|-----------------|
| **0.0 – 0.2** | Sterk deterministisch, consistente uitvoer | Productiemethoden, definitieve benchmarks |
| **0.3 – 0.5** | Enige variatie, soms creatiever | Verkenning, vroege iteratie |
| **0.6+** | Hoge variatie, onvoorspelbaar | Niet aanbevolen voor MT-benchmarking |

De temperatuur wordt vastgelegd in de run card, zodat verschillende temperaturen verschillende vingerafdrukken opleveren — ze worden behandeld als afzonderlijke experimenten.

### Helpt coachingdata?

Ja, aanzienlijk — voor laag-resourc talen. Coachingdata (grammaticaregels, woordenboekitems, stijlnotities) wordt ingevoegd in de systeemprompt van de LLM. Voor Plains Cree presteren gecoachte methoden consistent beter dan onbewerkte LLM-methoden voor polysynthetische talen, omdat algemene LLM's beperkte blootstelling aan polysynthetische talen hebben en geen morfologisch bewustzijn. Zelfs OMT-1600, dat specifiek is getraind voor CRK, gebruikt standaard BPE-tokenisatie die polysynthetische morfologie structureel niet kan representeren. De coachingdata biedt de linguïstische context die het model mist.

Voor hoog-resourc talen (Frans, Spaans) heeft coaching minder impact, omdat het model al over sterke basiskennis beschikt.

Zie [Coaching Data](https://champollion.dev/docs/concepts/coaching-data) voor de volledige specificatie.

---

## FST & Morfologische Validatie

### Wat als er geen FST is voor mijn taal?

Veel talen hebben geen finite-state transducer. Dat is geen probleem — de harness werkt ook zonder. De composite score gebruikt Profiel B-gewichten (zie [Scoring Specification §4.3](/docs/specifications/scoring#43-weight-tables)), die het gewicht verschuiven naar semantische en oppervlaktemetrics. FST acceptance wordt gemarkeerd als `null` in de run card.

De belangrijkste registers voor bestaande FST's:

| Register | Dekking | URL |
|----------|----------|-----|
| **GiellaLT** | Sámi, Cree, Inuktitut en andere Arctische/subarctische talen | [giellalt.uit.no](https://giellalt.uit.no/) |
| **ALTLab** | Plains Cree, Woods Cree, Ojibwe | [altlab.artsrn.ualberta.ca](https://altlab.artsrn.ualberta.ca/) |
| **Apertium** | ~60 taalparen, voornamelijk Europees | [apertium.org](https://apertium.org/) |
| **UniMorph** | Morfologische paradigma's voor 150+ talen | [unimorph.github.io](https://unimorph.github.io/) |

### Kan ik een FST bouwen?

Ja, maar het is niet eenvoudig. Een FST codeert de morfologische regels van een taal — alle geldige woordvormen. Het bouwen ervan vereist diepgaande linguïstische kennis van de taal. Als u toegang heeft tot een morfologische grammatica (bijv. van een taalkundeafdeling), kan deze worden gecompileerd tot een FST met behulp van tools zoals [HFST](https://hfst.github.io/) of [Foma](https://fomafst.github.io/).

### Hoe werkt FST-gating in de praktijk?

De FST-gated pipeline werkt als volgt:

1. De LLM genereert een vertaling
2. Elk woord in de uitvoer wordt gecontroleerd aan de hand van de FST
3. Woorden die de FST afwijst, worden gemarkeerd als morfologisch ongeldig
4. De methode kan het opnieuw proberen met feedback ("het woord X is niet geldig, probeer het opnieuw")
5. Na nieuwe pogingen worden resterende ongeldige woorden geregistreerd

De FST acceptance rate meet hoeveel woorden de validatie doorstaan. Zie de [FST-Gated Pipeline Tutorial](/docs/tutorials/fst-gated-pipeline) voor een volledig uitgewerkt voorbeeld.

---

## Data & Datasets

### Kan ik een dataset bijdragen voor een nieuwe taal?

Ja. Minimumvereisten uit [Benchmark Specification §11](/docs/specifications/benchmark#11-extending-to-new-languages):

- **50 goudstandaard-vermeldingen** (bron + geverifieerde referentievertaling)
- **30 ontwikkelingsvermeldingen** (kunnen overlappen met de goudstandaard voor kleine corpora)
- **Toestemming van de gemeenschap** (voor inheemse talen is expliciete toestemming van een bestuursorgaan vereist)
- **Herkomstdocumentatie** (waar de data vandaan komt, welke licentie van toepassing is)

Nieuwe datasets openen automatisch nieuwe leaderboard-tracks. Zie [Voor Taalgemeenschappen](/docs/community/for-language-communities) voor de bijdragersgids.

### In welk formaat moet mijn dataset zijn?

JSON met de canonieke veldnamen:

```json
{
  "name": "my-language-dev-v1",
  "language_pair": "en-xxx",
  "segment": "development",
  "version": "1.0",
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "[translation in target language]",
      "difficulty": 1,
      "domain": "general"
    }
  ]
}
```

Zie [Datasets](/docs/leaderboard/datasets) voor het volledige schema en de definities van moeilijkheidsniveaus.

---

## Soevereiniteit & Eigendom

### Wie is eigenaar van een methode die is gebouwd voor een inheemse taal?

Voor inheemse talen activeren methoden die het Deployable-niveau bereiken (composite ≥ 0.70) ÉN community-validatie doorstaan het proces van [eigendomsoverdracht](/docs/sovereignty/ownership-transfer). Het code-eigendom wordt overgedragen van de onderzoeker naar de bestuursorganisatie van de taalgemeenschap.

De onderzoeker behoudt:
- Publicatierechten (academische artikelen over de methode)
- Vermelding op het leaderboard
- Het recht om dezelfde *technieken* toe te passen op andere talen

De bestuursorganisatie verkrijgt:
- Volledig eigendom van de methodecode en coachingdata
- Controle over inzet (wanneer, waar en hoe)
- Inkomsten uit API-gebruik (90% gemeenschap, 10% infrastructuur)

### Kan ik champollion gebruiken voor niet-inheemse talen zonder soevereiniteitsproblemen?

Ja. Voor standaardtalen (Frans, Japans, Spaans, enz.) zijn er geen soevereiniteitsoverwegingen. Gebruik champollion normaal — vertaal, synchroniseer en publiceer naar wens. Het soevereiniteitskader is specifiek van toepassing op inheemse en door gemeenschappen beheerde talen waarbij beginselen van datagovernance (OCAP®, CARE, Te Mana Raraunga) bijzondere aandacht vereisen.

---

## Zie ook

- **[Hoe het werkt](https://champollion.dev/how-it-works)** — de volledige uitleg van de oplossing
- **[Scoring Specification](/docs/specifications/scoring)** — de SSOT voor alle scoringlogica (metrics, gewichten, niveaus)
- **[Benchmark Specification](/docs/specifications/benchmark)** — evaluatieprotocol, corpusformaat, soevereiniteit
- **[Een methode indienen](/docs/getting-started/submit-a-method)** — stapsgewijze quickstart
- **[Leaderboard-regels](/docs/leaderboard/rules)** — indieningscriteria
- **[Datasoevereiniteit](/docs/sovereignty/data-sovereignty)** — OCAP®, CARE en ethische verplichtingen