---
sidebar_position: 3
title: "Mula Benchmark hanggang Pang-araw-araw na Paggamit: Ang Landas ng Post-Editing"
slug: '/perspectives/from-benchmark-to-daily-use'
description: "Kung paano nagiging workflow ng pagsasalin ng komunidad ang isang benchmarked na paraan ng pagsasalin: machine draft, post-edit ng fluent speaker, nailathalang teksto — na may tapat na quality thresholds sa bawat hakbang."
related:
  - label: "Deploy to Production"
    to: /docs/getting-started/deploy-to-production
    kind: guide
    note: "From proven method to live translation"
  - label: "Cookbook: Partial Translation (Human + Machine)"
    to: /docs/tutorials/partial-translation
    kind: cookbook
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The quality thresholds behind the path"
  - label: "Translation Is Not Revitalization"
    to: /docs/perspectives/translation-is-not-revitalization
    kind: position
---
# Mula Benchmark Hanggang Pang-araw-araw na Paggamit: Ang Landas ng Post-Editing

> **Ang maikling bersyon.** Ang score sa leaderboard ay hindi produkto. Ang landas mula sa "ang method na ito ay may score na 0.78" hanggang sa "ang tanggapan ng band ay naglalathala ng mga dokumento sa wika bawat linggo" ay dumaraan sa iisang workflow lamang: gumagawa ang machine ng burador, iwawasto ito ng isang matatas na tagapagsalita, at tanging ang naiwastong teksto lamang ang ilalathala. Ang bawat quality threshold sa aming specs ay naka-calibrate sa workflow na iyon — hindi sa machine output na walang pangangasiwa, na hindi namin ineendorso para sa anumang wika sa platform na ito.

Minsan ay itinatanong ng mga tao kung kailan magiging "sapat ang ganda para basta gamitin" ang isang translation method. Para sa mga wikang pinaglilingkuran ng Arena na ito, may patibong ang tanong na iyon. Ang tapat na sagot ay ang pamantayang dapat puntiryahin ay hindi "sapat ang ganda para ilathala nang hindi nirerepaso" — kundi **"sapat ang ganda upang mas mainam ang pagrerepaso ng burador kaysa pagsasalin mula sa simula."** Mas mababa ang pamantayang iyon, nasusukat ito, at kapag nalampasan ito ay mababago kung ano ang kayang likhain ng isang community translation office sa loob ng isang linggo.

---

## Ang workflow, mula simula hanggang wakas

```
 English source document
        │
        ▼
 Machine draft  ←  a benchmarked, community-owned method
        │
        ▼
 Fluent-speaker post-edit  ←  the human gate; nothing skips it
        │
        ▼
 Published text  ←  carries human approval, not a machine score
        │
        ▼
 (Optional, community-controlled) corrections become
 data that improves the next version of the method
```

Tatlong bagay ang dapat mapansin:

1. **Hindi kailanman naglalathala ang machine.** Ang unit ng output ay burador. Ang correction pass ng tagapagsalita ay hindi quality assurance na idinagdag lamang sa dulo — ito mismo ang workflow.
2. **Ang oras ng tagapagsalita ang resource na ino-optimize.** Mas mabuti ang isang method kaysa sa ibang method eksakto sa antas na mas kaunti ang iniiwan nitong kailangang ayusin ng tagapagsalita. Patuloy na ipinapakita ng pananaliksik sa post-editing para sa mga wikang may sapat na resource na mas mabilis ito kaysa pagsasalin mula sa simula sa katamtamang kalidad ng MT (Plitt & Masselot 2010; Green, Heer & Manning 2013, parehong binanggit na may mga link sa [Ang Pagsasalin ay Hindi Revitalization](/docs/perspectives/translation-is-not-revitalization)). Kung totoo rin iyon para sa mga polysynthetic na wika ay eksaktong bagay na nilalayon ng benchmark na alamin — itinuturing namin ito bilang hipotesis na dapat beripikahin bawat wika, hindi bilang palagay.
3. **May malinaw na may-ari ang feedback loop.** Ang bawat naiwastong dokumento ay potensyal na datos para sa training at coaching — at ito ay pag-aari ng komunidad, upang ibalik (o hindi) ayon sa kanilang mga tuntunin sa ilalim ng mga patakaran sa [data sovereignty](/docs/sovereignty/data-sovereignty). Ang mekanismo ng feedback ay isang design goal ng platform, hindi pa isang built feature; tingnan ang [Pag-uulat ng Mga Error at Pagmamay-ari ng Mga Pagwawasto](/docs/perspectives/reporting-errors-and-owning-corrections) para sa kung paano nilalayong gumana ang mga pagwawasto at provenance.

