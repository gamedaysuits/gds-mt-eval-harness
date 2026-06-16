---
id: how-this-site-is-translated
title: "本网站如何翻译"
description: "本网站的每个语言版本都由 Champollion 自身进行机器翻译，使用在该语言对公开基准测试中获胜的方法。"
---
# 本网站的翻译方式

本网站提供 13 种语言版本。除英文外，**所有语言版本均由 Champollion 进行机器翻译**，Champollion 是与本竞技场一起开发的翻译 CLI——每种语言的翻译模型是**由本网站自身的基准测试选择的，而非默认选择**：每个语言对都在公开开发语料库上使用 MT eval 工具进行评估，复合分数最高的方法/模型（统计平局时按成本排序）用于翻译该语言版本。

这意味着作为读者，您应该了解以下两点：

1. **这些页面是机器翻译。** 它们是根据下面描述的寄存器和术语指导生成的，但并非每个句子都经过人工审核。如果某些内容读起来不对，英文版本是权威版本——我们很乐意接收更正。
2. **您可以审计选择过程。** 下表中的每一行都标注了为该语言选择模型的基准测试运行；这些运行已发布到 [MT Eval Arena 排行榜](https://mtevalarena.org/leaderboard)。

## 按语言版本的来源信息

| 语言版本 | 语言 | 方法 | 模型 | 基准语料库 | 复合分数 (95% CI) | 基准测试日期 | 最后同步时间 |
|--------|------|------|------|----------|-----------------|-----------|----------|
| fr | Français | llm | `anthropic/claude-haiku-4.5` | `eng-fra-dev-v1` (Tatoeba, CC-BY-2.0) | 0.581 [0.542, 0.617] | 2026-06-11 | 2026-06-12 |
| de | Deutsch | llm | `anthropic/claude-opus-4.8` | `eng-deu-dev-v1` (Tatoeba, CC-BY-2.0) | 0.590 [0.550, 0.633] | 2026-06-11 | 2026-06-12 |
| nl | Nederlands | llm | `anthropic/claude-sonnet-4.6` | `eng-nld-dev-v1` (Tatoeba, CC-BY-2.0) | 0.600 [0.558, 0.642] | 2026-06-11 | 2026-06-12 |
| fil | Filipino | llm | `openai/gpt-5.5` | `eng-tgl-dev-v1` (Tatoeba, CC-BY-2.0)¹ | 0.499 [0.471, 0.529] | 2026-06-11 | 2026-06-12 |
| es | Español | llm | `anthropic/claude-haiku-4.5` | `eng-spa-dev-v1` (Tatoeba, CC-BY-2.0) | 0.553 [0.523, 0.584] | 2026-06-11 | 2026-06-12 |
| zh | 简体中文 | llm | `anthropic/claude-haiku-4.5` | `eng-cmn-dev-v1` (Tatoeba, CC-BY-2.0) | 0.240 [0.207, 0.278] | 2026-06-11 | 2026-06-12 |
| ja | 日本語 | llm | `anthropic/claude-sonnet-4.6` | `eng-jpn-dev-v1` (Tatoeba, CC-BY-2.0) | 0.278 [0.252, 0.304] | 2026-06-11 | 2026-06-12 |
| ko | 한국어 | llm | `anthropic/claude-opus-4.8` | `eng-kor-dev-v1` (Tatoeba, CC-BY-2.0) | 0.286 [0.256, 0.318] | 2026-06-11 | 2026-06-12 |
| pt | Português | llm | `anthropic/claude-haiku-4.5` | `eng-por-dev-v1` (Tatoeba, CC-BY-2.0) | 0.609 [0.576, 0.646] | 2026-06-11 | 2026-06-12 |
| th | ไทย | llm | `anthropic/claude-sonnet-4.6` | `eng-tha-dev-v1` (Tatoeba, CC-BY-2.0) | 0.468 [0.426, 0.510] | 2026-06-11 | 2026-06-12 |
| vi | Tiếng Việt | llm | `google/gemini-3.5-flash` | `eng-vie-dev-v1` (Tatoeba, CC-BY-2.0) | 0.463 [0.433, 0.494] | 2026-06-11 | 2026-06-12 |
| ar | العربية | llm | `anthropic/claude-fable-5` | `eng-arb-dev-v1` (Tatoeba, CC-BY-2.0)² | 0.437 [0.403, 0.478] | 2026-06-11 | 2026-06-12 |

¹ 菲律宾语使用他加禄语数据进行基准测试——这是 Tatoeba 中最接近 `fil` 语言版本的可用语料库。
² 阿拉伯语语料库为现代标准阿拉伯语（ISO 639-3 `arb`），与本网站的 MSA 寄存器相匹配。

选择规则：对于每个语言对，基准测试阵容中的每个模型
（`google/gemini-3.5-flash`、`anthropic/claude-haiku-4.5`、
`anthropic/claude-fable-5`、`anthropic/claude-opus-4.8`、
`anthropic/claude-sonnet-4.6`、`openai/gpt-5.5`、
`google/gemini-3.1-pro-preview`）都在该语言对的开发语料库上进行评分。获胜者是复合分数最高的模型；当成本较低的模型在统计上与最高分数无差异时（配对自助重采样，p ≥ 0.05），选择成本较低的模型。

*复合分数*是 MT Eval Arena 的混合质量指标（chrF++、精确匹配和加载的指标插件，经自助置信区间验证）。分数在**同一语言对内**具有可比性，不同语言对之间不可比——韩语的 0.28 并不意味着韩语页面比法语页面（0.58）质量更差；语料库和文字系统不同。

## 寄存器和语调

每种语言都使用从 Champollion 语言卡中选择的明确寄存器进行翻译，以确保整个网站的正式程度保持一致：

- **Français** — 敬语形式（正式 *vous*）
- **Deutsch** — Sie-Form
- **Nederlands** — u-vorm
- **Filipino** — 正式，采用标准技术术语
- **Español** — 中立的拉丁美洲西班牙语
- **简体中文** — 专业技术寄存器
- **日本語** — です/ます（礼貌形式）
- **한국어** — 해요체（礼貌形式）
- **Português** — 专业寄存器
- **ไทย** — 中立专业
- **Tiếng Việt** — 中立 *bạn* 形式
- **العربية** — 现代标准阿拉伯语，专业寄存器

## 不进行机器翻译的内容

代码块、CLI 命令、配置键、包名、URL 和专有名词在翻译过程中受到保护，按设计保持英文不变。

## 发现翻译错误？

提交 issue 或 PR——每个翻译页面的源文件都是英文原文。对翻译页面的更正在后续同步中会被保留，只要该页面的英文源文件保持不变（仅当英文源文件更改时，同步才会重新翻译页面）。

*本页面本身由上表中的方法进行机器翻译——它描述了自己的翻译过程。*