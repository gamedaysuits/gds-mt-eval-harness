---
sidebar_position: 7
title: "Statistische Signifikanzprüfung"
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
# Test der statistischen Signifikanz — Implementierungsspezifikation

> **Ziel-Codebasis**: `arena` (insbesondere `tester.py` und `compare.py`)
> **Zweck**: Forschenden ermöglichen, festzustellen, ob der Unterschied zwischen zwei Evaluierungsläufen statistisch signifikant ist oder lediglich Rauschen darstellt.
> **Priorität**: Hoch — dies ist die mit Abstand wichtigste fehlende Funktion für veröffentlichungsfähige Ergebnisse.

---

## Warum dies wichtig ist

Beim Vergleich zweier Läufe (z. B. Gemini 3.1 Pro chrF++ 42.96 vs. Claude Sonnet chrF++ 41.80 bei 92 Einträgen) können wir derzeit nicht beurteilen, ob der Unterschied real oder Rauschen ist. Bei lediglich ~92 Testeinträgen können zufällige Schwankungen leicht Abweichungen von 1–2 Punkten hervorrufen. Fachleute werden nach Signifikanztests fragen. Wir müssen darauf antworten können.

---

## Algorithmus: Paired Bootstrap Resampling

Dies ist die Standardmethode, die von SacreBLEU, MT-Lens und den WMT Shared Tasks verwendet wird. Sie ist unter MT-Forschenden gut verstanden und liefert Ergebnisse, denen sie vertrauen.

### Funktionsweise

Gegeben zwei Systeme A und B, die anhand derselben N Testeinträge evaluiert werden:

1. Berechnen Sie die tatsächliche Metrikdifferenz: `Δ = metric(A) - metric(B)`
2. Wiederholen Sie `n_bootstrap` Mal (Standardwert 1000):
   a. Ziehen Sie N Einträge **mit Zurücklegen** aus dem gemeinsamen Testset
   b. Berechnen Sie die Metrik für A und B anhand dieser Bootstrap-Stichprobe
   c. Berechnen Sie die Bootstrap-Differenz: `Δ_boot = metric(A_boot) - metric(B_boot)`
3. Der p-Wert = Anteil der Bootstrap-Stichproben, bei denen `Δ_boot` das entgegengesetzte Vorzeichen zu `Δ` aufweist
4. Wenn p-Wert < α (Standardwert 0.05), ist der Unterschied statistisch signifikant

### Wesentliche Eigenschaften

- **Gepaart**: Beide Systeme werden anhand derselben Bootstrap-Stichprobe evaluiert, wodurch die Korrelation auf Eintragsebene erhalten bleibt
- **Nichtparametrisch**: Keine Annahme über die Verteilung der Bewertungen
- **Standard**: Genau dies macht `sacrebleu --paired-bs` intern

---

## Wichtig: sacrebleu ist eine harte Abhängigkeit

sacrebleu ist derzeit unter `[project.optional-dependencies]` aufgeführt und durch `try/except` in `tester.py` abgesichert. **Dies sollte geändert werden.** Ein MT-Evaluierungsframework, das chrF++ oder BLEU nicht berechnen kann, ist kein MT-Evaluierungsframework. sacrebleu sollte:

1. nach `[project.dependencies]` in `pyproject.toml` verschoben werden
2. direkt in `tester.py` importiert werden (Entfernen der `try/except HAS_SACREBLEU`-Absicherung)
3. direkt im neuen `significance.py`-Modul importiert werden

Die bedingten `HAS_SACREBLEU`-Pfade in `tester.py` sollten entfernt werden — sie erhöhen die Komplexität des Codes für ein Szenario (Ausführung ohne sacrebleu), das nicht unterstützt werden sollte.

---

## Implementierungsplan

### 1. sacrebleu zur harten Abhängigkeit erheben

**`pyproject.toml`**: Verschieben Sie `sacrebleu>=2.3` von `[project.optional-dependencies].metrics` nach `[project.dependencies]`.

**`tester.py`**: Ersetzen Sie:
```python
# Optional: sacrebleu for chrF++ and BLEU
try:
    from sacrebleu.metrics import CHRF, BLEU
    HAS_SACREBLEU = True
except ImportError:
    HAS_SACREBLEU = False
```
durch:
```python
from sacrebleu.metrics import CHRF, BLEU
```

Entfernen Sie alle `if HAS_SACREBLEU:`-Absicherungen in `tester.py`.

---

### 2. Neues Modul: `mt_eval_harness/significance.py`

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

### 3. Integrierte Metrikfunktionen

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

### 4. Integration in `compare.py`

