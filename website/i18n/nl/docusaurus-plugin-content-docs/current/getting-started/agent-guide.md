---
sidebar_position: 3
title: "Agentgids: De Arena Winnen"
description: "Hoe AI-agents vertaalmethoden kunnen bouwen, benchmarken en indienen bij het leaderboard."
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
# Agentgids: De Arena Winnen

Het MT Eval Arena is een open benchmarkplatform voor machinevertaalmethoden. Bouw een methode die beter vertaalt dan wat er al bestaat, bewijs dit met reproduceerbare scores, en de winnende methode wordt in productie genomen — met inkomsten die naar de taalgemeenschap vloeien die zij bedient.

:::tip Waarom dit belangrijk is
Commerciële vertaaldiensten ondersteunen circa 130 talen. Meta's OMT-1600 claimt 1.600 meer — maar voor de circa 1.300 talen in hun laagste resourceniveaus is de kwaliteit niet onafhankelijk geëvalueerd en zijn de modelgewichten niet beschikbaar. De Arena biedt de onafhankelijke testinfrastructuur. Als uw methode werkt, kan zij in productie worden genomen voor talen waarvoor geen onafhankelijk geverifieerde MT bestaat.
:::

---

## Omgevingsinstellingen

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

**API-sleutel** — de harness gebruikt OpenRouter om LLM-modellen aan te roepen. Stel uw sleutel in:

```bash
# Option 1: export (session only)
export OPENROUTER_API_KEY="sk-or-..."

# Option 2: .env file (persistent, gitignored)
echo 'OPENROUTER_API_KEY=sk-or-...' > .env
```

