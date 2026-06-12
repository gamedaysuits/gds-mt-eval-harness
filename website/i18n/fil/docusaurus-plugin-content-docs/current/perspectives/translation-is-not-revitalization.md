---
sidebar_position: 1
title: "Ang Pagsasalin ay Hindi Muling Pagpapasigla"
slug: '/perspectives/translation-is-not-revitalization'
description: "Kung ano ang kaya at hindi kayang gawin ng machine translation para sa mga nanganganib na wika — ipinapahayag nang malinaw. Ang MT ay imprastraktura para sa mga pamayanang pangwika. Hindi ito kailanman pumapalit sa pakikipag-usap ng tao sa kapwa tao."
related:
  - label: "How Speakers Get Paid"
    to: /docs/perspectives/how-speakers-get-paid
    kind: position
  - label: "From Benchmark to Daily Use"
    to: /docs/perspectives/from-benchmark-to-daily-use
    kind: position
    note: "The post-editing path from draft to published text"
  - label: "Data Sovereignty"
    to: /docs/sovereignty/data-sovereignty
    kind: doc
    note: "OCAP, CARE, and consent before deployment"
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
---
# Ang Pagsasalin ay Hindi Muling Pagpapasigla

> **Posisyon.** Ang machine translation ay nagko-convert ng teksto sa pagitan ng mga wika. Ang muling pagpapasigla ay lumilikha ng mga bagong tagapagsalita. Magkaibang gawain ang mga ito na may magkaibang pamantayan ng tagumpay, at walang leaderboard score na makapagbabago niyan. Itinatayo namin ang MT bilang imprastrakturang naglilingkod sa mga layunin ng isang komunidad — kailanman ay hindi bilang kapalit ng pagpapasa ng wika sa pagitan ng mga henerasyon. Natututo ang mga bata ng wika mula sa mga tao, hindi sa mga makina.

Noong 2026, madaling maniwala na kayang ayusin ng software ang anumang bagay, kabilang ang isang wikang nawawalan ng mga tagapagsalita. Nais naming maging tiyak kung bakit mali ang paniniwalang iyon — at kung ano ang maaari talagang maiambag ng teknolohiya ng pagsasalin nang tapat.

Umiiral ang pirasong ito dahil isang linguist na inimbitahan naming pumuna sa proyektong ito ang mariing nangatwiran: hindi lulutasin ng isang perpektong English→Cree translation system ang problema sa pagpapasa ng wika (mga batang hindi natututo ng wika sa tahanan), ang problema sa prestihiyo (English bilang wika ng kapangyarihang pang-ekonomiya), o ang problemang pedagohikal (hindi sapat ang immersion schools at mga sinanay na guro). Maaari pa nga nitong palalain ang mga bagay, sa pamamagitan ng paglikha ng ilusyon na "nakapagsasalita ng Cree ang computer" at pagpapalambot sa pagkaapurahan ng pagpapasa ng wika ng tao. Tinanggap namin ang malaking bahagi ng kritisismong iyon, at inilalathala namin dito ang aming tugon sa halip na ibaon ito.

---

## Ang talagang kinakailangan ng muling pagpapasigla

Pare-pareho ang pananaliksik sa literature tungkol sa language revitalization sa isang punto: nabubuhay ang mga wika kapag naipapasa ang mga ito sa pagitan ng mga henerasyon — kapag sinasalita ng mga magulang, lolo't lola, at mga komunidad ang mga ito sa mga bata, at lumalaki ang mga batang sinasagot sila gamit ang mga wikang iyon (Fishman 1991; Hinton & Hale 2001). Lahat ng iba pa — mga paaralan, media, diksyunaryo, apps — ay sumusuporta sa pagpapasang iyon o wala itong sinusuportahan.

Walang translation system ang nakikilahok sa palitang iyon. Ang model na nagko-convert ng isang English document tungo sa Plains Cree ay hindi lumilikha ng tagapagsalita. Hindi nito pinupunuan ng tauhan ang isang immersion classroom, sinasanay ang isang guro, o umuupo kasama ang isang bata sa mesa sa kusina. Kung kailanman ay ilarawan ang aming gawain bilang "pagliligtas ng mga wika," mali ang paglalarawang iyon at sasabihin namin iyon.

## Ang hindi kayang gawin ng MT

Tuwirang inilalahad, upang walang kalabuan kalaunan:

