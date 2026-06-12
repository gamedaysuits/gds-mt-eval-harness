---
sidebar_position: 1
title: "Từ Pāṇini đến Transformers"
---
# Từ Pāṇini đến Transformers: Ngôn ngữ, Tính toán và Hành trình dịch thuật chưa hoàn tất

**Lịch sử của những ý tưởng đằng sau champollion**

---

> *"Khi nhìn vào một bài viết bằng tiếng Nga, tôi tự nhủ: 'Bài viết này thực chất được viết bằng tiếng Anh, nhưng nó đã được mã hóa bằng một số ký hiệu kỳ lạ. Bây giờ tôi sẽ tiến hành giải mã nó.'"*
> — Warren Weaver, 1949

---

## Giới thiệu

Giấc mơ về một cỗ máy có thể dịch thuật giữa các ngôn ngữ của con người thậm chí còn có trước cả khi máy tính ra đời. Theo một nghĩa nào đó, đây chính là bài toán nguyên bản của trí tuệ nhân tạo—lâu đời hơn cả các chương trình chơi cờ vua, hệ chuyên gia hay mạng nơ-ron. Khát vọng này thường được đặt trong khuôn khổ các câu chuyện ngụ ngôn châu Âu như Tháp Babel, nơi coi sự đa dạng ngôn ngữ là một hình phạt hoặc một vấn đề cần giải quyết, bỏ qua thực tế rằng các xã hội bản địa trước thời kỳ tiếp xúc đã từ lâu chung sống với sự đa dạng ngôn ngữ đáng kinh ngạc thông qua các ngôn ngữ thương mại tinh vi (như Chinook Jargon) và hệ thống ký hiệu (như Ngôn ngữ ký hiệu của người bản địa vùng đồng bằng - Plains Indian Sign Language) mà không hề tìm kiếm sự đồng nhất hóa toàn cầu.

Nhưng lịch sử dẫn đến thời điểm này—đến một thế giới nơi các mô hình ngôn ngữ lớn có thể dịch tiếng Pháp ở mức chấp nhận được nhưng lại gặp hiện tượng ảo giác tạo ra những nội dung vô nghĩa bằng tiếng Cree—không phải là một đường thẳng. Đó là sự giao thoa của ít nhất bốn sợi chỉ riêng biệt: nghiên cứu hình thức về ngôn ngữ, lý thuyết toán học về tính toán, cuộc cách mạng thống kê trong học máy, và một lịch sử đen tối hơn giải thích *tại sao* những ngôn ngữ cần đến công nghệ nhất lại chính là những ngôn ngữ mà công nghệ chưa hề tồn tại. Sợi chỉ thứ tư đó là lịch sử đàn áp ngôn ngữ thuộc địa và diệt chủng văn hóa—sự hủy diệt có chủ ý và mang tính hệ thống đối với các ngôn ngữ bản địa trên khắp các châu lục nơi các cường quốc châu Âu thiết lập ách thống trị. Nếu không hiểu rõ lịch sử đó, bài toán kỹ thuật này sẽ chỉ giống như một sự cố ngẫu nhiên do khan hiếm dữ liệu. Nhưng đó hoàn toàn không phải là một sự ngẫu nhiên.

Bài viết này sẽ lần theo cả bốn sợi chỉ từ nguồn gốc của chúng cho đến điểm hội tụ ở ngày nay. Phải thừa nhận rằng, cách tiếp cận này có phần mang tính định hướng lịch sử (Whiggish)—kể câu chuyện như thể mọi ngả đường đều luôn dẫn đến đây. Tất nhiên, lịch sử không hề biết trước mình sẽ đi về đâu. Nhưng các sợi chỉ là có thật, các mối liên kết là chân thực, và việc hiểu chúng là điều cần thiết để hiểu tại sao các dự án như champollion tồn tại, tại sao chúng được xây dựng theo cách hiện tại, và tại sao chúng lại quan trọng vào lúc này.

---

## I. Ngữ pháp của vạn vật: Từ Pāṇini đến Chomsky

### Ngữ pháp hình thức đầu tiên (khoảng thế kỷ thứ 4 TCN)

Câu chuyện không bắt đầu tại một trường đại học châu Âu mà ở Ấn Độ cổ đại, với một học giả tên là Pāṇini. Khoảng thế kỷ thứ 4 TCN, Pāṇini đã biên soạn tác phẩm *Aṣṭādhyāyī*—một hệ ngữ pháp tiếng Phạn bao gồm khoảng 4.000 quy tắc. Đây không phải là một hệ ngữ pháp theo nghĩa sư phạm lỏng lẻo. Đó là một ngữ pháp *sản sinh* (generative grammar): một tập hợp hữu hạn các quy tắc, về mặt nguyên lý, có khả năng tạo ra mọi phát ngôn hợp lệ trong ngôn ngữ đó.

Hệ thống của Pāṇini đã sử dụng những gì mà ngày nay chúng ta công nhận là các quy tắc viết lại hình thức (formal rewriting rules), với các biến số, đệ quy và thứ tự áp dụng. Nhà ngôn ngữ học Paul Kiparsky đã lập luận rằng *Aṣṭādhyāyī* là "ngữ pháp sản sinh hoàn chỉnh nhất của bất kỳ ngôn ngữ nào từng được viết ra" (Kiparsky, 1993). Nhà khoa học máy tính Gerard Huet đã chỉ ra rằng các quy tắc của Pāṇini có thể được mô hình hóa dưới dạng một bộ chuyển đổi trạng thái hữu hạn (finite-state transducer)—cùng một dạng thức tính toán mà hai mươi lăm thế kỷ sau, sẽ trở thành trung tâm của phân tích hình thái học cho các ngôn ngữ đa tổng hợp (polysynthetic languages).

Pāṇini không hề biết mình đang làm khoa học máy tính. Nhưng thực tế là ông đã làm điều đó.

### Bia đá Rosetta và sự ra đời của Ngôn ngữ học so sánh (1799)

Trong phần lớn lịch sử được ghi chép lại, việc nghiên cứu ngôn ngữ chủ yếu là nghiên cứu ngôn ngữ *của chính mình*—hoặc cùng lắm là nghiên cứu một ngôn ngữ thiêng liêng hoặc cổ điển cho các mục đích phụng vụ. Cuộc cách mạng trí tuệ khai sinh ra ngôn ngữ học hiện đại đã bắt đầu từ một phiến đá.

Bia đá Rosetta, được binh lính của Napoleon phát hiện vào năm 1799, khắc cùng một sắc lệnh bằng ba loại chữ viết: chữ tượng hình Ai Cập, chữ Demotic và tiếng Hy Lạp cổ đại. Việc Jean-François Champollion giải mã thành công chữ tượng hình vào năm 1822 không chỉ là một chiến thắng khảo cổ học. Nó đã chứng minh một nguyên lý mang tính nền tảng: các ngôn ngữ có thể được hiểu *thông qua nhau*. Dịch thuật không chỉ đơn thuần là một kỹ năng thực hành; nó là một phương pháp nghiên cứu khoa học.

### William Jones và Giả thuyết Ấn-Âu (1786)

Ngay cả trước Champollion, nhà ngữ văn học người Anh Sir William Jones đã trình bày bài giảng nổi tiếng của mình trước Hiệp hội Á châu xứ Bengal vào năm 1786, nhận xét rằng tiếng Phạn có mối quan hệ mật thiết với tiếng Hy Lạp và tiếng Latinh "cả về gốc động từ lẫn các dạng thức ngữ pháp, mạnh mẽ đến mức không thể là do ngẫu nhiên tạo ra". Jones đề xuất rằng cả ba ngôn ngữ này đều bắt nguồn từ một tổ tiên chung "mà có lẽ, giờ đây không còn tồn tại nữa".

Đây chính là sự ra đời của ngôn ngữ học lịch sử và so sánh. Nó xác lập rằng ngôn ngữ không phải là những thực thể tĩnh lặng, cô lập mà là thành viên của các ngữ hệ—liên kết với nhau bằng nguồn gốc, được định hình bởi thời gian và tuân theo các quy luật biến đổi có hệ thống. Theo cách riêng của mình, đây là một lý thuyết tiến hóa có trước Darwin hàng thập kỷ.

### Cây ngôn ngữ của August Schleicher (1861)

Chính August Schleicher, một nhà ngôn ngữ học người Đức, đã làm rõ mối liên hệ mang tính Darwin này. Vào năm 1861—chỉ hai năm sau tác phẩm *Nguồn gốc các loài* (On the Origin of Species)—Schleicher đã công bố mô hình *Stammbaum* (cây gia hệ) của các ngôn ngữ Ấn-Âu. Các sơ đồ của ông trông gần như không thể phân biệt được với cây phát sinh chủng loại trong sinh học. Ngôn ngữ, giống như các loài sinh vật, phân nhánh, phân tách và đôi khi bị tuyệt chủng.

Cây ngôn ngữ của Schleicher là một sự đơn giản hóa (các ngôn ngữ cũng *hội tụ* thông qua tiếp xúc, vay mượn và bồi dịch - creolization), nhưng mô hình này đã chứng minh được tính hiệu quả vượt trội. Nó thiết lập nguyên lý rằng sự đa dạng ngôn ngữ không phải là nhiễu ngẫu nhiên mà là dữ liệu có cấu trúc, có thể phân tích một cách hệ thống. Và nó ngầm đặt ra một câu hỏi vẫn là trung tâm trong dự án của chúng tôi: điều gì sẽ xảy ra với những nhánh ngôn ngữ đang dần biến mất?

### Ferdinand de Saussure và Kiến trúc của Ngôn ngữ (1916)

Cuộc cách mạng tiếp theo đến từ Ferdinand de Saussure, người có tác phẩm *Giáo trình ngôn ngữ học đại cương* (Cours de linguistique générale - được xuất bản sau khi ông qua đời vào năm 1916 từ ghi chép của sinh viên) đã đặt nền móng cho ngôn ngữ học cấu trúc. Saussure đã phân biệt rạch ròi giữa *langue* (hệ thống trừu tượng của một ngôn ngữ) và *parole* (lời nói thực tế). Ông lập luận rằng các ký hiệu ngôn ngữ mang tính *quy ước/độc đoán* (arbitrary)—từ "cây" không có mối liên hệ nội tại nào với thực thể cái cây—và ý nghĩa nảy sinh từ *sự khác biệt* trong một hệ thống, chứ không phải từ bất kỳ nội dung tự thân nào.

Sơ đồ then chốt của Saussure—hình bầu dục được chia đôi giữa *signifié* (cái được biểu đạt, khái niệm) và *signifiant* (cái biểu đạt, hình ảnh âm thanh), được liên kết bằng các mũi tên thể hiện mối quan hệ không thể tách rời của chúng—đã trở thành một trong những hình ảnh được tái bản nhiều nhất trong ngành nhân văn. Nó thiết lập nguyên lý rằng một ngôn ngữ là một *hệ thống của các hệ thống*, nơi mỗi yếu tố có được giá trị từ mối quan hệ của nó với tất cả các yếu tố khác.

Điều này có ý nghĩa sâu sắc đối với dịch thuật. Nếu ý nghĩa mang tính quan hệ và hệ thống, thì dịch thuật không đơn thuần là việc hoán đổi từ ngữ. Nó đòi hỏi phải hiểu toàn bộ kiến trúc của một ngôn ngữ. Hai ngôn ngữ có thể phân chia thế giới theo những cách khác biệt căn bản—một góc nhìn sau này sẽ được phát triển (và đôi khi bị cường điệu hóa) bởi Edward Sapir và Benjamin Lee Whorf.

