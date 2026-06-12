---
sidebar_position: 7
title: "Pagsusuri ng Estadistikal na Kahalagahan"
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
# Pagsusuri ng Estadistikal na Kahalagahan — Spec ng Implementasyon

> **Target na codebase**: `arena` (partikular ang `tester.py` at `compare.py`)
> **Layunin**: Bigyang-daan ang mga mananaliksik na matukoy kung ang pagkakaiba sa pagitan ng dalawang evaluation run ay estadistikal na makabuluhan o ingay lamang.
> **Prayoridad**: Mataas — ito ang nag-iisang pinakamahalagang nawawalang feature para sa mga resultang maaaring mailathala.

---

## Bakit Ito Mahalaga

Kapag naghahambing ng dalawang run (hal., Gemini 3.1 Pro chrF++ 42.96 vs Claude Sonnet chrF++ 41.80 sa 92 entry), sa kasalukuyan ay hindi natin masasabi kung tunay ang pagkakaiba o ingay lamang. Sa ~92 test entries lamang, madaling makalikha ang random na baryasyon ng 1-2 puntos na pag-ugoy. Hihingi ang mga eksperto ng mga significance test. Kailangan nating makasagot.

---

## Algorithm: Paired Bootstrap Resampling

Ito ang karaniwang pamamaraang ginagamit ng SacreBLEU, MT-Lens, at WMT shared tasks. Mahusay itong nauunawaan ng mga mananaliksik sa MT at lumilikha ng mga resultang pinagkakatiwalaan nila.

### Paano Ito Gumagana

Ibinigay ang dalawang system A at B na sinusuri sa parehong N test entries:

1. Kuwentahin ang aktuwal na pagkakaiba ng metric: `Δ = metric(A) - metric(B)`
2. Ulitin nang `n_bootstrap` beses (default 1000):
   a. Magsampol ng N entries **na may kapalit** mula sa pinagsasaluhang test set
   b. Kuwentahin ang metric para sa parehong A at B sa bootstrap sample na ito
   c. Kuwentahin ang bootstrap difference: `Δ_boot = metric(A_boot) - metric(B_boot)`
3. Ang p-value = bahagi ng bootstrap samples kung saan ang `Δ_boot` ay may kabaligtarang sign mula sa `Δ`
4. Kung p-value < α (default 0.05), ang pagkakaiba ay estadistikal na makabuluhan

### Mahahalagang Katangian

- **Paired**: Sinusuri ang parehong system sa parehong bootstrap sample, na nagpapanatili ng entry-level correlation
- **Non-parametric**: Walang pagpapalagay tungkol sa distribusyon ng mga score
- **Standard**: Ito mismo ang ginagawa ng `sacrebleu --paired-bs` sa ilalim ng hood

---

## Mahalaga: Ang sacrebleu ay Hard Dependency

Kasalukuyang nakalista ang sacrebleu sa ilalim ng `[project.optional-dependencies]` at binabantayan ng `try/except` sa `tester.py`. **Dapat itong baguhin.** Ang isang MT eval harness na hindi makakuwenta ng chrF++ o BLEU ay hindi isang MT eval harness. Dapat ang sacrebleu ay:

1. Ilipat sa `[project.dependencies]` sa `pyproject.toml`
2. Direktang i-import sa `tester.py` (alisin ang `try/except HAS_SACREBLEU` guard)
3. Direktang i-import sa bagong `significance.py` module

Dapat alisin ang mga `HAS_SACREBLEU` conditional path sa `tester.py` — ginagawa nitong mas kumplikado ang code para sa isang senaryo (pagpapatakbo nang walang sacrebleu) na hindi dapat suportahan.

---

## Plano ng Implementasyon

### 1. I-promote ang sacrebleu bilang hard dependency

**`pyproject.toml`**: Ilipat ang `sacrebleu>=2.3` mula sa `[project.optional-dependencies].metrics` patungo sa `[project.dependencies]`.

**`tester.py`**: Palitan ang:
```python
# Optional: sacrebleu for chrF++ and BLEU
try:
    from sacrebleu.metrics import CHRF, BLEU
    HAS_SACREBLEU = True
except ImportError:
    HAS_SACREBLEU = False
```
Ng:
```python
from sacrebleu.metrics import CHRF, BLEU
```

Alisin ang lahat ng `if HAS_SACREBLEU:` guard sa buong `tester.py`.

