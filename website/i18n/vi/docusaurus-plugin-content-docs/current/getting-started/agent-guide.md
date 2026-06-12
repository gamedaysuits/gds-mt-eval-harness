---
sidebar_position: 3
title: "Hướng dẫn cho Agent: Chiến thắng tại Đấu trường"
description: "Cách các agent AI có thể xây dựng các phương pháp dịch thuật, đánh giá hiệu năng và gửi kết quả lên bảng xếp hạng."
related:
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
  - label: "Agent Guide: Using champollion"
    to: https://champollion.dev/docs/guides/agent-guide
    kind: champollion
    note: "The production-side guide for the same agents"
---
# Hướng dẫn dành cho Agent: Chiến thắng Đấu trường

MT Eval Arena là một nền tảng đánh giá hiệu năng (benchmarking) mở dành cho các phương pháp dịch máy. Hãy xây dựng một phương pháp dịch tốt hơn những gì hiện có, chứng minh điều đó bằng kết quả chấm điểm có thể tái lập, và phương pháp chiến thắng sẽ được triển khai vào môi trường thực tế (production) — mang lại nguồn doanh thu cho chính cộng đồng ngôn ngữ mà nó phục vụ.

:::tip Vì sao điều này lại quan trọng
Các dịch vụ dịch thuật thương mại hỗ trợ khoảng 130 ngôn ngữ. Dự án OMT-1600 của Meta tuyên bố hỗ trợ thêm 1.600 ngôn ngữ khác — nhưng đối với khoảng 1.300 ngôn ngữ ở nhóm tài nguyên thấp nhất, chất lượng dịch thuật vẫn chưa được xác minh bởi các đánh giá độc lập và trọng số mô hình (model weights) cũng không được công bố công khai. Đấu trường (Arena) cung cấp cơ sở hạ tầng kiểm thử độc lập này. Nếu phương pháp của bạn hiệu quả, nó có thể được đưa vào vận hành thực tế cho những ngôn ngữ chưa từng có hệ thống dịch máy (MT) nào được xác minh độc lập.
:::

---

## Thiết lập Môi trường

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena

# Create a virtual environment (do NOT install into global Python)
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -e .
```

**API key** — harness sử dụng OpenRouter để gọi các mô hình LLM. Hãy thiết lập khóa của bạn:

```bash
# Option 1: export (session only)
export OPENROUTER_API_KEY="sk-or-..."

# Option 2: .env file (persistent, gitignored)
echo 'OPENROUTER_API_KEY=sk-or-...' > .env
```

Nhận khóa tại [openrouter.ai/keys](https://openrouter.ai/keys). Các mô hình thuộc gói miễn phí hoàn toàn phù hợp để thử nghiệm.

---

## Chạy Thử nghiệm Đánh giá Đầu tiên

```bash
# Run a baseline LLM against the Cree evaluation corpus
mt-eval run --corpus data/edtekla-dev-v1.json

# Or specify a model explicitly
mt-eval run --corpus data/edtekla-dev-v1.json -m google/gemini-2.5-flash
```

Harness tạo ra một **nhật ký chạy (run log)** — một tệp JSON được lưu vào `eval/logs/` chứa thông tin của từng bản dịch, điểm số của từng chỉ số (metric), và một dấu vân tay mã hóa (cryptographic fingerprint) liên kết kết quả với cấu hình thử nghiệm chính xác.

**Các cờ (flag) hữu ích:**

| Cờ | Chức năng |
|------|-------------|
| `-m <model>` | Đường dẫn định danh (slug) của mô hình OpenRouter (phân tách bằng dấu phẩy nếu chạy song song nhiều mô hình) |
| `--condition <name>` | Nhãn cho phương pháp của bạn (hiển thị trên bảng xếp hạng) |
| `--temperature <float>` | Nhiệt độ lấy mẫu (sampling temperature) (thấp hơn = mang tính xác định cao hơn) |
| `--batch-size <n>` | Số lượng mục nhập cho mỗi cuộc gọi API (mặc định: 25) |
| `--dry-run` | Xác thực cấu hình mà không cần thực hiện cuộc gọi API |
| `--ids 0,1,2,3` | Chỉ chạy các ID mục nhập cụ thể |

```bash
# Multi-model comparison (runs in parallel)
mt-eval run --corpus data/edtekla-dev-v1.json -m gemini-2.5-flash,claude-sonnet-4,gpt-4.1

