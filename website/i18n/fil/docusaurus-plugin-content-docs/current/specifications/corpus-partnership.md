---
sidebar_position: 9
title: "Estratehiya sa Pakikipagsosyo sa Corpus"
slug: '/specifications/corpus-partnership'
---
# Estratehiya sa Pakikipag-partner para sa Corpus: Pagtatatag ng mga Evaluation Corpora sa Pamamagitan ng mga Academic Linguistics Department

> **Layunin.** Ibinibigay ng dokumentong ito ang kumpletong workflow para sa pagtatatag ng machine translation evaluation corpus sa pamamagitan ng pakikipag-partner sa isang linguistics department. Saklaw nito kung ano ang kailangan naming maihatid ng department, ano ang dapat na anyo ng corpus, paano ito cryptographically sealed, paano gumagana ang sandbox evaluation, at ano ang makukuha ng department bilang kapalit. Ito ang dokumentong dadalhin ninyo sa pulong kasama ang potensiyal na academic partner.
>
> **Audience.** Mga department head, principal investigator, research coordinator, at mga Indigenous language program director sa mga unibersidad na may aktibong language documentation o NLP programs.
>
> **Mga kasamang dokumento:**
> - [Protocol sa Pagpapatunay ng Speaker](/docs/specifications/speaker-validation) — ang hinihingi para sa bilingual speakers upang *markahan* ang umiiral na mga salin (quality rating, linter validation, FST review)
> - [Specification ng Benchmark](/docs/specifications/benchmark) — ang buong technical spec para sa corpora, run cards, at evaluation protocols
> - [Soberanya ng Datos](/docs/sovereignty/data-sovereignty) — OCAP®, CARE, at kung bakit mahalaga ang paglipat ng pagmamay-ari
>
> Huling na-update: 2026-06-07

---

## 1. Ano ang Nililikha ng Partnership na Ito

Isang **sealed evaluation corpus**: isang curated na set ng parallel text pairs (source language → target language) na nagiging ground truth para sa pagsukat ng kalidad ng machine translation. Sinusubok ang mga method laban sa corpus na ito sa isang sandbox — hindi kailanman nakikita ng mga developer ang test data.

Lumilikha ang partnership ng tatlong artifact:

| Artifact | Ano Ito | Sino ang Kumokontrol Dito |
|----------|-----------|-----------------|
| **Development corpus** | 100–200+ pampublikong parallel text pairs para sa method development | Inilalathala nang bukas (CC BY-NC-SA 4.0 o katumbas) |
| **Gold-standard test set** | 50–150 lihim na parallel text pairs para sa opisyal na evaluation | Community governance org (cryptographically sealed) |
| **Diagnostic test suite** | 10–50 naka-target na contrastive pairs na sumusubok sa mga partikular na linguistic phenomena | Inilalathala nang bukas |

Pinapagana ng development corpus ang sinuman na bumuo ng mga translation method. Tinitiyak ng gold-standard set na nasusuri ang mga method na iyon nang tapat. Nahuhuli ng diagnostic suite ang mga partikular na failure mode (hal., "kaya ba ng system na ito ang obviation?").

---

## 2. Ano ang Kailangang Gawin ng Department

### Phase 1: Disenyo ng Corpus (2–4 linggo, oras ng researcher)

**Lead:** PI o postdoc na may expertise sa target language.

1. **Pumili ng mga domain ng source material.** Pumili ng 4–6 real-world domain kung saan talagang kailangan ng language community ang pagsasalin. Sinusuportahan ng aming taxonomy ang 16 domain (tingnan ang Benchmark Spec §2.7):

   | Priority | Domain | Bakit |
   |----------|--------|-----|
   | 🔴 High | `edu` — Educational | Mga textbook, curricula — direktang pangangailangan ng community |
   | 🔴 High | `gov` — Government | Mga dokumento ng band council, policy — praktikal na pang-araw-araw na pangangailangan |
   | 🔴 High | `medical` — Health | Clinic intake forms, impormasyong pangkalusugan — safety-critical |
   | 🟡 Medium | `conv` — Conversational | Pang-araw-araw na pananalita — nagtatatag ng baseline fluency |
   | 🟡 Medium | `legal` — Legal | Mga dokumento ng karapatan, mga treaty — kahalagahan sa community |
   | 🟢 Lower | `literary` — Literary/Cultural | Mga kuwento, oral histories — pagpapanatili ng kultura |

