"""Plugin protocol definitions for mt-eval-harness."""

from mt_eval_harness.plugins.metrics import MetricPlugin
from mt_eval_harness.plugins.prompts import PromptProvider
from mt_eval_harness.plugins.hooks import PostTranslationHook
from mt_eval_harness.plugins.tools import ToolProvider

__all__ = [
    "MetricPlugin",
    "PromptProvider",
    "PostTranslationHook",
    "ToolProvider",
]