Das bestehende `compare.py` führt bereits einen direkten Vergleich mehrerer TestReports durch. Fügen Sie den Signifikanztest hinzu:

```python
# In compare_reports(), after computing deltas:
if len(reports) == 2:
    sig_results = run_significance_tests(reports[0], reports[1])
    comparison["significance"] = [asdict(r) for r in sig_results]
```

Wenn mehr als 2 Berichte verglichen werden, führen Sie paarweise Signifikanztests für alle Paare durch. Speichern Sie die Ergebnisse mit dem Schlüssel `"(run_a_id, run_b_id)"`.

### 5. CLI-Integration

Fügen Sie `mt-eval compare` ein `--significance`-Flag hinzu:

```bash
# Compare two runs with significance testing
mt-eval compare report_a.json report_b.json --significance

# Custom bootstrap count
mt-eval compare report_a.json report_b.json --significance --n-bootstrap 5000
```

Erwägen Sie außerdem einen eigenständigen Befehl:

```bash
# Quick significance check between two reports
mt-eval significance report_a.json report_b.json
```

### 6. Ausgabeformat

**Konsolenausgabe:**
```
  Significance Tests (paired bootstrap, n=1000, α=0.05):

  Metric              A         B       Δ      p-value  Sig?
  ─────────────────── ──────── ──────── ─────── ──────── ────
  corpus_chrf         42.96    41.80    +1.16   0.142    No
  exact_match_rate     0.198    0.185   +0.013  0.381    No
  corpus_bleu          6.80     3.81    +2.99   0.018    Yes *
```

**JSON-Ausgabe** (zum Vergleichsbericht hinzugefügt):
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

### 7. Dashboard-Integration

Wenn Signifikanzdaten im Vergleichs-JSON vorhanden sind, sollte das Dashboard diese anzeigen. Zeigen Sie in der Vergleichstabelle eine Zeile mit Signifikanzindikatoren an (z. B. `*` für p < 0.05, `**` für p < 0.01). Dies ist wünschenswert, aber nicht zwingend erforderlich.

---

## Sonderfälle und Validierung

1. **Nicht übereinstimmende Einträge**: Die beiden TestReports müssen dieselben Eintrags-IDs aufweisen. Ist dies nicht der Fall (z. B. wenn einer auf einer Teilmenge ausgeführt wurde), testen Sie die Signifikanz nur auf der Schnittmenge. Warnen Sie vor ausgeschlossenen Einträgen.

2. **Zu wenige Einträge**: Wenn N < 10, warnen Sie, dass Signifikanztests bei so wenigen Einträgen unzuverlässig sind. Führen Sie sie dennoch aus, geben Sie jedoch die Warnung aus.

3. **Identische Bewertungen**: Wenn beide Systeme identische Ergebnisse pro Eintrag liefern, sollte p_value 1.0 betragen (kein Unterschied).

4. **Plugin-Metriken**: Das Signifikanzmodul sollte auch alle Plugin-Metriken testen, die in BEIDEN Berichten vorkommen. Verwenden Sie einen generischen Ansatz: Wenn beide Berichte `plugin_metrics.crk_fst_validity.avg_fst_validity` enthalten, testen Sie es.

5. **Reproduzierbarkeit**: Der RNG-Seed muss in der Ausgabe protokolliert werden, damit die Ergebnisse exakt reproduzierbar sind. Standardwert ist 12345 (entsprechend der SacreBLEU-Konvention).

---

## Was NICHT zu implementieren ist

- **Keine separate COMET-Signifikanz**: COMET ist nun als Korpusmetrik über `metrics_comet.py` integriert. Bootstrap-Konfidenzintervalle werden über COMET-Bewertungen genauso wie über chrF++/BLEU berechnet. Für die paarweise COMET-Signifikanz zwischen zwei Systemen verwenden Sie `comet-compare` von Unbabel.
- **Keine Bayessche Analyse**: Bleiben Sie beim frequentistischen Bootstrap. Dies erwartet und versteht die MT-Community.
- **Keine Korrektur für multiples Testen**: Wenn Sie mehrere Metriken testen, wenden Sie keine Bonferroni- oder ähnlichen Korrekturen an. Die Konvention in der MT-Evaluierung ist, rohe p-Werte pro Metrik zu berichten und deren Interpretation der Leserschaft zu überlassen.

---

## Zu ändernde Dateien

