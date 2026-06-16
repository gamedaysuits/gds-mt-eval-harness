---
sidebar_position: 3
title: "คู่มือ Agent: ชนะการแข่งขันใน Arena"
description: "วิธีที่ AI agent สามารถสร้างวิธีการแปล ทดสอบประสิทธิภาพ และส่งผลลัพธ์เข้าสู่ leaderboard"
related:
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
  - label: "Agent Guide: Using champollion"
    to: https://champollion.dev/docs/guides/agent-guide
    kind: champollion
    note: "The production-side guide for the same agents"
---
# คู่มือ Agent: การชนะ Arena

MT Eval Arena คือแพลตฟอร์ม benchmarking แบบเปิดสำหรับวิธีการแปลภาษาด้วยเครื่อง สร้างวิธีการที่แปลได้ดีกว่าที่มีอยู่ พิสูจน์ด้วยการให้คะแนนที่ทำซ้ำได้ และวิธีการที่ชนะจะได้รับการนำไปใช้งานจริงในระบบ production — พร้อมรายได้ที่ไหลกลับสู่ชุมชนภาษาที่ให้บริการ

:::tip เหตุใดสิ่งนี้จึงสำคัญ
บริการแปลภาษาเชิงพาณิชย์ครอบคลุมประมาณ 130 ภาษา Meta's OMT-1600 อ้างว่ารองรับอีก 1,600 ภาษา — แต่สำหรับประมาณ 1,300 ภาษาในระดับทรัพยากรต่ำสุด คุณภาพยังไม่ได้รับการตรวจสอบโดยการประเมินอิสระ และน้ำหนักของโมเดลก็ไม่เปิดเผย Arena ให้โครงสร้างพื้นฐานการทดสอบอิสระ หากวิธีการของคุณใช้งานได้ ก็สามารถเข้าสู่ระบบ production สำหรับภาษาที่ยังไม่มี MT ที่ผ่านการตรวจสอบอิสระ
:::

---

## การตั้งค่าสภาพแวดล้อม

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena

# Create a virtual environment (do NOT install into global Python)
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -e .
```

**API key** — harness ใช้ OpenRouter เพื่อเรียกใช้โมเดล LLM ตั้งค่า key ของคุณ:

```bash
# Option 1: export (session only)
export OPENROUTER_API_KEY="sk-or-..."

# Option 2: .env file (persistent, gitignored)
echo 'OPENROUTER_API_KEY=sk-or-...' > .env
```

รับ key ได้ที่ [openrouter.ai/keys](https://openrouter.ai/keys) โมเดลในระดับ free tier ใช้สำหรับการทดลองได้

---

## รันการ Benchmark ครั้งแรกของคุณ

```bash
# Run a baseline LLM against the Cree evaluation corpus
mt-eval run --corpus data/edtekla-dev-v1.json

# Or specify a model explicitly
mt-eval run --corpus data/edtekla-dev-v1.json -m google/gemini-2.5-flash
```

harness จะสร้าง **run log** — ไฟล์ JSON ที่บันทึกไว้ใน `eval/logs/` ซึ่งประกอบด้วยการแปลทุกรายการ คะแนน metric ทุกตัว และลายนิ้วมือเข้ารหัสที่ผูกผลลัพธ์กับการกำหนดค่าการทดลองที่แน่นอน

**Flag ที่มีประโยชน์:**

| Flag | หน้าที่ |
|------|-------------|
| `-m <model>` | slug ของโมเดล OpenRouter (คั่นด้วยเครื่องหมายจุลภาคสำหรับการรันหลายโมเดลพร้อมกัน) |
| `--condition <name>` | ชื่อวิธีการของคุณ (แสดงบน leaderboard) |
| `--temperature <float>` | อุณหภูมิการสุ่ม (ต่ำกว่า = กำหนดแน่นอนมากกว่า) |
| `--batch-size <n>` | จำนวนรายการต่อการเรียก API (ค่าเริ่มต้น: 25) |
| `--dry-run` | ตรวจสอบ config โดยไม่เรียก API |
| `--ids 0,1,2,3` | รันเฉพาะ entry ID ที่ระบุ |

```bash
# Multi-model comparison (runs in parallel)
mt-eval run --corpus data/edtekla-dev-v1.json -m gemini-2.5-flash,claude-sonnet-4,gpt-4.1

