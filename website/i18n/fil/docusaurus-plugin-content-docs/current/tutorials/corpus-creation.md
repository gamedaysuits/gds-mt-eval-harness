---
sidebar_position: 11
title: "Cookbook: Paglikha ng Corpus"
---
# Gabay sa Paglikha ng Corpus

> **Ang ideya:** Bago ninyo masuri ang isang pamamaraan ng pagsasalin, kailangan ninyo ng corpus ng ebalwasyon. Sinasaklaw ng gabay na ito kung paano bumuo ng isa mula sa simula — pagkuha ng data, mga kinakailangan sa format, mga pamantayan sa kalidad, paglilisensiya, at pag-aambag sa Arena.

:::info Hindi ito pamamaraan ng pagsasalin
Ang gabay na ito ay paunang kinakailangan para sa maraming pamamaraan. Ang isang mahusay na corpus ng ebalwasyon ang pundasyong nagpapaging posible sa lahat ng iba pa. Kahit 50 na piniling pares ay sapat upang magbukas ng bagong leaderboard track.
:::

## Kailan Ito Gagamitin

- Nais ninyong **magdagdag ng bagong pares ng wika** sa Arena leaderboard
- Kayo ay isang **guro ng wika** na nais mag-benchmark ng mga salin ng mag-aaral
- Kayo ay isang **manggagawa sa wikang pangkomunidad** na may access sa mga materyales na bilingual
- Kayo ay isang **mananaliksik** na nangangailangan ng standardized na evaluation set para sa inyong pares ng wika

## Format ng Corpus

Gumagamit ang harness ng simpleng JSON:

```json title="my-corpus.json"
{
  "metadata": {
    "name": "Quechua Dev v1",
    "version": "1.0.0",
    "source_language": "eng",
    "target_language": "que",
    "entry_count": 75,
    "license": "CC-BY-SA-4.0",
    "author": "Your Name / Organization",
    "description": "75 English-Quechua pairs from educational materials"
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello, how are you?",
      "reference": "Allillanchu, imaynallan kashanki?"
    },
    {
      "id": 2,
      "source": "The sun is shining today",
      "reference": "Kunan p'unchay inti k'anchashan"
    }
  ]
}
```

## Saan Kukuha ng Data

| Pinagmulan | Kalidad | Dami | Paglilisensiya |
|--------|---------|--------|-----------|
| **Mga textbook / materyales na pang-edukasyon** | Mataas (sinuri ng eksperto) | Mababa-katamtaman | Suriin sa publisher |
| **Mga dokumento ng pamahalaan** | Katamtaman (pormal na rehistro) | Katamtaman-mataas | Kadalasang public domain |
| **Mga bilingual dictionary** | Mataas (beripikadong entries) | Katamtaman | Nag-iiba-iba |
| **Mga nakatatanda / tagapagsalita sa komunidad** | Pinakamataas (katutubong intuwisyon) | Mababa (limitadong oras) | Pinamamahalaan ng komunidad |
| **Mga tekstong panrelihiyon** | Katamtaman (partikular sa domain) | Mataas | Karaniwang bukas |
| **Mga umiiral na corpora** (Hansard, FLORES) | Katamtaman-mataas | Mataas | Suriin ang lisensiya |
| **Gawang-kamay** | Pinakamataas | Mababa | Pag-aari ninyo ito |

## Mga Pamantayan sa Kalidad

Ang isang mahusay na corpus ng ebalwasyon ay may:

1. **Iba’t ibang nilalaman** — hindi lamang mga pagbati o simpleng parirala. Isama ang mga tanong, utos, kumplikadong pangungusap, at mga terminong partikular sa domain
2. **Beripikadong mga salin** — nirepaso ng kahit isang mahusay magsalitang tagapagsalita, mas mainam kung dalawa
3. **Konsistent na ortograpiya** — isang script, isang kumbensiyon sa pagbaybay sa kabuuan
4. **Malalayang pinagmulan** — hindi hinango mula sa parehong tekstong pagsasanayan ng mga pamamaraan
5. **Malinaw na paglilisensiya** — tahasang lisensiyang nagpapahintulot ng paggamit para sa ebalwasyon

:::danger Kontaminasyon ng corpus
Ang corpus ng ebalwasyon ay dapat **malaya** mula sa anumang training data. Kung ang isang pamamaraan ay sinanay o na-prompt gamit ang data mula sa corpus ng ebalwasyon, ito ay madidisqualify. Idisenyo ang inyong corpus upang maging held-out mula pa sa unang araw.
:::

## Mga Patnubay sa Laki

| Laki | Ano ang Pinahihintulutan Nito |
|------|----------------|
| **50 entries** | Pinakamababang viable na ebalwasyon — sapat upang matukoy ang malalaking pagkakaiba sa kalidad |
| **100–200 entries** | Maaasahang ranking — sapat para sa istatistikal na kahalagahan sa pagitan ng mga pamamaraan |
| **500+ entries** | Antas-pananaliksik — matitibay na composite scores, mga agwat ng kumpiyansa |
| **1,000+ entries** | Gold standard — katumbas ng saklaw ng FLORES devtest |

Magsimula nang maliit. Sapat ang 50 entries upang magbukas ng leaderboard track. Maaari ninyo itong palawakin kalaunan.

## Pag-aambag sa Arena

1. **Lumikha ng inyong corpus** sa JSON format sa itaas
2. **Lisensiyahan ito** — inirerekomenda ang CC BY-SA 4.0 para sa bukas na ebalwasyon; CC BY-NC-SA 4.0 para sa restricted na paggamit
3. **Magsumite ng PR** sa [eval harness repo](https://github.com/gamedaysuits/arena) kasama ang inyong corpus sa `data/`
4. **Awtomatikong magbubukas ang leaderboard** para sa inyong pares ng wika kapag na-merge na ang corpus

## Para sa mga Indigenous Language Community

Ang paglikha ng corpus ay isang gawa ng **soberanya ng wika**. Ang inyong corpus, ang inyong mga tuntunin:

- Kayo ang nagpapasya sa lisensiya at mga kondisyon sa access
- Maaari kayong mag-ambag ng **pampublikong development set** (para sa pagbuo ng pamamaraan) habang pinananatili ang isang **lihim na test set** (para sa opisyal na ebalwasyon) sa ilalim ng kontrol ng komunidad
- Pinoprotektahan ng [balangkas ng soberanya](/docs/sovereignty/data-sovereignty) ang inyong data sa bawat antas

Kahit ang isang maliit na corpus ay isang **estratehikong asset** — ito ang benchmark na nagpapasya kung ano ang ibig sabihin ng "sapat na mabuti" para sa inyong wika.

## Mahusay Isama Sa

- **[Bahagyang Pagsasalin](./partial-translation)** — ang paglikha ng corpus AY ang hakbang ng pagsasalin ng tao
- **[Back-Translation](./back-translation)** — dinaragdagan ng synthetic data ang mga corpus na nilikha ng tao
- Bawat iba pang cookbook — lahat ng mga ito ay nangangailangan ng corpus ng ebalwasyon

## Tingnan Din

- [Mga Dataset ng Ebalwasyon](/docs/leaderboard/datasets) — mga umiiral na corpora (EDTeKLA, FLORES+)
- [Soberanya ng Data](/docs/sovereignty/data-sovereignty) — pagmamay-ari at kontrol
- [Para sa mga Language Community](/docs/community/for-language-communities) — pakikipag-ugnayan sa komunidad
- [Suportahan ang isang Low-Resource Language](/docs/community/low-resource-languages) — ang kabuuang larawan