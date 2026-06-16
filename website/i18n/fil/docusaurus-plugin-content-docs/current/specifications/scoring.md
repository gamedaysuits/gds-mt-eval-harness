---
sidebar_position: 5
title: "Espesipikasyon ng Pagmamarka"
slug: '/specifications/scoring'
related:
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
    note: "When a score difference actually means something"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
    note: "The tool that computes these metrics"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "These scores, live"
---
# Espesipikasyon ng Pagmamarka

> **Executive Summary.** Ito ang nag-iisang pinagmumulan ng katotohanan para sa lahat ng evaluation metrics, composite scoring, quality tiers, at cost analysis sa Champollion MT evaluation ecosystem. Ang language-specific evaluation metrics — FST morphological validity, linter equivalence classes, at deterministic semantic validation — ay sama-samang pinangalanang **LYSS** (Linguistically-informed Yield & Structural Scoring). Bawat metric na kinukuwenta ng harness, bawat weight sa composite formula, at bawat tier threshold ay tinutukoy dito — at dito lamang. Ang code, dokumentasyon, at database schemas ay nagmumula sa dokumentong ito. Kapag may salungatan, ang dokumentong ito ang awtoritatibo.
>
> **Saklaw.** Tinutukoy ng dokumentong ito kung *ano* ang sinusukat natin at *paano natin ito binibigyan ng score*. Hindi nito tinutukoy ang run card schema (tingnan ang BENCHMARK_SPEC §3), ang benchmark protocol (BENCHMARK_SPEC §6), o ang leaderboard rules (tingnan ang arena docs). Tinutukoy ng mga dokumentong iyon ang isang ito para sa metric definitions at scoring logic.
>
> Huling na-update: 2026-06-07

---

## 1. Pilosopiya sa Pagmamarka

### 1.1 Pilosopiya ng Microeval

> *"Kung tutuon lamang tayo sa kung ano ang nagge-generalize, hindi maiiwasang makalimutan natin kung saan ito hindi gumagana — at mawawala sa atin ang mga wikang ito at ang lahat ng kanilang kaalaman at karunungan."*

Isinasagawa ng proyektong ito ang **microeval development**: pagbuo ng evaluation metrics na iniangkop sa mga partikular na wika gamit ang pinakamahuhusay na kasalukuyang linguistic tools — finite-state transducers, bilingual dictionaries, morphological analyzers, linguist-curated equivalence rules. Kabaligtaran ito ng nangingibabaw na paradigma sa MT evaluation, na naghahanap ng universal metrics na gumagana sa lahat ng wika. Mahalaga ang universal metrics, ngunit pinakamahina ang mga ito mismong kung saan pinakakailangan ang mga ito: para sa mga wikang may kumplikadong morpolohiya, limitadong training data, at walang representasyon sa neural metric training sets.

Hindi tayo umuunlad sa machine translation para sa maraming wika sa mundo hindi lamang dahil kulang tayo sa corpora, kundi dahil **hindi pa nga natin alam kung ano ang itsura ng pag-unlad** — kulang tayo sa automated evaluation tools upang masukat kung bumubuti ang isang translation system. Ang LYSS ay ang aming pagtatangkang buuin ang mga tool na iyon, wika sa bawat wika, gamit ang anumang linguistic resources na mayroon.

### 1.2 Ang Automated Metrics ay mga Proxy

Bawat metric na tinutukoy dito ay machine-computed. Kapaki-pakinabang ang mga ito para sa mabilis na iteration, sistematikong paghahambing, at pagtukoy ng regressions. **Hindi sila kapalit ng paghuhusga ng tao**. Ang quality tiers sa §5 ay mga heuristic label — tanging human review lamang ang makapagkukumpirma ng aktuwal na usability.

### 1.3 Multi-Signal Design

Walang iisang metric ang ganap na nakakahuli sa kalidad ng pagsasalin. Maaaring may perpektong chrF++ overlap ang isang salin ngunit mabigo sa morphological validation. Maaari itong pumasa sa FST checks ngunit magdala ng maling kahulugan. Maaari itong maging semantically accurate ngunit stylistically alien sa target language. Pinagsasama ng composite score sa §4 ang maraming independent signals, na bawat isa ay kumukuha ng ibang dimensiyon ng kalidad.

### 1.4 Extensibility

Hindi sarado ang metric inventory na ito. Nagdadala ang mga bagong wika ng mga bagong kinakailangan: tone accuracy para sa tonal languages, diacritical precision para sa Semitic scripts, syllabary correctness para sa Cree. Ang architecture (MetricPlugin protocol, weighted composite na may re-normalization) ay idinisenyo upang maidagdag ang metrics nang hindi sinisira ang existing scores. Ang language-specific metrics (hal., linter at semantic validator ng CRK) ay idinedeklara sa language cards sa ilalim ng `evalMetrics` at nilo-load mula sa `eval_standards/` — ang harness ay may kasamang generic behavioral metrics lamang (code-switching, hallucination, terminology).

### 1.5 Tatlong Dimensiyon ng Ebalwasyon

Sinusukat ng bawat run card ang tatlong independent dimensions:

```
Quality   — How good is the translation?   (composite score, §4)
Cost      — How much does it cost?          (cost metrics, §6)
Speed     — How fast does it run?           (speed metrics, §7)
```

Mga independent axis ang mga ito. Maaaring mataas ang kalidad ng isang method ngunit mahal, mabilis ngunit hindi accurate, o anumang kombinasyon. Pinapagana ng leaderboard ang pag-sort ayon sa alinmang dimensiyon. Ang cost-adjusted score (§6.3) lamang ang metric na nagsasama ng mga dimensiyon.

### 1.6 Status ng Validation

Bawat metric sa espesipikasyong ito ay may **validation status** na hiwalay sa implementation status nito (§3). Sinusubaybayan ng implementation status kung umiiral ang code. Sinusubaybayan ng validation status kung naipakitang may correlation ang metric sa human quality judgments.

| Validation Level | Kahulugan | Kasalukuyang Metrics |
|------------------|---------|----------------|
| **✅ Externally validated** | May mga nalathalang human-correlation studies (WMT, academic papers) | `chrf_plus_plus`, `bleu`, `comet_score` |
| **⚡ Proxy-validated** | Validated para sa high-resource languages; unvalidated para sa aming target LRLs | `comet_score` (validated para sa EU pairs, hindi para sa CRK) |
| **🔶 Engineering heuristic** | Idinisenyo mula sa linguistic principles o observed failure modes; walang human correlation data | `fst_acceptance_rate`, `equivalent_match_rate`, `semantic_score`, `code_switching_rate`, `hallucination_rate`, `terminology_adherence` |
| **🔲 Unvalidated** | Hindi pa nasusubok sa anumang data | `morphological_accuracy`, `orthographic_accuracy`, `consistency_score` |

