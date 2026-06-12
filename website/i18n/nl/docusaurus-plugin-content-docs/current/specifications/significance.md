---
sidebar_position: 7
title: "Statistische Significantietoetsing"
slug: '/specifications/significance'
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The scores these tests protect"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "Where significance gates what ranks"
---
# Statistische Significantietoetsing — Implementatiespecificatie

> **Doelcodebase**: `arena` (specifiek `tester.py` en `compare.py`)
> **Doel**: Onderzoekers in staat stellen te bepalen of het verschil tussen twee evaluatieruns statistisch significant is of slechts ruis.
> **Prioriteit**: Hoog — dit is de belangrijkste ontbrekende functionaliteit voor publiceerbare resultaten.

---

## Waarom Dit Belangrijk Is

Wanneer twee runs worden vergeleken (bijv. Gemini 3.1 Pro chrF++ 42,96 vs. Claude Sonnet chrF++ 41,80 op 92 invoeren), kunnen we momenteel niet vaststellen of het verschil reëel is of ruis. Met slechts ~92 testinvoeren kan willekeurige variatie gemakkelijk schommelingen van 1 à 2 punten veroorzaken. Experts zullen om significantietoetsen vragen. We moeten hierop een antwoord kunnen geven.

---

## Algoritme: Paired Bootstrap Resampling

Dit is de standaardmethode die wordt gebruikt door SacreBLEU, MT-Lens en WMT shared tasks. De methode is goed bekend bij MT-onderzoekers en levert resultaten op die zij vertrouwen.

### Werking

Gegeven twee systemen A en B, geëvalueerd op dezelfde N testinvoeren:

1. Bereken het werkelijke metriekverschil: `Δ = metric(A) - metric(B)`
2. Herhaal `n_bootstrap` keer (standaard 1000):
   a. Sample N invoeren **met teruglegging** uit de gedeelde testset
   b. Bereken de metriek voor zowel A als B op dit bootstrapsample
   c. Bereken het bootstrapverschil: `Δ_boot = metric(A_boot) - metric(B_boot)`
3. De p-waarde = het aandeel bootstrapsamples waarbij `Δ_boot` het tegengestelde teken heeft van `Δ`
4. Als de p-waarde < α (standaard 0,05), is het verschil statistisch significant

### Belangrijkste Eigenschappen

- **Paired**: Beide systemen worden geëvalueerd op hetzelfde bootstrapsample, waardoor de correlatie op invoerniveau behouden blijft
- **Niet-parametrisch**: Geen aanname over de verdeling van scores
- **Standaard**: Dit is precies wat `sacrebleu --paired-bs` intern doet

---

## Belangrijk: sacrebleu Is een Harde Afhankelijkheid

sacrebleu staat momenteel vermeld onder `[project.optional-dependencies]` en wordt bewaakt door `try/except` in `tester.py`. **Dit dient te worden gewijzigd.** Een MT-evaluatieharnas dat geen chrF++ of BLEU kan berekenen, is geen MT-evaluatieharnas. sacrebleu dient:

1. Verplaatst te worden naar `[project.dependencies]` in `pyproject.toml`
2. Direct geïmporteerd te worden in `tester.py` (verwijder de `try/except HAS_SACREBLEU`-bewaker)
3. Direct geïmporteerd te worden in de nieuwe `significance.py`-module

De `HAS_SACREBLEU`-conditionele paden in `tester.py` dienen te worden verwijderd — zij maken de code complexer voor een scenario (uitvoeren zonder sacrebleu) dat niet ondersteund zou moeten worden.

---

## Implementatieplan

### 1. sacrebleu promoveren tot harde afhankelijkheid

**`pyproject.toml`**: Verplaats `sacrebleu>=2.3` van `[project.optional-dependencies].metrics` naar `[project.dependencies]`.

**`tester.py`**: Vervang:
```python
# Optional: sacrebleu for chrF++ and BLEU
try:
    from sacrebleu.metrics import CHRF, BLEU
    HAS_SACREBLEU = True
except ImportError:
    HAS_SACREBLEU = False
```
Door:
```python
from sacrebleu.metrics import CHRF, BLEU
```

