---
sidebar_position: 3
title: "Ensembles de données d'évaluation"
related:
  - label: "Corpus Design Framework"
    to: /docs/specifications/corpus-design
    kind: spec
    note: "How evaluation corpora are constructed"
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "Build a corpus for your language"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
---
# Ensembles de données d'évaluation

> **Résumé exécutif.** Cette page décrit les ensembles de données d'évaluation disponibles pour l'évaluation comparative, notamment le schéma d'entrée de corpus, les niveaux de difficulté (1–5) et les exigences de provenance. Actuellement disponibles : EDTeKLA Dev v1 (cri des Plaines, 548 entrées au total : 486 manuels + 62 standard de référence) et FLORES+ Devtest (39 langues, 1 012 entrées chacun).

Les ensembles de données sont les cibles fixes contre lesquelles le harnais s'exécute. Chaque ensemble de données est un fichier JSON contenant des paires source→cible avec des références standard de référence. Le harnais évalue les résultats du modèle par rapport à ces références — il ne les modifie jamais.

:::danger NE PAS ENTRAÎNER sur les données d'évaluation

⚠️ **Ces ensembles de données sont réservés à l'évaluation uniquement.** Les méthodes entraînées, affinées, sollicitées en contexte réduit, ou autrement exposées aux données d'évaluation produiront des scores artificiellement gonflés et seront **disqualifiées du classement.**

Utilisez des corpus distincts pour l'entraînement. Les ensembles d'évaluation doivent rester invisibles à votre modèle pendant le développement.
:::

---

## Format de l'ensemble de données

Chaque ensemble de données suit le même schéma JSON :

```json
{
  "dataset": {
    "id": "dataset-slug",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "description": "Human-readable description of the dataset",
    "source_language": "en",
    "target_language": "crk",
    "created": "2025-05-01",
    "license": "CC-BY-NC-4.0",
    "provenance": ["gold_standard", "textbook"]
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "tânisi",
      "difficulty": 1,
      "provenance": "gold_standard",
      "register": "conversational",
      "context": "greeting",
      "notes": "Common greeting, SRO orthography"
    }
  ]
}
```

:::info Schéma canonique
La [Spécification de référence](/docs/specifications/benchmark) définit le corpus canonique et le schéma d'entrée. Cette page documente les ensembles de données disponibles et comment en créer de nouveaux.
:::

### Bloc `dataset` de niveau supérieur

| Champ | Type | Description |
|-------|------|-------------|
| `id` | `string` | Identifiant unique de l'ensemble de données (utilisé dans les cartes d'exécution et le classement) |
| `version` | `string` | Version sémantique. L'incrémentation invalide les comparaisons de cartes d'exécution antérieures |
| `language_pair` | `string` | Étiquette d'affichage (par exemple, `EN→CRK`) |
| `description` | `string` | Optionnel. Résumé lisible par l'homme |
| `source_language` | `string` | Code de langue source BCP 47 |
| `target_language` | `string` | Code de langue cible BCP 47 |
| `created` | `string` | Date de création ISO 8601 |
| `license` | `string` | Identifiant de licence SPDX |
| `provenance` | `string[]` | Liste des étiquettes de provenance utilisées dans les entrées |

### Champs d'entrée

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `id` | `integer` | ✅ | Identifiant unique de l'entrée dans le corpus |
| `source` | `string` | ✅ | Le texte source à traduire |
| `reference` | `string` | ✅ | La traduction de référence standard de référence |
| `difficulty` | `integer` | ✅ | Niveau de difficulté 1–5 (voir ci-dessous) |
| `provenance` | `string` | ✅ | Origine de cette entrée (par exemple, `gold_standard`, `textbook`, `elicited`) |
| `register` | `string` | ✅ | Niveau de registre/formalité (par exemple, `conversational`, `formal`, `ceremonial`) |
| `context` | `string` | ✅ | Fonction communicative (par exemple, `greeting`, `declaration`, `instruction`) |
| `notes` | `string` | ❌ | Contexte optionnel pour les examinateurs humains |
| `morphological_analysis` | `string` | ❌ | Décomposition morphologique standard de référence |
| `variant_class` | `string` | ❌ | Étiquette de classe regroupant les variantes de traduction acceptables |

---

## Ensembles de données disponibles

### Ensemble de développement EDTeKLA v1

Le premier ensemble de données d'évaluation, construit pour la traduction anglais→cri des Plaines (SRO). Créé par le [groupe de recherche EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) de l'Université de l'Alberta.

| Propriété | Valeur |
|-----------|--------|
| **ID** | `edtekla-dev-v1` |
| **Version** | `1.0` |
| **Paire de langues** | EN → CRK (cri des Plaines, orthographe SRO) |
| **Nombre d'entrées** | 548 au total (486 manuels + 62 standard de référence). Le corpus de développement canonique est `textbook_dev.json` (436 entrées — la division de développement complète du manuel sur 486 au total : 436 développement + 50 test retenus) |
| **Distribution de difficulté** | Facile, Moyen, Difficile |
| **Provenance** | `gold_standard` (vérifié par des locuteurs), `textbook` (matériels pédagogiques publiés) |
| **Licence** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |

