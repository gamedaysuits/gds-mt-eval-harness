---
sidebar_position: 7
title: "Kader voor corpusontwerp"
---
# Raamwerk voor het Ontwerp van Evaluatiecorpora

> **Versie:** 1.0
> **Status:** Concept
> **Doel:** Een systematische methodologie voor het bouwen van evaluatiecorpora die geldige, betrouwbare en taalkundig betekenisvolle beoordelingen van vertaalkwaliteit opleveren. Dit is de gezaghebbende bron voor de manier waarop Champollion-evaluatiedatasets worden ontworpen, samengesteld en onderhouden.

---

## 1. Ontwerpprincipes

### 1.1 — Waarom geen publieke benchmarks?

Publieke parallelle corpora (FLORES+, Tatoeba, WMT-testsets, OPUS) zijn beschikbaar voor ontwikkeling en foutopsporing, maar zijn **uitgesloten van officiële leaderboard-evaluatie**. De reden is eenvoudig:

**Contaminatie.** Frontier-LLM's worden getraind op enorme webcrawls. Elke parallelle tekst die publiekelijk beschikbaar is geweest — met name in gecureerde, veelgeciteerde benchmarkdatasets — bevindt zich waarschijnlijk in hun trainingsdata. Wanneer u GPT-4o evalueert op FLORES+ en het scoort 85 chrF++, kunt u niet onderscheiden of "het model goed is in vertalen" of "het model deze specifieke zinsparen heeft gememoriseerd." Dit is geen theoretische zorg — [onderzoek heeft aangetoond](https://arxiv.org/abs/2311.04850) dat contaminatie-effecten op MT-benchmarks meetbaar zijn.

Voor Champollion is dit om de volgende redenen van bijzonder belang:
- Ons leaderboard vergelijkt primair LLM-gebaseerde methoden
- Onze toegevoegde waarde is *eerlijke, rigoureuze evaluatie*
- Onze doelgebruikers (taalgemeenschappen) nemen implementatiebeslissingen op basis van deze scores

### 1.2 — Kernvereisten

Elk Champollion-evaluatiecorpus moet voldoen aan:

| Vereiste | Motivering |
|----------|------------|
| **Door mensen geschreven** | Geen synthetische data. Alle bronteksten en referentievertaingen moeten door mensen zijn geschreven. LLM's mogen helpen bij uitlijning en opmaak, maar mogen nooit inhoud genereren. |
| **Niet publiekelijk beschikbaar in parallelle vorm** | De brontekst mag publiek zijn; de referentievertaingen mogen publiek zijn; maar de specifieke *koppeling* mag niet bestaan als downloadbaar parallel corpus. |
| **Herkomst gedocumenteerd** | Elke invoer moet een gedocumenteerde oorsprong hebben: brondocument, vertaler, licentie, datum. |
| **Taalkundig onderbouwd** | De dekking moet worden geleid door typologische kenmerken, niet door willekeurige steekproeven. |
| **Domeingestratificeerd** | Invoeren moeten meerdere gedefinieerde tekstdomeinen beslaan met gecontroleerde vertegenwoordiging. |
| **Moeilijkheidsgraad ingedeeld** | Invoeren moeten worden ingedeeld in moeilijkheidsgraden (1–5) op basis van structurele complexiteit. |
| **Versiebeheerd** | Corpusversies worden gehasht op basis van inhoud. Scores zijn alleen vergelijkbaar binnen dezelfde versie. |
| **Beoordeelbaar door de gemeenschap** | Referentievertaingen moeten beoordeelbaar zijn door leden van de taalgemeenschap. |

---

## 2. Selectie van bronteksten

### 2.1 — Domeintaxonomie

Champollion evalueert vertaling voor **praktische implementatiecontexten**, niet voor academische oefeningen. De domeintaxonomie weerspiegelt teksttypen uit de praktijk die gebruikers van vertalingen tegenkomen:

