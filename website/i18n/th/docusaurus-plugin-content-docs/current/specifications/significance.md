---
sidebar_position: 7
title: "การทดสอบนัยสำคัญทางสถิติ"
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
# การทดสอบนัยสำคัญทางสถิติ — ข้อกำหนดการนำไปใช้งาน

> **Codebase เป้าหมาย**: `arena` (โดยเฉพาะ `tester.py` และ `compare.py`)
> **วัตถุประสงค์**: ช่วยให้นักวิจัยสามารถระบุได้ว่าความแตกต่างระหว่าง evaluation run สองรายการนั้นมีนัยสำคัญทางสถิติหรือเป็นเพียง noise
> **ลำดับความสำคัญ**: สูง — นี่คือฟีเจอร์ที่ขาดหายไปและสำคัญที่สุดสำหรับผลลัพธ์ที่สามารถเผยแพร่ได้

---

## เหตุใดเรื่องนี้จึงสำคัญ

เมื่อเปรียบเทียบ run สองรายการ (เช่น Gemini 3.1 Pro chrF++ 42.96 กับ Claude Sonnet chrF++ 41.80 บน 92 รายการ) ในปัจจุบันเราไม่สามารถระบุได้ว่าความแตกต่างนั้นเป็นจริงหรือเป็นเพียง noise ด้วยรายการทดสอบเพียง ~92 รายการ ความแปรปรวนแบบสุ่มสามารถสร้างความแกว่งได้ง่าย 1-2 คะแนน ผู้เชี่ยวชาญจะถามหาการทดสอบนัยสำคัญ เราจำเป็นต้องตอบได้

---

## อัลกอริทึม: Paired Bootstrap Resampling

นี่คือวิธีมาตรฐานที่ใช้โดย SacreBLEU, MT-Lens และ WMT shared tasks เป็นที่เข้าใจดีในหมู่นักวิจัย MT และให้ผลลัพธ์ที่น่าเชื่อถือ

### หลักการทำงาน

กำหนดให้ระบบ A และ B ถูกประเมินบนรายการทดสอบ N รายการชุดเดียวกัน:

1. คำนวณความแตกต่างของ metric จริง: `Δ = metric(A) - metric(B)`
2. ทำซ้ำ `n_bootstrap` ครั้ง (ค่าเริ่มต้น 1000):
   a. สุ่มตัวอย่าง N รายการ **แบบคืนที่** จากชุดทดสอบร่วม
   b. คำนวณ metric สำหรับทั้ง A และ B บน bootstrap sample นี้
   c. คำนวณ bootstrap difference: `Δ_boot = metric(A_boot) - metric(B_boot)`
3. p-value = สัดส่วนของ bootstrap sample ที่ `Δ_boot` มีเครื่องหมายตรงข้ามกับ `Δ`
4. หาก p-value < α (ค่าเริ่มต้น 0.05) ความแตกต่างนั้นมีนัยสำคัญทางสถิติ

### คุณสมบัติสำคัญ

- **Paired**: ทั้งสองระบบถูกประเมินบน bootstrap sample เดียวกัน เพื่อรักษาความสัมพันธ์ระดับรายการ
- **Non-parametric**: ไม่มีข้อสมมติเกี่ยวกับการแจกแจงของคะแนน
- **Standard**: นี่คือสิ่งที่ `sacrebleu --paired-bs` ทำภายใต้ฝากระโปรง

---

## สำคัญ: sacrebleu เป็น Hard Dependency

sacrebleu ปัจจุบันอยู่ภายใต้ `[project.optional-dependencies]` และถูกป้องกันด้วย `try/except` ใน `tester.py` **ควรเปลี่ยนแปลงสิ่งนี้** เครื่องมือ MT eval harness ที่ไม่สามารถคำนวณ chrF++ หรือ BLEU ได้ ไม่ถือเป็น MT eval harness sacrebleu ควร:

