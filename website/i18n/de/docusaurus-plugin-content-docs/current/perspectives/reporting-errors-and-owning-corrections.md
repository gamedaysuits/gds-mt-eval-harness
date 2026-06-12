---
sidebar_position: 4
title: "Fehler melden und Korrekturen verantworten"
slug: '/perspectives/reporting-errors-and-owning-corrections'
description: "Wie ein:e Sprecher:in einen falschen Sachverhalt oder eine schlechte Übersetzung meldet, wer über die weiteren Schritte entscheidet, wie Korrekturen ihre Herkunft (Provenance) mitführen und warum Communities ein Vetorecht über ihre Sprachdaten besitzen."
related:
  - label: "Data Sovereignty"
    to: /docs/sovereignty/data-sovereignty
    kind: doc
    note: "Who holds veto power over language data"
  - label: "Ownership Transfer"
    to: /docs/sovereignty/ownership-transfer
    kind: doc
  - label: "Speaker Validation Protocol"
    to: /docs/specifications/speaker-validation
    kind: spec
  - label: "How Speakers Get Paid"
    to: /docs/perspectives/how-speakers-get-paid
    kind: position
---
# Fehler melden und Korrekturen verantworten

> **Standpunkt.** Für eine Plattform, die Fakten und Bewertungen zu Tausenden von Sprachen veröffentlicht, ist es unvermeidlich, Fehler zu machen. Was *nicht* unvermeidlich ist, ist die Frage, wem geglaubt wird, wenn ein Fehler gemeldet wird, und wer die Korrektur verantwortet. Unsere Antwort: Die Meldung einer fließend sprechenden Person hat Vorrang vor unserer Automatisierung, jede Korrektur trägt eine Provenienz, die festhält, wer was und warum geändert hat, und eine Gemeinschaft kann die Nutzung ihrer Sprachdaten zurückziehen oder mit einem Veto belegen – nicht als Höflichkeit, sondern als durchgesetzte Eigenschaft der Architektur.

Die meisten Datenplattformen behandeln Fehlermeldungen wie Support-Tickets: Eine nutzende Person beschwert sich, eine betreuende Person entscheidet, der Datensatz ändert sich stillschweigend. Für Daten indigener Sprachen ist dieses Modell verkehrt herum. Die Person, die den Fehler meldet, ist in der Regel maßgeblicher als die Plattform – eine sprechende Person, die uns sagt, dass ein Wort falsch ist, ist keine „nutzende Person“, sondern die Grundwahrheit, die einen Stellvertreter korrigiert. Das nachfolgende Design ergibt sich daraus, dies ernst zu nehmen.

---

## Zwei Arten von Fehlern, ein Prinzip

Die Plattform veröffentlicht zwei Arten von Aussagen, die falsch sein können:

1. **Fakten über eine Sprache** – die Sprachkarten, die die Bewertung steuern: Klassifikationsdaten, Orthografie, linguistische Merkmale, welche Metriken zur Anwendung kommen. Eine Karte könnte die falsche Schätzung der Sprecherzahl, die falsche Dialektbeziehung oder den falschen Status des Schriftsystems angeben.
2. **Urteile über Übersetzungen** – eine Referenzübersetzung in einem Korpus, die eine sprechende Person für falsch oder unnatürlich hält; eine automatisierte Metrik, die ein gültiges Wort ablehnt oder ein ungültiges akzeptiert; ein „Deployable“-Abzeichen auf einer Ausgabe, die sprechende Personen nicht akzeptieren würden.

