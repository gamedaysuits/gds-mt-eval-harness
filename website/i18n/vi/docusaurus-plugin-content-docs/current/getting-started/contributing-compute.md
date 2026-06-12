---
sidebar_position: 4
title: "Đóng góp tài nguyên tính toán"
description: "Đóng góp token của bạn: chạy các lượt benchmark mở từ hàng đợi công cộng bằng API key của riêng bạn và công bố kết quả."
related:
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
  - label: "Cookbook: Coached LLM Prompting"
    to: /docs/tutorials/coached-llm-prompting
    kind: cookbook
  - label: "Cookbook: FST-Gated Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "Method Interface & Dependency Classes"
    to: /docs/specifications/methods
    kind: spec
  - label: "Leaderboard Rules & Trust Tiers"
    to: /docs/leaderboard/rules
    kind: guide
---
# Đóng góp tài nguyên tính toán

> **Ý tưởng:** bảng xếp hạng có những ô trống — các tổ hợp (cặp ngôn ngữ, mô hình, điều kiện) chưa có ai đo lường. Chúng tôi duy trì một hàng đợi công khai cho các tổ hợp này. Bạn chạy các mục bằng API key của riêng mình, xuất bản báo cáo, và bản đồ sẽ được lấp đầy. "Quyên góp token" là một đóng góp thực tế, có thể trích dẫn cho việc đánh giá dịch máy (MT) tài nguyên thấp.

## Hàng đợi

