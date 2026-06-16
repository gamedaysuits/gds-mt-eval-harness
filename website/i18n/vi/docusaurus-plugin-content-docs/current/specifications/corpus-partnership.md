---
sidebar_position: 9
title: "Chiến lược hợp tác kho ngữ liệu"
slug: '/specifications/corpus-partnership'
---
# Chiến lược Hợp tác Xây dựng Ngữ liệu: Thiết lập Ngữ liệu Đánh giá Thông qua các Khoa Ngôn ngữ học Học thuật

> **Mục đích.** Tài liệu này cung cấp quy trình làm việc hoàn chỉnh để thiết lập một ngữ liệu đánh giá dịch máy thông qua quan hệ hợp tác với khoa ngôn ngữ học. Tài liệu bao gồm những gì chúng tôi cần khoa cung cấp, cấu trúc của ngữ liệu, cách niêm phong mã hóa ngữ liệu, cách thức hoạt động của quá trình đánh giá trong sandbox, và những gì khoa nhận lại được. Đây là tài liệu bạn mang theo khi gặp gỡ đối tác học thuật tiềm năng.
>
> **Đối tượng độc giả.** Trưởng khoa, nghiên cứu viên chính (PI), điều phối viên nghiên cứu, và giám đốc chương trình ngôn ngữ bản địa tại các trường đại học có chương trình tài liệu hóa ngôn ngữ hoặc xử lý ngôn ngữ tự nhiên (NLP) đang hoạt động.
>
> **Tài liệu đi kèm:**
> - [Giao thức Xác thực Người nói](/docs/specifications/speaker-validation) — yêu cầu người nói song ngữ *đánh dấu* các bản dịch hiện có (đánh giá chất lượng, xác thực linter, kiểm duyệt FST)
> - [Đặc tả Chuẩn đánh giá](/docs/specifications/benchmark) — đặc tả kỹ thuật đầy đủ cho ngữ liệu, thẻ chạy (run card), và giao thức đánh giá
> - [Chủ quyền Dữ liệu](/docs/sovereignty/data-sovereignty) — OCAP®, CARE, và lý do tại sao việc chuyển giao quyền sở hữu lại quan trọng
>
> Cập nhật lần cuối: 2026-06-07

---

## 1. Kết quả của Quan hệ Hợp tác này

Một **ngữ liệu đánh giá được niêm phong**: một tập hợp các cặp văn bản song song được tuyển chọn (ngôn ngữ nguồn → ngôn ngữ đích) đóng vai trò là ground truth để đo lường chất lượng dịch máy. Các phương pháp được thử nghiệm với ngữ liệu này trong một môi trường sandbox — các nhà phát triển không bao giờ nhìn thấy dữ liệu kiểm thử.

Quan hệ hợp tác này tạo ra ba sản phẩm:

| Sản phẩm | Mô tả | Bên kiểm soát |
|----------|-----------|-----------------|
| **Ngữ liệu phát triển** | Hơn 100–200 cặp văn bản song song công khai để phát triển phương pháp | Công bố công khai (CC BY-NC-SA 4.0 hoặc tương đương) |
| **Tập kiểm thử chuẩn vàng** | 50–150 cặp văn bản song song bí mật để đánh giá chính thức | Tổ chức quản trị cộng đồng (được niêm phong mã hóa) |
| **Bộ kiểm thử chẩn đoán** | 10–50 cặp tương phản mục tiêu nhằm kiểm thử các hiện tượng ngôn ngữ cụ thể | Công bố công khai |

Ngữ liệu phát triển cho phép bất kỳ ai cũng có thể xây dựng các phương pháp dịch thuật. Tập chuẩn vàng đảm bảo các phương pháp đó được kiểm thử một cách trung thực. Bộ chẩn đoán giúp phát hiện các lỗi cụ thể (ví dụ: "hệ thống này có xử lý được hiện tượng obviation không?").

---

## 2. Những việc Khoa cần thực hiện

### Giai đoạn 1: Thiết kế Ngữ liệu (2–4 tuần, thời gian của nghiên cứu viên)

**Người phụ trách:** PI hoặc nghiên cứu sinh sau tiến sĩ (postdoc) có chuyên môn về ngôn ngữ đích.

