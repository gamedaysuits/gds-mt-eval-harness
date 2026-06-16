---
sidebar_position: 7
title: "Tests de Significativité Statistique"
slug: '/specifications/significance'
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The scores these tests protect"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "Where significance gates what ranks"
---
# Tests de Signification Statistique — Spécification d'Implémentation

> **Base de code cible** : `arena` (spécifiquement `tester.py` et `compare.py`)
> **Objectif** : Permettre aux chercheurs de déterminer si la différence entre deux exécutions d'évaluation est statistiquement significative ou simplement du bruit.
> **Priorité** : Élevée — il s'agit de la fonctionnalité manquante la plus importante pour des résultats publiables.

---

## Pourquoi Cela Importe

Lors de la comparaison de deux exécutions (par exemple, Gemini 3.1 Pro chrF++ 42,96 vs Claude Sonnet chrF++ 41,80 sur 92 entrées), nous ne pouvons actuellement pas dire si la différence est réelle ou du bruit. Avec seulement ~92 entrées de test, la variation aléatoire peut facilement produire des variations de 1 à 2 points. Les experts demanderont des tests de signification. Nous devons répondre.

---

## Algorithme : Rééchantillonnage Bootstrap Appairé

Il s'agit de la méthode standard utilisée par SacreBLEU, MT-Lens et les tâches partagées WMT. Elle est bien comprise par les chercheurs en traduction automatique et produit des résultats en lesquels ils ont confiance.

### Fonctionnement

Étant donné deux systèmes A et B évalués sur les mêmes N entrées de test :

1. Calculer la différence métrique réelle : `Δ = metric(A) - metric(B)`
2. Répéter `n_bootstrap` fois (par défaut 1000) :
   a. Échantillonner N entrées **avec remplacement** à partir de l'ensemble de test partagé
   b. Calculer la métrique pour A et B sur cet échantillon bootstrap
   c. Calculer la différence bootstrap : `Δ_boot = metric(A_boot) - metric(B_boot)`
3. La p-valeur = fraction des échantillons bootstrap où `Δ_boot` a le signe opposé à `Δ`
4. Si p-valeur < α (par défaut 0,05), la différence est statistiquement significative

### Propriétés Clés

- **Appairé** : Les deux systèmes sont évalués sur le même échantillon bootstrap, préservant la corrélation au niveau des entrées
- **Non-paramétrique** : Aucune hypothèse sur la distribution des scores
- **Standard** : C'est exactement ce que `sacrebleu --paired-bs` fait en arrière-plan

---

## Important : sacrebleu est une Dépendance Obligatoire

sacrebleu est actuellement listé sous `[project.optional-dependencies]` et protégé par `try/except` dans `tester.py`. **Cela devrait être modifié.** Un outil d'évaluation de traduction automatique qui ne peut pas calculer chrF++ ou BLEU n'est pas un outil d'évaluation de traduction automatique. sacrebleu devrait être :

1. Déplacé vers `[project.dependencies]` dans `pyproject.toml`
2. Importé directement dans `tester.py` (supprimer la protection `try/except HAS_SACREBLEU`)
3. Importé directement dans le nouveau module `significance.py`

Les chemins conditionnels `HAS_SACREBLEU` dans `tester.py` doivent être supprimés — ils rendent le code plus complexe pour un scénario (exécution sans sacrebleu) qui ne devrait pas être pris en charge.

---

## Plan d'Implémentation

### 1. Promouvoir sacrebleu en dépendance obligatoire

**`pyproject.toml`** : Déplacer `sacrebleu>=2.3` de `[project.optional-dependencies].metrics` vers `[project.dependencies]`.

**`tester.py`** : Remplacer :
```python
# Optional: sacrebleu for chrF++ and BLEU
try:
    from sacrebleu.metrics import CHRF, BLEU
    HAS_SACREBLEU = True
except ImportError:
    HAS_SACREBLEU = False
```
Par :
```python
from sacrebleu.metrics import CHRF, BLEU
```

