---
sidebar_position: 5
title: "채점 사양"
slug: '/specifications/scoring'
related:
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
    note: "When a score difference actually means something"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
    note: "The tool that computes these metrics"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "These scores, live"
---
# 점수 산정 명세

> **핵심 요약.** 이 문서는 Champollion MT 평가 생태계의 모든 평가 지표, 종합 점수 산정, 품질 등급, 비용 분석에 대한 단일 진실 공급원(single source of truth)이에요. 언어별 평가 지표 — FST 형태론적 유효성, linter 등가 클래스, 결정론적 의미 검증 — 은 통틀어 **LYSS**(Linguistically-informed Yield & Structural Scoring)라고 불러요. 하니스에서 계산하는 모든 지표, 종합 공식의 모든 가중치, 모든 등급 임계값이 여기에서 — 그리고 오직 여기에서만 — 정의돼요. 코드, 문서, 데이터베이스 스키마는 모두 이 문서에서 파생돼요. 충돌이 발생하면 이 문서가 우선해요.
>
> **범위.** 이 문서는 우리가 *무엇을* 측정하고 *어떻게 점수를 매기는지*를 정의해요. 런 카드 스키마(BENCHMARK_SPEC §3 참조), 벤치마크 프로토콜(BENCHMARK_SPEC §6), 또는 리더보드 규칙(arena 문서 참조)은 정의하지 않아요. 해당 문서들은 지표 정의와 점수 산정 로직에 대해 이 문서를 참조해요.
>
> 최종 업데이트: 2026-06-07

---

## 1. 점수 산정 철학

### 1.1 마이크로평가 철학

> *"일반화되는 것에만 집중한다면, 우리는 필연적으로 그것이 일반화되지 않는 곳을 잊게 될 것이고 — 이 언어들과 그 안에 담긴 모든 지식과 지혜를 잃게 될 거예요."*

이 프로젝트는 **마이크로평가(microeval) 개발**을 실천해요. 즉, 유한 상태 변환기, 이중 언어 사전, 형태소 분석기, 언어학자가 큐레이션한 등가 규칙 같은 최선의 언어학 도구를 사용하여 특정 언어에 맞춰진 평가 지표를 구축하는 거예요. 이는 모든 언어에 걸쳐 작동하는 보편 지표를 추구하는, MT 평가의 지배적 패러다임과 정반대예요. 보편 지표는 가치가 있지만, 정작 가장 필요한 곳 — 복잡한 형태론을 가지고, 학습 데이터가 제한적이며, 신경망 지표 학습 세트에 전혀 포함되지 않은 언어 — 에서 가장 취약해요.

세계의 많은 언어에 대해 기계 번역이 진전을 이루지 못하는 이유는 단지 말뭉치가 부족해서가 아니라, **진전이 어떤 모습인지조차 모르기 때문**이에요 — 번역 시스템이 개선되고 있는지 측정할 자동화된 평가 도구가 없는 거죠. LYSS는 존재하는 어떤 언어학 자원이든 활용하여, 한 언어씩 그 도구를 구축하려는 우리의 시도예요.

### 1.2 자동화된 지표는 프록시예요

여기에서 정의하는 모든 지표는 기계로 계산돼요. 이 지표들은 빠른 반복, 체계적인 비교, 회귀 탐지에 유용해요. 하지만 **사람의 판단을 대체하지는 못해요**. §5의 품질 등급은 휴리스틱 레이블이며 — 실제 사용 가능성은 오직 사람의 검토로만 확인할 수 있어요.

### 1.3 다중 신호 설계

단일 지표만으로는 번역 품질을 포착할 수 없어요. 어떤 번역은 chrF++ 중첩이 완벽하면서도 형태론적 검증에 실패할 수 있어요. FST 검사를 통과하면서도 잘못된 의미를 담을 수 있어요. 의미적으로는 정확하지만 대상 언어 입장에서 문체적으로 낯설 수도 있어요. §4의 종합 점수는 여러 독립적인 신호를 집계하며, 각 신호는 품질의 서로 다른 차원을 포착해요.

### 1.4 확장성

이 지표 목록은 닫혀 있지 않아요. 새로운 언어는 새로운 요구사항을 가져와요. 성조 언어를 위한 성조 정확도, 셈어 문자를 위한 발음 부호 정밀도, 크리어를 위한 음절 문자 정확도 같은 것들이죠. 아키텍처(MetricPlugin 프로토콜, 재정규화를 동반한 가중 종합)는 기존 점수를 깨뜨리지 않고 지표를 추가할 수 있도록 설계되었어요. 언어별 지표(예: CRK의 linter와 의미 검증기)는 `evalMetrics` 아래의 언어 카드에 선언되고 `eval_standards/`에서 로드돼요 — 하니스는 일반적인 행동 지표(코드 스위칭, 환각, 용어)만 기본 제공해요.

### 1.5 평가의 세 가지 차원

모든 런 카드는 세 가지 독립적인 차원을 측정해요:

```
Quality   — How good is the translation?   (composite score, §4)
Cost      — How much does it cost?          (cost metrics, §6)
Speed     — How fast does it run?           (speed metrics, §7)
```

이들은 독립적인 축이에요. 어떤 방법은 고품질이지만 비쌀 수 있고, 빠르지만 부정확할 수 있으며, 그 어떤 조합도 가능해요. 리더보드는 어느 차원으로든 정렬할 수 있게 해줘요. 비용 조정 점수(§6.3)는 차원들을 결합하는 유일한 지표예요.

### 1.6 검증 상태

이 명세의 모든 지표는 구현 상태(§3)와 구별되는 **검증 상태**를 가져요. 구현 상태는 코드가 존재하는지를 추적해요. 검증 상태는 해당 지표가 사람의 품질 판단과 상관관계가 있음이 입증되었는지를 추적해요.

| 검증 수준 | 의미 | 현재 지표 |
|------------------|---------|----------------|
| **✅ 외부 검증됨** | 출판된 사람-상관관계 연구가 존재함(WMT, 학술 논문) | `chrf_plus_plus`, `bleu`, `comet_score` |
| **⚡ 프록시 검증됨** | 고자원 언어에 대해 검증됨; 대상 LRL에 대해서는 미검증 | `comet_score` (EU 쌍에 대해 검증됨, CRK에 대해서는 아님) |
| **🔶 엔지니어링 휴리스틱** | 언어학적 원리 또는 관찰된 실패 모드로부터 설계됨; 사람-상관관계 데이터 없음 | `fst_acceptance_rate`, `equivalent_match_rate`, `semantic_score`, `code_switching_rate`, `hallucination_rate`, `terminology_adherence` |
| **🔲 미검증** | 아직 어떤 데이터로도 테스트되지 않음 | `morphological_accuracy`, `orthographic_accuracy`, `consistency_score` |

