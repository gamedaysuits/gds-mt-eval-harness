---
sidebar_position: 5
title: "저자원 언어 지원하기"
related:
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "The first step for an uncovered language"
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
  - label: "Plains Cree, the trading card"
    to: https://champollion.dev/trading-cards?q=crk
    kind: card
    note: "The proof-of-concept language, as a card"
---
# 저자원 언어 지원하기

> **요약.** 저자원 및 다종합어(polysynthetic) 언어를 위한 기계 번역 구축에 관한 종합 가이드예요. 이 언어들이 왜 어려운지(형태론적 복잡성, 희소한 데이터, 환각), 기존 전산 자원(ALTLab FST, GiellaLT, Apertium, UniMorph, EdTeKLA), 10가지 이상의 접근 전략, champollion 코칭 시스템, 그리고 평가 루프를 다뤄요. 소외된 언어를 위한 방법을 기여하고 싶다면 여기서 시작하세요.

:::info Status: Under Active Development
Plains Cree(nêhiyawêwin) 지원은 현재 개발 중이에요. 여기서 설명하는 도구, 평가 하네스, 리더보드는 실제로 존재하며 오늘날 사용할 수 있지만, Cree 번역 파이프라인은 아직 출시되지 않았어요. 출시되면 이 문서는 FST 인프라를 갖춘 다른 다종합어 및 저자원 언어를 위한 청사진 역할을 하게 될 거예요.
:::

## 아직 해결되지 않은 문제

Google Translate는 약 130개 언어를 지원해요. Meta의 OMT-1600(2026년 3월)은 1,600개 언어를 다룬다고 주장하는데, 이는 지금까지 발표된 MT 시스템 중 가장 큰 규모예요. 하지만 가장 낮은 자원 등급에 속하는 약 1,300개 언어의 경우 품질은 사용 가능한 임계치 이하이고, 학습 데이터는 성경 텍스트가 지배적이며, 모델 가중치는 다운로드할 수 없고, 독립적인 평가나 커뮤니티 거버넌스 프레임워크도 없어요. 나머지 약 5,400개 언어의 경우, 어떤 사전 학습 모델도 결과물을 전혀 생성하지 못해요.

지형이 크게 바뀌었어요. 이제 빅테크가 LRL 커버리지에 투자하고 있죠. 하지만 커버리지가 곧 품질은 아니며, 독립적인 검증이 없는 품질은 신뢰가 아니에요. 저자원 언어에는 자신들을 다룬다고 주장하는 모델 이상의 것이 필요해요. 형태론적 검증을 동반한 독립적인 평가, 커뮤니티가 큐레이션한 코퍼스, 그리고 주권을 존중하는 거버넌스가 필요해요.

**champollion은 이를 바꾸기 위해 만들어졌어요.**

