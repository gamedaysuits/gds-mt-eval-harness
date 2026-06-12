---
sidebar_position: 2
title: "Hoe Sprekers Worden Betaald"
slug: '/perspectives/how-speakers-get-paid'
description: "Wat community validators en vertalers ontvangen voor benchmarkwerkzaamheden, waarom betaling van sprekers niet onderhandelbaar is, en hoe de vergoeding schaalt naarmate de Arena groeit. Alle cijfers zijn afkomstig uit de gepubliceerde specificaties."
related:
  - label: "Speaker Validation Protocol"
    to: /docs/specifications/speaker-validation
    kind: spec
    note: "The work validators are paid for"
  - label: "Prize Specification"
    to: /docs/specifications/prizes
    kind: spec
    note: "Where prize money goes, and why"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
---
# Hoe sprekers worden betaald

> **Transparantienota.** Elk getal op deze pagina staat al in een gepubliceerde specificatie — de [Benchmarkspecificatie §10](/docs/specifications/benchmark#10-cost-framework), het [Sprekervalidatieprotocol](/docs/specifications/speaker-validation) en de [Prijsspecificatie](/docs/specifications/prizes). Deze pagina brengt ze op één plek samen, in begrijpelijke taal, zodat niemand een specificatie hoeft te lezen om te weten wat spreektijd hier waard is. Er worden geen toezeggingen gedaan die verder gaan dan wat die documenten al vermelden.

Een tweetalige spreker die kan beoordelen of een machinaal geproduceerde zin authentiek en vloeiend is en de juiste betekenis heeft, is de schaarsste en meest waardevolle deelnemer in dit hele systeem. Al het andere — harnesses, metrics, leaderboards — bestaat om een kleine hoeveelheid van die persoons tijd zo ver mogelijk te laten reiken.

De eerste regel is dan ook eenvoudig: **sprekers worden betaald voor hun tijd, tegen professionele tarieven, ongeacht wat de resultaten laten zien.**

---

## Waarom het betalen van sprekers niet onderhandelbaar is

Taalkundig technologieonderzoek heeft een lange gewoonte om vloeiende sprekers te behandelen als een gratis hulpbron — "gemeenschapsbetrokkenheid" die datasets, publicaties en carrières oplevert voor iedereen behalve de sprekers zelf. Wij beschouwen dat patroon als extractief, en de mensen die het meest gekwalificeerd zijn voor dit werk zijn precies de mensen wier tijd al wordt opgeëist door het urgente werk van lesgeven, vertalen en kinderen opvoeden in de taal.

Drie ontwerpconsequenties volgen hieruit:

1. **Geen vrijwilligerspijplijn.** Wij vragen sprekers niet om evaluatiewerk te doneren als gunst aan het onderzoek. Deelname is een betaalde opdracht, en het afwijzen ervan kost een spreker niets.
2. **Betaling is onvoorwaardelijk.** Sprekers worden betaald ongeacht of hun beoordelingen worden gebruikt, en betaling is niet afhankelijk van de resultaten. Het gepubliceerde protocol verbindt zich tot betaling binnen twee weken na het voltooien van elk taakblok.
3. **Vergoeding is niet het enige.** Sprekers die beoordelingen bijdragen ontvangen ook naamsvermelding (met naam of anoniem, naar eigen keuze), optioneel mede-auteurschap op publicaties die hun beoordelingen gebruiken, het recht om hun bijdragen op elk moment in te trekken, en vetorecht over publicatie van resultaten die zij problematisch achten. Die voorwaarden staan in het [Sprekervalidatieprotocol §5–6](/docs/specifications/speaker-validation), niet in een bijlage.

## De gepubliceerde tarieven

Het kostenraamwerk van de benchmark stelt de vergoeding voor tweetalige sprekers vast op **$50–65 CAD per uur** voor corpus- en validatiewerk. Wat dat per rol betekent:

### Een benchmarkcorpus opbouwen

Het aanmaken van de referentievertaingen waaraan elke methode wordt beoordeeld, is de fundamentele sprekerstaak. Het gepubliceerde oprichtingsbudget per taal:

| Werk | Gepubliceerd bereik | Basis |
|------|---------------------|-------|
| Corpuscuratie (50–150 items) | $2.500–6.000 | $50–65/uur, tweetalige spreektijd |
| Beoordeling van methode-uitvoer | $500–1.500 | Zelfde uurtarieven |

Een volledig corpus kost een spreker traditioneel ongeveer 80 uur; de geplande agentondersteunde workflow (zinnen opstellen en opmaken wordt door tooling afgehandeld, vertalen altijd door een mens) is ontworpen om dat terug te brengen naar 30–40 uur — minder uren repetitief werk, hetzelfde uurtarief, waarbij de spreker alleen de onderdelen doet die werkelijk een mens vereisen.

### De metrics valideren

Voordat geautomatiseerde scores iets betekenen, moeten sprekers ze toetsen aan menselijk oordeel. Het [Sprekervalidatieprotocol](/docs/specifications/speaker-validation) publiceert de exacte taken, uren en vergoeding:

| Taak | Tijd | Vergoeding per spreker |
|------|------|------------------------|
| A — Beoordeel 200 machinevertaingen op adequaatheid en vloeiendheid | ~8 uur | $400–520 CAD |
| B — Beoordeel 50 "equivalente" vertaalparen | ~2 uur | $100–130 CAD |
| C — Beoordeel 100 woorden die de morfologische analysator heeft afgewezen | ~1,5 uur | $75–100 CAD |

Een spreker die alle drie uitvoert, verbindt zich aan ongeveer 11,5 uur verspreid over twee tot vier weken voor **$575–750 CAD**. De volledige validatieronde met drie sprekers kost het project $1.475–1.920 — en dat is precies het punt: sprekervalidatie is een kleine kostenpost voor het project en mag nooit de plek zijn waar kosten worden "bespaard."

### Prijsclaims beoordelen

Er wordt geen prijs uitgekeerd op basis van geautomatiseerde scores alleen. De [Founder's Prize](/docs/specifications/prizes) ($10.000 CAD, Engels→Plains Cree) vereist dat ten minste twee tweetalige sprekers onafhankelijk van elkaar een gestratificeerde steekproef van ten minste 30 uitvoerresultaten beoordelen, en dat 70% of meer wordt beoordeeld als "aanvaardbaar" of "uitstekend." Die beoordeling is betaald sprekerwerk tegen dezelfde tarieven — en het is ook een drempel: sprekers kunnen een prijsclaim torpederen, en dat is bewust zo ontworpen.

## Hoe het schaalt met wedstrijden

Het model is zo opgebouwd dat de sprekervergoeding meegroeit met het platform in plaats van erdoor te worden verdund:

- **Elke nieuwe taal begint met een betaalde corpusopdracht.** De gepubliceerde oprichtingskosten per taal ($3.350–8.500 alles inbegrepen) bestaan grotendeels uit sprekervergoeding — de grootste afzonderlijke component, bewust zo.
- **Elke nieuwe prijzenpot brengt zijn eigen betaalde beoordeling mee.** Elke gesponsorde wedstrijd die het [prijssjabloon](/docs/specifications/prizes#4-future-prize-pools) volgt, draagt dezelfde gemeenschapsvalidatievereiste met zich mee, wat betekent dat elke wedstrijd sprekerbeoordelingswerk voor die taal financiert.
- **Geïmplementeerde methoden financieren doorlopende beoordeling.** Wanneer een gemeenschapseigen methode API-inkomsten genereert, stroomt 90% naar de bestuursorganisatie van de gemeenschap ([het economisch model](/docs/sovereignty/economic-model)), die dit naar eigen inzicht kan aanwenden voor voortdurende beoordeling, corpusgroei en taalprogramma's. Die toewijzing is de beslissing van de gemeenschap, niet de onze.

## Wat wij *niet* hebben beloofd

Eerlijkheid vereist dat de grenzen worden aangegeven:

- De bovenstaande tarieven zijn de gepubliceerde tarieven voor het huidige Plains Cree-werk. Tarieven voor toekomstige talen worden vastgesteld samen met de partnergemeenschap en op dezelfde manier gepubliceerd — in de specificaties, vóór het werk begint.
- Het vliegwiel (inkomsten → gemeenschap → meer betaald werk) vereist externe financiering om op gang te komen en is nog niet zelfvoorzienend. Het [economisch model](/docs/sovereignty/economic-model) beschrijft het mechanisme, niet een garantie.
- "Eerlijk betaald" is noodzakelijk maar niet voldoende. Betaling maakt een project op zichzelf niet niet-extractief — eigendom en zeggenschap doen dat, en daarom is vergoeding ingebed in de [soevereiniteitsarchitectuur](/docs/sovereignty/data-sovereignty) in plaats van die te vervangen.

---

## Wat dit voor u betekent

:::info Als u een gemeenschapslid bent
Als u tweetalig bent in een ondervertegenwoordigde taal en het Engels, is uw oordeel de meest waardevolle input in dit systeem, en de gepubliceerde voorwaarden zijn: $50–65 CAD/uur, flexibele planning, betaling binnen twee weken, naamsvermelding op uw voorwaarden, en het recht om uw bijdragen in te trekken. Programmeerkennis is niet vereist. Begin met [Voor taalgemeenschappen](/docs/community/for-language-communities) of het [Sprekervalidatieprotocol §7](/docs/specifications/speaker-validation#7-how-to-get-started).
:::

:::info Als u een onderzoeker bent
Begroot sprekervergoeding als een eersteklas onderzoekskosten — de gepubliceerde cijfers ($1.475–1.920 voor een metriekvalidatieronde; $2.500–6.000 voor corpuscuratie) zijn klein naar maatstaven van subsidies en ze zijn wat geautomatiseerde scores verdedigbaar maakt. De [Corpuspartnerschapsstrategie](/docs/specifications/corpus-partnership) laat zien hoe een academische afdeling hierin kan instappen met ingebouwd gefinancierd sprekerwerk.
:::

:::info Als u een ontwikkelaar bent
U profiteert van betaald sprekerwerk zelfs als u het nooit financiert: gevalideerde metrics zijn wat uw leaderboardscore betekenisvol maakt, en betaalde gemeenschapsbeoordeling is wat er staat tussen uw methode en een prijs. Als u wint, kunt u ervan uitgaan dat sprekers zijn betaald om uw uitvoer te onderzoeken — en verwacht dat [het eigendom van uw methode wordt overgedragen](/docs/sovereignty/ownership-transfer) aan de gemeenschap wier taal het dient.
:::

## Zie ook

- [Vertaling is geen revitalisering](/docs/perspectives/translation-is-not-revitalization) — waarom sprekersgezag alles omlijst
- [Fouten rapporteren en correcties in eigendom nemen](/docs/perspectives/reporting-errors-and-owning-corrections) — sprekersgezag ook na de benchmark
- [Benchmarkspecificatie §10](/docs/specifications/benchmark#10-cost-framework) — het volledige kostenraamwerk waaruit deze cijfers afkomstig zijn