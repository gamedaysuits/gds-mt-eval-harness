---
id: how-this-site-is-translated
title: How this site is translated
description: Every locale on this site is machine-translated by Champollion itself, using the method that won our own public benchmark for that language pair.
---

# How this site is translated

This site is available in 13 languages. Every locale except English is
**machine-translated by Champollion**, the translation CLI built alongside
this arena — and the translation model for each language was chosen **by
this site's own benchmarks, not by default**: each language pair was
evaluated on a public development corpus with the MT eval harness, and the
method/model with the highest composite score (statistical ties broken by
cost) translates that locale.

That means two things you should know as a reader:

1. **These pages are machine translations.** They are produced with the
   register and terminology guidance described below, but no human reviewed
   every sentence. If something reads wrong, the English version is
   authoritative — and we'd love a correction.
2. **You can audit the choice.** Every row below names the benchmark run
   that picked the model for that language; the runs are published to the
   [MT Eval Arena leaderboard](https://mtevalarena.org/leaderboard).

## Provenance by locale

| Locale | Language | Method | Model | Benchmark corpus | Composite score (95% CI) | Benchmark date | Last synced |
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

¹ Filipino is benchmarked on Tagalog data — Tatoeba's closest available
corpus for the `fil` locale.
² The Arabic corpus is Modern Standard Arabic (ISO 639-3 `arb`), matching
this site's MSA register.

Selection rule: for each pair, every model in the benchmark lineup
(`google/gemini-3.5-flash`, `anthropic/claude-haiku-4.5`,
`anthropic/claude-fable-5`, `anthropic/claude-opus-4.8`,
`anthropic/claude-sonnet-4.6`, `openai/gpt-5.5`,
`google/gemini-3.1-pro-preview`) was scored on the pair's development
corpus. The winner is the highest composite score; when a cheaper model is
statistically indistinguishable from the top scorer (paired bootstrap
resampling, p ≥ 0.05), the cheaper model is chosen.

*Composite score* is the MT Eval Arena's blended quality metric (chrF++,
exact match, and loaded metric plugins, bootstrap-CI verified). Scores are
comparable **within a language pair**, not across pairs — a 0.28 in Korean
does not mean Korean pages are worse than French pages at 0.58; the corpora
and scripts differ.

## Register and tone

Each language is translated with an explicit register chosen from
Champollion's language cards, so formality is consistent site-wide:

- **Français** — vouvoiement (formal *vous*)
- **Deutsch** — Sie-Form
- **Nederlands** — u-vorm
- **Filipino** — formal, with standard technical terms
- **Español** — neutral Latin American Spanish
- **简体中文** — professional technical register
- **日本語** — です/ます (polite form)
- **한국어** — 해요체 (polite)
- **Português** — professional register
- **ไทย** — neutral professional
- **Tiếng Việt** — neutral *bạn*-form
- **العربية** — Modern Standard Arabic, professional register

## What is not machine-translated

Code blocks, CLI commands, configuration keys, package names, URLs, and
proper nouns are protected during translation and remain in English by
design.

## Found a mistranslation?

Open an issue or PR — the source of every translated page is the English
original. Corrections to a translated page are preserved on future syncs as
long as the English source of that page is unchanged (sync re-translates a
page only when its English source changes).

*This page is itself machine-translated by the method in the table above —
it describes its own translation.*
