---
sidebar_position: 3
title: "벤치마크에서 일상적 활용으로: 포스트 에디팅 경로"
slug: '/perspectives/from-benchmark-to-daily-use'
description: "벤치마크로 검증된 번역 방법이 어떻게 커뮤니티 번역 워크플로가 되는지: 기계 초안, 유창한 화자의 포스트 에디팅, 출판 텍스트 — 모든 단계에서 정직한 품질 기준을 적용해요."
related:
  - label: "Deploy to Production"
    to: /docs/getting-started/deploy-to-production
    kind: guide
    note: "From proven method to live translation"
  - label: "Cookbook: Partial Translation (Human + Machine)"
    to: /docs/tutorials/partial-translation
    kind: cookbook
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The quality thresholds behind the path"
  - label: "Translation Is Not Revitalization"
    to: /docs/perspectives/translation-is-not-revitalization
    kind: position
---
# 벤치마크에서 일상 사용으로: 포스트에디팅의 경로

> **요약하자면.** 리더보드 점수는 제품이 아니에요. "이 방법은 0.78점을 받았어요"에서 "지역 사무소가 매주 해당 언어로 문서를 발행해요"에 이르는 길은 정확히 하나의 워크플로를 거쳐요. 기계가 초안을 만들고, 유창한 화자가 그것을 교정하며, 교정된 텍스트만 발행돼요. 우리 명세의 모든 품질 기준은 그 워크플로에 맞춰 보정되어 있어요 — 이 플랫폼에서 어떤 언어에 대해서도 지지하지 않는 감독되지 않은 기계 출력에 맞춰져 있는 게 아니고요.

사람들은 때때로 번역 방법이 언제 "그냥 써도 될 만큼 좋아지는지" 물어봐요. 이 Arena가 다루는 언어들에게는 그 질문에 함정이 있어요. 솔직한 답은, 지향할 가치가 있는 기준이 "검토 없이 발행해도 될 만큼 좋은" 것이 아니라 — **"초안을 검토하는 게 처음부터 번역하는 것보다 나을 만큼 좋은"** 것이라는 거예요. 그 기준은 훨씬 낮고, 측정 가능하며, 이를 넘어서면 공동체 번역 사무소가 한 주에 생산할 수 있는 것이 바뀌어요.

---

## 워크플로, 처음부터 끝까지

```
 English source document
        │
        ▼
 Machine draft  ←  a benchmarked, community-owned method
        │
        ▼
 Fluent-speaker post-edit  ←  the human gate; nothing skips it
        │
        ▼
 Published text  ←  carries human approval, not a machine score
        │
        ▼
 (Optional, community-controlled) corrections become
 data that improves the next version of the method
```

주목할 점 세 가지예요:

1. **기계는 절대 발행하지 않아요.** 출력의 단위는 초안이에요. 화자의 교정 단계는 마지막에 덧붙인 품질 보증이 아니라 — 그 자체가 워크플로예요.
2. **화자의 시간이 최적화되는 자원이에요.** 한 방법이 다른 방법보다 낫다는 것은 정확히 화자가 고칠 것을 덜 남긴다는 정도만큼이에요. 자원이 풍부한 언어에 대한 포스트에디팅 연구는 중간 정도의 MT 품질에서 처음부터 번역하는 것보다 빠르다는 것을 일관되게 발견해요 (Plitt & Masselot 2010; Green, Heer & Manning 2013, 둘 다 [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization)에서 링크와 함께 인용되어 있어요). 그것이 다종합어에도 적용되는지는 바로 이 벤치마크가 알아내기 위해 존재하는 거예요 — 우리는 그것을 가정이 아니라 언어별로 검증해야 할 가설로 다뤄요.
3. **피드백 루프는 소유돼요.** 교정된 모든 문서는 잠재적 훈련 및 코칭 데이터예요 — 그리고 그것은 공동체에 속하며, [데이터 주권](/docs/sovereignty/data-sovereignty) 규칙에 따라 그들의 조건 아래 피드백할(또는 하지 않을) 수 있어요. 피드백 메커니즘은 플랫폼의 설계 목표이지 아직 구축된 기능은 아니에요. 교정과 출처가 어떻게 작동하도록 의도되었는지는 [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections)를 참고하세요.

