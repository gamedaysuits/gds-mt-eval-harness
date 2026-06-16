---
sidebar_position: 7
title: "Kiểm định ý nghĩa thống kê"
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
# Kiểm định ý nghĩa thống kê — Đặc tả triển khai

> **Mã nguồn mục tiêu**: `arena` (cụ thể là `tester.py` và `compare.py`)
> **Mục đích**: Cho phép các nhà nghiên cứu xác định xem sự khác biệt giữa hai lượt đánh giá có ý nghĩa thống kê hay chỉ là nhiễu.
> **Độ ưu tiên**: Cao — đây là tính năng quan trọng nhất còn thiếu để có thể công bố kết quả.

---

## Tại sao điều này lại quan trọng

Khi so sánh hai lượt chạy (ví dụ: Gemini 3.1 Pro chrF++ 42.96 so với Claude Sonnet chrF++ 41.80 trên 92 bản ghi), hiện tại chúng ta không thể khẳng định sự khác biệt đó là thực tế hay chỉ là nhiễu. Với chỉ khoảng 92 bản ghi thử nghiệm, biến động ngẫu nhiên có thể dễ dàng tạo ra mức chênh lệch 1-2 điểm. Các chuyên gia sẽ yêu cầu kiểm định ý nghĩa thống kê. Chúng ta cần phải trả lời được câu hỏi này.

---

## Thuật toán: Tái lấy mẫu bootstrap theo cặp

Đây là phương pháp tiêu chuẩn được sử dụng bởi SacreBLEU, MT-Lens và các tác vụ chung của WMT. Phương pháp này đã rất quen thuộc với các nhà nghiên cứu dịch máy (MT) và mang lại kết quả mà họ tin cậy.

### Cách thức hoạt động

Cho hai hệ thống A và B được đánh giá trên cùng N bản ghi thử nghiệm:

1. Tính toán sự khác biệt thực tế của chỉ số: `Δ = metric(A) - metric(B)`
2. Lặp lại `n_bootstrap` lần (mặc định là 1000):
   a. Lấy mẫu N bản ghi **có hoàn lại** từ tập thử nghiệm chung
   b. Tính toán chỉ số cho cả A và B trên mẫu bootstrap này
   c. Tính toán sự khác biệt bootstrap: `Δ_boot = metric(A_boot) - metric(B_boot)`
3. Giá trị p-value = tỷ lệ các mẫu bootstrap mà tại đó `Δ_boot` có dấu ngược lại với `Δ`
4. Nếu p-value < α (mặc định là 0.05), sự khác biệt có ý nghĩa thống kê

### Các đặc tính chính

- **Theo cặp (Paired)**: Cả hai hệ thống đều được đánh giá trên cùng một mẫu bootstrap, giúp bảo toàn mối tương quan ở cấp độ bản ghi
- **Phi tham số (Non-parametric)**: Không có giả định nào về phân phối của các điểm số
- **Tiêu chuẩn**: Đây chính xác là những gì `sacrebleu --paired-bs` thực hiện bên dưới

---

## Quan trọng: sacrebleu là một phụ thuộc bắt buộc

sacrebleu hiện đang được liệt kê trong `[project.optional-dependencies]` và được bảo vệ bởi `try/except` trong `tester.py`. **Điều này cần phải được thay đổi.** Một khung đánh giá dịch máy (MT eval harness) mà không thể tính toán chrF++ hoặc BLEU thì không phải là một khung đánh giá dịch máy thực thụ. sacrebleu cần phải được:

1. Chuyển sang `[project.dependencies]` trong `pyproject.toml`
2. Import trực tiếp trong `tester.py` (loại bỏ phần bảo vệ `try/except HAS_SACREBLEU`)
3. Import trực tiếp trong module `significance.py` mới

Các đường dẫn điều kiện `HAS_SACREBLEU` trong `tester.py` nên được loại bỏ — chúng làm cho mã nguồn trở nên phức tạp hơn đối với một kịch bản (chạy mà không có sacrebleu) vốn không nên được hỗ trợ.

---

## Kế hoạch triển khai

### 1. Nâng cấp sacrebleu thành phụ thuộc bắt buộc

**`pyproject.toml`**: Di chuyển `sacrebleu>=2.3` từ `[project.optional-dependencies].metrics` sang `[project.dependencies]`.

**`tester.py`**: Thay thế:
```python
# Optional: sacrebleu for chrF++ and BLEU
try:
    from sacrebleu.metrics import CHRF, BLEU
    HAS_SACREBLEU = True
except ImportError:
    HAS_SACREBLEU = False
```
Bằng:
```python
from sacrebleu.metrics import CHRF, BLEU
```

Loại bỏ tất cả các phần bảo vệ `if HAS_SACREBLEU:` trong toàn bộ `tester.py`.

---

### 2. Module mới: `mt_eval_harness/significance.py`

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

### 3. Các hàm chỉ số tích hợp sẵn

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

### 4. Tích hợp vào `compare.py`

`compare.py` hiện tại đã thực hiện so sánh song song nhiều TestReports. Thêm kiểm định ý nghĩa thống kê:

