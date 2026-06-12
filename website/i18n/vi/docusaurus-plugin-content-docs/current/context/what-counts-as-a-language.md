---
sidebar_position: 2
title: "Thế nào được tính là một ngôn ngữ ở đây?"
---
# Thế nào được tính là một ngôn ngữ ở đây?

> **Tóm tắt tổng quan.** Arena phân loại các ngôn ngữ theo tiêu chuẩn ISO 639-3, đánh giá benchmark từng ngôn ngữ riêng lẻ (không gộp chung theo nhóm ngôn ngữ vĩ mô - macrolanguage), công nhận ngôn ngữ ký hiệu là ngôn ngữ tự nhiên thực thụ, bao gồm các ngôn ngữ nhân tạo được ISO công nhận, loại trừ các ngôn ngữ lập trình, và hiển thị các tranh chấp về phân loại học mà không đứng về bên nào. Trang này giải thích từng lựa chọn và ý nghĩa của chúng đối với bảng xếp hạng.

Bất kỳ dự án nào thực hiện đánh giá benchmark dịch thuật trên hàng nghìn ngôn ngữ đều phải trả lời một câu hỏi xưa cũ nhưng khó khăn đến ngạc nhiên: thế nào được tính là một ngôn ngữ? Các nhà ngôn ngữ học từ lâu đã biết rằng ranh giới giữa "ngôn ngữ" (language) và "phương ngôn" (dialect) mang tính xã hội và chính trị nhiều như tính cấu trúc — câu nói đùa nổi tiếng rằng *"ngôn ngữ là một phương ngôn có quân đội và hải quân riêng"* đã được phổ biến bởi nhà ngôn ngữ học tiếng Yiddish Max Weinreich vào năm 1945 (ông ghi nhận câu nói này là của một khán giả trong một bài giảng của mình). Chúng tôi không thể né tránh câu hỏi này, vì vậy dưới đây là câu trả lời và lập luận của chúng tôi.

---

## Ngôn ngữ ký hiệu là ngôn ngữ. Chấm hết.

Ngôn ngữ ký hiệu là ngôn ngữ tự nhiên — với ngữ pháp hoàn chỉnh, được trẻ em tiếp thu một cách tự nhiên, và có cộng đồng ngôn ngữ đang hoạt động. Điều này đã được khẳng định trong ngôn ngữ học kể từ khi William Stokoe chứng minh vào năm 1960 rằng Ngôn ngữ Ký hiệu Mỹ (American Sign Language) có cùng loại cấu trúc nội tại như các ngôn ngữ nói, và sáu mươi năm nghiên cứu sau đó (Klima & Bellugi 1979; Sandler & Lillo-Martin 2006) chỉ càng làm sâu sắc thêm luận điểm này. ISO 639-3 cấp mã ngôn ngữ riêng lẻ cho các ngôn ngữ ký hiệu; Glottolog phân loại chúng cùng với các ngữ hệ nói. Danh mục của chúng tôi bao gồm hơn 160 ngôn ngữ ký hiệu, được gắn thẻ `modality: signed`.

Một số trong đó là các ngôn ngữ bản địa đang bị đe dọa: Ngôn ngữ Ký hiệu Thổ dân châu Mỹ vùng Đồng bằng (Plains Indian Sign Language - `psd`), từng là một ngôn ngữ chung (lingua franca) quan trọng giữa các bộ lạc trên khắp Bắc Mỹ trong lịch sử, hiện đang bị đe dọa nghiêm trọng (Davis 2010, *Hand Talk*). Sự mai một của ngôn ngữ ký hiệu *chính là* sự mai một của ngôn ngữ bản địa, và việc bảo tồn chúng nằm trong sứ mệnh của dự án này.

**Lưu ý trung thực về phạm vi.** Arena hiện tại chỉ đánh giá benchmark hệ thống dịch máy *dạng văn bản* (text-based). Dịch máy ngôn ngữ ký hiệu — làm việc với video, ngữ pháp không gian và các ngôn ngữ không có dạng viết được áp dụng rộng rãi — là một bài toán kỹ thuật khác biệt và phần lớn vẫn chưa có lời giải (xem Yin và cộng sự 2021, "Including Signed Languages in Natural Language Processing," ACL). Chúng tôi chưa hỗ trợ mảng này. Các mục ngôn ngữ ký hiệu trong danh mục của chúng tôi ghi rõ: **chưa được hỗ trợ — chứ không bao giờ là "không phải là một ngôn ngữ".**

