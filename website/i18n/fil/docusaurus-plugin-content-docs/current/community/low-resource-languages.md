---
sidebar_position: 5
title: "Suportahan ang Isang Low-Resource na Wika"
related:
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "The first step for an uncovered language"
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
  - label: "Plains Cree, the trading card"
    to: https://champollion.dev/trading-cards?q=crk
    kind: card
    note: "The proof-of-concept language, as a card"
---
# Suportahan ang isang Wikang Low-Resource

> **Executive Summary.** Isang komprehensibong gabay sa pagbuo ng machine translation para sa mga wikang low-resource at polysynthetic. Sinasaklaw nito kung bakit mahirap ang mga wikang ito (kompleksidad sa morpolohiya, kakaunting data, hallucination), mga umiiral na computational resource (ALTLab FST, GiellaLT, Apertium, UniMorph, EdTeKLA), 10+ estratehiya sa paglapit, ang champollion coaching system, at ang evaluation loop. Magsimula rito kung nais ninyong mag-ambag ng isang method para sa wikang kulang sa serbisyo.

:::info Status: Nasa Aktibong Pagpapaunlad
Kasalukuyang nasa pagpapaunlad ang suporta para sa Plains Cree (nêhiyawêwin). Ang mga tool, evaluation harness, at leaderboard na inilalarawan dito ay tunay at magagamit na ngayon, ngunit hindi pa nailalabas ang Cree translation pipeline. Kapag nailabas na ito, magsisilbi itong blueprint para sa iba pang polysynthetic at low-resource na wika na may FST infrastructure.
:::

## Ang Hindi Pa Nalulutas na Problema

Sinusuportahan ng Google Translate ang ~130 wika. Inaangkin ng Meta's OMT-1600 (Marso 2026) ang saklaw para sa 1,600 — ang pinakamalaking MT system na nailathala kailanman. Ngunit para sa ~1,300 wika sa kanilang pinakamababang resource tiers, ang kalidad ay mas mababa sa magagamit na threshold, pinangungunahan ng tekstong Bibliya ang training data, hindi available para i-download ang model weights, at walang independent evaluation o framework para sa community governance. Para sa natitirang ~5,400 wika, walang pretrained model na nakapaglalabas ng kahit anong output.

Malaki na ang ipinagbago ng landscape — namumuhunan na ngayon ang Big Tech sa saklaw para sa LRL. Ngunit ang saklaw ay hindi kalidad, at ang kalidad na walang independent verification ay hindi tiwala. Kailangan ng low-resource languages ang higit pa sa isang model na nagsasabing sakop sila nito — kailangan nila ng independent evaluation na may morphological validation, community-curated corpora, at governance na gumagalang sa sovereignty.

**Binuo ang champollion upang baguhin iyon.**

