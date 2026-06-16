---
sidebar_position: 1
title: "Von Pāṇini zu Transformers"
---
# Von Pāṇini zu Transformers: Sprache, Berechnung und die unvollendete Arbeit der Übersetzung

**Eine Geschichte der Ideen hinter champollion**

---

> *„Wenn ich einen Artikel auf Russisch betrachte, sage ich mir: ‚Dies ist eigentlich auf Englisch geschrieben, wurde jedoch in einigen seltsamen Symbolen kodiert. Ich werde nun fortfahren, es zu dekodieren.‘"*
> — Warren Weaver, 1949

---

## Einleitung

Der Traum von einer Maschine, die zwischen menschlichen Sprachen übersetzen könnte, ist älter als der Computer selbst. Es ist in gewissem Sinne *das* ursprüngliche Problem der künstlichen Intelligenz – älter als schachspielende Programme, älter als Expertensysteme, älter als neuronale Netze. Dieser Wunsch wird häufig durch europäische Gleichnisse wie den Turmbau zu Babel gerahmt, der sprachliche Vielfalt als Strafe oder als zu lösendes Problem darstellt und dabei die Realität übergeht, dass indigene Gesellschaften vor dem Kontakt seit langem eine erstaunliche sprachliche Vielfalt durch ausgefeilte Handelssprachen (wie das Chinook Jargon) und Zeichensysteme (wie die Plains Indian Sign Language) bewältigt haben, ohne eine universelle Homogenisierung anzustreben.

Doch die Geschichte, die zu diesem Moment führt – zu einer Welt, in der große Sprachmodelle ein passables Französisch übersetzen, aber Unsinn auf Cree halluzinieren –, verläuft nicht geradlinig. Sie ist ein Geflecht aus mindestens vier verschiedenen Strängen: der formalen Erforschung der Sprache, der mathematischen Theorie der Berechnung, der statistischen Revolution im maschinellen Lernen und einer dunkleren Geschichte, die erklärt, *warum* die Sprachen, die Technologie am dringendsten benötigen, gerade jene Sprachen sind, für die es sie nicht gibt. Dieser vierte Strang ist die Geschichte der kolonialen Sprachunterdrückung und des kulturellen Völkermords – der gezielten, systematischen Zerstörung indigener Sprachen auf jedem Kontinent, auf dem europäische Mächte ihre Herrschaft errichteten. Ohne ein Verständnis dieser Geschichte erscheint das technische Problem wie ein Zufall der Datenknappheit. Es ist kein Zufall.

Dieser Beitrag verfolgt alle vier Stränge von ihren Ursprüngen bis zu ihrer Konvergenz in der Gegenwart. Zugegebenermaßen ist er etwas whiggistisch – er erzählt die Geschichte, als hätte sie immer hierher geführt. Die Geschichte wusste natürlich nicht, wohin sie ging. Doch die Stränge sind real, die Verbindungen sind echt, und ihr Verständnis ist wesentlich, um zu verstehen, warum Projekte wie champollion existieren, warum sie so gebaut sind, wie sie gebaut sind, und warum sie gerade jetzt von Bedeutung sind.

---

## I. Die Grammatik von allem: Von Pāṇini zu Chomsky

### Die erste formale Grammatik (ca. 4. Jahrhundert v. Chr.)

Die Geschichte beginnt nicht an einer europäischen Universität, sondern im alten Indien, mit einem Gelehrten namens Pāṇini. Um das 4. Jahrhundert v. Chr. verfasste Pāṇini das *Aṣṭādhyāyī* – eine Grammatik des Sanskrit, die aus etwa 4.000 Regeln besteht. Dies war keine Grammatik im lockeren, pädagogischen Sinne. Es war eine *generative* Grammatik: eine endliche Menge von Regeln, die im Prinzip jede gültige Äußerung in der Sprache erzeugen konnten.

Pāṇinis System verwendete das, was wir heute als formale Ersetzungsregeln erkennen würden, mit Variablen, Rekursion und geordneter Anwendung. Der Linguist Paul Kiparsky hat argumentiert, dass das *Aṣṭādhyāyī* „die vollständigste generative Grammatik einer jeden bisher geschriebenen Sprache" sei (Kiparsky, 1993). Der Informatiker Gerard Huet hat gezeigt, dass Pāṇinis Regeln als endlicher Transduktor modelliert werden können – derselbe rechnerische Formalismus, der fünfundzwanzig Jahrhunderte später zentral für die morphologische Analyse polysynthetischer Sprachen werden sollte.

Pāṇini wusste nicht, dass er Informatik betrieb. Aber er tat es.

### Der Stein von Rosette und die Geburt der vergleichenden Sprachwissenschaft (1799)

Für den größten Teil der aufgezeichneten Geschichte war das Studium der Sprache in erster Linie das Studium der *eigenen* Sprache – oder bestenfalls das Studium einer heiligen oder klassischen Sprache zu liturgischen Zwecken. Die intellektuelle Revolution, die die moderne Sprachwissenschaft hervorbrachte, begann mit einem Stein.

Der Stein von Rosette, 1799 von Napoleons Soldaten entdeckt, trug denselben Erlass in drei Schriften: ägyptische Hieroglyphen, demotische Schrift und Altgriechisch. Jean-François Champollions Entzifferung der Hieroglyphen im Jahr 1822 war mehr als ein archäologischer Triumph. Sie demonstrierte ein Prinzip, das grundlegend werden sollte: dass Sprachen *durcheinander* verstanden werden konnten. Übersetzung war nicht bloß eine praktische Fertigkeit; sie war eine Methode der wissenschaftlichen Untersuchung.

### William Jones und die indogermanische Hypothese (1786)

Noch vor Champollion hatte der britische Philologe Sir William Jones im Jahr 1786 seine berühmte Vorlesung vor der Asiatic Society of Bengal gehalten, in der er feststellte, dass Sanskrit zu Griechisch und Latein „eine stärkere Verwandtschaft aufweist, sowohl in den Wurzeln der Verben als auch in den Formen der Grammatik, als sie möglicherweise durch Zufall hätte entstehen können". Jones schlug vor, dass alle drei von einem gemeinsamen Vorfahren abstammten, „der vielleicht nicht mehr existiert".

Dies war die Geburt der historischen und vergleichenden Sprachwissenschaft. Sie begründete, dass Sprachen keine isolierten, statischen Entitäten waren, sondern Mitglieder von Familien – verwandt durch Abstammung, geformt durch die Zeit, regelmäßigen Gesetzen des Wandels unterworfen. Es war auf seine Weise eine Evolutionstheorie, Jahrzehnte vor Darwin.

### August Schleichers Sprachbäume (1861)

Es war August Schleicher, ein deutscher Linguist, der die darwinistische Verbindung explizit machte. Im Jahr 1861 – nur zwei Jahre nach *On the Origin of Species* – veröffentlichte Schleicher sein *Stammbaum*-Modell der indogermanischen Sprachen. Seine Diagramme sehen fast nicht von phylogenetischen Bäumen in der Biologie zu unterscheiden aus. Sprachen verzweigten sich, divergierten und starben gelegentlich aus, ebenso wie Arten.

Schleichers Bäume waren eine Vereinfachung (Sprachen *konvergieren* auch durch Kontakt, Entlehnung und Kreolisierung), doch das Modell erwies sich als außerordentlich produktiv. Es begründete das Prinzip, dass sprachliche Vielfalt kein zufälliges Rauschen, sondern strukturierte Daten waren, die einer systematischen Analyse zugänglich sind. Und es warf implizit eine Frage auf, die für unser Projekt zentral bleibt: Was geschieht mit den Zweigen, die sterben?

### Ferdinand de Saussure und die Architektur der Sprache (1916)

Die nächste Revolution kam von Ferdinand de Saussure, dessen *Cours de linguistique générale* (posthum 1916 aus den Aufzeichnungen von Studenten veröffentlicht) die strukturalistische Sprachwissenschaft begründete. Saussure zog eine scharfe Unterscheidung zwischen *langue* (dem abstrakten System einer Sprache) und *parole* (der tatsächlichen Rede). Er argumentierte, dass sprachliche Zeichen *willkürlich* seien – das Wort „Baum" trägt keine inhärente Verbindung zu Bäumen – und dass Bedeutung aus *Differenzen* innerhalb eines Systems entstehe, nicht aus einem positiven Gehalt.

Saussures Schlüsseldiagramm – das Oval, geteilt zwischen *signifié* (Signifikat, dem Begriff) und *signifiant* (Signifikant, dem Lautbild), verbunden durch Pfeile, die ihre untrennbare Beziehung zeigen – wurde zu einem der am häufigsten reproduzierten Bilder in den Geisteswissenschaften. Es begründete das Prinzip, dass eine Sprache ein *System von Systemen* ist, in dem jedes Element seinen Wert aus seinen Beziehungen zu allen anderen ableitet.

Dies hatte tiefgreifende Auswirkungen auf die Übersetzung. Wenn Bedeutung relational und systemisch ist, dann ist Übersetzung keine Angelegenheit des Vertauschens von Wörtern. Sie erfordert das Verständnis der gesamten Architektur einer Sprache. Zwei Sprachen können die Welt auf grundlegend verschiedene Weise gliedern – eine Erkenntnis, die später von Edward Sapir und Benjamin Lee Whorf weiterentwickelt (und manchmal überzeichnet) wurde.

### Sapir, Bloomfield und das Studium indigener Sprachen

