---
sidebar_position: 7
title: "통계적 유의성 검정"
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
# 통계적 유의성 검정 — 구현 명세

> **대상 코드베이스**: `arena` (특히 `tester.py` 및 `compare.py`)
> **목적**: 두 평가 실행 간의 차이가 통계적으로 유의한지 아니면 단순한 노이즈인지 연구자가 판단할 수 있도록 해요.
> **우선순위**: 높음 — 출판 가능한 결과를 위해 가장 중요하게 빠져 있는 기능이에요.

---

## 이것이 중요한 이유

두 실행을 비교할 때(예: 92개 항목에 대한 Gemini 3.1 Pro chrF++ 42.96 vs Claude Sonnet chrF++ 41.80), 현재로서는 그 차이가 실제인지 노이즈인지 말할 수 없어요. 테스트 항목이 약 92개에 불과하면 무작위 변동이 1~2점의 변화를 쉽게 만들어낼 수 있어요. 전문가들은 유의성 검정을 요구할 거예요. 우리는 답해야 해요.

---

## 알고리즘: 짝지은 부트스트랩 재표집(Paired Bootstrap Resampling)

이것은 SacreBLEU, MT-Lens, WMT 공유 작업에서 사용하는 표준 방법이에요. MT 연구자들이 잘 이해하고 있으며 신뢰하는 결과를 만들어내요.

### 작동 방식

동일한 N개의 테스트 항목에서 평가된 두 시스템 A와 B가 주어졌을 때:

1. 실제 메트릭 차이를 계산해요: `Δ = metric(A) - metric(B)`
2. `n_bootstrap`번 반복해요(기본값 1000):
   a. 공유 테스트 세트에서 N개의 항목을 **복원 추출**해요
   b. 이 부트스트랩 표본에 대해 A와 B 모두의 메트릭을 계산해요
   c. 부트스트랩 차이를 계산해요: `Δ_boot = metric(A_boot) - metric(B_boot)`
3. p-value = `Δ_boot`이 `Δ`과 반대 부호를 갖는 부트스트랩 표본의 비율
4. p-value < α(기본값 0.05)이면 그 차이는 통계적으로 유의해요

### 주요 특성

- **짝지음(Paired)**: 두 시스템 모두 동일한 부트스트랩 표본에서 평가되어 항목 수준의 상관관계를 보존해요
- **비모수적(Non-parametric)**: 점수 분포에 대한 가정이 없어요
- **표준적**: 이것은 `sacrebleu --paired-bs`이 내부적으로 수행하는 것과 정확히 같아요

---

## 중요: sacrebleu는 필수 의존성이에요

sacrebleu는 현재 `[project.optional-dependencies]` 아래에 나열되어 있으며 `tester.py`의 `try/except`으로 보호되고 있어요. **이것은 변경되어야 해요.** chrF++나 BLEU를 계산할 수 없는 MT 평가 하니스는 MT 평가 하니스가 아니에요. sacrebleu는 다음과 같이 되어야 해요:

1. `pyproject.toml`의 `[project.dependencies]`으로 이동
2. `tester.py`에서 직접 임포트(`try/except HAS_SACREBLEU` 가드 제거)
3. 새로운 `significance.py` 모듈에서 직접 임포트

`tester.py`의 `HAS_SACREBLEU` 조건부 경로는 제거되어야 해요 — 지원되지 않아야 할 시나리오(sacrebleu 없이 실행)를 위해 코드를 더 복잡하게 만들어요.

---

## 구현 계획

### 1. sacrebleu를 필수 의존성으로 승격

**`pyproject.toml`**: `sacrebleu>=2.3`을 `[project.optional-dependencies].metrics`에서 `[project.dependencies]`으로 이동해요.

**`tester.py`**: 다음을 교체해요:
```python
# Optional: sacrebleu for chrF++ and BLEU
try:
    from sacrebleu.metrics import CHRF, BLEU
    HAS_SACREBLEU = True
except ImportError:
    HAS_SACREBLEU = False
```
다음으로:
```python
from sacrebleu.metrics import CHRF, BLEU
```

`tester.py` 전체에서 모든 `if HAS_SACREBLEU:` 가드를 제거해요.

---

### 2. 새 모듈: `mt_eval_harness/significance.py`

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

