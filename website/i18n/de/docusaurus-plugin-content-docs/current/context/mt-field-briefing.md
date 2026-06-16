# Maschinelle Übersetzung: Ein Lagebericht (2013–2026)

*Eine narrative Geschichte für alle, die in die MT-Landschaft einsteigen*

---

## Inhaltsverzeichnis

- [Teil 1: Die neuronale Revolution (2013–2017)](#part-1-the-neural-revolution-20132017)
- [Teil 2: Die multilinguale Wende (2018–2022)](#part-2-the-multilingual-turn-20182022)
- [Teil 3: Die LLM-Ära (2022–2026)](#part-3-the-llm-era-20222026)
- [Teil 4: Das Low-Resource-Problem](#part-4-the-low-resource-problem)
- [Teil 5: Finite-State-Transduktoren und regelbasierte Systeme](#part-5-finite-state-transducers-and-rule-based-systems)
- [Teil 6: Qualität messen — Das Evaluationsproblem](#part-6-measuring-quality--the-evaluation-problem)
- [Teil 7: Die institutionelle Landschaft](#part-7-the-institutional-landscape)
- [Teil 8: Offene Fronten](#part-8-open-frontiers)
- [Anhang A: Wichtige Arbeiten](#appendix-a-key-papers)
- [Anhang B: Konferenzen und Communities](#appendix-b-conferences-and-communities)
- [Anhang C: Werkzeuge, Datensätze und praktische Ressourcen](#appendix-c-tools-datasets-and-practical-resources)
- [Anhang D: Glossar](#appendix-d-glossary)

---

## Teil 1: Die neuronale Revolution (2013–2017)

### Das alte Regime: Statistische maschinelle Übersetzung

Um die Revolution zu verstehen, die die maschinelle Übersetzung Mitte der 2010er-Jahre neu gestaltete, müssen Sie zunächst verstehen, was ihr vorausging — und warum es scheiterte.

Von etwa 2003 bis 2015 war das vorherrschende Paradigma in der MT die **statistische maschinelle Übersetzung (SMT)**, genauer gesagt die **phrasenbasierte SMT**. Die Grundidee war trügerisch einfach: Anstatt Regeln darüber zu schreiben, wie Sprache funktioniert, sammelt man riesige Mengen an Paralleltext — von Menschen in zwei Sprachen übersetzte Dokumente — und lässt statistische Algorithmen die Entsprechungen lernen. Das System zerlegte einen Ausgangssatz in überlappende Phrasen (keine linguistischen Phrasen, sondern beliebige n-Gramm-Segmente), fand statistisch wahrscheinliche Übersetzungen für jedes Segment und setzte dann einen Zielsatz mithilfe eines **Sprachmodells** zusammen, das sicherstellte, dass die Ausgabe flüssig war.

Das Arbeitspferd dieser Ära war **Moses**, ein Open-Source-SMT-Toolkit, das hauptsächlich an der University of Edinburgh unter Philipp Koehn entwickelt und 2006 veröffentlicht wurde. Moses wurde zum Linux der MT-Forschung — praktisch jedes akademische MT-Labor der Welt nutzte es. Sein Begleiter, **cdec** (entwickelt von Chris Dyer an der Carnegie Mellon), bot ähnliche Fähigkeiten mit einem anderen Formalismus. Zusammen prägten diese Werkzeuge ein Jahrzehnt der MT-Forschung.

Phrasenbasierte SMT funktionierte überraschend gut für Sprachpaare mit reichlich vorhandenen Paralleldaten und ähnlicher Wortstellung — Englisch–Französisch, Englisch–Spanisch, Englisch–Deutsch. Doch sie hatte tiefgreifende strukturelle Einschränkungen. Das System hatte kein Konzept von Bedeutung. Es war Mustererkennung über Oberflächenzeichenketten, das Übersetzungen aus auswendig gelernten Fragmenten zusammensetzte. Es hatte Schwierigkeiten mit weitreichenden Abhängigkeiten (ein Pronomen, das sich auf ein mehrere Teilsätze zurückliegendes Nomen bezieht), mit der Umordnung zwischen typologisch unterschiedlichen Sprachen (Englisch–Japanisch etwa, wo Verben in entgegengesetzten Positionen erscheinen) und mit jedem Phänomen, das eine echte Abstraktion über Sprachstruktur erforderte. Jede Verbesserung verlangte zunehmend barocke Ingenieursarbeit: handgefertigte Umordnungsregeln, dünn besetzte Merkmale, riesige Sprachmodelle. Die Architektur näherte sich ihrer Obergrenze.

### Der Durchbruch: Sequence-to-Sequence mit Attention

Der erste Riss im SMT-Paradigma kam nicht aus der MT-Community, sondern von Deep-Learning-Forschern, die an Problemen der Sequenzmodellierung arbeiteten.

Im September 2014 veröffentlichten **Dzmitry Bahdanau, Kyunghyun Cho und Yoshua Bengio** an der Université de Montréal eine Arbeit, die sich als transformativ erweisen sollte: ["Neural Machine Translation by Jointly Learning to Align and Translate"](https://arxiv.org/abs/1409.0473) (vorgestellt auf der ICLR 2015). Die entscheidende Neuerung war der **Attention-Mechanismus**.

Um zu verstehen, warum dies von Bedeutung war, benötigen Sie den vorherigen Kontext. Nur Monate zuvor hatten Ilya Sutskever, Oriol Vinyals und Quoc V. Le bei Google ["Sequence to Sequence Learning with Neural Networks"](https://arxiv.org/abs/1409.3215) (NIPS 2014) veröffentlicht und gezeigt, dass ein neuronales Netz mit einer **Encoder-Decoder**-Architektur Sätze übersetzen konnte. Der Encoder liest den Ausgangssatz Wort für Wort und komprimiert ihn zu einem einzigen Vektor fester Länge — einer numerischen Zusammenfassung der gesamten Eingabe. Der Decoder erzeugt dann Wort für Wort den Zielsatz aus diesem Vektor.

Dies war elegant, hatte aber einen kritischen Fehler: Der einzelne Vektor war ein **Flaschenhals**. Alle Informationen in einem dreißig Wörter umfassenden Ausgangssatz mussten durch einen einzigen Vektor von etwa 1.000 Zahlen gepresst werden. Kurze Sätze wurden recht gut übersetzt; lange Sätze verschlechterten sich stark, weil das Modell frühere Wörter vergessen hatte, bis es spätere fertig kodiert hatte.

Bahdanaus Attention-Mechanismus löste dies. Anstatt die gesamte Quelle in einen Vektor zu komprimieren, durfte der Decoder auf alle verborgenen Zustände des Encoders **zurückblicken** — die Zwischenrepräsentationen an jeder Ausgangsposition — und dynamisch gewichten, welche Positionen für die Erzeugung jedes Zielworts am relevantesten waren. Beim Erzeugen des englischen Worts „cat" konnte das Modell am stärksten auf das französische Wort „chat" in der Quelle achten, selbst wenn diese im Satz weit voneinander entfernt waren. Das Modell lernte, Quell- und Zielwörter als Teil des Übersetzungsprozesses *auszurichten*, anstatt sich auf eine einzige komprimierte Zusammenfassung zu verlassen.

Dies war die grundlegende Neuerung. Attention verbesserte nicht nur die MT; es wurde zum zentralen Mechanismus praktisch aller nachfolgenden Fortschritte in der natürlichen Sprachverarbeitung.

### Google wird neuronal

Die akademischen Ergebnisse von 2014–2015 waren beeindruckend, aber noch nicht produktionsreif. Das änderte sich Ende 2016.

Im September 2016 veröffentlichte ein großes Team bei Google unter der Leitung von **Yonghui Wu** ["Google's Neural Machine Translation System: Bridging the Gap Between Human and Machine Translation"](https://arxiv.org/abs/1609.08144). Das System, bekannt als **GNMT** (Google Neural Machine Translation), war eine Encoder-Decoder-Architektur im Industriemaßstab mit Attention, trainiert auf Googles riesigen Paralleldatenressourcen. Die Arbeit machte eine bemerkenswerte Behauptung: Bei bestimmten Sprachpaaren reduzierte GNMT die Übersetzungsfehler um 55–85 % gegenüber Googles bestehendem phrasenbasiertem SMT-System.

Im November 2016 begann Google, Google Translate für wichtige Sprachpaare stillschweigend von phrasenbasierter SMT auf GNMT umzustellen. Der Übergang war für ressourcenstarke Paare bis 2017 im Wesentlichen abgeschlossen. Für die Nutzer war die Veränderung dramatisch. Übersetzungen, die zuvor gestelzt, fragmentiert und gelegentlich unsinnig gewirkt hatten, wurden wesentlich flüssiger — manchmal verblüffend so. Die Ära des „Google-Translate-Kauderwelschs" als Pointe ging zu Ende.

Die Reaktion der Konkurrenz erfolgte schnell. Im August 2017 startete **DeepL**, gegründet von **Gereon Frahling** in Köln, Deutschland, seinen Übersetzungsdienst. DeepL war aus dem zweisprachigen Konkordanzprojekt Linguee hervorgegangen und differenzierte sich durch die wahrgenommene Übersetzungsqualität — insbesondere für europäische Sprachpaare, wo es sich unter professionellen Übersetzern schnell einen Ruf für natürlichere, idiomatischere Ausgaben als Google erwarb. DeepLs Geschäftsmodell (Freemium mit kostenpflichtiger API) und sein Fokus auf Qualität statt Breite sollten seine Marktposition künftig prägen. Stand 2025 unterstützt DeepL etwa 33 Sprachen — weit weniger als Googles 240+, aber mit einer qualitätsorientierten Positionierung.

### Der Transformer

Wenn Bahdanaus Attention-Mechanismus das Fundament war, dann war der **Transformer** das darauf errichtete Gebäude — und das Gebäude war ein Wolkenkratzer.

Im Juni 2017 veröffentlichte ein Team von acht Forschern bei Google — **Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Łukasz Kaiser und Illia Polosukhin** — ["Attention Is All You Need"](https://arxiv.org/abs/1706.03762) auf der NIPS 2017. Der Titel war keine Übertreibung; er war eine präzise architektonische Aussage. Wo frühere Modelle rekurrente neuronale Netze (RNNs) als Rückgrat verwendeten — die Wörter sequenziell, eines nach dem anderen verarbeiteten, wie das Lesen eines Satzes von links nach rechts — verzichtete der Transformer vollständig auf Rekurrenz und stützte sich ausschließlich auf Attention.

Die entscheidenden Neuerungen waren:

1. **Self-Attention**: Jedes Wort in einem Satz achtet auf jedes andere Wort im selben Satz und berechnet Beziehungen parallel statt sequenziell. Dies erfasst weitreichende Abhängigkeiten ohne den Informationsflaschenhals der RNNs und — entscheidend — parallelisiert auf moderner Hardware (GPUs und TPUs), wodurch das Training dramatisch schneller wird.

2. **Multi-Head-Attention**: Anstatt ein einziges Attention-Muster zu berechnen, berechnet das Modell mehrere Attention-Muster gleichzeitig („Heads"), von denen jedes potenziell unterschiedliche Arten linguistischer Beziehungen erfassen kann — syntaktische, semantische, positionelle.

3. **Positional Encoding**: Da Self-Attention alle Wörter gleichzeitig verarbeitet (anders als RNNs, die sequenziell verarbeiten), hat das Modell keinen inhärenten Begriff von Wortreihenfolge. Positional Encodings — mathematische Funktionen, die in die Eingabe eingespeist werden — liefern diese Information.

Der Transformer übertraf RNN-basierte Modelle bei Übersetzungs-Benchmarks nicht nur. Er trainierte aufgrund seiner Parallelität **um Größenordnungen schneller**. Dies war wohl ebenso wichtig wie die Qualitätsverbesserung: Forscher konnten nun schneller iterieren, mit mehr Daten trainieren und auf größere Modelle skalieren. Der Tugendkreis der Skalierung hatte begonnen.

Innerhalb von zwei Jahren war die Transformer-Architektur zum Substrat für im Wesentlichen alle hochmodernen Arbeiten in der NLP geworden — nicht nur MT, sondern Sprachmodellierung, Textklassifikation, Beantwortung von Fragen, Zusammenfassung und schließlich die großen Sprachmodelle (GPT, BERT, LLaMA), die die breitere KI-Landschaft umgestalten sollten. Jedes System, das im verbleibenden Teil dieses Lageberichts erörtert wird, baut auf dem Transformer auf.

### Die Wasserscheide WMT 2016

Die **Conference on Machine Translation** (WMT), die jährlich als Workshop in Verbindung mit großen NLP-Konferenzen stattfindet, betreibt kompetitive **Shared Tasks**, bei denen Forschungsteams MT-Systeme einreichen und auf standardisierten Testdatensätzen gegeneinander gerankt werden. WMT ist das, was einer öffentlichen Bestenliste im MT-Bereich am nächsten kommt.

Auf der **WMT 2016** übertrafen neuronale MT-Systeme phrasenbasierte SMT-Systeme bei praktisch allen Sprachpaaren im Shared Task entscheidend. Dies war der Moment, in dem sich der Schwerpunkt des Feldes verschob. Forscher, die ihre Karrieren mit dem Bau phrasenbasierter Systeme verbracht hatten, begannen, sich auf das neuronale Paradigma umzustellen. Innerhalb von zwei Jahren hatten neue Veröffentlichungen, die phrasenbasierte SMT für etwas anderes als historische Vergleiche verwendeten, im Wesentlichen aufgehört. Moses, das Werkzeug, das ein Jahrzehnt geprägt hatte, war faktisch außer Dienst gestellt.

Der Übergang war nach den Maßstäben akademischer Paradigmenwechsel bemerkenswert schnell — etwa drei bis vier Jahre von Bahdanaus Arbeit von 2014 bis zur nahezu vollständigen Dominanz der neuronalen MT bis 2018. Für eine Forscherin, die heute in das Feld einsteigt, ist phrasenbasierte SMT historischer Kontext, keine lebendige Forschungsrichtung. Doch es ist wesentlicher Kontext, denn die Annahmen, Benchmarks und Evaluationsgewohnheiten der SMT-Ära hallen noch immer durch das Feld.

---

## Teil 2: Die multilinguale Wende (2018–2022)

### Ein Modell, viele Sprachen

Die erste Generation neuronaler MT-Systeme war **bilingual**: ein Modell pro Sprachpaar. Englisch–Französisch erforderte ein Modell; Französisch–Englisch ein separates. Die Skalierung dieses Ansatzes auf N Sprachen erforderte theoretisch N×(N−1) Modelle — ein Engpass in Bezug auf Ingenieursarbeit und Daten, der die neuronale MT faktisch auf eine Handvoll gut ausgestatteter Paare beschränkte.

Die Frage, die 2018–2022 prägte, lautete: *Kann ein einzelnes neuronales Modell lernen, zwischen vielen Sprachen gleichzeitig zu übersetzen?* Die Antwort stellte sich als Ja heraus, mit tiefgreifenden und komplizierten Folgen.

### Sprachübergreifende Repräsentationen: mBERT und XLM-R

Bevor multilinguale Übersetzungsmodelle auftauchten, bereitete eine unerwartete Entdeckung bei Modellen zum Sprach*verständnis* die Bühne.

Ende 2018 veröffentlichte Google **Multilingual BERT (mBERT)** — ein einzelnes Transformer-Modell, trainiert auf Wikipedia-Text aus 104 Sprachen. BERT (Bidirectional Encoder Representations from Transformers) war kein Übersetzungsmodell; es war ein universeller Sprach-Encoder, trainiert darauf, maskierte Wörter im Text vorherzusagen. Was die Forscher verblüffte, war eine emergente Eigenschaft: mBERT entwickelte **sprachübergreifende Repräsentationen**, ohne jemals explizit gelehrt worden zu sein, dass Sprachen verwandt sind. Wenn man mBERT auf einer englischen Sentiment-Klassifikationsaufgabe feinjustierte und es dann auf französischen Text anwandte — ganz ohne französische Trainingsdaten — schnitt es bemerkenswert gut ab. Dieses Phänomen, genannt **Zero-Shot-Cross-Lingual-Transfer**, deutete darauf hin, dass multilinguale Modelle eine Art gemeinsamen Repräsentationsraum über Sprachen hinweg erlernten.

Im Jahr 2020 trieben **Alexis Conneau** und Kollegen bei Facebook AI Research (heute Meta) dies mit **XLM-R** (Cross-lingual Language Model – RoBERTa) weiter voran. Trainiert auf 2,5 Terabyte gefilterter CommonCrawl-Daten über 100 Sprachen hinweg, übertraf XLM-R mBERT bei sprachübergreifenden Benchmarks deutlich. Es zeigte, dass mit genügend Daten und Modellkapazität ein einzelner Encoder robuste multilinguale Repräsentationen aufbauen konnte.

Diese Modelle waren selbst keine Übersetzer, aber sie lieferten das konzeptionelle und technische Fundament für die multilinguale MT. Wenn ein Modell gemeinsame Repräsentationen über 100 Sprachen hinweg erlernen konnte, dann sollte ein Übersetzungsmodell zwischen ihnen übersetzen können — zumindest im Prinzip.

### Many-to-Many-Übersetzung: M2M-100

Traditionelle multilinguale MT-Systeme hatten ein schmutziges Geheimnis: Sie leiteten die meisten Übersetzungen **über das Englische**. Von Portugiesisch nach Japanisch zu übersetzen bedeutete, zunächst Portugiesisch ins Englische und dann Englisch ins Japanische zu übersetzen. Dieser „englischzentrierte" Ansatz war pragmatisch — die meisten Paralleldaten haben Englisch auf einer Seite — aber er führte zu sich verstärkenden Fehlern und drückte jeder Übersetzung eine englischsprachige Struktur auf.

Im Oktober 2020 veröffentlichte Facebook AI **M2M-100** (Fan et al., ["Beyond English-Centric Multilingual Machine Translation"](https://arxiv.org/abs/2010.11125), JMLR 2021): ein Many-to-Many-Übersetzungsmodell, das **100 Sprachen und 2.200 Übersetzungsrichtungen** abdeckte, ohne über das Englische zu leiten. Dies war ein konzeptioneller Durchbruch. Das Modell konnte direkt zwischen, sagen wir, Bengali und Suaheli übersetzen, unter Verwendung von Paralleldaten, die für nicht-englische Paare aus dem Web gewonnen wurden.

M2M-100 bewies, dass das englische Pivoting keine notwendige Einschränkung der multilingualen MT war. Doch es offenbarte auch die Grenzen des Ansatzes: Die Qualität war über die Sprachpaare hinweg sehr ungleichmäßig, wobei einige Richtungen kaum nutzbar waren. Die Lücke zwischen „dieses Modell *deckt* 2.200 Richtungen ab" und „dieses Modell *funktioniert gut* in 2.200 Richtungen" sollte ein zentrales Thema werden.

### NLLB-200: No Language Left Behind

Metas ehrgeizigstes multilinguales MT-Vorhaben erschien im Juli 2022 mit **NLLB-200** (["No Language Left Behind: Scaling Human-Centered Machine Translation"](https://arxiv.org/abs/2207.04672), veröffentlicht als Meta-AI-Forschungsarbeit mit über 200 Co-Autoren). Das Ziel war im Namen explizit: ein einzelnes Modell zu bauen, das 200 Sprachen unterstützt, mit besonderem Fokus auf ressourcenarme Sprachen, die bisher von kommerzieller MT ignoriert wurden.

Die technischen Beiträge von NLLB-200 waren beträchtlich:

- **Architektur**: Ein dichter Transformer und eine **Mixture-of-Experts (MoE)**-Variante, bei der unterschiedliche Teilmengen der Modellparameter für unterschiedliche Sprachpaare aktiviert werden. Die größte Variante, NLLB-200-MoE-54B, hatte 54 Milliarden Parameter. Eine destillierte Version mit 600 Mio. Parametern machte den Einsatz praktikabel.

- **Data Mining**: Das Team entwickelte automatisierte Werkzeuge zum Schürfen paralleler Sätze aus Web-Crawls, einschließlich eines Spracherkennungsmodells (das 200+ Sprachen abdeckt) und eines Filters für parallele Sätze. Diese Pipeline war entscheidend für die Sammlung von Trainingsdaten für Sprachen mit minimaler Webpräsenz.

- **FLORES-200**: Ein standardisierter Evaluations-Benchmark, der alle 200 Sprachen mit professionell übersetzten Sätzen abdeckt. FLORES-200 wurde zu einem wesentlichen Werkzeug für das Feld — zuvor existierte für die meisten dieser Sprachen kein Benchmark.

- **Offene Veröffentlichung**: Sowohl das Modell als auch FLORES-200 wurden offen veröffentlicht, was Forschern weltweit ermöglichte, auf der Arbeit aufzubauen.

NLLB-200 war ein Meilenstein, aber seine Einschränkungen sind ebenso wichtig zu verstehen. Die Qualität variierte enorm über die Sprachen hinweg. Für gut ausgestattete Paare (Englisch–Französisch, Englisch–Chinesisch) war das Modell kompetent, aber nicht hochmodern im Vergleich zu spezialisierten Systemen. Für ressourcenarme Sprachen reichte die Ausgabequalität von nützlich bis im Wesentlichen funktionsuntüchtig, je nachdem, wie viele Trainingsdaten geschürft worden waren. Das Modell zeigte auch den **Fluch der Multilingualität**: Das Hinzufügen weiterer Sprachen zu einem Modell mit fester Kapazität verwässert die Repräsentationsqualität für jede einzelne Sprache. Ressourcenarme Sprachen profitieren vom Transferlernen (gemeinsame Struktur mit verwandten Sprachen), aber ressourcenstarke Sprachen können tatsächlich *schlechter* werden, wenn das Modell versucht, zu vielen Herren zu dienen. Dies ist nicht bloß ein Skalierungsproblem — es spiegelt eine grundlegende Spannung im Design multilingualer Modelle wider.

### Die Seamless-Suite

Meta trieb die multilinguale MT mit der **Seamless**-Modellfamilie in den Jahren 2023–2024 weiter voran. **SeamlessM4T** („Massively Multilingual and Multimodal Machine Translation", August 2023) war ein einzelnes Modell, das **Sprache-zu-Sprache-, Sprache-zu-Text-, Text-zu-Sprache- und Text-zu-Text-Übersetzung** über etwa 100 Sprachen hinweg bewältigte (mit unterschiedlicher Abdeckung über die Modalitäten hinweg). Dies stellte eine Konvergenz zuvor getrennter Forschungsstränge dar — automatische Spracherkennung (ASR), Textübersetzung und Text-zu-Sprache (TTS) — in einem einheitlichen multilingualen System.

Die nachfolgende **Seamless Communication**-Suite fügte Streaming-Fähigkeiten (nahezu Echtzeit-Übersetzung) und expressive Sprachübersetzung hinzu (Erhaltung von Stimmmerkmalen wie Emotion und Sprechstil über Sprachen hinweg). Diese Systeme bleiben Forschungsprototypen statt produktionsreifer Werkzeuge, aber sie signalisieren die Richtung des Feldes: multimodal, multilingual und in Echtzeit.

### Was „massiv multilingual" in der Praxis bedeutet

Für eine Forscherin, die in dieses Feld einsteigt, ist es entscheidend, zwischen der **Sprachabdeckung** eines Modells und seiner **Sprachqualität** zu unterscheiden. Ein Modell, das „200 Sprachen unterstützt", liefert möglicherweise exzellente Übersetzungen für 20 davon, brauchbare Ausgaben für 50 und im Wesentlichen zufälligen Text für den Rest. Die Schlagzeilenzahl ist ohne sprachspezifische Qualitätsbewertung irreführend.

Der **Fluch der Multilingualität** ist der Fachbegriff für das Problem der Kapazitätsverwässerung: Ein Modell mit endlichen Parametern kann nicht alle Sprachen gleich gut repräsentieren. Das Hinzufügen weiterer Sprachen kommt den ressourcenärmsten Sprachen zugute (durch sprachübergreifenden Transfer von verwandten Sprachen), schadet aber den ressourcenstärksten (durch den Verbrauch von Kapazität, die ihnen hätte gewidmet werden können). Dies schafft eine Designspannung: Baut man ein universelles Modell oder viele spezialisierte? Das Feld hat diese Frage nicht gelöst.

---

## Teil 3: Die LLM-Ära (2022–2026)

### Als universelle KI das Übersetzen lernte

Die Ankunft großer Sprachmodelle (LLMs) — GPT-3.5/4, Gemini, Claude, LLaMA — schuf eine seltsame Situation im MT-Bereich. Diese Modelle wurden nicht speziell für die Übersetzung trainiert. Sie wurden trainiert, das nächste Token in riesigen Textkorpora vorherzusagen, vorwiegend englisch, aber zunehmend multilingual. Dennoch erzeugten sie, wenn man sie mit Anweisungen wie „Übersetze den folgenden französischen Satz ins Englische" anregte, Übersetzungen, die für ressourcenstarke Sprachpaare verblüffend gut waren.

Dies stellte das Feld vor eine Identitätsfrage: Wenn universelle KI ebenso gut übersetzen kann wie zweckgebaute Übersetzungssysteme, bleibt „maschinelle Übersetzung" dann ein eigenständiges Forschungsgebiet? Die Antwort lautet, Stand 2026, ein eingeschränktes Ja — aber die Beziehung zwischen MT-Forschung und der Entwicklung universeller LLMs ist tief verwoben geworden.

### Die ersten Benchmarks: LLMs vs. dedizierte MT

Die systematische Evaluation von LLMs für die Übersetzung begann Anfang 2023, kurz nach der Veröffentlichung von ChatGPT (November 2022) und GPT-4 (März 2023).

**Jiao et al. (2023)** lieferten in ["Is ChatGPT A Good Translator? Yes With GPT-4 As The Engine"](https://arxiv.org/abs/2301.08745) eine frühe Bewertung. Ihre Erkenntnisse begründeten ein Muster, das bemerkenswert stabil geblieben ist: LLMs sind **für ressourcenstarke europäische Sprachpaare hochgradig konkurrenzfähig** (Englisch–Deutsch, Englisch–Französisch, Englisch–Chinesisch) und **deutlich schwächer für ressourcenarme und typologisch entfernte Paare**. Sie führten auch das **Pivot-Prompting** ein — die Anweisung an das Modell, über eine Zwischensprache zu übersetzen — was die Leistung bei schwierigen Paaren verbesserte.

**Hendy et al. (2023)** bei Microsoft ([arXiv:2302.09210](https://arxiv.org/abs/2302.09210)) führten eine umfassendere Evaluation über 18 Übersetzungsrichtungen durch. Ihre Schlussfolgerung: GPT-Modelle konkurrierten mit hochmoderner kommerzieller MT für ressourcenstarke Paare, hatten aber bei ressourcenarmen Sprachen „begrenzte Fähigkeit".

Bis 2024–2025 hatte sich das Bild geschärft. Für **ressourcenstarke Paare** erreichten oder übertrafen die besten LLMs (GPT-4o, Gemini 2.5 Pro, Claude 3.5 Sonnet) dedizierte MT-Systeme, insbesondere bei Aufgaben, die kontextuelles Verständnis, idiomatischen Ausdruck und dokumentenweite Kohärenz erforderten — Bereiche, mit denen traditionelle neuronale MT, die Sätze isoliert verarbeitet, schon immer Schwierigkeiten hatte. Für **ressourcenarme Paare** übertreffen dedizierte multilinguale Modelle wie NLLB-200 und die zweckgebauten Systeme von Google Translate die LLMs weiterhin, oft deutlich.

### BLOOM: Der offene multilinguale Moment

Im Juli 2022 veröffentlichte die kollaborative Initiative **BigScience** — ein einjähriges, von Hugging Face koordiniertes freiwilliges Bemühen, an dem Hunderte von Forschern weltweit beteiligt waren — **BLOOM**: ein offen zugängliches multilinguales Sprachmodell mit 176 Milliarden Parametern, das **46 natürliche Sprachen und 13 Programmiersprachen** abdeckte. Trainiert auf dem ROOTS-Korpus unter Verwendung des Supercomputers Jean Zay in Frankreich, war BLOOM das erste wirklich massive offen zugängliche multilinguale LLM.

BLOOM war kein dedizierter Übersetzer, aber seine Bedeutung für die MT war erheblich. Es zeigte, dass Open-Source-Modelle Dutzende von Sprachen im großen Maßstab unterstützen konnten und damit eine Grundlage für multilinguale Forschung außerhalb von Unternehmenslaboren bildeten. Seine instruktionsjustierte Variante, **BLOOMZ**, zeigte sprachübergreifende Generalisierungsfähigkeiten — auf Aufgaben in einer Sprache feinjustiert, konnte es diese in anderen ausführen.

### LLaMA und die Feinjustierungs-Explosion

Metas **LLaMA**-Reihe (Large Language Model Meta AI), beginnend im Februar 2023, schlug einen anderen Weg ein. LLaMA 1 war vorwiegend englischzentriert, mit begrenzter multilingualer Fähigkeit. LLaMA 2 (Juli 2023) verbesserte sich geringfügig, klassifizierte die nicht-englische Nutzung aber weiterhin als „außerhalb des Anwendungsbereichs". Der Wendepunkt kam mit **LLaMA 3** (April 2024), das die Trainingsdaten versiebenfachte und ein Vokabular von 128.000 Token einführte — was die Kodierung von nicht-englischem Text dramatisch verbesserte. LLaMA 3 unterstützte offiziell acht Sprachen (Englisch, Deutsch, Französisch, Italienisch, Portugiesisch, Hindi, Spanisch, Thai) mit unterschiedlicher Qualität für viele weitere.

LLaMAs Bedeutung für die MT liegt weniger in seiner direkten Übersetzungsfähigkeit als in seiner Rolle als **Basismodell für die Feinjustierung**. Beide der unten erörterten spezialisierten Übersetzungs-LLMs — Tower und ALMA — bauen auf LLaMA auf. Die offenen Gewichte schufen ein florierendes Ökosystem spezialisierter Derivate.

### Zweckgebaute Übersetzungs-LLMs: Tower und ALMA

Die bedeutendste Entwicklung von 2023–2024 war das Aufkommen von LLMs, die speziell für die Übersetzung feinjustiert wurden — Hybridsysteme, die die kontextuelle Raffinesse universeller LLMs erben, aber auf Übersetzungsqualität optimiert sind.

**ALMA** (Advanced Language Model-based trAnslator), entwickelt von **Haoran Xu** und Kollegen an der Johns Hopkins University, demonstrierte eine zentrale Einsicht: Man braucht keine riesigen Parallelkorpora, um einen exzellenten Übersetzer zu bauen. ALMA verwendete einen **zweistufigen Feinjustierungs**-Ansatz auf LLaMA-2: zunächst fortgesetztes Vortraining auf nicht-englischen einsprachigen Daten zur Erweiterung des multilingualen Wissens; dann Feinjustierung auf einem kleinen, hochwertigen Paralleldatensatz. Die Folgeversion, **ALMA-R** (Januar 2024), führte die **Contrastive Preference Optimisation (CPO)** ein — das Training des Modells auf Präferenzdaten (bessere vs. schlechtere Übersetzungen) anstatt nur auf Paralleltext. Das Ergebnis: Modelle mit 7B und 13B Parametern, die GPT-4 bei Übersetzungs-Benchmarks erreichten oder übertrafen. Die Arbeit wurde auf der ICLR 2024 veröffentlicht ([arXiv:2309.11674](https://arxiv.org/abs/2309.11674)). Eine spätere Version, **X-ALMA**, erweiterte die Abdeckung auf 50 Sprachen unter Verwendung sprachspezifischer Plug-and-Play-Module.

**Tower**, entwickelt von **Unbabel** (einem portugiesischen KI-Übersetzungsunternehmen) in Zusammenarbeit mit dem SARDINE Lab und dem MICS Lab, nahm eine breitere Perspektive ein. Anstatt allein auf die Übersetzung zu optimieren, deckte Tower die **gesamte Übersetzungspipeline** ab: Quellkorrektur, Eigennamenerkennung, Nachbearbeitung, Übersetzungsranking und Fehlererkennung. Die anfänglichen Tower-Modelle (7B und 13B, basierend auf LLaMA-2) übertrafen NLLB-200-54B. **Tower v2** (70B, vorgestellt auf der WMT 2024) übertraf GPT-4o, Claude 3.5 Sonnet und DeepL. Das neueste **Tower+** (2025) erweiterte sich auf 22–27 Sprachen und adressierte das „katastrophale Vergessen" — die Neigung feinjustierter Modelle, allgemeine Fähigkeiten zu verlieren — durch Präferenzoptimierung und bestärkendes Lernen.

### Prompting vs. Feinjustierung: Die anhaltende Debatte

Eine beharrliche Frage im LLM-MT-Bereich ist, ob es besser ist, ein universelles LLM zur Übersetzung zu **prompten** (Zero-Shot oder Few-Shot) oder ein Modell speziell für die Übersetzung **feinzujustieren**. Die Evidenz legt nahe, dass die Antwort aufgabenabhängig ist:

- **Prompting** erhält die allgemeinen Fähigkeiten des LLM — Formalitätssteuerung, Stilkontrolle, dokumentenweite Kohärenz — und erfordert kein zusätzliches Training. Es ist ideal für schnelle Iteration sowie kreative oder kontextuelle Übersetzung.
- **Feinjustierung** erzeugt höhere Genauigkeit bei bestimmten Sprachpaaren und Domänen, riskiert aber die Verschlechterung anderer Fähigkeiten („katastrophales Vergessen"). Sie erfordert Paralleldaten und Rechenleistung.
- **Hybride Ansätze** sind in der Praxis zunehmend dominant: feinjustierte Modelle für die anfängliche Übersetzung, mit LLM-basierten Nachbearbeitungs- oder Selbstverfeinerungsdurchläufen.

### Der aktuelle Stand der Technik (2025–2026)

Die ehrliche Antwort auf „Was ist das beste MT-System?" lautet: **Es kommt darauf an.**

| Anwendungsfall | Bester Ansatz | Warum |
|---|---|---|
| Ressourcenstark, hohes Volumen | Kommerzielle NMT (Google, DeepL) | Geschwindigkeit, Kosten, Konsistenz |
| Ressourcenstark, hohe Qualität | LLMs (GPT-4o, Gemini 2.5 Pro) oder Tower+ | Kontextuelles Verständnis, Idiom-Behandlung |
| Ressourcenarm, breite Abdeckung | Meta OMT, NLLB-200, Google Translate | Zweckgebaute multilinguale Abdeckung |
| Ressourcenarm, spezifisches Paar | Feinjustiertes NLLB oder LLM auf Domänendaten | Gezielte Qualitätsverbesserung |
| Open-Source-Forschung | Tower+, ALMA-R, X-ALMA | Offene Gewichte, reproduzierbar, konkurrenzfähig |

Im März 2026 veröffentlichte Meta **OMT (Omnilingual Machine Translation)** — den Nachfolger von NLLB-200, der die Abdeckung von 200 auf **1.600+ Sprachen** erweitert. OMT adressiert, was Meta den „Generierungs-Flaschenhals" nennt: Große Sprachmodelle können viele Sprachen verstehen, haben aber Schwierigkeiten, flüssigen Text in ihnen zu erzeugen. OMT kommt in zwei Architekturen — OMT-LLaMA (nur Decoder, 1B–8B Parameter) und OMT-NLLB (Encoder-Decoder) — und führt neue Evaluationswerkzeuge ein, darunter BOUQuET und BLASER 3 (eine referenzfreie Qualitätsschätzungsmetrik). Frühe Berichte deuten darauf hin, dass die Modelle mit 1B–8B Parametern 70B-LLM-Baselines bei Übersetzungsaufgaben erreichen oder übertreffen. Ob OMT schließlich Plains Cree oder andere algonkische Sprachen umfassen wird, bleibt abzuwarten.

Die Erkenntnisarbeit zum WMT-2024-Shared-Task trug treffend den Titel **„The LLM Era Is Here but MT Is Not Solved Yet."** LLMs haben die Obergrenze für ressourcenstarke Übersetzung angehoben, aber die grundlegenden Herausforderungen ressourcenarmer MT, der Evaluationsangemessenheit oder der morphologischen Komplexität nicht gelöst.

---

## Teil 4: Das Low-Resource-Problem

### Warum die meisten Sprachen zurückgelassen werden

Von den weltweit etwa 7.000 lebenden Sprachen decken kommerzielle MT-Systeme bestenfalls 200–250 ab. Die überwiegende Mehrheit der Sprachen hat **überhaupt keine maschinelle Übersetzung**. Um zu verstehen, warum, muss man verstehen, was MT-Systeme benötigen und was den meisten Sprachen fehlt.

Neuronale MT erfordert **Paralleldaten**: große Sammlungen von Sätzen, die von Menschen zwischen zwei Sprachen übersetzt wurden. Für Englisch–Französisch existieren diese Daten in Hülle und Fülle — EU-Parlamentsprotokolle (Europarl), UN-Dokumente, Nachrichtenarchive und kommerzielle Translation Memories liefern Hunderte Millionen paralleler Sätze. Für eine Sprache wie Plains Cree (*nêhiyawêwin*), die von etwa 27.000 Menschen hauptsächlich im westlichen Kanada gesprochen wird, existieren solche Daten im Wesentlichen nicht. Es gibt keine UN-Protokolle in Plains Cree. Es gibt keine zweisprachigen Nachrichtenkorpora. Der gesamte verfügbare Paralleltext könnte eher in Tausenden von Sätzen als in Millionen gemessen werden.

Das Feld verwendet grobe Ressourcenstufen, um Sprachen zu kategorisieren:

| Stufe | Verfügbare Paralleldaten | Beispiele |
|---|---|---|
| Ressourcenstark | >10 Millionen Satzpaare | Englisch, Französisch, Deutsch, Chinesisch, Spanisch |
| Mittel ausgestattet | 1–10 Millionen Paare | Türkisch, Vietnamesisch, Suaheli |
| Ressourcenarm | 100K–1 Million Paare | Yoruba, Guaraní, Maltesisch |
| Extrem ressourcenarm | <100K Paare | Plains Cree, Quechua, die meisten indigenen Sprachen |
| Im Wesentlichen null | <10K Paare | Tausende von Sprachen weltweit |

### Das Tokenizer-Problem

Bevor ein neuronales Modell Text verarbeiten kann, muss es Zeichen in numerische Token umwandeln — ein Prozess, der **Tokenisierung** genannt wird. Der vorherrschende Tokenisierungsalgorithmus ist die **Byte Pair Encoding (BPE)**, popularisiert von Sennrich et al. (2016) und implementiert in Werkzeugen wie **SentencePiece** (Kudo & Richardson, 2018). BPE funktioniert, indem es die häufigsten Zeichensequenzen in einem Trainingskorpus erlernt und ein Vokabular von Teilworteinheiten aufbaut. Im Englischen werden häufige Wörter wie „the" zu einzelnen Token; seltene Wörter werden in Teilwortstücke zerlegt („unforgivable" → „un" + „forgiv" + „able").

Das Problem ist, dass BPE-Vokabulare vorwiegend auf ressourcenstarken Sprachen trainiert werden, wobei das Englische typischerweise dominiert. Für ressourcenarme Sprachen, insbesondere solche mit komplexer Morphologie oder nicht-lateinischen Schriften, sind die Folgen gravierend:

- **Übersegmentierung**: Ein einzelnes Wort in einer polysynthetischen Sprache wie Plains Cree kann einen ganzen Teilsatz kodieren. Das Wort *nikî-nipâw* („Ich schlief") würde in zahlreiche Fragmente zerlegt — möglicherweise einzelne Bytes — weil der BPE-Algorithmus diese Zeichensequenzen nie zuvor gesehen hat. Was für eine Sprecherin eine bedeutungstragende Einheit ist, wird für das Modell zu einem Dutzend bedeutungsloser Fragmente.

- **Das Fertilitätsproblem**: Ein einzelnes Wort in einer morphologisch komplexen Sprache kann 5–15 Token erfordern, während seine englische Übersetzung 1–3 verwendet. Dies erzeugt eine massive Asymmetrie in der Sequenzlänge, die die Attention-Ausrichtung und Übersetzungsqualität verschlechtert.

- **Schriftpenalisierung**: Sprachen, die nicht-lateinische Schriften verwenden (Cree-Silbenschrift, Äthiopisch, Devanagari), werden noch ineffizienter tokenisiert und fallen manchmal auf einzelne Bytes zurück. Dies bedeutet, dass das effektive Kontextfenster des Modells für diese Sprachen dramatisch kleiner ist.

Dies ist nicht bloß eine technische Unannehmlichkeit. Das Vokabular des Tokenizers kodiert auf der grundlegendsten Ebene des Systems faktisch eine Verzerrung zugunsten gut ausgestatteter Sprachen. Ein Modell, das 15 Token für die Kodierung eines einzelnen Cree-Worts aufwendet, hat weitaus weniger Kapazität für das Verständnis des restlichen Satzes übrig als ein Modell, das Englisch verarbeitet, wo dieselbe Information vielleicht 3 Token belegt.

### Das Datenqualitätsproblem

Die begrenzten Paralleldaten, die für ressourcenarme Sprachen existieren, stammen oft aus **engen Domänen**. Die beiden größten Quellen für multilingualen Paralleltext für unterausgestattete Sprachen sind:

1. **Bibelübersetzungen**: Die Bibel wurde in über 700 Sprachen übersetzt und in Teilen in über 3.000. Dies macht religiöse Texte zur am häufigsten verfügbaren parallelen Ressource für viele Sprachen — aber ein Modell, das vorwiegend auf biblischem Text trainiert wurde, lernt ein spezifisches Register, Vokabular und eine spezifische Domäne. Es kann „du sollst nicht" erzeugen, aber nicht „bitte buchen Sie einen Flug" übersetzen.

2. **JW300**: Ein Datensatz, der aus Veröffentlichungen der Zeugen Jehovas extrahiert wurde und etwa 300 Sprachen abdeckt. Obwohl groß und multilingual, wirft JW300 sowohl Probleme der Domänenverzerrung (religiöse Inhalte) als auch ethische Bedenken hinsichtlich der Herkunft und Einwilligung zu den zugrunde liegenden Übersetzungen auf.

**Benchmark-Kontamination** ist ein weiteres ernstes Anliegen. Wenn Paralleldaten knapp sind, kann derselbe Text sowohl in Trainings- als auch in Evaluationsdatensätzen landen — ein Datenleck, das die Qualitätsmetriken aufbläht. Je kleiner der Datenpool, desto schwieriger ist dies zu verhindern und zu erkennen.

### Datenanreicherung: Aus weniger mehr machen

Forscher haben Techniken entwickelt, um begrenzte Daten zu strecken:

- **Backtranslation** (Sennrich et al., 2016): Trainieren eines anfänglichen Modells auf verfügbaren Paralleldaten und anschließende Verwendung, um **einsprachigen** zielsprachlichen Text zurück in die Ausgangssprache zu übersetzen. Dies erzeugt synthetische Paralleldaten, die verrauscht sind, aber die Modellqualität erheblich verbessern können. Backtranslation ist zu einer Standardtechnik über das gesamte Ressourcenspektrum hinweg geworden.

- **LLM-generierte synthetische Daten**: Verwendung großer Sprachmodelle zur Generierung von Trainingsdaten für ressourcenarme Paare. Dies ist vielversprechend, birgt aber Risiken — der generierte Text kann „Übersetzerisch" (unnatürlich wörtliche oder quellbeeinflusste Muster) aufweisen und kann etwaige im LLM vorhandene Verzerrungen verstärken.

- **Sprachübergreifender Transfer**: Training auf Paralleldaten einer verwandten ressourcenstärkeren Sprache (z. B. Verwendung von Spanisch–Englisch-Daten zum Bootstrapping der Guaraní–Englisch-MT) in der Hoffnung, dass die gemeinsamen strukturellen Merkmale übertragen werden. Dies funktioniert für eng verwandte Sprachen besser als für typologisch entfernte.

- **Morphologische Segmentierung**: Vorverarbeitung von Text, um Wörter in Morpheme (kleinste bedeutungstragende Einheiten) zu zerlegen, bevor sie dem Modell zugeführt werden. Für agglutinierende und polysynthetische Sprachen kann dies die Tokenisierungseffizienz und Übersetzungsqualität dramatisch verbessern. Dieser Ansatz steht in direktem Zusammenhang mit den im nächsten Abschnitt erörterten regelbasierten Werkzeugen.

---

## Teil 5: Finite-State-Transduktoren und regelbasierte Systeme

### Warum Regeln immer noch wichtig sind

Die bisherige Erzählung war eine der neuronalen Dominanz: statistische Systeme, ersetzt durch neuronale Netze, neuronale Netze, ersetzt durch Transformer, Transformer, hochskaliert zu LLMs. Doch es gibt eine parallele Tradition in der Computerlinguistik, die nie verschwand — und für bestimmte Sprachen bleibt sie unverzichtbar.

**Regelbasierte Systeme** kodieren explizites linguistisches Wissen: morphologische Regeln, Lexika, syntaktische Transfermuster. Sie lernen nicht aus Daten; sie werden von Linguisten gebaut, die die beteiligten Sprachen verstehen. Für gut ausgestattete Sprachen wurde dieser Ansatz längst von datengetriebenen Methoden übertroffen. Doch für Sprachen mit komplexer Morphologie und minimalen Daten liefern regelbasierte Systeme oft die einzige verlässliche verfügbare Analyse.

### Finite-State-Transduktoren: Eine Einführung

Ein **Finite-State-Transduktor (FST)** ist eine Recheneinrichtung, die zwischen zwei Repräsentationsebenen abbildet — typischerweise zwischen einer Oberflächenform (was Sie im Text sehen) und einer zugrunde liegenden Analyse (was es linguistisch bedeutet). Stellen Sie sich ihn als eine Maschine mit Zuständen und Übergängen vor: Sie liest Eingabesymbole, bewegt sich zwischen Zuständen und erzeugt Ausgabesymbole.

Als konkretes Beispiel betrachten Sie das Plains-Cree-Wort *nikî-nipâw*. Ein FST-basierter morphologischer Analysator kann diese Oberflächenform nehmen und erzeugen:

> nipâw + Verb + AI + Independent + Past + 1st Person Singular

Dies sagt Ihnen, dass das Wort das Verb *nipâw* („schlafen") in der unabhängigen Ordnung, Vergangenheitsform, erste Person Singular ist — „Ich schlief". Der Transduktor kodiert die Regeln der Cree-Morphologie: welche Präfixe Person anzeigen, welche Zeit markieren, welche Verbformen welche Flexionsmuster annehmen. Entscheidend ist, dass dies **bidirektional** funktioniert: Bei gegebener Analyse kann der FST die korrekte Oberflächenform erzeugen.

Die technische Infrastruktur zum Bau von FSTs umfasst:

- **HFST** (Helsinki Finite-State Transducer Technology): Ein Open-Source-Toolkit, das an der University of Helsinki gepflegt wird und das Rechenframework für den Bau und Betrieb von Transduktoren bereitstellt. HFST implementiert die ursprünglich von Xerox entwickelten Formalismen (lexc, twolc, xfst) und ist kompatibel mit **foma**, einem weiteren Open-Source-FST-Toolkit.

- **lexc**: Ein Formalismus zur Spezifikation des **Lexikons** — des Inventars von Morphemen (Wurzeln, Präfixe, Suffixe) und der Wortbildungsmuster, die sie kombinieren.

- **twolc**: Ein Formalismus zur Spezifikation **morphophonologischer Regeln** — der Lautveränderungen, die auftreten, wenn Morpheme kombiniert werden (z. B. Vokalharmonie, Konsonantenmutation).

### GiellaLT: Arktische Infrastruktur

**GiellaLT** (vom nordsamischen Wort *giella*, „Sprache") ist eine Sprachtechnologie-Infrastruktur mit Sitz an der **UiT — The Arctic University of Norway** in Tromsø. Es stellt die weltweit umfangreichste Bemühung dar, FST-basierte Werkzeuge für indigene und Minderheitensprachen zu bauen.

Ursprünglich bekannt als **Giellatekno** (Forschung) und **Divvun** (Sprachwerkzeuge), hat das Projekt — geleitet von den Linguisten **Trond Trosterud** und **Sjur Nygaard Moshagen** — morphologische Analysatoren, Rechtschreibprüfer und andere Sprachwerkzeuge für über **100 Sprachen** entwickelt, mit einem Fokus auf samische Sprachen (Nordsamisch, Lulesamisch, Südsamisch und andere), uralische Sprachen sowie andere arktische und indigene Sprachen.

GiellaLT verwendet HFST als sein Rechen-Backend und hat eine ausgefeilte gemeinsame Infrastruktur entwickelt: ein gemeinsames Build-System, gemeinsame Test-Frameworks und wiederverwendbare linguistische Komponenten. Der gesamte Code ist Open Source, gehostet auf [GitHub](https://github.com/giellalt), mit Hunderten von Repositorys, einschließlich Kerninfrastruktur und sprachspezifischer Repos (z. B. `lang-sme` für Nordsamisch, `lang-crk` für Plains Cree). Die Dokumentation des Projekts liegt unter [giellalt.github.io](https://giellalt.github.io/). Das öffentlich zugängliche Portal, **[Borealium.org](https://borealium.org)** — finanziert vom Nordischen Ministerrat — bietet freien Zugang zu Korrekturwerkzeugen, Tastaturen, Wörterbüchern, Sprachlernwerkzeugen (Oahpa) und Sprachsynthese für samische Sprachen, Kvenisch, Färöisch, Grönländisch und andere.

Die Beziehung zwischen GiellaLT und nationaler Sprachpolitik ist bemerkenswert. Ein Großteil der Finanzierung des Projekts kommt vom **Norwegischen Sámi-Parlament** und nordischen Regierungssprachprogrammen, was ein politisches Engagement für indigene Sprachtechnologie widerspiegelt, das in Umfang und Dauer ungewöhnlich ist.

### Apertium: Open-Source-regelbasierte MT

**[Apertium](https://www.apertium.org/)** ist eine Open-Source-regelbasierte Plattform für maschinelle Übersetzung, ursprünglich an der Universitat d'Alacant (Spanien) mit Finanzierung der spanischen und katalanischen Regierungen entwickelt. Sie begann 2004 mit einem Fokus auf verwandte Sprachpaare (Spanisch–Katalanisch, Spanisch–Portugiesisch), bei denen flache Transferregeln — Wort-für-Wort-Übersetzung mit morphologischen Anpassungen — überraschend gute Ergebnisse erzeugen. Zu den wichtigsten Mitwirkenden gehört **Francis M. Tyers**, der sowohl für Apertiums Entwicklung als auch für seine Übernahme für unterausgestattete Sprachen zentral war.

Apertiums Architektur ist eine klassische **Pipeline**:

1. **Morphologische Analyse** (FST-basiert): Identifikation des Lemmas und der morphologischen Merkmale jedes Worts
2. **Wortarten-Disambiguierung**: Auswahl der korrekten Analyse, wenn Wörter mehrdeutig sind
3. **Lexikalischer Transfer**: Abbildung der Lemmata der Ausgangssprache auf die Lemmata der Zielsprache
4. **Struktureller Transfer**: Anwendung von Regeln zur Behandlung von Wortstellungsänderungen, Kongruenz und anderen syntaktischen Unterschieden
5. **Morphologische Generierung** (FST-basiert): Erzeugung der korrekt flektierten Oberflächenform der Zielsprache

Stand 2025 unterstützt Apertium Hunderte von Sprachpaaren mit unterschiedlichen Qualitätsstufen, alle gehostet auf [GitHub](https://github.com/apertium). Es wird weiterhin aktiv von einer internationalen Community entwickelt und ist besonders nützlich für eng verwandte Sprachpaare, bei denen sein regelbasierter Ansatz ohne Trainingsdaten eine angemessene Qualität erreichen kann.

### Hybride Ansätze: FST + neuronal

Die vielversprechendste Front für ressourcenarme MT könnten **hybride Architekturen** sein, die regelbasierte morphologische Analyse mit neuronaler Übersetzung kombinieren. Die Idee ist unkompliziert: Verwenden Sie einen FST, um Wörter in Morpheme zu segmentieren (was das in Teil 4 beschriebene Tokenisierungsproblem löst), und führen Sie dann den segmentierten Text einem neuronalen MT-System zu.

Für eine polysynthetische Sprache wie Plains Cree bedeutet dies, dass das neuronale Modell eine Sequenz bedeutungstragender Einheiten statt willkürlicher Byte-Fragmente erhält. Das **Alberta Language Technology Lab (ALT Lab)** an der University of Alberta, geleitet von **Antti Arppe**, hat umfassende FST-basierte morphologische Analysatoren und communityorientierte Wörterbuchwerkzeuge für Plains Cree unter Verwendung der GiellaLT-Infrastruktur gebaut. Ihre jüngste veröffentlichte Arbeit (Arppe 2025, AmericasNLP) demonstriert FST-basierte Abbildung zwischen flektierten Cree-Wortformen und englischen Phrasen — im Wesentlichen „eingeschränkte Übersetzung" über Finite-State-Methoden, die auf der Wort-/Phrasenebene statt auf vollständigen Sätzen operiert. Bemerkenswerterweise hat das ALT Lab **kein** hybrides FST+neuronales MT-System veröffentlicht; ihre Arbeit ist linguistisch fundiert, regelbasiert und priorisiert Zuverlässigkeit und Community-Nutzen vor experimentellen neuronalen Ansätzen. Unterdessen demonstrierten Nguyen, Hammerly und Silfverberg (2025, AmericasNLP) eine hybride LLM+FST-Pipeline für Ojibwe-Verben an der UBC und erzielten starke Ergebnisse (chrF 0,82) — das nächste veröffentlichte Analogon zu einem hybriden Ansatz für eine algonkische Sprache.

Diese hybride Strategie stellt eine Konvergenz der beiden Traditionen dar, die sich durch die Geschichte der MT gezogen haben: das explizite Wissen des Linguisten und das statistische Lernen des Ingenieurs. Für die Sprachen, die MT am meisten benötigen, ist keine der beiden Traditionen allein ausreichend.

---

## Teil 6: Qualität messen — Das Evaluationsproblem

### Woher wissen Sie, ob eine Übersetzung gut ist?

Diese Frage klingt einfach. Sie ist tatsächlich eines der schwierigsten ungelösten Probleme im Feld, und wie Sie sie beantworten, bestimmt, welche Systeme zu „funktionieren" scheinen und welche nicht.

### BLEU: Der unvollkommene Standard

Über zwei Jahrzehnte lang war die vorherrschende automatische Metrik in der MT **BLEU** (Bilingual Evaluation Understudy), eingeführt von Papineni et al. bei IBM im Jahr 2002. BLEU misst, wie stark die Wortsequenzen (n-Gramme) der maschinellen Übersetzung mit einer oder mehreren menschlichen Referenzübersetzungen überlappen. Es enthält eine Kürzepenalisierung, um zu verhindern, dass Systeme den Score mit kurzen Ausgaben manipulieren.

BLEU wurde zur Währung des Feldes, weil es schnell, kostengünstig, sprachunabhängig und reproduzierbar ist. Nahezu jede zwischen 2002 und 2020 veröffentlichte MT-Arbeit berichtete BLEU-Scores. WMT-Shared-Tasks verwendeten es jahrelang als primäre Metrik.

Doch BLEU hat tiefgreifende Mängel, die zunehmend offensichtlich geworden sind:

- **Kein semantisches Verständnis**: BLEU ist reiner Oberflächenabgleich. Wenn eine Übersetzung ein perfektes Synonym verwendet, das zufällig nicht in der Referenz vorkommt, bestraft BLEU dies. Der Satz „die Katze saß auf der Matte" erzielt null Punkte gegenüber einer Referenz von „die Katze ruhte auf dem Teppich".
- **Schlechte Diskriminierung auf Satzebene**: BLEU wurde als Metrik auf Korpusebene entworfen. Auf Satzebene ist es unzuverlässig und verrauscht.
- **Morphologische Blindheit**: Für agglutinierende Sprachen (Türkisch, Finnisch, Suaheli), bei denen ein einzelnes Lemma Dutzende flektierter Formen haben kann, scheitert strikter Abgleich auf Wortebene katastrophal. Ein korrekt flektiertes Verb, das sich um ein Suffix von der Referenz unterscheidet, erzielt null Punkte.
- **Schwache Korrelation mit menschlichem Urteil**: Metaanalysen, insbesondere Reiter (2018), haben gezeigt, dass BLEUs Korrelation mit menschlichen Qualitätsbewertungen oft schwach ist, insbesondere bei hochwertigen Systemen und bei Sprachen, die weit vom Englischen entfernt sind.

### chrF und chrF++

**chrF** (Character F-Score), eingeführt von Maja Popović im Jahr 2015, adressiert BLEUs morphologische Blindheit, indem es die Überlappung auf **Zeichenebene** statt auf Wortebene misst. Dies gewährt Teilpunkte für gemeinsame Stämme und Wurzeln, selbst wenn sich die Flexionen unterscheiden — entscheidend für morphologisch reiche Sprachen. **chrF++** (Popović, 2017) fügt n-Gramme auf Wortebene wieder hinzu und erreicht eine bessere Korrelation mit menschlichem Urteil als rein zeichen- oder rein wortbasierte Metriken. Beide sind in **sacreBLEU**, dem Standard-Evaluations-Toolkit, implementiert und sind zu Standard-Sekundärmetriken in WMT-Shared-Tasks geworden.

### COMET und xCOMET: Neuronale Evaluation

Der bedeutendste Fortschritt in der MT-Evaluation war der Übergang zu **neuronalen Metriken** — Evaluationsmodellen, die selbst Transformer sind und darauf trainiert wurden, menschliche Qualitätsurteile vorherzusagen.

**COMET** (Crosslingual Optimized Metric for Evaluation of Translation), entwickelt von Ricardo Rei und Kollegen bei **Unbabel** (2020), verwendet einen sprachübergreifenden Encoder (XLM-RoBERTa), um den Ausgangssatz, die Übersetzung und die Referenz einzubetten, und sagt dann einen Qualitäts-Score voraus. Anders als BLEU operiert COMET im semantischen Raum — es erkennt Paraphrasen, erfasst die Bedeutungserhaltung und hat durchweg eine deutlich höhere Korrelation mit menschlichem Urteil als Metriken auf Oberflächenebene gezeigt. COMET gewann oder belegte den ersten Platz in den WMT Metrics Shared Tasks ab 2020.

**xCOMET** (Guerreiro et al., 2024, veröffentlicht in TACL) geht weiter: Zusätzlich zu einem Qualitäts-Score erzeugt es eine **feingranulare Fehlerspannen-Erkennung** — die Identifikation spezifischer Fehler in der Übersetzung, ihre Klassifizierung nach Typ (Genauigkeit, Flüssigkeit, Terminologie) und Schweregrad (geringfügig, schwerwiegend, kritisch). Dies überbrückt die Lücke zwischen automatischer Bewertung und menschlicher linguistischer Analyse.

### AfriCOMET: Evaluation für die Unterversorgten

Standard-COMET, das vorwiegend auf menschlichen Urteilen europäischer Sprachen trainiert wurde, generalisiert möglicherweise nicht gut auf typologisch unterschiedliche Sprachen. **AfriCOMET** (Wang, Adelani et al., NAACL 2024) adressiert dies, indem es auf menschlichen Evaluationsdaten aus **13 afrikanischen Sprachen** feinjustiert und **AfroXLM-R** verwendet — einen multilingualen Encoder, der speziell darauf trainiert wurde, afrikanische Sprachen besser zu repräsentieren. Diese Arbeit, hervorgebracht von der Masakhane-Community (siehe Teil 7), zeigt, dass Evaluationsmetriken selbst für linguistische Vielfalt angepasst werden müssen.

### Menschliche Evaluation: MQM und Direct Assessment

Automatische Metriken sind Proxys. Die Grundwahrheit bleibt die **menschliche Evaluation**, die zwei Hauptformen annimmt:

**Direct Assessment (DA)** bittet menschliche Bewerter, Übersetzungen auf einer Skala von 0–100 zu bewerten. Es ist relativ schnell und kostengünstig (crowdgesourcte Bewerter können verwendet werden) und war von 2017 bis 2020 die primäre menschliche Evaluationsmethode bei WMT. Seine Schwäche: Als sich die MT-Qualität verbesserte, konnten Nicht-Experten-Bewerter nicht mehr zwischen Systemen unterscheiden, die nahezu professionelle Ausgaben erzeugten. DA wurde am oberen Ende des Qualitätsspektrums unzuverlässig.

**Multidimensional Quality Metrics (MQM)** ersetzte DA ab 2021 als primäre menschliche Evaluationsmethode von WMT. MQM verwendet **professionelle Übersetzer**, die spezifische Fehlerspannen in der Übersetzung markieren, Fehler nach Typ (Fehlübersetzung, Auslassung, Grammatik, Terminologie) und Schweregrad (geringfügig = 1 Punkt, schwerwiegend = 5 Punkte, kritisch = 25 Punkte) klassifizieren. Dies erzeugt sowohl einen Qualitäts-Score als auch umsetzbare diagnostische Informationen — Sie wissen nicht nur, *wie schlecht* eine Übersetzung ist, sondern *was genau* schiefgelaufen ist.

| Merkmal | DA | MQM |
|---|---|---|
| Bewerter | Crowd-Worker | Professionelle Übersetzer |
| Methode | Ganzheitlicher 0–100-Score | Fehlerspannen-Annotation |
| Diagnostik | Keine | Detaillierte Fehlerkategorisierung |
| Kosten | Niedriger | Höher |
| Zuverlässigkeit | Schwächer für hochwertige MT | Goldstandard |
| WMT-Hauptverwendung | 2017–2020 | 2021–heute |

### Die Evaluationskrise für ressourcenarme Sprachen

Für ressourcenarme Sprachen wird das Evaluationsproblem durch mehrere Faktoren verschärft:

- **Keine qualifizierten Bewerter**: MQM erfordert zweisprachige professionelle Übersetzer. Für viele LRLs ist es äußerst schwierig, solche Bewerter zu finden.
- **Keine Referenzübersetzungen**: COMET und BLEU erfordern beide Referenzübersetzungen zum Vergleich. Für viele Domänen und Sprachen existieren diese nicht.
- **Metrik-Verzerrung**: Sowohl Oberflächenmetriken als auch neuronale Metriken wurden auf Daten europäischer Sprachen entwickelt und validiert. Ihr Verhalten bei typologisch entfernten Sprachen ist ungewiss.
- **Halluzinationsrisiko**: In ressourcenarmen Umgebungen können MT-Modelle flüssige Ausgaben erzeugen, die völlig unabhängig von der Quelle sind — ein Phänomen, das als **Halluzination** bezeichnet wird. Oberflächenmetriken können halluzinierten Ausgaben Scores ungleich null zuweisen, wenn diese zufällig n-Gramme mit der Referenz teilen.

Der Aufbau **maßgeschneiderter Evaluationsdatensätze** — selbst kleiner von 200–500 sorgfältig kuratierten Satzpaaren in der Zieldomäne — ist für jede ernsthafte ressourcenarme MT-Bemühung wesentlich. Sich ausschließlich auf FLORES-200 oder BLEU-Scores ohne domänenspezifische Evaluation zu verlassen, ist ein Rezept für falsches Vertrauen.

---

## Teil 7: Die institutionelle Landschaft

### Unternehmensakteure

Das MT-Feld wird von einer Handvoll großer Unternehmensakteure geprägt, von denen jeder unterschiedliche Strategien verfolgt:

**Google Translate** bleibt das weltweit am häufigsten genutzte MT-System und deckt Stand 2025 **240+ Sprachen** ab. Googles **1000 Languages Initiative** (2022 angekündigt) zielt darauf ab, KI-Modelle zu bauen, die die 1.000 meistgesprochenen Sprachen der Welt abdecken. Die Cloud Translation API bietet zwei Stufen: Basic (Legacy-NMT) und Advanced (neueste Modelle). Google hat seine Gemini-LLM-Fähigkeiten zunehmend in Translate integriert, wobei 2025 kontextbewusste, idiomatische Übersetzungsfunktionen auftauchten.

**Meta** hat sich durch NLLB-200, M2M-100, FLORES-200 und die Seamless-Suite als primärer Treiber der Open-Source-multilingualen MT positioniert. Metas Philosophie der offenen Modellveröffentlichung war für die akademische Forschung transformativ und lieferte Baselines und Werkzeuge, die andernfalls prohibitive Rechenressourcen erfordern würden.

**DeepL** besetzt eine qualitätsorientierte Nische und unterstützt etwa **33 Sprachen** — allesamt relativ gut ausgestattet — mit einem Ruf für natürliche, idiomatische Ausgaben, die von professionellen Übersetzern bevorzugt werden. DeepLs Geschäftsmodell (Freemium-Verbraucher + kostenpflichtige API für Unternehmen) und sein Formalitätsparameter (Steuerung formaler vs. informeller Register) spiegeln einen Fokus auf professionelle Übersetzungsabläufe statt breiter Sprachabdeckung wider.

**Microsoft Translator** (Teil von Azure AI Services) bietet Übersetzung über **130+ Sprachen** mit Unternehmensintegration durch Microsoft 365 und Teams. Seine Custom-Translator-Funktion ermöglicht es Organisationen, Modelle auf domänenspezifischen Daten feinzujustieren.

**Unbabel** kombiniert MT mit menschlicher Nachbearbeitung in einem „Human-in-the-Loop"-Ablauf, neben seinen Forschungsbeiträgen (COMET, xCOMET, Tower). Es repräsentiert die kommerzielle Anwendung des „MT + menschliche Überprüfung"-Paradigmas.

**LibreTranslate**, aufgebaut auf der **Argos Translate**-Engine, bietet eine vollständig quelloffene, selbst hostbare MT-Alternative ohne Unternehmensabhängigkeit — wichtig für Organisationen mit Anforderungen an die Datensouveränität.

### Basisinitiativen

Einige der wichtigsten Arbeiten in der MT — insbesondere für unterversorgte Sprachen — finden in communitygetriebenen Forschungsorganisationen statt:

**[Masakhane](https://www.masakhane.io/)** (vom isiZulu für „wir bauen gemeinsam") ist eine Basis-Forschungsgemeinschaft mit Fokus auf NLP für afrikanische Sprachen, gegründet 2019. Mit Hunderten von Mitgliedern auf dem Kontinent und in der Diaspora hat Masakhane grundlegende Datensätze (MasakhaNER, MAFAND-MT, MENYO-20k, AfriQA), Evaluationsmetriken (AfriCOMET) und Forschung hervorgebracht, die das NLP afrikanischer Sprachen erheblich vorangebracht hat. Zu den Schlüsselfiguren gehört **David Ifeoluwa Adelani** (Mila / UCL). Code und Daten sind auf [GitHub](https://github.com/masakhane-io) gehostet; der primäre Kommunikationsknotenpunkt ist ihr Slack-Workspace (beitreten über masakhane.io), mit wöchentlichen Community-Treffen. Masakhane operiert nach Prinzipien afrikanischer Eigentümerschaft afrikanischer Sprachtechnologie — ein bewusster Gegenentwurf zu extraktiven Forschungsmustern, bei denen Außeneinrichtungen Daten aus Sprachgemeinschaften ohne sinnvolle Zusammenarbeit sammeln. Sie raten ausdrücklich von „Fallschirm-Forschung" ab, bei der Außenstehende linguistische Daten ohne sinnvolle Community-Partnerschaft extrahieren.

**AmericasNLP** ist eine Workshop-Reihe (in Verbindung mit NAACL) mit Fokus auf NLP für indigene Sprachen Amerikas. Organisiert von Forschern einschließlich **Manuel Mager**, **Arturo Oncevay** und **Luis Chiruzzo**, betreibt sie Shared Tasks zur MT für Sprachen wie Quechua, Guaraní, Aymara, Nahuatl, Rarámuri und andere. Der Workshop bringt Forschungsherausforderungen ans Licht, die für Amerika einzigartig sind — polysynthetische Morphologie, Tonsysteme, extreme Datenknappheit und die politischen Dimensionen der Sprachtechnologie für kolonisierte Völker.

**[ALT Lab](https://altlab.ualberta.ca)** (Alberta Language Technology Lab) an der University of Alberta, geleitet von **Antti Arppe**, konzentriert sich speziell auf Rechenwerkzeuge für Plains Cree und andere indigene Sprachen des westlichen Kanada. Das ALT Lab baut FST-basierte morphologische Analysatoren und communityorientierte Sprachwerkzeuge (unter Verwendung der GiellaLT-Infrastruktur) und arbeitet in enger Zusammenarbeit mit Cree-sprechenden Gemeinschaften — ein Modell für communityzentrierte Sprachtechnologieentwicklung. Ihr öffentlich zugängliches Projekt **[21st Century Tools for Indigenous Languages](https://21c.tools)** bietet Online-Wörterbücher und morphologische Werkzeuge, die auf dieser Infrastruktur aufbauen.

**[NRC Indigenous Languages Technology](https://nrc.canada.ca)** (National Research Council Canada), geleitet von **Patrick Littell**, unterhält ein aktives Programm zur Unterstützung von 25+ indigenen Sprachen in ganz Kanada, einschließlich mehrerer Cree-Dialekte, Algonquin, Innu und Michif. NRC ILT hat MT-Forschung für Englisch–Inuktitut (unter Verwendung des Nunavut-Hansard-Korpus) veröffentlicht und entwickelt Open-Source-Werkzeuge, darunter **kiyânaw Transcribe** (Cree- und Ojibwe-Transkription), morphologische Analysatoren und **ReadAlong Studio** (Audio-Text-Ausrichtung). Der gesamte Code ist Open Source, und NRC beansprucht ausdrücklich kein Urheberrecht über linguistische Daten der Gemeinschaften.

**[Aya](https://cohere.com/research/aya)** (Cohere For AI) ist eine Open-Science-multilinguale LLM-Initiative mit 3.000+ Mitwirkenden aus 119+ Ländern. Obwohl es kein dediziertes MT-System ist, sind Aya-Modelle (Aya-101 mit 101 Sprachen, Aya 23 mit 23 wirkungsstarken Sprachen, Tiny Aya mit 70 Sprachen bei 3,35B Parametern) für Übersetzungsaufgaben hochwirksam. Die **Aya Collection** — 513M instruktionsartige Trainingsinstanzen — ist der größte offene multilinguale Instruktionsdatensatz. Das Community-Governance-Modell ist studierenswert.

**[GhanaNLP / Khaya](https://ghananlp.org)** ist eine communitygetriebene NLP-Initiative, die die Übersetzungsplattform **Khaya** hervorbrachte — eines der wenigen communitygesteuerten MT-Systeme, das tatsächlich für den täglichen Gebrauch eingesetzt wird. Khaya bietet neuronale maschinelle Übersetzung, ASR und TTS für ~12 ghanaische Sprachen (Twi, Ewe, Ga, Fante, Kusaal und andere) über Web, mobile Apps und Entwickler-API. Ihr Ansatz — 40.000+ parallele Satzpaare, aufgebaut durch Zusammenarbeit mit Linguisten und Community-Feedback — zeigt, dass communitygesteuerte MT betriebsfähig sein kann, nicht nur ein Wunschtraum.

### Finanzierung und Politik

MT-Forschung für ressourcenarme Sprachen hängt von Finanzierungsströmen ab, die sich deutlich von dem Wagniskapital und den Werbeeinnahmen unterscheiden, die kommerzielle MT tragen:

- **Lacuna Fund**: Ein kollaborativer Datenfonds, unterstützt von der Rockefeller Foundation, Google.org, Kanadas IDRC und Deutschlands GIZ. Lacuna finanziert speziell die Erstellung **gelabelter Datensätze** für unterrepräsentierte Sprachen — und schließt damit die Datenlücke, die die Grundursache der MT-Qualitätslücken ist.

- **AI4D** (Artificial Intelligence for Development): Ein Programm zur Unterstützung von KI-Forschungsstipendien für afrikanische Sprachtechnologie, betrieben über IDRC und die Schwedische Internationale Entwicklungszusammenarbeitsagentur.

- **UNESCO International Decade of Indigenous Languages (2022–2032)**: Ein politischer Rahmen, der das Profil indigener Sprachtechnologie weltweit angehoben hat, obwohl die konkrete Forschungsfinanzierung bescheiden war.

- **Inter-American Development Bank**: Finanzierte das **GuaranIA**-Projekt für Guaraní–Spanisch-MT in Paraguay, ein Beispiel für Entwicklungsfinanzierung zur Unterstützung von Sprachtechnologie.

- **Nationale Forschungsräte**: Ein Großteil der ressourcenarmen MT-Arbeit wird über standardmäßige akademische Kanäle finanziert (NSF, NSERC, EU-Horizon-Programme), oft als Bestandteile breiterer KI- oder Linguistikförderungen.

---

## Teil 8: Offene Fronten

### Was ungelöst bleibt

Das MT-Feld im Jahr 2026 ist gleichzeitig leistungsfähiger und ehrlicher über seine Grenzen als zu jedem früheren Zeitpunkt. Mehrere Frontprobleme definieren die aktuelle Forschungslandschaft:

**Dokumentenweite Übersetzung** bleibt weitgehend ungelöst. Die meisten MT-Systeme — einschließlich vieler LLMs — übersetzen Satz für Satz und verlieren dabei diskursive Kohärenz, Pronomenauflösung über Satzgrenzen hinweg und stilistische Konsistenz. Eine menschliche Übersetzerin liest das gesamte Dokument, bevor sie übersetzt; die meisten MT-Systeme verarbeiten Sätze isoliert. Die Forschung zur dokumentenweiten MT ist aktiv, hat aber noch keine Systeme hervorgebracht, die zuverlässig Kohärenz über lange Texte hinweg aufrechterhalten.

**Diskurs und Pragmatik** — die Lücke zwischen wörtlicher Bedeutung und kommunikativer Absicht — fordern die MT weiterhin heraus. Ironie, Untertreibung, kulturelle Anspielungen und Registersensibilität (formal vs. informell, respektvoll vs. lässig) werden von den besten LLMs teilweise erfasst, aber inkonsistent. Eine Übersetzerin, die zwischen Japanisch und Englisch arbeitet, muss durch ein ausgefeiltes Honorativsystem navigieren; aktuelle MT-Systeme bewältigen dies bestenfalls ungleichmäßig.

**Multimodale Übersetzung** — Übersetzung im Kontext mit Bildern, Video oder Audio — ist ein aufkommendes Forschungsgebiet. Ein als „fliegender Fischrogen" beschriebener Menüpunkt ergibt mit einem begleitenden Bild vollkommen Sinn; ohne es könnte MT etwas Seltsames erzeugen. Die Seamless-Suite und multimodale LLMs (Gemini, GPT-4o) haben begonnen, dies zu adressieren, aber robuste multimodale MT bleibt eine Front.

**Echtzeit-Sprache-zu-Sprache-Übersetzung** mit natürlicher Latenz (unter 3 Sekunden Verzögerung), Erhaltung der Sprecheridentität und Übertragung des emotionalen Tons nähert sich der Produktionsreife für ressourcenstarke Paare. Google, Meta und mehrere Start-ups demonstrierten 2025 Prototypsysteme. Für ressourcenarme Sprachen bleibt Echtzeit-Sprachübersetzung fern.

**Die „letzte Meile" für ressourcenarme Sprachen** ist vielleicht das wichtigste ungelöste Problem des Feldes. Die Lücke zwischen einem FLORES-200-Benchmark-Score und dem tatsächlichen Nutzen für eine Sprachgemeinschaft ist gewaltig. Ein Modell, das 15 BLEU bei der Plains-Cree–Englisch-Übersetzung erzielt, ist für keinen praktischen Zweck nützlich. Das Schließen dieser Lücke erfordert nicht nur bessere Modelle, sondern bessere Daten, bessere Evaluation, bessere Tokenisierung und — entscheidend — echte Zusammenarbeit mit Sprachgemeinschaften statt der Extraktion linguistischer Ressourcen für akademische Veröffentlichungen.

**Nachbearbeitung und Mensch-KI-Zusammenarbeit** wird zum vorherrschenden Paradigma für professionelle Übersetzung. Anstatt menschliche Übersetzer zu ersetzen, wird MT zunehmend als Erstentwurfsgenerator positioniert, den menschliche Übersetzer dann verfeinern. Das Verständnis der Kognitionswissenschaft der Nachbearbeitung, die Messung des Nachbearbeitungsaufwands und die Gestaltung von Schnittstellen, die Mensch-KI-Zusammenarbeit unterstützen, sind aktive Forschungsgebiete mit direkten kommerziellen Implikationen.

### Die politischen Dimensionen

MT ist nicht politisch neutral. Die Wahl, welche Sprachen unterstützt werden, welche Daten gesammelt werden, wer die Modelle kontrolliert und wessen Qualitätsstandards gelten, sind allesamt Entscheidungen mit erheblichen Konsequenzen für Sprachgemeinschaften.

Die Dominanz des Englischen als Pivot-Sprache kodiert eine bestimmte Sicht auf Übersetzung als etwas, das durch das Englische fließt. Die Verwendung von Bibel- und Missionarstexten als Trainingsdaten für indigene Sprachen wirft Fragen über Einwilligung und kulturelle Angemessenheit auf. Die Konzentration der MT-Fähigkeit auf eine Handvoll Silicon-Valley-Unternehmen schafft Abhängigkeitsbeziehungen, denen sich einige Sprachgemeinschaften ausdrücklich widersetzen.

**Datensouveränität** ist ein zentrales Anliegen. In Kanada behaupten die **OCAP-Prinzipien** (Ownership, Control, Access, Possession) — entwickelt vom First Nations Information Governance Centre —, dass indigene Gemeinschaften ihre Daten besitzen, kontrollieren, wie sie gesammelt und verwendet werden, Zugang dazu haben und sie physisch besitzen. Für die MT bedeutet dies, dass Trainingsdaten, die aus indigenen Sprachtexten abgeleitet werden, aus Gemeinschaftswissen aufgebaute Evaluationskorpora und auf gemeinschaftseigenen Ressourcen trainierte Übersetzungsmodelle allesamt unter die Governance der Gemeinschaft fallen — nicht unter die Governance der jeweiligen Forschungseinrichtung oder des Technologieunternehmens, das das Modell gebaut hat.

Dies hat direkte technische Implikationen. Ein mit Gemeinschaftsdaten gebautes MT-System kann nicht einfach im konventionellen Sinne quelloffen gemacht werden, wenn die Gemeinschaft dem nicht zugestimmt hat. Evaluations-Benchmarks können nicht veröffentlicht werden, wenn die Testdaten kulturell sensibles Material enthalten. Ein „gemeinschaftseigenes Modell" ist kein Widerspruch — es ist eine Designanforderung. Jede ernsthafte Bemühung in der ressourcenarmen MT für indigene Sprachen muss standardmäßig OCAP-vorausschauend sein, nicht als nachträglicher Gedanke.

Dies sind nicht bloß ethische Fußnoten — sie formen Forschungsprioritäten, Finanzierungsentscheidungen und technische Architekturen. „Bessere MT bauen" ist untrennbar mit Fragen darüber verbunden, wer profitiert, wer entscheidet und wessen linguistisches Wissen geschätzt wird.

---

## Anhang A: Wichtige Arbeiten

Eine chronologische Leseliste der Arbeiten, die die Entwicklung des Feldes definierten. Jeder Eintrag enthält eine kurze Anmerkung dazu, warum er von Bedeutung ist.

| Jahr | Arbeit | Autoren | Bedeutung |
|---|---|---|---|
| 2002 | [BLEU: a Method for Automatic Evaluation of MT](https://aclanthology.org/P02-1040/) | Papineni et al. (IBM) | Etablierte die zwei Jahrzehnte vorherrschende MT-Evaluationsmetrik |
| 2014 | [Sequence to Sequence Learning with Neural Networks](https://arxiv.org/abs/1409.3215) | Sutskever, Vinyals, Le (Google) | Demonstrierte neuronale Encoder-Decoder-Übersetzung |
| 2014 | [Neural MT by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) | Bahdanau, Cho, Bengio | Führte den Attention-Mechanismus ein |
| 2016 | [Google's Neural MT System](https://arxiv.org/abs/1609.08144) | Wu et al. (Google) | Brachte neuronale MT in den Produktionsmaßstab |
| 2016 | [Neural MT of Rare Words with Subword Units](https://aclanthology.org/P16-1162/) | Sennrich, Haddow, Birch | Führte die BPE-Tokenisierung für MT ein |
| 2016 | [Improving NMT Models with Monolingual Data](https://aclanthology.org/P16-1009/) | Sennrich, Haddow, Birch | Führte Backtranslation zur Datenanreicherung ein |
| 2017 | [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | Vaswani et al. (Google) | Führte die Transformer-Architektur ein |
| 2020 | [Unsupervised Cross-lingual Representation Learning at Scale](https://arxiv.org/abs/1911.02116) | Conneau et al. (Facebook) | XLM-R: sprachübergreifende Repräsentationen für 100 Sprachen |
| 2020 | [Beyond English-Centric Multilingual MT](https://arxiv.org/abs/2010.11125) | Fan et al. (Facebook) | M2M-100: Many-to-Many ohne englisches Pivoting |
| 2020 | [COMET: A Neural Framework for MT Evaluation](https://arxiv.org/abs/2009.09025) | Rei et al. (Unbabel) | Neuronale Evaluationsmetrik mit hoher menschlicher Korrelation |
| 2022 | [No Language Left Behind](https://arxiv.org/abs/2207.04672) | NLLB Team (Meta) | 200-Sprachen-MT-Modell + FLORES-200-Benchmark |
| 2023 | [ALMA: A Paradigm Shift in MT](https://arxiv.org/abs/2309.11674) | Xu et al. (JHU) | LLM-Feinjustierung für SOTA-Übersetzung mit wenig Daten |
| 2024 | [Tower: Open Multilingual LLM for Translation](https://arxiv.org/abs/2402.17733) | Alves et al. (Unbabel) | Vollständige Übersetzungspipeline in einem einzigen LLM |
| 2024 | [xCOMET: Transparent MT Evaluation](https://aclanthology.org/2024.tacl-1.54) | Guerreiro et al. | Feingranulare Fehlererkennung in der MT-Evaluation |
| 2024 | [AfriMTE and AfriCOMET](https://aclanthology.org/2024.naacl-long.334/) | Wang, Adelani et al. | MT-Evaluation, angepasst für afrikanische Sprachen |

---

## Anhang B: Konferenzen und Communities

### Wichtige Konferenzen

Das Ökosystem der NLP/MT-Konferenzen folgt einem jährlichen Rhythmus. Die folgende Tabelle listet die primären Veranstaltungsorte auf, gefolgt von bestätigten kommenden Terminen.

| Konferenz | Vollständiger Name | Häufigkeit | Anmerkungen |
|---|---|---|---|
| **[WMT](https://statmt.org/wmt25/)** | Conference on Machine Translation | Jährlich | Der primäre kompetitive Veranstaltungsort des Feldes; Shared Tasks definieren Benchmarks |
| **[ACL](https://www.aclweb.org/)** | Association for Computational Linguistics | Jährlich | Die Leitkonferenz der NLP |
| **EMNLP** | Empirical Methods in NLP | Jährlich | Zweitrangige Leitkonferenz; beherbergt typischerweise WMT |
| **NAACL** | North American Chapter of the ACL | Jährlich (rotiert mit ACL) | Wichtige regionale Konferenz |
| **EACL** | European Chapter of the ACL | Zweijährlich | Europäische regionale Konferenz |
| **COLING** | Intl. Conf. on Computational Linguistics | Zweijährlich | War 2024 mit LREC zusammengelegt; nun wieder getrennt |
| **LREC** | Language Resources & Evaluation Conference | Zweijährlich | Fokus auf Daten, Ressourcen und Evaluation |
| **[IWSLT](https://iwslt.org/)** | Intl. Workshop on Spoken Language Translation | Jährlich | Fokus auf Sprachübersetzung |

#### Aktuelle und kommende Termine

*Stand Mitte 2026. Vergangene Veranstaltungen sind als Referenz aufgeführt — ihre Proceedings sind auf der ACL Anthology verfügbar.*

| Veranstaltung | Termine | Ort | Status |
|---|---|---|---|
| **COLING 2025** | 19.–24. Jan. 2025 | Abu Dhabi, VAE | Vergangen — Proceedings verfügbar |
| **EACL 2026** | 24.–29. März 2026 | Rabat, Marokko | Vergangen — Proceedings verfügbar |
| **LREC 2026** | 11.–16. Mai 2026 | Palma de Mallorca, Spanien | Vergangen — Proceedings verfügbar |
| **ACL 2026** | 2.–7. Juli 2026 | San Diego, USA | **Kommend** |
| **AmericasNLP 2026** | 3.–4. Juli 2026 (in Verbindung mit ACL) | San Diego, USA | **Kommend** |

*ACL 2025 (Wien), EMNLP 2025 (Suzhou), WMT 2025 (Suzhou), IWSLT 2025 (Wien) und PACLIC 39 (Hanoi) fanden allesamt 2025 statt. Ihre Proceedings sind auf der [ACL Anthology](https://aclanthology.org) verfügbar.*

#### WMT-2025-Shared-Tasks

WMT-Shared-Tasks sind das, was einem öffentlichen Wettbewerb im MT-Feld am nächsten kommt. Die Ausgabe 2025 umfasst:

- **General Machine Translation** — die Leitaufgabe
- **Automated Translation Evaluation Systems** — einheitliche Metriken und Qualitätsschätzung
- **Low-Resource Indic Language Translation**
- **Creole Language Translation**
- **Terminology Shared Task**
- **Model Compression** — MT-Modelle kleiner und schneller machen
- **Open Language Data** — Verbesserung offener Trainingsdaten
- **Multilingual Instruction Shared Task (MIST)**
- **Limited Resources Slavic LLMs**

### Spezialisierte Workshops

| Workshop | Fokus | Nächster bekannter Termin | In Verbindung mit |
|---|---|---|---|
| **[AmericasNLP](https://americasnlp.org/)** | Indigene Sprachen Amerikas | 3.–4. Juli 2026 (ACL 2026, San Diego) | ACL |
| **AfricaNLP** | NLP afrikanischer Sprachen | 31. Juli 2025 (ACL 2025, Wien) | ACL / ICLR |
| **LoResMT** | Ressourcenarme MT | Typischerweise jährlich auf *ACL-Konferenzen | Verschiedene |
| **SIGTYP** | ACL SIG zu linguistischer Typologie | Jährlicher Workshop | ACL |

### Wichtige Community-Ressourcen

- **[machinetranslate.org](https://machinetranslate.org)** — Communitygetriebene, quelloffene Wissensbasis zur MT-Technologie. Betrieben von der Machine Translate Foundation (gemeinnützig, Zug, Schweiz, gegründet 2021). Deckt Ansätze, APIs, Modelle, Sprachunterstützung und Branchennachrichten ab. Lizenziert unter CC BY-SA 4.0. Ein ausgezeichneter Ausgangspunkt für jedes Thema in diesem Lagebericht.

- **[ACL Anthology](https://aclanthology.org)** — Das definitive frei zugängliche Archiv von NLP/CL-Forschungsarbeiten. Jede Arbeit bei ACL, EMNLP, NAACL, EACL, WMT und verwandten Veranstaltungsorten ist hier frei verfügbar.

---

## Anhang C: Werkzeuge, Datensätze und praktische Ressourcen

Dieser Anhang behandelt die konkreten Werkzeuge und Datenquellen, die in der MT-Arbeit heute von Bedeutung sind. Er ist für Personen geschrieben, die sich mit einem Terminal auskennen, aber das MT-Ökosystem möglicherweise nicht kennen.

### Trainings-Frameworks

Dies sind die Softwarepakete, die zum *Trainieren* neuronaler MT-Modelle von Grund auf (oder zum Feinjustieren bestehender) verwendet werden. Sie würden diese nutzen, wenn Sie Ihr eigenes Übersetzungsmodell bauen würden, anstatt ein bestehendes über eine API zu verwenden.

| Framework | Entwickler | Sprache | Anmerkungen |
|---|---|---|---|
| **[Marian NMT](https://marian-nmt.github.io/)** | Microsoft / U. Edinburgh | C++ | Der schnellste Open-Source-NMT-Trainer — kann ein Modell 3–5× schneller als PyTorch-basierte Alternativen trainieren. In reinem C++ mit minimalen Abhängigkeiten geschrieben. Treibt Microsoft Translator an. Jedes OpusMT-Modell (siehe unten) wurde damit trainiert. Benannt nach Marian Rejewski, dem polnischen Mathematiker, der half, Enigma zu knacken. |
| **[fairseq](https://github.com/facebookresearch/fairseq)** | Meta AI | Python (PyTorch) | Metas Arbeitspferd-Forschungstoolkit — verwendet zum Bau von M2M-100, NLLB-200 und den meisten von Metas veröffentlichten MT-Arbeiten. Hochmodular: Sie können Architekturen, Verlustfunktionen und Datenverarbeitung austauschen. Die Standardwahl für Forscher, die Metas Arbeiten reproduzieren oder erweitern. |
| **[OpenNMT](https://opennmt.net/)** | Harvard NLP / SYSTRAN | Python (PyTorch, TF) | Der zugänglichste Einstiegspunkt zum Trainieren benutzerdefinierter MT-Modelle. Entstand als Harvard-Forschungsprojekt, wird nun von SYSTRAN (einem kommerziellen MT-Unternehmen) gepflegt. Enthält CTranslate2 für den Einsatz (siehe unten). Gute Dokumentation für Anfänger. |

**Wann würden Sie diese verwenden?** Wenn Sie Paralleldaten haben (selbst nur wenige tausend Satzpaare) und ein dediziertes Übersetzungsmodell für ein bestimmtes Sprachpaar trainieren oder feinjustieren möchten. Sie würden diese NICHT für LLM-basierte Übersetzung verwenden (das Prompten von GPT/Claude/Gemini), die kein Training erfordert — nur API-Aufrufe.

### Inferenz und Einsatz

Diese Werkzeuge betreiben *bereits trainierte* Modelle, um Übersetzungen zu erzeugen. Stellen Sie sich die obigen Trainings-Frameworks als „die Werkstatt vor, in der das Auto gebaut wird", und diese als „den Zündschlüssel, der das Auto startet".

| Werkzeug | Was es tut | Wann verwenden |
|---|---|---|
| **[CTranslate2](https://github.com/OpenNMT/CTranslate2)** | Eine C++-Engine, die Transformer-Modelle mit hoher Geschwindigkeit und geringem Speicherverbrauch betreibt. Unterstützt INT8/INT4-Quantisierung (verkleinert Modelle auf 1/4 ihrer Größe bei minimalem Qualitätsverlust). Läuft auf CPU oder GPU, ohne dass PyTorch installiert sein muss. Unterstützt NLLB, M2M-100, OpusMT, LLaMA, Whisper. | Wenn Sie ein Übersetzungsmodell auf einem Server oder Laptop ohne GPU-Cluster selbst hosten möchten. Die Anlaufstelle für den Produktionseinsatz von Open-Source-MT-Modellen. |
| **[Hugging Face Transformers](https://huggingface.co/models?pipeline_tag=translation)** | Python-Bibliothek, die Modelle mit wenigen Codezeilen lädt und betreibt: `pipe = pipeline('translation', model='Helsinki-NLP/opus-mt-en-fr'); pipe('Hello world')`. Bietet ~1.500 vortrainierte OpusMT-bilinguale Modelle plus NLLB-200, mBART, mT5 und M2M-100. | Wenn Sie den schnellsten Weg von „Ich möchte etwas übersetzen" zu funktionierendem Code wünschen. Zwei Zeilen Python und Sie übersetzen. Geringerer Durchsatz als CTranslate2, aber weitaus einfacher einzurichten. |

### Vortrainierte Modellfamilien

Dies sind *bereits trainierte* Übersetzungsmodelle, die Sie herunterladen und sofort verwenden können. Kein Training erforderlich — einfach laden und übersetzen.

| Modellfamilie | Sprachen | Entwickler | Was es ist | Wo zu finden |
|---|---|---|---|---|
| **[OpusMT / Helsinki-NLP](https://huggingface.co/Helsinki-NLP)** | 1.000+ Paare | University of Helsinki (Jörg Tiedemann) | Die größte Sammlung von Open-Source-bilingualen Übersetzungsmodellen. Jedes Modell bewältigt ein Sprachpaar (z. B. `opus-mt-en-fr` für Englisch→Französisch). Trainiert auf OPUS-Daten mit Marian NMT, in das PyTorch-Format für Hugging Face konvertiert. Die Qualität variiert — exzellent für gut ausgestattete Paare, marginal für ressourcenarme. | Hugging Face (`Helsinki-NLP/opus-mt-*`) |
| **NLLB-200** | 200 Sprachen | Meta | Ein einzelnes multilinguales Modell, das zwischen beliebigen von 200 Sprachen übersetzt. Verfügbar in 600M-, 1,3B- und 3,3B-Parametervarianten. Die 600M-Version läuft auf einem Laptop; die 3,3B-Version benötigt eine anständige GPU. Die Qualität variiert enorm — stark für mittel ausgestattete, oft schlecht für wirklich ressourcenarme. | Hugging Face (`facebook/nllb-200-*`) |
| **M2M-100** | 100 Sprachen | Meta | Der Vorgänger von NLLB-200 — erstes Modell, das direkt zwischen nicht-englischen Paaren übersetzt (z. B. Bengali↔Suaheli), ohne über das Englische zu leiten. Historisch bedeutsam; weitgehend von NLLB-200 abgelöst. | Hugging Face (`facebook/m2m100_*`) |
| **Tower / Tower+** | 22–27 Sprachen | Unbabel | Nicht nur ein Übersetzer — bewältigt die vollständige Übersetzungspipeline (Korrektur, NER, Nachbearbeitung, Qualitätsschätzung) in einem einzigen LLM. Feinjustiert aus LLaMA. Stand 2025 übertrifft Tower v2 (70B) GPT-4o und DeepL bei mehreren Benchmarks. | Hugging Face |
| **ALMA / X-ALMA** | 50 Sprachen | Johns Hopkins University | LLaMA-basierte Modelle, die speziell für die Übersetzung mittels Präferenzoptimierung feinjustiert wurden (dem Modell wird beigebracht, welche Übersetzungen Menschen bevorzugen). Die 7B- und 13B-Versionen erreichen GPT-4-Qualität bei ressourcenstarken Paaren. X-ALMA erweitert sich auf 50 Sprachen mit sprachspezifischen Adapter-Modulen. | Hugging Face |

### Paralleldatenquellen

Paralleldaten sind der Treibstoff für das Training von MT-Modellen: Sammlungen von Sätzen in zwei Sprachen, die Übersetzungen voneinander sind, Zeile für Zeile ausgerichtet. Ohne Paralleldaten können Sie kein konventionelles MT-Modell trainieren. (LLM-basierte Übersetzung umgeht dies — Sie können GPT zum Übersetzen prompten, ohne Paralleldaten — aber dedizierte Modelle benötigen sie weiterhin.)

| Datensatz | Umfang | Was es ist | URL |
|---|---|---|---|
| **[OPUS](https://opus.nlpl.eu)** | 100B+ Satzpaare, 1.000+ Sprachen | Die mit Abstand wichtigste Ressource für MT-Daten. Eine Metasammlung, die Dutzende von Unterkorpora (siehe unten) in einem durchsuchbaren Portal aggregiert. Erstellt und gepflegt von Jörg Tiedemann an der University of Helsinki. Wenn Sie nach Paralleldaten in einer beliebigen Sprache suchen, ist OPUS der Ausgangspunkt. Zugänglich über Webportal, Python-`opustools`-Paket und Hugging Face. | [opus.nlpl.eu](https://opus.nlpl.eu) |
| **[Europarl](http://www.statmt.org/europarl/)** | ~60M Wörter/Sprache, 21 EU-Sprachen | Protokolle des Europäischen Parlaments — Reden von Politikern, übersetzt in alle offiziellen EU-Sprachen. Erstellt von Philipp Koehn. Historisch grundlegend (der Datensatz, der die SMT-Forschung ermöglichte), aber auf EU-Sprachen und Parlamentsregister beschränkt. | [statmt.org/europarl](http://www.statmt.org/europarl/) |
| **[ParaCrawl](https://paracrawl.eu)** | Milliarden von Paaren, 29+ Sprachpaare | EU-finanziertes Projekt, das das Web durchsucht, um natürlich vorkommenden Paralleltext zu finden (zweisprachige Websites, übersetzte Seiten). Weitaus verrauschter als kuratierte Korpora, aber erheblich größer. Veröffentlichte die Open-Source-Crawling-Pipeline **Bitextor**, die jeder verwenden kann, um eigene Paralleldaten aus dem Web zu schürfen. | [paracrawl.eu](https://paracrawl.eu) |
| **[CCAligned](http://www.statmt.org/cc-aligned/)** | 392M URL-Paare, 137 englisch-gepaarte Richtungen | Web-geschürfte parallele Dokumente aus Common Crawl (Meta/JHU). Besonders nützlich für niedrig bis mittel ausgestattete Sprachen, die nicht in kuratierten Korpora erscheinen. Die Qualität ist niedriger als bei Europarl, aber die Abdeckung ist weitaus breiter. | [statmt.org/cc-aligned](http://www.statmt.org/cc-aligned/) |
| **[WikiMatrix](https://github.com/facebookresearch/LASER)** | 135M parallele Sätze, 1.620 Paare | Parallele Sätze, die automatisch aus Wikipedia unter Verwendung von LASER-multilingualen Embeddings (Meta) geschürft wurden. Nützlich, weil Wikipedia in vielen Sprachen existiert — aber die Ausrichtung ist automatisch (nicht menschlich verifiziert), sodass einige Paare verrauscht oder falsch sind. | GitHub (LASER-Repo) |
| **[Tatoeba](https://tatoeba.org)** | 500+ Sprachen | Eine communitygepflegte Sammlung von Beispielsätzen und ihren Übersetzungen, beigetragen von Freiwilligen weltweit. Einzelne Sätze, keine Dokumente. Die zugehörige **[Tatoeba Translation Challenge](https://github.com/Helsinki-NLP/Tatoeba-Challenge)** (Helsinki-NLP) bietet saubere Trainings-/Test-Splits für Tausende von Sprachpaaren — verwendet zum Training der OpusMT-Modelle. | [tatoeba.org](https://tatoeba.org) |
| **FLORES-200** | 200 Sprachen | Ein standardisierter Evaluations-Benchmark (KEINE Trainingsdaten). Professionell übersetzte Sätze, die verwendet werden, um Systeme auf einem ebenen Spielfeld zu vergleichen. Erstellt von Meta zusammen mit NLLB-200. Wenn Sie Ihr System mit veröffentlichten Baselines vergleichen möchten, ist dies der zu verwendende Testdatensatz. | Hugging Face |

### Wichtige Unterkorpora innerhalb von OPUS

OPUS aggregiert viele unabhängige Parallelkorpora. Bei der Suche nach Daten in einer bestimmten Sprache sind diese Untersammlungen einen Blick wert:

- **OpenSubtitles** — Film- und Fernsehuntertitel. Riesiges Volumen, aber verrauscht — Untertitel sind oft vereinfacht, informell und können Transkriptionsfehler enthalten.
- **JW300** — Veröffentlichungen der Zeugen Jehovas, die ~300 Sprachen abdecken. Die breiteste Sprachabdeckung aller einzelnen Korpora, aber stark in Richtung religiöser Inhalte domänenverzerrt und ethisch umstritten (siehe Teil 4).
- **Bible** — Bibelübersetzungen in 700+ Sprachen. Engste Domäne von allen (alter religiöser Text), aber für viele Sprachen der einzige überhaupt existierende Paralleltext.
- **Tanzil** — Koranübersetzungen. Nützlich für arabisch-gepaarte Daten.
- **GNOME / KDE** — Software-Lokalisierungs-Strings („Datei → Speichern", „Sind Sie sicher, dass Sie löschen möchten?"). Nützlich für die technische/UI-Domäne, aber sehr formelhaft.
- **EMEA** — Dokumente der Europäischen Arzneimittel-Agentur. Nützlich für die Übersetzung in der biomedizinischen Domäne.

---

## Anhang D: Glossar

**Attention-Mechanismus**: Eine Komponente eines neuronalen Netzes, die es dem Modell ermöglicht, sich dynamisch auf verschiedene Teile der Eingabe zu konzentrieren, wenn jeder Teil der Ausgabe erzeugt wird. Eingeführt von Bahdanau et al. (2014) für die MT; verallgemeinert im Transformer (2017).

**Backtranslation**: Eine Datenanreicherungstechnik, bei der einsprachiger zielsprachlicher Text von einem vorläufigen MT-System zurück in die Ausgangssprache übersetzt wird, wodurch synthetische Paralleldaten für das Training erzeugt werden.

**BLEU**: Bilingual Evaluation Understudy. Eine automatische MT-Evaluationsmetrik, die auf der n-Gramm-Präzisionsüberlappung mit Referenzübersetzungen basiert.

**BPE (Byte Pair Encoding)**: Ein Teilwort-Tokenisierungsalgorithmus, der iterativ die häufigsten Zeichenpaare zusammenführt, um ein Vokabular aufzubauen. Verwendet in praktisch allen modernen NMT- und LLM-Systemen.

**COMET**: Eine neuronale MT-Evaluationsmetrik, die sprachübergreifende Embeddings verwendet, um menschliche Qualitätsurteile vorherzusagen, und auf Quelle + Hypothese + Referenz operiert.

**Fluch der Multilingualität**: Das Phänomen, bei dem das Hinzufügen weiterer Sprachen zu einem multilingualen Modell die Qualität pro Sprache aufgrund fester Modellkapazität verwässert.

**Encoder-Decoder**: Eine neuronale Architektur, bei der ein Encoder die Eingabesequenz zu Repräsentationen verarbeitet und ein Decoder die Ausgabesequenz aus diesen Repräsentationen erzeugt.

**FLORES-200**: Ein standardisierter MT-Evaluations-Benchmark, der 200 Sprachen abdeckt, erstellt von Meta zusammen mit NLLB-200.

**FST (Finite-State-Transduktor)**: Eine Recheneinrichtung, die mittels Zuständen und Übergängen zwischen Eingabe- und Ausgabesymbolsequenzen abbildet. Verwendet in der Computermorphologie zur Analyse und Erzeugung von Wortformen.

**Halluzination**: In der MT die Erzeugung flüssiger Ausgaben, die unabhängig von oder untreu zum Ausgangstext sind. Besonders häufig in ressourcenarmen Umgebungen.

**Ressourcenstarke Sprache**: Eine Sprache mit reichlich vorhandenem digitalem Text und parallelen Übersetzungsdaten (typischerweise >10M Satzpaare mit Englisch). Beispiele: Französisch, Deutsch, Chinesisch, Spanisch.

**LLM (Large Language Model)**: Ein neuronales Sprachmodell mit Milliarden von Parametern, trainiert auf riesigen Textkorpora, um das nächste Token vorherzusagen. Beispiele: GPT-4, Gemini, LLaMA, Claude.

**Ressourcenarme Sprache (LRL)**: Eine Sprache mit begrenztem digitalem Text und Paralleldaten (<1M Satzpaare). Die überwiegende Mehrheit der Sprachen der Welt fällt in diese Kategorie.

**MQM (Multidimensional Quality Metrics)**: Ein menschliches Evaluationsframework, bei dem professionelle Übersetzer spezifische Fehlerspannen in Übersetzungen annotieren, klassifiziert nach Typ und Schweregrad.

**NMT (Neural Machine Translation)**: MT unter Verwendung neuronaler Netze, im Gegensatz zu statistischen (SMT) oder regelbasierten (RBMT) Ansätzen.

**Paralleldaten / Parallelkorpus**: Eine Sammlung von Texten in zwei Sprachen, die Übersetzungen voneinander sind, auf Satzebene ausgerichtet. Die primäre Trainingsressource für die MT.

**Polysynthetische Sprache**: Eine Sprache, in der Wörter aus vielen Morphemen zusammengesetzt sind und oft Informationen kodieren, die in analytischen Sprachen wie dem Englischen einen vollständigen Teilsatz erfordern würden. Beispiele: Plains Cree, Mohawk, Inuktitut.

**SentencePiece**: Ein sprachunabhängiger Teilwort-Tokenizer und -Detokenizer, der BPE und Unigramm-Sprachmodellsegmentierung implementiert. Weit verbreitet in der multilingualen NLP.

**Transformer**: Die seit 2017 vorherrschende neuronale Architektur für die NLP, die vollständig auf Self-Attention-Mechanismen basiert. Eingeführt in „Attention Is All You Need" (Vaswani et al., 2017).

**Zero-Shot-Cross-Lingual-Transfer**: Die Anwendung eines auf einer Sprache (typischerweise Englisch) trainierten Modells auf eine andere Sprache ohne jegliche zielsprachliche Trainingsdaten, wobei auf gemeinsame multilinguale Repräsentationen zurückgegriffen wird.

---

*Dieser Lagebericht wurde im Juni 2026 zusammengestellt. Das MT-Feld bewegt sich rasch; spezifische Modellfähigkeiten und Benchmark-Ergebnisse sollten anhand aktueller Quellen verifiziert werden. Für die neuesten Entwicklungen konsultieren Sie [machinetranslate.org](https://machinetranslate.org), die [ACL Anthology](https://aclanthology.org) und die Proceedings des jüngsten WMT-Shared-Tasks.*