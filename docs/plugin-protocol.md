# Plugin Protocol

This document describes how external translation methods plug into the
eval harness. A plugin implements the `TranslationProcess` protocol and
gets registered via the `--process` CLI flag (v2.2) or programmatically.

## Architecture

```
Eval Harness (mt-eval run)
├── Built-in strategies
│   ├── SingleStrategy     ← one entry per API call
│   ├── BatchStrategy      ← multiple entries per call
│   └── ToolCallStrategy   ← entry + tool-calling loop
│
└── Plugin strategy
    └── ProcessStrategy    ← delegates to TranslationProcess
        └── Your plugin    ← implements the protocol below
```

## The TranslationProcess Protocol

Any Python class that implements this method signature works:

```python
from mt_eval_harness.config import RunConfig

class MyTranslationMethod:
    """Example plugin — wraps an external API or pipeline."""

    async def translate(
        self,
        entries: list[dict],
        config: RunConfig,
    ) -> list[dict]:
        """Translate a batch of entries.

        Args:
            entries: List of dicts, each containing at minimum:
                - id: int — entry ID from the corpus
                - source: str — source text (field name from config.source_field)

            config: Full run configuration for context (model, temperature, etc.)

        Returns:
            List of result dicts, one per entry, each containing:
                - id: int — same entry ID
                - predicted: str — the translated text
                - latency_s: float — time taken in seconds
                - usage: dict — token usage {prompt_tokens, completion_tokens}
                - error: str | None — error message if translation failed
                - tool_calls: list[dict] — tool call log (empty if no tools)
                - tool_call_count: int — total tool calls made
                - metadata: dict — any process-specific metadata
        """
        results = []
        for entry in entries:
            translation = await self._my_translate(entry[config.source_field])
            results.append({
                "id": entry["id"],
                "predicted": translation,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "error": None,
                "tool_calls": [],
                "tool_call_count": 0,
                "metadata": {"plugin": "my-method"},
            })
        return results
```

### Why a Protocol (not a base class)

The harness uses Python's `typing.Protocol` for **structural typing**.
Your plugin doesn't need to inherit from anything. If it has the right
`translate` method signature, it works. This means existing translation
pipelines can be adapted without modification.

## Wrapping Non-Python Methods

Since the protocol is Python, non-Python methods need a thin wrapper:

### Example: Wrapping an FST binary

```python
import subprocess

class FSTTranslationPlugin:
    """Wraps an HFST binary for morphological translation."""

    def __init__(self, analyzer_path: str):
        self.analyzer = analyzer_path

    async def translate(self, entries, config):
        results = []
        for entry in entries:
            # Call the FST binary via subprocess
            proc = subprocess.run(
                [self.analyzer],
                input=entry[config.source_field],
                capture_output=True, text=True,
            )
            results.append({
                "id": entry["id"],
                "predicted": proc.stdout.strip(),
                "latency_s": 0.1,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "error": proc.stderr if proc.returncode != 0 else None,
                "tool_calls": [],
                "tool_call_count": 0,
                "metadata": {"analyzer": self.analyzer},
            })
        return results
```

### Example: Wrapping an HTTP API

```python
import aiohttp
import time

class APITranslationPlugin:
    """Wraps a third-party translation API."""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    async def translate(self, entries, config):
        results = []
        async with aiohttp.ClientSession() as session:
            for entry in entries:
                start = time.monotonic()
                async with session.post(
                    self.api_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"text": entry[config.source_field]},
                ) as resp:
                    data = await resp.json()
                elapsed = time.monotonic() - start

                results.append({
                    "id": entry["id"],
                    "predicted": data.get("translation", ""),
                    "latency_s": elapsed,
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                    "error": data.get("error"),
                    "tool_calls": [],
                    "tool_call_count": 0,
                    "metadata": {"api": self.api_url},
                })
        return results
```

## Registration (v2.2 — Planned)

Currently, plugins are registered programmatically:

```python
from mt_eval_harness.config import RunConfig
from mt_eval_harness.runner import execute_run

config = RunConfig(
    corpus_path="data/corpus.json",
    process_name="my-method",
)

# Register the plugin and run
my_plugin = MyTranslationMethod()
await execute_run(config, process=my_plugin)
```

In v2.2, plugins will be discoverable via CLI:

```bash
# Path-based discovery
mt-eval run --corpus data/corpus.json --process ./my_plugin/

# Entry-point discovery (pip-installed plugins)
mt-eval run --corpus data/corpus.json --process my-translation-plugin
```

## Relationship to i18n-rosetta

The eval harness and i18n-rosetta share a common concept of "translation method"
but have different interfaces:

| | Eval Harness | i18n-rosetta |
|---|---|---|
| **Language** | Python | Node.js |
| **Entry point** | `translate.py` | `translate.js` |
| **Interface** | `TranslationProcess` protocol | `methodPlugin` config |
| **Purpose** | Batch evaluation | Live localization |

A method that supports both provides two entry points:

```
my-method/
├── manifest.json         # Shared metadata
├── method_card.json      # Leaderboard description
├── translate.py          # For eval harness
└── translate.js          # For i18n-rosetta
```

The **method card** is the bridge: it describes the method in a format
both systems understand, regardless of which entry point is used.
