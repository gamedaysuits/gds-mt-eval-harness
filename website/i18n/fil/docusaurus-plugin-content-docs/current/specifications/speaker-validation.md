---
sidebar_position: 8
title: "Protocol sa Pagpapatunay ng Tagapagsalita"
slug: '/specifications/speaker-validation'
---
# Protocol sa Pagpapatunay ng Tagapagsalita

> **Layunin.** Tinutukoy ng dokumentong ito nang eksakto kung ano ang kailangan namin mula sa mga bilingguwal na tagapagsalita ng Cree–English upang mapatunayan ang mga LYSS evaluation metrics. Kung wala ang pagpapatunay na ito, ang aming mga automated score ay mga pagtatantiyang pang-inhinyeriya, hindi napatunayang mga sukat ng kalidad. Ito ang nag-iisang pinakamahalagang kakulangan sa proyekto.
>
> **Audience.** Mga community partner, potensyal na collaborator, grant reviewer, at ang project team.
>
> Huling na-update: 2026-06-07

---

## 1. Bakit Kailangan Namin ang mga Tagapagsalita

Ang LYSS evaluation framework (Linguistically-informed Yield & Structural Scoring) ay nagkukuwenta ng mga automated quality score para sa mga saling English → Plains Cree. Gumagamit ito ng tatlong pangunahing signal:

- **LYSS-fst**: Naglalaman ba ang output ng mga valid na salitang Cree? (sinusuri ng GiellaLT finite-state transducer)
- **LYSS-eq**: Katanggap-tanggap bang variant ng reference translation ang output? (sinusuri ng equivalence classes ng linter)
- **LYSS-sem**: Napapanatili ba ng output ang kahulugan ng source? (sinusuri ng semantic validator)

Gumagawa ng mga numero ang mga metric na ito. **Hindi namin alam kung may kahulugan ang mga numerong iyon.** Maaaring tanggihan ng FST ang mga valid na salitang hindi nito nakikilala (loanwords, neologisms, proper nouns). Maaaring hindi makita ng linter ang mga valid equivalence o tanggapin ang mga invalid. Maaaring magkamali ang semantic validator sa paghusga ng kahulugan. Hangga't hindi sinasabi sa amin ng mga bilingguwal na tagapagsalita kung tumutugma ang aming mga automated score sa kanilang human judgment ng kalidad ng salin, nanghuhula lamang kami.

Ang bawat pangunahing MT evaluation metric (BLEU, COMET, chrF++) ay napatunayan sa pamamagitan ng paghahambing ng mga automated score laban sa libo-libong human quality assessment. Kailangan namin ang pareho — sa mas maliit na saklaw, dahil limitado ang aming mga resource, ngunit may parehong higpit.

---

## 2. Ano ang Kailangan Namin: Tatlong Gawain

### Gawain A: Translation Quality Rating (Pangunahin — ~8 oras sa kabuuan)

**Ano:** I-rate ang 200 machine-generated English → Cree translation sa dalawang scale.

**Sino:** 3+ bilingguwal na tagapagsalita ng Plains Cree–English na may reading fluency sa SRO (Standard Roman Orthography).

**Paano ito gumagana:**

1. Magbibigay kami ng spreadsheet o web form na may 200 row. Ang bawat row ay may:
   - Ang English source sentence
   - Isang machine-generated Cree translation
   - (Opsyonal) isang reference Cree translation para sa paghahambing

2. Para sa bawat salin, ire-rate ng tagapagsalita ang dalawang bagay:

   **Adequacy** (tama ba ang sinasabi nito?):
   | Iskor | Etiketa | Kahulugan |
   |-------|-------|---------|
   | 1 | Wala | Walang kinalaman ang salin sa source |
   | 2 | Kaunti | Tumutugma ang ilang salita ngunit mali ang kabuuang kahulugan |
   | 3 | Marami | Naroon ang pangunahing kahulugan ngunit may mahahalagang bahagi na nawawala o mali |
   | 4 | Karamihan | Halos lahat ay tama, may maliliit na puwang sa kahulugan |
   | 5 | Lahat | Ganap na naipapahayag ng salin ang kahulugan ng source |

   **Fluency** (parang tunay bang Cree ang tunog nito?):
   | Iskor | Etiketa | Kahulugan |
   |-------|-------|---------|
   | 1 | Hindi maintindihan | Hindi ito Cree |
   | 2 | Hindi fluent | Maaaring Cree ang mga indibidwal na salita ngunit sira ang pangungusap |
   | 3 | Hindi native | Nauunawaan ngunit malinaw na hindi ganito ito sasabihin ng tagapagsalita ng Cree |
   | 4 | Mabuti | Natural ang tunog na may kaunting pagkaasiwa |
   | 5 | Walang kapintasan | Maaaring isinulat ito ng isang tagapagsalita ng Cree |

3. Opsyonal, maaaring magdagdag ang tagapagsalita ng free-text note na nagpapaliwanag ng kanilang rating (hal., "mali ang animate/inanimate agreement sa verb," "ito ay th-dialect ngunit nag-rate ako batay sa y-dialect").

