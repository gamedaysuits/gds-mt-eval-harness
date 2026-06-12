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
# منصة التقييم Eval Harness v2.0

> **ملخص تنفيذي.** تغطي هذه الصفحة تثبيت وإعداد واستخدام منصة تقييم الترجمة الآلية (MT evaluation harness) — وهي الأداة التي تُقيّم أداء طرق الترجمة مقابل مدونات نصية موحّدة وتُنتج بطاقات تشغيل مُقيَّمة. للاطلاع على التعريفات المعتمدة للمقاييس والمخططات وبروتوكول التقييم، راجع [مواصفات المعيار](/docs/specifications/benchmark).

تُشغّل المنصة تجارب الترجمة وتُنتج بطاقات التشغيل. وهي تتولى بناء الموجّهات (prompts)، واستدعاءات واجهة برمجة التطبيقات (API)، والتقييم، وترميز النتائج وتخزينها — وأنت توفّر مجموعة البيانات والنموذج.

## التثبيت

**المتطلبات:** Python 3.10+

```bash
pip install sacrebleu aiohttp
```

استنسخ مستودع المنصة:

```bash
git clone https://github.com/gamedaysuits/arena.git
cd arena
```

## الاستخدام

```bash
mt-eval run --corpus path/to/dataset.json
```

يقوم هذا الأمر بتمرير كل مُدخل في المدونة النصية عبر النموذج المُعدّ (أو إضافة الطريقة)، ثم يُقيّم المخرجات، ويكتب ملف JSON لبطاقة التشغيل في دليل المخرجات.

## رايات سطر الأوامر (CLI Flags)

### `mt-eval run`