In Nordamerika brachte das frühe 20. Jahrhundert eine andere Tradition der sprachwissenschaftlichen Feldforschung hervor. Edward Sapir und Leonard Bloomfield arbeiteten ausgiebig mit indigenen Sprachen – Sapir mit Navajo, Nootka und vielen anderen; Bloomfield mit Menomini und anderen Algonkin-Sprachen. Sie stießen auf sprachliche Strukturen, die sich radikal von allem in der indogermanischen Familie unterschieden.

Insbesondere Sapir entwickelte ein typologisches Rahmenwerk, das Sprachen entlang mehrerer Achsen klassifizierte, darunter die entscheidende Unterscheidung zwischen *analytischen* Sprachen (wie dem Englischen, wo Wörter tendenziell kurz sind und die Bedeutung durch die Wortstellung getragen wird) und *polysynthetischen* Sprachen (wie dem Cree, wo ein einziges Wort das kodieren kann, was das Englische als ganzen Satz ausdrücken würde). Eine einzige Cree-Verbform könnte das Subjekt, das Objekt, das Tempus, den Aspekt, die Evidentialität und mehrere modifizierende Elemente in einem morphologisch komplexen Wort vereinen.

Diese Arbeit begründete zwei Tatsachen, die für unser Projekt zentral bleiben. Erstens: Die Sprachen der Welt sind weitaus strukturell vielfältiger, als es ein europazentrisches Modell vermuten ließe. Zweitens: Viele dieser Sprachen waren bereits gefährdet. Doch während die frühen strukturalistischen Linguisten diese Komplexität dokumentierten, beteiligten sie sich oft an einer „Bergungsanthropologie" (salvage anthropology) – einem ausbeuterischen akademischen Modell, das indigene Menschen lediglich als „Informanten" behandelte, um westliche akademische Karrieren aufzubauen. Dieser Ansatz trennte Sprachen von ihren erkenntnistheoretischen Wurzeln und ebnete den Weg dafür, Sprache als körperlose, extrahierbare Daten zu behandeln, statt als lebendige, relationale Systeme.

### Die Chomsky-Revolution (1957)

Im Jahr 1957 veröffentlichte ein 28-jähriger MIT-Linguist namens Noam Chomsky *Syntactic Structures*, ein schmales Buch, das in dem Fachgebiet einschlug wie eine Bombe. Chomsky argumentierte, dass das Ziel der Sprachwissenschaft darin bestehen sollte, die *generative Grammatik* einer Sprache zu entdecken – eine endliche Menge von Regeln, die alle und nur die grammatikalischen Sätze dieser Sprache erzeugen konnten.

Noch provokanter schlug Chomsky die *Chomsky-Hierarchie* vor: eine Klassifizierung formaler Grammatiken nach ihrer Rechenmächtigkeit. Die Hierarchie hat vier Ebenen:

- **Typ 3 (Regulär)**: Erkannt von endlichen Automaten. Einfache Muster.
- **Typ 2 (Kontextfrei)**: Erkannt von Kellerautomaten. Rekursive Strukturen wie verschachtelte Klammern.
- **Typ 1 (Kontextsensitiv)**: Erkannt von linear beschränkten Automaten. Komplexere Abhängigkeiten.
- **Typ 0 (Rekursiv aufzählbar)**: Erkannt von Turing-Maschinen. Alles Berechenbare.

Chomsky argumentierte, dass natürliche Sprachen mindestens kontextfreie Grammatiken erforderten und möglicherweise mehr. Dies war eine direkte Brücke zwischen der Sprachwissenschaft und der mathematischen Theorie der Berechnung. Dieselben formalen Werkzeuge, die Alan Turing entwickelt hatte, um über die Grenzen des Rechnens nachzudenken, konnten nun auf die menschliche Sprache angewendet werden.

Chomsky schlug auch die Idee der *Universalgrammatik* vor – dass die Fähigkeit zur Sprache angeboren sei, dass alle menschlichen Sprachen tiefe strukturelle Eigenschaften teilten und dass die Vielfalt der Oberflächenformen eine zugrunde liegende Einheit verberge. Dies bleibt umstritten (viele Typologen und Funktionalisten widersprechen), doch die formalen Werkzeuge, die Chomsky einführte – Phrasenstrukturregeln, Transformationsgrammatiken, die Hierarchie selbst –, wurden zur Grundlage der Computerlinguistik.

---

## II. Der Traum von der universellen Übersetzung

### Ramon Llulls Denkmaschine (1305)

Der Traum, das Denken zu mechanisieren – und damit der Traum von der maschinellen Übersetzung – ist bemerkenswert alt. Ramon Llull, ein katalanischer Mystiker des 13. Jahrhunderts, entwarf die *Ars Magna*: ein System rotierender konzentrischer Scheiben, die mit grundlegenden Begriffen beschriftet waren und deren Kombinationen alle möglichen Wahrheiten erzeugen sollten. Llulls Räder waren in gewissem Sinne die erste kombinatorische Logikmaschine. Leibniz nannte Llull später als Inspiration.

### Athanasius Kircher und die Polygraphia Nova (1663)

Athanasius Kircher, der große jesuitische Universalgelehrte, veröffentlichte 1663 die *Polygraphia Nova et Universalis* – ein System der „universellen Schrift", das die Kommunikation über Sprachbarrieren hinweg ermöglichen sollte. Kirchers System wies Begriffen Zahlen zu, die dann mit der entsprechenden Tabelle in jede Sprache dekodiert werden konnten. Es war im Wesentlichen eine Interlingua – eine sprachunabhängige Repräsentation von Bedeutung.

Das System funktionierte nicht sehr gut. Doch die *Idee* blieb bestehen: dass zwischen zwei beliebigen Sprachen ein gemeinsamer begrifflicher Raum existiert und dass Übersetzung eine Frage der Abbildung durch diesen Raum sei. Diese Interlingua-Hypothese war nicht nur ein fehlerhaftes wissenschaftliches Experiment; sie war eine erkenntnistheoretische Erweiterung der kolonialen Kontrolle, unfähig, divergierende Ontologien abzubilden. Der Philosoph W. V. O. Quine sollte dieses Scheitern später mit seinem Konzept der *Unbestimmtheit der Übersetzung* (1960) formalisieren und argumentieren, dass radikale Übersetzung von Natur aus unbestimmt ist. Eine universelle, kontextfreie Abbildung zwischen grundlegend divergierenden sprachlichen Systemen ist eine philosophische Unmöglichkeit, nicht bloß eine ingenieurtechnische Hürde.

### John Wilkins und die philosophische Sprache (1668)

Nur fünf Jahre nach Kircher veröffentlichte der englische Naturphilosoph John Wilkins *An Essay towards a Real Character, and a Philosophical Language* – ein Versuch, eine Sprache zu schaffen, deren Struktur *die Struktur der Realität perfekt widerspiegelte*. Jeder Begriff würde in einer großen Taxonomie klassifiziert, und sein Name würde seine Position in dieser Taxonomie kodieren.

Wilkins' Projekt scheiterte (die Realität erwies sich als widerständig gegenüber ordentlicher Klassifizierung), doch es nahm etwas Wichtiges vorweg: die Idee, dass Sprache *konstruiert* werden könne, dass die Beziehung zwischen Wörtern und Bedeutungen systematisch und explizit gemacht werden könne. Dies ist in einem tiefen Sinne das, was Computerlinguisten tun, wenn sie Ontologien und Wissensgraphen erstellen.

### Leibniz und die Characteristica Universalis

Gottfried Wilhelm Leibniz, der unabhängig die Infinitesimalrechnung erfand und eine mechanische Rechenmaschine entwarf, träumte von einer *characteristica universalis* – einer universellen formalen Sprache, in der alles menschliche Wissen ausgedrückt werden könnte – und einem *calculus ratiocinator* – einer Maschine, die in dieser Sprache schlussfolgern könnte. „Sollten Streitigkeiten entstehen", schrieb Leibniz, „so wäre zwischen zwei Philosophen ebenso wenig eine Erörterung nötig wie zwischen zwei Rechnern. Denn es würde genügen, die Federn in die Hand zu nehmen, sich an die Rechentafeln zu setzen und zueinander zu sagen: Lasst uns rechnen."

Leibniz erfand auch die binäre Arithmetik – das Zahlensystem, das Jahrhunderte später zur Sprache der digitalen Computer werden sollte. Seine Schrift *Explication de l'Arithmétique Binaire* von 1703 zeigte, dass jede Zahl allein mit 0 und 1 dargestellt werden konnte. Er sah dies als Spiegelbild der göttlichen Schöpfung (etwas aus dem Nichts), doch es sollte sich als Grundlage aller digitalen Berechnung erweisen.

### Warren Weavers Memorandum (1949)

Die moderne Ära der maschinellen Übersetzung beginnt mit einem Memorandum. Im Juli 1949 schrieb der amerikanische Mathematiker und Wissenschaftsadministrator Warren Weaver an Norbert Wiener und schlug vor, dass die neuen elektronischen Computer auf die Übersetzung angewendet werden könnten. Sein Memorandum enthielt die bemerkenswerte Passage, die zu Beginn dieses Beitrags zitiert wurde: die Idee, dass ein russischer Text „eigentlich auf Englisch geschrieben, aber ... in einigen seltsamen Symbolen kodiert" sei.

Weavers Metapher war der Kryptoanalyse aus Kriegszeiten entlehnt – die Idee, dass Übersetzung grundlegend ein *Dekodierungsproblem* sei. Dies war nicht bloß eine Analogie. Dieselben statistischen und informationstheoretischen Werkzeuge, die zur Entschlüsselung feindlicher Chiffren entwickelt worden waren, könnten, so schlug Weaver vor, auf das Problem der Übersetzung anwendbar sein.

Das Memorandum war wild optimistisch, doch es startete ein Forschungsprogramm. Innerhalb von fünf Jahren würde die erste Vorführung der maschinellen Übersetzung stattfinden.

