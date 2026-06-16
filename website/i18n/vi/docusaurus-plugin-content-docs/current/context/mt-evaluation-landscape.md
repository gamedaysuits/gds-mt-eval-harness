---
sidebar_position: 3
title: "Đo lường điều không thể đo lường"
---
# Đo lường những điều không thể đo lường: Vấn đề đánh giá trong dịch máy

**Khảo sát về cách ngành dịch máy đo lường chất lượng dịch thuật, những điểm hạn chế, và giải pháp thay thế từ LYSS (Linguistically-informed Yield & Structural Scoring)**

---

> *"Các hệ số đánh giá tự động là một lời nói dối tiện lợi. Chúng cho chúng ta một con số, con số đó giúp chúng ta viết một bài báo, và bài báo đó giúp chúng ta tuyên bố về sự tiến bộ. Liệu sự tiến bộ đó có thực sự xảy ra hay không lại là một câu hỏi hoàn toàn khác."*
> — Phỏng theo một quan điểm phổ biến tại WMT Metrics Shared Tasks

---

## Giới thiệu

Dịch máy đang gặp phải một vấn đề về đo lường.

Ngành này đã dành hai thập kỷ để xây dựng các hệ thống ngày càng phức tạp — từ bảng cụm từ (phrase tables), cơ chế chú ý (attention mechanisms) cho đến các mô hình ngôn ngữ hàng nghìn tỷ tham số — và trong suốt chặng đường đó, nó luôn phải vật lộn với một câu hỏi tưởng chừng như đơn giản: *làm thế nào để biết một bản dịch là tốt?*

Câu hỏi này không mang tính hàn lâm đơn thuần. Hệ số đánh giá (metric) bạn chọn sẽ quyết định hệ thống nào "chiến thắng". Nó quyết định dự án nào được cấp vốn, bài báo nào được xuất bản, hệ thống nào được triển khai, và — đối với các ngôn ngữ cần dịch máy nhất — liệu các bản dịch của một cộng đồng có bị đánh giá là thất bại khi chúng thực chất là chính xác hay không.

Lịch sử của việc đánh giá dịch máy (MT) phản ánh một cách thu nhỏ các giá trị của ngành này. Sự thống trị của BLEU trong gần hai thập kỷ cho thấy sự ưu tiên dành cho việc đo lường giá rẻ, nhanh chóng và không phụ thuộc vào ngôn ngữ, thay vì đánh giá dựa trên kiến thức ngôn ngữ học. Sự trỗi dậy của các metric nơ-ron như COMET phản ánh sự phát triển ngày càng tinh vi của ngành — cũng như sự phụ thuộc liên tục của nó vào dữ liệu huấn luyện lấy tiếng Anh làm trung tâm. Sự vắng bóng gần như hoàn toàn của các phương pháp đánh giá nhận biết hình thái học (morphology-aware) phản ánh một lĩnh vực mà cho đến gần đây, vẫn được xây dựng bởi và dành cho những người nói các ngôn ngữ châu Âu có tính phân tích (analytic languages).

Tài liệu này theo dõi sự phát triển của việc đánh giá dịch máy từ BLEU cho đến ngày nay, chỉ ra những điểm mà các phương pháp hiện tại thất bại một cách hệ thống đối với các ngôn ngữ có hình thái phức tạp và tài nguyên thấp, đồng thời xem xét một giải pháp thay thế dựa trên nền tảng ngôn ngữ học sẽ trông như thế nào. Đây là tài liệu đồng hành với các tài liệu bối cảnh khác của dự án — [*Từ Pāṇini đến Transformer*](./history-of-language-and-computation.md) (theo dõi lịch sử trí tuệ của ngôn ngữ và tính toán) và [*Báo cáo thực địa*](./mt-field-briefing.md) (khảo sát bức tranh toàn cảnh về dịch máy hiện tại). Trong khi các tài liệu đó đặt câu hỏi "làm thế nào chúng ta đến được đây?" và "những gì đang tồn tại?", thì tài liệu này hỏi: "làm thế nào chúng ta biết được liệu có bất kỳ giải pháp nào thực sự hiệu quả?"

---

## Phần 1: Kỷ nguyên khớp chuỗi (2002–2015)

### BLEU và sự ra đời của đánh giá tự động

Kỷ nguyên hiện đại của việc đánh giá dịch máy bắt đầu bằng một bài báo duy nhất: "BLEU: a Method for Automatic Evaluation of Machine Translation" của Kishore Papineni, Salim Roukos, Todd Ward, và Wei-Jing Zhu, được xuất bản tại ACL 2002. BLEU (Bilingual Evaluation Understudy) đo lường mức độ trùng lặp giữa các chuỗi từ (n-gram) của bản dịch máy với một hoặc nhiều bản dịch tham chiếu của con người. Nó bao gồm một hình phạt độ dài ngắn (brevity penalty) để ngăn các hệ thống gian lận điểm số bằng các đầu ra ngắn, và tính trung bình nhân của độ chính xác n-gram từ bậc 1 đến bậc 4.

BLEU trở thành "đồng tiền chung" của ngành vì một lý do đơn giản: nó nhanh, rẻ, có thể tái lập và không phụ thuộc vào ngôn ngữ. Trước khi có BLEU, việc đánh giá một hệ thống dịch máy đòi hỏi sự thẩm định tốn kém và chậm trễ từ con người. BLEU mang lại một con số có thể được tính toán trong vài mili giây, được so sánh giữa các bài báo và được sử dụng để xếp hạng các hệ thống trong các nhiệm vụ chung (shared tasks). Chỉ trong vòng vài năm, nó gần như trở thành bắt buộc — một bài báo không có điểm BLEU sẽ không thể xuất bản.

Nhưng BLEU có những khuyết điểm sâu sắc, đã được ghi nhận rõ ràng mà ngành dịch máy đã mất hai thập kỷ để cố gắng khắc phục:

**Không có sự hiểu biết về ngữ nghĩa.** BLEU thuần túy là so khớp bề mặt. "The cat sat on the mat" (Con mèo ngồi trên tấm thảm) sẽ nhận điểm 0 khi so với bản dịch tham chiếu "the feline rested on the rug" (con thú họ mèo nghỉ ngơi trên tấm thảm). Mọi từ đều là từ đồng nghĩa chính xác; ý nghĩa hoàn toàn giống nhau; nhưng điểm số lại bằng không.

**Mù mờ về hình thái học.** Đối với các ngôn ngữ chắp dính (agglutinative) và đa tổng hợp (polysynthetic), việc khớp chính xác ở cấp độ từ thất bại một cách thảm hại. Một động từ tiếng Cree được chia đúng cách nhưng chỉ khác một hình vị so với bản dịch tham chiếu sẽ nhận điểm 0 — ngay cả khi sự khác biệt đó chỉ là một tiểu từ tùy chọn về mặt ngữ pháp hoặc một trật tự từ có giá trị tương đương.

**Khả năng phân biệt kém ở cấp độ câu.** BLEU được thiết kế như một metric ở cấp độ ngữ liệu (corpus-level). Ở cấp độ câu, nó rất nhiễu và không đáng tin cậy — tuy nhiên nó vẫn thường xuyên được áp dụng cho các câu đơn lẻ.

**Thiên vị một bản dịch tham chiếu duy nhất.** BLEU giả định rằng chỉ có *một* bản dịch chính xác (hoặc một tập hợp nhỏ các bản dịch tham chiếu). Đối với các ngôn ngữ có trật tự từ tự do, từ vựng phong phú từ đồng nghĩa, hoặc có sự mơ hồ mang tính hệ thống (như đại từ "chúng tôi/chúng ta" bao gồm/loại trừ trong tiếng Cree), có thể có hàng tá bản dịch chính xác như nhau, và BLEU sẽ phạt tất cả trừ bản dịch trùng khớp với tham chiếu.

**Tương quan yếu với đánh giá của con người.** Các phân tích gộp — đáng chú ý là Reiter (2018, *Computational Linguistics*) — đã chỉ ra rằng mối tương quan của BLEU với các đánh giá chất lượng của con người thường rất yếu, đặc biệt là đối với các hệ thống chất lượng cao và đối với các ngôn ngữ khác xa tiếng Anh.

Những khuyết điểm này đã được biết đến ngay từ đầu. Tuy nhiên, BLEU vẫn tồn tại vì các giải pháp thay thế tệ hơn — không phải về độ chính xác, mà là về sự tiện lợi. Ngành dịch máy đã tối ưu hóa cho metric mà họ có thể tính toán được, chứ không phải metric mà họ thực sự cần.

### NIST (Doddington, 2002)

Metric NIST, được George Doddington công bố cùng năm với BLEU tại HLT 2002, đã sửa đổi công thức BLEU theo hai cách. Đầu tiên, nó trọng số hóa các n-gram dựa trên **hàm lượng thông tin** (information content) của chúng — các n-gram hiếm gặp sẽ nhận được trọng số cao hơn các n-gram phổ biến, dựa trên trực giác rằng việc dịch chính xác một cụm từ bất thường sẽ mang lại nhiều thông tin hơn là dịch chính xác từ "of the". Thứ hai, nó sử dụng **trung bình cộng** thay vì trung bình nhân của BLEU, tạo ra các điểm số ổn định hơn và không bị sụp đổ về 0 khi có bất kỳ bậc n-gram nào không có kết quả trùng khớp. NIST đã được sử dụng rộng rãi trong các chương trình đánh giá DARPA TIDES và NIST OpenMT nhưng chưa bao giờ đạt được sự thống trị như BLEU trong cộng đồng nghiên cứu rộng lớn hơn. Bất chấp những cải tiến, nó vẫn chia sẻ hạn chế cơ bản của BLEU: so khớp chuỗi ở cấp độ bề mặt mà không có khái niệm về ý nghĩa.

### METEOR (Banerjee & Lavie, 2005)

METEOR (Metric for Evaluation of Translation with Explicit ORdering) là một nỗ lực ban đầu nhằm giải quyết tính cứng nhắc của BLEU. Trong khi BLEU thực hiện khớp từ chính xác, METEOR đã giới thiệu ba cải tiến:

1. **Tách gốc từ (Stemming)**: Các từ được đưa về dạng gốc trước khi so sánh, giúp tính điểm một phần cho các biến thể hình thái (ví dụ: "running" khớp với "ran" sau khi tách gốc).
2. **Khớp từ đồng nghĩa**: Sử dụng WordNet, METEOR nhận biết rằng "car" và "automobile" là cùng một khái niệm.
3. **Căn chỉnh từ (Word alignment)**: Thay vì đếm các n-gram trùng lặp, METEOR căn chỉnh rõ ràng các từ giữa bản dịch giả thuyết và bản dịch tham chiếu, sau đó tính toán độ chính xác (precision) và độ gợi nhớ (recall) cùng với một hình phạt phân mảnh (fragmentation penalty).

METEOR liên tục cho thấy mối tương quan cao hơn với đánh giá của con người so với BLEU. Nhưng nó đòi hỏi các tài nguyên đặc thù cho từng ngôn ngữ (bộ tách gốc từ, cơ sở dữ liệu từ đồng nghĩa) làm hạn chế khả năng áp dụng, và tốc độ tính toán cũng chậm hơn. Đối với tiếng Anh, nó tốt hơn. Đối với các ngôn ngữ tài nguyên thấp, các bộ tách gốc từ và cơ sở dữ liệu từ đồng nghĩa đơn giản là không tồn tại.

### TER (Snover et al., 2006)

Translation Edit Rate đo lường số lượng chỉnh sửa tối thiểu (thêm, xóa, thay thế và *dịch chuyển cụm từ*) cần thiết để biến đổi bản dịch giả thuyết thành bản dịch tham chiếu, được chuẩn hóa theo độ dài của bản dịch tham chiếu. Thao tác dịch chuyển cụm từ (phrase-shift) — di chuyển một chuỗi từ liên tiếp sang một vị trí khác — là sự thừa nhận trực tiếp rằng trật tự từ không cố định giữa các ngôn ngữ. Cách tiếp cận khoảng cách chỉnh sửa (edit-distance) của TER rất trực quan (nó đo lường "người biên tập sau dịch máy cần phải làm bao nhiêu việc?") nhưng lại thừa hưởng cùng một hạn chế cơ bản: nó so sánh với một bản dịch tham chiếu duy nhất và không có khái niệm về ý nghĩa.

### chrF và chrF++ (Popović, 2015; 2017)

Cải tiến metric quan trọng nhất giữa BLEU và kỷ nguyên nơ-ron đến từ Maja Popović. **chrF** (character F-score) đo lường sự trùng lặp ở cấp độ *ký tự* thay vì cấp độ từ, tính toán độ chính xác và độ gợi nhớ của n-gram ký tự. **chrF++** bổ sung thêm các unigram và bigram ở cấp độ từ vào công thức.