---

### 2. Bagong module: `mt_eval_harness/significance.py`

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

### 3. Mga built-in na metric function

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

### 4. Integrasyon sa `compare.py`

Ang umiiral na `compare.py` ay gumagawa na ng side-by-side comparison ng maraming TestReports. Magdagdag ng significance testing:

```python
# In compare_reports(), after computing deltas:
if len(reports) == 2:
    sig_results = run_significance_tests(reports[0], reports[1])
    comparison["significance"] = [asdict(r) for r in sig_results]
```

Kapag higit sa 2 report ang inihahambing, magpatakbo ng pairwise significance tests para sa lahat ng pares. Itago ang mga resulta na naka-key ayon sa `"(run_a_id, run_b_id)"`.

### 5. Integrasyon sa CLI

Magdagdag ng `--significance` flag sa `mt-eval compare`:

```bash
# Compare two runs with significance testing
mt-eval compare report_a.json report_b.json --significance

# Custom bootstrap count
mt-eval compare report_a.json report_b.json --significance --n-bootstrap 5000
```

Isaalang-alang din ang standalone na command:

```bash
# Quick significance check between two reports
mt-eval significance report_a.json report_b.json
```

### 6. Format ng output

**Console output:**
```
  Significance Tests (paired bootstrap, n=1000, α=0.05):

  Metric              A         B       Δ      p-value  Sig?
  ─────────────────── ──────── ──────── ─────── ──────── ────
  corpus_chrf         42.96    41.80    +1.16   0.142    No
  exact_match_rate     0.198    0.185   +0.013  0.381    No
  corpus_bleu          6.80     3.81    +2.99   0.018    Yes *
```

**JSON output** (idinagdag sa comparison report):
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

### 7. Integrasyon sa dashboard

Kung may significance data sa comparison JSON, dapat itong ipakita ng dashboard. Magpakita ng row sa comparison table na may mga significance indicator (hal., `*` para sa p < 0.05, `**` para sa p < 0.01). Ito ay nice-to-have, hindi blocking.

---

## Mga Edge Case at Validation

1. **Hindi nagtutugmang entries**: Dapat may parehong entry IDs ang dalawang TestReports. Kung wala (hal., ang isa ay tumakbo sa isang subset), subukan lamang ang significance sa intersection. Magbigay ng babala tungkol sa mga inalis na entry.

2. **Napakakaunting entries**: Kung N < 10, magbabala na hindi maaasahan ang significance tests kapag napakakaunti ng entries. Patakbuhin pa rin ang mga ito, ngunit i-print ang babala.

3. **Magkaparehong scores**: Kung parehong gumagawa ang dalawang system ng magkaparehong per-entry results, dapat ang p_value ay 1.0 (walang pagkakaiba sa anumang paraan).

4. **Plugin metrics**: Dapat subukan din ng significance module ang anumang plugin metrics na lumalabas sa PAREHONG report. Gumamit ng generic na approach: kung parehong may `plugin_metrics.crk_fst_validity.avg_fst_validity` ang mga report, subukan ito.

5. **Reproducibility**: Dapat i-log ang RNG seed sa output upang eksaktong mareproduce ang mga resulta. Gamitin ang default na 12345 (tumutugma sa SacreBLEU convention).

---

## Ano ang HINDI Dapat Buuin

- **Walang hiwalay na COMET significance**: Ang COMET ay naka-integrate na ngayon bilang corpus metric sa pamamagitan ng `metrics_comet.py`. Kinukuwenta ang mga bootstrap CI sa ibabaw ng COMET scores tulad ng chrF++/BLEU. Para sa pairwise COMET significance sa pagitan ng dalawang system, gamitin ang `comet-compare` mula sa Unbabel.
- **Walang Bayesian analysis**: Manatili sa frequentist bootstrap. Ito ang inaasahan at nauunawaan ng komunidad ng MT.
- **Walang multi-test correction**: Kapag sumusubok ng maraming metric, huwag mag-apply ng Bonferroni o katulad na corrections. Ang convention sa MT evaluation ay iulat ang raw p-values bawat metric at hayaang mag-interpret ang mambabasa.

---

## Mga File na Babaguhin

