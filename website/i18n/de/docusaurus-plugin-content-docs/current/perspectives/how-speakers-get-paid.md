---
sidebar_position: 2
title: "Wie Sprecher:innen bezahlt werden"
slug: '/perspectives/how-speakers-get-paid'
description: "Wofür Community-Validator:innen und Übersetzer:innen für Benchmark-Arbeit bezahlt werden, warum die Bezahlung von Sprecher:innen nicht verhandelbar ist und wie die Vergütung mit dem Wachstum der Arena skaliert. Alle Zahlen stammen aus den veröffentlichten Spezifikationen."
related:
  - label: "Speaker Validation Protocol"
    to: /docs/specifications/speaker-validation
    kind: spec
    note: "The work validators are paid for"
  - label: "Prize Specification"
    to: /docs/specifications/prizes
    kind: spec
    note: "Where prize money goes, and why"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
---
# Wie Sprecher bezahlt werden

> **Transparenzhinweis.** Jede Zahl auf dieser Seite erscheint bereits in einer veröffentlichten Spezifikation — der [Benchmark Specification §10](/docs/specifications/benchmark#10-cost-framework), dem [Speaker Validation Protocol](/docs/specifications/speaker-validation) und der [Prize Specification](/docs/specifications/prizes). Diese Seite fasst sie an einem Ort in verständlicher Sprache zusammen, damit niemand eine Spezifikation lesen muss, um herauszufinden, was die Zeit eines Sprechers hier wert ist. Sie geht keine Verpflichtungen ein, die über das hinausgehen, was diese Dokumente bereits festhalten.

Ein zweisprachiger Sprecher, der beurteilen kann, ob ein maschinell erzeugter Satz echt und flüssig ist und die richtige Bedeutung trägt, ist der seltenste und wertvollste Teilnehmer in diesem gesamten System. Alles andere — Harnesses, Metriken, Bestenlisten — existiert, um eine geringe Menge der Zeit dieser Person weit reichen zu lassen.

Die erste Regel ist daher einfach: **Sprecher werden für ihre Zeit zu professionellen Honorarsätzen bezahlt, unabhängig davon, was die Ergebnisse zeigen.**

---

## Warum die Bezahlung von Sprechern nicht verhandelbar ist

Die Sprachtechnologieforschung hat eine lange Gewohnheit, fließende Sprecher als kostenlose Ressource zu behandeln — als „Community-Engagement“, das Datensätze, Veröffentlichungen und Karrieren für alle außer den Sprechern hervorbringt. Wir betrachten dieses Muster als ausbeuterisch, und die Menschen, die am qualifiziertesten für diese Arbeit sind, sind genau jene, deren Zeit bereits durch die dringende Arbeit des Unterrichtens, Übersetzens und der Kindererziehung in der Sprache beansprucht wird.

Daraus ergeben sich drei gestalterische Konsequenzen:

1. **Keine Freiwilligen-Pipeline.** Wir bitten Sprecher nicht darum, Evaluierungsarbeit als Gefallen für die Forschung zu spenden. Die Teilnahme ist ein bezahltes Engagement, und ihre Ablehnung kostet einen Sprecher nichts.
2. **Die Bezahlung ist bedingungslos.** Sprecher werden bezahlt, unabhängig davon, ob ihre Bewertungen verwendet werden, und die Bezahlung ist nicht von den Ergebnissen abhängig. Das veröffentlichte Protokoll verpflichtet sich zur Bezahlung innerhalb von zwei Wochen nach Abschluss jedes Aufgabenblocks.
3. **Die Vergütung ist nicht die ganze Vereinbarung.** Sprecher, die Bewertungen beitragen, erhalten außerdem eine Nennung (namentlich oder anonym, nach ihrer Wahl), eine optionale Mitautorschaft an Veröffentlichungen, die ihre Bewertungen verwenden, das Recht, ihre Beiträge jederzeit zurückzuziehen, sowie ein Vetorecht gegen die Veröffentlichung von Ergebnissen, die sie als problematisch empfinden. Diese Bedingungen stehen im [Speaker Validation Protocol §5–6](/docs/specifications/speaker-validation), nicht in einem Nebenschreiben.

## Die veröffentlichten Honorarsätze

Das Kostenrahmenwerk des Benchmarks legt die Vergütung für zweisprachige Sprecher auf **50–65 CAD pro Stunde** für Korpus- und Validierungsarbeit fest. Was das je Rolle bedeutet:

### Aufbau eines Benchmark-Korpus

Die Erstellung der Referenzübersetzungen, an denen jede Methode gemessen wird, ist die grundlegende Sprecheraufgabe. Das veröffentlichte Einrichtungsbudget je Sprache:

| Arbeit | Veröffentlichte Spanne | Grundlage |
|------|-----------------|-------|
| Korpuskuration (50–150 Einträge) | $2.500–6.000 | $50–65/Std., zweisprachige Sprecherzeit |
| Überprüfung von Methodenausgaben | $500–1.500 | Gleiche Stundensätze |

Ein vollständiges Korpus erfordert von einem Sprecher traditionell etwa 80 Stunden; der geplante agentengestützte Arbeitsablauf (Satzentwurf und Formatierung durch Werkzeuge übernommen, Übersetzung stets durch einen Menschen) ist darauf ausgelegt, dies in Richtung 30–40 Stunden zu bringen — weniger Stunden repetitiver Arbeit, gleicher Stundensatz, wobei der Sprecher nur jene Teile übernimmt, die tatsächlich einen Menschen erfordern.

### Validierung der Metriken

Bevor automatisierte Bewertungen irgendeine Bedeutung haben, müssen Sprecher sie anhand des menschlichen Urteils überprüfen. Das [Speaker Validation Protocol](/docs/specifications/speaker-validation) veröffentlicht die genauen Aufgaben, Stunden und Bezahlung:

| Aufgabe | Zeit | Bezahlung je Sprecher |
|------|------|-----------------|
| A — Bewertung von 200 maschinellen Übersetzungen hinsichtlich Adäquatheit und Flüssigkeit | ~8 Stunden | $400–520 CAD |
| B — Überprüfung von 50 „äquivalenten“ Übersetzungspaaren | ~2 Stunden | $100–130 CAD |
| C — Überprüfung von 100 Wörtern, die der morphologische Analysator abgelehnt hat | ~1,5 Stunden | $75–100 CAD |

Ein Sprecher, der alle drei Aufgaben übernimmt, verpflichtet sich über zwei bis vier Wochen zu etwa 11,5 Stunden für **575–750 CAD**. Die vollständige Validierungsrunde mit drei Sprechern kostet das Projekt $1.475–1.920 — was genau der Punkt ist: Die Sprechervalidierung ist ein kleiner Posten für das Projekt und sollte niemals die Stelle sein, an der Kosten „eingespart“ werden.

### Überprüfung von Preisansprüchen

Kein Preis wird allein auf Grundlage automatisierter Bewertungen ausgezahlt. Der [Founder's Prize](/docs/specifications/prizes) (10.000 CAD, English→Plains Cree) verlangt, dass mindestens zwei zweisprachige Sprecher unabhängig voneinander eine stratifizierte Stichprobe von mindestens 30 Ausgaben überprüfen und dass 70 % oder mehr als „akzeptabel“ oder „exzellent“ bewertet werden. Diese Überprüfung ist bezahlte Sprecherarbeit zu denselben Sätzen — und sie ist zugleich ein Tor: Sprecher können einen Preisanspruch zu Fall bringen, und das ist beabsichtigt.

## Wie es mit Wettbewerben skaliert

Das Modell ist so aufgebaut, dass die Sprechervergütung mit der Plattform wächst, anstatt durch sie verwässert zu werden:

- **Jede neue Sprache beginnt mit einem bezahlten Korpus-Engagement.** Die veröffentlichten Einrichtungskosten je Sprache ($3.350–8.500 insgesamt) bestehen größtenteils aus der Sprechervergütung — bewusst der größte Einzelbestandteil.
- **Jeder neue Preispool bringt seine eigene bezahlte Überprüfung mit sich.** Jeder gesponserte Wettbewerb, der der [Preisvorlage](/docs/specifications/prizes#4-future-prize-pools) folgt, trägt dieselbe Anforderung der Community-Validierung, was bedeutet, dass jeder Wettbewerb Sprecherüberprüfungsarbeit für diese Sprache finanziert.
- **Eingesetzte Methoden finanzieren fortlaufende Überprüfung.** Wenn eine im Besitz der Community befindliche Methode API-Einnahmen erzielt, fließen 90 % an die Governance-Organisation der Community ([das Wirtschaftsmodell](/docs/sovereignty/economic-model)), die nach eigenem Ermessen fortlaufende Überprüfung, Korpuswachstum und Sprachprogramme finanzieren kann. Diese Zuweisung ist die Entscheidung der Community, nicht unsere.

## Was wir *nicht* versprochen haben

Ehrlichkeit erfordert, die Grenzen zu markieren:

- Die obigen Sätze sind die veröffentlichten Sätze für die aktuelle Plains-Cree-Arbeit. Sätze für künftige Sprachen werden gemeinsam mit der Partner-Community festgelegt und auf dieselbe Weise veröffentlicht — in den Spezifikationen, bevor die Arbeit beginnt.
- Das Schwungrad (Einnahmen → Community → mehr bezahlte Arbeit) erfordert externe Finanzierung zum Anlaufen und ist noch nicht selbsttragend. Das [Wirtschaftsmodell](/docs/sovereignty/economic-model) beschreibt den Mechanismus, keine Garantie.
- „Fair bezahlt“ ist notwendig, aber nicht hinreichend. Die Bezahlung allein macht ein Projekt noch nicht nicht-ausbeuterisch — Eigentum und Kontrolle tun das, weshalb die Vergütung innerhalb der [Souveränitätsarchitektur](/docs/sovereignty/data-sovereignty) angesiedelt ist, anstatt sie zu ersetzen.

---

## Was das für Sie bedeutet

:::info Wenn Sie Mitglied einer Community sind
Wenn Sie zweisprachig in einer unterversorgten Sprache und Englisch sind, ist Ihr Urteil der wertvollste Beitrag in diesem System, und die veröffentlichten Bedingungen lauten: 50–65 CAD/Stunde, flexible Zeiteinteilung, Bezahlung innerhalb von zwei Wochen, Nennung zu Ihren Bedingungen sowie das Recht, Ihre Beiträge zurückzuziehen. Es sind keine Programmierkenntnisse erforderlich. Beginnen Sie mit [For Language Communities](/docs/community/for-language-communities) oder dem [Speaker Validation Protocol §7](/docs/specifications/speaker-validation#7-how-to-get-started).
:::

:::info Wenn Sie Forscher sind
Budgetieren Sie die Sprechervergütung als erstrangigen Forschungskostenpunkt — die veröffentlichten Zahlen ($1.475–1.920 für eine Metrikvalidierungsrunde; $2.500–6.000 für die Korpuskuration) sind nach Maßstäben von Fördermitteln gering und sie sind das, was automatisierte Bewertungen vertretbar macht. Die [Corpus Partnership Strategy](/docs/specifications/corpus-partnership) zeigt, wie sich ein akademischer Fachbereich mit eingeplanter, finanzierter Sprecherarbeit einklinkt.
:::

:::info Wenn Sie Entwickler sind
Sie profitieren von bezahlter Sprecherarbeit, selbst wenn Sie sie nie finanzieren: Validierte Metriken machen Ihre Bestenlisten-Bewertung aussagekräftig, und bezahlte Community-Überprüfung steht zwischen Ihrer Methode und einem Preis. Wenn Sie gewinnen, sollten Sie damit rechnen, dass Sprecher dafür bezahlt wurden, Ihre Ausgaben zu prüfen — und damit, dass das [Eigentum an Ihrer Methode übertragen wird](/docs/sovereignty/ownership-transfer) an die Community, deren Sprache sie dient.
:::

## Siehe auch

- [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization) — warum die Autorität der Sprecher alles andere rahmt
- [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections) — die Autorität der Sprecher auch nach dem Benchmark
- [Benchmark Specification §10](/docs/specifications/benchmark#10-cost-framework) — das vollständige Kostenrahmenwerk, aus dem diese Zahlen stammen