---
sidebar_position: 2
title: "Cách thức chi trả cho người nói"
slug: '/perspectives/how-speakers-get-paid'
description: "Mức chi trả cho các dịch giả và người kiểm định cộng đồng đối với công việc đánh giá chuẩn (benchmark), tại sao việc chi trả cho người nói là nguyên tắc bắt buộc, và cách thức điều chỉnh mức thù lao khi Arena phát triển. Tất cả số liệu đều được lấy từ các tài liệu đặc tả đã công bố."
related:
  - label: "Speaker Validation Protocol"
    to: /docs/specifications/speaker-validation
    kind: spec
    note: "The work validators are paid for"
  - label: "Prize Specification"
    to: /docs/specifications/prizes
    kind: spec
    note: "Where prize money goes, and why"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
---
# Cách người nói được trả phí

> **Lưu ý về tính minh bạch.** Mọi con số trên trang này đều đã xuất hiện trong các tài liệu đặc tả đã công bố — [Đặc tả Benchmark §10](/docs/specifications/benchmark#10-cost-framework), [Giao thức Xác thực của Người nói](/docs/specifications/speaker-validation), và [Đặc tả Giải thưởng](/docs/specifications/prizes). Trang này tổng hợp các số liệu đó tại một nơi bằng ngôn ngữ dễ hiểu, để không ai phải đọc tài liệu đặc tả chỉ để tìm hiểu xem thời gian của người nói được định giá như thế nào ở đây. Trang này không đưa ra cam kết nào vượt quá những gì các tài liệu đó đã tuyên bố.

Một người nói song ngữ có khả năng đánh giá liệu một câu do máy tạo ra có tự nhiên, trôi chảy và truyền tải đúng nghĩa hay không là người tham gia khan hiếm và có giá trị nhất trong toàn bộ hệ thống này. Mọi thứ khác — harness, metric, leaderboard — tồn tại chỉ để giúp tối ưu hóa tối đa một lượng nhỏ thời gian của người đó.

Vì vậy, nguyên tắc đầu tiên rất đơn giản: **người nói được trả phí cho thời gian của họ, theo mức thù lao chuyên nghiệp, bất kể kết quả hiển thị như thế nào.**

---

## Tại sao việc trả phí cho người nói là không thể thương lượng

Nghiên cứu công nghệ ngôn ngữ từ lâu đã có thói quen coi những người nói trôi chảy là một nguồn tài nguyên miễn phí — một hình thức "gắn kết cộng đồng" tạo ra các bộ dữ liệu, bài báo khoa học và sự nghiệp cho tất cả mọi người ngoại trừ chính những người nói đó. Chúng tôi coi mô hình đó là mang tính bóc lột, và những người có đủ năng lực nhất để thực hiện công việc này lại chính là những người mà quỹ thời gian của họ vốn đã bị chiếm dụng bởi những công việc cấp thiết như giảng dạy, dịch thuật và nuôi dạy con cái bằng ngôn ngữ đó.

Từ đó dẫn đến ba hệ quả trong thiết kế hệ thống:

1. **Không có quy trình tình nguyện.** Chúng tôi không yêu cầu người nói đóng góp công việc đánh giá như một sự giúp đỡ cho nghiên cứu. Việc tham gia là một công việc có trả phí, và việc từ chối tham gia không gây ra bất kỳ tổn thất nào cho người nói.
2. **Thanh toán vô điều kiện.** Người nói được trả phí bất kể đánh giá của họ có được sử dụng hay không, và việc thanh toán không phụ thuộc vào kết quả. Giao thức đã công bố cam kết thanh toán trong vòng hai tuần sau khi hoàn thành mỗi khối nhiệm vụ.
3. **Thù lao không phải là tất cả.** Những người nói đóng góp đánh giá cũng nhận được sự ghi nhận danh tính (nêu tên hoặc ẩn danh, tùy họ chọn), quyền đồng tác giả (tùy chọn) trong các công bố khoa học sử dụng đánh giá của họ, quyền rút lại đóng góp của mình bất kỳ lúc nào, và quyền phủ quyết đối với việc công bố các kết quả mà họ thấy có vấn đề. Các điều khoản đó nằm trong [Giao thức Xác thực của Người nói §5–6](/docs/specifications/speaker-validation), chứ không phải trong một thỏa thuận phụ.

## Các mức phí đã công bố

Khung chi phí của benchmark quy định mức thù lao cho người nói song ngữ là **$50–65 CAD mỗi giờ** cho công việc xây dựng ngữ liệu và xác thực. Ý nghĩa của mức phí này đối với từng vai trò:

### Xây dựng ngữ liệu benchmark

Tạo ra các bản dịch tham chiếu để làm cơ sở chấm điểm cho mọi phương pháp dịch thuật là nhiệm vụ nền tảng của người nói. Ngân sách thiết lập đã công bố cho mỗi ngôn ngữ:

| Công việc | Khoảng chi phí đã công bố | Cơ sở tính phí |
|------|-----------------|-------|
| Biên tập ngữ liệu (50–150 mục) | $2,500–6,000 | $50–65/giờ, thời gian của người nói song ngữ |
| Đánh giá kết quả của phương pháp | $500–1,500 | Cùng mức phí theo giờ |

Một ngữ liệu đầy đủ theo cách truyền thống thường tiêu tốn của người nói khoảng 80 giờ; quy trình làm việc có sự hỗ trợ của tác nhân (việc soạn thảo câu và định dạng do công cụ xử lý, việc dịch thuật luôn do con người thực hiện) được thiết kế để giảm thời gian đó xuống còn khoảng 30–40 giờ — ít giờ làm việc lặp đi lặp lại hơn, cùng một mức phí theo giờ, và người nói chỉ thực hiện những phần thực sự cần đến con người.

### Xác thực các chỉ số (metric)

Trước khi các điểm số tự động có bất kỳ ý nghĩa nào, người nói phải đối chiếu chúng với đánh giá của con người. [Giao thức Xác thực của Người nói](/docs/specifications/speaker-validation) công bố chính xác các nhiệm vụ, số giờ và mức thù lao:

| Nhiệm vụ | Thời gian | Thù lao cho mỗi người nói |
|------|------|-----------------|
| A — Đánh giá 200 bản dịch máy về độ đầy đủ và độ trôi chảy | ~8 giờ | $400–520 CAD |
| B — Đánh giá 50 cặp dịch thuật "tương đương" | ~2 giờ | $100–130 CAD |
| C — Đánh giá 100 từ bị bộ phân tích hình thái từ chối | ~1.5 giờ | $75–100 CAD |

Một người nói thực hiện cả ba nhiệm vụ sẽ dành khoảng 11,5 giờ trong vòng hai đến bốn tuần để nhận **$575–750 CAD**. Toàn bộ vòng xác thực gồm ba người nói tiêu tốn của dự án $1,475–1,920 — và đó chính là mấu chốt: xác thực bởi người nói là một hạng mục chi phí nhỏ đối với dự án và không bao giờ được là nơi để "tiết kiệm" chi phí.

### Đánh giá các yêu cầu nhận giải thưởng

Không có giải thưởng nào được trao chỉ dựa trên điểm số tự động. [Giải thưởng của Nhà sáng lập](/docs/specifications/prizes) ($10,000 CAD, English→Plains Cree) yêu cầu ít nhất hai người nói song ngữ đánh giá độc lập một mẫu phân tầng gồm ít nhất 30 kết quả đầu ra, và 70% trở lên trong số đó phải được đánh giá là "chấp nhận được" hoặc "xuất sắc". Công việc đánh giá đó là công việc có trả phí cho người nói theo cùng mức thù lao — và đó cũng là một cánh cổng kiểm soát: người nói có thể bác bỏ một yêu cầu nhận giải thưởng, và điều đó nằm trong thiết kế của hệ thống.

## Cách hệ thống mở rộng quy mô cùng các cuộc thi

Mô hình này được xây dựng để thù lao của người nói tăng lên cùng với sự phát triển của nền tảng thay vì bị pha loãng bởi nó:

- **Mỗi ngôn ngữ mới đều bắt đầu bằng một công việc xây dựng ngữ liệu có trả phí.** Chi phí thiết lập đã công bố cho mỗi ngôn ngữ ($3,350–8,500 tất cả chi phí) phần lớn là thù lao cho người nói — đây là thành phần đơn lẻ lớn nhất, và đó là sự sắp đặt có chủ ý.
- **Mỗi quỹ giải thưởng mới đều đi kèm với công việc đánh giá có trả phí riêng.** Mọi cuộc thi được tài trợ tuân theo [mẫu giải thưởng](/docs/specifications/prizes#4-future-prize-pools) đều mang cùng một yêu cầu xác thực từ cộng đồng, điều đó có nghĩa là mọi cuộc thi đều tài trợ cho công việc đánh giá của người nói đối với ngôn ngữ đó.
- **Các phương pháp được triển khai sẽ tài trợ cho việc đánh giá liên tục.** Khi một phương pháp thuộc sở hữu của cộng đồng tạo ra doanh thu từ API, 90% doanh thu sẽ chuyển về tổ chức quản trị của cộng đồng đó ([mô hình kinh tế](/docs/sovereignty/economic-model)), tổ chức này có thể tài trợ cho việc tiếp tục đánh giá, phát triển ngữ liệu và các chương trình ngôn ngữ theo cách họ thấy phù hợp. Việc phân bổ đó là quyết định của cộng đồng, không phải của chúng tôi.

## Những gì chúng tôi *chưa* hứa hẹn

Sự trung thực đòi hỏi chúng tôi phải vạch rõ các giới hạn:

- Các mức phí trên là các mức phí đã công bố cho công việc hiện tại với tiếng Plains Cree. Mức phí cho các ngôn ngữ trong tương lai sẽ được thiết lập cùng với cộng đồng đối tác và được công bố theo cùng một cách — trong các tài liệu đặc tả, trước khi công việc bắt đầu.
- Vòng quay bánh đà (doanh thu → cộng đồng → nhiều công việc có trả phí hơn) cần có nguồn vốn bên ngoài để khởi động và hiện chưa thể tự duy trì. [Mô hình kinh tế](/docs/sovereignty/economic-model) mô tả cơ chế hoạt động, chứ không phải là một sự đảm bảo.
- "Được trả phí công bằng" là điều kiện cần nhưng chưa đủ. Bản thân việc thanh toán không làm cho một dự án trở nên phi bóc lột — quyền sở hữu và quyền kiểm soát mới làm được điều đó, đó là lý do tại sao thù lao nằm bên trong [kiến trúc chủ quyền](/docs/sovereignty/data-sovereignty) chứ không phải để thay thế nó.

---

## Điều này có ý nghĩa gì đối với bạn

:::info Nếu bạn là thành viên cộng đồng
Nếu bạn là người nói song ngữ một ngôn ngữ ít được hỗ trợ và tiếng Anh, đánh giá của bạn là đầu vào có giá trị nhất trong hệ thống này, và các điều khoản đã công bố là: $50–65 CAD/giờ, lịch trình linh hoạt, thanh toán trong vòng hai tuần, ghi nhận đóng góp theo điều khoản của bạn, và quyền rút lại các đóng góp của mình. Không yêu cầu kỹ năng lập trình. Hãy bắt đầu với [Dành cho cộng đồng ngôn ngữ](/docs/community/for-language-communities) hoặc [Giao thức Xác thực của Người nói §7](/docs/specifications/speaker-validation#7-how-to-get-started).
:::

:::info Nếu bạn là nhà nghiên cứu
Hãy lập ngân sách cho thù lao của người nói như một chi phí nghiên cứu hàng đầu — các số liệu đã công bố ($1,475–1,920 cho một vòng xác thực metric; $2,500–6,000 cho việc biên tập ngữ liệu) là nhỏ so với các tiêu chuẩn tài trợ nghiên cứu và chúng là những gì giúp cho các điểm số tự động có cơ sở vững chắc. [Chiến lược Hợp tác Ngữ liệu](/docs/specifications/corpus-partnership) chỉ ra cách một khoa học thuật có thể kết nối vào hệ thống này với công việc của người nói được tài trợ sẵn.
:::

:::info Nếu bạn là nhà phát triển
Bạn được hưởng lợi từ công việc có trả phí của người nói ngay cả khi bạn không bao giờ tài trợ cho nó: các metric được xác thực là những gì làm cho điểm số trên bảng xếp hạng của bạn có ý nghĩa, và việc đánh giá có trả phí của cộng đồng là rào cản giữa phương pháp của bạn và giải thưởng. Nếu bạn giành chiến thắng, hãy chuẩn bị tinh thần rằng người nói đã được trả phí để xem xét kỹ lưỡng kết quả đầu ra của bạn — và hãy chuẩn bị cho việc [quyền sở hữu phương pháp của bạn được chuyển giao](/docs/sovereignty/ownership-transfer) cho cộng đồng mà ngôn ngữ của họ được phương pháp đó phục vụ.
:::

## Xem thêm

- [Dịch thuật không phải là phục hưng ngôn ngữ](/docs/perspectives/translation-is-not-revitalization) — tại sao quyền quyết định của người nói định hình mọi thứ khác
- [Báo cáo lỗi và sở hữu các bản sửa lỗi](/docs/perspectives/reporting-errors-and-owning-corrections) — quyền quyết định của người nói sau khi benchmark hoàn thành
- [Đặc tả Benchmark §10](/docs/specifications/benchmark#10-cost-framework) — khung chi phí đầy đủ nơi các con số này được trích xuất