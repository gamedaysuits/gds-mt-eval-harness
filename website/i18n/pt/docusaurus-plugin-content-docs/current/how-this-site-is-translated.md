---
id: how-this-site-is-translated
title: "Como este site é traduzido"
description: "Cada idioma neste site é traduzido por máquina pelo Champollion, usando o método que venceu nosso próprio benchmark público para esse par de idiomas."
---
# Como este site é traduzido

Este site está disponível em 13 idiomas. Todos os locales, exceto inglês,
são **traduzidos por máquina pelo Champollion**, a CLI de tradução construída
junto com esta arena — e o modelo de tradução para cada idioma foi escolhido
**pelos próprios benchmarks deste site, não por padrão**: cada par de idiomas
foi avaliado em um corpus de desenvolvimento público com o harness de avaliação
de MT, e o método/modelo com a pontuação composta mais alta (empates estatísticos
desempatados pelo custo) traduz esse locale.

Isso significa duas coisas que você deve saber como leitor:

1. **Estas páginas são traduções por máquina.** Elas são produzidas com a
   orientação de registro e terminologia descrita abaixo, mas nenhum humano
   revisou cada sentença. Se algo parecer errado, a versão em inglês é
   autoritária — e adoraríamos uma correção.
2. **Você pode auditar a escolha.** Cada linha abaixo nomeia a execução de
   benchmark que escolheu o modelo para esse idioma; as execuções são publicadas
   no [leaderboard da MT Eval Arena](https://mtevalarena.org/leaderboard).

## Proveniência por locale

| Locale | Idioma | Método | Modelo | Corpus de benchmark | Pontuação composta (IC 95%) | Data do benchmark | Última sincronização |
|--------|--------|--------|--------|---------------------|--------------------------|-------------------|----------------------|
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

¹ Filipino é avaliado em dados de Tagalog — o corpus mais próximo disponível
do Tatoeba para o locale `fil`.
² O corpus árabe é Árabe Padrão Moderno (ISO 639-3 `arb`), correspondendo
ao registro MSA deste site.

Regra de seleção: para cada par, todos os modelos no lineup de benchmark
(`google/gemini-3.5-flash`, `anthropic/claude-haiku-4.5`,
`anthropic/claude-fable-5`, `anthropic/claude-opus-4.8`,
`anthropic/claude-sonnet-4.6`, `openai/gpt-5.5`,
`google/gemini-3.1-pro-preview`) foram pontuados no corpus de desenvolvimento do par.
O vencedor é a pontuação composta mais alta; quando um modelo mais barato é
estatisticamente indistinguível do melhor pontuador (reamostragem bootstrap
pareada, p ≥ 0.05), o modelo mais barato é escolhido.

*Pontuação composta* é a métrica de qualidade combinada da MT Eval Arena
(chrF++, correspondência exata e plugins de métricas carregadas, IC bootstrap
verificado). As pontuações são comparáveis **dentro de um par de idiomas**,
não entre pares — uma pontuação de 0.28 em coreano não significa que as páginas
em coreano são piores do que as páginas em francês com 0.58; os corpora e
scripts diferem.

## Registro e tom

Cada idioma é traduzido com um registro explícito escolhido dos cartões de
idioma do Champollion, para que a formalidade seja consistente em todo o site:

- **Français** — vouvoiement (formal *vous*)
- **Deutsch** — Sie-Form
- **Nederlands** — u-vorm
- **Filipino** — formal, com termos técnicos padrão
- **Español** — espanhol latino-americano neutro
- **简体中文** — registro técnico profissional
- **日本語** — です/ます (forma polida)
- **한국어** — 해요체 (polida)
- **Português** — registro profissional
- **ไทย** — neutro profissional
- **Tiếng Việt** — neutro forma *bạn*
- **العربية** — Árabe Padrão Moderno, registro profissional

## O que não é traduzido por máquina

Blocos de código, comandos CLI, chaves de configuração, nomes de pacotes,
URLs e nomes próprios são protegidos durante a tradução e permanecem em
inglês por design.

## Encontrou uma tradução incorreta?

Abra uma issue ou PR — a fonte de cada página traduzida é o original em inglês.
As correções em uma página traduzida são preservadas em sincronizações futuras,
desde que a fonte em inglês dessa página não seja alterada (a sincronização
retraduz uma página apenas quando sua fonte em inglês muda).

*Esta página é ela mesma traduzida por máquina pelo método na tabela acima —
ela descreve sua própria tradução.*