```python
# In compare_reports(), after computing deltas:
if len(reports) == 2:
    sig_results = run_significance_tests(reports[0], reports[1])
    comparison["significance"] = [asdict(r) for r in sig_results]
```

Khi so sánh nhiều hơn 2 báo cáo, hãy chạy các kiểm định ý nghĩa thống kê theo từng cặp cho tất cả các cặp. Lưu trữ kết quả với khóa là `"(run_a_id, run_b_id)"`.

### 5. Tích hợp CLI

Thêm cờ `--significance` vào `mt-eval compare`:

```bash
# Compare two runs with significance testing
mt-eval compare report_a.json report_b.json --significance

# Custom bootstrap count
mt-eval compare report_a.json report_b.json --significance --n-bootstrap 5000
```

Đồng thời cân nhắc một lệnh độc lập:

```bash
# Quick significance check between two reports
mt-eval significance report_a.json report_b.json
```

### 6. Định dạng đầu ra

**Đầu ra console:**
```
  Significance Tests (paired bootstrap, n=1000, α=0.05):

  Metric              A         B       Δ      p-value  Sig?
  ─────────────────── ──────── ──────── ─────── ──────── ────
  corpus_chrf         42.96    41.80    +1.16   0.142    No
  exact_match_rate     0.198    0.185   +0.013  0.381    No
  corpus_bleu          6.80     3.81    +2.99   0.018    Yes *
```

**Đầu ra JSON** (được thêm vào báo cáo so sánh):
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

### 7. Tích hợp bảng điều khiển (Dashboard)

Nếu dữ liệu ý nghĩa thống kê có sẵn trong JSON so sánh, bảng điều khiển sẽ hiển thị dữ liệu đó. Hiển thị một hàng trong bảng so sánh với các chỉ báo ý nghĩa thống kê (ví dụ: `*` cho p < 0.05, `**` cho p < 0.01). Đây là tính năng bổ sung hữu ích (nice-to-have), không gây nghẽn tiến độ.

---

## Các trường hợp biên và xác thực

1. **Các bản ghi không khớp**: Hai TestReports phải có cùng ID bản ghi. Nếu không khớp (ví dụ: một báo cáo chạy trên một tập con), chỉ kiểm định ý nghĩa thống kê trên phần giao nhau. Đưa ra cảnh báo về các bản ghi bị loại trừ.

2. **Quá ít bản ghi**: Nếu N < 10, hãy cảnh báo rằng các kiểm định ý nghĩa thống kê không đáng tin cậy với số lượng bản ghi ít như vậy. Vẫn chạy kiểm định, nhưng in ra cảnh báo.

3. **Điểm số giống hệt nhau**: Nếu cả hai hệ thống tạo ra kết quả giống hệt nhau trên từng bản ghi, p_value phải là 1.0 (hoàn toàn không có sự khác biệt).

4. **Các chỉ số plugin**: Module kiểm định ý nghĩa thống kê cũng nên kiểm định bất kỳ chỉ số plugin nào xuất hiện trong CẢ HAI báo cáo. Sử dụng phương pháp tiếp cận chung: nếu cả hai báo cáo đều có `plugin_metrics.crk_fst_validity.avg_fst_validity`, hãy tiến hành kiểm định.

5. **Khả năng tái lặp**: Seed của bộ tạo số ngẫu nhiên (RNG seed) phải được ghi lại trong đầu ra để kết quả có thể được tái lặp một cách chính xác. Mặc định là 12345 (khớp với quy ước của SacreBLEU).

---

## Những gì KHÔNG cần xây dựng

- **Không kiểm định ý nghĩa thống kê COMET riêng biệt**: COMET hiện đã được tích hợp dưới dạng chỉ số cấp ngữ liệu (corpus metric) thông qua `metrics_comet.py`. Các khoảng tin cậy (CI) bootstrap được tính toán trên điểm số COMET tương tự như chrF++/BLEU. Đối với kiểm định ý nghĩa thống kê COMET theo cặp giữa hai hệ thống, hãy sử dụng `comet-compare` từ Unbabel.
- **Không phân tích Bayes**: Hãy trung thành với phương pháp bootstrap tần suất (frequentist bootstrap). Đây là những gì cộng đồng dịch máy (MT) mong đợi và hiểu rõ.
- **Không hiệu chỉnh đa kiểm định (multi-test correction)**: Khi kiểm định nhiều chỉ số, không áp dụng hiệu chỉnh Bonferroni hoặc các hiệu chỉnh tương tự. Quy ước trong đánh giá dịch máy là báo cáo các giá trị p-value thô cho từng chỉ số và để người đọc tự diễn giải.

---

## Các tệp cần sửa đổi

