---
sidebar_position: 1
title: "Eine Methode einreichen"
related:
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
    note: "The contract your method implements"
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
    note: "What every published run must disclose"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
    note: "The fastest first method to submit"
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
---
# Eine Methode einreichen

> **Zusammenfassung.** Eine schrittweise Schnellstartanleitung für das Einreichen Ihres ersten Benchmark-Laufs auf das Leaderboard. Klonen Sie die Harness, führen Sie sie gegen einen Datensatz aus, überprüfen Sie Ihre Run Card und reichen Sie sie ein. Dauert 10 Minuten, wenn Sie einen API-Schlüssel haben.

Diese Anleitung führt Sie durch das Einreichen Ihres ersten Benchmark-Laufs auf das Leaderboard der MT Eval Arena.

---

## Voraussetzungen

- **Python 3.10+**
- **Einen OpenRouter-API-Schlüssel** (oder ein Äquivalent für Ihren Modellanbieter)
- **Eine Übersetzungsmethode** — alles, was Übersetzungen aus einem Quelltext erzeugt

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## Schritt 1: Die Harness ausführen

Die Harness bewertet Ihre Methode gegen einen standardisierten Datensatz:

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| Flag | Funktion |
|---|---|
| `--corpus` | Pfad zum Evaluierungskorpus (`.json`, `.jsonl`, `.tsv`) |
| `--model` | Modell-Slug — Kurzalias (z. B. `gemini-pro`) oder vollständige OpenRouter-ID |
| `--condition` | Bezeichnung für Ihre Methode (erscheint auf dem Leaderboard) |
| `--temperature` | Sampling-Temperatur (niedriger = deterministischer) |
| `--fst-retries` | Optional: Anzahl der FST-Wiederholungsversuche |
| `--submit` | Die Run Card automatisch auf das Leaderboard einreichen |

Die Harness erzeugt eine **Run Card** — eine eigenständige JSON-Datei mit Ihren Bewertungen, dem Datensatz-Hash, dem Modell-Slug und einem kryptografischen Fingerabdruck, der die Ergebnisse mit der exakten Experimentkonfiguration verknüpft.

---

## Schritt 2: Ihre Run Card überprüfen

Run Cards werden in `results/` gespeichert. Prüfen Sie Ihre vor dem Einreichen:

```bash
cat results/your-run-card.json | python -m json.tool
```

Wichtige zu prüfende Felder:
- `scores.chrf_plus_plus` — Ihre primäre Qualitätsmetrik
- `scores.exact_match_rate` — Anteil der perfekten Übersetzungen
- `scores.fst_acceptance_rate` — morphologische Gültigkeit (falls FST verwendet wurde)
- `totals.total_cost_usd` — die Kosten des Laufs
- `fingerprint` — der Reproduzierbarkeits-Hash des Experiments

Siehe die [Run-Card-Spezifikation](/docs/specifications/run-card) für das vollständige Schema.

---

## Schritt 3: Einreichen

### Automatische Einreichung

Wenn Sie beim Ausführen der Harness `--submit` übergeben haben, wurde Ihre Run Card bereits hochgeladen.

### Manuelle Einreichung

Reichen Sie eine beliebige Run Card über die API ein:

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

Oder laden Sie sie über die [Leaderboard-Benutzeroberfläche](https://champollion.dev/leaderboard) hoch.

---

## Was als Nächstes geschieht

1. Ihre Einreichung wird validiert (Datensatz-Hash, Integrität der Run Card)
2. Die Ergebnisse erscheinen auf dem Leaderboard als **Self-benchmarked** (Vertrauensstufe 1)
3. Um den Status **GDS Verified** zu erhalten, reichen Sie Ihre Methode als installierbares Plugin ein, damit Maintainer Ihre Ergebnisse reproduzieren können
4. Für Methoden indigener Sprachen: Wenn Ihre Methode die Spitze erreicht, beginnt der Prozess der [Eigentumsübertragung](/docs/sovereignty/ownership-transfer)

---

## Siehe auch

- [Harness-Verwendung](/docs/specifications/harness) — vollständige CLI-Referenz
- [Leaderboard-Regeln](/docs/leaderboard/rules) — Einreichungskriterien und Anti-Gaming-Richtlinien
- [Eine Methode erstellen](/docs/specifications/methods) — das TranslationMethod-Protokoll
- [Datensätze](/docs/leaderboard/datasets) — verfügbare Evaluierungsdatensätze