---
sidebar_position: 3
title: "Tập dữ liệu đánh giá"
related:
  - label: "Corpus Design Framework"
    to: /docs/specifications/corpus-design
    kind: spec
    note: "How evaluation corpora are constructed"
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "Build a corpus for your language"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
---
# Tập dữ liệu Đánh giá

> **Tóm tắt dự án.** Trang này mô tả các tập dữ liệu đánh giá hiện có để đo kiểm (benchmarking), bao gồm cấu trúc (schema) của các mục trong ngữ liệu, các mức độ khó (1–5) và các yêu cầu về nguồn gốc (provenance). Hiện tại đang có sẵn: EDTeKLA Dev v1 (Plains Cree, tổng cộng 548 mục: 486 từ sách giáo khoa + 62 bản dịch chuẩn gold standard) và FLORES+ Devtest (39 ngôn ngữ, mỗi ngôn ngữ 1.012 mục).

Các tập dữ liệu là các mục tiêu cố định mà công cụ chạy đánh giá (harness) sẽ sử dụng để đối chiếu. Mỗi tập dữ liệu là một tệp JSON chứa các cặp nguồn→đích kèm theo các bản dịch tham chiếu gold-standard. Công cụ harness sẽ tính điểm đầu ra của mô hình dựa trên các bản dịch tham chiếu này — nó không bao giờ sửa đổi chúng.

:::danger KHÔNG HUẤN LUYỆN trên dữ liệu đánh giá

⚠️ **Các tập dữ liệu này chỉ dành riêng cho việc đánh giá.** Các phương pháp được huấn luyện (train), tinh chỉnh (fine-tune), gợi ý vài lượt (few-shot-prompted) hoặc tiếp xúc với dữ liệu đánh giá bằng bất kỳ hình thức nào khác sẽ tạo ra điểm số cao một cách giả tạo và sẽ bị **loại khỏi bảng xếp hạng (leaderboard).**

Hãy sử dụng các ngữ liệu riêng biệt để huấn luyện. Các tập dữ liệu đánh giá phải được giữ kín hoàn toàn với mô hình của bạn trong suốt quá trình phát triển.
:::

---

## Định dạng Tập dữ liệu

Mọi tập dữ liệu đều tuân theo cùng một cấu trúc (schema) JSON:

```json
{
  "dataset": {
    "id": "dataset-slug",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "description": "Human-readable description of the dataset",
    "source_language": "en",
    "target_language": "crk",
    "created": "2025-05-01",
    "license": "CC-BY-NC-4.0",
    "provenance": ["gold_standard", "textbook"]
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "tânisi",
      "difficulty": 1,
      "provenance": "gold_standard",
      "register": "conversational",
      "context": "greeting",
      "notes": "Common greeting, SRO orthography"
    }
  ]
}
```

:::info Cấu trúc Chuẩn (Canonical Schema)
Tài liệu [Benchmark Specification](/docs/specifications/benchmark) định nghĩa ngữ liệu chuẩn và cấu trúc của các mục dữ liệu. Trang này tài liệu hóa các tập dữ liệu hiện có và cách tạo tập dữ liệu mới.
:::

### Khối `dataset` Cấp cao nhất

| Trường | Kiểu dữ liệu | Mô tả |
|-------|------|-------------|
| `id` | `string` | Mã định danh duy nhất của tập dữ liệu (được sử dụng trong run card và bảng xếp hạng) |
| `version` | `string` | Phiên bản ngữ nghĩa (semantic version). Việc tăng phiên bản này sẽ làm mất hiệu lực của các so sánh run card trước đó |
| `language_pair` | `string` | Nhãn hiển thị (ví dụ: `EN→CRK`) |
| `description` | `string` | Không bắt buộc. Bản tóm tắt dễ đọc đối với con người |
| `source_language` | `string` | Mã ngôn ngữ nguồn BCP 47 |
| `target_language` | `string` | Mã ngôn ngữ đích BCP 47 |
| `created` | `string` | Ngày tạo theo chuẩn ISO 8601 |
| `license` | `string` | Mã định danh giấy phép SPDX |
| `provenance` | `string[]` | Danh sách các thẻ nguồn gốc (provenance tags) được sử dụng trên các mục dữ liệu |

### Các Trường của Mục dữ liệu

