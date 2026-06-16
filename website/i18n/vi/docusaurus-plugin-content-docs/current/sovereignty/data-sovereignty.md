---
sidebar_position: 7
title: "Chủ quyền Dữ liệu"
description: "Các nguyên tắc OCAP, CARE và Chủ quyền Dữ liệu Māori đối với dịch thuật ngôn ngữ bản địa. Vì sao sự đồng thuận của cộng đồng cần có trước khi triển khai."
related:
  - label: "Ownership Transfer"
    to: /docs/sovereignty/ownership-transfer
    kind: doc
    note: "How control of language data moves to communities"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
---
# Chủ quyền Dữ liệu

> **Tóm tắt tổng quan.** Trang này giải thích các nguyên tắc chủ quyền dữ liệu OCAP®, CARE và Te Mana Raraunga, cũng như ý nghĩa của chúng đối với các nhà phát triển đang xây dựng các phương pháp dịch thuật cho các ngôn ngữ bản địa. Nội dung bao gồm thời điểm cần có sự đồng ý của cộng đồng, cách kiến trúc phương pháp `api` của champollion hỗ trợ chủ quyền dữ liệu, và các nghĩa vụ đạo đức của bất kỳ ai làm việc với dữ liệu ngôn ngữ bản địa.

Dịch máy cho các ngôn ngữ bản địa đặt ra những câu hỏi không hề tồn tại đối với tiếng Pháp hay tiếng Nhật. Ai là người sở hữu dữ liệu huấn luyện? Ai kiểm soát cách một mô hình ngôn ngữ phát ngôn? Ai quyết định liệu một bản dịch có đủ tốt để xuất bản hay không?

**Câu trả lời luôn luôn là cộng đồng.**

champollion được xây dựng để hỗ trợ điều này. Phương pháp `api` giữ tất cả tài nguyên ngôn ngữ ở phía máy chủ dưới sự kiểm soát của cộng đồng. Hệ thống plugin tách biệt phương pháp khỏi công cụ. Nhưng công cụ không thể thực thi các nguyên tắc đạo đức — trang này giải thích các nguyên tắc mà bạn nên tuân theo.

---

## Các nguyên tắc OCAP®

