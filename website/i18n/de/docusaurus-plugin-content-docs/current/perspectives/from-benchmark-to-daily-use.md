---
sidebar_position: 3
title: "Vom Benchmark zum täglichen Einsatz: Der Weg über das Post-Editing"
slug: '/perspectives/from-benchmark-to-daily-use'
description: "Wie aus einer benchmarkten Übersetzungsmethode ein Community-Übersetzungsworkflow wird: maschineller Entwurf, Post-Editing durch fließend sprechende Personen, veröffentlichter Text – mit ehrlichen Qualitätsschwellen bei jedem Schritt."
related:
  - label: "Deploy to Production"
    to: /docs/getting-started/deploy-to-production
    kind: guide
    note: "From proven method to live translation"
  - label: "Cookbook: Partial Translation (Human + Machine)"
    to: /docs/tutorials/partial-translation
    kind: cookbook
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The quality thresholds behind the path"
  - label: "Translation Is Not Revitalization"
    to: /docs/perspectives/translation-is-not-revitalization
    kind: position
---
# Vom Benchmark zur täglichen Nutzung: Der Weg über das Post-Editing

> **Die Kurzfassung.** Eine Bestenlisten-Bewertung ist kein Produkt. Der Weg von „diese Methode erzielt 0,78“ bis hin zu „das Stammesbüro veröffentlicht jede Woche Dokumente in der Sprache“ führt über genau einen Workflow: Die Maschine erstellt einen Entwurf, eine sprachkundige Person korrigiert ihn, und nur der korrigierte Text wird veröffentlicht. Jeder Qualitätsschwellenwert in unseren Spezifikationen ist auf diesen Workflow abgestimmt — nicht auf unüberwachte maschinelle Ausgaben, die wir für keine Sprache auf dieser Plattform befürworten.

Mitunter wird gefragt, wann eine Übersetzungsmethode „gut genug zum einfachen Verwenden“ sein wird. Für die Sprachen, die diese Arena bedient, birgt diese Frage eine Falle. Die ehrliche Antwort lautet, dass die anzustrebende Messlatte nicht „gut genug zur ungeprüften Veröffentlichung“ ist — sie lautet **„gut genug, dass die Durchsicht eines Entwurfs der Übersetzung von Grund auf überlegen ist.“** Diese Messlatte liegt deutlich niedriger, sie ist messbar, und ihr Überschreiten verändert, was ein gemeinschaftliches Übersetzungsbüro in einer Woche leisten kann.

---

## Der Workflow von Anfang bis Ende

```
 English source document
        │
        ▼
 Machine draft  ←  a benchmarked, community-owned method
        │
        ▼
 Fluent-speaker post-edit  ←  the human gate; nothing skips it
        │
        ▼
 Published text  ←  carries human approval, not a machine score
        │
        ▼
 (Optional, community-controlled) corrections become
 data that improves the next version of the method
```

Drei Punkte sind zu beachten:

1. **Die Maschine veröffentlicht niemals.** Die Ausgabeeinheit ist ein Entwurf. Der Korrekturdurchlauf der sprachkundigen Person ist keine am Ende angesetzte Qualitätssicherung — er ist der Workflow.
2. **Die Zeit der sprachkundigen Person ist die zu optimierende Ressource.** Eine Methode ist genau insofern besser als eine andere, als sie der sprachkundigen Person weniger zu korrigieren hinterlässt. Forschung zum Post-Editing für ressourcenreiche Sprachen zeigt durchgängig, dass es bei moderater MT-Qualität schneller ist als die Übersetzung von Grund auf (Plitt & Masselot 2010; Green, Heer & Manning 2013, beide mit Links zitiert in [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization)). Ob dies für polysynthetische Sprachen gilt, ist genau das, was der Benchmark herauszufinden hilft — wir behandeln es als eine pro Sprache zu verifizierende Hypothese, nicht als Annahme.
3. **Die Rückkopplungsschleife liegt in eigener Hand.** Jedes korrigierte Dokument sind potenzielle Trainings- und Coaching-Daten — und es gehört der Gemeinschaft, die es zu ihren eigenen Bedingungen unter den Regeln der [Datensouveränität](/docs/sovereignty/data-sovereignty) zurückspeisen kann (oder auch nicht). Der Rückkopplungsmechanismus ist ein Designziel der Plattform, noch keine fertige Funktion; siehe [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections) dazu, wie Korrekturen und Herkunftsnachweis funktionieren sollen.

