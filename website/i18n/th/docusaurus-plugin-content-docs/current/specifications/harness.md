---
sidebar_position: 2
title: "Eval Harness v2.0"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "What the harness metrics feed into"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: Translate 30 Languages"
    to: https://champollion.dev/docs/tutorials/translate-30-languages
    kind: champollion
    note: "Use the harness to audit registers in production"
---
# Eval Harness v2.0

> **สรุปสำหรับผู้บริหาร** หน้านี้ครอบคลุมการติดตั้ง การกำหนดค่า และการใช้งาน MT evaluation harness — เครื่องมือที่ใช้ทดสอบประสิทธิภาพวิธีการแปลกับคอร์ปัสมาตรฐานและสร้าง run card ที่มีคะแนน สำหรับนิยามอย่างเป็นทางการของ metric, schema และโปรโตคอลการประเมิน โปรดดูที่ [Benchmark Specification](/docs/specifications/benchmark)

harness รันการทดลองแปลและสร้าง run card โดยจัดการการสร้าง prompt, การเรียก API, การให้คะแนน และการบันทึกผลลัพธ์ — คุณเพียงแค่จัดเตรียม dataset และ model

## การติดตั้ง

**ข้อกำหนด:** Python 3.10+

```bash
pip install sacrebleu aiohttp
```

Clone repository ของ harness:

```bash
git clone https://github.com/gamedaysuits/arena.git
cd arena
```

## การใช้งาน

```bash
mt-eval run --corpus path/to/dataset.json
```

คำสั่งนี้จะรันทุก entry ในคอร์ปัสผ่าน model ที่กำหนดค่าไว้ (หรือ method plugin), ให้คะแนน output และเขียนไฟล์ run card JSON ไปยัง output directory

## CLI Flags

### `mt-eval run`

