---
sidebar_position: 4
title: "Methode-interface"
related:
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
    note: "Put this interface on the leaderboard"
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
    note: "A full method, built end-to-end"
---
# Gedeelde Methode-interface

> **Samenvatting.** Deze pagina specificeert het `TranslationMethod`-protocol dat alle Arena-methoden moeten implementeren, de zes methodeklassen (`raw-llm`, `coached-llm`, `pipeline`, `custom-plugin`, `api`, `human`), het methode-pluginformaat en de **afhankelijkheidsklassen** (S/O/A1/A2/X) die bepalen of een methode in de evaluatiesandbox kan worden uitgevoerd en in aanmerking komt voor prijzen. Elke aanpak die dit protocol implementeert, kan worden gebenchmarkt; wat de methode vereist, bepaalt in welke categorie zij kan meedingen.

De eval-harness en champollion delen een gemeenschappelijk concept van **vertaalmethode**. Een methode is elke procedure die brontekst als invoer neemt en vertaalde tekst produceert — of het nu een directe LLM-aanroep is, een meerfasige pijplijn, een externe API, of een menselijke vertaler.

## Architectuur

```
Method Plugin (v2 Spec)
├── method.json           ← Manifest (name, class, entry_point, dependencies, metadata)
├── method_card.json      ← Leaderboard description (what, not how)
├── pipeline.py           ← Python module implementing TranslationMethod
└── (optional helpers)    ← Additional Python modules
```

Geladen via `--method path/to/dir`. De harness detecteert niets automatisch.

## Twee systemen, één interface

| | Eval Harness | champollion |
|---|---|---|
| **Taal** | Python | Node.js |
| **Toegangspunt** | `translate.py` | `translate.js` |
| **Interface** | `TranslationMethod`-protocol | `methodPlugin`-configuratie |
| **Doel** | Batchevaluatie met scoring | Live lokalisatie in dev/CI |
| **Uitvoer** | Run card met metriekwaarden | Vertaalde locale-bestanden |

Een methode die beide systemen ondersteunt, biedt twee toegangspunten — één voor elke taalruntime. De **method card** vormt de brug: zij beschrijft de methode in een formaat dat beide systemen begrijpen.

## Method Card {#method-card}

Een method card beschrijft *wat* een vertaalmethode is, zonder eigendomsgevoelige details zoals de volledige systeemprompt prijs te geven. Zij beantwoordt de volgende vragen:

- Tot welke klasse behoort deze methode? (ruwe LLM, gecoachte LLM, pijplijn, API, enz.)
- Welke hulpmiddelen gebruikt zij? (FST-analysator, woordenboek, enz.)
- Is de implementatie open source?
- Welke taalparen worden ondersteund?

