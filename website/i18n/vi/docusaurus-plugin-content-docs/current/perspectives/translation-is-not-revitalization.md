---
sidebar_position: 1
title: "Dịch thuật không phải là hồi sinh ngôn ngữ"
slug: '/perspectives/translation-is-not-revitalization'
description: "Những gì dịch máy có thể và không thể làm cho các ngôn ngữ đang bị đe dọa — được trình bày một cách thẳng thắn. MT là cơ sở hạ tầng cho các cộng đồng ngôn ngữ. Nó không bao giờ có thể thay thế việc con người trò chuyện với nhau."
related:
  - label: "How Speakers Get Paid"
    to: /docs/perspectives/how-speakers-get-paid
    kind: position
  - label: "From Benchmark to Daily Use"
    to: /docs/perspectives/from-benchmark-to-daily-use
    kind: position
    note: "The post-editing path from draft to published text"
  - label: "Data Sovereignty"
    to: /docs/sovereignty/data-sovereignty
    kind: doc
    note: "OCAP, CARE, and consent before deployment"
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
---
# Dịch thuật không phải là Hồi sinh Ngôn ngữ

> **Quan điểm.** Dịch máy chuyển đổi văn bản giữa các ngôn ngữ. Hồi sinh ngôn ngữ tạo ra những người nói mới. Đây là hai hoạt động khác nhau với các tiêu chí thành công khác nhau, và không có điểm số nào trên bảng xếp hạng có thể thay đổi điều đó. Chúng tôi xây dựng MT như một cơ sở hạ tầng phục vụ các mục tiêu của cộng đồng — tuyệt đối không phải là sự thế cho sự truyền dạy giữa các thế hệ. Trẻ em học ngôn ngữ từ con người, không phải từ máy móc.

Vào năm 2026, thật dễ dàng để tin rằng phần mềm có thể giải quyết mọi thứ, kể cả một ngôn ngữ đang dần mất đi người nói. Chúng tôi muốn làm rõ lý do tại sao niềm tin đó là sai lầm — và về những gì công nghệ dịch thuật *thực sự* có thể đóng góp một cách trung thực.

Bài viết này ra đời vì một nhà ngôn ngữ học mà chúng tôi mời phản biện dự án này đã đưa ra một lập luận rất mạnh mẽ: một hệ thống dịch thuật English→Cree hoàn hảo sẽ không giải quyết được vấn đề truyền dạy (trẻ em không được học ngôn ngữ ở nhà), vấn đề vị thế (tiếng Anh là ngôn ngữ của quyền lực kinh tế), hay vấn đề sư phạm (thiếu trường học nhúng ngôn ngữ và giáo viên được đào tạo). Nó thậm chí có thể làm cho mọi thứ tồi tệ hơn, bằng cách tạo ra ảo tưởng rằng "máy tính có thể nói tiếng Cree" và làm giảm đi tính cấp bách của việc truyền dạy giữa con người với nhau. Chúng tôi chấp nhận hầu hết những lời phản biện đó, và chúng tôi công bố phản hồi của mình ở đây thay vì che giấu nó.

---

## Những gì việc hồi sinh ngôn ngữ thực sự cần

Các tài liệu nghiên cứu về hồi sinh ngôn ngữ đều thống nhất ở một điểm: ngôn ngữ tồn tại khi chúng được truyền qua các thế hệ — khi cha mẹ, ông bà và cộng đồng nói ngôn ngữ đó với trẻ em, và trẻ em lớn lên nói lại bằng ngôn ngữ đó (Fishman 1991; Hinton & Hale 2001). Mọi thứ khác — trường học, truyền thông, từ điển, ứng dụng — chỉ hỗ trợ cho sự truyền dạy đó, bằng không chúng vô giá trị.

Không một hệ thống dịch thuật nào tham gia vào quá trình trao đổi đó. Một mô hình chuyển đổi tài liệu tiếng Anh sang tiếng Plains Cree không tạo ra một người nói mới. Nó không cung cấp nhân sự cho một lớp học nhúng ngôn ngữ, không đào tạo giáo viên, cũng không ngồi cùng một đứa trẻ bên bàn ăn. Nếu công việc của chúng tôi từng được mô tả là "cứu rỗi các ngôn ngữ", thì mô tả đó là sai và chúng tôi sẽ thẳng thắn phủ nhận điều đó.