2. **Mag-draft ng corpus design document** na tumutukoy sa:
   - Target size bawat segment (development, gold_standard, diagnostic)
   - Distribusyon ng difficulty tier (tingnan ang §3.3 sa ibaba)
   - Saklaw ng register at domain
   - Pamantayan sa pagpili ng source sentence (walang synthetic text, hindi Bible-only)
   - Plano sa speaker recruitment

3. **Isumite sa amin ang disenyo para sa review.** Ive-validate namin ito laban sa corpus schema (Benchmark Spec §2) at ibabalik ang feedback sa loob ng 1 linggo.

### Phase 2: Paglikha ng Source Sentence (4–8 linggo, oras ng speaker)

**Lead:** Research coordinator na nakikipagtulungan sa bilingual speakers.

1. **Gumawa o pumili ng mga source sentence** sa kabuuan ng mga planadong domain at difficulty tier. Maaaring ang sources ay:
   - Umiiral na nalathalang bilingual materials (mga textbook, dokumento ng pamahalaan)
   - Bagong elicited sentences na idinisenyo upang saklawin ang partikular na linguistic phenomena
   - Inangkop mula sa real-world documents (mga agenda ng band council, clinic forms, educational materials)

2. **Bawat source sentence ay dapat may:**
   - Domain tag (mula sa 16-code taxonomy)
   - Register tag (conversational, formal, technical, ceremonial, educational)
   - Context tag (greeting, declaration, question, instruction, narrative, label, error)
   - Tinatayang difficulty tier (1–5, tingnan ang §3.3)
   - Provenance tag (textbook, elicited, corpus, gold_standard)

3. **Isalin ang bawat source sentence** sa target language, na isasagawa ng bilingual speakers. Mahalaga ang multiple reference translations bawat entry ngunit hindi kinakailangan.

4. **Opsyonal, magdagdag ng morphological analysis** para sa bawat reference translation:
   - Interlinear gloss (morpheme-by-morpheme breakdown)
   - FST tag string (kung may FST para sa wika)
   - Mga tala ng translator tungkol sa dialectal variants, ambiguity, o cultural context

### Phase 3: Quality Assurance (2–4 linggo)

**Lead:** Linguist na may expertise sa target language.

1. **Cross-review.** Dapat suriin ang bawat translation ng kahit isang karagdagang bilingual speaker na hindi gumawa ng orihinal na translation. Tinitingnan ng reviewer:
   - Tumpak ba ang translation?
   - Natural ba ang tunog nito?
   - Tama ba ang difficulty rating?
   - Mayroon bang katanggap-tanggap na variants na dapat itala?

2. **Patakbuhin sa aming schema validator.** Nagbibigay kami ng script na nagva-validate ng corpus laban sa entry schema (Benchmark Spec §2.2). Tinitingnan nito:
   - Naroroon ang kinakailangang fields
   - Valid ang domain codes
   - Ang difficulty tiers ay integers 1–5
   - Walang duplicate IDs
   - Character encoding (UTF-8 NFC normalization)

3. **Kung may FST para sa wika,** patakbuhin dito ang reference translations. Dapat FST-valid ang bawat salita sa reference. Ang mga salitang hindi (loanwords, neologisms, proper nouns) ay dapat idokumento sa isang allowlist.

### Phase 4: Segmentation at Sealing (1 linggo, aming engineering)

**Lead:** Champollion team, na may review ng department.

