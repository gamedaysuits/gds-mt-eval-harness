---
sidebar_position: 8
title: "Ispesipikasyon ng Premyo"
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
# Espesipikasyon ng Premyo

> **Layunin.** Tinutukoy ng dokumentong ito ang estruktura ng pondo ng premyo, mga kondisyon ng threshold, proseso ng pag-claim, at mga tuntunin para sa MT Eval Arena. Eksakto nitong isinasaad kung ano ang ibig sabihin ng "may kakayahan sa machine translation" sa mga nasusukat na termino, at sa ilalim ng anong mga kondisyon inilalabas ang perang premyo. Tinutukoy ng dokumentong ito ang SCORING_SPEC para sa mga depinisyon ng metric at ang BENCHMARK_SPEC para sa protocol ng pagsusuri — hindi nito inuulit ang mga iyon.
>
> **Katayuan:** LIVE. Ang Founder's Prize (§2.1) ay pinondohan at aktibo.
>
> Huling na-update: 2026-06-04

---

## 1. Pilosopiya

### 1.1 Ginagantimpalaan ng mga Premyo ang mga Breakthrough, Hindi ang Pakikilahok

Inilalabas lamang ang perang premyo kapag ang isang pamamaraan ay demonstrableng nakaaabot sa isang tinukoy na threshold ng kakayahan. Walang mga premyo para sa pakikilahok, runner-up award, o consolation payout. Kung walang makalampas sa pamantayan, walang babayaran. Sinadya ito — nangangahulugan itong nagbabayad lamang ang mga sponsor para sa mga resultang talagang gumagana.

### 1.2 Hindi Maaaring Tawaran ang Pagpapatunay ng Komunidad

Ang mga automated metric ay mga proxy (SCORING_SPEC §1.1). Maaaring makakuha ng mataas na score ang isang pamamaraan sa chrF++ at FST acceptance habang gumagawa ng output na hindi tatanggapin ng sinumang tagapagsalita. **Kinakailangan ng bawat claim ng premyo ang pagpapatunay ng komunidad** — kailangang kumpirmahin ng mga bilingual na tagapagsalita na magagamit ang output. Ito ang human validation gate (BENCHMARK_SPEC §7).

### 1.3 Bahagi ng Kasunduan ang Paglipat ng Pagmamay-ari

Ang mga pamamaraang nagki-claim ng premyo ay saklaw ng ownership transfer clause (BENCHMARK_SPEC §8.3). Nananatili sa developer ang attribution at mga karapatan sa publikasyon. Nakukuha ng governance org ang karapatang gamitin, baguhin, ipamahagi, at pagkakitaan ang pamamaraan para sa kanilang wika. Hindi ito parusa — ito ang mismong punto. Pinopondohan ng perang premyo ang paglikha ng teknolohiyang pag-aari ng komunidad ng wika.

### 1.4 Anti-Gaming

Ang mga threshold ng premyo ay tinutukoy laban sa **gold-standard evaluation** (secret test set, pinapatakbo ng governance org sa sandbox). Hindi kailanman nakikita ng mga developer ang test data. Ipinapatupad ito sa arkitektura — hindi ito patakarang umaasa sa dangal. Tingnan ang BENCHMARK_SPEC §8.2.

### 1.5 Paglilisensiya ng Corpus: Mananatili sa Labas ng Prize Lane ang mga Non-Commercial Corpus

May ilang corpus na ginagamit sa development ng pamamaraan na may mga non-commercial license — halimbawa, ang EdTeKLA Cree Language Textbook corpus ay **CC BY-NC-SA 4.0**. Ang mga corpus na ito ay **para lamang sa research/development lane**:

1. **Hindi dapat mag-embed ng nilalamang corpus na may NC license ang mga prize gold-standard corpus.** Ang mga gold-standard test segment ay mga orihinal na kinomisyon ng komunidad (tingnan ang Corpus Partnership Strategy) — nilikha ng tao para sa premyo, na may mga karapatang malinaw na inayos para sa pagsusuri at commercial deployment mula sa simula.
2. **Ang isang pamamaraang nagki-claim ng premyo ay hindi dapat mag-embed ng nilalamang corpus na may NC license** (hal., bilang coaching data, embedded examples, o lookup tables). Ang inilipat na pamamaraan ay nilalayong gamitin para sa commercial deployment ng governance org (BENCHMARK_SPEC §8.3, Method Submission Agreement §6); kung may nilalamang may NC license sa loob nito, makokompromiso ang deployment na iyon.
3. **Malayang magagamit ng mga developer ang mga corpus na may NC license upang mag-develop at magsagawa ng self-evaluation** — iyon ang layunin ng development lane. Nalalapat ang restriksyon sa kung ano ang isinusumite at kung ano ang dine-deploy, hindi sa kung paano natututo ang isang developer.

