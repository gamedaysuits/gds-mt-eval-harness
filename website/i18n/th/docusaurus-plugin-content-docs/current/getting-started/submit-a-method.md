---
sidebar_position: 1
title: "ส่งวิธีการ"
related:
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
    note: "The contract your method implements"
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
    note: "What every published run must disclose"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
    note: "The fastest first method to submit"
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
---
# ส่งวิธีการแปล

> **สรุปสำหรับผู้บริหาร** คู่มือเริ่มต้นแบบทีละขั้นตอนสำหรับการส่งผลการทดสอบ benchmark ครั้งแรกของคุณไปยัง leaderboard โคลน harness รันกับชุดข้อมูล ตรวจสอบ run card ของคุณ แล้วส่ง ใช้เวลาเพียง 10 นาทีหากคุณมี API key

คู่มือนี้จะแนะนำคุณตลอดกระบวนการส่งผลการทดสอบ benchmark ครั้งแรกไปยัง leaderboard ของ MT Eval Arena

---

## ข้อกำหนดเบื้องต้น

- **Python 3.10+**
- **OpenRouter API key** (หรือเทียบเท่าสำหรับผู้ให้บริการโมเดลของคุณ)
- **วิธีการแปล** — สิ่งใดก็ตามที่สร้างคำแปลจากข้อความต้นฉบับ

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## ขั้นตอนที่ 1: รัน Harness

Harness จะให้คะแนนวิธีการของคุณเทียบกับชุดข้อมูลมาตรฐาน:

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| Flag | หน้าที่ |
|---|---|
| `--corpus` | พาธไปยัง evaluation corpus (`.json`, `.jsonl`, `.tsv`) |
| `--model` | Model slug — ชื่อย่อ (เช่น `gemini-pro`) หรือ OpenRouter ID แบบเต็ม |
| `--condition` | ชื่อสำหรับวิธีการของคุณ (แสดงบน leaderboard) |
| `--temperature` | Sampling temperature (ค่าต่ำ = ผลลัพธ์แน่นอนกว่า) |
| `--fst-retries` | ตัวเลือกเสริม: จำนวนครั้งที่ลองใหม่สำหรับ FST |
| `--submit` | ส่ง run card ไปยัง leaderboard โดยอัตโนมัติ |

Harness จะสร้าง **run card** — ไฟล์ JSON แบบ self-contained ที่บรรจุคะแนน, hash ของชุดข้อมูล, model slug และลายนิ้วมือเข้ารหัสที่ผูกผลลัพธ์กับการกำหนดค่าการทดลองที่แน่นอน

---

## ขั้นตอนที่ 2: ตรวจสอบ Run Card ของคุณ

Run card จะถูกบันทึกไว้ที่ `results/` ตรวจสอบก่อนส่ง:

```bash
cat results/your-run-card.json | python -m json.tool
```

ฟิลด์สำคัญที่ต้องตรวจสอบ:
- `scores.chrf_plus_plus` — เมตริกคุณภาพหลักของคุณ
- `scores.exact_match_rate` — สัดส่วนของคำแปลที่สมบูรณ์แบบ
- `scores.fst_acceptance_rate` — ความถูกต้องทางสัณฐานวิทยา (หากใช้ FST)
- `totals.total_cost_usd` — ค่าใช้จ่ายของการรัน
- `fingerprint` — hash สำหรับการทำซ้ำการทดลอง

ดู [ข้อกำหนด Run Card](/docs/specifications/run-card) สำหรับ schema ฉบับสมบูรณ์

---

## ขั้นตอนที่ 3: ส่ง

### การส่งอัตโนมัติ

หากคุณระบุ `--submit` ขณะรัน harness run card ของคุณถูกอัปโหลดไปแล้ว

### การส่งด้วยตนเอง

ส่ง run card ใดก็ได้ผ่าน API:

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

หรืออัปโหลดผ่าน [Leaderboard UI](https://champollion.dev/leaderboard)

---

## ขั้นตอนถัดไป

1. การส่งของคุณจะถูกตรวจสอบความถูกต้อง (dataset hash, ความสมบูรณ์ของ run card)
2. ผลลัพธ์จะปรากฏบน leaderboard ในสถานะ **Self-benchmarked** (ระดับความน่าเชื่อถือ 1)
3. เพื่อรับสถานะ **GDS Verified** ให้ส่งวิธีการของคุณในรูปแบบ installable plugin เพื่อให้ผู้ดูแลระบบสามารถทำซ้ำผลลัพธ์ของคุณได้
4. สำหรับวิธีการที่ใช้กับภาษาพื้นเมือง: หากวิธีการของคุณขึ้นสู่อันดับสูงสุด กระบวนการ [โอนกรรมสิทธิ์](/docs/sovereignty/ownership-transfer) จะเริ่มต้นขึ้น

---

## ดูเพิ่มเติม

- [การใช้งาน Harness](/docs/specifications/harness) — เอกสารอ้างอิง CLI ฉบับสมบูรณ์
- [กฎของ Leaderboard](/docs/leaderboard/rules) — เกณฑ์การส่งและนโยบายป้องกันการโกง
- [การสร้างวิธีการแปล](/docs/specifications/methods) — โปรโตคอล TranslationMethod
- [ชุดข้อมูล](/docs/leaderboard/datasets) — ชุดข้อมูลสำหรับการประเมินที่มีให้ใช้งาน