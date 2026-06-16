---
sidebar_position: 1
title: "MT 평가"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "How the composite score is computed"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Evaluation Datasets"
    to: /docs/leaderboard/datasets
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "The rules, applied"
---
# MT 평가

> **요약.** 이 페이지에서는 리더보드 제출 기준, 점수 측정 지표(chrF++, FST acceptance, exact match, equivalent match, semantic score), 부정행위 방지 정책, 검증 등급, 제출 워크플로를 정의해요. 평가 데이터에 노출된 적이 있는 방법은 자격이 박탈돼요.

champollion에는 번역 방법의 **재현 가능한 벤치마킹**을 위해 설계된 기계 번역 평가 프레임워크가 포함되어 있어요 — 특히 표준 MT 벤치마크가 존재하지 않고 품질 주장을 검증하기 어려운 저자원 언어 및 토착어를 대상으로 해요.

---

## 리더보드

핵심은 **[Method Leaderboard](https://champollion.dev/leaderboard)** 예요 — 연구자와 커뮤니티 구성원이 지문화된 재현 가능한 평가로 번역 방법을 제출하고 비교하는, Supabase 기반의 실시간 스코어보드예요.

모든 제출에는 다음이 포함돼요:

- **지문화된 파이프라인** — 특정 Git 커밋 및 config 해시에 연결되므로, 결과를 그것을 생성한 정확한 코드로 추적할 수 있어요
- **버전 관리된 데이터셋** — 콘텐츠 해시 처리되고 버전이 지정되며, 점수는 동일한 데이터셋 버전 내에서만 비교할 수 있어요
- **표준화된 지표** — 모든 점수는 공유 평가 하니스에 의해 계산되어 구현 차이를 제거해요
- **신뢰 등급** — self-benchmarked, GDS Verified, 또는 Community Validated
- **비용 추적** — 제출당 API 비용으로, 비용–품질 트레이드오프가 투명하게 드러나요

리더보드는 현재 다섯 가지 지표를 추적해요. 세 가지는 모든 언어에 적용되고, 두 가지는 Plains Cree에 사용할 수 있으며 확장하면서 일반화할 예정이에요:

| 지표 | 유형 | 측정 대상 |
|--------|------|------------------|
| **chrF++** | 문자 n-gram F-score | 주요 품질 지표 — 특히 형태론적으로 풍부한 언어에서 인간 판단과 잘 상관해요 |
| **Exact Match** | 완벽 일치 비율 | 엄격한 정확도 — 번역이 정확히 gold standard와 일치하는 빈도는 얼마나 되나요? |
| **FST Acceptance** | 형태론 게이트 통과율 | 유한 상태 변환기 검증을 사용하는 방법용 — 출력 중 형태론적으로 유효한 비율은 얼마나 되나요? |
| **Equivalent Match** | 허용 가능한 변형 비율 | 참조 또는 허용 가능한 변형(어순, 정서법 관례)과 일치하는 비율이에요. 현재 CRK이며 일반화 중이에요. |
| **Semantic Score** | 의미 충실도 | 의미 보존 — 표면 형태와 관계없이 번역이 의도한 의미를 포착하나요? 현재 CRK이며 일반화 중이에요. |

:::info 전체 지표 모음
[Scoring Specification](/docs/specifications/scoring)에서 5개 범주에 걸친 전체 19개 지표 목록, composite score 공식, 가중치 표, 품질 등급 임계값을 정의해요.
:::

**[→ 리더보드 보기](https://champollion.dev/leaderboard)**

---

## 사용 가능한 데이터셋

### EDTeKLA Development Set v1

English→Plains Cree(SRO) 번역을 위해 구축된 첫 번째 평가 데이터셋이에요. University of Alberta의 [EdTeKLA research group](https://spaces.facsci.ualberta.ca/edtekla/)에서 만들었어요.

| 속성 | 값 |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **언어 쌍** | EN → CRK (Plains Cree, SRO 정서법) |
| **항목 수** | 404 (`master_corpus.json`: gold 62개 + 교과서 342개); 총 548개 사용 가능 |
| **라이선스** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| **출처** | `gold_standard` (화자 검증), `textbook` (출판된 교육 자료) |

### FLORES+ Devtest — 개발 용도 전용

> [!WARNING]
> **FLORES+는 개발 및 디버깅에 사용할 수 있지만 공식 리더보드 평가에는 사용되지 않아요.** FLORES+(원래 Meta FLORES-200)는 프런티어 LLM이 거의 확실히 학습했을 널리 공개된 벤치마크 데이터셋이에요. FLORES+에 대한 점수는 LLM 기반 방법의 실제 번역 품질을 신뢰성 있게 반영하지 못해요. 비LLM 방법(FST, 규칙 기반, 미세 조정 NMT)은 영향을 덜 받지만, FLORES+ 점수는 여전히 리더보드에 게시되지 않아요.

FLORES+ 픽스처는 파이프라인 스모크 테스트, 교차 언어 검증, 개발 용도로 `test/benchmark/fixtures/`에서 계속 사용할 수 있어요. 공식 평가에는 병렬 형태로 공개되지 않은 인간 작성 텍스트로 구축한 맞춤형 코퍼스를 사용해요.

전체 데이터셋 스키마, 난이도 등급, 직접 만드는 방법은 [Evaluation Datasets](/docs/leaderboard/datasets)를 참조하세요.

:::danger 평가 데이터로 학습하지 마세요

**이 데이터셋은 평가 전용이에요.** 평가 데이터로 학습되거나, 미세 조정되거나, few-shot 프롬프트로 사용되거나, 그 밖의 방식으로 평가 데이터에 노출된 방법은 인위적으로 부풀려진 점수를 산출하며 **리더보드에서 자격이 박탈돼요.**

이는 권고 사항이 아니라 평가 무결성의 가장 중요한 단 하나의 규칙이에요. 학습에는 별도의 코퍼스를 사용하세요. 평가 세트는 개발 중에 모델이 보지 못한 상태로 유지되어야 해요.

코칭 데이터나 few-shot 예시를 사용한다면, 그것들은 **완전히 별개의 출처**에서 와야 해요. 의심스럽다면 포함하지 마세요.
:::

:::warning LLM 비결정성

LLM 출력은 비결정적이에요. 점수는 특정 모델 버전 및 API 구성하에서 특정 시점의 측정값을 나타내요. 모델 제공자는 가중치, 디코딩 전략, 안전 필터를 언제든지 업데이트할 수 있으며, 이로 인해 실행 간 점수 변동이 발생할 수 있어요. 리더보드는 모든 제출에 대해 정확한 모델 slug와 타임스탬프를 기록해요.
:::

---

## 좋은 방법의 조건

모든 방법이 동등하게 만들어진 것은 아니에요. 엄밀한 작업과 부풀려진 점수를 구분하는 기준은 다음과 같아요.

### 강력한 방법의 특성

- **학습 데이터와 평가 데이터의 명확한 분리** — 개발, 튜닝, 프롬프트 엔지니어링, few-shot 예시 선택 중에 방법이 평가 세트를 본 적이 없어요
- **재현 가능성** — 다른 사람이 저장소를 클론하고 하니스를 실행하여 동일한 점수를 얻을 수 있어요(LLM 비결정성 범위 내에서)
- **문서화** — [method card](/docs/specifications/methods)에 방법이 무엇을 하는지, 어떤 도구를 사용하는지, 한계가 무엇인지 설명되어 있어요
- **범위에 대한 정직성** — 방법이 하나의 언어 쌍에만 적용된다면 그렇다고 밝히고, 특정 형태론적 패턴에서 성능이 저하된다면 그것을 문서화하세요
- **커뮤니티 인식** — 토착어의 경우 방법이 데이터 주권을 존중해요. 언어 커뮤니티와 협의했거나 공개적으로 라이선스된 데이터만 사용했어요

### 위험 신호(자격 박탈 사유)

| 위험 신호 | 문제가 되는 이유 |
|----------|--------------------|
| 평가 데이터로 학습 | 평가의 목적을 완전히 무력화해요. 부풀려진 점수는 모두를 오도해요. |
| 결과 선별 | 10번 실행하고 다른 실행은 공개하지 않은 채 최고 실행만 제출 |
| 미공개 후처리 | 점수 산정 전에 출력을 수동으로 수정 |
| 오염된 코칭 데이터 | 평가 세트 예시를 few-shot 프롬프트나 사전 항목으로 사용 |
| 출처 없이 상업적 준비 완료를 주장 | 방법이 CC BY-NC-SA 데이터를 사용한다면 상업적으로 준비된 것이 아니에요 |

### 검증 등급

검증 등급은 **누가 결과를 검증했는지**를 설명하며, [Scoring Specification, §5](/docs/specifications/scoring#5-quality-tiers)에 정의된 품질 등급(Baseline → Fluent)과는 별개예요. 품질 등급은 자동화된 composite score가 무엇을 의미하는지 설명해요.

| 등급 | 의미 | 획득 방법 |
|------|---------|--------------|
| **Self-benchmarked** | 직접 하니스를 실행하고 결과를 제출했어요 | run card와 함께 PR을 열기 |
| **GDS Verified** | champollion 관리자가 결과를 재현했어요 | 설치 가능한 플러그인으로 방법을 제출 |
| **Community Validated** | 거버넌스 조직이 gold-standard 및 커뮤니티 검토에 대해 실행했어요 | 거버넌스 조직에 방법 코드를 제출 |

---

## 제출 방법

1. **방법 구축** — 방법 인터페이스는 [Building a Method](/docs/specifications/methods)를 참조하세요
2. **하니스 실행** — 설정 및 사용법은 [Eval Harness](/docs/specifications/harness)를 참조하세요
3. **run card 생성** — 하니스는 점수, 지문, 메타데이터가 포함된 JSON run card를 생성해요
4. **PR 열기** — [eval harness repository](https://github.com/gamedaysuits/arena)에 run card를 제출하세요
5. **리더보드에 등장** — 병합되면 결과가 [Method Leaderboard](https://champollion.dev/leaderboard)에 표시돼요

---

## 향후 방향

- **포괄적인 모델 비교 실행** — 맞춤형 평가 코퍼스(공개 벤치마크가 아님)를 사용하여 champollion 언어 전반에 걸쳐 프런티어 모델(GPT-4o, Claude, Gemini 등)을 체계적으로 평가
- **더 많은 언어 쌍** — 커뮤니티가 검증한 데이터셋이 마련됨에 따라 Quechua, Inuktitut 및 기타 저자원 언어
- **데이터셋 가져오기** — 외부 평가 데이터셋(WMT, Tatoeba 등)을 champollion 평가 형식으로 변환하는 도구
- **자동 재실행** — 모델 버전 변경을 감지하고 벤치마크를 재실행하여 점수 변동을 추적

---

## 더 보기

- **[Method Leaderboard](https://champollion.dev/leaderboard)** — 실시간 점수 및 제출
- **[Eval Harness](/docs/specifications/harness)** — 평가 실행 방법
- **[Evaluation Datasets](/docs/leaderboard/datasets)** — 데이터셋 형식 및 사용 가능한 데이터셋
- **[Building a Method](/docs/specifications/methods)** — 방법 인터페이스 사양
- **[Run Card Specification](/docs/specifications/run-card)** — run card JSON 스키마
- **[Benchmark Specification](/docs/specifications/benchmark)** — 평가 프로토콜, 코퍼스 형식, 주권
- **[Scoring Specification](/docs/specifications/scoring)** — 지표, composite 가중치, 품질 등급의 SSOT