---

## III. Die Maschinerie des Denkens: Berechnung und Information

### George Boole und die Algebra der Logik (1854)

Im Jahr 1854 veröffentlichte George Boole *An Investigation of the Laws of Thought* – ein Werk, das das logische Schlussfolgern auf algebraische Operationen reduzierte. Boole zeigte, dass die Aussagen der Logik mit denselben Regeln wie die Algebra manipuliert werden konnten, wobei AND der Multiplikation, OR der Addition und NOT dem Komplement entsprach.

Die boolesche Algebra erschien damals wie eine mathematische Kuriosität. Sie sollte zum Funktionsprinzip jeder jemals gebauten digitalen Schaltung werden.

### Charles Babbage und Ada Lovelace (1837–1843)

Charles Babbage entwarf (vollendete jedoch nie) die Analytical Engine – einen mechanischen, dampfbetriebenen Universalcomputer. Im Gegensatz zu seiner früheren Difference Engine (einem spezialisierten Rechner) verfügte die Analytical Engine über einen Speicher („the Store"), eine Verarbeitungseinheit („the Mill"), bedingte Verzweigung und Schleifen. Sie war im Prinzip Turing-vollständig.

Ada Lovelace, die von einer Beschreibung der Engine ausging, verfasste eine Reihe detaillierter Anmerkungen, die das enthielten, was weithin als das erste veröffentlichte Computerprogramm gilt: einen Algorithmus zur Berechnung der Bernoulli-Zahlen (Note G, 1843). Doch Lovelaces tiefgreifendster Beitrag war konzeptioneller Natur. Sie erkannte, dass die Engine *Symbole* manipulieren konnte, nicht nur Zahlen. „Die Analytical Engine webt algebraische Muster", schrieb sie, „genau wie der Jacquard-Webstuhl Blumen und Blätter webt." Die Implikation – dass Berechnung auf jeden Bereich mit einer formalen Struktur angewendet werden könnte, einschließlich der Sprache – war vorausschauend.

### Alan Turing und die universelle Maschine (1936)

Im Jahr 1936 veröffentlichte Alan Turing „On Computable Numbers, with an Application to the Entscheidungsproblem" – einen Aufsatz, der gleichzeitig die Berechnung definierte, ihre Grenzen bewies und den modernen Computer (in abstrakter Form) erfand.

Turings Schlüsselerkenntnis war die *universelle Maschine*: eine einzige Maschine, die bei den richtigen, auf ihrem Band kodierten Anweisungen *jede andere* Maschine simulieren konnte. Dies begründete, dass es keinen wesentlichen Unterschied zwischen Hardware und Software, zwischen der Maschine und dem Programm gab. Ein einziges Gerät konnte, richtig programmiert, alles berechnen, was überhaupt berechenbar war.

Turings Arbeit begründete auch die Grenzen der Berechnung (das Halteproblem) und legte das Fundament für seine spätere Erforschung der maschinellen Intelligenz. Sein Aufsatz „Computing Machinery and Intelligence" von 1950, der den berühmten Turing-Test vorschlug, formulierte die Frage der maschinellen Intelligenz explizit in Bezug auf *Sprache*: Eine Maschine ist intelligent, wenn sie sich in einer Unterhaltung nicht von einem Menschen unterscheiden lässt.

### Claude Shannon und die Informationstheorie (1948)

Im Jahr 1948 veröffentlichte Claude Shannon „A Mathematical Theory of Communication" im *Bell System Technical Journal* – einen Aufsatz, der das Gebiet der Informationstheorie begründete. Shannon zeigte, dass Kommunikation als ein System modelliert werden könne: Eine *Informationsquelle* erzeugt eine *Nachricht*, die ein *Sender* in ein *Signal* kodiert, das einen *Kanal* (der *Rauschen* unterworfen ist) durchläuft, das ein *Empfänger* wieder in eine Nachricht für ein *Ziel* dekodiert.

Shannons Schlüsselbeitrag war das Konzept der *Entropie* – ein Maß für die Unsicherheit oder den Informationsgehalt einer Nachricht. Er bewies, dass für jeden Kanal mit einem gegebenen Rauschpegel eine maximale Rate existiert, mit der Informationen zuverlässig übertragen werden können (die Kanalkapazität), und dass diese Rate mit hinreichend cleverer Kodierung erreicht werden kann.

Die Verbindung zur Übersetzung ist tiefgreifend. Shannon selbst nutzte in einem Aufsatz von 1951 die Informationstheorie, um die statistische Struktur des Englischen zu analysieren. Er zeigte, dass englischer Text hochgradig redundant ist – dass ein Muttersprachler, dem eine Buchstabenfolge gegeben wird, den nächsten Buchstaben mit hoher Genauigkeit vorhersagen kann. Diese Redundanz ist es, die die Kommunikation robust gegen Rauschen macht, doch sie bedeutet auch, dass der *Informationsgehalt* der Sprache weitaus geringer ist, als ihre rohe Symbolzahl vermuten ließe.

Warren Weaver sah die Verbindung sofort: Wenn Übersetzung Dekodierung ist und wenn die statistische Struktur der Sprache modelliert werden kann, dann ist Übersetzung ein informationstheoretisches Problem. Diese Erkenntnis sollte Jahrzehnte brauchen, um Früchte zu tragen, doch als es so weit war, verwandelte sie das Fachgebiet.

### Von Neumann und der speicherprogrammierte Computer (1945)

John von Neumanns Bericht von 1945 über den EDVAC (Electronic Discrete Variable Automatic Computer) beschrieb das, was wir heute die *Von-Neumann-Architektur* nennen: einen Computer mit einem einzigen Speicher für sowohl Daten als auch Anweisungen, einer zentralen Verarbeitungseinheit und Ein-/Ausgabemechanismen. Diese Architektur – Daten und Programme teilen sich denselben Speicher, sequenziell von einer CPU verarbeitet – bleibt das grundlegende Design nahezu jedes heute verwendeten Computers.

Die Von-Neumann-Architektur machte Software praktikabel. Programme konnten gespeichert, modifiziert und sogar von anderen Programmen erzeugt werden. Dies war die technologische Voraussetzung für alles, was folgte: Compiler, Betriebssysteme und schließlich die neuronalen Netzwerk-Frameworks, die die moderne maschinelle Übersetzung antreiben.

---

## IV. Maschinelle Übersetzung: Das erste KI-Problem

### Das Georgetown-IBM-Experiment und der Kalte Krieg (1954)

Am 7. Januar 1954 demonstrierten Forscher der Georgetown University und von IBM das erste öffentliche System zur maschinellen Übersetzung. Das System übersetzte 60 russische Sätze ins Englische unter Verwendung eines Vokabulars von 250 Wörtern und sechs Grammatikregeln. Die Sätze wurden sorgfältig so ausgewählt, dass sie innerhalb der Fähigkeiten des Systems lagen, doch die Vorführung erzeugte enorme Begeisterung.

Die *New York Times* berichtete, dass das Experiment eine Zukunft ankündigte, in der ein „elektronischer Übersetzer auf Knopfdruck" die gesamte wissenschaftliche Literatur der Welt augenblicklich zugänglich machen würde. Dieser öffentliche Optimismus verschleierte jedoch die materielle Realität der Finanzierung und des Zwecks des Projekts. Das Georgetown-IBM-Experiment – und das frühe Feld der maschinellen Übersetzung im Allgemeinen – wurde nicht von einem utopischen Wunsch nach universeller Kommunikation angetrieben. Es wurde vom militärischen und nachrichtendienstlichen Apparat der Vereinigten Staaten (einschließlich der CIA und DARPA) als dringendes Gebot des Kalten Krieges finanziert, um sowjetische wissenschaftliche und militärische Texte zu überwachen und abzufangen.

Die Sichtweise der Sprache als „zu knackender Code" (wie Weaver es ausdrückte) war untrennbar mit militarisierter Überwachung verbunden. Forscher sagten voraus, dass die maschinelle Übersetzung innerhalb von fünf Jahren ein gelöstes Problem sein würde. Sie irrten sich um mehr als ein halbes Jahrhundert.

### Der ALPAC-Bericht und der erste KI-Winter (1966)

Im Jahr 1966 gab das Automatic Language Processing Advisory Committee (ALPAC), das von der US-Regierung einberufen wurde, einen vernichtenden Bericht heraus. Nach der Überprüfung eines Jahrzehnts der MT-Forschung kam ALPAC zu dem Schluss, dass die maschinelle Übersetzung langsamer, ungenauer und teurer als die menschliche Übersetzung sei, und empfahl, die Finanzierung in die Grundlagenforschung der Computerlinguistik umzuleiten.

Der ALPAC-Bericht beendete in den Vereinigten Staaten die Finanzierung der MT-Forschung über ein Jahrzehnt lang effektiv. Es war der erste „KI-Winter" – ein Muster, das sich wiederholen sollte: extravagante Versprechungen, bescheidene Ergebnisse, Ernüchterung, Finanzierungszusammenbruch.

Doch der Bericht enthielt auch eine tiefere Erkenntnis. Die maschinelle Übersetzung war zum Teil deshalb gescheitert, weil die Sprache schwieriger war, als irgendjemand erwartet hatte. Der regelbasierte Ansatz – das Schreiben expliziter Grammatikregeln zum Parsen und Erzeugen von Sätzen – funktionierte für einfache Fälle, brach jedoch bei echtem Text katastrophal zusammen. Die Sprache war zu mehrdeutig, zu kontextabhängig, zu *lebendig*, als dass spröde Regeln sie erfassen könnten.

