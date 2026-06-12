---
sidebar_position: 9
title: "Estratehiya sa Pakikipagsosyo para sa Corpus"
slug: '/specifications/corpus-partnership'
---
# Estratehiya sa Pakikipagpartner para sa Corpus: Pagtatatag ng mga Corpus ng Ebalwasyon sa Pamamagitan ng mga Departamento ng Akademikong Lingguwistika

> **Layunin.** Ibinibigay ng dokumentong ito ang kumpletong workflow para sa pagtatatag ng corpus ng ebalwasyon para sa machine translation sa pamamagitan ng pakikipagpartner sa isang departamento ng lingguwistika. Sinasaklaw nito kung ano ang kailangan naming ihatid ng departamento, ano ang dapat na anyo ng corpus, paano ito isinasailalim sa cryptographic sealing, paano gumagana ang sandbox evaluation, at ano ang matatanggap ng departamento kapalit nito. Ito ang dokumentong dadalhin ninyo sa isang pulong kasama ang posibleng akademikong partner.
>
> **Audience.** Mga pinuno ng departamento, principal investigators, research coordinators, at mga direktor ng programang pangwikang Katutubo sa mga unibersidad na may aktibong mga programa sa dokumentasyong pangwika o NLP.
>
> **Mga kasamang dokumento:**
> - [Protocol sa Pagpapatunay ng Tagapagsalita](/docs/specifications/speaker-validation) — ang hiling para sa mga bilingual na tagapagsalita na *magmarka* ng umiiral na mga salin (quality rating, linter validation, FST review)
> - [Espesipikasyon ng Benchmark](/docs/specifications/benchmark) — ang buong teknikal na espesipikasyon para sa corpora, run cards, at mga protocol ng ebalwasyon
> - [Soberanya sa Datos](/docs/sovereignty/data-sovereignty) — OCAP®, CARE, at kung bakit mahalaga ang paglilipat ng pagmamay-ari
>
> Huling na-update: 2026-06-07

---

## 1. Ano ang Nalilikha ng Partnership na Ito

Isang **selyadong corpus ng ebalwasyon**: isang curated na hanay ng mga parallel text pair (source language → target language) na nagiging ground truth para sa pagsukat ng kalidad ng machine translation. Sinusubok ang mga pamamaraan laban sa corpus na ito sa isang sandbox — hindi kailanman nakikita ng mga developer ang test data.

Lumilikha ang partnership ng tatlong artifact:

| Artifact | Ano Ito | Sino ang May Kontrol Dito |
|----------|-----------|-----------------|
| **Development corpus** | 100–200+ pampublikong parallel text pair para sa pagpapaunlad ng pamamaraan | Inilalathala nang bukas (CC BY-NC-SA 4.0 o katumbas) |
| **Gold-standard test set** | 50–150 lihim na parallel text pair para sa opisyal na ebalwasyon | Community governance org (cryptographically sealed) |
| **Diagnostic test suite** | 10–50 naka-target na contrastive pair na sumusubok sa partikular na mga penomenong lingguwistiko | Inilalathala nang bukas |

Pinahihintulutan ng development corpus ang sinuman na bumuo ng mga pamamaraan ng pagsasalin. Tinitiyak ng gold-standard set na nasusubok nang tapat ang mga pamamaraang iyon. Nahuhuli ng diagnostic suite ang partikular na mga failure mode (hal., "kaya ba ng sistemang ito ang obviation?").

---

## 2. Ano ang Kailangang Gawin ng Departamento

### Phase 1: Disenyo ng Corpus (2–4 na linggo, oras ng mananaliksik)

**Lead:** PI o postdoc na may kadalubhasaan sa target language.

1. **Pumili ng mga domain ng source material.** Pumili ng 4–6 na real-world domain kung saan talagang kailangan ng pagsasalin ng pamayanang pangwika. Sinusuportahan ng aming taxonomy ang 16 na domain (tingnan ang Benchmark Spec §2.7):

   | Prayoridad | Domain | Bakit |
   |----------|--------|-----|
   | 🔴 Mataas | `edu` — Educational | Mga textbook, curricula — direktang pangangailangan ng komunidad |
   | 🔴 Mataas | `gov` — Government | Mga dokumento ng band council, polisiya — praktikal na pang-araw-araw na pangangailangan |
   | 🔴 Mataas | `medical` — Health | Mga clinic intake form, impormasyong pangkalusugan — kritikal sa kaligtasan |
   | 🟡 Katamtaman | `conv` — Conversational | Pang-araw-araw na pananalita — nagtatatag ng baseline fluency |
   | 🟡 Katamtaman | `legal` — Legal | Mga dokumento ng karapatan, treaty — kahalagahan sa komunidad |
   | 🟢 Mas Mababa | `literary` — Literary/Cultural | Mga kuwento, oral histories — pangangalagang kultural |