**OCAP** (Ownership, Control, Access, Possession - Quyền sở hữu, Quyền kiểm soát, Quyền truy cập, Quyền chiếm hữu) là một bộ các nguyên tắc được phát triển bởi [First Nations Information Governance Centre](https://fnigc.ca/ocap-training/) (FNIGC) nhằm thiết lập cách thức dữ liệu của các Quốc gia Sơ khai (First Nations) nên được thu thập, bảo vệ, sử dụng và chia sẻ.

| Nguyên tắc | Ý nghĩa đối với dịch thuật |
|-----------|------------------------------|
| **Ownership** (Quyền sở hữu) | Cộng đồng sở hữu dữ liệu ngôn ngữ của chính họ — từ điển, ngữ pháp, văn bản song ngữ, các tệp huấn luyện (coaching files) và bất kỳ bản dịch nào được tạo ra từ chúng. |
| **Control** (Quyền kiểm soát) | Cộng đồng kiểm soát cách dữ liệu ngôn ngữ của họ được sử dụng, ai có quyền truy cập và phương pháp dịch thuật nào là có thể chấp nhận được. |
| **Access** (Quyền truy cập) | Các thành viên trong cộng đồng có quyền truy cập và quản lý các tài nguyên ngôn ngữ của riêng họ, bất kể chúng được lưu trữ ở đâu. |
| **Possession** (Quyền chiếm hữu) | Dữ liệu vật lý (các tệp huấn luyện, từ điển, trọng số mô hình) phải nằm trên cơ sở hạ tầng mà cộng đồng kiểm soát — không phải trên đám mây của bên thứ ba. |

### Ý nghĩa thực tế của OCAP

- **Không xuất bản các bản dịch** của một ngôn ngữ bản địa mà không có sự cho phép rõ ràng từ cộng đồng.
- **Không huấn luyện các mô hình** trên dữ liệu ngôn ngữ do cộng đồng cung cấp mà không có thỏa thuận chia sẻ dữ liệu.
- **Không thu thập dữ liệu (scrape)** tài nguyên ngôn ngữ của cộng đồng từ các trang web, mạng xã hội hoặc tài liệu giáo dục.
- **Sử dụng phương pháp `api`** để các prompt, dữ liệu huấn luyện (coaching data) và từ điển luôn nằm trên các máy chủ do cộng đồng kiểm soát. Phương pháp `api` của champollion hoạt động như một "đường ống thụ động" (dumb pipe) — nó gửi các khóa (keys) đi và nhận lại các bản dịch. Tất cả sở hữu trí tuệ (IP) ngôn ngữ đều được giữ ở phía máy chủ.
- **Ghi nhận nguồn gốc (provenance)** — trường `provenance` trong [plugin manifest](https://champollion.dev/docs/reference/plugin-spec) phải liệt kê mọi tài nguyên được sử dụng, giấy phép và nguồn gốc của nó.

:::warning OCAP® là nhãn hiệu đã được đăng ký bảo hộ
OCAP® là nhãn hiệu đã được đăng ký bảo hộ của First Nations Information Governance Centre. Nguyên tắc này áp dụng cụ thể cho các Quốc gia Sơ khai (First Nations) ở Canada. Các nguyên tắc này có ý nghĩa ứng dụng rộng rãi hơn, nhưng nhãn hiệu và quyền quản trị thuộc về FNIGC.
:::

---

## Các nguyên tắc CARE

**Các nguyên tắc CARE về Quản trị Dữ liệu Bản địa** được phát triển bởi [Global Indigenous Data Alliance](https://www.gida-global.org/care) (GIDA) như một sự bổ sung cho các nguyên tắc dữ liệu FAIR. FAIR quy định rằng dữ liệu phải có khả năng Tìm kiếm được (Findable), Truy cập được (Accessible), Tương thích được (Interoperable) và Tái sử dụng được (Reusable). CARE chỉ ra rằng điều đó là chưa đủ — quản trị dữ liệu cũng phải đặt quyền lợi của người bản địa làm trung tâm.

| Nguyên tắc | Ứng dụng |
|-----------|------------|
| **Collective Benefit** (Lợi ích tập thể) | Các công cụ dịch thuật trước hết phải mang lại lợi ích cho cộng đồng ngôn ngữ đó. Điểm số trên bảng xếp hạng (leaderboard) là phương tiện để cải thiện các phương pháp, chứ không phải để khai thác giá trị thương mại từ các ngôn ngữ của cộng đồng. |
| **Authority to Control** (Quyền kiểm soát) | Các cộng đồng có quyền quản trị cách dữ liệu ngôn ngữ của họ được thu thập, sử dụng và chia sẻ. Điểm số cao trên bảng xếp hạng không đồng nghĩa với việc được phép xuất bản các bản dịch. |
| **Responsibility** (Trách nhiệm) | Các nhà nghiên cứu và nhà phát triển làm việc với dữ liệu ngôn ngữ bản địa có trách nhiệm xây dựng mối quan hệ, xin phép sự đồng ý và chia sẻ lợi ích. |
| **Ethics** (Đạo đức) | Quyền lợi và sự thịnh vượng của các dân tộc bản địa phải là mối quan tâm hàng đầu. Các phương pháp dịch thuật nên được phát triển *cùng với* cộng đồng, chứ không phải *về* họ. |

---

## Te Mana Raraunga — Chủ quyền Dữ liệu Māori

**Te Mana Raraunga** là [Mạng lưới Chủ quyền Dữ liệu Māori](https://www.temanararaunga.maori.nz/). Mạng lưới này khẳng định rằng dữ liệu Māori — bao gồm cả dữ liệu ngôn ngữ — là một taonga (báu vật) tuân theo các nguyên tắc của Hiệp ước Waitangi và tikanga Māori (luật tục của người Māori).

Các nguyên tắc chính:

| Nguyên tắc | Ý nghĩa |
|-----------|---------|
| **Rangatiratanga** (Quyền lực/Thẩm quyền) | Người Māori có quyền tự nhiên trong việc thực thi thẩm quyền đối với dữ liệu của họ, bao gồm cả dữ liệu ngôn ngữ. |
| **Whakapapa** (Mối quan hệ/Nguồn cội) | Dữ liệu có nguồn gốc và các mối liên kết. Dữ liệu ngôn ngữ mang theo các mối quan hệ và tri thức của những người đã tạo ra nó. |
| **Whanaungatanga** (Nghĩa vụ tương hỗ) | Những người nắm giữ hoặc xử lý dữ liệu Māori có nghĩa vụ tương hỗ đối với các cộng đồng nơi dữ liệu đó xuất phát. |
| **Kotahitanga** (Lợi ích tập thể) | Dữ liệu Māori nên được sử dụng vì lợi ích tập thể của người Māori. |
| **Manaakitanga** (Sự tôn trọng và tương hỗ) | Việc sử dụng dữ liệu Māori phải đi kèm với sự quan tâm, tôn trọng và tính tương hỗ. |
| **Kaitiakitanga** (Quyền giám hộ) | Những người giám hộ dữ liệu có nghĩa vụ bảo vệ dữ liệu và đảm bảo dữ liệu được sử dụng một cách thích hợp. |

Các nguyên tắc này áp dụng cho te reo Māori (tiếng Māori) và cho bất kỳ công việc tính toán nào liên quan đến dữ liệu tiếng Māori.

---

## Ý nghĩa đối với người dùng champollion

### Đối với các ngôn ngữ phổ biến (tiếng Pháp, tiếng Nhật, tiếng Tây Ban Nha...)

Hãy sử dụng champollion như bình thường. Các ngôn ngữ này có kho ngữ liệu lớn, công khai, các API dịch thuật đã được thiết lập sẵn và không có lo ngại về vấn đề chủ quyền. Bạn có thể dịch, đồng bộ hóa và xuất bản tùy ý.

### Đối với các ngôn ngữ bản địa và ngôn ngữ ít tài nguyên

Tình hình hoàn toàn khác biệt:

1. **Xin phép sự đồng ý trước.** Trước khi xây dựng một phương pháp dịch thuật cho một ngôn ngữ bản địa, hãy thiết lập mối quan hệ với cộng đồng. Một phương pháp được xây dựng mà không có sự tham gia của cộng đồng — dù có ấn tượng về mặt kỹ thuật đến đâu — cũng không nên được xuất bản hoặc phân phối.

2. **Sử dụng phương pháp `api`.** Lưu trữ quy trình dịch thuật (translation pipeline) trên cơ sở hạ tầng do cộng đồng kiểm soát. Phương pháp `api` trong champollion được thiết kế cho việc này: nó gửi các khóa và nhận lại các bản dịch mà không làm lộ các prompt, từ điển hoặc dữ liệu huấn luyện (coaching data) giúp phương pháp hoạt động.

    ```json title="Community-controlled setup"
    {
      "pairs": {
        "en:crk": {
          "method": "api",
          "endpoint": "https://api.community-server.example/translate"
        }
      }
    }
    ```

3. **Tài liệu hóa mọi thứ.** Sử dụng trường `provenance` trong plugin manifest của bạn để liệt kê mọi tài nguyên, giấy phép của nó và liệu nó có được cung cấp với sự đồng ý của cộng đồng hay không.

4. **Điểm số không phải là giấy phép.** Điểm số cao trên bảng xếp hạng chứng minh rằng một phương pháp hoạt động tốt về mặt kỹ thuật. Nó không cấp quyền xuất bản các bản dịch, phân phối plugin hoặc thương mại hóa phương pháp đó. Cộng đồng mới là bên quyết định.

5. **Chia sẻ phương pháp, không chia sẻ dữ liệu.** Nếu bạn phát triển một kỹ thuật hoạt động tốt (ví dụ: "FST-gated LLM với coached prompts"), hãy chia sẻ *kiến trúc* và *cách tiếp cận* trên bảng xếp hạng. Cộng đồng sẽ giữ quyền kiểm soát đối với dữ liệu ngôn ngữ giúp phương pháp đó hoạt động cho ngôn ngữ cụ thể của họ.

---

## Phương pháp `api` và Chủ quyền

[Phương pháp dịch thuật](https://champollion.dev/docs/guides/translation-methods) `api` tồn tại cụ thể là để hỗ trợ chủ quyền dữ liệu. Dưới đây là lý do:

| Khía cạnh | Các phương pháp khác | Phương pháp `api` |
|--------|--------------|-------------|
| **Nơi lưu trữ prompt** | Trong các tệp cấu hình (config) của champollion (mọi nhà phát triển đều có thể nhìn thấy) | Trên máy chủ của cộng đồng (riêng tư) |
| **Nơi lưu trữ dữ liệu huấn luyện (coaching data)** | Trong thư mục `.champollion/coaching/` (được commit lên git) | Trên máy chủ của cộng đồng (riêng tư) |
| **Nơi lưu trữ từ điển** | Trong thư mục plugin (được phân phối cùng với plugin) | Trên máy chủ của cộng đồng (riêng tư) |
| **Ai kiểm soát quy trình (pipeline)** | Bất kỳ ai chạy lệnh `champollion sync` | Cộng đồng vận hành API |
| **Những gì champollion nhìn thấy** | Tất cả mọi thứ | Khóa gửi vào, bản dịch trả về |

Phương pháp `api` là một lựa chọn kiến trúc có chủ ý. Nó là một "đường ống thụ động" vì sở hữu trí tuệ (IP) — tri thức ngôn ngữ, các quy tắc ngữ pháp, các ví dụ huấn luyện được tuyển chọn kỹ lưỡng — thuộc về cộng đồng, chứ không phải thuộc về công cụ.

Xem [Serving a Method via API](https://champollion.dev/docs/guides/serving-a-method) để biết chi tiết triển khai.

---

## Nghiên cứu điển hình: OMT-1600 và Chủ quyền Dữ liệu

OMT-1600 của Meta (tháng 3 năm 2026) cung cấp một ví dụ cụ thể về lý do tại sao chủ quyền dữ liệu lại quan trọng đối với các ngôn ngữ bản địa. OMT-1600 đã huấn luyện các mô hình dịch thuật cho 1.600 ngôn ngữ bằng cách sử dụng:

- **CC-2000-Web**: Văn bản đơn ngữ được thu thập từ web (web-scraped) từ hơn 2.000 thực thể ngôn ngữ (languoids) — được thu thập mà không có sự đồng ý của cộng đồng
- **Các bản dịch Kinh Thánh**: Các văn bản tôn giáo được sử dụng làm dữ liệu huấn luyện và đánh giá song ngữ cho các ngôn ngữ có tài nguyên thấp nhất
- **MeDLEy**: Văn bản song ngữ (bitext) được tuyển chọn thủ công — nhưng không có tài liệu chứng minh việc tuân thủ OCAP® hoặc CARE
- **Dữ liệu tổng hợp dịch ngược (Backtranslated synthetic data)**: Khoảng 270 triệu câu song ngữ tổng hợp do chính các mô hình tạo ra

Đối với các ngôn ngữ bản địa như tiếng Plains Cree (CRK), điều này có nghĩa là:

| Nguyên tắc | Thực tế của OMT-1600 | Tác động |
|-----------|-------------------|--------|
| **Ownership** (Quyền sở hữu) | Meta sở hữu các mô hình và quyết định cách phát hành chúng | Cộng đồng không có cổ phần sở hữu trong cách ngôn ngữ của họ được mô hình hóa |
| **Control** (Quyền kiểm soát) | Meta kiểm soát việc lựa chọn dữ liệu huấn luyện, kiến trúc mô hình và lịch trình phát hành | Cộng đồng không có đóng góp ý kiến về việc dữ liệu nào được sử dụng hoặc ngôn ngữ được thể hiện như thế nào |
| **Access** (Quyền truy cập) | Trọng số mô hình hiện không khả dụng — "không được phát hành do các yếu tố nằm ngoài tầm kiểm soát của các tác giả" | Cộng đồng không thể truy cập, kiểm tra hoặc sửa đổi mô hình nói ngôn ngữ của họ |
| **Possession** (Quyền chiếm hữu) | Tất cả dữ liệu và mô hình đều nằm trên cơ sở hạ tầng của Meta | Cộng đồng không thể lưu trữ, kiểm toán hoặc xóa dữ liệu được sử dụng để huấn luyện mô hình |

OMT-1600 là một thành tựu nghiên cứu. Nhưng nó cũng là một ví dụ về thực hành khai thác dữ liệu: dữ liệu ngôn ngữ được thu thập từ web và các văn bản tôn giáo, được xử lý thành một mô hình và được công bố dưới dạng một bài báo khoa học — tất cả đều không có sự tham gia, đồng ý hoặc chia sẻ lợi ích với cộng đồng.

**Đây chính xác là mô hình mà kiến trúc chủ quyền của champollion ngăn chặn.** Phương pháp `api` giữ sở hữu trí tuệ (IP) ngôn ngữ trên các máy chủ do cộng đồng kiểm soát. Các ngữ liệu đánh giá được cung cấp với sự đồng ý của cộng đồng và được lưu trữ dưới sự quản lý khóa của cộng đồng. Các phương pháp đoạt giải được chuyển giao quyền sở hữu cho cộng đồng. Sự khác biệt không nằm ở kỹ thuật — mà nằm ở đạo đức và cấu trúc.

:::note OMT-1600 không phải là trường hợp duy nhất có lỗi
Mô hình này — thu thập dữ liệu web sau đó huấn luyện mô hình mà không có sự đồng ý của cộng đồng — là thực hành tiêu chuẩn trong nghiên cứu NLP đa ngôn ngữ quy mô lớn. OMT-1600 được chọn làm nghiên cứu điển hình vì quy mô của nó (1.600 ngôn ngữ) và tính cập nhật (tháng 3 năm 2026), chứ không phải vì nó là trường hợp khai thác duy nhất. Lời phê bình tương tự cũng áp dụng cho NLLB-200, các nỗ lực đa ngôn ngữ của Google và hầu hết các nghiên cứu dịch máy (MT) quy mô lớn khác.
:::

---

## Đọc thêm

- [First Nations Information Governance Centre — OCAP®](https://fnigc.ca/ocap-training/)
- [Global Indigenous Data Alliance — Các nguyên tắc CARE](https://www.gida-global.org/care)
- [Te Mana Raraunga — Mạng lưới Chủ quyền Dữ liệu Māori](https://www.temanararaunga.maori.nz/)
- [USIDSN — Mạng lưới Chủ quyền Dữ liệu Bản địa Hoa Kỳ](https://usindigenousdata.org/)

---

## Xem thêm

- [Hỗ trợ một ngôn ngữ ít tài nguyên](/docs/community/low-resource-languages) — hướng dẫn kỹ thuật với bối cảnh OCAP
- [Các phương pháp dịch thuật](https://champollion.dev/docs/guides/translation-methods) — phương pháp `api` và cách nó bảo vệ IP
- [Cung cấp một phương pháp qua API](https://champollion.dev/docs/guides/serving-a-method) — lưu trữ một quy trình do cộng đồng kiểm soát
- [Đặc tả Plugin](https://champollion.dev/docs/reference/plugin-spec) — trường `provenance` để ghi nhận nguồn tài nguyên
- [Cookbook: Quy trình FST-Gated](/docs/tutorials/fst-gated-pipeline) — xây dựng một quy trình mà cộng đồng có thể tự lưu trữ