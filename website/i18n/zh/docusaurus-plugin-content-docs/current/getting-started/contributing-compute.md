---
sidebar_position: 4
title: "贡献计算资源"
description: "捐献您的 tokens：使用您自己的 API 密钥从公共队列运行开放基准测试扫描，并发布结果。"
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
# 贡献计算资源

> **核心理念：** 排行榜上有空白方格 — (语言对、模型、条件) 的组合尚未被测量。我们维护一个公开的任务队列。你用自己的 API 密钥运行队列中的项目、发布报告，地图就会被填满。"捐赠 token"是对低资源 MT 评估的真实、可引用的贡献。

## 任务队列

实时队列发布在 [champollion.dev/queue.json](https://champollion.dev/queue.json)，还有一个零安装的终端查看器：

```bash
curl -fsSL champollion.dev/queue | bash
```

查看器仅*显示*开放项目及其确切的 `mt-eval run` 命令 — 它永远不会执行任何操作或消耗你的 token。每个项目包含：

- `run_command` — 可直接复制粘贴（获取语料库、运行测试框架）
- `est_cost_usd` 和 `est_basis` — 要么是我们自己对相同 (语料库、模型) 基准运行的**观测**成本，要么是从该模型的扫描平均成本每条目 × 语料库条目数**推断**的成本。基础信息在每个项目中说明；你的实际成本取决于运行时的提供商定价。
- `priority` — 未覆盖的语言对优先、低资源对优先（语料库大小作为代理）、朴素方法优先于指导方法、最便宜的模型优先。

**无声明锁定 — 选择任何开放项目。** 两个人运行同一项目是无害的（按设计）：每个运行卡都有指纹（对数据集哈希 + 模型 + 条件 + 系统提示的 SHA-256，[基准规范 §3.8](/docs/specifications/benchmark)），所以相同的运行在发布时会去重，相同配置的独立复现是有用的证据，而非浪费。

队列中的语料库是开发集分割、CC-BY 系列许可证（Tatoeba 衍生）且标记为 `do_not_train` — 它们是评估集，不是训练数据。非商业许可证和隔离的语料库被排除在开放队列之外。

## 设置（一次性）

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### 选择哪个提供商密钥？

测试框架通过 [OpenRouter](https://openrouter.ai/keys) 路由**所有**模型调用。一个 `OPENROUTER_API_KEY` 可以访问队列中的每个模型 — Anthropic Claude、OpenAI GPT 和 Google Gemini 模型 — 测试框架的成本追踪和定价快照来自相同的 OpenRouter 元数据，所以报告的运行成本与你的密钥被计费的金额相符。

如果你的额度在 Anthropic、OpenAI 或 Google 直接账户中：测试框架**目前不**接受直接提供商密钥。运行卡架构为将来支持这一点预留了 `api_provider` 字段，但目前每个测试框架运行都是 OpenRouter 运行。创建 OpenRouter 账户并为其充值（或在 OpenRouter 支持的地方关联你自己的提供商账户）是支持的路径。

### 代理快速路径

如果你使用 Claude Code 或其他编码代理，整个贡献就是一个提示：

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## 第 1 层 — 运行基准

每个队列项目的 `run_command` 都是自包含的。一个典型的例子：

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

运行会打印总成本，并将运行日志和评分报告写入 `eval/logs/`。然后发布：

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

发布通过 OAuth 登录（你的名字成为排行榜的署名）并更新运行卡。社区提交落在**自基准测试**信任层 — 明确标记为"由运行者提交"。这不是降级；这是信任模型的工作方式。运行卡包含重新运行你的确切配置所需的一切：数据集哈希、模型、条件、完整系统提示和成本。更高的层级（验证、社区验证）通过审查授予 — 见 [排行榜规则](/docs/leaderboard/rules)。

## 第 2 层 — 编写指导提示

测试框架对**指导**有一流的支持：用包含真实语言学知识的提示替换朴素系统提示。传递 `--coaching-file`（或 `--coaching "inline text"` 用于短提示），测试框架使用你的文本作为系统提示，在运行日志的来源块中记录**完整文本及其 SHA-256**，并将运行的条件标记为 **`coached`**（除非你显式设置 `--prompt`）— 所以提示编写是一个可重现、可归属的实验，两个不同的指导文件永远不会相互混淆，指导运行在排行榜上永远不会被误认为是朴素基准。

一个法罗语的实际例子，使用语言的[公开语言卡](https://champollion.dev/languages)中的类型学事实和词汇表条目：

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

（编写你自己的指导内容 — 上面的事实说明了*形式*：几条高影响力的语法规则、一个小的模型容易出错的术语词汇表、一条寄存器指令。[champollion.dev/languages](https://champollion.dev/languages) 的语言卡引用了你可以参考的类型学来源。）

用 `mt-eval compare <naive_log> <coached_log>` 与朴素基准进行比较、迭代，并发布你最好的运行。运行会自动以条件 `coached` 发布；如果你希望排行榜显示命名方法而不是通用标签，在发布时附加方法卡（发布流程提供向导）。在低资源对上仅用提示工程击败朴素基准是真实的、可发布的发现 — 见完整的 [指导 LLM 提示烹饪书](/docs/tutorials/coached-llm-prompting) 以获取设计指导。

## 第 3 层 — 构建方法

最雄心勃勃的贡献：实现 `TranslationMethod` 协议（`translate(entries, config)`）并基准测试一个实际系统，而不仅仅是提示。测试框架通过 `--method <plugin-dir>` 运行它，并在运行卡中嵌入你的方法卡。带有实际例子的模式：

- **[FST 门控管道](/docs/tutorials/fst-gated-pipeline)** — 每个候选词都由形态分析器检查；LLM 重新生成直到通过门。半确定性、形态学保证的输出。
- **[字典增强生成](/docs/tutorials/dictionary-augmented-llm)** — 在翻译时在双语词典中查找源术语并约束输出。
- [链式模型](/docs/tutorials/chained-models)、[少样本检索](/docs/tutorials/few-shot-prompting)、[回译](/docs/tutorials/back-translation)、[基于规则的混合](/docs/tutorials/rule-based-hybrid)…

方法声明一个**依赖类**（S/O/A1/A2/X — 见 [方法规范](/docs/specifications/methods#method-validity-and-dependency-classes)）描述它们需要什么来运行和转移：自包含的管道是 S 类；在运行时调用许可字典 API 的是 A2 类。诚实声明 — 类别决定了你的方法可以在哪里竞争，清单会被审计。

## 为什么这对排行榜之外很重要

每个发布的运行都是关于商业提供商不测量的语言对 MT 质量的独立证据。队列也充当*需求*的公开记录：社区认为值得测量的语言对、当前 API 价格下的覆盖成本，以及捐赠的计算资源能走多远。当我们要求资助机构为系统性扫描提供资金时，这个队列及其填充率是需求证据。