Tại sao điều này lại quan trọng đối với các ngôn ngữ giàu hình thái: việc khớp ở cấp độ ký tự giúp *tính điểm một phần* cho các hình vị được chia sẻ. Các từ tiếng Cree *nikî-nipâw* ("tôi đã ngủ") và *kikî-nipâw* ("bạn đã ngủ") chia sẻ hầu hết các n-gram ký tự của chúng mặc dù là các từ khác nhau. chrF sẽ cho điểm một phần đáng kể; trong khi BLEU sẽ cho điểm 0.

chrF++ đã trở thành một metric phụ tiêu chuẩn tại các nhiệm vụ chung của WMT, được triển khai trong **sacreBLEU** (Post, 2018), và được công nhận rộng rãi là vượt trội hơn BLEU đối với các ngôn ngữ giàu hình thái. Nhưng nó vẫn là một metric khớp chuỗi — tốt hơn BLEU, nhưng bị hạn chế về mặt nền tảng bởi cùng một giả định rằng chất lượng dịch thuật có thể được đo lường bằng sự trùng lặp dạng bề mặt.

---

## Phần 2: Cuộc cách mạng metric nơ-ron (2018–Nay)

### Ý tưởng cốt lõi: Học cách chấm điểm

Các metric khớp chuỗi ở Phần 1 chia sẻ một lựa chọn thiết kế cơ bản: chúng là các công thức được thiết kế thủ công. Ai đó đã quyết định rằng độ chính xác n-gram, sự trùng lặp ký tự hoặc khoảng cách chỉnh sửa là một đại diện tốt cho chất lượng dịch thuật, và sau đó mọi người đã sử dụng công thức đó trong một thập kỷ.

Cuộc cách mạng metric nơ-ron bắt đầu với một câu hỏi khác: *điều gì sẽ xảy ra nếu chúng ta huấn luyện một mô hình để dự đoán chất lượng dịch thuật, giống như cách chúng ta huấn luyện các mô hình để dịch?*

### BERTScore (Zhang et al., 2020)

BERTScore, được xuất bản tại ICLR 2020 bởi Tianyi Zhang và các đồng nghiệp tại Cornell và MIT, là metric đầu tiên được áp dụng rộng rãi chuyển việc đánh giá từ khớp chuỗi chính xác sang độ tương đồng ngữ nghĩa. Cơ chế này rất trang nhã: mã hóa cả bản dịch giả thuyết và bản dịch tham chiếu thông qua một mô hình Transformer tiền huấn luyện (BERT, RoBERTa, hoặc DeBERTa), tính toán độ tương đồng cosine giữa mọi cặp nhúng token (token embedding), và sau đó sử dụng khớp tham lam (greedy matching) để tính toán độ chính xác (mỗi token giả thuyết khớp tốt nhất với token nào trong bản dịch tham chiếu), độ gợi nhớ (mỗi token tham chiếu khớp tốt nhất với token nào trong bản dịch giả thuyết), và F1.

BERTScore xử lý các từ đồng nghĩa, diễn đạt lại (paraphrase) và các biến thể trật tự từ một cách tự nhiên — "the feline rested on the rug" có độ tương đồng cao với "the cat sat on the mat" vì các nhúng ngữ cảnh (contextual embeddings) nắm bắt được sự tương đương về mặt ngữ nghĩa. Với mBERT (multilingual BERT), nó mở rộng sang bất kỳ ngôn ngữ nào mà mô hình hỗ trợ.

Nhưng BERTScore không được *huấn luyện* trên các đánh giá chất lượng của con người. Nó sử dụng các nhúng tiền huấn luyện nguyên bản, điều đó có nghĩa là nó nắm bắt độ tương đồng ngữ nghĩa chung chung chứ không học cụ thể những gì tạo nên một bản dịch *tốt*. Sự khác biệt này rất quan trọng: một câu có thể tương đồng về mặt ngữ nghĩa với bản dịch tham chiếu nhưng lại là một bản dịch tồi (sai văn phong, bỏ sót phủ định, tự tạo thêm từ hạn định). BERTScore cũng thừa hưởng bất kỳ sự thiên vị ngôn ngữ nào tồn tại trong mô hình nền tảng — đối với các ngôn ngữ ít xuất hiện trong dữ liệu huấn luyện của BERT, các nhúng có thể không nắm bắt được các sự khác biệt có ý nghĩa.

### BLEURT (Sellam et al., 2020)

BLEURT (Bilingual Evaluation Understudy with Representations from Transformers), được xuất bản tại ACL 2020 bởi Thibault Sellam, Dipanjan Das, và Ankur Parikh tại Google, đã giới thiệu một cải tiến quan trọng: **tiền huấn luyện trên các biến thể nhân tạo (synthetic perturbations)** trước khi tinh chỉnh (fine-tuning) trên các đánh giá của con người. Ý tưởng cốt lõi là việc tinh chỉnh trực tiếp một mô hình ngôn ngữ trên các tập dữ liệu đánh giá nhỏ của con người từ WMT sẽ tạo ra một metric rất mong manh — nó quá khớp (overfit) với các mẫu cụ thể trong dữ liệu huấn luyện và thất bại trên các đầu vào nằm ngoài phân phối.

Giải pháp của BLEURT là một quy trình huấn luyện hai giai đoạn. Trong giai đoạn một, hàng triệu cặp câu nhân tạo được tạo ra thông qua việc lược bỏ từ ngẫu nhiên, thêm từ, thay thế và dịch ngược (backtranslation). Mô hình được huấn luyện để dự đoán điểm số của các metric tự động hiện có (BLEU, ROUGE, BERTScore, entailment) cho các cặp câu này — từ đó học được các khái niệm chung về độ tương đồng văn bản. Trong giai đoạn hai, mô hình tiền huấn luyện được tinh chỉnh trên các điểm số Đánh giá Trực tiếp (Direct Assessment) của WMT. Quá trình "khởi động" này đã cải thiện đáng kể độ mạnh mẽ (robustness) của mô hình.

BLEURT-20 đã mở rộng phương pháp này sang đánh giá đa ngôn ngữ bằng cách sử dụng bộ mã hóa RemBERT của Google. Nhưng BLEURT vẫn chỉ dựa trên bản dịch tham chiếu — nó không sử dụng văn bản nguồn, điều đó có nghĩa là nó không thể phát hiện các lỗi ảo tưởng (hallucination) trông có vẻ trôi chảy, và nó phụ thuộc hoàn toàn vào chất lượng của bản dịch tham chiếu.

### COMET (Rei et al., 2020)

COMET (Crosslingual Optimized Metric for Evaluation of Translation) đại diện cho trạng thái công nghệ hiện tại (state of the art) trong việc đánh giá dịch máy tự động. Được phát triển bởi Ricardo Rei và các đồng nghiệp tại **Unbabel**, COMET sử dụng một bộ mã hóa đa ngôn ngữ (XLM-RoBERTa) để nhúng ba đầu vào — câu nguồn, bản dịch giả thuyết MT, và bản dịch tham chiếu — và dự đoán điểm chất lượng được huấn luyện trên các đánh giá trực tiếp của con người.

COMET đã giành chiến thắng hoặc đứng đầu trong các nhiệm vụ chung WMT Metrics từ năm 2020 trở đi. Mối tương quan của nó với đánh giá của con người cao hơn đáng kể so với bất kỳ metric khớp chuỗi nào. Nó nhận biết các cách diễn đạt lại, nắm bắt việc bảo toàn ý nghĩa và xử lý các biến thể từ đồng nghĩa mà BLEU hoàn toàn bỏ sót.

Nhưng COMET có một hạn chế nghiêm trọng đối với mục đích của chúng ta: nó được huấn luyện trên các đánh giá của con người từ WMT, vốn áp đảo là các ngôn ngữ châu Âu. Bộ mã hóa đa ngôn ngữ của nó (XLM-R) được huấn luyện trên dữ liệu CommonCrawl, nơi mà tiếng Plains Cree, North Sámi và hầu hết các ngôn ngữ bản địa gần như vắng bóng. Đối với các ngôn ngữ này, các biểu diễn nội bộ của COMET là không đáng tin cậy — nó có thể tạo ra điểm số, nhưng những điểm số đó không dựa trên bất kỳ sự hiểu biết thực sự nào về cấu trúc của ngôn ngữ.

### xCOMET (Guerreiro et al., 2024)

xCOMET, được xuất bản trên TACL 2024 bởi Nuno Guerreiro, Ricardo Rei và các đồng nghiệp tại Unbabel và Instituto Superior Técnico, đã mở rộng COMET từ một bộ chấm điểm hộp đen thành một **công cụ chẩn đoán** (diagnostic tool). Cải tiến chính là học đa nhiệm (multi-task learning): bên cạnh điểm chất lượng ở cấp độ câu, xCOMET thực hiện **gán nhãn chuỗi ở cấp độ phụ từ** (subword-level sequence tagging) để xác định các phân đoạn lỗi cụ thể trong bản dịch và phân loại chúng thành lỗi nhỏ (minor), lỗi lớn (major) hoặc lỗi nghiêm trọng (critical).

Điều này thu hẹp khoảng cách giữa chấm điểm tự động và phân tích lỗi của con người theo chuẩn MQM. Thay vì chỉ báo cáo "bản dịch này đạt điểm 0.73", xCOMET có thể chỉ ra những từ cụ thể nào bị sai và mức độ nghiêm trọng ra sao. Quá trình huấn luyện sử dụng phương pháp học theo lộ trình (curriculum learning): đầu tiên huấn luyện trên dữ liệu Đánh giá Trực tiếp cho tác vụ hồi quy cấp độ câu, sau đó thêm dữ liệu được gán nhãn MQM với các nhãn phân đoạn lỗi để huấn luyện chung.

xCOMET đã đạt được hiệu suất tối ưu đồng thời ở cả đánh giá cấp độ câu, cấp độ hệ thống và cấp độ phân đoạn lỗi. Nó hoạt động ở cả chế độ có bản dịch tham chiếu và không có bản dịch tham chiếu. Nhưng nó đòi hỏi dữ liệu huấn luyện được gán nhãn MQM — vốn rất tốn kém để tạo ra và hầu như chỉ tồn tại cho các cặp ngôn ngữ châu Âu.

### AfriCOMET (Wang & Adelani, NAACL 2024)

AfriCOMET, được xuất bản tại NAACL 2024 bởi Jiayi Wang, David Ifeoluwa Adelani và các đồng nghiệp trong cộng đồng Masakhane, là minh chứng quan trọng nhất cho thấy các metric nơ-ron *phải* được điều chỉnh cho các ngôn ngữ ít được hỗ trợ — chúng không thể tự động tổng quát hóa một cách hiệu quả.

Bài báo đầu tiên chứng minh vấn đề: COMET tiêu chuẩn, được huấn luyện trên dữ liệu WMT từ các ngôn ngữ châu Âu, cho thấy mối tương quan yếu hơn đáng kể với đánh giá của con người khi áp dụng cho 13 ngôn ngữ châu Phi (bao gồm tiếng Amharic, Hausa, Igbo, Swahili, Yoruba và Zulu). Giải pháp đòi hỏi hai thay đổi. Đầu tiên, thay thế XLM-R bằng **AfroXLM-R**, một bộ mã hóa đa ngôn ngữ được huấn luyện đặc biệt để biểu diễn tốt hơn các ngôn ngữ châu Phi. Thứ hai, tạo ra **AfriMTE**, một tập dữ liệu đánh giá của con người mới với các hướng dẫn MQM được đơn giản hóa dành cho những người gán nhãn không chuyên — vì việc tìm kiếm các dịch giả chuyên nghiệp song ngữ cho các ngôn ngữ này là rất khó khăn.

AfriCOMET đã chứng minh tính khả thi của ý tưởng: một metric nơ-ron đặc thù cho một ngữ hệ có thể vượt trội hơn đáng kể so với phiên bản chung chung. Nhưng nó cũng chứng minh chi phí đi kèm: ai đó phải xây dựng AfroXLM-R, thu thập dữ liệu đánh giá của con người cho 13 ngôn ngữ và huấn luyện một mô hình mới. Đối với tiếng Plains Cree, không có bộ mã hóa tương đương, tập dữ liệu đánh giá của con người hay metric thích ứng nào tồn tại. Con đường của AfriCOMET sẽ đòi hỏi phải tạo ra tất cả những thứ này từ đầu — một nỗ lực kéo dài nhiều năm liên quan đến đánh giá của con người dựa trên cộng đồng và có thể là một bộ mã hóa chuyên dụng cho ngữ hệ Algonquian.

### GEMBA: LLM đóng vai trò người đánh giá (Kocmi & Federmann, 2023)

