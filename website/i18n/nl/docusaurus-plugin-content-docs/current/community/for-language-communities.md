---
sidebar_position: 1
title: "Voor Taalgemeenschappen"
---
# Voor Taalgemeenschappen

> **Samenvatting.** Een gids voor sprekers van inheemse talen en talen met beperkte middelen, waarin wordt uitgelegd hoe u kunt bijdragen aan de Arena (referentievertaingen, vertaalreview, coachingdata) en wat de gemeenschap daarvoor terugkrijgt (code-eigendom, API-inkomsten, volledige controle over de implementatie). Programmeerkennis is niet vereist.

U hoeft geen programmeur te zijn om bij te dragen aan de Arena. Als u een inheemse taal of een taal met beperkte middelen spreekt, bent u de belangrijkste persoon in dit ecosysteem.

---

## Wat Wij Van U Nodig Hebben

### Referentievertaingen

Wij hebben gecureerde vertaalparen nodig voor evaluatie — aan de ene kant Engels, aan de andere kant uw taal. Deze worden de "antwoordsleutel" waaraan alle vertaalmethoden worden getoetst.

U kunt deze samenstellen uit:
- **Educatief materiaal** — oefeningen uit leerboeken, lesplannen, werkbladen
- **Gemeenschapsdocumenten** — notulen, nieuwsbrieven, aankondigingen
- **Alledaagse uitdrukkingen** — UI-teksten, app-labels, veelgebruikte uitdrukkingen
- **Culturele inhoud** — verhalen, liederen of beschrijvingen (met de juiste toestemmingen)

Het formaat is eenvoudige JSON:
```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

### Vertaalreview

Elke methode die beweert werkende vertalingen te produceren, heeft menselijke validatie nodig. Tweetalige sprekers beoordelen de uitvoer en vertellen ons of de computer het goed heeft gedaan — en belangrijker nog, *waarom* het fout ging.

### Coachingdata

Grammaticaregels, woordenboekitems, morfologische patronen — dit zijn de taalkundige bronnen die vertaalmethoden laten werken. Uw kennis van hoe uw taal werkt, is door geen enkel AI-model te vervangen.

---

## Wat U Daarvoor Terugkrijgt

### Eigendom

Wanneer een vertaalmethode voor uw taal is ontwikkeld en gevalideerd op de Arena, wordt het [eigendom overgedragen](/docs/sovereignty/ownership-transfer) aan de bestuursorganisatie van uw gemeenschap. U bezit de code, de modelgewichten en de implementatie.

### Inkomsten

Wanneer ontwikkelaars de methode voor uw taal gebruiken via de champollion API, ontvangt uw gemeenschap [90% van de API-inkomsten](/docs/sovereignty/economic-model). De resterende 10% dekt de infrastructuurkosten.

### Controle

Uw bestuursorganisatie bepaalt:
- Wie toegang heeft tot de methode
- Of deze commercieel mag worden gebruikt
- Welke prijsvoorwaarden van toepassing zijn
- Wanneer en hoe de methode wordt bijgewerkt
- Welke gegevens worden gebruikt voor verdere ontwikkeling

---

## Hoe U Kunt Deelnemen

1. **Neem contact op** — Open een issue in de [Arena-repository](https://github.com/gamedaysuits/arena) of stuur een e-mail naar de beheerders
2. **Beschrijf uw taal** — Tot welke taalfamilie behoort ze? Hoeveel sprekers zijn er? Welke schrijfsystemen worden gebruikt? Welke computationele middelen bestaan er (FST's, woordenboeken, corpora)?
3. **Begin klein** — Zelfs 50 gecureerde vertaalparen zijn voldoende om een evaluatiedataset aan te maken en een nieuw leaderboard-onderdeel te openen
4. **Verbind ons met het bestuur** — Wie in uw gemeenschap heeft zeggenschap over taaldata en technologie? Het soevereiniteitsmodel van de Arena vereist een bestuurspartner

---

## Datasoevereiniteit

Uw taaldata is van u. De Arena is gebouwd op [OCAP®-principes](/docs/sovereignty/data-sovereignty):

- Wij verzamelen of bewaren uw taalkundige gegevens nooit op onze servers
- Vertaalmethoden maken gebruik van de `api`-architectuur — alle coachingdata, woordenboeken en grammaticaregels blijven op infrastructuur die u beheert
- U bepaalt wie methoden voor uw taal mag ontwikkelen
- Leaderboard-scores bewijzen dat een methode werkt; ze verlenen geen toestemming om deze te implementeren

---

## Zie Ook

- [Datasoevereiniteit](/docs/sovereignty/data-sovereignty) — het volledige OCAP-, CARE- en Te Mana Raraunga-kader
- [Eigendomsoverdracht](/docs/sovereignty/ownership-transfer) — wat er gebeurt wanneer een methode wint
- [Het economisch model](/docs/sovereignty/economic-model) — hoe scores worden omgezet in inkomsten
- [Ondersteuning van een taal met beperkte middelen](/docs/community/low-resource-languages) — technische context voor onderzoekers die samenwerken met gemeenschappen