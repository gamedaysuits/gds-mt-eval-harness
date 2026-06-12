---
sidebar_position: 6
title: "دليل عملي: النماذج المتسلسلة"
---
# النماذج المتسلسلة (خط معالجة متعدد المراحل)

> **الفكرة:** النموذج A يولّد ترجمة أولية ← النموذج B يحرّرها لاحقًا ← النموذج C يقيّم النتيجة أو يتحقق منها. كل مرحلة متخصصة في مهمة واحدة. مخرجات خط المعالجة أفضل من أي نموذج منفرد بمفرده.

:::info هذا دليل عملي، وليس تنفيذًا مكتملًا
يرسم هذا الدليل الخطوط العامة لبنية خطوط المعالجة متعددة المراحل. تعتمد النماذج المحددة وتكوين السلسلة على الزوج اللغوي والميزانية المتاحة لديك.
:::

## متى تستخدم هذا الأسلوب

- عندما ينتج نموذج منفرد **جودة غير متسقة** — جيدة في بعض المدخلات وسيئة في غيرها
- عندما تريد **فصل التوليد عن التحقق** — نموذج يُنشئ، وآخر ينقد
- عندما تتوفر لديك ميزانية لإجراء **عدة استدعاءات API لكل ترجمة** (يتزايد زمن الاستجابة والتكلفة خطيًا مع عدد المراحل)
- عندما تريد الجمع بين نماذج ذات **نقاط قوة مختلفة** (مثل مولّد إبداعي + محرّر دقيق)

## كيف يعمل

```
Input ──→ [Stage 1: Generator] ──→ [Stage 2: Editor] ──→ [Stage 3: Validator] ──→ Output
              │                         │                        │
              │ "Translate this"        │ "Fix errors in         │ "Rate 1-5 and
              │                         │  this translation"     │  flag issues"
              ▼                         ▼                        ▼
         Raw translation          Polished translation      Score + accept/reject
```

## مثال: خط معالجة ثلاثي المراحل

```python
# Stage 1: Fast model generates candidate
raw = await fast_model.translate(source, target_lang="crk")

# Stage 2: Strong model post-edits
edited = await strong_model.complete(
    f"The following {target_lang} translation may contain errors. "
    f"Fix any grammatical or vocabulary mistakes:\n"
    f"Source: {source}\nTranslation: {raw}\nCorrected:"
)

# Stage 3: Validator model scores
score = await validator.complete(
    f"Rate this translation 1-5 for accuracy and fluency:\n"
    f"Source: {source}\nTranslation: {edited}\nScore:"
)

# Accept if score >= 3, otherwise retry Stage 1 with different temperature
```

## أنماط السلاسل الشائعة

| النمط | المراحل | حالة الاستخدام |
|---------|--------|----------|
| **توليد ← تحرير** | نموذج LLM سريع ← نموذج LLM قوي | تحسين الجودة بكفاءة في التكلفة |
| **توليد ← تحقق ← إعادة محاولة** | LLM ← FST/قواعد ← LLM (إعادة المحاولة عند الفشل) | الصحة الصرفية (انظر [FST-Gated](./fst-gated-pipeline)) |
| **توليد ← ترجمة عكسية ← تقييم** | LLM(en→crk) ← LLM(crk→en) ← مقارنة | فحص اتساق الترجمة ذهابًا وإيابًا |
| **مجموعة نماذج ← تصويت** | 3 نماذج LLM بشكل مستقل ← تصويت الأغلبية | المتانة من خلال التنوع |

## قرارات التصميم الرئيسية

**ميزانية زمن الاستجابة:** كل مرحلة تضاعف زمن الاستجابة. سلسلة من 3 مراحل بمعدل ثانيتين لكل مرحلة = 6 ثوانٍ لكل ترجمة. هذا مقبول للتقييم بالدفعات؛ لكنه قد لا يناسب الاستخدام في الزمن الحقيقي.

**مضاعِف التكلفة:** 3 مراحل = 3 أضعاف تكلفة API. استخدم نماذج أرخص للمراحل المبكرة، ونماذج أغلى للمراحل الحرجة.

**انتشار الأخطاء:** قد يضلّل مخرج سيئ من المرحلة 1 المرحلة 2. ضمّن النص المصدر الأصلي في كل مرحلة حتى تتمكن النماذج اللاحقة من التعافي.

## المزايا والعيوب

| | |
|---|---|
| ✅ إمكانية الجمع بين نقاط قوة النماذج المتخصصة | ❌ زمن الاستجابة والتكلفة يتضاعفان مع كل مرحلة |
| ✅ فصل المسؤوليات (التوليد مقابل التحقق) | ❌ تعقيد في تصحيح الأخطاء — أي مرحلة أدخلت الخطأ؟ |
| ✅ سهولة استبدال المراحل المنفردة | ❌ انتشار الأخطاء بين المراحل |
| ✅ التحقق ذهابًا وإيابًا يكشف الهلوسات | ❌ تناقص العوائد بعد 2-3 مراحل |

## يتكامل جيدًا مع

- **[FST-Gated Pipeline](./fst-gated-pipeline)** — استخدام FST كمرحلة تحقق
- **[Dictionary-Augmented LLM](./dictionary-augmented-llm)** — حقن القاموس في مرحلة التوليد
- **[Coached LLM Prompting](./coached-llm-prompting)** — التوجيه في مرحلة واحدة أو أكثر

## انظر أيضًا

- [Eval Harness](/docs/specifications/harness) — يقيس الـ harness مخرجات خط المعالجة من البداية إلى النهاية
- [Run Card Specification](/docs/specifications/run-card) — يُسجَّل زمن الاستجابة والتكلفة لكل إدخال
- [دعم لغة منخفضة الموارد](/docs/community/low-resource-languages)