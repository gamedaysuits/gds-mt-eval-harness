---
sidebar_position: 2
title: "Transfert de propriété"
---
# Transfert de propriété

> **Résumé exécutif.** Lorsqu'une méthode de traduction atteint le niveau Deployable (score composite ≥ 0,70) et réussit l'examen communautaire, la propriété du code est transférée du chercheur à l'organisation de gouvernance autochtone. Cette page documente le pipeline de transfert en cinq étapes, l'alignement OCAP®, et les conseils pour les chercheurs développant des méthodes pour les langues autochtones.

Lorsqu'une méthode de traduction remporte le classement de l'Arena, qu'advient-il du code ? Pour les langues autochtones et peu dotées en ressources, la réponse n'est pas « le chercheur le conserve ». La réponse est : **la communauté en est propriétaire.**

---

## Fonctionnement

L'Arena applique un pipeline clair allant de la recherche à la propriété communautaire :

### 1. Développement de la méthode
Un chercheur, un étudiant ou un développeur construit une méthode de traduction — un pipeline avec FST-gated, un LLM entraîné, un modèle affiné, ou toute autre approche. Il la développe en utilisant ses propres ressources.

### 2. Évaluation Arena
La méthode est évaluée par le biais du [harnais d'évaluation](/docs/specifications/harness). Chaque soumission est associée à un commit Git spécifique et à une version de dataset. Les scores sont reproductibles.

### 3. Examen communautaire
Pour les méthodes de langues autochtones, les résultats sont examinés par les travailleurs linguistiques communautaires et les organisations de gouvernance. Un score élevé au classement prouve que la méthode *fonctionne* ; cela ne prouve pas qu'elle est *appropriée*.

### 4. Transfert de code
Lorsqu'une méthode atteint le niveau **Deployable** (score composite ≥ 0,70 par rapport à l'évaluation de référence) **et** réussit l'examen communautaire (validation humaine) :
- Le chercheur remet le code source
- La propriété légale est transférée à l'organisation de gouvernance autochtone (par exemple, un conseil tribal, une autorité linguistique, ou une organisation Métis)
- L'organisation de gouvernance détient les clés de chiffrement pour les datasets d'évaluation
- La méthode devient un actif contrôlé par la communauté

Consultez la [Spécification de notation](/docs/specifications/scoring), §5 pour les définitions des niveaux de qualité et la [Spécification de référence](/docs/specifications/benchmark), §8.3 pour les conditions complètes de transfert et §7 pour la porte de validation humaine.

### 5. Déploiement en production
La méthode est exportée en tant que plugin [champollion](https://champollion.dev) et déployée vers l'API de production. La communauté contrôle :
- Qui peut accéder à la méthode
- Quels termes de tarification s'appliquent
- Si la méthode peut être utilisée commercialement
- Quand et comment la méthode est mise à jour

---

## Pourquoi c'est important

La recherche en ML traditionnelle suit un modèle extractif :
1. Le chercheur collecte des données auprès d'une communauté
2. Le chercheur entraîne un modèle
3. Le chercheur publie un article
4. La communauté ne reçoit rien

Ce modèle fonctionne désormais à l'échelle industrielle. OMT-1600 de Meta (mars 2026) a entraîné des modèles de traduction pour 1 600 langues — y compris des langues autochtones comme le cri des Plaines — en utilisant des données extraites du web et des traductions bibliques. Les modèles ont été entraînés sans protocoles de consentement communautaire, les poids ne sont actuellement pas disponibles en téléchargement, et les communautés dont les langues ont été modélisées n'ont aucune part de propriété, aucun rôle de gouvernance, et aucun revenu. L'article est le produit. La communauté est la source de données.

L'Arena inverse cela :
1. Le chercheur construit une méthode
2. L'Arena la valide par rapport à des corpus curés par la communauté avec des métriques morphologiques
3. La communauté reçoit la propriété du code fonctionnel
4. La communauté gagne des revenus de l'utilisation de l'API

**C'est la différence fondamentale entre Champollion et tous les autres efforts de traduction pour langues peu dotées, y compris OMT-1600 :** nous ne produisons pas seulement des méthodes pour les communautés — nous transférons la propriété des méthodes *aux* communautés. Le code, les poids, l'infrastructure de déploiement — tout devient propriété communautaire. Ce n'est pas un cadre théorique — c'est le pipeline opérationnel pour chaque méthode de langue autochtone sur la plateforme.

---

## Alignement OCAP®

Le processus de transfert de propriété met directement en œuvre les [principes OCAP®](/docs/sovereignty/data-sovereignty) :

| Principe | Mise en œuvre |
|---|---|
| **Ownership** | L'organisation de gouvernance détient le titre du code de la méthode et des poids du modèle |
| **Control** | L'organisation de gouvernance contrôle les conditions de déploiement, l'accès et la tarification |
| **Access** | Les membres de la communauté accèdent à la méthode via l'API champollion ou le téléchargement direct |
| **Possession** | Les ressources linguistiques (données d'entraînement, dictionnaires, règles FST) restent sur l'infrastructure contrôlée par la communauté via la méthode `api` |

---

## Pour les chercheurs

Si vous développez une méthode pour une langue autochtone :

1. **Établissez une relation** avec la communauté linguistique avant de commencer
2. **Utilisez des données sous licence ouverte** pour le développement (pas de ressources restreintes à la communauté)
3. **Documentez la provenance** dans votre [fiche de résultats](/docs/specifications/run-card) — listez chaque ressource, sa licence et son origine
4. **Soyez prêt à transférer** — si votre méthode réussit, le code appartient à la communauté, pas à vous
5. **C'est une fonctionnalité, pas une limitation** — votre contribution est l'architecture et la technique, que vous pouvez publier et réutiliser. La contribution de la communauté est la connaissance linguistique qui la rend efficace pour leur langue.

---

## Voir aussi

- [Souveraineté des données](/docs/sovereignty/data-sovereignty) — principes OCAP, CARE et Te Mana Raraunga
- [Le modèle économique](/docs/sovereignty/economic-model) — comment la propriété devient un revenu
- [Soutenir une langue peu dotée en ressources](/docs/community/low-resource-languages) — le contexte de recherche