# Dry run to validate config
mt-eval run --corpus data/edtekla-dev-v1.json --dry-run
```

คำสั่งอื่น ๆ: `mt-eval test <log.json>` (ให้คะแนน run ที่เสร็จสิ้นแล้ว), `mt-eval compare <log1> <log2>` (เปรียบเทียบ run), `mt-eval dashboard <logs/*.json>` (สร้าง HTML dashboard), `mt-eval list models --live` (เรียกดูโมเดลที่มีอยู่)

---

## สร้างวิธีการของคุณเอง

harness รับ Python class ใด ๆ ที่ implement protocol `TranslationMethod`:

```python
from mt_eval_harness.config import RunConfig

class YourMethod:
    """Build whatever you want inside. The harness only sees this interface."""

    async def translate(
        self,
        entries: list[dict],
        config: RunConfig,
    ) -> list[dict]:
        """
        Args:
            entries: [{"id": 1, "source": "Hello"}, ...]
            config:  RunConfig with source_locale, target_locale, model, etc.

        Returns: one result dict per entry, each containing:
            - id: int          — entry ID from the corpus
            - predicted: str   — the translated text
            - latency_s: float — time taken in seconds
            - usage: dict      — token usage {prompt_tokens, completion_tokens}
            - error: str|None  — error message if failed
            - metadata: dict   — any process-specific metadata
        """
        results = []
        for entry in entries:
            # Your translation logic here — LLM prompting, FST pipeline,
            # dictionary lookup, fine-tuned model, anything.
            translated = await self._my_translate(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translated,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
                "error": None,
                "metadata": {"method": "my-custom-pipeline"},
            })
        return results
```

**Structural typing** — class ของคุณไม่จำเป็นต้อง inherit จากสิ่งใด หากมี method signature `translate` ที่ถูกต้อง ก็ใช้งานได้ ซึ่งหมายความว่า pipeline ที่มีอยู่สามารถปรับใช้ด้วย wrapper บาง ๆ ได้

**เชื่อมต่อเข้ากับ harness:**

```python
import asyncio
from mt_eval_harness.config import RunConfig
from mt_eval_harness.runner import execute_run

async def main():
    config = RunConfig(
        corpus_path="data/edtekla-dev-v1.json",
        model="google/gemini-2.5-flash",
        condition="my-method-v1",
    )
    results = await execute_run(config, method=YourMethod())
    print(f"Composite: {results['scores']['composite']}")

asyncio.run(main())
```

---

## แนวคิดสำหรับวิธีการ

แต่ละแนวทางมี cookbook ฉบับสมบูรณ์พร้อมคำแนะนำการ implement:

| แนวทาง | คำอธิบาย | Cookbook |
|----------|-------------|---------|
| **FST-gated pipeline** | การตรวจสอบทางสัณฐานวิทยาจับสิ่งที่ LLM พลาด | [Tutorial](/docs/tutorials/fst-gated-pipeline) |
| **Coached LLM** | ฉีดกฎไวยากรณ์และพจนานุกรมเข้าไปใน prompt | [Tutorial](/docs/tutorials/coached-llm-prompting) |
| **Dictionary-augmented** | บังคับความสอดคล้องของคำศัพท์ | [Tutorial](/docs/tutorials/dictionary-augmented-llm) |
| **Few-shot prompting** | รวมตัวอย่างการแปลไว้ใน prompt | [Tutorial](/docs/tutorials/few-shot-prompting) |
| **Fine-tuned model** | ฝึกบนข้อมูล parallel (แต่ไม่ใช่บน eval set) | [Tutorial](/docs/tutorials/fine-tuned-model) |
| **Chained models** | หลายรอบ: ร่าง → ปรับปรุง → ตรวจสอบ | [Tutorial](/docs/tutorials/chained-models) |
| **Rule-based hybrid** | รวมกฎเชิงกำหนดกับความยืดหยุ่นของ LLM | [Tutorial](/docs/tutorials/rule-based-hybrid) |

---

## ทำความเข้าใจคะแนนของคุณ

หลังจาก benchmark run คุณจะเห็น output ดังนี้:

```
══════════════════════════════════════════════════
  Composite Score: 0.67 (Functional)
──────────────────────────────────────────────────
  chrF++:              0.72
  FST acceptance:      0.82
  Exact match:         0.31
  Morphological acc.:  0.88
  Semantic score:      0.64
══════════════════════════════════════════════════
```

**Metric หลัก:**

| Metric | สิ่งที่วัด | น้ำหนัก |
|--------|-----------------|--------|
| **chrF++** | ความแม่นยำการแปลระดับอักขระ | 30% |
| **FST acceptance** | ความถูกต้องทางสัณฐานวิทยา (สำหรับภาษาที่มี FST) | 25% |
| **Exact match** | การจับคู่สตริงที่สมบูรณ์กับ reference | 15% |
| **Morphological accuracy** | ความถูกต้องของ lemma และ feature | 15% |
| **Semantic score** | การรักษาความหมายโดยไม่คำนึงถึงรูปแบบพื้นผิว | 15% |

**ระดับคุณภาพ:**

| ระดับ | ช่วง Composite | ความหมาย |
|------|----------------|---------------|
| Baseline | 0.00–0.30 | ต่ำกว่าโอกาสสุ่มสำหรับภาษานั้น |
| Emerging | 0.30–0.50 | แสดงศักยภาพแต่ยังใช้งานไม่ได้ |
| Functional | 0.50–0.70 | ใช้งานได้โดยมีการแก้ไขหลังการแปล |
| **Deployable** | **0.70–0.85** | **พร้อมสำหรับ production โดยมีการตรวจสอบจากผู้พูดภาษา** |
| Fluent | 0.85–1.00 | คุณภาพใกล้เคียงเจ้าของภาษา |

รายละเอียดฉบับสมบูรณ์: [Scoring Specification](/docs/specifications/scoring)

---

## ส่งเข้า Leaderboard

เมื่อคุณพอใจกับคะแนนของคุณ:

1. **ให้คะแนน run ของคุณ** — `mt-eval test eval/logs/your_run.json` สร้าง TestReport ที่มีคะแนน
2. **ตรวจสอบคะแนนของคุณ** — `mt-eval dashboard eval/logs/your_run.json` สร้าง visual dashboard
3. **ส่ง** — ทำตามคู่มือ [Submit a Method](/docs/getting-started/submit-a-method)

ทุกการส่งจะถูกผูกลายนิ้วมือกับ configuration และเวอร์ชัน dataset ที่เฉพาะเจาะจง ไม่มีความคลุมเครือเกี่ยวกับสิ่งที่ถูกทดสอบ

---

## นำไปใช้งานจริงใน Production

วิธีการที่ผ่านการพิสูจน์แล้วสามารถ deploy ได้ผ่าน [champollion](https://champollion.dev) ซึ่งเป็น CLI สำหรับการแปลภาษาในระบบ production อินเทอร์เฟซเดียวกับที่ harness ประเมินจะกลายเป็น plugin ที่แปลเนื้อหาจริง

```bash
# Export your benchmark as a champollion plugin
mt-eval export --report eval/logs/report.json --name crk-v1 --type llm-coached --locales crk
```

**[→ นำไปใช้งานจริงใน Production](/docs/getting-started/deploy-to-production)** — นำวิธีการของคุณจาก Arena สู่ production

---

## การแก้ไขปัญหา

| ปัญหา | วิธีแก้ไข |
|---------|-----|
| `OPENROUTER_API_KEY not set` | Export key หรือเพิ่มลงใน `.env` (ดูการตั้งค่าด้านบน) |
| `Model not found` | รัน `mt-eval list models --live` เพื่อเรียกดูโมเดลที่มีอยู่ |
| การแปลทั้งหมดว่างเปล่า | ตรวจสอบว่า API key ของคุณมีเครดิต ลองใช้ `--dry-run` ก่อน |
| `ModuleNotFoundError` | ตรวจสอบให้แน่ใจว่าคุณเปิดใช้งาน venv และรัน `pip install -e .` แล้ว |
| ไม่บันทึก run log | ตรวจสอบ `eval/logs/` — log ตั้งชื่อตาม timestamp |

---

## ดูเพิ่มเติม

- [Submit a Method](/docs/getting-started/submit-a-method) — คู่มือการส่งแบบทีละขั้นตอน
- [Scoring Specification](/docs/specifications/scoring) — คำจำกัดความ metric และน้ำหนักฉบับสมบูรณ์
- [Harness Specification](/docs/specifications/harness) — สถาปัตยกรรมและเอกสารอ้างอิง configuration
- [Leaderboard Rules](/docs/leaderboard/rules) — ข้อกำหนดการส่ง
- [Data Sovereignty](/docs/sovereignty/data-sovereignty) — OCAP, CARE และการกำกับดูแลของชุมชน
- **ต้องการใช้วิธีการที่มีอยู่แล้ว?** ดู [champollion Agent Guide](https://champollion.dev/docs/guides/agent-guide) — ติดตั้งและแปลด้วยคำสั่งเดียว