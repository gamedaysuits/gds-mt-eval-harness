---
sidebar_position: 2
title: "FAQ"
related:
  - label: "How It Works"
    to: /docs/how-it-works
    kind: doc
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Glossary"
    to: https://champollion.dev/glossary
    kind: glossary
    note: "Plain-language definitions for every technical term"
---
# Questions Fréquemment Posées

> **Résumé exécutif.** Réponses aux questions courantes sur la MT Eval Arena — comment fonctionne la notation, ce qui entraîne une disqualification, comment gérer les langues sans FST, recommandations de modèles et de paramètres, et le processus de soumission.

---

## Notation et Métriques

### Quelles métriques le harness calcule-t-il ?

Le harness calcule cinq métriques pour le cri des Plaines (la langue de référence actuelle). Trois sont indépendantes de la langue et fonctionneront pour n'importe quelle langue ; deux reposent actuellement sur des plugins spécifiques au CRK et seront généralisées à mesure que nous nous étendons à d'autres langues.

| Métrique | Échelle | Ce qu'elle mesure | Statut |
|--------|-------|-----------------|--------|
| **chrF++** | 0–100 | Chevauchement des n-grammes de caractères entre les traductions prédites et de référence. Meilleure métrique de surface pour les langues morphologiquement riches. Utilise la notation native de sacrebleu. | ✅ Toutes les langues |
| **Correspondance exacte** | 0,0–1,0 | Proportion d'entrées où la prédiction correspond exactement à la référence après normalisation. | ✅ Toutes les langues |
| **Acceptation FST** | 0,0–1,0 | Proportion de mots de sortie acceptés par un transducteur à états finis (analyseur morphologique). Calculée uniquement lorsqu'un binaire FST est fourni. | ✅ Toutes les langues avec FST |
| **Correspondance équivalente** | 0,0–1,0 | Fraction d'entrées correspondant à la référence ou à une variante acceptable — tenant compte de l'ordre des mots, de la convention orthographique et des différences dialectales. | ⚡ CRK (généralisation en cours) |
| **Score sémantique** | 0,0–1,0 | Score de préservation du sens — la traduction capture-t-elle bien le sens prévu indépendamment de la forme de surface ? | ⚡ CRK (généralisation en cours) |

