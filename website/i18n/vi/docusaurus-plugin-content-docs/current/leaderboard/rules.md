---
sidebar_position: 1
title: "Đánh giá dịch máy"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "How the composite score is computed"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Evaluation Datasets"
    to: /docs/leaderboard/datasets
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "The rules, applied"
---
# Đánh giá Dịch máy

> **Tóm tắt tổng quan.** Trang này xác định các tiêu chí gửi bài lên bảng xếp hạng (leaderboard), các chỉ số chấm điểm (chrF++, FST acceptance, exact match, equivalent match, semantic score), chính sách chống gian lận, các cấp độ xác minh và quy trình gửi bài. Các phương pháp đã tiếp xúc với dữ liệu đánh giá sẽ bị loại.

champollion bao gồm một khung đánh giá dịch máy được thiết kế để **đánh giá hiệu năng có thể tái lập (reproducible benchmarking)** của các phương pháp dịch thuật — đặc biệt là đối với các ngôn ngữ ít tài nguyên và ngôn ngữ bản địa, nơi các bộ dữ liệu chuẩn (benchmark) MT tiêu chuẩn không tồn tại và các tuyên bố về chất lượng rất khó xác minh.

---

## Bảng xếp hạng

Trọng tâm của hệ thống là **[Bảng xếp hạng Phương pháp](https://champollion.dev/leaderboard)** — một bảng điểm trực tiếp, được hỗ trợ bởi Supabase, nơi các nhà nghiên cứu và thành viên cộng đồng gửi và so sánh các phương pháp dịch thuật với quy trình đánh giá có dấu vân tay (fingerprinted) và có thể tái lập.

Mỗi lượt gửi bao gồm:

- **Pipeline có dấu vân tay (Fingerprinted pipeline)** — được liên kết với một commit Git và mã băm cấu hình (config hash) cụ thể, giúp truy xuất kết quả về chính xác mã nguồn đã tạo ra chúng
- **Tập dữ liệu được đánh phiên bản (Versioned dataset)** — được băm nội dung (content-hashed) và đánh phiên bản; điểm số chỉ có thể so sánh được trong cùng một phiên bản tập dữ liệu
- **Các chỉ số chuẩn hóa (Standardised metrics)** — tất cả việc chấm điểm đều được tính toán bởi bộ công cụ đánh giá chung (evaluation harness), loại bỏ sự khác biệt về cách triển khai
- **Cấp độ tin cậy (Trust tiers)** — tự đánh giá (self-benchmarked), GDS Verified (Được xác minh bởi GDS), hoặc Community Validated (Được cộng đồng xác thực)
- **Theo dõi chi phí (Cost tracking)** — chi phí API cho mỗi lượt gửi, giúp minh bạch hóa sự đánh đổi giữa chi phí và chất lượng

Bảng xếp hạng hiện theo dõi năm chỉ số. Ba chỉ số hoạt động với mọi ngôn ngữ; hai chỉ số khả dụng cho tiếng Plains Cree và sẽ được tổng quát hóa khi chúng tôi mở rộng:

| Chỉ số | Loại | Ý nghĩa đo lường |
|--------|------|------------------|
| **chrF++** | F-score của n-gram ký tự | Chỉ số chất lượng chính — tương quan tốt với đánh giá của con người, đặc biệt đối với các ngôn ngữ phong phú về hình thái |
| **Exact Match** | Tỷ lệ khớp hoàn hảo | Độ chính xác nghiêm ngặt — tần suất bản dịch khớp hoàn toàn với bản dịch chuẩn (gold standard)? |
| **FST Acceptance** | Tỷ lệ vượt qua rào cản hình thái | Đối với các phương pháp có xác minh bằng bộ chuyển đổi trạng thái hữu hạn (finite-state transducer - FST) — tỷ lệ đầu ra hợp lệ về mặt hình thái là bao nhiêu? |
| **Equivalent Match** | Tỷ lệ biến thể chấp nhận được | Tỷ lệ khớp với bản tham chiếu hoặc một biến thể chấp nhận được (trật tự từ, quy ước chính tả). Hiện tại hỗ trợ CRK; đang tổng quát hóa. |
| **Semantic Score** | Độ trung thực về ngữ nghĩa | Khả năng bảo toàn ý nghĩa — bản dịch có nắm bắt được ý nghĩa dự định bất kể hình thức bề mặt hay không? Hiện tại hỗ trợ CRK; đang tổng quát hóa. |

:::info Bộ chỉ số đầy đủ
[Tài liệu đặc tả chấm điểm (Scoring Specification)](/docs/specifications/scoring) định nghĩa danh mục đầy đủ gồm 19 chỉ số thuộc 5 danh mục, công thức tính composite score (điểm tổng hợp), bảng trọng số và các ngưỡng cấp độ chất lượng.
:::

**[→ Xem bảng xếp hạng](https://champollion.dev/leaderboard)**

---

## Các tập dữ liệu hiện có

### Tập phát triển EDTeKLA v1

Tập dữ liệu đánh giá đầu tiên, được xây dựng cho tác vụ dịch English→Plains Cree (SRO). Được tạo bởi [nhóm nghiên cứu EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) tại Đại học Alberta.

| Thuộc tính | Giá trị |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Cặp ngôn ngữ** | EN → CRK (Plains Cree, chính tả SRO) |
| **Số lượng mục** | 404 (`master_corpus.json`: 62 gold + 342 textbook); tổng cộng 548 mục hiện có |
| **Giấy phép** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| **Nguồn gốc** | `gold_standard` (được xác minh bởi người bản xứ), `textbook` (tài liệu giáo dục đã xuất bản) |

### FLORES+ Devtest — Chỉ dùng cho mục đích phát triển

> [!WARNING]
> **FLORES+ khả dụng cho việc phát triển và gỡ lỗi nhưng KHÔNG được sử dụng để đánh giá trên bảng xếp hạng chính thức.** FLORES+ (ban đầu là Meta FLORES-200) là một tập dữ liệu chuẩn (benchmark) công khai rộng rãi mà các LLM tiên tiến gần như chắc chắn đã được huấn luyện trên đó. Điểm số đối với FLORES+ không phản ánh đáng tin cậy chất lượng dịch thuật thực tế của các phương pháp dựa trên LLM. Các phương pháp không dùng LLM (FST, dựa trên luật, NMT được tinh chỉnh) ít bị ảnh hưởng hơn nhưng điểm FLORES+ vẫn không được công bố trên bảng xếp hạng.

Các fixture của FLORES+ vẫn khả dụng trong `test/benchmark/fixtures/` để kiểm thử nhanh pipeline (smoke testing), xác thực chéo ngôn ngữ và sử dụng trong quá trình phát triển. Đánh giá chính thức sử dụng các ngữ liệu tùy chỉnh được xây dựng từ văn bản do con người viết, không được công khai dưới dạng song ngữ.

Xem [Tập dữ liệu đánh giá (Evaluation Datasets)](/docs/leaderboard/datasets) để biết lược đồ tập dữ liệu đầy đủ, các cấp độ khó và cách tạo tập dữ liệu của riêng bạn.

:::danger KHÔNG HUẤN LUYỆN trên dữ liệu đánh giá

**Các tập dữ liệu này chỉ dành cho mục đích đánh giá.** Các phương pháp được huấn luyện, tinh chỉnh (fine-tune), gợi ý vài ví dụ (few-shot-prompted) hoặc tiếp xúc với dữ liệu đánh giá bằng bất kỳ cách nào khác sẽ tạo ra điểm số cao một cách nhân tạo và sẽ bị **loại khỏi bảng xếp hạng.**

Đây không phải là một gợi ý — đây là quy tắc quan trọng nhất để đảm bảo tính trung thực của việc đánh giá. Hãy sử dụng các ngữ liệu riêng biệt để huấn luyện. Các tập đánh giá phải hoàn toàn mới lạ (unseen) đối với mô hình của bạn trong quá trình phát triển.

Nếu bạn đang sử dụng dữ liệu hướng dẫn (coaching data) hoặc các ví dụ few-shot, chúng phải đến từ **các nguồn hoàn toàn tách biệt**. Nếu còn nghi ngờ, đừng đưa chúng vào.
:::

:::warning Tính không xác định của LLM (LLM non-determinism)

Đầu ra của LLM có tính không xác định (non-deterministic). Điểm số thể hiện các phép đo tại một thời điểm cụ thể dưới các phiên bản mô hình và cấu hình API nhất định. Các nhà cung cấp mô hình có thể cập nhật trọng số, chiến lược giải mã hoặc bộ lọc an toàn bất kỳ lúc nào, điều này có thể gây ra sự lệch điểm số (score drift) giữa các lần chạy. Bảng xếp hạng ghi lại chính xác mã định danh mô hình (model slug) và mốc thời gian cho mỗi lượt gửi.
:::

---

## Thế nào là một phương pháp tốt

Không phải mọi phương pháp đều được tạo ra như nhau. Dưới đây là những điểm khác biệt giữa một công trình nghiên cứu nghiêm túc và những điểm số bị thổi phồng.

### Đặc điểm của một phương pháp mạnh

- **Sự phân tách rõ ràng giữa dữ liệu huấn luyện và dữ liệu đánh giá** — phương pháp của bạn chưa từng tiếp xúc với tập đánh giá trong quá trình phát triển, tinh chỉnh, thiết kế prompt (prompt engineering) hoặc lựa chọn ví dụ few-shot
- **Có thể tái lập (Reproducible)** — người khác có thể clone kho lưu trữ (repo) của bạn, chạy bộ công cụ đánh giá (harness) và nhận được điểm số tương tự (trong giới hạn tính không xác định của LLM)
- **Được ghi chép đầy đủ** — [thẻ phương pháp (method card)](/docs/specifications/methods) của bạn mô tả phương pháp của bạn làm gì, sử dụng những công cụ nào và các hạn chế của nó là gì
- **Trung thực về phạm vi** — nếu phương pháp của bạn chỉ hoạt động cho một cặp ngôn ngữ, hãy nêu rõ; nếu nó bị giảm hiệu năng trên một số cấu trúc hình thái nhất định, hãy ghi chép lại điều đó
- **Nhận thức về cộng đồng** — đối với các ngôn ngữ bản địa, phương pháp của bạn tôn trọng chủ quyền dữ liệu. Bạn đã tham vấn các cộng đồng ngôn ngữ hoặc chỉ sử dụng dữ liệu có giấy phép mở

### Các dấu hiệu cảnh báo (những gì sẽ bị loại)

| Dấu hiệu cảnh báo | Lý do là vấn đề |
|----------|--------------------|
| Huấn luyện trên dữ liệu đánh giá | Làm mất hoàn toàn mục đích của việc đánh giá. Điểm số bị thổi phồng sẽ gây hiểu lầm cho mọi người. |
| Lựa chọn kết quả tốt nhất (Cherry-picking) | Chạy 10 lần và chỉ gửi lượt chạy tốt nhất mà không công khai các lượt chạy khác |
| Hậu xử lý không công khai | Sửa đổi đầu ra bằng thủ công trước khi chấm điểm |
| Dữ liệu hướng dẫn bị ô nhiễm | Sử dụng các ví dụ từ tập đánh giá làm prompt few-shot hoặc mục từ điển |
| Tuyên bố sẵn sàng thương mại hóa mà không có nguồn gốc rõ ràng | Nếu phương pháp của bạn sử dụng dữ liệu CC BY-NC-SA data, nó không sẵn sàng để thương mại hóa |

### Các cấp độ xác minh

Các cấp độ xác minh mô tả **ai là người đã xác thực kết quả** — tách biệt với các cấp độ chất lượng (Baseline → Fluent) được định nghĩa trong [Tài liệu đặc tả chấm điểm, §5 (Scoring Specification, §5)](/docs/specifications/scoring#5-quality-tiers), vốn mô tả ý nghĩa của composite score tự động.

| Cấp độ | Ý nghĩa | Cách đạt được |
|------|---------|--------------|
| **Self-benchmarked** | Bạn tự chạy bộ công cụ đánh giá và gửi kết quả | Mở một PR với run card của bạn |
| **GDS Verified** | Đội ngũ duy trì champollion đã tái lập kết quả của bạn | Gửi phương pháp của bạn dưới dạng một plugin có thể cài đặt |
| **Community Validated** | Tổ chức quản trị đã chạy đánh giá dựa trên bản dịch chuẩn + đánh giá từ cộng đồng | Gửi mã nguồn phương pháp cho tổ chức quản trị |

---

## Cách gửi bài

1. **Xây dựng phương pháp của bạn** — xem [Xây dựng phương pháp (Building a Method)](/docs/specifications/methods) để biết giao diện phương pháp
2. **Chạy bộ công cụ đánh giá** — xem [Bộ công cụ đánh giá (Eval Harness)](/docs/specifications/harness) để biết cách thiết lập và sử dụng
3. **Tạo run card** — bộ công cụ đánh giá sẽ tạo ra một run card định dạng JSON chứa điểm số, dấu vân tay và siêu dữ liệu của bạn
4. **Mở một PR** — gửi run card của bạn đến [kho lưu trữ bộ công cụ đánh giá (eval harness repository)](https://github.com/gamedaysuits/arena)
5. **Xuất hiện trên bảng xếp hạng** — sau khi được hợp nhất (merge), kết quả của bạn sẽ xuất hiện trên [Bảng xếp hạng Phương pháp](https://champollion.dev/leaderboard)

---

## Định hướng tương lai

- **Các lượt chạy so sánh mô hình toàn diện** — đánh giá hệ thống các mô hình tiên tiến (GPT-4o, Claude, Gemini, v.v.) trên các ngôn ngữ của champollion bằng cách sử dụng các ngữ liệu đánh giá tùy chỉnh (không phải các bộ dữ liệu chuẩn công khai)
- **Nhiều cặp ngôn ngữ hơn** — tiếng Quechua, tiếng Inuktitut và các ngôn ngữ ít tài nguyên khác khi các tập dữ liệu được cộng đồng xác minh khả dụng
- **Nhập tập dữ liệu (Dataset import)** — bộ công cụ để chuyển đổi các tập dữ liệu đánh giá bên ngoài (WMT, Tatoeba, v.v.) sang định dạng đánh giá của champollion
- **Tự động chạy lại (Automated re-runs)** — phát hiện các thay đổi phiên bản mô hình và chạy lại các bài đánh giá hiệu năng để theo dõi sự lệch điểm số

---

## Xem thêm

- **[Bảng xếp hạng Phương pháp (Method Leaderboard)](https://champollion.dev/leaderboard)** — điểm số trực tiếp và các lượt gửi
- **[Bộ công cụ đánh giá (Eval Harness)](/docs/specifications/harness)** — cách chạy đánh giá
- **[Tập dữ liệu đánh giá (Evaluation Datasets)](/docs/leaderboard/datasets)** — định dạng tập dữ liệu và các tập dữ liệu hiện có
- **[Xây dựng phương pháp (Building a Method)](/docs/specifications/methods)** — đặc tả giao diện phương pháp
- **[Đặc tả Run Card (Run Card Specification)](/docs/specifications/run-card)** — schema JSON của run card
- **[Đặc tả Benchmark (Benchmark Specification)](/docs/specifications/benchmark)** — giao thức đánh giá, định dạng ngữ liệu, chủ quyền
- **[Tài liệu đặc tả chấm điểm (Scoring Specification)](/docs/specifications/scoring)** — SSOT (nguồn chân lý duy nhất) cho các chỉ số, trọng số tổng hợp và các cấp độ chất lượng