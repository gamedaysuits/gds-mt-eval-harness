---
sidebar_position: 2
title: "자주 묻는 질문"
related:
  - label: "How It Works"
    to: /docs/how-it-works
    kind: doc
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Glossary"
    to: https://champollion.dev/glossary
    kind: glossary
    note: "Plain-language definitions for every technical term"
---
# 자주 묻는 질문

> **핵심 요약.** MT Eval Arena에 대해 자주 묻는 질문에 답해요 — 채점 방식, 실격 사유, FST가 없는 언어 처리 방법, 모델 및 파라미터 권장 사항, 제출 절차를 다뤄요.

---

## 채점 및 메트릭

### 하니스는 어떤 메트릭을 계산하나요?

하니스는 Plains Cree(현재 벤치마크 언어)에 대해 다섯 가지 메트릭을 계산해요. 세 가지는 언어에 구애받지 않으며 모든 언어에서 작동해요. 나머지 두 가지는 현재 CRK 전용 플러그인에 의존하는데, 더 많은 언어로 확장하면서 일반화할 예정이에요.

| 메트릭 | 척도 | 측정 대상 | 상태 |
|--------|-------|-----------------|--------|
| **chrF++** | 0–100 | 예측 번역과 참조 번역 간 문자 n-gram 중첩. 형태론적으로 풍부한 언어에 가장 적합한 표면 메트릭. sacrebleu의 기본 채점을 사용. | ✅ 모든 언어 |
| **Exact match** | 0.0–1.0 | 정규화 후 예측이 참조와 정확히 일치하는 항목의 비율. | ✅ 모든 언어 |
| **FST acceptance** | 0.0–1.0 | 유한 상태 변환기(형태소 분석기)가 수용한 출력 단어의 비율. FST 바이너리가 제공된 경우에만 계산됨. | ✅ FST가 있는 모든 언어 |
| **Equivalent match** | 0.0–1.0 | 참조 또는 허용 가능한 변형과 일치하는 항목의 비율 — 어순, 정서법 관례, 방언 차이를 고려함. | ⚡ CRK (일반화 중) |
| **Semantic score** | 0.0–1.0 | 의미 보존 점수 — 표면 형태와 관계없이 번역이 의도된 의미를 얼마나 잘 포착하는가? | ⚡ CRK (일반화 중) |

