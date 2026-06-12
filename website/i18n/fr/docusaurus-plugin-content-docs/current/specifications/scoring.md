---
sidebar_position: 5
title: "Spécification de notation"
slug: '/specifications/scoring'
related:
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
    note: "When a score difference actually means something"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
    note: "The tool that computes these metrics"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "These scores, live"
---
# Spécification de Notation

> **Résumé exécutif.** Ceci est la source unique de vérité pour toutes les métriques d'évaluation, la notation composite, les niveaux de qualité et l'analyse des coûts dans l'écosystème d'évaluation de la traduction automatique Champollion. Les métriques d'évaluation spécifiques à la langue — validité morphologique FST, classes d'équivalence du linter et validation sémantique déterministe — sont collectivement nommées **LYSS** (Linguistically-informed Yield & Structural Scoring). Chaque métrique calculée par le harnais, chaque poids dans la formule composite et chaque seuil de niveau sont définis ici — et uniquement ici. Le code, la documentation et les schémas de base de données dérivent de ce document. En cas de conflit, ce document fait autorité.
>
> **Portée.** Ce document définit *ce que* nous mesurons et *comment* nous le notons. Il ne définit pas le schéma de la carte d'exécution (voir BENCHMARK_SPEC §3), le protocole d'évaluation (BENCHMARK_SPEC §6) ou les règles du classement (voir la documentation de l'arène). Ces documents font référence à celui-ci pour les définitions des métriques et la logique de notation.
>
> Dernière mise à jour : 2026-06-07

---

## 1. Philosophie de notation

### 1.1 Philosophie de la microévaluation

> *« Si nous nous concentrons uniquement sur ce qui se généralise, nous oublierons inévitablement les cas où cela ne fonctionne pas — et nous perdrons ces langues et toute leur connaissance et sagesse. »*

Ce projet pratique le **développement de microévaluation** : construire des métriques d'évaluation adaptées à des langues spécifiques en utilisant les meilleurs outils linguistiques disponibles — transducteurs à états finis, dictionnaires bilingues, analyseurs morphologiques, règles d'équivalence curées par des linguistes. C'est l'opposé du paradigme dominant en évaluation de la traduction automatique, qui cherche des métriques universelles fonctionnant pour toutes les langues. Les métriques universelles sont précieuses, mais elles sont les plus faibles précisément là où elles sont les plus nécessaires : pour les langues à morphologie complexe, données d'entraînement limitées et sans représentation dans les ensembles d'entraînement des métriques neurales.

Nous ne faisons pas de progrès en traduction automatique pour de nombreuses langues du monde non seulement parce que nous manquons de corpus, mais parce que **nous ne savons même pas à quoi ressemble le progrès** — nous manquons des outils d'évaluation automatisés pour mesurer si un système de traduction s'améliore. LYSS est notre tentative de construire ces outils, langue par langue, en utilisant les ressources linguistiques disponibles.

### 1.2 Les métriques automatisées sont des approximations

Chaque métrique définie ici est calculée par machine. Elles sont utiles pour l'itération rapide, la comparaison systématique et la détection des régressions. Elles ne sont **pas des substituts au jugement humain**. Les niveaux de qualité au §5 sont des étiquettes heuristiques — seul l'examen humain peut confirmer l'utilisabilité réelle.

### 1.3 Conception multi-signaux

Aucune métrique unique ne capture la qualité de la traduction. Une traduction peut avoir un chevauchement chrF++ parfait mais échouer la validation morphologique. Elle peut passer les vérifications FST mais porter le mauvais sens. Elle peut être sémantiquement exacte mais stylistiquement étrangère à la langue cible. Le score composite au §4 agrège plusieurs signaux indépendants, chacun capturant une dimension différente de la qualité.

### 1.4 Extensibilité

Cet inventaire de métriques n'est pas fermé. Les nouvelles langues apportent de nouvelles exigences : précision tonale pour les langues tonales, précision diacritique pour les scripts sémitiques, correction de syllabaire pour le Cree. L'architecture (protocole MetricPlugin, composite pondéré avec renormalisation) est conçue pour que les métriques soient ajoutées sans casser les scores existants. Les métriques spécifiques à la langue (par exemple, le linter et le validateur sémantique du CRK) sont déclarées sur les cartes de langue sous `evalMetrics` et chargées depuis `eval_standards/` — le harnais n'est livré qu'avec des métriques comportementales génériques (changement de code, hallucination, terminologie).

### 1.5 Trois dimensions d'évaluation

Chaque carte d'exécution mesure trois dimensions indépendantes :

```
Quality   — How good is the translation?   (composite score, §4)
Cost      — How much does it cost?          (cost metrics, §6)
Speed     — How fast does it run?           (speed metrics, §7)
```

Ce sont des axes indépendants. Une méthode peut être de haute qualité mais coûteuse, rapide mais inexacte, ou n'importe quelle combinaison. Le classement permet le tri selon n'importe quelle dimension. Le score ajusté au coût (§6.3) est la seule métrique qui combine les dimensions.

### 1.6 Statut de validation

Chaque métrique de cette spécification a un **statut de validation** distinct de son statut d'implémentation (§3). Le statut d'implémentation suit si le code existe. Le statut de validation suit si la métrique a été montrée comme corrélée aux jugements de qualité humains.

| Niveau de validation | Signification | Métriques actuelles |
|----------------------|---------------|-------------------|
| **✅ Validée en externe** | Des études de corrélation humaine publiées existent (WMT, articles académiques) | `chrf_plus_plus`, `bleu`, `comet_score` |
| **⚡ Validée par approximation** | Validée pour les langues à ressources élevées ; non validée pour nos LRL cibles | `comet_score` (validée pour les paires UE, pas pour le CRK) |
| **🔶 Heuristique d'ingénierie** | Conçue à partir de principes linguistiques ou de modes de défaillance observés ; aucune donnée de corrélation humaine | `fst_acceptance_rate`, `equivalent_match_rate`, `semantic_score`, `code_switching_rate`, `hallucination_rate`, `terminology_adherence` |
| **🔲 Non validée** | Pas encore testée sur aucune donnée | `morphological_accuracy`, `orthographic_accuracy`, `consistency_score` |

> **Ce que cela signifie en pratique.** Le score composite (§4) agrège les métriques à tous les niveaux de validation. C'est un choix de conception explicite : nous croyons qu'une heuristique d'ingénierie structurellement fondée (acceptation FST) est plus informative pour les langues polysynthétiques qu'une métrique neurale validée uniquement sur des paires européennes (COMET). Mais nous ne l'avons pas prouvé. Le score composite doit être traité comme une **estimation d'ingénierie**, pas une mesure de qualité validée, jusqu'à ce que des études de corrélation humaine soient complétées pour chaque langue cible.
>
> **Expériences de validation requises** (voir `mt-evaluation-landscape.md` §6 et `speaker-validation.md`) :
> 1. Étude de corrélation avec jugement humain : 200+ paires de phrases notées par 3+ locuteurs bilingues
> 2. Mesure du taux de rejet faux FST sur un corpus représentatif
> 3. Portage en deuxième langue (Sámi du Nord) pour tester la généralisation
> 4. Comparaison directe avec COMET sur les mêmes données


---

## 2. Inventaire des métriques

Les métriques sont organisées en quatre catégories. Chaque métrique a un statut d'implémentation, une échelle et un niveau (par entrée, au niveau du corpus, ou les deux).

### 2.1 Métriques de surface

Les métriques de surface comparent la traduction prédite à la traduction de référence au niveau de la chaîne. Elles ne nécessitent aucun outil linguistique — juste une comparaison de chaînes.

| ID | Métrique | Statut | Échelle | Niveau | Implémentation |
|----|----------|--------|--------|--------|----------------|
| `exact_match_rate` | Correspondance exacte | ✅ Implémentée | 0,0–1,0 | Les deux | Binaire : la sortie prédite == référence ? Taux de corpus = correspondances / total. |
| `equivalent_match_rate` | Correspondance équivalente | ⚡ Partielle | 0,0–1,0 | Les deux | La sortie prédite correspond-elle à une variante acceptée ? Pour CRK : implémentée via le standard d'évaluation CRK `CrkLinterMetric` (dans `eval_standards/crk/`) utilisant des règles de classe de variante déterministes (ordre des mots, orthographique, particule optionnelle, synonyme de lemme, ambiguïté progressive). Chargée automatiquement via la déclaration `evalMetrics` de la carte de langue CRK. L'implémentation générique multilingue nécessite `variants[]` par entrée dans le corpus. |
| `chrf_plus_plus` | chrF++ | ✅ Implémentée | 0–100 | Les deux | Score F de n-gramme de caractères (sacrebleu). Robuste à la variation morphologique. La métrique de surface principale pour les langues agglutinatives/polysynthétiques. Par entrée utilise `sentence_chrf` ; corpus utilise `corpus_chrf`. |
| `bleu` | BLEU | ✅ Implémentée | 0–100 | Corpus | Précision de n-gramme au niveau des mots (sacrebleu). **Exclue du composite** — la notation au niveau des mots pénalise injustement la variation morphologique. Calculée et rapportée pour la compatibilité avec la littérature de traduction automatique. |
| `ter` | Taux d'édition de traduction | ✅ Implémentée | 0–∞ (plus bas est mieux) | Les deux | Distance d'édition minimale entre la sortie prédite et la référence, normalisée par la longueur de la référence (sacrebleu `corpus_ter`). Calculée aux côtés de chrF++ et BLEU. Exclue du composite — corrèle avec chrF++ donc l'inclure doublerait le compte de la similarité de surface. |
| `length_ratio` | Ratio de longueur | ✅ Implémentée | 0–∞ (1,0 est idéal) | Les deux | `len(predicted) / len(reference)` en caractères. Détecte la troncature (<0,5) et l'inflation/hallucination (>2,0). Moyenné sur les entrées au niveau du corpus. |

### 2.2 Métriques structurelles

Les métriques structurelles valident la bonne formation linguistique de la traduction. Elles nécessitent des outils spécifiques à la langue (analyseurs FST, analyseurs morphologiques) et sont les signaux les plus forts pour les langues morphologiquement riches.

| ID | Métrique | Statut | Échelle | Niveau | Implémentation |
|----|----------|--------|--------|--------|----------------|
| `fst_acceptance_rate` | Acceptation FST | ✅ Implémentée | 0,0–1,0 | Les deux | Proportion de mots de sortie acceptés par un transducteur à états finis (GiellaLT). Un mot est « valide » si le FST retourne au moins une analyse morphologique. Disponible pour toute langue avec un analyseur `.hfstol` GiellaLT. |
| `morphological_accuracy` | Précision morphologique | 🔲 Planifiée | 0,0–1,0 | Les deux | Un mot peut être valide FST mais avoir la mauvaise inflexion (bonne racine, mauvais suffixe). Cette métrique compare l'analyse FST du mot prédit par rapport aux traits morphologiques attendus. Nécessite des annotations morphologiques par entrée dans le corpus. |
| `orthographic_accuracy` | Précision orthographique | 🔲 Planifiée | 0,0–1,0 | Les deux | Valide la correction spécifique au script : utilisation de macron/circonflexe SRO pour le Cree, marques diacritiques pour l'Inuktitut, marqueurs de longueur de voyelle pour l'Ojibwe. Ensembles de règles par langue. |

> **Pourquoi les métriques structurelles sont importantes.** OMT-1600 de Meta — le plus grand système de traduction automatique jamais publié (1 600 langues) — évalue avec ChrF++, xCOMET, MetricX et BLASER 3. Aucune de ces métriques ne valide la correction morphologique. ChrF++ mesure le chevauchement de n-grammes de caractères : elle récompense les chaînes qui *ressemblent* à la langue cible. Pour les langues polysynthétiques, cela signifie qu'un mot morphologiquement invalide qui partage de nombreux caractères avec la référence obtient un bon score. Notre métrique d'acceptation FST est un test structurel binaire : le mot est soit une forme valide dans la langue, soit il ne l'est pas. Aucun autre cadre d'évaluation de traduction automatique ne fournit cela à l'échelle.

### 2.3 Métriques sémantiques

Les métriques sémantiques mesurent la préservation du sens en utilisant des plongements ou des modèles appris. Elles capturent les traductions qui sont superficiellement différentes mais sémantiquement équivalentes, et signalent les traductions qui sont superficiellement similaires mais sémantiquement erronées.

| ID | Métrique | Statut | Échelle | Niveau | Implémentation |
|----|----------|--------|--------|--------|----------------|
| `semantic_score` | Similarité sémantique | ⚡ Partielle | 0,0–1,0 | Les deux | CRK : score pondéré par verdict du `CrkSemanticMetric` du standard d'évaluation CRK (dans `eval_standards/crk/`, approximation). Universel : similarité cosinus des plongements de phrases (source + prédit vs source + référence). Modèle TBD — doit supporter les langues à ressources limitées, ce qui exclut la plupart des modèles de plongement centrés sur l'anglais. |
| `comet_score` | COMET | ✅ Implémentée | ~0,0–1,0 | Les deux | Métrique d'évaluation de traduction automatique apprise (Unbabel). Entraînée sur des jugements de qualité humains. **Exclue du composite** — les données d'entraînement sont biaisées vers les langues européennes à ressources élevées ; les scores pour les LRL sont peu fiables. Calculée quand `unbabel-comet` est installé. Rapportée avec un drapeau d'avertissement pour les ressources limitées. Pour 35 langues africaines, le harnais sélectionne automatiquement AfriCOMET (`masakhane/africomet-mtl`) via `resolve_comet_model()`, qui a une meilleure corrélation avec les jugements humains pour ces langues. |

> **Pourquoi COMET est exclu du composite.** COMET est entraîné sur les données d'évaluation humaine WMT, qui sont massivement des paires de langues européennes à ressources élevées. Lorsqu'elle est appliquée au Cree des Plaines ou à d'autres LRL, les représentations internes du modèle n'ont aucune exposition à ces langues — elle extrapole à partir de langues avec des systèmes morphologiques fondamentalement différents. Les scores sont toujours directionnellement utiles (COMET plus élevé ≈ sortie plus fluide en général) mais les valeurs absolues ne sont pas calibrées. Nous rapportons COMET pour la transparence mais ne le laissons pas influencer le score composite jusqu'à ce que nous puissions le valider par rapport aux jugements humains pour chaque langue cible.

> **AfriCOMET pour les langues africaines.** Chaque carte de langue a un champ `metricModelSupport` (voir spécification de carte de langue §9) qui déclare quels modèles COMET spécialisés sont entraînés pour cette langue. Pour 35 langues africaines (yor, hau, ibo, amh, swa, etc.), la carte déclare AfriCOMET (`masakhane/africomet-mtl`) — un modèle COMET affiné sur les jugements humains de traduction automatique en langues africaines par la communauté Masakhane. Le harnais sélectionne automatiquement le modèle recommandé via `resolve_comet_model()` lisant les cartes de langue, mais cela peut être remplacé avec `--comet-model`. L'ajout de nouveaux mappages langue→modèle se fait en enrichissant la carte de langue (pas en éditant le code Python).

### 2.4 Métriques comportementales

Les métriques comportementales détectent les modes de défaillance spécifiques dans la sortie de traduction. Elles ne mesurent pas directement la qualité — elles détectent les problèmes.

| ID | Métrique | Statut | Échelle | Niveau | Implémentation |
|----|----------|--------|--------|--------|----------------|
| `code_switching_rate` | Taux de changement de code | ✅ Implémentée | 0,0–1,0 (plus bas est mieux) | Les deux | Proportion de mots de sortie qui sont dans la langue source (généralement l'anglais). Détectée via l'analyse de script Unicode et/ou une liste de mots de la langue source. Mode de défaillance très courant des LLM : le modèle insère des mots anglais quand il ne connaît pas l'équivalent en langue cible. |
| `hallucination_rate` | Taux d'hallucination | ✅ Implémentée | 0,0–1,0 (plus bas est mieux) | Les deux | Proportion du contenu de sortie qui n'a pas de contenu source correspondant. Détectée via l'alignement des mots ou le chevauchement des plongements multilingues. Capture le modèle générant des traductions plausibles mais fabriquées. |
| `terminology_adherence` | Adhérence à la terminologie | ✅ Implémentée | 0,0–1,0 | Les deux | Pour les méthodes coachées : proportion des termes de terminologie prescrits qui apparaissent dans la sortie. Nécessite les données du dictionnaire de coaching. Mesure si le modèle respecte le vocabulaire fourni par les experts. |
| `consistency_score` | Cohérence entre entrées | 🔲 Planifiée | 0,0–1,0 | Corpus uniquement | Le modèle traduit-il le même terme source de la même manière sur les entrées ? Une faible cohérence suggère que le modèle devine plutôt que d'appliquer des motifs appris. Nécessite des termes répétés sur les entrées du corpus. |

### 2.5 Métriques de conformité

Les métriques de conformité valident que les traductions préservent l'intégrité structurelle — espaces réservés, formatage et conventions typographiques. Ce sont des vérifications de qualité, pas des scores de qualité.

| ID | Métrique | Statut | Échelle | Niveau | Implémentation |
|----|----------|--------|--------|--------|----------------|
| `compliance_index` | Conformité double passage | ✅ Implémentée | 0,0–1,0 | Les deux | Composite pondéré : 60% intégrité des variables (les variables `{placeholder}` sont-elles préservées ?) + 20% conformité des guillemets (caractères de guillemets corrects par carte de langue) + 20% conformité de la casse (pas de fuite de lettres latines pour les langues sans casse). Calculée sur la sortie brute et post-traitée. Via `DoublePassCompliancePlugin`. |
| `repair_effectiveness` | Efficacité de réparation | ✅ Implémentée | 0,0–1,0 | Corpus | Proportion des violations de conformité qui ont été automatiquement réparées par les crochets de post-traduction. Mesure combien la porte de qualité a amélioré la sortie brute. |

> **Pourquoi la conformité n'est pas dans le composite.** Les métriques de conformité mesurent la préservation structurelle (espaces réservés, guillemets), pas la qualité de la traduction. Une traduction peut être parfaite linguistiquement mais échouer la conformité parce qu'elle a supprimé une variable `{name}`. Ce sont des portes de qualité — elles bloquent la mauvaise sortie de l'expédition, mais elles ne classent pas la qualité de la traduction.

---

## 3. Niveaux de statut des métriques

Chaque métrique au §2 se situe dans l'un des quatre niveaux d'implémentation :

| Niveau | Signification | Comportement de la carte d'exécution |
|--------|--------------|-------------------------------------|
| **✅ Implémentée** | Le code existe, testé, produisant des valeurs dans les cartes d'exécution aujourd'hui | Valeur numérique dans la carte d'exécution |
| **⚡ Partielle** | Une approximation spécifique à la langue existe (par exemple, CRK) mais l'implémentation universelle est en attente | Valeur numérique quand l'approximation s'applique, `null` sinon |
| **🔲 Planifiée** | Spécifiée mais pas encore implémentée | `null` dans la carte d'exécution (champ présent, valeur absente) |
| **💡 Proposée** | En discussion, pas encore spécifiée | Pas dans la carte d'exécution |

Une métrique passe de Planifiée → Partielle quand :
1. Une implémentation spécifique à la langue est fusionnée et testée
2. Elle produit des valeurs pour au moins une paire de langues
3. L'implémentation universelle reste en attente (documentée dans cette spécification)

Une métrique passe de Partielle → Implémentée quand :
1. Une implémentation indépendante de la langue est fusionnée et testée
2. Elle produit des valeurs pour n'importe quelle paire de langues sans plugins spécifiques à la langue
3. Ce document est mis à jour pour refléter le statut ✅

Une métrique passe de Planifiée → Implémentée quand :
1. L'implémentation est fusionnée et testée
2. Elle a été validée sur au moins une exécution d'évaluation réelle
3. Ce document est mis à jour avec ses détails d'implémentation

Une métrique passe de Proposée → Planifiée quand :
1. Sa définition, son échelle et sa méthode de calcul sont convenus
2. Elle est ajoutée à ce document avec un statut `🔲 Planned`
3. Un espace réservé nul est ajouté au schéma de la carte d'exécution

---

## 4. Score composite

### 4.1 Formule

Le score composite est une moyenne pondérée de toutes les métriques *disponibles*, renormalisée de sorte que les poids des métriques disponibles somment à 1,0 :

```
composite = Σ (weight_i × value_i)    for all available metrics
             ─────────────────────
             Σ weight_i               (re-normalization denominator)
```

Une métrique est « disponible » si sa valeur dans la carte d'exécution est un nombre (pas `null`). Quand une métrique n'est pas disponible — parce que la langue n'a pas de FST, ou parce qu'une métrique n'est pas encore implémentée — son poids est redistribué proportionnellement sur les métriques restantes.

**Cela signifie que le composite est toujours comparable dans une exécution :** il utilise les métriques disponibles et normalise en conséquence. La comparaison entre exécutions est valide quand les exécutions utilisent le même ensemble de métriques disponibles.

> [!WARNING]
> **Comparabilité entre exécutions.** Lors de la comparaison d'exécutions avec une disponibilité de métriques différente (par exemple, une exécution a des scores FST, une autre non), les scores composites ne sont **pas directement comparables**. Un composite de 0,72 calculé à partir de 5 métriques porte plus d'informations qu'un composite de 0,72 calculé à partir de 2 métriques. Le classement affiche un avertissement quand la couverture des métriques diffère entre les exécutions comparées. Pour une comparaison rigoureuse, utilisez des tests de signification bootstrap appariés (§8.2) sur les métriques partagées uniquement.

### 4.2 Normalisation d'entrée

Avant d'entrer dans la formule composite, toutes les métriques doivent être sur une **échelle 0,0–1,0** où 1,0 = parfait :

| Métrique | Échelle native | Normalisation |
|----------|----------------|---------------|
| `exact_match_rate` | 0,0–1,0 | Aucune (déjà normalisée) |
| `equivalent_match_rate` | 0,0–1,0 | Aucune |
| `fst_acceptance_rate` | 0,0–1,0 | Aucune |
| `morphological_accuracy` | 0,0–1,0 | Aucune |
| `chrf_plus_plus` | 0–100 | **Diviser par 100** |
| `semantic_score` | 0,0–1,0 | Aucune |
| `code_switching_rate` | 0,0–1,0 (plus bas = mieux) | **`1.0 - value`** (inverser : 0% changement de code = 1,0) |
| `hallucination_rate` | 0,0–1,0 (plus bas = mieux) | **`1.0 - value`** (inverser) |
| `terminology_adherence` | 0,0–1,0 | Aucune |

Les métriques exclues du composite (`bleu`, `comet_score`, `ter`, `length_ratio`, `consistency_score`) ne sont pas normalisées à cette fin.

### 4.3 Tableaux de poids

#### Profil A : Langues AVEC couverture FST

Pour les langues qui ont un transducteur à états finis GiellaLT disponible. Les métriques structurelles portent 40% du composite (FST 0,25 + précision morphologique 0,15), reflétant la primauté de la correction morphologique pour les langues polysynthétiques/agglutinatives.

| Métrique | Poids cible | Justification |
|----------|------------|---------------|
| `fst_acceptance_rate` | **0,25** | Poids le plus élevé. Si le FST rejette un mot, ce n'est pas une forme valide dans la langue — indépendamment de ce que disent les autres métriques. Binaire, structurellement fondée. |
| `morphological_accuracy` | **0,15** | Un mot peut être valide FST mais morphologiquement erroné (bonne racine, mauvaise inflexion). Ensemble avec FST, les métriques structurelles portent 40%. |
| `chrf_plus_plus` | **0,15** | Chevauchement de n-grammes de caractères : la meilleure approximation de surface pour les langues polysynthétiques. Gère mieux la morphologie agglutinative que les métriques au niveau des mots. |
| `semantic_score` | **0,15** | Préservation du sens quand la forme de surface diverge. Capture les traductions sémantiquement erronées qui passent les vérifications structurelles. |
| `equivalent_match_rate` | **0,10** | Récompense les variantes acceptables, pas seulement la traduction de référence unique. Important pour les langues avec ordre des mots flexible. |
| `code_switching_rate` | **0,05** | Pénalise la fuite de la langue source. Inversée : 0% changement de code = 1,0. |
| `terminology_adherence` | **0,05** | Récompense les méthodes coachées qui respectent le vocabulaire prescrit. Actif uniquement quand les données de coaching sont présentes. |
| `hallucination_rate` | **0,05** | Pénalise le contenu fabriqué. Inversée : 0% hallucination = 1,0. |
| `exact_match_rate` | **0,05** | Poids le plus bas. Trop strict pour les langues polysynthétiques — plusieurs traductions correctes existent. Conservé comme vérification de plafond. |

> **Total : 1,00.** Quand les métriques ne sont pas disponibles, leurs poids sont redistribués proportionnellement sur les métriques disponibles. Actuellement, `morphological_accuracy` (poids 0,15) est la seule métrique du Profil A non encore calculée — elle nécessite des annotations morphologiques par entrée au standard d'or. Avec cette métrique absente, les 8 métriques restantes (poids total 0,85) sont chacune mises à l'échelle par 1/0,85 ≈ 1,176. Par exemple :
> - FST : 0,25/0,85 = 0,294
> - chrF++ : 0,15/0,85 = 0,176
> - sémantique : 0,15/0,85 = 0,176

#### Profil B : Langues SANS couverture FST

Pour les langues sans outils de validation morphologique. Les métriques sémantiques et de surface portent un poids égal.

| Métrique | Poids cible | Justification |
|----------|------------|---------------|
| `semantic_score` | **0,25** | Sans validation structurelle, la préservation du sens est le signal disponible le plus fort. |
| `chrf_plus_plus` | **0,25** | Sans FST, le chevauchement au niveau des caractères devient la vérification de surface principale. |
| `equivalent_match_rate` | **0,15** | La correspondance des variantes fournit une évaluation de qualité structurée sans nécessiter des outils morphologiques. |
| `exact_match_rate` | **0,10** | Sans FST, la correspondance exacte porte plus de poids comme seule approximation de validation structurelle. |
| `code_switching_rate` | **0,10** | La fuite de la langue source est plus importante quand il n'y a pas de FST pour attraper la mauvaise sortie. |
| `terminology_adherence` | **0,05** | Conformité du vocabulaire coaché. |
| `hallucination_rate` | **0,05** | Détection de contenu fabriqué. |
| `orthographic_accuracy` | **0,05** | La correction spécifique au script comble partiellement le vide laissé par l'absence de FST. |

> **Total : 1,00.** `orthographic_accuracy` (poids 0,05) est planifiée mais pas encore calculée. Avec elle absente, les 7 métriques restantes (poids total 0,95) sont mises à l'échelle par 1/0,95 ≈ 1,053 — un impact négligeable sur le composite.

> **Note sur l'évolution des poids.** Ces poids sont provisoires et seront recalibrés à mesure que les données de validation humaine s'accumulent. L'objectif à long terme est de dériver les poids empiriquement : quelles métriques automatisées prédisent le mieux les jugements de qualité humains pour chaque famille de langues ?

### 4.4 Ajouter une nouvelle métrique au composite

Pour ajouter une nouvelle métrique au composite :

1. **La définir** au §2 avec le statut `🔲 Planned`, incluant l'échelle, le niveau et la méthode de calcul.
2. **L'implémenter** comme MetricPlugin (ou dans `tester.py` pour les métriques principales).
3. **Ajouter un espace réservé nul** dans le bloc des scores de la carte d'exécution.
4. **Lui assigner un poids cible** au §4.3 en ajustant les poids existants vers le bas. Les poids doivent sommer à 1,00.
5. **Mettre à jour BENCHMARK_SPEC.md** §3 si le schéma de la carte d'exécution change.
6. **Mettre à jour `scoring.py`** tableaux de poids (le code doit refléter ce document).
7. **Exécuter un benchmark de validation** pour confirmer que la métrique produit des valeurs sensées sur les données réelles.
8. **Mettre à jour ce document** pour changer le statut de `🔲` à `✅`.

---

## 5. Niveaux de qualité

Ces niveaux sont des étiquettes heuristiques sur les scores composites automatisés. Ils décrivent ce que les scores tendent à signifier en pratique, basés sur l'examen humain des sorties à chaque niveau. **Ce ne sont pas des jugements de qualité validés** — seul l'examen humain peut confirmer l'utilisabilité réelle.

> [!IMPORTANT]
> **Les niveaux automatisés sont provisoires.** Ces étiquettes sont des nominations pour examen, pas des déclarations de qualité. Une méthode atteignant « Déployable » sur les métriques automatisées est une candidate pour l'évaluation communautaire — pas un produit à expédier. Seul l'examen humain par des locuteurs bilingues peut confirmer l'utilisabilité réelle (voir [BENCHMARK_SPEC §7](/docs/specifications/benchmark#7-human-validation)). Aucune méthode ne peut prétendre à Déployable ou supérieur sans examen communautaire confirmant que les locuteurs conviennent que la sortie est utilisable. Les seuils des niveaux peuvent différer selon les langues à mesure que les données de validation humaine s'accumulent.

| Niveau | Plage composite | Ce qu'un locuteur voit généralement |
|--------|-----------------|-----------------------------------|
| **Baseline** | 0,00–0,30 | Sortie LLM brute sans support spécifique à la langue. La morphologie est principalement hallucincée. |
| **Émergent** | 0,30–0,50 | Certains motifs corrects commencent à apparaître. Le coaching aide, mais la sortie n'est pas fiable. |
| **Fonctionnel** | 0,50–0,70 | La sortie est reconnaissable pour un locuteur. Les catégories grammaticales majeures sont généralement correctes. Erreurs morphologiques fréquentes. |
| **Déployable** | 0,70–0,85 | Approprié pour la traduction de brouillon avec examen humain. La plupart de la morphologie est correcte. |
| **Fluide** | 0,85–1,00 | Approchant la traduction humaine compétente. Les erreurs sont rares et mineures. |

Ces niveaux sont provisoires. Ils seront recalibrés à mesure que les données de validation humaine s'accumulent et que nous apprenons où le seuil « un locuteur trouve cela utile » se situe réellement pour chaque langue. Aucune méthode ne peut prétendre à **Déployable** ou supérieur sans examen communautaire confirmant que les locuteurs bilingues conviennent que la sortie est utilisable.

### 5.1 Seuils des niveaux (lisibles par machine)

Pour les implémentations de code, les seuils sont (évalués de haut en bas, première correspondance gagne) :

```
composite >= 0.85  →  "fluent"
composite >= 0.70  →  "deployable"
composite >= 0.50  →  "functional"
composite >= 0.30  →  "emerging"
composite >= 0.00  →  "baseline"
composite is null  →  "unscored"
```

---

## 6. Métriques de coût

Les métriques de coût mesurent l'efficacité financière d'une méthode de traduction. Elles sont rapportées séparément de la qualité — le coût n'influence pas le score composite (sauf dans le classement secondaire ajusté au coût).

### 6.1 Métriques de jetons

| ID | Métrique | Calcul |
|----|----------|--------|
| `prompt_tokens` | Total des jetons d'entrée | Somme de `usage.prompt_tokens` sur tous les appels API |
| `completion_tokens` | Total des jetons de sortie | Somme de `usage.completion_tokens` |
| `reasoning_tokens` | Jetons de chaîne de pensée | Somme de `usage.completion_tokens_details.reasoning_tokens` (0 pour la plupart des modèles) |
| `cached_tokens` | Jetons mis en cache par le fournisseur | Somme de `usage.prompt_tokens_details.cached_tokens` |
| `total_tokens` | Total des jetons consommés | `prompt_tokens + completion_tokens` |
| `tokens_per_entry` | Moyenne de jetons par traduction | ✅ `total_tokens / entry_count` |

### 6.2 Métriques de coût

| ID | Métrique | Calcul | Cas d'usage |
|----|----------|--------|-----------|
| `total_cost_usd` | Coût total de l'exécution | Tarification rapportée par le fournisseur × comptes de jetons | « Combien ce benchmark a-t-il coûté ? » |
| `cost_per_entry_usd` | Coût par entrée du corpus | `total_cost_usd / entry_count` | Comparaison des méthodes sur le même corpus |
| `cost_per_1k_tokens` | Coût par 1 000 jetons | ✅ `total_cost_usd / total_tokens × 1000` | Efficacité universelle des LLM — comparable sur les corpus |
| `cost_per_source_char` | Coût par caractère source | `total_cost_usd / total_source_chars` | Comparable sur les langues avec tokenization différente |

> **Pourquoi plusieurs métriques de coût ?** Une « entrée » varie en longueur — une phrase de 3 mots coûte moins qu'un paragraphe. `cost_per_entry_usd` est utile pour comparer les méthodes sur le *même* corpus (mêmes entrées = mêmes longueurs = comparaison équitable). `cost_per_1k_tokens` est la métrique d'efficacité standard des LLM, comparable *sur* les corpus. `cost_per_source_char` normalise les différences de tokenization — la même phrase peut se tokenizer en différents nombres de jetons selon le vocabulaire du modèle.

### 6.3 Score ajusté au coût

Pour les méthodes utilisant des API payantes, nous calculons un classement secondaire :

```
cost_adjusted = composite / log2(1 + cost_per_entry_usd × 1000)
```

Cela récompense les méthodes qui obtiennent de bons scores efficacement. Il utilise `cost_per_entry_usd` (pas par jeton) parce que le score ajusté au coût est toujours calculé dans un seul benchmark (même corpus), rendant la comparaison par entrée équitable.

Le score ajusté au coût est un **classement secondaire** — le classement principal classe par score composite. Il répond à une question différente : « avec un budget, quelle méthode donne les meilleurs résultats ? »

---

## 7. Métriques de vitesse

Les métriques de vitesse mesurent la latence et le débit d'une méthode de traduction. Comme le coût, la vitesse n'influence pas le score composite.

| ID | Métrique | Calcul | Niveau |
|----|----------|--------|--------|
| `elapsed_seconds` | Durée d'exécution en temps réel | `time_end - time_start` | Exécution |
| `avg_latency_seconds` | Latence moyenne par entrée | `Σ latency_s / n_entries` | Corpus |
| `median_latency_seconds` | Latence médiane par entrée | 50e percentile de `latency_s` | Corpus |
| `p95_latency_seconds` | Latence au 95e percentile | 95e percentile de `latency_s` | Corpus |
| `tokens_per_second` | Débit | `total_tokens / elapsed_seconds` | Exécution |
| `entries_per_minute` | Taux de traduction | `entry_count / (elapsed_seconds / 60)` | Exécution |

---

## 8. Confiance et signification

### 8.1 Intervalles de confiance bootstrap

Toutes les métriques clés supportent les intervalles de confiance bootstrap (méthode des percentiles, n=1000 rééchantillonnages, α=0,05) :

| Métrique | IC rapporté |
|----------|------------|
| `chrf_plus_plus` | ✅ `chrf_ci_lower`, `chrf_ci_upper` |
| `exact_match_rate` | ✅ `exact_match_ci_lower`, `exact_match_ci_upper` |
| `fst_acceptance_rate` | ✅ `fst_ci_lower`, `fst_ci_upper` (calculé uniquement quand les données FST existent) |
| `comet_score` | ✅ `comet_ci_lower`, `comet_ci_upper` (bootstrappé à partir des scores par entrée mis en cache — pas d'inférence neurale redondante) |
| `composite` | ✅ `composite_ci_lower`, `composite_ci_upper` (calculé quand chrF++ et exact_match sont disponibles) |
| IC par niveau | ✅ `confidence_intervals_by_tier` — IC chrF++ et exact_match par niveau de difficulté (Niveau 1-5) |

### 8.2 Tests de signification bootstrap appariés

Pour comparer deux méthodes, le harnais calcule des tests de rééchantillonnage bootstrap appariés :

```
H₀: The two methods perform equally on this corpus.
H₁: One method is significantly better.
```

Si la valeur p < 0,05 et l'intervalle de confiance de la différence exclut zéro, la différence est statistiquement significative au niveau 95%.

---

## 9. Schéma des scores de la carte d'exécution

Cette section définit la structure hiérarchique du bloc `scores` dans une carte d'exécution. Ce schéma est dérivé des métriques définies aux §2–§7 et doit rester synchronisé.

```jsonc
{
  "scores": {
    // §2.1 Surface metrics
    "exact_match_rate":       0.6613,       // 0.0–1.0
    "exact_matches":          41,           // count
    "equivalent_match_rate":  0.7258,       // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "equivalent_matches":     45,           // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "chrf_plus_plus":         80.65,        // 0–100 (sacrebleu native scale)
    "bleu":                   54.78,        // 0–100, NOT in composite
    "ter":                    42.3,         // ✅ implemented, 0–∞ (lower=better)
    "length_ratio":           1.03,         // ✅ implemented, ideal=1.0

    // §2.2 Structural metrics
    "fst_acceptance_rate":    1.0,          // 0.0–1.0
    "fst_accepted":           74,           // count
    "morphological_accuracy": null,         // 🔲 planned
    "orthographic_accuracy":  null,         // 🔲 planned

    // §2.3 Semantic metrics
    "semantic_score":         0.6842,       // ⚡ partial (CRK: eval_standards/crk CrkSemanticMetric)
    "comet_score":            null,         // nullable, NOT in composite
    "comet_model":            "",           // model ID used for COMET

    // §2.4 Behavioral metrics
    "code_switching_rate":    0.03,         // ✅ implemented (lower=better)
    "hallucination_rate":     0.01,         // ✅ implemented (lower=better)
    "terminology_adherence":  null,         // ✅ implemented (null when no glossary)
    "consistency_score":      null,         // 🔲 planned

    // §4 Composite
    "composite":              0.8988,       // 0.0–1.0
    "quality_tier":           "fluent",     // §5 tier label
    "cost_adjusted":          null,         // §6.3 secondary ranking

    // §7 Speed metrics (merged into scores block)
    "tokens_per_second":      4462.5,       // ✅ total_tokens / elapsed
    "entries_per_minute":     82.30,        // ✅ entry_count / (elapsed/60)
    "avg_latency_seconds":    0.234,
    "median_latency_seconds": 0.190,
    "p95_latency_seconds":    0.415,

    // §8.1 Confidence intervals
    "confidence_intervals": {
      "chrf_plus_plus":     { "ci_lower": 78.2, "ci_upper": 83.1 },
      "exact_match_rate":   { "ci_lower": 0.54, "ci_upper": 0.78 },
      "corpus_comet":       { "ci_lower": 0.71, "ci_upper": 0.76 }
    },
    "confidence_intervals_by_tier": {
      "1": { "corpus_chrf": { "ci_lower": 68.1, "ci_upper": 76.5 } },
      "3": { "corpus_chrf": { "ci_lower": 36.2, "ci_upper": 47.0 } }
    },

    // Breakdowns
    "by_difficulty":          {},           // scores grouped by difficulty tier
    "by_provenance":          {},           // scores grouped by entry provenance

    // Counts
    "total":                  62,
    "evaluated":              62,
    "errors":                 0
  },

  "totals": {
    // §6.1 Token metrics
    "prompt_tokens":          13985,
    "completion_tokens":      187822,
    "reasoning_tokens":       175726,
    "cached_tokens":          0,
    // §6.2 Cost metrics
    "total_cost_usd":         1.7114,
    "cost_per_entry_usd":     0.027603,
    "cost_per_source_char":   null          // 🔲 needs source char counting
  }
}
```

> **Historique du schéma.** Les brouillons antérieurs de la spécification proposaient des blocs `cost`, `speed` et `tokens` séparés. Ceux-ci ont été fusionnés dans `scores` et `totals` respectivement pour la simplicité. Les métriques de vitesse (`tokens_per_second`, `entries_per_minute`, latences) vivent dans `scores` ; les comptes de jetons et les chiffres de coût vivent dans `totals`.

### 9.1 Mappage schéma–base de données

Le JSON de la carte d'exécution est stocké en intégralité comme colonne `jsonb` dans Supabase. Les métriques clés sont également dénormalisées dans les colonnes de niveau supérieur pour les performances de tri/filtre :

| Champ de la carte d'exécution | Colonne Supabase | Type | Index |
|------------------------------|-----------------|------|-------|
| `scores.composite` | `composite_score` | `real` | `idx_composite` |
| `scores.quality_tier` | `quality_tier` | `text` | — |
| `scores.chrf_plus_plus` | `chrf_plus_plus` | `real` | `idx_leaderboard` |
| `scores.exact_match_rate` | `exact_match_rate` | `real` | — |
| `scores.fst_acceptance_rate` | `fst_acceptance_rate` | `real` | — |
| `scores.bleu` | `corpus_bleu` | `real` | — |
| `scores.comet_score` | `comet_score` | `real` | — |
| `totals.total_cost_usd` | `total_cost_usd` | `real` | — |
| `totals.cost_per_entry_usd` | `cost_per_entry_usd` | `real` | — |
| `totals.cost_per_source_char` | `cost_per_source_char` | `real` | — |
| `scores.avg_latency_seconds` | `avg_latency_seconds` | `real` | — |
| `model_slug` | `model_slug` | `text` | `idx_model` |
| `condition` | `condition` | `text` | — |
| `dataset.id` | `dataset_id` | `text` | `idx_leaderboard` |
| `dataset.language_pair` | `language_pair` | `text` | — |
| `fingerprint.hash` | `fingerprint_hash` | `text` | `idx_fingerprint` |
| `scores.equivalent_match_rate` | `equivalent_match_rate` | `real` | — |
| `scores.semantic_score` | `semantic_score` | `real` | — |
| `scores.ter` | `ter` | `real` | — |
| `scores.length_ratio` | `length_ratio` | `real` | — |
| `scores.code_switching_rate` | `code_switching_rate` | `real` | — |
| `scores.hallucination_rate` | `hallucination_rate` | `real` | — |
| `scores.terminology_adherence` | `terminology_adherence` | `real` | — |
| `scores.tokens_per_second` | `tokens_per_second` | `real` | — |
| `scores.entries_per_minute` | `entries_per_minute` | `real` | — |
| `elapsed_seconds` | `elapsed_seconds` | `real` | — |
| *(carte complète)* | `run_card` | `jsonb` | — |

Quand de nouvelles métriques sont implémentées, la colonne correspondante doit être ajoutée via une migration numérotée dans `arena/migrations/`.

---

## 10. Synchronisation code–spécification

### 10.1 Source canonique

Ce document (`arena/website/docs/specifications/scoring.md`) est la source canonique pour :
- Les définitions de métriques (§2)
- Les tableaux de poids composite (§4.3)
- Les seuils des niveaux de qualité (§5.1)
- Les formules de métriques de coût (§6.2)
- Le schéma des scores de la carte d'exécution (§9)

### 10.2 Miroir de code

Le fichier `arena/mt_eval_harness/scoring.py` reflète les tableaux de poids et les seuils des niveaux de ce document. C'est l'**implémentation de code** des §4.3 et §5.1. Quand ce document est mis à jour :

1. Mettre à jour `scoring.py` pour correspondre
2. Exécuter `pytest tests/test_scoring_ssot.py` pour valider l'alignement
3. Mettre à jour la FAQ et la documentation du site qui résument les poids

### 10.3 Documents qui font référence à cette spécification

| Document | Ce qu'il référence | Comment rester synchronisé |
|----------|-------------------|---------------------------|
| `arena/website/docs/specifications/benchmark-spec.md` §4–§5 | Formule composite, tableaux de poids, seuils des niveaux | Référence croisée ce document ; ne pas dupliquer les tableaux |
| `website/docs/getting-started/faq.md` | Résumé simplifié des poids | Doit correspondre à §4.3 ; lien vers ce document |
| `arena/website/docs/how-it-works.md` | Seuil Déployable | Doit correspondre à §5 |
| `publish.py` via `scoring.py` | Dicts de poids + fonction de niveau | Test automatisé valide la correspondance |

---

## Appendice A : Métriques NON dans le composite (et pourquoi)

| Métrique | Pourquoi exclue |
|----------|-----------------|
| **BLEU** | La notation au niveau des mots pénalise la variation morphologique dans les langues polysynthétiques. Une différence d'inflexion mineure (sens correct, suffixe légèrement différent) compte comme un manque complet. chrF++ gère cela mieux au niveau des caractères. |
| **COMET** | Entraîné sur les données WMT (paires européennes à ressources élevées). Les scores pour les LRL sont peu fiables — le modèle extrapole à partir de langues avec des systèmes morphologiques différents. Rapporté pour la transparence, pas pour la notation. |
| **TER** | La distance d'édition corrèle avec chrF++ pour la plupart des cas d'usage. Inclure les deux doublerait le compte de la similarité de surface. TER est rapporté pour référence. |
| **Ratio de longueur** | Un diagnostic, pas un signal de qualité. Un ratio de 1,02 et un ratio de 0,98 sont tous deux corrects. Seules les valeurs extrêmes indiquent des problèmes. |
| **Score de cohérence** | Corpus uniquement — pas de valeur par entrée à agréger. Aussi, une certaine incohérence est légitime (même mot anglais → différentes traductions en langue cible selon le contexte). |
| **Index de conformité** | Porte de qualité, pas signal de qualité. Mesure la préservation structurelle (espaces réservés, guillemets), pas la précision de la traduction. |

## Appendice B : LYSS — Implémentations de métriques spécifiques à la langue

Le cadre **LYSS** (Linguistically-informed Yield & Structural Scoring) fournit des métriques spécifiques à la langue qui vont au-delà de la comparaison de chaînes de surface. LYSS a trois composants principaux :

- **LYSS-fst** — Validité morphologique (`fst_acceptance_rate`) : Chaque mot est-il une forme valide dans la langue cible ?
- **LYSS-eq** — Équivalence linguistique (`equivalent_match_rate`) : La sortie est-elle une variante acceptable de la référence ?
- **LYSS-sem** — Validation sémantique (`semantic_score`) : La sortie préserve-t-elle le sens source ?

> **Statut de validation : 🔶 Heuristique d'ingénierie.** Les métriques LYSS n'ont PAS été validées par rapport aux jugements de qualité humains. Elles sont conçues à partir de principes linguistiques (FST, dictionnaires, règles de grammaire construites par des linguistes au ALTLab de l'Université de l'Alberta), mais la corrélation entre les scores LYSS et la qualité réelle de la traduction n'a pas été mesurée. Voir le [Protocole de validation des locuteurs](/docs/specifications/speaker-validation) pour les expériences de validation requises.

| Langue | Plugin | Localisation | Composant LYSS | Clé de métrique | Notes |
|--------|--------|-------------|----------------|-----------------|-------|
| CRK (Cree des Plaines) | `CrkLinterMetric` | `eval_standards/crk/metrics.py` | **LYSS-eq** | `equivalent_match_rate` | Règles de classe de variante déterministes : ordre des mots, orthographique, particule optionnelle, synonyme de lemme, ambiguïté progressive, inclusif/exclusif. Produit par entrée `lint_verdict` (EXACT/EQUIVALENT/MISS/NO_OUTPUT). |
| CRK | `CrkSemanticMetric` | `eval_standards/crk/metrics.py` | **LYSS-sem** | `semantic_score` | Déterministe : extraction de lemme FST + glosses de dictionnaire + chevauchement de mots de contenu spaCy. Produit des verdicts (EXACT_MATCH/VALID/GRAMMAR_ISSUES/PARTIAL/INCOMPLETE/WRONG/NO_OUTPUT). |
| Langues GiellaLT | `GiellaLTFSTMetric` | `plugins/giellalt_fst.py` | **LYSS-fst** | `fst_acceptance_rate` | Générique : fonctionne pour CRK, SME, SMA, SMJ, SMN, SMS, FIN, NOB, IKU — toute langue avec un analyseur `.hfstol`. |

> **Note d'architecture (juin 2026).** Les métriques LYSS spécifiques à la langue sont maintenant déclarées sur la carte de langue sous `evalMetrics` et chargées depuis `eval_standards/<lang>/` par `plugin_discovery.py`. Ce sont des **standards d'évaluation** (arbitre), pas des métriques de plugin de méthode (concurrent). Cela signifie que toute méthode de traduction ciblant le CRK est automatiquement notée par LYSS — aucune configuration spécifique à la méthode nécessaire. `CrkFSTMetric` a été supprimé ; sa fonctionnalité est entièrement couverte par le `GiellaLTFSTMetric` générique.

## Appendice C : Métriques en considération

Ce sont des idées en cours d'évaluation mais pas encore assez spécifiées pour le §2 :

| Idée | Ce qu'elle mesurerait | Bloqueurs |
|------|----------------------|----------|
| Fluidité (perplexité LM) | La sortie est-elle bien formée en prose dans la langue cible ? | Nécessite un LM en langue cible. Aucun bon modèle n'existe pour la plupart des LRL. |
| Correspondance de registre | La traduction correspond-elle au niveau de formalité attendu ? | Nécessite des classificateurs sociolinguistiques. Problème de recherche. |
| Appropriateness culturelle | Les références culturelles sont-elles traitées correctement ? | Ne peut pas être automatisée — nécessite intrinsèquement un examen humain. |
| Cohérence du discours | Les traductions consécutives forment-elles un passage cohérent ? | Nécessite une évaluation au niveau du document, pas au niveau de la phrase. |

---

## Références

Articles académiques, outils et ressources linguistiques cités dans cette spécification.

### Métriques de surface

1. Popović, M. (2017). « chrF++: words helping character n-grams. » *Proceedings of the Second Conference on Machine Translation (WMT 2017)*, pp. 612–618. Copenhague, Danemark.

2. Papineni, K., Roukos, S., Ward, T., & Zhu, W.-J. (2002). « BLEU: a method for automatic evaluation of machine translation. » *Proceedings of the 40th Annual Meeting of the Association for Computational Linguistics (ACL 2002)*, pp. 311–318. Philadelphie, PA.

3. Post, M. (2018). « A Call for Clarity in Reporting BLEU Scores. » *Proceedings of the Third Conference on Machine Translation (WMT 2018)*, pp. 186–191. Belgique, Bruxelles. Implémentation de référence : [sacrebleu](https://github.com/mjpost/sacrebleu).

4. Snover, M., Dorr, B., Schwartz, R., Micciulla, L., & Makhoul, J. (2006). « A Study of Translation Edit Rate with Targeted Human Annotation. » *Proceedings of the 7th Conference of the Association for Machine Translation in the Americas (AMTA 2006)*, pp. 223–231. Cambridge, MA.

### Métriques neurales

5. Rei, R., Stewart, C., Farinha, A. C., & Lavie, A. (2020). « COMET: A Neural Framework for MT Evaluation. » *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP 2020)*, pp. 2685–2702. En ligne.

6. Juraska, J., Finkelstein, M., Deutsch, D., Siddhant, A., Miber, D., & Markl, A. (2023). « MetricX-23: The Google Submission to the WMT 2023 Metrics Shared Task. » *Proceedings of the Eighth Conference on Machine Translation (WMT 2023)*. Singapour.

7. Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2020). « BERTScore: Evaluating Text Generation with BERT. » *Proceedings of the Eighth International Conference on Learning Representations (ICLR 2020)*. Addis-Abeba, Éthiopie.

8. Sellam, T., Das, D., & Parikh, A. (2020). « BLEURT: Learning Robust Metrics for Text Generation. » *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020)*, pp. 7881–7892. En ligne.

### Outils morphologiques et linguistiques

9. Lindén, K., Silfverberg, M., Axelson, E., Hardwick, S., & Pirinen, T. (2011). « HFST—Framework for Compiling and Applying Morphologies. » *Systems and Frameworks for Computational Morphology (SFCM 2011)*, Communications in Computer and Information Science, vol. 100, pp. 67–85. Springer, Berlin, Heidelberg.

10. Sánchez-Cartagena, V. M., & Toral, A. (2024). « MorphEval: Automatic Evaluation of Morphological Capabilities of Machine Translation Systems. » *Machine Translation*, vol. 38, pp. 1–28.

### Classification des erreurs et évaluation diagnostique

11. Popović, M. (2011). « Hjerson: An Open Source Tool for Automatic Error Classification of Machine Translation Output. » *The Prague Bulletin of Mathematical Linguistics*, no. 96, pp. 59–68.

12. Dreyer, M. & Marcu, D. (2012). « HyTER: Meaning-Equivalent Semantics for Translation Evaluation. » *Proceedings of the 2012 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2012)*, pp. 162–171. Montréal, Canada.