| Trường | Kiểu dữ liệu | Bắt buộc | Mô tả |
|-------|------|----------|-------------|
| `id` | `integer` | ✅ | Mã định danh duy nhất của mục dữ liệu trong ngữ liệu |
| `source` | `string` | ✅ | Văn bản nguồn cần dịch |
| `reference` | `string` | ✅ | Bản dịch tham chiếu gold-standard |
| `difficulty` | `integer` | ✅ | Mức độ khó từ 1–5 (xem bên dưới) |
| `provenance` | `string` | ✅ | Nguồn gốc của mục dữ liệu này (ví dụ: `gold_standard`, `textbook`, `elicited`) |
| `register` | `string` | ✅ | Văn phong/mức độ trang trọng (ví dụ: `conversational`, `formal`, `ceremonial`) |
| `context` | `string` | ✅ | Chức năng giao tiếp (ví dụ: `greeting`, `declaration`, `instruction`) |
| `notes` | `string` | ❌ | Ngữ cảnh không bắt buộc dành cho người đánh giá |
| `morphological_analysis` | `string` | ❌ | Phân tích hình thái học gold-standard |
| `variant_class` | `string` | ❌ | Nhãn lớp nhóm các biến thể dịch thuật được chấp nhận |

---

## Các Tập dữ liệu Hiện có

### Tập Phát triển EDTeKLA v1

Tập dữ liệu đánh giá đầu tiên, được xây dựng cho tác vụ dịch English→Plains Cree (SRO). Được tạo bởi [nhóm nghiên cứu EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) tại Đại học Alberta.

| Thuộc tính | Giá trị |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Phiên bản** | `1.0` |
| **Cặp ngôn ngữ** | EN → CRK (Plains Cree, chữ viết SRO) |
| **Số lượng mục** | Tổng cộng 548 (486 từ sách giáo khoa + 62 gold standard). Ngữ liệu phát triển chuẩn (canonical dev corpus) là `textbook_dev.json` (436 mục — toàn bộ phần chia phát triển từ sách giáo khoa trong tổng số 486 mục: 436 phát triển + 50 kiểm tra được giữ lại) |
| **Phân bổ độ khó** | Dễ, Trung bình, Khó |
| **Nguồn gốc** | `gold_standard` (được xác minh bởi người bản xứ), `textbook` (tài liệu giáo dục đã xuất bản) |
| **Giấy phép** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |

**Nội dung kiểm tra:**

- Các câu chào hỏi cơ bản và cụm từ thông dụng
- Tính sinh vật của danh từ (noun animacy) và sự phân biệt ngôi thứ ba phụ (obviation)
- Chia động từ theo các ngôi và thì
- Cấu trúc chỉ vị trí (locative)
- Hệ biến hình sở hữu (possessive paradigms)
- Cấu trúc câu phức tạp

:::tip Cấu trúc ngữ liệu
Bộ sưu tập EdTeKLA đầy đủ có 548 mục được tuyển chọn: 486 mục từ ngữ liệu sách giáo khoa (436 phát triển + 50 giữ lại) và 62 mục từ bản dịch chuẩn gold-standard itwêwina. Ngữ liệu phát triển chuẩn là `textbook_dev.json` với 436 mục — toàn bộ phần chia phát triển từ sách giáo khoa. Mỗi mục dữ liệu đều được xác minh bởi những người nói lưu loát hoặc được lấy từ các sách giáo khoa tiếng Cree đã xuất bản. Một tập dữ liệu nhỏ hơn, chất lượng cao với các bản dịch chuẩn gold-standard đã được xác minh sẽ hữu ích hơn một tập dữ liệu lớn nhưng nhiều nhiễu — đặc biệt là đối với một ngôn ngữ ít tài nguyên (low-resource language), nơi các bản dịch "gần đúng" thường không hợp lệ về mặt hình thái học.
:::

---

## Tạo một Tập dữ liệu Mới

Để tạo một tập dữ liệu cho một cặp ngôn ngữ hoặc lĩnh vực mới:

### 1. Cấu trúc tệp JSON

