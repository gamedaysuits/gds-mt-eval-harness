"""
MicrosoftTranslatorMethod — Azure Cognitive Services Translator v3 adapter.

Mirrors the Champollion CLI (cli/lib/methods/microsoft-translator.js) so a
user's existing key works for both:

    Endpoint:  POST https://api.cognitive.microsofttranslator.com/translate
                    ?api-version=3.0&from=<src>&to=<tgt>
    Body:      [{"Text": "..."}, ...]
    Auth:      header  Ocp-Apim-Subscription-Key: <key>
               header  Ocp-Apim-Subscription-Region: <region>   (if set)
    Env:       MICROSOFT_TRANSLATOR_API_KEY  (+ MICROSOFT_TRANSLATOR_REGION)
    Batch:     max 100 segments / request
    Response:  json[i]["translations"][0]["text"]
    Locale:    pass-through (Azure uses BCP-47; no special remap)
    Cost:      proprietary; free tier 2M chars/month
"""

from __future__ import annotations

from urllib.parse import urlencode

import aiohttp

from mt_eval_harness.methods.base_http_mt import (
    HttpMTMethod,
    MTConfigError,
    _env_first,
)

MICROSOFT_API_BASE = "https://api.cognitive.microsofttranslator.com/translate"
MICROSOFT_API_VERSION = "3.0"


class MicrosoftTranslatorMethod(HttpMTMethod):
    """Microsoft (Azure) Translator v3 system-under-test."""

    name = "microsoft-translator"
    MAX_BATCH = 100

    method_id = "microsoft-translator-v3"
    method_class = "machine-translation-api"
    author = "Microsoft"
    description = "Azure Cognitive Services Translator v3 — neural MT, 100+ languages."
    homepage = "https://learn.microsoft.com/azure/ai-services/translator/"
    license = "Proprietary (Microsoft ToS)"
    commercial_ready = True
    cost_note = "Proprietary; free tier 2M chars/month"

    # --- Locale mapping ---------------------------------------------------

    @staticmethod
    def _map_locale(code: str) -> str:
        """Azure Translator uses BCP-47 codes directly — pass through."""
        return code

    # --- Credentials ------------------------------------------------------

    def _resolve_credentials(self) -> dict:
        api_key = (
            self.options.get("microsoft_api_key")
            or _env_first("MICROSOFT_TRANSLATOR_API_KEY")
        )
        if not api_key:
            raise MTConfigError(
                "Microsoft Translator: no API key found. Set "
                "MICROSOFT_TRANSLATOR_API_KEY in your environment."
            )
        # Region is optional (global resources omit it); pass through if set.
        region = (
            self.options.get("microsoft_region")
            or _env_first("MICROSOFT_TRANSLATOR_REGION")
        )
        return {"api_key": api_key, "region": region}

    # --- Request / response (factored out for direct testing) -------------

    def _build_request(
        self,
        texts: list[str],
        src: str,
        tgt: str,
        api_key: str,
        region: str | None,
    ) -> dict:
        """Build kwargs for the aiohttp POST (url/json/headers)."""
        query = urlencode({
            "api-version": MICROSOFT_API_VERSION,
            "from": self._map_locale(src),
            "to": self._map_locale(tgt),
        })
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Ocp-Apim-Subscription-Key": api_key,
        }
        if region:
            headers["Ocp-Apim-Subscription-Region"] = region
        return {
            "url": f"{MICROSOFT_API_BASE}?{query}",
            "json": [{"Text": t} for t in texts],
            "headers": headers,
        }

    @staticmethod
    def _parse_response(payload: list, expected: int) -> list[str]:
        if not payload or len(payload) != expected:
            got = len(payload) if payload else 0
            raise ValueError(
                f"Microsoft Translator: response length mismatch "
                f"(expected {expected}, got {got})"
            )
        return [item["translations"][0]["text"] for item in payload]

    # --- Backend ----------------------------------------------------------

    async def _translate_texts(
        self,
        texts: list[str],
        src: str,
        tgt: str,
        creds: dict,
    ) -> list[str]:
        req = self._build_request(
            texts, src, tgt, creds["api_key"], creds.get("region"),
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(**req) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise RuntimeError(
                        f"Microsoft Translator: HTTP {resp.status} — {body}"
                    )
                payload = await resp.json()
        return self._parse_response(payload, len(texts))