GEMBA (GPT Estimation Metric Based Assessment), được xuất bản tại EAMT 2023 bởi Tom Kocmi và Christian Federmann tại Microsoft, đã đặt ra một câu hỏi táo bạo: điều gì sẽ xảy ra nếu bạn chỉ cần *hỏi* GPT-4 xem một bản dịch có tốt hay không?

Cách tiếp cận này đơn giản đến mức đáng ngạc nhiên. **GEMBA-DA** gợi ý (prompt) LLM với câu nguồn và bản dịch giả thuyết rồi yêu cầu đưa ra điểm chất lượng trên thang điểm 0–100. **GEMBA-MQM** cung cấp ba ví dụ được gán nhãn và yêu cầu LLM xác định các phân đoạn lỗi cụ thể, phân loại chúng theo loại và mức độ nghiêm trọng, và đưa ra điểm số theo phong cách MQM. Không cần huấn luyện đặc thù cho metric.

Kết quả rất ấn tượng: ở cấp độ hệ thống, GEMBA đạt được mối tương quan cạnh tranh hoặc tối ưu với đánh giá của con người. Các gán nhãn lỗi của GEMBA-MQM, mặc dù không đáng tin cậy bằng người đánh giá chuyên nghiệp, nhưng đã cung cấp thông tin chẩn đoán có thể giải thích được mà không cần bất kỳ quá trình huấn luyện chuyên biệt nào.

Nhưng GEMBA cũng dấy lên những lo ngại nghiêm trọng. Nó phụ thuộc vào các mô hình nguồn đóng độc quyền có hành vi thay đổi giữa các phiên bản API. Kết quả không thể tái lập theo nghĩa nghiêm ngặt. Chi phí vận hành lớn ở quy mô rộng (chi phí API để đánh giá toàn bộ tập kiểm thử WMT). Và — điều quan trọng đối với mục đích của chúng ta — sự hiểu biết của LLM về các ngôn ngữ tài nguyên thấp là không chắc chắn. GPT-4 có thể hiểu hoặc không hiểu hình thái học tiếng Plains Cree đủ tốt để đánh giá các bản dịch; không có cách nào để biết mà không thử nghiệm, và không có gì đảm bảo hành vi đó sẽ nhất quán qua các bản cập nhật mô hình. Bản thân Kocmi và Federmann đã khuyên không nên sử dụng GEMBA để tuyên bố về những cải tiến trong các bài báo khoa học do tính chất hộp đen của việc đánh giá này.

### MetricX và WMT 2024 Metrics Shared Task

**MetricX-24**, được phát triển bởi Juraj Juraska, Daniel Deutsch, Mara Finkelstein, và Markus Freitag tại Google, đã giành chiến thắng trong WMT 2024 Metrics Shared Task. Được xây dựng trên **mT5** (Multilingual T5, một mô hình encoder-decoder thay vì chỉ encoder như XLM-R được sử dụng bởi COMET), MetricX đi theo một con đường kiến trúc khác. Nó sử dụng tinh chỉnh hai giai đoạn — đầu tiên trên dữ liệu Đánh giá Trực tiếp, sau đó trên điểm số MQM — với việc **tăng cường dữ liệu nhân tạo** trên diện rộng nhắm vào các lỗi thường gặp của metric (dịch thiếu, dịch trôi chảy nhưng sai nghĩa, ảo tưởng).

Bài báo tổng kết của WMT 2024, mang tên **"Are LLMs Breaking MT Metrics?"** (Liệu các LLM có đang phá vỡ các metric dịch máy?), đã đặt câu hỏi liệu các bản dịch do LLM tạo ra có làm hỏng hệ sinh thái metric hay không. Câu trả lời là không hẳn: các metric nơ-ron được tinh chỉnh (MetricX-24, các biến thể COMET) vẫn hiệu quả, mặc dù các metric dựa trên LLM (các biến thể GEMBA) cho thấy sức mạnh đáng ngạc nhiên ở cấp độ hệ thống. Các phát hiện chính bao gồm:

- **Các metric nhận biết nguồn** (sử dụng nguồn + tham chiếu + giả thuyết) liên tục vượt trội hơn các metric chỉ dựa trên bản dịch tham chiếu.
- **Các mô hình lai** hoạt động ở cả chế độ có bản dịch tham chiếu và không có bản dịch tham chiếu từ một kiến trúc duy nhất là hướng đi mới đang nổi lên.
- **Khoảng cách tài nguyên thấp** vẫn tồn tại: tất cả các metric đều hoạt động kém hơn trên các ngôn ngữ ít phổ biến, và khoảng cách này không hề thu hẹp.
- **Các metric được huấn luyện trên MQM** (sử dụng các gán nhãn lỗi chi tiết) liên tục vượt trội hơn các metric được huấn luyện trên DA (sử dụng điểm số vô hướng).

Các hàm ý cho việc đánh giá tài nguyên thấp là rất rõ ràng: ngành dịch máy đang hội tụ về các metric nơ-ron lớn, được huấn luyện và nhận biết nguồn như một tiêu chuẩn vàng. Các metric này đòi hỏi lượng dữ liệu huấn luyện, tài nguyên tính toán đáng kể và — quan trọng nhất — dữ liệu đánh giá của con người trong ngôn ngữ đích. Đối với các ngôn ngữ không có bất kỳ tài nguyên nào trong số này, quy trình metric tiên tiến nhất đơn giản là không thể áp dụng.

### Vấn đề thiên vị: Metric nơ-ron và ngôn ngữ tài nguyên thấp

Cuộc cách mạng metric nơ-ron, phần lớn, là một hiện tượng của các ngôn ngữ tài nguyên cao. Mọi metric được huấn luyện trong các phần trước đều được huấn luyện trên dữ liệu đánh giá của con người từ WMT, vốn chỉ bao phủ khoảng 20 cặp ngôn ngữ — tất cả đều liên quan đến các ngôn ngữ châu Âu, tiếng Trung hoặc tiếng Nhật. Các bộ mã hóa nền tảng (XLM-R, mT5, InfoXLM) được huấn luyện trên dữ liệu CommonCrawl, nơi mức độ đại diện tỷ lệ thuận với sự hiện diện trên web: tiếng Anh thống trị, các ngôn ngữ châu Âu được bao phủ tốt, và phần lớn trong số hơn 7.000 ngôn ngữ trên thế giới thực tế là vắng bóng.

Đối với một ngôn ngữ như tiếng Plains Cree, điều này tạo ra một chuỗi thất bại liên hoàn:

1. **Không có dữ liệu huấn luyện**: Không có đánh giá của con người từ WMT cho các bản dịch tiếng Cree, vì vậy không có metric nào được huấn luyện để đánh giá chúng.
2. **Không có độ bao phủ của bộ mã hóa**: Từ vựng của XLM-R được xây dựng trên CommonCrawl, nơi văn bản tiếng Cree cực kỳ hiếm. Bộ tách từ (tokenizer) phân tách các từ tiếng Cree thành các phân đoạn byte tùy ý, và các nhúng ngữ cảnh cho các phân đoạn đó được huấn luyện rất kém.
3. **Không có xác thực**: Chưa có ai đo lường xem liệu COMET, BLEURT, hoặc MetricX có tạo ra điểm số có ý nghĩa cho tiếng Cree hay không. Chúng có thể tạo ra *các con số*, nhưng không có bằng chứng nào cho thấy các con số đó tương quan với chất lượng dịch thuật thực tế.
4. **Không có con đường cải tiến**: Cách tiếp cận của AfriCOMET — xây dựng một bộ mã hóa đặc thù cho ngữ hệ, thu thập dữ liệu đánh giá của con người, huấn luyện một metric mới — là một nỗ lực kéo dài nhiều năm của nhiều tổ chức. Đối với một cộng đồng ngôn ngữ chỉ có 27.000 người nói, cơ sở hạ tầng nghiên cứu để hỗ trợ việc này hiện không tồn tại.

Kết quả là một nghịch lý: những ngôn ngữ cần đánh giá dịch máy khẩn cấp nhất (vì hệ thống dịch máy của chúng yếu nhất và cần đánh giá cẩn thận nhất) lại chính là những ngôn ngữ mà các công cụ đánh giá tốt nhất hoạt động kém tin cậy nhất. Câu trả lời của ngành là khuyến nghị sử dụng chrF++ như một giải pháp thay thế "đủ tốt" — và nó thực sự tốt hơn BLEU — nhưng chrF++ vẫn là một metric khớp chuỗi không thể phát hiện sự tương đương, không thể xử lý trật tự từ tự do và không có khái niệm về tính hợp lệ của hình thái học.

---

## Phần 3: Vượt ra ngoài việc chấm điểm — Đánh giá chẩn đoán và ngôn ngữ học

### Sự phân chia giữa Độ đầy đủ và Độ trôi chảy

Trước khi các metric tự động tồn tại, việc đánh giá dịch máy của con người đã sử dụng một khung đánh giá với hai chiều: **độ đầy đủ** (adequacy - bản dịch có truyền tải được ý nghĩa của nguồn không?) và **độ trôi chảy** (fluency - bản dịch có đúng ngữ pháp và tự nhiên trong ngôn ngữ đích không?). Sự phân biệt này, được hệ thống hóa trong các đánh giá dịch máy ban đầu của DARPA và sau đó là tại NIST, đã thừa nhận một điều mà các metric tự động phải mất hai thập kỷ để cố gắng tái hiện: chất lượng dịch thuật không phải là một chiều.

Khung đánh giá độ đầy đủ/độ trôi chảy đã không còn được ưa chuộng khi Đánh giá Trực tiếp (một điểm số vô hướng duy nhất) thay thế nó tại WMT. Nhưng ý tưởng cốt lõi vẫn rất quan trọng: một bản dịch có thể trôi chảy nhưng sai nghĩa (ảo tưởng), hoặc không trôi chảy nhưng đúng nghĩa (biến thể hình thái). Không một điểm số đơn lẻ nào có thể nắm bắt được cả hai.

### MQM: Tiêu chuẩn vàng (Lommel et al., 2014; Freitag et al., 2021)

**Hệ số Chất lượng Đa chiều (MQM)** đã thay thế Đánh giá Trực tiếp để trở thành phương pháp đánh giá chính của con người tại WMT từ năm 2021 trở đi. MQM sử dụng các dịch giả chuyên nghiệp để đánh dấu các phân đoạn lỗi cụ thể, phân loại chúng theo loại (dịch sai, bỏ sót, thêm từ, ngữ pháp, thuật ngữ) và mức độ nghiêm trọng (nhỏ = 1 điểm, lớn = 5 điểm, nghiêm trọng = 25 điểm). Điều này tạo ra cả điểm chất lượng và thông tin chẩn đoán có thể hành động được.

MQM là phương pháp gần nhất với một phương pháp đánh giá "chính xác" — nó không chỉ cho bạn biết bản dịch *tệ đến mức nào*, mà còn cho biết *cụ thể điều gì đã sai*. Nhưng nó đòi hỏi các dịch giả chuyên nghiệp song ngữ, vốn là nguồn lực không tồn tại đủ nhiều đối với hầu hết các ngôn ngữ tài nguyên thấp để thực hiện đánh giá đáng tin cậy về mặt thống kê.

### MorphEval: Đánh giá hình thái học tương phản (Burlot & Yvon, 2017)

MorphEval là nghiên cứu tiền đề trực tiếp nhất cho việc đánh giá dịch máy nhận biết hình thái học. Được giới thiệu bởi Franck Burlot và François Yvon tại WMT 2017 và mở rộng vào năm 2018, MorphEval đánh giá *năng lực* hình thái học bằng cách sử dụng **các bộ kiểm thử tương phản** (contrastive test suites).

**Cách hoạt động:** Bộ kiểm thử bao gồm các cặp câu trong ngôn ngữ nguồn chỉ khác nhau đúng một tương phản hình thái — ví dụ: số ít so với số nhiều, hiện tại so với quá khứ, giống đực so với giống cái. Hệ thống dịch máy sẽ dịch cả hai câu. Nếu hệ thống truyền tải chính xác sự tương phản trong các bản dịch của nó (ví dụ: tạo ra một đầu ra số nhiều khi nguồn là số nhiều và đầu ra số ít khi nguồn là số ít), tương phản đó được tính là chính xác.

**Các ngôn ngữ được bao phủ:** Anh→Séc, Anh→Latvia (v1, WMT 2017); mở rộng sang Anh→Pháp, Anh→Đức, Anh→Phần Lan, Thổ Nhĩ Kỳ→Anh (v2, WMT 2018).

**Các phát hiện chính:** MorphEval tiết lộ rằng ngay cả các hệ thống dịch máy nơ-ron hàng đầu cũng có những thất bại mang tính hệ thống về hình thái học — chúng có thể tạo ra đầu ra trôi chảy trong khi dịch sai thì, số hoặc cách. Những lỗi này vô hình trước BLEU và thậm chí vô hình một phần trước cả COMET.

