---
sidebar_position: 3
title: "Van Benchmark naar Dagelijks Gebruik: Het Post-Editing Traject"
slug: '/perspectives/from-benchmark-to-daily-use'
description: "Hoe een gebenchmarkte vertaalmethode een communityvertaalworkflow wordt: machineconcept, post-editing door een moedertaalspreker, gepubliceerde tekst — met eerlijke kwaliteitsdrempels bij elke stap."
related:
  - label: "Deploy to Production"
    to: /docs/getting-started/deploy-to-production
    kind: guide
    note: "From proven method to live translation"
  - label: "Cookbook: Partial Translation (Human + Machine)"
    to: /docs/tutorials/partial-translation
    kind: cookbook
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The quality thresholds behind the path"
  - label: "Translation Is Not Revitalization"
    to: /docs/perspectives/translation-is-not-revitalization
    kind: position
---
# Van Benchmark naar Dagelijks Gebruik: Het Nabewerkingspad

> **De korte versie.** Een leaderboard-score is geen product. Het pad van "deze methode scoort 0,78" naar "het bandkantoor publiceert wekelijks documenten in de taal" loopt langs precies één workflow: de machine produceert een concept, een vloeiende spreker corrigeert het, en alleen de gecorrigeerde tekst wordt gepubliceerd. Elke kwaliteitsdrempel in onze specificaties is gekalibreerd op die workflow — niet op onbeheerde machine-uitvoer, die wij voor geen enkele taal op dit platform aanbevelen.

Mensen vragen soms wanneer een vertaalmethode "goed genoeg is om gewoon te gebruiken." Voor de talen die deze Arena bedient, zit daar een valkuil in. Het eerlijke antwoord is dat de lat die het waard is om na te streven niet "goed genoeg om ongereviewd te publiceren" is — maar **"goed genoeg dat het nakijken van een concept sneller gaat dan vertalen vanaf nul."** Die lat ligt veel lager, is meetbaar, en het halen ervan verandert wat een gemeenschapsvertaalbureau in een week kan produceren.

---

## De workflow, van begin tot eind

```
 English source document
        │
        ▼
 Machine draft  ←  a benchmarked, community-owned method
        │
        ▼
 Fluent-speaker post-edit  ←  the human gate; nothing skips it
        │
        ▼
 Published text  ←  carries human approval, not a machine score
        │
        ▼
 (Optional, community-controlled) corrections become
 data that improves the next version of the method
```

Drie dingen om op te letten:

1. **De machine publiceert nooit.** De eenheid van uitvoer is een concept. De correctieronde van de spreker is geen kwaliteitsborging die achteraf wordt toegevoegd — het ís de workflow.
2. **De tijd van de spreker is de te optimaliseren resource.** Een methode is beter dan een andere methode precies voor zover ze de spreker minder te corrigeren overlaat. Onderzoek naar nabewerking voor goed-geresourcede talen laat consistent zien dat het sneller gaat dan vertalen vanaf nul bij matige MT-kwaliteit (Plitt & Masselot 2010; Green, Heer & Manning 2013, beide geciteerd met links in [Vertaling Is Geen Revitalisering](/docs/perspectives/translation-is-not-revitalization)). Of dat geldt voor polysynthetische talen is precies wat de benchmark bestaat om te achterhalen — wij behandelen het als een hypothese die per taal geverifieerd moet worden, niet als een aanname.
3. **De feedbacklus is in eigen beheer.** Elk gecorrigeerd document is potentiële trainings- en coachingsdata — en het behoort toe aan de gemeenschap, om terug te voeden (of niet) op hun eigen voorwaarden onder de [datasouvereiniteits](/docs/sovereignty/data-sovereignty)regels. Het feedbackmechanisme is een ontwerpdoel van het platform, maar nog geen gebouwde functie; zie [Fouten Melden en Correcties in Eigen Beheer Houden](/docs/perspectives/reporting-errors-and-owning-corrections) voor hoe correcties en herkomst bedoeld zijn te werken.

## Wat de kwaliteitsniveaus betekenen voor dagelijks gebruik

Het leaderboard beoordeelt methoden op een samengestelde score van geautomatiseerde metrics ([Scoringsspecificatie](/docs/specifications/scoring)), en de scores worden gekoppeld aan benoemde niveaus. Hier volgt de eerlijke vertaling van die niveaus naar dagelijks-gebruikstermen:

| Niveau (composite) | Wat het betekent voor het nabewerkingspad |
|---|---|
| **Baseline** (0,00–0,30) | Niet bruikbaar voor wat dan ook. De uitvoer is grotendeels niet de doeltaal. Alleen nuttig als onderzoeksbodem. |
| **Emerging** (0,30–0,50) | Nog steeds geen concepttool. Correcte fragmenten verschijnen, maar een spreker zou meer tijd kwijt zijn aan corrigeren dan aan vers schrijven. |
| **Functional** (0,50–0,70) | Het eerste niveau waarbij nabewerking *mogelijk* sneller gaat dan vertalen vanaf nul voor eenvoudige teksten — de moeite waard om te piloten met een spreker, maar niet om op te vertrouwen. Frequente morfologische fouten blijven aanwezig. |
| **Deployable** (0,70–0,85) | Het doelniveau voor de bovenstaande workflow: concepten waarbij de meeste morfologie correct is en een vloeiende spreker zinvol sneller kan corrigeren dan opnieuw vertalen. **"Deployable" betekent inzetbaar *in een nabewerkingsworkflow* — nooit "publiceer zonder review."** |
| **Fluent** (0,85–1,00) | Benadert competente menselijke vertaling; fouten zijn zeldzaam en gering. De reviewronde blijft — ze wordt alleen sneller. |