> **실무에서 이것이 의미하는 바.** 종합 점수(§4)는 모든 검증 수준의 지표를 집계해요. 이는 명시적인 설계 선택이에요. 우리는 구조적으로 근거를 갖춘 엔지니어링 휴리스틱(FST 수용)이 유럽어 쌍에 대해서만 검증된 신경망 지표(COMET)보다 포합어에 대해 더 유익하다고 믿어요. 하지만 이를 증명하지는 못했어요. 종합 점수는 각 대상 언어에 대해 사람-상관관계 연구가 완료될 때까지 검증된 품질 측정이 아니라 **엔지니어링 추정치**로 취급되어야 해요.
>
> **필요한 검증 실험**(`mt-evaluation-landscape.md` §6 및 `speaker-validation.md` 참조):
> 1. 사람 판단 상관관계 연구: 3명 이상의 이중 언어 화자가 평가한 200개 이상의 문장 쌍
> 2. 대표적인 말뭉치에 대한 FST 거짓 거부율 측정
> 3. 일반화를 테스트하기 위한 제2 언어 포팅(북부 사미어)
> 4. 동일한 데이터에 대한 COMET과의 직접 비교


---

## 2. 지표 목록 {#2-metric-inventory}

지표는 네 가지 범주로 구성돼요. 각 지표는 구현 상태, 척도, 수준(항목별, 말뭉치 수준, 또는 둘 다)을 가져요.

### 2.1 표면 지표

표면 지표는 예측된 번역을 참조 번역과 문자열 수준에서 비교해요. 언어학 도구가 필요 없고 — 그저 문자열 비교만 하면 돼요.

| ID | 지표 | 상태 | 척도 | 수준 | 구현 |
|----|--------|--------|-------|-------|---------------|
| `exact_match_rate` | Exact Match | ✅ 구현됨 | 0.0–1.0 | 둘 다 | 이진: 예측 == 참조인가? 말뭉치 비율 = 일치 수 / 전체. |
| `equivalent_match_rate` | Equivalent Match | ⚡ 부분 | 0.0–1.0 | 둘 다 | 예측 출력이 허용되는 변형 중 하나와 일치하는가? CRK의 경우: 결정론적 변형-클래스 규칙(어순, 정서법, 선택적 첨사, 표제어 동의어, 진행상 모호성)을 사용하여 CRK 평가 표준의 `CrkLinterMetric`(`eval_standards/crk/` 내)를 통해 구현됨. CRK 언어 카드의 `evalMetrics` 선언을 통해 자동으로 로드됨. 일반적인 교차 언어 구현은 말뭉치 내 항목별 `variants[]`가 필요함. |
| `chrf_plus_plus` | chrF++ | ✅ 구현됨 | 0–100 | 둘 다 | 문자 n-그램 F-점수(sacrebleu). 형태론적 변형에 강건함. 교착어/포합어를 위한 주요 표면 지표. 항목별은 `sentence_chrf`를 사용하고; 말뭉치는 `corpus_chrf`를 사용함. |
| `bleu` | BLEU | ✅ 구현됨 | 0–100 | 말뭉치 | 단어 수준 n-그램 정밀도(sacrebleu). **종합에서 제외됨** — 단어 수준 점수 산정은 형태론적 변형을 부당하게 벌점 처리함. MT 문헌과의 호환성을 위해 계산되고 보고됨. |
| `ter` | Translation Edit Rate | ✅ 구현됨 | 0–∞ (낮을수록 좋음) | 둘 다 | 예측과 참조 사이의 최소 편집 거리, 참조 길이로 정규화(sacrebleu `corpus_ter`). chrF++ 및 BLEU와 함께 계산됨. 종합에서 제외됨 — chrF++와 상관관계가 있어 둘 다 포함하면 표면 유사성을 이중 계산하게 됨. |
| `length_ratio` | Length Ratio | ✅ 구현됨 | 0–∞ (1.0이 이상적) | 둘 다 | 문자 단위의 `len(predicted) / len(reference)`. 잘림(<0.5)과 팽창/환각(>2.0)을 탐지함. 말뭉치 수준에서 항목들에 걸쳐 평균함. |

### 2.2 구조 지표

구조 지표는 번역의 언어학적 적격성(well-formedness)을 검증해요. 언어별 도구(FST 분석기, 형태소 파서)가 필요하며 형태론적으로 풍부한 언어에 가장 강력한 신호예요.

| ID | 지표 | 상태 | 척도 | 수준 | 구현 |
|----|--------|--------|-------|-------|---------------|
| `fst_acceptance_rate` | FST Acceptance | ✅ 구현됨 | 0.0–1.0 | 둘 다 | 유한 상태 변환기(GiellaLT)가 수용하는 출력 단어의 비율. 단어는 FST가 적어도 하나의 형태론적 분석을 반환하면 "유효"함. GiellaLT `.hfstol` 분석기를 가진 모든 언어에 사용 가능. |
| `morphological_accuracy` | Morphological Accuracy | 🔲 계획됨 | 0.0–1.0 | 둘 다 | 단어는 FST-유효하지만 잘못된 굴절(올바른 어근, 잘못된 접미사)을 가질 수 있음. 이 지표는 예측 단어의 FST 분석을 기대되는 형태론적 자질과 비교함. 말뭉치 내 항목별 형태론적 주석이 필요함. |
| `orthographic_accuracy` | Orthographic Accuracy | 🔲 계획됨 | 0.0–1.0 | 둘 다 | 문자별 정확성을 검증함: 크리어를 위한 SRO 마크론/곡절 부호 사용, 이누크티투트어를 위한 발음 부호, 오지브웨어를 위한 모음 길이 표시. 언어별 규칙 세트. |

> **구조 지표가 중요한 이유.** Meta의 OMT-1600 — 지금까지 출판된 가장 큰 MT 시스템(1,600개 언어) — 은 ChrF++, xCOMET, MetricX, BLASER 3로 평가해요. 이 중 어느 것도 형태론적 정확성을 검증하지 않아요. ChrF++는 문자 n-그램 중첩을 측정해요. 즉, 대상 언어처럼 *보이는* 문자열에 보상을 줘요. 포합어의 경우, 이는 참조와 많은 문자를 공유하는 형태론적으로 무효한 단어가 좋은 점수를 받는다는 뜻이에요. 우리의 FST 수용 지표는 이진 구조 테스트예요. 단어는 그 언어에서 유효한 형태이거나, 그렇지 않거나 둘 중 하나예요. 다른 어떤 MT 평가 프레임워크도 이를 대규모로 제공하지 않아요.

### 2.3 의미 지표

의미 지표는 임베딩이나 학습된 모델을 사용하여 의미 보존을 측정해요. 표면적으로는 다르지만 의미가 동등한 번역을 포착하고, 표면적으로는 유사하지만 의미적으로 잘못된 번역을 표시해요.

| ID | 지표 | 상태 | 척도 | 수준 | 구현 |
|----|--------|--------|-------|-------|---------------|
| `semantic_score` | Semantic Similarity | ⚡ 부분 | 0.0–1.0 | 둘 다 | CRK: CRK 평가 표준의 `CrkSemanticMetric`(`eval_standards/crk/` 내, 프록시)로부터의 평결 가중 점수. 보편: 문장 임베딩의 코사인 유사도(원천 + 예측 대 원천 + 참조). 모델 미정 — 저자원 언어를 지원해야 하며, 이는 대부분의 영어 중심 임베딩 모델을 배제함. |
| `comet_score` | COMET | ✅ 구현됨 | ~0.0–1.0 | 둘 다 | 학습된 MT 평가 지표(Unbabel). 사람의 품질 판단으로 학습됨. **종합에서 제외됨** — 학습 데이터가 고자원 유럽어 쪽으로 편향되어 있어; LRL에 대한 점수는 신뢰할 수 없음. `unbabel-comet`가 설치되면 계산됨. 저자원 경고 플래그와 함께 보고됨. 35개 아프리카 언어의 경우, 하니스는 `resolve_comet_model()`를 통해 AfriCOMET(`masakhane/africomet-mtl`)을 자동 선택하며, 이는 해당 언어들에 대해 사람-판단 상관관계가 더 우수함. |

