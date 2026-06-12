---
sidebar_position: 2
title: "Was zählt hier als Sprache?"
---
# Was zählt hier als Sprache?

> **Zusammenfassung.** Die Arena katalogisiert Sprachen nach ISO 639-3, benchmarkt einzelne Sprachen (nicht Makrosprachen-Dachbegriffe), schließt Gebärdensprachen als die natürlichen Sprachen ein, die sie sind, berücksichtigt ISO-anerkannte Plansprachen, schließt Programmiersprachen aus und stellt Klassifikationsstreitigkeiten dar, ohne Partei zu ergreifen. Diese Seite erläutert jede dieser Entscheidungen und ihre Bedeutung für die Bestenliste.

Jedes Projekt, das Übersetzungen über Tausende von Sprachen hinweg benchmarkt, muss eine alte und überraschend schwierige Frage beantworten: Was zählt als Sprache? Linguisten wissen seit Langem, dass die Grenze zwischen „Sprache“ und „Dialekt“ ebenso sehr sozialer und politischer wie struktureller Natur ist – der berühmte Ausspruch, dass *„eine Sprache ein Dialekt mit einer Armee und einer Marine ist“*, wurde 1945 von dem jiddischen Linguisten Max Weinreich popularisiert (er schrieb ihn einem Zuhörer bei einem seiner Vorträge zu). Wir können der Frage nicht ausweichen, daher hier unsere Antworten und unsere Begründung.

---

## Gebärdensprachen sind Sprachen. Punkt.

Gebärdensprachen sind natürliche Sprachen – mit vollständigen Grammatiken, muttersprachlichem Erwerb durch Kinder und lebendigen Sprachgemeinschaften. Dies ist seit William Stokoes Nachweis von 1960, dass die Amerikanische Gebärdensprache dieselbe Art innerer Struktur wie gesprochene Sprachen aufweist, etablierte Linguistik, und sechzig Jahre Forschung seither (Klima & Bellugi 1979; Sandler & Lillo-Martin 2006) haben diesen Punkt nur weiter vertieft. ISO 639-3 weist Gebärdensprachen individuelle Sprachcodes zu; Glottolog katalogisiert sie neben den gesprochenen Sprachfamilien. Unser Katalog umfasst mehr als 160 von ihnen, gekennzeichnet als `modality: signed`.

Einige sind bedrohte indigene Sprachen: Plains Indian Sign Language (`psd`), historisch eine bedeutende interstammliche Lingua franca in ganz Nordamerika, ist heute vom Aussterben bedroht (Davis 2010, *Hand Talk*). Die Bedrohung von Gebärdensprachen *ist* die Bedrohung indigener Sprachen, und sie liegt innerhalb der Mission dieses Projekts.

**Eine ehrliche Anmerkung zum Geltungsbereich.** Die Arena benchmarkt derzeit *textbasierte* maschinelle Übersetzung. Maschinelle Übersetzung von Gebärdensprachen – die mit Video, räumlicher Grammatik und Sprachen arbeitet, die über keine weithin übernommene Schriftform verfügen – ist ein anderes und weitgehend ungelöstes technisches Problem (siehe Yin et al. 2021, „Including Signed Languages in Natural Language Processing“, ACL). Wir bedienen sie noch nicht. Die Einträge zu Gebärdensprachen in unserem Katalog sagen genau das aus: **noch nicht bedient – niemals „keine Sprache“.**

## Es gibt zwei Modalitäten. Schrift ist keine davon.

Sprachen treten in zwei primären Modalitäten auf: **gesprochen** und **gebärdet**. Schrift ist keine dritte Modalität – sie ist eine Technologie, die über einer Sprache liegt, und die meisten Sprachen der Welt kommen ohne eine standardisierte Schrift aus. Aus diesem Grund erfassen unsere Sprachkarten die Schrift gesondert (welche Schriftsysteme eine Sprache verwendet oder ob sie überhaupt keine standardisierte Orthographie besitzt) und erfassen sie ehrlich: Für eine textbasierte MT-Plattform ist die Frage, ob eine Sprache verschriftet ist, eine entscheidende Information und keine Fußnote – und eine unverschriftete Sprache ist keine geringere Sprache.

## Plansprachen: dabei. Programmiersprachen: außen vor.

Wir folgen der von ISO 639-3 selbst gezogenen Grenze. Der Standard lässt eine Plansprache nur dann zu, wenn sie eine vollständige Sprache ist, für die menschliche Kommunikation entworfen wurde, über eine Literatur verfügt und eine Gemeinschaft besitzt, die sie an eine zweite Generation von Sprechern weitergegeben hat – und er schließt Computer-Programmiersprachen ausdrücklich aus. Esperanto qualifiziert sich mit seinen Muttersprachlern; Python nicht, da niemand Python als Erstsprache von seinen Eltern erwirbt. Unser Katalog umfasst die zwei Dutzend von ISO anerkannten Plansprachen, als solche typisiert, und keine Programmiersprachen.

## Wir benchmarken einzelne Sprachen, keine Dachbegriffe

