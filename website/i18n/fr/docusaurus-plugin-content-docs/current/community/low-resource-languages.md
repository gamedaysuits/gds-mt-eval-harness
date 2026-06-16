---
sidebar_position: 5
title: "Soutenir une langue peu dotée en ressources"
related:
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "The first step for an uncovered language"
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
  - label: "Plains Cree, the trading card"
    to: https://champollion.dev/trading-cards?q=crk
    kind: card
    note: "The proof-of-concept language, as a card"
---
# Soutenir une langue peu dotée en ressources

> **Résumé exécutif.** Un guide complet pour construire la traduction automatique pour les langues peu dotées en ressources et polysynthétiques. Couvre les raisons pour lesquelles ces langues sont difficiles (complexité morphologique, données éparses, hallucinations), les ressources informatiques existantes (ALTLab FST, GiellaLT, Apertium, UniMorph, EdTeKLA), plus de 10 stratégies d'approche, le système d'accompagnement champollion et la boucle d'évaluation. Commencez ici si vous souhaitez contribuer une méthode pour une langue mal desservie.

:::info Statut : En développement actif
Le support du cri des Plaines (nêhiyawêwin) est actuellement en développement. Les outils, le harnais d'évaluation et le classement décrits ici sont réels et utilisables dès aujourd'hui, mais le pipeline de traduction du cri n'a pas encore été publié. Lorsqu'il le sera, ceci servira de modèle pour d'autres langues polysynthétiques et peu dotées en ressources disposant d'une infrastructure FST.
:::

## Le problème non résolu

Google Translate supporte environ 130 langues. OMT-1600 de Meta (mars 2026) revendique une couverture de 1 600 — le plus grand système de traduction automatique jamais publié. Mais pour les environ 1 300 langues aux niveaux de ressources les plus bas, la qualité est en dessous des seuils utilisables, les données d'entraînement sont dominées par des textes bibliques, les poids du modèle ne sont pas disponibles en téléchargement, et il n'existe aucune évaluation indépendante ni cadre de gouvernance communautaire. Pour les 5 400 langues restantes, aucun modèle préentraîné ne produit aucune sortie.

Le paysage a considérablement changé — les grandes entreprises technologiques investissent maintenant dans la couverture des langues peu dotées en ressources. Mais la couverture n'est pas la qualité, et la qualité sans vérification indépendante n'est pas la confiance. Les langues peu dotées en ressources ont besoin de plus qu'un modèle qui prétend les couvrir — elles ont besoin d'une évaluation indépendante avec validation morphologique, de corpus curés par la communauté et d'une gouvernance respectueuse de la souveraineté.

**champollion a été construit pour changer cela.**