> **COMET이 종합에서 제외되는 이유.** COMET은 WMT 사람 평가 데이터로 학습되었는데, 이는 압도적으로 고자원 유럽어 쌍이에요. 평원 크리어나 다른 LRL에 적용할 때, 모델의 내부 표현은 그런 언어들에 노출된 적이 없어요 — 근본적으로 다른 형태론 체계를 가진 언어들로부터 외삽하는 거죠. 점수는 여전히 방향적으로는 유용하지만(높은 COMET ≈ 일반적으로 더 유창하게 들리는 출력) 절대값은 보정되어 있지 않아요. 우리는 투명성을 위해 COMET을 보고하지만, 각 대상 언어에 대해 사람의 판단과 비교 검증할 수 있을 때까지 그것이 종합 점수에 영향을 주지 않게 해요.

> **아프리카 언어를 위한 AfriCOMET.** 각 언어 카드에는 해당 언어에 대해 어떤 특수 COMET 모델이 학습되었는지를 선언하는 `metricModelSupport` 필드(언어 카드 명세 §9 참조)가 있어요. 35개 아프리카 언어(yor, hau, ibo, amh, swa 등)의 경우, 카드는 AfriCOMET(`masakhane/africomet-mtl`)을 선언해요 — 이는 Masakhane 커뮤니티가 아프리카 언어 MT 사람 판단으로 미세 조정한 COMET 모델이에요. 하니스는 언어 카드에서 읽어들이는 `resolve_comet_model()`을 통해 권장 모델을 자동 선택하지만, 이는 `--comet-model`로 재정의할 수 있어요. 새로운 언어→모델 매핑 추가는 언어 카드를 보강하여 수행해요(Python 코드를 편집하는 것이 아니라).

### 2.4 행동 지표

행동 지표는 번역 출력에서 특정 실패 모드를 탐지해요. 품질을 직접 측정하지 않고 — 문제를 탐지해요.

| ID | 지표 | 상태 | 척도 | 수준 | 구현 |
|----|--------|--------|-------|-------|---------------|
| `code_switching_rate` | Code-Switching Rate | ✅ 구현됨 | 0.0–1.0 (낮을수록 좋음) | 둘 다 | 원천 언어(보통 영어)인 출력 단어의 비율. 유니코드 문자 분석 및/또는 원천 언어 단어 목록을 통해 탐지됨. 매우 흔한 LLM 실패 모드: 모델이 대상 언어 등가물을 모를 때 영어 단어를 삽입함. |
| `hallucination_rate` | Hallucination Rate | ✅ 구현됨 | 0.0–1.0 (낮을수록 좋음) | 둘 다 | 대응하는 원천 내용이 없는 출력 내용의 비율. 단어 정렬 또는 교차 언어 임베딩 중첩을 통해 탐지됨. 모델이 그럴듯하게 들리지만 조작된 번역을 생성하는 것을 포착함. |
| `terminology_adherence` | Terminology Adherence | ✅ 구현됨 | 0.0–1.0 | 둘 다 | 코칭 방법의 경우: 출력에 나타나는 규정 용어의 비율. 코칭 사전 데이터가 필요함. 모델이 전문가가 제공한 어휘를 존중하는지 측정함. |
| `consistency_score` | Cross-Entry Consistency | 🔲 계획됨 | 0.0–1.0 | 말뭉치 전용 | 모델이 동일한 원천 용어를 항목들에 걸쳐 동일하게 번역하는가? 낮은 일관성은 모델이 학습된 패턴을 적용하기보다 추측하고 있음을 시사함. 말뭉치 항목들에 걸쳐 반복되는 용어가 필요함. |

### 2.5 준수 지표

준수 지표는 번역이 구조적 무결성 — 자리 표시자, 서식, 타이포그래피 관례 — 을 보존하는지 검증해요. 이는 품질 점수가 아니라 품질 게이트 검사예요.

| ID | 지표 | 상태 | 척도 | 수준 | 구현 |
|----|--------|--------|-------|-------|---------------|
| `compliance_index` | Double-Pass Compliance | ✅ 구현됨 | 0.0–1.0 | 둘 다 | 가중 종합: 60% 변수 무결성(`{placeholder}` 변수가 보존되었는가?) + 20% 인용 부호 준수(언어 카드별 올바른 인용 문자) + 20% 대소문자 준수(대소문자 없는 언어에 라틴 문자 누출 없음). 원시 및 후처리 출력 둘 다에서 계산됨. `DoublePassCompliancePlugin`를 통해. |
| `repair_effectiveness` | Repair Effectiveness | ✅ 구현됨 | 0.0–1.0 | 말뭉치 | 번역 후 훅에 의해 자동으로 복구된 준수 위반의 비율. 품질 게이트가 원시 출력을 얼마나 개선했는지 측정함. |

> **준수가 종합에 포함되지 않는 이유.** 준수 지표는 번역 품질이 아니라 구조 보존(자리 표시자, 인용 부호)을 측정해요. 어떤 번역은 언어학적으로 완벽하지만 `{name}` 변수를 누락하여 준수에 실패할 수 있어요. 이들은 품질 게이트예요 — 나쁜 출력이 배포되는 것을 막지만, 번역 품질의 순위를 매기지는 않아요.

---

## 3. 지표 상태 등급

§2의 모든 지표는 네 가지 구현 등급 중 하나에 해당해요:

| 등급 | 의미 | 런 카드 동작 |
|------|---------|-------------------|
| **✅ 구현됨** | 코드가 존재하고, 테스트되었으며, 오늘날 런 카드에서 값을 산출함 | 런 카드의 숫자 값 |
| **⚡ 부분** | 언어별 프록시가 존재함(예: CRK)지만 보편 구현은 보류 중 | 프록시가 적용될 때 숫자 값, 그 외에는 `null` |
| **🔲 계획됨** | 명세화되었으나 아직 구현되지 않음 | 런 카드의 `null`(필드는 존재, 값은 부재) |
| **💡 제안됨** | 논의 중, 아직 명세화되지 않음 | 런 카드에 없음 |

지표가 계획됨 → 부분으로 이동하는 경우:
1. 언어별 구현이 병합되고 테스트됨
2. 적어도 하나의 언어 쌍에 대해 값을 산출함
3. 보편 구현은 보류 중으로 유지됨(이 명세에 문서화됨)

지표가 부분 → 구현됨으로 이동하는 경우:
1. 언어 비종속적 구현이 병합되고 테스트됨
2. 언어별 플러그인 없이 어떤 언어 쌍에 대해서도 값을 산출함
3. 이 문서가 ✅ 상태를 반영하도록 업데이트됨

지표가 계획됨 → 구현됨으로 이동하는 경우:
1. 구현이 병합되고 테스트됨
2. 적어도 하나의 실제 평가 실행에서 검증됨
3. 이 문서가 구현 세부 사항으로 업데이트됨

지표가 제안됨 → 계획됨으로 이동하는 경우:
1. 그 정의, 척도, 계산 방법이 합의됨
2. `🔲 Planned` 상태로 이 문서에 추가됨
3. 런 카드 스키마에 null 자리 표시자가 추가됨

