---
sidebar_position: 7
title: "اختبار الدلالة الإحصائية"
slug: '/specifications/significance'
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The scores these tests protect"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "Where significance gates what ranks"
---
# اختبار الدلالة الإحصائية — مواصفات التنفيذ

> **قاعدة الشيفرة المستهدفة**: `arena` (وتحديدًا `tester.py` و `compare.py`)
> **الغرض**: تمكين الباحثين من تحديد ما إذا كان الفرق بين تشغيلَي تقييم ذا دلالة إحصائية أم مجرد ضوضاء.
> **الأولوية**: عالية — هذه هي أهم ميزة مفقودة على الإطلاق للحصول على نتائج قابلة للنشر.

---

## لماذا هذا الأمر مهم

عند مقارنة تشغيلَين (مثلًا، Gemini 3.1 Pro بدرجة chrF++ تساوي 42.96 مقابل Claude Sonnet بدرجة chrF++ تساوي 41.80 على 92 مدخلة)، لا يمكننا حاليًا الجزم بما إذا كان الفرق حقيقيًا أم ضوضاء. مع وجود ~92 مدخلة اختبار فقط، يمكن للتباين العشوائي أن يُنتج بسهولة تقلبات بمقدار نقطة أو نقطتين. سيطلب الخبراء اختبارات الدلالة. وعلينا أن نكون قادرين على الإجابة.

---

## الخوارزمية: إعادة المعاينة بطريقة Bootstrap المزدوجة (Paired Bootstrap Resampling)

هذه هي الطريقة القياسية المستخدمة في SacreBLEU وMT-Lens والمهام المشتركة في WMT. وهي طريقة مفهومة جيدًا لدى باحثي الترجمة الآلية وتُنتج نتائج يثقون بها.

### كيف تعمل

بافتراض وجود نظامين A وB تم تقييمهما على نفس مدخلات الاختبار البالغ عددها N:

1. احسب الفرق الفعلي في المقياس: `Δ = metric(A) - metric(B)`
2. كرّر `n_bootstrap` مرة (القيمة الافتراضية 1000):
   a. اسحب عينة من N مدخلة **مع الإرجاع** من مجموعة الاختبار المشتركة
   b. احسب المقياس لكل من A وB على عينة bootstrap هذه
   c. احسب فرق bootstrap: `Δ_boot = metric(A_boot) - metric(B_boot)`
3. القيمة الاحتمالية (p-value) = نسبة عينات bootstrap التي تكون فيها إشارة `Δ_boot` معاكسة لإشارة `Δ`
4. إذا كانت القيمة الاحتمالية < α (القيمة الافتراضية 0.05)، فإن الفرق ذو دلالة إحصائية

### الخصائص الرئيسية

- **مزدوجة (Paired)**: يتم تقييم كلا النظامين على نفس عينة bootstrap، مما يحافظ على الترابط على مستوى المدخلات
- **لا معلمية (Non-parametric)**: لا تفترض أي توزيع معين للدرجات
- **قياسية**: هذا بالضبط ما يفعله `sacrebleu --paired-bs` داخليًا

---

## هام: sacrebleu تبعية إلزامية

تُدرج sacrebleu حاليًا ضمن `[project.optional-dependencies]` ومحمية بواسطة `try/except` في `tester.py`. **ينبغي تغيير هذا.** فمنصة تقييم للترجمة الآلية لا تستطيع حساب chrF++ أو BLEU ليست منصة تقييم للترجمة الآلية. ينبغي أن تكون sacrebleu:

1. منقولة إلى `[project.dependencies]` في `pyproject.toml`
2. مستوردة مباشرة في `tester.py` (مع إزالة حارس `try/except HAS_SACREBLEU`)
3. مستوردة مباشرة في الوحدة الجديدة `significance.py`

ينبغي إزالة المسارات الشرطية `HAS_SACREBLEU` في `tester.py` — فهي تجعل الشيفرة أكثر تعقيدًا من أجل سيناريو (التشغيل بدون sacrebleu) لا ينبغي دعمه أصلًا.

---

## خطة التنفيذ

### 1. ترقية sacrebleu إلى تبعية إلزامية

**`pyproject.toml`**: انقل `sacrebleu>=2.3` من `[project.optional-dependencies].metrics` إلى `[project.dependencies]`.

**`tester.py`**: استبدل:
```python
# Optional: sacrebleu for chrF++ and BLEU
try:
    from sacrebleu.metrics import CHRF, BLEU
    HAS_SACREBLEU = True
except ImportError:
    HAS_SACREBLEU = False
```
بـ:
```python
from sacrebleu.metrics import CHRF, BLEU
```

