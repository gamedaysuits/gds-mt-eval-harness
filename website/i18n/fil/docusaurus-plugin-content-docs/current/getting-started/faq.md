---
sidebar_position: 2
title: "FAQ"
related:
  - label: "How It Works"
    to: /docs/how-it-works
    kind: doc
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Glossary"
    to: https://champollion.dev/glossary
    kind: glossary
    note: "Plain-language definitions for every technical term"
---
# Mga Madalas Itanong

> **Ehekutibong Buod.** Mga sagot sa karaniwang tanong tungkol sa MT Eval Arena — kung paano gumagana ang scoring, ano ang nadidiskwalipika, paano pangasiwaan ang mga wikang walang FST, mga rekomendasyon sa model at parameter, at ang proseso ng pagsusumite.

---

## Scoring & Metrics

### Anong metrics ang kinokompyut ng harness?

Kinokompyut ng harness ang limang metrics para sa Plains Cree (ang kasalukuyang benchmark language). Tatlo ang language-agnostic at gagana para sa anumang wika; dalawa ang kasalukuyang umaasa sa mga CRK-specific plugin at gagawing mas pangkalahatan habang lumalawak tayo sa mas maraming wika.

| Metric | Scale | Ano ang Sinusukat Nito | Status |
|--------|-------|-----------------|--------|
| **chrF++** | 0–100 | Character n-gram overlap sa pagitan ng hinulaang salin at reference translations. Pinakamahusay na surface metric para sa mga wikang mayaman sa morpolohiya. Gumagamit ng native scoring ng sacrebleu. | ✅ Lahat ng wika |
| **Exact match** | 0.0–1.0 | Proporsyon ng mga entry kung saan eksaktong tumutugma ang prediction sa reference pagkatapos ng normalization. | ✅ Lahat ng wika |
| **FST acceptance** | 0.0–1.0 | Proporsyon ng mga output word na tinatanggap ng finite-state transducer (morphological analyzer). Kinokompyut lamang kapag may ibinigay na FST binary. | ✅ Lahat ng wikang may FST |
| **Equivalent match** | 0.0–1.0 | Bahagi ng mga entry na tumutugma sa reference o sa isang katanggap-tanggap na variant — isinasaalang-alang ang word order, orthographic convention, at mga pagkakaibang pandiyalekto. | ⚡ CRK (ginagawang pangkalahatan) |
| **Semantic score** | 0.0–1.0 | Meaning preservation score — gaano kahusay nakukuha ng salin ang nilalayong kahulugan anuman ang surface form? | ⚡ CRK (ginagawang pangkalahatan) |

