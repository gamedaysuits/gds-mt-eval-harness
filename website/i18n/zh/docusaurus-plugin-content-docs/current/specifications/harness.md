---
sidebar_position: 2
title: "Eval Harness v2.0"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "What the harness metrics feed into"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: Translate 30 Languages"
    to: https://champollion.dev/docs/tutorials/translate-30-languages
    kind: champollion
    note: "Use the harness to audit registers in production"
---
# Eval Harness v2.0

> **执行摘要。** 本页涵盖 MT 评估工具的安装、配置和使用 — 该工具针对标准化语料库对翻译方法进行基准测试，并生成评分运行卡。有关指标、模式和评估协议的规范定义，请参阅[基准规范](/docs/specifications/benchmark)。

该工具运行翻译实验并生成运行卡。它处理提示构建、API 调用、评分和结果序列化 — 你提供数据集和模型。

## 安装

**要求：** Python 3.10+

```bash
pip install sacrebleu aiohttp
```

克隆工具仓库：

```bash
git clone https://github.com/gamedaysuits/arena.git
cd arena
```

## 使用

```bash
mt-eval run --corpus path/to/dataset.json
```

这会通过配置的模型（或方法插件）运行语料库中的每个条目，对输出进行评分，并将运行卡 JSON 文件写入输出目录。

## CLI 标志

### `mt-eval run`