Verwijder alle `if HAS_SACREBLEU:`-bewakers in `tester.py`.

---

### 2. Nieuwe module: `mt_eval_harness/significance.py`

```python
"""
Statistical significance testing via paired bootstrap resampling.

Standard method used by WMT shared tasks, SacreBLEU, and MT-Lens.
Compares two runs on the same corpus to determine if the performance
difference is statistically significant.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from sacrebleu.metrics import CHRF, BLEU


@dataclass
class SignificanceResult:
    """Result of a paired bootstrap significance test."""
    metric_name: str           # e.g., "corpus_chrf", "exact_match_rate"
    system_a_score: float      # Score for system A
    system_b_score: float      # Score for system B
    delta: float               # A - B
    p_value: float             # Two-sided p-value
    n_bootstrap: int           # Number of bootstrap iterations
    confidence_level: float    # 1 - alpha
    significant: bool          # p_value < alpha
    winner: str | None         # "A", "B", or None if not significant
    ci_lower: float            # Lower bound of 95% CI on the delta
    ci_upper: float            # Upper bound of 95% CI on the delta


def paired_bootstrap(
    entries_a: list[dict],
    entries_b: list[dict],
    metric_fn: callable,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 12345,
    metric_name: str = "metric",
) -> SignificanceResult:
    """Run paired bootstrap resampling significance test.

    Args:
        entries_a: Per-entry results from system A (from TestReport["entries"])
        entries_b: Per-entry results from system B (must be same length, same IDs)
        metric_fn: Function(list[dict]) -> float that computes the corpus-level
                   metric from a list of entry dicts. Must handle the entry format
                   from TestReport.
        n_bootstrap: Number of bootstrap iterations (1000 is standard)
        alpha: Significance level (0.05 = 95% confidence)
        seed: RNG seed for reproducibility (12345 matches SacreBLEU default)
        metric_name: Human-readable name for the metric being tested

    Returns:
        SignificanceResult with all fields populated.

    Raises:
        ValueError: If entries_a and entries_b have different lengths or IDs.
    """
    ...
```

### 3. Ingebouwde metriekfuncties

```python
def exact_match_rate(entries: list[dict]) -> float:
    """Compute exact match rate from a list of entry dicts."""
    non_error = [e for e in entries if not e.get("error")]
    if not non_error:
        return 0.0
    exact = sum(1 for e in non_error if e.get("exact_match"))
    return exact / len(non_error)


def corpus_chrf(entries: list[dict]) -> float:
    """Compute corpus-level chrF++ from a list of entry dicts."""
    chrf = CHRF(word_order=2)
    refs = [e["expected"] for e in entries if e.get("expected", "").strip()]
    hyps = [e["predicted"] if e.get("predicted", "").strip() else "EMPTY"
            for e in entries if e.get("expected", "").strip()]
    if not refs:
        return 0.0
    return chrf.corpus_score(hyps, [refs]).score


def corpus_bleu(entries: list[dict]) -> float:
    """Compute corpus-level BLEU from a list of entry dicts."""
    bleu = BLEU()
    refs = [e["expected"] for e in entries if e.get("expected", "").strip()]
    hyps = [e["predicted"] if e.get("predicted", "").strip() else "EMPTY"
            for e in entries if e.get("expected", "").strip()]
    if not refs:
        return 0.0
    return bleu.corpus_score(hyps, [refs]).score
```

### 4. Integratie in `compare.py`

De bestaande `compare.py` voert al een zij-aan-zij-vergelijking uit van meerdere TestReports. Voeg significantietoetsing toe:

```python
# In compare_reports(), after computing deltas:
if len(reports) == 2:
    sig_results = run_significance_tests(reports[0], reports[1])
    comparison["significance"] = [asdict(r) for r in sig_results]
```

Wanneer meer dan 2 rapporten worden vergeleken, voer paarsgewijze significantietoetsen uit voor alle paren. Sla resultaten op met `"(run_a_id, run_b_id)"` als sleutel.

### 5. CLI-integratie

Voeg een `--significance`-vlag toe aan `mt-eval compare`:

