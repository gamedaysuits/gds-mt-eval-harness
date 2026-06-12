---
sidebar_position: 4
title: "Rekenkracht bijdragen"
description: "Doneer uw tokens: voer open benchmark-sweeps uit vanuit de publieke wachtrij met uw eigen API-sleutel en publiceer de resultaten."
related:
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
  - label: "Cookbook: Coached LLM Prompting"
    to: /docs/tutorials/coached-llm-prompting
    kind: cookbook
  - label: "Cookbook: FST-Gated Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "Method Interface & Dependency Classes"
    to: /docs/specifications/methods
    kind: spec
  - label: "Leaderboard Rules & Trust Tiers"
    to: /docs/leaderboard/rules
    kind: guide
---
# Rekenkracht bijdragen

> **Het idee:** het scorebord heeft lege vakken — combinaties van (taalpaar, model, conditie) die niemand heeft gemeten. Wij onderhouden een publieke wachtrij hiervan. U voert items uit met uw eigen API-sleutel, publiceert de rapporten, en de kaart vult zich. "Tokens doneren" is een echte, citeerbare bijdrage aan de evaluatie van MT voor talen met weinig middelen.

## De wachtrij

De actuele wachtrij is gepubliceerd op [champollion.dev/queue.json](https://champollion.dev/queue.json), en er is een terminalviewer zonder installatie:

```bash
curl -fsSL champollion.dev/queue | bash
```

De viewer *toont* alleen open items en hun exacte `mt-eval run`-opdrachten — hij voert nooit iets uit en verbruikt geen tokens. Elk item bevat:

- `run_command` — direct kopieer-plakbaar (haalt het corpus op, voert de harness uit)
- `est_cost_usd` en `est_basis` — ofwel de **geobserveerde** kosten van onze eigen basisrun van hetzelfde (corpus, model), ofwel een **extrapolatie** op basis van de gemiddelde kosten per item van dat model over de sweep × het aantal items in het corpus. De grondslag wordt per item vermeld; uw werkelijke kosten zijn afhankelijk van de providerprijzen op het moment van uitvoering.
- `priority` — ongedekte taalparen eerst, taalparen met de minste middelen eerst (corpusgrootte is de maatstaf), naïef vóór gecoacht, goedkoopste model eerst.

**Geen reserveringsslot — kies elk open item.** Twee personen die hetzelfde item uitvoeren is by design onschadelijk: elke run-kaart heeft een vingerafdruk (SHA-256 over dataset-hash + model + conditie + systeemprompt, [Benchmark Spec §3.8](/docs/specifications/benchmark)), zodat identieke runs bij publicatie worden gededupliceerd, en onafhankelijke herhalingen van dezelfde configuratie zijn nuttig bewijs, geen verspilling.

Wachtrijcorpora zijn dev-splits, CC-BY-familie (Tatoeba-afgeleid) en gemarkeerd als `do_not_train` — het zijn evaluatiesets, geen trainingsdata. Corpora met niet-commerciële licenties en in quarantaine geplaatste corpora zijn uitgesloten van de publieke wachtrij.

## Installatie (eenmalig)

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### Welke providersleutel?

De harness routeert **alle** modelaanroepen via [OpenRouter](https://openrouter.ai/keys). Eén `OPENROUTER_API_KEY` bereikt elk model in de wachtrij — Anthropic Claude, OpenAI GPT en Google Gemini-modellen — en de kostenregistratie en prijsmomentopnames van de harness zijn afkomstig van dezelfde OpenRouter-metadata, zodat de gerapporteerde runkosten overeenkomen met wat uw sleutel in rekening is gebracht.

Als uw credits rechtstreeks bij Anthropic, OpenAI of Google staan: de harness accepteert momenteel **geen** directe providersleutels. Het run-kaartschema reserveert een `api_provider`-veld voor de dag dat dit wel het geval is, maar vandaag is elke harness-run een OpenRouter-run. Een OpenRouter-account aanmaken en financieren (of uw eigen provideraccount koppelen waar OpenRouter dat ondersteunt) is het ondersteunde pad.

### Het snelle agentpad

Als u werkt met Claude Code of een andere codeeragent, is de volledige bijdrage één prompt:

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## Tier 1 — Een benchmark uitvoeren

De `run_command` van elk wachtrij-item is op zichzelf staand. Een typisch voorbeeld:

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

De run drukt de totale kosten af en schrijft een runlog plus een gescoord rapport naar `eval/logs/`. Publiceer vervolgens:

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

Publiceren meldt u aan via OAuth (uw naam wordt de scorebordattributie) en voegt de run-kaart in of werkt deze bij. Bijdragen van de community komen terecht op het vertrouwensniveau **zelf-gebenchmarkt** — duidelijk gelabeld als "ingediend door de persoon die het heeft uitgevoerd." Dat is geen degradatie; het is het vertrouwensmodel dat werkt. De run-kaart bevat alles wat nodig is om uw exacte configuratie opnieuw uit te voeren: dataset-hash, model, conditie, de volledige systeemprompt en kosten. Hogere niveaus (verificatie, communityvalidatie) worden toegekend na beoordeling — zie [Scorebordregels](/docs/leaderboard/rules).

## Tier 2 — Gecoachte prompts opstellen

De harness heeft eersteklas ondersteuning voor **coaching**: vervang de naïeve systeemprompt door een prompt die echte taalkundige kennis bevat. Geef `--coaching-file` (of `--coaching "inline text"` voor korte prompts) mee en de harness gebruikt uw tekst als systeemprompt, legt de **volledige tekst plus de SHA-256** vast in het provenance-blok van het runlog, en labelt de conditie van de run als **`coached`** (tenzij u `--prompt` expliciet instelt) — zodat promptontwerp een reproduceerbaar, toeschrijfbaar experiment is, twee verschillende coachingbestanden nooit met elkaar verward kunnen worden, en gecoachte runs nooit worden aangezien voor naïeve basislijnen op het scorebord.

Een uitgewerkt voorbeeld voor het Faeröers, met typologische feiten en woordenlijstvermeldingen van de [publieke taalkaart](https://champollion.dev/languages) van de taal:

```text title="coaching-fao.txt"
You are translating Danish into Faroese (føroyskt).

Grammar notes:
- Faroese is a North Germanic V2 language: the finite verb is the second
  constituent of a main clause.
- Nouns inflect for case (nominative, accusative, dative, genitive),
  gender (masculine, feminine, neuter), and number. Make adjectives and
  determiners agree.
- The skerping pattern applies before -gv/-ggj sequences; preserve
  standard orthography including ð (which is silent).

Glossary (use these exact equivalents):
- language -> mál
- island -> oyggj
- weather -> veður

Style: plain register, modern standard orthography. Output only the
Faroese translation, no commentary.
```

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/dan-fao-dev-v1.json
mt-eval run --corpus dan-fao-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Faroese" \
  --coaching-file coaching-fao.txt
```

(Schrijf uw eigen coachinginhoud — de bovenstaande feiten illustreren de *vorm*: een paar grammaticaregels met grote impact, een kleine woordenlijst van termen die het model fout doet, een registerinstructie. Taalkaarten op [champollion.dev/languages](https://champollion.dev/languages) vermelden typologiebronnen waaruit u kunt putten.)

Vergelijk met de naïeve basislijn via `mt-eval compare <naive_log> <coached_log>`, itereer, en publiceer uw beste run. De run wordt automatisch gepubliceerd met conditie `coached`; als u wilt dat het scorebord een benoemde methode toont in plaats van het generieke label, voeg dan een methodekaart toe bij het publiceren (de publicatiestroom biedt een wizard). De naïeve basislijn verslaan op een taalpaar met weinig middelen met niets anders dan prompt engineering is een echte, publiceerbare bevinding — zie het volledige [Gecoachte LLM-prompting-kookboek](/docs/tutorials/coached-llm-prompting) voor ontwerprichtlijnen.

## Tier 3 — Een methode bouwen

De meest ambitieuze bijdrage: implementeer het `TranslationMethod`-protocol (`translate(entries, config)`) en benchmark een werkelijk systeem, niet een prompt. De harness voert het uit via `--method <plugin-dir>` en sluit uw methodekaart in de run-kaart in. Patronen met uitgewerkte kookboeken:

- **[FST-gated pipelines](/docs/tutorials/fst-gated-pipeline)** — elk kandidaatwoord wordt gecontroleerd door een morfologische analysator; het LLM genereert opnieuw totdat de gate slaagt. Semi-deterministisch, morfologisch gegarandeerde uitvoer.
- **[Woordenboekversterkte generatie](/docs/tutorials/dictionary-augmented-llm)** — zoek brontermen op in een tweetalig lexicon tijdens het vertalen en beperk de uitvoer.
- [Geketende modellen](/docs/tutorials/chained-models), [few-shot retrieval](/docs/tutorials/few-shot-prompting), [terugvertaling](/docs/tutorials/back-translation), [regelgebaseerde hybriden](/docs/tutorials/rule-based-hybrid)…

Methoden declareren een **afhankelijkheidsklasse** (S/O/A1/A2/X — zie [de methodespecificatie](/docs/specifications/methods#method-validity-and-dependency-classes)) die beschrijft wat ze nodig hebben om uit te voeren en over te dragen: een op zichzelf staande pipeline is Klasse S; een pipeline die tijdens de uitvoering een gelicentieerde woordenboek-API aanroept is A2. Declareer eerlijk — de klasse bepaalt waar uw methode kan meedingen, en manifesten worden geauditeerd.

## Waarom dit verder reikt dan het scorebord

Elke gepubliceerde run is onafhankelijk bewijs over MT-kwaliteit voor een taalpaar dat commerciële providers niet meten. De wachtrij fungeert ook als een publiek register van *vraag*: welke paren de community het waard acht om te meten, wat dekking kost tegen huidige API-prijzen, en hoe ver gedoneerde rekenkracht reikt. Wanneer wij financieringsinstanties vragen om systematische sweeps te financieren, zijn deze wachtrij en de vulgraad het vraagbewijs.