1. **Lựa chọn lĩnh vực tài liệu nguồn.** Chọn 4–6 lĩnh vực thực tế mà cộng đồng ngôn ngữ thực sự có nhu cầu dịch thuật. Hệ thống phân loại của chúng tôi hỗ trợ 16 lĩnh vực (xem Đặc tả Chuẩn đánh giá §2.7):

   | Độ ưu tiên | Lĩnh vực | Lý do |
   |----------|--------|-----|
   | 🔴 Cao | `edu` — Giáo dục | Sách giáo khoa, chương trình giảng dạy — nhu cầu trực tiếp của cộng đồng |
   | 🔴 Cao | `gov` — Chính phủ | Tài liệu của hội đồng bộ tộc, chính sách — nhu cầu thực tế hàng ngày |
   | 🔴 Cao | `medical` — Y tế | Biểu mẫu tiếp nhận của phòng khám, thông tin sức khỏe — cực kỳ quan trọng đối với an toàn |
   | 🟡 Trung bình | `conv` — Giao tiếp | Giao tiếp hàng ngày — thiết lập mức độ lưu loát cơ bản |
   | 🟡 Trung bình | `legal` — Pháp lý | Tài liệu về quyền lợi, hiệp ước — có ý nghĩa quan trọng với cộng đồng |
   | 🟢 Thấp hơn | `literary` — Văn học/Vân hóa | Truyện kể, lịch sử truyền miệng — bảo tồn văn hóa |

2. **Soạn thảo tài liệu thiết kế ngữ liệu** nêu rõ:
   - Quy mô mục tiêu cho từng phân đoạn (development, gold_standard, diagnostic)
   - Phân bổ mức độ khó (xem §3.3 bên dưới)
   - Phạm vi ngữ vực và lĩnh vực
   - Tiêu chí lựa chọn câu nguồn (không dùng văn bản tổng hợp nhân tạo, không chỉ dùng Kinh Thánh)
   - Kế hoạch tuyển chọn người nói

3. **Gửi bản thiết kế cho chúng tôi để xem xét.** Chúng tôi sẽ xác thực bản thiết kế dựa trên lược đồ ngữ liệu (Đặc tả Chuẩn đánh giá §2) và gửi lại phản hồi trong vòng 1 tuần.

### Giai đoạn 2: Tạo Câu Nguồn (4–8 tuần, thời gian của người nói)

**Người phụ trách:** Điều phối viên nghiên cứu làm việc với những người nói song ngữ.

1. **Tạo hoặc lựa chọn các câu nguồn** trên khắp các lĩnh vực và mức độ khó đã lên kế hoạch. Nguồn có thể là:
   - Tài liệu song ngữ đã xuất bản hiện có (sách giáo khoa, tài liệu chính phủ)
   - Các câu mới được thu thập nhằm bao quát các hiện tượng ngôn ngữ cụ thể
   - Được điều chỉnh từ các tài liệu thực tế (chương trình họp của hội đồng bộ tộc, biểu mẫu phòng khám, tài liệu giáo dục)

2. **Mỗi câu nguồn phải có:**
   - Thẻ lĩnh vực (từ hệ thống phân loại 16 mã)
   - Thẻ ngữ vực (giao tiếp, trang trọng, kỹ thuật, nghi lễ, giáo dục)
   - Thẻ ngữ cảnh (chào hỏi, tuyên bố, câu hỏi, hướng dẫn, tự sự, nhãn, lỗi)
   - Mức độ khó ước tính (1–5, xem §3.3)
   - Thẻ nguồn gốc (sách giáo khoa, thu thập trực tiếp, ngữ liệu, gold_standard)

3. **Dịch từng câu nguồn** sang ngôn ngữ đích, do người nói song ngữ thực hiện. Việc có nhiều bản dịch tham chiếu cho mỗi mục là rất giá trị nhưng không bắt buộc.

4. **Tùy chọn, thêm phân tích hình thái** cho mỗi bản dịch tham chiếu:
   - Chú giải liên dòng (phân tích chi tiết từng hình vị)
   - Chuỗi thẻ FST (nếu có FST cho ngôn ngữ đó)
   - Ghi chú của người dịch về các biến thể phương ngôn, tính mơ hồ, hoặc bối cảnh văn hóa

### Giai đoạn 3: Đảm bảo Chất lượng (2–4 tuần)

**Người phụ trách:** Nhà ngôn ngữ học có chuyên môn về ngôn ngữ đích.

1. **Đánh giá chéo.** Mỗi bản dịch nên được xem xét bởi ít nhất một người nói song ngữ khác (người không thực hiện bản dịch gốc). Người đánh giá sẽ kiểm tra:
   - Bản dịch có chính xác không?
   - Nghe có tự nhiên không?
   - Đánh giá mức độ khó có chính xác không?
   - Có biến thể nào được chấp nhận cần lưu ý không?

