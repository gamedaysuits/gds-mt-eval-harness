---
sidebar_position: 1
title: "Ebalwasyon ng MT"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "How the composite score is computed"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Evaluation Datasets"
    to: /docs/leaderboard/datasets
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "The rules, applied"
---
# Pagsusuri ng MT

> **Executive Summary.** Tinutukoy ng pahinang ito ang pamantayan sa pagsusumite sa leaderboard, mga scoring metric (chrF++, FST acceptance, exact match, equivalent match, semantic score), mga anti-gaming policy, verification tier, at workflow ng pagsusumite. Ang mga method na nailantad na sa evaluation data ay madi-disqualify.

Kasama sa champollion ang isang machine translation evaluation framework na idinisenyo para sa **reproducible benchmarking** ng mga translation method — lalo na para sa mga low-resource at Indigenous language kung saan walang karaniwang MT benchmark at mahirap patunayan ang mga claim sa kalidad.

---

## Ang Leaderboard

Ang sentro nito ay ang **[Method Leaderboard](https://champollion.dev/leaderboard)** — isang live, Supabase-backed scoreboard kung saan nagsusumite at naghahambing ang mga researcher at miyembro ng komunidad ng mga translation method gamit ang fingerprinted, reproducible evaluation.

Kasama sa bawat pagsusumite ang:

- **Fingerprinted pipeline** — nakatali sa isang partikular na Git commit at config hash, upang ma-trace ang mga resulta pabalik sa eksaktong code na nagprodyus ng mga ito
- **Versioned dataset** — content-hashed at versioned; maihahambing lamang ang mga score sa loob ng parehong dataset version
- **Standardised metrics** — kinakalkula ang lahat ng scoring ng shared evaluation harness, na nag-aalis ng mga pagkakaiba sa implementation
- **Trust tiers** — self-benchmarked, GDS Verified, o Community Validated
- **Cost tracking** — API cost bawat pagsusumite, upang maging transparent ang mga cost–quality tradeoff

Kasalukuyang sinusubaybayan ng leaderboard ang limang metric. Tatlo ang gumagana para sa anumang wika; dalawa ang available para sa Plains Cree at gagawing pangkalahatan habang lumalawak tayo:

| Metric | Type | What It Measures |
|--------|------|------------------|
| **chrF++** | Character n-gram F-score | Pangunahing quality metric — mahusay ang korelasyon sa human judgement, lalo na para sa mga wikang mayaman sa morpolohiya |
| **Exact Match** | Proportion ng mga perpektong match | Mahigpit na accuracy — gaano kadalas eksaktong tumutugma ang salin sa gold standard? |
| **FST Acceptance** | Morphological gate pass rate | Para sa mga method na may finite-state transducer verification — anong proporsyon ng outputs ang valid sa morpolohiya? |
| **Equivalent Match** | Acceptable variant rate | Bahaging tumutugma sa reference o sa isang katanggap-tanggap na variant (ayos ng salita, orthographic convention). Kasalukuyang CRK; ginagawang pangkalahatan. |
| **Semantic Score** | Semantic fidelity | Pagpapanatili ng kahulugan — nakukuha ba ng salin ang nilalayong kahulugan anuman ang surface form? Kasalukuyang CRK; ginagawang pangkalahatan. |

:::info Buong Metric Suite
Tinutukoy ng [Scoring Specification](/docs/specifications/scoring) ang kumpletong 19-metric inventory sa 5 kategorya, composite score formula, weight table, at mga quality tier threshold.
:::

**[→ Tingnan ang leaderboard](https://champollion.dev/leaderboard)**

---

## Mga Available na Dataset

### EDTeKLA Development Set v1

Ang unang evaluation dataset, na binuo para sa English→Plains Cree (SRO) translation. Nilikha ng [EdTeKLA research group](https://spaces.facsci.ualberta.ca/edtekla/) sa University of Alberta.

| Property | Value |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Language pair** | EN → CRK (Plains Cree, SRO orthography) |
| **Entry count** | 404 (`master_corpus.json`: 62 gold + 342 textbook); 548 kabuuang available |
| **License** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| **Provenance** | `gold_standard` (beripikado ng mga speaker), `textbook` (nailathalang materyal na pang-edukasyon) |

### FLORES+ Devtest — Para Lamang sa Development Use

> [!WARNING]
> **Available ang FLORES+ para sa development at debugging ngunit HINDI ito ginagamit para sa opisyal na leaderboard evaluation.** Ang FLORES+ (orihinal na Meta FLORES-200) ay isang malawak na pampublikong benchmark dataset na halos tiyak na naisama na sa training ng mga frontier LLM. Ang mga score laban sa FLORES+ ay hindi mapagkakatiwalaang sumasalamin sa tunay na translation quality para sa mga LLM-based method. Mas kaunti ang epekto nito sa mga non-LLM method (FST, rule-based, fine-tuned NMT), ngunit hindi pa rin inilalathala sa leaderboard ang mga FLORES+ score.

Nananatiling available ang mga FLORES+ fixture sa `test/benchmark/fixtures/` para sa pipeline smoke testing, cross-language validation, at development use. Gumagamit ang opisyal na evaluation ng custom corpora na binuo mula sa human-authored text na hindi available sa publiko sa parallel form.

Tingnan ang [Evaluation Datasets](/docs/leaderboard/datasets) para sa buong dataset schema, difficulty tiers, at kung paano gumawa ng sarili ninyo.

:::danger HUWAG MAG-TRAIN sa evaluation data

**Ang mga dataset na ito ay para lamang sa evaluation.** Ang mga method na trained, fine-tuned, few-shot-prompted, o kung hindi man ay nailantad sa evaluation data ay magpoprodyus ng artipisyal na pinataas na mga score at **madi-disqualify mula sa leaderboard.**

Hindi ito mungkahi — ito ang nag-iisang pinakamahalagang tuntunin ng integridad ng evaluation. Gumamit ng hiwalay na corpora para sa training. Dapat manatiling hindi nakikita ng inyong model ang mga evaluation set habang nasa development.

Kung gumagamit kayo ng coaching data o few-shot examples, dapat manggaling ang mga iyon sa **ganap na hiwalay na sources**. Kung may pagdududa, huwag itong isama.
:::

:::warning LLM non-determinism

Non-deterministic ang outputs ng LLM. Kumakatawan ang mga score sa point-in-time measurements sa ilalim ng partikular na model versions at API configurations. Maaaring i-update ng mga model provider ang weights, decoding strategies, o safety filters anumang oras, na maaaring magdulot ng score drift sa pagitan ng mga run. Itinatala ng leaderboard ang eksaktong model slug at timestamp para sa bawat pagsusumite.
:::

---

## Ano ang Bumubuo sa Isang Mahusay na Method

Hindi pantay-pantay ang lahat ng method. Narito ang naghihiwalay sa masusing trabaho mula sa mga pinataas na score.

### Mga katangian ng isang matibay na method

- **Malinis na paghihiwalay ng train at eval data** — hindi pa kailanman nakita ng inyong method ang evaluation set habang nasa development, tuning, prompt engineering, o pagpili ng few-shot example
- **Reproducible** — maaaring i-clone ng iba ang inyong repo, patakbuhin ang harness, at makuha ang parehong mga score (sa loob ng hangganan ng LLM non-determinism)
- **Documented** — inilalarawan ng inyong [method card](/docs/specifications/methods) kung ano ang ginagawa ng inyong method, anong tools ang ginagamit nito, at ano ang mga limitasyon nito
- **Tapat tungkol sa scope** — kung gumagana lamang ang inyong method para sa isang language pair, sabihin ito; kung humihina ito sa ilang morphological pattern, idokumento iyon
- **Community-aware** — para sa mga Indigenous language, nirerespeto ng inyong method ang data sovereignty. Nakipagkonsulta kayo sa mga language community o gumamit lamang ng openly licensed data

### Mga red flag (kung ano ang madi-disqualify)

| Red Flag | Why It's a Problem |
|----------|--------------------|
| Training sa eval data | Ganap nitong binabalewala ang layunin ng evaluation. Nililinlang ng pinataas na mga score ang lahat. |
| Cherry-picking ng mga resulta | Pagpapatakbo nang 10 beses at pagsusumite ng pinakamahusay na run nang hindi isiniwalat ang iba |
| Hindi isiniwalat na post-processing | Manwal na pag-aayos ng outputs bago ang scoring |
| Kontaminadong coaching data | Paggamit ng mga halimbawa mula sa eval set bilang few-shot prompts o dictionary entries |
| Pag-angkin ng commercial readiness nang walang provenance | Kung gumagamit ang inyong method ng CC BY-NC-SA data, hindi ito handa para sa komersyal na paggamit |

### Mga verification tier

Inilalarawan ng mga verification tier kung **sino ang nag-validate ng resulta** — hiwalay sa mga quality tier (Baseline → Fluent) na tinukoy sa [Scoring Specification, §5](/docs/specifications/scoring#5-quality-tiers), na naglalarawan kung ano ang ibig sabihin ng automated composite score.

| Tier | Meaning | How to Get It |
|------|---------|--------------|
| **Self-benchmarked** | Kayo mismo ang nagpatakbo ng harness at nagsumite ng mga resulta | Magbukas ng PR kasama ang inyong run card |
| **GDS Verified** | Na-reproduce ng mga maintainer ng champollion ang inyong mga resulta | Isumite ang inyong method bilang installable plugin |
| **Community Validated** | Nagpatakbo ang governance org laban sa gold-standard + community review | Isumite ang method code sa governance org |

---

## Paano Magsumite

1. **Buuin ang inyong method** — tingnan ang [Building a Method](/docs/specifications/methods) para sa method interface
2. **Patakbuhin ang harness** — tingnan ang [Eval Harness](/docs/specifications/harness) para sa setup at paggamit
3. **Bumuo ng run card** — nagpoprodyus ang harness ng JSON run card kasama ang inyong mga score, fingerprint, at metadata
4. **Magbukas ng PR** — isumite ang inyong run card sa [eval harness repository](https://github.com/gamedaysuits/arena)
5. **Lumabas sa leaderboard** — kapag na-merge na, lalabas ang inyong mga resulta sa [Method Leaderboard](https://champollion.dev/leaderboard)

---

## Mga Direksiyon sa Hinaharap

- **Komprehensibong model comparison runs** — sistematikong evaluation ng frontier models (GPT-4o, Claude, Gemini, etc.) sa buong mga wika ng champollion gamit ang custom evaluation corpora (hindi public benchmarks)
- **Mas maraming language pair** — Quechua, Inuktitut, at iba pang low-resource languages habang nagiging available ang community-verified datasets
- **Dataset import** — tooling upang i-convert ang external evaluation datasets (WMT, Tatoeba, etc.) sa champollion evaluation format
- **Automated re-runs** — pagtukoy ng mga pagbabago sa model version at muling pagpapatakbo ng benchmarks upang subaybayan ang score drift

---

## Tingnan Din

- **[Method Leaderboard](https://champollion.dev/leaderboard)** — live na mga score at pagsusumite
- **[Eval Harness](/docs/specifications/harness)** — kung paano magpatakbo ng evaluations
- **[Evaluation Datasets](/docs/leaderboard/datasets)** — dataset format at available datasets
- **[Building a Method](/docs/specifications/methods)** — ang method interface specification
- **[Run Card Specification](/docs/specifications/run-card)** — ang run card JSON schema
- **[Benchmark Specification](/docs/specifications/benchmark)** — evaluation protocol, corpus format, sovereignty
- **[Scoring Specification](/docs/specifications/scoring)** — SSOT para sa metrics, composite weights, at quality tiers