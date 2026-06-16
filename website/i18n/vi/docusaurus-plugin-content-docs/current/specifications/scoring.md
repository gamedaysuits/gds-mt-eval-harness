---
sidebar_position: 5
title: "Đặc tả tính điểm"
slug: '/specifications/scoring'
related:
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
    note: "When a score difference actually means something"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
    note: "The tool that computes these metrics"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "These scores, live"
---
# Đặc tả Chấm điểm

> **Tóm tắt Tổng quan.** Đây là nguồn thông tin chính xác duy nhất cho tất cả các số đo đánh giá, điểm số tổng hợp (composite score), các phân bậc chất lượng, và phân tích chi phí trong hệ sinh thái đánh giá dịch máy (MT) Champollion. Các số đo đánh giá đặc thù theo ngôn ngữ — tính hợp lệ về hình thái FST, các lớp tương đương linter, và xác thực ngữ nghĩa tất định — được gọi chung là **LYSS** (Linguistically-informed Yield & Structural Scoring). Mọi số đo được tính toán bởi khung thử nghiệm (harness), mọi trọng số trong công thức tổng hợp, và mọi ngưỡng phân bậc đều được định nghĩa tại đây — và chỉ tại đây. Mã nguồn, tài liệu hướng dẫn, và lược đồ cơ sở dữ liệu đều được xây dựng dựa trên tài liệu này. Khi có sự xung đột, tài liệu này sẽ là căn cứ có thẩm quyền cao nhất.
>
> **Phạm vi.** Tài liệu này định nghĩa chúng tôi đo lường *cái gì* và *chấm điểm như thế nào*. Nó không định nghĩa lược đồ run card (xem BENCHMARK_SPEC §3), giao thức benchmark (BENCHMARK_SPEC §6), hay các quy tắc của bảng xếp hạng (leaderboard) (xem tài liệu về arena). Các tài liệu đó sẽ tham chiếu đến tài liệu này để lấy định nghĩa số đo và logic chấm điểm.
>
> Cập nhật lần cuối: 2026-06-07

---

## 1. Triết lý Chấm điểm

### 1.1 Triết lý Đánh giá Vi mô (Microeval)

> *"Nếu chúng ta chỉ tập trung vào những gì có tính khái quát hóa, chúng ta chắc chắn sẽ lãng quên những nơi mà nó không thể áp dụng — và đánh mất đi các ngôn ngữ này cùng toàn bộ tri thức và trí tuệ của chúng."*

Dự án này thực hành **phát triển đánh giá vi mô (microeval)**: xây dựng các số đo đánh giá được thiết kế riêng cho từng ngôn ngữ cụ thể bằng cách sử dụng các công cụ ngôn ngữ tốt nhất hiện có — bộ chuyển đổi trạng thái hữu hạn (FST), từ điển song ngữ, bộ phân tích hình thái, và các quy tắc tương đương do các nhà ngôn ngữ học tuyển chọn. Điều này trái ngược với mô hình thống trị trong đánh giá dịch máy (MT), vốn tìm kiếm các số đo phổ quát hoạt động trên tất cả các ngôn ngữ. Các số đo phổ quát rất có giá trị, nhưng chúng lại yếu nhất ở chính những nơi cần chúng nhất: đối với các ngôn ngữ có hình thái phức tạp, dữ liệu huấn luyện hạn chế, và không có sự hiện diện trong các tập dữ liệu huấn luyện số đo mạng neural.

Chúng tôi không đạt được tiến bộ trong dịch máy cho nhiều ngôn ngữ trên thế giới không chỉ vì thiếu ngữ liệu (corpora), mà còn vì **chúng ta thậm chí không biết tiến bộ trông như thế nào** — chúng ta thiếu các công cụ đánh giá tự động để đo lường xem một hệ thống dịch thuật có đang cải thiện hay không. LYSS là nỗ lực của chúng tôi nhằm xây dựng các công cụ đó, cho từng ngôn ngữ một, bằng cách sử dụng bất kỳ tài nguyên ngôn ngữ nào hiện có.

### 1.2 Các Số đo Tự động Chỉ là Đại diện (Proxies)

Mọi số đo được định nghĩa ở đây đều được tính toán bằng máy. Chúng hữu ích cho việc lặp nhanh (rapid iteration), so sánh có hệ thống, và phát hiện sự suy giảm chất lượng (regressions). Chúng **không thể thay thế cho đánh giá của con người**. Các phân bậc chất lượng trong §5 là các nhãn phỏng đoán (heuristic) — chỉ có sự đánh giá của con người mới có thể xác nhận khả năng sử dụng thực tế.

### 1.3 Thiết kế Đa Tín hiệu

Không có một số đo đơn lẻ nào có thể nắm bắt trọn vẹn chất lượng dịch thuật. Một bản dịch có thể có độ trùng khớp chrF++ hoàn hảo nhưng lại thất bại trong việc xác thực hình thái. Nó có thể vượt qua các kiểm tra FST nhưng lại mang sai ý nghĩa. Nó có thể chính xác về mặt ngữ nghĩa nhưng lại xa lạ về mặt phong cách đối với ngôn ngữ đích. Điểm số tổng hợp (composite score) trong §4 tổng hợp nhiều tín hiệu độc lập, mỗi tín hiệu nắm bắt một khía cạnh chất lượng khác nhau.

### 1.4 Khả năng Mở rộng

Danh mục số đo này không khép kín. Các ngôn ngữ mới mang lại những yêu cầu mới: độ chính xác của thanh điệu đối với các ngôn ngữ có thanh điệu, độ chính xác của dấu phụ đối với chữ viết Semit, tính chính xác của bảng âm tiết đối với tiếng Cree. Kiến trúc (giao thức MetricPlugin, điểm số tổng hợp có trọng số với tính năng tái chuẩn hóa) được thiết kế để có thể thêm các số đo mới mà không làm ảnh hưởng đến các điểm số hiện tại. Các số đo đặc thù theo ngôn ngữ (ví dụ: linter và bộ xác thực ngữ nghĩa của CRK) được khai báo trên các thẻ ngôn ngữ (language cards) dưới mục `evalMetrics` và được tải từ `eval_standards/` — khung thử nghiệm đi kèm chỉ chứa các số đo hành vi chung (chuyển mã ngôn ngữ, ảo tưởng, thuật ngữ).

### 1.5 Ba Khía cạnh Đánh giá

Mỗi run card đo lường ba khía cạnh độc lập:

```
Quality   — How good is the translation?   (composite score, §4)
Cost      — How much does it cost?          (cost metrics, §6)
Speed     — How fast does it run?           (speed metrics, §7)
```

Đây là các trục độc lập. Một phương pháp có thể có chất lượng cao nhưng đắt đỏ, nhanh nhưng không chính xác, hoặc bất kỳ sự kết hợp nào khác. Bảng xếp hạng cho phép sắp xếp theo bất kỳ khía cạnh nào. Điểm số điều chỉnh theo chi phí (§6.3) là số đo duy nhất kết hợp các khía cạnh này.

### 1.6 Trạng thái Xác thực

Mọi số đo trong đặc tả này đều có một **trạng thái xác thực** khác biệt với trạng thái triển khai của nó (§3). Trạng thái triển khai theo dõi xem mã nguồn đã tồn tại hay chưa. Trạng thái xác thực theo dõi xem số đo đó đã được chứng minh là tương quan với các đánh giá chất lượng của con người hay chưa.

| Mức độ Xác thực | Ý nghĩa | Các Số đo Hiện tại |
|------------------|---------|----------------|
| **✅ Đã được xác thực bên ngoài** | Đã có các nghiên cứu tương quan với con người được công bố (WMT, các bài báo học thuật) | `chrf_plus_plus`, `bleu`, `comet_score` |
| **⚡ Xác thực gián tiếp (Proxy-validated)** | Đã được xác thực cho các ngôn ngữ giàu tài nguyên; chưa được xác thực cho các ngôn ngữ ít tài nguyên (LRL) mục tiêu của chúng tôi | `comet_score` (đã xác thực cho các cặp ngôn ngữ EU, chưa xác thực cho CRK) |
| **🔶 Phỏng đoán kỹ thuật (Engineering heuristic)** | Được thiết kế từ các nguyên lý ngôn ngữ học hoặc các dạng lỗi quan sát được; chưa có dữ liệu tương quan với con người | `fst_acceptance_rate`, `equivalent_match_rate`, `semantic_score`, `code_switching_rate`, `hallucination_rate`, `terminology_adherence` |
| **🔲 Chưa được xác thực** | Chưa được thử nghiệm trên bất kỳ dữ liệu nào | `morphological_accuracy`, `orthographic_accuracy`, `consistency_score` |

