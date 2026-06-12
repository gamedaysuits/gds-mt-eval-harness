---
sidebar_position: 3
title: "Du benchmark à l'utilisation quotidienne : le parcours de post-édition"
slug: '/perspectives/from-benchmark-to-daily-use'
description: "Comment une méthode de traduction évaluée en benchmark devient un flux de travail de traduction communautaire : brouillon automatique, post-édition par locuteur·rice fluide, texte publié — avec des seuils de qualité honnêtes à chaque étape."
related:
  - label: "Deploy to Production"
    to: /docs/getting-started/deploy-to-production
    kind: guide
    note: "From proven method to live translation"
  - label: "Cookbook: Partial Translation (Human + Machine)"
    to: /docs/tutorials/partial-translation
    kind: cookbook
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The quality thresholds behind the path"
  - label: "Translation Is Not Revitalization"
    to: /docs/perspectives/translation-is-not-revitalization
    kind: position
---
# Du benchmark à l'utilisation quotidienne : le parcours de post-édition

> **La version courte.** Un score au classement n'est pas un produit. Le parcours allant de « cette méthode obtient 0,78 » à « le bureau de la bande publie des documents dans la langue chaque semaine » passe par exactement un flux de travail : la machine produit un brouillon, un locuteur fluide le corrige, et seul le texte corrigé est publié. Chaque seuil de qualité dans nos spécifications est calibré pour ce flux de travail — non pour la sortie machine non supervisée, que nous n'approuvons pour aucune langue sur cette plateforme.

Les gens demandent parfois quand une méthode de traduction sera « assez bonne pour être utilisée directement ». Pour les langues que cette Arena sert, cette question contient un piège. La réponse honnête est que le seuil qui vaut la peine d'être visé n'est pas « assez bon pour publier sans révision » — c'est **« assez bon pour que réviser un brouillon soit mieux que traduire à partir de zéro »**. Ce seuil est beaucoup plus bas, il est mesurable, et le franchir change ce qu'un bureau de traduction communautaire peut produire en une semaine.

---

## Le flux de travail, de bout en bout

```
 English source document
        │
        ▼
 Machine draft  ←  a benchmarked, community-owned method
        │
        ▼
 Fluent-speaker post-edit  ←  the human gate; nothing skips it
        │
        ▼
 Published text  ←  carries human approval, not a machine score
        │
        ▼
 (Optional, community-controlled) corrections become
 data that improves the next version of the method
```

Trois points à remarquer :

1. **La machine ne publie jamais.** L'unité de sortie est un brouillon. La passe de correction du locuteur n'est pas une assurance qualité ajoutée à la fin — c'est le flux de travail.
2. **Le temps du locuteur est la ressource optimisée.** Une méthode est meilleure qu'une autre méthode exactement dans la mesure où elle laisse moins à corriger au locuteur. La recherche sur la post-édition pour les langues bien dotées en ressources constate régulièrement qu'elle est plus rapide que la traduction à partir de zéro à une qualité TA modérée (Plitt & Masselot 2010 ; Green, Heer & Manning 2013, tous deux cités avec des liens dans [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization)). Que cela s'applique aux langues polysynthétiques est précisément ce que le benchmark existe pour découvrir — nous le traitons comme une hypothèse à vérifier par langue, non comme une hypothèse.
3. **La boucle de rétroaction est maîtrisée.** Chaque document corrigé est un potentiel de données d'entraînement et de coaching — et il appartient à la communauté, pour être réinjecté (ou non) selon ses conditions en vertu des règles de [souveraineté des données](/docs/sovereignty/data-sovereignty). Le mécanisme de rétroaction est un objectif de conception de la plateforme, pas encore une fonctionnalité construite ; voir [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections) pour savoir comment les corrections et la provenance sont censées fonctionner.

## Ce que les niveaux de qualité signifient pour l'utilisation réelle

Le classement évalue les méthodes sur une composition de métriques automatisées ([Scoring Specification](/docs/specifications/scoring)), et les scores correspondent à des niveaux nommés. Voici la traduction honnête de ces niveaux en termes d'utilisation quotidienne :

| Niveau (composite) | Ce que cela signifie pour le parcours de post-édition |
|---|---|
| **Baseline** (0,00–0,30) | Inutilisable pour quoi que ce soit. La sortie n'est largement pas la langue cible. Utile uniquement comme plancher de recherche. |
| **Emerging** (0,30–0,50) | Toujours pas un outil de brouillon. Des fragments corrects apparaissent, mais un locuteur passerait plus de temps à corriger qu'à écrire à partir de zéro. |
| **Functional** (0,50–0,70) | Le premier niveau où la post-édition *pourrait* surpasser la traduction à partir de zéro pour les textes faciles — vaut la peine de tester avec un locuteur, pas la peine de s'y fier. Des erreurs morphologiques fréquentes subsistent. |
| **Deployable** (0,70–0,85) | Le niveau cible pour le flux de travail ci-dessus : des brouillons où la plupart de la morphologie est correcte et un locuteur fluide peut corriger significativement plus vite que de retraduire. **« Deployable » signifie déployable *dans un flux de travail de post-édition* — jamais « publier sans révision »**. |
| **Fluent** (0,85–1,00) | S'approchant d'une traduction humaine compétente ; les erreurs sont rares et mineures. La passe de révision reste — elle devient juste plus rapide. |