### Sapir, Bloomfield và việc nghiên cứu các Ngôn ngữ Bản địa

Tại Bắc Mỹ, đầu thế kỷ 20 đã mang lại một truyền thống điền dã ngôn ngữ học khác biệt. Edward Sapir và Leonard Bloomfield đã làm việc sâu rộng với các ngôn ngữ bản địa—Sapir với tiếng Navajo, Nootka và nhiều ngôn ngữ khác; Bloomfield với tiếng Menomini và các ngôn ngữ Algonquian khác. Họ đã gặp phải những cấu trúc ngôn ngữ khác biệt hoàn toàn so với bất kỳ ngôn ngữ nào trong ngữ hệ Ấn-Âu.

Đặc biệt, Sapir đã phát triển một khung loại hình học phân loại các ngôn ngữ theo nhiều trục, bao gồm sự phân biệt quan trọng giữa ngôn ngữ *đơn lập/phân tích* (analytic - như tiếng Anh, nơi các từ có xu hướng ngắn và ý nghĩa được truyền tải bằng trật tự từ) và ngôn ngữ *đa tổng hợp* (polysynthetic - như tiếng Cree, nơi một từ duy nhất có thể mã hóa những gì tiếng Anh phải diễn đạt bằng cả một câu). Một dạng động từ tiếng Cree duy nhất có thể tích hợp chủ ngữ, tân ngữ, thì, thể, tính chứng thực (evidentiality) và một số yếu tố bổ nghĩa vào trong một từ phức tạp về mặt hình thái.

Công trình này đã xác lập hai sự thật vẫn là trung tâm trong dự án của chúng tôi. Thứ nhất: các ngôn ngữ trên thế giới đa dạng về mặt cấu trúc hơn nhiều so với bất kỳ mô hình lấy châu Âu làm trung tâm nào có thể gợi ý. Thứ hai: nhiều ngôn ngữ trong số này vốn đã bị đe dọa tuyệt chủng. Tuy nhiên, trong khi các nhà ngôn ngữ học cấu trúc thời kỳ đầu ghi chép lại sự phức tạp này, họ thường tham gia vào "nhân học cứu hộ" (salvage anthropology)—một mô hình học thuật mang tính bóc lột, coi người bản địa chỉ đơn thuần là "người cung cấp thông tin" để xây dựng sự nghiệp học thuật phương Tây. Cách tiếp cận này đã cắt đứt ngôn ngữ khỏi cội nguồn nhận thức luận của chúng, mở đường cho việc coi ngôn ngữ như dữ liệu tách rời, có thể khai thác được thay vì là các hệ thống sống động và mang tính quan hệ.

### Cuộc cách mạng Chomsky (1957)

Vào năm 1957, một nhà ngôn ngữ học 28 tuổi của MIT tên là Noam Chomsky đã xuất bản cuốn *Cấu trúc cú pháp* (Syntactic Structures), một cuốn sách mỏng nhưng đã tạo ra một tiếng vang lớn trong lĩnh vực này. Chomsky lập luận rằng mục tiêu của ngôn ngữ học phải là khám phá ra *ngữ pháp sản sinh* của một ngôn ngữ—một tập hợp hữu hạn các quy tắc có thể tạo ra tất cả và chỉ những câu đúng ngữ pháp của ngôn ngữ đó.

Thách thức hơn, Chomsky đã đề xuất *hệ phân cấp Chomsky* (Chomsky hierarchy): một sự phân loại các ngữ pháp hình thức theo sức mạnh tính toán của chúng. Hệ phân cấp này có quan hệ với bốn cấp độ:

- **Loại 3 (Chính quy - Regular)**: Được nhận dạng bởi các máy tự động hữu hạn (finite automata). Các mẫu đơn giản.
- **Loại 2 (Phi ngữ cảnh - Context-Free)**: Được nhận dạng bởi các máy tự động đẩy xuống (pushdown automata). Các cấu trúc đệ quy như các dấu ngoặc lồng nhau.
- **Loại 1 (Nhạy ngữ cảnh - Context-Sensitive)**: Được nhận dạng bởi các máy tự động giới hạn tuyến tính (linear bounded automata). Các phụ thuộc phức tạp hơn.
- **Loại 0 (Liệt kê đệ quy - Recursively Enumerable)**: Được nhận dạng bởi máy Turing. Bất cứ thứ gì có thể tính toán được.

Chomsky lập luận rằng các ngôn ngữ tự nhiên đòi hỏi ít nhất là ngữ pháp phi ngữ cảnh, và có thể còn hơn thế. Đây là một cây cầu trực tiếp nối liền ngôn ngữ học và lý thuyết toán học về tính toán. Chính những công cụ hình thức mà Alan Turing đã phát triển để lập luận về các giới hạn của tính toán giờ đây có thể được áp dụng cho ngôn ngữ của con người.

Chomsky cũng đề xuất ý tưởng về *Ngữ pháp phổ quát* (Universal Grammar)—rằng năng lực ngôn ngữ là bẩm sinh, rằng tất cả các ngôn ngữ của con người đều chia sẻ các đặc tính cấu trúc sâu sắc, và sự đa dạng của các dạng thức bề mặt chỉ che giấu một sự thống nhất tiềm ẩn. Điều này vẫn còn gây tranh cãi (nhiều nhà loại hình học và nhà chức năng học không đồng ý), nhưng các công cụ hình thức mà Chomsky giới thiệu—quy tắc cấu trúc cụm từ, ngữ pháp cải biến, và chính hệ phân cấp này—đã trở thành nền tảng của ngôn ngữ học tính toán.

---

## II. Giấc mơ về Dịch thuật Phổ quát

### Cỗ máy tư duy của Ramon Llull (1305)

Giấc mơ cơ giới hóa tư duy—và cùng với nó là giấc mơ dịch thuật cơ học—có lịch sử lâu đời một cách đáng kinh ngạc. Ramon Llull, một nhà thần học người Catalan vào thế kỷ 13, đã thiết kế hệ thống *Ars Magna*: một hệ thống các đĩa đồng tâm xoay được khắc các khái niệm cơ bản, mà sự kết hợp của chúng nhằm tạo ra tất cả các chân lý có thể. Các bánh xe của Llull, theo một nghĩa nào đó, là cỗ máy logic tổ hợp đầu tiên. Leibniz sau này đã trích dẫn Llull như một nguồn cảm hứng.

### Athanasius Kircher và tác phẩm Polygraphia Nova (1663)

Athanasius Kircher, nhà bác học vĩ đại dòng Tên, đã xuất bản tác phẩm *Polygraphia Nova et Universalis* vào năm 1663—a hệ thống "chữ viết phổ quát" nhằm cho phép giao tiếp vượt qua các rào cản ngôn ngữ. Hệ thống của Kircher gán các con số cho các khái niệm, sau đó có thể được giải mã sang bất kỳ ngôn ngữ nào bằng bảng tra cứu thích hợp. Về bản chất, đó là một ngôn ngữ trung gian (interlingua)—một sự biểu diễn ý nghĩa độc lập với ngôn ngữ.

Hệ thống này hoạt động không hiệu quả lắm. Nhưng *ý tưởng* vẫn tồn tại: rằng giữa hai ngôn ngữ bất kỳ luôn tồn tại một không gian khái niệm chung, và dịch thuật là việc ánh xạ thông qua không gian đó. Giả thuyết ngôn ngữ trung gian này không chỉ là một thử nghiệm khoa học thiếu sót; nó còn là một sự mở rộng nhận thức luận của sự kiểm soát thuộc địa, không có khả năng ánh xạ các bản thể luận khác biệt. Triết gia W.V.O. Quine sau này đã hình thức hóa thất bại này bằng khái niệm *tính bất định của dịch thuật* (indeterminacy of translation) (1960), lập luận rằng dịch thuật triệt để vốn dĩ mang tính bất định. Việc ánh xạ phổ quát, phi ngữ cảnh giữa các hệ thống ngôn ngữ khác biệt căn bản là một điều bất khả thi về mặt triết học, chứ không đơn thuần là một rào cản kỹ thuật.

### John Wilkins và Ngôn ngữ Triết học (1668)

Chỉ năm năm sau Kircher, nhà triết học tự nhiên người Anh John Wilkins đã xuất bản tác phẩm *An Essay towards a Real Character, and a Philosophical Language*—một nỗ lực nhằm tạo ra một ngôn ngữ có cấu trúc *phản chiếu hoàn hảo cấu trúc của thực tại*. Mỗi khái niệm sẽ được phân loại trong một hệ thống phân loại lớn, và tên của nó sẽ mã hóa vị trí của nó trong hệ thống phân loại đó.

Dự án của Wilkins đã thất bại (thực tại tỏ ra kháng cự lại sự phân loại ngăn nắp), nhưng nó đã dự báo trước một điều quan trọng: ý tưởng rằng ngôn ngữ có thể được *thiết kế kỹ thuật*, rằng mối quan hệ giữa từ ngữ và ý nghĩa có thể được thực hiện một cách hệ thống và rõ ràng. Theo một nghĩa sâu sắc, đây chính là những gì các nhà ngôn ngữ học tính toán làm khi họ xây dựng các bản thể luận (ontologies) và đồ thị tri thức (knowledge graphs).

### Leibniz và Characteristica Universalis

Gottfried Wilhelm Leibniz, người đã độc lập phát minh ra phép tính vi tích phân và thiết kế một máy tính cơ học, đã mơ về một *characteristica universalis*—một ngôn ngữ hình thức phổ quát mà trong đó mọi tri thức của con người đều có thể được biểu đạt—và một *calculus ratiocinator*—một cỗ máy có thể suy luận bằng ngôn ngữ đó. "Nếu có tranh chấp nảy sinh," Leibniz viết, "thì giữa hai nhà triết học sẽ không cần phải tranh luận nhiều hơn giữa hai kế toán viên. Bởi vì chỉ cần họ cầm bút chì trong tay, ngồi xuống trước bảng đá của mình và nói với nhau: Chúng ta hãy tính toán."

Leibniz cũng đã phát minh ra hệ nhị phân—hệ thống số mà nhiều thế kỷ sau sẽ trở thành ngôn ngữ của máy tính kỹ thuật số. Bài báo năm 1703 của ông *Explication de l'Arithmétique Binaire* đã chỉ ra rằng bất kỳ số nào cũng có thể được biểu diễn chỉ bằng cách sử dụng 0 và 1. Ông coi đây là sự phản chiếu của sự sáng tạo thiêng liêng (tạo ra vạn vật từ hư vô), nhưng nó đã chứng minh là nền tảng của mọi tính toán kỹ thuật số.

### Bản ghi nhớ của Warren Weaver (1949)

Kỷ nguyên hiện đại của dịch máy bắt đầu bằng một bản ghi nhớ. Vào tháng 7 năm 1949, nhà toán học kiêm nhà quản lý khoa học người Mỹ Warren Weaver đã viết thư cho Norbert Wiener, đề xuất rằng các máy tính điện tử mới có thể được áp dụng vào dịch thuật. Bản ghi nhớ của ông chứa đoạn văn đáng chú ý được trích dẫn ở phần mở đầu của bài viết này: ý tưởng rằng một văn bản tiếng Nga "thực chất được viết bằng tiếng Anh, nhưng... được mã hóa bằng một số ký hiệu kỳ lạ."

