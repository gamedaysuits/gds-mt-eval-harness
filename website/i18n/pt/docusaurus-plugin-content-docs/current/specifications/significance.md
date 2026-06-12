---
sidebar_position: 7
title: "Teste de Significância Estatística"
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
# Testes de Significância Estatística — Especificação de Implementação

> **Codebase alvo**: `arena` (especificamente `tester.py` e `compare.py`)
> **Propósito**: Permitir que pesquisadores determinem se a diferença entre duas execuções de avaliação é estatisticamente significativa ou apenas ruído.
> **Prioridade**: Alta — esta é a funcionalidade mais importante que falta para resultados publicáveis.

---

## Por Que Isso Importa

Ao comparar duas execuções (por exemplo, Gemini 3.1 Pro chrF++ 42.96 vs Claude Sonnet chrF++ 41.80 em 92 entradas), atualmente não podemos dizer se a diferença é real ou ruído. Com apenas ~92 entradas de teste, a variação aleatória pode facilmente produzir oscilações de 1-2 pontos. Especialistas pedirão testes de significância. Precisamos responder.

---

## Algoritmo: Reamostragem Bootstrap Pareada

Este é o método padrão usado por SacreBLEU, MT-Lens e tarefas compartilhadas da WMT. É bem compreendido por pesquisadores de MT e produz resultados em que confiam.

### Como Funciona

Dados dois sistemas A e B avaliados nas mesmas N entradas de teste:

1. Calcule a diferença de métrica real: `Δ = metric(A) - metric(B)`
2. Repita `n_bootstrap` vezes (padrão 1000):
   a. Amostre N entradas **com reposição** do conjunto de teste compartilhado
   b. Calcule a métrica para A e B nesta amostra bootstrap
   c. Calcule a diferença bootstrap: `Δ_boot = metric(A_boot) - metric(B_boot)`
3. O p-valor = fração de amostras bootstrap onde `Δ_boot` tem sinal oposto a `Δ`
4. Se p-valor < α (padrão 0.05), a diferença é estatisticamente significativa

### Propriedades-Chave

- **Pareada**: Ambos os sistemas são avaliados na mesma amostra bootstrap, preservando correlação no nível de entrada
- **Não-paramétrica**: Sem suposição sobre a distribuição de pontuações
- **Padrão**: Isto é exatamente o que `sacrebleu --paired-bs` faz internamente

---

## Importante: sacrebleu É uma Dependência Obrigatória

sacrebleu está atualmente listado sob `[project.optional-dependencies]` e protegido por `try/except` em `tester.py`. **Isto deve ser alterado.** Um harness de avaliação de MT que não consegue calcular chrF++ ou BLEU não é um harness de avaliação de MT. sacrebleu deve ser:

1. Movido para `[project.dependencies]` em `pyproject.toml`
2. Importado diretamente em `tester.py` (remova a proteção `try/except HAS_SACREBLEU`)
3. Importado diretamente no novo módulo `significance.py`

Os caminhos condicionais `HAS_SACREBLEU` em `tester.py` devem ser removidos — eles tornam o código mais complexo para um cenário (executar sem sacrebleu) que não deve ser suportado.

---

## Plano de Implementação

### 1. Promover sacrebleu a dependência obrigatória

**`pyproject.toml`**: Mova `sacrebleu>=2.3` de `[project.optional-dependencies].metrics` para `[project.dependencies]`.

**`tester.py`**: Substitua:
```python
# Optional: sacrebleu for chrF++ and BLEU
try:
    from sacrebleu.metrics import CHRF, BLEU
    HAS_SACREBLEU = True
except ImportError:
    HAS_SACREBLEU = False
```
Por:
```python
from sacrebleu.metrics import CHRF, BLEU
```

Remova todas as proteções `if HAS_SACREBLEU:` em `tester.py`.

---

### 2. Novo módulo: `mt_eval_harness/significance.py`

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

