---
sidebar_position: 4
title: "Pag-uulat ng mga Error at Pagmamay-ari sa mga Pagwawasto"
slug: '/perspectives/reporting-errors-and-owning-corrections'
description: "Kung paano nag-uulat ang isang tagapagsalita ng maling impormasyon o hindi maayos na salin, kung sino ang nagpapasya sa susunod na hakbang, kung paano nagtataglay ng provenance ang mga pagwawasto, at kung bakit may kapangyarihang mag-veto ang mga komunidad sa datos ng kanilang wika."
related:
  - label: "Data Sovereignty"
    to: /docs/sovereignty/data-sovereignty
    kind: doc
    note: "Who holds veto power over language data"
  - label: "Ownership Transfer"
    to: /docs/sovereignty/ownership-transfer
    kind: doc
  - label: "Speaker Validation Protocol"
    to: /docs/specifications/speaker-validation
    kind: spec
  - label: "How Speakers Get Paid"
    to: /docs/perspectives/how-speakers-get-paid
    kind: position
---
# Pag-uulat ng mga Error at Pananagutan sa mga Pagwawasto

> **Paninindigan.** Hindi maiiwasang magkamali ang isang platform na naglalathala ng mga katotohanan at pagsusuri tungkol sa libo-libong wika. Ang *hindi* maiiwasan ay kung sino ang pinaniniwalaan kapag may iniulat na error, at kung sino ang mananagot sa pagwawasto. Ang aming sagot: mas mataas ang bigat ng ulat ng isang matatas na tagapagsalita kaysa sa aming automation, bawat pagwawasto ay may provenance na nagsasaad kung sino ang nagbago ng ano at bakit, at maaaring bawiin o i-veto ng isang komunidad ang paggamit ng datos ng kanilang wika — hindi bilang paggalang lamang, kundi bilang ipinatutupad na katangian ng architecture.

Itinuturing ng karamihan sa mga data platform ang mga ulat ng error bilang support tickets: may gumagamit na nagrereklamo, may maintainer na nagpapasya, tahimik na nagbabago ang tala. Para sa datos ng mga Indigenous na wika, baligtad ang modelong iyon. Ang taong nag-uulat ng error ay karaniwang mas may awtoridad kaysa sa platform — ang isang tagapagsalita na nagsasabi sa amin na mali ang isang salita ay hindi isang "user," sila ang ground truth na nagwawasto sa isang proxy. Ang disenyo sa ibaba ay nagmumula sa seryosong pagtingin dito.

---

## Dalawang uri ng error, isang prinsipyo

Naglalathala ang platform ng dalawang uri ng claim na maaaring mali:

1. **Mga katotohanan tungkol sa isang wika** — ang mga language card na gumagabay sa evaluation: classification data, orthography, linguistic features, kung aling metrics ang naaangkop. Maaaring mag-claim ang isang card ng maling tantiya ng bilang ng tagapagsalita, maling ugnayan ng dialect, maling status ng writing system.
2. **Mga paghatol tungkol sa mga salin** — isang reference translation sa corpus na itinuturing ng isang tagapagsalita na mali o hindi natural; isang automated metric na tumatanggi sa valid na salita o tumatanggap ng invalid na salita; isang badge na "Deployable" sa output na hindi tatanggapin ng mga tagapagsalita.

