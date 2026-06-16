---
id: how-this-site-is-translated
title: "Wie diese Website übersetzt wird"
description: "Jede Sprachvariante dieser Website wird von Champollion selbst maschinell übersetzt – und zwar mit der Methode, die unseren eigenen öffentlichen Benchmark für das jeweilige Sprachpaar gewonnen hat."
---
# Wie diese Website übersetzt wird

Diese Website ist in 13 Sprachen verfügbar. Jede Sprachversion außer Englisch wird
**maschinell von Champollion übersetzt**, dem Übersetzungs-CLI, das parallel zu
dieser Arena entwickelt wurde — und das Übersetzungsmodell für jede Sprache wurde **durch
die eigenen Benchmarks dieser Website ausgewählt, nicht standardmäßig**: Jedes Sprachpaar wurde
anhand eines öffentlichen Entwicklungskorpus mit dem MT-Eval-Harness
evaluiert, und die Methode bzw. das Modell mit dem höchsten Composite Score (bei statistischem Gleichstand
nach Kosten entschieden) übersetzt diese Sprachversion.

Das bedeutet zweierlei, was Sie als Leser wissen sollten:

1. **Diese Seiten sind maschinelle Übersetzungen.** Sie werden mit den
   unten beschriebenen Vorgaben für Register und Terminologie erstellt, aber kein Mensch hat
   jeden Satz überprüft. Falls etwas falsch klingt, ist die englische Version
   maßgeblich — und wir freuen uns über eine Korrektur.
2. **Sie können die Auswahl nachvollziehen.** Jede Zeile unten nennt den Benchmark-Lauf,
   der das Modell für die jeweilige Sprache ausgewählt hat; die Läufe werden auf der
   [MT Eval Arena Bestenliste](https://mtevalarena.org/leaderboard) veröffentlicht.

## Herkunft nach Sprachversion

| Sprachversion | Sprache | Methode | Modell | Benchmark-Korpus | Composite Score (95% CI) | Benchmark-Datum | Zuletzt synchronisiert |
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

¹ Filipino wird anhand von Tagalog-Daten benchmarkt — Tatoebas nächstverfügbares
Korpus für die `fil`-Sprachversion.
² Das arabische Korpus ist modernes Hocharabisch (ISO 639-3 `arb`), passend
zum MSA-Register dieser Website.

Auswahlregel: Für jedes Paar wurde jedes Modell in der Benchmark-Aufstellung
(`google/gemini-3.5-flash`, `anthropic/claude-haiku-4.5`,
`anthropic/claude-fable-5`, `anthropic/claude-opus-4.8`,
`anthropic/claude-sonnet-4.6`, `openai/gpt-5.5`,
`google/gemini-3.1-pro-preview`) anhand des Entwicklungskorpus des Paares
bewertet. Gewinner ist der höchste Composite Score; wenn ein günstigeres Modell
statistisch nicht vom Spitzenreiter zu unterscheiden ist (paired Bootstrap-
Resampling, p ≥ 0.05), wird das günstigere Modell ausgewählt.

*Composite Score* ist die kombinierte Qualitätsmetrik der MT Eval Arena (chrF++,
exakte Übereinstimmung und geladene Metrik-Plugins, mit Bootstrap-Konfidenzintervall verifiziert). Die Werte sind
**innerhalb eines Sprachpaares** vergleichbar, nicht über Paare hinweg — ein Wert von 0.28 im Koreanischen
bedeutet nicht, dass koreanische Seiten schlechter sind als französische Seiten mit 0.58; die Korpora
und Schriftsysteme unterscheiden sich.

## Register und Ton

Jede Sprache wird mit einem expliziten Register übersetzt, das aus den
Sprachkarten von Champollion ausgewählt wird, sodass die Formalität auf der gesamten Website konsistent ist:

- **Français** — vouvoiement (formelles *vous*)
- **Deutsch** — Sie-Form
- **Nederlands** — u-vorm
- **Filipino** — formell, mit standardisierten Fachbegriffen
- **Español** — neutrales lateinamerikanisches Spanisch
- **简体中文** — professionelles technisches Register
- **日本語** — です/ます (höfliche Form)
- **한국어** — 해요체 (höflich)
- **Português** — professionelles Register
- **ไทย** — neutral-professionell
- **Tiếng Việt** — neutrale *bạn*-Form
- **العربية** — modernes Hocharabisch, professionelles Register

## Was nicht maschinell übersetzt wird

Code-Blöcke, CLI-Befehle, Konfigurationsschlüssel, Paketnamen, URLs und
Eigennamen werden während der Übersetzung geschützt und bleiben gewollt in Englisch.

## Eine Fehlübersetzung gefunden?

Eröffnen Sie ein Issue oder einen PR — die Quelle jeder übersetzten Seite ist das englische
Original. Korrekturen an einer übersetzten Seite bleiben bei künftigen Synchronisationen erhalten,
solange die englische Quelle dieser Seite unverändert ist (die Synchronisation übersetzt eine
Seite nur dann neu, wenn sich ihre englische Quelle ändert).

*Diese Seite ist selbst maschinell übersetzt durch die in der obigen Tabelle aufgeführte Methode —
sie beschreibt ihre eigene Übersetzung.*