### Regelbasierte und transferbasierte MT (1970er–1980er)

Die Forschung wurde, leiser, durch die 1970er und 1980er Jahre fortgesetzt. Systeme wie SYSTRAN (das die frühen Übersetzungsdienste der Europäischen Kommission antrieb) verwendeten große, handgefertigte Wörterbücher und Transferregeln, um zwischen Sprachpaaren abzubilden. Diese Systeme konnten für eingeschränkte Domänen brauchbare grobe Übersetzungen erzeugen, doch sie erforderten einen enormen technischen Aufwand für jedes Sprachpaar, und sie bewältigten uneingeschränkten Text selten anmutig.

Das grundlegende Problem war klar: Sprache ist keine Chiffre. Man kann nicht übersetzen, indem man Wörter in einem Wörterbuch nachschlägt und sie nach grammatikalischen Regeln umordnet, denn Bedeutung hängt vom Kontext ab, vom Weltwissen, von der Absicht des Sprechers, von der gesamten Geschichte einer Unterhaltung. Der Interlingua-Ansatz – das Übersetzen über eine abstrakte, sprachunabhängige Repräsentation – war theoretisch elegant, aber praktisch unmöglich. Niemand konnte die Interlingua definieren.

### Die statistische Revolution (1990er)

Der Durchbruch kam nicht von besseren Regeln, sondern von besseren Daten. In den späten 1980er und frühen 1990er Jahren entwickelten Forscher bei IBM (Peter Brown, Stephen Della Pietra, Vincent Della Pietra und Robert Mercer) eine Reihe statistischer Modelle für die maschinelle Übersetzung – die berühmten IBM-Modelle 1 bis 5.

Die Schlüsselerkenntnis war Weavers alte Idee, endlich rigoros gemacht: Übersetzung als Dekodierung. Finde für einen fremdsprachlichen Satz *f* den englischen Satz *e*, der P(e|f) maximiert. Nach dem Satz von Bayes ist dies äquivalent zur Maximierung von P(f|e) × P(e) – einem *Übersetzungsmodell* (wie wahrscheinlich ist dieser fremdsprachliche Satz angesichts dieses englischen?) mal einem *Sprachmodell* (wie wahrscheinlich ist dieser englische Satz für sich genommen?).

Die IBM-Modelle lernten diese Wahrscheinlichkeiten aus großen *Parallelkorpora* – Sammlungen von Texten, die in beiden Sprachen existierten (wie die kanadischen Parlamentsprotokolle, die Hansards, die sowohl auf Englisch als auch auf Französisch veröffentlicht wurden). Es waren keine handgefertigten Regeln erforderlich. Das System lernte zu übersetzen, indem es Millionen von Beispielen menschlicher Übersetzung beobachtete.

Statistische MT funktionierte für Sprachen mit reichlich vorhandenen Paralleldaten dramatisch besser als regelbasierte MT. Sie führte auch ein entscheidendes Stück Infrastruktur ein: den **BLEU**-Score (Papineni et al., 2002), eine Metrik zur automatischen Bewertung der Übersetzungsqualität durch den Vergleich der Maschinenausgabe mit menschlichen Referenzübersetzungen. BLEU machte es möglich, Fortschritte quantitativ zu messen und groß angelegte Experimente durchzuführen.

Doch der statistischen MT war eine fatale Annahme einprogrammiert: Sie erforderte *Parallelkorpora*. Für die wichtigsten Sprachpaare der Welt – Englisch-Französisch, Englisch-Chinesisch, Englisch-Spanisch – waren Paralleldaten reichlich vorhanden. Für die überwiegende Mehrheit der 7.000 Sprachen der Welt existierten sie schlicht nicht.

### Die neuronale Revolution: Seq2Seq, Attention, Transformers (2014–2017)

Die nächste Transformation kam mit dem Deep Learning. Im Jahr 2014 demonstrierten Ilya Sutskever, Oriol Vinyals und Quoc Le *Sequence-to-Sequence*-Modelle (seq2seq) für MT: neuronale Netze, die einen ganzen Satz in einer Sprache einlesen und eine Übersetzung in einer anderen erzeugen konnten, ohne jegliche explizite Ausrichtung oder Phrasentabellen.

Im Jahr 2015 führten Dzmitry Bahdanau, Kyunghyun Cho und Yoshua Bengio den *Attention-Mechanismus* ein – der es dem Decoder erlaubte, beim Erzeugen jedes Wortes der Übersetzung auf verschiedene Teile des Quellsatzes „zurückzublicken". Dies verbesserte die Leistung bei langen Sätzen dramatisch.

Und im Jahr 2017 veröffentlichten Vaswani et al. bei Google „Attention Is All You Need" und führten die *Transformer*-Architektur ein. Der Transformer verzichtete vollständig auf Rekurrenz und verarbeitete ganze Sequenzen parallel mittels Self-Attention. Er war schneller zu trainieren, leichter zu skalieren und erzeugte bessere Übersetzungen als alles, was zuvor gekommen war.

Transformers führten direkt zu den großen Sprachmodellen (LLMs) der 2020er Jahre: GPT, BERT, PaLM, LLaMA und ihren Nachkommen. Diese Modelle, trainiert auf riesigen Textmengen aus dem Internet, können zwischen Hunderten von Sprachpaaren mit bemerkenswerter Sprachgewandtheit übersetzen.

Doch „bemerkenswerte Sprachgewandtheit" ist nicht dasselbe wie „zuverlässige Genauigkeit". Und für die ressourcenarmen Sprachen der Welt ist die Situation weitaus schlimmer, als sie scheint.

---

## V. Die andere Geschichte: Sprache, Macht und kultureller Völkermord

Die vorangegangenen vier Abschnitte erzählen die Geschichte der Ideen – von Grammatikern, Mathematikern und Ingenieuren, die auf die maschinelle Übersetzung hinarbeiteten. Doch es gibt eine andere Geschichte, die parallel verläuft und erklärt, *warum* die Sprachen, die Übersetzungstechnologie am dringendsten benötigen, gerade jene sind, für die es sie nicht gibt. Dies ist keine Geschichte über Datenknappheit als neutrale Tatsache. Es ist eine Geschichte über gezielte Zerstörung.

Der Grund, warum es für das Plains Cree keine maschinelle Übersetzungsunterstützung gibt, ist nicht in erster Linie, dass Cree eine schwierige Sprache für Computer ist (obwohl es das ist). Es liegt daran, dass die Regierungen Kanadas und der Vereinigten Staaten über ein Jahrhundert lang systematische Programme betrieben haben, um indigene Sprachen aus den Mündern von Kindern auszurotten. Die „Datenknappheit", die ressourcenarme MT so schwierig macht, ist zum großen Teil die *nachgelagerte Folge des kulturellen Völkermords*. Jede ehrliche Darstellung dessen, warum diese Sprachen Technologie benötigen, muss sich damit auseinandersetzen, warum sie überhaupt an den Rand des Aussterbens gebracht wurden.

### Vor dem Kontakt: Ein Kontinent von Sprachen

Die sprachliche Vielfalt des vorkolonialen Amerikas war erstaunlich. Zur Zeit des europäischen Kontakts beheimatete allein Nordamerika schätzungsweise 300 bis 600 verschiedene Sprachen, organisiert in Dutzenden nicht verwandter Sprachfamilien – mehr genetische Vielfalt als in ganz Europa. Südamerika hatte möglicherweise 1.500 oder mehr (Campbell, 1997). Australien hatte über 250 Sprachen. Die Pazifikinseln, das südlich der Sahara gelegene Afrika und das südostasiatische Festland waren ähnlich vielfältig.

Dies waren keine „primitiven" oder „einfachen" Sprachen. Viele der strukturell komplexesten je dokumentierten Sprachen sind indigen. Die polysynthetische Morphologie der Algonkin-Sprachen (einschließlich Cree, Ojibwe und Blackfoot), die Tonsysteme des Navajo, die ausgefeilte Evidentialitätsmarkierung des Quechua, die Klick-Konsonanten der Khoisan-Sprachen – diese repräsentieren das gesamte Spektrum dessen, was menschliche Sprache sein kann. Sie kodieren ausgefeilte Wissenssysteme über Verwandtschaft, Ökologie, Recht, Spiritualität und Geschichte. Jede Sprache ist eine Bibliothek – ein unersetzlicher Bericht über die Art und Weise, wie eine Gemeinschaft die Welt versteht und ordnet.

Edward Sapir erkannte dies deutlich. 1921 schrieb er, dass „wenn es um die sprachliche Form geht, Platon mit dem mazedonischen Schweinehirten geht, Konfuzius mit dem kopfjagenden Wilden von Assam." Die Sprachen indigener Völker waren nicht minderwertig. Sie waren anders – und ihre Unterschiede enthielten Wissen, das keine andere Sprache besaß.

### Die Mechanik des Sprachtods

Sprachen sterben nicht an natürlichen Ursachen. Sie sterben, wenn die Bedingungen für ihre Weitergabe gestört werden – wenn Kinder aufhören, sie zu lernen, wenn Sprecher für ihren Gebrauch bestraft werden, wenn sich die sozialen und wirtschaftlichen Anreize so verschieben, dass das Sprechen der dominanten Sprache zur Überlebensbedingung wird.

Diese Störung kann allmählich geschehen, durch wirtschaftlichen und demografischen Druck. Doch in der gesamten kolonialen Welt war sie überwältigend *gezielt*. Die Unterdrückung indigener Sprachen war keine Nebenwirkung der Kolonisierung. Sie war ein erklärtes politisches Ziel.

### Kanada: Das Residential-School-System (1831–1996)