Twee structurele eerlijkheidsregels staan bovenop deze tabel, rechtstreeks uit de [Benchmarkspecificatie §5 en §7](/docs/specifications/benchmark#5-quality-tiers):

- **Geautomatiseerde niveaus zijn voorlopige labels, geen uitspraken.** Het zijn nominaties voor menselijke review. De drempelwaarden worden opnieuw gekalibreerd naarmate sprekersvalidatiedata zich opstapelt, en ze kunnen anders uitvallen voor verschillende talen.
- **Geen enkele methode kan Deployable of hoger claimen zonder gemeenschapsreview.** Een gestratificeerde steekproef van de uitvoer gaat naar tweetalige sprekers, die elke vertaling beoordelen als *afwijzen / globaal / acceptabel / uitstekend*. De bestuursorganisatie — niet het leaderboard — beslist of de methode doorstroomt.

Ter vergelijking: de drempel voor de [Founder's Prize](/docs/specifications/prizes) (composite ≥ 0,80, ≥99% morfologisch geldige woorden, ≥70% door sprekers beoordeeld als acceptabel-of-beter) beschrijft een methode waarvan de resterende fouten *echte taalfouten* zijn — verkeerde verbuiging, geen gefabriceerde woorden. Dat is wat "een concept dat een spreker zijn tijd waard is" er in cijfers uitziet.

## Van een winnende methode naar een werkend bureau

Stel dat een methode die poorten passeert. De resterende stappen zijn organisatorisch, en ze zijn gespecificeerd in plaats van geïmproviseerd:

1. **Eigendom wordt overgedragen.** De code van de methode wordt eigendom van de bestuursorganisatie van de gemeenschap — de ontwikkelaar behoudt naamsvermelding en publicatierechten ([Eigendomsoverdracht](/docs/sovereignty/ownership-transfer)).
2. **De methode wordt een dienst.** Ze wordt verpakt als een plugin en aangeboden via het deploymentplatform, waarbij de gemeenschap de toegang, prijsstelling en toegestane toepassingen beheert ([Implementeren naar Productie](/docs/getting-started/deploy-to-production)).
3. **Vertalers integreren het in hun werkdag.** Een vertaalbureau koppelt zijn bestaande documentworkflow aan de API van de methode: brontekst in, concept uit, nabewerken, publiceren. De gepubliceerde tekst draagt de naam en het gezag van de vertaler — de machine is een hulpmiddel op hun bureau, zoals een woordenboek.
4. **Inkomsten volgen gebruik.** Externe ontwikkelaars die de methode gebruiken betalen op basis van verbruik, en 90% van die inkomsten stroomt naar de bestuursorganisatie ([Het Economisch Model](/docs/sovereignty/economic-model)) — die daarmee meer vertaaluren kan financieren en zo de cirkel sluit.

## Waar dit vandaag staat

Ronduit gezegd: het volledige pad is van begin tot eind gespecificeerd en gedeeltelijk gebouwd. De evaluatieharnas, metrics, run cards en het publieke leaderboard bestaan; het Plains Cree-ontwikkelingscorpus en een actieve prijs bestaan; het deploymentplatform bestaat. De gemeenschapsreview-interface, de evaluatiesandbox en de feedbacklus voor gecorrigeerde teksten zijn gespecificeerd maar nog niet operationeel — de specificaties markeren ze als gepland, en wij doen dat ook. Geen enkele methode heeft tot nu toe de volledige reis van benchmark naar dagelijks gemeenschapsgebruik voltooid. Die reis is de definitie van succes van het project, en dat is precies waarom wij dat niet vroegtijdig zullen claimen.

---

## Wat dit voor u betekent

:::info Als u een gemeenschapslid bent
Een "Deployable"-badge op een leaderboard betekent nooit dat een machine onbeheerd in uw taal zal publiceren — het betekent dat een conceptgenerator klaar kan zijn om *auditie te doen* voor uw vertalers, op uw voorwaarden, met uw sprekers als beoordelaars (betaalde — zie [Hoe Sprekers Betaald Worden](/docs/perspectives/how-speakers-get-paid)). Als uw gemeenschap een vertaalbureau heeft, is de relevante vraag die u aan ons kunt stellen: "hoe zou een pilot eruitzien, en wie beoordeelt de uitvoer?"
:::

:::info Als u een onderzoeker bent
De nabewerkingsframing verandert wat het waard is te meten: tijd-tot-acceptabele-tekst met een spreker in de lus, niet alleen de composite score. De metrics van de Arena zijn proxies daarvoor ([Scoringsspecificatie §1](/docs/specifications/scoring)), en per-taal nabewerkingsstudies voor morfologisch complexe talen zijn een open onderzoekslacune die deze infrastructuur is ontworpen te ondersteunen.
:::

:::info Als u een ontwikkelaar bent
Optimaliseer voor de redacteur, niet voor de metric. Een methode die echte woorden produceert met af en toe een verkeerde verbuiging is in seconden te corrigeren door een spreker; een methode die plausibel ogende vormen hallucineert vergiftigt de hele workflow — en dat is waarom morfologische geldigheid hier zo streng wordt bewaakt. Begin bij [Een Methode Indienen](/docs/getting-started/submit-a-method), en lees de [Methode-interface](/docs/specifications/methods) voor wat u uiteindelijk overdraagt als u wint.
:::

## Zie ook

- [Vertaling Is Geen Revitalisering](/docs/perspectives/translation-is-not-revitalization) — waarom de menselijke poort het punt is, niet een beperking
- [Fouten Melden en Correcties in Eigen Beheer Houden](/docs/perspectives/reporting-errors-and-owning-corrections) — wat er gebeurt als de gepubliceerde tekst toch onjuist is
- [Benchmarkspecificatie §7](/docs/specifications/benchmark#7-human-validation) — de menselijke validatiepoort, formeel beschreven