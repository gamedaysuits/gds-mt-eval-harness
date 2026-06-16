---
id: how-this-site-is-translated
title: "Cách trang web này được dịch"
description: "Mọi ngôn ngữ trên trang web này đều được dịch máy bởi chính Champollion, sử dụng phương pháp đã chiến thắng trong thử nghiệm benchmark công khai của chúng tôi cho cặp ngôn ngữ đó."
---
# Trang web này được dịch như thế nào

Trang web này hiện có sẵn bằng 13 ngôn ngữ. Mọi locale ngoại trừ tiếng Anh đều được
**dịch máy bởi Champollion**, công cụ CLI dịch thuật được xây dựng cùng với
đấu trường này — và mô hình dịch cho mỗi ngôn ngữ được lựa chọn **bởi
chính các thử nghiệm hiệu năng (benchmark) của trang web này, chứ không phải theo mặc định**:
mỗi cặp ngôn ngữ được đánh giá trên một kho ngữ liệu phát triển công khai bằng
công cụ đánh giá dịch máy (MT eval harness), và phương pháp/mô hình có composite score
cao nhất (các trường hợp tương đương về mặt thống kê được giải quyết bằng chi phí)
sẽ dịch locale đó.

Điều đó có nghĩa là có hai điều bạn cần biết với tư cách là người đọc:

1. **Các trang này là bản dịch máy.** Chúng được tạo ra với sự hướng dẫn về
   văn phong và thuật ngữ được mô tả bên dưới, nhưng không có con người kiểm duyệt
   lại từng câu. Nếu có nội dung nào chưa chính xác, phiên bản tiếng Anh sẽ là
   bản chuẩn — và chúng tôi rất mong nhận được đóng góp sửa đổi từ bạn.