| Flag | Required | Default | คำอธิบาย |
|------|----------|---------|-------------|
| `--corpus` | ✅ | — | พาธไปยังไฟล์คอร์ปัส (`.json`, `.jsonl`, `.tsv`) |
| `--source-file` / `--reference-file` | — | — | ไฟล์ข้อความคู่ขนาน (รูปแบบ FLORES+, WMT) |
| `-m, --model` | — | `gemini-pro` | Model slug (ชื่อย่อหรือ OpenRouter ID แบบเต็ม) ค้นหาผ่าน `shared/model-aliases.json` คั่นด้วยเครื่องหมายจุลภาคสำหรับการรันหลาย model |
| `-d, --dataset` | — | `all` | ตัวกรอง dataset: `all`, ชื่อ segment หรือช่วง ID |
| `--ids` | — | — | ID ของ entry ที่ต้องการประเมิน คั่นด้วยเครื่องหมายจุลภาค |
| `--source-lang` | — | `English` | ชื่อภาษาต้นทาง |
| `--target-lang` | — | — | ชื่อภาษาปลายทาง |
| `-p, --prompt` | — | `naive` | เวอร์ชันของ prompt (`naive`, `custom`, `champollion`) |
| `--coaching-file` | — | — | พาธไปยังไฟล์ข้อความ coaching prompt |
| `--coaching` | — | — | ข้อความ coaching แบบ inline (string ที่อยู่ในเครื่องหมายคำพูด) |
| `--method` | — | — | พาธไปยัง directory ของ method plugin (ประกอบด้วย `method.json` + Python module) |
| `--method-card` | — | — | พาธไปยัง method card JSON สำหรับ metadata ของ leaderboard |
| `--fst-retries` | — | `0` | จำนวนครั้งที่ลองใหม่สำหรับ FST (เฉพาะ default LLM method เท่านั้น) |
| `--skip-fst` | — | `false` | ข้าม FST quality gate ทั้งหมด |
| `--tools` | — | `false` | เปิดใช้งานโหมด tool-calling |
| `--tools-list` | — | — | ชื่อ tool คั่นด้วยเครื่องหมายจุลภาค |
| `--max-tool-rounds` | — | `8` | จำนวนรอบ tool-calling สูงสุดต่อ entry |
| `--hooks` | — | — | ชื่อ hook หลังการแปล |
| `--style-profile` | — | — | พาธไปยัง style profile JSON เปิดใช้งาน metric ความสอดคล้องของรูปแบบการเขียน (เพื่อให้ข้อมูลเท่านั้น — ไม่นับรวมใน composite score เลย ดู [§ Writing-style and register metrics](#writing-style-and-register-metrics-informational)) |
| `-b, --batch-size` | — | `25` | จำนวน entry ต่อการเรียก API หนึ่งครั้ง |
| `-c, --concurrency` | — | `8` | จำนวนการเรียก API แบบขนาน |
| `--max-tokens` | — | `32768` | จำนวน token สูงสุดต่อการเรียก API หนึ่งครั้ง |
| `--temperature` | — | `0.0` | อุณหภูมิการสุ่ม (0.0 = กำหนดตายตัว) |
| `--no-cache` | — | `false` | ปิดใช้งานการแคช response |
| `--cache-dir` | — | `eval/cache/harness` | พาธของ directory สำหรับแคช |
| `-o, --output-dir` | — | `eval/logs/harness` | Output directory สำหรับ run card และ log |
| `-n, --name` | — | — | ชื่อ run ที่อ่านได้โดยมนุษย์ |
| `--dry-run` | — | `false` | ตรวจสอบการกำหนดค่าโดยไม่เรียก API |
| `--champollion-config` | — | — | พาธไปยัง `champollion.config.json` |
| `--champollion-cards-dir` | — | — | directory ของ language card |
| `--target-lang-code` | — | — | รหัสภาษา BCP-47 |

### Subcommand อื่น ๆ

| Subcommand | คำอธิบาย |
|------------|-------------|
| `mt-eval test <log_path>` | วิเคราะห์ run log ที่เสร็จสมบูรณ์แล้ว |
| `mt-eval publish <report_path>` | ส่ง run card ไปยัง leaderboard |
| `mt-eval compare <logs...>` | เปรียบเทียบหลาย run แบบเคียงกัน |
| `mt-eval dashboard <logs...>` | สร้าง HTML dashboard จาก run log |
| `mt-eval list models\|prompts\|datasets` | แสดงรายการทรัพยากรที่มีอยู่ |
| `mt-eval export` | แพ็กเกจการตั้งค่าปัจจุบันเป็น champollion method plugin |
| `mt-eval export-config` | ส่งออก MethodConfig ที่ resolve แล้ว (ทั้ง 8 canonical field) เป็น JSON |

### ตัวอย่าง

```bash
# Run with defaults (gemini-pro alias → google/gemini-3.1-pro-preview, naive prompt)
mt-eval run --corpus data/edtekla-dev-v1.json

# Coached experiment with coaching file
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model google/gemini-3.1-pro \
  --coaching-file prompts/crk-coaching-v8.txt \
  --temperature 0.0

# Run a custom method plugin with FST retries
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --method ./methods/fst-gated-pipeline \
  --fst-retries 3
```

---

## Run Card Schema

ทุกการทดลองจะสร้าง **run card** — เอกสาร JSON ที่มีข้อมูลครบในตัวเอง โครงสร้างระดับบนสุด:

```json
{
  "run_id": "uuid-v4",
  "harness_version": "2.0",
  "model_slug": "google/gemini-3.1-pro",
  "model_id": "gemini-3.1-pro-001",
  "condition": "baseline",
  "timestamp": "2026-06-01T03:22:41Z",
  "elapsed_seconds": 142.7,
  "dataset": { ... },
  "config": { ... },
  "method_card": { ... },
  "system_prompt_sha256": "abc123...",
  "system_prompt_used": "You are a translator...",
  "fingerprint": { ... },
  "scores": { ... },
  "totals": { ... },
  "environment": { ... },
  "results": [ ... ],
  "run_card_hash": "sha256-of-entire-card"
}
```

ดู [Run Card Specification](/docs/specifications/run-card) สำหรับ schema แบบเต็มพร้อมเอกสารประกอบทุก field

:::info Schema อ้างอิง
[Benchmark Specification](/docs/specifications/benchmark) คือแหล่งข้อมูลเดียวที่เชื่อถือได้สำหรับ run card schema สำหรับนิยาม metric, น้ำหนัก composite และระดับคุณภาพ โปรดดูที่ [Scoring Specification](/docs/specifications/scoring) หน้านี้อธิบายวิธีใช้ harness ส่วน spec กำหนดความหมายของ output
:::

### บล็อกสำคัญ

**`dataset`** — ระบุว่าใช้ dataset ใด รวมถึง content hash เพื่อผูกผลลัพธ์กับเวอร์ชันที่เฉพาะเจาะจง:

```json
// Example using master_corpus.json (62 gold + 342 textbook = 404)
{
  "id": "edtekla-dev-v1",
  "version": "1.0",
  "language_pair": "EN→CRK",
  "sha256": "...",
  "entry_count": 404
}
```

**`scores`** — metric รวมสำหรับการรัน:

```json
// Counts reflect the dataset used (here: master_corpus.json, 404 entries)
{
  "total": 404,
  "exact_matches": 12,
  "exact_match_rate": 0.0968,
  "fst_accepted": 87,
  "fst_acceptance_rate": 0.7016,
  "chrf_plus_plus": 42.31,
  "errors": 0,
  "avg_latency_seconds": 1.15,
  "median_latency_seconds": 1.02,
  "p95_latency_seconds": 2.34,
  "by_difficulty": { ... },
  "by_provenance": { ... }
}
```

**`totals`** — การติดตามการใช้ token และค่าใช้จ่าย:

```json
{
  "prompt_tokens": 48200,
  "completion_tokens": 3100,
  "reasoning_tokens": 0,
  "cached_tokens": 12000,
  "total_cost_usd": 0.42,
  "cost_per_entry_usd": 0.0034,
  "reasoning_ratio": 0.0
}
```

---

## Writing-style and register metrics (เพื่อให้ข้อมูลเท่านั้น)

harness สามารถประเมินว่าการแปลตรงกับ **register** และ **รูปแบบการเขียน** เป้าหมายหรือไม่ ผ่าน metric plugin `WritingStyleConsistency` (`mt_eval_harness/plugins/writing_style.py`) การแปลอาจถูกต้องทางภาษาศาสตร์แต่ใช้ register ผิด — การใช้ภาษาไม่เป็นทางการในเอกสารทางกฎหมาย หรือภาษาทางการในสำเนาการตลาด — และ string metric จะไม่สังเกตเห็น แต่ metric เหล่านี้จะตรวจพบ

**สิ่งที่วัด (ต่อ entry):**

| Metric | Scale | ความหมาย |
|--------|-------|---------|
| `style_register_match` | boolean | output ตรงกับ register ที่คาดหวังหรือไม่? เป้าหมายมาจาก field `register` ของ corpus entry (ดู [Benchmark Spec §2.6](/docs/specifications/benchmark)) หรือจาก style profile |
| `style_sentence_length_ratio` | float | ความยาวประโยคเฉลี่ยที่คาดการณ์เทียบกับ reference (1.0 = ตรงกัน; ค่าที่เบี่ยงเบน = style drift) |
| `style_formality_score` | 0.0–1.0 | การมีอยู่ของตัวบ่งชี้ภาษาทางการ/ไม่เป็นทางการ (สรรพนาม T–V, คำย่อ, …) โดยใช้ทรัพยากรตัวบ่งชี้เฉพาะภาษา |

**ค่ารวม:** `style_consistency_rate` — สัดส่วนของ entry ที่ไม่พบ register mismatch

เปิดใช้งานเป้าหมายที่กำหนดเองด้วย `--style-profile path/to/profile.json` (เช่น brand-voice profile) หากไม่มี plugin จะใช้ metadata `register` ของแต่ละ corpus entry แทนเมื่อมีข้อมูล

:::caution ขอบเขตที่ชัดเจน
metric เหล่านี้ **เพื่อให้ข้อมูลเท่านั้น** — ไม่นับรวมใน composite score เลย และการตรวจจับ formality ใช้วิธีอิงตัวบ่งชี้ (heuristic) ไม่ใช่การตัดสินจากการเรียนรู้ ให้ถือว่าเป็นตัวตรวจจับการเบี่ยงเบนของ register ไม่ใช่คำตัดสินคุณภาพของ style
:::

---

## Fingerprint เทียบกับ Run Card Hash {#fingerprint-vs-run-card-hash}

harness สร้าง hash สองแบบที่แตกต่างกัน โดยมีวัตถุประสงค์ต่างกัน:

### Fingerprint

**fingerprint** ตอบคำถามว่า: *"การรันนี้สามารถทำซ้ำได้หรือไม่?"*

มันสร้าง hash จากการรวมกันของ input ที่กำหนดการกำหนดค่าการทดลอง — ไม่ใช่ output:

- Dataset SHA-256
- Model slug
- Condition label
- System prompt SHA-256
- Temperature
- Harness version

การรันสองครั้งที่มี fingerprint เหมือนกันใช้การตั้งค่าเดียวกัน ผลลัพธ์ควรเปรียบเทียบกันได้ (ยกเว้นความไม่แน่นอนของ API)

### Run Card Hash

**run card hash** ตอบคำถามว่า: *"ไฟล์ผลลัพธ์เฉพาะนี้ถูกแก้ไขหรือไม่?"*

มันคือ SHA-256 ของ run card JSON ทั้งหมด (ยกเว้น field `run_card_hash` เอง) หาก field ใดเปลี่ยนแปลง — คะแนน, timestamp, output เพียงรายการเดียว — hash จะเสีย

:::info ควรใช้แบบไหนเมื่อใด
ใช้ **fingerprint** เพื่อจัดกลุ่มการรันที่เปรียบเทียบกันได้ (การทดลองเดียวกัน, การรันต่างกัน) ใช้ **run card hash** เพื่อตรวจสอบความสมบูรณ์ของไฟล์ผลลัพธ์เฉพาะ
:::

---

## การเผยแพร่ไปยัง Leaderboard

หลังจากรันเสร็จสมบูรณ์ ใช้ `mt-eval publish` เพื่อส่ง run card:

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

หากไม่ได้ระบุ `--method-card` ระหว่างการรัน `mt-eval publish` จะเปิด interactive wizard (`method_card_wizard.py`) ที่จะแนะนำคุณในการอธิบาย method (ชื่อ, class, tool ที่ใช้ ฯลฯ) output ของ wizard จะถูกฝังใน run card ก่อนการส่ง

### การส่งด้วยตนเอง

run card จะถูกบันทึกเป็นไฟล์ JSON ใน output directory คุณยังสามารถส่ง run card ไฟล์ใดก็ได้ผ่าน leaderboard UI ที่ [/leaderboard](https://champollion.dev/leaderboard) หรือผ่าน API:

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning การตรวจสอบ Leaderboard
leaderboard จะตรวจสอบ run card ที่ส่งมากับ dataset registry การส่งที่อ้างอิง dataset ที่ไม่รู้จัก หรือมี `run_card_hash` ที่เสีย จะถูกปฏิเสธ
:::

:::danger ห้ามนำข้อมูลการประเมินไปฝึก model
หาก method ของคุณเคยเห็น evaluation dataset ระหว่างการพัฒนา — ไม่ว่าจะเป็นข้อมูลฝึก, ตัวอย่าง few-shot, รายการพจนานุกรม หรือวัสดุสำหรับ prompt engineering — การส่งของคุณจะถูก **ตัดสิทธิ์** ดู [MT Evaluation](/docs/leaderboard/rules) สำหรับสิ่งที่ทำให้ method ดีหรือไม่ดี
:::

---

## ดูเพิ่มเติม

- [MT Evaluation](/docs/leaderboard/rules) — ภาพรวม, คุณค่าของ leaderboard และแนวทาง method ที่ดีและไม่ดี
- [Evaluation Datasets](/docs/leaderboard/datasets) — รูปแบบ dataset, EDTeKLA, FLORES+
- [Run Card Specification](/docs/specifications/run-card) — JSON schema แบบเต็ม
- [Building a Method](/docs/specifications/methods) — method interface สำหรับการสร้าง method ที่ประเมินได้
- [Method Leaderboard](https://champollion.dev/leaderboard) — คะแนน benchmark แบบ live
- [Benchmark Specification](/docs/specifications/benchmark) — โปรโตคอลการประเมิน, รูปแบบคอร์ปัส, run card schema
- [Scoring Specification](/docs/specifications/scoring) — SSOT สำหรับ metric, น้ำหนัก composite และระดับคุณภาพ