**Tính khả dụng:** Mã nguồn mở trên GitHub ([franckbrl/morpheval](https://github.com/franckbrl/morpheval), [franckbrl/morpheval_v2](https://github.com/franckbrl/morpheval_v2)).

**Hạn chế:** MorphEval đòi hỏi các bộ kiểm thử tương phản được thiết kế thủ công cho từng ngôn ngữ đích bởi các nhà ngôn ngữ học hiểu rõ các tương phản hình thái của ngôn ngữ đó. Không có bộ kiểm thử nào tồn tại cho bất kỳ ngôn ngữ đa tổng hợp nào. Phương pháp này kiểm tra *năng lực* (hệ thống có thể xử lý tương phản này không?) chứ không kiểm tra *tính hợp lệ* (hệ thống có tạo ra các từ thực tế không?) hay *tính tương đương* (hai bản dịch khác nhau này có cùng chính xác không?).

### CheckList: Kiểm thử hành vi cho NLP (Ribeiro et al., ACL 2020)

**CheckList**, được xuất bản tại ACL 2020 bởi Marco Tulio Ribeiro và các đồng nghiệp (đạt giải Bài báo xuất sắc nhất), đã nhập khẩu một ý tưởng từ kỹ nghệ phần mềm vào việc đánh giá NLP: **kiểm thử đơn vị** (unit testing). Thay vì đánh giá hiệu suất tổng hợp của mô hình trên một điểm chuẩn, CheckList định nghĩa một ma trận các **năng lực** (từ vựng, phủ định, thực thể đặt tên, suy luận thời gian, đồng tham chiếu) kết hợp với các **loại kiểm thử**:

- **Kiểm thử chức năng tối thiểu (MFT)**: Các trường hợp kiểm thử đơn giản, có mục tiêu rõ ràng mà bất kỳ mô hình có năng lực nào cũng phải vượt qua.
- **Kiểm thử tính bất biến (INV)**: Các biến đổi đối với đầu vào mà *không nên* làm thay đổi đầu ra (ví dụ: thay đổi một cái tên không nên làm thay đổi cảm xúc).
- **Kiểm thử kỳ vọng định hướng (DIR)**: Các biến đổi *nên* làm thay đổi đầu ra theo một hướng có thể dự đoán được.

CheckList ban đầu được thiết kế cho phân tích cảm xúc và suy luận ngôn ngữ tự nhiên (NLI), nhưng mô hình này hoàn toàn có thể áp dụng trực tiếp cho dịch máy. Người ta có thể tạo ra các MFT cho các hiện tượng hình thái học ("hệ thống có tạo ra dạng số nhiều chính xác không?"), các kiểm thử INV cho trật tự từ tự do ("việc thay đổi trật tự từ tiếng Cree có làm thay đổi bản dịch tiếng Anh không?"), và các kiểm thử DIR cho các đặc trưng hình thái ("việc thay đổi nguồn từ thì quá khứ sang thì hiện tại có làm thay đổi thì của đích không?").

Mô hình CheckList đặc biệt phù hợp vì nó hệ thống hóa những gì MorphEval thực hiện một cách trực quan: kiểm thử các năng lực cụ thể thay vì đo lường các điểm số tổng hợp. Các lớp biến thể của bộ linter của chúng tôi (WORD_ORDER, ORTHOGRAPHIC, OPTIONAL_PARTICLE, v.v.) thực chất là các quy tắc bất biến — chúng định nghĩa các biến đổi không nên làm thay đổi kết quả đánh giá.

### Bộ thử thách và Đánh giá mục tiêu

Mô hình rộng hơn của **các bộ thử thách (challenge sets)** — các bộ kiểm thử được thiết kế thủ công nhắm vào các hiện tượng ngôn ngữ cụ thể — đã trở thành một phương pháp đánh giá bổ sung được thiết lập tại WMT từ khoảng năm 2017.

**Isabelle, Cherry & Foster (2017)**, tại NRC Canada, đã tiên phong trong cách tiếp cận này cho dịch máy với các bộ kiểm thử được thiết kế thủ công nhằm cô lập các sự khác biệt cấu trúc giữa các ngôn ngữ — những trường hợp mà dịch thô (literal translation) có khả năng cao là sai. Nghiên cứu tiếp theo của họ (Isabelle & Kuhn, 2018) đã xây dựng 506 câu tiếng Pháp nhắm vào các thách thức dịch thuật cụ thể, cung cấp bức tranh chi tiết về năng lực của hệ thống.

**LingEval97** (Sennrich, EACL 2017) đã tạo ra 97.000 cặp dịch tương phản Anh→Đức để kiểm tra xem các mô hình NMT có gán xác suất cao hơn cho các bản dịch chính xác so với các cặp câu có lỗi cú pháp hình thái được đưa vào hay không. Một phát hiện chính: các mô hình cấp độ ký tự xuất sắc trong việc chuyển tự (transliteration) nhưng hoạt động kém hơn trong việc duy trì sự hòa hợp cú pháp hình thái ở khoảng cách xa.

**ACES** (Amrhein, Moghe & Guillou, 2022–2023) đã mở rộng quy mô tiếp cận bộ thử thách một cách mạnh mẽ: 36,476 ví dụ trải dài trên 146 cặp ngôn ngữ kiểm thử 68 hiện tượng ngôn ngữ khác nhau. ACES đã được sử dụng để siêu đánh giá (meta-evaluate) các metric được gửi đến nhiệm vụ chung WMT metrics — kiểm thử xem liệu các *metric* có thể phát hiện các tương phản hay không, chứ không chỉ là liệu các *hệ thống* có thể tạo ra chúng hay không. Được mở rộng thành **SPAN-ACES** với các gán nhãn phân đoạn lỗi.

**MT-GenEval** (Currey et al., EMNLP 2022) và **WinoMT** (Stanovsky, Smith & Zettlemoyer, ACL 2019) nhắm vào độ chính xác về giới tính cụ thể. WinoMT đáng chú ý vì nó sử dụng rõ ràng **phân tích hình thái học** trên ngôn ngữ đích để xác minh giới tính của các nghề nghiệp được dịch — một trong số ít trường hợp bộ phân tích hình thái học được sử dụng như một phần của công cụ đánh giá dịch máy.

**Hjerson** (Popović & Ney, 2011) là một công cụ mã nguồn mở để phân loại lỗi dịch máy tự động sử dụng **lemma và nhãn từ loại (POS tags)** để phân loại lỗi thành năm loại: hình thái, trật tự từ, thiếu từ, thừa từ và lỗi từ vựng. Đây có lẽ là nghiên cứu tiền đề gần nhất với bộ linter của chúng tôi về mặt tinh thần — nó sử dụng phân tích ngôn ngữ học để cung cấp các danh mục lỗi chẩn đoán thay vì một điểm số duy nhất.

Sợi chỉ đỏ xuyên suốt: ngành dịch máy đã thừa nhận, nhiều lần, rằng các điểm số tổng hợp là không đủ. Đánh giá chẩn đoán cung cấp độ chi tiết cần thiết để hiểu *tại sao* một hệ thống thất bại. Nhưng các phương pháp chẩn đoán đòi hỏi chuyên môn ngôn ngữ học cho từng ngôn ngữ, và chuyên môn đó hiện đang tập trung chủ yếu ở các ngôn ngữ châu Âu.

### AmericasNLP: Đánh giá trong thực tế khó khăn

Chuỗi hội thảo AmericasNLP (đồng tổ chức với NAACL), tập trung vào NLP cho các ngôn ngữ bản địa của châu Mỹ, cung cấp điểm so sánh trực tiếp nhất cho các thách thức đánh giá của chúng tôi.

Từ năm 2021 đến năm 2023, nhiệm vụ chung đã sử dụng **chrF** làm metric đánh giá chính — được chọn vì tính mạnh mẽ của nó trong các thiết lập tài nguyên thấp và khả năng khớp ở cấp độ ký tự, giúp tính điểm một phần cho sự trùng lặp hình thái. Ban tổ chức thừa nhận các hạn chế của chrF nhưng không có giải pháp thay thế nào tốt hơn có thể hoạt động trên các loại hình ngôn ngữ đa dạng được đại diện (Quechua, Guaraní, Aymara, Nahuatl, Rarámuri, và các ngôn ngữ khác).

Vào năm 2025, AmericasNLP đã giới thiệu một **Nhiệm vụ chung 3 (Shared Task 3)** chuyên biệt dành riêng cho việc phát triển các metric đánh giá dịch máy cho các ngôn ngữ bản địa — lần đầu tiên ngành dịch máy thừa nhận một cách rõ ràng rằng các metric hiện tại là không đầy đủ cho các ngôn ngữ này. Giải pháp giành chiến thắng, **FUSE** (Feature-Union Scorer), đã kết hợp các nhúng câu đa ngôn ngữ (LaBSE được tinh chỉnh), độ tương đồng từ vựng, độ tương đồng ngữ âm và khớp token mờ thông qua hồi quy Ridge và Gradient Boosting. FUSE không sử dụng các bộ phân tích hình thái học — việc thiết kế đặc trưng (feature engineering) của nó không phụ thuộc vào ngôn ngữ.

Đây chính là khoảng trống mà nghiên cứu của chúng tôi lấp đầy. AmericasNLP đã xác định được vấn đề (các metric tiêu chuẩn thất bại đối với các ngôn ngữ bản địa) và bắt đầu phát triển các giải pháp thay thế (FUSE). Nhưng không có giải pháp thay thế nào sử dụng kiến thức hình thái học mà các FST cung cấp. Cộng đồng AmericasNLP sử dụng chrF++ vì đó là tùy chọn chung tốt nhất hiện có, trong khi cộng đồng GiellaLT xây dựng các công cụ hình thái học tinh vi nhưng chưa bao giờ được tích hợp vào việc đánh giá dịch máy. Hai cộng đồng này vẫn chưa hội tụ.

---

## Phần 4: Đánh giá không cần bản dịch tham chiếu và Ước lượng chất lượng

Một số tín hiệu đánh giá quan trọng nhất trong khung thử nghiệm của chúng tôi hoàn toàn không yêu cầu bản dịch tham chiếu. Việc kiểm tra tính hợp lệ của FST ("đây có phải là một từ thực tế không?") chỉ cần đầu ra của dịch máy. Bộ phát hiện ảo tưởng cần câu nguồn và bản dịch giả thuyết. Bộ phát hiện chuyển mã ngôn ngữ chỉ cần bản dịch giả thuyết và kiến thức về hệ chữ viết của ngôn ngữ đích. Việc hiểu rõ vị trí của các công cụ này trong bức tranh rộng lớn hơn của đánh giá không cần bản dịch tham chiếu là điều cần thiết để định vị chúng một cách chính xác.

### Mô hình ước lượng chất lượng

**Ước lượng chất lượng (Quality Estimation - QE)** là một nhánh của đánh giá dịch máy liên quan đến việc dự đoán chất lượng dịch thuật *không cần* bản dịch tham chiếu. Đây là một nhiệm vụ chung chuyên biệt tại WMT từ năm 2012, được thúc đẩy bởi nhu cầu thực tế là đánh giá chất lượng dịch máy tại thời điểm triển khai — khi bạn đang dịch văn bản mới và không có bản dịch tham chiếu của con người để so sánh.

Nhiệm vụ QE đã trải qua ba thế hệ. **QE dựa trên đặc trưng** (2012–2016) trích xuất các đặc trưng được thiết kế thủ công từ nguồn và giả thuyết — độ hỗn loạn (perplexity) của mô hình ngôn ngữ, tần suất từ, sự trùng lặp n-gram với dữ liệu đơn ngữ — và huấn luyện các bộ phân loại để dự đoán chất lượng. **QE nơ-ron** (2017–2021) thay thế các đặc trưng thủ công bằng các biểu diễn học được, thường sử dụng các bộ mã hóa song ngữ. **QE hiện tại** (2022–nay) được thống trị bởi các phương pháp dựa trên COMET, đặc biệt là **CometKiwi**.

### CometKiwi và COMET không cần bản dịch tham chiếu

**CometKiwi** (Rei et al., WMT 2022), biến thể không cần bản dịch tham chiếu của COMET, sử dụng InfoXLM để mã hóa câu nguồn và bản dịch giả thuyết MT (không cần bản dịch tham chiếu) và dự đoán điểm chất lượng. Nó đã đạt được kết quả tối ưu trong các nhiệm vụ chung QE của WMT 2022 và 2023.

Phát hiện đáng chú ý: CometKiwi không cần bản dịch tham chiếu đạt được mối tương quan gần tương đương với đánh giá của con người so với COMET có bản dịch tham chiếu. Điều này gợi ý rằng, đối với các ngôn ngữ giàu tài nguyên, văn bản nguồn chứa đựng lượng tín hiệu đánh giá gần như tương đương với bản dịch tham chiếu. Nhưng cảnh báo tương tự vẫn áp dụng: bộ mã hóa của CometKiwi có mức độ biểu diễn tối thiểu cho các ngôn ngữ tài nguyên thấp, vì vậy các dự đoán không cần bản dịch tham chiếu của nó cho tiếng Cree hoặc Sámi là không đáng tin cậy.

Đây là điểm mà các metric dựa trên FST của chúng tôi mang lại một điều gì đó thực sự khác biệt. Việc kiểm tra tính hợp lệ của FST là một **tín hiệu chất lượng tất định, không cần bản dịch tham chiếu** không đòi hỏi mô hình được huấn luyện và không cần dữ liệu đánh giá của con người. Nếu FST nói một từ không phải là từ tiếng Cree hợp lệ, thì từ đó không phải là từ tiếng Cree hợp lệ — ngoại trừ các trường hợp từ chối sai (false rejections) đối với từ mượn, từ mới và danh từ riêng. Loại tín hiệu chất lượng cứng, dựa trên quy tắc này không có thực thể tương đương trong hệ sinh thái QE nơ-ron.

### Phát hiện ảo tưởng trong dịch máy

Ảo tưởng (hallucination) trong dịch máy — đầu ra trôi chảy nhưng hoàn toàn không liên quan đến nguồn — là một lỗi nghiêm trọng, đặc biệt là trong các thiết lập tài nguyên thấp nơi các mô hình không có đủ dữ liệu huấn luyện để học các mối tương quan nguồn-đích đáng tin cậy.

Trạng thái công nghệ hiện tại trong nghiên cứu phát hiện ảo tưởng sử dụng một số phương pháp:

- **Phát hiện dựa trên nhúng**: So sánh các nhúng của nguồn và giả thuyết trong một không gian chung (LASER, LaBSE) và gắn cờ các trường hợp độ tương đồng dưới một ngưỡng nhất định.
- **Phát hiện dựa trên xác suất**: Sử dụng chính điểm số độ tin cậy của mô hình dịch máy — các lỗi ảo tưởng có xu hướng có xác suất đầu ra cao nhưng xác suất điều kiện nguồn thấp.
- **Biến đổi tương phản**: So sánh đầu ra dịch máy cho nguồn thực tế với đầu ra cho một nguồn bị biến đổi hoặc không liên quan; nếu các đầu ra giống nhau một cách đáng ngờ, mô hình đang bỏ qua nguồn.
- **LLM đóng vai trò trọng tài**: Gợi ý một LLM để đánh giá xem bản dịch có trung thực với nguồn hay không.

Khung thử nghiệm của chúng tôi sử dụng một **plugin phát hiện dựa trên thuật toán phỏng đoán (heuristic)** kết hợp bốn tín hiệu: sự phình to độ dài (bản dịch giả thuyết dài hơn nhiều so với mong đợi), sự lặp lại (các cụm từ bị lặp lại), sự không khớp thực thể (các thực thể đặt tên trong nguồn bị thiếu trong giả thuyết), và sự lặp lại nguồn (bản dịch giả thuyết quá giống với văn bản nguồn, gợi ý việc sao chép không dịch). Đây là mức cơ bản so với trạng thái công nghệ hiện tại của nghiên cứu — nó bắt được các lỗi ảo tưởng thô thiển nhưng sẽ bỏ sót các lỗi tinh vi. Giá trị của nó là một **bộ lọc không cần bản dịch tham chiếu, nhanh và rẻ** có thể gắn cờ các lỗi nghiêm trọng nhất mà không cần GPU hoặc gọi API.

### Phát hiện chuyển mã ngôn ngữ

Chuyển mã ngôn ngữ (code-switching) trong đầu ra dịch máy — nơi hệ thống tạo ra các từ bằng ngôn ngữ nguồn thay vì dịch chúng — là một lỗi khác biệt so với ảo tưởng. Nó thường xảy ra khi mô hình gặp một từ mà nó không thể dịch và quay lại sao chép nguồn.

Plugin phát hiện chuyển mã ngôn ngữ của chúng tôi sử dụng **phân tích khối Unicode** (phát hiện các ký tự từ hệ chữ viết của ngôn ngữ nguồn trong đầu ra đáng lẽ phải là ngôn ngữ đích) và **danh sách từ phổ biến** (xác định các từ nguồn có tần suất cao xuất hiện mà không được dịch). Đối với tiếng Cree, vốn sử dụng cả SRO (dựa trên ký tự Latin) và chữ âm tiết (syllabics), điều này đòi hỏi sự cẩn thận — tiếng Anh và SRO chia sẻ ký tự Latin, vì vậy chỉ riêng phân tích khối Unicode là không đủ.

Các tài liệu nghiên cứu về phát hiện chuyển mã ngôn ngữ trong dịch máy còn khá thưa thớt so với phát hiện ảo tưởng. Hầu hết các nghiên cứu tập trung vào chuyển mã ngôn ngữ trong văn bản *đầu vào* (người nói song ngữ trộn lẫn các ngôn ngữ) hơn là trong văn bản *đầu ra* (hệ thống dịch máy thất bại trong việc dịch). Cách tiếp cận dựa trên thuật toán phỏng đoán của chúng tôi, theo hiểu biết của chúng tôi, không bị tụt hậu đáng kể so với bất kỳ trạng thái công nghệ hiện tại nào được công bố cho vấn đề cụ thể này.

---

## Phần 5: Khoảng cách hình thái học

### Những điều các metric hiện tại không thể thấy

Đây là lập luận cốt lõi của tài liệu này, và nó đòi hỏi một minh chứng cụ thể.

Hãy xem xét cặp câu tiếng Plains Cree:

| | Văn bản |
|--|------|
| **Nguồn (tiếng Anh)** | "I saw the man" |
| **Tham chiếu (tiếng Cree)** | *nikî-wâpamâw nâpêw* |
| **Giả thuyết A** | *nâpêw nikî-wâpamâw* |
| **Giả thuyết B** | *nikî-wâpamikow nâpêsis* |

**Giả thuyết A** là một bản dịch hoàn hảo — nó có cùng các từ nhưng ở một trật tự khác, điều này hoàn toàn đúng ngữ pháp trong tiếng Cree (trật tự từ tự do). **Giả thuyết B** có nghĩa là "cậu bé đã được nhìn thấy bởi tôi" — sai hướng hành động (*-ikow* là thể nghịch đảo), sai đối tượng tác động (*nâpêsis* = "cậu bé", chứ không phải "người đàn ông").

| Metric | Giả thuyết A (đúng) | Giả thuyết B (sai) | Có thể phân biệt được không? |
|--------|----------------------|---------------------|------------------------|
| BLEU | ~30% | ~20% | Hầu như không |
| chrF++ | ~65% | ~55% | Phần nào |
| COMET | Không xác định (không có dữ liệu huấn luyện tiếng Cree) | Không xác định | Không đáng tin cậy |
| **FST chấp nhận** | 100% | 100% | Không (cả hai đều là tiếng Cree hợp lệ) |
| **Linter** | EQUIVALENT (WORD_ORDER) | MISS | **Có** |
| **Bộ xác thực ngữ nghĩa** | VALID | WRONG | **Có** |

Bộ linter và bộ xác thực ngữ nghĩa thành công ở những điểm mà BLEU, chrF++, và COMET thất bại — không phải vì chúng là "các metric tốt hơn" theo một nghĩa vạn năng nào đó, mà vì chúng có quyền truy cập vào *kiến thức ngôn ngữ học* mà các metric khớp chuỗi và metric nơ-ron không có. Chúng biết rằng tiếng Cree có trật tự từ tự do. Chúng biết rằng *wâpamêw* và *wâpamikow* là các lemma khác nhau với cấu trúc đối số khác nhau. Chúng biết rằng *nâpêw* và *nâpêsis* là các từ khác nhau.

Kiến thức này đến từ FST (mã hóa ngữ pháp hình thái), từ điển song ngữ (cung cấp nghĩa tiếng Anh cho mỗi lemma), và các lớp biến thể được định nghĩa thủ công (mã hóa các quy tắc tương đương dựa trên ngôn ngữ học). Không một kiến thức nào trong số này có sẵn cho một metric coi bản dịch thuần túy là một chuỗi ký tự.

### Tại sao ngành dịch máy vẫn chưa giải quyết vấn đề này

Khoảng cách hình thái học trong đánh giá dịch máy không phải là một bí ẩn. Ngành này biết nó tồn tại. Những lý do nó vẫn tồn tại mang tính cấu trúc:

1. **Thiên vị quy mô.** Cộng đồng đánh giá dịch máy tối ưu hóa cho các metric hoạt động trên tất cả các cặp ngôn ngữ của WMT. Các metric dựa trên FST hoạt động cho khoảng 30 ngôn ngữ. COMET hoạt động cho hơn 100 ngôn ngữ. chrF++ hoạt động cho tất cả các ngôn ngữ có hệ thống chữ viết. Cộng đồng phần thưởng cho tính vạn năng hơn là độ chính xác.

2. **Sự cô lập của các cộng đồng.** Những người xây dựng FST (các nhà ngôn ngữ học tính toán tại UiT Tromsø, NRC Canada, Đại học Alberta) và những người xây dựng các metric đánh giá (các nhà nghiên cứu ML tại Google, Unbabel, WMT) tham gia các hội nghị khác nhau, xuất bản ở các địa điểm khác nhau và hoạt động dưới các cấu trúc khuyến khích khác nhau. Sự giao thoa cần thiết để xây dựng các metric đánh giá dựa trên FST đã không xảy ra — không phải vì nó đã được thử nghiệm và thất bại, mà vì các cộng đồng chưa bao giờ hội tụ.

3. **Lo ngại về độ bao phủ.** Các FST có các vấn đề từ chối sai đã biết: từ mượn, từ mới và danh từ riêng có thể bị từ chối là không hợp lệ ngay cả khi chúng hoàn toàn có thể chấp nhận được. Điều này khiến các nhà nghiên cứu lo ngại về việc sử dụng FST làm metric — một lỗi từ chối sai sẽ làm tăng tỷ lệ lỗi một cách giả tạo. Mối lo ngại này là có cơ sở nhưng có thể định lượng được: việc đo lường tỷ lệ từ chối sai trên văn bản chuẩn đã biết là điều dễ dàng.

4. **Nhu cầu không đủ lớn.** Rất ít người đang xây dựng hệ thống dịch máy cho các ngôn ngữ đa tổng hợp, và những người đang làm việc đó (ALT Lab, NRC, những người tham gia AmericasNLP) thường sử dụng chrF++ vì đó là những gì đang tồn tại. Chưa có một nỗ lực phối hợp nào từ cộng đồng dịch máy tài nguyên thấp cho việc đánh giá nhận biết hình thái học, một phần vì cộng đồng này nhỏ và một phần vì việc xây dựng các metric như vậy đòi hỏi chuyên môn trong cả kỹ nghệ NLP và hình thái học của ngôn ngữ đích cụ thể.

5. **Giả định về metric nơ-ron.** Giả định phổ biến từ năm 2020 là các metric nơ-ron cuối cùng sẽ giải quyết được vấn đề hình thái học thông qua các biểu diễn học được. Nếu bạn huấn luyện COMET trên đủ dữ liệu từ các ngôn ngữ giàu hình thái, lập luận cho rằng, nó sẽ tự động học cách xử lý các biến thể hình thái một cách ngầm định. Điều này có thể đúng đối với các ngôn ngữ giàu hình thái tài nguyên cao (tiếng Phần Lan, Thổ Nhĩ Kỳ, Séc). Nhưng nó khó có thể đúng đối với các ngôn ngữ thực tế không có biểu diễn trong dữ liệu huấn luyện.

---

## Phần 6: LYSS — Giải pháp thay thế dựa trên ngôn ngữ học

### Những gì champollion đã xây dựng: LYSS (Linguistically-informed Yield & Structural Scoring)

Khung thử nghiệm đánh giá của dự án champollion triển khai một khung chấm điểm tổng hợp gọi là **LYSS** kết hợp các metric tiêu chuẩn (chrF++, khớp chính xác) với bốn danh mục metric dựa trên ngôn ngữ học. Tên gọi phản ánh trọng tâm của khung đánh giá này: đo lường *hiệu suất* (yield - bao nhiêu ý nghĩa được bảo toàn qua quá trình dịch) thông qua *chấm điểm cấu trúc* (structural scoring - các kiểm tra tất định, dựa trên ngôn ngữ học thay vì các nhúng học được).

#### 1. Cổng kiểm tra tính hợp lệ hình thái (GiellaLT FST Metric)

Metric đơn giản và có khả năng áp dụng rộng rãi nhất: đưa mọi từ của đầu ra dịch máy qua bộ phân tích hình thái học trạng thái hữu hạn GiellaLT cho ngôn ngữ đích. Nếu FST có thể phân tích một từ (trả về ít nhất một kết quả phân tích), từ đó hợp lệ về mặt hình thái. Nếu không, từ đó không tồn tại trong ngôn ngữ đích — đó là một từ tự tạo (hallucinated), một lỗi hình thái, một lỗi chính tả, hoặc một từ mượn không có trong từ điển.

**Đầu ra:** `fst_validity_rate` (0.0–1.0, càng cao càng tốt). Trung bình vĩ mô (trung bình cộng của tỷ lệ từng câu) và trung bình vi mô (tổng số từ hợp lệ / tổng số từ).

**Phụ thuộc:** `pyhfst` (các liên kết Python của Công nghệ Trạng thái Hữu hạn Helsinki), một tệp phân tích `.hfstol` đã được biên dịch cho ngôn ngữ đích.

**Khả năng mở rộng:** Hoạt động cho bất kỳ ngôn ngữ nào có bộ phân tích GiellaLT FST — hiện tại là hơn 30 ngôn ngữ, chủ yếu là các ngôn ngữ Sámi, Uralic và các ngôn ngữ bản địa vùng Bắc Cực.

**Mối liên hệ với nghiên cứu tiền đề:** MorphEval kiểm tra xem một hệ thống có thể xử lý các tương phản cụ thể hay không. Metric FST kiểm tra xem đầu ra của hệ thống có bao gồm các từ thực tế hay không. Hai phương pháp này bổ trợ cho nhau: MorphEval kiểm tra năng lực, metric FST kiểm tra tính hợp lệ.

#### 2. Các lớp tương đương ngôn ngữ (CRK Linter)

Bộ linter giải quyết những gì có thể là lỗi nghiêm trọng nhất của đánh giá dựa trên bản dịch tham chiếu: **phạt các bản dịch chính xác nhưng khác với bản dịch tham chiếu**.

Bộ linter tiếng Plains Cree (844 dòng code) triển khai sáu **lớp biến thể**, mỗi lớp mã hóa một quy tắc tương đương dựa trên ngôn ngữ học:

- **WORD_ORDER**: Tiếng Cree có trật tự từ tự do về mặt thực dụng (Wolfart, 1973 §3.2). *nikî-wâpamâw nâpêw* và *nâpêw nikî-wâpamâw* có cùng ý nghĩa. Bộ linter tạo ra tất cả các hoán vị và kiểm tra xem bản dịch giả thuyết có khớp với bất kỳ hoán vị nào không.
- **ORTHOGRAPHIC**: Phép chính tả chuẩn La-tinh (SRO) có các điểm biến thể đã biết — dấu mũ so với dấu gạch ngang (*â* so với *ā*), việc sử dụng dấu gạch nối của các tiền động từ (*nikî-nipâw* so với *nikî nipâw* so với *nikînipâw*). Bộ linter sẽ chuẩn hóa các điểm này.
- **OPTIONAL_PARTICLE**: Một số tiểu từ hội thoại (*mâka*, *êkwa*, *êwako*) có thể xuất hiện hoặc vắng mặt mà không làm thay đổi mệnh đề cốt lõi. Bộ linter kiểm tra xem bản dịch giả thuyết có khớp với bản dịch tham chiếu sau khi loại bỏ tiểu từ hay không.
- **LEMMA_SYNONYM**: Một số lemma tiếng Cree có thể thay thế cho nhau trong các ngữ cảnh cụ thể. Điều này sử dụng một danh sách từ đồng nghĩa được tuyển chọn (ví dụ: các biến thể phương ngôn) và, khi có FST, kiểm tra xem bản dịch giả thuyết và bản dịch tham chiếu có chia sẻ các phân tích hình thái học hay không.
- **PROGRESSIVE_AMBIGUITY**: Các dạng tiếp diễn trong tiếng Anh ("is walking") có thể được dịch sang tiếng Cree bằng các cấu trúc khác nhau. Bộ linter công nhận các cấu trúc này là tương đương.
- **INCLUSIVE_EXCLUSIVE**: Tiếng Cree phân biệt "chúng ta" bao gồm người nghe (tiền tố *ki-*) và "chúng tôi" loại trừ người nghe (tiền tố *ni-*) — một sự phân biệt mà tiếng Anh gộp chung vào một đại từ duy nhất. Bộ linter công nhận rằng cả hai dạng đều có thể chính xác khi câu nguồn tiếng Anh bị mơ hồ.

Bộ linter đưa ra ba kết quả đánh giá: **EXACT** (giả thuyết khớp chính xác với tham chiếu), **EQUIVALENT** (giả thuyết khác biệt nhưng được phân loại là một biến thể hợp lệ), hoặc **MISS** (không tìm thấy kết quả khớp). Ở cấp độ tổng hợp, nó tính toán một `equivalent_match_rate` — tỷ lệ các bản dịch chính xác hoặc tương đương.

**Mối liên hệ với nghiên cứu tiền đề:** Nghiên cứu song song gần nhất là **HyTER** (Dreyer & Marcu, NAACL-HLT 2012), mã hóa vô số bản dịch hợp lệ dưới dạng các mạng lưới diễn đạt lại và đo lường khoảng cách chỉnh sửa đến dạng hợp lệ gần nhất. Bộ linter của chúng tôi có ý tưởng tương tự — nó định nghĩa một tập hợp các bản dịch hợp lệ cho mỗi bản dịch tham chiếu — nhưng sử dụng các quy tắc biến đổi được định nghĩa theo ngôn ngữ học thay vì các cơ sở dữ liệu diễn đạt lại. HyTER được thiết kế cho tiếng Anh; chưa có ai xây dựng các mạng lưới diễn đạt lại cho tiếng Cree. Các lớp biến thể của chúng tôi, trên thực tế, là một sự xấp xỉ nhỏ gọn, dựa trên quy tắc của những gì HyTER thực hiện với các đồ thị.

Trong khung thử nghiệm CheckList, các lớp biến thể của chúng tôi hoạt động như **các kiểm thử tính bất biến**: các biến đổi không nên làm thay đổi kết quả đánh giá. Sự khác biệt là các kiểm thử CheckList thường được áp dụng cho *mô hình*; còn các quy tắc biến thể của chúng tôi được áp dụng cho *metric*.

#### 3. Xác thực ngữ nghĩa tất định (CRK Semantic Metric)

Bộ xác thực ngữ nghĩa (792 dòng code) cố gắng thực hiện một điều tham vọng hơn: **so sánh ý nghĩa tất định** không cần các nhúng nơ-ron. Nó hoạt động qua bốn giai đoạn:

1. **Phân tích hình thái học**: Cả bản dịch giả thuyết và bản dịch tham chiếu đều được đưa qua bộ phân tích CRK FST, trả về lemma và các đặc trưng hình thái cho mỗi từ.
2. **Tra cứu nghĩa**: Mỗi lemma được tra cứu trong từ điển Cree–Anh (Wolvengrey, 2001) để lấy nghĩa tiếng Anh.
3. **Trích xuất từ thực từ**: Sử dụng quy trình tiếng Anh của spaCy (`en_core_web_md`), các hư từ (function words) được lọc bỏ khỏi cả nghĩa tiếng Anh và văn bản nguồn.
4. **Tính điểm trùng lặp**: Sự trùng lặp thực từ giữa nghĩa của bản dịch giả thuyết và nghĩa của bản dịch tham chiếu sẽ quyết định kết quả ngữ nghĩa.

Bộ xác thực tạo ra các kết quả phân loại: **EXACT_MATCH**, **VALID** (các từ khác nhau nhưng cùng ý nghĩa), **GRAMMAR_ISSUES** (đúng lemma nhưng gặp vấn đề ngữ pháp cấp độ câu — sự hòa hợp, tính động vật, dạng động từ), **PARTIAL** (bảo toàn được một phần ý nghĩa), **INCOMPLETE** (ý nghĩa bị thiếu một phần), **WRONG** (sai ý nghĩa), hoặc **NO_OUTPUT**.

**Mối liên hệ với nghiên cứu tiền đề:** Đây, trên thực tế, là một **sự xấp xỉ tất định cho việc tính toán độ tương đồng ngữ nghĩa của COMET**. Trong khi COMET sử dụng các nhúng đa ngôn ngữ học được để đánh giá xem hai câu có cùng ý nghĩa hay không, bộ xác thực của chúng tôi sử dụng một chuỗi các tra cứu tất định: FST → từ điển → spaCy. Ưu điểm là tính minh bạch (mọi bước đều có thể kiểm tra và mang tính tất định) và sự độc lập khỏi dữ liệu huấn luyện. Nhược điểm là tính mong manh: chất lượng của việc đánh giá phụ thuộc hoàn toàn vào độ bao phủ của FST và tính đầy đủ của từ điển.

Cách tiếp cận này có liên quan về mặt ý tưởng với **MEANT** (Lo & Wu, 2011; Lo, 2017), vốn sử dụng gán nhãn vai trò ngữ nghĩa (semantic role labeling) để đánh giá xem cấu trúc "ai đã làm gì với ai" có được bảo toàn trong bản dịch hay không. Cách tiếp cận của chúng tôi thô hơn (trùng lặp thực từ thay vì các vai trò ngữ nghĩa) nhưng hoạt động trên một ngôn ngữ chưa có bất kỳ công cụ SRL nào tồn tại.

#### 4. Các plugin phát hiện hành vi (Ảo tưởng, Chuyển mã ngôn ngữ, Thuật ngữ)

Ba plugin bổ sung cung cấp **các tín hiệu chất lượng hành vi** bổ trợ cho các metric hình thái học:

- **Phát hiện ảo tưởng** (259 dòng code): Bốn tín hiệu phỏng đoán được trọng số hóa và kết hợp — phình to độ dài (40%), lặp lại (30%), không khớp thực thể (20%), lặp lại nguồn (10%). Đây là các bộ lọc giá rẻ, không cần bản dịch tham chiếu giúp bắt các lỗi tự tạo thô thiển.
- **Phát hiện chuyển mã ngôn ngữ** (~280 dòng code): Phân tích khối Unicode cộng với danh sách từ phổ biến để phát hiện các token ngôn ngữ nguồn chưa được dịch. Đầu ra là một `code_switching_rate` (0.0–1.0).
- **Tuân thủ thuật ngữ** (199 dòng code): Kiểm tra xem các thuật ngữ được chỉ định trong bảng thuật ngữ có được dịch nhất quán hay không. Trả về `terminology_adherence` (0.0–1.0) hoặc None nếu không có bảng thuật ngữ nào được cấu hình.

Các plugin này được định vị một cách trung thực là **các bộ phát hiện phỏng đoán cơ bản**, không phải là trạng thái công nghệ hiện tại. Giá trị của chúng là cung cấp các tín hiệu giá rẻ, nhanh chóng, có thể giải thích được và có thể được tính toán song song với các metric hình thái học phức tạp hơn. Trong khung chấm điểm tổng hợp, chúng mang trọng số thấp (0.05 cho mỗi loại).

### Những hạn chế thực tế

Cách tiếp cận này có những hạn chế đáng kể cần phải được thừa nhận trước khi đưa ra bất kỳ tuyên bố nào về tính mới mẻ hay hữu ích:

1. **Tỷ lệ từ chối sai của FST.** FST sẽ từ chối các từ hợp lệ không có trong từ điển của nó — từ mượn, từ mới, danh từ riêng, các thuật ngữ trộn mã. Điều này làm tăng tỷ lệ lỗi hình thái một cách giả tạo. Tỷ lệ từ chối sai chưa được đo lường một cách chính thức trên một ngữ liệu đại diện của tiếng Cree. Nếu không có phép đo này, độ chính xác của metric tính hợp lệ FST là không xác định.

2. **Độ bao phủ của từ điển.** Chất lượng của bộ xác thực ngữ nghĩa phụ thuộc hoàn toàn vào độ bao phủ của từ điển Wolvengrey. Các từ tiếng Cree không có trong từ điển sẽ không tạo ra nghĩa, điều mà bộ xác thực sẽ coi là một khoảng trống ý nghĩa. Từ điển chứa khoảng 22.000 mục từ — đáng kể, nhưng không phải là toàn diện.

3. **Tính đầy đủ của lớp biến thể.** Sáu lớp biến thể của bộ linter được thiết kế dựa trên tài liệu ngôn ngữ học và quan sát các mẫu đầu ra của dịch máy. Có thể có các lớp tương đương bổ sung chưa được nắm bắt — các biến thể phương ngôn, sự khác biệt văn phong, các từ đồng nghĩa ở cấp độ hội thoại. Không có quy trình chính thức nào đảm bảo tính đầy đủ này.

4. **Chưa có nghiên cứu tương quan với con người.** Khoảng trống nghiêm trọng nhất: chưa có ai đo lường xem liệu các kết quả đánh giá của bộ linter (EXACT/EQUIVALENT/MISS) hay các kết quả của bộ xác thực ngữ nghĩa có tương quan với các đánh giá của con người về chất lượng dịch thuật hay không. Các metric nơ-ron phải mất nhiều năm để thiết lập mối tương quan với đánh giá của con người (các nhiệm vụ chung của WMT). Các metric của chúng tôi chưa có sự xác thực như vậy.

5. **Tính đặc thù của ngôn ngữ.** Các lớp biến thể, danh sách từ đồng nghĩa và các quy tắc tiểu từ tùy chọn là đặc thù cho tiếng Plains Cree. Việc chuyển chúng sang tiếng North Sámi, Inuktitut, hoặc bất kỳ ngôn ngữ nào khác đòi hỏi các nhà ngôn ngữ học hiểu rõ hình thái học, tính linh hoạt của trật tự từ và các biến thể chính tả của ngôn ngữ đó. *Khung làm việc* có thể chuyển đổi; nhưng *các quy tắc* thì không.

6. **Khoảng trống kết nối metric.** Tại thời điểm viết tài liệu này, bốn trong số chín metric trong hồ sơ chấm điểm tổng hợp (semantic_score, morphological_accuracy, equivalent_match_rate, orthographic_accuracy) có kết nối plugin chưa hoàn thiện hoặc chưa rõ ràng trong khung thử nghiệm của đấu trường. Điểm số tổng hợp thực tế được tính toán từ khoảng năm metric với các trọng số được phân bổ lại.

### Những yêu cầu để xác thực phương pháp này

Để làm cho nghiên cứu này có thể xuất bản được — ở bất kỳ địa điểm nào, ở bất kỳ cấp độ nghiêm túc học thuật nào — các thử nghiệm sau đây là bắt buộc:

1. **Nghiên cứu tương quan với đánh giá của con người.** Thu thập các đánh giá chất lượng của con người cho một tập hợp các bản dịch Anh→Cree (lý tưởng là hơn 200 cặp câu được đánh giá bởi hơn 3 người nói song ngữ). Tính toán mối tương quan giữa điểm số của con người và từng metric của chúng tôi. Đây là bước xác thực quan trọng nhất. Nếu không có nó, các metric chỉ là các sản phẩm kỹ thuật chứ không phải là công cụ đánh giá.

2. **Đo lường tỷ lệ từ chối sai của FST.** Chạy bộ phân tích FST trên một ngữ liệu văn bản tiếng Cree chuẩn đã biết (ví dụ: các văn bản tiếng Cree đã xuất bản, các ngữ liệu song song đã được xác thực) và đo lường tỷ lệ phần trăm các từ hợp lệ bị từ chối. Điều này định lượng độ chính xác của metric tính hợp lệ FST.

3. **Xác thực trên ngôn ngữ thứ hai.** Chuyển đổi metric tính hợp lệ FST sang một ngôn ngữ GiellaLT thứ hai (nhiều khả năng là tiếng North Sámi, vốn có bộ phân tích FST trưởng thành nhất trong hệ sinh thái GiellaLT). Chứng minh rằng metric tạo ra các kết quả hợp lý trên đầu ra dịch máy tiếng Sámi. Điều này xác thực tuyên bố về khả năng mở rộng.

4. **So sánh với COMET.** Chạy COMET trên cùng dữ liệu tiếng Cree và so sánh điểm số của nó với các metric của chúng tôi và với đánh giá của con người. Nếu COMET tạo ra các điểm số có ý nghĩa cho tiếng Cree (điều mà chúng tôi nghi ngờ, nhưng chưa thử nghiệm), các metric của chúng tôi cần phải vượt trội hơn nó để chứng minh tính hữu ích. Nếu COMET tạo ra kết quả nhiễu (điều chúng tôi dự đoán), điều này xác thực nhu cầu cho phương pháp của chúng tôi.

5. **Bổ sung chẩn đoán MorphEval.** Xây dựng một bộ kiểm thử nhỏ (50–100 tương phản) theo phong cách MorphEval cho tiếng Plains Cree nhắm vào các đặc trưng hình thái đặc trưng nhất của ngôn ngữ này (sự phân biệt ngôi thứ ba, thể nghịch đảo, thức liên kết/độc lập, đại từ "chúng tôi" bao gồm/loại trừ, chuỗi tiền động từ). Chạy các hệ thống dịch máy trên bộ kiểm thử này và chỉ ra rằng thông tin chẩn đoán thu được là có thể hành động được.

6. **Kiểm toán kết nối và tích hợp.** Khắc phục các khoảng trống kết nối hồ sơ chấm điểm được xác định trong kho mã nguồn. Đảm bảo rằng tất cả chín metric tổng hợp đều tạo ra giá trị và điểm số tổng hợp được tính toán chính xác.

---

## Phần 7: Định vị và Định hướng tương lai

### Vị trí của LYSS trong bức tranh đánh giá dịch máy

Phân loại các phương pháp đánh giá dịch máy một cách trung thực:

| Chiều đánh giá | Metric chuỗi (BLEU, chrF++) | Metric nơ-ron (COMET, MetricX) | LLM làm trọng tài (GEMBA) | Chẩn đoán (MorphEval, CheckList) | **LYSS** |
|-----------|-------------------------------|---|----|-------|--------|
| Loại tín hiệu | Trùng lặp bề mặt | Độ tương đồng ngữ nghĩa học được | Đánh giá mở | Thử nghiệm năng lực mục tiêu | Tính hợp lệ hình thái + tương đương dựa trên quy tắc |
| Dữ liệu huấn luyện cần thiết | Không | Đánh giá của con người (hàng nghìn) | LLM tiền huấn luyện | Bộ kiểm thử do nhà ngôn ngữ học thiết kế | FST + từ điển + quy tắc biến thể |
| Khả năng áp dụng cho LRL | Vạn năng nhưng yếu | Bị giới hạn bởi độ bao phủ của bộ mã hóa | Bị giới hạn bởi độ bao phủ của LLM | Bị giới hạn bởi việc tạo bộ kiểm thử | Bị giới hạn bởi tính sẵn có của FST (~30 ngôn ngữ) |
| Cần bản dịch tham chiếu | Có | Có (hoặc QE chỉ cần nguồn) | Tùy chọn | Có (tương phản) | Có (LYSS-eq/LYSS-sem) / Không (LYSS-fst) |
| Khả năng giải thích | Thấp (một con số) | Thấp (một con số) | Cao (giải thích bằng văn bản) | Cao (đạt/không đạt cho mỗi hiện tượng) | Cao (kết quả đánh giá + các lớp biến thể) |

**LYSS không phải là**: một giải pháp thay thế cho COMET trên các ngôn ngữ giàu tài nguyên, một metric vạn năng, hay phương pháp đánh giá nhận biết hình thái học đầu tiên.

**LYSS là**: một khung làm việc tích hợp kết hợp xác thực hình thái học dựa trên FST với các metric tiêu chuẩn cho trường hợp cụ thể của các ngôn ngữ mà các metric nơ-ron thiếu độ bao phủ và các công cụ dựa trên quy tắc (FST, từ điển) đã tồn tại. Nó có ba thành phần cốt lõi:
- **LYSS-fst** — Tính hợp lệ hình thái qua FST (`fst_acceptance_rate`)
- **LYSS-eq** — Tính tương đương ngôn ngữ qua bộ linter (`equivalent_match_rate`)
- **LYSS-sem** — Xác thực ngữ nghĩa tất định (`semantic_score`)

**LYSS mở rộng**: ý tưởng cốt lõi của MorphEval (sử dụng các công cụ hình thái học để đánh giá) từ kiểm thử năng lực chẩn đoán sang chấm điểm chất lượng liên tục.

**LYSS bổ trợ**: chrF++ (tính điểm một phần cho các hình vị chia sẻ nhưng không thể phát hiện sự tương đương), COMET (hoạt động trong không gian ngữ nghĩa nhưng thiếu dữ liệu huấn luyện cho LRL), và FUSE (sử dụng thiết kế đặc trưng nhưng không dùng bộ phân tích hình thái học).

**Nghiên cứu tiền đề gần nhất là**: Hjerson (phân loại lỗi ngôn ngữ) + HyTER (các lớp tương đương qua mạng lưới diễn đạt lại) + metric độ bao phủ ngây thơ của Apertium (kiểm tra tính hợp lệ dựa trên FST). Đóng góp của LYSS không phải là bất kỳ kỹ thuật đơn lẻ nào mà là sự tích hợp các ý tưởng này — đặc biệt là tính hợp lệ dựa trên FST và tính tương đương dựa trên quy tắc — vào một khung thử nghiệm đánh giá hoạt động cho một ngôn ngữ đa tổng hợp.

### Tích hợp MorphEval

Phương pháp bộ kiểm thử tương phản của MorphEval và cách tiếp cận chấm điểm liên tục của chúng tôi bổ trợ cho nhau:

- **MorphEval** trả lời: "Hệ thống này có thể xử lý việc đánh dấu thì không? Sự hòa hợp về số? Sự gán cách?"
- **Metric FST của chúng tôi** trả lời: "Hệ thống này có tạo ra các từ thực tế không?"
- **Bộ linter của chúng tôi** trả lời: "Bản dịch này có tương đương với bản dịch tham chiếu bất chấp các khác biệt bề mặt không?"
- **Bộ xác thực ngữ nghĩa của chúng tôi** trả lời: "Bản dịch này có mang lại ý nghĩa chính xác không?"

MorphEval là mã nguồn mở. Việc tạo ra một bộ kiểm thử tiếng Plains Cree sẽ đòi hỏi một nhà ngôn ngữ học thiết kế các cặp tương phản bao gồm các tương phản hình thái đặc thù của tiếng Cree (sự phân biệt ngôi thứ ba, đánh dấu thể nghịch đảo, thức liên kết/độc lập, đại từ "chúng tôi" bao gồm/loại trừ, chuỗi tiền động từ). Đây là một công việc đáng kể nhưng có giới hạn — tính bằng tuần, chứ không phải bằng tháng — và sẽ cung cấp năng lực chẩn đoán mà không một công cụ đánh giá nào khác có thể mang lại cho tiếng Cree.

### Câu hỏi về khả năng mở rộng

Những ngôn ngữ nào khác có thể áp dụng phương pháp này? Hạn chế chính là tính sẵn có của FST. Cơ sở hạ tầng GiellaLT cung cấp các bộ phân tích hình thái học cho hơn 30 ngôn ngữ, chủ yếu thuộc ba ngữ hệ:

- **Các ngôn ngữ Sámi** (North Sámi, Lule Sámi, South Sámi, Skolt Sámi, Inari Sámi): Các FST trưởng thành với độ bao phủ rộng. North Sámi là mục tiêu có thể chuyển đổi ngay lập tức nhất.
- **Các ngôn ngữ Uralic** (Phần Lan, Estonia, Komi, Erzya, Moksha): Các bộ phân tích được phát triển tốt, mặc dù tiếng Phần Lan và tiếng Estonia có thể không cần đánh giá dựa trên FST một cách khẩn cấp (chúng có nhiều độ bao phủ của metric nơ-ron hơn).
- **Các ngôn ngữ bản địa vùng Bắc Cực** (Inuktitut qua Uqailaut, Greenlandic): Các bộ phân tích đã tồn tại nhưng độ bao phủ khác nhau.
- **Các ngôn ngữ GiellaLT khác**: Faroe, Ireland, Cornish, Livonian, và các ngôn ngữ khác với các mức độ trưởng thành FST khác nhau.

Ngoài GiellaLT, nền tảng **Apertium** cung cấp các bộ phân tích hình thái học cho khoảng hơn 40 cặp ngôn ngữ. Hệ sinh thái **HFST** (Helsinki Finite-State Technology) là cơ sở hạ tầng chung mà cả GiellaLT và Apertium sử dụng, nghĩa là bất kỳ bộ phân tích Apertium nào về nguyên tắc đều có thể được kết nối vào cùng một metric tính hợp lệ FST.

Hạn chế thực tế không phải là tính sẵn có của FST mà là **việc tuyển chọn lớp biến thể**. Các quy tắc tương đương của bộ linter đòi hỏi chuyên môn ngôn ngữ học cho từng ngôn ngữ đích. Đối với tiếng North Sámi, điều này đòi hỏi sự hiểu biết về tính linh hoạt của trật tự từ tiếng Sámi, các quy ước chính tả và biến thể phương ngôn. Đối với tiếng Inuktitut, nó đòi hỏi sự hiểu biết về hình thái học đa tổng hợp ở mức độ tương đương với những gì đã được thực hiện cho tiếng Cree. Tuy nhiên, metric tính hợp lệ FST có thể được triển khai ngay lập tức cho bất kỳ ngôn ngữ nào có bộ phân tích GiellaLT — không đòi hỏi thêm công việc ngôn ngữ học nào khác.

### Hướng tới một bài báo khoa học

Một ấn phẩm dựa trên nghiên cứu này sẽ hướng tới một trong các địa điểm sau một cách tự nhiên nhất:

- **WMT Metrics Shared Task** (đồng tổ chức với EMNLP): Địa điểm trực tiếp nhất. Sẽ đòi hỏi việc triển khai các metric dưới dạng một bài nộp nhiệm vụ chung và đánh giá trên các tập kiểm thử WMT — vốn hiện tại không bao gồm bất kỳ ngôn ngữ đa tổng hợp nào. Có thể nộp dưới dạng một bài báo "phát hiện" (findings) hoặc tham gia vào nhiệm vụ phụ bộ thử thách (challenge sets).
- **LREC-COLING** (Language Resources and Evaluation Conference): Phù hợp tự nhiên cho một bài báo về tài nguyên/công cụ mô tả khung đánh giá và các tài nguyên ngôn ngữ học mà nó sử dụng (FST, từ điển, quy tắc biến thể).
- **ACL hoặc NAACL** (hội nghị chính): Sẽ đòi hỏi nghiên cứu tương quan với con người và ít nhất một ngôn ngữ bổ sung để đạt tiêu chuẩn cho một bài báo hội nghị chính.
- **Hội thảo AmericasNLP**: Khán giả dễ tiếp nhận nhất cho việc đánh giá dịch máy ngôn ngữ bản địa. Tiêu chuẩn xuất bản thấp hơn, nhưng tác động cao trong cộng đồng mục tiêu.
- **ComputEL** (Computational Approaches to Endangered Languages): Địa điểm chuyên biệt cho chính xác loại nghiên cứu này.

Bất kỳ ấn phẩm nào cũng sẽ đòi hỏi các đồng tác giả có chuyên môn về ngôn ngữ học tiếng Cree (để xác thực các lớp biến thể và giải thích kết quả) và lý tưởng nhất là những người nói tiếng Cree song ngữ (để cung cấp các đánh giá chất lượng của con người cho nghiên cứu tương quan). Đây không phải là một lựa chọn tùy ý — một bài báo về đánh giá dịch máy tiếng Cree được viết hoàn toàn bởi những người không nói tiếng Cree, tốt nhất, sẽ là chưa hoàn thiện, và tệ nhất, là sự tiếp diễn của các động lực nghiên cứu mang tính khai thác mà ngành này đang cố gắng vượt qua.

---

## Phụ lục A: Ma trận yêu cầu của các metric

| Metric | Cần bản dịch tham chiếu? | Cần câu nguồn? | Có mô hình huấn luyện? | Tài nguyên đặc thù ngôn ngữ? | Hoạt động cho LRL? |
|--------|-------------------|---------------|----------------|------------------------------|----------------|
| BLEU | Có | Không | Không | Không | Kém |
| chrF++ | Có | Không | Không | Không | Tốt hơn BLEU |
| METEOR | Có | Không | Không | Bộ tách gốc từ + WordNet | Chỉ khi tài nguyên tồn tại |
| TER | Có | Không | Không | Không | Tương tự BLEU |
| BERTScore | Có | Không | Có (mBERT) | Không | Phụ thuộc độ bao phủ của mô hình |
| BLEURT | Có | Không | Có (được huấn luyện) | Không | Phụ thuộc dữ liệu huấn luyện |
| COMET | Có | Có | Có (XLM-R) | Không | Phụ thuộc độ bao phủ của XLM-R |
| CometKiwi | Không | Có | Có (XLM-R) | Không | Phụ thuộc độ bao phủ của XLM-R |
| GEMBA | Tùy chọn | Có | Có (LLM) | Không | Phụ thuộc độ bao phủ của LLM |
| **FST chấp nhận** | **Không** | **Không** | **Không** | **Có (bộ phân tích FST)** | **Có, nếu FST tồn tại** |
| **CRK Linter** | **Có** | **Không** | **Không** | **Có (FST + quy tắc biến thể)** | **Có, nếu tài nguyên tồn tại** |
| **CRK Semantic** | **Có** | **Tùy chọn** | **Không** | **Có (FST + từ điển + spaCy)** | **Có, nếu tài nguyên tồn tại** |
| Phát hiện ảo tưởng | Không | Có | Không | Không | Có |
| Phát hiện chuyển mã | Tùy chọn | Có | Không | Tối thiểu | Có |
| MorphEval | Có (tương phản) | Có | Không | Có (bộ kiểm thử + bộ phân tích) | Chỉ khi bộ kiểm thử tồn tại |

## Phụ lục B: Các bài báo khoa học chính

| Trích dẫn | Địa điểm | Mức độ liên quan |
|----------|-------|-----------|
| Papineni et al. (2002). BLEU: a Method for Automatic Evaluation of Machine Translation | ACL 2002 | Metric định hình cả ngành |
| Doddington (2002). Automatic Evaluation of Machine Translation Quality Using N-gram Co-Occurrence Statistics | HLT 2002 | Khớp n-gram được trọng số hóa theo thông tin |
| Banerjee & Lavie (2005). METEOR: An Automatic Metric for MT Evaluation | ACL 2005 Workshop | Tách gốc từ, từ đồng nghĩa, căn chỉnh từ |
| Snover et al. (2006). A Study of Translation Edit Rate | AMTA 2006 | Khoảng cách chỉnh sửa với dịch chuyển cụm từ |
| Popović & Ney (2011). Morphemes and POS tags for n-gram based evaluation metrics | WMT 2011 | Phân loại lỗi Hjerson |
| Dreyer & Marcu (2012). HyTER: Meaning-Equivalent Semantics for Translation Evaluation | NAACL-HLT 2012 | Các lớp tương đương qua mạng lưới diễn đạt lại |
| Lommel et al. (2014). Multidimensional Quality Metrics | — | Phân loại lỗi MQM |
| Popović (2015). chrF: character n-gram F-score for automatic MT evaluation | WMT 2015 | Đánh giá cấp độ ký tự |
| Popović (2017). chrF++: words helping character n-grams | WMT 2017 | Đánh giá n-gram ký tự + từ |
| Burlot & Yvon (2017). Evaluating the Morphological Competence of Machine Translation Systems | WMT 2017 | Các bộ kiểm thử hình thái học tương phản |
| Sennrich (2017). How Grammatical is Character-level Neural Machine Translation? | EACL 2017 | Các cặp tương phản LingEval97 |
| Isabelle, Cherry & Foster (2017). A Challenge Set Approach to Evaluating Machine Translation | EMNLP 2017 | Kiểm thử sự khác biệt cấu trúc mục tiêu |
| Post (2018). A Call for Clarity in Reporting BLEU Scores | WMT 2018 | Chuẩn hóa sacreBLEU |
| Reiter (2018). A Structured Review of the Validity of BLEU | Computational Linguistics | Phân tích gộp về mối tương quan của BLEU với con người |
| Stanovsky, Smith & Zettlemoyer (2019). Evaluating Gender Bias in Machine Translation | ACL 2019 | Đánh giá giới tính WinoMT |
| Ribeiro et al. (2020). Beyond Accuracy: Behavioral Testing of NLP Models with CheckList | ACL 2020 (Best Paper) | Kiểm thử đơn vị dựa trên năng lực cho NLP |
| Zhang et al. (2020). BERTScore: Evaluating Text Generation with BERT | ICLR 2020 | Độ tương đồng ngữ nghĩa dựa trên nhúng |
| Sellam et al. (2020). BLEURT: Learning Robust Metrics for Text Generation | ACL 2020 | Metric tiền huấn luyện + tinh chỉnh |
| Rei et al. (2020). COMET: A Neural Framework for MT Evaluation | EMNLP 2020 | Đánh giá ba đầu vào đa ngôn ngữ |
| Freitag et al. (2021). Results of the WMT 2021 Metrics Shared Task | WMT 2021 | Siêu đánh giá dựa trên MQM |
| Thompson & Post (2020). PRISM: Automatic MT Evaluation via Zero-Shot Paraphrasing | EMNLP 2020 | NMT đa ngôn ngữ như bộ chấm điểm diễn đạt lại |
| Currey et al. (2022). MT-GenEval | EMNLP 2022 | Độ chính xác giới tính phản thực tế |
| Amrhein et al. (2022). ACES: Translation Accuracy Challenge Sets | WMT 2022 | 68 hiện tượng, 146 cặp ngôn ngữ |
| Kocmi & Federmann (2023). GEMBA: Large Language Models Are State-of-the-Art Evaluators | EAMT 2023 | LLM đóng vai trò người đánh giá |
| Guerreiro et al. (2024). xCOMET: Transparent MT Evaluation through Fine-grained Error Detection | TACL 2024 | Phát hiện phân đoạn lỗi |
| Wang & Adelani (2024). AfriMTE and AfriCOMET | NAACL 2024 | Metric nơ-ron cho các ngôn ngữ châu Phi |
| Juraska et al. (2024). MetricX-24 | WMT 2024 | Metric chiến thắng dựa trên mT5 |

## Phụ lục C: Thuật ngữ đánh giá dịch máy

| Thuật ngữ | Định nghĩa |
|------|------------|
| **Độ đầy đủ (Adequacy)** | Liệu một bản dịch có truyền tải được ý nghĩa của câu nguồn hay không. |
| **Độ trôi chảy (Fluency)** | Liệu một bản dịch có đúng ngữ pháp và tự nhiên trong ngôn ngữ đích hay không. |
| **Đánh giá Trực tiếp (DA)** | Phương pháp đánh giá của con người nơi người chấm điểm xếp hạng các bản dịch trên thang điểm 0–100. |
| **MQM** | Multidimensional Quality Metrics — phương pháp đánh giá của con người dựa trên phân đoạn lỗi với các mức độ nghiêm trọng được phân loại. |
| **Ước lượng chất lượng (QE)** | Việc dự đoán chất lượng dịch thuật mà không cần bản dịch tham chiếu. |
| **FST** | Finite-State Transducer (Bộ chuyển đổi trạng thái hữu hạn) — một thiết bị tính toán mã hóa các quy tắc hình thái của một ngôn ngữ. |
| **GiellaLT** | Cơ sở hạ tầng cho công nghệ ngôn ngữ dựa trên quy tắc, chủ yếu dành cho các ngôn ngữ Sámi và các ngôn ngữ vùng Bắc Cực khác. |
| **HFST** | Helsinki Finite-State Technology — khung phần mềm nền tảng cho GiellaLT và Apertium. |
| **SRO** | Standard Roman Orthography (Phép chính tả chuẩn La-tinh) — hệ thống chữ viết dựa trên ký tự Latin cho tiếng Plains Cree. |
| **Chữ âm tiết (Syllabics)** | Chữ âm tiết của người bản địa Canada — một hệ thống chữ viết abugida được sử dụng cho tiếng Cree và các ngôn ngữ Algonquian khác. |
| **Đa tổng hợp (Polysynthetic)** | Một loại hình ngôn ngữ nơi một từ đơn lẻ có thể mã hóa nội dung tương đương với cả một câu tiếng Anh thông qua việc ghép nhiều phụ tố. |
| **Sự phân biệt ngôi thứ ba (Obviation)** | Một phạm trù ngữ pháp trong các ngôn ngữ Algonquian giúp phân biệt giữa hai đối tượng ngôi thứ ba khác nhau. |
| **Thể nghịch đảo (Inverse)** | Một phạm trù giống như thể (voice) trong các ngôn ngữ Algonquian đánh dấu rằng đối tượng chịu tác động có thứ hạng cao hơn tác nhân trên hệ phân cấp tính động vật. |
| **WMT** | Conference on Machine Translation (Hội nghị về Dịch máy) — địa điểm chính cho các nhiệm vụ chung và đánh giá dịch máy. |
| **Đánh giá tương phản** | Việc kiểm thử xem một hệ thống có thể phân biệt các đầu vào khác biệt tối thiểu nhưng đòi hỏi các đầu ra khác nhau hay không. |
| **Bộ thử thách (Challenge set)** | Một bộ kiểm thử được thiết kế thủ công nhắm vào các hiện tượng ngôn ngữ cụ thể. |
| **Lớp tương đương** | Một tập hợp các dạng bề mặt khác nhau nhưng biểu diễn cùng một ý nghĩa và nên nhận được cùng một điểm số đánh giá. |