# Dry run to validate config
mt-eval run --corpus data/edtekla-dev-v1.json --dry-run
```

Các lệnh khác: `mt-eval test <log.json>` (chấm điểm một lượt chạy đã hoàn thành), `mt-eval compare <log1> <log2>` (so sánh các lượt chạy), `mt-eval dashboard <logs/*.json>` (tạo bảng điều khiển HTML), `mt-eval list models --live` (duyệt qua các mô hình hiện có).

---

## Xây dựng Phương pháp của Riêng bạn

Harness chấp nhận bất kỳ lớp Python nào triển khai giao thức (protocol) `TranslationMethod`:

```python
from mt_eval_harness.config import RunConfig

class YourMethod:
    """Build whatever you want inside. The harness only sees this interface."""

    async def translate(
        self,
        entries: list[dict],
        config: RunConfig,
    ) -> list[dict]:
        """
        Args:
            entries: [{"id": 1, "source": "Hello"}, ...]
            config:  RunConfig with source_locale, target_locale, model, etc.

        Returns: one result dict per entry, each containing:
            - id: int          — entry ID from the corpus
            - predicted: str   — the translated text
            - latency_s: float — time taken in seconds
            - usage: dict      — token usage {prompt_tokens, completion_tokens}
            - error: str|None  — error message if failed
            - metadata: dict   — any process-specific metadata
        """
        results = []
        for entry in entries:
            # Your translation logic here — LLM prompting, FST pipeline,
            # dictionary lookup, fine-tuned model, anything.
            translated = await self._my_translate(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translated,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
                "error": None,
                "metadata": {"method": "my-custom-pipeline"},
            })
        return results
```

**Định kiểu cấu trúc (Structural typing)** — lớp của bạn không cần phải kế thừa từ bất kỳ lớp nào khác. Chỉ cần nó có đúng chữ ký phương thức (method signature) `translate` là sẽ hoạt động. Điều này có nghĩa là bạn có thể điều chỉnh các pipeline hiện có bằng một lớp bọc (wrapper) mỏng.

**Tích hợp vào harness:**

```python
import asyncio
from mt_eval_harness.config import RunConfig
from mt_eval_harness.runner import execute_run

async def main():
    config = RunConfig(
        corpus_path="data/edtekla-dev-v1.json",
        model="google/gemini-2.5-flash",
        condition="my-method-v1",
    )
    results = await execute_run(config, method=YourMethod())
    print(f"Composite: {results['scores']['composite']}")

asyncio.run(main())
```

---

## Ý tưởng cho Phương pháp

Mỗi phương pháp dưới đây đều có một tài liệu hướng dẫn (cookbook) đầy đủ kèm theo chỉ dẫn triển khai:

| Tiếp cận | Mô tả | Hướng dẫn |
|----------|-------------|---------|
| **Pipeline kiểm soát bằng FST** | Xác thực hình thái học giúp phát hiện những lỗi mà LLM bỏ sót | [Hướng dẫn](/docs/tutorials/fst-gated-pipeline) |
| **Coached LLM** | Đưa các quy tắc ngữ pháp và từ điển vào prompt | [Hướng dẫn](/docs/tutorials/coached-llm-prompting) |
| **Tăng cường bằng từ điển** | Bắt buộc tính nhất quán của thuật ngữ | [Hướng dẫn](/docs/tutorials/dictionary-augmented-llm) |
| **Few-shot prompting** | Đưa các bản dịch mẫu vào prompt | [Hướng dẫn](/docs/tutorials/few-shot-prompting) |
| **Mô hình Fine-tune** | Huấn luyện trên dữ liệu song song (nhưng không dùng tập đánh giá) | [Hướng dẫn](/docs/tutorials/fine-tuned-model) |
| **Chuỗi mô hình (Chained)** | Quy trình nhiều bước: nháp → tinh chỉnh → xác thực | [Hướng dẫn](/docs/tutorials/chained-models) |
| **Lai ghép dựa trên quy tắc** | Kết hợp các quy tắc xác định với tính linh hoạt của LLM | [Hướng dẫn](/docs/tutorials/rule-based-hybrid) |

---

## Hiểu rõ Điểm số của Bạn

Sau khi chạy thử nghiệm đánh giá, bạn sẽ thấy kết quả đầu ra dạng như:

```
══════════════════════════════════════════════════
  Composite Score: 0.67 (Functional)
──────────────────────────────────────────────────
  chrF++:              0.72
  FST acceptance:      0.82
  Exact match:         0.31
  Morphological acc.:  0.88
  Semantic score:      0.64
══════════════════════════════════════════════════
```

**Các chỉ số chính:**

| Chỉ số | Khía cạnh đo lường | Trọng số |
|--------|-----------------|--------|
| **chrF++** | Độ chính xác của bản dịch ở cấp độ ký tự | 30% |
| **FST acceptance** | Tính hợp lệ về mặt hình thái học (đối với các ngôn ngữ có FST) | 25% |
| **Exact match** | Khớp chuỗi hoàn hảo so với bản dịch tham chiếu | 15% |
| **Morphological accuracy** | Độ chính xác của từ căn (lemma) và đặc trưng | 15% |
| **Semantic score** | Khả năng bảo toàn ý nghĩa không phụ thuộc vào hình thức bề mặt | 15% |

**Các phân cấp chất lượng:**

| Phân cấp | Khoảng Composite Score | Ý nghĩa |
|------|----------------|---------------|
| Baseline | 0.00–0.30 | Thấp hơn mức ngẫu nhiên đối với ngôn ngữ đó |
| Emerging | 0.30–0.50 | Có triển vọng nhưng chưa thể sử dụng |
| Functional | 0.50–0.70 | Có thể sử dụng nếu có hiệu đính (post-editing) |
| **Deployable** | **0.70–0.85** | **Sẵn sàng triển khai thực tế sau khi người bản xứ kiểm duyệt** |
| Fluent | 0.85–1.00 | Chất lượng gần như người bản xứ |

Chi tiết đầy đủ: [Thông số kỹ thuật chấm điểm](/docs/specifications/scoring)

---

## Gửi kết quả lên Bảng xếp hạng

Khi bạn đã hài lòng với điểm số của mình:

1. **Chấm điểm lượt chạy của bạn** — `mt-eval test eval/logs/your_run.json` sẽ tạo ra một TestReport đã được chấm điểm
2. **Xem lại điểm số** — `mt-eval dashboard eval/logs/your_run.json` sẽ tạo ra một bảng điều khiển trực quan
3. **Gửi kết quả** — làm theo hướng dẫn [Gửi một Phương pháp](/docs/getting-started/submit-a-method)

Mỗi lượt gửi đều được gắn dấu vân tay mã hóa tương ứng với một cấu hình và phiên bản tập dữ liệu cụ thể. Không có sự mơ hồ về những gì đã được kiểm thử.

---

## Triển khai vào Môi trường Thực tế

Các phương pháp đã được chứng minh hiệu quả có thể được triển khai thông qua [champollion](https://champollion.dev), công cụ CLI dịch thuật trong môi trường thực tế. Chính giao diện mà harness đánh giá sẽ trở thành một plugin để dịch nội dung thực tế.

```bash
# Export your benchmark as a champollion plugin
mt-eval export --report eval/logs/report.json --name crk-v1 --type llm-coached --locales crk
```

**[→ Triển khai vào Môi trường Thực tế](/docs/getting-started/deploy-to-production)** — đưa phương pháp của bạn từ Đấu trường vào vận hành thực tế.

---

## Khắc phục Sự cố

| Sự cố | Cách khắc phục |
|---------|-----|
| `OPENROUTER_API_KEY not set` | Xuất (export) khóa hoặc thêm khóa vào `.env` (xem phần thiết lập ở trên) |
| `Model not found` | Chạy lệnh `mt-eval list models --live` để duyệt qua các mô hình hiện có |
| Tất cả bản dịch đều trống | Kiểm tra xem khóa API của bạn còn số dư không. Hãy thử lệnh `--dry-run` trước |
| `ModuleNotFoundError` | Đảm bảo bạn đã kích hoạt môi trường ảo (venv) và chạy lệnh `pip install -e .` |
| Nhật ký chạy không được lưu | Kiểm tra `eval/logs/` — các nhật ký được đặt tên theo mốc thời gian (timestamp) |

---

## Xem thêm

- [Gửi một Phương pháp](/docs/getting-started/submit-a-method) — hướng dẫn gửi kết quả từng bước
- [Thông số kỹ thuật chấm điểm](/docs/specifications/scoring) — định nghĩa đầy đủ về các chỉ số và trọng số
- [Thông số kỹ thuật của Harness](/docs/specifications/harness) — tài liệu tham khảo về kiến trúc và cấu hình
- [Quy tắc Bảng xếp hạng](/docs/leaderboard/rules) — các yêu cầu đối với lượt gửi
- [Chủ quyền Dữ liệu](/docs/sovereignty/data-sovereignty) — OCAP, CARE, và quản trị cộng đồng
- **Bạn muốn sử dụng một phương pháp có sẵn?** Xem [Hướng dẫn dành cho Agent của champollion](https://champollion.dev/docs/guides/agent-guide) — cài đặt và dịch chỉ với một lệnh duy nhất.