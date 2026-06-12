---
sidebar_position: 4
title: "อินเทอร์เฟซวิธีการ"
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
# อินเทอร์เฟซเมธอดร่วม

> **สรุปสำหรับผู้บริหาร** หน้านี้ระบุโปรโตคอล `TranslationMethod` ที่เมธอดทุกตัวใน Arena ต้องนำไปใช้งาน คลาสเมธอดทั้งหก (`raw-llm`, `coached-llm`, `pipeline`, `custom-plugin`, `api`, `human`) รูปแบบปลั๊กอินเมธอด และ **คลาสการพึ่งพา** (S/O/A1/A2/X) ที่กำหนดว่าเมธอดสามารถทำงานในแซนด์บ็อกซ์การประเมินผลและมีสิทธิ์รับรางวัลได้หรือไม่ แนวทางใดก็ตามที่นำโปรโตคอลนี้ไปใช้งานสามารถเข้ารับการเปรียบเทียบประสิทธิภาพได้ โดยสิ่งที่เมธอดนั้นพึ่งพาจะเป็นตัวกำหนดว่าสามารถแข่งขันในส่วนใดได้บ้าง

eval harness และ champollion ใช้แนวคิดร่วมกันเกี่ยวกับ **เมธอดการแปล** เมธอดคือกระบวนการใดก็ตามที่รับข้อความต้นฉบับและสร้างข้อความที่แปลแล้ว ไม่ว่าจะเป็นการเรียก LLM โดยตรง ไปป์ไลน์หลายขั้นตอน API ของบุคคลที่สาม หรือนักแปลมนุษย์

## สถาปัตยกรรม

```
Method Plugin (v2 Spec)
├── method.json           ← Manifest (name, class, entry_point, dependencies, metadata)
├── method_card.json      ← Leaderboard description (what, not how)
├── pipeline.py           ← Python module implementing TranslationMethod
└── (optional helpers)    ← Additional Python modules
```

โหลดผ่าน `--method path/to/dir` โดย harness ไม่ค้นหาสิ่งใดโดยอัตโนมัติ

## สองระบบ หนึ่งอินเทอร์เฟซ

| | Eval Harness | champollion |
|---|---|---|
| **ภาษา** | Python | Node.js |
| **จุดเข้าใช้งาน** | `translate.py` | `translate.js` |
| **อินเทอร์เฟซ** | โปรโตคอล `TranslationMethod` | คอนฟิก `methodPlugin` |
| **วัตถุประสงค์** | การประเมินแบบกลุ่มพร้อมการให้คะแนน | การแปลไฟล์ locale แบบสดในสภาพแวดล้อม dev/CI |
| **ผลลัพธ์** | Run card พร้อมเมตริก | ไฟล์ locale ที่แปลแล้ว |

เมธอดที่รองรับทั้งสองระบบจะมีจุดเข้าใช้งานสองจุด — หนึ่งจุดสำหรับแต่ละ language runtime **Method card** คือสะพานเชื่อม: อธิบายเมธอดในรูปแบบที่ทั้งสองระบบเข้าใจได้

## Method Card {#method-card}

Method card อธิบาย *ว่า* เมธอดการแปลคืออะไร โดยไม่เปิดเผยรายละเอียดที่เป็นกรรมสิทธิ์ เช่น system prompt ฉบับเต็ม โดยตอบคำถามต่อไปนี้:

- เมธอดนี้อยู่ในคลาสใด? (raw LLM, coached LLM, pipeline, API ฯลฯ)
- ใช้เครื่องมือใดบ้าง? (FST analyzer, dictionary ฯลฯ)
- การนำไปใช้งานเป็น open source หรือไม่?
- รองรับคู่ภาษาใดบ้าง?

