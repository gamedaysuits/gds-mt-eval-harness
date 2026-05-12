"""
Async OpenRouter API Client — Unified HTTP layer for LLM calls.

Consolidates the duplicated API patterns from raw_llm_baseline.py,
v6_fst_gate.py, and v7_agent.py into a single, well-tested client.

Features:
    - Request construction with prompt caching (cache_control: ephemeral)
    - Automatic rate limit retry with exponential backoff
    - Timeout handling (configurable per call type)
    - Response parsing and error normalization
    - Dynamic pricing via OpenRouter /api/v1/models endpoint
    - Cost estimation from token counts + pricing data

Design decisions:
    - aiohttp session is managed externally (passed in, not owned)
    - Pricing table is fetched once per session, cached in memory
    - All errors are caught and returned as structured dicts (never throws)
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import aiohttp


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

# Timeout for standard (non-tool) calls
DEFAULT_TIMEOUT_S = 600
# Timeout for tool-calling calls (shorter, they're iterative)
TOOL_TIMEOUT_S = 120

# Maximum retry attempts for transient errors (429, 5xx)
MAX_RETRIES = 5
# Base delay for exponential backoff (seconds)
RETRY_BASE_DELAY = 2.0


# ---------------------------------------------------------------------------
# API key loader
# ---------------------------------------------------------------------------

def load_api_key() -> str:
    """Load OpenRouter API key from environment or .env / .env.local file.

    Search order:
        1. OPENROUTER_API_KEY environment variable
        2. .env.local in current directory or any parent
        3. .env in current directory or any parent
    """
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key

    # Use python-dotenv to search from CWD upward
    try:
        from dotenv import dotenv_values
        for filename in (".env.local", ".env"):
            from dotenv import find_dotenv
            env_path = find_dotenv(filename=filename, usecwd=True)
            if env_path:
                values = dotenv_values(env_path)
                key = values.get("OPENROUTER_API_KEY")
                if key:
                    return key
    except ImportError:
        pass

    raise RuntimeError(
        "OPENROUTER_API_KEY not found. "
        "Set it as an environment variable or in .env / .env.local"
    )


# ---------------------------------------------------------------------------
# Response cleaning — extract Cree from model output
# ---------------------------------------------------------------------------

# Default English reasoning prefixes that models emit before translation output.
# Override by passing reasoning_patterns to clean_response().
_DEFAULT_REASONING_PATTERNS = [
    "let me", "now ", "perfect", "based on", "i need", "i'll ",
    "the ", "for ", "here ", "so ", "first", "next", "this ",
    "using ", "since ", "checking", "looking", "translat",
    "sure", "of course", "certainly", "okay", "alright",
]


def clean_response(content: str, reasoning_patterns: list[str] | None = None) -> str:
    """Extract the translation from a model response.

    Language-agnostic strategy:
        1. Strip markdown formatting (bold, backticks, quotes)
        2. If single line, return it
        3. If multi-line, skip lines that look like source-language reasoning
           and return the first non-reasoning line
        4. Fall back to the last line

    Args:
        content: Raw model response text.
        reasoning_patterns: Optional list of lowercase prefixes to filter
            as reasoning lines. Defaults to English patterns. Pass an
            empty list to disable reasoning filtering entirely.

    This is intentionally conservative — if your target language uses
    Latin script, some reasoning lines may leak through. Register a
    custom TranslationProcess for fine-grained control.
    """
    if not content:
        return ""
    content = content.strip().strip('"').strip("'").strip("`")
    # Strip markdown bold wrapping
    if content.startswith("**") and content.endswith("**"):
        content = content[2:-2].strip()
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    if not lines:
        return content
    if len(lines) == 1:
        return lines[0]

    # Multi-line: skip reasoning, return first non-reasoning line
    patterns = reasoning_patterns if reasoning_patterns is not None else _DEFAULT_REASONING_PATTERNS
    for line in lines:
        low = line.lower().strip()
        if not low:
            continue
        # Skip lines that look like source-language meta-commentary
        if not any(low.startswith(p) for p in patterns):
            return line

    # All lines look like reasoning — fall back to last line
    return lines[-1]


# Pattern for extracting numbered lines from batch responses
_NUMBERED_LINE_RE = re.compile(
    r"^\s*(\d+)\s*[.):\-]\s*(.+)$", re.MULTILINE
)


def parse_numbered_response(content: str, expected: int) -> list[str]:
    """Extract translations from a numbered response (batch mode)."""
    matches = _NUMBERED_LINE_RE.findall(content)
    if len(matches) >= expected:
        return [m[1].strip() for m in matches[:expected]]

    # Fallback: split by newlines and strip leading numbers
    lines = [l.strip() for l in content.strip().split("\n") if l.strip()]
    cleaned = []
    for line in lines:
        m = re.match(r"^\s*\d+\s*[.):\-]\s*(.+)$", line)
        cleaned.append(m.group(1).strip() if m else line)

    while len(cleaned) < expected:
        cleaned.append("[PARSE_ERROR]")
    return cleaned[:expected]


# ---------------------------------------------------------------------------
# Pricing — dynamic from OpenRouter, with embedded fallback
# ---------------------------------------------------------------------------

# Embedded fallback pricing (USD per 1M tokens) for when API is unavailable.
# Updated: 2026-05-09. These are approximate and may drift.
_FALLBACK_PRICING: dict[str, dict[str, float]] = {
    "google/gemini-3.1-pro-preview":  {"input": 1.25,  "output": 10.0,  "cached": 0.31},
    "anthropic/claude-opus-4.7":      {"input": 15.0,  "output": 75.0,  "cached": 1.88},
    "anthropic/claude-opus-4.6":      {"input": 15.0,  "output": 75.0,  "cached": 1.88},
    "anthropic/claude-sonnet-4":      {"input": 3.0,   "output": 15.0,  "cached": 0.38},
    "openai/gpt-5.5":                {"input": 2.0,   "output": 8.0,   "cached": 0.50},
    "google/gemini-2.5-flash":        {"input": 0.15,  "output": 0.60,  "cached": 0.04},
    "google/gemini-3-flash-preview":  {"input": 0.15,  "output": 0.60,  "cached": 0.04},
    "deepseek/deepseek-v4-pro":       {"input": 0.90,  "output": 2.18,  "cached": 0.14},
    "deepseek/deepseek-r1-0528":      {"input": 0.55,  "output": 2.19,  "cached": 0.14},
}

# In-memory pricing cache (populated on first cost calculation)
_pricing_cache: dict[str, dict[str, float]] | None = None


async def fetch_pricing(
    session: aiohttp.ClientSession,
    api_key: str,
) -> dict[str, dict[str, float]]:
    """Fetch current model pricing from OpenRouter.

    Returns a dict mapping model_id to pricing info:
        {"input": float, "output": float, "cached": float}
    All values in USD per 1M tokens.

    Falls back to embedded table on network errors.
    """
    global _pricing_cache
    if _pricing_cache is not None:
        return _pricing_cache

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        async with session.get(
            OPENROUTER_MODELS_URL,
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                pricing = {}
                for model in data.get("data", []):
                    model_id = model.get("id", "")
                    model_pricing = model.get("pricing", {})
                    if model_pricing:
                        # OpenRouter returns pricing as strings in $/token
                        # Convert to $/1M tokens for readability
                        try:
                            prompt_price = float(model_pricing.get("prompt", "0"))
                            completion_price = float(model_pricing.get("completion", "0"))
                            # Cached pricing is typically not in API — estimate
                            cached_price = prompt_price * 0.25  # ~75% discount
                            pricing[model_id] = {
                                "input": prompt_price * 1_000_000,
                                "output": completion_price * 1_000_000,
                                "cached": cached_price * 1_000_000,
                            }
                        except (ValueError, TypeError):
                            continue
                if pricing:
                    _pricing_cache = pricing
                    return pricing
    except Exception:
        pass  # Fall back to embedded table

    _pricing_cache = _FALLBACK_PRICING
    return _FALLBACK_PRICING


def estimate_cost(
    usage: dict,
    model_id: str,
    pricing: dict[str, dict[str, float]],
) -> float:
    """Estimate API cost in USD from token usage and pricing data.

    Args:
        usage: Token usage dict from OpenRouter response.
        model_id: The full OpenRouter model ID.
        pricing: Pricing table from fetch_pricing().

    Returns:
        Estimated cost in USD.
    """
    model_price = pricing.get(model_id, _FALLBACK_PRICING.get(model_id, {}))
    if not model_price:
        return 0.0

    prompt_tok = usage.get("prompt_tokens", 0)
    completion_tok = usage.get("completion_tokens", 0)
    # Some providers report cached tokens inside prompt_tokens_details
    cached_tok = usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)

    uncached_prompt = max(0, prompt_tok - cached_tok)
    cost = (
        uncached_prompt * model_price.get("input", 0)
        + cached_tok * model_price.get("cached", 0)
        + completion_tok * model_price.get("output", 0)
    ) / 1_000_000  # Pricing is per 1M tokens

    return round(cost, 6)


# ---------------------------------------------------------------------------
# Core API call
# ---------------------------------------------------------------------------

async def call_openrouter(
    session: aiohttp.ClientSession,
    messages: list[dict],
    model_id: str,
    api_key: str,
    semaphore: asyncio.Semaphore,
    max_tokens: int = 13680,
    temperature: float = 0.0,
    tools: list[dict] | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> dict:
    """Make a single OpenRouter API call with retry logic.

    Args:
        session: Active aiohttp session.
        messages: Chat messages (system, user, assistant, tool).
        model_id: Full OpenRouter model ID.
        api_key: OpenRouter API key.
        semaphore: Concurrency limiter.
        max_tokens: Maximum response tokens.
        temperature: Sampling temperature.
        tools: Tool schemas for tool-calling mode (None to disable).
        timeout_s: Request timeout in seconds.

    Returns:
        Dict with keys:
            - content: str — text response (empty if tool_calls present)
            - tool_calls: list[dict] — tool call requests from model
            - usage: dict — token usage stats
            - latency_s: float — time taken
            - error: str | None — error message if failed
            - finish_reason: str — why the model stopped
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/gamedaysuits/gds-mt-eval-harness",
    }

    payload: dict[str, Any] = {
        "model": model_id,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if tools:
        payload["tools"] = tools

    for attempt in range(MAX_RETRIES):
        async with semaphore:
            start = time.monotonic()
            try:
                async with session.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=timeout_s),
                ) as resp:
                    elapsed = time.monotonic() - start

                    if resp.status == 429:
                        # Rate limited — backoff and retry
                        wait = RETRY_BASE_DELAY * (2 ** attempt)
                        await asyncio.sleep(wait)
                        continue

                    if resp.status != 200:
                        body = await resp.text()
                        if resp.status >= 500 and attempt < MAX_RETRIES - 1:
                            # Server error — retry with backoff
                            await asyncio.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                            continue
                        return {
                            "content": "",
                            "tool_calls": [],
                            "usage": {},
                            "latency_s": round(elapsed, 3),
                            "error": f"HTTP {resp.status}: {body[:300]}",
                            "finish_reason": "error",
                        }

                    data = await resp.json()

            except asyncio.TimeoutError:
                elapsed = time.monotonic() - start
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_BASE_DELAY * (2 ** attempt))
                    continue
                return {
                    "content": "",
                    "tool_calls": [],
                    "usage": {},
                    "latency_s": round(elapsed, 3),
                    "error": f"Timeout after {timeout_s}s",
                    "finish_reason": "timeout",
                }
            except Exception as e:
                elapsed = time.monotonic() - start
                return {
                    "content": "",
                    "tool_calls": [],
                    "usage": {},
                    "latency_s": round(elapsed, 3),
                    "error": str(e),
                    "finish_reason": "error",
                }

        # Parse successful response
        usage = data.get("usage", {})
        choices = data.get("choices", [])
        if not choices:
            return {
                "content": "",
                "tool_calls": [],
                "usage": usage,
                "latency_s": round(elapsed, 3),
                "error": "No choices in response",
                "finish_reason": "error",
            }

        msg = choices[0].get("message", {})
        finish_reason = choices[0].get("finish_reason", "stop")
        content = msg.get("content") or msg.get("text") or ""
        tool_calls = msg.get("tool_calls", [])

        return {
            "content": content,
            "tool_calls": tool_calls,
            "usage": usage,
            "latency_s": round(elapsed, 3),
            "error": None,
            "finish_reason": finish_reason,
            "raw_message": msg,  # Keep for tool-calling conversation continuation
        }

    # Exhausted all retries
    return {
        "content": "",
        "tool_calls": [],
        "usage": {},
        "latency_s": 0,
        "error": f"Exhausted {MAX_RETRIES} retries",
        "finish_reason": "error",
    }


def build_system_message(prompt_text: str) -> dict:
    """Build a system message with OpenRouter prompt caching enabled.

    Uses cache_control: ephemeral to cache the system prompt across
    calls. This is critical for coached prompts (~8k tokens) — without
    caching, each call re-tokenizes the full prompt.
    """
    return {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": prompt_text,
                "cache_control": {"type": "ephemeral"},
            }
        ],
    }