> **Ý nghĩa thực tế.** Điểm số tổng hợp (§4) gộp các số đo ở tất cả các mức độ xác thực. Đây là một lựa chọn thiết kế có chủ ý: chúng tôi tin rằng một phỏng đoán kỹ thuật dựa trên cấu trúc (sự chấp nhận của FST) sẽ cung cấp nhiều thông tin hơn cho các ngôn ngữ đa tổng hợp so với một số đo mạng neural chỉ được xác thực trên các cặp ngôn ngữ châu Âu (COMET). Nhưng chúng tôi chưa chứng minh được điều này. Điểm số tổng hợp nên được coi là một **ước tính kỹ thuật**, chứ không phải là một phép đo chất lượng đã được xác thực, cho đến khi các nghiên cứu tương quan với con người được hoàn thành cho từng ngôn ngữ mục tiêu.
>
> **Các thực nghiệm xác thực bắt buộc** (xem `mt-evaluation-landscape.md` §6 và `speaker-validation.md`):
> 1. Nghiên cứu tương quan đánh giá của con người: hơn 200 cặp câu được đánh giá bởi ít nhất 3 người nói song ngữ
> 2. Đo lường tỷ lệ từ chối sai (false rejection rate) của FST trên một ngữ liệu đại diện
> 3. Chuyển đổi sang ngôn ngữ thứ hai (tiếng North Sámi) để kiểm tra khả năng khái quát hóa
> 4. So sánh trực tiếp với COMET trên cùng một dữ liệu

---

## 2. Danh mục Số đo {#2-metric-inventory}

Các số đo được tổ chức thành bốn danh mục. Mỗi số đo có một trạng thái triển khai, thang đo, và cấp độ (theo từng mục - per-entry, cấp độ ngữ liệu - corpus-level, hoặc cả hai).

### 2.1 Số đo Bề mặt

Các số đo bề mặt so sánh bản dịch dự đoán với bản dịch tham chiếu ở cấp độ chuỗi ký tự. Chúng không yêu cầu công cụ ngôn ngữ nào — chỉ đơn thuần là so sánh chuỗi.

| ID | Số đo | Trạng thái | Thang đo | Cấp độ | Triển khai |
|----|--------|--------|-------|-------|---------------|
| `exact_match_rate` | Exact Match | ✅ Đã triển khai | 0.0–1.0 | Cả hai | Nhị phân: bản dịch dự đoán có trùng khớp hoàn toàn (==) với bản dịch tham chiếu không? Tỷ lệ ngữ liệu = số trùng khớp / tổng số. |
| `equivalent_match_rate` | Equivalent Match | ⚡ Một phần | 0.0–1.0 | Cả hai | Đầu ra dự đoán có khớp với bất kỳ biến thể nào được chấp nhận không? Đối với CRK: được triển khai thông qua `CrkLinterMetric` của tiêu chuẩn đánh giá CRK (trong `eval_standards/crk/`) bằng cách sử dụng các quy tắc lớp biến thể tất định (trật tự từ, chính tả, tiểu từ tùy chọn, từ đồng nghĩa của từ căn - lemma synonym, tính mơ hồ tiếp diễn - progressive ambiguity). Được tải tự động thông qua khai báo `evalMetrics` của thẻ ngôn ngữ CRK. Việc triển khai chung giữa các ngôn ngữ yêu cầu `variants[]` theo từng mục trong ngữ liệu. |
| `chrf_plus_plus` | chrF++ | ✅ Đã triển khai | 0–100 | Cả hai | Điểm F-score của n-gram ký tự (sacrebleu). Kháng lỗi tốt với các biến thể hình thái. Số đo bề mặt chính cho các ngôn ngữ chắp dính/đa tổng hợp. Cấp độ từng mục sử dụng `sentence_chrf`; cấp độ ngữ liệu sử dụng `corpus_chrf`. |
| `bleu` | BLEU | ✅ Đã triển khai | 0–100 | Ngữ liệu | Độ chính xác n-gram cấp độ từ (sacrebleu). **Bị loại trừ khỏi điểm số tổng hợp** — việc chấm điểm ở cấp độ từ sẽ phạt các biến thể hình thái một cách không công bằng. Được tính toán và báo cáo để tương thích với các tài liệu nghiên cứu MT. |
| `ter` | Translation Edit Rate | ✅ Đã triển khai | 0–∞ (thấp hơn là tốt hơn) | Cả hai | Khoảng cách chỉnh sửa tối thiểu giữa bản dịch dự đoán và bản dịch tham chiếu, được chuẩn hóa theo độ dài của bản dịch tham chiếu (sacrebleu `corpus_ter`). Được tính toán cùng với chrF++ và BLEU. Bị loại trừ khỏi điểm số tổng hợp — do tương quan với chrF++ nên việc đưa cả hai vào sẽ tính trùng lặp độ tương đồng bề mặt. |
| `length_ratio` | Length Ratio | ✅ Đã triển khai | 0–∞ (1.0 là lý tưởng) | Cả hai | `len(predicted) / len(reference)` tính bằng ký tự. Phát hiện việc bị cắt ngắn (<0.5) và phóng đại/ảo tưởng (>2.0). Được tính trung bình trên các mục ở cấp độ ngữ liệu. |

### 2.2 Số đo Cấu trúc

Các số đo cấu trúc xác thực tính chuẩn xác về mặt ngôn ngữ của bản dịch. Chúng yêu cầu các công cụ đặc thù theo ngôn ngữ (bộ phân tích FST, bộ phân tích cú pháp hình thái) và là những tín hiệu mạnh mẽ nhất đối với các ngôn ngữ giàu hình thái.

| ID | Số đo | Trạng thái | Thang đo | Cấp độ | Triển khai |
|----|--------|--------|-------|-------|---------------|
| `fst_acceptance_rate` | FST Acceptance | ✅ Đã triển khai | 0.0–1.0 | Cả hai | Tỷ lệ các từ đầu ra được chấp nhận bởi bộ chuyển đổi trạng thái hữu hạn (GiellaLT). Một từ được coi là "hợp lệ" nếu FST trả về ít nhất một phân tích hình thái. Khả dụng cho bất kỳ ngôn ngữ nào có bộ phân tích `.hfstol` của GiellaLT. |
| `morphological_accuracy` | Morphological Accuracy | 🔲 Đã lên kế hoạch | 0.0–1.0 | Cả hai | Một từ có thể hợp lệ về mặt FST nhưng lại có biến hình sai (đúng từ căn, sai hậu tố). Số đo này so sánh phân tích FST của từ dự đoán với các đặc trưng hình thái mong đợi. Yêu cầu các chú thích hình thái theo từng mục trong ngữ liệu. |
| `orthographic_accuracy` | Orthographic Accuracy | 🔲 Đã lên kế hoạch | 0.0–1.0 | Cả hai | Xác thực tính chính xác đặc thù của chữ viết: cách sử dụng dấu macron/circumflex trong SRO cho tiếng Cree, các dấu phụ cho tiếng Inuktitut, các ký hiệu độ dài nguyên âm cho tiếng Ojibwe. Các bộ quy tắc theo từng ngôn ngữ. |

> **Tại sao các số đo cấu trúc lại quan trọng.** Hệ thống OMT-1600 của Meta — hệ thống dịch máy lớn nhất từng được công bố (1.600 ngôn ngữ) — đánh giá bằng ChrF++, xCOMET, MetricX, và BLASER 3. Không có công cụ nào trong số này xác thực tính chính xác về mặt hình thái. ChrF++ đo lường mức độ trùng khớp n-gram ký tự: nó thưởng cho các chuỗi ký tự trông *có vẻ* giống với ngôn ngữ đích. Đối với các ngôn ngữ đa tổng hợp, điều này có nghĩa là một từ không hợp lệ về mặt hình thái nhưng chia sẻ nhiều ký tự với bản dịch tham chiếu vẫn đạt điểm cao. Số đo FST acceptance của chúng tôi là một bài kiểm tra cấu trúc nhị phân: từ đó hoặc là một dạng hợp lệ trong ngôn ngữ, hoặc là không. Không có khung đánh giá dịch máy nào khác cung cấp tính năng này ở quy mô lớn.

### 2.3 Số đo Ngữ nghĩa

Các số đo ngữ nghĩa đo lường mức độ bảo toàn ý nghĩa bằng cách sử dụng các vector nhúng (embeddings) hoặc các mô hình đã được huấn luyện. Chúng phát hiện các bản dịch khác nhau về mặt bề mặt nhưng tương đương về mặt ý nghĩa, đồng thời gắn cờ các bản dịch tương đồng về mặt bề mặt nhưng sai lệch về mặt ngữ nghĩa.