2. **Bạn có thể kiểm tra lựa chọn này.** Mỗi hàng bên dưới nêu tên lượt chạy thử nghiệm
   hiệu năng đã chọn mô hình cho ngôn ngữ đó; các lượt chạy này được công bố trên
   [bảng xếp hạng MT Eval Arena](https://mtevalarena.org/leaderboard).

## Nguồn gốc theo locale

| Locale | Ngôn ngữ | Phương pháp | Mô hình | Kho ngữ liệu thử nghiệm | Composite score (Khoảng tin cậy 95%) | Ngày thử nghiệm | Đồng bộ lần cuối |
|--------|----------|--------|-------|------------------|--------------------------|----------------|-------------|
| fr | Tiếng Pháp | llm | `anthropic/claude-haiku-4.5` | `eng-fra-dev-v1` (Tatoeba, CC-BY-2.0) | 0.581 [0.542, 0.617] | 2026-06-11 | 2026-06-12 |
| de | Tiếng Đức | llm | `anthropic/claude-opus-4.8` | `eng-deu-dev-v1` (Tatoeba, CC-BY-2.0) | 0.590 [0.550, 0.633] | 2026-06-11 | 2026-06-12 |
| nl | Tiếng Hà Lan | llm | `anthropic/claude-sonnet-4.6` | `eng-nld-dev-v1` (Tatoeba, CC-BY-2.0) | 0.600 [0.558, 0.642] | 2026-06-11 | 2026-06-12 |
| fil | Tiếng Filipino | llm | `openai/gpt-5.5` | `eng-tgl-dev-v1` (Tatoeba, CC-BY-2.0)¹ | 0.499 [0.471, 0.529] | 2026-06-11 | 2026-06-12 |
| es | Tiếng Tây Ban Nha | llm | `anthropic/claude-haiku-4.5` | `eng-spa-dev-v1` (Tatoeba, CC-BY-2.0) | 0.553 [0.523, 0.584] | 2026-06-11 | 2026-06-12 |
| zh | Tiếng Trung giản thể | llm | `anthropic/claude-haiku-4.5` | `eng-cmn-dev-v1` (Tatoeba, CC-BY-2.0) | 0.240 [0.207, 0.278] | 2026-06-11 | 2026-06-12 |
| ja | Tiếng Nhật | llm | `anthropic/claude-sonnet-4.6` | `eng-jpn-dev-v1` (Tatoeba, CC-BY-2.0) | 0.278 [0.252, 0.304] | 2026-06-11 | 2026-06-12 |
| ko | Tiếng Hàn | llm | `anthropic/claude-opus-4.8` | `eng-kor-dev-v1` (Tatoeba, CC-BY-2.0) | 0.286 [0.256, 0.318] | 2026-06-11 | 2026-06-12 |
| pt | Tiếng Bồ Đào Nha | llm | `anthropic/claude-haiku-4.5` | `eng-por-dev-v1` (Tatoeba, CC-BY-2.0) | 0.609 [0.576, 0.646] | 2026-06-11 | 2026-06-12 |
| th | Tiếng Thái | llm | `anthropic/claude-sonnet-4.6` | `eng-tha-dev-v1` (Tatoeba, CC-BY-2.0) | 0.468 [0.426, 0.510] | 2026-06-11 | 2026-06-12 |
| vi | Tiếng Việt | llm | `google/gemini-3.5-flash` | `eng-vie-dev-v1` (Tatoeba, CC-BY-2.0) | 0.463 [0.433, 0.494] | 2026-06-11 | 2026-06-12 |
| ar | Tiếng Ả Rập | llm | `anthropic/claude-fable-5` | `eng-arb-dev-v1` (Tatoeba, CC-BY-2.0)² | 0.437 [0.403, 0.478] | 2026-06-11 | 2026-06-12 |

¹ Tiếng Filipino được thử nghiệm hiệu năng trên dữ liệu tiếng Tagalog — kho ngữ liệu
có sẵn gần nhất của Tatoeba cho locale `fil`.
² Kho ngữ liệu tiếng Ả Rập là tiếng Ả Rập Chuẩn Hiện đại (Modern Standard Arabic - ISO 639-3 `arb`),
phù hợp với văn phong MSA của trang web này.

Quy tắc lựa chọn: đối với mỗi cặp ngôn ngữ, mọi mô hình trong danh sách thử nghiệm hiệu năng
(`google/gemini-3.5-flash`, `anthropic/claude-haiku-4.5`,
`anthropic/claude-fable-5`, `anthropic/claude-opus-4.8`,
`anthropic/claude-sonnet-4.6`, `openai/gpt-5.5`,
`google/gemini-3.1-pro-preview`) đều được chấm điểm trên kho ngữ liệu
phát triển của cặp đó. Mô hình chiến thắng là mô hình có composite score cao nhất;
khi một mô hình có chi phí rẻ hơn không có sự khác biệt có ý nghĩa thống kê so với mô hình
có điểm số cao nhất (sử dụng phương pháp tái lấy mẫu bootstrap bắt cặp, p ≥ 0,05),
mô hình rẻ hơn sẽ được chọn.

*Composite score* là số đo chất lượng hỗn hợp của MT Eval Arena (bao gồm chrF++,
exact match, và các plugin số đo được tải, được xác thực bằng khoảng tin cậy bootstrap).
Điểm số chỉ có thể so sánh được **trong cùng một cặp ngôn ngữ**, chứ không thể so sánh
giữa các cặp khác nhau — điểm số 0,28 ở tiếng Hàn không có nghĩa là các trang tiếng Hàn
tệ hơn các trang tiếng Pháp có điểm số 0,58; do kho ngữ liệu và hệ chữ viết của chúng khác nhau.

## Văn phong và giọng điệu

Mỗi ngôn ngữ được dịch với một văn phong rõ ràng được chọn từ các thẻ ngôn ngữ
(language cards) của Champollion, nhờ đó mức độ trang trọng sẽ nhất quán trên toàn bộ trang web:

- **Tiếng Pháp** — vouvoiement (ngôi *vous* trang trọng)
- **Tiếng Đức** — Sie-Form
- **Tiếng Hà Lan** — u-vorm
- **Tiếng Filipino** — trang trọng, với các thuật ngữ kỹ thuật tiêu chuẩn
- **Tiếng Tây Ban Nha** — tiếng Tây Ban Nha Mỹ Latinh trung tính
- **Tiếng Trung giản thể** — văn phong kỹ thuật chuyên nghiệp
- **Tiếng Nhật** — です/ます (thể lịch sự)
- **Tiếng Hàn** — 해요체 (lịch sự)
- **Tiếng Bồ Đào Nha** — văn phong chuyên nghiệp
- **Tiếng Thái** — chuyên nghiệp trung tính
- **Tiếng Việt** — xưng hô *bạn* trung tính
- **Tiếng Ả Rập** — tiếng Ả Rập Chuẩn Hiện đại, văn phong chuyên nghiệp

## Những nội dung không được dịch máy

Các khối mã (code block), lệnh CLI, khóa cấu hình (configuration key), tên gói (package name),
URL và danh từ riêng được bảo vệ trong quá trình dịch và được giữ nguyên bằng tiếng Anh theo thiết kế.

## Bạn phát hiện bản dịch sai?

Hãy mở một issue hoặc PR — nguồn của mọi trang được dịch đều là bản gốc tiếng Anh.
Các sửa đổi đối với một trang đã dịch sẽ được bảo toàn trong các lần đồng bộ hóa trong tương lai
miễn là nguồn tiếng Anh của trang đó không thay đổi (quá trình đồng bộ hóa chỉ dịch lại một trang
khi nguồn tiếng Anh của trang đó thay đổi).

*Bản thân trang này cũng được dịch máy bằng phương pháp trong bảng trên — nó tự mô tả bản dịch của chính mình.*