| Tệp | Thay đổi |
|---|---|
| `pyproject.toml` | Chuyển sacrebleu từ phụ thuộc tùy chọn sang phụ thuộc bắt buộc |
| `mt_eval_harness/tester.py` | Loại bỏ các phần bảo vệ `HAS_SACREBLEU`, import trực tiếp |
| `mt_eval_harness/significance.py` | **[MỚI]** Triển khai cốt lõi |
| `mt_eval_harness/__init__.py` | Export `SignificanceResult`, `paired_bootstrap` |
| `mt_eval_harness/compare.py` | Tích hợp các kiểm định ý nghĩa thống kê vào việc so sánh báo cáo |
| `mt_eval_harness/cli.py` | Thêm các cờ `--significance` và `--n-bootstrap` |
| `mt_eval_harness/dashboard.py` | Hiển thị ý nghĩa thống kê trong bảng so sánh (tính năng bổ sung hữu ích) |
| `tests/test_significance.py` | **[MỚI]** Unit test |

---

## Yêu cầu kiểm thử

1. **Tính tất định với seed**: Cùng đầu vào + cùng seed = cùng p-value, trong mọi lần chạy
2. **Kiểm thử với kết quả đã biết trước (Known-answer test)**: Hai tập kết quả giống hệt nhau → p_value = 1.0
3. **Kiểm thử với ý nghĩa thống kê đã biết trước (Known-significant test)**: Xây dựng hai tập kết quả trong đó một tập tốt hơn rõ rệt (ví dụ: tất cả đều khớp chính xác so với tất cả đều trượt) → p_value ≈ 0.0
4. **ID không khớp**: Nên ném ra lỗi ValueError hoặc cảnh báo và tính toán trên phần giao nhau
5. **Đầu vào trống**: Nên xử lý một cách mượt mà (trả về p_value = 1.0 hoặc ném ra lỗi)

---

## Khoảng tin cậy (Tính năng đi kèm)

> **Trạng thái**: ✅ ĐÃ TRIỂN KHAI trong `confidence.py`

Khoảng tin cậy (CI) trả lời cho một câu hỏi khác so với kiểm định ý nghĩa thống kê:

- **Kiểm định ý nghĩa thống kê** (`significance.py`): "Sự khác biệt giữa hệ thống A và hệ thống B có thực sự tồn tại?"
- **Khoảng tin cậy** (`confidence.py`): "Mức độ không chắc chắn của điểm số của riêng hệ thống này là bao nhiêu?"

### Triển khai: `confidence.py`

Sử dụng cùng phương pháp tái lấy mẫu bootstrap phân vị như kiểm định ý nghĩa thống kê:

| Tham số | Giá trị | Lý do lựa chọn |
|---|---|---|
| `n_bootstrap` | 1000 | Mặc định của SacreBLEU, quy ước của WMT 2024 |
| `seed` | 12345 | Seed mặc định của SacreBLEU để đảm bảo khả năng tái lặp |
| `alpha` | 0.05 | Mức tin cậy 95% tiêu chuẩn |
| Phương pháp | Bootstrap phân vị | Koehn (2004), Efron (1979) |

### Những gì sẽ có khoảng tin cậy (CI)

Tất cả các chỉ số cấp ngữ liệu được tính toán bởi khung đánh giá:
- `corpus_chrf` (điểm chrF++)
- `corpus_bleu` (điểm BLEU)
- `exact_match_rate` (0.0–1.0)

### Các cờ CLI

```bash
# Default: CIs are computed automatically
mt-eval test run_log.json

# Skip CI computation (faster, for quick iteration)
mt-eval test run_log.json --no-ci

# More bootstrap iterations (more precise, slower)
mt-eval test run_log.json --n-bootstrap-ci 2000
```

### Cảnh báo mẫu nhỏ

Khi N < 30 bản ghi, module sẽ phát ra cảnh báo rằng các khoảng tin cậy (CI) có thể có độ bao phủ kém. Phương pháp bootstrap không thể tạo ra thông tin vốn không tồn tại trong mẫu — với rất ít bản ghi, các khoảng tin cậy sẽ rộng, phản ánh chính xác mức độ không chắc chắn cao.

### Tích hợp COMET

COMET (`metrics_comet.py`) hiện đã được tích hợp dưới dạng chỉ số hạng nhất (first-class metric):
- Mô hình: `Unbabel/wmt22-comet-da` (mô hình dựa trên tham chiếu đã chiến thắng tại WMT 2022)
- Tự động được tính toán khi `unbabel-comet` được cài đặt
- Điểm số trên từng bản ghi được lưu trữ trong các bản ghi của TestReport
- Phát hiện ngôn ngữ tài nguyên thấp thông qua bảng bao phủ XLM-R
- Phụ thuộc tùy chọn: `pip install mt-eval-harness[comet]`

### Di chuyển dữ liệu Supabase (Supabase Migration)

Các cột mới được thêm vào bảng `run_cards`:
- `comet_score` (FLOAT8, nullable)
- `corpus_bleu` (FLOAT8, nullable)
- `chrf_ci_lower` / `chrf_ci_upper` (FLOAT8, nullable)
- `exact_match_ci_lower` / `exact_match_ci_upper` (FLOAT8, nullable)

Xem `migrations/001_add_comet_and_ci_columns.sql` để biết kịch bản di chuyển dữ liệu.