| Domein | Code | Beschrijving | Voorbeeldbronnen |
|--------|------|--------------|------------------|
| **Software-UI** | `ui` | Knoplabels, menu-items, foutmeldingen, tooltips, onboarding-flows | Open-source app-strings, documentatieportalen |
| **Officieel/Administratief** | `admin` | Overheidsdocumenten, juridische kennisgevingen, formulieren, beleidsverklaringen | Publieke overheidspublicaties, gemeentelijke documenten |
| **Educatief** | `edu` | Leerboekinhoud, lesmateriaal, instructieteksten | Gepubliceerd onderwijsmateriaal, leshandleidingen |
| **Narratief/Literair** | `lit` | Verhalen, culturele teksten, transcripties van mondelinge geschiedenis | Gepubliceerde boeken, culturele archieven (met toestemming) |
| **Conversationeel** | `conv` | Dialoog, chatachtige uitwisselingen, informele schriftelijke communicatie | Gepubliceerde dialoogcorpora, scenario's, interviewtranscripties |
| **Technisch** | `tech` | API-documentatie, README-bestanden, technische specificaties | Open-source projectdocumentatie |
| **Gezondheid/Medisch** | `health` | Medische informatie voor patiënten, berichten over volksgezondheid | Overheidspublicaties over gezondheid |
| **Nieuws/Journalistiek** | `news` | Nieuwsartikelen, persberichten, actuele zaken | Gemeenschapskranten, inheemse mediakanalen |

### 2.2 — Domeinverdeling

Een standaard evaluatiecorpus moet streven naar de volgende verdeling. De exacte percentages kunnen per taalpaar variëren op basis van welke teksttypen het meest relevant zijn voor de doelgemeenschap:

| Domein | Doelpercentage | Motivering |
|--------|----------------|------------|
| Software-UI | 25% | Primaire implementatiecontext voor champollion CLI-gebruikers |
| Officieel/Administratief | 15% | Vertaling met hoge inzet en juridische implicaties |
| Educatief | 15% | Kerngebruiksscenario voor taalrevitalisering |
| Narratief/Literair | 10% | Test culturele nuance en literair register |
| Conversationeel | 10% | Test informeel register en natuurlijke spreekpatronen |
| Technisch | 10% | Test precisie en terminologieconsistentie |
| Gezondheid/Medisch | 10% | Hoge inzet, test domeinspecifiek vocabulaire |
| Nieuws/Journalistiek | 5% | Test hedendaags vocabulaire en neutraal register |

### 2.3 — Selectiecriteria voor bronteksten

Bij het selecteren van bronteksten voor een nieuw corpus:

1. **Licentiecompatibiliteit.** De brontekst moet onder een licentie vallen die gebruik in een evaluatiecorpus toestaat. Geef de voorkeur aan CC BY, CC BY-SA of publiek domein. Documenteer de licentie.

2. **Actualiteit.** Geef de voorkeur aan teksten die in de afgelopen 10 jaar zijn gepubliceerd. Taal evolueert — met name vocabulaire rondom technologie, bestuur en geneeskunde.

3. **Registerdiversiteit.** Zoek binnen elk domein naar teksten op verschillende formaliteitsniveaus. Een persconferentie van de overheid (formeel) en een bericht op sociale media van de overheid (informeel) behoren beide tot het domein `admin`, maar hebben een verschillend register.

4. **Culturele relevantie.** Geef voor inheemse en minderheidstalen prioriteit aan teksten die van belang zijn voor de gemeenschap — documenten over landbeheer, onderwijsmateriaal in de taal, teksten voor cultureel behoud — boven teksten die toevallig in parallelle vorm beschikbaar zijn.

5. **Geen machinaal vertaalde bronnen.** Als een "parallel" document is gemaakt door het origineel door Google Translate te halen en vervolgens na te bewerken, is dit NIET aanvaardbaar als referentievertaling. De referentie moet een onafhankelijke menselijke vertaling zijn.

