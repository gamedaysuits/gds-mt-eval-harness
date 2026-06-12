---
sidebar_position: 4
title: "Contribution de ressources de calcul"
description: "Donnez vos tokens : exécutez des évaluations comparatives ouvertes à partir de la file d'attente publique avec votre propre clé API et publiez les résultats."
related:
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
  - label: "Cookbook: Coached LLM Prompting"
    to: /docs/tutorials/coached-llm-prompting
    kind: cookbook
  - label: "Cookbook: FST-Gated Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "Method Interface & Dependency Classes"
    to: /docs/specifications/methods
    kind: spec
  - label: "Leaderboard Rules & Trust Tiers"
    to: /docs/leaderboard/rules
    kind: guide
---
# Contribuer du calcul

> **L'idée :** le classement comporte des cases vides — des combinaisons (paire linguistique, modèle, condition) que personne n'a mesurées. Nous maintenons une file d'attente publique de ces éléments. Vous exécutez les éléments avec votre propre clé API, publiez les rapports, et la carte se remplit. « Donner des jetons » est une contribution réelle et citée à l'évaluation de la traduction automatique pour les langues peu dotées.

## La file d'attente

La file d'attente en direct est publiée à [champollion.dev/queue.json](https://champollion.dev/queue.json), et il existe un visualiseur de terminal sans installation :

```bash
curl -fsSL champollion.dev/queue | bash
```

Le visualiseur *affiche* uniquement les éléments ouverts et leurs commandes `mt-eval run` exactes — il n'exécute jamais rien ni ne dépense vos jetons. Chaque élément porte :

- `run_command` — prêt à copier-coller (récupère le corpus, exécute le harnais)
- `est_cost_usd` et `est_basis` — soit le coût **observé** de notre propre exécution de base de la même (corpus, modèle), soit une **extrapolation** à partir du coût moyen par entrée du balayage de ce modèle × le nombre d'entrées du corpus. La base est indiquée par élément ; votre coût réel dépend de la tarification du fournisseur au moment de l'exécution.
- `priority` — paires linguistiques non couvertes en premier, paires les moins dotées en premier (la taille du corpus est le proxy), naïf avant entraîné, modèle le moins cher en premier.

**Pas de verrouillage de réclamation — choisissez n'importe quel élément ouvert.** Deux personnes exécutant le même élément est inoffensif par conception : chaque carte d'exécution est empreinte (SHA-256 sur le hachage du jeu de données + modèle + condition + invite système, [Benchmark Spec §3.8](/docs/specifications/benchmark)), donc les exécutions identiques se dédupliquent à la publication, et les réplications indépendantes de la même configuration sont des preuves utiles, non du gaspillage.

Les corpus en file d'attente sont divisés en dev, CC-BY-family (dérivés de Tatoeba), et signalés `do_not_train` — ce sont des ensembles d'évaluation, pas des données d'entraînement. Les corpus sans licence commerciale et mis en quarantaine sont exclus de la file d'attente ouverte.

## Configuration (une fois)

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### Quelle clé de fournisseur ?

