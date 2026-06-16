---
sidebar_position: 11
title: "Sổ tay: Tạo ngữ liệu"
---
# Hướng dẫn Tạo Corpus

> **Ý tưởng cốt lõi:** Trước khi có thể đánh giá một phương pháp dịch thuật, bạn cần một corpus đánh giá (evaluation corpus). Hướng dẫn này sẽ trình bày cách xây dựng một corpus từ con số không — từ việc tìm nguồn dữ liệu, yêu cầu định dạng, tiêu chuẩn chất lượng, cấp phép, cho đến việc đóng góp vào Arena.

:::info Đây không phải là một phương pháp dịch thuật
Hướng dẫn này là điều kiện tiên quyết cho nhiều phương pháp khác. Một corpus đánh giá tốt là nền tảng giúp mọi thứ khác trở nên khả thi. Chỉ cần 50 cặp câu được tuyển chọn kỹ lưỡng là đã đủ để mở một nhánh bảng xếp hạng (leaderboard) mới.
:::

## Khi nào nên Sử dụng

- Bạn muốn **thêm một cặp ngôn ngữ mới** vào bảng xếp hạng của Arena
- Bạn là **giáo viên ngôn ngữ** muốn đánh giá năng lực dịch thuật của học sinh
- Bạn là **nhân sự hoạt động ngôn ngữ cộng đồng** có quyền truy cập vào các tài liệu song ngữ
- Bạn là **nhà nghiên cứu** cần một tập đánh giá chuẩn hóa cho cặp ngôn ngữ của mình

## Định dạng Corpus

Hệ thống harness sử dụng định dạng JSON đơn giản:

```json title="my-corpus.json"
{
  "metadata": {
    "name": "Quechua Dev v1",
    "version": "1.0.0",
    "source_language": "eng",
    "target_language": "que",
    "entry_count": 75,
    "license": "CC-BY-SA-4.0",
    "author": "Your Name / Organization",
    "description": "75 English-Quechua pairs from educational materials"
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello, how are you?",
      "reference": "Allillanchu, imaynallan kashanki?"
    },
    {
      "id": 2,
      "source": "The sun is shining today",
      "reference": "Kunan p'unchay inti k'anchashan"
    }
  ]
}
```

## Nguồn Khai thác Dữ liệu

| Nguồn | Chất lượng | Dung lượng | Cấp phép |
|--------|---------|--------|-----------|
| **Sách giáo khoa / tài liệu giáo dục** | Cao (được chuyên gia bình duyệt) | Thấp - trung bình | Kiểm tra với nhà xuất bản |
| **Tài liệu chính phủ** | Trung bình (văn phong trang trọng) | Trung bình - cao | Thường thuộc phạm vi công cộng |
| **Từ điển song ngữ** | Cao (các mục từ đã được xác thực) | Trung bình | Thay đổi tùy nguồn |
| **Người lớn tuổi / người bản xứ trong cộng đồng** | Cao nhất (trực giác bản xứ) | Thấp (thời gian hạn chế) | Cộng đồng quản lý |
| **Văn bản tôn giáo** | Trung bình (đặc thù lĩnh vực) | Cao | Thường là mở |
| **Các corpus hiện có** (Hansard, FLORES) | Trung bình - cao | Cao | Kiểm tra giấy phép |
| **Tự biên soạn thủ công** | Cao nhất | Thấp | Thuộc sở hữu của bạn |

## Tiêu chuẩn Chất lượng

Một corpus đánh giá tốt cần có:

1. **Nội dung đa dạng** — không chỉ gồm các câu chào hỏi hoặc cụm từ đơn giản. Hãy bao gồm cả câu hỏi, câu lệnh, câu phức và các thuật ngữ chuyên ngành
2. **Bản dịch đã được xác thực** — được soát xét bởi ít nhất một người nói trôi chảy, lý tưởng nhất là hai người
3. **Chính tả nhất quán** — sử dụng thống nhất một hệ chữ viết và một quy chuẩn chính tả xuyên suốt
4. **Nguồn độc lập** — không được lấy từ cùng một văn bản mà các phương pháp dịch thuật sẽ dùng để huấn luyện
5. **Cấp phép rõ ràng** — có giấy phép rõ ràng cho phép sử dụng vào mục đích đánh giá

