---
sidebar_position: 3
title: "평가 데이터셋"
related:
  - label: "Corpus Design Framework"
    to: /docs/specifications/corpus-design
    kind: spec
    note: "How evaluation corpora are constructed"
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "Build a corpus for your language"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
---
# 평가 데이터셋

> **핵심 요약.** 이 페이지에서는 벤치마킹에 사용할 수 있는 평가 데이터셋을 설명해요. 코퍼스 엔트리 스키마, 난이도 등급(1–5), 출처(provenance) 요구 사항을 다뤄요. 현재 제공되는 데이터셋은 EDTeKLA Dev v1(Plains Cree, 총 548개 엔트리: 교과서 486개 + 골드 스탠더드 62개)과 FLORES+ Devtest(39개 언어, 각 1,012개 엔트리)예요.

데이터셋은 하니스(harness)가 실행 대상으로 삼는 고정된 목표예요. 각 데이터셋은 골드 스탠더드 레퍼런스와 함께 source→target 쌍을 담은 JSON 파일이에요. 하니스는 이 레퍼런스를 기준으로 모델 출력을 채점하며, 레퍼런스 자체를 수정하지는 않아요.

:::danger 평가 데이터로 학습하지 마세요

⚠️ **이 데이터셋은 평가 전용이에요.** 평가 데이터로 학습, 파인튜닝, few-shot 프롬프팅을 하거나 그 외 방식으로 평가 데이터에 노출된 방법은 인위적으로 부풀려진 점수를 산출하게 되며, **리더보드에서 실격 처리돼요.**

학습에는 별도의 코퍼스를 사용하세요. 평가 세트는 개발 과정에서 모델이 보지 못한 상태로 유지되어야 해요.
:::

---

## 데이터셋 형식

모든 데이터셋은 동일한 JSON 스키마를 따라요:

```json
{
  "dataset": {
    "id": "dataset-slug",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "description": "Human-readable description of the dataset",
    "source_language": "en",
    "target_language": "crk",
    "created": "2025-05-01",
    "license": "CC-BY-NC-4.0",
    "provenance": ["gold_standard", "textbook"]
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "tânisi",
      "difficulty": 1,
      "provenance": "gold_standard",
      "register": "conversational",
      "context": "greeting",
      "notes": "Common greeting, SRO orthography"
    }
  ]
}
```

:::info 표준 스키마
[Benchmark Specification](/docs/specifications/benchmark)에서 표준 코퍼스 및 엔트리 스키마를 정의해요. 이 페이지에서는 사용 가능한 데이터셋과 새 데이터셋을 만드는 방법을 설명해요.
:::

### 최상위 `dataset` 블록

| 필드 | 타입 | 설명 |
|-------|------|-------------|
| `id` | `string` | 고유 데이터셋 식별자(run card 및 리더보드에서 사용) |
| `version` | `string` | 시맨틱 버전. 이 값을 올리면 이전 run card 비교가 무효화돼요 |
| `language_pair` | `string` | 표시 레이블(예: `EN→CRK`) |
| `description` | `string` | 선택 사항. 사람이 읽을 수 있는 요약 |
| `source_language` | `string` | BCP 47 소스 언어 코드 |
| `target_language` | `string` | BCP 47 타깃 언어 코드 |
| `created` | `string` | ISO 8601 생성 날짜 |
| `license` | `string` | SPDX 라이선스 식별자 |
| `provenance` | `string[]` | 엔트리 전반에서 사용되는 출처(provenance) 태그 목록 |

### 엔트리 필드

| 필드 | 타입 | 필수 | 설명 |
|-------|------|----------|-------------|
| `id` | `integer` | ✅ | 코퍼스 내 고유 엔트리 식별자 |
| `source` | `string` | ✅ | 번역할 소스 텍스트 |
| `reference` | `string` | ✅ | 골드 스탠더드 레퍼런스 번역 |
| `difficulty` | `integer` | ✅ | 난이도 등급 1–5(아래 참고) |
| `provenance` | `string` | ✅ | 이 엔트리의 출처(예: `gold_standard`, `textbook`, `elicited`) |
| `register` | `string` | ✅ | 레지스터/격식 수준(예: `conversational`, `formal`, `ceremonial`) |
| `context` | `string` | ✅ | 의사소통 기능(예: `greeting`, `declaration`, `instruction`) |
| `notes` | `string` | ❌ | 휴먼 리뷰어를 위한 선택적 컨텍스트 |
| `morphological_analysis` | `string` | ❌ | 골드 스탠더드 형태소 분석 |
| `variant_class` | `string` | ❌ | 허용 가능한 번역 변형을 묶는 클래스 레이블 |

---

## 사용 가능한 데이터셋

### EDTeKLA Development Set v1

