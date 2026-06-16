---
sidebar_position: 1
title: "تقديم طريقة"
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
# إرسال طريقة ترجمة

> **ملخص تنفيذي.** دليل بدء سريع خطوة بخطوة لإرسال أول تشغيل قياس أداء (benchmark) إلى لوحة المتصدرين. استنسخ أداة التقييم (harness)، وشغّلها على مجموعة بيانات، وراجع بطاقة التشغيل الخاصة بك، ثم أرسلها. تستغرق العملية 10 دقائق إذا كان لديك مفتاح API.

يرشدك هذا الدليل خلال خطوات إرسال أول تشغيل قياس أداء إلى لوحة المتصدرين في MT Eval Arena.

---

## المتطلبات المسبقة

- **Python 3.10+**
- **مفتاح API من OpenRouter** (أو ما يعادله لمزوّد النموذج الخاص بك)
- **طريقة ترجمة** — أي شيء يُنتج ترجمات من نص مصدر

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## الخطوة 1: تشغيل أداة التقييم (Harness)

تقوم أداة التقييم بتقييم طريقتك مقابل مجموعة بيانات موحّدة:

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| الخيار | وظيفته |
|---|---|
| `--corpus` | مسار مجموعة التقييم (`.json`، `.jsonl`، `.tsv`) |
| `--model` | معرّف النموذج — اسم مختصر (مثل `gemini-pro`) أو معرّف OpenRouter الكامل |
| `--condition` | تسمية طريقتك (تظهر على لوحة المتصدرين) |
| `--temperature` | درجة حرارة أخذ العينات (قيمة أقل = نتائج أكثر حتمية) |
| `--fst-retries` | اختياري: عدد محاولات إعادة التشغيل لـ FST |
| `--submit` | إرسال بطاقة التشغيل تلقائيًا إلى لوحة المتصدرين |

تُنتج أداة التقييم **بطاقة تشغيل (run card)** — وهي ملف JSON مستقل بذاته يحتوي على نتائجك، وقيمة التجزئة (hash) لمجموعة البيانات، ومعرّف النموذج، وبصمة تشفيرية تربط النتائج بإعدادات التجربة بدقة.

---

## الخطوة 2: مراجعة بطاقة التشغيل

تُحفظ بطاقات التشغيل في `results/`. افحص بطاقتك قبل الإرسال:

```bash
cat results/your-run-card.json | python -m json.tool
```

الحقول الأساسية التي يجب التحقق منها:
- `scores.chrf_plus_plus` — مقياس الجودة الأساسي الخاص بك
- `scores.exact_match_rate` — نسبة الترجمات المثالية
- `scores.fst_acceptance_rate` — الصحة الصرفية (إذا تم استخدام FST)
- `totals.total_cost_usd` — تكلفة التشغيل
- `fingerprint` — قيمة التجزئة الخاصة بقابلية إعادة إنتاج التجربة

راجع [مواصفات بطاقة التشغيل](/docs/specifications/run-card) للاطلاع على المخطط الكامل.

---

## الخطوة 3: الإرسال

### الإرسال التلقائي

إذا مرّرت `--submit` عند تشغيل أداة التقييم، فإن بطاقة التشغيل الخاصة بك قد تم رفعها بالفعل.

### الإرسال اليدوي

أرسل أي بطاقة تشغيل عبر API:

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

أو ارفعها من خلال [واجهة لوحة المتصدرين](https://champollion.dev/leaderboard).

---

## ماذا يحدث بعد ذلك

1. يتم التحقق من صحة إرسالك (قيمة تجزئة مجموعة البيانات، وسلامة بطاقة التشغيل)
2. تظهر النتائج على لوحة المتصدرين بحالة **Self-benchmarked** (مستوى الثقة 1)
3. للحصول على حالة **GDS Verified**، أرسل طريقتك كإضافة (plugin) قابلة للتثبيت حتى يتمكن المشرفون من إعادة إنتاج نتائجك
4. بالنسبة لطرق ترجمة لغات الشعوب الأصلية: إذا وصلت طريقتك إلى الصدارة، تبدأ عملية [نقل الملكية](/docs/sovereignty/ownership-transfer)

---

## انظر أيضًا

- [استخدام أداة التقييم](/docs/specifications/harness) — المرجع الكامل لواجهة سطر الأوامر (CLI)
- [قواعد لوحة المتصدرين](/docs/leaderboard/rules) — معايير الإرسال وسياسات مكافحة التلاعب
- [بناء طريقة ترجمة](/docs/specifications/methods) — بروتوكول TranslationMethod
- [مجموعات البيانات](/docs/leaderboard/datasets) — مجموعات بيانات التقييم المتاحة