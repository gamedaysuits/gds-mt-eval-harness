---
sidebar_position: 2
title: "스피커 보수 지급 방식"
slug: '/perspectives/how-speakers-get-paid'
description: "벤치마크 작업에 참여한 커뮤니티 검증자와 번역가에게 무엇에 대해 보수를 지급하는지, 스피커에게 보수를 지급하는 것이 왜 타협할 수 없는 원칙인지, 그리고 Arena가 성장함에 따라 보상이 어떻게 확장되는지 설명해요. 모든 수치는 공개된 명세에서 가져온 것이에요."
related:
  - label: "Speaker Validation Protocol"
    to: /docs/specifications/speaker-validation
    kind: spec
    note: "The work validators are paid for"
  - label: "Prize Specification"
    to: /docs/specifications/prizes
    kind: spec
    note: "Where prize money goes, and why"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
---
# 화자에게 비용이 지급되는 방식

> **투명성 안내.** 이 페이지의 모든 수치는 이미 공개된 명세서에 등장해요 — [Benchmark Specification §10](/docs/specifications/benchmark#10-cost-framework), [Speaker Validation Protocol](/docs/specifications/speaker-validation), 그리고 [Prize Specification](/docs/specifications/prizes)이에요. 이 페이지는 이를 한곳에 쉬운 언어로 모아서, 여기서 화자의 시간이 얼마의 가치를 지니는지 알아보기 위해 명세서를 읽지 않아도 되도록 했어요. 이 문서는 해당 문서들이 이미 명시한 내용을 넘어서는 어떠한 약속도 하지 않아요.

기계가 생성한 문장이 실제로 자연스럽고 의미가 올바른지를 판단할 수 있는 이중 언어 화자는 이 시스템 전체에서 가장 희소하고 가장 가치 있는 참여자예요. 그 외의 모든 것 — 하니스, 메트릭, 리더보드 — 은 그 사람의 적은 시간을 멀리까지 활용하기 위해 존재해요.

그래서 첫 번째 원칙은 간단해요: **화자는 결과가 무엇을 보여주든 관계없이, 전문적인 요율로 자신의 시간에 대한 비용을 지급받아요.**

---

## 화자에게 비용을 지급하는 것이 타협 불가능한 이유

언어 기술 연구는 오랫동안 유창한 화자를 무료 자원으로 취급하는 습관을 가져왔어요 — 화자를 제외한 모두에게 데이터셋, 논문, 경력을 만들어주는 "커뮤니티 참여" 말이에요. 우리는 그러한 패턴을 착취적이라고 보며, 이 작업을 수행할 가장 적합한 사람들은 바로 이미 그 언어로 가르치고, 번역하고, 아이를 키우는 시급한 일에 시간을 쓰고 있는 사람들이에요.

세 가지 설계상의 결과가 뒤따라요:

1. **자원봉사 파이프라인 없음.** 우리는 화자에게 연구에 대한 호의로 평가 작업을 기부해 달라고 요청하지 않아요. 참여는 유료 계약이며, 이를 거절해도 화자에게는 아무 비용이 들지 않아요.
2. **지급은 무조건적이에요.** 화자는 자신의 평가가 사용되든 아니든 비용을 지급받으며, 지급은 결과에 좌우되지 않아요. 공개된 프로토콜은 각 작업 블록 완료 후 2주 이내에 지급할 것을 약속해요.
3. **보상이 전부는 아니에요.** 평가에 기여하는 화자는 크레딧(실명 또는 익명, 본인 선택), 자신의 평가를 사용하는 출판물에 대한 선택적 공저자 자격, 언제든지 자신의 기여를 철회할 권리, 그리고 문제가 있다고 판단하는 결과의 출판에 대한 거부권도 받아요. 이러한 조건은 부속 합의가 아닌 [Speaker Validation Protocol §5–6](/docs/specifications/speaker-validation)에 담겨 있어요.

## 공개된 요율

벤치마크 비용 체계는 코퍼스 및 검증 작업에 대한 이중 언어 화자 보상을 **시간당 $50–65 CAD**로 정하고 있어요. 역할별로 의미하는 바는 다음과 같아요:

### 벤치마크 코퍼스 구축

모든 방법이 점수를 산정받는 기준이 되는 참조 번역을 만드는 것은 화자의 기초적인 작업이에요. 언어당 공개된 구축 예산은 다음과 같아요:

| 작업 | 공개 범위 | 근거 |
|------|-----------------|-------|
| 코퍼스 큐레이션 (50–150개 항목) | $2,500–6,000 | $50–65/hr, 이중 언어 화자 시간 |
| 방법 출력 검토 | $500–1,500 | 동일한 시간당 요율 |

전체 코퍼스는 전통적으로 화자에게 약 80시간이 걸려요. 계획된 에이전트 지원 워크플로(문장 초안 작성과 서식 작업은 도구가 처리하고, 번역은 항상 사람이 수행)는 이를 30–40시간 수준으로 줄이도록 설계되어 있어요 — 반복적인 작업 시간은 줄이고, 시간당 요율은 동일하게 유지하며, 화자는 진정으로 사람이 필요한 부분만 담당해요.

### 메트릭 검증

자동화된 점수가 의미를 갖기 전에, 화자는 그것을 인간의 판단과 대조해 확인해야 해요. [Speaker Validation Protocol](/docs/specifications/speaker-validation)은 정확한 작업, 시간, 비용을 공개해요:

| 작업 | 시간 | 화자당 비용 |
|------|------|-----------------|
| A — 200개 기계 번역의 적절성과 유창성 평가 | ~8시간 | $400–520 CAD |
| B — 50개의 "동등한" 번역 쌍 검토 | ~2시간 | $100–130 CAD |
| C — 형태소 분석기가 거부한 100개 단어 검토 | ~1.5시간 | $75–100 CAD |

세 가지를 모두 수행하는 화자는 2~4주에 걸쳐 약 11.5시간을 들이고 **$575–750 CAD**를 받아요. 화자 3명으로 구성된 전체 검증 라운드는 프로젝트에 $1,475–1,920의 비용이 들어요 — 바로 이것이 핵심이에요: 화자 검증은 프로젝트에서 작은 항목이며, 비용을 "절약"하는 곳이 되어서는 절대 안 돼요.

### 상금 청구 검토

어떤 상금도 자동화된 점수만으로 지급되지 않아요. [Founder's Prize](/docs/specifications/prizes) ($10,000 CAD, English→Plains Cree)는 최소 2명의 이중 언어 화자가 최소 30개 출력의 층화 샘플을 독립적으로 검토하고, 그중 70% 이상이 "허용 가능" 또는 "우수"로 평가될 것을 요구해요. 그 검토는 동일한 요율로 비용이 지급되는 화자 작업이며 — 동시에 관문이기도 해요: 화자는 상금 청구를 무산시킬 수 있고, 그것은 의도된 설계예요.

## 콘테스트에 따라 어떻게 확장되는가

이 모델은 화자 보상이 플랫폼에 의해 희석되는 대신 플랫폼과 함께 성장하도록 구축되어 있어요:

- **각 새로운 언어는 유료 코퍼스 계약으로 시작돼요.** 언어당 공개된 구축 비용($3,350–8,500 종합)은 대부분 화자 보상이며 — 의도적으로 가장 큰 단일 구성 요소예요.
- **각 새로운 상금 풀은 자체적인 유료 검토를 가져와요.** [prize template](/docs/specifications/prizes#4-future-prize-pools)을 따르는 모든 후원 콘테스트는 동일한 커뮤니티 검증 요건을 지니며, 이는 모든 콘테스트가 해당 언어에 대한 화자 검토 작업에 자금을 댄다는 것을 의미해요.
- **배포된 방법은 지속적인 검토에 자금을 대요.** 커뮤니티 소유 방법이 API 수익을 올리면, 그 90%가 커뮤니티의 거버넌스 조직으로 흘러가며([the economic model](/docs/sovereignty/economic-model)), 이 조직은 적절하다고 판단하는 대로 지속적인 검토, 코퍼스 성장, 언어 프로그램에 자금을 댈 수 있어요. 그 배분은 우리가 아니라 커뮤니티의 결정이에요.

## 우리가 약속하지 *않은* 것

정직함을 위해서는 경계를 표시해야 해요:

- 위의 요율은 현재 Plains Cree 작업에 대한 공개된 요율이에요. 향후 언어에 대한 요율은 파트너 커뮤니티와 함께 정해지며, 작업 시작 전에 명세서에 동일한 방식으로 공개될 거예요.
- 플라이휠(수익 → 커뮤니티 → 더 많은 유료 작업)은 시작하려면 외부 자금이 필요하며 아직 자립적이지 않아요. [economic model](/docs/sovereignty/economic-model)은 보장이 아니라 메커니즘을 설명해요.
- "공정한 지급"은 필요하지만 충분하지는 않아요. 지급 자체만으로는 프로젝트가 비착취적이 되지 않아요 — 소유권과 통제권이 그렇게 만들며, 그렇기 때문에 보상이 [sovereignty architecture](/docs/sovereignty/data-sovereignty)를 대체하는 것이 아니라 그 안에 자리 잡고 있어요.

---

## 이것이 당신에게 의미하는 바

:::info 커뮤니티 구성원이라면
당신이 서비스가 부족한 언어와 English에 모두 능통하다면, 당신의 판단은 이 시스템에서 가장 가치 있는 입력이며, 공개된 조건은 다음과 같아요: 시간당 $50–65 CAD, 유연한 일정, 2주 이내 지급, 본인이 정하는 조건의 크레딧, 그리고 기여를 철회할 권리. 프로그래밍은 필요하지 않아요. [For Language Communities](/docs/community/for-language-communities) 또는 [Speaker Validation Protocol §7](/docs/specifications/speaker-validation#7-how-to-get-started)에서 시작하세요.
:::

:::info 연구자라면
화자 보상을 일급 연구 비용으로 예산에 잡으세요 — 공개된 수치(메트릭 검증 라운드 $1,475–1,920; 코퍼스 큐레이션 $2,500–6,000)는 보조금 기준으로는 적은 금액이며, 자동화된 점수를 변호 가능하게 만드는 요소예요. [Corpus Partnership Strategy](/docs/specifications/corpus-partnership)는 학과가 자금이 마련된 화자 작업을 내장한 채 이 시스템에 연결되는 방법을 보여줘요.
:::

:::info 빌더라면
당신이 화자 작업에 직접 자금을 대지 않더라도 그 혜택을 받아요: 검증된 메트릭은 당신의 리더보드 점수를 의미 있게 만들고, 유료 커뮤니티 검토는 당신의 방법과 상금 사이에 서 있는 요소예요. 당신이 우승한다면, 화자들이 당신의 출력을 면밀히 검토하도록 비용을 지급받았을 것이라고 예상하세요 — 그리고 [당신의 방법의 소유권이 이전](/docs/sovereignty/ownership-transfer)되어 그 언어를 위해 봉사하는 커뮤니티에 넘어갈 것이라고 예상하세요.
:::

## 함께 보기

- [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization) — 화자의 권위가 다른 모든 것을 어떻게 규정하는지
- [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections) — 벤치마크 이후에도 유지되는 화자의 권위
- [Benchmark Specification §10](/docs/specifications/benchmark#10-cost-framework) — 이 수치들이 나온 전체 비용 체계