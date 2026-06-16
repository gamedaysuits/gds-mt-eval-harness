---
sidebar_position: 7
title: "Khung thiết kế ngữ liệu"
---
# Khung Thiết kế Corpus Đánh giá

> **Phiên bản:** 1.0  
> **Trạng thái:** Bản thảo  
> **Mục đích:** Một phương pháp luận hệ thống để xây dựng các corpus đánh giá nhằm tạo ra các kết quả đánh giá chất lượng dịch thuật hợp lệ, đáng tin cậy và có ý nghĩa về mặt ngôn ngữ học. Đây là nguồn thông tin gốc (source of truth) về cách các tập dữ liệu đánh giá của Champollion được thiết kế, xây dựng và duy trì.

---

## 1. Nguyên tắc Thiết kế

### 1.1 — Tại sao không dùng các Benchmark Công khai?

Các corpus song ngữ công khai (FLORES+, Tatoeba, các bộ test WMT, OPUS) luôn có sẵn để phát triển và gỡ lỗi nhưng **bị loại trừ khỏi việc đánh giá trên bảng xếp hạng chính thức**. Lý do rất đơn giản:

**Sự rò rỉ dữ liệu (Contamination).** Các LLM hàng đầu (frontier LLM) được huấn luyện trên lượng dữ liệu khổng lồ thu thập từ web. Bất kỳ văn bản song ngữ nào từng tồn tại công khai — đặc biệt là trong các tập dữ liệu benchmark được tuyển chọn và trích dẫn rộng rãi — đều có khả năng đã nằm trong dữ liệu huấn luyện của chúng. Khi bạn đánh giá GPT-4o trên FLORES+ và nó đạt điểm 85 chrF++, bạn không thể phân biệt được giữa "mô hình dịch tốt" và "mô hình đã ghi nhớ các cặp câu cụ thể này". Đây không phải là một mối lo ngại mang tính lý thuyết — [nghiên cứu đã chứng minh](https://arxiv.org/abs/2311.04850) các ảnh hưởng rõ rệt của sự rò rỉ dữ liệu đối với các benchmark dịch máy (MT).

Đối với Champollion, điều này đặc biệt quan trọng vì:
- Bảng xếp hạng của chúng tôi chủ yếu so sánh các phương pháp dựa trên LLM
- Giá trị cốt lõi của chúng tôi là *sự đánh giá trung thực và nghiêm ngặt*
- Người dùng mục tiêu của chúng tôi (các cộng đồng ngôn ngữ) đưa ra quyết định triển khai dựa trên các điểm số này

### 1.2 — Các Yêu cầu Cốt lõi

Mỗi corpus đánh giá của Champollion phải đáp ứng:

| Yêu cầu | Cơ sở lý luận |
|-------------|-----------|
| **Do con người viết** | Không sử dụng dữ liệu tổng hợp (synthetic data). Tất cả văn bản nguồn và bản dịch tham chiếu phải do con người viết. LLM có thể hỗ trợ căn chỉnh (alignment) và định dạng nhưng không bao giờ được tạo nội dung. |
| **Không công khai ở dạng song ngữ** | Văn bản nguồn có thể công khai; bản dịch tham chiếu có thể công khai; nhưng *sự kết cặp* cụ thể không được tồn tại dưới dạng một corpus song ngữ có thể tải xuống. |
| **Được theo dõi nguồn gốc** | Mỗi mục nhập phải có nguồn gốc được tài liệu hóa rõ ràng: tài liệu nguồn, người dịch, giấy phép, ngày tháng. |
| **Dựa trên cơ sở ngôn ngữ học** | Phạm vi bao phủ phải được định hướng bởi các đặc điểm loại hình học (typological features), không phải lấy mẫu ngẫu nhiên. |
| **Phân tầng theo lĩnh vực** | Các mục nhập phải trải dài trên các lĩnh vực văn bản được xác định với tỷ lệ đại diện được kiểm soát. |
| **Phân bậc độ khó** | Các mục nhập phải được gán các bậc độ khó (1–5) dựa trên độ phức tạp về mặt cấu trúc. |
| **Kiểm soát phiên bản** | Các phiên bản corpus được băm nội dung (content-hashed). Điểm số chỉ có thể so sánh được trong cùng một phiên bản. |
| **Cộng đồng có thể đánh giá** | Các bản dịch tham chiếu phải có thể được xem xét và đánh giá bởi các thành viên trong cộng đồng ngôn ngữ. |

---

## 2. Lựa chọn Văn bản Nguồn

### 2.1 — Phân loại Lĩnh vực (Domain Taxonomy)

Champollion đánh giá bản dịch cho **các bối cảnh triển khai thực tế**, không phải cho các bài tập học thuật. Phân loại lĩnh vực phản ánh các loại văn bản thực tế mà người dùng dịch thuật thường gặp phải:

| Lĩnh vực | Mã | Mô tả | Nguồn Ví dụ |
|--------|------|-------------|-----------------|
| **Giao diện Phần mềm (Software UI)** | `ui` | Nhãn nút, mục menu, thông báo lỗi, tooltip, luồng hướng dẫn người dùng mới (onboarding) | Các chuỗi ký tự trong ứng dụng mã nguồn mở, cổng thông tin tài liệu |
| **Chính thức/Hành chính** | `admin` | Tài liệu chính phủ, thông báo pháp lý, biểu mẫu, tuyên bố chính sách | Các ấn phẩm chính phủ công khai, tài liệu của chính quyền địa phương |
| **Giáo dục** | `edu` | Nội dung sách giáo khoa, tài liệu bài học, văn bản hướng dẫn | Các tài liệu giáo dục đã xuất bản, hướng dẫn giảng dạy |
| **Tự sự/Văn học** | `lit` | Câu chuyện, văn bản văn hóa, bản ghi chép lịch sử truyền miệng | Sách đã xuất bản, kho lưu trữ văn hóa (khi được phép) |
| **Hội thoại** | `conv` | Đối thoại, trao đổi dạng chat, giao tiếp viết không chính thức | Các corpus đối thoại đã xuất bản, kịch bản, bản ghi phỏng vấn |
| **Kỹ thuật** | `tech` | Tài liệu API, tệp README, thông số kỹ thuật | Tài liệu dự án mã nguồn mở |
| **Y tế/Y khoa** | `health` | Thông tin y tế dành cho bệnh nhân, thông điệp sức khỏe cộng đồng | Các ấn phẩm y tế của chính phủ |
| **Tin tức/Báo chí** | `news` | Bài báo, thông cáo báo chí, thời sự | Báo chí cộng đồng, các kênh truyền thông bản địa |

### 2.2 — Phân bổ Lĩnh vực

Một corpus đánh giá tiêu chuẩn nên hướng tới tỷ lệ phân bổ sau đây. Tỷ lệ phần trăm chính xác có thể thay đổi tùy theo cặp ngôn ngữ dựa trên loại văn bản nào phù hợp nhất với cộng đồng mục tiêu:

| Lĩnh vực | % Mục tiêu | Cơ sở lý luận |
|--------|----------|-----------|
| Giao diện Phần mềm | 25% | Bối cảnh triển khai chính cho người dùng champollion CLI |
| Chính thức/Hành chính | 15% | Dịch thuật có độ rủi ro cao với các tác động pháp lý |
| Giáo dục | 15% | Trường hợp sử dụng cốt lõi cho việc phục hưng ngôn ngữ |
| Tự sự/Văn học | 10% | Kiểm tra sắc thái văn hóa và văn phong văn học |
| Hội thoại | 10% | Kiểm tra văn phong không chính thức và các mẫu lời nói tự nhiên |
| Kỹ thuật | 10% | Kiểm tra độ chính xác và tính nhất quán của thuật ngữ |
| Y tế/Y khoa | 10% | Độ rủi ro cao, kiểm tra từ vựng chuyên ngành |
| Tin tức/Báo chí | 5% | Kiểm tra từ vựng đương đại và văn phong trung lập |

### 2.3 — Tiêu chí Lựa chọn Nguồn

Khi lựa chọn văn bản nguồn cho một corpus mới:

1. **Tính tương thích của giấy phép.** Văn bản nguồn phải có giấy phép cho phép sử dụng trong corpus đánh giá. Ưu tiên CC BY, CC BY-SA, hoặc thuộc phạm vi công cộng (public domain). Hãy tài liệu hóa giấy phép.

2. **Tính cập nhật.** Ưu tiên các văn bản được xuất bản trong vòng 10 năm qua. Ngôn ngữ luôn phát triển — đặc biệt là từ vựng xung quanh công nghệ, quản trị và y học.

3. **Sự đa dạng về văn phong (register).** Trong mỗi lĩnh vực, hãy tìm kiếm các văn bản ở các mức độ trang trọng khác nhau. Một thông cáo báo chí của chính phủ (trang trọng) và một bài đăng trên mạng xã hội của chính phủ (thân mật) đều thuộc lĩnh vực `admin` nhưng có văn phong khác nhau.

4. **Sự phù hợp về văn hóa.** Đối với các ngôn ngữ bản địa và thiểu số, hãy ưu tiên các văn bản quan trọng đối với cộng đồng — tài liệu quản lý đất đai, tài liệu giáo dục bằng ngôn ngữ đó, văn bản bảo tồn văn hóa — thay vì các văn bản ngẫu nhiên tồn tại ở dạng song ngữ.

5. **Không sử dụng nguồn dịch máy.** Nếu một tài liệu "song ngữ" được tạo ra bằng cách chạy bản gốc qua Google Translate rồi sau đó hiệu đính (post-editing), nó KHÔNG được chấp nhận làm bản dịch tham chiếu. Bản dịch tham chiếu phải là một bản dịch độc lập do con người thực hiện.

---

## 3. Hệ thống Bậc Độ khó

### 3.1 — Định nghĩa các Bậc

Mỗi mục nhập được gán một bậc độ khó (1–5) dựa trên độ phức tạp về mặt cấu trúc của *văn bản nguồn*, chứ không phải độ khó của việc dịch (vốn thay đổi tùy theo phương pháp).

| Bậc | Nhãn | Đặc điểm Cấu trúc |
|------|-------|---------------------------|
| 1 | **Sơ cấp (Elementary)** | Câu đơn giản. Một mệnh đề. Thì hiện tại. Từ vựng thông dụng. Không có thành ngữ. Không có cấu trúc lồng ghép. |
| 2 | **Trung cấp (Intermediate)** | Câu ghép. Hai mệnh đề được nối bằng liên từ. Thì quá khứ/tương lai. Có một số từ vựng chuyên ngành. |
| 3 | **Cao cấp (Advanced)** | Câu phức. Mệnh đề phụ, mệnh đề quan hệ. Trộn lẫn các thì. Thuật ngữ chuyên ngành cụ thể. Thể bị động. |
| 4 | **Chuyên gia (Expert)** | Nhiều mệnh đề lồng nhau. Văn phong pháp lý/kỹ thuật. Cấu trúc điều kiện. Khái niệm trừu tượng. Các tham chiếu văn hóa. |
| 5 | **Cực độ (Extreme)** | Văn xuôi dày đặc với nhiều thách thức đồng thời: mệnh đề phụ lồng nhau, tham chiếu đại từ mơ hồ, thành ngữ văn hóa, văn phong hỗn hợp, từ vựng hiếm gặp. |

### 3.2 — Các Yếu tố Độ khó dựa trên Ngôn ngữ học

Bên cạnh độ phức tạp về mặt cấu trúc, độ khó còn được điều chỉnh bởi **khoảng cách loại hình học (typological distance)** giữa ngôn ngữ nguồn và ngôn ngữ mục tiêu. Các yếu tố này được rút ra từ các đặc điểm loại hình học của WALS và dữ liệu phân loại của thẻ ngôn ngữ (language card):

| Yếu tố | Độ khó Thấp | Độ khó Cao |
|--------|---------------|-----------------|
| **Trật tự từ** | Cùng trật tự cơ bản (ví dụ: SVO→SVO) | Khác trật tự cơ bản (ví dụ: SVO→SOV) |
| **Loại hình hình thái học** | Loại hình tương tự (ví dụ: đơn lập→đơn lập) | Khác loại hình (ví dụ: đơn lập→đa tổng hợp) |
| **Giống ngữ pháp** | Cùng hệ thống hoặc không có giống | Nguồn không có giống, mục tiêu có hệ thống giống phức tạp |
| **Kính ngữ/Văn phong** | Không đánh dấu văn phong | Mục tiêu có hệ thống văn phong phức tạp (ví dụ: tiếng Nhật, tiếng Hàn) |
| **Hệ chữ viết** | Cùng hệ chữ viết | Khác hệ chữ viết (yêu cầu chuyển tự) |
| **Tính hữu sinh (Animacy)** | Không phân biệt tính hữu sinh | Mục tiêu có sự hòa hợp dựa trên tính hữu sinh (ví dụ: tiếng Cree) |
| **Tính chứng thực (Evidentiality)** | Không có tính chứng thực | Mục tiêu đánh dấu nguồn thông tin bằng ngữ pháp |

### 3.3 — Phân bổ các Bậc

Một corpus tiêu chuẩn nên có tỷ lệ xấp xỉ:

| Bậc | % Mục tiêu | Cơ sở lý luận |
|------|----------|-----------|
| 1 | 15% | Thiết lập mức cơ sở (baseline) — ngay cả các phương pháp kém cũng phải xử lý được |
| 2 | 25% | Các bản dịch thực tế phổ thông |
| 3 | 30% | Nơi sự khác biệt về chất lượng giữa các phương pháp bắt đầu lộ rõ |
| 4 | 20% | Phân biệt giữa phương pháp tốt và phương pháp xuất sắc |
| 5 | 10% | Thử nghiệm giới hạn trần — rất ít phương pháp có thể xử lý tốt các trường hợp này |

---

## 4. Chất lượng Bản dịch Tham chiếu

### 4.1 — Yêu cầu đối với Người dịch

Bản dịch tham chiếu phải được thực hiện bởi những người:

1. **Sử dụng trôi chảy** ngôn ngữ mục tiêu (tiếng mẹ đẻ L1 hoặc tương đương)
2. **Có khả năng đọc viết tốt** bằng cả ngôn ngữ nguồn và ngôn ngữ mục tiêu
3. **Có hiểu biết về lĩnh vực** của văn bản (ví dụ: biên dịch viên y khoa cho các văn bản sức khỏe, v.v.)
4. **Độc lập** — người dịch không được tiếp cận với bất kỳ kết quả dịch máy (MT) nào của cùng một văn bản trong quá trình dịch

### 4.2 — Bản Yêu cầu Dịch thuật (Translation Brief)

Mỗi người dịch sẽ nhận được một bản yêu cầu bao gồm:

- **Văn phong (register)** cần sử dụng (trang trọng, hội thoại, v.v.)
- **Đối tượng độc giả mục tiêu** (công chúng, chuyên gia, trẻ em, v.v.)
- Bất kỳ **quy ước thuật ngữ** nào đặc thù cho cộng đồng ngôn ngữ đó
- Hướng dẫn rõ ràng: "Hãy dịch nghĩa, không dịch từ. Một bản dịch nghe tự nhiên có giá trị hơn một bản dịch sát nghĩa từng chữ."

### 4.3 — Đảm bảo Chất lượng (Quality Assurance)

1. **Dịch song song (Dual translation).** Lý tưởng nhất là mỗi mục nhập có hai bản dịch tham chiếu độc lập bởi các biên dịch viên khác nhau. Trong trường hợp không khả thi, hãy ưu tiên dịch song song cho các Bậc 4–5.

2. **Cộng đồng xem xét.** Các bản dịch tham chiếu nên được xem xét bởi ít nhất một người bản xứ khác không tham gia vào quá trình dịch.

3. **Các biến thể chấp nhận được.** Đối với mỗi bản dịch tham chiếu, hãy tài liệu hóa các biến thể chấp nhận được đã biết (trật tự từ, quy ước chính tả, dạng phương ngữ). Những thông tin này sẽ cung cấp dữ liệu cho chỉ số `equivalent_match_rate`.

### 4.4 — Thế nào là một Bản dịch Tham chiếu Tồi

| Vấn đề | Tại sao nó làm mất hiệu lực đánh giá |
|---------|------------------------------|
| Được dịch máy rồi hiệu đính | Việc hiệu đính vẫn giữ nguyên cấu trúc dịch máy; gây bất lợi cho các phương pháp tạo ra bản dịch tự nhiên hơn |
| Được dịch bởi người đang học, không phải người nói trôi chảy | Bản dịch tham chiếu có thể chứa lỗi, dẫn đến việc phạt các kết quả dịch máy đúng |
| Quá sát nghĩa từng chữ | Các bản dịch tự nhiên sẽ bị điểm thấp khi so sánh với các bản dịch tham chiếu quá sát nghĩa |
| Chỉ có một cách hiểu duy nhất cho nguồn mơ hồ | Phạt các cách hiểu thay thế khác cũng hợp lệ |

---

## 5. Ngăn ngừa Rò rỉ Dữ liệu

### 5.1 — Mô hình Mối đe dọa Rò rỉ Dữ liệu

| Mối đe dọa | Mô tả | Biện pháp Giảm thiểu |
|--------|-------------|------------|
| **Trùng lặp dữ liệu huấn luyện** | Các LLM được huấn luyện trên chính corpus song ngữ đó | Không công bố công khai corpus song ngữ |
| **Rò rỉ qua few-shot** | Tác giả phương pháp sử dụng các mục đánh giá làm ví dụ few-shot | Kiểm tra dấu vân tay (fingerprint-check): các mục nhập trong prompt sẽ bị phát hiện và gắn cờ |
| **Rò rỉ gián tiếp** | Văn bản nguồn tồn tại trong dữ liệu huấn luyện của LLM (đơn ngữ) | Có thể chấp nhận được — việc văn bản nguồn đơn ngữ tồn tại là điều bình thường. Nhưng *sự kết cặp* phải là mới hoàn toàn. |
| **Rò rỉ qua cộng đồng** | Những người xem xét trong cộng đồng chia sẻ công khai các mục nhập | Các điều khoản giấy phép nghiêm cấm việc phân phối lại corpus song ngữ |

### 5.2 — Các Bậc Bảo mật của Corpus

| Bậc | Khả năng hiển thị | Cách sử dụng |
|------|-----------|-----|
| **Tập phát triển công khai (Public development set)** | Công khai hoàn toàn | Phát triển phương pháp, gỡ lỗi, kiểm thử hồi quy. Điểm số KHÔNG được công bố trên bảng xếp hạng. |
| **Tập đánh giá giữ lại (Held-out evaluation set)** | Văn bản nguồn hiển thị, bản dịch tham chiếu được giữ kín | Đánh giá bảng xếp hạng chính thức. Các phương pháp nhận văn bản nguồn và trả về bản dịch; việc tính điểm diễn ra ở phía máy chủ. Bản dịch tham chiếu không bao giờ bị lộ ra ngoài. |
| **Tập chuẩn vàng (Gold-standard set)** | Bí mật hoàn toàn, do cộng đồng kiểm soát | Đánh giá được cộng đồng xác thực. Được quản lý bởi tổ chức quản trị. Được sử dụng cho bậc xác thực "Được cộng đồng xác thực" (Community Validated). |

### 5.3 — Chính sách Luân phiên

Các corpus đánh giá nên được **luân phiên** định kỳ:

1. Sau khi một corpus đã được sử dụng trong 12 tháng, hãy bắt đầu xây dựng một corpus thay thế
2. Chuyển corpus cũ sang trạng thái "tập phát triển" (công khai)
3. Nâng cấp corpus mới lên thành "tập đánh giá giữ lại"
4. Điều này ngăn ngừa sự rò rỉ dữ liệu dần dần thông qua việc tối ưu hóa lặp đi lặp lại đối với một mục tiêu cố định

---

## 6. Quy trình Xây dựng Corpus

### 6.1 — Quy trình Từng bước

```
Step 1: Language Pair Selection
    └─ Identify target language, read language card
    └─ Review typological features (WALS), contact influences, scripts
    └─ Identify which difficulty factors apply

Step 2: Source Text Curation
    └─ Identify candidate source documents per domain
    └─ Verify licenses
    └─ Extract candidate sentences/segments
    └─ Classify by domain and preliminary difficulty tier

Step 3: Segment Selection
    └─ Sample segments to match domain distribution (§2.2)
    └─ Sample segments to match difficulty distribution (§3.3)
    └─ Ensure linguistic phenomenon coverage (§6.2)
    └─ Target minimum corpus size (§6.3)

Step 4: Reference Translation
    └─ Assign segments to qualified translators
    └─ Provide translation brief
    └─ Collect translations
    └─ Dual-translate Tier 4–5 entries

Step 5: Quality Assurance
    └─ Community review of references
    └─ Document acceptable variants
    └─ Flag and resolve disagreements

Step 6: Metadata & Packaging
    └─ Assign final difficulty tiers
    └─ Add provenance metadata per entry
    └─ Content-hash the corpus for versioning
    └─ Package as corpus JSON per harness spec

Step 7: Registration
    └─ Register in Supabase datasets table
    └─ Add to ATTRIBUTION.md if new sources used
    └─ Document in arena website
```

### 6.2 — Phạm vi Bao phủ Hiện tượng Ngôn ngữ học

Mỗi corpus nên bao gồm các mục nhập để kiểm tra các hiện tượng ngôn ngữ học cụ thể liên quan đến cặp ngôn ngữ. Những hiện tượng này được rút ra từ các trường `linguisticChallenges` và `contactInfluences` của thẻ ngôn ngữ:

**Các hiện tượng phổ quát (tất cả các cặp ngôn ngữ):**
- Giải quyết đại từ (tiền ngữ mơ hồ)
- Phủ định (phủ định đơn, phủ định kép, phạm vi phủ định)
- Từ chỉ số lượng (tất cả, một số, không có gì, hầu hết)
- Biểu thức thời gian (ngày tương đối, khoảng thời gian)
- Thực thể có tên (người, địa danh, tổ chức)
- Con số và phép đo lường
- Danh sách và sự liệt kê

**Các hiện tượng đặc thù theo cặp (từ thẻ ngôn ngữ):**
- Đối với ngôn ngữ mục tiêu đa tổng hợp: hình thái động từ phức tạp, sự hợp nhất (incorporation)
- Đối với ngôn ngữ mục tiêu có giống: sự hòa hợp giống, tham chiếu trung lập/bao hàm
- Đối với ngôn ngữ mục tiêu SOV: động từ cuối mệnh đề, hậu giới từ
- Đối với ngôn ngữ có thanh điệu: phân biệt ý nghĩa dựa trên thanh điệu
- Đối với ngôn ngữ có kính ngữ: dấu hiệu văn phong, bối cảnh xã hội
- Đối với ngôn ngữ tiếp xúc: ranh giới chuyển mã (code-switching), sự tích hợp từ mượn

### 6.3 — Kích thước Corpus Tối thiểu

Độ tin cậy thống kê đòi hỏi số lượng mục nhập tối thiểu. Những số lượng này dựa trên các yêu cầu về khoảng tin cậy bootstrap cặp (từ `significance.py`):

| Mục đích | Số mục nhập Tối thiểu | Khuyến nghị |
|---------|-----------------|-------------|
| Tập phát triển | 50 | 100–200 |
| Tập đánh giá giữ lại | 100 | 200–500 |
| Tập chuẩn vàng | 200 | 500+ |
| Tối thiểu cho mỗi lĩnh vực | 10 | 25+ |
| Tối thiểu cho mỗi bậc | 10 | 20+ |

**Tại sao tối thiểu phải là 100 cho việc đánh giá?** Với ít hơn khoảng 100 mục nhập, các kiểm định ý nghĩa thống kê bootstrap cặp (1.000 lần lấy mẫu lại) không thể phát hiện một cách đáng tin cậy các khác biệt nhỏ hơn khoảng 5 điểm chrF++. Với hơn 200 mục nhập, chúng tôi có thể phát hiện các khác biệt khoảng 2 điểm ở mức ý nghĩa p<0.05.

---

## 7. Định dạng JSON của Corpus

Mỗi mục nhập corpus tuân theo đặc tả harness:

```json
{
  "id": "edtekla-dev-v1-042",
  "source": "The school board will meet on Tuesday to discuss the new curriculum.",
  "reference": "ᑭᓯᑭᓄᐦᐊᒫᑐᐏᓐ ᑲ ᐃᔑ ᐱᒥᐸᔨᐦᑕᐦᒃ ᑭᔅᑭᓄᐦᐊᒫᑐᐏᓇ ᐁ ᐃᔑ ᒫᒥᑐᓀᔨᐦᑕᐦᒃ ᐅᔥᑭ ᑭᔅᑭᓄᐦᐊᒫᑫᐏᓂᔭ ᓂᔓ ᑭᔑᑲᐤ",
  "acceptable_variants": [
    "ᑭᔅᑭᓄᐦᐊᒫᑐᐏᓐ ᓂᔓ ᑭᔑᑲᐤ ᑲ ᐃᔑ ᒫᒥᑐᓀᔨᐦᑕᐦᒃ ᐅᔥᑭ ᑭᔅᑭᓄᐦᐊᒫᑫᐏᓂᔭ"
  ],
  "domain": "edu",
  "difficulty": 3,
  "phenomena": ["temporal_expression", "named_entity", "future_tense"],
  "provenance": {
    "source_doc": "EdTeKLA Module 4, Unit 7",
    "source_license": "CC BY-NC-SA 4.0",
    "translator": "anonymous-speaker-001",
    "translator_qualification": "L1 Plains Cree, certified translator",
    "translation_date": "2025-11-15",
    "reviewer": "anonymous-speaker-002",
    "review_date": "2025-12-01"
  }
}
```

---

## 8. Các Biện pháp Chống Gian lận

### 8.1 — Tính Toàn vẹn của Corpus

| Biện pháp | Triển khai |
|---------|----------------|
| **Băm nội dung (Content hashing)** | Phiên bản corpus = SHA-256 của các ID mục nhập đã sắp xếp + các bản dịch tham chiếu. Bất kỳ sửa đổi nào cũng sẽ tạo ra một phiên bản mới. |
| **Tạo dấu vân tay mục nhập (Entry fingerprinting)** | Mỗi mục nhập có một ID được tạo ra từ nội dung. Nếu ai đó gửi kết quả dựa trên một corpus đã bị sửa đổi, dấu vân tay sẽ không khớp. |
| **Bắt buộc sử dụng tập giữ lại** | Đối với đánh giá chính thức, các phương pháp CHỈ nhận được văn bản nguồn. Bản dịch tham chiếu không bao giờ bị lộ. Việc tính điểm diễn ra ở phía máy chủ. |
| **Lịch trình luân phiên** | Các corpus được luân phiên hàng năm để ngăn chặn việc tối ưu hóa dài hạn đối với một mục tiêu cố định. |

### 8.2 — Tính Toàn vẹn của Lượt nộp

| Biện pháp | Triển khai |
|---------|----------------|
| **Dấu vân tay xác định (Deterministic fingerprint)** | Cấu hình chạy (mô hình, nhiệt độ, prompt, phiên bản corpus) được băm. Các cấu hình giống hệt nhau sẽ tạo ra các dấu vân tay giống hệt nhau. |
| **Phát hiện chọn lọc kết quả tốt nhất (Cherry-pick detection)** | Người nộp phải công khai tất cả các lượt chạy, không chỉ lượt chạy tốt nhất. Nhiều lượt nộp có cùng dấu vân tay sẽ bị gắn cờ. |
| **Kiểm tra rò rỉ dữ liệu** | Nếu các mục đánh giá xuất hiện nguyên văn trong prompt hoặc dữ liệu hướng dẫn của phương pháp, lượt nộp sẽ bị hủy tư cách. |

---

## 9. Các Corpus Hiện tại

### 9.1 — Tập Phát triển EDTeKLA v1

| Thuộc tính | Giá trị |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Cặp** | EN → CRK (Plains Cree, SRO) |
| **Số mục nhập** | 404 (`master_corpus.json`: 62 gold + 342 sách giáo khoa); tổng cộng có sẵn 548 |
| **Lĩnh vực** | Giáo dục (100%) |
| **Các bậc** | 1–5 (phân bổ sẽ được xác định sau khi kiểm tra mục nhập) |
| **Giấy phép** | CC BY-NC-SA 4.0 |
| **Trạng thái** | Tập phát triển (công khai) |

**Hạn chế:** Chỉ có một lĩnh vực duy nhất (chỉ giáo dục). Không có sự phân tầng lĩnh vực. Việc gán bậc độ khó có thể cần được kiểm tra lại. Kích thước corpus nhỏ làm hạn chế sức mạnh thống kê cho việc kiểm định ý nghĩa.

### 9.2 — Các Corpus Dự kiến

| Corpus | Cặp | Trạng thái | Chủ sở hữu |
|--------|------|--------|-------|
| Corpus tùy chỉnh EN → TL (Filipino) | EN → TL | Đã lên kế hoạch | Chủ sở hữu dự án |
| Tập giữ lại EN → CRK | EN → CRK | Tương lai (cần đối tác cộng đồng) | Tổ chức quản trị cộng đồng |

---

## 10. Tích hợp Thẻ Ngôn ngữ (Language Card)

Khung thiết kế corpus tích hợp với hệ thống thẻ ngôn ngữ:

1. **Lựa chọn lĩnh vực** được định hướng bởi trường `linguisticChallenges` của thẻ — nếu một ngôn ngữ có các thách thức đặc thù (đa tổng hợp, thanh điệu, tính hữu sinh), corpus phải bao gồm các mục nhập để kiểm tra chúng.

2. **Hiệu chuẩn độ khó** sử dụng trường `classification` của thẻ — khoảng cách loại hình học giữa họ ngôn ngữ nguồn và mục tiêu sẽ ảnh hưởng đến những gì được coi là "khó".

3. **Phạm vi bao phủ văn phong** sử dụng trường `registers` của thẻ — nếu một ngôn ngữ có các văn phong được xác định rõ (formal-filipino, taglish-professional, taglish-casual), corpus nên bao gồm các mục nhập ở từng mức độ văn phong.

4. **Kiểm tra ảnh hưởng tiếp xúc** sử dụng trường `contactInfluences` của thẻ — đối với các ngôn ngữ có các lớp từ mượn dày đặc (tiếng Filipino: tiếng Tây Ban Nha + tiếng Anh + tiếng Ả Rập), hãy bao gồm các mục nhập để kiểm tra xem các phương pháp có xử lý từ mượn một cách chính xác hay dịch quá đà (over-translating) chúng.

5. **Xử lý hệ chữ viết** sử dụng trường `scripts[]` của thẻ — đối với các ngôn ngữ sử dụng nhiều hệ chữ viết (tiếng Serbia: chữ Cyrillic + chữ Latinh), hãy bao gồm các mục nhập để kiểm tra việc lựa chọn hệ chữ viết chính xác.

---

## Tài liệu Tham khảo

- **Champollion Scoring Specification** — định nghĩa tất cả các chỉ số, trọng số tổng hợp, các bậc chất lượng
- **Champollion Benchmark Specification** — giao thức đánh giá, định dạng corpus, chủ quyền dữ liệu
- **WALS** (World Atlas of Language Structures) — cơ sở dữ liệu về các đặc điểm loại hình học
- **Glottolog** — nguồn thông tin gốc về phân loại ngôn ngữ
- **ISO 639-3** — tiêu chuẩn định danh ngôn ngữ
- **EdTeKLA** — nguồn của corpus đánh giá đầu tiên

---

*Tài liệu này là một đặc tả động (living specification). Hãy cập nhật nó khi các corpus mới được xây dựng và các bài học kinh nghiệm được rút ra.*