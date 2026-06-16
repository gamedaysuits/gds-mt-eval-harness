---
sidebar_position: 1
title: "Übersetzung ist keine Revitalisierung"
slug: '/perspectives/translation-is-not-revitalization'
description: "Was maschinelle Übersetzung für bedrohte Sprachen leisten kann und was nicht – klar und deutlich formuliert. MT ist Infrastruktur für Sprachgemeinschaften. Sie ersetzt niemals Menschen, die mit Menschen sprechen."
related:
  - label: "How Speakers Get Paid"
    to: /docs/perspectives/how-speakers-get-paid
    kind: position
  - label: "From Benchmark to Daily Use"
    to: /docs/perspectives/from-benchmark-to-daily-use
    kind: position
    note: "The post-editing path from draft to published text"
  - label: "Data Sovereignty"
    to: /docs/sovereignty/data-sovereignty
    kind: doc
    note: "OCAP, CARE, and consent before deployment"
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
---
# Übersetzung ist keine Revitalisierung

> **Standpunkt.** Maschinelle Übersetzung konvertiert Text zwischen Sprachen. Revitalisierung schafft neue Sprecher. Dies sind unterschiedliche Tätigkeiten mit unterschiedlichen Erfolgskriterien, und kein Leaderboard-Wert ändert daran etwas. Wir entwickeln MT als Infrastruktur, die den Zielen einer Gemeinschaft dient — niemals als Ersatz für die generationenübergreifende Weitergabe. Kinder lernen Sprache von Menschen, nicht von Maschinen.

Im Jahr 2026 ist es leicht zu glauben, dass Software alles beheben kann, einschließlich einer Sprache, die ihre Sprecher verliert. Wir möchten präzise darlegen, warum dieser Glaube falsch ist — und was Übersetzungstechnologie ehrlicherweise *beitragen* kann.

Dieser Text existiert, weil eine Linguistin, die wir eingeladen hatten, dieses Projekt zu kritisieren, das Argument nachdrücklich vorbrachte: Ein perfektes Englisch→Cree-Übersetzungssystem würde weder das Weitergabeproblem (Kinder, die die Sprache zu Hause nicht lernen) noch das Prestigeproblem (Englisch als Sprache der wirtschaftlichen Macht) noch das pädagogische Problem (zu wenige Immersionsschulen und ausgebildete Lehrkräfte) lösen. Es könnte die Dinge sogar verschlimmern, indem es die Illusion erzeugt, dass „der Computer Cree sprechen kann“ und die Dringlichkeit der menschlichen Weitergabe abschwächt. Wir haben den Großteil dieser Kritik akzeptiert, und wir veröffentlichen unsere Antwort hier, statt sie zu verschweigen.

---

## Was Revitalisierung tatsächlich erfordert

Die Forschungsliteratur zur Sprachrevitalisierung ist in einem Punkt einheitlich: Sprachen überleben, wenn sie zwischen den Generationen weitergegeben werden — wenn Eltern, Großeltern und Gemeinschaften sie zu Kindern sprechen und Kinder damit aufwachsen, sie zurückzusprechen (Fishman 1991; Hinton & Hale 2001). Alles andere — Schulen, Medien, Wörterbücher, Apps — unterstützt diese Weitergabe, oder es unterstützt nichts.

Kein Übersetzungssystem nimmt an diesem Austausch teil. Ein Modell, das ein englisches Dokument in Plains Cree konvertiert, schafft keinen Sprecher. Es besetzt kein Immersionsklassenzimmer, bildet keine Lehrkraft aus und sitzt mit keinem Kind am Küchentisch. Sollte unsere Arbeit jemals als „Sprachen retten“ beschrieben werden, ist diese Beschreibung falsch, und wir werden das auch sagen.

## Was MT nicht leisten kann

Klar formuliert, damit später keine Mehrdeutigkeit besteht:

- **Sie kann Sprecher nicht ersetzen.** Eine Ausgabe, die kein fließend sprechender Mensch überprüft hat, ist ein Entwurf, kein Text. Unsere eigenen [Bewertungsregeln](/docs/specifications/scoring) behandeln jeden automatisierten Wert als Stellvertreter; nur die menschliche Überprüfung bestätigt die Verwendbarkeit.
- **Sie kann keine Erstsprache vermitteln.** Kinder erwerben Sprache durch Beziehung und Immersion, nicht durch übersetzte Dokumente.
- **Sie kann eine schädliche Illusion erzeugen.** Eine Demo, die eine Sprache „spricht“, kann nahelegen, die Sprache sei sicher, obwohl sie es nicht ist. Dieses Prestigerisiko ist real, und wir behandeln es als offene Frage, die *mit* den Gemeinschaften zu untersuchen ist, und nicht als Sprechpunkt, der zu verwalten ist.
- **Sie kann nichts entscheiden.** Ob ein Übersetzungssystem für eine Sprache existieren soll und wo es verwendet werden darf, ist die Entscheidung der Gemeinschaft — einschließlich der Entscheidung, es überhaupt nicht einzusetzen. Diese Kontrolle ist in die Architektur des [Eigentumsübergangs](/docs/sovereignty/ownership-transfer) und der [Datensouveränität](/docs/sovereignty/data-sovereignty) eingebaut, und sie umfasst auch Kontexte: Eine Gemeinschaft könnte MT für offizielle Dokumente akzeptieren und sie für Unterrichtsmaterialien ablehnen.