Ang prinsipyong sumasaklaw sa dalawa, na umiiral na sa [Scoring Specification](/docs/specifications/scoring) at [Benchmark Specification §7](/docs/specifications/benchmark#7-human-validation): **ang automated outputs ay proxies; ang mga tagapagsalita ang ground truth.** Tahasang inilalahad ito ng inilathalang commitment sa [Speaker Validation Protocol §6](/docs/specifications/speaker-validation#6-what-speakers-get): kung sinasabi ng isang tagapagsalita na mali ang linter tungkol sa isang bagay, aayusin namin ang linter.

## Paano dumaraan ang isang ulat

Narito ang dinaraanan ng isang ulat, na may tapat na status markers — ang ilan dito ay tumatakbo na ngayon, ang ilan ay tinukoy na ngunit hindi pa nabubuo.

**Pag-uulat ng maling salin o metric judgment (tumatakbo ngayon, sa direktang channel).** Ang isang tagapagsalita na nakakakita ng maling reference translation, salitang maling tinanggihan, o hindi katanggap-tanggap na "equivalent" ay maaaring mag-ulat nito sa public repository issue tracker ng proyekto o sa direktang pakikipag-ugnayan sa proyekto. Ang structured na bersyon nito — rating screens na may mga opsyong *reject / gist / acceptable / excellent* at free-text notes — ay ang community review interface, na tinukoy sa [Benchmark Specification §7.3](/docs/specifications/benchmark#7-human-validation) ngunit hindi pa live. Hanggang hindi pa ito live, hinahawakan ang mga ulat nang person-to-person, at ang mismong validation tasks (bayad, structured speaker review — tingnan ang [Paano Binabayaran ang mga Tagapagsalita](/docs/perspectives/how-speakers-get-paid)) ang pangunahing correction pipeline.

**Pag-uulat ng maling katotohanan sa isang language card (tumatakbo ngayon, parehong channels).** Sumusunod ang mga pagwawasto sa card sa parehong landas: ulat, review, versioned change. Dahil ang mga card ang nagtutulak sa evaluation behavior — kung aling metrics ang nilo-load, kung aling models ang inirerekomenda — maaaring baguhin ng pag-aayos sa card ang scores, kaya inilalapat ang mga pagwawasto bilang recorded data changes, hindi kailanman bilang tahimik na edits.

**Ano ang susunod na nangyayari — sino ang nagpapasya:**

- **Ang linguistic judgment calls ay nauukol sa mga tagapagsalita ng wikang iyon.** Kung valid ba ang isang anyo, kung magkatumbas ba ang dalawang phrasing, kung angkop ba ang isang register — ipinatutupad ng platform ang sagot; hindi ito ang nagbibigay nito. Kapag hindi nagkakasundo ang mga tagapagsalita (dialects, orthographic conventions), itinatala ang sagot bilang variation, hindi namin ito hinahatulan — sinusuportahan ng corpus at linter schemas ang pag-tag sa dialectal variants bilang acceptable alternatives sa halip na piliting magkaroon ng isang panalo.
- **Ang mga desisyon tungkol sa datos ng isang komunidad ay nauukol sa governance organization nito.** Para sa mga wikang may governance org, dumaraan sa kanila ang mga pagbabago sa evaluation corpora, pagtanggap ng mga pagwawasto sa sealed test sets, at deployment consequences — iyon ang Control principle ng [OCAP®](/docs/sovereignty/data-sovereignty) na ipinatutupad bilang proseso, hindi poster.
- **Inaayos lang ang mechanical errors.** Isang typo, sirang link, maling na-parse na field — iniuulat, itinatama, nilo-log. Hindi lahat ay nangangailangan ng konseho.

## May kasamang provenance ang mga pagwawasto

Ang pagwawastong hindi ninyo matutunton ay isa lamang mas bagong opinyon. Tatlong provenance rules ang nalalapat sa bawat katotohanan at bawat pag-aayos:

1. **Tinutukoy ng bawat katotohanan ang source nito.** Itinatala ng language cards at corpus entries kung saan nagmula ang bawat value — isang published dataset, community contribution, review ng tagapagsalita.
2. **Ang derived values ay nilalagyan ng label bilang amin, hindi sa upstream.** Kapag may kinukuwenta ang platform — isang aggregate, recoding, composite — itinatala ito bilang platform derivation *mula sa* upstream source, at hindi kailanman isinusulat sa ilalim ng pangalan ng upstream. Hindi dapat kailanman sisihin o bigyan ng kredito ang isang upstream dataset para sa isang numerong hindi nito inilathala.
3. **Nagiging bahagi ng record ang mga pagwawasto.** Itinatala ang pagwawasto ng isang tagapagsalita bilang isang bago at attributed assertion (pinangalanan o anonymous, ayon sa pagpili ng tagapagsalita — kaparehong terms ng validation work) na pumapalit sa lumang value; nananatiling auditable ang kasaysayan ng kung ano ang nagbago. Ang corpus versions ay hash-manifested ([Corpus Partnership §4.4](/docs/specifications/corpus-partnership)), kaya ang isang corrected corpus ay malinaw na bagong version, at itinatala ng bawat run card ang eksaktong version kung saan ito na-score — nananatiling naiinterpret ang lumang scores, at sumasalamin ang bagong scores sa pag-aayos.

## Ang veto, sa kongkretong paraan

Madaling i-claim ang "community control." Narito kung ano ang aktuwal na kahulugan nito sa inilathalang architecture:

- **Maaaring bawiin ng mga tagapagsalita ang kanilang contributions.** Maaaring bawiin ng isang tagapagsalita ang kanilang ratings anumang oras, at inaalis sila ng withdrawal mula sa lahat ng analyses ([Speaker Validation §5](/docs/specifications/speaker-validation#5-data-governance)). Mayroon ding veto power ang mga tagapagsalita sa publication ng results na itinuturing nilang problematic.
- **Maaaring ganap na ihinto ng mga komunidad ang evaluation.** Naka-encrypt ang sealed test sets, na may keys na hawak sa paraang hindi kailanman muling mabubuo ng platform nang mag-isa ang mga ito; maaaring bawiin ng isang komunidad ang evaluation access sa pamamagitan ng pagtangging lumahok sa key reconstruction ([Corpus Partnership §4.3](/docs/specifications/corpus-partnership#4-cryptographic-sealing-and-sandbox-testing)). May tinukoy na sagot sa "Paano kung gusto naming huminto?": hindi kailanman inilalantad ang sealed data, at nagtatapos ang evaluation.
- **Walang score na nangingibabaw sa desisyon ng komunidad.** Ang isang method na nangunguna sa leaderboard ay dine-deploy pa rin lamang kung papayag ang governance organization ([Ownership Transfer](/docs/sovereignty/ownership-transfer)) — at ang isang komunidad na nagpapasyang hindi dapat i-deploy ang MT para sa kanilang wika sa anumang paraan ay gumagamit sa system ayon sa disenyo nito, hindi sinisira ito (tingnan ang [Ang Translation ay Hindi Revitalization](/docs/perspectives/translation-is-not-revitalization)).

## Ano ang hindi pa namin nabubuo

Sa diwa ng natitirang bahagi ng shelf na ito: planado ang community review interface, hindi pa live. Wala pang naitatag na governance organizations para sa alinman sa kasalukuyang mga wika — nasa confirmation ang community custodianship para sa Plains Cree benchmark, at hindi namin pinapangalanan sa publiko ang custodians bago sila pumayag. Hanggang umiral ang mga bahaging iyon, dumaraan ang mga pagwawasto sa direkta at attributable na channels, at ang mga inilathalang specs — hindi ang pahinang ito — ang nananatiling binding description ng proseso. Kapag hindi nagkasundo ang pahinang ito at ang isang spec, ang spec ang mananaig, at ituturing din namin ang hindi pagkakasundong iyon bilang bug na karapat-dapat iulat.

---

## Ano ang ibig sabihin nito para sa inyo

:::info Kung kayo ay miyembro ng komunidad
Kung may mali tungkol sa inyong wika sa platform na ito — isang katotohanan, isang salin, isang label — ang inyong ulat ay patotoo mula sa ground truth, hindi isang reklamong ita-triage. Kayo ang magpapasya kung kikilalanin ang inyong pagwawasto sa pangalan; maaaring bawiin ang inyong contribution sa kalaunan; at maaaring ganap na ihinto ng inyong komunidad ang paggamit ng datos nito. Magsimula sa [Para sa mga Komunidad ng Wika](/docs/community/for-language-communities), o magbukas lang ng issue sa public repository.
:::

:::info Kung kayo ay researcher
Ang mga pagwawasto rito ay datos na may provenance, hindi tahimik na edits: naka-hash ang corpus versions, ipinapako ng run cards ang eksaktong version kung saan na-score ang mga ito, at nilalagyan ng label ang derived values bilang derivations. Kung gagamit kayo ng Arena scores o corpora, banggitin ang version — at ituring ang isang speaker-driven correction wave bilang finding tungkol sa metric validity, dahil iyon talaga ito.
:::

:::info Kung kayo ay builder
Maaaring lehitimong magbago ang score ng inyong method kahit hindi nagbabago ang inyong code — na-a-allowlist ang isang salitang maling tinanggihan, naitatama ang isang reference translation, naaayos ang isang variant class. Idisenyo para rito: i-pin ang corpus versions sa inyong run cards ([Run Card spec](/docs/specifications/run-card)), bantayan ang dataset changelogs, at ituring ang speaker corrections bilang pinakamaaasahang error signal na makukuha ninyo nang libre.
:::

## Tingnan din

- [Paano Binabayaran ang mga Tagapagsalita](/docs/perspectives/how-speakers-get-paid) — ang parehong speaker authority, sa benchmark stage
- [Mula Benchmark hanggang Pang-araw-araw na Paggamit](/docs/perspectives/from-benchmark-to-daily-use) — kung saan nagtatagpo ang mga pagwawasto at ang publishing workflow
- [Data Sovereignty](/docs/sovereignty/data-sovereignty) — OCAP®, CARE, at Te Mana Raraunga, ang mga prinsipyong nasa likod ng disenyong ito