## Những gì MT không thể làm

Nói một cách rõ ràng để không có sự mơ hồ về sau:

- **Nó không thể thay thế người nói.** Bản dịch đầu ra chưa được người nói lưu loát kiểm duyệt chỉ là một bản nháp, không phải là một văn bản hoàn chỉnh. [Quy tắc chấm điểm](/docs/specifications/scoring) của chính chúng tôi coi mọi điểm số tự động chỉ là một chỉ số đại diện; chỉ có sự đánh giá của con người mới xác nhận được khả năng sử dụng thực tế.
- **Nó không thể dạy ngôn ngữ mẹ đẻ.** Trẻ em tiếp thu ngôn ngữ thông qua các mối quan hệ và sự nhúng mình vào môi trường ngôn ngữ, chứ không phải qua các tài liệu được dịch thuật.
- **Nó có thể tạo ra một ảo tưởng có hại.** Một bản demo "nói" được một ngôn ngữ có thể tạo cảm giác rằng ngôn ngữ đó đã an toàn trong khi thực tế không phải vậy. Nguy cơ về vị thế này là có thật, và chúng tôi coi đó là một câu hỏi mở cần được nghiên cứu *cùng với* các cộng đồng, chứ không phải là một chủ đề truyền thông cần được xử lý.
- **Nó không thể quyết định bất cứ điều gì.** Việc một hệ thống dịch thuật có nên tồn tại cho một ngôn ngữ hay không, và nó được sử dụng ở đâu, là quyết định của cộng đồng — bao gồm cả quyết định không triển khai nó. Quyền kiểm soát đó được tích hợp vào kiến trúc [chuyển giao quyền sở hữu](/docs/sovereignty/ownership-transfer) và [chủ quyền dữ liệu](/docs/sovereignty/data-sovereignty), và nó bao gồm cả các bối cảnh cụ thể: một cộng đồng có thể chấp nhận MT cho các tài liệu chính thức nhưng từ chối sử dụng nó cho các tài liệu trong lớp học.

## Những gì MT thực sự có thể làm

Trong bối cảnh đó, có những đóng góp cụ thể và có giới hạn mà cơ sở hạ tầng dịch thuật mang lại — mỗi đóng góp đều phục vụ những người đang thực sự thực hiện công việc cốt lõi.

**1. Tăng hiệu suất cho các dịch giả đang quá tải.** Các văn phòng dịch thuật của cộng đồng phải đối mặt với số lượng tài liệu *cần* được dịch sang ngôn ngữ bản địa nhiều hơn mức mà các dịch giả con người có thể tự dịch từ đầu. Một bản nháp dịch máy sẽ chuyển đổi công việc từ "dịch mọi thứ" sang "kiểm duyệt và chỉnh sửa" — và các nghiên cứu có kiểm soát đã chỉ ra rằng việc hậu hiệu đính (post-editing) nhanh hơn đáng kể so với việc dịch từ đầu, trong khi chất lượng vẫn được duy trì hoặc cải thiện (Plitt & Masselot 2010; Green, Heer & Manning 2013). Chúng tôi mô tả chi tiết quy trình làm việc này trong bài viết [Từ Thử nghiệm đến Sử dụng Hàng ngày](/docs/perspectives/from-benchmark-to-daily-use). Lưu ý: các nghiên cứu đó được thực hiện trên các cặp ngôn ngữ giàu tài nguyên; chúng tôi chưa có bằng chứng tương đương cho các ngôn ngữ đa tổng hợp (polysynthetic languages), và đó là một phần những gì dự án này được thiết lập để đo lường.

**2. Đòn bẩy thực tế cho quyền ngôn ngữ.** Quyền được tiếp cận các dịch vụ chính phủ bằng ngôn ngữ bản địa đã được quy định trong luật pháp ở một số khu vực tài phán. Điều thường thiếu là năng lực thực tế để tạo ra các bản dịch với tốc độ mà bộ máy hành chính yêu cầu. Một cộng đồng có thể chuyển đổi một tài liệu chính sách dài 50 trang thành một bản dịch đã qua kiểm duyệt trong vài ngày thay vì vài tháng sẽ có vị thế đàm phán mạnh mẽ hơn. Công nghệ không tạo ra quyền lợi; nó làm cho quyền lợi đó khó bị phớt lờ hơn.

