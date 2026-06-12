---
sidebar_position: 8
title: "Giao thức xác thực người nói"
slug: '/specifications/speaker-validation'
---
# Quy trình Xác thực bởi Người nói

> **Mục đích.** Tài liệu này xác định chính xác những gì chúng tôi cần từ những người nói song ngữ tiếng Cree–Anh để xác thực các số đo đánh giá LYSS. Nếu không có sự xác thực này, các điểm số tự động của chúng tôi chỉ là những ước tính kỹ thuật, chứ không phải là các phép đo chất lượng đã được chứng minh. Đây là khoảng trống quan trọng nhất trong dự án.
>
> **Đối tượng độc giả.** Các đối tác cộng đồng, cộng tác viên tiềm năng, người đánh giá tài trợ và đội ngũ dự án.
>
> Cập nhật lần cuối: 2026-06-07

---

## 1. Tại sao chúng tôi cần người nói

Khung đánh giá LYSS (Linguistically-informed Yield & Structural Scoring) tính toán điểm số chất lượng tự động cho các bản dịch tiếng Anh → tiếng Cree Đồng bằng (Plains Cree). Khung này sử dụng ba tín hiệu cốt lõi:

- **LYSS-fst**: Bản dịch đầu ra có chứa các từ tiếng Cree hợp lệ không? (được kiểm tra bởi bộ chuyển đổi trạng thái hữu hạn GiellaLT)
- **LYSS-eq**: Bản dịch đầu ra có phải là một biến thể chấp nhận được của bản dịch tham chiếu không? (được kiểm tra bởi các lớp tương đương của linter)
- **LYSS-sem**: Bản dịch đầu ra có giữ nguyên ý nghĩa của văn bản gốc không? (được kiểm tra bởi bộ xác thực ngữ nghĩa)

Các số đo này tạo ra các con số. **Chúng tôi không biết liệu những con số đó có ý nghĩa gì hay không.** FST có thể từ chối các từ hợp lệ mà nó không nhận diện được (từ mượn, từ mới, danh từ riêng). Linter có thể bỏ sót các trường hợp tương đương hợp lệ hoặc chấp nhận các trường hợp không hợp lệ. Bộ xác thực ngữ nghĩa có thể đánh giá sai ý nghĩa. Cho đến khi những người nói song ngữ cho chúng tôi biết liệu điểm số tự động của chúng tôi có khớp với đánh giá của con người về chất lượng dịch thuật hay không, chúng tôi vẫn chỉ đang đoán mò.

Mọi số đo đánh giá dịch máy (MT) lớn (BLEU, COMET, chrF++) đều được xác thực bằng cách so sánh điểm số tự động với hàng nghìn đánh giá chất lượng của con người. Chúng tôi cũng cần điều tương tự — ở quy mô nhỏ hơn vì tài nguyên có hạn, nhưng với cùng một mức độ nghiêm ngặt.

---

## 2. Những gì chúng tôi cần: Ba nhiệm vụ

### Nhiệm vụ A: Đánh giá chất lượng bản dịch (Chính — tổng cộng khoảng 8 giờ)

**Nội dung:** Đánh giá 200 bản dịch tiếng Anh → tiếng Cree do máy tạo ra theo hai thang đo.

**Đối tượng:** Hơn 3 người nói song ngữ tiếng Cree Đồng bằng–Anh có khả năng đọc trôi chảy chữ viết SRO (Standard Roman Orthography).

**Cách thức hoạt động:**

1. Chúng tôi cung cấp một bảng tính hoặc biểu mẫu web gồm 200 hàng. Mỗi hàng có:
   - Câu gốc tiếng Anh
   - Bản dịch tiếng Cree do máy tạo ra
   - (Tùy chọn) bản dịch tiếng Cree tham chiếu để so sánh