2. **Mag-draft ng dokumento ng disenyo ng corpus** na tumutukoy sa:
   - Target na laki bawat segment (development, gold_standard, diagnostic)
   - Distribusyon ng difficulty tier (tingnan ang §3.3 sa ibaba)
   - Saklaw ng register at domain
   - Pamantayan sa pagpili ng source sentence (walang synthetic text, hindi Bible-only)
   - Plano sa pagre-recruit ng tagapagsalita

3. **Isumite sa amin ang disenyo para sa review.** Iva-validate namin ito laban sa corpus schema (Benchmark Spec §2) at magbabalik ng feedback sa loob ng 1 linggo.

### Phase 2: Paglikha ng Source Sentence (4–8 na linggo, oras ng tagapagsalita)

**Lead:** Research coordinator na nakikipagtulungan sa mga bilingual na tagapagsalita.

1. **Bumuo o pumili ng mga source sentence** sa kabuuan ng mga nakaplanong domain at difficulty tier. Maaaring manggaling ang mga source sa:
   - Umiiral na nailathalang bilingual na materyales (mga textbook, dokumento ng pamahalaan)
   - Bagong elicited na mga pangungusap na idinisenyo upang saklawin ang partikular na mga penomenong lingguwistiko
   - Inangkop mula sa real-world na mga dokumento (mga agenda ng band council, clinic form, materyales na pang-edukasyon)

2. **Bawat source sentence ay dapat may:**
   - Domain tag (mula sa 16-code taxonomy)
   - Register tag (conversational, formal, technical, ceremonial, educational)
   - Context tag (greeting, declaration, question, instruction, narrative, label, error)
   - Tinatayang difficulty tier (1–5, tingnan ang §3.3)
   - Provenance tag (textbook, elicited, corpus, gold_standard)

3. **Isalin ang bawat source sentence** sa target language, na isinasagawa ng mga bilingual na tagapagsalita. Mahalaga ang maraming reference translation bawat entry ngunit hindi kinakailangan.

4. **Opsyonal, magdagdag ng morphological analysis** para sa bawat reference translation:
   - Interlinear gloss (morpheme-by-morpheme breakdown)
   - FST tag string (kung may FST para sa wika)
   - Mga tala ng tagasalin tungkol sa mga dialectal variant, ambiguity, o cultural context

### Phase 3: Quality Assurance (2–4 na linggo)

**Lead:** Lingguwistang may kadalubhasaan sa target language.

1. **Cross-review.** Dapat i-review ang bawat salin ng hindi bababa sa isang karagdagang bilingual na tagapagsalita na hindi gumawa ng orihinal na salin. Tinitingnan ng reviewer:
   - Tumpak ba ang salin?
   - Natural ba itong pakinggan?
   - Tama ba ang difficulty rating?
   - May mga katanggap-tanggap bang variant na dapat itala?

2. **Patakbuhin sa aming schema validator.** Nagbibigay kami ng script na nagva-validate ng corpus laban sa entry schema (Benchmark Spec §2.2). Tinitingnan nito:
   - Naroon ang mga kinakailangang field
   - Valid ang mga domain code
   - Ang difficulty tiers ay mga integer na 1–5
   - Walang duplicate na ID
   - Character encoding (UTF-8 NFC normalization)

3. **Kung may FST para sa wika,** patakbuhin dito ang mga reference translation. Dapat FST-valid ang bawat salita sa reference. Ang mga salitang hindi (loanwords, neologisms, proper nouns) ay dapat idokumento sa isang allowlist.

### Phase 4: Segmentation at Sealing (1 linggo, aming engineering)

**Lead:** Champollion team, may review ng departamento.