## Was MT ehrlicherweise leisten kann

Vor diesem Hintergrund gibt es konkrete, begrenzte Dinge, die Übersetzungsinfrastruktur beiträgt — wobei jedes davon Menschen dient, die bereits die eigentliche Arbeit leisten.

**1. Durchsatz für überlastete Übersetzer.** Übersetzungsbüros von Gemeinschaften sehen sich mit mehr Dokumenten konfrontiert, die in der Sprache *existieren sollten*, als menschliche Übersetzer von Grund auf erstellen können. Ein maschineller Entwurf verändert die Aufgabe von „alles übersetzen“ zu „überprüfen und korrigieren“ — und kontrollierte Studien haben festgestellt, dass das Post-Editing erheblich schneller ist als das Übersetzen von Grund auf, bei gleichbleibender oder verbesserter Qualität (Plitt & Masselot 2010; Green, Heer & Manning 2013). Wir beschreiben diesen Arbeitsablauf ausführlich in [Vom Benchmark zur täglichen Nutzung](/docs/perspectives/from-benchmark-to-daily-use). Die Einschränkung: Diese Studien deckten ressourcenreiche Sprachpaare ab; für polysynthetische Sprachen liegen uns noch keine gleichwertigen Belege vor, was Teil dessen ist, was dieses Projekt zu messen eingerichtet ist.

**2. Praktischer Hebel für Sprachenrechte.** Das Recht auf staatliche Dienstleistungen in indigenen Sprachen ist in mehreren Jurisdiktionen gesetzlich verankert. Was häufig fehlt, ist die praktische Kapazität, Übersetzungen in der Geschwindigkeit zu erstellen, die die Bürokratie verlangt. Eine Gemeinschaft, die ein fünfzigseitiges Grundsatzdokument innerhalb von Tagen statt Monaten in eine überprüfte Übersetzung verwandeln kann, befindet sich in einer stärkeren Verhandlungsposition. Die Technologie schafft das Recht nicht; sie macht es schwieriger, das Recht zu ignorieren.

**3. Wiederverwendbare linguistische Infrastruktur.** Der morphologische Analysator (FST), den wir verwenden, um zu überprüfen, dass die Übersetzungsausgabe echte Wörter enthält — und keine halluzinierten — kodiert, *warum* jede Wortform gültig ist. Dieselbe Maschinerie ist die Grundlage für Lernwerkzeuge: Konjugationstrainer, fehlerkorrigierende Schreibhilfen, morphologische Explorer. Die Verifikationsmaschine und die pädagogische Maschine sind dasselbe Artefakt. Dies ist ein Weg, kein Versprechen — die Lernwerkzeuge müssen erst gebaut werden, und ob sie gebaut werden, ist eine Entscheidung der Gemeinschaft.

**4. Unterstützung für Zweitsprachenlernende.** Revitalisierung besteht nicht nur darin, dass Kinder eine Erstsprache erwerben. Sie umfasst auch Erwachsene, die als Zweitsprache lernen — Menschen, die möglicherweise nie das Niveau der Sprachgewandtheit von Ältesten erreichen, die aber Gemeinschaftsdokumente lesen, mit Verständnis teilnehmen und die öffentliche Präsenz der Sprache durch ihre Nutzung erhöhen können. Für diese Bevölkerungsgruppe ist eine Übersetzungshilfe ein echtes Werkzeug, so wie ein Wörterbuch ein Werkzeug ist.

**5. Ein Grund, warum die Arbeit vor Ort finanziert und besessen werden soll.** In unserem Modell [gehen erprobte Methoden in das Eigentum der Gemeinschaft über](/docs/sovereignty/ownership-transfer), und die API-Einnahmen fließen ganz überwiegend an die Gemeinschaft ([das Wirtschaftsmodell](/docs/sovereignty/economic-model)). Sprecher werden [für ihr Fachwissen bezahlt](/docs/perspectives/how-speakers-get-paid), nicht gebeten, es ehrenamtlich zur Verfügung zu stellen. Nichts davon ist ebenfalls Revitalisierung — aber es lenkt Ressourcen zu den Menschen, die Revitalisierung betreiben, statt von ihnen weg.

## Die ehrliche Rahmung

