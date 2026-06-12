---
sidebar_position: 3
title: "Agent 指南：赢得竞技场"
description: "AI 代理如何构建翻译方法、对其进行基准测试，以及提交到排行榜的方法。"
related:
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
  - label: "Agent Guide: Using champollion"
    to: https://champollion.dev/docs/guides/agent-guide
    kind: champollion
    note: "The production-side guide for the same agents"
---
# Agent 指南：赢得竞技场

MT Eval Arena 是一个开放的机器翻译方法基准测试平台。构建一个比现有方法翻译效果更好的方法，用可重现的评分证明其有效性，获胜的方法将被部署到生产环境——收益流向它所服务的语言社区。

:::tip 为什么这很重要
商业翻译服务覆盖约 130 种语言。Meta 的 OMT-1600 声称覆盖 1,600 种更多语言——但对于约 1,300 种资源最少的语言，质量未经独立评估验证，模型权重也不可用。竞技场提供了独立的测试基础设施。如果你的方法有效，它可以用于那些没有独立验证 MT 的语言。
:::

---

## 环境设置

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena

# Create a virtual environment (do NOT install into global Python)
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -e .
```

**API 密钥** — 测试框架使用 OpenRouter 调用 LLM 模型。设置你的密钥：

```bash
# Option 1: export (session only)
export OPENROUTER_API_KEY="sk-or-..."

# Option 2: .env file (persistent, gitignored)
echo 'OPENROUTER_API_KEY=sk-or-...' > .env
```

在 [openrouter.ai/keys](https://openrouter.ai/keys) 获取密钥。免费层模型适合实验。

---

## 运行你的第一个基准测试

```bash
# Run a baseline LLM against the Cree evaluation corpus
mt-eval run --corpus data/edtekla-dev-v1.json

# Or specify a model explicitly
mt-eval run --corpus data/edtekla-dev-v1.json -m google/gemini-2.5-flash
```

测试框架生成一个**运行日志** — 一个 JSON 文件，保存到 `eval/logs/`，包含每个翻译、每个指标分数，以及一个将结果与精确实验配置绑定的密码学指纹。

**有用的标志：**

| 标志 | 功能 |
|------|-------------|
| `-m <model>` | OpenRouter 模型 slug（用逗号分隔以进行多模型并行运行） |
| `--condition <name>` | 方法标签（显示在排行榜上） |
| `--temperature <float>` | 采样温度（较低 = 更确定性） |
| `--batch-size <n>` | 每个 API 调用的条目数（默认：25） |
| `--dry-run` | 验证配置而不进行 API 调用 |
| `--ids 0,1,2,3` | 仅运行特定条目 ID |

```bash
# Multi-model comparison (runs in parallel)
mt-eval run --corpus data/edtekla-dev-v1.json -m gemini-2.5-flash,claude-sonnet-4,gpt-4.1