**Tinatayang oras:** ~2.5 minuto bawat salin × 200 salin = ~8 oras. Maaaring hatiin sa maraming session (hal., 4 × 2-oras na session sa loob ng 2 linggo).

**Kompensasyon:** $50–65 CAD/oras (tugma sa BENCHMARK_SPEC §10.3 speaker compensation rates). Kabuuan bawat tagapagsalita: $400–520 CAD. Para sa 3 tagapagsalita: **$1,200–1,560 CAD**.

**Ano ang gagawin namin dito:** Kukuwentahin namin ang korelasyon sa pagitan ng aming mga automated LYSS score at ng mga rating ng tagapagsalita. Kung may korelasyon ang LYSS-fst sa fluency ratings at may korelasyon ang LYSS-sem sa adequacy ratings, napapatunayan ang mga metric. Kung hindi, malalaman namin kung saan sila aayusin.

---

### Gawain B: Pagpapatunay ng Linter Equivalence (~2 oras)

**Ano:** Suriin ang 50 pares ng Cree translation na ikinaklasipika ng aming linter bilang "equivalent" at sabihin sa amin kung talagang pareho ang kahulugan ng mga ito.

**Sino:** 1–2 bilingguwal na tagapagsalita (maaaring ang parehong mga tagapagsalita sa Gawain A).

**Paano ito gumagana:**

1. Magbibigay kami ng 50 pares. Ang bawat pares ay may:
   - Ang English source
   - Translation A (ang reference)
   - Translation B (isang variant na sinasabi ng aming linter na equivalent)
   - Ang dahilan ng equivalence (hal., "word order permutation," "orthographic variant," "optional particle removed")

2. Para sa bawat pares, sasagutin ng tagapagsalita:
   - **Pareho ang kahulugan?** Oo / Hindi / Depende sa konteksto
   - **Parehong natural?** Oo / Mas mabuti ang A / Mas mabuti ang B / Wala sa dalawa ang natural
   - **Mga tala** (opsyonal na free text)

**Tinatayang oras:** ~2 minuto bawat pares × 50 pares = ~2 oras.

**Kompensasyon:** $50–65 CAD/oras × 2 oras = **$100–130 CAD bawat tagapagsalita**.

**Ano ang gagawin namin dito:** Kukuwentahin namin ang presisyon ng bawat equivalence class. Kung sinasabi ng mga tagapagsalita na 90% ng "word order" equivalences ay tunay na equivalent, napapatunayan ang class na iyon. Kung sinasabi nilang mali ang 40% ng "lemma synonym" equivalences, malalaman naming kailangang ayusin o alisin ang class na iyon.

---

### Gawain C: Pagsusuri ng FST False Rejection (~1.5 oras)

**Ano:** Suriin ang 100 salitang Cree na tinatanggihan ng FST analyzer (sinasabing hindi valid na salitang Cree) at sabihin sa amin kung talagang valid ang mga ito.

**Sino:** 1 bilingguwal na tagapagsalita na may malakas na kaalaman sa bokabularyong Cree.

**Paano ito gumagana:**

1. Patatakbuhin namin ang FST analyzer sa aming 436-entry EDTeKLA gold-standard corpus at kokolektahin ang bawat salitang tinatanggihan nito.
2. Ipapakita namin sa tagapagsalita ang hanggang 100 tinanggihang salita kasama ang kanilang sentence context.
3. Para sa bawat salita, sasagutin ng tagapagsalita:
   - **Valid ba itong salitang Cree?** Oo / Hindi / Hindi sigurado
   - **Kung oo, anong uri?** Established word / Loanword / Name / Dialectal form / Neologism / Other
   - **Mga tala** (opsyonal)

**Tinatayang oras:** ~1 minuto bawat salita × 100 salita = ~1.5 oras.

**Kompensasyon:** $50–65 CAD/oras × 1.5 oras = **$75–100 CAD**.

**Ano ang gagawin namin dito:** Kukuwentahin namin ang false rejection rate ng FST. Kung tinatanggihan ng FST ang 50 salita at sinasabi ng mga tagapagsalita na valid ang 30 sa mga ito, ang false rejection rate ay 60% — hindi katanggap-tanggap na mataas, kaya nangangailangan ng loanword/exception allowlist. Kung sinasabi ng mga tagapagsalita na 5 lamang ang valid, ang false rejection rate ay 10% — maaasahan ang metric.

---

## 3. Kabuuang Commitment ng Tagapagsalita

| Gawain | Kailangang Tagapagsalita | Oras bawat Tagapagsalita | Gastos bawat Tagapagsalita | Kabuuang Gastos |
|------|----------------|-------------------|-----------------|------------|
| A: Quality Rating | 3 | ~8 oras | $400–520 | $1,200–1,560 |
| B: Linter Validation | 2 | ~2 oras | $100–130 | $200–260 |
| C: FST Review | 1 | ~1.5 oras | $75–100 | $75–100 |
| **Kabuuan** | **3 tagapagsalita** | **~11.5 oras (max bawat tagapagsalita)** | **$575–750 (max)** | **$1,475–1,920** |