Das Fachgebiet hat eine lange Bilanz von Technologieprojekten, die mit Rettungserzählungen ankommen und mit Publikationen wieder abreisen (Bird 2020). Wir versuchen, eine engere Behauptung aufrechtzuerhalten: **MT ist Infrastruktur.** Infrastruktur dient Zielen, die andere Menschen festlegen. Straßen entscheiden nicht, wohin Sie reisen; diese Technologie entscheidet nicht, ob eine Sprache lebt. Sprecher, Familien und Gemeinschaften tun das — und die Rahmung der [UNESCO-Internationalen Dekade der indigenen Sprachen](https://idil2022-2032.org/) hat recht damit, indigene Völker und nicht Werkzeuge in den Mittelpunkt zu stellen.

Wenn eine Gemeinschaft zu dem Schluss kommt, dass Übersetzungstechnologie ihren Zielen hilft, möchten wir, dass es die beste, am besten rechenschaftspflichtige Version ist, die möglich ist — in ihrem Eigentum, validiert durch ihre Sprecher, eingesetzt zu ihren Bedingungen. Wenn eine Gemeinschaft zu dem Schluss kommt, dass sie nicht hilft, ist dieser Schluss ein gültiges Ergebnis dieses Projekts und kein Scheitern davon. Beide Hälften dieses Satzes sind Verpflichtungen.

---

## Was das für Sie bedeutet

:::info Wenn Sie ein Mitglied einer Gemeinschaft sind
Dieses Projekt wird Ihnen nicht sagen, dass eine App Ihre Sprache retten kann — sie kann es nicht. Was es bietet, ist begrenzt: schnellere Dokumentenübersetzung unter Überprüfung durch fließend sprechende Personen, Infrastruktur, die Ihre Gemeinschaft vollständig besitzen kann, und Vergütung für das Fachwissen der Sprecher. Ob und wie irgendetwas davon genutzt wird, ist die Entscheidung Ihrer Gemeinschaft, einschließlich der Entscheidung, es nicht zu nutzen. Siehe [Für Sprachgemeinschaften](/docs/community/for-language-communities) und [Fehler melden und Korrekturen besitzen](/docs/perspectives/reporting-errors-and-owning-corrections).
:::

:::info Wenn Sie ein Forschender sind
Behandeln Sie „MT für gefährdete Sprachen“ als Infrastrukturbehauptung, nicht als Revitalisierungsbehauptung, und Ihre Bewertungsfrage ändert sich: nicht „ist der BLEU-Wert hoch?“, sondern „reduziert dies messbar die Arbeitsbelastung der Menschen, die die eigentliche Arbeit leisten, zu ihren Bedingungen?“ Die [Benchmark-Spezifikation](/docs/specifications/benchmark) und [Wie es funktioniert §8 (Spannungen und Einschränkungen)](/docs/how-it-works#8-tensions-and-limitations) sind die Orte, an denen wir uns an diesem Maßstab messen lassen.
:::

:::info Wenn Sie ein Entwickler sind
Bauen Sie für den Post-Editing-Arbeitsablauf, nicht für die Demo. Der Nutzer Ihrer Methode ist eine fließend sprechende Person, die einen Entwurf korrigiert, und der schlimmste Fehlerfall sind halluzinierte Wörter, die für Nicht-Sprecher plausibel aussehen — weshalb die morphologische Validierung hier alles absichert. Beginnen Sie mit [Eine Methode einreichen](/docs/getting-started/submit-a-method) und [Vom Benchmark zur täglichen Nutzung](/docs/perspectives/from-benchmark-to-daily-use).
:::

---

## Quellen

- Fishman, J. A. (1991). *Reversing Language Shift: Theoretical and Empirical Foundations of Assistance to Threatened Languages.* Multilingual Matters.
- Hinton, L., & Hale, K. (eds.) (2001). *The Green Book of Language Revitalization in Practice.* Academic Press.
- Plitt, M., & Masselot, F. (2010). "A Productivity Test of Statistical Machine Translation Post-Editing in a Typical Localisation Context." *The Prague Bulletin of Mathematical Linguistics*, 93, 7–16. [PDF](https://ufal.mff.cuni.cz/pbml/93/art-plitt-masselot.pdf)
- Green, S., Heer, J., & Manning, C. D. (2013). "The Efficacy of Human Post-Editing for Language Translation." *Proceedings of CHI 2013.* [Paper](https://idl.uw.edu/papers/post-editing)
- Bird, S. (2020). "Decolonising Speech and Language Technology." *Proceedings of COLING 2020*, 3504–3519. [Paper](https://aclanthology.org/2020.coling-main.42/)
- UNESCO. *International Decade of Indigenous Languages 2022–2032.* [idil2022-2032.org](https://idil2022-2032.org/)

## Siehe auch

- [Wie Sprecher bezahlt werden](/docs/perspectives/how-speakers-get-paid) — das Vergütungsmodell, in Zahlen
- [Vom Benchmark zur täglichen Nutzung](/docs/perspectives/from-benchmark-to-daily-use) — der Post-Editing-Pfad
- [Wie es funktioniert](/docs/how-it-works) — die vollständige Plattformarchitektur, einschließlich §8 zu Spannungen, die wir nicht gelöst haben