### 3. 내장 메트릭 함수

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

### 4. `compare.py`에 통합

기존 `compare.py`은 이미 여러 TestReport의 나란한 비교를 수행해요. 유의성 검정을 추가해요:

```python
# In compare_reports(), after computing deltas:
if len(reports) == 2:
    sig_results = run_significance_tests(reports[0], reports[1])
    comparison["significance"] = [asdict(r) for r in sig_results]
```

2개를 초과하는 리포트가 비교될 때, 모든 쌍에 대해 쌍별 유의성 검정을 실행해요. `"(run_a_id, run_b_id)"`으로 키를 지정하여 결과를 저장해요.

### 5. CLI 통합

`mt-eval compare`에 `--significance` 플래그를 추가해요:

```bash
# Compare two runs with significance testing
mt-eval compare report_a.json report_b.json --significance

# Custom bootstrap count
mt-eval compare report_a.json report_b.json --significance --n-bootstrap 5000
```

독립 실행형 명령도 고려해요:

```bash
# Quick significance check between two reports
mt-eval significance report_a.json report_b.json
```

### 6. 출력 형식

**콘솔 출력:**
```
  Significance Tests (paired bootstrap, n=1000, α=0.05):

  Metric              A         B       Δ      p-value  Sig?
  ─────────────────── ──────── ──────── ─────── ──────── ────
  corpus_chrf         42.96    41.80    +1.16   0.142    No
  exact_match_rate     0.198    0.185   +0.013  0.381    No
  corpus_bleu          6.80     3.81    +2.99   0.018    Yes *
```

**JSON 출력**(비교 리포트에 추가됨):
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

### 7. 대시보드 통합

비교 JSON에 유의성 데이터가 있으면 대시보드가 이를 표시해야 해요. 유의성 표시기(예: p < 0.05의 경우 `*`, p < 0.01의 경우 `**`)와 함께 비교 표에 행을 표시해요. 이것은 필수가 아닌 있으면 좋은 기능이에요.

---

## 엣지 케이스 및 검증

1. **불일치 항목**: 두 TestReport는 동일한 항목 ID를 가져야 해요. 그렇지 않은 경우(예: 한쪽이 부분 집합에서 실행됨), 교집합에 대해서만 유의성을 검정해요. 제외된 항목에 대해 경고해요.

2. **항목이 너무 적음**: N < 10이면, 항목이 그렇게 적으면 유의성 검정이 신뢰할 수 없다고 경고해요. 그래도 실행하되, 경고를 출력해요.

3. **동일한 점수**: 두 시스템이 항목별로 동일한 결과를 만들어내면, p_value는 1.0이어야 해요(차이가 전혀 없음).

4. **플러그인 메트릭**: 유의성 모듈은 두 리포트 모두에 나타나는 플러그인 메트릭도 검정해야 해요. 일반적인 접근 방식을 사용해요: 두 리포트 모두 `plugin_metrics.crk_fst_validity.avg_fst_validity`을 가지면 검정해요.

5. **재현성**: 결과가 정확히 재현될 수 있도록 RNG 시드는 출력에 기록되어야 해요. 기본값은 12345(SacreBLEU 관례에 맞춤)예요.

---

## 만들지 말아야 할 것

- **별도의 COMET 유의성 없음**: COMET은 이제 `metrics_comet.py`을 통해 코퍼스 메트릭으로 통합되어 있어요. 부트스트랩 CI는 chrF++/BLEU와 마찬가지로 COMET 점수에 대해 계산돼요. 두 시스템 간의 쌍별 COMET 유의성은 Unbabel의 `comet-compare`을 사용해요.
- **베이지안 분석 없음**: 빈도주의 부트스트랩을 고수해요. 이것이 MT 커뮤니티가 기대하고 이해하는 것이에요.
- **다중 검정 보정 없음**: 여러 메트릭을 검정할 때 Bonferroni나 유사한 보정을 적용하지 마세요. MT 평가의 관례는 메트릭별로 원시 p-value를 보고하고 독자가 해석하도록 하는 거예요.

---

## 수정할 파일

