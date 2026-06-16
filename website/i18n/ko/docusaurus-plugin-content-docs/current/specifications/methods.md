---
sidebar_position: 4
title: "메서드 인터페이스"
related:
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
    note: "Put this interface on the leaderboard"
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
    note: "A full method, built end-to-end"
---
# 공유 메서드 인터페이스

> **요약.** 이 페이지는 모든 Arena 메서드가 구현해야 하는 `TranslationMethod` 프로토콜, 여섯 가지 메서드 클래스(`raw-llm`, `coached-llm`, `pipeline`, `custom-plugin`, `api`, `human`), 메서드 플러그인 형식, 그리고 메서드가 평가 샌드박스에서 실행되어 상을 받을 자격이 있는지를 결정하는 **의존성 클래스**(S/O/A1/A2/X)를 명세해요. 이 프로토콜을 구현하는 어떤 접근 방식이든 벤치마킹할 수 있어요. 무엇에 의존하느냐가 어디에서 경쟁할 수 있는지를 결정해요.

eval harness와 champollion은 **번역 메서드**라는 공통 개념을 공유해요. 메서드란 소스 텍스트를 받아 번역된 텍스트를 생성하는 모든 절차예요 — 직접적인 LLM 호출이든, 다단계 파이프라인이든, 서드파티 API든, 인간 번역가든 상관없어요.

## 아키텍처

```
Method Plugin (v2 Spec)
├── method.json           ← Manifest (name, class, entry_point, dependencies, metadata)
├── method_card.json      ← Leaderboard description (what, not how)
├── pipeline.py           ← Python module implementing TranslationMethod
└── (optional helpers)    ← Additional Python modules
```

`--method path/to/dir`을 통해 로드돼요. harness는 아무것도 자동으로 발견하지 않아요.

## 두 개의 시스템, 하나의 인터페이스

| | Eval Harness | champollion |
|---|---|---|
| **언어** | Python | Node.js |
| **진입점** | `translate.py` | `translate.js` |
| **인터페이스** | `TranslationMethod` 프로토콜 | `methodPlugin` 설정 |
| **목적** | 점수 평가가 포함된 배치 평가 | dev/CI에서의 실시간 현지화 |
| **출력** | 메트릭이 포함된 run card | 번역된 로케일 파일 |

두 시스템을 모두 지원하는 메서드는 두 개의 진입점을 제공해요 — 각 언어 런타임마다 하나씩이에요. **method card**가 그 다리 역할을 해요. 이는 두 시스템 모두 이해할 수 있는 형식으로 메서드를 설명해요.

## Method Card {#method-card}

method card는 전체 시스템 프롬프트 같은 독점적인 세부 사항을 드러내지 않으면서 번역 메서드가 *무엇*인지를 설명해요. 다음 질문에 답해요:

- 이것은 어떤 클래스의 메서드인가요? (raw LLM, coached LLM, pipeline, API 등)
- 어떤 도구를 사용하나요? (FST analyzer, dictionary 등)
- 구현이 오픈소스인가요?
- 어떤 언어 쌍을 지원하나요?

