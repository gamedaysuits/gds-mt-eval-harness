---
sidebar_position: 4
title: "مواصفات بطاقة التشغيل (Run Card)"
---
# مواصفات بطاقة التشغيل

> **ملخص تنفيذي.** بطاقة التشغيل هي الوحدة الذرية لقياس الأداء — وهي مستند JSON يسجّل التكوين الكامل والنتائج لكل إدخال والدرجات الإجمالية لعملية تقييم واحدة. توثّق هذه الصفحة المخطط (schema) والحقول وآلية البصمة وبنية الدرجات. راجع [مواصفات قياس الأداء](/docs/specifications/benchmark) للاطلاع على التعريفات المعتمدة.

بطاقة التشغيل هي السجل الكامل لعملية تقييم واحدة. وهي تحتوي على كل ما يلزم لفهم التجربة وإعادة إنتاجها والتحقق منها: التكوين، والدرجات، والنتائج الفردية، واستخدام الرموز (tokens)، والبيانات الوصفية للبيئة.

**إصدار المخطط:** 2.0

:::info المخطط المعتمد
تُعد [مواصفات قياس الأداء](/docs/specifications/benchmark) المصدر الوحيد للحقيقة فيما يخص مخطط بطاقة التشغيل. للاطلاع على تعريفات المقاييس وأوزان composite score ومستويات الجودة، راجع [مواصفات التقييم](/docs/specifications/scoring). توثّق هذه الصفحة التنفيذ الحالي.
:::

---

## الحقول ذات المستوى الأعلى

| الحقل | النوع | الوصف |
|-------|------|-------------|
| `run_id` | `string` | معرّف UUID v4 يُولَّد عند بدء التشغيل |
| `harness_version` | `string` | الإصدار الدلالي (semantic version) لأداة التشغيل التي أنتجت هذه البطاقة (مثل `2.0`) |
| `model_slug` | `string` | معرّف النموذج المختصر المستخدم في التشغيل (مثل `google/gemini-3.1-pro`) |
| `model_id` | `string` | معرّف النموذج المحلول الذي تُرجعه واجهة API (مثل `gemini-3.1-pro-001`) |
| `condition` | `string` | تسمية التجربة (مثل `baseline`، `coached-v3`، `few-shot`) |
| `timestamp` | `string` | الطابع الزمني بتوقيت UTC وفق ISO 8601 عند بدء التشغيل |
| `elapsed_seconds` | `number` | المدة الفعلية الكاملة للتشغيل |

```json
{
  "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "harness_version": "2.0",
  "model_slug": "google/gemini-3.1-pro",
  "model_id": "gemini-3.1-pro-001",
  "condition": "baseline",
  "timestamp": "2026-06-01T03:22:41Z",
  "elapsed_seconds": 142.7
}
```

---

## `dataset`

يحدّد مجموعة بيانات التقييم ويثبّتها على إصدار محتوى معيّن عبر SHA-256.

| الحقل | النوع | الوصف |
|-------|------|-------------|
| `id` | `string` | معرّف مجموعة البيانات (مثل `edtekla-dev-v1`) |
| `version` | `string` | سلسلة إصدار مجموعة البيانات |
| `language_pair` | `string` | تسمية العرض (مثل `EN→CRK`) |
| `sha256` | `string` | بصمة SHA-256 لمحتويات ملف مجموعة البيانات. تضمن تحديد البيانات المستخدمة بدقة |
| `entry_count` | `number` | عدد الإدخالات في مجموعة البيانات |

```json
// Example using master_corpus.json (62 gold + 342 textbook = 404)
{
  "dataset": {
    "id": "edtekla-dev-v1",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "entry_count": 404
  }
}
```

---

## `config`

تكوين واجهة API والتجميع (batching) المستخدم في هذا التشغيل.

| الحقل | النوع | الوصف |
|-------|------|-------------|
| `api_provider` | `string` | اسم مزوّد واجهة API (مثل `openrouter`) |
| `temperature` | `number` | درجة حرارة أخذ العينات (temperature) |
| `max_tokens` | `number` | الحد الأقصى للرموز (tokens) لكل إكمال |
| `batch_size` | `number` | عدد الإدخالات لكل دفعة متزامنة |
| `concurrency` | `number` | الحد الأقصى لطلبات API المتوازية |
| `coaching_file` | `string` | مسار ملف موجّه التدريب (coaching prompt)، إذا استُخدم |
| `method_path` | `string` | مسار مجلد ملحق الطريقة (method plugin)، إذا استُخدم |
| `fst_retries` | `number` | عدد محاولات إعادة المحاولة لـ FST |