## Ano ang ibig sabihin ng quality tiers para sa tunay na paggamit

Niraranggo ng leaderboard ang mga method batay sa composite ng mga automated metrics ([Espesipikasyon sa Scoring](/docs/specifications/scoring)), at ang mga score ay tumutugma sa mga pinangalanang tier. Narito ang tapat na pagsasalin ng mga tier na iyon sa mga termino ng pang-araw-araw na paggamit:

| Tier (composite) | Ano ang ibig sabihin nito para sa landas ng post-editing |
|---|---|
| **Baseline** (0.00–0.30) | Hindi magagamit para sa anumang bagay. Ang output ay sa malaking bahagi hindi ang target language. Kapaki-pakinabang lamang bilang research floor. |
| **Emerging** (0.30–0.50) | Hindi pa rin ito kasangkapan sa paggawa ng burador. Lumilitaw ang mga wastong fragment, ngunit mas maraming oras ang gugugulin ng tagapagsalita sa pag-aayos kaysa sa pagsusulat ng bago. |
| **Functional** (0.50–0.70) | Ang unang tier kung saan ang post-editing ay *maaaring* maging mas mainam kaysa pagsasalin mula sa simula para sa madaling mga teksto — karapat-dapat i-pilot kasama ang isang tagapagsalita, ngunit hindi pa karapat-dapat asahan. Nananatili ang madalas na mga pagkakamaling morpolohikal. |
| **Deployable** (0.70–0.85) | Ang target tier para sa workflow sa itaas: mga burador kung saan tama ang karamihan ng morphology at maaaring magwasto ang isang matatas na tagapagsalita nang makabuluhang mas mabilis kaysa muling pagsasalin. **Ang "Deployable" ay nangangahulugang deployable *sa loob ng post-editing workflow* — hindi kailanman "ilathala nang walang review."** |
| **Fluent** (0.85–1.00) | Papalapit sa mahusay na pagsasaling pantao; bihira at maliliit ang mga error. Nananatili ang review pass — nagiging mas mabilis lamang ito. |

