---
sidebar_position: 6
title: "Espesipikasyon ng Benchmark"
slug: '/specifications/benchmark'
related:
  - label: "Corpus Design Framework"
    to: /docs/specifications/corpus-design
    kind: spec
  - label: "Evaluation Datasets"
    to: /docs/leaderboard/datasets
    kind: doc
    note: "The corpora currently in play"
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
  - label: "Speaker Validation Protocol"
    to: /docs/specifications/speaker-validation
    kind: spec
---
# Espesipikasyon ng Benchmark

> **Ehekutibong Buod.** Tinutukoy ng dokumentong ito ang protocol ng pagsusuri para sa Champollion MT evaluation ecosystem: format ng corpus (§2), schema ng run card (§3), protocol ng benchmark (§6), mga kinakailangan sa human validation (§7), mga mekanismo ng sovereignty (§8), leaderboard at modelo ng submission (§9), framework ng gastos (§10), at extensibility sa mga bagong wika (§11). Para sa mga depinisyon ng metric, composite scoring weights, quality tier thresholds, at mga formula ng cost/speed metric, tingnan ang `SCORING_SPEC.md` — ang nag-iisang source of truth para sa lahat ng scoring logic. Tinutukoy ng dokumentong ito ang SCORING_SPEC para sa mga detalyeng iyon sa halip na duplikahin ang mga ito.
>
> Huling na-update: 2026-06-07

---

## 1. Mga Prinsipyo

### 1.1 Ang Automated Metrics ay mga Proxy

Bawat metric na tinukoy sa dokumentong ito ay kinakalkula ng makina. chrF++, FST acceptance, morphological accuracy, semantic similarity — lahat ng ito ay mga automated proxy para sa kalidad ng pagsasalin. Kapaki-pakinabang ang mga ito para sa mabilis na iteration, sistematikong paghahambing, at pagtukoy ng mga regression. **Hindi sila pamalit sa human judgment**.

Ang hierarchy ng pagsusuri:

```
Automated metrics (run cards, benchmarks)
    ↓ proxy for
Human review (bilingual speakers validate output)
    ↓ proxy for
Actual utility (does this help a language community?)
```

Walang automated score, gaano man kataas, ang makapapalit sa isang fluent speaker na binabasa ang output at kinukumpirmang ito ay tama, natural, at angkop sa kultura. Ang mga quality tier na tinukoy sa §5 ay mga heuristic label sa mga automated composite score — kapaki-pakinabang para sa pagsubaybay ng progreso, ngunit hindi kailanman sapat nang mag-isa.

### 1.2 Mga Method, Hindi Mga Model

Ibine-benchmark namin ang **mga method**, hindi ang mga model. Ang model ay isang component lamang. Ang method ay ang buong recipe: pagpili ng model, disenyo ng prompt, paggamit ng tool, pre/post-processing, coaching data, mga retry strategy, lahat. Dalawang team na gumagamit ng parehong model ngunit may magkaibang method ay magkakaroon ng magkaibang score. Iyon ang punto.

### 1.3 Reproducibility

Dapat na reproducible ang bawat resulta ng benchmark. Kinukuha ng run card (§3) ang kumpletong configuration ng isang eksperimento. Tinutukoy ng fingerprint (§3.5) ang experimental setup. Bine-verify ng run card hash (§3.6) ang integridad ng resulta. Sinumang may parehong method, corpus, at configuration ay dapat makamit ang mga score sa loob ng ±2% (isinasaalang-alang ang LLM sampling non-determinism sa temperature > 0).

### 1.4 Walang Synthetic Evaluation Data

**Ang proyektong ito ay hindi gumagawa, gumagamit, o nag-eendorso ng synthetic evaluation data.** Ang lahat ng corpora ay dapat kunin mula sa tunay na human-authored text — mga nailathalang pagsasalin, textbook, bilingual document, o elicited translations mula sa mga fluent speaker.

Maaaring tumulong ang LLMs sa:
- Sentence alignment (paghahanap ng parallel passages sa umiiral na bilingual texts)
- Format conversion (pag-convert ng mga nailathalang materyal sa corpus schema)
- Metadata enrichment (pagmumungkahi ng difficulty tiers, register labels)
- Pagmumungkahi ng source sentences para sa human translation (§11.3 — ang hakbang ng pagsasalin ay palaging ginagawa ng tao)

Hindi dapat **kailanman** gumawa ang LLMs ng reference translations o evaluation pairs.

**Development-neutral kami tungkol sa training data.** Kung gumagamit ang isang method developer ng synthetic training data, backtranslation, o data augmentation sa kanilang method, iyon ay kanilang pagpili — sinusuri namin ang output, hindi ang training process. Gumagamit ang Meta's OMT-1600 ng humigit-kumulang 270 milyong synthetic parallel sentences na ginawa sa pamamagitan ng backtranslation. Wala kaming pagtutol sa mga method na sinanay sa ganitong paraan. Sinusubok namin sa human curation lamang.

> **Bakit hindi Bible text para sa pagsusuri?** Sinusuri ng OMT-1600 ang 1,560 sa 1,600 wika sa Bible-domain text. Ang mga pagsasalin ng Bibliya ay may archaic register, liturgical vocabulary, at formulaic sentence structure. Ang aming evaluation corpora ay kinukuha mula sa community-curated, domain-diverse text — mga domain na health, legal, educational, governmental, conversational, at technical (tingnan ang §2.7). Ito ay sinadyang design choice. Kailangan ng mga komunidad ng pagsasalin para sa mga domain kung saan sila aktuwal na nabubuhay at nagtatrabaho, hindi iisang religious register. Ang method na may mataas na score sa Genesis 1:1 ay halos walang sinasabi tungkol sa performance nito sa agenda ng band council o clinic intake form.

---

## 2. Corpus Schema

Ang corpus ay curated set ng parallel text pairs na may structured metadata. Ito ang ground truth kung saan sinusukat ang lahat ng method.

### 2.1 Dataset Envelope

Ang top-level structure ng corpus file:

