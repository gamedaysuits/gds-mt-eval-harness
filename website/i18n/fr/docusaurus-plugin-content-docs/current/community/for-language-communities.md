---
sidebar_position: 1
title: "Pour les communautés linguistiques"
---
# Pour les communautés linguistiques

> **Résumé exécutif.** Un guide destiné aux locuteurs de langues autochtones et peu dotées en ressources expliquant comment contribuer à l'Arena (traductions de référence, révision de traductions, données d'entraînement) et ce que la communauté reçoit en retour (propriété du code, revenus API, contrôle complet du déploiement). Aucune compétence en programmation requise.

Vous n'avez pas besoin d'être programmeur pour contribuer à l'Arena. Si vous parlez une langue autochtone ou peu dotée en ressources, vous êtes la personne la plus importante de cet écosystème.

---

## Ce que nous attendons de vous

### Traductions de référence

Nous avons besoin de paires de traductions curées pour l'évaluation — l'anglais d'un côté, votre langue de l'autre. Celles-ci deviennent la « clé de correction » par rapport à laquelle toutes les méthodes de traduction sont évaluées.

Vous pouvez les créer à partir de :
- **Matériels pédagogiques** — exercices de manuels, plans de cours, feuilles de travail
- **Documents communautaires** — procès-verbaux de réunions, bulletins d'information, annonces
- **Expressions courantes** — chaînes d'interface utilisateur, étiquettes d'applications, expressions communes
- **Contenu culturel** — histoires, chansons ou descriptions (avec les autorisations appropriées)

Le format est un simple JSON :
```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

### Révision de traductions

Chaque méthode qui prétend produire des traductions fonctionnelles nécessite une validation humaine. Les locuteurs bilingues examinent les résultats et nous disent si l'ordinateur a eu raison — et plus important encore, *pourquoi* il s'est trompé.

### Données d'entraînement

Les règles de grammaire, les entrées de dictionnaire, les modèles morphologiques — ce sont les ressources linguistiques qui font fonctionner les méthodes de traduction. Votre connaissance du fonctionnement de votre langue est irremplaçable par n'importe quel modèle d'IA.

---

## Ce que vous recevez en retour

### Propriété

Lorsqu'une méthode de traduction est construite pour votre langue et validée sur l'Arena, la [propriété est transférée](/docs/sovereignty/ownership-transfer) à l'organisation de gouvernance de votre communauté. Vous possédez le code, les poids du modèle et le déploiement.

### Revenus

Lorsque les développeurs utilisent la méthode de votre langue via l'API champollion, votre communauté reçoit [90 % des revenus API](/docs/sovereignty/economic-model). Les 10 % restants couvrent les frais d'infrastructure.

### Contrôle

Votre organisation de gouvernance contrôle :
- Qui peut accéder à la méthode
- Si elle peut être utilisée commercialement
- Quels termes de tarification s'appliquent
- Quand et comment elle est mise à jour
- Quelles données sont utilisées pour le développement ultérieur

---

## Comment s'impliquer

1. **Nous contacter** — Ouvrez un problème sur le [dépôt Arena](https://github.com/gamedaysuits/arena) ou envoyez un courriel aux responsables
2. **Décrivez votre langue** — À quelle famille appartient-elle ? Combien de locuteurs ? Quels systèmes d'écriture sont utilisés ? Quelles ressources informatiques existent (FST, dictionnaires, corpus) ?
3. **Commencez petit** — Même 50 paires de traductions curées suffisent pour créer un ensemble de données d'évaluation et ouvrir une nouvelle piste de classement
4. **Connectez-nous à la gouvernance** — Qui dans votre communauté a autorité sur les données et technologies linguistiques ? Le modèle de souveraineté de l'Arena nécessite un partenaire de gouvernance

---

## Souveraineté des données

Vos données linguistiques vous appartiennent. L'Arena est construite sur les principes [OCAP®](/docs/sovereignty/data-sovereignty) :

- Nous ne collectons ni ne stockons jamais vos données linguistiques sur nos serveurs
- Les méthodes de traduction utilisent l'architecture `api` — toutes les données d'entraînement, dictionnaires et règles de grammaire restent sur l'infrastructure que vous contrôlez
- Vous décidez qui peut développer des méthodes pour votre langue
- Les scores du classement prouvent qu'une méthode fonctionne ; ils n'accordent pas la permission de la déployer

---

## Voir aussi

- [Souveraineté des données](/docs/sovereignty/data-sovereignty) — le cadre complet OCAP, CARE et Te Mana Raraunga
- [Transfert de propriété](/docs/sovereignty/ownership-transfer) — ce qui se passe quand une méthode gagne
- [Le modèle économique](/docs/sovereignty/economic-model) — comment les scores deviennent des revenus
- [Soutenir une langue peu dotée en ressources](/docs/community/low-resource-languages) — contexte technique pour les chercheurs travaillant aux côtés des communautés