> **Ano ang ibig sabihin nito sa praktika.** Pinagsasama ng composite score (§4) ang metrics sa lahat ng validation levels. Isa itong tahasang design choice: naniniwala kami na ang structurally-grounded engineering heuristic (FST acceptance) ay mas nagbibigay-kaalaman para sa polysynthetic languages kaysa sa neural metric na validated lamang sa European pairs (COMET). Ngunit hindi pa namin ito napatutunayan. Dapat ituring ang composite score bilang **engineering estimate**, hindi validated quality measurement, hanggang makumpleto ang human correlation studies para sa bawat target language.
>
> **Mga kinakailangang validation experiments** (tingnan ang `mt-evaluation-landscape.md` §6 at `speaker-validation.md`):
> 1. Human judgment correlation study: 200+ sentence pairs na ni-rate ng 3+ bilingual speakers
> 2. Pagsukat ng FST false rejection rate sa isang representative corpus
> 3. Second-language port (North Sámi) upang subukin ang generalization
> 4. Direktang paghahambing sa COMET sa parehong data


---

## 2. Metric Inventory {#2-metric-inventory}

Inaayos ang metrics sa apat na kategorya. Bawat metric ay may implementation status, scale, at level (per-entry, corpus-level, o pareho).

### 2.1 Surface Metrics

Inihahambing ng surface metrics ang predicted translation sa reference translation sa string level. Hindi kailangan ng mga ito ng linguistic tools — string comparison lamang.

| ID | Metric | Status | Scale | Level | Implementation |
|----|--------|--------|-------|-------|---------------|
| `exact_match_rate` | Exact Match | ✅ Implemented | 0.0–1.0 | Both | Binary: predicted == reference ba? Corpus rate = matches / total. |
| `equivalent_match_rate` | Equivalent Match | ⚡ Partial | 0.0–1.0 | Both | Tumutugma ba ang predicted output sa anumang accepted variant? Para sa CRK: implemented sa pamamagitan ng `CrkLinterMetric` ng CRK eval standard (sa `eval_standards/crk/`) gamit ang deterministic variant-class rules (word order, orthographic, optional particle, lemma synonym, progressive ambiguity). Awtomatikong nilo-load sa pamamagitan ng `evalMetrics` declaration ng CRK language card. Nangangailangan ang generic cross-language implementation ng per-entry `variants[]` sa corpus. |
| `chrf_plus_plus` | chrF++ | ✅ Implemented | 0–100 | Both | Character n-gram F-score (sacrebleu). Matibay sa morphological variation. Ang pangunahing surface metric para sa agglutinative/polysynthetic languages. Gumagamit ang per-entry ng `sentence_chrf`; gumagamit ang corpus ng `corpus_chrf`. |
| `bleu` | BLEU | ✅ Implemented | 0–100 | Corpus | Word-level n-gram precision (sacrebleu). **Hindi kasama sa composite** — hindi patas na pinaparusahan ng word-level scoring ang morphological variation. Kinukuwenta at iniuulat para sa compatibility sa MT literature. |
| `ter` | Translation Edit Rate | ✅ Implemented | 0–∞ (mas mababa ay mas mabuti) | Both | Minimum edit distance sa pagitan ng predicted at reference, normalized ayon sa reference length (sacrebleu `corpus_ter`). Kinukuwenta kasabay ng chrF++ at BLEU. Hindi kasama sa composite — may correlation ito sa chrF++ kaya madodoble ang bilang ng surface similarity kung isasama ang pareho. |
| `length_ratio` | Length Ratio | ✅ Implemented | 0–∞ (1.0 ang ideal) | Both | `len(predicted) / len(reference)` sa characters. Tinutukoy ang truncation (<0.5) at inflation/hallucination (>2.0). Ina-average sa entries sa corpus level. |

### 2.2 Structural Metrics

Tini-validate ng structural metrics ang linguistic well-formedness ng salin. Nangangailangan ang mga ito ng language-specific tools (FST analyzers, morphological parsers) at sila ang pinakamalalakas na signal para sa morphologically rich languages.

| ID | Metric | Status | Scale | Level | Implementation |
|----|--------|--------|-------|-------|---------------|
| `fst_acceptance_rate` | FST Acceptance | ✅ Implemented | 0.0–1.0 | Both | Proporsiyon ng output words na tinatanggap ng finite-state transducer (GiellaLT). Ang isang salita ay "valid" kung nagbabalik ang FST ng kahit isang morphological analysis. Available para sa anumang wika na may GiellaLT `.hfstol` analyzer. |
| `morphological_accuracy` | Morphological Accuracy | 🔲 Planned | 0.0–1.0 | Both | Maaaring FST-valid ang isang salita ngunit may maling inflection (tamang root, maling suffix). Inihahambing ng metric na ito ang FST analysis ng predicted word sa inaasahang morphological features. Nangangailangan ng per-entry morphological annotations sa corpus. |
| `orthographic_accuracy` | Orthographic Accuracy | 🔲 Planned | 0.0–1.0 | Both | Tini-validate ang script-specific correctness: paggamit ng SRO macron/circumflex para sa Cree, diacritical marks para sa Inuktitut, vowel length markers para sa Ojibwe. Per-language rule sets. |

> **Bakit mahalaga ang structural metrics.** Ang OMT-1600 ng Meta — ang pinakamalaking MT system na nailathala kailanman (1,600 wika) — ay nag-e-evaluate gamit ang ChrF++, xCOMET, MetricX, at BLASER 3. Wala sa mga ito ang nagva-validate ng morphological correctness. Sinusukat ng ChrF++ ang character n-gram overlap: nire-reward nito ang strings na *mukhang* target language. Para sa polysynthetic languages, nangangahulugan ito na mataas ang score ng isang morphologically invalid word na may maraming kaparehong characters sa reference. Ang aming FST acceptance metric ay isang binary structural test: ang salita ay alinman sa valid form sa wika, o hindi. Walang ibang MT evaluation framework ang nagbibigay nito sa scale.

### 2.3 Semantic Metrics

Sinusukat ng semantic metrics ang meaning preservation gamit ang embeddings o learned models. Nahuhuli nila ang translations na magkaiba sa surface ngunit meaning-equivalent, at fina-flag ang translations na surface-similar ngunit semantically wrong.

| ID | Metric | Status | Scale | Level | Implementation |
|----|--------|--------|-------|-------|---------------|
| `semantic_score` | Semantic Similarity | ⚡ Partial | 0.0–1.0 | Both | CRK: verdict-weighted score mula sa `CrkSemanticMetric` ng CRK eval standard (sa `eval_standards/crk/`, proxy). Universal: cosine similarity ng sentence embeddings (source + predicted vs source + reference). Model TBD — dapat suportahan ang low-resource languages, kaya hindi maaari ang karamihan sa English-centric embedding models. |
| `comet_score` | COMET | ✅ Implemented | ~0.0–1.0 | Both | Learned MT evaluation metric (Unbabel). Trained sa human quality judgments. **Hindi kasama sa composite** — biased ang training data tungo sa high-resource European languages; hindi maaasahan ang scores para sa LRLs. Kinukuwenta kapag naka-install ang `unbabel-comet`. Iniuulat na may low-resource warning flag. Para sa 35 African languages, awtomatikong pinipili ng harness ang AfriCOMET (`masakhane/africomet-mtl`) sa pamamagitan ng `resolve_comet_model()`, na may mas mabuting human-judgment correlation para sa mga wikang iyon. |