2. Đối với mỗi bản dịch, người nói sẽ đánh giá hai yếu tố:

   **Độ đầy đủ (Adequacy)** (bản dịch có truyền tải đúng nội dung không?):
   | Điểm | Nhãn | Ý nghĩa |
   |-------|-------|---------|
   | 1 | Không có | Bản dịch không liên quan gì đến văn bản gốc |
   | 2 | Ít | Một vài từ khớp nhưng ý nghĩa tổng thể bị sai |
   | 3 | Nhiều | Ý nghĩa cốt lõi được giữ lại nhưng các phần quan trọng bị thiếu hoặc sai |
   | 4 | Hầu hết | Hầu hết mọi thứ đều chính xác, chỉ có một vài khoảng trống nhỏ về nghĩa |
   | 5 | Toàn bộ | Bản dịch truyền tải đầy đủ ý nghĩa của văn bản gốc |

   **Độ trôi chảy (Fluency)** (nghe có giống tiếng Cree tự nhiên không?):
   | Điểm | Nhãn | Ý nghĩa |
   |-------|-------|---------|
   | 1 | Không thể hiểu được | Đây không phải là tiếng Cree |
   | 2 | Không trôi chảy | Các từ riêng lẻ có thể là tiếng Cree nhưng cấu trúc câu bị hỏng |
   | 3 | Không tự nhiên | Có thể hiểu được nhưng rõ ràng không phải là cách người nói tiếng Cree sẽ nói |
   | 4 | Tốt | Nghe tự nhiên với một vài chỗ hơi gượng gạo |
   | 5 | Hoàn hảo | Một người nói tiếng Cree bản xứ có thể viết như thế này |

3. Tùy chọn, người nói có thể thêm ghi chú bằng văn bản tự do để giải thích cho đánh giá của mình (ví dụ: "sai sự hòa hợp động từ động vật/bất động vật", "đây là phương ngữ th nhưng tôi đánh giá dựa trên phương ngữ y").

**Thời gian ước tính:** ~2,5 phút cho mỗi bản dịch × 200 bản dịch = ~8 giờ. Có thể chia thành nhiều buổi (ví dụ: 4 buổi × 2 giờ trong vòng 2 tuần).

**Thù lao:** 50–65 CAD/giờ (khớp với mức thù lao cho người nói trong BENCHMARK_SPEC §10.3). Tổng cộng mỗi người nói: 400–520 CAD. Cho 3 người nói: **1.200–1.560 CAD**.

**Chúng tôi sẽ làm gì với dữ liệu này:** Chúng tôi tính toán hệ số tương quan (correlation) giữa điểm số LYSS tự động và đánh giá của người nói. Nếu LYSS-fst tương quan với điểm đánh giá độ trôi chảy và LYSS-sem tương quan với điểm đánh giá độ đầy đủ, các số đo sẽ được xác thực. Nếu không, chúng tôi sẽ biết cần phải sửa chúng ở đâu.

---

### Nhiệm vụ B: Xác thực tính tương đương của Linter (~2 giờ)

**Nội dung:** Xem xét 50 cặp bản dịch tiếng Cree mà linter của chúng tôi phân loại là "tương đương" và cho chúng tôi biết liệu chúng có thực sự mang ý nghĩa giống nhau hay không.

**Đối tượng:** 1–2 người nói song ngữ (có thể là cùng những người nói trong Nhiệm vụ A).

**Cách thức hoạt động:**

1. Chúng tôi cung cấp 50 cặp. Mỗi cặp có:
   - Văn bản gốc tiếng Anh
   - Bản dịch A (bản dịch tham chiếu)
   - Bản dịch B (một biến thể mà linter của chúng tôi cho là tương đương)
   - Lý do tương đương (ví dụ: "hoán vị trật tự từ", "biến thể chính tả", "loại bỏ tiểu từ tùy chọn")

2. Đối với mỗi cặp, người nói sẽ trả lời:
   - **Cùng ý nghĩa?** Có / Không / Tùy thuộc vào ngữ cảnh
   - **Cả hai đều tự nhiên?** Có / A tốt hơn / B tốt hơn / Cả hai đều không tự nhiên
   - **Ghi chú** (văn bản tự do tùy chọn)

**Thời gian ước tính:** ~2 phút cho mỗi cặp × 50 cặp = ~2 giờ.

**Thù lao:** 50–65 CAD/giờ × 2 giờ = **100–130 CAD mỗi người nói**.

**Chúng tôi sẽ làm gì với dữ liệu này:** Chúng tôi tính toán độ chính xác (precision) của từng lớp tương đương. Nếu người nói xác nhận 90% các trường hợp tương đương về "trật tự từ" là thực sự tương đương, lớp đó sẽ được xác thực. Nếu họ nói 40% các trường hợp tương đương về "từ đồng nghĩa của từ căn (lemma synonym)" là sai, chúng tôi biết cần phải sửa đổi hoặc loại bỏ lớp đó.

---

### Nhiệm vụ C: Đánh giá tỷ lệ từ chối sai của FST (~1,5 giờ)

