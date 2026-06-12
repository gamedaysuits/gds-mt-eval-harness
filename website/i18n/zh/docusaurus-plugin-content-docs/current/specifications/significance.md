---
sidebar_position: 7
title: "统计显著性检验"
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
# 统计显著性检验 — 实现规范

> **目标代码库**: `arena` (特别是 `tester.py` 和 `compare.py`)
> **目的**: 使研究人员能够确定两次评估运行之间的差异是否具有统计显著性或仅仅是噪声。
> **优先级**: 高 — 这是可发表结果中最重要的缺失功能。

---

## 为什么这很重要

在比较两次运行时（例如，Gemini 3.1 Pro chrF++ 42.96 vs Claude Sonnet chrF++ 41.80，共92个条目），我们目前无法判断差异是真实的还是噪声。仅有约92个测试条目，随机变异很容易产生1-2个点的波动。专家会要求进行显著性检验。我们需要给出答案。

---

## 算法：配对自助法重采样

这是SacreBLEU、MT-Lens和WMT共享任务使用的标准方法。它被MT研究人员充分理解，并产生他们信任的结果。

### 工作原理

给定在相同N个测试条目上评估的两个系统A和B：

1. 计算实际的指标差异：`Δ = metric(A) - metric(B)`
2. 重复 `n_bootstrap` 次（默认1000次）：
   a. 从共享测试集中**有放回地**采样N个条目
   b. 在此自助样本上计算A和B的指标
   c. 计算自助差异：`Δ_boot = metric(A_boot) - metric(B_boot)`
3. p值 = 自助样本中 `Δ_boot` 与 `Δ` 符号相反的比例
4. 如果p值 < α（默认0.05），则差异具有统计显著性

### 关键特性

- **配对**: 两个系统在相同的自助样本上进行评估，保留条目级相关性
- **非参数**: 对分数分布没有假设
- **标准**: 这正是 `sacrebleu --paired-bs` 在底层所做的

---

## 重要：sacrebleu 是硬依赖

sacrebleu 目前在 `[project.optional-dependencies]` 中列出并由 `try/except` 在 `tester.py` 中保护。**这应该改变。** 无法计算chrF++或BLEU的MT评估工具不是MT评估工具。sacrebleu 应该：

1. 在 `pyproject.toml` 中从 `[project.dependencies]` 移动到
2. 直接在 `tester.py` 中导入（移除 `try/except HAS_SACREBLEU` 保护）
3. 直接在新的 `significance.py` 模块中导入

`tester.py` 中的 `HAS_SACREBLEU` 条件路径应该被移除 — 它们使代码对于一个不应该被支持的场景（在没有sacrebleu的情况下运行）变得更复杂。

---

## 实现计划

### 1. 将sacrebleu提升为硬依赖

**`pyproject.toml`**: 将 `sacrebleu>=2.3` 从 `[project.optional-dependencies].metrics` 移动到 `[project.dependencies]`。

**`tester.py`**: 替换：
```python
# Optional: sacrebleu for chrF++ and BLEU
try:
    from sacrebleu.metrics import CHRF, BLEU
    HAS_SACREBLEU = True
except ImportError:
    HAS_SACREBLEU = False
```
为：
```python
from sacrebleu.metrics import CHRF, BLEU
```

移除整个 `tester.py` 中的所有 `if HAS_SACREBLEU:` 保护。

---

### 2. 新模块：`mt_eval_harness/significance.py`

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

### 3. 内置指标函数

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

### 4. 集成到 `compare.py`

现有的 `compare.py` 已经进行多个TestReports的并排比较。添加显著性检验：

```python
# In compare_reports(), after computing deltas:
if len(reports) == 2:
    sig_results = run_significance_tests(reports[0], reports[1])
    comparison["significance"] = [asdict(r) for r in sig_results]
```

当比较超过2个报告时，对所有对运行成对显著性检验。按 `"(run_a_id, run_b_id)"` 键存储结果。

### 5. CLI集成

向 `mt-eval compare` 添加 `--significance` 标志：

```bash
# Compare two runs with significance testing
mt-eval compare report_a.json report_b.json --significance

# Custom bootstrap count
mt-eval compare report_a.json report_b.json --significance --n-bootstrap 5000
```

还可以考虑一个独立命令：

```bash
# Quick significance check between two reports
mt-eval significance report_a.json report_b.json
```

### 6. 输出格式

**控制台输出：**
```
  Significance Tests (paired bootstrap, n=1000, α=0.05):

  Metric              A         B       Δ      p-value  Sig?
  ─────────────────── ──────── ──────── ─────── ──────── ────
  corpus_chrf         42.96    41.80    +1.16   0.142    No
  exact_match_rate     0.198    0.185   +0.013  0.381    No
  corpus_bleu          6.80     3.81    +2.99   0.018    Yes *
```

**JSON输出**（添加到比较报告）：
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

### 7. 仪表板集成

如果比较JSON中存在显著性数据，仪表板应显示它。在比较表中显示一行，带有显著性指示符（例如，p < 0.05时为 `*`，p < 0.01时为 `**`）。这是一个很好的功能，但不是阻塞性的。