May dalawang patakaran ng estruktural na katapatan sa ibabaw ng talahang ito, tuwirang mula sa [Espesipikasyon ng Benchmark §5 at §7](/docs/specifications/benchmark#5-quality-tiers):

- **Ang mga automated tier ay pansamantalang label, hindi hatol.** Mga nominasyon ang mga ito para sa human review. Muling ika-calibrate ang mga threshold habang naiipon ang speaker validation data, at maaari silang mauwi sa magkakaibang antas para sa iba't ibang wika.
- **Walang method ang maaaring mag-claim ng Deployable o mas mataas kung walang community review.** Isang istratipikadong sampol ng output nito ang ibibigay sa mga bilingual na tagapagsalita, na magra-rate sa bawat salin bilang *tanggihan / diwa / katanggap-tanggap / mahusay*. Ang governance organization — hindi ang leaderboard — ang magpapasya kung aabante ang method.

Bilang paghahambing, inilalarawan ng threshold ng [Founder's Prize](/docs/specifications/prizes) (composite ≥ 0.80, ≥99% na morphologically valid words, ≥70% na ni-rate ng tagapagsalita bilang katanggap-tanggap-o-mas-mahusay) ang isang method na ang natitirang mga pagkakamali ay *real-language errors* — maling inflection, hindi imbentong mga salita. Iyan ang hitsura sa mga numero ng "burador na sulit sa oras ng tagapagsalita."

## Mula winning method hanggang gumaganang opisina

Ipagpalagay na nalampasan ng isang method ang mga gate na iyon. Organisasyonal ang natitirang mga hakbang, at tinutukoy ang mga ito sa halip na iniimbento lamang:

1. **Lilipat ang pagmamay-ari.** Ang code ng method ay magiging pag-aari ng governance organization ng komunidad — pananatilihin ng developer ang attribution at publication rights ([Paglipat ng Pagmamay-ari](/docs/sovereignty/ownership-transfer)).
2. **Magiging service ang method.** Ipa-package ito bilang plugin at ihahatid sa pamamagitan ng deployment platform, habang kontrolado ng komunidad ang access, pricing, at mga pinahihintulutang paggamit ([I-deploy sa Production](/docs/getting-started/deploy-to-production)).
3. **Isasama ito ng mga translator sa kanilang araw.** Ituturo ng isang translation office ang umiiral nitong document workflow sa API ng method: papasok ang source text, lalabas ang burador, post-edit, publish. Dala ng nailathalang teksto ang pangalan at awtoridad ng translator — ang machine ay kasangkapan sa kanilang mesa, gaya ng diksyunaryo.
4. **Susunod ang revenue sa paggamit.** Ang mga outside developer na gumagamit ng method ay magbabayad ng metered rates, at 90% ng revenue na iyon ay dadaloy sa governance organization ([Ang Modelong Pang-ekonomiya](/docs/sovereignty/economic-model)) — na maaaring pondohan ang mas maraming oras ng translator, at isara ang loop.

## Nasaan na ito ngayon

Sa tuwirang salita: ang buong landas ay tinukoy mula simula hanggang wakas, at bahagyang naitayo. Umiiral na ang evaluation harness, metrics, run cards, at pampublikong leaderboard; umiiral na ang Plains Cree development corpus at isang aktibong prize; umiiral na ang deployment platform. Ang community review interface, evaluation sandbox, at corrected-text feedback loop ay tinukoy na ngunit hindi pa operational — minamarkahan sila ng specs bilang planned, at ganoon din kami. Wala pang method ang nakakumpleto ng buong paglalakbay mula benchmark hanggang pang-araw-araw na paggamit ng komunidad. Ang paglalakbay na iyon ang depinisyon ng tagumpay ng proyekto, kaya eksaktong dahilan iyon kung bakit hindi namin ito aangkinin nang maaga.

---

## Ano ang ibig sabihin nito para sa inyo

:::info Kung kayo ay miyembro ng komunidad
Ang badge na "Deployable" sa leaderboard ay hindi kailanman nangangahulugang maglalathala ang machine sa inyong wika nang walang pangangasiwa — nangangahulugan ito na maaaring handa na ang isang draft generator na *mag-audition* para sa inyong mga translator, ayon sa inyong mga tuntunin, at ang inyong mga tagapagsalita ang magiging mga hukom (mga binabayaran — tingnan ang [Paano Binabayaran ang Mga Tagapagsalita](/docs/perspectives/how-speakers-get-paid)). Kung nagpapatakbo ang inyong komunidad ng translation office, ang mahalagang tanong na dapat dalhin sa amin ay: "ano ang magiging itsura ng isang pilot, at sino ang magrerepaso ng output?"
:::

:::info Kung kayo ay researcher
Binabago ng framing ng post-editing kung ano ang karapat-dapat sukatin: time-to-acceptable-text na may tagapagsalita sa loop, hindi lamang composite score. Ang metrics ng Arena ay mga proxy para doon ([Espesipikasyon sa Scoring §1](/docs/specifications/scoring)), at ang mga post-editing study bawat wika para sa mga wikang komplikado ang morphology ay isang bukas na research gap na idinisenyong suportahan ng infrastructure na ito.
:::

:::info Kung kayo ay builder
Mag-optimize para sa editor, hindi para sa metric. Ang method na gumagawa ng tunay na mga salita na may paminsan-minsang maling inflection ay naaayos ng tagapagsalita sa loob ng ilang segundo; ang method na nagha-hallucinate ng mga anyong mukhang posible ay nilalason ang buong workflow — kaya naman napakahigpit ng gating sa morphological validity dito. Magsimula sa [Magsumite ng Method](/docs/getting-started/submit-a-method), at basahin ang [Method Interface](/docs/specifications/methods) para sa kung ano ang sa huli ay ibibigay ninyo kung mananalo kayo.
:::

## Tingnan din

- [Ang Pagsasalin ay Hindi Revitalization](/docs/perspectives/translation-is-not-revitalization) — kung bakit ang human gate ang punto, hindi isang limitasyon
- [Pag-uulat ng Mga Error at Pagmamay-ari ng Mga Pagwawasto](/docs/perspectives/reporting-errors-and-owning-corrections) — kung ano ang nangyayari kapag mali pa rin ang nailathalang teksto
- [Espesipikasyon ng Benchmark §7](/docs/specifications/benchmark#7-human-validation) — ang human validation gate, sa pormal na paraan