| ID | Số đo | Trạng thái | Thang đo | Cấp độ | Triển khai |
|----|--------|--------|-------|-------|---------------|
| `semantic_score` | Semantic Similarity | ⚡ Một phần | 0.0–1.0 | Cả hai | CRK: điểm số được tính trọng số theo phán quyết từ `CrkSemanticMetric` của tiêu chuẩn đánh giá CRK (trong `eval_standards/crk/`, proxy). Phổ quát: độ tương đồng cosine của các vector nhúng câu (nguồn + dự đoán so với nguồn + tham chiếu). Mô hình sẽ được quyết định sau (TBD) — phải hỗ trợ các ngôn ngữ ít tài nguyên, điều này loại bỏ hầu hết các mô hình nhúng tập trung vào tiếng Anh. |
| `comet_score` | COMET | ✅ Đã triển khai | ~0.0–1.0 | Cả hai | Số đo đánh giá dịch máy dạng học máy (Unbabel). Được huấn luyện trên các đánh giá chất lượng của con người. **Bị loại trừ khỏi điểm số tổng hợp** — dữ liệu huấn luyện bị thiên vị về các ngôn ngữ châu Âu giàu tài nguyên; điểm số cho các ngôn ngữ ít tài nguyên (LRL) là không đáng tin cậy. Được tính toán khi `unbabel-comet` được cài đặt. Được báo cáo kèm theo cờ cảnh báo ngôn ngữ ít tài nguyên. Đối với 35 ngôn ngữ châu Phi, khung thử nghiệm tự động chọn AfriCOMET (`masakhane/africomet-mtl`) thông qua `resolve_comet_model()`, vốn có độ tương quan tốt hơn với đánh giá của con người đối với các ngôn ngữ đó. |

> **Tại sao COMET bị loại trừ khỏi điểm số tổng hợp.** COMET được huấn luyện trên dữ liệu đánh giá của con người từ WMT, vốn chủ yếu là các cặp ngôn ngữ châu Âu giàu tài nguyên. Khi áp dụng cho tiếng Plains Cree hoặc các ngôn ngữ ít tài nguyên (LRL) khác, các biểu diễn nội bộ của mô hình không hề được tiếp xúc với các ngôn ngữ đó — nó đang ngoại suy từ các ngôn ngữ có hệ thống hình thái hoàn toàn khác biệt. Các điểm số này vẫn hữu ích về mặt định hướng (COMET cao hơn ≈ đầu ra nghe trôi chảy hơn nói chung) nhưng các giá trị tuyệt đối không được hiệu chuẩn. Chúng tôi báo cáo COMET để đảm bảo tính minh bạch nhưng không để nó ảnh hưởng đến điểm số tổng hợp cho đến khi chúng tôi có thể xác thực nó so với các đánh giá của con người cho từng ngôn ngữ mục tiêu.

> **AfriCOMET cho các ngôn ngữ châu Phi.** Mỗi thẻ ngôn ngữ có một trường `metricModelSupport` (xem đặc tả thẻ ngôn ngữ §9) khai báo mô hình COMET chuyên biệt nào được huấn luyện cho ngôn ngữ đó. Đối với 35 ngôn ngữ châu Phi (yor, hau, ibo, amh, swa, v.v.), thẻ này khai báo AfriCOMET (`masakhane/africomet-mtl`) — một mô hình COMET được tinh chỉnh trên các đánh giá dịch máy của con người đối với các ngôn ngữ châu Phi bởi cộng đồng Masakhane. Khung thử nghiệm tự động chọn mô hình được khuyến nghị thông qua `resolve_comet_model()` đọc từ các thẻ ngôn ngữ, nhưng điều này có thể được ghi đè bằng `--comet-model`. Việc thêm các ánh xạ ngôn ngữ→mô hình mới được thực hiện bằng cách làm phong phú thẻ ngôn ngữ (không phải chỉnh sửa mã nguồn Python).

### 2.4 Số đo Hành vi

Các số đo hành vi phát hiện các dạng lỗi cụ thể trong đầu ra dịch thuật. Chúng không đo lường trực tiếp chất lượng — chúng phát hiện các vấn đề.

| ID | Số đo | Trạng thái | Thang đo | Cấp độ | Triển khai |
|----|--------|--------|-------|-------|---------------|
| `code_switching_rate` | Code-Switching Rate | ✅ Đã triển khai | 0.0–1.0 (thấp hơn là tốt hơn) | Cả hai | Tỷ lệ các từ đầu ra nằm ở ngôn ngữ nguồn (thường là tiếng Anh). Được phát hiện thông qua phân tích hệ chữ viết Unicode và/hoặc danh sách từ của ngôn ngữ nguồn. Dạng lỗi rất phổ biến của LLM: mô hình chèn các từ tiếng Anh khi nó không biết từ tương đương trong ngôn ngữ đích. |
| `hallucination_rate` | Hallucination Rate | ✅ Đã triển khai | 0.0–1.0 (thấp hơn là tốt hơn) | Cả hai | Tỷ lệ nội dung đầu ra không có nội dung tương ứng ở nguồn. Được phát hiện thông qua căn chỉnh từ (word alignment) hoặc độ trùng khớp vector nhúng xuyên ngôn ngữ. Phát hiện việc mô hình tạo ra các bản dịch nghe có vẻ hợp lý nhưng thực chất là bịa đặt. |
| `terminology_adherence` | Terminology Adherence | ✅ Đã triển khai | 0.0–1.0 | Cả hai | Đối với các phương pháp có hướng dẫn (coached): tỷ lệ các thuật ngữ được quy định xuất hiện trong đầu ra. Yêu cầu dữ liệu từ điển hướng dẫn. Đo lường xem mô hình có tôn trọng từ vựng do chuyên gia cung cấp hay không. |
| `consistency_score` | Cross-Entry Consistency | 🔲 Đã lên kế hoạch | 0.0–1.0 | Chỉ ngữ liệu | Mô hình có dịch cùng một thuật ngữ nguồn theo cùng một cách trên các mục khác nhau không? Tính nhất quán thấp gợi ý rằng mô hình đang đoán mò thay vì áp dụng các mẫu đã học. Yêu cầu các thuật ngữ lặp lại giữa các mục trong ngữ liệu. |

### 2.5 Số đo Tuân thủ

Các số đo tuân thủ xác thực rằng các bản dịch bảo toàn tính toàn vẹn cấu trúc — các trình giữ chỗ (placeholders), định dạng, và các quy ước trình bày. Chúng là các bước kiểm tra cổng chất lượng (quality-gate checks), chứ không phải điểm số chất lượng.

| ID | Số đo | Trạng thái | Thang đo | Cấp độ | Triển khai |
|----|--------|--------|-------|-------|---------------|
| `compliance_index` | Double-Pass Compliance | ✅ Đã triển khai | 0.0–1.0 | Cả hai | Điểm tổng hợp có trọng số: 60% tính toàn vẹn của biến (các biến `{placeholder}` có được bảo toàn không?) + 20% tính tuân thủ dấu ngoặc kép (đúng ký tự ngoặc kép theo thẻ ngôn ngữ) + 20% tính tuân thủ chữ hoa-chữ thường (không rò rỉ chữ cái Latinh đối với các ngôn ngữ không phân biệt chữ hoa-chữ thường). Được tính toán trên cả đầu ra thô và đầu ra sau xử lý. Thông qua `DoublePassCompliancePlugin`. |
| `repair_effectiveness` | Repair Effectiveness | ✅ Đã triển khai | 0.0–1.0 | Ngữ liệu | Tỷ lệ các vi phạm tuân thủ đã được tự động sửa chữa bởi các hook sau dịch thuật. Đo lường mức độ cải thiện của đầu ra thô nhờ vào cổng chất lượng. |

> **Tại sao tính tuân thủ không nằm trong điểm số tổng hợp.** Các số đo tuân thủ đo lường việc bảo toàn cấu trúc (trình giữ chỗ, dấu ngoặc kép), chứ không phải chất lượng dịch thuật. Một bản dịch có thể hoàn hảo về mặt ngôn ngữ nhưng thất bại về mặt tuân thủ vì nó làm mất một biến `{name}`. Đây là các cổng chất lượng — chúng ngăn chặn đầu ra kém chất lượng được phân phối, nhưng chúng không xếp hạng chất lượng dịch thuật.

---

## 3. Các Phân bậc Trạng thái Số đo

Mọi số đo trong §2 đều thuộc một trong bốn phân bậc triển khai sau:

| Phân bậc | Ý nghĩa | Hành vi trên Run Card |
|------|---------|-------------------|
| **✅ Đã triển khai** | Mã nguồn đã tồn tại, đã được kiểm thử, hiện đang tạo ra các giá trị trong run card | Giá trị số trong run card |
| **⚡ Một phần** | Đã có proxy đặc thù theo ngôn ngữ (ví dụ: CRK) nhưng việc triển khai phổ quát vẫn đang chờ xử lý | Giá trị số khi áp dụng proxy, ngược lại là `null` |
| **🔲 Đã lên kế hoạch** | Đã được đặc tả nhưng chưa được triển khai | `null` trong run card (trường có tồn tại, giá trị bị khuyết) |
| **💡 Được đề xuất** | Đang được thảo luận, chưa được đặc tả | Không có trong run card |

Một số đo chuyển từ Đã lên kế hoạch → Một phần khi:
1. Bản triển khai đặc thù theo ngôn ngữ được merge và kiểm thử
2. Nó tạo ra các giá trị cho ít nhất một cặp ngôn ngữ
3. Bản triển khai phổ quát vẫn đang chờ xử lý (được ghi nhận trong đặc tả này)

Một số đo chuyển từ Một phần → Đã triển khai khi:
1. Bản triển khai không phụ thuộc ngôn ngữ (language-agnostic) được merge và kiểm thử
2. Nó tạo ra các giá trị cho bất kỳ cặp ngôn ngữ nào mà không cần các plugin đặc thù theo ngôn ngữ
3. Tài liệu này được cập nhật để phản ánh trạng thái ✅

Một số đo chuyển từ Đã lên kế hoạch → Đã triển khai khi:
1. Bản triển khai được merge và kiểm thử
2. Nó đã được xác thực trên ít nhất một lượt chạy đánh giá thực tế
3. Tài liệu này được cập nhật với các chi tiết triển khai của nó

Một số đo chuyển từ Được đề xuất → Đã lên kế hoạch khi:
1. Định nghĩa, thang đo, và phương pháp tính toán của nó được đồng thuận
2. Nó được thêm vào tài liệu này với trạng thái `🔲 Planned`
3. Một trình giữ chỗ null được thêm vào lược đồ run card

---

## 4. Điểm số Tổng hợp {#4-composite-score}

### 4.1 Công thức

Điểm số tổng hợp là trung bình cộng có trọng số của tất cả các số đo *khả dụng*, được tái chuẩn hóa sao cho tổng trọng số của các số đo khả dụng bằng 1.0:

```
composite = Σ (weight_i × value_i)    for all available metrics
             ─────────────────────
             Σ weight_i               (re-normalization denominator)
```

Một số đo được coi là "khả dụng" nếu giá trị của nó trong run card là một số (không phải `null`). Khi một số đo không khả dụng — do ngôn ngữ đó không có FST, hoặc do số đo đó chưa được triển khai — trọng số của nó sẽ được phân bổ lại theo tỷ lệ cho các số đo còn lại.

**Điều này có nghĩa là điểm số tổng hợp luôn có thể so sánh được trong cùng một lượt chạy:** nó sử dụng bất kỳ số đo nào khả dụng và chuẩn hóa tương ứng. Việc so sánh giữa các lượt chạy khác nhau chỉ hợp lệ khi các lượt chạy đó sử dụng cùng một tập hợp các số đo khả dụng.

> [!WARNING]
> **Khả năng so sánh giữa các lượt chạy.** Khi so sánh các lượt chạy có tính khả dụng của số đo khác nhau (ví dụ: một lượt chạy có điểm FST, lượt chạy khác thì không), các điểm số tổng hợp **không thể so sánh trực tiếp với nhau**. Một điểm số tổng hợp bằng 0.72 được tính từ 5 số đo mang lại nhiều thông tin hơn so với điểm số tổng hợp bằng 0.72 được tính từ 2 số đo. Bảng xếp hạng sẽ hiển thị cảnh báo khi phạm vi số đo khác nhau giữa các lượt chạy được so sánh. Để so sánh một cách chặt chẽ, hãy sử dụng các kiểm định ý nghĩa bootstrap bắt cặp (§8.2) chỉ trên các số đo chung.

### 4.2 Chuẩn hóa Đầu vào

Trước khi đưa vào công thức tổng hợp, tất cả các số đo phải nằm trên **thang đo 0.0–1.0** với 1.0 = hoàn hảo:

| Số đo | Thang đo Gốc | Chuẩn hóa |
|--------|-------------|---------------|
| `exact_match_rate` | 0.0–1.0 | Không (đã được chuẩn hóa) |
| `equivalent_match_rate` | 0.0–1.0 | Không |
| `fst_acceptance_rate` | 0.0–1.0 | Không |
| `morphological_accuracy` | 0.0–1.0 | Không |
| `chrf_plus_plus` | 0–100 | **Chia cho 100** |
| `semantic_score` | 0.0–1.0 | Không |
| `code_switching_rate` | 0.0–1.0 (thấp hơn = tốt hơn) | **`1.0 - value`** (đảo ngược: 0% chuyển mã ngôn ngữ = 1.0) |
| `hallucination_rate` | 0.0–1.0 (thấp hơn = tốt hơn) | **`1.0 - value`** (đảo ngược) |
| `terminology_adherence` | 0.0–1.0 | Không |

Các số đo bị loại trừ khỏi điểm số tổng hợp (`bleu`, `comet_score`, `ter`, `length_ratio`, `consistency_score`) không được chuẩn hóa cho mục đích này.

### 4.3 Bảng Trọng số {#43-weight-tables}

#### Profile A: Các ngôn ngữ CÓ Hỗ trợ FST

Dành cho các ngôn ngữ có sẵn bộ chuyển đổi trạng thái hữu hạn GiellaLT. Các số đo cấu trúc chiếm 40% điểm số tổng hợp (FST 0.25 + độ chính xác hình thái 0.15), phản ánh tầm quan trọng hàng đầu của tính chính xác hình thái đối với các ngôn ngữ đa tổng hợp/chắp dính.

| Số đo | Trọng số Mục tiêu | Cơ sở lý luận |
|--------|--------------|-----------|
| `fst_acceptance_rate` | **0.25** | Trọng số cao nhất. Nếu FST từ chối một từ, đó không phải là một dạng từ hợp lệ trong ngôn ngữ — bất kể các số đo khác nói gì. Nhị phân, dựa trên cấu trúc vững chắc. |
| `morphological_accuracy` | **0.15** | Một từ có thể hợp lệ về mặt FST nhưng sai về mặt hình thái (đúng từ căn, sai biến hình). Cùng với FST, các số đo cấu trúc chiếm 40%. |
| `chrf_plus_plus` | **0.15** | Độ trùng khớp n-gram ký tự: đại diện cấp độ bề mặt tốt nhất cho các ngôn ngữ đa tổng hợp. Xử lý hình thái chắp dính tốt hơn các số đo cấp độ từ. |
| `semantic_score` | **0.15** | Bảo toàn ý nghĩa khi dạng bề mặt khác biệt. Phát hiện các bản dịch sai ngữ nghĩa nhưng vượt qua các kiểm tra cấu trúc. |
| `equivalent_match_rate` | **0.10** | Thưởng cho các biến thể được chấp nhận, không chỉ một bản dịch tham chiếu duy nhất. Quan trọng đối với các ngôn ngữ có trật tự từ linh hoạt. |
| `code_switching_rate` | **0.05** | Phạt việc rò rỉ ngôn ngữ nguồn. Đảo ngược: 0% chuyển mã ngôn ngữ = 1.0. |
| `terminology_adherence` | **0.05** | Thưởng cho các phương pháp có hướng dẫn tôn trọng từ vựng được quy định. Chỉ hoạt động khi có dữ liệu hướng dẫn. |
| `hallucination_rate` | **0.05** | Phạt nội dung bịa đặt. Đảo ngược: 0% ảo tưởng = 1.0. |
| `exact_match_rate` | **0.05** | Trọng số thấp nhất. Quá khắt khe đối với các ngôn ngữ đa tổng hợp — do có nhiều bản dịch đúng cùng tồn tại. Được giữ lại như một bước kiểm tra giới hạn trần. |

> **Tổng cộng: 1.00.** Khi các số đo không khả dụng, trọng số của chúng sẽ được phân bổ lại theo tỷ lệ cho các số đo khả dụng. Hiện tại, `morphological_accuracy` (trọng số 0.15) là số đo duy nhất của Profile A chưa được tính toán — nó yêu cầu các chú thích hình thái chuẩn (gold-standard) theo từng mục. Khi thiếu số đo này, 8 số đo còn lại (tổng trọng số 0.85) sẽ được nhân với tỷ lệ tương ứng là 1/0.85 ≈ 1.176. Ví dụ:
> - FST: 0.25/0.85 = 0.294
> - chrF++: 0.15/0.85 = 0.176
> - semantic: 0.15/0.85 = 0.176