ดู [Method Card Spec](/docs/specifications/methods#method-card) สำหรับ JSON schema ฉบับสมบูรณ์

### ตัวอย่าง

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

ฟิลด์ `dependency_class` สรุปสิ่งที่เมธอดต้องการเพื่อทำงานและถ่ายโอน — ดู [ความถูกต้องของเมธอดและคลาสการพึ่งพา](#method-validity-and-dependency-classes) ด้านล่าง

### คลาสเมธอด

| คลาส | คำอธิบาย |
|-------|-------------|
| `raw-llm` | การเรียก LLM โดยตรงพร้อมคำสั่งขั้นต่ำ |
| `coached-llm` | LLM พร้อม prompt ที่มีโครงสร้าง ตัวอย่าง และข้อจำกัด |
| `pipeline` | ไปป์ไลน์หลายขั้นตอนพร้อมส่วนประกอบแบบ deterministic |
| `custom-plugin` | กระบวนการภายนอกที่นำโปรโตคอล `TranslationMethod` ไปใช้งาน |
| `api` | API การแปลของบุคคลที่สาม (Google Translate, DeepL ฯลฯ) |
| `human` | การแปลโดยมนุษย์ (สำหรับการกำหนด baseline) |

## ความถูกต้องของเมธอดและคลาสการพึ่งพา {#method-validity-and-dependency-classes}

เมธอดสามารถทำงานได้และถ่ายโอนได้เพียงเท่าที่การพึ่งพาที่มีความพร้อมใช้งานน้อยที่สุดจะอนุญาต กลไกสองอย่างของ Arena ขึ้นอยู่กับการทราบอย่างชัดเจนว่าเมธอดต้องการอะไร:

1. **การประเมินในแซนด์บ็อกซ์** ([Benchmark Specification §8.2](/docs/specifications/benchmark)) — คะแนนมาตรฐานทองคำอย่างเป็นทางการมาจากแซนด์บ็อกซ์ที่มีนโยบายเครือข่ายแบบ **default-deny** เมธอดที่ต้องการบริการภายนอกโดยไม่ประกาศไม่สามารถสร้างคะแนนอย่างเป็นทางการได้
2. **การถ่ายโอนรางวัล** ([Prize Specification](/docs/specifications/prizes)) — เมธอดที่ชนะรางวัลจะถ่ายโอนไปยังองค์กรกำกับดูแลของชุมชนภาษา เมธอดที่รวมเนื้อหาที่ผู้ส่งไม่มีสิทธิ์รวมไว้ไม่สามารถถ่ายโอนได้โดยชอบด้วยกฎหมาย ผู้ส่งต้องถือ (หรือได้รับ) สิทธิ์ในทุกสิ่งที่อยู่ในแพ็กเกจ

เพื่อให้การตรวจสอบทั้งสองอย่างเป็นกระบวนการเชิงกลไกแทนที่จะเป็นแบบเฉพาะกิจ เมธอดทุกตัวต้องประกาศ **คลาสการพึ่งพา** ซึ่งได้มาจาก **dependency manifest** ใน `method.json`

> **หมายเหตุเกี่ยวกับการตั้งชื่อ** *คลาสเมธอด* (§ข้างต้น: `raw-llm`, `pipeline`, …) อธิบาย *วิธีที่เมธอดแปล* *คลาสการพึ่งพา* (ส่วนนี้) อธิบาย *สิ่งที่เมธอดต้องการเพื่อทำงานและถ่ายโอน* ทั้งสองเป็นแกนที่เป็นอิสระต่อกัน: เมธอด `pipeline` สามารถอยู่ในคลาสการพึ่งพาใดก็ได้

### คลาสการพึ่งพาทั้งห้า

| คลาส | ชื่อ | คำนิยาม | ทำงานในแซนด์บ็อกซ์ได้? | มีสิทธิ์รับรางวัล? |
|-------|------|-----------|-------------------|-----------------|
| **S** | Self-contained | โค้ด ข้อมูล โมเดล และน้ำหนักทั้งหมดอยู่ในไดเรกทอรีเมธอด ภายใต้ใบอนุญาตที่อนุญาตให้เผยแพร่ซ้ำและถ่ายโอนให้ชุมชนได้ | ✅ ใช่ ใช้ได้ทันที | ✅ ใช่ |
| **O** | Open external | พึ่งพา artifact ที่โฮสต์ภายนอกภายใต้ใบอนุญาตเปิดที่อนุญาตให้เผยแพร่ซ้ำได้ (รวมถึงใบอนุญาต copyleft เช่น AGPL) — เช่น FST ที่ดาวน์โหลดในขณะติดตั้ง | ✅ ใช่ — artifact ถูกปักหมุดและ **นำเข้าในการส่ง** | ✅ ใช่ พร้อมเงื่อนไขความเข้ากันได้ของใบอนุญาต: เงื่อนไข copyleft ยังคงอยู่ผ่านการถ่ายโอน และชุมชนได้รับสิทธิ์เดียวกับที่ใบอนุญาตมอบให้ทุกคน |
| **A1** | API-dependent, substitutable | ต้องการการอนุมาน LLM ในขณะรันไทม์ โดยโมเดลเป็น **การกำหนดค่าที่แทนที่ได้** — โมเดลที่มีความสามารถเพียงพอใดก็ตามสามารถใส่แทนได้ คุณค่าของเมธอดอยู่ที่ prompt ข้อมูลการฝึก และโค้ด ไม่ใช่โมเดลของผู้ให้บริการรายใดรายหนึ่ง | ⚠️ เฉพาะผ่าน **LLM gateway** ที่ข้อกำหนดแซนด์บ็อกซ์กำหนด (🔲 วางแผนไว้ — ดูด้านล่าง) | ⚠️ มีเงื่อนไข — ดูด้านล่าง |
| **A2** | API-dependent, non-substitutable | ต้องการการเรียก API ข้อมูลหรือบริการภายนอกในขณะรันไทม์ที่ไม่สามารถนำเข้าหรือแทนที่ได้ — โดยทั่วไปเพราะเนื้อหาที่ให้บริการเป็นกรรมสิทธิ์หรือไม่มีใบอนุญาต (เช่น dictionary API ที่พจนานุกรมพื้นฐานไม่มีใบอนุญาตสาธารณะ) | ❌ ไม่ — การพึ่งพาไม่สามารถมีอยู่ในแซนด์บ็อกซ์โดยไม่ได้รับอนุญาตจากเจ้าของสิทธิ์ | ❌ ไม่ จนกว่าเจ้าของสิทธิ์จะให้สิทธิ์การรวมในแซนด์บ็อกซ์ **และ** สิทธิ์การถ่ายโอน อนุญาตให้แสดงบน leaderboard แบบเปิด (ส่วนการพัฒนา) พร้อมแฟล็ก **"external dependency"** ที่มองเห็นได้ |
| **X** | Closed | รวมเนื้อหาที่ผู้ส่งไม่มีสิทธิ์เผยแพร่ซ้ำ — ชุดข้อมูลที่ไม่มีใบอนุญาต เนื้อหาที่ดึงมาโดยไม่ได้รับอนุญาต ส่วนประกอบที่ใบอนุญาตไม่เข้ากัน | ❌ | ❌ ไม่ได้รับอนุญาตในทุกเลน การรวมเนื้อหาโดยไม่มีสิทธิ์ถือเป็นการละเมิดใบอนุญาตโดยไม่คำนึงว่าเมธอดทำงานที่ใด |

**คลาสที่มีผล** คลาสการพึ่งพาของเมธอดคือคลาสที่ *จำกัดที่สุด* ในบรรดาการพึ่งพาที่ประกาศทั้งหมด ตามลำดับ S < O < A1 < A2 < X พจนานุกรมที่ไม่มีใบอนุญาตเพียงรายการเดียวทำให้ไปป์ไลน์ที่ self-contained กลายเป็นคลาส A2 (หากเข้าถึงในขณะรันไทม์) หรือคลาส X (หากรวมไว้โดยไม่มีสิทธิ์)

### ความแตกต่าง A1/A2: ความสามารถในการแทนที่

เมธอดส่วนใหญ่เรียก LLM Arena ไม่ได้แกล้งทำเป็นว่าไม่เป็นเช่นนั้น — แต่แยกแยะการพึ่งพา API สองประเภทที่แตกต่างกันมาก:

- **A1 (แทนที่ได้):** API ให้บริการการอนุมาน LLM แบบ commodity ตัวระบุโมเดลเป็นการกำหนดค่า: เมธอดต้องทำงานได้ตั้งแต่ต้นจนจบกับ inference endpoint ที่เข้ากันได้ใดก็ตาม รวมถึงโมเดลน้ำหนักเปิดที่โฮสต์โดยชุมชน คุณภาพผลลัพธ์อาจแตกต่างกันตามโมเดล — นั่นคือความเสี่ยงของนักพัฒนา และคะแนนอย่างเป็นทางการผูกกับโมเดลที่ปักหมุดที่ใช้ในการประเมิน เมธอดที่พึ่งพา **สถานะฝั่งผู้ให้บริการ** (fine-tune ที่โฮสต์เฉพาะที่ผู้ให้บริการ file store ของผู้ให้บริการ assistant เฉพาะผู้ให้บริการ) *ไม่สามารถแทนที่ได้*: สถานะนั้นไม่สามารถสลับออกได้ ดังนั้นการพึ่งพาจึงเป็น A2 เว้นแต่น้ำหนักหรือข้อมูลพื้นฐานจะรวมอยู่ในการส่ง
- **A2 (แทนที่ไม่ได้):** API ให้บริการสิ่งที่ไม่ซ้ำกัน — โดยทั่วไปเป็นข้อมูลที่เป็นกรรมสิทธิ์หรือไม่มีใบอนุญาต ไม่มี endpoint ทางเลือกใดที่สามารถให้บริการได้ และเนื้อหาไม่สามารถนำเข้าในแซนด์บ็อกซ์โดยไม่ได้รับอนุญาตจากเจ้าของสิทธิ์ เมธอดทำงานบน leaderboard แบบเปิด (พร้อมแฟล็ก) แต่ไม่สามารถสร้างคะแนนแซนด์บ็อกซ์อย่างเป็นทางการหรือมีสิทธิ์รับรางวัลได้จนกว่าจะมีสิทธิ์ที่จำเป็น

**สิ่งที่การถ่ายโอนรางวัล A1 ส่งมอบจริงๆ** ชุมชนไม่ได้รับโมเดล — ไม่มีใครสามารถถ่ายโอนน้ำหนักของ Anthropic, Google หรือ OpenAI ได้ การถ่ายโอนครอบคลุมสูตรที่สมบูรณ์ *รอบๆ* โมเดล: prompt ทั้งหมด ข้อมูลการฝึก โค้ดไปป์ไลน์ logic การลองใหม่ การกำหนดค่า และข้อกำหนดโมเดลที่บันทึกไว้ เนื่องจากโมเดลสามารถแทนที่ได้โดยการออกแบบ ชุมชนจึงสามารถชี้เมธอดที่ถ่ายโอนแล้วไปยังผู้ให้บริการใดก็ได้ที่ต้องการ — หรือโมเดลน้ำหนักเปิดบนฮาร์ดแวร์ของตนเอง — โดยไม่ต้องมีส่วนร่วมของนักพัฒนา สูตรเป็นสิ่งที่เป็นเจ้าของ เครื่องยนต์เป็นสิ่งที่เช่าและแทนที่ได้

### Dependency Manifest (`method.json`)

เมธอดทุกตัวประกาศการพึ่งพาใน manifest `method.json` แต่ละรายการบันทึกว่า artifact คืออะไร มาจากไหน ใบอนุญาตใดครอบคลุม และเมธอดเข้าถึงอย่างไร:

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

| ฟิลด์ | จำเป็น | คำอธิบาย |
|-------|----------|-------------|
| `id` | ✅ | ตัวระบุที่เสถียรสำหรับการพึ่งพา |
| `kind` | ✅ | `data`, `model`, `software` หรือ `service` |
| `license` | ✅ | ตัวระบุ SPDX, `proprietary` หรือ `none` `none` หมายความว่าไม่มีใบอนุญาตสาธารณะ — ถือว่าสงวนสิทธิ์ทั้งหมด |
| `access` | ✅ | `bundled` (อยู่ในไดเรกทอรีเมธอด), `mirrored` (ดึงมาในขณะติดตั้ง ปักหมุด นำเข้าในการส่ง), `gateway` (การอนุมาน LLM ในขณะรันไทม์ผ่าน evaluation gateway), `external-api` (การเรียกเครือข่ายในขณะรันไทม์อื่นๆ) |
| `source` | ✅ | URL ที่เป็นมาตรฐานหรือตัวระบุ `provider:slug` |
| `pin` | สำหรับ `mirrored` | เวอร์ชัน commit หรือ content hash ที่ปักหมุด artifact ที่แน่นอน |
| `substitutable` | สำหรับ `gateway`/`external-api` | endpoint ที่เข้ากันได้ใดก็ตามสามารถให้บริการการพึ่งพานี้ได้หรือไม่ |
| `redistributable` | ✅ | ใบอนุญาตอนุญาตให้เผยแพร่ artifact ซ้ำได้หรือไม่ |
| `transferable` | ✅ | artifact (หรือสิทธิ์ในนั้น) สามารถส่งต่อให้ชุมชนภายใต้เงื่อนไขการถ่ายโอนรางวัลได้หรือไม่ |
| `notes` | ❌ | บริบทในรูปแบบอิสระ |

**การได้มาซึ่งคลาส** การพึ่งพาแต่ละรายการมีส่วนร่วมในคลาส โดย `dependency_class` ของเมธอดคือที่จำกัดที่สุด:

| โปรไฟล์การพึ่งพา | มีส่วนร่วม |
|--------------------|-------------|
| `bundled` + ใบอนุญาตอนุญาตให้เผยแพร่ซ้ำและถ่ายโอน | S |
| `mirrored` + ใบอนุญาตเปิดที่อนุญาตให้เผยแพร่ซ้ำ (รวม copyleft) | O |
| `gateway` + `substitutable: true` (การอนุมาน LLM) | A1 |
| `external-api` หรือ `gateway` พร้อม `substitutable: false` | A2 |
| `bundled` + `license: none` หรือใบอนุญาตที่ไม่เข้ากันกับการเผยแพร่ซ้ำ | X |

`dependency_class` ที่ประกาศต้องตรงกับคลาสที่ harness ได้มาจาก manifest ความไม่ตรงกันถือเป็นข้อผิดพลาดในการตรวจสอบ

เมธอดที่ **ไม่มี** การพึ่งพาภายนอกประกาศ `"dependency_class": "S"` และ `"dependencies": []` อาร์เรย์ว่างเปล่าเป็นคำแถลงเชิงยืนยัน ซึ่งได้รับการตรวจสอบเช่นเดียวกับรายการอื่นๆ

### วิธีการตรวจสอบความถูกต้อง

สามชั้น จากถูกที่สุดไปยังมีอำนาจมากที่สุด:

1. **การตรวจสอบ manifest** harness ได้มาซึ่งคลาสที่มีผลจาก manifest และปฏิเสธความไม่ตรงกัน ผู้ตรวจสอบตรวจสอบการพึ่งพาที่ประกาศแต่ละรายการกับใบอนุญาตและแหล่งที่มาที่ระบุ — การพึ่งพาที่ประกาศว่า `redistributable: true` แต่ใบอนุญาต upstream ระบุเป็นอย่างอื่นจะไม่ผ่านการตรวจสอบ
2. **การวิเคราะห์แบบ static** โค้ดที่ส่งมาจะถูกสแกนหาการเรียกเครือข่าย การดาวน์โหลดแบบ dynamic และการเข้าถึงระบบไฟล์ที่ manifest ไม่ได้ระบุ การพึ่งพา *ที่ไม่ได้ประกาศ* ที่พบในการตรวจสอบเป็นเหตุให้ปฏิเสธโดยไม่คำนึงว่าจะอยู่ในคลาสใด — manifest ต้องสมบูรณ์ ไม่ใช่แค่ถูกต้อง
3. **นโยบายเครือข่ายแซนด์บ็อกซ์** ข้อกำหนดแซนด์บ็อกซ์กำหนดให้ **egress แบบ default-deny**: container ของเมธอดไม่มีการเข้าถึงเครือข่ายเว้นแต่จะมีการอนุญาต path อย่างชัดเจน path egress เดียวที่ข้อกำหนดกำหนดคือ **LLM gateway** — proxy การอนุมานที่ดำเนินการโดยโครงสร้างพื้นฐานการประเมิน จำกัดเฉพาะรายการที่อนุญาตของโมเดลที่ปักหมุดอย่างชัดเจน โดยทุกคำขอและการตอบสนองถูกบันทึกสำหรับการตรวจสอบหลังการรัน สิ่งใดที่ไม่อยู่ในรายการที่อนุญาตจะล้มเหลวที่ชั้นเครือข่าย ไม่ใช่ชั้นนโยบาย ดู [Benchmark Specification §8.6](/docs/specifications/benchmark) สำหรับนโยบายเครือข่ายและการออกแบบ gateway

> 🔲 **วางแผนไว้** แซนด์บ็อกซ์และ LLM gateway ถูกระบุไว้แล้วแต่ยังไม่ได้สร้าง จนกว่า gateway จะพร้อมใช้งาน เฉพาะเมธอดคลาส S และคลาส O เท่านั้นที่สามารถประเมินในแซนด์บ็อกซ์ได้ เมธอดคลาส A1 มีสิทธิ์รับรางวัล *ในหลักการ* แต่ยังไม่สามารถสร้างคะแนนมาตรฐานทองคำอย่างเป็นทางการได้ หน้านี้อธิบายสิ่งที่ข้อกำหนดกำหนด ไม่ใช่สิ่งที่ทำงานอยู่ในปัจจุบัน

### การแสดงผลบน Leaderboard

- leaderboard แสดงคลาสการพึ่งพาของแต่ละเมธอดควบคู่กับ badge คลาสเมธอด
- เมธอดคลาส A2 บน leaderboard แบบเปิดมีแฟล็ก **"external dependency"** ที่มองเห็นได้: คะแนนของพวกเขาขึ้นอยู่กับบริการของบุคคลที่สามที่อาจเปลี่ยนแปลงหรือหายไป และปัจจุบันไม่มีสิทธิ์รับรางวัล
- เมธอดคลาส X ไม่ถูกแสดงรายการ

## Eval Harness: TranslationMethod Protocol {#eval-harness-translationmethod-protocol}

eval harness ใช้ structural typing ของ Python (`Protocol`) สำหรับปลั๊กอิน คลาสใดก็ตามที่มี method signature ที่ถูกต้องจะทำงานได้ — ไม่จำเป็นต้องสืบทอด:

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

ดู [Plugin Protocol](/docs/specifications/methods#eval-harness-translationmethod-protocol) สำหรับเอกสารฉบับสมบูรณ์รวมถึงตัวอย่าง wrapper สำหรับเมธอดที่ไม่ใช่ Python

## champollion: methodPlugin Config

ใน champollion เมธอดถูกลงทะเบียนต่อคู่ภาษาใน `champollion.config.json`:

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

ดู [Plugin Spec](https://champollion.dev/docs/reference/plugin-spec) สำหรับอินเทอร์เฟซฝั่ง champollion

## การรวมกับ Leaderboard

เมื่อ method card ถูกแนบกับการรัน (ผ่าน `--method-card`) จะถูกฝังใน run card และแสดงบน leaderboard:

```bash
# Run with method card attached
mt-eval run \
  --method path/to/my-method \
  --corpus data/edtekla-dev-v1.json \
  --method-card method_card.json

# Publish to the leaderboard
mt-eval publish eval/logs/harness/your-run-card.json
```

หากไม่ได้ระบุ `--method-card` `mt-eval publish` จะเปิด wizard แบบโต้ตอบที่แนะนำคุณผ่านการอธิบายเมธอดของคุณ

leaderboard แสดง:
- **Class badge** — ตัวบ่งชี้ภาพ (เช่น "pipeline", "coached-llm")
- **คลาสการพึ่งพา** — S/O/A1/A2 (ดู [ความถูกต้องของเมธอดและคลาสการพึ่งพา](#method-validity-and-dependency-classes)); เมธอด A2 มีแฟล็ก "external dependency"
- **ชื่อเมธอด** — จาก method card
- **เครื่องมือที่ใช้** — แสดงรายการจาก method card
- **ตัวบ่งชี้ open source**

เมื่อไม่มี method card แนบ leaderboard จะแสดงการกำหนดค่าที่เป็น native ของ harness (โมเดล เวอร์ชัน prompt อุณหภูมิ เครื่องมือที่เปิดใช้งาน)

:::danger ห้ามฝึกโมเดลด้วยข้อมูลการประเมิน
เมธอดที่กระบวนการพัฒนารวมถึงการสัมผัสกับชุดข้อมูลการประเมิน — เป็นข้อมูลการฝึก ตัวอย่าง few-shot รายการพจนานุกรม หรือวัสดุการปรับ prompt — จะถูก **ตัดสิทธิ์** จาก leaderboard ดู [MT Evaluation](/docs/leaderboard/rules) สำหรับสิ่งที่แยกแยะเมธอดที่ดีออกจากเมธอดที่ไม่ดี
:::

---

## ดูเพิ่มเติม

- [MT Evaluation](/docs/leaderboard/rules) — ภาพรวม คุณค่าของ leaderboard และแนวทางเมธอดที่ดี/ไม่ดี
- [Eval Harness](/docs/specifications/harness) — วิธีการรันการประเมิน
- [Evaluation Datasets](/docs/leaderboard/datasets) — ชุดข้อมูลที่มีอยู่ (EDTeKLA, FLORES+)
- [Run Card Specification](/docs/specifications/run-card) — JSON schema ของ run card
- [Plugin Spec](https://champollion.dev/docs/reference/plugin-spec) — อินเทอร์เฟซปลั๊กอินฝั่ง champollion
- [Method Leaderboard](https://champollion.dev/leaderboard) — คะแนนเปรียบเทียบประสิทธิภาพแบบสด
- [Benchmark Specification](/docs/specifications/benchmark) — โปรโตคอลการประเมิน รูปแบบ corpus schema ของ run card
- [Scoring Specification](/docs/specifications/scoring) — SSOT สำหรับเมตริก น้ำหนัก composite และระดับคุณภาพ