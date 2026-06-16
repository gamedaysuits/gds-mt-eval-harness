---
sidebar_position: 7
title: "Souveraineté des données"
description: "Principes OCAP, CARE et Māori Data Sovereignty pour la traduction des langues autochtones. Pourquoi le consentement communautaire doit précéder le déploiement."
related:
  - label: "Ownership Transfer"
    to: /docs/sovereignty/ownership-transfer
    kind: doc
    note: "How control of language data moves to communities"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
---
# Souveraineté des données

> **Résumé exécutif.** Cette page explique les principes de souveraineté des données OCAP®, CARE et Te Mana Raraunga et ce qu'ils signifient pour les développeurs créant des méthodes de traduction pour les langues autochtones. Elle couvre les cas où le consentement communautaire est requis, comment l'architecture de la méthode `api` de champollion soutient la souveraineté des données, et les obligations éthiques de toute personne travaillant avec des données linguistiques autochtones.

La traduction automatique pour les langues autochtones soulève des questions qui n'existent pas pour le français ou le japonais. Qui possède les données d'entraînement ? Qui contrôle la façon dont un modèle de langue s'exprime ? Qui décide si une traduction est suffisamment bonne pour être publiée ?

**La réponse est toujours la communauté.**

champollion est construit pour soutenir cela. La méthode `api` conserve toutes les ressources linguistiques côté serveur sous le contrôle de la communauté. Le système de plugins sépare la méthode de l'outil. Mais l'outil ne peut pas imposer l'éthique — cette page explique les principes que vous devriez suivre.

---

## Principes OCAP®

