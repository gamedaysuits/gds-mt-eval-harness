---
sidebar_position: 2
title: "Câu hỏi thường gặp"
related:
  - label: "How It Works"
    to: /docs/how-it-works
    kind: doc
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Glossary"
    to: https://champollion.dev/glossary
    kind: glossary
    note: "Plain-language definitions for every technical term"
---
# Câu hỏi thường gặp

> **Tóm tắt nhanh.** Câu trả lời cho các câu hỏi thường gặp về MT Eval Arena — cách tính điểm, những trường hợp bị loại, cách xử lý các ngôn ngữ không có FST, đề xuất về mô hình và tham số, cũng như quy trình gửi bài.

---

## Điểm số & Chỉ số đánh giá

### Bộ khung đánh giá tính toán những chỉ số nào?

Bộ khung đánh giá tính toán năm chỉ số cho tiếng Plains Cree (ngôn ngữ chuẩn đối sánh hiện tại). Ba chỉ số trong số đó độc lập với ngôn ngữ và hoạt động với mọi ngôn ngữ; hai chỉ số còn lại hiện phụ thuộc vào các plugin dành riêng cho CRK và sẽ được tổng quát hóa khi chúng tôi mở rộng sang nhiều ngôn ngữ hơn.

| Chỉ số | Thang đo | Đối tượng đo lường | Trạng thái |
|--------|-------|-----------------|--------|
| **chrF++** | 0–100 | Độ trùng lặp n-gram ký tự giữa bản dịch dự đoán và bản dịch tham chiếu. Chỉ số bề mặt tốt nhất cho các ngôn ngữ giàu hình thái. Sử dụng cách tính điểm gốc của sacrebleu. | ✅ Tất cả ngôn ngữ |
| **Exact match** | 0.0–1.0 | Tỷ lệ các mục mà bản dịch dự đoán khớp hoàn toàn với bản dịch tham chiếu sau khi chuẩn hóa. | ✅ Tất cả ngôn ngữ |
| **FST acceptance** | 0.0–1.0 | Tỷ lệ các từ đầu ra được chấp nhận bởi bộ chuyển đổi trạng thái hữu hạn (bộ phân tích hình thái). Chỉ được tính toán khi tệp nhị phân FST được cung cấp. | ✅ Tất cả ngôn ngữ có FST |
| **Equivalent match** | 0.0–1.0 | Tỷ lệ các mục khớp với bản dịch tham chiếu hoặc một biến thể chấp nhận được — có tính đến trật tự từ, quy ước chính tả và sự khác biệt về phương ngữ. | ⚡ CRK (đang tổng quát hóa) |
| **Semantic score** | 0.0–1.0 | Điểm bảo toàn ngữ nghĩa — mức độ bản dịch truyền tải đúng ý nghĩa mong muốn bất kể hình thức bề mặt? | ⚡ CRK (đang tổng quát hóa) |