Le [Classement des méthodes](https://champollion.dev/leaderboard) est un défi ouvert : construisez la meilleure méthode de traduction pour une langue mal desservie, prouvez-le avec une évaluation reproductible et réclamez le meilleur score. N'importe qui dans le monde peut contribuer — linguistes, chercheurs en apprentissage automatique, travailleurs linguistiques communautaires, étudiants, passionnés. Le problème n'est pas résolu. L'infrastructure est là. Le classement attend.

---

## Pourquoi c'est difficile : morphologie polysynthétique

La plupart des systèmes de traduction automatique commerciaux ont été conçus pour des langues comme l'anglais, le français et le chinois — des langues où les mots sont relativement courts et les phrases sont construites à partir de jetons discrets. Mais de nombreuses langues autochtones, y compris le cri des Plaines, sont **polysynthétiques** : un seul mot peut encoder ce que l'anglais exprime comme une phrase entière.

### L'exemple du cri

Considérez le mot du cri des Plaines :

> **ê-kî-nitawi-kîskinwahamâkosiyân**
> *« when I went to school »*

C'est **un seul mot**. Il encode le temps (passé), la direction (aller à), la racine (apprendre), la voix (passif/réfléchi) et la personne (première du singulier). Un modèle de langage entraîné principalement sur l'anglais n'a aucune intuition pour ce type de densité morphologique.

Les défis se multiplient :

| Défi | Ce que cela signifie |
|------|---------------------|
| **Complexité morphologique** | Une seule racine verbale peut générer des milliers de formes fléchies valides par préfixation, suffixation et circumfixation |
| **Distinction animé/inanimé** | Les noms sont grammaticalement animés ou inanimés — cela affecte la conjugaison verbale, les démonstratifs et la pluralisation. La classification ne suit pas toujours l'animacité biologique (*askiy* « terre » est animé ; *maskisin* « chaussure » est aussi animé) |
| **Obviation** | Les références à la troisième personne sont classées par proximité/saillance. La distinction « proximal » et « oblatif » n'a pas d'équivalent en anglais |
| **Données d'entraînement éparses** | Les modèles de langage ont vu très peu de texte en cri des Plaines. Ce qu'ils ont vu peut mélanger les dialectes (dialecte Y, dialecte TH) ou les orthographies (SRO vs. syllabiques) |
| **Baseline commerciale faible** | OMT-1600 inclut CRK au niveau R1 (Très peu de ressources) avec entraînement sur domaine biblique et tokenisation BPE standard. Google Translate ne supporte pas le cri. L'évaluation indépendante avec des métriques morphologiques est ce qui rend ces baselines significatives. |

La traduction des langues polysynthétiques reste un **problème de recherche ouvert** — OMT-1600 inclut les langues polysynthétiques mais utilise la tokenisation BPE standard (vocabulaire de 256K) sans conscience morphologique, ce qui signifie qu'il déchire les mots compositionnels en fragments d'octets dénués de sens.

---

## Travaux antérieurs : comment les gens ont abordé cela

### Le FST d'ALTLab

La ressource informatique la plus importante pour le cri des Plaines est le **transducteur à états finis (FST)** développé par le [Laboratoire de technologie linguistique de l'Alberta (ALTLab)](https://altlab.artsrn.ualberta.ca/) à l'Université de l'Alberta, en collaboration avec [Giellatekno](https://giellatekno.uit.no/) à l'Université arctique UiT de Norvège.

Le FST d'ALTLab est un **analyseur et générateur morphologique** : étant donné un mot cri fléchi, il peut le décomposer en sa racine et ses étiquettes grammaticales, et étant donné une racine plus des étiquettes, il peut générer la forme fléchie correcte. C'est déterministe — pas de réseau de neurones, pas d'hallucination, pas de probabilité. Si le FST accepte un mot, ce mot est morphologiquement valide en cri.

C'est pourquoi le classement champollion suit le **taux d'acceptation FST** comme métrique. Une méthode de traduction qui produit des mots que le FST rejette produit du cri morphologiquement invalide — indépendamment de ce que dit le score chrF++.

**Ressources clés d'ALTLab :**
- [itwêwina](https://itwewina.altlab.app/) — un dictionnaire cri des Plaines–anglais intelligent alimenté par le FST
- [Morphodict](https://github.com/UAlbertaALTLab/morphodict) — plateforme de dictionnaire consciente de la morphologie en open source
- [crk-db](https://github.com/UAlbertaALTLab/crk-db) — base de données lexicale du cri des Plaines
- [21st Century Tools for Indigenous Languages](https://21c.tools/) — le contexte du projet plus large

### Registres FST et morphologiques mondiaux

Le cri des Plaines n'est pas la seule langue disposant d'une infrastructure FST de haute qualité. Si vous souhaitez développer des pipelines de traduction pour d'autres langues peu dotées en ressources ou morphologiquement complexes, vous pouvez exploiter ces centres mondiaux établis :

* **[GiellaLT / Giellatekno](https://giellalt.github.io/) (Université arctique UiT de Norvège) :** Le plus grand référentiel d'analyseurs et générateurs morphologiques FST en open source, couvrant plus de 100 langues. Les domaines de focus incluent les langues sámi (`sme`, `smj`, `sma`, etc.), les langues ouraliennes (Komi, Erzya, Oudmourte, etc.) et d'autres langues minoritaires/autochtones. Ils hébergent des corpus de texte traité publiquement (`corpus-xxx`) dans leur [Organisation GitHub](https://github.com/giellalt/).
* **[Le projet Apertium](https://www.apertium.org/) :** Une plateforme de traduction automatique basée sur des règles en open source. Apertium maintient des analyseurs morphologiques FST hautement optimisés (utilisant `lttoolbox` et `hfst`) et des dictionnaires bilingues pour des dizaines de langues, y compris une large suite de langues turques (kazakh, tatar, kirghize, etc.) et de langues européennes minoritaires. Toutes les ressources sont publiques sur [GitHub d'Apertium](https://github.com/apertium).
* **[UniMorph (Morphologie universelle)](https://unimorph.github.io/) :** Un projet collaboratif fournissant des paradigmes morphologiques standardisés pour plus de 150 langues. L'ensemble de données est hébergé sur Hugging Face à [unimorph/universal_morphologies](https://huggingface.co/datasets/unimorph/universal_morphologies). Si un binaire FST compilé n'est pas disponible pour une langue, les tableaux UniMorph peuvent être utilisés comme porte de recherche de base de données statique.
* **[Conseil national de recherches Canada (CNRC)](https://nrc-digital-repository.canada.ca/) :** Offre des outils pour les langues autochtones canadiennes, y compris l'analyseur morphologique FST **Uqailaut** inuktitut et le massif **Corpus parallèle Hansard du Nunavut** (1,3 M paires de phrases alignées anglais-inuktitut).

### Le corpus EdTeKLA

Le groupe de recherche [EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) (également à UAlberta) a assemblé un corpus de langue cri des Plaines à partir de matériels éducatifs, de transcriptions audio et de sources communautaires. L'ensemble de données d'évaluation champollion [EDTeKLA Dev v1](/docs/leaderboard/datasets) est dérivé de ce travail, sous licence [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

### Autres approches que les gens ont essayées ou pourraient essayer

Le classement est agnostique quant à la méthode. Voici les stratégies qui ont été explorées ou proposées pour la traduction automatique peu dotée en ressources, dont n'importe laquelle pourrait être soumise :

| Approche | Comment cela fonctionne | Avantages | Inconvénients |
|----------|------------------------|----------|--------------|
| **[Incitation LLM accompagnée](/docs/tutorials/coached-llm-prompting)** | Injecter des règles de grammaire, des dictionnaires et des paires d'exemples dans l'invite système | Rapide à itérer, aucun entraînement nécessaire | Le plafond de qualité est limité par les connaissances de base du LLM |
| **[Incitation few-shot](/docs/tutorials/few-shot-prompting)** | Inclure des traductions vérifiées comme exemples en contexte | Bon pour un style cohérent | Petite fenêtre de contexte ; les exemples ne doivent PAS provenir des données d'évaluation |
| **[Pipeline avec porte FST](/docs/tutorials/fst-gated-pipeline)** | Le LLM génère → le FST valide → rejette et réessaie la morphologie invalide | Garantit la validité morphologique | Nécessite une infrastructure FST ; les boucles de retry ajoutent de la latence et du coût |
| **[Recherche dans le dictionnaire + LLM](/docs/tutorials/dictionary-augmented-llm)** | Forcer les termes connus d'un dictionnaire bilingue, laisser le LLM gérer le reste | Réduit les hallucinations pour les termes connus | La couverture du dictionnaire est toujours incomplète |
| **[Modèle affiné](/docs/tutorials/fine-tuned-model)** | Affiner un modèle ouvert (Llama, Mistral) sur du texte parallèle — juste pas sur les données d'évaluation | Potentiellement la plus haute qualité | Nécessite un corpus parallèle (rare) ; coûteux ; risque de surapprentissage |
| **[Modèles chaînés](/docs/tutorials/chained-models)** | Le modèle A génère une traduction brute → Le modèle B post-édite → Le modèle C note | Peut combiner les forces des spécialistes | Complexe ; lent ; coûteux |
| **[Hybride basé sur des règles + LLM](/docs/tutorials/rule-based-hybrid)** | Utiliser des règles linguistiques pour les motifs connus, LLM pour tout le reste | Précis où les règles s'appliquent | Nécessite une expertise linguistique approfondie |
| **[Augmentation par rétrotraduction](/docs/tutorials/back-translation)** | Générer des données parallèles synthétiques en traduisant cri→anglais, puis en entraînant sur l'inverse | Élargit les données d'entraînement à bon marché | Amplifie les erreurs du modèle existant |
| **[Approche évolutionnaire](/docs/tutorials/evolutionary-approach)** | Générer des traductions candidates, les noter, muter les meilleurs performeurs, répéter | Peut découvrir des solutions nouvelles ; parallélisable | Coûteux en calcul ; nécessite une bonne fonction de fitness |
| **[Traduction partielle](/docs/tutorials/partial-translation)** | Traduire manuellement un échantillon représentatif, prouver que votre méthode correspond à votre style sur celui-ci, puis traduire automatiquement le reste en masse | Combine la qualité humaine avec l'échelle machine | Nécessite un effort humain initial |
| **JSON manuel / notation d'examen** | Construire à la main un fichier JSON d'ensemble de données pour tester les réponses des étudiants sur un examen de langue, ou noter un lot de traductions humaines par rapport à un standard or | Zéro ML requis ; fonctionne pour l'éducation et l'assurance qualité | Ne s'adapte pas aux besoins de traduction continus |

### C'est juste du JSON

Le harnais prend du JSON en entrée et produit du JSON en sortie. Le [format d'ensemble de données](/docs/leaderboard/datasets) est simple :

```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

Vous pouvez construire cela à la main. Vous pouvez l'exporter d'une feuille de calcul. Vous pouvez le générer à partir d'un corpus. Un professeur de langue pourrait l'utiliser pour noter les traductions des étudiants. Une agence de traduction pourrait l'utiliser pour évaluer les pigistes. Un laboratoire de recherche pourrait l'utiliser pour comparer les architectures de modèles. Le harnais ne se soucie pas d'où provient le JSON — il le note simplement.

Et parce que le cadre de déploiement en production prend la même interface de plugin, une méthode qui obtient un bon score dans le harnais se déploie sur votre site Web avec un changement de configuration. **Prouvez-le et utilisez-le.**

Les possibilités sont véritablement infinies. **Si vous avez une idée, construisez-la, exécutez le harnais et soumettez vos scores.**

---

## Comment champollion s'intègre

champollion fournit la couche d'infrastructure — vous apportez la méthode.

### Le système d'accompagnement

La méthode `llm-coached` de champollion vous permet d'injecter directement les connaissances linguistiques dans l'invite du LLM :

```json title=".champollion/coaching/crk.json"
{
  "grammar_rules": [
    "Plains Cree is polysynthetic — a single word can express what English needs a full sentence for",
    "Animate/inanimate noun distinction affects verb conjugation, demonstratives, and pluralization",
    "Use SRO (Standard Roman Orthography) as the working script — syllabic conversion is handled by the deterministic converter",
    "Obviation: when two third-person referents appear, the less salient one takes obviative marking (-a suffix on nouns, -iyiwa on verbs)"
  ],
  "dictionary": {
    "home": "kīwēwin",
    "settings": "isi-nākatohkēwin",
    "search": "nānātawāpahtam",
    "welcome": "tānisi",
    "dashboard": "kīskinwahamākēwin-māsinahikan"
  },
  "style_notes": "Use formal register appropriate for educational and community contexts. Preserve English technical terms in parentheses when no Cree equivalent exists or is widely accepted."
}
```

Les données d'accompagnement sont injectées dans chaque invite LLM pour la paire `en:crk`, donnant au modèle un contexte linguistique structuré qu'il n'aurait pas autrement. Voir [Données d'accompagnement](https://champollion.dev/docs/concepts/coaching-data) pour la spécification complète.

### Registres

Le registre est la partie de l'invite système qui oriente le ton, la formalité et les conventions orthographiques. champollion est livré avec un registre du cri des Plaines :

```
nêhiyawêwin (Plains Cree). Use SRO (Standard Roman Orthography) as the working
script. Output will be converted to Syllabics via deterministic converter.
Professional register appropriate for educational and community contexts.
```

Vous pouvez remplacer ceci dans votre configuration pour expérimenter différentes stratégies d'incitation :

```json title="champollion.config.json"
{
  "languages": {
    "crk": {
      "register": "Casual Plains Cree (Y-dialect). Use SRO. Prefer everyday vocabulary over formal or archaic terms. Address the reader directly."
    }
  }
}
```

Différents registres produisent différents styles de traduction — et différents scores sur le classement. Chaque soumission enregistre le registre exact et l'invite système utilisée (sous forme de hachage SHA-256 dans la [carte d'exécution](/docs/specifications/run-card)), de sorte que les expériences sont reproductibles.

### Conversion de script

Le cri des Plaines s'écrit dans deux scripts : **Orthographe romane standard (SRO)** et **Syllabiques autochtones canadiennes**. Le pipeline de champollion :

1. Le LLM traduit en SRO (basé sur le latin, que les LLM gèrent mieux)
2. La porte de qualité valide la sortie SRO
3. Un convertisseur déterministe transforme SRO → Syllabiques
4. Le texte converti est écrit sur le disque

Le convertisseur gère tous les diacritiques SRO (ê, î, ô, â pour les voyelles longues) et les mappe aux caractères syllabiques corrects. Voir [Convertisseurs de script](https://champollion.dev/docs/concepts/script-converters) pour les détails techniques.

### La boucle d'évaluation

Le [harnais d'évaluation](/docs/specifications/harness) exécute votre méthode par rapport à l'ensemble de données d'évaluation et produit une [carte d'exécution](/docs/specifications/run-card) notée :

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install -e .

# Run a baseline experiment
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v7

# Run with FST validation (if you have an FST binary)
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --fst-analyzer ./bin/crk-analyzer \
  --condition fst-gated-v1
```

Le drapeau `--condition` est une étiquette que vous choisissez. Il apparaît sur le classement pour que les gens puissent voir quelle stratégie d'incitation vous avez utilisée. Le harnais enregistre l'invite système complète dans la carte d'exécution, de sorte que votre approche exacte est reproductible.

:::tip Expérimentez librement, soumettez votre meilleur
Le harnais est conçu pour une itération rapide. Exécutez des dizaines d'expériences avec différents modèles, données d'accompagnement, registres et conditions. Soumettez au classement uniquement lorsque vous avez quelque chose dont vous êtes fier.
:::

---

## Principes OCAP

champollion est conçu pour soutenir la souveraineté des données autochtones. Les [principes OCAP](https://fnigc.ca/ocap-training/) (Propriété, Contrôle, Accès, Possession) guident notre approche de la technologie linguistique pour les communautés autochtones :

| Principe | Comment champollion le soutient |
|----------|-------------------------------|
| **Propriété** | Les communautés linguistiques possèdent leurs données linguistiques. champollion n'appelle jamais à la maison ni ne transmet les données à nos serveurs |
| **Contrôle** | La [méthode API](https://champollion.dev/docs/guides/serving-a-method) permet aux communautés d'héberger leur propre pipeline de traduction — nous fournissons l'interface, elles contrôlent l'implémentation |
| **Accès** | Les communautés décident qui peut utiliser leur méthode. L'API peut être protégée par authentification |
| **Possession** | Toutes les données de traduction restent dans le système de fichiers de votre projet. Le [système de provenance](https://champollion.dev/docs/concepts/security) suit d'où provient chaque traduction |

L'architecture de plugin signifie qu'une communauté peut construire une méthode qui incorpore en interne des connaissances sacrées ou restreintes, exposer uniquement l'API de traduction et maintenir le contrôle total sur ses ressources linguistiques.

---

## La vision : ce qui vient ensuite

Le cri des Plaines est la première cible. Une fois que le pipeline est validé et que la communauté est satisfaite de la qualité, la même architecture s'étend à d'autres langues polysynthétiques disposant d'une infrastructure FST :

- **Autres langues algonquiennes** : cri des bois, cri des marais, ojibwé, pieds-noirs
- **Langues inuit** : inuktitut, inuinnaqtun (qui utilisent également des scripts syllabiques)
- **Autres familles linguistiques** : toute langue disposant d'un analyseur FST peut utiliser le pipeline avec porte FST

Le classement est limité à la paire linguistique. À mesure que de nouveaux ensembles de données d'évaluation sont contribués par les communautés linguistiques, de nouvelles pistes de classement s'ouvrent automatiquement.

**C'est une invitation ouverte.** Si vous travaillez avec une langue peu dotée en ressources — en tant que chercheur, membre de la communauté, étudiant ou simplement quelqu'un qui s'en soucie — champollion vous donne les outils pour construire quelque chose de réel, le mesurer honnêtement et le partager avec le monde. Le [Classement des méthodes](https://champollion.dev/leaderboard) attend votre soumission.

---

## Voir aussi

- **[Classement des méthodes](https://champollion.dev/leaderboard)** — soumettez vos scores et voyez comment les méthodes se comparent
- **[Évaluation de la traduction automatique](/docs/leaderboard/rules)** — ce qui fait une bonne méthode, ce qui est disqualifié
- **[Harnais d'évaluation](/docs/specifications/harness)** — comment exécuter des expériences
- **[Ensembles de données d'évaluation](/docs/leaderboard/datasets)** — EDTeKLA Dev v1 et FLORES+
- **[Données d'accompagnement](https://champollion.dev/docs/concepts/coaching-data)** — comment structurer les connaissances linguistiques pour le LLM
- **[Convertisseurs de script](https://champollion.dev/docs/concepts/script-converters)** — le pipeline SRO→Syllabiques
- **[Servir une méthode via API](https://champollion.dev/docs/guides/serving-a-method)** — héberger une traduction contrôlée par la communauté
- **[ALTLab](https://altlab.artsrn.ualberta.ca/)** — le Laboratoire de technologie linguistique de l'Alberta
- **[EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/)** — le groupe de recherche Technologie éducative, Connaissance et Langue
- **[Dictionnaire itwêwina](https://itwewina.altlab.app/)** — dictionnaire cri des Plaines–anglais alimenté par FST