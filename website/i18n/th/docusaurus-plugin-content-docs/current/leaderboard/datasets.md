---
sidebar_position: 3
title: "ชุดข้อมูลการประเมิน"
related:
  - label: "Corpus Design Framework"
    to: /docs/specifications/corpus-design
    kind: spec
    note: "How evaluation corpora are constructed"
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "Build a corpus for your language"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
---
# ชุดข้อมูลสำหรับการประเมิน

> **สรุปสำหรับผู้บริหาร** หน้านี้อธิบายชุดข้อมูลสำหรับการประเมินที่ใช้ในการทำ benchmarking รวมถึงโครงสร้าง schema ของรายการในคลังข้อมูล ระดับความยาก (1–5) และข้อกำหนดด้านที่มาของข้อมูล ชุดข้อมูลที่พร้อมใช้งานในปัจจุบัน: EDTeKLA Dev v1 (Plains Cree, รวม 548 รายการ: 486 จากตำราเรียน + 62 มาตรฐานทอง) และ FLORES+ Devtest (39 ภาษา, 1,012 รายการต่อภาษา)

ชุดข้อมูลคือเป้าหมายคงที่ที่ harness ใช้ในการประเมิน แต่ละชุดข้อมูลเป็นไฟล์ JSON ที่ประกอบด้วยคู่ข้อความต้นทาง→ปลายทางพร้อมการแปลอ้างอิงมาตรฐานทอง harness จะให้คะแนนผลลัพธ์ของโมเดลโดยเปรียบเทียบกับการอ้างอิงเหล่านี้ และจะไม่แก้ไขข้อมูลเหล่านั้นเด็ดขาด

:::danger ห้ามนำข้อมูลสำหรับการประเมินไปใช้ฝึกโมเดล

⚠️ **ชุดข้อมูลเหล่านี้มีไว้สำหรับการประเมินเท่านั้น** วิธีการที่ถูกฝึก fine-tuned few-shot-prompted หรือได้รับการเปิดเผยต่อข้อมูลสำหรับการประเมินในรูปแบบใดก็ตาม จะให้คะแนนที่สูงเกินจริงและจะ**ถูกตัดสิทธิ์จาก leaderboard**

ใช้คลังข้อมูลแยกต่างหากสำหรับการฝึก ชุดข้อมูลสำหรับการประเมินต้องไม่ถูกเปิดเผยต่อโมเดลของคุณในระหว่างการพัฒนา
:::

---

## รูปแบบชุดข้อมูล

ชุดข้อมูลทุกชุดใช้ JSON schema เดียวกัน:

```json
{
  "dataset": {
    "id": "dataset-slug",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "description": "Human-readable description of the dataset",
    "source_language": "en",
    "target_language": "crk",
    "created": "2025-05-01",
    "license": "CC-BY-NC-4.0",
    "provenance": ["gold_standard", "textbook"]
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "tânisi",
      "difficulty": 1,
      "provenance": "gold_standard",
      "register": "conversational",
      "context": "greeting",
      "notes": "Common greeting, SRO orthography"
    }
  ]
}
```

:::info Schema มาตรฐาน
[Benchmark Specification](/docs/specifications/benchmark) กำหนด schema มาตรฐานของคลังข้อมูลและรายการข้อมูล หน้านี้จัดทำเอกสารชุดข้อมูลที่มีอยู่และวิธีการสร้างชุดข้อมูลใหม่
:::

### บล็อก `dataset` ระดับบนสุด

| ฟิลด์ | ประเภท | คำอธิบาย |
|-------|------|-------------|
| `id` | `string` | ตัวระบุชุดข้อมูลที่ไม่ซ้ำกัน (ใช้ใน run card และ leaderboard) |
| `version` | `string` | Semantic version การเพิ่มค่านี้จะทำให้การเปรียบเทียบ run card ก่อนหน้าใช้ไม่ได้ |
| `language_pair` | `string` | ป้ายชื่อสำหรับแสดงผล (เช่น `EN→CRK`) |
| `description` | `string` | ไม่บังคับ สรุปที่มนุษย์อ่านได้ |
| `source_language` | `string` | รหัสภาษาต้นทาง BCP 47 |
| `target_language` | `string` | รหัสภาษาปลายทาง BCP 47 |
| `created` | `string` | วันที่สร้างในรูปแบบ ISO 8601 |
| `license` | `string` | ตัวระบุสัญญาอนุญาต SPDX |
| `provenance` | `string[]` | รายการแท็กที่มาของข้อมูลที่ใช้ในรายการต่าง ๆ |

### ฟิลด์ของรายการข้อมูล

