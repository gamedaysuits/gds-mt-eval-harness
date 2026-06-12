---
sidebar_position: 3
title: "Từ Benchmark đến Sử dụng Thực tế: Quy trình Hậu biên tập"
slug: '/perspectives/from-benchmark-to-daily-use'
description: "Cách một phương pháp dịch thuật đã được benchmark trở thành một quy trình dịch thuật cộng đồng: bản dịch nháp bằng máy, hậu biên tập bởi người nói lưu loát, văn bản được xuất bản — với các ngưỡng chất lượng trung thực ở từng bước."
related:
  - label: "Deploy to Production"
    to: /docs/getting-started/deploy-to-production
    kind: guide
    note: "From proven method to live translation"
  - label: "Cookbook: Partial Translation (Human + Machine)"
    to: /docs/tutorials/partial-translation
    kind: cookbook
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The quality thresholds behind the path"
  - label: "Translation Is Not Revitalization"
    to: /docs/perspectives/translation-is-not-revitalization
    kind: position
---
# Từ Benchmark đến Sử dụng Hàng ngày: Lộ trình Hậu biên tập

> **Tóm tắt ngắn gọn.** Điểm số trên bảng xếp hạng (leaderboard) không phải là một sản phẩm. Lộ trình từ "phương pháp này đạt điểm 0,78" đến "văn phòng cộng đồng xuất bản tài liệu bằng ngôn ngữ bản địa mỗi tuần" chỉ đi qua duy nhất một quy trình làm việc: máy dịch tạo ra bản nháp, một người nói lưu loát hiệu đính bản nháp đó, và chỉ có văn bản đã hiệu đính mới được xuất bản. Mọi ngưỡng chất lượng trong thông số kỹ thuật của chúng tôi đều được hiệu chuẩn theo quy trình đó — chứ không phải theo đầu ra máy dịch không có sự giám sát, điều mà chúng tôi không khuyến nghị cho bất kỳ ngôn ngữ nào trên nền tảng này.

Mọi người đôi khi hỏi khi nào một phương pháp dịch thuật sẽ "đủ tốt để chỉ việc sử dụng". Đối với các ngôn ngữ mà Arena này phục vụ, câu hỏi đó ẩn chứa một cái bẫy. Câu trả lời thành thật là mục tiêu đáng để hướng tới không phải là "đủ tốt để xuất bản mà không cần xem xét lại" — mà là **"đủ tốt để việc xem xét một bản nháp vẫn hiệu quả hơn là dịch lại từ đầu".** Ngưỡng đó thấp hơn nhiều, có thể đo lường được, và việc vượt qua nó sẽ thay đổi hoàn toàn khối lượng công việc mà một văn phòng dịch thuật cộng đồng có thể sản xuất trong một tuần.

---

## Quy trình làm việc, từ đầu đến cuối

```
 English source document
        │
        ▼
 Machine draft  ←  a benchmarked, community-owned method
        │
        ▼
 Fluent-speaker post-edit  ←  the human gate; nothing skips it
        │
        ▼
 Published text  ←  carries human approval, not a machine score
        │
        ▼
 (Optional, community-controlled) corrections become
 data that improves the next version of the method
```

Ba điều cần lưu ý:

1. **Máy dịch không bao giờ tự xuất bản.** Đơn vị đầu ra là một bản nháp. Bước hiệu đính của người nói không phải là khâu đảm bảo chất lượng được thêm vào ở cuối — đó chính là quy trình làm việc.
2. **Thời gian của người nói là tài nguyên được tối ưu hóa.** Một phương pháp tốt hơn một phương pháp khác chính xác ở chỗ nó giúp người nói có ít lỗi cần sửa hơn. Nghiên cứu về hậu biên tập (post-editing) đối với các ngôn ngữ giàu tài nguyên liên tục chỉ ra rằng quy trình này nhanh hơn dịch từ đầu ở mức chất lượng dịch máy (MT) trung bình (Plitt & Masselot 2010; Green, Heer & Manning 2013, cả hai đều được trích dẫn kèm liên kết trong [Dịch thuật không phải là Hồi sinh Ngôn ngữ](/docs/perspectives/translation-is-not-revitalization)). Liệu điều đó có đúng với các ngôn ngữ đa tổng hợp (polysynthetic) hay không chính là lý do hệ thống benchmark này tồn tại để tìm câu trả lời — chúng tôi coi đó là một giả thuyết cần xác minh cho từng ngôn ngữ, chứ không phải là một giả định.
3. **Vòng phản hồi được sở hữu.** Mỗi tài liệu được hiệu đính đều là dữ liệu huấn luyện và đào tạo tiềm năng — và nó thuộc về cộng đồng, để phản hồi lại (hoặc không) theo các điều khoản của họ dưới các quy tắc [chủ quyền dữ liệu](/docs/sovereignty/data-sovereignty). Cơ chế phản hồi là một mục tiêu thiết kế của nền tảng, chưa phải là một tính năng đã hoàn thiện; xem [Báo cáo Lỗi và Sở hữu Bản sửa lỗi](/docs/perspectives/reporting-errors-and-owning-corrections) để biết cách thức hoạt động dự kiến của các bản sửa lỗi và nguồn gốc dữ liệu.

