---
sidebar_position: 2
title: "Sổ tay hướng dẫn: Coached LLM Prompting"
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
# Coached LLM Prompting

> **Ý tưởng:** Nhúng trực tiếp các quy tắc ngữ pháp, từ điển song ngữ và lưu ý về phong cách vào system prompt của LLM. Không cần huấn luyện, không cần fine-tuning — chỉ cần kiến thức ngôn ngữ có cấu trúc để định hướng đầu ra hướng tới các bản dịch chuẩn xác.

:::info Đây là tài liệu hướng dẫn (cookbook), không phải là một triển khai hoàn chỉnh
Hướng dẫn này phác thảo phương pháp và các quyết định thiết kế chính. Hãy điều chỉnh nó cho phù hợp với cặp ngôn ngữ, tài nguyên sẵn có và mục tiêu đánh giá của bạn.
:::

## Khi nào nên sử dụng

- Bạn có **kiến thức ngôn ngữ** về ngôn ngữ đích (quy tắc ngữ pháp, mục từ điển, tùy chọn phong cách) nhưng không có đủ dữ liệu song song để fine-tuning
- Bạn muốn **lặp nhanh (iterate fast)** — các thay đổi prompt được triển khai trong vài giây, không cần huấn luyện lại
- Ngôn ngữ đích có **các mẫu đã biết (known patterns)** mà LLM thường làm sai (sự hòa hợp giống, quy ước chữ viết, mức độ trang trọng)
- Bạn muốn benchmark phương pháp coached prompting với một baseline và lặp lại những gì hiệu quả

## Cách thức hoạt động

1. **Thu thập dữ liệu hướng dẫn (coaching data)** — các quy tắc ngữ pháp, từ điển song ngữ và lưu ý phong cách trong một file JSON có cấu trúc
2. **Cấu hình văn phong (register)** — một tiền tố system prompt để thiết lập ngôn ngữ, chữ viết và giọng điệu
3. **Chạy harness** — dữ liệu hướng dẫn sẽ được nhúng vào mỗi prompt của LLM
4. **Xem xét các lỗi** — xem những gì bị quality gate từ chối, thêm các quy tắc để giải quyết các mẫu lỗi đó
5. **Lặp lại** — mỗi phiên bản file hướng dẫn là một thử nghiệm mới; harness sẽ theo dõi tất cả

## Cấu trúc dữ liệu hướng dẫn

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

## Các quyết định thiết kế chính

**Độ cụ thể của quy tắc so với cửa sổ ngữ cảnh (context window):** Nhiều quy tắc hơn sẽ giúp LLM có nhiều hướng dẫn hơn, nhưng lại chiếm dụng cửa sổ ngữ cảnh dành cho bản dịch thực tế. Hãy bắt đầu với 5–10 quy tắc có tác động cao và chỉ thêm nhiều hơn khi bạn thấy các mẫu lỗi cụ thể.

**Độ bao phủ của từ điển:** Bạn không cần một từ điển hoàn chỉnh — hãy tập trung vào các thuật ngữ mà LLM liên tục dịch sai. Ngay cả 20–30 thuật ngữ bắt buộc cũng có thể cải thiện đáng kể tính nhất quán.

**Thứ tự quy tắc rất quan trọng:** Đặt các quy tắc quan trọng nhất lên đầu. LLM chú ý mạnh mẽ hơn đến các hướng dẫn xuất hiện sớm.

## Chạy thử nghiệm

```bash
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v1 \
  --coaching-file coaching/crk.json
```

## Ưu điểm và Nhược điểm

| | |
|---|---|
| ✅ Không tốn chi phí huấn luyện | ❌ Giới hạn chất lượng bị hạn chế bởi kiến thức nền tảng của LLM |
| ✅ Lặp lại tức thì (thay đổi prompt → chạy lại) | ❌ Cửa sổ ngữ cảnh giới hạn lượng thông tin hướng dẫn có thể đưa vào |
| ✅ Hoạt động với bất kỳ nhà cung cấp LLM nào | ❌ Các quy tắc có thể xung đột — việc gỡ lỗi tương tác prompt là một nghệ thuật |
| ✅ Minh bạch — bạn có thể đọc chính xác những gì LLM nhìn thấy | ❌ Không tạo ra kiến thức mới, chỉ định hướng kiến thức hiện có |

## Kết hợp tốt với

- **[FST-Gated Pipeline](./fst-gated-pipeline)** — hướng dẫn + xác thực hình thái (morphological validation) sẽ phát hiện những gì mà chỉ riêng hướng dẫn bỏ sót
- **[Dictionary-Augmented LLM](./dictionary-augmented-llm)** — thuật ngữ bắt buộc là một dạng hướng dẫn
- **[Few-Shot Prompting](./few-shot-prompting)** — ví dụ + quy tắc kết hợp với nhau sẽ mạnh mẽ hơn là sử dụng riêng lẻ

## Xem thêm

- [Method Interface](/docs/specifications/methods) — định dạng dữ liệu hướng dẫn và giao thức TranslationMethod
- [Support a Low-Resource Language](/docs/community/low-resource-languages) — ngữ cảnh đầy đủ
- [Eval Harness](/docs/specifications/harness) — cách chạy thử nghiệm