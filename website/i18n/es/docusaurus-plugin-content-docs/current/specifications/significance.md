---
sidebar_position: 7
title: "Pruebas de Significancia Estadística"
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
# Pruebas de Significancia Estadística — Especificación de Implementación

> **Codebase objetivo**: `arena` (específicamente `tester.py` y `compare.py`)
> **Propósito**: Permitir que los investigadores determinen si la diferencia entre dos ejecuciones de evaluación es estadísticamente significativa o solo ruido.
> **Prioridad**: Alta — esta es la característica faltante más importante para resultados publicables.

---

## Por Qué Esto Es Importante

Al comparar dos ejecuciones (p. ej., Gemini 3.1 Pro chrF++ 42.96 vs Claude Sonnet chrF++ 41.80 en 92 entradas), actualmente no podemos determinar si la diferencia es real o ruido. Con solo ~92 entradas de prueba, la variación aleatoria puede producir fácilmente cambios de 1-2 puntos. Los expertos solicitarán pruebas de significancia. Necesitamos responder.

---

## Algoritmo: Remuestreo Bootstrap Pareado

Este es el método estándar utilizado por SacreBLEU, MT-Lens y las tareas compartidas de WMT. Es bien comprendido por investigadores de traducción automática y produce resultados en los que confían.

### Cómo Funciona

Dados dos sistemas A y B evaluados en las mismas N entradas de prueba:

1. Calcule la diferencia métrica real: `Δ = metric(A) - metric(B)`
2. Repita `n_bootstrap` veces (predeterminado 1000):
   a. Muestree N entradas **con reemplazo** del conjunto de prueba compartido
   b. Calcule la métrica para ambos A y B en esta muestra bootstrap
   c. Calcule la diferencia bootstrap: `Δ_boot = metric(A_boot) - metric(B_boot)`
3. El valor p = fracción de muestras bootstrap donde `Δ_boot` tiene el signo opuesto a `Δ`
4. Si valor p < α (predeterminado 0.05), la diferencia es estadísticamente significativa

### Propiedades Clave

- **Pareado**: Ambos sistemas se evalúan en la misma muestra bootstrap, preservando la correlación a nivel de entrada
- **No paramétrico**: Sin suposiciones sobre la distribución de puntuaciones
- **Estándar**: Esto es exactamente lo que `sacrebleu --paired-bs` hace internamente

---

## Importante: sacrebleu Es una Dependencia Obligatoria

sacrebleu actualmente se encuentra en `[project.optional-dependencies]` y está protegido por `try/except` en `tester.py`. **Esto debe cambiar.** Un arnés de evaluación de traducción automática que no puede calcular chrF++ o BLEU no es un arnés de evaluación de traducción automática. sacrebleu debe ser:

1. Movido a `[project.dependencies]` en `pyproject.toml`
2. Importado directamente en `tester.py` (elimine la protección `try/except HAS_SACREBLEU`)
3. Importado directamente en el nuevo módulo `significance.py`

Las rutas condicionales `HAS_SACREBLEU` en `tester.py` deben eliminarse — hacen el código más complejo para un escenario (ejecutar sin sacrebleu) que no debe ser soportado.

---

## Plan de Implementación

### 1. Promover sacrebleu a dependencia obligatoria

**`pyproject.toml`**: Mueva `sacrebleu>=2.3` de `[project.optional-dependencies].metrics` a `[project.dependencies]`.

**`tester.py`**: Reemplace:
```python
# Optional: sacrebleu for chrF++ and BLEU
try:
    from sacrebleu.metrics import CHRF, BLEU
    HAS_SACREBLEU = True
except ImportError:
    HAS_SACREBLEU = False
```
Con:
```python
from sacrebleu.metrics import CHRF, BLEU
```

Elimine todas las protecciones `if HAS_SACREBLEU:` en `tester.py`.

---

### 2. Nuevo módulo: `mt_eval_harness/significance.py`

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

### 3. Funciones de métrica integradas

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

### 4. Integración en `compare.py`

