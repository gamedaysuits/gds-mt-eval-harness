---
sidebar_position: 1
title: "提交方法"
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
# 提交方法

> **执行摘要。** 分步快速入门指南，用于向排行榜提交您的第一个基准测试运行。克隆工具，针对数据集运行它，查看您的运行卡，然后提交。如果您有 API 密钥，只需 10 分钟。

本指南将引导您完成向 MT Eval Arena 排行榜提交第一个基准测试运行的过程。

---

## 前置条件

- **Python 3.10+**
- **OpenRouter API 密钥**（或您的模型提供商的等效密钥）
- **翻译方法** — 任何能从源文本生成翻译的方法

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## 步骤 1：运行工具

工具针对标准化数据集对您的方法进行评分：

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| 标志 | 功能 |
|---|---|
| `--corpus` | 评估语料库的路径（`.json`、`.jsonl`、`.tsv`） |
| `--model` | 模型标识 — 短别名（例如 `gemini-pro`）或完整 OpenRouter ID |
| `--condition` | 您的方法的标签（显示在排行榜上） |
| `--temperature` | 采样温度（较低 = 更具确定性） |
| `--fst-retries` | 可选：FST 重试次数 |
| `--submit` | 自动将运行卡提交到排行榜 |

工具生成一个**运行卡** — 一个自包含的 JSON 文件，包含您的分数、数据集哈希、模型标识和一个将结果与确切实验配置绑定的密码学指纹。

---

## 步骤 2：查看您的运行卡

运行卡保存到 `results/`。在提交前检查您的：

```bash
cat results/your-run-card.json | python -m json.tool
```

要检查的关键字段：
- `scores.chrf_plus_plus` — 您的主要质量指标
- `scores.exact_match_rate` — 完美翻译的比例
- `scores.fst_acceptance_rate` — 形态学有效性（如果使用了 FST）
- `totals.total_cost_usd` — 运行的成本
- `fingerprint` — 实验的可重现性哈希

查看[运行卡规范](/docs/specifications/run-card)了解完整架构。

---

## 步骤 3：提交

### 自动提交

如果您在运行工具时传递了 `--submit`，您的运行卡已经上传。

### 手动提交

通过 API 提交任何运行卡：

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

或通过[排行榜 UI](https://champollion.dev/leaderboard) 上传。

---

## 接下来会发生什么

1. 您的提交被验证（数据集哈希、运行卡完整性）
2. 结果以**自基准测试**（信任等级 1）的形式出现在排行榜上
3. 要获得 **GDS Verified** 状态，请将您的方法作为可安装的插件提交，以便维护者可以重现您的结果
4. 对于土著语言方法：如果您的方法排名靠前，[所有权转移](/docs/sovereignty/ownership-transfer)流程开始

---

## 另请参阅

- [工具使用](/docs/specifications/harness) — 完整 CLI 参考
- [排行榜规则](/docs/leaderboard/rules) — 提交标准和反作弊政策
- [构建方法](/docs/specifications/methods) — TranslationMethod 协议
- [数据集](/docs/leaderboard/datasets) — 可用的评估数据集