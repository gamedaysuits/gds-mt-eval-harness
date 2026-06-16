---
sidebar_position: 1
title: "Gửi phương pháp"
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
# Gửi Phương pháp

> **Tóm tắt nhanh.** Hướng dẫn từng bước để nhanh chóng gửi lượt chạy benchmark đầu tiên của bạn lên bảng xếp hạng (leaderboard). Sao chép (clone) harness, chạy thử nghiệm với một tập dữ liệu, xem lại run card của bạn và gửi. Chỉ mất 10 phút nếu bạn đã có API key.

Hướng dẫn này sẽ dẫn dắt bạn qua các bước để gửi lượt chạy benchmark đầu tiên của mình lên bảng xếp hạng MT Eval Arena.

---

## Điều kiện tiên quyết

- **Python 3.10+**
- **Một OpenRouter API key** (hoặc tương đương cho nhà cung cấp mô hình của bạn)
- **Một phương pháp dịch thuật** — bất kỳ thứ gì tạo ra bản dịch từ một văn bản nguồn

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## Bước 1: Chạy Harness

Harness sẽ chấm điểm phương pháp của bạn dựa trên một tập dữ liệu chuẩn hóa:

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| Flag | Chức năng |
|---|---|
| `--corpus` | Đường dẫn đến tập ngữ liệu đánh giá (`.json`, `.jsonl`, `.tsv`) |
| `--model` | Model slug — tên viết tắt (ví dụ: `gemini-pro`) hoặc OpenRouter ID đầy đủ |
| `--condition` | Nhãn cho phương pháp của bạn (hiển thị trên bảng xếp hạng) |
| `--temperature` | Nhiệt độ lấy mẫu (sampling temperature) (thấp hơn = mang tính xác định cao hơn) |
| `--fst-retries` | Tùy chọn: số lần thử lại FST |
| `--submit` | Tự động gửi run card lên bảng xếp hạng |

Harness sẽ tạo ra một **run card** — một tệp JSON độc lập chứa điểm số của bạn, mã hash của tập dữ liệu, model slug và một dấu vân tay mã hóa (cryptographic fingerprint) liên kết kết quả với cấu hình thử nghiệm chính xác.

---

## Bước 2: Xem lại Run Card của bạn

Các run card được lưu vào `results/`. Hãy kiểm tra run card của bạn trước khi gửi:

```bash
cat results/your-run-card.json | python -m json.tool
```

Các trường quan trọng cần kiểm tra:
- `scores.chrf_plus_plus` — chỉ số chất lượng chính của bạn
- `scores.exact_match_rate` — tỷ lệ các bản dịch hoàn hảo
- `scores.fst_acceptance_rate` — tính hợp lệ về mặt hình thái (nếu có sử dụng FST)
- `totals.total_cost_usd` — chi phí của lượt chạy
- `fingerprint` — mã hash khả năng tái lặp của thử nghiệm

Xem [Thông số kỹ thuật Run Card](/docs/specifications/run-card) để biết schema đầy đủ.

---

## Bước 3: Gửi kết quả

### Gửi tự động

Nếu bạn đã truyền `--submit` khi chạy harness, run card của bạn đã được tải lên.

### Gửi thủ công

Gửi bất kỳ run card nào qua API:

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

Or tải lên thông qua [Giao diện Bảng xếp hạng](https://champollion.dev/leaderboard).

---

## Điều gì xảy ra tiếp theo

1. Bản gửi của bạn sẽ được xác thực (mã hash tập dữ liệu, tính toàn vẹn của run card)
2. Kết quả sẽ xuất hiện trên bảng xếp hạng dưới dạng **Self-benchmarked** (mức độ tin cậy 1)
3. Để đạt trạng thái **GDS Verified**, hãy gửi phương pháp của bạn dưới dạng một plugin có thể cài đặt để những người duy trì dự án có thể tái lập kết quả của bạn
4. Đối với các phương pháp dành cho ngôn ngữ bản địa: nếu phương pháp của bạn đạt vị trí dẫn đầu, quy trình [chuyển giao quyền sở hữu](/docs/sovereignty/ownership-transfer) sẽ bắt đầu

---

## Xem thêm

- [Cách sử dụng Harness](/docs/specifications/harness) — tài liệu tham khảo CLI đầy đủ
- [Quy tắc Bảng xếp hạng](/docs/leaderboard/rules) — tiêu chí gửi bài và chính sách chống gian lận
- [Xây dựng Phương pháp](/docs/specifications/methods) — giao thức TranslationMethod
- [Tập dữ liệu](/docs/leaderboard/datasets) — các tập dữ liệu đánh giá hiện có