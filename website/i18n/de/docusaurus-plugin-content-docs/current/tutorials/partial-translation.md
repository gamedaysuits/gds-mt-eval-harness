---
sidebar_position: 10
title: "Cookbook: Partielle Übersetzung (Mensch + Maschine)"
---
# Partielle Übersetzung (Mensch + Maschine)

> **Die Idee:** Übersetzen Sie eine repräsentative Stichprobe manuell, weisen Sie nach, dass Ihre maschinelle Methode dem menschlichen Stil auf dieser Stichprobe entspricht, und übersetzen Sie anschließend die verbleibende Masse automatisch. So verbinden Sie menschliche Qualität mit maschineller Skalierbarkeit — der Mensch setzt den Maßstab, die Maschine folgt ihm.

:::info Dies ist ein Kochbuch, keine fertige Implementierung
Dieser Leitfaden skizziert den hybriden Mensch-Maschine-Arbeitsablauf. Er ist besonders relevant für Übersetzungsagenturen, Sprachmittler aus der Gemeinschaft sowie für Bildungskontexte.
:::

## Wann sollten Sie dies verwenden

- Sie haben **Zugang zu fließend sprechenden Personen**, aber deren Zeit ist begrenzt
- Sie müssen ein **großes Volumen** übersetzen, aber nur ein kleiner Teil muss perfekt sein
- Sie möchten eine **Qualitätsbasis** mit menschlicher Übersetzung **etablieren** und anschließend mit MT skalieren
- Sie arbeiten in einem **Bildungs- oder Gemeinschaftskontext**, in dem eine menschliche Überprüfung einer Teilmenge machbar ist

## Funktionsweise

```
[Full corpus: 1,000 entries]
        │
        ├── [100 entries] ──→ Human translator ──→ Gold translations
        │                                              │
        │                                              ▼
        │                                    Train / prompt machine
        │                                    method to match style
        │                                              │
        └── [900 entries] ──→ Machine method ──→ Auto translations
                                                       │
                                                       ▼
                                              [Optional: human review
                                               of flagged entries]
```

1. **Wählen Sie eine repräsentative Stichprobe aus** — decken Sie verschiedene Satztypen, Längen und Themen ab
2. **Übersetzen Sie die Stichprobe von Hand** — legen Sie den Goldstandard für Stil, Register und Terminologie fest
3. **Konfigurieren Sie Ihre maschinelle Methode** — verwenden Sie die menschlichen Übersetzungen als Coaching-Daten, Few-Shot-Beispiele oder Fine-Tuning-Daten
4. **Bewerten Sie die Maschine anhand der menschlichen Stichprobe** — entspricht die Maschine dem Stil des Menschen?
5. **Übersetzen Sie den Rest automatisch** — sofern die maschinelle Qualität auf der Stichprobe akzeptabel ist
6. **Optionale menschliche Überprüfung** — markieren Sie Ausgaben mit geringer Konfidenz für die Überprüfung durch sprachkundige Personen

## Qualitätssicherung: Der Stilabgleichstest

```bash
# Translate the human-translated sample with your machine method
python eval/baseline_experiment.py \
  --dataset data/human-sample.json \
  --condition coached-v3

# Compare: does the machine match the human translator's choices?
# Look at: chrF++ (similarity), FST acceptance (validity),
# and qualitative patterns (register, formality, terminology)
```

## Auswahl der Stichprobe

**Decken Sie die Verteilung ab.** Ihre 100 Einträge sollten Folgendes umfassen:
- Kurze Wendungen (1–3 Wörter) und vollständige Sätze
- Häufiges Vokabular und domänenspezifische Begriffe
- Einfache und komplexe Strukturen
- Mehrere grammatikalische Merkmale (Fragen, Imperative, Konditionalsätze)

**Picken Sie nicht die einfachen Einträge heraus.** Die Stichprobe muss Einträge enthalten, mit denen Ihre Methode voraussichtlich Schwierigkeiten hat — genau dort ist menschliche Qualität am wichtigsten.

## Der Arbeitsablauf zur gemeinschaftlichen Überprüfung

Für indigene Sprachgemeinschaften berücksichtigt dieser Ansatz die Zeit der sprachkundigen Personen:

1. **Eine sprachkundige Person übersetzt 50–100 Einträge** (2–4 Stunden konzentrierter Arbeit)
2. **Die Maschine übersetzt die verbleibenden 900** und verwendet dabei die Arbeit der sprachkundigen Person als Coaching-Daten
3. **Die sprachkundige Person überprüft die markierten Einträge** — nur diejenigen, bei denen die Maschine am wenigsten zuversichtlich war (weitere 1–2 Stunden)
4. **Ergebnis:** 1.000 Übersetzungen in nahezu menschlicher Qualität mit etwa 5 statt etwa 50 Stunden Aufwand der sprachkundigen Person

## Vor- und Nachteile

| | |
|---|---|
| ✅ Verbindet menschliche Qualität mit maschineller Skalierbarkeit | ❌ Erfordert anfänglichen menschlichen Aufwand |
| ✅ Berücksichtigt die begrenzte Verfügbarkeit sprachkundiger Personen | ❌ Die Maschine erfasst möglicherweise nicht alle stilistischen Nuancen |
| ✅ Natürlicher Arbeitsablauf zur Qualitätssicherung | ❌ Die Auswahl der Stichprobe wirkt sich auf die Gesamtqualität aus |
| ✅ Hervorragend geeignet für Gemeinschafts-/Bildungskontexte | ❌ Engpass bei der menschlichen Überprüfung markierter Einträge |

## Lässt sich gut kombinieren mit

- **[Coached LLM Prompting](./coached-llm-prompting)** — menschliche Übersetzungen fließen in die Coaching-Daten ein
- **[Few-Shot Prompting](./few-shot-prompting)** — menschliche Übersetzungen als kontextbezogene Beispiele
- **[Corpus Creation](./corpus-creation)** — die menschliche Stichprobe IST Korpuserstellung

## Siehe auch

- [Für Sprachgemeinschaften](/docs/community/for-language-communities) — Modell zur Einbindung der Gemeinschaft
- [Data Sovereignty](/docs/sovereignty/data-sovereignty) — Eigentum an Übersetzungsdaten
- [Eine ressourcenarme Sprache unterstützen](/docs/community/low-resource-languages)