Tuân theo cấu trúc [Định dạng Tập dữ liệu](#dataset-format). Mỗi mục dữ liệu phải có `source`, `reference`, `difficulty`, `provenance`, `register`, và `context`.

### 2. Gán một ID duy nhất

Sử dụng một slug mô tả: `{project}-{split}-v{version}` (ví dụ: `edtekla-dev-v1`, `quechua-test-v1`).

### 3. Xác minh các bản dịch chuẩn gold-standard

Mỗi giá trị `reference` phải được xác minh bởi người nói lưu loát hoặc được lấy từ một nguồn tài liệu đã xuất bản và được bình duyệt (peer-reviewed). Các bản dịch tham chiếu do máy tạo ra sẽ làm mất đi mục đích của việc đánh giá.

### 4. Thiết lập các mức độ khó

Gán cho mỗi mục dữ liệu một mức độ khó bằng số nguyên:

| Mức độ | Mô tả | Ví dụ |
|------|-------------|----------|
| 1 — Từ vựng cơ bản | Từ đơn, câu chào hỏi thông dụng, chữ số | "hello" → "tânisi" |
| 2 — Câu đơn giản | Chủ ngữ-động từ hoặc SVO, thì hiện tại | "I see the dog" |
| 3 — Độ phức tạp trung bình | Thì quá khứ/tương lai, từ sở hữu, tính sinh vật | "I saw his dog yesterday" |
| 4 — Hình thái học phức tạp | Sự phân biệt ngôi thứ ba phụ (obviation), thể bị động, trật tự liên hợp (conjunct order) | "the woman whose son went to the store" |
| 5 — Nâng cao | Nhiều mệnh đề, văn phong trang trọng, nghi lễ, thành ngữ | Một đoạn văn đầy đủ với giọng điệu phù hợp với văn phong |

### 5. Gắn thẻ nguồn gốc (provenance)

Mỗi mục dữ liệu nên chỉ rõ nguồn gốc của nó. Các thẻ phổ biến:

- `gold_standard` — Được xác minh bởi người nói lưu loát
- `textbook` — Từ các tài liệu giáo dục đã xuất bản
- `elicited` — Được tạo ra thông qua các buổi thu thập dữ liệu có cấu trúc (elicitation sessions)
- `corpus` — Được trích xuất từ một ngữ liệu song song

### 6. Xác thực tệp

Chạy công cụ harness đối với tập dữ liệu của bạn bằng bất kỳ mô hình nào để xác minh rằng tệp JSON được định dạng đúng và có đầy đủ tất cả các trường bắt buộc:

```bash
python eval/baseline_experiment.py --dataset path/to/your-dataset.json
```

Công cụ harness sẽ báo lỗi nếu thiếu trường, trùng lặp chỉ mục hoặc vi phạm cấu trúc (schema).

### 7. Gửi yêu cầu tích hợp

Hãy mở một pull request tới [kho lưu trữ eval harness](https://github.com/gamedaysuits/arena) kèm theo tệp dữ liệu của bạn trong thư mục `data/`. Đính kèm tài liệu mô tả phương pháp xác minh và các nguồn gốc dữ liệu của bạn.

---

## FLORES+ Devtest

Một bộ đo kiểm đa ngôn ngữ có độ bao phủ rộng được duy trì bởi [Open Language Data Initiative (OLDI)](https://huggingface.co/datasets/openlanguagedata/flores_plus). Được sử dụng cho bộ đo kiểm đa mô hình tiên phong (multi-model frontier benchmark) của champollion.

| Thuộc tính | Giá trị |
|----------|-------|
| **ID** | `flores-plus-devtest` |
| **Các cặp ngôn ngữ** | EN → 39 ngôn ngữ (tất cả các ngôn ngữ tự nhiên đã đăng ký của champollion) |
| **Số lượng mục** | 1.012 câu cho mỗi ngôn ngữ |
| **Giấy phép** | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| **Nguồn** | Ban đầu là Meta FLORES-200, hiện được duy trì bởi OLDI |
| **Vị trí** | Các tệp fixtures được trích xuất sẵn tại `test/benchmark/fixtures/` trong kho lưu trữ champollion chính |

:::danger Chỉ dành cho đánh giá
FLORES+ chỉ được thiết kế dành riêng cho việc đánh giá. Các nhà quản lý yêu cầu rõ ràng rằng nó **không được sử dụng làm dữ liệu huấn luyện**. Hãy đảm bảo nội dung của nó được loại trừ khỏi bất kỳ ngữ liệu huấn luyện nào.
:::

---

## Xem thêm

- [Đánh giá dịch máy (MT Evaluation)](/docs/leaderboard/rules) — tổng quan về khung đánh giá và bảng xếp hạng
- [Eval Harness](/docs/specifications/harness) — cách chạy đánh giá đối với các tập dữ liệu này
- [Đặc tả Run Card](/docs/specifications/run-card) — cấu trúc JSON để ghi lại kết quả
- [Bảng xếp hạng Phương pháp (Method Leaderboard)](https://champollion.dev/leaderboard) — điểm số đo kiểm trực tiếp
- [Dự án EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) — nhóm nghiên cứu của Đại học Alberta đứng sau tập dữ liệu tiếng Cree