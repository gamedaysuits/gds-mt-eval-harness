---
sidebar_position: 2
title: "Cookbook: Coached LLM Prompting"
related:
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
  - label: "Cookbook: Fine-Tuned Model"
    to: /docs/tutorials/fine-tuned-model
    kind: cookbook
  - label: "Coaching Data"
    to: https://champollion.dev/docs/concepts/coaching-data
    kind: champollion
    note: "How coaching data ships to production"
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
---
# Coached LLM Prompting

> **Die Idee:** Grammatikregeln, zweisprachige Wörterbücher und Stilhinweise werden direkt in den System-Prompt des LLM eingefügt. Kein Training, kein Fine-Tuning — lediglich strukturiertes linguistisches Wissen, das die Ausgabe in Richtung valider Übersetzungen lenkt.

:::info Dies ist ein Kochbuch, keine fertige Implementierung
Dieser Leitfaden skizziert den Ansatz und seine wesentlichen Entwurfsentscheidungen. Passen Sie ihn an Ihr Sprachpaar, die verfügbaren Ressourcen und Ihre Evaluierungsziele an.
:::

## Wann Sie diesen Ansatz verwenden sollten

- Sie verfügen über **linguistisches Wissen** über die Zielsprache (Grammatikregeln, Wörterbucheinträge, Stilpräferenzen), aber nicht über genügend Paralleldaten für ein Fine-Tuning
- Sie möchten **schnell iterieren** — Prompt-Änderungen werden in Sekunden ausgerollt, ohne erneutes Training
- Die Zielsprache weist **bekannte Muster** auf, die ein LLM falsch wiedergibt (Genuskongruenz, Schriftkonventionen, Formalitätsstufen)
- Sie möchten Coached Prompting gegen eine Baseline benchmarken und das Wirksame iterativ verbessern

## Funktionsweise

1. **Coaching-Daten zusammenstellen** — Grammatikregeln, ein zweisprachiges Wörterbuch und Stilhinweise in einer strukturierten JSON-Datei
2. **Register konfigurieren** — ein System-Prompt-Präfix, das Sprache, Schrift und Tonalität festlegt
3. **Harness ausführen** — die Coaching-Daten werden in jeden LLM-Prompt eingefügt
4. **Fehler überprüfen** — betrachten Sie, was das Quality Gate ablehnt, und fügen Sie Regeln hinzu, um diese Muster zu adressieren
5. **Iterieren** — jede Revision der Coaching-Datei ist ein neues Experiment; der Harness verfolgt sie alle

## Struktur der Coaching-Daten

```json title="coaching/<locale>.json"
{
  "grammar_rules": [
    "Adjectives agree in gender and number with the noun they modify",
    "Use formal register (vous) for all UI text",
    "Preserve interpolation variables exactly: {{name}}, {count}"
  ],
  "dictionary": {
    "dashboard": "tableau de bord",
    "settings": "paramètres",
    "deploy": "déployer"
  },
  "style_notes": "Prefer active voice. Avoid anglicisms where a native term exists. Keep sentences concise for UI readability."
}
```

## Wesentliche Entwurfsentscheidungen

**Regelspezifität vs. Kontextfenster:** Mehr Regeln geben dem LLM mehr Anleitung, beanspruchen jedoch das Kontextfenster, das für die eigentliche Übersetzung zur Verfügung steht. Beginnen Sie mit 5–10 wirkungsvollen Regeln und fügen Sie weitere nur dann hinzu, wenn Sie spezifische Fehlermuster erkennen.

**Wörterbuchabdeckung:** Sie benötigen kein vollständiges Wörterbuch — konzentrieren Sie sich auf Begriffe, die das LLM durchgängig falsch wiedergibt. Schon 20–30 erzwungene Begriffe können die Konsistenz erheblich verbessern.

**Reihenfolge der Regeln ist entscheidend:** Setzen Sie die wichtigsten Regeln an den Anfang. LLMs gewichten frühe Anweisungen stärker.

## Ein Experiment durchführen

```bash
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v1 \
  --coaching-file coaching/crk.json
```

## Vor- und Nachteile

| | |
|---|---|
| ✅ Keine Trainingskosten | ❌ Qualitätsobergrenze durch das Basiswissen des LLM begrenzt |
| ✅ Sofortige Iteration (Prompt ändern → erneut ausführen) | ❌ Das Kontextfenster begrenzt, wie viel Coaching hineinpasst |
| ✅ Funktioniert mit jedem LLM-Anbieter | ❌ Regeln können in Konflikt geraten — das Debuggen von Prompt-Wechselwirkungen ist eine Kunst |
| ✅ Transparent — Sie können genau lesen, was das LLM sieht | ❌ Erzeugt kein neues Wissen, sondern lenkt nur vorhandenes Wissen |

## Lässt sich gut kombinieren mit

- **[FST-Gated Pipeline](./fst-gated-pipeline)** — Coaching + morphologische Validierung erfasst, was Coaching allein übersieht
- **[Dictionary-Augmented LLM](./dictionary-augmented-llm)** — erzwungene Terminologie ist eine Form des Coachings
- **[Few-Shot Prompting](./few-shot-prompting)** — Beispiele + Regeln gemeinsam sind wirkungsvoller als jedes für sich allein

## Siehe auch

- [Method Interface](/docs/specifications/methods) — Format der Coaching-Daten und das TranslationMethod-Protokoll
- [Support a Low-Resource Language](/docs/community/low-resource-languages) — der vollständige Kontext
- [Eval Harness](/docs/specifications/harness) — wie Sie Experimente durchführen