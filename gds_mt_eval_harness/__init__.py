"""
gds-mt-eval-harness — A configurable, language-agnostic evaluation
harness for machine translation pipelines.

Two-component architecture:
    Run Harness:  Executes translation experiments with configurable
                  model, prompt, tools, batching, and caching.
    Test Harness: Analyzes run results offline with deterministic
                  linguistic metrics (chrF++, BLEU, exact match)
                  and extensible plugin metrics.

Any translation method can plug into the harness for regularized,
apple-to-apple comparison. See GUIDE.md for full documentation.
"""

__version__ = "0.1.0"

# Public API — importable from the top-level package
from gds_mt_eval_harness.config import RunConfig
from gds_mt_eval_harness.exporter import ExportConfig, export_plugin
from gds_mt_eval_harness.plugins.metrics import MetricPlugin
from gds_mt_eval_harness.plugins.prompts import PromptProvider
from gds_mt_eval_harness.plugins.hooks import PostTranslationHook
from gds_mt_eval_harness.plugins.tools import ToolProvider

__all__ = [
    "RunConfig",
    "ExportConfig",
    "export_plugin",
    "MetricPlugin",
    "PromptProvider",
    "PostTranslationHook",
    "ToolProvider",
]