أزل جميع حواجز `if HAS_SACREBLEU:` في كافة أنحاء `tester.py`.

---

### 2. وحدة جديدة: `mt_eval_harness/significance.py`

```python
"""
Statistical significance testing via paired bootstrap resampling.

Standard method used by WMT shared tasks, SacreBLEU, and MT-Lens.
Compares two runs on the same corpus to determine if the performance
difference is statistically significant.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from sacrebleu.metrics import CHRF, BLEU


@dataclass
class SignificanceResult:
    """Result of a paired bootstrap significance test."""
    metric_name: str           # e.g., "corpus_chrf", "exact_match_rate"
    system_a_score: float      # Score for system A
    system_b_score: float      # Score for system B
    delta: float               # A - B
    p_value: float             # Two-sided p-value
    n_bootstrap: int           # Number of bootstrap iterations
    confidence_level: float    # 1 - alpha
    significant: bool          # p_value < alpha
    winner: str | None         # "A", "B", or None if not significant
    ci_lower: float            # Lower bound of 95% CI on the delta
    ci_upper: float            # Upper bound of 95% CI on the delta


def paired_bootstrap(
    entries_a: list[dict],
    entries_b: list[dict],
    metric_fn: callable,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 12345,
    metric_name: str = "metric",
) -> SignificanceResult:
    """Run paired bootstrap resampling significance test.

    Args:
        entries_a: Per-entry results from system A (from TestReport["entries"])
        entries_b: Per-entry results from system B (must be same length, same IDs)
        metric_fn: Function(list[dict]) -> float that computes the corpus-level
                   metric from a list of entry dicts. Must handle the entry format
                   from TestReport.
        n_bootstrap: Number of bootstrap iterations (1000 is standard)
        alpha: Significance level (0.05 = 95% confidence)
        seed: RNG seed for reproducibility (12345 matches SacreBLEU default)
        metric_name: Human-readable name for the metric being tested

    Returns:
        SignificanceResult with all fields populated.

    Raises:
        ValueError: If entries_a and entries_b have different lengths or IDs.
    """
    ...
```

### 3. دوال المقاييس المدمجة

```python
def exact_match_rate(entries: list[dict]) -> float:
    """Compute exact match rate from a list of entry dicts."""
    non_error = [e for e in entries if not e.get("error")]
    if not non_error:
        return 0.0
    exact = sum(1 for e in non_error if e.get("exact_match"))
    return exact / len(non_error)


def corpus_chrf(entries: list[dict]) -> float:
    """Compute corpus-level chrF++ from a list of entry dicts."""
    chrf = CHRF(word_order=2)
    refs = [e["expected"] for e in entries if e.get("expected", "").strip()]
    hyps = [e["predicted"] if e.get("predicted", "").strip() else "EMPTY"
            for e in entries if e.get("expected", "").strip()]
    if not refs:
        return 0.0
    return chrf.corpus_score(hyps, [refs]).score


def corpus_bleu(entries: list[dict]) -> float:
    """Compute corpus-level BLEU from a list of entry dicts."""
    bleu = BLEU()
    refs = [e["expected"] for e in entries if e.get("expected", "").strip()]
    hyps = [e["predicted"] if e.get("predicted", "").strip() else "EMPTY"
            for e in entries if e.get("expected", "").strip()]
    if not refs:
        return 0.0
    return bleu.corpus_score(hyps, [refs]).score
```

### 4. التكامل مع `compare.py`

تقوم `compare.py` الحالية بالفعل بمقارنة جنبًا إلى جنب لعدة تقارير TestReports. أضف اختبار الدلالة:

```python
# In compare_reports(), after computing deltas:
if len(reports) == 2:
    sig_results = run_significance_tests(reports[0], reports[1])
    comparison["significance"] = [asdict(r) for r in sig_results]
```

عند مقارنة أكثر من تقريرين، شغّل اختبارات الدلالة الثنائية لجميع الأزواج. خزّن النتائج مفهرسة بواسطة `"(run_a_id, run_b_id)"`.

### 5. التكامل مع واجهة سطر الأوامر (CLI)

أضف خيار `--significance` إلى `mt-eval compare`:

```bash
# Compare two runs with significance testing
mt-eval compare report_a.json report_b.json --significance

# Custom bootstrap count
mt-eval compare report_a.json report_b.json --significance --n-bootstrap 5000
```

ضع في الاعتبار أيضًا أمرًا مستقلًا:

```bash
# Quick significance check between two reports
mt-eval significance report_a.json report_b.json
```