Ẩn dụ của Weaver được rút ra từ ngành giải mật mã thời chiến—ý tưởng rằng dịch thuật về cơ bản là một bài toán *giải mã*. Đây không đơn thuần là một sự so sánh tương đồng. Weaver gợi ý rằng chính các công cụ thống kê và lý thuyết thông tin được phát triển để bẻ khóa mật mã của kẻ thù có thể áp dụng được cho bài toán dịch thuật. Bản ghi nhớ này cực kỳ lạc quan, nhưng nó đã khởi động một chương trình nghiên cứu. Trong vòng năm năm, buổi trình diễn dịch máy đầu tiên đã diễn ra.

---

## III. Bộ máy của Tư duy: Tính toán và Thông tin

### George Boole và Đại số Logic (1854)

Vào năm 1854, George Boole đã xuất bản tác phẩm *An Investigation of the Laws of Thought*—một công trình đã giản lược lập luận logic thành các phép toán đại số. Boole chỉ ra rằng các mệnh đề logic có thể được thao tác bằng cách sử dụng các quy tắc tương tự như đại số, với phép AND tương ứng với phép nhân, OR tương ứng với phép cộng, và NOT tương ứng với phép bù.

Đại số Boolean dường như chỉ là một sự tò mò toán học vào thời điểm đó. Nó đã trở thành nguyên lý hoạt động của mọi mạch kỹ thuật số từng được chế tạo.

### Charles Babbage và Ada Lovelace (1837–1843)

Charles Babbage đã thiết kế (nhưng chưa bao giờ hoàn thành) Máy Phân tích (Analytical Engine)—một máy tính đa năng, chạy bằng hơi nước và hoạt động bằng cơ học. Khác với Máy Vi phân (Difference Engine) trước đó của ông (một máy tính chuyên dụng), Máy Phân tích có bộ nhớ ("the Store"), bộ xử lý ("the Mill"), rẽ nhánh có điều kiện và vòng lặp. Về mặt nguyên lý, nó đạt tính toàn vẹn Turing (Turing-complete).

Ada Lovelace, làm việc từ bản mô tả của cỗ máy này, đã viết một tập hợp các ghi chú chi tiết bao gồm những gì được coi là chương trình máy tính đầu tiên được công bố: một thuật toán để tính toán các số Bernoulli (Ghi chú G, 1843). Nhưng đóng góp sâu sắc nhất của Lovelace mang tính khái niệm. Bà nhận thấy rằng cỗ máy này có thể thao tác trên các *ký hiệu*, chứ không chỉ các con số. "Máy Phân tích dệt nên các mẫu đại số," bà viết, "giống như khung cửi Jacquard dệt nên hoa và lá." Hàm ý của điều này—rằng tính toán có thể được áp dụng cho bất kỳ lĩnh vực nào có cấu trúc hình thức, bao gồm cả ngôn ngữ—là vô cùng tiên tri.

### Alan Turing và Máy Vạn năng (1936)

Vào năm 1936, Alan Turing đã xuất bản bài báo "On Computable Numbers, with an Application to the Entscheidungsproblem"—một công trình đồng thời định nghĩa tính toán, chứng minh các giới hạn của nó và phát minh ra máy tính hiện đại (dưới dạng trừu tượng).

Nhận thức then chốt của Turing là *máy vạn năng* (universal machine): một cỗ máy duy nhất, khi được cung cấp các hướng dẫn phù hợp được mã hóa trên băng từ của nó, có thể mô phỏng *bất kỳ* cỗ máy nào khác. Điều này xác lập rằng không có sự khác biệt cốt lõi nào giữa phần cứng và phần mềm, giữa cỗ máy và chương trình. Một thiết bị duy nhất, nếu được lập trình đúng cách, có thể tính toán bất cứ thứ gì có thể tính toán được.

Công trình của Turing cũng xác lập các giới hạn của tính toán (bài toán dừng - halting problem) và đặt nền móng cho những khám phá sau này của ông về trí tuệ máy móc. Bài báo năm 1950 của ông "Computing Machinery and Intelligence", đề xuất Phép thử Turing (Turing Test) nổi tiếng, đã đóng khung câu hỏi về trí tuệ máy móc một cách rõ ràng thông qua *ngôn ngữ*: một cỗ máy là thông minh nếu, thông qua trò chuyện, nó không thể bị phân biệt với con người.

### Claude Shannon và Lý thuyết Thông tin (1948)

Vào năm 1948, Claude Shannon đã xuất bản bài báo "A Mathematical Theory of Communication" trên tạp chí *Bell System Technical Journal*—một công trình sáng lập nên lĩnh vực lý thuyết thông tin. Shannon chỉ ra rằng truyền thông có thể được mô hình hóa như một hệ thống: một *nguồn thông tin* tạo ra một *thông điệp*, được một *bộ phát* mã hóa thành một *tín hiệu*, truyền qua một *kênh* (chịu tác động của *nhiễu*), được một *bộ thu* giải mã ngược lại thành thông điệp cho một *điểm đích*.

Đóng góp then chốt của Shannon là khái niệm *entropy*—một thước đo mức độ không chắc chắn hoặc hàm lượng thông tin của một thông điệp. Ông đã chứng minh rằng đối với bất kỳ kênh truyền nào có mức nhiễu cho trước, luôn tồn tại một tốc độ tối đa mà tại đó thông tin có thể được truyền đi một cách đáng tin cậy (dung lượng kênh), và tốc độ này có thể đạt được bằng cách mã hóa đủ thông minh.

Mối liên hệ với dịch thuật là rất sâu sắc. Chính Shannon, trong một bài báo năm 1951, đã sử dụng lý thuyết thông tin để phân tích cấu trúc thống kê của tiếng Anh. Ông chỉ ra rằng văn bản tiếng Anh có tính dư thừa cao—rằng một người bản xứ, khi được cung cấp một chuỗi các chữ cái, có thể dự đoán chữ cái tiếp theo với độ chính xác cao. Sự dư thừa này là điều làm cho truyền thông trở nên mạnh mẽ trước nhiễu, nhưng nó cũng có nghĩa là *hàm lượng thông tin* của ngôn ngữ thấp hơn nhiều so với những gì số lượng ký hiệu thô gợi ý.

Warren Weaver ngay lập tức nhận thấy mối liên hệ: nếu dịch thuật là giải mã, và nếu cấu trúc thống kê của ngôn ngữ có thể được mô hình hóa, thì dịch thuật là một bài toán lý thuyết thông tin. Góc nhìn này phải mất hàng thập kỷ mới mang lại kết quả, nhưng khi đạt được, nó đã thay đổi hoàn toàn lĩnh vực này.

### Von Neumann và Máy tính Chương trình Lưu trữ (1945)

Báo cáo năm 1945 của John von Neumann về EDVAC (Electronic Discrete Variable Automatic Computer) đã mô tả những gì ngày nay chúng ta gọi là *kiến trúc von Neumann*: một máy tính có một bộ nhớ lưu trữ duy nhất cho cả dữ liệu và lệnh, một bộ xử lý trung tâm (CPU) và các cơ chế đầu vào/đầu ra. Kiến trúc này—dữ liệu và chương trình chia sẻ cùng một bộ nhớ, được xử lý tuần tự bởi một CPU—vẫn là thiết kế cơ bản của hầu hết mọi máy tính được sử dụng ngày nay.

Kiến trúc von Neumann đã làm cho phần mềm trở nên thực tế. Các chương trình có thể được lưu trữ, sửa đổi và thậm chí được tạo ra bởi các chương trình khác. Đây là điều kiện tiên quyết về mặt công nghệ cho mọi thứ diễn ra sau đó: trình biên dịch, hệ điều hành và cuối cùng là các khung mạng nơ-ron cung cấp sức mạnh cho dịch máy hiện đại.

---

## IV. Dịch máy: Bài toán AI đầu tiên

### Thử nghiệm Georgetown-IBM và Chiến tranh Lạnh (1954)

Vào ngày 7 tháng 1 năm 1954, các nhà nghiên cứu tại Đại học Georgetown và IBM đã trình diễn hệ thống dịch máy công cộng đầu tiên. Hệ thống đã dịch 60 câu tiếng Nga sang tiếng Anh bằng cách sử dụng vốn từ vựng gồm 250 từ và sáu quy tắc ngữ pháp. Các câu dịch được lựa chọn cẩn thận để nằm trong khả năng của hệ thống, nhưng buổi trình diễn đã tạo ra sự phấn khích to lớn.

Tờ *New York Times* đưa tin rằng thử nghiệm này báo hiệu một tương lai nơi "một bộ dịch điện tử nhấn nút" sẽ giúp toàn bộ tài liệu khoa học trên thế giới có thể truy cập ngay lập tức. Tuy nhiên, sự lạc quan công khai này đã che giấu thực tế vật chất về nguồn tài trợ và mục đích của dự án. Thử nghiệm Georgetown-IBM—và lĩnh vực dịch máy thời kỳ đầu nói chung—không được thúc đẩy bởi một khát vọng không tưởng về giao tiếp phổ quát. Nó được tài trợ bởi bộ máy quân sự và tình báo Hoa Kỳ (bao gồm CIA và DARPA) như một yêu cầu cấp bách trong Chiến tranh Lạnh nhằm giám sát và đánh chặn các văn bản khoa học và quân sự của Liên Xô.

Quan điểm coi ngôn ngữ là một "mật mã cần bẻ khóa" (như Weaver đã nói) gắn liền một cách chặt chẽ với hoạt động giám sát quân sự hóa. Các nhà nghiên cứu dự đoán rằng dịch máy sẽ là một bài toán được giải quyết trong vòng năm năm. Họ đã sai lầm trong hơn nửa thế kỷ.

### Báo cáo ALPAC và Mùa đông AI đầu tiên (1966)

Vào năm 1966, Ủy ban Cố vấn Xử lý Ngôn ngữ Tự động (ALPAC), do chính phủ Hoa Kỳ triệu tập, đã ban hành một báo cáo mang tính tàn phá. Sau khi xem xét một thập kỷ nghiên cứu dịch máy (MT), ALPAC kết luận rằng dịch máy chậm hơn, kém chính xác hơn và đắt đỏ hơn dịch thuật của con người, đồng thời khuyến nghị chuyển hướng nguồn tài trợ sang nghiên cứu cơ bản trong ngôn ngữ học tính toán.

Báo cáo ALPAC đã chấm dứt một cách hiệu quả nguồn tài trợ nghiên cứu MT tại Hoa Kỳ trong hơn một thập kỷ. Đó là "mùa đông AI" đầu tiên—một mô hình sẽ lặp lại: những lời hứa hẹn thái quá, kết quả khiêm tốn, sự vỡ mộng và sự sụp đổ của nguồn tài trợ.

Nhưng báo cáo cũng chứa đựng một góc nhìn sâu sắc hơn. Dịch máy đã thất bại, một phần vì ngôn ngữ khó hơn bất kỳ ai tưởng tượng. Cách tiếp cận dựa trên quy tắc (rule-based)—viết các quy tắc ngữ pháp rõ ràng để phân tích cú pháp và tạo câu—chỉ hoạt động trong các trường hợp đơn giản nhưng lại thất bại thảm hại trên văn bản thực tế. Ngôn ngữ quá mơ hồ, quá phụ thuộc vào ngữ cảnh, quá *sống động* để những quy tắc cứng nhắc có thể nắm bắt được.

