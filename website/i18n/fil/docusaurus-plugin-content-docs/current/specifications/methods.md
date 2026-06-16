---
sidebar_position: 4
title: "Interface ng Method"
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
# Ibinahaging Method Interface

> **Executive Summary.** Tinutukoy ng pahinang ito ang `TranslationMethod` protocol na dapat ipatupad ng lahat ng Arena methods, ang anim na method classes (`raw-llm`, `coached-llm`, `pipeline`, `custom-plugin`, `api`, `human`), ang method plugin format, at ang **dependency classes** (S/O/A1/A2/X) na tumutukoy kung maaaring tumakbo ang isang method sa evaluation sandbox at maging kuwalipikado para sa mga premyo. Maaaring i-benchmark ang anumang approach na nagpapatupad ng protocol na ito; ang mga dependency nito ang tumutukoy kung saan ito maaaring makipagkompetensiya.

Ang eval harness at champollion ay may iisang konsepto ng **translation method**. Ang method ay anumang procedure na tumatanggap ng source text at gumagawa ng translated text — direktang LLM call man ito, multi-stage pipeline, third-party API, o human translator.

## Arkitektura

```
Method Plugin (v2 Spec)
├── method.json           ← Manifest (name, class, entry_point, dependencies, metadata)
├── method_card.json      ← Leaderboard description (what, not how)
├── pipeline.py           ← Python module implementing TranslationMethod
└── (optional helpers)    ← Additional Python modules
```

Nilo-load sa pamamagitan ng `--method path/to/dir`. Walang awtomatikong dini-discover ang harness.

## Dalawang Sistema, Isang Interface

| | Eval Harness | champollion |
|---|---|---|
| **Wika** | Python | Node.js |
| **Entry point** | `translate.py` | `translate.js` |
| **Interface** | `TranslationMethod` protocol | `methodPlugin` config |
| **Layunin** | Batch evaluation na may scoring | Live localization sa dev/CI |
| **Output** | Run card na may metrics | Translated locale files |

Ang method na sumusuporta sa parehong sistema ay nagbibigay ng dalawang entry point — isa para sa bawat language runtime. Ang **method card** ang tulay: inilalarawan nito ang method sa format na nauunawaan ng parehong sistema.

## Method Card {#method-card}

Inilalarawan ng method card kung *ano* ang isang translation method nang hindi ibinubunyag ang mga proprietary detail tulad ng buong system prompt. Sinasagot nito ang:

- Anong class ng method ito? (raw LLM, coached LLM, pipeline, API, atbp.)
- Anong tools ang ginagamit nito? (FST analyzer, dictionary, atbp.)
- Open source ba ang implementation?
- Anong language pairs ang sinusuportahan nito?

