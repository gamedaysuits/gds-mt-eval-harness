---
sidebar_position: 2
title: "Eval Harness v2.0"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "What the harness metrics feed into"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: Translate 30 Languages"
    to: https://champollion.dev/docs/tutorials/translate-30-languages
    kind: champollion
    note: "Use the harness to audit registers in production"
---
# Eval Harness v2.0

> **Résumé exécutif.** Cette page couvre l'installation, la configuration et l'utilisation du harnais d'évaluation de traduction automatique — l'outil qui évalue les méthodes de traduction par rapport à des corpus standardisés et produit des cartes de résultats notées. Pour les définitions canoniques des métriques, des schémas et du protocole d'évaluation, consultez la [Spécification de référence](/docs/specifications/benchmark).

Le harnais exécute des expériences de traduction et produit des cartes de résultats. Il gère la construction des invites, les appels API, la notation et la sérialisation des résultats — vous fournissez le corpus et le modèle.

## Installation

**Prérequis :** Python 3.10+

```bash
pip install sacrebleu aiohttp
```

Clonez le référentiel du harnais :

```bash
git clone https://github.com/gamedaysuits/arena.git
cd arena
```

## Utilisation

```bash
mt-eval run --corpus path/to/dataset.json
```

Cela exécute chaque entrée du corpus via le modèle configuré (ou le plugin de méthode), note les résultats et écrit un fichier JSON de carte de résultats dans le répertoire de sortie.

## Drapeaux CLI

### `mt-eval run`