**Ce qu'il teste :**

- Salutations de base et expressions courantes
- Animacité nominale et obviation
- Conjugaison verbale selon les personnes et les temps
- Constructions locatives
- Paradigmes possessifs
- Structures de phrases complexes

:::tip Structure du corpus
La collection complète d'EDTeKLA compte 548 entrées curées : 486 du corpus de manuel (436 développement + 50 retenus) et 62 du standard de référence itwêwina. Le corpus de développement canonique est `textbook_dev.json` avec 436 entrées — la division de développement complète du manuel. Chaque entrée a été vérifiée par des locuteurs courants ou provient de manuels de langue crie publiés. Un ensemble de données plus petit et de haute qualité avec des standards de référence vérifiés est plus utile qu'un ensemble volumineux et bruyant — en particulier pour une langue peu dotée en ressources où les traductions « suffisamment bonnes » sont souvent morphologiquement invalides.
:::

---

## Création d'un nouvel ensemble de données

Pour créer un ensemble de données pour une nouvelle paire de langues ou un nouveau domaine :

### 1. Structurer le JSON

Suivez le schéma [Format de l'ensemble de données](#format-de-lensemble-de-données). Chaque entrée doit avoir `source`, `reference`, `difficulty`, `provenance`, `register` et `context`.

### 2. Attribuer un ID unique

Utilisez un slug descriptif : `{project}-{split}-v{version}` (par exemple, `edtekla-dev-v1`, `quechua-test-v1`).

### 3. Vérifier les standards de référence

Chaque valeur `reference` doit être vérifiée par un locuteur courant ou provenir d'une ressource publiée et examinée par les pairs. Les références générées par machine contredisent l'objectif de l'évaluation.

### 4. Définir les niveaux de difficulté

Attribuez à chaque entrée un niveau de difficulté entier :

| Niveau | Description | Exemples |
|--------|-------------|----------|
| 1 — Vocabulaire de base | Mots simples, salutations courantes, nombres | « hello » → « tânisi » |
| 2 — Phrases simples | Sujet-verbe ou SVO, temps présent | « I see the dog » |
| 3 — Complexité modérée | Temps passé/futur, possessifs, animacité | « I saw his dog yesterday » |
| 4 — Morphologie complexe | Obviation, voix passive, ordre conjoint | « the woman whose son went to the store » |
| 5 — Avancé | Multi-clause, registre formel, cérémoniel, idiomatique | Paragraphe complet avec ton approprié au registre |

### 5. Étiqueter la provenance

Chaque entrée doit indiquer sa provenance. Étiquettes courantes :

- `gold_standard` — Vérifié par des locuteurs courants
- `textbook` — Provenant de matériels pédagogiques publiés
- `elicited` — Produit par des séances d'élicitation structurées
- `corpus` — Extrait d'un corpus parallèle

### 6. Valider le fichier

Exécutez le harnais contre votre ensemble de données avec n'importe quel modèle pour vérifier que le JSON est bien formé et que tous les champs requis sont présents :

```bash
python eval/baseline_experiment.py --dataset path/to/your-dataset.json
```

Le harnais génèrera une erreur en cas de champs manquants, d'indices en double ou de violations de schéma.

### 7. Soumettre pour inclusion

Ouvrez une demande de tirage contre le [référentiel du harnais d'évaluation](https://github.com/gamedaysuits/arena) avec votre fichier d'ensemble de données dans le répertoire `data/`. Incluez la documentation de votre méthodologie de vérification et de vos sources de provenance.

---

## FLORES+ Devtest

Un repère multilingue à large couverture maintenu par l'[Initiative de données de langue ouverte (OLDI)](https://huggingface.co/datasets/openlanguagedata/flores_plus). Utilisé pour l'évaluation comparative multi-modèles de champollion.

| Propriété | Valeur |
|-----------|--------|
| **ID** | `flores-plus-devtest` |
| **Paires de langues** | EN → 39 langues (toutes les langues naturelles enregistrées par champollion) |
| **Nombre d'entrées** | 1 012 phrases par langue |
| **Licence** | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| **Source** | Originellement Meta FLORES-200, maintenant maintenu par OLDI |
| **Localisation** | Fixtures pré-extraites à `test/benchmark/fixtures/` dans le référentiel champollion principal |

:::danger Évaluation uniquement
FLORES+ est destiné uniquement à l'évaluation. Les curateurs demandent explicitement qu'il **ne soit pas utilisé comme données d'entraînement**. Assurez-vous que son contenu est exclu de tout corpus d'entraînement.
:::

---

## Voir aussi

- [Évaluation de la traduction automatique](/docs/leaderboard/rules) — aperçu du cadre d'évaluation et du classement
- [Harnais d'évaluation](/docs/specifications/harness) — comment exécuter les évaluations contre ces ensembles de données
- [Spécification de la carte d'exécution](/docs/specifications/run-card) — le schéma JSON pour enregistrer les résultats
- [Classement des méthodes](https://champollion.dev/leaderboard) — scores d'évaluation comparative en direct
- [Projet EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) — le groupe de recherche de l'Université de l'Alberta derrière l'ensemble de données cri