# Dry run to validate config
mt-eval run --corpus data/edtekla-dev-v1.json --dry-run
```

其他命令：`mt-eval test <log.json>`（对已完成的运行评分）、`mt-eval compare <log1> <log2>`（比较运行）、`mt-eval dashboard <logs/*.json>`（生成 HTML 仪表板）、`mt-eval list models --live`（浏览可用模型）。

---

## 构建你自己的方法

测试框架接受任何实现 `TranslationMethod` 协议的 Python 类：

```python
from mt_eval_harness.config import RunConfig

class YourMethod:
    """Build whatever you want inside. The harness only sees this interface."""

    async def translate(
        self,
        entries: list[dict],
        config: RunConfig,
    ) -> list[dict]:
        """
        Args:
            entries: [{"id": 1, "source": "Hello"}, ...]
            config:  RunConfig with source_locale, target_locale, model, etc.

        Returns: one result dict per entry, each containing:
            - id: int          — entry ID from the corpus
            - predicted: str   — the translated text
            - latency_s: float — time taken in seconds
            - usage: dict      — token usage {prompt_tokens, completion_tokens}
            - error: str|None  — error message if failed
            - metadata: dict   — any process-specific metadata
        """
        results = []
        for entry in entries:
            # Your translation logic here — LLM prompting, FST pipeline,
            # dictionary lookup, fine-tuned model, anything.
            translated = await self._my_translate(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translated,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
                "error": None,
                "metadata": {"method": "my-custom-pipeline"},
            })
        return results
```

**结构化类型** — 你的类不需要继承任何东西。如果它有正确的 `translate` 方法签名，它就能工作。这意味着现有管道可以用一个薄包装器进行适配。

**将其连接到测试框架：**

```python
import asyncio
from mt_eval_harness.config import RunConfig
from mt_eval_harness.runner import execute_run

async def main():
    config = RunConfig(
        corpus_path="data/edtekla-dev-v1.json",
        model="google/gemini-2.5-flash",
        condition="my-method-v1",
    )
    results = await execute_run(config, method=YourMethod())
    print(f"Composite: {results['scores']['composite']}")

asyncio.run(main())
```

---

## 方法思路

每种方法都有一个完整的食谱，包含实现指导：

| 方法 | 描述 | 食谱 |
|----------|-------------|---------|
| **FST 门控管道** | 形态学验证捕捉 LLM 遗漏的内容 | [教程](/docs/tutorials/fst-gated-pipeline) |
| **指导 LLM** | 将语法规则和字典注入提示 | [教程](/docs/tutorials/coached-llm-prompting) |
| **字典增强** | 强制术语一致性 | [教程](/docs/tutorials/dictionary-augmented-llm) |
| **少样本提示** | 在提示中包含示例翻译 | [教程](/docs/tutorials/few-shot-prompting) |
| **微调模型** | 在平行数据上训练（只是不在评估集上） | [教程](/docs/tutorials/fine-tuned-model) |
| **链式模型** | 多轮：草稿 → 精化 → 验证 | [教程](/docs/tutorials/chained-models) |
| **基于规则的混合** | 结合确定性规则和 LLM 灵活性 | [教程](/docs/tutorials/rule-based-hybrid) |

---

## 理解你的分数

基准测试运行后，你会看到如下输出：

```
══════════════════════════════════════════════════
  Composite Score: 0.67 (Functional)
──────────────────────────────────────────────────
  chrF++:              0.72
  FST acceptance:      0.82
  Exact match:         0.31
  Morphological acc.:  0.88
  Semantic score:      0.64
══════════════════════════════════════════════════
```

**关键指标：**

| 指标 | 测量内容 | 权重 |
|--------|-----------------|--------|
| **chrF++** | 字符级翻译准确度 | 30% |
| **FST 接受度** | 形态学有效性（对于有 FST 的语言） | 25% |
| **精确匹配** | 与参考完全相同的字符串 | 15% |
| **形态学准确度** | 词元 + 特征正确性 | 15% |
| **语义分数** | 意义保留，不考虑表面形式 | 15% |

**质量等级：**

| 等级 | 综合范围 | 含义 |
|------|----------------|---------------|
| 基线 | 0.00–0.30 | 低于该语言的随机概率 |
| 新兴 | 0.30–0.50 | 显示潜力但不可用 |
| 功能性 | 0.50–0.70 | 可用于后编辑 |
| **可部署** | **0.70–0.85** | **准备好生产，需要使用者审查** |
| 流畅 | 0.85–1.00 | 接近本地人质量 |

完整详情：[评分规范](/docs/specifications/scoring)

---

## 提交到排行榜

当你对分数满意时：

1. **对运行评分** — `mt-eval test eval/logs/your_run.json` 生成一个评分的 TestReport
2. **审查你的分数** — `mt-eval dashboard eval/logs/your_run.json` 生成一个可视化仪表板
3. **提交** — 按照[提交方法](/docs/getting-started/submit-a-method)指南操作

每个提交都被指纹识别到特定的配置和数据集版本。对测试内容没有歧义。

---

## 部署到生产

经过验证的方法可以通过 [champollion](https://champollion.dev) 部署，这是生产翻译 CLI。测试框架评估的相同接口成为一个翻译真实内容的插件。

```bash
# Export your benchmark as a champollion plugin
mt-eval export --report eval/logs/report.json --name crk-v1 --type llm-coached --locales crk
```

**[→ 部署到生产](/docs/getting-started/deploy-to-production)** — 将你的方法从竞技场带到生产。

---

## 故障排除

| 问题 | 解决方案 |
|---------|-----|
| `OPENROUTER_API_KEY not set` | 导出密钥或将其添加到 `.env`（见上面的设置） |
| `Model not found` | 运行 `mt-eval list models --live` 浏览可用模型 |
| 所有翻译都是空的 | 检查你的 API 密钥是否有额度。先尝试 `--dry-run` |
| `ModuleNotFoundError` | 确保你激活了 venv 并运行了 `pip install -e .` |
| 运行日志未保存 | 检查 `eval/logs/` — 日志按时间戳命名 |

---

## 另见

- [提交方法](/docs/getting-started/submit-a-method) — 分步提交指南
- [评分规范](/docs/specifications/scoring) — 完整的指标定义和权重
- [测试框架规范](/docs/specifications/harness) — 架构和配置参考
- [排行榜规则](/docs/leaderboard/rules) — 提交要求
- [数据主权](/docs/sovereignty/data-sovereignty) — OCAP、CARE 和社区治理
- **想使用现有方法？** 参见 [champollion Agent 指南](https://champollion.dev/docs/guides/agent-guide) — 一条命令安装和翻译。