### Dịch máy dựa trên quy tắc và dựa trên chuyển đổi (Thập niên 1970–1980)

Nghiên cứu vẫn tiếp tục, một cách lặng lẽ hơn, trong suốt những năm 1970 và 1980. Các hệ thống như SYSTRAN (vốn cung cấp sức mạnh cho các dịch vụ dịch thuật ban đầu của Ủy ban Châu Âu) đã sử dụng các từ điển lớn được xây dựng thủ công và các quy tắc chuyển đổi (transfer rules) để ánh xạ giữa các cặp ngôn ngữ. Các hệ thống này có thể tạo ra các bản dịch thô hữu ích cho các lĩnh vực hạn chế, nhưng chúng đòi hỏi nỗ lực kỹ thuật khổng lồ cho mỗi cặp ngôn ngữ, và chúng hiếm khi xử lý các văn bản không hạn chế một cách mượt mà.

Bài toán cơ bản đã rõ ràng: ngôn ngữ không phải là một mật mã. Bạn không thể dịch bằng cách tra từ trong từ điển và sắp xếp lại chúng theo các quy tắc ngữ pháp, bởi vì ý nghĩa phụ thuộc vào ngữ cảnh, vào tri thức thế giới, vào ý định của người nói, và vào toàn bộ lịch sử của một cuộc hội thoại. Cách tiếp cận ngôn ngữ trung gian (interlingua)—dịch thông qua một biểu diễn trừu tượng, độc lập với ngôn ngữ—về mặt lý thuyết thì rất thanh lịch nhưng về mặt thực tế lại bất khả thi. Không ai có thể định nghĩa được ngôn ngữ trung gian đó.

### Cuộc cách mạng Thống kê (Thập niên 1990)

Bước đột phá không đến từ các quy tắc tốt hơn mà đến từ dữ liệu tốt hơn. Vào cuối những năm 1980 và đầu những năm 1990, các nhà nghiên cứu tại IBM (Peter Brown, Stephen Della Pietra, Vincent Della Pietra và Robert Mercer) đã phát triển một loạt các mô hình thống kê cho dịch máy—các Mô hình IBM nổi tiếng từ 1 đến 5.

Nhận thức then chốt chính là ý tưởng cũ của Weaver, cuối cùng đã được thực hiện một cách chặt chẽ: dịch thuật như một quá trình giải mã. Cho một câu tiếng nước ngoài *f*, tìm câu tiếng Anh *e* sao cho tối đa hóa P(e|f). Theo định lý Bayes, điều này tương đương với việc tối đa hóa P(f|e) × P(e)—một *mô hình dịch* (khả năng câu tiếng nước ngoài này xuất hiện khi cho trước câu tiếng Anh này là bao nhiêu?) nhân với một *mô hình ngôn ngữ* (khả năng câu tiếng Anh này tự xuất hiện là bao nhiêu?).

Các mô hình IBM đã học các xác suất này từ các ngữ liệu song song (parallel corpora) lớn—các tập hợp văn bản tồn tại ở cả hai ngôn ngữ (như biên bản nghị viện Hansards của Canada, được xuất bản bằng cả tiếng Anh và tiếng Pháp). Không cần đến các quy tắc được xây dựng thủ công. Hệ thống đã học cách dịch bằng cách quan sát hàng triệu ví dụ về dịch thuật của con người.

Dịch máy thống kê (Statistical MT) hoạt động hiệu quả hơn đáng kể so với dịch máy dựa trên quy tắc đối với các ngôn ngữ có dữ liệu song song phong phú. Nó cũng giới thiệu một phần cơ sở hạ tầng quan trọng: **BLEU score** (Papineni và cộng sự, 2002), một chỉ số để tự động đánh giá chất lượng dịch thuật bằng cách so sánh đầu ra của máy với các bản dịch tham chiếu của con người. BLEU giúp việc đo lường tiến độ một cách định lượng và thực hiện các thử nghiệm quy mô lớn trở nên khả thi.

Nhưng dịch máy thống kê có một giả định chí mạng đi kèm: nó đòi hỏi ngữ liệu song song. Đối với các cặp ngôn ngữ lớn trên thế giới—Anh-Pháp, Anh-Trung, Anh-Tây Ban Nha—dữ liệu song song rất phong phú. Nhưng đối với đại đa số trong số 7.000 ngôn ngữ trên thế giới, nó đơn giản là không tồn tại.

### Cuộc cách mạng Nơ-ron: Seq2Seq, Attention, Transformers (2014–2017)

Sự chuyển đổi tiếp theo đến cùng với học sâu (deep learning). Vào năm 2014, Ilya Sutskever, Oriol Vinyals và Quốc Lê đã trình diễn các mô hình *sequence-to-sequence* (seq2seq) cho dịch máy: các mạng nơ-ron có thể đọc toàn bộ một câu bằng một ngôn ngữ và tạo ra bản dịch bằng một ngôn ngữ khác, mà không cần bất kỳ sự căn chỉnh rõ ràng hay bảng cụm từ nào.

Vào năm 2015, Dzmitry Bahdanau, Kyunghyun Cho và Yoshua Bengio đã giới thiệu *cơ chế chú ý* (attention mechanism)—cho phép bộ giải mã "nhìn lại" các phần khác nhau của câu nguồn trong khi tạo ra từng từ của bản dịch. Điều này đã cải thiện đáng kể hiệu suất trên các câu dài.

Và vào năm 2017, Vaswani và cộng sự tại Google đã xuất bản bài báo "Attention Is All You Need", giới thiệu kiến trúc *Transformer*. Transformer đã loại bỏ hoàn toàn tính đệ quy tuần hoàn (recurrence), xử lý toàn bộ các chuỗi song song bằng cách sử dụng cơ chế tự chú ý (self-attention). Nó huấn luyện nhanh hơn, dễ mở rộng hơn và tạo ra các bản dịch tốt hơn bất kỳ thứ gì trước đó.

Transformers đã dẫn trực tiếp đến các mô hình ngôn ngữ lớn (LLM) của những năm 2020: GPT, BERT, PaLM, LLaMA và các thế hệ kế cận của chúng. Các mô hình này, được huấn luyện trên lượng văn bản khổng lồ từ internet, có thể dịch thuật giữa hàng trăm cặp ngôn ngữ với độ trôi chảy đáng kinh ngạc.

Nhưng "độ trôi chảy đáng kinh ngạc" không đồng nghĩa với "độ chính xác đáng tin cậy". Và đối với các ngôn ngữ nghèo tài nguyên (low-resource languages) trên thế giới, tình hình tồi tệ hơn nhiều so với những gì chúng ta thấy.

---

## V. Một lịch sử khác: Ngôn ngữ, Quyền lực và Diệt chủng Văn hóa

Bốn phần trước đã kể câu chuyện về các ý tưởng—về các nhà ngữ pháp, nhà toán học và kỹ sư cùng xây dựng hướng tới dịch máy. Nhưng có một lịch sử khác, chạy song song, giải thích *tại sao* những ngôn ngữ cần đến công nghệ dịch thuật nhất lại chính là những ngôn ngữ mà công nghệ này không tồn tại. Đây không phải là câu chuyện về sự khan hiếm dữ liệu như một sự thật khách quan trung lập. Đó là câu chuyện về sự hủy diệt có chủ ý.

Lý do tiếng Cree vùng Đồng bằng (Plains Cree) không có sự hỗ trợ dịch máy không phải chủ yếu vì tiếng Cree là một ngôn ngữ khó đối với máy tính (mặc dù đúng là như vậy). Đó là bởi vì, trong hơn một thế kỷ, chính phủ Canada và Hoa Kỳ đã vận hành các chương trình mang tính hệ thống nhằm xóa sổ các ngôn ngữ bản địa khỏi miệng của trẻ em. Sự "khan hiếm dữ liệu" khiến cho dịch máy nghèo tài nguyên trở nên vô cùng khó khăn, phần lớn là *hệ quả hạ nguồn của nạn diệt chủng văn hóa*. Bất kỳ sự giải trình trung thực nào về lý do tại sao các ngôn ngữ này cần đến công nghệ đều phải đối mặt với lý do tại sao chúng bị đẩy đến bờ vực tuyệt chủng ngay từ đầu.

### Trước thời kỳ tiếp xúc: Một lục địa của các Ngôn ngữ

Sự đa dạng ngôn ngữ của châu Mỹ trước thời kỳ tiếp xúc là vô cùng kinh ngạc. Vào thời điểm tiếp xúc với người châu Âu, chỉ riêng Bắc Mỹ đã là nhà của khoảng 300 đến 600 ngôn ngữ riêng biệt, được tổ chức thành hàng chục ngữ hệ không liên quan đến nhau—sự đa dạng về nguồn gốc còn lớn hơn toàn bộ châu Âu. Nam Mỹ có thể đã có 1.500 ngôn ngữ hoặc hơn (Campbell, 1997). Úc có hơn 250 ngôn ngữ. Các đảo Thái Bình Dương, châu Phi cận Sahara và Đông Nam Á lục địa cũng đa dạng tương tự.

Đây không phải là những ngôn ngữ "nguyên thủy" hay "đơn giản". Nhiều ngôn ngữ có cấu trúc phức tạp nhất từng được ghi nhận chính là ngôn ngữ bản địa. Hình thái học đa tổng hợp của các ngôn ngữ Algonquian (bao gồm tiếng Cree, Ojibwe và Blackfoot), hệ thống thanh điệu của tiếng Navajo, sự đánh dấu tính chứng thực phức tạp của tiếng Quechua, các phụ âm tặc (click consonants) của các ngôn ngữ Khoisan—những điều này đại diện cho toàn bộ phạm vi khả năng của ngôn ngữ loài người. Chúng mã hóa các hệ thống tri thức tinh vi về quan hệ họ hàng, sinh thái, luật pháp, tâm linh và lịch sử. Mỗi ngôn ngữ là một thư viện—một ghi chép không thể thay thế về cách một cộng đồng hiểu và tổ chức thế giới.

Edward Sapir đã nhận ra điều này một cách rõ ràng. Viết vào năm 1921, ông nhận xét rằng "khi nói đến dạng thức ngôn ngữ, Plato cũng bình đẳng như người chăn lợn Macedonia, Khổng Tử cũng như người săn đầu người hoang dã ở Assam." Ngôn ngữ của các dân tộc bản địa không hề thấp kém hơn. Chúng khác biệt—và sự khác biệt của chúng chứa đựng tri thức mà không ngôn ngữ nào khác có được.

### Cơ chế của sự biến mất ngôn ngữ

Ngôn ngữ không biến mất vì những nguyên nhân tự nhiên. Chúng biến mất khi các điều kiện truyền dạy bị gián đoạn—khi trẻ em ngừng học chúng, khi người nói bị trừng phạt vì sử dụng chúng, khi các động lực xã hội và kinh tế thay đổi khiến việc nói ngôn ngữ thống trị trở thành điều kiện để sinh tồn.