## 품질 등급이 실제 사용에 의미하는 것

리더보드는 자동화된 지표들의 복합 점수로 방법들을 채점하며 ([Scoring Specification](/docs/specifications/scoring)), 그 점수들은 명명된 등급으로 매핑돼요. 다음은 그 등급들을 일상 사용 용어로 솔직하게 번역한 거예요:

| 등급 (composite) | 포스트에디팅 경로에 의미하는 것 |
|---|---|
| **Baseline** (0.00–0.30) | 어떤 것에도 사용할 수 없어요. 출력의 대부분이 대상 언어가 아니에요. 연구의 하한선으로만 유용해요. |
| **Emerging** (0.30–0.50) | 여전히 초안 작성 도구가 아니에요. 올바른 단편들이 나타나지만, 화자가 새로 쓰는 것보다 고치는 데 더 많은 시간을 쓸 거예요. |
| **Functional** (0.50–0.70) | 쉬운 텍스트에 대해 포스트에디팅이 처음부터 번역하는 것을 능가할 *수도 있는* 첫 등급이에요 — 화자와 함께 시범 운영할 가치는 있지만, 의존할 가치는 없어요. 빈번한 형태론적 오류가 남아 있어요. |
| **Deployable** (0.70–0.85) | 위 워크플로의 목표 등급이에요: 대부분의 형태론이 올바르고 유창한 화자가 다시 번역하는 것보다 의미 있게 더 빠르게 교정할 수 있는 초안이에요. **"Deployable"은 *포스트에디팅 워크플로에* 배포 가능하다는 뜻이지 — 절대 "검토 없이 발행"이 아니에요.** |
| **Fluent** (0.85–1.00) | 유능한 인간 번역에 근접해요; 오류가 드물고 사소해요. 검토 단계는 유지돼요 — 단지 더 빨라질 뿐이에요. |