El `compare.py` existente ya realiza comparación lado a lado de múltiples TestReports. Agregue pruebas de significancia:

```python
# In compare_reports(), after computing deltas:
if len(reports) == 2:
    sig_results = run_significance_tests(reports[0], reports[1])
    comparison["significance"] = [asdict(r) for r in sig_results]
```

Cuando se comparan más de 2 reportes, ejecute pruebas de significancia pareadas para todos los pares. Almacene resultados con clave `"(run_a_id, run_b_id)"`.

### 5. Integración CLI

Agregue una bandera `--significance` a `mt-eval compare`:

```bash
# Compare two runs with significance testing
mt-eval compare report_a.json report_b.json --significance

# Custom bootstrap count
mt-eval compare report_a.json report_b.json --significance --n-bootstrap 5000
```

También considere un comando independiente:

```bash
# Quick significance check between two reports
mt-eval significance report_a.json report_b.json
```

### 6. Formato de salida

**Salida de consola:**
```
  Significance Tests (paired bootstrap, n=1000, α=0.05):

  Metric              A         B       Δ      p-value  Sig?
  ─────────────────── ──────── ──────── ─────── ──────── ────
  corpus_chrf         42.96    41.80    +1.16   0.142    No
  exact_match_rate     0.198    0.185   +0.013  0.381    No
  corpus_bleu          6.80     3.81    +2.99   0.018    Yes *
```

**Salida JSON** (agregada al reporte de comparación):
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

### 7. Integración del panel

Si los datos de significancia están presentes en el JSON de comparación, el panel debe mostrarlos. Muestre una fila en la tabla de comparación con indicadores de significancia (p. ej., `*` para p < 0.05, `**` para p < 0.01). Esto es un complemento agradable, no bloqueante.

---

## Casos Extremos y Validación

1. **Entradas no coincidentes**: Los dos TestReports deben tener los mismos IDs de entrada. Si no es así (p. ej., uno se ejecutó en un subconjunto), solo pruebe significancia en la intersección. Advierta sobre entradas excluidas.

2. **Muy pocas entradas**: Si N < 10, advierta que las pruebas de significancia no son confiables con tan pocas entradas. Aún así ejecútelas, pero imprima la advertencia.

3. **Puntuaciones idénticas**: Si ambos sistemas producen resultados idénticos por entrada, p_value debe ser 1.0 (sin diferencia en absoluto).

4. **Métricas de complemento**: El módulo de significancia también debe probar cualquier métrica de complemento que aparezca en AMBOS reportes. Use un enfoque genérico: si ambos reportes tienen `plugin_metrics.crk_fst_validity.avg_fst_validity`, pruébelo.

5. **Reproducibilidad**: La semilla del RNG debe registrarse en la salida para que los resultados sean exactamente reproducibles. Predeterminado a 12345 (coincidiendo con la convención de SacreBLEU).

---

## Qué NO Construir

- **Sin significancia COMET separada**: COMET ahora está integrado como métrica de corpus a través de `metrics_comet.py`. Los ICs bootstrap se calculan sobre puntuaciones COMET al igual que chrF++/BLEU. Para significancia COMET pareada entre dos sistemas, use `comet-compare` de Unbabel.
- **Sin análisis Bayesiano**: Manténgase en bootstrap frecuentista. Es lo que la comunidad de traducción automática espera y entiende.
- **Sin corrección de pruebas múltiples**: Al probar múltiples métricas, no aplique correcciones de Bonferroni o similares. La convención en evaluación de traducción automática es reportar valores p sin procesar por métrica y dejar que el lector interprete.

---

## Archivos a Modificar

