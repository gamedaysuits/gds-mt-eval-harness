---
sidebar_position: 1
title: "Für Sprachgemeinschaften"
---
# Für Sprachgemeinschaften

> **Zusammenfassung.** Ein Leitfaden für Sprecherinnen und Sprecher indigener und ressourcenarmer Sprachen, der erläutert, wie man zur Arena beitragen kann (Referenzübersetzungen, Übersetzungsprüfung, Coaching-Daten) und was die Gemeinschaft im Gegenzug erhält (Eigentum am Code, API-Einnahmen, vollständige Kontrolle über die Bereitstellung). Keine Programmierkenntnisse erforderlich.

Sie müssen kein Programmierer sein, um zur Arena beizutragen. Wenn Sie eine indigene oder ressourcenarme Sprache sprechen, sind Sie die wichtigste Person in diesem Ökosystem.

---

## Was wir von Ihnen benötigen

### Referenzübersetzungen

Wir benötigen kuratierte Übersetzungspaare für die Evaluierung — Englisch auf der einen Seite, Ihre Sprache auf der anderen. Diese werden zum „Lösungsschlüssel“, anhand dessen alle Übersetzungsmethoden bewertet werden.

Sie könnten diese erstellen aus:
- **Bildungsmaterialien** — Lehrbuchübungen, Unterrichtspläne, Arbeitsblätter
- **Gemeinschaftsdokumenten** — Sitzungsprotokolle, Newsletter, Ankündigungen
- **Alltagsphrasen** — UI-Texte, App-Beschriftungen, gängige Ausdrücke
- **Kulturellen Inhalten** — Geschichten, Lieder oder Beschreibungen (mit entsprechenden Genehmigungen)

Das Format ist einfaches JSON:
```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

### Übersetzungsprüfung

Jede Methode, die beansprucht, funktionierende Übersetzungen zu erzeugen, benötigt eine menschliche Validierung. Zweisprachige Sprecher prüfen die Ausgaben und teilen uns mit, ob der Computer es richtig gemacht hat — und, was noch wichtiger ist, *warum* er einen Fehler gemacht hat.

### Coaching-Daten

Grammatikregeln, Wörterbucheinträge, morphologische Muster — dies sind die linguistischen Ressourcen, die Übersetzungsmethoden funktionsfähig machen. Ihr Wissen über die Funktionsweise Ihrer Sprache ist durch kein KI-Modell zu ersetzen.

---

## Was Sie im Gegenzug erhalten

### Eigentum

Wenn eine Übersetzungsmethode für Ihre Sprache entwickelt und in der Arena validiert wird, geht das [Eigentum auf Ihre Governance-Organisation über](/docs/sovereignty/ownership-transfer). Sie besitzen den Code, die Modellgewichte und die Bereitstellung.

### Einnahmen

Wenn Entwickler die Methode Ihrer Sprache über die champollion-API nutzen, erhält Ihre Gemeinschaft [90 % der API-Einnahmen](/docs/sovereignty/economic-model). Die verbleibenden 10 % decken die Infrastrukturkosten.

### Kontrolle

Ihre Governance-Organisation kontrolliert:
- Wer auf die Methode zugreifen kann
- Ob sie kommerziell genutzt werden darf
- Welche Preisbedingungen gelten
- Wann und wie sie aktualisiert wird
- Welche Daten für die weitere Entwicklung verwendet werden

---

## So beteiligen Sie sich

1. **Nehmen Sie Kontakt auf** — Eröffnen Sie ein Issue im [Arena-Repository](https://github.com/gamedaysuits/arena) oder schreiben Sie eine E-Mail an die Betreuer
2. **Beschreiben Sie Ihre Sprache** — Zu welcher Familie gehört sie? Wie viele Sprecher gibt es? Welche Schriftsysteme werden verwendet? Welche computergestützten Ressourcen existieren (FSTs, Wörterbücher, Korpora)?
3. **Fangen Sie klein an** — Schon 50 kuratierte Übersetzungspaare genügen, um einen Evaluierungsdatensatz zu erstellen und eine neue Leaderboard-Kategorie zu eröffnen
4. **Verbinden Sie uns mit Ihrer Governance** — Wer in Ihrer Gemeinschaft hat die Hoheit über Sprachdaten und -technologie? Das Souveränitätsmodell der Arena erfordert einen Governance-Partner

---

## Datensouveränität

Ihre Sprachdaten gehören Ihnen. Die Arena basiert auf den [OCAP®-Prinzipien](/docs/sovereignty/data-sovereignty):

- Wir erfassen oder speichern Ihre linguistischen Daten niemals auf unseren Servern
- Übersetzungsmethoden nutzen die `api`-Architektur — sämtliche Coaching-Daten, Wörterbücher und Grammatikregeln verbleiben auf einer von Ihnen kontrollierten Infrastruktur
- Sie entscheiden, wer Methoden für Ihre Sprache entwickeln darf
- Leaderboard-Bewertungen belegen, dass eine Methode funktioniert; sie erteilen jedoch keine Erlaubnis, diese bereitzustellen

---

## Siehe auch

- [Datensouveränität](/docs/sovereignty/data-sovereignty) — das vollständige Rahmenwerk aus OCAP, CARE und Te Mana Raraunga
- [Eigentumsübertragung](/docs/sovereignty/ownership-transfer) — was geschieht, wenn eine Methode gewinnt
- [Das Wirtschaftsmodell](/docs/sovereignty/economic-model) — wie Bewertungen zu Einnahmen werden
- [Eine ressourcenarme Sprache unterstützen](/docs/community/low-resource-languages) — technischer Kontext für Forschende, die mit Gemeinschaften zusammenarbeiten