## Was die Qualitätsstufen für die reale Nutzung bedeuten

Die Bestenliste bewertet Methoden anhand eines Composite aus automatisierten Metriken ([Scoring Specification](/docs/specifications/scoring)), und die Bewertungen werden benannten Stufen zugeordnet. Hier die ehrliche Übersetzung dieser Stufen in Begriffe der täglichen Nutzung:

| Stufe (Composite) | Was es für den Post-Editing-Weg bedeutet |
|---|---|
| **Baseline** (0,00–0,30) | Für nichts brauchbar. Die Ausgabe ist größtenteils nicht die Zielsprache. Nur als Forschungs-Untergrenze nützlich. |
| **Emerging** (0,30–0,50) | Noch kein Entwurfswerkzeug. Korrekte Fragmente treten auf, aber eine sprachkundige Person würde mehr Zeit mit Korrigieren als mit neuem Schreiben verbringen. |
| **Functional** (0,50–0,70) | Die erste Stufe, auf der Post-Editing die Übersetzung von Grund auf bei einfachen Texten übertreffen *könnte* — wert, mit einer sprachkundigen Person erprobt zu werden, aber nicht, sich darauf zu verlassen. Häufige morphologische Fehler bleiben bestehen. |
| **Deployable** (0,70–0,85) | Die Zielstufe für den obigen Workflow: Entwürfe, bei denen der Großteil der Morphologie korrekt ist und eine sprachkundige Person bedeutend schneller korrigieren als neu übersetzen kann. **„Deployable“ bedeutet einsatzfähig *für einen Post-Editing-Workflow* — niemals „ohne Durchsicht veröffentlichen“.** |
| **Fluent** (0,85–1,00) | Nähert sich kompetenter menschlicher Übersetzung; Fehler selten und geringfügig. Der Korrekturdurchlauf bleibt — er wird nur schneller. |

