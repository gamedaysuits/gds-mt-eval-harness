---
sidebar_position: 7
title: "Soberanya ng Datos"
description: "Mga prinsipyo ng OCAP, CARE, at Māori Data Sovereignty para sa pagsasalin ng mga wikang Katutubo. Bakit nauuna ang pahintulot ng komunidad bago ang deployment."
related:
  - label: "Ownership Transfer"
    to: /docs/sovereignty/ownership-transfer
    kind: doc
    note: "How control of language data moves to communities"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
---
# Soberanya ng Datos

> **Ehekutibong Buod.** Ipinapaliwanag ng pahinang ito ang mga prinsipyo ng soberanya ng datos na OCAP®, CARE, at Te Mana Raraunga at kung ano ang kahulugan ng mga ito para sa mga developer na bumubuo ng mga paraan ng pagsasalin para sa mga Katutubong wika. Sinasaklaw nito kung kailan kinakailangan ang pahintulot ng komunidad, kung paano sinusuportahan ng arkitektura ng method na `api` ng champollion ang soberanya ng datos, at ang mga etikal na obligasyon ng sinumang nagtatrabaho gamit ang Katutubong datos lingguwistiko.

Ang machine translation para sa mga Katutubong wika ay nagbubukas ng mga tanong na hindi umiiral para sa French o Japanese. Sino ang nagmamay-ari ng training data? Sino ang kumokontrol kung paano magsasalita ang isang language model? Sino ang nagpapasiya kung sapat na ang kalidad ng isang salin upang ilathala?

**Ang sagot ay palaging ang komunidad.**

Itinayo ang champollion upang suportahan ito. Pinapanatili ng method na `api` ang lahat ng linguistic resources sa server-side sa ilalim ng kontrol ng komunidad. Pinaghihiwalay ng plugin system ang method mula sa tool. Ngunit hindi maipatutupad ng tool ang etika — ipinapaliwanag ng pahinang ito ang mga prinsipyong dapat ninyong sundin.

---

## Mga Prinsipyo ng OCAP®

