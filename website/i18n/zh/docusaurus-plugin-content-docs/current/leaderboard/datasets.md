---
sidebar_position: 3
title: "评估数据集"
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
# 评估数据集

> **执行摘要。** 本页描述了可用于基准测试的评估数据集，包括语料库条目架构、难度等级（1–5）和来源要求。当前可用：EDTeKLA Dev v1（平原克里语，共548个条目：486个教科书 + 62个黄金标准）和 FLORES+ Devtest（39种语言，每种1,012个条目）。

数据集是测试框架运行的固定目标。每个数据集是一个 JSON 文件，包含源→目标对及黄金标准参考。测试框架根据这些参考对模型输出进行评分——它永远不会修改它们。

:::danger 不要在评估数据上进行训练

⚠️ **这些数据集仅用于评估。** 在评估数据上进行训练、微调、少样本提示或以其他方式接触评估数据的方法将产生人为夸大的分数，并将被**从排行榜中取消资格。**

使用单独的语料库进行训练。评估集必须在模型开发期间保持未见过。
:::

---

## 数据集格式

每个数据集都遵循相同的 JSON 架构：

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

:::info 规范架构
[基准规范](/docs/specifications/benchmark)定义了规范语料库和条目架构。本页记录了可用数据集以及如何创建新数据集。
:::

### 顶级 `dataset` 块

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `id` | `string` | 唯一的数据集标识符（用于运行卡和排行榜） |
| `version` | `string` | 语义版本。增加此版本会使之前的运行卡比较失效 |
| `language_pair` | `string` | 显示标签（例如，`EN→CRK`） |
| `description` | `string` | 可选。人类可读的摘要 |
| `source_language` | `string` | BCP 47 源语言代码 |
| `target_language` | `string` | BCP 47 目标语言代码 |
| `created` | `string` | ISO 8601 创建日期 |
| `license` | `string` | SPDX 许可证标识符 |
| `provenance` | `string[]` | 在条目中使用的来源标签列表 |

### 条目字段

| 字段 | 类型 | 必需 | 描述 |
|-------|------|----------|-------------|
| `id` | `integer` | ✅ | 语料库内的唯一条目标识符 |
| `source` | `string` | ✅ | 要翻译的源文本 |
| `reference` | `string` | ✅ | 黄金标准参考翻译 |
| `difficulty` | `integer` | ✅ | 难度等级 1–5（见下文） |
| `provenance` | `string` | ✅ | 此条目的来源（例如，`gold_standard`、`textbook`、`elicited`） |
| `register` | `string` | ✅ | 寄存器/正式程度（例如，`conversational`、`formal`、`ceremonial`） |
| `context` | `string` | ✅ | 交际功能（例如，`greeting`、`declaration`、`instruction`） |
| `notes` | `string` | ❌ | 为人类审阅者提供的可选上下文 |
| `morphological_analysis` | `string` | ❌ | 黄金标准形态学分解 |
| `variant_class` | `string` | ❌ | 分组可接受翻译变体的类标签 |

---

## 可用数据集

### EDTeKLA 开发集 v1

