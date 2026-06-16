---
sidebar_position: 8
title: "Prijsspecificatie"
slug: '/specifications/prizes'
related:
  - label: "How Speakers Get Paid"
    to: /docs/perspectives/how-speakers-get-paid
    kind: position
    note: "The plain-language version of these numbers"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
---
# Prijsspecificatie

> **Doel.** Dit document definieert de prijsfondsstructuur, drempelvoorwaarden, het claimproces en de regels voor de MT Eval Arena. Het specificeert precies wat "in staat tot machinevertaling" betekent in meetbare termen, en onder welke voorwaarden prijsgeld wordt uitgekeerd. Dit document verwijst naar SCORING_SPEC voor metriekdefinities en BENCHMARK_SPEC voor het evaluatieprotocol — het dupliceert deze niet.
>
> **Status:** ACTIEF. De Stichtersprijs (§2.1) is gefinancierd en actief.
>
> Laatst bijgewerkt: 2026-06-04

---

## 1. Filosofie

### 1.1 Prijzen Belonen Doorbraken, Geen Deelname

Prijsgeld wordt alleen uitgekeerd wanneer een methode aantoonbaar een gedefinieerde capaciteitsdrempel bereikt. Er zijn geen deelnameprijzen, onderscheidingen voor de tweede plaats of troostuitkeringen. Als niemand de lat haalt, wordt niemand betaald. Dit is bewust zo ontworpen — het betekent dat sponsors alleen betalen voor resultaten die daadwerkelijk werken.

### 1.2 Gemeenschapsvalidatie Is Niet Onderhandelbaar

Geautomatiseerde metrieken zijn benaderingen (SCORING_SPEC §1.1). Een methode kan goed scoren op chrF++ en FST-acceptatie terwijl de uitvoer produceert die geen enkele spreker zou accepteren. **Elke prijsclaim vereist gemeenschapsvalidatie** — tweetalige sprekers moeten bevestigen dat de uitvoer bruikbaar is. Dit is de menselijke validatiepoort (BENCHMARK_SPEC §7).

### 1.3 Eigendomsoverdracht Is Onderdeel van de Overeenkomst

Methoden die een prijs claimen, zijn onderworpen aan de eigendomsoverdrachtclausule (BENCHMARK_SPEC §8.3). De ontwikkelaar behoudt de attributie- en publicatierechten. De bestuursorganisatie verkrijgt het recht om de methode te gebruiken, te wijzigen, te distribueren en te monetariseren voor hun taal. Dit is geen straf — dit is het doel. Prijsgeld financiert de creatie van technologie die toebehoort aan de taalgemeenschap.

### 1.4 Anti-Gaming

Prijsdrempels worden gedefinieerd ten opzichte van **goudstandaard-evaluatie** (geheime testset, uitgevoerd door de bestuursorganisatie in een sandbox). Ontwikkelaars zien de testdata nooit. Dit is architecturaal afgedwongen — geen beleid dat berust op vertrouwen. Zie BENCHMARK_SPEC §8.2.

### 1.5 Corpuslicenties: Niet-Commerciële Corpora Blijven Buiten de Prijsbaan

Sommige corpora die tijdens de methode-ontwikkeling worden gebruikt, hebben niet-commerciële licenties — zo is het EdTeKLA Cree Language Textbook-corpus bijvoorbeeld **CC BY-NC-SA 4.0**. Deze corpora zijn **uitsluitend bestemd voor de onderzoeks-/ontwikkelingsbaan**:

1. **Goudstandaard-prijscorpora mogen geen NC-gelicentieerde corpusinhoud bevatten.** Goudstandaard-testsegmenten zijn door de gemeenschap in opdracht gegeven originelen (zie Corpus Partnership Strategy) — door mensen geschreven voor de prijs, met rechten die vanaf het begin zijn vrijgegeven voor evaluatie en commerciële inzet.
2. **Een methode die een prijs claimt, mag geen NC-gelicentieerde corpusinhoud bevatten** (bijv. als coachingdata, ingebedde voorbeelden of opzoektabellen). De overgedragen methode is bedoeld voor commerciële inzet door de bestuursorganisatie (BENCHMARK_SPEC §8.3, Method Submission Agreement §6); NC-gelicentieerde inhoud daarin zou die inzet onmogelijk maken.
3. **Ontwikkelaars mogen NC-gelicentieerde corpora vrijelijk gebruiken voor ontwikkeling en zelfevaluatie** — dat is waarvoor de ontwikkelingsbaan bedoeld is. De beperking geldt voor wat wordt ingediend en ingezet, niet voor hoe een ontwikkelaar leert.