Das Prinzip, das beide abdeckt und bereits in der [Scoring-Spezifikation](/docs/specifications/scoring) und der [Benchmark-Spezifikation §7](/docs/specifications/benchmark#7-human-validation) verbindlich ist: **Automatisierte Ausgaben sind Stellvertreter; sprechende Personen sind die Grundwahrheit.** Die veröffentlichte Verpflichtung im [Speaker Validation Protocol §6](/docs/specifications/speaker-validation#6-what-speakers-get) bringt es unmissverständlich auf den Punkt: Wenn eine sprechende Person sagt, dass der Linter bei etwas falsch liegt, korrigieren wir den Linter.

## Wie eine Meldung ihren Weg nimmt

Hier ist der Weg, den eine Meldung nimmt, mit ehrlichen Statusmarkierungen – manches davon läuft bereits heute, anderes ist spezifiziert, aber noch nicht implementiert.

**Melden einer fehlerhaften Übersetzung oder eines Metrik-Urteils (läuft heute, über direkten Kanal).** Eine sprechende Person, die eine falsche Referenzübersetzung, ein fälschlich abgelehntes Wort oder ein inakzeptables „Äquivalent“ entdeckt, kann dies über den Issue-Tracker des öffentlichen Repositorys des Projekts melden oder indem sie das Projekt direkt kontaktiert. Die strukturierte Variante davon – Bewertungsbildschirme mit den Optionen *reject / gist / acceptable / excellent* und Freitextnotizen – ist die Schnittstelle für das Community-Review, die in der [Benchmark-Spezifikation §7.3](/docs/specifications/benchmark#7-human-validation) spezifiziert, aber noch nicht aktiv ist. Bis dahin werden Meldungen von Person zu Person bearbeitet, und die Validierungsaufgaben selbst (bezahltes, strukturiertes Speaker-Review – siehe [Wie sprechende Personen bezahlt werden](/docs/perspectives/how-speakers-get-paid)) bilden die Haupt-Korrekturpipeline.

**Melden eines falschen Fakts auf einer Sprachkarte (läuft heute, gleiche Kanäle).** Kartenkorrekturen folgen demselben Weg: Meldung, Überprüfung, versionierte Änderung. Da Karten das Bewertungsverhalten steuern – welche Metriken geladen werden, welche Modelle empfohlen werden –, kann eine Kartenkorrektur die Scores verändern, weshalb Korrekturen als protokollierte Datenänderungen angewendet werden, niemals als stillschweigende Bearbeitungen.

**Was als Nächstes geschieht – wer entscheidet:**

- **Linguistische Ermessensfragen gehören den sprechenden Personen dieser Sprache.** Ob eine Form gültig ist, ob zwei Formulierungen gleichwertig sind, ob ein Register angemessen ist – die Plattform setzt die Antwort um; sie liefert sie nicht. Wo sprechende Personen uneinig sind (Dialekte, orthografische Konventionen), wird die Antwort als Variation festgehalten, nicht von uns entschieden – die Korpus- und Linter-Schemata unterstützen die Auszeichnung dialektaler Varianten als akzeptable Alternativen, anstatt einen einzigen Sieger zu erzwingen.
- **Entscheidungen über die Daten einer Gemeinschaft gehören ihrer Governance-Organisation.** Bei Sprachen mit einer Governance-Organisation laufen Änderungen an Evaluierungskorpora, die Aufnahme von Korrekturen in versiegelte Testsätze und die Konsequenzen für das Deployment über sie – das ist das Control-Prinzip von [OCAP®](/docs/sovereignty/data-sovereignty), umgesetzt als Prozess, nicht als Plakat.
- **Mechanische Fehler werden einfach behoben.** Ein Tippfehler, ein defekter Link, ein falsch geparstes Feld – gemeldet, korrigiert, protokolliert. Nicht alles braucht einen Rat.

## Korrekturen tragen eine Provenienz

Eine Korrektur, die Sie nicht zurückverfolgen können, ist nur eine neuere Meinung. Drei Provenienzregeln gelten für jeden Fakt und jede Korrektur:

1. **Jeder Fakt nennt seine Quelle.** Sprachkarten und Korpuseinträge erfassen, woher jeder Wert stammt – ein veröffentlichter Datensatz, ein Beitrag aus der Gemeinschaft, das Review einer sprechenden Person.
2. **Abgeleitete Werte werden als unsere ausgewiesen, nicht als die der vorgelagerten Quelle.** Wenn die Plattform etwas berechnet – ein Aggregat, eine Umkodierung, einen Composite-Wert –, wird dies als Ableitung der Plattform *aus* der vorgelagerten Quelle erfasst, niemals unter dem Namen der vorgelagerten Quelle eingetragen. Ein vorgelagerter Datensatz sollte niemals für eine Zahl verantwortlich gemacht oder ihr zugeschrieben werden, die er nicht veröffentlicht hat.
3. **Korrekturen werden Teil des Datensatzes.** Die Korrektur einer sprechenden Person wird als neue, zugeschriebene Aussage erfasst (namentlich oder anonym, nach Wahl der sprechenden Person – zu denselben Bedingungen wie die Validierungsarbeit), die den alten Wert ersetzt; die Historie der Änderungen bleibt überprüfbar. Korpusversionen werden über Hash-Manifeste festgehalten ([Corpus Partnership §4.4](/docs/specifications/corpus-partnership)), sodass ein korrigiertes Korpus eine sichtbar neue Version ist, und jede Run-Card hält genau fest, gegen welche Version bewertet wurde – alte Scores bleiben interpretierbar, neue Scores spiegeln die Korrektur wider.

## Das Veto, konkret

„Kontrolle durch die Gemeinschaft“ lässt sich leicht behaupten. Hier ist, worauf es sich in der veröffentlichten Architektur konkret beläuft:

- **Sprechende Personen können ihre Beiträge zurückziehen.** Eine sprechende Person kann ihre Bewertungen jederzeit zurückziehen, und der Widerruf entfernt sie aus allen Analysen ([Speaker Validation §5](/docs/specifications/speaker-validation#5-data-governance)). Sprechende Personen besitzen außerdem ein Vetorecht gegen die Veröffentlichung von Ergebnissen, die sie als problematisch erachten.
- **Gemeinschaften können die Evaluierung vollständig stoppen.** Versiegelte Testsätze sind verschlüsselt, und die Schlüssel werden so verwahrt, dass die Plattform sie allein niemals rekonstruieren kann; eine Gemeinschaft kann den Zugang zur Evaluierung widerrufen, indem sie sich nicht an der Schlüsselrekonstruktion beteiligt ([Corpus Partnership §4.3](/docs/specifications/corpus-partnership#4-cryptographic-sealing-and-sandbox-testing)). „Was, wenn wir aufhören wollen?“ hat eine spezifizierte Antwort: Die versiegelten Daten werden niemals offengelegt, und die Evaluierung endet.
- **Kein Score setzt sich über eine Entscheidung der Gemeinschaft hinweg.** Eine Methode, die das Leaderboard anführt, wird nur dann eingesetzt, wenn die Governance-Organisation dies sagt ([Ownership Transfer](/docs/sovereignty/ownership-transfer)) – und eine Gemeinschaft, die entscheidet, dass MT für ihre Sprache überhaupt nicht eingesetzt werden soll, nutzt das System wie vorgesehen, anstatt es zu durchbrechen (siehe [Übersetzung ist keine Revitalisierung](/docs/perspectives/translation-is-not-revitalization)).

## Was wir noch nicht gebaut haben

Im Sinne des übrigen Inhalts dieses Regals: Die Schnittstelle für das Community-Review ist geplant, nicht aktiv. Für keine der aktuellen Sprachen sind bislang Governance-Organisationen etabliert – die Treuhänderschaft der Gemeinschaft für den Plains-Cree-Benchmark befindet sich in der Bestätigung, und wir nennen Treuhänder nicht öffentlich, bevor sie eingewilligt haben. Bis diese Bausteine existieren, laufen Korrekturen über direkte, zuschreibbare Kanäle, und die veröffentlichten Spezifikationen – nicht diese Seite – bleiben die verbindliche Beschreibung des Prozesses. Wo diese Seite und eine Spezifikation einander widersprechen, gewinnt die Spezifikation, und wir würden den Widerspruch ebenfalls als einen meldenswerten Fehler betrachten.

---

## Was das für Sie bedeutet

:::info Wenn Sie Mitglied einer Gemeinschaft sind
Wenn etwas an Ihrer Sprache auf dieser Plattform falsch ist – ein Fakt, eine Übersetzung, eine Bezeichnung –, ist Ihre Meldung ein Zeugnis aus der Grundwahrheit, keine zu sortierende Beschwerde. Sie entscheiden, ob Ihre Korrektur namentlich zugeschrieben wird; Ihr Beitrag kann später zurückgezogen werden; und Ihre Gemeinschaft kann die Nutzung ihrer Daten gänzlich unterbinden. Beginnen Sie bei [Für Sprachgemeinschaften](/docs/community/for-language-communities), oder öffnen Sie einfach ein Issue im öffentlichen Repository.
:::

:::info Wenn Sie forschend tätig sind
Korrekturen sind hier Daten mit Provenienz, keine stillschweigenden Bearbeitungen: Korpusversionen werden gehasht, Run-Cards verankern die genaue Version, gegen die bewertet wurde, und abgeleitete Werte werden als Ableitungen ausgewiesen. Wenn Sie auf Arena-Scores oder -Korpora aufbauen, zitieren Sie die Version – und behandeln Sie eine durch sprechende Personen ausgelöste Korrekturwelle als Befund über die Validität der Metrik, denn genau das ist sie.
:::

:::info Wenn Sie entwickeln
Der Score Ihrer Methode kann sich legitim ändern, ohne dass sich Ihr Code ändert – ein fälschlich abgelehntes Wort wird auf eine Allowlist gesetzt, eine Referenzübersetzung wird korrigiert, eine Variantenklasse wird behoben. Gestalten Sie dafür: Verankern Sie Korpusversionen in Ihren Run-Cards ([Run-Card-Spezifikation](/docs/specifications/run-card)), beobachten Sie die Changelogs der Datensätze und behandeln Sie Korrekturen durch sprechende Personen als das zuverlässigste Fehlersignal, das Sie je kostenlos erhalten werden.
:::

## Siehe auch

- [Wie sprechende Personen bezahlt werden](/docs/perspectives/how-speakers-get-paid) – dieselbe Autorität sprechender Personen, in der Benchmark-Phase
- [Vom Benchmark zum täglichen Gebrauch](/docs/perspectives/from-benchmark-to-daily-use) – wo Korrekturen auf den Publikationsworkflow treffen
- [Datensouveränität](/docs/sovereignty/data-sovereignty) – OCAP®, CARE und Te Mana Raraunga, die Prinzipien hinter diesem Design