- **Hindi nito kayang palitan ang mga tagapagsalita.** Ang output na hindi pa nasusuri ng fluent speaker ay draft, hindi teksto. Itinuturing ng sarili naming [mga panuntunan sa scoring](/docs/specifications/scoring) ang bawat automated score bilang proxy; human review lamang ang nagpapatunay ng usability.
- **Hindi nito kayang magturo ng unang wika.** Natatamo ng mga bata ang wika sa pamamagitan ng ugnayan at immersion, hindi sa pamamagitan ng mga isinaling dokumento.
- **Maaari itong lumikha ng mapaminsalang ilusyon.** Ang demo na "nagsasalita" ng isang wika ay maaaring magpahiwatig na ligtas ang wika kahit hindi naman. Totoo ang panganib na ito sa prestihiyo, at itinuturing namin ito bilang bukas na tanong na dapat suriin *kasama* ang mga komunidad, hindi bilang talking point na dapat pamahalaan.
- **Hindi ito kayang magpasya ng anuman.** Kung dapat bang umiral ang translation system para sa isang wika, at kung saan ito maaaring gamitin, ay pasya ng komunidad — kabilang ang pasyang huwag itong i-deploy kahit kailan. Nakapaloob ang kontrol na iyon sa arkitektura ng [paglilipat ng pagmamay-ari](/docs/sovereignty/ownership-transfer) at [data sovereignty](/docs/sovereignty/data-sovereignty), at kasama rito ang mga konteksto: maaaring tanggapin ng isang komunidad ang MT para sa mga opisyal na dokumento at tanggihan ito para sa classroom materials.

## Ang tapat na kayang gawin ng MT

Sa harap ng kontekstong iyon, may mga kongkreto at may hangganang bagay na naiaambag ng imprastraktura ng pagsasalin — bawat isa ay naglilingkod sa mga taong gumagawa na ng tunay na gawain.

**1. Throughput para sa mga overloaded translator.** Humaharap ang mga tanggapan ng pagsasalin sa komunidad sa mas maraming dokumentong *dapat* umiral sa wika kaysa sa kayang likhain mula sa simula ng mga human translator. Binabago ng machine draft ang trabaho mula sa "isalin ang lahat" tungo sa "suriin at itama" — at natuklasan ng controlled studies na makabuluhang mas mabilis ang post-editing kaysa sa pagsasalin mula sa simula, habang napapanatili o napapabuti ang kalidad (Plitt & Masselot 2010; Green, Heer & Manning 2013). Inilalarawan namin nang detalyado ang workflow na ito sa [Mula Benchmark tungo sa Pang-araw-araw na Paggamit](/docs/perspectives/from-benchmark-to-daily-use). Ang pag-iingat: sinaklaw ng mga pag-aaral na iyon ang high-resource language pairs; wala pa kaming katumbas na ebidensiya para sa polysynthetic languages, na bahagi ng itinatakdang sukatin ng proyektong ito.

**2. Praktikal na leverage para sa mga karapatan sa wika.** Umiiral sa batas ang karapatan sa mga serbisyo ng pamahalaan sa Indigenous languages sa ilang hurisdiksyon. Ang kadalasang kulang ay ang praktikal na kapasidad na makagawa ng mga pagsasalin sa bilis na hinihingi ng burukrasya. Ang komunidad na kayang gawing reviewed translation ang isang limampung-pahinang policy document sa loob ng mga araw sa halip na mga buwan ay nasa mas matatag na posisyon sa pakikipagnegosasyon. Hindi nililikha ng teknolohiya ang karapatan; ginagawa nitong mas mahirap balewalain ang karapatan.

**3. Magagamit-muling linguistic infrastructure.** Ang morphological analyzer (FST) na ginagamit namin upang tiyakin na ang translation output ay naglalaman ng mga tunay na salita — hindi mga hallucinated na salita — ay nag-e-encode kung *bakit* valid ang bawat word form. Ang parehong machinery na iyon ang pundasyon para sa learning tools: conjugation trainers, error-correcting writing aids, morphological explorers. Ang verification engine at ang pedagogical engine ay iisang artifact. Isa itong landas, hindi pangako — kinakailangan pang buuin ang learning tools, at pasya ng komunidad kung bubuuin ang mga ito.

**4. Suporta para sa second-language learners.** Ang muling pagpapasigla ay hindi lamang mga batang natututo ng unang wika. Ito rin ay mga nasa hustong gulang na natututo bilang second language — mga taong maaaring hindi kailanman umabot sa fluency na antas ng Elder ngunit kayang magbasa ng mga dokumento ng komunidad, lumahok nang may pag-unawa, at itaas ang pampublikong presensiya ng wika sa pamamagitan ng paggamit nito. Para sa populasyong ito, tunay na tool ang translation aid, tulad ng pagiging tool ng diksyunaryo.

**5. Dahilan upang mapondohan at maari sa sariling komunidad ang gawain.** Sa aming model, ang mga napatunayang pamamaraan ay [inililipat sa pagmamay-ari ng komunidad](/docs/sovereignty/ownership-transfer) at ang API revenue ay dumadaloy nang napakalaki sa komunidad ([ang modelong pang-ekonomiya](/docs/sovereignty/economic-model)). Ang mga tagapagsalita ay [binabayaran para sa kanilang expertise](/docs/perspectives/how-speakers-get-paid), hindi hinihilingang i-volunteer ito. Wala rin sa mga iyon ang mismong muling pagpapasigla — ngunit idinidirekta nito ang resources tungo sa mga taong gumagawa ng revitalization, sa halip na palayo sa kanila.

## Ang tapat na pag-frame