Sự gián đoạn này có thể xảy ra dần dần, thông qua áp lực kinh tế và nhân khẩu học. Nhưng trên khắp thế giới thuộc địa, điều đó phần lớn là *có chủ ý*. Sự đàn áp các ngôn ngữ bản địa không phải là một tác dụng phụ của quá trình thực dân hóa. Nó là một mục tiêu chính sách được tuyên bố rõ ràng.

### Canada: Hệ thống Trường Nội trú (1831–1996)

Tại Canada, hệ thống Trường Nội trú dành cho người bản địa (Indian Residential School) đã hoạt động trong hơn 160 năm, với mục tiêu rõ ràng là xóa bỏ ngôn ngữ và văn hóa bản địa. Ước tính có khoảng 150.000 trẻ em thuộc các bộ tộc First Nations, Métis và Inuit đã bị tách khỏi gia đình và cộng đồng của họ để đưa vào các trường nội trú do chính phủ tài trợ và nhà thờ vận hành.

Chính sách trung tâm đã được Duncan Campbell Scott, Phó Tổng giám đốc phụ trách các vấn đề người bản địa, phát biểu với sự rõ ràng đến rợn người vào năm 1920: "Tôi muốn loại bỏ vấn đề người bản địa... Mục tiêu của chúng tôi là tiếp tục cho đến khi không còn một người bản địa nào ở Canada chưa được hấp thụ vào thể chế chính trị, và không còn câu hỏi về người bản địa cũng như không còn Bộ phụ trách người bản địa nữa."

Cơ chế thực hiện chính là ngôn ngữ. Trẻ em bị cấm nói tiếng mẹ đẻ của mình. Các hình phạt cho việc nói ngôn ngữ bản địa dao động từ đánh đập, biệt giam cho đến việc bị kim đâm qua lưỡi. Trẻ em đến trường khi đang nói tiếng Cree, Ojibwe, Inuktitut, Dene, Haida, hoặc bất kỳ ngôn ngữ nào trong số hàng chục ngôn ngữ khác. Chúng bị trừng phạt cho đến khi dừng lại.

Ủy ban Sự thật và Hòa giải Canada (2015) đã ghi chép lại tính chất hệ thống của cuộc tấn công này. Báo cáo cuối cùng của ủy ban kết luận rằng hệ thống trường nội trú đã cấu thành hành vi *diệt chủng văn hóa*—sự hủy hoại các cấu trúc và thực hành cho phép một nhóm người tiếp tục tồn tại như một cộng đồng. Ngôn ngữ là mục tiêu hàng đầu. Không có ngôn ngữ, các nghi lễ bị gián đoạn, lịch sử truyền miệng bị đứt gãy, hệ thống họ hàng trở nên khó hiểu, và sự truyền dạy tri thức giữa các thế hệ bị chấm dứt.

Ngôi trường nội trú do liên bang vận hành cuối cùng ở Canada đã đóng cửa vào năm 1996. Nhiều vị Trưởng lão (Elders), những người nói trôi chảy cuối cùng các ngôn ngữ của họ ngày nay, chính là những người sống sót từ các trường nội trú này. Sự trôi chảy của họ không đơn thuần là một tài nguyên ngôn ngữ. Đó là một hành động kháng cự.

### Hoa Kỳ: Các trường nội trú dành cho người bản địa (Thập niên 1860–1960)

Hoa Kỳ cũng vận hành một hệ thống song song. Đại úy Richard Henry Pratt, người sáng lập Trường Công nghiệp Carlisle dành cho người bản địa vào năm 1879, đã đặt ra cụm từ định hình cả kỷ nguyên này: "Giết phần bản địa, cứu phần người." Hơn 350 trường nội trú do chính phủ tài trợ đã hoạt động trên khắp Hoa Kỳ, với các chính sách gần như giống hệt ở Canada. Trẻ em bản địa bị cấm nói ngôn ngữ của mình, bị buộc phải nhận tên tiếng Anh và phải chịu sự xóa nhòa văn hóa mang tính hệ thống.

Một báo cáo năm 2022 của Bộ Nội vụ Hoa Kỳ đã xác định hơn 400 trường nội trú liên bang dành cho người bản địa tại 37 bang, ghi nhận cái chết của ít nhất 500 trẻ em trong hệ thống—một con số mà báo cáo thừa nhận gần như chắc chắn thấp hơn nhiều so với thực tế. Cuộc điều tra phát hiện ra rằng hệ thống này được thiết kế không chỉ để giáo dục mà còn để "đồng hóa văn hóa trẻ em bản địa bằng cách cưỡng chế di dời chúng khỏi gia đình và cộng đồng."

Hậu quả đối với ngôn ngữ là vô cùng thảm khốc. Trong số khoảng 300 ngôn ngữ bản địa được nói trên lãnh thổ mà sau này trở thành Hoa Kỳ, hơn một nửa hiện đã tuyệt chủng. Trong số những ngôn ngữ còn tồn tại, hầu hết có ít hơn 1.000 người nói trôi chảy, và nhiều ngôn ngữ có ít hơn 10 người. Dự án Ngôn ngữ bị Đe dọa (Endangered Languages Project) phân loại phần lớn các ngôn ngữ bản địa Mỹ còn tồn tại vào nhóm bị đe dọa "nghiêm trọng" hoặc "nguy cấp".

### Úc: Những thế hệ bị đánh cắp (1910–1970)

Tại Úc, các chính sách của chính phủ từ năm 1910 đến 1970 đã cưỡng chế tách trẻ em thổ dân và người đảo Torres Strait khỏi gia đình của họ. Những đứa trẻ này—được gọi là Những thế hệ bị đánh cắp (Stolen Generations)—đã bị đưa vào các cơ sở truyền giáo, khu bảo tồn và các gia đình da trắng nhận nuôi. Mục tiêu rõ ràng là đồng hóa: xóa bỏ bản sắc thổ dân trong vòng vài thế hệ.

Các ngôn ngữ thổ dân bị đàn áp trong các cơ sở truyền giáo và các tổ chức chính phủ. Trẻ em nói ngôn ngữ của mình đều bị trừng phạt. Báo cáo Đưa các em về nhà (Bringing Them Home) (1997), do Ủy ban Nhân quyền Úc thực hiện, đã ghi chép lại tính chất hệ thống của các vụ cưỡng chế di dời này và những tác động tàn phá của chúng đối với ngôn ngữ, văn hóa và gia đình.

Trong số ước tính 250 ngôn ngữ thổ dân Úc được nói vào thời điểm tiếp xúc với người châu Âu, hiện nay có chưa đầy 20 ngôn ngữ đang được truyền dạy cho trẻ em (Marmion và cộng sự, 2014). Hơn 100 ngôn ngữ đã tuyệt chủng hoàn toàn. Các ngôn ngữ còn lại tồn tại phần lớn nhờ vào nỗ lực của những người nói lớn tuổi làm việc với các nhà ngôn ngữ học và các tổ chức cộng đồng trong một cuộc đua với thời gian.

### Scandinavia: Các ngôn ngữ Sámi

Sự đàn áp các ngôn ngữ bản địa không chỉ giới hạn ở các quốc gia thuộc địa định cư ở bán cầu nam. Tại Na Uy, Thụy Điển và Phần Lan, trẻ em người Sámi đã phải chịu hệ thống trường nội trú (*internatskoler*) từ giữa thế kỷ 19 cho đến những năm 1960. Các ngôn ngữ Sámi bị cấm trong trường học; trẻ em bị trừng phạt nếu nói chúng. Chính sách "Na Uy hóa" (*fornorskingspolitikk*) của Na Uy nhằm mục đích rõ ràng là xóa bỏ tiếng Sámi và thay thế bằng tiếng Na Uy.

Trong số chín ngôn ngữ Sámi còn tồn tại, một số ngôn ngữ có ít hơn 500 người nói. Tiếng Ume Sámi có khoảng 20 người. Tiếng Pite Sámi có ít hơn 30 người. Các ngôn ngữ này tồn tại một phần nhờ vào các chương trình hồi sinh bắt đầu từ những năm 1970, bao gồm việc thành lập các trường học và phương tiện truyền thông bằng tiếng Sámi—những chương trình đã đến vừa kịp lúc đối với một số phương ngữ và quá muộn đối với những phương ngữ khác.

### Aotearoa New Zealand: Te Reo Māori

Tiếng Māori (te reo Māori) là ngôn ngữ đa số của vùng Aotearoa cho đến giữa thế kỷ 20. Các chính sách giáo dục thuộc địa của Anh, bắt đầu từ những năm 1860, đã dần dần gạt bỏ te reo ra ngoài lề trong các trường học. Đến những năm 1970, chưa đầy 20% người Māori nói trôi chảy ngôn ngữ này, và ngôn ngữ này đứng trước nguy cơ tuyệt chủng trong vòng một thế hệ.

Phản ứng của người Māori là một trong những phong trào hồi sinh ngôn ngữ sớm nhất và thành công nhất trên thế giới. Kōhanga reo (tổ ấm ngôn ngữ) dành cho trẻ em mầm non, được thành lập vào năm 1982, đã giúp trẻ sơ sinh và trẻ nhỏ đắm mình trong te reo ngay từ khi mới sinh. Các trường học giảng dạy bằng tiếng Māori (Kura kaupapa Māori) được thành lập tiếp sau đó. Các chương trình này, cùng với Đạo luật Ngôn ngữ Māori năm 1987 (đạo luật đưa te reo trở thành ngôn ngữ chính thức), đã giúp ổn định ngôn ngữ này—mặc dù những người nói trôi chảy vẫn chỉ chiếm một thiểu số trong dân số người Māori.

New Zealand cũng đã tạo ra một trong những khung quản trị dữ liệu bản địa quan trọng nhất: *Te Mana Raraunga*, Mạng lưới Chủ quyền Dữ liệu Māori. Khung quản trị này khẳng định rằng dữ liệu của người Māori—bao gồm cả dữ liệu ngôn ngữ—là một taonga (báu vật) chịu sự chi phối của các quyền hạn và trách nhiệm kaitiakitanga (quyền giám hộ). Nó đã trực tiếp định hình sự phát triển của các nguyên tắc CARE đối với quản trị dữ liệu bản địa và là tài liệu tham khảo nền tảng cho các cơ chế chủ quyền dữ liệu trong champollion.

### Mô hình chung: Ngôn ngữ là Mục tiêu của Quyền lực Thuộc địa

Các đặc điểm địa lý và văn hóa cụ thể có thể khác nhau, nhưng mô hình chung lại nhất quán một cách đáng kinh ngạc. Trên khắp Canada, Hoa Kỳ, Úc, Scandinavia và New Zealand—and ở nhiều nơi khác, từ Đài Loan đến Siberia hay vùng cao nguyên Andes—các quốc gia thuộc địa và hậu thuộc địa đã xác định ngôn ngữ bản địa là rào cản đối với sự đồng hóa và đưa chúng vào tầm ngắm để xóa sổ. Các công cụ ở khắp mọi nơi đều tương tự nhau: tách trẻ em khỏi gia đình, cấm sử dụng ngôn ngữ bản địa, trừng phạt các hành vi vi phạm và thưởng cho việc tiếp nhận ngôn ngữ thuộc địa.

