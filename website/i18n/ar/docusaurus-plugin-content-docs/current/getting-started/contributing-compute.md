---
sidebar_position: 4
title: "المساهمة بالموارد الحاسوبية"
description: "تبرّعوا برموزكم (tokens): شغّلوا عمليات قياس الأداء المفتوحة من قائمة الانتظار العامة باستخدام مفتاح API الخاص بكم وانشروا النتائج."
related:
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
  - label: "Cookbook: Coached LLM Prompting"
    to: /docs/tutorials/coached-llm-prompting
    kind: cookbook
  - label: "Cookbook: FST-Gated Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "Method Interface & Dependency Classes"
    to: /docs/specifications/methods
    kind: spec
  - label: "Leaderboard Rules & Trust Tiers"
    to: /docs/leaderboard/rules
    kind: guide
---
# المساهمة بالموارد الحاسوبية

> **الفكرة:** تحتوي لوحة الصدارة على خانات فارغة — توليفات (زوج لغوي، نموذج، حالة) لم يقم أحد بقياسها. نحن نحتفظ بقائمة انتظار عامة لها. تقوم أنت بتشغيل العناصر باستخدام مفتاح API الخاص بك، وتنشر التقارير، فتمتلئ الخريطة تدريجياً. "التبرع بالرموز (tokens)" هو مساهمة حقيقية وقابلة للاستشهاد بها في تقييم الترجمة الآلية للغات منخفضة الموارد.

## قائمة الانتظار