In Kanada existierte das Indian-Residential-School-System über 160 Jahre lang, mit dem ausdrücklichen Ziel, indigene Sprachen und Kulturen zu beseitigen. Schätzungsweise 150.000 Kinder der First Nations, der Métis und der Inuit wurden aus ihren Familien und Gemeinschaften entfernt und in staatlich finanzierte, von Kirchen betriebene Internate gebracht.

Die zentrale Politik wurde von Duncan Campbell Scott, dem Deputy Superintendent General of Indian Affairs, im Jahr 1920 mit erschreckender Klarheit formuliert: „Ich will das Indianerproblem loswerden ... Unser Ziel ist es fortzufahren, bis es nicht einen einzigen Indianer in Kanada gibt, der nicht in den Staatskörper aufgenommen wurde, und es keine Indianerfrage und kein Indianerministerium mehr gibt."

Der Mechanismus war die Sprache. Den Kindern war es verboten, ihre Muttersprachen zu sprechen. Bestrafungen für das Sprechen einer indigenen Sprache reichten von Schlägen über Einzelhaft bis hin dazu, dass ihnen Nadeln durch die Zunge gestochen wurden. Die Kinder kamen an und sprachen Cree, Ojibwe, Inuktitut, Dene, Haida oder eine von Dutzenden anderer Sprachen. Sie wurden bestraft, bis sie aufhörten.

Die Truth and Reconciliation Commission of Canada (2015) dokumentierte den systematischen Charakter dieses Angriffs. Ihr Abschlussbericht kam zu dem Schluss, dass das Residential-School-System einen *kulturellen Völkermord* darstellte – die Zerstörung der Strukturen und Praktiken, die es einer Gruppe erlauben, als Gruppe fortzubestehen. Die Sprache war das vorrangige Ziel. Ohne Sprache wird die Zeremonie gestört, die mündliche Geschichte zerbrochen, Verwandtschaftssysteme werden unverständlich, und die generationenübergreifende Weitergabe von Wissen hört auf.

Die letzte bundesstaatlich betriebene Residential School in Kanada schloss 1996. Viele der Ältesten, die heute die letzten fließenden Sprecher ihrer Sprachen sind, sind Überlebende der Residential Schools. Ihre Sprachgewandtheit ist nicht bloß eine sprachliche Ressource. Sie ist ein Akt des Widerstands.

### Die Vereinigten Staaten: Indian Boarding Schools (1860er–1960er)

Die Vereinigten Staaten betrieben ein paralleles System. Captain Richard Henry Pratt, Gründer der Carlisle Indian Industrial School im Jahr 1879, prägte den Satz, der die Ära definierte: „Töte den Indianer, rette den Menschen." Über 350 staatlich finanzierte Internate waren in den Vereinigten Staaten in Betrieb, mit Richtlinien, die nahezu identisch mit denen in Kanada waren. Indigenen Kindern war es verboten, ihre Sprachen zu sprechen, sie wurden gezwungen, englische Namen anzunehmen, und einer systematischen kulturellen Auslöschung unterzogen.

Ein Bericht des U.S. Department of the Interior aus dem Jahr 2022 identifizierte über 400 bundesstaatliche Indian Boarding Schools in 37 Bundesstaaten und dokumentierte den Tod von mindestens 500 Kindern im System – eine Zahl, von der der Bericht einräumte, dass sie mit ziemlicher Sicherheit eine erhebliche Unterschätzung war. Die Untersuchung stellte fest, dass das System nicht bloß zur Bildung, sondern zur „kulturellen Assimilierung indigener Kinder durch ihre gewaltsame Umsiedlung aus ihren Familien und Gemeinschaften" konzipiert war.

Die sprachlichen Folgen waren katastrophal. Von den rund 300 indigenen Sprachen, die auf dem Gebiet gesprochen wurden, das zu den Vereinigten Staaten wurde, sind heute mehr als die Hälfte ausgestorben. Von den überlebenden haben die meisten weniger als 1.000 fließende Sprecher, und viele haben weniger als 10. Das Endangered Languages Project klassifiziert die Mehrheit der überlebenden indianischen Sprachen als „stark" oder „kritisch" gefährdet.

### Australien: Die Stolen Generations (1910–1970)

In Australien entfernten Regierungsrichtlinien zwischen 1910 und 1970 gewaltsam Kinder der Aborigines und der Torres-Strait-Insulaner aus ihren Familien. Diese Kinder – bekannt als die Stolen Generations – wurden in Missionen, Reservate und weiße Pflegefamilien gebracht. Das ausdrückliche Ziel war die Assimilation: die Identität der Aborigines innerhalb weniger Generationen wegzuzüchten.

Die Sprachen der Aborigines wurden in Missionen und Regierungsinstitutionen unterdrückt. Kinder, die ihre Sprachen sprachen, wurden bestraft. Der Bericht Bringing Them Home (1997), erstellt von der Australian Human Rights Commission, dokumentierte den systematischen Charakter dieser Entfernungen und ihre verheerenden Auswirkungen auf Sprache, Kultur und Familie.

Von den schätzungsweise 250 australischen Aborigine-Sprachen, die zur Zeit des europäischen Kontakts gesprochen wurden, werden heute weniger als 20 an Kinder weitergegeben (Marmion et al., 2014). Über 100 sind vollständig ausgestorben. Die verbleibenden Sprachen überleben größtenteils durch die Bemühungen älterer Sprecher, die mit Linguisten und Gemeinschaftsorganisationen in einem Wettlauf gegen die Zeit zusammenarbeiten.

### Skandinavien: Die samischen Sprachen

Die Unterdrückung indigener Sprachen beschränkte sich nicht auf siedlungskoloniale Staaten auf der Südhalbkugel. In Norwegen, Schweden und Finnland wurden samische Kinder von der Mitte des 19. Jahrhunderts bis in die 1960er Jahre Internatssystemen (*internatskoler*) unterzogen. Samische Sprachen wurden in den Schulen verboten; Kinder wurden für das Sprechen bestraft. Norwegens Politik der „Norwegisierung" (*fornorskingspolitikk*) zielte ausdrücklich darauf ab, die samische Sprache zu beseitigen und durch das Norwegische zu ersetzen.

Von den neun überlebenden samischen Sprachen haben mehrere weniger als 500 Sprecher. Das Umesamische hat etwa 20. Das Pitesamische hat weniger als 30. Die Sprachen überleben zum Teil aufgrund von Revitalisierungsprogrammen, die in den 1970er Jahren begannen, einschließlich der Einrichtung samischsprachiger Schulen und Medien – Programme, die für einige Dialekte gerade rechtzeitig und für andere zu spät kamen.

### Aotearoa Neuseeland: Te Reo Māori

Die Māori-Sprache (te reo Māori) war bis Mitte des 20. Jahrhunderts die Mehrheitssprache von Aotearoa. Die britischen kolonialen Bildungsrichtlinien, beginnend in den 1860er Jahren, marginalisierten te reo zunehmend in den Schulen. In den 1970er Jahren waren weniger als 20 % der Māori fließende Sprecher, und die Sprache war innerhalb einer Generation vom Aussterben bedroht.

Die Reaktion der Māori war eine der frühesten und erfolgreichsten Sprachrevitalisierungsbewegungen der Welt. Kōhanga reo (Sprachnester) für Vorschulkinder, 1982 eingerichtet, tauchten Säuglinge und Kleinkinder von Geburt an in te reo ein. Kura kaupapa Māori (Māori-sprachige Schulen) folgten. Diese Programme haben, zusammen mit dem Māori Language Act von 1987 (der te reo zu einer Amtssprache machte), die Sprache stabilisiert – obwohl fließende Sprecher noch immer eine Minderheit der Māori-Bevölkerung darstellen.

Neuseeland brachte auch eines der wichtigsten Rahmenwerke für die indigene Datenverwaltung hervor: *Te Mana Raraunga*, das Māori Data Sovereignty Network. Dieses Rahmenwerk behauptet, dass Māori-Daten – einschließlich sprachlicher Daten – ein taonga (Schatz) sind, der den Rechten und Verantwortlichkeiten der kaitiakitanga (Hüterschaft) unterliegt. Es informierte direkt die Entwicklung der CARE-Prinzipien für die indigene Datenverwaltung und ist eine grundlegende Referenz für die Mechanismen der Datensouveränität in champollion.

### Das Muster: Sprache als Ziel kolonialer Macht

Die geografischen und kulturellen Einzelheiten unterscheiden sich, doch das Muster ist bemerkenswert konsistent. In Kanada, den Vereinigten Staaten, Australien, Skandinavien und Neuseeland – und an vielen anderen Orten, von Taiwan über Sibirien bis zum andinen Hochland – identifizierten koloniale und postkoloniale Staaten indigene Sprachen als Hindernisse für die Assimilation und nahmen sie zur Beseitigung ins Visier. Die Werkzeuge waren überall ähnlich: Kinder aus ihren Familien entfernen, den Gebrauch indigener Sprachen verbieten, Übertretungen bestrafen und die Annahme der kolonialen Sprache belohnen.

Dies war keine historische Fußnote. Die letzte Residential School in Kanada schloss *1996*. Die letzte Indian Boarding School in den Vereinigten Staaten schloss in den *1960er Jahren*. Viele der Menschen, die diese Systeme überlebt haben, leben noch. Das Trauma ist generationenübergreifend. Und der sprachliche Schaden dauert an: Sprachen, die in der Ära der Internate eine Generation von Sprechern verloren haben, verlieren nun ihre letzten fließenden Ältesten.

### Vom kulturellen Völkermord zur „Datenknappheit"

