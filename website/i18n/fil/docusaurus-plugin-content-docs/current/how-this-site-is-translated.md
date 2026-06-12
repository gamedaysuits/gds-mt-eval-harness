---
id: how-this-site-is-translated
title: "Paano isinasalin ang site na ito"
description: "Ang bawat locale sa site na ito ay isinasalin sa pamamagitan ng machine translation ng Champollion mismo, gamit ang pamamaraang nanalo sa aming sariling pampublikong benchmark para sa pares ng wikang iyon."
---
# Paano isinasalin ang site na ito

Available ang site na ito sa 13 wika. Bawat locale maliban sa English ay
**machine-translated by Champollion**, ang translation CLI na binuo kasabay
ng arena na ito — at ang translation model para sa bawat wika ay pinili **ng
sariling mga benchmark ng site na ito, hindi bilang default**: bawat pares ng wika ay
sinuri sa isang pampublikong development corpus gamit ang MT eval harness, at ang
method/model na may pinakamataas na composite score (ang mga statistical tie ay nilulutas ayon sa
gastos) ang nagsasalin ng locale na iyon.

Nangangahulugan iyon ng dalawang bagay na dapat ninyong malaman bilang mambabasa:

1. **Ang mga pahinang ito ay mga machine translation.** Ginagawa ang mga ito gamit ang
   patnubay sa register at terminolohiya na inilalarawan sa ibaba, ngunit walang taong nagsuri sa
   bawat pangungusap. Kung may mababasang mali, ang English na bersyon ang
   awtoritatibo — at ikalulugod namin ang isang pagwawasto.