```json
{
  "dataset": {
    "id": "edtekla-dev-v1",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "source_language": "en",
    "target_language": "crk",
    "created": "2026-05-01",
    "license": "CC-BY-NC-SA-4.0",
    "provenance": ["gold_standard", "textbook"]
  },
  "entries": [ ... ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Natatanging dataset identifier, ginagamit sa run cards at leaderboard |
| `version` | string | ✅ | Semantic version. Ang incrementing ay nag-i-invalidate ng mga naunang paghahambing ng run card |
| `language_pair` | string | ✅ | Display label (hal., `EN→CRK`) |
| `source_language` | string | ✅ | BCP 47 source language code |
| `target_language` | string | ✅ | BCP 47 target language code |
| `created` | string | ✅ | ISO 8601 creation date |
| `license` | string | ✅ | SPDX license identifier |
| `provenance` | string[] | ✅ | Listahan ng provenance tags na ginagamit sa lahat ng entries |

### 2.2 Entry Schema

Ang bawat entry sa corpus ay kumakatawan sa isang translation challenge:

```json
{
  "id": 42,
  "source": "I see the dog",
  "reference": "niwâpamâw atim",
  "segment": "gold_standard",
  "difficulty": 2,
  "provenance": "gold_standard",
  "register": "conversational",
  "context": "declaration",
  "morphological_analysis": "ni-wâpam-âw atim | 1sg-see.TA-3sg.DIR dog.AN",
  "notes": "Animate noun (atim); direct form because speaker is proximate",
  "variant_class": "simple-ta-direct"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | ✅ | Natatanging identifier sa loob ng corpus |
| `source` | string | ✅ | Source text sa source language |
| `reference` | string | ✅ | Gold-standard reference translation sa target language |
| `segment` | string | 📎 | Corpus partition: `gold_standard`, `held_out`, `development`, o `diagnostic` |
| `difficulty` | integer | 📎 | Difficulty rating 1–5 (tingnan ang §2.4) |
| `provenance` | string | 📎 | Pinagmulan ng entry na ito (tingnan ang §2.5) |
| `register` | string | 📎 | Antas ng register/formality (tingnan ang §2.6) |
| `context` | string | 📎 | Communicative function (tingnan ang §2.6) |
| `domain` | string | 📎 | Use-case domain mula sa 16-code taxonomy (tingnan ang §2.7). Dapat isa sa: `conv`, `ecommerce`, `edu`, `financial`, `gov`, `legal`, `literary`, `marketing`, `medical`, `news`, `religious`, `scientific`, `subtitles`, `support`, `tech`, `ui`. Vine-validate sa construction time. |

> **📎 = RECOMMENDED.** Graceful na hinahawakan ng harness ang nawawalang optional fields sa pamamagitan ng defaults. Kailangan lamang magbigay ang third-party corpora ng `id`, `source`, at `reference` kada entry.
| `morphological_analysis` | string | ❌ | Gold-standard morphological breakdown |
| `notes` | string | ❌ | Translator notes, dialectal variants, ambiguity flags |
| `variant_class` | string | ❌ | Class label na nagpapangkat ng katanggap-tanggap na translation variants |


### 2.3 Mga Segment ng Corpus

Hinahati ang corpus sa mga segment na may magkakaibang antas ng access:

| Segment | Purpose | Access | Minimum Size |
|---------|---------|--------|-------------|
| `development` | Pag-develop at iteration ng method. Malayang ginagamit ito ng mga developer. | **Public** | 30 entries |
| `diagnostic` | Targeted tests para sa mga partikular na linguistic phenomena. | **Public** | 10 entries |
| `gold_standard` | Opisyal na benchmark evaluation. Dito nagmumula ang leaderboard scores. | **Secret** — hawak ng governance org | 50 entries |
| `held_out` | Nakareserba para sa future evaluation. Hindi kailanman gagamitin hanggang ma-activate. | **Secret** — hawak ng governance org | 10 entries |

> **Kasalukuyang estado:** Tanging ang `development` segment ang umiiral sa shipped datasets. Ang mga segment na `diagnostic`, `gold_standard`, at `held_out` ay tinukoy para sa paggamit sa hinaharap habang lumalaki ang corpora.

Ganap na secret ang mga segment na `gold_standard` at `held_out`. Parehong ang source sentences at ang reference translations ay hawak sa governance-controlled infrastructure. Hindi kailanman nakikita ng mga method developer ang mga tanong o ang mga sagot. Tingnan ang §8 para sa sovereignty mechanism.

### 2.4 Difficulty Tiers

| Tier | Description | Examples |
|------|-------------|----------|
| 1 — Basic vocabulary | Mga iisang salita, karaniwang pagbati, numero | "hello" → "tânisi", "dog" → "atim" |
| 2 — Simple sentences | Subject-verb o SVO, present tense | "I see the dog" → "niwâpamâw atim" |
| 3 — Moderate complexity | Past/future tense, possessives, animacy | "I saw his dog yesterday" |
| 4 — Complex morphology | Obviation, passive voice, conjunct order, relative clauses | "the woman whose son went to the store" |
| 5 — Advanced | Multi-clause, formal register, ceremonial, idiomatic | Buong paragraph na may register-appropriate tone |

Ang mahusay na pagkakabuo ng corpus ay dapat may entries sa lahat ng limang difficulty tiers, na mas binibigyang-timbang ang tiers 2–4 kung saan nakapaloob ang karamihan ng real-world translation challenges.

### 2.5 Provenance Tags

Dapat ipahiwatig ng bawat entry ang pinagmulan nito:

| Tag | Meaning |
|-----|---------|
| `gold_standard` | Na-verify ng mga fluent speaker |
| `textbook` | Mula sa nailathalang educational materials |
| `elicited` | Ginawa sa pamamagitan ng structured elicitation sessions |
| `corpus` | Kinuha mula sa parallel corpus |

> **Tala:** Sa praktika, ang provenance values ay free-form strings. Ang mga tag sa itaas ay mga convention, hindi validated enum — maaaring gumamit ang datasets ng iba pang descriptive provenance strings.

### 2.6 Register at Context

Inilalarawan ng **Register** ang formality at social context:

| Register | Description |
|----------|-------------|
| `conversational` | Pang-araw-araw na pananalita sa pagitan ng magkakapantay |
| `formal` | Opisyal o institutional na wika |
| `technical` | Domain-specific vocabulary |
| `ceremonial` | Tradisyonal o sacred na paggamit ng wika |
| `educational` | Mga materyal sa pagtuturo ng wika |

Inilalarawan ng **Context** ang communicative function:

> 🔲 **Planned.** Ang field na `context` ay tinukoy sa schema ngunit hindi pa pinupunan sa kasalukuyang datasets. Nakareserba ito para sa future corpus enrichment.

| Context | Description |
|---------|-------------|
| `greeting` | Social greeting o pamamaalam |
| `declaration` | Pahayag ng katotohanan |
| `question` | Interrogative |
| `instruction` | Utos o directive |
| `narrative` | Pagkukuwento o paglalarawan |
| `label` | UI label, button text, o heading |
| `error` | Error message o warning |

### 2.7 Domain {#27-domain}

Inilalarawan ng **Domain** ang real-world use case — ang uri ng content na isinasalin. Orthogonal ito sa register at context:

- Sinasagot ng **Register**: *Gaano ito ka-formal?*
- Sinasagot ng **Context**: *Ano ang ginagawa ng pangungusap na ito?*
- Sinasagot ng **Domain**: *Para sa anong industriya/use case ito?*

Ang legal contract (domain: `legal`) ay maaaring formal (register: `formal`) at naglalaman ng declaration (context: `declaration`). Ang legal chatbot transcript (domain: `legal`) ay maaaring conversational (register: `conversational`) at naglalaman ng mga tanong (context: `question`). Parehong domain, magkaibang register at context.

| Domain Code | Description | Typical Consumers |
|-------------|-------------|-------------------|
| `ui` | Software interface strings | App developers, localization teams |
| `legal` | Contracts, statutes, court filings, immigration documents | Law firms, courts, compliance teams, IP lawyers |
| `medical` | Clinical notes, drug labels, patient communications, trial protocols | Hospitals, pharma, clinical trials, patient portals |
| `financial` | Banking, insurance, regulatory filings, audit reports | Banks, insurers, regulators, auditors |
| `edu` | Textbooks, curricula, lesson plans, academic materials | Schools, universities, textbook publishers |
| `ecommerce` | Product descriptions, reviews, marketplace listings | Online retailers, marketplace sellers |
| `marketing` | Ad copy, brand messaging, campaigns, slogans | Ad agencies, brand teams |
| `gov` | Policy documents, regulations, public notices, legislation | Government agencies, compliance teams |
| `scientific` | Research papers, abstracts, methodology, grant proposals | Researchers, journals, grant agencies |
| `religious` | Scripture, liturgical texts, theological commentary | Faith communities, liturgical publishers |
| `support` | FAQs, error messages, troubleshooting guides, chatbot scripts | SaaS companies, help desks |
| `subtitles` | Film, TV, streaming, at gaming dialogue | Streaming platforms, studios, gaming companies |
| `news` | Journalism, wire reports, editorial, press releases | Media organizations, wire services |
| `literary` | Fiction, poetry, narrative, cultural texts | Publishers, cultural preservation orgs |
| `conv` | Informal conversation, social media, messaging | Consumer apps, social platforms |
| `tech` | API docs, manuals, engineering specifications, technical guides | Documentation teams, engineering orgs |

> **Domain-specific benchmarks.** Sinusuri ng general benchmark ang isang method sa lahat ng domain. Ngunit sinusuportahan din ng Arena ang **domain-filtered benchmarks** — kung saan kinakalkula ang mga score lamang sa entries na naka-tag sa partikular na domain. Nagbibigay-daan ito sa mga user na sagutin: "Aling method ang pinakamainam para sa pagsasalin ng legal documents sa French?" kumpara sa "Aling method ang may pinakamainam na overall French score?"
>
> Ang domain-filtered leaderboard rankings ay mahalagang product feature. Mag-iiba ang performance ng magkakaibang method sa bawat domain — ang method na fine-tuned sa legal terminology ay maaaring mangibabaw sa legal benchmarks ngunit mag-underperform sa conversational text. Tinutulungan ng Arena ang mga user na mahanap ang solusyong pinakamainam para sa kanilang partikular na use case.

> **Hinaharap: Arena Chatbot.** Magkakaroon ang Arena website ng conversational assistant na tumutulong sa mga user na ilarawan ang kanilang MT use case (domain, language pair, quality requirements) at magrerekomenda ng pinakamahusay na community-validated method mula sa leaderboard. Halimbawa: "Kailangan kong isalin ang clinical trial protocols mula English papuntang Japanese — aling method ang may pinakamataas na score sa medical-domain EN→JA benchmarks?" Nakasalalay ito sa pagkakaroon ng sapat na domain-tagged evaluation data at method diversity.

---

## 3. Run Card Schema {#3-run-card-schema}

Ang run card ang atomic unit ng pagsusuri. Isa itong self-contained JSON document na nagtatala ng kumpletong configuration at mga resulta ng isang evaluation run: isang method, isang model, isang configuration, isang dataset.

Kinukuha ng bawat run card ang tatlong dimensyon:
- **Quality** — gaano kahusay ang mga pagsasalin?
- **Cost** — magkano ang ginastos upang gawin ang mga ito?
- **Speed** — gaano katagal ang inabot?

### 3.1 Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string | UUID v4 na ginawa sa simula ng run |
| `harness_version` | string | Semantic version ng harness (hal., `2.0`) |
| `timestamp` | string | ISO 8601 UTC timestamp noong nagsimula ang run |
| `elapsed_seconds` | number | Wall-clock duration ng buong run |

### 3.2 Method Configuration

Tinutukoy ng fields na ito ang experimental setup — ano ang sinubok at paano.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model_slug` | string | ✅ | Model identifier (hal., `google/gemini-2.5-flash`) |
| `model_id` | string | ❌ | Resolved model identifier na ibinalik ng API |
| `condition` | string | ✅ | Experiment label (hal., `baseline`, `coached-v3`, `few-shot`) |
| `temperature` | number | ✅ | Sampling temperature |
| `system_prompt_sha256` | string | ✅ | SHA-256 hash ng buong system prompt |
| `system_prompt_used` | string | ✅ | Ang buong system prompt text |
| `coaching_data_sha256` | string | ❌ | SHA-256 hash ng coaching data file, kung ginamit |
| `fst_version` | string | ❌ | Version ng FST analyzer, kung ginamit |
| `tools_enabled` | string[] | ❌ | Listahan ng tools na available sa method |
| `batch_size` | number | ❌ | Entries kada concurrent API batch |
| `max_retries` | number | ❌ | Maximum retries para sa FST rejection, kung naaangkop |

:::info Ang Published Run Cards ay May method_config
Kapag na-publish ang run card sa leaderboard (sa pamamagitan ng `mt-eval publish`), kasama rin dito ang isang `method_config` block na naglalaman ng canonical 8-field MethodConfig (`model`, `temperature`, `batchSize`, `register`, `coachingFile`, `coachingPrompt`, `promptContext`, `qualityTier` — lahat ay camelCase). Nagbibigay-daan ito sa zero-reconstruction import: direktang binabasa ng `champollion leaderboard --install` ang `method_config` at isinusulat ito bilang plugin manifest. Itinatala ng telemetry fields sa itaas (§3.2) kung ano ang naobserbahan ng harness; itinatala ng `method_config` kung ano ang nilayon ng developer.
:::

### 3.3 Dataset Reference

| Field | Type | Description |
|-------|------|-------------|
| `dataset.id` | string | Dataset identifier |
| `dataset.version` | string | Dataset version |
| `dataset.language_pair` | string | Display label |
| `dataset.sha256` | string | SHA-256 hash ng mga nilalaman ng dataset file |
| `dataset.entry_count` | number | Bilang ng entries na sinuri |

Itinatali ng dataset SHA-256 ang resulta sa partikular na version ng data. Kung magbabago ang dataset, hindi na comparable ang lumang run cards.

### 3.4 Scores (Quality)

Aggregate metrics para sa buong run. Ang lahat ng quality metrics ay **automated** — tingnan ang §1.1.

| Field | Type | Description |
|-------|------|-------------|
| `scores.total` | number | Kabuuang entries na sinuri |
| `scores.exact_matches` | number | Entries kung saan eksaktong tumugma ang output sa reference |
| `scores.exact_match_rate` | number | 0.0–1.0 |
| `scores.equivalent_matches` | number | Entries na tumutugma sa acceptable variant |
| `scores.equivalent_match_rate` | number | 0.0–1.0 |
| `scores.fst_accepted` | number | Entries na tinanggap ng FST analyzer |
| `scores.fst_acceptance_rate` | number | 0.0–1.0, `null` kung walang FST na naka-configure |
| `scores.morphological_accuracy` | number | 0.0–1.0, `null` kung walang gold-standard analysis |
| `scores.chrf_plus_plus` | number | Corpus-level chrF++ score (0–100) |
| `scores.semantic_score` | number | Embedding-based semantic similarity (0.0–1.0) |
| `scores.ter` | number | Translation Edit Rate (0–∞, mas mababa ay mas mahusay) |
| `scores.length_ratio` | number | avg(len(predicted)/len(reference)), ideal = 1.0 |
| `scores.code_switching_rate` | number | 0.0–1.0, fraction ng entries na may source-language leakage |
| `scores.hallucination_rate` | number | 0.0–1.0, fraction ng entries na may hallucinated content |
| `scores.terminology_adherence` | number | 0.0–1.0, pagsunod sa glossary terms (`null` kung walang glossary) |
| `scores.tokens_per_second` | number | total_tokens / elapsed_seconds |
| `scores.entries_per_minute` | number | entries na naisalin kada minuto |
| `scores.composite` | number | Weighted composite score (0.0–1.0). Tingnan ang SCORING_SPEC §4 |
| `scores.errors` | number | Entries na nabigo (API error, timeout, atbp.) |
| `scores.by_difficulty` | object | Scores na hinati ayon sa difficulty tier |
| `scores.by_provenance` | object | Scores na hinati ayon sa provenance tag |
| `scores.by_domain` | object | ✅ Implemented — Scores na hinati ayon sa domain (§2.7). Nagbibigay-daan sa domain-filtered leaderboard ranking. Kinakalkula ng tester.py at ipinapasa sa publish.py. |

### 3.5 Totals (Cost)

| Field | Type | Description |
|-------|------|-------------|
| `totals.prompt_tokens` | number | Kabuuang input tokens sa lahat ng API calls |
| `totals.completion_tokens` | number | Kabuuang output tokens |
| `totals.reasoning_tokens` | number | Tokens na ginamit para sa chain-of-thought (0 para sa karamihan ng models) |
| `totals.cached_tokens` | number | Tokens na na-serve mula sa prompt cache ng provider |
| `totals.total_cost_usd` | number | Kabuuang gastos sa USD |
| `totals.cost_per_entry_usd` | number | `total_cost_usd / entry_count` |
| `totals.cost_per_source_char` | number | USD kada source character — comparable sa mga wika |

### 3.6 Timing (Speed)

| Field | Type | Description |
|-------|------|-------------|
| `elapsed_seconds` | number | Wall-clock duration ng buong run (top-level) |
| `scores.avg_latency_seconds` | number | Mean response time kada entry |
| `scores.median_latency_seconds` | number | Median response time kada entry |
| `scores.p95_latency_seconds` | number | 95th percentile response time kada entry |

### 3.7 Per-Entry Results

Itinatala ng bawat entry sa `results[]` array ang isang pagsasalin. Ang per-entry data ay ipinipersist sa `run_card_entries` table (migration 005) na may denormalized LYSS verdicts (migration 006).

| Field | Type | Description |
|-------|------|-------------|
| `entry_id` | string | Tumatugma sa `entries[].id` sa corpus |
| `source` | string | Source text na isinalin |
| `expected` | string | Gold-standard reference translation |
| `raw_predicted` | string \| null | Raw model output bago ang post-processing |
| `predicted` | string | Aktuwal na output ng method (post-processed) |
| `segment` | string | Segment identifier (hal., sentence index) |
| `difficulty` | string \| null | Difficulty tier mula sa corpus |
| `domain` | string | Domain tag mula sa corpus (§2.7) |
| `exact_match` | boolean | Kung eksaktong tumugma ang output sa reference |
| `chrf_score` | number \| null | Sentence-level chrF++ (0–100) |
| `bleu_score` | number \| null | Sentence-level BLEU (0–100) |
| `latency_s` | number \| null | Response time sa segundo |
| `cost_usd` | number \| null | Gastos sa USD para sa entry na ito |
| `tool_call_count` | integer | Bilang ng tool calls na ginamit (0 kung wala) |
| `error` | string \| null | Error message kung nabigo ang entry na ito |
| `plugin_metrics` | object | Buong per-entry plugin output (JSONB) |
| `fst_valid` | boolean \| null | Tinanggap ng GiellaLT FST ang prediction (denormalized LYSS-fst) |
| `equivalent_match` | boolean \| null | Kinumpirma ng CRK linter ang structural equivalence (denormalized LYSS-eq) |
| `semantic_verdict` | string \| null | LYSS-sem verdict: `VALID`, `MISMATCH`, `UNKNOWN`, `ERROR` |
| `code_switching_detected` | boolean \| null | May source-language tokens na natukoy sa output |
| `hallucination_detected` | boolean \| null | May fabricated content na natukoy sa output |



### 3.8 Fingerprint

Isang reproducibility identifier. Dalawang run na may magkaparehong fingerprints ang gumamit ng parehong experimental setup.

Ang fingerprint ay ang SHA-256 hash ng sorted concatenation ng:
- `dataset.sha256`
- `model_slug`
- `condition`
- `system_prompt_sha256`
- `temperature`
- `harness_version`
- `batch_size`
- `tools_enabled`

> **Bakit 8 components?** Malaki ang epekto ng batch size at tool-calling sa output quality at dapat isama ang mga ito sa identity. Ang dalawang run na may magkaibang batch sizes o magkaibang tools na enabled ay magkaibang experimental setups, kahit tumugma ang lahat ng ibang parameter.

Ang dalawang run na may magkaparehong fingerprints ay dapat makagawa ng comparable results. Ang mga pagkakaiba ay dahil sa API non-determinism (temperature > 0) o provider-side model updates.

### 3.9 Run Card Hash

Ang SHA-256 hash ng buong run card JSON (na may field na `run_card_hash` mismo na nakatakda sa `""` habang nagha-hash). Ito ang tamper-detection seal. Kung magbabago ang anumang field, masisira ang hash.

---

## 4. Automated Metrics

Ang lahat ng metrics sa seksyong ito ay machine-computed. Tingnan ang §1.1.

### 4.1 Metric Definitions

| Metric | Status | What It Measures | Range |
|--------|--------|-----------------|-------|
| **chrF++** | ✅ Implemented | Character n-gram F-score. Gumagana sa character level, kaya mas robust ito kaysa word-level metrics (BLEU) para sa morphologically rich languages kung saan mahahaba at highly inflected ang mga salita. Kinakalkula ng sacrebleu. | 0–100 (native scale). Hinahati sa 100 kapag ginamit sa composite. |
| **FST acceptance rate** | ✅ Implemented | Fraction ng predicted words na tinanggap ng morphological analyzer (GiellaLT HFST) bilang valid forms sa target language. Ang salitang tinatanggap ng FST ay tunay at structurally valid na salita — hindi hallucination. | 0.0–1.0 |
| **Exact match** | ✅ Implemented | Fraction ng predictions na eksaktong tumutugma sa reference pagkatapos ng Unicode normalization. Mahigpit ngunit unambiguous — kapaki-pakinabang bilang ceiling check. | 0.0–1.0 |
| **Morphological accuracy** | 🔲 Planned | Para sa entries na may gold-standard morphological analysis: fraction ng morphemes na wastong na-generate. Mas granular kaysa FST acceptance — maaaring FST-valid ang isang salita ngunit mali ang morpheme structure (tamang root, maling tense). | 0.0–1.0 |
| **Equivalent match** | ⚡ Partial | Fraction na tumutugma sa acceptable variant ng reference — isinasaalang-alang ang word order, dialectal differences, at orthographic conventions. Kasalukuyang implemented para sa CRK sa pamamagitan ng `CrkLinterMetric` ng CRK eval standard (sa `eval_standards/crk/`); awtomatikong nilo-load sa pamamagitan ng deklarasyong `evalMetrics` ng CRK language card. Nangangailangan ang generic implementation ng per-entry `variants[]` sa corpus. | 0.0–1.0 |
| **Semantic score** | ⚡ Partial | Pagpapanatili ng kahulugan anuman ang surface form. Kasalukuyang implemented para sa CRK sa pamamagitan ng `CrkSemanticMetric` ng CRK eval standard (sa `eval_standards/crk/`, verdict-weighted proxy). Planned ang universal embedding-based cosine similarity — tingnan ang SCORING_SPEC §2.3. | 0.0–1.0 |

### 4.2 Composite Score

Ang composite score ay weighted average ng lahat ng *available* metrics:

```
composite = Σ (weight_i × metric_i)   for all available metrics
             ─────────────────────
             Σ weight_i              (renormalized to sum to 1.0)
```

Kapag unavailable ang metric (walang FST na naka-configure, walang variant classes na tinukoy, walang embedding model), ang weight nito ay muling ipinapamahagi nang proporsyonal sa natitirang metrics. Ibig sabihin, palaging comparable ang composite sa loob ng isang wika — ginagamit nito kung anumang metrics ang available para sa wikang iyon at nagno-normalize nang naaayon.

**Ang weight tables, input normalization rules, at buong metric inventory ay tinukoy sa `SCORING_SPEC.md` §4.** Ang dokumentong iyon ang SSOT para sa:
- Profile A weights (mga wikang may FST coverage — 9 metrics, structural metrics carry 40%)
- Profile B weights (mga wikang walang FST coverage — 8 metrics)
- Normalization rules (chrF++ ÷ 100, code-switching at hallucination rate inversion)
- Metrics na excluded mula sa composite (BLEU, COMET, TER, length ratio, consistency) at bakit

Sinasalamin ng harness code ang mga table na ito sa `mt_eval_harness/scoring.py`. Kapag nagbago ang SCORING_SPEC, ina-update ang `scoring.py` upang tumugma at vine-validate ng `test_scoring_ssot.py` ang alignment.

> **Bakit hindi BLEU?** Gumagana ang BLEU sa word level at pinaparusahan ang morphological variation. Para sa polysynthetic languages, maaaring maging buong clause ang iisang salita — ituturing ng BLEU ang maliliit na inflectional differences bilang ganap na miss. Mas mahusay itong hinahawakan ng chrF++ sa pamamagitan ng paggana sa character level. Excluded ang BLEU mula sa parehong weight tables. Tingnan ang SCORING_SPEC Appendix A para sa buong rationale.


### 4.3 Cost-Adjusted Score

Para sa mga method na gumagamit ng paid APIs, nag-uulat din kami ng secondary ranking. Ang cost-adjusted formula ay tinukoy sa `SCORING_SPEC.md` §6.3.

---

## 5. Quality Tiers {#5-quality-tiers}

Ang quality tiers ay heuristic labels sa automated composite scores. Inilalarawan ng mga ito kung ano ang karaniwang kahulugan ng mga score sa praktika, batay sa human review ng outputs sa bawat level. **Hindi sila validated quality judgments** — human review (§6) lamang ang makapagkukumpirma ng aktuwal na usability.

**Ang tier thresholds at descriptions ay tinukoy sa `SCORING_SPEC.md` §5.** Ang tiers ay: Baseline (0.00–0.30), Emerging (0.30–0.50), Functional (0.50–0.70), Deployable (0.70–0.85), at Fluent (0.85–1.00).

> [!IMPORTANT]
> **Provisional ang automated tiers.** Ang mga label na ito ay mga nominasyon para sa review, hindi quality declarations. Ang method na umaabot sa "Deployable" sa automated metrics ay kandidato para sa community evaluation — hindi produktong dapat i-ship. Human review (§7) lamang ang makapagkukumpirma ng aktuwal na usability. Maaaring magkaiba ang tier boundaries sa bawat wika.

Provisional ang tiers na ito. Ire-recalibrate ang mga ito habang naiipon ang human validation data at natututuhan namin kung nasaan ang aktuwal na threshold na "nakikita ng speaker na kapaki-pakinabang ito" para sa bawat wika. Maaaring magkaiba ang tier boundaries sa bawat wika.

Walang method ang maaaring mag-claim ng **Deployable** o mas mataas nang walang community review na kumukumpirma na sumasang-ayon ang bilingual speakers na usable ang output.

---

## 6. Benchmark Protocol

Ang **benchmark** ay ang sistematikong paggawa ng run cards sa kabuuan ng idineklarang parameter space sa isang ibinigay na dataset. Hindi ito iisang run — ito ay structured exploration kung paano nagpe-perform ang iba't ibang configuration.

### 6.1 Ano ang Ginagawa ng Benchmark

Gumagawa ang benchmark ng **matrix ng run cards** — isa para sa bawat kombinasyon ng parameter values. Nagbibigay-daan ang matrix sa multifaceted comparison sa:

- **Quality** — composite score, individual metric breakdowns
- **Cost** — kabuuan at per-entry cost para sa bawat configuration
- **Speed** — wall-clock time at per-entry latency

Walang iisang "benchmark score." Ang benchmark ay ang buong matrix. Magkakaibang facet ang mahalaga sa magkakaibang stakeholder: ang researcher ay nag-o-optimize para sa composite score, ang deployment engineer ay nag-o-optimize para sa cost-per-entry, ang komunidad ay nagre-review ng kalidad.

### 6.2 Parameter Space

Idinedeklara ng benchmark kung aling parameters ang pine-permute:

| Axis | Typical Values | Purpose |
|------|---------------|---------|
| `model` | 4–12 models (frontier + mid-tier + budget) | Gaano kahalaga ang model capability? |
| `temperature` | 0.0, 0.3, 0.7 | Nakakatulong ba o nakakasama ang sampling randomness? |
| `prompt_version` | 2–3 prompt strategies | Gaano ka-sensitive ang method sa prompt design? |
| `coaching_config` | with/without coaching data | Pinapabuti ba ng pag-inject ng linguistic knowledge ang output? |
| `tool_config` | with/without FST, with/without dictionary | Pinapabuti ba ng linguistic tools ang output? |

Ang buong permutation space:
```
runs = |models| × |temperatures| × |prompts| × |coaching| × |tools|
```

Karaniwang initial benchmark: 12 models × 3 temperatures × 2 prompts × 2 coaching = 144 runs.

### 6.3 Baseline vs. Method Evaluation

May dalawang natatanging layunin ang benchmark:

**Baselining** — pagmamapa ng landscape gamit ang naive approaches. "Ano ang kaya ng umiiral na models para sa wikang ito nang walang anumang language-specific engineering?" Itinatatag nito ang bar. Sinasabi sa inyo ng baseline matrix: aling models ang may pinakamababang hallucination, aling temperatures ang gumagawa ng pinaka-consistent na output, kung nakakatulong ba ang coaching data kahit kaunti, kung saan uniformly nabibigo ang lahat ng models (na nagpapakita ng mahihirap na linguistic problems).

**Method evaluation** — pagsubok sa partikular na engineered method. "Nalalampasan ba ng aking FST-gated coached pipeline ang baselines?" Inihahambing ang run card ng method sa baseline matrix. Interesante ang isang method kapag nalalampasan nito ang pinakamahusay na baseline — kapag nagdaragdag ng value ang engineering higit sa naive model calls.

Parehong gumagawa ang dalawang aktibidad ng run cards na may parehong schema. Ang pagkakaiba ay nasa intent at parameter space: ang baselines ay nagpe-permute sa models at configs; ang method evaluation ay sumusubok ng isang method laban sa pinakamahuhusay na configurations.

### 6.4 Dev vs. Gold-Standard Evaluation

Malayang nag-i-iterate ang mga method developer laban sa `development` at `diagnostic` corpus segments. Ito ay informal — walang limits, walang submissions, walang governance involvement. Inaalam ng developer kung ano ang gumagana.

Ang opisyal na leaderboard scores ay nagmumula lamang sa `gold_standard` evaluation. Ito ay formal:
1. Isinusumite ng developer ang kanilang kumpleto at runnable na method (code + config + coaching data)
2. Pinapatakbo ito ng governance org sa sandboxed harness laban sa secret test set
3. Mga score lamang ang ibinabalik

Tingnan ang §8 para sa buong sovereignty mechanism.

---

## 7. Human Validation {#7-human-validation}

Ang automated metrics ay mga proxy. Ang human validation ang ground truth.

### 7.1 Ano ang Nahuhuli ng Human Review na Nakakaligtaan ng Metrics

- **Morphologically valid ngunit semantically wrong** — tinatanggap ng FST ang salita, mataas ang chrF++, ngunit iba ang kahulugan ng pagsasalin
- **Culturally inappropriate** — technically correct ang pagsasalin ngunit gumagamit ng register o framing na tatanggihan ng komunidad
- **Hallucinated plausibility** — mukhang target language ang output para sa non-speaker ngunit gibberish para sa fluent speaker
- **Acceptable ngunit unmarked variation** — tama ang output ngunit minamarkahan itong mali ng automated metrics dahil gumagamit ito ng dialectal variant na wala sa reference

### 7.2 Ang Validation Gate

Walang method ang maaaring umusad mula **Functional** patungong **Deployable** tier nang walang human validation na kumukumpirma na sumasang-ayon ang bilingual speakers na usable ang output. Hindi ito formality — ito ang punto. Umiiral ang automated metrics upang bawasan ang dami ng output na kailangang i-human review. Hindi nila ito mapapalitan.

### 7.3 Community Review Protocol

> 🔲 **Planned**: Hindi pa live ang community review interface. Inilalarawan ng seksyong ito ang nilalayong proseso.

1. Umaabot ang isang method sa Deployable threshold sa automated metrics
2. Inihaharap sa bilingual speakers ang sample ng outputs (stratified ayon sa difficulty tier)
3. Nire-rate ng speakers ang bawat pagsasalin sa scale: **reject**, **gist** (malinaw ang kahulugan ngunit mali ang phrasing), **acceptable** (tama na may minor issues), **excellent** (hindi maipagkaiba sa human translation)
4. Nire-review ng governance org ang aggregate ratings
5. Kung tinatanggap ng komunidad ang method, nagpapatuloy ito sa ownership transfer at deployment

---

## 8. Sovereignty

Naglalaman ang evaluation datasets ng curated linguistic knowledge na pag-aari ng language community. Tinutukoy ng seksyong ito ang technical at legal framework para protektahan ang data na iyon.

### 8.1 Ang Problema

Karaniwang inilalathala ng conventional benchmarks ang test sets nang bukas. Kapag nailathala na, hindi na maaaring i-un-publish ang data. Para sa Indigenous at minority language communities, lumilikha ito ng extractive dynamic — ginagamit ang linguistic data nang walang ongoing consent. Alinsunod sa pragmatic view ni Dhein sa biodata sovereignty, itinuturing namin ang linguistic data bilang "mercurial resource with unknowable potential" na nangangailangan ng dynamic, relational governance.

### 8.2 Sandboxed Execution

Ang pangunahing enforcement mechanism: ibinibigay ng developer ang kanilang method module, pinapatakbo ito ng governance org laban sa ganap na secret test set sa sarili nilang infrastructure, at mga score lamang ang ibinabalik. Hindi kailanman nakikita ng developer ang source sentences o ang reference translations.

```mermaid
graph TD
    A["Developer builds method\nusing public development corpus"] --> B["Developer submits\nmethod module\n(code + config + coaching)"]
    B --> C["Governance org runs method\nin sandboxed harness\nagainst secret test set"]
    C --> D["Scores returned\nto developer"]
    D --> E{"Meets Deployable\nthreshold?"}
    E -->|Yes| F["Ownership transfer\n+ community review"]
    E -->|No| G["Developer iterates"]
    G --> A
```

Ang flow:
1. **Public ang development corpus.** Walang restrictions sa mga segment na `development` at `diagnostic`.
2. **Ganap na secret ang gold-standard test set.** Parehong ang source sentences at reference translations ay nasa governance-controlled infrastructure.
3. **Upang makakuha ng opisyal na score, ibinibigay ninyo ang inyong method.** Pinapatakbo ito ng governance org sa sandbox. Mga score lamang ang bumabalik.
4. **Nasa governance org na ang method.** Ang submission AY ang method code. Kung umabot ito sa Deployable threshold, kasalukuyan nang isinasagawa ang ownership transfer.
5. **Nangangailangan ang submission ng pagsang-ayon sa terms.** Kasama ang ownership transfer clause (§8.3).
6. **Ganap na kontrolado ng governance org ang access.** Maaari nilang tanggihan o bawiin ang evaluation anumang oras. Dynamic consent.
7. **Ang encryption at rest ay defense-in-depth.** Architectural ang primary enforcement.

### 8.3 Ownership Transfer

Ang mga method na nakakamit ng composite score na nasa o lampas sa Deployable threshold (0.70) laban sa gold-standard evaluation, **at** pumapasa sa human validation (§7), ay napapailalim sa ownership transfer.

**Pinananatili ng developer ang:**
- Attribution at credit (nananatili ang pangalan sa leaderboard)
- Karapatang maglathala tungkol sa method
- Karapatang gamitin ang method para sa ibang language pairs

**Nakukuha ng governance org ang:**
- Karapatang gamitin, baguhin, ipamahagi, at i-monetize ang method para sa kanilang wika
- Karapatang mag-sublicense
- Pisikal na pagmamay-ari ng method code (hawak na mula sa evaluation submission)

### 8.4 Mga Kinakailangan para sa Governance Organization

Upang magsilbing key custodian para sa language benchmark:

1. **Katawanin ang language community** — maipapakitang ugnayan sa speakers at cultural authorities
2. **Kapasidad para sa key management** — technical ability na pamahalaan ang cryptographic keys
3. **Mangako sa evaluation availability** — dapat manatiling evaluable ang benchmark
4. **Maglathala ng terms of participation** — malinaw na dokumentasyon ng sinasang-ayunan ng developers
5. **Mag-operate sa ilalim ng kinikilalang sovereignty principles** — OCAP®, CARE, o katumbas

### 8.5 Alignment sa OCAP® at CARE

| Principle | Implementation |
|-----------|---------------|
| **Ownership** (OCAP) | Ang linguistic data ay pag-aari ng komunidad. Kinokontrol ng governance org ang evaluation infrastructure. |
| **Control** (OCAP) | Kinokontrol ng governance org ang evaluation sa pamamagitan ng sandboxed execution. Sila ang nagpapasya kung sino ang magsusumite at sa anong terms. |
| **Access** (OCAP) | May unrestricted access ang komunidad sa sarili nilang data, results, at methods na binuo laban dito. |
| **Possession** (OCAP) | Hindi kailanman umaalis ang test set sa governance infrastructure. Encryption at rest bilang backup. |
| **Collective Benefit** (CARE) | Tinitiyak ng ownership transfer na nakikinabang ang komunidad sa methods. Pinananatili ito ng revenue model (10% throughbill margin; nananatili sa komunidad ang ~90%). |
| **Authority to Control** (CARE) | Ang sandboxed execution ang technical implementation. |
| **Responsibility** (CARE) | Tinatanggap ng developers ang responsibilidad sa pamamagitan ng terms of participation. |
| **Ethics** (CARE) | Karapatan ng komunidad kaysa kaginhawaan ng researcher. |

### 8.6 Dependency Classes at ang Sandbox Network Policy

Parehong nakasalalay ang sandboxed execution (§8.2) at ownership transfer (§8.3) sa eksaktong pagkaalam kung ano ang kailangan ng method sa runtime. Tinutukoy ng [Method Interface spec](/docs/specifications/methods#method-validity-and-dependency-classes) ang limang **dependency classes** — S (self-contained), O (open external), A1 (substitutable LLM inference), A2 (non-substitutable external API), X (closed) — at ang dependency manifest na dapat ideklara ng bawat method. Itinatala ng subsection na ito kung paano ipinapatupad ng sandbox network policy ang mga ito.

**Default-deny egress.** Kinakailangan ng sandbox specification na walang network access ang method containers bilang default. Hindi ito firewall rule — inaalis ng specification ang network mula sa execution environment, kaya ang undeclared network dependency ay nabibigo sa architecture layer, hindi sa policy layer. Ganap na tumatakbo ang Class S at O methods mula sa artifacts na vendored sa submission (ang Class O artifacts ay pinned at mirrored sa submission time).

**Ang LLM gateway (🔲 planned).** Karamihan sa methods ay tumatawag sa LLMs, kaya tinutukoy ng sandbox specification ang eksaktong isang egress exception: isang **LLM gateway** na pinapatakbo ng evaluation infrastructure. Ang gateway ay:

- nagpo-proxy ng inference requests sa **explicit allowlist of pinned models** — ang model identifiers na nakatala sa manifest at run card ng method;
- **naglo-log ng bawat request at response** sa sealed audit log, upang ma-review ang gateway traffic para sa data-exfiltration attempts bago i-release ang scores;
- ang *tanging* network path — walang general egress, walang DNS, walang ibang endpoints.

Ito ang dahilan kung bakit evaluable ang Class A1 methods nang hindi iniiwan ang verifiability guarantees ng §8.2 — ngunit tunay itong trade-off, at malinaw itong pinapangalanan ng specification: ang pagsasalin ng secret source sentence sa pamamagitan ng external model ay **nagdi-disclose ng source sentence na iyon sa model provider**. Hindi kailanman umaalis ang reference translations (hawak ang mga ito ng harness, sa labas ng container; tingnan ang §8.2), at hindi pa rin makakapag-exfiltrate ang method mismo ng anumang higit sa nilalaman ng logged, allowlisted inference calls. Kung katanggap-tanggap ang bounded disclosure na iyon para sa isang partikular na corpus ay desisyon ng steward: ang pag-authorize ng Class A1 evaluation ay nangangahulugang knowingly itong ina-authorize, kada run, tulad ng bawat iba pang paggamit ng data.

**Status.** Specified na ang sandbox at gateway nito ngunit hindi pa built. Hanggang operational na ang gateway, Class S at O methods lamang ang makagagawa ng gold-standard scores; nananatiling prize-eligible in principle ang Class A1 methods (tingnan ang [Prize Specification §1.6](/docs/specifications/prizes)) ngunit hindi pa maaaring ma-evaluate laban sa secret segments. Hindi makakapasok sa sandbox ang Class A2 dependencies hangga't hindi nagbibigay ng pahintulot ang rights holder — dapat payagang *umiral* ang artifact sa sandbox bago pa man lumitaw ang anumang usapin sa network.

---

## 9. Leaderboard at Submission

### 9.1 Submission Requirements

Dapat kasama sa isang valid leaderboard submission ang:

1. Kumpletong run card (§3) na may lahat ng required fields
2. Ang method code — ganap na runnable, may installation instructions
3. Lahat ng dependencies — coaching data, dictionaries, FST binaries, prompts
4. Cost report
5. README na naglalarawan sa approach at limitations ng method

### 9.2 Legitimacy Criteria

1. **Walang training sa evaluation data.** Hindi dapat na-expose ang methods sa entries na `gold_standard` o `held_out`. (Architecturally enforced — hindi kayo makakapag-train sa data na hindi ninyo kailanman nakita.)
2. **Ideklara ang paggamit ng development data.** Pinapayagan ang paggamit ng `development` entries para sa few-shot prompting ngunit dapat itong ideklara.
3. **Reproducibility.** Dapat makapag-re-run ang governance org at makamit ang scores sa loob ng ±2%.
4. **Generalization.** Dapat gumana ang methods sa unseen entries, hindi lamang sa memorized examples.

### 9.3 Anti-Gaming

1. **Variant-class linting** — fina-flag ang kahina-hinalang perpektong performance sa entries na may known variants
2. **Corpus rotation** — maaaring i-rotate ng governance org ang entries sa pagitan ng segments nang walang abiso
3. **Community review** — nahuhuli ng human validation gate (§7) ang methods na naglalaro ng metrics ngunit gumagawa ng masamang output

### 9.4 Verification Tiers

Inilalarawan ng verification tiers kung **sino ang nag-validate ng resulta** — orthogonal sa quality tiers (§5), na naglalarawan kung ano ang ibig sabihin ng automated score.

| Tier | Meaning | How Achieved |
|------|---------|--------------|
| **Self-benchmarked** | Pinatakbo ng developer ang harness at isinumite ang run card | PR o `--submit` flag laban sa `development` segment |
| **GDS Verified** | Independently ni-reproduce ng maintainers ang resulta | Isumite ang method bilang installable plugin; re-run ng maintainers |
| **Community Validated** | Pinatakbo ng governance org laban sa `gold_standard` + community review | Isumite ang method code sa governance org (§8.2); pumasa sa human validation (§7) |

Maaaring maging Self-benchmarked ang isang method sa Functional quality tier. Independent axes ang quality tier at verification tier sa leaderboard.

### 9.5 Layered Submission Model

Nakasalalay ang submission mechanism sa kung aling corpus segment ang inyong sinusuri:

| Segment | Submission Path | Verification | Method Code Required? |
|---------|----------------|-------------|----------------------|
| `development` | Self-serve: patakbuhin ang harness, isumite ang run card sa pamamagitan ng PR o API | Self-benchmarked | Hindi — pinananatili ninyo ang inyong code |
| `development` | Maintainer re-run: isumite ang method bilang plugin | GDS Verified | Oo — dapat installable ang method |
| `gold_standard` | Isumite ang method sa governance org; pinapatakbo nila ito sa sandbox | Community Validated | Oo — isinusumite at hinahawakan ang method |

Walang restrictions ang self-serve path (development segment). Nangangailangan ang sovereign path (gold-standard segment) ng buong method submission dahil (a) hindi kailanman nakikita ng developer ang test set, at (b) ang methods na umaabot sa Deployable ay napapailalim sa ownership transfer (§8.3).

### 9.6 Method Classes

Inuuri ang methods ayon sa type. Ang canonical enum ay tinukoy sa harness codebase (`VALID_METHOD_CLASSES` sa `config.py`):

| Class | Description |
|-------|-------------|
| `raw-llm` | Direktang LLM call nang walang language-specific engineering |
| `coached-llm` | LLM na may coaching data (examples, grammar notes, dictionary entries) |
| `pipeline` | Multi-step pipeline (hal., translate → FST validate → retry) |
| `custom-plugin` | Custom `TranslationMethod` plugin |
| `api` | External translation API (Google Translate, DeepL, atbp.) |
| `human` | Human translator baseline |

### 9.7 Leaderboard Fields

| Field | Description |
|-------|-------------|
| Rank | Posisyon ayon sa composite score |
| Method name | Identifier na pinili ng developer |
| Composite score | Weighted average ng available metrics (§4.2) |
| chrF++ | Character n-gram score (0–100) |
| FST acceptance | Morphological validity rate (0.0–1.0) |
| Exact match | Strict match rate (0.0–1.0) |
| Semantic score | Pagpapanatili ng kahulugan (0.0–1.0) — 🔲 kapag available |
| Cost per entry | USD kada corpus entry |
| Speed | Avg latency kada entry (seconds) |
| Cost-adjusted score | Secondary ranking (§4.3) |
| Method class | Mula sa §9.6 enum |
| Model | LLM/engine na ginamit |
| Quality tier | Automated composite range (§5) |
| Verification tier | Sino ang nag-validate (§9.4) |
| Date | Kailan sinuri |

> [!NOTE]
> **Ang lahat ng scores na ipinapakita sa leaderboard ay automated proxy measurements.** Ipinapahiwatig ng mga ito ang relative method performance sa ilalim ng controlled conditions ngunit hindi bumubuo ng quality guarantees. Hiwalay na minamarkahan ang community-validated methods sa pamamagitan ng Verification tier column. Para sa mga detalye ng methodology, tingnan ang [SCORING_SPEC.md](/docs/specifications/scoring).

---

## 10. Cost Framework {#10-cost-framework}

### 10.1 Per-Run Cost

```
run_cost = entries × api_calls_per_entry × cost_per_api_call
```

Karaniwang per-run costs para sa 150-entry corpus:

| Method | Model | Estimated Cost |
|--------|-------|---------------|
| Naive LLM | Gemini 2.5 Flash | $0.15–0.30 |
| Coached LLM | Gemini 2.5 Flash | $0.30–0.60 |
| FST-gated (3 retries) | Gemini 2.5 Flash | $0.45–1.20 |
| Naive LLM | Claude Sonnet 4 | $0.45–0.90 |
| Coached LLM | GPT-4.1 | $0.60–1.50 |

### 10.2 Benchmark (Sweep) Cost

```
sweep_cost = Σ run_cost(i)   for each parameter combination i
```

Karaniwang sweep: 12 models × 3 temps × 2 prompts × 2 coaching = 144 runs sa ~$0.50 avg = **~$72 kada sweep**.

### 10.3 Per-Language Establishment

| Component | Cost Range | Notes |
|-----------|-----------|-------|
| Speaker compensation (corpus) | $2,500–6,000 | 50–150 entries sa $50–65/hr |
| Speaker compensation (review) | $500–1,500 | Pagre-review ng method output |
| Compute (benchmark sweeps) | $100–500 | Maramihang sweeps sa panahon ng development |
| Compute (ongoing leaderboard) | $50–200/year | Pagpapatakbo ng submitted methods |
| Infrastructure (sandbox) | $200–500/year | Eval infra ng governance org |
| **Total establishment** | **$3,350–8,500** | |

### 10.4 Program Scale

| Scale | Annual Cost | Notes |
|-------|------------|-------|
| 1 language (maintenance) | $1,000–3,000 | Pagkatapos ng establishment |
| 5 languages (establishment + maintenance) | $25,000–65,000 | Unang taon |
| 10 languages (steady state) | $15,000–40,000 | Kada taon pagkatapos ng establishment |

---

## 11. Extending to New Languages {#11-extending-to-new-languages}

### 11.1 Minimum Requirements

1. **50+ entries** sa `gold_standard` segment
2. **30+ entries** sa `development` segment
3. **10+ entries** sa `diagnostic` segment na tumatarget sa partikular na linguistic phenomena
4. **Provenance** para sa bawat entry
5. **Difficulty distribution** — hindi bababa sa 3 sa 5 tiers
6. **Register distribution** — hindi bababa sa 2 registers
7. **Community consent** — dokumentadong kasunduan mula sa language community

### 11.2 Optional but Valuable

- **FST morphological analyzer** — nagbibigay-daan sa pinakamakapangyarihang metric para sa polysynthetic languages
- **Bilingual dictionary** — nagbibigay-daan sa dictionary-based methods, binabawasan ang hallucination
- **Gold-standard morphological analysis** — nagbibigay-daan sa morphological accuracy metric
- **Variant classes** — nagbibigay-daan sa equivalent match metric at anti-gaming linting
- **Governance organization** — nagbibigay-daan sa cryptographic sovereignty at ownership transfer

### 11.3 Ang Agent-Assisted Path

> 🔲 **Planned**: Ang agent-assisted corpus creation ay future capability.

Para sa mga wikang walang malawak na umiiral na resources:

1. Gumagawa ang agent ng candidate source sentences sa iba't ibang difficulty tiers at registers
2. Isinasalin ng bilingual speaker ang mga ito (ang hakbang na ito ay palaging ginagawa ng tao)
3. Nagmumungkahi ang agent ng morphological analysis (validated ng FST kung available, kung hindi ay ng speaker)
4. Ipo-format ng agent ang lahat sa corpus schema
5. Nire-review ng linguist o speaker ang final corpus

Binabawasan nito ang speaker time mula ~80 oras tungo sa ~30–40 oras kada wika.

---

*Ang spec na ito ay living document. Habang nagtatatag kami ng benchmarks para sa mas maraming wika, matututuhan namin kung ano ang gumagana at irerepina namin ito nang naaayon. Ang layunin ay sapat na rigorous upang maging credible, sapat na flexible upang maging useful, at sapat na open upang makalahok ang sinuman — ayon sa terms ng komunidad.*