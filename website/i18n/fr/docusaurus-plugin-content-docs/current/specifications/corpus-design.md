---
sidebar_position: 7
title: "Cadre de conception de corpus"
---
# Cadre de Conception de Corpus d'Évaluation

> **Version :** 1.0  
> **Statut :** Brouillon  
> **Objectif :** Une méthodologie systématique pour construire des corpus d'évaluation qui produisent des évaluations de qualité de traduction valides, fiables et linguistiquement significatives. Ceci est la source de vérité pour la façon dont les ensembles de données d'évaluation Champollion sont conçus, construits et maintenus.

---

## 1. Principes de Conception

### 1.1 — Pourquoi pas les Benchmarks Publics ?

Les corpus parallèles publics (FLORES+, Tatoeba, ensembles de test WMT, OPUS) sont disponibles pour le développement et le débogage mais sont **exclus de l'évaluation officielle du classement**. La raison est simple :

**Contamination.** Les LLM de pointe sont entraînés sur d'énormes extractions du web. Tout texte parallèle qui a existé publiquement — en particulier dans des ensembles de données de référence organisés et largement cités — est probablement dans leurs données d'entraînement. Lorsque vous évaluez GPT-4o sur FLORES+ et qu'il obtient 85 chrF++, vous ne pouvez pas distinguer « le modèle est bon pour traduire » de « le modèle a mémorisé ces paires de phrases spécifiques ». Ce n'est pas une préoccupation théorique — [la recherche a démontré](https://arxiv.org/abs/2311.04850) des effets de contamination mesurables sur les benchmarks de traduction automatique.

Pour Champollion, cela importe particulièrement parce que :
- Notre classement compare principalement des méthodes basées sur les LLM
- Notre proposition de valeur est *l'évaluation honnête et rigoureuse*
- Nos utilisateurs cibles (communautés linguistiques) prennent des décisions de déploiement basées sur ces scores

### 1.2 — Exigences Fondamentales

Chaque corpus d'évaluation Champollion doit satisfaire :

| Exigence | Justification |
|----------|---------------|
| **Rédigé par des humains** | Pas de données synthétiques. Tout texte source et toutes les traductions de référence doivent être rédigés par des humains. Les LLM peuvent assister l'alignement et le formatage mais ne doivent jamais générer de contenu. |
| **Non disponible publiquement sous forme parallèle** | Le texte source peut être public ; les traductions de référence peuvent être publiques ; mais l'*appairage* spécifique ne doit pas exister en tant que corpus parallèle téléchargeable. |
| **Provenance tracée** | Chaque entrée doit avoir une origine documentée : document source, traducteur, licence, date. |
| **Linguistiquement informé** | La couverture doit être guidée par des caractéristiques typologiques, pas par un échantillonnage aléatoire. |
| **Stratifié par domaine** | Les entrées doivent couvrir des domaines définis avec une représentation contrôlée. |
| **Échelonné par difficulté** | Les entrées doivent être assignées à des niveaux de difficulté (1–5) basés sur la complexité structurelle. |
| **Contrôlé en version** | Les versions de corpus sont hachées par contenu. Les scores ne sont comparables que dans la même version. |
| **Examinable par la communauté** | Les traductions de référence doivent être examinables par les membres de la communauté linguistique. |

---

## 2. Sélection du Texte Source

### 2.1 — Taxonomie des Domaines

Champollion évalue la traduction pour les **contextes de déploiement pratiques**, pas pour les exercices académiques. La taxonomie des domaines reflète les types de textes réels que les utilisateurs de traduction rencontrent :

| Domaine | Code | Description | Sources Exemples |
|---------|------|-------------|------------------|
| **Interface Logicielle** | `ui` | Étiquettes de boutons, éléments de menu, messages d'erreur, info-bulles, flux d'intégration | Chaînes d'applications open-source, portails de documentation |
| **Officiel/Administratif** | `admin` | Documents gouvernementaux, avis juridiques, formulaires, déclarations de politique | Publications gouvernementales publiques, documents municipaux |
| **Éducatif** | `edu` | Contenu de manuels, matériel de cours, texte instructif | Matériel éducatif publié, guides d'enseignement |
| **Narratif/Littéraire** | `lit` | Histoires, textes culturels, transcriptions d'histoire orale | Livres publiés, archives culturelles (avec permission) |
| **Conversationnel** | `conv` | Dialogue, échanges de type chat, communication écrite informelle | Corpus de dialogue publiés, scénarios, transcriptions d'entretiens |
| **Technique** | `tech` | Documentation API, fichiers README, spécifications techniques | Documentation de projets open-source |
| **Santé/Médical** | `health` | Information médicale destinée aux patients, messages de santé publique | Publications de santé gouvernementales |
| **Actualités/Journalistique** | `news` | Articles d'actualités, communiqués de presse, affaires courantes | Journaux communautaires, médias autochtones |

### 2.2 — Distribution par Domaine

Un corpus d'évaluation standard devrait viser la distribution suivante. Les pourcentages exacts peuvent varier selon la paire de langues en fonction des types de texte les plus pertinents pour la communauté cible :

| Domaine | Cible % | Justification |
|---------|---------|---------------|
| Interface Logicielle | 25% | Contexte de déploiement principal pour les utilisateurs de l'interface de ligne de commande champollion |
| Officiel/Administratif | 15% | Traduction à enjeux élevés avec implications juridiques |
| Éducatif | 15% | Cas d'usage principal pour la revitalisation linguistique |
| Narratif/Littéraire | 10% | Teste la nuance culturelle et le registre littéraire |
| Conversationnel | 10% | Teste le registre informel et les modèles de parole naturelle |
| Technique | 10% | Teste la précision et la cohérence terminologique |
| Santé/Médical | 10% | Enjeux élevés, teste le vocabulaire spécifique au domaine |
| Actualités/Journalistique | 5% | Teste le vocabulaire contemporain et le registre neutre |

### 2.3 — Critères de Sélection des Sources

Lors de la sélection de textes sources pour un nouveau corpus :

1. **Compatibilité de licence.** Le texte source doit être sous une licence qui permet son utilisation dans un corpus d'évaluation. Préférez CC BY, CC BY-SA, ou domaine public. Documentez la licence.

2. **Actualité.** Préférez les textes publiés au cours des 10 dernières années. La langue évolue — en particulier le vocabulaire autour de la technologie, de la gouvernance et de la médecine.

3. **Diversité de registre.** Dans chaque domaine, recherchez des textes à différents niveaux de formalité. Un communiqué de presse gouvernemental (formel) et un message gouvernemental sur les réseaux sociaux (informel) sont tous deux du domaine `admin` mais avec des registres différents.

4. **Pertinence culturelle.** Pour les langues autochtones et minoritaires, priorisez les textes qui importent à la communauté — documents de gestion des terres, matériel éducatif dans la langue, textes de préservation culturelle — plutôt que des textes qui se trouvent simplement exister en parallèle.

5. **Pas de sources traduites par machine.** Si un document « parallèle » a été créé en exécutant l'original via Google Translate puis en post-édition, ce n'est PAS acceptable comme traduction de référence. La référence doit être une traduction humaine indépendante.

---

## 3. Système d'Échelonnement par Difficulté

### 3.1 — Définitions des Niveaux

Chaque entrée est assignée à un niveau de difficulté (1–5) basé sur la complexité structurelle du *texte source*, pas sur la difficulté de traduction (qui varie selon la méthode).

| Niveau | Étiquette | Caractéristiques Structurelles |
|--------|-----------|-------------------------------|
| 1 | **Élémentaire** | Phrases simples. Clause unique. Temps présent. Vocabulaire courant. Pas d'idiomes. Pas de structures imbriquées. |
| 2 | **Intermédiaire** | Phrases composées. Deux clauses jointes par une conjonction. Temps passé/futur. Vocabulaire de domaine. |
| 3 | **Avancé** | Phrases complexes. Clauses subordonnées, clauses relatives. Temps mixtes. Terminologie spécifique au domaine. Voix passive. |
| 4 | **Expert** | Clauses imbriquées multiples. Registre juridique/technique. Structures conditionnelles. Concepts abstraits. Références culturelles. |
| 5 | **Extrême** | Prose dense avec défis multiples simultanés : subordination imbriquée, référence de pronom ambiguë, idiomes culturels, registre mixte, vocabulaire rare. |

### 3.2 — Facteurs de Difficulté Linguistiquement Informés

Au-delà de la complexité structurelle, la difficulté est modulée par la **distance typologique** entre la langue source et la langue cible. Ces facteurs sont tirés des caractéristiques typologiques WALS et des données de classification de la fiche de langue :

| Facteur | Faible Difficulté | Haute Difficulté |
|---------|------------------|------------------|
| **Ordre des mots** | Même ordre de base (p. ex., SVO→SVO) | Ordre de base différent (p. ex., SVO→SOV) |
| **Type morphologique** | Type similaire (p. ex., analytique→analytique) | Type différent (p. ex., analytique→polysynthétique) |
| **Genre grammatical** | Même système ou pas de genre | Source sans genre, cible avec genre complexe |
| **Honorifique/Registre** | Pas de marquage de registre | Cible avec système de registre complexe (p. ex., japonais, coréen) |
| **Écriture** | Même écriture | Écriture différente (translittération requise) |
| **Animacité** | Pas de distinction d'animacité | Cible avec accord basé sur l'animacité (p. ex., cri) |
| **Évidentialité** | Pas d'évidentialité | Cible marquant la source d'information grammaticalement |

### 3.3 — Distribution par Niveau

Un corpus standard devrait avoir approximativement :

| Niveau | Cible % | Justification |
|--------|---------|---------------|
| 1 | 15% | Établit la ligne de base — même les mauvaises méthodes devraient gérer celles-ci |
| 2 | 25% | Traduction pratique de base |
| 3 | 30% | Où les différences de qualité des méthodes deviennent visibles |
| 4 | 20% | Sépare les bonnes méthodes des excellentes |
| 5 | 10% | Test de plafond — très peu de méthodes géreront bien celles-ci |

---

## 4. Qualité de la Traduction de Référence

### 4.1 — Exigences pour les Traducteurs

Les traductions de référence doivent être produites par des humains qui sont :

1. **Locuteurs courants** de la langue cible (L1 ou équivalent)
2. **Alphabétisés** dans les deux langues source et cible
3. **Conscients du domaine** pour le domaine du texte (un traducteur médical pour les textes de santé, etc.)
4. **Indépendants** — le traducteur ne doit pas avoir accès à aucune sortie de traduction automatique pour le même texte pendant la traduction

### 4.2 — Cahier des Charges de Traduction

Chaque traducteur reçoit un cahier des charges qui inclut :

- Le **registre** à utiliser (formel, conversationnel, etc.)
- L'**audience cible** (grand public, spécialistes, enfants, etc.)
- Toute **convention terminologique** spécifique à la communauté linguistique
- Instruction explicite : « Traduisez le sens, pas les mots. Une traduction qui sonne naturelle est plus précieuse qu'une traduction littérale. »

### 4.3 — Assurance Qualité

1. **Traduction double.** Idéalement, chaque entrée a deux traductions de référence indépendantes par des traducteurs différents. Lorsque ce n'est pas possible, priorisez la traduction double pour les niveaux 4–5.

2. **Examen communautaire.** Les traductions de référence doivent être examinées par au moins un locuteur supplémentaire qui n'a pas produit la traduction.

3. **Variantes acceptables.** Pour chaque référence, documentez les variantes acceptables connues (ordre des mots, conventions orthographiques, formes dialectales). Celles-ci alimentent la métrique `equivalent_match_rate`.

### 4.4 — Ce qui Rend une Référence Mauvaise

| Problème | Pourquoi Cela Invalide l'Évaluation |
|---------|-----------------------------------|
| Traduit par machine puis post-édité | La post-édition préserve la structure de la traduction automatique ; pénalise les méthodes qui produisent des traductions plus naturelles |
| Traduit par un apprenant, pas un locuteur courant | La référence peut contenir des erreurs qui pénalisent la sortie de traduction automatique correcte |
| Trop littéral | Les traductions naturelles obtiennent un mauvais score par rapport aux références littérales |
| Interprétation unique valide pour une source ambiguë | Pénalise les interprétations alternatives valides |

---

## 5. Prévention de la Contamination

### 5.1 — Modèle de Menace de Contamination

| Menace | Description | Atténuation |
|--------|-------------|------------|
| **Chevauchement des données d'entraînement** | Les LLM entraînés sur le corpus parallèle | Ne publiez pas le corpus parallèle publiquement |
| **Fuite en few-shot** | L'auteur de la méthode utilise les entrées d'évaluation comme exemples few-shot | Vérification d'empreinte : les entrées dans l'invite sont détectées et signalées |
| **Contamination indirecte** | Le texte source existe dans les données d'entraînement du LLM (monolingue) | Acceptable — le texte source monolingue est attendu. L'*appairage* doit être nouveau. |
| **Contamination par foule** | Les examinateurs communautaires partagent les entrées publiquement | Les conditions de licence interdisent la redistribution du corpus parallèle |

### 5.2 — Niveaux de Secret du Corpus

| Niveau | Visibilité | Utilisation |
|--------|-----------|------------|
| **Ensemble de développement public** | Entièrement public | Développement de méthodes, débogage, tests de régression. Les scores NE SONT PAS publiés au classement. |
| **Ensemble d'évaluation retenu** | Texte source visible, références secrètes | Évaluation officielle du classement. Les méthodes reçoivent le texte source et retournent les traductions ; le scoring se fait côté serveur. Les références ne sont jamais exposées à la méthode. |
| **Ensemble de référence or** | Entièrement secret, contrôlé par la communauté | Évaluation validée par la communauté. Géré par l'organisation de gouvernance. Utilisé pour la vérification du niveau « Validé par la Communauté ». |

### 5.3 — Politique de Rotation

Les corpus d'évaluation doivent être **rotatés** périodiquement :

1. Après qu'un corpus a été utilisé pendant 12 mois, commencez à construire un remplacement
2. Retirez l'ancien corpus au statut « ensemble de développement » (public)
3. Promouvez le nouveau corpus au statut « ensemble d'évaluation retenu »
4. Cela prévient la contamination progressive par l'optimisation itérative par rapport à une cible fixe

---

## 6. Flux de Travail de Construction du Corpus

### 6.1 — Processus Étape par Étape

```
Step 1: Language Pair Selection
    └─ Identify target language, read language card
    └─ Review typological features (WALS), contact influences, scripts
    └─ Identify which difficulty factors apply

Step 2: Source Text Curation
    └─ Identify candidate source documents per domain
    └─ Verify licenses
    └─ Extract candidate sentences/segments
    └─ Classify by domain and preliminary difficulty tier

Step 3: Segment Selection
    └─ Sample segments to match domain distribution (§2.2)
    └─ Sample segments to match difficulty distribution (§3.3)
    └─ Ensure linguistic phenomenon coverage (§6.2)
    └─ Target minimum corpus size (§6.3)

Step 4: Reference Translation
    └─ Assign segments to qualified translators
    └─ Provide translation brief
    └─ Collect translations
    └─ Dual-translate Tier 4–5 entries

Step 5: Quality Assurance
    └─ Community review of references
    └─ Document acceptable variants
    └─ Flag and resolve disagreements

Step 6: Metadata & Packaging
    └─ Assign final difficulty tiers
    └─ Add provenance metadata per entry
    └─ Content-hash the corpus for versioning
    └─ Package as corpus JSON per harness spec

Step 7: Registration
    └─ Register in Supabase datasets table
    └─ Add to ATTRIBUTION.md if new sources used
    └─ Document in arena website
```

### 6.2 — Couverture des Phénomènes Linguistiques

Chaque corpus devrait inclure des entrées qui testent des phénomènes linguistiques spécifiques pertinents pour la paire de langues. Ceux-ci sont tirés des champs `linguisticChallenges` et `contactInfluences` de la fiche de langue :

**Phénomènes universels (toutes les paires de langues) :**
- Résolution de pronom (antécédents ambigus)
- Négation (simple, double, portée)
- Quantificateurs (tous, certains, aucun, la plupart)
- Expressions temporelles (dates relatives, durées)
- Entités nommées (personnes, lieux, organisations)
- Nombres et mesures
- Listes et énumération

**Phénomènes spécifiques à la paire (à partir de la fiche de langue) :**
- Pour les cibles polysynthétiques : morphologie verbale complexe, incorporation
- Pour les cibles genrées : accord de genre, référence neutre/inclusive
- Pour les cibles SOV : verbes en fin de clause, postpositions
- Pour les langues tonales : distinctions de sens dépendantes du ton
- Pour les langues honorifiques : marqueurs de registre, contexte social
- Pour les langues de contact : limites de code-switching, intégration des emprunts

### 6.3 — Taille Minimale du Corpus

La fiabilité statistique nécessite des nombres d'entrées minimums. Ceux-ci sont basés sur les exigences d'intervalle de confiance bootstrap appairé (à partir de `significance.py`) :

| Objectif | Entrées Minimales | Recommandé |
|----------|------------------|-----------|
| Ensemble de développement | 50 | 100–200 |
| Ensemble d'évaluation retenu | 100 | 200–500 |
| Ensemble de référence or | 200 | 500+ |
| Minimum par domaine | 10 | 25+ |
| Minimum par niveau | 10 | 20+ |

**Pourquoi 100 minimum pour l'évaluation ?** Avec moins de ~100 entrées, les tests de signification bootstrap appairé (1 000 rééchantillonnages) ne peuvent pas détecter de manière fiable les différences inférieures à ~5 points chrF++. Avec 200+ entrées, nous pouvons détecter des différences de ~2 points à p<0,05.

---

## 7. Format JSON du Corpus

Chaque entrée de corpus suit la spécification du harnais :

```json
{
  "id": "edtekla-dev-v1-042",
  "source": "The school board will meet on Tuesday to discuss the new curriculum.",
  "reference": "ᑭᓯᑭᓄᐦᐊᒫᑐᐏᓐ ᑲ ᐃᔑ ᐱᒥᐸᔨᐦᑕᐦᒃ ᑭᔅᑭᓄᐦᐊᒫᑐᐏᓇ ᐁ ᐃᔑ ᒫᒥᑐᓀᔨᐦᑕᐦᒃ ᐅᔥᑭ ᑭᔅᑭᓄᐦᐊᒫᑫᐏᓂᔭ ᓂᔓ ᑭᔑᑲᐤ",
  "acceptable_variants": [
    "ᑭᔅᑭᓄᐦᐊᒫᑐᐏᓐ ᓂᔓ ᑭᔑᑲᐤ ᑲ ᐃᔑ ᒫᒥᑐᓀᔨᐦᑕᐦᒃ ᐅᔥᑭ ᑭᔅᑭᓄᐦᐊᒫᑫᐏᓂᔭ"
  ],
  "domain": "edu",
  "difficulty": 3,
  "phenomena": ["temporal_expression", "named_entity", "future_tense"],
  "provenance": {
    "source_doc": "EdTeKLA Module 4, Unit 7",
    "source_license": "CC BY-NC-SA 4.0",
    "translator": "anonymous-speaker-001",
    "translator_qualification": "L1 Plains Cree, certified translator",
    "translation_date": "2025-11-15",
    "reviewer": "anonymous-speaker-002",
    "review_date": "2025-12-01"
  }
}
```

---

## 8. Mesures Anti-Jeu

### 8.1 — Intégrité du Corpus

| Mesure | Implémentation |
|--------|----------------|
| **Hachage de contenu** | Version du corpus = SHA-256 des ID d'entrée triés + références. Toute modification produit une nouvelle version. |
| **Empreinte d'entrée** | Chaque entrée a un ID dérivé du contenu. Si quelqu'un soumet des résultats contre un corpus modifié, l'empreinte ne correspondra pas. |
| **Application du secret** | Pour l'évaluation officielle, les méthodes reçoivent UNIQUEMENT le texte source. Les références ne sont jamais exposées. Le scoring se fait côté serveur. |
| **Calendrier de rotation** | Les corpus tournent annuellement pour prévenir l'optimisation à long terme par rapport à une cible fixe. |

### 8.2 — Intégrité de la Soumission

| Mesure | Implémentation |
|--------|----------------|
| **Empreinte déterministe** | La configuration d'exécution (modèle, température, invite, version du corpus) est hachée. Les configurations identiques produisent des empreintes identiques. |
| **Détection de sélection** | Les soumetteurs doivent divulguer toutes les exécutions, pas seulement la meilleure. Les soumissions multiples avec la même empreinte sont signalées. |
| **Vérification de contamination** | Si les entrées d'évaluation apparaissent verbatim dans l'invite ou les données de coaching de la méthode, la soumission est disqualifiée. |

---

## 9. Corpus Existants

### 9.1 — Ensemble de Développement EDTeKLA v1

| Propriété | Valeur |
|-----------|--------|
| **ID** | `edtekla-dev-v1` |
| **Paire** | EN → CRK (Cri des Plaines, SRO) |
| **Entrées** | 404 (`master_corpus.json` : 62 or + 342 manuel) ; 548 total disponible |
| **Domaines** | Éducatif (100%) |
| **Niveaux** | 1–5 (distribution à déterminer par audit d'entrée) |
| **Licence** | CC BY-NC-SA 4.0 |
| **Statut** | Ensemble de développement (public) |

**Limitations :** Domaine unique (éducatif uniquement). Pas de stratification par domaine. Les assignations de niveau peuvent nécessiter un audit. La petite taille du corpus limite la puissance statistique pour les tests de signification.

### 9.2 — Corpus Prévus

| Corpus | Paire | Statut | Propriétaire |
|--------|-------|--------|-------------|
| Corpus personnalisé EN → TL (Tagalog) | EN → TL | Planifié | Propriétaire du projet |
| Ensemble retenu EN → CRK | EN → CRK | Futur (nécessite un partenaire communautaire) | Organisme de gouvernance communautaire |

---

## 10. Intégration de la Fiche de Langue

Le cadre du corpus s'intègre au système de fiche de langue :

1. **La sélection de domaine** est informée par la fiche `linguisticChallenges` — si une langue a des défis uniques (polysynthèse, ton, animacité), le corpus doit inclure des entrées qui les testent.

2. **L'étalonnage de difficulté** utilise la fiche `classification` — la distance typologique entre les familles source et cible affecte ce qui constitue « difficile ».

3. **La couverture de registre** utilise la fiche `registers` — si une langue a des registres définis (tagalog-formel, taglish-professionnel, taglish-casual), le corpus devrait inclure des entrées à chaque niveau de registre.

4. **Le test d'influence de contact** utilise la fiche `contactInfluences` — pour les langues avec des couches d'emprunt lourdes (Tagalog : espagnol + anglais + arabe), incluez des entrées qui testent si les méthodes gèrent correctement les emprunts par rapport à la sur-traduction.

5. **La gestion des écritures** utilise la fiche `scripts[]` — pour les langues multi-écritures (serbe : cyrillique + latin), incluez des entrées qui testent la sélection correcte de l'écriture.

---

## Références

- **Spécification de Scoring Champollion** — définit toutes les métriques, poids composites, niveaux de qualité
- **Spécification de Benchmark Champollion** — protocole d'évaluation, format du corpus, souveraineté des données
- **WALS** (World Atlas of Language Structures) — base de données des caractéristiques typologiques
- **Glottolog** — source de vérité de classification des langues
- **ISO 639-3** — norme d'identification des langues
- **EdTeKLA** — source du premier corpus d'évaluation

---

*Ce document est une spécification vivante. Mettez-le à jour à mesure que de nouveaux corpus sont construits et que des leçons sont apprises.*