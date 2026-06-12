---
sidebar_position: 2
title: "Eigendomsoverdracht"
---
# Eigendomsoverdracht

> **Samenvatting.** Wanneer een vertaalmethode de Deployable-tier bereikt (composite ≥ 0.70) en de gemeenschapsreview doorstaat, gaat de code-eigendom over van de onderzoeker naar de inheemse bestuursorganisatie. Deze pagina documenteert de vijffasige overdrachtsworkflow, de OCAP®-afstemming en richtlijnen voor onderzoekers die methoden ontwikkelen voor inheemse talen.

Wanneer een vertaalmethode de Arena-ranglijst wint, wat gebeurt er dan met de code? Voor inheemse en laagbronnen-talen is het antwoord niet "de onderzoeker behoudt deze." Het antwoord is: **de gemeenschap is eigenaar.**

---

## Hoe Het Werkt

De Arena hanteert een duidelijke workflow van onderzoek naar gemeenschapseigendom:

### 1. Methode-ontwikkeling
Een onderzoeker, student of ontwikkelaar bouwt een vertaalmethode — een FST-gated pipeline, een coached LLM, een fijnafgestemd model of een andere aanpak. Ze ontwikkelen deze met eigen middelen.

### 2. Arena-evaluatie
De methode wordt gebenchmarkt via de [eval harness](/docs/specifications/harness). Elke inzending wordt gekoppeld aan een specifieke Git-commit en datasetversie via een vingerafdruk. Scores zijn reproduceerbaar.

### 3. Gemeenschapsreview
Voor methoden voor inheemse talen worden de resultaten beoordeeld door gemeenschapstalenwerkers en bestuursorganisaties. Een hoge score op de ranglijst bewijst dat de methode *werkt*; het bewijst niet dat deze *passend* is.

### 4. Code-overdracht
Wanneer een methode de **Deployable**-tier bereikt (composite score ≥ 0.70 ten opzichte van de goudstandaard-evaluatie) **en** de gemeenschapsreview doorstaat (menselijke validatie):
- Draagt de onderzoeker de broncode over
- Gaat het juridisch eigendom over naar de inheemse bestuursorganisatie (bijv. een stamraad, taalautoriteit of Métis-organisatie)
- Beheert de bestuursorganisatie de encryptiesleutels voor evaluatiedatasets
- Wordt de methode een door de gemeenschap beheerd bezit

Zie de [Scoring Specification](/docs/specifications/scoring), §5 voor definities van kwaliteitstiers en de [Benchmark Specification](/docs/specifications/benchmark), §8.3 voor de volledige overdrachtsvoorwaarden en §7 voor de menselijke validatiepoort.

### 5. Productie-implementatie
De methode wordt geëxporteerd als een [champollion](https://champollion.dev)-plugin en geïmplementeerd in de productie-API. De gemeenschap beheert:
- Wie toegang heeft tot de methode
- Welke prijsvoorwaarden van toepassing zijn
- Of de methode commercieel gebruikt mag worden
- Wanneer en hoe de methode wordt bijgewerkt

---

## Waarom Dit Belangrijk Is

Traditioneel ML-onderzoek volgt een extractief patroon:
1. Onderzoeker verzamelt gegevens van een gemeenschap
2. Onderzoeker traint een model
3. Onderzoeker publiceert een artikel
4. Gemeenschap ontvangt niets

Dit patroon opereert nu op industriële schaal. Meta's OMT-1600 (maart 2026) trainde vertaalmodellen voor 1.600 talen — waaronder inheemse talen zoals Plains Cree — met behulp van web-gescrapete gegevens en bijbelvertalingen. De modellen werden getraind zonder gemeenschapstoestemmingsprotocollen, de gewichten zijn momenteel niet beschikbaar voor download, en de gemeenschappen wier talen werden gemodelleerd hebben geen eigendomsbelang, geen bestuursrol en geen inkomsten. Het artikel is het product. De gemeenschap is de gegevensbron.

De Arena keert dit om:
1. Onderzoeker bouwt een methode
2. Arena valideert deze aan de hand van door de gemeenschap samengestelde corpora met morfologische metrieken
3. Gemeenschap ontvangt eigendom van de werkende code
4. Gemeenschap verdient inkomsten uit API-gebruik

**Dit is het fundamentele verschil tussen Champollion en elke andere LRL MT-inspanning, inclusief OMT-1600:** wij produceren niet alleen methoden vóór gemeenschappen — wij dragen eigendom van methoden over *aan* gemeenschappen. De code, de gewichten, de implementatie-infrastructuur — het wordt allemaal gemeenschapseigendom. Dit is geen theoretisch kader — het is de operationele workflow voor elke methode voor inheemse talen op het platform.

---

## OCAP®-Afstemming

Het eigendomsoverdrachtproces implementeert direct de [OCAP®-principes](/docs/sovereignty/data-sovereignty):

| Principe | Implementatie |
|---|---|
| **Ownership** | De bestuursorganisatie heeft de eigendomstitel van de methodecode en modelgewichten |
| **Control** | De bestuursorganisatie beheert de implementatievoorwaarden, toegang en prijsstelling |
| **Access** | Gemeenschapsleden hebben toegang tot de methode via de champollion API of directe download |
| **Possession** | Linguïstische bronnen (coaching-gegevens, woordenboeken, FST-regels) blijven op door de gemeenschap beheerde infrastructuur via de `api`-methode |

---

## Voor Onderzoekers

Als u een methode ontwikkelt voor een inheemse taal:

1. **Bouw een relatie op** met de taalgemeenschap voordat u begint
2. **Gebruik openlijk gelicentieerde gegevens** voor ontwikkeling (geen door de gemeenschap beperkte bronnen)
3. **Documenteer herkomst** in uw [run card](/docs/specifications/run-card) — vermeld elke bron, de licentie en de oorsprong
4. **Wees bereid tot overdracht** — als uw methode slaagt, behoort de code toe aan de gemeenschap, niet aan u
5. **Dit is een kenmerk, geen beperking** — uw bijdrage is de architectuur en techniek, die u kunt publiceren en hergebruiken. De bijdrage van de gemeenschap is de linguïstische kennis die het laat werken voor hun taal.

---

## Zie Ook

- [Data Sovereignty](/docs/sovereignty/data-sovereignty) — OCAP-, CARE- en Te Mana Raraunga-principes
- [Het Economisch Model](/docs/sovereignty/economic-model) — hoe eigendom inkomsten genereert
- [Ondersteuning van een Laagbronnen-taal](/docs/community/low-resource-languages) — de onderzoekscontext