이 표 위에는 [Benchmark Specification §5 및 §7](/docs/specifications/benchmark#5-quality-tiers)에서 바로 가져온 두 가지 구조적 정직성 규칙이 있어요:

- **자동화된 등급은 잠정적인 라벨이지 판정이 아니에요.** 그것들은 인간 검토를 위한 후보 지명이에요. 화자 검증 데이터가 축적됨에 따라 기준이 재보정될 것이며, 언어마다 다르게 정해질 수 있어요.
- **어떤 방법도 공동체 검토 없이 Deployable 이상을 주장할 수 없어요.** 출력의 계층화된 표본이 이중 언어 화자에게 전달되고, 그들이 각 번역을 *reject / gist / acceptable / excellent*로 평가해요. 리더보드가 아니라 거버넌스 조직이 — 그 방법을 진전시킬지 결정해요.

비교를 위해, [Founder's Prize](/docs/specifications/prizes) 기준(composite ≥ 0.80, 형태론적으로 유효한 단어 ≥99%, 화자 평가 acceptable-or-better ≥70%)은 남은 실수가 *실제 언어 오류* — 조작된 단어가 아니라 잘못된 굴절 — 인 방법을 설명해요. 그것이 바로 "화자의 시간을 들일 가치가 있는 초안"이 숫자로 어떻게 보이는지예요.

## 우승 방법에서 작동하는 사무소로

어떤 방법이 그 관문들을 통과했다고 가정해 봐요. 남은 단계들은 조직적이며, 즉흥적으로 처리되는 게 아니라 명세화되어 있어요:

1. **소유권이 이전돼요.** 방법의 코드가 공동체의 거버넌스 조직의 소유가 돼요 — 개발자는 귀속과 출판 권리를 유지해요 ([Ownership Transfer](/docs/sovereignty/ownership-transfer)).
2. **방법이 서비스가 돼요.** 그것은 플러그인으로 패키징되어 배포 플랫폼을 통해 제공되며, 공동체가 접근, 가격, 허용된 사용을 통제해요 ([Deploy to Production](/docs/getting-started/deploy-to-production)).
3. **번역가들이 그것을 자신의 하루에 연결해요.** 번역 사무소가 기존 문서 워크플로를 방법의 API에 연결해요: 원본 텍스트 입력, 초안 출력, 포스트에디팅, 발행. 발행된 텍스트에는 번역가의 이름과 권한이 실려요 — 기계는 사전처럼 그들의 책상 위에 있는 도구예요.
4. **수익은 사용을 따라가요.** 방법을 사용하는 외부 개발자는 미터링된 요율을 지불하며, 그 수익의 90%가 거버넌스 조직으로 흘러가요 ([The Economic Model](/docs/sovereignty/economic-model)) — 그것은 더 많은 번역가 시간을 지원하여 루프를 닫을 수 있어요.

## 오늘날 이것이 어디에 서 있는가

명확히 말하자면: 전체 경로는 처음부터 끝까지 명세화되어 있고, 부분적으로 구축되어 있어요. 평가 하니스, 지표, 실행 카드, 공개 리더보드가 존재해요; Plains Cree 개발 코퍼스와 활성 상금이 존재해요; 배포 플랫폼이 존재해요. 공동체 검토 인터페이스, 평가 샌드박스, 교정 텍스트 피드백 루프는 명세화되어 있지만 아직 작동하지 않아요 — 명세는 그것들을 계획된 것으로 표시하고, 우리도 그렇게 해요. 아직 어떤 방법도 벤치마크에서 일상적인 공동체 사용에 이르는 전체 여정을 완료하지 못했어요. 그 여정이 프로젝트가 정의하는 성공이며, 바로 그것이 우리가 그것을 일찍 주장하지 않는 이유예요.

---

## 이것이 당신에게 의미하는 것

:::info 공동체 구성원이라면
리더보드의 "Deployable" 배지는 결코 기계가 당신의 언어로 감독 없이 발행한다는 뜻이 아니에요 — 그것은 초안 생성기가 당신의 조건에 따라, 당신의 화자를 심사위원으로 하여(보수를 받는 심사위원 — [How Speakers Get Paid](/docs/perspectives/how-speakers-get-paid) 참고), 당신의 번역가들을 위해 *오디션을 볼* 준비가 되었을 수 있다는 뜻이에요. 당신의 공동체가 번역 사무소를 운영한다면, 우리에게 가져올 적절한 질문은 이거예요: "시범 운영은 어떤 모습일까요, 그리고 누가 출력을 검토하나요?"
:::

:::info 연구자라면
포스트에디팅 관점은 측정할 가치가 있는 것을 바꿔요: 복합 점수만이 아니라 화자가 루프에 있는 상태에서의 수용 가능한 텍스트까지의 시간이에요. Arena의 지표들은 그것에 대한 대리 지표이며 ([Scoring Specification §1](/docs/specifications/scoring)), 형태론적으로 복잡한 언어에 대한 언어별 포스트에디팅 연구는 이 인프라가 지원하도록 설계된 열린 연구 공백이에요.
:::

:::info 빌더라면
지표가 아니라 편집자를 위해 최적화하세요. 가끔 잘못된 굴절을 가진 실제 단어를 생성하는 방법은 화자가 몇 초 만에 고칠 수 있어요; 그럴듯해 보이는 형태를 환각하는 방법은 워크플로 전체를 오염시켜요 — 그것이 여기서 형태론적 유효성이 그렇게 강하게 게이트되는 이유예요. [Submit a Method](/docs/getting-started/submit-a-method)에서 시작하고, 우승했을 때 결국 넘겨주게 될 것에 대해서는 [Method Interface](/docs/specifications/methods)를 읽어보세요.
:::

## 함께 보기

- [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization) — 인간 관문이 한계가 아니라 핵심인 이유
- [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections) — 발행된 텍스트가 그래도 틀렸을 때 무슨 일이 일어나는지
- [Benchmark Specification §7](/docs/specifications/benchmark#7-human-validation) — 인간 검증 관문, 공식적으로