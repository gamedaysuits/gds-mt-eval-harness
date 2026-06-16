---
sidebar_position: 9
title: "كتيّب الوصفات: الطرق التطورية / القائمة على البحث"
---
# الترجمة التطورية / القائمة على البحث

> **الفكرة:** توليد عدة ترجمات مرشّحة، وتقييمها وفق دالة لياقة (chrF++، قبول FST، اتساق الترجمة ذهابًا وإيابًا)، ثم إجراء طفرات على الأفضل أداءً، وتكرار العملية. انتقاء طبيعي للترجمات — الأصلح هو الذي يبقى.

:::info هذا دليل إرشادي، وليس تنفيذًا مكتملًا
هذا هو النهج الأكثر تجريبية في سلسلة الأدلة الإرشادية. لم تثبت فعاليته للترجمة الآلية على نطاق واسع، لكن البنية المعمارية سليمة، وسيقوم نظام التقييم بكل سرور بتقييم أي مخرجات ينتجها.
:::

## متى تستخدم هذا النهج

- لديك **دالة تقييم جيدة** لكن لا يوجد نموذج واحد ينتج نتائج متسقة
- تريد **استكشاف فضاء الحلول** على نطاق أوسع من توليد جشع واحد
- لديك **ميزانية حوسبة** تكفي للعديد من عمليات التوليد المتوازية (عشرات المرشّحين لكل مدخل)
- أنت مهتم **بالبحث المبتكر** — هذا النهج غير مستكشف بما يكفي في الترجمة الآلية للغات منخفضة الموارد

## كيف يعمل

```
[Generation 0]    Generate N candidates (different models, temperatures, prompts)
       │
       ▼
[Score]           Evaluate each candidate: chrF++, FST acceptance, fluency
       │
       ▼
[Select]          Keep top K performers
       │
       ▼
[Mutate]          Prompt an LLM: "improve this translation, fix these issues"
       │
       ▼
[Generation 1]    Score again. Repeat for G generations.
       │
       ▼
[Output]          Best-scoring candidate from final generation
```

## الهيكل الأساسي

```python
async def evolutionary_translate(source, reference=None, generations=3, pop_size=8):
    # Generation 0: diverse candidates
    population = []
    for model in ["gemini-2.5-pro", "gpt-4o", "claude-sonnet-4-6"]:
        for temp in [0.3, 0.7, 1.0]:
            candidate = await translate(source, model=model, temperature=temp)
            population.append(candidate)
    
    for gen in range(generations):
        # Score each candidate
        scored = [(c, score(c, reference)) for c in population]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Select top K
        survivors = [c for c, s in scored[:pop_size // 2]]
        
        # Mutate: ask LLM to improve each survivor
        mutants = []
        for survivor in survivors:
            mutant = await improve(source, survivor, feedback=scored[0])
            mutants.append(mutant)
        
        population = survivors + mutants
    
    return max(population, key=lambda c: score(c, reference))
```

## تصميم دالة اللياقة

دالة اللياقة هي كل شيء. الخيارات:

| المقياس | ما يقيسه | مؤتمت؟ |
|--------|-----------------|------------|
| chrF++ مقارنةً بالمرجع | التشابه على مستوى الأحرف مع الترجمة المعيارية | ✅ نعم |
| معدل قبول FST | الصحة الصرفية | ✅ نعم (إذا توفر FST) |
| اتساق الترجمة ذهابًا وإيابًا | هل تستعيد الترجمة العكسية النص المصدر؟ | ✅ نعم |
| LLM كحَكَم | نموذج لغوي آخر يقيّم الطلاقة/الدقة | ✅ نعم (لكنه مشوّش) |
| وجود مصطلحات القاموس | هل تظهر المصطلحات المعروفة بشكل صحيح؟ | ✅ نعم |

:::tip اجمع بين إشارات متعددة
الدمج الموزون لعدة مقاييس ينتج دالة لياقة أكثر متانة من أي مقياس منفرد. وهذا يحاكي [composite score](/docs/leaderboard/rules) الخاص بنظام التقييم نفسه.
:::

## المزايا والعيوب

| | |
|---|---|
| ✅ يستكشف حلولًا متنوعة | ❌ مكلف حوسبيًا (N × G استدعاء API) |
| ✅ يمكنه اكتشاف مقاربات لا يجدها أي نموذج منفرد | ❌ يتطلب دالة لياقة جيدة |
| ✅ قابل للتوازي | ❌ بطيء — عدة أجيال لكل ترجمة |
| ✅ مستقل عن النموذج | ❌ عوائد متناقصة بعد بضعة أجيال |

## يتكامل جيدًا مع

- **[Chained Models](./chained-models)** — خطوة الطفرة هي شكل من أشكال التسلسل
- **[FST-Gated Pipeline](./fst-gated-pipeline)** — قبول FST كإشارة لياقة
- **[Dictionary-Augmented LLM](./dictionary-augmented-llm)** — وجود مصطلحات القاموس كإشارة لياقة

## انظر أيضًا

- [مواصفات Run Card](/docs/specifications/run-card) — يتم تسجيل التكلفة وزمن الاستجابة لكل إدخال
- [Eval Harness](/docs/specifications/harness) — نظام التقييم يقيّم مخرجاتك النهائية، لا العملية التي اتبعتها
- [ادعم لغة منخفضة الموارد](/docs/community/low-resource-languages)