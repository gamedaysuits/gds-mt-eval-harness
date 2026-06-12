---
sidebar_position: 5
title: "Ondersteuning van een taal met weinig middelen"
related:
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "The first step for an uncovered language"
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
  - label: "Plains Cree, the trading card"
    to: https://champollion.dev/trading-cards?q=crk
    kind: card
    note: "The proof-of-concept language, as a card"
---
# Ondersteuning voor een Taal met Weinig Middelen

> **Samenvatting.** Een uitgebreide gids voor het bouwen van machinevertaling voor talen met weinig middelen en polysynthetische talen. Behandelt waarom deze talen moeilijk zijn (morfologische complexiteit, schaarse data, hallucinatie), bestaande computationele hulpbronnen (ALTLab FST, GiellaLT, Apertium, UniMorph, EdTeKLA), meer dan 10 benaderingsstrategieën, het champollion-coachingsysteem en de evaluatielus. Begin hier als u een methode wilt bijdragen voor een ondervertegenwoordigde taal.

:::info Status: In Actieve Ontwikkeling
Ondersteuning voor Plains Cree (nêhiyawêwin) is momenteel in ontwikkeling. De tools, de evaluatieomgeving en het leaderboard die hier worden beschreven zijn reëel en vandaag bruikbaar, maar de Cree-vertaalpijplijn is nog niet uitgebracht. Wanneer dat het geval is, zal dit dienen als blauwdruk voor andere polysynthetische talen en talen met weinig middelen die over FST-infrastructuur beschikken.
:::

## Het Onopgeloste Probleem

Google Translate ondersteunt circa 130 talen. Meta's OMT-1600 (maart 2026) claimt dekking voor 1.600 talen — het grootste MT-systeem dat ooit is gepubliceerd. Maar voor de circa 1.300 talen in hun laagste resourceniveaus ligt de kwaliteit onder bruikbare drempelwaarden, wordt trainingsdata gedomineerd door bijbeltekst, zijn de modelgewichten niet beschikbaar voor download, en is er geen onafhankelijke evaluatie of communitygovernancekader. Voor de resterende circa 5.400 talen produceert geen enkel voorgetraind model enige uitvoer.

Het landschap is aanzienlijk veranderd — Big Tech investeert nu in LRL-dekking. Maar dekking is geen kwaliteit, en kwaliteit zonder onafhankelijke verificatie is geen vertrouwen. Talen met weinig middelen hebben meer nodig dan een model dat beweert ze te ondersteunen — ze hebben onafhankelijke evaluatie met morfologische validatie, door de gemeenschap samengestelde corpora en soevereiniteitsrespecterende governance nodig.

**champollion is gebouwd om dat te veranderen.**