1. ย้ายไปยัง `[project.dependencies]` ใน `pyproject.toml`
2. Import โดยตรงใน `tester.py` (ลบ guard `try/except HAS_SACREBLEU` ออก)
3. Import โดยตรงใน module `significance.py` ใหม่

เส้นทาง conditional `HAS_SACREBLEU` ใน `tester.py` ควรถูกลบออก — เพราะทำให้โค้ดซับซ้อนขึ้นสำหรับสถานการณ์ (การรันโดยไม่มี sacrebleu) ที่ไม่ควรรองรับ

---

## แผนการนำไปใช้งาน

### 1. เลื่อน sacrebleu เป็น hard dependency

**`pyproject.toml`**: ย้าย `sacrebleu>=2.3` จาก `[project.optional-dependencies].metrics` ไปยัง `[project.dependencies]`

**`tester.py`**: แทนที่:
```python
# Optional: sacrebleu for chrF++ and BLEU
try:
    from sacrebleu.metrics import CHRF, BLEU
    HAS_SACREBLEU = True
except ImportError:
    HAS_SACREBLEU = False
```
ด้วย:
```python
from sacrebleu.metrics import CHRF, BLEU
```

ลบ guard `if HAS_SACREBLEU:` ทั้งหมดออกจาก `tester.py`

---

### 2. Module ใหม่: `mt_eval_harness/significance.py`

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

### 3. ฟังก์ชัน metric ในตัว

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

### 4. การผสานรวมเข้ากับ `compare.py`

`compare.py` ที่มีอยู่แล้วทำการเปรียบเทียบ TestReport หลายรายการแบบ side-by-side อยู่แล้ว เพิ่มการทดสอบนัยสำคัญ:

```python
# In compare_reports(), after computing deltas:
if len(reports) == 2:
    sig_results = run_significance_tests(reports[0], reports[1])
    comparison["significance"] = [asdict(r) for r in sig_results]
```

เมื่อเปรียบเทียบ report มากกว่า 2 รายการ ให้รันการทดสอบนัยสำคัญแบบ pairwise สำหรับทุกคู่ เก็บผลลัพธ์โดยใช้คีย์ `"(run_a_id, run_b_id)"`

### 5. การผสานรวมกับ CLI

เพิ่ม flag `--significance` ให้กับ `mt-eval compare`:

```bash
# Compare two runs with significance testing
mt-eval compare report_a.json report_b.json --significance

# Custom bootstrap count
mt-eval compare report_a.json report_b.json --significance --n-bootstrap 5000
```

นอกจากนี้ควรพิจารณาคำสั่งแบบ standalone:

```bash
# Quick significance check between two reports
mt-eval significance report_a.json report_b.json
```

### 6. รูปแบบผลลัพธ์

**ผลลัพธ์บน Console:**
```
  Significance Tests (paired bootstrap, n=1000, α=0.05):

  Metric              A         B       Δ      p-value  Sig?
  ─────────────────── ──────── ──────── ─────── ──────── ────
  corpus_chrf         42.96    41.80    +1.16   0.142    No
  exact_match_rate     0.198    0.185   +0.013  0.381    No
  corpus_bleu          6.80     3.81    +2.99   0.018    Yes *
```

**ผลลัพธ์ JSON** (เพิ่มใน comparison report):
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

### 7. การผสานรวมกับ Dashboard

หากข้อมูลนัยสำคัญมีอยู่ใน comparison JSON dashboard ควรแสดงผล โดยแสดงแถวในตารางเปรียบเทียบพร้อมตัวบ่งชี้นัยสำคัญ (เช่น `*` สำหรับ p < 0.05, `**` สำหรับ p < 0.01) นี่เป็น nice-to-have ไม่ใช่สิ่งที่บล็อกการพัฒนา

---

## กรณีขอบและการตรวจสอบ

