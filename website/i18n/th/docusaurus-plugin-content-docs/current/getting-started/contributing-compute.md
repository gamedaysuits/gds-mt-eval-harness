---
sidebar_position: 4
title: "การมีส่วนร่วมด้าน Compute"
description: "บริจาค token ของคุณ: รัน benchmark sweep แบบเปิดจากคิวสาธารณะด้วย API key ของคุณเองและเผยแพร่ผลลัพธ์"
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
# การมีส่วนร่วมด้านทรัพยากรการประมวลผล

> **แนวคิด:** ลีดเดอร์บอร์ดมีช่องว่างอยู่ — คือชุดผสมผสาน (คู่ภาษา, โมเดล, เงื่อนไข) ที่ยังไม่มีใครวัดผล เรารักษาคิวสาธารณะสำหรับรายการเหล่านี้ไว้ คุณรันรายการด้วย API key ของตัวเอง เผยแพร่รายงาน และแผนที่ก็จะถูกเติมเต็ม "การบริจาค token" ถือเป็นการมีส่วนร่วมที่แท้จริงและสามารถอ้างอิงได้ในการประเมิน MT สำหรับภาษาที่มีทรัพยากรน้อย

## คิว

คิวที่ใช้งานอยู่เผยแพร่ที่ [champollion.dev/queue.json](https://champollion.dev/queue.json) และมีตัวแสดงผลในเทอร์มินัลแบบไม่ต้องติดตั้ง:

```bash
curl -fsSL champollion.dev/queue | bash
```

ตัวแสดงผลจะ*แสดง*เฉพาะรายการที่เปิดอยู่และคำสั่ง `mt-eval run` ที่แน่นอนเท่านั้น — ไม่มีการรันคำสั่งใดหรือใช้ token ของคุณ แต่ละรายการประกอบด้วย:

- `run_command` — พร้อมสำหรับการคัดลอกและวาง (ดึงข้อมูล corpus, รัน harness)
- `est_cost_usd` และ `est_basis` — ไม่ว่าจะเป็นต้นทุน**ที่สังเกตได้จริง**จากการรัน baseline ของเราเองสำหรับ (corpus, โมเดล) เดียวกัน หรือ**การประมาณการ**จากต้นทุนเฉลี่ยต่อรายการของโมเดลนั้นในการ sweep × จำนวนรายการใน corpus โดยระบุพื้นฐานไว้ต่อรายการ ต้นทุนจริงของคุณขึ้นอยู่กับราคาของผู้ให้บริการในขณะรัน
- `priority` — คู่ภาษาที่ยังไม่ครอบคลุมก่อน คู่ภาษาที่มีทรัพยากรน้อยที่สุดก่อน (ขนาด corpus เป็นตัวแทน) naive ก่อน coached โมเดลที่ถูกที่สุดก่อน

**ไม่มีการล็อกการจอง — เลือกรายการที่เปิดอยู่รายการใดก็ได้** การที่สองคนรันรายการเดียวกันไม่เป็นปัญหาโดยการออกแบบ: run card ทุกใบมีลายนิ้วมือ (SHA-256 จาก dataset hash + โมเดล + เงื่อนไข + system prompt, [Benchmark Spec §3.8](/docs/specifications/benchmark)) ดังนั้นการรันที่เหมือนกันจะถูกรวมเป็นหนึ่งเมื่อเผยแพร่ และการทำซ้ำอิสระของการกำหนดค่าเดียวกันถือเป็นหลักฐานที่มีประโยชน์ ไม่ใช่ความสูญเปล่า

corpus ในคิวเป็น dev-split, ใช้สัญญาอนุญาต CC-BY-family (ได้มาจาก Tatoeba) และมีการทำเครื่องหมาย `do_not_train` — เป็นชุดข้อมูลสำหรับการประเมิน ไม่ใช่ข้อมูลสำหรับการฝึก corpus ที่มีสัญญาอนุญาตเชิงพาณิชย์และ corpus ที่ถูกกักกันจะถูกยกเว้นจากคิวสาธารณะ

## การตั้งค่า (ครั้งเดียว)

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### ควรใช้ provider key ของผู้ให้บริการใด?

harness จะส่งการเรียกโมเดล**ทั้งหมด**ผ่าน [OpenRouter](https://openrouter.ai/keys) `OPENROUTER_API_KEY` เพียงตัวเดียวสามารถเข้าถึงโมเดลทุกตัวในรายการคิว — ทั้ง Anthropic Claude, OpenAI GPT และ Google Gemini — และการติดตามต้นทุนและ snapshot ราคาของ harness มาจาก metadata ของ OpenRouter เดียวกัน ดังนั้นต้นทุนการรันที่รายงานจะตรงกับสิ่งที่ key ของคุณถูกเรียกเก็บ

หากเครดิตของคุณอยู่กับ Anthropic, OpenAI หรือ Google โดยตรง: harness **ไม่รองรับ** direct provider key ในปัจจุบัน schema ของ run card สงวนฟิลด์ `api_provider` ไว้สำหรับวันที่รองรับ แต่ในปัจจุบันการรัน harness ทุกครั้งเป็นการรันผ่าน OpenRouter การสร้างบัญชี OpenRouter และเติมเงิน (หรือเชื่อมต่อบัญชีผู้ให้บริการของคุณเองในกรณีที่ OpenRouter รองรับ) คือแนวทางที่รองรับ

### เส้นทางด่วนผ่าน agent

หากคุณทำงานกับ Claude Code หรือ coding agent อื่น การมีส่วนร่วมทั้งหมดใช้เพียง prompt เดียว:

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## Tier 1 — รัน benchmark

`run_command` ของรายการในคิวทุกรายการเป็น self-contained ตัวอย่างทั่วไป:

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

การรันจะแสดงต้นทุนรวมและเขียน run log พร้อม scored report ไปยัง `eval/logs/` จากนั้นเผยแพร่:

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

การเผยแพร่จะให้คุณลงชื่อเข้าใช้ผ่าน OAuth (ชื่อของคุณจะกลายเป็นการระบุแหล่งที่มาบนลีดเดอร์บอร์ด) และ upsert run card การส่งจากชุมชนจะอยู่ในระดับความน่าเชื่อถือ **self-benchmarked** — ระบุอย่างชัดเจนว่า "ส่งโดยผู้ที่รันเอง" นั่นไม่ใช่การลดระดับ แต่เป็นโมเดลความน่าเชื่อถือที่ทำงานอยู่ run card มีทุกสิ่งที่จำเป็นสำหรับให้ใครก็ตามรันการกำหนดค่าเดียวกันของคุณซ้ำได้: dataset hash, โมเดล, เงื่อนไข, system prompt ฉบับเต็ม และต้นทุน ระดับที่สูงขึ้น (verification, community validation) จะได้รับโดยการตรวจสอบ — ดู [Leaderboard Rules](/docs/leaderboard/rules)

## Tier 2 — สร้าง coached prompt

harness รองรับ **coaching** อย่างเต็มรูปแบบ: แทนที่ naive system prompt ด้วย prompt ที่มีความรู้ทางภาษาศาสตร์จริง ส่ง `--coaching-file` (หรือ `--coaching "inline text"` สำหรับ prompt สั้น) และ harness จะใช้ข้อความของคุณเป็น system prompt บันทึก**ข้อความฉบับเต็มพร้อม SHA-256** ในบล็อก provenance ของ run log และระบุเงื่อนไขของการรันว่า **`coached`** (เว้นแต่คุณจะตั้งค่า `--prompt` อย่างชัดเจน) — ดังนั้นการสร้าง prompt จึงเป็นการทดลองที่ทำซ้ำได้และระบุแหล่งที่มาได้ ไฟล์ coaching สองไฟล์ที่แตกต่างกันจะไม่มีทางสับสนกัน และการรันแบบ coached จะไม่ถูกเข้าใจผิดว่าเป็น naive baseline บนลีดเดอร์บอร์ด

ตัวอย่างการใช้งานสำหรับภาษา Faroese โดยใช้ข้อเท็จจริงด้านประเภทวิทยาและรายการคำศัพท์จาก [public language card](https://champollion.dev/languages) ของภาษา:

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

(เขียนเนื้อหา coaching ของคุณเอง — ข้อเท็จจริงข้างต้นแสดงให้เห็น*รูปแบบ*: กฎไวยากรณ์ที่มีผลกระทบสูงสองสามข้อ คำศัพท์ขนาดเล็กของคำที่โมเดลมักแปลผิด และคำแนะนำด้านรูปแบบภาษา Language card ที่ [champollion.dev/languages](https://champollion.dev/languages) อ้างอิงแหล่งที่มาด้านประเภทวิทยาที่คุณสามารถนำมาใช้ได้)

เปรียบเทียบกับ naive baseline ด้วย `mt-eval compare <naive_log> <coached_log>` ปรับปรุงซ้ำ และเผยแพร่การรันที่ดีที่สุดของคุณ การรันจะเผยแพร่พร้อมเงื่อนไข `coached` โดยอัตโนมัติ หากคุณต้องการให้ลีดเดอร์บอร์ดแสดงชื่อวิธีการแทนป้ายกำกับทั่วไป ให้แนบ method card เมื่อเผยแพร่ (ขั้นตอนการเผยแพร่มี wizard ให้ใช้) การเอาชนะ naive baseline ในคู่ภาษาที่มีทรัพยากรน้อยด้วย prompt engineering เพียงอย่างเดียวถือเป็นผลการค้นพบที่แท้จริงและสามารถตีพิมพ์ได้ — ดู [Coached LLM Prompting cookbook](/docs/tutorials/coached-llm-prompting) ฉบับเต็มสำหรับแนวทางการออกแบบ

## Tier 3 — สร้างวิธีการ

การมีส่วนร่วมที่ทะเยอทะยานที่สุด: ใช้งานโปรโตคอล `TranslationMethod` (`translate(entries, config)`) และทำ benchmark ระบบจริง ไม่ใช่แค่ prompt harness รันผ่าน `--method <plugin-dir>` และฝัง method card ของคุณใน run card รูปแบบพร้อม cookbook ที่มีตัวอย่างการใช้งาน:

- **[FST-gated pipelines](/docs/tutorials/fst-gated-pipeline)** — คำผู้สมัครทุกคำถูกตรวจสอบโดย morphological analyzer; LLM จะสร้างใหม่จนกว่า gate จะผ่าน ผลลัพธ์แบบกึ่ง-deterministic ที่รับประกันด้านสัณฐานวิทยา
- **[Dictionary-augmented generation](/docs/tutorials/dictionary-augmented-llm)** — ค้นหาคำต้นฉบับใน bilingual lexicon ในขณะแปลและจำกัดผลลัพธ์
- [Chained models](/docs/tutorials/chained-models), [few-shot retrieval](/docs/tutorials/few-shot-prompting), [back-translation](/docs/tutorials/back-translation), [rule-based hybrids](/docs/tutorials/rule-based-hybrid)…

วิธีการต้องประกาศ **dependency class** (S/O/A1/A2/X — ดู [the methods spec](/docs/specifications/methods#method-validity-and-dependency-classes)) ที่อธิบายสิ่งที่จำเป็นสำหรับการรันและการถ่ายโอน: pipeline ที่ self-contained คือ Class S; วิธีที่เรียก licensed dictionary API ในขณะรันคือ A2 ประกาศอย่างซื่อสัตย์ — class จะกำหนดว่าวิธีการของคุณสามารถแข่งขันได้ที่ใด และ manifest จะถูกตรวจสอบ

## เหตุใดสิ่งนี้จึงมีความสำคัญเกินกว่าแค่ลีดเดอร์บอร์ด

การรันที่เผยแพร่ทุกครั้งเป็นหลักฐานอิสระเกี่ยวกับคุณภาพ MT สำหรับคู่ภาษาที่ผู้ให้บริการเชิงพาณิชย์ไม่ได้วัดผล คิวยังทำหน้าที่เป็นบันทึกสาธารณะของ*ความต้องการ*: คู่ภาษาใดที่ชุมชนพิจารณาว่าคุ้มค่าแก่การวัด ต้นทุนของการครอบคลุมในราคา API ปัจจุบัน และทรัพยากรการประมวลผลที่บริจาคสามารถขยายได้ไกลแค่ไหน เมื่อเราขอให้หน่วยงานให้ทุนสนับสนุนการ sweep อย่างเป็นระบบ คิวนี้และอัตราการเติมเต็มคือหลักฐานของความต้องการ