May mga karagdagang metric na nakaplano: **morphological accuracy**, **code-switching detection**, **terminology adherence**, at **hallucination detection**. Tingnan ang [Scoring Specification §2](/docs/specifications/scoring#2-metric-inventory) para sa buong 19-metric inventory.

### Paano kinakalkula ang composite score?

Ang composite ay weighted average ng mga available na metric, na naka-normalize sa scale na 0.0–1.0. Ang mga weight ay tinutukoy sa dalawang profile:

- **Profile A** (mga wikang may FST): 9 metrics, ang structural metrics (FST + morphological accuracy) ay may 40% ng composite weight
- **Profile B** (mga wikang walang FST): 8 metrics, ang semantic at chrF++ ay may magkapantay na pinakamataas na weight

Kapag hindi available ang isang metric, ang weight nito ay muling ipinamamahagi nang proporsyonal sa natitirang metrics. Ibig sabihin, ang mga early-stage benchmark (na chrF++ at exact match lamang ang available) ay nakakagawa pa rin ng valid na composites — ipinapakita lamang ng effective weights kung ano ang available.

**Ang buong weight tables, normalization rules, at exclusion rationale ay nasa [Scoring Specification §4](/docs/specifications/scoring#4-composite-score).** Sinasalamin ng harness code ang mga table na ito sa `mt_eval_harness/scoring.py`. Nino-normalize ang chrF++ sa pamamagitan ng paghahati sa 100 bago i-weight; ang code-switching at hallucination rates ay ini-invert (mas mababa = mas mahusay).

### Ano ang quality tiers?

Ang quality tiers ay heuristic labels na naka-map sa mga saklaw ng composite score. Tumutulong ang mga ito na ipahayag kung ano ang praktikal na *kahulugan* ng isang score:

| Tier | Composite Range | Interpretasyon |
|------|----------------|----------------|
| **Baseline** | 0.00 – 0.30 | Mas mababa sa kapaki-pakinabang na kalidad. Nangangailangan ang method ng malaking pagpapabuti. |
| **Emerging** | 0.30 – 0.50 | Nagpapakita ng potensyal. Tama ang ilang salin ngunit hindi consistent. |
| **Functional** | 0.50 – 0.70 | Magagamit bilang reference na may human review. Hindi angkop para sa deployment na walang review. |
| **Deployable** | 0.70 – 0.85 | Handa para sa production use na may pana-panahong review. Nagti-trigger ng eligibility para sa ownership transfer. |
| **Fluent** | 0.85 – 1.00 | Malapit sa native quality. Angkop para sa unsupervised deployment. |

### Ano ang pagkakaiba ng quality tiers at verification tiers?

Inilalarawan ng **Quality tiers** kung *ano ang kahulugan ng automated score* (Baseline → Fluent). Inilalarawan ng **Verification tiers** kung *sino ang nag-validate ng resulta*:

| Verification Tier | Ano ang Kahulugan Nito |
|-------------------|---------------|
| **Self-benchmarked** | Ang submitter mismo ang nagpatakbo ng harness. Plausible ang scores ngunit hindi pa verified. |
| **GDS Verified** | Na-reproduce ng maintainer ang resulta gamit ang isinumiteng method configuration. |
| **Community Validated** | Sinuri ng bilingual speakers ang mga salin at kinumpirma ang kalidad. |

Maaaring "Deployable" ang kalidad ng isang method ngunit "Self-benchmarked" lamang ang verification — ibig sabihin, mukhang mahusay ang score ngunit wala pang nakapagkumpirma nito nang independent.

---

## Pagsusumite & Diskwalipikasyon

### Ano ang nagdudulot ng diskwalipikasyon ng aking submission?

Tatanggihan o ipa-flag ang inyong submission kung:

1. **Na-expose ang inyong method sa evaluation data.** Kung nag-train, nag-fine-tune, nag-few-shot-prompt, o gumamit kayo sa anumang paraan ng alinmang entry mula sa evaluation dataset, artipisyal na tumataas ang inyong scores. Kasama rito ang paggamit ng reference translations sa inyong prompt.
2. **Nabigo ang inyong run card sa integrity checks.** Dapat tumugma ang fingerprint sa configuration. Tinatanggihan ang mga tampered run card.
3. **Hindi ini-implement ng inyong method ang TranslationMethod protocol.** Inaasahan ng harness ang `translate(entries, config) → results`. Hindi tinatanggap ang custom integrations na lumalampas sa harness.

### Maaari ba akong magsumite nang maraming beses?

Oo. Sinusubaybayan ng leaderboard ang lahat ng submission. Maaari kayong mag-iterate — magpatakbo ng dose-dosenang eksperimento, at isumite lamang ang pinakamahusay. Nagtatala ang bawat submission ng natatanging fingerprint, kaya walang kalituhan kung aling run ang nagprodyus ng aling score.

### Paano ko mapa-verify ang aking score?

1. **Self-benchmarked (automatic):** Dito nagsisimula ang bawat submission.
2. **GDS Verified:** Isumite ang inyong method bilang reproducible package (code + config + coaching data). Muling patatakbuhin ito ng maintainer laban sa parehong dataset at kukumpirmahing tumutugma ang scores.
3. **Community Validated:** Para sa Indigenous languages, kinakailangan nitong repasuhin ng bilingual speakers ang sample ng mga salin. Hindi ito maaaring i-automate — nangangailangan ito ng community engagement.

### Live na ba ang submission API?

Hindi pa. Ang `https://mtevalarena.org/api/leaderboard/submit` endpoint ay aspirational. Ang kasalukuyang submissions ay dapat gawin sa pamamagitan ng pull request sa [eval harness repo](https://github.com/gamedaysuits/arena) kasama ang inyong run card JSON sa `results/` directory.

---

## Models & Parameters

### Anong model ang dapat kong gamitin?

Walang iisang pinakamahusay na model — nakadepende ito sa language pair, inyong budget, at inyong approach. Pangkalahatang gabay:

| Language Type | Inirerekomendang Simula | Bakit |
|---------------|---------------------------|-----|
| **High-resource** (French, Spanish, Japanese) | `google/gemini-2.5-flash` o `gpt-4o-mini` | Mabilis, mura, matibay na baseline |
| **Low-resource na may kaunting LLM coverage** (Quechua, Yoruba) | `google/gemini-2.5-pro` o `anthropic/claude-sonnet-4` | May mas mahusay na latent knowledge ang mas malalaking model |
| **Polysynthetic / napaka-low-resource** (Plains Cree, Inuktitut) | `google/gemini-2.5-pro` na may coaching | Mas mahalaga ang coaching data kaysa sa pagpili ng model. Kasama sa OMT-1600 ang ilang polysynthetic languages (hal., CRK sa R1 tier) ngunit may standard BPE tokenization — i-benchmark ito bilang baseline sa Arena. |

Gumagamit ang eval harness ng OpenRouter, kaya maaaring i-benchmark ang anumang model na available sa OpenRouter. Patakbuhin ang `champollion models --method llm` upang makita ang available models.

### Anong temperature ang dapat kong gamitin?

Karaniwang mas mababa ang mas mahusay para sa translation:

| Temperature | Epekto | Inirerekomenda Para Sa |
|-------------|--------|-----------------|
| **0.0 – 0.2** | Lubhang deterministic, consistent ang output | Production methods, final benchmarks |
| **0.3 – 0.5** | May kaunting variation, paminsan-minsang mas creative | Exploration, early iteration |
| **0.6+** | Mataas ang variation, unpredictable | Hindi inirerekomenda para sa MT benchmarking |

Itinatala ang temperature sa run card, kaya ang magkakaibang temperature ay nagpoprodyus ng magkakaibang fingerprints — itinuturing ang mga ito bilang magkakaibang eksperimento.

### Nakakatulong ba ang coaching data?

Oo, malaki ang naitutulong nito — para sa low-resource languages. Ang coaching data (grammar rules, dictionary entries, style notes) ay ini-inject sa LLM system prompt. Para sa Plains Cree, consistently na nahihigitan ng coached methods ang raw LLM methods para sa polysynthetic languages dahil limitado ang exposure ng general-purpose LLMs sa polysynthetic languages at wala itong morphological awareness. Kahit ang OMT-1600, na partikular na na-train para sa CRK, ay gumagamit ng standard BPE tokenization na hindi kayang kumatawan sa polysynthetic morphology nang structural. Ibinibigay ng coaching data ang linguistic context na kulang sa model.

Para sa high-resource languages (French, Spanish), mas maliit ang epekto ng coaching dahil mayroon nang matibay na baseline knowledge ang model.

Tingnan ang [Coaching Data](https://champollion.dev/docs/concepts/coaching-data) para sa buong specification.

---

## FST & Morphological Validation

### Paano kung walang FST para sa aking wika?

Maraming wika ang walang finite-state transducer. OK lang iyon — gumagana ang harness kahit wala nito. Ginagamit ng composite score ang Profile B weights (tingnan ang [Scoring Specification §4.3](/docs/specifications/scoring#43-weight-tables)) na naglilipat ng weight sa semantic at surface metrics. Minamarkahan ang FST acceptance bilang `null` sa run card.

Ang pangunahing registries para sa existing FSTs:

| Registry | Coverage | URL |
|----------|----------|-----|
| **GiellaLT** | Sámi, Cree, Inuktitut, at iba pang Arctic/subarctic languages | [giellalt.uit.no](https://giellalt.uit.no/) |
| **ALTLab** | Plains Cree, Woods Cree, Ojibwe | [altlab.artsrn.ualberta.ca](https://altlab.artsrn.ualberta.ca/) |
| **Apertium** | ~60 language pairs, karamihan ay European | [apertium.org](https://apertium.org/) |
| **UniMorph** | Morphological paradigms para sa 150+ languages | [unimorph.github.io](https://unimorph.github.io/) |

### Maaari ba akong bumuo ng FST?

Oo, ngunit hindi ito trivial. Ini-encode ng FST ang morphological rules ng isang wika — lahat ng valid word forms. Nangangailangan ang pagbuo nito ng malalim na kaalamang panglingguwistika sa wika. Kung mayroon kayong access sa morphological grammar (hal., mula sa linguistics department), maaari itong i-compile sa FST gamit ang mga tool tulad ng [HFST](https://hfst.github.io/) o [Foma](https://fomafst.github.io/).

### Paano gumagana ang FST gating sa praktika?

Ganito gumagana ang FST-gated pipeline:

1. Bumubuo ang LLM ng salin
2. Sinusuri ang bawat salita sa output laban sa FST
3. Ang mga salitang nire-reject ng FST ay mina-flag bilang morphologically invalid
4. Maaaring mag-retry ang method na may feedback ("hindi valid ang salitang X, subukan muli")
5. Pagkatapos ng retries, nila-log ang natitirang invalid words

Sinusukat ng FST acceptance rate kung ilang salita ang pumapasa sa validation. Tingnan ang [FST-Gated Pipeline Tutorial](/docs/tutorials/fst-gated-pipeline) para sa kumpletong worked example.

---

## Data & Datasets

### Maaari ba akong mag-ambag ng dataset para sa bagong wika?

Oo. Minimum requirements mula sa [Benchmark Specification §11](/docs/specifications/benchmark#11-extending-to-new-languages):

- **50 gold-standard entries** (source + verified reference translation)
- **30 development entries** (maaaring mag-overlap sa gold standard para sa maliliit na corpora)
- **Community consent** (para sa Indigenous languages, explicit authorization mula sa governance body)
- **Provenance documentation** (saan nanggaling ang data, anong license ang naaangkop)

Awtomatikong nagbubukas ang bagong datasets ng bagong leaderboard tracks. Tingnan ang [Para sa Language Communities](/docs/community/for-language-communities) para sa contributor guide.

### Anong format dapat ang aking dataset?

JSON na may canonical field names:

```json
{
  "name": "my-language-dev-v1",
  "language_pair": "en-xxx",
  "segment": "development",
  "version": "1.0",
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "[translation in target language]",
      "difficulty": 1,
      "domain": "general"
    }
  ]
}
```

Tingnan ang [Datasets](/docs/leaderboard/datasets) para sa buong schema at difficulty tier definitions.

---

## Soberanya & Pagmamay-ari

### Sino ang nagmamay-ari ng method na binuo para sa isang Indigenous language?

Para sa Indigenous languages, ang methods na umaabot sa Deployable tier (composite ≥ 0.70) AT pumapasa sa community validation ay nagti-trigger ng proseso ng [paglilipat ng pagmamay-ari](/docs/sovereignty/ownership-transfer). Inililipat ang pagmamay-ari ng code mula sa researcher patungo sa governance organization ng language community.

Pinananatili ng researcher ang:
- Publication rights (academic papers tungkol sa method)
- Credit sa leaderboard
- Karapatang ilapat ang parehong *techniques* sa ibang wika

Nakakamit ng governance organization ang:
- Buong pagmamay-ari ng method code at coaching data
- Kontrol sa deployment (kailan, saan, paano)
- Revenue mula sa API usage (90% community, 10% infrastructure)

### Maaari ko bang gamitin ang champollion para sa non-Indigenous languages nang walang anumang alalahanin sa soberanya?

Oo. Para sa standard languages (French, Japanese, Spanish, atbp.), walang sovereignty considerations. Gamitin ang champollion nang normal — magsalin, mag-sync, mag-publish ayon sa inyong nais. Partikular na naaangkop ang sovereignty framework sa Indigenous at community-governed languages kung saan nangangailangan ng espesyal na konsiderasyon ang data governance principles (OCAP®, CARE, Te Mana Raraunga).

---

## Tingnan Din

- **[Paano Ito Gumagana](https://champollion.dev/how-it-works)** — ang buong solution explainer
- **[Scoring Specification](/docs/specifications/scoring)** — ang SSOT para sa lahat ng scoring logic (metrics, weights, tiers)
- **[Benchmark Specification](/docs/specifications/benchmark)** — evaluation protocol, corpus format, sovereignty
- **[Magsumite ng Method](/docs/getting-started/submit-a-method)** — step-by-step quickstart
- **[Leaderboard Rules](/docs/leaderboard/rules)** — submission criteria
- **[Data Sovereignty](/docs/sovereignty/data-sovereignty)** — OCAP®, CARE, at ethical obligations