```bash
# Compare two runs with significance testing
mt-eval compare report_a.json report_b.json --significance

# Custom bootstrap count
mt-eval compare report_a.json report_b.json --significance --n-bootstrap 5000
```

Overweeg ook een zelfstandig commando:

```bash
# Quick significance check between two reports
mt-eval significance report_a.json report_b.json
```

### 6. Uitvoerformaat

**Console-uitvoer:**
```
  Significance Tests (paired bootstrap, n=1000, α=0.05):

  Metric              A         B       Δ      p-value  Sig?
  ─────────────────── ──────── ──────── ─────── ──────── ────
  corpus_chrf         42.96    41.80    +1.16   0.142    No
  exact_match_rate     0.198    0.185   +0.013  0.381    No
  corpus_bleu          6.80     3.81    +2.99   0.018    Yes *
```

**JSON-uitvoer** (toegevoegd aan vergelijkingsrapport):
```json
{
  "significance": [
    {
      "metric_name": "corpus_chrf",
      "system_a_score": 42.96,
      "system_b_score": 41.80,
      "delta": 1.16,
      "p_value": 0.142,
      "n_bootstrap": 1000,
      "confidence_level": 0.95,
      "significant": false,
      "winner": null,
      "ci_lower": -0.85,
      "ci_upper": 3.12
    }
  ]
}
```

### 7. Dashboard-integratie

Als significantiegegevens aanwezig zijn in de vergelijkings-JSON, dient het dashboard deze weer te geven. Toon een rij in de vergelijkingstabel met significantie-indicatoren (bijv. `*` voor p < 0,05, `**` voor p < 0,01). Dit is een nice-to-have, geen blokker.

---

## Randgevallen en Validatie

1. **Niet-overeenkomende invoeren**: De twee TestReports moeten dezelfde invoer-ID's hebben. Als dat niet het geval is (bijv. één rapport is uitgevoerd op een subset), voer de significantietoets alleen uit op de doorsnede. Waarschuw voor uitgesloten invoeren.

2. **Te weinig invoeren**: Als N < 10, waarschuw dan dat significantietoetsen onbetrouwbaar zijn bij zo weinig invoeren. Voer ze toch uit, maar druk de waarschuwing af.

3. **Identieke scores**: Als beide systemen identieke resultaten per invoer produceren, dient p_value gelijk te zijn aan 1,0 (geen enkel verschil).

4. **Plugin-metrieken**: De significantiemodule dient ook plugin-metrieken te toetsen die in BEIDE rapporten voorkomen. Gebruik een generieke aanpak: als beide rapporten `plugin_metrics.crk_fst_validity.avg_fst_validity` bevatten, toets deze dan.

5. **Reproduceerbaarheid**: De RNG-seed moet worden vastgelegd in de uitvoer zodat resultaten exact reproduceerbaar zijn. Standaard 12345 (conform de SacreBLEU-conventie).

---

## Wat NIET te Bouwen

- **Geen afzonderlijke COMET-significantie**: COMET is nu geïntegreerd als corpusmetriek via `metrics_comet.py`. Bootstrap-betrouwbaarheidsintervallen worden berekend over COMET-scores, net als bij chrF++/BLEU. Gebruik voor paarsgewijze COMET-significantie tussen twee systemen `comet-compare` van Unbabel.
- **Geen Bayesiaanse analyse**: Houd het bij frequentistische bootstrap. Dit is wat de MT-gemeenschap verwacht en begrijpt.
- **Geen correctie voor meervoudig toetsen**: Pas bij het toetsen van meerdere metrieken geen Bonferroni-correctie of vergelijkbare correcties toe. De conventie in MT-evaluatie is om ruwe p-waarden per metriek te rapporteren en de interpretatie aan de lezer over te laten.

---

## Te Wijzigen Bestanden

| Bestand | Wijziging |
|---|---|
| `pyproject.toml` | Verplaats sacrebleu van optionele naar harde afhankelijkheid |
| `mt_eval_harness/tester.py` | Verwijder `HAS_SACREBLEU`-bewakers, directe import |
| `mt_eval_harness/significance.py` | **[NIEUW]** Kernimplementatie |
| `mt_eval_harness/__init__.py` | Exporteer `SignificanceResult`, `paired_bootstrap` |
| `mt_eval_harness/compare.py` | Koppel significantietoetsen aan rapportvergelijking |
| `mt_eval_harness/cli.py` | Voeg `--significance`- en `--n-bootstrap`-vlaggen toe |
| `mt_eval_harness/dashboard.py` | Toon significantie in vergelijkingstabel (nice-to-have) |
| `tests/test_significance.py` | **[NIEUW]** Unittests |