**3. Cơ sở hạ tầng ngôn ngữ có thể tái sử dụng.** Bộ phân tích hình thái học (FST) mà chúng tôi sử dụng để xác minh rằng đầu ra dịch thuật chứa các từ có thật — chứ không phải các từ bị ảo tưởng — mã hóa lý do *tại sao* mỗi dạng từ lại hợp lệ. Chính cơ chế đó là nền tảng cho các công cụ học tập: trình luyện chia động từ, công cụ hỗ trợ viết sửa lỗi, trình khám phá hình thái học. Công cụ xác minh và công cụ sư phạm là cùng một sản phẩm. Đây là một lộ trình, không phải là một lời hứa — các công cụ học tập cần được xây dựng, và việc chúng có được xây dựng hay không là quyết định của cộng đồng.

**4. Hỗ trợ cho người học ngôn ngữ thứ hai.** Hồi sinh ngôn ngữ không chỉ là việc trẻ em tiếp thu ngôn ngữ mẹ đẻ. Đó còn là những người lớn học nó như một ngôn ngữ thứ hai — những người có thể không bao giờ đạt đến mức độ lưu loát như các Trưởng lão (Elder-level) nhưng có thể đọc các tài liệu của cộng đồng, tham gia và hiểu biết, đồng thời nâng cao sự hiện diện của ngôn ngữ trước công chúng bằng cách sử dụng nó. Đối với nhóm đối tượng này, một công cụ hỗ trợ dịch thuật là một công cụ thực sự hữu ích, giống như từ điển vậy.

**5. Lý do để công việc được tài trợ và sở hữu tại địa phương.** Trong mô hình của chúng tôi, các phương pháp đã được chứng minh sẽ được [chuyển giao quyền sở hữu cho cộng đồng](/docs/sovereignty/ownership-transfer) và phần lớn doanh thu từ API sẽ chảy về cộng đồng ([mô hình kinh tế](/docs/sovereignty/economic-model)). Người nói được [trả tiền cho chuyên môn của họ](/docs/perspectives/how-speakers-get-paid), chứ không bị yêu cầu làm tình nguyện. Bản thân những điều đó cũng không phải là sự hồi sinh ngôn ngữ — nhưng nó hướng nguồn lực về phía những người đang thực hiện việc hồi sinh, thay vì lấy đi từ họ.

## Cách tiếp cận trung thực