전체 JSON 스키마는 [Method Card Spec](/docs/specifications/methods#method-card)을 참조하세요.

### 예시

```json
{
  "method_id": "fst-gated-v8",
  "name": "FST-Gated Coached Translation v8",
  "class": "pipeline",
  "description": "LLM translation with morphological validation. Failed words are retried with FST feedback.",
  "author": "Curtis Forbes",
  "tools_used": ["HFST morphological analyzer", "Wolvengrey dictionary"],
  "open_source": false,
  "dependency_class": "A2",
  "supported_pairs": ["eng>crk"]
}
```

`dependency_class` 필드는 메서드가 실행되고 이전되기 위해 필요한 것을 요약해요 — 아래 [메서드 유효성 및 의존성 클래스](#method-validity-and-dependency-classes)를 참조하세요.

### 메서드 클래스

| 클래스 | 설명 |
|-------|-------------|
| `raw-llm` | 최소한의 지시만 있는 직접적인 LLM 호출 |
| `coached-llm` | 구조화된 프롬프트, 예시, 제약 조건이 있는 LLM |
| `pipeline` | 결정론적 구성 요소가 있는 다단계 파이프라인 |
| `custom-plugin` | `TranslationMethod` 프로토콜을 구현하는 외부 프로세스 |
| `api` | 서드파티 번역 API (Google Translate, DeepL 등) |
| `human` | 인간 번역 (baseline 수립용) |

## 메서드 유효성 및 의존성 클래스 {#method-validity-and-dependency-classes}

메서드는 가장 가용성이 낮은 의존성만큼만 실행 가능하고, 그만큼만 이전 가능해요. 두 가지 Arena 메커니즘이 메서드가 정확히 무엇을 필요로 하는지를 아는 데 의존해요:

1. **샌드박스 평가** ([Benchmark Specification §8.2](/docs/specifications/benchmark)) — 공식 gold-standard 점수는 네트워크 정책이 **default-deny**인 샌드박스에서 나와요. 외부 서비스를 암묵적으로 요구하는 메서드는 공식 점수를 생성할 수 없어요.
2. **상 이전** ([Prize Specification](/docs/specifications/prizes)) — 상을 수상한 메서드는 해당 언어 커뮤니티의 거버넌스 조직으로 이전돼요. 제출자가 포함할 권리가 없는 콘텐츠를 번들로 묶은 메서드는 합법적으로 이전될 수 없어요. 제출자는 박스 안의 모든 것에 대한 권리를 보유하거나 부여받아야 해요.

두 검사 모두 임시방편이 아닌 기계적으로 이뤄지도록, 모든 메서드는 `method.json`의 **의존성 매니페스트**에서 도출된 **의존성 클래스**를 선언해요.

> **명명에 관한 참고.** *메서드 클래스*(위 §: `raw-llm`, `pipeline`, …)는 *메서드가 어떻게 번역하는지*를 설명해요. *의존성 클래스*(이 섹션)는 *메서드가 실행되고 이전되기 위해 무엇이 필요한지*를 설명해요. 이 둘은 독립적인 축이에요. `pipeline` 메서드는 어떤 의존성 클래스든 될 수 있어요.

### 다섯 가지 의존성 클래스

| 클래스 | 이름 | 정의 | 샌드박스 실행 가능? | 상 자격 있음? |
|-------|------|-----------|-------------------|-----------------|
| **S** | Self-contained | 모든 코드, 데이터, 모델, 가중치가 재배포 및 커뮤니티 이전을 허용하는 라이선스 하에 메서드 디렉터리 안에 포함되어 있어요. | ✅ 예, 있는 그대로 | ✅ 예 |
| **O** | Open external | 재배포를 허용하는 오픈 라이선스(AGPL 같은 copyleft 라이선스 포함) 하에 외부에 호스팅된 아티팩트에 의존해요 — 예: 설치 시 다운로드되는 FST. | ✅ 예 — 아티팩트는 고정되어 **제출물에 미러링**돼요 | ✅ 예, 라이선스 호환성 조건과 함께: copyleft 조건이 이전을 통해 보존되고, 커뮤니티는 라이선스가 모두에게 부여하는 것과 동일한 권리를 받아요 |
| **A1** | API-dependent, substitutable | 런타임 LLM 추론을 요구하며, 여기서 모델은 **대체 가능한 설정**이에요 — 충분히 유능한 어떤 모델이든 끼워넣을 수 있어요. 메서드의 가치는 프롬프트, coaching 데이터, 코드에 있으며, 특정 제공자의 모델에 있지 않아요. | ⚠️ 샌드박스 명세가 정의하는 **LLM gateway**를 통해서만 (🔲 계획됨 — 아래 참조) | ⚠️ 조건부 — 아래 참조 |
| **A2** | API-dependent, non-substitutable | 미러링하거나 대체할 수 없는 외부 데이터 또는 서비스 API에 대한 런타임 호출을 요구해요 — 일반적으로 제공되는 콘텐츠가 독점적이거나 라이선스가 없기 때문이에요 (예: 기반 사전에 공개 라이선스가 없는 dictionary API). | ❌ 아니요 — 권리 보유자의 허가 없이는 샌드박스에 의존성이 존재할 수 없어요 | ❌ 권리 보유자가 샌드박스 포함 **및** 이전 권한을 부여하기 전까지는 불가해요. 눈에 보이는 **"external dependency"** 플래그와 함께 오픈(개발 세그먼트) 리더보드에서는 허용돼요 |
| **X** | Closed | 제출자가 재배포할 권리가 없는 콘텐츠를 번들로 묶어요 — 라이선스 없는 데이터셋, 스크래핑된 독점 콘텐츠, 라이선스 비호환 구성 요소. | ❌ | ❌ 모든 레인에서 부적격이에요. 권리 없이 콘텐츠를 번들로 묶는 것은 메서드가 어디서 실행되든 라이선스 위반이에요 |

**유효 클래스(Effective class).** 메서드의 의존성 클래스는 선언된 모든 의존성 중에서 *가장 제한적인* 클래스이며, S < O < A1 < A2 < X 순서를 따라요. 라이선스 없는 사전 하나가 그 외엔 self-contained인 파이프라인을 Class A2(런타임에 접근하는 경우) 또는 Class X(권리 없이 번들로 묶은 경우)로 만들어요.

### A1/A2 구분: 대체 가능성

대부분의 메서드는 LLM을 호출해요. Arena는 그렇지 않은 척하지 않아요 — 그러나 매우 다른 두 종류의 API 의존성을 구분해요:

- **A1 (대체 가능):** API는 범용 LLM 추론을 제공해요. 모델 식별자는 설정이에요: 메서드는 커뮤니티가 호스팅하는 open-weight 모델을 포함해 호환되는 어떤 추론 엔드포인트에 대해서도 처음부터 끝까지 실행되어야 해요. 출력 품질은 모델에 따라 다를 수 있어요 — 그것은 개발자의 위험이며, 공식 점수는 평가에 사용된 고정 모델에 연결돼요. **제공자 측 상태**(제공자에서만 호스팅되는 fine-tune, 제공자 파일 저장소, 제공자 전용 어시스턴트)에 의존하는 메서드는 대체 가능하지 *않아요*: 그 상태는 끼워넣고 빼낼 수 없으므로, 기반 가중치나 데이터가 제출물에 포함되지 않는 한 의존성은 A2예요.
- **A2 (대체 불가):** API는 고유한 무언가를 제공해요 — 일반적으로 독점적이거나 라이선스 없는 데이터예요. 대체 엔드포인트가 그것을 제공할 수 없으며, 권리 보유자의 허가 없이는 콘텐츠를 샌드박스에 미러링할 수 없어요. 메서드는 오픈 리더보드에서 (플래그가 붙은 채로) 작동하지만, 권한이 존재하기 전까지는 공식 샌드박스 점수를 생성하거나 상 자격을 얻을 수 없어요.

**A1 상 이전이 실제로 전달하는 것.** 커뮤니티는 모델을 받지 않아요 — 누구도 Anthropic, Google, OpenAI의 가중치를 이전할 수 없어요. 이전은 모델 *주변*의 완전한 레시피를 포함해요: 모든 프롬프트, coaching 데이터, 파이프라인 코드, 재시도 로직, 설정, 그리고 문서화된 모델 요구 사항이에요. 모델은 구조적으로 대체 가능하기 때문에, 커뮤니티는 이전된 메서드를 자신들이 선택한 어떤 제공자에게든 — 또는 자체 하드웨어의 open-weight 모델에게든 — 개발자의 개입 없이 연결할 수 있어요. 레시피는 소유되고, 엔진은 빌린 것이며 교체 가능해요.

### 의존성 매니페스트 (`method.json`)

모든 메서드는 `method.json` 매니페스트에서 자신의 의존성을 선언해요. 각 항목은 아티팩트가 무엇인지, 어디에서 오는지, 어떤 라이선스가 적용되는지, 그리고 메서드가 어떻게 접근하는지를 기록해요:

```json
{
  "name": "FST-Gated Coached Translation v8",
  "method_id": "fst-gated-v8",
  "class": "pipeline",
  "entry_point": "pipeline:PipelineMethod",
  "supported_pairs": ["eng>crk"],
  "dependency_class": "A2",
  "dependencies": [
    {
      "id": "giellalt-lang-crk-fst",
      "kind": "software",
      "license": "AGPL-3.0-or-later",
      "access": "mirrored",
      "source": "https://github.com/giellalt/lang-crk",
      "pin": "sha256:3f1a…",
      "redistributable": true,
      "transferable": true
    },
    {
      "id": "llm-inference",
      "kind": "model",
      "license": "proprietary",
      "access": "gateway",
      "source": "openrouter:google/gemini-2.5-flash",
      "substitutable": true,
      "redistributable": false,
      "transferable": false,
      "notes": "Any compatible chat-completions endpoint works; the model slug is configuration."
    },
    {
      "id": "crk-dictionary-api",
      "kind": "service",
      "license": "none",
      "access": "external-api",
      "source": "https://itwewina.altlab.app/",
      "redistributable": false,
      "transferable": false,
      "notes": "Dictionary content has no public license; runtime lookups only. Class A2 until the rights holders grant permission."
    }
  ]
}
```

| 필드 | 필수 | 설명 |
|-------|----------|-------------|
| `id` | ✅ | 의존성에 대한 안정적인 식별자 |
| `kind` | ✅ | `data`, `model`, `software`, 또는 `service` |
| `license` | ✅ | SPDX 식별자, `proprietary`, 또는 `none`. `none`은 공개 라이선스가 존재하지 않음을 의미해요 — all-rights-reserved로 취급돼요 |
| `access` | ✅ | `bundled` (메서드 디렉터리에 포함), `mirrored` (설치 시 가져와 고정되고 제출물에 벤더링됨), `gateway` (평가 gateway를 통한 런타임 LLM 추론), `external-api` (기타 모든 런타임 네트워크 호출) |
| `source` | ✅ | 정규 URL 또는 `provider:slug` 식별자 |
| `pin` | `mirrored`의 경우 | 정확한 아티팩트를 고정하는 버전, 커밋, 또는 콘텐츠 해시 |
| `substitutable` | `gateway`/`external-api`의 경우 | 호환되는 어떤 엔드포인트든 이 의존성을 제공할 수 있는지 여부 |
| `redistributable` | ✅ | 라이선스가 아티팩트의 재배포를 허용하는지 여부 |
| `transferable` | ✅ | 아티팩트(또는 그에 대한 권리)가 상 이전 조건 하에 커뮤니티로 전달될 수 있는지 여부 |
| `notes` | ❌ | 자유 형식 컨텍스트 |

**클래스 도출.** 각 의존성은 하나의 클래스에 기여해요. 메서드의 `dependency_class`는 가장 제한적인 것이에요:

| 의존성 프로파일 | 기여 |
|--------------------|-------------|
| `bundled` + 라이선스가 재배포와 이전을 허용 | S |
| `mirrored` + 재배포를 허용하는 오픈 라이선스 (copyleft 포함) | O |
| `gateway` + `substitutable: true` (LLM 추론) | A1 |
| `external-api`, 또는 `substitutable: false`가 있는 `gateway` | A2 |
| `bundled` + `license: none` 또는 재배포 비호환 라이선스 | X |

선언된 `dependency_class`는 harness가 매니페스트에서 도출하는 클래스와 일치해야 해요. 불일치는 검증 오류예요.

외부 의존성이 **없는** 메서드는 `"dependency_class": "S"`과 `"dependencies": []`를 선언해요. 빈 배열은 적극적인 진술이며, 다른 것과 마찬가지로 감사돼요.

### 유효성 검증 방법

세 가지 계층으로, 가장 저렴한 것부터 가장 권위 있는 것까지예요:

1. **매니페스트 감사.** harness는 매니페스트에서 유효 클래스를 도출하고 불일치를 거부해요. 검토자는 선언된 각 의존성을 명시된 라이선스와 소스에 대조해 확인해요 — 상위 라이선스가 다르게 명시하는데 `redistributable: true`로 선언된 의존성은 검토에서 탈락해요.
2. **정적 분석.** 제출된 코드는 매니페스트가 설명하지 않는 네트워크 호출, 동적 다운로드, 파일시스템 접근에 대해 스캔돼요. 검토에서 발견된 *미선언* 의존성은 그것이 어떤 클래스였을지와 무관하게 거부 사유가 돼요 — 매니페스트는 정확할 뿐만 아니라 완전해야 해요.
3. **샌드박스 네트워크 정책.** 샌드박스 명세는 **default-deny egress**를 요구해요: 메서드 컨테이너는 경로가 명시적으로 allowlist에 등록되지 않는 한 네트워크 접근이 없어요. 명세가 정의하는 유일한 egress 경로는 **LLM gateway**예요 — 평가 인프라가 운영하는 추론 프록시로, 고정 모델의 명시적 allowlist로 제한되며, 실행 후 감사를 위해 모든 요청과 응답이 로깅돼요. allowlist에 없는 것은 정책 계층이 아닌 네트워크 계층에서 실패해요. 네트워크 정책과 gateway 설계는 [Benchmark Specification §8.6](/docs/specifications/benchmark)을 참조하세요.

> 🔲 **계획됨.** 샌드박스와 그 LLM gateway는 명세되어 있지만 아직 구축되지 않았어요. gateway가 운영되기 전까지는 Class S와 Class O 메서드만 샌드박스에서 평가될 수 있어요. Class A1 메서드는 *원칙적으로는* 상 자격이 있지만 아직 공식 gold-standard 점수를 생성할 수 없어요. 이 페이지는 명세가 요구하는 것을 설명하며, 현재 실행되는 것을 설명하지 않아요.

### 리더보드 표시

- 리더보드는 각 메서드의 의존성 클래스를 메서드 클래스 배지와 함께 표시해요.
- 오픈 리더보드의 Class A2 메서드는 눈에 보이는 **"external dependency"** 플래그를 달아요: 그 점수는 변경되거나 사라질 수 있는 서드파티 서비스에 의존하며, 현재 상 자격이 없어요.
- Class X 메서드는 목록에 표시되지 않아요.

## Eval Harness: TranslationMethod 프로토콜 {#eval-harness-translationmethod-protocol}

eval harness는 플러그인에 Python의 구조적 타이핑(`Protocol`)을 사용해요. 올바른 메서드 시그니처를 가진 어떤 클래스든 작동해요 — 상속이 필요 없어요:

```python
class MyMethod:
    async def translate(self, entries: list[dict], config: RunConfig) -> list[dict]:
        results = []
        for entry in entries:
            translation = await self.do_translation(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translation,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "error": None,
                "tool_calls": [],
                "tool_call_count": 0,
                "metadata": {},
            })
        return results
```

비-Python 메서드를 위한 wrapper 예시를 포함한 전체 문서는 [Plugin Protocol](/docs/specifications/methods#eval-harness-translationmethod-protocol)을 참조하세요.

## champollion: methodPlugin 설정

champollion에서 메서드는 `champollion.config.json`에 언어 쌍별로 등록돼요:

```json
{
  "version": 3,
  "pairs": {
    "en:crk": {
      "methodPlugin": "crk-coached-v1"
    }
  }
}
```

champollion 측 인터페이스는 [Plugin Spec](https://champollion.dev/docs/reference/plugin-spec)을 참조하세요.

## 리더보드 통합

method card가 (`--method-card`을 통해) 실행에 첨부되면, run card에 임베딩되어 리더보드에 표시돼요:

```bash
# Run with method card attached
mt-eval run \
  --method path/to/my-method \
  --corpus data/edtekla-dev-v1.json \
  --method-card method_card.json

# Publish to the leaderboard
mt-eval publish eval/logs/harness/your-run-card.json
```

`--method-card`가 제공되지 않으면, `mt-eval publish`가 메서드를 설명하는 과정을 안내하는 대화형 마법사를 실행해요.

리더보드는 다음을 표시해요:
- **클래스 배지** — 시각적 표시 (예: "pipeline", "coached-llm")
- **의존성 클래스** — S/O/A1/A2 ([메서드 유효성 및 의존성 클래스](#method-validity-and-dependency-classes) 참조); A2 메서드는 "external dependency" 플래그를 달아요
- **메서드 이름** — method card에서 가져옴
- **사용된 도구** — method card에서 나열됨
- **오픈소스 표시**

method card가 첨부되지 않으면, 리더보드는 harness 네이티브 설정(모델, 프롬프트 버전, temperature, 활성화된 도구)을 표시해요.

:::danger 평가 데이터로 학습하지 마세요
개발 과정에서 평가 데이터셋에 노출된 메서드 — 학습 데이터, few-shot 예시, dictionary 항목, 또는 프롬프트 튜닝 자료로서 — 는 리더보드에서 **실격**돼요. 좋은 메서드와 나쁜 메서드를 구별하는 기준은 [MT Evaluation](/docs/leaderboard/rules)을 참조하세요.
:::

---

## 함께 보기

- [MT Evaluation](/docs/leaderboard/rules) — 개요, 리더보드 가치, 좋은/나쁜 메서드 가이드
- [Eval Harness](/docs/specifications/harness) — 평가 실행 방법
- [Evaluation Datasets](/docs/leaderboard/datasets) — 사용 가능한 데이터셋 (EDTeKLA, FLORES+)
- [Run Card Specification](/docs/specifications/run-card) — run card JSON 스키마
- [Plugin Spec](https://champollion.dev/docs/reference/plugin-spec) — champollion 측 플러그인 인터페이스
- [Method Leaderboard](https://champollion.dev/leaderboard) — 실시간 벤치마크 점수
- [Benchmark Specification](/docs/specifications/benchmark) — 평가 프로토콜, 코퍼스 형식, run card 스키마
- [Scoring Specification](/docs/specifications/scoring) — 메트릭, composite 가중치, 품질 등급의 SSOT