---

## Testvereisten

1. **Deterministisch met seed**: Dezelfde invoer + dezelfde seed = dezelfde p-waarde, altijd
2. **Bekende-antwoordtest**: Twee identieke resultaatsets → p_value = 1,0
3. **Bekende-significantietest**: Construeer twee resultaatsets waarbij één duidelijk beter is (bijv. alle exacte overeenkomsten vs. alle missers) → p_value ≈ 0,0
4. **Niet-overeenkomende ID's**: Dient een ValueError te geven of te waarschuwen en te berekenen op de doorsnede
5. **Lege invoer**: Dient correct afgehandeld te worden (geef p_value = 1,0 terug of gooi een uitzondering)

---

## Betrouwbaarheidsintervallen (Aanvullende Functionaliteit)

> **Status**: ✅ GEÏMPLEMENTEERD in `confidence.py`

Betrouwbaarheidsintervallen (BI's) beantwoorden een andere vraag dan significantietoetsing:

- **Significantietoetsing** (`significance.py`): "Is het verschil tussen systeem A en systeem B reëel?"
- **Betrouwbaarheidsintervallen** (`confidence.py`): "Hoe onzeker is de score van dit systeem op zichzelf?"

### Implementatie: `confidence.py`

Maakt gebruik van dezelfde percentielboostrap-resamplingmethode als significantietoetsing:

| Parameter | Waarde | Motivering |
|---|---|---|
| `n_bootstrap` | 1000 | SacreBLEU-standaard, WMT 2024-conventie |
| `seed` | 12345 | SacreBLEU-standaardseed voor reproduceerbaarheid |
| `alpha` | 0,05 | Standaard 95%-betrouwbaarheidsniveau |
| Methode | Percentielbootstrap | Koehn (2004), Efron (1979) |

### Welke Metrieken BI's Krijgen

Alle corpusniveau-metrieken berekend door het harnas:
- `corpus_chrf` (chrF++-score)
- `corpus_bleu` (BLEU-score)
- `exact_match_rate` (0,0–1,0)

### CLI-vlaggen

```bash
# Default: CIs are computed automatically
mt-eval test run_log.json

# Skip CI computation (faster, for quick iteration)
mt-eval test run_log.json --no-ci

# More bootstrap iterations (more precise, slower)
mt-eval test run_log.json --n-bootstrap-ci 2000
```

### Waarschuwing bij Kleine Steekproeven

Wanneer N < 30 invoeren, geeft de module een waarschuwing dat BI's mogelijk een slechte dekking hebben. Bootstrap kan geen informatie creëren die afwezig is in de steekproef — bij zeer weinig invoeren zullen de intervallen breed zijn, wat de hoge onzekerheid correct weerspiegelt.

### COMET-integratie

COMET (`metrics_comet.py`) is nu geïntegreerd als eersteklas metriek:
- Model: `Unbabel/wmt22-comet-da` (WMT 2022-winnend referentiegebaseerd model)
- Automatisch berekend wanneer `unbabel-comet` is geïnstalleerd
- Scores per invoer opgeslagen in TestReport-invoeren
- Detectie van laagresourcentalen via XLM-R-dekkingstabel
- Optionele afhankelijkheid: `pip install mt-eval-harness[comet]`

### Supabase-migratie

Nieuwe kolommen toegevoegd aan de `run_cards`-tabel:
- `comet_score` (FLOAT8, nullable)
- `corpus_bleu` (FLOAT8, nullable)
- `chrf_ci_lower` / `chrf_ci_upper` (FLOAT8, nullable)
- `exact_match_ci_lower` / `exact_match_ci_upper` (FLOAT8, nullable)

Zie `migrations/001_add_comet_and_ci_columns.sql` voor het migratiescript.