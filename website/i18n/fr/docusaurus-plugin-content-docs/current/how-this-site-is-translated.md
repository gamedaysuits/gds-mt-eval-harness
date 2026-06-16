---
id: how-this-site-is-translated
title: "Comment ce site est traduit"
description: "Chaque locale sur ce site est traduite automatiquement par Champollion lui-même, en utilisant la méthode qui a remporté notre propre benchmark public pour cette paire de langues."
---
# Comment ce site est traduit

Ce site est disponible en 13 langues. Chaque locale à l'exception de l'anglais est
**traduite automatiquement par Champollion**, l'interface de ligne de commande de traduction construite aux côtés
de cette arène — et le modèle de traduction pour chaque langue a été choisi **par
les benchmarks de ce site lui-même, et non par défaut** : chaque paire linguistique a été
évaluée sur un corpus de développement public avec le harnais d'évaluation MT, et la
méthode/le modèle avec le score composite le plus élevé (les égalités statistiques étant tranchées par le coût) traduit cette locale.

Cela signifie deux choses que vous devez savoir en tant que lecteur :

1. **Ces pages sont des traductions automatiques.** Elles sont produites avec
   les conseils de registre et de terminologie décrits ci-dessous, mais aucun humain n'a examiné
   chaque phrase. Si quelque chose semble incorrect, la version anglaise fait
   autorité — et nous aimerions bien une correction.
2. **Vous pouvez vérifier le choix.** Chaque ligne ci-dessous nomme l'exécution du benchmark
   qui a sélectionné le modèle pour cette langue ; les exécutions sont publiées sur le
   [classement MT Eval Arena](https://mtevalarena.org/leaderboard).

## Provenance par locale

| Locale | Langue | Méthode | Modèle | Corpus de benchmark | Score composite (IC 95 %) | Date du benchmark | Dernière synchronisation |
|--------|--------|---------|--------|-------------------|--------------------------|-------------------|-------------------------|
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

¹ Le Filipino est évalué sur des données du Tagalog — le corpus Tatoeba le plus proche
disponible pour la locale `fil`.
² Le corpus arabe est l'arabe standard moderne (ISO 639-3 `arb`), correspondant
au registre MSA de ce site.

Règle de sélection : pour chaque paire, chaque modèle de la ligne de benchmark
(`google/gemini-3.5-flash`, `anthropic/claude-haiku-4.5`,
`anthropic/claude-fable-5`, `anthropic/claude-opus-4.8`,
`anthropic/claude-sonnet-4.6`, `openai/gpt-5.5`,
`google/gemini-3.1-pro-preview`) a été évalué sur le corpus de développement de la paire.
Le gagnant est le score composite le plus élevé ; lorsqu'un modèle moins coûteux est
statistiquement indistinguable du meilleur score (rééchantillonnage bootstrap appairé, p ≥ 0,05), le modèle moins coûteux est choisi.

*Score composite* est la métrique de qualité fusionnée de MT Eval Arena (chrF++,
correspondance exacte et plugins de métriques chargés, IC bootstrap vérifié). Les scores sont
comparables **au sein d'une paire linguistique**, non entre les paires — un 0,28 en coréen
ne signifie pas que les pages coréennes sont pires que les pages françaises à 0,58 ; les corpus
et les scripts diffèrent.

## Registre et ton

Chaque langue est traduite avec un registre explicite choisi parmi
les fiches linguistiques de Champollion, de sorte que la formalité est cohérente sur tout le site :

- **Français** — vouvoiement (formel *vous*)
- **Deutsch** — Sie-Form
- **Nederlands** — u-vorm
- **Filipino** — formel, avec des termes techniques standard
- **Español** — espagnol latino-américain neutre
- **简体中文** — registre technique professionnel
- **日本語** — です/ます (forme polie)
- **한국어** — 해요체 (poli)
- **Português** — registre professionnel
- **ไทย** — neutre professionnel
- **Tiếng Việt** — neutre *bạn*-form
- **العربية** — arabe standard moderne, registre professionnel

## Ce qui n'est pas traduit automatiquement

Les blocs de code, les commandes CLI, les clés de configuration, les noms de paquets, les URL et
les noms propres sont protégés pendant la traduction et restent en anglais par conception.

## Vous avez trouvé une erreur de traduction ?

Ouvrez un problème ou une demande de fusion — la source de chaque page traduite est l'original
anglais. Les corrections apportées à une page traduite sont conservées lors des synchronisations futures
tant que la source anglaise de cette page reste inchangée (la synchronisation ne retraduit une page que si sa source anglaise change).

*Cette page est elle-même traduite automatiquement par la méthode du tableau ci-dessus —
elle décrit sa propre traduction.*