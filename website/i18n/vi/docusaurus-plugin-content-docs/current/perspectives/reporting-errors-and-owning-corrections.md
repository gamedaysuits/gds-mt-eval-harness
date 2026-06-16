---
sidebar_position: 4
title: "Báo cáo sai sót và Quyền sở hữu bản sửa lỗi"
slug: '/perspectives/reporting-errors-and-owning-corrections'
description: "Cách người nói báo cáo một thông tin sai lệch hoặc một bản dịch kém chất lượng, ai là người quyết định bước tiếp theo, cách các bản sửa lỗi lưu lại thông tin nguồn gốc, và tại sao các cộng đồng lại nắm giữ quyền phủ quyết đối với dữ liệu ngôn ngữ của họ."
related:
  - label: "Data Sovereignty"
    to: /docs/sovereignty/data-sovereignty
    kind: doc
    note: "Who holds veto power over language data"
  - label: "Ownership Transfer"
    to: /docs/sovereignty/ownership-transfer
    kind: doc
  - label: "Speaker Validation Protocol"
    to: /docs/specifications/speaker-validation
    kind: spec
  - label: "How Speakers Get Paid"
    to: /docs/perspectives/how-speakers-get-paid
    kind: position
---
# Báo cáo Lỗi và Quyền sở hữu Bản sửa lỗi

> **Quan điểm.** Sai sót là điều không thể tránh khỏi đối với một nền tảng công bố các dữ kiện và đánh giá về hàng ngàn ngôn ngữ. Điều *có thể* tránh được là việc ai sẽ được tin tưởng khi có báo cáo lỗi, và ai là người sở hữu bản sửa lỗi đó. Câu trả lời của chúng tôi: báo cáo của một người nói lưu loát có giá trị cao hơn hệ thống tự động của chúng tôi, mỗi bản sửa lỗi đều mang theo nguồn gốc (provenance) ghi rõ ai đã thay đổi nội dung gì và tại sao, và một cộng đồng có thể rút lại hoặc phủ quyết việc sử dụng dữ liệu ngôn ngữ của họ — không phải như một sự chiếu cố, mà là một thuộc tính được thực thi của kiến trúc hệ thống.

Hầu hết các nền tảng dữ liệu đều coi các báo cáo lỗi như các yêu cầu hỗ trợ (support ticket): người dùng phàn nàn, người duy trì quyết định, và bản ghi thay đổi một cách âm thầm. Đối với dữ liệu ngôn ngữ bản địa, mô hình đó hoàn toàn bị đảo ngược. Người báo cáo lỗi thường có thẩm quyền cao hơn nền tảng — một người bản xứ nói với chúng tôi rằng một từ bị sai không phải là một "người dùng", họ chính là ground truth đang sửa lại một proxy. Thiết kế dưới đây xuất phát từ việc nghiêm túc thực hiện nguyên tắc đó.

---

## Hai loại lỗi, một nguyên tắc

Nền tảng công bố hai loại khẳng định có thể bị sai:

1. **Các dữ kiện về một ngôn ngữ** — các thẻ ngôn ngữ (language card) điều phối việc đánh giá: dữ liệu phân loại, chính tả, các đặc điểm ngôn ngữ, các chỉ số (metric) nào được áp dụng. Một thẻ có thể đưa ra ước tính sai về số lượng người nói, quan hệ phương ngữ sai, hoặc trạng thái hệ thống chữ viết sai.
2. **Các đánh giá về bản dịch** — một bản dịch tham chiếu trong kho ngữ liệu (corpus) mà người nói bản xứ coi là sai hoặc không tự nhiên; một chỉ số tự động từ chối một từ hợp lệ hoặc chấp nhận một từ không hợp lệ; một huy hiệu "Có thể triển khai" (Deployable) trên kết quả đầu ra mà người nói bản xứ không chấp nhận.