### 1.6 Ang mga Dependency Class ang Nagkokontrol sa Eligibility para sa Premyo

Lahat ng pagsusuri para sa premyo ay nangyayari sa isang sandbox (§1.4), at ang mga pamamaraang nananalo ng premyo ay inililipat sa governance org (§1.3). Ipinapataw ng parehong katotohanan ang iisang constraint: **lahat ng pinagdedependehan ng isang pamamaraan ay dapat isang bagay na may karapatan ang developer na ilagay sa sandbox at ipasa sa komunidad.** Idinedeklara ng bawat submission ang isang dependency class — tinukoy sa [Method Interface spec](/docs/specifications/methods#method-validity-and-dependency-classes), na may admissibility terms sa Method Submission Agreement §2.6 — at sumusunod ang eligibility sa class:

| Dependency class | Eligible para sa premyo? | Mga kondisyon |
|------------------|----------------|------------|
| **S** — self-contained | ✅ Oo | Wala bukod sa mga kondisyon ng threshold sa §2 |
| **O** — open external (hal., AGPL FST na naka-mirror sa submission) | ✅ Oo | Naka-pin at naka-vendor ang mga artifact sa submission; pinahihintulutan ng mga license ang paglipat sa komunidad; pinananatili ang mga copyleft term (natatanggap ng komunidad ang parehong mga karapatang ibinibigay ng license sa lahat) |
| **A1** — substitutable LLM inference | ⚠️ Kondisyonal | Idineklara, naka-pin, at substitutable ang model (dapat tumakbo laban sa community-hosted open-weight model); ang pagsusuri ay iruruta sa sandbox LLM gateway (🔲 nakaplano — hindi maaaring makabuo ng gold-standard scores ang mga A1 method hanggang operational na ang gateway); inililipat ang buong recipe (prompts, coaching, code), hindi ang model |
| **A2** — non-substitutable external data/service API | ❌ Hindi pa | Hindi eligible hanggang magbigay ang rights holder ng mga pahintulot para sa sandbox-inclusion at transfer. Pinahihintulutan sa open leaderboard na may nakikitang "external dependency" flag |
| **X** — bundled content without rights | ❌ Kailanman hindi | Inadmissible sa bawat lane |

Ang class ng isang pamamaraan ay ang pinakarestriktibong class sa mga idineklara nitong dependency. Anumang hindi idineklarang dependency ng anumang class ay nagdidisqualify (§5).

---

## 2. Mga Aktibong Pondo ng Premyo

### 2.1 Ang Founder's Prize — EN→Plains Cree (nêhiyawêwin)

| Field | Value |
|-------|-------|
| **Pondo ng premyo** | **$10,000 CAD** |
| **Language pair** | English → Plains Cree (EN→CRK) |
| **Pinondohan ng** | Founder ng Champollion project |
| **Katayuan** | **ACTIVE** — tumatanggap ng mga submission |
| **Nagbubukas** | Kapag naitatag na ang gold-standard corpus + governance org |
| **Nag-e-expire** | Walang expiry. Mananatiling aktibo ang premyo hanggang ma-claim o tahasang bawiin. |

#### Mga Kondisyon ng Threshold

Naki-claim ng isang pamamaraan ang Founder's Prize sa pamamagitan ng sabayang pagtugon sa **LAHAT** ng sumusunod na kondisyon:

| # | Kondisyon | Metric | Threshold | Rasyonal |
|---|-----------|--------|-----------|-----------|
| 1 | **Composite score** | `composite` (SCORING_SPEC §4) | **≥ 0.80** | Nasa pagitan ng Deployable (0.70) at Fluent (0.85). Nangangailangan ng mataas na kalidad sa lahat ng dimensiyon ng metric — hindi lamang morphological validity. |
| 2 | **FST acceptance** | `fst_acceptance_rate` (SCORING_SPEC §2.2) | **≥ 0.99 (99%+)** | Sa praktika, lahat ng output word ay dapat mga morphologically valid form na kinikilala ng GiellaLT FST. Isinasaalang-alang ng 1% tolerance ang mga edge case (proper nouns, neologisms, loanwords) na maaaring lehitimong hindi saklaw ng FST. Ito ang tumutukoy na quality gate para sa polysynthetic MT — kung nire-reject ng FST ang higit sa 1% ng mga salita, gumagawa ang pamamaraan ng mga anyong hindi umiiral sa wika. Ang buong punto ng premyong ito ay bumili ng sistemang hindi sumisira sa wika. |
| 3 | **chrF++** | `chrf_plus_plus` (SCORING_SPEC §2.1) | **≥ 55.0** | Kailangang lumampas sa 55 ang character n-gram overlap sa 0–100 scale. Tinitiyak ang surface-level similarity sa mga reference translation, hindi lamang morphological validity. |
| 4 | **Pagpapatunay ng komunidad** | Human review (BENCHMARK_SPEC §7) | **≥ 70% "acceptable" o "excellent"** | Susuriin ng ≥2 bilingual na tagapagsalita ng CRK ang isang stratified sample ng mga output (≥30 entry sa mga difficulty tier 2–5). Hindi bababa sa 70% ng mga sinuring entry ang dapat makatanggap ng rating na "acceptable" o "excellent". |
| 5 | **Gold-standard evaluation** | Sandbox execution (BENCHMARK_SPEC §8.2) | **Required** | Lahat ng automated metric ay dapat kalkulahin laban sa `gold_standard` corpus segment, na pinatatakbo ng governance org sa isang sandboxed environment. Hindi binibilang ang development-set scores. |
| 6 | **Reproducibility** | Fingerprint match (BENCHMARK_SPEC §3.8) | **±2%** | Kailangang magawa ng governance org na muling patakbuhin ang pamamaraan at makamit ang mga score na nasa loob ng ±2% ng isinumiteng run card. |

> **Bakit 99+% FST?** Ang sentral na problema sa machine translation para sa mga polysynthetic language ay hallucination — gumagawa ang mga LLM ng mga string na *mukhang* target language ngunit morphologically invalid. Ang pamamaraang gumagawa ng 95% valid output ay mayroon pa ring 5% fabricated words — hindi katanggap-tanggap na ingay para sa anumang production use. Hinihingi ng 99%+ threshold ang halos zero hallucination habang pinahihintulutan ang bihirang edge case (isang proper noun na hindi alam ng FST, isang lehitimong neologism). Kung hindi makakamit ng isang pamamaraan ang 99%+ FST acceptance, hindi nito nalutas ang problema.
>
> **Bakit 0.80 composite?** Nasa pagitan ito ng Deployable (0.70) at Fluent (0.85). Ang pamamaraang nasa 0.80 na may 99%+ FST acceptance ay gumagawa ng output kung saan halos bawat salita ay totoong salitang Cree *at* mataas ang kabuuang kalidad ng pagsasalin sa mga dimensiyong surface, structural, at semantic. Tinitiyak ng community validation gate (kondisyon #4) na hindi lamang ito metric gaming — kailangang kumpirmahin ng mga tagapagsalita na tunay na magagamit ang output.

#### Ano ang Ibig Sabihin ng Threshold na Ito sa Praktika

Sa composite ≥ 0.80 na may FST ≥ 0.99 at chrF++ ≥ 55, karaniwang makikita ng isang bilingual na tagapagsalita na:

- **Halos bawat** output word ay totoong salitang Cree (bine-validate ng FST ang 99%+ — halos zero hallucinated forms)
- Tama ang mga pangunahing grammatical category (person, number, tense) sa karamihan ng mga entry
- Karaniwang natural ang word order
- Maaasahang napapanatili ang kahulugan
- Ang natitirang mga error ay mga error sa tunay na wika (maling inflection, hindi tamang obviation, animacy mismatches) — hindi fabricated words
- Magagamit ng isang fluent speaker ang output bilang high-quality draft at maitama ito nang mas mabilis kaysa magsalin mula sa simula

Ito ay isang sistemang **hindi sumisira sa wika.** Maaaring hindi ito perpekto, ngunit bawat salitang ginagawa nito ay tunay na salita. Iyan ang minimum na pamantayan para sa magalang na machine translation ng isang polysynthetic language.

---

## 3. Proseso ng Pag-claim ng Premyo

### 3.1 Submission

1. Isinusumite ng developer ang kanilang kumpleto at runnable na pamamaraan sa governance org:
   - Lahat ng source code
   - Lahat ng dependency (coaching data, dictionaries, FST configs, prompts)
   - Mga tagubilin sa installation at execution
   - Isang README na naglalarawan sa approach ng pamamaraan
   - Isang development-set run card na nagpapakita ng tinatayang mga score (para sa pre-screening)

2. Pinipirmahan ng developer ang mga tuntunin ng pakikilahok, kabilang ang:
   - Ownership transfer clause (BENCHMARK_SPEC §8.3)
   - Deklarasyon na walang training sa evaluation data
   - Pangako sa reproducibility

### 3.2 Evaluation

1. Ini-install at pinatatakbo ng governance org ang pamamaraan sa isang sandboxed harness laban sa `gold_standard` corpus
2. Kinakalkula ang mga automated metric (composite, FST, chrF++, atbp.)
3. Kung natugunan ang mga automated threshold (mga kondisyon 1–3), magpapatuloy ang governance org sa community review
4. Kung HINDI natugunan ang mga automated threshold, matatanggap ng developer ang mga score at feedback. Walang community review na iti-trigger.

### 3.3 Community Review

1. Ipinapakita sa mga bilingual na tagapagsalita ang isang stratified sample ng mga output (≥30 entry, saklaw ang difficulty tiers 2–5)
2. Hindi bababa sa 2 independent reviewer ang magre-rate sa bawat entry
3. Rating scale: **reject** / **gist** / **acceptable** / **excellent**
4. Kung ≥70% ng mga entry ang makatanggap ng "acceptable" o "excellent" mula sa parehong reviewer, pasado ang pagpapatunay ng komunidad

### 3.4 Payout

1. Natugunan ang lahat ng 6 na kondisyon
2. Kinukumpirma ng governance org ang resulta
3. Binabayaran ang premyo sa loob ng 30 araw mula sa kumpirmasyon
4. Naililipat ang pagmamay-ari ng pamamaraan ayon sa BENCHMARK_SPEC §8.3
5. Inilalathala ang resulta sa leaderboard na may verification tier na "Community Validated"

### 3.5 Maramihang Submission

- Maaaring magsumite nang maraming beses ang parehong developer/team
- Sinusuri nang hiwalay ang bawat submission
- Kung pinahusay at muling isinumite ang isang pamamaraan, ang pinakabagong run card lamang ang bibilangin
- Iginagawad ang premyo sa **unang** pamamaraang makalampas sa lahat ng threshold — hindi ito hinahati

### 3.6 Mga Team Submission

- Eligible ang mga team at pares ng Elder-kabataan
- Responsibilidad ng team ang pamamahagi ng premyo sa loob ng team
- Kailangang pirmahan ng lahat ng team member ang mga tuntunin ng pakikilahok
- Inililista ng attribution sa leaderboard ang lahat ng team member

---

## 4. Mga Hinaharap na Pondo ng Premyo {#4-future-prize-pools}

Ang Founder's Prize ang binhi. Pinopondohan ng mga sponsor ang karagdagang mga pondo ng premyo. Idodokumento ang bawat bagong pondo ng premyo bilang bagong subsection ng §2 na may sarili nitong:

- Halaga ng premyo at currency
- Language pair
- Attribution ng sponsor
- Mga kondisyon ng threshold (na maaaring iba sa Founder's Prize)
- Expiry date (kung mayroon)
- Anumang espesyal na kondisyon

### 4.1 Template ng Sponsor Prize

Pinopondohan ng mga sponsor ang mga pondo ng premyo sa anumang halaga. Mga iminumungkahing tier:

| Tier | Halaga | Iminungkahing Threshold |
|------|--------|---------------------|
| **Seed** | $5,000–$15,000 | Deployable (composite ≥ 0.70) + pagpapatunay ng komunidad |
| **Breakthrough** | $25,000–$50,000 | Fluent (composite ≥ 0.85) + pagpapatunay ng komunidad |
| **Grand Prize** | $100,000+ | Fluent + multi-register coverage + deployment integration |

Maaari ring pondohan ng mga sponsor ang:
- **Improvement bounties** — fixed payment para sa bawat 5-point improvement sa chrF++ kumpara sa kasalukuyang pinakamahusay
- **Register prizes** — magkakahiwalay na award para sa mga partikular na register (formal, ceremonial, educational)
- **Speed prizes** — pinakamahusay na cost-adjusted score (SCORING_SPEC §6.3)

### 4.2 Escrow ng Pondo ng Premyo

Lahat ng prize fund ay hinahawakan sa escrow (pinamamahalaan ng proyekto o ng itinalagang trustee) hanggang matugunan ang mga kondisyon ng threshold. Kung mag-expire ang isang premyo nang hindi na-claim, ibabalik ang pondo sa sponsor o ire-redirect sa isang bagong pondo ng premyo ayon sa pagpapasya ng sponsor.

---

## 5. Disqualification

Nadi-disqualify ang isang submission kung:

1. **Training sa evaluation data.** Na-expose ang pamamaraan sa mga entry ng `gold_standard` o `held_out` corpus. (Napipigilan sa arkitektura sa pamamagitan ng sandboxed execution — ngunit kung may makitang ebidensiya ng contamination, ivo-void ang resulta.)
2. **Hindi reproducible.** Hindi ma-reproduce ng governance org ang mga score sa loob ng ±2%.
3. **Hindi idineklara o hindi eligible na mga dependency.** Nangangailangan ang pamamaraan ng runtime access sa external services na lampas sa idinedeklara ng dependency manifest nito, o ang effective dependency class nito ay A2 o X (§1.6). Pinahihintulutan ang idineklarang Class A1 LLM inference na iruruta sa evaluation gateway; anumang ibang runtime network dependency — at anumang hindi idineklarang dependency ng anumang class — ay nagdidisqualify.
4. **Hindi napirmahan ang mga tuntunin ng pakikilahok.** Kailangang sumang-ayon ang lahat ng team member sa ownership transfer.
5. **Natukoy ang gaming.** Na-optimize ang output para sa metric sa halip na kalidad ng pagsasalin (nahuhuli sa pamamagitan ng community review at/o anti-gaming checks ayon sa BENCHMARK_SPEC §9.3).

---

## 6. Kaugnayan sa Iba Pang Specs

| Dokumentong Ito | Mga Reference | Para sa |
|--------------|-----------|-----|
| §2 mga kondisyon ng threshold | SCORING_SPEC §4 (composite), §2.1–2.2 (metrics), §5 (tiers) | Mga depinisyon at scale ng metric |
| §2 pagpapatunay ng komunidad | BENCHMARK_SPEC §7 | Protocol ng human review |
| §3 sandbox execution | BENCHMARK_SPEC §8.2 | Mekanismo ng sovereignty |
| §3 ownership transfer | BENCHMARK_SPEC §8.3 | Mga term ng IP transfer |
| §1.6 dependency classes | Method Interface spec; Method Submission Agreement §2.6; BENCHMARK_SPEC §8.6 | Mga depinisyon ng class, admissibility terms, sandbox network policy |
| §4 cost-adjusted prizes | SCORING_SPEC §6.3 | Cost-adjusted formula |

---

## 7. Code–Spec Synchronization

### 7.1 Canonical Source

Ang dokumentong ito (`arena/website/docs/specifications/prize-spec.md`) ang canonical source para sa:
- Mga depinisyon ng pondo ng premyo (§2)
- Mga kondisyon ng threshold (§2.x)
- Proseso ng pag-claim (§3)
- Mga tuntunin sa disqualification (§5)

### 7.2 Mga Kinakailangan sa Implementation

Kapag na-activate ang isang pondo ng premyo:
1. Dapat ipakita ng leaderboard UI ang mga aktibong premyo at ang kanilang mga kondisyon ng threshold
2. Dapat i-flag para sa community review ang mga run card na nakatutugon sa mga automated threshold (mga kondisyon 1–3)
3. Nakukuha na ng field na `quality_tier` sa run card schema ang tier ("deployable", "fluent")
4. Walang kinakailangang bagong code change sa harness — ang prize spec ay policy layer sa ibabaw ng kasalukuyang scoring

---

*Dapat compatible ang mga estruktura ng premyo sa ownership transfer terms. Maaaring i-claim ng nanalo ang premyo, ngunit nagiging pag-aari ng governance org ang pamamaraan kung maaabot nito ang Deployable tier. Sinadya ito — pinopondohan ng premyo ang paglikha ng teknolohiyang pag-aari ng komunidad ng wika.*