Ang **OCAP** (Ownership, Control, Access, Possession) ay isang hanay ng mga prinsipyong binuo ng [First Nations Information Governance Centre](https://fnigc.ca/ocap-training/) (FNIGC) na nagtatakda kung paano dapat kolektahin, protektahan, gamitin, at ibahagi ang datos ng First Nations.

| Prinsipyo | Ano ang Kahulugan Nito para sa Pagsasalin |
|-----------|------------------------------|
| **Ownership** | Pagmamay-ari ng komunidad ang datos lingguwistiko nito — mga diksyunaryo, gramatika, parallel texts, coaching files, at anumang saling nagawa mula sa mga ito. |
| **Control** | Kinokontrol ng komunidad kung paano ginagamit ang datos ng wika nito, sino ang may access, at aling mga paraan ng pagsasalin ang katanggap-tanggap. |
| **Access** | May karapatan ang mga kasapi ng komunidad na ma-access at mapamahalaan ang sarili nilang language resources saanman nakaimbak ang mga ito. |
| **Possession** | Ang pisikal na datos (coaching files, mga diksyunaryo, model weights) ay dapat manatili sa imprastrukturang kinokontrol ng komunidad — hindi sa third-party cloud. |

### Ano ang ibig sabihin ng OCAP sa praktika

- **Huwag maglathala ng mga salin** ng isang Katutubong wika nang walang tahasang awtorisasyon ng komunidad.
- **Huwag mag-train ng mga modelo** gamit ang datos lingguwistiko na ibinigay ng komunidad nang walang data-sharing agreement.
- **Huwag mag-scrape** ng community language resources mula sa mga website, social media, o materyales na pang-edukasyon.
- **Gamitin ang method na `api`** upang manatili sa mga server na kontrolado ng komunidad ang prompts, coaching data, at mga diksyunaryo. Ang method na `api` ng champollion ay isang "dumb pipe" — nagpapadala ito ng keys palabas at tumatanggap ng translations pabalik. Nananatili sa server-side ang lahat ng linguistic IP.
- **Idokumento ang provenance** — dapat ilista ng field na `provenance` sa [plugin manifest](https://champollion.dev/docs/reference/plugin-spec) ang bawat resource na ginamit, ang lisensiya nito, at ang pinagmulan nito.

:::warning Ang OCAP® ay isang rehistradong trademark
Ang OCAP® ay isang rehistradong trademark ng First Nations Information Governance Centre. Partikular itong nalalapat sa First Nations sa Canada. Mas malawak ang kaugnayan ng mga prinsipyo, ngunit ang trademark at awtoridad sa pamamahala ay pag-aari ng FNIGC.
:::

---

## Mga Prinsipyo ng CARE

Ang **CARE Principles for Indigenous Data Governance** ay binuo ng [Global Indigenous Data Alliance](https://www.gida-global.org/care) (GIDA) bilang katuwang ng FAIR data principles. Sinasabi ng FAIR na dapat ang datos ay Findable, Accessible, Interoperable, at Reusable. Sinasabi ng CARE na hindi sapat iyon — dapat ding isentro ng pamamahala ng datos ang mga karapatan ng mga Katutubo.

| Prinsipyo | Aplikasyon |
|-----------|------------|
| **Collective Benefit** | Dapat makinabang muna ang komunidad ng wika sa mga translation tool. Ang leaderboard scores ay paraan upang mapahusay ang mga method, hindi upang kumuha ng komersyal na halaga mula sa mga wika ng komunidad. |
| **Authority to Control** | May awtoridad ang mga komunidad na pamahalaan kung paano kinokolekta, ginagamit, at ibinabahagi ang datos ng kanilang wika. Ang mataas na leaderboard score ay hindi nagbibigay ng pahintulot na maglathala ng mga salin. |
| **Responsibility** | May responsibilidad ang mga mananaliksik at developer na nagtatrabaho gamit ang datos ng Katutubong wika na bumuo ng mga ugnayan, kumuha ng pahintulot, at magbahagi ng mga benepisyo. |
| **Ethics** | Dapat maging pangunahing alalahanin ang mga karapatan at kapakanan ng mga Katutubo. Dapat paunlarin ang mga paraan ng pagsasalin *kasama* ang mga komunidad, hindi *tungkol* sa kanila. |

---

## Te Mana Raraunga — Soberanya ng Datos ng Māori

Ang **Te Mana Raraunga** ay ang [Māori Data Sovereignty Network](https://www.temanararaunga.maori.nz/). Iginigiit nito na ang datos ng Māori — kabilang ang datos ng wika — ay isang taonga (kayamanan) na saklaw ng mga prinsipyo ng Treaty of Waitangi at tikanga Māori (Māori customary law).

Mahahalagang prinsipyo:

| Prinsipyo | Kahulugan |
|-----------|---------|
| **Rangatiratanga** (Awtoridad) | May likas na karapatan ang Māori na gamitin ang awtoridad sa kanilang datos, kabilang ang datos ng wika. |
| **Whakapapa** (Mga Ugnayan) | May pinagmulan at mga koneksyon ang datos. Dala ng datos ng wika ang mga ugnayan at kaalaman ng mga taong lumikha nito. |
| **Whanaungatanga** (Mga Obligasyon) | Ang mga may hawak o nagpoproseso ng datos ng Māori ay may mga katumbas na obligasyon sa mga komunidad na pinagmulan nito. |
| **Kotahitanga** (Kolektibong benepisyo) | Dapat gamitin ang datos ng Māori para sa kolektibong benepisyo ng Māori. |
| **Manaakitanga** (Mutuwalidad) | Dapat kasangkot sa paggamit ng datos ng Māori ang pangangalaga, paggalang, at mutuwalidad. |
| **Kaitiakitanga** (Pagbabantay) | May tungkulin ang data guardians na protektahan ang datos at tiyaking ginagamit ito nang angkop. |

Nalalapat ang mga prinsipyong ito sa te reo Māori (ang wikang Māori) at sa anumang computational work na kinasasangkutan ng datos ng wikang Māori.

---

## Ano ang Kahulugan Nito para sa mga User ng champollion

### Para sa mga standard na wika (French, Japanese, Spanish...)

Gamitin ang champollion nang normal. Ang mga wikang ito ay may malalaking corpus na pampublikong magagamit, matatag na translation APIs, at walang alalahanin sa soberanya. Magsalin, mag-sync, at maglathala ayon sa inyong nais.

### Para sa mga Katutubong wika at wikang may kaunting mapagkukunan

Pundamental na naiiba ang sitwasyon:

1. **Kumuha muna ng pahintulot.** Bago bumuo ng paraan ng pagsasalin para sa isang Katutubong wika, magtatag muna ng ugnayan sa komunidad. Ang method na binuo nang walang pakikilahok ng komunidad — gaano man ito kahusay sa teknikal — ay hindi dapat ilathala o ipamahagi.

2. **Gamitin ang method na `api`.** I-host ang translation pipeline sa imprastrukturang kontrolado ng komunidad. Dinisenyo ang method na `api` sa champollion para dito: nagpapadala ito ng keys at tumatanggap ng translations pabalik nang hindi inilalantad ang prompts, mga diksyunaryo, o coaching data na nagpapagana sa method.

    ```json title="Community-controlled setup"
    {
      "pairs": {
        "en:crk": {
          "method": "api",
          "endpoint": "https://api.community-server.example/translate"
        }
      }
    }
    ```

3. **Idokumento ang lahat.** Gamitin ang field na `provenance` sa inyong plugin manifest upang ilista ang bawat resource, ang lisensiya nito, at kung ibinigay ba ito nang may pahintulot ng komunidad.

4. **Ang scores ay hindi mga lisensiya.** Pinatutunayan ng mataas na score sa leaderboard na mahusay ang teknikal na paggana ng isang method. Hindi ito nagbibigay ng pahintulot na maglathala ng mga salin, mamahagi ng plugin, o gawing komersyal ang method. Ang komunidad ang nagpapasiya.

5. **Ibahagi ang method, hindi ang datos.** Kung makabubuo kayo ng technique na mahusay gumana (hal., "FST-gated LLM with coached prompts"), ibahagi ang *architecture* at *approach* sa leaderboard. Pinananatili ng komunidad ang kontrol sa datos lingguwistiko na nagpapagana rito para sa kanilang partikular na wika.

---

## Ang Method na `api` at Soberanya

Ang [translation method](https://champollion.dev/docs/guides/translation-methods) na `api` ay umiiral partikular upang suportahan ang soberanya ng datos. Narito kung bakit:

| Aspeto | Ibang Methods | Method na `api` |
|--------|--------------|-------------|
| **Kung saan nakatira ang prompts** | Sa config files ng champollion (nakikita ng lahat ng developer) | Sa server ng komunidad (pribado) |
| **Kung saan nakatira ang coaching data** | Sa directory na `.champollion/coaching/` (committed sa git) | Sa server ng komunidad (pribado) |
| **Kung saan nakatira ang mga diksyunaryo** | Sa plugin directory (ipinamamahagi kasama ng plugin) | Sa server ng komunidad (pribado) |
| **Sino ang kumokontrol sa pipeline** | Sinumang nagpapatakbo ng `champollion sync` | Ang komunidad na nagpapatakbo ng API |
| **Ano ang nakikita ng champollion** | Lahat | Keys papasok, translations palabas |

Ang method na `api` ay isang sinadyang pagpiling pang-arkitektura. Isa itong "dumb pipe" dahil ang IP — ang kaalamang lingguwistiko, ang mga tuntunin ng gramatika, ang maingat na kinuratang coaching examples — ay pag-aari ng komunidad, hindi ng tool.

Tingnan ang [Pag-serve ng Method sa pamamagitan ng API](https://champollion.dev/docs/guides/serving-a-method) para sa mga detalye ng implementasyon.

---

## Case Study: OMT-1600 at Soberanya ng Datos

Ang OMT-1600 ng Meta (Marso 2026) ay nagbibigay ng kongkretong halimbawa kung bakit mahalaga ang soberanya ng datos para sa mga Katutubong wika. Nag-train ang OMT-1600 ng mga translation model para sa 1,600 wika gamit ang:

- **CC-2000-Web**: Monolingual text na web-scraped mula sa 2,000+ languoids — kinolekta nang walang pahintulot ng komunidad
- **Bible translations**: Mga tekstong panrelihiyon na ginamit bilang parallel training at evaluation data para sa mga wikang may pinakamababang mapagkukunan
- **MeDLEy**: Manually curated bitext — ngunit walang dokumentadong pagsunod sa OCAP® o CARE
- **Backtranslated synthetic data**: ~270 milyong synthetic parallel sentences na nilikha ng mismong mga modelo

Para sa mga Katutubong wika tulad ng Plains Cree (CRK), nangangahulugan ito ng:

| Prinsipyo | Praktika ng OMT-1600 | Epekto |
|-----------|-------------------|--------|
| **Ownership** | Pagmamay-ari ng Meta ang mga modelo at ito ang nagpapasiya kung paano ilalabas ang mga ito | Walang bahagi ang komunidad sa pagmamay-ari kung paano minomodelo ang kanilang wika |
| **Control** | Kinokontrol ng Meta ang pagpili ng training data, model architecture, at iskedyul ng release | Walang input ang komunidad sa kung anong datos ang ginagamit o kung paano kinakatawan ang wika |
| **Access** | Kasalukuyang hindi magagamit ang model weights — "not released due to factors outside the authors' control" | Hindi ma-access, masuri, o mabago ng komunidad ang modelong nagsasalita ng kanilang wika |
| **Possession** | Nasa imprastruktura ng Meta ang lahat ng datos at modelo | Hindi ma-host, ma-audit, o mabura ng komunidad ang datos na ginamit upang i-train ang modelo |

Ang OMT-1600 ay isang tagumpay sa pananaliksik. Isa rin itong halimbawa ng extractive data practice: kinolekta ang datos lingguwistiko mula sa web at mga tekstong panrelihiyon, pinroseso tungo sa isang modelo, at inilathala bilang papel — lahat nang walang pakikilahok, pahintulot, o benefit-sharing sa komunidad.

**Ito mismo ang pattern na pinipigilan ng sovereignty architecture ng champollion.** Pinapanatili ng method na `api` ang linguistic IP sa mga server na kontrolado ng komunidad. Ibinibigay ang evaluation corpora nang may pahintulot ng komunidad at iniimbak sa ilalim ng pangangalaga ng susi ng komunidad. Inililipat ang prize-winning methods sa pagmamay-ari ng komunidad. Hindi teknikal ang pagkakaiba — ito ay etikal at estruktural.

:::note Hindi natatanging may kasalanan ang OMT-1600
Ang pattern na ito — web scraping na sinusundan ng model training nang walang pahintulot ng komunidad — ay standard practice sa massively multilingual NLP research. Ang OMT-1600 ay isang case study dahil sa sukat nito (1,600 wika) at pagiging kamakailan nito (Marso 2026), hindi dahil natatangi itong extractive. Nalalapat ang parehong kritika sa NLLB-200, multilingual efforts ng Google, at karamihan ng large-scale MT research.
:::

---

## Karagdagang Babasahin

- [First Nations Information Governance Centre — OCAP®](https://fnigc.ca/ocap-training/)
- [Global Indigenous Data Alliance — CARE Principles](https://www.gida-global.org/care)
- [Te Mana Raraunga — Māori Data Sovereignty Network](https://www.temanararaunga.maori.nz/)
- [USIDSN — United States Indigenous Data Sovereignty Network](https://usindigenousdata.org/)

---

## Tingnan Din

- [Suportahan ang Wikang May Kaunting Mapagkukunan](/docs/community/low-resource-languages) — ang teknikal na gabay na may konteksto ng OCAP
- [Mga Paraan ng Pagsasalin](https://champollion.dev/docs/guides/translation-methods) — ang method na `api` at kung paano nito pinoprotektahan ang IP
- [Pag-serve ng Method sa pamamagitan ng API](https://champollion.dev/docs/guides/serving-a-method) — pag-host ng pipeline na kontrolado ng komunidad
- [Plugin Specification](https://champollion.dev/docs/reference/plugin-spec) — ang field na `provenance` para sa resource attribution
- [Cookbook: FST-Gated Pipeline](/docs/tutorials/fst-gated-pipeline) — pagbuo ng pipeline na maaaring i-self-host ng isang komunidad