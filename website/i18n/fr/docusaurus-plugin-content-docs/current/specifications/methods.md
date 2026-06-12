---
sidebar_position: 4
title: "Interface de méthode"
related:
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
    note: "Put this interface on the leaderboard"
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
    note: "A full method, built end-to-end"
---
# Interface de Méthode Partagée

> **Résumé exécutif.** Cette page spécifie le protocole `TranslationMethod` que toutes les méthodes Arena doivent implémenter, les six classes de méthodes (`raw-llm`, `coached-llm`, `pipeline`, `custom-plugin`, `api`, `human`), le format de plugin de méthode, et les **classes de dépendances** (S/O/A1/A2/X) qui déterminent si une méthode peut s'exécuter dans le bac à sable d'évaluation et se qualifier pour les prix. Toute approche qui implémente ce protocole peut être évaluée ; ce dont elle dépend détermine où elle peut concourir.

Le harnais d'évaluation et champollion partagent un concept commun de **méthode de traduction**. Une méthode est toute procédure qui prend du texte source et produit du texte traduit — qu'il s'agisse d'un appel LLM direct, d'un pipeline multi-étapes, d'une API tierce, ou d'un traducteur humain.

## Architecture

```
Method Plugin (v2 Spec)
├── method.json           ← Manifest (name, class, entry_point, dependencies, metadata)
├── method_card.json      ← Leaderboard description (what, not how)
├── pipeline.py           ← Python module implementing TranslationMethod
└── (optional helpers)    ← Additional Python modules
```

Chargé via `--method path/to/dir`. Le harnais ne découvre rien automatiquement.

## Deux Systèmes, Une Interface

| | Harnais d'Évaluation | champollion |
|---|---|---|
| **Langage** | Python | Node.js |
| **Point d'entrée** | `translate.py` | `translate.js` |
| **Interface** | protocole `TranslationMethod` | config `methodPlugin` |
| **Objectif** | Évaluation par lot avec notation | Localisation en direct en dev/CI |
| **Sortie** | Carte d'exécution avec métriques | Fichiers de locale traduits |

Une méthode qui supporte les deux systèmes fournit deux points d'entrée — un pour chaque runtime de langage. La **carte de méthode** est le pont : elle décrit la méthode dans un format que les deux systèmes comprennent.

## Carte de Méthode {#method-card}

Une carte de méthode décrit *ce qu'est* une méthode de traduction sans révéler les détails propriétaires comme l'invite système complète. Elle répond à :

- Quelle classe de méthode est-ce ? (LLM brut, LLM entraîné, pipeline, API, etc.)
- Quels outils utilise-t-elle ? (analyseur FST, dictionnaire, etc.)
- L'implémentation est-elle open source ?
- Quelles paires de langues supporte-t-elle ?

