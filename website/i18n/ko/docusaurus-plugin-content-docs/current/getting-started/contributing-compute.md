---
sidebar_position: 4
title: "컴퓨팅 자원 기여하기"
description: "토큰을 기부하세요. 본인의 API 키로 공개 큐의 오픈 벤치마크 스윕을 실행하고 결과를 게시할 수 있어요."
related:
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
  - label: "Cookbook: Coached LLM Prompting"
    to: /docs/tutorials/coached-llm-prompting
    kind: cookbook
  - label: "Cookbook: FST-Gated Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "Method Interface & Dependency Classes"
    to: /docs/specifications/methods
    kind: spec
  - label: "Leaderboard Rules & Trust Tiers"
    to: /docs/leaderboard/rules
    kind: guide
---
# 연산 자원 기여하기

> **기본 개념:** 리더보드에는 빈 칸들이 있어요 — 아무도 측정하지 않은 (언어 쌍, 모델, 조건) 조합들이죠. 저희는 이런 항목들의 공개 큐를 운영하고 있어요. 여러분이 자신의 API 키로 항목을 실행하고 리포트를 게시하면, 지도가 채워져요. "토큰 기부"는 저자원 MT 평가에 대한 실제로 인용 가능한 기여예요.

## 큐

실시간 큐는 [champollion.dev/queue.json](https://champollion.dev/queue.json)에 게시되어 있고, 설치가 필요 없는 터미널 뷰어도 있어요:

```bash
curl -fsSL champollion.dev/queue | bash
```

이 뷰어는 열린 항목과 정확한 `mt-eval run` 명령어를 *표시*만 해요 — 어떤 것도 실행하거나 여러분의 토큰을 소비하지 않아요. 각 항목에는 다음이 담겨 있어요:

- `run_command` — 복사-붙여넣기 준비 완료 (코퍼스를 가져오고 하니스를 실행해요)
- `est_cost_usd` 및 `est_basis` — 동일한 (코퍼스, 모델)에 대한 저희 자체 베이스라인 실행의 **관측된** 비용이거나, 해당 모델의 스윕 평균 항목당 비용 × 코퍼스 항목 수로부터의 **외삽값**이에요. 기준은 항목별로 명시되어 있고, 실제 비용은 실행 시점의 제공자 가격에 따라 달라져요.
- `priority` — 미포함 언어 쌍 우선, 최저자원 쌍 우선(코퍼스 크기가 프록시예요), naive가 coached보다 먼저, 가장 저렴한 모델 우선이에요.

**잠금 방식 없음 — 열린 항목 아무거나 고르세요.** 두 사람이 같은 항목을 실행하는 것은 설계상 무해해요: 모든 실행 카드는 핑거프린팅되므로(데이터셋 해시 + 모델 + 조건 + 시스템 프롬프트에 대한 SHA-256, [Benchmark Spec §3.8](/docs/specifications/benchmark)), 동일한 실행은 게시 시 중복 제거되고, 같은 구성의 독립적인 복제는 낭비가 아니라 유용한 증거예요.

큐에 들어간 코퍼스는 dev-split이고, CC-BY 계열(Tatoeba 파생)이며, `do_not_train`로 플래그되어 있어요 — 이것들은 평가 세트이지 학습 데이터가 아니에요. 비상업 라이선스 코퍼스와 격리된 코퍼스는 열린 큐에서 제외돼요.

## 설정 (한 번만)

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### 어떤 제공자 키를 써야 하나요?

이 하니스는 **모든** 모델 호출을 [OpenRouter](https://openrouter.ai/keys)를 통해 라우팅해요. 하나의 `OPENROUTER_API_KEY`로 큐 라인업의 모든 모델 — Anthropic Claude, OpenAI GPT, Google Gemini 모델 모두 — 에 도달할 수 있고, 하니스의 비용 추적과 가격 스냅샷도 동일한 OpenRouter 메타데이터에서 나오기 때문에, 보고된 실행 비용이 여러분의 키에 청구된 금액과 일치해요.

크레딧이 Anthropic, OpenAI, Google에 직접 있는 경우: 하니스는 현재 제공자 키를 직접 받지 **않아요**. 실행 카드 스키마는 그날을 위해 `api_provider` 필드를 예약해 두었지만, 현재로서는 모든 하니스 실행이 OpenRouter 실행이에요. OpenRouter 계정을 만들고 자금을 충전하는 것(또는 OpenRouter가 지원하는 곳에서 자신의 제공자 계정을 연결하는 것)이 지원되는 경로예요.

### 에이전트 빠른 경로

Claude Code나 다른 코딩 에이전트를 사용하신다면, 전체 기여 과정이 프롬프트 하나로 끝나요:

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## Tier 1 — 벤치마크 실행하기

모든 큐 항목의 `run_command`는 자체 완결적이에요. 일반적인 예시:

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

실행은 총 비용을 출력하고, 실행 로그와 채점된 리포트를 `eval/logs/`에 기록해요. 그런 다음 게시하세요:

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

게시하면 OAuth로 로그인되고(여러분의 이름이 리더보드 출처 표기가 돼요) 실행 카드가 upsert돼요. 커뮤니티 제출물은 **self-benchmarked** 신뢰 등급으로 들어가요 — "실행한 사람이 직접 제출함"이라고 분명히 표시돼요. 이것은 강등이 아니라 신뢰 모델이 작동하는 방식이에요. 실행 카드에는 누구든 여러분의 정확한 구성을 재실행하는 데 필요한 모든 것이 담겨 있어요: 데이터셋 해시, 모델, 조건, 전체 시스템 프롬프트, 비용이죠. 상위 등급(검증, 커뮤니티 검증)은 리뷰를 통해 부여돼요 — [Leaderboard Rules](/docs/leaderboard/rules)를 참조하세요.

## Tier 2 — coached 프롬프트 제작하기

하니스는 **coaching**을 일급으로 지원해요: naive 시스템 프롬프트를 실제 언어학적 지식이 담긴 것으로 교체하세요. `--coaching-file`(짧은 프롬프트의 경우 `--coaching "inline text"`)를 전달하면 하니스가 여러분의 텍스트를 시스템 프롬프트로 사용하고, 실행 로그의 출처 블록에 **전체 텍스트와 그 SHA-256**를 기록하며, 실행의 조건을 **`coached`**로 표시해요(`--prompt`를 명시적으로 설정하지 않은 경우) — 그래서 프롬프트 제작은 재현 가능하고 출처 추적이 가능한 실험이 되고, 서로 다른 두 coaching 파일이 절대 혼동될 수 없으며, coached 실행이 리더보드에서 naive 베이스라인으로 오인되는 일이 없어요.

언어의 [공개 언어 카드](https://champollion.dev/languages)에서 가져온 유형론 정보와 용어집 항목을 사용한 Faroese 작업 예시:

```text title="coaching-fao.txt"
You are translating Danish into Faroese (føroyskt).

Grammar notes:
- Faroese is a North Germanic V2 language: the finite verb is the second
  constituent of a main clause.
- Nouns inflect for case (nominative, accusative, dative, genitive),
  gender (masculine, feminine, neuter), and number. Make adjectives and
  determiners agree.
- The skerping pattern applies before -gv/-ggj sequences; preserve
  standard orthography including ð (which is silent).

Glossary (use these exact equivalents):
- language -> mál
- island -> oyggj
- weather -> veður

Style: plain register, modern standard orthography. Output only the
Faroese translation, no commentary.
```

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/dan-fao-dev-v1.json
mt-eval run --corpus dan-fao-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Faroese" \
  --coaching-file coaching-fao.txt
```

(자신만의 coaching 콘텐츠를 작성하세요 — 위의 정보는 *형태*를 보여줘요: 영향력 높은 문법 규칙 몇 가지, 모델이 틀리는 용어들의 작은 용어집, 레지스터 지침이죠. [champollion.dev/languages](https://champollion.dev/languages)의 언어 카드는 여러분이 활용할 수 있는 유형론 출처를 인용하고 있어요.)

`mt-eval compare <naive_log> <coached_log>`로 naive 베이스라인과 비교하고, 반복하고, 최고의 실행을 게시하세요. 실행은 자동으로 조건 `coached`로 게시돼요. 리더보드가 일반 라벨 대신 이름이 붙은 메서드를 표시하길 원한다면, 게시할 때 메서드 카드를 첨부하세요(게시 흐름에 마법사가 제공돼요). 프롬프트 엔지니어링만으로 저자원 쌍에서 naive 베이스라인을 능가하는 것은 진정한, 게시 가능한 발견이에요 — 설계 지침은 전체 [Coached LLM Prompting cookbook](/docs/tutorials/coached-llm-prompting)을 참조하세요.

## Tier 3 — 메서드 구축하기

가장 야심찬 기여: `TranslationMethod` 프로토콜(`translate(entries, config)`)을 구현하고 프롬프트가 아닌 실제 시스템을 벤치마크하는 것이에요. 하니스는 `--method <plugin-dir>`를 통해 이를 실행하고 여러분의 메서드 카드를 실행 카드에 임베드해요. 작업 cookbook이 있는 패턴들:

- **[FST-gated pipelines](/docs/tutorials/fst-gated-pipeline)** — 모든 후보 단어가 형태소 분석기로 검사돼요. LLM은 게이트를 통과할 때까지 재생성해요. 준결정론적이고 형태론이 보장된 출력이에요.
- **[Dictionary-augmented generation](/docs/tutorials/dictionary-augmented-llm)** — 번역 시점에 이중 언어 어휘집에서 원문 용어를 조회하고 출력을 제약해요.
- [Chained models](/docs/tutorials/chained-models), [few-shot retrieval](/docs/tutorials/few-shot-prompting), [back-translation](/docs/tutorials/back-translation), [rule-based hybrids](/docs/tutorials/rule-based-hybrid)…

메서드는 실행과 이식에 필요한 것을 설명하는 **의존성 클래스**(S/O/A1/A2/X — [메서드 명세](/docs/specifications/methods#method-validity-and-dependency-classes) 참조)를 선언해요: 자체 완결적인 파이프라인은 Class S이고, 런타임에 라이선스가 있는 사전 API를 호출하는 것은 A2예요. 정직하게 선언하세요 — 클래스가 여러분의 메서드가 경쟁할 수 있는 곳을 결정하고, 매니페스트는 감사받아요.

## 이것이 리더보드를 넘어 중요한 이유

게시된 모든 실행은 상업 제공자가 측정하지 않는 언어 쌍의 MT 품질에 대한 독립적인 증거예요. 큐는 *수요*의 공개 기록 역할도 해요: 커뮤니티가 측정할 가치가 있다고 여기는 쌍이 무엇인지, 현재 API 가격으로 커버리지에 드는 비용이 얼마인지, 기부된 연산 자원이 얼마나 멀리 미치는지를 보여주죠. 저희가 자금 지원 기관에 체계적인 스윕을 후원해 달라고 요청할 때, 이 큐와 그 채워지는 속도가 바로 수요 증거예요.