13. Reiter, E. & Belz, A. (2009). « An Investigation into the Validity of Some Metrics for Automatically Evaluating Natural Language Generation Systems. » *Computational Linguistics*, vol. 35, no. 4, pp. 529–558. (Travaux connexes sur les métriques d'évaluation basées sur les caractéristiques, incluant FUSE.)

### Détection d'hallucination

14. Raunak, V., Menezes, A., & Junczys-Dowmunt, M. (2021). « The Curious Case of Hallucinations in Neural Machine Translation. » *Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2021)*, pp. 1172–1183. En ligne.

15. Guerreiro, N. M., Voita, E., & Martins, A. F. T. (2023). « Looking for a Needle in a Haystack: A Comprehensive Study of Hallucinations in Neural Machine Translation. » *Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2023)*, pp. 1059–1075. Dubrovnik, Croatie.

### Ressources en langue Cree

16. Wolfart, H. C. (1973). « Plains Cree: A Grammatical Study. » *Transactions of the American Philosophical Society*, vol. 63, no. 5, pp. 1–90.

17. Wolvengrey, A. (2001). *nêhiyawêwin: itwêwina / Cree: Words.* Canadian Plains Research Center, Université de Regina.

### Gouvernance des données

18. First Nations Information Governance Centre. « The First Nations Principles of OCAP®. » [https://fnigc.ca/ocap-training/](https://fnigc.ca/ocap-training/). (OCAP® est une marque déposée du First Nations Information Governance Centre.)

19. Carroll, S. R., Garba, I., Figueroa-Rodríguez, O. L., Holbrook, J., Lovett, R., Materechera, S., Parsons, M., Raseroka, K., Rodriguez-Lonebear, D., Rowe, R., Sara, R., Walker, J. D., Anderson, J., & Hudson, M. (2020). « The CARE Principles for Indigenous Data Governance. » *Data Science Journal*, vol. 19, no. 1, p. 43.