| ฟิลด์ | ประเภท | จำเป็น | คำอธิบาย |
|-------|------|----------|-------------|
| `id` | `integer` | ✅ | ตัวระบุรายการที่ไม่ซ้ำกันภายในคลังข้อมูล |
| `source` | `string` | ✅ | ข้อความต้นทางที่ต้องการแปล |
| `reference` | `string` | ✅ | การแปลอ้างอิงมาตรฐานทอง |
| `difficulty` | `integer` | ✅ | ระดับความยาก 1–5 (ดูด้านล่าง) |
| `provenance` | `string` | ✅ | ที่มาของรายการนี้ (เช่น `gold_standard`, `textbook`, `elicited`) |
| `register` | `string` | ✅ | ระดับทะเบียนภาษา/ความเป็นทางการ (เช่น `conversational`, `formal`, `ceremonial`) |
| `context` | `string` | ✅ | หน้าที่ในการสื่อสาร (เช่น `greeting`, `declaration`, `instruction`) |
| `notes` | `string` | ❌ | บริบทเสริมสำหรับผู้ตรวจสอบที่เป็นมนุษย์ |
| `morphological_analysis` | `string` | ❌ | การวิเคราะห์ทางสัณฐานวิทยามาตรฐานทอง |
| `variant_class` | `string` | ❌ | ป้ายกำกับคลาสสำหรับจัดกลุ่มรูปแบบการแปลที่ยอมรับได้ |

---

## ชุดข้อมูลที่พร้อมใช้งาน

### EDTeKLA Development Set v1

ชุดข้อมูลสำหรับการประเมินชุดแรก สร้างขึ้นสำหรับการแปลภาษาอังกฤษ→Plains Cree (SRO) จัดทำโดย [กลุ่มวิจัย EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) แห่งมหาวิทยาลัย Alberta

| คุณสมบัติ | ค่า |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **เวอร์ชัน** | `1.0` |
| **คู่ภาษา** | EN → CRK (Plains Cree, อักขรวิธี SRO) |
| **จำนวนรายการ** | รวม 548 รายการ (486 จากตำราเรียน + 62 มาตรฐานทอง) คลังข้อมูล dev มาตรฐานคือ `textbook_dev.json` (436 รายการ — ชุด dev ของตำราเรียนทั้งหมดจาก 486 รายการ: 436 dev + 50 held-out test) |
| **การกระจายระดับความยาก** | ง่าย ปานกลาง ยาก |
| **ที่มาของข้อมูล** | `gold_standard` (ตรวจสอบโดยผู้พูดภาษา), `textbook` (สื่อการศึกษาที่ตีพิมพ์แล้ว) |
| **สัญญาอนุญาต** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |

**สิ่งที่ชุดข้อมูลนี้ทดสอบ:**

- คำทักทายพื้นฐานและวลีที่ใช้บ่อย
- ความมีชีวิตของคำนามและ obviation
- การผันกริยาตามบุคคลและกาล
- โครงสร้าง locative
- กระบวนทัศน์ possessive
- โครงสร้างประโยคซับซ้อน

:::tip โครงสร้างคลังข้อมูล
คอลเลกชัน EdTeKLA ทั้งหมดมี 548 รายการที่ผ่านการคัดสรร: 486 รายการจากคลังข้อมูลตำราเรียน (436 dev + 50 held-out) และ 62 รายการจากมาตรฐานทอง itwêwina คลังข้อมูล dev มาตรฐานคือ `textbook_dev.json` ซึ่งมี 436 รายการ — ชุด dev ของตำราเรียนทั้งหมด แต่ละรายการได้รับการตรวจสอบโดยผู้พูดภาษาที่คล่องแคล่ว หรือนำมาจากตำราเรียนภาษา Cree ที่ตีพิมพ์แล้ว ชุดข้อมูลขนาดเล็กที่มีคุณภาพสูงพร้อมมาตรฐานทองที่ผ่านการตรวจสอบมีประโยชน์มากกว่าชุดข้อมูลขนาดใหญ่ที่มีสัญญาณรบกวน โดยเฉพาะอย่างยิ่งสำหรับภาษาที่มีทรัพยากรน้อย ซึ่งการแปลที่ "ใกล้เคียงพอ" มักไม่ถูกต้องในเชิงสัณฐานวิทยา
:::

---

## การสร้างชุดข้อมูลใหม่

หากต้องการสร้างชุดข้อมูลสำหรับคู่ภาษาหรือโดเมนใหม่:

### 1. จัดโครงสร้าง JSON