تُنشر قائمة الانتظار المباشرة على [champollion.dev/queue.json](https://champollion.dev/queue.json)، ويتوفر عارض طرفية لا يتطلب أي تثبيت:

```bash
curl -fsSL champollion.dev/queue | bash
```

العارض *يعرض* فقط العناصر المفتوحة وأوامر `mt-eval run` الدقيقة الخاصة بها — وهو لا ينفّذ أي شيء على الإطلاق ولا يستهلك رموزك. يحمل كل عنصر:

- `run_command` — جاهز للنسخ واللصق (يجلب المدونة اللغوية ويشغّل أداة الاختبار)
- `est_cost_usd` و`est_basis` — إما التكلفة **المرصودة** لتشغيلنا المرجعي الخاص لنفس التوليفة (مدونة، نموذج)، أو **استقراء** من متوسط تكلفة ذلك النموذج لكل مدخل في المسح × عدد مدخلات المدونة. يُذكر الأساس لكل عنصر؛ وتعتمد تكلفتك الفعلية على تسعير المزود وقت التشغيل.
- `priority` — الأزواج اللغوية غير المغطاة أولاً، والأزواج الأقل موارد أولاً (حجم المدونة هو المؤشر التقريبي)، والشرط الأساسي (naive) قبل الموجَّه (coached)، والنموذج الأرخص أولاً.

**لا يوجد حجز للعناصر — اختر أي عنصر مفتوح.** قيام شخصين بتشغيل نفس العنصر أمر غير ضار بحكم التصميم: كل بطاقة تشغيل تحمل بصمة فريدة (SHA-256 على تجزئة مجموعة البيانات + النموذج + الحالة + موجّه النظام، [Benchmark Spec §3.8](/docs/specifications/benchmark))، لذا تُزال التشغيلات المتطابقة عند النشر، كما أن التكرارات المستقلة لنفس التهيئة تُعد أدلة مفيدة وليست هدراً.

المدونات اللغوية في قائمة الانتظار هي من تقسيم التطوير (dev-split)، وتخضع لعائلة تراخيص CC-BY (مشتقة من Tatoeba)، ومعلَّمة بـ `do_not_train` — فهي مجموعات تقييم وليست بيانات تدريب. تُستثنى من قائمة الانتظار المفتوحة المدونات المرخصة لأغراض غير تجارية والمدونات الموضوعة في الحجر.

## الإعداد (مرة واحدة)

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### أي مفتاح مزوّد؟

توجّه أداة الاختبار **جميع** استدعاءات النماذج عبر [OpenRouter](https://openrouter.ai/keys). مفتاح `OPENROUTER_API_KEY` واحد يصل إلى كل نموذج في تشكيلة قائمة الانتظار — نماذج Anthropic Claude وOpenAI GPT وGoogle Gemini على حد سواء — كما أن تتبع التكاليف ولقطات التسعير في أداة الاختبار تأتي من بيانات OpenRouter الوصفية نفسها، لذا تتطابق تكلفة التشغيل المُبلَّغ عنها مع ما تمت فوترته على مفتاحك.

إذا كانت أرصدتك موجودة لدى Anthropic أو OpenAI أو Google مباشرة: أداة الاختبار **لا** تقبل حالياً مفاتيح المزودين المباشرة. تحجز مخطّطات بطاقة التشغيل حقل `api_provider` لليوم الذي تقبل فيه ذلك، لكن اليوم كل تشغيل لأداة الاختبار هو تشغيل عبر OpenRouter. إنشاء حساب OpenRouter وتمويله (أو ربط حساب المزود الخاص بك حيثما يدعم OpenRouter ذلك) هو المسار المدعوم.

### المسار السريع للوكلاء

إذا كنت تعمل مع Claude Code أو وكيل برمجة آخر، فإن المساهمة بأكملها تتم بموجّه واحد:

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## المستوى 1 — تشغيل اختبار معياري

كل `run_command` في عنصر قائمة الانتظار مكتفٍ بذاته. مثال نموذجي:

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

يطبع التشغيل تكلفته الإجمالية ويكتب سجل تشغيل بالإضافة إلى تقرير مُقيَّم في `eval/logs/`. ثم انشر:

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

يسجّلك النشر عبر OAuth (يصبح اسمك هو الإسناد على لوحة الصدارة) ويُدرج أو يُحدّث بطاقة التشغيل. تُصنَّف مساهمات المجتمع ضمن فئة الثقة **self-benchmarked** (مُقيَّم ذاتياً) — معلَّمة بوضوح بأنها "مقدَّمة من الشخص الذي قام بتشغيلها." هذا ليس تخفيضاً لمكانتها؛ بل هو نموذج الثقة وهو يعمل. تحمل بطاقة التشغيل كل ما يلزم لأي شخص لإعادة تشغيل تهيئتك بالضبط: تجزئة مجموعة البيانات، والنموذج، والحالة، وموجّه النظام الكامل، والتكلفة. تُمنح الفئات الأعلى (التحقق، والمصادقة المجتمعية) عن طريق المراجعة — انظر [قواعد لوحة الصدارة](/docs/leaderboard/rules).

## المستوى 2 — صياغة موجّهات موجَّهة

تتمتع أداة الاختبار بدعم كامل **للتوجيه (coaching)**: استبدل موجّه النظام الأساسي بموجّه يحمل معرفة لغوية حقيقية. مرّر `--coaching-file` (أو `--coaching "inline text"` للموجّهات القصيرة) وستستخدم أداة الاختبار نصك كموجّه نظام، وتسجّل **النص الكامل مع تجزئته SHA-256** في كتلة المصدر (provenance) في سجل التشغيل، وتُعلِّم حالة التشغيل بـ **`coached`** (ما لم تحدّد `--prompt` صراحة) — وبذلك تصبح صياغة الموجّهات تجربة قابلة للتكرار والإسناد، ولا يمكن أبداً الخلط بين ملفي توجيه مختلفين، ولا تُخلَط أبداً التشغيلات الموجَّهة مع الأسس الأساسية (naive) على لوحة الصدارة.

مثال عملي للغة الفاروية، باستخدام حقائق تصنيفية لغوية ومدخلات مسرد من [بطاقة اللغة العامة](https://champollion.dev/languages) الخاصة بها:

```text title="coaching-fao.txt"
You are translating Danish into Faroese (føroyskt).

Grammar notes:
- Faroese is a North Germanic V2 language: the finite verb is the second
  constituent of a main clause.
- Nouns inflect for case (nominative, accusative, dative, genitive),
  gender (masculine, feminine, neuter), and number. Make adjectives and
  determiners agree.
- The skerping pattern applies before -gv/-ggj sequences; preserve
  standard orthography including ð (which is silent).

Glossary (use these exact equivalents):
- language -> mál
- island -> oyggj
- weather -> veður

Style: plain register, modern standard orthography. Output only the
Faroese translation, no commentary.
```

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/dan-fao-dev-v1.json
mt-eval run --corpus dan-fao-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Faroese" \
  --coaching-file coaching-fao.txt
```

(اكتب محتوى التوجيه الخاص بك — الحقائق أعلاه توضح *الشكل*: بضع قواعد نحوية عالية التأثير، ومسرد صغير للمصطلحات التي يخطئ فيها النموذج، وتعليمات بشأن السجل اللغوي. بطاقات اللغات على [champollion.dev/languages](https://champollion.dev/languages) تستشهد بمصادر تصنيفية لغوية يمكنك الاستفادة منها.)

قارن مع الأساس الأساسي (naive) باستخدام `mt-eval compare <naive_log> <coached_log>`، وكرّر العملية، وانشر أفضل تشغيل لديك. يُنشر التشغيل بحالة `coached` تلقائياً؛ وإذا أردت أن تعرض لوحة الصدارة اسم طريقة محددة بدلاً من التسمية العامة، فأرفق بطاقة طريقة عند النشر (يقدم مسار النشر معالجاً إرشادياً). التفوق على الأساس الأساسي في زوج لغوي منخفض الموارد بالاعتماد فقط على هندسة الموجّهات هو نتيجة حقيقية قابلة للنشر — انظر دليل [Coached LLM Prompting cookbook](/docs/tutorials/coached-llm-prompting) الكامل للإرشادات التصميمية.

## المستوى 3 — بناء طريقة

المساهمة الأكثر طموحاً: تنفيذ بروتوكول `TranslationMethod` (`translate(entries, config)`) وإخضاع نظام فعلي للاختبار المعياري، وليس مجرد موجّه. تشغّله أداة الاختبار عبر `--method <plugin-dir>` وتُضمّن بطاقة طريقتك في بطاقة التشغيل. أنماط مع أدلة عملية:

- **[FST-gated pipelines](/docs/tutorials/fst-gated-pipeline)** — يُفحص كل كلمة مرشحة بواسطة محلّل صرفي؛ ويعيد النموذج اللغوي الكبير التوليد حتى يجتاز البوابة. مخرجات شبه حتمية مضمونة صرفياً.
- **[Dictionary-augmented generation](/docs/tutorials/dictionary-augmented-llm)** — البحث عن مصطلحات المصدر في معجم ثنائي اللغة وقت الترجمة وتقييد المخرجات.
- [Chained models](/docs/tutorials/chained-models)، [few-shot retrieval](/docs/tutorials/few-shot-prompting)، [back-translation](/docs/tutorials/back-translation)، [rule-based hybrids](/docs/tutorials/rule-based-hybrid)…

تعلن الطرق عن **فئة اعتمادية** (S/O/A1/A2/X — انظر [مواصفات الطرق](/docs/specifications/methods#method-validity-and-dependency-classes)) تصف ما تحتاجه للتشغيل والنقل: خط المعالجة المكتفي ذاتياً هو من الفئة S؛ والخط الذي يستدعي واجهة API لقاموس مرخّص وقت التشغيل هو من الفئة A2. أعلن بصدق — فالفئة تحدد المجال الذي يمكن لطريقتك التنافس فيه، وتخضع بيانات الإعلان (manifests) للتدقيق.

## لماذا يهم هذا أبعد من لوحة الصدارة

كل تشغيل منشور هو دليل مستقل حول جودة الترجمة الآلية لزوج لغوي لا يقيسه المزودون التجاريون. وتعمل قائمة الانتظار أيضاً كسجل عام *للطلب*: أي الأزواج يرى المجتمع أنها تستحق القياس، وكم تبلغ تكلفة التغطية بأسعار API الحالية، وإلى أي مدى تصل الموارد الحاسوبية المتبرَّع بها. عندما نطلب من جهات التمويل دعم المسوحات المنهجية، تكون قائمة الانتظار هذه ومعدل امتلائها هما دليل الطلب.