2. **Maaari ninyong i-audit ang pagpili.** Bawat hilera sa ibaba ay pinapangalanan ang benchmark run
   na pumili sa model para sa wikang iyon; inilalathala ang mga run sa
   [leaderboard ng MT Eval Arena](https://mtevalarena.org/leaderboard).

## Provenance ayon sa locale

| Locale | Wika | Method | Model | Benchmark corpus | Composite score (95% CI) | Petsa ng benchmark | Huling na-sync |
|--------|----------|--------|-------|------------------|--------------------------|----------------|-------------|
| fr | Français | llm | `anthropic/claude-haiku-4.5` | `eng-fra-dev-v1` (Tatoeba, CC-BY-2.0) | 0.581 [0.542, 0.617] | 2026-06-11 | 2026-06-12 |
| de | Deutsch | llm | `anthropic/claude-opus-4.8` | `eng-deu-dev-v1` (Tatoeba, CC-BY-2.0) | 0.590 [0.550, 0.633] | 2026-06-11 | 2026-06-12 |
| nl | Nederlands | llm | `anthropic/claude-sonnet-4.6` | `eng-nld-dev-v1` (Tatoeba, CC-BY-2.0) | 0.600 [0.558, 0.642] | 2026-06-11 | 2026-06-12 |
| fil | Filipino | llm | `openai/gpt-5.5` | `eng-tgl-dev-v1` (Tatoeba, CC-BY-2.0)¹ | 0.499 [0.471, 0.529] | 2026-06-11 | 2026-06-12 |
| es | Español | llm | `anthropic/claude-haiku-4.5` | `eng-spa-dev-v1` (Tatoeba, CC-BY-2.0) | 0.553 [0.523, 0.584] | 2026-06-11 | 2026-06-12 |
| zh | 简体中文 | llm | `anthropic/claude-haiku-4.5` | `eng-cmn-dev-v1` (Tatoeba, CC-BY-2.0) | 0.240 [0.207, 0.278] | 2026-06-11 | 2026-06-12 |
| ja | 日本語 | llm | `anthropic/claude-sonnet-4.6` | `eng-jpn-dev-v1` (Tatoeba, CC-BY-2.0) | 0.278 [0.252, 0.304] | 2026-06-11 | 2026-06-12 |
| ko | 한국어 | llm | `anthropic/claude-opus-4.8` | `eng-kor-dev-v1` (Tatoeba, CC-BY-2.0) | 0.286 [0.256, 0.318] | 2026-06-11 | 2026-06-12 |
| pt | Português | llm | `anthropic/claude-haiku-4.5` | `eng-por-dev-v1` (Tatoeba, CC-BY-2.0) | 0.609 [0.576, 0.646] | 2026-06-11 | 2026-06-12 |
| th | ไทย | llm | `anthropic/claude-sonnet-4.6` | `eng-tha-dev-v1` (Tatoeba, CC-BY-2.0) | 0.468 [0.426, 0.510] | 2026-06-11 | 2026-06-12 |
| vi | Tiếng Việt | llm | `google/gemini-3.5-flash` | `eng-vie-dev-v1` (Tatoeba, CC-BY-2.0) | 0.463 [0.433, 0.494] | 2026-06-11 | 2026-06-12 |
| ar | العربية | llm | `anthropic/claude-fable-5` | `eng-arb-dev-v1` (Tatoeba, CC-BY-2.0)² | 0.437 [0.403, 0.478] | 2026-06-11 | 2026-06-12 |

¹ Ang Filipino ay ibinibenchmark sa datos na Tagalog — ang pinakamalapit na available na
corpus ng Tatoeba para sa `fil` locale.
² Ang Arabic corpus ay Modern Standard Arabic (ISO 639-3 `arb`), na tumutugma sa
MSA register ng site na ito.

Panuntunan sa pagpili: para sa bawat pares, bawat model sa benchmark lineup
(`google/gemini-3.5-flash`, `anthropic/claude-haiku-4.5`,
`anthropic/claude-fable-5`, `anthropic/claude-opus-4.8`,
`anthropic/claude-sonnet-4.6`, `openai/gpt-5.5`,
`google/gemini-3.1-pro-preview`) ay binigyan ng score sa development
corpus ng pares. Ang panalo ay ang may pinakamataas na composite score; kapag ang isang mas murang model ay
hindi mapag-iiba sa estadistika mula sa nangungunang scorer (paired bootstrap
resampling, p ≥ 0.05), ang mas murang model ang pinipili.

Ang *Composite score* ay ang pinaghalong metric ng kalidad ng MT Eval Arena (chrF++,
exact match, at loaded metric plugins, na beripikado ng bootstrap-CI). Ang mga score ay
maihahambing **sa loob ng isang pares ng wika**, hindi sa pagitan ng mga pares — ang 0.28 sa Korean
ay hindi nangangahulugang mas masama ang mga pahinang Korean kaysa sa mga pahinang French sa 0.58; magkaiba ang mga corpus
at script.

## Register at tono

Isinasalin ang bawat wika gamit ang isang tahasang register na pinili mula sa
mga language card ng Champollion, kaya konsistente ang pormalidad sa buong site:

- **Français** — vouvoiement (formal *vous*)
- **Deutsch** — Sie-Form
- **Nederlands** — u-vorm
- **Filipino** — pormal, gamit ang mga karaniwang teknikal na termino
- **Español** — neutral na Latin American Spanish
- **简体中文** — propesyonal na teknikal na register
- **日本語** — です/ます (polite form)
- **한국어** — 해요체 (polite)
- **Português** — propesyonal na register
- **ไทย** — neutral na propesyonal
- **Tiếng Việt** — neutral na *bạn*-form
- **العربية** — Modern Standard Arabic, propesyonal na register

## Ano ang hindi machine-translated

Ang mga code block, CLI command, configuration key, pangalan ng package, URL, at
proper noun ay pinoprotektahan habang nagsasalin at nananatili sa English ayon sa
disenyo.

## Nakakita ng maling salin?

Magbukas ng issue o PR — ang pinagmulan ng bawat isinaling pahina ay ang English
na orihinal. Ang mga pagwawasto sa isang isinaling pahina ay pinananatili sa mga susunod na sync hangga't
hindi nababago ang English source ng pahinang iyon (muling isinasalin ng sync ang isang
pahina lamang kapag nagbago ang English source nito).

*Ang pahinang ito mismo ay machine-translated ng method sa talahanayan sa itaas —
inilalarawan nito ang sarili nitong salin.*