2. **Chạy qua công cụ xác thực lược đồ của chúng tôi.** Chúng tôi cung cấp một tập lệnh để xác thực ngữ liệu dựa trên lược đồ đầu vào (Đặc tả Chuẩn đánh giá §2.2). Tập lệnh sẽ kiểm tra:
   - Sự hiện diện của các trường bắt buộc
   - Mã lĩnh vực hợp lệ
   - Mức độ khó là số nguyên từ 1–5
   - Không trùng lặp ID
   - Mã hóa ký tự (chuẩn hóa UTF-8 NFC)

3. **Nếu có FST cho ngôn ngữ đó,** hãy chạy các bản dịch tham chiếu qua FST. Mọi từ trong bản dịch tham chiếu phải hợp lệ với FST. Những từ không hợp lệ (từ mượn, từ mới, danh từ riêng) cần được ghi lại trong danh sách cho phép (allowlist).

### Giai đoạn 4: Phân đoạn và Niêm phong (1 tuần, kỹ thuật của chúng tôi)

**Người phụ trách:** Đội ngũ Champollion, với sự xem xét từ phía khoa.

1. **Phân tách phân tầng.** Chúng tôi chia ngữ liệu thành các phân đoạn bằng cách sử dụng phương pháp lấy mẫu ngẫu nhiên tất định (seed được ghi lại tài liệu, có thể tái lập):

   | Phân đoạn | Quy mô mục tiêu | Quyền truy cập |
   |---------|------------|--------|
   | `development` | 60% số mục (tối thiểu 100) | Công khai |
   | `gold_standard` | 30% số mục (tối thiểu 50) | Bí mật, được niêm phong |
   | `held_out` | 10% số mục (tối thiểu 10) | Bí mật, được niêm phong, không bao giờ sử dụng cho đến khi được kích hoạt |

   Việc phân tách này bảo toàn sự phân bổ mức độ khó (lấy mẫu phân tầng) để mỗi phân đoạn có tỷ lệ đại diện tương ứng trên các mức độ.

2. **Niêm phong mã hóa** các phân đoạn gold_standard và held_out:

   ```
   1. SHA-256 hash of each entry (source + reference + metadata)
   2. SHA-256 hash of the complete segment file
   3. Segment file encrypted with AES-256-GCM
   4. Encryption key split using Shamir Secret Sharing (2-of-3 threshold)
   5. Key shares distributed to:
        - Share 1: Community governance organization
        - Share 2: Academic department partner
        - Share 3: Champollion project (escrow)
   6. Hash manifest published to a public commit (proves the corpus existed
      at a specific time without revealing its contents)
   ```

3. **Phân đoạn phát triển (development)** được đưa vào kho lưu trữ công khai và xuất bản với đầy đủ giấy phép.

4. **Phân đoạn chẩn đoán (diagnostic)** cũng được công khai — phân đoạn này kiểm thử các hiện tượng ngôn ngữ cụ thể (xem §3.4).

### Giai đoạn 5: Tích hợp và Ra mắt (1–2 tuần, kỹ thuật của chúng tôi)

1. **Cấu hình khung đánh giá (harness).** Chúng tôi thêm ngôn ngữ vào khung đánh giá:
   - Thẻ ngôn ngữ được tạo hoặc xác minh
   - Ngữ liệu được đăng ký trong danh mục bộ dữ liệu
   - Các chỉ số LYSS được cấu hình (LYSS-fst nếu có FST, LYSS-eq nếu có quy tắc linter)
   - Hồ sơ tính điểm mặc định được chọn (Hồ sơ A nếu có FST, ngược lại là Hồ sơ B)

2. **Đánh giá chuẩn cơ sở (baseline).** Chúng tôi chạy thử nghiệm quét qua 12 mô hình đối với phân đoạn phát triển để cập nhật bảng xếp hạng với các điểm số ban đầu.

3. **Thông báo công khai.** Ngôn ngữ sẽ xuất hiện trên bảng xếp hạng Arena với điểm đánh giá chuẩn trực tiếp của phân đoạn phát triển. Khoa sẽ được ghi nhận là đối tác xây dựng ngữ liệu.

---

## 3. Yêu cầu về Cấu trúc Ngữ liệu

### 3.1 Định dạng

Mỗi tệp ngữ liệu là một tài liệu JSON tuân theo lược đồ trong Đặc tả Chuẩn đánh giá §2.1–§2.2:

```json
{
  "dataset": {
    "id": "crk-ualberta-v1",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "source_language": "en",
    "target_language": "crk",
    "created": "2026-09-15",
    "license": "CC-BY-NC-SA-4.0",
    "provenance": ["textbook", "elicited", "gold_standard"]
  },
  "entries": [
    {
      "id": 1,
      "source": "I see the dog",
      "reference": "niwâpamâw atim",
      "segment": "development",
      "difficulty": 2,
      "provenance": "textbook",
      "register": "conversational",
      "context": "declaration",
      "domain": "edu",
      "morphological_analysis": "ni-wâpam-âw atim | 1sg-see.TA-3sg.DIR dog.AN",
      "notes": "Animate noun (atim); direct form because speaker is proximate"
    }
  ]
}
```

