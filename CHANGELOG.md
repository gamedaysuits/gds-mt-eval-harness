# Changelog

All notable changes to the MT Eval Harness (arena) are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0-rc.1] — 2026-06-07

### Added

- **COMET bootstrap confidence intervals** — CIs for COMET scores are now computed using cached per-entry scores. This avoids running neural inference 1,000× per bootstrap iteration by caching the initial per-entry COMET scores and bootstrapping from those cached values. Implementation: `_comet_from_cached_scores()` in `confidence.py`.
- **AfriCOMET auto-selection** — For 35 African languages (yor, hau, ibo, amh, swa, kin, lug, wol, etc.), the harness automatically selects `masakhane/africomet-mtl` instead of the default `Unbabel/wmt22-comet-da`. This provides better correlation with human quality judgments for African language pairs. Implementation: `resolve_comet_model()` and `COMET_MODEL_REGISTRY` in `metrics_comet.py`.
- **Per-difficulty-tier CIs** — Bootstrap confidence intervals are now computed per difficulty tier (Tier 1–5), stored as `confidence_intervals_by_tier` in the report JSON. Implementation: `compute_per_tier_cis()` in `confidence.py`.
- **Difficulty tier display** — Console summary now includes a per-tier breakdown table showing Count, Exact Match %, chrF++, BLEU, and chrF++ CI per difficulty level, with human-readable labels (Easy → Expert).
- **COMET column in compare** — `compare.py` now includes COMET scores in the side-by-side comparison table. Column only appears when at least one report has COMET data.
- **`--comet-model` CLI override** — Explicit COMET model selection via config dict, overriding auto-selection.
- **`resolve_comet_model()` public API** — Exported from package. Priority: CLI override → language registry → default model.
- **`COMET_MODEL_REGISTRY` public API** — Extensible dict mapping language codes to COMET model names.
- **`mt-eval setup` wizard** — Interactive command that installs optional dependencies (COMET, FST) with explanations. Users never need to know pip commands. Also provides contextual install prompts during eval runs when an optional metric is missing. Flags: `--all`, `--comet`, `--fst`, `--status`.
- **Canonical MethodConfig schema** — All config surfaces (method.json, run cards, export-config, leaderboard publish/install) now use the same 8-field canonical shape: `model`, `temperature`, `batchSize`, `register`, `coachingFile`, `coachingPrompt`, `promptContext`, `qualityTier`. All fields are always present; unused values are `null`.
- **`mt-eval export-config`** — New command that generates a `champollion.config.json` snippet from a TestReport, bridging harness evaluation results back to production config.
- **`ChampollionRunConfig`** — Renamed from `ChampollionPromptConfig` (back-compat alias kept). Now includes all 8 canonical MethodConfig fields (Python snake_case): `model`, `temperature`, `batch_size`, `register`, `coaching_file`, `coaching_prompt`, `prompt_context`, `quality_tier`.
- **Shared model aliases** — Both Python harness and JS CLI now load model aliases from `shared/model-aliases.json`. Default model changed from `gemini-3.1-pro` to `gemini-pro` (alias).
- **Full `--champollion-config` import** — The `--champollion-config` flag now imports model, temperature, batchSize, and coaching data from the production config (not just register/prompt). Explicit CLI flags override imported values.
- **Coaching prompt parity** — `build_champollion_system_prompt()` now includes a coaching guidance block between register and rules, byte-identical to the JS `buildSystemMessage()` in `cli/lib/methods/llm.js`.
- **Run card `method_config` block** — `publish.py` now writes the full canonical MethodConfig to each published run card, enabling zero-reconstruction leaderboard install.

### Changed

- `compute_comet()` now accepts optional `model_name` parameter for explicit model selection.
- `tester.py` COMET section now resolves model via `resolve_comet_model()` before scoring.
- `tester.py` COMET missing-dep message replaced with interactive install prompt — users can install COMET right from the eval flow, no pip commands needed.
- `__init__.py` exports `resolve_comet_model` and `COMET_MODEL_REGISTRY`.

## [3.0.0-rc.0] — 2026-06-05

### Added

- Multi-model parallel runs via comma-separated `-m` flag.
- Four corpus formats: JSON, JSONL, TSV, parallel text.
- Champollion config interop (`--champollion-config`).
- Plugin architecture: MetricPlugin, PromptProvider, ToolProvider, PostTranslationHook.
- Bootstrap 95% confidence intervals for chrF++, exact_match_rate, composite.
- Paired bootstrap significance testing.
- HTML dashboard generator.
- Run comparison with regression/improvement tracking.
- Plugin export for champollion method deployment.
- COMET neural metric (optional, `pip install mt-eval-harness[comet]`).
- FST acceptance metric (optional, `pip install mt-eval-harness[fst]`).
- Leaderboard publish with OAuth PKCE authentication.