1. **Stratified split.** Hinahati namin ang corpus sa mga segment gamit ang deterministic random sampling (nakadokumento ang seed, reproducible):

   | Segment | Target Size | Access |
   |---------|------------|--------|
   | `development` | 60% ng entries (min 100) | Public |
   | `gold_standard` | 30% ng entries (min 50) | Secret, sealed |
   | `held_out` | 10% ng entries (min 10) | Secret, sealed, hindi kailanman ginagamit hanggang ma-activate |

   Pinapanatili ng split ang distribusyon ng difficulty tier (stratified sampling) upang ang bawat segment ay may proporsyonal na representasyon sa lahat ng tier.

2. **Cryptographic sealing** ng gold_standard at held_out segments:

   ```
   1. SHA-256 hash of each entry (source + reference + metadata)
   2. SHA-256 hash of the complete segment file
   3. Segment file encrypted with AES-256-GCM
   4. Encryption key split using Shamir Secret Sharing (2-of-3 threshold)
   5. Key shares distributed to:
        - Share 1: Community governance organization
        - Share 2: Academic department partner
        - Share 3: Champollion project (escrow)
   6. Hash manifest published to a public commit (proves the corpus existed
      at a specific time without revealing its contents)
   ```

3. **Ang development segment** ay kino-commit sa public repository at inilalathala na may buong licensing.

4. **Ang diagnostic segment** ay public din — sinusubok nito ang partikular na linguistic phenomena (tingnan ang §3.4).

### Phase 5: Integration at Launch (1–2 linggo, aming engineering)

1. **Harness configuration.** Idinaragdag namin ang wika sa evaluation harness:
   - Language card created o verified
   - Corpus registered sa dataset registry
   - LYSS metrics configured (LYSS-fst kung may FST, LYSS-eq kung may linter rules)
   - Default scoring profile selected (Profile A kung may FST, Profile B kung wala)

2. **Baseline benchmark.** Nagpapatakbo kami ng 12-model sweep laban sa development segment upang punan ang leaderboard ng initial scores.

3. **Public announcement.** Lumilitaw ang wika sa Arena leaderboard na may live development-segment benchmark. Kinikilala ang department bilang corpus partner.

---

## 3. Ano ang Dapat na Anyo ng Corpus

### 3.1 Format

Bawat corpus file ay isang JSON document na sumusunod sa schema sa Benchmark Spec §2.1–§2.2:

```json
{
  "dataset": {
    "id": "crk-ualberta-v1",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "source_language": "en",
    "target_language": "crk",
    "created": "2026-09-15",
    "license": "CC-BY-NC-SA-4.0",
    "provenance": ["textbook", "elicited", "gold_standard"]
  },
  "entries": [
    {
      "id": 1,
      "source": "I see the dog",
      "reference": "niwâpamâw atim",
      "segment": "development",
      "difficulty": 2,
      "provenance": "textbook",
      "register": "conversational",
      "context": "declaration",
      "domain": "edu",
      "morphological_analysis": "ni-wâpam-âw atim | 1sg-see.TA-3sg.DIR dog.AN",
      "notes": "Animate noun (atim); direct form because speaker is proximate"
    }
  ]
}
```

### 3.2 Minimum Size Requirements

| Segment | Minimum Entries | Recommended |
|---------|----------------|-------------|
| `development` | 100 | 200–300 |
| `gold_standard` | 50 | 100–150 |
| `diagnostic` | 10 | 30–50 |
| `held_out` | 10 | 20–30 |
| **Total** | **170** | **350–530** |

### 3.3 Difficulty Distribution

Dapat magsama ang corpus ng entries sa lahat ng limang difficulty tiers, na mas binibigyang-bigat ang tiers 2–4:

| Tier | Description | Target Distribution |
|------|-------------|-------------------|
| 1 — Basic vocabulary | Single words, common greetings, numbers | 10–15% |
| 2 — Simple sentences | SVO, present tense | 25–30% |
| 3 — Moderate complexity | Past/future tense, possessives, animacy | 30–35% |
| 4 — Complex morphology | Obviation, passive, conjunct order, relative clauses | 15–20% |
| 5 — Advanced | Multi-clause, formal register, ceremonial, idiomatic | 5–10% |