**Nội dung:** Xem xét 100 từ tiếng Cree bị bộ phân tích FST từ chối (báo rằng không phải là từ tiếng Cree hợp lệ) và cho chúng tôi biết liệu chúng có thực sự hợp lệ hay không.

**Đối tượng:** 1 người nói song ngữ có vốn từ vựng tiếng Cree phong phú.

**Cách thức hoạt động:**

1. Chúng tôi chạy bộ phân tích FST trên kho ngữ liệu chuẩn vàng (gold-standard corpus) EDTeKLA gồm 436 mục của chúng tôi và thu thập mọi từ bị từ chối.
2. Chúng tôi trình bày tối đa 100 từ bị từ chối cho người nói cùng với ngữ cảnh câu của chúng.
3. Đối với mỗi từ, người nói sẽ trả lời:
   - **Đây có phải là một từ tiếng Cree hợp lệ không?** Có / Không / Không chắc chắn
   - **Nếu có, thuộc loại nào?** Từ đã được thiết lập / Từ mượn / Tên riêng / Dạng phương ngữ / Từ mới / Khác
   - **Ghi chú** (tùy chọn)

**Thời gian ước tính:** ~1 phút cho mỗi từ × 100 từ = ~1,5 giờ.

**Thù lao:** 50–65 CAD/giờ × 1,5 giờ = **75–100 CAD**.

**Chúng tôi sẽ làm gì với dữ liệu này:** Chúng tôi tính toán tỷ lệ từ chối sai (false rejection rate) của FST. Nếu FST từ chối 50 từ và người nói cho biết 30 từ trong số đó là hợp lệ, tỷ lệ từ chối sai là 60% — mức cao không thể chấp nhận được, đòi hỏi phải có danh sách cho phép (allowlist) cho từ mượn/ngoại lệ. Nếu người nói cho biết chỉ có 5 từ là hợp lệ, tỷ lệ từ chối sai là 10% — số đo này là đáng tin cậy.

---

## 3. Tổng thời gian cam kết của người nói

| Nhiệm vụ | Số lượng người nói cần thiết | Số giờ mỗi người nói | Chi phí mỗi người nói | Tổng chi phí |
|------|----------------|-------------------|-----------------|------------|
| A: Đánh giá chất lượng | 3 | ~8 giờ | 400–520 CAD | 1.200–1.560 CAD |
| B: Xác thực Linter | 2 | ~2 giờ | 100–130 CAD | 200–260 CAD |
| C: Đánh giá FST | 1 | ~1,5 giờ | 75–100 CAD | 75–100 CAD |
| **Tổng cộng** | **3 người nói** | **~11,5 giờ (tối đa mỗi người)** | **575–750 CAD (tối đa)** | **1.475–1.920 CAD** |

Nếu cùng 3 người nói thực hiện tất cả các nhiệm vụ: **~11,5 giờ mỗi người trong vòng 2–4 tuần, 575–750 CAD mỗi người**.

Một người nói chỉ thực hiện Nhiệm vụ A sẽ cam kết khoảng **~8 giờ trong vòng 2 tuần với mức thù lao 400–520 CAD**.

---

## 4. Tiêu chuẩn của người nói

**Yêu cầu bắt buộc:**
- Song ngữ tiếng Cree Đồng bằng và tiếng Anh
- Đọc trôi chảy chữ viết SRO (Standard Roman Orthography)
- Thoải mái với việc đánh giá các bản dịch theo một thang đo có cấu trúc

**Ưu tiên:**
- Có kinh nghiệm với phương ngữ y (phương ngữ được sử dụng trong kho ngữ liệu tham chiếu của chúng tôi từ EDTeKLA)
- Có kinh nghiệm giảng dạy hoặc dịch thuật (giúp đưa ra những đánh giá chất lượng chuẩn xác)
- Quen thuộc với các văn phong khác nhau (trang trọng, giáo dục, giao tiếp)

**Không yêu cầu:**
- Kiến thức kỹ thuật hoặc xử lý ngôn ngữ tự nhiên (NLP) (chúng tôi cung cấp tất cả các công cụ và ngữ cảnh)
- Kỹ năng máy tính (giao diện đánh giá sẽ là một bảng tính hoặc biểu mẫu web đơn giản)
- Đã từng tham gia vào dự án Champollion trước đây

---

## 5. Quản trị dữ liệu

