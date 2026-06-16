---
sidebar_position: 2
title: "Paglipat ng Pagmamay-ari"
---
# Paglipat ng Pagmamay-ari

> **Buod para sa Ehekutibo.** Kapag umabot ang isang pamamaraan ng pagsasalin sa Deployable tier (composite ≥ 0.70) at pumasa sa pagsusuri ng komunidad, ang pagmamay-ari ng code ay inililipat mula sa mananaliksik patungo sa organisasyong pamamahala ng Katutubo. Idinodokumento ng pahinang ito ang limang-yugtong pipeline ng paglipat, pagkakaayon sa OCAP®, at gabay para sa mga mananaliksik na bumubuo ng mga pamamaraan para sa mga wikang Katutubo.

Kapag nanalo ang isang pamamaraan ng pagsasalin sa Arena leaderboard, ano ang nangyayari sa code? Para sa mga wikang Katutubo at low-resource, ang sagot ay hindi “pinananatili ito ng mananaliksik.” Ang sagot ay: **pagmamay-ari ito ng komunidad.**

---

## Paano Ito Gumagana

Ipinapatupad ng Arena ang isang malinaw na pipeline mula sa pananaliksik tungo sa pagmamay-ari ng komunidad:

### 1. Pagbuo ng Pamamaraan
Bumubuo ang isang mananaliksik, estudyante, o developer ng pamamaraan ng pagsasalin — isang FST-gated pipeline, isang coached LLM, isang fine-tuned model, o anumang iba pang lapit. Binubuo nila ito gamit ang sarili nilang mga resource.

### 2. Ebalwasyon sa Arena
Ang pamamaraan ay ibinibenchmark sa pamamagitan ng [eval harness](/docs/specifications/harness). Ang bawat submission ay binibigyan ng fingerprint sa isang partikular na Git commit at bersyon ng dataset. Maaaring ulitin at mapatunayan ang mga score.

### 3. Pagsusuri ng Komunidad
Para sa mga pamamaraan para sa wikang Katutubo, sinusuri ang mga resulta ng mga manggagawa sa wika ng komunidad at mga organisasyong pamamahala. Pinatutunayan ng mataas na score sa leaderboard na *gumagana* ang pamamaraan; hindi nito pinatutunayan na ito ay *angkop*.

### 4. Paglipat ng Code
Kapag nakamit ng isang pamamaraan ang **Deployable** tier (composite score ≥ 0.70 laban sa gold-standard evaluation) **at** pumasa sa pagsusuri ng komunidad (human validation):
- Ibinibigay ng mananaliksik ang source code
- Ang legal na pagmamay-ari ay inililipat sa organisasyong pamamahala ng Katutubo (hal., tribal council, language authority, o organisasyong Métis)
- Hawak ng governance org ang mga encryption key para sa mga evaluation dataset
- Ang pamamaraan ay nagiging asset na kontrolado ng komunidad

Tingnan ang [Scoring Specification](/docs/specifications/scoring), §5 para sa mga depinisyon ng quality tier at ang [Benchmark Specification](/docs/specifications/benchmark), §8.3 para sa kumpletong mga kondisyon ng paglipat at §7 para sa human validation gate.

