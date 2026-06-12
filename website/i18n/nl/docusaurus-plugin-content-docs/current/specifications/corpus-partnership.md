---
sidebar_position: 9
title: "Corpuspartnerschapsstrategie"
slug: '/specifications/corpus-partnership'
---
# Corpuspartnerschapsstrategie: Evaluatiecorpora Opzetten via Academische Taalkunde-afdelingen

> **Doel.** Dit document beschrijft de volledige werkwijze voor het opzetten van een evaluatiecorpus voor machinevertaling via een partnerschap met een taalkunde-afdeling. Het behandelt wat wij van de afdeling verwachten, hoe het corpus eruit moet zien, hoe het cryptografisch wordt verzegeld, hoe sandboxevaluatie werkt en wat de afdeling ervoor terugkrijgt. Dit is het document dat u meeneemt naar een vergadering met een potentiële academische partner.
>
> **Doelgroep.** Afdelingshoofden, hoofdonderzoekers, onderzoekscoördinatoren en directeuren van programma's voor inheemse talen aan universiteiten met actieve programma's voor taaldocumentatie of NLP.
>
> **Begeleidende documenten:**
> - [Sprekervalidatieprotocol](/docs/specifications/speaker-validation) — het verzoek aan tweetalige sprekers om bestaande vertalingen te *beoordelen* (kwaliteitsbeoordeling, lintervalidatie, FST-review)
> - [Benchmarkspecificatie](/docs/specifications/benchmark) — de volledige technische specificatie voor corpora, run cards en evaluatieprotocollen
> - [Gegevenssouvereiniteit](/docs/sovereignty/data-sovereignty) — OCAP®, CARE en waarom eigendomsoverdracht van belang is
>
> Laatst bijgewerkt: 2026-06-07

---

## 1. Wat Dit Partnerschap Oplevert

Een **verzegeld evaluatiecorpus**: een samengestelde verzameling parallelle tekstparen (brontaal → doeltaal) die de grondwaarheid vormt voor het meten van de kwaliteit van machinevertaling. Methoden worden in een sandbox getest aan de hand van dit corpus — ontwikkelaars zien de testdata nooit.

Het partnerschap levert drie artefacten op:

| Artefact | Wat het is | Wie het beheert |
|----------|-----------|-----------------|
| **Ontwikkelingscorpus** | 100–200+ openbare parallelle tekstparen voor methode-ontwikkeling | Openbaar gepubliceerd (CC BY-NC-SA 4.0 of gelijkwaardig) |
| **Goudstandaard testset** | 50–150 geheime parallelle tekstparen voor officiële evaluatie | Communautaire bestuursorganisatie (cryptografisch verzegeld) |
| **Diagnostische testsuite** | 10–50 gerichte contrastieve paren die specifieke taalkundige verschijnselen testen | Openbaar gepubliceerd |

Het ontwikkelingscorpus stelt iedereen in staat vertaalmethoden te bouwen. De goudstandaard testset zorgt ervoor dat die methoden eerlijk worden getest. De diagnostische suite detecteert specifieke faalpatronen (bijv. "kan dit systeem obviatie verwerken?").

---

## 2. Wat de Afdeling Moet Doen

### Fase 1: Corpusontwerp (2–4 weken, onderzoekersinzet)

**Verantwoordelijke:** PI of postdoc met expertise in de doeltaal.

1. **Selecteer domeinen voor bronmateriaal.** Kies 4–6 praktijkdomeinen waarbinnen vertaling daadwerkelijk nodig is voor de taalgemeenschap. Onze taxonomie ondersteunt 16 domeinen (zie Benchmarkspecificatie §2.7):

   | Prioriteit | Domein | Reden |
   |----------|--------|-----|
   | 🔴 Hoog | `edu` — Onderwijs | Leerboeken, curricula — directe behoefte van de gemeenschap |
   | 🔴 Hoog | `gov` — Overheid | Documenten van de bandraad, beleid — praktische dagelijkse behoefte |
   | 🔴 Hoog | `medical` — Gezondheid | Intakeformulieren voor klinieken, gezondheidsinformatie — veiligheidskritisch |
   | 🟡 Gemiddeld | `conv` — Conversationeel | Alledaags taalgebruik — stelt basisvloeiendheid vast |
   | 🟡 Gemiddeld | `legal` — Juridisch | Rechtendocumenten, verdragen — belang voor de gemeenschap |
   | 🟢 Lager | `literary` — Literair/Cultureel | Verhalen, mondelinge geschiedenis — cultureel behoud |

