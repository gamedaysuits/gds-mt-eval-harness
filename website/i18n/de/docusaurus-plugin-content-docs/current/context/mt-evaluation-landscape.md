---
sidebar_position: 3
title: "Das Unermessliche messen"
---
# Das Unermessliche messen: Das Evaluierungsproblem in der maschinellen Übersetzung

**Ein Überblick darüber, wie das Fachgebiet die Übersetzungsqualität misst, wo es daran scheitert und was LYSS (Linguistically-informed Yield & Structural Scoring) als Alternative bietet**

---

> *„Automatische Metriken sind eine bequeme Lüge. Sie geben uns eine Zahl, und die Zahl erlaubt es uns, ein Paper zu schreiben, und das Paper erlaubt es uns, Fortschritt zu behaupten. Ob tatsächlich Fortschritt stattgefunden hat, ist eine andere Frage."*
> — Adaptiert von einer wiederkehrenden Stimmung bei den WMT Metrics Shared Tasks

---

## Einleitung

Die maschinelle Übersetzung hat ein Messproblem.

Das Fachgebiet hat zwei Jahrzehnte damit verbracht, zunehmend ausgefeilte Systeme zu entwickeln — von Phrasentabellen über Aufmerksamkeitsmechanismen bis hin zu Sprachmodellen mit Billionen von Parametern — und während dieses gesamten Bogens hat es mit einer trügerisch einfachen Frage gerungen: *Woher weiß man, ob eine Übersetzung gut ist?*

Diese Frage ist nicht akademisch. Die Metrik, die Sie wählen, bestimmt, welches System „gewinnt". Sie bestimmt, was finanziert, was veröffentlicht, was eingesetzt wird und — für die Sprachen, die MT am dringendsten benötigen — ob die Übersetzungen einer Gemeinschaft als Fehlschläge beurteilt werden, obwohl sie in Wirklichkeit korrekt sind.

Die Geschichte der MT-Evaluierung ist im Kleinen eine Geschichte der Wertvorstellungen des Fachgebiets. Die Dominanz von BLEU über fast zwei Jahrzehnte hinweg offenbart eine Vorliebe für billige, schnelle, sprachunabhängige Messung gegenüber linguistisch fundierter Beurteilung. Der Aufstieg neuronaler Metriken wie COMET spiegelt die wachsende Reife des Fachgebiets wider — und seine fortgesetzte Abhängigkeit von englischzentrierten Trainingsdaten. Das nahezu vollständige Fehlen morphologiebewusster Evaluierung spiegelt ein Fachgebiet wider, das bis vor Kurzem von und für Sprecher analytischer europäischer Sprachen aufgebaut wurde.

Dieses Paper verfolgt die Entwicklung der MT-Evaluierung von BLEU bis heute, identifiziert, wo bestehende Ansätze für morphologisch komplexe und ressourcenarme Sprachen systematisch scheitern, und untersucht, wie eine linguistisch fundierte Alternative aussehen könnte. Es ist ein Begleitdokument zu den anderen Kontextdokumenten des Projekts — [*Von Pāṇini zu Transformers*](./history-of-language-and-computation.md) (das die intellektuelle Geschichte von Sprache und Computertechnik verfolgt) und dem [*Field Briefing*](./mt-field-briefing.md) (das die aktuelle MT-Landschaft überblickt). Wo jene Dokumente fragen „Wie sind wir hierhergekommen?" und „Was existiert?", fragt dieses: „Woher wissen wir, ob etwas davon funktioniert?"

---

## Teil 1: Die Ära des String-Matchings (2002–2015)

### BLEU und die Geburt der automatischen Evaluierung

Die moderne Ära der MT-Evaluierung beginnt mit einem einzigen Paper: Kishore Papineni, Salim Roukos, Todd Ward und Wei-Jing Zhus „BLEU: a Method for Automatic Evaluation of Machine Translation", veröffentlicht auf der ACL 2002. BLEU (Bilingual Evaluation Understudy) misst, wie stark die Wortsequenzen (n-Gramme) einer maschinellen Übersetzung mit einer oder mehreren menschlichen Referenzübersetzungen überlappen. Es enthält eine Kürzestrafe (brevity penalty), um zu verhindern, dass Systeme den Score mit kurzen Ausgaben manipulieren, und es berechnet ein geometrisches Mittel der n-Gramm-Präzisionen für die Ordnungen 1 bis 4.

BLEU wurde aus einem einfachen Grund zur Währung des Fachgebiets: Es war schnell, billig, reproduzierbar und sprachunabhängig. Vor BLEU erforderte die Evaluierung eines MT-Systems eine teure, langsame menschliche Beurteilung. BLEU bot eine Zahl, die in Millisekunden berechnet, über Papers hinweg verglichen und zur Rangordnung von Systemen in Shared Tasks verwendet werden konnte. Innerhalb weniger Jahre war es im Wesentlichen verpflichtend — ein Paper ohne BLEU-Scores war nicht veröffentlichbar.

Doch BLEU weist tiefgreifende, gut dokumentierte Mängel auf, deren Umgehung das Fachgebiet zwei Jahrzehnte lang versucht hat:

**Kein semantisches Verständnis.** BLEU ist reines Oberflächen-Matching. „The cat sat on the mat" erhält null gegenüber einer Referenz „the feline rested on the rug". Jedes Wort ist ein korrektes Synonym; die Bedeutung ist identisch; der Score ist null.

**Morphologische Blindheit.** Für agglutinierende und polysynthetische Sprachen scheitert striktes Matching auf Wortebene katastrophal. Ein korrekt konjugiertes Cree-Verb, das sich um ein Morphem von der Referenz unterscheidet, erhält null — selbst wenn der Unterschied ein grammatikalisch optionales Partikel oder eine ebenso gültige Wortstellung ist.

**Schlechte Diskriminierung auf Satzebene.** BLEU wurde als Metrik auf Korpusebene konzipiert. Auf Satzebene ist es verrauscht und unzuverlässig — dennoch wird es routinemäßig auf einzelne Sätze angewendet.

