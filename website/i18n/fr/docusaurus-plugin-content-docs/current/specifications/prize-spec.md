---
sidebar_position: 8
title: "Spécification des prix"
slug: '/specifications/prizes'
related:
  - label: "How Speakers Get Paid"
    to: /docs/perspectives/how-speakers-get-paid
    kind: position
    note: "The plain-language version of these numbers"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
---
# Spécification des Prix

> **Objectif.** Ce document définit la structure du fonds de prix, les conditions de seuil, le processus de réclamation et les règles de l'MT Eval Arena. Il précise exactement ce que « capable de traduction automatique » signifie en termes mesurables, et dans quelles conditions l'argent des prix est versé. Ce document fait référence à SCORING_SPEC pour les définitions des métriques et à BENCHMARK_SPEC pour le protocole d'évaluation — il ne les duplique pas.
>
> **Statut :** EN VIGUEUR. Le Founder's Prize (§2.1) est financé et actif.
>
> Dernière mise à jour : 2026-06-04

---

## 1. Philosophie

### 1.1 Les Prix Récompensent les Percées, Non la Participation

L'argent des prix n'est versé que lorsqu'une méthode démontre clairement qu'elle atteint un seuil de capacité défini. Il n'y a pas de prix de participation, de prix pour les finalistes ou de versements de consolation. Si personne ne franchit la barre, personne n'est payé. C'est intentionnel — cela signifie que les sponsors ne paient que pour les résultats qui fonctionnent réellement.

### 1.2 La Validation Communautaire Est Non-Négociable

Les métriques automatisées sont des approximations (SCORING_SPEC §1.1). Une méthode peut obtenir un bon score en chrF++ et en acceptation FST tout en produisant un résultat qu'aucun locuteur n'accepterait. **Chaque réclamation de prix nécessite une validation communautaire** — les locuteurs bilingues doivent confirmer que le résultat est utilisable. C'est la porte de validation humaine (BENCHMARK_SPEC §7).

### 1.3 Le Transfert de Propriété Fait Partie de l'Accord

Les méthodes qui réclament un prix sont soumises à la clause de transfert de propriété (BENCHMARK_SPEC §8.3). Le développeur conserve les droits d'attribution et de publication. L'organisation de gouvernance obtient le droit d'utiliser, de modifier, de distribuer et de monétiser la méthode pour leur langue. Ce n'est pas une pénalité — c'est l'objectif. L'argent des prix finance la création de technologie qui appartient à la communauté linguistique.

### 1.4 Anti-Triche

Les seuils des prix sont définis par rapport à **l'évaluation de référence** (ensemble de test secret, exécuté par l'organisation de gouvernance dans un bac à sable). Les développeurs ne voient jamais les données de test. Ceci est appliqué architecturalement — pas une politique qui repose sur l'honneur. Voir BENCHMARK_SPEC §8.2.

### 1.5 Licence de Corpus : Les Corpus Non-Commerciaux Restent Hors de la Voie des Prix

Certains corpus utilisés lors du développement de la méthode portent des licences non-commerciales — par exemple, le corpus EdTeKLA Cree Language Textbook est **CC BY-NC-SA 4.0**. Ces corpus sont **réservés à la voie recherche/développement uniquement** :

