---
sidebar_position: 5
title: "支持低资源语言"
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
# 支持低资源语言

> **执行摘要。** 为低资源和多综合语言构建机器翻译的综合指南。涵盖这些语言为何困难（形态复杂性、数据稀疏、幻觉），现有计算资源（ALTLab FST、GiellaLT、Apertium、UniMorph、EdTeKLA），10+ 种方法策略、champollion 教练系统和评估循环。如果您想为服务不足的语言贡献一种方法，请从这里开始。

:::info 状态：积极开发中
平原克里语（nêhiyawêwin）支持目前正在开发中。此处描述的工具、评估工具和排行榜是真实的，今天可用，但克里语翻译管道尚未发布。发布时，这将作为其他具有 FST 基础设施的多综合语言和低资源语言的蓝图。
:::

## 未解决的问题

谷歌翻译支持约 130 种语言。Meta 的 OMT-1600（2026 年 3 月）声称覆盖 1,600 种——有史以来最大的 MT 系统。但对于约 1,300 种处于最低资源层级的语言，质量低于可用阈值，训练数据主要由圣经文本组成，模型权重不可下载，也没有独立评估或社区治理框架。对于剩余约 5,400 种语言，没有预训练模型能产生任何输出。

格局已发生重大转变——大科技公司现在正在投资低资源语言覆盖。但覆盖不等于质量，没有独立验证的质量不等于信任。低资源语言需要的不仅仅是声称覆盖它们的模型——它们需要具有形态验证的独立评估、社区策划的语料库和尊重主权的治理框架。

**champollion 就是为了改变这一点而构建的。**