Diese Geschichte ist für das technische Problem der maschinellen Übersetzung unmittelbar relevant. Wenn Informatiker eine Sprache als „ressourcenarm" beschreiben, meinen sie typischerweise: Es gibt wenige digitale Texte, wenige Parallelkorpora, wenige Wörterbücher und wenige annotierte Datensätze. Die Rahmung ist neutral, als wäre Datenknappheit ein Naturereignis, wie eine Wüste mit wenig Regen.

Das ist sie nicht. Die „Datenknappheit" indigener Sprachen ist die *nachgelagerte Folge* von Politiken der Sprachunterdrückung. Sprachen, die in den Schulen verboten wurden, brachten weniger geschriebene Texte hervor. Sprachen, deren Sprecher für das Sprechen bestraft wurden, entwickelten weniger institutionelle Verwendungen. Sprachen, die eine Generation der Weitergabe verloren, brachten weniger zweisprachige Sprecher hervor, die Parallelkorpora erstellen konnten.

Die Pipeline vom kulturellen Völkermord zur Datenknappheit ist direkt:

1. **Unterdrückung** → Kinder werden für das Sprechen der Sprache bestraft
2. **Gestörte Weitergabe** → Weniger Kinder lernen die Sprache
3. **Reduzierte Sprecherbasis** → Weniger Erwachsene verwenden sie im täglichen Leben
4. **Reduzierte institutionelle Verwendung** → Weniger schriftliche Dokumente, weniger digitale Texte
5. **Datenknappheit** → ML-Modelle haben nichts zum Trainieren
6. **Keine MT-Unterstützung** → Die Sprache ist für die Technologie unsichtbar
7. **Beschleunigter Niedergang** → Technologie verstärkt die Marginalisierung, die die Politik begonnen hat

Diese Pipeline bedeutet, dass jedes Technologieprojekt, das mit indigenen Sprachen arbeitet, einen politischen und moralischen Kontext erbt, ob es ihn anerkennt oder nicht. Ein System zur maschinellen Übersetzung, das Cree-Sprachdaten als von Modellen aufzunehmendes Rohmaterial behandelt, setzt, wie unbeabsichtigt auch immer, die extraktive Dynamik fort, die mit den Residential Schools begann. Die Daten wurden durch Gewalt knapp gemacht. Die Sprecher, die die vorhandenen Daten schufen, taten dies gegen enorme Widerstände. Jedes System, das diese Daten ohne die bedeutsame Kontrolle der Gemeinschaft verwendet, verschlimmert den ursprünglichen Schaden.

### Die Mittäterschaft der Wissenschaften und die westliche Ideologie

Es ist von entscheidender Bedeutung zu erkennen, dass Wissenschaft und Technologie keine unschuldigen Zuschauer dieses kolonialen Projekts waren; sie waren aktive Teilnehmer. Die „Aufklärungs"-Ideologie, die danach strebte, die Welt zu kategorisieren, zu quantifizieren und zu standardisieren, behandelte indigene Völker und ihre Sprachen oft bloß als Forschungsgegenstände oder Kuriositäten für eine „Bergungsanthropologie". Diese extraktive Praxis schloss Wissen in westlichen Universitäten ein, während sie wenig tat, um die politische Maschinerie zu stoppen, die jene Gemeinschaften zerstörte.

Dieses Projekt steht in scharfem Gegensatz zu Methoden wie der Tuskegee-Syphilisstudie oder der extraktiven sprachlichen Anthropologie, die BIPOC-Menschen als Versuchspersonen oder passive Lieferanten von Rohdaten behandeln. Wir sind nicht hier, um an indigenen Menschen zu experimentieren, ihr Wissen zu extrahieren oder ihnen eine westliche, kulturell monolithische Ideologie aufzuzwingen. Unser Ziel ist es, ihre *eigenen* Wege des Wissens und ihre *eigenen* Wertmaßstäbe zu unterstützen. Wir stellen die Infrastruktur bereit; die Sprachgemeinschaften erstellen die Testsätze, definieren die Metriken und erhalten die Zustimmung aufrecht. Ohne ihre Zustimmung funktioniert nichts davon.

### Warum diese Geschichte unser Design prägt

Deshalb ist das Governance-Modell von champollion kein Feature – es ist das Fundament. Jede wichtige Designentscheidung im Projekt ist eine *direkte Reaktion* auf die oben beschriebene Geschichte. Das Ziel ist die Datensouveränität: Gemeinschaften dabei zu unterstützen, ihre lebendigen Sprachen vollständig nach ihren eigenen Bedingungen zu erhalten, zu revitalisieren und zu verwalten.

**Warum die Testdaten verschlüsselt sind und von Gemeinschaftstreuhandstellen gehalten werden.** Weil indigene Sprachdaten seit über einem Jahrhundert ohne Zustimmung extrahiert, veröffentlicht und ausgebeutet wurden. Die missionarische Linguistik, wie die Bemühungen des Summer Institute of Linguistics (SIL), monopolisierte historisch indigene Parallelkorpora unter einem extraktiven, assimilatorischen Rahmenwerk. Darüber hinaus verwenden wir, anders als viele moderne NLP-Projekte, die sich für ressourcenarme Sprachen stark auf übersetzte Bibeln als ihr primäres Parallelkorpus stützen, ausdrücklich keine übersetzten Bibeln als Korpora. Der verschlüsselte Testsatz, mit Schlüsseln, die nur von der Governance-Organisation der Gemeinschaft gehalten werden, ist ein technischer Mechanismus, der es *architektonisch unmöglich* macht, extraktive Muster zu wiederholen.

**Warum wir Sandbox-Ausführung statt offener Testsätze verwenden.** Weil die Gemeinschaft, sobald sprachliche Daten offen veröffentlicht werden, dauerhaft die Kontrolle darüber verliert. Konventionelle ML-Benchmarks veröffentlichen ihre Testsätze – jeder kann sie herunterladen, darauf trainieren oder sie für jeden beliebigen Zweck verwenden. Dieses moderne Scraping von KI-Daten stellt eine neue Form von „Datenkolonialismus" und „digitaler Einhegung" dar. Für Gemeinschaften, deren Sprachen durch Gewalt fast ausgerottet wurden, ist der Verlust der Kontrolle über ihre verbleibenden sprachlichen Ressourcen keine geringfügige Unannehmlichkeit. Es ist eine direkte Fortsetzung der historischen territorialen Enteignung. Die Sandbox-Ausführung stellt sicher, dass die Daten der Gemeinschaft niemals ihre Infrastruktur verlassen.

**Warum das Eigentum an der Methode an die Gemeinschaft übergeht.** Weil die Geschichte des „Helfens" indigener Gemeinschaften überwältigend eine Geschichte von Außenstehenden ist, die Dinge *über* indigene Menschen bauen, statt *für* oder *mit* ihnen. Akademische Aufsätze werden veröffentlicht, Fördermittel werden eingesammelt, Karrieren werden vorangetrieben – und die Gemeinschaft bleibt mit nichts zurück. Der Mechanismus der Eigentumsübertragung stellt sicher, dass, wenn ein ML-Ingenieur eine funktionierende Übersetzungsmethode für das Plains Cree baut, die Plains-Cree-Gemeinschaft *diese Methode besitzt*. Der Ingenieur behält die Anerkennung und Zuschreibung. Die Gemeinschaft behält das Gut.

**Warum das Einnahmemodell 90 % an die Gemeinschaft sendet.** Weil Sprachrevitalisierung teuer ist und die Gemeinschaften, die die härteste Arbeit leisten – die lehrenden Ältesten, die Eltern, die ihre Kinder in Immersionsschulen schicken, die Aktivisten, die Sprachnester betreiben –, chronisch unterfinanziert sind. Darüber hinaus fordert die KI-Infrastruktur selbst, die wir verwenden (z. B. Rechenzentren, Mineralienabbau, Wasserverbrauch), einen unverhältnismäßigen materiellen Tribut von indigenem Land weltweit. Wenn eine Cree-Übersetzungs-API Einnahmen generiert, sollten 90 % dieser Einnahmen Cree-Sprachprogramme finanzieren. Technologie sollte ein Werkzeug sein, das Gemeinschaften dient, kein Mechanismus, der Wert aus ihnen extrahiert.

**Warum wir „OCAP®-forward" statt „OCAP®-konform" sagen.** Die OCAP®-Prinzipien (Ownership, Control, Access, Possession) wurden vom First Nations Information Governance Centre speziell für Kontexte der First Nations entwickelt. Andere Rahmenwerke der indigenen Datenverwaltung – CARE (Collective Benefit, Authority to Control, Responsibility, Ethics), Te Mana Raraunga (Māori-Datensouveränität) und die FAIR-Prinzipien – behandeln ähnliche Anliegen aus verschiedenen kulturellen und rechtlichen Positionen. Wir beanspruchen nicht, OCAP® vollständig umzusetzen; diese Entscheidung gehört den Gemeinschaften der First Nations. Wir sagen, unser Design ist *OCAP®-forward*: Es ist so gebaut, dass Gemeinschaften Eigentum, Kontrolle, Zugang und Besitz über ihre Daten und die daraus abgeleiteten Technologien *ausüben können*. Die Architektur ermöglicht Souveränität. Ob sie Souveränität erreicht, ist von den Gemeinschaften zu entscheiden.