Het [Method Leaderboard](https://champollion.dev/leaderboard) is een open uitdaging: bouw de beste vertaalmethode voor een ondervertegenwoordigde taal, bewijs dit met reproduceerbare evaluatie en claim de topscore. Iedereen ter wereld kan bijdragen — taalkundigen, ML-onderzoekers, gemeenschapstaalwerkers, studenten, hobbyisten. Het probleem is onopgelost. De infrastructuur is beschikbaar. Het leaderboard wacht.

---

## Waarom Dit Moeilijk Is: Polysynthetische Morfologie

De meeste commerciële MT-systemen zijn ontworpen voor talen zoals Engels, Frans en Chinees — talen waarbij woorden relatief kort zijn en zinnen worden opgebouwd uit afzonderlijke tokens. Maar veel inheemse talen, waaronder Plains Cree, zijn **polysynthetisch**: één enkel woord kan uitdrukken wat het Engels als een volledige zin formuleert.

### Het Cree-voorbeeld

Beschouw het Plains Cree-woord:

> **ê-kî-nitawi-kîskinwahamâkosiyân**
> *"when I went to school"*

Dat is **één woord**. Het codeert tijd (verleden), richting (gaan naar), de stam (leren), diathese (passief/reflexief) en persoon (eerste enkelvoud). Een LLM dat voornamelijk op Engels is getraind, heeft geen intuïtie voor dit soort morfologische dichtheid.

De uitdagingen stapelen zich op:

| Uitdaging | Wat Het Betekent |
|-----------|-----------------|
| **Morfologische complexiteit** | Één enkele werkwoordsstam kan duizenden geldige verbuigde vormen genereren via prefixatie, suffixatie en circumfixatie |
| **Animaat/inanimaat-onderscheid** | Zelfstandige naamwoorden zijn grammaticaal animaat of inanimaat — dit beïnvloedt werkwoordsvervoeging, demonstratieven en meervoudsvorming. De classificatie volgt niet altijd biologische animaatheid (*askiy* "aarde" is animaat; *maskisin* "schoen" is ook animaat) |
| **Obviatie** | Verwijzingen naar de derde persoon worden gerangschikt naar nabijheid/prominentie. Het onderscheid tussen "proximatief" en "obviatief" heeft geen equivalent in het Engels |
| **Schaarse trainingsdata** | LLM's hebben zeer weinig Plains Cree-tekst gezien. Wat ze hebben gezien, kan dialecten mengen (Y-dialect, TH-dialect) of orthografieën (SRO vs. syllabics) |
| **Zwakke commerciële basislijn** | OMT-1600 bevat CRK op R1-niveau (Very Low Resource) met bijbeldomeintraining en standaard BPE-tokenisatie. Google Translate ondersteunt Cree niet. Onafhankelijke evaluatie met morfologische metrieken is wat deze basislijnen betekenisvol maakt. |

Vertaling van polysynthetische talen blijft een **open onderzoeksprobleem** — OMT-1600 bevat polysynthetische talen maar gebruikt standaard BPE-tokenisatie (256K vocabulaire) zonder morfologisch bewustzijn, wat betekent dat het compositionele woorden versnippert tot betekenisloze bytefragmenten.

---

## Eerder Werk: Hoe Mensen Dit Hebben Benaderd

### De ALTLab FST

De meest significante computationele hulpbron voor Plains Cree is de **finite-state transducer (FST)** ontwikkeld door het [Alberta Language Technology Lab (ALTLab)](https://altlab.artsrn.ualberta.ca/) aan de Universiteit van Alberta, in samenwerking met [Giellatekno](https://giellatekno.uit.no/) aan UiT The Arctic University of Norway.

De ALTLab FST is een **morfologische analysator en generator**: gegeven een verbogen Cree-woord kan hij het ontleden in zijn stam en grammaticale tags, en gegeven een stam plus tags kan hij de correcte verbogen vorm genereren. Dit is deterministisch — geen neuraal netwerk, geen hallucinatie, geen kansen. Als de FST een woord accepteert, is dat woord morfologisch geldig.

Dit is waarom het champollion-leaderboard de **FST Acceptance Rate** bijhoudt als metriek. Een vertaalmethode die woorden produceert die de FST afwijst, produceert morfologisch ongeldig Cree — ongeacht wat de chrF++-score aangeeft.

**Belangrijke ALTLab-hulpbronnen:**
- [itwêwina](https://itwewina.altlab.app/) — een intelligent Plains Cree–Engels woordenboek aangedreven door de FST
- [Morphodict](https://github.com/UAlbertaALTLab/morphodict) — open-source morfologisch bewust woordenboekplatform
- [crk-db](https://github.com/UAlbertaALTLab/crk-db) — Plains Cree lexicale database
- [21st Century Tools for Indigenous Languages](https://21c.tools/) — de bredere projectcontext

### Globale FST- en Morfologische Registers

Plains Cree is niet de enige taal met hoogwaardige FST-infrastructuur. Als u vertaalpijplijnen wilt ontwikkelen voor andere talen met weinig middelen of morfologisch complexe talen, kunt u gebruikmaken van deze gevestigde mondiale hubs:

* **[GiellaLT / Giellatekno](https://giellalt.github.io/) (UiT The Arctic University of Norway):** De grootste repository van open-source FST-morfologische analysatoren en generatoren, met meer dan 100 talen. Focusgebieden omvatten Sámi-talen (`sme`, `smj`, `sma`, etc.), Oeraalse talen (Komi, Erzya, Udmurt, etc.) en andere minderheidstalen/inheemse talen. Ze hosten publieke verwerkte tekstcorpora (`corpus-xxx`) in hun [GitHub-organisatie](https://github.com/giellalt/).
* **[The Apertium Project](https://www.apertium.org/):** Een open-source regelgebaseerd machinevertaalplatform. Apertium onderhoudt sterk geoptimaliseerde FST-morfologische analysatoren (met behulp van `lttoolbox` en `hfst`) en tweetalige woordenboeken voor tientallen talen, waaronder een grote reeks Turkse talen (Kazachs, Tataars, Kirgizisch, etc.) en Europese minderheidstalen. Alle hulpbronnen zijn openbaar op [Apertium's GitHub](https://github.com/apertium).
* **[UniMorph (Universal Morphology)](https://unimorph.github.io/):** Een samenwerkingsproject dat gestandaardiseerde morfologische paradigma's biedt voor meer dan 150 talen. De dataset wordt gehost op Hugging Face op [unimorph/universal_morphologies](https://huggingface.co/datasets/unimorph/universal_morphologies). Als er geen gecompileerd FST-binair bestand beschikbaar is voor een taal, kunnen UniMorph-tabellen worden gebruikt als statische databaseopzoekpoort.
* **[National Research Council Canada (NRC)](https://nrc-digital-repository.canada.ca/):** Biedt tools voor Canadese inheemse talen, waaronder de **Uqailaut** Inuktitut FST-morfologische analysator en het omvangrijke **Nunavut Hansard Parallel Corpus** (1,3 miljoen uitgelijnde Engelse-Inuktitut zinsparen).

### Het EdTeKLA-corpus

De [EdTeKLA-onderzoeksgroep](https://spaces.facsci.ualberta.ca/edtekla/) (eveneens aan UAlberta) heeft een Plains Cree-talenkorpus samengesteld uit educatief materiaal, audiotranscripties en gemeenschapsbronnen. De champollion-evaluatiedataset [EDTeKLA Dev v1](/docs/leaderboard/datasets) is afgeleid van dit werk, gelicentieerd onder [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

### Andere benaderingen die mensen hebben geprobeerd of kunnen proberen

Het leaderboard is methode-agnostisch. Hier zijn strategieën die zijn onderzocht of voorgesteld voor MT met weinig middelen, waarvan elk kan worden ingediend:

| Benadering | Hoe Het Werkt | Voordelen | Nadelen |
|------------|--------------|-----------|---------|
| **[Gecoachte LLM-prompting](/docs/tutorials/coached-llm-prompting)** | Injecteer grammaticaregels, woordenboeken en voorbeeldparen in de systeemprompt | Snel te itereren, geen training nodig | Kwaliteitsplafond beperkt door basiskennis van de LLM |
| **[Few-shot prompting](/docs/tutorials/few-shot-prompting)** | Voeg geverifieerde vertalingen toe als in-context-voorbeelden | Goed voor consistente stijl | Klein contextvenster; voorbeelden mogen NIET afkomstig zijn uit evaluatiedata |
| **[FST-gated pipeline](/docs/tutorials/fst-gated-pipeline)** | LLM genereert → FST valideert → wijst ongeldige morfologie af en probeert opnieuw | Garandeert morfologische geldigheid | Vereist FST-infrastructuur; herhaallussen voegen latentie en kosten toe |
| **[Woordenboekopzoekingen + LLM](/docs/tutorials/dictionary-augmented-llm)** | Forceer bekende termen uit een tweetalig woordenboek, laat de LLM de rest afhandelen | Vermindert hallucinatie voor bekende termen | Woordenboekdekking is altijd onvolledig |
| **[Fijnafgestemd model](/docs/tutorials/fine-tuned-model)** | Stem een open model (Llama, Mistral) fijn op parallelle tekst — maar niet op de evaluatiedata | Potentieel hoogste kwaliteit | Vereist parallel corpus (schaars); duur; risico op overfitting |
| **[Geketende modellen](/docs/tutorials/chained-models)** | Model A genereert ruwe vertaling → Model B bewerkt na → Model C scoort | Kan specialistische sterktes combineren | Complex; traag; duur |
| **[Regelgebaseerde + LLM-hybride](/docs/tutorials/rule-based-hybrid)** | Gebruik taalkundige regels voor bekende patronen, LLM voor al het overige | Precies waar regels van toepassing zijn | Vereist diepgaande taalkundige expertise |
| **[Back-translationaugmentatie](/docs/tutorials/back-translation)** | Genereer synthetische parallelle data door Cree→Engels te vertalen en vervolgens te trainen op het omgekeerde | Breidt trainingsdata goedkoop uit | Versterkt bestaande modelfouten |
| **[Evolutionaire benadering](/docs/tutorials/evolutionary-approach)** | Genereer kandidaatvertalingen, scoor ze, muteer de beste uitvoerders, herhaal | Kan nieuwe oplossingen ontdekken; paralleliseerbaar | Rekenkundig duur; heeft een goede fitnessfunctie nodig |
| **[Gedeeltelijke vertaling](/docs/tutorials/partial-translation)** | Vertaal handmatig een representatief sample, bewijs dat uw methode uw stijl daarop matcht, en vertaal vervolgens automatisch de resterende bulk | Combineert menselijke kwaliteit met machineschaal | Vereist initiële menselijke inspanning |
| **Handmatige JSON / examenbeoordeling** | Stel handmatig een dataset-JSON-bestand samen om antwoorden van studenten op een taalexamen te toetsen, of beoordeel een batch menselijke vertalingen aan de hand van een gouden standaard | Geen ML vereist; werkt voor onderwijs en kwaliteitsborging | Schaalt niet naar doorlopende vertaalbehoeften |

### Het is gewoon JSON

De harness neemt JSON als invoer en produceert gescoorde JSON als uitvoer. Het [datasetformaat](/docs/leaderboard/datasets) is eenvoudig:

```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

U kunt dit handmatig samenstellen. U kunt het exporteren vanuit een spreadsheet. U kunt het genereren vanuit een corpus. Een taalleraar kan het gebruiken om studentvertalingen te beoordelen. Een vertaalbureau kan het gebruiken om freelancers te benchmarken. Een onderzoekslab kan het gebruiken om modelarchitecturen te vergelijken. De harness maakt niet uit waar de JSON vandaan komt — hij scoort het gewoon.

En omdat het productie-deploymentframework dezelfde plug-in-interface gebruikt, wordt een methode die goed scoort in de harness met één configuratiewijziging op uw website geïmplementeerd. **Bewijs het en gebruik het.**

De mogelijkheden zijn werkelijk eindeloos. **Als u een idee heeft, bouw het, voer de harness uit en dien uw scores in.**

---

## Hoe champollion Past In Het Geheel

champollion biedt de infrastructuurlaag — u brengt de methode mee.

### Het coachingsysteem

De `llm-coached`-methode van champollion laat u taalkundige kennis rechtstreeks in de LLM-prompt injecteren:

```json title=".champollion/coaching/crk.json"
{
  "grammar_rules": [
    "Plains Cree is polysynthetic — a single word can express what English needs a full sentence for",
    "Animate/inanimate noun distinction affects verb conjugation, demonstratives, and pluralization",
    "Use SRO (Standard Roman Orthography) as the working script — syllabic conversion is handled by the deterministic converter",
    "Obviation: when two third-person referents appear, the less salient one takes obviative marking (-a suffix on nouns, -iyiwa on verbs)"
  ],
  "dictionary": {
    "home": "kīwēwin",
    "settings": "isi-nākatohkēwin",
    "search": "nānātawāpahtam",
    "welcome": "tānisi",
    "dashboard": "kīskinwahamākēwin-māsinahikan"
  },
  "style_notes": "Use formal register appropriate for educational and community contexts. Preserve English technical terms in parentheses when no Cree equivalent exists or is widely accepted."
}
```

De coachingdata wordt in elke LLM-prompt voor het `en:crk`-paar geïnjecteerd, waardoor het model gestructureerde taalkundige context krijgt die het anders niet zou hebben. Zie [Coaching Data](https://champollion.dev/docs/concepts/coaching-data) voor de volledige specificatie.

### Registers

Het register is het deel van de systeemprompt dat toon, formaliteit en orthografische conventies stuurt. champollion wordt geleverd met één Plains Cree-register:

```
nêhiyawêwin (Plains Cree). Use SRO (Standard Roman Orthography) as the working
script. Output will be converted to Syllabics via deterministic converter.
Professional register appropriate for educational and community contexts.
```

U kunt dit in uw configuratie overschrijven om te experimenteren met verschillende promptingstrategieën:

```json title="champollion.config.json"
{
  "languages": {
    "crk": {
      "register": "Casual Plains Cree (Y-dialect). Use SRO. Prefer everyday vocabulary over formal or archaic terms. Address the reader directly."
    }
  }
}
```

Verschillende registers produceren verschillende vertaalstijlen — en verschillende scores op het leaderboard. Elke inzending registreert het exacte register en de gebruikte systeemprompt (als een SHA-256-hash in de [run card](/docs/specifications/run-card)), zodat experimenten reproduceerbaar zijn.

### Scriptconversie

Plains Cree wordt geschreven in twee schriften: **Standard Roman Orthography (SRO)** en **Canadian Aboriginal Syllabics**. De pijplijn van champollion:

1. LLM vertaalt naar SRO (op Latin gebaseerd, wat LLM's beter verwerken)
2. Kwaliteitspoort valideert de SRO-uitvoer
3. Deterministische converter transformeert SRO → Syllabics
4. Geconverteerde tekst wordt naar schijf geschreven

De converter verwerkt alle SRO-diakritische tekens (ê, î, ô, â voor lange klinkers) en zet ze om naar de juiste syllabische tekens. Zie [Script Converters](https://champollion.dev/docs/concepts/script-converters) voor technische details.

### De evaluatielus

De [eval harness](/docs/specifications/harness) voert uw methode uit tegen de evaluatiedataset en produceert een gescoorde [run card](/docs/specifications/run-card):

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install -e .

# Run a baseline experiment
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v7

# Run with FST validation (if you have an FST binary)
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --fst-analyzer ./bin/crk-analyzer \
  --condition fst-gated-v1
```

De `--condition`-vlag is een label dat u zelf kiest. Het verschijnt op het leaderboard zodat mensen kunnen zien welke promptstrategie u heeft gebruikt. De harness registreert de volledige systeemprompt in de run card, zodat uw exacte aanpak reproduceerbaar is.

:::tip Experimenteer vrijelijk, dien uw beste in
De harness is ontworpen voor snelle iteratie. Voer tientallen experimenten uit met verschillende modellen, coachingdata, registers en condities. Dien pas in bij het leaderboard wanneer u iets heeft waar u trots op bent.
:::

---

## OCAP-principes

champollion is ontworpen om de datasouvereiniteit van inheemse volkeren te ondersteunen. De [OCAP-principes](https://fnigc.ca/ocap-training/) (Ownership, Control, Access, Possession) sturen onze aanpak van taaltechnologie voor inheemse gemeenschappen:

| Principe | Hoe champollion het ondersteunt |
|----------|---------------------------------|
| **Ownership** | Taalgemeenschappen zijn eigenaar van hun taalkundige data. champollion belt nooit naar huis of verzendt data naar onze servers |
| **Control** | De [API-methode](https://champollion.dev/docs/guides/serving-a-method) stelt gemeenschappen in staat hun eigen vertaalpijplijn te hosten — wij bieden de interface, zij beheren de implementatie |
| **Access** | Gemeenschappen beslissen wie hun methode kan gebruiken. De API kan worden beveiligd met authenticatie |
| **Possession** | Alle vertaaldata blijft in het bestandssysteem van uw project. Het [provenancesysteem](https://champollion.dev/docs/concepts/security) houdt bij waar elke vertaling vandaan komt |

De plug-in-architectuur betekent dat een gemeenschap een methode kan bouwen die intern heilige of beperkte kennis incorporeert, alleen de vertaal-API blootstelt en volledige controle behoudt over hun taalkundige hulpbronnen.

---

## De Visie: Wat Hierna Komt

Plains Cree is het eerste doelwit. Zodra de pijplijn is gevalideerd en de gemeenschap tevreden is met de kwaliteit, breidt dezelfde architectuur zich uit naar andere polysynthetische talen met FST-infrastructuur:

- **Andere Algonquiaanse talen**: Woods Cree, Swampy Cree, Ojibwe, Blackfoot
- **Inuit-talen**: Inuktitut, Inuinnaqtun (die ook syllabische schriften gebruiken)
- **Andere taalfamilies**: elke taal met een FST-analysator kan de FST-gated pipeline gebruiken

Het leaderboard is afgebakend per taalpaar. Naarmate nieuwe evaluatiedatasets worden bijgedragen door taalgemeenschappen, openen er automatisch nieuwe leaderboard-tracks.

**Dit is een open uitnodiging.** Als u werkt met een taal met weinig middelen — als onderzoeker, gemeenschapslid, student of gewoon iemand die het belangrijk vindt — geeft champollion u de tools om iets reëels te bouwen, het eerlijk te meten en het met de wereld te delen. Het [Method Leaderboard](https://champollion.dev/leaderboard) wacht op uw inzending.

---

## Zie Ook

- **[Method Leaderboard](https://champollion.dev/leaderboard)** — dien uw scores in en zie hoe methoden zich verhouden
- **[MT-evaluatie](/docs/leaderboard/rules)** — wat een goede methode maakt, wat wordt gediskwalificeerd
- **[Eval Harness](/docs/specifications/harness)** — hoe u experimenten uitvoert
- **[Evaluatiedatasets](/docs/leaderboard/datasets)** — EDTeKLA Dev v1 en FLORES+
- **[Coaching Data](https://champollion.dev/docs/concepts/coaching-data)** — hoe u taalkundige kennis structureert voor de LLM
- **[Script Converters](https://champollion.dev/docs/concepts/script-converters)** — de SRO→Syllabics-pijplijn
- **[Een methode aanbieden via API](https://champollion.dev/docs/guides/serving-a-method)** — door de gemeenschap beheerde vertaling hosten
- **[ALTLab](https://altlab.artsrn.ualberta.ca/)** — het Alberta Language Technology Lab
- **[EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/)** — de onderzoeksgroep Educational Technology, Knowledge & Language
- **[itwêwina-woordenboek](https://itwewina.altlab.app/)** — FST-aangedreven Plains Cree–Engels woordenboek