Le harnais achemine **tous** les appels de modèle via [OpenRouter](https://openrouter.ai/keys). Une `OPENROUTER_API_KEY` atteint chaque modèle de l'alignement de la file d'attente — modèles Anthropic Claude, OpenAI GPT et Google Gemini — et le suivi des coûts du harnais et les instantanés de tarification proviennent des mêmes métadonnées OpenRouter, donc le coût d'exécution signalé correspond à ce qui a été facturé à votre clé.

Si vos crédits se trouvent chez Anthropic, OpenAI ou Google directement : le harnais n'accepte **pas** actuellement les clés de fournisseur direct. Le schéma de la carte d'exécution réserve un champ `api_provider` pour le jour où il le fera, mais aujourd'hui chaque exécution du harnais est une exécution OpenRouter. Créer un compte OpenRouter et le financer (ou attacher votre propre compte fournisseur où OpenRouter le supporte) est le chemin pris en charge.

### Le chemin rapide de l'agent

Si vous travaillez avec Claude Code ou un autre agent de codage, la contribution entière est une invite :

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## Niveau 1 — Exécuter un benchmark

La `run_command` de chaque élément de la file d'attente est autonome. Un élément typique :

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

L'exécution affiche son coût total et écrit un journal d'exécution plus un rapport noté à `eval/logs/`. Puis publiez :

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

La publication vous connecte via OAuth (votre nom devient l'attribution du classement) et met à jour la carte d'exécution. Les soumissions communautaires arrivent au niveau de confiance **auto-évalué** — clairement étiqueté comme « soumis par la personne qui l'a exécuté ». Ce n'est pas une rétrogradation ; c'est le modèle de confiance qui fonctionne. La carte d'exécution porte tout ce qui est nécessaire pour que quiconque réexécute votre configuration exacte : hachage du jeu de données, modèle, condition, l'invite système complète et le coût. Les niveaux élevés (vérification, validation communautaire) sont accordés par examen — voir [Règles du classement](/docs/leaderboard/rules).

## Niveau 2 — Créer des invites entraînées

Le harnais a un support de première classe pour **l'entraînement** : remplacez l'invite système naïve par une qui porte une véritable connaissance linguistique. Passez `--coaching-file` (ou `--coaching "inline text"` pour les invites courtes) et le harnais utilise votre texte comme invite système, enregistre le **texte complet plus son SHA-256** dans le bloc de provenance du journal d'exécution, et étiquette la condition de l'exécution **`coached`** (sauf si vous définissez `--prompt` explicitement) — donc l'élaboration d'invites est une expérience reproductible et attribuable, deux fichiers d'entraînement différents ne peuvent jamais être confondus l'un avec l'autre, et les exécutions entraînées ne sont jamais confondues avec les bases naïves sur le classement.

Un exemple travaillé pour le féroïen, utilisant des faits de typologie et des entrées de glossaire de la [carte de langue publique](https://champollion.dev/languages) de la langue :

```text title="coaching-fao.txt"
You are translating Danish into Faroese (føroyskt).

Grammar notes:
- Faroese is a North Germanic V2 language: the finite verb is the second
  constituent of a main clause.
- Nouns inflect for case (nominative, accusative, dative, genitive),
  gender (masculine, feminine, neuter), and number. Make adjectives and
  determiners agree.
- The skerping pattern applies before -gv/-ggj sequences; preserve
  standard orthography including ð (which is silent).

Glossary (use these exact equivalents):
- language -> mál
- island -> oyggj
- weather -> veður

Style: plain register, modern standard orthography. Output only the
Faroese translation, no commentary.
```

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/dan-fao-dev-v1.json
mt-eval run --corpus dan-fao-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Faroese" \
  --coaching-file coaching-fao.txt
```

(Écrivez votre propre contenu d'entraînement — les faits ci-dessus illustrent la *forme* : quelques règles de grammaire à fort impact, un petit glossaire de termes que le modèle se trompe, une instruction de registre. Les cartes de langue à [champollion.dev/languages](https://champollion.dev/languages) citent les sources de typologie dont vous pouvez vous inspirer.)

Comparez avec la base naïve avec `mt-eval compare <naive_log> <coached_log>`, itérez et publiez votre meilleure exécution. L'exécution se publie avec la condition `coached` automatiquement ; si vous voulez que le classement affiche une méthode nommée au lieu de l'étiquette générique, joignez une carte de méthode lors de la publication (le flux de publication offre un assistant). Battre la base naïve sur une paire peu dotée avec rien d'autre que l'ingénierie d'invite est une découverte authentique et publiable — voir le [guide complet d'invite LLM entraînée](/docs/tutorials/coached-llm-prompting) pour des conseils de conception.

## Niveau 3 — Construire une méthode

La contribution la plus ambitieuse : implémenter le protocole `TranslationMethod` (`translate(entries, config)`) et évaluer un système réel, pas une invite. Le harnais l'exécute via `--method <plugin-dir>` et intègre votre carte de méthode dans la carte d'exécution. Modèles avec guides pratiques travaillés :

- **[Pipelines à porte FST](/docs/tutorials/fst-gated-pipeline)** — chaque mot candidat est vérifié par un analyseur morphologique ; le LLM régénère jusqu'à ce que la porte passe. Sortie semi-déterministe, morphologie garantie.
- **[Génération augmentée par dictionnaire](/docs/tutorials/dictionary-augmented-llm)** — recherchez les termes source dans un lexique bilingue au moment de la traduction et contraignez la sortie.
- [Modèles chaînés](/docs/tutorials/chained-models), [récupération peu de coups](/docs/tutorials/few-shot-prompting), [rétrotraduction](/docs/tutorials/back-translation), [hybrides basés sur des règles](/docs/tutorials/rule-based-hybrid)…

Les méthodes déclarent une **classe de dépendance** (S/O/A1/A2/X — voir [la spécification des méthodes](/docs/specifications/methods#method-validity-and-dependency-classes)) décrivant ce dont elles ont besoin pour s'exécuter et se transférer : un pipeline autonome est la classe S ; celui qui appelle une API de dictionnaire sous licence au moment de l'exécution est A2. Déclarez honnêtement — la classe détermine où votre méthode peut concourir, et les manifestes sont audités.

## Pourquoi cela importe au-delà du classement

Chaque exécution publiée est une preuve indépendante de la qualité de la traduction automatique pour une paire linguistique que les fournisseurs commerciaux ne mesurent pas. La file d'attente sert également de registre public de la *demande* : quelles paires la communauté considère comme dignes de mesure, quel coût de couverture aux prix actuels des API, et jusqu'où le calcul donné s'étend. Lorsque nous demandons aux agences de financement de financer des balayages systématiques, cette file d'attente et son taux de remplissage sont la preuve de la demande.