---

## 4. 종합 점수 {#4-composite-score}

### 4.1 공식

종합 점수는 *사용 가능한* 모든 지표의 가중 평균이며, 사용 가능한 지표의 가중치가 합계 1.0이 되도록 재정규화돼요:

```
composite = Σ (weight_i × value_i)    for all available metrics
             ─────────────────────
             Σ weight_i               (re-normalization denominator)
```

지표는 런 카드에서의 값이 숫자(`null`가 아닌)이면 "사용 가능"해요. 지표를 사용할 수 없을 때 — 언어에 FST가 없거나, 지표가 아직 구현되지 않았기 때문 — 그 가중치는 나머지 지표에 비례적으로 재분배돼요.

**이는 종합 점수가 항상 한 실행 내에서 비교 가능하다는 뜻이에요:** 사용 가능한 어떤 지표든 사용하고 그에 따라 정규화해요. 실행 간 비교는 실행들이 동일한 사용 가능 지표 세트를 사용할 때 유효해요.

> [!WARNING]
> **실행 간 비교 가능성.** 지표 가용성이 다른 실행들을 비교할 때(예: 한 실행은 FST 점수가 있고 다른 실행은 없음), 종합 점수는 **직접 비교할 수 없어요**. 5개 지표로 계산된 종합 점수 0.72는 2개 지표로 계산된 종합 점수 0.72보다 더 많은 정보를 담고 있어요. 리더보드는 비교되는 실행들 간에 지표 적용 범위가 다를 때 경고를 표시해요. 엄밀한 비교를 위해서는 공유된 지표에만 대해 짝지은 부트스트랩 유의성 검정(§8.2)을 사용하세요.

### 4.2 입력 정규화

종합 공식에 들어가기 전에, 모든 지표는 1.0 = 완벽인 **0.0–1.0 척도**에 있어야 해요:

| 지표 | 원래 척도 | 정규화 |
|--------|-------------|---------------|
| `exact_match_rate` | 0.0–1.0 | 없음 (이미 정규화됨) |
| `equivalent_match_rate` | 0.0–1.0 | 없음 |
| `fst_acceptance_rate` | 0.0–1.0 | 없음 |
| `morphological_accuracy` | 0.0–1.0 | 없음 |
| `chrf_plus_plus` | 0–100 | **100으로 나눔** |
| `semantic_score` | 0.0–1.0 | 없음 |
| `code_switching_rate` | 0.0–1.0 (낮을수록 좋음) | **`1.0 - value`** (반전: 0% 코드 스위칭 = 1.0) |
| `hallucination_rate` | 0.0–1.0 (낮을수록 좋음) | **`1.0 - value`** (반전) |
| `terminology_adherence` | 0.0–1.0 | 없음 |

종합에서 제외된 지표(`bleu`, `comet_score`, `ter`, `length_ratio`, `consistency_score`)는 이 목적을 위해 정규화되지 않아요.

### 4.3 가중치 표 {#43-weight-tables}

#### 프로필 A: FST 적용 범위가 있는 언어

GiellaLT 유한 상태 변환기를 사용할 수 있는 언어용이에요. 구조 지표가 종합의 40%(FST 0.25 + 형태론적 정확도 0.15)를 차지하며, 이는 포합어/교착어에 대해 형태론적 정확성이 가장 중요함을 반영해요.

| 지표 | 목표 가중치 | 근거 |
|--------|--------------|-----------|
| `fst_acceptance_rate` | **0.25** | 최고 가중치. FST가 단어를 거부하면, 그것은 — 다른 지표가 무엇을 말하든 — 그 언어에서 유효한 형태가 아님. 이진적이고, 구조적으로 근거를 갖춤. |
| `morphological_accuracy` | **0.15** | 단어는 FST-유효하지만 형태론적으로 틀릴 수 있음(올바른 어근, 잘못된 굴절). FST와 함께, 구조 지표가 40%를 차지함. |
| `chrf_plus_plus` | **0.15** | 문자 n-그램 중첩: 포합어를 위한 최선의 표면 수준 프록시. 단어 수준 지표보다 교착어 형태론을 더 잘 다룸. |
| `semantic_score` | **0.15** | 표면 형태가 갈라질 때의 의미 보존. 구조 검사를 통과하는 의미적으로 잘못된 번역을 포착함. |
| `equivalent_match_rate` | **0.10** | 단 하나의 참조 번역뿐만 아니라 허용 가능한 변형에 보상함. 유연한 어순을 가진 언어에 중요함. |
| `code_switching_rate` | **0.05** | 원천 언어 누출을 벌점 처리함. 반전: 0% 코드 스위칭 = 1.0. |
| `terminology_adherence` | **0.05** | 규정 어휘를 존중하는 코칭 방법에 보상함. 코칭 데이터가 있을 때만 활성화됨. |
| `hallucination_rate` | **0.05** | 조작된 내용을 벌점 처리함. 반전: 0% 환각 = 1.0. |
| `exact_match_rate` | **0.05** | 최저 가중치. 포합어에 너무 엄격함 — 여러 올바른 번역이 존재함. 상한 검사로 유지됨. |

> **합계: 1.00.** 지표를 사용할 수 없을 때, 그 가중치는 사용 가능한 지표에 비례적으로 재분배돼요. 현재 `morphological_accuracy`(가중치 0.15)는 아직 계산되지 않은 유일한 프로필 A 지표예요 — 항목별 골드 스탠다드 형태론적 주석이 필요해요. 이 지표가 부재할 때, 나머지 8개 지표(총 가중치 0.85)는 각각 1/0.85 ≈ 1.176으로 스케일링돼요. 예를 들어:
> - FST: 0.25/0.85 = 0.294
> - chrF++: 0.15/0.85 = 0.176
> - semantic: 0.15/0.85 = 0.176

#### 프로필 B: FST 적용 범위가 없는 언어

형태론적 검증 도구가 없는 언어용이에요. 의미 지표와 표면 지표가 동일한 가중치를 가져요.

| 지표 | 목표 가중치 | 근거 |
|--------|--------------|-----------|
| `semantic_score` | **0.25** | 구조적 검증이 없을 때, 의미 보존이 사용 가능한 가장 강력한 신호임. |
| `chrf_plus_plus` | **0.25** | FST가 없을 때, 문자 수준 중첩이 주요 표면 검사가 됨. |
| `equivalent_match_rate` | **0.15** | 변형 매칭은 형태론적 도구 없이도 구조화된 품질 평가를 제공함. |
| `exact_match_rate` | **0.10** | FST가 없을 때, exact match가 유일한 구조적 검증 프록시로서 더 큰 가중치를 가짐. |
| `code_switching_rate` | **0.10** | 나쁜 출력을 포착할 FST가 없을 때 원천 언어 누출이 더 중요함. |
| `terminology_adherence` | **0.05** | 코칭 어휘 준수. |
| `hallucination_rate` | **0.05** | 조작된 내용 탐지. |
| `orthographic_accuracy` | **0.05** | 문자별 정확성이 부재한 FST가 남긴 공백의 일부를 채움. |

> **합계: 1.00.** `orthographic_accuracy`(가중치 0.05)는 계획되었으나 아직 계산되지 않았어요. 이것이 부재할 때, 나머지 7개 지표(총 가중치 0.95)는 1/0.95 ≈ 1.053으로 스케일링되며 — 종합에 미치는 영향은 미미해요.

