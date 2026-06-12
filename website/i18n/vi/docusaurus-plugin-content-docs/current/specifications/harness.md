---
sidebar_position: 2
title: "Eval Harness v2.0"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "What the harness metrics feed into"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: Translate 30 Languages"
    to: https://champollion.dev/docs/tutorials/translate-30-languages
    kind: champollion
    note: "Use the harness to audit registers in production"
---
# Eval Harness v2.0

> **Tóm tắt tổng quan.** Trang này hướng dẫn cài đặt, cấu hình và sử dụng MT evaluation harness — công cụ đánh giá hiệu năng (benchmark) các phương pháp dịch thuật dựa trên các ngữ liệu chuẩn hóa và tạo ra các run card có tính điểm. Để xem định nghĩa chuẩn của các chỉ số, schema và giao thức đánh giá, hãy xem [Tài liệu đặc tả Benchmark](/docs/specifications/benchmark).

Harness này thực hiện các thử nghiệm dịch thuật và tạo ra các run card. Nó xử lý việc xây dựng prompt, gọi API, tính điểm và tuần tự hóa (serialization) kết quả — bạn chỉ cần cung cấp tập dữ liệu và mô hình.

## Cài đặt

**Yêu cầu:** Python 3.10+

```bash
pip install sacrebleu aiohttp
```

Clone kho lưu trữ (repository) của harness:

```bash
git clone https://github.com/gamedaysuits/arena.git
cd arena
```

## Cách sử dụng

```bash
mt-eval run --corpus path/to/dataset.json
```

Lệnh này sẽ chạy từng mục trong ngữ liệu (corpus) qua mô hình đã cấu hình (hoặc plugin phương pháp), tính điểm cho các kết quả đầu ra và ghi tệp JSON của run card vào thư mục đầu ra.

## Các cờ CLI

### `mt-eval run`

