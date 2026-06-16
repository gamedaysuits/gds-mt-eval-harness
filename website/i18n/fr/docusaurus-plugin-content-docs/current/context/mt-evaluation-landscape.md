---
sidebar_position: 3
title: "Mesurer l'incommensurable"
---
# Mesurer l'incommensurable : Le problème de l'évaluation en traduction automatique

**Un examen de la façon dont le domaine mesure la qualité de la traduction, où il échoue, et ce que LYSS (Linguistically-informed Yield & Structural Scoring) offre comme alternative**

---

> *« Les métriques automatiques sont un mensonge commode. Elles nous donnent un nombre, et le nombre nous permet d'écrire un article, et l'article nous permet de revendiquer un progrès. Que le progrès ait réellement eu lieu est une question distincte. »*
> — Adapté d'un sentiment récurrent aux WMT Metrics Shared Tasks

---

## Introduction

La traduction automatique a un problème de mesure.

Le domaine a passé deux décennies à construire des systèmes de plus en plus sophistiqués — des tables de phrases aux mécanismes d'attention aux modèles de langage avec des billions de paramètres — et tout au long de cette trajectoire, il a lutté avec une question apparemment simple : *comment savez-vous si une traduction est bonne ?*

Cette question n'est pas académique. La métrique que vous choisissez détermine quel système « gagne ». Elle détermine ce qui est financé, ce qui est publié, ce qui est déployé, et — pour les langues qui ont le plus besoin de TA — si les traductions d'une communauté sont jugées comme des échecs alors qu'elles sont, en fait, correctes.

L'histoire de l'évaluation en TA est, en miniature, une histoire des valeurs du domaine. La domination de BLEU pendant près de deux décennies révèle une préférence pour la mesure bon marché, rapide et indépendante de la langue par rapport à l'évaluation informée linguistiquement. L'émergence de métriques neurales comme COMET reflète la sophistication croissante du domaine — et sa dépendance continue aux données d'entraînement centrées sur l'anglais. L'absence quasi totale d'évaluation tenant compte de la morphologie reflète un domaine qui, jusqu'à récemment, a été construit par et pour les locuteurs de langues analytiques européennes.