> **Bakit hindi kasama ang COMET sa composite.** Ang COMET ay trained sa WMT human evaluation data, na lubhang nakatuon sa high-resource European language pairs. Kapag inilapat sa Plains Cree o iba pang LRLs, walang exposure ang internal representations ng model sa mga wikang iyon — nag-e-extrapolate ito mula sa mga wikang may pundamental na ibang morphological systems. Kapaki-pakinabang pa rin ang scores sa direksiyonal na paraan (mas mataas na COMET ≈ mas fluent-sounding na output sa pangkalahatan) ngunit hindi calibrated ang absolute values. Iniuulat namin ang COMET para sa transparency ngunit hindi namin hinahayaang makaapekto ito sa composite score hanggang ma-validate namin ito laban sa human judgments para sa bawat target language.

> **AfriCOMET para sa African languages.** Bawat language card ay may `metricModelSupport` field (tingnan ang language card spec §9) na nagdedeklara kung aling specialized COMET models ang trained para sa wikang iyon. Para sa 35 African languages (yor, hau, ibo, amh, swa, atbp.), idinedeklara ng card ang AfriCOMET (`masakhane/africomet-mtl`) — isang COMET model na fine-tuned sa African language MT human judgments ng Masakhane community. Awtomatikong pinipili ng harness ang recommended model sa pamamagitan ng `resolve_comet_model()` na nagbabasa mula sa language cards, ngunit maaari itong i-override gamit ang `--comet-model`. Ginagawa ang pagdaragdag ng bagong language→model mappings sa pamamagitan ng pagpapayaman sa language card (hindi sa pag-edit ng Python code).

### 2.4 Behavioral Metrics

Tinutukoy ng behavioral metrics ang specific failure modes sa translation output. Hindi nila direktang sinusukat ang kalidad — tinutukoy nila ang mga problema.

| ID | Metric | Status | Scale | Level | Implementation |
|----|--------|--------|-------|-------|---------------|
| `code_switching_rate` | Code-Switching Rate | ✅ Implemented | 0.0–1.0 (mas mababa ay mas mabuti) | Both | Proporsiyon ng output words na nasa source language (karaniwang English). Natutukoy sa pamamagitan ng Unicode script analysis at/o source-language word list. Napakakaraniwang LLM failure mode: naglalagay ang model ng English words kapag hindi nito alam ang katumbas sa target language. |
| `hallucination_rate` | Hallucination Rate | ✅ Implemented | 0.0–1.0 (mas mababa ay mas mabuti) | Both | Proporsiyon ng output content na walang kaukulang source content. Natutukoy sa pamamagitan ng word alignment o cross-lingual embedding overlap. Nahuhuli nito ang model na bumubuo ng plausible-sounding ngunit fabricated translations. |
| `terminology_adherence` | Terminology Adherence | ✅ Implemented | 0.0–1.0 | Both | Para sa coached methods: proporsiyon ng prescribed terminology terms na lumilitaw sa output. Nangangailangan ng coaching dictionary data. Sinusukat kung nirerespeto ng model ang expert-provided vocabulary. |
| `consistency_score` | Cross-Entry Consistency | 🔲 Planned | 0.0–1.0 | Corpus only | Isinasalin ba ng model ang parehong source term sa parehong paraan sa entries? Ipinahihiwatig ng mababang consistency na nanghuhula ang model sa halip na maglapat ng learned patterns. Nangangailangan ng repeated terms sa corpus entries. |

### 2.5 Compliance Metrics

Tini-validate ng compliance metrics na pinananatili ng translations ang structural integrity — placeholders, formatting, at typography conventions. Quality-gate checks ang mga ito, hindi quality scores.

| ID | Metric | Status | Scale | Level | Implementation |
|----|--------|--------|-------|-------|---------------|
| `compliance_index` | Double-Pass Compliance | ✅ Implemented | 0.0–1.0 | Both | Weighted composite: 60% variable integrity (napapanatili ba ang `{placeholder}` vars?) + 20% quote compliance (tamang quote characters ayon sa language card) + 20% casing compliance (walang Latin letter leakage para sa caseless languages). Kinukuwenta sa parehong raw at post-processed output. Sa pamamagitan ng `DoublePassCompliancePlugin`. |
| `repair_effectiveness` | Repair Effectiveness | ✅ Implemented | 0.0–1.0 | Corpus | Proporsiyon ng compliance violations na awtomatikong na-repair ng post-translation hooks. Sinusukat kung gaano napahusay ng quality gate ang raw output. |

> **Bakit wala sa composite ang compliance.** Sinusukat ng compliance metrics ang structural preservation (placeholders, quotes), hindi ang translation quality. Maaaring perpekto ang isang salin sa linguistic na aspeto ngunit mabigo sa compliance dahil nag-drop ito ng `{name}` variable. Quality gates ang mga ito — hinaharang nila ang bad output upang hindi ma-ship, ngunit hindi nila niraranggo ang translation quality.

---

## 3. Metric Status Tiers

Bawat metric sa §2 ay kabilang sa isa sa apat na implementation tiers:

| Tier | Kahulugan | Run Card Behavior |
|------|---------|-------------------|
| **✅ Implemented** | May code, tested, at kasalukuyang nagpo-produce ng values sa run cards | Numeric value sa run card |
| **⚡ Partial** | May language-specific proxy (hal., CRK) ngunit pending pa ang universal implementation | Numeric value kapag naaangkop ang proxy, `null` kung hindi |
| **🔲 Planned** | Naispesipika ngunit hindi pa implemented | `null` sa run card (field present, value absent) |
| **💡 Proposed** | Pinag-uusapan pa, hindi pa naispesipika | Wala sa run card |

Lumilipat ang isang metric mula Planned → Partial kapag:
1. Na-merge at na-test ang isang language-specific implementation
2. Nagpo-produce ito ng values para sa kahit isang language pair
3. Pending pa rin ang universal implementation (nakadokumento sa spec na ito)

Lumilipat ang isang metric mula Partial → Implemented kapag:
1. Na-merge at na-test ang isang language-agnostic implementation
2. Nagpo-produce ito ng values para sa anumang language pair nang walang language-specific plugins
3. Na-update ang dokumentong ito upang ipakita ang ✅ status

Lumilipat ang isang metric mula Planned → Implemented kapag:
1. Na-merge at na-test ang implementation
2. Na-validate ito sa kahit isang tunay na evaluation run
3. Na-update ang dokumentong ito kasama ang implementation details nito

Lumilipat ang isang metric mula Proposed → Planned kapag:
1. Napagkasunduan ang definition, scale, at computation method nito
2. Naidagdag ito sa dokumentong ito na may `🔲 Planned` status
3. Naidagdag ang null placeholder sa run card schema

---

## 4. Composite Score {#4-composite-score}

### 4.1 Formula