:::danger Nhiễm độc corpus (Corpus contamination)
Corpus đánh giá phải **độc lập** với mọi dữ liệu huấn luyện. Nếu một phương pháp được huấn luyện hoặc gợi ý (prompted) bằng dữ liệu từ corpus đánh giá, phương pháp đó sẽ bị truất quyền thi đấu. Hãy thiết kế corpus của bạn tách biệt hoàn toàn ngay từ ngày đầu tiên.
:::

## Hướng dẫn về Quy mô

| Quy mô | Khả năng đáp ứng |
|------|----------------|
| **50 mục** | Đánh giá khả thi tối thiểu — đủ để phát hiện các khác biệt lớn về chất lượng |
| **100–200 mục** | Xếp hạng đáng tin cậy — đủ để đạt ý nghĩa thống kê (statistical significance) giữa các phương pháp |
| **500+ mục** | Đạt chuẩn nghiên cứu — cho điểm số tổng hợp (composite score) và khoảng tin cậy (confidence interval) mạnh mẽ |
| **1.000+ mục** | Tiêu chuẩn vàng (Gold standard) — tương đương với độ bao phủ của tập devtest FLORES |

Hãy bắt đầu từ quy mô nhỏ. 50 mục là đủ để mở một nhánh bảng xếp hạng mới. Bạn có thể mở rộng quy mô sau này.

## Đóng góp vào Arena

1. **Tạo corpus của bạn** theo định dạng JSON ở trên
2. **Cấp phép cho corpus** — khuyến nghị sử dụng CC BY-SA 4.0 cho đánh giá mở; CC BY-NC-SA 4.0 cho mục đích sử dụng hạn chế
3. **Gửi một PR** đến [eval harness repo](https://github.com/gamedaysuits/arena) chứa corpus của bạn trong `data/`
4. **Bảng xếp hạng sẽ tự động mở** cho cặp ngôn ngữ của bạn ngay khi corpus được hợp nhất (merge)

## Dành cho các Cộng đồng Ngôn ngữ Bản địa

Việc tạo lập corpus là một hành động khẳng định **chủ quyền ngôn ngữ**. Corpus của bạn, điều khoản của bạn:

- Bạn quyết định giấy phép và các điều kiện truy cập
- Bạn có thể đóng góp một **tập phát triển công khai (public development set)** (để phát triển phương pháp) trong khi vẫn giữ một **tập kiểm thử bí mật (secret test set)** (để đánh giá chính thức) dưới sự kiểm soát của cộng đồng
- [Khung chủ quyền](/docs/sovereignty/data-sovereignty) bảo vệ dữ liệu của bạn ở mọi cấp độ

Ngay cả một corpus nhỏ cũng là một **tài sản chiến lược** — đó là tiêu chuẩn quyết định thế nào là "đủ tốt" đối với ngôn ngữ của bạn.

## Kết hợp Tốt với

- **[Dịch thuật một phần (Partial Translation)](./partial-translation)** — việc tạo lập corpus CHÍNH LÀ bước dịch thuật thủ công bởi con người
- **[Dịch ngược (Back-Translation)](./back-translation)** — dữ liệu tổng hợp bổ sung cho các corpus do con người tạo ra
- Mọi tài liệu hướng dẫn (cookbook) khác — tất cả đều cần một corpus đánh giá

## Xem thêm

- [Tập dữ liệu Đánh giá (Evaluation Datasets)](/docs/leaderboard/datasets) — các corpus hiện có (EDTeKLA, FLORES+)
- [Chủ quyền Dữ liệu (Data Sovereignty)](/docs/sovereignty/data-sovereignty) — quyền sở hữu và kiểm soát
- [Dành cho các Cộng đồng Ngôn ngữ](/docs/community/for-language-communities) — sự tham gia của cộng đồng
- [Hỗ trợ Ngôn ngữ Nguồn lực thấp](/docs/community/low-resource-languages) — bức tranh toàn cảnh