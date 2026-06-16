---
sidebar_position: 1
title: "Évaluation de la traduction automatique"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "How the composite score is computed"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Evaluation Datasets"
    to: /docs/leaderboard/datasets
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "The rules, applied"
---
# Évaluation de la traduction automatique

> **Résumé exécutif.** Cette page définit les critères de soumission au classement, les métriques de notation (chrF++, acceptation FST, correspondance exacte, correspondance équivalente, score sémantique), les politiques anti-triche, les niveaux de vérification et le flux de soumission. Les méthodes exposées aux données d'évaluation sont disqualifiées.

champollion inclut un cadre d'évaluation de la traduction automatique conçu pour l'**évaluation comparative reproductible** des méthodes de traduction — en particulier pour les langues peu dotées en ressources et les langues autochtones où les étalons de référence MT standard n'existent pas et où les affirmations de qualité sont difficiles à vérifier.

---

## Le classement

Le cœur du système est le **[Classement des méthodes](https://champollion.dev/leaderboard)** — un tableau de bord en direct, alimenté par Supabase, où les chercheurs et les membres de la communauté soumettent et comparent les méthodes de traduction avec une évaluation reproductible et empreinte numérique.

Chaque soumission comprend :

- **Pipeline empreinte numérique** — lié à un commit Git spécifique et à un hash de configuration, de sorte que les résultats remontent au code exact qui les a produits
- **Ensemble de données versionnée** — avec hash de contenu et versionnée ; les scores ne sont comparables que dans la même version d'ensemble de données
- **Métriques standardisées** — tous les scores sont calculés par le harnais d'évaluation partagé, éliminant les différences d'implémentation
- **Niveaux de confiance** — auto-évalué, GDS Verified ou Community Validated
- **Suivi des coûts** — coût API par soumission, de sorte que les compromis coût-qualité sont transparents

Le classement suit actuellement cinq métriques. Trois fonctionnent pour n'importe quelle langue ; deux sont disponibles pour le cri des Plaines et seront généralisées à mesure que nous nous développons :

| Métrique | Type | Ce qu'elle mesure |
|----------|------|------------------|
| **chrF++** | Score F des n-grammes de caractères | Métrique de qualité principale — corrèle bien avec le jugement humain, en particulier pour les langues morphologiquement riches |
| **Exact Match** | Proportion de correspondances parfaites | Précision stricte — à quelle fréquence la traduction correspond-elle exactement à l'étalon de référence ? |
| **FST Acceptance** | Taux de passage de la porte morphologique | Pour les méthodes avec vérification par transducteur à états finis — quelle proportion des résultats sont morphologiquement valides ? |
| **Equivalent Match** | Taux de variante acceptable | Fraction correspondant à la référence ou à une variante acceptable (ordre des mots, convention orthographique). Actuellement CRK ; généralisation en cours. |
| **Semantic Score** | Fidélité sémantique | Préservation du sens — la traduction capture-t-elle le sens prévu indépendamment de la forme de surface ? Actuellement CRK ; généralisation en cours. |

:::info Suite complète de métriques
La [Spécification de notation](/docs/specifications/scoring) définit l'inventaire complet de 19 métriques réparties en 5 catégories, la formule du score composite, les tableaux de poids et les seuils de niveau de qualité.
:::

**[→ Consulter le classement](https://champollion.dev/leaderboard)**

---

## Ensembles de données disponibles

### Ensemble de développement EDTeKLA v1

Le premier ensemble de données d'évaluation, construit pour la traduction anglais→cri des Plaines (SRO). Créé par le [groupe de recherche EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) de l'Université de l'Alberta.

| Propriété | Valeur |
|-----------|--------|
| **ID** | `edtekla-dev-v1` |
| **Paire de langues** | EN → CRK (cri des Plaines, orthographe SRO) |
| **Nombre d'entrées** | 404 (`master_corpus.json` : 62 or + 342 manuel) ; 548 au total disponibles |
| **Licence** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| **Provenance** | `gold_standard` (vérifiée par des locuteurs), `textbook` (matériels pédagogiques publiés) |

### FLORES+ Devtest — Utilisation en développement uniquement

> [!WARNING]
> **FLORES+ est disponible pour le développement et le débogage mais n'est PAS utilisé pour l'évaluation officielle du classement.** FLORES+ (anciennement Meta FLORES-200) est un ensemble de données d'évaluation largement public sur lequel les LLM de pointe ont presque certainement été entraînés. Les scores par rapport à FLORES+ ne reflètent pas de manière fiable la qualité réelle de la traduction pour les méthodes basées sur LLM. Les méthodes non-LLM (FST, basées sur des règles, NMT affiné) sont moins affectées mais les scores FLORES+ ne sont toujours pas publiés au classement.

Les fixtures FLORES+ restent disponibles dans `test/benchmark/fixtures/` pour les tests de fumée du pipeline, la validation inter-langues et l'utilisation en développement. L'évaluation officielle utilise des corpus personnalisés construits à partir de texte rédigé par des humains non disponible publiquement sous forme parallèle.

Voir [Ensembles de données d'évaluation](/docs/leaderboard/datasets) pour le schéma complet de l'ensemble de données, les niveaux de difficulté et comment créer le vôtre.

:::danger NE PAS ENTRAÎNER sur les données d'évaluation

**Ces ensembles de données sont réservés à l'évaluation.** Les méthodes entraînées, affinées, incitées par quelques exemples ou autrement exposées aux données d'évaluation produiront des scores artificiellement gonflés et seront **disqualifiées du classement.**

Ce n'est pas une suggestion — c'est la règle la plus importante de l'intégrité de l'évaluation. Utilisez des corpus distincts pour l'entraînement. Les ensembles d'évaluation doivent rester invisibles à votre modèle pendant le développement.

Si vous utilisez des données d'entraînement ou des exemples avec quelques coups, ceux-ci doivent provenir de **sources complètement distinctes**. En cas de doute, ne l'incluez pas.
:::

:::warning Non-déterminisme des LLM

Les résultats des LLM sont non-déterministes. Les scores représentent des mesures ponctuelles dans le temps selon des versions de modèle spécifiques et des configurations API. Les fournisseurs de modèles peuvent mettre à jour les poids, les stratégies de décodage ou les filtres de sécurité à tout moment, ce qui peut entraîner une dérive des scores entre les exécutions. Le classement enregistre le slug de modèle exact et l'horodatage pour chaque soumission.
:::

---

## Ce qui fait une bonne méthode

Toutes les méthodes ne sont pas créées égales. Voici ce qui distingue le travail rigoureux des scores gonflés.

### Caractéristiques d'une méthode solide

- **Séparation nette des données d'entraînement et d'évaluation** — votre méthode n'a jamais vu l'ensemble d'évaluation pendant le développement, l'ajustement, l'ingénierie des incitations ou la sélection d'exemples avec quelques coups
- **Reproductible** — quelqu'un d'autre peut cloner votre dépôt, exécuter le harnais et obtenir les mêmes scores (dans les limites du non-déterminisme des LLM)
- **Documentée** — votre [fiche de méthode](/docs/specifications/methods) décrit ce que votre méthode fait, quels outils elle utilise et quelles sont ses limitations
- **Honnête sur la portée** — si votre méthode ne fonctionne que pour une paire de langues, dites-le ; si elle se dégrade sur certains motifs morphologiques, documentez-le
- **Consciente de la communauté** — pour les langues autochtones, votre méthode respecte la souveraineté des données. Vous avez consulté les communautés linguistiques ou utilisé uniquement des données sous licence ouverte

### Signaux d'alerte (ce qui entraîne une disqualification)

| Signal d'alerte | Pourquoi c'est un problème |
|-----------------|---------------------------|
| Entraînement sur les données d'évaluation | Annule complètement l'objectif de l'évaluation. Les scores gonflés trompent tout le monde. |
| Sélection des résultats | Exécution 10 fois et soumission de la meilleure exécution sans divulguer les autres |
| Post-traitement non divulgué | Correction manuelle des résultats avant la notation |
| Données d'entraînement contaminées | Utilisation d'exemples d'ensemble d'évaluation comme incitations avec quelques coups ou entrées de dictionnaire |
| Affirmation de disponibilité commerciale sans provenance | Si votre méthode utilise des données CC BY-NC-SA, elle n'est pas prête commercialement |

### Niveaux de vérification

Les niveaux de vérification décrivent **qui a validé le résultat** — distinct des niveaux de qualité (Baseline → Fluent) définis dans la [Spécification de notation, §5](/docs/specifications/scoring#5-quality-tiers), qui décrivent ce que le score composite automatisé signifie.

| Niveau | Signification | Comment l'obtenir |
|--------|---------------|-------------------|
| **Auto-évalué** | Vous avez exécuté le harnais vous-même et soumis les résultats | Ouvrez une PR avec votre fiche d'exécution |
| **GDS Verified** | Les responsables de champollion ont reproduit vos résultats | Soumettez votre méthode en tant que plugin installable |
| **Community Validated** | L'organisation de gouvernance a exécuté contre l'étalon de référence or + examen communautaire | Soumettez le code de la méthode à l'organisation de gouvernance |

---

## Comment soumettre

1. **Construisez votre méthode** — voir [Construire une méthode](/docs/specifications/methods) pour l'interface de méthode
2. **Exécutez le harnais** — voir [Harnais d'évaluation](/docs/specifications/harness) pour la configuration et l'utilisation
3. **Générez une fiche d'exécution** — le harnais produit une fiche d'exécution JSON avec vos scores, votre empreinte numérique et vos métadonnées
4. **Ouvrez une PR** — soumettez votre fiche d'exécution au [dépôt du harnais d'évaluation](https://github.com/gamedaysuits/arena)
5. **Apparaissez au classement** — une fois fusionnée, vos résultats apparaissent sur le [Classement des méthodes](https://champollion.dev/leaderboard)

---

## Orientations futures

- **Exécutions de comparaison de modèles complètes** — évaluation systématique des modèles de pointe (GPT-4o, Claude, Gemini, etc.) dans les langues champollion en utilisant des corpus d'évaluation personnalisés (pas des étalons de référence publics)
- **Plus de paires de langues** — quechua, inuktitut et autres langues peu dotées en ressources à mesure que des ensembles de données vérifiés par la communauté deviennent disponibles
- **Importation d'ensembles de données** — outils pour convertir les ensembles de données d'évaluation externes (WMT, Tatoeba, etc.) au format d'évaluation champollion
- **Réexécutions automatisées** — détection des changements de version de modèle et réexécution des étalons de référence pour suivre la dérive des scores

---

## Voir aussi

- **[Classement des méthodes](https://champollion.dev/leaderboard)** — scores en direct et soumissions
- **[Harnais d'évaluation](/docs/specifications/harness)** — comment exécuter les évaluations
- **[Ensembles de données d'évaluation](/docs/leaderboard/datasets)** — format d'ensemble de données et ensembles de données disponibles
- **[Construire une méthode](/docs/specifications/methods)** — la spécification de l'interface de méthode
- **[Spécification de fiche d'exécution](/docs/specifications/run-card)** — le schéma JSON de fiche d'exécution
- **[Spécification d'étalon de référence](/docs/specifications/benchmark)** — protocole d'évaluation, format de corpus, souveraineté
- **[Spécification de notation](/docs/specifications/scoring)** — SSOT pour les métriques, les poids composites et les niveaux de qualité