## Ý nghĩa của các phân cấp chất lượng trong sử dụng thực tế

Bảng xếp hạng chấm điểm các phương pháp dựa trên một điểm số tổng hợp (composite score) từ các chỉ số tự động ([Thông số chấm điểm](/docs/specifications/scoring)), và các điểm số này được ánh xạ vào các phân cấp (tier) được đặt tên. Dưới đây là cách giải nghĩa thực tế của các phân cấp đó trong điều kiện sử dụng hàng ngày:

| Phân cấp (composite) | Ý nghĩa đối với lộ trình hậu biên tập |
|---|---|
| **Baseline** (0.00–0.30) | Không thể sử dụng cho bất kỳ việc gì. Đầu ra phần lớn không phải là ngôn ngữ đích. Chỉ hữu ích làm mức sàn nghiên cứu. |
| **Emerging** (0.30–0.50) | Vẫn chưa thể làm công cụ soạn thảo. Các đoạn dịch đúng có xuất hiện, nhưng người nói sẽ mất nhiều thời gian để sửa hơn là viết mới. |
| **Functional** (0.50–0.70) | Phân cấp đầu tiên mà việc hậu biên tập *có thể* vượt trội hơn dịch từ đầu đối với các văn bản dễ — đáng để thử nghiệm với một người nói, nhưng chưa đáng để phụ thuộc vào. Các lỗi hình thái học (morphological errors) vẫn xuất hiện thường xuyên. |
| **Deployable** (0.70–0.85) | Phân cấp mục tiêu cho quy trình làm việc ở trên: các bản nháp có hầu hết hình thái học chính xác và một người nói lưu loát có thể sửa nhanh hơn đáng kể so với việc dịch lại. **"Deployable" nghĩa là có thể triển khai *vào một quy trình hậu biên tập* — tuyệt đối không phải là "xuất bản không cần xem xét".** |
| **Fluent** (0.85–1.00) | Tiếp cận mức độ dịch thuật thành thạo của con người; lỗi hiếm gặp và nhỏ. Bước xem xét lại vẫn giữ nguyên — chỉ là nó sẽ nhanh hơn. |