**OCAP** (Ownership, Control, Access, Possession) est un ensemble de principes développés par le [First Nations Information Governance Centre](https://fnigc.ca/ocap-training/) (FNIGC) qui établissent comment les données des Premières Nations doivent être collectées, protégées, utilisées et partagées.

| Principe | Ce que cela signifie pour la traduction |
|-----------|------------------------------|
| **Ownership** | La communauté possède ses données linguistiques — dictionnaires, grammaires, textes parallèles, fichiers d'entraînement et toutes les traductions produites à partir de ceux-ci. |
| **Control** | La communauté contrôle comment ses données linguistiques sont utilisées, qui y a accès et quelles méthodes de traduction sont acceptables. |
| **Access** | Les membres de la communauté ont le droit d'accéder à leurs propres ressources linguistiques et de les gérer, quel que soit l'endroit où elles sont stockées. |
| **Possession** | Les données physiques (fichiers d'entraînement, dictionnaires, poids de modèles) doivent résider sur une infrastructure que la communauté contrôle — pas sur un cloud tiers. |

### Ce que signifie OCAP en pratique

- **Ne publiez pas de traductions** d'une langue autochtone sans autorisation explicite de la communauté.
- **Ne formez pas de modèles** sur des données linguistiques fournies par la communauté sans accord de partage de données.
- **Ne récupérez pas** les ressources linguistiques communautaires à partir de sites web, de médias sociaux ou de matériels éducatifs.
- **Utilisez la méthode `api`** afin que les invites, les données d'entraînement et les dictionnaires restent sur les serveurs contrôlés par la communauté. La méthode `api` de champollion est un « tuyau muet » — elle envoie des clés et reçoit des traductions en retour. Toute la propriété intellectuelle linguistique reste côté serveur.
- **Documentez la provenance** — le champ `provenance` dans le [manifeste du plugin](https://champollion.dev/docs/reference/plugin-spec) doit lister chaque ressource utilisée, sa licence et son origine.

:::warning OCAP® est une marque déposée
OCAP® est une marque déposée du First Nations Information Governance Centre. Elle s'applique spécifiquement aux Premières Nations au Canada. Les principes ont une pertinence plus large, mais la marque et l'autorité de gouvernance appartiennent au FNIGC.
:::

---

## Principes CARE

Les **Principes CARE pour la gouvernance des données autochtones** ont été développés par l'[Alliance mondiale pour les données autochtones](https://www.gida-global.org/care) (GIDA) en complément des principes de données FAIR. FAIR dit que les données doivent être Findable, Accessible, Interoperable et Reusable. CARE dit que ce n'est pas suffisant — la gouvernance des données doit également centrer les droits autochtones.

| Principe | Application |
|-----------|------------|
| **Collective Benefit** | Les outils de traduction doivent d'abord bénéficier à la communauté linguistique. Les scores du classement sont un moyen d'améliorer les méthodes, non d'extraire de la valeur commerciale des langues communautaires. |
| **Authority to Control** | Les communautés ont l'autorité de gouverner comment leurs données linguistiques sont collectées, utilisées et partagées. Un score élevé au classement n'accorde pas la permission de publier des traductions. |
| **Responsibility** | Les chercheurs et développeurs travaillant avec des données linguistiques autochtones ont la responsabilité de construire des relations, d'obtenir le consentement et de partager les bénéfices. |
| **Ethics** | Les droits et le bien-être des peuples autochtones doivent être la préoccupation principale. Les méthodes de traduction doivent être développées *avec* les communautés, non *à propos* d'elles. |

---

## Te Mana Raraunga — Souveraineté des données Māori

**Te Mana Raraunga** est le [Réseau de souveraineté des données Māori](https://www.temanararaunga.maori.nz/). Il affirme que les données Māori — y compris les données linguistiques — sont un taonga (trésor) soumis aux principes du Traité de Waitangi et au tikanga Māori (droit coutumier Māori).

Principes clés :

| Principe | Signification |
|-----------|---------|
| **Rangatiratanga** (Autorité) | Les Māori ont un droit inhérent d'exercer l'autorité sur leurs données, y compris les données linguistiques. |
| **Whakapapa** (Relations) | Les données ont des origines et des connexions. Les données linguistiques portent les relations et les connaissances des personnes qui les ont créées. |
| **Whanaungatanga** (Obligations) | Ceux qui détiennent ou traitent les données Māori ont des obligations réciproques envers les communautés dont elles proviennent. |
| **Kotahitanga** (Bénéfice collectif) | Les données Māori doivent être utilisées pour le bénéfice collectif des Māori. |
| **Manaakitanga** (Réciprocité) | L'utilisation des données Māori doit impliquer le soin, le respect et la réciprocité. |
| **Kaitiakitanga** (Gardiennage) | Les gardiens des données ont le devoir de protéger les données et de s'assurer qu'elles sont utilisées de manière appropriée. |

Ces principes s'appliquent au te reo Māori (la langue Māori) et à tout travail informatique impliquant des données linguistiques Māori.

---

## Ce que cela signifie pour les utilisateurs de champollion

### Pour les langues standard (français, japonais, espagnol...)

Utilisez champollion normalement. Ces langues disposent de grands corpus publiquement disponibles, d'API de traduction établies et n'ont pas de préoccupations en matière de souveraineté. Traduisez, synchronisez et publiez comme vous le souhaitez.

### Pour les langues autochtones et peu dotées en ressources

La situation est fondamentalement différente :

1. **Obtenez d'abord le consentement.** Avant de construire une méthode de traduction pour une langue autochtone, établissez une relation avec la communauté. Une méthode construite sans implication communautaire — aussi impressionnante techniquement soit-elle — ne doit pas être publiée ou distribuée.

2. **Utilisez la méthode `api`.** Hébergez le pipeline de traduction sur une infrastructure contrôlée par la communauté. La méthode `api` dans champollion est conçue pour cela : elle envoie des clés et reçoit des traductions en retour sans exposer les invites, les dictionnaires ou les données d'entraînement qui font fonctionner la méthode.

    ```json title="Community-controlled setup"
    {
      "pairs": {
        "en:crk": {
          "method": "api",
          "endpoint": "https://api.community-server.example/translate"
        }
      }
    }
    ```

3. **Documentez tout.** Utilisez le champ `provenance` dans votre manifeste de plugin pour lister chaque ressource, sa licence et si elle a été fournie avec le consentement de la communauté.

4. **Les scores ne sont pas des licences.** Un score élevé au classement prouve qu'une méthode fonctionne bien techniquement. Cela n'accorde pas la permission de publier des traductions, de distribuer le plugin ou de commercialiser la méthode. La communauté décide.

5. **Partagez la méthode, pas les données.** Si vous développez une technique qui fonctionne bien (par exemple, « LLM contrôlé par FST avec invites entraînées »), partagez l'*architecture* et l'*approche* sur le classement. La communauté conserve le contrôle sur les données linguistiques qui la font fonctionner pour leur langue spécifique.

---

## La méthode `api` et la souveraineté

La méthode `api` [de traduction](https://champollion.dev/docs/guides/translation-methods) existe spécifiquement pour soutenir la souveraineté des données. Voici pourquoi :

| Aspect | Autres méthodes | Méthode `api` |
|--------|--------------|-------------|
| **Où vivent les invites** | Dans les fichiers de configuration de champollion (visibles à tous les développeurs) | Sur le serveur de la communauté (privé) |
| **Où vivent les données d'entraînement** | Dans le répertoire `.champollion/coaching/` (commis à git) | Sur le serveur de la communauté (privé) |
| **Où vivent les dictionnaires** | Dans le répertoire du plugin (distribué avec le plugin) | Sur le serveur de la communauté (privé) |
| **Qui contrôle le pipeline** | Quiconque exécute `champollion sync` | La communauté qui exploite l'API |
| **Ce que champollion voit** | Tout | Clés entrantes, traductions sortantes |

La méthode `api` est un choix architectural délibéré. C'est un « tuyau muet » parce que la propriété intellectuelle — les connaissances linguistiques, les règles de grammaire, les exemples d'entraînement soigneusement sélectionnés — appartient à la communauté, pas à l'outil.

Voir [Serving a Method via API](https://champollion.dev/docs/guides/serving-a-method) pour les détails de mise en œuvre.

---

## Étude de cas : OMT-1600 et souveraineté des données

OMT-1600 de Meta (mars 2026) fournit un exemple concret de pourquoi la souveraineté des données est importante pour les langues autochtones. OMT-1600 a formé des modèles de traduction pour 1 600 langues en utilisant :

- **CC-2000-Web** : Texte monolingue récupéré sur le web à partir de 2 000+ languoïdes — collecté sans consentement communautaire
- **Traductions bibliques** : Textes religieux utilisés comme données d'entraînement parallèles et d'évaluation pour les langues les moins dotées en ressources
- **MeDLEy** : Bitext manuellement sélectionné — mais sans conformité OCAP® ou CARE documentée
- **Données synthétiques rétrotraduites** : ~270 millions de phrases parallèles synthétiques générées par les modèles eux-mêmes

Pour les langues autochtones comme le Cree des Plaines (CRK), cela signifie :

| Principe | Pratique OMT-1600 | Impact |
|-----------|-------------------|--------|
| **Ownership** | Meta possède les modèles et décide comment les publier | La communauté n'a aucune part de propriété dans la façon dont leur langue est modélisée |
| **Control** | Meta contrôle la sélection des données d'entraînement, l'architecture du modèle et le calendrier de publication | La communauté n'a aucune influence sur les données utilisées ou la façon dont la langue est représentée |
| **Access** | Les poids du modèle ne sont actuellement pas disponibles — « non publiés en raison de facteurs indépendants de la volonté des auteurs » | La communauté ne peut pas accéder, inspecter ou modifier le modèle qui parle sa langue |
| **Possession** | Toutes les données et tous les modèles résident sur l'infrastructure de Meta | La communauté ne peut pas héberger, auditer ou supprimer les données utilisées pour former le modèle |

OMT-1600 est une réussite de recherche. C'est aussi un exemple de pratique extractive de données : les données linguistiques ont été collectées sur le web et dans des textes religieux, traitées dans un modèle et publiées sous forme d'article — tout cela sans implication, consentement ou partage des bénéfices de la communauté.

**C'est exactement le modèle que l'architecture de souveraineté de champollion prévient.** La méthode `api` conserve la propriété intellectuelle linguistique sur les serveurs contrôlés par la communauté. Les corpus d'évaluation sont fournis avec le consentement de la communauté et stockés sous la garde des clés communautaires. Les méthodes gagnantes des prix sont transférées à la propriété communautaire. La différence n'est pas technique — elle est éthique et structurelle.

:::note OMT-1600 n'est pas uniquement responsable
Ce modèle — récupération sur le web suivie d'une formation de modèle sans consentement communautaire — est une pratique standard dans la recherche en NLP multilingue massif. OMT-1600 est une étude de cas en raison de son ampleur (1 600 langues) et de sa récence (mars 2026), non parce qu'elle est uniquement extractive. La même critique s'applique à NLLB-200, aux efforts multilingues de Google et à la plupart des recherches en TA à grande échelle.
:::

---

## Lectures complémentaires

- [First Nations Information Governance Centre — OCAP®](https://fnigc.ca/ocap-training/)
- [Global Indigenous Data Alliance — CARE Principles](https://www.gida-global.org/care)
- [Te Mana Raraunga — Māori Data Sovereignty Network](https://www.temanararaunga.maori.nz/)
- [USIDSN — United States Indigenous Data Sovereignty Network](https://usindigenousdata.org/)

---

## Voir aussi

- [Support a Low-Resource Language](/docs/community/low-resource-languages) — le guide technique avec contexte OCAP
- [Translation Methods](https://champollion.dev/docs/guides/translation-methods) — la méthode `api` et comment elle protège la propriété intellectuelle
- [Serving a Method via API](https://champollion.dev/docs/guides/serving-a-method) — héberger un pipeline contrôlé par la communauté
- [Plugin Specification](https://champollion.dev/docs/reference/plugin-spec) — le champ `provenance` pour l'attribution des ressources
- [Cookbook: FST-Gated Pipeline](/docs/tutorials/fst-gated-pipeline) — construire un pipeline qu'une communauté peut auto-héberger