```json
{
  "config": {
    "api_provider": "openrouter",
    "temperature": 0.0,
    "max_tokens": 32768,
    "batch_size": 25,
    "concurrency": 8
  }
}
```

:::info بطاقات التشغيل المنشورة تتضمّن `method_config`
عند نشر بطاقة تشغيل عبر `mt-eval publish`، تقوم `publish.py` بإدراج كتلة `method_config` تحتوي على MethodConfig المعتمد المكوّن من 8 حقول. يتيح ذلك تثبيتًا سلسًا من لوحة المتصدرين — إذ يمكن لأي شخص إعادة إنتاج الطريقة مباشرة من البطاقة المنشورة.

```json
{
  "method_config": {
    "model": "gemini-pro",
    "temperature": 0.0,
    "batchSize": 25,
    "register": "Formal Plains Cree. Use SRO orthography.",
    "coachingFile": "prompts/crk-coaching-v8.txt",
    "coachingPrompt": null,
    "promptContext": "champollion",
    "qualityTier": "verified"
  }
}
```

تستخدم جميع الحقول صيغة **camelCase** وتتبع مخطط MethodConfig المعتمد (راجع [بناء طريقة](/docs/specifications/methods)).
:::

---

## `system_prompt_sha256` / `system_prompt_used`

| الحقل | النوع | الوصف |
|-------|------|-------------|
| `system_prompt_sha256` | `string` | بصمة SHA-256 لموجّه النظام (system prompt). مضمّنة في البصمة |
| `system_prompt_used` | `string` | النص الكامل لموجّه النظام المرسَل إلى النموذج |