> **가중치 진화에 관한 참고.** 이 가중치들은 잠정적이며 사람 검증 데이터가 축적됨에 따라 재보정될 거예요. 장기 목표는 가중치를 경험적으로 도출하는 거예요. 즉, 각 어족에 대해 어떤 자동화 지표가 사람의 품질 판단을 가장 잘 예측하는가?

### 4.4 종합에 새로운 지표 추가하기

종합에 새로운 지표를 추가하려면:

1. 척도, 수준, 계산 방법을 포함하여 `🔲 Planned` 상태로 §2에서 **정의해요**.
2. MetricPlugin으로(또는 핵심 지표의 경우 `tester.py`에서) **구현해요**.
3. 런 카드 점수 블록에 **null 자리 표시자를 추가해요**.
4. 기존 가중치를 하향 조정하여 §4.3에서 **목표 가중치를 할당해요**. 가중치는 합계 1.00이 되어야 해요.
5. 런 카드 스키마가 변경되면 **BENCHMARK_SPEC.md** §3을 **업데이트해요**.
6. **`scoring.py`** 가중치 표를 **업데이트해요**(코드는 이 문서를 반영해야 해요).
7. 지표가 실제 데이터에서 합리적인 값을 산출하는지 확인하기 위해 **검증 벤치마크를 실행해요**.
8. 상태를 `🔲`에서 `✅`로 변경하기 위해 **이 문서를 업데이트해요**.

---

## 5. 품질 등급 {#5-quality-tiers}

이 등급들은 자동화된 종합 점수에 대한 휴리스틱 레이블이에요. 각 수준의 출력에 대한 사람 검토를 바탕으로, 이 점수들이 실무에서 의미하는 경향을 설명해요. **이들은 검증된 품질 판단이 아니에요** — 실제 사용 가능성은 오직 사람 검토로만 확인할 수 있어요.

