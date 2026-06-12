---
id: how-this-site-is-translated
title: "Cómo se traduce este sitio"
description: "Cada idioma en este sitio se traduce automáticamente mediante Champollion, utilizando el método que ganó nuestro propio benchmark público para ese par de idiomas."
---
# Cómo se traduce este sitio

Este sitio está disponible en 13 idiomas. Cada configuración regional excepto
inglés es **traducida automáticamente por Champollion**, la herramienta CLI
de traducción construida junto con esta arena — y el modelo de traducción
para cada idioma fue elegido **por los propios puntos de referencia de este
sitio, no por defecto**: cada par de idiomas fue evaluado en un corpus de
desarrollo público con el arnés de evaluación MT, y el método/modelo con la
puntuación compuesta más alta (empates estadísticos resueltos por costo)
traduce esa configuración regional.

Esto significa dos cosas que debe saber como lector:

1. **Estas páginas son traducciones automáticas.** Se producen con la
   orientación de registro y terminología descrita a continuación, pero
   ninguna persona revisó cada oración. Si algo se lee incorrectamente, la
   versión en inglés es la autorizada — y nos encantaría una corrección.
2. **Puede auditar la elección.** Cada fila a continuación nombra la ejecución
   de punto de referencia que eligió el modelo para ese idioma; las ejecuciones
   se publican en el [tablero de clasificación de MT Eval Arena](https://mtevalarena.org/leaderboard).

## Procedencia por configuración regional

| Configuración regional | Idioma | Método | Modelo | Corpus de punto de referencia | Puntuación compuesta (IC 95%) | Fecha del punto de referencia | Última sincronización |
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

¹ Filipino se evalúa en datos de tagalo — el corpus más cercano disponible de
Tatoeba para la configuración regional `fil`.
² El corpus de árabe es árabe estándar moderno (ISO 639-3 `arb`), que
coincide con el registro MSA de este sitio.

Regla de selección: para cada par, cada modelo en la alineación de puntos de
referencia (`google/gemini-3.5-flash`, `anthropic/claude-haiku-4.5`,
`anthropic/claude-fable-5`, `anthropic/claude-opus-4.8`,
`anthropic/claude-sonnet-4.6`, `openai/gpt-5.5`,
`google/gemini-3.1-pro-preview`) fue puntuado en el corpus de desarrollo del par. El ganador
es la puntuación compuesta más alta; cuando un modelo más económico es
estadísticamente indistinguible del mejor puntuador (remuestreo bootstrap
pareado, p ≥ 0.05), se elige el modelo más económico.

*Puntuación compuesta* es la métrica de calidad combinada de MT Eval Arena
(chrF++, coincidencia exacta y complementos de métricas cargadas, IC bootstrap
verificado). Las puntuaciones son comparables **dentro de un par de idiomas**,
no entre pares — una puntuación de 0.28 en coreano no significa que las páginas
en coreano sean peores que las páginas en francés con 0.58; los corpus y
escrituras difieren.

## Registro y tono

Cada idioma se traduce con un registro explícito elegido de las tarjetas de
idioma de Champollion, por lo que la formalidad es consistente en todo el sitio:

- **Français** — vouvoiement (formal *vous*)
- **Deutsch** — Sie-Form
- **Nederlands** — u-vorm
- **Filipino** — formal, con términos técnicos estándar
- **Español** — español latinoamericano neutral
- **简体中文** — registro técnico profesional
- **日本語** — です/ます (forma cortés)
- **한국어** — 해요체 (cortés)
- **Português** — registro profesional
- **ไทย** — neutral profesional
- **Tiếng Việt** — neutral forma *bạn*
- **العربية** — árabe estándar moderno, registro profesional

## Lo que no se traduce automáticamente

Los bloques de código, comandos CLI, claves de configuración, nombres de
paquetes, URLs y nombres propios están protegidos durante la traducción y
permanecen en inglés por diseño.

## ¿Encontró una traducción incorrecta?

Abra un problema o solicitud de extracción — la fuente de cada página traducida
es el original en inglés. Las correcciones a una página traducida se conservan
en futuras sincronizaciones siempre que la fuente en inglés de esa página no
cambie (la sincronización retraduce una página solo cuando su fuente en inglés
cambia).

*Esta página se traduce automáticamente por el método en la tabla anterior —
describe su propia traducción.*