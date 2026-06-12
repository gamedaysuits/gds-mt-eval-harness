---
sidebar_position: 11
title: "Guide pratique : Création de corpus"
---
# Guide de Création de Corpus

> **L'idée :** Avant de pouvoir évaluer une méthode de traduction, vous avez besoin d'un corpus d'évaluation. Ce guide couvre la construction d'un corpus à partir de zéro — sourçage des données, exigences de format, normes de qualité, licences et contribution à l'Arena.

:::info Ce n'est pas une méthode de traduction
Ce guide est un prérequis pour de nombreuses méthodes. Un bon corpus d'évaluation est la fondation qui rend tout le reste possible. Même 50 paires curées suffisent pour ouvrir une nouvelle piste de classement.
:::

## Quand Utiliser Ceci

- Vous souhaitez **ajouter une nouvelle paire de langues** au classement de l'Arena
- Vous êtes un **enseignant de langue** qui souhaite évaluer les traductions des étudiants
- Vous êtes un **travailleur communautaire en langue** ayant accès à des matériaux bilingues
- Vous êtes un **chercheur** qui a besoin d'un ensemble d'évaluation standardisé pour votre paire de langues

## Format du Corpus

Le harness accepte du JSON simple :

```json title="my-corpus.json"
{
  "metadata": {
    "name": "Quechua Dev v1",
    "version": "1.0.0",
    "source_language": "eng",
    "target_language": "que",
    "entry_count": 75,
    "license": "CC-BY-SA-4.0",
    "author": "Your Name / Organization",
    "description": "75 English-Quechua pairs from educational materials"
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello, how are you?",
      "reference": "Allillanchu, imaynallan kashanki?"
    },
    {
      "id": 2,
      "source": "The sun is shining today",
      "reference": "Kunan p'unchay inti k'anchashan"
    }
  ]
}
```

## Où Sourcer les Données

| Source | Qualité | Volume | Licence |
|--------|---------|--------|---------|
| **Manuels scolaires / matériels pédagogiques** | Élevée (examinée par des experts) | Faible à moyen | Vérifier auprès de l'éditeur |
| **Documents gouvernementaux** | Moyenne (registre formel) | Moyen à élevé | Souvent domaine public |
| **Dictionnaires bilingues** | Élevée (entrées vérifiées) | Moyen | Varie |
| **Aînés communautaires / locuteurs** | Très élevée (intuition native) | Faible (temps limité) | Gouvernée par la communauté |
| **Textes religieux** | Moyenne (spécifique au domaine) | Élevé | Généralement ouvert |
| **Corpus existants** (Hansard, FLORES) | Moyen à élevé | Élevé | Vérifier la licence |
| **Créé manuellement** | Très élevée | Faible | Vous en êtes propriétaire |

## Normes de Qualité

Un bon corpus d'évaluation possède :

1. **Un contenu diversifié** — pas seulement des salutations ou des phrases simples. Incluez des questions, des commandes, des phrases complexes, des termes spécifiques au domaine
2. **Des traductions vérifiées** — examinées par au moins un locuteur courant, idéalement deux
3. **Une orthographe cohérente** — un script, une convention d'orthographe unique tout au long
4. **Des sources indépendantes** — non dérivées du même texte sur lequel les méthodes s'entraîneront
5. **Une licence claire** — licence explicite permettant l'utilisation pour l'évaluation

:::danger Contamination du corpus
Le corpus d'évaluation doit être **indépendant** de toute donnée d'entraînement. Si une méthode a été entraînée ou sollicitée avec des données du corpus d'évaluation, elle sera disqualifiée. Concevez votre corpus pour être tenu à l'écart dès le départ.
:::

## Directives de Taille

| Taille | Ce qu'elle Permet |
|--------|------------------|
| **50 entrées** | Évaluation minimale viable — suffisant pour détecter les différences de qualité grossières |
| **100–200 entrées** | Classement fiable — suffisant pour la signification statistique entre les méthodes |
| **500+ entrées** | Qualité de recherche — scores composites robustes, intervalles de confiance |
| **1 000+ entrées** | Standard d'or — équivalent à la couverture devtest de FLORES |

Commencez petit. 50 entrées suffisent pour ouvrir une piste de classement. Vous pouvez l'étendre ultérieurement.

## Contribuer à l'Arena

1. **Créez votre corpus** au format JSON ci-dessus
2. **Licenciez-le** — CC BY-SA 4.0 est recommandé pour l'évaluation ouverte ; CC BY-NC-SA 4.0 pour l'utilisation restreinte
3. **Soumettez une PR** au [dépôt du harness d'évaluation](https://github.com/gamedaysuits/arena) avec votre corpus dans `data/`
4. **Le classement s'ouvre automatiquement** pour votre paire de langues une fois le corpus fusionné

## Pour les Communautés de Langues Autochtones

La création de corpus est un acte de **souveraineté linguistique**. Votre corpus, vos conditions :

- Vous décidez de la licence et des conditions d'accès
- Vous pouvez contribuer un **ensemble de développement public** (pour le développement de méthodes) tout en conservant un **ensemble de test secret** (pour l'évaluation officielle) sous contrôle communautaire
- Le [cadre de souveraineté](/docs/sovereignty/data-sovereignty) protège vos données à tous les niveaux

Même un petit corpus est un **atout stratégique** — c'est le benchmark qui décide ce que « suffisamment bon » signifie pour votre langue.

## S'Associe Bien Avec

- **[Traduction Partielle](./partial-translation)** — créer un corpus EST l'étape de traduction humaine
- **[Rétrotraduction](./back-translation)** — les données synthétiques complètent les corpus créés par l'homme
- Tous les autres guides — ils ont tous besoin d'un corpus d'évaluation

## Voir Aussi

- [Ensembles de Données d'Évaluation](/docs/leaderboard/datasets) — corpus existants (EDTeKLA, FLORES+)
- [Souveraineté des Données](/docs/sovereignty/data-sovereignty) — propriété et contrôle
- [Pour les Communautés Linguistiques](/docs/community/for-language-communities) — engagement communautaire
- [Soutenir une Langue Peu Dotée en Ressources](/docs/community/low-resource-languages) — la vue d'ensemble