| Archivo | Cambio |
|---|---|
| `pyproject.toml` | Mueva sacrebleu de opcional a dependencia obligatoria |
| `mt_eval_harness/tester.py` | Elimine protecciones `HAS_SACREBLEU`, importación directa |
| `mt_eval_harness/significance.py` | **[NUEVO]** Implementación central |
| `mt_eval_harness/__init__.py` | Exporte `SignificanceResult`, `paired_bootstrap` |
| `mt_eval_harness/compare.py` | Conecte pruebas de significancia en comparación de reportes |
| `mt_eval_harness/cli.py` | Agregue banderas `--significance` y `--n-bootstrap` |
| `mt_eval_harness/dashboard.py` | Muestre significancia en tabla de comparación (complemento agradable) |
| `tests/test_significance.py` | **[NUEVO]** Pruebas unitarias |

---

## Requisitos de Prueba

1. **Determinista con semilla**: Mismas entradas + misma semilla = mismo valor p, cada vez
2. **Prueba de respuesta conocida**: Dos conjuntos de resultados idénticos → p_value = 1.0
3. **Prueba significativa conocida**: Construya dos conjuntos de resultados donde uno es claramente mejor (p. ej., todas las coincidencias exactas vs todos los fallos) → p_value ≈ 0.0
4. **IDs no coincidentes**: Debe generar ValueError o advertir y calcular en la intersección
5. **Entradas vacías**: Debe manejar correctamente (devolver p_value = 1.0 o generar)

---

## Intervalos de Confianza (Característica Complementaria)

> **Estado**: ✅ IMPLEMENTADO en `confidence.py`

Los intervalos de confianza (ICs) responden una pregunta diferente de la prueba de significancia:

- **Prueba de significancia** (`significance.py`): "¿Es la diferencia entre el sistema A y el sistema B real?"
- **Intervalos de confianza** (`confidence.py`): "¿Cuál es la incertidumbre en la puntuación de este sistema por sí solo?"

### Implementación: `confidence.py`

Utiliza el mismo método de remuestreo bootstrap percentil que la prueba de significancia:

| Parámetro | Valor | Justificación |
|---|---|---|
| `n_bootstrap` | 1000 | Predeterminado de SacreBLEU, convención WMT 2024 |
| `seed` | 12345 | Semilla predeterminada de SacreBLEU para reproducibilidad |
| `alpha` | 0.05 | Nivel de confianza estándar del 95% |
| Método | Bootstrap percentil | Koehn (2004), Efron (1979) |

### Qué Obtiene ICs

Todas las métricas a nivel de corpus calculadas por el arnés:
- `corpus_chrf` (puntuación chrF++)
- `corpus_bleu` (puntuación BLEU)
- `exact_match_rate` (0.0–1.0)

### Banderas CLI

```bash
# Default: CIs are computed automatically
mt-eval test run_log.json

# Skip CI computation (faster, for quick iteration)
mt-eval test run_log.json --no-ci

# More bootstrap iterations (more precise, slower)
mt-eval test run_log.json --n-bootstrap-ci 2000
```

### Advertencia de Muestra Pequeña

Cuando N < 30 entradas, el módulo emite una advertencia de que los ICs pueden tener cobertura deficiente. El bootstrap no puede crear información ausente de la muestra — con muy pocas entradas, los intervalos serán amplios, reflejando correctamente la alta incertidumbre.

### Integración COMET

COMET (`metrics_comet.py`) ahora está integrado como métrica de primera clase:
- Modelo: `Unbabel/wmt22-comet-da` (modelo de referencia ganador de WMT 2022)
- Calculado automáticamente cuando `unbabel-comet` está instalado
- Puntuaciones por entrada almacenadas en entradas de TestReport
- Detección de idioma de bajo recurso a través de tabla de cobertura XLM-R
- Dependencia opcional: `pip install mt-eval-harness[comet]`

### Migración Supabase

Nuevas columnas agregadas a la tabla `run_cards`:
- `comet_score` (FLOAT8, nullable)
- `corpus_bleu` (FLOAT8, nullable)
- `chrf_ci_lower` / `chrf_ci_upper` (FLOAT8, nullable)
- `exact_match_ci_lower` / `exact_match_ci_upper` (FLOAT8, nullable)

Vea `migrations/001_add_comet_and_ci_columns.sql` para el script de migración.