**Warum die Plattform *Methoden* und nicht *Modelle* benchmarkt.** Weil indigene Sprachgemeinschaften nicht vom Modell eines einzelnen Unternehmens abhängig sein sollten. Die offene Architektur einer „Methode" bedeutet, dass die Lösung nicht einmal ein kostspieliges, materialintensives LLM sein muss. Es könnte ein hocheffizientes, von der Gemeinschaft gehostetes regelbasiertes System sein, das auf traditioneller Computerhardware läuft. Wenn die beste Übersetzungsmethode für Cree heute Googles Gemini verwendet, sollte die Gemeinschaft morgen zu einer Open-Source- oder deterministischen Alternative wechseln können, ohne alles neu aufbauen zu müssen. Benchmarking auf Methodenebene stellt sicher, dass das Gut der Gemeinschaft ein *Rezept* ist, keine Abhängigkeit.

**Warum die Gemeinschaft diese Infrastruktur jetzt aufbauen muss.** Das Paradoxon, KI zu nutzen und gleichzeitig ihre materielle Extraktion zu kritisieren, wird durch eine harte strategische Realität aufgelöst: Wenn dieses Problem nicht von der Gemeinschaft zu ihren eigenen souveränen Bedingungen gelöst wird, wird es unweigerlich von Big Tech (Google, Meta, OpenAI) zu extraktiven Bedingungen „gelöst" werden. Selbst wenn ein riesiges Unternehmen schließlich ein Übersetzungsmodell für eine gegebene indigene Sprache baut, benötigt die Gemeinschaft ihre eigene unabhängige, in einer Sandbox betriebene Benchmarking-Infrastruktur, um zu überprüfen, *wann* und *ob* sie nach den Maßstäben der Gemeinschaft tatsächlich erfolgreich waren – und um sicherzustellen, dass die Gemeinschaft den Wert dieses Erfolgs erfasst.

Dies ist keine Politik, die auf Technologie aufgeschraubt wird. Es ist Technologie, die von Menschen entworfen wurde, die die Geschichte verstehen.

---

## VI. Der gegenwärtige Moment: 6.800 zurückgelassene Sprachen

### Das Ausmaß des Problems

Von den rund 7.000 lebenden Sprachen, die heute auf der Erde gesprochen werden, haben weniger als 200 überhaupt irgendeine maschinelle Übersetzungsunterstützung. Die verbleibenden 6.800+ sind für die Technologie unsichtbar – nicht weil sie weniger wert sind, sondern weil die statistischen und neuronalen Ansätze, die die moderne MT dominieren, grundlegend *datenhungrig* sind. Sie benötigen Millionen von parallelen Sätzen, aus denen sie lernen können. Für die meisten Sprachen der Welt existieren diese Sätze nicht.

Die am stärksten betroffenen Sprachen sind genau jene, die am stärksten gefährdet sind: indigene Sprachen, Minderheitensprachen, mündliche Traditionen mit begrenzten schriftlichen Aufzeichnungen. Dies sind Sprachen, deren Sprecher oft betagt sind, deren Gemeinschaften klein sind, deren politische Macht minimal ist. Es sind die Sprachen, die technologische Unterstützung für Bewahrung und Revitalisierung am dringendsten benötigen – und es sind die Sprachen, für die die vorhandene Technologie am wenigsten nützlich ist.

### Die polysynthetische Herausforderung

Das Problem ist nicht bloß eines der Datenknappheit. Viele der am stärksten gefährdeten Sprachen der Welt sind *polysynthetisch* – sie haben morphologische Systeme von außerordentlicher Komplexität, die die Annahmen der Standard-NLP grundlegend durchbrechen.

Man betrachte das Plains Cree (nêhiyawêwin), eine Algonkin-Sprache, die in den kanadischen Prärien gesprochen wird. Ein einziges Cree-Verb kann Informationen kodieren, die das Englische über eine ganze Phrase verteilen würde: das Subjekt, das Objekt, das Tempus, den Aspekt, die Evidentialität, die Modalität und verschiedene andere grammatikalische Kategorien, alle in einem einzigen Wort verpackt durch ein System von Präfixen, Suffixen und internen Modifikationen.

Dies schafft mehrere Probleme für Standard-MT-Ansätze:

1. **Tokenisierungsversagen.** Subwort-Tokenizer wie BPE (Byte Pair Encoding), entworfen für analytische Sprachen wie das Englische, zerschmettern polysynthetische Wörter in bedeutungslose Fragmente. Die morphologische Struktur wird zerstört, bevor das Modell sie jemals sieht. BPE ist nicht neutral; es repräsentiert eine rein empiristische, oberflächliche Erkenntnistheorie, die grundlegend mit den tiefen, regelbasierten morphologischen Hierarchien kollidiert, die polysynthetischen Sprachen innewohnen. Es ist eine architektonische Voreingenommenheit, die strukturelle Morphologie aktiv zerlegt.

2. **Kombinatorische Explosion.** Eine polysynthetische Sprache kann Millionen möglicher Wortformen für eine einzige Verbwurzel haben. Kein Trainingskorpus, wie groß auch immer, kann mehr als einen winzigen Bruchteil davon enthalten. Neuronale Modelle haben keine Möglichkeit, auf ungesehene Formen zu *generalisieren*.

3. **Halluzination.** Große Sprachmodelle erzeugen, wenn sie aufgefordert werden, in polysynthetische Sprachen zu übersetzen, oft morphologisch ungültige Formen – Wörter, die kein Muttersprachler jemals produzieren würde. Das Modell hat statistische Muster aus begrenzten Daten gelernt, hat aber kein Verständnis der morphologischen Regeln der Sprache.

### Finite-State-Transduktoren: Die Brücke

Es gibt jedoch eine Technologie, die morphologische Komplexität *gut* handhabt: den **Finite-State-Transduktor** (FST). Ein FST ist ein formales rechnerisches Gerät, das durch eine Reihe von Zustandsübergängen zwischen einer Eingabezeichenkette und einer Ausgabezeichenkette abbildet. Für die morphologische Analyse kann ein FST eine Oberflächenwortform auf ihre zugrunde liegende morphologische Struktur abbilden (und umgekehrt) und dabei die volle kombinatorische Komplexität der Morphologie der Sprache handhaben.

FSTs sind die direkten Nachkommen von Pāṇinis Ersetzungsregeln. Sie sind Chomskys Typ-3-Grammatiken (regulär) in rechnerischer Form. Sie sind die lebendige Verkörperung der Verbindung zwischen formaler Sprachwissenschaft und Berechnung.

Durch die Kopplung von FSTs mit LLMs vollzieht `champollion` eine entscheidende philosophische Synthese: Es versöhnt die *rationalistische* strukturalistische Tradition (Regeln) mit dem *empiristischen* statistischen Paradigma (Wahrscheinlichkeit), um den datenhungrigen, mehrheitsorientierten Voreingenommenheiten der modernen KI entgegenzuwirken.

Für polysynthetische Sprachen können FSTs etwas bieten, das neuronale Modelle nicht können: *deterministische Verifikation*. Bei einer gegebenen Wortform kann ein FST definitiv sagen, ob sie eine gültige Form in der Sprache ist – nicht probabilistisch, nicht „das sieht richtig aus", sondern *ja* oder *nein*. Dies ist die Antwort auf die Kernfrage, die die neuronale MT für ressourcenarme Sprachen heimsucht: *Wie verifiziert man, dass ein erzeugtes Wort echt ist, ohne einen Menschen in der Schleife?*

Die technische Antwort lautet: Man verwendet die formale Grammatik. Man verwendet genau die Werkzeuge, die Pāṇini vor fünfundzwanzig Jahrhunderten erfand, kodiert in dem rechnerischen Formalismus, den Turing und Chomsky rigoros machten.

Wir müssen jedoch anerkennen, dass diese deterministische Macht ihre eigenen Risiken birgt. Eine „Ja"- oder „Nein"-Validierung einer mündlichen, fließenden Sprache aufzuzwingen, läuft Gefahr, eine starre Standardsprachenideologie aufzuerlegen. Wenn ein FST diktiert, was „korrekt" ist, kann er unbeabsichtigt genau die koloniale Normativität rekapitulieren, die er umgehen sollte – indem er dialektale Variation einebnet, Code-Switching bestraft und einer vielfältigen Gemeinschaft eine einzige, normalisierte Grammatik aufzwingt. Weil FSTs nur eine Metrik formaler Korrektheit darstellen, muss ihr starrer Empirismus gemildert werden. Genau deshalb muss die Gemeinschaft die Feder halten. Die Gemeinschaft setzt den Standard, baut die Regeln und definiert, was die Maschine als gültig akzeptiert, indem sie FSTs konstruiert, die Raum für mündliche Fließfähigkeit und regionale Dialekte schaffen. Die formale Grammatik ist keine universelle Wahrheit, die von Informatikern überliefert wird; sie ist eine Infrastruktur, die von den Sprechern selbst betrieben wird.

### champollion: Wo die Stränge zusammenlaufen

Hier tritt das champollion-Projekt in die Geschichte ein. Es sitzt genau am Konvergenzpunkt all der Stränge, die wir verfolgt haben:

- **Von Pāṇini**: Das Prinzip, dass Sprache durch formale, generative Regeln beschrieben werden kann.
- **Von Schleicher und Sapir**: Das Verständnis, dass die Sprachen der Welt vielfältig, strukturiert und oft gefährdet sind.
- **Von den Residential Schools und ihren Nachwirkungen**: Das Verständnis, dass „Datenknappheit" keine neutrale technische Tatsache ist, sondern die Folge gezielter Sprachunterdrückung – und dass jede Technologie, die diese Sprachen berührt, mit Souveränität als Fundament gebaut werden muss.
- **Von Chomsky**: Die formale Hierarchie der Grammatiken, die Sprachwissenschaft mit Berechnung verbindet.
- **Von Shannon**: Das mathematische Rahmenwerk zum Verständnis von Kommunikation, Rauschen und Signal.
- **Von Turing und von Neumann**: Die universellen Maschinen, die jede berechenbare Funktion ausführen können.
- **Von Weaver und den IBM-Modellen**: Die Erkenntnis, dass Übersetzung als statistisches Problem behandelt werden kann.
- **Von der Transformer-Revolution**: Die mächtigen neuronalen Modelle, die übersetzen können – aber nur, wenn sie genügend Daten haben.
- **Von der FST-Tradition**: Die formalen Werkzeuge, die morphologische Komplexität handhaben können, wo neuronale Modelle versagen.
- **Von OCAP®, CARE und Te Mana Raraunga**: Die Governance-Rahmenwerke, die sicherstellen, dass Technologie Gemeinschaften dient, anstatt aus ihnen zu extrahieren.