1. **Stratified split.** Hinahati namin ang corpus sa mga segment gamit ang deterministic random sampling (nakadokumento ang seed, reproducible):

   | Segment | Target na Laki | Access |
   |---------|------------|--------|
   | `development` | 60% ng mga entry (min 100) | Pampubliko |
   | `gold_standard` | 30% ng mga entry (min 50) | Lihim, sealed |
   | `held_out` | 10% ng mga entry (min 10) | Lihim, sealed, hindi kailanman gagamitin hanggang ma-activate |

   Pinananatili ng split ang distribusyon ng difficulty tier (stratified sampling) upang magkaroon ang bawat segment ng proporsyonal na representasyon sa kabuuan ng mga tier.

2. **Cryptographic sealing** ng gold_standard at held_out na mga segment:

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

3. **Ang development segment** ay kino-commit sa pampublikong repository at inilalathala nang may buong licensing.

4. **Ang diagnostic segment** ay pampubliko rin — sinusubok nito ang partikular na mga penomenong lingguwistiko (tingnan ang §3.4).

### Phase 5: Integration at Launch (1–2 linggo, aming engineering)

1. **Harness configuration.** Idinaragdag namin ang wika sa evaluation harness:
   - Ginawa o na-verify ang language card
   - Narehistro ang corpus sa dataset registry
   - Na-configure ang LYSS metrics (LYSS-fst kung may FST, LYSS-eq kung may linter rules)
   - Napili ang default scoring profile (Profile A kung may FST, Profile B kung wala)

2. **Baseline benchmark.** Nagpapatakbo kami ng 12-model sweep laban sa development segment upang punuan ang leaderboard ng mga paunang score.

3. **Pampublikong anunsyo.** Lumilitaw ang wika sa Arena leaderboard na may live na development-segment benchmark. Kinikilala ang departamento bilang corpus partner.

---

## 3. Ano ang Dapat na Anyo ng Corpus

### 3.1 Format

Ang bawat corpus file ay isang JSON document na sumusunod sa schema sa Benchmark Spec §2.1–§2.2:

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

| Segment | Minimum na Entry | Inirerekomenda |
|---------|----------------|-------------|
| `development` | 100 | 200–300 |
| `gold_standard` | 50 | 100–150 |
| `diagnostic` | 10 | 30–50 |
| `held_out` | 10 | 20–30 |
| **Kabuuan** | **170** | **350–530** |

### 3.3 Difficulty Distribution

Dapat magsama ang corpus ng mga entry sa lahat ng limang difficulty tier, na may bigat sa tiers 2–4:

| Tier | Paglalarawan | Target na Distribusyon |
|------|-------------|-------------------|
| 1 — Basic vocabulary | Iisang salita, karaniwang pagbati, mga numero | 10–15% |
| 2 — Simple sentences | SVO, present tense | 25–30% |
| 3 — Moderate complexity | Past/future tense, possessives, animacy | 30–35% |
| 4 — Complex morphology | Obviation, passive, conjunct order, relative clauses | 15–20% |
| 5 — Advanced | Multi-clause, formal register, ceremonial, idiomatic | 5–10% |

### 3.4 Diagnostic Test Suite

Sinusubok ng diagnostic segment ang partikular na mga penomenong lingguwistiko gamit ang **contrastive pairs**: isang tamang salin at isang minimally-different na maling salin. Kung mas mataas ang ibinigay na score ng metric ng isang sistema sa tama, pumapasa ang test.

Para sa mga polysynthetic language, dapat i-target ng diagnostic suite ang:

| Penomenon | Halimbawa (Cree) | Ano ang Sinusubok Nito |
|-----------|----------------|--------------|
| **Animacy agreement** | atim (AN) vs. maskisin (IN) — magkakaibang verb form | Alam ba ng sistema kung aling mga noun ang animate? |
| **Obviation** | Proximate vs. obviative third person | Nasusubaybayan ba nito ang third-person hierarchy? |
| **Inverse marking** | Direct vs. inverse verb forms | Nahahawakan ba nito ang patient-outranks-agent? |
| **Conjunct/Independent** | Main clause vs. subordinate clause verb order | Ginagamit ba nito ang tamang verb paradigm? |
| **Inclusive/Exclusive** | "Tayo (kasama ka)" vs. "Kami (hindi ka kasama)" | Natutukoy ba nito ang pagkakaiba ng first-person plural forms? |

Para sa ibang mga pamilya ng wika, tukuyin ang 3–5 pinakadiagnostic na penomenon na naghihiwalay sa mahusay sa hindi mahusay na pagsasalin. Mahalaga rito ang kadalubhasaan ng departamento sa lingguwistika — ito ang mga test na tanging espesyalista lamang ang makaaalam kung paano isusulat.