> [!IMPORTANT]
> **자동화된 등급은 잠정적이에요.** 이 레이블들은 검토를 위한 추천이지, 품질 선언이 아니에요. 자동화 지표에서 "배포 가능(Deployable)"에 도달한 방법은 커뮤니티 평가의 후보이지 — 배포할 제품이 아니에요. 이중 언어 화자에 의한 사람 검토만이 실제 사용 가능성을 확인할 수 있어요([BENCHMARK_SPEC §7](/docs/specifications/benchmark#7-human-validation) 참조). 화자들이 출력이 사용 가능하다고 동의함을 확인하는 커뮤니티 검토 없이는 어떤 방법도 배포 가능 이상을 주장할 수 없어요. 등급 경계는 사람 검증 데이터가 축적됨에 따라 언어마다 다를 수 있어요.

| 등급 | 종합 점수 범위 | 화자가 일반적으로 보는 것 |
|------|----------------|-------------------------------|
| **Baseline** | 0.00–0.30 | 언어별 지원이 없는 원시 LLM 출력. 형태론은 대부분 환각임. |
| **Emerging** | 0.30–0.50 | 일부 올바른 패턴이 나타남. 코칭이 도움이 되지만, 출력은 신뢰할 수 없음. |
| **Functional** | 0.50–0.70 | 출력을 화자가 알아볼 수 있음. 주요 문법 범주는 보통 올바름. 빈번한 형태론적 오류. |
| **Deployable** | 0.70–0.85 | 사람 검토를 동반한 초안 번역에 적합함. 대부분의 형태론이 올바름. |
| **Fluent** | 0.85–1.00 | 유능한 사람 번역에 근접함. 오류는 드물고 사소함. |

이 등급들은 잠정적이에요. 사람 검증 데이터가 축적되고 각 언어에 대해 "화자가 이를 유용하다고 느끼는" 임계값이 실제로 어디에 떨어지는지 알게 됨에 따라 재보정될 거예요. 이중 언어 화자들이 출력이 사용 가능하다고 동의함을 확인하는 커뮤니티 검토 없이는 어떤 방법도 **배포 가능(Deployable)** 이상을 주장할 수 없어요.

### 5.1 등급 임계값 (기계 판독 가능)

코드 구현의 경우, 임계값은 다음과 같아요(위에서 아래로 평가, 첫 일치가 우선):

```
composite >= 0.85  →  "fluent"
composite >= 0.70  →  "deployable"
composite >= 0.50  →  "functional"
composite >= 0.30  →  "emerging"
composite >= 0.00  →  "baseline"
composite is null  →  "unscored"
```

---

## 6. 비용 지표

비용 지표는 번역 방법의 재무적 효율성을 측정해요. 품질과 별도로 보고되며 — 비용은 종합 점수에 영향을 주지 않아요(비용 조정 보조 순위는 예외).

### 6.1 토큰 지표

| ID | 지표 | 계산 |
|----|--------|-------------|
| `prompt_tokens` | 총 입력 토큰 | 모든 API 호출에 걸친 `usage.prompt_tokens`의 합 |
| `completion_tokens` | 총 출력 토큰 | `usage.completion_tokens`의 합 |
| `reasoning_tokens` | 사고 연쇄(chain-of-thought) 토큰 | `usage.completion_tokens_details.reasoning_tokens`의 합 (대부분의 모델에서 0) |
| `cached_tokens` | 공급자 캐싱된 토큰 | `usage.prompt_tokens_details.cached_tokens`의 합 |
| `total_tokens` | 소비된 총 토큰 | `prompt_tokens + completion_tokens` |
| `tokens_per_entry` | 번역당 평균 토큰 | ✅ `total_tokens / entry_count` |

### 6.2 비용 지표

| ID | 지표 | 계산 | 사용 사례 |
|----|--------|-------------|----------|
| `total_cost_usd` | 총 실행 비용 | 공급자 보고 가격 × 토큰 수 | "이 벤치마크에 얼마나 들었나?" |
| `cost_per_entry_usd` | 말뭉치 항목당 비용 | `total_cost_usd / entry_count` | 동일한 말뭉치에서 방법들 비교 |
| `cost_per_1k_tokens` | 1,000 토큰당 비용 | ✅ `total_cost_usd / total_tokens × 1000` | 보편적인 LLM 효율성 — 말뭉치 간 비교 가능 |
| `cost_per_source_char` | 원천 문자당 비용 | `total_cost_usd / total_source_chars` | 토큰화가 다른 언어 간 비교 가능 |

> **왜 여러 비용 지표인가?** "항목"은 길이가 다양해요 — 3단어 구절은 한 단락보다 비용이 적어요. `cost_per_entry_usd`는 *동일한* 말뭉치에서 방법들을 비교하는 데 유용해요(동일한 항목 = 동일한 길이 = 공정한 비교). `cost_per_1k_tokens`는 표준 LLM 효율성 지표로, 말뭉치 *간* 비교가 가능해요. `cost_per_source_char`는 토큰화 차이를 정규화해요 — 동일한 문장이라도 모델의 어휘에 따라 다른 수의 토큰으로 토큰화될 수 있어요.

### 6.3 비용 조정 점수

유료 API를 사용하는 방법의 경우, 보조 순위를 계산해요:

```
cost_adjusted = composite / log2(1 + cost_per_entry_usd × 1000)
```

이는 좋은 점수를 효율적으로 달성하는 방법에 보상해요. 비용 조정 점수는 항상 단일 벤치마크(동일한 말뭉치) 내에서 계산되므로 항목별 비교가 공정하기 때문에 (토큰당이 아니라) `cost_per_entry_usd`를 사용해요.

비용 조정 점수는 **보조 순위**예요 — 주요 리더보드는 종합 점수로 순위를 매겨요. 이는 다른 질문에 답해요: "예산이 주어졌을 때, 어떤 방법이 최선의 결과를 주는가?"

---

## 7. 속도 지표

속도 지표는 번역 방법의 지연 시간과 처리량을 측정해요. 비용과 마찬가지로, 속도는 종합 점수에 영향을 주지 않아요.

| ID | 지표 | 계산 | 수준 |
|----|--------|-------------|-------|
| `elapsed_seconds` | 벽시계 실행 시간 | `time_end - time_start` | 실행 |
| `avg_latency_seconds` | 항목별 평균 지연 시간 | `Σ latency_s / n_entries` | 말뭉치 |
| `median_latency_seconds` | 항목별 중앙값 지연 시간 | `latency_s`의 50번째 백분위수 | 말뭉치 |
| `p95_latency_seconds` | 95번째 백분위수 지연 시간 | `latency_s`의 95번째 백분위수 | 말뭉치 |
| `tokens_per_second` | 처리량 | `total_tokens / elapsed_seconds` | 실행 |
| `entries_per_minute` | 번역 속도 | `entry_count / (elapsed_seconds / 60)` | 실행 |

---

## 8. 신뢰도와 유의성

### 8.1 부트스트랩 신뢰 구간

모든 핵심 지표는 부트스트랩 신뢰 구간(백분위수 방법, n=1000 재표본, α=0.05)을 지원해요:

| 지표 | 보고된 CI |
|--------|------------|
| `chrf_plus_plus` | ✅ `chrf_ci_lower`, `chrf_ci_upper` |
| `exact_match_rate` | ✅ `exact_match_ci_lower`, `exact_match_ci_upper` |
| `fst_acceptance_rate` | ✅ `fst_ci_lower`, `fst_ci_upper` (FST 데이터가 존재할 때만 계산됨) |
| `comet_score` | ✅ `comet_ci_lower`, `comet_ci_upper` (캐싱된 항목별 점수로부터 부트스트랩됨 — 중복 신경망 추론 없음) |
| `composite` | ✅ `composite_ci_lower`, `composite_ci_upper` (chrF++와 exact_match가 사용 가능할 때 계산됨) |
| 등급별 CI | ✅ `confidence_intervals_by_tier` — 난이도 수준별(등급 1-5) chrF++ 및 exact_match CI |

### 8.2 짝지은 부트스트랩 유의성 검정

두 방법을 비교하기 위해, 하니스는 짝지은 부트스트랩 재표본 검정을 계산해요:

```
H₀: The two methods perform equally on this corpus.
H₁: One method is significantly better.
```

p-값 < 0.05이고 차이의 신뢰 구간이 0을 제외하면, 그 차이는 95% 수준에서 통계적으로 유의해요.

---

## 9. 런 카드 점수 스키마

이 섹션은 런 카드 내 `scores` 블록의 계층적 구조를 정의해요. 이 스키마는 §2–§7에서 정의된 지표로부터 파생되며 동기화 상태를 유지해야 해요.

```jsonc
{
  "scores": {
    // §2.1 Surface metrics
    "exact_match_rate":       0.6613,       // 0.0–1.0
    "exact_matches":          41,           // count
    "equivalent_match_rate":  0.7258,       // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "equivalent_matches":     45,           // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "chrf_plus_plus":         80.65,        // 0–100 (sacrebleu native scale)
    "bleu":                   54.78,        // 0–100, NOT in composite
    "ter":                    42.3,         // ✅ implemented, 0–∞ (lower=better)
    "length_ratio":           1.03,         // ✅ implemented, ideal=1.0

    // §2.2 Structural metrics
    "fst_acceptance_rate":    1.0,          // 0.0–1.0
    "fst_accepted":           74,           // count
    "morphological_accuracy": null,         // 🔲 planned
    "orthographic_accuracy":  null,         // 🔲 planned

    // §2.3 Semantic metrics
    "semantic_score":         0.6842,       // ⚡ partial (CRK: eval_standards/crk CrkSemanticMetric)
    "comet_score":            null,         // nullable, NOT in composite
    "comet_model":            "",           // model ID used for COMET

    // §2.4 Behavioral metrics
    "code_switching_rate":    0.03,         // ✅ implemented (lower=better)
    "hallucination_rate":     0.01,         // ✅ implemented (lower=better)
    "terminology_adherence":  null,         // ✅ implemented (null when no glossary)
    "consistency_score":      null,         // 🔲 planned

    // §4 Composite
    "composite":              0.8988,       // 0.0–1.0
    "quality_tier":           "fluent",     // §5 tier label
    "cost_adjusted":          null,         // §6.3 secondary ranking

    // §7 Speed metrics (merged into scores block)
    "tokens_per_second":      4462.5,       // ✅ total_tokens / elapsed
    "entries_per_minute":     82.30,        // ✅ entry_count / (elapsed/60)
    "avg_latency_seconds":    0.234,
    "median_latency_seconds": 0.190,
    "p95_latency_seconds":    0.415,

    // §8.1 Confidence intervals
    "confidence_intervals": {
      "chrf_plus_plus":     { "ci_lower": 78.2, "ci_upper": 83.1 },
      "exact_match_rate":   { "ci_lower": 0.54, "ci_upper": 0.78 },
      "corpus_comet":       { "ci_lower": 0.71, "ci_upper": 0.76 }
    },
    "confidence_intervals_by_tier": {
      "1": { "corpus_chrf": { "ci_lower": 68.1, "ci_upper": 76.5 } },
      "3": { "corpus_chrf": { "ci_lower": 36.2, "ci_upper": 47.0 } }
    },

    // Breakdowns
    "by_difficulty":          {},           // scores grouped by difficulty tier
    "by_provenance":          {},           // scores grouped by entry provenance

    // Counts
    "total":                  62,
    "evaluated":              62,
    "errors":                 0
  },

  "totals": {
    // §6.1 Token metrics
    "prompt_tokens":          13985,
    "completion_tokens":      187822,
    "reasoning_tokens":       175726,
    "cached_tokens":          0,
    // §6.2 Cost metrics
    "total_cost_usd":         1.7114,
    "cost_per_entry_usd":     0.027603,
    "cost_per_source_char":   null          // 🔲 needs source char counting
  }
}
```

> **스키마 이력.** 이전 명세 초안은 별도의 `cost`, `speed`, `tokens` 블록을 제안했어요. 단순성을 위해 이들은 각각 `scores`과 `totals`으로 병합되었어요. 속도 지표(`tokens_per_second`, `entries_per_minute`, 지연 시간)는 `scores`에 있고; 토큰 수와 비용 수치는 `totals`에 있어요.

### 9.1 스키마–데이터베이스 매핑

런 카드 JSON은 Supabase에 `jsonb` 열로 전체가 저장돼요. 핵심 지표는 정렬/필터 성능을 위해 최상위 열로도 비정규화돼요:

| 런 카드 필드 | Supabase 열 | 유형 | 인덱스 |
|---------------|----------------|------|-------|
| `scores.composite` | `composite_score` | `real` | `idx_composite` |
| `scores.quality_tier` | `quality_tier` | `text` | — |
| `scores.chrf_plus_plus` | `chrf_plus_plus` | `real` | `idx_leaderboard` |
| `scores.exact_match_rate` | `exact_match_rate` | `real` | — |
| `scores.fst_acceptance_rate` | `fst_acceptance_rate` | `real` | — |
| `scores.bleu` | `corpus_bleu` | `real` | — |
| `scores.comet_score` | `comet_score` | `real` | — |
| `totals.total_cost_usd` | `total_cost_usd` | `real` | — |
| `totals.cost_per_entry_usd` | `cost_per_entry_usd` | `real` | — |
| `totals.cost_per_source_char` | `cost_per_source_char` | `real` | — |
| `scores.avg_latency_seconds` | `avg_latency_seconds` | `real` | — |
| `model_slug` | `model_slug` | `text` | `idx_model` |
| `condition` | `condition` | `text` | — |
| `dataset.id` | `dataset_id` | `text` | `idx_leaderboard` |
| `dataset.language_pair` | `language_pair` | `text` | — |
| `fingerprint.hash` | `fingerprint_hash` | `text` | `idx_fingerprint` |
| `scores.equivalent_match_rate` | `equivalent_match_rate` | `real` | — |
| `scores.semantic_score` | `semantic_score` | `real` | — |
| `scores.ter` | `ter` | `real` | — |
| `scores.length_ratio` | `length_ratio` | `real` | — |
| `scores.code_switching_rate` | `code_switching_rate` | `real` | — |
| `scores.hallucination_rate` | `hallucination_rate` | `real` | — |
| `scores.terminology_adherence` | `terminology_adherence` | `real` | — |
| `scores.tokens_per_second` | `tokens_per_second` | `real` | — |
| `scores.entries_per_minute` | `entries_per_minute` | `real` | — |
| `elapsed_seconds` | `elapsed_seconds` | `real` | — |
| *(전체 카드)* | `run_card` | `jsonb` | — |

새로운 지표가 구현되면, 해당 열은 `arena/migrations/`의 번호가 매겨진 마이그레이션을 통해 추가되어야 해요.

---

## 10. 코드–명세 동기화

### 10.1 정본 출처

이 문서(`arena/website/docs/specifications/scoring.md`)는 다음의 정본 출처예요:
- 지표 정의 (§2)
- 종합 가중치 표 (§4.3)
- 품질 등급 임계값 (§5.1)
- 비용 지표 공식 (§6.2)
- 런 카드 점수 스키마 (§9)

### 10.2 코드 미러

파일 `arena/mt_eval_harness/scoring.py`는 이 문서의 가중치 표와 등급 임계값을 반영해요. 이는 §4.3과 §5.1의 **코드 구현**이에요. 이 문서가 업데이트될 때:

1. `scoring.py`를 일치하도록 업데이트해요
2. 정렬을 검증하기 위해 `pytest tests/test_scoring_ssot.py`를 실행해요
3. 가중치를 요약하는 FAQ 및 웹사이트 문서를 업데이트해요

### 10.3 이 명세를 참조하는 문서

| 문서 | 참조하는 내용 | 동기화 유지 방법 |
|----------|-------------------|---------------------|
| `arena/website/docs/specifications/benchmark-spec.md` §4–§5 | 종합 공식, 가중치 표, 등급 임계값 | 이 문서를 상호 참조; 표를 복제하지 마세요 |
| `website/docs/getting-started/faq.md` | 단순화된 가중치 요약 | §4.3과 일치해야 함; 이 문서로 다시 링크 |
| `arena/website/docs/how-it-works.md` | 배포 가능 임계값 | §5와 일치해야 함 |
| `publish.py` via `scoring.py` | 가중치 딕셔너리 + 등급 함수 | 자동화 테스트가 일치를 검증함 |

---

## 부록 A: 종합에 포함되지 않은 지표 (그리고 그 이유)

| 지표 | 제외 이유 |
|--------|-------------|
| **BLEU** | 단어 수준 점수 산정은 포합어에서 형태론적 변형을 벌점 처리해요. 사소한 굴절 차이(올바른 의미, 약간 다른 접미사)가 완전한 빗나감으로 계산돼요. chrF++는 이를 문자 수준에서 더 잘 다뤄요. |
| **COMET** | WMT 데이터(고자원 유럽어 쌍)로 학습되었어요. LRL에 대한 점수는 신뢰할 수 없어요 — 모델이 다른 형태론 체계를 가진 언어들로부터 외삽하고 있어요. 점수 산정이 아니라 투명성을 위해 보고돼요. |
| **TER** | 편집 거리는 대부분의 사용 사례에서 chrF++와 상관관계가 있어요. 둘 다 포함하면 표면 유사성을 이중 계산하게 돼요. TER은 참조용으로 보고돼요. |
| **Length Ratio** | 품질 신호가 아니라 진단이에요. 1.02 비율과 0.98 비율 둘 다 괜찮아요. 극단적인 값만이 문제를 나타내요. |
| **Consistency Score** | 말뭉치 수준 전용 — 집계할 항목별 값이 없어요. 또한, 일부 비일관성은 정당해요(동일한 영어 단어 → 맥락에 따라 다른 대상 언어 번역). |
| **Compliance Index** | 품질 신호가 아니라 품질 게이트예요. 번역 정확성이 아니라 구조 보존(자리 표시자, 인용 부호)을 측정해요. |

## 부록 B: LYSS — 언어별 지표 구현

**LYSS** 프레임워크(Linguistically-informed Yield & Structural Scoring)는 표면 수준의 문자열 비교를 넘어서는 언어별 지표를 제공해요. LYSS에는 세 가지 핵심 구성 요소가 있어요:

- **LYSS-fst** — 형태론적 유효성(`fst_acceptance_rate`): 각 단어가 대상 언어에서 유효한 형태인가?
- **LYSS-eq** — 언어학적 등가성(`equivalent_match_rate`): 출력이 참조의 허용 가능한 변형인가?
- **LYSS-sem** — 의미 검증(`semantic_score`): 출력이 원천 의미를 보존하는가?

> **검증 상태: 🔶 엔지니어링 휴리스틱.** LYSS 지표는 사람의 품질 판단에 대해 검증되지 않았어요. 이들은 언어학적 원리(UAlberta ALTLab의 언어학자들이 구축한 FST, 사전, 문법 규칙)로부터 설계되었지만, LYSS 점수와 실제 번역 품질 사이의 상관관계는 측정되지 않았어요. 필요한 검증 실험에 대해서는 [화자 검증 프로토콜](/docs/specifications/speaker-validation)을 참조하세요.

| 언어 | 플러그인 | 위치 | LYSS 구성 요소 | 지표 키 | 비고 |
|----------|--------|----------|----------------|------------|-------|
| CRK (평원 크리어) | `CrkLinterMetric` | `eval_standards/crk/metrics.py` | **LYSS-eq** | `equivalent_match_rate` | 결정론적 변형-클래스 규칙: 어순, 정서법, 선택적 첨사, 표제어 동의어, 진행상 모호성, 포괄/배제. 항목별 `lint_verdict`(EXACT/EQUIVALENT/MISS/NO_OUTPUT)를 산출함. |
| CRK | `CrkSemanticMetric` | `eval_standards/crk/metrics.py` | **LYSS-sem** | `semantic_score` | 결정론적: FST 표제어 추출 + 사전 주석 + spaCy 내용어 중첩. 평결(EXACT_MATCH/VALID/GRAMMAR_ISSUES/PARTIAL/INCOMPLETE/WRONG/NO_OUTPUT)을 산출함. |
| GiellaLT 언어들 | `GiellaLTFSTMetric` | `plugins/giellalt_fst.py` | **LYSS-fst** | `fst_acceptance_rate` | 일반: CRK, SME, SMA, SMJ, SMN, SMS, FIN, NOB, IKU에 대해 작동함 — `.hfstol` 분석기를 가진 모든 언어. |

> **아키텍처 참고 (2026년 6월).** 언어별 LYSS 지표는 이제 `evalMetrics` 아래의 언어 카드에 선언되고 `plugin_discovery.py`에 의해 `eval_standards/<lang>/`에서 로드돼요. 이들은 메서드 플러그인 지표(참가자)가 아니라 **평가 표준**(심판)이에요. 이는 CRK를 대상으로 하는 모든 번역 방법이 LYSS에 의해 자동으로 점수가 매겨진다는 뜻이에요 — 메서드별 구성이 필요 없어요. `CrkFSTMetric`는 제거되었어요; 그 기능은 일반적인 `GiellaLTFSTMetric`로 완전히 다뤄져요.

## 부록 C: 검토 중인 지표

이들은 평가 중이지만 아직 §2에 들어갈 만큼 충분히 명세화되지 않은 아이디어예요:

| 아이디어 | 측정할 내용 | 장애 요소 |
|------|----------------------|----------|
| 유창성 (LM 퍼플렉시티) | 출력이 대상 언어에서 적격한 산문인가? | 대상 언어 LM이 필요함. 대부분의 LRL에 좋은 모델이 존재하지 않음. |
| 어조 일치 | 번역이 기대되는 격식 수준과 일치하는가? | 사회언어학적 분류기가 필요함. 연구 문제. |
| 문화적 적합성 | 문화적 참조가 올바르게 처리되는가? | 자동화할 수 없음 — 본질적으로 사람 검토가 필요함. |
| 담화 일관성 | 연속된 번역이 일관된 단락을 형성하는가? | 문장 수준이 아니라 문서 수준 평가가 필요함. |

---

## 참고문헌

이 명세 전반에 걸쳐 인용된 학술 논문, 도구, 언어 자원.

### 표면 지표

1. Popović, M. (2017). "chrF++: words helping character n-grams." *Proceedings of the Second Conference on Machine Translation (WMT 2017)*, pp. 612–618. Copenhagen, Denmark.

2. Papineni, K., Roukos, S., Ward, T., & Zhu, W.-J. (2002). "BLEU: a method for automatic evaluation of machine translation." *Proceedings of the 40th Annual Meeting of the Association for Computational Linguistics (ACL 2002)*, pp. 311–318. Philadelphia, PA.

3. Post, M. (2018). "A Call for Clarity in Reporting BLEU Scores." *Proceedings of the Third Conference on Machine Translation (WMT 2018)*, pp. 186–191. Belgium, Brussels. Reference implementation: [sacrebleu](https://github.com/mjpost/sacrebleu).

4. Snover, M., Dorr, B., Schwartz, R., Micciulla, L., & Makhoul, J. (2006). "A Study of Translation Edit Rate with Targeted Human Annotation." *Proceedings of the 7th Conference of the Association for Machine Translation in the Americas (AMTA 2006)*, pp. 223–231. Cambridge, MA.

### 신경망 지표

5. Rei, R., Stewart, C., Farinha, A. C., & Lavie, A. (2020). "COMET: A Neural Framework for MT Evaluation." *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP 2020)*, pp. 2685–2702. Online.

6. Juraska, J., Finkelstein, M., Deutsch, D., Siddhant, A., Miber, D., & Markl, A. (2023). "MetricX-23: The Google Submission to the WMT 2023 Metrics Shared Task." *Proceedings of the Eighth Conference on Machine Translation (WMT 2023)*. Singapore.

7. Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2020). "BERTScore: Evaluating Text Generation with BERT." *Proceedings of the Eighth International Conference on Learning Representations (ICLR 2020)*. Addis Ababa, Ethiopia.

8. Sellam, T., Das, D., & Parikh, A. (2020). "BLEURT: Learning Robust Metrics for Text Generation." *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020)*, pp. 7881–7892. Online.

