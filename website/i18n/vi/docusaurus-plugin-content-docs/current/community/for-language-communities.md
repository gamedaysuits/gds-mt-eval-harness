---
sidebar_position: 1
title: "Dành cho các cộng đồng ngôn ngữ"
---
# Dành cho các Cộng đồng Ngôn ngữ

> **Tóm tắt dự án.** Hướng dẫn dành cho người nói tiếng bản địa và ngôn ngữ ít tài nguyên, giải thích cách đóng góp cho Arena (bản dịch tham chiếu, đánh giá bản dịch, dữ liệu coaching) và những gì cộng đồng nhận lại (quyền sở hữu mã nguồn, doanh thu API, toàn quyền kiểm soát triển khai). Không yêu cầu kỹ năng lập trình.

Bạn không cần phải là một lập trình viên để đóng góp cho Arena. Nếu bạn nói một ngôn ngữ bản địa hoặc ngôn ngữ ít tài nguyên, bạn chính là người quan trọng nhất trong hệ sinh thái này.

---

## Những gì chúng tôi cần từ bạn

### Bản dịch tham chiếu

Chúng tôi cần các cặp dịch thuật được tuyển chọn để đánh giá — một bên là tiếng Anh, bên kia là ngôn ngữ của bạn. Chúng sẽ trở thành "đáp án" để chấm điểm cho tất cả các phương pháp dịch thuật.

Bạn có thể tạo ra chúng từ:
- **Tài liệu giáo dục** — bài tập trong sách giáo khoa, giáo án, phiếu bài tập
- **Tài liệu cộng đồng** — biên bản cuộc họp, bản tin, thông báo
- **Cụm từ hàng ngày** — chuỗi giao diện người dùng (UI), nhãn ứng dụng, các cách diễn đạt phổ biến
- **Nội dung văn hóa** — câu chuyện, bài hát hoặc mô tả (với sự cho phép phù hợp)

Định dạng là JSON đơn giản:
```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

### Đánh giá bản dịch

Mọi phương pháp được cho là tạo ra bản dịch hoạt động tốt đều cần có sự xác thực của con người. Người nói song ngữ sẽ đánh giá kết quả đầu ra và cho chúng tôi biết liệu máy tính có dịch đúng hay không — và quan trọng hơn là *tại sao* nó lại dịch sai.

### Dữ liệu coaching

Các quy tắc ngữ pháp, mục từ điển, cấu trúc hình thái học — đây là những tài nguyên ngôn ngữ giúp các phương pháp dịch thuật hoạt động. Kiến thức của bạn về cách ngôn ngữ của bạn hoạt động là điều không một mô hình AI nào có thể thay thế được.

---

## Những gì bạn nhận lại

### Quyền sở hữu

Khi một phương pháp dịch thuật được xây dựng cho ngôn ngữ của bạn và được xác thực trên Arena, [quyền sở hữu sẽ được chuyển giao](/docs/sovereignty/ownership-transfer) cho tổ chức quản trị của cộng đồng bạn. Bạn sở hữu mã nguồn, trọng số mô hình (model weights) và việc triển khai.

### Doanh thu

Khi các nhà phát triển sử dụng phương pháp dịch thuật của ngôn ngữ của bạn thông qua champollion API, cộng đồng của bạn sẽ nhận được [90% doanh thu từ API](/docs/sovereignty/economic-model). 10% còn lại dùng để chi trả cho chi phí cơ sở hạ tầng.

### Quyền kiểm soát

Tổ chức quản trị của bạn kiểm soát:
- Ai có thể truy cập phương pháp
- Liệu nó có thể được sử dụng cho mục đích thương mại hay không
- Các điều khoản về giá cả nào được áp dụng
- Khi nào và làm thế nào nó được cập nhật
- Dữ liệu nào được sử dụng để phát triển thêm

---

## Cách thức tham gia

1. **Liên hệ** — Mở một issue trên [kho lưu trữ Arena](https://github.com/gamedaysuits/arena) hoặc gửi email cho những người duy trì dự án
2. **Mô tả ngôn ngữ của bạn** — Ngôn ngữ đó thuộc ngữ hệ nào? Có bao nhiêu người nói? Sử dụng hệ thống chữ viết nào? Có những tài nguyên tính toán nào (FST, từ điển, kho ngữ liệu)?
3. **Bắt đầu từ việc nhỏ** — Thậm chí chỉ cần 50 cặp dịch thuật được tuyển chọn là đã đủ để tạo ra một bộ dữ liệu đánh giá và mở một bảng xếp hạng (leaderboard) mới
4. **Kết nối chúng tôi với ban quản trị** — Ai trong cộng đồng của bạn có thẩm quyền đối với dữ liệu và công nghệ ngôn ngữ? Mô hình chủ quyền của Arena yêu cầu một đối tác quản trị

---

## Chủ quyền Dữ liệu

Dữ liệu ngôn ngữ của bạn là của bạn. Arena được xây dựng dựa trên [các nguyên tắc OCAP®](/docs/sovereignty/data-sovereignty):

- Chúng tôi không bao giờ thu thập hoặc lưu trữ dữ liệu ngôn ngữ của bạn trên máy chủ của chúng tôi
- Các phương pháp dịch thuật sử dụng kiến trúc `api` — tất cả dữ liệu coaching, từ điển và quy tắc ngữ pháp đều nằm trên cơ sở hạ tầng do bạn kiểm soát
- Bạn quyết định ai có thể phát triển các phương pháp cho ngôn ngữ của bạn
- Điểm số trên bảng xếp hạng chứng minh một phương pháp hoạt động hiệu quả; chúng không cấp quyền triển khai phương pháp đó

---

## Xem thêm

- [Chủ quyền Dữ liệu](/docs/sovereignty/data-sovereignty) — khung quy chuẩn đầy đủ của OCAP, CARE và Te Mana Raraunga
- [Chuyển giao Quyền sở hữu](/docs/sovereignty/ownership-transfer) — điều gì xảy ra khi một phương pháp chiến thắng
- [Mô hình Kinh tế](/docs/sovereignty/economic-model) — cách điểm số chuyển hóa thành doanh thu
- [Hỗ trợ Ngôn ngữ ít Tài nguyên](/docs/community/low-resource-languages) — bối cảnh kỹ thuật dành cho các nhà nghiên cứu làm việc cùng với các cộng đồng