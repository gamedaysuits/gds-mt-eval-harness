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

> **ملخص تنفيذي.** تغطي هذه الصفحة تثبيت أداة تقييم الترجمة الآلية وإعدادها واستخدامها — وهي الأداة التي تقيس أداء أساليب الترجمة مقارنةً بمدونات نصية موحدة وتُنتج بطاقات تشغيل مُقيَّمة. للاطلاع على التعريفات المعتمدة للمقاييس والمخططات وبروتوكول التقييم، راجع [Benchmark Specification](/docs/specifications/benchmark).

تقوم الأداة بتشغيل تجارب الترجمة وتُنتج بطاقات التشغيل. وهي تتولى بناء الموجّهات (prompts) واستدعاءات واجهة برمجة التطبيقات (API) والتقييم وتسلسل النتائج — وأنت تقدّم مجموعة البيانات والنموذج.

## التثبيت

**المتطلبات:** Python 3.10+

```bash
pip install sacrebleu aiohttp
```

استنسخ مستودع الأداة:

```bash
git clone https://github.com/gamedaysuits/arena.git
cd arena
```

## الاستخدام

```bash
mt-eval run --corpus path/to/dataset.json
```

يقوم هذا الأمر بتمرير كل مدخل في المدونة النصية عبر النموذج المُعدّ (أو الإضافة البرمجية للأسلوب)، ثم يقيّم المخرجات ويكتب ملف JSON لبطاقة التشغيل في مجلد الإخراج.

## خيارات سطر الأوامر (CLI Flags)

### `mt-eval run`