### 3.2 Yêu cầu về Quy mô Tối thiểu

| Phân đoạn | Số mục tối thiểu | Khuyến nghị |
|---------|----------------|-------------|
| `development` | 100 | 200–300 |
| `gold_standard` | 50 | 100–150 |
| `diagnostic` | 10 | 30–50 |
| `held_out` | 10 | 20–30 |
| **Tổng cộng** | **170** | **350–530** |

### 3.3 Phân bổ Mức độ Khó

Ngữ liệu phải bao gồm các mục thuộc cả năm mức độ khó, tập trung nhiều hơn vào các mức từ 2–4:

| Mức độ | Mô tả | Phân bổ mục tiêu |
|------|-------------|-------------------|
| 1 — Từ vựng cơ bản | Từ đơn, câu chào hỏi thông dụng, chữ số | 10–15% |
| 2 — Câu đơn giản | SVO, thì hiện tại | 25–30% |
| 3 — Độ phức tạp trung bình | Thì quá khứ/tương lai, từ sở hữu, tính hoạt tính (animacy) | 30–35% |
| 4 — Hình thái phức tạp | Hiện tượng obviation, thể bị động, trật tự liên kết (conjunct order), mệnh đề quan hệ | 15–20% |
| 5 — Nâng cao | Nhiều mệnh đề, ngữ vực trang trọng, nghi lễ, thành ngữ | 5–10% |

### 3.4 Bộ Kiểm thử Chẩn đoán

Phân đoạn chẩn đoán kiểm thử các hiện tượng ngôn ngữ cụ thể bằng cách sử dụng **các cặp tương phản**: một bản dịch đúng và một bản dịch sai có sự khác biệt tối thiểu. Nếu chỉ số của hệ thống chấm điểm bản dịch đúng cao hơn, bài kiểm thử đó đạt.

Đối với các ngôn ngữ đa tổng hợp, bộ chẩn đoán nên nhắm vào:

| Hiện tượng | Ví dụ (tiếng Cree) | Nội dung kiểm thử |
|-----------|----------------|--------------|
| **Sự hợp dạng về tính hoạt tính** | atim (AN) so với maskisin (IN) — các dạng động từ khác nhau | Hệ thống có biết danh từ nào là danh từ chỉ thực thể hoạt tính không? |
| **Hiện tượng obviation** | Ngôi thứ ba gần (proximate) so với ngôi thứ ba xa (obviative) | Hệ thống có theo dõi được phân cấp ngôi thứ ba không? |
| **Đánh dấu nghịch đảo** | Dạng động từ trực tiếp so với nghịch đảo | Hệ thống có xử lý được trường hợp đối tượng chịu tác động vượt cấp tác nhân (patient-outranks-agent) không? |
| **Liên kết/Độc lập** | Trật tự động từ trong mệnh đề chính so với mệnh đề phụ | Hệ thống có sử dụng đúng hệ biến hình động từ không? |
| **Bao gồm/Loại trừ** | "Chúng ta (bao gồm bạn)" so với "Chúng tôi (không bao gồm bạn)" | Hệ thống có phân biệt được các dạng ngôi thứ nhất số nhiều không? |

Đối với các ngữ hệ khác, hãy xác định 3–5 hiện tượng mang tính chẩn đoán cao nhất để phân biệt giữa bản dịch đạt yêu cầu và không đạt yêu cầu. Chuyên môn ngôn ngữ học của khoa là vô cùng thiết yếu ở đây — đây là những bài kiểm thử mà chỉ chuyên gia mới biết cách xây dựng.

### 3.5 Những điều chúng tôi KHÔNG mong muốn

| Phản mẫu (Anti-Pattern) | Lý do |
|-------------|-----|
| **Chỉ dùng văn bản Kinh Thánh** | Ngữ vực cổ xưa, từ vựng phụng vụ, cấu trúc rập khuôn. Dự án OMT-1600 đã đánh giá 1.560 ngôn ngữ theo cách này — chúng tôi chủ động tránh điều đó. |
| **Các cặp đánh giá tổng hợp** | Các bản dịch tham chiếu do LLM tạo ra sẽ làm mất đi mục đích của việc đánh giá. Bản dịch tham chiếu phải do con người viết. |
| **Ngữ liệu chỉ có một ngữ vực** | Toàn bộ là trang trọng, hoặc toàn bộ là giao tiếp. Dịch thuật trong thực tế bao gồm nhiều ngữ vực khác nhau. |
| **Chỉ có mức độ khó 1** | Các từ đơn và câu chào hỏi không giúp kiểm thử khả năng dịch thuật — chúng chỉ kiểm thử việc tra cứu từ vựng. |
| **Bản dịch tham chiếu được dịch bằng máy** | Sử dụng kết quả của Google Translate làm "bản dịch tham chiếu" sẽ tạo ra lỗi lập luận vòng quanh. |
| **Các câu không có thẻ ngữ cảnh** | Chúng tôi cần biết chức năng giao tiếp để phục vụ phân tích chẩn đoán. |