| File | Pagbabago |
|---|---|
| `pyproject.toml` | Ilipat ang sacrebleu mula optional patungo sa hard dependency |
| `mt_eval_harness/tester.py` | Alisin ang `HAS_SACREBLEU` guards, direktang import |
| `mt_eval_harness/significance.py` | **[BAGO]** Core implementation |
| `mt_eval_harness/__init__.py` | I-export ang `SignificanceResult`, `paired_bootstrap` |
| `mt_eval_harness/compare.py` | I-wire ang significance tests sa report comparison |
| `mt_eval_harness/cli.py` | Idagdag ang `--significance` at `--n-bootstrap` flags |
| `mt_eval_harness/dashboard.py` | Ipakita ang significance sa comparison table (nice-to-have) |
| `tests/test_significance.py` | **[BAGO]** Unit tests |

---

## Mga Kinakailangan sa Testing

1. **Deterministic gamit ang seed**: Parehong inputs + parehong seed = parehong p-value, sa bawat pagkakataon
2. **Known-answer test**: Dalawang magkaparehong result set → p_value = 1.0
3. **Known-significant test**: Bumuo ng dalawang result set kung saan malinaw na mas mahusay ang isa (hal., lahat exact matches vs lahat misses) → p_value ≈ 0.0
4. **Hindi nagtutugmang IDs**: Dapat mag-raise ng ValueError o magbabala at magkuwenta sa intersection
5. **Empty inputs**: Dapat pangasiwaan nang maayos (magbalik ng p_value = 1.0 o mag-raise)

---

## Mga Agwat ng Kompiyansa (Kasamang Feature)

> **Status**: ✅ IMPLEMENTED sa `confidence.py`

Sumasagot ang confidence intervals (CIs) sa ibang tanong kaysa significance testing:

- **Significance testing** (`significance.py`): "Totoo ba ang pagkakaiba sa pagitan ng system A at system B?"
- **Confidence intervals** (`confidence.py`): "Gaano kalaki ang kawalan ng katiyakan sa score ng system na ito sa sarili nito?"

### Implementasyon: `confidence.py`

Gumagamit ng parehong percentile bootstrap resampling method gaya ng significance testing:

| Parameter | Value | Katwiran |
|---|---|---|
| `n_bootstrap` | 1000 | SacreBLEU default, WMT 2024 convention |
| `seed` | 12345 | SacreBLEU default seed para sa reproducibility |
| `alpha` | 0.05 | Standard na 95% confidence level |
| Method | Percentile bootstrap | Koehn (2004), Efron (1979) |

### Ano ang Nagkakaroon ng CIs

Lahat ng corpus-level metrics na kinukuwenta ng harness:
- `corpus_chrf` (chrF++ score)
- `corpus_bleu` (BLEU score)
- `exact_match_rate` (0.0–1.0)

### CLI Flags

```bash
# Default: CIs are computed automatically
mt-eval test run_log.json

# Skip CI computation (faster, for quick iteration)
mt-eval test run_log.json --no-ci

# More bootstrap iterations (more precise, slower)
mt-eval test run_log.json --n-bootstrap-ci 2000
```

### Babala para sa Maliit na Sample

Kapag N < 30 entries, naglalabas ang module ng babala na maaaring mahina ang coverage ng CIs. Hindi makalilikha ang bootstrap ng impormasyong wala sa sample — kapag napakakaunti ng entries, magiging malalapad ang mga interval, na wastong sumasalamin sa mataas na kawalan ng katiyakan.

### Integrasyon ng COMET

Ang COMET (`metrics_comet.py`) ay naka-integrate na ngayon bilang first-class metric:
- Model: `Unbabel/wmt22-comet-da` (WMT 2022 winning reference-based model)
- Awtomatikong kinukuwenta kapag naka-install ang `unbabel-comet`
- Per-entry scores na nakaimbak sa TestReport entries
- Low-resource language detection sa pamamagitan ng XLM-R coverage table
- Optional dependency: `pip install mt-eval-harness[comet]`

### Supabase Migration

Mga bagong column na idinagdag sa `run_cards` table:
- `comet_score` (FLOAT8, nullable)
- `corpus_bleu` (FLOAT8, nullable)
- `chrf_ci_lower` / `chrf_ci_upper` (FLOAT8, nullable)
- `exact_match_ci_lower` / `exact_match_ci_upper` (FLOAT8, nullable)

Tingnan ang `migrations/001_add_comet_and_ci_columns.sql` para sa migration script.