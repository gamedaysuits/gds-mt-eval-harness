---
sidebar_position: 2
title: "Eigentumsübertragung"
---
# Eigentumsübertragung

> **Zusammenfassung für Entscheidungsträger.** Wenn eine Übersetzungsmethode die Stufe „Deployable“ (Composite-Score ≥ 0,70) erreicht und das Community-Review besteht, wird das Eigentum am Code vom Forschenden auf die indigene Governance-Organisation übertragen. Diese Seite dokumentiert die fünfstufige Übertragungspipeline, die OCAP®-Ausrichtung sowie Leitlinien für Forschende, die Methoden für indigene Sprachen entwickeln.

Wenn eine Übersetzungsmethode in der Arena-Bestenliste gewinnt, was geschieht dann mit dem Code? Für indigene und ressourcenarme Sprachen lautet die Antwort nicht „der Forschende behält ihn“. Die Antwort lautet: **die Community besitzt ihn.**

---

## Funktionsweise

Die Arena erzwingt eine klare Pipeline von der Forschung bis zum Community-Eigentum:

### 1. Methodenentwicklung
Ein Forschender, Studierender oder Entwickler erstellt eine Übersetzungsmethode — eine FST-gesteuerte Pipeline, ein gecoachtes LLM, ein feinabgestimmtes Modell oder einen beliebigen anderen Ansatz. Die Entwicklung erfolgt mit den eigenen Ressourcen.

### 2. Arena-Evaluierung
Die Methode wird über das [Eval-Harness](/docs/specifications/harness) gebenchmarkt. Jede Einreichung erhält einen Fingerabdruck zu einem bestimmten Git-Commit und einer bestimmten Datensatzversion. Die Scores sind reproduzierbar.

### 3. Community-Review
Bei Methoden für indigene Sprachen werden die Ergebnisse von Sprachfachkräften der Community und von Governance-Organisationen geprüft. Ein hoher Wert in der Bestenliste belegt, dass die Methode *funktioniert*; er belegt nicht, dass sie *angemessen* ist.

### 4. Code-Übertragung
Wenn eine Methode die Stufe **Deployable** erreicht (Composite-Score ≥ 0,70 gegenüber der Goldstandard-Evaluierung) **und** das Community-Review besteht (menschliche Validierung):
- Der Forschende übergibt den Quellcode
- Das rechtliche Eigentum geht auf die indigene Governance-Organisation über (z. B. einen Stammesrat, eine Sprachbehörde oder eine Métis-Organisation)
- Die Governance-Organisation verwahrt die Verschlüsselungsschlüssel für die Evaluierungsdatensätze
- Die Methode wird zu einem von der Community kontrollierten Vermögenswert

Siehe die [Scoring-Spezifikation](/docs/specifications/scoring), §5 für die Definitionen der Qualitätsstufen sowie die [Benchmark-Spezifikation](/docs/specifications/benchmark), §8.3 für die vollständigen Übertragungsbedingungen und §7 für das Gate der menschlichen Validierung.

### 5. Produktiv-Bereitstellung
Die Methode wird als [champollion](https://champollion.dev)-Plugin exportiert und auf der Produktiv-API bereitgestellt. Die Community kontrolliert:
- Wer auf die Methode zugreifen kann
- Welche Preisbedingungen gelten
- Ob die Methode kommerziell genutzt werden darf
- Wann und wie die Methode aktualisiert wird

---

## Warum dies wichtig ist

Traditionelle ML-Forschung folgt einem extraktiven Muster:
1. Forschende sammeln Daten von einer Community
2. Forschende trainieren ein Modell
3. Forschende veröffentlichen eine Arbeit
4. Die Community erhält nichts

Dieses Muster wirkt mittlerweile im industriellen Maßstab. Metas OMT-1600 (März 2026) trainierte Übersetzungsmodelle für 1.600 Sprachen — darunter indigene Sprachen wie Plains Cree — auf Basis von aus dem Web gescrapten Daten und Bibelübersetzungen. Die Modelle wurden ohne Protokolle zur Einwilligung der Community trainiert, die Gewichte stehen derzeit nicht zum Download bereit, und die Communities, deren Sprachen modelliert wurden, haben weder Eigentumsanteile noch eine Governance-Rolle noch Einnahmen. Die Arbeit ist das Produkt. Die Community ist die Datenquelle.

Die Arena kehrt dies um:
1. Forschende erstellen eine Methode
2. Die Arena validiert sie gegen von der Community kuratierte Korpora mit morphologischen Metriken
3. Die Community erhält das Eigentum am funktionierenden Code
4. Die Community erzielt Einnahmen aus der API-Nutzung

**Dies ist der grundlegende Unterschied zwischen Champollion und allen anderen LRL-MT-Bestrebungen, einschließlich OMT-1600:** Wir erstellen nicht nur Methoden für Communities — wir übertragen das Eigentum an Methoden *an* die Communities. Der Code, die Gewichte, die Bereitstellungsinfrastruktur — all dies wird zum Eigentum der Community. Dies ist kein theoretisches Rahmenwerk — es ist die operative Pipeline für jede Methode für indigene Sprachen auf der Plattform.

---

## OCAP®-Ausrichtung

Der Prozess der Eigentumsübertragung setzt die [OCAP®-Prinzipien](/docs/sovereignty/data-sovereignty) unmittelbar um:

| Prinzip | Umsetzung |
|---|---|
| **Ownership** | Die Governance-Organisation hält die Rechte am Methodencode und an den Modellgewichten |
| **Control** | Die Governance-Organisation kontrolliert Bereitstellungsbedingungen, Zugriff und Preisgestaltung |
| **Access** | Community-Mitglieder greifen über die champollion-API oder den direkten Download auf die Methode zu |
| **Possession** | Linguistische Ressourcen (Coaching-Daten, Wörterbücher, FST-Regeln) verbleiben über die `api`-Methode auf einer von der Community kontrollierten Infrastruktur |

---

## Für Forschende

Wenn Sie eine Methode für eine indigene Sprache entwickeln:

1. **Bauen Sie eine Beziehung** zur Sprachgemeinschaft auf, bevor Sie beginnen
2. **Verwenden Sie offen lizenzierte Daten** für die Entwicklung (keine Community-beschränkten Ressourcen)
3. **Dokumentieren Sie die Herkunft** in Ihrer [Run-Card](/docs/specifications/run-card) — führen Sie jede Ressource, ihre Lizenz und ihren Ursprung auf
4. **Seien Sie bereit zur Übertragung** — wenn Ihre Methode erfolgreich ist, gehört der Code der Community, nicht Ihnen
5. **Dies ist ein Merkmal, keine Einschränkung** — Ihr Beitrag besteht in der Architektur und Technik, die Sie veröffentlichen und wiederverwenden können. Der Beitrag der Community besteht im linguistischen Wissen, das die Methode für ihre Sprache funktionieren lässt.

---

## Siehe auch

- [Data Sovereignty](/docs/sovereignty/data-sovereignty) — OCAP-, CARE- und Te-Mana-Raraunga-Prinzipien
- [Das ökonomische Modell](/docs/sovereignty/economic-model) — wie aus Eigentum Einnahmen werden
- [Eine ressourcenarme Sprache unterstützen](/docs/community/low-resource-languages) — der Forschungskontext