Các chỉ số bổ sung đang được lên kế hoạch: **morphological accuracy**, **code-switching detection**, **terminology adherence**, và **hallucination detection**. Xem [Tài liệu đặc tả tính điểm §2](/docs/specifications/scoring#2-metric-inventory) để biết danh mục đầy đủ gồm 19 chỉ số.

### Điểm composite score được tính như thế nào?

Điểm composite score là trung bình có trọng số của các chỉ số hiện có, được chuẩn hóa theo thang điểm từ 0.0–1.0. Trọng số được định nghĩa trong hai cấu hình (profile):

- **Profile A** (ngôn ngữ có FST): 9 chỉ số, các chỉ số cấu trúc (FST + morphological accuracy) chiếm 40% trọng số composite score
- **Profile B** (ngôn ngữ không có FST): 8 chỉ số, semantic score và chrF++ chiếm trọng số cao nhất bằng nhau

Khi một chỉ số không khả dụng, trọng số của nó sẽ được phân bổ lại theo tỷ lệ cho các chỉ số còn lại. Điều này có nghĩa là các chuẩn đối sánh ở giai đoạn đầu (chỉ có sẵn chrF++ và exact match) vẫn tạo ra điểm composite score hợp lệ — trọng số thực tế chỉ phản ánh những gì đang có sẵn.

**Bảng trọng số đầy đủ, quy tắc chuẩn hóa và lý do loại trừ được trình bày chi tiết trong [Tài liệu đặc tả tính điểm §4](/docs/specifications/scoring#4-composite-score).** Mã nguồn của bộ khung đánh giá phản ánh các bảng này trong `mt_eval_harness/scoring.py`. chrF++ được chuẩn hóa bằng cách chia cho 100 trước khi tính trọng số; tỷ lệ code-switching và hallucination được đảo ngược (thấp hơn = tốt hơn).

### Các phân cấp chất lượng (quality tiers) là gì?

Các phân cấp chất lượng là các nhãn phỏng đoán được ánh xạ tới các khoảng điểm composite score. Chúng giúp truyền đạt ý nghĩa thực tế của một mức điểm:

| Phân cấp | Khoảng điểm Composite | Ý nghĩa |
|------|----------------|----------------|
| **Baseline** | 0.00 – 0.30 | Dưới mức chất lượng hữu ích. Phương pháp cần cải thiện đáng kể. |
| **Emerging** | 0.30 – 0.50 | Cho thấy triển vọng. Một số bản dịch chính xác nhưng không nhất quán. |
| **Functional** | 0.50 – 0.70 | Có thể sử dụng để tham khảo khi có con người kiểm duyệt. Không phù hợp để triển khai trực tiếp mà không qua kiểm duyệt. |
| **Deployable** | 0.70 – 0.85 | Sẵn sàng sử dụng trong môi trường thực tế với việc kiểm duyệt định kỳ. Đủ điều kiện để kích hoạt chuyển giao quyền sở hữu. |
| **Fluent** | 0.85 – 1.00 | Chất lượng gần như người bản xứ. Phù hợp để triển khai tự động không cần giám sát. |

### Sự khác biệt giữa phân cấp chất lượng và phân cấp xác minh là gì?

**Phân cấp chất lượng** mô tả *ý nghĩa của điểm số tự động* (Baseline → Fluent). **Phân cấp xác minh** mô tả *ai là người đã xác thực kết quả đó*:

| Phân cấp xác minh | Ý nghĩa |
|-------------------|---------------|
| **Self-benchmarked** | Người gửi tự chạy bộ khung đánh giá. Điểm số có vẻ hợp lý nhưng chưa được xác minh. |
| **GDS Verified** | Người duy trì dự án đã tái hiện lại kết quả bằng cách sử dụng cấu hình phương pháp được gửi. |
| **Community Validated** | Những người nói song ngữ đã xem xét các bản dịch và xác nhận chất lượng. |

Một phương pháp có thể đạt chất lượng "Deployable" nhưng chỉ ở mức xác minh "Self-benchmarked" — nghĩa là điểm số trông rất tuyệt vời nhưng chưa có ai độc lập xác nhận kết quả đó.

---

## Gửi bài & Loại hồ sơ

### Điều gì khiến bài gửi của tôi bị loại?

Bài gửi của bạn sẽ bị từ chối hoặc bị gắn cờ nếu:

1. **Phương pháp của bạn đã tiếp xúc với dữ liệu đánh giá.** Nếu bạn đã huấn luyện, tinh chỉnh (fine-tune), gợi ý vài mẫu (few-shot-prompt), hoặc sử dụng bất kỳ mục nào từ tập dữ liệu đánh giá bằng cách khác, điểm số của bạn đã bị thổi phồng một cách nhân tạo. Điều này bao gồm cả việc sử dụng các bản dịch tham chiếu trong câu lệnh (prompt) của bạn.
2. **Thẻ chạy (run card) của bạn không vượt qua các kiểm tra tính toàn vẹn.** Dấu vân tay (fingerprint) phải khớp với cấu hình. Các thẻ chạy bị can thiệp sẽ bị từ chối.
3. **Phương pháp của bạn không triển khai giao thức TranslationMethod.** Bộ khung đánh giá yêu cầu `translate(entries, config) → results`. Các tích hợp tùy chỉnh bỏ qua bộ khung đánh giá sẽ không được chấp nhận.

### Tôi có thể gửi bài nhiều lần không?

Có. Bảng xếp hạng theo dõi tất cả các lượt gửi bài. Bạn có thể lặp đi lặp lại — chạy hàng tá thử nghiệm và chỉ gửi kết quả tốt nhất của mình. Mỗi lượt gửi bài đều ghi lại một dấu vân tay (fingerprint) duy nhất, vì vậy không có sự mơ hồ về việc lượt chạy nào đã tạo ra điểm số nào.

### Làm thế nào để điểm số của tôi được xác minh?

1. **Self-benchmarked (tự động):** Mọi bài gửi đều bắt đầu từ đây.
2. **GDS Verified:** Gửi phương pháp của bạn dưới dạng một gói có thể tái hiện (mã nguồn + cấu hình + dữ liệu huấn luyện/coaching data). Người duy trì dự án sẽ chạy lại phương pháp đó trên cùng một tập dữ liệu và xác nhận các điểm số trùng khớp.
3. **Community Validated:** Đối với các ngôn ngữ bản địa, điều này yêu cầu những người nói song ngữ xem xét một mẫu bản dịch. Quá trình này không thể tự động hóa — nó đòi hỏi sự tham gia của cộng đồng.

### API gửi bài đã hoạt động chưa?

Chưa. Điểm cuối (endpoint) `https://mtevalarena.org/api/leaderboard/submit` hiện tại là mục tiêu hướng tới. Các bài gửi hiện tại nên được thực hiện thông qua pull request tới [kho lưu trữ eval harness](https://github.com/gamedaysuits/arena) với tệp JSON thẻ chạy của bạn nằm trong thư mục `results/`.

---

## Mô hình & Tham số

### Tôi nên sử dụng mô hình nào?

Không có một mô hình nào là tốt nhất cho mọi trường hợp — điều đó phụ thuộc vào cặp ngôn ngữ, ngân sách và cách tiếp cận của bạn. Hướng dẫn chung:

| Loại ngôn ngữ | Điểm bắt đầu khuyến nghị | Lý do |
|---------------|---------------------------|-----|
| **Tài nguyên cao** (tiếng Pháp, tiếng Tây Ban Nha, tiếng Nhật) | `google/gemini-2.5-flash` hoặc `gpt-4o-mini` | Nhanh, rẻ, baseline mạnh mẽ |
| **Tài nguyên thấp có một số mức độ hỗ trợ từ LLM** (tiếng Quechua, tiếng Yoruba) | `google/gemini-2.5-pro` hoặc `anthropic/claude-sonnet-4` | Các mô hình lớn hơn có tri thức ẩn (latent knowledge) tốt hơn |
| **Đa tổng hợp / tài nguyên cực thấp** (tiếng Plains Cree, tiếng Inuktitut) | `google/gemini-2.5-pro` với coaching | Dữ liệu huấn luyện (coaching data) quan trọng hơn việc lựa chọn mô hình. OMT-1600 bao gồm một số ngôn ngữ đa tổng hợp (ví dụ: CRK ở phân cấp R1) nhưng sử dụng phân tách từ chuẩn BPE tiêu chuẩn — hãy đánh giá nó như một baseline trong Arena. |

Bộ khung đánh giá sử dụng OpenRouter, so any model available on OpenRouter can be benchmarked. Chạy `champollion models --method llm` để xem các mô hình khả dụng.

### Tôi nên sử dụng mức nhiệt độ (temperature) nào?

Nhiệt độ thấp hơn thường tốt hơn cho tác vụ dịch thuật:

| Nhiệt độ (Temperature) | Ảnh hưởng | Khuyến nghị cho |
|-------------|--------|-----------------|
| **0.0 – 0.2** | Tính xác định cao, đầu ra nhất quán | Các phương pháp triển khai thực tế, đánh giá chuẩn đối sánh cuối cùng |
| **0.3 – 0.5** | Có một số biến thể, đôi khi sáng tạo hơn | Khám phá, lặp thử nghiệm ở giai đoạn đầu |
| **0.6+** | Biến động cao, không thể dự đoán | Không khuyến nghị cho việc đánh giá chuẩn đối sánh dịch máy |

Nhiệt độ được ghi lại trong thẻ chạy, vì vậy các mức nhiệt độ khác nhau sẽ tạo ra các dấu vân tay (fingerprint) khác nhau — chúng được coi là các thử nghiệm khác nhau.

### Dữ liệu huấn luyện (coaching data) có giúp ích không?

Có, rất nhiều — đối với các ngôn ngữ tài nguyên thấp. Dữ liệu huấn luyện (coaching data - bao gồm các quy tắc ngữ pháp, mục từ điển, lưu ý về phong cách) được đưa vào câu lệnh hệ thống (system prompt) của LLM. Đối với tiếng Plains Cree, các phương pháp có sử dụng coaching liên tục vượt trội hơn các phương pháp LLM thuần túy đối với các ngôn ngữ đa tổng hợp, vì các LLM đa dụng có mức độ tiếp xúc hạn chế với ngôn ngữ đa tổng hợp và không có nhận thức về mặt hình thái. Ngay cả OMT-1600, vốn được huấn luyện riêng cho CRK, cũng sử dụng phân tách từ chuẩn BPE tiêu chuẩn vốn không thể biểu diễn cấu trúc hình thái đa tổng hợp. Dữ liệu huấn luyện cung cấp ngữ cảnh ngôn ngữ học mà mô hình còn thiếu.

Đối với các ngôn ngữ tài nguyên cao (tiếng Pháp, tiếng Tây Ban Nha), coaching ít có tác động hơn vì mô hình đã có sẵn tri thức nền tảng mạnh mẽ.

Xem [Dữ liệu huấn luyện (Coaching Data)](https://champollion.dev/docs/concepts/coaching-data) để biết đặc tả đầy đủ.

---

## FST & Xác thực hình thái

### Sẽ ra sao nếu không có FST cho ngôn ngữ của tôi?

Nhiều ngôn ngữ không có bộ chuyển đổi trạng thái hữu hạn (FST). Điều đó không sao cả — bộ khung đánh giá vẫn hoạt động mà không cần nó. Điểm composite score sử dụng trọng số của Profile B (xem [Tài liệu đặc tả tính điểm §4.3](/docs/specifications/scoring#43-weight-tables)), giúp chuyển trọng số sang các chỉ số ngữ nghĩa và bề mặt. Trạng thái chấp nhận FST được đánh dấu là `null` trong thẻ chạy.

Các kho đăng ký chính cho các FST hiện có:

| Kho đăng ký | Phạm vi hỗ trợ | URL |
|----------|----------|-----|
| **GiellaLT** | Tiếng Sámi, tiếng Cree, tiếng Inuktitut và các ngôn ngữ vùng Bắc Cực/cận Bắc Cực khác | [giellalt.uit.no](https://giellalt.uit.no/) |
| **ALTLab** | Tiếng Plains Cree, tiếng Woods Cree, tiếng Ojibwe | [altlab.artsrn.ualberta.ca](https://altlab.artsrn.ualberta.ca/) |
| **Apertium** | Khoảng 60 cặp ngôn ngữ, chủ yếu là các ngôn ngữ châu Âu | [apertium.org](https://apertium.org/) |
| **UniMorph** | Các mô hình hình thái cho hơn 150 ngôn ngữ | [unimorph.github.io](https://unimorph.github.io/) |

### Tôi có thể tự xây dựng một FST không?

Có, nhưng việc này không hề đơn giản. Một FST mã hóa các quy tắc hình thái của một ngôn ngữ — tất cả các dạng từ hợp lệ. Việc xây dựng một FST đòi hỏi kiến thức ngôn ngữ học sâu sắc về ngôn ngữ đó. Nếu bạn có quyền truy cập vào tài liệu ngữ pháp hình thái (ví dụ: từ một khoa ngôn ngữ học), nó có thể được biên dịch thành một FST bằng cách sử dụng các công cụ như [HFST](https://hfst.github.io/) hoặc [Foma](https://fomafst.github.io/).

### Cơ chế lọc bằng FST (FST gating) hoạt động như thế nào trên thực tế?

Đường ống xử lý được lọc bằng FST (FST-gated pipeline) hoạt động như sau:

1. LLM tạo ra một bản dịch
2. Mỗi từ trong đầu ra được kiểm tra đối chiếu với FST
3. Các từ bị FST từ chối sẽ bị gắn cờ là không hợp lệ về mặt hình thái
4. Phương pháp có thể thử lại với phản hồi ("từ X không hợp lệ, hãy thử lại")
5. Sau các lượt thử lại, các từ không hợp lệ còn lại sẽ được ghi nhật ký (log)

Tỷ lệ chấp nhận FST (FST acceptance rate) đo lường số lượng từ vượt qua bước xác thực. Xem [Hướng dẫn về đường ống xử lý được lọc bằng FST](/docs/tutorials/fst-gated-pipeline) để biết ví dụ thực tế hoàn chỉnh.

---

## Dữ liệu & Tập dữ liệu

### Tôi có thể đóng góp tập dữ liệu cho một ngôn ngữ mới không?

Có. Các yêu cầu tối thiểu từ [Tài liệu đặc tả chuẩn đối sánh §11](/docs/specifications/benchmark#11-extending-to-new-languages):

- **50 mục tiêu chuẩn vàng (gold-standard)** (nguồn + bản dịch tham chiếu đã được xác minh)
- **30 mục phát triển (development)** (có thể trùng lặp với tiêu chuẩn vàng đối với các ngữ liệu nhỏ)
- **Sự đồng thuận của cộng đồng** (đối với các ngôn ngữ bản địa, cần có sự cho phép rõ ràng từ một cơ quan quản lý)
- **Tài liệu về nguồn gốc xuất xứ** (dữ liệu đến từ đâu, áp dụng giấy phép nào)

Các tập dữ liệu mới sẽ tự động mở ra các nhánh bảng xếp hạng mới. Xem [Dành cho cộng đồng ngôn ngữ](/docs/community/for-language-communities) để biết hướng dẫn dành cho người đóng góp.

### Tập dữ liệu của tôi nên ở định dạng nào?

Định dạng JSON với các tên trường chuẩn tắc:

```json
{
  "name": "my-language-dev-v1",
  "language_pair": "en-xxx",
  "segment": "development",
  "version": "1.0",
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "[translation in target language]",
      "difficulty": 1,
      "domain": "general"
    }
  ]
}
```

Xem [Tập dữ liệu](/docs/leaderboard/datasets) để biết lược đồ (schema) đầy đủ và định nghĩa về các phân cấp độ khó.

---

## Chủ quyền & Quyền sở hữu

### Ai sở hữu phương pháp được xây dựng cho một ngôn ngữ bản địa?

Đối với các ngôn ngữ bản địa, các phương pháp đạt đến phân cấp Deployable (composite ≥ 0.70) VÀ vượt qua bước xác thực của cộng đồng sẽ kích hoạt quy trình [chuyển giao quyền sở hữu](/docs/sovereignty/ownership-transfer). Quyền sở hữu mã nguồn sẽ chuyển giao từ nhà nghiên cứu sang tổ chức quản lý của cộng đồng ngôn ngữ đó.

Nhà nghiên cứu vẫn giữ lại:
- Quyền công bố (các bài báo học thuật về phương pháp)
- Ghi nhận đóng góp trên bảng xếp hạng
- Quyền áp dụng các *kỹ thuật* tương tự cho các ngôn ngữ khác

Tổ chức quản lý sẽ nhận được:
- Toàn quyền sở hữu mã nguồn phương pháp và dữ liệu huấn luyện (coaching data)
- Quyền kiểm soát việc triển khai (khi nào, ở đâu, như thế nào)
- Doanh thu từ việc sử dụng API (90% cho cộng đồng, 10% cho cơ sở hạ tầng)

### Tôi có thể sử dụng champollion cho các ngôn ngữ không phải bản địa mà không cần lo ngại về vấn đề chủ quyền không?

Có. Đối với các ngôn ngữ phổ thông (tiếng Pháp, tiếng Nhật, tiếng Tây Ban Nha, v.v.), không có các cân nhắc về chủ quyền. Hãy sử dụng champollion một cách bình thường — dịch, đồng bộ hóa, xuất bản theo ý muốn của bạn. Khung chủ quyền áp dụng cụ thể cho các ngôn ngữ bản địa và ngôn ngữ do cộng đồng quản lý, nơi các nguyên tắc quản trị dữ liệu (OCAP®, CARE, Te Mana Raraunga) đòi hỏi sự cân nhắc đặc biệt.

---

## Xem thêm

- **[Cách thức hoạt động](https://champollion.dev/how-it-works)** — giải thích chi tiết về giải pháp
- **[Tài liệu đặc tả tính điểm](/docs/specifications/scoring)** — nguồn thông tin xác thực duy nhất (SSOT) cho tất cả logic tính điểm (chỉ số, trọng số, phân cấp)
- **[Tài liệu đặc tả chuẩn đối sánh](/docs/specifications/benchmark)** — giao thức đánh giá, định dạng ngữ liệu, chủ quyền
- **[Gửi một phương pháp](/docs/getting-started/submit-a-method)** — hướng dẫn nhanh từng bước
- **[Quy tắc bảng xếp hạng](/docs/leaderboard/rules)** — tiêu chí gửi bài
- **[Chủ quyền dữ liệu](/docs/sovereignty/data-sovereignty)** — OCAP®, CARE và các nghĩa vụ đạo đức