Đây không phải là một chú thích lịch sử bên lề. Trường nội trú cuối cùng ở Canada đóng cửa vào năm *1996*. Trường nội trú dành cho người bản địa cuối cùng ở Hoa Kỳ đóng cửa vào những năm *1960*. Nhiều người sống sót qua các hệ thống này hiện vẫn còn sống. Chấn thương tâm lý này mang tính liên thế hệ. Và tổn hại về mặt ngôn ngữ vẫn đang tiếp diễn: các ngôn ngữ đã mất đi một thế hệ người nói trong kỷ nguyên trường nội trú giờ đây đang mất đi những vị Trưởng lão nói trôi chảy cuối cùng.

### Từ Diệt chủng Văn hóa đến "Sự khan hiếm dữ liệu"

Lịch sử này liên quan trực tiếp đến bài toán kỹ thuật của dịch máy. Khi các nhà khoa học máy tính mô tả một ngôn ngữ là "nghèo tài nguyên" (low-resource), họ thường có ý nói: có rất ít văn bản kỹ thuật số, ít ngữ liệu song song, ít từ điển và ít tập dữ liệu được gán nhãn. Cách đóng khung này mang tính trung lập, như thể sự khan hiếm dữ liệu là một hiện tượng tự nhiên, giống như một sa mạc ít mưa.

Nhưng thực tế không phải vậy. Sự "khan hiếm dữ liệu" của các ngôn ngữ bản địa là *hệ quả hạ nguồn* của các chính sách đàn áp ngôn ngữ. Những ngôn ngữ bị cấm trong trường học tạo ra ít văn bản viết hơn. Những ngôn ngữ có người nói bị trừng phạt vì sử dụng chúng sẽ phát triển ít ứng dụng mang tính thể chế hơn. Những ngôn ngữ bị mất đi một thế hệ truyền dạy tạo ra ít người nói song ngữ hơn để có thể xây dựng các ngữ liệu song song.

Đường ống dẫn từ diệt chủng văn hóa đến khan hiếm dữ liệu là trực tiếp:

1. **Đàn áp** → Trẻ em bị trừng phạt vì nói ngôn ngữ đó
2. **Gián đoạn truyền dạy** → Ít trẻ em học ngôn ngữ đó hơn
3. **Thu hẹp lượng người nói** → Ít người lớn sử dụng nó trong cuộc sống hàng ngày hơn
4. **Giảm sử dụng mang tính thể chế** → Ít tài liệu viết hơn, ít văn bản kỹ thuật số hơn
5. **Khan hiếm dữ liệu** → Các mô hình ML không có gì để huấn luyện
6. **Không có hỗ trợ dịch máy (MT)** → Ngôn ngữ trở nên vô hình trước công nghệ
7. **Đẩy nhanh sự suy thoái** → Công nghệ củng cố sự gạt bỏ ra ngoài lề mà chính sách đã bắt đầu

Đường ống này có nghĩa là bất kỳ dự án công nghệ nào làm việc với các ngôn ngữ bản địa đều kế thừa một bối cảnh chính trị và đạo đức, dù có thừa nhận nó hay không. Một hệ thống dịch máy coi dữ liệu ngôn ngữ Cree như nguyên liệu thô để các mô hình nạp vào, dù vô tình hay hữu ý, đang tiếp tục động lực mang tính bóc lột vốn đã bắt đầu từ các trường nội trú. Dữ liệu bị làm cho khan hiếm bởi bạo lực. Những người nói đã tạo ra lượng dữ liệu ít ỏi hiện có đã làm điều đó vượt qua những nghịch cảnh khổng lồ. Bất kỳ hệ thống nào sử dụng dữ liệu đó mà không có sự kiểm soát thực chất của cộng đồng đều đang làm trầm trọng thêm tổn hại ban đầu.

### Sự đồng lõa của Khoa học và Hệ tư tưởng Phương Tây

Điều quan trọng là phải nhận ra rằng khoa học và công nghệ không phải là những kẻ đứng ngoài cuộc vô tội trong dự án thuộc địa này; họ là những người tham gia tích cực. Hệ tư tưởng "Khai sáng" tìm cách phân loại, định lượng và tiêu chuẩn hóa thế giới thường coi các dân tộc bản địa và ngôn ngữ của họ chỉ đơn thuần là đối tượng nghiên cứu hoặc sự tò mò cho một ngành "nhân học cứu hộ". Thực hành mang tính bóc lột này đã khóa chặt tri thức trong các trường đại học phương Tây trong khi hầu như không làm gì để ngăn chặn bộ máy chính trị đang hủy hoại các cộng đồng đó.

Dự án này đứng ở thế đối lập hoàn toàn với các phương pháp luận như nghiên cứu giang mai Tuskegee hay nhân học ngôn ngữ mang tính bóc lột, vốn coi những người BIPOC (người da màu, người bản địa) như những đối tượng thử nghiệm hoặc những người cung cấp dữ liệu thô thụ động. Chúng tôi không ở đây để thử nghiệm trên người bản địa, khai thác tri thức của họ, hay áp đặt một hệ tư tưởng văn hóa phương Tây nguyên khối lên họ. Mục tiêu của chúng tôi là tạo điều kiện thuận lợi cho các phương thức nhận thức *của riêng họ* và các tiêu chuẩn giá trị *của riêng họ*. Chúng tôi cung cấp cơ sở hạ tầng; các cộng đồng ngôn ngữ tự xây dựng các tập kiểm thử (test sets), định nghĩa các chỉ số (metrics) và duy trì sự đồng thuận tham gia (buy-in). Nếu không có sự đồng thuận tham gia của họ, không có gì trong số này hoạt động được.

### Tại sao Lịch sử này định hình Thiết kế của Chúng tôi

Đây là lý do tại sao mô hình quản trị của champollion không phải là một tính năng—nó là nền tảng. Mỗi quyết định thiết kế lớn trong dự án là một *phản hồi trực tiếp* đối với lịch sử được mô tả ở trên. Mục tiêu là chủ quyền dữ liệu: hỗ trợ các cộng đồng trong việc duy trì, hồi sinh và quản trị các ngôn ngữ sống của họ hoàn toàn theo các điều khoản của riêng họ.

**Tại sao dữ liệu kiểm thử được mã hóa và nắm giữ bởi các quỹ tín thác cộng đồng.** Bởi vì dữ liệu ngôn ngữ bản địa đã bị khai thác, công bố và lợi dụng mà không có sự đồng ý trong hơn một thế kỷ. Ngôn ngữ học truyền giáo, chẳng hạn như các nỗ lực của Viện Ngôn ngữ học Mùa hè (SIL), trong lịch sử đã độc quyền hóa các ngữ liệu song song bản địa dưới một khung làm việc mang tính bóc lột và đồng hóa. Hơn nữa, không giống như nhiều dự án NLP hiện đại phụ thuộc nhiều vào các bản dịch Kinh Thánh làm ngữ liệu song song chính cho các ngôn ngữ nghèo tài nguyên, chúng tôi tuyên bố rõ ràng không sử dụng các bản dịch Kinh Thánh làm ngữ liệu. Tập kiểm thử được mã hóa, với các khóa chỉ do tổ chức quản trị của cộng đồng nắm giữ, là một cơ chế kỹ thuật giúp ngăn chặn các mô hình bóc lột lặp lại *về mặt kiến trúc*.

**Tại sao chúng tôi sử dụng thực thi trong môi trường cô lập (sandboxed execution) thay vì các tập kiểm thử mở.** Bởi vì một khi dữ liệu ngôn ngữ được công bố công khai, cộng đồng sẽ mất quyền kiểm soát nó vĩnh viễn. Các chuẩn đánh giá (benchmarks) ML truyền thống công bố các tập kiểm thử của họ—bất kỳ ai cũng có thể tải chúng xuống, huấn luyện trên đó hoặc sử dụng chúng cho bất kỳ mục đích nào. Việc cào dữ liệu AI hiện đại này đại diện cho một hình thức mới của "chủ nghĩa thực dân dữ liệu" (data colonialism) và "bao chiếm kỹ thuật số" (digital enclosure). Đối với các cộng đồng có ngôn ngữ gần như bị xóa sổ bằng bạo lực, việc mất quyền kiểm soát đối với các tài nguyên ngôn ngữ còn lại của họ không phải là một sự bất tiện nhỏ. Đó là sự tiếp nối trực tiếp của việc tước đoạt lãnh thổ trong lịch sử. Thực thi trong môi trường cô lập đảm bảo rằng dữ liệu của cộng đồng không bao giờ rời khỏi cơ sở hạ tầng của họ.

**Tại sao quyền sở hữu phương pháp được chuyển giao cho cộng đồng.** Bởi vì lịch sử "giúp đỡ" các cộng đồng bản địa, phần lớn, là lịch sử của những người bên ngoài xây dựng những thứ *về* người bản địa thay vì *cho* hoặc *cùng với* họ. Các bài báo học thuật được xuất bản, các khoản tài trợ được thu thập, sự nghiệp được thăng tiến—và cộng đồng không nhận được gì. Cơ chế chuyển giao quyền sở hữu đảm bảo rằng khi một kỹ sư ML xây dựng một phương pháp dịch thuật hoạt động hiệu quả cho tiếng Plains Cree, cộng đồng Plains Cree sẽ *sở hữu phương pháp đó*. Kỹ sư vẫn giữ được sự ghi nhận và đóng góp (credit và attribution). Cộng đồng giữ lại tài sản.

**Tại sao mô hình doanh thu gửi 90% về cho cộng đồng.** Bởi vì việc hồi sinh ngôn ngữ rất tốn kém, và các cộng đồng đang làm những công việc khó khăn nhất—các Trưởng lão giảng dạy, cha mẹ gửi con đến các trường học đắm mình ngôn ngữ (immersion schools), các nhà hoạt động vận hành các tổ ấm ngôn ngữ—đang bị thiếu kinh phí một cách kinh niên. Hơn nữa, chính cơ sở hạ tầng AI mà chúng ta sử dụng (ví dụ: trung tâm dữ liệu, khai thác khoáng sản, sử dụng nước) gây ra những tổn hại vật chất không cân xứng lên các vùng đất của người bản địa trên toàn cầu. Nếu một API dịch thuật tiếng Cree tạo ra doanh thu, 90% doanh thu đó nên được dùng để tài trợ cho các chương trình ngôn ngữ tiếng Cree. Công nghệ nên là một công cụ phục vụ các cộng đồng, chứ không phải là một cơ chế bóc lột giá trị từ họ.

**Tại sao chúng tôi nói "hướng tới OCAP®" (OCAP®-forward) thay vì "tuân thủ OCAP®" (OCAP®-compliant).** Các nguyên tắc OCAP® (Quyền sở hữu, Quyền kiểm soát, Quyền truy cập, Quyền sở hữu thực tế - Ownership, Control, Access, Possession) được phát triển bởi Trung tâm Quản trị Thông tin First Nations dành riêng cho các bối cảnh của First Nations. Các khung quản trị dữ liệu bản địa khác—CARE (Lợi ích tập thể, Quyền kiểm soát, Trách nhiệm, Đạo đức), Te Mana Raraunga (Chủ quyền dữ liệu Māori) và các nguyên tắc FAIR—giải quyết các mối quan tâm tương tự từ các vị thế văn hóa và pháp lý khác nhau. Chúng tôi không tuyên bố thực hiện đầy đủ OCAP®; quyết định đó thuộc về các cộng đồng First Nations. Chúng tôi nói rằng thiết kế của mình là *hướng tới OCAP®* (OCAP®-forward): nó được xây dựng để các cộng đồng *có thể* thực hiện quyền sở hữu, kiểm soát, truy cập và sở hữu thực tế đối với dữ liệu của họ và các công nghệ bắt nguồn từ đó. Kiến trúc này cho phép thực thi chủ quyền. Việc nó có đạt được chủ quyền hay không là do các cộng đồng quyết định.

