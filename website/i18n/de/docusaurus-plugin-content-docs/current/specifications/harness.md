---
sidebar_position: 2
title: "Eval Harness v2.0"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "What the harness metrics feed into"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: Translate 30 Languages"
    to: https://champollion.dev/docs/tutorials/translate-30-languages
    kind: champollion
    note: "Use the harness to audit registers in production"
---
# Eval Harness v2.0

> **Zusammenfassung.** Diese Seite behandelt Installation, Konfiguration und Verwendung des MT-Evaluierungsharness — des Werkzeugs, das Übersetzungsmethoden anhand standardisierter Korpora benchmarkt und bewertete Run Cards erzeugt. Für die maßgeblichen Definitionen von Metriken, Schemata und Evaluierungsprotokoll siehe die [Benchmark Specification](/docs/specifications/benchmark).

Das Harness führt Übersetzungsexperimente durch und erzeugt Run Cards. Es übernimmt die Prompt-Konstruktion, API-Aufrufe, Bewertung und Ergebnisserialisierung — Sie stellen den Datensatz und das Modell bereit.

## Installation

**Anforderungen:** Python 3.10+

```bash
pip install sacrebleu aiohttp
```

Klonen Sie das Harness-Repository:

```bash
git clone https://github.com/gamedaysuits/arena.git
cd arena
```

## Verwendung

```bash
mt-eval run --corpus path/to/dataset.json
```

Dies führt jeden Eintrag im Korpus durch das konfigurierte Modell (oder Methoden-Plugin), bewertet die Ausgaben und schreibt eine Run-Card-JSON-Datei in das Ausgabeverzeichnis.

## CLI-Flags

### `mt-eval run`