## Có hai phương thức biểu đạt. Chữ viết không nằm trong số đó.

Ngôn ngữ tồn tại dưới hai phương thức biểu đạt chính: **nói** (spoken) và **ký hiệu** (signed). Chữ viết không phải là phương thức thứ ba — đó là một công nghệ được xây dựng dựa trên ngôn ngữ, và hầu hết các ngôn ngữ trên thế giới vẫn tồn tại tốt mà không cần một hệ thống chữ viết chuẩn hóa. Đó là lý do tại sao các thẻ ngôn ngữ của chúng tôi theo dõi chữ viết một cách riêng biệt (ngôn ngữ đó sử dụng hệ chữ viết nào, hoặc liệu nó có hoàn toàn không có chính tả chuẩn hóa hay không) và theo dõi một cách trung thực: đối với một nền tảng dịch máy dạng văn bản, việc một ngôn ngữ có dạng viết hay không là thông tin cực kỳ quan trọng chứ không phải là một ghi chú phụ — và một ngôn ngữ không có chữ viết không phải là một ngôn ngữ kém giá trị hơn.

## Ngôn ngữ nhân tạo: Được đưa vào. Ngôn ngữ lập trình: Bị loại ra.

Chúng tôi tuân theo đúng ranh giới của ISO 639-3. Tiêu chuẩn này chỉ chấp nhận một ngôn ngữ nhân tạo (constructed language) nếu nó là một ngôn ngữ hoàn chỉnh, được thiết kế cho giao tiếp của con người, có nền văn học và một cộng đồng đã truyền lại ngôn ngữ đó cho thế hệ người dùng thứ hai — và nó loại trừ rõ ràng các ngôn ngữ lập trình máy tính. Esperanto, với những người nói bản xứ, đủ điều kiện; Python thì không, vì không ai học Python như một ngôn ngữ mẹ đẻ từ cha mẹ mình. Danh mục của chúng tôi bao gồm hai mươi ngôn ngữ nhân tạo được ISO công nhận, được phân loại đúng như vậy, và không có ngôn ngữ lập trình nào.

## Chúng tôi đánh giá benchmark các ngôn ngữ riêng lẻ, không đánh giá theo nhóm chung

ISO 639-3 phân biệt giữa *ngôn ngữ riêng lẻ* (individual languages) và *ngôn ngữ vĩ mô* (macrolanguages) — các mã bao trùm như `cre` (tiếng Cree), `ara` (tiếng Ả Rập), hoặc `zho` (tiếng Trung) bao gồm nhiều ngôn ngữ riêng lẻ có quan hệ họ hàng gần gũi. Đơn vị đánh giá benchmark của Arena là **ngôn ngữ riêng lẻ**, vì một lý do vận hành thực tế: tài nguyên dịch thuật mang tính đặc thù theo từng biến thể. Một công cụ phân tích hình thái được xây dựng cho tiếng Plains Cree (`crk`) không thể tạo ra tiếng Moose Cree (`crm`); một ngữ liệu tiếng Ả Rập Ai Cập nói lên rất ít điều về chất lượng của một phương pháp dịch đối với tiếng Ả Rập Maroc. Một điểm số gắn liền với một mã bao trùm sẽ là một khẳng định vô căn cứ về các biến thể chưa từng thực sự được đánh giá — vì vậy chúng tôi không làm điều đó.

Các ngôn ngữ vĩ mô vẫn xuất hiện trong danh mục dưới dạng **trang trung tâm (hub pages)**: các trang điều hướng liên kết một danh tính bao trùm với các thành viên riêng lẻ của nó, phản ánh đúng quan sát của ISO rằng cả hai cấp độ danh tính đều có thật. Dưới cấp độ ngôn ngữ riêng lẻ, chúng tôi hiển thị thông tin về phương ngôn (dialect) và nguồn gốc (lineage) từ cây ngôn ngữ (languoid tree) của Glottolog (Hammarström & Forkel 2022), mô hình hóa các ngữ hệ, ngôn ngữ và phương ngôn thành một hệ thống phân cấp có thể điều hướng được.

## Khi các cơ quan có thẩm quyền bất đồng ý kiến, chúng tôi hiển thị cả hai