영어→Plains Cree(SRO) 번역을 위해 구축된 첫 번째 평가 데이터셋이에요. University of Alberta의 [EdTeKLA 연구 그룹](https://spaces.facsci.ualberta.ca/edtekla/)에서 만들었어요.

| 속성 | 값 |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **버전** | `1.0` |
| **언어 쌍** | EN → CRK (Plains Cree, SRO 정서법) |
| **엔트리 수** | 총 548개(교과서 486개 + 골드 스탠더드 62개). 표준 dev 코퍼스는 `textbook_dev.json`(436개 엔트리 — 총 486개 중 전체 교과서 dev 분할: dev 436개 + held-out 테스트 50개)이에요 |
| **난이도 분포** | Easy, Medium, Hard |
| **출처(provenance)** | `gold_standard`(화자 검증), `textbook`(출판된 교육 자료) |
| **라이선스** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |

**테스트 항목:**

- 기본 인사말 및 일반적인 표현
- 명사 유생성(animacy)과 obviation
- 인칭과 시제에 따른 동사 활용
- 처소(locative) 구문
- 소유 패러다임
- 복합 문장 구조

:::tip 코퍼스 구조
전체 EdTeKLA 컬렉션은 큐레이션된 548개 엔트리로 구성돼요: 교과서 코퍼스에서 486개(dev 436개 + held-out 50개), itwêwina 골드 스탠더드에서 62개예요. 표준 dev 코퍼스는 436개 엔트리를 가진 `textbook_dev.json`이며, 이는 전체 교과서 dev 분할이에요. 각 엔트리는 유창한 화자에 의해 검증되었거나 출판된 Cree 언어 교과서에서 가져왔어요. 검증된 골드 스탠더드를 갖춘 작고 고품질의 데이터셋이 크고 노이즈가 많은 데이터셋보다 더 유용해요 — 특히 "거의 비슷한" 번역이 형태론적으로 무효한 경우가 많은 저자원 언어에서는 더욱 그래요.
:::

---

## 새 데이터셋 만들기

새 언어 쌍이나 도메인을 위한 데이터셋을 만들려면:

### 1. JSON 구조화하기

[데이터셋 형식](#dataset-format) 스키마를 따르세요. 모든 엔트리에는 `source`, `reference`, `difficulty`, `provenance`, `register`, `context`가 있어야 해요.

### 2. 고유 ID 할당하기

설명적인 슬러그를 사용하세요: `{project}-{split}-v{version}`(예: `edtekla-dev-v1`, `quechua-test-v1`).

### 3. 골드 스탠더드 검증하기

모든 `reference` 값은 유창한 화자에 의해 검증되거나 출판된 동료 심사(peer-reviewed) 자료에서 가져와야 해요. 머신 생성 레퍼런스는 평가의 목적을 무력화시켜요.

### 4. 난이도 등급 설정하기

각 엔트리에 정수 난이도 수준을 할당하세요:

| 등급 | 설명 | 예시 |
|------|-------------|----------|
| 1 — 기본 어휘 | 단일 단어, 일반적인 인사말, 숫자 | "hello" → "tânisi" |
| 2 — 간단한 문장 | 주어-동사 또는 SVO, 현재 시제 | "I see the dog" |
| 3 — 중간 복잡도 | 과거/미래 시제, 소유격, 유생성 | "I saw his dog yesterday" |
| 4 — 복잡한 형태론 | obviation, 수동태, conjunct order | "the woman whose son went to the store" |
| 5 — 고급 | 다중 절, 격식체, 의례적 표현, 관용 표현 | 레지스터에 적합한 어조를 갖춘 전체 단락 |

### 5. 출처(provenance) 태그 지정하기

각 엔트리는 출처를 표시해야 해요. 일반적인 태그:

- `gold_standard` — 유창한 화자에 의해 검증됨
- `textbook` — 출판된 교육 자료에서 가져옴
- `elicited` — 구조화된 elicitation 세션을 통해 생성됨
- `corpus` — 병렬 코퍼스에서 추출됨

### 6. 파일 검증하기

JSON이 올바른 형식이며 모든 필수 필드가 존재하는지 확인하기 위해, 임의의 모델로 데이터셋에 대해 하니스를 실행하세요:

```bash
python eval/baseline_experiment.py --dataset path/to/your-dataset.json
```

하니스는 누락된 필드, 중복된 인덱스, 스키마 위반이 있으면 오류를 발생시켜요.

### 7. 포함을 위해 제출하기

[eval harness 저장소](https://github.com/gamedaysuits/arena)에 데이터셋 파일을 `data/` 디렉터리에 넣어 풀 리퀘스트를 열어 주세요. 검증 방법론과 출처(provenance)에 대한 문서를 포함해 주세요.

---

## FLORES+ Devtest

[Open Language Data Initiative (OLDI)](https://huggingface.co/datasets/openlanguagedata/flores_plus)에서 관리하는 광범위 커버리지 다국어 벤치마크예요. champollion의 멀티 모델 프런티어 벤치마크에 사용돼요.

| 속성 | 값 |
|----------|-------|
| **ID** | `flores-plus-devtest` |
| **언어 쌍** | EN → 39개 언어(champollion에 등록된 모든 자연어) |
| **엔트리 수** | 언어당 1,012개 문장 |
| **라이선스** | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| **출처** | 원래 Meta FLORES-200, 현재 OLDI 관리 |
| **위치** | 메인 champollion 저장소의 `test/benchmark/fixtures/`에 사전 추출된 픽스처 |

:::danger 평가 전용
FLORES+는 오직 평가를 위한 것이에요. 큐레이터들은 이를 **학습 데이터로 사용하지 말 것**을 명시적으로 요청해요. 그 내용이 학습 코퍼스에서 제외되도록 하세요.
:::

---

## 함께 보기

- [MT Evaluation](/docs/leaderboard/rules) — 평가 프레임워크 및 리더보드 개요
- [Eval Harness](/docs/specifications/harness) — 이 데이터셋에 대해 평가를 실행하는 방법
- [Run Card Specification](/docs/specifications/run-card) — 결과 기록을 위한 JSON 스키마
- [Method Leaderboard](https://champollion.dev/leaderboard) — 실시간 벤치마크 점수
- [EdTeKLA Project](https://spaces.facsci.ualberta.ca/edtekla/) — Cree 데이터셋을 만든 University of Alberta 연구 그룹