---

## 边界情况和验证

1. **条目不匹配**: 两个TestReports必须具有相同的条目ID。如果不匹配（例如，一个在子集上运行），仅在交集上测试显著性。警告排除的条目。

2. **条目太少**: 如果N < 10，警告显著性检验在这么少的条目上不可靠。仍然运行它们，但打印警告。

3. **相同分数**: 如果两个系统产生相同的每条目结果，p_value应该是1.0（完全没有差异）。

4. **插件指标**: 显著性模块也应该测试出现在两个报告中的任何插件指标。使用通用方法：如果两个报告都有 `plugin_metrics.crk_fst_validity.avg_fst_validity`，测试它。

5. **可重现性**: RNG种子必须记录在输出中，以便结果完全可重现。默认为12345（与SacreBLEU约定匹配）。

---

## 不要构建的内容

- **无单独的COMET显著性**: COMET现在通过 `metrics_comet.py` 集成为语料库指标。自助CI在COMET分数上计算，就像chrF++/BLEU一样。对于两个系统之间的成对COMET显著性，使用来自Unbabel的 `comet-compare`。
- **无贝叶斯分析**: 坚持频率论自助法。这是MT社区期望和理解的。
- **无多重检验校正**: 测试多个指标时，不应用Bonferroni或类似校正。MT评估中的约定是报告每个指标的原始p值，让读者自己解释。

---

## 要修改的文件

| 文件 | 更改 |
|---|---|
| `pyproject.toml` | 将sacrebleu从可选依赖移动到硬依赖 |
| `mt_eval_harness/tester.py` | 移除 `HAS_SACREBLEU` 保护，直接导入 |
| `mt_eval_harness/significance.py` | **[新增]** 核心实现 |
| `mt_eval_harness/__init__.py` | 导出 `SignificanceResult`、`paired_bootstrap` |
| `mt_eval_harness/compare.py` | 将显著性检验连接到报告比较 |
| `mt_eval_harness/cli.py` | 添加 `--significance` 和 `--n-bootstrap` 标志 |
| `mt_eval_harness/dashboard.py` | 在比较表中显示显著性（很好的功能） |
| `tests/test_significance.py` | **[新增]** 单元测试 |

---

## 测试要求

1. **使用种子确定性**: 相同输入 + 相同种子 = 相同p值，每次都是
2. **已知答案测试**: 两个相同的结果集 → p_value = 1.0
3. **已知显著测试**: 构造两个结果集，其中一个明显更好（例如，所有精确匹配vs所有错误） → p_value ≈ 0.0
4. **ID不匹配**: 应该抛出ValueError或警告并在交集上计算
5. **空输入**: 应该优雅处理（返回p_value = 1.0或抛出）

---

## 置信区间（配套功能）

> **状态**: ✅ 在 `confidence.py` 中已实现

置信区间（CI）回答了与显著性检验不同的问题：

- **显著性检验** (`significance.py`): "系统A和系统B之间的差异是真实的吗？"
- **置信区间** (`confidence.py`): "这个系统自身的分数有多不确定？"

### 实现：`confidence.py`

使用与显著性检验相同的百分位数自助重采样方法：

| 参数 | 值 | 理由 |
|---|---|---|
| `n_bootstrap` | 1000 | SacreBLEU默认值，WMT 2024约定 |
| `seed` | 12345 | SacreBLEU默认种子以确保可重现性 |
| `alpha` | 0.05 | 标准95%置信水平 |
| 方法 | 百分位数自助法 | Koehn (2004)、Efron (1979) |

### 获得CI的内容

工具计算的所有语料库级指标：
- `corpus_chrf` (chrF++分数)
- `corpus_bleu` (BLEU分数)
- `exact_match_rate` (0.0–1.0)

### CLI标志

```bash
# Default: CIs are computed automatically
mt-eval test run_log.json

# Skip CI computation (faster, for quick iteration)
mt-eval test run_log.json --no-ci

# More bootstrap iterations (more precise, slower)
mt-eval test run_log.json --n-bootstrap-ci 2000
```

### 小样本警告

当N < 30个条目时，模块发出警告，CI可能覆盖率不佳。自助法无法创建样本中不存在的信息 — 条目很少时，区间会很宽，正确反映高度不确定性。

### COMET集成

COMET (`metrics_comet.py`) 现在集成为一流指标：
- 模型：`Unbabel/wmt22-comet-da` (WMT 2022获奖的基于参考的模型)
- 安装 `unbabel-comet` 时自动计算
- 每条目分数存储在TestReport条目中
- 通过XLM-R覆盖表进行低资源语言检测
- 可选依赖：`pip install mt-eval-harness[comet]`

### Supabase迁移

添加到 `run_cards` 表的新列：
- `comet_score` (FLOAT8，可空)
- `corpus_bleu` (FLOAT8，可空)
- `chrf_ci_lower` / `chrf_ci_upper` (FLOAT8，可空)
- `exact_match_ci_lower` / `exact_match_ci_upper` (FLOAT8，可空)

参见 `migrations/001_add_comet_and_ci_columns.sql` 获取迁移脚本。