Ang composite score ay weighted average ng lahat ng *available* metrics, na nire-re-normalize upang ang weights ng available metrics ay mag-sum sa 1.0:

```
composite = Σ (weight_i × value_i)    for all available metrics
             ─────────────────────
             Σ weight_i               (re-normalization denominator)
```

Ang isang metric ay "available" kung ang value nito sa run card ay number (hindi `null`). Kapag unavailable ang isang metric — dahil walang FST ang wika, o dahil hindi pa implemented ang isang metric — ang weight nito ay nire-redistribute nang proporsiyonal sa natitirang metrics.

**Ibig sabihin nito, ang composite ay palaging comparable sa loob ng isang run:** ginagamit nito ang anumang available metrics at nagno-normalize nang naaayon. Valid ang cross-run comparison kapag gumagamit ang runs ng parehong set ng available metrics.

> [!WARNING]
> **Cross-run comparability.** Kapag naghahambing ng runs na may magkakaibang metric availability (hal., may FST scores ang isang run, wala ang isa), **hindi direktang comparable** ang composite scores. Ang composite na 0.72 na kinuwenta mula sa 5 metrics ay may dalang mas maraming impormasyon kaysa sa composite na 0.72 na kinuwenta mula sa 2 metrics. Nagpapakita ang leaderboard ng babala kapag nagkakaiba ang metric coverage sa pagitan ng compared runs. Para sa mahigpit na paghahambing, gumamit ng paired bootstrap significance tests (§8.2) sa shared metrics lamang.

### 4.2 Input Normalization

Bago pumasok sa composite formula, dapat nasa **0.0–1.0 scale** ang lahat ng metrics kung saan 1.0 = perfect:

| Metric | Native Scale | Normalization |
|--------|-------------|---------------|
| `exact_match_rate` | 0.0–1.0 | Wala (normalized na) |
| `equivalent_match_rate` | 0.0–1.0 | Wala |
| `fst_acceptance_rate` | 0.0–1.0 | Wala |
| `morphological_accuracy` | 0.0–1.0 | Wala |
| `chrf_plus_plus` | 0–100 | **Hatiin sa 100** |
| `semantic_score` | 0.0–1.0 | Wala |
| `code_switching_rate` | 0.0–1.0 (mas mababa = mas mabuti) | **`1.0 - value`** (invert: 0% code-switching = 1.0) |
| `hallucination_rate` | 0.0–1.0 (mas mababa = mas mabuti) | **`1.0 - value`** (invert) |
| `terminology_adherence` | 0.0–1.0 | Wala |

Ang metrics na hindi kasama sa composite (`bleu`, `comet_score`, `ter`, `length_ratio`, `consistency_score`) ay hindi ino-normalize para sa layuning ito.

### 4.3 Weight Tables {#43-weight-tables}

#### Profile A: Mga Wikang MAY FST Coverage

Para sa mga wikang may available na GiellaLT finite-state transducer. Ang structural metrics ay may 40% ng composite (FST 0.25 + morphological accuracy 0.15), na nagpapakita ng primacy ng morphological correctness para sa polysynthetic/agglutinative languages.

| Metric | Target Weight | Rationale |
|--------|--------------|-----------|
| `fst_acceptance_rate` | **0.25** | Pinakamataas na weight. Kung nire-reject ng FST ang isang salita, hindi ito valid form sa wika — anuman ang sabihin ng ibang metrics. Binary, structurally grounded. |
| `morphological_accuracy` | **0.15** | Maaaring FST-valid ang isang salita ngunit morphologically wrong (tamang root, maling inflection). Kasama ng FST, bumubuo ang structural metrics ng 40%. |
| `chrf_plus_plus` | **0.15** | Character n-gram overlap: ang pinakamahusay na surface-level proxy para sa polysynthetic languages. Mas mahusay nitong hinahawakan ang agglutinative morphology kaysa word-level metrics. |
| `semantic_score` | **0.15** | Meaning preservation kapag lumilihis ang surface form. Nahuhuli ang semantically wrong translations na pumapasa sa structural checks. |
| `equivalent_match_rate` | **0.10** | Nire-reward ang acceptable variants, hindi lamang ang iisang reference translation. Mahalaga para sa mga wikang may flexible word order. |
| `code_switching_rate` | **0.05** | Pinaparusahan ang source-language leakage. Inverted: 0% code-switching = 1.0. |
| `terminology_adherence` | **0.05** | Nire-reward ang coached methods na nirerespeto ang prescribed vocabulary. Active lamang kapag may coaching data. |
| `hallucination_rate` | **0.05** | Pinaparusahan ang fabricated content. Inverted: 0% hallucination = 1.0. |
| `exact_match_rate` | **0.05** | Pinakamababang weight. Masyadong strict para sa polysynthetic languages — mayroong maraming tamang salin. Pinananatili bilang ceiling check. |

> **Kabuuan: 1.00.** Kapag unavailable ang metrics, ang weights ng mga ito ay nire-redistribute nang proporsiyonal sa available metrics. Sa kasalukuyan, ang `morphological_accuracy` (0.15 weight) ang tanging Profile A metric na hindi pa kinukuwenta — nangangailangan ito ng per-entry gold-standard morphological annotations. Kapag wala ang metric na ito, ang natitirang 8 metrics (total weight 0.85) ay bawat isa na-scale ng 1/0.85 ≈ 1.176. Halimbawa:
> - FST: 0.25/0.85 = 0.294
> - chrF++: 0.15/0.85 = 0.176
> - semantic: 0.15/0.85 = 0.176

#### Profile B: Mga Wikang WALANG FST Coverage

Para sa mga wikang walang morphological validation tools. Magkapantay ang weight ng semantic at surface metrics.

| Metric | Target Weight | Rationale |
|--------|--------------|-----------|
| `semantic_score` | **0.25** | Kapag walang structural validation, meaning preservation ang pinakamalakas na available signal. |
| `chrf_plus_plus` | **0.25** | Kapag walang FST, ang character-level overlap ang nagiging primary surface check. |
| `equivalent_match_rate` | **0.15** | Nagbibigay ang variant matching ng structured quality assessment nang hindi nangangailangan ng morphological tools. |
| `exact_match_rate` | **0.10** | Kapag walang FST, mas mataas ang weight ng exact match bilang tanging structural validation proxy. |
| `code_switching_rate` | **0.10** | Mas mahalaga ang source language leakage kapag walang FST na makahuhuli ng bad output. |
| `terminology_adherence` | **0.05** | Coached vocabulary compliance. |
| `hallucination_rate` | **0.05** | Fabricated content detection. |
| `orthographic_accuracy` | **0.05** | Pinupunan ng script-specific correctness ang bahagi ng puwang na naiwan ng absent FST. |

> **Kabuuan: 1.00.** Ang `orthographic_accuracy` (0.05 weight) ay planned ngunit hindi pa kinukuwenta. Kapag wala ito, ang natitirang 7 metrics (total weight 0.95) ay na-scale ng 1/0.95 ≈ 1.053 — negligible ang epekto sa composite.