| Drapeau | Obligatoire | Défaut | Description |
|--------|-------------|--------|-------------|
| `--corpus` | ✅ | — | Chemin du fichier corpus (`.json`, `.jsonl`, `.tsv`) |
| `--source-file` / `--reference-file` | — | — | Fichiers texte parallèles (FLORES+, format WMT) |
| `-m, --model` | — | `gemini-pro` | Slug du modèle (nom court ou ID OpenRouter complet). Résolu via `shared/model-aliases.json`. Séparé par des virgules pour les exécutions multi-modèles |
| `-d, --dataset` | — | `all` | Filtre de corpus : `all`, nom de segment ou plage d'ID |
| `--ids` | — | — | ID d'entrées séparés par des virgules à évaluer |
| `--source-lang` | — | `English` | Nom de la langue source |
| `--target-lang` | — | — | Nom de la langue cible |
| `-p, --prompt` | — | `naive` | Version de l'invite (`naive`, `custom`, `champollion`) |
| `--coaching-file` | — | — | Chemin du fichier texte d'invite de coaching |
| `--coaching` | — | — | Texte de coaching en ligne (chaîne entre guillemets) |
| `--method` | — | — | Chemin du répertoire du plugin de méthode (contient `method.json` + module Python) |
| `--method-card` | — | — | Chemin du JSON de carte de méthode pour les métadonnées du classement |
| `--fst-retries` | — | `0` | Nombre de tentatives de relance FST (méthode LLM par défaut uniquement) |
| `--skip-fst` | — | `false` | Ignorer complètement la porte de qualité FST |
| `--tools` | — | `false` | Activer le mode d'appel d'outils |
| `--tools-list` | — | — | Noms d'outils séparés par des virgules |
| `--max-tool-rounds` | — | `8` | Nombre maximal de tours d'appel d'outils par entrée |
| `--hooks` | — | — | Noms de hooks post-traduction |
| `--style-profile` | — | — | Chemin d'un profil de style JSON. Active les métriques de cohérence de style d'écriture (informatif — jamais partie du score composite ; voir [§ Métriques de style d'écriture et de registre](#métriques-de-style-décriture-et-de-registre-informatif)) |
| `-b, --batch-size` | — | `25` | Entrées par appel API |
| `-c, --concurrency` | — | `8` | Appels API parallèles |
| `--max-tokens` | — | `32768` | Jetons max par appel API |
| `--temperature` | — | `0.0` | Température d'échantillonnage (0.0 = déterministe) |
| `--no-cache` | — | `false` | Désactiver la mise en cache des réponses |
| `--cache-dir` | — | `eval/cache/harness` | Chemin du répertoire de cache |
| `-o, --output-dir` | — | `eval/logs/harness` | Répertoire de sortie pour les cartes de résultats et les journaux |
| `-n, --name` | — | — | Nom d'exécution lisible |
| `--dry-run` | — | `false` | Valider la configuration sans effectuer d'appels API |
| `--champollion-config` | — | — | Chemin vers `champollion.config.json` |
| `--champollion-cards-dir` | — | — | Répertoire des cartes de langue |
| `--target-lang-code` | — | — | Code de langue BCP-47 |

### Autres sous-commandes

| Sous-commande | Description |
|---------------|-------------|
| `mt-eval test <log_path>` | Analyser un journal d'exécution complété |
| `mt-eval publish <report_path>` | Soumettre une carte de résultats au classement |
| `mt-eval compare <logs...>` | Comparer plusieurs exécutions côte à côte |
| `mt-eval dashboard <logs...>` | Générer un tableau de bord HTML à partir des journaux d'exécution |
| `mt-eval list models\|prompts\|datasets` | Lister les ressources disponibles |
| `mt-eval export` | Empaqueter la configuration actuelle en tant que plugin de méthode champollion |
| `mt-eval export-config` | Exporter la MethodConfig résolue (les 8 champs canoniques) en JSON |

### Exemples

```bash
# Run with defaults (gemini-pro alias → google/gemini-3.1-pro-preview, naive prompt)
mt-eval run --corpus data/edtekla-dev-v1.json

# Coached experiment with coaching file
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model google/gemini-3.1-pro \
  --coaching-file prompts/crk-coaching-v8.txt \
  --temperature 0.0

# Run a custom method plugin with FST retries
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --method ./methods/fst-gated-pipeline \
  --fst-retries 3
```

---

## Schéma de carte de résultats

Chaque expérience produit une **carte de résultats** — un document JSON autonome. La structure de haut niveau :

```json
{
  "run_id": "uuid-v4",
  "harness_version": "2.0",
  "model_slug": "google/gemini-3.1-pro",
  "model_id": "gemini-3.1-pro-001",
  "condition": "baseline",
  "timestamp": "2026-06-01T03:22:41Z",
  "elapsed_seconds": 142.7,
  "dataset": { ... },
  "config": { ... },
  "method_card": { ... },
  "system_prompt_sha256": "abc123...",
  "system_prompt_used": "You are a translator...",
  "fingerprint": { ... },
  "scores": { ... },
  "totals": { ... },
  "environment": { ... },
  "results": [ ... ],
  "run_card_hash": "sha256-of-entire-card"
}
```

Consultez la [Spécification de carte de résultats](/docs/specifications/run-card) pour le schéma complet avec chaque champ documenté.

:::info Schéma faisant autorité
La [Spécification de référence](/docs/specifications/benchmark) est l'unique source de vérité pour le schéma de carte de résultats. Pour les définitions de métriques, les poids composites et les niveaux de qualité, consultez la [Spécification de notation](/docs/specifications/scoring). Cette page documente comment utiliser le harnais ; les spécifications définissent ce que signifient les résultats.
:::

### Blocs clés

**`dataset`** — Identifie le corpus utilisé, y compris son hash de contenu pour que les résultats soient liés à une version spécifique :

```json
// Example using master_corpus.json (62 gold + 342 textbook = 404)
{
  "id": "edtekla-dev-v1",
  "version": "1.0",
  "language_pair": "EN→CRK",
  "sha256": "...",
  "entry_count": 404
}
```

**`scores`** — Métriques agrégées pour l'exécution :

```json
// Counts reflect the dataset used (here: master_corpus.json, 404 entries)
{
  "total": 404,
  "exact_matches": 12,
  "exact_match_rate": 0.0968,
  "fst_accepted": 87,
  "fst_acceptance_rate": 0.7016,
  "chrf_plus_plus": 42.31,
  "errors": 0,
  "avg_latency_seconds": 1.15,
  "median_latency_seconds": 1.02,
  "p95_latency_seconds": 2.34,
  "by_difficulty": { ... },
  "by_provenance": { ... }
}
```

**`totals`** — Suivi de l'utilisation des jetons et des coûts :

```json
{
  "prompt_tokens": 48200,
  "completion_tokens": 3100,
  "reasoning_tokens": 0,
  "cached_tokens": 12000,
  "total_cost_usd": 0.42,
  "cost_per_entry_usd": 0.0034,
  "reasoning_ratio": 0.0
}
```

---

## Métriques de style d'écriture et de registre (informatif)

Le harnais peut évaluer si les traductions correspondent à un **registre** et un **style d'écriture** cibles, via le plugin de métrique `WritingStyleConsistency` (`mt_eval_harness/plugins/writing_style.py`). Une traduction peut être linguistiquement correcte mais dans le mauvais registre — formulation informelle dans un document juridique, texte passe-partout formel dans une copie marketing — et les métriques de chaîne ne le remarqueront pas. Ces métriques le font.

**Ce qui est mesuré (par entrée) :**

| Métrique | Échelle | Signification |
|----------|---------|-------------|
| `style_register_match` | booléen | La sortie correspond-elle au registre attendu ? La cible provient du champ `register` de l'entrée du corpus (voir [Spécification de référence §2.6](/docs/specifications/benchmark)) ou d'un profil de style |
| `style_sentence_length_ratio` | float | Longueur moyenne de phrase prédite vs référence (1.0 = correspondance ; divergence = dérive de style) |
| `style_formality_score` | 0.0–1.0 | Présence de marqueurs formels/informels (pronoms T–V, contractions, …) utilisant des ressources de marqueurs par langue |

**Agrégat :** `style_consistency_rate` — la fraction d'entrées sans décalage de registre détecté.

Activez une cible personnalisée avec `--style-profile path/to/profile.json` (par exemple un profil de voix de marque) ; sans cela, le plugin revient aux métadonnées `register` de chaque entrée du corpus le cas échéant.

:::caution Portée honnête
Ces métriques sont **informatif uniquement** — elles ne font jamais partie du score composite, et la détection de formalité est basée sur des marqueurs (une heuristique), pas un jugement appris. Traitez-les comme un détecteur de dérive pour l'adhérence au registre, pas un verdict sur la qualité du style.
:::

---

## Empreinte vs Hash de carte de résultats

Le harnais produit deux hashes distincts. Ils servent des objectifs différents :

### Empreinte

L'**empreinte** répond à : *« Cette exécution pourrait-elle être reproduite ? »*

Elle hache la combinaison d'entrées qui définissent la configuration de l'expérience — pas les résultats :

- SHA-256 du corpus
- Slug du modèle
- Étiquette de condition
- SHA-256 de l'invite système
- Température
- Version du harnais

Deux exécutions avec des empreintes identiques ont utilisé la même configuration. Leurs résultats doivent être comparables (modulo le non-déterminisme de l'API).

### Hash de carte de résultats

Le **hash de carte de résultats** répond à : *« Ce fichier de résultats spécifique a-t-il été altéré ? »*

C'est le SHA-256 de l'ensemble du JSON de carte de résultats (excluant le champ `run_card_hash` lui-même). Si un champ change — un score, un horodatage, une seule sortie — le hash se casse.

:::info Quand utiliser lequel
Utilisez l'**empreinte** pour regrouper les exécutions comparables (même expérience, exécutions différentes). Utilisez le **hash de carte de résultats** pour vérifier l'intégrité d'un fichier de résultats spécifique.
:::

---

## Publication au classement

Après avoir complété une exécution, utilisez `mt-eval publish` pour soumettre la carte de résultats :

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

Si aucun `--method-card` n'a été fourni lors de l'exécution, `mt-eval publish` lance un assistant interactif (`method_card_wizard.py`) qui vous guide dans la description de votre méthode (nom, classe, outils utilisés, etc.). La sortie de l'assistant est intégrée dans la carte de résultats avant la soumission.

### Soumission manuelle

Les cartes de résultats sont enregistrées en tant que fichiers JSON dans le répertoire de sortie. Vous pouvez également soumettre n'importe quel fichier de carte de résultats via l'interface utilisateur du classement à [/leaderboard](https://champollion.dev/leaderboard), ou via l'API :

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning Validation du classement
Le classement valide les cartes de résultats soumises par rapport au registre de corpus. Les soumissions référençant des corpus inconnus, ou avec un `run_card_hash` cassé, sont rejetées.
:::

:::danger NE PAS ENTRAÎNER sur les données d'évaluation
Si votre méthode a vu le corpus d'évaluation lors du développement — en tant que données d'entraînement, exemples few-shot, entrées de dictionnaire ou matériel d'ingénierie d'invite — votre soumission sera **disqualifiée**. Consultez [Évaluation de la traduction automatique](/docs/leaderboard/rules) pour savoir ce qui constitue une bonne vs mauvaise méthode.
:::

---

## Voir aussi

- [Évaluation de la traduction automatique](/docs/leaderboard/rules) — aperçu, proposition de valeur du classement et conseils sur les bonnes/mauvaises méthodes
- [Corpus d'évaluation](/docs/leaderboard/datasets) — format de corpus, EDTeKLA, FLORES+
- [Spécification de carte de résultats](/docs/specifications/run-card) — le schéma JSON complet
- [Construire une méthode](/docs/specifications/methods) — l'interface de méthode pour créer des méthodes évaluables
- [Classement des méthodes](https://champollion.dev/leaderboard) — scores de référence en direct
- [Spécification de référence](/docs/specifications/benchmark) — protocole d'évaluation, format de corpus, schéma de carte de résultats
- [Spécification de notation](/docs/specifications/scoring) — SSOT pour les métriques, les poids composites et les niveaux de qualité