#### Profile B: Các ngôn ngữ KHÔNG CÓ Hỗ trợ FST

Dành cho các ngôn ngữ không có công cụ xác thực hình thái. Các số đo ngữ nghĩa và bề mặt có trọng số ngang nhau.

| Số đo | Trọng số Mục tiêu | Cơ sở lý luận |
|--------|--------------|-----------|
| `semantic_score` | **0.25** | Nếu không có xác thực cấu trúc, việc bảo toàn ý nghĩa là tín hiệu mạnh mẽ nhất hiện có. |
| `chrf_plus_plus` | **0.25** | Nếu không có FST, độ trùng khớp cấp độ ký tự trở thành bước kiểm tra bề mặt chính. |
| `equivalent_match_rate` | **0.15** | Khớp biến thể cung cấp đánh giá chất lượng có cấu trúc mà không yêu cầu các công cụ hình thái. |
| `exact_match_rate` | **0.10** | Nếu không có FST, khớp hoàn toàn (exact match) mang nhiều trọng số hơn như là đại diện xác thực cấu trúc duy nhất. |
| `code_switching_rate` | **0.10** | Việc rò rỉ ngôn ngữ nguồn quan trọng hơn khi không có FST để phát hiện đầu ra lỗi. |
| `terminology_adherence` | **0.05** | Tuân thủ từ vựng có hướng dẫn. |
| `hallucination_rate` | **0.05** | Phát hiện nội dung bịa đặt. |
| `orthographic_accuracy` | **0.05** | Tính chính xác đặc thù của chữ viết bù đắp một phần khoảng trống do thiếu FST để lại. |

> **Tổng cộng: 1.00.** `orthographic_accuracy` (trọng số 0.05) đã được lên kế hoạch nhưng chưa được tính toán. Khi thiếu nó, 7 số đo còn lại (tổng trọng số 0.95) được nhân với tỷ lệ tương ứng là 1/0.95 ≈ 1.053 — một tác động không đáng kể đến điểm số tổng hợp.

> **Lưu ý về sự phát triển của trọng số.** Các trọng số này mang tính tạm thời và sẽ được hiệu chuẩn lại khi dữ liệu xác thực của con người được tích lũy thêm. Mục tiêu dài hạn là rút ra các trọng số bằng thực nghiệm: số đo tự động nào dự đoán tốt nhất các đánh giá chất lượng của con người cho từng ngữ hệ?

### 4.4 Thêm một Số đo Mới vào Điểm số Tổng hợp

Để thêm một số đo mới vào điểm số tổng hợp:

1. **Định nghĩa nó** trong §2 với trạng thái `🔲 Planned`, bao gồm thang đo, cấp độ, và phương pháp tính toán.
2. **Triển khai nó** dưới dạng một MetricPlugin (or trong `tester.py` đối với các số đo cốt lõi).
3. **Thêm một trình giữ chỗ null** vào khối điểm số (scores block) của run card.
4. **Gán cho nó một trọng số mục tiêu** trong §4.3 bằng cách điều chỉnh giảm các trọng số hiện tại. Tổng các trọng số phải bằng 1.00.
5. **Cập nhật BENCHMARK_SPEC.md** §3 nếu lược đồ run card thay đổi.
6. **Cập nhật các bảng trọng số của `scoring.py`** (mã nguồn phải phản ánh chính xác tài liệu này).
7. **Chạy một benchmark xác thực** để xác nhận số đo tạo ra các giá trị hợp lý trên dữ liệu thực tế.
8. **Cập nhật tài liệu này** để chuyển trạng thái từ `🔲` sang `✅`.

---

## 5. Các Phân bậc Chất lượng {#5-quality-tiers}

Các phân bậc này là các nhãn phỏng đoán trên điểm số tổng hợp tự động. Chúng mô tả ý nghĩa thực tế thường thấy của các điểm số, dựa trên đánh giá của con người đối với đầu ra ở từng cấp độ. **Chúng không phải là các đánh giá chất lượng đã được xác thực** — chỉ có sự đánh giá của con người mới có thể xác nhận khả năng sử dụng thực tế.