### 3.4 Diagnostic Test Suite

Sinusubok ng diagnostic segment ang partikular na linguistic phenomena gamit ang **contrastive pairs**: isang tamang translation at isang minimally-different na maling translation. Kung mas mataas ang score na ibinibigay ng metric ng system sa tama, pasado ang test.

Para sa polysynthetic languages, dapat i-target ng diagnostic suite ang:

| Phenomenon | Example (Cree) | What It Tests |
|-----------|----------------|--------------|
| **Animacy agreement** | atim (AN) vs. maskisin (IN) — magkaibang verb forms | Alam ba ng system kung aling nouns ang animate? |
| **Obviation** | Proximate vs. obviative third person | Nasusubaybayan ba nito ang third-person hierarchy? |
| **Inverse marking** | Direct vs. inverse verb forms | Nahahawakan ba nito ang patient-outranks-agent? |
| **Conjunct/Independent** | Main clause vs. subordinate clause verb order | Ginagamit ba nito ang tamang verb paradigm? |
| **Inclusive/Exclusive** | "We (including you)" vs. "We (excluding you)" | Nakikilala ba nito ang first-person plural forms? |

Para sa ibang language families, tukuyin ang 3–5 pinaka-diagnostic na phenomena na nagpapakilala sa competent mula sa incompetent translation. Mahalaga rito ang linguistic expertise ng department — ito ang mga test na tanging specialist ang makaaalam kung paano isulat.

### 3.5 Ano ang HINDI Namin Gusto

| Anti-Pattern | Bakit |
|-------------|-----|
| **Bible-only text** | Archaic register, liturgical vocabulary, formulaic structure. Sinuri ng OMT-1600 ang 1,560 wika sa ganitong paraan — sinasadya naming iwasan ito. |
| **Synthetic evaluation pairs** | Pinapawalang-saysay ng LLM-generated references ang layunin ng evaluation. Dapat human-authored ang reference. |
| **Single-register corpora** | Pawang formal, o pawang conversational. Sumasaklaw ang real-world translation sa maraming register. |
| **Difficulty-1-only** | Hindi sumusubok ng translation ang single words at greetings — vocabulary lookup ang sinusubok ng mga ito. |
| **Machine-translated references** | Circular ang paggamit ng Google Translate output bilang "reference". |
| **Sentences with no context tag** | Kailangan naming malaman ang communicative function para sa diagnostic analysis. |

---

## 4. Cryptographic Sealing at Sandbox Testing {#4-cryptographic-sealing-and-sandbox-testing}

### 4.1 Bakit Ise-seal ang Test Set?

Karaniwang inilalathala nang bukas ng conventional ML benchmarks ang test sets. Kapag nalathala na, kalaunan ay masasanay ang frontier LLMs sa mga ito (sinadya man o sa pamamagitan ng web scraping), kaya nagiging hindi maaasahan ang scores. Para sa Indigenous language data, may karagdagang alalahanin: maaaring magamit ang nalathalang linguistic data nang walang consent ng community.

Tinitiyak ng sealing ang:
- **Integridad ng test set:** Hindi maaaring mag-overfit ang methods sa data na hindi pa nila kailanman nakita
- **Soberanya ng datos:** Kinokontrol ng community kung sino ang mage-evaluate laban sa kanilang data
- **Perpetual freshness:** Hindi kailanman nakokontamina ang test set

### 4.2 Paano Gumagana ang Sandbox Testing

```
Developer workflow:
  1. Developer builds a translation method using the PUBLIC development corpus
  2. Developer tests locally against the development segment (unlimited, self-serve)
  3. When ready, developer submits their complete method (code + config + coaching data)
  4. Governance org installs the method in the evaluation sandbox
  5. Sandbox runs the method against the SEALED gold-standard test set
  6. Only scores are returned to the developer
  7. Developer never sees the source sentences or reference translations

The sandbox:
  - Runs on governance-controlled infrastructure
  - Has selective network access (LLM APIs only, no exfiltration)
  - Produces a tamper-proof run card (SHA-256 hash of all inputs and outputs)
  - Logs all execution for audit purposes
  - Can be inspected by the governance org at any time
```