Mọi đóng góp của người nói đều được quản lý bởi các chính sách dữ liệu hướng tới OCAP® của dự án:

- **Quyền sở hữu:** Đánh giá chất lượng của người nói vẫn là đóng góp trí tuệ của chính họ. Họ sẽ được ghi nhận tên tuổi (hoặc ẩn danh, tùy theo lựa chọn của họ) trong bất kỳ ấn phẩm nào.
- **Quyền kiểm soát:** Người nói có thể rút lại các đánh giá của mình bất kỳ lúc nào. Việc rút lại sẽ xóa dữ liệu của họ khỏi tất cả các phân tích.
- **Quyền truy cập:** Dữ liệu đánh giá được lưu trữ trên cơ sở hạ tầng do tổ chức quản trị cộng đồng kiểm soát (khi được thành lập) hoặc trên nền tảng ưu tiên của người nói.
- **Quyền sở hữu thực tế (Possession):** Dữ liệu đánh giá thô không bao giờ được công bố. Chỉ có các số liệu thống kê tổng hợp (hệ số tương quan, mức độ đồng thuận giữa các người đánh giá) mới xuất hiện trong các ấn phẩm.
- **Thù lao:** Người nói được trả tiền cho thời gian của họ bất kể chúng tôi có sử dụng các đánh giá của họ hay không. Việc thanh toán không phụ thuộc vào kết quả.

---

## 6. Quyền lợi của người nói

Ngoài thù lao:

- **Đồng tác giả** trên bất kỳ ấn phẩm nào sử dụng đánh giá của họ (nếu muốn)
- **Được ghi nhận** trong tất cả các tài liệu của dự án
- **Quyền truy cập sớm** vào các công cụ và kết quả đánh giá
- **Đóng góp ý kiến** về cách sử dụng các số đo — nếu người nói cho rằng "linter của bạn sai về X", chúng tôi sẽ sửa linter
- **Quyền phủ quyết** đối với việc công bố các kết quả mà họ thấy có vấn đề

---

## 7. Cách thức bắt đầu

Nếu bạn là người nói song ngữ tiếng Cree–Anh quan tâm đến việc tham gia, hoặc nếu bạn biết ai đó có thể quan tâm:

1. **Liên hệ với chúng tôi** tại [project email/contact] — không yêu cầu cam kết, chỉ là một cuộc trò chuyện
2. **Chúng tôi giải thích các nhiệm vụ** bằng ngôn ngữ bình dân (không dùng thuật ngữ chuyên ngành)
3. **Bạn chọn các nhiệm vụ** mà bạn quan tâm (A, B, C hoặc bất kỳ sự kết hợp nào)
4. **Chúng tôi thiết lập một lịch trình** phù hợp với bạn (các khoảng thời gian 2 giờ, thời gian linh hoạt)
5. **Bạn đánh giá các bản dịch** qua bảng tính hoặc biểu mẫu web — từ bất kỳ đâu, vào thời gian riêng của bạn
6. **Chúng tôi thanh toán nhanh chóng** — trong vòng 2 tuần sau khi hoàn thành mỗi phần nhiệm vụ

---

## 8. Điều gì xảy ra sau đó

Với dữ liệu xác thực từ người nói, chúng tôi có thể:

1. **Công bố các hệ số tương quan của số đo** — chứng minh (hoặc bác bỏ) rằng điểm số LYSS phản ánh đúng đánh giá của con người
2. **Hiệu chuẩn lại các số đo** — điều chỉnh trọng số, ngưỡng và các lớp tương đương dựa trên phản hồi của người nói
3. **Sửa lỗi linter** — loại bỏ các trường hợp tương đương sai, thêm các trường hợp còn thiếu
4. **Sửa danh sách cho phép của FST** — thêm các từ hợp lệ mà FST từ chối một cách không chính xác
5. **Nộp bài cho một hội nghị/tạp chí học thuật** — với những người nói là đồng tác giả, thiết lập LYSS như một số đo đã được xác thực để đánh giá dịch máy cho các ngôn ngữ đa tổng hợp (polysynthetic language)

Nếu không có sự xác thực của người nói, LYSS vẫn chỉ là một công cụ kỹ thuật. Có nó, LYSS sẽ trở thành một số đo đánh giá có cơ sở khoa học. Đó là sự khác biệt giữa "chúng tôi đã xây dựng một thứ gì đó" và "chúng tôi đã chứng minh nó hoạt động hiệu quả".