### 1.6 Afhankelijkheidsklassen Bepalen de Prijsgeschiktheid

Alle prijsevaluatie vindt plaats in een sandbox (§1.4), en prijswinnende methoden worden overgedragen aan de bestuursorganisatie (§1.3). Beide feiten leggen dezelfde beperking op: **alles waarvan een methode afhankelijk is, moet iets zijn waarvoor de ontwikkelaar het recht heeft het in de sandbox te plaatsen en aan de gemeenschap over te dragen.** Elke inzending declareert een afhankelijkheidsklasse — gedefinieerd in de [Method Interface-specificatie](/docs/specifications/methods#method-validity-and-dependency-classes), met toelaatbaarheidsvoorwaarden in Method Submission Agreement §2.6 — en de geschiktheid volgt de klasse:

| Afhankelijkheidsklasse | Prijsgeschikt? | Voorwaarden |
|------------------------|---------------|-------------|
| **S** — zelfstandig | ✅ Ja | Geen, buiten de drempelvoorwaarden in §2 |
| **O** — open extern (bijv. AGPL FST gespiegeld bij inzending) | ✅ Ja | Artefacten vastgezet en opgenomen in de inzending; licenties staan gemeenschapsoverdracht toe; copyleft-voorwaarden worden gehandhaafd (de gemeenschap ontvangt dezelfde rechten die de licentie aan iedereen verleent) |
| **A1** — vervangbare LLM-inferentie | ⚠️ Voorwaardelijk | Model gedeclareerd, vastgezet en vervangbaar (moet draaien op een door de gemeenschap gehost open-weight model); evaluatie verloopt via de sandbox LLM-gateway (🔲 gepland — A1-methoden kunnen geen goudstandaard-scores produceren totdat de gateway operationeel is); overdracht omvat het volledige recept (prompts, coaching, code), niet het model |
| **A2** — niet-vervangbare externe data-/service-API | ❌ Nog niet | Niet geschikt totdat de rechthebbende toestemming verleent voor sandbox-opname en overdracht. Toegestaan op het open leaderboard met een zichtbare vlag "externe afhankelijkheid" |
| **X** — gebundelde inhoud zonder rechten | ❌ Nooit | Ontoelaatbaar in elke baan |

De klasse van een methode is de meest beperkende klasse onder de gedeclareerde afhankelijkheden. Niet-gedeclareerde afhankelijkheden van welke klasse dan ook zijn diskwalificerend (§5).

---

## 2. Actieve Prijsfondsen

### 2.1 De Stichtersprijs — EN→Plains Cree (nêhiyawêwin)

| Veld | Waarde |
|------|--------|
| **Prijsfonds** | **$10.000 CAD** |
| **Taalpaar** | Engels → Plains Cree (EN→CRK) |
| **Gefinancierd door** | Oprichter van het Champollion-project |
| **Status** | **ACTIEF** — inzendingen worden geaccepteerd |
| **Opent** | Wanneer het goudstandaard-corpus en de bestuursorganisatie beschikbaar zijn |
| **Vervalt** | Geen vervaldatum. De prijs blijft actief totdat hij geclaimd of expliciet ingetrokken wordt. |

#### Drempelvoorwaarden

Een methode claimt de Stichtersprijs door **ALLE** volgende voorwaarden gelijktijdig te vervullen:

| # | Voorwaarde | Metriek | Drempel | Motivering |
|---|------------|---------|---------|------------|
| 1 | **Composietscore** | `composite` (SCORING_SPEC §4) | **≥ 0,80** | Tussen Inzetbaar (0,70) en Vloeiend (0,85). Vereist hoge kwaliteit over alle metriekdimensies — niet alleen morfologische geldigheid. |
| 2 | **FST-acceptatie** | `fst_acceptance_rate` (SCORING_SPEC §2.2) | **≥ 0,99 (99%+)** | Vrijwel alle uitvoerwoorden moeten morfologisch geldige vormen zijn die door de GiellaLT FST worden herkend. De tolerantie van 1% is bedoeld voor randgevallen (eigennamen, neologismen, leenwoorden) die de FST legitiem mogelijk niet dekt. Dit is de bepalende kwaliteitspoort voor polysynthetische MT — als de FST meer dan 1% van de woorden afwijst, produceert de methode vormen die niet bestaan in de taal. Het hele doel van deze prijs is het verkrijgen van een systeem dat de taal niet verminkt. |
| 3 | **chrF++** | `chrf_plus_plus` (SCORING_SPEC §2.1) | **≥ 55,0** | Overlapping van karakter-n-grammen moet 55 overschrijden op de schaal van 0–100. Zorgt voor gelijkenis op oppervlakteniveau met referentievertaling, niet alleen morfologische geldigheid. |
| 4 | **Gemeenschapsvalidatie** | Menselijke beoordeling (BENCHMARK_SPEC §7) | **≥ 70% "acceptabel" of "uitstekend"** | Een gestratificeerde steekproef van uitvoer (≥30 vermeldingen over moeilijkheidsgraden 2–5) wordt beoordeeld door ≥2 tweetalige CRK-sprekers. Ten minste 70% van de beoordeelde vermeldingen moet een beoordeling "acceptabel" of "uitstekend" ontvangen. |
| 5 | **Goudstandaard-evaluatie** | Sandbox-uitvoering (BENCHMARK_SPEC §8.2) | **Vereist** | Alle geautomatiseerde metrieken moeten worden berekend ten opzichte van het `gold_standard`-corpussegment, uitgevoerd door de bestuursorganisatie in een sandbox-omgeving. Scores op de ontwikkelingsset tellen niet mee. |
| 6 | **Reproduceerbaarheid** | Vingerafdrukovereenkomst (BENCHMARK_SPEC §3.8) | **±2%** | De bestuursorganisatie moet de methode opnieuw kunnen uitvoeren en scores bereiken binnen ±2% van de ingediende run card. |

> **Waarom 99%+ FST?** Het centrale probleem bij machinevertaling voor polysynthetische talen is hallucinatie — LLM's produceren tekenreeksen die *eruitzien* als de doeltaal maar morfologisch ongeldig zijn. Een methode die 95% geldige uitvoer produceert, heeft nog steeds 5% gefabriceerde woorden — onaanvaardbare ruis voor elk productiegebruik. De drempel van 99%+ vereist vrijwel nul hallucinatie, terwijl ruimte wordt gelaten voor het zeldzame randgeval (een eigennaam die de FST niet kent, een legitiem neologisme). Als een methode geen 99%+ FST-acceptatie kan bereiken, heeft zij het probleem niet opgelost.
>
> **Waarom 0,80 composiet?** Dit ligt tussen Inzetbaar (0,70) en Vloeiend (0,85). Een methode met 0,80 en 99%+ FST-acceptatie produceert uitvoer waarbij vrijwel elk woord een echt Cree-woord is *en* de algehele vertaalkwaliteit hoog is over oppervlakte-, structurele en semantische dimensies. De gemeenschapsvalidatiepoort (voorwaarde #4) zorgt ervoor dat dit geen louter metriekoptimalisatie is — sprekers moeten bevestigen dat de uitvoer daadwerkelijk bruikbaar is.

#### Wat Deze Drempel in de Praktijk Betekent

Bij composiet ≥ 0,80 met FST ≥ 0,99 en chrF++ ≥ 55 zou een tweetalige spreker doorgaans het volgende zien:

- **Vrijwel elk** uitvoerwoord is een echt Cree-woord (FST valideert 99%+ — vrijwel nul gehallucineeerde vormen)
- Grote grammaticale categorieën (persoon, getal, tijd) zijn in de meeste vermeldingen correct
- Woordvolgorde is over het algemeen natuurlijk
- Betekenis wordt betrouwbaar bewaard
- Resterende fouten zijn echte taalfouten (verkeerde vervoeging, onjuiste obviatie, animaciteitsfouten) — geen gefabriceerde woorden
- Een vloeiende spreker kan de uitvoer gebruiken als een concept van hoge kwaliteit en dit aanzienlijk sneller corrigeren dan vanaf nul vertalen

Dit is een systeem dat **de taal niet verminkt.** Het is misschien niet perfect, maar elk woord dat het produceert is een echt woord. Dat is de minimumdrempel voor respectvolle machinevertaling van een polysynthetische taal.

---

## 3. Prijsclaimproces

### 3.1 Inzending

1. De ontwikkelaar dient zijn volledige, uitvoerbare methode in bij de bestuursorganisatie:
   - Alle broncode
   - Alle afhankelijkheden (coachingdata, woordenboeken, FST-configuraties, prompts)
   - Installatie- en uitvoeringsinstructies
   - Een README die de aanpak van de methode beschrijft
   - Een run card van de ontwikkelingsset met geschatte scores (voor voorafgaande screening)

2. De ontwikkelaar ondertekent de deelnemingsvoorwaarden, waaronder:
   - Eigendomsoverdrachtclausule (BENCHMARK_SPEC §8.3)
   - Verklaring van geen training op evaluatiedata
   - Reproduceerbaarheidsverbintenis

### 3.2 Evaluatie

1. De bestuursorganisatie installeert en voert de methode uit in een sandbox-harnas ten opzichte van het `gold_standard`-corpus
2. Geautomatiseerde metrieken worden berekend (composiet, FST, chrF++, enz.)
3. Als aan de geautomatiseerde drempels wordt voldaan (voorwaarden 1–3), gaat de bestuursorganisatie over tot gemeenschapsbeoordeling
4. Als aan de geautomatiseerde drempels NIET wordt voldaan, ontvangt de ontwikkelaar scores en feedback. Er wordt geen gemeenschapsbeoordeling gestart.

### 3.3 Gemeenschapsbeoordeling

1. Een gestratificeerde steekproef van uitvoer (≥30 vermeldingen, over moeilijkheidsgraden 2–5) wordt voorgelegd aan tweetalige sprekers
2. Ten minste 2 onafhankelijke beoordelaars beoordelen elke vermelding
3. Beoordelingsschaal: **afwijzen** / **globale betekenis** / **acceptabel** / **uitstekend**
4. Als ≥70% van de vermeldingen "acceptabel" of "uitstekend" ontvangt van beide beoordelaars, slaagt de gemeenschapsvalidatie

### 3.4 Uitbetaling

1. Aan alle 6 voorwaarden is voldaan
2. De bestuursorganisatie bevestigt het resultaat
3. De prijs wordt uitbetaald binnen 30 dagen na bevestiging
4. Eigendom van de methode wordt overgedragen conform BENCHMARK_SPEC §8.3
5. Het resultaat wordt gepubliceerd op het leaderboard met verificatieniveau "Community Validated"

### 3.5 Meerdere Inzendingen

- Dezelfde ontwikkelaar/hetzelfde team mag meerdere keren indienen
- Elke inzending wordt onafhankelijk geëvalueerd
- Als een methode wordt verbeterd en opnieuw ingediend, telt alleen de meest recente run card
- De prijs wordt toegekend aan de **eerste** methode die alle drempels haalt — hij wordt niet gedeeld

### 3.6 Teaminzendingen

- Teams en Elder-jeugdparen zijn geschikt
- De verdeling van de prijs binnen een team is de verantwoordelijkheid van het team
- Alle teamleden moeten de deelnemingsvoorwaarden ondertekenen
- Attributie op het leaderboard vermeldt alle teamleden

---

## 4. Toekomstige Prijsfondsen {#4-future-prize-pools}

De Stichtersprijs is het startpunt. Aanvullende prijsfondsen worden gefinancierd door sponsors. Elk nieuw prijsfonds wordt gedocumenteerd als een nieuwe subsectie van §2 met zijn eigen:

- Prijsbedrag en valuta
- Taalpaar
- Sponsorattributie
- Drempelvoorwaarden (die kunnen afwijken van de Stichtersprijs)
- Vervaldatum (indien van toepassing)
- Eventuele bijzondere voorwaarden

### 4.1 Sponsorprijssjabloon

Sponsors financieren prijsfondsen voor elk bedrag. Voorgestelde niveaus:

| Niveau | Bedrag | Voorgestelde Drempel |
|--------|--------|----------------------|
| **Zaad** | $5.000–$15.000 | Inzetbaar (composiet ≥ 0,70) + gemeenschapsvalidatie |
| **Doorbraak** | $25.000–$50.000 | Vloeiend (composiet ≥ 0,85) + gemeenschapsvalidatie |
| **Grote Prijs** | $100.000+ | Vloeiend + dekking van meerdere registers + integratie voor inzet |

Sponsors kunnen ook financieren:
- **Verbeteringsbounties** — vaste betaling voor elke verbetering van 5 punten in chrF++ ten opzichte van het huidige beste resultaat
- **Registerprijzen** — afzonderlijke onderscheidingen voor specifieke registers (formeel, ceremonieel, educatief)
- **Snelheidsprijzen** — beste kostengecorrigeerde score (SCORING_SPEC §6.3)

### 4.2 Prijsfonds-Escrow

Alle prijsgelden worden in escrow gehouden (beheerd door het project of een aangewezen trustee) totdat aan de drempelvoorwaarden is voldaan. Als een prijs vervalt zonder te zijn geclaimd, worden de middelen teruggestort aan de sponsor of omgeleid naar een nieuw prijsfonds naar goeddunken van de sponsor.

---

## 5. Diskwalificatie

Een inzending wordt gediskwalificeerd als:

1. **Training op evaluatiedata.** De methode is blootgesteld aan `gold_standard`- of `held_out`-corpusvermeldingen. (Architecturaal voorkomen door sandbox-uitvoering — maar als bewijs van contaminatie wordt gevonden, wordt het resultaat ongeldig verklaard.)
2. **Niet-reproduceerbaar.** De bestuursorganisatie kan scores niet reproduceren binnen ±2%.
3. **Niet-gedeclareerde of niet-geschikte afhankelijkheden.** De methode vereist runtime-toegang tot externe diensten buiten wat het afhankelijkheidsmanifest declareert, of de effectieve afhankelijkheidsklasse is A2 of X (§1.6). Gedeclareerde klasse A1 LLM-inferentie via de evaluatiegateway is toegestaan; elke andere runtime-netwerkafhankelijkheid — en elke niet-gedeclareerde afhankelijkheid van welke klasse dan ook — is diskwalificerend.
4. **Deelnemingsvoorwaarden niet ondertekend.** Alle teamleden moeten instemmen met eigendomsoverdracht.
5. **Gaming gedetecteerd.** Uitvoer is geoptimaliseerd voor de metriek in plaats van vertaalkwaliteit (gedetecteerd door gemeenschapsbeoordeling en/of anti-gamingcontroles conform BENCHMARK_SPEC §9.3).

---

## 6. Relatie tot Andere Specificaties

| Dit Document | Verwijst naar | Voor |
|--------------|--------------|------|
| §2 drempelvoorwaarden | SCORING_SPEC §4 (composiet), §2.1–2.2 (metrieken), §5 (niveaus) | Metriekdefinities en schaal |
| §2 gemeenschapsvalidatie | BENCHMARK_SPEC §7 | Menselijk beoordelingsprotocol |
| §3 sandbox-uitvoering | BENCHMARK_SPEC §8.2 | Soevereiniteitsmechanisme |
| §3 eigendomsoverdracht | BENCHMARK_SPEC §8.3 | IP-overdrachtsvoorwaarden |
| §1.6 afhankelijkheidsklassen | Method Interface-specificatie; Method Submission Agreement §2.6; BENCHMARK_SPEC §8.6 | Klassedefinities, toelaatbaarheidsvoorwaarden, sandbox-netwerkbeleid |
| §4 kostengecorrigeerde prijzen | SCORING_SPEC §6.3 | Kostengecorrigeerde formule |

---

## 7. Code–Specificatiesynchronisatie

### 7.1 Canonieke Bron

Dit document (`arena/website/docs/specifications/prize-spec.md`) is de canonieke bron voor:
- Prijsfondsdefinitiess (§2)
- Drempelvoorwaarden (§2.x)
- Claimproces (§3)
- Diskwalificatieregels (§5)

### 7.2 Implementatievereisten

Wanneer een prijsfonds wordt geactiveerd:
1. De leaderboard-UI moet actieve prijzen en hun drempelvoorwaarden weergeven
2. Run cards die voldoen aan de geautomatiseerde drempels (voorwaarden 1–3) moeten worden gemarkeerd voor gemeenschapsbeoordeling
3. Het veld `quality_tier` in het run card-schema legt het niveau al vast ("deployable", "fluent")
4. Er zijn geen nieuwe codewijzigingen in het harnas nodig — de prijsspecificatie is een beleidslaag bovenop de bestaande scoring

---

*Prijsstructuren moeten compatibel zijn met de eigendomsoverdrachtvoorwaarden. De winnaar kan de prijs claimen, maar de methode wordt eigendom van de bestuursorganisatie als deze het niveau Inzetbaar bereikt. Dit is bewust zo ontworpen — de prijs financiert de creatie van technologie die toebehoort aan de taalgemeenschap.*