Consultez la [Spécification de Carte de Méthode](/docs/specifications/methods#method-card) pour le schéma JSON complet.

### Exemple

```json
{
  "method_id": "fst-gated-v8",
  "name": "FST-Gated Coached Translation v8",
  "class": "pipeline",
  "description": "LLM translation with morphological validation. Failed words are retried with FST feedback.",
  "author": "Curtis Forbes",
  "tools_used": ["HFST morphological analyzer", "Wolvengrey dictionary"],
  "open_source": false,
  "dependency_class": "A2",
  "supported_pairs": ["eng>crk"]
}
```

Le champ `dependency_class` résume ce dont la méthode a besoin pour s'exécuter et se transférer — voir [Validité de Méthode et Classes de Dépendances](#method-validity-and-dependency-classes) ci-dessous.

### Classes de Méthodes

| Classe | Description |
|-------|-------------|
| `raw-llm` | Appel LLM direct avec instruction minimale |
| `coached-llm` | LLM avec invite structurée, exemples, contraintes |
| `pipeline` | Pipeline multi-étapes avec composants déterministes |
| `custom-plugin` | Processus externe implémentant le protocole `TranslationMethod` |
| `api` | API de traduction tierce (Google Translate, DeepL, etc.) |
| `human` | Traduction humaine (pour établir des références) |

## Validité de Méthode et Classes de Dépendances {#method-validity-and-dependency-classes}

Une méthode n'est exécutable, et n'est transférable, que dans la mesure de sa dépendance la moins disponible. Deux mécanismes Arena dépendent de la connaissance exacte de ce dont une méthode a besoin :

1. **Évaluation en bac à sable** ([Spécification de Benchmark §8.2](/docs/specifications/benchmark)) — les scores de référence officiels proviennent d'un bac à sable dont la politique réseau est **refus par défaut**. Une méthode qui dépend silencieusement d'un service externe ne peut pas produire un score officiel.
2. **Transfert de prix** ([Spécification de Prix](/docs/specifications/prizes)) — les méthodes gagnantes de prix se transfèrent à l'organisation de gouvernance de la communauté linguistique. Une méthode qui regroupe du contenu que le soumetteur n'avait pas le droit d'inclure ne peut pas être transférée légalement. Le soumetteur doit détenir (ou se voir accorder) les droits sur tout ce qui se trouve dans la boîte.

Pour rendre les deux vérifications mécaniques plutôt qu'ad hoc, chaque méthode déclare une **classe de dépendance**, dérivée d'un **manifeste de dépendance** dans `method.json`.

> **Note sur la nomenclature.** *Classe de méthode* (§ci-dessus : `raw-llm`, `pipeline`, …) décrit *comment une méthode traduit*. *Classe de dépendance* (cette section) décrit *ce dont une méthode a besoin pour s'exécuter et se transférer*. Ce sont des axes indépendants : une méthode `pipeline` peut être de n'importe quelle classe de dépendance.

### Les Cinq Classes de Dépendances

| Classe | Nom | Définition | Exécutable en bac à sable ? | Admissible aux prix ? |
|-------|------|-----------|-------------------|-----------------|
| **S** | Autonome | Tout le code, les données, les modèles et les poids sont livrés dans le répertoire de la méthode, sous des licences qui permettent la redistribution et le transfert communautaire. | ✅ Oui, tel quel | ✅ Oui |
| **O** | Externe ouvert | Dépend d'artefacts hébergés en externe sous des licences ouvertes qui permettent la redistribution (y compris les licences copyleft telles que AGPL) — par exemple, un FST téléchargé au moment de l'installation. | ✅ Oui — les artefacts sont épinglés et **mis en miroir dans la soumission** | ✅ Oui, avec conditions de compatibilité de licence : les termes copyleft sont préservés lors du transfert, et la communauté reçoit les mêmes droits que la licence accorde à tous |
| **A1** | Dépendant d'API, substituable | Nécessite l'inférence LLM à l'exécution, où le modèle est une **configuration substituable** — n'importe quel modèle suffisamment capable peut être inséré. La valeur de la méthode réside dans ses invites, ses données d'entraînement et son code, pas dans le modèle d'un fournisseur particulier. | ⚠️ Uniquement via la **passerelle LLM** que la spécification de bac à sable définit (🔲 prévu — voir ci-dessous) | ⚠️ Conditionnel — voir ci-dessous |
| **A2** | Dépendant d'API, non-substituable | Nécessite des appels à l'exécution à une API de données ou de service externe qui ne peut pas être mise en miroir ou substituée — généralement parce que le contenu servi est propriétaire ou sans licence (par exemple, une API de dictionnaire dont le dictionnaire sous-jacent n'a pas de licence publique). | ❌ Non — la dépendance ne peut pas exister dans le bac à sable sans la permission du détenteur des droits | ❌ Pas tant que le détenteur des droits n'accorde pas les permissions d'inclusion en bac à sable **et** de transfert. Autorisé sur le classement ouvert (segment de développement) avec un drapeau **« dépendance externe »** visible |
| **X** | Fermé | Regroupe du contenu que le soumetteur n'a pas le droit de redistribuer — ensembles de données sans licence, contenu propriétaire raclé, composants incompatibles avec la licence. | ❌ | ❌ Inadmissible dans toutes les catégories. Regrouper du contenu sans droits est une violation de licence indépendamment de l'endroit où la méthode s'exécute |

**Classe effective.** La classe de dépendance d'une méthode est la classe *la plus restrictive* parmi toutes ses dépendances déclarées, dans l'ordre S < O < A1 < A2 < X. Un dictionnaire sans licence rend un pipeline autrement autonome de classe A2 (s'il est accédé à l'exécution) ou de classe X (s'il est regroupé sans droits).

### La Distinction A1/A2 : Substituabilité

La plupart des méthodes appellent des LLM. L'Arena ne prétend pas le contraire — mais elle distingue deux types très différents de dépendance d'API :

- **A1 (substituable) :** L'API fournit l'inférence LLM de base. L'identifiant du modèle est une configuration : la méthode doit s'exécuter de bout en bout contre n'importe quel point de terminaison d'inférence compatible, y compris un modèle de poids ouvert hébergé par la communauté. La qualité de sortie peut différer selon les modèles — c'est le risque du développeur, et les scores officiels sont liés au modèle épinglé utilisé dans l'évaluation. Une méthode qui dépend d'un **état côté fournisseur** (un fine-tune hébergé uniquement chez le fournisseur, des magasins de fichiers du fournisseur, des assistants spécifiques au fournisseur) n'est *pas* substituable : cet état ne peut pas être retiré, donc la dépendance est A2 sauf si les poids ou données sous-jacents sont inclus dans la soumission.
- **A2 (non-substituable) :** L'API sert quelque chose d'unique — généralement des données propriétaires ou sans licence. Aucun point de terminaison alternatif ne peut le fournir, et le contenu ne peut pas être mis en miroir dans le bac à sable sans la permission du détenteur des droits. La méthode fonctionne sur le classement ouvert (signalée), mais ne peut pas produire de scores de bac à sable officiels ou se qualifier pour les prix tant que les permissions n'existent pas.

**Ce qu'un transfert de prix A1 transmet réellement.** La communauté ne reçoit pas le modèle — personne ne peut transférer les poids d'Anthropic, Google ou OpenAI. Le transfert couvre la recette complète *autour* du modèle : toutes les invites, données d'entraînement, code de pipeline, logique de nouvelle tentative, configuration et exigences de modèle documentées. Parce que le modèle est substituable par construction, la communauté peut pointer la méthode transférée vers n'importe quel fournisseur qu'elle choisit — ou vers un modèle de poids ouvert sur son propre matériel — sans l'implication du développeur. La recette est possédée ; le moteur est loué et remplaçable.

### Manifeste de Dépendance (`method.json`)

Chaque méthode déclare ses dépendances dans le manifeste `method.json`. Chaque entrée enregistre ce qu'est l'artefact, d'où il provient, quelle licence le couvre et comment la méthode y accède :

```json
{
  "name": "FST-Gated Coached Translation v8",
  "method_id": "fst-gated-v8",
  "class": "pipeline",
  "entry_point": "pipeline:PipelineMethod",
  "supported_pairs": ["eng>crk"],
  "dependency_class": "A2",
  "dependencies": [
    {
      "id": "giellalt-lang-crk-fst",
      "kind": "software",
      "license": "AGPL-3.0-or-later",
      "access": "mirrored",
      "source": "https://github.com/giellalt/lang-crk",
      "pin": "sha256:3f1a…",
      "redistributable": true,
      "transferable": true
    },
    {
      "id": "llm-inference",
      "kind": "model",
      "license": "proprietary",
      "access": "gateway",
      "source": "openrouter:google/gemini-2.5-flash",
      "substitutable": true,
      "redistributable": false,
      "transferable": false,
      "notes": "Any compatible chat-completions endpoint works; the model slug is configuration."
    },
    {
      "id": "crk-dictionary-api",
      "kind": "service",
      "license": "none",
      "access": "external-api",
      "source": "https://itwewina.altlab.app/",
      "redistributable": false,
      "transferable": false,
      "notes": "Dictionary content has no public license; runtime lookups only. Class A2 until the rights holders grant permission."
    }
  ]
}
```

| Champ | Requis | Description |
|-------|----------|-------------|
| `id` | ✅ | Identifiant stable pour la dépendance |
| `kind` | ✅ | `data`, `model`, `software`, ou `service` |
| `license` | ✅ | Identifiant SPDX, `proprietary`, ou `none`. `none` signifie qu'aucune licence publique n'existe — traité comme tous droits réservés |
| `access` | ✅ | `bundled` (livré dans le répertoire de la méthode), `mirrored` (récupéré à l'installation, épinglé, vendorisé dans la soumission), `gateway` (inférence LLM à l'exécution via la passerelle d'évaluation), `external-api` (tout autre appel réseau à l'exécution) |
| `source` | ✅ | URL canonique ou identifiant `provider:slug` |
| `pin` | pour `mirrored` | Version, commit ou hash de contenu qui épingle l'artefact exact |
| `substitutable` | pour `gateway`/`external-api` | Si n'importe quel point de terminaison compatible peut servir cette dépendance |
| `redistributable` | ✅ | Si la licence permet de redistribuer l'artefact |
| `transferable` | ✅ | Si l'artefact (ou les droits sur celui-ci) peut se transférer à une communauté selon les termes de transfert de prix |
| `notes` | ❌ | Contexte libre |

**Dérivation de classe.** Chaque dépendance contribue une classe ; la `dependency_class` de la méthode est la plus restrictive :

| Profil de dépendance | Contribue |
|--------------------|-------------|
| `bundled` + la licence permet la redistribution et le transfert | S |
| `mirrored` + licence ouverte permettant la redistribution (copyleft inclus) | O |
| `gateway` + `substitutable: true` (inférence LLM) | A1 |
| `external-api`, ou `gateway` avec `substitutable: false` | A2 |
| `bundled` + `license: none` ou licence incompatible avec la redistribution | X |

La `dependency_class` déclarée doit correspondre à la classe que le harnais dérive du manifeste. Une non-correspondance est une erreur de validation.

Une méthode sans **aucune** dépendance externe déclare `"dependency_class": "S"` et `"dependencies": []`. Le tableau vide est une affirmation positive, auditée comme toute autre.

### Comment la Validité Est Vérifiée

Trois couches, du moins cher au plus autoritaire :

1. **Audit de manifeste.** Le harnais dérive la classe effective du manifeste et rejette les non-correspondances. Les examinateurs vérifient chaque dépendance déclarée par rapport à sa licence déclarée et sa source — une dépendance déclarée `redistributable: true` dont la licence en amont dit le contraire échoue l'examen.
2. **Analyse statique.** Le code soumis est analysé pour les appels réseau, les téléchargements dynamiques et l'accès au système de fichiers que le manifeste ne tient pas compte. Une dépendance *non déclarée* trouvée lors de l'examen est motif de rejet indépendamment de la classe qu'elle aurait été — le manifeste doit être complet, pas seulement exact.
3. **Politique réseau du bac à sable.** La spécification du bac à sable exige une **sortie refus par défaut** : les conteneurs de méthode n'obtiennent aucun accès réseau sauf si un chemin est explicitement autorisé. Le seul chemin de sortie que la spécification définit est la **passerelle LLM** — un proxy d'inférence exploité par l'infrastructure d'évaluation, limité à une liste d'autorisation explicite de modèles épinglés, avec chaque demande et réponse enregistrées pour audit post-exécution. Tout ce qui n'est pas sur la liste d'autorisation échoue au niveau réseau, pas au niveau politique. Consultez [Spécification de Benchmark §8.6](/docs/specifications/benchmark) pour la politique réseau et la conception de la passerelle.

> 🔲 **Prévu.** Le bac à sable et sa passerelle LLM sont spécifiés mais pas encore construits. Jusqu'à ce que la passerelle soit opérationnelle, seules les méthodes de classe S et O peuvent être évaluées dans le bac à sable ; les méthodes de classe A1 sont admissibles aux prix *en principe* mais ne peuvent pas encore produire de scores de référence officiels. Cette page décrit ce que la spécification exige, pas ce qui s'exécute actuellement.

### Affichage du Classement

- Le classement affiche la classe de dépendance de chaque méthode à côté de son badge de classe de méthode.
- Les méthodes de classe A2 sur le classement ouvert portent un drapeau **« dépendance externe »** visible : leurs scores dépendent d'un service tiers qui peut changer ou disparaître, et elles ne sont actuellement pas admissibles aux prix.
- Les méthodes de classe X ne sont pas listées.

## Harnais d'Évaluation : Protocole TranslationMethod {#eval-harness-translationmethod-protocol}

Le harnais d'évaluation utilise le typage structurel de Python (`Protocol`) pour les plugins. Toute classe avec la bonne signature de méthode fonctionne — aucun héritage requis :

```python
class MyMethod:
    async def translate(self, entries: list[dict], config: RunConfig) -> list[dict]:
        results = []
        for entry in entries:
            translation = await self.do_translation(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translation,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "error": None,
                "tool_calls": [],
                "tool_call_count": 0,
                "metadata": {},
            })
        return results
```

Consultez le [Protocole de Plugin](/docs/specifications/methods#eval-harness-translationmethod-protocol) pour la documentation complète incluant des exemples de wrapper pour les méthodes non-Python.

## champollion : Config methodPlugin

Dans champollion, les méthodes sont enregistrées par paire de langues dans `champollion.config.json` :

```json
{
  "version": 3,
  "pairs": {
    "en:crk": {
      "methodPlugin": "crk-coached-v1"
    }
  }
}
```

Consultez la [Spécification de Plugin](https://champollion.dev/docs/reference/plugin-spec) pour l'interface côté champollion.

## Intégration du Classement

Quand une carte de méthode est attachée à une exécution (via `--method-card`), elle est intégrée dans la carte d'exécution et affichée sur le classement :

```bash
# Run with method card attached
mt-eval run \
  --method path/to/my-method \
  --corpus data/edtekla-dev-v1.json \
  --method-card method_card.json

# Publish to the leaderboard
mt-eval publish eval/logs/harness/your-run-card.json
```

Si aucune `--method-card` n'a été fournie, `mt-eval publish` lance un assistant interactif qui vous guide dans la description de votre méthode.

Le classement affiche :
- **Badge de classe** — indicateur visuel (par exemple, « pipeline », « coached-llm »)
- **Classe de dépendance** — S/O/A1/A2 (voir [Validité de Méthode et Classes de Dépendances](#method-validity-and-dependency-classes)) ; les méthodes A2 portent un drapeau « dépendance externe »
- **Nom de la méthode** — de la carte de méthode
- **Outils utilisés** — listés de la carte de méthode
- **Indicateur open source**

Quand aucune carte de méthode n'est attachée, le classement affiche la configuration native du harnais (modèle, version d'invite, température, outils activés).

:::danger NE PAS ENTRAÎNER sur les données d'évaluation
Les méthodes dont le processus de développement a inclus l'exposition à l'ensemble de données d'évaluation — comme données d'entraînement, exemples few-shot, entrées de dictionnaire ou matériel d'ajustement d'invite — seront **disqualifiées** du classement. Consultez [Évaluation MT](/docs/leaderboard/rules) pour ce qui distingue une bonne méthode d'une mauvaise.
:::

---

## Voir Aussi

- [Évaluation MT](/docs/leaderboard/rules) — aperçu, valeur du classement et conseils sur les bonnes/mauvaises méthodes
- [Harnais d'Évaluation](/docs/specifications/harness) — comment exécuter les évaluations
- [Ensembles de Données d'Évaluation](/docs/leaderboard/datasets) — ensembles de données disponibles (EDTeKLA, FLORES+)
- [Spécification de Carte d'Exécution](/docs/specifications/run-card) — le schéma JSON de la carte d'exécution
- [Spécification de Plugin](https://champollion.dev/docs/reference/plugin-spec) — interface de plugin côté champollion
- [Classement de Méthodes](https://champollion.dev/leaderboard) — scores de benchmark en direct
- [Spécification de Benchmark](/docs/specifications/benchmark) — protocole d'évaluation, format de corpus, schéma de carte d'exécution
- [Spécification de Notation](/docs/specifications/scoring) — SSOT pour les métriques, poids composites et niveaux de qualité