---
sidebar_position: 2
title: "Eval Harness v2.0"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "What the harness metrics feed into"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: Translate 30 Languages"
    to: https://champollion.dev/docs/tutorials/translate-30-languages
    kind: champollion
    note: "Use the harness to audit registers in production"
---
# Eval Harness v2.0

> **요약.** 이 페이지에서는 MT 평가 하니스 — 표준화된 코퍼스에 대해 번역 방법을 벤치마킹하고 점수가 매겨진 run card를 생성하는 도구 — 의 설치, 구성, 사용법을 다뤄요. 메트릭, 스키마, 평가 프로토콜의 표준 정의는 [Benchmark Specification](/docs/specifications/benchmark)을 참고하세요.

하니스는 번역 실험을 실행하고 run card를 생성해요. 프롬프트 구성, API 호출, 채점, 결과 직렬화를 처리하고 — 데이터셋과 모델은 여러분이 제공해요.

## 설치

**요구 사항:** Python 3.10+

```bash
pip install sacrebleu aiohttp
```

하니스 저장소를 클론하세요:

```bash
git clone https://github.com/gamedaysuits/arena.git
cd arena
```

## 사용법

```bash
mt-eval run --corpus path/to/dataset.json
```

이렇게 하면 코퍼스의 모든 항목을 구성된 모델(또는 method 플러그인)을 통해 실행하고, 출력을 채점하며, run card JSON 파일을 출력 디렉터리에 작성해요.

## CLI 플래그

### `mt-eval run`

