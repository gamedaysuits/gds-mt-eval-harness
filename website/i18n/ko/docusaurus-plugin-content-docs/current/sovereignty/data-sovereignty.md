---
sidebar_position: 7
title: "데이터 주권"
description: "원주민 언어 번역을 위한 OCAP, CARE, Māori 데이터 주권 원칙입니다. 배포에 앞서 커뮤니티의 동의가 필요한 이유를 설명해요."
related:
  - label: "Ownership Transfer"
    to: /docs/sovereignty/ownership-transfer
    kind: doc
    note: "How control of language data moves to communities"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
---
# 데이터 주권

> **핵심 요약.** 이 페이지에서는 OCAP®, CARE, Te Mana Raraunga 데이터 주권 원칙과, 원주민 언어를 위한 번역 방식을 구축하는 개발자에게 이 원칙들이 어떤 의미를 갖는지 설명해요. 커뮤니티의 동의가 필요한 시점, champollion의 `api` 방식 아키텍처가 데이터 주권을 어떻게 지원하는지, 그리고 원주민 언어 데이터를 다루는 모든 사람의 윤리적 의무를 다뤄요.

원주민 언어를 위한 기계 번역은 프랑스어나 일본어에는 존재하지 않는 질문들을 제기해요. 학습 데이터는 누가 소유하나요? 언어 모델이 말하는 방식은 누가 통제하나요? 번역이 출판할 만큼 충분히 좋은지는 누가 결정하나요?

**그 답은 언제나 커뮤니티예요.**

champollion은 이를 지원하도록 만들어졌어요. `api` 방식은 모든 언어 자원을 서버 측에서 커뮤니티의 통제 아래 유지해요. 플러그인 시스템은 방식과 도구를 분리해요. 하지만 도구가 윤리를 강제할 수는 없어요 — 이 페이지에서는 여러분이 따라야 할 원칙들을 설명해요.

---

## OCAP® 원칙