> **Tala sa weight evolution.** Provisional ang weights na ito at ire-recalibrate habang naiipon ang human validation data. Ang pangmatagalang layunin ay kunin ang weights nang empirically: aling automated metrics ang pinakamahusay na nagpe-predict ng human quality judgments para sa bawat language family?

### 4.4 Pagdaragdag ng Bagong Metric sa Composite

Upang magdagdag ng bagong metric sa composite:

1. **Tukuyin ito** sa §2 na may status na `🔲 Planned`, kasama ang scale, level, at computation method.
2. **I-implement ito** bilang MetricPlugin (o sa `tester.py` para sa core metrics).
3. **Magdagdag ng null placeholder** sa run card scores block.
4. **Mag-assign ng target weight** sa §4.3 sa pamamagitan ng pagbaba ng existing weights. Dapat mag-sum sa 1.00 ang weights.
5. **I-update ang BENCHMARK_SPEC.md** §3 kung magbabago ang run card schema.
6. **I-update ang `scoring.py`** weight tables (dapat i-mirror ng code ang dokumentong ito).
7. **Magpatakbo ng validation benchmark** upang kumpirmahing nagpo-produce ang metric ng sensible values sa tunay na data.
8. **I-update ang dokumentong ito** upang baguhin ang status mula `🔲` tungong `✅`.

---

## 5. Quality Tiers {#5-quality-tiers}

Ang tiers na ito ay heuristic labels sa automated composite scores. Inilalarawan ng mga ito kung ano ang karaniwang ibig sabihin ng scores sa praktika, batay sa human review ng outputs sa bawat level. **Hindi validated quality judgments ang mga ito** — tanging human review lamang ang makapagkukumpirma ng aktuwal na usability.