### 형태론 및 언어학 도구

9. Lindén, K., Silfverberg, M., Axelson, E., Hardwick, S., & Pirinen, T. (2011). "HFST—Framework for Compiling and Applying Morphologies." *Systems and Frameworks for Computational Morphology (SFCM 2011)*, Communications in Computer and Information Science, vol. 100, pp. 67–85. Springer, Berlin, Heidelberg.

10. Sánchez-Cartagena, V. M., & Toral, A. (2024). "MorphEval: Automatic Evaluation of Morphological Capabilities of Machine Translation Systems." *Machine Translation*, vol. 38, pp. 1–28.

### 오류 분류 및 진단 평가

11. Popović, M. (2011). "Hjerson: An Open Source Tool for Automatic Error Classification of Machine Translation Output." *The Prague Bulletin of Mathematical Linguistics*, no. 96, pp. 59–68.

12. Dreyer, M. & Marcu, D. (2012). "HyTER: Meaning-Equivalent Semantics for Translation Evaluation." *Proceedings of the 2012 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2012)*, pp. 162–171. Montréal, Canada.

13. Reiter, E. & Belz, A. (2009). "An Investigation into the Validity of Some Metrics for Automatically Evaluating Natural Language Generation Systems." *Computational Linguistics*, vol. 35, no. 4, pp. 529–558. (FUSE를 포함한 자질 기반 평가 지표에 관한 관련 연구.)

