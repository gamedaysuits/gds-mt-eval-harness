# Dịch máy: Tổng quan lĩnh vực (2013–2026)

*Lịch sử dạng tự sự dành cho bất kỳ ai mới bước chân vào lĩnh vực dịch máy (MT)*

---

## Mục lục

- [Phần 1: Cuộc cách mạng Neural (2013–2017)](#part-1-the-neural-revolution-20132017)
- [Phần 2: Bước chuyển mình đa ngữ (2018–2022)](#part-2-the-multilingual-turn-20182022)
- [Phần 3: Kỷ nguyên LLM (2022–2026)](#part-3-the-llm-era-20222026)
- [Phần 4: Bài toán tài nguyên thấp](#part-4-the-low-resource-problem)
- [Phần 5: Bộ chuyển đổi trạng thái hữu hạn và Hệ thống dựa trên luật](#part-5-finite-state-transducers-and-rule-based-systems)
- [Phần 6: Đo lường chất lượng — Bài toán đánh giá](#part-6-measuring-quality--the-evaluation-problem)
- [Phần 7: Toàn cảnh các tổ chức và cộng đồng](#part-7-the-institutional-landscape)
- [Phần 8: Những ranh giới mở](#part-8-open-frontiers)
- [Phụ lục A: Các bài báo nghiên cứu quan trọng](#appendix-a-key-papers)
- [Phụ lục B: Hội thảo và Cộng đồng](#appendix-b-conferences-and-communities)
- [Phụ lục C: Công cụ, Tập dữ liệu và Tài nguyên thực tế](#appendix-c-tools-datasets-and-practical-resources)
- [Phụ lục D: Thuật ngữ](#appendix-d-glossary)

---

## Phần 1: Cuộc cách mạng Neural (2013–2017)

### Chế độ cũ: Dịch máy thống kê

Để hiểu được cuộc cách mạng đã tái định hình ngành dịch máy vào giữa những năm 2010, trước tiên bạn cần hiểu những gì đã tồn tại trước đó — và tại sao nó lại sụp đổ.

Từ khoảng năm 2003 đến 2015, mô hình thống trị trong MT là **Dịch máy thống kê (Statistical Machine Translation - SMT)**, cụ thể là **SMT dựa trên cụm từ (phrase-based SMT)**. Ý tưởng cốt lõi cực kỳ đơn giản: thay vì viết các quy tắc về cách ngôn ngữ hoạt động, bạn thu thập một lượng lớn văn bản song ngữ (parallel text) — các tài liệu được con người dịch sang hai ngôn ngữ — và để các thuật toán thống kê tự học các mối tương quan. Hệ thống sẽ phân tách một câu nguồn thành các cụm từ chồng chéo (không phải các cụm từ ngữ pháp, mà là các phân đoạn n-gram tùy ý), tìm các bản dịch có khả năng thống kê cao nhất cho từng phân đoạn, rồi lắp ghép thành câu đích bằng cách sử dụng một **mô hình ngôn ngữ (language model)** để đảm bảo đầu ra trôi chảy.

Công cụ chủ lực của kỷ nguyên này là **Moses**, một bộ công cụ SMT mã nguồn mở được phát triển chủ yếu tại Đại học Edinburgh dưới sự dẫn dắt của Philipp Koehn, phát hành vào năm 2006. Moses đã trở thành "Linux" của nghiên cứu MT — hầu như mọi phòng thí nghiệm MT học thuật trên thế giới đều sử dụng nó. Người bạn đồng hành của nó, **cdec** (được phát triển bởi Chris Dyer tại Carnegie Mellon), cung cấp các khả năng tương tự với một cơ chế hình thức khác. Cùng nhau, những công cụ này đã định hình một thập kỷ nghiên cứu MT.

SMT dựa trên cụm từ hoạt động hiệu quả đến kinh ngạc đối với các cặp ngôn ngữ có dữ liệu song ngữ dồi dào và trật tự từ tương đồng — tiếng Anh–tiếng Pháp, tiếng Anh–tiếng Tây Ban Nha, tiếng Anh–tiếng Đức. Nhưng nó có những hạn chế sâu sắc về mặt cấu trúc. Hệ thống hoàn toàn không có khái niệm về ngữ nghĩa. Nó chỉ khớp mẫu trên các chuỗi bề mặt, lắp ghép các bản dịch từ các phân đoạn đã ghi nhớ. Nó gặp khó khăn với các phụ thuộc tầm xa (một đại từ tham chiếu đến một danh từ cách đó vài mệnh đề), với việc sắp xếp lại trật tự từ giữa các ngôn ngữ khác biệt về loại hình (ví dụ: tiếng Anh–tiếng Nhật, nơi động từ xuất hiện ở các vị trí đối lập), và với bất kỳ hiện tượng nào đòi hỏi sự trừu tượng hóa thực sự về cấu trúc ngôn ngữ. Mỗi cải tiến đều đòi hỏi kỹ thuật ngày càng phức tạp và rườm rà: các quy tắc sắp xếp lại từ được thiết kế thủ công, các đặc trưng thưa (sparse features), các mô hình ngôn ngữ khổng lồ. Kiến trúc này đã dần chạm trần giới hạn.

### Bước đột phá: Sequence-to-Sequence với Attention

Vết nứt đầu tiên trong mô hình SMT không đến từ cộng đồng MT, mà từ các nhà nghiên cứu học sâu (deep learning) đang giải quyết các bài toán mô hình hóa chuỗi (sequence modelling).

Vào tháng 9 năm 2014, **Dzmitry Bahdanau, Kyunghyun Cho, và Yoshua Bengio** tại Đại học Montréal đã công bố một bài báo mang tính bước ngoặt: ["Neural Machine Translation by Jointly Learning to Align and Translate"](https://arxiv.org/abs/1409.0473) (được trình bày tại ICLR 2015). Cải tiến cốt lõi chính là **cơ chế chú ý (attention mechanism)**.

Để hiểu tại sao điều này lại quan trọng, bạn cần biết bối cảnh trước đó. Chỉ vài tháng trước đó, Ilya Sutskever, Oriol Vinyals, và Quoc V. Le tại Google đã công bố bài báo ["Sequence to Sequence Learning with Neural Networks"](https://arxiv.org/abs/1409.3215) (NIPS 2014), chứng minh rằng một mạng neural với kiến trúc **encoder–decoder** (bộ mã hóa - bộ giải mã) có thể dịch các câu. Bộ mã hóa đọc câu nguồn theo từng từ và nén nó thành một vector có độ dài cố định duy nhất — một bản tóm tắt bằng số của toàn bộ đầu vào. Bộ giải mã sau đó sẽ tạo ra câu đích theo từng từ từ vector đó.

Phương pháp này rất trang nhã nhưng có một khuyết điểm chí mạng: vector duy nhất đó chính là một **nút thắt cổ chai (bottleneck)**. Tất cả thông tin trong một câu nguồn dài 30 từ phải được ép chặt vào một vector duy nhất gồm, ví dụ, 1.000 con số. Các câu ngắn được dịch tương đối tốt; các câu dài bị giảm chất lượng nghiêm trọng, vì mô hình đã quên các từ trước đó vào thời điểm nó hoàn thành việc mã hóa các từ phía sau.

Cơ chế chú ý của Bahdanau đã giải quyết vấn đề này. Thay vì nén toàn bộ câu nguồn vào một vector duy nhất, bộ giải mã được phép **nhìn lại** tất cả các trạng thái ẩn (hidden states) của bộ mã hóa — các biểu diễn trung gian tại mọi vị trí nguồn — và tự động gán trọng số xem vị trí nào là phù hợp nhất để tạo ra từng từ đích. Khi tạo ra từ tiếng Anh "cat", mô hình có thể tập trung chú ý mạnh nhất vào từ tiếng Pháp "chat" trong câu nguồn, ngay cả khi chúng nằm cách xa nhau trong câu. Mô hình đã tự học cách *gióng hàng* (align) các từ nguồn và đích như một phần của quá trình dịch, thay vì phụ thuộc vào một bản tóm tắt nén duy nhất.

Đây là cải tiến nền tảng. Attention không chỉ cải thiện MT; nó đã trở thành cơ chế trung tâm của hầu hết mọi tiến bộ sau này trong xử lý ngôn ngữ tự nhiên (NLP).

### Google chuyển sang Neural

Các kết quả học thuật của giai đoạn 2014–2015 rất ấn tượng nhưng chưa sẵn sàng để đưa vào vận hành thực tế (production). Điều đó đã thay đổi vào cuối năm 2016.

Vào tháng 9 năm 2016, một đội ngũ lớn tại Google do **Yonghui Wu** dẫn dắt đã công bố bài báo ["Google's Neural Machine Translation System: Bridging the Gap Between Human and Machine Translation"](https://arxiv.org/abs/1609.08144). Hệ thống này, được gọi là **GNMT** (Google Neural Machine Translation), là một kiến trúc encoder–decoder quy mô công nghiệp tích hợp cơ chế chú ý, được huấn luyện trên nguồn dữ liệu song ngữ khổng lồ của Google. Bài báo đã đưa ra một tuyên bố gây kinh ngạc: trên một số cặp ngôn ngữ nhất định, GNMT đã giảm lỗi dịch từ 55–85% so với hệ thống SMT dựa trên cụm từ hiện có của Google.

Vào tháng 11 năm 2016, Google bắt đầu âm thầm chuyển đổi Google Translate từ SMT dựa trên cụm từ sang GNMT cho các cặp ngôn ngữ chính. Quá trình chuyển đổi về cơ bản đã hoàn tất cho các cặp ngôn ngữ có tài nguyên cao vào năm 2017. Đối với người dùng, sự thay đổi này là vô cùng rõ rệt. Những bản dịch trước đây vốn bị coi là gượng gạo, rời rạc và đôi khi vô nghĩa đã trở nên trôi chảy hơn đáng kể — đôi khi đến mức đáng kinh ngạc. Kỷ nguyên mà "Google Dịch nói nhảm" là một trò đùa đang dần khép lại.

Phản ứng cạnh tranh diễn ra nhanh chóng. Vào tháng 8 năm 2017, **DeepL**, được thành lập bởi **Gereon Frahling** tại Cologne, Đức, đã ra mắt dịch vụ dịch thuật của mình. DeepL phát triển từ dự án tra cứu song ngữ Linguee và tạo nên sự khác biệt nhờ chất lượng dịch thuật vượt trội — đặc biệt là đối với các cặp ngôn ngữ châu Âu, nơi nó nhanh chóng tạo dựng được danh tiếng trong giới dịch giả chuyên nghiệp nhờ tạo ra đầu ra tự nhiên và giàu tính bản ngữ hơn Google. Mô hình kinh doanh của DeepL (freemium kết hợp với API trả phí) và sự tập trung vào chất lượng thay vì số lượng ngôn ngữ đã định hình vị thế thị trường của hãng sau này. Tính đến năm 2025, DeepL hỗ trợ khoảng 33 ngôn ngữ — ít hơn nhiều so với con số hơn 240 của Google, nhưng sở hữu định vị ưu tiên chất lượng hàng đầu.

### Transformer

Nếu cơ chế chú ý của Bahdanau là nền móng, thì **Transformer** chính là tòa nhà được xây dựng trên đó — và tòa nhà đó là một tòa nhà chọc trời.

Vào tháng 6 năm 2017, một nhóm gồm tám nhà nghiên cứu tại Google — **Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser, và Illia Polosukhin** — đã công bố bài báo ["Attention Is All You Need"](https://arxiv.org/abs/1706.03762) tại NIPS 2017. Tiêu đề này không hề cường điệu; đó là một tuyên bố chính xác về mặt kiến trúc. Trong khi các mô hình trước đây sử dụng mạng neural hồi quy (RNN) làm xương sống — xử lý các từ một cách tuần tự, từng từ một, giống như đọc một câu từ trái sang phải — thì Transformer loại bỏ hoàn toàn tính hồi quy và chỉ dựa vào cơ chế chú ý.

Những cải tiến then chốt bao gồm:

1. **Self-attention (Tự chú ý)**: Mỗi từ trong một câu sẽ chú ý đến mọi từ khác trong cùng một câu, tính toán các mối quan hệ một cách song song thay vì tuần tự. Điều này giúp nắm bắt các phụ thuộc tầm xa mà không gặp phải nút thắt cổ chai thông tin của RNN, và — quan trọng nhất — nó có thể song song hóa trên phần cứng hiện đại (GPU và TPU), giúp quá trình huấn luyện nhanh hơn rõ rệt.

2. **Multi-head attention (Chú ý đa đầu)**: Thay vì tính toán một mẫu chú ý duy nhất, mô hình tính toán đồng thời nhiều mẫu chú ý khác nhau ("đầu"), mỗi đầu có khả năng nắm bắt các loại quan hệ ngôn ngữ khác nhau — cú pháp, ngữ nghĩa, vị trí.

3. **Positional encoding (Mã hóa vị trí)**: Vì self-attention xử lý tất cả các từ cùng một lúc (không giống như RNN xử lý tuần tự), mô hình không có khái niệm vốn có về trật tự từ. Mã hóa vị trí — các hàm toán học được đưa vào đầu vào — sẽ cung cấp thông tin này.

Transformer không chỉ vượt trội hơn các mô hình dựa trên RNN trên các thang đo đánh giá dịch thuật. Nó còn có tốc độ huấn luyện **nhanh hơn nhiều bậc đại lượng** nhờ khả năng song song hóa. Điều này được cho là cũng quan trọng không kém gì việc cải thiện chất lượng: các nhà nghiên cứu giờ đây có thể thử nghiệm nhanh hơn, huấn luyện trên nhiều dữ liệu hơn và mở rộng quy mô lên các mô hình lớn hơn. Vòng lặp tích cực của việc mở rộng quy mô (scale) đã bắt đầu.

Trong vòng hai năm, kiến trúc Transformer đã trở thành nền tảng cho hầu hết mọi nghiên cứu tiên tiến (state-of-the-art) trong NLP — không chỉ MT, mà còn cả mô hình hóa ngôn ngữ, phân loại văn bản, trả lời câu hỏi, tóm tắt văn bản, và cuối cùng là các mô hình ngôn ngữ lớn (GPT, BERT, LLaMA) tái định hình toàn bộ bối cảnh AI rộng lớn hơn. Mọi hệ thống được thảo luận trong phần còn lại của tài liệu này đều được xây dựng trên Transformer.

### Bước ngoặt WMT 2016

**Conference on Machine Translation** (WMT), được tổ chức hàng năm dưới dạng một hội thảo song hành với các hội nghị NLP lớn, tổ chức các **nhiệm vụ chung (shared tasks)** mang tính cạnh tranh, nơi các nhóm nghiên cứu gửi các hệ thống MT của họ và được xếp hạng với nhau trên các tập kiểm thử chuẩn hóa. WMT là thứ gần gũi nhất với một bảng xếp hạng công khai trong lĩnh vực MT.

Tại **WMT 2016**, các hệ thống neural MT đã vượt trội một cách thuyết phục trước các hệ thống SMT dựa trên cụm từ trên hầu hết mọi cặp ngôn ngữ trong nhiệm vụ chung. Đây chính là thời điểm trọng tâm của lĩnh vực này dịch chuyển. Các nhà nghiên cứu vốn dành cả sự nghiệp để xây dựng các hệ thống dựa trên cụm từ bắt đầu chuyển hướng sang mô hình neural. Trong vòng hai năm, các công bố mới sử dụng SMT dựa trên cụm từ cho bất kỳ mục đích nào khác ngoài so sánh lịch sử về cơ bản đã ngừng xuất hiện. Moses, công cụ đã định hình cả một thập kỷ, đã chính thức lùi vào hậu trường.

Quá trình chuyển đổi diễn ra nhanh chóng một cách đáng kinh ngạc so với các tiêu chuẩn chuyển dịch mô hình học thuật — có lẽ chỉ mất từ ba đến bốn năm kể từ bài báo năm 2014 của Bahdanau cho đến sự thống trị gần như hoàn toàn của neural MT vào năm 2018. Đối với một nhà nghiên cứu mới bước vào lĩnh vực này ngày nay, SMT dựa trên cụm từ chỉ là bối cảnh lịch sử, không phải là một hướng nghiên cứu thực tế. Nhưng đó là bối cảnh thiết yếu, bởi vì các giả định, tiêu chuẩn đánh giá (benchmarks) và thói quen đánh giá của kỷ nguyên SMT vẫn còn vang vọng trong lĩnh vực này.

---

## Phần 2: Bước chuyển mình đa ngữ (2018–2022)

### Một mô hình, Nhiều ngôn ngữ

Thế hệ hệ thống neural MT đầu tiên là **song ngữ (bilingual)**: một mô hình cho mỗi cặp ngôn ngữ. Tiếng Anh–tiếng Pháp yêu cầu một mô hình; tiếng Pháp–tiếng Anh yêu cầu một mô hình riêng biệt. Việc mở rộng cách tiếp cận này lên N ngôn ngữ về mặt lý thuyết đòi hỏi N×(N−1) mô hình — một nút thắt cổ chai về mặt kỹ thuật và dữ liệu đã hạn chế neural MT chỉ hoạt động hiệu quả trên một số ít cặp ngôn ngữ có tài nguyên dồi dào.

Câu hỏi định hình giai đoạn 2018–2022 là: *liệu một mô hình neural duy nhất có thể học cách dịch giữa nhiều ngôn ngữ cùng một lúc không?* Câu trả lời hóa ra là có, đi kèm với những hệ quả sâu sắc và phức tạp.

### Biểu diễn xuyên ngôn ngữ: mBERT và XLM-R

Trước khi các mô hình dịch thuật đa ngữ xuất hiện, một phát hiện bất ngờ trong các mô hình *hiểu* ngôn ngữ đã tạo tiền đề cho bước tiến này.

Vào cuối năm 2018, Google đã phát hành **Multilingual BERT (mBERT)** — một mô hình Transformer duy nhất được huấn luyện trên văn bản Wikipedia từ 104 ngôn ngữ. BERT (Bidirectional Encoder Representations from Transformers) không phải là một mô hình dịch thuật; nó là một bộ mã hóa ngôn ngữ đa dụng, được huấn luyện để dự đoán các từ bị che (masked words) trong văn bản. Điều khiến các nhà nghiên cứu kinh ngạc là một đặc tính mới nổi (emergent property): mBERT đã tự phát triển các **biểu diễn xuyên ngôn ngữ (cross-lingual representations)** mà không cần được dạy một cách rõ ràng rằng các ngôn ngữ có liên quan đến nhau. Nếu bạn tinh chỉnh (fine-tune) mBERT trên một tác vụ phân loại cảm xúc tiếng Anh rồi áp dụng nó vào văn bản tiếng Pháp — hoàn toàn không có dữ liệu huấn luyện tiếng Pháp — nó vẫn hoạt động tốt một cách đáng ngạc nhiên. Hiện tượng này, được gọi là **chuyển giao xuyên ngôn ngữ zero-shot (zero-shot cross-lingual transfer)**, gợi ý rằng các mô hình đa ngữ đang học một loại không gian biểu diễn chung giữa các ngôn ngữ.

Vào năm 2020, **Alexis Conneau** và các đồng nghiệp tại Facebook AI Research (nay là Meta) đã thúc đẩy điều này xa hơn với **XLM-R** (Cross-lingual Language Model – RoBERTa). Được huấn luyện trên 2,5 terabyte dữ liệu CommonCrawl đã qua lọc trên 100 ngôn ngữ, XLM-R đã vượt trội hơn đáng kể so với mBERT trên các bài kiểm thử xuyên ngôn ngữ. Nó chứng minh rằng với đủ dữ liệu và dung lượng mô hình, một bộ mã hóa duy nhất có thể xây dựng các biểu diễn đa ngữ mạnh mẽ.

Bản thân các mô hình này không phải là công cụ dịch thuật, nhưng chúng đã cung cấp nền tảng khái niệm và kỹ thuật cho MT đa ngữ. Nếu một mô hình có thể học các biểu diễn chung trên 100 ngôn ngữ, thì một mô hình dịch thuật cũng phải có khả năng dịch giữa các ngôn ngữ đó — ít nhất là về mặt nguyên lý.

### Dịch thuật Many-to-Many: M2M-100

Các hệ thống MT đa ngữ truyền thống có một bí mật không mấy hay ho: chúng định tuyến hầu hết các bản dịch **thông qua tiếng Anh**. Dịch từ tiếng Bồ Đào Nha sang tiếng Nhật có nghĩa là trước tiên dịch tiếng Bồ Đào Nha sang tiếng Anh, sau đó dịch tiếng Anh sang tiếng Nhật. Cách tiếp cận "lấy tiếng Anh làm trung tâm" này mang tính thực dụng — vì hầu hết dữ liệu song ngữ đều có tiếng Anh ở một bên — nhưng nó lại tích tụ sai số qua các bước và áp đặt cấu trúc tiếng Anh lên mọi bản dịch.

Vào tháng 10 năm 2020, Facebook AI đã công bố **M2M-100** (Fan và các đồng nghiệp, ["Beyond English-Centric Multilingual Machine Translation"](https://arxiv.org/abs/2010.11125), JMLR 2021): một mô hình dịch thuật many-to-many (nhiều-sang-nhiều) bao phủ **100 ngôn ngữ và 2.200 hướng dịch** mà không cần định tuyến qua tiếng Anh. Đây là một bước đột phá về mặt khái niệm. Mô hình có thể dịch trực tiếp giữa, ví dụ, tiếng Bengal và tiếng Swahili, sử dụng dữ liệu song ngữ được khai thác từ web cho các cặp ngôn ngữ không chứa tiếng Anh.

M2M-100 đã chứng minh rằng việc sử dụng tiếng Anh làm cầu nối (English pivoting) không phải là một hạn chế bắt buộc của MT đa ngữ. Nhưng nó cũng bộc lộ những giới hạn của cách tiếp cận này: chất lượng cực kỳ không đồng đều giữa các cặp ngôn ngữ, với một số hướng dịch hầu như không thể sử dụng được. Khoảng cách giữa 'mô hình này *bao phủ* 2.200 hướng' và 'mô hình này *hoạt động tốt* trong 2.200 hướng' đã trở thành một chủ đề trung tâm.

### NLLB-200: No Language Left Behind

Nỗ lực MT đa ngữ đầy tham vọng nhất của Meta đã xuất hiện vào tháng 7 năm 2022 với **NLLB-200** (["No Language Left Behind: Scaling Human-Centered Machine Translation"](https://arxiv.org/abs/2207.04672), được công bố dưới dạng một bài báo nghiên cứu của Meta AI với hơn 200 đồng tác giả). Mục tiêu được thể hiện rõ ràng ngay trong tên gọi: xây dựng một mô hình duy nhất hỗ trợ 200 ngôn ngữ, đặc biệt tập trung vào các ngôn ngữ nghèo tài nguyên vốn bị các hệ thống MT thương mại bỏ qua trước đây.

Những đóng góp kỹ thuật của NLLB-200 là rất lớn:

- **Kiến trúc**: Một Transformer dày đặc (dense) và một biến thể **Mixture-of-Experts (MoE)**, nơi các tập hợp con khác nhau của các tham số mô hình sẽ kích hoạt cho các cặp ngôn ngữ khác nhau. Biến thể lớn nhất, NLLB-200-MoE-54B, có 54 tỷ tham số. Một phiên bản chắt lọc (distilled) 600 triệu tham số giúp việc triển khai trở nên khả thi.

- **Khai thác dữ liệu**: Nhóm nghiên cứu đã phát triển các công cụ tự động để khai thác các câu song ngữ từ các bản thu thập dữ liệu web (web crawls), bao gồm một mô hình nhận dạng ngôn ngữ (bao phủ hơn 200 ngôn ngữ) và một bộ lọc câu song ngữ. Quy trình này cực kỳ quan trọng để thu thập dữ liệu huấn luyện cho các ngôn ngữ có sự hiện diện tối thiểu trên web.

- **FLORES-200**: Một bộ tiêu chuẩn đánh giá chuẩn hóa bao phủ toàn bộ 200 ngôn ngữ với các câu được dịch một cách chuyên nghiệp. FLORES-200 đã trở thành một công cụ thiết yếu cho lĩnh vực này — trước đó, hầu như không có bộ tiêu chuẩn đánh giá nào tồn tại cho phần lớn các ngôn ngữ này.

- **Phát hành mở**: Cả mô hình và FLORES-200 đều được phát hành công khai, cho phép các nhà nghiên cứu trên toàn thế giới kế thừa và phát triển.

NLLB-200 là một cột mốc quan trọng, nhưng việc hiểu rõ các hạn chế của nó cũng quan trọng không kém. Chất lượng dịch thuật có sự chênh lệch rất lớn giữa các ngôn ngữ. Đối với các cặp ngôn ngữ có tài nguyên dồi dào (tiếng Anh–tiếng Pháp, tiếng Anh–tiếng Trung), mô hình hoạt động tốt nhưng không đạt mức tiên tiến nhất (state-of-the-art) so với các hệ thống chuyên dụng. Đối với các ngôn ngữ nghèo tài nguyên, chất lượng đầu ra dao động từ mức hữu ích cho đến hoàn toàn không thể sử dụng được, tùy thuộc vào lượng dữ liệu huấn luyện được khai thác nhiều hay ít. Mô hình cũng bộc lộ **lời nguyền đa ngữ (curse of multilinguality)**: việc thêm nhiều ngôn ngữ vào một mô hình có dung lượng cố định sẽ làm loãng chất lượng biểu diễn của từng ngôn ngữ. Các ngôn ngữ nghèo tài nguyên được hưởng lợi từ việc học chuyển giao (transfer learning - chia sẻ cấu trúc với các ngôn ngữ liên quan), nhưng các ngôn ngữ giàu tài nguyên thực tế có thể trở nên *tệ hơn* khi mô hình cố gắng phục vụ quá nhiều mục tiêu cùng lúc. Đây không đơn thuần là vấn đề về mở rộng quy mô — nó phản ánh sự mâu thuẫn cơ bản trong thiết kế mô hình đa ngữ.

### Bộ giải pháp Seamless

Meta tiếp tục thúc đẩy MT đa ngữ với dòng mô hình **Seamless** trong giai đoạn 2023–2024. **SeamlessM4T** ("Massively Multilingual and Multimodal Machine Translation", tháng 8 năm 2023) là một mô hình duy nhất xử lý **dịch giọng nói-sang-giọng nói, giọng nói-sang-văn bản, văn bản-sang-giọng nói và văn bản-sang-văn bản** trên khoảng 100 ngôn ngữ (với mức độ bao phủ khác nhau tùy theo từng phương thức). Điều này thể hiện sự hội tụ của các hướng nghiên cứu vốn tách biệt trước đây — nhận dạng giọng nói tự động (ASR), dịch thuật văn bản và tổng hợp giọng nói (TTS) — vào một hệ thống đa ngữ thống nhất.

Bộ giải pháp **Seamless Communication** tiếp theo đã bổ sung khả năng truyền phát trực tuyến (dịch thời gian thực) và dịch giọng nói biểu cảm (giữ nguyên các đặc tính giọng nói như cảm xúc và phong cách nói giữa các ngôn ngữ). Các hệ thống này hiện vẫn là các nguyên mẫu nghiên cứu chứ chưa phải là các công cụ sẵn sàng vận hành thực tế, nhưng chúng báo hiệu hướng đi của lĩnh vực này: đa phương thức (multimodal), đa ngữ và thời gian thực.

### Ý nghĩa thực tế của "Đa ngữ quy mô lớn"

Đối với một nhà nghiên cứu mới bước vào lĩnh vực này, điều quan trọng là phải phân biệt giữa **độ bao phủ ngôn ngữ (language coverage)** và **chất lượng ngôn ngữ (language quality)** của một mô hình. Một mô hình "hỗ trợ 200 ngôn ngữ" có thể cung cấp bản dịch xuất sắc cho 20 ngôn ngữ, đầu ra tạm chấp nhận được cho 50 ngôn ngữ và văn bản ngẫu nhiên vô nghĩa cho phần còn lại. Con số tiêu đề sẽ gây hiểu lầm nếu thiếu đi sự đánh giá chất lượng trên từng ngôn ngữ cụ thể.

**Lời nguyền đa ngữ** là thuật ngữ kỹ thuật cho vấn đề loãng dung lượng: một mô hình với các tham số hữu hạn không thể biểu diễn tất cả các ngôn ngữ tốt như nhau. Việc thêm nhiều ngôn ngữ sẽ có lợi cho các ngôn ngữ nghèo tài nguyên nhất (thông qua chuyển giao xuyên ngôn ngữ từ các ngôn ngữ liên quan) nhưng lại gây hại cho các ngôn ngữ giàu tài nguyên nhất (bằng cách tiêu tốn dung lượng lẽ ra có thể dành riêng cho chúng). Điều này tạo ra một sự mâu thuẫn trong thiết kế: bạn nên xây dựng một mô hình vạn năng duy nhất, hay nhiều mô hình chuyên dụng? Lĩnh vực này vẫn chưa có câu trả lời dứt điểm cho câu hỏi đó.

---

## Phần 3: Kỷ nguyên LLM (2022–2026)

### Khi AI đa dụng học cách dịch thuật

Sự xuất hiện của các mô hình ngôn ngữ lớn (LLM) — GPT-3.5/4, Gemini, Claude, LLaMA — đã tạo ra một tình huống kỳ lạ trong lĩnh vực MT. Các mô hình này không được huấn luyện chuyên biệt cho dịch thuật. Chúng được huấn luyện để dự đoán token tiếp theo trong các kho ngữ liệu văn bản khổng lồ, chủ yếu là tiếng Anh nhưng ngày càng đa ngữ hơn. Tuy nhiên, khi được nhắc (prompt) bằng các hướng dẫn như "Hãy dịch câu tiếng Pháp sau sang tiếng Anh", chúng lại tạo ra các bản dịch tốt đến kinh ngạc đối với các cặp ngôn ngữ giàu tài nguyên.

Điều này đặt ra cho lĩnh vực này một câu hỏi về mặt bản sắc: nếu AI đa dụng có thể dịch tốt như các hệ thống dịch thuật chuyên dụng, liệu "dịch máy" có còn là một lĩnh vực nghiên cứu riêng biệt? Câu trả lời, tính đến năm 2026, là có (với một số điều kiện) — nhưng mối quan hệ giữa nghiên cứu MT và sự phát triển của LLM đa dụng đã trở nên gắn kết vô cùng chặt chẽ.

### Những tiêu chuẩn đánh giá đầu tiên: LLM so với MT chuyên dụng

Việc đánh giá một cách hệ thống các LLM cho dịch thuật bắt đầu vào đầu năm 2023, ngay sau khi phát hành ChatGPT (tháng 11 năm 2022) và GPT-4 (tháng 3 năm 2023).

**Jiao và các đồng nghiệp (2023)**, trong bài báo ["Is ChatGPT A Good Translator? Yes With GPT-4 As The Engine"](https://arxiv.org/abs/2301.08745), đã đưa ra một đánh giá ban đầu. Phát hiện của họ đã thiết lập một mô hình hoạt động cực kỳ ổn định cho đến nay: các LLM **có khả năng cạnh tranh rất cao đối với các cặp ngôn ngữ châu Âu giàu tài nguyên** (tiếng Anh–tiếng Đức, tiếng Anh–tiếng Pháp, tiếng Anh–tiếng Trung) và **yếu hơn đáng kể đối với các cặp ngôn ngữ nghèo tài nguyên hoặc khác biệt về loại hình**. Họ cũng giới thiệu phương pháp **nhắc bắc cầu (pivot prompting)** — hướng dẫn mô hình dịch thông qua một ngôn ngữ trung gian — giúp cải thiện hiệu suất trên các cặp ngôn ngữ khó.

**Hendy và các đồng nghiệp (2023)** tại Microsoft ([arXiv:2302.09210](https://arxiv.org/abs/2302.09210)) đã tiến hành một đánh giá toàn diện hơn trên 18 hướng dịch. Kết luận của họ: các mô hình GPT cạnh tranh sòng phẳng với các hệ thống MT thương mại tiên tiến nhất đối với các cặp ngôn ngữ giàu tài nguyên nhưng có "khả năng hạn chế" đối với các ngôn ngữ nghèo tài nguyên.

Đến giai đoạn 2024–2025, bức tranh toàn cảnh đã trở nên rõ nét hơn. Đối với **các cặp ngôn ngữ giàu tài nguyên**, các LLM tốt nhất (GPT-4o, Gemini 2.5 Pro, Claude 3.5 Sonnet) đã ngang bằng hoặc vượt trội hơn các hệ thống MT chuyên dụng, đặc biệt là đối với các tác vụ đòi hỏi sự hiểu biết về ngữ cảnh, cách diễn đạt tự nhiên và tính mạch lạc ở cấp độ tài liệu (document-level coherence) — những lĩnh vực mà neural MT truyền thống (vốn xử lý các câu một cách cô lập) luôn gặp khó khăn. Đối với **các cặp ngôn ngữ nghèo tài nguyên**, các mô hình đa ngữ chuyên dụng như NLLB-200 và các hệ thống được xây dựng chuyên biệt của Google Translate vẫn hoạt động tốt hơn các LLM, thường là với khoảng cách đáng kể.

### BLOOM: Khoảnh khắc đa ngữ mở

Vào tháng 7 năm 2022, dự án hợp tác **BigScience** — một nỗ lực tình nguyện kéo dài một năm do Hugging Face điều phối với sự tham gia của hàng trăm nhà nghiên cứu trên toàn cầu — đã phát hành **BLOOM**: một mô hình ngôn ngữ đa ngữ truy cập mở với 176 tỷ tham số, bao phủ **46 ngôn ngữ tự nhiên và 13 ngôn ngữ lập trình**. Được huấn luyện trên kho ngữ liệu ROOTS bằng siêu máy tính Jean Zay ở Pháp, BLOOM là LLM đa ngữ truy cập mở thực sự khổng lồ đầu tiên.

BLOOM không phải là một công cụ dịch thuật chuyên dụng, nhưng ý nghĩa của nó đối với MT là rất lớn. Nó chứng minh rằng các mô hình mã nguồn mở có thể hỗ trợ hàng chục ngôn ngữ ở quy mô lớn, cung cấp nền tảng cho nghiên cứu đa ngữ bên ngoài các phòng thí nghiệm của các tập đoàn lớn. Biến thể được tinh chỉnh theo hướng dẫn (instruction-tuned) của nó, **BLOOMZ**, đã thể hiện khả năng khái quát hóa xuyên ngôn ngữ — khi được tinh chỉnh trên các tác vụ ở một ngôn ngữ, nó có thể thực hiện chúng ở các ngôn ngữ khác.

### LLaMA và sự bùng nổ của tinh chỉnh (Fine-Tuning)

Dòng mô hình **LLaMA** (Large Language Model Meta AI) của Meta, bắt đầu từ tháng 2 năm 2023, đã đi theo một con đường khác. LLaMA 1 chủ yếu tập trung vào tiếng Anh, với khả năng đa ngữ hạn chế. LLaMA 2 (tháng 7 năm 2023) có cải thiện đôi chút nhưng vẫn phân loại việc sử dụng ngoài tiếng Anh là "nằm ngoài phạm vi" (out-of-scope).

Bước ngoặt xuất hiện với **LLaMA 3** (tháng 4 năm 2024), khi dữ liệu huấn luyện được mở rộng gấp bảy lần và giới thiệu một từ vựng gồm 128.000 token — giúp cải thiện đáng kể việc mã hóa văn bản không phải tiếng Anh. LLaMA 3 chính thức hỗ trợ tám ngôn ngữ (tiếng Anh, tiếng Đức, tiếng Pháp, tiếng Ý, tiếng Bồ Đào Nha, tiếng Hindi, tiếng Tây Ban Nha, tiếng Thái) với chất lượng khác nhau cho nhiều ngôn ngữ khác.

Tầm quan trọng của LLaMA đối với MT không nằm nhiều ở khả năng dịch trực tiếp của nó, mà nằm ở vai trò là một **mô hình nền tảng cho việc tinh chỉnh (foundation model for fine-tuning)**. Cả hai LLM dịch thuật chuyên dụng được thảo luận dưới đây — Tower và ALMA — đều được xây dựng trên nền tảng LLaMA. Việc công khai trọng số (open weights) đã tạo ra một hệ sinh thái phát triển mạnh mẽ của các biến thể chuyên dụng.

### Các LLM được xây dựng chuyên biệt cho dịch thuật: Tower và ALMA

Sự phát triển đáng chú ý nhất trong giai đoạn 2023–2024 là sự xuất hiện của các LLM được tinh chỉnh chuyên biệt cho dịch thuật — các hệ thống lai (hybrid) thừa hưởng sự tinh tế về mặt ngữ cảnh của các LLM đa dụng nhưng được tối ưu hóa cho chất lượng dịch thuật.

**ALMA** (Advanced Language Model-based trAnslator), được phát triển bởi **Haoran Xu** và các đồng nghiệp tại Đại học Johns Hopkins, đã chứng minh một hiểu biết cốt lõi: bạn không cần các kho ngữ liệu song ngữ khổng lồ để xây dựng một công cụ dịch thuật xuất sắc. ALMA đã sử dụng phương pháp **tinh chỉnh hai giai đoạn** trên LLaMA-2: đầu tiên, tiếp tục tiền huấn luyện (pre-training) trên dữ liệu đơn ngữ không phải tiếng Anh để mở rộng kiến thức đa ngữ; sau đó, tinh chỉnh trên một tập dữ liệu song ngữ nhỏ nhưng có chất lượng cao. Phiên bản tiếp theo, **ALMA-R** (tháng 1 năm 2024), đã giới thiệu **Tối ưu hóa ưu tiên tương phản (Contrastive Preference Optimisation - CPO)** — huấn luyện mô hình trên dữ liệu ưu tiên (bản dịch tốt hơn so với bản dịch tệ hơn) thay vì chỉ sử dụng văn bản song ngữ. Kết quả: các mô hình tham số 7B và 13B đã ngang bằng hoặc vượt trội hơn GPT-4 trên các bài kiểm thử dịch thuật. Bài báo đã được công bố tại ICLR 2024 ([arXiv:2309.11674](https://arxiv.org/abs/2309.11674)). Một phiên bản sau đó, **X-ALMA**, đã mở rộng phạm vi bao phủ lên 50 ngôn ngữ bằng cách sử dụng các mô hình cắm-và-chạy (plug-and-play) đặc thù cho từng ngôn ngữ.

**Tower**, được phát triển bởi **Unbabel** (một công ty dịch thuật AI của Bồ Đào Nha) hợp tác với SARDINE Lab và MICS Lab, đã tiếp cận vấn đề một cách toàn diện hơn. Thay vì chỉ tối ưu hóa cho riêng tác vụ dịch thuật, Tower bao phủ **toàn bộ quy trình dịch thuật**: sửa lỗi nguồn, nhận dạng thực thể có tên (NER), hậu biên tập (post-editing), xếp hạng bản dịch và phát hiện lỗi. Các mô hình Tower ban đầu (7B và 13B, dựa trên LLaMA-2) đã vượt trội hơn NLLB-200-54B. **Tower v2** (70B, được trình bày tại WMT 2024) đã vượt trội hơn GPT-4o, Claude 3.5 Sonnet và DeepL. Phiên bản **Tower+** mới nhất (2025) đã mở rộng lên 22–27 ngôn ngữ và giải quyết vấn đề "quên lãng thảm họa" (catastrophic forgetting) — xu hướng các mô hình sau khi tinh chỉnh bị mất đi các khả năng tổng quát — thông qua tối ưu hóa ưu tiên và học tăng cường.

### Prompting so với Fine-Tuning: Cuộc tranh luận chưa hồi kết

Một câu hỏi dai dẳng trong không gian LLM-MT là liệu việc **prompt (thiết kế câu lệnh)** cho một LLM đa dụng để dịch thuật (zero-shot hoặc few-shot) sẽ tốt hơn, hay việc **fine-tune (tinh chỉnh)** một mô hình chuyên biệt cho dịch thuật sẽ tốt hơn. Các bằng chứng thực tế cho thấy câu trả lời phụ thuộc vào từng tác vụ cụ thể:

- **Prompting** giữ lại các khả năng tổng quát của LLM — điều hướng mức độ trang trọng (formality steering), kiểm soát phong cách, tính mạch lạc ở cấp độ tài liệu — và không yêu cầu huấn luyện thêm. Phương pháp này lý tưởng cho việc thử nghiệm nhanh và dịch thuật sáng tạo hoặc dịch thuật theo ngữ cảnh.
- **Fine-tuning** mang lại độ chính xác cao hơn trên các cặp ngôn ngữ và lĩnh vực cụ thể nhưng có nguy cơ làm giảm các khả năng khác ("quên lãng thảm họa"). Phương pháp này đòi hỏi dữ liệu song ngữ và tài nguyên tính toán.
- **Các cách tiếp cận lai (hybrid)** ngày càng chiếm ưu thế trong thực tế: sử dụng các mô hình đã được tinh chỉnh cho bản dịch ban đầu, kết hợp với các bước hậu biên tập hoặc tự cải thiện (self-refinement) dựa trên LLM.

### Trạng thái công nghệ tiên tiến nhất hiện nay (2025–2026)

Câu trả lời thành thực cho câu hỏi "hệ thống MT nào tốt nhất?" là: **tùy thuộc vào nhu cầu**.

| Trường hợp sử dụng | Cách tiếp cận tốt nhất | Lý do |
|---|---|---|
| Tài nguyên cao, khối lượng lớn | NMT thương mại (Google, DeepL) | Tốc độ, chi phí, tính nhất quán |
| Tài nguyên cao, chất lượng cao | LLM (GPT-4o, Gemini 2.5 Pro) hoặc Tower+ | Hiểu ngữ cảnh, xử lý thành ngữ |
| Tài nguyên thấp, độ bao phủ rộng | Meta OMT, NLLB-200, Google Translate | Độ bao phủ đa ngữ được xây dựng chuyên biệt |
| Tài nguyên thấp, cặp ngôn ngữ cụ thể | NLLB hoặc LLM được tinh chỉnh trên dữ liệu chuyên ngành | Cải thiện chất lượng có mục tiêu |
| Nghiên cứu mã nguồn mở | Tower+, ALMA-R, X-ALMA | Trọng số mở, có thể tái lập, có tính cạnh tranh cao |

Vào tháng 3 năm 2026, Meta đã phát hành **OMT (Omnilingual Machine Translation)** — phiên bản kế nhiệm của NLLB-200, mở rộng độ bao phủ từ 200 lên **hơn 1.600 ngôn ngữ**. OMT giải quyết cái mà Meta gọi là "nút thắt cổ chai thế hệ" (generation bottleneck): các mô hình ngôn ngữ lớn có thể hiểu nhiều ngôn ngữ nhưng lại gặp khó khăn trong việc tạo ra văn bản trôi chảy bằng các ngôn ngữ đó. OMT có hai kiến trúc — OMT-LLaMA (chỉ giải mã - decoder-only, 1B–8B tham số) và OMT-NLLB (encoder-decoder) — đồng thời giới thiệu các công cụ đánh giá mới bao gồm BOUQuET và BLASER 3 (một hệ số đánh giá chất lượng không cần tham chiếu - reference-free quality estimation metric). Các báo cáo ban đầu chỉ ra rằng các mô hình tham số 1B–8B đạt hiệu suất ngang bằng hoặc vượt trội so với các mô hình cơ sở LLM 70B trên các tác vụ dịch thuật. Liệu OMT cuối cùng có bao gồm tiếng Plains Cree hoặc các ngôn ngữ Algonquian khác hay không vẫn còn là một câu hỏi bỏ ngỏ.

Bài báo công bố kết quả nhiệm vụ chung WMT 2024 đã được đặt tiêu đề rất phù hợp: **"The LLM Era Is Here but MT Is Not Solved Yet"** (Kỷ nguyên LLM đã đến nhưng MT vẫn chưa được giải quyết triệt để). Các LLM đã nâng trần giới hạn cho dịch thuật tài nguyên cao nhưng vẫn chưa giải quyết được các thách thức cơ bản của MT tài nguyên thấp, tính đầy đủ của việc đánh giá (evaluation adequacy) hay độ phức tạp về mặt hình thái học (morphological complexity).

---

## Phần 4: Bài toán tài nguyên thấp

### Tại sao hầu hết các ngôn ngữ bị bỏ lại phía sau

Trong số khoảng 7.000 ngôn ngữ đang tồn tại trên thế giới, các hệ thống MT thương mại chỉ bao phủ tốt nhất khoảng 200–250 ngôn ngữ. Đại đa số các ngôn ngữ hoàn toàn **không có dịch máy**. Để hiểu tại sao, chúng ta cần hiểu các hệ thống MT cần gì và hầu hết các ngôn ngữ đang thiếu gì.

Neural MT đòi hỏi **dữ liệu song ngữ (parallel data)**: các tập hợp câu lớn được con người dịch giữa hai ngôn ngữ. Đối với tiếng Anh–tiếng Pháp, dữ liệu này tồn tại vô cùng dồi dào — các biên bản họp của Nghị viện châu Âu (Europarl), tài liệu của Liên Hợp Quốc, kho lưu trữ tin tức và bộ nhớ dịch thuật thương mại cung cấp hàng trăm triệu câu song ngữ. Đối với một ngôn ngữ như tiếng Plains Cree (*nêhiyawêwin*), được nói bởi khoảng 27.000 người chủ yếu ở miền tây Canada, dữ liệu như vậy về cơ bản là không tồn tại. Không có biên bản họp nào của Liên Hợp Quốc bằng tiếng Plains Cree. Không có kho ngữ liệu tin tức song ngữ nào. Tổng số văn bản song ngữ hiện có chỉ có thể được tính bằng hàng nghìn câu thay vì hàng triệu câu.

Lĩnh vực này sử dụng các phân nhóm tài nguyên thô để phân loại các ngôn ngữ:

| Phân nhóm | Dữ liệu song ngữ hiện có | Ví dụ |
|---|---|---|
| Tài nguyên cao | >10 triệu cặp câu | Tiếng Anh, tiếng Pháp, tiếng Đức, tiếng Trung, tiếng Tây Ban Nha |
| Tài nguyên trung bình | 1–10 triệu cặp câu | Tiếng Thổ Nhĩ Kỳ, tiếng Việt, tiếng Swahili |
| Tài nguyên thấp | 100K–1 triệu cặp câu | Tiếng Yoruba, tiếng Guaraní, tiếng Malta |
| Tài nguyên cực thấp | <100K cặp câu | Tiếng Plains Cree, tiếng Quechua, hầu hết các ngôn ngữ bản địa |
| Gần như bằng không | <10K cặp câu | Hàng nghìn ngôn ngữ trên toàn thế giới |

### Bài toán bộ tách từ (Tokenizer)

Trước khi một mô hình neural có thể xử lý văn bản, nó phải chuyển đổi các ký tự thành các token dạng số — một quá trình được gọi là **tách từ (tokenisation)**. Thuật toán tách từ thống trị là **Byte Pair Encoding (BPE)**, được phổ biến bởi Sennrich và các đồng nghiệp (2016) và được triển khai trong các công cụ như **SentencePiece** (Kudo & Richardson, 2018). BPE hoạt động bằng cách học các chuỗi ký tự phổ biến nhất trong một kho ngữ liệu huấn luyện và xây dựng một từ vựng gồm các đơn vị từ phụ (subword units). Trong tiếng Anh, các từ phổ biến như "the" trở thành các token đơn lẻ; các từ hiếm gặp được chia thành các phần từ phụ ("unforgivable" → "un" + "forgiv" + "able").

Vấn đề là từ vựng BPE được huấn luyện chủ yếu trên các ngôn ngữ giàu tài nguyên, trong đó tiếng Anh thường chiếm ưu thế tuyệt đối. Đối với các ngôn ngữ nghèo tài nguyên, đặc biệt là những ngôn ngữ có hình thái học phức tạp hoặc sử dụng chữ viết không phải Latin, hậu quả là rất nghiêm trọng:

- **Phân mảnh quá mức (Over-segmentation)**: Một từ duy nhất trong một ngôn ngữ đa tổng hợp (polysynthetic) như tiếng Plains Cree có thể mã hóa cả một mệnh đề. Từ *nikî-nipâw* ("Tôi đã ngủ") sẽ bị bẻ gãy thành vô số mảnh nhỏ — thậm chí là các byte riêng lẻ — bởi vì thuật toán BPE chưa từng thấy các chuỗi ký tự này trước đây. Thứ vốn là một đơn vị có nghĩa đối với người nói lại trở thành hàng tá mảnh vụn vô nghĩa đối với mô hình.

- **Bài toán độ sinh token (fertility problem)**: Một từ duy nhất trong một ngôn ngữ có hình thái phức tạp có thể yêu cầu từ 5–15 token, trong khi bản dịch tiếng Anh của nó chỉ sử dụng 1–3 token. Điều này tạo ra sự bất đối xứng khổng lồ về độ dài chuỗi, làm giảm hiệu quả gióng hàng chú ý (attention alignment) và chất lượng dịch thuật.

- **Bất lợi về chữ viết (Script penalties)**: Các ngôn ngữ sử dụng chữ viết không phải Latin (chữ âm tiết Cree, chữ Ethiopia, chữ Devanagari) được tách từ thậm chí còn kém hiệu quả hơn, đôi khi phải lùi về các byte riêng lẻ. Điều này có nghĩa là cửa sổ ngữ cảnh hiệu dụng (effective context window) của mô hình đối với các ngôn ngữ này bị thu hẹp lại một cách đáng kể.

Đây không chỉ là một sự bất tiện về mặt kỹ thuật. Từ vựng của bộ tách từ thực chất đã mã hóa một định kiến thiên vị các ngôn ngữ giàu tài nguyên ngay từ cấp độ cơ bản nhất của hệ thống. Một mô hình phải tốn 15 token để mã hóa một từ tiếng Cree duy nhất sẽ còn rất ít dung lượng để hiểu phần còn lại của câu so với một mô hình xử lý tiếng Anh, nơi thông tin tương tự chỉ chiếm 3 token.

### Bài toán chất lượng dữ liệu

Lượng dữ liệu song ngữ hạn chế thực sự tồn tại cho các ngôn ngữ nghèo tài nguyên thường đến từ các **lĩnh vực hạn hẹp (narrow domains)**. Hai nguồn văn bản song ngữ đa ngữ lớn nhất cho các ngôn ngữ thiếu tài nguyên là:

1. **Các bản dịch Kinh Thánh**: Kinh Thánh đã được dịch sang hơn 700 ngôn ngữ, và các phần của nó được dịch sang hơn 3.000 ngôn ngữ. Điều này làm cho văn bản tôn giáo trở thành tài nguyên song ngữ duy nhất có sẵn cho many ngôn ngữ — nhưng một mô hình được huấn luyện chủ yếu trên văn bản Kinh Thánh sẽ học một văn phong, từ vựng và lĩnh vực đặc thù. Nó có thể tạo ra những câu kiểu cổ kính như "ngươi chớ nên" nhưng không thể dịch được câu "làm ơn đặt giúp tôi một chuyến bay".

2. **JW300**: Một tập dữ liệu được trích xuất từ các ấn phẩm của Nhân chứng Giê-hô-va, bao phủ khoảng 300 ngôn ngữ. Mặc dù có quy mô lớn và đa ngữ, JW300 lại đặt ra cả vấn đề lệch lĩnh vực (nội dung tôn giáo) lẫn các mối lo ngại về mặt đạo đức liên quan đến nguồn gốc và sự đồng ý đối với các bản dịch nền tảng.

**Sự rò rỉ dữ liệu kiểm thử (Benchmark contamination)** là một mối lo ngại nghiêm trọng khác. Khi dữ liệu song ngữ khan hiếm, cùng một văn bản có thể xuất hiện ở cả tập huấn luyện và tập đánh giá — một sự rò rỉ dữ liệu làm thổi phồng các chỉ số chất lượng. Bể dữ liệu càng nhỏ thì việc ngăn chặn và phát hiện điều này càng khó khăn.

### Tăng cường dữ liệu: Làm nhiều hơn từ ít hơn

Các nhà nghiên cứu đã phát triển các kỹ thuật để tận dụng tối đa nguồn dữ liệu hạn chế:

- **Dịch ngược (Backtranslation)** (Sennrich và các đồng nghiệp, 2016): Huấn luyện một mô hình ban đầu trên dữ liệu song ngữ hiện có, sau đó sử dụng nó để dịch ngược văn bản **đơn ngữ (monolingual)** của ngôn ngữ đích về ngôn ngữ nguồn. Điều này tạo ra dữ liệu song ngữ tổng hợp (synthetic parallel data) tuy có nhiều nhiễu nhưng có thể cải thiện đáng kể chất lượng mô hình. Dịch ngược đã trở thành một kỹ thuật tiêu chuẩn trên mọi dải tài nguyên.

- **Dữ liệu tổng hợp do LLM tạo ra**: Sử dụng các mô hình ngôn ngữ lớn để tạo dữ liệu huấn luyện cho các cặp ngôn ngữ nghèo tài nguyên. Phương pháp này đầy hứa hẹn nhưng cũng mang lại rủi ro — văn bản được tạo ra có thể mang phong cách "văn dịch" (translationese - các mẫu câu dịch thô cứng một cách phi tự nhiên hoặc bị ảnh hưởng nặng nề bởi ngôn ngữ nguồn) và có thể khuếch đại bất kỳ định kiến nào tồn tại trong LLM.

- **Chuyển giao xuyên ngôn ngữ (Cross-lingual transfer)**: Huấn luyện trên dữ liệu song ngữ từ một ngôn ngữ liên quan có tài nguyên cao hơn (ví dụ: sử dụng dữ liệu tiếng Tây Ban Nha–tiếng Anh để khởi tạo MT tiếng Guaraní–tiếng Anh) và hy vọng các đặc trưng cấu trúc chung sẽ được chuyển giao. Phương pháp này hoạt động tốt hơn đối với các ngôn ngữ có quan hệ họ hàng gần gũi so với các ngôn ngữ khác biệt về loại hình.

- **Phân đoạn hình thái (Morphological segmentation)**: Tiền xử lý văn bản để chia các từ thành các hình vị (morphemes - đơn vị nhỏ nhất có nghĩa) trước khi đưa chúng vào mô hình. Đối với các ngôn ngữ chắp dính (agglutinative) và đa tổng hợp, điều này có thể cải thiện đáng kể hiệu quả tách từ và chất lượng dịch thuật. Cách tiếp cận này kết nối trực tiếp với các công cụ dựa trên luật được thảo luận trong phần tiếp theo.

---

## Phần 5: Bộ chuyển đổi trạng thái hữu hạn và Hệ thống dựa trên luật

### Tại sao các quy tắc vẫn quan trọng

Câu chuyện cho đến nay dường như là sự thống trị tuyệt đối của neural: các hệ thống thống kê bị thay thế bởi mạng neural, mạng neural bị thay thế bởi Transformer, Transformer được mở rộng quy mô thành các LLM. Nhưng có một truyền thống song song trong ngôn ngữ học máy tính chưa bao giờ biến mất — và đối với một số ngôn ngữ nhất định, nó vẫn là thứ không thể thay thế.

**Các hệ thống dựa trên luật (Rule-based systems)** mã hóa kiến thức ngôn ngữ một cách rõ ràng: các quy tắc hình thái, từ vựng, các mẫu chuyển đổi cú pháp. Chúng không học từ dữ liệu; chúng được xây dựng bởi các nhà ngôn ngữ học hiểu rõ các ngôn ngữ liên quan. Đối với các ngôn ngữ giàu tài nguyên, cách tiếp cận này từ lâu đã bị vượt qua bởi các phương pháp dựa trên dữ liệu. Nhưng đối với các ngôn ngữ có hình thái phức tạp và dữ liệu tối thiểu, các hệ thống dựa trên luật thường cung cấp công cụ phân tích đáng tin cậy duy nhất hiện có.

### Bộ chuyển đổi trạng thái hữu hạn: Khái niệm cơ bản

Một **Bộ chuyển đổi trạng thái hữu hạn (Finite-State Transducer - FST)** là một thiết bị tính toán thực hiện ánh xạ giữa hai cấp độ biểu diễn — điển hình là giữa dạng bề mặt (những gì bạn thấy trong văn bản) và phân tích bên dưới (ý nghĩa của nó về mặt ngôn ngữ học). Hãy nghĩ về nó như một cỗ máy với các trạng thái và các bước chuyển: nó đọc các ký hiệu đầu vào, di chuyển giữa các trạng thái và tạo ra các ký hiệu đầu ra.

Để có một ví dụ cụ thể, hãy xem xét từ tiếng Plains Cree *nikî-nipâw*. Một bộ phân tích hình thái dựa trên FST có thể nhận dạng bề mặt này và tạo ra:

> nipâw + Verb + AI + Independent + Past + 1st Person Singular

Điều này cho bạn biết từ đó là động từ *nipâw* ("ngủ") ở thể độc lập, thì quá khứ, ngôi thứ nhất số ít — "Tôi đã ngủ". Bộ chuyển đổi mã hóa các quy tắc hình thái học tiếng Cree: tiền tố nào chỉ ngôi, tiền tố nào chỉ thì, dạng động từ nào đi với mẫu biến hình nào. Quan trọng là, cơ chế này hoạt động **hai chiều (bidirectionally)**: từ một phân tích, FST có thể tạo ra dạng bề mặt chính xác.

Cơ sở hạ tầng kỹ thuật để xây dựng các FST bao gồm:

- **HFST** (Helsinki Finite-State Transducer Technology): Một bộ công cụ mã nguồn mở được duy trì tại Đại học Helsinki, cung cấp khung tính toán để xây dựng và chạy các bộ chuyển đổi. HFST triển khai các cơ chế hình thức ban đầu được phát triển bởi Xerox (lexc, twolc, xfst) và tương thích với **foma**, một bộ công cụ FST mã nguồn mở khác.

- **lexc**: Một cơ chế hình thức để xác định **từ vựng (lexicon)** — danh mục các hình vị (gốc từ, tiền tố, hậu tố) và các mẫu cấu tạo từ kết hợp chúng.

- **twolc**: Một cơ chế hình thức để xác định **các quy tắc hình thái-ngữ âm (morphophonological rules)** — những thay đổi về âm xảy ra khi các hình vị kết hợp với nhau (ví dụ: sự hài hòa nguyên âm, sự biến đổi phụ âm).

### GiellaLT: Cơ sở hạ tầng vùng Bắc Cực

**GiellaLT** (từ từ tiếng Northern Sámi *giella*, nghĩa là "ngôn ngữ") là một cơ sở hạ tầng công nghệ ngôn ngữ có trụ sở tại **UiT — Đại học Bắc Cực Na Uy** ở Tromsø. Nó đại diện cho nỗ lực sâu rộng nhất trên toàn thế giới nhằm xây dựng các công cụ dựa trên FST cho các ngôn ngữ bản địa và ngôn ngữ thiểu số.

Ban đầu được biết đến với tên gọi **Giellatekno** (nghiên cứu) và **Divvun** (công cụ ngôn ngữ), dự án — do các nhà ngôn ngữ học **Trond Trosterud** và **Sjur Nygaard Moshagen** dẫn dắt — đã phát triển các bộ phân tích hình thái, bộ kiểm tra chính tả và các công cụ ngôn ngữ khác cho hơn **100 ngôn ngữ**, tập trung vào các ngôn ngữ Sámi (Northern Sámi, Lule Sámi, South Sámi, v.v.), các ngôn ngữ Ural và các ngôn ngữ Bắc Cực cũng như bản địa khác.

GiellaLT sử dụng HFST làm nền tảng tính toán phía sau (backend) và đã phát triển một cơ sở hạ tầng chia sẻ tinh vi: một hệ thống biên dịch chung, các khung kiểm thử dùng chung và các thành phần ngôn ngữ có thể tái sử dụng. Toàn bộ mã nguồn là mã nguồn mở, được lưu trữ trên [GitHub](https://github.com/giellalt), với hàng trăm kho lưu trữ bao gồm cơ sở hạ tầng cốt lõi và các kho lưu trữ đặc thù cho từng ngôn ngữ (ví dụ: `lang-sme` cho tiếng Northern Sámi, `lang-crk` cho tiếng Plains Cree). Tài liệu của dự án nằm tại [giellalt.github.io](https://giellalt.github.io/). Cổng thông tin công cộng, **[Borealium.org](https://borealium.org)** — được tài trợ bởi Hội đồng Bộ trưởng Bắc Âu — cung cấp quyền truy cập miễn phí vào các công cụ hiệu đính, bàn phím, từ điển, công cụ học ngôn ngữ (Oahpa) và tổng hợp giọng nói cho các ngôn ngữ Sámi, tiếng Kven, tiếng Faroe, tiếng Greenland và các ngôn ngữ khác.

Mối quan hệ giữa GiellaLT và chính sách ngôn ngữ quốc gia là rất đáng chú ý. Phần lớn kinh phí của dự án đến từ **Nghị viện Sámi Na Uy** và các chương trình ngôn ngữ của chính phủ các nước Bắc Âu, phản ánh một cam kết chính trị đối với công nghệ ngôn ngữ bản địa có quy mô và thời gian kéo dài hiếm thấy.

### Apertium: Dịch máy dựa trên luật mã nguồn mở

**[Apertium](https://www.apertium.org/)** là một nền tảng dịch máy dựa trên luật mã nguồn mở, ban đầu được phát triển tại Đại học Alicante (Tây Ban Nha) với nguồn tài trợ từ chính phủ Tây Ban Nha và Catalonia. Nó bắt đầu vào năm 2004 với sự tập trung vào các cặp ngôn ngữ có liên quan (tiếng Tây Ban Nha–tiếng Catalan, tiếng Tây Ban Nha–tiếng Bồ Đào Nha), nơi các quy tắc chuyển đổi nông (shallow transfer rules) — dịch từng từ một kết hợp với các điều chỉnh hình thái — mang lại kết quả tốt đến kinh ngạc. Các nhà đóng góp chính bao gồm **Francis M. Tyers**, người đóng vai trò trung tâm trong cả sự phát triển của Apertium lẫn việc áp dụng nó cho các ngôn ngữ thiếu tài nguyên.

Kiến trúc của Apertium là một **quy trình đường ống (pipeline)** cổ điển:

1. **Phân tích hình thái** (dựa trên FST): Xác định từ nguyên (lemma) và các đặc trưng hình thái của từng từ
2. **Khử nhập nhằng từ loại (Part-of-speech disambiguation)**: Chọn phân tích chính xác khi các từ có nghĩa mơ hồ
3. **Chuyển đổi từ vựng (Lexical transfer)**: Ánh xạ từ nguyên của ngôn ngữ nguồn sang từ nguyên của ngôn ngữ đích
4. **Chuyển đổi cấu trúc (Structural transfer)**: Áp dụng các quy tắc để xử lý các thay đổi về trật tự từ, sự hòa hợp (agreement) và các khác biệt cú pháp khác
5. **Tạo hình thái** (dựa trên FST): Tạo ra dạng bề mặt ngôn ngữ đích được biến hình chính xác

Tính đến năm 2025, Apertium hỗ trợ hàng trăm cặp ngôn ngữ ở các mức chất lượng khác nhau, tất cả đều được lưu trữ trên [GitHub](https://github.com/apertium). Nó vẫn đang được phát triển tích cực bởi một cộng đồng quốc tế và đặc biệt hữu ích cho các cặp ngôn ngữ có quan hệ họ hàng gần gũi, nơi cách tiếp cận dựa trên luật của nó có thể đạt được chất lượng hợp lý mà không cần dữ liệu huấn luyện.

### Các cách tiếp cận lai: FST + Neural

Ranh giới đầy hứa hẹn nhất cho MT tài nguyên thấp có thể là **các kiến trúc lai (hybrid architectures)** kết hợp phân tích hình thái dựa trên luật với dịch thuật neural. Ý tưởng rất đơn giản: sử dụng một FST để phân đoạn các từ thành các hình vị (giải quyết bài toán tách từ được mô tả trong Phần 4), sau đó đưa văn bản đã phân đoạn vào một hệ thống neural MT.

Đối với một ngôn ngữ đa tổng hợp như tiếng Plains Cree, điều này có nghĩa là mô hình neural sẽ nhận được một chuỗi các đơn vị có nghĩa thay vì các mảnh byte ngẫu nhiên. **Phòng thí nghiệm Công nghệ Ngôn ngữ Alberta (ALT Lab)** tại Đại học Alberta, do **Antti Arppe** dẫn dắt, đã xây dựng các bộ phân tích hình thái dựa trên FST toàn diện và các công cụ từ điển hướng tới cộng đồng cho tiếng Plains Cree bằng cách sử dụng cơ sở hạ tầng GiellaLT. Công trình công bố gần đây nhất của họ (Arppe 2025, AmericasNLP) trình bày việc ánh xạ dựa trên FST giữa các dạng từ biến hình tiếng Cree và các cụm từ tiếng Anh — về mặt bản chất là "dịch thuật hạn chế" (restricted translation) thông qua các phương pháp trạng thái hữu hạn, hoạt động ở cấp độ từ/cụm từ thay vì toàn bộ câu. Đáng chú ý là ALT Lab **chưa** công bố một hệ thống MT lai FST+neural nào; công việc của họ dựa trên nền tảng ngôn ngữ học, dựa trên luật và ưu tiên độ tin cậy cũng như tính hữu dụng cho cộng đồng hơn là các cách tiếp cận neural mang tính thử nghiệm. Trong khi đó, Nguyen, Hammerly, và Silfverberg (2025, AmericasNLP) đã trình bày một quy trình lai LLM+FST cho các động từ tiếng Ojibwe tại UBC, đạt được kết quả ấn tượng (chrF 0.82) — đây là mô hình tương tự gần nhất được công bố cho một cách tiếp cận lai đối với một ngôn ngữ Algonquian.

Chiến lược lai này đại diện cho sự hội tụ của hai truyền thống đã chạy suốt lịch sử của MT: kiến thức rõ ràng của nhà ngôn ngữ học và việc học thống kê của kỹ sư. Đối với những ngôn ngữ cần MT nhất, không một truyền thống đơn lẻ nào là đủ.

---

## Phần 6: Đo lường chất lượng — Bài toán đánh giá

### Làm thế nào để biết một bản dịch là tốt?

Câu hỏi này nghe có vẻ đơn giản. Nhưng trên thực tế, nó là một trong những bài toán khó nhất chưa có lời giải trong lĩnh vực này, và cách bạn trả lời nó sẽ quyết định hệ thống nào có vẻ như "hoạt động hiệu quả" và hệ thống nào không.

### BLEU: Tiêu chuẩn không hoàn hảo

Trong hơn hai thập kỷ, hệ số tự động thống trị trong MT là **BLEU** (Bilingual Evaluation Understudy), được giới thiệu bởi Papineni và các đồng nghiệp tại IBM vào năm 2002. BLEU đo lường mức độ trùng khớp của các chuỗi từ (n-grams) trong bản dịch máy với một hoặc nhiều bản dịch tham chiếu do con người thực hiện. Nó bao gồm một hình phạt độ ngắn (brevity penalty) để ngăn các hệ thống gian lận điểm số bằng các đầu ra quá ngắn.

BLEU đã trở thành thước đo chung của lĩnh vực này vì nó nhanh, rẻ, không phụ thuộc vào ngôn ngữ và có thể tái lập (reproducible). Hầu như mọi bài báo nghiên cứu MT được công bố từ năm 2002 đến 2020 đều báo cáo điểm BLEU. Các nhiệm vụ chung của WMT đã sử dụng nó làm hệ số đánh giá chính trong nhiều năm.

But BLEU có những khuyết điểm sâu sắc ngày càng lộ rõ:

- **Không có sự hiểu biết về ngữ nghĩa**: BLEU thuần túy là so khớp bề mặt. Nếu một bản dịch sử dụng một từ đồng nghĩa hoàn hảo nhưng tình cờ không xuất hiện trong bản dịch tham chiếu, BLEU sẽ phạt nó. Câu "the cat sat on the mat" sẽ nhận điểm 0 so với bản dịch tham chiếu "the feline rested on the rug."
- **Khả năng phân biệt kém ở cấp độ câu**: BLEU được thiết kế như một hệ số đánh giá ở cấp độ kho ngữ liệu (corpus-level). Ở cấp độ câu, nó không đáng tin cậy và chứa nhiều nhiễu.
- **Mù hình thái học (Morphological blindness)**: Đối với các ngôn ngữ chắp dính (tiếng Thổ Nhĩ Kỳ, tiếng Phần Lan, tiếng Swahili), nơi một từ nguyên duy nhất có thể có hàng tá dạng biến hình, việc so khớp nghiêm ngặt ở cấp độ từ sẽ thất bại thảm hại. Một động từ được biến hình chính xác nhưng chỉ khác một hậu tố so với bản dịch tham chiếu cũng sẽ nhận điểm 0.
- **Tương quan yếu với đánh giá của con người**: Các phân tích gộp (meta-analyses), đặc biệt là Reiter (2018), đã chỉ ra rằng mối tương quan của BLEU với các đánh giá chất lượng của con người thường rất yếu, đặc biệt là đối với các hệ thống chất lượng cao và đối với các ngôn ngữ khác xa tiếng Anh.

### chrF và chrF++

**chrF** (character F-score), được giới thiệu bởi Maja Popović vào năm 2015, giải quyết điểm mù hình thái học của BLEU bằng cách đo lường mức độ trùng khớp ở **cấp độ ký tự** thay vì cấp độ từ. Điều này giúp ghi nhận một phần điểm cho các gốc từ chung ngay cả khi các biến hình khác nhau — điều cực kỳ quan trọng đối với các ngôn ngữ giàu hình thái. **chrF++** (Popović, 2017) bổ sung thêm các n-gram cấp độ từ vào lại, đạt được mối tương quan tốt hơn với đánh giá của con người so với các hệ số chỉ dựa trên ký tự hoặc chỉ dựa trên từ. Cả hai đều được triển khai trong **sacreBLEU**, bộ công cụ đánh giá tiêu chuẩn, và đã trở thành các hệ số phụ tiêu chuẩn trong các nhiệm vụ chung của WMT.

### COMET và xCOMET: Đánh giá bằng Neural

Bước tiến đáng kể nhất trong việc đánh giá MT là việc chuyển sang **các hệ số neural (neural metrics)** — các mô hình đánh giá bản chất chính là các Transformer, được huấn luyện để dự đoán các đánh giá chất lượng của con người.

**COMET** (Crosslingual Optimized Metric for Evaluation of Translation), được phát triển bởi Ricardo Rei và các đồng nghiệp tại **Unbabel** (2020), sử dụng một bộ mã hóa xuyên ngôn ngữ (XLM-RoBERTa) để nhúng (embed) câu nguồn, bản dịch và bản dịch tham chiếu, sau đó dự đoán điểm chất lượng. Không giống như BLEU, COMET hoạt động trong không gian ngữ nghĩa — nó nhận diện các cách diễn đạt khác (paraphrases), nắm bắt việc bảo toàn ý nghĩa và liên tục cho thấy mối tương quan cao hơn nhiều với đánh giá của con người so với các hệ số cấp độ bề mặt. COMET đã giành chiến thắng hoặc xếp thứ nhất trong các Nhiệm vụ chung về Hệ số đánh giá của WMT từ năm 2020 trở đi.

**xCOMET** (Guerreiro và các đồng nghiệp, 2024, công bố trên TACL) còn tiến xa hơn: bên cạnh điểm chất lượng, nó còn tạo ra **khả năng phát hiện phân đoạn lỗi chi tiết (fine-grained error span detection)** — xác định các lỗi cụ thể trong bản dịch, phân loại chúng theo loại lỗi (độ chính xác, độ trôi chảy, thuật ngữ) và mức độ nghiêm trọng (nhẹ, nặng, nghiêm trọng). Điều này giúp thu hẹp khoảng cách giữa việc chấm điểm tự động và phân tích ngôn ngữ học của con người.

### AfriCOMET: Đánh giá cho các ngôn ngữ thiếu tài nguyên

COMET tiêu chuẩn, được huấn luyện chủ yếu trên các đánh giá của con người đối với các ngôn ngữ châu Âu, có thể không khái quát hóa tốt cho các ngôn ngữ khác biệt về loại hình. **AfriCOMET** (Wang, Adelani và các đồng nghiệp, NAACL 2024) giải quyết vấn đề này bằng cách tinh chỉnh trên dữ liệu đánh giá của con người từ **13 ngôn ngữ châu Phi** và sử dụng **AfroXLM-R** — một bộ mã hóa đa ngữ được huấn luyện đặc biệt để biểu diễn tốt hơn các ngôn ngữ châu Phi. Công trình này, được thực hiện bởi cộng đồng Masakhane (xem Phần 7), chứng minh rằng bản thân các hệ số đánh giá cũng phải được điều chỉnh để thích ứng với sự đa dạng ngôn ngữ.

### Đánh giá của con người: MQM và Đánh giá trực tiếp

Các hệ số tự động chỉ là các đại diện thay thế. Chân lý cuối cùng vẫn là **đánh giá của con người (human evaluation)**, vốn có hai hình thức chính:

**Đánh giá trực tiếp (Direct Assessment - DA)** yêu cầu người đánh giá chấm điểm các bản dịch trên thang điểm từ 0–100. Phương pháp này tương đối nhanh và rẻ (có thể sử dụng người đánh giá từ nguồn lực cộng đồng - crowd-sourced) và là phương pháp đánh giá của con người chính tại WMT từ năm 2017 đến 2020. Điểm yếu của nó: khi chất lượng MT được cải thiện, những người đánh giá không chuyên không còn có thể phân biệt giữa các hệ thống tạo ra đầu ra gần đạt mức chuyên nghiệp. DA trở nên không đáng tin cậy ở phân khúc chất lượng cao nhất.

**Hệ thống chỉ số chất lượng đa chiều (Multidimensional Quality Metrics - MQM)** đã thay thế DA để trở thành phương pháp đánh giá của con người chính của WMT từ năm 2021 trở đi. MQM sử dụng **các dịch giả chuyên nghiệp**, những người sẽ đánh dấu các phân đoạn lỗi cụ thể trong bản dịch, phân loại lỗi theo loại (dịch sai, bỏ sót, ngữ pháp, thuật ngữ) và mức độ nghiêm trọng (nhẹ = 1 điểm, nặng = 5 điểm, nghiêm trọng = 25 điểm). Điều này tạo ra cả điểm số chất lượng lẫn thông tin chẩn đoán có thể hành động — bạn không chỉ biết bản dịch *tệ đến mức nào*, mà còn biết *cụ thể lỗi nằm ở đâu*.

| Đặc điểm | DA | MQM |
|---|---|---|
| Người đánh giá | Lao động cộng đồng (Crowd-workers) | Dịch giả chuyên nghiệp |
| Phương pháp | Điểm số tổng thể từ 0–100 | Chú thích phân đoạn lỗi |
| Thông tin chẩn đoán | Không có | Phân loại lỗi chi tiết |
| Chi phí | Thấp hơn | Cao hơn |
| Độ tin cậy | Yếu hơn đối với MT chất lượng cao | Tiêu chuẩn vàng |
| Sử dụng chính tại WMT | 2017–2020 | 2021–nay |

### Cuộc khủng hoảng đánh giá đối với các ngôn ngữ nghèo tài nguyên

Đối với các ngôn ngữ nghèo tài nguyên, bài toán đánh giá càng trở nên phức tạp bởi một số yếu tố:

- **Thiếu người đánh giá có trình độ**: MQM yêu cầu các dịch giả chuyên nghiệp song ngữ. Đối với nhiều ngôn ngữ nghèo tài nguyên, việc tìm kiếm những người đánh giá như vậy là vô cùng khó khăn.
- **Không có bản dịch tham chiếu**: Cả COMET và BLEU đều yêu cầu các bản dịch tham chiếu để so sánh. Đối với nhiều lĩnh lĩnh vực và ngôn ngữ, các bản dịch này hoàn toàn không tồn tại.
- **Định kiến của hệ số đánh giá**: Cả các hệ số cấp độ bề mặt và hệ số neural đều được phát triển và xác thực trên dữ liệu ngôn ngữ châu Âu. Hành vi của chúng trên các ngôn ngữ khác biệt về loại hình vẫn chưa chắc chắn.
- **Nguy cơ ảo tưởng (Hallucination)**: Trong bối cảnh nghèo tài nguyên, các mô hình MT có thể tạo ra đầu ra trôi chảy nhưng hoàn toàn không liên quan hoặc không trung thực với văn bản nguồn — một hiện tượng gọi là **ảo tưởng (hallucination)**. Các hệ số cấp độ bề mặt có thể gán điểm số khác không cho đầu ra ảo tưởng nếu nó vô tình chia sẻ các n-gram với bản dịch tham chiếu.

Việc xây dựng **các tập đánh giá tùy chỉnh** — ngay cả những tập nhỏ gồm 200–500 cặp câu được tuyển chọn cẩn thận trong lĩnh vực mục tiêu — là điều cần thiết cho bất kỳ nỗ lực MT tài nguyên thấp nghiêm túc nào. Việc chỉ dựa vào điểm số FLORES-200 hoặc BLEU mà không có đánh giá đặc thù cho từng lĩnh vực là một công thức dẫn đến sự tự tin sai lầm.

---

## Phần 7: Toàn cảnh các tổ chức và cộng đồng

### Các tập đoàn lớn

Lĩnh vực MT được định hình bởi một số ít các tập đoàn lớn, mỗi bên có những chiến lược riêng biệt:

**Google Translate** vẫn là hệ thống MT được sử dụng rộng rãi nhất trên toàn cầu, bao phủ **hơn 240 ngôn ngữ** tính đến năm 2025. Sáng kiến **1000 Languages Initiative** của Google (được công bố năm 2022) nhằm mục đích xây dựng các mô hình AI bao phủ 1.000 ngôn ngữ được nói nhiều nhất trên thế giới. Cloud Translation API cung cấp hai cấp độ: Basic (NMT cũ) và Advanced (các mô hình mới nhất). Google ngày càng tích hợp nhiều khả năng của LLM Gemini vào Translate, với các tính năng dịch thuật hiểu ngữ cảnh và tự nhiên xuất hiện vào năm 2025.

**Meta** đã tự định vị mình là động lực chính thúc đẩy MT đa ngữ mã nguồn mở thông qua NLLB-200, M2M-100, FLORES-200 và bộ giải pháp Seamless. Triết lý phát hành mô hình mở của Meta đã mang lại sự thay đổi mang tính bước ngoặt cho nghiên cứu học thuật, cung cấp các mô hình cơ sở và công cụ mà nếu không có chúng, người ta sẽ phải tốn một lượng tài nguyên tính toán khổng lồ.

**DeepL** chiếm lĩnh một phân khúc tập trung vào chất lượng, hỗ trợ khoảng **33 ngôn ngữ** — tất cả đều tương đối giàu tài nguyên — với danh tiếng về đầu ra tự nhiên, chuẩn bản ngữ được các dịch giả chuyên nghiệp ưa chuộng. Mô hình kinh doanh của DeepL (người dùng cá nhân freemium + API trả phí cho doanh nghiệp) và sự tập trung vào chất lượng thay vì số lượng phản ánh sự chú trọng vào quy trình dịch thuật chuyên nghiệp hơn là độ bao phủ ngôn ngữ rộng.

**Microsoft Translator** (một phần của Azure AI Services) cung cấp dịch thuật trên **hơn 130 ngôn ngữ** với khả năng tích hợp doanh nghiệp thông qua Microsoft 365 và Teams. Tính năng Custom Translator của nó cho phép các tổ chức tinh chỉnh các mô hình trên dữ liệu đặc thù của ngành.

**Unbabel** kết hợp MT với hậu biên tập của con người trong một quy trình làm việc "human-in-the-loop" (con người tham gia vào chu trình), bên cạnh các đóng góp nghiên cứu của mình (COMET, xCOMET, Tower). Nó đại diện cho ứng dụng thương mại của mô hình "MT + đánh giá của con người".

**LibreTranslate**, được xây dựng trên công cụ **Argos Translate**, cung cấp một giải pháp thay thế MT hoàn toàn mã nguồn mở, có thể tự lưu trữ (self-hostable) mà không phụ thuộc vào tập đoàn — điều quan trọng đối với các tổ chức có yêu cầu về chủ quyền dữ liệu (data sovereignty).

### Các cộng đồng cơ sở

Một số công việc quan trọng nhất trong MT — đặc biệt là đối với các ngôn ngữ thiếu tài nguyên — diễn ra tại các tổ chức nghiên cứu do cộng đồng dẫn dắt:

**[Masakhane](https://www.masakhane.io/)** (từ tiếng isiZulu có nghĩa là "chúng ta cùng nhau xây dựng") là một cộng đồng nghiên cứu cơ sở tập trung vào NLP cho các ngôn ngữ châu Phi, được thành lập vào năm 2019. Với hàng trăm thành viên trên khắp châu lục và cộng đồng hải ngoại, Masakhane đã tạo ra các tập dữ liệu nền tảng (MasakhaNER, MAFAND-MT, MENYO-20k, AfriQA), các hệ số đánh giá (AfriCOMET) và các nghiên cứu thúc đẩy đáng kể NLP cho các ngôn ngữ châu Phi. Các nhân vật chủ chốt bao gồm **David Ifeoluwa Adelani** (Mila / UCL). Mã nguồn và dữ liệu được lưu trữ trên [GitHub](https://github.com/masakhane-io); kênh liên lạc chính là không gian làm việc Slack của họ (tham gia qua masakhane.io), với các cuộc họp cộng đồng hàng tuần. Masakhane hoạt động trên các nguyên tắc về quyền sở hữu của người châu Phi đối với công nghệ ngôn ngữ châu Phi — một sự phản kháng có chủ ý đối với các mô hình nghiên cứu mang tính khai thác, nơi các tổ chức bên ngoài thu thập dữ liệu từ các cộng đồng ngôn ngữ mà không có sự hợp tác thực chất. Họ rõ ràng không khuyến khích "nghiên cứu nhảy dù" (parachute research), nơi những người bên ngoài khai thác dữ liệu ngôn ngữ mà không có quan hệ đối tác thực chất với cộng đồng.

**AmericasNLP** là một chuỗi hội thảo (song hành với NAACL) tập trung vào NLP cho các ngôn ngữ bản địa của châu Mỹ. Được tổ chức bởi các nhà nghiên cứu bao gồm **Manuel Mager**, **Arturo Oncevay**, và **Luis Chiruzzo**, hội thảo tổ chức các nhiệm vụ chung về MT cho các ngôn ngữ như tiếng Quechua, tiếng Guaraní, tiếng Aymara, tiếng Nahuatl, tiếng Rarámuri và các ngôn ngữ khác. Hội thảo làm nổi bật các thách thức nghiên cứu đặc thù của châu Mỹ — hình thái học đa tổng hợp, hệ thống thanh điệu, sự khan hiếm dữ liệu cực độ và các khía cạnh chính trị của công nghệ ngôn ngữ đối với các dân tộc từng bị thuộc địa hóa.

**[ALT Lab](https://altlab.ualberta.ca)** (Phòng thí nghiệm Công nghệ Ngôn ngữ Alberta) tại Đại học Alberta, do **Antti Arppe** dẫn dắt, tập trung đặc biệt vào các công cụ tính toán cho tiếng Plains Cree và các ngôn ngữ bản địa khác ở miền tây Canada. ALT Lab xây dựng các bộ phân tích hình thái dựa trên FST và các công cụ ngôn ngữ hướng tới cộng đồng (sử dụng cơ sở hạ tầng GiellaLT), đồng thời hợp tác chặt chẽ với các cộng đồng nói tiếng Cree — một hình mẫu cho việc phát triển công nghệ ngôn ngữ lấy cộng đồng làm trung tâm. Dự án hướng tới công chúng của họ **[21st Century Tools for Indigenous Languages](https://21c.tools)** cung cấp các từ điển trực tuyến và các công cụ hình thái học được xây dựng trên cơ sở hạ tầng này.

**[NRC Indigenous Languages Technology](https://nrc.canada.ca)** (Hội đồng Nghiên cứu Quốc gia Canada), do **Patrick Littell** dẫn dắt, duy trì một chương trình tích cực hỗ trợ hơn 25 ngôn ngữ bản địa trên khắp Canada, bao gồm nhiều phương ngữ tiếng Cree, tiếng Algonquin, tiếng Innu và tiếng Michif. NRC ILT đã công bố nghiên cứu MT cho tiếng Anh–tiếng Inuktitut (sử dụng kho ngữ liệu Nunavut Hansard) và phát triển các công cụ mã nguồn mở bao gồm **kiyânaw Transcribe** (chuyển âm tiếng Cree và tiếng Ojibwe), các bộ phân tích hình thái và **ReadAlong Studio** (gióng hàng âm thanh-văn bản). Toàn bộ mã nguồn là mã nguồn mở và NRC tuyên bố rõ ràng không yêu cầu bản quyền đối với dữ liệu ngôn ngữ của cộng đồng.

**[Aya](https://cohere.com/research/aya)** (Cohere For AI) là một sáng kiến LLM đa ngữ khoa học mở với hơn 3.000 người đóng góp từ hơn 119 quốc gia. Mặc dù không phải là một hệ thống MT chuyên dụng, các mô hình Aya (Aya-101 bao phủ 101 ngôn ngữ, Aya 23 bao phủ 23 ngôn ngữ có tầm ảnh hưởng lớn, Tiny Aya bao phủ 70 ngôn ngữ với 3,35 tỷ tham số) hoạt động cực kỳ hiệu quả cho các tác vụ dịch thuật. **Aya Collection** — gồm 513 triệu mẫu huấn luyện dạng hướng dẫn — là tập dữ liệu hướng dẫn đa ngữ mở lớn nhất. Mô hình quản trị cộng đồng của dự án này rất đáng để nghiên cứu.

**[GhanaNLP / Khaya](https://ghananlp.org)** là một sáng kiến NLP do cộng đồng thúc đẩy đã tạo ra nền tảng dịch thuật **Khaya** — một trong số ít các hệ thống MT do cộng đồng quản lý thực sự được triển khai để sử dụng hàng ngày. Khaya cung cấp dịch máy neural, ASR và TTS cho khoảng 12 ngôn ngữ Ghana (Twi, Ewe, Ga, Fante, Kusaal, v.v.) thông qua web, ứng dụng di động và API dành cho nhà phát triển. Cách tiếp cận của họ — với hơn 40.000 cặp câu song ngữ được xây dựng thông qua sự hợp tác của các nhà ngôn ngữ học và phản hồi từ cộng đồng — chứng minh rằng MT do cộng đồng quản lý có thể đi vào vận hành thực tế chứ không chỉ dừng lại ở mức kỳ vọng.

### Tài trợ và Chính sách

Nghiên cứu MT cho các ngôn ngữ nghèo tài nguyên phụ thuộc vào các nguồn tài trợ rất khác so với vốn đầu tư mạo hiểm và doanh thu quảng cáo vốn đang duy trì các hệ thống MT thương mại:

- **Lacuna Fund**: Một quỹ dữ liệu hợp tác được hỗ trợ bởi Quỹ Rockefeller, Google.org, IDRC của Canada và GIZ của Đức. Lacuna tài trợ cụ thể cho việc tạo ra **các tập dữ liệu được gán nhãn (labelled datasets)** cho các ngôn ngữ ít được đại diện — lấp đầy khoảng trống dữ liệu vốn là nguyên nhân gốc rễ của khoảng cách chất lượng MT.

- **AI4D** (Artificial Intelligence for Development): Một chương trình hỗ trợ các học bổng nghiên cứu AI cho công nghệ ngôn ngữ châu Phi, được vận hành thông qua IDRC và Cơ quan Hợp tác Phát triển Quốc tế Thụy Điển.

- **Thập kỷ Quốc tế về Ngôn ngữ Bản địa của UNESCO (2022–2032)**: Một khuôn khổ chính trị đã nâng cao vị thế của công nghệ ngôn ngữ bản địa trên toàn cầu, mặc dù nguồn tài trợ nghiên cứu cụ thể vẫn còn khiêm tốn.

- **Ngân hàng Phát triển Liên Mỹ**: Đã tài trợ cho dự án **GuaranIA** cho hệ thống MT tiếng Guaraní–tiếng Tây Ban Nha ở Paraguay, một ví dụ về tài chính phát triển hỗ trợ công nghệ ngôn ngữ.

- **Các hội đồng nghiên cứu quốc gia**: Phần lớn công việc MT tài nguyên thấp được tài trợ thông qua các kênh học thuật tiêu chuẩn (NSF, NSERC, các chương trình Horizon của EU), thường là các thành phần của các khoản tài trợ AI hoặc ngôn ngữ học rộng lớn hơn.

---

## Phần 8: Những ranh giới mở

### Những gì vẫn chưa được giải quyết

Lĩnh vực MT vào năm 2026 đồng thời có năng lực mạnh mẽ hơn và cũng trung thực hơn về các hạn chế của mình so với bất kỳ thời điểm nào trước đây. Một số bài toán ranh giới đang định hình bối cảnh nghiên cứu hiện tại:

**Dịch thuật ở cấp độ tài liệu (Document-level translation)** về cơ bản vẫn chưa được giải quyết triệt để. Hầu hết các hệ thống MT — bao gồm cả nhiều LLM — dịch theo từng câu, làm mất đi tính mạch lạc của diễn ngôn (discourse coherence), khả năng phân giải đại từ (pronoun resolution) qua ranh giới câu và tính nhất quán về mặt phong cách. Một dịch giả là con người sẽ đọc toàn bộ tài liệu trước khi dịch; trong khi hầu hết các hệ thống MT xử lý các câu một cách cô lập. Nghiên cứu về MT cấp độ tài liệu đang diễn ra tích cực nhưng vẫn chưa tạo ra các hệ thống duy trì tính mạch lạc một cách đáng tin cậy trên các văn bản dài.

**Diễn ngôn và ngữ dụng học (Discourse and pragmatics)** — khoảng cách giữa nghĩa đen và ý định giao tiếp — tiếp tục là thách thức đối với MT. Châm biếm, nói giảm nói tránh, các điển tích văn hóa và sự nhạy cảm về văn phong (trang trọng so với thân mật, tôn kính so với bình dân) được các LLM tốt nhất nắm bắt một phần nhưng không nhất quán. Một dịch giả làm việc giữa tiếng Nhật và tiếng Anh phải điều hướng một hệ thống kính ngữ phức tạp; các hệ thống MT hiện tại xử lý việc này ở mức độ không đồng đều.

**Dịch thuật đa phương thức (Multimodal translation)** — dịch thuật trong ngữ cảnh đi kèm hình ảnh, video hoặc âm thanh — là một lĩnh vực nghiên cứu mới nổi. Một món ăn trong thực đơn được mô tả là "trứng cá chuồn" sẽ hoàn toàn dễ hiểu nếu có hình ảnh đi kèm; nếu không có nó, MT có thể tạo ra một bản dịch kỳ lạ. Bộ giải pháp Seamless và các LLM đa phương thức (Gemini, GPT-4o) đã bắt đầu giải quyết vấn đề này, nhưng MT đa phương thức mạnh mẽ vẫn là một ranh giới phía trước.

**Dịch giọng nói-sang-giọng nói thời gian thực** với độ trễ tự nhiên (dưới 3 giây), bảo toàn danh tính người nói và chuyển giao tông giọng cảm xúc đang tiến gần đến mức