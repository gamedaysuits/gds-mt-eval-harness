---
sidebar_position: 7
title: "Datasouvereiniteit"
description: "OCAP-, CARE- en Māori Data Sovereignty-principes voor de vertaling van inheemse talen. Waarom gemeenschapstoestemming voorafgaat aan inzet."
related:
  - label: "Ownership Transfer"
    to: /docs/sovereignty/ownership-transfer
    kind: doc
    note: "How control of language data moves to communities"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
---
# Gegevenssouvereiniteit

> **Samenvatting voor leidinggevenden.** Deze pagina legt de OCAP®-, CARE- en Te Mana Raraunga-principes voor gegevenssouvereiniteit uit en wat deze betekenen voor ontwikkelaars die vertaalmethoden bouwen voor inheemse talen. Behandelt wanneer toestemming van de gemeenschap vereist is, hoe de `api`-methode-architectuur van champollion gegevenssouvereiniteit ondersteunt, en de ethische verplichtingen van iedereen die werkt met inheemse taalkundige gegevens.

Machinevertaling voor inheemse talen roept vragen op die niet bestaan voor Frans of Japans. Wie is eigenaar van de trainingsgegevens? Wie bepaalt hoe een taalmodel spreekt? Wie beslist of een vertaling goed genoeg is om te publiceren?

**Het antwoord is altijd de gemeenschap.**

champollion is gebouwd om dit te ondersteunen. De `api`-methode houdt alle taalkundige bronnen server-side onder controle van de gemeenschap. Het plug-insysteem scheidt de methode van het hulpmiddel. Maar het hulpmiddel kan ethiek niet afdwingen — deze pagina legt de principes uit die u dient te volgen.

---

## OCAP®-principes

