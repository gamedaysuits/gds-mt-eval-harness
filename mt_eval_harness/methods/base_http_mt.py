"""
HttpMTMethod — shared base class for REST-API machine-translation adapters.

This is the foundation for the "consumer-reports" MT systems-under-test
(Google Translate, DeepL, Microsoft Translator, LibreTranslate). It is shaped
to satisfy the ``mt_eval_harness.config.TranslationMethod`` protocol so the
harness can score these systems exactly like any LLM method.

WHAT THIS BASE PROVIDES (so subclasses stay tiny):
    - The async translate() loop: chunk entries into per-provider-limit
      batches, call the abstract ``_translate_texts()`` once per batch,
      capture per-entry latency + errors, and assemble protocol-shaped
      result dicts (id, predicted, latency_s, usage, error, tool_calls,
      tool_call_count, metadata).
    - Error isolation: a batch that raises (network error, bad status,
      length mismatch) marks each of its entries with ``error`` set and
      ``predicted=""`` — translate() never raises for an API failure, so a
      partial run still yields usable data (matching execute_run's "capture,
      never throw" contract).
    - A default ``method_card()`` built from class-level provenance fields.
    - Env-var key resolution helpers and the ``_resolve_lang_codes`` helper
      that maps human language NAMES → ISO codes via explicit code fields.

WHAT SUBCLASSES IMPLEMENT:
    - class attrs: ``name``, ``MAX_BATCH``, plus method-card provenance
      (``method_id``, ``description``, ``license``, ``commercial_ready``, …)
    - ``_resolve_credentials()`` → dict of resolved keys/urls (or raise
      MTConfigError if a required key is missing)
    - ``async _translate_texts(texts, src, tgt, creds)`` → list[str], one
      translation per input text, in order. Locale mapping happens here.

NO real network calls happen in tests — tests patch ``_translate_texts``
(or the aiohttp layer) so the suite is fully offline.
"""

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing only
    from mt_eval_harness.config import RunConfig


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class MTConfigError(RuntimeError):
    """Raised when an MT adapter cannot be configured to run.

    Two cases:
        - A required API key / endpoint is missing from the environment.
        - The run did not supply ISO language codes (source_code /
          target_code) and we only have human-readable language NAMES,
          which the MT REST APIs cannot consume.

    This is a configuration problem, not a per-entry translation failure —
    it is raised up front (before any HTTP) so the caller fails fast with an
    actionable message, rather than every entry silently erroring.
    """


# ---------------------------------------------------------------------------
# Env helpers — mirror the CLI's getEnvOrFileVar priority (env first).
# ---------------------------------------------------------------------------

def _env_first(*names: str) -> str | None:
    """Return the first non-empty environment variable among ``names``.

    Mirrors the CLI's resolution order: it checks each candidate env var in
    turn and returns the first that is set and non-empty. (The CLI also reads
    .env / .env.local files; the harness relies on the process environment,
    which is what runs/CI populate. Keeping it env-only also keeps tests
    hermetic.)
    """
    for name in names:
        val = os.environ.get(name)
        if val:
            return val
    return None


# ---------------------------------------------------------------------------
# Language code resolution
# ---------------------------------------------------------------------------