### 4.3 Key Management

Hinahati ang encryption key para sa sealed test set gamit ang Shamir Secret Sharing na may 2-of-3 threshold:

| Share Holder | Role | Revocation Power |
|-------------|------|-----------------|
| **Community governance org** | Pangunahing custodian | Maaaring mag-revoke ng evaluation access nang unilateral |
| **Academic department partner** | Co-custodian | Maaaring lumahok sa key reconstruction |
| **Champollion project** | Escrow | Hindi kayang i-access ang data nang mag-isa; tinitiyak ang continuity kung maging unavailable ang ibang parties |

Alinmang 2 sa 3 shares ang makapag-reconstruct ng key. Ibig sabihin nito:
- Maa-access ng community + department ang data nang walang Champollion
- Maa-access ng community + Champollion ang data nang wala ang department
- HINDI KAILANMAN maa-access ng Champollion lamang ang data

### 4.4 Hash Manifests

Kapag na-seal ang corpus, isang **hash manifest** ang inilalathala sa public Git commit:

```json
{
  "corpus_id": "crk-ualberta-v1",
  "seal_date": "2026-09-15T00:00:00Z",
  "segments": {
    "development": {
      "entry_count": 200,
      "sha256": "a3f7c...",
      "access": "public"
    },
    "gold_standard": {
      "entry_count": 100,
      "sha256": "b8d2e...",
      "access": "sealed",
      "key_scheme": "shamir-2-of-3"
    },
    "held_out": {
      "entry_count": 20,
      "sha256": "c9e4f...",
      "access": "sealed",
      "key_scheme": "shamir-2-of-3"
    },
    "diagnostic": {
      "entry_count": 30,
      "sha256": "d1a3b...",
      "access": "public"
    }
  },
  "total_entries": 350,
  "manifest_sha256": "e2b5c..."
}
```

Pinatutunayan nito:
- Umiiral ang corpus sa isang partikular na petsa
- Mayroon itong kilalang laki at istruktura
- Ang anumang pagbabago sa sealed segments ay sisira sa hash chain
- Mave-verify ng community na hindi pinakialaman ang kanilang data

---

## 5. Ano ang Makukuha ng Department

### 5.1 Research Infrastructure

| Asset | Description |
|-------|------------|
| **Evaluation harness** | Isang gumagana at nasubok na evaluation framework para sa kanilang wika — nakakatipid ng buwan-buwang tool-building |
| **LYSS metrics** | Language-specific evaluation metrics (LYSS-fst, LYSS-eq, LYSS-sem) na configured para sa kanilang wika — kung may FST at dictionary resources |
| **Leaderboard** | Isang public, live leaderboard na nagpapakita ng state of the art para sa kanilang language pair |
| **Baseline benchmark** | 12-model sweep na nagbibigay ng agarang, publishable baselines |
| **Diagnostic test suite** | Naka-target na tests para sa partikular na linguistic phenomena — reusable para sa ibang evaluations |

### 5.2 Publications

Sinusuportahan ng corpus construction at evaluation results ang maraming publication:

| Paper | Venue | Department Role |
|-------|-------|-----------------|
| Corpus construction methodology | LREC, ComputEL | Lead o co-author |
| Baseline evaluation results | ACL, EMNLP | Co-author |
| LYSS metric validation | WMT Metrics Shared Task | Co-author |
| Diagnostic test suite design | SIGMORPHON, NAACL | Lead o co-author |
| Language-specific NLP resources | Language-specific venues | Lead author |

### 5.3 Grant Positioning

Nagbibigay ang partnership ng kongkretong outputs para sa grant proposals:

- "Open-source evaluation infrastructure for [language] MT" — demonstrable deliverable
- "Cryptographic data sovereignty for Indigenous linguistic data" — novel, publishable
- "Community-governed benchmark with live leaderboard" — ongoing impact metric
- "Independent evaluation of OMT-1600 / Google Translate for [language]" — timely, high-visibility

### 5.4 Community Impact

- Nagkakaroon ang language community ng **independent evaluation capability** — maaari nilang tasahin kung talagang gumagana ang anumang MT system (Google, Meta, o custom) para sa kanilang wika
- **Kinokontrol ng community ang test data** sa pamamagitan ng cryptographic key custody
- Ang anumang methods na napatunayan sa pamamagitan ng benchmark ay **naglilipat ng pagmamay-ari** sa community (tingnan ang Benchmark Spec §8.3)
- Dumadaloy sa community ang revenue mula sa deployed methods (90/10 split)

### 5.5 Ano ang Gastos sa Department

| Component | Estimated Cost | Who Pays |
|-----------|---------------|----------|
| Oras ng PI/postdoc (design, oversight) | ~40 oras | Department (o grant-funded) |
| Speaker compensation (translation) | $2,500–6,000 | Grant-funded o Champollion-funded |
| Speaker compensation (review) | $500–1,500 | Grant-funded o Champollion-funded |
| Oras ng research coordinator | ~20 oras | Department |
| **Engineering, infrastructure, harness** | **$0** | **Champollion project** |

Ibinibigay namin ang lahat ng engineering, harness configuration, LYSS metric setup, leaderboard integration, at patuloy na infrastructure nang walang gastos sa department. Ang kontribusyon ng department ay linguistic expertise at access sa speakers.

---

## 6. Timeline

| Phase | Duration | Key Milestone |
|-------|----------|--------------|
| 1: Corpus Design | 2–4 linggo | Naaprubahan ang design document |
| 2: Source Sentences + Translation | 4–8 linggo | Nakumpleto ang raw corpus |
| 3: Quality Assurance | 2–4 linggo | Cross-reviewed, schema-validated |
| 4: Sealing | 1 linggo | Na-seal ang gold-standard, nalathala ang hash manifest |
| 5: Integration | 1–2 linggo | Live ang wika sa leaderboard na may baselines |
| **Total** | **10–19 linggo** | **Live leaderboard na may sealed evaluation** |

---

## 7. Paano Magsimula {#7-how-to-get-started}

1. **Makipag-ugnayan po sa amin** — [project email/contact]. Mag-iiskedyul kami ng 30-minutong tawag upang talakayin ang inyong wika, available resources, at partnership logistics.

2. **Ibinibigay namin ang:**
   - Dokumentong ito
   - Corpus schema at validation tools
   - Mga halimbawa mula sa aming umiiral na Cree (CRK) corpus
   - Draft corpus design template

3. **Ibinibigay ninyo ang:**
   - Isang PI o postdoc na mangunguna sa linguistic work
   - Access sa bilingual speakers (o planong mag-recruit sa kanila)
   - Impormasyon tungkol sa available resources (FST, dictionary, existing corpora)
   - Institutional approval para sa data governance (OCAP® compliance o katumbas)

4. **Co-design po natin ang corpus** — domain selection, difficulty distribution, diagnostic tests, timeline, at budget.

5. **Magsisimula ang trabaho.** Nagche-check in kami lingguhan. May buong autonomy ang department sa linguistic decisions; kami ang hahawak ng lahat ng engineering.

---

## 8. Mga Madalas Itanong

### "Mayroon na kaming parallel corpus. Maaari ba namin itong gamitin?"

Oo — kung malinaw ang provenance ng corpus, human-authored ito, at pinahihintulutan ng license ang paggamit sa evaluation. Tutulungan namin kayong i-format ito sa aming schema, magdagdag ng nawawalang metadata, at i-integrate ito. Maaaring lubos na pabilisin ng umiiral na corpora ang timeline (laktawan ang Phase 2 o bawasan ito sa isang gap-fill exercise).