> [!IMPORTANT]
> **Các phân bậc tự động mang tính tạm thời.** Các nhãn này là các đề cử để xem xét, không phải là tuyên bố về chất lượng. Một phương pháp đạt mức "Deployable" (Có thể triển khai) trên các số đo tự động chỉ là một ứng viên cho việc đánh giá của cộng đồng — chứ không phải là một sản phẩm để bàn giao. Chỉ có sự đánh giá của con người bởi những người nói song ngữ mới có thể xác nhận khả năng sử dụng thực tế (xem [BENCHMARK_SPEC §7](/docs/specifications/benchmark#7-human-validation)). Không phương pháp nào có thể tuyên bố đạt mức Deployable trở lên nếu không có sự đánh giá của cộng đồng xác nhận rằng những người nói đồng ý đầu ra là có thể sử dụng được. Ranh giới phân bậc có thể khác nhau giữa các ngôn ngữ khi dữ liệu xác thực của con người được tích lũy thêm.

| Phân bậc | Khoảng Điểm Tổng hợp | Những gì Người nói Thường thấy |
|------|----------------|-------------------------------|
| **Baseline** | 0.00–0.30 | Đầu ra LLM thô không có hỗ trợ đặc thù theo ngôn ngữ. Hình thái hầu hết là ảo tưởng. |
| **Emerging** | 0.30–0.50 | Xuất hiện một số mẫu đúng. Việc hướng dẫn (coaching) có giúp ích, nhưng đầu ra chưa đáng tin cậy. |
| **Functional** | 0.50–0.70 | Người nói có thể nhận diện được đầu ra. Các phạm trù ngữ pháp chính thường chính xác. Lỗi hình thái xuất hiện thường xuyên. |
| **Deployable** | 0.70–0.85 | Phù hợp cho bản dịch nháp có sự xem xét của con người. Hầu hết hình thái là chính xác. |
| **Fluent** | 0.85–1.00 | Tiệm cận bản dịch của người có năng lực. Lỗi hiếm gặp và nhỏ. |

Các phân bậc này mang tính tạm thời. Chúng sẽ được hiệu chuẩn lại khi dữ liệu xác thực của con người được tích lũy thêm và chúng tôi biết được ngưỡng "người nói thấy hữu ích" thực sự nằm ở đâu đối với từng ngôn ngữ. Không phương pháp nào có thể tuyên bố đạt mức **Deployable** trở lên nếu không có sự đánh giá của cộng đồng xác nhận rằng những người nói song ngữ đồng ý đầu ra là có thể sử dụng được.

### 5.1 Ngưỡng Phân bậc (Dành cho Máy đọc)

Đối với các triển khai mã nguồn, các ngưỡng là (được đánh giá từ trên xuống dưới, khớp đầu tiên sẽ thắng):

```
composite >= 0.85  →  "fluent"
composite >= 0.70  →  "deployable"
composite >= 0.50  →  "functional"
composite >= 0.30  →  "emerging"
composite >= 0.00  →  "baseline"
composite is null  →  "unscored"
```

---

## 6. Số đo Chi phí

Các số đo chi phí đo lường hiệu quả tài chính của một phương pháp dịch thuật. Chúng được báo cáo riêng biệt với chất lượng — chi phí không ảnh hưởng đến điểm số tổng hợp (ngoại trừ trong bảng xếp hạng phụ được điều chỉnh theo chi phí).

### 6.1 Số đo Token

| ID | Số đo | Cách tính |
|----|--------|-------------|
| `prompt_tokens` | Tổng số token đầu vào | Tổng của `usage.prompt_tokens` trên tất cả các lệnh gọi API |
| `completion_tokens` | Tổng số token đầu ra | Tổng của `usage.completion_tokens` |
| `reasoning_tokens` | Token chuỗi suy nghĩ (chain-of-thought) | Tổng của `usage.completion_tokens_details.reasoning_tokens` (bằng 0 đối với hầu hết các mô hình) |
| `cached_tokens` | Token được cache bởi nhà cung cấp | Tổng của `usage.prompt_tokens_details.cached_tokens` |
| `total_tokens` | Tổng số token đã tiêu thụ | `prompt_tokens + completion_tokens` |
| `tokens_per_entry` | Số token trung bình cho mỗi bản dịch | ✅ `total_tokens / entry_count` |

### 6.2 Số đo Chi phí

| ID | Số đo | Cách tính | Trường hợp Sử dụng |
|----|--------|-------------|----------|
| `total_cost_usd` | Tổng chi phí lượt chạy | Giá do nhà cung cấp báo × số lượng token | "Lượt chạy benchmark này tốn bao nhiêu tiền?" |
| `cost_per_entry_usd` | Chi phí cho mỗi mục ngữ liệu | `total_cost_usd / entry_count` | So sánh các phương pháp trên cùng một ngữ liệu |
| `cost_per_1k_tokens` | Chi phí trên 1.000 token | ✅ `total_cost_usd / total_tokens × 1000` | Hiệu suất LLM phổ quát — có thể so sánh giữa các ngữ liệu khác nhau |
| `cost_per_source_char` | Chi phí trên mỗi ký tự nguồn | `total_cost_usd / total_source_chars` | Có thể so sánh giữa các ngôn ngữ có cách phân tách token (tokenization) khác nhau |

> **Tại sao lại có nhiều số đo chi phí?** Một "mục" (entry) có độ dài khác nhau — một cụm từ 3 từ có chi phí thấp hơn một đoạn văn. `cost_per_entry_usd` hữu ích để so sánh các phương pháp trên *cùng một* ngữ liệu (cùng các mục = cùng độ dài = so sánh công bằng). `cost_per_1k_tokens` là số đo hiệu suất LLM tiêu chuẩn, có thể so sánh *giữa các* ngữ liệu khác nhau. `cost_per_source_char` chuẩn hóa cho các khác biệt về phân tách token — cùng một câu có thể được phân tách thành số lượng token khác nhau tùy thuộc vào từ vựng của mô hình.

### 6.3 Điểm số Điều chỉnh theo Chi phí

Đối với các phương pháp sử dụng API trả phí, chúng tôi tính toán một bảng xếp hạng phụ:

```
cost_adjusted = composite / log2(1 + cost_per_entry_usd × 1000)
```

Điều này thưởng cho các phương pháp đạt điểm số tốt một cách hiệu quả. Nó sử dụng `cost_per_entry_usd` (không phải theo token) vì điểm số điều chỉnh theo chi phí luôn được tính toán trong phạm vi một benchmark duy nhất (cùng một ngữ liệu), giúp việc so sánh theo từng mục trở nên công bằng.

Điểm số điều chỉnh theo chi phí là một **bảng xếp hạng phụ** — bảng xếp hạng chính xếp hạng theo điểm số tổng hợp. Nó trả lời cho một câu hỏi khác: "với một mức ngân sách nhất định, phương pháp nào mang lại kết quả tốt nhất?"

---

## 7. Số đo Tốc độ

Các số đo tốc độ đo lường độ trễ (latency) và thông lượng (throughput) của một phương pháp dịch thuật. Giống như chi phí, tốc độ không ảnh hưởng đến điểm số tổng hợp.

| ID | Số đo | Cách tính | Cấp độ |
|----|--------|-------------|-------|
| `elapsed_seconds` | Thời gian chạy thực tế (wall-clock) | `time_end - time_start` | Lượt chạy |
| `avg_latency_seconds` | Độ trễ trung bình mỗi mục | `Σ latency_s / n_entries` | Ngữ liệu |
| `median_latency_seconds` | Độ trễ trung vị mỗi mục | Phân vị thứ 50 của `latency_s` | Ngữ liệu |
| `p95_latency_seconds` | Độ trễ ở phân vị thứ 95 | Phân vị thứ 95 của `latency_s` | Ngữ liệu |
| `tokens_per_second` | Thông lượng | `total_tokens / elapsed_seconds` | Lượt chạy |
| `entries_per_minute` | Tốc độ dịch | `entry_count / (elapsed_seconds / 60)` | Lượt chạy |

---

## 8. Khoảng tin cậy và Ý nghĩa Thống kê

### 8.1 Khoảng Tin cậy Bootstrap

Tất cả các số đo chính đều hỗ trợ khoảng tin cậy bootstrap (phương pháp phân vị, n=1000 mẫu lại, α=0.05):

| Số đo | Khoảng Tin cậy (CI) được Báo cáo |
|--------|------------|
| `chrf_plus_plus` | ✅ `chrf_ci_lower`, `chrf_ci_upper` |
| `exact_match_rate` | ✅ `exact_match_ci_lower`, `exact_match_ci_upper` |
| `fst_acceptance_rate` | ✅ `fst_ci_lower`, `fst_ci_upper` (chỉ được tính toán khi có dữ liệu FST) |
| `comet_score` | ✅ `comet_ci_lower`, `comet_ci_upper` (được bootstrap từ các điểm số từng mục đã lưu cache — không cần suy luận mạng neural dư thừa) |
| `composite` | ✅ `composite_ci_lower`, `composite_ci_upper` (được tính toán khi có sẵn chrF++ và exact_match) |
| Khoảng tin cậy theo từng phân bậc | ✅ `confidence_intervals_by_tier` — khoảng tin cậy chrF++ và exact_match theo từng mức độ khó (Phân bậc 1-5) |

### 8.2 Kiểm định Ý nghĩa Bootstrap Bắt cặp

Để so sánh hai phương pháp, khung thử nghiệm tính toán các kiểm định tái lấy mẫu bootstrap bắt cặp:

```
H₀: The two methods perform equally on this corpus.
H₁: One method is significantly better.
```

Nếu giá trị p (p-value) < 0.05 và khoảng tin cậy của sự khác biệt không chứa giá trị không, sự khác biệt đó có ý nghĩa thống kê ở mức 95%.

---

## 9. Lược đồ Điểm số Run Card

Phần này định nghĩa cấu trúc phân cấp của khối `scores` trong một run card. Lược đồ này được rút ra từ các số đo được định nghĩa trong §2–§7 và phải được giữ đồng bộ.

```jsonc
{
  "scores": {
    // §2.1 Surface metrics
    "exact_match_rate":       0.6613,       // 0.0–1.0
    "exact_matches":          41,           // count
    "equivalent_match_rate":  0.7258,       // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "equivalent_matches":     45,           // ⚡ partial (CRK: eval_standards/crk CrkLinterMetric)
    "chrf_plus_plus":         80.65,        // 0–100 (sacrebleu native scale)
    "bleu":                   54.78,        // 0–100, NOT in composite
    "ter":                    42.3,         // ✅ implemented, 0–∞ (lower=better)
    "length_ratio":           1.03,         // ✅ implemented, ideal=1.0

    // §2.2 Structural metrics
    "fst_acceptance_rate":    1.0,          // 0.0–1.0
    "fst_accepted":           74,           // count
    "morphological_accuracy": null,         // 🔲 planned
    "orthographic_accuracy":  null,         // 🔲 planned

    // §2.3 Semantic metrics
    "semantic_score":         0.6842,       // ⚡ partial (CRK: eval_standards/crk CrkSemanticMetric)
    "comet_score":            null,         // nullable, NOT in composite
    "comet_model":            "",           // model ID used for COMET

    // §2.4 Behavioral metrics
    "code_switching_rate":    0.03,         // ✅ implemented (lower=better)
    "hallucination_rate":     0.01,         // ✅ implemented (lower=better)
    "terminology_adherence":  null,         // ✅ implemented (null when no glossary)
    "consistency_score":      null,         // 🔲 planned

    // §4 Composite
    "composite":              0.8988,       // 0.0–1.0
    "quality_tier":           "fluent",     // §5 tier label
    "cost_adjusted":          null,         // §6.3 secondary ranking

    // §7 Speed metrics (merged into scores block)
    "tokens_per_second":      4462.5,       // ✅ total_tokens / elapsed
    "entries_per_minute":     82.30,        // ✅ entry_count / (elapsed/60)
    "avg_latency_seconds":    0.234,
    "median_latency_seconds": 0.190,
    "p95_latency_seconds":    0.415,

    // §8.1 Confidence intervals
    "confidence_intervals": {
      "chrf_plus_plus":     { "ci_lower": 78.2, "ci_upper": 83.1 },
      "exact_match_rate":   { "ci_lower": 0.54, "ci_upper": 0.78 },
      "corpus_comet":       { "ci_lower": 0.71, "ci_upper": 0.76 }
    },
    "confidence_intervals_by_tier": {
      "1": { "corpus_chrf": { "ci_lower": 68.1, "ci_upper": 76.5 } },
      "3": { "corpus_chrf": { "ci_lower": 36.2, "ci_upper": 47.0 } }
    },

    // Breakdowns
    "by_difficulty":          {},           // scores grouped by difficulty tier
    "by_provenance":          {},           // scores grouped by entry provenance

    // Counts
    "total":                  62,
    "evaluated":              62,
    "errors":                 0
  },

  "totals": {
    // §6.1 Token metrics
    "prompt_tokens":          13985,
    "completion_tokens":      187822,
    "reasoning_tokens":       175726,
    "cached_tokens":          0,
    // §6.2 Cost metrics
    "total_cost_usd":         1.7114,
    "cost_per_entry_usd":     0.027603,
    "cost_per_source_char":   null          // 🔲 needs source char counting
  }
}
```

> **Lịch sử lược đồ.** Các bản thảo đặc tả trước đây đã đề xuất các khối `cost`, `speed`, và `tokens` riêng biệt. Chúng đã được gộp tương ứng vào `scores` và `totals` để đơn giản hóa. Các số đo tốc độ (`tokens_per_second`, `entries_per_minute`, độ trễ) nằm trong `scores`; số lượng token và số liệu chi phí nằm trong `totals`.

### 9.1 Ánh xạ Lược đồ–Cơ sở dữ liệu

JSON của run card được lưu trữ đầy đủ dưới dạng một cột `jsonb` trong Supabase. Các số đo chính cũng được phi chuẩn hóa (denormalized) thành các cột cấp cao nhất để tối ưu hóa hiệu năng sắp xếp/lọc:

| Trường Run Card | Cột Supabase | Kiểu dữ liệu | Chỉ mục |
|---------------|----------------|------|-------|
| `scores.composite` | `composite_score` | `real` | `idx_composite` |
| `scores.quality_tier` | `quality_tier` | `text` | — |
| `scores.chrf_plus_plus` | `chrf_plus_plus` | `real` | `idx_leaderboard` |
| `scores.exact_match_rate` | `exact_match_rate` | `real` | — |
| `scores.fst_acceptance_rate` | `fst_acceptance_rate` | `real` | — |
| `scores.bleu` | `corpus_bleu` | `real` | — |
| `scores.comet_score` | `comet_score` | `real` | — |
| `totals.total_cost_usd` | `total_cost_usd` | `real` | — |
| `totals.cost_per_entry_usd` | `cost_per_entry_usd` | `real` | — |
| `totals.cost_per_source_char` | `cost_per_source_char` | `real` | — |
| `scores.avg_latency_seconds` | `avg_latency_seconds` | `real` | — |
| `model_slug` | `model_slug` | `text` | `idx_model` |
| `condition` | `condition` | `text` | — |
| `dataset.id` | `dataset_id` | `text` | `idx_leaderboard` |
| `dataset.language_pair` | `language_pair` | `text` | — |
| `fingerprint.hash` | `fingerprint_hash` | `text` | `idx_fingerprint` |
| `scores.equivalent_match_rate` | `equivalent_match_rate` | `real` | — |
| `scores.semantic_score` | `semantic_score` | `real` | — |
| `scores.ter` | `ter` | `real` | — |
| `scores.length_ratio` | `length_ratio` | `real` | — |
| `scores.code_switching_rate` | `code_switching_rate` | `real` | — |
| `scores.hallucination_rate` | `hallucination_rate` | `real` | — |
| `scores.terminology_adherence` | `terminology_adherence` | `real` | — |
| `scores.tokens_per_second` | `tokens_per_second` | `real` | — |
| `scores.entries_per_minute` | `entries_per_minute` | `real` | — |
| `elapsed_seconds` | `elapsed_seconds` | `real` | — |
| *(toàn bộ card)* | `run_card` | `jsonb` | — |

Khi các số đo mới được triển khai, cột tương ứng nên được thêm vào thông qua một file migration được đánh số trong `arena/migrations/`.

---

## 10. Đồng bộ hóa Mã nguồn–Đặc tả

### 10.1 Nguồn Chuẩn (Canonical Source)

Tài liệu này (`arena/website/docs/specifications/scoring.md`) là nguồn chuẩn cho:
- Các định nghĩa số đo (§2)
- Các bảng trọng số tổng hợp (§4.3)
- Các ngưỡng phân bậc chất lượng (§5.1)
- Các công thức số đo chi phí (§6.2)
- Lược đồ điểm số run card (§9)

### 10.2 Phản chiếu Mã nguồn

Tệp `arena/mt_eval_harness/scoring.py` phản chiếu các bảng trọng số và ngưỡng phân bậc từ tài liệu này. Đây là **bản triển khai mã nguồn** của §4.3 và §5.1. Khi tài liệu này được cập nhật:

1. Cập nhật `scoring.py` để khớp
2. Chạy `pytest tests/test_scoring_ssot.py` để xác thực sự đồng bộ
3. Cập nhật FAQ và các tài liệu trên website tóm tắt các trọng số

### 10.3 Các Tài liệu Tham chiếu Đặc tả này

| Tài liệu | Nội dung Tham chiếu | Cách giữ Đồng bộ |
|----------|-------------------|---------------------|
| `arena/website/docs/specifications/benchmark-spec.md` §4–§5 | Công thức tổng hợp, bảng trọng số, ngưỡng phân bậc | Tham chiếu chéo đến tài liệu này; không sao chép lại các bảng |
| `website/docs/getting-started/faq.md` | Tóm tắt trọng số rút gọn | Phải khớp với §4.3; liên kết ngược lại tài liệu này |
| `arena/website/docs/how-it-works.md` | Ngưỡng Deployable | Phải khớp với §5 |
| `publish.py` thông qua `scoring.py` | Các từ điển trọng số + hàm phân bậc | Kiểm thử tự động xác thực sự trùng khớp |

---

## Phụ lục A: Các Số đo KHÔNG nằm trong Điểm số Tổng hợp (và Lý do)

| Số đo | Lý do Loại trừ |
|--------|-------------|
| **BLEU** | Việc chấm điểm ở cấp độ từ sẽ phạt các biến thể hình thái trong các ngôn ngữ đa tổng hợp. Một khác biệt nhỏ về biến hình (đúng ý nghĩa, hậu tố hơi khác một chút) sẽ bị tính là hoàn toàn sai lệch. chrF++ xử lý điều này tốt hơn ở cấp độ ký tự. |
| **COMET** | Được huấn luyện trên dữ liệu WMT (các cặp ngôn ngữ châu Âu giàu tài nguyên). Điểm số cho các ngôn ngữ ít tài nguyên (LRL) là không đáng tin cậy — mô hình đang ngoại suy từ các ngôn ngữ có hệ thống hình thái khác nhau. Được báo cáo để đảm bảo tính minh bạch, không dùng để chấm điểm. |
| **TER** | Khoảng cách chỉnh sửa tương quan với chrF++ trong hầu hết các trường hợp sử dụng. Việc đưa cả hai vào sẽ tính trùng lặp độ tương đồng bề mặt. TER được báo cáo để tham khảo. |
| **Length Ratio** | Một công cụ chẩn đoán, không phải tín hiệu chất lượng. Tỷ lệ 1.02 và tỷ lệ 0.98 đều ổn. Chỉ các giá trị cực đoan mới biểu thị vấn đề. |
| **Consistency Score** | Chỉ ở cấp độ ngữ liệu — không có giá trị theo từng mục để tổng hợp. Ngoài ra, một số sự không nhất quán là hợp lệ (cùng một từ tiếng Anh → các bản dịch ngôn ngữ đích khác nhau tùy thuộc vào ngữ cảnh). |
| **Compliance Index** | Cổng chất lượng, không phải tín hiệu chất lượng. Đo lường việc bảo toàn cấu trúc (trình giữ chỗ, dấu ngoặc kép), không phải độ chính xác của bản dịch. |

## Phụ lục B: LYSS — Các Bản triển khai Số đo Đặc thù theo Ngôn ngữ

Khung **LYSS** (Linguistically-informed Yield & Structural Scoring) cung cấp các số đo đặc thù theo ngôn ngữ vượt ra ngoài việc so sánh chuỗi ký tự ở cấp độ bề mặt. LYSS có ba thành phần cốt lõi:

- **LYSS-fst** — Tính hợp lệ về hình thái (`fst_acceptance_rate`): Mỗi từ có phải là một dạng hợp lệ trong ngôn ngữ đích không?
- **LYSS-eq** — Tính tương đương ngôn ngữ (`equivalent_match_rate`): Đầu ra có phải là một biến thể được chấp nhận của bản dịch tham chiếu không?
- **LYSS-sem** — Xác thực ngữ nghĩa (`semantic_score`): Đầu ra có bảo toàn ý nghĩa nguồn không?

> **Trạng thái xác thực: 🔶 Phỏng đoán kỹ thuật.** Các số đo LYSS CHƯA được xác thực so với các đánh giá chất lượng của con người. Chúng được thiết kế từ các nguyên lý ngôn ngữ học (FST, từ điển, quy tắc ngữ pháp được xây dựng bởi các nhà ngôn ngữ học tại UAlberta ALTLab), nhưng mối tương quan giữa điểm số LYSS và chất lượng dịch thuật thực tế vẫn chưa được đo lường. Xem [Speaker Validation Protocol](/docs/specifications/speaker-validation) để biết các thực nghiệm xác thực bắt buộc.

| Ngôn ngữ | Plugin | Vị trí | Thành phần LYSS | Khóa Số đo | Ghi chú |
|----------|--------|----------|----------------|------------|-------|
| CRK (Plains Cree) | `CrkLinterMetric` | `eval_standards/crk/metrics.py` | **LYSS-eq** | `equivalent_match_rate` | Các quy tắc lớp biến thể tất định: trật tự từ, chính tả, tiểu từ tùy chọn, từ đồng nghĩa của từ căn, tính mơ hồ tiếp diễn, bao gồm/loại trừ. Tạo ra `lint_verdict` theo từng mục (EXACT/EQUIVALENT/MISS/NO_OUTPUT). |
| CRK | `CrkSemanticMetric` | `eval_standards/crk/metrics.py` | **LYSS-sem** | `semantic_score` | Tất định: trích xuất từ căn FST + nghĩa từ điển + độ trùng khớp từ mang nội dung của spaCy. Tạo ra các phán quyết (EXACT_MATCH/VALID/GRAMMAR_ISSUES/PARTIAL/INCOMPLETE/WRONG/NO_OUTPUT). |
| Các ngôn ngữ GiellaLT | `GiellaLTFSTMetric` | `plugins/giellalt_fst.py` | **LYSS-fst** | `fst_acceptance_rate` | Chung: hoạt động cho CRK, SME, SMA, SMJ, SMN, SMS, FIN, NOB, IKU — bất kỳ ngôn ngữ nào có bộ phân tích `.hfstol`. |

> **Lưu ý về kiến trúc (Tháng 6 năm 2026).** Các số đo LYSS đặc thù theo ngôn ngữ hiện được khai báo trên thẻ ngôn ngữ dưới mục `evalMetrics` và được tải từ `eval_standards/<lang>/` bởi `plugin_discovery.py`. Chúng là **các tiêu chuẩn đánh giá** (trọng tài - referee), chứ không phải các số đo plugin phương pháp (thí sinh - contestant). Điều này có nghĩa là bất kỳ phương pháp dịch thuật nào nhắm mục tiêu đến CRK đều tự động được chấm điểm bởi LYSS — không cần cấu hình đặc thù theo phương pháp. `CrkFSTMetric` đã bị loại bỏ; chức năng của nó được bao quát hoàn toàn bởi `GiellaLTFSTMetric` chung.

## Phụ lục C: Các Số đo Đang được Cân nhắc

Các ý tưởng này đang được đánh giá nhưng chưa đủ chi tiết để đưa vào §2:

| Ý tưởng | Nội dung Đo lường | Rào cản |
|------|----------------------|----------|
| Độ trôi chảy (độ bối rối LM - LM perplexity) | Đầu ra có phải là văn xuôi được cấu trúc tốt trong ngôn ngữ đích không? | Yêu cầu một mô hình ngôn ngữ (LM) đích. Không có mô hình tốt nào tồn tại cho hầu hết các ngôn ngữ ít tài nguyên (LRL). |
| Khớp văn phong (Register match) | Bản dịch có khớp với mức độ trang trọng mong đợi không? | Yêu cầu các bộ phân loại ngôn ngữ học xã hội. Vấn đề nghiên cứu. |
| Tính phù hợp về văn hóa | Các tham chiếu văn hóa có được xử lý chính xác không? | Không thể tự động hóa — về bản chất yêu cầu sự đánh giá của con người. |
| Tính mạch lạc của diễn ngôn | Các bản dịch liên tiếp có tạo thành một đoạn văn mạch lạc không? | Yêu cầu đánh giá ở cấp độ tài liệu, không phải cấp độ câu. |

---

## Tài liệu Tham khảo

Các bài báo học thuật, công cụ, và tài nguyên ngôn ngữ được trích dẫn trong suốt đặc tả này.

### Số đo Bề mặt

1. Popović, M. (2017). "chrF++: words helping character n-grams." *Proceedings of the Second Conference on Machine Translation (WMT 2017)*, pp. 612–618. Copenhagen, Denmark.

2. Papineni, K., Roukos, S., Ward, T., & Zhu, W.-J. (2002). "BLEU: a method for automatic evaluation of machine translation." *Proceedings of the 40th Annual Meeting of the Association for Computational Linguistics (ACL 2002)*, pp. 311–318. Philadelphia, PA.

3. Post, M. (2018). "A Call for Clarity in Reporting BLEU Scores." *Proceedings of the Third Conference on Machine Translation (WMT 2018)*, pp. 186–191. Belgium, Brussels. Reference implementation: [sacrebleu](https://github.com/mjpost/sacrebleu).

4. Snover, M., Dorr, B., Schwartz, R., Micciulla, L., & Makhoul, J. (2006). "A Study of Translation Edit Rate with Targeted Human Annotation." *Proceedings of the 7th Conference of the Association for Machine Translation in the Americas (AMTA 2006)*, pp. 223–231. Cambridge, MA.

### Số đo Mạng Neural

5. Rei, R., Stewart, C., Farinha, A. C., & Lavie, A. (2020). "COMET: A Neural Framework for MT Evaluation." *Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP 2020)*, pp. 2685–2702. Online.

6. Juraska, J., Finkelstein, M., Deutsch, D., Siddhant, A., Miber, D., & Markl, A. (2023). "MetricX-23: The Google Submission to the WMT 2023 Metrics Shared Task." *Proceedings of the Eighth Conference on Machine Translation (WMT 2023)*. Singapore.

7. Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2020). "BERTScore: Evaluating Text Generation with BERT." *Proceedings of the Eighth International Conference on Learning Representations (ICLR 2020)*. Addis Ababa, Ethiopia.

8. Sellam, T., Das, D., & Parikh, A. (2020). "BLEURT: Learning Robust Metrics for Text Generation." *Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics (ACL 2020)*, pp. 7881–7892. Online.

### Công cụ Hình thái và Ngôn ngữ học

9. Lindén, K., Silfverberg, M., Axelson, E., Hardwick, S., & Pirinen, T. (2011). "HFST—Framework for Compiling and Applying Morphologies." *Systems and Frameworks for Computational Morphology (SFCM 2011)*, Communications in Computer and Information Science, vol. 100, pp. 67–85. Springer, Berlin, Heidelberg.

10. Sánchez-Cartagena, V. M., & Toral, A. (2024). "MorphEval: Automatic Evaluation of Morphological Capabilities of Machine Translation Systems." *Machine Translation*, vol. 38, pp. 1–28.

### Phân loại Lỗi và Đánh giá Chẩn đoán

11. Popović, M. (2011). "Hjerson: An Open Source Tool for Automatic Error Classification of Machine Translation Output." *The Prague Bulletin of Mathematical Linguistics*, no. 96, pp. 59–68.

12. Dreyer, M. & Marcu, D. (2012). "HyTER: Meaning-Equivalent Semantics for Translation Evaluation." *Proceedings of the 2012 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2012)*, pp. 162–171. Montréal, Canada.

