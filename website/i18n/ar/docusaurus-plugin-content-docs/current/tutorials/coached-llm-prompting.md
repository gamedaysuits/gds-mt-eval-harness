---
sidebar_position: 2
title: "دليل عملي: التلقين الموجّه لنماذج LLM (Coached LLM Prompting)"
related:
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
  - label: "Cookbook: Fine-Tuned Model"
    to: /docs/tutorials/fine-tuned-model
    kind: cookbook
  - label: "Coaching Data"
    to: https://champollion.dev/docs/concepts/coaching-data
    kind: champollion
    note: "How coaching data ships to production"
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
---
# الترجمة بالتوجيه الموجَّه لنماذج اللغة الكبيرة (Coached LLM Prompting)

> **الفكرة:** حقن قواعد النحو والقواميس ثنائية اللغة وملاحظات الأسلوب مباشرةً في موجّه النظام (system prompt) الخاص بنموذج اللغة الكبير. لا تدريب ولا ضبط دقيق — فقط معرفة لغوية منظَّمة توجّه المخرجات نحو ترجمات صحيحة.

:::info هذا دليل إرشادي، وليس تنفيذًا نهائيًا
يعرض هذا الدليل الخطوط العريضة للنهج وقراراته التصميمية الأساسية. قم بتكييفه وفقًا لزوج اللغات لديك، والموارد المتاحة، وأهداف التقييم.
:::

## متى تستخدم هذا الأسلوب

- لديك **معرفة لغوية** باللغة الهدف (قواعد نحوية، مدخلات قاموسية، تفضيلات أسلوبية) لكن لا تملك بيانات متوازية كافية للضبط الدقيق
- تريد **التكرار بسرعة** — تغييرات الموجّه تُنشر في ثوانٍ، دون إعادة تدريب
- اللغة الهدف تحتوي على **أنماط معروفة** يخطئ فيها نموذج اللغة الكبير (المطابقة في الجنس، اصطلاحات نظام الكتابة، مستويات الرسمية)
- تريد قياس أداء التوجيه الموجَّه مقارنةً بخط أساس والتكرار على ما ينجح

## كيف يعمل

1. **تجميع بيانات التوجيه** — قواعد نحوية وقاموس ثنائي اللغة وملاحظات أسلوبية في ملف JSON منظَّم
2. **تهيئة السجل اللغوي** — بادئة لموجّه النظام تحدد اللغة ونظام الكتابة والنبرة
3. **تشغيل منصة الاختبار (harness)** — تُحقن بيانات التوجيه في كل موجّه يُرسل إلى نموذج اللغة الكبير
4. **مراجعة الإخفاقات** — افحص ما ترفضه بوابة الجودة، وأضف قواعد لمعالجة الأنماط المتكررة
5. **التكرار** — كل مراجعة لملف التوجيه تُعد تجربة جديدة؛ وتتتبعها منصة الاختبار جميعًا

## بنية بيانات التوجيه

```json title="coaching/<locale>.json"
{
  "grammar_rules": [
    "Adjectives agree in gender and number with the noun they modify",
    "Use formal register (vous) for all UI text",
    "Preserve interpolation variables exactly: {{name}}, {count}"
  ],
  "dictionary": {
    "dashboard": "tableau de bord",
    "settings": "paramètres",
    "deploy": "déployer"
  },
  "style_notes": "Prefer active voice. Avoid anglicisms where a native term exists. Keep sentences concise for UI readability."
}
```

## القرارات التصميمية الأساسية

**تحديد القواعد مقابل نافذة السياق:** المزيد من القواعد يمنح نموذج اللغة الكبير إرشادًا أكبر، لكنه يستهلك من نافذة السياق المتاحة للترجمة الفعلية. ابدأ بـ 5–10 قواعد عالية التأثير، ولا تضف المزيد إلا عند ملاحظة أنماط إخفاق محددة.

**تغطية القاموس:** لست بحاجة إلى قاموس كامل — ركّز على المصطلحات التي يخطئ فيها نموذج اللغة الكبير باستمرار. حتى 20–30 مصطلحًا مفروضًا يمكن أن تحسّن الاتساق بشكل كبير.

**ترتيب القواعد مهم:** ضع القواعد الأكثر أهمية أولًا. تولي نماذج اللغة الكبيرة اهتمامًا أكبر للتعليمات المبكرة.

## تشغيل تجربة

```bash
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v1 \
  --coaching-file coaching/crk.json
```

## المزايا والعيوب

| | |
|---|---|
| ✅ تكلفة تدريب صفرية | ❌ سقف الجودة محدود بالمعرفة الأساسية لنموذج اللغة الكبير |
| ✅ تكرار فوري (غيّر الموجّه ← أعد التشغيل) | ❌ نافذة السياق تحدّ من كمية التوجيه الممكن إدراجها |
| ✅ يعمل مع أي مزوّد لنماذج اللغة الكبيرة | ❌ القواعد قد تتعارض — تصحيح تفاعلات الموجّه فنٌّ بحد ذاته |
| ✅ شفاف — يمكنك قراءة ما يراه نموذج اللغة الكبير بالضبط | ❌ لا ينشئ معرفة جديدة، بل يوجّه المعرفة الموجودة فقط |

## يتكامل جيدًا مع

- **[FST-Gated Pipeline](./fst-gated-pipeline)** — التوجيه + التحقق الصرفي يلتقطان ما يفوته التوجيه وحده
- **[Dictionary-Augmented LLM](./dictionary-augmented-llm)** — المصطلحات المفروضة هي شكل من أشكال التوجيه
- **[Few-Shot Prompting](./few-shot-prompting)** — الأمثلة والقواعد معًا أقوى من أي منهما بمفرده

## انظر أيضًا

- [Method Interface](/docs/specifications/methods) — تنسيق بيانات التوجيه وبروتوكول TranslationMethod
- [دعم لغة منخفضة الموارد](/docs/community/low-resource-languages) — السياق الكامل
- [Eval Harness](/docs/specifications/harness) — كيفية تشغيل التجارب