**OCAP**(Ownership, Control, Access, Possession)은 [First Nations Information Governance Centre](https://fnigc.ca/ocap-training/)(FNIGC)에서 개발한 원칙 모음으로, First Nations 데이터를 어떻게 수집, 보호, 사용, 공유해야 하는지를 규정해요.

| 원칙 | 번역에 있어 의미하는 바 |
|-----------|------------------------------|
| **Ownership(소유권)** | 커뮤니티는 자신들의 언어 데이터 — 사전, 문법, 병렬 텍스트, 코칭 파일, 그리고 그로부터 생성된 모든 번역 — 를 소유해요. |
| **Control(통제권)** | 커뮤니티는 자신들의 언어 데이터가 어떻게 사용되는지, 누가 접근할 수 있는지, 어떤 번역 방식이 허용되는지를 통제해요. |
| **Access(접근권)** | 커뮤니티 구성원은 데이터가 어디에 저장되어 있든 자신들의 언어 자원에 접근하고 관리할 권리를 가져요. |
| **Possession(보유권)** | 물리적 데이터(코칭 파일, 사전, 모델 가중치)는 제3자 클라우드가 아니라 커뮤니티가 통제하는 인프라에 존재해야 해요. |

### OCAP이 실제로 의미하는 것

- 명시적인 커뮤니티 승인 없이 원주민 언어의 **번역을 출판하지 마세요**.
- 데이터 공유 협약 없이 커뮤니티가 제공한 언어 데이터로 **모델을 학습시키지 마세요**.
- 웹사이트, 소셜 미디어, 교육 자료에서 커뮤니티의 언어 자원을 **스크래핑하지 마세요**.
- 프롬프트, 코칭 데이터, 사전이 커뮤니티가 통제하는 서버에 머물도록 **`api` 방식을 사용하세요**. champollion의 `api` 방식은 "단순 파이프(dumb pipe)"예요 — 키를 내보내고 번역을 받아 와요. 모든 언어 IP는 서버 측에 남아 있어요.
- **출처를 문서화하세요** — [플러그인 매니페스트](https://champollion.dev/docs/reference/plugin-spec)의 `provenance` 필드에는 사용된 모든 자원과 그 라이선스, 출처를 나열해야 해요.

:::warning OCAP®은 등록 상표예요
OCAP®은 First Nations Information Governance Centre의 등록 상표예요. 이는 특히 캐나다의 First Nations에 적용돼요. 그 원칙들은 더 넓은 관련성을 갖지만, 상표권과 거버넌스 권한은 FNIGC에 속해요.
:::

---

## CARE 원칙

**원주민 데이터 거버넌스를 위한 CARE 원칙**은 [Global Indigenous Data Alliance](https://www.gida-global.org/care)(GIDA)에서 FAIR 데이터 원칙을 보완하기 위해 개발했어요. FAIR는 데이터가 Findable(검색 가능), Accessible(접근 가능), Interoperable(상호 운용 가능), Reusable(재사용 가능)해야 한다고 말해요. CARE는 그것으로는 충분하지 않으며, 데이터 거버넌스가 원주민의 권리도 중심에 두어야 한다고 말해요.

| 원칙 | 적용 |
|-----------|------------|
| **Collective Benefit(집단적 혜택)** | 번역 도구는 무엇보다 언어 커뮤니티에 혜택을 주어야 해요. 리더보드 점수는 방식을 개선하기 위한 수단이지, 커뮤니티 언어에서 상업적 가치를 추출하기 위한 것이 아니에요. |
| **Authority to Control(통제 권한)** | 커뮤니티는 자신들의 언어 데이터가 어떻게 수집, 사용, 공유되는지를 관장할 권한을 가져요. 높은 리더보드 점수가 번역을 출판할 허가를 부여하지는 않아요. |
| **Responsibility(책임)** | 원주민 언어 데이터를 다루는 연구자와 개발자는 관계를 구축하고, 동의를 얻으며, 혜택을 공유할 책임이 있어요. |
| **Ethics(윤리)** | 원주민의 권리와 안녕이 최우선 관심사여야 해요. 번역 방식은 커뮤니티에 *대해서(about)*가 아니라 커뮤니티와 *함께(with)* 개발되어야 해요. |

---

## Te Mana Raraunga — 마오리 데이터 주권

**Te Mana Raraunga**는 [마오리 데이터 주권 네트워크(Māori Data Sovereignty Network)](https://www.temanararaunga.maori.nz/)예요. 이 네트워크는 마오리 데이터 — 언어 데이터를 포함하여 — 가 와이탕이 조약(Treaty of Waitangi)과 tikanga Māori(마오리 관습법)의 원칙을 따르는 taonga(보물)라고 주장해요.

주요 원칙:

| 원칙 | 의미 |
|-----------|---------|
| **Rangatiratanga(권한)** | 마오리는 언어 데이터를 포함한 자신들의 데이터에 대해 권한을 행사할 고유한 권리를 가져요. |
| **Whakapapa(관계)** | 데이터에는 기원과 연결이 있어요. 언어 데이터는 그것을 만든 사람들의 관계와 지식을 담고 있어요. |
| **Whanaungatanga(의무)** | 마오리 데이터를 보유하거나 처리하는 이들은 그 데이터가 비롯된 커뮤니티에 대해 상호적 의무를 가져요. |
| **Kotahitanga(집단적 혜택)** | 마오리 데이터는 마오리의 집단적 혜택을 위해 사용되어야 해요. |
| **Manaakitanga(상호성)** | 마오리 데이터의 사용에는 배려, 존중, 상호성이 포함되어야 해요. |
| **Kaitiakitanga(수호)** | 데이터 수호자는 데이터를 보호하고 적절하게 사용되도록 보장할 의무가 있어요. |

이 원칙들은 te reo Māori(마오리어)와 마오리 언어 데이터를 다루는 모든 전산 작업에 적용돼요.

---

## 이것이 champollion 사용자에게 의미하는 바

### 표준 언어(프랑스어, 일본어, 스페인어...)의 경우

champollion을 평소대로 사용하세요. 이 언어들은 크고 공개적으로 이용 가능한 코퍼스, 확립된 번역 API를 갖추고 있으며 주권 관련 우려가 없어요. 원하는 대로 번역하고, 동기화하고, 출판하세요.

### 원주민 언어 및 저자원 언어의 경우

상황은 근본적으로 달라요:

1. **먼저 동의를 받으세요.** 원주민 언어를 위한 번역 방식을 구축하기 전에 커뮤니티와 관계를 맺으세요. 커뮤니티의 참여 없이 구축된 방식은 — 기술적으로 아무리 인상적이더라도 — 출판하거나 배포해서는 안 돼요.

2. **`api` 방식을 사용하세요.** 번역 파이프라인을 커뮤니티가 통제하는 인프라에 호스팅하세요. champollion의 `api` 방식은 이를 위해 설계되었어요: 방식을 작동시키는 프롬프트, 사전, 코칭 데이터를 노출하지 않고 키를 보내고 번역을 받아 와요.

    ```json title="Community-controlled setup"
    {
      "pairs": {
        "en:crk": {
          "method": "api",
          "endpoint": "https://api.community-server.example/translate"
        }
      }
    }
    ```

3. **모든 것을 문서화하세요.** 플러그인 매니페스트의 `provenance` 필드를 사용하여 모든 자원, 그 라이선스, 그리고 커뮤니티 동의하에 제공되었는지 여부를 나열하세요.

4. **점수는 라이선스가 아니에요.** 리더보드에서의 높은 점수는 방식이 기술적으로 잘 작동한다는 것을 입증해요. 그것이 번역을 출판하거나, 플러그인을 배포하거나, 방식을 상업화할 허가를 부여하지는 않아요. 커뮤니티가 결정해요.

5. **데이터가 아니라 방식을 공유하세요.** 잘 작동하는 기법(예: "코칭된 프롬프트를 사용한 FST-게이팅 LLM")을 개발한다면, 그 *아키텍처*와 *접근법*을 리더보드에 공유하세요. 커뮤니티는 자신들의 특정 언어에 그것을 작동하게 만드는 언어 데이터에 대한 통제권을 유지해요.

---

## `api` 방식과 주권

`api` [번역 방식](https://champollion.dev/docs/guides/translation-methods)은 데이터 주권을 지원하기 위해 특별히 존재해요. 그 이유는 다음과 같아요:

| 측면 | 다른 방식 | `api` 방식 |
|--------|--------------|-------------|
| **프롬프트가 존재하는 곳** | champollion의 설정 파일 안(모든 개발자에게 보임) | 커뮤니티의 서버(비공개) |
| **코칭 데이터가 존재하는 곳** | `.champollion/coaching/` 디렉터리 안(git에 커밋됨) | 커뮤니티의 서버(비공개) |
| **사전이 존재하는 곳** | 플러그인 디렉터리 안(플러그인과 함께 배포됨) | 커뮤니티의 서버(비공개) |
| **파이프라인을 통제하는 주체** | `champollion sync`을 실행하는 누구든 | API를 운영하는 커뮤니티 |
| **champollion이 보는 것** | 모든 것 | 들어오는 키, 나가는 번역 |

`api` 방식은 의도적인 아키텍처 선택이에요. 그것이 "단순 파이프(dumb pipe)"인 이유는 IP — 언어 지식, 문법 규칙, 신중하게 큐레이션된 코칭 예시 — 가 도구가 아니라 커뮤니티에 속하기 때문이에요.

구현 세부 사항은 [API를 통한 방식 제공](https://champollion.dev/docs/guides/serving-a-method)을 참고하세요.

---

## 사례 연구: OMT-1600과 데이터 주권

Meta의 OMT-1600(2026년 3월)은 원주민 언어에 데이터 주권이 왜 중요한지 보여 주는 구체적인 예시예요. OMT-1600은 다음을 사용하여 1,600개 언어를 위한 번역 모델을 학습시켰어요:

- **CC-2000-Web**: 2,000개 이상의 languoid에서 웹 스크래핑한 단일어 텍스트 — 커뮤니티 동의 없이 수집됨
- **성경 번역본**: 최저자원 언어를 위한 병렬 학습 및 평가 데이터로 사용된 종교 텍스트
- **MeDLEy**: 수작업으로 큐레이션된 bitext — 그러나 OCAP® 또는 CARE 준수 사항이 문서화되지 않음
- **역번역 합성 데이터**: 모델이 자체적으로 생성한 약 2억 7천만 개의 합성 병렬 문장

Plains Cree(CRK)와 같은 원주민 언어의 경우, 이는 다음을 의미해요:

| 원칙 | OMT-1600의 실제 관행 | 영향 |
|-----------|-------------------|--------|
| **Ownership(소유권)** | Meta가 모델을 소유하고 그것을 어떻게 공개할지 결정함 | 커뮤니티는 자신들의 언어가 모델화되는 방식에 대해 소유 지분이 없음 |
| **Control(통제권)** | Meta가 학습 데이터 선택, 모델 아키텍처, 공개 일정을 통제함 | 커뮤니티는 어떤 데이터가 사용되는지, 언어가 어떻게 표현되는지에 대해 의견을 낼 수 없음 |
| **Access(접근권)** | 모델 가중치는 현재 이용 불가능함 — "저자가 통제할 수 없는 요인으로 인해 공개되지 않음" | 커뮤니티는 자신들의 언어를 말하는 모델에 접근하거나, 검사하거나, 수정할 수 없음 |
| **Possession(보유권)** | 모든 데이터와 모델이 Meta의 인프라에 존재함 | 커뮤니티는 모델 학습에 사용된 데이터를 호스팅하거나, 감사하거나, 삭제할 수 없음 |

OMT-1600은 연구 성과예요. 그것은 또한 추출적 데이터 관행의 한 예시이기도 해요: 언어 데이터를 웹과 종교 텍스트에서 수집하여 모델로 처리하고 논문으로 출판했어요 — 모두 커뮤니티의 참여, 동의, 혜택 공유 없이요.

**이것이 바로 champollion의 주권 아키텍처가 방지하는 패턴이에요.** `api` 방식은 언어 IP를 커뮤니티가 통제하는 서버에 유지해요. 평가 코퍼스는 커뮤니티 동의하에 제공되며 커뮤니티 키 관리 아래 저장돼요. 수상 방식은 커뮤니티 소유로 이전돼요. 그 차이는 기술적인 것이 아니라 — 윤리적이고 구조적인 것이에요.

:::note OMT-1600만 잘못한 것은 아니에요
이 패턴 — 커뮤니티 동의 없는 웹 스크래핑에 이은 모델 학습 — 은 대규모 다국어 NLP 연구에서 표준 관행이에요. OMT-1600이 사례 연구가 된 것은 그 규모(1,600개 언어)와 최근성(2026년 3월) 때문이지, 유독 추출적이기 때문이 아니에요. 같은 비판이 NLLB-200, Google의 다국어 작업, 그리고 대부분의 대규모 MT 연구에 적용돼요.
:::

---

## 추가 자료

- [First Nations Information Governance Centre — OCAP®](https://fnigc.ca/ocap-training/)
- [Global Indigenous Data Alliance — CARE Principles](https://www.gida-global.org/care)
- [Te Mana Raraunga — Māori Data Sovereignty Network](https://www.temanararaunga.maori.nz/)
- [USIDSN — United States Indigenous Data Sovereignty Network](https://usindigenousdata.org/)

---

## 함께 보기

- [저자원 언어 지원하기](/docs/community/low-resource-languages) — OCAP 맥락이 담긴 기술 가이드
- [번역 방식](https://champollion.dev/docs/guides/translation-methods) — `api` 방식과 그것이 IP를 보호하는 방법
- [API를 통한 방식 제공](https://champollion.dev/docs/guides/serving-a-method) — 커뮤니티가 통제하는 파이프라인 호스팅하기
- [플러그인 명세](https://champollion.dev/docs/reference/plugin-spec) — 자원 출처 표시를 위한 `provenance` 필드
- [Cookbook: FST-게이팅 파이프라인](/docs/tutorials/fst-gated-pipeline) — 커뮤니티가 직접 호스팅할 수 있는 파이프라인 구축하기