Des métriques supplémentaires sont prévues : **précision morphologique**, **détection du code-switching**, **respect de la terminologie** et **détection des hallucinations**. Voir [Spécification de notation §2](/docs/specifications/scoring#2-metric-inventory) pour l'inventaire complet de 19 métriques.

### Comment le score composite est-il calculé ?

Le composite est une moyenne pondérée des métriques disponibles, normalisée à une échelle 0,0–1,0. Les poids sont définis dans deux profils :

- **Profil A** (langues avec FST) : 9 métriques, les métriques structurelles (FST + précision morphologique) représentent 40 % du poids composite
- **Profil B** (langues sans FST) : 8 métriques, les métriques sémantiques et chrF++ ont un poids égal au sommet

Lorsqu'une métrique n'est pas disponible, son poids est redistribué proportionnellement entre les métriques restantes. Cela signifie que les benchmarks en phase initiale (avec seulement chrF++ et correspondance exacte disponibles) produisent toujours des composites valides — les poids effectifs reflètent simplement ce qui est disponible.

**Les tableaux de poids complets, les règles de normalisation et la justification des exclusions se trouvent dans [Spécification de notation §4](/docs/specifications/scoring#4-composite-score).** Le code du harness reflète ces tableaux dans `mt_eval_harness/scoring.py`. chrF++ est normalisé en divisant par 100 avant la pondération ; les taux de code-switching et d'hallucinations sont inversés (inférieur = meilleur).

### Que sont les niveaux de qualité ?

Les niveaux de qualité sont des étiquettes heuristiques mappées à des plages de scores composites. Ils aident à communiquer ce qu'un score *signifie* pratiquement :

| Niveau | Plage composite | Interprétation |
|------|----------------|----------------|
| **Baseline** | 0,00 – 0,30 | Qualité non utile. La méthode nécessite une amélioration significative. |
| **Émergent** | 0,30 – 0,50 | Montre des promesses. Certaines traductions sont correctes mais incohérentes. |
| **Fonctionnel** | 0,50 – 0,70 | Utilisable comme référence avec révision humaine. Non adapté au déploiement sans révision. |
| **Déployable** | 0,70 – 0,85 | Prêt pour une utilisation en production avec révision périodique. Déclenche l'admissibilité au transfert de propriété. |
| **Fluide** | 0,85 – 1,00 | Qualité quasi native. Adapté au déploiement sans supervision. |

### Quelle est la différence entre les niveaux de qualité et les niveaux de vérification ?

**Les niveaux de qualité** décrivent *ce que le score automatisé signifie* (Baseline → Fluide). **Les niveaux de vérification** décrivent *qui a validé le résultat* :

| Niveau de vérification | Ce que cela signifie |
|-------------------|---------------|
| **Auto-benchmarké** | Le soumetteur a exécuté le harness lui-même. Les scores sont plausibles mais non vérifiés. |
| **Vérifié par GDS** | Un responsable a reproduit le résultat en utilisant la configuration de méthode soumise. |
| **Validé par la communauté** | Des locuteurs bilingues ont examiné les traductions et confirmé la qualité. |

Une méthode peut être de qualité « Déployable » mais seulement « Auto-benchmarkée » en vérification — ce qui signifie que le score semble excellent mais personne n'a indépendamment confirmé.

---

## Soumission et Disqualification

### Qu'est-ce qui entraîne la disqualification de ma soumission ?

Votre soumission sera rejetée ou signalée si :

1. **Votre méthode a été exposée aux données d'évaluation.** Si vous avez entraîné, affiné, utilisé des invites few-shot ou autrement utilisé des entrées du jeu de données d'évaluation, vos scores sont artificiellement gonflés. Cela inclut l'utilisation des traductions de référence dans votre invite.
2. **Votre carte d'exécution échoue les vérifications d'intégrité.** L'empreinte digitale doit correspondre à la configuration. Les cartes d'exécution falsifiées sont rejetées.
3. **Votre méthode n'implémente pas le protocole TranslationMethod.** Le harness s'attend à `translate(entries, config) → results`. Les intégrations personnalisées qui contournent le harness ne sont pas acceptées.

### Puis-je soumettre plusieurs fois ?

Oui. Le classement suit toutes les soumissions. Vous pouvez itérer — exécuter des dizaines d'expériences, soumettre uniquement la meilleure. Chaque soumission enregistre une empreinte digitale unique, il n'y a donc aucune ambiguïté sur la soumission qui a produit quel score.

### Comment faire vérifier mon score ?

1. **Auto-benchmarké (automatique) :** Chaque soumission commence ici.
2. **Vérifié par GDS :** Soumettez votre méthode en tant que package reproductible (code + configuration + données de coaching). Un responsable la réexécutera contre le même jeu de données et confirmera que les scores correspondent.
3. **Validé par la communauté :** Pour les langues autochtones, cela nécessite que des locuteurs bilingues examinent un échantillon de traductions. Cela ne peut pas être automatisé — cela nécessite l'engagement de la communauté.

### L'API de soumission est-elle en direct ?

Pas encore. Le point de terminaison `https://mtevalarena.org/api/leaderboard/submit` est aspirationnel. Les soumissions actuelles doivent être effectuées via une demande de tirage vers le [dépôt du harness d'évaluation](https://github.com/gamedaysuits/arena) avec votre JSON de carte d'exécution dans le répertoire `results/`.

---

## Modèles et Paramètres

### Quel modèle dois-je utiliser ?

Il n'y a pas de meilleur modèle unique — cela dépend de la paire de langues, de votre budget et de votre approche. Conseils généraux :

| Type de langue | Point de départ recommandé | Pourquoi |
|---------------|---------------------------|-----|
| **Haute ressource** (français, espagnol, japonais) | `google/gemini-2.5-flash` ou `gpt-4o-mini` | Rapide, bon marché, ligne de base solide |
| **Basse ressource avec une certaine couverture LLM** (quechua, yoruba) | `google/gemini-2.5-pro` ou `anthropic/claude-sonnet-4` | Les modèles plus grands ont une meilleure connaissance latente |
| **Polysynthétique / très basse ressource** (cri des Plaines, inuktitut) | `google/gemini-2.5-pro` avec coaching | Les données de coaching importent plus que le choix du modèle. OMT-1600 inclut certaines langues polysynthétiques (par exemple, CRK au niveau R1) mais avec une tokenisation BPE standard — benchmarkez-le comme ligne de base dans l'Arena. |

Le harness d'évaluation utilise OpenRouter, donc n'importe quel modèle disponible sur OpenRouter peut être benchmarké. Exécutez `champollion models --method llm` pour voir les modèles disponibles.

### Quelle température dois-je utiliser ?

Inférieur est généralement meilleur pour la traduction :

| Température | Effet | Recommandé pour |
|-------------|--------|-----------------|
| **0,0 – 0,2** | Sortie hautement déterministe et cohérente | Méthodes de production, benchmarks finaux |
| **0,3 – 0,5** | Certaines variations, occasionnellement plus créatif | Exploration, itération précoce |
| **0,6+** | Variation élevée, imprévisible | Non recommandé pour le benchmarking MT |

La température est enregistrée dans la carte d'exécution, donc différentes températures produisent différentes empreintes digitales — elles sont traitées comme des expériences différentes.

### Les données de coaching aident-elles ?

Oui, significativement — pour les langues basse ressource. Les données de coaching (règles de grammaire, entrées de dictionnaire, notes de style) sont injectées dans l'invite système du LLM. Pour le cri des Plaines, les méthodes coachées surpassent systématiquement les méthodes LLM brutes pour les langues polysynthétiques car les LLM à usage général ont une exposition polysynthétique limitée et aucune conscience morphologique. Même OMT-1600, qui a été spécifiquement entraîné pour CRK, utilise une tokenisation BPE standard qui ne peut pas représenter structurellement la morphologie polysynthétique. Les données de coaching fournissent le contexte linguistique que le modèle n'a pas.

Pour les langues haute ressource (français, espagnol), le coaching a moins d'impact car le modèle a déjà une connaissance de base solide.

Voir [Données de coaching](https://champollion.dev/docs/concepts/coaching-data) pour la spécification complète.

---

## FST et Validation Morphologique

### Que faire s'il n'y a pas de FST pour ma langue ?

De nombreuses langues n'ont pas de transducteur à états finis. C'est OK — le harness fonctionne sans. Le score composite utilise les poids du profil B (voir [Spécification de notation §4.3](/docs/specifications/scoring#43-weight-tables)) qui décalent le poids vers les métriques sémantiques et de surface. L'acceptation FST est marquée comme `null` dans la carte d'exécution.

Les principaux registres pour les FST existants :

| Registre | Couverture | URL |
|----------|----------|-----|
| **GiellaLT** | Sámi, cri, inuktitut et autres langues arctiques/subarctiques | [giellalt.uit.no](https://giellalt.uit.no/) |
| **ALTLab** | Cri des Plaines, cri des bois, ojibwé | [altlab.artsrn.ualberta.ca](https://altlab.artsrn.ualberta.ca/) |
| **Apertium** | ~60 paires de langues, principalement européennes | [apertium.org](https://apertium.org/) |
| **UniMorph** | Paradigmes morphologiques pour 150+ langues | [unimorph.github.io](https://unimorph.github.io/) |

### Puis-je construire un FST ?

Oui, mais ce n'est pas trivial. Un FST encode les règles morphologiques d'une langue — toutes les formes de mots valides. En construire un nécessite une connaissance linguistique approfondie de la langue. Si vous avez accès à une grammaire morphologique (par exemple, d'un département de linguistique), elle peut être compilée en FST en utilisant des outils comme [HFST](https://hfst.github.io/) ou [Foma](https://fomafst.github.io/).

### Comment fonctionne le gating FST en pratique ?

Le pipeline avec gating FST fonctionne comme suit :

1. Le LLM génère une traduction
2. Chaque mot de la sortie est vérifié par rapport au FST
3. Les mots que le FST rejette sont signalés comme morphologiquement invalides
4. La méthode peut réessayer avec rétroaction (« le mot X n'est pas valide, réessayez »)
5. Après les tentatives, les mots invalides restants sont enregistrés

Le taux d'acceptation FST mesure combien de mots passent la validation. Voir le [Tutoriel du pipeline avec gating FST](/docs/tutorials/fst-gated-pipeline) pour un exemple complet travaillé.

---

## Données et Jeux de Données

### Puis-je contribuer un jeu de données pour une nouvelle langue ?

Oui. Exigences minimales de [Spécification de benchmark §11](/docs/specifications/benchmark#11-extending-to-new-languages) :

- **50 entrées de référence** (source + traduction de référence vérifiée)
- **30 entrées de développement** (peuvent chevaucher la référence pour les petits corpus)
- **Consentement communautaire** (pour les langues autochtones, autorisation explicite d'un organisme de gouvernance)
- **Documentation de provenance** (d'où proviennent les données, quelle licence s'applique)

Les nouveaux jeux de données ouvrent automatiquement de nouvelles pistes de classement. Voir [Pour les communautés linguistiques](/docs/community/for-language-communities) pour le guide du contributeur.

### Quel format mon jeu de données doit-il avoir ?

JSON avec les noms de champs canoniques :

```json
{
  "name": "my-language-dev-v1",
  "language_pair": "en-xxx",
  "segment": "development",
  "version": "1.0",
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "[translation in target language]",
      "difficulty": 1,
      "domain": "general"
    }
  ]
}
```

Voir [Jeux de données](/docs/leaderboard/datasets) pour le schéma complet et les définitions de niveaux de difficulté.

---

## Souveraineté et Propriété

### Qui possède une méthode construite pour une langue autochtone ?

Pour les langues autochtones, les méthodes qui atteignent le niveau Déployable (composite ≥ 0,70) ET passent la validation communautaire déclenchent le processus de [transfert de propriété](/docs/sovereignty/ownership-transfer). La propriété du code est transférée du chercheur à l'organisme de gouvernance de la communauté linguistique.

Le chercheur conserve :
- Les droits de publication (articles académiques sur la méthode)
- Le crédit sur le classement
- Le droit d'appliquer les mêmes *techniques* à d'autres langues

L'organisme de gouvernance obtient :
- La propriété complète du code de la méthode et des données de coaching
- Le contrôle du déploiement (quand, où, comment)
- Les revenus de l'utilisation de l'API (90 % communauté, 10 % infrastructure)

### Puis-je utiliser champollion pour les langues non autochtones sans aucune préoccupation de souveraineté ?

Oui. Pour les langues standard (français, japonais, espagnol, etc.), il n'y a aucune considération de souveraineté. Utilisez champollion normalement — traduisez, synchronisez, publiez comme vous le souhaitez. Le cadre de souveraineté s'applique spécifiquement aux langues autochtones et gouvernées par la communauté où les principes de gouvernance des données (OCAP®, CARE, Te Mana Raraunga) nécessitent une considération particulière.

---

## Voir aussi

- **[Comment ça marche](https://champollion.dev/how-it-works)** — l'explication complète de la solution
- **[Spécification de notation](/docs/specifications/scoring)** — la source unique de vérité pour toute la logique de notation (métriques, poids, niveaux)
- **[Spécification de benchmark](/docs/specifications/benchmark)** — protocole d'évaluation, format de corpus, souveraineté
- **[Soumettre une méthode](/docs/getting-started/submit-a-method)** — guide de démarrage rapide étape par étape
- **[Règles du classement](/docs/leaderboard/rules)** — critères de soumission
- **[Souveraineté des données](/docs/sovereignty/data-sovereignty)** — OCAP®, CARE et obligations éthiques