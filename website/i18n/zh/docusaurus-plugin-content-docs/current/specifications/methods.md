---
sidebar_position: 4
title: "方法接口"
related:
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
    note: "Put this interface on the leaderboard"
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
    note: "A full method, built end-to-end"
---
# 共享方法接口

> **执行摘要。** 本页规定了所有 Arena 方法必须实现的 `TranslationMethod` 协议、六个方法类别（`raw-llm`、`coached-llm`、`pipeline`、`custom-plugin`、`api`、`human`）、方法插件格式，以及**依赖类别**（S/O/A1/A2/X），这些类别决定了方法是否可以在评估沙箱中运行并有资格获得奖项。任何实现此协议的方法都可以进行基准测试；它的依赖关系决定了它可以在哪里竞争。

评估工具和 champollion 共享一个**翻译方法**的通用概念。方法是任何接收源文本并生成翻译文本的过程——无论是直接的 LLM 调用、多阶段管道、第三方 API 还是人工翻译。

## 架构

```
Method Plugin (v2 Spec)
├── method.json           ← Manifest (name, class, entry_point, dependencies, metadata)
├── method_card.json      ← Leaderboard description (what, not how)
├── pipeline.py           ← Python module implementing TranslationMethod
└── (optional helpers)    ← Additional Python modules
```

通过 `--method path/to/dir` 加载。工具不会自动发现任何内容。

## 两个系统，一个接口

| | 评估工具 | champollion |
|---|---|---|
| **语言** | Python | Node.js |
| **入口点** | `translate.py` | `translate.js` |
| **接口** | `TranslationMethod` 协议 | `methodPlugin` 配置 |
| **用途** | 批量评估和评分 | 开发/CI 中的实时本地化 |
| **输出** | 包含指标的运行卡 | 翻译的区域设置文件 |

支持两个系统的方法提供两个入口点——每个语言运行时一个。**方法卡**是桥梁：它以两个系统都能理解的格式描述方法。

## 方法卡 {#method-card}

方法卡描述*什么是*翻译方法，而不暴露专有细节，如完整的系统提示。它回答：

- 这是什么类别的方法？（原始 LLM、经过指导的 LLM、管道、API 等）
- 它使用什么工具？（FST 分析器、字典等）
- 实现是开源的吗？
- 它支持哪些语言对？