---

## 3. Systeem van moeilijkheidsgraden

### 3.1 — Definitie van de niveaus

Elke invoer krijgt een moeilijkheidsgraad (1–5) toegewezen op basis van de structurele complexiteit van de *brontekst*, niet van de vertaalmoeilijkheid (die per methode verschilt).

| Niveau | Label | Structurele kenmerken |
|--------|-------|----------------------|
| 1 | **Elementair** | Eenvoudige zinnen. Enkelvoudige bijzin. Tegenwoordige tijd. Gangbaar vocabulaire. Geen idiomen. Geen ingebedde structuren. |
| 2 | **Gemiddeld** | Samengestelde zinnen. Twee bijzinnen verbonden door een voegwoord. Verleden/toekomstige tijd. Enig domeinvocabulaire. |
| 3 | **Gevorderd** | Complexe zinnen. Bijzinnen, betrekkelijke bijzinnen. Gemengde tijden. Domeinspecifieke terminologie. Passieve constructies. |
| 4 | **Expert** | Meerdere ingebedde bijzinnen. Juridisch/technisch register. Conditionele structuren. Abstracte concepten. Culturele verwijzingen. |
| 5 | **Extreem** | Dicht proza met meerdere gelijktijdige uitdagingen: geneste onderschikking, ambigue pronominale verwijzing, culturele idiomen, gemengd register, zeldzaam vocabulaire. |

### 3.2 — Taalkundig onderbouwde moeilijkheidsfactoren

Naast structurele complexiteit wordt de moeilijkheidsgraad beïnvloed door de **typologische afstand** tussen de bron- en doeltaal. Deze factoren zijn ontleend aan WALS-typologische kenmerken en de classificatiegegevens van de taalkaart:

| Factor | Lage moeilijkheid | Hoge moeilijkheid |
|--------|-------------------|-------------------|
| **Woordvolgorde** | Dezelfde basisvolgorde (bijv. SVO→SVO) | Verschillende basisvolgorde (bijv. SVO→SOV) |
| **Morfologisch type** | Vergelijkbaar type (bijv. analytisch→analytisch) | Verschillend type (bijv. analytisch→polysynthetisch) |
| **Grammaticaal geslacht** | Hetzelfde systeem of geen geslacht | Bron heeft geen geslacht, doel heeft complex geslachtssysteem |
| **Honorifiek/register** | Geen registermarkering | Doel heeft complex registersysteem (bijv. Japans, Koreaans) |
| **Schrift** | Hetzelfde schrift | Verschillend schrift (transliteratie vereist) |
| **Animaatheid** | Geen animaatheidsonderscheid | Doel heeft op animaatheid gebaseerde congruentie (bijv. Cree) |
| **Evidentialiteit** | Geen evidentialiteit | Doel markeert informatiebron grammaticaal |

### 3.3 — Verdeling van moeilijkheidsgraden

Een standaard corpus moet bij benadering de volgende verdeling hebben:

| Niveau | Doelpercentage | Motivering |
|--------|----------------|------------|
| 1 | 15% | Stelt de basislijn vast — zelfs zwakke methoden zouden hiermee overweg moeten kunnen |
| 2 | 25% | Alledaagse praktische vertaling |
| 3 | 30% | Hier worden kwaliteitsverschillen tussen methoden zichtbaar |
| 4 | 20% | Onderscheidt goede methoden van uitstekende |
| 5 | 10% | Plafondtest — zeer weinig methoden zullen hiermee goed omgaan |

---

## 4. Kwaliteit van referentievertaingen

### 4.1 — Vereisten voor vertalers

Referentievertaingen moeten worden geproduceerd door mensen die:

1. **Vloeiende sprekers** zijn van de doeltaal (moedertaal of gelijkwaardig)
2. **Geletterd** zijn in zowel de bron- als de doeltaal
3. **Domeinbewust** zijn voor het domein van de tekst (een medisch vertaler voor gezondheidsteksten, enz.)
4. **Onafhankelijk** zijn — de vertaler mag tijdens het vertalen geen toegang hebben tot MT-uitvoer voor dezelfde tekst