| Flag | Erforderlich | Standard | Beschreibung |
|------|----------|---------|-------------|
| `--corpus` | ✅ | — | Pfad zur Korpusdatei (`.json`, `.jsonl`, `.tsv`) |
| `--source-file` / `--reference-file` | — | — | Paralleltextdateien (FLORES+, WMT-Format) |
| `-m, --model` | — | `gemini-pro` | Modell-Slug (Kurzname oder vollständige OpenRouter-ID). Wird über `shared/model-aliases.json` aufgelöst. Kommagetrennt für Mehrmodell-Läufe |
| `-d, --dataset` | — | `all` | Datensatzfilter: `all`, Segmentname oder ID-Bereich |
| `--ids` | — | — | Kommagetrennte Eintrags-IDs zur Evaluierung |
| `--source-lang` | — | `English` | Name der Ausgangssprache |
| `--target-lang` | — | — | Name der Zielsprache |
| `-p, --prompt` | — | `naive` | Prompt-Version (`naive`, `custom`, `champollion`) |
| `--coaching-file` | — | — | Pfad zur Coaching-Prompt-Textdatei |
| `--coaching` | — | — | Inline-Coaching-Text (Zeichenkette in Anführungszeichen) |
| `--method` | — | — | Pfad zum Methoden-Plugin-Verzeichnis (enthält `method.json` + Python-Modul) |
| `--method-card` | — | — | Pfad zur Method-Card-JSON für Leaderboard-Metadaten |
| `--fst-retries` | — | `0` | Anzahl der FST-Wiederholungsversuche (nur Standard-LLM-Methode) |
| `--skip-fst` | — | `false` | FST-Qualitätsschranke vollständig überspringen |
| `--tools` | — | `false` | Tool-Calling-Modus aktivieren |
| `--tools-list` | — | — | Kommagetrennte Tool-Namen |
| `--max-tool-rounds` | — | `8` | Maximale Anzahl an Tool-Calling-Runden pro Eintrag |
| `--hooks` | — | — | Namen der Post-Translation-Hooks |
| `--style-profile` | — | — | Pfad zu einer Stilprofil-JSON. Aktiviert Metriken zur Konsistenz des Schreibstils (informativ — niemals Teil des composite score; siehe [§ Schreibstil- und Register-Metriken](#writing-style-and-register-metrics-informational)) |
| `-b, --batch-size` | — | `25` | Einträge pro API-Aufruf |
| `-c, --concurrency` | — | `8` | Parallele API-Aufrufe |
| `--max-tokens` | — | `32768` | Maximale Tokens pro API-Aufruf |
| `--temperature` | — | `0.0` | Sampling-Temperatur (0.0 = deterministisch) |
| `--no-cache` | — | `false` | Antwort-Caching deaktivieren |
| `--cache-dir` | — | `eval/cache/harness` | Pfad zum Cache-Verzeichnis |
| `-o, --output-dir` | — | `eval/logs/harness` | Ausgabeverzeichnis für Run Cards und Logs |
| `-n, --name` | — | — | Menschenlesbarer Laufname |
| `--dry-run` | — | `false` | Konfiguration validieren, ohne API-Aufrufe durchzuführen |
| `--champollion-config` | — | — | Pfad zu `champollion.config.json` |
| `--champollion-cards-dir` | — | — | Verzeichnis der Sprachkarten |
| `--target-lang-code` | — | — | BCP-47-Sprachcode |

### Weitere Unterbefehle

| Unterbefehl | Beschreibung |
|------------|-------------|
| `mt-eval test <log_path>` | Ein abgeschlossenes Run-Log analysieren |
| `mt-eval publish <report_path>` | Eine Run Card an das Leaderboard übermitteln |
| `mt-eval compare <logs...>` | Mehrere Läufe nebeneinander vergleichen |
| `mt-eval dashboard <logs...>` | Ein HTML-Dashboard aus Run-Logs erzeugen |
| `mt-eval list models\|prompts\|datasets` | Verfügbare Ressourcen auflisten |
| `mt-eval export` | Das aktuelle Setup als Champollion-Methoden-Plugin paketieren |
| `mt-eval export-config` | Die aufgelöste MethodConfig (alle 8 kanonischen Felder) als JSON exportieren |

### Beispiele

```bash
# Run with defaults (gemini-pro alias → google/gemini-3.1-pro-preview, naive prompt)
mt-eval run --corpus data/edtekla-dev-v1.json

# Coached experiment with coaching file
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model google/gemini-3.1-pro \
  --coaching-file prompts/crk-coaching-v8.txt \
  --temperature 0.0

# Run a custom method plugin with FST retries
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --method ./methods/fst-gated-pipeline \
  --fst-retries 3
```

---

## Run-Card-Schema

Jedes Experiment erzeugt eine **Run Card** — ein eigenständiges JSON-Dokument. Die Struktur der obersten Ebene:

```json
{
  "run_id": "uuid-v4",
  "harness_version": "2.0",
  "model_slug": "google/gemini-3.1-pro",
  "model_id": "gemini-3.1-pro-001",
  "condition": "baseline",
  "timestamp": "2026-06-01T03:22:41Z",
  "elapsed_seconds": 142.7,
  "dataset": { ... },
  "config": { ... },
  "method_card": { ... },
  "system_prompt_sha256": "abc123...",
  "system_prompt_used": "You are a translator...",
  "fingerprint": { ... },
  "scores": { ... },
  "totals": { ... },
  "environment": { ... },
  "results": [ ... ],
  "run_card_hash": "sha256-of-entire-card"
}
```

Siehe die [Run Card Specification](/docs/specifications/run-card) für das vollständige Schema mit dokumentierten Feldern.

:::info Maßgebliches Schema
Die [Benchmark Specification](/docs/specifications/benchmark) ist die einzige Quelle der Wahrheit für das Run-Card-Schema. Für Metrikdefinitionen, composite weights und Qualitätsstufen siehe die [Scoring Specification](/docs/specifications/scoring). Diese Seite dokumentiert die Verwendung des Harness; die Spezifikationen definieren, was die Ausgaben bedeuten.
:::

### Wichtige Blöcke

**`dataset`** — Identifiziert, welcher Datensatz verwendet wurde, einschließlich seines Inhaltshashes, sodass Ergebnisse an eine bestimmte Version gebunden sind:

```json
// Example using master_corpus.json (62 gold + 342 textbook = 404)
{
  "id": "edtekla-dev-v1",
  "version": "1.0",
  "language_pair": "EN→CRK",
  "sha256": "...",
  "entry_count": 404
}
```

**`scores`** — Aggregierte Metriken für den Lauf:

```json
// Counts reflect the dataset used (here: master_corpus.json, 404 entries)
{
  "total": 404,
  "exact_matches": 12,
  "exact_match_rate": 0.0968,
  "fst_accepted": 87,
  "fst_acceptance_rate": 0.7016,
  "chrf_plus_plus": 42.31,
  "errors": 0,
  "avg_latency_seconds": 1.15,
  "median_latency_seconds": 1.02,
  "p95_latency_seconds": 2.34,
  "by_difficulty": { ... },
  "by_provenance": { ... }
}
```

**`totals`** — Token-Verbrauch und Kostenerfassung:

```json
{
  "prompt_tokens": 48200,
  "completion_tokens": 3100,
  "reasoning_tokens": 0,
  "cached_tokens": 12000,
  "total_cost_usd": 0.42,
  "cost_per_entry_usd": 0.0034,
  "reasoning_ratio": 0.0
}
```

---

## Schreibstil- und Register-Metriken (informativ)

Das Harness kann evaluieren, ob Übersetzungen einem Ziel-**Register** und **Schreibstil** entsprechen, über das `WritingStyleConsistency` Metrik-Plugin (`mt_eval_harness/plugins/writing_style.py`). Eine Übersetzung kann sprachlich korrekt sein, aber im falschen Register stehen — informelle Formulierungen in einem Rechtsdokument, formelhafte Standardtexte in Marketingtexten — und String-Metriken bemerken dies nicht. Diese Metriken schon.

**Was gemessen wird (pro Eintrag):**

| Metrik | Skala | Bedeutung |
|--------|-------|---------|
| `style_register_match` | boolesch | Entspricht die Ausgabe dem erwarteten Register? Das Ziel stammt aus dem Feld `register` des Korpuseintrags (siehe [Benchmark Spec §2.6](/docs/specifications/benchmark)) oder aus einem Stilprofil |
| `style_sentence_length_ratio` | float | Vorhergesagte vs. durchschnittliche Satzlänge der Referenz (1.0 = Übereinstimmung; Abweichung = Stildrift) |
| `style_formality_score` | 0.0–1.0 | Vorhandensein formeller/informeller Marker (T–V-Pronomen, Kontraktionen, …) anhand sprachspezifischer Marker-Ressourcen |

**Aggregat:** `style_consistency_rate` — der Anteil der Einträge ohne erkannte Register-Diskrepanz.

Aktivieren Sie ein benutzerdefiniertes Ziel mit `--style-profile path/to/profile.json` (z. B. ein Markenstimmen-Profil); ohne ein solches greift das Plugin auf die `register`-Metadaten jedes Korpuseintrags zurück, sofern vorhanden.

:::caution Ehrliche Abgrenzung
Diese Metriken sind **rein informativ** — sie sind niemals Teil des composite score, und die Formalitätserkennung ist markerbasiert (eine Heuristik), kein erlerntes Urteil. Behandeln Sie sie als Drift-Detektor für die Registertreue, nicht als Urteil über die Stilqualität.
:::

---

## Fingerprint vs. Run Card Hash {#fingerprint-vs-run-card-hash}

Das Harness erzeugt zwei verschiedene Hashes. Sie dienen unterschiedlichen Zwecken:

### Fingerprint

Der **Fingerprint** beantwortet die Frage: *„Könnte dieser Lauf reproduziert werden?"*

Er hasht die Kombination der Eingaben, die die Experimentkonfiguration definieren — nicht die Ausgaben:

- Datensatz-SHA-256
- Modell-Slug
- Bedingungslabel
- System-Prompt-SHA-256
- Temperatur
- Harness-Version

Zwei Läufe mit identischen Fingerprints verwendeten dasselbe Setup. Ihre Ergebnisse sollten vergleichbar sein (modulo API-Nichtdeterminismus).

### Run Card Hash

Der **Run Card Hash** beantwortet die Frage: *„Wurde diese spezifische Ergebnisdatei manipuliert?"*

Es ist der SHA-256 der gesamten Run-Card-JSON (ausgenommen das `run_card_hash`-Feld selbst). Wenn sich ein Feld ändert — ein Score, ein Zeitstempel, eine einzelne Ausgabe — bricht der Hash.

:::info Wann welcher zu verwenden ist
Verwenden Sie den **Fingerprint**, um vergleichbare Läufe zu gruppieren (dasselbe Experiment, unterschiedliche Ausführungen). Verwenden Sie den **Run Card Hash**, um die Integrität einer bestimmten Ergebnisdatei zu überprüfen.
:::

---

## Veröffentlichung auf dem Leaderboard

Verwenden Sie nach Abschluss eines Laufs `mt-eval publish`, um die Run Card zu übermitteln:

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

Wenn während des Laufs keine `--method-card` bereitgestellt wurde, startet `mt-eval publish` einen interaktiven Assistenten (`method_card_wizard.py`), der Sie durch die Beschreibung Ihrer Methode führt (Name, Klasse, verwendete Tools usw.). Die Ausgabe des Assistenten wird vor der Übermittlung in die Run Card eingebettet.

### Manuelle Übermittlung

Run Cards werden als JSON-Dateien im Ausgabeverzeichnis gespeichert. Sie können auch jede Run-Card-Datei über die Leaderboard-UI unter [/leaderboard](https://champollion.dev/leaderboard) oder über die API übermitteln:

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning Leaderboard-Validierung
Das Leaderboard validiert übermittelte Run Cards anhand des Datensatzregisters. Übermittlungen, die auf unbekannte Datensätze verweisen oder einen fehlerhaften `run_card_hash` aufweisen, werden abgelehnt.
:::

:::danger TRAINIEREN Sie NICHT mit Evaluierungsdaten
Wenn Ihre Methode den Evaluierungsdatensatz während der Entwicklung gesehen hat — als Trainingsdaten, Few-Shot-Beispiele, Wörterbucheinträge oder Prompt-Engineering-Material — wird Ihre Übermittlung **disqualifiziert**. Siehe [MT Evaluation](/docs/leaderboard/rules) für die Unterscheidung zwischen guten und schlechten Methoden.
:::

---

## Siehe auch

- [MT Evaluation](/docs/leaderboard/rules) — Überblick, Wertversprechen des Leaderboards und Hinweise zu guten/schlechten Methoden
- [Evaluation Datasets](/docs/leaderboard/datasets) — Datensatzformat, EDTeKLA, FLORES+
- [Run Card Specification](/docs/specifications/run-card) — das vollständige JSON-Schema
- [Building a Method](/docs/specifications/methods) — die Methodenschnittstelle zur Erstellung evaluierbarer Methoden
- [Method Leaderboard](https://champollion.dev/leaderboard) — Live-Benchmark-Scores
- [Benchmark Specification](/docs/specifications/benchmark) — Evaluierungsprotokoll, Korpusformat, Run-Card-Schema
- [Scoring Specification](/docs/specifications/scoring) — SSOT für Metriken, composite weights und Qualitätsstufen