ISO 639-3 unterscheidet *einzelne Sprachen* von *Makrosprachen* – Dachcodes wie `cre` (Cree), `ara` (Arabisch) oder `zho` (Chinesisch), die mehrere eng verwandte Einzelsprachen umfassen. Die Benchmark-Einheit der Arena ist die **Einzelsprache**, aus einem operativen Grund: Übersetzungsressourcen sind varietätsspezifisch. Ein morphologischer Analysator, der für Plains Cree (`crk`) entwickelt wurde, generiert kein Moose Cree (`crm`); ein Korpus des ägyptischen Arabisch sagt wenig über die Qualität einer Methode im marokkanischen Arabisch aus. Ein an einen Dachcode geknüpfter Wert wäre eine Aussage über Varietäten, die nie tatsächlich evaluiert wurden – daher tun wir das nicht.

Makrosprachen erscheinen im Katalog dennoch als **Hub-Seiten**: eine Navigation, die eine Dach-Identität mit ihren einzelnen Mitgliedern verknüpft und damit die Beobachtung von ISO selbst widerspiegelt, dass beide Identitätsebenen real sind. Unterhalb der Einzelsprache zeigen wir Dialekt- und Abstammungsinformationen aus Glottologs Languoid-Baum (Hammarström & Forkel 2022), der Familien, Sprachen und Dialekte als eine navigierbare Hierarchie modelliert.

## Wenn die Instanzen uneins sind, zeigen wir beides

ISO 639-3 und Glottolog teilen oder bündeln gelegentlich unterschiedlich, und Gemeinschaften sind mitunter mit beiden uneins. Wir entscheiden nicht. Sprachkarten bieten eine Funktion für *Klassifikationshinweise*, die die Uneinigkeit mit Quellen darstellt, und die Benennung folgt der Gemeinschaft, wo immer die Gemeinschaft eine Präferenz geäußert hat. Ob eine Varietät „eine Sprache“ ist, ist letztlich teils eine Frage der Identität – und Identitätsfragen gehören den Gemeinschaften selbst, ein Grundsatz, den wir aus indigenen Daten-Governance-Rahmenwerken wie OCAP® übernehmen.

## Eine Forschungsrichtung: Benchmarks als Messinstrument

Eine Sache, die eine Arena wie diese fast als Nebenprodukt hervorbringt, ist eine neue Art von Evidenz darüber, wie nah sich Sprachvarietäten *operativ* tatsächlich sind. Wenn eine einzige, festgehaltene Übersetzungsmethode mehrere verwandte Varietäten in einsatzfähiger Qualität bedient, gruppieren sich diese Varietäten in der Praxis; wenn sie getrennte Korpora und getrennte Methoden erfordern, sind sie operativ unterschiedlich – ungeachtet dessen, was die Benennungspolitik besagt. Dies ähnelt älteren empirischen Traditionen, von der Verständlichkeitsprüfung anhand aufgezeichneter Texte bis hin zu automatisierten lexikalischen Distanzmessungen, mit einer einsatzbezogenen Wendung.

Wir bieten dies mit Bedacht an, als Forschungsrichtung und nicht als Behauptung. Ergebnisse zur Methodenübertragung werden durch Korpusgröße, Domäne, Orthographie und Kontamination der Trainingsdaten verfälscht, und eine Gruppierung ist stets relativ zu einer Methode und einem Qualitätsschwellenwert. Vor allem: Dieses Signal kann Gespräche über Sprache und Dialekt *informieren*, aber es setzt sich niemals darüber hinweg, wie eine Gemeinschaft ihre eigene Sprache identifiziert.

---

## Literaturverzeichnis

- Davis, Jeffrey E. (2010). *Hand Talk: Sign Language among American Indian Nations.* Cambridge University Press.
- Dryer, Matthew S. & Martin Haspelmath, eds. (2013). *The World Atlas of Language Structures Online.* https://wals.info
- Hammarström, Harald & Robert Forkel (2022). „Glottocodes: Identifiers Linking Families, Languages and Dialects to Comprehensive Reference Information.“ *Semantic Web* 13(6).
- Haugen, Einar (1966). „Dialect, Language, Nation.“ *American Anthropologist* 68(4).
- ISO 639-3 Registration Authority. „Scope of denotation“ und „Types of individual languages.“ https://iso639-3.sil.org/about/scope · https://iso639-3.sil.org/about/types
- Klima, Edward S. & Ursula Bellugi (1979). *The Signs of Language.* Harvard University Press.
- Sandler, Wendy & Diane Lillo-Martin (2006). *Sign Language and Linguistic Universals.* Cambridge University Press.
- Stokoe, William C. (1960). *Sign Language Structure.* Studies in Linguistics, Occasional Papers 8.
- Weinreich, Max (1945). „Der YIVO un di problemen fun undzer tsayt.“ *YIVO Bleter* 25(1).
- Yin, Kayo, Amit Moryossef, Julie Hochgesang, Yoav Goldberg & Malihe Alikhani (2021). „Including Signed Languages in Natural Language Processing.“ *Proc. ACL-IJCNLP 2021.* https://aclanthology.org/2021.acl-long.570/
- First Nations Information Governance Centre. *The First Nations Principles of OCAP®.* https://fnigc.ca/ocap-training/