### 3.5 Ano ang HINDI Namin Nais

| Anti-Pattern | Bakit |
|-------------|-----|
| **Bible-only text** | Archaic register, liturgical vocabulary, formulaic structure. Sinuri ng OMT-1600 ang 1,560 wika sa ganitong paraan — sinasadya naming iwasan ito. |
| **Synthetic evaluation pairs** | Pinapawalang-saysay ng LLM-generated references ang layunin ng ebalwasyon. Dapat human-authored ang reference. |
| **Single-register corpora** | Pawang formal, o pawang conversational. Sumasaklaw ang real-world na pagsasalin sa maraming register. |
| **Difficulty-1-only** | Hindi sinusubok ng iisang salita at pagbati ang pagsasalin — sinusubok nila ang vocabulary lookup. |
| **Machine-translated references** | Circular ang paggamit ng Google Translate output bilang isang "reference". |
| **Mga pangungusap na walang context tag** | Kailangan naming malaman ang communicative function para sa diagnostic analysis. |

---

## 4. Cryptographic Sealing at Sandbox Testing

### 4.1 Bakit Ise-seal ang Test Set?

Karaniwang inilalathala nang bukas ng mga conventional ML benchmark ang mga test set. Kapag nailathala na, kalaunan ay matetrain dito ang frontier LLMs (sinadya man o sa pamamagitan ng web scraping), kaya nagiging hindi maaasahan ang mga score. Para sa datos ng mga wikang Katutubo, may karagdagang alalahanin: maaaring gamitin ang nailathalang datos lingguwistiko nang walang pahintulot ng komunidad.

Tinitiyak ng sealing ang:
- **Integridad ng test set:** Hindi maaaring mag-overfit ang mga pamamaraan sa datos na hindi pa nila kailanman nakita
- **Soberanya sa datos:** Kontrolado ng komunidad kung sino ang nag-eevaluate laban sa kanilang datos
- **Pangmatagalang freshness:** Hindi kailanman nakokontamina ang test set

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
| **Community governance org** | Pangunahing custodian | Maaaring unilateral na mag-revoke ng evaluation access |
| **Academic department partner** | Co-custodian | Maaaring lumahok sa key reconstruction |
| **Champollion project** | Escrow | Hindi makaa-access ng datos nang mag-isa; tinitiyak ang continuity kung maging unavailable ang ibang partido |

Anumang 2 sa 3 share ang nakapag-reconstruct ng key. Ibig sabihin nito:
- Maa-access ng komunidad + departamento ang datos nang wala ang Champollion
- Maa-access ng komunidad + Champollion ang datos nang wala ang departamento
- HINDI KAILANMAN maa-access ng Champollion nang mag-isa ang datos

### 4.4 Hash Manifests

Kapag na-seal ang corpus, inilalathala ang isang **hash manifest** sa isang pampublikong Git commit:

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

Pinatutunayan nito na:
- Umiiral ang corpus sa isang partikular na petsa
- Mayroon itong kilalang laki at estruktura
- Anumang pagbabago sa sealed segments ay sisira sa hash chain
- Mave-verify ng komunidad na hindi pinakialaman ang kanilang datos

---

## 5. Ano ang Matatanggap ng Departamento

### 5.1 Research Infrastructure

| Asset | Paglalarawan |
|-------|------------|
| **Evaluation harness** | Isang gumagana at nasubok na evaluation framework para sa kanilang wika — nakatitipid ng buwan ng paggawa ng tool |
| **LYSS metrics** | Language-specific evaluation metrics (LYSS-fst, LYSS-eq, LYSS-sem) na naka-configure para sa kanilang wika — kung may mga resource na FST at dictionary |
| **Leaderboard** | Isang pampubliko at live na leaderboard na nagpapakita ng state of the art para sa kanilang language pair |
| **Baseline benchmark** | 12-model sweep na nagbibigay ng agarang, nailalathalang mga baseline |
| **Diagnostic test suite** | Naka-target na mga test para sa partikular na mga penomenong lingguwistiko — magagamit muli para sa ibang ebalwasyon |

### 5.2 Publications

Sinusuportahan ng corpus construction at mga resulta ng ebalwasyon ang maraming publication:

| Paper | Venue | Role ng Departamento |
|-------|-------|-----------------|
| Corpus construction methodology | LREC, ComputEL | Lead o co-author |
| Baseline evaluation results | ACL, EMNLP | Co-author |
| LYSS metric validation | WMT Metrics Shared Task | Co-author |
| Diagnostic test suite design | SIGMORPHON, NAACL | Lead o co-author |
| Language-specific NLP resources | Language-specific venues | Lead author |

