---
sidebar_position: 5
title: "รองรับภาษาที่มีทรัพยากรน้อย"
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
# รองรับภาษาที่มีทรัพยากรน้อย

> **สรุปสำหรับผู้บริหาร** คู่มือฉบับสมบูรณ์สำหรับการสร้างระบบแปลภาษาเครื่องสำหรับภาษาที่มีทรัพยากรน้อยและภาษาโพลีซินเทติก ครอบคลุมสาเหตุที่ภาษาเหล่านี้มีความท้าทาย (ความซับซ้อนทางสัณฐานวิทยา ข้อมูลเบาบาง การสร้างข้อมูลเท็จ) ทรัพยากรการประมวลผลที่มีอยู่ (ALTLab FST, GiellaLT, Apertium, UniMorph, EdTeKLA) กลยุทธ์การดำเนินการมากกว่า 10 แนวทาง ระบบ coaching ของ champollion และวงจรการประเมินผล เริ่มต้นที่นี่หากคุณต้องการมีส่วนร่วมในการพัฒนาวิธีการสำหรับภาษาที่ยังขาดการสนับสนุน

:::info สถานะ: อยู่ระหว่างการพัฒนาอย่างต่อเนื่อง
การรองรับภาษา Plains Cree (nêhiyawêwin) อยู่ระหว่างการพัฒนา เครื่องมือ eval harness และ leaderboard ที่อธิบายไว้ที่นี่พร้อมใช้งานจริงในปัจจุบัน แต่ pipeline การแปลภาษา Cree ยังไม่ได้เผยแพร่ เมื่อพร้อมแล้ว เอกสารนี้จะทำหน้าที่เป็นแบบแผนสำหรับภาษาโพลีซินเทติกและภาษาที่มีทรัพยากรน้อยอื่น ๆ ที่มีโครงสร้างพื้นฐาน FST
:::

## ปัญหาที่ยังไม่ได้รับการแก้ไข

Google Translate รองรับประมาณ 130 ภาษา OMT-1600 ของ Meta (มีนาคม 2026) อ้างว่าครอบคลุม 1,600 ภาษา — ระบบ MT ที่ใหญ่ที่สุดที่เคยเผยแพร่ แต่สำหรับภาษาประมาณ 1,300 ภาษาในระดับทรัพยากรต่ำสุด คุณภาพยังต่ำกว่าเกณฑ์ที่ใช้งานได้จริง ข้อมูลการฝึกอบรมถูกครอบงำด้วยข้อความจากพระคัมภีร์ น้ำหนักโมเดลไม่สามารถดาวน์โหลดได้ และไม่มีกรอบการประเมินอิสระหรือการกำกับดูแลโดยชุมชน สำหรับภาษาที่เหลืออีกประมาณ 5,400 ภาษา ไม่มีโมเดลที่ผ่านการฝึกล่วงหน้าใดที่สามารถสร้างผลลัพธ์ได้เลย

ภูมิทัศน์เปลี่ยนแปลงไปอย่างมีนัยสำคัญ — บริษัทเทคโนโลยีขนาดใหญ่กำลังลงทุนในการครอบคลุมภาษาที่มีทรัพยากรน้อย แต่การครอบคลุมไม่ใช่คุณภาพ และคุณภาพที่ปราศจากการตรวจสอบอิสระไม่ใช่ความน่าเชื่อถือ ภาษาที่มีทรัพยากรน้อยต้องการมากกว่าโมเดลที่อ้างว่าครอบคลุม — พวกเขาต้องการการประเมินอิสระพร้อมการตรวจสอบทางสัณฐานวิทยา คลังข้อมูลที่ดูแลโดยชุมชน และการกำกับดูแลที่เคารพอำนาจอธิปไตย

**champollion ถูกสร้างขึ้นเพื่อเปลี่ยนแปลงสิ่งนั้น**