Hàng đợi trực tiếp được công bố tại [champollion.dev/queue.json](https://champollion.dev/queue.json), và có một trình xem trên terminal không cần cài đặt:

```bash
curl -fsSL champollion.dev/queue | bash
```

Trình xem này chỉ *hiển thị* các mục đang mở và các lệnh `mt-eval run` chính xác của chúng — nó không bao giờ thực thi bất kỳ lệnh nào hoặc tiêu tốn token của bạn. Mỗi mục bao gồm:

- `run_command` — sẵn sàng để sao chép-dán (tải ngữ liệu, chạy harness)
- `est_cost_usd` và `est_basis` — có thể là chi phí **thực tế ghi nhận được** từ lượt chạy baseline của chính chúng tôi cho cùng tổ hợp (ngữ liệu, mô hình), hoặc một phép **ngoại suy** từ chi phí trung bình của mô hình đó trên mỗi mục nhập × số lượng mục nhập của ngữ liệu. Cơ sở tính toán được nêu rõ cho từng mục; chi phí thực tế của bạn sẽ phụ thuộc vào giá của nhà cung cấp tại thời điểm chạy.
- `priority` — ưu tiên các cặp ngôn ngữ chưa được bao phủ trước, các cặp ngôn ngữ có tài nguyên thấp nhất trước (kích thước ngữ liệu là đại diện), naive trước coached, mô hình rẻ nhất trước.

**Không cần khóa lượt nhận — hãy chọn bất kỳ mục nào đang mở.** Việc hai người cùng chạy một mục hoàn toàn không gây hại theo thiết kế: mỗi thẻ lượt chạy (run card) đều được gắn dấu vân tay (SHA-256 dựa trên hash của tập dữ liệu + mô hình + điều kiện + system prompt, [Thông số kỹ thuật Benchmark §3.8](/docs/specifications/benchmark)), vì vậy các lượt chạy giống hệt nhau sẽ được loại bỏ trùng lặp khi xuất bản, và các lượt tái lập độc lập của cùng một cấu hình là bằng chứng hữu ích chứ không hề lãng phí.

Các ngữ liệu trong hàng đợi là dev-split, thuộc họ giấy phép CC-BY (nguồn gốc từ Tatoeba), và được gắn cờ `do_not_train` — chúng là các tập dữ liệu đánh giá, không phải dữ liệu huấn luyện. Các ngữ liệu có giấy phép phi thương mại và ngữ liệu bị cách ly (quarantined) sẽ bị loại trừ khỏi hàng đợi công khai.

## Thiết lập (một lần duy nhất)

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### Sử dụng key của nhà cung cấp nào?

Harness định tuyến **tất cả** các lệnh gọi mô hình thông qua [OpenRouter](https://openrouter.ai/keys). Chỉ cần một `OPENROUTER_API_KEY` là có thể tiếp cận mọi mô hình trong danh sách hàng đợi — từ Anthropic Claude, OpenAI GPT cho đến Google Gemini — và việc theo dõi chi phí cũng như ảnh chụp nhanh giá (pricing snapshot) của harness đều lấy từ siêu dữ liệu của OpenRouter, vì vậy chi phí lượt chạy được báo cáo sẽ khớp với số tiền thực tế bị trừ trong tài khoản của bạn.

Nếu số dư của bạn nằm trực tiếp tại Anthropic, OpenAI hoặc Google: harness hiện tại **không** chấp nhận key trực tiếp từ các nhà cung cấp này. Lược đồ thẻ lượt chạy (run-card schema) có dự phòng một trường `api_provider` cho tương lai, nhưng hiện tại mọi lượt chạy harness đều thông qua OpenRouter. Tạo tài khoản OpenRouter và nạp tiền (hoặc liên kết tài khoản nhà cung cấp của riêng bạn nếu OpenRouter hỗ trợ) là phương án được hỗ trợ.

### Cách nhanh nhất dùng AI Agent

Nếu bạn làm việc với Claude Code hoặc một coding agent khác, toàn bộ quá trình đóng góp chỉ gói gọn trong một prompt:

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## Cấp độ 1 — Chạy một benchmark

Mỗi `run_command` của mục hàng đợi đều độc lập và tự chứa đầy đủ thông tin. Một ví dụ điển hình:

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

Lượt chạy sẽ in ra tổng chi phí và ghi nhật ký chạy (run log) cùng báo cáo điểm số vào `eval/logs/`. Sau đó, hãy xuất bản:

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

Việc xuất bản sẽ đăng nhập bạn thông qua OAuth (tên của bạn sẽ được ghi nhận trên bảng xếp hạng) và cập nhật (upsert) thẻ lượt chạy. Các đóng góp từ cộng đồng sẽ nằm ở cấp độ tin cậy **self-benchmarked** (tự đo lường) — được dán nhãn rõ ràng là "được gửi bởi người thực hiện". Đây không phải là hạ cấp; đó là cách mô hình tin cậy hoạt động. Thẻ lượt chạy chứa mọi thứ cần thiết để bất kỳ ai cũng có thể chạy lại chính xác cấu hình của bạn: hash của tập dữ liệu, mô hình, điều kiện, system prompt đầy đủ và chi phí. Các cấp độ tin cậy cao hơn (xác minh, xác thực bởi cộng đồng) sẽ được cấp thông qua quá trình đánh giá — xem [Quy tắc Bảng xếp hạng](/docs/leaderboard/rules).

## Cấp độ 2 — Thiết kế prompt có hướng dẫn (coached prompt)

Harness hỗ trợ tối đa cho tính năng **coaching**: thay thế system prompt mặc định (naive) bằng một prompt mang kiến thức ngôn ngữ thực tế. Truyền `--coaching-file` (or `--coaching "inline text"` cho các prompt ngắn) và harness sẽ sử dụng văn bản của bạn làm system prompt, ghi lại **toàn bộ văn bản cùng với mã SHA-256 của nó** trong khối nguồn gốc (provenance block) của nhật ký chạy, và dán nhãn điều kiện của lượt chạy là **`coached`** (trừ khi bạn thiết lập `--prompt` một cách rõ ràng) — nhờ đó, việc thiết kế prompt trở thành một thử nghiệm có thể tái lập và ghi nhận công lao rõ ràng, hai tệp coaching khác nhau không bao giờ bị nhầm lẫn với nhau, và các lượt chạy coached không bao giờ bị đánh đồng với các baseline naive trên bảng xếp hạng.

Một ví dụ thực tế cho tiếng Faroe, sử dụng các đặc điểm loại hình học (typology facts) và các mục từ điển từ [thẻ ngôn ngữ công khai](https://champollion.dev/languages) của ngôn ngữ này:

```text title="coaching-fao.txt"
You are translating Danish into Faroese (føroyskt).

Grammar notes:
- Faroese is a North Germanic V2 language: the finite verb is the second
  constituent of a main clause.
- Nouns inflect for case (nominative, accusative, dative, genitive),
  gender (masculine, feminine, neuter), and number. Make adjectives and
  determiners agree.
- The skerping pattern applies before -gv/-ggj sequences; preserve
  standard orthography including ð (which is silent).

Glossary (use these exact equivalents):
- language -> mál
- island -> oyggj
- weather -> veður

Style: plain register, modern standard orthography. Output only the
Faroese translation, no commentary.
```

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/dan-fao-dev-v1.json
mt-eval run --corpus dan-fao-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Faroese" \
  --coaching-file coaching-fao.txt
```

(Hãy tự viết nội dung coaching của riêng bạn — các thông tin trên minh họa cho *khung sườn*: một vài quy tắc ngữ pháp có tác động lớn, một bảng thuật ngữ nhỏ gồm các từ mô hình hay dịch sai, một hướng dẫn về văn phong. Các thẻ ngôn ngữ tại [champollion.dev/languages](https://champollion.dev/languages) có trích dẫn các nguồn loại hình học mà bạn có thể tham khảo.)

So sánh với baseline naive bằng `mt-eval compare <naive_log> <coached_log>`, lặp lại thử nghiệm và xuất bản lượt chạy tốt nhất của bạn. Lượt chạy sẽ tự động được xuất bản với điều kiện `coached`; nếu bạn muốn bảng xếp hạng hiển thị một phương pháp có tên cụ thể thay vì nhãn chung, hãy đính kèm một thẻ phương pháp (method card) khi xuất bản (quy trình xuất bản có cung cấp một trình hướng dẫn từng bước). Việc vượt qua baseline naive trên một cặp ngôn ngữ tài nguyên thấp chỉ bằng kỹ nghệ prompt (prompt engineering) là một phát hiện thực sự có giá trị và có thể công bố — xem hướng dẫn đầy đủ tại [Tài liệu hướng dẫn Coached LLM Prompting](/docs/tutorials/coached-llm-prompting) để biết thêm chi tiết thiết kế.

## Cấp độ 3 — Xây dựng một phương pháp

Đóng góp đầy tham vọng nhất: triển khai giao thức `TranslationMethod` (`translate(entries, config)`) và benchmark một hệ thống thực tế, chứ không chỉ là một prompt. Harness sẽ chạy nó thông qua `--method <plugin-dir>` và nhúng thẻ phương pháp của bạn vào thẻ lượt chạy. Các mô hình thiết kế kèm hướng dẫn thực hành:

- **[FST-gated pipelines](/docs/tutorials/fst-gated-pipeline)** — mỗi từ ứng viên đều được kiểm tra bởi một bộ phân tích hình thái; LLM sẽ tạo lại cho đến khi vượt qua cổng kiểm duyệt. Đầu ra bán xác định (semi-deterministic), đảm bảo chuẩn xác về mặt hình thái học.
- **[Dictionary-augmented generation](/docs/tutorials/dictionary-augmented-llm)** — tra cứu các thuật ngữ nguồn trong từ điển song ngữ tại thời điểm dịch và áp đặt ràng buộc cho đầu ra.
- [Chained models](/docs/tutorials/chained-models), [few-shot retrieval](/docs/tutorials/few-shot-prompting), [back-translation](/docs/tutorials/back-translation), [rule-based hybrids](/docs/tutorials/rule-based-hybrid)…

Các phương pháp khai báo một **dependency class** (S/O/A1/A2/X — xem [thông số kỹ thuật của phương pháp](/docs/specifications/methods#method-validity-and-dependency-classes)) mô tả những gì chúng cần để chạy và chuyển giao: một pipeline độc lập là Class S; một pipeline gọi API từ điển có bản quyền khi chạy là A2. Hãy khai báo trung thực — class này quyết định nơi phương pháp của bạn có thể cạnh tranh, và các manifest sẽ được kiểm định.

## Tại sao điều này lại quan trọng ngoài phạm vi bảng xếp hạng

Mỗi lượt chạy được xuất bản là một bằng chứng độc lập về chất lượng dịch máy (MT) cho một cặp ngôn ngữ mà các nhà cung cấp thương mại không đo lường. Hàng đợi này đồng thời đóng vai trò là một hồ sơ công khai về *nhu cầu*: những cặp ngôn ngữ nào được cộng đồng đánh giá là đáng đo lường, chi phí bao phủ ở mức giá API hiện tại là bao nhiêu, và tài nguyên tính toán được quyên góp có thể đi được bao xa. Khi chúng tôi yêu cầu các quỹ tài trợ bảo trợ cho các đợt quét hệ thống (systematic sweeps), hàng đợi này và tỷ lệ lấp đầy của nó chính là bằng chứng thực tế về nhu cầu.