Kung gagawin ng parehong 3 tagapagsalita ang lahat ng gawain: **~11.5 oras bawat isa sa loob ng 2–4 na linggo, $575–750 bawat isa**.

Ang isang tagapagsalita na gagawa lamang ng Gawain A ay maglalaan ng **~8 oras sa loob ng 2 linggo para sa $400–520**.

---

## 4. Mga Kwalipikasyon ng Tagapagsalita

**Kinakailangan:**
- Bilingguwal sa Plains Cree at English
- Reading fluency sa SRO (Standard Roman Orthography)
- Komportable sa pag-rate ng mga salin gamit ang structured scale

**Mas mainam:**
- Karanasan sa y-dialect (ang dialect na ginagamit sa aming reference corpus mula sa EDTeKLA)
- Karanasan sa pagtuturo o pagsasalin (nagbibigay ng calibrated quality judgment)
- Pamilyaridad sa iba't ibang register (formal, educational, conversational)

**Hindi kinakailangan:**
- Kaalamang teknikal o NLP (ibibigay namin ang lahat ng tool at konteksto)
- Computational skills (ang rating interface ay magiging simpleng spreadsheet o web form)
- Dating pakikilahok sa Champollion project

---

## 5. Data Governance

Ang lahat ng kontribusyon ng tagapagsalita ay pinamamahalaan ng OCAP®-forward data policies ng proyekto:

- **Ownership:** Nananatiling intellectual contribution ng mga tagapagsalita ang kanilang mga quality rating. Kikilalanin sila sa pangalan (o nang anonymous, ayon sa kanilang pagpili) sa anumang publication.
- **Control:** Maaaring bawiin ng mga tagapagsalita ang kanilang mga rating anumang oras. Kapag binawi, aalisin ang kanilang data mula sa lahat ng analysis.
- **Access:** Iniimbak ang rating data sa infrastructure na kontrolado ng community governance organization (kapag naitatag) o sa platform na mas gusto ng tagapagsalita.
- **Possession:** Hindi kailanman inilalathala ang raw rating data. Tanging aggregate statistics (correlations, inter-annotator agreement) ang lumilitaw sa mga publication.
- **Compensation:** Binabayaran ang mga tagapagsalita para sa kanilang oras kahit gamitin man namin o hindi ang kanilang mga rating. Hindi nakadepende sa resulta ang bayad.

---

## 6. Ano ang Makukuha ng mga Tagapagsalita

Bukod sa kompensasyon:

- **Co-authorship** sa anumang publication na gumagamit ng kanilang mga rating (kung nais)
- **Acknowledgment** sa lahat ng dokumentasyon ng proyekto
- **Early access** sa evaluation tools at mga resulta
- **Input** sa kung paano ginagamit ang mga metric — kung sasabihin ng isang tagapagsalita na "mali ang inyong linter tungkol sa X," aayusin namin ang linter
- **Veto power** sa paglalathala ng mga resultang itinuturing nilang problematiko

---

## 7. Paano Magsimula

Kung kayo ay isang bilingguwal na tagapagsalita ng Cree–English na interesadong lumahok, o kung may kilala kayong maaaring interesado:

1. **Makipag-ugnayan sa amin** sa [project email/contact] — walang kinakailangang commitment, pag-uusap lamang
2. **Ipapaliwanag namin ang mga gawain** sa simpleng wika (walang jargon)
3. **Pipiliin ninyo kung aling mga gawain** ang interesado kayo (A, B, C, o anumang kombinasyon)
4. **Magtatakda kami ng iskedyul** na angkop sa inyo (2-oras na block, flexible timing)
5. **Magre-rate kayo ng mga salin** sa pamamagitan ng spreadsheet o web form — mula saanman, sa sarili ninyong oras
6. **Magbabayad kami kaagad** — sa loob ng 2 linggo matapos makumpleto ang bawat task block

---

## 8. Ano ang Mangyayari Pagkatapos

Gamit ang speaker validation data, magagawa naming:

1. **Ilathala ang metric correlations** — pinatutunayan (o pinabubulaanan) na ang LYSS scores ay sumasalamin sa human judgment
2. **I-recalibrate ang metrics** — inaayos ang weights, thresholds, at equivalence classes batay sa feedback ng tagapagsalita
3. **Ayusin ang linter** — inaalis ang false equivalences, nagdaragdag ng mga nawawala
4. **Ayusin ang FST allowlist** — nagdaragdag ng mga valid na salitang maling tinatanggihan ng FST
5. **Magsumite sa isang academic venue** — kasama ang mga tagapagsalita bilang co-authors, itinatatag ang LYSS bilang validated metric para sa polysynthetic language MT evaluation

Kung walang speaker validation, nananatiling engineering tool ang LYSS. Sa pamamagitan nito, nagiging scientifically grounded evaluation metric ang LYSS. Iyon ang pagkakaiba ng "may ginawa kami" at "napatunayan naming gumagana ito."