### 4.2 — Vertaalopdracht

Elke vertaler ontvangt een opdracht die het volgende bevat:

- Het te gebruiken **register** (formeel, conversationeel, enz.)
- De **doelgroep** (algemeen publiek, specialisten, kinderen, enz.)
- Eventuele **terminologieconventies** die specifiek zijn voor de taalgemeenschap
- Expliciete instructie: "Vertaal de betekenis, niet de woorden. Een natuurlijk klinkende vertaling is waardevoller dan een letterlijke."

### 4.3 — Kwaliteitsborging

1. **Dubbele vertaling.** Idealiter heeft elke invoer twee onafhankelijke referentievertaingen van verschillende vertalers. Waar dit niet haalbaar is, geef dan prioriteit aan dubbele vertaling voor niveaus 4–5.

2. **Beoordeling door de gemeenschap.** Referentievertaingen moeten worden beoordeeld door ten minste één extra spreker die de vertaling niet heeft geproduceerd.

3. **Aanvaardbare varianten.** Documenteer voor elke referentie bekende aanvaardbare varianten (woordvolgorde, orthografische conventies, dialectvormen). Deze voeden de `equivalent_match_rate`-metriek.

### 4.4 — Kenmerken van een slechte referentie

| Probleem | Waarom het de evaluatie ongeldig maakt |
|----------|----------------------------------------|
| Machinaal vertaald en vervolgens nabewerkt | Nabewerking behoudt de MT-structuur; benadeelt methoden die meer natuurlijke vertalingen produceren |
| Vertaald door een leerder, niet door een vloeiende spreker | De referentie kan fouten bevatten die correcte MT-uitvoer benadelen |
| Overdreven letterlijk | Natuurlijke vertalingen scoren slecht ten opzichte van letterlijke referenties |
| Enkelvoudige geldige interpretatie voor een ambigue bron | Benadeelt geldige alternatieve interpretaties |

---

## 5. Preventie van contaminatie

### 5.1 — Het bedreigingsmodel voor contaminatie

| Bedreiging | Beschrijving | Maatregel |
|------------|--------------|-----------|
| **Overlap met trainingsdata** | LLM's getraind op het parallelle corpus | Publiceer het parallelle corpus niet openbaar |
| **Few-shot-lekkage** | Methode-auteur gebruikt evaluatie-invoeren als few-shot-voorbeelden | Vingerafdrukcontrole: invoeren in de prompt worden gedetecteerd en gemarkeerd |
| **Indirecte contaminatie** | Brontekst bestaat in LLM-trainingsdata (eentalig) | Aanvaardbaar — eentalige brontekst is te verwachten. De *koppeling* moet nieuw zijn. |
| **Gemeenschapscontaminatie** | Gemeenschapsbeoordelaars delen invoeren publiekelijk | Licentievoorwaarden verbieden herdistributie van het parallelle corpus |

### 5.2 — Geheimhoudingsniveaus van het corpus

| Niveau | Zichtbaarheid | Gebruik |
|--------|---------------|---------|
| **Publieke ontwikkelingsset** | Volledig publiek | Methode-ontwikkeling, foutopsporing, regressietesten. Scores worden NIET gepubliceerd op het leaderboard. |
| **Afgeschermde evaluatieset** | Brontekst zichtbaar, referenties geheim | Officiële leaderboard-evaluatie. Methoden ontvangen de brontekst en retourneren vertalingen; scoring vindt plaats aan de serverzijde. Referenties worden nooit blootgesteld aan de methode. |
| **Goudstandaard-set** | Volledig geheim, beheerd door de gemeenschap | Door de gemeenschap gevalideerde evaluatie. Beheerd door een governanceorganisatie. Gebruikt voor het verificatieniveau "Community Validated". |