ISO 639-3 và Glottolog đôi khi có cách chia tách hoặc gộp nhóm khác nhau, và các cộng đồng đôi khi cũng không đồng ý với cả hai bên. Chúng tôi không phân xử. Các thẻ ngôn ngữ có phần *ghi chú phân loại học* (taxonomy notes) hiển thị các điểm bất đồng kèm theo nguồn tài liệu, và việc đặt tên sẽ tuân theo cộng đồng bất cứ khi nào cộng đồng thể hiện sự ưu tiên. Việc một biến thể có phải là "một ngôn ngữ" hay không, suy cho cùng, một phần là câu hỏi về danh tính — và các câu hỏi về danh tính thuộc về chính các cộng đồng đó, một nguyên tắc mà chúng tôi áp dụng từ các khung quản trị dữ liệu của người bản địa như OCAP®.

## Một hướng nghiên cứu: Benchmark như một công cụ đo lường

Một điều mà một đấu trường (arena) như thế này tạo ra, gần như là một sản phẩm phụ, là một loại bằng chứng mới về mức độ gần gũi thực sự của các biến thể ngôn ngữ *trên phương diện vận hành*. Nếu một phương pháp dịch thuật duy nhất, được giữ cố định, có thể phục vụ nhiều biến thể có liên quan với chất lượng có thể triển khai được, thì các biến thể đó sẽ nhóm lại với nhau (cluster) trên thực tế; nếu chúng yêu cầu các ngữ liệu riêng biệt và các phương pháp riêng biệt, chúng sẽ khác biệt về mặt vận hành — bất kể các quan điểm chính trị về việc đặt tên có là gì đi nữa. Điều này tương tự như các truyền thống thực nghiệm cũ hơn, từ kiểm tra mức độ dễ hiểu của văn bản được ghi âm (recorded-text intelligibility testing) cho đến các phép đo khoảng cách từ vựng tự động (automated lexical-distance measures), nhưng có sự điều chỉnh dựa trên thực tế triển khai.

Chúng tôi đưa ra điều này một cách cẩn trọng, như một hướng nghiên cứu hơn là một khẳng định chắc chắn. Kết quả chuyển giao phương pháp (method-transfer) bị nhiễu bởi quy mô ngữ liệu, lĩnh vực, chính tả và sự rò rỉ dữ liệu huấn luyện (training-data contamination), và việc phân cụm luôn phụ thuộc vào phương pháp và ngưỡng chất lượng cụ thể. Trên hết: tín hiệu này có thể *cung cấp thông tin* cho các cuộc thảo luận về ngôn ngữ và phương ngôn, nhưng nó không bao giờ có quyền phủ quyết cách một cộng đồng tự xác định ngôn ngữ của chính họ.

---

## Tài liệu tham khảo

- Davis, Jeffrey E. (2010). *Hand Talk: Sign Language among American Indian Nations.* Cambridge University Press.
- Dryer, Matthew S. & Martin Haspelmath, eds. (2013). *The World Atlas of Language Structures Online.* https://wals.info
- Hammarström, Harald & Robert Forkel (2022). "Glottocodes: Identifiers Linking Families, Languages and Dialects to Comprehensive Reference Information." *Semantic Web* 13(6).
- Haugen, Einar (1966). "Dialect, Language, Nation." *American Anthropologist* 68(4).
- ISO 639-3 Registration Authority. "Scope of denotation" and "Types of individual languages." https://iso639-3.sil.org/about/scope · https://iso639-3.sil.org/about/types
- Klima, Edward S. & Ursula Bellugi (1979). *The Signs of Language.* Harvard University Press.
- Sandler, Wendy & Diane Lillo-Martin (2006). *Sign Language and Linguistic Universals.* Cambridge University Press.
- Stokoe, William C. (1960). *Sign Language Structure.* Studies in Linguistics, Occasional Papers 8.
- Weinreich, Max (1945). "Der YIVO un di problemen fun undzer tsayt." *YIVO Bleter* 25(1).
- Yin, Kayo, Amit Moryossef, Julie Hochgesang, Yoav Goldberg & Malihe Alikhani (2021). "Including Signed Languages in Natural Language Processing." *Proc. ACL-IJCNLP 2021.* https://aclanthology.org/2021.acl-long.570/
- First Nations Information Governance Centre. *The First Nations Principles of OCAP®.* https://fnigc.ca/ocap-training/