| 플래그 | 필수 | 기본값 | 설명 |
|------|----------|---------|-------------|
| `--corpus` | ✅ | — | 코퍼스 파일 경로 (`.json`, `.jsonl`, `.tsv`) |
| `--source-file` / `--reference-file` | — | — | 병렬 텍스트 파일 (FLORES+, WMT 형식) |
| `-m, --model` | — | `gemini-pro` | 모델 slug (짧은 이름 또는 전체 OpenRouter ID). `shared/model-aliases.json`을 통해 해석돼요. 다중 모델 실행 시 쉼표로 구분 |
| `-d, --dataset` | — | `all` | 데이터셋 필터: `all`, 세그먼트 이름, 또는 ID 범위 |
| `--ids` | — | — | 평가할 항목 ID(쉼표로 구분) |
| `--source-lang` | — | `English` | 출발 언어 이름 |
| `--target-lang` | — | — | 도착 언어 이름 |
| `-p, --prompt` | — | `naive` | 프롬프트 버전 (`naive`, `custom`, `champollion`) |
| `--coaching-file` | — | — | 코칭 프롬프트 텍스트 파일 경로 |
| `--coaching` | — | — | 인라인 코칭 텍스트(따옴표로 묶은 문자열) |
| `--method` | — | — | method 플러그인 디렉터리 경로 (`method.json` + Python 모듈 포함) |
| `--method-card` | — | — | 리더보드 메타데이터용 method card JSON 경로 |
| `--fst-retries` | — | `0` | FST 재시도 횟수 (기본 LLM method 전용) |
| `--skip-fst` | — | `false` | FST 품질 게이트를 완전히 건너뛰기 |
| `--tools` | — | `false` | tool-calling 모드 활성화 |
| `--tools-list` | — | — | 도구 이름(쉼표로 구분) |
| `--max-tool-rounds` | — | `8` | 항목당 최대 tool-calling 라운드 수 |
| `--hooks` | — | — | 번역 후 hook 이름 |
| `--style-profile` | — | — | 스타일 프로필 JSON 경로. 작문 스타일 일관성 메트릭을 활성화해요 (정보 제공용 — 절대 composite score의 일부가 아님; [§ 작문 스타일 및 레지스터 메트릭](#writing-style-and-register-metrics-informational) 참고) |
| `-b, --batch-size` | — | `25` | API 호출당 항목 수 |
| `-c, --concurrency` | — | `8` | 병렬 API 호출 |
| `--max-tokens` | — | `32768` | API 호출당 최대 토큰 수 |
| `--temperature` | — | `0.0` | 샘플링 temperature (0.0 = 결정론적) |
| `--no-cache` | — | `false` | 응답 캐싱 비활성화 |
| `--cache-dir` | — | `eval/cache/harness` | 캐시 디렉터리 경로 |
| `-o, --output-dir` | — | `eval/logs/harness` | run card 및 로그를 위한 출력 디렉터리 |
| `-n, --name` | — | — | 사람이 읽을 수 있는 실행 이름 |
| `--dry-run` | — | `false` | API 호출 없이 구성 검증 |
| `--champollion-config` | — | — | `champollion.config.json` 경로 |
| `--champollion-cards-dir` | — | — | 언어 카드 디렉터리 |
| `--target-lang-code` | — | — | BCP-47 언어 코드 |

### 기타 하위 명령

| 하위 명령 | 설명 |
|------------|-------------|
| `mt-eval test <log_path>` | 완료된 실행 로그 분석 |
| `mt-eval publish <report_path>` | 리더보드에 run card 제출 |
| `mt-eval compare <logs...>` | 여러 실행을 나란히 비교 |
| `mt-eval dashboard <logs...>` | 실행 로그에서 HTML 대시보드 생성 |
| `mt-eval list models\|prompts\|datasets` | 사용 가능한 리소스 목록 표시 |
| `mt-eval export` | 현재 설정을 champollion method 플러그인으로 패키징 |
| `mt-eval export-config` | 해석된 MethodConfig(8개의 표준 필드 전체)를 JSON으로 내보내기 |

### 예시

```bash
# Run with defaults (gemini-pro alias → google/gemini-3.1-pro-preview, naive prompt)
mt-eval run --corpus data/edtekla-dev-v1.json

# Coached experiment with coaching file
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model google/gemini-3.1-pro \
  --coaching-file prompts/crk-coaching-v8.txt \
  --temperature 0.0

# Run a custom method plugin with FST retries
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --method ./methods/fst-gated-pipeline \
  --fst-retries 3
```

---

## Run Card 스키마

모든 실험은 **run card** — 자체 완결형 JSON 문서 — 를 생성해요. 최상위 구조는 다음과 같아요:

```json
{
  "run_id": "uuid-v4",
  "harness_version": "2.0",
  "model_slug": "google/gemini-3.1-pro",
  "model_id": "gemini-3.1-pro-001",
  "condition": "baseline",
  "timestamp": "2026-06-01T03:22:41Z",
  "elapsed_seconds": 142.7,
  "dataset": { ... },
  "config": { ... },
  "method_card": { ... },
  "system_prompt_sha256": "abc123...",
  "system_prompt_used": "You are a translator...",
  "fingerprint": { ... },
  "scores": { ... },
  "totals": { ... },
  "environment": { ... },
  "results": [ ... ],
  "run_card_hash": "sha256-of-entire-card"
}
```

모든 필드가 문서화된 전체 스키마는 [Run Card Specification](/docs/specifications/run-card)을 참고하세요.

:::info 권위 있는 스키마
[Benchmark Specification](/docs/specifications/benchmark)은 run card 스키마의 단일 진실 공급원이에요. 메트릭 정의, composite 가중치, 품질 등급은 [Scoring Specification](/docs/specifications/scoring)을 참고하세요. 이 페이지는 하니스 사용법을 설명하고, 스펙은 출력의 의미를 정의해요.
:::

### 주요 블록

**`dataset`** — 어떤 데이터셋이 사용되었는지 식별하며, 결과가 특정 버전에 연결되도록 콘텐츠 해시를 포함해요:

```json
// Example using master_corpus.json (62 gold + 342 textbook = 404)
{
  "id": "edtekla-dev-v1",
  "version": "1.0",
  "language_pair": "EN→CRK",
  "sha256": "...",
  "entry_count": 404
}
```

**`scores`** — 실행에 대한 집계 메트릭:

```json
// Counts reflect the dataset used (here: master_corpus.json, 404 entries)
{
  "total": 404,
  "exact_matches": 12,
  "exact_match_rate": 0.0968,
  "fst_accepted": 87,
  "fst_acceptance_rate": 0.7016,
  "chrf_plus_plus": 42.31,
  "errors": 0,
  "avg_latency_seconds": 1.15,
  "median_latency_seconds": 1.02,
  "p95_latency_seconds": 2.34,
  "by_difficulty": { ... },
  "by_provenance": { ... }
}
```

**`totals`** — 토큰 사용량 및 비용 추적:

```json
{
  "prompt_tokens": 48200,
  "completion_tokens": 3100,
  "reasoning_tokens": 0,
  "cached_tokens": 12000,
  "total_cost_usd": 0.42,
  "cost_per_entry_usd": 0.0034,
  "reasoning_ratio": 0.0
}
```

---

## 작문 스타일 및 레지스터 메트릭 (정보 제공용)

하니스는 `WritingStyleConsistency` 메트릭 플러그인(`mt_eval_harness/plugins/writing_style.py`)을 통해 번역이 목표 **레지스터**와 **작문 스타일**에 부합하는지 평가할 수 있어요. 번역은 언어적으로 정확하더라도 잘못된 레지스터일 수 있어요 — 법률 문서의 비격식 표현, 마케팅 카피의 격식 있는 정형 문구 등 — 그리고 문자열 메트릭은 이를 알아채지 못해요. 이 메트릭들은 알아채요.

**측정 항목 (항목당):**

| 메트릭 | 척도 | 의미 |
|--------|-------|---------|
| `style_register_match` | boolean | 출력이 예상 레지스터와 일치하나요? 목표는 코퍼스 항목의 `register` 필드([Benchmark Spec §2.6](/docs/specifications/benchmark) 참고) 또는 스타일 프로필에서 가져와요 |
| `style_sentence_length_ratio` | float | 예측 대 참조 평균 문장 길이 (1.0 = 일치; 차이 = 스타일 드리프트) |
| `style_formality_score` | 0.0–1.0 | 언어별 마커 리소스를 사용한 격식/비격식 마커(T–V 대명사, 축약형 등)의 존재 여부 |

**집계:** `style_consistency_rate` — 레지스터 불일치가 감지되지 않은 항목의 비율.

`--style-profile path/to/profile.json`으로 사용자 지정 목표를 활성화하세요(예: 브랜드 보이스 프로필). 지정하지 않으면 플러그인은 가능한 경우 각 코퍼스 항목의 `register` 메타데이터로 대체해요.

:::caution 정직한 범위
이 메트릭들은 **정보 제공용일 뿐**이에요 — 절대 composite score의 일부가 아니며, 격식 감지는 학습된 판단이 아니라 마커 기반(휴리스틱)이에요. 스타일 품질에 대한 판정이 아니라 레지스터 준수에 대한 드리프트 감지기로 다뤄 주세요.
:::

---

## Fingerprint 대 Run Card Hash {#fingerprint-vs-run-card-hash}

하니스는 두 가지 별개의 해시를 생성해요. 각각 다른 목적을 위한 것이에요:

### Fingerprint

**fingerprint**는 다음 질문에 답해요: *"이 실행을 재현할 수 있나요?"*

이는 실험 구성을 정의하는 입력의 조합을 해싱해요 — 출력이 아니라요:

- Dataset SHA-256
- 모델 slug
- 조건 레이블
- System prompt SHA-256
- Temperature
- 하니스 버전

동일한 fingerprint를 가진 두 실행은 동일한 설정을 사용했어요. 그 결과는 (API 비결정성을 제외하면) 비교 가능해야 해요.

### Run Card Hash

**run card hash**는 다음 질문에 답해요: *"이 특정 결과 파일이 변조되었나요?"*

이는 전체 run card JSON의 SHA-256이에요(`run_card_hash` 필드 자체는 제외). 어떤 필드든 변경되면 — 점수, 타임스탬프, 단일 출력이든 — 해시가 깨져요.

:::info 어느 것을 언제 사용할까
비교 가능한 실행을 그룹화하려면(동일한 실험, 다른 실행) **fingerprint**를 사용하세요. 특정 결과 파일의 무결성을 검증하려면 **run card hash**를 사용하세요.
:::

---

## 리더보드에 게시하기

실행을 완료한 후 `mt-eval publish`를 사용하여 run card를 제출하세요:

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

실행 중에 `--method-card`이 제공되지 않으면, `mt-eval publish`이 대화형 마법사(`method_card_wizard.py`)를 실행하여 여러분의 method를 설명하는 과정(이름, 클래스, 사용된 도구 등)을 안내해요. 마법사 출력은 제출 전에 run card에 포함돼요.

### 수동 제출

run card는 출력 디렉터리에 JSON 파일로 저장돼요. [/leaderboard](https://champollion.dev/leaderboard)의 리더보드 UI를 통해, 또는 API를 통해 어떤 run card 파일이든 제출할 수도 있어요:

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning 리더보드 검증
리더보드는 제출된 run card를 데이터셋 레지스트리에 대해 검증해요. 알 수 없는 데이터셋을 참조하거나 `run_card_hash`이 깨진 제출은 거부돼요.
:::

:::danger 평가 데이터로 학습하지 마세요
여러분의 method가 개발 과정에서 평가 데이터셋을 본 적이 있다면 — 학습 데이터, few-shot 예시, 사전 항목, 또는 프롬프트 엔지니어링 자료로서 — 여러분의 제출은 **실격** 처리돼요. 좋은 method와 나쁜 method를 결정하는 요소는 [MT Evaluation](/docs/leaderboard/rules)을 참고하세요.
:::

---

## 함께 보기

- [MT Evaluation](/docs/leaderboard/rules) — 개요, 리더보드 가치 제안, 좋은/나쁜 method 안내
- [Evaluation Datasets](/docs/leaderboard/datasets) — 데이터셋 형식, EDTeKLA, FLORES+
- [Run Card Specification](/docs/specifications/run-card) — 전체 JSON 스키마
- [Building a Method](/docs/specifications/methods) — 평가 가능한 method 생성을 위한 method 인터페이스
- [Method Leaderboard](https://champollion.dev/leaderboard) — 실시간 벤치마크 점수
- [Benchmark Specification](/docs/specifications/benchmark) — 평가 프로토콜, 코퍼스 형식, run card 스키마
- [Scoring Specification](/docs/specifications/scoring) — 메트릭, composite 가중치, 품질 등급의 SSOT