---
sidebar_position: 1
title: "Para sa mga Komunidad ng Wika"
---
# Para sa mga Komunidad ng Wika

> **Buod na Pangkalahatan.** Isang gabay para sa mga nagsasalita ng Indigenous at mga wikang may limitadong mapagkukunan na nagpapaliwanag kung paano mag-ambag sa Arena (mga reference translation, pagsusuri ng pagsasalin, coaching data) at kung ano ang matatanggap ng komunidad bilang kapalit (pagmamay-ari ng code, kita sa API, ganap na kontrol sa deployment). Hindi kinakailangan ang programming.

Hindi ninyo kailangang maging programmer upang mag-ambag sa Arena. Kung nagsasalita kayo ng Indigenous o wikang may limitadong mapagkukunan, kayo ang pinakamahalagang tao sa ecosystem na ito.

---

## Ang Kailangan Namin Mula sa Inyo

### Mga reference translation

Kailangan namin ng mga curated na pares ng pagsasalin para sa pagsusuri — English sa isang panig, at ang inyong wika sa kabilang panig. Ang mga ito ang nagiging "answer key" na pinagbabatayan ng score ng lahat ng pamamaraan ng pagsasalin.

Maaari ninyong likhain ang mga ito mula sa:
- **Mga materyales pang-edukasyon** — mga ehersisyo sa textbook, lesson plan, worksheet
- **Mga dokumento ng komunidad** — minutes ng pagpupulong, newsletter, anunsiyo
- **Mga pang-araw-araw na parirala** — UI strings, app labels, karaniwang ekspresyon
- **Nilalamang pangkultura** — mga kuwento, awit, o paglalarawan (na may naaangkop na pahintulot)

Ang format ay simpleng JSON:
```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

### Pagsusuri ng pagsasalin

Bawat pamamaraan na nagsasabing nakagagawa ito ng gumaganang mga pagsasalin ay nangangailangan ng human validation. Sinusuri ng mga bilingual na tagapagsalita ang mga output at sinasabi sa amin kung tama ang ginawa ng computer — at higit na mahalaga, *bakit* ito nagkamali.

### Coaching data

Mga tuntunin sa gramatika, entry sa diksyunaryo, morphological pattern — ito ang mga linguistic resource na nagpapagana sa mga pamamaraan ng pagsasalin. Ang inyong kaalaman kung paano gumagana ang inyong wika ay hindi mapapalitan ng anumang AI model.

---

## Ang Matatanggap Ninyo Bilang Kapalit

### Pagmamay-ari

Kapag nabuo ang isang pamamaraan ng pagsasalin para sa inyong wika at na-validate sa Arena, ang [pagmamay-ari ay inililipat](/docs/sovereignty/ownership-transfer) sa organisasyong pang-pamamahala ng inyong komunidad. Pagmamay-ari ninyo ang code, ang model weights, at ang deployment.

### Kita

Kapag ginagamit ng mga developer ang pamamaraan ng inyong wika sa pamamagitan ng champollion API, makatatanggap ang inyong komunidad ng [90% ng kita sa API](/docs/sovereignty/economic-model). Ang natitirang 10% ay sumasaklaw sa mga gastos sa imprastraktura.

### Kontrol

Kinokontrol ng inyong organisasyong pang-pamamahala ang:
- Kung sino ang maaaring maka-access sa pamamaraan
- Kung maaari ba itong gamitin nang komersiyal
- Kung anong mga tuntunin sa pagpepresyo ang ilalapat
- Kung kailan at paano ito ina-update
- Kung anong data ang ginagamit para sa karagdagang pag-develop

---

## Paano Makibahagi

1. **Makipag-ugnayan** — Magbukas ng issue sa [repository ng Arena](https://github.com/gamedaysuits/arena) o mag-email sa mga maintainer
2. **Ilarawan ang inyong wika** — Saang pamilya ito kabilang? Ilan ang nagsasalita? Anong mga writing system ang ginagamit? Anong computational resources ang mayroon (FSTs, dictionaries, corpora)?
3. **Magsimula sa maliit** — Kahit 50 curated na pares ng pagsasalin ay sapat upang makalikha ng evaluation dataset at makapagbukas ng bagong leaderboard track
4. **Ikonekta kami sa pamamahala** — Sino sa inyong komunidad ang may awtoridad sa language data at teknolohiya? Nangangailangan ang sovereignty model ng Arena ng governance partner

---

## Data Sovereignty

Sa inyo ang inyong language data. Itinayo ang Arena sa [mga prinsipyo ng OCAP®](/docs/sovereignty/data-sovereignty):

- Hindi namin kailanman kinokolekta o iniimbak ang inyong linguistic data sa aming mga server
- Ginagamit ng mga pamamaraan ng pagsasalin ang arkitekturang `api` — lahat ng coaching data, dictionaries, at grammar rules ay nananatili sa imprastrakturang kinokontrol ninyo
- Kayo ang nagpapasya kung sino ang maaaring mag-develop ng mga pamamaraan para sa inyong wika
- Pinatutunayan ng mga score sa leaderboard na gumagana ang isang pamamaraan; hindi nagbibigay ang mga ito ng pahintulot na i-deploy ito

---

## Tingnan Din

- [Data Sovereignty](/docs/sovereignty/data-sovereignty) — ang buong framework ng OCAP, CARE, at Te Mana Raraunga
- [Paglilipat ng Pagmamay-ari](/docs/sovereignty/ownership-transfer) — kung ano ang nangyayari kapag nanalo ang isang pamamaraan
- [Ang Economic Model](/docs/sovereignty/economic-model) — kung paano nagiging kita ang mga score
- [Suportahan ang isang Wikang May Limitadong Mapagkukunan](/docs/community/low-resource-languages) — teknikal na konteksto para sa mga researcher na nakikipagtulungan sa mga komunidad