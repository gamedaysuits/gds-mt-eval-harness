---
sidebar_position: 1
title: "방법 제출하기"
related:
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
    note: "The contract your method implements"
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
    note: "What every published run must disclose"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
    note: "The fastest first method to submit"
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
---
# 메서드 제출하기

> **요약.** 첫 벤치마크 실행을 리더보드에 제출하기 위한 단계별 빠른 시작 가이드예요. 하니스를 클론하고, 데이터셋에 대해 실행하고, 실행 카드를 검토한 뒤 제출하세요. API 키가 있다면 10분이면 충분해요.

이 가이드는 첫 벤치마크 실행을 MT Eval Arena 리더보드에 제출하는 과정을 안내해 드려요.

---

## 사전 준비 사항

- **Python 3.10+**
- **OpenRouter API 키** (또는 사용하는 모델 제공자에 해당하는 키)
- **번역 메서드** — 소스 텍스트로부터 번역을 생성하는 모든 것

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## 1단계: 하니스 실행하기

하니스는 표준화된 데이터셋에 대해 메서드를 채점해요:

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| 플래그 | 기능 |
|---|---|
| `--corpus` | 평가 코퍼스 경로 (`.json`, `.jsonl`, `.tsv`) |
| `--model` | 모델 슬러그 — 짧은 별칭 (예: `gemini-pro`) 또는 전체 OpenRouter ID |
| `--condition` | 메서드의 레이블 (리더보드에 표시됨) |
| `--temperature` | 샘플링 온도 (낮을수록 더 결정론적) |
| `--fst-retries` | 선택 사항: FST 재시도 횟수 |
| `--submit` | 실행 카드를 리더보드에 자동 제출 |

하니스는 **실행 카드**를 생성해요 — 점수, 데이터셋 해시, 모델 슬러그, 그리고 결과를 정확한 실험 구성과 연결하는 암호화 지문을 담은 독립적인 JSON 파일이에요.

---

## 2단계: 실행 카드 검토하기

실행 카드는 `results/`에 저장돼요. 제출하기 전에 검토하세요:

```bash
cat results/your-run-card.json | python -m json.tool
```

확인해야 할 주요 필드:
- `scores.chrf_plus_plus` — 기본 품질 지표
- `scores.exact_match_rate` — 완벽한 번역의 비율
- `scores.fst_acceptance_rate` — 형태론적 유효성 (FST를 사용한 경우)
- `totals.total_cost_usd` — 실행 비용
- `fingerprint` — 실험의 재현성 해시

전체 스키마는 [실행 카드 명세](/docs/specifications/run-card)를 참고하세요.

---

## 3단계: 제출하기

### 자동 제출

하니스를 실행할 때 `--submit`를 전달했다면, 실행 카드가 이미 업로드되었어요.

### 수동 제출

API를 통해 어떤 실행 카드든 제출할 수 있어요:

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

또는 [리더보드 UI](https://champollion.dev/leaderboard)를 통해 업로드하세요.

---

## 다음 단계

1. 제출 내용이 검증돼요 (데이터셋 해시, 실행 카드 무결성)
2. 결과가 **Self-benchmarked** (신뢰 등급 1)로 리더보드에 표시돼요
3. **GDS Verified** 상태를 받으려면, 관리자가 결과를 재현할 수 있도록 메서드를 설치 가능한 플러그인으로 제출하세요
4. 토착어 메서드의 경우: 메서드가 최상위에 도달하면 [소유권 이전](/docs/sovereignty/ownership-transfer) 절차가 시작돼요

---

## 함께 보기

- [하니스 사용법](/docs/specifications/harness) — 전체 CLI 레퍼런스
- [리더보드 규칙](/docs/leaderboard/rules) — 제출 기준 및 부정 행위 방지 정책
- [메서드 구축하기](/docs/specifications/methods) — TranslationMethod 프로토콜
- [데이터셋](/docs/leaderboard/datasets) — 사용 가능한 평가 데이터셋