13. Reiter, E. & Belz, A. (2009). "An Investigation into the Validity of Some Metrics for Automatically Evaluating Natural Language Generation Systems." *Computational Linguistics*, vol. 35, no. 4, pp. 529–558. (Related work on feature-based evaluation metrics, including FUSE.)

### Phát hiện Ảo tưởng

14. Raunak, V., Menezes, A., & Junczys-Dowmunt, M. (2021). "The Curious Case of Hallucinations in Neural Machine Translation." *Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (NAACL 2021)*, pp. 1172–1183. Online.

15. Guerreiro, N. M., Voita, E., & Martins, A. F. T. (2023). "Looking for a Needle in a Haystack: A Comprehensive Study of Hallucinations in Neural Machine Translation." *Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2023)*, pp. 1059–1075. Dubrovnik, Croatia.

### Tài nguyên Ngôn ngữ Cree

16. Wolfart, H. C. (1973). "Plains Cree: A Grammatical Study." *Transactions of the American Philosophical Society*, vol. 63, no. 5, pp. 1–90.

17. Wolvengrey, A. (2001). *nêhiyawêwin: itwêwina / Cree: Words.* Canadian Plains Research Center, University of Regina.

### Quản trị Dữ liệu

18. First Nations Information Governance Centre. "The First Nations Principles of OCAP®." [https://fnigc.ca/ocap-training/](https://fnigc.ca/ocap-training/). (OCAP® là nhãn hiệu đã đăng ký của First Nations Information Governance Centre.)

19. Carroll, S. R., Garba, I., Figueroa-Rodríguez, O. L., Holbrook, J., Lovett, R., Materechera, S., Parsons, M., Raseroka, K., Rodriguez-Lonebear, D., Rowe, R., Sara, R., Walker, J. D., Anderson, J., & Hudson, M. (2020). "The CARE Principles for Indigenous Data Governance." *Data Science Journal*, vol. 19, no. 1, p. 43.