2. **Stel een corpusontwerpdocument op** met daarin:
   - Beoogde omvang per segment (development, gold_standard, diagnostic)
   - Verdeling over moeilijkheidsgraden (zie §3.3 hieronder)
   - Dekking van register en domein
   - Selectiecriteria voor bronzinnen (geen synthetische tekst, niet uitsluitend Bijbeltekst)
   - Plan voor werving van sprekers

3. **Dien het ontwerp bij ons in ter beoordeling.** Wij valideren het aan de hand van het corpusschema (Benchmarkspecificatie §2) en geven binnen 1 week feedback.

### Fase 2: Aanmaken van Bronzinnen (4–8 weken, sprekersinzet)

**Verantwoordelijke:** Onderzoekscoördinator in samenwerking met tweetalige sprekers.

1. **Genereer of selecteer bronzinnen** over de geplande domeinen en moeilijkheidsgraden. Bronnen kunnen zijn:
   - Bestaand gepubliceerd tweetalig materiaal (leerboeken, overheidsdocumenten)
   - Nieuw ontlokte zinnen die zijn ontworpen om specifieke taalkundige verschijnselen te dekken
   - Aangepast vanuit praktijkdocumenten (agenda's van de bandraad, kliniekformulieren, onderwijsmateriaal)

2. **Elke bronzin moet het volgende bevatten:**
   - Domeinlabel (uit de 16-code taxonomie)
   - Registerlabel (conversationeel, formeel, technisch, ceremonieel, educatief)
   - Contextlabel (begroeting, verklaring, vraag, instructie, narratief, label, fout)
   - Geschatte moeilijkheidsgraad (1–5, zie §3.3)
   - Herkomstlabel (leerboek, ontlokt, corpus, gold_standard)

3. **Vertaal elke bronzin** naar de doeltaal; dit wordt uitgevoerd door tweetalige sprekers. Meerdere referentievertalingen per item zijn waardevol maar niet vereist.

4. **Voeg optioneel morfologische analyse toe** voor elke referentievertaling:
   - Interlineaire gloss (morfeem-voor-morfeem uitsplitsing)
   - FST-tagstring (indien er een FST bestaat voor de taal)
   - Opmerkingen van de vertaler over dialectale varianten, ambiguïteit of culturele context

### Fase 3: Kwaliteitsborging (2–4 weken)

**Verantwoordelijke:** Taalkundige met expertise in de doeltaal.

1. **Kruisreview.** Elke vertaling dient te worden beoordeeld door ten minste één extra tweetalige spreker die de oorspronkelijke vertaling niet heeft gemaakt. De beoordelaar controleert:
   - Is de vertaling nauwkeurig?
   - Klinkt ze natuurlijk?
   - Is de moeilijkheidsgraad correct?
   - Zijn er aanvaardbare varianten die vermeld moeten worden?

2. **Voer de schemavalidator uit.** Wij leveren een script dat het corpus valideert aan de hand van het itemschema (Benchmarkspecificatie §2.2). Het controleert:
   - Aanwezigheid van verplichte velden
   - Geldigheid van domeincodes
   - Moeilijkheidsgraden zijn gehele getallen 1–5
   - Geen dubbele ID's
   - Tekencodering (UTF-8 NFC-normalisatie)

3. **Als er een FST bestaat voor de taal,** voer de referentievertalingen daar doorheen. Elk woord in de referentie dient FST-geldig te zijn. Woorden die dat niet zijn (leenwoorden, neologismen, eigennamen) dienen te worden gedocumenteerd in een allowlist.

### Fase 4: Segmentatie en Verzegeling (1 week, onze engineering)

**Verantwoordelijke:** Champollion-team, met beoordeling door de afdeling.

1. **Gestratificeerde splitsing.** Wij splitsen het corpus in segmenten met behulp van deterministische willekeurige steekproeftrekking (seed gedocumenteerd, reproduceerbaar):

   | Segment | Beoogde omvang | Toegang |
   |---------|------------|--------|
   | `development` | 60% van de items (min. 100) | Openbaar |
   | `gold_standard` | 30% van de items (min. 50) | Geheim, verzegeld |
   | `held_out` | 10% van de items (min. 10) | Geheim, verzegeld, nooit gebruikt tot activering |

   De splitsing behoudt de verdeling over moeilijkheidsgraden (gestratificeerde steekproeftrekking), zodat elk segment een evenredige vertegenwoordiging over alle graden heeft.

2. **Cryptografische verzegeling** van de gold_standard- en held_out-segmenten:

   ```
   1. SHA-256 hash of each entry (source + reference + metadata)
   2. SHA-256 hash of the complete segment file
   3. Segment file encrypted with AES-256-GCM
   4. Encryption key split using Shamir Secret Sharing (2-of-3 threshold)
   5. Key shares distributed to:
        - Share 1: Community governance organization
        - Share 2: Academic department partner
        - Share 3: Champollion project (escrow)
   6. Hash manifest published to a public commit (proves the corpus existed
      at a specific time without revealing its contents)
   ```

3. **Het development-segment** wordt vastgelegd in de openbare repository en gepubliceerd met volledige licentie-informatie.

4. **Het diagnostische segment** is eveneens openbaar — het test specifieke taalkundige verschijnselen (zie §3.4).

### Fase 5: Integratie en Lancering (1–2 weken, onze engineering)

1. **Harness-configuratie.** Wij voegen de taal toe aan de evaluatieharness:
   - Taalkaart aangemaakt of geverifieerd
   - Corpus geregistreerd in het datasetregister
   - LYSS-metrics geconfigureerd (LYSS-fst indien FST beschikbaar, LYSS-eq indien linterregels bestaan)
   - Standaard scoringprofiel geselecteerd (Profiel A indien FST beschikbaar, Profiel B anders)

2. **Basisbenchmark.** Wij voeren een sweep van 12 modellen uit op het development-segment om het leaderboard te vullen met initiële scores.

3. **Publieke aankondiging.** De taal verschijnt op het Arena-leaderboard met een live benchmark op het development-segment. De afdeling wordt vermeld als corpuspartner.

---

## 3. Hoe het Corpus Eruit Moet Zien

### 3.1 Formaat

Elk corpusbestand is een JSON-document dat het schema in Benchmarkspecificatie §2.1–§2.2 volgt:

```json
{
  "dataset": {
    "id": "crk-ualberta-v1",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "source_language": "en",
    "target_language": "crk",
    "created": "2026-09-15",
    "license": "CC-BY-NC-SA-4.0",
    "provenance": ["textbook", "elicited", "gold_standard"]
  },
  "entries": [
    {
      "id": 1,
      "source": "I see the dog",
      "reference": "niwâpamâw atim",
      "segment": "development",
      "difficulty": 2,
      "provenance": "textbook",
      "register": "conversational",
      "context": "declaration",
      "domain": "edu",
      "morphological_analysis": "ni-wâpam-âw atim | 1sg-see.TA-3sg.DIR dog.AN",
      "notes": "Animate noun (atim); direct form because speaker is proximate"
    }
  ]
}
```

### 3.2 Minimale Omvangsvereisten

| Segment | Minimale items | Aanbevolen |
|---------|----------------|-------------|
| `development` | 100 | 200–300 |
| `gold_standard` | 50 | 100–150 |
| `diagnostic` | 10 | 30–50 |
| `held_out` | 10 | 20–30 |
| **Totaal** | **170** | **350–530** |

### 3.3 Verdeling over Moeilijkheidsgraden

Het corpus moet items bevatten over alle vijf moeilijkheidsgraden, met nadruk op graden 2–4:

| Graad | Beschrijving | Beoogde verdeling |
|------|-------------|-------------------|
| 1 — Basiswoordenschat | Losse woorden, veelgebruikte begroetingen, getallen | 10–15% |
| 2 — Eenvoudige zinnen | SVO, tegenwoordige tijd | 25–30% |
| 3 — Gemiddelde complexiteit | Verleden/toekomstige tijd, bezittelijke vormen, animaatheid | 30–35% |
| 4 — Complexe morfologie | Obviatie, passief, conjunctorde, betrekkelijke bijzinnen | 15–20% |
| 5 — Gevorderd | Meervoudige bijzinnen, formeel register, ceremonieel, idiomatisch | 5–10% |

### 3.4 Diagnostische Testsuite

Het diagnostische segment test specifieke taalkundige verschijnselen aan de hand van **contrastieve paren**: één correcte vertaling en één minimaal afwijkende incorrecte vertaling. Als de metrische score van een systeem de correcte hoger beoordeelt, slaagt de test.

Voor polysynthetische talen dient de diagnostische suite gericht te zijn op:

| Verschijnsel | Voorbeeld (Cree) | Wat het test |
|-----------|----------------|--------------|
| **Animaatheidscongruentie** | atim (AN) vs. maskisin (IN) — verschillende werkwoordsvormen | Weet het systeem welke zelfstandige naamwoorden animaat zijn? |
| **Obviatie** | Proximatief vs. obviatiefde derde persoon | Volgt het de hiërarchie van de derde persoon? |
| **Inversmarkering** | Directe vs. inverse werkwoordsvormen | Verwerkt het patiënt-overtreft-agens? |
| **Conjunct/Onafhankelijk** | Hoofdzin vs. bijzin werkwoordsvolgorde | Gebruikt het het juiste werkwoordsparadigma? |
| **Inclusief/Exclusief** | "Wij (inclusief u)" vs. "Wij (exclusief u)" | Onderscheidt het meervoudsvormen van de eerste persoon? |

Voor andere taalfamilies: identificeer de 3–5 meest diagnostische verschijnselen die competente van incompetente vertaling onderscheiden. De taalkundige expertise van de afdeling is hier essentieel — dit zijn de tests die alleen een specialist zou weten te schrijven.

### 3.5 Wat Wij NIET Willen

| Anti-patroon | Reden |
|-------------|-----|
| **Uitsluitend Bijbeltekst** | Archaïsch register, liturgisch vocabulaire, formulaïsche structuur. OMT-1600 evalueerde 1.560 talen op deze manier — wij vermijden dit bewust. |
| **Synthetische evaluatieparen** | Door LLM gegenereerde referenties ondermijnen het doel van evaluatie. De referentie moet door een mens zijn geschreven. |
| **Corpora met één register** | Uitsluitend formeel of uitsluitend conversationeel. Vertaling in de praktijk omvat meerdere registers. |
| **Uitsluitend moeilijkheidsgraad 1** | Losse woorden en begroetingen testen geen vertaling — ze testen het opzoeken van vocabulaire. |
| **Machinaal vertaalde referenties** | Google Translate-uitvoer gebruiken als "referentie" is circulair. |
| **Zinnen zonder contextlabel** | Wij hebben de communicatieve functie nodig voor diagnostische analyse. |

---

## 4. Cryptografische Verzegeling en Sandboxtesten

### 4.1 Waarom de Testset Verzegelen?

Conventionele ML-benchmarks publiceren testsets openbaar. Zodra gepubliceerd, zullen frontier-LLM's er uiteindelijk op trainen (opzettelijk of via webscraping), waardoor scores onbetrouwbaar worden. Voor inheemse taaldata bestaat er een bijkomende zorg: gepubliceerde taalkundige data kan worden gebruikt zonder toestemming van de gemeenschap.

Verzegeling garandeert:
- **Integriteit van de testset:** Methoden kunnen niet overfitting vertonen op data die ze nooit hebben gezien
- **Gegevenssouvereiniteit:** De gemeenschap bepaalt wie haar data evalueert
- **Blijvende versheid:** De testset raakt nooit besmet

### 4.2 Hoe Sandboxtesten Werkt

```
Developer workflow:
  1. Developer builds a translation method using the PUBLIC development corpus
  2. Developer tests locally against the development segment (unlimited, self-serve)
  3. When ready, developer submits their complete method (code + config + coaching data)
  4. Governance org installs the method in the evaluation sandbox
  5. Sandbox runs the method against the SEALED gold-standard test set
  6. Only scores are returned to the developer
  7. Developer never sees the source sentences or reference translations

The sandbox:
  - Runs on governance-controlled infrastructure
  - Has selective network access (LLM APIs only, no exfiltration)
  - Produces a tamper-proof run card (SHA-256 hash of all inputs and outputs)
  - Logs all execution for audit purposes
  - Can be inspected by the governance org at any time
```

### 4.3 Sleutelbeheer

De encryptiesleutel voor de verzegelde testset wordt gesplitst met behulp van Shamir Secret Sharing met een drempel van 2 van 3:

| Sleutelhouder | Rol | Intrekkingsbevoegdheid |
|-------------|------|-----------------|
| **Communautaire bestuursorganisatie** | Primaire beheerder | Kan evaluatietoegang eenzijdig intrekken |
| **Academische afdelingspartner** | Mede-beheerder | Kan deelnemen aan sleutelreconstructie |
| **Champollion-project** | Escrow | Heeft geen toegang tot data alleen; waarborgt continuïteit als andere partijen niet beschikbaar zijn |

Elke 2 van 3 aandelen reconstrueren de sleutel. Dit betekent:
- De gemeenschap + afdeling kunnen de data raadplegen zonder Champollion
- De gemeenschap + Champollion kunnen de data raadplegen zonder de afdeling
- Champollion alleen kan de data NOOIT raadplegen

### 4.4 Hash-manifesten

Wanneer het corpus wordt verzegeld, wordt een **hash-manifest** gepubliceerd in een openbare Git-commit:

```json
{
  "corpus_id": "crk-ualberta-v1",
  "seal_date": "2026-09-15T00:00:00Z",
  "segments": {
    "development": {
      "entry_count": 200,
      "sha256": "a3f7c...",
      "access": "public"
    },
    "gold_standard": {
      "entry_count": 100,
      "sha256": "b8d2e...",
      "access": "sealed",
      "key_scheme": "shamir-2-of-3"
    },
    "held_out": {
      "entry_count": 20,
      "sha256": "c9e4f...",
      "access": "sealed",
      "key_scheme": "shamir-2-of-3"
    },
    "diagnostic": {
      "entry_count": 30,
      "sha256": "d1a3b...",
      "access": "public"
    }
  },
  "total_entries": 350,
  "manifest_sha256": "e2b5c..."
}
```

Dit bewijst:
- Het corpus bestond op een specifieke datum
- Het heeft een bekende omvang en structuur
- Elke wijziging aan de verzegelde segmenten zou de hashketen verbreken
- De gemeenschap kan verifiëren dat haar data niet is gemanipuleerd

---

## 5. Wat de Afdeling Krijgt

### 5.1 Onderzoeksinfrastructuur

| Asset | Beschrijving |
|-------|------------|
| **Evaluatieharness** | Een werkend, getest evaluatieraamwerk voor hun taal — bespaart maanden aan toolontwikkeling |
| **LYSS-metrics** | Taalspecifieke evaluatiemetrics (LYSS-fst, LYSS-eq, LYSS-sem) geconfigureerd voor hun taal — indien FST- en woordenboekbronnen beschikbaar zijn |
| **Leaderboard** | Een openbaar, live leaderboard dat de stand van de techniek voor hun taalpaar toont |
| **Basisbenchmark** | Sweep van 12 modellen die onmiddellijk publiceerbare basislijnen oplevert |
| **Diagnostische testsuite** | Gerichte tests voor specifieke taalkundige verschijnselen — herbruikbaar voor andere evaluaties |

### 5.2 Publicaties

De corpusconstructie en evaluatieresultaten ondersteunen meerdere publicaties:

| Artikel | Venue | Rol van de afdeling |
|-------|-------|-----------------|
| Methodologie voor corpusconstructie | LREC, ComputEL | Eerste of mede-auteur |
| Basisevaluatieresultaten | ACL, EMNLP | Mede-auteur |
| Validatie van LYSS-metrics | WMT Metrics Shared Task | Mede-auteur |
| Ontwerp van diagnostische testsuite | SIGMORPHON, NAACL | Eerste of mede-auteur |
| Taalspecifieke NLP-bronnen | Taalspecifieke venues | Eerste auteur |

### 5.3 Positionering voor Subsidies

Het partnerschap levert concrete resultaten op voor subsidieaanvragen:

- "Open-source evaluatie-infrastructuur voor [taal] MT" — aantoonbaar deliverable
- "Cryptografische gegevenssouvereiniteit voor inheemse taalkundige data" — nieuw, publiceerbaar
- "Door de gemeenschap beheerde benchmark met live leaderboard" — doorlopende impactmeting
- "Onafhankelijke evaluatie van OMT-1600 / Google Translate voor [taal]" — actueel, hoge zichtbaarheid

### 5.4 Impact op de Gemeenschap

- De taalgemeenschap krijgt een **onafhankelijke evaluatiecapaciteit** — zij kan beoordelen of een MT-systeem (Google, Meta of op maat gemaakt) daadwerkelijk werkt voor haar taal
- De gemeenschap **beheert de testdata** via cryptografisch sleutelbeheer
- Methoden die via de benchmark zijn bewezen, **dragen eigendom over** aan de gemeenschap (zie Benchmarkspecificatie §8.3)
- Inkomsten uit geïmplementeerde methoden vloeien naar de gemeenschap (verdeling 90/10)

### 5.5 Wat het de Afdeling Kost

| Component | Geschatte kosten | Wie betaalt |
|-----------|---------------|----------|
| PI/postdoc-inzet (ontwerp, toezicht) | ~40 uur | Afdeling (of gefinancierd via subsidie) |
| Sprekervergoeding (vertaling) | $2.500–6.000 | Gefinancierd via subsidie of Champollion |
| Sprekervergoeding (review) | $500–1.500 | Gefinancierd via subsidie of Champollion |
| Inzet onderzoekscoördinator | ~20 uur | Afdeling |
| **Engineering, infrastructuur, harness** | **$0** | **Champollion-project** |

Wij leveren alle engineering, harness-configuratie, LYSS-metricconfiguratie, leaderboard-integratie en doorlopende infrastructuur kosteloos aan de afdeling. De bijdrage van de afdeling bestaat uit taalkundige expertise en toegang tot sprekers.

---

## 6. Tijdlijn

| Fase | Duur | Belangrijke mijlpaal |
|-------|----------|--------------|
| 1: Corpusontwerp | 2–4 weken | Ontwerpdocument goedgekeurd |
| 2: Bronzinnen + Vertaling | 4–8 weken | Ruw corpus voltooid |
| 3: Kwaliteitsborging | 2–4 weken | Kruisbeoordeeld, schemagevalideerd |
| 4: Verzegeling | 1 week | Goudstandaard verzegeld, hash-manifest gepubliceerd |
| 5: Integratie | 1–2 weken | Taal live op leaderboard met basislijnen |
| **Totaal** | **10–19 weken** | **Live leaderboard met verzegelde evaluatie** |

---

## 7. Hoe te Beginnen

1. **Neem contact met ons op** — [project e-mail/contact]. Wij plannen een gesprek van 30 minuten om uw taal, beschikbare middelen en de logistiek van het partnerschap te bespreken.

2. **Wij leveren:**
   - Dit document
   - Het corpusschema en de validatietools
   - Voorbeelden uit ons bestaande Cree (CRK)-corpus
   - Een sjabloon voor het corpusontwerp

3. **U levert:**
   - Een PI of postdoc om het taalkundige werk te leiden
   - Toegang tot tweetalige sprekers (of een plan om hen te werven)
   - Informatie over beschikbare bronnen (FST, woordenboek, bestaande corpora)
   - Institutionele goedkeuring voor gegevensbeheer (OCAP®-naleving of gelijkwaardig)

4. **Wij ontwerpen het corpus samen** — domeinselectie, verdeling over moeilijkheidsgraden, diagnostische tests, tijdlijn en budget.

5. **Het werk begint.** Wij checken wekelijks in. De afdeling heeft volledige autonomie over taalkundige beslissingen; wij verzorgen alle engineering.

---

## 8. Veelgestelde Vragen

### "Wij hebben al een parallel corpus. Kunnen wij dat gebruiken?"

Ja — mits het corpus een duidelijke herkomst heeft, door mensen is geschreven en de licentie gebruik voor evaluatie toestaat. Wij helpen u het te formatteren naar ons schema, ontbrekende metadata toe te voegen en het te integreren. Bestaande corpora kunnen de tijdlijn aanzienlijk versnellen (sla Fase 2 over of beperk het tot een aanvullingsoefening).

### "Wij hebben geen FST voor onze taal."

Dat is geen probleem. LYSS-fst (morfologische geldigheid) vereist een FST, maar de harness werkt zonder FST via Profiel B-gewichten (chrF++, BLEU, COMET, gedragsmetrics). Als er een GiellaLT FST bestaat voor een verwante taal, kunnen wij die mogelijk aanpassen. Zo niet, dan maakt het corpus nog steeds waardevolle evaluatie mogelijk — alleen zonder de morfologische geldigheidspoort.

### "Onze sprekers gebruiken een niet-Latijns schrift."

Volledig ondersteund. Het corpusschema verwerkt elk Unicode-schrift. Wij hebben ontworpen voor SRO (Standard Roman Orthography) en syllabics voor Cree, maar dezelfde infrastructuur werkt voor Devanagari, Arabisch schrift, CJK, Ethiopisch of elk ander schrijfsysteem.

### "Hoe zit het met dialectvariatie?"

Label het. Het itemschema van het corpus bevat een `notes`-veld voor dialectinformatie. Als meerdere dialecten zijn vertegenwoordigd, documenteer ze dan. De equivalentieklassen van de linter (LYSS-eq) kunnen worden geconfigureerd om dialectale varianten als equivalent te accepteren. De diagnostische testsuite kan dialectspecifieke contrasten bevatten.

### "Wie is eigenaar van het corpus?"

De taalgemeenschap, via de bestuursorganisatie. De afdeling wordt vermeld als onderzoekspartner. Champollion houdt een escrow-sleutelaandeel aan voor operationele continuïteit, maar heeft geen toegang tot de verzegelde data alleen. Het development-segment wordt gepubliceerd onder een Creative Commons-licentie die door de gemeenschap wordt bepaald.

### "Wat als wij willen stoppen?"

De gemeenschap kan evaluatietoegang op elk moment intrekken door te weigeren de encryptiesleutel te reconstrueren. De verzegelde data wordt nooit blootgesteld. Het development-segment, dat al is gepubliceerd, blijft openbaar onder zijn licentie. De onderzoeksresultaten van de afdeling (publicaties, presentaties) blijven van haar, ongeacht wat er gebeurt.

### "Wat als de bestuursorganisatie nog niet bestaat?"

Wij kunnen beginnen met Fasen 1–3 (corpusontwerp, aanmaak, kwaliteitsborging) zonder een bestuursorganisatie. De verzegeling (Fase 4) vereist het aanwijzen van een sleutelbeheerder. In de tussentijd kan de afdeling optreden als mede-beheerder naast het Champollion-project, met de afspraak dat het beheer wordt overgedragen aan de communautaire bestuursorganisatie zodra die is opgericht.

---

## Bijlage: Labeling versus Corpusconstructie

Dit document behandelt **corpusconstructie** — het aanmaken van de parallelle tekstparen die de evaluatiegrondwaarheid vormen. Labeling (morfologische annotatie, interlineaire glossing, FST-tagstrings) is een afzonderlijke activiteit die het corpus verrijkt maar niet vereist is voor basisevaluatie.

| Activiteit | Vereist? | Wat het mogelijk maakt |
|----------|-----------|-----------------|
| **Corpusconstructie** (dit document) | ✅ Vereist | Basisevaluatie: chrF++, exacte overeenkomst, COMET, gedragsmetrics |
| **FST-dekkingscontrole** | 🟡 Optioneel | LYSS-fst morfologische geldigheidsmetriek |
| **Morfologische annotatie** | 🟡 Optioneel | `morphological_accuracy`-metriek (Scoringspecificatie §2.2) |
| **Linter-equivalentieregels** | 🟡 Optioneel | LYSS-eq equivalente overeenkomstmetriek |
| **Semantische validatorregels** | 🟡 Optioneel | LYSS-sem semantische validatiemetriek |
| **Kwaliteitsbeoordelingen door sprekers** | Afzonderlijke activiteit | Metriekvalidatie (zie [Sprekervalidatieprotocol](/docs/specifications/speaker-validation)) |

Labeling en sprekervalidatie worden behandeld in afzonderlijke documenten en kunnen parallel aan of na de corpusconstructie plaatsvinden.