Cet article retrace l'évolution de l'évaluation en TA de BLEU à nos jours, identifie où les approches existantes échouent systématiquement pour les langues morphologiquement complexes et peu dotées en ressources, et examine à quoi pourrait ressembler une alternative fondée linguistiquement. Il accompagne les autres documents de contexte du projet — [*De Pāṇini aux Transformers*](./history-of-language-and-computation.md) (qui retrace l'histoire intellectuelle du langage et du calcul) et le [*Briefing du domaine*](./mt-field-briefing.md) (qui examine le paysage actuel de la TA). Là où ces documents demandent « comment en sommes-nous arrivés là ? » et « qu'existe-t-il ? », celui-ci demande : « comment savons-nous si tout cela fonctionne ? »

---

## Partie 1 : L'ère de la correspondance de chaînes (2002–2015)

### BLEU et la naissance de l'évaluation automatique

L'ère moderne de l'évaluation en TA commence par un seul article : « BLEU: a Method for Automatic Evaluation of Machine Translation » de Kishore Papineni, Salim Roukos, Todd Ward et Wei-Jing Zhu, publié à l'ACL 2002. BLEU (Bilingual Evaluation Understudy) mesure le chevauchement entre les séquences de mots (n-grammes) d'une traduction automatique et une ou plusieurs traductions de référence humaines. Il inclut une pénalité de brièveté pour empêcher les systèmes de tricher avec des résultats courts, et il calcule une moyenne géométrique des précisions de n-grammes aux ordres 1 à 4.

BLEU est devenu la monnaie du domaine pour une raison simple : c'était rapide, bon marché, reproductible et indépendant de la langue. Avant BLEU, l'évaluation d'un système de TA nécessitait une évaluation humaine coûteuse et lente. BLEU offrait un nombre qui pouvait être calculé en millisecondes, comparé entre les articles et utilisé pour classer les systèmes dans les tâches partagées. En quelques années, c'était essentiellement obligatoire — un article sans scores BLEU était impubliable.

Mais BLEU a des défauts profonds et bien documentés que le domaine a passé deux décennies à contourner :

**Pas de compréhension sémantique.** BLEU est une pure correspondance de surface. « The cat sat on the mat » obtient un score de zéro par rapport à une référence de « the feline rested on the rug ». Chaque mot est un synonyme correct ; le sens est identique ; le score est zéro.

**Cécité morphologique.** Pour les langues agglutinantes et polysynthétiques, la correspondance stricte au niveau des mots échoue catastrophiquement. Un verbe Cree correctement conjugué qui diffère d'un morphème de la référence obtient un score de zéro — même si la différence est une particule grammaticalement optionnelle ou un ordre de mots également valide.

**Discrimination faible au niveau des phrases.** BLEU a été conçu comme une métrique au niveau du corpus. Au niveau des phrases, il est bruyant et peu fiable — pourtant il est régulièrement appliqué aux phrases individuelles.

**Biais de référence unique.** BLEU suppose qu'il existe *une* traduction correcte (ou un petit ensemble de références). Pour les langues avec un ordre des mots libre, des vocabulaires riches en synonymes ou des ambiguïtés systématiques (comme le « nous » inclusif/exclusif du Cree), il peut y avoir des dizaines de traductions également correctes, et BLEU pénalise toutes sauf celle qui correspond à la référence.

**Corrélation faible avec le jugement humain.** Les méta-analyses — notamment Reiter (2018, *Computational Linguistics*) — ont montré que la corrélation de BLEU avec les évaluations de qualité humaines est souvent faible, particulièrement pour les systèmes de haute qualité et pour les langues éloignées de l'anglais.

Ces défauts étaient connus presque dès le début. Pourtant BLEU a persisté parce que les alternatives étaient pires — non pas en précision, mais en commodité. Le domaine s'est optimisé pour la métrique qu'il pouvait calculer, pas pour la métrique dont il avait besoin.

### NIST (Doddington, 2002)

La métrique NIST, publiée la même année que BLEU par George Doddington à HLT 2002, a modifié la formule BLEU de deux façons. Premièrement, elle a pondéré les n-grammes par leur **contenu informatif** — les n-grammes rares recevaient un poids plus élevé que les n-grammes courants, sur l'intuition que traduire correctement une phrase inhabituelle est plus informatif que traduire correctement « of the ». Deuxièmement, elle a utilisé une **moyenne arithmétique** au lieu de la moyenne géométrique de BLEU, produisant des scores plus stables qui ne s'effondraient pas à zéro quand un seul ordre de n-gramme n'avait pas de correspondances. NIST a été utilisée de manière extensive dans les programmes d'évaluation DARPA TIDES et NIST OpenMT, mais n'a jamais atteint la domination de BLEU dans la communauté de recherche plus large. Malgré ses améliorations, elle partageait la limitation fondamentale de BLEU : la correspondance de chaînes au niveau de la surface sans concept de sens.

### METEOR (Banerjee & Lavie, 2005)

METEOR (Metric for Evaluation of Translation with Explicit ORdering) était une première tentative de résoudre la rigidité de BLEU. Là où BLEU effectue une correspondance exacte des mots, METEOR a introduit trois innovations :

1. **Racinisation** : Les mots sont réduits à leurs racines avant la comparaison, donnant un crédit partiel pour les variantes morphologiques (par exemple, « running » correspond à « ran » après racinisation).
2. **Correspondance de synonymes** : En utilisant WordNet, METEOR reconnaît que « car » et « automobile » sont le même concept.
3. **Alignement des mots** : Plutôt que de compter les chevauchements de n-grammes, METEOR aligne explicitement les mots entre l'hypothèse et la référence, puis calcule la précision et le rappel avec une pénalité de fragmentation.

METEOR a montré une corrélation systématiquement plus élevée avec les jugements humains que BLEU. Mais il nécessitait des ressources spécifiques à la langue (raciniseurs, bases de données de synonymes) qui limitaient son applicabilité, et il était plus lent à calculer. Pour l'anglais, c'était mieux. Pour les langues peu dotées en ressources, les raciniseurs et les bases de données de synonymes n'existaient simplement pas.

### TER (Snover et al., 2006)

Translation Edit Rate mesure le nombre minimum d'éditions (insertions, suppressions, substitutions et *décalages de phrases*) nécessaires pour transformer l'hypothèse en référence, normalisé par la longueur de la référence. L'opération de décalage de phrase — déplacer une séquence contiguë de mots à une position différente — était une reconnaissance directe que l'ordre des mots n'est pas fixe entre les langues. L'approche de distance d'édition de TER est intuitive (elle mesure « combien de travail un post-éditeur humain devrait-il faire ? ») mais hérite de la même limitation fondamentale : elle compare par rapport à une seule référence et n'a pas de concept de sens.

### chrF et chrF++ (Popović, 2015 ; 2017)

L'innovation métrique la plus importante entre BLEU et l'ère neurale est venue de Maja Popović. **chrF** (character F-score) mesure le chevauchement au niveau des *caractères* plutôt qu'au niveau des mots, en calculant la précision et le rappel des n-grammes de caractères. **chrF++** ajoute les unigrammes et bigrammes au niveau des mots.

Pourquoi cela importe pour les langues morphologiquement riches : la correspondance au niveau des caractères donne un *crédit partiel* pour les morphèmes partagés. Les mots Cree *nikî-nipâw* (« j'ai dormi ») et *kikî-nipâw* (« tu as dormi ») partagent la plupart de leurs n-grammes de caractères malgré le fait qu'ils soient des mots différents. chrF donnerait un crédit substantiel ; BLEU donnerait zéro.

chrF++ est devenu une métrique secondaire standard aux tâches partagées WMT, implémenté dans **sacreBLEU** (Post, 2018), et est largement reconnu comme supérieur à BLEU pour les langues morphologiquement riches. Mais c'est toujours une métrique de correspondance de chaînes — meilleure que BLEU, mais fondamentalement limitée par la même hypothèse que la qualité de la traduction peut être mesurée par le chevauchement de formes de surface.

---

## Partie 2 : La révolution des métriques neurales (2018–Présent)

### L'intuition : Apprendre à évaluer

Les métriques de correspondance de chaînes de la Partie 1 partagent un choix de conception fondamental : ce sont des formules conçues à la main. Quelqu'un a décidé que la précision des n-grammes, le chevauchement des caractères ou la distance d'édition était un bon proxy pour la qualité de la traduction, et ensuite tout le monde a utilisé cette formule pendant une décennie.

La révolution des métriques neurales a commencé par une question différente : *et si nous entraînions un modèle à prédire la qualité de la traduction, de la même manière que nous entraînons les modèles à traduire ?*

### BERTScore (Zhang et al., 2020)

BERTScore, publié à ICLR 2020 par Tianyi Zhang et ses collègues de Cornell et du MIT, a été la première métrique largement adoptée à passer de la correspondance exacte de chaînes à la similarité sémantique. Le mécanisme est élégant : encoder à la fois l'hypothèse et la référence via un modèle Transformer pré-entraîné (BERT, RoBERTa ou DeBERTa), calculer la similarité cosinus entre chaque paire d'embeddings de tokens, puis utiliser une correspondance gourmande pour calculer la précision (meilleure correspondance de chaque token d'hypothèse dans la référence), le rappel (meilleure correspondance de chaque token de référence dans l'hypothèse) et F1.

BERTScore gère naturellement les synonymes, les paraphrases et les variations d'ordre des mots — « the feline rested on the rug » obtient une similarité élevée avec « the cat sat on the mat » parce que les embeddings contextuels capturent l'équivalence sémantique. Avec BERT multilingue, il s'étend à toute langue couverte par le modèle.

Mais BERTScore n'est pas *entraîné* sur les jugements de qualité humains. Il utilise les embeddings pré-entraînés tels quels, ce qui signifie qu'il capture la similarité sémantique générale plutôt que d'apprendre spécifiquement ce qui rend une *traduction* bonne. Cette distinction importe : une phrase peut être sémantiquement similaire à une référence tout en étant une mauvaise traduction (registre incorrect, négation omise, qualificatif hallucié). BERTScore hérite également de tous les biais linguistiques existant dans le modèle sous-jacent — pour les langues sous-représentées dans les données d'entraînement de BERT, les embeddings peuvent ne pas capturer les distinctions significatives.

### BLEURT (Sellam et al., 2020)

BLEURT (Bilingual Evaluation Understudy with Representations from Transformers), publié à l'ACL 2020 par Thibault Sellam, Dipanjan Das et Ankur Parikh de Google, a introduit une innovation clé : **pré-entraînement sur des perturbations synthétiques** avant l'ajustement fin sur les jugements humains. L'intuition était que l'ajustement fin d'un modèle de langage directement sur les petits ensembles de jugements humains WMT produisait une métrique fragile — elle surapprenait les motifs spécifiques dans les données d'entraînement et échouait sur les entrées hors distribution.

La solution de BLEURT était une recette d'entraînement en deux phases. Dans la phase un, des millions de paires de phrases synthétiques ont été générées par des suppressions aléatoires de mots, des insertions, des substitutions et la rétrotraduction. Le modèle a été entraîné à prédire les scores de métriques automatiques existantes (BLEU, ROUGE, BERTScore, entailment) pour ces paires — apprenant des notions générales de similarité textuelle. Dans la phase deux, le modèle pré-entraîné a été ajusté fin sur les évaluations Direct Assessment de WMT. Ce « préchauffage » a considérablement amélioré la robustesse.

BLEURT-20 a étendu l'approche à l'évaluation multilingue en utilisant l'encodeur RemBERT de Google. Mais BLEURT reste basé sur la référence uniquement — il n'utilise pas le texte source, ce qui signifie qu'il ne peut pas détecter les hallucinations qui se produisent pour être fluides, et il dépend entièrement de la qualité de la référence.

### COMET (Rei et al., 2020)

COMET (Crosslingual Optimized Metric for Evaluation of Translation) représente l'état de l'art actuel en évaluation automatique de TA. Développé par Ricardo Rei et ses collègues à **Unbabel**, COMET utilise un encodeur multilingue (XLM-RoBERTa) pour encoder trois entrées — la phrase source, l'hypothèse de TA et la traduction de référence — et prédit un score de qualité entraîné sur les jugements Direct Assessment humains.

COMET a remporté ou s'est classé premier aux WMT Metrics Shared Tasks de 2020 à présent. Sa corrélation avec le jugement humain est substantiellement plus élevée que n'importe quelle métrique de correspondance de chaînes. Elle reconnaît les paraphrases, capture la préservation du sens et gère la variation de synonymes que BLEU manque entièrement.

Mais COMET a une limitation critique pour nos objectifs : elle est entraînée sur les données de jugement humain de WMT, qui sont écrasamment dans les langues européennes. Son encodeur multilingue (XLM-R) a été entraîné sur les données CommonCrawl où le Cree des Plaines, le Sámi du Nord et la plupart des langues autochtones sont essentiellement absents. Pour ces langues, les représentations internes de COMET ne sont pas fiables — elle peut produire des scores, mais ces scores ne sont pas fondés sur une compréhension réelle de la structure de la langue.

### xCOMET (Guerreiro et al., 2024)

xCOMET, publié dans TACL 2024 par Nuno Guerreiro, Ricardo Rei et ses collègues à Unbabel et Instituto Superior Técnico, a étendu COMET d'un évaluateur de boîte noire à un **outil de diagnostic**. L'innovation clé est l'apprentissage multitâche : aux côtés du score de qualité au niveau des phrases, xCOMET effectue un **étiquetage de séquence au niveau des sous-mots** pour identifier les spans d'erreur spécifiques dans la traduction et les classer comme mineures, majeures ou critiques.

Cela comble le fossé entre l'évaluation automatique et l'analyse d'erreurs de style MQM humain. Au lieu de simplement rapporter « cette traduction obtient un score de 0,73 », xCOMET peut pointer vers les mots spécifiques qui sont faux et indiquer la gravité. L'entraînement utilise une approche d'apprentissage par curriculum : d'abord entraîner sur les données Direct Assessment pour la régression au niveau des phrases, puis ajouter les données annotées MQM avec les labels de spans d'erreur pour l'entraînement conjoint.

xCOMET a atteint les performances de pointe au niveau des phrases, au niveau du système et au niveau des spans simultanément. Elle fonctionne en modes basés sur la référence et sans référence. Mais elle nécessite des données annotées MQM — qui sont coûteuses à créer et existent écrasamment pour les paires de langues européennes.

### AfriCOMET (Wang & Adelani, NAACL 2024)

AfriCOMET, publié à NAACL 2024 par Jiayi Wang, David Ifeoluwa Adelani et ses collègues de la communauté Masakhane, est la preuve la plus importante que les métriques neurales *doivent* être adaptées pour les langues peu dotées — elles ne se généralisent pas directement.

L'article a d'abord démontré le problème : COMET standard, entraîné sur les données WMT des langues européennes, a montré une corrélation significativement plus faible avec les jugements humains lorsqu'il a été appliqué à 13 langues africaines (y compris l'amharique, le haoussa, l'igbo, le swahili, le yoruba et le zoulou). La correction nécessitait deux changements. Premièrement, remplacer XLM-R par **AfroXLM-R**, un encodeur multilingue spécifiquement entraîné pour mieux représenter les langues africaines. Deuxièmement, créer **AfriMTE**, un nouvel ensemble de données d'évaluation humaine avec des directives MQM simplifiées conçues pour les annotateurs non experts — parce que trouver des traducteurs professionnels bilingues pour ces langues est difficile.

AfriCOMET a prouvé le concept : une métrique neurale spécifique à une famille de langues peut considérablement surpasser la version générique. Mais elle a également prouvé le coût : quelqu'un devait construire AfroXLM-R, collecter les données de jugement humain pour 13 langues et entraîner un nouveau modèle. Pour le Cree des Plaines, aucun encodeur équivalent, ensemble de données de jugement humain ou métrique adaptée n'existe. Le chemin AfriCOMET nécessiterait de créer tous ces éléments à partir de zéro — un effort de plusieurs années impliquant l'évaluation humaine basée sur la communauté et probablement un encodeur dédié à la famille algonquienne.

### GEMBA : LLM-as-Evaluator (Kocmi & Federmann, 2023)

GEMBA (GPT Estimation Metric Based Assessment), publié à EAMT 2023 par Tom Kocmi et Christian Federmann de Microsoft, a posé une question radicale : et si vous demandiez simplement à GPT-4 si une traduction était bonne ?

L'approche est désarmante de simplicité. **GEMBA-DA** invite le LLM avec la source et l'hypothèse et demande une évaluation de qualité sur une échelle 0–100. **GEMBA-MQM** fournit trois exemples annotés et demande au LLM d'identifier les spans d'erreur spécifiques, de les classer par type et gravité, et de produire un score de style MQM. Aucun entraînement spécifique à la métrique n'est requis.

Les résultats ont été frappants : au niveau du système, GEMBA a atteint une corrélation compétitive ou de pointe avec les jugements humains. Les annotations d'erreur GEMBA-MQM, bien que pas aussi fiables que les annotateurs humains, ont fourni des informations de diagnostic interprétables sans aucun entraînement spécialisé.

Mais GEMBA soulève des préoccupations sérieuses. Elle dépend de modèles propriétaires en source fermée dont le comportement change entre les versions d'API. Les résultats ne sont pas reproductibles au sens strict. C'est coûteux à grande échelle (coûts d'API pour évaluer un ensemble de test WMT complet). Et — de manière critique pour nos objectifs — la connaissance du LLM des langues peu dotées est incertaine. GPT-4 peut ou non comprendre suffisamment bien la morphologie du Cree des Plaines pour évaluer les traductions ; il n'y a aucun moyen de le savoir sans tester, et aucune garantie que le comportement sera cohérent entre les mises à jour de modèles. Kocmi et Federmann eux-mêmes ont conseillé contre l'utilisation de GEMBA pour revendiquer des améliorations dans les articles académiques en raison de la nature de boîte noire de l'évaluation.

### MetricX et la WMT 2024 Metrics Shared Task

**MetricX-24**, développé par Juraj Juraska, Daniel Deutsch, Mara Finkelstein et Markus Freitag de Google, a remporté la WMT 2024 Metrics Shared Task. Construit sur **mT5** (Multilingual T5, un modèle encodeur-décodeur plutôt que l'encodeur uniquement XLM-R utilisé par COMET), MetricX emprunte un chemin architectural différent. Il utilise l'ajustement fin en deux étapes — d'abord sur les données Direct Assessment, puis sur les scores MQM — avec une **augmentation de données synthétiques** extensive ciblant les modes de défaillance connus des métriques (sous-traduction, traductions fluides mais incorrectes, hallucinations).

Le document des résultats de WMT 2024, intitulé **« Are LLMs Breaking MT Metrics? »**, a demandé si les traductions générées par LLM avaient cassé l'écosystème des métriques. La réponse était un non qualifié : les métriques neurales ajustées (MetricX-24, variantes COMET) sont restées efficaces, bien que les métriques basées sur LLM (variantes GEMBA) aient montré une force surprenante au niveau du système. Les conclusions clés :

- Les **métriques conscientes de la source** (utilisant source + référence + hypothèse) ont systématiquement surpassé les métriques basées sur la référence uniquement
- Les **modèles hybrides** qui fonctionnent en modes basés sur la référence et sans référence à partir d'une seule architecture sont la direction émergente
- L'**écart pour les langues peu dotées** persiste : toutes les métriques fonctionnent moins bien sur les langues sous-représentées, et l'écart ne se réduit pas
- Les **métriques entraînées MQM** (utilisant des annotations d'erreur granulaires) surpassent systématiquement les métriques entraînées DA (utilisant des scores scalaires)

Les implications pour l'évaluation des langues peu dotées sont claires : le domaine converge vers les grandes métriques neurales entraînées et conscientes de la source comme l'étalon-or. Ces métriques nécessitent des données d'entraînement substantielles, du calcul et — de manière critique — des données d'évaluation humaine dans la langue cible. Pour les langues sans aucune de ces ressources, le pipeline de métrique de pointe simplement ne s'applique pas.

### Le problème du biais : Métriques neurales et langues peu dotées

La révolution des métriques neurales a été, écrasamment, un phénomène des langues bien dotées. Chaque métrique entraînée dans les sections précédentes a été entraînée sur les données de jugement humain WMT, qui couvrent environ 20 paires de langues — toutes impliquant des langues européennes, le chinois ou le japonais. Les encodeurs sous-jacents (XLM-R, mT5, InfoXLM) ont été entraînés sur les données CommonCrawl où la représentation est proportionnelle à la présence sur le web : l'anglais domine, les langues européennes sont bien couvertes, et la grande majorité des 7 000+ langues du monde sont effectivement absentes.

Pour une langue comme le Cree des Plaines, cela crée une défaillance en cascade :

1. **Pas de données d'entraînement** : Il n'y a pas de jugements humains WMT pour les traductions Cree, donc aucune métrique n'a été entraînée pour les évaluer.
2. **Pas de couverture d'encodeur** : Le vocabulaire d'XLM-R a été construit sur CommonCrawl, où le texte Cree est extrêmement rare. Le tokeniseur sur-segmente les mots Cree en fragments d'octets arbitraires, et les embeddings contextuels pour ces fragments sont mal entraînés.
3. **Pas de validation** : Personne n'a mesuré si COMET, BLEURT ou MetricX produit des scores significatifs pour le Cree. Ils peuvent produire des *nombres*, mais il n'y a aucune preuve que ces nombres corrèlent avec la qualité réelle de la traduction.
4. **Pas de chemin vers l'amélioration** : L'approche AfriCOMET — construire un encodeur spécifique à la famille de langues, collecter les données d'évaluation humaine, entraîner une nouvelle métrique — est un effort de plusieurs années impliquant plusieurs institutions. Pour une communauté linguistique de 27 000 locuteurs, l'infrastructure de recherche pour soutenir cela n'existe actuellement pas.

Le résultat est un paradoxe : les langues qui ont le plus besoin urgent d'évaluation de TA (parce que leurs systèmes de TA sont les plus faibles et ont besoin de l'évaluation la plus soigneuse) sont précisément les langues où les meilleurs outils d'évaluation sont les moins fiables. La réponse du domaine a été de recommander chrF++ comme une alternative « suffisamment bonne » — et c'est mieux que BLEU — mais chrF++ est toujours une métrique de correspondance de chaînes qui ne peut pas détecter l'équivalence, ne peut pas gérer l'ordre libre des mots et n'a pas de concept de validité morphologique.

---

## Partie 3 : Au-delà de l'évaluation — Évaluation diagnostique et linguistique

### La division adéquation/fluidité

Avant l'existence des métriques automatiques, l'évaluation humaine de la TA utilisait un cadre avec deux dimensions : **l'adéquation** (la traduction transmet-elle le sens de la source ?) et la **fluidité** (la traduction est-elle grammaticale et naturelle dans la langue cible ?). Cette distinction, codifiée dans les premières évaluations de TA DARPA et plus tard à NIST, reconnaissait quelque chose que les métriques automatiques passeraient deux décennies à essayer de recapturer : la qualité de la traduction n'est pas unidimensionnelle.

Le cadre adéquation/fluidité est tombé en désuétude quand Direct Assessment (un score scalaire unique) l'a remplacé à WMT. Mais l'intuition sous-jacente reste critique : une traduction peut être fluide mais incorrecte (hallucination), ou peu fluide mais correcte (variante morphologique). Aucun score unique ne capture les deux.

### MQM : L'étalon-or (Lommel et al., 2014 ; Freitag et al., 2021)

**Multidimensional Quality Metrics (MQM)** a remplacé Direct Assessment comme évaluation humaine primaire de WMT à partir de 2021. MQM utilise des traducteurs professionnels qui marquent les spans d'erreur spécifiques, les classent par type (erreur de traduction, omission, ajout, grammaire, terminologie) et gravité (mineur = 1 point, majeur = 5 points, critique = 25 points). Cela produit à la fois un score de qualité et des informations de diagnostic exploitables.

MQM est la chose la plus proche d'une méthodologie d'évaluation « correcte » — elle vous dit non seulement *à quel point* une traduction est mauvaise, mais *ce qui spécifiquement a mal tourné*. Mais elle nécessite des traducteurs professionnels bilingues, qui pour la plupart des langues peu dotées n'existent pas en nombre suffisant pour une évaluation statistiquement fiable.

### MorphEval : Évaluation morphologique contrastive (Burlot & Yvon, 2017)

MorphEval est l'art antérieur le plus direct pour l'évaluation de TA consciente de la morphologie. Introduit par Franck Burlot et François Yvon à WMT 2017 et étendu en 2018, MorphEval évalue la *compétence* morphologique en utilisant des **suites de tests contrastifs**.

**Comment cela fonctionne :** La suite de tests consiste en des paires de phrases dans la langue source qui diffèrent par exactement un contraste morphologique — par exemple, singulier vs. pluriel, présent vs. passé, masculin vs. féminin. Le système de TA traduit les deux phrases. Si le système transmet correctement le contraste dans ses traductions (par exemple, en produisant un cible pluriel quand la source est pluriel et une cible singulier quand la source est singulier), le contraste est marqué comme correct.

**Langues couvertes :** Anglais→Tchèque, Anglais→Letton (v1, WMT 2017) ; étendu à Anglais→Français, Anglais→Allemand, Anglais→Finnois, Turc→Anglais (v2, WMT 2018).

**Conclusions clés :** MorphEval a révélé que même les systèmes de TA neurale les plus performants avaient des défaillances morphologiques systématiques — ils pouvaient produire une sortie fluide tout en se trompant sur le temps, le nombre ou le cas. Ces erreurs étaient invisibles à BLEU et même partiellement invisibles à COMET.

**Disponibilité :** Open source sur GitHub ([franckbrl/morpheval](https://github.com/franckbrl/morpheval), [franckbrl/morpheval_v2](https://github.com/franckbrl/morpheval_v2)).

**Limitations :** MorphEval nécessite des suites de tests contrastifs conçues par langue cible, conçues par des linguistes qui comprennent les contrastes morphologiques de cette langue. Aucune suite de tests n'existe pour aucune langue polysynthétique. La méthodologie teste la *compétence* (le système peut-il gérer ce contraste ?) plutôt que la *validité* (le système a-t-il produit des mots réels ?) ou l'*équivalence* (ces deux traductions différentes sont-elles toutes les deux correctes ?).

### CheckList : Tests comportementaux pour NLP (Ribeiro et al., ACL 2020)

**CheckList**, publié à l'ACL 2020 par Marco Tulio Ribeiro et ses collègues (remportant le meilleur article), a importé une idée de l'ingénierie logicielle dans l'évaluation NLP : les **tests unitaires**. Plutôt que d'évaluer les performances agrégées d'un modèle sur un benchmark, CheckList définit une matrice de **capacités** (vocabulaire, négation, entités nommées, raisonnement temporel, coréférence) croisées avec des **types de tests** :

- **Tests de fonctionnalité minimale (MFT)** : Des cas de test simples et ciblés que tout modèle compétent devrait réussir.
- **Tests d'invariance (INV)** : Des perturbations de l'entrée qui ne *devraient pas* changer la sortie (par exemple, changer un nom ne devrait pas changer le sentiment).
- **Tests d'attente directionnelle (DIR)** : Des perturbations qui *devraient* changer la sortie de manière prévisible.

Checklist a été conçu à l'origine pour l'analyse des sentiments et NLI, mais le paradigme s'applique directement à la TA. On pourrait créer des MFT pour les phénomènes morphologiques (« le système produit-il la forme plurielle correcte ? »), des tests INV pour l'ordre libre des mots (« réordonner les mots Cree change-t-il la traduction anglaise ? »), et des tests DIR pour les caractéristiques morphologiques (« changer la source du passé au présent change-t-il le temps cible ? »).

Le paradigme CheckList est particulièrement pertinent parce qu'il formalise ce que MorphEval fait intuitivement : tester des capacités spécifiques plutôt que de mesurer des scores agrégés. Les classes de variantes de notre linter (WORD_ORDER, ORTHOGRAPHIC, OPTIONAL_PARTICLE, etc.) sont, en effet, des règles d'invariance — elles définissent des perturbations qui ne devraient pas changer le verdict d'évaluation.

### Challenge Sets et évaluation ciblée

Le paradigme plus large des **challenge sets** — des suites de tests conçues ciblant des phénomènes linguistiques spécifiques — est devenu une méthodologie d'évaluation complémentaire établie à WMT depuis environ 2017.

**Isabelle, Cherry & Foster (2017)**, au NRC Canada, ont ouvert la voie avec des suites de tests conçues à la main isolant les divergences structurelles entre les langues — des cas où la traduction littérale est probablement incorrecte. Leur travail de suivi (Isabelle & Kuhn, 2018) a construit 506 phrases françaises ciblant des défis de traduction spécifiques, fournissant des images granulaires des capacités du système.

**LingEval97** (Sennrich, EACL 2017) a créé 97 000 paires de traduction contrastives Anglais→Allemand testant si les modèles NMT attribuent une probabilité plus élevée aux traductions correctes par rapport aux paires avec des erreurs morphosyntaxiques introduites. Une conclusion clé : les modèles au niveau des caractères excellaient à la translittération mais fonctionnaient moins bien à l'accord morphosyntaxique à longue distance.

**ACES** (Amrhein, Moghe & Guillou, 2022–2023) a mis à l'échelle l'approche des challenge sets de manière dramatique : 36 476 exemples couvrant 146 paires de langues testant 68 phénomènes linguistiques distincts. ACES a été utilisé pour méta-évaluer les métriques soumises à la tâche partagée des métriques WMT — testant si les *métriques* pouvaient détecter les contrastes, pas seulement si les *systèmes* pouvaient les produire. Étendu à **SPAN-ACES** avec des annotations de spans d'erreur.

**MT-GenEval** (Currey et al., EMNLP 2022) et **WinoMT** (Stanovsky, Smith & Zettlemoyer, ACL 2019) ciblent spécifiquement la précision du genre. WinoMT est notable parce qu'il utilise explicitement l'**analyse morphologique** sur la langue cible pour vérifier le genre des professions traduites — l'un des rares cas où un analyseur morphologique est utilisé comme partie d'un outil d'évaluation de TA.

**Hjerson** (Popović & Ney, 2011) est un outil open source pour la classification automatique des erreurs de TA qui utilise les **lemmes et les étiquettes POS** pour catégoriser les erreurs en cinq types : morphologique, réordonner, mots manquants, mots supplémentaires et erreurs lexicales. C'est peut-être l'art antérieur le plus proche du nôtre en esprit — il utilise l'analyse linguistique pour fournir des catégories d'erreur de diagnostic plutôt qu'un score unique.

Le fil conducteur : le domaine a reconnu, à plusieurs reprises, que les scores agrégés sont insuffisants. L'évaluation diagnostique fournit la granularité nécessaire pour comprendre *pourquoi* un système échoue. Mais les approches diagnostiques nécessitent une expertise linguistique par langue, et cette expertise est concentrée dans les langues européennes.

### AmericasNLP : Évaluation sur le terrain

La série d'ateliers AmericasNLP (co-localisée avec NAACL), axée sur le NLP pour les langues autochtones des Amériques, fournit le point de comparaison le plus direct pour nos défis d'évaluation.

De 2021 à 2023, la tâche partagée a utilisé **chrF** comme sa métrique d'évaluation primaire — choisie pour sa robustesse dans les paramètres peu dotés en ressources et sa correspondance au niveau des caractères, qui fournit un crédit partiel pour le chevauchement morphologique. Les organisateurs ont reconnu les limitations de chrF mais n'avaient pas de meilleure alternative qui pourrait fonctionner sur les typologies diverses représentées (Quechua, Guaraní, Aymara, Nahuatl, Rarámuri et autres).

En 2025, AmericasNLP a introduit une **Shared Task 3** dédiée spécifiquement au développement de métriques d'évaluation de TA pour les langues autochtones — la première fois que le domaine a explicitement reconnu que les métriques existantes sont inadéquates pour ces langues. La soumission gagnante, **FUSE** (Feature-Union Scorer), a combiné les embeddings de phrases multilingues (LaBSE ajusté fin), la similarité lexicale, la similarité phonétique et la correspondance floue de tokens via la régression Ridge et le Gradient Boosting. FUSE n'utilise pas d'analyseurs morphologiques — l'ingénierie des caractéristiques est indépendante de la langue.

C'est le fossé que notre travail occupe. AmericasNLP a identifié le problème (les métriques standard échouent pour les langues autochtones) et a commencé à développer des alternatives (FUSE). Mais aucune des alternatives n'utilise la connaissance morphologique que les FST fournissent. La communauté AmericasNLP utilise chrF++ parce que c'est la meilleure option générique disponible, tandis que la communauté GiellaLT construit des outils morphologiques sophistiqués qui ne sont jamais branchés sur l'évaluation de TA. Les deux communautés n'ont pas convergé.

---

## Partie 4 : Évaluation sans référence et estimation de la qualité

Certains des signaux d'évaluation les plus importants dans notre harnais ne nécessitent pas du tout de traductions de référence. La vérification de validité FST (« est-ce un mot réel ? ») a besoin seulement de la sortie de TA. Le détecteur d'hallucination a besoin de la source et de l'hypothèse. Le détecteur de code-switching a besoin seulement de l'hypothèse et de la connaissance du script de la langue cible. Comprendre où ces éléments s'inscrivent dans le paysage plus large de l'évaluation sans référence est essentiel pour les positionner correctement.

### Le paradigme d'estimation de la qualité

**L'estimation de la qualité (QE)** est le sous-domaine de l'évaluation de TA concerné par la prédiction de la qualité de la traduction *sans* traductions de référence. C'est une tâche partagée dédiée à WMT depuis 2012, motivée par le besoin pratique d'évaluer la qualité de la TA au moment du déploiement — quand vous traduisez un nouveau texte et n'avez pas de référence humaine pour comparer.

La tâche QE a évolué à travers trois générations. **QE basée sur les caractéristiques** (2012–2016) a extrait des caractéristiques conçues à la main de la source et de l'hypothèse — perplexité du modèle de langage, fréquence des mots, chevauchement de n-grammes avec des données monolingues — et a entraîné des classificateurs à prédire la qualité. **QE neurale** (2017–2021) a remplacé les caractéristiques conçues à la main par des représentations apprises, utilisant généralement des encodeurs bilingues. **QE actuelle** (2022–présent) est dominée par les approches basées sur COMET, particulièrement **CometKiwi**.

### CometKiwi et COMET sans référence

**CometKiwi** (Rei et al., WMT 2022), la variante sans référence de COMET, utilise InfoXLM pour encoder la phrase source et l'hypothèse de TA (sans référence) et prédit un score de qualité. Elle a atteint les résultats de pointe dans les tâches partagées QE de WMT 2022 et 2023.

La conclusion remarquable : CometKiwi sans référence approche la corrélation avec le jugement humain atteinte par COMET basé sur la référence. Cela suggère que, pour les langues bien dotées, le texte source contient presque autant de signal d'évaluation que la traduction de référence. Mais la même mise en garde s'applique : l'encodeur de CometKiwi a une représentation minimale pour les langues peu dotées, donc ses prédictions sans référence pour le Cree ou le Sámi ne sont pas fiables.

C'est là que nos métriques basées sur FST offrent quelque chose de véritablement différent. La vérification de validité FST est un **signal de qualité sans référence déterministe** qui ne nécessite aucun modèle entraîné et aucune donnée de jugement humain. Si le FST dit qu'un mot n'est pas un mot Cree valide, ce mot n'est pas un mot Cree valide — avec la mise en garde des faux rejets pour les emprunts, les néologismes et les noms propres. Ce type de signal de qualité dur et basé sur des règles n'a pas d'équivalent dans l'écosystème QE neuronal.

### Détection d'hallucination en TA

L'hallucination en TA — une sortie fluide complètement sans rapport avec la source — est un mode de défaillance grave, particulièrement dans les paramètres peu dotés en ressources où les modèles ont des données d'entraînement insuffisantes pour apprendre des correspondances source-cible fiables.

L'état de l'art académique en détection d'hallucination utilise plusieurs approches :

- **Détection basée sur les embeddings** : Comparer les embeddings source et hypothèse dans un espace partagé (LASER, LaBSE) et signaler les cas où la similarité est en dessous d'un seuil.
- **Détection basée sur la probabilité** : Utiliser les scores de confiance du modèle de TA lui-même — les hallucinations ont tendance à avoir une probabilité de sortie élevée mais une probabilité conditionnée à la source faible.
- **Perturbation contrastive** : Comparer la sortie de TA pour la source réelle par rapport à la sortie pour une source perturbée ou sans rapport ; si les sorties sont suspecieusement similaires, le modèle ignore la source.
- **LLM-as-judge** : Inviter un LLM à évaluer si la traduction est fidèle à la source.

Notre harnais utilise un **plugin de détection heuristique** qui combine quatre signaux : inflation de longueur (hypothèse beaucoup plus longue que prévu), répétition (phrases répétées), décalage d'entité (entités nommées dans la source manquantes de l'hypothèse) et écho source (hypothèse trop similaire au texte source, suggérant une copie non traduite). C'est au niveau de base par rapport à l'état de l'art académique — cela attrape les hallucinations grossières mais en manquera les subtiles. Sa valeur est comme un **écran bon marché, rapide et interprétable** qui peut signaler les pires défaillances sans nécessiter un GPU ou un appel API.

### Détection de code-switching

Le code-switching en sortie de TA — où le système produit des mots dans la langue source plutôt que de les traduire — est un mode de défaillance distinct de l'hallucination. Il se produit généralement quand le modèle rencontre un mot qu'il ne peut pas traduire et revient à copier la source.

Notre plugin de détection de code-switching utilise l'**analyse de bloc Unicode** (détection de caractères de la langue source dans ce qui devrait être une sortie de langue cible) et les **listes de mots courants** (identification des mots source à haute fréquence qui apparaissent non traduits). Pour le Cree, qui utilise à la fois SRO (basé sur le latin) et les syllabiques, cela nécessite un certain soin — l'anglais et SRO partagent le script latin, donc l'analyse de bloc Unicode seule est insuffisante.

La littérature académique sur la détection de code-switching en TA est clairsemée par rapport à la détection d'hallucination. La plupart des travaux se concentrent sur le code-switching dans le texte *d'entrée* (locuteurs bilingues mélangeant les langues) plutôt que dans le texte de *sortie* (systèmes de TA échouant à traduire). Notre approche heuristique est, à notre connaissance, pas significativement derrière n'importe quel état de l'art publié pour ce problème spécifique.

---

## Partie 5 : Le fossé morphologique

### Ce que les métriques existantes ne peuvent pas voir

C'est l'argument central de cet article, et il nécessite une démonstration concrète.

Considérez la paire de phrases Cree des Plaines :

| | Texte |
|--|------|
| **Source (Anglais)** | « I saw the man » |
| **Référence (Cree)** | *nikî-wâpamâw nâpêw* |
| **Hypothèse A** | *nâpêw nikî-wâpamâw* |
| **Hypothèse B** | *nikî-wâpamikow nâpêsis* |

**L'hypothèse A** est une traduction parfaite — elle a les mêmes mots dans un ordre différent, ce qui est grammatical en Cree (ordre libre des mots). **L'hypothèse B** dit « le garçon a été vu par moi » — mauvaise direction de l'action (*-ikow* est inverse), mauvais référent (*nâpêsis* = « garçon », pas « homme »).

| Métrique | Hypothèse A (correcte) | Hypothèse B (incorrecte) | Peut-elle les distinguer ? |
|--------|----------------------|---------------------|------------------------|
| BLEU | ~30% | ~20% | À peine |
| chrF++ | ~65% | ~55% | Quelque peu |
| COMET | Inconnue (pas de données d'entraînement Cree) | Inconnue | Peu fiable |
| **Acceptation FST** | 100% | 100% | Non (les deux sont du Cree valide) |
| **Linter** | ÉQUIVALENT (WORD_ORDER) | MISS | **Oui** |
| **Validateur sémantique** | VALIDE | INCORRECT | **Oui** |

Le linter et le validateur sémantique réussissent là où BLEU, chrF++ et COMET échouent — non pas parce qu'ils sont des « meilleures métriques » au sens universel, mais parce qu'ils ont accès à la *connaissance linguistique* que les métriques de correspondance de chaînes et neurales n'ont pas. Ils savent que le Cree a un ordre libre des mots. Ils savent que *wâpamêw* et *wâpamikow* sont des lemmes différents avec des structures d'arguments différentes. Ils savent que *nâpêw* et *nâpêsis* sont des mots différents.

Cette connaissance provient du FST (qui encode la grammaire morphologique), du dictionnaire bilingue (qui fournit des glosses anglaises pour chaque lemme) et des classes de variantes définies manuellement (qui codent les règles d'équivalence fondées linguistiquement). Aucune de cette connaissance n'est disponible pour une métrique qui traite la traduction comme une chaîne.

### Pourquoi le domaine n'a pas résolu cela

Le fossé morphologique en évaluation de TA n'est pas un mystère. Le domaine sait qu'il existe. Les raisons pour lesquelles il persiste sont structurelles :

1. **Biais d'échelle.** La communauté d'évaluation de TA s'optimise pour les métriques qui fonctionnent sur toutes les paires de langues WMT. Les métriques basées sur FST fonctionnent pour ~30 langues. COMET fonctionne pour 100+. chrF++ fonctionne pour toutes les langues avec un système d'écriture. La communauté récompense l'universalité par rapport à la précision.

2. **Silos communautaires.** Les personnes qui construisent les FST (linguistes informatiques à UiT Tromsø, NRC Canada, Université de l'Alberta) et les personnes qui construisent les métriques d'évaluation (chercheurs en ML à Google, Unbabel, WMT) assistent à des conférences différentes, publient dans des lieux différents et opèrent sous des structures d'incitation différentes. La pollinisation croisée qui serait nécessaire pour construire des métriques d'évaluation basées sur FST ne s'est pas produite — non pas parce qu'elle a été essayée et a échoué, mais parce que les communautés ne se sont jamais converties.

3. **Anxiété de couverture.** Les FST ont des problèmes de faux rejet connus : les emprunts, les néologismes et les noms propres peuvent être rejetés comme invalides même quand ils sont parfaitement acceptables. Cela rend les chercheurs nerveux à l'idée d'utiliser les FST comme métriques — un faux rejet gonfle le taux d'erreur. La préoccupation est valide mais quantifiable : mesurer le taux de faux rejet sur du texte connu comme bon est simple.

4. **Demande insuffisante.** Très peu de personnes construisent de la TA pour les langues polysynthétiques, et celles qui le font (ALT Lab, NRC, participants AmericasNLP) utilisent généralement chrF++ parce que c'est ce qui existe. Il n'y a pas eu de poussée concertée de la communauté de TA peu dotée pour l'évaluation consciente de la morphologie, en partie parce que la communauté est petite et en partie parce que construire de telles métriques nécessite une expertise à la fois en ingénierie NLP et dans la morphologie de la langue cible spécifique.

5. **L'hypothèse de métrique neurale.** L'hypothèse dominante depuis 2020 a été que les métriques neurales résoudront finalement le problème morphologique par le biais de représentations apprises. Si vous entraînez COMET sur suffisamment de données de langues morphologiquement riches, l'argument va, elle apprendra à gérer la variation morphologique implicitement. Cela peut être vrai pour les langues morphologiquement riches bien dotées (finnois, turc, tchèque). C'est peu probable pour les langues avec une représentation effectivement nulle dans les données d'entraînement.

---

## Partie 6 : LYSS — Une alternative fondée linguistiquement

### Ce que champollion a construit : LYSS (Linguistically-informed Yield & Structural Scoring)

Le harnais d'évaluation du projet champollion implémente un cadre de notation composite appelé **LYSS** qui combine les métriques standard (chrF++, correspondance exacte) avec quatre catégories de métriques informées linguistiquement. Le nom reflète l'accent du cadre : mesurer le *rendement* (combien de sens survit au processus de traduction) par le biais de la *notation structurelle* (vérifications déterministes et fondées linguistiquement plutôt que des embeddings appris).

#### 1. Porte de validité morphologique (Métrique FST GiellaLT)

La métrique la plus simple et la plus largement applicable : alimenter chaque mot de la sortie de TA par l'analyseur morphologique à états finis GiellaLT pour la langue cible. Si le FST peut analyser un mot (retourne au moins une analyse), le mot est morphologiquement valide. Si non, le mot n'existe pas dans la langue cible — c'est soit un mot hallucié, soit une erreur morphologique, soit une faute d'orthographe, soit un emprunt absent du lexique.

**Sortie :** `fst_validity_rate` (0,0–1,0, plus élevé = mieux). Moyenne macro (moyenne des taux par entrée) et moyenne micro (mots valides totaux / mots totaux).

**Dépendances :** `pyhfst` (liaisons Python Helsinki Finite-State Technology), un fichier analyseur `.hfstol` compilé pour la langue cible.

**Extensibilité :** Fonctionne pour toute langue avec un analyseur FST GiellaLT — actuellement ~30+ langues, principalement Sámi, Ouralo et langues autochtones arctiques.

**Relation à l'art antérieur :** MorphEval teste si un système peut gérer des contrastes spécifiques. La métrique FST teste si la sortie du système consiste en des mots réels. Ce sont des compléments : MorphEval teste la compétence, la métrique FST teste la validité.

#### 2. Classes d'équivalence linguistique (Linter CRK)

Le linter aborde ce qui peut être le mode de défaillance le plus insidieux de l'évaluation basée sur la référence : **pénaliser les traductions correctes qui diffèrent de la référence**.

Le linter Cree des Plaines (844 lignes) implémente six **classes de variantes**, chacune codant une règle d'équivalence fondée linguistiquement :

- **WORD_ORDER** : Le Cree a un ordre des mots pragmatiquement libre (Wolfart, 1973 §3.2). *nikî-wâpamâw nâpêw* et *nâpêw nikî-wâpamâw* signifient la même chose. Le linter génère toutes les permutations et vérifie si l'hypothèse correspond à l'une d'elles.
- **ORTHOGRAPHIC** : L'orthographe romane standard a des points de variation connus — circonflexe vs. macron (*â* vs. *ā*), trait d'union des preverbes (*nikî-nipâw* vs. *nikî nipâw* vs. *nikînipâw*). Le linter normalise ceux-ci.
- **OPTIONAL_PARTICLE** : Certaines particules de discours (*mâka*, *êkwa*, *êwako*) peuvent être présentes ou absentes sans changer la proposition centrale. Le linter vérifie si l'hypothèse correspond à la référence après suppression de particule.
- **LEMMA_SYNONYM** : Certains lemmes Cree sont interchangeables dans des contextes spécifiques. Cela utilise une liste de synonymes curée (par exemple, variantes dialectales) et, quand le FST est disponible, vérifie si l'hypothèse et la référence partagent des analyses morphologiques.
- **PROGRESSIVE_AMBIGUITY** : Les formes progressives anglaises (« is walking ») peuvent être traduites en Cree en utilisant différentes constructions. Le linter reconnaît celles-ci comme équivalentes.
- **INCLUSIVE_EXCLUSIVE** : Le Cree distingue le « nous » inclusif (*ki-* préfixe) du « nous » exclusif (*ni-* préfixe) — une distinction que l'anglais réduit à un seul pronom. Le linter reconnaît que l'une ou l'autre forme peut être correcte quand la source anglaise est ambiguë.

Le linter produit trois verdicts : **EXACT** (l'hypothèse correspond à la référence), **EQUIVALENT** (l'hypothèse diffère mais est classée comme une variante valide), ou **MISS** (aucune correspondance trouvée). Au niveau agrégé, il calcule un `equivalent_match_rate` — la proportion de traductions qui sont exactes ou équivalentes.

**Relation à l'art antérieur :** Le parallèle le plus proche est **HyTER** (Dreyer & Marcu, NAACL-HLT 2012), qui code exponentiellement de nombreuses traductions valides comme des réseaux de paraphrase et mesure la distance d'édition à la forme valide la plus proche. Notre linter est conceptuellement similaire — il définit un ensemble de traductions valides pour chaque référence — mais utilise des règles de transformation définies linguistiquement plutôt que des bases de données de paraphrase. HyTER a été conçu pour l'anglais ; personne n'a construit de réseaux de paraphrase pour le Cree. Nos classes de variantes sont, en effet, une approximation compacte et basée sur des règles de ce que HyTER fait avec des graphiques.

Dans le cadre CheckList, nos classes de variantes fonctionnent comme des **tests d'invariance** : des transformations qui ne devraient pas changer le verdict d'évaluation. La différence est que les tests CheckList sont généralement appliqués au *modèle* ; nos règles de variantes sont appliquées à la *métrique*.

#### 3. Validation sémantique déterministe (Métrique sémantique CRK)

Le validateur sémantique (792 lignes) tente quelque chose de plus ambitieux : la **comparaison de sens déterministe** sans embeddings neuraux. Il fonctionne en quatre étapes :

1. **Analyse morphologique** : L'hypothèse et la référence sont passées par l'analyseur FST CRK, qui retourne le lemme et les caractéristiques morphologiques pour chaque mot.
2. **Résolution de glose** : Chaque lemme est recherché dans le dictionnaire Cree–Anglais (Wolvengrey, 2001) pour obtenir les glosses anglaises.
3. **Extraction de mots de contenu** : En utilisant le pipeline anglais de spaCy (`en_core_web_md`), les mots de fonction sont filtrés à la fois des glosses anglaises et du texte source.
4. **Notation de chevauchement** : Le chevauchement de mots de contenu entre les glosses de l'hypothèse et les glosses de la référence détermine le verdict sémantique.

Le validateur produit des verdicts catégoriques : **EXACT_MATCH**, **VALID** (mots différents mais même sens), **GRAMMAR_ISSUES** (lemmes corrects mais problèmes de grammaire au niveau des phrases — accord, animacité, forme verbale), **PARTIAL** (sens partiellement préservé), **INCOMPLETE** (sens partiellement manquant), **WRONG** (sens différent), ou **NO_OUTPUT**.

**Relation à l'art antérieur :** C'est, en effet, une **approximation déterministe du calcul de similarité sémantique de COMET**. Là où COMET utilise des embeddings multilingues appris pour évaluer si deux phrases signifient la même chose, notre validateur utilise une chaîne de recherches déterministes : FST → dictionnaire → spaCy. L'avantage est la transparence (chaque étape est inspectable et déterministe) et l'indépendance des données d'entraînement. L'inconvénient est la fragilité : la qualité de l'évaluation dépend entièrement de la couverture du FST et de la complétude du dictionnaire.

L'approche est conceptuellement liée à **MEANT** (Lo & Wu, 2011 ; Lo, 2017), qui a utilisé l'étiquetage des rôles sémantiques pour évaluer si la structure « qui a fait quoi à qui » a été préservée dans la traduction. Notre approche est plus grossière (chevauchement de mots de contenu plutôt que rôles sémantiques) mais fonctionne sur une langue où aucun outil SRL n'existe.

#### 4. Plugins de détection comportementale (Hallucination, Code-Switching, Terminologie)

Trois plugins supplémentaires fournissent des **signaux de qualité comportementale** qui complètent les métriques morphologiques :

- **Détection d'hallucination** (259 lignes) : Quatre signaux heuristiques pondérés et combinés — inflation de longueur (40%), répétition (30%), décalage d'entité (20%), écho source (10%). Ce sont des écrans bon marché et rapides qui attrapent la fabrication grossière.
- **Détection de code-switching** (~280 lignes) : Analyse de bloc Unicode plus listes de mots courants pour détecter les tokens de langue source non traduits. Produit un `code_switching_rate` (0,0–1,0).
- **Adhérence à la terminologie** (199 lignes) : Vérifie si les termes de glossaire spécifiés sont traduits de manière cohérente. Retourne `terminology_adherence` (0,0–1,0) ou None si aucun glossaire n'est configuré.

Ces plugins sont honnêtement positionnés comme des **détecteurs heuristiques de base**, pas l'état de l'art. Leur valeur est de fournir des signaux bon marché, rapides et interprétables qui peuvent être calculés aux côtés des métriques morphologiques plus sophistiquées. Dans le cadre de notation composite, ils portent des poids faibles (0,05 chacun).

### Limitations honnêtes

Cette approche a des limitations significatives qui doivent être reconnues avant toute revendication de nouveauté ou d'utilité :

1. **Taux de faux rejet FST.** Le FST rejettera les mots valides qui ne sont pas dans son lexique — emprunts, néologismes, noms propres, termes de code-switching. Cela gonfle le taux d'erreur morphologique. Le taux de faux rejet n'a pas été formellement mesuré sur un corpus représentatif de texte Cree. Sans cette mesure, la précision de la métrique de validité FST est inconnue.

2. **Couverture du dictionnaire.** La qualité du validateur sémantique dépend entièrement de la couverture du dictionnaire Wolvengrey. Les mots Cree absents du dictionnaire ne produisent pas de glosses, que le validateur traite comme un fossé de sens. Le dictionnaire contient environ 22 000 entrées — substantiel, mais pas exhaustif.

3. **Complétude de la classe de variantes.** Les six classes de variantes du linter ont été conçues sur la base de la littérature linguistique et de l'observation des motifs de sortie de TA. Il peut y avoir des classes d'équivalence supplémentaires non capturées — variations dialectales, différences de registre, synonymes au niveau du discours. Aucun processus formel n'assure la complétude.

4. **Pas d'étude de corrélation humaine.** Le fossé le plus critique : personne n'a mesuré si les verdicts du linter (EXACT/EQUIVALENT/MISS) ou les verdicts du validateur sémantique corrèlent avec les jugements humains de qualité de traduction. Les métriques neurales passent des années à établir la corrélation avec l'évaluation humaine (tâches partagées WMT). Nos métriques n'ont pas cette validation.

5. **Spécificité linguistique.** Les classes de variantes, les listes de synonymes et les règles de particules optionnelles sont spécifiques au Cree des Plaines. Les porter au Sámi du Nord, à l'Inuktitut ou à toute autre langue nécessite des linguistes qui comprennent la morphologie, la flexibilité de l'ordre des mots et la variation orthographique de cette langue. Le *cadre* est portable ; les *règles* ne le sont pas.

6. **Lacunes de câblage des métriques.** À ce jour, quatre des neuf métriques du profil de notation composite (semantic_score, morphological_accuracy, equivalent_match_rate, orthographic_accuracy) ont un câblage de plugin incomplet ou peu clair dans le harnais de l'arène. Le score composite est effectivement calculé à partir d'environ cinq métriques avec des poids redistribués.

### Ce qui serait nécessaire pour valider cette approche

Pour que ce travail soit publiable — dans n'importe quel lieu, à n'importe quel niveau de sérieux académique — les expériences suivantes seraient nécessaires :

1. **Étude de corrélation avec jugement humain.** Collecter les évaluations de qualité humaine pour un ensemble de traductions Anglais→Cree (idéalement 200+ paires de phrases évaluées par 3+ locuteurs bilingues). Calculer les corrélations entre les scores humains et chacune de nos métriques. C'est la validation la plus importante. Sans elle, les métriques sont des artefacts d'ingénierie, pas des outils d'évaluation.

2. **Mesure du taux de faux rejet FST.** Exécuter l'analyseur FST sur un corpus de texte Cree connu comme bon (par exemple, textes Cree publiés, corpus parallèles validés) et mesurer quel pourcentage de mots valides sont rejetés. Cela quantifie la précision de la métrique de validité FST.

3. **Validation de deuxième langue.** Porter la métrique de validité FST à une deuxième langue GiellaLT (très probablement le Sámi du Nord, qui a l'analyseur FST le plus mature de l'écosystème GiellaLT). Démontrer que la métrique produit des résultats sensés sur la sortie de TA Sámi. Cela valide la revendication de portabilité.

4. **Comparaison avec COMET.** Exécuter COMET sur les mêmes données Cree et comparer ses scores avec nos métriques et avec les jugements humains. Si COMET produit des scores significatifs pour le Cree (ce que nous doutons, mais n'avons pas testé), nos métriques doivent le surpasser pour être utiles. Si COMET produit du bruit (ce que nous attendons), cela valide le besoin de notre approche.

5. **Complément diagnostique MorphEval.** Construire une petite (50–100 contrastes) suite de tests de style MorphEval pour le Cree des Plaines ciblant les caractéristiques morphologiques les plus distinctives de la langue (obviation, inverse, ordre conjunct/indépendant, « nous » inclusif/exclusif). Exécuter les systèmes de TA contre elle et montrer que les informations de diagnostic sont exploitables.

6. **Audit de câblage et d'intégration.** Corriger les lacunes de câblage du profil de notation identifiées dans l'inventaire du code. Assurer que les neuf métriques composites produisent des valeurs et que le score agrégé est calculé correctement.

---

## Partie 7 : Positionnement et travaux futurs

### Où LYSS s'inscrit dans le paysage d'évaluation

Une taxonomie des approches d'évaluation de TA, positionnée honnêtement :

| Dimension | Métriques de chaînes (BLEU, chrF++) | Métriques neurales (COMET, MetricX) | LLM-as-judge (GEMBA) | Diagnostic (MorphEval, CheckList) | **LYSS** |
|-----------|-------------------------------|---|----|-------|--------|
| Type de signal | Chevauchement de surface | Similarité sémantique apprise | Jugement ouvert | Sondes de capacité ciblées | Validité morphologique + équivalence basée sur des règles |
| Données d'entraînement nécessaires | Aucune | Jugements humains (milliers) | LLM pré-entraîné | Suites de tests conçues par des linguistes | FST + dictionnaire + règles de variantes |
| Applicabilité LRL | Universelle mais faible | Limitée par la couverture d'encodeur | Limitée par la couverture LLM | Limitée par la création de suite de tests | Limitée par la disponibilité FST (~30 langues) |
| Référence nécessaire | Oui | Oui (ou QE source uniquement) | Optionnel | Oui (contrastif) | Oui (LYSS-eq/LYSS-sem) / Non (LYSS-fst) |
| Interprétabilité | Faible (un nombre) | Faible (un nombre) | Élevée (rationale textuelle) | Élevée (réussite/échec par phénomène) | Élevée (verdicts + classes de variantes) |

**LYSS n'est pas** : un remplacement pour COMET sur les langues bien dotées, une métrique universelle, ou la première évaluation consciente de la morphologie.

**LYSS est** : un cadre intégré qui combine la validation morphologique basée sur FST avec les métriques standard pour le cas spécifique des langues où les métriques neurales manquent de couverture et où les outils basés sur des règles (FST, dictionnaires) existent. Il a trois composants principaux :
- **LYSS-fst** — Validité morphologique via FST (`fst_acceptance_rate`)
- **LYSS-eq** — Équivalence linguistique via le linter (`equivalent_match_rate`)
- **LYSS-sem** — Validation sémantique déterministe (`semantic_score`)

**LYSS étend** : l'intuition centrale de MorphEval (utiliser les outils morphologiques pour l'évaluation) des tests de compétence diagnostique à la notation de qualité continue.

**LYSS complète** : chrF++ (qui donne un crédit partiel pour les morphèmes partagés mais ne peut pas détecter l'équivalence), COMET (qui fonctionne dans l'espace sémantique mais manque de données d'entraînement pour LRL), et FUSE (qui utilise l'ingénierie des caractéristiques mais pas les analyseurs morphologiques). 

**L'art antérieur le plus proche est** : Hjerson (classification d'erreur linguistique) + HyTER (classes d'équivalence via réseaux de paraphrase) + métrique de couverture naïve d'Apertium (vérification de validité basée sur FST). La contribution de LYSS n'est pas une technique unique mais l'intégration de ces idées — particulièrement la validité basée sur FST et l'équivalence basée sur des règles — dans un harnais d'évaluation fonctionnant pour une langue polysynthétique.

### Intégration de MorphEval

La méthodologie de suite de tests contrastifs de MorphEval et notre approche de notation continue sont complémentaires :

- **MorphEval** répond : « Ce système peut-il gérer le marquage du temps ? L'accord du nombre ? L'assignation de cas ? »
- **Notre métrique FST** répond : « Ce système a-t-il produit des mots réels ? »
- **Notre linter** répond : « Cette traduction est-elle équivalente à la référence malgré les différences de surface ? »
- **Notre validateur sémantique** répond : « Cette traduction signifie-t-elle la bonne chose ? »

MorphEval est open source. Créer une suite de tests Cree des Plaines nécessiterait qu'un linguiste conçoive des paires contrastives couvrant les contrastes morphologiques spécifiques au Cree (obviation, marquage inverse, ordre conjunct/indépendant, « nous » inclusif/exclusif, chaînes de preverbes). C'est un travail substantiel mais délimité — des semaines, pas des mois — et fournirait une capacité de diagnostic qu'aucun autre outil d'évaluation n'offre pour le Cree.

### La question de la portabilité

Quelles autres langues pourraient adopter cette approche ? La contrainte principale est la disponibilité FST. L'infrastructure GiellaLT fournit des analyseurs morphologiques pour 30+ langues, principalement dans trois familles :

- **Langues Sámi** (Sámi du Nord, Sámi de Lule, Sámi du Sud, Sámi Skolt, Sámi Inari) : FST matures avec couverture large. Le Sámi du Nord est la cible la plus immédiatement portable.
- **Langues ouraliennes** (finnois, estonien, komi, erzya, moksha) : Analyseurs bien développés, bien que le finnois et l'estonien n'aient peut-être pas besoin d'évaluation basée sur FST aussi urgemment (ils ont plus de couverture de métrique neurale).
- **Langues autochtones arctiques** (Inuktitut via Uqailaut, groenlandais) : Les analyseurs existent mais la couverture varie.
- **Autres langues GiellaLT** : Féroïen, irlandais, cornique, livonien et autres avec des niveaux de maturité FST variés.

Au-delà de GiellaLT, la plateforme **Apertium** fournit des analyseurs morphologiques pour environ 40+ paires de langues. L'écosystème **HFST** (Helsinki Finite-State Technology) est l'infrastructure partagée que GiellaLT et Apertium utilisent, ce qui signifie que tout analyseur Apertium pourrait en principe être branché sur la même métrique de validité FST.

La contrainte pratique n'est pas la disponibilité FST mais la **curation de classe de variantes**. Les règles d'équivalence du linter nécessitent une expertise linguistique par langue cible. Pour le Sámi du Nord, cela nécessiterait de comprendre la flexibilité de l'ordre des mots Sámi, les conventions orthographiques et la variation dialectale. Pour l'Inuktitut, cela nécessiterait de comprendre la morphologie polysynthétique à un niveau comparable à ce qui a été fait pour le Cree. La métrique de validité FST, cependant, peut être déployée immédiatement pour toute langue avec un analyseur GiellaLT — aucun travail linguistique supplémentaire requis.

### Vers un article

Une publication basée sur ce travail cibleait naturellement l'un de ces lieux :

- **WMT Metrics Shared Task** (co-localisée avec EMNLP) : Le lieu le plus direct. Nécessiterait d'implémenter les métriques comme une soumission de tâche partagée et d'évaluer sur les ensembles de tests WMT — qui n'incluent actuellement aucune langue polysynthétique. Pourrait soumettre comme un article « findings » ou participer au sous-tâche des challenge sets.
- **LREC-COLING** (Language Resources and Evaluation Conference) : Ajustement naturel pour un article de ressource/outil décrivant le cadre d'évaluation et les ressources linguistiques qu'il utilise (FST, dictionnaires, règles de variantes).
- **ACL ou NAACL** (conférence principale) : Nécessiterait l'étude de corrélation avec jugement humain et au moins une langue supplémentaire pour atteindre la barre d'une conférence principale.
- **Atelier AmericasNLP** : L'audience la plus réceptive pour l'évaluation de TA des langues autochtones. Barre de publication plus basse, mais impact élevé au sein de la communauté cible.
- **ComputEL** (Computational Approaches to Endangered Languages) : Lieu axé pour exactement ce type de travail.

Toute publication nécessiterait des co-auteurs ayant une expertise en linguistique Cree (pour valider les classes de variantes et interpréter les résultats) et idéalement des locuteurs bilingues Cree (pour fournir les évaluations de qualité humaine pour l'étude de corrélation). Ce n'est pas optionnel — un article sur l'évaluation de TA Cree écrit entièrement par des non-locuteurs Cree serait, au mieux, incomplet, et au pire, une continuation de la dynamique de recherche extractive que le domaine essaie de dépasser.

---

## Appendice A : Matrice des exigences des métriques

| Métrique | Référence nécessaire ? | Source nécessaire ? | Modèle entraîné ? | Ressources spécifiques à la langue ? | Fonctionne pour LRL ? |
|--------|-------------------|---------------|----------------|------------------------------|----------------|
| BLEU | Oui | Non | Non | Non | Mal |
| chrF++ | Oui | Non | Non | Non | Mieux que BLEU |
| METEOR | Oui | Non | Non | Raciniseur + WordNet | Seulement si les ressources existent |
| TER | Oui | Non | Non | Non | Même que BLEU |
| BERTScore | Oui | Non | Oui (mBERT) | Non | Dépend de la couverture du modèle |
| BLEURT | Oui | Non | Oui (entraîné) | Non | Dépend des données d'entraînement |
| COMET | Oui | Oui | Oui (XLM-R) | Non | Dépend de la couverture XLM-R |
| CometKiwi | Non | Oui | Oui (XLM-R) | Non | Dépend de la couverture XLM-R |
| GEMBA | Optionnel | Oui | Oui (LLM) | Non | Dépend de la couverture LLM |
| **Acceptation FST** | **Non** | **Non** | **Non** | **Oui (analyseur FST)** | **Oui, si FST existe** |
| **Linter CRK** | **Oui** | **Non** | **Non** | **Oui (FST + règles de variantes)** | **Oui, si les ressources existent** |
| **Sémantique CRK** | **Oui** | **Optionnel** | **Non** | **Oui (FST + dictionnaire + spaCy)** | **Oui, si les ressources existent** |
| Détection d'hallucination | Non | Oui | Non | Non | Oui |
| Détection de code-switching | Optionnel | Oui | Non | Minimal | Oui |
| MorphEval | Oui (contrastif) | Oui | Non | Oui (suite de tests + analyseur) | Seulement si la suite de tests existe |

## Appendice B : Articles clés

| Citation | Lieu | Pertinence |
|----------|-------|-----------|
| Papineni et al. (2002). BLEU: a Method for Automatic Evaluation of Machine Translation | ACL 2002 | La métrique qui a défini le domaine |
| Doddington (2002). Automatic Evaluation of Machine Translation Quality Using N-gram Co-Occurrence Statistics | HLT 2002 | Correspondance de n-grammes pondérée par l'information |
| Banerjee & Lavie (2005). METEOR: An Automatic Metric for MT Evaluation | Atelier ACL 2005 | Racinisation, synonymes, alignement des mots |
| Snover et al. (2006). A Study of Translation Edit Rate | AMTA 2006 | Distance d'édition avec décalages de phrases |
| Popović & Ney (2011). Morphemes and POS tags for n-gram based evaluation metrics | WMT 2011 | Classification d'erreur Hjerson |
| Dreyer & Marcu (2012). HyTER: Meaning-Equivalent Semantics for Translation Evaluation | NAACL-HLT 2012 | Classes d'équivalence via réseaux de paraphrase |
| Lommel et al. (2014). Multidimensional Quality Metrics | — | Typologie d'erreur MQM |
| Popović (2015). chrF: character n-gram F-score for automatic MT evaluation | WMT 2015 | Évaluation au niveau des caractères |
| Popović (2017). chrF++: words helping character n-grams | WMT 2017 | Évaluation au niveau des caractères + mots |
| Burlot & Yvon (2017). Evaluating the Morphological Competence of Machine Translation Systems | WMT 2017 | Suites de tests morphologiques contrastifs |
| Sennrich (2017). How Grammatical is Character-level Neural Machine Translation? | EACL 2017 | Paires contrastives LingEval97 |
| Isabelle, Cherry & Foster (2017). A Challenge Set Approach to Evaluating Machine Translation | EMNLP 2017 | Tests de divergence structurelle ciblée |
| Post (2018). A Call for Clarity in Reporting BLEU Scores | WMT 2018 | Standardisation sacreBLEU |
| Reiter (2018). A Structured Review of the Validity of BLEU | Computational Linguistics | Méta-analyse de la corrélation de BLEU avec le jugement humain |
| Stanovsky, Smith & Zettlemoyer (2019). Evaluating Gender Bias in Machine Translation | ACL 2019 | Évaluation du genre WinoMT |
| Ribeiro et al. (2020). Beyond Accuracy: Behavioral Testing of NLP Models with CheckList | ACL 2020 (Meilleur article) | Tests unitaires basés sur les capacités pour NLP |
| Zhang et al. (2020). BERTScore: Evaluating Text Generation with BERT | ICLR 2020 | Similarité sémantique basée sur les embeddings |
| Sellam et al. (2020). BLEURT: Learning Robust Metrics for Text Generation | ACL 2020 | Métrique pré-entraînée + ajustée fin |
| Rei et al. (2020). COMET: A Neural Framework for MT Evaluation | EMNLP 2020 | Évaluation trilingue multilingue |
| Freitag et al. (2021). Results of the WMT 2021 Metrics Shared Task | WMT 2021 | Méta-évaluation basée sur MQM |
| Thompson & Post (2020). PRISM: Automatic MT Evaluation via Zero-Shot Paraphrasing | EMNLP 2020 | NMT multilingue comme évaluateur de paraphrase |
| Currey et al. (2022). MT-GenEval | EMNLP 2022 | Précision du genre contrefactuelle |
| Amrhein et al. (2022). ACES: Translation Accuracy Challenge Sets | WMT 2022 | 68 phénomènes, 146 paires de langues |
| Kocmi & Federmann (2023). GEMBA: Large Language Models Are State-of-the-Art Evaluators | EAMT 2023 | LLM-as-evaluator |
| Guerreiro et al. (2024). xCOMET: Transparent MT Evaluation through Fine-grained Error Detection | TACL 2024 | Détection d'erreur au niveau des spans |
| Wang & Adelani (2024). AfriMTE and AfriCOMET | NAACL 2024 | Métriques neurales pour les langues africaines |
| Juraska et al. (2024). MetricX-24 | WMT 2024 | Métrique gagnante basée sur mT5 |

## Appendice C : Glossaire des termes d'évaluation

| Terme | Définition |
|------|-----------|
| **Adéquation** | Si une traduction transmet le sens de la source. |
| **Fluidité** | Si une traduction est grammaticale et naturelle dans la langue cible. |
| **Direct Assessment (DA)** | Méthode d'évaluation humaine où les annotateurs évaluent les traductions sur une échelle 0–100. |
| **MQM** | Multidimensional Quality Metrics — évaluation humaine basée sur les spans d'erreur avec des gravités typées. |
| **Quality Estimation (QE)** | Prédiction de la qualité de la traduction sans traduction de référence. |
| **FST** | Transducteur à états finis — un dispositif informatique qui encode les règles morphologiques d'une langue. |
| **GiellaLT** | Infrastructure pour la technologie linguistique basée sur des règles, principalement pour le Sámi et les autres langues arctiques. |
| **HFST** | Helsinki Finite-State Technology — le cadre logiciel sous-jacent à GiellaLT et Apertium. |
| **SRO** | Standard Roman Orthography — le système d'écriture basé sur le latin pour le Cree des Plaines. |
| **Syllabiques** | Syllabaires autochtones canadiens — un système d'écriture abugida utilisé pour le Cree et d'autres langues algonquiennes. |
| **Polysynthétique** | Un type de langue où un seul mot peut encoder l'équivalent d'une phrase anglaise entière par affixation extensive. |
| **Obviation** | Une catégorie grammaticale dans les langues algonquiennes qui distingue deux référents à la troisième personne. |
| **Inverse** | Une catégorie de type voix dans les langues algonquiennes marquant que le patient surclasse l'agent sur la hiérarchie d'animacité. |
| **WMT** | Conference on Machine Translation — le lieu principal pour les tâches partagées et l'évaluation de TA. |
| **Évaluation contrastive** | Test si un système peut distinguer les entrées minimalement différentes qui nécessitent des sorties différentes. |
| **Challenge set** | Une suite de tests conçue ciblant des phénomènes linguistiques spécifiques. |
| **Classe d'équivalence** | Un ensemble de formes de surface différentes qui représentent le même sens et devraient recevoir le même score d'évaluation. |