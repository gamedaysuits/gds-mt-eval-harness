"""
Provider registry — maps provider name strings to LLMProvider instances.

The registry uses the same vocabulary as the CLI's METHOD_REGISTRY
(cli/lib/translate.js) for direct provider names. This eliminates the
brittle mapping layer between harness and CLI terminology.

Provider names:
    "openrouter"  → OpenRouterProvider (default, proxies any model)
    "openai"      → OpenAIProvider     (direct OpenAI API)
    "anthropic"   → AnthropicProvider  (direct Anthropic API)
    "gemini"      → GeminiProvider     (direct Google Gemini API)

Usage:
    provider = get_provider("openai")
    api_key = provider.load_api_key()
"""

from __future__ import annotations

from mt_eval_harness.providers.base import LLMProvider


# Lazy imports to avoid loading provider modules until actually needed.
# This keeps startup fast and avoids import errors for unused providers.
def _openrouter() -> LLMProvider:
    from mt_eval_harness.providers.openrouter import OpenRouterProvider
    return OpenRouterProvider()


def _openai() -> LLMProvider:
    from mt_eval_harness.providers.openai_provider import OpenAIProvider
    return OpenAIProvider()


def _anthropic() -> LLMProvider:
    from mt_eval_harness.providers.anthropic_provider import AnthropicProvider
    return AnthropicProvider()


def _gemini() -> LLMProvider:
    from mt_eval_harness.providers.gemini_provider import GeminiProvider
    return GeminiProvider()


# Maps provider name → lazy constructor.
# These names match the CLI's METHOD_REGISTRY for direct providers
# ("openai", "anthropic", "gemini") and extend it with "openrouter"
# for the harness's proxy-based default.
PROVIDER_REGISTRY: dict[str, callable] = {
    "openrouter": _openrouter,
    "openai": _openai,
    "anthropic": _anthropic,
    "gemini": _gemini,
}


def get_provider(name: str | None = None) -> LLMProvider:
    """Get an LLMProvider instance by name.

    Args:
        name: Provider name (one of PROVIDER_REGISTRY keys).
              None or empty string defaults to "openrouter".

    Returns:
        An LLMProvider instance ready to use.

    Raises:
        ValueError: If the provider name is not recognized.
    """
    resolved = (name or "openrouter").strip().lower()

    factory = PROVIDER_REGISTRY.get(resolved)
    if factory is None:
        available = ", ".join(sorted(PROVIDER_REGISTRY.keys()))
        raise ValueError(
            f"Unknown provider '{resolved}'. "
            f"Available: {available}. "
            f"Set --provider or config.provider to one of these."
        )

    return factory()