### 3. Funções de métrica integradas

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

### 4. Integração em `compare.py`

O `compare.py` existente já faz comparação lado a lado de múltiplos TestReports. Adicione testes de significância:

```python
# In compare_reports(), after computing deltas:
if len(reports) == 2:
    sig_results = run_significance_tests(reports[0], reports[1])
    comparison["significance"] = [asdict(r) for r in sig_results]
```

Quando mais de 2 relatórios são comparados, execute testes de significância pareados para todos os pares. Armazene resultados com chave `"(run_a_id, run_b_id)"`.

### 5. Integração CLI

Adicione uma flag `--significance` a `mt-eval compare`:

```bash
# Compare two runs with significance testing
mt-eval compare report_a.json report_b.json --significance

# Custom bootstrap count
mt-eval compare report_a.json report_b.json --significance --n-bootstrap 5000
```

Considere também um comando autônomo:

```bash
# Quick significance check between two reports
mt-eval significance report_a.json report_b.json
```

### 6. Formato de saída

**Saída de console:**
```
  Significance Tests (paired bootstrap, n=1000, α=0.05):

  Metric              A         B       Δ      p-value  Sig?
  ─────────────────── ──────── ──────── ─────── ──────── ────
  corpus_chrf         42.96    41.80    +1.16   0.142    No
  exact_match_rate     0.198    0.185   +0.013  0.381    No
  corpus_bleu          6.80     3.81    +2.99   0.018    Yes *
```

**Saída JSON** (adicionada ao relatório de comparação):
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

### 7. Integração do dashboard

Se dados de significância estão presentes no JSON de comparação, o dashboard deve exibi-los. Mostre uma linha na tabela de comparação com indicadores de significância (por exemplo, `*` para p < 0.05, `**` para p < 0.01). Isto é um nice-to-have, não é bloqueante.

---

## Casos Extremos e Validação

1. **Entradas incompatíveis**: Os dois TestReports devem ter os mesmos IDs de entrada. Se não tiverem (por exemplo, um foi executado em um subconjunto), teste significância apenas na interseção. Avise sobre entradas excluídas.

2. **Poucas entradas**: Se N < 10, avise que testes de significância são pouco confiáveis com tão poucas entradas. Ainda assim execute-os, mas imprima o aviso.

3. **Pontuações idênticas**: Se ambos os sistemas produzem resultados idênticos por entrada, p_value deve ser 1.0 (nenhuma diferença).

4. **Métricas de plugin**: O módulo de significância também deve testar qualquer métrica de plugin que apareça em AMBOS os relatórios. Use uma abordagem genérica: se ambos os relatórios têm `plugin_metrics.crk_fst_validity.avg_fst_validity`, teste-a.

5. **Reprodutibilidade**: A seed do RNG deve ser registrada na saída para que os resultados sejam exatamente reproduzíveis. Padrão 12345 (seguindo convenção SacreBLEU).

---

## O Que NÃO Construir

- **Sem significância COMET separada**: COMET agora está integrado como métrica de corpus via `metrics_comet.py`. ICs bootstrap são calculados sobre pontuações COMET assim como chrF++/BLEU. Para significância COMET pareada entre dois sistemas, use `comet-compare` da Unbabel.
- **Sem análise Bayesiana**: Mantenha bootstrap frequentista. É o que a comunidade de MT espera e compreende.
- **Sem correção de múltiplos testes**: Ao testar múltiplas métricas, não aplique correções de Bonferroni ou similares. A convenção em avaliação de MT é relatar p-valores brutos por métrica e deixar o leitor interpretar.

---

## Arquivos a Modificar