추가 메트릭도 계획되어 있어요: **형태론적 정확도(morphological accuracy)**, **코드 전환 탐지(code-switching detection)**, **용어 준수(terminology adherence)**, **환각 탐지(hallucination detection)**. 전체 19개 메트릭 목록은 [Scoring Specification §2](/docs/specifications/scoring#2-metric-inventory)를 참조하세요.

### 복합 점수(composite score)는 어떻게 계산하나요?

복합 점수는 사용 가능한 메트릭의 가중 평균으로, 0.0–1.0 척도로 정규화돼요. 가중치는 두 가지 프로필로 정의돼요:

- **Profile A** (FST가 있는 언어): 9개 메트릭, 구조적 메트릭(FST + 형태론적 정확도)이 복합 가중치의 40%를 차지
- **Profile B** (FST가 없는 언어): 8개 메트릭, 의미 메트릭과 chrF++가 동일한 최상위 가중치를 차지

메트릭을 사용할 수 없는 경우, 해당 가중치는 나머지 메트릭에 비례하여 재분배돼요. 즉, 초기 단계의 벤치마크(chrF++와 exact match만 사용 가능한 경우)도 여전히 유효한 복합 점수를 산출해요 — 유효 가중치는 단지 사용 가능한 메트릭을 반영할 뿐이에요.

**전체 가중치 표, 정규화 규칙, 제외 근거는 [Scoring Specification §4](/docs/specifications/scoring#4-composite-score)에 있어요.** 하니스 코드는 `mt_eval_harness/scoring.py`에서 이 표를 그대로 반영해요. chrF++는 가중치 적용 전에 100으로 나눠 정규화하고, 코드 전환율과 환각율은 반전돼요(낮을수록 좋음).

### 품질 등급(quality tier)이란 무엇인가요?

품질 등급은 복합 점수 범위에 매핑된 휴리스틱 레이블이에요. 점수가 실질적으로 *무엇을 의미하는지* 전달하는 데 도움이 돼요:

| 등급 | 복합 점수 범위 | 해석 |
|------|----------------|----------------|
| **Baseline** | 0.00 – 0.30 | 유용한 품질 미만. 메서드의 상당한 개선이 필요함. |
| **Emerging** | 0.30 – 0.50 | 가능성을 보임. 일부 번역은 정확하지만 일관성이 없음. |
| **Functional** | 0.50 – 0.70 | 사람의 검토와 함께 참고용으로 사용 가능. 검토 없는 배포에는 부적합. |
| **Deployable** | 0.70 – 0.85 | 주기적 검토와 함께 프로덕션 사용 준비 완료. 소유권 이전 자격 조건을 발동시킴. |
| **Fluent** | 0.85 – 1.00 | 원어민에 가까운 품질. 감독 없는 배포에 적합. |

### 품질 등급과 검증 등급(verification tier)의 차이는 무엇인가요?

**품질 등급**은 *자동화된 점수가 무엇을 의미하는지*(Baseline → Fluent)를 설명해요. **검증 등급**은 *누가 결과를 검증했는지*를 설명해요:

| 검증 등급 | 의미 |
|-------------------|---------------|
| **Self-benchmarked** | 제출자가 직접 하니스를 실행함. 점수는 그럴듯하지만 검증되지 않음. |
| **GDS Verified** | 메인테이너가 제출된 메서드 구성을 사용하여 결과를 재현함. |
| **Community Validated** | 이중 언어 화자가 번역을 검토하고 품질을 확인함. |

메서드는 "Deployable" 품질이면서도 "Self-benchmarked" 검증에 불과할 수 있어요 — 점수는 훌륭해 보이지만 아무도 독립적으로 확인하지 않았다는 뜻이에요.

---

## 제출 및 실격

### 무엇 때문에 제출이 실격되나요?

다음의 경우 제출이 거부되거나 플래그가 지정돼요:

1. **메서드가 평가 데이터에 노출된 경우.** 평가 데이터셋의 항목을 학습, 파인튜닝, few-shot 프롬프팅 또는 기타 방식으로 사용했다면 점수가 인위적으로 부풀려져요. 여기에는 프롬프트에 참조 번역을 사용하는 것도 포함돼요.
2. **실행 카드(run card)가 무결성 검사에 실패한 경우.** 핑거프린트가 구성과 일치해야 해요. 변조된 실행 카드는 거부돼요.
3. **메서드가 TranslationMethod 프로토콜을 구현하지 않은 경우.** 하니스는 `translate(entries, config) → results`를 기대해요. 하니스를 우회하는 커스텀 통합은 허용되지 않아요.

### 여러 번 제출할 수 있나요?

네. 리더보드는 모든 제출을 추적해요. 반복할 수 있어요 — 수십 개의 실험을 실행하고 최고의 결과만 제출하세요. 각 제출은 고유한 핑거프린트를 기록하므로, 어떤 실행이 어떤 점수를 산출했는지에 대한 모호함이 없어요.

### 점수를 검증받으려면 어떻게 하나요?

1. **Self-benchmarked (자동):** 모든 제출은 여기서 시작해요.
2. **GDS Verified:** 메서드를 재현 가능한 패키지(코드 + 구성 + 코칭 데이터)로 제출하세요. 메인테이너가 동일한 데이터셋에 대해 다시 실행하여 점수가 일치하는지 확인해요.
3. **Community Validated:** 원주민 언어의 경우, 이중 언어 화자가 번역 샘플을 검토해야 해요. 이것은 자동화할 수 없어요 — 커뮤니티 참여가 필요해요.

### 제출 API가 운영 중인가요?

아직 아니에요. `https://mtevalarena.org/api/leaderboard/submit` 엔드포인트는 향후 목표예요. 현재 제출은 `results/` 디렉토리에 실행 카드 JSON을 포함하여 [eval harness repo](https://github.com/gamedaysuits/arena)에 풀 리퀘스트로 진행해야 해요.

---

## 모델 및 파라미터

### 어떤 모델을 사용해야 하나요?

단 하나의 최고 모델은 없어요 — 언어 쌍, 예산, 접근 방식에 따라 달라져요. 일반적인 지침은 다음과 같아요:

| 언어 유형 | 권장 시작점 | 이유 |
|---------------|---------------------------|-----|
| **고자원** (프랑스어, 스페인어, 일본어) | `google/gemini-2.5-flash` 또는 `gpt-4o-mini` | 빠르고 저렴하며 강력한 베이스라인 |
| **일부 LLM 커버리지가 있는 저자원** (케추아어, 요루바어) | `google/gemini-2.5-pro` 또는 `anthropic/claude-sonnet-4` | 더 큰 모델은 더 나은 잠재 지식을 가짐 |
| **다종합어 / 매우 저자원** (Plains Cree, 이누크티투트어) | `google/gemini-2.5-pro` + 코칭 | 코칭 데이터가 모델 선택보다 더 중요함. OMT-1600은 일부 다종합어(예: R1 등급의 CRK)를 포함하지만 표준 BPE 토큰화를 사용함 — Arena에서 베이스라인으로 벤치마크하세요. |

eval 하니스는 OpenRouter를 사용하므로 OpenRouter에서 사용 가능한 모든 모델을 벤치마크할 수 있어요. 사용 가능한 모델을 확인하려면 `champollion models --method llm`을 실행하세요.

### 어떤 temperature를 사용해야 하나요?

번역에는 일반적으로 낮을수록 좋아요:

| Temperature | 효과 | 권장 용도 |
|-------------|--------|-----------------|
| **0.0 – 0.2** | 고도로 결정론적이고 일관된 출력 | 프로덕션 메서드, 최종 벤치마크 |
| **0.3 – 0.5** | 약간의 변동, 때때로 더 창의적 | 탐색, 초기 반복 |
| **0.6+** | 높은 변동, 예측 불가능 | MT 벤치마킹에는 권장하지 않음 |

Temperature는 실행 카드에 기록되므로, 서로 다른 temperature는 서로 다른 핑거프린트를 생성해요 — 별개의 실험으로 취급돼요.

### 코칭 데이터가 도움이 되나요?

네, 상당히 — 저자원 언어의 경우에요. 코칭 데이터(문법 규칙, 사전 항목, 스타일 노트)는 LLM 시스템 프롬프트에 주입돼요. Plains Cree의 경우, 범용 LLM은 다종합어에 대한 노출이 제한적이고 형태론적 인식이 없기 때문에, 다종합어에 대해 코칭된 메서드가 원시 LLM 메서드를 일관되게 능가해요. CRK용으로 특별히 학습된 OMT-1600조차도 다종합어 형태론을 구조적으로 표현할 수 없는 표준 BPE 토큰화를 사용해요. 코칭 데이터는 모델에 부족한 언어적 맥락을 제공해요.

고자원 언어(프랑스어, 스페인어)의 경우, 모델이 이미 강력한 베이스라인 지식을 가지고 있기 때문에 코칭의 영향이 적어요.

전체 명세는 [Coaching Data](https://champollion.dev/docs/concepts/coaching-data)를 참조하세요.

---

## FST 및 형태론적 검증

### 언어에 FST가 없으면 어떻게 하나요?

많은 언어에 유한 상태 변환기가 없어요. 괜찮아요 — 하니스는 FST 없이도 작동해요. 복합 점수는 의미 및 표면 메트릭으로 가중치를 이동시키는 Profile B 가중치(자세한 내용은 [Scoring Specification §4.3](/docs/specifications/scoring#43-weight-tables) 참조)를 사용해요. FST acceptance는 실행 카드에서 `null`로 표시돼요.

기존 FST의 주요 레지스트리는 다음과 같아요:

| 레지스트리 | 커버리지 | URL |
|----------|----------|-----|
| **GiellaLT** | 사미어, Cree, 이누크티투트어 및 기타 북극/아북극 언어 | [giellalt.uit.no](https://giellalt.uit.no/) |
| **ALTLab** | Plains Cree, Woods Cree, Ojibwe | [altlab.artsrn.ualberta.ca](https://altlab.artsrn.ualberta.ca/) |
| **Apertium** | 약 60개 언어 쌍, 대부분 유럽어 | [apertium.org](https://apertium.org/) |
| **UniMorph** | 150개 이상 언어의 형태론적 패러다임 | [unimorph.github.io](https://unimorph.github.io/) |

### FST를 만들 수 있나요?

네, 하지만 간단하지 않아요. FST는 언어의 형태론적 규칙 — 모든 유효한 단어 형태를 인코딩해요. 하나를 만들려면 해당 언어에 대한 깊은 언어학적 지식이 필요해요. 형태론적 문법(예: 언어학과의 자료)에 접근할 수 있다면, [HFST](https://hfst.github.io/)나 [Foma](https://fomafst.github.io/) 같은 도구를 사용하여 FST로 컴파일할 수 있어요.

### FST 게이팅은 실제로 어떻게 작동하나요?

FST 게이트 파이프라인은 다음과 같이 작동해요:

1. LLM이 번역을 생성함
2. 출력의 각 단어가 FST와 대조하여 검사됨
3. FST가 거부하는 단어는 형태론적으로 무효한 것으로 플래그됨
4. 메서드는 피드백과 함께 재시도할 수 있음("단어 X는 유효하지 않습니다, 다시 시도하세요")
5. 재시도 후 남은 무효 단어는 로그에 기록됨

FST acceptance 비율은 검증을 통과한 단어 수를 측정해요. 완전한 작동 예제는 [FST-Gated Pipeline Tutorial](/docs/tutorials/fst-gated-pipeline)을 참조하세요.

---

## 데이터 및 데이터셋

### 새로운 언어를 위한 데이터셋을 기여할 수 있나요?

네. [Benchmark Specification §11](/docs/specifications/benchmark#11-extending-to-new-languages)의 최소 요구 사항은 다음과 같아요:

- **50개의 골드 스탠다드 항목** (소스 + 검증된 참조 번역)
- **30개의 개발 항목** (소규모 코퍼스의 경우 골드 스탠다드와 겹칠 수 있음)
- **커뮤니티 동의** (원주민 언어의 경우, 거버넌스 기관의 명시적 승인)
- **출처 문서화** (데이터의 출처, 적용되는 라이선스)

새로운 데이터셋은 자동으로 새로운 리더보드 트랙을 열어요. 기여자 가이드는 [For Language Communities](/docs/community/for-language-communities)를 참조하세요.

### 데이터셋은 어떤 형식이어야 하나요?

표준 필드 이름을 사용하는 JSON이에요:

```json
{
  "name": "my-language-dev-v1",
  "language_pair": "en-xxx",
  "segment": "development",
  "version": "1.0",
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "[translation in target language]",
      "difficulty": 1,
      "domain": "general"
    }
  ]
}
```

전체 스키마와 난이도 등급 정의는 [Datasets](/docs/leaderboard/datasets)를 참조하세요.

---

## 주권 및 소유권

### 원주민 언어를 위해 구축된 메서드는 누가 소유하나요?

원주민 언어의 경우, Deployable 등급(복합 점수 ≥ 0.70)에 도달하고 커뮤니티 검증을 통과한 메서드는 [소유권 이전](/docs/sovereignty/ownership-transfer) 절차를 발동시켜요. 코드 소유권은 연구자에게서 언어 커뮤니티의 거버넌스 조직으로 이전돼요.

연구자는 다음을 유지해요:
- 출판권 (메서드에 관한 학술 논문)
- 리더보드 크레딧
- 동일한 *기법*을 다른 언어에 적용할 권리

거버넌스 조직은 다음을 얻어요:
- 메서드 코드 및 코칭 데이터의 완전한 소유권
- 배포에 대한 통제권 (시기, 장소, 방법)
- API 사용으로 인한 수익 (커뮤니티 90%, 인프라 10%)

### 주권 관련 우려 없이 비원주민 언어에 champollion을 사용할 수 있나요?

네. 표준 언어(프랑스어, 일본어, 스페인어 등)의 경우 주권 관련 고려 사항이 없어요. champollion을 평소처럼 사용하세요 — 원하는 대로 번역하고, 동기화하고, 게시하세요. 주권 프레임워크는 데이터 거버넌스 원칙(OCAP®, CARE, Te Mana Raraunga)이 특별한 고려를 요하는 원주민 및 커뮤니티 거버넌스 언어에 특별히 적용돼요.

---

## 참고 자료

- **[How It Works](https://champollion.dev/how-it-works)** — 전체 솔루션 설명
- **[Scoring Specification](/docs/specifications/scoring)** — 모든 채점 로직(메트릭, 가중치, 등급)에 대한 SSOT
- **[Benchmark Specification](/docs/specifications/benchmark)** — 평가 프로토콜, 코퍼스 형식, 주권
- **[Submit a Method](/docs/getting-started/submit-a-method)** — 단계별 빠른 시작
- **[Leaderboard Rules](/docs/leaderboard/rules)** — 제출 기준
- **[Data Sovereignty](/docs/sovereignty/data-sovereignty)** — OCAP®, CARE 및 윤리적 의무