Mahaba ang rekord ng larangan pagdating sa mga proyektong teknolohiya na dumarating na may mga salaysay ng pagliligtas at umaalis na may mga publikasyon (Bird 2020). Sinisikap naming panatilihin ang mas makitid na pahayag: **Ang MT ay imprastraktura.** Ang imprastraktura ay naglilingkod sa mga layuning itinakda ng ibang tao. Hindi nagpapasya ang mga kalsada kung saan kayo maglalakbay; hindi nagpapasya ang teknolohiyang ito kung mabubuhay ang isang wika. Ang mga tagapagsalita, pamilya, at komunidad ang gumagawa niyon — at tama ang framing ng [UNESCO International Decade of Indigenous Languages](https://idil2022-2032.org/) na ilagay ang Indigenous peoples, hindi ang tools, sa sentro.

Kung magpasiya ang isang komunidad na nakatutulong ang translation technology sa kanilang mga layunin, nais naming ito ang maging pinakamainam at pinakapananagutang bersiyon na posible — pag-aari nila, validated ng kanilang mga tagapagsalita, at deployed ayon sa kanilang mga tuntunin. Kung magpasiya ang isang komunidad na hindi ito nakatutulong, valid na kinalabasan ng proyektong ito ang konklusyong iyon, hindi kabiguan nito. Ang dalawang bahagi ng pangungusap na iyon ay kapwa mga pangako.

---

## Ano ang ibig sabihin nito para sa inyo

:::info Kung kayo ay miyembro ng komunidad
Hindi sasabihin sa inyo ng proyektong ito na kayang iligtas ng app ang inyong wika — hindi nito kaya. May hangganan ang iniaalok nito: mas mabilis na pagsasalin ng dokumento sa ilalim ng review ng fluent speaker, imprastrakturang ganap na maaaring ariin ng inyong komunidad, at kompensasyon para sa expertise ng mga tagapagsalita. Kung gagamitin man ito at paano ito gagamitin ay pasya ng inyong komunidad, kabilang ang pasyang huwag itong gamitin. Tingnan ang [Para sa Mga Komunidad ng Wika](/docs/community/for-language-communities) at [Pag-uulat ng Mga Error at Pagmamay-ari sa Mga Pagwawasto](/docs/perspectives/reporting-errors-and-owning-corrections).
:::

:::info Kung kayo ay mananaliksik
Ituring ang "MT for endangered languages" bilang pahayag tungkol sa imprastraktura, hindi bilang pahayag tungkol sa revitalization, at magbabago ang inyong tanong sa evaluation: hindi "mataas ba ang BLEU score?" kundi "nasusukat ba nitong binabawasan ang workload ng mga taong gumagawa ng tunay na gawain, ayon sa kanilang mga tuntunin?" Ang [benchmark specification](/docs/specifications/benchmark) at [Paano Ito Gumagana §8 (Mga Tensiyon at Limitasyon)](/docs/how-it-works#8-tensions-and-limitations) ang mga lugar kung saan pinapanagot namin ang aming sarili sa pamantayang iyon.
:::

:::info Kung kayo ay builder
Bumuo para sa post-editing workflow, hindi para sa demo. Ang gumagamit ng inyong method ay isang fluent speaker na nagwawasto ng draft, at ang pinakamasamang failure mode ay mga hallucinated na salitang mukhang kapani-paniwala sa mga hindi tagapagsalita — kaya naman morphological validation ang nagsasala sa lahat dito. Magsimula sa [Magsumite ng Method](/docs/getting-started/submit-a-method) at [Mula Benchmark tungo sa Pang-araw-araw na Paggamit](/docs/perspectives/from-benchmark-to-daily-use).
:::

---

## Mga Sanggunian

- Fishman, J. A. (1991). *Reversing Language Shift: Theoretical and Empirical Foundations of Assistance to Threatened Languages.* Multilingual Matters.
- Hinton, L., & Hale, K. (eds.) (2001). *The Green Book of Language Revitalization in Practice.* Academic Press.
- Plitt, M., & Masselot, F. (2010). "A Productivity Test of Statistical Machine Translation Post-Editing in a Typical Localisation Context." *The Prague Bulletin of Mathematical Linguistics*, 93, 7–16. [PDF](https://ufal.mff.cuni.cz/pbml/93/art-plitt-masselot.pdf)
- Green, S., Heer, J., & Manning, C. D. (2013). "The Efficacy of Human Post-Editing for Language Translation." *Proceedings of CHI 2013.* [Papel](https://idl.uw.edu/papers/post-editing)
- Bird, S. (2020). "Decolonising Speech and Language Technology." *Proceedings of COLING 2020*, 3504–3519. [Papel](https://aclanthology.org/2020.coling-main.42/)
- UNESCO. *International Decade of Indigenous Languages 2022–2032.* [idil2022-2032.org](https://idil2022-2032.org/)

## Tingnan din

- [Paano Binabayaran ang Mga Tagapagsalita](/docs/perspectives/how-speakers-get-paid) — ang compensation model, sa mga numero
- [Mula Benchmark tungo sa Pang-araw-araw na Paggamit](/docs/perspectives/from-benchmark-to-daily-use) — ang post-editing path
- [Paano Ito Gumagana](/docs/how-it-works) — ang buong platform architecture, kabilang ang §8 tungkol sa mga tensiyong hindi pa namin nalulutas