Tingnan ang [Method Card Spec](/docs/specifications/methods#method-card) para sa buong JSON schema.

### Halimbawa

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

Ibinubuod ng `dependency_class` field kung ano ang kailangan ng method upang tumakbo at mailipat — tingnan ang [Validity ng Method at Dependency Classes](#method-validity-and-dependency-classes) sa ibaba.

### Method Classes

| Class | Paglalarawan |
|-------|-------------|
| `raw-llm` | Direktang LLM call na may minimal na instruction |
| `coached-llm` | LLM na may structured prompt, mga halimbawa, at constraints |
| `pipeline` | Multi-stage pipeline na may deterministic components |
| `custom-plugin` | External process na nagpapatupad ng `TranslationMethod` protocol |
| `api` | Third-party translation API (Google Translate, DeepL, atbp.) |
| `human` | Human translation (para magtatag ng baselines) |

## Validity ng Method at Dependency Classes {#method-validity-and-dependency-classes}

Ang pagiging runnable at transferable ng isang method ay nakasalalay sa least available dependency nito. Dalawang mekanismo ng Arena ang nakadepende sa eksaktong pagkaalam kung ano ang kailangan ng isang method:

1. **Sandboxed evaluation** ([Benchmark Specification §8.2](/docs/specifications/benchmark)) — ang opisyal na gold-standard scores ay nagmumula sa sandbox na ang network policy ay **default-deny**. Ang method na tahimik na nangangailangan ng external service ay hindi makagagawa ng opisyal na score.
2. **Prize transfer** ([Prize Specification](/docs/specifications/prizes)) — ang prize-winning methods ay inililipat sa governance organization ng language community. Ang method na nagba-bundle ng content na walang karapatan ang submitter na isama ay hindi maaaring legal na mailipat. Dapat hawak ng submitter (o ipinagkaloob sa kanya) ang mga karapatan sa lahat ng nasa kahon.

Upang gawing mekanikal at hindi ad hoc ang parehong pagsusuri, nagdedeklara ang bawat method ng **dependency class**, na hinango mula sa **dependency manifest** sa `method.json`.

> **Tala sa pagpapangalan.** Inilalarawan ng *method class* (§sa itaas: `raw-llm`, `pipeline`, …) kung *paano nagsasalin ang method*. Inilalarawan ng *dependency class* (seksyong ito) kung *ano ang kailangan ng method upang tumakbo at mailipat*. Magkahiwalay na axis ang mga ito: ang isang `pipeline` method ay maaaring nasa anumang dependency class.

### Ang Limang Dependency Classes

| Class | Pangalan | Depinisyon | Runnable sa sandbox? | Eligible sa premyo? |
|-------|------|-----------|-------------------|-----------------|
| **S** | Self-contained | Lahat ng code, data, models, at weights ay kasama sa method directory, sa ilalim ng mga lisensiyang nagpapahintulot ng redistribution at community transfer. | ✅ Oo, as-is | ✅ Oo |
| **O** | Open external | Nakadepende sa externally hosted artifacts sa ilalim ng open licenses na nagpapahintulot ng redistribution (kabilang ang copyleft licenses tulad ng AGPL) — hal., FST na dina-download sa install time. | ✅ Oo — ang artifacts ay pinned at **naka-mirror sa submission** | ✅ Oo, may mga kondisyon sa license compatibility: pinananatili ang copyleft terms sa pamamagitan ng transfer, at natatanggap ng community ang parehong karapatang ibinibigay ng lisensiya sa lahat |
| **A1** | API-dependent, substitutable | Nangangailangan ng runtime LLM inference, kung saan ang model ay **substitutable configuration** — maaaring ipalit ang anumang sapat ang kakayahang model. Nasa prompts, coaching data, at code ang halaga ng method, hindi sa model ng iisang provider. | ⚠️ Sa pamamagitan lamang ng **LLM gateway** na tinutukoy ng sandbox specification (🔲 planado — tingnan sa ibaba) | ⚠️ Kondisyonal — tingnan sa ibaba |
| **A2** | API-dependent, non-substitutable | Nangangailangan ng runtime calls sa external data o service API na hindi maaaring i-mirror o palitan — karaniwan dahil proprietary o walang lisensiya ang served content (hal., dictionary API na ang underlying dictionary ay walang public license). | ❌ Hindi — hindi maaaring umiral ang dependency sa sandbox nang walang pahintulot ng rights holder | ❌ Hindi hangga’t hindi nagbibigay ang rights holder ng sandbox-inclusion **at** transfer permissions. Pinapayagan sa open (development-segment) leaderboard na may nakikitang **"panlabas na dependency"** flag |
| **X** | Closed | Nagba-bundle ng content na walang karapatan ang submitter na i-redistribute — unlicensed datasets, scraped proprietary content, license-incompatible components. | ❌ | ❌ Hindi tinatanggap sa anumang lane. Ang pagba-bundle ng content nang walang karapatan ay paglabag sa lisensiya saanman tumakbo ang method |

**Effective class.** Ang dependency class ng isang method ay ang *pinaka-restrictive* na class sa lahat ng dineklarang dependencies nito, sa ayos na S < O < A1 < A2 < X. Ang isang unlicensed dictionary ay gagawing Class A2 ang isang self-contained sana na pipeline (kung ina-access sa runtime) o Class X (kung naka-bundle nang walang karapatan).

### Ang Pagkakaiba ng A1/A2: Substitutability

Karamihan ng methods ay tumatawag sa LLMs. Hindi ito ipinagkakaila ng Arena — ngunit pinag-iiba nito ang dalawang magkaibang uri ng API dependency:

- **A1 (substitutable):** Nagbibigay ang API ng commodity LLM inference. Configuration ang model identifier: dapat tumakbo ang method end-to-end laban sa anumang compatible inference endpoint, kabilang ang community-hosted open-weight model. Maaaring magkaiba ang output quality sa iba’t ibang model — iyon ang panganib ng developer, at nakatali ang opisyal na scores sa pinned model na ginamit sa evaluation. Ang method na nakadepende sa **provider-side state** (fine-tune na hosted lamang sa provider, provider file stores, provider-specific assistants) ay *hindi* substitutable: hindi maaaring alisin o palitan ang state na iyon, kaya A2 ang dependency maliban kung kasama sa submission ang underlying weights o data.
- **A2 (non-substitutable):** May sineserbisyong natatangi ang API — karaniwang proprietary o unlicensed data. Walang alternatibong endpoint na makapagbibigay nito, at hindi maaaring i-mirror ang content sa sandbox nang walang pahintulot ng rights holder. Gumagana ang method sa open leaderboard (may flag), ngunit hindi makagagawa ng opisyal na sandbox scores o magiging kuwalipikado para sa mga premyo hangga’t walang mga pahintulot.

**Ano talaga ang naipapasa ng A1 prize transfer.** Hindi natatanggap ng community ang model — walang sinuman ang makapaglilipat ng weights ng Anthropic, Google, o OpenAI. Saklaw ng transfer ang kumpletong recipe *sa paligid* ng model: lahat ng prompts, coaching data, pipeline code, retry logic, configuration, at dokumentadong model requirements. Dahil substitutable by construction ang model, maaaring ituro ng community ang nailipat na method sa anumang provider na pipiliin nila — o sa open-weight model sa sarili nilang hardware — nang hindi kinakailangan ang developer. Pag-aari ang recipe; inuupahan at napapalitan ang engine.

### Dependency Manifest (`method.json`)

Idinedeklara ng bawat method ang dependencies nito sa `method.json` manifest. Itinatala ng bawat entry kung ano ang artifact, saan ito nagmumula, anong lisensiya ang sumasaklaw dito, at paano ito ina-access ng method:

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

| Field | Required | Paglalarawan |
|-------|----------|-------------|
| `id` | ✅ | Stable identifier para sa dependency |
| `kind` | ✅ | `data`, `model`, `software`, o `service` |
| `license` | ✅ | SPDX identifier, `proprietary`, o `none`. Ang `none` ay nangangahulugang walang public license — itinuturing na all-rights-reserved |
| `access` | ✅ | `bundled` (kasama sa method directory), `mirrored` (kinukuha sa install, pinned, vendored sa submission), `gateway` (runtime LLM inference sa pamamagitan ng evaluation gateway), `external-api` (anumang iba pang runtime network call) |
| `source` | ✅ | Canonical URL o `provider:slug` identifier |
| `pin` | para sa `mirrored` | Version, commit, o content hash na nagpi-pin sa eksaktong artifact |
| `substitutable` | para sa `gateway`/`external-api` | Kung maaaring i-serve ng anumang compatible endpoint ang dependency na ito |
| `redistributable` | ✅ | Kung pinahihintulutan ng lisensiya ang redistribution ng artifact |
| `transferable` | ✅ | Kung maaaring mailipat ang artifact (o mga karapatan dito) sa community sa ilalim ng prize transfer terms |
| `notes` | ❌ | Free-form context |

**Class derivation.** Nag-aambag ng class ang bawat dependency; ang `dependency_class` ng method ay ang pinaka-restrictive:

| Dependency profile | Nag-aambag |
|--------------------|-------------|
| `bundled` + pinahihintulutan ng lisensiya ang redistribution at transfer | S |
| `mirrored` + open license na nagpapahintulot ng redistribution (kabilang ang copyleft) | O |
| `gateway` + `substitutable: true` (LLM inference) | A1 |
| `external-api`, o `gateway` na may `substitutable: false` | A2 |
| `bundled` + `license: none` o redistribution-incompatible license | X |

Dapat tumugma ang dineklarang `dependency_class` sa class na hinango ng harness mula sa manifest. Ang mismatch ay validation error.

Ang method na **walang** external dependencies ay nagdedeklara ng `"dependency_class": "S"` at `"dependencies": []`. Ang empty array ay affirmative statement, na ina-audit tulad ng iba pa.

### Paano Bine-verify ang Validity

Tatlong layer, mula sa pinakamura hanggang sa pinaka-authoritative:

1. **Manifest audit.** Hinahango ng harness ang effective class mula sa manifest at nire-reject ang mismatches. Sinusuri ng reviewers ang bawat dineklarang dependency laban sa nakasaad nitong lisensiya at source — ang dependency na dineklarang `redistributable: true` ngunit iba ang sinasabi ng upstream license ay babagsak sa review.
2. **Static analysis.** Ini-scan ang submitted code para sa network calls, dynamic downloads, at filesystem access na hindi isinasaalang-alang ng manifest. Ang *undeclared* dependency na matatagpuan sa review ay batayan para sa rejection anuman ang class sana nito — dapat kumpleto ang manifest, hindi lamang tumpak.
3. **Sandbox network policy.** Kinakailangan ng sandbox specification ang **default-deny egress**: walang network access ang method containers maliban kung ang path ay tahasang nasa allowlist. Ang tanging egress path na tinutukoy ng specification ay ang **LLM gateway** — isang inference proxy na pinapatakbo ng evaluation infrastructure, limitado sa tahasang allowlist ng pinned models, at naka-log ang bawat request at response para sa post-run audit. Anumang wala sa allowlist ay mabibigo sa network layer, hindi sa policy layer. Tingnan ang [Benchmark Specification §8.6](/docs/specifications/benchmark) para sa network policy at gateway design.

> 🔲 **Planado.** Natukoy na sa specification ang sandbox at ang LLM gateway nito ngunit hindi pa nabubuo. Hangga’t hindi operational ang gateway, Class S at Class O methods lamang ang maaaring i-evaluate sa sandbox; ang Class A1 methods ay prize-eligible *sa prinsipyo* ngunit hindi pa makagagawa ng opisyal na gold-standard scores. Inilalarawan ng pahinang ito kung ano ang hinihingi ng specification, hindi kung ano ang kasalukuyang tumatakbo.

### Display ng Leaderboard

- Ipinapakita ng leaderboard ang dependency class ng bawat method katabi ng method class badge nito.
- Ang Class A2 methods sa open leaderboard ay may nakikitang **"panlabas na dependency"** flag: nakadepende ang kanilang scores sa third-party service na maaaring magbago o mawala, at hindi sila kasalukuyang prize-eligible.
- Hindi inililista ang Class X methods.

## Eval Harness: TranslationMethod Protocol {#eval-harness-translationmethod-protocol}

Gumagamit ang eval harness ng structural typing ng Python (`Protocol`) para sa plugins. Gagana ang anumang class na may tamang method signature — hindi kailangan ng inheritance:

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

Tingnan ang [Plugin Protocol](/docs/specifications/methods#eval-harness-translationmethod-protocol) para sa kumpletong dokumentasyon kabilang ang mga wrapper example para sa non-Python methods.

## champollion: methodPlugin Config

Sa champollion, nire-register ang methods per language pair sa `champollion.config.json`:

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

Tingnan ang [Plugin Spec](https://champollion.dev/docs/reference/plugin-spec) para sa champollion-side interface.

## Integrasyon sa Leaderboard

Kapag naka-attach ang method card sa isang run (sa pamamagitan ng `--method-card`), ine-embed ito sa run card at ipinapakita sa leaderboard:

```bash
# Run with method card attached
mt-eval run \
  --method path/to/my-method \
  --corpus data/edtekla-dev-v1.json \
  --method-card method_card.json

# Publish to the leaderboard
mt-eval publish eval/logs/harness/your-run-card.json
```

Kung walang ibinigay na `--method-card`, ilulunsad ng `mt-eval publish` ang interactive wizard na gagabay sa inyo sa paglalarawan ng inyong method.

Ipinapakita ng leaderboard ang:
- **Class badge** — visual indicator (hal., "pipeline", "coached-llm")
- **Dependency class** — S/O/A1/A2 (tingnan ang [Validity ng Method at Dependency Classes](#method-validity-and-dependency-classes)); ang A2 methods ay may "panlabas na dependency" flag
- **Pangalan ng method** — mula sa method card
- **Tools na ginamit** — nakalista mula sa method card
- **Open source indicator**

Kapag walang naka-attach na method card, ipinapakita ng leaderboard ang harness-native configuration (model, prompt version, temperature, tools enabled).

:::danger HUWAG MAG-TRAIN sa evaluation data
Ang methods na ang development process ay nagkaroon ng exposure sa evaluation dataset — bilang training data, few-shot examples, dictionary entries, o prompt tuning material — ay **madidisqualify** mula sa leaderboard. Tingnan ang [MT Evaluation](/docs/leaderboard/rules) para sa pagkakaiba ng mabuting method at masamang method.
:::

---

## Tingnan Din

- [MT Evaluation](/docs/leaderboard/rules) — overview, halaga ng leaderboard, at gabay sa mabuti/masamang method
- [Eval Harness](/docs/specifications/harness) — kung paano magpatakbo ng evaluations
- [Evaluation Datasets](/docs/leaderboard/datasets) — available datasets (EDTeKLA, FLORES+)
- [Run Card Specification](/docs/specifications/run-card) — ang run card JSON schema
- [Plugin Spec](https://champollion.dev/docs/reference/plugin-spec) — champollion-side plugin interface
- [Method Leaderboard](https://champollion.dev/leaderboard) — live benchmark scores
- [Benchmark Specification](/docs/specifications/benchmark) — evaluation protocol, corpus format, run card schema
- [Scoring Specification](/docs/specifications/scoring) — SSOT para sa metrics, composite weights, at quality tiers