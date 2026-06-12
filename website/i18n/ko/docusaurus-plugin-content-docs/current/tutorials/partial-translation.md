---
sidebar_position: 10
title: "쿡북: 부분 번역 (인간 + 기계)"
---
# 부분 번역 (사람 + 기계)

> **핵심 아이디어:** 대표 샘플을 직접 번역하고, 해당 샘플에서 기계 번역 방식이 사람의 스타일과 일치함을 입증한 다음, 나머지 대량의 내용을 자동으로 번역하는 거예요. 사람의 품질과 기계의 확장성을 결합하는 방식으로, 사람이 기준을 정하고 기계가 그 기준을 따라가요.

:::info 이것은 완성된 구현이 아니라 쿡북이에요
이 가이드는 사람-기계 하이브리드 워크플로를 개략적으로 설명해요. 특히 번역 에이전시, 커뮤니티 언어 작업자, 그리고 교육 환경에 적합해요.
:::

## 언제 사용하나요

- **유창한 화자에게 접근**할 수 있지만 그들의 시간이 제한적일 때
- **대량**을 번역해야 하지만 일부만 완벽하면 될 때
- 사람 번역으로 **품질 기준선을 확립**한 다음 MT로 확장하고 싶을 때
- 일부에 대한 사람 검토가 가능한 **교육 또는 커뮤니티 환경**에서 작업할 때

## 작동 방식

```
[Full corpus: 1,000 entries]
        │
        ├── [100 entries] ──→ Human translator ──→ Gold translations
        │                                              │
        │                                              ▼
        │                                    Train / prompt machine
        │                                    method to match style
        │                                              │
        └── [900 entries] ──→ Machine method ──→ Auto translations
                                                       │
                                                       ▼
                                              [Optional: human review
                                               of flagged entries]
```

1. **대표 샘플 선택** — 다양한 문장 유형, 길이, 주제를 포괄해요
2. **샘플을 사람이 번역** — 스타일, 격식, 용어에 대한 골드 스탠더드를 확립해요
3. **기계 번역 방식 구성** — 사람의 번역을 코칭 데이터, few-shot 예시, 또는 파인튜닝 데이터로 사용해요
4. **사람 샘플로 기계 채점** — 기계가 사람의 스타일과 일치하나요?
5. **나머지 자동 번역** — 샘플에서 기계 품질이 허용 가능하다면요
6. **선택적 사람 검토** — 신뢰도가 낮은 출력을 화자 검토를 위해 표시해요

## 품질 보증: 스타일 일치 테스트

```bash
# Translate the human-translated sample with your machine method
python eval/baseline_experiment.py \
  --dataset data/human-sample.json \
  --condition coached-v3

# Compare: does the machine match the human translator's choices?
# Look at: chrF++ (similarity), FST acceptance (validity),
# and qualitative patterns (register, formality, terminology)
```

## 샘플 선택

**분포를 포괄하세요.** 100개 항목에는 다음이 포함되어야 해요:
- 짧은 구절(1~3 단어)과 완전한 문장
- 일반 어휘와 도메인 특정 용어
- 단순한 구조와 복잡한 구조
- 여러 문법적 특징(의문문, 명령문, 조건문)

**쉬운 것만 골라내지 마세요.** 샘플에는 번역 방식이 어려움을 겪을 가능성이 높은 항목이 포함되어야 해요. 바로 그 지점에서 사람의 품질이 가장 중요해요.

## 커뮤니티 검토 워크플로

원주민 언어 커뮤니티의 경우, 이 접근 방식은 화자의 시간을 존중해요:

1. **화자가 50~100개 항목을 번역** (집중 작업 2~4시간)
2. **기계가 나머지 900개를 번역** — 화자의 작업을 코칭 데이터로 사용해요
3. **화자가 표시된 항목을 검토** — 기계가 가장 신뢰도가 낮았던 항목만 검토해요 (추가 1~2시간)
4. **결과:** 약 50시간이 아닌 약 5시간의 화자 시간으로 사람에 가까운 품질의 번역 1,000개를 얻어요

## 장단점

| | |
|---|---|
| ✅ 사람의 품질과 기계의 확장성을 결합 | ❌ 초기 사람 투자가 필요 |
| ✅ 제한적인 화자 가용성을 존중 | ❌ 기계가 모든 스타일적 뉘앙스를 포착하지 못할 수 있음 |
| ✅ 자연스러운 품질 보증 워크플로 | ❌ 샘플 선택이 전체 품질에 영향을 줌 |
| ✅ 커뮤니티/교육 환경에 적합 | ❌ 표시된 항목에 대한 사람 검토 병목 |

## 함께 사용하면 좋은 방법

- **[Coached LLM Prompting](./coached-llm-prompting)** — 사람 번역이 코칭 데이터에 정보를 제공해요
- **[Few-Shot Prompting](./few-shot-prompting)** — 사람 번역을 인컨텍스트 예시로 활용해요
- **[Corpus Creation](./corpus-creation)** — 사람 샘플 자체가 코퍼스 생성이에요

## 참고 자료

- [언어 커뮤니티를 위하여](/docs/community/for-language-communities) — 커뮤니티 참여 모델
- [데이터 주권](/docs/sovereignty/data-sovereignty) — 번역 데이터의 소유권
- [저자원 언어 지원하기](/docs/community/low-resource-languages)