Supprimer toutes les protections `if HAS_SACREBLEU:` dans `tester.py`.

---

### 2. Nouveau module : `mt_eval_harness/significance.py`

```python
"""
Statistical significance testing via paired bootstrap resampling.

Standard method used by WMT shared tasks, SacreBLEU, and MT-Lens.
Compares two runs on the same corpus to determine if the performance
difference is statistically significant.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from sacrebleu.metrics import CHRF, BLEU


@dataclass
class SignificanceResult:
    """Result of a paired bootstrap significance test."""
    metric_name: str           # e.g., "corpus_chrf", "exact_match_rate"
    system_a_score: float      # Score for system A
    system_b_score: float      # Score for system B
    delta: float               # A - B
    p_value: float             # Two-sided p-value
    n_bootstrap: int           # Number of bootstrap iterations
    confidence_level: float    # 1 - alpha
    significant: bool          # p_value < alpha
    winner: str | None         # "A", "B", or None if not significant
    ci_lower: float            # Lower bound of 95% CI on the delta
    ci_upper: float            # Upper bound of 95% CI on the delta


def paired_bootstrap(
    entries_a: list[dict],
    entries_b: list[dict],
    metric_fn: callable,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 12345,
    metric_name: str = "metric",
) -> SignificanceResult:
    """Run paired bootstrap resampling significance test.

    Args:
        entries_a: Per-entry results from system A (from TestReport["entries"])
        entries_b: Per-entry results from system B (must be same length, same IDs)
        metric_fn: Function(list[dict]) -> float that computes the corpus-level
                   metric from a list of entry dicts. Must handle the entry format
                   from TestReport.
        n_bootstrap: Number of bootstrap iterations (1000 is standard)
        alpha: Significance level (0.05 = 95% confidence)
        seed: RNG seed for reproducibility (12345 matches SacreBLEU default)
        metric_name: Human-readable name for the metric being tested

    Returns:
        SignificanceResult with all fields populated.

    Raises:
        ValueError: If entries_a and entries_b have different lengths or IDs.
    """
    ...
```

### 3. Fonctions de métriques intégrées

```python
def exact_match_rate(entries: list[dict]) -> float:
    """Compute exact match rate from a list of entry dicts."""
    non_error = [e for e in entries if not e.get("error")]
    if not non_error:
        return 0.0
    exact = sum(1 for e in non_error if e.get("exact_match"))
    return exact / len(non_error)


def corpus_chrf(entries: list[dict]) -> float:
    """Compute corpus-level chrF++ from a list of entry dicts."""
    chrf = CHRF(word_order=2)
    refs = [e["expected"] for e in entries if e.get("expected", "").strip()]
    hyps = [e["predicted"] if e.get("predicted", "").strip() else "EMPTY"
            for e in entries if e.get("expected", "").strip()]
    if not refs:
        return 0.0
    return chrf.corpus_score(hyps, [refs]).score


def corpus_bleu(entries: list[dict]) -> float:
    """Compute corpus-level BLEU from a list of entry dicts."""
    bleu = BLEU()
    refs = [e["expected"] for e in entries if e.get("expected", "").strip()]
    hyps = [e["predicted"] if e.get("predicted", "").strip() else "EMPTY"
            for e in entries if e.get("expected", "").strip()]
    if not refs:
        return 0.0
    return bleu.corpus_score(hyps, [refs]).score
```

### 4. Intégration dans `compare.py`

Le `compare.py` existant effectue déjà une comparaison côte à côte de plusieurs TestReports. Ajouter les tests de signification :

```python
# In compare_reports(), after computing deltas:
if len(reports) == 2:
    sig_results = run_significance_tests(reports[0], reports[1])
    comparison["significance"] = [asdict(r) for r in sig_results]
```

Lors de la comparaison de plus de 2 rapports, exécuter des tests de signification par paires pour toutes les paires. Stocker les résultats indexés par `"(run_a_id, run_b_id)"`.

### 5. Intégration CLI