| الخيار | مطلوب | القيمة الافتراضية | الوصف |
|------|----------|---------|-------------|
| `--corpus` | ✅ | — | مسار ملف المدونة النصية (`.json`، `.jsonl`، `.tsv`) |
| `--source-file` / `--reference-file` | — | — | ملفات نصوص متوازية (بتنسيق FLORES+ وWMT) |
| `-m, --model` | — | `gemini-pro` | معرّف النموذج (اسم مختصر أو معرّف OpenRouter كامل). يُحلّ عبر `shared/model-aliases.json`. مفصول بفواصل لتشغيل نماذج متعددة |
| `-d, --dataset` | — | `all` | مرشّح مجموعة البيانات: `all`، أو اسم المقطع، أو نطاق معرّفات |
| `--ids` | — | — | معرّفات المدخلات المراد تقييمها مفصولة بفواصل |
| `--source-lang` | — | `English` | اسم اللغة المصدر |
| `--target-lang` | — | — | اسم اللغة الهدف |
| `-p, --prompt` | — | `naive` | إصدار الموجّه (`naive`، `custom`، `champollion`) |
| `--coaching-file` | — | — | مسار ملف نصي لموجّه التدريب |
| `--coaching` | — | — | نص تدريب مضمّن (سلسلة نصية بين علامتي اقتباس) |
| `--method` | — | — | مسار مجلد الإضافة البرمجية للأسلوب (يحتوي على `method.json` + وحدة Python) |
| `--method-card` | — | — | مسار ملف JSON لبطاقة الأسلوب الخاصة ببيانات لوحة المتصدرين الوصفية |
| `--fst-retries` | — | `0` | عدد محاولات إعادة FST (للأسلوب الافتراضي LLM فقط) |
| `--skip-fst` | — | `false` | تخطّي بوابة جودة FST بالكامل |
| `--tools` | — | `false` | تفعيل وضع استدعاء الأدوات |
| `--tools-list` | — | — | أسماء الأدوات مفصولة بفواصل |
| `--max-tool-rounds` | — | `8` | الحد الأقصى لجولات استدعاء الأدوات لكل مدخل |
| `--hooks` | — | — | أسماء خطّافات ما بعد الترجمة |
| `--style-profile` | — | — | مسار ملف JSON لملف الأسلوب التعريفي. يفعّل مقاييس اتساق أسلوب الكتابة (إعلامية — لا تدخل أبدًا في composite score؛ راجع [§ مقاييس أسلوب الكتابة والسجل اللغوي](#writing-style-and-register-metrics-informational)) |
| `-b, --batch-size` | — | `25` | عدد المدخلات لكل استدعاء API |
| `-c, --concurrency` | — | `8` | استدعاءات API المتوازية |
| `--max-tokens` | — | `32768` | الحد الأقصى للرموز (tokens) لكل استدعاء API |
| `--temperature` | — | `0.0` | درجة حرارة أخذ العينات (0.0 = حتمي) |
| `--no-cache` | — | `false` | تعطيل التخزين المؤقت للاستجابات |
| `--cache-dir` | — | `eval/cache/harness` | مسار مجلد التخزين المؤقت |
| `-o, --output-dir` | — | `eval/logs/harness` | مجلد الإخراج لبطاقات التشغيل والسجلات |
| `-n, --name` | — | — | اسم التشغيل بصيغة مقروءة |
| `--dry-run` | — | `false` | التحقق من صحة الإعدادات دون إجراء استدعاءات API |
| `--champollion-config` | — | — | مسار `champollion.config.json` |
| `--champollion-cards-dir` | — | — | مجلد بطاقات اللغات |
| `--target-lang-code` | — | — | رمز اللغة وفق BCP-47 |

### أوامر فرعية أخرى

| الأمر الفرعي | الوصف |
|------------|-------------|
| `mt-eval test <log_path>` | تحليل سجل تشغيل مكتمل |
| `mt-eval publish <report_path>` | إرسال بطاقة تشغيل إلى لوحة المتصدرين |
| `mt-eval compare <logs...>` | مقارنة عدة عمليات تشغيل جنبًا إلى جنب |
| `mt-eval dashboard <logs...>` | إنشاء لوحة معلومات HTML من سجلات التشغيل |
| `mt-eval list models\|prompts\|datasets` | عرض الموارد المتاحة |
| `mt-eval export` | تجميع الإعداد الحالي كإضافة برمجية لأسلوب champollion |
| `mt-eval export-config` | تصدير MethodConfig المُحلّل (جميع الحقول القياسية الثمانية) بصيغة JSON |

### أمثلة

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

## مخطط بطاقة التشغيل

تُنتج كل تجربة **بطاقة تشغيل** — وهي مستند JSON مكتفٍ ذاتيًا. البنية على المستوى الأعلى:

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

راجع [Run Card Specification](/docs/specifications/run-card) للاطلاع على المخطط الكامل مع توثيق كل حقل.

:::info المخطط المعتمد
يُعد [Benchmark Specification](/docs/specifications/benchmark) المصدر الوحيد للحقيقة بالنسبة لمخطط بطاقة التشغيل. للاطلاع على تعريفات المقاييس وأوزان composite ومستويات الجودة، راجع [Scoring Specification](/docs/specifications/scoring). توثّق هذه الصفحة كيفية استخدام الأداة؛ بينما تحدد المواصفات معنى المخرجات.
:::

### الكتل الرئيسية

**`dataset`** — تحدد مجموعة البيانات المستخدمة، بما في ذلك تجزئة محتواها (content hash) بحيث تُربط النتائج بإصدار محدد:

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

**`scores`** — المقاييس الإجمالية للتشغيل:

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

**`totals`** — تتبع استخدام الرموز والتكلفة:

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

## مقاييس أسلوب الكتابة والسجل اللغوي (إعلامية)

يمكن للأداة تقييم مدى مطابقة الترجمات لـ**سجل لغوي** و**أسلوب كتابة** مستهدفين، عبر الإضافة البرمجية للمقياس `WritingStyleConsistency` (`mt_eval_harness/plugins/writing_style.py`). قد تكون الترجمة صحيحة لغويًا لكن بسجل لغوي خاطئ — صياغة غير رسمية في مستند قانوني، أو عبارات رسمية جاهزة في نص تسويقي — والمقاييس النصية لن تلاحظ ذلك. هذه المقاييس تلاحظه.

**ما يُقاس (لكل مدخل):**

| المقياس | النطاق | المعنى |
|--------|-------|---------|
| `style_register_match` | قيمة منطقية (boolean) | هل يطابق الإخراج السجل اللغوي المتوقع؟ يأتي الهدف من حقل `register` في مدخل المدونة النصية (راجع [Benchmark Spec §2.6](/docs/specifications/benchmark)) أو من ملف أسلوب تعريفي |
| `style_sentence_length_ratio` | عدد عشري (float) | متوسط طول الجملة المتنبأ به مقابل المرجعي (1.0 = تطابق؛ التباعد = انحراف أسلوبي) |
| `style_formality_score` | 0.0–1.0 | وجود علامات الرسمية/اللارسمية (ضمائر T–V، الاختصارات، …) باستخدام موارد العلامات الخاصة بكل لغة |

**الإجمالي:** `style_consistency_rate` — نسبة المدخلات التي لم يُكتشف فيها عدم تطابق في السجل اللغوي.

فعّل هدفًا مخصصًا باستخدام `--style-profile path/to/profile.json` (مثل ملف تعريفي لصوت العلامة التجارية)؛ وبدونه، تعود الإضافة البرمجية إلى البيانات الوصفية `register` لكل مدخل في المدونة النصية حيثما وُجدت.

:::caution نطاق صريح
هذه المقاييس **إعلامية فقط** — فهي لا تدخل أبدًا في composite score، كما أن كشف الرسمية يعتمد على العلامات (وهو أسلوب استدلالي)، وليس حكمًا قائمًا على التعلّم. تعامل معها ككاشف انحراف في الالتزام بالسجل اللغوي، وليس كحكم على جودة الأسلوب.
:::

---

## الفرق بين Fingerprint وRun Card Hash

تُنتج الأداة تجزئتين مختلفتين، ولكل منهما غرض مختلف:

### Fingerprint

تجيب **البصمة (fingerprint)** عن السؤال: *"هل يمكن إعادة إنتاج هذا التشغيل؟"*

فهي تجزّئ مجموعة المدخلات التي تحدد إعدادات التجربة — وليس المخرجات:

- SHA-256 الخاص بمجموعة البيانات
- معرّف النموذج
- تسمية الحالة (condition)
- SHA-256 الخاص بموجّه النظام
- درجة الحرارة (temperature)
- إصدار الأداة

أي تشغيلين بنفس البصمة استخدما الإعداد نفسه. ويُفترض أن تكون نتائجهما قابلة للمقارنة (مع مراعاة اللاحتمية في API).

### Run Card Hash

تجيب **تجزئة بطاقة التشغيل (run card hash)** عن السؤال: *"هل تم العبث بملف النتائج المحدد هذا؟"*

وهي SHA-256 لكامل ملف JSON لبطاقة التشغيل (باستثناء الحقل `run_card_hash` نفسه). إذا تغيّر أي حقل — درجة، أو طابع زمني، أو مخرج واحد — تنكسر التجزئة.

:::info متى تستخدم كلًا منهما
استخدم **البصمة** لتجميع عمليات التشغيل القابلة للمقارنة (تجربة واحدة، عمليات تنفيذ مختلفة). واستخدم **تجزئة بطاقة التشغيل** للتحقق من سلامة ملف نتائج محدد.
:::

---

## النشر على لوحة المتصدرين

بعد إكمال التشغيل، استخدم `mt-eval publish` لإرسال بطاقة التشغيل:

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

إذا لم يتم توفير `--method-card` أثناء التشغيل، يُطلق `mt-eval publish` معالجًا تفاعليًا (`method_card_wizard.py`) يرشدك خلال وصف أسلوبك (الاسم، والفئة، والأدوات المستخدمة، وغير ذلك). ويُضمَّن مخرج المعالج في بطاقة التشغيل قبل الإرسال.

### الإرسال اليدوي

تُحفظ بطاقات التشغيل كملفات JSON في مجلد الإخراج. يمكنك أيضًا إرسال أي ملف بطاقة تشغيل عبر واجهة لوحة المتصدرين على [/leaderboard](https://champollion.dev/leaderboard)، أو عبر API:

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning التحقق في لوحة المتصدرين
تتحقق لوحة المتصدرين من بطاقات التشغيل المُرسلة مقارنةً بسجل مجموعات البيانات. وتُرفض الإرسالات التي تشير إلى مجموعات بيانات غير معروفة، أو التي تحتوي على `run_card_hash` معطوب.
:::

:::danger لا تدرّب نموذجك على بيانات التقييم
إذا كان أسلوبك قد اطّلع على مجموعة بيانات التقييم أثناء التطوير — كبيانات تدريب، أو أمثلة few-shot، أو مدخلات قاموس، أو مادة لهندسة الموجّهات — فسيتم **استبعاد** إرسالك. راجع [MT Evaluation](/docs/leaderboard/rules) لمعرفة ما يميز الأسلوب الجيد عن السيئ.
:::

---

## انظر أيضًا

- [MT Evaluation](/docs/leaderboard/rules) — نظرة عامة، والقيمة المقترحة للوحة المتصدرين، وإرشادات الأساليب الجيدة/السيئة
- [Evaluation Datasets](/docs/leaderboard/datasets) — تنسيق مجموعات البيانات، وEDTeKLA، وFLORES+
- [Run Card Specification](/docs/specifications/run-card) — مخطط JSON الكامل
- [Building a Method](/docs/specifications/methods) — واجهة الأسلوب لإنشاء أساليب قابلة للتقييم
- [Method Leaderboard](https://champollion.dev/leaderboard) — درجات القياس المباشرة
- [Benchmark Specification](/docs/specifications/benchmark) — بروتوكول التقييم، وتنسيق المدونة النصية، ومخطط بطاقة التشغيل
- [Scoring Specification](/docs/specifications/scoring) — المصدر الوحيد للحقيقة (SSOT) للمقاييس وأوزان composite ومستويات الجودة