Deux règles d'honnêteté structurelle s'ajoutent à ce tableau, directement issues de la [Benchmark Specification §5 et §7](/docs/specifications/benchmark#5-quality-tiers) :

- **Les niveaux automatisés sont des étiquettes provisoires, pas des verdicts.** Ce sont des nominations pour examen humain. Les seuils seront recalibrés à mesure que les données de validation des locuteurs s'accumulent, et ils peuvent différer selon les langues.
- **Aucune méthode ne peut revendiquer Deployable ou supérieur sans examen communautaire.** Un échantillon stratifié de sa sortie est soumis à des locuteurs bilingues, qui évaluent chaque traduction *rejeter / gist / acceptable / excellent*. L'organisation de gouvernance — pas le classement — décide si la méthode progresse.

À titre de comparaison, le seuil du [Founder's Prize](/docs/specifications/prizes) (composite ≥ 0,80, ≥99 % de mots morphologiquement valides, ≥70 % de traductions évaluées acceptable-ou-mieux par les locuteurs) décrit une méthode dont les erreurs restantes sont des *erreurs de langue réelle* — mauvaise inflexion, pas des mots fabriqués. C'est ce qu'« un brouillon qui vaut le temps d'un locuteur » ressemble en chiffres.

## D'une méthode gagnante à un bureau fonctionnel

Supposons qu'une méthode franchisse ces portes. Les étapes restantes sont organisationnelles, et elles sont spécifiées plutôt qu'improvisées :

1. **La propriété est transférée.** Le code de la méthode devient la propriété de l'organisation de gouvernance de la communauté — le développeur conserve les droits d'attribution et de publication ([Ownership Transfer](/docs/sovereignty/ownership-transfer)).
2. **La méthode devient un service.** Elle est empaquetée en tant que plugin et servie via la plateforme de déploiement, la communauté contrôlant l'accès, la tarification et les utilisations autorisées ([Deploy to Production](/docs/getting-started/deploy-to-production)).
3. **Les traducteurs l'intègrent à leur journée.** Un bureau de traduction pointe son flux de travail de document existant vers l'API de la méthode : texte source en entrée, brouillon en sortie, post-édition, publication. Le texte publié porte le nom et l'autorité du traducteur — la machine est un outil sur son bureau, comme un dictionnaire.
4. **Les revenus suivent l'utilisation.** Les développeurs externes qui utilisent la méthode paient des tarifs mesurés, et 90 % de ces revenus vont à l'organisation de gouvernance ([The Economic Model](/docs/sovereignty/economic-model)) — qui peut financer plus d'heures de traducteur, fermant la boucle.

## Où cela en est aujourd'hui

Clairement : le parcours complet est spécifié de bout en bout, et partiellement construit. Le harnais d'évaluation, les métriques, les fiches de course et le classement public existent ; le corpus de développement Plains Cree et un prix actif existent ; la plateforme de déploiement existe. L'interface d'examen communautaire, le bac à sable d'évaluation et la boucle de rétroaction de texte corrigé sont spécifiés mais pas encore opérationnels — les spécifications les marquent comme prévus, et nous aussi. Aucune méthode n'a encore complété le parcours entier du benchmark à l'utilisation quotidienne communautaire. Ce parcours est la définition du succès du projet, ce qui est exactement pourquoi nous ne le revendiquerons pas prématurément.

---

## Ce que cela signifie pour vous

:::info Si vous êtes un membre de la communauté
Un badge « Deployable » au classement ne signifie jamais qu'une machine publiera dans votre langue sans supervision — cela signifie qu'un générateur de brouillon peut être prêt à *auditionner* pour vos traducteurs, selon vos conditions, avec vos locuteurs comme juges (rémunérés — voir [How Speakers Get Paid](/docs/perspectives/how-speakers-get-paid)). Si votre communauté gère un bureau de traduction, la question pertinente à nous poser est : « à quoi ressemblerait un projet pilote, et qui examine la sortie ? »
:::

:::info Si vous êtes un chercheur
Le cadre de post-édition change ce qui vaut la peine de mesurer : le temps jusqu'au texte acceptable avec un locuteur dans la boucle, pas seulement le score composite. Les métriques de l'Arena sont des approximations pour cela ([Scoring Specification §1](/docs/specifications/scoring)), et les études de post-édition par langue pour les langues morphologiquement complexes sont un écart de recherche ouvert que cette infrastructure est conçue pour soutenir.
:::

:::info Si vous êtes un développeur
Optimisez pour l'éditeur, pas pour la métrique. Une méthode qui produit des mots réels avec des inflexions occasionnellement incorrectes est corrigeable en secondes par un locuteur ; une méthode qui hallucine des formes plausibles empoisonne tout le flux de travail — c'est pourquoi la validité morphologique est si strictement contrôlée ici. Commencez par [Submit a Method](/docs/getting-started/submit-a-method), et lisez la [Method Interface](/docs/specifications/methods) pour savoir ce que vous remettrez éventuellement si vous gagnez.
:::

## Voir aussi

- [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization) — pourquoi la porte humaine est le point, pas une limitation
- [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections) — ce qui se passe quand le texte publié est quand même incorrect
- [Benchmark Specification §7](/docs/specifications/benchmark#7-human-validation) — la porte de validation humaine, formellement