**Tại sao nền tảng đánh giá chuẩn (benchmarks) các *phương pháp*, chứ không phải các *mô hình*.** Bởi vì các cộng đồng ngôn ngữ bản địa không nên phụ thuộc vào mô hình của bất kỳ tập đoàn đơn lẻ nào. Kiến trúc mở của một "phương pháp" có nghĩa là giải pháp thậm chí không cần phải là một LLM tốn kém và nặng nề về tài nguyên vật chất. Nó có thể là một hệ thống dựa trên quy tắc cực kỳ hiệu quả, do cộng đồng tự lưu trữ và chạy trên phần cứng máy tính truyền thống. Nếu phương pháp dịch thuật tốt nhất cho tiếng Cree sử dụng Gemini của Google hôm nay, cộng đồng sẽ có thể chuyển sang một giải pháp thay thế mã nguồn mở hoặc mang tính quyết định (deterministic) vào ngày mai mà không cần phải xây dựng lại mọi thứ. Việc đánh giá chuẩn ở cấp độ phương pháp đảm bảo rằng tài sản của cộng đồng là một *công thức*, chứ không phải là một sự phụ thuộc.

**Tại sao cộng đồng phải xây dựng cơ sở hạ tầng này ngay bây giờ.** Nghịch lý của việc tận dụng AI trong khi phê phán sự bóc lột vật chất của nó được giải quyết bằng một thực tế chiến lược khắc nghiệt: nếu bài toán này không được giải quyết bởi chính cộng đồng theo các điều khoản chủ quyền của riêng họ, nó chắc chắn sẽ bị "giải quyết" bởi Big Tech (Google, Meta, OpenAI) theo các điều khoản mang tính bóc lột. Ngay cả khi một tập đoàn khổng lồ cuối cùng xây dựng được một mô hình dịch thuật cho một ngôn ngữ bản địa nhất định, cộng đồng vẫn cần cơ sở hạ tầng đánh giá chuẩn độc lập, được cô lập của riêng mình để xác minh *khi nào* và *liệu* họ có thực sự thành công theo các tiêu chuẩn của cộng đồng hay không—và để đảm bảo cộng đồng nắm giữ được giá trị của sự thành công đó.

Đây không phải là chính trị được áp đặt khiên cưỡng vào công nghệ. Đây là công nghệ được thiết kế bởi những người hiểu rõ lịch sử.

---

## VI. Thời điểm hiện tại: 6.800 Ngôn ngữ bị bỏ lại phía sau

### Quy mô của Vấn đề

Trong số khoảng 7.000 ngôn ngữ sống được nói trên Trái Đất ngày nay, chưa đầy 200 ngôn ngữ nhận được bất kỳ sự hỗ trợ dịch máy nào. Hơn 6.800 ngôn ngữ còn lại hoàn toàn vô hình trước công nghệ—không phải vì chúng kém giá trị hơn, mà vì các cách tiếp cận thống kê và nơ-ron đang thống trị dịch máy hiện đại về cơ bản là cực kỳ *khát dữ liệu* (data-hungry). Chúng đòi hỏi hàng triệu câu song song để học hỏi. Đối với hầu hết các ngôn ngữ trên thế giới, những câu đó đơn giản là không tồn tại.

Những ngôn ngữ bị ảnh hưởng nhiều nhất chính xác là những ngôn ngữ bị đe dọa tuyệt chủng nghiêm trọng nhất: ngôn ngữ bản địa, ngôn ngữ thiểu số, các truyền thống truyền miệng với các ghi chép viết hạn chế. Đây là những ngôn ngữ có người nói thường là người cao tuổi, cộng đồng nhỏ và quyền lực chính trị ở mức tối thiểu. Chúng là những ngôn ngữ cần sự hỗ trợ của công nghệ nhất để bảo tồn và hồi sinh—và chúng lại là những ngôn ngữ mà công nghệ hiện tại ít hữu ích nhất.

### Thách thức từ Ngôn ngữ Đa tổng hợp

Vấn đề không chỉ đơn thuần là sự khan hiếm dữ liệu. Nhiều ngôn ngữ bị đe dọa tuyệt chủng nhất trên thế giới là ngôn ngữ *đa tổng hợp* (polysynthetic)—chúng có các hệ thống hình thái học vô cùng phức tạp, phá vỡ hoàn toàn các giả định của NLP tiêu chuẩn.

Hãy xem xét tiếng Plains Cree (nêhiyawêwin), một ngôn ngữ Algonquian được nói trên khắp các vùng thảo nguyên của Canada. Một động từ tiếng Cree duy nhất có thể mã hóa thông tin mà tiếng Anh phải trải rộng trên cả một mệnh đề: chủ ngữ, tân ngữ, thì, thể, tính chứng thực, tình thái (modality) và nhiều phạm trù ngữ pháp khác, tất cả được đóng gói vào một từ duy nhất thông qua một hệ thống tiền tố, hậu tố và các biến đổi nội bộ.

Điều này tạo ra một số vấn đề cho các cách tiếp cận dịch máy tiêu chuẩn:

1. **Thất bại trong phân tách từ (Tokenization failure).** Các bộ phân tách từ con (subword tokenizers) như BPE (Byte Pair Encoding), được thiết kế cho các ngôn ngữ phân tích như tiếng Anh, làm vỡ vụn các từ đa tổng hợp thành các mảnh vô nghĩa. Cấu trúc hình thái học bị phá hủy trước khi mô hình kịp nhìn thấy nó. BPE không hề trung lập; nó đại diện cho một nhận thức luận thuần túy theo chủ nghĩa kinh nghiệm, ở cấp độ bề mặt, xung đột sâu sắc với các hệ thống phân cấp hình thái học dựa trên quy tắc sâu sắc vốn có của các ngôn ngữ đa tổng hợp. Đó là một sự thiên vị về mặt kiến trúc tích cực tháo dỡ hình thái học cấu trúc.

2. **Bùng nổ tổ hợp (Combinatorial explosion).** Một ngôn ngữ đa tổng hợp có thể có hàng triệu dạng từ khả dĩ cho một gốc động từ duy nhất. Không một ngữ liệu huấn luyện nào, dù lớn đến đâu, có thể chứa nhiều hơn một phần rất nhỏ trong số đó. Các mô hình nơ-ron không có cách nào để *khái quát hóa* (generalize) cho các dạng từ chưa từng thấy.

3. **Ảo tưởng (Hallucination).** Các mô hình ngôn ngữ lớn, khi được yêu cầu dịch sang các ngôn ngữ đa tổng hợp, thường tạo ra các dạng từ không hợp lệ về mặt hình thái—những từ mà không người bản xứ nào từng tạo ra. Mô hình đã học các mẫu thống kê từ dữ liệu hạn chế nhưng không có sự hiểu biết về các quy tắc hình thái học của ngôn ngữ đó.

### Bộ chuyển đổi trạng thái hữu hạn: Cây cầu nối

Tuy nhiên, có một công nghệ xử lý tốt sự phức tạp về mặt hình thái: **Bộ chuyển đổi trạng thái hữu hạn** (Finite State Transducer - FST). FST là một thiết bị tính toán hình thức ánh xạ giữa một chuỗi đầu vào và một chuỗi đầu ra thông qua một chuỗi các chuyển đổi trạng thái. Đối với phân tích hình thái học, một FST có thể ánh xạ một dạng từ bề mặt sang cấu trúc hình thái học tiềm ẩn của nó (và ngược lại), xử lý toàn bộ sự phức tạp tổ hợp của hình thái học ngôn ngữ.

FST là hậu duệ trực tiếp của các quy tắc viết lại của Pāṇini. Chúng là ngữ pháp Loại 3 (chính quy) của Chomsky dưới dạng thức tính toán. Chúng là hiện thân sống động của mối liên kết giữa ngôn ngữ học hình thức và tính toán.

Khi kết hợp FST với các LLM, `champollion` thực hiện một sự tổng hợp triết học quan trọng: nó hòa giải truyền thống cấu trúc *duy lý* (các quy tắc) với mô hình thống kê *duy nghiệm* (xác suất) để chống lại các thiên vị đa số, khát dữ liệu của AI hiện đại.

Đối với các ngôn ngữ đa tổng hợp, FST có thể cung cấp một thứ mà các mô hình nơ-ron không thể: *xác minh mang tính quyết định* (deterministic verification). Cho một dạng từ, một FST có thể khẳng định chắc chắn liệu đó có phải là một dạng từ hợp lệ trong ngôn ngữ đó hay không—không phải theo kiểu xác suất, không phải "trông có vẻ đúng", mà là *có* hoặc *không*. Đây là câu trả lời cho câu hỏi cốt lõi ám ảnh dịch máy nơ-ron đối với các ngôn ngữ nghèo tài nguyên: *Làm thế nào để bạn xác minh một từ được tạo ra là có thật mà không cần con người tham gia vào quy trình (human in the loop)?*

Câu trả lời kỹ thuật là: bạn sử dụng ngữ pháp hình thức. Bạn sử dụng chính những công cụ mà Pāṇini đã phát minh ra hai mươi lăm thế kỷ trước, được mã hóa trong dạng thức tính toán mà Turing và Chomsky đã thực hiện một cách chặt chẽ.

Tuy nhiên, chúng ta phải nhận ra rằng sức mạnh mang tính quyết định này cũng mang lại những rủi ro riêng. Việc áp đặt một sự xác thực "có" hoặc "không" lên một ngôn ngữ truyền miệng, linh hoạt có nguy cơ áp đặt một Hệ tư tưởng Ngôn ngữ Tiêu chuẩn cứng nhắc. Khi một FST quy định điều gì là "đúng", nó có thể vô tình lặp lại chính tính quy chuẩn thuộc địa mà nó được thiết kế để né tránh—làm phẳng các biến thể phương ngữ, trừng phạt việc chuyển mã (code-switching) và áp đặt một ngữ pháp chuẩn hóa, đơn nhất lên một cộng đồng đa dạng. Bởi vì FST chỉ đại diện cho một chỉ số về tính chính xác hình thức, chủ nghĩa kinh nghiệm cứng nhắc của chúng cần phải được tiết chế. Đây chính xác là lý do tại sao cộng đồng phải là người nắm giữ ngòi bút. Cộng đồng thiết lập tiêu chuẩn, xây dựng các quy tắc và định nghĩa những gì máy móc chấp nhận là hợp lệ, thiết kế các FST để tạo không gian cho sự linh hoạt truyền miệng và các phương ngữ vùng miền. Ngữ pháp hình thức không phải là một chân lý phổ quát được truyền lại bởi các nhà khoa học máy tính; nó là một cơ sở hạ tầng được vận hành bởi chính những người nói.

### champollion: Nơi các Sợi chỉ Hội tụ

Đây là lúc dự án champollion bước vào câu chuyện. Nó nằm ở chính điểm hội tụ của tất cả các sợi chỉ mà chúng ta đã lần theo:

- **Từ Pāṇini**: Nguyên lý cho rằng ngôn ngữ có thể được mô tả bằng các quy tắc hình thức, sản sinh.
- **Từ Schleicher và Sapir**: Sự hiểu biết rằng các ngôn ngữ trên thế giới rất đa dạng, có cấu trúc và thường bị đe dọa tuyệt chủng.
- **Từ các trường nội trú và hậu quả của chúng**: Sự hiểu biết rằng "sự khan hiếm dữ liệu" không phải là một sự thật kỹ thuật trung lập mà là hệ quả của sự đàn áp ngôn ngữ có chủ ý—và bất kỳ công nghệ nào chạm đến các ngôn ngữ này đều phải được xây dựng với nền tảng là chủ quyền.
- **Từ Chomsky**: Hệ phân cấp hình thức của các ngữ pháp kết nối ngôn ngữ học với tính toán.
- **Từ Shannon**: Khung toán học để hiểu về truyền thông, nhiễu và tín hiệu.
- **Từ Turing và von Neumann**: Các máy vạn năng có thể thực thi bất kỳ hàm khả tính nào.
- **Từ Weaver và các Mô hình IBM**: Góc nhìn cho rằng dịch thuật có thể được xử lý như một bài toán thống kê.
- **Từ cuộc cách mạng Transformer**: Các mô hình nơ-ron mạnh mẽ có thể dịch thuật—nhưng chỉ khi chúng có đủ dữ liệu.
- **Từ truyền thống FST**: Các công cụ hình thức có thể xử lý sự phức tạp về mặt hình thái nơi các mô hình nơ-ron thất bại.
- **Từ OCAP®, CARE và Te Mana Raraunga**: Các khung quản trị đảm bảo công nghệ phục vụ các cộng đồng thay vì bóc lột từ họ.

champollion là một nền tảng được thiết kế để hướng năng lượng cạnh tranh của cộng đồng học máy vào các ngôn ngữ mà thị trường đã bỏ rơi. Nó cung cấp một cơ sở hạ tầng đánh giá chuẩn (benchmarking) nơi bất kỳ ai cũng có thể gửi một phương pháp dịch thuật—nơ-ron, dựa trên quy tắc, lai (hybrid) hoặc mới lạ—và được đánh giá theo các tiêu chuẩn nghiêm ngặt. Quan trọng là, nó sử dụng xác thực dựa trên FST để đảm bảo các dạng từ được tạo ra là hợp lệ về mặt hình thái, và nó dựa vào sự xác minh của người bản xứ như là dữ liệu thực tế khách quan (ground truth).

Nền tảng này thể hiện một số nguyên lý mà lịch sử này đã làm rõ:

**Không một cách tiếp cận đơn lẻ nào là đủ.** Lịch sử của dịch máy (MT) là lịch sử của các bước chuyển dịch mô hình (paradigm shifts)—từ quy tắc sang thống kê rồi đến mạng nơ-ron. Mỗi mô hình mới giải quyết được các vấn đề mà mô hình trước đó không thể, nhưng mỗi mô hình cũng có những điểm mù riêng. Đối với các ngôn ngữ đa tổng hợp nghèo tài nguyên, câu trả lời gần như chắc chắn là *lai* (hybrid): độ trôi chảy nơ-ron được ràng buộc bởi tính chính xác hình thức.

**Chủ quyền dữ liệu không phải là một tùy chọn—đó là một phản hồi mang tính cấu trúc đối với tổn hại trong lịch sử.** Như Phần V đã tài liệu hóa chi tiết, các ngôn ngữ bản địa không chỉ đơn thuần "nghèo dữ liệu" một cách ngẫu nhiên. Chúng bị làm cho khan hiếm bởi chính sách có chủ ý. Thiết kế hướng tới OCAP® của dự án—đảm bảo dữ liệu ngôn ngữ vẫn nằm dưới sự kiểm soát của các cộng đồng bản địa, các khóa giải mã được nắm giữ bởi các quỹ tín thác cộng đồng, quyền sở hữu thuật toán được chuyển giao cho người nói—không phải là một ý nghĩ nảy sinh sau cùng. Đó là một phản hồi trực tiếp đối với hàng thế kỷ thực hành mang tính bóc lột, từ việc ghi chép tài liệu thời kỳ trường nội trú bởi những người bên ngoài cho đến việc cào tập dữ liệu thời hiện đại. Kiến trúc này làm cho việc lặp lại các mô hình bóc lột này trở nên *bất khả thi về mặt kỹ thuật*.

**Mục tiêu dài hạn là sự hồi sinh.** Dịch thuật là *bãi thử nghiệm*, nhưng giải thưởng thực sự là sự hồi sinh ngôn ngữ thông qua giảng dạy. Các ngữ pháp hình thức và mô hình hình thái học được xây dựng cho dịch máy chính xác là những nền tảng kỹ thuật cần thiết cho việc học ngôn ngữ có sự hỗ trợ của máy móc. Nếu chúng ta có thể xây dựng một FST xác thực các dạng động từ tiếng Cree cho một hệ thống dịch thuật, chúng ta cũng có thể sử dụng FST đó để giúp một học sinh học cách chia động từ tiếng Cree.

### Tại sao lại là Thời điểm này

Chúng ta đang sống trong một thời điểm độc nhất vô nhị trong lịch sử công nghệ ngôn ngữ. Một số yếu tố đã hội tụ:

1. **Các công cụ mã nguồn mở đã trưởng thành.** Các bộ công cụ FST (như HFST và Foma), các khung dịch máy nơ-ron (như OpenNMT và Fairseq), và cơ sở hạ tầng đánh giá giờ đây có thể được lắp ghép bởi một đội ngũ nhỏ với chi phí tối thiểu.

2. **Hoạt động tổ chức cộng đồng đang tăng tốc.** Các cộng đồng ngôn ngữ bản địa ngày càng tinh tế hơn trong việc sử dụng công nghệ và khẳng định chủ quyền dữ liệu của họ. Các tổ chức như sáng kiến First Voices, Dự án Công nghệ Ngôn ngữ Bản địa Canada, và vô số nỗ lực do cộng đồng dẫn dắt đang xây dựng cơ sở hạ tầng con người mà chỉ riêng công nghệ không thể cung cấp.

3. **Các năng lực AI đã đạt đến một ngưỡng giới hạn.** Các mô hình ngôn ngữ lớn, mặc dù tự thân chúng không đủ cho dịch máy nghèo tài nguyên, có thể đóng vai trò là các thành phần mạnh mẽ trong các hệ thống lai—tạo ra các bản dịch ứng viên sau đó được xác minh và ràng buộc bởi các phương pháp hình thức.

4. **Chi phí đã sụp đổ.** Những gì từng đòi hỏi một phòng thí nghiệm của chính phủ vào năm 1954 hoặc một tập đoàn lớn vào năm 2000 giờ đây có thể được thực hiện bằng các khoản tín dụng điện toán đám mây và phần mềm mã nguồn mở. Điểm nghẽn không còn là công nghệ hay tiền bạc. Đó là *ý chí*.

Câu hỏi không phải là liệu công nghệ có thể được xây dựng hay không. Nó hoàn toàn có thể. Câu hỏi là liệu nó có được xây dựng một cách *đúng đắn* hay không—với sự quản trị đúng đắn, các động lực đúng đắn và sự tôn trọng đúng đắn đối với các cộng đồng mà nó hướng tới phục vụ.

Đó chính là câu hỏi mà dự án này tồn tại để trả lời.

---

## Tài liệu tham khảo

- Bahdanau, D., Cho, K., & Bengio, Y. (2015). Neural Machine Translation by Jointly Learning to Align and Translate. *ICLR*.
- Boole, G. (1854). *An Investigation of the Laws of Thought*. Walton and Maberly.
- Bringing Them Home: Report of the National Inquiry into the Separation of Aboriginal and Torres Strait Islander Children from Their Families. (1997). Australian Human Rights Commission.
- Brown, P., Della Pietra, S., Della Pietra, V., & Mercer, R. (1993). The Mathematics of Statistical Machine Translation. *Computational Linguistics*, 19(2).
- Campbell, L. (1997). *American Indian Languages: The Historical Linguistics of Native America*. Oxford University Press.
- Champollion, J.-F. (1822). *Lettre à M. Dacier relative à l'alphabet des hiéroglyphes phonétiques*.
- Chomsky, N. (1957). *Syntactic Structures*. Mouton.
- Chomsky, N. (1956). Three Models for the Description of Language. *IRE Transactions on Information Theory*, 2(3).
- Huet, G. (2006). Lexicon-directed Segmentation and Tagging of Sanskrit. In *Proceedings of the XIIth World Sanskrit Conference*.
- Jones, W. (1786). The Third Anniversary Discourse. *Asiatick Researches*, 1.
- Kiparsky, P. (1993). Paninian Linguistics. In R. E. Asher (Ed.), *The Encyclopedia of Language and Linguistics*. Pergamon.
- Kircher, A. (1663). *Polygraphia Nova et Universalis*.
- Leibniz, G. W. (1703). Explication de l'Arithmétique Binaire. *Mémoires de l'Académie Royale des Sciences*.
- Llull, R. (c. 1305). *Ars Magna*.
- Lovelace, A. (1843). Notes by the Translator (Note G). In L. F. Menabrea, *Sketch of the Analytical Engine Invented by Charles Babbage*.
- Marmion, D., Obata, K., & Troy, J. (2014). *Community, Identity, Wellbeing: The Report of the Second National Indigenous Languages Survey*. Australian Institute of Aboriginal and Torres Strait Islander Studies.
- National Research Council. (1966). *Language and Machines: Computers in Translation and Linguistics* (ALPAC Report). National Academy of Sciences.
- Papineni, K., Roukos, S., Ward, T., & Zhu, W.-J. (2002). BLEU: A Method for Automatic Evaluation of Machine Translation. *ACL*.
- Saussure, F. de. (1916). *Cours de linguistique générale* (C. Bally & A. Sechehaye, Eds.). Payot.
- Schleicher, A. (1861). *Compendium der vergleichenden Grammatik der indogermanischen Sprachen*.
- Shannon, C. E. (1948). A Mathematical Theory of Communication. *Bell System Technical Journal*, 27(3).
- Shannon, C. E. (1951). Prediction and Entropy of Printed English. *Bell System Technical Journal*, 30(1).
- Sutskever, I., Vinyals, O., & Le, Q. V. (2014). Sequence to Sequence Learning with Neural Networks. *NeurIPS*.
- Truth and Reconciliation Commission of Canada. (2015). *Honouring the Truth, Reconciling for the Future: Summary of the Final Report*. Government of Canada.
- Turing, A. M. (1936). On Computable Numbers, with an Application to the Entscheidungsproblem. *Proceedings of the London Mathematical Society*, 2(42).
- Turing, A. M. (1950). Computing Machinery and Intelligence. *Mind*, 59(236).
- Vaswani, A., et al. (2017). Attention Is All You Need. *NeurIPS*.
- von Neumann, J. (1945). *First Draft of a Report on the EDVAC*. University of Pennsylvania.
- Weaver, W. (1949). Translation. Memorandum, Rockefeller Foundation.
- Wilkins, J. (1668). *An Essay towards a Real Character, and a Philosophical Language*. Royal Society.
- U.S. Department of the Interior. (2022). *Federal Indian Boarding School Initiative Investigative Report*. Bureau of Indian Affairs.

---

*Tài liệu này là một phần của tài liệu dự án champollion. Nó được phát hành theo cùng một giấy phép với chính dự án.*