ปฏิบัติตาม schema ใน [รูปแบบชุดข้อมูล](#dataset-format) แต่ละรายการต้องมี `source`, `reference`, `difficulty`, `provenance`, `register` และ `context`

### 2. กำหนด ID ที่ไม่ซ้ำกัน

ใช้ slug ที่สื่อความหมาย: `{project}-{split}-v{version}` (เช่น `edtekla-dev-v1`, `quechua-test-v1`)

### 3. ตรวจสอบมาตรฐานทอง

ค่า `reference` ทุกค่าต้องได้รับการตรวจสอบโดยผู้พูดภาษาที่คล่องแคล่ว หรือนำมาจากแหล่งที่ตีพิมพ์และผ่านการทบทวนโดยผู้เชี่ยวชาญ การอ้างอิงที่สร้างโดยเครื่องจะทำให้วัตถุประสงค์ของการประเมินสูญเสียความหมาย

### 4. กำหนดระดับความยาก

กำหนดระดับความยากเป็นจำนวนเต็มให้แต่ละรายการ:

| ระดับ | คำอธิบาย | ตัวอย่าง |
|------|-------------|----------|
| 1 — คำศัพท์พื้นฐาน | คำเดี่ยว คำทักทายทั่วไป ตัวเลข | "hello" → "tânisi" |
| 2 — ประโยคง่าย | ประธาน-กริยา หรือ SVO กาลปัจจุบัน | "I see the dog" |
| 3 — ความซับซ้อนปานกลาง | กาลอดีต/อนาคต possessive animacy | "I saw his dog yesterday" |
| 4 — สัณฐานวิทยาซับซ้อน | Obviation passive voice conjunct order | "the woman whose son went to the store" |
| 5 — ขั้นสูง | หลายอนุประโยค ทะเบียนภาษาทางการ พิธีกรรม สำนวน | ย่อหน้าเต็มที่มีน้ำเสียงเหมาะสมกับทะเบียนภาษา |

### 5. ติดแท็กที่มาของข้อมูล

แต่ละรายการควรระบุแหล่งที่มา แท็กที่ใช้บ่อย:

- `gold_standard` — ตรวจสอบโดยผู้พูดภาษาที่คล่องแคล่ว
- `textbook` — นำมาจากสื่อการศึกษาที่ตีพิมพ์แล้ว
- `elicited` — ผลิตผ่านการสัมภาษณ์เชิงโครงสร้าง
- `corpus` — สกัดจากคลังข้อมูลคู่ขนาน

### 6. ตรวจสอบความถูกต้องของไฟล์

รัน harness กับชุดข้อมูลของคุณด้วยโมเดลใดก็ได้ เพื่อตรวจสอบว่า JSON มีรูปแบบถูกต้องและฟิลด์ที่จำเป็นทั้งหมดมีอยู่ครบถ้วน:

```bash
python eval/baseline_experiment.py --dataset path/to/your-dataset.json
```

harness จะแสดงข้อผิดพลาดหากพบฟิลด์ที่ขาดหายไป ดัชนีซ้ำกัน หรือการละเมิด schema

### 7. ส่งเพื่อรวมเข้าในระบบ

เปิด pull request ไปยัง [eval harness repository](https://github.com/gamedaysuits/arena) พร้อมไฟล์ชุดข้อมูลของคุณในไดเรกทอรี `data/` พร้อมแนบเอกสารระบุวิธีการตรวจสอบและแหล่งที่มาของข้อมูล

---

## FLORES+ Devtest

benchmark หลายภาษาที่ครอบคลุมกว้าง ดูแลโดย [Open Language Data Initiative (OLDI)](https://huggingface.co/datasets/openlanguagedata/flores_plus) ใช้สำหรับ frontier benchmark หลายโมเดลของ champollion

| คุณสมบัติ | ค่า |
|----------|-------|
| **ID** | `flores-plus-devtest` |
| **คู่ภาษา** | EN → 39 ภาษา (ภาษาธรรมชาติที่ลงทะเบียนใน champollion ทั้งหมด) |
| **จำนวนรายการ** | 1,012 ประโยคต่อภาษา |
| **สัญญาอนุญาต** | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| **แหล่งที่มา** | เดิมคือ Meta FLORES-200 ปัจจุบันดูแลโดย OLDI |
| **ที่เก็บข้อมูล** | fixtures ที่สกัดไว้ล่วงหน้าที่ `test/benchmark/fixtures/` ใน champollion repo หลัก |

:::danger สำหรับการประเมินเท่านั้น
FLORES+ มีไว้สำหรับการประเมินเท่านั้น ผู้ดูแลระบบขอร้องอย่างชัดเจนว่า**ห้ามนำไปใช้เป็นข้อมูลฝึก** ตรวจสอบให้แน่ใจว่าเนื้อหาของ FLORES+ ถูกยกเว้นออกจากคลังข้อมูลฝึกทั้งหมด
:::

---

## ดูเพิ่มเติม

- [MT Evaluation](/docs/leaderboard/rules) — ภาพรวมของกรอบการประเมินและ leaderboard
- [Eval Harness](/docs/specifications/harness) — วิธีการรันการประเมินกับชุดข้อมูลเหล่านี้
- [Run Card Specification](/docs/specifications/run-card) — JSON schema สำหรับบันทึกผลลัพธ์
- [Method Leaderboard](https://champollion.dev/leaderboard) — คะแนน benchmark แบบเรียลไทม์
- [EdTeKLA Project](https://spaces.facsci.ualberta.ca/edtekla/) — กลุ่มวิจัยมหาวิทยาลัย Alberta ผู้อยู่เบื้องหลังชุดข้อมูลภาษา Cree