---

## 4. Niêm phong Mã hóa và Kiểm thử trong Sandbox {#4-cryptographic-sealing-and-sandbox-testing}

### 4.1 Tại sao cần Niêm phong Tập Kiểm thử?

Các chuẩn đánh giá ML thông thường công bố công khai các tập kiểm thử. Sau khi được công bố, các LLM tiên tiến cuối cùng sẽ huấn luyện trên chúng (vô tình hoặc thông qua việc thu thập dữ liệu web), khiến điểm số không còn đáng tin cậy. Đối với dữ liệu ngôn ngữ bản địa, còn có một mối lo ngại khác: dữ liệu ngôn ngữ được công bố có thể bị sử dụng mà không có sự đồng ý của cộng đồng.

Việc niêm phong đảm bảo:
- **Tính toàn vẹn của tập kiểm thử:** Các phương pháp không thể khớp quá mức (overfit) với dữ liệu mà chúng chưa từng thấy
- **Chủ quyền dữ liệu:** Cộng đồng kiểm soát ai được đánh giá dựa trên dữ liệu của họ
- **Độ mới vĩnh viễn:** Tập kiểm thử không bao giờ bị rò rỉ hay ô nhiễm

### 4.2 Cách thức Hoạt động của Kiểm thử trong Sandbox

```
Developer workflow:
  1. Developer builds a translation method using the PUBLIC development corpus
  2. Developer tests locally against the development segment (unlimited, self-serve)
  3. When ready, developer submits their complete method (code + config + coaching data)
  4. Governance org installs the method in the evaluation sandbox
  5. Sandbox runs the method against the SEALED gold-standard test set
  6. Only scores are returned to the developer
  7. Developer never sees the source sentences or reference translations

The sandbox:
  - Runs on governance-controlled infrastructure
  - Has selective network access (LLM APIs only, no exfiltration)
  - Produces a tamper-proof run card (SHA-256 hash of all inputs and outputs)
  - Logs all execution for audit purposes
  - Can be inspected by the governance org at any time
```

### 4.3 Quản lý Khóa

Khóa mã hóa cho tập kiểm thử được niêm phong được chia nhỏ bằng phương thức Chia sẻ Bí mật Shamir với ngưỡng 2-trên-3:

| Bên giữ phần khóa | Vai trò | Quyền thu hồi |
|-------------|------|-----------------|
| **Tổ chức quản trị cộng đồng** | Bên giám hộ chính | Có thể đơn phương thu hồi quyền truy cập đánh giá |
| **Khoa học thuật đối tác** | Bên đồng giám hộ | Có thể tham gia vào việc khôi phục khóa |
| **Dự án Champollion** | Bên giữ hộ (Escrow) | Không thể tự truy cập dữ liệu; đảm bảo tính liên tục nếu các bên khác không còn khả năng hoạt động |

Bất kỳ 2 trong số 3 phần khóa đều có thể khôi phục lại khóa. Điều này có nghĩa là:
- Cộng đồng + khoa có thể truy cập dữ liệu mà không cần Champollion
- Cộng đồng + Champollion có thể truy cập dữ liệu mà không cần khoa
- Riêng Champollion KHÔNG BAO GIỜ có thể tự truy cập dữ liệu

### 4.4 Bản kê khai mã băm (Hash Manifest)

Khi ngữ liệu được niêm phong, một **bản kê khai mã băm (hash manifest)** sẽ được công bố trên một commit Git công khai:

```json
{
  "corpus_id": "crk-ualberta-v1",
  "seal_date": "2026-09-15T00:00:00Z",
  "segments": {
    "development": {
      "entry_count": 200,
      "sha256": "a3f7c...",
      "access": "public"
    },
    "gold_standard": {
      "entry_count": 100,
      "sha256": "b8d2e...",
      "access": "sealed",
      "key_scheme": "shamir-2-of-3"
    },
    "held_out": {
      "entry_count": 20,
      "sha256": "c9e4f...",
      "access": "sealed",
      "key_scheme": "shamir-2-of-3"
    },
    "diagnostic": {
      "entry_count": 30,
      "sha256": "d1a3b...",
      "access": "public"
    }
  },
  "total_entries": 350,
  "manifest_sha256": "e2b5c..."
}
```