def _resolve_lang_codes(config: "RunConfig") -> tuple[str, str]:
    """Resolve (source_code, target_code) ISO codes from a run config.

    ``config.source_lang`` / ``config.target_lang`` are human-readable NAMES
    ("English", "Plains Cree (nêhiyawêwin, SRO)") used for LLM prompts — the
    MT REST APIs need ISO codes ("en", "crk"). This helper prefers explicit
    code fields if the config carries them:

        getattr(config, 'source_code', '')  /  getattr(config, 'target_code', '')

    Populating those fields from dataset/corpus metadata is the documented
    follow-up. Until then, a run that wants to use an MT adapter MUST supply
    codes. If they are absent we raise a clear MTConfigError telling the
    caller exactly what to provide, rather than guessing a code from a
    free-text language name (which would silently mistranslate).

    Returns:
        (source_code, target_code) — both non-empty ISO code strings.

    Raises:
        MTConfigError: if either code is missing/empty.
    """
    source_code = (getattr(config, "source_code", "") or "").strip()
    target_code = (getattr(config, "target_code", "") or "").strip()

    missing = []
    if not source_code:
        missing.append("source_code")
    if not target_code:
        missing.append("target_code")

    if missing:
        src_name = getattr(config, "source_lang", "") or "?"
        tgt_name = getattr(config, "target_lang", "") or "?"
        raise MTConfigError(
            "MT adapters require ISO language codes, but the run config is "
            f"missing: {', '.join(missing)}. "
            f"The config carries language NAMES (source_lang={src_name!r}, "
            f"target_lang={tgt_name!r}) which the MT REST APIs cannot use. "
            "Set config.source_code / config.target_code (e.g. 'en', 'crk') "
            "from the dataset/corpus metadata before running an MT method."
        )

    return source_code, target_code


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class HttpMTMethod:
    """Shared base for REST-API machine-translation methods.

    Implements the TranslationMethod protocol's async ``translate()`` so each
    provider subclass only has to describe *its* endpoint, auth, request
    shape, response parsing, and locale mapping.

    Subclass contract (override these):
        name:               human-readable method name (e.g. "google-translate")
        MAX_BATCH:          max source segments per HTTP request
        _resolve_credentials() -> dict
        async _translate_texts(texts, src, tgt, creds) -> list[str]

    Optional method-card provenance class attrs (used by method_card()):
        method_id, method_class, author, description, homepage,
        license, commercial_ready, cost_note
    """

    # --- Identity ---------------------------------------------------------
    name: str = "http-mt"

    # --- Batching ---------------------------------------------------------
    # Max source segments per request. Subclasses override to each
    # provider's documented limit.
    MAX_BATCH: int = 64

    # --- Method-card provenance (subclasses override) ---------------------
    method_id: str = "http-mt"
    method_class: str = "machine-translation-api"
    author: str = "Champollion MT Eval"
    description: str = "Generic REST machine-translation adapter."
    homepage: str = ""
    license: str = "unknown"
    commercial_ready: bool = False
    cost_note: str = ""

    def __init__(self, **options: Any) -> None:
        """Accept arbitrary keyword options (e.g. explicit api_key, endpoint).

        Options are stored on ``self.options`` and consulted by each
        subclass's ``_resolve_credentials()`` before falling back to env
        vars — mirroring the CLI's ``options.googleApiKey || env`` pattern.
        """
        self.options = options

    # --- Provenance -------------------------------------------------------

    def method_card(self) -> dict | None:
        """Return method metadata for provenance tracking.

        Embedded in the RunLog / published run card so a result can be
        attributed to a specific MT system. Subclasses normally just set the
        provenance class attrs and inherit this.
        """
        return {
            "name": self.name,
            "method_id": self.method_id,
            "class": self.method_class,
            "author": self.author,
            "description": self.description,
            "homepage": self.homepage,
            # Consumer-reports MT systems are black boxes — no source text
            # leaves except the segment, no tools, no coaching data.
            "tools_used": [],
            "supported_pairs": "provider-defined",
            "license": self.license,
            "commercialReady": self.commercial_ready,
            "cost_note": self.cost_note,
        }

    # --- Credentials (subclass hook) -------------------------------------

    def _resolve_credentials(self) -> dict:
        """Resolve API keys / endpoints needed to translate.

        Subclasses return a dict (consumed by ``_translate_texts``). Raise
        MTConfigError if a required key is missing. The base implementation
        returns an empty dict (no credentials required).
        """
        return {}

    # --- Translation backend (subclass hook) -----------------------------

    async def _translate_texts(
        self,
        texts: list[str],
        src: str,
        tgt: str,
        creds: dict,
    ) -> list[str]:
        """Translate a batch of source strings → list of translations.

        Must return exactly ``len(texts)`` strings, in the same order.
        Locale mapping (e.g. Google he→iw) happens inside the subclass, on
        the ISO codes passed in as ``src`` / ``tgt``.

        Raise on any failure (bad status, network error, length mismatch);
        the base ``translate()`` catches it and marks the batch's entries as
        errored.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement _translate_texts()"
        )

    # --- Result shaping ---------------------------------------------------

    @staticmethod
    def _result(
        entry_id: Any,
        predicted: str,
        latency_s: float,
        error: str | None,
        usage: dict | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Assemble one protocol-shaped result dict.

        Matches the per-entry shape produced by the built-in strategies
        (see strategies/single.py): id, predicted, latency_s, usage,
        tool_calls, tool_call_count, error, metadata.
        """
        return {
            "id": entry_id,
            "predicted": predicted,
            "latency_s": float(latency_s),
            "usage": usage if usage is not None else {},
            "error": error,
            "tool_calls": [],
            "tool_call_count": 0,
            "metadata": metadata if metadata is not None else {},
        }

    # --- Main async loop --------------------------------------------------

    async def translate(
        self,
        entries: list[dict],
        config: "RunConfig",
    ) -> list[dict]:
        """Translate a batch of entries via the provider REST API.

        Returns one result dict per input entry, in input order. A failed
        batch (network error, bad status, length mismatch) does NOT raise:
        each entry in that batch gets ``error`` set and ``predicted=""``.

        A configuration problem (missing key, missing language codes) DOES
        raise MTConfigError — that is an up-front, run-wide failure, not a
        per-entry one, and should stop the run before any HTTP.
        """
        # Resolve up-front config — these raise (run cannot proceed at all).
        src, tgt = _resolve_lang_codes(config)
        creds = self._resolve_credentials()

        source_field = getattr(config, "source_field", "source") or "source"

        results: list[dict] = []

        # Process in provider-sized chunks. Each chunk is one HTTP request.
        for start in range(0, len(entries), self.MAX_BATCH):
            chunk = entries[start:start + self.MAX_BATCH]
            texts = [str(e.get(source_field, "")) for e in chunk]

            t0 = time.monotonic()
            try:
                translations = await self._translate_texts(
                    texts, src, tgt, creds,
                )
                elapsed = time.monotonic() - t0

                if len(translations) != len(chunk):
                    raise ValueError(
                        f"{self.name}: response length mismatch "
                        f"(expected {len(chunk)}, got {len(translations)})"
                    )

                # Amortize the batch latency across its entries so per-entry
                # latency_s sums back to wall-clock (matches batch strategy).
                per_latency = elapsed / len(chunk) if chunk else 0.0
                for entry, translated in zip(chunk, translations):
                    results.append(
                        self._result(
                            entry_id=entry.get("id"),
                            predicted=translated if translated is not None else "",
                            latency_s=per_latency,
                            error=None,
                        )
                    )
            except Exception as exc:  # noqa: BLE001 - capture, never throw
                elapsed = time.monotonic() - t0
                per_latency = elapsed / len(chunk) if chunk else 0.0
                err = f"{type(exc).__name__}: {exc}"
                for entry in chunk:
                    results.append(
                        self._result(
                            entry_id=entry.get("id"),
                            predicted="",
                            latency_s=per_latency,
                            error=err,
                        )
                    )

        return results