1. **รายการไม่ตรงกัน**: TestReport ทั้งสองต้องมี entry ID เดียวกัน หากไม่ตรงกัน (เช่น รายการหนึ่งรันบน subset) ให้ทดสอบนัยสำคัญเฉพาะบน intersection เท่านั้น และแจ้งเตือนเกี่ยวกับรายการที่ถูกยกเว้น

2. **รายการน้อยเกินไป**: หาก N < 10 ให้แจ้งเตือนว่าการทดสอบนัยสำคัญไม่น่าเชื่อถือเมื่อมีรายการน้อยมาก ยังคงรันการทดสอบ แต่พิมพ์คำเตือน

3. **คะแนนเหมือนกัน**: หากทั้งสองระบบให้ผลลัพธ์ต่อรายการเหมือนกัน p_value ควรเป็น 1.0 (ไม่มีความแตกต่างเลย)

4. **Plugin metrics**: module นัยสำคัญควรทดสอบ plugin metric ใดก็ตามที่ปรากฏใน report ทั้งสอง ใช้แนวทางทั่วไป: หาก report ทั้งสองมี `plugin_metrics.crk_fst_validity.avg_fst_validity` ให้ทดสอบ

5. **การทำซ้ำได้**: seed ของ RNG ต้องถูกบันทึกในผลลัพธ์เพื่อให้ผลลัพธ์สามารถทำซ้ำได้อย่างแม่นยำ ค่าเริ่มต้นคือ 12345 (ตามแบบแผนของ SacreBLEU)

---

## สิ่งที่ไม่ควรสร้าง

- **ไม่มีนัยสำคัญ COMET แยกต่างหาก**: COMET ถูกผสานรวมเป็น corpus metric ผ่าน `metrics_comet.py` แล้ว Bootstrap CI ถูกคำนวณบนคะแนน COMET เช่นเดียวกับ chrF++/BLEU สำหรับนัยสำคัญ COMET แบบ pairwise ระหว่างสองระบบ ให้ใช้ `comet-compare` จาก Unbabel
- **ไม่มีการวิเคราะห์แบบ Bayesian**: ยึดถือ frequentist bootstrap เพราะนั่นคือสิ่งที่ชุมชน MT คาดหวังและเข้าใจ
- **ไม่มีการแก้ไขการทดสอบหลายรายการ**: เมื่อทดสอบ metric หลายรายการ ไม่ต้องใช้การแก้ไขแบบ Bonferroni หรือที่คล้ายกัน แบบแผนในการประเมิน MT คือการรายงาน p-value ดิบต่อ metric และให้ผู้อ่านตีความเอง

---

## ไฟล์ที่ต้องแก้ไข

| ไฟล์ | การเปลี่ยนแปลง |
|---|---|
| `pyproject.toml` | ย้าย sacrebleu จาก optional เป็น hard dependency |
| `mt_eval_harness/tester.py` | ลบ guard `HAS_SACREBLEU` ออก, import โดยตรง |
| `mt_eval_harness/significance.py` | **[ใหม่]** การนำไปใช้งานหลัก |
| `mt_eval_harness/__init__.py` | Export `SignificanceResult`, `paired_bootstrap` |
| `mt_eval_harness/compare.py` | เชื่อมต่อการทดสอบนัยสำคัญเข้ากับการเปรียบเทียบ report |
| `mt_eval_harness/cli.py` | เพิ่ม flag `--significance` และ `--n-bootstrap` |
| `mt_eval_harness/dashboard.py` | แสดงนัยสำคัญในตารางเปรียบเทียบ (nice-to-have) |
| `tests/test_significance.py` | **[ใหม่]** Unit tests |

---

## ข้อกำหนดการทดสอบ