This proves:
- Ngữ liệu đã tồn tại vào một ngày cụ thể
- Nó có quy mô và cấu trúc đã biết
- Bất kỳ sửa đổi nào đối với các phân đoạn được niêm phong sẽ làm đứt gãy chuỗi băm
- Cộng đồng có thể xác minh dữ liệu của họ không bị can thiệp trái phép

---

## 5. Những gì Khoa Nhận được

### 5.1 Cơ sở Hạ tầng Nghiên cứu

| Tài nguyên | Mô tả |
|-------|------------|
| **Khung đánh giá (harness)** | Một khung đánh giá hoạt động tốt, đã được kiểm thử cho ngôn ngữ của họ — tiết kiệm hàng tháng trời xây dựng công cụ |
| **Các chỉ số LYSS** | Các chỉ số đánh giá đặc thù cho ngôn ngữ (LYSS-fst, LYSS-eq, LYSS-sem) được cấu hình cho ngôn ngữ của họ — nếu có tài nguyên FST và từ điển |
| **Bảng xếp hạng** | Một bảng xếp hạng công khai, trực tiếp hiển thị các giải pháp tiên tiến nhất (state of the art) cho cặp ngôn ngữ của họ |
| **Đánh giá chuẩn cơ sở** | Quá trình quét qua 12 mô hình cung cấp các kết quả cơ sở tức thì, có thể công bố ngay |
| **Bộ kiểm thử chẩn đoán** | Các bài kiểm thử mục tiêu cho các hiện tượng ngôn ngữ cụ thể — có thể tái sử dụng cho các đánh giá khác |

### 5.2 Công bố Khoa học

Việc xây dựng ngữ liệu và kết quả đánh giá sẽ hỗ trợ cho nhiều công bố khoa học:

| Bài báo khoa học | Nơi công bố | Vai trò của Khoa |
|-------|-------|-----------------|
| Phương pháp luận xây dựng ngữ liệu | LREC, ComputEL | Tác giả chính hoặc đồng tác giả |
| Kết quả đánh giá cơ sở | ACL, EMNLP | Đồng tác giả |
| Xác thực chỉ số LYSS | WMT Metrics Shared Task | Đồng tác giả |
| Thiết kế bộ kiểm thử chẩn đoán | SIGMORPHON, NAACL | Tác giả chính hoặc đồng tác giả |
| Tài nguyên NLP đặc thù cho ngôn ngữ | Các hội thảo/tạp chí chuyên biệt về ngôn ngữ | Tác giả chính |

### 5.3 Lợi thế khi Xin Tài trợ (Grant)

Quan hệ hợp tác cung cấp các kết quả đầu ra cụ thể cho các đề xuất xin tài trợ:

- "Cơ sở hạ tầng đánh giá mã nguồn mở cho dịch máy tiếng [ngôn ngữ]" — sản phẩm bàn giao có thể chứng minh được
- "Chủ quyền dữ liệu mã hóa cho dữ liệu ngôn ngữ bản địa" — mới mẻ, có thể công bố khoa học
- "Chuẩn đánh giá do cộng đồng quản trị với bảng xếp hạng trực tiếp" — chỉ số đo lường tác động liên tục
- "Đánh giá độc lập về OMT-1600 / Google Translate cho tiếng [ngôn ngữ]" — mang tính thời sự, độ nhận diện cao

### 5.4 Tác động Cộng đồng

- Cộng đồng ngôn ngữ có được **năng lực đánh giá độc lập** — họ có thể đánh giá xem liệu bất kỳ hệ thống dịch máy nào (Google, Meta, hoặc tùy chỉnh) có thực sự hoạt động hiệu quả đối với ngôn ngữ của họ hay không
- Cộng đồng **kiểm soát dữ liệu kiểm thử** thông qua việc giám hộ khóa mã hóa
- Bất kỳ phương pháp nào được chứng minh hiệu quả thông qua chuẩn đánh giá sẽ **chuyển giao quyền sở hữu** cho cộng đồng (xem Đặc tả Chuẩn đánh giá §8.3)
- Doanh thu từ các phương pháp được triển khai sẽ chảy về cộng đồng (chia sẻ theo tỷ lệ 90/10)

### 5.5 Chi phí đối với Khoa

