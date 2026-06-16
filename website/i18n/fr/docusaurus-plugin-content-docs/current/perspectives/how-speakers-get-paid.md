---
sidebar_position: 2
title: "Comment les contributeur·rice·s sont rémunéré·e·s"
slug: '/perspectives/how-speakers-get-paid'
description: "Ce que les validateur·rice·s communautaires et les traducteur·rice·s perçoivent pour leur travail de benchmarking, pourquoi la rémunération des contributeur·rice·s est non-négociable, et comment la compensation évolue à mesure que l'Arena se développe. Tous les chiffres proviennent des spécifications publiées."
related:
  - label: "Speaker Validation Protocol"
    to: /docs/specifications/speaker-validation
    kind: spec
    note: "The work validators are paid for"
  - label: "Prize Specification"
    to: /docs/specifications/prizes
    kind: spec
    note: "Where prize money goes, and why"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
---
# Comment les locuteurs sont rémunérés

> **Note de transparence.** Chaque chiffre de cette page figure déjà dans une spécification publiée — la [Spécification du benchmark §10](/docs/specifications/benchmark#10-cost-framework), le [Protocole de validation des locuteurs](/docs/specifications/speaker-validation), et la [Spécification des prix](/docs/specifications/prizes). Cette page les rassemble en un seul endroit, en langage clair, afin que personne n'ait besoin de lire une spécification pour savoir ce que vaut le temps d'un locuteur ici. Elle ne s'engage à rien au-delà de ce que ces documents énoncent déjà.

Un locuteur bilingue capable de juger si une phrase produite par une machine est réelle, fluide et signifie la bonne chose est le participant le plus rare et le plus précieux de tout ce système. Tout le reste — harnais, métriques, classements — existe pour faire en sorte qu'une petite quantité du temps de cette personne aille très loin.

La première règle est donc simple : **les locuteurs sont rémunérés pour leur temps, à des tarifs professionnels, indépendamment des résultats.**

---

## Pourquoi rémunérer les locuteurs est non négociable

La recherche en technologie linguistique a l'habitude de traiter les locuteurs courants comme une ressource gratuite — un « engagement communautaire » qui produit des ensembles de données, des articles et des carrières pour tout le monde sauf les locuteurs. Nous considérons ce modèle comme extractif, et les personnes les plus qualifiées pour faire ce travail sont précisément celles dont le temps est déjà réclamé par le travail urgent d'enseigner, de traduire et d'élever des enfants dans la langue.

Trois conséquences de conception en découlent :

1. **Pas de pipeline de bénévoles.** Nous ne demandons pas aux locuteurs de donner du travail d'évaluation en faveur de la recherche. La participation est un engagement rémunéré, et le refuser ne coûte rien au locuteur.
2. **Le paiement est inconditionnel.** Les locuteurs sont rémunérés que leurs évaluations soient utilisées ou non, et le paiement n'est pas subordonné aux résultats. Le protocole publié s'engage à verser le paiement dans les deux semaines suivant l'achèvement de chaque bloc de tâches.
3. **La rémunération n'est pas tout.** Les locuteurs qui contribuent des évaluations reçoivent également un crédit (nommé ou anonyme, à leur choix), une co-paternité optionnelle sur les publications qui utilisent leurs évaluations, le droit de retirer leurs contributions à tout moment, et un droit de veto sur la publication des résultats qu'ils jugent problématiques. Ces conditions figurent dans le [Protocole de validation des locuteurs §5–6](/docs/specifications/speaker-validation), et non dans une lettre d'accompagnement.

## Les tarifs publiés

Le cadre de coûts du benchmark fixe la rémunération des locuteurs bilingues à **50–65 CAD par heure** pour le travail de corpus et de validation. Voici ce que cela signifie par rôle :

### Construire un corpus de benchmark

La création des traductions de référence par rapport auxquelles chaque méthode est évaluée est la tâche fondamentale du locuteur. Le budget d'établissement publié par langue :

| Travail | Plage publiée | Base |
|---------|---------------|------|
| Curation du corpus (50–150 entrées) | 2 500–6 000 $ | 50–65 $/h, temps du locuteur bilingue |
| Examen de la sortie des méthodes | 500–1 500 $ | Mêmes tarifs horaires |

Un corpus complet prend traditionnellement à un locuteur environ 80 heures ; le flux de travail assisté par agent prévu (brouillon de phrase et formatage gérés par les outils, traduction toujours par un humain) est conçu pour ramener cela vers 30–40 heures — moins d'heures de travail répétitif, même tarif horaire, le locuteur ne faisant que les parties qui nécessitent véritablement un humain.

### Valider les métriques

Avant que les scores automatisés ne signifient quelque chose, les locuteurs doivent les vérifier par rapport au jugement humain. Le [Protocole de validation des locuteurs](/docs/specifications/speaker-validation) publie les tâches exactes, les heures et le paiement :

| Tâche | Temps | Paiement par locuteur |
|-------|-------|----------------------|
| A — Évaluer 200 traductions automatiques pour l'adéquation et la fluidité | ~8 heures | 400–520 CAD |
| B — Examiner 50 paires de traductions « équivalentes » | ~2 heures | 100–130 CAD |
| C — Examiner 100 mots que l'analyseur morphologique a rejetés | ~1,5 heures | 75–100 CAD |

Un locuteur effectuant les trois tâches s'engage pour environ 11,5 heures sur deux à quatre semaines pour **575–750 CAD**. Le cycle complet de validation à trois locuteurs coûte au projet 1 475–1 920 $ — c'est le point : la validation des locuteurs est un petit poste budgétaire pour le projet et ne devrait jamais être l'endroit où les coûts sont « économisés ».

### Examiner les réclamations de prix

Aucun prix n'est versé sur la base de scores automatisés seuls. Le [Prix du fondateur](/docs/specifications/prizes) (10 000 CAD, anglais→cri des Plaines) exige qu'au moins deux locuteurs bilingues examinent indépendamment un échantillon stratifié d'au moins 30 résultats, et que 70 % ou plus soient évalués comme « acceptables » ou « excellents ». Cet examen est un travail de locuteur rémunéré selon les mêmes tarifs — et c'est aussi une barrière : les locuteurs peuvent rejeter une réclamation de prix, et c'est intentionnel.

## Comment cela s'adapte aux concours

Le modèle est construit de sorte que la rémunération des locuteurs augmente avec la plateforme au lieu d'être diluée par elle :

- **Chaque nouvelle langue commence par un engagement de corpus rémunéré.** Le coût d'établissement publié par langue (3 350–8 500 $ au total) est principalement une rémunération des locuteurs — le plus grand composant unique, délibérément.
- **Chaque nouveau pool de prix apporte son propre examen rémunéré.** Chaque concours parrainé qui suit le [modèle de prix](/docs/specifications/prizes#4-future-prize-pools) porte la même exigence de validation communautaire, ce qui signifie que chaque concours finance le travail d'examen des locuteurs pour cette langue.
- **Les méthodes déployées financent l'examen continu.** Lorsqu'une méthode appartenant à la communauté génère des revenus d'API, 90 % vont à l'organisation de gouvernance de la communauté ([le modèle économique](/docs/sovereignty/economic-model)), qui peut financer l'examen continu, la croissance du corpus et les programmes linguistiques comme elle le juge bon. Cette allocation est la décision de la communauté, pas la nôtre.

## Ce que nous n'avons *pas* promis

L'honnêteté exige de marquer les limites :

- Les tarifs ci-dessus sont les tarifs publiés pour le travail actuel en cri des Plaines. Les tarifs pour les langues futures seront fixés avec la communauté partenaire et publiés de la même manière — dans les spécifications, avant le début du travail.
- La boucle de rétroaction (revenus → communauté → plus de travail rémunéré) nécessite un financement externe pour démarrer et n'est pas encore autonome. Le [modèle économique](/docs/sovereignty/economic-model) décrit le mécanisme, pas une garantie.
- « Rémunéré équitablement » est nécessaire mais insuffisant. Le paiement ne rend pas un projet non extractif en soi — c'est la propriété et le contrôle qui le font, c'est pourquoi la rémunération s'inscrit dans l'[architecture de souveraineté](/docs/sovereignty/data-sovereignty) plutôt que de la remplacer.

---

## Ce que cela signifie pour vous

:::info Si vous êtes un membre de la communauté
Si vous êtes bilingue dans une langue sous-desservie et l'anglais, votre jugement est l'apport le plus précieux de ce système, et les conditions publiées sont : 50–65 CAD/h, horaires flexibles, paiement dans les deux semaines, crédit selon vos conditions, et le droit de retirer vos contributions. Aucune programmation n'est requise. Commencez par [Pour les communautés linguistiques](/docs/community/for-language-communities) ou le [Protocole de validation des locuteurs §7](/docs/specifications/speaker-validation#7-how-to-get-started).
:::

:::info Si vous êtes un chercheur
Budgétisez la rémunération des locuteurs comme un coût de recherche de première classe — les chiffres publiés (1 475–1 920 $ pour un cycle de validation de métriques ; 2 500–6 000 $ pour la curation du corpus) sont petits selon les normes des subventions et c'est ce qui rend les scores automatisés défendables. La [Stratégie de partenariat de corpus](/docs/specifications/corpus-partnership) montre comment un département universitaire s'intègre à cela avec le travail des locuteurs financé intégré.
:::

:::info Si vous êtes un développeur
Vous bénéficiez du travail des locuteurs rémunérés même si vous ne le financez jamais : les métriques validées sont ce qui rend votre score de classement significatif, et l'examen communautaire rémunéré est ce qui se tient entre votre méthode et un prix. Si vous gagnez, attendez-vous à ce que les locuteurs aient été rémunérés pour examiner attentivement votre résultat — et attendez-vous à ce que la [propriété de votre méthode soit transférée](/docs/sovereignty/ownership-transfer) à la communauté dont elle sert la langue.
:::

## Voir aussi

- [La traduction n'est pas la revitalisation](/docs/perspectives/translation-is-not-revitalization) — pourquoi l'autorité des locuteurs encadre tout le reste
- [Signaler les erreurs et assumer les corrections](/docs/perspectives/reporting-errors-and-owning-corrections) — l'autorité des locuteurs après le benchmark aussi
- [Spécification du benchmark §10](/docs/specifications/benchmark#10-cost-framework) — le cadre de coûts complet d'où proviennent ces chiffres