champollion ist eine Plattform, die darauf ausgelegt ist, die wettbewerbsorientierte Energie der Machine-Learning-Gemeinschaft auf Sprachen zu lenken, die der Markt aufgegeben hat. Sie stellt eine Benchmarking-Infrastruktur bereit, bei der jeder eine Übersetzungsmethode einreichen kann – neuronal, regelbasiert, hybrid oder neuartig – und sie anhand rigoroser Standards bewerten lassen kann. Entscheidend ist, dass sie FST-basierte Validierung verwendet, um sicherzustellen, dass erzeugte Formen morphologisch gültig sind, und sie stützt sich auf die Verifikation durch Muttersprachler als ultimative Grundwahrheit.

Die Plattform verkörpert mehrere Prinzipien, die diese Geschichte deutlich macht:

**Kein einzelner Ansatz ist ausreichend.** Die Geschichte der MT ist eine Geschichte von Paradigmenwechseln – von Regeln zu Statistik zu neuronalen Netzen. Jedes neue Paradigma löste Probleme, die das vorherige nicht konnte, doch jedes hatte auch blinde Flecken. Für ressourcenarme polysynthetische Sprachen ist die Antwort mit ziemlicher Sicherheit *hybrid*: neuronale Sprachgewandtheit, eingeschränkt durch formale Korrektheit.

**Datensouveränität ist nicht optional – sie ist eine strukturelle Reaktion auf historischen Schaden.** Wie Abschnitt V im Detail dokumentiert, sind indigene Sprachen nicht bloß zufällig „datenarm". Sie wurden durch gezielte Politik knapp gemacht. Das OCAP®-forward-Design des Projekts – das sicherstellt, dass Sprachdaten unter der Kontrolle indigener Gemeinschaften bleiben, dass Entschlüsselungsschlüssel von Gemeinschaftstreuhandstellen gehalten werden, dass das Eigentum an Algorithmen an die Sprecher übergeht – ist kein nachträglicher Einfall. Es ist eine direkte Reaktion auf Jahrhunderte extraktiver Praxis, von der Dokumentation durch Außenstehende in der Ära der Residential Schools bis zum heutigen Scraping von Datensätzen. Die Architektur macht es *technisch unmöglich*, diese Muster zu wiederholen.

**Das Langzeitspiel ist Revitalisierung.** Übersetzung ist das *Erprobungsfeld*, doch der wahre Preis ist die Sprachrevitalisierung durch Lehre. Die formalen Grammatiken und morphologischen Modelle, die für die maschinelle Übersetzung gebaut wurden, sind genau die technischen Grundlagen, die für maschinengestütztes Sprachenlernen benötigt werden. Wenn wir einen FST bauen können, der Cree-Verbformen für ein Übersetzungssystem validiert, können wir diesen FST auch verwenden, um einem Schüler zu helfen, zu lernen, Cree-Verben zu konjugieren.

### Warum dieser Moment

Wir leben in einem einzigartigen Moment in der Geschichte der Sprachtechnologie. Mehrere Faktoren sind zusammengelaufen:

1. **Open-Source-Werkzeuge sind ausgereift.** Die FST-Toolkits (wie HFST und Foma), die neuronalen MT-Frameworks (wie OpenNMT und Fairseq) und die Evaluierungsinfrastruktur können nun von einem kleinen Team zu minimalen Kosten zusammengestellt werden.

2. **Die Organisierung der Gemeinschaften beschleunigt sich.** Indigene Sprachgemeinschaften werden in ihrer Nutzung von Technologie und ihrer Behauptung der Datensouveränität zunehmend versierter. Organisationen wie die First-Voices-Initiative, das Canadian Indigenous Languages Technology Project und zahlreiche von Gemeinschaften geführte Bemühungen bauen die menschliche Infrastruktur auf, die Technologie allein nicht bieten kann.

3. **Die KI-Fähigkeiten haben eine Schwelle erreicht.** Große Sprachmodelle können, obwohl sie allein für ressourcenarme MT unzureichend sind, als mächtige Komponenten in hybriden Systemen dienen – sie erzeugen Kandidatenübersetzungen, die dann durch formale Methoden verifiziert und eingeschränkt werden.

4. **Die Kosten sind zusammengebrochen.** Was 1954 ein Regierungslabor oder im Jahr 2000 ein großes Unternehmen erfordert hätte, kann nun mit Cloud-Computing-Guthaben und Open-Source-Software erledigt werden. Der Engpass ist nicht mehr Technologie oder Geld. Es ist der *Wille*.

Die Frage ist nicht, ob die Technologie gebaut werden kann. Sie kann es. Die Frage ist, ob sie *richtig* gebaut wird – mit der richtigen Governance, den richtigen Anreizen und dem richtigen Respekt für die Gemeinschaften, denen sie dienen soll.

Das ist die Frage, zu deren Beantwortung dieses Projekt existiert.

---

## Literaturverzeichnis

- Bahdanau, D., Cho, K., & Bengio, Y. (2015). Neural Machine Translation by Jointly Learning to Align and Translate. *ICLR*.
- Boole, G. (1854). *An Investigation of the Laws of Thought*. Walton and Maberly.
- Bringing Them Home: Report of the National Inquiry into the Separation of Aboriginal and Torres Strait Islander Children from Their Families. (1997). Australian Human Rights Commission.
- Brown, P., Della Pietra, S., Della Pietra, V., & Mercer, R. (1993). The Mathematics of Statistical Machine Translation. *Computational Linguistics*, 19(2).
- Campbell, L. (1997). *American Indian Languages: The Historical Linguistics of Native America*. Oxford University Press.
- Champollion, J.-F. (1822). *Lettre à M. Dacier relative à l'alphabet des hiéroglyphes phonétiques*.
- Chomsky, N. (1957). *Syntactic Structures*. Mouton.
- Chomsky, N. (1956). Three Models for the Description of Language. *IRE Transactions on Information Theory*, 2(3).
- Huet, G. (2006). Lexicon-directed Segmentation and Tagging of Sanskrit. In *Proceedings of the XIIth World Sanskrit Conference*.
- Jones, W. (1786). The Third Anniversary Discourse. *Asiatick Researches*, 1.
- Kiparsky, P. (1993). Paninian Linguistics. In R. E. Asher (Ed.), *The Encyclopedia of Language and Linguistics*. Pergamon.
- Kircher, A. (1663). *Polygraphia Nova et Universalis*.
- Leibniz, G. W. (1703). Explication de l'Arithmétique Binaire. *Mémoires de l'Académie Royale des Sciences*.
- Llull, R. (c. 1305). *Ars Magna*.
- Lovelace, A. (1843). Notes by the Translator (Note G). In L. F. Menabrea, *Sketch of the Analytical Engine Invented by Charles Babbage*.
- Marmion, D., Obata, K., & Troy, J. (2014). *Community, Identity, Wellbeing: The Report of the Second National Indigenous Languages Survey*. Australian Institute of Aboriginal and Torres Strait Islander Studies.
- National Research Council. (1966). *Language and Machines: Computers in Translation and Linguistics* (ALPAC Report). National Academy of Sciences.
- Papineni, K., Roukos, S., Ward, T., & Zhu, W.-J. (2002). BLEU: A Method for Automatic Evaluation of Machine Translation. *ACL*.
- Saussure, F. de. (1916). *Cours de linguistique générale* (C. Bally & A. Sechehaye, Eds.). Payot.
- Schleicher, A. (1861). *Compendium der vergleichenden Grammatik der indogermanischen Sprachen*.
- Shannon, C. E. (1948). A Mathematical Theory of Communication. *Bell System Technical Journal*, 27(3).
- Shannon, C. E. (1951). Prediction and Entropy of Printed English. *Bell System Technical Journal*, 30(1).
- Sutskever, I., Vinyals, O., & Le, Q. V. (2014). Sequence to Sequence Learning with Neural Networks. *NeurIPS*.
- Truth and Reconciliation Commission of Canada. (2015). *Honouring the Truth, Reconciling for the Future: Summary of the Final Report*. Government of Canada.
- Turing, A. M. (1936). On Computable Numbers, with an Application to the Entscheidungsproblem. *Proceedings of the London Mathematical Society*, 2(42).
- Turing, A. M. (1950). Computing Machinery and Intelligence. *Mind*, 59(236).
- Vaswani, A., et al. (2017). Attention Is All You Need. *NeurIPS*.
- von Neumann, J. (1945). *First Draft of a Report on the EDVAC*. University of Pennsylvania.
- Weaver, W. (1949). Translation. Memorandum, Rockefeller Foundation.
- Wilkins, J. (1668). *An Essay towards a Real Character, and a Philosophical Language*. Royal Society.
- U.S. Department of the Interior. (2022). *Federal Indian Boarding School Initiative Investigative Report*. Bureau of Indian Affairs.

---

*Dieses Dokument ist Teil der Dokumentation des champollion-Projekts. Es wird unter derselben Lizenz wie das Projekt selbst veröffentlicht.*