---
sidebar_position: 5
title: "Hỗ trợ ngôn ngữ ít tài nguyên"
related:
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "The first step for an uncovered language"
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
  - label: "Plains Cree, the trading card"
    to: https://champollion.dev/trading-cards?q=crk
    kind: card
    note: "The proof-of-concept language, as a card"
---
# Hỗ trợ một Ngôn ngữ Ít tài nguyên

> **Tóm tắt tổng quan.** Hướng dẫn toàn diện về việc xây dựng hệ thống dịch máy cho các ngôn ngữ ít tài nguyên và đa tổng hợp (polysynthetic). Nội dung bao gồm lý do tại sao các ngôn ngữ này lại khó xử lý (độ phức tạp về hình thái, dữ liệu thưa thớt, hiện tượng ảo giác), các tài nguyên tính toán hiện có (ALTLab FST, GiellaLT, Apertium, UniMorph, EdTeKLA), hơn 10 chiến lược tiếp cận, hệ thống huấn luyện (coaching system) của champollion, và vòng lặp đánh giá. Hãy bắt đầu từ đây nếu bạn muốn đóng góp một phương pháp cho một ngôn ngữ chưa được hỗ trợ đầy đủ.

:::info Trạng thái: Đang trong quá trình phát triển tích cực
Hỗ trợ cho tiếng Plains Cree (nêhiyawêwin) hiện đang được phát triển. Các công cụ, khung đánh giá (evaluation harness) và bảng xếp hạng (leaderboard) được mô tả ở đây là có thật và có thể sử dụng ngay hôm nay, nhưng quy trình dịch (pipeline) tiếng Cree vẫn chưa được phát hành. Khi được ra mắt, đây sẽ là bản thiết kế mẫu cho các ngôn ngữ đa tổng hợp và ít tài nguyên khác có cơ sở hạ tầng FST.
:::

## Bài toán chưa có lời giải

Google Translate hỗ trợ khoảng 130 ngôn ngữ. Dự án OMT-1600 của Meta (tháng 3 năm 2026) tuyên bố bao phủ 1.600 ngôn ngữ — hệ thống dịch máy (MT) lớn nhất từng được công bố. Nhưng đối với khoảng 1.300 ngôn ngữ ở các tầng tài nguyên thấp nhất, chất lượng dịch thuật vẫn dưới ngưỡng có thể sử dụng, dữ liệu huấn luyện chủ yếu là văn bản Kinh Thánh, trọng số mô hình (model weights) không có sẵn để tải xuống, và không có đánh giá độc lập hay khung quản trị cộng đồng nào. Đối với khoảng 5.400 ngôn ngữ còn lại, không có mô hình tiền huấn luyện (pretrained model) nào tạo ra bất kỳ kết quả đầu ra nào.

Bối cảnh đã thay đổi đáng kể — các tập đoàn công nghệ lớn (Big Tech) hiện đang đầu tư vào việc bao phủ các ngôn ngữ ít tài nguyên (LRL). Nhưng độ bao phủ không đồng nghĩa với chất lượng, và chất lượng mà không có sự xác minh độc lập thì không thể tạo dựng niềm tin. Các ngôn ngữ ít tài nguyên cần nhiều hơn là một mô hình tuyên bố hỗ trợ chúng — chúng cần sự đánh giá độc lập với xác thực hình thái học, các kho ngữ liệu do cộng đồng tuyển chọn, và một cơ chế quản trị tôn trọng chủ quyền dữ liệu.

**champollion được xây dựng để thay đổi điều đó.**