### 환각 탐지

14. Raunak, V., Menezes, A., & Junczys-Dowmunt, M. (2021). "The Curious Case of Hallucinations in Neural Machine Translation." *Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2021)*, pp. 1172–1183. Online.

15. Guerreiro, N. M., Voita, E., & Martins, A. F. T. (2023). "Looking for a Needle in a Haystack: A Comprehensive Study of Hallucinations in Neural Machine Translation." *Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2023)*, pp. 1059–1075. Dubrovnik, Croatia.

### 크리어 언어 자원

16. Wolfart, H. C. (1973). "Plains Cree: A Grammatical Study." *Transactions of the American Philosophical Society*, vol. 63, no. 5, pp. 1–90.

17. Wolvengrey, A. (2001). *nêhiyawêwin: itwêwina / Cree: Words.* Canadian Plains Research Center, University of Regina.

### 데이터 거버넌스

18. First Nations Information Governance Centre. "The First Nations Principles of OCAP®." [https://fnigc.ca/ocap-training/](https://fnigc.ca/ocap-training/). (OCAP®은 First Nations Information Governance Centre의 등록 상표예요.)

19. Carroll, S. R., Garba, I., Figueroa-Rodríguez, O. L., Holbrook, J., Lovett, R., Materechera, S., Parsons, M., Raseroka, K., Rodriguez-Lonebear, D., Rowe, R., Sara, R., Walker, J. D., Anderson, J., & Hudson, M. (2020). "The CARE Principles for Indigenous Data Governance." *Data Science Journal*, vol. 19, no. 1, p. 43.