> [!IMPORTANT]
> **Provisional ang automated tiers.** Ang mga label na ito ay nominations para sa review, hindi declarations ng kalidad. Ang method na umaabot sa "Deployable" sa automated metrics ay candidate para sa community evaluation — hindi produktong dapat i-ship. Tanging human review ng bilingual speakers lamang ang makapagkukumpirma ng aktuwal na usability (tingnan ang [BENCHMARK_SPEC §7](/docs/specifications/benchmark#7-human-validation)). Walang method ang maaaring mag-claim ng Deployable o mas mataas nang walang community review na nagkukumpirma na sumasang-ayon ang speakers na usable ang output. Maaaring magkaiba ang tier boundaries sa bawat wika habang naiipon ang human validation data.

| Tier | Composite Range | Karaniwang Nakikita ng Speaker |
|------|----------------|-------------------------------|
| **Baseline** | 0.00–0.30 | Raw LLM output na walang language-specific support. Karamihan ng morphology ay hallucinated. |
| **Emerging** | 0.30–0.50 | May lumilitaw na ilang tamang patterns. Nakakatulong ang coaching, ngunit hindi reliable ang output. |
| **Functional** | 0.50–0.70 | Nakikilala ng speaker ang output. Karaniwang tama ang major grammatical categories. Madalas ang morphological errors. |
| **Deployable** | 0.70–0.85 | Angkop para sa draft translation na may human review. Karamihan ng morphology ay tama. |
| **Fluent** | 0.85–1.00 | Papalapit sa competent human translation. Bihira at minor ang errors. |

Provisional ang tiers na ito. Ire-recalibrate ang mga ito habang naiipon ang human validation data at natututuhan natin kung saan aktuwal na bumabagsak ang threshold na "nakikita ng speaker na kapaki-pakinabang ito" para sa bawat wika. Walang method ang maaaring mag-claim ng **Deployable** o mas mataas nang walang community review na nagkukumpirma na sumasang-ayon ang bilingual speakers na usable ang output.

### 5.1 Tier Thresholds (Machine-Readable)

Para sa code implementations, ang thresholds ay (evaluated top-down, first match wins):

```
composite >= 0.85  →  "fluent"
composite >= 0.70  →  "deployable"
composite >= 0.50  →  "functional"
composite >= 0.30  →  "emerging"
composite >= 0.00  →  "baseline"
composite is null  →  "unscored"
```

---

## 6. Cost Metrics

Sinusukat ng cost metrics ang financial efficiency ng isang translation method. Iniuulat ang mga ito nang hiwalay sa kalidad — hindi naiimpluwensiyahan ng cost ang composite score (maliban sa cost-adjusted secondary ranking).

### 6.1 Token Metrics

| ID | Metric | Computation |
|----|--------|-------------|
| `prompt_tokens` | Total input tokens | Sum ng `usage.prompt_tokens` sa lahat ng API calls |
| `completion_tokens` | Total output tokens | Sum ng `usage.completion_tokens` |
| `reasoning_tokens` | Chain-of-thought tokens | Sum ng `usage.completion_tokens_details.reasoning_tokens` (0 para sa karamihan ng models) |
| `cached_tokens` | Provider-cached tokens | Sum ng `usage.prompt_tokens_details.cached_tokens` |
| `total_tokens` | Total tokens consumed | `prompt_tokens + completion_tokens` |
| `tokens_per_entry` | Average tokens per translation | ✅ `total_tokens / entry_count` |

### 6.2 Cost Metrics

| ID | Metric | Computation | Use Case |
|----|--------|-------------|----------|
| `total_cost_usd` | Total run cost | Provider-reported pricing × token counts | "Magkano ang ginastos ng benchmark na ito?" |
| `cost_per_entry_usd` | Cost per corpus entry | `total_cost_usd / entry_count` | Paghahambing ng methods sa parehong corpus |
| `cost_per_1k_tokens` | Cost per 1,000 tokens | ✅ `total_cost_usd / total_tokens × 1000` | Universal LLM efficiency — comparable sa corpora |
| `cost_per_source_char` | Cost per source character | `total_cost_usd / total_source_chars` | Comparable sa mga wikang may magkakaibang tokenization |

> **Bakit maraming cost metrics?** Nag-iiba ang haba ng isang "entry" — mas mababa ang gastos ng 3-word phrase kaysa sa paragraph. Kapaki-pakinabang ang `cost_per_entry_usd` para sa paghahambing ng methods sa *parehong* corpus (parehong entries = parehong haba = patas na paghahambing). Ang `cost_per_1k_tokens` ang standard LLM efficiency metric, comparable *sa* corpora. Ino-normalize ng `cost_per_source_char` ang tokenization differences — maaaring ma-tokenize ang parehong sentence sa magkakaibang bilang ng tokens depende sa vocabulary ng model.

### 6.3 Cost-Adjusted Score

Para sa methods na gumagamit ng paid APIs, kumukuwenta kami ng secondary ranking:

```
cost_adjusted = composite / log2(1 + cost_per_entry_usd × 1000)
```

Nire-reward nito ang methods na nakakamit ang mabubuting scores nang efficient. Gumagamit ito ng `cost_per_entry_usd` (hindi per-token) dahil palaging kinukuwenta ang cost-adjusted score sa loob ng iisang benchmark (parehong corpus), kaya patas ang per-entry comparison.

Ang cost-adjusted score ay **secondary ranking** — ang primary leaderboard ay niraranggo ayon sa composite score. Sinasagot nito ang ibang tanong: "sa ibinigay na budget, aling method ang nagbibigay ng pinakamahusay na resulta?"

---

## 7. Speed Metrics

Sinusukat ng speed metrics ang latency at throughput ng isang translation method. Tulad ng cost, hindi naiimpluwensiyahan ng speed ang composite score.

| ID | Metric | Computation | Level |
|----|--------|-------------|-------|
| `elapsed_seconds` | Wall-clock run duration | `time_end - time_start` | Run |
| `avg_latency_seconds` | Mean per-entry latency | `Σ latency_s / n_entries` | Corpus |
| `median_latency_seconds` | Median per-entry latency | 50th percentile ng `latency_s` | Corpus |
| `p95_latency_seconds` | 95th percentile latency | 95th percentile ng `latency_s` | Corpus |
| `tokens_per_second` | Throughput | `total_tokens / elapsed_seconds` | Run |
| `entries_per_minute` | Translation rate | `entry_count / (elapsed_seconds / 60)` | Run |

---

## 8. Confidence at Significance

### 8.1 Bootstrap Confidence Intervals

Sinusuportahan ng lahat ng key metrics ang bootstrap confidence intervals (percentile method, n=1000 resamples, α=0.05):

| Metric | CI Reported |
|--------|------------|
| `chrf_plus_plus` | ✅ `chrf_ci_lower`, `chrf_ci_upper` |
| `exact_match_rate` | ✅ `exact_match_ci_lower`, `exact_match_ci_upper` |
| `fst_acceptance_rate` | ✅ `fst_ci_lower`, `fst_ci_upper` (kinukuwenta lamang kapag may FST data) |
| `comet_score` | ✅ `comet_ci_lower`, `comet_ci_upper` (bootstrapped mula sa cached per-entry scores — walang redundant neural inference) |
| `composite` | ✅ `composite_ci_lower`, `composite_ci_upper` (kinukuwenta kapag available ang chrF++ at exact_match) |
| per-tier CIs | ✅ `confidence_intervals_by_tier` — chrF++ at exact_match CIs kada difficulty level (Tier 1-5) |

### 8.2 Paired Bootstrap Significance Tests

Para sa paghahambing ng dalawang methods, kinukuwenta ng harness ang paired bootstrap resampling tests:

```
H₀: The two methods perform equally on this corpus.
H₁: One method is significantly better.
```

Kung ang p-value < 0.05 at hindi kasama ang zero sa confidence interval ng difference, ang difference ay statistically significant sa 95% level.

---

## 9. Run Card Scores Schema

Tinutukoy ng seksyong ito ang hierarchical structure ng `scores` block sa isang run card. Ang schema na ito ay hinango mula sa metrics na tinukoy sa §2–§7 at dapat panatilihing naka-sync.

```jsonc
{
  "scores": {
    // §2.1 Surface metrics
    "exact_match_rate":       0.6613,       // 0.0–1.0
    "exact_matches":          41,           // count
    "equivalent_match_rate":  0.7258,       // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "equivalent_matches":     45,           // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "chrf_plus_plus":         80.65,        // 0–100 (sacrebleu native scale)
    "bleu":                   54.78,        // 0–100, NOT in composite
    "ter":                    42.3,         // ✅ implemented, 0–∞ (lower=better)
    "length_ratio":           1.03,         // ✅ implemented, ideal=1.0

    // §2.2 Structural metrics
    "fst_acceptance_rate":    1.0,          // 0.0–1.0
    "fst_accepted":           74,           // count
    "morphological_accuracy": null,         // 🔲 planned
    "orthographic_accuracy":  null,         // 🔲 planned

    // §2.3 Semantic metrics
    "semantic_score":         0.6842,       // ⚡ partial (CRK: eval_standards/crk CrkSemanticMetric)
    "comet_score":            null,         // nullable, NOT in composite
    "comet_model":            "",           // model ID used for COMET

    // §2.4 Behavioral metrics
    "code_switching_rate":    0.03,         // ✅ implemented (lower=better)
    "hallucination_rate":     0.01,         // ✅ implemented (lower=better)
    "terminology_adherence":  null,         // ✅ implemented (null when no glossary)
    "consistency_score":      null,         // 🔲 planned

    // §4 Composite
    "composite":              0.8988,       // 0.0–1.0
    "quality_tier":           "fluent",     // §5 tier label
    "cost_adjusted":          null,         // §6.3 secondary ranking

    // §7 Speed metrics (merged into scores block)
    "tokens_per_second":      4462.5,       // ✅ total_tokens / elapsed
    "entries_per_minute":     82.30,        // ✅ entry_count / (elapsed/60)
    "avg_latency_seconds":    0.234,
    "median_latency_seconds": 0.190,
    "p95_latency_seconds":    0.415,

    // §8.1 Confidence intervals
    "confidence_intervals": {
      "chrf_plus_plus":     { "ci_lower": 78.2, "ci_upper": 83.1 },
      "exact_match_rate":   { "ci_lower": 0.54, "ci_upper": 0.78 },
      "corpus_comet":       { "ci_lower": 0.71, "ci_upper": 0.76 }
    },
    "confidence_intervals_by_tier": {
      "1": { "corpus_chrf": { "ci_lower": 68.1, "ci_upper": 76.5 } },
      "3": { "corpus_chrf": { "ci_lower": 36.2, "ci_upper": 47.0 } }
    },

    // Breakdowns
    "by_difficulty":          {},           // scores grouped by difficulty tier
    "by_provenance":          {},           // scores grouped by entry provenance

    // Counts
    "total":                  62,
    "evaluated":              62,
    "errors":                 0
  },

  "totals": {
    // §6.1 Token metrics
    "prompt_tokens":          13985,
    "completion_tokens":      187822,
    "reasoning_tokens":       175726,
    "cached_tokens":          0,
    // §6.2 Cost metrics
    "total_cost_usd":         1.7114,
    "cost_per_entry_usd":     0.027603,
    "cost_per_source_char":   null          // 🔲 needs source char counting
  }
}
```

> **Schema history.** Nagmungkahi ang mga naunang spec drafts ng magkakahiwalay na `cost`, `speed`, at `tokens` blocks. Pinagsama ang mga ito sa `scores` at `totals` ayon sa pagkakabanggit para sa simplicity. Ang speed metrics (`tokens_per_second`, `entries_per_minute`, latencies) ay nasa `scores`; ang token counts at cost figures ay nasa `totals`.

### 9.1 Schema–Database Mapping

Ang run card JSON ay buong ini-store bilang `jsonb` column sa Supabase. Ang key metrics ay dine-denormalize din sa top-level columns para sa sort/filter performance:

| Run Card Field | Supabase Column | Type | Index |
|---------------|----------------|------|-------|
| `scores.composite` | `composite_score` | `real` | `idx_composite` |
| `scores.quality_tier` | `quality_tier` | `text` | — |
| `scores.chrf_plus_plus` | `chrf_plus_plus` | `real` | `idx_leaderboard` |
| `scores.exact_match_rate` | `exact_match_rate` | `real` | — |
| `scores.fst_acceptance_rate` | `fst_acceptance_rate` | `real` | — |
| `scores.bleu` | `corpus_bleu` | `real` | — |
| `scores.comet_score` | `comet_score` | `real` | — |
| `totals.total_cost_usd` | `total_cost_usd` | `real` | — |
| `totals.cost_per_entry_usd` | `cost_per_entry_usd` | `real` | — |
| `totals.cost_per_source_char` | `cost_per_source_char` | `real` | — |
| `scores.avg_latency_seconds` | `avg_latency_seconds` | `real` | — |
| `model_slug` | `model_slug` | `text` | `idx_model` |
| `condition` | `condition` | `text` | — |
| `dataset.id` | `dataset_id` | `text` | `idx_leaderboard` |
| `dataset.language_pair` | `language_pair` | `text` | — |
| `fingerprint.hash` | `fingerprint_hash` | `text` | `idx_fingerprint` |
| `scores.equivalent_match_rate` | `equivalent_match_rate` | `real` | — |
| `scores.semantic_score` | `semantic_score` | `real` | — |
| `scores.ter` | `ter` | `real` | — |
| `scores.length_ratio` | `length_ratio` | `real` | — |
| `scores.code_switching_rate` | `code_switching_rate` | `real` | — |
| `scores.hallucination_rate` | `hallucination_rate` | `real` | — |
| `scores.terminology_adherence` | `terminology_adherence` | `real` | — |
| `scores.tokens_per_second` | `tokens_per_second` | `real` | — |
| `scores.entries_per_minute` | `entries_per_minute` | `real` | — |
| `elapsed_seconds` | `elapsed_seconds` | `real` | — |
| *(full card)* | `run_card` | `jsonb` | — |

Kapag na-implement ang bagong metrics, dapat idagdag ang corresponding column sa pamamagitan ng numbered migration sa `arena/migrations/`.

---

## 10. Code–Spec Synchronization

### 10.1 Canonical Source

Ang dokumentong ito (`arena/website/docs/specifications/scoring.md`) ang canonical source para sa:
- Metric definitions (§2)
- Composite weight tables (§4.3)
- Quality tier thresholds (§5.1)
- Cost metric formulas (§6.2)
- Run card scores schema (§9)

### 10.2 Code Mirror

Ang file na `arena/mt_eval_harness/scoring.py` ay nagmi-mirror ng weight tables at tier thresholds mula sa dokumentong ito. Ito ang **code implementation** ng §4.3 at §5.1. Kapag na-update ang dokumentong ito:

1. I-update ang `scoring.py` upang tumugma
2. Patakbuhin ang `pytest tests/test_scoring_ssot.py` upang i-validate ang alignment
3. I-update ang FAQ at website docs na nagsu-summarize ng weights

### 10.3 Mga Dokumentong Tumutukoy sa Spec na Ito

| Document | Ano ang Tinutukoy Nito | Paano Panatilihing Naka-sync |
|----------|-------------------|---------------------|
| `arena/website/docs/specifications/benchmark-spec.md` §4–§5 | Composite formula, weight tables, tier thresholds | I-cross-reference ang doc na ito; huwag i-duplicate ang tables |
| `website/docs/getting-started/faq.md` | Simplified weight summary | Dapat tumugma sa §4.3; mag-link pabalik sa doc na ito |
| `arena/website/docs/how-it-works.md` | Deployable threshold | Dapat tumugma sa §5 |
| `publish.py` sa pamamagitan ng `scoring.py` | Weight dicts + tier function | Automated test ang nagva-validate ng tugma |

---

## Appendix A: Metrics na WALA sa Composite (at Bakit)

| Metric | Bakit Hindi Kasama |
|--------|-------------|
| **BLEU** | Pinaparusahan ng word-level scoring ang morphological variation sa polysynthetic languages. Ang minor inflectional difference (tamang kahulugan, bahagyang ibang suffix) ay binibilang bilang complete miss. Mas mahusay itong hinahawakan ng chrF++ sa character level. |
| **COMET** | Trained sa WMT data (high-resource European pairs). Hindi maaasahan ang scores para sa LRLs — nag-e-extrapolate ang model mula sa mga wikang may ibang morphological systems. Iniuulat para sa transparency, hindi para sa scoring. |
| **TER** | May correlation ang edit distance sa chrF++ para sa karamihan ng use cases. Ang pagsasama sa pareho ay magdodoble ng bilang ng surface similarity. Iniuulat ang TER para sa reference. |
| **Length Ratio** | Diagnostic ito, hindi quality signal. Parehong maayos ang ratio na 1.02 at ratio na 0.98. Extreme values lamang ang nagpapahiwatig ng problema. |
| **Consistency Score** | Corpus-level lamang — walang per-entry value na maa-aggregate. Gayundin, lehitimo ang ilang inconsistency (parehong English word → ibang target-language translations depende sa context). |
| **Compliance Index** | Quality gate, hindi quality signal. Sinusukat ang structural preservation (placeholders, quotes), hindi translation accuracy. |

## Appendix B: LYSS — Language-Specific Metric Implementations

Ang **LYSS** framework (Linguistically-informed Yield & Structural Scoring) ay nagbibigay ng language-specific metrics na lumalagpas sa surface-level string comparison. May tatlong core components ang LYSS:

- **LYSS-fst** — Morphological validity (`fst_acceptance_rate`): Valid form ba sa target language ang bawat salita?
- **LYSS-eq** — Linguistic equivalence (`equivalent_match_rate`): Acceptable variant ba ng reference ang output?
- **LYSS-sem** — Semantic validation (`semantic_score`): Napapanatili ba ng output ang source meaning?

> **Validation status: 🔶 Engineering heuristic.** HINDI pa na-validate ang LYSS metrics laban sa human quality judgments. Idinisenyo ang mga ito mula sa linguistic principles (FSTs, dictionaries, grammar rules na binuo ng linguists sa UAlberta ALTLab), ngunit hindi pa nasusukat ang correlation sa pagitan ng LYSS scores at aktuwal na translation quality. Tingnan ang [Speaker Validation Protocol](/docs/specifications/speaker-validation) para sa kinakailangang validation experiments.

| Language | Plugin | Location | LYSS Component | Metric Key | Notes |
|----------|--------|----------|----------------|------------|-------|
| CRK (Plains Cree) | `CrkLinterMetric` | `eval_standards/crk/metrics.py` | **LYSS-eq** | `equivalent_match_rate` | Deterministic variant-class rules: word order, orthographic, optional particle, lemma synonym, progressive ambiguity, inclusive/exclusive. Nagpo-produce ng per-entry `lint_verdict` (EXACT/EQUIVALENT/MISS/NO_OUTPUT). |
| CRK | `CrkSemanticMetric` | `eval_standards/crk/metrics.py` | **LYSS-sem** | `semantic_score` | Deterministic: FST lemma extraction + dictionary glosses + spaCy content-word overlap. Nagpo-produce ng verdicts (EXACT_MATCH/VALID/GRAMMAR_ISSUES/PARTIAL/INCOMPLETE/WRONG/NO_OUTPUT). |
| GiellaLT langs | `GiellaLTFSTMetric` | `plugins/giellalt_fst.py` | **LYSS-fst** | `fst_acceptance_rate` | Generic: gumagana para sa CRK, SME, SMA, SMJ, SMN, SMS, FIN, NOB, IKU — anumang wika na may `.hfstol` analyzer. |

> **Architecture note (Hunyo 2026).** Idinedeklara na ngayon ang language-specific LYSS metrics sa language card sa ilalim ng `evalMetrics` at nilo-load mula sa `eval_standards/<lang>/` ng `plugin_discovery.py`. Ang mga ito ay **evaluation standards** (referee), hindi method plugin metrics (contestant). Ibig sabihin nito, anumang translation method na nagta-target sa CRK ay awtomatikong sine-score ng LYSS — walang kinakailangang method-specific configuration. Inalis ang `CrkFSTMetric`; ang functionality nito ay ganap nang sakop ng generic `GiellaLTFSTMetric`.

## Appendix C: Metrics na Isinasaalang-alang

Ito ang mga ideyang sinusuri ngunit hindi pa sapat na naispesipika para sa §2:

| Idea | Ano ang Susukatin Nito | Blockers |
|------|----------------------|----------|
| Fluency (LM perplexity) | Well-formed prose ba ang output sa target language? | Nangangailangan ng target-language LM. Walang magagandang models para sa karamihan ng LRLs. |
| Register match | Tumutugma ba ang salin sa inaasahang formality level? | Nangangailangan ng sociolinguistic classifiers. Research problem. |
| Cultural appropriateness | Tama bang nahahawakan ang cultural references? | Hindi maaaring i-automate — likas na nangangailangan ng human review. |
| Discourse coherence | Bumubuo ba ng coherent passage ang magkakasunod na translations? | Nangangailangan ng document-level evaluation, hindi sentence-level. |

---

## References

Academic papers, tools, at language resources na binanggit sa buong espesipikasyong ito.

### Surface Metrics

1. Popović, M. (2017). "chrF++: words helping character n-grams." *Proceedings of the Second Conference on Machine Translation (WMT 2017)*, pp. 612–618. Copenhagen, Denmark.

2. Papineni, K., Roukos, S., Ward, T., & Zhu, W.-J. (2002). "BLEU: a method for automatic evaluation of machine translation." *Proceedings of the 40th Annual Meeting of the Association for Computational Linguistics (ACL 2002)*, pp. 311–318. Philadelphia, PA.

3. Post, M. (2018). "A Call for Clarity in Reporting BLEU Scores." *Proceedings of the Third Conference on Machine Translation (WMT 2018)*, pp. 186–191. Belgium, Brussels. Reference implementation: [sacrebleu](https://github.com/mjpost/sacrebleu).

4. Snover, M., Dorr, B., Schwartz, R., Micciulla, L., & Makhoul, J. (2006). "A Study of Translation Edit Rate with Targeted Human Annotation." *Proceedings of the 7th Conference of the Association for Machine Translation in the Americas (AMTA 2006)*, pp. 223–231. Cambridge, MA.

### Neural Metrics

5. Rei, R., Stewart, C., Farinha, A. C., & Lavie, A. (2020). "COMET: A Neural Framework for MT Evaluation." *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP 2020)*, pp. 2685–2702. Online.

6. Juraska, J., Finkelstein, M., Deutsch, D., Siddhant, A., Miber, D., & Markl, A. (2023). "MetricX-23: The Google Submission to the WMT 2023 Metrics Shared Task." *Proceedings of the Eighth Conference on Machine Translation (WMT 2023)*. Singapore.

7. Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2020). "BERTScore: Evaluating Text Generation with BERT." *Proceedings of the Eighth International Conference on Learning Representations (ICLR 2020)*. Addis Ababa, Ethiopia.

8. Sellam, T., Das, D., & Parikh, A. (2020). "BLEURT: Learning Robust Metrics for Text Generation." *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020)*, pp. 7881–7892. Online.