### 5. Deployment sa Produksyon
Ang pamamaraan ay ine-export bilang [champollion](https://champollion.dev) plugin at dine-deploy sa production API. Kinokontrol ng komunidad:
- Sino ang maaaring maka-access sa pamamaraan
- Anong mga termino sa pagpepresyo ang ilalapat
- Kung maaaring gamitin ang pamamaraan para sa komersiyal na layunin
- Kailan at paano ina-update ang pamamaraan

---

## Bakit Mahalaga Ito

Ang tradisyonal na pananaliksik sa ML ay sumusunod sa isang extractive na pattern:
1. Nangongolekta ang mananaliksik ng data mula sa isang komunidad
2. Nagsasanay ang mananaliksik ng model
3. Naglalathala ang mananaliksik ng papel
4. Walang natatanggap ang komunidad

Gumagana na ngayon ang pattern na ito sa industriyal na sukat. Ang OMT-1600 ng Meta (Marso 2026) ay nagsanay ng mga translation model para sa 1,600 wika — kabilang ang mga wikang Katutubo tulad ng Plains Cree — gamit ang web-scraped data at mga salin ng Bibliya. Sinanay ang mga model nang walang mga protocol ng pahintulot ng komunidad, kasalukuyang hindi available para i-download ang weights, at ang mga komunidad na ang mga wika ay minodel ay walang bahagi sa pagmamay-ari, walang papel sa pamamahala, at walang kita. Ang papel ang produkto. Ang komunidad ang pinagmumulan ng data.

Binabaligtad ito ng Arena:
1. Bumubuo ang mananaliksik ng isang pamamaraan
2. Pinatutunayan ito ng Arena laban sa mga corpus na kinurata ng komunidad gamit ang mga morphological metric
3. Natatanggap ng komunidad ang pagmamay-ari ng gumaganang code
4. Kumikita ang komunidad mula sa paggamit ng API

**Ito ang pangunahing pagkakaiba sa pagitan ng Champollion at ng bawat iba pang pagsisikap sa LRL MT, kabilang ang OMT-1600:** hindi lamang kami gumagawa ng mga pamamaraan para sa mga komunidad — inililipat namin ang pagmamay-ari ng mga pamamaraan *sa* mga komunidad. Ang code, ang weights, ang deployment infrastructure — lahat ng ito ay nagiging ari-arian ng komunidad. Hindi ito isang teoretikal na balangkas — ito ang operational pipeline para sa bawat pamamaraan para sa wikang Katutubo sa platform.

---

## Pagkakaayon sa OCAP®

Direktang ipinatutupad ng proseso ng paglipat ng pagmamay-ari ang [mga prinsipyo ng OCAP®](/docs/sovereignty/data-sovereignty):

| Prinsipyo | Implementasyon |
|---|---|
| **Pagmamay-ari** | Hawak ng governance org ang titulo sa method code at model weights |
| **Kontrol** | Kinokontrol ng governance org ang mga termino ng deployment, access, at pagpepresyo |
| **Access** | Ina-access ng mga miyembro ng komunidad ang pamamaraan sa pamamagitan ng champollion API o direktang download |
| **Pagkakaroon sa Posesyon** | Ang mga resource na lingguwistiko (coaching data, dictionaries, FST rules) ay nananatili sa infrastructure na kontrolado ng komunidad sa pamamagitan ng pamamaraang `api` |

---

## Para sa mga Mananaliksik

Kung kayo ay bumubuo ng pamamaraan para sa isang wikang Katutubo:

1. **Magtatag ng ugnayan** sa komunidad ng wika bago kayo magsimula
2. **Gumamit ng openly licensed data** para sa development (hindi mga resource na restricted sa komunidad)
3. **Idokumento ang provenance** sa inyong [run card](/docs/specifications/run-card) — ilista ang bawat resource, ang lisensya nito, at pinagmulan
4. **Maging handang maglipat** — kung magtagumpay ang inyong pamamaraan, ang code ay pagmamay-ari ng komunidad, hindi ninyo
5. **Ito ay isang feature, hindi limitasyon** — ang inyong ambag ay ang arkitektura at teknik, na maaari ninyong ilathala at muling gamitin. Ang ambag ng komunidad ay ang kaalamang lingguwistiko na nagpapagana nito para sa kanilang wika.

---

## Tingnan Din

- [Soberanya ng Data](/docs/sovereignty/data-sovereignty) — mga prinsipyo ng OCAP, CARE, at Te Mana Raraunga
- [Ang Modelong Pang-ekonomiya](/docs/sovereignty/economic-model) — kung paano nagiging kita ang pagmamay-ari
- [Suportahan ang isang Low-Resource Language](/docs/community/low-resource-languages) — ang konteksto ng pananaliksik