[方法排行榜](https://champollion.dev/leaderboard)是一个开放挑战：为服务不足的语言构建最佳翻译方法，用可重现的评估证明它，并声称最高分数。世界上任何人都可以贡献——语言学家、ML 研究人员、社区语言工作者、学生、爱好者。这个问题未解决。基础设施已就位。排行榜在等待。

---

## 为什么这很困难：多综合形态

大多数商业 MT 系统是为英语、法语和中文等语言设计的——这些语言中单词相对较短，句子由离散标记构建。但许多土著语言，包括平原克里语，是**多综合的**：单个单词可以编码英语表达为整个句子的内容。

### 克里语示例

考虑平原克里语单词：

> **ê-kî-nitawi-kîskinwahamâkosiyân**
> *"when I went to school"*

那是**一个单词**。它编码时态（过去）、方向（去）、词根（学习）、语态（被动/反身）和人称（第一人称单数）。主要在英语上训练的 LLM 对这种形态密度没有直觉。

挑战复合：

| 挑战 | 含义 |
|-----------|--------------|
| **形态复杂性** | 单个动词词根可以通过前缀、后缀和环缀生成数千种有效的屈折形式 |
| **有生/无生区分** | 名词在语法上是有生的或无生的——这影响动词共轭、指示词和复数化。分类不总是遵循生物有生性（*askiy* "地球"是有生的；*maskisin* "鞋"也是有生的） |
| **显著性** | 第三人称引用按接近度/显著性排序。"近指"和"远指"区分在英语中没有等价物 |
| **数据稀疏** | LLM 看到的平原克里语文本很少。他们看到的可能混合方言（Y 方言、TH 方言）或正字法（SRO vs. 音节文字） |
| **弱商业基线** | OMT-1600 在 R1（极低资源）层级包含 CRK，使用圣经领域训练和标准 BPE 分词。谷歌翻译不支持克里语。具有形态指标的独立评估是使这些基线有意义的原因。 |

多综合语言的翻译仍然是一个**开放研究问题**——OMT-1600 包含多综合语言，但使用标准 BPE 分词（256K 词汇表），没有形态意识，意味着它将组合词分解成无意义的字节片段。

---

## 先前工作：人们如何处理这个问题

### ALTLab FST

平原克里语最重要的计算资源是由阿尔伯塔大学[阿尔伯塔语言技术实验室（ALTLab）](https://altlab.artsrn.ualberta.ca/)与挪威北极大学[Giellatekno](https://giellatekno.uit.no/)合作开发的**有限状态转换器（FST）**。

ALTLab FST 是一个**形态分析器和生成器**：给定一个屈折的克里语单词，它可以将其分解为其词根和语法标记，给定词根加标记，它可以生成正确的屈折形式。这是确定性的——没有神经网络、没有幻觉、没有概率。如果 FST 接受一个单词，那个单词在形态上是有效的。

这就是为什么 champollion 排行榜将 **FST 接受率**作为指标进行跟踪。产生 FST 拒绝的单词的翻译方法正在产生形态上无效的克里语——无论 chrF++ 分数说什么。

**关键 ALTLab 资源：**
- [itwêwina](https://itwewina.altlab.app/) ——由 FST 驱动的智能平原克里语-英语词典
- [Morphodict](https://github.com/UAlbertaALTLab/morphodict) ——开源形态感知词典平台
- [crk-db](https://github.com/UAlbertaALTLab/crk-db) ——平原克里语词汇数据库
- [21st Century Tools for Indigenous Languages](https://21c.tools/) ——更广泛的项目背景

### 全球 FST 和形态注册表

平原克里语不是唯一具有高质量 FST 基础设施的语言。如果您想为其他低资源或形态复杂的语言开发翻译管道，您可以利用这些已建立的全球中心：

* **[GiellaLT / Giellatekno](https://giellalt.github.io/)（挪威北极大学）：** 最大的开源 FST 形态分析器和生成器存储库，覆盖 100 多种语言。重点领域包括萨米语言（`sme`、`smj`、`sma` 等）、乌拉尔语言（科米语、厄尔茨亚语、乌德穆尔特语等）和其他少数民族/土著语言。他们在其 [GitHub 组织](https://github.com/giellalt/)中托管公共处理文本语料库（`corpus-xxx`）。
* **[Apertium 项目](https://www.apertium.org/)：** 开源基于规则的机器翻译平台。Apertium 维护高度优化的 FST 形态分析器（使用 `lttoolbox` 和 `hfst`）和数十种语言的双语词典，包括大量突厥语言（哈萨克语、鞑靼语、吉尔吉斯语等）和少数欧洲语言。所有资源都在 [Apertium 的 GitHub](https://github.com/apertium) 上公开。
* **[UniMorph（通用形态学）](https://unimorph.github.io/)：** 为 150 多种语言提供标准化形态范式的协作项目。数据集托管在 Hugging Face 的 [unimorph/universal_morphologies](https://huggingface.co/datasets/unimorph/universal_morphologies)。如果编译的 FST 二进制文件对某种语言不可用，UniMorph 表可用作静态数据库查找门。
* **[加拿大国家研究委员会（NRC）](https://nrc-digital-repository.canada.ca/)：** 为加拿大土著语言提供工具，包括 **Uqailaut** 因纽特语 FST 形态分析器和大规模 **Nunavut Hansard 平行语料库**（130 万对对齐的英语-因纽特语句子对）。

### EdTeKLA 语料库

[EdTeKLA 研究小组](https://spaces.facsci.ualberta.ca/edtekla/)（也在阿尔伯塔大学）从教育材料、音频转录和社区来源组装了平原克里语语料库。champollion 评估数据集 [EDTeKLA Dev v1](/docs/leaderboard/datasets) 源自这项工作，许可证为 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)。

### 人们尝试过或可以尝试的其他方法

排行榜是方法无关的。以下是为低资源 MT 探索或提议的策略，任何这些都可以提交：

| 方法 | 工作原理 | 优点 | 缺点 |
|----------|-------------|------|------|
| **[教练 LLM 提示](/docs/tutorials/coached-llm-prompting)** | 将语法规则、词典和示例对注入系统提示 | 快速迭代，无需训练 | 质量上限受 LLM 基础知识限制 |
| **[少样本提示](/docs/tutorials/few-shot-prompting)** | 包括已验证的翻译作为上下文示例 | 对一致的风格有好处 | 小上下文窗口；示例不得来自评估数据 |
| **[FST 门控管道](/docs/tutorials/fst-gated-pipeline)** | LLM 生成 → FST 验证 → 拒绝并重试无效形态 | 保证形态有效性 | 需要 FST 基础设施；重试循环增加延迟和成本 |
| **[词典查找 + LLM](/docs/tutorials/dictionary-augmented-llm)** | 强制已知术语来自双语词典，让 LLM 处理其余部分 | 减少已知术语的幻觉 | 词典覆盖总是不完整的 |
| **[微调模型](/docs/tutorials/fine-tuned-model)** | 在平行文本上微调开源模型（Llama、Mistral）——只是不在评估数据上 | 可能的最高质量 | 需要平行语料库（稀缺）；昂贵；过拟合风险 |
| **[链式模型](/docs/tutorials/chained-models)** | 模型 A 生成粗翻译 → 模型 B 后编辑 → 模型 C 评分 | 可以结合专家优势 | 复杂；缓慢；昂贵 |
| **[基于规则 + LLM 混合](/docs/tutorials/rule-based-hybrid)** | 对已知模式使用语言规则，对其他所有内容使用 LLM | 规则适用的地方精确 | 需要深厚的语言学专业知识 |
| **[回译增强](/docs/tutorials/back-translation)** | 通过翻译克里语→英语生成合成平行数据，然后在反向上训练 | 廉价扩展训练数据 | 放大现有模型错误 |
| **[进化方法](/docs/tutorials/evolutionary-approach)** | 生成候选翻译、评分、变异最佳表现者、重复 | 可以发现新颖解决方案；可并行化 | 计算昂贵；需要好的适应度函数 |
| **[部分翻译](/docs/tutorials/partial-translation)** | 手动翻译代表性样本，证明您的方法在其上匹配您的风格，然后自动翻译剩余的大部分 | 结合人工质量和机器规模 | 需要初始人工工作 |
| **手动 JSON / 考试评分** | 手工制作数据集 JSON 文件以测试学生对语言考试的答案，或根据黄金标准对一批人工翻译进行评分 | 无需 ML；适用于教育和 QA | 不适合持续翻译需求 |

### 它只是 JSON

工具接受 JSON 输入并输出 JSON 评分。[数据集格式](/docs/leaderboard/datasets)很简单：

```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

您可以手工构造这个。您可以从电子表格导出它。您可以从语料库生成它。语言教师可以用它来评分学生翻译。翻译机构可以用它来评估自由职业者。研究实验室可以用它来比较模型架构。工具不关心 JSON 来自哪里——它只是评分。

而且因为生产部署框架采用相同的插件接口，在工具中评分良好的方法可以通过一个配置更改部署到您的网站。**证明它并使用它。**

可能性真的是无限的。**如果您有想法，构建它，运行工具，并提交您的分数。**

---

## champollion 如何适应

champollion 提供基础设施层——您提供方法。

### 教练系统

champollion 的 `llm-coached` 方法让您直接将语言知识注入 LLM 提示：

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

教练数据被注入 `en:crk` 对的每个 LLM 提示，为模型提供它本来不会有的结构化语言背景。有关完整规范，请参阅[教练数据](https://champollion.dev/docs/concepts/coaching-data)。

### 寄存器

寄存器是系统提示的一部分，引导语调、正式性和正字法约定。champollion 附带一个平原克里语寄存器：

```
nêhiyawêwin (Plains Cree). Use SRO (Standard Roman Orthography) as the working
script. Output will be converted to Syllabics via deterministic converter.
Professional register appropriate for educational and community contexts.
```

您可以在配置中覆盖这个以尝试不同的提示策略：

```json title="champollion.config.json"
{
  "languages": {
    "crk": {
      "register": "Casual Plains Cree (Y-dialect). Use SRO. Prefer everyday vocabulary over formal or archaic terms. Address the reader directly."
    }
  }
}
```

不同的寄存器产生不同的翻译风格——以及排行榜上的不同分数。每个提交都记录使用的确切寄存器和系统提示（作为 [运行卡](/docs/specifications/run-card)中的 SHA-256 哈希），因此实验是可重现的。

### 脚本转换

平原克里语用两种脚本书写：**标准罗马正字法（SRO）**和**加拿大土著音节文字**。champollion 的管道：

1. LLM 翻译成 SRO（基于拉丁文，LLM 处理得更好）
2. 质量门验证 SRO 输出
3. 确定性转换器将 SRO → 音节文字转换
4. 转换后的文本写入磁盘

转换器处理所有 SRO 变音符号（ê、î、ô、â 表示长元音）并将其映射到正确的音节字符。有关技术细节，请参阅[脚本转换器](https://champollion.dev/docs/concepts/script-converters)。

### 评估循环

[评估工具](/docs/specifications/harness)针对评估数据集运行您的方法并生成评分的[运行卡](/docs/specifications/run-card)：

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

`--condition` 标志是您选择的标签。它出现在排行榜上，以便人们可以看到您使用的提示策略。工具在运行卡中记录完整的系统提示，因此您的确切方法是可重现的。

:::tip 自由实验，提交您最好的
工具设计用于快速迭代。使用不同的模型、教练数据、寄存器和条件运行数十个实验。仅当您有值得骄傲的东西时才提交到排行榜。
:::

---

## OCAP 原则

champollion 旨在支持土著数据主权。[OCAP 原则](https://fnigc.ca/ocap-training/)（所有权、控制权、访问权、占有权）指导我们如何处理土著社区的语言技术：

| 原则 | champollion 如何支持它 |
|-----------|------------------------|
| **所有权** | 语言社区拥有其语言数据。champollion 从不回传或将数据传输到我们的服务器 |
| **控制** | [API 方法](https://champollion.dev/docs/guides/serving-a-method)允许社区托管自己的翻译管道——我们提供接口，他们控制实现 |
| **访问** | 社区决定谁可以使用他们的方法。API 可以在身份验证后面进行门控 |
| **占有** | 所有翻译数据保留在您的项目文件系统中。[来源系统](https://champollion.dev/docs/concepts/security)跟踪每个翻译的来源 |

插件架构意味着社区可以构建一个在内部包含神圣或受限知识的方法，仅公开翻译 API，并对其语言资源保持完全控制。

---

## 愿景：接下来会发生什么

平原克里语是第一个目标。一旦管道得到验证并且社区对质量满意，相同的架构扩展到其他具有 FST 基础设施的多综合语言：

- **其他阿尔冈昆语言**：伍兹克里语、沼泽克里语、奥吉布瓦语、黑脚语
- **因纽特语言**：因纽特语、因纽因纳克顿语（也使用音节文字）
- **其他语言族**：任何具有 FST 分析器的语言都可以使用 FST 门控管道

排行榜是语言对范围的。随着语言社区贡献新的评估数据集，新的排行榜轨道自动打开。

**这是一个开放邀请。** 如果您使用低资源语言——作为研究人员、社区成员、学生或只是关心的人——champollion 为您提供工具来构建真实的东西、诚实地测量它，并与世界分享。[方法排行榜](https://champollion.dev/leaderboard)在等待您的提交。

---

## 另见

- **[方法排行榜](https://champollion.dev/leaderboard)** ——提交您的分数并查看方法如何比较
- **[MT 评估](/docs/leaderboard/rules)** ——什么是好方法，什么会被取消资格
- **[评估工具](/docs/specifications/harness)** ——如何运行实验
- **[评估数据集](/docs/leaderboard/datasets)** ——EDTeKLA Dev v1 和 FLORES+
- **[教练数据](https://champollion.dev/docs/concepts/coaching-data)** ——如何为 LLM 构造语言知识
- **[脚本转换器](https://champollion.dev/docs/concepts/script-converters)** ——SRO→音节文字管道
- **[通过 API 提供方法](https://champollion.dev/docs/guides/serving-a-method)** ——托管社区控制的翻译
- **[ALTLab](https://altlab.artsrn.ualberta.ca/)** ——阿尔伯塔语言技术实验室
- **[EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/)** ——教育技术、知识和语言研究小组
- **[itwêwina 词典](https://itwewina.altlab.app/)** ——FST 驱动的平原克里语-英语词典