[Bảng xếp hạng Phương pháp](https://champollion.dev/leaderboard) là một thử thách mở: hãy xây dựng phương pháp dịch tốt nhất cho một ngôn ngữ chưa được hỗ trợ đầy đủ, chứng minh điều đó bằng đánh giá có thể tái lập, và giành vị trí dẫn đầu. Bất kỳ ai trên thế giới cũng có thể đóng góp — các nhà ngôn ngữ học, nhà nghiên cứu ML, những người làm việc về ngôn ngữ trong cộng đồng, sinh viên, hay những người đam mê. Bài toán vẫn chưa có lời giải. Cơ sở hạ tầng đã sẵn sàng. Bảng xếp hạng đang chờ đợi bạn.

---

## Tại sao việc này lại khó: Hình thái học Đa tổng hợp

Hầu hết các hệ thống dịch máy thương mại được thiết kế cho các ngôn ngữ như tiếng Anh, tiếng Pháp và tiếng Trung — những ngôn ngữ có từ tương đối ngắn và câu được xây dựng từ các token rời rạc. Nhưng nhiều ngôn ngữ bản địa, bao gồm cả tiếng Plains Cree, là ngôn ngữ **đa tổng hợp** (polysynthetic): một từ duy nhất có thể mã hóa những gì tiếng Anh phải diễn đạt bằng cả một câu.

### Ví dụ về tiếng Cree

Hãy xem xét từ tiếng Plains Cree sau:

> **ê-kî-nitawi-kîskinwahamâkosiyân**
> *"khi tôi đi học"*

Đó là **một từ duy nhất**. Nó mã hóa thì (quá khứ), hướng (đi đến), gốc từ (học), thể (bị động/phản thân), và ngôi (ngôi thứ nhất số ít). Một LLM được huấn luyện chủ yếu bằng tiếng Anh không có trực giác về mật độ hình thái học như thế này.

Các thách thức chồng chất lên nhau:

| Thách thức | Ý nghĩa |
|-----------|--------------|
| **Độ phức tạp về hình thái** | Một gốc động từ duy nhất có thể tạo ra hàng ngàn dạng biến hình hợp lệ thông qua việc thêm tiền tố, hậu tố và liên tố (circumfixation) |
| **Phân biệt Động vật/Bất động vật** | Danh từ được phân loại theo ngữ pháp là động vật (animate) hoặc bất động vật (inanimate) — điều này ảnh hưởng đến cách chia động từ, từ chỉ định và dạng số nhiều. Việc phân loại không phải lúc nào cũng tuân theo tính chất sinh học (*askiy* "trái đất" là động vật; *maskisin* "chiếc giày" cũng là động vật) |
| **Sự phân biệt ngôi thứ ba (Obviation)** | Các tham chiếu ngôi thứ ba được xếp hạng theo mức độ gần gũi/nổi bật. Sự phân biệt giữa "ngôi thứ ba gần" (proximate) và "ngôi thứ ba xa" (obviative) không có từ tương đương trong tiếng Anh |
| **Dữ liệu huấn luyện thưa thớt** | Các LLM đã tiếp xúc với rất ít văn bản tiếng Plains Cree. Những gì chúng đã thấy có thể bị trộn lẫn giữa các phương ngữ (phương ngữ Y, phương ngữ TH) hoặc các hệ chữ viết (SRO so với chữ âm tiết - syllabics) |
| **Mốc so sánh thương mại yếu** | OMT-1600 bao gồm CRK ở tầng R1 (Tài nguyên cực kỳ thấp) với dữ liệu huấn luyện thuộc lĩnh vực Kinh Thánh và phân tách token BPE tiêu chuẩn. Google Translate không hỗ trợ tiếng Cree. Đánh giá độc lập với các chỉ số hình thái học là điều làm cho các mốc so sánh này trở nên có ý nghĩa. |

Dịch thuật các ngôn ngữ đa tổng hợp vẫn là một **bài toán nghiên cứu mở** — OMT-1600 bao gồm các ngôn ngữ đa tổng hợp nhưng sử dụng phân tách token BPE tiêu chuẩn (từ vựng 256K) mà không có sự nhận biết về hình thái học, nghĩa là nó xé nhỏ các từ ghép thành các mảnh byte vô nghĩa.

---

## Các nghiên cứu trước đây: Cách mọi người tiếp cận vấn đề này

### ALTLab FST

Tài nguyên tính toán quan trọng nhất cho tiếng Plains Cree là **bộ chuyển đổi trạng thái hữu hạn (finite-state transducer - FST)** được phát triển bởi [Alberta Language Technology Lab (ALTLab)](https://altlab.artsrn.ualberta.ca/) tại Đại học Alberta, hợp tác với [Giellatekno](https://giellatekno.uit.no/) tại UiT Đại học Bắc Cực Na Uy.

ALTLab FST là một **bộ phân tích và tạo hình thái học**: cho một từ tiếng Cree đã biến hình, nó có thể phân tích từ đó thành gốc từ và các thẻ ngữ pháp của nó, và cho một gốc từ cộng với các thẻ, nó có thể tạo ra dạng biến hình chính xác. Quá trình này mang tính tất định (deterministic) — không có mạng thần kinh, không có hiện tượng ảo giác, không có xác suất. Nếu FST chấp nhận một từ, từ đó hợp lệ về mặt hình thái học.

Đây là lý do tại sao bảng xếp hạng champollion theo dõi **Tỷ lệ chấp nhận FST (FST Acceptance Rate)** như một chỉ số đánh giá. Một phương pháp dịch tạo ra các từ bị FST từ chối nghĩa là đang tạo ra tiếng Cree không hợp lệ về mặt hình thái — bất kể điểm số chrF++ có là bao nhiêu.

**Các tài nguyên chính của ALTLab:**
- [itwêwina](https://itwewina.altlab.app/) — từ điển thông minh Plains Cree–Anh được hỗ trợ bởi FST
- [Morphodict](https://github.com/UAlbertaALTLab/morphodict) — nền tảng từ điển mã nguồn mở nhận biết hình thái học
- [crk-db](https://github.com/UAlbertaALTLab/crk-db) — cơ sở dữ liệu từ vựng tiếng Plains Cree
- [21st Century Tools for Indigenous Languages](https://21c.tools/) — bối cảnh dự án rộng hơn

### FST Toàn cầu & Các Đăng ký Hình thái học

Plains Cree không phải là ngôn ngữ duy nhất có cơ sở hạ tầng FST chất lượng cao. Nếu bạn muốn phát triển các quy trình dịch thuật cho các ngôn ngữ ít tài nguyên hoặc có cấu trúc hình thái phức tạp khác, bạn có thể khai thác các trung tâm toàn cầu đã được thiết lập sau:

* **[GiellaLT / Giellatekno](https://giellalt.github.io/) (UiT Đại học Bắc Cực Na Uy):** Kho lưu trữ lớn nhất gồm các bộ phân tích và tạo hình thái học FST mã nguồn mở, bao phủ hơn 100 ngôn ngữ. Các lĩnh vực tập trung bao gồm các ngôn ngữ Sámi (`sme`, `smj`, `sma`, v.v.), các ngôn ngữ Ural (Komi, Erzya, Udmurt, v.v.) và các ngôn ngữ thiểu số/bản địa khác. Họ lưu trữ các kho ngữ liệu văn bản đã xử lý công khai (`corpus-xxx`) trong [Tổ chức GitHub](https://github.com/giellalt/) của mình.
* **[The Apertium Project](https://www.apertium.org/):** Một nền tảng dịch máy dựa trên luật mã nguồn mở. Apertium duy trì các bộ phân tích hình thái học FST được tối ưu hóa cao (sử dụng `lttoolbox` và `hfst`) và từ điển song ngữ cho hàng chục ngôn ngữ, bao gồm một bộ lớn các ngôn ngữ Turk (Kazakh, Tatar, Kyrgyz, v.v.) và các ngôn ngữ châu Âu thiểu số. Tất cả tài nguyên đều được công khai trên [GitHub của Apertium](https://github.com/apertium).
* **[UniMorph (Universal Morphology)](https://unimorph.github.io/):** Một dự án hợp tác cung cấp các mô hình hình thái học chuẩn hóa cho hơn 150 ngôn ngữ. Tập dữ liệu được lưu trữ trên Hugging Face tại [unimorph/universal_morphologies](https://huggingface.co/datasets/unimorph/universal_morphologies). Nếu không có sẵn tệp nhị phân FST đã biên dịch cho một ngôn ngữ, các bảng UniMorph có thể được sử dụng làm cổng tra cứu cơ sở dữ liệu tĩnh.
* **[National Research Council Canada (NRC)](https://nrc-digital-repository.canada.ca/):** Cung cấp các công cụ cho các ngôn ngữ bản địa Canada, bao gồm bộ phân tích hình thái học FST tiếng Inuktitut **Uqailaut** và **Kho ngữ liệu song song Nunavut Hansard** khổng lồ (1,3 triệu cặp câu tiếng Anh-Inuktitut được căn chỉnh).

### Kho ngữ liệu EdTeKLA

[Nhóm nghiên cứu EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) (cũng tại UAlberta) đã thu thập một kho ngữ liệu tiếng Plains Cree từ các tài liệu giáo dục, bản ghi âm và các nguồn cộng đồng. Tập dữ liệu đánh giá champollion [EDTeKLA Dev v1](/docs/leaderboard/datasets) được kế thừa từ công trình này, được cấp phép theo [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

### Các phương pháp tiếp cận khác mà mọi người đã thử hoặc có thể thử

Bảng xếp hạng không phụ thuộc vào phương pháp cụ thể nào. Dưới đây là các chiến lược đã được khám phá hoặc đề xuất cho dịch máy ít tài nguyên, bất kỳ chiến lược nào trong số đó đều có thể được gửi lên:

| Phương pháp tiếp cận | Cách hoạt động | Ưu điểm | Nhược điểm |
|----------|-------------|------|------|
| **[Coached LLM prompting](/docs/tutorials/coached-llm-prompting)** | Đưa các quy tắc ngữ pháp, từ điển và các cặp ví dụ vào system prompt | Lặp nhanh, không cần huấn luyện | Trần chất lượng bị giới hạn bởi kiến thức nền tảng của LLM |
| **[Few-shot prompting](/docs/tutorials/few-shot-prompting)** | Đưa các bản dịch đã được xác minh vào làm ví dụ trong ngữ cảnh (in-context) | Tốt cho việc duy trì phong cách nhất quán | Cửa sổ ngữ cảnh nhỏ; các ví dụ KHÔNG được lấy từ dữ liệu đánh giá |
| **[FST-gated pipeline](/docs/tutorials/fst-gated-pipeline)** | LLM tạo kết quả → FST xác thực → từ chối và thử lại nếu hình thái không hợp lệ | Đảm bảo tính hợp lệ về mặt hình thái | Yêu cầu cơ sở hạ tầng FST; các vòng lặp thử lại làm tăng độ trễ và chi phí |
| **[Dictionary lookup + LLM](/docs/tutorials/dictionary-augmented-llm)** | Bắt buộc sử dụng các thuật ngữ đã biết từ từ điển song ngữ, để LLM xử lý phần còn lại | Giảm hiện tượng ảo giác đối với các thuật ngữ đã biết | Độ bao phủ của từ điển luôn không đầy đủ |
| **[Fine-tuned model](/docs/tutorials/fine-tuned-model)** | Tinh chỉnh (fine-tune) một mô hình mở (Llama, Mistral) trên văn bản song song — ngoại trừ dữ liệu đánh giá | Có tiềm năng đạt chất lượng cao nhất | Yêu cầu kho ngữ liệu song song (khan hiếm); tốn kém; nguy cơ quá khớp (overfitting) |
| **[Chained models](/docs/tutorials/chained-models)** | Mô hình A tạo bản dịch thô → Mô hình B biên tập lại → Mô hình C chấm điểm | Có thể kết hợp thế mạnh của các mô hình chuyên biệt | Phức tạp; chậm; tốn kém |
| **[Rule-based + LLM hybrid](/docs/tutorials/rule-based-hybrid)** | Sử dụng các quy tắc ngôn ngữ cho các mẫu đã biết, LLM cho mọi thứ khác | Chính xác ở những nơi áp dụng quy tắc | Yêu cầu chuyên môn ngôn ngữ sâu sắc |
| **[Back-translation augmentation](/docs/tutorials/back-translation)** | Tạo dữ liệu song song tổng hợp bằng cách dịch Cree→Anh, sau đó huấn luyện theo chiều ngược lại | Mở rộng dữ liệu huấn luyện với chi phí thấp | Làm trầm trọng thêm các lỗi hiện có của mô hình |
| **[Evolutionary approach](/docs/tutorials/evolutionary-approach)** | Tạo các bản dịch ứng viên, chấm điểm chúng, đột biến những bản dịch tốt nhất, lặp lại | Có thể khám phá ra các giải pháp mới lạ; có thể song song hóa | Tốn kém tài nguyên tính toán; cần một hàm thích nghi (fitness function) tốt |
| **[Partial translation](/docs/tutorials/partial-translation)** | Dịch thủ công một mẫu đại diện, chứng minh phương pháp của bạn khớp với phong cách dịch đó, sau đó dịch tự động phần còn lại | Kết hợp chất lượng của con người với quy mô của máy móc | Yêu cầu nỗ lực ban đầu của con người |
| **Chấm điểm JSON / bài thi thủ công** | Tự tay soạn một tệp JSON tập dữ liệu để kiểm tra câu trả lời của học sinh trong một kỳ thi ngôn ngữ, hoặc chấm điểm một loạt bản dịch của con người so với bản dịch chuẩn (gold standard) | Không yêu cầu ML; hoạt động tốt cho giáo dục và QA | Không thể mở rộng quy mô cho nhu cầu dịch thuật liên tục |

### Chỉ đơn giản là JSON

Khung đánh giá nhận đầu vào là JSON và trả về điểm số dưới dạng JSON. [Định dạng tập dữ liệu](/docs/leaderboard/datasets) rất đơn giản:

```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

Bạn có thể tự tay xây dựng tệp này. Bạn có thể xuất nó từ một bảng tính. Bạn có thể tạo nó từ một kho ngữ liệu. Một giáo viên ngôn ngữ có thể sử dụng nó để chấm điểm bài dịch của học sinh. Một công ty dịch thuật có thể sử dụng nó để đánh giá năng lực của các cộng tác viên tự do. Một phòng nghiên cứu có thể sử dụng nó để so sánh các kiến trúc mô hình. Khung đánh giá không quan tâm tệp JSON đến từ đâu — nó chỉ chấm điểm.

Và bởi vì khung triển khai thực tế (production deployment framework) sử dụng cùng một giao diện plugin, một phương pháp đạt điểm cao trong khung đánh giá có thể được triển khai lên trang web của bạn chỉ với một thay đổi cấu hình. **Hãy chứng minh và đưa vào sử dụng.**

Các khả năng thực sự là vô tận. **Nếu bạn có một ý tưởng, hãy xây dựng nó, chạy khung đánh giá và gửi điểm số của bạn.**

---

## Vai trò của champollion

champollion cung cấp lớp cơ sở hạ tầng — bạn mang đến phương pháp.

### Hệ thống huấn luyện (coaching system)

Phương pháp `llm-coached` của champollion cho phép bạn đưa kiến thức ngôn ngữ trực tiếp vào prompt của LLM:

```json title=".champollion/coaching/crk.json"
{
  "grammar_rules": [
    "Plains Cree is polysynthetic — a single word can express what English needs a full sentence for",
    "Animate/inanimate noun distinction affects verb conjugation, demonstratives, and pluralization",
    "Use SRO (Standard Roman Orthography) as the working script — syllabic conversion is handled by the deterministic converter",
    "Obviation: when two third-person referents appear, the less salient one takes obviative marking (-a suffix on nouns, -iyiwa on verbs)"
  ],
  "dictionary": {
    "home": "kīwēwin",
    "settings": "isi-nākatohkēwin",
    "search": "nānātawāpahtam",
    "welcome": "tānisi",
    "dashboard": "kīskinwahamākēwin-māsinahikan"
  },
  "style_notes": "Use formal register appropriate for educational and community contexts. Preserve English technical terms in parentheses when no Cree equivalent exists or is widely accepted."
}
```

Dữ liệu huấn luyện được đưa vào mọi prompt của LLM cho cặp ngôn ngữ `en:crk`, cung cấp cho mô hình ngữ cảnh ngôn ngữ có cấu trúc mà bình thường nó không có. Xem [Dữ liệu Huấn luyện (Coaching Data)](https://champollion.dev/docs/concepts/coaching-data) để biết đặc tả đầy đủ.

### Các phong cách ngôn ngữ (Registers)

Register là một phần của system prompt giúp định hướng tông giọng, mức độ trang trọng và các quy ước chính tả. champollion đi kèm với một register tiếng Plains Cree:

```
nêhiyawêwin (Plains Cree). Use SRO (Standard Roman Orthography) as the working
script. Output will be converted to Syllabics via deterministic converter.
Professional register appropriate for educational and community contexts.
```

Bạn có thể ghi đè cấu hình này trong tệp config của mình để thử nghiệm các chiến lược viết prompt khác nhau:

```json title="champollion.config.json"
{
  "languages": {
    "crk": {
      "register": "Casual Plains Cree (Y-dialect). Use SRO. Prefer everyday vocabulary over formal or archaic terms. Address the reader directly."
    }
  }
}
```

Các register khác nhau tạo ra các phong cách dịch khác nhau — và điểm số khác nhau trên bảng xếp hạng. Mỗi lượt gửi kết quả sẽ ghi lại chính xác register và system prompt được sử dụng (dưới dạng mã băm SHA-256 trong [thẻ chạy - run card](/docs/specifications/run-card)), nhờ đó các thử nghiệm có thể được tái lập.

### Chuyển đổi hệ chữ viết

Tiếng Plains Cree được viết bằng hai hệ chữ viết: **Chính tả La Mã Tiêu chuẩn (SRO)** và **Chữ âm tiết của Thổ dân Canada (Canadian Aboriginal Syllabics)**. Quy trình của champollion:

1. LLM dịch sang SRO (dựa trên bảng chữ cái Latinh, giúp LLM xử lý tốt hơn)
2. Cổng chất lượng (quality gate) xác thực kết quả đầu ra SRO
3. Bộ chuyển đổi tất định chuyển đổi SRO → Chữ âm tiết (Syllabics)
4. Văn bản đã chuyển đổi được ghi vào đĩa

Bộ chuyển đổi xử lý tất cả các dấu phụ SRO (ê, î, ô, â cho các nguyên âm dài) và ánh xạ chúng sang các ký tự âm tiết chính xác. Xem [Bộ chuyển đổi hệ chữ viết (Script Converters)](https://champollion.dev/docs/concepts/script-converters) để biết chi tiết kỹ thuật.

### Vòng lặp đánh giá

[Khung đánh giá (eval harness)](/docs/specifications/harness) chạy phương pháp của bạn trên tập dữ liệu đánh giá và tạo ra một [thẻ chạy (run card)](/docs/specifications/run-card) đã được chấm điểm:

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install -e .

# Run a baseline experiment
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v7

# Run with FST validation (if you have an FST binary)
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --fst-analyzer ./bin/crk-analyzer \
  --condition fst-gated-v1
```

Cờ `--condition` là một nhãn do bạn chọn. Nó xuất hiện trên bảng xếp hạng để mọi người có thể thấy chiến lược prompt bạn đã sử dụng. Khung đánh giá ghi lại toàn bộ system prompt trong thẻ chạy, giúp phương pháp tiếp cận chính xác của bạn có thể tái lập.

:::tip Tự do thử nghiệm, gửi kết quả tốt nhất của bạn
Khung đánh giá được thiết kế để lặp lại nhanh chóng. Hãy chạy hàng chục thử nghiệm với các mô hình, dữ liệu huấn luyện, register và điều kiện khác nhau. Chỉ gửi lên bảng xếp hạng khi bạn có kết quả mà mình tự hào.
:::

---

## Các nguyên tắc OCAP

champollion được thiết kế để hỗ trợ chủ quyền dữ liệu của người bản địa. [Các nguyên tắc OCAP](https://fnigc.ca/ocap-training/) (Quyền sở hữu - Ownership, Quyền kiểm soát - Control, Quyền truy cập - Access, Quyền chiếm hữu - Possession) định hướng cách chúng tôi tiếp cận công nghệ ngôn ngữ cho các cộng đồng bản địa:

| Nguyên tắc | Cách champollion hỗ trợ |
|-----------|------------------------|
| **Quyền sở hữu (Ownership)** | Các cộng đồng ngôn ngữ sở hữu dữ liệu ngôn ngữ của họ. champollion không bao giờ tự động gửi thông tin về máy chủ hoặc truyền dữ liệu đến máy chủ của chúng tôi |
| **Quyền kiểm soát (Control)** | [Phương thức API](https://champollion.dev/docs/guides/serving-a-method) cho phép các cộng đồng tự lưu trữ quy trình dịch thuật của riêng họ — chúng tôi cung cấp giao diện, họ kiểm soát việc triển khai |
| **Quyền truy cập (Access)** | Các cộng đồng quyết định ai có thể sử dụng phương pháp của họ. API có thể được bảo vệ sau lớp xác thực |
| **Quyền chiếm hữu (Possession)** | Tất cả dữ liệu dịch thuật đều nằm trong hệ thống tệp của dự án của bạn. [Hệ thống truy xuất nguồn gốc (provenance system)](https://champollion.dev/docs/concepts/security) theo dõi nguồn gốc của từng bản dịch |

Kiến trúc plugin có nghĩa là một cộng đồng có thể xây dựng một phương pháp tích hợp các kiến thức thiêng liêng hoặc bị hạn chế trong nội bộ, chỉ công khai API dịch thuật và duy trì toàn quyền kiểm soát đối với tài nguyên ngôn ngữ của họ.

---

## Tầm nhìn: Chặng đường tiếp theo

Tiếng Plains Cree là mục tiêu đầu tiên. Một khi quy trình dịch được xác thực và cộng đồng hài lòng với chất lượng, kiến trúc tương tự sẽ được mở rộng sang các ngôn ngữ đa tổng hợp khác có cơ sở hạ tầng FST:

- **Các ngôn ngữ Algonquian khác**: Woods Cree, Swampy Cree, Ojibwe, Blackfoot
- **Các ngôn ngữ Inuit**: Inuktitut, Inuinnaqtun (những ngôn ngữ cũng sử dụng chữ viết âm tiết)
- **Các ngữ hệ khác**: bất kỳ ngôn ngữ nào có bộ phân tích FST đều có thể sử dụng quy trình dịch FST-gated

Bảng xếp hạng được phân chia theo phạm vi cặp ngôn ngữ. Khi các tập dữ liệu đánh giá mới được đóng góp bởi các cộng đồng ngôn ngữ, các nhánh bảng xếp hạng mới sẽ tự động được mở.

**Đây là một lời mời mở.** Nếu bạn đang làm việc với một ngôn ngữ ít tài nguyên — với tư cách là nhà nghiên cứu, thành viên cộng đồng, sinh viên hay chỉ là một người quan tâm — champollion cung cấp cho bạn các công cụ để xây dựng một sản phẩm thực tế, đo lường nó một cách trung thực và chia sẻ nó với thế giới. [Bảng xếp hạng Phương pháp](https://champollion.dev/leaderboard) đang chờ đợi bài nộp của bạn.

---

## Xem thêm

- **[Bảng xếp hạng Phương pháp](https://champollion.dev/leaderboard)** — gửi điểm số của bạn và xem các phương pháp so sánh với nhau như thế nào
- **[Đánh giá dịch máy (MT Evaluation)](/docs/leaderboard/rules)** — điều gì tạo nên một phương pháp tốt, điều gì khiến phương pháp bị loại
- **[Khung đánh giá (Eval Harness)](/docs/specifications/harness)** — cách chạy các thử nghiệm
- **[Tập dữ liệu đánh giá (Evaluation Datasets)](/docs/leaderboard/datasets)** — EDTeKLA Dev v1 và FLORES+
- **[Dữ liệu huấn luyện (Coaching Data)](https://champollion.dev/docs/concepts/coaching-data)** — cách cấu trúc kiến thức ngôn ngữ cho LLM
- **[Bộ chuyển đổi hệ chữ viết (Script Converters)](https://champollion.dev/docs/concepts/script-converters)** — quy trình chuyển đổi SRO→Syllabics
- **[Cung cấp phương pháp qua API (Serving a Method via API)](https://champollion.dev/docs/guides/serving-a-method)** — lưu trữ hệ thống dịch thuật do cộng đồng kiểm soát
- **[ALTLab](https://altlab.artsrn.ualberta.ca/)** — Alberta Language Technology Lab
- **[EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/)** — nhóm nghiên cứu Công nghệ Giáo dục, Tri thức & Ngôn ngữ
- **[Từ điển itwêwina](https://itwewina.altlab.app/)** — từ điển Plains Cree–Anh được hỗ trợ bởi FST