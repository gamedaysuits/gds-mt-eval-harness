---
sidebar_position: 8
title: "Chi tiết giải thưởng"
slug: '/specifications/prizes'
related:
  - label: "How Speakers Get Paid"
    to: /docs/perspectives/how-speakers-get-paid
    kind: position
    note: "The plain-language version of these numbers"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
---
# Quy định Giải thưởng

> **Mục đích.** Tài liệu này xác định cấu trúc quỹ giải thưởng, các điều kiện ngưỡng, quy trình nhận giải và các quy tắc dành cho MT Eval Arena. Tài liệu này chỉ rõ chính xác thế nào là "có khả năng dịch máy" theo các thuật ngữ có thể đo lường được, và tiền thưởng được giải ngân dưới những điều kiện nào. Tài liệu này tham chiếu đến SCORING_SPEC để biết định nghĩa về các chỉ số và BENCHMARK_SPEC để biết giao thức đánh giá — tài liệu này không lặp lại các nội dung đó.
>
> **Trạng thái:** ĐANG HOẠT ĐỘNG. Giải thưởng của Nhà sáng lập (§2.1) đã được cấp vốn và đang hoạt động.
>
> Cập nhật lần cuối: 2026-06-04

---

## 1. Triết lý

### 1.1 Giải thưởng dành cho Sự bứt phá, Không phải cho Sự tham gia

Tiền thưởng chỉ được giải ngân khi một phương pháp chứng minh được rằng nó đạt đến một ngưỡng năng lực xác định. Không có giải khuyến khích, giải á quân hay giải thưởng an ủi. Nếu không ai vượt qua được rào cản, không ai được nhận tiền. Đây là thiết kế có chủ đích — điều đó có nghĩa là các nhà tài trợ chỉ trả tiền cho những kết quả thực sự hiệu quả.

### 1.2 Xác thực từ Cộng đồng là Không thể thương lượng

Các chỉ số tự động chỉ là các đại diện (SCORING_SPEC §1.1). Một phương pháp có thể đạt điểm cao trên chrF++ và tỷ lệ chấp nhận FST trong khi vẫn tạo ra bản dịch mà không người bản xứ nào chấp nhận. **Mọi yêu cầu nhận giải thưởng đều cần có sự xác thực từ cộng đồng** — những người nói song ngữ phải xác nhận rằng bản dịch có thể sử dụng được. Đây là cổng xác thực của con người (BENCHMARK_SPEC §7).

### 1.3 Chuyển giao Quyền sở hữu là một phần của Thỏa thuận

Các phương pháp nhận giải thưởng phải tuân theo điều khoản chuyển giao quyền sở hữu (BENCHMARK_SPEC §8.3). Nhà phát triển vẫn giữ quyền ghi công và quyền công bố. Tổ chức quản trị có quyền sử dụng, sửa đổi, phân phối và thương mại hóa phương pháp này cho ngôn ngữ của họ. Đây không phải là một hình phạt — đây chính là mục đích. Tiền thưởng tài trợ cho việc tạo ra công nghệ thuộc về cộng đồng ngôn ngữ.

### 1.4 Chống gian lận

Các ngưỡng giải thưởng được xác định dựa trên **đánh giá tiêu chuẩn vàng (gold-standard)** (tập dữ liệu kiểm thử bí mật, được chạy bởi tổ chức quản trị trong môi trường sandbox). Các nhà phát triển không bao giờ được xem dữ liệu kiểm thử. Điều này được thực thi bằng kiến trúc hệ thống — chứ không phải là một chính sách dựa trên danh dự. Xem BENCHMARK_SPEC §8.2.

### 1.5 Bản quyền Kho ngữ liệu: Các kho ngữ liệu phi thương mại không được tham gia Nhánh Giải thưởng

Một số kho ngữ liệu được sử dụng trong quá trình phát triển phương pháp có giấy phép phi thương mại — ví dụ: kho ngữ liệu EdTeKLA Cree Language Textbook là **CC BY-NC-SA 4.0**. Các kho ngữ liệu này **chỉ dành cho nhánh nghiên cứu/phát triển**:

1. **Các kho ngữ liệu tiêu chuẩn vàng của giải thưởng không được chứa nội dung kho ngữ liệu có giấy phép NC (phi thương mại).** Các phân đoạn kiểm thử tiêu chuẩn vàng là các bản gốc do cộng đồng ủy thác (xem Chiến lược Hợp tác Kho ngữ liệu) — do con người biên soạn riêng cho giải thưởng, với các quyền được giải phóng để đánh giá và triển khai thương mại ngay từ đầu.
2. **Một phương pháp nhận giải thưởng không được chứa nội dung kho ngữ liệu có giấy phép NC** (ví dụ: làm dữ liệu hướng dẫn, ví dụ nhúng hoặc bảng tra cứu). Phương pháp được chuyển giao nhằm mục đích triển khai thương mại bởi tổ chức quản trị (BENCHMARK_SPEC §8.3, Thỏa thuận Nộp Phương pháp §6); nội dung có giấy phép NC bên trong nó sẽ làm hỏng việc triển khai đó.
3. **Các nhà phát triển có thể tự do sử dụng các kho ngữ liệu có giấy phép NC để phát triển và tự đánh giá** — đó là mục đích của nhánh phát triển. Hạn chế này áp dụng cho những gì được nộp và những gì được triển khai, chứ không áp dụng cho cách nhà phát triển học hỏi.

### 1.6 Các lớp Phụ thuộc quyết định Đủ điều kiện nhận Giải thưởng