### Morphological and Linguistic Tools

9. Lindén, K., Silfverberg, M., Axelson, E., Hardwick, S., & Pirinen, T. (2011). "HFST—Framework for Compiling and Applying Morphologies." *Systems and Frameworks for Computational Morphology (SFCM 2011)*, Communications in Computer and Information Science, vol. 100, pp. 67–85. Springer, Berlin, Heidelberg.

10. Sánchez-Cartagena, V. M., & Toral, A. (2024). "MorphEval: Automatic Evaluation of Morphological Capabilities of Machine Translation Systems." *Machine Translation*, vol. 38, pp. 1–28.

### Error Classification and Diagnostic Evaluation

11. Popović, M. (2011). "Hjerson: An Open Source Tool for Automatic Error Classification of Machine Translation Output." *The Prague Bulletin of Mathematical Linguistics*, no. 96, pp. 59–68.

12. Dreyer, M. & Marcu, D. (2012). "HyTER: Meaning-Equivalent Semantics for Translation Evaluation." *Proceedings of the 2012 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2012)*, pp. 162–171. Montréal, Canada.

13. Reiter, E. & Belz, A. (2009). "An Investigation into the Validity of Some Metrics for Automatically Evaluating Natural Language Generation Systems." *Computational Linguistics*, vol. 35, no. 4, pp. 529–558. (Related work sa feature-based evaluation metrics, kabilang ang FUSE.)