### 6. صيغة المخرجات

**مخرجات وحدة التحكم:**
```
  Significance Tests (paired bootstrap, n=1000, α=0.05):

  Metric              A         B       Δ      p-value  Sig?
  ─────────────────── ──────── ──────── ─────── ──────── ────
  corpus_chrf         42.96    41.80    +1.16   0.142    No
  exact_match_rate     0.198    0.185   +0.013  0.381    No
  corpus_bleu          6.80     3.81    +2.99   0.018    Yes *
```

**مخرجات JSON** (تُضاف إلى تقرير المقارنة):
```json
{
  "significance": [
    {
      "metric_name": "corpus_chrf",
      "system_a_score": 42.96,
      "system_b_score": 41.80,
      "delta": 1.16,
      "p_value": 0.142,
      "n_bootstrap": 1000,
      "confidence_level": 0.95,
      "significant": false,
      "winner": null,
      "ci_lower": -0.85,
      "ci_upper": 3.12
    }
  ]
}
```

### 7. التكامل مع لوحة المعلومات

إذا كانت بيانات الدلالة موجودة في ملف JSON الخاص بالمقارنة، فينبغي أن تعرضها لوحة المعلومات. اعرض صفًا في جدول المقارنة مع مؤشرات الدلالة (مثل `*` عندما تكون p < 0.05، و`**` عندما تكون p < 0.01). هذه ميزة مرغوبة وليست شرطًا أساسيًا.

---

## الحالات الحدّية والتحقق

1. **مدخلات غير متطابقة**: يجب أن يحتوي تقريرا TestReports على نفس معرّفات المدخلات. إذا لم يكن الأمر كذلك (مثلًا، أحدهما شُغّل على مجموعة جزئية)، فاختبر الدلالة فقط على التقاطع. حذّر بشأن المدخلات المستبعدة.

2. **مدخلات قليلة جدًا**: إذا كان N < 10، فحذّر من أن اختبارات الدلالة غير موثوقة مع هذا العدد القليل من المدخلات. شغّلها مع ذلك، ولكن اطبع التحذير.

3. **درجات متطابقة**: إذا أنتج كلا النظامين نتائج متطابقة لكل مدخلة، فينبغي أن تكون p_value تساوي 1.0 (لا يوجد فرق على الإطلاق).

4. **مقاييس الإضافات (Plugins)**: ينبغي أن تختبر وحدة الدلالة أيضًا أي مقاييس إضافات تظهر في كلا التقريرين. استخدم نهجًا عامًا: إذا كان كلا التقريرين يحتويان على `plugin_metrics.crk_fst_validity.avg_fst_validity`، فاختبره.

5. **قابلية إعادة الإنتاج**: يجب تسجيل بذرة مولّد الأرقام العشوائية (RNG seed) في المخرجات بحيث تكون النتائج قابلة لإعادة الإنتاج بدقة. القيمة الافتراضية 12345 (بما يتوافق مع اصطلاح SacreBLEU).

---

## ما لا ينبغي بناؤه

- **لا اختبار دلالة منفصل لـ COMET**: أصبح COMET الآن مدمجًا كمقياس على مستوى المتن (corpus) عبر `metrics_comet.py`. تُحسب فترات الثقة بطريقة bootstrap على درجات COMET تمامًا كما هو الحال مع chrF++/BLEU. لاختبار دلالة COMET الثنائية بين نظامين، استخدم `comet-compare` من Unbabel.
- **لا تحليل بايزي (Bayesian)**: التزم بطريقة bootstrap التكرارية (frequentist). فهي ما يتوقعه ويفهمه مجتمع الترجمة الآلية.
- **لا تصحيح للاختبارات المتعددة**: عند اختبار عدة مقاييس، لا تطبّق تصحيح Bonferroni أو ما شابهه. فالعُرف في تقييم الترجمة الآلية هو الإبلاغ عن القيم الاحتمالية الخام لكل مقياس وترك التفسير للقارئ.

---

## الملفات المطلوب تعديلها

| الملف | التغيير |
|---|---|
| `pyproject.toml` | نقل sacrebleu من تبعية اختيارية إلى تبعية إلزامية |
| `mt_eval_harness/tester.py` | إزالة حواجز `HAS_SACREBLEU` والاستيراد المباشر |
| `mt_eval_harness/significance.py` | **[جديد]** التنفيذ الأساسي |
| `mt_eval_harness/__init__.py` | تصدير `SignificanceResult` و `paired_bootstrap` |
| `mt_eval_harness/compare.py` | ربط اختبارات الدلالة بمقارنة التقارير |
| `mt_eval_harness/cli.py` | إضافة خياري `--significance` و `--n-bootstrap` |
| `mt_eval_harness/dashboard.py` | عرض الدلالة في جدول المقارنة (ميزة مرغوبة) |
| `tests/test_significance.py` | **[جديد]** اختبارات الوحدة |