Hai quy tắc trung thực về mặt cấu trúc được áp dụng cho bảng này, được trích trực tiếp từ [Thông số kỹ thuật Benchmark §5 và §7](/docs/specifications/benchmark#5-quality-tiers):

- **Các phân cấp tự động chỉ là nhãn tạm thời, không phải là phán quyết.** Chúng là các đề cử để con người đánh giá lại. Các ngưỡng sẽ được hiệu chuẩn lại khi dữ liệu xác thực từ người nói được tích lũy, và chúng có thể có kết quả khác nhau đối với các ngôn ngữ khác nhau.
- **Không phương pháp nào có thể tuyên bố đạt mức Deployable trở lên nếu không có sự đánh giá của cộng đồng.** Một mẫu phân tầng (stratified sample) từ đầu ra của phương pháp đó sẽ được gửi đến những người nói song ngữ, họ sẽ đánh giá từng bản dịch theo các mức *từ chối (reject) / hiểu ý chính (gist) / chấp nhận được (acceptable) / xuất sắc (excellent)*. Tổ chức quản trị — chứ không phải bảng xếp hạng — sẽ quyết định xem phương pháp đó có được thăng cấp hay không.

Để so sánh, ngưỡng của giải thưởng [Founder's Prize](/docs/specifications/prizes) (composite score ≥ 0.80, ≥99% từ hợp lệ về mặt hình thái, ≥70% được người nói đánh giá từ mức chấp nhận được trở lên) mô tả một phương pháp mà các lỗi còn lại là *lỗi ngôn ngữ thực tế* — chia sai từ (wrong inflection), chứ không phải là các từ tự bịa ra. Đó là hình ảnh bằng số liệu của "một bản nháp xứng đáng với thời gian của người nói".

## Từ một phương pháp chiến thắng đến một văn phòng hoạt động hiệu quả

Giả sử một phương pháp vượt qua được các rào cản đó. Các bước còn lại thuộc về mặt tổ chức, và chúng được quy định rõ ràng chứ không phải là tự phát:

1. **Chuyển giao quyền sở hữu.** Mã nguồn của phương pháp trở thành tài sản của tổ chức quản trị của cộng đồng — nhà phát triển vẫn giữ quyền ghi nhận tác giả và quyền công bố ([Chuyển giao quyền sở hữu](/docs/sovereignty/ownership-transfer)).
2. **Phương pháp trở thành một dịch vụ.** Nó được đóng gói dưới dạng một plugin và được cung cấp thông qua nền tảng triển khai, với việc cộng đồng kiểm soát quyền truy cập, giá cả và các mục đích sử dụng được phép ([Triển khai lên Môi trường Thực tế](/docs/getting-started/deploy-to-production)).
3. **Biên dịch viên tích hợp nó vào công việc hàng ngày.** Một văn phòng dịch thuật hướng quy trình tài liệu hiện tại của mình vào API của phương pháp: văn bản nguồn đi vào, bản nháp đi ra, hậu biên tập, xuất bản. Văn bản được xuất bản mang tên và uy tín của biên dịch viên — máy dịch chỉ là một công cụ trên bàn làm việc của họ, giống như một cuốn từ điển.
4. **Doanh thu đi liền với mức độ sử dụng.** Các nhà phát triển bên ngoài sử dụng phương pháp này sẽ trả phí theo mức sử dụng, và 90% doanh thu đó sẽ chảy về tổ chức quản trị ([Mô hình Kinh tế](/docs/sovereignty/economic-model)) — nguồn kinh phí này có thể tài trợ thêm giờ làm việc cho biên dịch viên, khép kín vòng lặp.

## Tình trạng hiện tại

Nói một cách rõ ràng: toàn bộ lộ trình đã được quy định từ đầu đến cuối, và đã được xây dựng một phần. Hệ thống đánh giá (evaluation harness), các chỉ số (metrics), thẻ chạy (run cards) và bảng xếp hạng công khai đã tồn tại; kho ngữ liệu phát triển tiếng Plains Cree và một giải thưởng đang hoạt động đã tồn tại; nền tảng triển khai đã tồn tại. Giao diện đánh giá của cộng đồng, môi trường thử nghiệm đánh giá (evaluation sandbox) và vòng phản hồi văn bản đã hiệu đính đã được quy định nhưng chưa đi vào hoạt động — các thông số kỹ thuật đánh dấu chúng là đang lên kế hoạch, và chúng tôi cũng vậy. Chưa có phương pháp nào hoàn thành toàn bộ hành trình từ benchmark đến việc sử dụng hàng ngày trong cộng đồng. Hành trình đó chính là định nghĩa về sự thành công của dự án, đó chính xác là lý do tại sao chúng tôi sẽ không tuyên bố đạt được nó quá sớm.

---

## Điều này có ý nghĩa gì đối với bạn

:::info Nếu bạn là một thành viên cộng đồng
Huy hiệu "Deployable" trên bảng xếp hạng không bao giờ có nghĩa là máy dịch sẽ tự xuất bản bằng ngôn ngữ của bạn mà không có sự giám sát — nó có nghĩa là một công cụ tạo bản nháp có thể đã sẵn sàng để *thử việc* trước các biên dịch viên của bạn, theo các điều khoản của bạn, với người nói của bạn làm giám khảo (những người được trả lương — xem [Cách người nói được trả lương](/docs/perspectives/how-speakers-get-paid)). Nếu cộng đồng của bạn vận hành một văn phòng dịch thuật, câu hỏi liên quan cần đặt ra cho chúng tôi là: "một chương trình thí điểm sẽ trông như thế nào, và ai sẽ đánh giá kết quả đầu ra?"
:::

:::info Nếu bạn là một nhà nghiên cứu
Cách tiếp cận theo hướng hậu biên tập thay đổi những gì đáng để đo lường: thời gian để đạt được văn bản chấp nhận được (time-to-acceptable-text) với sự tham gia của người nói, chứ không chỉ là composite score. Các chỉ số của Arena là đại diện cho điều đó ([Thông số chấm điểm §1](/docs/specifications/scoring)), và các nghiên cứu hậu biên tập theo từng ngôn ngữ đối với các ngôn ngữ có cấu trúc hình thái phức tạp là một khoảng trống nghiên cứu mở mà cơ sở hạ tầng này được thiết kế để hỗ trợ.
:::

:::info Nếu bạn là một nhà phát triển
Hãy tối ưu hóa cho người biên tập, chứ không phải cho chỉ số. Một phương pháp tạo ra các từ có thật với các lỗi chia từ thỉnh thoảng xảy ra có thể được người nói sửa trong vài giây; một phương pháp tạo ra các từ giả trông có vẻ hợp lý sẽ làm hỏng toàn bộ quy trình làm việc — đó là lý do tại sao tính hợp lệ về mặt hình thái (morphological validity) được kiểm soát rất nghiêm ngặt ở đây. Hãy bắt đầu tại [Gửi một Phương pháp](/docs/getting-started/submit-a-method), và đọc [Giao diện Phương pháp](/docs/specifications/methods) để biết những gì bạn sẽ bàn giao nếu giành chiến thắng.
:::

## Xem thêm

- [Dịch thuật không phải là Hồi sinh Ngôn ngữ](/docs/perspectives/translation-is-not-revitalization) — tại sao rào cản con người là điểm mấu chốt, chứ không phải là một hạn chế
- [Báo cáo Lỗi và Sở hữu Bản sửa lỗi](/docs/perspectives/reporting-errors-and-owning-corrections) — điều gì xảy ra khi văn bản được xuất bản vẫn bị sai
- [Thông số kỹ thuật Benchmark §7](/docs/specifications/benchmark#7-human-validation) — rào cản xác thực bởi con người, một cách chính thức