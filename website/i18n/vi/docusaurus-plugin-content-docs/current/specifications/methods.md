---
sidebar_position: 4
title: "Giao diện phương thức"
related:
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
    note: "Put this interface on the leaderboard"
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
    note: "A full method, built end-to-end"
---
# Giao diện Phương thức Dùng chung

> **Tóm tắt tổng quan.** Trang này quy định giao thức `TranslationMethod` mà tất cả các phương thức trong Arena phải triển khai, sáu lớp phương thức (`raw-llm`, `coached-llm`, `pipeline`, `custom-plugin`, `api`, `human`), định dạng plugin phương thức, và các **lớp phụ thuộc** (S/O/A1/A2/X) quyết định xem một phương thức có thể chạy trong sandbox đánh giá và đủ điều kiện nhận giải thưởng hay không. Bất kỳ phương pháp nào triển khai giao thức này đều có thể được đánh giá hiệu năng (benchmarked); việc phương thức đó phụ thuộc vào yếu tố nào sẽ quyết định nơi nó có thể cạnh tranh.

Hệ thống đánh giá (eval harness) và champollion chia sẻ một khái niệm chung về **phương thức dịch thuật** (translation method). Một phương thức là bất kỳ quy trình nào nhận văn bản nguồn và tạo ra văn bản dịch — cho dù đó là một cuộc gọi LLM trực tiếp, một pipeline nhiều giai đoạn, một API bên thứ ba, hay một dịch giả con người.

## Kiến trúc

```
Method Plugin (v2 Spec)
├── method.json           ← Manifest (name, class, entry_point, dependencies, metadata)
├── method_card.json      ← Leaderboard description (what, not how)
├── pipeline.py           ← Python module implementing TranslationMethod
└── (optional helpers)    ← Additional Python modules
```

Được tải thông qua `--method path/to/dir`. Hệ thống đánh giá không tự động phát hiện bất kỳ điều gì.

## Hai Hệ thống, Một Giao diện

| | Eval Harness | champollion |
|---|---|---|
| **Ngôn ngữ** | Python | Node.js |
| **Điểm đầu vào** | `translate.py` | `translate.js` |
| **Giao diện** | Giao thức `TranslationMethod` | Cấu hình `methodPlugin` |
| **Mục đích** | Đánh giá hàng loạt kèm tính điểm | Bản địa hóa trực tiếp trong dev/CI |
| **Đầu ra** | Run card kèm các chỉ số (metrics) | Các tệp ngôn ngữ (locale) đã dịch |

Một phương thức hỗ trợ cả hai hệ thống sẽ cung cấp hai điểm đầu vào — mỗi điểm cho một môi trường thực thi (runtime) ngôn ngữ tương ứng. **Thẻ phương thức** (method card) đóng vai trò là cầu nối: nó mô tả phương thức dưới định dạng mà cả hai hệ thống đều hiểu.

## Thẻ Phương thức

Thẻ phương thức mô tả phương thức dịch thuật đó là *gì* mà không làm lộ các chi tiết độc quyền như toàn bộ system prompt. Nó trả lời các câu hỏi:

- Đây là lớp phương thức nào? (LLM thô, LLM có hướng dẫn, pipeline, API, v.v.)
- Nó sử dụng những công cụ nào? (bộ phân tích FST, từ điển, v.v.)
- Bản triển khai có phải là mã nguồn mở không?
- Nó hỗ trợ những cặp ngôn ngữ nào?