Nguyên tắc bao trùm cả hai, vốn đã mang tính ràng buộc trong [Tài liệu kỹ thuật Scoring Specification](/docs/specifications/scoring) và [Tài liệu kỹ thuật Benchmark Specification §7](/docs/specifications/benchmark#7-human-validation): **kết quả đầu ra tự động là các proxy; người nói bản xứ là ground truth.** Cam kết được công bố trong [Giao thức Xác thực Người nói (Speaker Validation Protocol) §6](/docs/specifications/speaker-validation#6-what-speakers-get) đã nêu rõ ràng: nếu một người nói bản xứ nói rằng linter sai về điều gì đó, chúng tôi sẽ sửa linter.

## Quy trình xử lý báo cáo

Dưới đây là lộ trình mà một báo cáo sẽ trải qua, cùng với các trạng thái thực tế — một số tính năng hiện đã hoạt động, một số khác mới chỉ nằm trong tài liệu kỹ thuật và chưa được xây dựng.

**Báo cáo bản dịch kém chất lượng hoặc đánh giá chỉ số sai (đang hoạt động, qua kênh trực tiếp).** Người nói bản xứ khi phát hiện bản dịch tham chiếu sai, một từ bị từ chối oan, hoặc một từ "tương đương" không thể chấp nhận được có thể báo cáo thông qua trình theo dõi lỗi (issue tracker) trên kho lưu trữ công khai của dự án hoặc bằng cách liên hệ trực tiếp với dự án. Phiên bản có cấu trúc của tính năng này — màn hình xếp hạng với các tùy chọn *từ chối (reject) / nắm ý chính (gist) / chấp nhận được (acceptable) / xuất sắc (excellent)* và ghi chú tự do — là giao diện đánh giá của cộng đồng, được quy định trong [Tài liệu kỹ thuật Benchmark Specification §7.3](/docs/specifications/benchmark#7-human-validation) nhưng chưa được đưa vào hoạt động. Cho đến lúc đó, các báo cáo sẽ được xử lý trực tiếp giữa người với người, và bản thân các tác vụ xác thực (đánh giá có trả phí, có cấu trúc của người nói bản xứ — xem [Cách Người nói bản xứ được Trả phí](/docs/perspectives/how-speakers-get-paid)) là kênh sửa lỗi chính.

**Báo cáo dữ kiện sai trên thẻ ngôn ngữ (đang hoạt động, cùng các kênh trên).** Việc sửa lỗi trên thẻ cũng tuân theo lộ trình tương tự: báo cáo, xem xét, thay đổi có phiên bản. Vì các thẻ điều phối hành vi đánh giá — chỉ số nào được tải, mô hình nào được đề xuất — việc sửa thẻ có thể làm thay đổi điểm số, do đó các sửa đổi được áp dụng dưới dạng các thay đổi dữ liệu được ghi nhận, tuyệt đối không có việc chỉnh sửa âm thầm.

**Điều gì xảy ra tiếp theo — ai là người quyết định:**

- **Các quyết định đánh giá ngôn ngữ thuộc về người nói ngôn ngữ đó.** Liệu một dạng từ có hợp lệ hay không, hai cách diễn đạt có tương đương hay không, một văn phong (register) có phù hợp hay không — nền tảng chỉ thực thi câu trả lời chứ không tự đưa ra câu trả lời. Khi những người nói bản xứ không đồng ý với nhau (về phương ngữ, quy ước chính tả), câu trả lời sẽ được ghi nhận dưới dạng biến thể chứ không phải do chúng tôi phân xử — cấu trúc (schema) của kho ngữ liệu và linter hỗ trợ gắn thẻ các biến thể phương ngữ như các lựa chọn thay thế được chấp nhận thay vì bắt buộc chọn ra một phương án duy nhất.
- **Các quyết định về dữ liệu của một cộng đồng thuộc về tổ chức quản trị của cộng đồng đó.** Đối với các ngôn ngữ có tổ chức quản trị, các thay đổi đối với kho ngữ liệu đánh giá, việc chấp nhận các sửa đổi vào các tập kiểm thử khép kín (sealed test sets), và các hệ quả triển khai đều phải thông qua họ — đó là nguyên tắc Kiểm soát (Control) của [OCAP®](/docs/sovereignty/data-sovereignty) được thực thi dưới dạng quy trình thực tế, chứ không phải khẩu hiệu trên áp phích.
- **Các lỗi kỹ thuật thuần túy sẽ được sửa trực tiếp.** Lỗi chính tả, liên kết hỏng, trường dữ liệu bị phân tích sai — sau khi được báo cáo sẽ được sửa và ghi nhật ký (log). Không phải việc gì cũng cần đến một hội đồng.

## Các bản sửa lỗi phải mang theo nguồn gốc dữ liệu

Một bản sửa lỗi mà bạn không thể truy vết nguồn gốc thì chỉ là một ý kiến mới hơn mà thôi. Ba quy tắc về nguồn gốc dữ liệu (provenance) được áp dụng cho mọi dữ kiện và mọi bản sửa lỗi:

1. **Mọi dữ kiện đều phải chỉ rõ nguồn.** Các thẻ ngôn ngữ và các mục trong kho ngữ liệu đều ghi lại nguồn gốc của từng giá trị — một tập dữ liệu đã công bố, một đóng góp từ cộng đồng, hoặc một đánh giá của người nói bản xứ.
2. **Các giá trị phái sinh được gắn nhãn là của chúng tôi, không phải của nguồn thượng nguồn (upstream).** Khi nền tảng tính toán một giá trị nào đó — một giá trị tổng hợp, một mã hóa lại, một composite score — giá trị đó sẽ được ghi nhận là một phái sinh của nền tảng *từ* nguồn thượng nguồn, tuyệt đối không bao giờ được ghi dưới tên của nguồn thượng nguồn đó. Một tập dữ liệu thượng nguồn không bao giờ phải chịu trách nhiệm hoặc được ghi nhận công lao cho một con số mà họ không hề công bố.
3. **Các bản sửa lỗi trở thành một phần của hồ sơ.** Bản sửa lỗi của người nói bản xứ được ghi nhận là một khẳng định mới, có ghi nhận nguồn đóng góp (nêu tên hoặc ẩn danh, tùy theo lựa chọn của người nói — cùng các điều khoản như công việc xác thực) thay thế cho giá trị cũ; lịch sử thay đổi vẫn có thể kiểm toán được. Các phiên bản kho ngữ liệu được xác thực bằng mã băm (hash-manifested) ([Hợp tác Kho ngữ liệu (Corpus Partnership) §4.4](/docs/specifications/corpus-partnership)), vì vậy một kho ngữ liệu đã sửa đổi sẽ hiển thị rõ ràng là một phiên bản mới, và mỗi run card đều ghi lại chính xác phiên bản nào đã được dùng để chấm điểm — các điểm số cũ vẫn có thể giải thích được, các điểm số mới phản ánh đúng bản sửa lỗi.

## Quyền phủ quyết, một cách cụ thể

"Kiểm soát của cộng đồng" là điều dễ dàng tuyên bố. Dưới đây là cách điều đó được hiện thực hóa trong kiến trúc đã công bố:

- **Người nói bản xứ có thể rút lại đóng góp của họ.** Người nói bản xứ có thể rút lại các đánh giá của mình bất kỳ lúc nào, và việc rút lại này sẽ xóa chúng khỏi tất cả các phân tích ([Xác thực Người nói (Speaker Validation) §5](/docs/specifications/speaker-validation#5-data-governance)). Người nói bản xứ cũng nắm quyền phủ quyết đối với việc công bố các kết quả mà họ thấy có vấn đề.
- **Cộng đồng có thể dừng hoàn toàn việc đánh giá.** Các tập kiểm thử khép kín được mã hóa, với các khóa được lưu giữ sao cho riêng nền tảng không bao giờ có thể khôi phục lại chúng; một cộng đồng có thể thu hồi quyền truy cập đánh giá bằng cách từ chối tham gia vào việc khôi phục khóa ([Hợp tác Kho ngữ liệu (Corpus Partnership) §4.3](/docs/specifications/corpus-partnership#4-cryptographic-sealing-and-sandbox-testing)). Câu hỏi "Nếu chúng tôi muốn dừng lại thì sao?" đã có câu trả lời rõ ràng trong tài liệu kỹ thuật: dữ liệu khép kín không bao giờ bị lộ, và việc đánh giá sẽ kết thúc.
- **Không có điểm số nào có thể ghi đè quyết định của cộng đồng.** Một phương pháp đứng đầu bảng xếp hạng vẫn chỉ được triển khai nếu tổ chức quản trị cho phép ([Chuyển giao Quyền sở hữu (Ownership Transfer)](/docs/sovereignty/ownership-transfer)) — và một cộng đồng quyết định hoàn toàn không triển khai dịch máy (MT) cho ngôn ngữ của họ là đang vận hành hệ thống đúng như thiết kế, chứ không phải làm hỏng hệ thống (xem [Dịch thuật không phải là Khôi phục Ngôn ngữ (Translation Is Not Revitalization)](/docs/perspectives/translation-is-not-revitalization)).

## Những gì chúng tôi chưa xây dựng

Theo tinh thần của phần còn lại trong kho tài liệu này: giao diện đánh giá của cộng đồng mới chỉ nằm trong kế hoạch chứ chưa hoạt động. Chưa có tổ chức quản trị nào được thành lập cho bất kỳ ngôn ngữ hiện tại nào — quyền giám hộ của cộng đồng đối với điểm chuẩn Plains Cree đang trong quá trình xác nhận, và chúng tôi không công khai tên của những người giám hộ trước khi họ đồng ý. Cho đến khi các mảnh ghép đó tồn tại, các sửa đổi sẽ được thực hiện thông qua các kênh trực tiếp, có thể truy xuất nguồn gốc, và các tài liệu kỹ thuật đã công bố — chứ không phải trang này — vẫn là mô tả có tính ràng buộc về quy trình. Nếu trang này và tài liệu kỹ thuật có điểm không thống nhất, tài liệu kỹ thuật sẽ được ưu tiên áp dụng, và chúng tôi cũng coi sự không thống nhất đó là một lỗi đáng để báo cáo.

---

## Ý nghĩa của điều này đối với bạn

:::info Nếu bạn là thành viên cộng đồng
Nếu có điều gì đó về ngôn ngữ của bạn trên nền tảng này bị sai — một dữ kiện, một bản dịch, một nhãn dán — báo cáo của bạn là minh chứng từ ground truth, chứ không phải là một khiếu nại cần được phân loại xử lý. Bạn quyết định xem bản sửa lỗi của mình có được ghi nhận bằng tên hay không; đóng góp của bạn có thể được rút lại sau đó; và cộng đồng của bạn có thể dừng hoàn toàn việc sử dụng dữ liệu của mình. Hãy bắt đầu tại [Dành cho các Cộng đồng Ngôn ngữ](/docs/community/for-language-communities), hoặc chỉ cần mở một issue trên kho lưu trữ công khai.
:::

:::info Nếu bạn là nhà nghiên cứu
Các bản sửa lỗi ở đây là dữ liệu có nguồn gốc rõ ràng (provenance), không phải là các chỉnh sửa âm thầm: các phiên bản kho ngữ liệu được băm mã hóa, các run card ghim chính xác phiên bản được dùng để chấm điểm, và các giá trị phái sinh được gắn nhãn rõ ràng. Nếu bạn phát triển dựa trên điểm số hoặc kho ngữ liệu của Arena, hãy trích dẫn phiên bản — và hãy coi làn sóng sửa lỗi do người nói bản xứ dẫn dắt là một phát hiện về tính hợp lệ của chỉ số (metric validity), bởi vì bản chất của nó chính là như vậy.
:::

:::info Nếu bạn là nhà phát triển
Điểm số phương pháp của bạn có thể thay đổi một cách hợp lệ mà không cần mã nguồn của bạn thay đổi — một từ bị từ chối oan được đưa vào danh sách cho phép (allowlist), một bản dịch tham chiếu được sửa đổi, một lớp biến thể được khắc phục. Hãy thiết kế hệ thống để thích ứng với điều đó: ghim các phiên bản kho ngữ liệu trong các run card của bạn ([Tài liệu kỹ thuật Run Card](/docs/specifications/run-card)), theo dõi nhật ký thay đổi (changelog) của tập dữ liệu, và coi các sửa đổi của người nói bản xứ là tín hiệu lỗi đáng tin cậy nhất mà bạn có thể nhận được hoàn toàn miễn phí.
:::

## Xem thêm

- [Cách Người nói bản xứ được Trả phí](/docs/perspectives/how-speakers-get-paid) — cùng một thẩm quyền của người nói bản xứ, ở giai đoạn thiết lập điểm chuẩn
- [Từ Điểm chuẩn đến Sử dụng Hàng ngày (From Benchmark to Daily Use)](/docs/perspectives/from-benchmark-to-daily-use) — nơi các bản sửa lỗi gặp gỡ quy trình xuất bản
- [Chủ quyền Dữ liệu (Data Sovereignty)](/docs/sovereignty/data-sovereignty) — OCAP®, CARE, và Te Mana Raraunga, các nguyên tắc đằng sau thiết kế này