| Cờ | Bắt buộc | Mặc định | Mô tả |
|------|----------|---------|-------------|
| `--corpus` | ✅ | — | Đường dẫn đến tệp ngữ liệu (`.json`, `.jsonl`, `.tsv`) |
| `--source-file` / `--reference-file` | — | — | Các tệp văn bản song song (định dạng FLORES+, WMT) |
| `-m, --model` | — | `gemini-pro` | Slug của mô hình (tên ngắn hoặc ID OpenRouter đầy đủ). Được phân giải qua `shared/model-aliases.json`. Phân tách bằng dấu phẩy đối với các lượt chạy đa mô hình |
| `-d, --dataset` | — | `all` | Bộ lọc tập dữ liệu: `all`, tên phân đoạn (segment name), hoặc khoảng ID |
| `--ids` | — | — | Các ID mục cần đánh giá, phân tách bằng dấu phẩy |
| `--source-lang` | — | `English` | Tên ngôn ngữ nguồn |
| `--target-lang` | — | — | Tên ngôn ngữ đích |
| `-p, --prompt` | — | `naive` | Phiên bản prompt (`naive`, `custom`, `champollion`) |
| `--coaching-file` | — | — | Đường dẫn đến tệp văn bản coaching prompt |
| `--coaching` | — | — | Văn bản coaching nội dòng (chuỗi trong dấu ngoặc kép) |
| `--method` | — | — | Đường dẫn đến thư mục plugin phương pháp (chứa `method.json` + module Python) |
| `--method-card` | — | — | Đường dẫn đến tệp JSON của method card cho siêu dữ liệu (metadata) bảng xếp hạng |
| `--fst-retries` | — | `0` | Số lần thử lại FST (chỉ áp dụng cho phương pháp LLM mặc định) |
| `--skip-fst` | — | `false` | Bỏ qua hoàn toàn cổng chất lượng (quality gate) FST |
| `--tools` | — | `false` | Kích hoạt chế độ gọi công cụ (tool-calling) |
| `--tools-list` | — | — | Tên các công cụ, phân tách bằng dấu phẩy |
| `--max-tool-rounds` | — | `8` | Số vòng gọi công cụ tối đa cho mỗi mục |
| `--hooks` | — | — | Tên các hook sau dịch thuật (post-translation hook) |
| `--style-profile` | — | — | Đường dẫn đến tệp JSON của hồ sơ phong cách (style profile). Kích hoạt các chỉ số về tính nhất quán của phong cách viết (chỉ mang tính thông tin — không bao giờ là một phần của composite score; xem [§ Chỉ số phong cách viết và văn phong](#writing-style-and-register-metrics-informational)) |
| `-b, --batch-size` | — | `25` | Số mục trên mỗi cuộc gọi API |
| `-c, --concurrency` | — | `8` | Số cuộc gọi API song song |
| `--max-tokens` | — | `32768` | Số token tối đa trên mỗi cuộc gọi API |
| `--temperature` | — | `0.0` | Nhiệt độ lấy mẫu (sampling temperature) (0.0 = xác định/deterministic) |
| `--no-cache` | — | `false` | Vô hiệu hóa bộ nhớ đệm phản hồi (response caching) |
| `--cache-dir` | — | `eval/cache/harness` | Đường dẫn thư mục bộ nhớ đệm (cache) |
| `-o, --output-dir` | — | `eval/logs/harness` | Thư mục đầu ra cho các run card và nhật ký (log) |
| `-n, --name` | — | — | Tên lượt chạy dễ đọc đối với con người |
| `--dry-run` | — | `false` | Xác thực cấu hình mà không thực hiện cuộc gọi API |
| `--champollion-config` | — | — | Đường dẫn đến `champollion.config.json` |
| `--champollion-cards-dir` | — | — | Thư mục chứa các thẻ ngôn ngữ (language card) |
| `--target-lang-code` | — | — | Mã ngôn ngữ BCP-47 |

### Các lệnh con khác

| Lệnh con | Mô tả |
|------------|-------------|
| `mt-eval test <log_path>` | Phân tích nhật ký (log) của một lượt chạy đã hoàn thành |
| `mt-eval publish <report_path>` | Gửi một run card lên bảng xếp hạng (leaderboard) |
| `mt-eval compare <logs...>` | So sánh trực quan nhiều lượt chạy cạnh nhau |
| `mt-eval dashboard <logs...>` | Tạo một bảng điều khiển (dashboard) HTML từ nhật ký lượt chạy |
| `mt-eval list models\|prompts\|datasets` | Liệt kê các tài nguyên hiện có |
| `mt-eval export` | Đóng gói thiết lập hiện tại thành một plugin phương pháp champollion |
| `mt-eval export-config` | Xuất MethodConfig đã phân giải (tất cả 8 trường chuẩn) dưới dạng JSON |

### Ví dụ

```bash
# Run with defaults (gemini-pro alias → google/gemini-3.1-pro-preview, naive prompt)
mt-eval run --corpus data/edtekla-dev-v1.json

# Coached experiment with coaching file
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model google/gemini-3.1-pro \
  --coaching-file prompts/crk-coaching-v8.txt \
  --temperature 0.0

# Run a custom method plugin with FST retries
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --method ./methods/fst-gated-pipeline \
  --fst-retries 3
```

---

## Schema của Run Card

Mỗi thử nghiệm đều tạo ra một **run card** — một tài liệu JSON độc lập. Cấu trúc cấp cao nhất:

```json
{
  "run_id": "uuid-v4",
  "harness_version": "2.0",
  "model_slug": "google/gemini-3.1-pro",
  "model_id": "gemini-3.1-pro-001",
  "condition": "baseline",
  "timestamp": "2026-06-01T03:22:41Z",
  "elapsed_seconds": 142.7,
  "dataset": { ... },
  "config": { ... },
  "method_card": { ... },
  "system_prompt_sha256": "abc123...",
  "system_prompt_used": "You are a translator...",
  "fingerprint": { ... },
  "scores": { ... },
  "totals": { ... },
  "environment": { ... },
  "results": [ ... ],
  "run_card_hash": "sha256-of-entire-card"
}
```

Xem [Tài liệu đặc tả Run Card](/docs/specifications/run-card) để biết schema đầy đủ với tài liệu chi tiết cho từng trường.

:::info Schema chuẩn
[Tài liệu đặc tả Benchmark](/docs/specifications/benchmark) là nguồn thông tin chuẩn duy nhất (single source of truth) cho schema của run card. Để biết định nghĩa về các chỉ số, trọng số tổng hợp (composite weight) và các bậc chất lượng (quality tier), hãy xem [Tài liệu đặc tả tính điểm](/docs/specifications/scoring). Trang này hướng dẫn cách sử dụng harness; các tài liệu đặc tả sẽ định nghĩa ý nghĩa của các kết quả đầu ra.
:::

### Các khối chính

**`dataset`** — Xác định tập dữ liệu nào đã được sử dụng, bao gồm cả mã băm nội dung (content hash) của nó để kết quả luôn gắn liền với một phiên bản cụ thể:

```json
// Example using master_corpus.json (62 gold + 342 textbook = 404)
{
  "id": "edtekla-dev-v1",
  "version": "1.0",
  "language_pair": "EN→CRK",
  "sha256": "...",
  "entry_count": 404
}
```

**`scores`** — Các chỉ số tổng hợp cho lượt chạy:

```json
// Counts reflect the dataset used (here: master_corpus.json, 404 entries)
{
  "total": 404,
  "exact_matches": 12,
  "exact_match_rate": 0.0968,
  "fst_accepted": 87,
  "fst_acceptance_rate": 0.7016,
  "chrf_plus_plus": 42.31,
  "errors": 0,
  "avg_latency_seconds": 1.15,
  "median_latency_seconds": 1.02,
  "p95_latency_seconds": 2.34,
  "by_difficulty": { ... },
  "by_provenance": { ... }
}
```

**`totals`** — Theo dõi lượng token sử dụng và chi phí:

```json
{
  "prompt_tokens": 48200,
  "completion_tokens": 3100,
  "reasoning_tokens": 0,
  "cached_tokens": 12000,
  "total_cost_usd": 0.42,
  "cost_per_entry_usd": 0.0034,
  "reasoning_ratio": 0.0
}
```

---

## Chỉ số phong cách viết và văn phong (mang tính thông tin)

Harness có thể đánh giá xem các bản dịch có khớp với **văn phong (register)** và **phong cách viết (writing style)** mục tiêu hay không, thông qua plugin chỉ số `WritingStyleConsistency` (`mt_eval_harness/plugins/writing_style.py`). Một bản dịch có thể chính xác về mặt ngôn ngữ nhưng lại sai văn phong — ví dụ như cách diễn đạt thân mật trong một tài liệu pháp lý, hoặc các câu mẫu trang trọng trong văn bản tiếp thị — và các chỉ số so khớp chuỗi (string metrics) sẽ không nhận ra điều này. Nhưng các chỉ số này thì có.

**Những gì được đo lường (trên mỗi mục):**

| Chỉ số | Thang đo | Ý nghĩa |
|--------|-------|---------|
| `style_register_match` | boolean | Kết quả đầu ra có khớp với văn phong mong đợi không? Mục tiêu được lấy từ trường `register` của mục ngữ liệu (xem [Đặc tả Benchmark §2.6](/docs/specifications/benchmark)) hoặc từ một hồ sơ phong cách (style profile) |
| `style_sentence_length_ratio` | float | Độ dài câu trung bình dự đoán so với tham chiếu (1.0 = khớp; sự sai lệch = trôi lệch phong cách/style drift) |
| `style_formality_score` | 0.0–1.0 | Sự xuất hiện của các dấu hiệu trang trọng/thân mật (đại từ xưng hô trang trọng/thân mật, từ viết tắt, ...) sử dụng tài nguyên dấu hiệu theo từng ngôn ngữ |

**Tổng hợp:** `style_consistency_rate` — tỷ lệ các mục không phát hiện thấy sự không khớp về văn phong.

Kích hoạt mục tiêu tùy chỉnh bằng `--style-profile path/to/profile.json` (ví dụ: hồ sơ giọng điệu thương hiệu/brand-voice profile); nếu không có, plugin sẽ tự động sử dụng siêu dữ liệu `register` của từng mục ngữ liệu nếu có.

:::caution Lưu ý về phạm vi
Các chỉ số này **chỉ mang tính thông tin** — chúng không bao giờ là một phần của composite score, và việc phát hiện mức độ trang trọng dựa trên các dấu hiệu (một phương pháp phỏng đoán/heuristic), chứ không phải là một đánh giá được học máy (learned judgment). Hãy coi chúng như một công cụ phát hiện sự trôi lệch (drift detector) đối với việc tuân thủ văn phong, chứ không phải là phán quyết về chất lượng phong cách.
:::

---

## Fingerprint so với Run Card Hash {#fingerprint-vs-run-card-hash}

Harness tạo ra hai mã băm (hash) riêng biệt. Chúng phục vụ các mục đích khác nhau:

### Fingerprint

**Fingerprint** trả lời cho câu hỏi: *"Lượt chạy này có thể được tái lập không?"*

Nó băm sự kết hợp của các đầu vào xác định cấu hình thử nghiệm — chứ không phải các đầu ra:

- SHA-256 của tập dữ liệu
- Slug của mô hình
- Nhãn điều kiện (condition label)
- SHA-256 của system prompt
- Nhiệt độ (temperature)
- Phiên bản harness

Hai lượt chạy có fingerprint giống hệt nhau nghĩa là đã sử dụng cùng một thiết lập. Kết quả của chúng sẽ có thể so sánh được với nhau (ngoại trừ tính không xác định/non-determinism của API).

### Run Card Hash

**Run card hash** trả lời cho câu hỏi: *"Tệp kết quả cụ thể này có bị can thiệp hay thay đổi không?"*

Đó là mã băm SHA-256 của toàn bộ tệp JSON của run card (ngoại trừ chính trường `run_card_hash`). Nếu bất kỳ trường nào thay đổi — một điểm số, một mốc thời gian, hay một kết quả đầu ra duy nhất — mã băm sẽ không còn khớp.

:::info Khi nào nên sử dụng loại nào
Sử dụng **fingerprint** để nhóm các lượt chạy có thể so sánh được (cùng một thử nghiệm, các lần thực thi khác nhau). Sử dụng **run card hash** để xác minh tính toàn vẹn của một tệp kết quả cụ thể.
:::

---

## Đăng tải lên Bảng xếp hạng

Sau khi hoàn thành một lượt chạy, hãy sử dụng `mt-eval publish` để gửi run card:

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

Nếu không có `--method-card` nào được cung cấp trong lượt chạy, `mt-eval publish` sẽ khởi chạy một trình hướng dẫn tương tác (`method_card_wizard.py`) để hướng dẫn bạn mô tả phương pháp của mình (tên, lớp, các công cụ được sử dụng, v.v.). Kết quả đầu ra của trình hướng dẫn sẽ được nhúng vào run card trước khi gửi.

### Gửi thủ công

Các run card được lưu dưới dạng tệp JSON trong thư mục đầu ra. Bạn cũng có thể gửi bất kỳ tệp run card nào thông qua giao diện người dùng của bảng xếp hạng tại [/leaderboard](https://champollion.dev/leaderboard), hoặc thông qua API:

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning Xác thực bảng xếp hạng
Bảng xếp hạng sẽ xác thực các run card được gửi so với danh mục đăng ký tập dữ liệu. Các lượt gửi tham chiếu đến các tập dữ liệu không xác định, hoặc có `run_card_hash` bị lỗi, sẽ bị từ chối.
:::

:::danger KHÔNG ĐƯỢC HUẤN LUYỆN trên dữ liệu đánh giá
Nếu phương pháp của bạn đã tiếp xúc với tập dữ liệu đánh giá trong quá trình phát triển — dưới dạng dữ liệu huấn luyện (training data), ví dụ few-shot, các mục từ điển hoặc tài liệu thiết kế prompt (prompt engineering) — lượt gửi của bạn sẽ bị **tước quyền thi đấu (disqualified)**. Xem [Đánh giá dịch máy (MT Evaluation)](/docs/leaderboard/rules) để biết thế nào là một phương pháp tốt và không tốt.
:::

---

## Xem thêm

- [Đánh giá dịch máy (MT Evaluation)](/docs/leaderboard/rules) — tổng quan, giá trị cốt lõi của bảng xếp hạng, và hướng dẫn về phương pháp tốt/không tốt
- [Tập dữ liệu đánh giá](/docs/leaderboard/datasets) — định dạng tập dữ liệu, EDTeKLA, FLORES+
- [Tài liệu đặc tả Run Card](/docs/specifications/run-card) — schema JSON đầy đủ
- [Xây dựng một phương pháp](/docs/specifications/methods) — giao diện phương pháp để tạo ra các phương pháp có thể đánh giá được
- [Bảng xếp hạng phương pháp](https://champollion.dev/leaderboard) — điểm số benchmark trực tiếp
- [Tài liệu đặc tả Benchmark](/docs/specifications/benchmark) — giao thức đánh giá, định dạng ngữ liệu, schema của run card
- [Tài liệu đặc tả tính điểm](/docs/specifications/scoring) — nguồn thông tin chuẩn duy nhất (SSOT) cho các chỉ số, trọng số tổng hợp (composite weight) và các bậc chất lượng (quality tier)