| 파일 | 변경 |
|---|---|
| `pyproject.toml` | sacrebleu를 선택적에서 필수 의존성으로 이동 |
| `mt_eval_harness/tester.py` | `HAS_SACREBLEU` 가드 제거, 직접 임포트 |
| `mt_eval_harness/significance.py` | **[신규]** 핵심 구현 |
| `mt_eval_harness/__init__.py` | `SignificanceResult`, `paired_bootstrap` 익스포트 |
| `mt_eval_harness/compare.py` | 리포트 비교에 유의성 검정 연결 |
| `mt_eval_harness/cli.py` | `--significance` 및 `--n-bootstrap` 플래그 추가 |
| `mt_eval_harness/dashboard.py` | 비교 표에 유의성 표시(있으면 좋음) |
| `tests/test_significance.py` | **[신규]** 단위 테스트 |

---

## 테스트 요구사항

1. **시드를 통한 결정성**: 동일한 입력 + 동일한 시드 = 동일한 p-value, 항상
2. **알려진 답 테스트**: 두 개의 동일한 결과 세트 → p_value = 1.0
3. **알려진 유의성 테스트**: 한쪽이 명확히 더 나은 두 개의 결과 세트를 구성해요(예: 모두 정확히 일치 vs 모두 불일치) → p_value ≈ 0.0
4. **불일치 ID**: ValueError를 발생시키거나 경고하고 교집합에 대해 계산해야 해요
5. **빈 입력**: 우아하게 처리해야 해요(p_value = 1.0 반환 또는 발생)

---

## 신뢰 구간(부속 기능)

> **상태**: ✅ `confidence.py`에 구현됨

신뢰 구간(CI)은 유의성 검정과 다른 질문에 답해요:

- **유의성 검정**(`significance.py`): "시스템 A와 시스템 B 간의 차이가 실제인가요?"
- **신뢰 구간**(`confidence.py`): "이 시스템의 점수 자체가 얼마나 불확실한가요?"

### 구현: `confidence.py`

유의성 검정과 동일한 백분위수 부트스트랩 재표집 방법을 사용해요:

| 매개변수 | 값 | 근거 |
|---|---|---|
| `n_bootstrap` | 1000 | SacreBLEU 기본값, WMT 2024 관례 |
| `seed` | 12345 | 재현성을 위한 SacreBLEU 기본 시드 |
| `alpha` | 0.05 | 표준 95% 신뢰 수준 |
| 방법 | 백분위수 부트스트랩 | Koehn (2004), Efron (1979) |

### CI를 받는 항목

하니스가 계산하는 모든 코퍼스 수준 메트릭:
- `corpus_chrf` (chrF++ 점수)
- `corpus_bleu` (BLEU 점수)
- `exact_match_rate` (0.0–1.0)

### CLI 플래그

```bash
# Default: CIs are computed automatically
mt-eval test run_log.json

# Skip CI computation (faster, for quick iteration)
mt-eval test run_log.json --no-ci

# More bootstrap iterations (more precise, slower)
mt-eval test run_log.json --n-bootstrap-ci 2000
```

### 소표본 경고

N < 30 항목일 때, 모듈은 CI의 커버리지가 좋지 않을 수 있다는 경고를 내보내요. 부트스트랩은 표본에 없는 정보를 만들어낼 수 없어요 — 항목이 매우 적으면 구간이 넓어져 높은 불확실성을 올바르게 반영해요.

### COMET 통합

COMET(`metrics_comet.py`)은 이제 일급 메트릭으로 통합되어 있어요:
- 모델: `Unbabel/wmt22-comet-da` (WMT 2022 수상 참조 기반 모델)
- `unbabel-comet`가 설치되면 자동으로 계산됨
- 항목별 점수가 TestReport 항목에 저장됨
- XLM-R 커버리지 표를 통한 저자원 언어 감지
- 선택적 의존성: `pip install mt-eval-harness[comet]`

### Supabase 마이그레이션

`run_cards` 테이블에 추가된 새 열:
- `comet_score` (FLOAT8, nullable)
- `corpus_bleu` (FLOAT8, nullable)
- `chrf_ci_lower` / `chrf_ci_upper` (FLOAT8, nullable)
- `exact_match_ci_lower` / `exact_match_ci_upper` (FLOAT8, nullable)

마이그레이션 스크립트는 `migrations/001_add_comet_and_ci_columns.sql`을 참조하세요.