[Method Leaderboard](https://champollion.dev/leaderboard) คือความท้าทายแบบเปิด: สร้างวิธีการแปลที่ดีที่สุดสำหรับภาษาที่ยังขาดการสนับสนุน พิสูจน์ด้วยการประเมินที่ทำซ้ำได้ และครองคะแนนสูงสุด ทุกคนในโลกสามารถมีส่วนร่วมได้ — นักภาษาศาสตร์ นักวิจัย ML นักทำงานด้านภาษาชุมชน นักศึกษา และผู้ที่สนใจ ปัญหายังไม่ได้รับการแก้ไข โครงสร้างพื้นฐานพร้อมแล้ว leaderboard กำลังรอคุณอยู่

---

## เหตุใดจึงยาก: สัณฐานวิทยาโพลีซินเทติก

ระบบ MT เชิงพาณิชย์ส่วนใหญ่ถูกออกแบบมาสำหรับภาษาอย่างอังกฤษ ฝรั่งเศส และจีน — ภาษาที่คำค่อนข้างสั้นและประโยคถูกสร้างจาก token ที่แยกจากกัน แต่ภาษาพื้นเมืองหลายภาษา รวมถึง Plains Cree เป็น **โพลีซินเทติก**: คำเดียวสามารถเข้ารหัสสิ่งที่ภาษาอังกฤษแสดงออกเป็นประโยคทั้งประโยค

### ตัวอย่างภาษา Cree

พิจารณาคำในภาษา Plains Cree:

> **ê-kî-nitawi-kîskinwahamâkosiyân**
> *"when I went to school"*

นั่นคือ **คำเดียว** มันเข้ารหัสกาล (อดีต) ทิศทาง (ไปยัง) รากศัพท์ (เรียนรู้) วอยซ์ (passive/reflexive) และบุคคล (บุรุษที่หนึ่งเอกพจน์) LLM ที่ฝึกส่วนใหญ่บนภาษาอังกฤษไม่มีความเข้าใจสำหรับความหนาแน่นทางสัณฐานวิทยาประเภทนี้

ความท้าทายทวีคูณ:

| ความท้าทาย | ความหมาย |
|-----------|--------------|
| **ความซับซ้อนทางสัณฐานวิทยา** | รากกริยาเดียวสามารถสร้างรูปแบบที่ผันแล้วที่ถูกต้องได้หลายพันรูปแบบผ่านการเติมคำนำหน้า คำต่อท้าย และ circumfixation |
| **ความแตกต่างระหว่างสิ่งมีชีวิต/ไม่มีชีวิต** | คำนามมีความเป็นสิ่งมีชีวิตหรือไม่มีชีวิตทางไวยากรณ์ — ซึ่งส่งผลต่อการผันกริยา demonstratives และการทำพหูพจน์ การจำแนกประเภทไม่ได้เป็นไปตามความมีชีวิตทางชีววิทยาเสมอไป (*askiy* "โลก" มีชีวิต; *maskisin* "รองเท้า" ก็มีชีวิตเช่นกัน) |
| **Obviation** | การอ้างอิงบุรุษที่สามถูกจัดอันดับตามความใกล้ชิด/ความโดดเด่น ความแตกต่างระหว่าง "proximate" และ "obviative" ไม่มีคู่เทียบในภาษาอังกฤษ |
| **ข้อมูลการฝึกอบรมเบาบาง** | LLM ได้เห็นข้อความภาษา Plains Cree น้อยมาก สิ่งที่เห็นอาจผสมภาษาถิ่น (Y-dialect, TH-dialect) หรือระบบการเขียน (SRO กับ syllabics) |
| **เส้นฐานเชิงพาณิชย์ที่อ่อนแอ** | OMT-1600 รวม CRK ในระดับ R1 (Very Low Resource) พร้อมการฝึกในโดเมนพระคัมภีร์และการแบ่ง token แบบ BPE มาตรฐาน Google Translate ไม่รองรับภาษา Cree การประเมินอิสระด้วยเมตริกทางสัณฐานวิทยาคือสิ่งที่ทำให้เส้นฐานเหล่านี้มีความหมาย |

การแปลภาษาโพลีซินเทติกยังคงเป็น **ปัญหาการวิจัยที่เปิดอยู่** — OMT-1600 รวมภาษาโพลีซินเทติกแต่ใช้การแบ่ง token แบบ BPE มาตรฐาน (คำศัพท์ 256K) โดยไม่มีความตระหนักทางสัณฐานวิทยา ซึ่งหมายความว่ามันแยกคำที่มีองค์ประกอบออกเป็นชิ้นส่วนไบต์ที่ไม่มีความหมาย

---

## งานก่อนหน้า: วิธีที่ผู้คนได้ลองใช้

### ALTLab FST

ทรัพยากรการประมวลผลที่สำคัญที่สุดสำหรับภาษา Plains Cree คือ **finite-state transducer (FST)** ที่พัฒนาโดย [Alberta Language Technology Lab (ALTLab)](https://altlab.artsrn.ualberta.ca/) ที่มหาวิทยาลัย Alberta ร่วมกับ [Giellatekno](https://giellatekno.uit.no/) ที่ UiT The Arctic University of Norway

ALTLab FST คือ **ตัววิเคราะห์และตัวสร้างทางสัณฐานวิทยา**: เมื่อได้รับคำภาษา Cree ที่ผันแล้ว มันสามารถแยกออกเป็นรากศัพท์และแท็กทางไวยากรณ์ได้ และเมื่อได้รับรากศัพท์พร้อมแท็ก มันสามารถสร้างรูปแบบที่ผันถูกต้องได้ กระบวนการนี้เป็นแบบ deterministic — ไม่มีเครือข่ายประสาทเทียม ไม่มีการสร้างข้อมูลเท็จ ไม่มีความน่าจะเป็น หาก FST ยอมรับคำ คำนั้นถูกต้องทางสัณฐานวิทยา

นี่คือเหตุผลที่ leaderboard ของ champollion ติดตาม **FST Acceptance Rate** เป็นเมตริก วิธีการแปลที่สร้างคำที่ FST ปฏิเสธกำลังสร้างภาษา Cree ที่ไม่ถูกต้องทางสัณฐานวิทยา — โดยไม่คำนึงว่าคะแนน chrF++ จะบอกว่าอะไร

**ทรัพยากร ALTLab หลัก:**
- [itwêwina](https://itwewina.altlab.app/) — พจนานุกรม Plains Cree–อังกฤษอัจฉริยะที่ขับเคลื่อนด้วย FST
- [Morphodict](https://github.com/UAlbertaALTLab/morphodict) — แพลตฟอร์มพจนานุกรมที่ตระหนักถึงสัณฐานวิทยาแบบโอเพนซอร์ส
- [crk-db](https://github.com/UAlbertaALTLab/crk-db) — ฐานข้อมูลคำศัพท์ Plains Cree
- [21st Century Tools for Indigenous Languages](https://21c.tools/) — บริบทโครงการที่กว้างขึ้น

### รีจิสทรี FST และสัณฐานวิทยาระดับโลก

Plains Cree ไม่ใช่ภาษาเดียวที่มีโครงสร้างพื้นฐาน FST คุณภาพสูง หากคุณต้องการพัฒนา pipeline การแปลสำหรับภาษาที่มีทรัพยากรน้อยหรือภาษาที่มีความซับซ้อนทางสัณฐานวิทยาอื่น ๆ คุณสามารถใช้ประโยชน์จากศูนย์กลางระดับโลกที่จัดตั้งขึ้นเหล่านี้:

* **[GiellaLT / Giellatekno](https://giellalt.github.io/) (UiT The Arctic University of Norway):** คลังเก็บตัววิเคราะห์และตัวสร้างสัณฐานวิทยา FST แบบโอเพนซอร์สที่ใหญ่ที่สุด ครอบคลุมมากกว่า 100 ภาษา พื้นที่เน้นได้แก่ภาษา Sámi (`sme`, `smj`, `sma` ฯลฯ) ภาษา Uralic (Komi, Erzya, Udmurt ฯลฯ) และภาษาชนกลุ่มน้อย/ภาษาพื้นเมืองอื่น ๆ พวกเขาโฮสต์คลังข้อความที่ผ่านการประมวลผลสาธารณะ (`corpus-xxx`) ใน [GitHub Organization](https://github.com/giellalt/) ของพวกเขา
* **[The Apertium Project](https://www.apertium.org/):** แพลตฟอร์มการแปลภาษาเครื่องแบบ rule-based โอเพนซอร์ส Apertium ดูแลตัววิเคราะห์สัณฐานวิทยา FST ที่ได้รับการปรับให้เหมาะสมอย่างสูง (โดยใช้ `lttoolbox` และ `hfst`) และพจนานุกรมสองภาษาสำหรับหลายสิบภาษา รวมถึงชุดภาษา Turkic ขนาดใหญ่ (Kazakh, Tatar, Kyrgyz ฯลฯ) และภาษาชนกลุ่มน้อยในยุโรป ทรัพยากรทั้งหมดเป็นสาธารณะบน [Apertium's GitHub](https://github.com/apertium)
* **[UniMorph (Universal Morphology)](https://unimorph.github.io/):** โครงการความร่วมมือที่ให้ paradigm สัณฐานวิทยามาตรฐานสำหรับมากกว่า 150 ภาษา ชุดข้อมูลโฮสต์บน Hugging Face ที่ [unimorph/universal_morphologies](https://huggingface.co/datasets/unimorph/universal_morphologies) หากไม่มีไบนารี FST ที่คอมไพล์แล้วสำหรับภาษาหนึ่ง ตาราง UniMorph สามารถใช้เป็นฐานข้อมูลค้นหาแบบ static ได้
* **[National Research Council Canada (NRC)](https://nrc-digital-repository.canada.ca/):** เสนอเครื่องมือสำหรับภาษาพื้นเมืองของแคนาดา รวมถึง **Uqailaut** ตัววิเคราะห์สัณฐานวิทยา FST สำหรับภาษา Inuktitut และ **Nunavut Hansard Parallel Corpus** ขนาดใหญ่ (คู่ประโยคภาษาอังกฤษ-Inuktitut ที่จัดแนวแล้ว 1.3 ล้านคู่)

### คลังข้อมูล EdTeKLA

[กลุ่มวิจัย EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) (ที่ UAlberta เช่นกัน) ได้รวบรวมคลังข้อมูลภาษา Plains Cree จากสื่อการศึกษา การถอดเสียง และแหล่งข้อมูลชุมชน ชุดข้อมูลการประเมิน champollion [EDTeKLA Dev v1](/docs/leaderboard/datasets) ได้มาจากงานนี้ ภายใต้ลิขสิทธิ์ [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

### แนวทางอื่น ๆ ที่ผู้คนได้ลองหรืออาจลอง

leaderboard ไม่ผูกติดกับวิธีการใดวิธีการหนึ่ง ต่อไปนี้คือกลยุทธ์ที่ได้รับการสำรวจหรือเสนอสำหรับ MT ที่มีทรัพยากรน้อย ซึ่งสามารถส่งได้ทั้งหมด:

| แนวทาง | วิธีการทำงาน | ข้อดี | ข้อเสีย |
|----------|-------------|------|------|
| **[Coached LLM prompting](/docs/tutorials/coached-llm-prompting)** | ฉีดกฎไวยากรณ์ พจนานุกรม และคู่ตัวอย่างเข้าไปใน system prompt | ทำซ้ำได้เร็ว ไม่ต้องการการฝึก | เพดานคุณภาพถูกจำกัดด้วยความรู้พื้นฐานของ LLM |
| **[Few-shot prompting](/docs/tutorials/few-shot-prompting)** | รวมการแปลที่ตรวจสอบแล้วเป็นตัวอย่าง in-context | ดีสำหรับสไตล์ที่สม่ำเสมอ | context window เล็ก; ตัวอย่างต้องไม่มาจากข้อมูล eval |
| **[FST-gated pipeline](/docs/tutorials/fst-gated-pipeline)** | LLM สร้าง → FST ตรวจสอบ → ปฏิเสธและลองใหม่สำหรับสัณฐานวิทยาที่ไม่ถูกต้อง | รับประกันความถูกต้องทางสัณฐานวิทยา | ต้องการโครงสร้างพื้นฐาน FST; การวนซ้ำเพิ่ม latency และต้นทุน |
| **[Dictionary lookup + LLM](/docs/tutorials/dictionary-augmented-llm)** | บังคับใช้คำที่รู้จักจากพจนานุกรมสองภาษา ให้ LLM จัดการส่วนที่เหลือ | ลดการสร้างข้อมูลเท็จสำหรับคำที่รู้จัก | ความครอบคลุมของพจนานุกรมไม่สมบูรณ์เสมอ |
| **[Fine-tuned model](/docs/tutorials/fine-tuned-model)** | Fine-tune โมเดลแบบเปิด (Llama, Mistral) บนข้อความคู่ขนาน — แต่ไม่ใช่บนข้อมูล eval | อาจมีคุณภาพสูงสุด | ต้องการคลังข้อมูลคู่ขนาน (หายาก); แพง; ความเสี่ยง overfitting |
| **[Chained models](/docs/tutorials/chained-models)** | โมเดล A สร้างการแปลคร่าว ๆ → โมเดล B แก้ไข → โมเดล C ให้คะแนน | สามารถรวมจุดแข็งของผู้เชี่ยวชาญ | ซับซ้อน; ช้า; แพง |
| **[Rule-based + LLM hybrid](/docs/tutorials/rule-based-hybrid)** | ใช้กฎภาษาศาสตร์สำหรับรูปแบบที่รู้จัก LLM สำหรับส่วนที่เหลือ | แม่นยำในที่ที่กฎใช้ได้ | ต้องการความเชี่ยวชาญทางภาษาศาสตร์เชิงลึก |
| **[Back-translation augmentation](/docs/tutorials/back-translation)** | สร้างข้อมูลคู่ขนานสังเคราะห์โดยการแปล Cree→อังกฤษ แล้วฝึกในทิศทางกลับ | ขยายข้อมูลการฝึกได้ถูก | ขยายข้อผิดพลาดของโมเดลที่มีอยู่ |
| **[Evolutionary approach](/docs/tutorials/evolutionary-approach)** | สร้างการแปลที่เป็นตัวเลือก ให้คะแนน กลายพันธุ์ผู้ทำงานได้ดีที่สุด ทำซ้ำ | สามารถค้นพบวิธีแก้ปัญหาใหม่; ทำแบบขนานได้ | ใช้ทรัพยากรการคำนวณมาก; ต้องการฟังก์ชัน fitness ที่ดี |
| **[Partial translation](/docs/tutorials/partial-translation)** | แปลตัวอย่างที่เป็นตัวแทนด้วยมือ พิสูจน์ว่าวิธีของคุณตรงกับสไตล์ของคุณ แล้วแปลส่วนที่เหลือด้วยเครื่อง | รวมคุณภาพของมนุษย์กับขนาดของเครื่อง | ต้องการความพยายามของมนุษย์ในตอนแรก |
| **Manual JSON / exam grading** | สร้างไฟล์ JSON ชุดข้อมูลด้วยมือเพื่อทดสอบคำตอบของนักเรียนในการสอบภาษา หรือให้คะแนนชุดการแปลของมนุษย์เทียบกับมาตรฐานทอง | ไม่ต้องการ ML เลย; ใช้ได้สำหรับการศึกษาและ QA | ไม่สามารถขยายขนาดสำหรับความต้องการการแปลที่ต่อเนื่อง |

### มันแค่ JSON

harness รับ JSON เข้าและให้คะแนน JSON ออก [รูปแบบชุดข้อมูล](/docs/leaderboard/datasets) นั้นเรียบง่าย:

```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

คุณสามารถสร้างสิ่งนี้ด้วยมือ ส่งออกจากสเปรดชีต หรือสร้างจากคลังข้อมูล ครูสอนภาษาสามารถใช้มันเพื่อให้คะแนนการแปลของนักเรียน หน่วยงานแปลสามารถใช้มันเพื่อเปรียบเทียบนักแปลอิสระ ห้องปฏิบัติการวิจัยสามารถใช้มันเพื่อเปรียบเทียบสถาปัตยกรรมโมเดล harness ไม่สนใจว่า JSON มาจากไหน — มันแค่ให้คะแนน

และเนื่องจากกรอบการ deploy ในการผลิตใช้ plugin interface เดียวกัน วิธีการที่ได้คะแนนดีใน harness จะ deploy ไปยังเว็บไซต์ของคุณด้วยการเปลี่ยน config เพียงครั้งเดียว **พิสูจน์แล้วใช้งาน**

ความเป็นไปได้นั้นไม่มีที่สิ้นสุดจริง ๆ **หากคุณมีไอเดีย สร้างมัน รัน harness และส่งคะแนนของคุณ**

---

## champollion เข้ามาเกี่ยวข้องอย่างไร

champollion ให้ชั้นโครงสร้างพื้นฐาน — คุณนำวิธีการมาเอง

### ระบบ coaching

วิธี `llm-coached` ของ champollion ช่วยให้คุณฉีดความรู้ทางภาษาศาสตร์เข้าไปใน LLM prompt โดยตรง:

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

ข้อมูล coaching ถูกฉีดเข้าไปใน LLM prompt ทุกรายการสำหรับคู่ `en:crk` ทำให้โมเดลมีบริบทภาษาศาสตร์ที่มีโครงสร้างซึ่งมันจะไม่มีในกรณีอื่น ดู [Coaching Data](https://champollion.dev/docs/concepts/coaching-data) สำหรับข้อกำหนดฉบับสมบูรณ์

### Registers

register คือส่วนหนึ่งของ system prompt ที่กำหนดทิศทางของโทน ความเป็นทางการ และแบบแผนการเขียน champollion มาพร้อมกับ register ภาษา Plains Cree หนึ่งรายการ:

```
nêhiyawêwin (Plains Cree). Use SRO (Standard Roman Orthography) as the working
script. Output will be converted to Syllabics via deterministic converter.
Professional register appropriate for educational and community contexts.
```

คุณสามารถแทนที่สิ่งนี้ใน config ของคุณเพื่อทดลองกับกลยุทธ์การ prompt ที่แตกต่างกัน:

```json title="champollion.config.json"
{
  "languages": {
    "crk": {
      "register": "Casual Plains Cree (Y-dialect). Use SRO. Prefer everyday vocabulary over formal or archaic terms. Address the reader directly."
    }
  }
}
```

register ที่แตกต่างกันสร้างสไตล์การแปลที่แตกต่างกัน — และคะแนนที่แตกต่างกันบน leaderboard การส่งแต่ละครั้งบันทึก register และ system prompt ที่แน่นอนที่ใช้ (เป็น SHA-256 hash ใน [run card](/docs/specifications/run-card)) ดังนั้นการทดลองจึงทำซ้ำได้

### การแปลงสคริปต์

Plains Cree เขียนด้วยสองสคริปต์: **Standard Roman Orthography (SRO)** และ **Canadian Aboriginal Syllabics** pipeline ของ champollion:

1. LLM แปลเป็น SRO (ฐาน Latin ซึ่ง LLM จัดการได้ดีกว่า)
2. quality gate ตรวจสอบผลลัพธ์ SRO
3. ตัวแปลงแบบ deterministic แปลง SRO → Syllabics
4. ข้อความที่แปลงแล้วถูกเขียนลงดิสก์

ตัวแปลงจัดการ diacritics SRO ทั้งหมด (ê, î, ô, â สำหรับสระยาว) และแมปไปยังอักขระ syllabic ที่ถูกต้อง ดู [Script Converters](https://champollion.dev/docs/concepts/script-converters) สำหรับรายละเอียดทางเทคนิค

### วงจรการประเมิน

[eval harness](/docs/specifications/harness) รันวิธีการของคุณกับชุดข้อมูลการประเมินและสร้าง [run card](/docs/specifications/run-card) ที่มีคะแนน:

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

แฟล็ก `--condition` คือป้ายกำกับที่คุณเลือก มันปรากฏบน leaderboard เพื่อให้ผู้คนเห็นว่าคุณใช้กลยุทธ์ prompt ใด harness บันทึก system prompt ฉบับสมบูรณ์ใน run card ดังนั้นแนวทางที่แน่นอนของคุณจึงทำซ้ำได้

:::tip ทดลองได้อย่างอิสระ ส่งผลงานที่ดีที่สุดของคุณ
harness ถูกออกแบบมาสำหรับการทำซ้ำอย่างรวดเร็ว รันการทดลองหลายสิบครั้งด้วยโมเดล ข้อมูล coaching register และเงื่อนไขที่แตกต่างกัน ส่งไปยัง leaderboard เมื่อคุณมีสิ่งที่คุณภูมิใจเท่านั้น
:::

---

## หลักการ OCAP

champollion ถูกออกแบบมาเพื่อสนับสนุนอำนาจอธิปไตยข้อมูลของชนพื้นเมือง [หลักการ OCAP](https://fnigc.ca/ocap-training/) (Ownership, Control, Access, Possession) เป็นแนวทางในวิธีที่เราเข้าถึงเทคโนโลยีภาษาสำหรับชุมชนพื้นเมือง:

| หลักการ | วิธีที่ champollion สนับสนุน |
|-----------|------------------------|
| **Ownership** | ชุมชนภาษาเป็นเจ้าของข้อมูลภาษาของตน champollion ไม่เคยโทรกลับบ้านหรือส่งข้อมูลไปยังเซิร์ฟเวอร์ของเรา |
| **Control** | [วิธี API](https://champollion.dev/docs/guides/serving-a-method) ช่วยให้ชุมชนโฮสต์ pipeline การแปลของตนเอง — เราให้ interface พวกเขาควบคุมการ implement |
| **Access** | ชุมชนตัดสินใจว่าใครสามารถใช้วิธีการของตนได้ API สามารถกั้นด้วยการยืนยันตัวตน |
| **Possession** | ข้อมูลการแปลทั้งหมดอยู่ในระบบไฟล์ของโครงการของคุณ [ระบบ provenance](https://champollion.dev/docs/concepts/security) ติดตามว่าการแปลแต่ละรายการมาจากไหน |

สถาปัตยกรรม plugin หมายความว่าชุมชนสามารถสร้างวิธีการที่รวมความรู้ศักดิ์สิทธิ์หรือจำกัดภายใน เปิดเผยเฉพาะ API การแปล และรักษาการควบคุมทรัพยากรภาษาของตนอย่างสมบูรณ์

---

## วิสัยทัศน์: สิ่งที่จะเกิดขึ้นต่อไป

Plains Cree คือเป้าหมายแรก เมื่อ pipeline ได้รับการตรวจสอบและชุมชนพอใจกับคุณภาพแล้ว สถาปัตยกรรมเดียวกันจะขยายไปยังภาษาโพลีซินเทติกอื่น ๆ ที่มีโครงสร้างพื้นฐาน FST:

- **ภาษา Algonquian อื่น ๆ**: Woods Cree, Swampy Cree, Ojibwe, Blackfoot
- **ภาษา Inuit**: Inuktitut, Inuinnaqtun (ซึ่งใช้สคริปต์ syllabic เช่นกัน)
- **ตระกูลภาษาอื่น ๆ**: ภาษาใดก็ตามที่มีตัววิเคราะห์ FST สามารถใช้ FST-gated pipeline ได้

leaderboard มีขอบเขตตามคู่ภาษา เมื่อชุดข้อมูลการประเมินใหม่ถูกมีส่วนร่วมโดยชุมชนภาษา แทร็ก leaderboard ใหม่จะเปิดโดยอัตโนมัติ

**นี่คือคำเชิญแบบเปิด** หากคุณทำงานกับภาษาที่มีทรัพยากรน้อย — ในฐานะนักวิจัย สมาชิกชุมชน นักศึกษา หรือเพียงแค่คนที่ใส่ใจ — champollion มอบเครื่องมือให้คุณสร้างสิ่งที่เป็นจริง วัดผลอย่างซื่อสัตย์ และแบ่งปันกับโลก [Method Leaderboard](https://champollion.dev/leaderboard) กำลังรอการส่งผลงานของคุณ

---

## ดูเพิ่มเติม

- **[Method Leaderboard](https://champollion.dev/leaderboard)** — ส่งคะแนนของคุณและดูว่าวิธีการต่าง ๆ เปรียบเทียบกันอย่างไร
- **[MT Evaluation](/docs/leaderboard/rules)** — สิ่งที่ทำให้วิธีการดี สิ่งที่ถูกตัดสิทธิ์
- **[Eval Harness](/docs/specifications/harness)** — วิธีการรันการทดลอง
- **[Evaluation Datasets](/docs/leaderboard/datasets)** — EDTeKLA Dev v1 และ FLORES+
- **[Coaching Data](https://champollion.dev/docs/concepts/coaching-data)** — วิธีการจัดโครงสร้างความรู้ทางภาษาศาสตร์สำหรับ LLM
- **[Script Converters](https://champollion.dev/docs/concepts/script-converters)** — pipeline SRO→Syllabics
- **[Serving a Method via API](https://champollion.dev/docs/guides/serving-a-method)** — การโฮสต์การแปลที่ควบคุมโดยชุมชน
- **[ALTLab](https://altlab.artsrn.ualberta.ca/)** — Alberta Language Technology Lab
- **[EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/)** — กลุ่มวิจัย Educational Technology, Knowledge & Language
- **[itwêwina dictionary](https://itwewina.altlab.app/)** — พจนานุกรม Plains Cree–อังกฤษที่ขับเคลื่อนด้วย FST