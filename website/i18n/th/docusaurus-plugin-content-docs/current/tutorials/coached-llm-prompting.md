---
sidebar_position: 2
title: "คู่มือ: Coached LLM Prompting"
related:
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
  - label: "Cookbook: Fine-Tuned Model"
    to: /docs/tutorials/fine-tuned-model
    kind: cookbook
  - label: "Coaching Data"
    to: https://champollion.dev/docs/concepts/coaching-data
    kind: champollion
    note: "How coaching data ships to production"
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
---
# การกำหนดทิศทาง LLM ด้วยการโค้ช

> **แนวคิด:** ฝังกฎไวยากรณ์ พจนานุกรมสองภาษา และหมายเหตุด้านสไตล์ลงใน system prompt ของ LLM โดยตรง ไม่ต้องฝึกหรือ fine-tune — เพียงใช้ความรู้ทางภาษาศาสตร์ที่มีโครงสร้างเพื่อนำทางผลลัพธ์ไปสู่การแปลที่ถูกต้อง

:::info นี่คือ cookbook ไม่ใช่การนำไปใช้งานสำเร็จรูป
คู่มือนี้ร่างแนวทางและการตัดสินใจออกแบบที่สำคัญ ปรับให้เหมาะกับคู่ภาษา ทรัพยากรที่มี และเป้าหมายการประเมินของคุณ
:::

## เมื่อใดควรใช้วิธีนี้

- คุณมี **ความรู้ทางภาษาศาสตร์** เกี่ยวกับภาษาเป้าหมาย (กฎไวยากรณ์ รายการพจนานุกรม ความต้องการด้านสไตล์) แต่ไม่มีข้อมูลคู่ขนานเพียงพอสำหรับการ fine-tune
- คุณต้องการ **ทำซ้ำอย่างรวดเร็ว** — การเปลี่ยน prompt ใช้งานได้ทันทีในไม่กี่วินาที ไม่ต้องฝึกใหม่
- ภาษาเป้าหมายมี **รูปแบบที่ทราบแน่ชัด** ซึ่ง LLM มักทำผิด (การสอดคล้องทางเพศ รูปแบบอักษร ระดับความสุภาพ)
- คุณต้องการเปรียบเทียบประสิทธิภาพของการโค้ช prompt กับ baseline และปรับปรุงสิ่งที่ได้ผล

## วิธีการทำงาน

1. **รวบรวมข้อมูลการโค้ช** — กฎไวยากรณ์ พจนานุกรมสองภาษา และหมายเหตุด้านสไตล์ในไฟล์ JSON ที่มีโครงสร้าง
2. **กำหนดค่า register** — คำนำหน้า system prompt ที่ระบุภาษา อักษร และโทนเสียง
3. **รัน harness** — ข้อมูลการโค้ชจะถูกฝังลงใน LLM prompt ทุกรายการ
4. **ตรวจสอบความล้มเหลว** — ดูสิ่งที่ quality gate ปฏิเสธ แล้วเพิ่มกฎเพื่อแก้ไขรูปแบบที่พบ
5. **ทำซ้ำ** — การแก้ไขไฟล์การโค้ชแต่ละครั้งคือการทดลองใหม่ harness จะติดตามทั้งหมด

## โครงสร้างข้อมูลการโค้ช

```json title="coaching/<locale>.json"
{
  "grammar_rules": [
    "Adjectives agree in gender and number with the noun they modify",
    "Use formal register (vous) for all UI text",
    "Preserve interpolation variables exactly: {{name}}, {count}"
  ],
  "dictionary": {
    "dashboard": "tableau de bord",
    "settings": "paramètres",
    "deploy": "déployer"
  },
  "style_notes": "Prefer active voice. Avoid anglicisms where a native term exists. Keep sentences concise for UI readability."
}
```

## การตัดสินใจออกแบบที่สำคัญ

**ความเฉพาะเจาะจงของกฎ vs. context window:** กฎที่มากขึ้นให้คำแนะนำแก่ LLM มากขึ้น แต่ใช้พื้นที่ใน context window ที่มีไว้สำหรับการแปลจริง เริ่มต้นด้วยกฎที่มีผลกระทบสูง 5–10 ข้อ และเพิ่มเติมเฉพาะเมื่อพบรูปแบบความล้มเหลวที่เฉพาะเจาะจง

**ความครอบคลุมของพจนานุกรม:** คุณไม่จำเป็นต้องมีพจนานุกรมที่สมบูรณ์ — มุ่งเน้นที่คำศัพท์ที่ LLM แปลผิดอย่างสม่ำเสมอ แม้แต่คำที่บังคับใช้ 20–30 คำก็สามารถปรับปรุงความสอดคล้องได้อย่างมาก

**ลำดับของกฎมีความสำคัญ:** วางกฎที่สำคัญที่สุดไว้ก่อน LLM ให้ความสนใจกับคำสั่งที่อยู่ต้นมากกว่า

## การรันการทดลอง

```bash
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v1 \
  --coaching-file coaching/crk.json
```

## ข้อดีและข้อเสีย

| | |
|---|---|
| ✅ ไม่มีต้นทุนการฝึก | ❌ เพดานคุณภาพถูกจำกัดด้วยความรู้พื้นฐานของ LLM |
| ✅ ทำซ้ำได้ทันที (เปลี่ยน prompt → รันใหม่) | ❌ context window จำกัดปริมาณการโค้ชที่ใส่ได้ |
| ✅ ใช้งานได้กับผู้ให้บริการ LLM ทุกราย | ❌ กฎอาจขัดแย้งกัน — การดีบัก prompt interactions ต้องอาศัยประสบการณ์ |
| ✅ โปร่งใส — คุณสามารถอ่านสิ่งที่ LLM เห็นได้ทุกอย่าง | ❌ ไม่ได้สร้างความรู้ใหม่ เพียงแต่นำทางความรู้ที่มีอยู่ |

## ใช้งานร่วมกันได้ดีกับ

- **[FST-Gated Pipeline](./fst-gated-pipeline)** — การโค้ชร่วมกับการตรวจสอบทางสัณฐานวิทยาจะจับสิ่งที่การโค้ชเพียงอย่างเดียวพลาดไป
- **[Dictionary-Augmented LLM](./dictionary-augmented-llm)** — การบังคับใช้คำศัพท์เป็นรูปแบบหนึ่งของการโค้ช
- **[Few-Shot Prompting](./few-shot-prompting)** — ตัวอย่างร่วมกับกฎมีประสิทธิภาพมากกว่าการใช้อย่างใดอย่างหนึ่งเพียงอย่างเดียว

## ดูเพิ่มเติม

- [Method Interface](/docs/specifications/methods) — รูปแบบข้อมูลการโค้ชและ TranslationMethod protocol
- [Support a Low-Resource Language](/docs/community/low-resource-languages) — บริบทฉบับสมบูรณ์
- [Eval Harness](/docs/specifications/harness) — วิธีการรันการทดลอง