**Verzerrung durch Einzelreferenz.** BLEU geht davon aus, dass es *eine* korrekte Übersetzung (oder einen kleinen Satz von Referenzen) gibt. Für Sprachen mit freier Wortstellung, synonymreichem Wortschatz oder systematischen Mehrdeutigkeiten (wie Crees inklusivem/exklusivem „wir") kann es Dutzende gleichermaßen korrekter Übersetzungen geben, und BLEU bestraft alle bis auf diejenige, die zufällig mit der Referenz übereinstimmt.

**Schwache Korrelation mit menschlichem Urteil.** Metaanalysen — insbesondere Reiter (2018, *Computational Linguistics*) — haben gezeigt, dass die Korrelation von BLEU mit menschlichen Qualitätsbeurteilungen oft schwach ist, insbesondere bei hochwertigen Systemen und bei Sprachen, die weit vom Englischen entfernt sind.

Diese Mängel waren fast von Anfang an bekannt. Dennoch hielt sich BLEU, weil die Alternativen schlechter waren — nicht in der Genauigkeit, sondern in der Bequemlichkeit. Das Fachgebiet optimierte für die Metrik, die es berechnen konnte, nicht für die Metrik, die es brauchte.

### NIST (Doddington, 2002)

Die NIST-Metrik, im selben Jahr wie BLEU von George Doddington auf der HLT 2002 veröffentlicht, modifizierte die BLEU-Formel auf zwei Arten. Erstens gewichtete sie n-Gramme nach ihrem **Informationsgehalt** — seltene n-Gramme erhielten ein höheres Gewicht als häufige, basierend auf der Intuition, dass die korrekte Übersetzung einer ungewöhnlichen Phrase informativer ist als die korrekte Übersetzung von „of the". Zweitens verwendete sie ein **arithmetisches Mittel** anstelle des geometrischen Mittels von BLEU, was zu stabileren Scores führte, die nicht auf null fielen, wenn eine einzelne n-Gramm-Ordnung keine Übereinstimmungen aufwies. NIST wurde umfangreich in den DARPA-TIDES- und NIST-OpenMT-Evaluierungsprogrammen verwendet, erreichte aber nie die Dominanz von BLEU in der breiteren Forschungsgemeinschaft. Trotz seiner Verbesserungen teilte es die grundlegende Beschränkung von BLEU: String-Matching auf Oberflächenebene ohne ein Konzept von Bedeutung.

### METEOR (Banerjee & Lavie, 2005)

METEOR (Metric for Evaluation of Translation with Explicit ORdering) war ein früher Versuch, die Starrheit von BLEU zu adressieren. Während BLEU exaktes Wort-Matching durchführt, führte METEOR drei Neuerungen ein:

1. **Stemming**: Wörter werden vor dem Vergleich auf ihre Stämme reduziert, was morphologischen Varianten Teilanrechnung gewährt (z. B. passt „running" nach dem Stemming zu „ran").
2. **Synonym-Matching**: Mithilfe von WordNet erkennt METEOR, dass „car" und „automobile" dasselbe Konzept sind.
3. **Wort-Alignment**: Anstatt n-Gramm-Überlappungen zu zählen, richtet METEOR Wörter zwischen Hypothese und Referenz explizit aus und berechnet dann Präzision und Recall mit einer Fragmentierungsstrafe.

METEOR zeigte durchweg eine höhere Korrelation mit menschlichen Urteilen als BLEU. Es erforderte jedoch sprachspezifische Ressourcen (Stemmer, Synonymdatenbanken), die seine Anwendbarkeit einschränkten, und es war langsamer in der Berechnung. Für Englisch war es besser. Für ressourcenarme Sprachen existierten die Stemmer und Synonymdatenbanken schlichtweg nicht.

### TER (Snover et al., 2006)

Translation Edit Rate misst die minimale Anzahl von Bearbeitungen (Einfügungen, Löschungen, Substitutionen und *Phrasenverschiebungen*), die erforderlich sind, um die Hypothese in die Referenz zu transformieren, normalisiert auf die Referenzlänge. Die Phrasenverschiebungsoperation — das Verschieben einer zusammenhängenden Wortsequenz an eine andere Position — war eine direkte Anerkennung der Tatsache, dass die Wortstellung über Sprachen hinweg nicht festgelegt ist. Der Edit-Distance-Ansatz von TER ist intuitiv (er misst „wie viel Arbeit müsste ein menschlicher Post-Editor leisten?"), erbt jedoch dieselbe grundlegende Beschränkung: Er vergleicht mit einer einzigen Referenz und hat kein Konzept von Bedeutung.

### chrF und chrF++ (Popović, 2015; 2017)

Die wichtigste Metrik-Innovation zwischen BLEU und der neuronalen Ära stammt von Maja Popović. **chrF** (character F-score) misst die Überlappung auf *Zeichen*ebene statt auf Wortebene und berechnet die Präzision und den Recall von Zeichen-n-Grammen. **chrF++** fügt Wort-Unigramme und -Bigramme wieder hinzu.

Warum dies für morphologisch reiche Sprachen von Bedeutung ist: Matching auf Zeichenebene gewährt *Teilanrechnung* für gemeinsame Morpheme. Die Cree-Wörter *nikî-nipâw* („ich schlief") und *kikî-nipâw* („du schliefst") teilen sich die meisten ihrer Zeichen-n-Gramme, obwohl sie unterschiedliche Wörter sind. chrF würde erhebliche Teilanrechnung gewähren; BLEU würde null gewähren.

chrF++ ist zu einer standardmäßigen sekundären Metrik bei den WMT Shared Tasks geworden, implementiert in **sacreBLEU** (Post, 2018), und gilt weithin als BLEU für morphologisch reiche Sprachen überlegen. Doch es bleibt eine String-Matching-Metrik — besser als BLEU, aber grundlegend durch dieselbe Annahme begrenzt, dass Übersetzungsqualität durch Überlappung von Oberflächenformen gemessen werden kann.

---

## Teil 2: Die Revolution der neuronalen Metriken (2018–Gegenwart)

### Die Erkenntnis: Das Scoring erlernen

Die String-Matching-Metriken aus Teil 1 teilen eine grundlegende Designentscheidung: Es sind handgefertigte Formeln. Jemand entschied, dass n-Gramm-Präzision, Zeichenüberlappung oder Edit-Distance ein guter Indikator für Übersetzungsqualität sei, und dann verwendete jeder diese Formel ein Jahrzehnt lang.

Die Revolution der neuronalen Metriken begann mit einer anderen Frage: *Was wäre, wenn wir ein Modell trainieren würden, um die Übersetzungsqualität vorherzusagen, so wie wir Modelle zum Übersetzen trainieren?*

### BERTScore (Zhang et al., 2020)

BERTScore, 2020 auf der ICLR von Tianyi Zhang und Kollegen an der Cornell und am MIT veröffentlicht, war die erste weithin übernommene Metrik, die die Evaluierung vom exakten String-Matching zur semantischen Ähnlichkeit verlagerte. Der Mechanismus ist elegant: Sowohl die Hypothese als auch die Referenz werden durch ein vortrainiertes Transformer-Modell (BERT, RoBERTa oder DeBERTa) kodiert, die Kosinusähnlichkeit zwischen jedem Paar von Token-Embeddings wird berechnet, und dann wird Greedy-Matching verwendet, um Präzision (beste Übereinstimmung jedes Hypothesen-Tokens in der Referenz), Recall (beste Übereinstimmung jedes Referenz-Tokens in der Hypothese) und F1 zu berechnen.

BERTScore behandelt Synonyme, Paraphrasen und Wortstellungsvariationen auf natürliche Weise — „the feline rested on the rug" erhält eine hohe Ähnlichkeit zu „the cat sat on the mat", weil die kontextuellen Embeddings semantische Äquivalenz erfassen. Mit mehrsprachigem BERT erstreckt es sich auf jede Sprache, die das Modell abdeckt.

Doch BERTScore wird nicht *auf* menschlichen Qualitätsurteilen *trainiert*. Es verwendet vortrainierte Embeddings unverändert, was bedeutet, dass es allgemeine semantische Ähnlichkeit erfasst, anstatt speziell zu lernen, was eine *Übersetzung* gut macht. Diese Unterscheidung ist von Bedeutung: Ein Satz kann einer Referenz semantisch ähnlich sein und dennoch eine schlechte Übersetzung darstellen (falsches Register, ausgelassene Negation, halluziniertes Attribut). BERTScore erbt zudem etwaige Sprachverzerrungen, die im zugrunde liegenden Modell existieren — für Sprachen, die in den Trainingsdaten von BERT unterrepräsentiert sind, erfassen die Embeddings möglicherweise keine bedeutungsvollen Unterscheidungen.

### BLEURT (Sellam et al., 2020)

BLEURT (Bilingual Evaluation Understudy with Representations from Transformers), 2020 auf der ACL von Thibault Sellam, Dipanjan Das und Ankur Parikh bei Google veröffentlicht, führte eine zentrale Neuerung ein: **Vortraining auf synthetischen Perturbationen** vor dem Fine-Tuning auf menschlichen Urteilen. Die Erkenntnis war, dass das direkte Fine-Tuning eines Sprachmodells auf den kleinen WMT-Datensätzen menschlicher Urteile zu einer Metrik führte, die brüchig war — sie überangepasst (overfit) sich an die spezifischen Muster in den Trainingsdaten und versagte bei Eingaben außerhalb der Verteilung.

BLEURTs Lösung war ein zweiphasiges Trainingsrezept. In Phase eins wurden Millionen synthetischer Satzpaare durch zufällige Wortlöschungen, -einfügungen, -substitutionen und Rückübersetzung erzeugt. Das Modell wurde darauf trainiert, bestehende automatische Metrik-Scores (BLEU, ROUGE, BERTScore, Entailment) für diese Paare vorherzusagen — und lernte so allgemeine Vorstellungen von Textähnlichkeit. In Phase zwei wurde das vortrainierte Modell auf WMT-Direct-Assessment-Bewertungen feinabgestimmt. Dieses „Aufwärmen" verbesserte die Robustheit dramatisch.

BLEURT-20 erweiterte den Ansatz mithilfe von Googles RemBERT-Encoder auf mehrsprachige Evaluierung. Doch BLEURT bleibt referenzbasiert — es verwendet nicht den Quelltext, was bedeutet, dass es keine Halluzinationen erkennen kann, die zufällig flüssig sind, und es hängt vollständig von der Qualität der Referenz ab.

### COMET (Rei et al., 2020)

COMET (Crosslingual Optimized Metric for Evaluation of Translation) repräsentiert den aktuellen Stand der Technik in der automatischen MT-Evaluierung. Entwickelt von Ricardo Rei und Kollegen bei **Unbabel**, verwendet COMET einen sprachübergreifenden Encoder (XLM-RoBERTa), um drei Eingaben — den Quellsatz, die MT-Hypothese und die Referenzübersetzung — einzubetten, und sagt einen Qualitäts-Score voraus, der auf menschlichen Direct-Assessment-Urteilen trainiert wurde.

COMET gewann oder belegte ab 2020 den ersten Platz bei den WMT Metrics Shared Tasks. Seine Korrelation mit menschlichem Urteil ist erheblich höher als die jeder String-Matching-Metrik. Es erkennt Paraphrasen, erfasst die Bedeutungserhaltung und behandelt Synonymvariationen, die BLEU vollständig übersieht.

Doch COMET hat für unsere Zwecke eine kritische Beschränkung: Es wird auf menschlichen Urteilen von WMT trainiert, die überwiegend in europäischen Sprachen vorliegen. Sein sprachübergreifender Encoder (XLM-R) wurde auf CommonCrawl-Daten trainiert, in denen Plains Cree, Nordsamisch und die meisten indigenen Sprachen im Wesentlichen abwesend sind. Für diese Sprachen sind die internen Repräsentationen von COMET unzuverlässig — es mag Scores erzeugen, aber diese Scores sind in keinem realen Verständnis der Struktur der Sprache fundiert.

### xCOMET (Guerreiro et al., 2024)

xCOMET, 2024 in den TACL von Nuno Guerreiro, Ricardo Rei und Kollegen bei Unbabel und am Instituto Superior Técnico veröffentlicht, erweiterte COMET von einem Black-Box-Scorer zu einem **Diagnosewerkzeug**. Die zentrale Neuerung ist Multi-Task-Learning: Neben dem Qualitäts-Score auf Satzebene führt xCOMET **Sequenz-Tagging auf Subwort-Ebene** durch, um spezifische Fehlerspannen in der Übersetzung zu identifizieren und sie als geringfügig, schwerwiegend oder kritisch zu klassifizieren.

Dies überbrückt die Lücke zwischen automatischem Scoring und MQM-artiger menschlicher Fehleranalyse. Anstatt nur zu berichten „diese Übersetzung erhält 0,73", kann xCOMET auf die spezifischen Wörter verweisen, die falsch sind, und angeben, wie schwerwiegend. Das Training verwendet einen Ansatz des Curriculum-Learnings: zunächst Training auf Direct-Assessment-Daten für die Regression auf Satzebene, dann Hinzufügung von MQM-annotierten Daten mit Fehlerspannen-Labels für das gemeinsame Training.

xCOMET erzielte gleichzeitig Spitzenleistungen bei der Evaluierung auf Satz-, System- und Spannenebene. Es funktioniert sowohl im referenzbasierten als auch im referenzfreien Modus. Doch es erfordert MQM-annotierte Trainingsdaten — deren Erstellung teuer ist und die überwiegend für europäische Sprachpaare existieren.

### AfriCOMET (Wang & Adelani, NAACL 2024)

AfriCOMET, 2024 auf der NAACL von Jiayi Wang, David Ifeoluwa Adelani und Kollegen in der Masakhane-Gemeinschaft veröffentlicht, ist der wichtigste Beweis dafür, dass neuronale Metriken für unterversorgte Sprachen angepasst werden *müssen* — sie generalisieren nicht von Haus aus.

Das Paper demonstrierte zunächst das Problem: Standard-COMET, trainiert auf WMT-Daten aus europäischen Sprachen, zeigte eine signifikant schwächere Korrelation mit menschlichen Urteilen, wenn es auf 13 afrikanische Sprachen (darunter Amharisch, Hausa, Igbo, Swahili, Yoruba und Zulu) angewendet wurde. Die Behebung erforderte zwei Änderungen. Erstens den Ersatz von XLM-R durch **AfroXLM-R**, einen sprachübergreifenden Encoder, der speziell darauf trainiert wurde, afrikanische Sprachen besser zu repräsentieren. Zweitens die Erstellung von **AfriMTE**, einem neuen menschlichen Evaluierungsdatensatz mit vereinfachten MQM-Richtlinien, die für Nicht-Experten-Annotatoren konzipiert wurden — denn es ist schwierig, professionelle zweisprachige Übersetzer für diese Sprachen zu finden.

AfriCOMET bewies das Konzept: Eine sprachfamilienspezifische neuronale Metrik kann die generische Version dramatisch übertreffen. Doch es bewies auch die Kosten: Jemand musste AfroXLM-R erstellen, menschliche Urteilsdaten für 13 Sprachen sammeln und ein neues Modell trainieren. Für Plains Cree existiert kein gleichwertiger Encoder, kein menschlicher Urteilsdatensatz und keine angepasste Metrik. Der AfriCOMET-Weg würde erfordern, all dies von Grund auf neu zu erstellen — ein mehrjähriges Unterfangen, das gemeinschaftsbasierte menschliche Evaluierung und wahrscheinlich einen dedizierten Encoder für die Algonkin-Sprachfamilie umfasst.

### GEMBA: LLM-as-Evaluator (Kocmi & Federmann, 2023)

GEMBA (GPT Estimation Metric Based Assessment), 2023 auf der EAMT von Tom Kocmi und Christian Federmann bei Microsoft veröffentlicht, stellte eine radikale Frage: Was, wenn man GPT-4 einfach *fragt*, ob eine Übersetzung gut sei?

Der Ansatz ist entwaffnend einfach. **GEMBA-DA** versorgt das LLM mit der Quelle und der Hypothese und bittet um eine Qualitätsbewertung auf einer Skala von 0–100. **GEMBA-MQM** liefert drei annotierte Beispiele und bittet das LLM, spezifische Fehlerspannen zu identifizieren, sie nach Typ und Schweregrad zu klassifizieren und einen MQM-artigen Score zu erzeugen. Es ist kein metrikspezifisches Training erforderlich.

Die Ergebnisse waren bemerkenswert: Auf Systemebene erzielte GEMBA eine wettbewerbsfähige oder dem Stand der Technik entsprechende Korrelation mit menschlichen Urteilen. Die Fehlerannotationen von GEMBA-MQM lieferten, wenngleich nicht so zuverlässig wie menschliche Annotatoren, interpretierbare diagnostische Informationen ganz ohne spezialisiertes Training.

Doch GEMBA wirft ernsthafte Bedenken auf. Es hängt von proprietären Closed-Source-Modellen ab, deren Verhalten sich zwischen API-Versionen ändert. Die Ergebnisse sind im strengen Sinne nicht reproduzierbar. Es ist im großen Maßstab teuer (API-Kosten für die Evaluierung eines vollständigen WMT-Testsets). Und — entscheidend für unsere Zwecke — das Wissen des LLM über ressourcenarme Sprachen ist ungewiss. GPT-4 versteht die Morphologie von Plains Cree möglicherweise gut genug, um Übersetzungen zu evaluieren, oder auch nicht; ohne Tests lässt sich das nicht feststellen, und es gibt keine Garantie, dass das Verhalten über Modellaktualisierungen hinweg konsistent bleibt. Kocmi und Federmann selbst rieten aufgrund der Black-Box-Natur der Evaluierung davon ab, GEMBA zu verwenden, um Verbesserungen in akademischen Papers zu behaupten.

### MetricX und der WMT 2024 Metrics Shared Task

**MetricX-24**, entwickelt von Juraj Juraska, Daniel Deutsch, Mara Finkelstein und Markus Freitag bei Google, gewann den WMT 2024 Metrics Shared Task. Aufgebaut auf **mT5** (Multilingual T5, ein Encoder-Decoder-Modell statt des von COMET verwendeten Encoder-only XLM-R) verfolgt MetricX einen anderen architektonischen Weg. Es verwendet zweistufiges Fine-Tuning — zunächst auf Direct-Assessment-Daten, dann auf MQM-Scores — mit umfangreicher **synthetischer Datenaugmentierung**, die auf bekannte Fehlermodi von Metriken abzielt (Unterübersetzung, flüssige-aber-falsche Übersetzungen, Halluzinationen).

Das WMT-2024-Befundpaper mit dem Titel **„Are LLMs Breaking MT Metrics?"** fragte, ob LLM-generierte Übersetzungen das Metrik-Ökosystem zerbrochen hätten. Die Antwort war ein qualifiziertes Nein: Feinabgestimmte neuronale Metriken (MetricX-24, COMET-Varianten) blieben wirksam, obwohl LLM-basierte Metriken (GEMBA-Varianten) auf Systemebene überraschende Stärke zeigten. Wichtige Befunde:

- **Quellbewusste Metriken** (unter Verwendung von Quelle + Referenz + Hypothese) übertrafen durchweg referenzbasierte Metriken
- **Hybride Modelle**, die aus einer einzigen Architektur heraus sowohl im referenzbasierten als auch im referenzfreien Modus arbeiten, sind die aufkommende Richtung
- Die **Lücke bei ressourcenarmen Sprachen** besteht fort: Alle Metriken schneiden bei unterrepräsentierten Sprachen schlechter ab, und die Lücke verengt sich nicht
- **MQM-trainierte Metriken** (unter Verwendung feingranularer Fehlerannotationen) übertreffen durchweg DA-trainierte Metriken (unter Verwendung skalarer Scores)

Die Implikationen für die Evaluierung ressourcenarmer Sprachen sind klar: Das Fachgebiet konvergiert auf große, trainierte, quellbewusste neuronale Metriken als Goldstandard. Diese Metriken erfordern erhebliche Trainingsdaten, Rechenleistung und — entscheidend — menschliche Evaluierungsdaten in der Zielsprache. Für Sprachen, denen all dies fehlt, ist die hochmoderne Metrik-Pipeline schlichtweg nicht anwendbar.

### Das Verzerrungsproblem: Neuronale Metriken und ressourcenarme Sprachen

Die Revolution der neuronalen Metriken war überwiegend ein Phänomen ressourcenreicher Sprachen. Jede trainierte Metrik in den vorhergehenden Abschnitten wurde auf WMT-Daten menschlicher Urteile trainiert, die etwa 20 Sprachpaare abdecken — alle davon unter Beteiligung europäischer Sprachen, des Chinesischen oder des Japanischen. Die zugrunde liegenden Encoder (XLM-R, mT5, InfoXLM) wurden auf CommonCrawl-Daten trainiert, in denen die Repräsentation proportional zur Webpräsenz ist: Englisch dominiert, europäische Sprachen sind gut abgedeckt, und die überwältigende Mehrheit der über 7.000 Sprachen der Welt ist faktisch abwesend.

Für eine Sprache wie Plains Cree erzeugt dies ein kaskadierendes Versagen:

1. **Keine Trainingsdaten**: Es gibt keine WMT-Urteile von Menschen für Cree-Übersetzungen, sodass keine Metrik darauf trainiert wurde, sie zu evaluieren.
2. **Keine Encoder-Abdeckung**: Das Vokabular von XLM-R wurde auf CommonCrawl aufgebaut, wo Cree-Text verschwindend selten ist. Der Tokenizer übersegmentiert Cree-Wörter in willkürliche Byte-Fragmente, und die kontextuellen Embeddings für diese Fragmente sind schlecht trainiert.
3. **Keine Validierung**: Niemand hat gemessen, ob COMET, BLEURT oder MetricX bedeutungsvolle Scores für Cree erzeugt. Sie mögen *Zahlen* erzeugen, aber es gibt keinen Beweis, dass diese Zahlen mit der tatsächlichen Übersetzungsqualität korrelieren.
4. **Kein Weg zur Verbesserung**: Der AfriCOMET-Ansatz — einen sprachfamilienspezifischen Encoder bauen, menschliche Evaluierungsdaten sammeln, eine neue Metrik trainieren — ist ein mehrjähriges Unterfangen mehrerer Institutionen. Für eine Sprachgemeinschaft von 27.000 Sprechern existiert die Forschungsinfrastruktur, um dies zu unterstützen, derzeit nicht.

Das Ergebnis ist ein Paradox: Die Sprachen, die MT-Evaluierung am dringendsten benötigen (weil ihre MT-Systeme am schwächsten sind und die sorgfältigste Beurteilung erfordern), sind genau die Sprachen, bei denen die besten Evaluierungswerkzeuge am unzuverlässigsten sind. Die Reaktion des Fachgebiets bestand darin, chrF++ als „gut genug"-Alternative zu empfehlen — und es ist besser als BLEU — doch chrF++ ist immer noch eine String-Matching-Metrik, die keine Äquivalenz erkennen kann, keine freie Wortstellung handhaben kann und kein Konzept von morphologischer Gültigkeit hat.

---

## Teil 3: Jenseits des Scorings — diagnostische und linguistische Evaluierung

### Die Aufteilung in Adäquatheit/Flüssigkeit

Bevor automatische Metriken existierten, verwendete die menschliche Evaluierung von MT ein Framework mit zwei Dimensionen: **Adäquatheit** (vermittelt die Übersetzung die Bedeutung der Quelle?) und **Flüssigkeit** (ist die Übersetzung in der Zielsprache grammatikalisch und natürlich?). Diese Unterscheidung, kodifiziert in frühen DARPA-MT-Evaluierungen und später bei NIST, erkannte etwas an, das automatische Metriken zwei Jahrzehnte lang wiederzuerlangen versuchen würden: Übersetzungsqualität ist nicht eindimensional.

Das Adäquatheit/Flüssigkeit-Framework geriet in Ungnade, als das Direct Assessment (ein einzelner skalarer Score) es bei WMT ersetzte. Doch die zugrunde liegende Erkenntnis bleibt von entscheidender Bedeutung: Eine Übersetzung kann flüssig, aber falsch sein (Halluzination), oder unflüssig, aber korrekt (morphologische Variante). Kein einzelner Score erfasst beides.

### MQM: Der Goldstandard (Lommel et al., 2014; Freitag et al., 2021)

**Multidimensional Quality Metrics (MQM)** ersetzte ab 2021 das Direct Assessment als primäre menschliche Evaluierung von WMT. MQM setzt professionelle Übersetzer ein, die spezifische Fehlerspannen markieren, sie nach Typ (Fehlübersetzung, Auslassung, Hinzufügung, Grammatik, Terminologie) und Schweregrad (geringfügig = 1 Punkt, schwerwiegend = 5 Punkte, kritisch = 25 Punkte) klassifizieren. Dies erzeugt sowohl einen Qualitäts-Score als auch handlungsrelevante diagnostische Informationen.

MQM kommt einer „korrekten" Evaluierungsmethodik am nächsten — sie sagt Ihnen nicht nur, *wie schlecht* eine Übersetzung ist, sondern *was genau* schiefgelaufen ist. Doch sie erfordert professionelle zweisprachige Übersetzer, die für die meisten ressourcenarmen Sprachen nicht in ausreichender Zahl existieren, um eine statistisch zuverlässige Evaluierung zu ermöglichen.

### MorphEval: Kontrastive morphologische Evaluierung (Burlot & Yvon, 2017)

MorphEval ist der direkteste Vorläufer für morphologiebewusste MT-Evaluierung. Eingeführt von Franck Burlot und François Yvon auf der WMT 2017 und 2018 erweitert, evaluiert MorphEval morphologische *Kompetenz* unter Verwendung **kontrastiver Testsuiten**.

**Funktionsweise:** Die Testsuite besteht aus Satzpaaren in der Quellsprache, die sich um genau einen morphologischen Kontrast unterscheiden — zum Beispiel Singular vs. Plural, Präsens vs. Präteritum, Maskulinum vs. Femininum. Das MT-System übersetzt beide Sätze. Wenn das System den Kontrast in seinen Übersetzungen korrekt vermittelt (z. B. ein plurales Ziel erzeugt, wenn die Quelle plural ist, und ein singulares Ziel, wenn die Quelle singular ist), wird der Kontrast als korrekt gewertet.

**Abgedeckte Sprachen:** Englisch→Tschechisch, Englisch→Lettisch (v1, WMT 2017); erweitert auf Englisch→Französisch, Englisch→Deutsch, Englisch→Finnisch, Türkisch→Englisch (v2, WMT 2018).

**Wichtige Befunde:** MorphEval offenbarte, dass selbst leistungsstärkste neuronale MT-Systeme systematische morphologische Fehler aufwiesen — sie konnten flüssige Ausgaben erzeugen und dabei Tempus, Numerus oder Kasus falsch wiedergeben. Diese Fehler waren für BLEU unsichtbar und sogar für COMET teilweise unsichtbar.

**Verfügbarkeit:** Open Source auf GitHub ([franckbrl/morpheval](https://github.com/franckbrl/morpheval), [franckbrl/morpheval_v2](https://github.com/franckbrl/morpheval_v2)).

**Beschränkungen:** MorphEval erfordert gefertigte kontrastive Testsuiten pro Zielsprache, entworfen von Linguisten, die die morphologischen Kontraste dieser Sprache verstehen. Für keine polysynthetische Sprache existieren Testsuiten. Die Methodik testet auf *Kompetenz* (kann das System diesen Kontrast handhaben?) statt auf *Gültigkeit* (hat das System echte Wörter erzeugt?) oder *Äquivalenz* (sind diese beiden verschiedenen Übersetzungen beide korrekt?).

### CheckList: Verhaltensbasiertes Testen für NLP (Ribeiro et al., ACL 2020)

**CheckList**, 2020 auf der ACL von Marco Tulio Ribeiro und Kollegen veröffentlicht (Gewinner des Best Paper Award), importierte eine Idee aus dem Software-Engineering in die NLP-Evaluierung: **Unit-Testing**. Anstatt die Gesamtleistung eines Modells anhand eines Benchmarks zu evaluieren, definiert CheckList eine Matrix von **Fähigkeiten** (Vokabular, Negation, Eigennamen, zeitliches Schlussfolgern, Koreferenz), gekreuzt mit **Testtypen**:

- **Minimum Functionality Tests (MFT)**: Einfache, gezielte Testfälle, die jedes kompetente Modell bestehen sollte.
- **Invariance Tests (INV)**: Perturbationen der Eingabe, die die Ausgabe *nicht* ändern sollten (z. B. sollte die Änderung eines Namens nicht die Stimmung ändern).
- **Directional Expectation Tests (DIR)**: Perturbationen, die die Ausgabe in eine vorhersehbare Richtung ändern *sollten*.

CheckList war ursprünglich für Sentiment-Analyse und NLI konzipiert, doch das Paradigma ist direkt auf MT anwendbar. Man könnte MFTs für morphologische Phänomene erstellen („erzeugt das System die korrekte Pluralform?"), INV-Tests für freie Wortstellung („ändert die Umstellung der Cree-Wörter die englische Übersetzung?") und DIR-Tests für morphologische Merkmale („ändert die Änderung der Quelle von Präteritum zu Präsens das Tempus des Ziels?").

Das CheckList-Paradigma ist besonders relevant, weil es formalisiert, was MorphEval intuitiv tut: spezifische Fähigkeiten testen, statt Gesamt-Scores zu messen. Die Variantenklassen unseres Linters (WORD_ORDER, ORTHOGRAPHIC, OPTIONAL_PARTICLE usw.) sind faktisch Invarianzregeln — sie definieren Perturbationen, die das Evaluierungsurteil nicht ändern sollten.

### Challenge Sets und gezielte Evaluierung

Das breitere Paradigma der **Challenge Sets** — gefertigte Testsuiten, die auf spezifische linguistische Phänomene abzielen — ist seit etwa 2017 zu einer etablierten komplementären Evaluierungsmethodik bei WMT geworden.

**Isabelle, Cherry & Foster (2017)** am NRC Canada leisteten Pionierarbeit für diesen Ansatz für MT mit handgefertigten Testsets, die strukturelle Divergenzen zwischen Sprachen isolieren — Fälle, in denen eine wörtliche Übersetzung wahrscheinlich falsch ist. Ihre Folgearbeit (Isabelle & Kuhn, 2018) konstruierte 506 französische Sätze, die auf spezifische Übersetzungsherausforderungen abzielten, und lieferte feingranulare Bilder der Systemfähigkeiten.

**LingEval97** (Sennrich, EACL 2017) erstellte 97.000 kontrastive Englisch→Deutsch-Übersetzungspaare, die testeten, ob NMT-Modelle korrekten Übersetzungen eine höhere Wahrscheinlichkeit zuweisen als Paaren mit eingeführten morphosyntaktischen Fehlern. Ein zentraler Befund: Modelle auf Zeichenebene zeichneten sich bei der Transliteration aus, schnitten aber bei morphosyntaktischer Kongruenz über große Distanzen schlechter ab.

**ACES** (Amrhein, Moghe & Guillou, 2022–2023) skalierte den Challenge-Set-Ansatz dramatisch: 36.476 Beispiele über 146 Sprachpaare hinweg, die 68 unterschiedliche linguistische Phänomene testen. ACES wurde verwendet, um Metriken, die beim WMT Metrics Shared Task eingereicht wurden, meta-zu-evaluieren — und testete, ob *Metriken* die Kontraste erkennen konnten, nicht nur, ob *Systeme* sie erzeugen konnten. Erweitert zu **SPAN-ACES** mit Fehlerspannen-Annotationen.

**MT-GenEval** (Currey et al., EMNLP 2022) und **WinoMT** (Stanovsky, Smith & Zettlemoyer, ACL 2019) zielen speziell auf Geschlechtsgenauigkeit ab. WinoMT ist bemerkenswert, weil es explizit **morphologische Analyse** an der Zielsprache verwendet, um das Geschlecht übersetzter Berufsbezeichnungen zu verifizieren — einer der wenigen Fälle, in denen ein morphologischer Analysator als Teil eines MT-Evaluierungswerkzeugs verwendet wird.

**Hjerson** (Popović & Ney, 2011) ist ein Open-Source-Werkzeug zur automatischen MT-Fehlerklassifikation, das **Lemmata und POS-Tags** verwendet, um Fehler in fünf Typen zu kategorisieren: morphologische, Umstellungs-, fehlende Wörter, überzählige Wörter und lexikalische Fehler. Dies ist vom Geiste her vielleicht der nächste Vorläufer zu unserem Linter — es verwendet linguistische Analyse, um diagnostische Fehlerkategorien statt eines einzelnen Scores zu liefern.

Der gemeinsame Nenner: Das Fachgebiet hat wiederholt anerkannt, dass Gesamt-Scores unzureichend sind. Diagnostische Evaluierung liefert die Granularität, die nötig ist, um zu verstehen, *warum* ein System scheitert. Doch diagnostische Ansätze erfordern linguistische Expertise pro Sprache, und diese Expertise konzentriert sich auf europäische Sprachen.

### AmericasNLP: Evaluierung an der Front

Die AmericasNLP-Workshop-Reihe (zusammen mit der NAACL veranstaltet), die sich auf NLP für indigene Sprachen Amerikas konzentriert, bietet den direktesten Vergleichspunkt für unsere Evaluierungsherausforderungen.

Von 2021 bis 2023 verwendete der Shared Task **chrF** als primäre Evaluierungsmetrik — gewählt wegen seiner Robustheit in ressourcenarmen Umgebungen und seines Matchings auf Zeichenebene, das Teilanrechnung für morphologische Überlappung gewährt. Die Organisatoren erkannten die Beschränkungen von chrF an, hatten aber keine bessere Alternative, die über die vielfältigen repräsentierten Typologien hinweg (Quechua, Guaraní, Aymara, Nahuatl, Rarámuri und andere) funktionieren konnte.

2025 führte AmericasNLP einen dedizierten **Shared Task 3** speziell für die Entwicklung von MT-Evaluierungsmetriken für indigene Sprachen ein — das erste Mal, dass das Fachgebiet explizit anerkannte, dass bestehende Metriken für diese Sprachen unzureichend sind. Die siegreiche Einreichung, **FUSE** (Feature-Union Scorer), kombinierte mehrsprachige Satz-Embeddings (feinabgestimmtes LaBSE), lexikalische Ähnlichkeit, phonetische Ähnlichkeit und unscharfes Token-Matching mittels Ridge-Regression und Gradient Boosting. FUSE verwendet keine morphologischen Analysatoren — das Feature-Engineering ist sprachunabhängig.

Dies ist die Lücke, die unsere Arbeit besetzt. AmericasNLP hat das Problem identifiziert (Standardmetriken scheitern für indigene Sprachen) und begonnen, Alternativen zu entwickeln (FUSE). Doch keine der Alternativen verwendet das morphologische Wissen, das FSTs bieten. Die AmericasNLP-Gemeinschaft verwendet chrF++, weil es die beste verfügbare generische Option ist, während die GiellaLT-Gemeinschaft ausgefeilte morphologische Werkzeuge baut, die nie in die MT-Evaluierung eingebunden werden. Die beiden Gemeinschaften sind nicht konvergiert.

---

## Teil 4: Referenzfreie Evaluierung und Quality Estimation

Einige der wichtigsten Evaluierungssignale in unserer Harness erfordern überhaupt keine Referenzübersetzungen. Die FST-Gültigkeitsprüfung („ist dies ein echtes Wort?") benötigt nur die MT-Ausgabe. Der Halluzinationsdetektor benötigt die Quelle und die Hypothese. Der Code-Switching-Detektor benötigt nur die Hypothese und Wissen über das Schriftsystem der Zielsprache. Zu verstehen, wo diese in die breitere Landschaft der referenzfreien Evaluierung passen, ist wesentlich, um sie korrekt zu positionieren.

### Das Quality-Estimation-Paradigma

**Quality Estimation (QE)** ist das Teilgebiet der MT-Evaluierung, das sich mit der Vorhersage von Übersetzungsqualität *ohne* Referenzübersetzungen befasst. Es ist seit 2012 ein dedizierter Shared Task bei WMT, motiviert durch die praktische Notwendigkeit, MT-Qualität zum Zeitpunkt des Einsatzes zu beurteilen — wenn Sie neuen Text übersetzen und keine menschliche Referenz zum Vergleich haben.

Die QE-Aufgabe hat sich über drei Generationen entwickelt. **Feature-basierte QE** (2012–2016) extrahierte handgefertigte Merkmale aus der Quelle und der Hypothese — Perplexität von Sprachmodellen, Worthäufigkeit, n-Gramm-Überlappung mit einsprachigen Daten — und trainierte Klassifikatoren, um die Qualität vorherzusagen. **Neuronale QE** (2017–2021) ersetzte handgefertigte Merkmale durch gelernte Repräsentationen, typischerweise unter Verwendung zweisprachiger Encoder. **Aktuelle QE** (2022–Gegenwart) wird von COMET-basierten Ansätzen dominiert, insbesondere **CometKiwi**.

### CometKiwi und referenzfreies COMET

**CometKiwi** (Rei et al., WMT 2022), die referenzfreie Variante von COMET, verwendet InfoXLM, um den Quellsatz und die MT-Hypothese (ohne Referenz) zu kodieren und einen Qualitäts-Score vorherzusagen. Es erzielte Spitzenergebnisse bei den QE Shared Tasks der WMT 2022 und 2023.

Der bemerkenswerte Befund: Das referenzfreie CometKiwi nähert sich der Korrelation mit menschlichem Urteil an, die das referenzbasierte COMET erreicht. Dies deutet darauf hin, dass für gut ausgestattete Sprachen der Quelltext beinahe so viel Evaluierungssignal enthält wie die Referenzübersetzung. Doch derselbe Vorbehalt gilt: Der Encoder von CometKiwi hat eine minimale Repräsentation für ressourcenarme Sprachen, sodass seine referenzfreien Vorhersagen für Cree oder Samisch unzuverlässig sind.

Hier bieten unsere FST-basierten Metriken etwas wirklich Andersartiges. Die FST-Gültigkeitsprüfung ist ein **deterministisches, referenzfreies Qualitätssignal**, das kein trainiertes Modell und keine menschlichen Urteilsdaten erfordert. Wenn der FST sagt, dass ein Wort kein gültiges Cree-Wort ist, dann ist dieses Wort kein gültiges Cree-Wort — mit dem Vorbehalt der Falschablehnungen für Lehnwörter, Neologismen und Eigennamen. Diese Art von hartem, regelbasiertem Qualitätssignal hat im neuronalen QE-Ökosystem keine Entsprechung.

### Halluzinationserkennung in MT

Halluzination in MT — flüssige Ausgabe, die völlig unverbunden mit der Quelle ist — ist ein schwerwiegender Fehlermodus, insbesondere in ressourcenarmen Umgebungen, in denen Modelle unzureichende Trainingsdaten haben, um zuverlässige Quelle-Ziel-Korrespondenzen zu lernen.

Der akademische Stand der Technik in der Halluzinationserkennung verwendet mehrere Ansätze:

- **Embedding-basierte Erkennung**: Vergleich von Quell- und Hypothesen-Embeddings in einem gemeinsamen Raum (LASER, LaBSE) und Kennzeichnung von Fällen, in denen die Ähnlichkeit unter einem Schwellenwert liegt.
- **Wahrscheinlichkeitsbasierte Erkennung**: Verwendung der eigenen Konfidenz-Scores des MT-Modells — Halluzinationen neigen dazu, eine hohe Ausgabewahrscheinlichkeit, aber eine niedrige quellbedingte Wahrscheinlichkeit zu haben.
- **Kontrastive Perturbation**: Vergleich der MT-Ausgabe für die reale Quelle mit der Ausgabe für eine perturbierte oder unverbundene Quelle; sind die Ausgaben verdächtig ähnlich, ignoriert das Modell die Quelle.
- **LLM-as-judge**: Veranlassen eines LLM, zu beurteilen, ob die Übersetzung der Quelle treu ist.

Unsere Harness verwendet ein **heuristisches Erkennungs-Plugin**, das vier Signale kombiniert: Längeninflation (Hypothese viel länger als erwartet), Wiederholung (wiederholte Phrasen), Entitätsdiskrepanz (Eigennamen in der Quelle, die in der Hypothese fehlen) und Quell-Echo (Hypothese ist dem Quelltext zu ähnlich, was auf unübersetztes Kopieren hindeutet). Dies ist im Vergleich zum akademischen Stand der Technik auf Baseline-Niveau — es fängt grobe Halluzinationen ab, übersieht aber subtile. Sein Wert liegt darin, ein **billiges, schnelles, referenzfreies Sieb** zu sein, das die schlimmsten Fehler kennzeichnen kann, ohne eine GPU oder einen API-Aufruf zu erfordern.

### Code-Switching-Erkennung

Code-Switching in MT-Ausgaben — wo das System Wörter in der Quellsprache erzeugt, anstatt sie zu übersetzen — ist ein von Halluzination verschiedener Fehlermodus. Es tritt typischerweise auf, wenn das Modell auf ein Wort stößt, das es nicht übersetzen kann, und auf das Kopieren der Quelle zurückgreift.

Unser Code-Switching-Erkennungs-Plugin verwendet **Unicode-Block-Analyse** (Erkennung von Zeichen aus dem Schriftsystem der Quellsprache in dem, was Ausgabe in der Zielsprache sein sollte) und **Listen häufiger Wörter** (Identifizierung hochfrequenter quellsprachlicher Wörter, die unübersetzt erscheinen). Für Cree, das sowohl SRO (lateinbasiert) als auch Silbenschrift verwendet, erfordert dies einige Sorgfalt — Englisch und SRO teilen sich das lateinische Schriftsystem, sodass die Unicode-Block-Analyse allein unzureichend ist.

Die akademische Literatur zur Code-Switching-Erkennung in MT ist im Vergleich zur Halluzinationserkennung spärlich. Die meiste Arbeit konzentriert sich auf Code-Switching im *Eingabe*text (zweisprachige Sprecher, die Sprachen mischen) statt im *Ausgabe*text (MT-Systeme, die nicht übersetzen). Unser heuristischer Ansatz liegt unseres Wissens nicht wesentlich hinter einem veröffentlichten Stand der Technik für dieses spezifische Problem zurück.

---

## Teil 5: Die morphologische Lücke

### Was bestehende Metriken nicht sehen können

Dies ist das Kernargument dieses Papers, und es erfordert eine konkrete Demonstration.

Betrachten Sie das Satzpaar in Plains Cree:

| | Text |
|--|------|
| **Quelle (Englisch)** | „I saw the man" |
| **Referenz (Cree)** | *nikî-wâpamâw nâpêw* |
| **Hypothese A** | *nâpêw nikî-wâpamâw* |
| **Hypothese B** | *nikî-wâpamikow nâpêsis* |

**Hypothese A** ist eine perfekte Übersetzung — sie hat dieselben Wörter in einer anderen Reihenfolge, was im Cree grammatikalisch ist (freie Wortstellung). **Hypothese B** sagt „der Junge wurde von mir gesehen" — falsche Richtung der Handlung (*-ikow* ist invers), falscher Referent (*nâpêsis* = „Junge", nicht „Mann").

| Metrik | Hypothese A (korrekt) | Hypothese B (falsch) | Kann sie sie unterscheiden? |
|--------|----------------------|---------------------|------------------------|
| BLEU | ~30 % | ~20 % | Kaum |
| chrF++ | ~65 % | ~55 % | Etwas |
| COMET | Unbekannt (keine Cree-Trainingsdaten) | Unbekannt | Unzuverlässig |
| **FST-Akzeptanz** | 100 % | 100 % | Nein (beide sind gültiges Cree) |
| **Linter** | EQUIVALENT (WORD_ORDER) | MISS | **Ja** |
| **Semantischer Validator** | VALID | WRONG | **Ja** |

Der Linter und der semantische Validator gelingen dort, wo BLEU, chrF++ und COMET scheitern — nicht weil sie in einem universellen Sinne „bessere Metriken" sind, sondern weil sie Zugang zu *linguistischem Wissen* haben, das String-Matching- und neuronale Metriken nicht haben. Sie wissen, dass Cree freie Wortstellung hat. Sie wissen, dass *wâpamêw* und *wâpamikow* unterschiedliche Lemmata mit unterschiedlichen Argumentstrukturen sind. Sie wissen, dass *nâpêw* und *nâpêsis* unterschiedliche Wörter sind.

Dieses Wissen stammt aus dem FST (der die morphologische Grammatik kodiert), dem zweisprachigen Wörterbuch (das englische Glossen für jedes Lemma liefert) und den manuell definierten Variantenklassen (die linguistisch fundierte Äquivalenzregeln kodieren). Keines dieses Wissens steht einer Metrik zur Verfügung, die die Übersetzung als String behandelt.

### Warum das Fachgebiet dies nicht adressiert hat

Die morphologische Lücke in der MT-Evaluierung ist kein Geheimnis. Das Fachgebiet weiß, dass sie existiert. Die Gründe, warum sie fortbesteht, sind struktureller Natur:

1. **Skalierungsverzerrung.** Die MT-Evaluierungsgemeinschaft optimiert für Metriken, die über alle WMT-Sprachpaare hinweg funktionieren. FST-basierte Metriken funktionieren für etwa 30 Sprachen. COMET funktioniert für 100+. chrF++ funktioniert für alle Sprachen mit einem Schriftsystem. Die Gemeinschaft belohnt Universalität gegenüber Präzision.

2. **Gemeinschaftssilos.** Die Menschen, die FSTs bauen (Computerlinguisten an der UiT Tromsø, am NRC Canada, an der University of Alberta), und die Menschen, die Evaluierungsmetriken bauen (ML-Forscher bei Google, Unbabel, WMT), besuchen verschiedene Konferenzen, publizieren an verschiedenen Orten und operieren unter verschiedenen Anreizstrukturen. Die Querbefruchtung, die erforderlich wäre, um FST-basierte Evaluierungsmetriken zu bauen, hat nicht stattgefunden — nicht weil sie versucht wurde und scheiterte, sondern weil die Gemeinschaften nie konvergierten.

3. **Abdeckungsangst.** FSTs haben bekannte Falschablehnungsprobleme: Lehnwörter, Neologismen und Eigennamen können als ungültig abgelehnt werden, selbst wenn sie vollkommen akzeptabel sind. Dies macht Forscher nervös, FSTs als Metriken zu verwenden — eine Falschablehnung bläht die Fehlerrate auf. Das Bedenken ist berechtigt, aber quantifizierbar: Die Falschablehnungsrate an als gut bekanntem Text zu messen, ist unkompliziert.

4. **Unzureichende Nachfrage.** Sehr wenige Menschen bauen MT für polysynthetische Sprachen, und diejenigen, die es tun (ALT Lab, NRC, AmericasNLP-Teilnehmer), verwenden typischerweise chrF++, weil das ist, was existiert. Es gab keinen konzertierten Vorstoß seitens der MT-Gemeinschaft für ressourcenarme Sprachen für morphologiebewusste Evaluierung, teils weil die Gemeinschaft klein ist und teils weil der Bau solcher Metriken Expertise sowohl im NLP-Engineering als auch in der Morphologie der spezifischen Zielsprache erfordert.

5. **Die Annahme der neuronalen Metrik.** Die vorherrschende Annahme seit 2020 lautet, dass neuronale Metriken das morphologische Problem schließlich durch gelernte Repräsentationen lösen werden. Wenn man COMET auf genügend Daten aus morphologisch reichen Sprachen trainiert, so das Argument, wird es lernen, morphologische Variation implizit zu handhaben. Dies mag für ressourcenreiche morphologisch reiche Sprachen (Finnisch, Türkisch, Tschechisch) zutreffen. Für Sprachen mit faktisch null Repräsentation in den Trainingsdaten ist es unwahrscheinlich.

---

## Teil 6: LYSS — eine linguistisch fundierte Alternative

### Was champollion gebaut hat: LYSS (Linguistically-informed Yield & Structural Scoring)

Die Evaluierungs-Harness des champollion-Projekts implementiert ein Composite-Scoring-Framework namens **LYSS**, das Standardmetriken (chrF++, exakte Übereinstimmung) mit vier Kategorien linguistisch fundierter Metriken kombiniert. Der Name spiegelt den Fokus des Frameworks wider: die Messung des *Yields* (wie viel Bedeutung den Übersetzungsprozess überlebt) durch *Structural Scoring* (deterministische, linguistisch fundierte Prüfungen statt gelernter Embeddings).

#### 1. Morphologisches Gültigkeitsgatter (GiellaLT-FST-Metrik)

Die einfachste und am breitesten anwendbare Metrik: Jedes Wort der MT-Ausgabe wird durch den endlichen morphologischen GiellaLT-Analysator für die Zielsprache geführt. Wenn der FST ein Wort parsen kann (mindestens eine Analyse zurückgibt), ist das Wort morphologisch gültig. Falls nicht, existiert das Wort in der Zielsprache nicht — es ist entweder ein halluziniertes Wort, ein morphologischer Fehler, ein Schreibfehler oder ein Lehnwort, das nicht im Lexikon enthalten ist.

**Ausgabe:** `fst_validity_rate` (0,0–1,0, höher = besser). Makro-Durchschnitt (Mittelwert der Raten pro Eintrag) und Mikro-Durchschnitt (gesamte gültige Wörter / gesamte Wörter).

**Abhängigkeiten:** `pyhfst` (Python-Bindings für Helsinki Finite-State Technology), eine kompilierte `.hfstol`-Analysatordatei für die Zielsprache.

**Erweiterbarkeit:** Funktioniert für jede Sprache mit einem GiellaLT-FST-Analysator — derzeit über 30 Sprachen, primär samische, uralische und indigene arktische Sprachen.

**Bezug zum Vorläufer:** MorphEval testet, ob ein System spezifische Kontraste handhaben kann. Die FST-Metrik testet, ob die Ausgabe des Systems aus echten Wörtern besteht. Diese sind komplementär: MorphEval testet Kompetenz, die FST-Metrik testet Gültigkeit.

#### 2. Linguistische Äquivalenzklassen (CRK-Linter)

Der Linter adressiert das, was vielleicht der heimtückischste Fehlermodus der referenzbasierten Evaluierung ist: **die Bestrafung korrekter Übersetzungen, die von der Referenz abweichen**.

Der Plains-Cree-Linter (844 Zeilen) implementiert sechs **Variantenklassen**, von denen jede eine linguistisch fundierte Äquivalenzregel kodiert:

- **WORD_ORDER**: Cree hat pragmatisch freie Wortstellung (Wolfart, 1973 §3.2). *nikî-wâpamâw nâpêw* und *nâpêw nikî-wâpamâw* bedeuten dasselbe. Der Linter erzeugt alle Permutationen und prüft, ob die Hypothese mit irgendeiner übereinstimmt.
- **ORTHOGRAPHIC**: Die Standard Roman Orthography hat bekannte Variationspunkte — Zirkumflex vs. Makron (*â* vs. *ā*), Bindestrichsetzung von Präverben (*nikî-nipâw* vs. *nikî nipâw* vs. *nikînipâw*). Der Linter normalisiert diese.
- **OPTIONAL_PARTICLE**: Bestimmte Diskurspartikeln (*mâka*, *êkwa*, *êwako*) können vorhanden oder abwesend sein, ohne die Kernproposition zu ändern. Der Linter prüft, ob die Hypothese nach der Entfernung der Partikel mit der Referenz übereinstimmt.
- **LEMMA_SYNONYM**: Einige Cree-Lemmata sind in spezifischen Kontexten austauschbar. Dies verwendet eine kuratierte Synonymliste (z. B. dialektale Varianten) und prüft, sofern der FST verfügbar ist, ob die Hypothese und die Referenz morphologische Analysen teilen.
- **PROGRESSIVE_AMBIGUITY**: Englische Verlaufsformen („is walking") können mit verschiedenen Konstruktionen ins Cree übersetzt werden. Der Linter erkennt diese als äquivalent.
- **INCLUSIVE_EXCLUSIVE**: Cree unterscheidet inklusives „wir" (*ki-*-Präfix) vom exklusiven „wir" (*ni-*-Präfix) — eine Unterscheidung, die das Englische in ein einziges Pronomen zusammenfasst. Der Linter erkennt, dass beide Formen korrekt sein können, wenn die englische Quelle mehrdeutig ist.

Der Linter erzeugt drei Urteile: **EXACT** (Hypothese stimmt mit Referenz überein), **EQUIVALENT** (Hypothese weicht ab, wird aber als gültige Variante klassifiziert) oder **MISS** (keine Übereinstimmung gefunden). Auf aggregierter Ebene berechnet er eine `equivalent_match_rate` — den Anteil der Übersetzungen, die exakt oder äquivalent sind.

**Bezug zum Vorläufer:** Die nächste Parallele ist **HyTER** (Dreyer & Marcu, NAACL-HLT 2012), das exponentiell viele gültige Übersetzungen als Paraphrasennetzwerke kodiert und die Edit-Distance zur nächstgelegenen gültigen Form misst. Unser Linter ist konzeptionell ähnlich — er definiert eine Menge gültiger Übersetzungen für jede Referenz — verwendet aber linguistisch definierte Transformationsregeln statt Paraphrasendatenbanken. HyTER wurde für Englisch konzipiert; niemand hat Paraphrasennetzwerke für Cree gebaut. Unsere Variantenklassen sind faktisch eine kompakte, regelbasierte Annäherung an das, was HyTER mit Graphen tut.

Im CheckList-Framework fungieren unsere Variantenklassen als **Invarianztests**: Transformationen, die das Evaluierungsurteil nicht ändern sollten. Der Unterschied besteht darin, dass CheckList-Tests typischerweise auf das *Modell* angewendet werden; unsere Variantenregeln werden auf die *Metrik* angewendet.

#### 3. Deterministische semantische Validierung (CRK-Semantik-Metrik)

Der semantische Validator (792 Zeilen) versucht etwas Ambitionierteres: **deterministischer Bedeutungsvergleich** ohne neuronale Embeddings. Er operiert in vier Stufen:

1. **Morphologische Analyse**: Sowohl die Hypothese als auch die Referenz werden durch den CRK-FST-Analysator geführt, der das Lemma und die morphologischen Merkmale für jedes Wort zurückgibt.
2. **Glossen-Auflösung**: Jedes Lemma wird im Cree–Englisch-Wörterbuch (Wolvengrey, 2001) nachgeschlagen, um englische Glossen zu erhalten.
3. **Extraktion der Inhaltswörter**: Mithilfe der englischen Pipeline von spaCy (`en_core_web_md`) werden Funktionswörter sowohl aus den englischen Glossen als auch aus dem Quelltext herausgefiltert.
4. **Überlappungs-Scoring**: Die Überlappung der Inhaltswörter zwischen den Glossen der Hypothese und den Glossen der Referenz bestimmt das semantische Urteil.

Der Validator erzeugt kategoriale Urteile: **EXACT_MATCH**, **VALID** (verschiedene Wörter, aber dieselbe Bedeutung), **GRAMMAR_ISSUES** (korrekte Lemmata, aber Grammatikprobleme auf Satzebene — Kongruenz, Belebtheit, Verbform), **PARTIAL** (etwas Bedeutung erhalten), **INCOMPLETE** (Bedeutung teilweise fehlend), **WRONG** (andere Bedeutung) oder **NO_OUTPUT**.

**Bezug zum Vorläufer:** Dies ist faktisch eine **deterministische Annäherung an COMETs Berechnung der semantischen Ähnlichkeit**. Wo COMET gelernte sprachübergreifende Embeddings verwendet, um zu beurteilen, ob zwei Sätze dasselbe bedeuten, verwendet unser Validator eine Kette deterministischer Nachschläge: FST → Wörterbuch → spaCy. Der Vorteil ist Transparenz (jeder Schritt ist inspizierbar und deterministisch) und Unabhängigkeit von Trainingsdaten. Der Nachteil ist Brüchigkeit: Die Qualität der Beurteilung hängt vollständig von der Abdeckung des FST und der Vollständigkeit des Wörterbuchs ab.

Der Ansatz ist konzeptionell verwandt mit **MEANT** (Lo & Wu, 2011; Lo, 2017), das Semantic Role Labelling verwendete, um zu beurteilen, ob die „Wer hat wem was getan"-Struktur in der Übersetzung erhalten blieb. Unser Ansatz ist grobgranularer (Überlappung von Inhaltswörtern statt semantischer Rollen), operiert aber auf einer Sprache, für die keine SRL-Werkzeuge existieren.

#### 4. Verhaltensbasierte Erkennungs-Plugins (Halluzination, Code-Switching, Terminologie)

Drei zusätzliche Plugins liefern **verhaltensbasierte Qualitätssignale**, die die morphologischen Metriken ergänzen:

- **Halluzinationserkennung** (259 Zeilen): Vier heuristische Signale gewichtet und kombiniert — Längeninflation (40 %), Wiederholung (30 %), Entitätsdiskrepanz (20 %), Quell-Echo (10 %). Dies sind billige, referenzfreie Siebe, die grobe Erfindungen abfangen.
- **Code-Switching-Erkennung** (~280 Zeilen): Unicode-Block-Analyse plus Listen häufiger Wörter zur Erkennung unübersetzter quellsprachlicher Tokens. Gibt eine `code_switching_rate` aus (0,0–1,0).
- **Terminologietreue** (199 Zeilen): Prüft, ob spezifizierte Glossarbegriffe konsistent übersetzt werden. Gibt `terminology_adherence` (0,0–1,0) oder None zurück, falls kein Glossar konfiguriert ist.

Diese Plugins sind ehrlich als **Baseline-heuristische Detektoren** positioniert, nicht als Stand der Technik. Ihr Wert liegt darin, billige, schnelle, interpretierbare Signale zu liefern, die parallel zu den ausgefeilteren morphologischen Metriken berechnet werden können. Im Composite-Scoring-Framework tragen sie geringe Gewichte (je 0,05).

### Ehrliche Beschränkungen

Dieser Ansatz hat erhebliche Beschränkungen, die anerkannt werden müssen, bevor ein Anspruch auf Neuartigkeit oder Nutzen erhoben wird:

1. **FST-Falschablehnungsrate.** Der FST wird gültige Wörter ablehnen, die nicht in seinem Lexikon enthalten sind — Lehnwörter, Neologismen, Eigennamen, code-gemischte Begriffe. Dies bläht die morphologische Fehlerrate auf. Die Falschablehnungsrate wurde nicht formal an einem repräsentativen Korpus von Cree-Text gemessen. Ohne diese Messung ist die Präzision der FST-Gültigkeitsmetrik unbekannt.

2. **Wörterbuchabdeckung.** Die Qualität des semantischen Validators hängt vollständig von der Abdeckung des Wolvengrey-Wörterbuchs ab. Cree-Wörter, die nicht im Wörterbuch enthalten sind, erzeugen keine Glossen, was der Validator als Bedeutungslücke behandelt. Das Wörterbuch enthält etwa 22.000 Einträge — beträchtlich, aber nicht erschöpfend.

3. **Vollständigkeit der Variantenklassen.** Die sechs Variantenklassen des Linters wurden auf Basis linguistischer Literatur und der Beobachtung von MT-Ausgabemustern konzipiert. Es mag zusätzliche Äquivalenzklassen geben, die nicht erfasst werden — dialektale Variationen, Registerunterschiede, Synonyme auf Diskursebene. Kein formaler Prozess gewährleistet Vollständigkeit.

4. **Keine Studie zur menschlichen Korrelation.** Die kritischste Lücke: Niemand hat gemessen, ob die Urteile des Linters (EXACT/EQUIVALENT/MISS) oder die Urteile des semantischen Validators mit menschlichen Urteilen über die Übersetzungsqualität korrelieren. Neuronale Metriken verbringen Jahre damit, die Korrelation mit menschlicher Beurteilung herzustellen (WMT Shared Tasks). Unsere Metriken haben keine derartige Validierung.

5. **Sprachspezifik.** Die Variantenklassen, Synonymlisten und Regeln für optionale Partikeln sind spezifisch für Plains Cree. Ihre Portierung auf Nordsamisch, Inuktitut oder eine andere Sprache erfordert Linguisten, die die Morphologie, die Flexibilität der Wortstellung und die orthographische Variation dieser Sprache verstehen. Das *Framework* ist portierbar; die *Regeln* sind es nicht.

6. **Lücken in der Metrik-Verdrahtung.** Zum Zeitpunkt dieses Schreibens haben vier der neun Metriken im Composite-Scoring-Profil (semantic_score, morphological_accuracy, equivalent_match_rate, orthographic_accuracy) eine unvollständige oder unklare Plugin-Verdrahtung in der Arena-Harness. Der Composite-Score wird faktisch aus etwa fünf Metriken mit umverteilten Gewichten berechnet.

### Was erforderlich wäre, um diesen Ansatz zu validieren

Um diese Arbeit veröffentlichungsfähig zu machen — an jedem Ort, auf jeder Ebene akademischer Ernsthaftigkeit — wären die folgenden Experimente erforderlich:

1. **Studie zur Korrelation mit menschlichem Urteil.** Sammeln Sie menschliche Qualitätsbeurteilungen für eine Reihe von Englisch→Cree-Übersetzungen (idealerweise 200+ Satzpaare, von 3+ zweisprachigen Sprechern beurteilt). Berechnen Sie Korrelationen zwischen den menschlichen Scores und jeder unserer Metriken. Dies ist die einzige wichtigste Validierung. Ohne sie sind die Metriken Engineering-Artefakte, keine Evaluierungswerkzeuge.

2. **Messung der FST-Falschablehnungsrate.** Führen Sie den FST-Analysator auf einem Korpus von als gut bekanntem Cree-Text aus (z. B. veröffentlichte Cree-Texte, validierte Parallelkorpora) und messen Sie, welcher Prozentsatz gültiger Wörter abgelehnt wird. Dies quantifiziert die Präzision der FST-Gültigkeitsmetrik.

3. **Validierung an einer zweiten Sprache.** Portieren Sie die FST-Gültigkeitsmetrik auf eine zweite GiellaLT-Sprache (höchstwahrscheinlich Nordsamisch, das den ausgereiftesten FST-Analysator im GiellaLT-Ökosystem hat). Demonstrieren Sie, dass die Metrik sinnvolle Ergebnisse bei samischer MT-Ausgabe erzeugt. Dies validiert den Anspruch der Erweiterbarkeit.

4. **Vergleich mit COMET.** Führen Sie COMET auf denselben Cree-Daten aus und vergleichen Sie seine Scores mit unseren Metriken und mit menschlichen Urteilen. Wenn COMET bedeutungsvolle Scores für Cree erzeugt (was wir bezweifeln, aber nicht getestet haben), müssen unsere Metriken es schlagen, um nützlich zu sein. Wenn COMET Rauschen erzeugt (was wir erwarten), validiert dies die Notwendigkeit unseres Ansatzes.

5. **Diagnostische Ergänzung mit MorphEval.** Bauen Sie eine kleine (50–100 Kontraste) MorphEval-artige Testsuite für Plains Cree, die auf die markantesten morphologischen Merkmale der Sprache abzielt (Obviativ, Invers, Conjunct/Independent, Inklusiv/Exklusiv). Lassen Sie MT-Systeme dagegen laufen und zeigen Sie, dass die diagnostischen Informationen handlungsrelevant sind.

6. **Verdrahtungs- und Integrationsaudit.** Beheben Sie die in der Codebasis-Inventur identifizierten Lücken in der Verdrahtung des Scoring-Profils. Stellen Sie sicher, dass alle neun Composite-Metriken Werte erzeugen und dass der aggregierte Score korrekt berechnet wird.

---

## Teil 7: Positionierung und zukünftige Arbeit

### Wo LYSS in der Evaluierungslandschaft sitzt

Eine Taxonomie der MT-Evaluierungsansätze, ehrlich positioniert:

| Dimension | String-Metriken (BLEU, chrF++) | Neuronale Metriken (COMET, MetricX) | LLM-as-judge (GEMBA) | Diagnostisch (MorphEval, CheckList) | **LYSS** |
|-----------|-------------------------------|---|----|-------|--------|
| Signaltyp | Oberflächenüberlappung | Gelernte semantische Ähnlichkeit | Offenes Urteil | Gezielte Fähigkeitssonden | Morphologische Gültigkeit + regelbasierte Äquivalenz |
| Benötigte Trainingsdaten | Keine | Menschliche Urteile (Tausende) | Vortrainiertes LLM | Von Linguisten konzipierte Testsuiten | FST + Wörterbuch + Variantenregeln |
| Anwendbarkeit auf LRL | Universell, aber schwach | Begrenzt durch Encoder-Abdeckung | Begrenzt durch LLM-Abdeckung | Begrenzt durch Testsuiten-Erstellung | Begrenzt durch FST-Verfügbarkeit (~30 Sprachen) |
| Referenz benötigt | Ja | Ja (oder reine Quelle-QE) | Optional | Ja (kontrastiv) | Ja (LYSS-eq/LYSS-sem) / Nein (LYSS-fst) |
| Interpretierbarkeit | Gering (eine Zahl) | Gering (eine Zahl) | Hoch (Text-Begründung) | Hoch (bestanden/nicht bestanden pro Phänomen) | Hoch (Urteile + Variantenklassen) |

**LYSS ist nicht**: ein Ersatz für COMET bei gut ausgestatteten Sprachen, eine universelle Metrik oder die erste morphologiebewusste Evaluierung.

**LYSS ist**: ein integriertes Framework, das FST-basierte morphologische Validierung mit Standardmetriken für den spezifischen Fall von Sprachen kombiniert, bei denen neuronalen Metriken die Abdeckung fehlt und regelbasierte Werkzeuge (FSTs, Wörterbücher) existieren. Es hat drei Kernkomponenten:
- **LYSS-fst** — Morphologische Gültigkeit via FST (`fst_acceptance_rate`)
- **LYSS-eq** — Linguistische Äquivalenz via den Linter (`equivalent_match_rate`)
- **LYSS-sem** — Deterministische semantische Validierung (`semantic_score`)

**LYSS erweitert**: MorphEvals Kernerkenntnis (morphologische Werkzeuge für die Evaluierung verwenden) von diagnostischem Kompetenztest zu kontinuierlichem Qualitäts-Scoring.

**LYSS ergänzt**: chrF++ (das Teilanrechnung für gemeinsame Morpheme gewährt, aber keine Äquivalenz erkennen kann), COMET (das im semantischen Raum operiert, aber dem Trainingsdaten für LRL fehlen) und FUSE (das Feature-Engineering verwendet, aber keine morphologischen Analysatoren).

**Der nächste Vorläufer ist**: Hjerson (linguistische Fehlerklassifikation) + HyTER (Äquivalenzklassen via Paraphrasennetzwerke) + Apertiums naive Abdeckungsmetrik (FST-basierte Gültigkeitsprüfung). LYSS' Beitrag ist nicht irgendeine einzelne Technik, sondern die Integration dieser Ideen — insbesondere FST-basierter Gültigkeit und regelbasierter Äquivalenz — in eine funktionierende Evaluierungs-Harness für eine polysynthetische Sprache.

### Integration von MorphEval

Die kontrastive Testsuiten-Methodik von MorphEval und unser kontinuierlicher Scoring-Ansatz sind komplementär:

- **MorphEval** beantwortet: „Kann dieses System Tempusmarkierung handhaben? Numeruskongruenz? Kasuszuweisung?"
- **Unsere FST-Metrik** beantwortet: „Hat dieses System echte Wörter erzeugt?"
- **Unser Linter** beantwortet: „Ist diese Übersetzung trotz Oberflächenunterschieden äquivalent zur Referenz?"
- **Unser semantischer Validator** beantwortet: „Bedeutet diese Übersetzung das Richtige?"

MorphEval ist Open Source. Die Erstellung einer Plains-Cree-Testsuite würde erfordern, dass ein Linguist kontrastive Paare entwirft, die Cree-spezifische morphologische Kontraste abdecken (Obviation, Inversmarkierung, Conjunct/Independent-Reihenfolge, inklusives/exklusives „wir", Präverbketten). Dies ist beträchtliche, aber begrenzte Arbeit — Wochen, nicht Monate — und würde eine diagnostische Fähigkeit bieten, die kein anderes Evaluierungswerkzeug für Cree bietet.

### Die Frage der Erweiterbarkeit

Welche anderen Sprachen könnten diesen Ansatz übernehmen? Die primäre Einschränkung ist die FST-Verfügbarkeit. Die GiellaLT-Infrastruktur bietet morphologische Analysatoren für über 30 Sprachen, primär in drei Familien:

- **Samische Sprachen** (Nordsamisch, Lulesamisch, Südsamisch, Skoltsamisch, Inarisamisch): Ausgereifte FSTs mit breiter Abdeckung. Nordsamisch ist das am unmittelbarsten portierbare Ziel.
- **Uralische Sprachen** (Finnisch, Estnisch, Komi, Ersja, Mokscha): Gut entwickelte Analysatoren, obwohl Finnisch und Estnisch möglicherweise nicht so dringend FST-basierte Evaluierung benötigen (sie haben mehr Abdeckung durch neuronale Metriken).
- **Indigene arktische Sprachen** (Inuktitut via Uqailaut, Grönländisch): Analysatoren existieren, aber die Abdeckung variiert.
- **Andere GiellaLT-Sprachen**: Färöisch, Irisch, Kornisch, Livisch und andere mit unterschiedlichem Reifegrad der FSTs.

Über GiellaLT hinaus bietet die **Apertium**-Plattform morphologische Analysatoren für etwa über 40 Sprachpaare. Das **HFST**-Ökosystem (Helsinki Finite-State Technology) ist die gemeinsame Infrastruktur, die sowohl GiellaLT als auch Apertium verwenden, was bedeutet, dass jeder Apertium-Analysator im Prinzip in dieselbe FST-Gültigkeitsmetrik eingebunden werden könnte.

Die praktische Einschränkung ist nicht die FST-Verfügbarkeit, sondern die **Kuratierung der Variantenklassen**. Die Äquivalenzregeln des Linters erfordern linguistische Expertise pro Zielsprache. Für Nordsamisch würde dies ein Verständnis der samischen Wortstellungsflexibilität, der orthographischen Konventionen und der dialektalen Variation erfordern. Für Inuktitut würde es ein Verständnis der polysynthetischen Morphologie auf einem Niveau erfordern, das mit dem für Cree Geleisteten vergleichbar ist. Die FST-Gültigkeitsmetrik jedoch kann für jede Sprache mit einem GiellaLT-Analysator sofort eingesetzt werden — keine zusätzliche linguistische Arbeit erforderlich.

### Auf dem Weg zu einem Paper

Eine auf dieser Arbeit basierende Publikation würde am natürlichsten auf einen dieser Orte abzielen:

- **WMT Metrics Shared Task** (zusammen mit der EMNLP veranstaltet): Der direkteste Ort. Würde erfordern, die Metriken als Shared-Task-Einreichung zu implementieren und auf WMT-Testsets zu evaluieren — die derzeit keine polysynthetische Sprache umfassen. Könnte als „findings"-Paper eingereicht werden oder am Challenge-Sets-Untertask teilnehmen.
- **LREC-COLING** (Language Resources and Evaluation Conference): Natürliche Passform für ein Ressourcen-/Werkzeug-Paper, das das Evaluierungs-Framework und die von ihm verwendeten linguistischen Ressourcen (FSTs, Wörterbücher, Variantenregeln) beschreibt.
- **ACL oder NAACL** (Hauptkonferenz): Würde die Studie zur menschlichen Korrelation und mindestens eine zusätzliche Sprache erfordern, um die Messlatte für ein Hauptkonferenz-Paper zu erfüllen.
- **AmericasNLP-Workshop**: Das aufgeschlossenste Publikum für die MT-Evaluierung indigener Sprachen. Niedrigere Publikationshürde, aber hohe Wirkung innerhalb der Zielgemeinschaft.
- **ComputEL** (Computational Approaches to Endangered Languages): Fokussierter Ort für genau diese Art von Arbeit.

Jede Publikation würde Co-Autoren mit Expertise in Cree-Linguistik erfordern (um die Variantenklassen zu validieren und Ergebnisse zu interpretieren) und idealerweise zweisprachige Cree-Sprecher (um die menschlichen Qualitätsbeurteilungen für die Korrelationsstudie zu liefern). Dies ist nicht optional — ein Paper über Cree-MT-Evaluierung, das vollständig von Nicht-Cree-Sprechern geschrieben wurde, wäre bestenfalls unvollständig und schlimmstenfalls eine Fortsetzung der extraktiven Forschungsdynamiken, von denen das Fachgebiet sich zu lösen versucht.

---

## Anhang A: Matrix der Metrik-Anforderungen

| Metrik | Referenz benötigt? | Quelle benötigt? | Trainiertes Modell? | Sprachspezifische Ressourcen? | Funktioniert für LRL? |
|--------|-------------------|---------------|----------------|------------------------------|----------------|
| BLEU | Ja | Nein | Nein | Nein | Schlecht |
| chrF++ | Ja | Nein | Nein | Nein | Besser als BLEU |
| METEOR | Ja | Nein | Nein | Stemmer + WordNet | Nur wenn Ressourcen existieren |
| TER | Ja | Nein | Nein | Nein | Wie BLEU |
| BERTScore | Ja | Nein | Ja (mBERT) | Nein | Abhängig von Modellabdeckung |
| BLEURT | Ja | Nein | Ja (trainiert) | Nein | Abhängig von Trainingsdaten |
| COMET | Ja | Ja | Ja (XLM-R) | Nein | Abhängig von XLM-R-Abdeckung |
| CometKiwi | Nein | Ja | Ja (XLM-R) | Nein | Abhängig von XLM-R-Abdeckung |
| GEMBA | Optional | Ja | Ja (LLM) | Nein | Abhängig von LLM-Abdeckung |
| **FST-Akzeptanz** | **Nein** | **Nein** | **Nein** | **Ja (FST-Analysator)** | **Ja, wenn FST existiert** |
| **CRK-Linter** | **Ja** | **Nein** | **Nein** | **Ja (FST + Variantenregeln)** | **Ja, wenn Ressourcen existieren** |
| **CRK-Semantik** | **Ja** | **Optional** | **Nein** | **Ja (FST + Wörterbuch + spaCy)** | **Ja, wenn Ressourcen existieren** |
| Halluzinationserk. | Nein | Ja | Nein | Nein | Ja |
| Code-Switching-Erk. | Optional | Ja | Nein | Minimal | Ja |
| MorphEval | Ja (kontrastiv) | Ja | Nein | Ja (Testsuite + Analysator) | Nur wenn Testsuite existiert |

## Anhang B: Wichtige Papers

| Zitation | Ort | Relevanz |
|----------|-------|----------|
| Papineni et al. (2002). BLEU: a Method for Automatic Evaluation of Machine Translation | ACL 2002 | Die Metrik, die das Fachgebiet definierte |
| Doddington (2002). Automatic Evaluation of Machine Translation Quality Using N-gram Co-Occurrence Statistics | HLT 2002 | Informationsgewichtetes n-Gramm-Matching |
| Banerjee & Lavie (2005). METEOR: An Automatic Metric for MT Evaluation | ACL 2005 Workshop | Stemming, Synonyme, Wort-Alignment |
| Snover et al. (2006). A Study of Translation Edit Rate | AMTA 2006 | Edit-Distance mit Phrasenverschiebungen |
| Popović & Ney (2011). Morphemes and POS tags for n-gram based evaluation metrics | WMT 2011 | Hjerson-Fehlerklassifikation |
| Dreyer & Marcu (2012). HyTER: Meaning-Equivalent Semantics for Translation Evaluation | NAACL-HLT 2012 | Äquivalenzklassen via Paraphrasennetzwerke |
| Lommel et al. (2014). Multidimensional Quality Metrics | — | MQM-Fehlertypologie |
| Popović (2015). chrF: character n-gram F-score for automatic MT evaluation | WMT 2015 | Evaluierung auf Zeichenebene |
| Popović (2017). chrF++: words helping character n-grams | WMT 2017 | Evaluierung mit Zeichen- + Wort-n-Grammen |
| Burlot & Yvon (2017). Evaluating the Morphological Competence of Machine Translation Systems | WMT 2017 | Kontrastive morphologische Testsuiten |
| Sennrich (2017). How Grammatical is Character-level Neural Machine Translation? | EACL 2017 | LingEval97 kontrastive Paare |
| Isabelle, Cherry & Foster (2017). A Challenge Set Approach to Evaluating Machine Translation | EMNLP 2017 | Gezieltes Testen struktureller Divergenz |
| Post (2018). A Call for Clarity in Reporting BLEU Scores | WMT 2018 | sacreBLEU-Standardisierung |
| Reiter (2018). A Structured Review of the Validity of BLEU | Computational Linguistics | Metaanalyse der Korrelation von BLEU mit menschlichem Urteil |
| Stanovsky, Smith & Zettlemoyer (2019). Evaluating Gender Bias in Machine Translation | ACL 2019 | WinoMT-Geschlechtsevaluierung |
| Ribeiro et al. (2020). Beyond Accuracy: Behavioral Testing of NLP Models with CheckList | ACL 2020 (Best Paper) | Fähigkeitsbasiertes Unit-Testing für NLP |
| Zhang et al. (2020). BERTScore: Evaluating Text Generation with BERT | ICLR 2020 | Embedding-basierte semantische Ähnlichkeit |
| Sellam et al. (2020). BLEURT: Learning Robust Metrics for Text Generation | ACL 2020 | Vortrainierte + feinabgestimmte Metrik |
| Rei et al. (2020). COMET: A Neural Framework for MT Evaluation | EMNLP 2020 | Sprachübergreifende trilinguale Evaluierung |
| Freitag et al. (2021). Results of the WMT 2021 Metrics Shared Task | WMT 2021 | MQM-basierte Meta-Evaluierung |
| Thompson & Post (2020). PRISM: Automatic MT Evaluation via Zero-Shot Paraphrasing | EMNLP 2020 | Mehrsprachiges NMT als Paraphrasen-Scorer |
| Currey et al. (2022). MT-GenEval | EMNLP 2022 | Kontrafaktische Geschlechtsgenauigkeit |
| Amrhein et al. (2022). ACES: Translation Accuracy Challenge Sets | WMT 2022 | 68 Phänomene, 146 Sprachpaare |
| Kocmi & Federmann (2023). GEMBA: Large Language Models Are State-of-the-Art Evaluators | EAMT 2023 | LLM-as-evaluator |
| Guerreiro et al. (2024). xCOMET: Transparent MT Evaluation through Fine-grained Error Detection | TACL 2024 | Fehlerspannen-Erkennung |
| Wang & Adelani (2024). AfriMTE and AfriCOMET | NAACL 2024 | Neuronale Metriken für afrikanische Sprachen |
| Juraska et al. (2024). MetricX-24 | WMT 2024 | mT5-basierte siegreiche Metrik |

## Anhang C: Glossar der Evaluierungsbegriffe

| Begriff | Definition |
|------|------------|
| **Adäquatheit** | Ob eine Übersetzung die Bedeutung der Quelle vermittelt. |
| **Flüssigkeit** | Ob eine Übersetzung in der Zielsprache grammatikalisch und natürlich ist. |
| **Direct Assessment (DA)** | Menschliche Evaluierungsmethode, bei der Annotatoren Übersetzungen auf einer Skala von 0–100 bewerten. |
| **MQM** | Multidimensional Quality Metrics — fehlerspannenbasierte menschliche Evaluierung mit typisierten Schweregraden. |
| **Quality Estimation (QE)** | Vorhersage der Übersetzungsqualität ohne Referenzübersetzung. |
| **FST** | Finite-State Transducer — ein Rechenmechanismus, der die morphologischen Regeln einer Sprache kodiert. |
| **GiellaLT** | Infrastruktur für regelbasierte Sprachtechnologie, primär für Samisch und andere arktische Sprachen. |
| **HFST** | Helsinki Finite-State Technology — das Software-Framework, das GiellaLT und Apertium zugrunde liegt. |
| **SRO** | Standard Roman Orthography — das lateinbasierte Schriftsystem für Plains Cree. |
| **Silbenschrift (Syllabics)** | Canadian Aboriginal Syllabics — ein Abugida-Schriftsystem, das für Cree und andere Algonkin-Sprachen verwendet wird. |
| **Polysynthetisch** | Ein Sprachtyp, bei dem ein einzelnes Wort durch umfangreiche Affigierung das Äquivalent eines ganzen englischen Satzes kodieren kann. |
| **Obviation** | Eine grammatikalische Kategorie in den Algonkin-Sprachen, die zwischen zwei Referenten der dritten Person unterscheidet. |
| **Invers** | Eine genusartige Kategorie in den Algonkin-Sprachen, die markiert, dass der Patiens den Agens auf der Belebtheitshierarchie übertrifft. |
| **WMT** | Conference on Machine Translation — der primäre Ort für MT Shared Tasks und Evaluierung. |
| **Kontrastive Evaluierung** | Testen, ob ein System minimal verschiedene Eingaben unterscheiden kann, die unterschiedliche Ausgaben erfordern. |
| **Challenge Set** | Eine gefertigte Testsuite, die auf spezifische linguistische Phänomene abzielt. |
| **Äquivalenzklasse** | Eine Menge unterschiedlicher Oberflächenformen, die dieselbe Bedeutung repräsentieren und denselben Evaluierungs-Score erhalten sollten. |