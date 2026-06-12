---
sidebar_position: 7
title: "Balangkas ng Disenyo ng Corpus"
---
# Balangkas sa Disenyo ng Evaluation Corpus

> **Bersyon:** 1.0  
> **Katayuan:** Draft  
> **Layunin:** Isang sistematikong metodolohiya para sa pagbuo ng mga evaluation corpus na nagbubunga ng wasto, maaasahan, at makabuluhang pangwikang pagtatasa ng kalidad ng pagsasalin. Ito ang opisyal na sanggunian kung paano dinidisenyo, binubuo, at pinananatili ang mga Champollion evaluation dataset.

---

## 1. Mga Prinsipyo sa Disenyo

### 1.1 — Bakit Hindi Public Benchmarks?

Ang mga pampublikong parallel corpus (FLORES+, Tatoeba, WMT test sets, OPUS) ay magagamit para sa development at debugging ngunit **hindi kasama sa official leaderboard evaluation**. Tuwiran ang dahilan:

**Contamination.** Ang mga frontier LLM ay sinasanay sa napakalalaking web scrape. Anumang parallel text na umiral na nang pampubliko — lalo na sa mga curated at malawakang binabanggit na benchmark dataset — ay malamang na nasa kanilang training data. Kapag sinuri ninyo ang GPT-4o sa FLORES+ at nakakuha ito ng 85 chrF++, hindi ninyo matutukoy kung "mahusay ang model sa pagsasalin" o "nakabisado ng model ang mga partikular na pares ng pangungusap na ito." Hindi ito isang teoretikal na alalahanin — [ipinakita ng pananaliksik](https://arxiv.org/abs/2311.04850) ang nasusukat na epekto ng contamination sa mga MT benchmark.

Para sa Champollion, napakahalaga nito dahil:
- Pangunahing inihahambing ng aming leaderboard ang mga LLM-based method
- Ang aming value proposition ay *tapat at masusing evaluation*
- Ang aming target users (mga pamayanang pangwika) ay gumagawa ng mga pasya sa deployment batay sa mga score na ito

### 1.2 — Mga Pangunahing Kinakailangan

Dapat matugunan ng bawat Champollion evaluation corpus ang mga sumusunod:

| Kinakailangan | Rasyonal |
|-------------|-----------|
| **Human-authored** | Walang synthetic data. Ang lahat ng source text at reference translation ay dapat isulat ng tao. Maaaring tumulong ang LLMs sa alignment at formatting ngunit hindi kailanman dapat bumuo ng content. |
| **Hindi pampublikong available sa parallel form** | Maaaring pampubliko ang source text; maaaring pampubliko ang reference translations; ngunit ang partikular na *pagpapares* ay hindi dapat umiiral bilang downloadable parallel corpus. |
| **Provenance-tracked** | Dapat may nakadokumentong pinagmulan ang bawat entry: source document, translator, license, date. |
| **Linguistically informed** | Dapat gabayan ang coverage ng mga typological feature, hindi ng random sampling. |
| **Domain-stratified** | Dapat sumaklaw ang mga entry sa mga tinukoy na text domain na may kontroladong representasyon. |
| **Difficulty-tiered** | Dapat italaga ang mga entry sa difficulty tiers (1–5) batay sa structural complexity. |
| **Version-controlled** | Ang mga corpus version ay content-hashed. Maikukumpara lamang ang mga score sa loob ng parehong version. |
| **Community-reviewable** | Dapat marepaso ng mga miyembro ng pamayanang pangwika ang reference translations. |

---

## 2. Pagpili ng Source Text

### 2.1 — Domain Taxonomy

Sinusuri ng Champollion ang pagsasalin para sa **mga praktikal na konteksto ng deployment**, hindi para sa akademikong ehersisyo. Sinasalamin ng domain taxonomy ang mga uri ng teksto sa totoong mundo na nakakaharap ng mga gumagamit ng pagsasalin:

| Domain | Code | Paglalarawan | Mga Halimbawang Source |
|--------|------|-------------|-----------------|
| **Software UI** | `ui` | Mga label ng button, menu item, error message, tooltip, onboarding flow | Mga string ng open-source app, documentation portal |
| **Opisyal/Administratibo** | `admin` | Mga dokumento ng pamahalaan, legal notice, form, pahayag ng patakaran | Mga pampublikong publikasyon ng pamahalaan, mga dokumentong munisipal |
| **Pang-edukasyon** | `edu` | Nilalaman ng textbook, lesson material, tekstong instructional | Mga nailathalang materyal na pang-edukasyon, gabay sa pagtuturo |
| **Narrative/Literary** | `lit` | Mga kuwento, tekstong kultural, transkripsyon ng oral history | Mga nailathalang aklat, cultural archives (may pahintulot) |
| **Conversational** | `conv` | Diyalogo, mga palitang parang chat, impormal na nakasulat na komunikasyon | Mga nailathalang dialog corpus, screenplay, transcript ng interview |
| **Technical** | `tech` | API documentation, README files, technical specifications | Dokumentasyon ng open-source project |
| **Health/Medical** | `health` | Medikal na impormasyong nakatuon sa pasyente, public health messaging | Mga publikasyong pangkalusugan ng pamahalaan |
| **News/Journalistic** | `news` | Mga artikulo ng balita, press release, kasalukuyang pangyayari | Mga pahayagan ng komunidad, Indigenous media outlets |

### 2.2 — Domain Distribution

Dapat tunguhin ng isang standard evaluation corpus ang sumusunod na distribusyon. Maaaring mag-iba ang eksaktong porsiyento ayon sa language pair batay sa kung aling mga uri ng teksto ang pinakanauugnay sa target community:

| Domain | Target % | Rasyonal |
|--------|----------|-----------|
| Software UI | 25% | Pangunahing deployment context para sa mga gumagamit ng champollion CLI |
| Opisyal/Administratibo | 15% | High-stakes translation na may legal na implikasyon |
| Pang-edukasyon | 15% | Pangunahing use case para sa language revitalization |
| Narrative/Literary | 10% | Sinusubok ang kultural na nuance at literary register |
| Conversational | 10% | Sinusubok ang impormal na register at natural na pattern ng pananalita |
| Technical | 10% | Sinusubok ang precision at consistency ng terminolohiya |
| Health/Medical | 10% | High-stakes, sinusubok ang domain-specific vocabulary |
| News/Journalistic | 5% | Sinusubok ang kontemporaryong bokabularyo at neutral na register |

### 2.3 — Pamantayan sa Pagpili ng Source

Kapag pumipili ng source texts para sa bagong corpus:

1. **License compatibility.** Dapat nasa ilalim ng lisensiyang nagpapahintulot sa paggamit sa isang evaluation corpus ang source text. Mas mainam ang CC BY, CC BY-SA, o public domain. Idokumento ang license.

2. **Recency.** Mas mainam ang mga tekstong nailathala sa loob ng huling 10 taon. Nagbabago ang wika — lalo na ang bokabularyo tungkol sa teknolohiya, pamamahala, at medisina.

3. **Register diversity.** Sa loob ng bawat domain, humanap ng mga teksto sa iba’t ibang antas ng pormalidad. Ang isang government press release (pormal) at isang government social media post (impormal) ay parehong nasa domain na `admin` ngunit magkaibang register.

4. **Cultural relevance.** Para sa Indigenous at minority languages, bigyang-priyoridad ang mga tekstong mahalaga sa komunidad — mga dokumento sa land management, materyal na pang-edukasyon sa wika, mga tekstong pangangalaga ng kultura — kaysa sa mga tekstong nagkataong umiiral sa parallel.

5. **Walang machine-translated sources.** Kung ang isang "parallel" document ay ginawa sa pamamagitan ng pagpapatakbo ng orihinal sa Google Translate at saka post-editing, HINDI ito katanggap-tanggap bilang reference translation. Dapat maging independiyenteng human translation ang reference.

---

## 3. Difficulty Tier System

### 3.1 — Mga Kahulugan ng Tier

Itinatalaga ang bawat entry sa isang difficulty tier (1–5) batay sa structural complexity ng *source text*, hindi sa kahirapan ng pagsasalin (na nag-iiba ayon sa method).

| Tier | Label | Structural Characteristics |
|------|-------|---------------------------|
| 1 | **Elementary** | Mga simpleng pangungusap. Iisang clause. Present tense. Karaniwang bokabularyo. Walang idiom. Walang embedded structures. |
| 2 | **Intermediate** | Compound sentences. Dalawang clause na pinagdugtong ng conjunction. Past/future tense. Ilang domain vocabulary. |
| 3 | **Advanced** | Complex sentences. Subordinate clauses, relative clauses. Mixed tenses. Domain-specific terminology. Passive voice. |
| 4 | **Expert** | Maramihang embedded clauses. Legal/technical register. Conditional structures. Abstract concepts. Cultural references. |
| 5 | **Extreme** | Siksik na prosa na may maraming sabay-sabay na hamon: nested subordination, malabong pronoun reference, cultural idioms, mixed register, bihirang bokabularyo. |

### 3.2 — Linguistically Informed Difficulty Factors

Bukod sa structural complexity, naaapektuhan ang difficulty ng **typological distance** sa pagitan ng source at target language. Ang mga salik na ito ay hinango mula sa WALS typological features at classification data ng language card:

| Salik | Mababang Difficulty | Mataas na Difficulty |
|--------|---------------|-----------------|
| **Word order** | Parehong basic order (hal., SVO→SVO) | Magkaibang basic order (hal., SVO→SOV) |
| **Morphological type** | Magkatulad na type (hal., analytic→analytic) | Magkaibang type (hal., analytic→polysynthetic) |
| **Grammatical gender** | Parehong sistema o walang gender | Walang gender ang source, may complex gender ang target |
| **Honorific/register** | Walang register marking | May complex register system ang target (hal., Japanese, Korean) |
| **Script** | Parehong script | Magkaibang script (kailangan ang transliteration) |
| **Animacy** | Walang animacy distinction | May animacy-based agreement ang target (hal., Cree) |
| **Evidentiality** | Walang evidentiality | Minamarkahan ng target ang information source sa gramatika |

### 3.3 — Tier Distribution

Ang isang standard corpus ay dapat magkaroon ng humigit-kumulang:

| Tier | Target % | Rasyonal |
|------|----------|-----------|
| 1 | 15% | Nagtatatag ng baseline — dapat kayanin ito kahit ng mahihinang method |
| 2 | 25% | Pangkaraniwang praktikal na pagsasalin |
| 3 | 30% | Dito nagiging nakikita ang mga pagkakaiba sa kalidad ng method |
| 4 | 20% | Inihihiwalay ang mabubuting method mula sa napakahuhusay |
| 5 | 10% | Ceiling test — napakakaunting method ang makakahawak nito nang maayos |

---

## 4. Kalidad ng Reference Translation

### 4.1 — Mga Kinakailangan para sa Translator

Dapat likhain ang reference translations ng mga taong:

1. **Fluent speakers** ng target language (L1 o katumbas)
2. **Literate** sa parehong source at target language
3. **Domain-aware** para sa domain ng teksto (medical translator para sa health texts, atbp.)
4. **Independent** — hindi dapat magkaroon ang translator ng access sa anumang MT output para sa parehong teksto habang nagsasalin

### 4.2 — Translation Brief

Tumatanggap ang bawat translator ng brief na kinabibilangan ng:

- Ang **register** na gagamitin (formal, conversational, atbp.)
- Ang **target audience** (general public, specialists, children, atbp.)
- Anumang **terminology conventions** na espesipiko sa language community
- Tahasang tagubilin: "Isalin ang kahulugan, hindi ang mga salita. Mas mahalaga ang natural pakinggang salin kaysa sa literal na salin."

### 4.3 — Quality Assurance

1. **Dual translation.** Sa pinakamainam na kalagayan, may dalawang independent reference translation ang bawat entry mula sa magkaibang translator. Kung hindi ito magagawa, bigyang-priyoridad ang dual translation para sa Tiers 4–5.

2. **Community review.** Dapat repasuhin ang reference translations ng kahit isang karagdagang speaker na hindi gumawa ng salin.

3. **Acceptable variants.** Para sa bawat reference, idokumento ang mga kilalang katanggap-tanggap na variant (word order, orthographic conventions, dialectal forms). Pinapakain ng mga ito ang metric na `equivalent_match_rate`.

### 4.4 — Ano ang Nagpapasama sa Isang Reference

| Problema | Bakit Nito Pinawawalang-bisa ang Evaluation |
|---------|------------------------------|
| Machine-translated pagkatapos ay post-edited | Pinananatili ng post-editing ang MT structure; pinaparusahan nito ang mga method na gumagawa ng mas natural na salin |
| Isinalin ng learner, hindi fluent speaker | Maaaring maglaman ang reference ng mga error na nagpaparusa sa tamang MT output |
| Sobrang literal | Mababa ang score ng natural translations laban sa literal references |
| Iisang valid interpretation para sa ambiguous source | Pinaparusahan ang valid alternative interpretations |

---

## 5. Pag-iwas sa Contamination

### 5.1 — Ang Contamination Threat Model

| Banta | Paglalarawan | Mitigation |
|--------|-------------|------------|
| **Training data overlap** | Sinasanay ang LLMs sa parallel corpus | Huwag ilathala nang pampubliko ang parallel corpus |
| **Few-shot leakage** | Ginagamit ng method author ang eval entries bilang few-shot examples | Fingerprint-check: natutukoy at nafa-flag ang mga entry sa prompt |
| **Indirect contamination** | Umiiral ang source text sa LLM training data (monolingual) | Katanggap-tanggap — inaasahan ang monolingual source text. Dapat maging bago ang *pagpapares*. |
| **Crowd contamination** | Ibinabahagi ng community reviewers ang entries nang pampubliko | Ipinagbabawal ng license terms ang redistribusyon ng parallel corpus |

### 5.2 — Corpus Secrecy Tiers

| Tier | Visibility | Gamit |
|------|-----------|-----|
| **Public development set** | Ganap na pampubliko | Method development, debugging, regression testing. HINDI inilalathala sa leaderboard ang mga score. |
| **Held-out evaluation set** | Nakikita ang source text, secret ang references | Official leaderboard evaluation. Tumatanggap ang mga method ng source text at nagbabalik ng translations; server-side ang scoring. Hindi kailanman inilalantad sa method ang references. |
| **Gold-standard set** | Ganap na secret, community-controlled | Community-validated evaluation. Pinamamahalaan ng governance organization. Ginagamit para sa "Community Validated" verification tier. |

### 5.3 — Rotation Policy

Dapat **i-rotate** paminsan-minsan ang evaluation corpora:

1. Pagkaraan ng 12 buwan ng paggamit ng corpus, simulan ang pagbuo ng kapalit
2. I-retire ang lumang corpus patungo sa katayuang "development set" (public)
3. I-promote ang bagong corpus bilang "held-out evaluation set"
4. Pinipigilan nito ang unti-unting contamination sa pamamagitan ng paulit-ulit na optimization laban sa isang fixed target

---

## 6. Workflow sa Pagbuo ng Corpus

### 6.1 — Step-by-Step Process

```
Step 1: Language Pair Selection
    └─ Identify target language, read language card
    └─ Review typological features (WALS), contact influences, scripts
    └─ Identify which difficulty factors apply

Step 2: Source Text Curation
    └─ Identify candidate source documents per domain
    └─ Verify licenses
    └─ Extract candidate sentences/segments
    └─ Classify by domain and preliminary difficulty tier

Step 3: Segment Selection
    └─ Sample segments to match domain distribution (§2.2)
    └─ Sample segments to match difficulty distribution (§3.3)
    └─ Ensure linguistic phenomenon coverage (§6.2)
    └─ Target minimum corpus size (§6.3)

Step 4: Reference Translation
    └─ Assign segments to qualified translators
    └─ Provide translation brief
    └─ Collect translations
    └─ Dual-translate Tier 4–5 entries

Step 5: Quality Assurance
    └─ Community review of references
    └─ Document acceptable variants
    └─ Flag and resolve disagreements

Step 6: Metadata & Packaging
    └─ Assign final difficulty tiers
    └─ Add provenance metadata per entry
    └─ Content-hash the corpus for versioning
    └─ Package as corpus JSON per harness spec

Step 7: Registration
    └─ Register in Supabase datasets table
    └─ Add to ATTRIBUTION.md if new sources used
    └─ Document in arena website
```

### 6.2 — Coverage ng Linguistic Phenomenon

Dapat magsama ang bawat corpus ng mga entry na sumusubok sa partikular na linguistic phenomena na nauugnay sa language pair. Hinango ang mga ito mula sa mga field na `linguisticChallenges` at `contactInfluences` ng language card:

**Universal phenomena (lahat ng language pair):**
- Pronoun resolution (ambiguous antecedents)
- Negation (single, double, scope)
- Quantifiers (all, some, none, most)
- Temporal expressions (relative dates, durations)
- Named entities (people, places, organizations)
- Numbers and measurements
- Lists and enumeration

**Pair-specific phenomena (mula sa language card):**
- Para sa polysynthetic targets: complex verb morphology, incorporation
- Para sa gendered targets: gender agreement, neutral/inclusive reference
- Para sa SOV targets: clause-final verbs, postpositions
- Para sa tone languages: tone-dependent meaning distinctions
- Para sa honorific languages: register markers, social context
- Para sa contact languages: code-switching boundaries, loanword integration

### 6.3 — Minimum Corpus Size

Nangangailangan ang statistical reliability ng minimum entry counts. Batay ang mga ito sa paired bootstrap confidence interval requirements (mula sa `significance.py`):

| Layunin | Minimum Entries | Recommended |
|---------|-----------------|-------------|
| Development set | 50 | 100–200 |
| Held-out evaluation set | 100 | 200–500 |
| Gold-standard set | 200 | 500+ |
| Per-domain minimum | 10 | 25+ |
| Per-tier minimum | 10 | 20+ |

**Bakit 100 ang minimum para sa evaluation?** Sa mas kaunti sa ~100 entry, hindi maaasahang matutukoy ng paired bootstrap significance tests (1,000 resamples) ang mga pagkakaibang mas maliit sa ~5 chrF++ points. Sa 200+ entry, matutukoy natin ang ~2-point differences sa p<0.05.

---

## 7. Corpus JSON Format

Sinusunod ng bawat corpus entry ang harness specification:

```json
{
  "id": "edtekla-dev-v1-042",
  "source": "The school board will meet on Tuesday to discuss the new curriculum.",
  "reference": "ᑭᓯᑭᓄᐦᐊᒫᑐᐏᓐ ᑲ ᐃᔑ ᐱᒥᐸᔨᐦᑕᐦᒃ ᑭᔅᑭᓄᐦᐊᒫᑐᐏᓇ ᐁ ᐃᔑ ᒫᒥᑐᓀᔨᐦᑕᐦᒃ ᐅᔥᑭ ᑭᔅᑭᓄᐦᐊᒫᑫᐏᓂᔭ ᓂᔓ ᑭᔑᑲᐤ",
  "acceptable_variants": [
    "ᑭᔅᑭᓄᐦᐊᒫᑐᐏᓐ ᓂᔓ ᑭᔑᑲᐤ ᑲ ᐃᔑ ᒫᒥᑐᓀᔨᐦᑕᐦᒃ ᐅᔥᑭ ᑭᔅᑭᓄᐦᐊᒫᑫᐏᓂᔭ"
  ],
  "domain": "edu",
  "difficulty": 3,
  "phenomena": ["temporal_expression", "named_entity", "future_tense"],
  "provenance": {
    "source_doc": "EdTeKLA Module 4, Unit 7",
    "source_license": "CC BY-NC-SA 4.0",
    "translator": "anonymous-speaker-001",
    "translator_qualification": "L1 Plains Cree, certified translator",
    "translation_date": "2025-11-15",
    "reviewer": "anonymous-speaker-002",
    "review_date": "2025-12-01"
  }
}
```

---

## 8. Anti-Gaming Measures

### 8.1 — Corpus Integrity

| Measure | Implementation |
|---------|----------------|
| **Content hashing** | Corpus version = SHA-256 ng sorted entry IDs + references. Anumang pagbabago ay nagbubunga ng bagong version. |
| **Entry fingerprinting** | May content-derived ID ang bawat entry. Kung may magsumite ng results laban sa modified corpus, hindi magmamatch ang fingerprint. |
| **Held-out enforcement** | Para sa official evaluation, TANGING source text ang natatanggap ng mga method. Hindi kailanman inilalantad ang references. Server-side ang scoring. |
| **Rotation schedule** | Taunang iniikot ang corpora upang maiwasan ang long-term optimization laban sa fixed target. |

### 8.2 — Submission Integrity

| Measure | Implementation |
|---------|----------------|
| **Deterministic fingerprint** | Hina-hash ang run config (model, temperature, prompt, corpus version). Ang identical configs ay nagbubunga ng identical fingerprints. |
| **Cherry-pick detection** | Dapat ibunyag ng submitters ang lahat ng runs, hindi lamang ang pinakamainam. Nafa-flag ang maramihang submission na may parehong fingerprint. |
| **Contamination check** | Kung lumitaw nang verbatim ang eval entries sa prompt o coaching data ng method, madi-disqualify ang submission. |

---

## 9. Umiiral na Corpora

### 9.1 — EDTeKLA Development Set v1

| Property | Value |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Pair** | EN → CRK (Plains Cree, SRO) |
| **Entries** | 404 (`master_corpus.json`: 62 gold + 342 textbook); 548 total available |
| **Domains** | Pang-edukasyon (100%) |
| **Tiers** | 1–5 (distribution TBD per entry audit) |
| **License** | CC BY-NC-SA 4.0 |
| **Status** | Development set (public) |

**Mga Limitasyon:** Iisang domain (pang-edukasyon lamang). Walang domain stratification. Maaaring mangailangan ng audit ang tier assignments. Nililimitahan ng maliit na corpus size ang statistical power para sa significance testing.

### 9.2 — Mga Planong Corpora

| Corpus | Pair | Status | Owner |
|--------|------|--------|-------|
| EN → TL (Filipino) custom corpus | EN → TL | Planned | Project owner |
| EN → CRK held-out set | EN → CRK | Future (needs community partner) | Community governance org |

---

## 10. Integration sa Language Card

Nakikipag-integrate ang corpus framework sa language card system:

1. Ang **domain selection** ay ginagabayan ng `linguisticChallenges` ng card — kung may natatanging hamon ang isang wika (polysynthesis, tone, animacy), dapat magsama ang corpus ng mga entry na sumusubok sa mga ito.

2. Ginagamit ng **difficulty calibration** ang `classification` ng card — naaapektuhan ng typological distance sa pagitan ng source at target families kung ano ang maituturing na "difficult."

3. Ginagamit ng **register coverage** ang `registers` ng card — kung may mga tinukoy na register ang isang wika (formal-filipino, taglish-professional, taglish-casual), dapat magsama ang corpus ng mga entry sa bawat antas ng register.

4. Ginagamit ng **contact influence testing** ang `contactInfluences` ng card — para sa mga wikang may matitinding borrowing layers (Filipino: Spanish + English + Arabic), magsama ng mga entry na sumusubok kung tama bang hinahawakan ng mga method ang loanwords kumpara sa over-translating ng mga ito.

5. Ginagamit ng **script handling** ang `scripts[]` ng card — para sa multi-script languages (Serbian: Cyrillic + Latin), magsama ng mga entry na sumusubok sa tamang script selection.

---

## Mga Sanggunian

- **Champollion Scoring Specification** — tumutukoy sa lahat ng metrics, composite weights, quality tiers
- **Champollion Benchmark Specification** — evaluation protocol, corpus format, data sovereignty
- **WALS** (World Atlas of Language Structures) — typological features database
- **Glottolog** — language classification source of truth
- **ISO 639-3** — language identification standard
- **EdTeKLA** — source ng unang evaluation corpus

---

*Ang dokumentong ito ay isang living specification. I-update ito habang binubuo ang mga bagong corpora at natututuhan ang mga aral.*