有关完整的 JSON 架构，请参阅[方法卡规范](/docs/specifications/methods#method-card)。

### 示例

```json
{
  "method_id": "fst-gated-v8",
  "name": "FST-Gated Coached Translation v8",
  "class": "pipeline",
  "description": "LLM translation with morphological validation. Failed words are retried with FST feedback.",
  "author": "Curtis Forbes",
  "tools_used": ["HFST morphological analyzer", "Wolvengrey dictionary"],
  "open_source": false,
  "dependency_class": "A2",
  "supported_pairs": ["eng>crk"]
}
```

`dependency_class` 字段总结了方法需要运行和转移的内容——请参阅下面的[方法有效性和依赖类别](#method-validity-and-dependency-classes)。

### 方法类别

| 类别 | 描述 |
|-------|-------------|
| `raw-llm` | 直接 LLM 调用，指令最少 |
| `coached-llm` | 具有结构化提示、示例和约束的 LLM |
| `pipeline` | 具有确定性组件的多阶段管道 |
| `custom-plugin` | 实现 `TranslationMethod` 协议的外部进程 |
| `api` | 第三方翻译 API（Google Translate、DeepL 等） |
| `human` | 人工翻译（用于建立基准） |

## 方法有效性和依赖类别 {#method-validity-and-dependency-classes}

方法的可运行性和可转移性取决于其最不可用的依赖。两个 Arena 机制取决于准确了解方法需要什么：

1. **沙箱化评估**（[基准规范 §8.2](/docs/specifications/benchmark)）——官方黄金标准分数来自网络策略为**默认拒绝**的沙箱。无声地需要外部服务的方法无法生成官方分数。
2. **奖项转移**（[奖项规范](/docs/specifications/prizes)）——获奖方法转移到语言社区的治理组织。捆绑提交者无权包含的内容的方法无法合法转移。提交者必须持有（或被授予）盒子中所有内容的权利。

为了使两项检查都是机械性的而不是临时性的，每个方法都声明一个**依赖类别**，该类别源自 `method.json` 中的**依赖清单**。

> **关于命名的说明。** *方法类别*（上面的 §：`raw-llm`、`pipeline`、…）描述*方法如何翻译*。*依赖类别*（本节）描述*方法需要什么来运行和转移*。它们是独立的轴：`pipeline` 方法可以是任何依赖类别。

### 五个依赖类别

| 类别 | 名称 | 定义 | 沙箱可运行？ | 有资格获得奖项？ |
|-------|------|-----------|-------------------|-----------------|
| **S** | 自包含 | 所有代码、数据、模型和权重都在方法目录内，采用允许重新分发和社区转移的许可证。 | ✅ 是，按原样 | ✅ 是 |
| **O** | 开放外部 | 依赖于允许重新分发的开放许可证下的外部托管工件（包括 AGPL 等 copyleft 许可证）——例如，在安装时下载的 FST。 | ✅ 是——工件被固定并**镜像到提交中** | ✅ 是，具有许可证兼容性条件：copyleft 条款通过转移保留，社区获得许可证授予所有人的相同权利 |
| **A1** | API 依赖，可替代 | 需要运行时 LLM 推理，其中模型是**可替代配置**——任何足够强大的模型都可以插入。方法的价值在于其提示、指导数据和代码，而不是任何一个提供商的模型。 | ⚠️ 仅通过沙箱规范定义的 **LLM 网关**（🔲 计划中——见下文） | ⚠️ 条件性——见下文 |
| **A2** | API 依赖，不可替代 | 需要运行时调用无法镜像或替代的外部数据或服务 API——通常是因为所提供的内容是专有的或无许可的（例如，其基础字典没有公开许可证的字典 API）。 | ❌ 否——该依赖在没有权利持有人许可的情况下无法存在于沙箱中 | ❌ 在权利持有人授予沙箱包含**和**转移权限之前不符合条件。允许在开放（开发段）排行榜上使用可见的**"外部依赖"**标志 |
| **X** | 封闭 | 捆绑提交者无权重新分发的内容——无许可数据集、抓取的专有内容、许可证不兼容的组件。 | ❌ | ❌ 在每个赛道中都不可接受。在没有权利的情况下捆绑内容是许可证违规，无论方法在哪里运行 |

**有效类别。** 方法的依赖类别是其所有声明依赖中*最严格的*类别，顺序为 S < O < A1 < A2 < X。一个无许可字典使得原本自包含的管道成为 A2 类（如果在运行时访问）或 X 类（如果在没有权利的情况下捆绑）。

### A1/A2 区分：可替代性

大多数方法调用 LLM。Arena 不否认这一点——但它区分两种非常不同的 API 依赖：

- **A1（可替代）：** API 提供商品 LLM 推理。模型标识符是配置：方法必须针对任何兼容的推理端点（包括社区托管的开放权重模型）端到端运行。输出质量可能因模型而异——这是开发者的风险，官方分数与评估中使用的固定模型相关联。依赖于**提供商端状态**的方法（仅在提供商处托管的微调、提供商文件存储、提供商特定助手）*不*可替代：该状态无法替换，因此除非基础权重或数据包含在提交中，否则依赖是 A2。
- **A2（不可替代）：** API 提供独特的东西——通常是专有或无许可数据。没有替代端点可以提供它，内容无法在没有权利持有人许可的情况下镜像到沙箱中。方法在开放排行榜上工作（带标志），但在获得权限之前无法生成官方沙箱分数或有资格获得奖项。

**A1 奖项转移实际传达的内容。** 社区不会获得模型——没有人可以转移 Anthropic、Google 或 OpenAI 的权重。转移涵盖模型*周围*的完整配方：所有提示、指导数据、管道代码、重试逻辑、配置和记录的模型要求。因为模型在构造上是可替代的，社区可以将转移的方法指向他们选择的任何提供商——或指向他们自己硬件上的开放权重模型——无需开发者的参与。配方是拥有的；引擎是租赁的和可替换的。

### 依赖清单（`method.json`）

每个方法在 `method.json` 清单中声明其依赖。每个条目记录工件是什么、来自何处、许可证覆盖范围以及方法如何访问它：

```json
{
  "name": "FST-Gated Coached Translation v8",
  "method_id": "fst-gated-v8",
  "class": "pipeline",
  "entry_point": "pipeline:PipelineMethod",
  "supported_pairs": ["eng>crk"],
  "dependency_class": "A2",
  "dependencies": [
    {
      "id": "giellalt-lang-crk-fst",
      "kind": "software",
      "license": "AGPL-3.0-or-later",
      "access": "mirrored",
      "source": "https://github.com/giellalt/lang-crk",
      "pin": "sha256:3f1a…",
      "redistributable": true,
      "transferable": true
    },
    {
      "id": "llm-inference",
      "kind": "model",
      "license": "proprietary",
      "access": "gateway",
      "source": "openrouter:google/gemini-2.5-flash",
      "substitutable": true,
      "redistributable": false,
      "transferable": false,
      "notes": "Any compatible chat-completions endpoint works; the model slug is configuration."
    },
    {
      "id": "crk-dictionary-api",
      "kind": "service",
      "license": "none",
      "access": "external-api",
      "source": "https://itwewina.altlab.app/",
      "redistributable": false,
      "transferable": false,
      "notes": "Dictionary content has no public license; runtime lookups only. Class A2 until the rights holders grant permission."
    }
  ]
}
```

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `id` | ✅ | 依赖的稳定标识符 |
| `kind` | ✅ | `data`、`model`、`software` 或 `service` |
| `license` | ✅ | SPDX 标识符、`proprietary` 或 `none`。`none` 表示不存在公开许可证——视为全部保留权利 |
| `access` | ✅ | `bundled`（在方法目录中发货）、`mirrored`（在安装时获取、固定、供应到提交中）、`gateway`（通过评估网关进行运行时 LLM 推理）、`external-api`（任何其他运行时网络调用） |
| `source` | ✅ | 规范 URL 或 `provider:slug` 标识符 |
| `pin` | 对于 `mirrored` | 固定确切工件的版本、提交或内容哈希 |
| `substitutable` | 对于 `gateway`/`external-api` | 任何兼容端点是否可以提供此依赖 |
| `redistributable` | ✅ | 许可证是否允许重新分发工件 |
| `transferable` | ✅ | 工件（或其权利）是否可以在奖项转移条款下转移到社区 |
| `notes` | ❌ | 自由格式上下文 |

**类别推导。** 每个依赖贡献一个类别；方法的 `dependency_class` 是最严格的：

| 依赖配置文件 | 贡献 |
|--------------------|-------------|
| `bundled` + 许可证允许重新分发和转移 | S |
| `mirrored` + 允许重新分发的开放许可证（包括 copyleft） | O |
| `gateway` + `substitutable: true`（LLM 推理） | A1 |
| `external-api`，或 `gateway` 带 `substitutable: false` | A2 |
| `bundled` + `license: none` 或不兼容重新分发的许可证 | X |

声明的 `dependency_class` 必须与工具从清单推导的类别相匹配。不匹配是验证错误。

没有**任何**外部依赖的方法声明 `"dependency_class": "S"` 和 `"dependencies": []`。空数组是一个肯定的陈述，像任何其他陈述一样被审计。

### 如何验证有效性

三个层次，从最便宜到最权威：

1. **清单审计。** 工具从清单推导有效类别并拒绝不匹配。审查者根据其声明的许可证和来源检查每个声明的依赖——声明为 `redistributable: true` 的依赖，其上游许可证另有说明，审查失败。
2. **静态分析。** 提交的代码被扫描以查找网络调用、动态下载和清单未说明的文件系统访问。在审查中发现的*未声明*依赖是拒绝的理由，无论它属于哪个类别——清单必须完整，而不仅仅是准确。
3. **沙箱网络策略。** 沙箱规范要求**默认拒绝出站**：方法容器除非明确允许路径，否则无法获得网络访问。规范定义的唯一出站路径是 **LLM 网关**——由评估基础设施运营的推理代理，限制为显式允许列表中的固定模型，每个请求和响应都被记录以供运行后审计。不在允许列表上的任何内容在网络层失败，而不是在策略层。有关网络策略和网关设计，请参阅[基准规范 §8.6](/docs/specifications/benchmark)。

> 🔲 **计划中。** 沙箱及其 LLM 网关已指定但尚未构建。在网关运行之前，只有 S 类和 O 类方法可以在沙箱中评估；A1 类方法原则上有资格获得奖项，但目前无法生成官方黄金标准分数。本页描述规范要求的内容，而不是当前运行的内容。

### 排行榜显示

- 排行榜在其方法类别徽章旁边显示每个方法的依赖类别。
- 开放排行榜上的 A2 类方法带有可见的**"外部依赖"**标志：它们的分数取决于可能改变或消失的第三方服务，目前不符合奖项资格。
- X 类方法未列出。

## 评估工具：TranslationMethod 协议 {#eval-harness-translationmethod-protocol}

评估工具使用 Python 的结构类型（`Protocol`）进行插件。任何具有正确方法签名的类都可以工作——不需要继承：

```python
class MyMethod:
    async def translate(self, entries: list[dict], config: RunConfig) -> list[dict]:
        results = []
        for entry in entries:
            translation = await self.do_translation(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translation,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "error": None,
                "tool_calls": [],
                "tool_call_count": 0,
                "metadata": {},
            })
        return results
```

有关完整文档（包括非 Python 方法的包装器示例），请参阅[插件协议](/docs/specifications/methods#eval-harness-translationmethod-protocol)。

## champollion：methodPlugin 配置

在 champollion 中，方法按语言对在 `champollion.config.json` 中注册：

```json
{
  "version": 3,
  "pairs": {
    "en:crk": {
      "methodPlugin": "crk-coached-v1"
    }
  }
}
```

有关 champollion 端接口，请参阅[插件规范](https://champollion.dev/docs/reference/plugin-spec)。

## 排行榜集成

当方法卡附加到运行时（通过 `--method-card`），它被嵌入到运行卡中并显示在排行榜上：

```bash
# Run with method card attached
mt-eval run \
  --method path/to/my-method \
  --corpus data/edtekla-dev-v1.json \
  --method-card method_card.json

# Publish to the leaderboard
mt-eval publish eval/logs/harness/your-run-card.json
```

如果未提供 `--method-card`，`mt-eval publish` 会启动一个交互式向导，引导您完成描述方法的过程。

排行榜显示：
- **类别徽章** — 视觉指示符（例如"pipeline"、"coached-llm"）
- **依赖类别** — S/O/A1/A2（请参阅[方法有效性和依赖类别](#method-validity-and-dependency-classes)）；A2 方法带有"external dependency"标志
- **方法名称** — 来自方法卡
- **使用的工具** — 从方法卡列出
- **开源指示符**

当未附加方法卡时，排行榜显示工具原生配置（模型、提示版本、温度、启用的工具）。

:::danger 不要在评估数据上训练
开发过程包括接触评估数据集的方法——作为训练数据、少样本示例、字典条目或提示调整材料——将从排行榜**取消资格**。有关什么区分好方法和坏方法，请参阅[机器翻译评估](/docs/leaderboard/rules)。
:::

---

## 另请参阅

- [机器翻译评估](/docs/leaderboard/rules) — 概述、排行榜价值和好/坏方法指导
- [评估工具](/docs/specifications/harness) — 如何运行评估
- [评估数据集](/docs/leaderboard/datasets) — 可用数据集（EDTeKLA、FLORES+）
- [运行卡规范](/docs/specifications/run-card) — 运行卡 JSON 架构
- [插件规范](https://champollion.dev/docs/reference/plugin-spec) — champollion 端插件接口
- [方法排行榜](https://champollion.dev/leaderboard) — 实时基准分数
- [基准规范](/docs/specifications/benchmark) — 评估协议、语料库格式、运行卡架构
- [评分规范](/docs/specifications/scoring) — 指标、复合权重和质量等级的 SSOT