Ajouter un drapeau `--significance` à `mt-eval compare` :

```bash
# Compare two runs with significance testing
mt-eval compare report_a.json report_b.json --significance

# Custom bootstrap count
mt-eval compare report_a.json report_b.json --significance --n-bootstrap 5000
```

Envisager également une commande autonome :

```bash
# Quick significance check between two reports
mt-eval significance report_a.json report_b.json
```

### 6. Format de sortie

**Sortie console :**
```
  Significance Tests (paired bootstrap, n=1000, α=0.05):

  Metric              A         B       Δ      p-value  Sig?
  ─────────────────── ──────── ──────── ─────── ──────── ────
  corpus_chrf         42.96    41.80    +1.16   0.142    No
  exact_match_rate     0.198    0.185   +0.013  0.381    No
  corpus_bleu          6.80     3.81    +2.99   0.018    Yes *
```

**Sortie JSON** (ajoutée au rapport de comparaison) :
```json
{
  "significance": [
    {
      "metric_name": "corpus_chrf",
      "system_a_score": 42.96,
      "system_b_score": 41.80,
      "delta": 1.16,
      "p_value": 0.142,
      "n_bootstrap": 1000,
      "confidence_level": 0.95,
      "significant": false,
      "winner": null,
      "ci_lower": -0.85,
      "ci_upper": 3.12
    }
  ]
}
```

### 7. Intégration du tableau de bord

Si les données de signification sont présentes dans le JSON de comparaison, le tableau de bord devrait les afficher. Afficher une ligne dans le tableau de comparaison avec des indicateurs de signification (par exemple, `*` pour p < 0,05, `**` pour p < 0,01). Il s'agit d'une fonctionnalité optionnelle, non bloquante.

---

## Cas Limites et Validation

1. **Entrées non appariées** : Les deux TestReports doivent avoir les mêmes identifiants d'entrée. S'ils ne les ont pas (par exemple, l'un s'est exécuté sur un sous-ensemble), tester la signification uniquement sur l'intersection. Avertir à propos des entrées exclues.

2. **Trop peu d'entrées** : Si N < 10, avertir que les tests de signification ne sont pas fiables avec si peu d'entrées. Les exécuter quand même, mais imprimer l'avertissement.

3. **Scores identiques** : Si les deux systèmes produisent des résultats identiques au niveau des entrées, p_value devrait être 1,0 (aucune différence du tout).

4. **Métriques de plugin** : Le module de signification devrait également tester toute métrique de plugin qui apparaît dans les DEUX rapports. Utiliser une approche générique : si les deux rapports ont `plugin_metrics.crk_fst_validity.avg_fst_validity`, la tester.

5. **Reproductibilité** : La graine RNG doit être enregistrée dans la sortie pour que les résultats soient exactement reproductibles. Par défaut 12345 (correspondant à la convention SacreBLEU).

---

## Ce qu'il NE FAUT PAS Construire

- **Pas de signification COMET séparée** : COMET est maintenant intégré en tant que métrique de corpus via `metrics_comet.py`. Les IC bootstrap sont calculés sur les scores COMET tout comme chrF++/BLEU. Pour la signification COMET par paires entre deux systèmes, utiliser `comet-compare` d'Unbabel.
- **Pas d'analyse bayésienne** : S'en tenir au bootstrap fréquentiste. C'est ce que la communauté de traduction automatique attend et comprend.
- **Pas de correction multi-test** : Lors du test de plusieurs métriques, ne pas appliquer de corrections Bonferroni ou similaires. La convention en évaluation de traduction automatique est de rapporter les p-valeurs brutes par métrique et de laisser le lecteur interpréter.

---

## Fichiers à Modifier