Ang [Method Leaderboard](https://champollion.dev/leaderboard) ay isang bukas na hamon: buuin ang pinakamahusay na translation method para sa wikang kulang sa serbisyo, patunayan ito gamit ang reproducible evaluation, at angkinin ang pinakamataas na score. Maaaring mag-ambag ang sinuman sa mundo — mga linguist, ML researcher, community language worker, estudyante, hobbyist. Hindi pa nalulutas ang problema. Narito na ang infrastructure. Naghihintay ang leaderboard.

---

## Bakit Ito Mahirap: Polysynthetic Morphology

Karamihan sa commercial MT systems ay idinisenyo para sa mga wikang tulad ng English, French, at Chinese — mga wikang ang mga salita ay relatibong maikli at ang mga pangungusap ay binubuo mula sa hiwa-hiwalay na token. Ngunit maraming Indigenous languages, kabilang ang Plains Cree, ay **polysynthetic**: maaaring i-encode ng iisang salita ang ipinapahayag ng English bilang isang buong pangungusap.

### Ang halimbawa sa Cree

Isaalang-alang ang salitang Plains Cree:

> **ê-kî-nitawi-kîskinwahamâkosiyân**
> *"noong pumunta ako sa paaralan"*

Iyan ay **isang salita**. Ine-encode nito ang tense (nakaraan), direksiyon (pagpunta sa), root (matuto), voice (passive/reflexive), at person (unang panauhang isahan). Ang LLM na pangunahing sinanay sa English ay walang likas na pagkaunawa sa ganitong uri ng morphological density.

Dumaragdag pa ang mga hamon:

| Hamon | Ano ang Ibig Sabihin Nito |
|-----------|--------------|
| **Kompleksidad sa morpolohiya** | Ang iisang verb root ay maaaring makabuo ng libo-libong valid na inflected forms sa pamamagitan ng prefixation, suffixation, at circumfixation |
| **Pagkakaibang animate/inanimate** | Ang mga pangngalan ay grammatically animate o inanimate — naaapektuhan nito ang verb conjugation, demonstratives, at pluralization. Hindi palaging sumusunod ang klasipikasyon sa biological animacy (*askiy* "lupa" ay animate; *maskisin* "sapatos" ay animate din) |
| **Obviation** | Niraranggo ang mga third-person reference ayon sa proximity/salience. Walang katumbas sa English ang pagkakaibang "proximate" at "obviative" |
| **Kakaunting training data** | Napakakaunting tekstong Plains Cree ang nakita ng mga LLM. Ang nakita nila ay maaaring naghalo ng mga dialect (Y-dialect, TH-dialect) o orthographies (SRO vs. syllabics) |
| **Mahinang commercial baseline** | Kasama sa OMT-1600 ang CRK sa R1 (Very Low Resource) tier na may Bible-domain training at karaniwang BPE tokenization. Hindi sinusuportahan ng Google Translate ang Cree. Ang independent evaluation na may morphological metrics ang nagbibigay-kahulugan sa mga baseline na ito. |

Nananatiling **bukas na suliraning pananaliksik** ang pagsasalin ng polysynthetic languages — kasama sa OMT-1600 ang polysynthetic languages ngunit gumagamit ito ng karaniwang BPE tokenization (256K vocabulary) na walang morphological awareness, ibig sabihin, dinudurog nito ang compositional words bilang walang-kahulugang byte fragments.

---

## Naunang Gawain: Paano Ito Nilapitan ng Iba

### Ang ALTLab FST

Ang pinakamahalagang computational resource para sa Plains Cree ay ang **finite-state transducer (FST)** na binuo ng [Alberta Language Technology Lab (ALTLab)](https://altlab.artsrn.ualberta.ca/) sa University of Alberta, sa pakikipagtulungan sa [Giellatekno](https://giellatekno.uit.no/) sa UiT The Arctic University of Norway.

Ang ALTLab FST ay isang **morphological analyzer at generator**: kapag binigyan ng inflected Cree word, maaari nitong i-decompose ito sa root at grammatical tags nito, at kapag binigyan ng root kasama ang tags, maaari nitong buuin ang tamang inflected form. Deterministic ito — walang neural network, walang hallucination, walang probability. Kung tinatanggap ng FST ang isang salita, ang salitang iyon ay morphologically valid.

Ito ang dahilan kung bakit sinusubaybayan ng champollion leaderboard ang **FST Acceptance Rate** bilang metric. Ang translation method na gumagawa ng mga salitang tinatanggihan ng FST ay gumagawa ng morphologically invalid na Cree — anuman ang sinasabi ng chrF++ score.

**Mahahalagang ALTLab resource:**
- [itwêwina](https://itwewina.altlab.app/) — isang intelligent Plains Cree–English dictionary na pinapatakbo ng FST
- [Morphodict](https://github.com/UAlbertaALTLab/morphodict) — open-source na morphologically-aware dictionary platform
- [crk-db](https://github.com/UAlbertaALTLab/crk-db) — Plains Cree lexical database
- [21st Century Tools for Indigenous Languages](https://21c.tools/) — ang mas malawak na konteksto ng proyekto

### Pandaigdigang FST at Morphological Registries

Hindi lamang Plains Cree ang wikang may mataas na kalidad na FST infrastructure. Kung nais ninyong bumuo ng translation pipelines para sa iba pang low-resource o morphologically complex na wika, maaari ninyong gamitin ang mga matatag nang pandaigdigang hub na ito:

* **[GiellaLT / Giellatekno](https://giellalt.github.io/) (UiT The Arctic University of Norway):** Ang pinakamalaking repository ng open-source FST morphological analyzers at generators, na sumasaklaw sa mahigit 100 wika. Kabilang sa focus areas ang Sámi languages (`sme`, `smj`, `sma`, atbp.), Uralic languages (Komi, Erzya, Udmurt, atbp.), at iba pang minority/indigenous languages. Nagho-host sila ng public processed text corpora (`corpus-xxx`) sa kanilang [GitHub Organization](https://github.com/giellalt/).
* **[The Apertium Project](https://www.apertium.org/):** Isang open-source rule-based machine translation platform. Pinananatili ng Apertium ang highly optimized FST morphological analyzers (gamit ang `lttoolbox` at `hfst`) at bilingual dictionaries para sa dose-dosenang wika, kabilang ang malaking suite ng Turkic languages (Kazakh, Tatar, Kyrgyz, atbp.) at minority European languages. Pampubliko ang lahat ng resource sa [GitHub ng Apertium](https://github.com/apertium).
* **[UniMorph (Universal Morphology)](https://unimorph.github.io/):** Isang collaborative project na nagbibigay ng standardized morphological paradigms para sa mahigit 150 wika. Naka-host ang dataset sa Hugging Face sa [unimorph/universal_morphologies](https://huggingface.co/datasets/unimorph/universal_morphologies). Kung walang available na compiled FST binary para sa isang wika, maaaring gamitin ang UniMorph tables bilang static database lookup gate.
* **[National Research Council Canada (NRC)](https://nrc-digital-repository.canada.ca/):** Nag-aalok ng mga tool para sa Canadian Indigenous languages, kabilang ang **Uqailaut** Inuktitut FST morphological analyzer at ang napakalaking **Nunavut Hansard Parallel Corpus** (1.3M aligned English-Inuktitut sentence pairs).

### Ang EdTeKLA Corpus

Ang [EdTeKLA research group](https://spaces.facsci.ualberta.ca/edtekla/) (na nasa UAlberta rin) ay nakapagtipon ng Plains Cree language corpus mula sa educational materials, audio transcriptions, at community sources. Ang champollion evaluation dataset na [EDTeKLA Dev v1](/docs/leaderboard/datasets) ay hinango mula sa gawaing ito, lisensiyado sa ilalim ng [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

### Iba pang approach na nasubukan na ng mga tao o maaaring subukan

Method-agnostic ang leaderboard. Narito ang mga estratehiyang na-explore o naimungkahi para sa low-resource MT, at alinman sa mga ito ay maaaring isumite:

| Approach | Paano Ito Gumagana | Mga Kalamangan | Mga Kahinaan |
|----------|-------------|------|------|
| **[Coached LLM prompting](/docs/tutorials/coached-llm-prompting)** | Mag-inject ng grammar rules, dictionaries, at example pairs sa system prompt | Mabilis mag-iterate, walang kailangang training | Limitado ang quality ceiling ng base knowledge ng LLM |
| **[Few-shot prompting](/docs/tutorials/few-shot-prompting)** | Isama ang verified translations bilang in-context examples | Mabuti para sa consistent style | Maliit ang context window; HINDI dapat manggaling sa eval data ang examples |
| **[FST-gated pipeline](/docs/tutorials/fst-gated-pipeline)** | LLM generates → FST validates → rejects and retries invalid morphology | Ginagarantiyahan ang morphological validity | Nangangailangan ng FST infrastructure; nagdaragdag ng latency at cost ang retry loops |
| **[Dictionary lookup + LLM](/docs/tutorials/dictionary-augmented-llm)** | Ipilit ang known terms mula sa bilingual dictionary, hayaang ang LLM ang humawak sa natitira | Binabawasan ang hallucination para sa known terms | Laging hindi kumpleto ang dictionary coverage |
| **[Fine-tuned model](/docs/tutorials/fine-tuned-model)** | I-fine-tune ang isang open model (Llama, Mistral) sa parallel text — basta hindi sa eval data | Posibleng pinakamataas ang kalidad | Nangangailangan ng parallel corpus (bihira); magastos; may panganib ng overfitting |
| **[Chained models](/docs/tutorials/chained-models)** | Model A generates rough translation → Model B post-edits → Model C scores | Maaaring pagsamahin ang lakas ng mga specialist | Komplikado; mabagal; magastos |
| **[Rule-based + LLM hybrid](/docs/tutorials/rule-based-hybrid)** | Gumamit ng linguistic rules para sa known patterns, LLM para sa lahat ng iba pa | Tumpak kung saan naaangkop ang rules | Nangangailangan ng malalim na linguistic expertise |
| **[Back-translation augmentation](/docs/tutorials/back-translation)** | Bumuo ng synthetic parallel data sa pamamagitan ng pagsasalin ng Cree→English, pagkatapos ay magsanay sa reverse | Murang nagpapalawak ng training data | Pinalalakas ang kasalukuyang model errors |
| **[Evolutionary approach](/docs/tutorials/evolutionary-approach)** | Bumuo ng candidate translations, i-score ang mga ito, i-mutate ang pinakamahusay na performers, ulitin | Maaaring makatuklas ng novel solutions; parallelizable | Computationally expensive; nangangailangan ng mahusay na fitness function |
| **[Partial translation](/docs/tutorials/partial-translation)** | Manu-manong isalin ang representative sample, patunayan na tumutugma ang inyong method sa inyong style dito, pagkatapos ay i-auto-translate ang natitirang bulk | Pinagsasama ang human quality at machine scale | Nangangailangan ng paunang human effort |
| **Manual JSON / exam grading** | Manu-manong gumawa ng dataset JSON file upang subukin ang mga sagot ng estudyante sa language exam, o mag-grade ng batch ng human translations laban sa gold standard | Walang kinakailangang ML; gumagana para sa edukasyon at QA | Hindi nag-scale sa tuloy-tuloy na translation needs |

### JSON lamang ito

Tumatanggap ang harness ng JSON at naglalabas ng scored JSON. Simple ang [dataset format](/docs/leaderboard/datasets):

```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

Maaari ninyo itong buuin nang mano-mano. Maaari ninyo itong i-export mula sa spreadsheet. Maaari ninyo itong i-generate mula sa corpus. Maaaring gamitin ito ng isang language teacher upang i-score ang mga translation ng estudyante. Maaaring gamitin ito ng isang translation agency upang i-benchmark ang freelancers. Maaaring gamitin ito ng isang research lab upang ihambing ang model architectures. Walang pakialam ang harness kung saan nanggaling ang JSON — ini-score lang nito ito.

At dahil ginagamit ng production deployment framework ang parehong plugin interface, ang method na mataas ang score sa harness ay nade-deploy sa inyong website sa isang pagbabago lang sa config. **Patunayan ito at gamitin ito.**

Talagang walang katapusan ang mga posibilidad. **Kung mayroon kayong ideya, buuin ito, patakbuhin ang harness, at isumite ang inyong scores.**

---

## Paano Umaangkop ang champollion

Ibinibigay ng champollion ang infrastructure layer — kayo ang magdadala ng method.

### Ang coaching system

Hinahayaan kayo ng `llm-coached` method ng champollion na direktang mag-inject ng linguistic knowledge sa LLM prompt:

```json title=".champollion/coaching/crk.json"
{
  "grammar_rules": [
    "Plains Cree is polysynthetic — a single word can express what English needs a full sentence for",
    "Animate/inanimate noun distinction affects verb conjugation, demonstratives, and pluralization",
    "Use SRO (Standard Roman Orthography) as the working script — syllabic conversion is handled by the deterministic converter",
    "Obviation: when two third-person referents appear, the less salient one takes obviative marking (-a suffix on nouns, -iyiwa on verbs)"
  ],
  "dictionary": {
    "home": "kīwēwin",
    "settings": "isi-nākatohkēwin",
    "search": "nānātawāpahtam",
    "welcome": "tānisi",
    "dashboard": "kīskinwahamākēwin-māsinahikan"
  },
  "style_notes": "Use formal register appropriate for educational and community contexts. Preserve English technical terms in parentheses when no Cree equivalent exists or is widely accepted."
}
```

Ini-inject ang coaching data sa bawat LLM prompt para sa `en:crk` pair, na nagbibigay sa model ng structured linguistic context na wala sana ito. Tingnan ang [Coaching Data](https://champollion.dev/docs/concepts/coaching-data) para sa buong specification.

### Registers

Ang register ay bahagi ng system prompt na gumagabay sa tone, formality, at orthographic conventions. May kasamang isang Plains Cree register ang champollion:

```
nêhiyawêwin (Plains Cree). Use SRO (Standard Roman Orthography) as the working
script. Output will be converted to Syllabics via deterministic converter.
Professional register appropriate for educational and community contexts.
```

Maaari ninyo itong i-override sa inyong config upang mag-eksperimento sa iba't ibang prompting strategies:

```json title="champollion.config.json"
{
  "languages": {
    "crk": {
      "register": "Casual Plains Cree (Y-dialect). Use SRO. Prefer everyday vocabulary over formal or archaic terms. Address the reader directly."
    }
  }
}
```

Iba't ibang translation styles ang nalilikha ng iba't ibang registers — at iba't ibang scores sa leaderboard. Itinatala ng bawat submission ang eksaktong register at system prompt na ginamit (bilang SHA-256 hash sa [run card](/docs/specifications/run-card)), kaya reproducible ang mga eksperimento.

### Script conversion

Isinusulat ang Plains Cree sa dalawang script: **Standard Roman Orthography (SRO)** at **Canadian Aboriginal Syllabics**. Ang pipeline ng champollion:

1. Nagsasalin ang LLM sa SRO (Latin-based, na mas mahusay hawakan ng mga LLM)
2. Vina-validate ng quality gate ang SRO output
3. Tinutransform ng deterministic converter ang SRO → Syllabics
4. Isinusulat sa disk ang converted text

Hinahawakan ng converter ang lahat ng SRO diacritics (ê, î, ô, â para sa long vowels) at ima-map ang mga ito sa tamang syllabic characters. Tingnan ang [Script Converters](https://champollion.dev/docs/concepts/script-converters) para sa technical details.

### Ang evaluation loop

Pinatatakbo ng [eval harness](/docs/specifications/harness) ang inyong method laban sa evaluation dataset at gumagawa ng scored [run card](/docs/specifications/run-card):

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install -e .

# Run a baseline experiment
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v7

# Run with FST validation (if you have an FST binary)
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --fst-analyzer ./bin/crk-analyzer \
  --condition fst-gated-v1
```

Ang `--condition` flag ay label na pinipili ninyo. Lumilitaw ito sa leaderboard upang makita ng mga tao kung anong prompt strategy ang ginamit ninyo. Itinatala ng harness ang buong system prompt sa run card, kaya reproducible ang eksaktong approach ninyo.

:::tip Malayang mag-eksperimento, isumite ang pinakamahusay ninyo
Idinisenyo ang harness para sa mabilis na iteration. Magpatakbo ng dose-dosenang eksperimento gamit ang iba't ibang models, coaching data, registers, at conditions. Isumite lamang sa leaderboard kapag mayroon na kayong ipinagmamalaki.
:::

---

## Mga Prinsipyo ng OCAP

Idinisenyo ang champollion upang suportahan ang Indigenous data sovereignty. Ang [OCAP principles](https://fnigc.ca/ocap-training/) (Ownership, Control, Access, Possession) ang gumagabay sa aming paglapit sa language technology para sa Indigenous communities:

| Prinsipyo | Paano ito sinusuportahan ng champollion |
|-----------|------------------------|
| **Ownership** | Ang mga language community ang nagmamay-ari ng kanilang linguistic data. Hindi kailanman nagpa-phone home o nagpapadala ng data ang champollion sa aming servers |
| **Control** | Pinapayagan ng [API method](https://champollion.dev/docs/guides/serving-a-method) ang mga community na i-host ang sarili nilang translation pipeline — ibinibigay namin ang interface, kontrolado nila ang implementation |
| **Access** | Ang mga community ang nagpapasya kung sino ang maaaring gumamit ng kanilang method. Maaaring lagyan ng authentication gate ang API |
| **Possession** | Nananatili ang lahat ng translation data sa file system ng inyong proyekto. Sinusubaybayan ng [provenance system](https://champollion.dev/docs/concepts/security) kung saan nanggaling ang bawat translation |

Ibig sabihin ng plugin architecture, maaaring bumuo ang isang community ng method na internally nagsasama ng sacred o restricted knowledge, ilantad lamang ang translation API, at panatilihin ang buong kontrol sa kanilang linguistic resources.

---

## Ang Vision: Ano ang Susunod

Plains Cree ang unang target. Kapag na-validate na ang pipeline at nasiyahan ang community sa kalidad, lumalawak ang parehong architecture sa iba pang polysynthetic languages na may FST infrastructure:

- **Iba pang Algonquian languages**: Woods Cree, Swampy Cree, Ojibwe, Blackfoot
- **Inuit languages**: Inuktitut, Inuinnaqtun (na gumagamit din ng syllabic scripts)
- **Iba pang language families**: anumang wikang may FST analyzer ay maaaring gumamit ng FST-gated pipeline

Language-pair-scoped ang leaderboard. Habang nag-aambag ang language communities ng mga bagong evaluation dataset, awtomatikong nagbubukas ang mga bagong leaderboard track.

**Ito ay isang bukas na paanyaya.** Kung nagtatrabaho kayo sa isang low-resource language — bilang researcher, community member, estudyante, o simpleng taong nagmamalasakit — binibigyan kayo ng champollion ng mga tool upang bumuo ng tunay na bagay, sukatin ito nang tapat, at ibahagi ito sa mundo. Naghihintay ang [Method Leaderboard](https://champollion.dev/leaderboard) sa inyong submission.

---

## Tingnan Din

- **[Method Leaderboard](https://champollion.dev/leaderboard)** — isumite ang inyong scores at tingnan kung paano naghahambing ang mga method
- **[MT Evaluation](/docs/leaderboard/rules)** — ano ang bumubuo sa isang mahusay na method, ano ang nagdudulot ng disqualification
- **[Eval Harness](/docs/specifications/harness)** — paano magpatakbo ng mga eksperimento
- **[Evaluation Datasets](/docs/leaderboard/datasets)** — EDTeKLA Dev v1 at FLORES+
- **[Coaching Data](https://champollion.dev/docs/concepts/coaching-data)** — paano i-structure ang linguistic knowledge para sa LLM
- **[Script Converters](https://champollion.dev/docs/concepts/script-converters)** — ang SRO→Syllabics pipeline
- **[Serving a Method via API](https://champollion.dev/docs/guides/serving-a-method)** — pag-host ng community-controlled translation
- **[ALTLab](https://altlab.artsrn.ualberta.ca/)** — ang Alberta Language Technology Lab
- **[EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/)** — ang Educational Technology, Knowledge & Language research group
- **[itwêwina dictionary](https://itwewina.altlab.app/)** — FST-powered Plains Cree–English dictionary