### 5.3 Grant Positioning

Nagbibigay ang partnership ng kongkretong outputs para sa mga grant proposal:

- "Open-source evaluation infrastructure for [language] MT" — demonstrable deliverable
- "Cryptographic data sovereignty for Indigenous linguistic data" — bago at mailalathala
- "Community-governed benchmark with live leaderboard" — ongoing impact metric
- "Independent evaluation of OMT-1600 / Google Translate for [language]" — napapanahon, mataas ang visibility

### 5.4 Epekto sa Komunidad

- Nagkakaroon ang pamayanang pangwika ng **independent evaluation capability** — masusuri nila kung talagang gumagana para sa kanilang wika ang anumang MT system (Google, Meta, o custom)
- **Kontrolado ng komunidad ang test data** sa pamamagitan ng cryptographic key custody
- Anumang pamamaraang napatunayan sa pamamagitan ng benchmark ay **maglilipat ng pagmamay-ari** sa komunidad (tingnan ang Benchmark Spec §8.3)
- Ang kita mula sa mga deployed method ay napupunta sa komunidad (90/10 split)

### 5.5 Ano ang Gastos sa Departamento

| Component | Tinatayang Gastos | Sino ang Magbabayad |
|-----------|---------------|----------|
| Oras ng PI/postdoc (disenyo, oversight) | ~40 oras | Departamento (o grant-funded) |
| Bayad sa tagapagsalita (pagsasalin) | $2,500–6,000 | Grant-funded o Champollion-funded |
| Bayad sa tagapagsalita (review) | $500–1,500 | Grant-funded o Champollion-funded |
| Oras ng research coordinator | ~20 oras | Departamento |
| **Engineering, infrastructure, harness** | **$0** | **Champollion project** |

Ibinibigay namin ang lahat ng engineering, harness configuration, LYSS metric setup, leaderboard integration, at ongoing infrastructure nang walang gastos sa departamento. Ang kontribusyon ng departamento ay kadalubhasaang lingguwistiko at access sa mga tagapagsalita.

---

## 6. Timeline

| Phase | Tagal | Pangunahing Milestone |
|-------|----------|--------------|
| 1: Disenyo ng Corpus | 2–4 na linggo | Naaprubahan ang design document |
| 2: Source Sentences + Translation | 4–8 na linggo | Nakumpleto ang raw corpus |
| 3: Quality Assurance | 2–4 na linggo | Cross-reviewed, schema-validated |
| 4: Sealing | 1 linggo | Na-seal ang Gold-standard, nailathala ang hash manifest |
| 5: Integration | 1–2 linggo | Live ang wika sa leaderboard na may mga baseline |
| **Kabuuan** | **10–19 na linggo** | **Live na leaderboard na may sealed evaluation** |

---

## 7. Paano Magsimula

1. **Makipag-ugnayan sa amin** — [project email/contact]. Mag-iiskedyul kami ng 30 minutong tawag upang talakayin ang inyong wika, mga available na resource, at logistics ng partnership.

2. **Ibinibigay namin ang:**
   - Dokumentong ito
   - Corpus schema at mga validation tool
   - Mga halimbawa mula sa aming umiiral na Cree (CRK) corpus
   - Isang draft na template ng disenyo ng corpus

3. **Ibinibigay ninyo ang:**
   - Isang PI o postdoc na mangunguna sa gawaing lingguwistiko
   - Access sa mga bilingual na tagapagsalita (o plano upang i-recruit sila)
   - Impormasyon tungkol sa available resources (FST, dictionary, umiiral na corpora)
   - Institutional approval para sa data governance (OCAP® compliance o katumbas)

4. **Sama-sama nating idinidisenyo ang corpus** — pagpili ng domain, distribusyon ng difficulty, diagnostic tests, timeline, at budget.

5. **Magsisimula ang trabaho.** Nagche-check in kami linggu-linggo. May buong autonomy ang departamento sa mga desisyong lingguwistiko; kami ang hahawak ng lahat ng engineering.

---

## 8. Frequently Asked Questions

### "Mayroon na kaming parallel corpus. Maaari ba namin itong gamitin?"

