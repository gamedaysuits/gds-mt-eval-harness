---
sidebar_position: 3
title: "Gabay ng Agent: Pagwagi sa Arena"
description: "Paano makabubuo ang AI agents ng mga pamamaraan sa pagsasalin, masusukat ang mga ito sa benchmark, at makapagsusumite sa leaderboard."
related:
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
  - label: "Agent Guide: Using champollion"
    to: https://champollion.dev/docs/guides/agent-guide
    kind: champollion
    note: "The production-side guide for the same agents"
---
# Gabay ng Agent: Pagwawagi sa Arena

Ang MT Eval Arena ay isang bukás na platformang benchmarking para sa mga pamamaraan ng machine translation. Bumuo po kayo ng pamamaraang nagsasalin nang mas mahusay kaysa sa mga kasalukuyan, patunayan ito gamit ang reproducible scoring, at ang nanalong pamamaraan ay ide-deploy sa production — na may revenue na dadaloy sa language community na pinaglilingkuran nito.

:::tip Bakit mahalaga ito
Saklaw ng mga komersyal na serbisyo sa pagsasalin ang ~130 wika. Inaangkin ng Meta's OMT-1600 ang 1,600 pa — ngunit para sa ~1,300 sa kanilang pinakamababang resource tiers, hindi pa nabeberipika ang kalidad sa pamamagitan ng independiyenteng ebalwasyon at hindi available ang model weights. Ibinibigay ng Arena ang independiyenteng imprastraktura sa pagsubok. Kung gumagana ang inyong pamamaraan, maaari itong umabot sa production para sa mga wikang walang umiiral na independiyenteng nabeberipikang MT.
:::

---

## Pag-set Up ng Environment

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena

# Create a virtual environment (do NOT install into global Python)
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -e .
```

**API key** — ginagamit ng harness ang OpenRouter upang tumawag ng mga LLM model. Itakda po ang inyong key:

```bash
# Option 1: export (session only)
export OPENROUTER_API_KEY="sk-or-..."

# Option 2: .env file (persistent, gitignored)
echo 'OPENROUTER_API_KEY=sk-or-...' > .env
```

Kumuha ng key sa [openrouter.ai/keys](https://openrouter.ai/keys). Gumagana ang mga free-tier model para sa eksperimento.

---

## Patakbuhin ang Inyong Unang Benchmark

```bash
# Run a baseline LLM against the Cree evaluation corpus
mt-eval run --corpus data/edtekla-dev-v1.json

# Or specify a model explicitly
mt-eval run --corpus data/edtekla-dev-v1.json -m google/gemini-2.5-flash
```

Gumagawa ang harness ng **run log** — isang JSON file na sine-save sa `eval/logs/` na naglalaman ng bawat salin, bawat metric score, at isang cryptographic fingerprint na nag-uugnay ng mga resulta sa eksaktong configuration ng eksperimento.

**Mga kapaki-pakinabang na flag:**

| Flag | Ginagawa nito |
|------|-------------|
| `-m <model>` | OpenRouter model slug (paghiwalayin gamit ang kuwit para sa multi-model parallel runs) |
| `--condition <name>` | Label para sa inyong pamamaraan (lumalabas sa leaderboard) |
| `--temperature <float>` | Sampling temperature (mas mababa = mas deterministic) |
| `--batch-size <n>` | Mga entry kada API call (default: 25) |
| `--dry-run` | I-validate ang config nang hindi gumagawa ng API calls |
| `--ids 0,1,2,3` | Patakbuhin lamang ang mga partikular na entry ID |

```bash
# Multi-model comparison (runs in parallel)
mt-eval run --corpus data/edtekla-dev-v1.json -m gemini-2.5-flash,claude-sonnet-4,gpt-4.1

