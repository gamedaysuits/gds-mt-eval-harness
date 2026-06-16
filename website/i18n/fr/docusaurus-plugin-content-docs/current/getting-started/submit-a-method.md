---
sidebar_position: 1
title: "Soumettre une méthode"
related:
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
    note: "The contract your method implements"
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
    note: "What every published run must disclose"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
    note: "The fastest first method to submit"
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
---
# Soumettre une méthode

> **Résumé exécutif.** Un guide pas à pas pour soumettre votre première exécution de benchmark au classement. Clonez le harnais, exécutez-le sur un ensemble de données, examinez votre carte d'exécution et soumettez. Prend 10 minutes si vous disposez d'une clé API.

Ce guide vous accompagne dans la soumission de votre première exécution de benchmark au classement de MT Eval Arena.

---

## Prérequis

- **Python 3.10+**
- **Une clé API OpenRouter** (ou équivalent pour votre fournisseur de modèle)
- **Une méthode de traduction** — tout ce qui produit des traductions à partir d'un texte source

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## Étape 1 : Exécuter le harnais

Le harnais évalue votre méthode par rapport à un ensemble de données standardisé :

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| Drapeau | Fonction |
|---|---|
| `--corpus` | Chemin d'accès au corpus d'évaluation (`.json`, `.jsonl`, `.tsv`) |
| `--model` | Slug du modèle — alias court (p. ex. `gemini-pro`) ou identifiant OpenRouter complet |
| `--condition` | Étiquette de votre méthode (apparaît sur le classement) |
| `--temperature` | Température d'échantillonnage (plus bas = plus déterministe) |
| `--fst-retries` | Optionnel : nombre de tentatives de relance FST |
| `--submit` | Soumettre automatiquement la carte d'exécution au classement |

Le harnais produit une **carte d'exécution** — un fichier JSON autonome contenant vos scores, le hash de l'ensemble de données, le slug du modèle et une empreinte cryptographique reliant les résultats à la configuration exacte de l'expérience.

---

## Étape 2 : Examiner votre carte d'exécution

Les cartes d'exécution sont enregistrées dans `results/`. Inspectez la vôtre avant de soumettre :

```bash
cat results/your-run-card.json | python -m json.tool
```

Champs clés à vérifier :
- `scores.chrf_plus_plus` — votre métrique de qualité principale
- `scores.exact_match_rate` — proportion de traductions parfaites
- `scores.fst_acceptance_rate` — validité morphologique (si FST a été utilisé)
- `totals.total_cost_usd` — le coût de l'exécution
- `fingerprint` — le hash de reproductibilité de l'expérience

Consultez la [Spécification de la carte d'exécution](/docs/specifications/run-card) pour le schéma complet.

---

## Étape 3 : Soumettre

### Soumission automatique

Si vous avez transmis `--submit` lors de l'exécution du harnais, votre carte d'exécution a déjà été téléchargée.

### Soumission manuelle

Soumettez n'importe quelle carte d'exécution via l'API :

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

Ou téléchargez via l'[interface du classement](https://champollion.dev/leaderboard).

---

## Étapes suivantes

1. Votre soumission est validée (hash de l'ensemble de données, intégrité de la carte d'exécution)
2. Les résultats apparaissent sur le classement en tant que **Auto-évalué** (niveau de confiance 1)
3. Pour obtenir le statut **GDS Verified**, soumettez votre méthode en tant que plugin installable afin que les responsables puissent reproduire vos résultats
4. Pour les méthodes de langues autochtones : si votre méthode atteint le sommet, le [processus de transfert de propriété](/docs/sovereignty/ownership-transfer) commence

---

## Voir aussi

- [Utilisation du harnais](/docs/specifications/harness) — référence CLI complète
- [Règles du classement](/docs/leaderboard/rules) — critères de soumission et politiques anti-triche
- [Construire une méthode](/docs/specifications/methods) — le protocole TranslationMethod
- [Ensembles de données](/docs/leaderboard/datasets) — ensembles de données d'évaluation disponibles