---
sidebar_position: 11
title: "Kochbuch: Korpus-Erstellung"
---
# Leitfaden zur Korpuserstellung

> **Die Idee:** Bevor Sie eine Übersetzungsmethode evaluieren können, benötigen Sie einen Evaluationskorpus. Dieser Leitfaden behandelt den Aufbau eines solchen Korpus von Grund auf — Datenbeschaffung, Formatanforderungen, Qualitätsstandards, Lizenzierung sowie das Beitragen zur Arena.

:::info Dies ist keine Übersetzungsmethode
Dieser Leitfaden ist die Voraussetzung für viele Methoden. Ein guter Evaluationskorpus ist das Fundament, das alles andere erst möglich macht. Selbst 50 kuratierte Paare reichen aus, um einen neuen Leaderboard-Track zu eröffnen.
:::

## Wann Sie dies verwenden sollten

- Sie möchten dem Arena-Leaderboard ein **neues Sprachpaar hinzufügen**
- Sie sind **Sprachlehrkraft** und möchten studentische Übersetzungen benchmarken
- Sie sind eine **Sprachfachkraft aus der Community** mit Zugang zu zweisprachigen Materialien
- Sie sind **Forschende/r** und benötigen einen standardisierten Evaluationssatz für Ihr Sprachpaar

## Korpusformat

Das Harness verarbeitet einfaches JSON:

```json title="my-corpus.json"
{
  "metadata": {
    "name": "Quechua Dev v1",
    "version": "1.0.0",
    "source_language": "eng",
    "target_language": "que",
    "entry_count": 75,
    "license": "CC-BY-SA-4.0",
    "author": "Your Name / Organization",
    "description": "75 English-Quechua pairs from educational materials"
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello, how are you?",
      "reference": "Allillanchu, imaynallan kashanki?"
    },
    {
      "id": 2,
      "source": "The sun is shining today",
      "reference": "Kunan p'unchay inti k'anchashan"
    }
  ]
}
```

## Woher Sie Daten beziehen

| Quelle | Qualität | Umfang | Lizenzierung |
|--------|---------|--------|-----------|
| **Lehrbücher / Bildungsmaterialien** | Hoch (von Fachleuten geprüft) | Niedrig-mittel | Beim Verlag erfragen |
| **Behördendokumente** | Mittel (formales Register) | Mittel-hoch | Häufig gemeinfrei |
| **Zweisprachige Wörterbücher** | Hoch (verifizierte Einträge) | Mittel | Variiert |
| **Älteste / Sprechende aus der Community** | Höchste (muttersprachliche Intuition) | Niedrig (begrenzte Zeit) | Von der Community verwaltet |
| **Religiöse Texte** | Mittel (domänenspezifisch) | Hoch | Üblicherweise offen |
| **Bestehende Korpora** (Hansard, FLORES) | Mittel-hoch | Hoch | Lizenz prüfen |
| **Eigenhändig erstellt** | Höchste | Niedrig | Sie besitzen sie |

## Qualitätsstandards

Ein guter Evaluationskorpus weist auf:

1. **Vielfältige Inhalte** — nicht nur Begrüßungen oder einfache Phrasen. Beziehen Sie Fragen, Aufforderungen, komplexe Sätze und domänenspezifische Begriffe ein
2. **Verifizierte Übersetzungen** — von mindestens einer fließend sprechenden Person geprüft, idealerweise von zwei
3. **Konsistente Orthografie** — durchgängig eine Schrift, eine Rechtschreibkonvention
4. **Unabhängige Quellen** — nicht aus demselben Text abgeleitet, mit dem die Methoden trainiert werden
5. **Klare Lizenzierung** — eine ausdrückliche Lizenz, die die Nutzung zu Evaluationszwecken gestattet

:::danger Korpuskontamination
Der Evaluationskorpus muss von jeglichen Trainingsdaten **unabhängig** sein. Wurde eine Methode mit Daten aus dem Evaluationskorpus trainiert oder geprompted, so wird sie disqualifiziert. Konzipieren Sie Ihren Korpus von Anfang an als zurückgehaltenen (held-out) Datensatz.
:::

## Richtlinien zum Umfang

| Umfang | Was er ermöglicht |
|------|----------------|
| **50 Einträge** | Minimal funktionsfähige Evaluation — ausreichend, um grobe Qualitätsunterschiede zu erkennen |
| **100–200 Einträge** | Verlässliche Rangfolge — ausreichend für statistische Signifikanz zwischen Methoden |
| **500+ Einträge** | Forschungstauglich — robuste composite scores, Konfidenzintervalle |
| **1.000+ Einträge** | Goldstandard — entspricht der Abdeckung von FLORES devtest |

Beginnen Sie im Kleinen. 50 Einträge reichen aus, um einen Leaderboard-Track zu eröffnen. Sie können später erweitern.

## Beitragen zur Arena

1. **Erstellen Sie Ihren Korpus** im oben gezeigten JSON-Format
2. **Lizenzieren Sie ihn** — CC BY-SA 4.0 wird für offene Evaluation empfohlen; CC BY-NC-SA 4.0 für eingeschränkte Nutzung
3. **Reichen Sie einen PR** beim [eval harness repo](https://github.com/gamedaysuits/arena) mit Ihrem Korpus in `data/` ein
4. **Das Leaderboard öffnet sich automatisch** für Ihr Sprachpaar, sobald der Korpus gemergt wurde

## Für indigene Sprachgemeinschaften

Die Korpuserstellung ist ein Akt der **Sprachsouveränität**. Ihr Korpus, Ihre Bedingungen:

- Sie entscheiden über Lizenz und Zugangsbedingungen
- Sie können einen **öffentlichen Entwicklungssatz** beisteuern (für die Methodenentwicklung) und gleichzeitig einen **geheimen Testsatz** (für die offizielle Evaluation) unter Kontrolle der Community behalten
- Das [Souveränitäts-Framework](/docs/sovereignty/data-sovereignty) schützt Ihre Daten auf jeder Ebene

Selbst ein kleiner Korpus ist ein **strategisches Gut** — er ist der Maßstab, der entscheidet, was „gut genug“ für Ihre Sprache bedeutet.

## Lässt sich gut kombinieren mit

- **[Partielle Übersetzung](./partial-translation)** — die Erstellung eines Korpus IST der menschliche Übersetzungsschritt
- **[Rückübersetzung](./back-translation)** — synthetische Daten ergänzen von Menschen erstellte Korpora
- Jedes andere Kochbuch — alle benötigen einen Evaluationskorpus

## Siehe auch

- [Evaluationsdatensätze](/docs/leaderboard/datasets) — bestehende Korpora (EDTeKLA, FLORES+)
- [Datensouveränität](/docs/sovereignty/data-sovereignty) — Eigentum und Kontrolle
- [Für Sprachgemeinschaften](/docs/community/for-language-communities) — Einbindung der Community
- [Eine ressourcenarme Sprache unterstützen](/docs/community/low-resource-languages) — das Gesamtbild