| Hạng mục | Chi phí ước tính | Bên chi trả |
|-----------|---------------|----------|
| Thời gian của PI/postdoc (thiết kế, giám sát) | ~40 giờ | Khoa (hoặc từ nguồn tài trợ) |
| Thù lao cho người nói (dịch thuật) | $2.500–6.000 | Từ nguồn tài trợ hoặc do dự án Champollion tài trợ |
| Thù lao cho người nói (đánh giá) | $500–1.500 | Từ nguồn tài trợ hoặc do dự án Champollion tài trợ |
| Thời gian của điều phối viên nghiên cứu | ~20 giờ | Khoa |
| **Kỹ thuật, cơ sở hạ tầng, khung đánh giá** | **$0** | **Dự án Champollion** |

Chúng tôi cung cấp toàn bộ phần kỹ thuật, cấu hình khung đánh giá, thiết lập chỉ số LYSS, tích hợp bảng xếp hạng và cơ sở hạ tầng liên tục mà không tính phí đối với khoa. Đóng góp của khoa là chuyên môn ngôn ngữ học và khả năng tiếp cận người nói.

---

## 6. Lộ trình Thực hiện

| Giai đoạn | Thời gian | Cột mốc quan trọng |
|-------|----------|--------------|
| 1: Thiết kế Ngữ liệu | 2–4 tuần | Tài liệu thiết kế được phê duyệt |
| 2: Câu Nguồn + Dịch thuật | 4–8 tuần | Hoàn thành ngữ liệu thô |
| 3: Đảm bảo Chất lượng | 2–4 tuần | Được đánh giá chéo, xác thực lược đồ |
| 4: Niêm phong | 1 tuần | Niêm phong tập chuẩn vàng, công bố bản kê khai mã băm |
| 5: Tích hợp | 1–2 tuần | Ngôn ngữ xuất hiện trực tuyến trên bảng xếp hạng cùng các kết quả cơ sở |
| **Tổng cộng** | **10–19 tuần** | **Bảng xếp hạng trực tuyến với đánh giá được niêm phong** |

---

## 7. Cách thức Bắt đầu {#7-how-to-get-started}

1. **Liên hệ với chúng tôi** — [project email/contact]. Chúng tôi sẽ lên lịch một cuộc gọi 30 phút để thảo luận về ngôn ngữ của bạn, các tài nguyên sẵn có và hậu cần hợp tác.

2. **Chúng tôi cung cấp:**
   - Tài liệu này
   - Lược đồ ngữ liệu và các công cụ xác thực
   - Các ví dụ từ ngữ liệu tiếng Cree (CRK) hiện có của chúng tôi
   - Mẫu thiết kế ngữ liệu nháp

3. **Bạn cung cấp:**
   - Một PI hoặc postdoc để dẫn dắt công việc ngôn ngữ học
   - Khả năng tiếp cận những người nói song ngữ (hoặc kế hoạch tuyển dụng họ)
   - Thông tin về các tài nguyên sẵn có (FST, từ điển, ngữ liệu hiện có)
   - Sự phê duyệt của tổ chức về quản trị dữ liệu (tuân thủ OCAP® hoặc tương đương)

4. **Chúng ta cùng thiết kế ngữ liệu** — lựa chọn lĩnh vực, phân bổ mức độ khó, các bài kiểm thử chẩn đoán, lộ trình và ngân sách.

5. **Bắt đầu công việc.** Chúng tôi sẽ trao đổi cập nhật hàng tuần. Khoa có toàn quyền tự quyết đối với các quyết định ngôn ngữ học; chúng tôi đảm nhận toàn bộ phần kỹ thuật.

---

## 8. Câu hỏi Thường gặp

### "Chúng tôi đã có sẵn một ngữ liệu song song. Chúng tôi có thể sử dụng nó không?"

Có — nếu ngữ liệu có nguồn gốc rõ ràng, do con người biên soạn và giấy phép cho phép sử dụng trong đánh giá. Chúng tôi sẽ giúp bạn định dạng nó theo lược đồ của chúng tôi, thêm siêu dữ liệu còn thiếu và tích hợp nó. Ngữ liệu hiện có có thể đẩy nhanh đáng kể lộ trình (bỏ qua Giai đoạn 2 hoặc giảm bớt xuống thành một bài tập điền vào chỗ trống).

### "Chúng tôi không có FST cho ngôn ngữ của mình."

Không sao cả. Chỉ số LYSS-fst (tính hợp lệ về hình thái) yêu cầu một FST, nhưng khung đánh giá vẫn hoạt động tốt mà không cần nó bằng cách sử dụng trọng số của Hồ sơ B (chrF++, BLEU, COMET, các chỉ số hành vi). Nếu có FST GiellaLT cho một ngôn ngữ có liên quan, chúng tôi có thể điều chỉnh nó. Nếu không, ngữ liệu vẫn cho phép thực hiện đánh giá có giá trị — chỉ là không có bước kiểm tra tính hợp lệ về hình thái.