| الراية | إلزامية | القيمة الافتراضية | الوصف |
|------|----------|---------|-------------|
| `--corpus` | ✅ | — | مسار ملف المدونة النصية (`.json`، `.jsonl`، `.tsv`) |
| `--source-file` / `--reference-file` | — | — | ملفات نصية متوازية (بصيغة FLORES+ وWMT) |
| `-m, --model` | — | `gemini-pro` | مُعرّف النموذج (اسم مختصر أو مُعرّف OpenRouter كامل). يُحلّ عبر `shared/model-aliases.json`. يُفصل بفواصل عند تشغيل عدة نماذج |
| `-d, --dataset` | — | `all` | مُرشّح مجموعة البيانات: `all`، أو اسم مقطع، أو نطاق معرّفات |
| `--ids` | — | — | معرّفات المُدخلات المراد تقييمها، مفصولة بفواصل |
| `--source-lang` | — | `English` | اسم اللغة المصدر |
| `--target-lang` | — | — | اسم اللغة الهدف |
| `-p, --prompt` | — | `naive` | إصدار الموجّه (`naive`، `custom`، `champollion`) |
| `--coaching-file` | — | — | مسار ملف نصي لموجّه التدريب التوجيهي |
| `--coaching` | — | — | نص توجيهي مباشر (سلسلة نصية بين علامتي اقتباس) |
| `--method` | — | — | مسار دليل إضافة الطريقة (يحتوي على `method.json` + وحدة Python) |
| `--method-card` | — | — | مسار ملف JSON لبطاقة الطريقة الخاصة ببيانات لوحة المتصدرين الوصفية |
| `--fst-retries` | — | `0` | عدد محاولات إعادة FST (لطريقة LLM الافتراضية فقط) |
| `--skip-fst` | — | `false` | تخطي بوابة جودة FST بالكامل |
| `--tools` | — | `false` | تفعيل وضع استدعاء الأدوات |
| `--tools-list` | — | — | أسماء الأدوات مفصولة بفواصل |
| `--max-tool-rounds` | — | `8` | الحد الأقصى لجولات استدعاء الأدوات لكل مُدخل |
| `--hooks` | — | — | أسماء الخطافات (hooks) لما بعد الترجمة |
| `--style-profile` | — | — | مسار ملف JSON لملف تعريف الأسلوب. يُفعّل مقاييس اتساق أسلوب الكتابة (معلوماتية — لا تدخل أبدًا في composite score؛ راجع [§ مقاييس أسلوب الكتابة والمستوى اللغوي](#writing-style-and-register-metrics-informational)) |
| `-b, --batch-size` | — | `25` | عدد المُدخلات لكل استدعاء API |
| `-c, --concurrency` | — | `8` | استدعاءات API المتوازية |
| `--max-tokens` | — | `32768` | الحد الأقصى للرموز (tokens) لكل استدعاء API |
| `--temperature` | — | `0.0` | درجة حرارة أخذ العينات (0.0 = حتمي) |
| `--no-cache` | — | `false` | تعطيل التخزين المؤقت للاستجابات |
| `--cache-dir` | — | `eval/cache/harness` | مسار دليل التخزين المؤقت |
| `-o, --output-dir` | — | `eval/logs/harness` | دليل المخرجات لبطاقات التشغيل والسجلات |
| `-n, --name` | — | — | اسم تشغيل قابل للقراءة البشرية |
| `--dry-run` | — | `false` | التحقق من صحة الإعدادات دون إجراء استدعاءات API |
| `--champollion-config` | — | — | مسار `champollion.config.json` |
| `--champollion-cards-dir` | — | — | دليل بطاقات اللغات |
| `--target-lang-code` | — | — | رمز اللغة وفق BCP-47 |

### الأوامر الفرعية الأخرى

| الأمر الفرعي | الوصف |
|------------|-------------|
| `mt-eval test <log_path>` | تحليل سجل تشغيل مكتمل |
| `mt-eval publish <report_path>` | إرسال بطاقة تشغيل إلى لوحة المتصدرين |
| `mt-eval compare <logs...>` | مقارنة عدة عمليات تشغيل جنبًا إلى جنب |
| `mt-eval dashboard <logs...>` | إنشاء لوحة معلومات HTML من سجلات التشغيل |
| `mt-eval list models\|prompts\|datasets` | عرض الموارد المتاحة |
| `mt-eval export` | تجميع الإعداد الحالي كإضافة طريقة champollion |
| `mt-eval export-config` | تصدير MethodConfig المُحلّ (جميع الحقول القياسية الثمانية) بصيغة JSON |

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

تُنتج كل تجربة **بطاقة تشغيل** — وهي مستند JSON مكتفٍ بذاته. البنية على المستوى الأعلى:

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

راجع [مواصفات بطاقة التشغيل](/docs/specifications/run-card) للاطلاع على المخطط الكامل مع توثيق كل حقل.

:::info المخطط المعتمد
تُعد [مواصفات المعيار](/docs/specifications/benchmark) المصدر الوحيد للحقيقة فيما يخص مخطط بطاقة التشغيل. لتعريفات المقاييس وأوزان composite ومستويات الجودة، راجع [مواصفات التقييم](/docs/specifications/scoring). توثّق هذه الصفحة كيفية استخدام المنصة؛ بينما تحدد المواصفات معنى المخرجات.
:::

### الكتل الرئيسية

**`dataset`** — تحدد مجموعة البيانات المستخدمة، بما في ذلك تجزئة محتواها (content hash) بحيث ترتبط النتائج بإصدار محدد:

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

**`scores`** — المقاييس المُجمَّعة للتشغيل:

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

**`totals`** — تتبّع استخدام الرموز والتكلفة:

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

## مقاييس أسلوب الكتابة والمستوى اللغوي (معلوماتية)

يمكن للمنصة تقييم ما إذا كانت الترجمات تطابق **المستوى اللغوي** و**أسلوب الكتابة** المستهدفين، عبر إضافة مقياس `WritingStyleConsistency` (`mt_eval_harness/plugins/writing_style.py`). فقد تكون الترجمة صحيحة لغويًا لكن بمستوى لغوي خاطئ — صياغة غير رسمية في مستند قانوني، أو عبارات رسمية جاهزة في نص تسويقي — ولن تلاحظ المقاييس النصية ذلك. أما هذه المقاييس فتلاحظه.

**ما يُقاس (لكل مُدخل):**

| المقياس | النطاق | المعنى |
|--------|-------|---------|
| `style_register_match` | قيمة منطقية (boolean) | هل يطابق المخرج المستوى اللغوي المتوقع؟ يُستمد الهدف من حقل `register` في مُدخل المدونة النصية (راجع [مواصفات المعيار §2.6](/docs/specifications/benchmark)) أو من ملف تعريف أسلوب |
| `style_sentence_length_ratio` | عدد عشري (float) | متوسط طول الجملة المتوقع مقابل المرجعي (1.0 = تطابق؛ التباعد = انحراف أسلوبي) |
| `style_formality_score` | 0.0–1.0 | وجود علامات الرسمية/عدم الرسمية (ضمائر T–V، الاختصارات، …) باستخدام موارد العلامات الخاصة بكل لغة |

**المُجمَّع:** `style_consistency_rate` — نسبة المُدخلات التي لم يُكتشف فيها عدم تطابق في المستوى اللغوي.

فعّل هدفًا مخصصًا باستخدام `--style-profile path/to/profile.json` (مثل ملف تعريف صوت العلامة التجارية)؛ ومن دونه، تعود الإضافة إلى البيانات الوصفية `register` لكل مُدخل في المدونة النصية حيثما وُجدت.

:::caution تحديد نزيه للنطاق
هذه المقاييس **معلوماتية فقط** — فهي لا تدخل أبدًا في composite score، كما أن اكتشاف الرسمية يعتمد على العلامات (أسلوب استدلالي)، وليس حكمًا قائمًا على التعلّم. تعامل معها كأداة لاكتشاف الانحراف في الالتزام بالمستوى اللغوي، وليس حكمًا على جودة الأسلوب.
:::

---

## البصمة (Fingerprint) مقابل تجزئة بطاقة التشغيل {#fingerprint-vs-run-card-hash}

تُنتج المنصة تجزئتين مختلفتين، ولكل منهما غرض مختلف:

### البصمة (Fingerprint)

تجيب **البصمة** على السؤال: *"هل يمكن إعادة إنتاج هذا التشغيل؟"*

فهي تُجزّئ مجموعة المُدخلات التي تحدد إعدادات التجربة — وليس المخرجات:

- SHA-256 لمجموعة البيانات
- مُعرّف النموذج
- تسمية الحالة
- SHA-256 لموجّه النظام
- درجة الحرارة
- إصدار المنصة

عمليتا تشغيل بهما بصمتان متطابقتان استخدمتا الإعداد نفسه. وينبغي أن تكون نتائجهما قابلة للمقارنة (مع مراعاة عدم حتمية واجهة برمجة التطبيقات).

### تجزئة بطاقة التشغيل

تجيب **تجزئة بطاقة التشغيل** على السؤال: *"هل تم العبث بملف النتائج المحدد هذا؟"*

فهي قيمة SHA-256 لملف JSON الكامل لبطاقة التشغيل (باستثناء حقل `run_card_hash` نفسه). فإذا تغيّر أي حقل — درجة، أو طابع زمني، أو مخرج واحد — تنكسر التجزئة.

:::info متى تستخدم كلًّا منهما
استخدم **البصمة** لتجميع عمليات التشغيل القابلة للمقارنة (التجربة نفسها، عمليات تنفيذ مختلفة). واستخدم **تجزئة بطاقة التشغيل** للتحقق من سلامة ملف نتائج محدد.
:::

---

## النشر إلى لوحة المتصدرين

بعد إكمال التشغيل، استخدم `mt-eval publish` لإرسال بطاقة التشغيل:

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

إذا لم يتم توفير `--method-card` أثناء التشغيل، يُطلق `mt-eval publish` معالجًا تفاعليًا (`method_card_wizard.py`) يرشدك خلال وصف طريقتك (الاسم، الفئة، الأدوات المستخدمة، وما إلى ذلك). يُدمج ناتج المعالج في بطاقة التشغيل قبل الإرسال.

### الإرسال اليدوي

تُحفظ بطاقات التشغيل كملفات JSON في دليل المخرجات. يمكنك أيضًا إرسال أي ملف بطاقة تشغيل عبر واجهة لوحة المتصدرين على [/leaderboard](https://champollion.dev/leaderboard)، أو من خلال واجهة برمجة التطبيقات:

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning التحقق من صحة لوحة المتصدرين
تتحقق لوحة المتصدرين من صحة بطاقات التشغيل المُرسلة مقابل سجل مجموعات البيانات. تُرفض الإرسالات التي تشير إلى مجموعات بيانات غير معروفة، أو التي تحتوي على `run_card_hash` معطوب.
:::

:::danger لا تُدرّب على بيانات التقييم
إذا اطّلعت طريقتك على مجموعة بيانات التقييم أثناء التطوير — كبيانات تدريب، أو أمثلة few-shot، أو مُدخلات معجمية، أو مادة لهندسة الموجّهات — فسيتم **استبعاد** إرسالك. راجع [تقييم الترجمة الآلية](/docs/leaderboard/rules) لمعرفة ما يميز الطريقة الجيدة من السيئة.
:::

---

## انظر أيضًا

- [تقييم الترجمة الآلية](/docs/leaderboard/rules) — نظرة عامة، والقيمة المقترحة للوحة المتصدرين، وإرشادات الطرق الجيدة/السيئة
- [مجموعات بيانات التقييم](/docs/leaderboard/datasets) — صيغة مجموعة البيانات، EDTeKLA، FLORES+
- [مواصفات بطاقة التشغيل](/docs/specifications/run-card) — مخطط JSON الكامل
- [بناء طريقة](/docs/specifications/methods) — واجهة الطريقة لإنشاء طرق قابلة للتقييم
- [لوحة متصدري الطرق](https://champollion.dev/leaderboard) — درجات المعيار المباشرة
- [مواصفات المعيار](/docs/specifications/benchmark) — بروتوكول التقييم، وصيغة المدونة النصية، ومخطط بطاقة التشغيل
- [مواصفات التقييم](/docs/specifications/scoring) — المصدر الوحيد للحقيقة (SSOT) للمقاييس وأوزان composite ومستويات الجودة