[Method Leaderboard](https://champollion.dev/leaderboard)는 공개 챌린지예요. 소외된 언어를 위한 최고의 번역 방법을 구축하고, 재현 가능한 평가로 이를 입증하며, 최고 점수를 차지하세요. 전 세계 누구나 기여할 수 있어요. 언어학자, ML 연구자, 커뮤니티 언어 활동가, 학생, 취미로 하는 분까지요. 이 문제는 아직 해결되지 않았어요. 인프라는 여기 있어요. 리더보드가 여러분을 기다리고 있어요.

---

## 왜 어려운가: 다종합어 형태론

대부분의 상용 MT 시스템은 영어, 프랑스어, 중국어 같은 언어를 위해 설계됐어요. 이런 언어들은 단어가 비교적 짧고 문장이 개별 토큰으로 구성돼요. 하지만 Plains Cree를 포함한 많은 토착 언어는 **다종합어**예요. 한 단어가 영어로는 문장 전체로 표현되는 내용을 담을 수 있어요.

### Cree 예시

다음 Plains Cree 단어를 보세요:

> **ê-kî-nitawi-kîskinwahamâkosiyân**
> *"내가 학교에 갔을 때"*

이게 **한 단어**예요. 이 단어는 시제(과거), 방향(~로 가는), 어근(배우다), 태(수동/재귀), 인칭(1인칭 단수)을 모두 인코딩해요. 주로 영어로 학습된 LLM은 이런 종류의 형태론적 밀도에 대한 직관이 없어요.

문제들은 복합적으로 작용해요:

| 문제 | 의미 |
|-----------|--------------|
| **형태론적 복잡성** | 하나의 동사 어근이 접두사화, 접미사화, 접요사화를 통해 수천 개의 유효한 굴절형을 생성할 수 있어요 |
| **유정물/무정물 구분** | 명사는 문법적으로 유정물 또는 무정물이에요. 이는 동사 활용, 지시사, 복수화에 영향을 미쳐요. 이 분류가 항상 생물학적 유정성을 따르는 것은 아니에요(*askiy* "땅"은 유정물이고, *maskisin* "신발"도 유정물이에요) |
| **방외화(Obviation)** | 3인칭 지시 대상은 근접성/현저성에 따라 순위가 매겨져요. "근접(proximate)"과 "방외(obviative)" 구분은 영어에 대응어가 없어요 |
| **희소한 학습 데이터** | LLM은 Plains Cree 텍스트를 매우 적게 봤어요. 본 것조차 방언(Y-방언, TH-방언)이나 정서법(SRO 대 음절문자)이 혼재되어 있을 수 있어요 |
| **약한 상용 베이스라인** | OMT-1600은 성경 도메인 학습과 표준 BPE 토큰화로 CRK를 R1(매우 낮은 자원) 등급에 포함하고 있어요. Google Translate는 Cree를 지원하지 않아요. 이러한 베이스라인을 의미 있게 만드는 것은 형태론적 지표를 동반한 독립적인 평가예요. |

다종합어의 번역은 여전히 **미해결 연구 문제**예요. OMT-1600은 다종합어를 포함하지만 형태론적 인식이 없는 표준 BPE 토큰화(256K 어휘)를 사용해요. 즉, 합성적 단어를 의미 없는 바이트 조각으로 잘라버려요.

---

## 선행 연구: 사람들은 이 문제에 어떻게 접근해 왔나

### ALTLab FST

Plains Cree를 위한 가장 중요한 전산 자원은 University of Alberta의 [Alberta Language Technology Lab (ALTLab)](https://altlab.artsrn.ualberta.ca/)이 UiT The Arctic University of Norway의 [Giellatekno](https://giellatekno.uit.no/)와 협력하여 개발한 **유한상태 변환기(finite-state transducer, FST)**예요.

ALTLab FST는 **형태론적 분석기이자 생성기**예요. 굴절된 Cree 단어가 주어지면 이를 어근과 문법 태그로 분해할 수 있고, 어근과 태그가 주어지면 올바른 굴절형을 생성할 수 있어요. 이는 결정론적이에요. 신경망도, 환각도, 확률도 없어요. FST가 어떤 단어를 받아들이면, 그 단어는 형태론적으로 유효한 거예요.

이것이 champollion 리더보드가 **FST Acceptance Rate**를 지표로 추적하는 이유예요. FST가 거부하는 단어를 생성하는 번역 방법은 형태론적으로 유효하지 않은 Cree를 생성하는 것이에요. chrF++ 점수가 무엇이라고 말하든 상관없이요.

**주요 ALTLab 자원:**
- [itwêwina](https://itwewina.altlab.app/) — FST로 구동되는 지능형 Plains Cree–영어 사전
- [Morphodict](https://github.com/UAlbertaALTLab/morphodict) — 형태론을 인식하는 오픈소스 사전 플랫폼
- [crk-db](https://github.com/UAlbertaALTLab/crk-db) — Plains Cree 어휘 데이터베이스
- [21st Century Tools for Indigenous Languages](https://21c.tools/) — 더 넓은 프로젝트 맥락

### 글로벌 FST 및 형태론 레지스트리

Plains Cree만이 고품질 FST 인프라를 갖춘 유일한 언어는 아니에요. 다른 저자원 또는 형태론적으로 복잡한 언어를 위한 번역 파이프라인을 개발하고 싶다면, 다음과 같이 잘 구축된 글로벌 허브를 활용할 수 있어요:

* **[GiellaLT / Giellatekno](https://giellalt.github.io/) (UiT The Arctic University of Norway):** 100개 이상의 언어를 다루는 오픈소스 FST 형태론적 분석기 및 생성기 중 가장 큰 저장소예요. 중점 영역으로는 Sámi 언어(`sme`, `smj`, `sma` 등), 우랄어족 언어(Komi, Erzya, Udmurt 등), 그리고 기타 소수/토착 언어가 있어요. 이들은 [GitHub Organization](https://github.com/giellalt/)에서 공개적으로 처리된 텍스트 코퍼스(`corpus-xxx`)를 호스팅하고 있어요.
* **[The Apertium Project](https://www.apertium.org/):** 오픈소스 규칙 기반 기계 번역 플랫폼이에요. Apertium은 Turkic 언어 대규모 모음(Kazakh, Tatar, Kyrgyz 등)과 소수 유럽 언어를 포함한 수십 개 언어에 대해 고도로 최적화된 FST 형태론적 분석기(`lttoolbox` 및 `hfst` 사용)와 이중 언어 사전을 유지하고 있어요. 모든 자원은 [Apertium의 GitHub](https://github.com/apertium)에서 공개돼 있어요.
* **[UniMorph (Universal Morphology)](https://unimorph.github.io/):** 150개 이상의 언어에 대한 표준화된 형태론적 패러다임을 제공하는 공동 프로젝트예요. 데이터셋은 Hugging Face의 [unimorph/universal_morphologies](https://huggingface.co/datasets/unimorph/universal_morphologies)에서 호스팅돼요. 특정 언어에 대해 컴파일된 FST 바이너리를 사용할 수 없는 경우, UniMorph 테이블을 정적 데이터베이스 조회 게이트로 사용할 수 있어요.
* **[National Research Council Canada (NRC)](https://nrc-digital-repository.canada.ca/):** **Uqailaut** Inuktitut FST 형태론적 분석기와 방대한 **Nunavut Hansard Parallel Corpus**(영어-Inuktitut 정렬 문장 쌍 130만 개)를 포함한 캐나다 토착 언어 도구를 제공해요.

### EdTeKLA 코퍼스

[EdTeKLA 연구 그룹](https://spaces.facsci.ualberta.ca/edtekla/)(역시 UAlberta 소속)은 교육 자료, 오디오 전사, 커뮤니티 출처에서 Plains Cree 언어 코퍼스를 구축했어요. champollion 평가 데이터셋 [EDTeKLA Dev v1](/docs/leaderboard/datasets)은 이 작업에서 파생됐으며, [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 라이선스를 따라요.

### 사람들이 시도했거나 시도할 수 있는 다른 접근법

리더보드는 방법에 구애받지 않아요. 다음은 저자원 MT를 위해 탐구되거나 제안된 전략들로, 어느 것이든 제출할 수 있어요:

| 접근법 | 작동 방식 | 장점 | 단점 |
|----------|-------------|------|------|
| **[Coached LLM prompting](/docs/tutorials/coached-llm-prompting)** | 문법 규칙, 사전, 예시 쌍을 시스템 프롬프트에 주입해요 | 빠른 반복, 학습 불필요 | LLM의 기본 지식에 의해 품질 상한이 제한돼요 |
| **[Few-shot prompting](/docs/tutorials/few-shot-prompting)** | 검증된 번역을 컨텍스트 내 예시로 포함해요 | 일관된 스타일에 적합 | 작은 컨텍스트 윈도우; 예시는 평가 데이터에서 가져오면 안 돼요 |
| **[FST-gated pipeline](/docs/tutorials/fst-gated-pipeline)** | LLM이 생성 → FST가 검증 → 유효하지 않은 형태론을 거부하고 재시도해요 | 형태론적 유효성을 보장해요 | FST 인프라 필요; 재시도 루프가 지연과 비용을 더해요 |
| **[Dictionary lookup + LLM](/docs/tutorials/dictionary-augmented-llm)** | 이중 언어 사전에서 알려진 용어를 강제하고 나머지는 LLM이 처리하게 해요 | 알려진 용어의 환각을 줄여요 | 사전 커버리지는 항상 불완전해요 |
| **[Fine-tuned model](/docs/tutorials/fine-tuned-model)** | 오픈 모델(Llama, Mistral)을 병렬 텍스트로 파인튜닝해요. 단, 평가 데이터로는 안 돼요 | 잠재적으로 가장 높은 품질 | 병렬 코퍼스 필요(희소); 비용이 큼; 과적합 위험 |
| **[Chained models](/docs/tutorials/chained-models)** | 모델 A가 대략적인 번역 생성 → 모델 B가 사후 편집 → 모델 C가 점수 매김 | 전문가의 강점을 결합할 수 있어요 | 복잡함; 느림; 비용이 큼 |
| **[Rule-based + LLM hybrid](/docs/tutorials/rule-based-hybrid)** | 알려진 패턴에는 언어학적 규칙을, 나머지는 모두 LLM을 사용해요 | 규칙이 적용되는 곳에서는 정확함 | 깊은 언어학적 전문성 필요 |
| **[Back-translation augmentation](/docs/tutorials/back-translation)** | Cree→영어로 번역하여 합성 병렬 데이터를 생성한 후, 역방향으로 학습해요 | 학습 데이터를 저렴하게 확장해요 | 기존 모델 오류를 증폭시켜요 |
| **[Evolutionary approach](/docs/tutorials/evolutionary-approach)** | 후보 번역을 생성하고, 점수를 매기고, 최고 성능을 변이시키며, 반복해요 | 새로운 해법을 발견할 수 있음; 병렬화 가능 | 계산 비용이 큼; 좋은 적합도 함수 필요 |
| **[Partial translation](/docs/tutorials/partial-translation)** | 대표 샘플을 수동으로 번역하고, 그에 대해 여러분의 방법이 스타일과 일치함을 입증한 후, 나머지 대량을 자동 번역해요 | 사람의 품질과 기계의 규모를 결합해요 | 초기에 사람의 노력이 필요해요 |
| **수동 JSON / 시험 채점** | 언어 시험에서 학생 답안을 테스트하기 위해 데이터셋 JSON 파일을 수작업으로 만들거나, 사람의 번역 묶음을 골드 스탠더드와 대조해 채점해요 | ML 불필요; 교육 및 QA에 적합 | 지속적인 번역 수요에는 확장되지 않아요 |

### 그저 JSON일 뿐이에요

하네스는 JSON을 입력받아 JSON으로 점수를 출력해요. [데이터셋 형식](/docs/leaderboard/datasets)은 간단해요:

```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

이를 손으로 직접 만들 수 있어요. 스프레드시트에서 내보낼 수도 있어요. 코퍼스에서 생성할 수도 있어요. 언어 교사는 학생 번역을 채점하는 데 사용할 수 있어요. 번역 회사는 프리랜서를 벤치마킹하는 데 사용할 수 있어요. 연구실은 모델 아키텍처를 비교하는 데 사용할 수 있어요. 하네스는 JSON이 어디서 왔는지 신경 쓰지 않아요. 그저 점수를 매길 뿐이에요.

그리고 프로덕션 배포 프레임워크가 동일한 플러그인 인터페이스를 사용하기 때문에, 하네스에서 좋은 점수를 받은 방법은 설정 하나만 바꾸면 여러분의 웹사이트에 배포돼요. **입증하고 사용하세요.**

가능성은 정말로 무한해요. **아이디어가 있다면, 만들고, 하네스를 실행하고, 점수를 제출하세요.**

---

## champollion은 어떻게 맞물리는가

champollion은 인프라 계층을 제공해요. 여러분은 방법을 가져오면 돼요.

### 코칭 시스템

champollion의 `llm-coached` 방법을 사용하면 언어학적 지식을 LLM 프롬프트에 직접 주입할 수 있어요:

```json title=".champollion/coaching/crk.json"
{
  "grammar_rules": [
    "Plains Cree is polysynthetic — a single word can express what English needs a full sentence for",
    "Animate/inanimate noun distinction affects verb conjugation, demonstratives, and pluralization",
    "Use SRO (Standard Roman Orthography) as the working script — syllabic conversion is handled by the deterministic converter",
    "Obviation: when two third-person referents appear, the less salient one takes obviative marking (-a suffix on nouns, -iyiwa on verbs)"
  ],
  "dictionary": {
    "home": "kīwēwin",
    "settings": "isi-nākatohkēwin",
    "search": "nānātawāpahtam",
    "welcome": "tānisi",
    "dashboard": "kīskinwahamākēwin-māsinahikan"
  },
  "style_notes": "Use formal register appropriate for educational and community contexts. Preserve English technical terms in parentheses when no Cree equivalent exists or is widely accepted."
}
```

코칭 데이터는 `en:crk` 쌍에 대한 모든 LLM 프롬프트에 주입되어, 모델에게 그렇지 않으면 갖지 못할 구조화된 언어학적 컨텍스트를 제공해요. 전체 사양은 [Coaching Data](https://champollion.dev/docs/concepts/coaching-data)를 참고하세요.

### 레지스터

레지스터는 어조, 격식, 정서법 관습을 조정하는 시스템 프롬프트의 일부예요. champollion은 하나의 Plains Cree 레지스터를 기본 제공해요:

```
nêhiyawêwin (Plains Cree). Use SRO (Standard Roman Orthography) as the working
script. Output will be converted to Syllabics via deterministic converter.
Professional register appropriate for educational and community contexts.
```

설정에서 이를 재정의하여 다양한 프롬프트 전략을 실험할 수 있어요:

```json title="champollion.config.json"
{
  "languages": {
    "crk": {
      "register": "Casual Plains Cree (Y-dialect). Use SRO. Prefer everyday vocabulary over formal or archaic terms. Address the reader directly."
    }
  }
}
```

레지스터가 다르면 번역 스타일도 달라지고, 리더보드 점수도 달라져요. 각 제출은 사용된 정확한 레지스터와 시스템 프롬프트를 기록하므로([run card](/docs/specifications/run-card)에 SHA-256 해시로), 실험은 재현 가능해요.

### 스크립트 변환

Plains Cree는 두 가지 스크립트로 쓰여요: **Standard Roman Orthography (SRO)**와 **Canadian Aboriginal Syllabics**예요. champollion의 파이프라인은:

1. LLM이 SRO로 번역해요(라틴 기반으로, LLM이 더 잘 다뤄요)
2. 품질 게이트가 SRO 출력을 검증해요
3. 결정론적 변환기가 SRO → Syllabics로 변환해요
4. 변환된 텍스트가 디스크에 기록돼요

변환기는 모든 SRO 발음 구별 부호(장모음의 경우 ê, î, ô, â)를 처리하고 이를 올바른 음절문자에 매핑해요. 기술적 세부 사항은 [Script Converters](https://champollion.dev/docs/concepts/script-converters)를 참고하세요.

### 평가 루프

[eval harness](/docs/specifications/harness)는 평가 데이터셋에 대해 여러분의 방법을 실행하고 점수가 매겨진 [run card](/docs/specifications/run-card)를 생성해요:

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install -e .

# Run a baseline experiment
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v7

# Run with FST validation (if you have an FST binary)
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --fst-analyzer ./bin/crk-analyzer \
  --condition fst-gated-v1
```

`--condition` 플래그는 여러분이 선택하는 라벨이에요. 이는 리더보드에 표시되어 사람들이 여러분이 어떤 프롬프트 전략을 사용했는지 볼 수 있어요. 하네스는 전체 시스템 프롬프트를 run card에 기록하므로, 여러분의 정확한 접근법은 재현 가능해요.

:::tip Experiment freely, submit your best
하네스는 빠른 반복을 위해 설계됐어요. 다양한 모델, 코칭 데이터, 레지스터, 조건으로 수십 가지 실험을 실행하세요. 자랑스러운 결과가 나왔을 때만 리더보드에 제출하세요.
:::

---

## OCAP 원칙

champollion은 토착민 데이터 주권을 지원하도록 설계됐어요. [OCAP 원칙](https://fnigc.ca/ocap-training/)(Ownership, Control, Access, Possession)은 토착 커뮤니티를 위한 언어 기술에 우리가 접근하는 방식을 안내해요:

| 원칙 | champollion이 지원하는 방식 |
|-----------|------------------------|
| **Ownership** | 언어 커뮤니티가 자신의 언어 데이터를 소유해요. champollion은 절대 본사로 연결하거나 데이터를 우리 서버로 전송하지 않아요 |
| **Control** | [API method](https://champollion.dev/docs/guides/serving-a-method)를 통해 커뮤니티는 자체 번역 파이프라인을 호스팅할 수 있어요. 우리는 인터페이스를 제공하고, 그들이 구현을 통제해요 |
| **Access** | 커뮤니티가 누가 자신의 방법을 사용할 수 있는지 결정해요. API는 인증 뒤에 게이트할 수 있어요 |
| **Possession** | 모든 번역 데이터는 여러분 프로젝트의 파일 시스템에 머물러요. [provenance system](https://champollion.dev/docs/concepts/security)이 모든 번역이 어디서 왔는지 추적해요 |

플러그인 아키텍처 덕분에 커뮤니티는 신성하거나 제한된 지식을 내부적으로 통합한 방법을 구축하고, 번역 API만 노출하며, 자신의 언어 자원에 대한 완전한 통제를 유지할 수 있어요.

---

## 비전: 다음에 올 것

Plains Cree는 첫 번째 대상이에요. 파이프라인이 검증되고 커뮤니티가 품질에 만족하면, 동일한 아키텍처가 FST 인프라를 갖춘 다른 다종합어로 확장돼요:

- **다른 Algonquian 언어**: Woods Cree, Swampy Cree, Ojibwe, Blackfoot
- **Inuit 언어**: Inuktitut, Inuinnaqtun(이 역시 음절 스크립트를 사용해요)
- **다른 어족**: FST 분석기를 갖춘 모든 언어는 FST-gated 파이프라인을 사용할 수 있어요

리더보드는 언어 쌍 범위로 구성돼요. 언어 커뮤니티가 새로운 평가 데이터셋을 기여하면, 새로운 리더보드 트랙이 자동으로 열려요.

**이것은 열린 초대장이에요.** 저자원 언어를 다루는 분이라면, 연구자든, 커뮤니티 구성원이든, 학생이든, 그저 관심 있는 사람이든, champollion은 실제로 무언가를 구축하고, 정직하게 측정하며, 세상과 공유할 수 있는 도구를 제공해요. [Method Leaderboard](https://champollion.dev/leaderboard)가 여러분의 제출을 기다리고 있어요.

---

## 함께 보기

- **[Method Leaderboard](https://champollion.dev/leaderboard)** — 점수를 제출하고 방법들이 어떻게 비교되는지 확인하세요
- **[MT Evaluation](/docs/leaderboard/rules)** — 무엇이 좋은 방법이고, 무엇이 실격되는지
- **[Eval Harness](/docs/specifications/harness)** — 실험 실행 방법
- **[Evaluation Datasets](/docs/leaderboard/datasets)** — EDTeKLA Dev v1과 FLORES+
- **[Coaching Data](https://champollion.dev/docs/concepts/coaching-data)** — LLM을 위한 언어학적 지식 구조화 방법
- **[Script Converters](https://champollion.dev/docs/concepts/script-converters)** — SRO→Syllabics 파이프라인
- **[Serving a Method via API](https://champollion.dev/docs/guides/serving-a-method)** — 커뮤니티가 통제하는 번역 호스팅
- **[ALTLab](https://altlab.artsrn.ualberta.ca/)** — Alberta Language Technology Lab
- **[EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/)** — Educational Technology, Knowledge & Language 연구 그룹
- **[itwêwina dictionary](https://itwewina.altlab.app/)** — FST로 구동되는 Plains Cree–영어 사전