Oo — kung malinaw ang provenance ng corpus, human-authored ito, at pinahihintulutan ng lisensya ang paggamit sa ebalwasyon. Tutulungan namin kayong i-format ito sa aming schema, idagdag ang nawawalang metadata, at i-integrate ito. Malaki ang maipapabilis ng umiiral na corpora sa timeline (laktawan ang Phase 2 o bawasan ito sa isang gap-fill exercise).

### "Wala kaming FST para sa aming wika."

Ayos lamang iyon. Nangangailangan ang LYSS-fst (morphological validity) ng FST, ngunit gumagana ang harness nang wala nito gamit ang Profile B weights (chrF++, BLEU, COMET, behavioral metrics). Kung may GiellaLT FST para sa kaugnay na wika, maaaring ma-adapt namin ito. Kung wala, nagbibigay pa rin ang corpus ng mahalagang ebalwasyon — wala nga lamang ang morphological validity gate.

### "Gumagamit ang aming mga tagapagsalita ng non-Latin script."

Ganap na sinusuportahan. Kayang hawakan ng corpus schema ang anumang Unicode script. Dinisenyo namin ito para sa SRO (Standard Roman Orthography) at syllabics para sa Cree, ngunit gumagana ang parehong infrastructure para sa Devanagari, Arabic script, CJK, Ethiopic, o anumang ibang writing system.

### "Paano ang dialect variation?"

I-tag ito. Kasama sa corpus entry schema ang field na `notes` para sa impormasyong dialectal. Kung kinakatawan ang maraming dialect, idokumento ang mga ito. Maaaring i-configure ang equivalence classes ng linter (LYSS-eq) upang tanggapin ang dialectal variants bilang equivalent. Maaaring magsama ang diagnostic test suite ng mga dialect-specific contrast.

### "Sino ang may-ari ng corpus?"

Ang pamayanang pangwika, sa pamamagitan ng governance organization. Kinikilala ang departamento bilang research partner. Humahawak ang Champollion ng escrow key share para sa operational continuity ngunit hindi nito maa-access ang sealed data nang mag-isa. Inilalathala ang development segment sa ilalim ng Creative Commons license na tinutukoy ng komunidad.

### "Paano kung nais naming tumigil?"

Maaaring i-revoke ng komunidad ang evaluation access anumang oras sa pamamagitan ng pagtangging i-reconstruct ang encryption key. Hindi kailanman nailalantad ang sealed data. Ang development segment, na nailathala na, ay nananatiling pampubliko sa ilalim ng lisensya nito. Ang mga research output ng departamento (publications, presentations) ay mananatiling sa kanila anuman ang mangyari.

### "Paano kung wala pang governance organization?"

Maaari tayong magsimula sa Phases 1–3 (disenyo ng corpus, paglikha, QA) nang walang governance org. Nangangailangan ang sealing (Phase 4) ng pagtukoy ng key custodian. Pansamantala, maaaring magsilbi ang departamento bilang co-custodian kasama ng Champollion project, na may pagkaunawang ililipat ang custody sa community governance org kapag naitatag na ito.

---

## Appendix: Tagging vs. Corpus Construction

Sinasaklaw ng dokumentong ito ang **corpus construction** — paglikha ng parallel text pairs na bumubuo sa evaluation ground truth. Ang tagging (morphological annotation, interlinear glossing, FST tag strings) ay hiwalay na aktibidad na nagpapayaman sa corpus ngunit hindi kinakailangan para sa basic evaluation.

| Activity | Required? | Ano ang Pinahihintulutan Nito |
|----------|-----------|-----------------|
| **Corpus construction** (dokumentong ito) | ✅ Required | Basic evaluation: chrF++, exact match, COMET, behavioral metrics |
| **FST coverage checking** | 🟡 Optional | LYSS-fst morphological validity metric |
| **Morphological annotation** | 🟡 Optional | `morphological_accuracy` metric (Scoring Spec §2.2) |
| **Linter equivalence rules** | 🟡 Optional | LYSS-eq equivalent match metric |
| **Semantic validator rules** | 🟡 Optional | LYSS-sem semantic validation metric |
| **Speaker quality ratings** | Hiwalay na aktibidad | Metric validation (tingnan ang [Protocol sa Pagpapatunay ng Tagapagsalita](/docs/specifications/speaker-validation)) |

Sinasaklaw ng magkakahiwalay na dokumento ang tagging at speaker validation at maaaring magpatuloy kasabay ng o pagkatapos ng corpus construction.