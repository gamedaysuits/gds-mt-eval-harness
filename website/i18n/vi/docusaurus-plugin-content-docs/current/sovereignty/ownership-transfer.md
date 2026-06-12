---
sidebar_position: 2
title: "Chuyển giao quyền sở hữu"
---
# Chuyển giao Quyền sở hữu

> **Tóm tắt dự án.** Khi một phương pháp dịch thuật đạt đến cấp độ Deployable (composite score ≥ 0.70) và vượt qua vòng đánh giá của cộng đồng, quyền sở hữu mã nguồn sẽ được chuyển giao từ nhà nghiên cứu sang tổ chức quản trị của người bản địa. Trang này tài liệu hóa quy trình chuyển giao năm giai đoạn, sự tương thích với OCAP® và hướng dẫn dành cho các nhà nghiên cứu xây dựng phương pháp dịch thuật cho các ngôn ngữ bản địa.

Khi một phương pháp dịch thuật giành chiến thắng trên bảng xếp hạng Arena, điều gì sẽ xảy ra với mã nguồn? Đối với các ngôn ngữ bản địa và ngôn ngữ ít tài nguyên, câu trả lời không phải là "nhà nghiên cứu giữ lại nó". Câu trả lời là: **cộng đồng sở hữu nó.**

---

## Quy trình hoạt động

Arena áp dụng một quy trình rõ ràng từ nghiên cứu đến quyền sở hữu của cộng đồng:

### 1. Phát triển Phương pháp
Một nhà nghiên cứu, sinh viên hoặc nhà phát triển xây dựng một phương pháp dịch thuật — một pipeline kiểm soát bằng FST, một coached LLM, một mô hình fine-tuned, hoặc bất kỳ phương pháp tiếp cận nào khác. Họ tự phát triển phương pháp đó bằng tài nguyên của chính mình.

### 2. Đánh giá trên Arena
Phương pháp này được đánh giá hiệu năng (benchmark) thông qua [hệ thống đánh giá (eval harness)](/docs/specifications/harness). Mỗi lượt gửi bài đều được gắn dấu vân tay số (fingerprint) với một commit Git và phiên bản tập dữ liệu cụ thể. Các điểm số đều có thể tái lập.

### 3. Cộng đồng Đánh giá
Đối với các phương pháp dịch thuật ngôn ngữ bản địa, kết quả sẽ được xem xét bởi các nhân sự ngôn ngữ cộng đồng và các tổ chức quản trị. Điểm số cao trên bảng xếp hạng chứng minh phương pháp đó *hoạt động hiệu quả*; nó không chứng minh rằng phương pháp đó là *phù hợp*.

### 4. Chuyển giao Mã nguồn
Khi một phương pháp đạt đến cấp độ **Deployable** (composite score ≥ 0.70 so với đánh giá chuẩn vàng) **và** vượt qua vòng đánh giá của cộng đồng (xác thực bởi con người):
- Nhà nghiên cứu bàn giao mã nguồn
- Quyền sở hữu pháp lý được chuyển giao cho tổ chức quản trị của người bản địa (ví dụ: hội đồng bộ tộc, cơ quan quản lý ngôn ngữ hoặc tổ chức Métis)
- Tổ chức quản trị nắm giữ các khóa mã hóa cho các tập dữ liệu đánh giá
- Phương pháp này trở thành một tài sản do cộng đồng kiểm soát

Xem [Scoring Specification](/docs/specifications/scoring), §5 để biết định nghĩa về các cấp độ chất lượng, [Benchmark Specification](/docs/specifications/benchmark), §8.3 để biết đầy đủ các điều kiện chuyển giao và §7 cho cổng xác thực bởi con người.