### 5.3 — Rotatiebeleid

Evaluatiecorpora moeten periodiek worden **geroteerd**:

1. Nadat een corpus 12 maanden in gebruik is, begint u met het samenstellen van een vervanger
2. Zet het oude corpus terug naar de status "ontwikkelingsset" (publiek)
3. Promoveer het nieuwe corpus naar "afgeschermde evaluatieset"
4. Dit voorkomt geleidelijke contaminatie door iteratieve optimalisatie tegen een vast doel

---

## 6. Workflow voor corpusconstructie

### 6.1 — Stapsgewijs proces

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

### 6.2 — Dekking van taalkundige verschijnselen

Elk corpus moet invoeren bevatten die specifieke taalkundige verschijnselen testen die relevant zijn voor het taalpaar. Deze zijn ontleend aan de velden `linguisticChallenges` en `contactInfluences` van de taalkaart:

**Universele verschijnselen (alle taalparen):**
- Pronominale verwijzing (ambigue antecedenten)
- Negatie (enkelvoudig, dubbel, bereik)
- Kwantoren (alle, sommige, geen, de meeste)
- Temporele uitdrukkingen (relatieve datums, duren)
- Eigennamen (personen, plaatsen, organisaties)
- Getallen en maten
- Lijsten en opsommingen

**Paarsspecifieke verschijnselen (uit de taalkaart):**
- Voor polysynthetische doeltalen: complexe werkwoordsmorfologie, incorporatie
- Voor doeltalen met grammaticaal geslacht: geslachtscongruentie, neutrale/inclusieve verwijzing
- Voor SOV-doeltalen: werkwoorden aan het einde van de bijzin, postposities
- Voor toontalen: betekenisonderscheidingen op basis van toon
- Voor honorifieke talen: registermarkeringen, sociale context
- Voor contacttalen: grenzen van code-switching, integratie van leenwoorden

### 6.3 — Minimale corpusomvang

Statistische betrouwbaarheid vereist minimale aantallen invoeren. Deze zijn gebaseerd op vereisten voor betrouwbaarheidsintervallen via paarsgewijze bootstrap (uit `significance.py`):

| Doel | Minimale invoeren | Aanbevolen |
|------|-------------------|------------|
| Ontwikkelingsset | 50 | 100–200 |
| Afgeschermde evaluatieset | 100 | 200–500 |
| Goudstandaard-set | 200 | 500+ |
| Minimum per domein | 10 | 25+ |
| Minimum per niveau | 10 | 20+ |

**Waarom minimaal 100 voor evaluatie?** Met minder dan ~100 invoeren kunnen paarsgewijze bootstrap-significantietoetsen (1.000 hersteekproeven) geen verschillen kleiner dan ~5 chrF++-punten betrouwbaar detecteren. Met 200+ invoeren kunnen we ~2-puntverschillen detecteren bij p<0,05.

---

## 7. JSON-formaat voor het corpus

Elke corpusinvoer volgt de harness-specificatie:

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

## 8. Maatregelen tegen manipulatie

### 8.1 — Integriteit van het corpus

| Maatregel | Implementatie |
|-----------|---------------|
| **Inhashering van inhoud** | Corpusversie = SHA-256 van gesorteerde invoer-ID's + referenties. Elke wijziging produceert een nieuwe versie. |
| **Vingerafdruk van invoeren** | Elke invoer heeft een op inhoud gebaseerd ID. Als iemand resultaten indient op basis van een gewijzigd corpus, komt de vingerafdruk niet overeen. |
| **Handhaving van afscherming** | Voor officiële evaluatie ontvangen methoden ALLEEN de brontekst. Referenties worden nooit blootgesteld. Scoring vindt plaats aan de serverzijde. |
| **Rotatieschema** | Corpora worden jaarlijks geroteerd om langdurige optimalisatie tegen een vast doel te voorkomen. |

### 8.2 — Integriteit van inzendingen

