---
sidebar_position: 8
title: "Espesipikasyon ng Gantimpala"
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
# Espesipikasyon ng Gantimpala

> **Layunin.** Itinatakda ng dokumentong ito ang istruktura ng prize pool, mga kundisyon ng threshold, proseso ng pag-claim, at mga tuntunin para sa MT Eval Arena. Tiyak nitong isinasaad kung ano ang ibig sabihin ng "capable of machine translation" sa nasusukat na mga termino, at sa ilalim ng anong mga kundisyon inilalabas ang perang gantimpala. Tinutukoy ng dokumentong ito ang SCORING_SPEC para sa mga depinisyon ng metric at ang BENCHMARK_SPEC para sa protocol ng ebalwasyon — hindi nito inuulit ang mga iyon.
>
> **Katayuan:** LIVE. Ang Founder's Prize (§2.1) ay may pondo at aktibo.
>
> Huling na-update: 2026-06-04

---

## 1. Pilosopiya

### 1.1 Ginagantimpalaan ng mga Prize ang mga Breakthrough, Hindi ang Pakikilahok

Inilalabas lamang ang perang gantimpala kapag ang isang method ay mapapatunayang nakakamit ang isang tinukoy na capability threshold. Walang mga gantimpala para sa pakikilahok, runner-up awards, o consolation payouts. Kung walang makalampas sa itinakdang antas, walang babayaran. Sinasadya ito — nangangahulugan itong nagbabayad lamang ang mga sponsor para sa mga resultang talagang gumagana.

### 1.2 Hindi Maaaring Ikonsiderang Opsyonal ang Pagpapatunay ng Komunidad

Ang automated metrics ay mga proxy (SCORING_SPEC §1.1). Maaaring mataas ang score ng isang method sa chrF++ at FST acceptance habang lumilikha ng output na hindi tatanggapin ng sinumang tagapagsalita. **Bawat prize claim ay nangangailangan ng pagpapatunay ng komunidad** — kailangang kumpirmahin ng mga bilingual speaker na magagamit ang output. Ito ang human validation gate (BENCHMARK_SPEC §7).

### 1.3 Bahagi ng Kasunduan ang Paglipat ng Pagmamay-ari

Ang mga method na nagki-claim ng prize ay saklaw ng ownership transfer clause (BENCHMARK_SPEC §8.3). Pinananatili ng developer ang attribution at publication rights. Nakakamit ng governance org ang karapatang gamitin, baguhin, ipamahagi, at pagkakitaan ang method para sa kanilang wika. Hindi ito parusa — ito ang mismong layunin. Pinopondohan ng perang gantimpala ang paglikha ng teknolohiyang pag-aari ng komunidad ng wika.

### 1.4 Anti-Gaming

Tinukoy ang prize thresholds batay sa **gold-standard evaluation** (secret test set, pinapatakbo ng governance org sa sandbox). Hindi kailanman nakikita ng mga developer ang test data. Ipinapatupad ito sa arkitektura — hindi ito patakarang umaasa sa dangal. Tingnan ang BENCHMARK_SPEC §8.2.

### 1.5 Paglilisensya ng Corpus: Hindi Kasama sa Prize Lane ang Non-Commercial Corpora

May ilang corpora na ginagamit habang gumagawa ng method na may non-commercial licenses — halimbawa, ang EdTeKLA Cree Language Textbook corpus ay **CC BY-NC-SA 4.0**. Ang mga corpus na ito ay **research/development-lane only**:

1. **Hindi dapat mag-embed ng NC-licensed corpus content ang prize gold-standard corpora.** Ang gold-standard test segments ay mga community-commissioned original (tingnan ang Corpus Partnership Strategy) — isinulat ng tao para sa prize, na may mga karapatang malinaw na naayos para sa ebalwasyon at komersyal na deployment mula pa sa simula.
2. **Hindi dapat mag-embed ng NC-licensed corpus content ang method na nagki-claim ng prize** (hal., bilang coaching data, embedded examples, o lookup tables). Nilalayon ang transferred method para sa komersyal na deployment ng governance org (BENCHMARK_SPEC §8.3, Method Submission Agreement §6); magiging hadlang sa deployment na iyon ang NC-licensed content sa loob nito.
3. **Malayang magagamit ng mga developer ang NC-licensed corpora para sa development at self-evaluation** — iyon ang layunin ng development lane. Nalalapat ang restriksyon sa kung ano ang isinusumite at kung ano ang dine-deploy, hindi sa kung paano natututo ang developer.