### 5. Triển khai Thực tế
Phương pháp này được xuất dưới dạng một plugin [champollion](https://champollion.dev) và được triển khai lên API thực tế (production API). Cộng đồng sẽ kiểm soát:
- Ai có thể truy cập phương pháp
- Các điều khoản định giá nào được áp dụng
- Phương pháp có thể được sử dụng cho mục đích thương mại hay không
- Khi nào và làm thế nào phương pháp được cập nhật

---

## Tại sao điều này lại quan trọng

Nghiên cứu ML truyền thống thường đi theo mô hình khai thác:
1. Nhà nghiên cứu thu thập dữ liệu từ một cộng đồng
2. Nhà nghiên cứu huấn luyện một mô hình
3. Nhà nghiên cứu công bố một bài báo khoa học
4. Cộng đồng không nhận được gì

Mô hình này hiện đang hoạt động ở quy mô công nghiệp. Dự án OMT-1600 của Meta (tháng 3 năm 2026) đã huấn luyện các mô hình dịch thuật cho 1.600 ngôn ngữ — bao gồm cả các ngôn ngữ bản địa như tiếng Plains Cree — bằng cách sử dụng dữ liệu thu thập từ web và các bản dịch Kinh Thánh. Các mô hình này được huấn luyện mà không có các giao thức đồng thuận từ cộng đồng, các trọng số (weights) hiện không có sẵn để tải xuống, và các cộng đồng có ngôn ngữ được mô hình hóa không có cổ phần sở hữu, không có vai trò quản trị và không có doanh thu. Bài báo khoa học là sản phẩm. Cộng đồng chỉ là nguồn dữ liệu.

Arena đảo ngược quy trình này:
1. Nhà nghiên cứu xây dựng một phương pháp
2. Arena xác thực phương pháp đó dựa trên các kho ngữ liệu do cộng đồng tuyển chọn bằng các số đo hình thái (morphological metrics)
3. Cộng đồng nhận quyền sở hữu mã nguồn hoạt động
4. Cộng đồng kiếm được doanh thu từ việc sử dụng API

**Đây là sự khác biệt cơ bản giữa Champollion và mọi nỗ lực dịch máy ngôn ngữ ít tài nguyên (LRL MT) khác, bao gồm cả OMT-1600:** chúng tôi không chỉ tạo ra các phương pháp cho cộng đồng — chúng tôi chuyển giao quyền sở hữu các phương pháp đó *cho* cộng đồng. Mã nguồn, trọng số (weights), cơ sở hạ tầng triển khai — tất cả đều trở thành tài sản của cộng đồng. Đây không phải là một khung lý thuyết — đó là quy trình vận hành thực tế cho mọi phương pháp ngôn ngữ bản địa trên nền tảng.

---

## Sự tương thích với OCAP®

Quy trình chuyển giao quyền sở hữu trực tiếp thực thi các [nguyên tắc OCAP®](/docs/sovereignty/data-sovereignty):

| Nguyên tắc | Triển khai thực tế |
|---|---|
| **Ownership** (Sở hữu) | Tổ chức quản trị nắm giữ quyền sở hữu đối với mã nguồn phương pháp và trọng số mô hình |
| **Control** (Kiểm soát) | Tổ chức quản trị kiểm soát các điều khoản triển khai, quyền truy cập và định giá |
| **Access** (Truy cập) | Các thành viên cộng đồng truy cập phương pháp thông qua API champollion hoặc tải xuống trực tiếp |
| **Possession** (Sở hữu thực tế) | Các tài nguyên ngôn ngữ (dữ liệu huấn luyện kèm cặp, từ điển, quy tắc FST) vẫn nằm trên cơ sở hạ tầng do cộng đồng kiểm soát thông qua phương thức `api` |

---

## Dành cho các nhà nghiên cứu

Nếu bạn đang phát triển một phương pháp cho một ngôn ngữ bản địa:

1. **Thiết lập mối quan hệ** với cộng đồng ngôn ngữ trước khi bạn bắt đầu
2. **Sử dụng dữ liệu có giấy phép mở** để phát triển (không sử dụng các tài nguyên bị giới hạn của cộng đồng)
3. **Tài liệu hóa nguồn gốc (provenance)** trong [run card](/docs/specifications/run-card) của bạn — liệt kê mọi tài nguyên, giấy phép và nguồn gốc của nó
4. **Hãy chuẩn bị sẵn sàng để chuyển giao** — nếu phương pháp của bạn thành công, mã nguồn sẽ thuộc về cộng đồng, không phải của bạn
5. **Đây là một tính năng, không phải là một hạn chế** — đóng góp của bạn là kiến trúc và kỹ thuật, những thứ bạn có thể công bố và tái sử dụng. Đóng góp của cộng đồng là tri thức ngôn ngữ giúp phương pháp đó hoạt động hiệu quả cho ngôn ngữ của họ.

---

## Xem thêm

- [Chủ quyền Dữ liệu](/docs/sovereignty/data-sovereignty) — Các nguyên tắc OCAP, CARE và Te Mana Raraunga
- [Mô hình Kinh tế](/docs/sovereignty/economic-model) — Cách quyền sở hữu chuyển hóa thành doanh thu
- [Hỗ trợ Ngôn ngữ ít Tài nguyên](/docs/community/low-resource-languages) — Bối cảnh nghiên cứu