为英语→平原克里语 (SRO) 翻译构建的第一个评估数据集。由[阿尔伯塔大学](https://spaces.facsci.ualberta.ca/edtekla/) EdTeKLA 研究小组创建。

| 属性 | 值 |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **版本** | `1.0` |
| **语言对** | EN → CRK（平原克里语，SRO 正字法） |
| **条目数** | 共548个（486个教科书 + 62个黄金标准）。规范开发语料库是 `textbook_dev.json`（436个条目——来自486个总数的完整教科书开发分割：436个开发 + 50个保留测试） |
| **难度分布** | 简单、中等、困难 |
| **来源** | `gold_standard`（由使用者验证）、`textbook`（已发布的教育材料） |
| **许可证** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |

**它测试的内容：**

- 基本问候和常见短语
- 名词生命性和显著性
- 动词在人称和时态中的变位
- 位置构式
- 所有格范式
- 复杂句子结构

:::tip 语料库结构
完整的 EdTeKLA 集合有548个精选条目：486个来自教科书语料库（436个开发 + 50个保留），62个来自 itwêwina 黄金标准。规范开发语料库是 `textbook_dev.json`，包含436个条目——完整的教科书开发分割。每个条目都由流利使用者验证或来自已发布的克里语教科书。一个较小的、高质量的、经过验证的黄金标准数据集比一个大的、嘈杂的数据集更有用——特别是对于低资源语言，其中"足够接近"的翻译通常在形态上是无效的。
:::

---

## 创建新数据集

要为新的语言对或领域创建数据集：

### 1. 构建 JSON

遵循[数据集格式](#数据集格式)架构。每个条目必须有 `source`、`reference`、`difficulty`、`provenance`、`register` 和 `context`。

### 2. 分配唯一 ID

使用描述性 slug：`{project}-{split}-v{version}`（例如，`edtekla-dev-v1`、`quechua-test-v1`）。

### 3. 验证黄金标准

每个 `reference` 值必须由流利使用者验证或来自已发布的、经过同行评审的资源。机器生成的参考会破坏评估的目的。

### 4. 设置难度等级

为每个条目分配一个整数难度级别：

| 等级 | 描述 | 示例 |
|------|-------------|----------|
| 1 — 基本词汇 | 单词、常见问候、数字 | "hello" → "tânisi" |
| 2 — 简单句子 | 主谓或 SVO、现在时 | "I see the dog" |
| 3 — 中等复杂性 | 过去/未来时、所有格、生命性 | "I saw his dog yesterday" |
| 4 — 复杂形态 | 显著性、被动语态、连接顺序 | "the woman whose son went to the store" |
| 5 — 高级 | 多子句、正式寄存器、仪式、习语 | 具有寄存器适当语调的完整段落 |

### 5. 标记来源

每个条目应指示其来源。常见标签：

- `gold_standard` — 由流利使用者验证
- `textbook` — 来自已发布的教育材料
- `elicited` — 通过结构化引出会话产生
- `corpus` — 从平行语料库中提取

### 6. 验证文件

使用任何模型针对您的数据集运行测试框架，以验证 JSON 格式正确且所有必需字段都存在：

```bash
python eval/baseline_experiment.py --dataset path/to/your-dataset.json
```

测试框架将在缺少字段、重复索引或架构违规时出错。

### 7. 提交以供包含

针对[评估测试框架存储库](https://github.com/gamedaysuits/arena)打开拉取请求，将您的数据集文件放在 `data/` 目录中。包括您的验证方法和来源的文档。

---

## FLORES+ Devtest

由[开放语言数据倡议 (OLDI)](https://huggingface.co/datasets/openlanguagedata/flores_plus) 维护的广泛覆盖多语言基准。用于 champollion 的多模型前沿基准。

| 属性 | 值 |
|----------|-------|
| **ID** | `flores-plus-devtest` |
| **语言对** | EN → 39种语言（所有 champollion 注册的自然语言） |
| **条目数** | 每种语言1,012个句子 |
| **许可证** | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| **来源** | 原始 Meta FLORES-200，现由 OLDI 维护 |
| **位置** | 主 champollion 存储库中 `test/benchmark/fixtures/` 处的预提取固定装置 |

:::danger 仅用于评估
FLORES+ 仅用于评估。策展人明确要求**不将其用作训练数据**。确保其内容被排除在任何训练语料库之外。
:::

---

## 另请参阅

- [机器翻译评估](/docs/leaderboard/rules) — 评估框架和排行榜概述
- [评估测试框架](/docs/specifications/harness) — 如何针对这些数据集运行评估
- [运行卡规范](/docs/specifications/run-card) — 用于记录结果的 JSON 架构
- [方法排行榜](https://champollion.dev/leaderboard) — 实时基准分数
- [EdTeKLA 项目](https://spaces.facsci.ualberta.ca/edtekla/) — 克里语数据集背后的阿尔伯塔大学研究小组