Mọi hoạt động đánh giá giải thưởng đều diễn ra trong môi trường sandbox (§1.4), và các phương pháp đoạt giải sẽ được chuyển giao cho tổ chức quản trị (§1.3). Cả hai thực tế này đều áp dụng cùng một ràng buộc: **mọi thứ mà một phương pháp phụ thuộc vào phải là thứ mà nhà phát triển có quyền đưa vào sandbox và chuyển giao cho cộng đồng.** Mỗi bài nộp đều phải khai báo một lớp phụ thuộc — được định nghĩa trong [Tài liệu kỹ thuật Giao diện Phương pháp](/docs/specifications/methods#method-validity-and-dependency-classes), với các điều khoản chấp nhận trong Thỏa thuận Nộp Phương pháp §2.6 — và tính đủ điều kiện sẽ tuân theo lớp đó:

| Lớp phụ thuộc | Đủ điều kiện nhận giải? | Điều kiện |
|---|---|---|
| **S** — tự đóng gói (self-contained) | ✅ Có | Không có điều kiện nào khác ngoài các điều kiện ngưỡng ở §2 |
| **O** — bên ngoài mở (ví dụ: AGPL FST được sao lưu khi nộp) | ✅ Có | Các thành phần tạo tác (artifacts) được ghim cố định và tích hợp trực tiếp (vendored) vào bài nộp; giấy phép cho phép chuyển giao cho cộng đồng; các điều khoản copyleft được bảo toàn (cộng đồng nhận được các quyền tương tự như giấy phép cấp cho mọi người) |
| **A1** — suy luận LLM có thể thay thế | ⚠️ Có điều kiện | Mô hình được khai báo, ghim cố định và có thể thay thế (phải chạy trên một mô hình trọng số mở do cộng đồng lưu trữ); việc đánh giá được định tuyến qua cổng LLM của sandbox (🔲 đã lên kế hoạch — các phương pháp A1 không thể tạo ra điểm tiêu chuẩn vàng cho đến khi cổng này đi vào hoạt động); việc chuyển giao sẽ chuyển giao toàn bộ công thức (prompts, dữ liệu hướng dẫn, mã nguồn), chứ không phải mô hình |
| **A2** — API dịch vụ/dữ liệu bên ngoài không thể thay thế | ❌ Chưa được | Không đủ điều kiện cho đến khi bên giữ bản quyền cấp quyền đưa vào sandbox và quyền chuyển giao. Được phép xuất hiện trên bảng xếp hạng mở với nhãn "phụ thuộc bên ngoài" hiển thị rõ ràng |
| **X** — nội dung đi kèm không có bản quyền | ❌ Không bao giờ | Không được chấp nhận ở bất kỳ nhánh nào |

Lớp của một phương pháp là lớp hạn chế nhất trong số các phụ thuộc đã khai báo của nó. Các phụ thuộc không được khai báo thuộc bất kỳ lớp nào đều dẫn đến việc bị loại (§5).

---

## 2. Các Quỹ Giải thưởng đang Hoạt động

### 2.1 Giải thưởng của Nhà sáng lập — EN→Plains Cree (nêhiyawêwin)

| Trường | Giá trị |
|-------|-------|
| **Quỹ giải thưởng** | **$10,000 CAD** |
| **Cặp ngôn ngữ** | Tiếng Anh → Plains Cree (EN→CRK) |
| **Được tài trợ bởi** | Nhà sáng lập dự án Champollion |
| **Trạng thái** | **ĐANG HOẠT ĐỘNG** — đang nhận bài nộp |
| **Mở nhận bài** | Khi kho ngữ liệu tiêu chuẩn vàng + tổ chức quản trị đã sẵn sàng |
| **Hết hạn** | Không hết hạn. Giải thưởng vẫn hoạt động cho đến khi có người nhận hoặc bị rút lại một cách rõ ràng. |

#### Các Điều kiện Ngưỡng

Một phương pháp sẽ nhận được Giải thưởng của Nhà sáng lập bằng cách đáp ứng đồng thời **TẤT CẢ** các điều kiện sau:

| # | Điều kiện | Chỉ số | Ngưỡng | Cơ sở lý luận |
|---|-----------|--------|-----------|-----------|
| 1 | **Composite score** | `composite` (SCORING_SPEC §4) | **≥ 0.80** | Nằm giữa mức Có thể triển khai (0.70) và Trôi chảy (0.85). Đòi hỏi chất lượng cao trên tất cả các khía cạnh chỉ số — không chỉ là tính hợp lệ về mặt hình thái. |
| 2 | **FST acceptance** | `fst_acceptance_rate` (SCORING_SPEC §2.2) | **≥ 0.99 (99%+)** | Về mặt hiệu quả, tất cả các từ đầu ra phải là các dạng hợp lệ về mặt hình thái được công nhận bởi GiellaLT FST. Mức dung sai 1% dành cho các trường hợp đặc biệt (danh từ riêng, từ mới, từ mượn) mà FST có thể không bao gồm một cách hợp lý. Đây là cổng chất lượng quyết định đối với dịch máy đa tổng hợp (polysynthetic MT) — nếu FST từ chối hơn 1% số từ, phương pháp đó đang tạo ra các dạng từ không tồn tại trong ngôn ngữ. Toàn bộ mục đích của giải thưởng này là để mua một hệ thống không làm biến dạng ngôn ngữ. |
| 3 | **chrF++** | `chrf_plus_plus` (SCORING_SPEC §2.1) | **≥ 55.0** | Độ trùng lặp n-gram ký tự phải vượt quá 55 trên thang điểm 0–100. Đảm bảo sự tương đồng ở mức độ bề mặt với các bản dịch tham chiếu, chứ không chỉ là tính hợp lệ về mặt hình thái. |
| 4 | **Xác thực từ cộng đồng** | Đánh giá bởi con người (BENCHMARK_SPEC §7) | **≥ 70% "chấp nhận được" hoặc "xuất sắc"** | Một mẫu phân tầng của các kết quả đầu ra (≥30 mục trên các cấp độ khó từ 2–5) được đánh giá bởi ≥2 người nói song ngữ CRK. Ít nhất 70% số mục được đánh giá phải nhận được xếp hạng "chấp nhận được" (acceptable) hoặc "xuất sắc" (excellent). |
| 5 | **Đánh giá tiêu chuẩn vàng** | Thực thi trong sandbox (BENCHMARK_SPEC §8.2) | **Bắt buộc** | Tất cả các chỉ số tự động phải được tính toán dựa trên phân đoạn kho ngữ liệu `gold_standard`, được chạy bởi tổ chức quản trị trong môi trường sandbox. Điểm số trên tập phát triển (development-set) không được tính. |
| 6 | **Khả năng tái lặp** | Khớp dấu vết đặc trưng (BENCHMARK_SPEC §3.8) | **±2%** | Tổ chức quản trị phải có khả năng chạy lại phương pháp và đạt được điểm số trong khoảng ±2% so với thẻ chạy (run card) đã nộp. |

> **Tại sao lại là FST 99% trở lên?** Vấn đề trung tâm trong dịch máy đối với các ngôn ngữ đa tổng hợp là hiện tượng ảo giác (hallucination) — các LLM tạo ra các chuỗi ký tự *trông có vẻ* giống ngôn ngữ đích nhưng lại không hợp lệ về mặt hình thái. Một phương pháp tạo ra 95% đầu ra hợp lệ vẫn chứa 5% từ bịa đặt — đây là mức nhiễu không thể chấp nhận được đối với bất kỳ mục đích sử dụng thực tế nào. Ngưỡng 99%+ đòi hỏi hiện tượng ảo giác gần như bằng không trong khi vẫn cho phép các trường hợp đặc biệt hiếm gặp (một danh từ riêng mà FST không biết, một từ mới hợp pháp). Nếu một phương pháp không thể đạt được tỷ lệ chấp nhận FST từ 99% trở lên, nó vẫn chưa giải quyết được vấn đề.
>
> **Tại sao lại là điểm composite 0.80?** Mức này nằm giữa Có thể triển khai (0.70) và Trôi chảy (0.85). Một phương pháp đạt mức 0.80 với tỷ lệ chấp nhận FST từ 99% trở lên sẽ tạo ra đầu ra mà hầu như mọi từ đều là từ tiếng Cree có thật *và* chất lượng dịch thuật tổng thể đạt mức cao trên các khía cạnh bề mặt, cấu trúc và ngữ nghĩa. Cổng xác thực từ cộng đồng (điều kiện số 4) đảm bảo đây không chỉ là việc gian lận chỉ số — người nói bản xứ phải xác nhận rằng kết quả đầu ra thực sự có thể sử dụng được.

#### Ý nghĩa thực tế của Ngưỡng này

Tại mức composite ≥ 0.80 với FST ≥ 0.99 và chrF++ ≥ 55, một người nói song ngữ thường sẽ thấy:

- **Hầu như mọi** từ đầu ra đều là từ tiếng Cree có thật (FST xác thực trên 99% — gần như không có các dạng từ ảo giác)
- Các phạm trù ngữ pháp chính (ngôi, số, thì) đều chính xác trong hầu hết các mục
- Trật tự từ nhìn chung là tự nhiên
- Ý nghĩa được bảo toàn một cách đáng tin cậy
- Các lỗi còn lại là lỗi ngôn ngữ thực tế (biến hình từ sai, phân biệt trực tiếp/gián tiếp (obviation) không chính xác, không khớp về tính động vật/bất động vật (animacy)) — chứ không phải là các từ bịa đặt
- Một người nói trôi chảy có thể sử dụng kết quả đầu ra như một bản nháp chất lượng cao và sửa nó nhanh hơn đáng kể so với việc dịch lại từ đầu

Đây là một hệ thống **không làm biến dạng ngôn ngữ.** Nó may ra không hoàn hảo, nhưng mọi từ nó tạo ra đều là một từ có thật. Đó là mức tối thiểu để thể hiện sự tôn trọng trong dịch máy đối với một ngôn ngữ đa tổng hợp.

---

## 3. Quy trình Nhận Giải thưởng

### 3.1 Nộp bài

1. Nhà phát triển nộp phương pháp hoàn chỉnh, có thể chạy được của họ cho tổ chức quản trị:
   - Toàn bộ mã nguồn
   - Tất cả các phụ thuộc (dữ liệu hướng dẫn, từ điển, cấu hình FST, prompts)
   - Hướng dẫn cài đặt và thực thi
   - Một tệp README mô tả cách tiếp cận của phương pháp
   - Một thẻ chạy trên tập phát triển (development-set run card) hiển thị điểm số ước tính (để sàng lọc trước)

2. Nhà phát triển ký các điều khoản tham gia, bao gồm:
   - Điều khoản chuyển giao quyền sở hữu (BENCHMARK_SPEC §8.3)
   - Tuyên bố không huấn luyện trên dữ liệu đánh giá
   - Cam kết về khả năng tái lặp

### 3.2 Đánh giá

1. Tổ chức quản trị cài đặt và chạy phương pháp trong một khung thử nghiệm (harness) được sandbox hóa đối với kho ngữ liệu `gold_standard`
2. Các chỉ số tự động được tính toán (composite, FST, chrF++, v.v.)
3. Nếu đạt được các ngưỡng tự động (điều kiện 1–3), tổ chức quản trị sẽ tiến hành đánh giá từ cộng đồng
4. Nếu KHÔNG đạt được các ngưỡng tự động, nhà phát triển sẽ nhận được điểm số và phản hồi. Không có hoạt động đánh giá từ cộng đồng nào được kích hoạt.

### 3.3 Đánh giá từ Cộng đồng

1. Một mẫu phân tầng của các kết quả đầu ra (≥30 mục, bao gồm các cấp độ khó từ 2–5) được trình bày cho những người nói song ngữ
2. Có ít nhất 2 người đánh giá độc lập xếp hạng cho mỗi mục
3. Thang điểm đánh giá: **từ chối (reject)** / **hiểu ý chính (gist)** / **chấp nhận được (acceptable)** / **xuất sắc (excellent)**
4. Nếu ≥70% số mục nhận được đánh giá "chấp nhận được" hoặc "xuất sắc" từ cả hai người đánh giá, quá trình xác thực từ cộng đồng sẽ được thông qua

### 3.4 Thanh toán

1. Tất cả 6 điều kiện đều được đáp ứng
2. Tổ chức quản trị xác nhận kết quả
3. Tiền thưởng được thanh toán trong vòng 30 ngày kể từ ngày xác nhận
4. Quyền sở hữu phương pháp được chuyển giao theo BENCHMARK_SPEC §8.3
5. Kết quả được công bố trên bảng xếp hạng với cấp độ xác minh "Đã được Cộng đồng Xác thực" (Community Validated)

### 3.5 Nộp bài Nhiều lần

- Cùng một nhà phát triển/nhóm có thể nộp bài nhiều lần
- Mỗi bài nộp được đánh giá độc lập
- Nếu một phương pháp được cải tiến và nộp lại, chỉ có thẻ chạy mới nhất được tính
- Giải thưởng được trao cho phương pháp **đầu tiên** vượt qua tất cả các ngưỡng — giải thưởng không được chia nhỏ

### 3.6 Bài nộp theo Nhóm

- Các nhóm và các cặp Người lớn tuổi - Thanh niên (Elder-youth) đều đủ điều kiện
- Việc phân chia giải thưởng trong nhóm là trách nhiệm của chính nhóm đó
- Tất cả các thành viên trong nhóm phải ký vào các điều khoản tham gia
- Phần ghi công trên bảng xếp hạng sẽ liệt kê tất cả các thành viên trong nhóm

---

## 4. Các Quỹ Giải thưởng trong Tương lai {#4-future-prize-pools}

Giải thưởng của Nhà sáng lập là hạt giống. Các quỹ giải thưởng bổ sung sẽ do các nhà tài trợ cấp vốn. Mỗi quỹ giải thưởng mới sẽ được ghi nhận thành một tiểu mục mới của §2 với các thông tin riêng:

- Số tiền thưởng và đơn vị tiền tệ
- Cặp ngôn ngữ
- Ghi công nhà tài trợ
- Các điều kiện ngưỡng (có thể khác với Giải thưởng của Nhà sáng lập)
- Ngày hết hạn (nếu có)
- Bất kỳ điều kiện đặc biệt nào

### 4.1 Mẫu Giải thưởng của Nhà tài trợ

Các nhà tài trợ có thể tài trợ cho các quỹ giải thưởng với bất kỳ số tiền nào. Các cấp độ gợi ý:

| Cấp độ | Số tiền | Ngưỡng gợi ý |
|------|--------|---------------------|
| **Hạt giống (Seed)** | $5,000–$15,000 | Có thể triển khai (composite ≥ 0.70) + xác thực từ cộng đồng |
| **Bứt phá (Breakthrough)** | $25,000–$50,000 | Trôi chảy (composite ≥ 0.85) + xác thực từ cộng đồng |
| **Giải đặc biệt (Grand Prize)** | $100,000+ | Trôi chảy + bao phủ đa phong cách ngôn ngữ (multi-register) + tích hợp triển khai |

Các nhà tài trợ cũng có thể tài trợ cho:
- **Phần thưởng cải tiến (Improvement bounties)** — khoản thanh toán cố định cho mỗi 5 điểm cải tiến của chrF++ so với kết quả tốt nhất hiện tại
- **Giải thưởng theo phong cách ngôn ngữ (Register prizes)** — các giải thưởng riêng biệt cho các phong cách ngôn ngữ cụ thể (trang trọng, nghi lễ, giáo dục)
- **Giải thưởng tốc độ (Speed prizes)** — điểm số được điều chỉnh theo chi phí tốt nhất (SCORING_SPEC §6.3)

### 4.2 Ký quỹ Quỹ Giải thưởng

Tất cả các khoản tiền thưởng được giữ trong tài khoản ký quỹ (do dự án hoặc một bên ủy thác được chỉ định quản lý) cho đến khi các điều kiện ngưỡng được đáp ứng. Nếu một giải thưởng hết hạn mà không có người nhận, tiền tài trợ sẽ được hoàn trả cho nhà tài trợ hoặc chuyển sang một quỹ giải thưởng mới theo quyết định của nhà tài trợ.

---

## 5. Bị loại

Một bài nộp sẽ bị loại nếu:

1. **Huấn luyện trên dữ liệu đánh giá.** Phương pháp đã tiếp xúc với các mục trong kho ngữ liệu `gold_standard` hoặc `held_out`. (Điều này được ngăn chặn bằng kiến trúc thông qua việc thực thi trong sandbox — nhưng nếu phát hiện bằng chứng về sự rò rỉ dữ liệu, kết quả sẽ bị hủy bỏ.)
2. **Không thể tái lặp.** Tổ chức quản trị không thể tái lặp điểm số trong khoảng ±2%.
3. **Các phụ thuộc không được khai báo hoặc không đủ điều kiện.** Phương pháp yêu cầu quyền truy cập trong thời gian chạy (runtime) vào các dịch vụ bên ngoài vượt quá những gì bản khai báo phụ thuộc của nó công bố, hoặc lớp phụ thuộc thực tế của nó là A2 hoặc X (§1.6). Việc suy luận LLM Lớp A1 đã khai báo được định tuyến qua cổng đánh giá là được phép; bất kỳ phụ thuộc mạng thời gian chạy nào khác — và bất kỳ phụ thuộc không được khai báo thuộc bất kỳ lớp nào — đều dẫn đến việc bị loại.
4. **Chưa ký các điều khoản tham gia.** Tất cả các thành viên trong nhóm phải đồng ý chuyển giao quyền sở hữu.
5. **Phát hiện hành vi gian lận chỉ số (gaming).** Kết quả đầu ra được tối ưu hóa cho chỉ số thay vì chất lượng dịch thuật (bị phát hiện bởi hoạt động đánh giá từ cộng đồng và/hoặc các kiểm tra chống gian lận theo BENCHMARK_SPEC §9.3).

---

## 6. Mối quan hệ với các Tài liệu kỹ thuật khác

| Tài liệu này | Tham chiếu | Để |
|--------------|-----------|-----|
| Các điều kiện ngưỡng ở §2 | SCORING_SPEC §4 (composite), §2.1–2.2 (metrics), §5 (tiers) | Định nghĩa và thang đo chỉ số |
| Xác thực từ cộng đồng ở §2 | BENCHMARK_SPEC §7 | Giao thức đánh giá bởi con người |
| Thực thi trong sandbox ở §3 | BENCHMARK_SPEC §8.2 | Cơ chế chủ quyền |
| Chuyển giao quyền sở hữu ở §3 | BENCHMARK_SPEC §8.3 | Các điều khoản chuyển giao SHTT (IP) |
| Các lớp phụ thuộc ở §1.6 | Tài liệu kỹ thuật Giao diện Phương pháp; Thỏa thuận Nộp Phương pháp §2.6; BENCHMARK_SPEC §8.6 | Định nghĩa lớp, các điều khoản chấp nhận, chính sách mạng sandbox |
| Giải thưởng điều chỉnh theo chi phí ở §4 | SCORING_SPEC §6.3 | Công thức điều chỉnh theo chi phí |

---

## 7. Đồng bộ hóa Mã nguồn – Tài liệu kỹ thuật

### 7.1 Nguồn Chuẩn (Canonical Source)

Tài liệu này (`arena/website/docs/specifications/prize-spec.md`) là nguồn chuẩn cho:
- Định nghĩa quỹ giải thưởng (§2)
- Các điều kiện ngưỡng (§2.x)
- Quy trình nhận giải (§3)
- Quy tắc bị loại (§5)

### 7.2 Yêu cầu Triển khai

Khi một quỹ giải thưởng được kích hoạt:
1. Giao diện người dùng (UI) của bảng xếp hạng phải hiển thị các giải thưởng đang hoạt động và các điều kiện ngưỡng của chúng
2. Các thẻ chạy (run cards) đáp ứng các ngưỡng tự động (đi kiện 1–3) phải được gắn cờ để đánh giá từ cộng đồng
3. Trường `quality_tier` trong lược đồ thẻ chạy (run card schema) đã ghi nhận cấp độ ("deployable", "fluent")
4. Không cần thay đổi mã nguồn mới nào đối với khung thử nghiệm (harness) — tài liệu kỹ thuật giải thưởng là một lớp chính sách nằm trên hệ thống tính điểm hiện tại

---

*Cấu trúc giải thưởng phải tương thích với các điều khoản chuyển giao quyền sở hữu. Người chiến thắng có thể nhận giải thưởng, nhưng phương pháp đó sẽ trở thành tài sản của tổ chức quản trị nếu nó đạt đến cấp độ Có thể triển khai (Deployable). Đây là thiết kế có chủ đích — giải thưởng tài trợ cho việc tạo ra công nghệ thuộc về cộng đồng ngôn ngữ.*