| Maatregel | Implementatie |
|-----------|---------------|
| **Deterministische vingerafdruk** | De run-configuratie (model, temperatuur, prompt, corpusversie) wordt gehasht. Identieke configuraties produceren identieke vingerafdrukken. |
| **Detectie van cherry-picking** | Inzenders moeten alle runs openbaar maken, niet alleen de beste. Meerdere inzendingen met dezelfde vingerafdruk worden gemarkeerd. |
| **Contaminatiecontrole** | Als evaluatie-invoeren woordelijk voorkomen in de prompt of trainingsdata van de methode, wordt de inzending gediskwalificeerd. |

---

## 9. Bestaande corpora

### 9.1 — EDTeKLA-ontwikkelingsset v1

| Eigenschap | Waarde |
|------------|--------|
| **ID** | `edtekla-dev-v1` |
| **Taalpaar** | EN → CRK (Plains Cree, SRO) |
| **Invoeren** | 404 (`master_corpus.json`: 62 goud + 342 leerboek); 548 in totaal beschikbaar |
| **Domeinen** | Educatief (100%) |
| **Niveaus** | 1–5 (verdeling nader te bepalen na audit van invoeren) |
| **Licentie** | CC BY-NC-SA 4.0 |
| **Status** | Ontwikkelingsset (publiek) |

**Beperkingen:** Enkel domein (uitsluitend educatief). Geen domeinstratisficatie. Niveautoewijzingen kunnen een audit vereisen. Kleine corpusomvang beperkt de statistische kracht voor significantietoetsing.

### 9.2 — Geplande corpora

| Corpus | Taalpaar | Status | Eigenaar |
|--------|----------|--------|----------|
| Aangepast corpus EN → TL (Filipijns) | EN → TL | Gepland | Projecteigenaar |
| Afgeschermde set EN → CRK | EN → CRK | Toekomstig (gemeenschapspartner vereist) | Gemeenschapsgovernanceorganisatie |

---

## 10. Integratie van de taalkaart

Het corpusraamwerk integreert met het taalkaartensysteem:

1. **Domainselectie** wordt geïnformeerd door het veld `linguisticChallenges` van de kaart — als een taal unieke uitdagingen heeft (polysynthese, toon, animaatheid), moet het corpus invoeren bevatten die deze testen.

2. **Kalibratie van moeilijkheidsgraad** maakt gebruik van het veld `classification` van de kaart — de typologische afstand tussen bron- en doeltaalfamilies beïnvloedt wat als "moeilijk" wordt beschouwd.

3. **Registerdekking** maakt gebruik van het veld `registers` van de kaart — als een taal gedefinieerde registers heeft (formal-filipino, taglish-professional, taglish-casual), moet het corpus invoeren bevatten op elk registerniveau.

4. **Testen van contactinvloed** maakt gebruik van het veld `contactInfluences` van de kaart — voor talen met zware leenlagen (Filipijns: Spaans + Engels + Arabisch), neem invoeren op die testen of methoden leenwoorden correct verwerken versus ze over-vertalen.

5. **Schriftverwerking** maakt gebruik van het veld `scripts[]` van de kaart — voor meertalige schriften (Servisch: Cyrillisch + Latijn), neem invoeren op die de correcte schriftselectie testen.

---

## Referenties

- **Champollion Scoring Specification** — definieert alle metrieken, samengestelde gewichten, kwaliteitsniveaus
- **Champollion Benchmark Specification** — evaluatieprotocol, corpusformaat, datasouvereiniteit
- **WALS** (World Atlas of Language Structures) — database van typologische kenmerken
- **Glottolog** — gezaghebbende bron voor taalclassificatie
- **ISO 639-3** — standaard voor taalidentificatie
- **EdTeKLA** — bron van het eerste evaluatiecorpus

---

*Dit document is een levende specificatie. Werk het bij naarmate nieuwe corpora worden gebouwd en lessen worden geleerd.*