# Dry run to validate config
mt-eval run --corpus data/edtekla-dev-v1.json --dry-run
```

Iba pang command: `mt-eval test <log.json>` (i-score ang nakumpletong run), `mt-eval compare <log1> <log2>` (ikumpara ang mga run), `mt-eval dashboard <logs/*.json>` (bumuo ng HTML dashboard), `mt-eval list models --live` (mag-browse ng mga available na model).

---

## Bumuo ng Sarili Ninyong Pamamaraan

Tumatanggap ang harness ng anumang Python class na nag-iimplement ng `TranslationMethod` protocol:

```python
from mt_eval_harness.config import RunConfig

class YourMethod:
    """Build whatever you want inside. The harness only sees this interface."""

    async def translate(
        self,
        entries: list[dict],
        config: RunConfig,
    ) -> list[dict]:
        """
        Args:
            entries: [{"id": 1, "source": "Hello"}, ...]
            config:  RunConfig with source_locale, target_locale, model, etc.

        Returns: one result dict per entry, each containing:
            - id: int          — entry ID from the corpus
            - predicted: str   — the translated text
            - latency_s: float — time taken in seconds
            - usage: dict      — token usage {prompt_tokens, completion_tokens}
            - error: str|None  — error message if failed
            - metadata: dict   — any process-specific metadata
        """
        results = []
        for entry in entries:
            # Your translation logic here — LLM prompting, FST pipeline,
            # dictionary lookup, fine-tuned model, anything.
            translated = await self._my_translate(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translated,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
                "error": None,
                "metadata": {"method": "my-custom-pipeline"},
            })
        return results
```

**Structural typing** — hindi kailangang mag-inherit ang inyong class mula sa anumang bagay. Kung mayroon itong tamang `translate` method signature, gagana ito. Ibig sabihin, maaaring i-adapt ang mga umiiral na pipeline gamit ang isang manipis na wrapper.

**Ikonekta ito sa harness:**

```python
import asyncio
from mt_eval_harness.config import RunConfig
from mt_eval_harness.runner import execute_run

async def main():
    config = RunConfig(
        corpus_path="data/edtekla-dev-v1.json",
        model="google/gemini-2.5-flash",
        condition="my-method-v1",
    )
    results = await execute_run(config, method=YourMethod())
    print(f"Composite: {results['scores']['composite']}")

asyncio.run(main())
```

---

## Mga Ideya sa Pamamaraan

Bawat isa sa mga ito ay may kumpletong cookbook na may gabay sa implementasyon:

| Pamamaraan | Paglalarawan | Cookbook |
|----------|-------------|---------|
| **FST-gated pipeline** | Nahuhuli ng morphological validation ang hindi napapansin ng LLMs | [Tutorial](/docs/tutorials/fst-gated-pipeline) |
| **Coached LLM** | Mag-inject ng grammar rules at dictionaries sa mga prompt | [Tutorial](/docs/tutorials/coached-llm-prompting) |
| **Dictionary-augmented** | Ipilit ang pagkakapare-pareho ng terminology | [Tutorial](/docs/tutorials/dictionary-augmented-llm) |
| **Few-shot prompting** | Isama ang mga halimbawang salin sa prompt | [Tutorial](/docs/tutorials/few-shot-prompting) |
| **Fine-tuned model** | Sanayin gamit ang parallel data (huwag lamang sa eval set) | [Tutorial](/docs/tutorials/fine-tuned-model) |
| **Chained models** | Multi-pass: draft → refine → validate | [Tutorial](/docs/tutorials/chained-models) |
| **Rule-based hybrid** | Pagsamahin ang deterministic rules sa flexibility ng LLM | [Tutorial](/docs/tutorials/rule-based-hybrid) |

---

## Pag-unawa sa Inyong mga Score

Pagkatapos ng benchmark run, makakakita po kayo ng output na gaya nito:

```
══════════════════════════════════════════════════
  Composite Score: 0.67 (Functional)
──────────────────────────────────────────────────
  chrF++:              0.72
  FST acceptance:      0.82
  Exact match:         0.31
  Morphological acc.:  0.88
  Semantic score:      0.64
══════════════════════════════════════════════════
```

**Mahahalagang metric:**

| Metric | Sinusukat nito | Timbang |
|--------|-----------------|--------|
| **chrF++** | Katumpakan ng pagsasalin sa antas ng character | 30% |
| **FST acceptance** | Morphological validity (para sa mga wikang may FSTs) | 25% |
| **Exact match** | Perpektong string matches laban sa reference | 15% |
| **Morphological accuracy** | Katumpakan ng lemma + feature | 15% |
| **Semantic score** | Pagpapanatili ng kahulugan anuman ang surface form | 15% |

**Mga antas ng kalidad:**

| Antas | Saklaw ng composite score | Kahulugan nito |
|------|----------------|---------------|
| Baseline | 0.00–0.30 | Mas mababa sa random chance para sa wika |
| Emerging | 0.30–0.50 | Nagpapakita ng potensyal ngunit hindi pa magagamit |
| Functional | 0.50–0.70 | Magagamit nang may post-editing |
| **Deployable** | **0.70–0.85** | **Handa para sa production na may pagsusuri ng speaker** |
| Fluent | 0.85–1.00 | Malapit sa native na kalidad |

Buong detalye: [Scoring Specification](/docs/specifications/scoring)

---

## Magsumite sa Leaderboard

Kapag kuntento na po kayo sa inyong score:

1. **I-score ang inyong run** — gumagawa ang `mt-eval test eval/logs/your_run.json` ng scored TestReport
2. **Suriin ang inyong mga score** — bumubuo ang `mt-eval dashboard eval/logs/your_run.json` ng visual dashboard
3. **Magsumite** — sundin ang gabay na [Magsumite ng Pamamaraan](/docs/getting-started/submit-a-method)

Bawat submission ay may fingerprint na tumutukoy sa isang partikular na configuration at bersyon ng dataset. Walang kalabuan tungkol sa kung ano ang sinubok.

---

## I-deploy sa Production

Maaaring i-deploy ang mga napatunayang pamamaraan sa pamamagitan ng [champollion](https://champollion.dev), ang production translation CLI. Ang parehong interface na ine-evaluate ng harness ay nagiging plugin na nagsasalin ng tunay na content.

```bash
# Export your benchmark as a champollion plugin
mt-eval export --report eval/logs/report.json --name crk-v1 --type llm-coached --locales crk
```

**[→ I-deploy sa Production](/docs/getting-started/deploy-to-production)** — dalhin ang inyong pamamaraan mula sa Arena patungo sa production.

---

## Troubleshooting

| Problema | Pag-aayos |
|---------|-----|
| `OPENROUTER_API_KEY not set` | I-export ang key o idagdag ito sa `.env` (tingnan ang setup sa itaas) |
| `Model not found` | Patakbuhin ang `mt-eval list models --live` upang mag-browse ng mga available na model |
| Walang laman ang lahat ng salin | Tingnan kung may credits ang inyong API key. Subukan muna ang `--dry-run` |
| `ModuleNotFoundError` | Tiyaking na-activate ninyo ang venv at pinatakbo ang `pip install -e .` |
| Hindi na-save ang run log | Tingnan ang `eval/logs/` — pinapangalanan ang mga log ayon sa timestamp |

---

## Tingnan Din

- [Magsumite ng Pamamaraan](/docs/getting-started/submit-a-method) — sunod-sunod na gabay sa submission
- [Scoring Specification](/docs/specifications/scoring) — kumpletong kahulugan at timbang ng mga metric
- [Harness Specification](/docs/specifications/harness) — sanggunian sa arkitektura at configuration
- [Leaderboard Rules](/docs/leaderboard/rules) — mga kinakailangan sa submission
- [Data Sovereignty](/docs/sovereignty/data-sovereignty) — OCAP, CARE, at pamamahalang pangkomunidad
- **Nais po bang gumamit ng umiiral na pamamaraan?** Tingnan ang [champollion Agent Guide](https://champollion.dev/docs/guides/agent-guide) — mag-install at magsalin gamit ang isang command.