**OCAP** (Ownership, Control, Access, Possession) is een set principes ontwikkeld door het [First Nations Information Governance Centre](https://fnigc.ca/ocap-training/) (FNIGC) die vastleggen hoe First Nations-gegevens verzameld, beschermd, gebruikt en gedeeld dienen te worden.

| Principe | Wat het betekent voor vertaling |
|-----------|------------------------------|
| **Ownership** | De gemeenschap is eigenaar van haar taalkundige gegevens — woordenboeken, grammatica's, parallelle teksten, coachingbestanden en alle vertalingen die daaruit voortkomen. |
| **Control** | De gemeenschap bepaalt hoe haar taalgegevens worden gebruikt, wie toegang heeft en welke vertaalmethoden aanvaardbaar zijn. |
| **Access** | Gemeenschapsleden hebben het recht om hun eigen taalbronnen te raadplegen en te beheren, ongeacht waar deze zijn opgeslagen. |
| **Possession** | De fysieke gegevens (coachingbestanden, woordenboeken, modelgewichten) moeten zich bevinden op infrastructuur die de gemeenschap beheert — niet op een externe cloud. |

### Wat OCAP in de praktijk betekent

- **Publiceer geen vertalingen** van een inheemse taal zonder uitdrukkelijke toestemming van de gemeenschap.
- **Train geen modellen** op door de gemeenschap aangeleverde taalkundige gegevens zonder een gegevensdeling­sovereenkomst.
- **Scrape geen** taalbronnen van gemeenschappen van websites, sociale media of educatief materiaal.
- **Gebruik de `api`-methode** zodat prompts, coachinggegevens en woordenboeken op door de gemeenschap beheerde servers blijven. De champollion `api`-methode is een "domme doorvoer" — zij stuurt sleutels uit en ontvangt vertalingen terug. Alle taalkundige intellectuele eigendom blijft server-side.
- **Documenteer herkomst** — het `provenance`-veld in de [plug-inmanifest](https://champollion.dev/docs/reference/plugin-spec) dient elke gebruikte bron te vermelden, inclusief licentie en oorsprong.

:::warning OCAP® is een geregistreerd handelsmerk
OCAP® is een geregistreerd handelsmerk van het First Nations Information Governance Centre. Het is specifiek van toepassing op First Nations in Canada. De principes hebben bredere relevantie, maar het handelsmerk en de governance-autoriteit behoren toe aan FNIGC.
:::

---

## CARE-principes

De **CARE Principles for Indigenous Data Governance** zijn ontwikkeld door de [Global Indigenous Data Alliance](https://www.gida-global.org/care) (GIDA) als aanvulling op de FAIR-gegevensprincipes. FAIR stelt dat gegevens Findable, Accessible, Interoperable en Reusable moeten zijn. CARE stelt dat dit onvoldoende is — gegevensbeheer moet ook de rechten van inheemse volkeren centraal stellen.

| Principe | Toepassing |
|-----------|------------|
| **Collective Benefit** | Vertaalhulpmiddelen dienen in de eerste plaats de taalgemeenschap te baten. Leaderboard-scores zijn een middel om methoden te verbeteren, niet om commerciële waarde te onttrekken aan gemeenschapstalen. |
| **Authority to Control** | Gemeenschappen hebben de bevoegdheid om te bepalen hoe hun taalgegevens worden verzameld, gebruikt en gedeeld. Een hoge leaderboard-score verleent geen toestemming om vertalingen te publiceren. |
| **Responsibility** | Onderzoekers en ontwikkelaars die werken met inheemse taalgegevens hebben de verantwoordelijkheid om relaties op te bouwen, toestemming te verkrijgen en voordelen te delen. |
| **Ethics** | De rechten en het welzijn van inheemse volkeren moeten de primaire zorg zijn. Vertaalmethoden dienen te worden ontwikkeld *samen met* gemeenschappen, niet *over* hen. |

---

## Te Mana Raraunga — Māori-gegevenssouvereiniteit

**Te Mana Raraunga** is het [Māori Data Sovereignty Network](https://www.temanararaunga.maori.nz/). Het stelt dat Māori-gegevens — inclusief taalgegevens — een taonga (schat) zijn die onderworpen is aan de principes van het Verdrag van Waitangi en tikanga Māori (Māori gewoonterecht).

Kernprincipes:

| Principe | Betekenis |
|-----------|---------|
| **Rangatiratanga** (Gezag) | Māori hebben een inherent recht om gezag uit te oefenen over hun gegevens, inclusief taalgegevens. |
| **Whakapapa** (Relaties) | Gegevens hebben oorsprongen en verbindingen. Taalgegevens dragen de relaties en kennis van de mensen die ze hebben gecreëerd. |
| **Whanaungatanga** (Verplichtingen) | Degenen die Māori-gegevens bewaren of verwerken, hebben wederkerige verplichtingen jegens de gemeenschappen waaruit deze afkomstig zijn. |
| **Kotahitanga** (Collectief voordeel) | Māori-gegevens dienen te worden gebruikt voor het collectieve voordeel van Māori. |
| **Manaakitanga** (Wederkerigheid) | Het gebruik van Māori-gegevens dient zorg, respect en wederkerigheid te omvatten. |
| **Kaitiakitanga** (Beheerderschap) | Gegevensbeheerders hebben de plicht de gegevens te beschermen en te waarborgen dat deze op passende wijze worden gebruikt. |

Deze principes zijn van toepassing op te reo Māori (de Māori-taal) en op elk computationeel werk waarbij Māori-taalgegevens betrokken zijn.

---

## Wat dit betekent voor champollion-gebruikers

### Voor standaardtalen (Frans, Japans, Spaans...)

Gebruik champollion op de gebruikelijke wijze. Deze talen beschikken over grote, openbaar beschikbare corpora, gevestigde vertaal-API's en geen soevereiniteitskwesties. Vertaal, synchroniseer en publiceer naar eigen inzicht.

### Voor inheemse en laagbronnen-talen

De situatie is fundamenteel anders:

1. **Verkrijg eerst toestemming.** Voordat u een vertaalmethode bouwt voor een inheemse taal, dient u een relatie op te bouwen met de gemeenschap. Een methode die is gebouwd zonder betrokkenheid van de gemeenschap — hoe technisch indrukwekkend ook — mag niet worden gepubliceerd of verspreid.

2. **Gebruik de `api`-methode.** Host de vertaalpijplijn op door de gemeenschap beheerde infrastructuur. De `api`-methode in champollion is hiervoor ontworpen: zij stuurt sleutels en ontvangt vertalingen terug zonder de prompts, woordenboeken of coachinggegevens bloot te stellen die de methode doen werken.

    ```json title="Community-controlled setup"
    {
      "pairs": {
        "en:crk": {
          "method": "api",
          "endpoint": "https://api.community-server.example/translate"
        }
      }
    }
    ```

3. **Documenteer alles.** Gebruik het `provenance`-veld in uw plug-inmanifest om elke bron te vermelden, inclusief licentie en of deze is aangeleverd met toestemming van de gemeenschap.

4. **Scores zijn geen licenties.** Een hoge score op het leaderboard bewijst dat een methode technisch goed werkt. Het verleent geen toestemming om vertalingen te publiceren, de plug-in te verspreiden of de methode te commercialiseren. De gemeenschap beslist.

5. **Deel de methode, niet de gegevens.** Als u een techniek ontwikkelt die goed werkt (bijv. "FST-gated LLM met gecoachte prompts"), deel dan de *architectuur* en *aanpak* op het leaderboard. De gemeenschap behoudt de controle over de taalkundige gegevens die het laten werken voor hun specifieke taal.

---

## De `api`-methode en souvereiniteit

De `api` [vertaalmethode](https://champollion.dev/docs/guides/translation-methods) bestaat specifiek om gegevenssouvereiniteit te ondersteunen. Dit is de reden:

| Aspect | Andere methoden | `api`-methode |
|--------|--------------|-------------|
| **Waar prompts zich bevinden** | In de configuratiebestanden van champollion (zichtbaar voor alle ontwikkelaars) | Op de server van de gemeenschap (privé) |
| **Waar coachinggegevens zich bevinden** | In de `.champollion/coaching/`-map (vastgelegd in git) | Op de server van de gemeenschap (privé) |
| **Waar woordenboeken zich bevinden** | In de plug-inmap (verspreid met de plug-in) | Op de server van de gemeenschap (privé) |
| **Wie de pijplijn beheert** | Degene die `champollion sync` uitvoert | De gemeenschap die de API beheert |
| **Wat champollion ziet** | Alles | Sleutels in, vertalingen uit |

De `api`-methode is een bewuste architecturale keuze. Het is een "domme doorvoer" omdat het intellectuele eigendom — de taalkundige kennis, de grammaticaregels, de zorgvuldig samengestelde coachingvoorbeelden — toebehoort aan de gemeenschap, niet aan het hulpmiddel.

Zie [Een methode aanbieden via API](https://champollion.dev/docs/guides/serving-a-method) voor implementatiedetails.

---

## Casestudy: OMT-1600 en gegevenssouvereiniteit

Meta's OMT-1600 (maart 2026) biedt een concreet voorbeeld van waarom gegevenssouvereiniteit belangrijk is voor inheemse talen. OMT-1600 trainde vertaalmodellen voor 1.600 talen met behulp van:

- **CC-2000-Web**: Eentalige tekst die van het web is gescraped voor 2.000+ taalvarianten — verzameld zonder toestemming van de gemeenschap
- **Bijbelvertalingen**: Religieuze teksten gebruikt als parallelle trainings- en evaluatiegegevens voor de talen met de minste bronnen
- **MeDLEy**: Handmatig samengestelde bitekst — maar zonder gedocumenteerde OCAP®- of CARE-naleving
- **Terugvertaalde synthetische gegevens**: ~270 miljoen synthetische parallelle zinnen gegenereerd door de modellen zelf

Voor inheemse talen zoals Plains Cree (CRK) betekent dit:

| Principe | OMT-1600-praktijk | Impact |
|-----------|-------------------|--------|
| **Ownership** | Meta is eigenaar van de modellen en beslist hoe deze worden vrijgegeven | De gemeenschap heeft geen eigendomsbelang in de manier waarop hun taal wordt gemodelleerd |
| **Control** | Meta bepaalt de selectie van trainingsgegevens, modelarchitectuur en vrijgaveschema | De gemeenschap heeft geen inbreng over welke gegevens worden gebruikt of hoe de taal wordt weergegeven |
| **Access** | Modelgewichten zijn momenteel niet beschikbaar — "niet vrijgegeven vanwege factoren buiten de controle van de auteurs" | De gemeenschap heeft geen toegang tot, kan het model dat hun taal spreekt niet inspecteren of aanpassen |
| **Possession** | Alle gegevens en modellen bevinden zich op de infrastructuur van Meta | De gemeenschap kan de gegevens die zijn gebruikt om het model te trainen niet hosten, controleren of verwijderen |

OMT-1600 is een onderzoeksprestatie. Het is ook een voorbeeld van extractieve gegevenspraktijk: taalkundige gegevens werden verzameld van het web en religieuze teksten, verwerkt tot een model en gepubliceerd als een artikel — allemaal zonder betrokkenheid van de gemeenschap, toestemming of het delen van voordelen.

**Dit is precies het patroon dat de soevereiniteitsarchitectuur van champollion voorkomt.** De `api`-methode houdt taalkundig intellectueel eigendom op door de gemeenschap beheerde servers. Evaluatiecorpora worden aangeleverd met toestemming van de gemeenschap en opgeslagen onder beheer van gemeenschapssleutels. Prijswinnende methoden worden overgedragen aan het eigendom van de gemeenschap. Het verschil is niet technisch — het is ethisch en structureel.

:::note OMT-1600 is niet uniek verantwoordelijk
Dit patroon — webscraping gevolgd door modeltraining zonder toestemming van de gemeenschap — is standaardpraktijk in grootschalig meertalig NLP-onderzoek. OMT-1600 is een casestudy vanwege zijn schaal (1.600 talen) en recentheid (maart 2026), niet omdat het uniek extractief is. Dezelfde kritiek is van toepassing op NLLB-200, de meertalige inspanningen van Google en de meeste grootschalige MT-onderzoeken.
:::

---

## Verdere lectuur

- [First Nations Information Governance Centre — OCAP®](https://fnigc.ca/ocap-training/)
- [Global Indigenous Data Alliance — CARE-principes](https://www.gida-global.org/care)
- [Te Mana Raraunga — Māori Data Sovereignty Network](https://www.temanararaunga.maori.nz/)
- [USIDSN — United States Indigenous Data Sovereignty Network](https://usindigenousdata.org/)

---

## Zie ook

- [Een taal met weinig bronnen ondersteunen](/docs/community/low-resource-languages) — de technische handleiding met OCAP-context
- [Vertaalmethoden](https://champollion.dev/docs/guides/translation-methods) — de `api`-methode en hoe deze intellectueel eigendom beschermt
- [Een methode aanbieden via API](https://champollion.dev/docs/guides/serving-a-method) — het hosten van een door de gemeenschap beheerde pijplijn
- [Plug-inspecificatie](https://champollion.dev/docs/reference/plugin-spec) — het `provenance`-veld voor bronvermelding
- [Kookboek: FST-gated pijplijn](/docs/tutorials/fst-gated-pipeline) — het bouwen van een pijplijn die een gemeenschap zelf kan hosten