| Datei | Änderung |
|---|---|
| `pyproject.toml` | sacrebleu von optionaler zu harter Abhängigkeit verschieben |
| `mt_eval_harness/tester.py` | `HAS_SACREBLEU`-Absicherungen entfernen, direkter Import |
| `mt_eval_harness/significance.py` | **[NEU]** Kernimplementierung |
| `mt_eval_harness/__init__.py` | `SignificanceResult`, `paired_bootstrap` exportieren |
| `mt_eval_harness/compare.py` | Signifikanztests in den Berichtsvergleich einbinden |
| `mt_eval_harness/cli.py` | `--significance`- und `--n-bootstrap`-Flags hinzufügen |
| `mt_eval_harness/dashboard.py` | Signifikanz in der Vergleichstabelle anzeigen (wünschenswert) |
| `tests/test_significance.py` | **[NEU]** Unit-Tests |

---

## Testanforderungen

1. **Deterministisch mit Seed**: Gleiche Eingaben + gleicher Seed = gleicher p-Wert, jedes Mal
2. **Test mit bekanntem Ergebnis**: Zwei identische Ergebnismengen → p_value = 1.0
3. **Test mit bekannter Signifikanz**: Konstruieren Sie zwei Ergebnismengen, bei denen eine eindeutig besser ist (z. B. alle exakten Treffer vs. alle Fehlschläge) → p_value ≈ 0.0
4. **Nicht übereinstimmende IDs**: Sollte einen ValueError auslösen oder warnen und auf der Schnittmenge berechnen
5. **Leere Eingaben**: Sollte sauber behandelt werden (Rückgabe von p_value = 1.0 oder Auslösen einer Ausnahme)

---

## Konfidenzintervalle (Begleitfunktion)

> **Status**: ✅ IMPLEMENTIERT in `confidence.py`

Konfidenzintervalle (KIs) beantworten eine andere Frage als der Signifikanztest:

- **Signifikanztest** (`significance.py`): „Ist der Unterschied zwischen System A und System B real?“
- **Konfidenzintervalle** (`confidence.py`): „Wie unsicher ist die Bewertung dieses Systems für sich genommen?“

### Implementierung: `confidence.py`

Verwendet dieselbe Methode des Perzentil-Bootstrap-Resamplings wie der Signifikanztest:

| Parameter | Wert | Begründung |
|---|---|---|
| `n_bootstrap` | 1000 | SacreBLEU-Standardwert, WMT-2024-Konvention |
| `seed` | 12345 | SacreBLEU-Standard-Seed für Reproduzierbarkeit |
| `alpha` | 0.05 | Standard-Konfidenzniveau von 95 % |
| Methode | Perzentil-Bootstrap | Koehn (2004), Efron (1979) |

### Was KIs erhält

Alle vom Framework berechneten Metriken auf Korpusebene:
- `corpus_chrf` (chrF++-Bewertung)
- `corpus_bleu` (BLEU-Bewertung)
- `exact_match_rate` (0.0–1.0)

### CLI-Flags

```bash
# Default: CIs are computed automatically
mt-eval test run_log.json

# Skip CI computation (faster, for quick iteration)
mt-eval test run_log.json --no-ci

# More bootstrap iterations (more precise, slower)
mt-eval test run_log.json --n-bootstrap-ci 2000
```

### Warnung bei kleiner Stichprobe

Wenn N < 30 Einträge, gibt das Modul eine Warnung aus, dass die KIs eine schlechte Abdeckung aufweisen können. Der Bootstrap kann keine Information erzeugen, die in der Stichprobe nicht vorhanden ist — bei sehr wenigen Einträgen werden die Intervalle breit sein und damit die hohe Unsicherheit korrekt widerspiegeln.

### COMET-Integration

COMET (`metrics_comet.py`) ist nun als erstklassige Metrik integriert:
- Modell: `Unbabel/wmt22-comet-da` (referenzbasiertes Siegermodell der WMT 2022)
- Wird automatisch berechnet, wenn `unbabel-comet` installiert ist
- Bewertungen pro Eintrag werden in den TestReport-Einträgen gespeichert
- Erkennung ressourcenarmer Sprachen über die XLM-R-Abdeckungstabelle
- Optionale Abhängigkeit: `pip install mt-eval-harness[comet]`

### Supabase-Migration

Neue Spalten, die der Tabelle `run_cards` hinzugefügt wurden:
- `comet_score` (FLOAT8, nullable)
- `corpus_bleu` (FLOAT8, nullable)
- `chrf_ci_lower` / `chrf_ci_upper` (FLOAT8, nullable)
- `exact_match_ci_lower` / `exact_match_ci_upper` (FLOAT8, nullable)

Siehe `migrations/001_add_comet_and_ci_columns.sql` für das Migrationsskript.