| Fichier | Modification |
|---|---|
| `pyproject.toml` | Déplacer sacrebleu de dépendance optionnelle à obligatoire |
| `mt_eval_harness/tester.py` | Supprimer les protections `HAS_SACREBLEU`, importation directe |
| `mt_eval_harness/significance.py` | **[NOUVEAU]** Implémentation principale |
| `mt_eval_harness/__init__.py` | Exporter `SignificanceResult`, `paired_bootstrap` |
| `mt_eval_harness/compare.py` | Intégrer les tests de signification dans la comparaison de rapports |
| `mt_eval_harness/cli.py` | Ajouter les drapeaux `--significance` et `--n-bootstrap` |
| `mt_eval_harness/dashboard.py` | Afficher la signification dans le tableau de comparaison (optionnel) |
| `tests/test_significance.py` | **[NOUVEAU]** Tests unitaires |

---

## Exigences de Test

1. **Déterministe avec graine** : Mêmes entrées + même graine = même p-valeur, à chaque fois
2. **Test de réponse connue** : Deux ensembles de résultats identiques → p_value = 1,0
3. **Test de signification connue** : Construire deux ensembles de résultats où l'un est clairement meilleur (par exemple, tous les correspondances exactes vs tous les échecs) → p_value ≈ 0,0
4. **Identifiants non appariés** : Devrait lever ValueError ou avertir et calculer sur l'intersection
5. **Entrées vides** : Devrait gérer correctement (retourner p_value = 1,0 ou lever)

---

## Intervalles de Confiance (Fonctionnalité Complémentaire)

> **Statut** : ✅ IMPLÉMENTÉ dans `confidence.py`

Les intervalles de confiance (IC) répondent à une question différente des tests de signification :

- **Test de signification** (`significance.py`) : « La différence entre le système A et le système B est-elle réelle ? »
- **Intervalles de confiance** (`confidence.py`) : « Quelle est l'incertitude sur le score de ce système en lui-même ? »

### Implémentation : `confidence.py`

Utilise la même méthode de rééchantillonnage bootstrap par percentile que les tests de signification :

| Paramètre | Valeur | Justification |
|---|---|---|
| `n_bootstrap` | 1000 | Défaut SacreBLEU, convention WMT 2024 |
| `seed` | 12345 | Graine par défaut SacreBLEU pour la reproductibilité |
| `alpha` | 0,05 | Niveau de confiance standard de 95 % |
| Méthode | Bootstrap par percentile | Koehn (2004), Efron (1979) |

### Quelles Métriques Obtiennent des IC

Toutes les métriques au niveau du corpus calculées par l'outil :
- `corpus_chrf` (score chrF++)
- `corpus_bleu` (score BLEU)
- `exact_match_rate` (0,0–1,0)

### Drapeaux CLI

```bash
# Default: CIs are computed automatically
mt-eval test run_log.json

# Skip CI computation (faster, for quick iteration)
mt-eval test run_log.json --no-ci

# More bootstrap iterations (more precise, slower)
mt-eval test run_log.json --n-bootstrap-ci 2000
```

### Avertissement pour Petit Échantillon

Quand N < 30 entrées, le module émet un avertissement que les IC peuvent avoir une couverture médiocre. Le bootstrap ne peut pas créer d'information absente de l'échantillon — avec très peu d'entrées, les intervalles seront larges, reflétant correctement l'incertitude élevée.

### Intégration COMET

COMET (`metrics_comet.py`) est maintenant intégré en tant que métrique de première classe :
- Modèle : `Unbabel/wmt22-comet-da` (modèle de référence gagnant WMT 2022)
- Calculé automatiquement quand `unbabel-comet` est installé
- Scores par entrée stockés dans les entrées TestReport
- Détection de langue peu dotée via table de couverture XLM-R
- Dépendance optionnelle : `pip install mt-eval-harness[comet]`

### Migration Supabase

Nouvelles colonnes ajoutées à la table `run_cards` :
- `comet_score` (FLOAT8, nullable)
- `corpus_bleu` (FLOAT8, nullable)
- `chrf_ci_lower` / `chrf_ci_upper` (FLOAT8, nullable)
- `exact_match_ci_lower` / `exact_match_ci_upper` (FLOAT8, nullable)

Voir `migrations/001_add_comet_and_ci_columns.sql` pour le script de migration.