"""
Config exporter — generate champollion.config.json snippets from TestReports.

Usage:
    mt-eval export-config --report report.json --target-lang-code crk

Produces a JSON fragment using the canonical MethodConfig shape that can
be merged directly into an existing champollion.config.json. The format is
identical to what method.json, the leaderboard, and --install use.

Why:
    After finding a winning configuration in the harness, this command
    generates the exact champollion.config.json settings needed to deploy
    that configuration in production. "Test what you ship."
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from mt_eval_harness.config import MODEL_REGISTRY
from mt_eval_harness.scoring import classify_quality_tier

# Version of the export format. Bumped when fields are added/changed.
EXPORT_FORMAT_VERSION = "1.0.0"

# The CLI's valid `defaultMethod` values — the keys of its METHOD_REGISTRY
# (cli/lib/translate.js). The harness uses a DIFFERENT vocabulary internally
# (`prompt_version`: naive | coached | custom | champollion), so an export
# MUST translate; a raw passthrough writes a config the CLI rejects with
# "Unknown translation method" (pre-launch audit 2026-06-13, blocking #1).
_CLI_METHODS = frozenset({
    "llm", "llm-coached", "google-translate", "api", "deepl",
    "microsoft-translator", "libretranslate", "openai", "anthropic",
    "gemini", "external",
})

# Harness prompt_version -> CLI defaultMethod. `custom` and `champollion`
# are harness-only prompt strategies with no portable CLI equivalent; we map
# them to the closest deployable method (coached) and annotate the snippet so
# the operator knows the prompt nuance is not reproduced by the CLI.
_PROMPT_VERSION_TO_METHOD = {
    "naive": "llm",
    "coached": "llm-coached",
    "custom": "llm-coached",
    "champollion": "llm-coached",
}
_NON_PORTABLE_PROMPT_VERSIONS = frozenset({"custom", "champollion"})


def _resolve_default_method(prompt_version: str | None) -> tuple[str, str | None]:
    """Map a harness `prompt_version` to a CLI-valid `defaultMethod`.

    Returns (method, note). `note` is a human-readable caveat when the
    harness prompt strategy has no exact CLI equivalent, else None.
    Raises ValueError if the result is somehow not a CLI method — the
    export refuses to emit a config that would crash the CLI.
    """
    pv = (prompt_version or "naive").strip()
    method = _PROMPT_VERSION_TO_METHOD.get(pv)
    note = None
    if method is None:
        # Unknown prompt_version — fail loud rather than passthrough.
        raise ValueError(
            f"Cannot export config: unknown prompt_version {pv!r}. "
            f"Known: {sorted(_PROMPT_VERSION_TO_METHOD)}. "
            f"Add a mapping in config_exporter._PROMPT_VERSION_TO_METHOD."
        )
    if pv in _NON_PORTABLE_PROMPT_VERSIONS:
        note = (
            f"Harness prompt mode {pv!r} has no exact CLI equivalent; "
            f"exported as {method!r}. The CLI will reproduce the model and "
            f"settings but not the {pv!r} prompt strategy."
        )
    if method not in _CLI_METHODS:  # defensive — should be unreachable
        raise ValueError(
            f"Internal error: mapped method {method!r} is not a valid CLI "
            f"method {sorted(_CLI_METHODS)}."
        )
    return method, note


def _extract_composite_score(overall: dict) -> float | None:
    """Pull the composite score out of a TestReport's `overall` block.

    TestReports store the composite under
    `overall.confidence_intervals.composite_score.score`, not as a
    top-level `overall.composite_score`. Check the CI block first, then
    fall back to a top-level key for forward compatibility.
    """
    ci_block = overall.get("confidence_intervals") or {}
    composite_ci = ci_block.get("composite_score") or {}
    score = composite_ci.get("score")
    if score is not None:
        return score
    return overall.get("composite_score")


def export_champollion_config(
    report_path: str | Path,
    target_lang_code: str,
    output_path: str | Path | None = None,
) -> dict:
    """Read a TestReport and emit a champollion.config.json snippet.

    The output uses the canonical MethodConfig shape — the same field names
    and structure used by champollion.config.json, method.json, leaderboard
    publish, and leaderboard install.

    Args:
        report_path: Path to the TestReport JSON file.
        target_lang_code: BCP-47 language code (e.g., "crk", "fr").
        output_path: Path to write the JSON output. If None, writes to stdout.

    Returns:
        The config snippet as a dict.
    """
    report_path = Path(report_path)
    if not report_path.exists():
        print(f"ERROR: Report not found: {report_path}", file=sys.stderr)
        sys.exit(1)

    report = json.loads(report_path.read_text(encoding="utf-8"))
    config = report.get("config", {})
    overall = report.get("overall", {})

    # Resolve model ID to full slug
    model_raw = config.get("model", "")
    model = MODEL_REGISTRY.get(model_raw, model_raw)

    # Build the canonical MethodConfig
    method_config = {
        "model": model,
        "temperature": config.get("temperature"),
        "batchSize": config.get("batch_size"),
        "register": None,  # Comes from language card, not the report
        "coachingFile": config.get("coaching_file"),
        "coachingPrompt": None,  # Resolved at runtime — not stored
        "promptContext": None,  # Comes from project config, not the report
        "qualityTier": None,
    }

    # Extract register from provenance if available
    provenance = report.get("provenance", {})
    if provenance.get("register_used"):
        method_config["register"] = provenance["register_used"]

    # Build quality tier from scores. Reports don't store a tier — derive
    # it from the composite (SCORING_SPEC §5.1), preferring an explicit
    # report value if a future format adds one.
    composite_score = _extract_composite_score(overall)
    quality_tier = overall.get("quality_tier")
    if quality_tier is None and composite_score is not None:
        quality_tier = classify_quality_tier(composite_score)
    if quality_tier:
        method_config["qualityTier"] = quality_tier

    # Map the harness prompt strategy to a CLI-valid method (never a raw
    # passthrough — see _resolve_default_method).
    default_method, method_note = _resolve_default_method(
        config.get("prompt_version")
    )

    # Detect source language
    source_lang_code = config.get("source_lang_code", "en")
    target_lang_name = config.get("target_lang", target_lang_code)

    # Assemble the export snippet
    # This is a mergeable fragment — the user pastes it into their
    # existing champollion.config.json.
    snippet = {
        "_generated_by": f"mt-eval-harness export-config v{EXPORT_FORMAT_VERSION}",
        "_source": str(report_path.name),
        "_timestamp": report.get("timestamp", ""),
        # Top-level method defaults
        "model": method_config["model"],
        "temperature": method_config["temperature"],
        "batchSize": method_config["batchSize"],
        "defaultMethod": default_method,
        # Per-language settings
        "languages": {
            target_lang_code: {
                "register": method_config["register"],
            },
        },
    }
    if method_note:
        snippet["_method_note"] = method_note

    # Include coaching file reference if used
    if method_config["coachingFile"]:
        snippet["coachingFile"] = method_config["coachingFile"]

    # Include per-pair override if source isn't English. Carry the source
    # code explicitly (inputLocale) so a non-English-source config doesn't
    # silently default to English on the CLI side.
    if source_lang_code and source_lang_code != "en":
        pair_key = f"{source_lang_code}:{target_lang_code}"
        snippet["inputLocale"] = source_lang_code
        snippet["pairs"] = {
            pair_key: {
                "model": method_config["model"],
                "temperature": method_config["temperature"],
            },
        }

    # Add benchmark summary for reference (not config, just FYI)
    snippet["_benchmark_summary"] = {
        "corpus_size": overall.get("total_entries", 0),
        "exact_match_rate": overall.get("exact_match_rate"),
        "chrf_plus_plus": overall.get("corpus_chrf"),
        "composite_score": composite_score,
        "quality_tier": quality_tier,
    }

    # Output
    output_json = json.dumps(snippet, indent=2, ensure_ascii=False) + "\n"

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json, encoding="utf-8")
        print(f"  ✅ Config snippet written to: {output_path}")
    else:
        print(output_json)

    return snippet


def cmd_export_config(args) -> None:
    """CLI entry point for the export-config subcommand."""
    export_champollion_config(
        report_path=args.report,
        target_lang_code=args.target_lang_code,
        output_path=getattr(args, "output", None),
    )