بصمة الموجّه جزء من [البصمة](#fingerprint) — عمليتا تشغيل بموجّهين مختلفين ستحملان بصمتين مختلفتين حتى لو تطابقت جميع الإعدادات الأخرى.

---

## `fingerprint`

معرّف لقابلية إعادة الإنتاج. عمليتا تشغيل ببصمتين متطابقتين استخدمتا الإعداد التجريبي نفسه.

| الحقل | النوع | الوصف |
|-------|------|-------------|
| `hash` | `string` | بصمة SHA-256 للمكوّنات المرتّبة |
| `components` | `object` | قيم الإدخال التي جرى حساب البصمة منها |

### مكوّنات البصمة

| المكوّن | الوصف |
|-----------|-------------|
| `dataset_sha256` | بصمة ملف مجموعة البيانات |
| `model_slug` | النموذج المستخدم |
| `condition` | تسمية حالة التجربة |
| `system_prompt_sha256` | بصمة موجّه النظام |
| `temperature` | درجة حرارة أخذ العينات |
| `harness_version` | إصدار أداة التشغيل |

```json
{
  "fingerprint": {
    "hash": "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
    "components": {
      "dataset_sha256": "e3b0c44298fc1c14...",
      "model_slug": "google/gemini-3.1-pro",
      "condition": "baseline",
      "system_prompt_sha256": "abc123...",
      "temperature": 0.0,
      "harness_version": "2.0"
    }
  }
}
```

:::info البصمة ≠ بصمة بطاقة التشغيل
تحدّد البصمة *تكوين التجربة*. أما `run_card_hash` فتتحقق من *سلامة ملف النتائج*. راجع [Fingerprint vs Run Card Hash](/docs/specifications/harness#fingerprint-vs-run-card-hash) لمزيد من التفاصيل.
:::

---

## `scores`

المقاييس الإجمالية للتشغيل بأكمله.

### الدرجات ذات المستوى الأعلى

| الحقل | النوع | الوصف |
|-------|------|-------------|
| `total` | `number` | إجمالي الإدخالات المقيَّمة |
| `exact_matches` | `number` | الإدخالات التي تطابق فيها المخرج تمامًا مع المعيار الذهبي |
| `exact_match_rate` | `number` | `exact_matches / total` (0.0–1.0) |
| `fst_accepted` | `number` | الإدخالات التي قَبِل فيها محلّل FST المخرج |
| `fst_acceptance_rate` | `number` | `fst_accepted / total` (0.0–1.0). `null` إذا لم يُستخدم محلّل FST |
| `chrf_plus_plus` | `number` | درجة chrF++ على مستوى المتن (0–100) |
| `errors` | `number` | الإدخالات التي أخفقت (خطأ في API، انتهاء المهلة، إلخ) |
| `avg_latency_seconds` | `number` | متوسط زمن الاستجابة عبر جميع الإدخالات |
| `median_latency_seconds` | `number` | وسيط زمن الاستجابة |
| `p95_latency_seconds` | `number` | زمن الاستجابة عند المئين 95 |

### `by_difficulty`

الدرجات مصنّفة حسب مستوى الصعوبة. يحتوي كل مفتاح (عدد صحيح من 1 إلى 5) على حقول المقاييس نفسها الموجودة في الدرجات ذات المستوى الأعلى.

```json
{
  "by_difficulty": {
    "1": {
      "total": 20,
      "exact_matches": 8,
      "exact_match_rate": 0.40,
      "chrf_plus_plus": 68.2,
      "fst_accepted": 18,
      "fst_acceptance_rate": 0.90
    },
    "2": { ... },
    "3": { ... },
    "4": { ... },
    "5": { ... }
  }
}
```

### `by_provenance`

الدرجات مصنّفة حسب مصدر الإدخال (provenance). يحتوي كل مفتاح (مثل `gold_standard`، `textbook`) على حقول المقاييس نفسها.

```json
{
  "by_provenance": {
    "gold_standard": {
      "total": 80,
      "exact_matches": 10,
      "exact_match_rate": 0.125,
      "chrf_plus_plus": 44.8
    },
    "textbook": { ... }
  }
}
```

---

## `totals`

تتبّع استخدام الرموز (tokens) والتكلفة للتشغيل بأكمله.

| الحقل | النوع | الوصف |
|-------|------|-------------|
| `prompt_tokens` | `number` | إجمالي رموز الإدخال عبر جميع استدعاءات API |
| `completion_tokens` | `number` | إجمالي رموز الإخراج |
| `reasoning_tokens` | `number` | الرموز المستخدمة في الاستدلال بسلسلة التفكير (chain-of-thought) (يعتمد على النموذج، وقيمته 0 لمعظم النماذج) |
| `cached_tokens` | `number` | الرموز المقدَّمة من ذاكرة التخزين المؤقت للموجّهات لدى المزوّد |
| `total_cost_usd` | `number` | التكلفة الإجمالية بالدولار الأمريكي (كما تُبلّغ عنها واجهة API) |
| `cost_per_entry_usd` | `number` | `total_cost_usd / entry_count` |
| `reasoning_ratio` | `number` | `reasoning_tokens / completion_tokens` (0.0–1.0) |

```json
{
  "totals": {
    "prompt_tokens": 48200,
    "completion_tokens": 3100,
    "reasoning_tokens": 0,
    "cached_tokens": 12000,
    "total_cost_usd": 0.42,
    "cost_per_entry_usd": 0.0034,
    "reasoning_ratio": 0.0
  }
}
```

---

## `environment`

البيانات الوصفية لبيئة التشغيل لأغراض قابلية إعادة الإنتاج.

| الحقل | النوع | الوصف |
|-------|------|-------------|
| `harness_version` | `string` | إصدار أداة التشغيل (يطابق `harness_version` في المستوى الأعلى) |
| `harness_git_commit` | `string` | بصمة SHA لإيداع Git الخاص بأداة التشغيل وقت التنفيذ |
| `python_version` | `string` | إصدار مفسّر Python |
| `sacrebleu_version` | `string` | إصدار مكتبة sacrebleu (المستخدمة لحساب درجة chrF++) |
| `os` | `string` | معرّف نظام التشغيل |

```json
{
  "environment": {
    "harness_version": "2.0",
    "harness_git_commit": "a1b2c3d",
    "python_version": "3.11.9",
    "sacrebleu_version": "2.4.0",
    "os": "macOS-14.5-arm64"
  }
}
```

---

## `results[]`

مصفوفة النتائج لكل إدخال. كائن واحد لكل إدخال في مجموعة البيانات، مرتّبة حسب الفهرس.

| الحقل | النوع | الوصف |
|-------|------|-------------|
| `entry_id` | `integer` | معرّف هذا الإدخال في المتن (يطابق `entries[].id`) |
| `source` | `string` | النص المصدر الذي جرت ترجمته |
| `reference` | `string` | المرجع المعياري الذهبي من المتن |
| `predicted` | `string` | المخرج الفعلي للطريقة |
| `exact_match` | `boolean` | ما إذا كان `predicted` يطابق تمامًا `reference` بعد التطبيع |
| `entry_chrf` | `number` | درجة chrF++ على مستوى الجملة لهذا الإدخال (0–100) |
| `fst_accepted` | `boolean \| null` | ما إذا كان محلّل FST قد قَبِل المخرج. `null` إذا لم يُكوَّن أي محلّل |
| `fst_analysis` | `string[]` | سلاسل تحليل FST للمخرج (مصفوفة فارغة إذا لم يُحلَّل أو رُفض) |
| `difficulty` | `integer` | مستوى الصعوبة من المتن (1–5) |
| `provenance` | `string` | وسم المصدر (provenance) من المتن |
| `latency_seconds` | `number` | زمن الاستجابة لهذا الإدخال بمفرده |
| `usage` | `object` | استخدام الرموز لكل إدخال: `{ prompt_tokens, completion_tokens, reasoning_tokens }` |
| `error` | `string \| null` | رسالة الخطأ إذا أخفق هذا الإدخال. `null` عند النجاح |

```json
{
  "results": [
    {
      "entry_id": 1,
      "source": "Hello",
      "reference": "tânisi",
      "predicted": "tânisi",
      "exact_match": true,
      "entry_chrf": 100.0,
      "fst_accepted": true,
      "fst_analysis": ["tânisi+V+AI+Ind+2Sg"],
      "difficulty": 1,
      "provenance": "gold_standard",
      "latency_seconds": 0.82,
      "usage": {
        "prompt_tokens": 385,
        "completion_tokens": 12,
        "reasoning_tokens": 0
      },
      "error": null
    }
  ]
}
```

---

## `run_card_hash`

| الحقل | النوع | الوصف |
|-------|------|-------------|
| `run_card_hash` | `string` | بصمة SHA-256 لملف JSON الكامل لبطاقة التشغيل، مع تعيين الحقل `run_card_hash` نفسه إلى `""` أثناء حساب البصمة |

هذا هو ختم كشف العبث. تعيد لوحة المتصدرين حساب هذه البصمة عند التقديم وترفض البطاقات التي لا تتطابق فيها.

**حساب البصمة:**

1. حوّل بطاقة التشغيل إلى صيغة JSON مع تعيين `run_card_hash` إلى `""`
2. احسب SHA-256 للسلسلة المحوَّلة
3. عيّن `run_card_hash` إلى الملخص السداسي العشري الناتج

```python
import hashlib, json

card["run_card_hash"] = ""
card_json = json.dumps(card, sort_keys=True, ensure_ascii=False)
card["run_card_hash"] = hashlib.sha256(card_json.encode()).hexdigest()
```

:::info التحليل التفصيلي لكل إدخال
تملأ بطاقات التشغيل المنشورة أيضًا جدول Supabase `run_card_entries`، الذي يخزّن النتائج لكل إدخال لأغراض التحليل التفصيلي في لوحة المتصدرين. يُملأ هذا الجدول تلقائيًا أثناء `mt-eval publish`.
:::

---

## انظر أيضًا

- [تقييم الترجمة الآلية](/docs/leaderboard/rules) — نظرة عامة، وقيمة لوحة المتصدرين، وإرشادات الطرق الجيدة/السيئة
- [Eval Harness](/docs/specifications/harness) — كيفية تشغيل التقييمات وإنشاء بطاقات التشغيل
- [مجموعات بيانات التقييم](/docs/leaderboard/datasets) — تنسيق مجموعة البيانات، EDTeKLA، FLORES+
- [بناء طريقة](/docs/specifications/methods) — واجهة الطريقة ومواصفات بطاقة الطريقة
- [لوحة متصدري الطرق](https://champollion.dev/leaderboard) — درجات قياس الأداء المباشرة
- [مواصفات قياس الأداء](/docs/specifications/benchmark) — بروتوكول التقييم، وتنسيق المتن، ومخطط بطاقة التشغيل
- [مواصفات التقييم](/docs/specifications/scoring) — المصدر الوحيد للحقيقة (SSOT) للمقاييس وأوزان composite score ومستويات الجودة