1. **Deterministic ด้วย seed**: input เดียวกัน + seed เดียวกัน = p-value เดียวกัน ทุกครั้ง
2. **Known-answer test**: ชุดผลลัพธ์สองชุดที่เหมือนกัน → p_value = 1.0
3. **Known-significant test**: สร้างชุดผลลัพธ์สองชุดที่ชุดหนึ่งดีกว่าอย่างชัดเจน (เช่น exact match ทั้งหมด กับ miss ทั้งหมด) → p_value ≈ 0.0
4. **Mismatched IDs**: ควร raise ValueError หรือแจ้งเตือนและคำนวณบน intersection
5. **Input ว่างเปล่า**: ควรจัดการได้อย่างเหมาะสม (คืนค่า p_value = 1.0 หรือ raise)

---

## Confidence Intervals (ฟีเจอร์เสริม)

> **สถานะ**: ✅ นำไปใช้งานแล้วใน `confidence.py`

Confidence intervals (CI) ตอบคำถามที่แตกต่างจากการทดสอบนัยสำคัญ:

- **การทดสอบนัยสำคัญ** (`significance.py`): "ความแตกต่างระหว่างระบบ A และระบบ B เป็นจริงหรือไม่?"
- **Confidence intervals** (`confidence.py`): "คะแนนของระบบนี้มีความไม่แน่นอนมากเพียงใดในตัวมันเอง?"

### การนำไปใช้งาน: `confidence.py`

ใช้วิธี percentile bootstrap resampling เดียวกับการทดสอบนัยสำคัญ:

| พารามิเตอร์ | ค่า | เหตุผล |
|---|---|---|
| `n_bootstrap` | 1000 | ค่าเริ่มต้นของ SacreBLEU, แบบแผน WMT 2024 |
| `seed` | 12345 | seed เริ่มต้นของ SacreBLEU สำหรับการทำซ้ำได้ |
| `alpha` | 0.05 | ระดับความเชื่อมั่นมาตรฐาน 95% |
| Method | Percentile bootstrap | Koehn (2004), Efron (1979) |

### สิ่งที่ได้รับ CI

metric ระดับ corpus ทั้งหมดที่คำนวณโดย harness:
- `corpus_chrf` (คะแนน chrF++)
- `corpus_bleu` (คะแนน BLEU)
- `exact_match_rate` (0.0–1.0)

### CLI Flags

```bash
# Default: CIs are computed automatically
mt-eval test run_log.json

# Skip CI computation (faster, for quick iteration)
mt-eval test run_log.json --no-ci

# More bootstrap iterations (more precise, slower)
mt-eval test run_log.json --n-bootstrap-ci 2000
```

### คำเตือนสำหรับตัวอย่างขนาดเล็ก

เมื่อมีรายการ N < 30 รายการ module จะส่งคำเตือนว่า CI อาจมี coverage ที่ไม่ดี Bootstrap ไม่สามารถสร้างข้อมูลที่ไม่มีอยู่ในตัวอย่างได้ — เมื่อมีรายการน้อยมาก ช่วงความเชื่อมั่นจะกว้าง ซึ่งสะท้อนความไม่แน่นอนสูงได้อย่างถูกต้อง

### การผสานรวม COMET

COMET (`metrics_comet.py`) ถูกผสานรวมเป็น metric ระดับ first-class แล้ว:
- Model: `Unbabel/wmt22-comet-da` (model อ้างอิงที่ชนะ WMT 2022)
- คำนวณโดยอัตโนมัติเมื่อติดตั้ง `unbabel-comet`
- คะแนนต่อรายการถูกเก็บไว้ใน TestReport entries
- การตรวจจับภาษา low-resource ผ่านตาราง XLM-R coverage
- Optional dependency: `pip install mt-eval-harness[comet]`

### Supabase Migration

คอลัมน์ใหม่ที่เพิ่มในตาราง `run_cards`:
- `comet_score` (FLOAT8, nullable)
- `corpus_bleu` (FLOAT8, nullable)
- `chrf_ci_lower` / `chrf_ci_upper` (FLOAT8, nullable)
- `exact_match_ci_lower` / `exact_match_ci_upper` (FLOAT8, nullable)

ดู `migrations/001_add_comet_and_ci_columns.sql` สำหรับ migration script