1. **Les corpus de référence des prix ne doivent pas intégrer de contenu de corpus sous licence NC.** Les segments de test de référence sont des originaux commandés par la communauté (voir Corpus Partnership Strategy) — rédigés par des humains pour le prix, avec les droits clarifiés pour l'évaluation et le déploiement commercial dès le départ.
2. **Une méthode qui réclame un prix ne doit pas intégrer de contenu de corpus sous licence NC** (par exemple, comme données d'entraînement, exemples intégrés ou tables de consultation). La méthode transférée est destinée au déploiement commercial par l'organisation de gouvernance (BENCHMARK_SPEC §8.3, Method Submission Agreement §6) ; le contenu sous licence NC à l'intérieur l'empoisonnerait.
3. **Les développeurs peuvent librement utiliser des corpus sous licence NC pour développer et auto-évaluer** — c'est à cela que sert la voie de développement. La restriction s'applique à ce qui est soumis et à ce qui est déployé, non à la façon dont un développeur apprend.

### 1.6 Les Classes de Dépendances Contrôlent l'Admissibilité aux Prix

Toute évaluation de prix se déroule dans un bac à sable (§1.4), et les méthodes gagnantes sont transférées à l'organisation de gouvernance (§1.3). Les deux faits imposent la même contrainte : **tout ce dont une méthode dépend doit être quelque chose que le développeur a le droit de mettre dans le bac à sable et de transférer à la communauté.** Chaque soumission déclare une classe de dépendance — définie dans la [spécification de l'interface des méthodes](/docs/specifications/methods#method-validity-and-dependency-classes), avec les conditions d'admissibilité dans la Method Submission Agreement §2.6 — et l'admissibilité suit la classe :

| Classe de dépendance | Admissible aux prix ? | Conditions |
|------------------|----------------|------------|
| **S** — autonome | ✅ Oui | Aucune au-delà des conditions de seuil dans §2 |
| **O** — externe ouvert (par exemple, FST AGPL mirrorisé à la soumission) | ✅ Oui | Artefacts épinglés et vendus dans la soumission ; les licences permettent le transfert communautaire ; les termes copyleft préservés (la communauté reçoit les mêmes droits que la licence accorde à tous) |
| **A1** — inférence LLM substituable | ⚠️ Conditionnel | Modèle déclaré, épinglé et substituable (doit s'exécuter contre un modèle de poids ouvert hébergé par la communauté) ; l'évaluation acheminée via la passerelle LLM du bac à sable (🔲 prévu — les méthodes A1 ne peuvent pas produire de scores de référence jusqu'à ce que la passerelle soit opérationnelle) ; le transfert transmet la recette complète (invites, entraînement, code), pas le modèle |
| **A2** — API de service/données externe non-substituable | ❌ Pas encore | Inadmissible jusqu'à ce que le détenteur des droits accorde les permissions d'inclusion dans le bac à sable et de transfert. Autorisé sur le classement ouvert avec un drapeau visible « dépendance externe » |
| **X** — contenu groupé sans droits | ❌ Jamais | Inadmissible dans chaque voie |

La classe d'une méthode est la classe la plus restrictive parmi ses dépendances déclarées. Les dépendances non déclarées de toute classe sont disqualifiantes (§5).

---

## 2. Fonds de Prix Actifs

### 2.1 Le Founder's Prize — EN→Plains Cree (nêhiyawêwin)

| Champ | Valeur |
|-------|--------|
| **Fonds de prix** | **10 000 $ CAD** |
| **Paire linguistique** | Anglais → Plains Cree (EN→CRK) |
| **Financé par** | Fondateur du projet Champollion |
| **Statut** | **ACTIF** — accepte les soumissions |
| **Ouverture** | Lorsque le corpus de référence + l'organisation de gouvernance sont en place |
| **Expiration** | Pas d'expiration. Le prix reste actif jusqu'à ce qu'il soit réclamé ou explicitement retiré. |

#### Conditions de Seuil

Une méthode réclame le Founder's Prize en remplissant **TOUTES** les conditions suivantes simultanément :

| # | Condition | Métrique | Seuil | Justification |
|---|-----------|--------|-----------|-----------|
| 1 | **Score composite** | `composite` (SCORING_SPEC §4) | **≥ 0,80** | Entre Déployable (0,70) et Fluide (0,85). Nécessite une qualité élevée dans toutes les dimensions des métriques — pas seulement la validité morphologique. |
| 2 | **Acceptation FST** | `fst_acceptance_rate` (SCORING_SPEC §2.2) | **≥ 0,99 (99 %+)** | Pratiquement tous les mots de sortie doivent être des formes morphologiquement valides reconnues par le FST GiellaLT. La tolérance de 1 % tient compte des cas limites (noms propres, néologismes, emprunts) que le FST peut légitimement ne pas couvrir. C'est la porte de qualité définissante pour la TA polysynthétique — si le FST rejette plus de 1 % des mots, la méthode produit des formes qui n'existent pas dans la langue. Tout l'objectif de ce prix est d'acheter un système qui ne massacre pas la langue. |
| 3 | **chrF++** | `chrf_plus_plus` (SCORING_SPEC §2.1) | **≥ 55,0** | Le chevauchement des n-grammes de caractères doit dépasser 55 sur l'échelle 0–100. Assure la similarité au niveau de la surface avec les traductions de référence, pas seulement la validité morphologique. |
| 4 | **Validation communautaire** | Examen humain (BENCHMARK_SPEC §7) | **≥ 70 % « acceptable » ou « excellent »** | Un échantillon stratifié de résultats (≥30 entrées dans les niveaux de difficulté 2–5) est examiné par ≥2 locuteurs bilingues du CRK. Au moins 70 % des entrées examinées doivent recevoir une note « acceptable » ou « excellent ». |
| 5 | **Évaluation de référence** | Exécution en bac à sable (BENCHMARK_SPEC §8.2) | **Obligatoire** | Toutes les métriques automatisées doivent être calculées par rapport au segment de corpus `gold_standard`, exécuté par l'organisation de gouvernance dans un environnement en bac à sable. Les scores sur l'ensemble de développement ne comptent pas. |
| 6 | **Reproductibilité** | Correspondance d'empreinte (BENCHMARK_SPEC §3.8) | **±2 %** | L'organisation de gouvernance doit pouvoir réexécuter la méthode et obtenir des scores dans les ±2 % de la carte d'exécution soumise. |

> **Pourquoi 99+ % FST ?** Le problème central de la traduction automatique pour les langues polysynthétiques est l'hallucination — les LLM produisent des chaînes qui *ressemblent* à la langue cible mais sont morphologiquement invalides. Une méthode qui produit 95 % de résultats valides a toujours 5 % de mots fabriqués — du bruit inacceptable pour tout usage en production. Le seuil de 99+ % FST exige une hallucination quasi-nulle tout en permettant le cas rare (un nom propre que le FST ne connaît pas, un néologisme légitime). Si une méthode ne peut pas atteindre 99+ % d'acceptation FST, elle n'a pas résolu le problème.
>
> **Pourquoi 0,80 composite ?** Cela se situe entre Déployable (0,70) et Fluide (0,85). Une méthode à 0,80 avec 99+ % d'acceptation FST produit un résultat où pratiquement chaque mot est un vrai mot du Cree *et* la qualité globale de la traduction est élevée dans toutes les dimensions de surface, structurelles et sémantiques. La porte de validation communautaire (condition #4) assure que ce n'est pas seulement du jeu de métriques — les locuteurs doivent confirmer que le résultat est véritablement utilisable.

#### Ce Que Ce Seuil Signifie en Pratique

Avec un composite ≥ 0,80 avec FST ≥ 0,99 et chrF++ ≥ 55, un locuteur bilingue verrait généralement :

- **Pratiquement chaque** mot de sortie est un vrai mot du Cree (FST valide 99+ % — hallucinations de formes quasi-nulles)
- Les catégories grammaticales majeures (personne, nombre, temps) sont correctes dans la plupart des entrées
- L'ordre des mots est généralement naturel
- Le sens est préservé de manière fiable
- Les erreurs restantes sont des erreurs de vraie langue (mauvaise inflexion, obviation incorrecte, désaccords d'animacité) — pas des mots fabriqués
- Un locuteur courant pourrait utiliser le résultat comme un brouillon de haute qualité et le corriger beaucoup plus rapidement que de traduire à partir de zéro

C'est un système qui **ne massacre pas la langue.** Il peut ne pas être parfait, mais chaque mot qu'il produit est un vrai mot. C'est la barre minimale pour une traduction automatique respectueuse d'une langue polysynthétique.

---

## 3. Processus de Réclamation du Prix

### 3.1 Soumission

1. Le développeur soumet sa méthode complète et exécutable à l'organisation de gouvernance :
   - Tout le code source
   - Toutes les dépendances (données d'entraînement, dictionnaires, configurations FST, invites)
   - Instructions d'installation et d'exécution
   - Un README décrivant l'approche de la méthode
   - Une carte d'exécution sur l'ensemble de développement montrant les scores approximatifs (pour le pré-filtrage)

2. Le développeur signe les conditions de participation, y compris :
   - Clause de transfert de propriété (BENCHMARK_SPEC §8.3)
   - Déclaration de non-entraînement sur les données d'évaluation
   - Engagement de reproductibilité

### 3.2 Évaluation

1. L'organisation de gouvernance installe et exécute la méthode dans un harnais en bac à sable par rapport au corpus `gold_standard`
2. Les métriques automatisées sont calculées (composite, FST, chrF++, etc.)
3. Si les seuils automatisés sont atteints (conditions 1–3), l'organisation de gouvernance procède à l'examen communautaire
4. Si les seuils automatisés ne sont PAS atteints, le développeur reçoit les scores et les commentaires. Aucun examen communautaire n'est déclenché.

### 3.3 Examen Communautaire

1. Un échantillon stratifié de résultats (≥30 entrées, couvrant les niveaux de difficulté 2–5) est présenté aux locuteurs bilingues
2. Au minimum 2 examinateurs indépendants évaluent chaque entrée
3. Échelle d'évaluation : **rejeter** / **gist** / **acceptable** / **excellent**
4. Si ≥70 % des entrées reçoivent « acceptable » ou « excellent » des deux examinateurs, la validation communautaire réussit

### 3.4 Versement

1. Les 6 conditions sont remplies
2. L'organisation de gouvernance confirme le résultat
3. Le prix est versé dans les 30 jours suivant la confirmation
4. La propriété de la méthode est transférée selon BENCHMARK_SPEC §8.3
5. Le résultat est publié sur le classement avec le niveau de vérification « Community Validated »

### 3.5 Soumissions Multiples

- Le même développeur/équipe peut soumettre plusieurs fois
- Chaque soumission est évaluée indépendamment
- Si une méthode est améliorée et re-soumise, seule la dernière carte d'exécution compte
- Le prix est attribué à la **première** méthode qui franchit tous les seuils — il n'est pas divisé

### 3.6 Soumissions d'Équipe

- Les équipes et les paires Aîné-jeunesse sont admissibles
- La distribution du prix au sein d'une équipe est la responsabilité de l'équipe
- Tous les membres de l'équipe doivent signer les conditions de participation
- L'attribution sur le classement énumère tous les membres de l'équipe

---

## 4. Fonds de Prix Futurs {#4-future-prize-pools}

Le Founder's Prize est la graine. Des fonds de prix supplémentaires sont financés par des sponsors. Chaque nouveau fonds de prix est documenté comme une nouvelle sous-section de §2 avec ses propres :

- Montant et devise du prix
- Paire linguistique
- Attribution du sponsor
- Conditions de seuil (qui peuvent différer du Founder's Prize)
- Date d'expiration (le cas échéant)
- Toute condition spéciale

### 4.1 Modèle de Prix du Sponsor

Les sponsors financent des fonds de prix à tout montant. Niveaux suggérés :

| Niveau | Montant | Seuil Suggéré |
|------|--------|---------------------|
| **Graine** | 5 000–15 000 $ | Déployable (composite ≥ 0,70) + validation communautaire |
| **Percée** | 25 000–50 000 $ | Fluide (composite ≥ 0,85) + validation communautaire |
| **Grand Prix** | 100 000 $+ | Fluide + couverture multi-registre + intégration de déploiement |

Les sponsors peuvent également financer :
- **Primes d'amélioration** — paiement fixe pour chaque amélioration de 5 points en chrF++ par rapport au meilleur actuel
- **Prix de registre** — prix distincts pour des registres spécifiques (formel, cérémoniel, éducatif)
- **Prix de vitesse** — meilleur score ajusté au coût (SCORING_SPEC §6.3)

### 4.2 Séquestre du Fonds de Prix

Tous les fonds de prix sont détenus en séquestre (gérés par le projet ou un tiers désigné) jusqu'à ce que les conditions de seuil soient remplies. Si un prix expire sans être réclamé, les fonds sont retournés au sponsor ou redirigés vers un nouveau fonds de prix à la discrétion du sponsor.

---

## 5. Disqualification

Une soumission est disqualifiée si :

1. **Entraînement sur les données d'évaluation.** La méthode a été exposée aux entrées du corpus `gold_standard` ou `held_out`. (Architecturalement prévenu par l'exécution en bac à sable — mais si des preuves de contamination sont trouvées, le résultat est annulé.)
2. **Non-reproductible.** L'organisation de gouvernance ne peut pas reproduire les scores dans les ±2 %.
3. **Dépendances non déclarées ou inadmissibles.** La méthode nécessite un accès à l'exécution à des services externes au-delà de ce que son manifeste de dépendance déclare, ou sa classe de dépendance effective est A2 ou X (§1.6). L'inférence LLM de classe A1 déclarée acheminée via la passerelle d'évaluation est autorisée ; toute autre dépendance réseau à l'exécution — et toute dépendance non déclarée de toute classe — est disqualifiante.
4. **Conditions de participation non signées.** Tous les membres de l'équipe doivent accepter le transfert de propriété.
5. **Triche détectée.** Le résultat est optimisé pour la métrique plutôt que pour la qualité de la traduction (détecté par l'examen communautaire et/ou les vérifications anti-triche selon BENCHMARK_SPEC §9.3).

---

## 6. Relation avec les Autres Spécifications

| Ce Document | Références | Pour |
|--------------|-----------|-----|
| §2 conditions de seuil | SCORING_SPEC §4 (composite), §2.1–2.2 (métriques), §5 (niveaux) | Définitions des métriques et échelle |
| §2 validation communautaire | BENCHMARK_SPEC §7 | Protocole d'examen humain |
| §3 exécution en bac à sable | BENCHMARK_SPEC §8.2 | Mécanisme de souveraineté |
| §3 transfert de propriété | BENCHMARK_SPEC §8.3 | Conditions de transfert de PI |
| §1.6 classes de dépendances | Spécification de l'interface des méthodes ; Method Submission Agreement §2.6 ; BENCHMARK_SPEC §8.6 | Définitions de classe, conditions d'admissibilité, politique réseau du bac à sable |
| §4 prix ajustés au coût | SCORING_SPEC §6.3 | Formule ajustée au coût |

---

## 7. Synchronisation Code–Spécification

### 7.1 Source Canonique

Ce document (`arena/website/docs/specifications/prize-spec.md`) est la source canonique pour :
- Définitions des fonds de prix (§2)
- Conditions de seuil (§2.x)
- Processus de réclamation (§3)
- Règles de disqualification (§5)

### 7.2 Exigences de Mise en Œuvre

Lorsqu'un fonds de prix est activé :
1. L'interface utilisateur du classement doit afficher les prix actifs et leurs conditions de seuil
2. Les cartes d'exécution qui remplissent les seuils automatisés (conditions 1–3) doivent être signalées pour examen communautaire
3. Le champ `quality_tier` dans le schéma de la carte d'exécution capture déjà le niveau (« deployable », « fluent »)
4. Aucune nouvelle modification de code du harnais n'est nécessaire — la spécification des prix est une couche de politique au-dessus de la notation existante

---

*Les structures de prix doivent être compatibles avec les conditions de transfert de propriété. Le gagnant peut réclamer le prix, mais la méthode devient la propriété de l'organisation de gouvernance si elle atteint le niveau Déployable. C'est intentionnel — le prix finance la création de technologie qui appartient à la communauté linguistique.*