Zwei strukturelle Ehrlichkeitsregeln liegen über dieser Tabelle, direkt aus der [Benchmark Specification §5 und §7](/docs/specifications/benchmark#5-quality-tiers):

- **Automatisierte Stufen sind vorläufige Bezeichnungen, keine Urteile.** Sie sind Nominierungen für die menschliche Durchsicht. Die Schwellenwerte werden neu kalibriert, sobald sich Validierungsdaten von sprachkundigen Personen ansammeln, und sie können für verschiedene Sprachen unterschiedlich ausfallen.
- **Keine Methode kann Deployable oder höher beanspruchen ohne Community-Review.** Eine geschichtete Stichprobe ihrer Ausgaben geht an zweisprachige sprachkundige Personen, die jede Übersetzung mit *reject / gist / acceptable / excellent* bewerten. Die Governance-Organisation — nicht die Bestenliste — entscheidet, ob die Methode vorrückt.

Zum Vergleich beschreibt der Schwellenwert des [Founder's Prize](/docs/specifications/prizes) (Composite ≥ 0,80, ≥99 % morphologisch valide Wörter, ≥70 % von sprachkundigen Personen als acceptable-or-better bewertet) eine Methode, deren verbleibende Fehler *Fehler echter Sprache* sind — falsche Flexion, nicht erfundene Wörter. So sieht „ein Entwurf, der die Zeit einer sprachkundigen Person wert ist“ in Zahlen aus.

## Von einer siegreichen Methode zum funktionierenden Büro

Angenommen, eine Methode überwindet diese Hürden. Die verbleibenden Schritte sind organisatorischer Art und werden spezifiziert statt improvisiert:

1. **Eigentum wird übertragen.** Der Code der Methode wird Eigentum der Governance-Organisation der Gemeinschaft — die entwickelnde Person behält Namensnennungs- und Veröffentlichungsrechte ([Ownership Transfer](/docs/sovereignty/ownership-transfer)).
2. **Die Methode wird zum Dienst.** Sie wird als Plugin paketiert und über die Bereitstellungsplattform angeboten, wobei die Gemeinschaft Zugang, Preisgestaltung und zulässige Verwendungen kontrolliert ([Deploy to Production](/docs/getting-started/deploy-to-production)).
3. **Übersetzende binden sie in ihren Arbeitsalltag ein.** Ein Übersetzungsbüro richtet seinen bestehenden Dokumenten-Workflow auf die API der Methode aus: Quelltext hinein, Entwurf heraus, Post-Editing, Veröffentlichung. Der veröffentlichte Text trägt den Namen und die Autorität der übersetzenden Person — die Maschine ist ein Werkzeug auf ihrem Schreibtisch, wie ein Wörterbuch.
4. **Einnahmen folgen der Nutzung.** Externe Entwickelnde, die die Methode nutzen, zahlen nutzungsabhängige Tarife, und 90 % dieser Einnahmen fließen an die Governance-Organisation ([The Economic Model](/docs/sovereignty/economic-model)) — die damit weitere Übersetzungsstunden finanzieren kann und so die Schleife schließt.

## Wo dies heute steht

Klar gesagt: Der vollständige Weg ist von Anfang bis Ende spezifiziert und teilweise umgesetzt. Das Evaluierungs-Framework, die Metriken, die Run Cards und die öffentliche Bestenliste existieren; das Plains-Cree-Entwicklungskorpus und ein aktiver Preis existieren; die Bereitstellungsplattform existiert. Die Community-Review-Schnittstelle, die Evaluierungs-Sandbox und die Rückkopplungsschleife für korrigierte Texte sind spezifiziert, aber noch nicht betriebsbereit — die Spezifikationen kennzeichnen sie als geplant, und wir tun das ebenso. Noch hat keine Methode die gesamte Reise vom Benchmark zur täglichen gemeinschaftlichen Nutzung abgeschlossen. Diese Reise ist die Definition des Erfolgs für das Projekt, was genau der Grund ist, warum wir sie nicht vorzeitig beanspruchen.

---

## Was dies für Sie bedeutet

:::info Wenn Sie Mitglied einer Gemeinschaft sind
Ein „Deployable“-Abzeichen auf einer Bestenliste bedeutet niemals, dass eine Maschine unüberwacht in Ihrer Sprache veröffentlicht — es bedeutet, dass ein Entwurfsgenerator bereit sein könnte, bei Ihren Übersetzenden *vorzusprechen*, zu Ihren Bedingungen, mit Ihren sprachkundigen Personen als Beurteilende (bezahlten — siehe [How Speakers Get Paid](/docs/perspectives/how-speakers-get-paid)). Falls Ihre Gemeinschaft ein Übersetzungsbüro betreibt, lautet die relevante Frage an uns: „Wie würde ein Pilotprojekt aussehen, und wer prüft die Ausgaben?“
:::

:::info Wenn Sie forschend tätig sind
Die Post-Editing-Rahmung verändert, was zu messen lohnt: die Zeit bis zum akzeptablen Text mit einer sprachkundigen Person im Arbeitsablauf, nicht nur die Composite-Bewertung. Die Metriken der Arena sind Stellvertreter dafür ([Scoring Specification §1](/docs/specifications/scoring)), und sprachspezifische Post-Editing-Studien für morphologisch komplexe Sprachen sind eine offene Forschungslücke, die diese Infrastruktur zu unterstützen ausgelegt ist.
:::

:::info Wenn Sie entwickelnd tätig sind
Optimieren Sie für die korrigierende Person, nicht für die Metrik. Eine Methode, die echte Wörter mit gelegentlich falschen Flexionen erzeugt, ist von einer sprachkundigen Person in Sekunden korrigierbar; eine Methode, die plausibel aussehende Formen halluziniert, vergiftet den gesamten Workflow — weshalb morphologische Validität hier so streng als Hürde gesetzt ist. Beginnen Sie bei [Submit a Method](/docs/getting-started/submit-a-method), und lesen Sie das [Method Interface](/docs/specifications/methods) dazu, was Sie im Falle eines Siegs letztlich übergeben werden.
:::

## Siehe auch

- [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization) — warum die menschliche Hürde der Sinn der Sache ist, keine Einschränkung
- [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections) — was geschieht, wenn der veröffentlichte Text trotzdem falsch ist
- [Benchmark Specification §7](/docs/specifications/benchmark#7-human-validation) — die menschliche Validierungshürde, formell