Lĩnh vực này đã có một lịch sử lâu dài về các dự án công nghệ xuất hiện với những câu chuyện giải cứu hào nhoáng nhưng khi rời đi chỉ để lại các bài báo khoa học (Bird 2020). Chúng tôi cố gắng giữ một tuyên bố khiêm tốn hơn: **MT là cơ sở hạ tầng.** Cơ sở hạ tầng phục vụ các mục tiêu do người khác đặt ra. Đường sá không quyết định nơi bạn đi; công nghệ này không quyết định một ngôn ngữ có tồn tại hay không. Người nói, gia đình và cộng đồng mới là những người quyết định — và khuôn khổ [Thập kỷ Quốc tế về Ngôn ngữ Bản địa của UNESCO](https://idil2022-2032.org/) đã đúng khi đặt các dân tộc bản địa, chứ không phải các công cụ, vào vị trí trung tâm.

Nếu một cộng đồng kết luận rằng công nghệ dịch thuật giúp ích cho các mục tiêu của họ, chúng tôi muốn đó phải là phiên bản tốt nhất, có trách nhiệm giải trình cao nhất có thể — do họ sở hữu, được xác thực bởi chính những người nói của họ, và được triển khai theo các điều khoản của họ. Nếu một cộng đồng kết luận rằng nó không giúp ích gì, thì kết luận đó là một kết quả có giá trị của dự án này, chứ không phải là một thất bại. Cả hai vế của câu nói đó đều là những cam kết của chúng tôi.

---

## Điều này có ý nghĩa gì đối với bạn

:::info Nếu bạn là thành viên của cộng đồng
Dự án này sẽ không nói với bạn rằng một ứng dụng có thể cứu rỗi ngôn ngữ của bạn — nó không thể làm được điều đó. Những gì nó mang lại là có giới hạn: dịch tài liệu nhanh hơn dưới sự kiểm duyệt của người nói lưu loát, cơ sở hạ tầng mà cộng đồng của bạn có thể sở hữu hoàn toàn, và sự đền bù xứng đáng cho chuyên môn của người nói. Việc có sử dụng bất kỳ phần nào trong số đó hay không và sử dụng như thế nào là quyết định của cộng đồng bạn, bao gồm cả quyết định không sử dụng. Xem thêm [Dành cho các Cộng đồng Ngôn ngữ](/docs/community/for-language-communities) và [Báo cáo Lỗi và Sở hữu Bản sửa lỗi](/docs/perspectives/reporting-errors-and-owning-corrections).
:::

:::info Nếu bạn là một nhà nghiên cứu
Hãy coi "MT cho các ngôn ngữ đang bị đe dọa" là một tuyên bố về cơ sở hạ tầng, chứ không phải một tuyên bố về hồi sinh ngôn ngữ, và câu hỏi đánh giá của bạn sẽ thay đổi: không phải là "điểm BLEU có cao không?" mà là "điều này có giúp giảm bớt khối lượng công việc của những người đang thực hiện công việc thực tế một cách rõ rệt, theo các điều khoản của họ hay không?" [Thông số kỹ thuật benchmark](/docs/specifications/benchmark) và [Cách thức Hoạt động §8 (Mâu thuẫn và Hạn chế)](/docs/how-it-works#8-tensions-and-limitations) là nơi chúng tôi tự cam kết thực hiện theo tiêu chuẩn đó.
:::

:::info Nếu bạn là một nhà phát triển
Hãy xây dựng cho quy trình hậu hiệu đính (post-editing), chứ không phải cho bản demo. Người dùng phương pháp của bạn là một người nói lưu loát đang sửa một bản nháp, và lỗi nghiêm trọng nhất là các từ bị ảo tưởng trông có vẻ hợp lý đối với những người không biết tiếng — đó là lý do tại sao việc xác thực hình thái học là chốt chặn cho mọi thứ ở đây. Bắt đầu với [Gửi một Phương pháp](/docs/getting-started/submit-a-method) and [Từ Thử nghiệm đến Sử dụng Hàng ngày](/docs/perspectives/from-benchmark-to-daily-use).
:::

---

## Nguồn tài liệu

- Fishman, J. A. (1991). *Reversing Language Shift: Theoretical and Empirical Foundations of Assistance to Threatened Languages.* Multilingual Matters.
- Hinton, L., & Hale, K. (eds.) (2001). *The Green Book of Language Revitalization in Practice.* Academic Press.
- Plitt, M., & Masselot, F. (2010). "A Productivity Test of Statistical Machine Translation Post-Editing in a Typical Localisation Context." *The Prague Bulletin of Mathematical Linguistics*, 93, 7–16. [PDF](https://ufal.mff.cuni.cz/pbml/93/art-plitt-masselot.pdf)
- Green, S., Heer, J., & Manning, C. D. (2013). "The Efficacy of Human Post-Editing for Language Translation." *Proceedings of CHI 2013.* [Bài báo](https://idl.uw.edu/papers/post-editing)
- Bird, S. (2020). "Decolonising Speech and Language Technology." *Proceedings of COLING 2020*, 3504–3519. [Bài báo](https://aclanthology.org/2020.coling-main.42/)
- UNESCO. *International Decade of Indigenous Languages 2022–2032.* [idil2022-2032.org](https://idil2022-2032.org/)

## Xem thêm

- [Cách Người nói được Trả tiền](/docs/perspectives/how-speakers-get-paid) — mô hình đền bù, bằng những con số
- [Từ Thử nghiệm đến Sử dụng Hàng ngày](/docs/perspectives/from-benchmark-to-daily-use) — lộ trình hậu hiệu đính
- [Cách thức Hoạt động](/docs/how-it-works) — toàn bộ kiến trúc nền tảng, bao gồm §8 về những mâu thuẫn chúng tôi chưa giải quyết