Zie de [Method Card Spec](/docs/specifications/methods#method-card) voor het volledige JSON-schema.

### Voorbeeld

```json
{
  "method_id": "fst-gated-v8",
  "name": "FST-Gated Coached Translation v8",
  "class": "pipeline",
  "description": "LLM translation with morphological validation. Failed words are retried with FST feedback.",
  "author": "Curtis Forbes",
  "tools_used": ["HFST morphological analyzer", "Wolvengrey dictionary"],
  "open_source": false,
  "dependency_class": "A2",
  "supported_pairs": ["eng>crk"]
}
```

Het veld `dependency_class` geeft een samenvatting van wat de methode nodig heeft om te worden uitgevoerd en overgedragen — zie [Methodegeldigheid en afhankelijkheidsklassen](#method-validity-and-dependency-classes) hieronder.

### Methodeklassen

| Klasse | Beschrijving |
|-------|-------------|
| `raw-llm` | Directe LLM-aanroep met minimale instructie |
| `coached-llm` | LLM met gestructureerde prompt, voorbeelden en beperkingen |
| `pipeline` | Meerfasige pijplijn met deterministische componenten |
| `custom-plugin` | Extern proces dat het `TranslationMethod`-protocol implementeert |
| `api` | Externe vertaal-API (Google Translate, DeepL, enz.) |
| `human` | Menselijke vertaling (voor het vaststellen van basislijnen) |

## Methodegeldigheid en afhankelijkheidsklassen {#method-validity-and-dependency-classes}

Een methode is slechts zo uitvoerbaar en overdraagbaar als haar minst beschikbare afhankelijkheid. Twee Arena-mechanismen zijn afhankelijk van een exacte kennis van wat een methode vereist:

1. **Sandbox-evaluatie** ([Benchmark Specification §8.2](/docs/specifications/benchmark)) — officiële goudstandaard-scores worden gegenereerd in een sandbox waarvan het netwerkbeleid **standaard-weigeren** is. Een methode die stilzwijgend een externe dienst vereist, kan geen officiële score produceren.
2. **Prijsoverdracht** ([Prize Specification](/docs/specifications/prizes)) — prijswinnende methoden worden overgedragen aan de bestuursorganisatie van de taalgemeenschap. Een methode die inhoud bevat waarop de indiener geen rechten heeft, kan niet rechtmatig worden overgedragen. De indiener moet de rechten bezitten (of verleend hebben gekregen) op alles wat in het pakket is opgenomen.

Om beide controles mechanisch in plaats van ad hoc te maken, declareert elke methode een **afhankelijkheidsklasse**, afgeleid van een **afhankelijkheidsmanifest** in `method.json`.

> **Opmerking over naamgeving.** *Methodeklasse* (§hierboven: `raw-llm`, `pipeline`, …) beschrijft *hoe een methode vertaalt*. *Afhankelijkheidsklasse* (dit gedeelte) beschrijft *wat een methode nodig heeft om te worden uitgevoerd en overgedragen*. Dit zijn onafhankelijke assen: een `pipeline`-methode kan tot elke afhankelijkheidsklasse behoren.

### De vijf afhankelijkheidsklassen

| Klasse | Naam | Definitie | Uitvoerbaar in sandbox? | In aanmerking voor prijs? |
|-------|------|-----------|-------------------|-----------------|
| **S** | Zelfvoorzienend | Alle code, gegevens, modellen en gewichten worden meegeleverd in de methodemap, onder licenties die herdistributie en overdracht aan de gemeenschap toestaan. | ✅ Ja, zonder aanpassingen | ✅ Ja |
| **O** | Open extern | Afhankelijk van extern gehoste artefacten onder open licenties die herdistributie toestaan (inclusief copyleft-licenties zoals AGPL) — bijv. een FST die bij installatie wordt gedownload. | ✅ Ja — artefacten zijn vastgepind en **gespiegeld in de inzending** | ✅ Ja, met licentiecompatibiliteitsvoorwaarden: copyleft-bepalingen blijven behouden bij overdracht, en de gemeenschap ontvangt dezelfde rechten die de licentie aan iedereen verleent |
| **A1** | API-afhankelijk, vervangbaar | Vereist runtime LLM-inferentie, waarbij het model **vervangbare configuratie** is — elk voldoende capabel model kan worden ingeplugd. De waarde van de methode ligt in haar prompts, coachinggegevens en code, niet in het model van één specifieke aanbieder. | ⚠️ Alleen via de **LLM-gateway** die de sandboxspecificatie definieert (🔲 gepland — zie hieronder) | ⚠️ Voorwaardelijk — zie hieronder |
| **A2** | API-afhankelijk, niet-vervangbaar | Vereist runtime-aanroepen naar een externe gegevens- of dienst-API die niet gespiegeld of vervangen kan worden — doorgaans omdat de aangeboden inhoud eigendomsrechtelijk beschermd of niet-gelicentieerd is (bijv. een woordenboek-API waarvan het onderliggende woordenboek geen publieke licentie heeft). | ❌ Nee — de afhankelijkheid kan niet in de sandbox bestaan zonder toestemming van de rechthebbende | ❌ Niet totdat de rechthebbende sandbox-opname **en** overdrachtsrechten verleent. Toegestaan op het open (ontwikkelingssegment-)leaderboard met een zichtbare **"externe afhankelijkheid"**-markering |
| **X** | Gesloten | Bevat inhoud waarop de indiener geen recht heeft tot herdistributie — niet-gelicentieerde datasets, gescrapte eigendomsinhoud, licentie-incompatibele componenten. | ❌ | ❌ Niet toegelaten in elke categorie. Het bundelen van inhoud zonder rechten is een licentieovertreding, ongeacht waar de methode wordt uitgevoerd |

**Effectieve klasse.** De afhankelijkheidsklasse van een methode is de *meest beperkende* klasse onder al haar gedeclareerde afhankelijkheden, in de volgorde S < O < A1 < A2 < X. Één niet-gelicentieerd woordenboek maakt een verder zelfvoorzienende pijplijn tot Klasse A2 (indien benaderd tijdens runtime) of Klasse X (indien gebundeld zonder rechten).

### Het A1/A2-onderscheid: vervangbaarheid

De meeste methoden roepen LLM's aan. De Arena doet niet alsof dit anders is — maar zij maakt onderscheid tussen twee zeer verschillende soorten API-afhankelijkheid:

- **A1 (vervangbaar):** De API biedt generieke LLM-inferentie. De modelidentificator is configuratie: de methode moet end-to-end kunnen worden uitgevoerd tegen elk compatibel inferentie-eindpunt, inclusief een door de gemeenschap gehost open-gewichtenmodel. De uitvoerkwaliteit kan per model verschillen — dat is het risico van de ontwikkelaar, en officiële scores zijn gekoppeld aan het vastgepinde model dat bij de evaluatie is gebruikt. Een methode die afhankelijk is van **aanbiederzijdige toestand** (een fine-tune die alleen bij de aanbieder wordt gehost, bestandsopslag van de aanbieder, aanbiederspecifieke assistenten) is *niet* vervangbaar: die toestand kan niet worden uitgewisseld, waardoor de afhankelijkheid A2 is, tenzij de onderliggende gewichten of gegevens in de inzending zijn opgenomen.
- **A2 (niet-vervangbaar):** De API biedt iets unieks — doorgaans eigendomsrechtelijk beschermde of niet-gelicentieerde gegevens. Geen alternatief eindpunt kan dit leveren, en de inhoud kan niet in de sandbox worden gespiegeld zonder toestemming van de rechthebbende. De methode werkt op het open leaderboard (gemarkeerd), maar kan geen officiële sandbox-scores produceren of in aanmerking komen voor prijzen totdat de benodigde toestemmingen zijn verkregen.

**Wat een A1-prijsoverdracht daadwerkelijk omvat.** De gemeenschap ontvangt het model niet — niemand kan de gewichten van Anthropic, Google of OpenAI overdragen. De overdracht omvat het volledige recept *rondom* het model: alle prompts, coachinggegevens, pijplijncode, retry-logica, configuratie en gedocumenteerde modelvereisten. Omdat het model per definitie vervangbaar is, kan de gemeenschap de overgedragen methode richten op elke gewenste aanbieder — of op een open-gewichtenmodel op eigen hardware — zonder betrokkenheid van de ontwikkelaar. Het recept is eigendom; de motor wordt gehuurd en is vervangbaar.

### Afhankelijkheidsmanifest (`method.json`)

Elke methode declareert haar afhankelijkheden in het manifest `method.json`. Elke vermelding registreert wat het artefact is, waar het vandaan komt, welke licentie erop van toepassing is en hoe de methode er toegang toe heeft:

```json
{
  "name": "FST-Gated Coached Translation v8",
  "method_id": "fst-gated-v8",
  "class": "pipeline",
  "entry_point": "pipeline:PipelineMethod",
  "supported_pairs": ["eng>crk"],
  "dependency_class": "A2",
  "dependencies": [
    {
      "id": "giellalt-lang-crk-fst",
      "kind": "software",
      "license": "AGPL-3.0-or-later",
      "access": "mirrored",
      "source": "https://github.com/giellalt/lang-crk",
      "pin": "sha256:3f1a…",
      "redistributable": true,
      "transferable": true
    },
    {
      "id": "llm-inference",
      "kind": "model",
      "license": "proprietary",
      "access": "gateway",
      "source": "openrouter:google/gemini-2.5-flash",
      "substitutable": true,
      "redistributable": false,
      "transferable": false,
      "notes": "Any compatible chat-completions endpoint works; the model slug is configuration."
    },
    {
      "id": "crk-dictionary-api",
      "kind": "service",
      "license": "none",
      "access": "external-api",
      "source": "https://itwewina.altlab.app/",
      "redistributable": false,
      "transferable": false,
      "notes": "Dictionary content has no public license; runtime lookups only. Class A2 until the rights holders grant permission."
    }
  ]
}
```

| Veld | Vereist | Beschrijving |
|-------|----------|-------------|
| `id` | ✅ | Stabiele identificator voor de afhankelijkheid |
| `kind` | ✅ | `data`, `model`, `software`, of `service` |
| `license` | ✅ | SPDX-identificator, `proprietary`, of `none`. `none` betekent dat er geen publieke licentie bestaat — behandeld als alle rechten voorbehouden |
| `access` | ✅ | `bundled` (wordt meegeleverd in de methodemap), `mirrored` (opgehaald bij installatie, vastgepind, opgenomen in de inzending), `gateway` (runtime LLM-inferentie via de evaluatiegateway), `external-api` (elke andere runtime-netwerkaanroep) |
| `source` | ✅ | Canonieke URL of `provider:slug`-identificator |
| `pin` | voor `mirrored` | Versie, commit of inhoudshasj die het exacte artefact vastpint |
| `substitutable` | voor `gateway`/`external-api` | Of elk compatibel eindpunt deze afhankelijkheid kan bedienen |
| `redistributable` | ✅ | Of de licentie herdistributie van het artefact toestaat |
| `transferable` | ✅ | Of het artefact (of de rechten daarop) kan worden overgedragen aan een gemeenschap onder de voorwaarden van prijsoverdracht |
| `notes` | ❌ | Vrije-vormcontext |

**Klassederivatie.** Elke afhankelijkheid draagt een klasse bij; de `dependency_class` van de methode is de meest beperkende:

| Afhankelijkheidsprofiel | Draagt bij |
|--------------------|-------------|
| `bundled` + licentie staat herdistributie en overdracht toe | S |
| `mirrored` + open licentie die herdistributie toestaat (copyleft inbegrepen) | O |
| `gateway` + `substitutable: true` (LLM-inferentie) | A1 |
| `external-api`, of `gateway` met `substitutable: false` | A2 |
| `bundled` + `license: none` of licentie die herdistributie niet toestaat | X |

De gedeclareerde `dependency_class` moet overeenkomen met de klasse die de harness afleidt uit het manifest. Een afwijking is een validatiefout.

Een methode zonder **externe** afhankelijkheden declareert `"dependency_class": "S"` en `"dependencies": []`. De lege array is een bevestigende verklaring die net als elke andere wordt geauditeerd.

### Hoe geldigheid wordt geverifieerd

Drie lagen, van goedkoopst tot meest gezaghebbend:

1. **Manifestaudit.** De harness leidt de effectieve klasse af uit het manifest en verwerpt afwijkingen. Reviewers controleren elke gedeclareerde afhankelijkheid aan de hand van de opgegeven licentie en bron — een afhankelijkheid die als `redistributable: true` is gedeclareerd maar waarvan de upstream-licentie anders luidt, slaagt niet voor de review.
2. **Statische analyse.** De ingediende code wordt gescand op netwerkaanroepen, dynamische downloads en bestandssysteemtoegang die niet in het manifest zijn opgenomen. Een *niet-gedeclareerde* afhankelijkheid die bij de review wordt gevonden, is grond voor afwijzing, ongeacht welke klasse zij zou hebben gehad — het manifest moet volledig zijn, niet alleen nauwkeurig.
3. **Sandbox-netwerkbeleid.** De sandboxspecificatie vereist **standaard-weigeren egress**: methodecontainers krijgen geen netwerktoegang tenzij een pad expliciet op de allowlist staat. Het enige egress-pad dat de specificatie definieert, is de **LLM-gateway** — een inferentieproxy die wordt beheerd door de evaluatie-infrastructuur, beperkt tot een expliciete allowlist van vastgepinde modellen, waarbij elk verzoek en elke respons wordt gelogd voor audit na de run. Alles wat niet op de allowlist staat, mislukt op de netwerklaag, niet op de beleidslaag. Zie [Benchmark Specification §8.6](/docs/specifications/benchmark) voor het netwerkbeleid en het gateway-ontwerp.

> 🔲 **Gepland.** De sandbox en haar LLM-gateway zijn gespecificeerd maar nog niet gebouwd. Totdat de gateway operationeel is, kunnen alleen Klasse S- en Klasse O-methoden in de sandbox worden geëvalueerd; Klasse A1-methoden komen *in principe* in aanmerking voor prijzen, maar kunnen nog geen officiële goudstandaard-scores produceren. Deze pagina beschrijft wat de specificatie vereist, niet wat momenteel wordt uitgevoerd.

### Weergave op het leaderboard

- Het leaderboard toont de afhankelijkheidsklasse van elke methode naast haar methodeklasse-badge.
- Klasse A2-methoden op het open leaderboard dragen een zichtbare **"externe afhankelijkheid"**-markering: hun scores zijn afhankelijk van een externe dienst die kan veranderen of verdwijnen, en zij komen momenteel niet in aanmerking voor prijzen.
- Klasse X-methoden worden niet vermeld.

## Eval Harness: TranslationMethod-protocol {#eval-harness-translationmethod-protocol}

De eval-harness maakt gebruik van Python's structurele typering (`Protocol`) voor plugins. Elke klasse met de juiste methodehandtekening werkt — overerving is niet vereist:

```python
class MyMethod:
    async def translate(self, entries: list[dict], config: RunConfig) -> list[dict]:
        results = []
        for entry in entries:
            translation = await self.do_translation(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translation,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "error": None,
                "tool_calls": [],
                "tool_call_count": 0,
                "metadata": {},
            })
        return results
```

Zie het [Plugin Protocol](/docs/specifications/methods#eval-harness-translationmethod-protocol) voor volledige documentatie, inclusief wrapper-voorbeelden voor niet-Python-methoden.

## champollion: methodPlugin-configuratie

In champollion worden methoden per taalpaar geregistreerd in `champollion.config.json`:

```json
{
  "version": 3,
  "pairs": {
    "en:crk": {
      "methodPlugin": "crk-coached-v1"
    }
  }
}
```

Zie de [Plugin Spec](https://champollion.dev/docs/reference/plugin-spec) voor de champollion-zijdige interface.

## Leaderboard-integratie

Wanneer een method card aan een run is gekoppeld (via `--method-card`), wordt zij ingesloten in de run card en weergegeven op het leaderboard:

```bash
# Run with method card attached
mt-eval run \
  --method path/to/my-method \
  --corpus data/edtekla-dev-v1.json \
  --method-card method_card.json

# Publish to the leaderboard
mt-eval publish eval/logs/harness/your-run-card.json
```

Als er geen `--method-card` is opgegeven, start `mt-eval publish` een interactieve wizard die u begeleidt bij het beschrijven van uw methode.

Het leaderboard toont:
- **Klassebadge** — visuele indicator (bijv. "pipeline", "coached-llm")
- **Afhankelijkheidsklasse** — S/O/A1/A2 (zie [Methodegeldigheid en afhankelijkheidsklassen](#method-validity-and-dependency-classes)); A2-methoden dragen een "externe afhankelijkheid"-markering
- **Methodenaam** — afkomstig uit de method card
- **Gebruikte hulpmiddelen** — vermeld in de method card
- **Open source-indicator**

Wanneer er geen method card is gekoppeld, toont het leaderboard de harness-native configuratie (model, promptversie, temperatuur, ingeschakelde hulpmiddelen).

:::danger TRAIN NIET op evaluatiegegevens
Methoden waarvan het ontwikkelingsproces blootstelling aan de evaluatiedataset omvatte — als trainingsgegevens, few-shot-voorbeelden, woordenboekitems of prompt-tuningmateriaal — worden **gediskwalificeerd** van het leaderboard. Zie [MT Evaluation](/docs/leaderboard/rules) voor wat een goede methode onderscheidt van een slechte.
:::

---

## Zie ook

- [MT Evaluation](/docs/leaderboard/rules) — overzicht, leaderboard-waarde en richtlijnen voor goede en slechte methoden
- [Eval Harness](/docs/specifications/harness) — hoe evaluaties worden uitgevoerd
- [Evaluatiedatasets](/docs/leaderboard/datasets) — beschikbare datasets (EDTeKLA, FLORES+)
- [Run Card Specification](/docs/specifications/run-card) — het JSON-schema van de run card
- [Plugin Spec](https://champollion.dev/docs/reference/plugin-spec) — champollion-zijdige plugin-interface
- [Method Leaderboard](https://champollion.dev/leaderboard) — live benchmarkscores
- [Benchmark Specification](/docs/specifications/benchmark) — evaluatieprotocol, corpusformaat, run card-schema
- [Scoring Specification](/docs/specifications/scoring) — SSOT voor metriekwaarden, samengestelde gewichten en kwaliteitsniveaus