"""Plugin protocol definitions for gds-mt-eval-harness."""

from gds_mt_eval_harness.plugins.metrics import MetricPlugin
from gds_mt_eval_harness.plugins.prompts import PromptProvider
from gds_mt_eval_harness.plugins.hooks import PostTranslationHook
from gds_mt_eval_harness.plugins.tools import ToolProvider

__all__ = [
    "MetricPlugin",
    "PromptProvider",
    "PostTranslationHook",
    "ToolProvider",
]
