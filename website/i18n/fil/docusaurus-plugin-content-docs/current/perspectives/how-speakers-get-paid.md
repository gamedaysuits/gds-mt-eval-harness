---
sidebar_position: 2
title: "Paano Binabayaran ang mga Speaker"
slug: '/perspectives/how-speakers-get-paid'
description: "Kung magkano ang binabayad sa community validators at translators para sa benchmark work, kung bakit hindi maaaring ipagkompromiso ang pagbabayad sa mga speaker, at kung paano lumalaki ang compensation habang lumalago ang Arena. Ang lahat ng numero ay mula sa mga nalathalang specifications."
related:
  - label: "Speaker Validation Protocol"
    to: /docs/specifications/speaker-validation
    kind: spec
    note: "The work validators are paid for"
  - label: "Prize Specification"
    to: /docs/specifications/prizes
    kind: spec
    note: "Where prize money goes, and why"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
---
# Paano Binabayaran ang mga Tagapagsalita

> **Tala sa transparency.** Bawat numero sa pahinang ito ay lumilitaw na sa isang nailathalang specification — ang [Benchmark Specification §10](/docs/specifications/benchmark#10-cost-framework), ang [Speaker Validation Protocol](/docs/specifications/speaker-validation), at ang [Prize Specification](/docs/specifications/prizes). Pinagsasama-sama ng pahinang ito ang mga iyon sa iisang lugar, sa malinaw na wika, upang walang kailangang magbasa ng spec para malaman kung ano ang halaga ng oras ng tagapagsalita dito. Wala itong ipinapangakong lampas sa nakasaad na ng mga dokumentong iyon.

Ang bilingual na tagapagsalita na kayang humusga kung ang isang pangungusap na ginawa ng makina ay tunay, matatas, at tama ang kahulugan ang pinakabihira at pinakamahalagang kalahok sa buong sistemang ito. Ang lahat ng iba pa — harnesses, metrics, leaderboards — ay umiiral upang mapalawak ang naabot ng kaunting oras ng taong iyon.

Kaya simple ang unang tuntunin: **binabayaran ang mga tagapagsalita para sa kanilang oras, sa mga propesyonal na rate, anuman ang ipakita ng mga resulta.**

---

## Bakit hindi mapagtatawaran ang pagbabayad sa mga tagapagsalita

Matagal nang nakasanayan ng pananaliksik sa language technology na ituring ang matatatas na tagapagsalita bilang libreng resource — "community engagement" na lumilikha ng datasets, papers, at careers para sa lahat maliban sa mga tagapagsalita. Itinuturing namin ang ganitong padron bilang mapagsamantala, at ang mga taong pinakakwalipikadong gumawa ng gawaing ito ay mismong mga taong ang oras ay abala na sa agarang gawain ng pagtuturo, pagsasalin, at pagpapalaki ng mga bata sa wika.

Tatlong kahihinatnang pangdisenyo ang sumusunod:

1. **Walang volunteer pipeline.** Hindi namin hinihiling sa mga tagapagsalita na magbigay ng evaluation work bilang pabor sa pananaliksik. Ang pakikilahok ay bayad na engagement, at walang nawawala sa tagapagsalita kung tatanggihan nila ito.
2. **Walang kondisyon ang pagbabayad.** Binabayaran ang mga tagapagsalita gamitin man o hindi ang kanilang ratings, at hindi nakadepende ang pagbabayad sa mga resulta. Nangangako ang nailathalang protocol ng pagbabayad sa loob ng dalawang linggo pagkatapos makumpleto ang bawat task block.
3. **Hindi kabuuan ng usapan ang kompensasyon.** Ang mga tagapagsalitang nag-aambag ng ratings ay tumatanggap din ng credit (nakapangalan o anonymous, ayon sa kanilang pinili), opsyonal na co-authorship sa mga publikasyong gumagamit ng kanilang ratings, karapatang bawiin ang kanilang mga kontribusyon anumang oras, at veto power sa paglalathala ng mga resultang itinuturing nilang problematiko. Ang mga terminong iyon ay nasa [Speaker Validation Protocol §5–6](/docs/specifications/speaker-validation), hindi sa hiwalay na kasulatan.

## Ang mga nailathalang rate

Itinatakda ng benchmark cost framework ang kompensasyon ng bilingual na tagapagsalita sa **$50–65 CAD kada oras** para sa corpus at validation work. Ang ibig sabihin nito kada role:

### Pagbuo ng benchmark corpus

Ang paglikha ng reference translations na pagbabatayan ng score ng bawat method ang pundasyonal na gawain ng tagapagsalita. Ang nailathalang establishment budget kada wika:

| Gawain | Nailathalang saklaw | Batayan |
|------|-----------------|-------|
| Corpus curation (50–150 entries) | $2,500–6,000 | $50–65/hr, oras ng bilingual na tagapagsalita |
| Pagsusuri ng method output | $500–1,500 | Parehong hourly rates |

Karaniwang umaabot nang humigit-kumulang 80 oras ang buong corpus para sa isang tagapagsalita; ang planadong agent-assisted workflow (sentence drafting at formatting na pinangangasiwaan ng tooling, at ang pagsasalin ay laging ng tao) ay idinisenyong ibaba iyon tungo sa 30–40 oras — mas kaunting oras ng paulit-ulit na gawain, parehong hourly rate, at ginagawa lamang ng tagapagsalita ang mga bahaging tunay na nangangailangan ng tao.

### Pag-validate ng metrics

Bago magkaroon ng anumang kahulugan ang automated scores, kailangang itugma ang mga ito ng mga tagapagsalita sa human judgment. Inilalathala ng [Speaker Validation Protocol](/docs/specifications/speaker-validation) ang eksaktong mga gawain, oras, at bayad:

| Gawain | Oras | Bayad kada tagapagsalita |
|------|------|-----------------|
| A — Mag-rate ng 200 machine translations para sa adequacy at fluency | ~8 oras | $400–520 CAD |
| B — Suriin ang 50 "katumbas" na translation pairs | ~2 oras | $100–130 CAD |
| C — Suriin ang 100 salitang tinanggihan ng morphological analyzer | ~1.5 oras | $75–100 CAD |

Ang tagapagsalitang gagawa ng lahat ng tatlo ay maglalaan ng humigit-kumulang 11.5 oras sa loob ng dalawa hanggang apat na linggo para sa **$575–750 CAD**. Ang buong three-speaker validation round ay nagkakahalaga sa proyekto ng $1,475–1,920 — at iyon ang punto: maliit na line item para sa proyekto ang speaker validation at hindi dapat kailanman dito "magtipid" ng gastos.

### Pagsusuri ng mga prize claim

Walang prize na ibinabayad batay lamang sa automated scores. Kinakailangan ng [Founder's Prize](/docs/specifications/prizes) ($10,000 CAD, English→Plains Cree) na hindi bababa sa dalawang bilingual na tagapagsalita ang independiyenteng magsuri ng isang estratipikadong sample ng hindi bababa sa 30 outputs, at na 70% o higit pa ay ma-rate bilang "katanggap-tanggap" o "napakahusay." Ang pagsusuring iyon ay bayad na gawain ng tagapagsalita sa ilalim ng parehong mga rate — at isa rin itong gate: maaaring mapabagsak ng mga tagapagsalita ang isang prize claim, at sinadya iyon sa disenyo.

## Paano ito lumalawak kasabay ng mga contest

Itinayo ang modelo upang lumago ang kompensasyon ng tagapagsalita kasabay ng platform sa halip na malabnaw dahil dito:

- **Nagsisimula ang bawat bagong wika sa bayad na corpus engagement.** Ang nailathalang establishment cost kada wika ($3,350–8,500 all-in) ay halos kompensasyon ng tagapagsalita — ang pinakamalaking iisang bahagi, at sinadya iyon.
- **May sariling bayad na pagsusuri ang bawat bagong prize pool.** Bawat sponsored contest na sumusunod sa [prize template](/docs/specifications/prizes#4-future-prize-pools) ay may parehong community-validation requirement, na nangangahulugang bawat contest ay nagpopondo ng speaker review work para sa wikang iyon.
- **Pinopondohan ng deployed methods ang patuloy na pagsusuri.** Kapag kumikita ng API revenue ang isang community-owned method, 90% ay dumadaloy sa governance organization ng komunidad ([ang economic model](/docs/sovereignty/economic-model)), na maaaring magpondo ng patuloy na pagsusuri, paglago ng corpus, at mga programa sa wika ayon sa minamabuti nito. Desisyon iyon ng komunidad, hindi sa amin.

## Ang *hindi* namin ipinangako

Kinakailangan ng katapatan na markahan ang mga hangganan:

- Ang mga rate sa itaas ay ang mga nailathalang rate para sa kasalukuyang gawaing Plains Cree. Itatakda ang mga rate para sa mga susunod na wika kasama ang partner community at ilalathala sa parehong paraan — sa specs, bago magsimula ang trabaho.
- Ang flywheel (revenue → komunidad → mas maraming bayad na trabaho) ay nangangailangan ng panlabas na pagpopondo upang magsimula at hindi pa self-sustaining. Inilalarawan ng [economic model](/docs/sovereignty/economic-model) ang mekanismo, hindi isang garantiya.
- Kinakailangan ang "makatarungang bayad" ngunit hindi ito sapat. Ang pagbabayad ay hindi awtomatikong nagpapaging hindi mapagsamantala sa isang proyekto — ownership at control ang gumagawa niyon, kaya ang kompensasyon ay nasa loob ng [sovereignty architecture](/docs/sovereignty/data-sovereignty) sa halip na pumalit dito.

---

## Ano ang ibig sabihin nito para sa inyo

:::info Kung kayo ay miyembro ng komunidad
Kung bilingual kayo sa isang underserved language at English, ang inyong paghatol ang pinakamahalagang input sa sistemang ito, at ang nailathalang mga termino ay: $50–65 CAD/hour, flexible scheduling, pagbabayad sa loob ng dalawang linggo, credit ayon sa inyong mga termino, at karapatang bawiin ang inyong mga kontribusyon. Hindi kailangan ang programming. Magsimula sa [Para sa mga Language Community](/docs/community/for-language-communities) o sa [Speaker Validation Protocol §7](/docs/specifications/speaker-validation#7-how-to-get-started).
:::

:::info Kung kayo ay researcher
I-budget ang kompensasyon ng tagapagsalita bilang first-class research cost — ang nailathalang mga bilang ($1,475–1,920 para sa metric-validation round; $2,500–6,000 para sa corpus curation) ay maliit ayon sa grant standards at ang mga ito ang nagpapaging depensable sa automated scores. Ipinapakita ng [Corpus Partnership Strategy](/docs/specifications/corpus-partnership) kung paano makakapasok dito ang isang academic department na may nakapaloob na funded speaker work.
:::

:::info Kung kayo ay builder
Nakikinabang kayo sa bayad na gawain ng tagapagsalita kahit hindi ninyo ito kailanman pondohan: validated metrics ang nagpapakahulugan sa inyong leaderboard score, at bayad na community review ang nasa pagitan ng inyong method at ng isang prize. Kung manalo kayo, asahan ninyong nabayaran ang mga tagapagsalita upang masusing suriin ang inyong output — at asahan ang [paglipat ng ownership ng inyong method](/docs/sovereignty/ownership-transfer) sa komunidad na pinaglilingkuran ng wika nito.
:::

## Tingnan din

- [Ang Translation ay Hindi Revitalization](/docs/perspectives/translation-is-not-revitalization) — bakit binabalangkas ng awtoridad ng tagapagsalita ang lahat ng iba pa
- [Pag-uulat ng mga Error at Pagmamay-ari ng mga Correction](/docs/perspectives/reporting-errors-and-owning-corrections) — awtoridad ng tagapagsalita pagkatapos din ng benchmark
- [Benchmark Specification §10](/docs/specifications/benchmark#10-cost-framework) — ang buong cost framework na pinagmulan ng mga numerong ito