### Hallucination Detection

14. Raunak, V., Menezes, A., & Junczys-Dowmunt, M. (2021). "The Curious Case of Hallucinations in Neural Machine Translation." *Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2021)*, pp. 1172–1183. Online.

15. Guerreiro, N. M., Voita, E., & Martins, A. F. T. (2023). "Looking for a Needle in a Haystack: A Comprehensive Study of Hallucinations in Neural Machine Translation." *Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2023)*, pp. 1059–1075. Dubrovnik, Croatia.

### Cree Language Resources

16. Wolfart, H. C. (1973). "Plains Cree: A Grammatical Study." *Transactions of the American Philosophical Society*, vol. 63, no. 5, pp. 1–90.

17. Wolvengrey, A. (2001). *nêhiyawêwin: itwêwina / Cree: Words.* Canadian Plains Research Center, University of Regina.

### Data Governance

18. First Nations Information Governance Centre. "The First Nations Principles of OCAP®." [https://fnigc.ca/ocap-training/](https://fnigc.ca/ocap-training/). (Ang OCAP® ay registered trademark ng First Nations Information Governance Centre.)

19. Carroll, S. R., Garba, I., Figueroa-Rodríguez, O. L., Holbrook, J., Lovett, R., Materechera, S., Parsons, M., Raseroka, K., Rodriguez-Lonebear, D., Rowe, R., Sara, R., Walker, J. D., Anderson, J., & Hudson, M. (2020). "The CARE Principles for Indigenous Data Governance." *Data Science Journal*, vol. 19, no. 1, p. 43.