Xem [Thông số Thẻ Phương thức](/docs/specifications/methods#method-card) để biết schema JSON đầy đủ.

### Ví dụ

```json
{
  "method_id": "fst-gated-v8",
  "name": "FST-Gated Coached Translation v8",
  "class": "pipeline",
  "description": "LLM translation with morphological validation. Failed words are retried with FST feedback.",
  "author": "Curtis Forbes",
  "tools_used": ["HFST morphological analyzer", "Wolvengrey dictionary"],
  "open_source": false,
  "dependency_class": "A2",
  "supported_pairs": ["eng>crk"]
}
```

Trường `dependency_class` tóm tắt những gì phương thức cần để chạy và chuyển giao — xem phần [Tính hợp lệ của Phương thức và Lớp Phụ thuộc](#method-validity-and-dependency-classes) bên dưới.

### Các Lớp Phương thức

| Lớp | Mô tả |
|-------|-------------|
| `raw-llm` | Gọi LLM trực tiếp với chỉ dẫn tối thiểu |
| `coached-llm` | LLM với prompt có cấu trúc, ví dụ, và các ràng buộc |
| `pipeline` | Pipeline nhiều giai đoạn với các thành phần tất định (deterministic) |
| `custom-plugin` | Tiến trình bên ngoài triển khai giao thức `TranslationMethod` |
| `api` | API dịch thuật của bên thứ ba (Google Translate, DeepL, v.v.) |
| `human` | Dịch thuật bởi con người (để thiết lập mốc so sánh - baseline) |

## Tính hợp lệ của Phương thức và Lớp Phụ thuộc

Một phương thức chỉ có thể chạy được và chuyển giao được dựa trên mức độ sẵn có của thành phần phụ thuộc kém sẵn có nhất của nó. Hai cơ chế của Arena phụ thuộc vào việc biết chính xác một phương thức cần những gì:

1. **Đánh giá trong sandbox** ([Thông số Benchmark §8.2](/docs/specifications/benchmark)) — các điểm số tiêu chuẩn vàng chính thức đến từ một sandbox có chính sách mạng là **từ chối theo mặc định (default-deny)**. Một phương thức âm thầm yêu cầu dịch vụ bên ngoài sẽ không thể tạo ra điểm số chính thức.
2. **Chuyển giao giải thưởng** ([Thông số Giải thưởng](/docs/specifications/prizes)) — các phương thức đoạt giải sẽ được chuyển giao cho tổ chức quản trị của cộng đồng ngôn ngữ. Một phương thức đóng gói nội dung mà người nộp không có quyền tích hợp thì không thể được chuyển giao một cách hợp pháp. Người nộp phải nắm giữ (hoặc được cấp) quyền đối với mọi thứ bên trong gói.

Để cả hai quá trình kiểm tra này diễn ra một cách tự động thay vì tự phát (ad hoc), mỗi phương thức phải khai báo một **lớp phụ thuộc** (dependency class), được suy ra từ một **bản kê khai phụ thuộc** (dependency manifest) trong `method.json`.

> **Lưu ý về cách đặt tên.** *Lớp phương thức* (mục trên: `raw-llm`, `pipeline`, …) mô tả *cách một phương thức dịch*. *Lớp phụ thuộc* (phần này) mô tả *những gì một phương thức cần để chạy và chuyển giao*. Chúng là các trục độc lập: một phương thức `pipeline` có thể thuộc bất kỳ lớp phụ thuộc nào.

### Năm Lớp Phụ thuộc

| Lớp | Tên | Định nghĩa | Có thể chạy trong Sandbox? | Đủ điều kiện nhận giải? |
|-------|------|-----------|-------------------|-----------------|
| **S** | Tự đóng gói (Self-contained) | Toàn bộ mã nguồn, dữ liệu, mô hình và trọng số được phân phối bên trong thư mục phương thức, dưới các giấy phép cho phép phân phối lại và chuyển giao cho cộng đồng. | ✅ Có, nguyên bản | ✅ Có |
| **O** | Bên ngoài mở (Open external) | Phụ thuộc vào các thành phần lưu trữ bên ngoài dưới các giấy phép mở cho phép phân phối lại (bao gồm cả các giấy phép copyleft như AGPL) — ví dụ: một FST được tải xuống tại thời điểm cài đặt. | ✅ Có — các thành phần được ghim cố định và **được sao lưu (mirror) vào bản nộp** | ✅ Có, với các điều kiện tương thích giấy phép: các điều khoản copyleft được bảo toàn qua quá trình chuyển giao, và cộng đồng nhận được các quyền tương tự như giấy phép cấp cho mọi người |
| **A1** | Phụ thuộc API, có thể thay thế | Yêu cầu suy luận LLM tại thời điểm chạy, trong đó mô hình là **cấu hình có thể thay thế** — bất kỳ mô hình nào đủ năng lực đều có thể được đưa vào. Giá trị của phương thức nằm ở các prompt, dữ liệu hướng dẫn (coaching data) và mã nguồn của nó, chứ không nằm ở mô hình của bất kỳ nhà cung cấp cụ thể nào. | ⚠️ Chỉ thông qua **cổng LLM (LLM gateway)** được định nghĩa trong thông số sandbox (🔲 đã lên kế hoạch — xem bên dưới) | ⚠️ Có điều kiện — xem bên dưới |
| **A2** | Phụ thuộc API, không thể thay thế | Yêu cầu gọi đến một API dữ liệu hoặc dịch vụ bên ngoài tại thời điểm chạy mà không thể sao lưu hoặc thay thế — thường là do nội dung được cung cấp là độc quyền hoặc không có giấy phép (ví dụ: một API từ điển mà từ điển nền tảng của nó không có giấy phép công khai). | ❌ Không — thành phần phụ thuộc không thể tồn tại trong sandbox nếu không có sự cho phép của chủ sở hữu quyền | ❌ Không cho đến khi chủ sở hữu quyền cấp quyền tích hợp vào sandbox **và** quyền chuyển giao. Được phép xuất hiện trên bảng xếp hạng mở (phân khúc phát triển) với nhãn **"phụ thuộc bên ngoài" (external dependency)** hiển thị rõ ràng |
| **X** | Đóng (Closed) | Đóng gói nội dung mà người nộp không có quyền phân phối lại — các tập dữ liệu không có giấy phép, nội dung độc quyền được thu thập trái phép (scraped), các thành phần không tương thích về giấy phép. | ❌ | ❌ Không được chấp nhận trong mọi phân khúc. Việc đóng gói nội dung không có bản quyền là vi phạm giấy phép bất kể phương thức chạy ở đâu |

**Lớp hiệu dụng.** Lớp phụ thuộc của một phương thức là lớp *hạn chế nhất* trong số tất cả các phụ thuộc đã khai báo của nó, theo thứ tự S < O < A1 < A2 < X. Một từ điển không có giấy phép sẽ biến một pipeline vốn tự đóng gói thành Lớp A2 (nếu được truy cập tại thời điểm chạy) hoặc Lớp X (nếu được đóng gói kèm theo mà không có quyền).

### Sự khác biệt giữa A1/A2: Khả năng thay thế

Hầu hết các phương thức đều gọi LLM. Arena không phủ nhận điều đó — nhưng nó phân biệt hai loại phụ thuộc API rất khác nhau:

- **A1 (có thể thay thế):** API cung cấp dịch vụ suy luận LLM thông thường. Định danh mô hình là một cấu hình: phương thức phải chạy từ đầu đến cuối với bất kỳ điểm cuối suy luận (inference endpoint) tương thích nào, bao gồm cả mô hình trọng số mở (open-weight) do cộng đồng tự lưu trữ. Chất lượng đầu ra có thể khác nhau giữa các mô hình — đó là rủi ro của nhà phát triển, và điểm số chính thức sẽ gắn liền với mô hình được ghim cố định dùng trong quá trình đánh giá. Một phương thức phụ thuộc vào **trạng thái phía nhà cung cấp** (một bản fine-tune chỉ được lưu trữ tại nhà cung cấp, kho lưu trữ tệp của nhà cung cấp, các trợ lý riêng của nhà cung cấp) thì *không* thể thay thế: trạng thái đó không thể bị loại bỏ hoặc thay thế, vì vậy thành phần phụ thuộc đó là A2 trừ khi các trọng số hoặc dữ liệu nền tảng được bao gồm trong bản nộp.
- **A2 (không thể thay thế):** API cung cấp một thứ gì đó độc nhất — thường là dữ liệu độc quyền hoặc không có giấy phép. Không có điểm cuối thay thế nào có thể cung cấp nó, và nội dung không thể được sao lưu vào sandbox nếu không có sự cho phép của chủ sở hữu quyền. Phương thức này vẫn hoạt động trên bảng xếp hạng mở (được gắn nhãn), nhưng không thể tạo ra điểm số sandbox chính thức hoặc đủ điều kiện nhận giải thưởng cho đến khi có sự cho phép.

**Những gì một đợt chuyển giao giải thưởng A1 thực sự mang lại.** Cộng đồng không nhận được mô hình — không ai có thể chuyển giao trọng số của Anthropic, Google hay OpenAI. Việc chuyển giao bao gồm toàn bộ công thức *xung quanh* mô hình: tất cả các prompt, dữ liệu hướng dẫn, mã nguồn pipeline, logic thử lại (retry logic), cấu hình và các yêu cầu mô hình đã được ghi chép lại. Vì mô hình được thiết kế để có thể thay thế, cộng đồng có thể hướng phương thức được chuyển giao tới bất kỳ nhà cung cấp nào họ chọn — hoặc tới một mô hình trọng số mở trên phần cứng của riêng họ — mà không cần sự can thiệp của nhà phát triển. Công thức là thứ được sở hữu; động cơ là thứ được thuê và có thể thay thế.

### Bản kê khai Phụ thuộc (`method.json`)

Mỗi phương thức khai báo các phụ thuộc của nó trong bản kê khai `method.json`. Mỗi mục ghi lại thành phần (artifact) đó là gì, nó đến từ đâu, giấy phép nào bảo hộ nó và cách phương thức truy cập nó:

```json
{
  "name": "FST-Gated Coached Translation v8",
  "method_id": "fst-gated-v8",
  "class": "pipeline",
  "entry_point": "pipeline:PipelineMethod",
  "supported_pairs": ["eng>crk"],
  "dependency_class": "A2",
  "dependencies": [
    {
      "id": "giellalt-lang-crk-fst",
      "kind": "software",
      "license": "AGPL-3.0-or-later",
      "access": "mirrored",
      "source": "https://github.com/giellalt/lang-crk",
      "pin": "sha256:3f1a…",
      "redistributable": true,
      "transferable": true
    },
    {
      "id": "llm-inference",
      "kind": "model",
      "license": "proprietary",
      "access": "gateway",
      "source": "openrouter:google/gemini-2.5-flash",
      "substitutable": true,
      "redistributable": false,
      "transferable": false,
      "notes": "Any compatible chat-completions endpoint works; the model slug is configuration."
    },
    {
      "id": "crk-dictionary-api",
      "kind": "service",
      "license": "none",
      "access": "external-api",
      "source": "https://itwewina.altlab.app/",
      "redistributable": false,
      "transferable": false,
      "notes": "Dictionary content has no public license; runtime lookups only. Class A2 until the rights holders grant permission."
    }
  ]
}
```

| Trường | Bắt buộc | Mô tả |
|-------|----------|-------------|
| `id` | ✅ | Định danh ổn định cho thành phần phụ thuộc |
| `kind` | ✅ | `data`, `model`, `software`, hoặc `service` |
| `license` | ✅ | Định danh SPDX, `proprietary`, hoặc `none`. `none` nghĩa là không có giấy phép công khai — được coi là giữ toàn bộ bản quyền (all-rights-reserved) |
| `access` | ✅ | `bundled` (đi kèm trong thư mục phương thức), `mirrored` (được tải khi cài đặt, được ghim cố định, được tích hợp vào bản nộp), `gateway` (suy luận LLM tại thời điểm chạy qua cổng đánh giá), `external-api` (bất kỳ cuộc gọi mạng nào khác tại thời điểm chạy) |
| `source` | ✅ | URL chuẩn (canonical URL) hoặc định danh `provider:slug` |
| `pin` | cho `mirrored` | Phiên bản, commit, hoặc mã băm nội dung (content hash) giúp ghim chính xác thành phần |
| `substitutable` | cho `gateway`/`external-api` | Liệu bất kỳ điểm cuối tương thích nào cũng có thể cung cấp thành phần phụ thuộc này hay không |
| `redistributable` | ✅ | Liệu giấy phép có cho phép phân phối lại thành phần này hay không |
| `transferable` | ✅ | Liệu thành phần (hoặc quyền đối với nó) có thể được chuyển giao cho cộng đồng theo các điều khoản chuyển giao giải thưởng hay không |
| `notes` | ❌ | Ngữ cảnh tự do |

**Suy luận lớp.** Mỗi thành phần phụ thuộc sẽ đóng góp một lớp; `dependency_class` của phương thức sẽ là lớp hạn chế nhất:

| Hồ sơ phụ thuộc | Đóng góp |
|--------------------|-------------|
| `bundled` + giấy phép cho phép phân phối lại và chuyển giao | S |
| `mirrored` + giấy phép mở cho phép phân phối lại (bao gồm cả copyleft) | O |
| `gateway` + `substitutable: true` (suy luận LLM) | A1 |
| `external-api`, hoặc `gateway` với `substitutable: false` | A2 |
| `bundled` + `license: none` hoặc giấy phép không tương thích với việc phân phối lại | X |

`dependency_class` được khai báo phải khớp với lớp mà hệ thống đánh giá suy ra từ bản kê khai. Sự không khớp sẽ dẫn đến lỗi xác thực.

Một phương thức **không** có phụ thuộc bên ngoài sẽ khai báo `"dependency_class": "S"` và `"dependencies": []`. Mảng rỗng là một tuyên bố khẳng định, được kiểm tra giống như bất kỳ khai báo nào khác.

### Cách Xác minh Tính hợp lệ

Ba lớp xác minh, từ đơn giản nhất đến đáng tin cậy nhất:

1. **Kiểm tra bản kê khai.** Hệ thống đánh giá sẽ suy ra lớp hiệu dụng từ bản kê khai và từ chối nếu có sự không khớp. Người đánh giá sẽ kiểm tra từng phụ thuộc đã khai báo so với giấy phép và nguồn đã nêu của nó — một phụ thuộc được khai báo là `redistributable: true` nhưng giấy phép gốc của nó nói ngược lại sẽ không vượt qua vòng kiểm duyệt.
2. **Phân tích tĩnh.** Mã nguồn được nộp sẽ được quét để tìm các cuộc gọi mạng, tải xuống động và truy cập hệ thống tệp mà bản kê khai không đề cập đến. Một phụ thuộc *không được khai báo* bị phát hiện trong quá trình kiểm duyệt sẽ là lý do để từ chối bản nộp, bất kể nó thuộc lớp nào — bản kê khai phải đầy đủ chứ không chỉ chính xác.
3. **Chính sách mạng của Sandbox.** Thông số sandbox yêu cầu **từ chối lưu lượng đi theo mặc định (default-deny egress)**: các container phương thức không có quyền truy cập mạng trừ khi một đường dẫn được đưa vào danh sách cho phép (allowlist) một cách rõ ràng. Đường dẫn đi duy nhất mà thông số kỹ thuật định nghĩa là **cổng LLM (LLM gateway)** — một proxy suy luận được vận hành bởi cơ sở hạ tầng đánh giá, bị giới hạn trong một danh sách cho phép rõ ràng gồm các mô hình được ghim cố định, với mọi yêu cầu và phản hồi đều được ghi nhật ký (log) để kiểm tra sau khi chạy. Bất kỳ thứ gì không nằm trong danh sách cho phép sẽ thất bại ở lớp mạng, chứ không phải ở lớp chính sách. Xem [Thông số Benchmark §8.6](/docs/specifications/benchmark) để biết thiết kế cổng kết nối và chính sách mạng.

> 🔲 **Đã lên kế hoạch.** Sandbox và cổng LLM của nó đã được đặc tả nhưng chưa được xây dựng. Cho đến khi cổng kết nối đi vào hoạt động, chỉ các phương thức Lớp S và Lớp O mới có thể được đánh giá trong sandbox; các phương thức Lớp A1 *về nguyên tắc* vẫn đủ điều kiện nhận giải thưởng nhưng chưa thể tạo ra điểm số tiêu chuẩn vàng chính thức. Trang này mô tả những gì thông số kỹ thuật yêu cầu, chứ không phải những gì hiện đang chạy.

### Hiển thị trên Bảng xếp hạng

- Bảng xếp hạng hiển thị lớp phụ thuộc của từng phương thức bên cạnh huy hiệu lớp phương thức của nó.
- Các phương thức Lớp A2 trên bảng xếp hạng mở sẽ mang nhãn **"phụ thuộc bên ngoài" (external dependency)** hiển thị rõ ràng: điểm số của chúng phụ thuộc vào dịch vụ của bên thứ ba có thể thay đổi hoặc biến mất, và hiện tại chúng không đủ điều kiện nhận giải thưởng.
- Các phương thức Lớp X không được liệt kê.

## Eval Harness: Giao thức TranslationMethod

Hệ thống đánh giá (eval harness) sử dụng kiểu cấu trúc (structural typing) của Python (`Protocol`) cho các plugin. Bất kỳ lớp nào có chữ ký phương thức (method signature) phù hợp đều hoạt động — không yêu cầu kế thừa:

```python
class MyMethod:
    async def translate(self, entries: list[dict], config: RunConfig) -> list[dict]:
        results = []
        for entry in entries:
            translation = await self.do_translation(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translation,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "error": None,
                "tool_calls": [],
                "tool_call_count": 0,
                "metadata": {},
            })
        return results
```

Xem [Giao thức Plugin](/docs/specifications/methods#eval-harness-translationmethod-protocol) để biết tài liệu đầy đủ bao gồm các ví dụ về trình bao bọc (wrapper) cho các phương thức không phải Python.

## champollion: Cấu hình methodPlugin

Trong champollion, các phương thức được đăng ký theo từng cặp ngôn ngữ trong `champollion.config.json`:

```json
{
  "version": 3,
  "pairs": {
    "en:crk": {
      "methodPlugin": "crk-coached-v1"
    }
  }
}
```

Xem [Thông số Plugin](https://champollion.dev/docs/reference/plugin-spec) để biết giao diện phía champollion.

## Tích hợp Bảng xếp hạng

Khi một thẻ phương thức được đính kèm vào một lượt chạy (thông qua `--method-card`), nó sẽ được nhúng vào run card và hiển thị trên bảng xếp hạng:

```bash
# Run with method card attached
mt-eval run \
  --method path/to/my-method \
  --corpus data/edtekla-dev-v1.json \
  --method-card method_card.json

# Publish to the leaderboard
mt-eval publish eval/logs/harness/your-run-card.json
```

Nếu không cung cấp `--method-card`, `mt-eval publish` sẽ khởi chạy một trình hướng dẫn tương tác (wizard) để dẫn dắt bạn qua các bước mô tả phương thức của mình.

Bảng xếp hạng hiển thị:
- **Huy hiệu lớp** — chỉ báo trực quan (ví dụ: "pipeline", "coached-llm")
- **Lớp phụ thuộc** — S/O/A1/A2 (xem [Tính hợp lệ của Phương thức và Lớp Phụ thuộc](#method-validity-and-dependency-classes)); các phương thức A2 mang nhãn "phụ thuộc bên ngoài"
- **Tên phương thức** — lấy từ thẻ phương thức
- **Công cụ sử dụng** — được liệt kê từ thẻ phương thức
- **Chỉ báo mã nguồn mở**

Khi không có thẻ phương thức nào được đính kèm, bảng xếp hạng sẽ hiển thị cấu hình gốc của hệ thống đánh giá (mô hình, phiên bản prompt, nhiệt độ - temperature, các công cụ được bật).

:::danger KHÔNG HUẤN LUYỆN trên dữ liệu đánh giá
Các phương thức có quy trình phát triển bao gồm việc tiếp xúc với tập dữ liệu đánh giá — dưới dạng dữ liệu huấn luyện, ví dụ few-shot, mục từ điển hoặc tài liệu tinh chỉnh prompt (prompt tuning) — sẽ bị **tước quyền thi đấu (disqualified)** khỏi bảng xếp hạng. Xem [Đánh giá MT](/docs/leaderboard/rules) để biết điều gì phân biệt một phương thức tốt với một phương thức không tốt.
:::

---

## Xem thêm

- [Đánh giá MT](/docs/leaderboard/rules) — tổng quan, giá trị của bảng xếp hạng và hướng dẫn về phương thức tốt/không tốt
- [Eval Harness](/docs/specifications/harness) — cách chạy các đánh giá
- [Tập dữ liệu Đánh giá](/docs/leaderboard/datasets) — các tập dữ liệu có sẵn (EDTeKLA, FLORES+)
- [Thông số Run Card](/docs/specifications/run-card) — schema JSON của run card
- [Thông số Plugin](https://champollion.dev/docs/reference/plugin-spec) — giao diện plugin phía champollion
- [Bảng xếp hạng Phương thức](https://champollion.dev/leaderboard) — điểm số benchmark trực tiếp
- [Thông số Benchmark](/docs/specifications/benchmark) — giao thức đánh giá, định dạng ngữ liệu (corpus), schema của run card
- [Thông số Tính điểm](/docs/specifications/scoring) — SSOT cho các chỉ số (metrics), trọng số tổng hợp (composite weights) và các phân tầng chất lượng (quality tiers)