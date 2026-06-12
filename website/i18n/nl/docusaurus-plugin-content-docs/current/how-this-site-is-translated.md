---
id: how-this-site-is-translated
title: "Hoe deze site wordt vertaald"
description: "Elke taalversie op deze site is machinaal vertaald door Champollion zelf, met behulp van de methode die ons eigen publieke benchmark voor dat taalpaar heeft gewonnen."
---
# Hoe deze site wordt vertaald

Deze site is beschikbaar in 13 talen. Elke taalversie, met uitzondering van het Engels, is
**machinaal vertaald door Champollion**, de vertaal-CLI die samen met
deze arena is ontwikkeld — en het vertaalmodel voor elke taal werd gekozen **door
de eigen benchmarks van deze site, niet als standaardinstelling**: elk taalpaar werd
geëvalueerd op een openbaar ontwikkelcorpus met de MT eval harness, en de
methode/het model met de hoogste composite score (statistische gelijkspellen worden beslist op basis van
kosten) vertaalt die taalversie.

Dat betekent twee dingen die u als lezer moet weten:

1. **Deze pagina's zijn machinevertalingen.** Ze zijn geproduceerd met de
   register- en terminologierichtlijnen die hieronder worden beschreven, maar geen enkele mens heeft
   elke zin beoordeeld. Als iets onjuist leest, is de Engelstalige versie
   gezaghebbend — en we stellen een correctie zeer op prijs.
2. **U kunt de keuze controleren.** Elke rij hieronder vermeldt de benchmarkrun
   die het model voor die taal heeft geselecteerd; de runs worden gepubliceerd op het
   [MT Eval Arena-leaderboard](https://mtevalarena.org/leaderboard).

## Herkomst per taalversie

| Taalversie | Taal | Methode | Model | Benchmarkcorpus | Composite score (95% BI) | Benchmarkdatum | Laatste synchronisatie |
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

¹ Filipino wordt gebenchmarkt op Tagalog-gegevens — het dichtstbijzijnde beschikbare
corpus van Tatoeba voor de `fil`-taalversie.
² Het Arabische corpus is Modern Standaard Arabisch (ISO 639-3 `arb`), passend bij
het MSA-register van deze site.

Selectieregel: voor elk taalpaar werd elk model in de benchmark-lineup
(`google/gemini-3.5-flash`, `anthropic/claude-haiku-4.5`,
`anthropic/claude-fable-5`, `anthropic/claude-opus-4.8`,
`anthropic/claude-sonnet-4.6`, `openai/gpt-5.5`,
`google/gemini-3.1-pro-preview`) gescoord op het ontwikkelcorpus van het betreffende taalpaar. De winnaar is de hoogste composite score; wanneer een goedkoper model
statistisch niet te onderscheiden is van de hoogste scorer (paarsgewijze bootstrap-
resampling, p ≥ 0.05), wordt het goedkopere model gekozen.

*Composite score* is de gemengde kwaliteitsmetriek van de MT Eval Arena (chrF++,
exacte overeenkomst en geladen metriek-plugins, bootstrap-CI geverifieerd). Scores zijn
vergelijkbaar **binnen een taalpaar**, niet tussen taalparen — een 0,28 in het Koreaans
betekent niet dat Koreaanse pagina's slechter zijn dan Franse pagina's met 0,58; de corpora
en scripts verschillen.

## Register en toon

Elke taal wordt vertaald met een expliciet register dat is gekozen uit
de taalkaarten van Champollion, zodat de formaliteit consistent is over de gehele site:

- **Français** — vouvoiement (formeel *vous*)
- **Deutsch** — Sie-Form
- **Nederlands** — u-vorm
- **Filipino** — formeel, met standaard technische termen
- **Español** — neutraal Latijns-Amerikaans Spaans
- **简体中文** — professioneel technisch register
- **日本語** — です/ます (beleefde vorm)
- **한국어** — 해요체 (beleefd)
- **Português** — professioneel register
- **ไทย** — neutraal professioneel
- **Tiếng Việt** — neutrale *bạn*-vorm
- **العربية** — Modern Standaard Arabisch, professioneel register

## Wat niet machinaal wordt vertaald

Codeblokken, CLI-opdrachten, configuratiesleutels, pakketnamen, URL's en
eigennamen worden tijdens de vertaling beschermd en blijven by design in het Engels.

## Een onjuiste vertaling gevonden?

Open een issue of PR — de bron van elke vertaalde pagina is het Engelstalige
origineel. Correcties op een vertaalde pagina blijven behouden bij toekomstige synchronisaties, zolang
de Engelstalige bron van die pagina ongewijzigd is (synchronisatie vertaalt een
pagina opnieuw alleen wanneer de Engelstalige bron ervan wijzigt).

*Deze pagina is zelf machinaal vertaald door de methode in de bovenstaande tabel —
zij beschrijft haar eigen vertaling.*