| Arquivo | Mudança |
|---|---|
| `pyproject.toml` | Mova sacrebleu de opcional para dependência obrigatória |
| `mt_eval_harness/tester.py` | Remova proteções `HAS_SACREBLEU`, importe diretamente |
| `mt_eval_harness/significance.py` | **[NOVO]** Implementação principal |
| `mt_eval_harness/__init__.py` | Exporte `SignificanceResult`, `paired_bootstrap` |
| `mt_eval_harness/compare.py` | Conecte testes de significância à comparação de relatórios |
| `mt_eval_harness/cli.py` | Adicione flags `--significance` e `--n-bootstrap` |
| `mt_eval_harness/dashboard.py` | Exiba significância na tabela de comparação (nice-to-have) |
| `tests/test_significance.py` | **[NOVO]** Testes unitários |

---

## Requisitos de Teste

1. **Determinístico com seed**: Mesmas entradas + mesma seed = mesmo p-valor, sempre
2. **Teste de resposta conhecida**: Dois conjuntos de resultados idênticos → p_value = 1.0
3. **Teste significativo conhecido**: Construa dois conjuntos de resultados onde um é claramente melhor (por exemplo, todos os acertos exatos vs todos os erros) → p_value ≈ 0.0
4. **IDs incompatíveis**: Deve lançar ValueError ou avisar e calcular na interseção
5. **Entradas vazias**: Deve lidar graciosamente (retornar p_value = 1.0 ou lançar)

---

## Intervalos de Confiança (Funcionalidade Complementar)

> **Status**: ✅ IMPLEMENTADO em `confidence.py`

Intervalos de confiança (ICs) respondem uma pergunta diferente de testes de significância:

- **Teste de significância** (`significance.py`): "A diferença entre o sistema A e o sistema B é real?"
- **Intervalos de confiança** (`confidence.py`): "Quão incerta é a pontuação deste sistema por si só?"

### Implementação: `confidence.py`

Usa o mesmo método de reamostragem bootstrap percentil que testes de significância:

| Parâmetro | Valor | Justificativa |
|---|---|---|
| `n_bootstrap` | 1000 | Padrão SacreBLEU, convenção WMT 2024 |
| `seed` | 12345 | Seed padrão SacreBLEU para reprodutibilidade |
| `alpha` | 0.05 | Nível de confiança padrão de 95% |
| Método | Bootstrap percentil | Koehn (2004), Efron (1979) |

### O Que Recebe ICs

Todas as métricas no nível de corpus calculadas pelo harness:
- `corpus_chrf` (pontuação chrF++)
- `corpus_bleu` (pontuação BLEU)
- `exact_match_rate` (0.0–1.0)

### Flags CLI

```bash
# Default: CIs are computed automatically
mt-eval test run_log.json

# Skip CI computation (faster, for quick iteration)
mt-eval test run_log.json --no-ci

# More bootstrap iterations (more precise, slower)
mt-eval test run_log.json --n-bootstrap-ci 2000
```

### Aviso de Amostra Pequena

Quando N < 30 entradas, o módulo emite um aviso de que ICs podem ter cobertura deficiente. O bootstrap não pode criar informação ausente da amostra — com muito poucas entradas, os intervalos serão amplos, refletindo corretamente alta incerteza.

### Integração COMET

COMET (`metrics_comet.py`) agora está integrado como métrica de primeira classe:
- Modelo: `Unbabel/wmt22-comet-da` (modelo baseado em referência vencedor WMT 2022)
- Calculado automaticamente quando `unbabel-comet` está instalado
- Pontuações por entrada armazenadas em entradas TestReport
- Detecção de idioma de baixo recurso via tabela de cobertura XLM-R
- Dependência opcional: `pip install mt-eval-harness[comet]`

### Migração Supabase

Novas colunas adicionadas à tabela `run_cards`:
- `comet_score` (FLOAT8, anulável)
- `corpus_bleu` (FLOAT8, anulável)
- `chrf_ci_lower` / `chrf_ci_upper` (FLOAT8, anulável)
- `exact_match_ci_lower` / `exact_match_ci_upper` (FLOAT8, anulável)

Veja `migrations/001_add_comet_and_ci_columns.sql` para o script de migração.