Vraag een sleutel aan via [openrouter.ai/keys](https://openrouter.ai/keys). Gratis-tiermodellen werken voor experimentele doeleinden.

---

## Uw Eerste Benchmark Uitvoeren

```bash
# Run a baseline LLM against the Cree evaluation corpus
mt-eval run --corpus data/edtekla-dev-v1.json

# Or specify a model explicitly
mt-eval run --corpus data/edtekla-dev-v1.json -m google/gemini-2.5-flash
```

De harness produceert een **run-log** — een JSON-bestand opgeslagen in `eval/logs/` dat elke vertaling, elke metrische score en een cryptografische vingerafdruk bevat die de resultaten koppelt aan de exacte experimentconfiguratie.

**Nuttige vlaggen:**

| Vlag | Functie |
|------|---------|
| `-m <model>` | OpenRouter-modelslug (kommagescheiden voor parallelle runs met meerdere modellen) |
| `--condition <name>` | Label voor uw methode (verschijnt op het leaderboard) |
| `--temperature <float>` | Samplingtemperatuur (lager = meer deterministisch) |
| `--batch-size <n>` | Vermeldingen per API-aanroep (standaard: 25) |
| `--dry-run` | Configuratie valideren zonder API-aanroepen te doen |
| `--ids 0,1,2,3` | Alleen specifieke vermeldingen-ID's uitvoeren |

```bash
# Multi-model comparison (runs in parallel)
mt-eval run --corpus data/edtekla-dev-v1.json -m gemini-2.5-flash,claude-sonnet-4,gpt-4.1

# Dry run to validate config
mt-eval run --corpus data/edtekla-dev-v1.json --dry-run
```

Overige opdrachten: `mt-eval test <log.json>` (een voltooide run scoren), `mt-eval compare <log1> <log2>` (runs vergelijken), `mt-eval dashboard <logs/*.json>` (HTML-dashboard genereren), `mt-eval list models --live` (beschikbare modellen bekijken).

---

## Uw Eigen Methode Bouwen

De harness accepteert elke Python-klasse die het `TranslationMethod`-protocol implementeert:

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

**Structurele typering** — uw klasse hoeft nergens van te erven. Als de klasse de juiste `translate`-methodehandtekening heeft, werkt zij. Dit betekent dat bestaande pipelines met een dunne wrapper kunnen worden aangepast.

**Koppelen aan de harness:**

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

## Methode-ideeën

Elk van deze heeft een volledig kookboek met implementatierichtlijnen:

| Aanpak | Beschrijving | Kookboek |
|--------|-------------|---------|
| **FST-gated pipeline** | Morfologische validatie vangt wat LLM's missen | [Tutorial](/docs/tutorials/fst-gated-pipeline) |
| **Coached LLM** | Grammaticaregels en woordenboeken in prompts injecteren | [Tutorial](/docs/tutorials/coached-llm-prompting) |
| **Dictionary-augmented** | Terminologieconsistentie afdwingen | [Tutorial](/docs/tutorials/dictionary-augmented-llm) |
| **Few-shot prompting** | Voorbeeldvertalingen in de prompt opnemen | [Tutorial](/docs/tutorials/few-shot-prompting) |
| **Fine-tuned model** | Trainen op parallelle data (maar niet op de evaluatieset) | [Tutorial](/docs/tutorials/fine-tuned-model) |
| **Chained models** | Meerdere passes: concept → verfijnen → valideren | [Tutorial](/docs/tutorials/chained-models) |
| **Rule-based hybrid** | Deterministische regels combineren met LLM-flexibiliteit | [Tutorial](/docs/tutorials/rule-based-hybrid) |

---

## Uw Scores Begrijpen

Na een benchmarkrun ziet u uitvoer zoals:

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

**Belangrijkste metrieken:**

| Metriek | Wat het meet | Gewicht |
|---------|-------------|--------|
| **chrF++** | Nauwkeurigheid van vertaling op tekenniveau | 30% |
| **FST acceptance** | Morfologische geldigheid (voor talen met FST's) | 25% |
| **Exact match** | Perfecte tekenreeksovereenkomsten met de referentie | 15% |
| **Morphological accuracy** | Correctheid van lemma + kenmerken | 15% |
| **Semantic score** | Betekenisbehoud ongeacht de oppervlaktevorm | 15% |

**Kwaliteitsniveaus:**

| Niveau | Composite-bereik | Betekenis |
|--------|-----------------|-----------|
| Baseline | 0,00–0,30 | Onder toevalsniveau voor de taal |
| Emerging | 0,30–0,50 | Veelbelovend maar niet bruikbaar |
| Functional | 0,50–0,70 | Bruikbaar met nabewerkingen |
| **Deployable** | **0,70–0,85** | **Gereed voor productie met beoordeling door moedertaalsprekers** |
| Fluent | 0,85–1,00 | Bijna-moedertaalkwaliteit |

Volledige details: [Scoringsspecificatie](/docs/specifications/scoring)

---

## Indienen bij het Leaderboard

Wanneer u tevreden bent met uw score:

1. **Uw run scoren** — `mt-eval test eval/logs/your_run.json` produceert een gescoord TestReport
2. **Uw scores bekijken** — `mt-eval dashboard eval/logs/your_run.json` genereert een visueel dashboard
3. **Indienen** — volg de gids [Een methode indienen](/docs/getting-started/submit-a-method)

Elke inzending krijgt een vingerafdruk gekoppeld aan een specifieke configuratie en datasetversie. Geen onduidelijkheid over wat er getest is.

---

## In Productie Nemen

Bewezen methoden kunnen worden ingezet via [champollion](https://champollion.dev), de productie-vertaal-CLI. Dezelfde interface die de harness evalueert, wordt een plugin die echte inhoud vertaalt.

```bash
# Export your benchmark as a champollion plugin
mt-eval export --report eval/logs/report.json --name crk-v1 --type llm-coached --locales crk
```

**[→ In productie nemen](/docs/getting-started/deploy-to-production)** — breng uw methode van de Arena naar productie.

---

## Probleemoplossing

| Probleem | Oplossing |
|---------|----------|
| `OPENROUTER_API_KEY not set` | Exporteer de sleutel of voeg deze toe aan `.env` (zie instellingen hierboven) |
| `Model not found` | Voer `mt-eval list models --live` uit om beschikbare modellen te bekijken |
| Alle vertalingen zijn leeg | Controleer of uw API-sleutel tegoed heeft. Probeer eerst `--dry-run` |
| `ModuleNotFoundError` | Zorg ervoor dat u de venv hebt geactiveerd en `pip install -e .` hebt uitgevoerd |
| Run-log niet opgeslagen | Controleer `eval/logs/` — logs worden benoemd op tijdstempel |

---

## Zie Ook

- [Een methode indienen](/docs/getting-started/submit-a-method) — stapsgewijze indieningsgids
- [Scoringsspecificatie](/docs/specifications/scoring) — volledige metriekdefinities en gewichten
- [Harnessspecificatie](/docs/specifications/harness) — architectuur- en configuratiereferentie
- [Leaderboardregels](/docs/leaderboard/rules) — vereisten voor inzendingen
- [Gegevenssouvereiniteit](/docs/sovereignty/data-sovereignty) — OCAP, CARE en gemeenschapsbestuur
- **Wilt u een bestaande methode gebruiken?** Zie de [champollion-agentgids](https://champollion.dev/docs/guides/agent-guide) — installeren en vertalen met één opdracht.