| 标志 | 必需 | 默认值 | 描述 |
|------|----------|---------|-------------|
| `--corpus` | ✅ | — | 语料库文件路径（`.json`、`.jsonl`、`.tsv`） |
| `--source-file` / `--reference-file` | — | — | 平行文本文件（FLORES+、WMT 格式） |
| `-m, --model` | — | `gemini-pro` | 模型 slug（短名称或完整 OpenRouter ID）。通过 `shared/model-aliases.json` 解析。逗号分隔用于多模型运行 |
| `-d, --dataset` | — | `all` | 数据集过滤器：`all`、分段名称或 ID 范围 |
| `--ids` | — | — | 逗号分隔的条目 ID 以进行评估 |
| `--source-lang` | — | `English` | 源语言名称 |
| `--target-lang` | — | — | 目标语言名称 |
| `-p, --prompt` | — | `naive` | 提示版本（`naive`、`custom`、`champollion`） |
| `--coaching-file` | — | — | 指导提示文本文件路径 |
| `--coaching` | — | — | 内联指导文本（引用字符串） |
| `--method` | — | — | 方法插件目录路径（包含 `method.json` + Python 模块） |
| `--method-card` | — | — | 方法卡 JSON 路径用于排行榜元数据 |
| `--fst-retries` | — | `0` | FST 重试尝试次数（仅默认 LLM 方法） |
| `--skip-fst` | — | `false` | 完全跳过 FST 质量门 |
| `--tools` | — | `false` | 启用工具调用模式 |
| `--tools-list` | — | — | 逗号分隔的工具名称 |
| `--max-tool-rounds` | — | `8` | 每个条目的最大工具调用轮数 |
| `--hooks` | — | — | 翻译后钩子名称 |
| `--style-profile` | — | — | 样式配置文件 JSON 路径。启用写作风格一致性指标（信息性 — 永远不是复合分数的一部分；参见[§ 写作风格和寄存器指标](#writing-style-and-register-metrics-informational)） |
| `-b, --batch-size` | — | `25` | 每个 API 调用的条目数 |
| `-c, --concurrency` | — | `8` | 并行 API 调用数 |
| `--max-tokens` | — | `32768` | 每个 API 调用的最大令牌数 |
| `--temperature` | — | `0.0` | 采样温度（0.0 = 确定性） |
| `--no-cache` | — | `false` | 禁用响应缓存 |
| `--cache-dir` | — | `eval/cache/harness` | 缓存目录路径 |
| `-o, --output-dir` | — | `eval/logs/harness` | 运行卡和日志的输出目录 |
| `-n, --name` | — | — | 人类可读的运行名称 |
| `--dry-run` | — | `false` | 验证配置而不进行 API 调用 |
| `--champollion-config` | — | — | `champollion.config.json` 的路径 |
| `--champollion-cards-dir` | — | — | 语言卡目录 |
| `--target-lang-code` | — | — | BCP-47 语言代码 |

### 其他子命令

| 子命令 | 描述 |
|------------|-------------|
| `mt-eval test <log_path>` | 分析已完成的运行日志 |
| `mt-eval publish <report_path>` | 将运行卡提交到排行榜 |
| `mt-eval compare <logs...>` | 并排比较多个运行 |
| `mt-eval dashboard <logs...>` | 从运行日志生成 HTML 仪表板 |
| `mt-eval list models\|prompts\|datasets` | 列出可用资源 |
| `mt-eval export` | 将当前设置打包为 champollion 方法插件 |
| `mt-eval export-config` | 将解析的 MethodConfig（所有 8 个规范字段）导出为 JSON |

### 示例

```bash
# Run with defaults (gemini-pro alias → google/gemini-3.1-pro-preview, naive prompt)
mt-eval run --corpus data/edtekla-dev-v1.json

# Coached experiment with coaching file
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model google/gemini-3.1-pro \
  --coaching-file prompts/crk-coaching-v8.txt \
  --temperature 0.0

# Run a custom method plugin with FST retries
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --method ./methods/fst-gated-pipeline \
  --fst-retries 3
```

---

## 运行卡模式

每个实验都会生成一个**运行卡** — 一个自包含的 JSON 文档。顶级结构：

```json
{
  "run_id": "uuid-v4",
  "harness_version": "2.0",
  "model_slug": "google/gemini-3.1-pro",
  "model_id": "gemini-3.1-pro-001",
  "condition": "baseline",
  "timestamp": "2026-06-01T03:22:41Z",
  "elapsed_seconds": 142.7,
  "dataset": { ... },
  "config": { ... },
  "method_card": { ... },
  "system_prompt_sha256": "abc123...",
  "system_prompt_used": "You are a translator...",
  "fingerprint": { ... },
  "scores": { ... },
  "totals": { ... },
  "environment": { ... },
  "results": [ ... ],
  "run_card_hash": "sha256-of-entire-card"
}
```

有关每个字段的完整模式文档，请参阅[运行卡规范](/docs/specifications/run-card)。

:::info 权威模式
[基准规范](/docs/specifications/benchmark)是运行卡模式的唯一真实来源。有关指标定义、复合权重和质量等级，请参阅[评分规范](/docs/specifications/scoring)。本页记录如何使用工具；规范定义输出的含义。
:::

### 关键块

**`dataset`** — 标识使用了哪个数据集，包括其内容哈希，以便结果与特定版本相关联：

```json
// Example using master_corpus.json (62 gold + 342 textbook = 404)
{
  "id": "edtekla-dev-v1",
  "version": "1.0",
  "language_pair": "EN→CRK",
  "sha256": "...",
  "entry_count": 404
}
```

**`scores`** — 运行的聚合指标：

```json
// Counts reflect the dataset used (here: master_corpus.json, 404 entries)
{
  "total": 404,
  "exact_matches": 12,
  "exact_match_rate": 0.0968,
  "fst_accepted": 87,
  "fst_acceptance_rate": 0.7016,
  "chrf_plus_plus": 42.31,
  "errors": 0,
  "avg_latency_seconds": 1.15,
  "median_latency_seconds": 1.02,
  "p95_latency_seconds": 2.34,
  "by_difficulty": { ... },
  "by_provenance": { ... }
}
```

**`totals`** — 令牌使用和成本跟踪：

```json
{
  "prompt_tokens": 48200,
  "completion_tokens": 3100,
  "reasoning_tokens": 0,
  "cached_tokens": 12000,
  "total_cost_usd": 0.42,
  "cost_per_entry_usd": 0.0034,
  "reasoning_ratio": 0.0
}
```

---

## 写作风格和寄存器指标（信息性）

工具可以通过 `WritingStyleConsistency` 指标插件（`mt_eval_harness/plugins/writing_style.py`）评估翻译是否与目标**寄存器**和**写作风格**相匹配。翻译在语言上可能是正确的，但寄存器错误 — 法律文件中的非正式措辞、营销文案中的正式样板 — 字符串指标不会注意到。这些指标会。

**测量内容（每个条目）：**

| 指标 | 范围 | 含义 |
|--------|-------|---------|
| `style_register_match` | 布尔值 | 输出是否与预期的寄存器相匹配？目标来自语料库条目的 `register` 字段（参见[基准规范 §2.6](/docs/specifications/benchmark)）或样式配置文件 |
| `style_sentence_length_ratio` | 浮点数 | 预测与参考平均句子长度（1.0 = 匹配；偏差 = 风格漂移） |
| `style_formality_score` | 0.0–1.0 | 正式/非正式标记的存在（T–V 代词、缩写等）使用每种语言的标记资源 |

**聚合：** `style_consistency_rate` — 没有检测到寄存器不匹配的条目的比例。

使用 `--style-profile path/to/profile.json` 启用自定义目标（例如品牌语音配置文件）；没有它，插件会回退到每个语料库条目的 `register` 元数据（如果存在）。

:::caution 诚实的范围界定
这些指标**仅供参考** — 它们永远不是复合分数的一部分，正式性检测是基于标记的（一种启发式方法），而不是学习判断。将它们视为寄存器遵守的漂移检测器，而不是风格质量的判决。
:::

---

## 指纹与运行卡哈希 {#fingerprint-vs-run-card-hash}

工具生成两个不同的哈希。它们有不同的用途：

### 指纹

**指纹**回答：*"这个运行能被重现吗？"*

它对定义实验配置的输入组合进行哈希 — 而不是输出：

- 数据集 SHA-256
- 模型 slug
- 条件标签
- 系统提示 SHA-256
- 温度
- 工具版本

两个具有相同指纹的运行使用了相同的设置。它们的结果应该是可比较的（模除 API 非确定性）。

### 运行卡哈希

**运行卡哈希**回答：*"这个特定结果文件是否被篡改过？"*

它是整个运行卡 JSON 的 SHA-256（不包括 `run_card_hash` 字段本身）。如果任何字段改变 — 一个分数、一个时间戳、一个输出 — 哈希就会破裂。

:::info 何时使用哪个
使用**指纹**对可比较的运行进行分组（相同的实验、不同的执行）。使用**运行卡哈希**验证特定结果文件的完整性。
:::

---

## 发布到排行榜

完成运行后，使用 `mt-eval publish` 提交运行卡：

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

如果在运行期间没有提供 `--method-card`，`mt-eval publish` 会启动交互式向导（`method_card_wizard.py`），引导你描述你的方法（名称、类别、使用的工具等）。向导输出在提交前嵌入到运行卡中。

### 手动提交

运行卡作为 JSON 文件保存在输出目录中。你也可以通过排行榜 UI 在 [/leaderboard](https://champollion.dev/leaderboard) 提交任何运行卡文件，或通过 API：

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning 排行榜验证
排行榜根据数据集注册表验证提交的运行卡。引用未知数据集或具有破损 `run_card_hash` 的提交会被拒绝。
:::

:::danger 不要在评估数据上进行训练
如果你的方法在开发期间见过评估数据集 — 作为训练数据、少样本示例、字典条目或提示工程材料 — 你的提交将被**取消资格**。有关什么是好方法与坏方法，请参阅 [MT 评估](/docs/leaderboard/rules)。
:::

---

## 另见

- [MT 评估](/docs/leaderboard/rules) — 概述、排行榜价值主张和好/坏方法指导
- [评估数据集](/docs/leaderboard/datasets) — 数据集格式、EDTeKLA、FLORES+
- [运行卡规范](/docs/specifications/run-card) — 完整的 JSON 模式
- [构建方法](/docs/specifications/methods) — 用于创建可评估方法的方法接口
- [方法排行榜](https://champollion.dev/leaderboard) — 实时基准分数
- [基准规范](/docs/specifications/benchmark) — 评估协议、语料库格式、运行卡模式
- [评分规范](/docs/specifications/scoring) — 指标、复合权重和质量等级的 SSOT