### "Người nói của chúng tôi sử dụng chữ viết không phải Latin."

Được hỗ trợ đầy đủ. Lược đồ ngữ liệu xử lý bất kỳ chữ viết Unicode nào. Chúng tôi đã thiết kế cho SRO (Chữ viết La-tinh chuẩn) và chữ âm tiết (syllabics) cho tiếng Cree, nhưng cơ sở hạ tầng tương tự cũng hoạt động tốt cho chữ Devanagari, chữ Ả Rập, CJK, chữ Ethiopia, hoặc bất kỳ hệ thống chữ viết nào khác.

### "Còn về sự khác biệt phương ngôn (dialect) thì sao?"

Hãy gắn thẻ cho nó. Lược đồ mục nhập ngữ liệu bao gồm một trường `notes` cho thông tin phương ngôn. Nếu có nhiều phương ngôn được đại diện, hãy ghi lại tài liệu về chúng. Các lớp tương đương của linter (LYSS-eq) can be configured to accept dialectal variants as equivalent. Bộ kiểm thử chẩn đoán có thể bao gồm các cặp tương phản đặc thù cho từng phương ngôn.

### "Ai sở hữu ngữ liệu?"

Cộng đồng ngôn ngữ sở hữu, thông qua tổ chức quản trị. Khoa được ghi nhận là đối tác nghiên cứu. Champollion giữ một phần khóa ký quỹ (escrow) để đảm bảo tính liên tục của hoạt động nhưng không thể tự mình truy cập dữ liệu được niêm phong. Phân đoạn phát triển được xuất bản dưới giấy phép Creative Commons do cộng đồng chỉ định.

### "Nếu chúng tôi muốn dừng lại thì sao?"

Cộng đồng có thể thu hồi quyền truy cập đánh giá bất kỳ lúc nào bằng cách từ chối khôi phục khóa mã hóa. Dữ liệu được niêm phong không bao giờ bị lộ. Phân đoạn phát triển, vốn đã được xuất bản, vẫn được công khai theo giấy phép của nó. Các kết quả nghiên cứu của khoa (công bố khoa học, bài thuyết trình) vẫn thuộc quyền sở hữu của khoa trong mọi trường hợp.

### "Nếu tổ chức quản trị chưa tồn tại thì sao?"

Chúng ta có thể bắt đầu với các Giai đoạn 1–3 (thiết kế, tạo lập, QA ngữ liệu) mà chưa cần tổ chức quản trị. Việc niêm phong (Giai đoạn 4) yêu cầu xác định một bên giám hộ khóa. Trong thời gian tạm thời, khoa có thể đóng vai trò là bên đồng giám hộ cùng với dự án Champollion, với sự thống nhất rằng quyền giám hộ sẽ được chuyển giao cho tổ chức quản trị cộng đồng khi tổ chức này được thành lập.

---

## Phụ lục: Gắn thẻ so với Xây dựng Ngữ liệu

Tài liệu này đề cập đến **việc xây dựng ngữ liệu** — tạo ra các cặp văn bản song song tạo thành ground truth cho việc đánh giá. Việc gắn thẻ (chú thích hình thái, chú giải liên dòng, chuỗi thẻ FST) là một hoạt động riêng biệt giúp làm phong phú ngữ liệu nhưng không bắt buộc đối với việc đánh giá cơ bản.

| Hoạt động | Bắt buộc? | Khả năng mang lại |
|----------|-----------|-----------------|
| **Xây dựng ngữ liệu** (tài liệu này) | ✅ Bắt buộc | Đánh giá cơ bản: chrF++, khớp chính xác (exact match), COMET, các chỉ số hành vi |
| **Kiểm tra độ bao phủ FST** | 🟡 Tùy chọn | Chỉ số tính hợp lệ về hình thái LYSS-fst |
| **Chú thích hình thái** | 🟡 Tùy chọn | Chỉ số `morphological_accuracy` (Đặc tả Tính điểm §2.2) |
| **Quy tắc tương đương linter** | 🟡 Tùy chọn | Chỉ số khớp tương đương LYSS-eq |
| **Quy tắc xác thực ngữ nghĩa** | 🟡 Tùy chọn | Chỉ số xác thực ngữ nghĩa LYSS-sem |
| **Đánh giá chất lượng của người nói** | Hoạt động riêng biệt | Xác thực chỉ số (xem [Giao thức Xác thực Người nói](/docs/specifications/speaker-validation)) |

Việc gắn thẻ và xác thực người nói được đề cập trong các tài liệu riêng biệt và có thể tiến hành song song hoặc sau khi xây dựng ngữ liệu.