---

## متطلبات الاختبار

1. **حتمية مع البذرة**: نفس المدخلات + نفس البذرة = نفس القيمة الاحتمالية، في كل مرة
2. **اختبار بإجابة معروفة**: مجموعتا نتائج متطابقتان ← p_value = 1.0
3. **اختبار بدلالة معروفة**: أنشئ مجموعتي نتائج تكون إحداهما أفضل بوضوح (مثلًا، جميعها تطابقات تامة مقابل جميعها إخفاقات) ← p_value ≈ 0.0
4. **معرّفات غير متطابقة**: ينبغي إثارة ValueError أو التحذير والحساب على التقاطع
5. **مدخلات فارغة**: ينبغي التعامل معها بسلاسة (إرجاع p_value = 1.0 أو إثارة استثناء)

---

## فترات الثقة (ميزة مرافقة)

> **الحالة**: ✅ تم التنفيذ في `confidence.py`

تجيب فترات الثقة (CIs) عن سؤال مختلف عن اختبار الدلالة:

- **اختبار الدلالة** (`significance.py`): "هل الفرق بين النظام A والنظام B حقيقي؟"
- **فترات الثقة** (`confidence.py`): "ما مدى عدم اليقين في درجة هذا النظام بمفرده؟"

### التنفيذ: `confidence.py`

يستخدم نفس طريقة إعادة المعاينة بطريقة percentile bootstrap المستخدمة في اختبار الدلالة:

| المعامل | القيمة | المسوّغ |
|---|---|---|
| `n_bootstrap` | 1000 | القيمة الافتراضية لـ SacreBLEU، اصطلاح WMT 2024 |
| `seed` | 12345 | البذرة الافتراضية لـ SacreBLEU لضمان قابلية إعادة الإنتاج |
| `alpha` | 0.05 | مستوى الثقة القياسي 95% |
| الطريقة | Percentile bootstrap | Koehn (2004), Efron (1979) |

### المقاييس التي تحصل على فترات ثقة

جميع المقاييس على مستوى المتن التي تحسبها المنصة:
- `corpus_chrf` (درجة chrF++)
- `corpus_bleu` (درجة BLEU)
- `exact_match_rate` (0.0–1.0)

### خيارات واجهة سطر الأوامر

```bash
# Default: CIs are computed automatically
mt-eval test run_log.json

# Skip CI computation (faster, for quick iteration)
mt-eval test run_log.json --no-ci

# More bootstrap iterations (more precise, slower)
mt-eval test run_log.json --n-bootstrap-ci 2000
```

### تحذير العينات الصغيرة

عندما يكون N < 30 مدخلة، تُصدر الوحدة تحذيرًا بأن فترات الثقة قد تكون ذات تغطية ضعيفة. لا يمكن لطريقة bootstrap أن تُنشئ معلومات غير موجودة في العينة — فمع عدد قليل جدًا من المدخلات، ستكون الفترات واسعة، مما يعكس بشكل صحيح درجة عالية من عدم اليقين.

### تكامل COMET

أصبح COMET (`metrics_comet.py`) الآن مدمجًا كمقياس من الدرجة الأولى:
- النموذج: `Unbabel/wmt22-comet-da` (النموذج المعتمد على المراجع الفائز في WMT 2022)
- يُحسب تلقائيًا عند تثبيت `unbabel-comet`
- تُخزّن الدرجات لكل مدخلة في مدخلات TestReport
- اكتشاف اللغات منخفضة الموارد عبر جدول تغطية XLM-R
- تبعية اختيارية: `pip install mt-eval-harness[comet]`

### ترحيل Supabase

أعمدة جديدة أُضيفت إلى جدول `run_cards`:
- `comet_score` (FLOAT8، قابل لقيمة فارغة)
- `corpus_bleu` (FLOAT8، قابل لقيمة فارغة)
- `chrf_ci_lower` / `chrf_ci_upper` (FLOAT8، قابل لقيمة فارغة)
- `exact_match_ci_lower` / `exact_match_ci_upper` (FLOAT8، قابل لقيمة فارغة)

انظر `migrations/001_add_comet_and_ci_columns.sql` للاطلاع على نص الترحيل البرمجي.