### 1.6 Kinokontrol ng Dependency Classes ang Prize Eligibility

Lahat ng prize evaluation ay nagaganap sa sandbox (§1.4), at ang mga prize-winning method ay inililipat sa governance org (§1.3). Parehong nagpapataw ang dalawang katotohanang ito ng iisang constraint: **lahat ng pinagdedependehan ng isang method ay dapat na isang bagay na may karapatan ang developer na ilagay sa sandbox at ipasa sa komunidad.** Bawat submission ay nagdedeklara ng dependency class — tinukoy sa [Method Interface spec](/docs/specifications/methods#method-validity-and-dependency-classes), na may admissibility terms sa Method Submission Agreement §2.6 — at sumusunod ang eligibility sa class:

| Dependency class | Prize-eligible? | Mga Kundisyon |
|------------------|----------------|------------|
| **S** — self-contained | ✅ Oo | Wala bukod sa mga threshold condition sa §2 |
| **O** — open external (hal., AGPL FST na naka-mirror sa submission) | ✅ Oo | Naka-pin at naka-vendor ang artifacts sa submission; pinahihintulutan ng licenses ang paglipat sa komunidad; pinananatili ang copyleft terms (natatanggap ng komunidad ang parehong karapatang ibinibigay ng license sa lahat) |
| **A1** — substitutable LLM inference | ⚠️ Conditional | Idineklara, naka-pin, at substitutable ang model (dapat tumakbo laban sa community-hosted open-weight model); idinadaan ang ebalwasyon sa sandbox LLM gateway (🔲 planned — hindi makagagawa ng gold-standard scores ang A1 methods hanggang operational ang gateway); ipinapasa ng transfer ang buong recipe (prompts, coaching, code), hindi ang model |
| **A2** — non-substitutable external data/service API | ❌ Hindi pa | Hindi eligible hanggang magbigay ang rights holder ng pahintulot para sa sandbox-inclusion at transfer. Pinahihintulutan sa open leaderboard na may nakikitang "external dependency" flag |
| **X** — bundled content without rights | ❌ Hindi kailanman | Hindi admissible sa anumang lane |

Ang class ng isang method ay ang pinaka-restrictive na class sa mga idineklara nitong dependency. Ang mga hindi idineklarang dependency ng anumang class ay batayan ng diskwalipikasyon (§5).

---

## 2. Mga Aktibong Prize Pool

### 2.1 Ang Founder's Prize — EN→Plains Cree (nêhiyawêwin)

| Field | Value |
|-------|-------|
| **Prize pool** | **$10,000 CAD** |
| **Language pair** | English → Plains Cree (EN→CRK) |
| **Funded by** | Champollion project founder |
| **Status** | **ACTIVE** — tumatanggap ng mga submission |
| **Opens** | Kapag nasa lugar na ang gold-standard corpus + governance org |
| **Expires** | Walang expiry. Mananatiling aktibo ang prize hanggang ma-claim o tahasang bawiin. |

#### Mga Threshold Condition

Makukuha ng isang method ang Founder's Prize sa pamamagitan ng sabay-sabay na pagtugon sa **LAHAT** ng sumusunod na kundisyon:

| # | Kundisyon | Metric | Threshold | Rationale |
|---|-----------|--------|-----------|-----------|
| 1 | **Composite score** | `composite` (SCORING_SPEC §4) | **≥ 0.80** | Nasa pagitan ng Deployable (0.70) at Fluent (0.85). Nangangailangan ng mataas na kalidad sa lahat ng metric dimensions — hindi lamang morphological validity. |
| 2 | **FST acceptance** | `fst_acceptance_rate` (SCORING_SPEC §2.2) | **≥ 0.99 (99%+)** | Sa praktikal na kahulugan, lahat ng output words ay dapat na morphologically valid forms na kinikilala ng GiellaLT FST. Isinasaalang-alang ng 1% tolerance ang mga edge case (proper nouns, neologisms, loanwords) na maaaring lehitimong hindi saklaw ng FST. Ito ang tumutukoy na quality gate para sa polysynthetic MT — kung tinatanggihan ng FST ang higit sa 1% ng mga salita, gumagawa ang method ng mga anyong hindi umiiral sa wika. Ang buong layunin ng prize na ito ay bumili ng system na hindi sumisira sa wika. |
| 3 | **chrF++** | `chrf_plus_plus` (SCORING_SPEC §2.1) | **≥ 55.0** | Dapat lumampas sa 55 sa 0–100 scale ang character n-gram overlap. Tinitiyak ang surface-level similarity sa reference translations, hindi lamang morphological validity. |
| 4 | **Pagpapatunay ng komunidad** | Human review (BENCHMARK_SPEC §7) | **≥ 70% "acceptable" o "excellent"** | Sinusuri ng ≥2 bilingual CRK speakers ang stratified sample ng outputs (≥30 entries sa difficulty tiers 2–5). Hindi bababa sa 70% ng reviewed entries ang dapat makatanggap ng rating na "acceptable" o "excellent". |
| 5 | **Gold-standard evaluation** | Sandbox execution (BENCHMARK_SPEC §8.2) | **Required** | Lahat ng automated metrics ay dapat kuwentahin laban sa `gold_standard` corpus segment, na pinapatakbo ng governance org sa isang sandboxed environment. Hindi binibilang ang development-set scores. |
| 6 | **Reproducibility** | Fingerprint match (BENCHMARK_SPEC §3.8) | **±2%** | Dapat kayang muling patakbuhin ng governance org ang method at makamit ang scores na nasa loob ng ±2% ng submitted run card. |

> **Bakit 99+% FST?** Ang sentral na problema sa machine translation para sa polysynthetic languages ay hallucination — lumilikha ang LLMs ng strings na *mukhang* target language ngunit morphologically invalid. Ang method na gumagawa ng 95% valid output ay mayroon pa ring 5% fabricated words — hindi katanggap-tanggap na ingay para sa anumang production use. Hinihingi ng 99%+ threshold ang halos zero hallucination habang pinapayagan ang bihirang edge case (isang proper noun na hindi alam ng FST, isang lehitimong neologism). Kung hindi makakamit ng isang method ang 99%+ FST acceptance, hindi nito nalutas ang problema.
>
> **Bakit 0.80 composite?** Nasa pagitan ito ng Deployable (0.70) at Fluent (0.85). Ang method na nasa 0.80 na may 99%+ FST acceptance ay lumilikha ng output kung saan halos bawat salita ay totoong Cree word *at* mataas ang kabuuang translation quality sa surface, structural, at semantic dimensions. Tinitiyak ng community validation gate (condition #4) na hindi lamang ito metric gaming — kailangang kumpirmahin ng mga speaker na tunay na magagamit ang output.

#### Ano ang Ibig Sabihin ng Threshold na Ito sa Praktika

Sa composite ≥ 0.80 na may FST ≥ 0.99 at chrF++ ≥ 55, karaniwang makikita ng bilingual speaker na:

- **Halos bawat** output word ay totoong Cree word (vina-validate ng FST ang 99%+ — halos zero hallucinated forms)
- Tama ang mga pangunahing grammatical categories (person, number, tense) sa karamihan ng entries
- Karaniwang natural ang word order
- Maaasahang napapanatili ang kahulugan
- Ang natitirang errors ay real-language errors (maling inflection, incorrect obviation, animacy mismatches) — hindi fabricated words
- Magagamit ng fluent speaker ang output bilang high-quality draft at maiwawasto ito nang mas mabilis kaysa pagsasalin mula sa simula

Ito ay isang system na **hindi sumisira sa wika.** Maaaring hindi ito perpekto, ngunit bawat salitang ginagawa nito ay totoong salita. Iyon ang minimum bar para sa magalang na machine translation ng polysynthetic language.

---

## 3. Proseso ng Prize Claim

### 3.1 Submission

1. Isinusumite ng developer ang kanilang kumpleto at runnable na method sa governance org:
   - Lahat ng source code
   - Lahat ng dependencies (coaching data, dictionaries, FST configs, prompts)
   - Installation at execution instructions
   - Isang README na naglalarawan sa approach ng method
   - Isang development-set run card na nagpapakita ng tinatayang scores (para sa pre-screening)

2. Pinipirmahan ng developer ang terms of participation, kabilang ang:
   - Ownership transfer clause (BENCHMARK_SPEC §8.3)
   - Deklarasyon na walang training sa evaluation data
   - Reproducibility commitment

### 3.2 Ebalwasyon

1. Ini-install at pinapatakbo ng governance org ang method sa isang sandboxed harness laban sa `gold_standard` corpus
2. Kinukuwenta ang automated metrics (composite, FST, chrF++, atbp.)
3. Kung natugunan ang automated thresholds (conditions 1–3), nagpapatuloy ang governance org sa community review
4. Kung HINDI natugunan ang automated thresholds, matatanggap ng developer ang scores at feedback. Walang community review na iti-trigger.

### 3.3 Community Review

1. Isang stratified sample ng outputs (≥30 entries, na sumasaklaw sa difficulty tiers 2–5) ang ipinapakita sa bilingual speakers
2. Hindi bababa sa 2 independent reviewers ang nagre-rate sa bawat entry
3. Rating scale: **reject** / **gist** / **acceptable** / **excellent**
4. Kung ≥70% ng entries ay makatanggap ng "acceptable" o "excellent" mula sa parehong reviewers, pumapasa ang community validation

### 3.4 Payout

1. Natugunan ang lahat ng 6 na kundisyon
2. Kinukumpirma ng governance org ang resulta
3. Binabayaran ang prize sa loob ng 30 araw mula sa kumpirmasyon
4. Lumilipat ang ownership ng method alinsunod sa BENCHMARK_SPEC §8.3
5. Inilalathala ang resulta sa leaderboard na may verification tier na "Community Validated"

### 3.5 Maramihang Submissions

- Maaaring magsumite nang maraming beses ang parehong developer/team
- Independiyenteng ine-evaluate ang bawat submission
- Kung ang isang method ay pinahusay at muling isinumite, ang pinakabagong run card lamang ang bibilangin
- Iginagawad ang prize sa **unang** method na makalalampas sa lahat ng thresholds — hindi ito hahatiin

### 3.6 Team Submissions

- Eligible ang teams at Elder-youth pairs
- Responsibilidad ng team ang distribusyon ng prize sa loob ng team
- Dapat pirmahan ng lahat ng team members ang terms of participation
- Inililista ng attribution sa leaderboard ang lahat ng team members

---

## 4. Mga Hinaharap na Prize Pool

Ang Founder's Prize ang seed. Pinopondohan ng mga sponsor ang karagdagang prize pools. Idinedokumento ang bawat bagong prize pool bilang bagong subsection ng §2 na may sarili nitong:

- Halaga ng prize at currency
- Language pair
- Sponsor attribution
- Threshold conditions (na maaaring iba sa Founder's Prize)
- Expiry date (kung mayroon)
- Anumang special conditions

### 4.1 Template ng Sponsor Prize

Nagpopondo ang mga sponsor ng prize pools sa anumang halaga. Mga iminungkahing tier:

| Tier | Halaga | Iminungkahing Threshold |
|------|--------|---------------------|
| **Seed** | $5,000–$15,000 | Deployable (composite ≥ 0.70) + community validation |
| **Breakthrough** | $25,000–$50,000 | Fluent (composite ≥ 0.85) + community validation |
| **Grand Prize** | $100,000+ | Fluent + multi-register coverage + deployment integration |

Maaari ring pondohan ng mga sponsor ang:
- **Improvement bounties** — fixed payment para sa bawat 5-point improvement sa chrF++ lampas sa kasalukuyang best
- **Register prizes** — hiwalay na awards para sa partikular na registers (formal, ceremonial, educational)
- **Speed prizes** — pinakamahusay na cost-adjusted score (SCORING_SPEC §6.3)

### 4.2 Prize Pool Escrow

Lahat ng prize funds ay hinahawakan sa escrow (pinamamahalaan ng project o isang designated trustee) hanggang matugunan ang threshold conditions. Kung mag-expire ang prize nang hindi na-claim, ibinabalik ang pondo sa sponsor o inililipat sa bagong prize pool ayon sa pagpapasya ng sponsor.

---

## 5. Diskwalipikasyon

Nadi-disqualify ang isang submission kung:

1. **Training sa evaluation data.** Nalantad ang method sa `gold_standard` o `held_out` corpus entries. (Napipigilan sa arkitektura sa pamamagitan ng sandboxed execution — ngunit kung makakita ng ebidensya ng contamination, pinapawalang-bisa ang resulta.)
2. **Hindi reproducible.** Hindi mareproduce ng governance org ang scores sa loob ng ±2%.
3. **Hindi idineklara o hindi eligible na dependencies.** Nangangailangan ang method ng runtime access sa external services na lampas sa idinedeklara ng dependency manifest nito, o ang effective dependency class nito ay A2 o X (§1.6). Pinahihintulutan ang idineklarang Class A1 LLM inference na idinadaan sa evaluation gateway; anumang iba pang runtime network dependency — at anumang hindi idineklarang dependency ng anumang class — ay batayan ng diskwalipikasyon.
4. **Hindi napirmahan ang terms of participation.** Dapat sumang-ayon ang lahat ng team members sa ownership transfer.
5. **May natukoy na gaming.** In-optimize ang output para sa metric sa halip na translation quality (nahuhuli ng community review at/o anti-gaming checks alinsunod sa BENCHMARK_SPEC §9.3).

---

## 6. Kaugnayan sa Ibang Specs

| Dokumentong Ito | Mga Tinutukoy | Para sa |
|--------------|-----------|-----|
| §2 threshold conditions | SCORING_SPEC §4 (composite), §2.1–2.2 (metrics), §5 (tiers) | Mga depinisyon at scale ng metric |
| §2 community validation | BENCHMARK_SPEC §7 | Human review protocol |
| §3 sandbox execution | BENCHMARK_SPEC §8.2 | Sovereignty mechanism |
| §3 ownership transfer | BENCHMARK_SPEC §8.3 | IP transfer terms |
| §1.6 dependency classes | Method Interface spec; Method Submission Agreement §2.6; BENCHMARK_SPEC §8.6 | Mga class definition, admissibility terms, sandbox network policy |
| §4 cost-adjusted prizes | SCORING_SPEC §6.3 | Cost-adjusted formula |

---

## 7. Code–Spec Synchronization

### 7.1 Canonical Source

Ang dokumentong ito (`arena/website/docs/specifications/prize-spec.md`) ang canonical source para sa:
- Mga depinisyon ng prize pool (§2)
- Threshold conditions (§2.x)
- Proseso ng claim (§3)
- Mga tuntunin sa diskwalipikasyon (§5)

### 7.2 Mga Kinakailangan sa Implementation

Kapag na-activate ang isang prize pool:
1. Dapat ipakita ng leaderboard UI ang mga aktibong prize at ang kanilang threshold conditions
2. Dapat i-flag para sa community review ang mga run card na nakakatugon sa automated thresholds (conditions 1–3)
3. Naka-capture na ng `quality_tier` field sa run card schema ang tier ("deployable", "fluent")
4. Walang kailangang bagong code changes sa harness — ang prize spec ay isang policy layer sa ibabaw ng umiiral na scoring

---

*Dapat compatible ang mga prize structure sa ownership transfer terms. Maaaring i-claim ng winner ang prize, ngunit nagiging pag-aari ng governance org ang method kung maaabot nito ang Deployable tier. Sinasadya ito — pinopondohan ng prize ang paglikha ng teknolohiyang pag-aari ng komunidad ng wika.*