---
id: how-this-site-is-translated
title: "이 사이트가 번역되는 방식"
description: "이 사이트의 모든 로케일은 Champollion이 직접 기계 번역하며, 해당 언어 쌍에 대해 자체 공개 벤치마크에서 우승한 방법을 사용해요."
---
# 이 사이트가 번역되는 방식

이 사이트는 13개 언어로 제공돼요. 영어를 제외한 모든 로케일은 이 아레나와 함께
만들어진 번역 CLI인 **Champollion이 기계 번역**하며, 각 언어의 번역 모델은
**기본값이 아니라 이 사이트 자체의 벤치마크로** 선정됐어요. 각 언어 쌍은
공개 개발 코퍼스에서 MT eval harness로 평가됐고, composite score가 가장 높은
방법/모델(통계적으로 동률인 경우 비용으로 결정)이 해당 로케일을 번역해요.

이는 독자로서 알아두셔야 할 두 가지를 의미해요:

1. **이 페이지들은 기계 번역물이에요.** 아래에 설명된 어조 및 용어 지침에
   따라 생성되지만, 모든 문장을 사람이 검토하지는 않았어요. 잘못 읽히는
   부분이 있다면 영어 버전이 정본이며, 수정 제안을 환영해요.
2. **선택을 검증할 수 있어요.** 아래 각 행에는 해당 언어의 모델을 선정한
   벤치마크 실행이 명시돼 있고, 실행 결과는
   [MT Eval Arena 리더보드](https://mtevalarena.org/leaderboard)에 공개돼 있어요.

## 로케일별 출처

| 로케일 | 언어 | 방법 | 모델 | 벤치마크 코퍼스 | Composite score (95% CI) | 벤치마크 날짜 | 마지막 동기화 |
|--------|----------|--------|-------|------------------|--------------------------|----------------|-------------|
| fr | Français | llm | `anthropic/claude-haiku-4.5` | `eng-fra-dev-v1` (Tatoeba, CC-BY-2.0) | 0.581 [0.542, 0.617] | 2026-06-11 | 2026-06-12 |
| de | Deutsch | llm | `anthropic/claude-opus-4.8` | `eng-deu-dev-v1` (Tatoeba, CC-BY-2.0) | 0.590 [0.550, 0.633] | 2026-06-11 | 2026-06-12 |
| nl | Nederlands | llm | `anthropic/claude-sonnet-4.6` | `eng-nld-dev-v1` (Tatoeba, CC-BY-2.0) | 0.600 [0.558, 0.642] | 2026-06-11 | 2026-06-12 |
| fil | Filipino | llm | `openai/gpt-5.5` | `eng-tgl-dev-v1` (Tatoeba, CC-BY-2.0)¹ | 0.499 [0.471, 0.529] | 2026-06-11 | 2026-06-12 |
| es | Español | llm | `anthropic/claude-haiku-4.5` | `eng-spa-dev-v1` (Tatoeba, CC-BY-2.0) | 0.553 [0.523, 0.584] | 2026-06-11 | 2026-06-12 |
| zh | 简体中文 | llm | `anthropic/claude-haiku-4.5` | `eng-cmn-dev-v1` (Tatoeba, CC-BY-2.0) | 0.240 [0.207, 0.278] | 2026-06-11 | 2026-06-12 |
| ja | 日本語 | llm | `anthropic/claude-sonnet-4.6` | `eng-jpn-dev-v1` (Tatoeba, CC-BY-2.0) | 0.278 [0.252, 0.304] | 2026-06-11 | 2026-06-12 |
| ko | 한국어 | llm | `anthropic/claude-opus-4.8` | `eng-kor-dev-v1` (Tatoeba, CC-BY-2.0) | 0.286 [0.256, 0.318] | 2026-06-11 | 2026-06-12 |
| pt | Português | llm | `anthropic/claude-haiku-4.5` | `eng-por-dev-v1` (Tatoeba, CC-BY-2.0) | 0.609 [0.576, 0.646] | 2026-06-11 | 2026-06-12 |
| th | ไทย | llm | `anthropic/claude-sonnet-4.6` | `eng-tha-dev-v1` (Tatoeba, CC-BY-2.0) | 0.468 [0.426, 0.510] | 2026-06-11 | 2026-06-12 |
| vi | Tiếng Việt | llm | `google/gemini-3.5-flash` | `eng-vie-dev-v1` (Tatoeba, CC-BY-2.0) | 0.463 [0.433, 0.494] | 2026-06-11 | 2026-06-12 |
| ar | العربية | llm | `anthropic/claude-fable-5` | `eng-arb-dev-v1` (Tatoeba, CC-BY-2.0)² | 0.437 [0.403, 0.478] | 2026-06-11 | 2026-06-12 |

¹ Filipino은 Tagalog 데이터로 벤치마크돼요. Tagalog은 `fil` 로케일에
대해 Tatoeba에서 이용 가능한 가장 가까운 코퍼스예요.
² Arabic 코퍼스는 이 사이트의 MSA 어조와 일치하는 Modern Standard Arabic
(ISO 639-3 `arb`)이에요.

선정 규칙: 각 쌍에 대해 벤치마크 라인업의 모든 모델
(`google/gemini-3.5-flash`, `anthropic/claude-haiku-4.5`,
`anthropic/claude-fable-5`, `anthropic/claude-opus-4.8`,
`anthropic/claude-sonnet-4.6`, `openai/gpt-5.5`,
`google/gemini-3.1-pro-preview`)이 해당 쌍의 개발 코퍼스에서 점수가 매겨졌어요.
승자는 composite score가 가장 높은 모델이며, 더 저렴한 모델이 최고
점수 모델과 통계적으로 구별되지 않는 경우(paired bootstrap resampling,
p ≥ 0.05) 더 저렴한 모델이 선택돼요.

*Composite score*는 MT Eval Arena의 혼합 품질 지표예요(chrF++, exact match,
로드된 metric 플러그인, bootstrap-CI로 검증됨). 점수는 쌍을 넘나들며 비교할 수
없고 **하나의 언어 쌍 내에서만** 비교 가능해요. Korean의 0.28이 0.58인 French
페이지보다 Korean 페이지가 더 나쁘다는 의미는 아니에요. 코퍼스와 스크립트가
다르기 때문이에요.

## 어조 및 톤

각 언어는 Champollion의 언어 카드에서 선택한 명시적 어조로 번역되므로,
사이트 전반에서 격식 수준이 일관돼요:

- **Français** — vouvoiement (격식체 *vous*)
- **Deutsch** — Sie-Form
- **Nederlands** — u-vorm
- **Filipino** — 표준 기술 용어를 사용한 격식체
- **Español** — 중립적 라틴 아메리카 스페인어
- **简体中文** — 전문 기술 어조
- **日本語** — です/ます (정중체)
- **한국어** — 해요체 (정중체)
- **Português** — 전문 어조
- **ไทย** — 중립적 전문 어조
- **Tiếng Việt** — 중립적 *bạn*-형
- **العربية** — Modern Standard Arabic, 전문 어조

## 기계 번역되지 않는 항목

코드 블록, CLI 명령어, 설정 키, 패키지 이름, URL, 고유 명사는 번역 중에
보호되며 설계상 영어로 유지돼요.

## 오역을 발견하셨나요?

이슈나 PR을 열어주세요. 모든 번역 페이지의 소스는 영어 원본이에요. 번역
페이지에 대한 수정 사항은 해당 페이지의 영어 소스가 변경되지 않는 한 향후
동기화에서도 유지돼요(동기화는 영어 소스가 변경될 때만 페이지를 다시
번역해요).

*이 페이지 자체도 위 표에 있는 방법으로 기계 번역됐어요. 즉, 자신의 번역
과정을 스스로 설명하고 있는 셈이에요.*