### "Wala kaming FST para sa aming wika."

Ayos lamang iyon. Nangangailangan ang LYSS-fst (morphological validity) ng FST, ngunit gumagana ang harness nang wala ito gamit ang Profile B weights (chrF++, BLEU, COMET, behavioral metrics). Kung may GiellaLT FST para sa kaugnay na wika, maaari namin itong ma-adapt. Kung wala, nagbibigay pa rin ang corpus ng mahalagang evaluation — wala lamang morphological validity gate.

### "Gumagamit ang aming speakers ng non-Latin script."

Ganap itong sinusuportahan. Kaya ng corpus schema ang anumang Unicode script. Nagdisenyo kami para sa SRO (Standard Roman Orthography) at syllabics para sa Cree, ngunit gumagana ang parehong infrastructure para sa Devanagari, Arabic script, CJK, Ethiopic, o anumang iba pang writing system.

### "Paano ang dialect variation?"

I-tag ito. Kasama sa corpus entry schema ang `notes` field para sa dialectal information. Kung maraming dialect ang kinakatawan, idokumento ang mga ito. Maaaring i-configure ang equivalence classes ng linter (LYSS-eq) upang tanggapin ang dialectal variants bilang equivalent. Maaaring magsama ang diagnostic test suite ng dialect-specific contrasts.

### "Sino ang may-ari ng corpus?"

Ang language community, sa pamamagitan ng governance organization. Kinikilala ang department bilang research partner. Hawak ng Champollion ang isang escrow key share para sa operational continuity ngunit hindi nito maa-access ang sealed data nang mag-isa. Inilalathala ang development segment sa ilalim ng Creative Commons license na tinutukoy ng community.

### "Paano kung nais naming huminto?"

Maaaring i-revoke ng community ang evaluation access anumang oras sa pamamagitan ng pagtangging i-reconstruct ang encryption key. Hindi kailanman na-e-expose ang sealed data. Ang development segment, na nalathala na, ay mananatiling public sa ilalim ng license nito. Ang research outputs ng department (publications, presentations) ay mananatiling sa kanila anuman ang mangyari.

### "Paano kung wala pang governance organization?"

Maaari kaming magsimula sa Phases 1–3 (corpus design, creation, QA) nang walang governance org. Nangangailangan ang sealing (Phase 4) ng pagtukoy ng key custodian. Pansamantala, maaaring magsilbi ang department bilang co-custodian kasama ang Champollion project, na may pag-unawang ililipat ang custody sa community governance org kapag naitatag na ito.

---

## Appendix: Tagging vs. Corpus Construction

Saklaw ng dokumentong ito ang **corpus construction** — paglikha ng parallel text pairs na bumubuo sa evaluation ground truth. Ang tagging (morphological annotation, interlinear glossing, FST tag strings) ay hiwalay na gawain na nagpapayaman sa corpus ngunit hindi kinakailangan para sa basic evaluation.

| Activity | Required? | What It Enables |
|----------|-----------|-----------------|
| **Corpus construction** (dokumentong ito) | ✅ Required | Basic evaluation: chrF++, exact match, COMET, behavioral metrics |
| **FST coverage checking** | 🟡 Optional | LYSS-fst morphological validity metric |
| **Morphological annotation** | 🟡 Optional | `morphological_accuracy` metric (Scoring Spec §2.2) |
| **Linter equivalence rules** | 🟡 Optional | LYSS-eq equivalent match metric |
| **Semantic validator rules** | 🟡 Optional | LYSS-sem semantic validation metric |
| **Speaker quality ratings** | Hiwalay na gawain | Metric validation (tingnan ang [Protocol sa Pagpapatunay ng Speaker](/docs/specifications/speaker-validation)) |

Saklaw ng hiwalay na mga dokumento ang tagging at speaker validation at maaari itong magpatuloy kasabay ng o pagkatapos ng corpus construction.