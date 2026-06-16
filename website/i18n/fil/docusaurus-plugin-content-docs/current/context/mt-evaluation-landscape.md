---
sidebar_position: 3
title: "Pagsukat sa Hindi Masusukat"
---
# Pagsukat sa Hindi Masusukat: Ang Suliranin ng Ebalwasyon sa Machine Translation

**Isang survey kung paano sinusukat ng larangan ang kalidad ng pagsasalin, kung saan ito nabibigo, at kung ano ang iniaalok ng LYSS (Linguistically-informed Yield & Structural Scoring) bilang alternatibo**

---

> *"Ang mga awtomatikong metric ay isang maginhawang kasinungalingan. Binibigyan nila tayo ng isang numero, at hinahayaan tayo ng numerong iyon na sumulat ng papel, at hinahayaan tayo ng papel na mag-angkin ng pag-unlad. Kung talagang nagkaroon ng pag-unlad ay ibang usapin."*
> — Inangkop mula sa paulit-ulit na damdamin sa WMT Metrics Shared Tasks

---

## Panimula

May problema sa pagsukat ang machine translation.

Dalawang dekada nang bumubuo ang larangan ng papasopistikadong mga sistema — mula sa phrase tables hanggang attention mechanisms at trillion-parameter language models — at sa buong panahong iyon, nahirapan ito sa isang mapanlinlang na simpleng tanong: *paano ninyo malalaman kung mahusay ang isang salin?*

Hindi akademiko lamang ang tanong na ito. Tinutukoy ng metric na pipiliin ninyo kung aling sistema ang "mananalo." Tinutukoy nito kung ano ang popondohan, ilalathala, ide-deploy, at — para sa mga wikang pinaka-nangangailangan ng MT — kung huhusgahan bilang mga kabiguan ang mga salin ng isang komunidad kahit na, sa katunayan, tama ang mga ito.

Ang kasaysayan ng MT evaluation ay, sa maliit na anyo, kasaysayan ng mga pagpapahalaga ng larangan. Ipinapakita ng dominasyon ng BLEU sa loob ng halos dalawang dekada ang kagustuhan para sa mura, mabilis, at language-agnostic na pagsukat kaysa linguistically informed na pagtatasa. Ipinapakita ng pag-usbong ng mga neural metric tulad ng COMET ang lumalaking pagiging sopistikado ng larangan — at ang patuloy nitong pag-asa sa English-centric na training data. Ipinapakita ng halos ganap na kawalan ng morphology-aware evaluation ang isang larangang, hanggang kamakailan, itinayo ng at para sa mga nagsasalita ng analytic European languages.

Sinusundan ng papel na ito ang ebolusyon ng MT evaluation mula BLEU hanggang sa kasalukuyan, tinutukoy kung saan sistematikong nabibigo ang mga umiiral na lapit para sa mga wikang morphologically complex at low-resource, at sinusuri kung ano ang maaaring itsura ng isang linguistically-grounded na alternatibo. Ito ay kasama ng iba pang mga dokumentong pangkonteksto ng proyekto — [*Mula Pāṇini hanggang Transformers*](./history-of-language-and-computation.md) (na sumusubaybay sa intelektuwal na kasaysayan ng wika at computation) at ang [*Field Briefing*](./mt-field-briefing.md) (na nagsu-survey sa kasalukuyang MT landscape). Kung ang mga dokumentong iyon ay nagtatanong ng "paano tayo nakarating dito?" at "ano ang umiiral?", ito naman ay nagtatanong: "paano natin malalaman kung gumagana ang alinman dito?"

---

## Bahagi 1: Ang Panahon ng String-Matching (2002–2015)

### BLEU at ang Kapanganakan ng Awtomatikong Ebalwasyon



Nagsisimula ang modernong panahon ng MT evaluation sa iisang papel: ang "BLEU: a Method for Automatic Evaluation of Machine Translation" nina Kishore Papineni, Salim Roukos, Todd Ward, at Wei-Jing Zhu, na inilathala sa ACL 2002. Sinusukat ng BLEU (Bilingual Evaluation Understudy) kung gaano kalaki ang overlap ng mga word sequence (n-grams) ng isang machine translation sa isa o higit pang human reference translations. May kasama itong brevity penalty upang pigilan ang mga sistema na manipulahin ang score gamit ang maiikling output, at kinakalkula nito ang geometric mean ng n-gram precisions sa orders 1 hanggang 4.

Naging pera ng larangan ang BLEU sa simpleng dahilan: mabilis ito, mura, reproducible, at language-independent. Bago ang BLEU, kailangan ng mahal at mabagal na human assessment upang suriin ang isang MT system. Nag-alok ang BLEU ng numerong maaaring kalkulahin sa milliseconds, ihambing sa mga papel, at gamitin upang iranggo ang mga sistema sa shared tasks. Sa loob ng ilang taon, halos mandatoryo na ito — hindi mailalathala ang isang papel na walang BLEU scores.

Ngunit may malalalim at mahusay na naidokumentong kahinaan ang BLEU na dalawang dekada nang sinusubukang lusutan ng larangan:

**Walang semantic understanding.** Purong surface matching ang BLEU. Ang "The cat sat on the mat" ay makakakuha ng zero laban sa reference na "the feline rested on the rug." Tama ang bawat salita bilang synonym; magkapareho ang kahulugan; zero ang score.

**Bulag sa morphology.** Para sa agglutinative at polysynthetic languages, katastrope ang pagkabigo ng mahigpit na word-level matching. Ang isang wastong naconjugate na Cree verb na naiiba ng isang morpheme mula sa reference ay makakakuha ng zero — kahit na ang pagkakaiba ay isang grammatically optional particle o parehong valid na word order.

**Mahinang sentence-level discrimination.** Idinisenyo ang BLEU bilang corpus-level metric. Sa sentence level, maingay ito at hindi maaasahan — ngunit rutinang inilalapat ito sa indibidwal na mga pangungusap.

**Single-reference bias.** Ipinagpapalagay ng BLEU na may *isang* tamang salin (o maliit na hanay ng references). Para sa mga wikang may free word order, mayayamang synonym na bokabularyo, o sistematikong ambiguities (tulad ng inclusive/exclusive "we" ng Cree), maaaring may dose-dosenang parehong tamang salin, at pinaparusahan ng BLEU ang lahat maliban sa isa na nagkataong tumugma sa reference.

**Mahinang korelasyon sa paghatol ng tao.** Ipinakita ng mga meta-analysis — kapansin-pansin ang Reiter (2018, *Computational Linguistics*) — na madalas mahina ang korelasyon ng BLEU sa human quality assessments, partikular para sa high-quality systems at para sa mga wikang malayo sa English.

Halos mula sa simula ay alam na ang mga kahinaang ito. Gayunman, nagpatuloy ang BLEU dahil mas masahol ang mga alternatibo — hindi sa accuracy, kundi sa convenience. Inoptimize ng larangan ang metric na kaya nitong kalkulahin, hindi ang metric na kailangan nito.

### NIST (Doddington, 2002)

Ang NIST metric, na inilathala sa parehong taon ng BLEU ni George Doddington sa HLT 2002, ay nagbago sa BLEU formula sa dalawang paraan. Una, tinitimbang nito ang n-grams ayon sa kanilang **information content** — mas mataas ang bigat ng rare n-grams kaysa common ones, batay sa intuysyong mas informative ang wastong pagsasalin ng hindi karaniwang phrase kaysa wastong pagsasalin ng "of the." Ikalawa, gumamit ito ng **arithmetic mean** sa halip na geometric mean ng BLEU, na nagbubunga ng mas stable na scores na hindi bumabagsak sa zero kapag walang matches ang alinmang isang n-gram order. Malawak na ginamit ang NIST sa DARPA TIDES at NIST OpenMT evaluation programmes ngunit hindi kailanman naabot ang dominasyon ng BLEU sa mas malawak na research community. Sa kabila ng mga pagpapahusay nito, ibinahagi nito ang pangunahing limitasyon ng BLEU: surface-level string matching na walang konsepto ng kahulugan.

### METEOR (Banerjee & Lavie, 2005)

Ang METEOR (Metric for Evaluation of Translation with Explicit ORdering) ay maagang pagtatangkang tugunan ang kahigpitan ng BLEU. Kung exact word matching ang ginagawa ng BLEU, nagpakilala ang METEOR ng tatlong inobasyon:

1. **Stemming**: Binabawasan ang mga salita sa kanilang stems bago ikumpara, na nagbibigay ng partial credit para sa morphological variants (hal., tumutugma ang "running" sa "ran" pagkatapos ng stemming).
2. **Synonym matching**: Gamit ang WordNet, kinikilala ng METEOR na ang "car" at "automobile" ay parehong konsepto.
3. **Word alignment**: Sa halip na bilangin ang n-gram overlaps, tahasang ini-align ng METEOR ang mga salita sa pagitan ng hypothesis at reference, pagkatapos ay kinakalkula ang precision at recall na may fragmentation penalty.

Palaging nagpakita ang METEOR ng mas mataas na korelasyon sa human judgments kaysa BLEU. Ngunit nangailangan ito ng language-specific resources (stemmers, synonym databases) na naglimita sa applicability nito, at mas mabagal itong kalkulahin. Para sa English, mas mahusay ito. Para sa low-resource languages, wala lang talagang stemmers at synonym databases.

### TER (Snover et al., 2006)

Sinusukat ng Translation Edit Rate ang minimum na bilang ng edits (insertions, deletions, substitutions, at *phrase shifts*) na kailangan upang baguhin ang hypothesis tungo sa reference, na normalized ayon sa haba ng reference. Ang phrase-shift operation — paglipat ng contiguous sequence ng mga salita sa ibang posisyon — ay direktang pagkilala na hindi fixed ang word order sa iba’t ibang wika. Intuitive ang edit-distance approach ng TER (sinusukat nito ang "gaano karaming trabaho ang kailangang gawin ng human post-editor?") ngunit minamana nito ang parehong pangunahing limitasyon: inihahambing ito laban sa iisang reference at walang konsepto ng kahulugan.

### chrF at chrF++ (Popović, 2015; 2017)

Ang pinakamahalagang metric innovation sa pagitan ng BLEU at ng neural era ay nagmula kay Maja Popović. Sinusukat ng **chrF** (character F-score) ang overlap sa *character* level sa halip na word level, na kinakalkula ang character n-gram precision at recall. Idinaragdag muli ng **chrF++** ang word-level unigrams at bigrams sa halo.

Bakit ito mahalaga para sa morphologically rich languages: nagbibigay ang character-level matching ng *partial credit* para sa shared morphemes. Ang mga Cree word na *nikî-nipâw* ("I slept") at *kikî-nipâw* ("you slept") ay nagbabahagi ng karamihan sa kanilang character n-grams kahit magkaibang salita ang mga ito. Magbibigay ang chrF ng malaking partial credit; zero ang ibibigay ng BLEU.

Naging standard secondary metric ang chrF++ sa WMT shared tasks, ipinatupad sa **sacreBLEU** (Post, 2018), at malawak na kinikilala bilang mas mahusay kaysa BLEU para sa morphologically rich languages. Ngunit nananatili itong string-matching metric — mas mahusay kaysa BLEU, ngunit pangunahing nalilimitahan ng parehong palagay na masusukat ang translation quality sa pamamagitan ng overlap ng surface-form.

---

## Bahagi 2: Ang Neural Metric Revolution (2018–Kasalukuyan)



### Ang Insight: Matutong Mag-score

May ibinabahaging pangunahing design choice ang string-matching metrics ng Bahagi 1: hand-crafted formulas ang mga ito. May nagpasya na ang n-gram precision, character overlap, o edit distance ay magandang proxy para sa translation quality, at pagkatapos ginamit ng lahat ang formula na iyon sa loob ng isang dekada.

Nagsimula ang neural metric revolution sa ibang tanong: *paano kung magsanay tayo ng model upang hulaan ang translation quality, sa parehong paraan ng pagsasanay natin sa models na magsalin?*

### BERTScore (Zhang et al., 2020)

Ang BERTScore, na inilathala sa ICLR 2020 ni Tianyi Zhang at mga kasamahan sa Cornell at MIT, ang unang malawakang pinagtibay na metric na naglipat ng evaluation mula exact string matching patungo sa semantic similarity. Elegant ang mekanismo: i-encode ang hypothesis at reference sa pamamagitan ng pre-trained Transformer model (BERT, RoBERTa, o DeBERTa), kalkulahin ang cosine similarity sa pagitan ng bawat pares ng token embeddings, at pagkatapos gamitin ang greedy matching upang kalkulahin ang precision (pinakamahusay na match ng bawat hypothesis token sa reference), recall (pinakamahusay na match ng bawat reference token sa hypothesis), at F1.

Natural na nahahawakan ng BERTScore ang synonyms, paraphrases, at word-order variations — mataas ang similarity ng "the feline rested on the rug" sa "the cat sat on the mat" dahil nahuhuli ng contextual embeddings ang semantic equivalence. Gamit ang multilingual BERT, umaabot ito sa anumang wikang sakop ng model.

Ngunit ang BERTScore ay hindi *sinanay* sa human quality judgments. Ginagamit nito ang pre-trained embeddings as-is, na nangangahulugang nahuhuli nito ang pangkalahatang semantic similarity sa halip na partikular na matutunan kung ano ang nagpapaganda sa isang *translation*. Mahalaga ang pagkakaibang ito: maaaring semantically similar ang isang pangungusap sa reference habang masamang salin pa rin (maling register, omitted negation, hallucinated qualifier). Minamana rin ng BERTScore ang anumang language biases na umiiral sa underlying model — para sa mga wikang underrepresented sa training data ng BERT, maaaring hindi mahuli ng embeddings ang makabuluhang distinctions.

### BLEURT (Sellam et al., 2020)

Ang BLEURT (Bilingual Evaluation Understudy with Representations from Transformers), na inilathala sa ACL 2020 nina Thibault Sellam, Dipanjan Das, at Ankur Parikh sa Google, ay nagpakilala ng mahalagang inobasyon: **pre-training on synthetic perturbations** bago ang fine-tuning sa human judgments. Ang insight ay ang fine-tuning ng language model nang direkta sa maliliit na WMT human judgment datasets ay nagbunga ng metric na brittle — nag-overfit ito sa specific patterns sa training data at nabigo sa out-of-distribution inputs.

Ang solusyon ng BLEURT ay two-phase training recipe. Sa phase one, milyun-milyong synthetic sentence pairs ang nabuo sa pamamagitan ng random word drops, insertions, substitutions, at backtranslation. Sinanay ang model upang hulaan ang umiiral na automatic metric scores (BLEU, ROUGE, BERTScore, entailment) para sa mga pares na ito — natututo ng pangkalahatang notions ng textual similarity. Sa phase two, fine-tuned ang pre-trained model sa WMT Direct Assessment ratings. Dramatikong pinahusay ng "warming up" na ito ang robustness.

Pinalawak ng BLEURT-20 ang lapit sa multilingual evaluation gamit ang RemBERT encoder ng Google. Ngunit nananatiling reference-only ang BLEURT — hindi nito ginagamit ang source text, na nangangahulugang hindi nito matutukoy ang hallucinations na nagkataong fluent, at lubos itong nakadepende sa kalidad ng reference.

### COMET (Rei et al., 2020)

Kinakatawan ng COMET (Crosslingual Optimized Metric for Evaluation of Translation) ang kasalukuyang state of the art sa automatic MT evaluation. Binuo ni Ricardo Rei at mga kasamahan sa **Unbabel**, gumagamit ang COMET ng cross-lingual encoder (XLM-RoBERTa) upang i-embed ang tatlong input — ang source sentence, ang MT hypothesis, at ang reference translation — at hinuhulaan ang quality score na sinanay sa human Direct Assessment judgments.

Nanalo o nanguna ang COMET sa WMT Metrics Shared Tasks mula 2020 pataas. Higit na mas mataas ang korelasyon nito sa human judgment kaysa anumang string-matching metric. Kinikilala nito ang paraphrases, nahuhuli ang meaning preservation, at nahahawakan ang synonym variation na lubusang nakakaligtaan ng BLEU.

Ngunit may kritikal na limitasyon ang COMET para sa ating layunin: sinanay ito sa human judgments mula sa WMT, na labis na nakatuon sa European languages. Ang cross-lingual encoder nito (XLM-R) ay sinanay sa CommonCrawl data kung saan halos wala ang Plains Cree, North Sámi, at karamihan ng indigenous languages. Para sa mga wikang ito, hindi maaasahan ang internal representations ng COMET — maaaring maglabas ito ng scores, ngunit ang mga score na iyon ay hindi nakaugat sa anumang tunay na pag-unawa sa estruktura ng wika.

### xCOMET (Guerreiro et al., 2024)

Ang xCOMET, na inilathala sa TACL 2024 nina Nuno Guerreiro, Ricardo Rei, at mga kasamahan sa Unbabel at Instituto Superior Técnico, ay nagpalawak sa COMET mula black-box scorer tungo sa **diagnostic tool**. Ang pangunahing inobasyon ay multi-task learning: kasabay ng sentence-level quality score, nagsasagawa ang xCOMET ng **subword-level sequence tagging** upang tukuyin ang partikular na error spans sa salin at uriin ang mga ito bilang minor, major, o critical.

Tinutulay nito ang agwat sa pagitan ng automatic scoring at MQM-style human error analysis. Sa halip na iulat lamang na "ang salin na ito ay may score na 0.73," maaaring ituro ng xCOMET ang partikular na mga salitang mali at ipahiwatig kung gaano kalala. Gumagamit ang training ng curriculum learning approach: unang magsanay sa Direct Assessment data para sa sentence-level regression, pagkatapos idagdag ang MQM-annotated data na may error span labels para sa joint training.

Nakamit ng xCOMET ang state-of-the-art performance sa sentence-level, system-level, at span-level evaluation nang sabay-sabay. Gumagana ito sa parehong reference-based at reference-free modes. Ngunit nangangailangan ito ng MQM-annotated training data — na mahal likhain at labis na umiiral para sa European language pairs.

### AfriCOMET (Wang & Adelani, NAACL 2024)

Ang AfriCOMET, na inilathala sa NAACL 2024 nina Jiayi Wang, David Ifeoluwa Adelani, at mga kasamahan sa Masakhane community, ang pinakamahalagang patunay na ang neural metrics ay *kailangang* iangkop para sa underserved languages — hindi sila nagge-generalize out of the box.

Una munang ipinakita ng papel ang problema: ang standard COMET, na sinanay sa WMT data mula sa European languages, ay nagpakita ng makabuluhang mas mahinang korelasyon sa human judgments nang inilapat sa 13 African languages (kabilang ang Amharic, Hausa, Igbo, Swahili, Yoruba, at Zulu). Nangailangan ang ayos ng dalawang pagbabago. Una, palitan ang XLM-R ng **AfroXLM-R**, isang cross-lingual encoder na partikular na sinanay upang mas mahusay na i-represent ang African languages. Ikalawa, lumikha ng **AfriMTE**, isang bagong human evaluation dataset na may pinasimpleng MQM guidelines na dinisenyo para sa non-expert annotators — dahil mahirap makahanap ng bilingual professional translators para sa mga wikang ito.

Pinatunayan ng AfriCOMET ang konsepto: maaaring lampasan nang malaki ng isang language-family-specific neural metric ang generic version. Ngunit pinatunayan din nito ang gastos: may kailangang bumuo ng AfroXLM-R, mangolekta ng human judgment data para sa 13 wika, at magsanay ng bagong model. Para sa Plains Cree, walang katumbas na encoder, human judgment dataset, o adapted metric. Mangangailangan ang landas ng AfriCOMET na likhain ang lahat ng ito mula sa simula — isang multi-year effort na kinasasangkutan ng community-based human evaluation at marahil isang nakalaang Algonquian-family encoder.

### GEMBA: LLM-as-Evaluator (Kocmi & Federmann, 2023)

Ang GEMBA (GPT Estimation Metric Based Assessment), na inilathala sa EAMT 2023 nina Tom Kocmi at Christian Federmann sa Microsoft, ay nagtanong ng radikal na tanong: paano kung *tanungin* lang ninyo ang GPT-4 kung maganda ang isang salin?

Nakakalinlang sa kasimplehan ang lapit. Pinoprompt ng **GEMBA-DA** ang LLM gamit ang source at hypothesis at humihingi ng quality rating sa 0–100 scale. Nagbibigay ang **GEMBA-MQM** ng tatlong annotated examples at humihiling sa LLM na tukuyin ang partikular na error spans, uriin ang mga ito ayon sa type at severity, at gumawa ng MQM-style score. Walang kinakailangang metric-specific training.

Kapansin-pansin ang mga resulta: sa system level, nakamit ng GEMBA ang competitive o state-of-the-art na korelasyon sa human judgments. Ang error annotations ng GEMBA-MQM, bagaman hindi kasing maaasahan ng human annotators, ay nagbigay ng interpretable diagnostic information nang walang anumang specialized training.

Ngunit nagbubukas ang GEMBA ng seryosong alalahanin. Nakadepende ito sa proprietary closed-source models na nagbabago ang behavior sa pagitan ng API versions. Hindi reproducible ang mga resulta sa mahigpit na kahulugan. Mahal ito sa scale (API costs para sa pagsusuri ng buong WMT test set). At — kritikal para sa ating layunin — hindi tiyak ang kaalaman ng LLM sa low-resource languages. Maaaring nauunawaan o maaaring hindi nauunawaan ng GPT-4 ang Plains Cree morphology nang sapat upang suriin ang mga salin; walang paraan upang malaman nang hindi sinusubok, at walang garantiya na magiging consistent ang behavior sa mga model update. Mismong sina Kocmi at Federmann ay nagpayo laban sa paggamit ng GEMBA upang mag-angkin ng improvements sa academic papers dahil sa black-box nature ng evaluation.

### MetricX at ang WMT 2024 Metrics Shared Task

Ang **MetricX-24**, na binuo nina Juraj Juraska, Daniel Deutsch, Mara Finkelstein, at Markus Freitag sa Google, ang nanalo sa WMT 2024 Metrics Shared Task. Itinayo sa **mT5** (Multilingual T5, isang encoder-decoder model sa halip na encoder-only XLM-R na ginagamit ng COMET), ibang architectural path ang tinatahak ng MetricX. Gumagamit ito ng two-stage fine-tuning — una sa Direct Assessment data, pagkatapos sa MQM scores — na may malawak na **synthetic data augmentation** na tumatarget sa kilalang metric failure modes (undertranslation, fluent-but-wrong translations, hallucinations).

Ang WMT 2024 findings paper, na pinamagatang **"Are LLMs Breaking MT Metrics?"**, ay nagtanong kung sinira ba ng LLM-generated translations ang metric ecosystem. Ang sagot ay qualified no: nanatiling epektibo ang fine-tuned neural metrics (MetricX-24, COMET variants), bagaman nagpakita ng nakakagulat na lakas ang LLM-based metrics (GEMBA variants) sa system level. Mahahalagang findings:

- Palaging nalampasan ng **source-aware metrics** (gamit ang source + reference + hypothesis) ang reference-only metrics
- Ang **hybrid models** na tumatakbo sa parehong reference-based at reference-free modes mula sa iisang architecture ang umuusbong na direksyon
- Nagpapatuloy ang **low-resource gap**: mas mahina ang performance ng lahat ng metrics sa underrepresented languages, at hindi lumiliit ang gap
- Palaging nalalampasan ng **MQM-trained metrics** (gamit ang fine-grained error annotations) ang DA-trained metrics (gamit ang scalar scores)

Malinaw ang implikasyon para sa low-resource evaluation: nagko-converge ang larangan sa malalaki, trained, source-aware neural metrics bilang gold standard. Nangangailangan ang mga metric na ito ng malaking training data, compute, at — kritikal — human evaluation data sa target language. Para sa mga wikang walang alinman sa mga resource na ito, hindi lang naaangkop ang state-of-the-art metric pipeline.

### Ang Problema ng Bias: Neural Metrics at Low-Resource Languages

Ang neural metric revolution ay, sa napakalaking bahagi, isang high-resource phenomenon. Bawat trained metric sa mga naunang seksyon ay sinanay sa WMT human judgment data, na sumasaklaw sa humigit-kumulang 20 language pairs — lahat ay kinasasangkutan ng European languages, Chinese, o Japanese. Ang underlying encoders (XLM-R, mT5, InfoXLM) ay sinanay sa CommonCrawl data kung saan proporsyonal sa web presence ang representasyon: nangingibabaw ang English, mahusay na sakop ang European languages, at epektibong wala ang napakalaking mayorya ng 7,000+ wika sa mundo.

Para sa wikang tulad ng Plains Cree, lumilikha ito ng cascading failure:

1. **Walang training data**: Walang WMT human judgments para sa Cree translations, kaya walang metric na sinanay upang suriin ang mga ito.
2. **Walang encoder coverage**: Itinayo ang vocabulary ng XLM-R sa CommonCrawl, kung saan napakabihira ng Cree text. Sobra ang pagse-segment ng tokeniser sa Cree words tungo sa arbitrary byte fragments, at mahina ang pagkakasany sa contextual embeddings para sa mga fragment na iyon.
3. **Walang validation**: Walang nakapagsukat kung ang COMET, BLEURT, o MetricX ay gumagawa ng meaningful scores para sa Cree. Maaaring gumawa sila ng *numbers*, ngunit walang ebidensiyang nagko-correlate ang mga numerong iyon sa aktwal na translation quality.
4. **Walang landas sa improvement**: Ang AfriCOMET approach — bumuo ng language-family-specific encoder, mangolekta ng human evaluation data, magsanay ng bagong metric — ay multi-year, multi-institution effort. Para sa isang language community na may 27,000 speakers, hindi kasalukuyang umiiral ang research infrastructure upang suportahan ito.

Ang resulta ay isang paradox: ang mga wikang pinaka-agarang nangangailangan ng MT evaluation (dahil pinakamahina ang kanilang MT systems at nangangailangan ng pinakamaingat na pagtatasa) ang mismong mga wikang pinakadi-maaasahan ang pinakamahusay na evaluation tools. Ang tugon ng larangan ay irekomenda ang chrF++ bilang "good enough" na alternatibo — at mas mahusay ito kaysa BLEU — ngunit string-matching metric pa rin ang chrF++ na hindi makakatukoy ng equivalence, hindi makahawak ng free word order, at walang konsepto ng morphological validity.

---

## Bahagi 3: Higit pa sa Scoring — Diagnostic at Linguistic Evaluation

### Ang Adequacy/Fluency Split

Bago umiral ang automatic metrics, gumamit ang human evaluation ng MT ng framework na may dalawang dimension: **adequacy** (naipapahayag ba ng salin ang kahulugan ng source?) at **fluency** (grammatical at natural ba ang salin sa target language?). Kinikilala ng pagkakaibang ito, na codified sa maagang DARPA MT evaluations at kalaunan sa NIST, ang isang bagay na gugugol ang automatic metrics ng dalawang dekada upang muling mahuli: hindi one-dimensional ang translation quality.

Nawala sa pabor ang adequacy/fluency framework nang palitan ito ng Direct Assessment (isang single scalar score) sa WMT. Ngunit nananatiling kritikal ang underlying insight: maaaring fluent ngunit mali ang isang salin (hallucination), o disfluent ngunit tama (morphological variant). Walang iisang score ang nakakahuli sa pareho.

### MQM: Ang Gold Standard (Lommel et al., 2014; Freitag et al., 2021)

Pinalitan ng **Multidimensional Quality Metrics (MQM)** ang Direct Assessment bilang pangunahing human evaluation ng WMT mula 2021 pataas. Gumagamit ang MQM ng professional translators na nagmamarka ng partikular na error spans, nag-uuri ng mga ito ayon sa type (mistranslation, omission, addition, grammar, terminology) at severity (minor = 1 point, major = 5 points, critical = 25 points). Nagbubunga ito ng parehong quality score at actionable diagnostic information.

Ang MQM ang pinakamalapit na bagay sa "tamang" evaluation methodology — sinasabi nito hindi lamang *gaano kasama* ang isang salin, kundi *ano mismo ang nagkamali*. Ngunit nangangailangan ito ng bilingual professional translators, na para sa karamihan ng low-resource languages ay hindi umiiral sa sapat na bilang para sa statistically reliable evaluation.

### MorphEval: Contrastive Morphological Evaluation (Burlot & Yvon, 2017)

Ang MorphEval ang pinakadirektang prior art para sa morphology-aware MT evaluation. Ipinakilala nina Franck Burlot at François Yvon sa WMT 2017 at pinalawak noong 2018, sinusuri ng MorphEval ang morphological *competence* gamit ang **contrastive test suites**.

**Paano ito gumagana:** Binubuo ang test suite ng sentence pairs sa source language na nagkakaiba sa eksaktong isang morphological contrast — halimbawa, singular vs. plural, present vs. past, masculine vs. feminine. Isinasalin ng MT system ang parehong pangungusap. Kung wastong naipapahayag ng sistema ang contrast sa mga salin nito (hal., gumagawa ng plural target kapag plural ang source at singular target kapag singular ang source), itinatala ang contrast bilang tama.

**Mga wikang sakop:** English→Czech, English→Latvian (v1, WMT 2017); pinalawak sa English→French, English→German, English→Finnish, Turkish→English (v2, WMT 2018).

**Mahahalagang findings:** Ipinakita ng MorphEval na kahit ang top-performing neural MT systems ay may sistematikong morphological failures — maaaring gumawa sila ng fluent output habang nagkakamali sa tense, number, o case. Hindi nakikita ng BLEU ang mga error na ito at kahit ang COMET ay bahagyang hindi rin nakikita ang mga ito.

**Availability:** Open source sa GitHub ([franckbrl/morpheval](https://github.com/franckbrl/morpheval), [franckbrl/morpheval_v2](https://github.com/franckbrl/morpheval_v2)).

**Limitations:** Nangangailangan ang MorphEval ng crafted contrastive test suites kada target language, na dinisenyo ng linguists na nakauunawa sa morphological contrasts ng wikang iyon. Walang test suites para sa anumang polysynthetic language. Sinusubok ng methodology ang *competence* (kaya ba ng sistema ang contrast na ito?) sa halip na *validity* (gumawa ba ang sistema ng totoong mga salita?) o *equivalence* (pareho bang tama ang dalawang magkaibang salin na ito?).

### CheckList: Behavioral Testing for NLP (Ribeiro et al., ACL 2020)

Ang **CheckList**, na inilathala sa ACL 2020 ni Marco Tulio Ribeiro at mga kasamahan (nanalo ng Best Paper), ay nagdala ng ideya mula software engineering tungo sa NLP evaluation: **unit testing**. Sa halip na suriin ang aggregate performance ng model sa benchmark, nagtatakda ang CheckList ng matrix ng **capabilities** (vocabulary, negation, named entities, temporal reasoning, coreference) na ikinukrus sa **test types**:

- **Minimum Functionality Tests (MFT)**: Simple, targeted test cases na dapat maipasa ng anumang competent model.
- **Invariance Tests (INV)**: Perturbations sa input na *hindi dapat* magbago ng output (hal., hindi dapat baguhin ng pagpapalit ng pangalan ang sentiment).
- **Directional Expectation Tests (DIR)**: Perturbations na *dapat* magbago ng output sa predictable na direksyon.

Orihinal na dinisenyo ang Checklist para sa sentiment analysis at NLI, ngunit direktang naaangkop ang paradigm sa MT. Maaaring lumikha ng MFTs para sa morphological phenomena ("gumagawa ba ang sistema ng tamang plural form?"), INV tests para sa free word order ("binabago ba ng reordering ng Cree words ang English translation?"), at DIR tests para sa morphological features ("binabago ba ng pagpapalit ng source mula past tungo present tense ang target tense?").

Partikular na relevant ang CheckList paradigm dahil pormalisado nito ang ginagawa ng MorphEval nang intuitively: subukin ang specific capabilities sa halip na sukatin ang aggregate scores. Ang variant classes ng aming linter (WORD_ORDER, ORTHOGRAPHIC, OPTIONAL_PARTICLE, etc.) ay, sa bisa, invariance rules — nagtatakda ang mga ito ng perturbations na hindi dapat magbago ng evaluation verdict.

### Challenge Sets at Targeted Evaluation

Ang mas malawak na paradigm ng **challenge sets** — crafted test suites na tumatarget sa specific linguistic phenomena — ay naging established complementary evaluation methodology sa WMT mula humigit-kumulang 2017.

Pinangunahan nina **Isabelle, Cherry & Foster (2017)**, sa NRC Canada, ang lapit para sa MT gamit ang hand-crafted test sets na naghihiwalay ng structural divergences sa pagitan ng mga wika — mga kaso kung saan malamang mali ang literal translation. Ang kanilang follow-up work (Isabelle & Kuhn, 2018) ay bumuo ng 506 French sentences na tumatarget sa specific translation challenges, nagbibigay ng fine-grained na larawan ng system capabilities.

Lumikha ang **LingEval97** (Sennrich, EACL 2017) ng 97,000 contrastive English→German translation pairs na sumusubok kung nag-aassign ang NMT models ng mas mataas na probability sa correct translations kumpara sa pairs na may ipinasok na morphosyntactic errors. Isang mahalagang finding: mahusay ang character-level models sa transliteration ngunit mas mahina sa long-distance morphosyntactic agreement.

Pinalaki ng **ACES** (Amrhein, Moghe & Guillou, 2022–2023) ang challenge set approach nang dramatiko: 36,476 examples na sumasaklaw sa 146 language pairs na sumusubok sa 68 distinct linguistic phenomena. Ginamit ang ACES upang meta-evaluate ang metrics na isinumite sa WMT metrics shared task — sinusubok kung kayang matukoy ng *metrics* ang contrasts, hindi lamang kung kayang gawin ng *systems* ang mga ito. Pinalawak sa **SPAN-ACES** na may error span annotations.

Tinatarget ng **MT-GenEval** (Currey et al., EMNLP 2022) at **WinoMT** (Stanovsky, Smith & Zettlemoyer, ACL 2019) ang gender accuracy partikular. Kapansin-pansin ang WinoMT dahil tahasan nitong ginagamit ang **morphological analysis** sa target language upang beripikahin ang gender ng translated occupations — isa sa iilang kaso kung saan ginagamit ang morphological analyser bilang bahagi ng MT evaluation tool.

Ang **Hjerson** (Popović & Ney, 2011) ay isang open-source tool para sa automatic MT error classification na gumagamit ng **lemmas and POS tags** upang ikategorya ang errors sa limang uri: morphological, reordering, missing words, extra words, at lexical errors. Marahil ito ang pinakamalapit na prior art sa aming linter sa diwa — gumagamit ito ng linguistic analysis upang magbigay ng diagnostic error categories sa halip na iisang score.

Ang karaniwang sinulid: paulit-ulit na kinilala ng larangan na hindi sapat ang aggregate scores. Nagbibigay ang diagnostic evaluation ng granularity na kailangan upang maunawaan *bakit* nabibigo ang isang sistema. Ngunit nangangailangan ang diagnostic approaches ng linguistic expertise kada wika, at nakasentro ang expertise na iyon sa European languages.

### AmericasNLP: Ebalwasyon sa Aktuwal na Larangan

Ang AmericasNLP workshop series (co-located with NAACL), na nakatuon sa NLP para sa Indigenous languages of the Americas, ay nagbibigay ng pinakadirektang comparison point para sa aming evaluation challenges.

Mula 2021 hanggang 2023, ginamit ng shared task ang **chrF** bilang pangunahing evaluation metric — pinili dahil sa robustness nito sa low-resource settings at character-level matching nito, na nagbibigay ng partial credit para sa morphological overlap. Kinilala ng mga organiser ang limitations ng chrF ngunit wala silang mas mahusay na alternatibong maaaring gumana sa magkakaibang typologies na kinakatawan (Quechua, Guaraní, Aymara, Nahuatl, Rarámuri, at iba pa).

Noong 2025, ipinakilala ng AmericasNLP ang nakalaang **Shared Task 3** partikular para sa pagbuo ng MT evaluation metrics para sa Indigenous languages — ang unang pagkakataong tahasang kinilala ng larangan na hindi sapat ang umiiral na metrics para sa mga wikang ito. Pinagsama ng winning submission, **FUSE** (Feature-Union Scorer), ang multilingual sentence embeddings (fine-tuned LaBSE), lexical similarity, phonetic similarity, at fuzzy token matching sa pamamagitan ng Ridge regression at Gradient Boosting. Hindi gumagamit ang FUSE ng morphological analysers — language-agnostic ang feature engineering.

Ito ang gap na kinatatayuan ng aming gawain. Natukoy ng AmericasNLP ang problema (nabibigo ang standard metrics para sa Indigenous languages) at nagsimulang bumuo ng alternatives (FUSE). Ngunit wala sa mga alternatibo ang gumagamit ng morphological knowledge na ibinibigay ng FSTs. Gumagamit ang AmericasNLP community ng chrF++ dahil ito ang pinakamahusay na available generic option, habang bumubuo ang GiellaLT community ng sophisticated morphological tools na hindi kailanman naikakabit sa MT evaluation. Hindi pa nagtatagpo ang dalawang community.

---

## Bahagi 4: Reference-Free Evaluation at Quality Estimation

Ang ilan sa pinakamahalagang evaluation signals sa aming harness ay hindi nangangailangan ng reference translations. Kailangan lamang ng FST validity check ("totoong salita ba ito?") ang MT output. Kailangan ng hallucination detector ang source at hypothesis. Kailangan lamang ng code-switching detector ang hypothesis at kaalaman sa script ng target language. Mahalaga ang pag-unawa kung saan pumapasok ang mga ito sa mas malawak na landscape ng reference-free evaluation upang maiposisyon ang mga ito nang tama.

### Ang Quality Estimation Paradigm

Ang **Quality Estimation (QE)** ay subfield ng MT evaluation na may kinalaman sa paghula ng translation quality *nang walang* reference translations. Isa itong nakalaang shared task sa WMT mula 2012, na udyok ng praktikal na pangangailangang tasahin ang MT quality sa deployment time — kapag nagsasalin kayo ng bagong text at walang human reference na maihahambing dito.

Umunlad ang QE task sa tatlong henerasyon. Ang **Feature-based QE** (2012–2016) ay kumukuha ng hand-crafted features mula sa source at hypothesis — language model perplexity, word frequency, n-gram overlap sa monolingual data — at nagsasanay ng classifiers upang hulaan ang quality. Pinalitan ng **Neural QE** (2017–2021) ang hand-crafted features ng learned representations, karaniwang gamit ang bilingual encoders. Ang **Current QE** (2022–kasalukuyan) ay pinangingibabawan ng COMET-based approaches, partikular ang **CometKiwi**.

### CometKiwi at Reference-Free COMET

Ang **CometKiwi** (Rei et al., WMT 2022), ang reference-free variant ng COMET, ay gumagamit ng InfoXLM upang i-encode ang source sentence at MT hypothesis (nang walang reference) at hulaan ang quality score. Nakamit nito ang state-of-the-art results sa WMT 2022 at 2023 QE shared tasks.

Ang kapansin-pansing finding: lumalapit ang reference-free CometKiwi sa korelasyon sa human judgment na nakamit ng reference-based COMET. Ipinahihiwatig nito na, para sa well-resourced languages, naglalaman ang source text ng halos kasindaming evaluation signal ng reference translation. Ngunit nalalapat ang parehong caveat: minimal ang representasyon ng encoder ng CometKiwi para sa low-resource languages, kaya hindi maaasahan ang reference-free predictions nito para sa Cree o Sámi.

Dito nag-aalok ang aming FST-based metrics ng isang tunay na naiiba. Ang FST validity check ay isang **deterministic, reference-free quality signal** na hindi nangangailangan ng trained model at walang human judgment data. Kung sinasabi ng FST na hindi valid na Cree word ang isang salita, hindi valid na Cree word ang salitang iyon — kasama ang caveat ng false rejections para sa loanwords, neologisms, at proper nouns. Walang katumbas ang ganitong uri ng hard, rule-based quality signal sa neural QE ecosystem.

### Hallucination Detection sa MT

Ang hallucination sa MT — fluent output na ganap na walang kaugnayan sa source — ay seryosong failure mode, partikular sa low-resource settings kung saan kulang ang training data ng models upang matutunan ang maaasahang source-target correspondences.

Gumagamit ang academic state of the art sa hallucination detection ng ilang lapit:

- **Embedding-based detection**: Paghahambing ng source at hypothesis embeddings sa shared space (LASER, LaBSE) at pag-flag ng mga kaso kung saan mas mababa sa threshold ang similarity.
- **Probability-based detection**: Paggamit ng sariling confidence scores ng MT model — kadalasang may mataas na output probability ngunit mababang source-conditioned probability ang hallucinations.
- **Contrastive perturbation**: Paghahambing ng MT output para sa tunay na source laban sa output para sa perturbed o unrelated source; kung kahina-hinalang magkatulad ang outputs, binabalewala ng model ang source.
- **LLM-as-judge**: Pagprompt sa LLM upang tasahin kung faithful ang salin sa source.

Gumagamit ang aming harness ng **heuristic detection plugin** na pinagsasama ang apat na signal: length inflation (hypothesis na mas mahaba kaysa inaasahan), repetition (paulit-ulit na phrases), entity mismatch (named entities sa source na nawawala sa hypothesis), at source echo (napakahawig ng hypothesis sa source text, na nagpapahiwatig ng hindi naisaling copying). Baseline-level ito kumpara sa academic SOTA — nahuhuli nito ang gross hallucinations ngunit makakaligtaan ang subtle ones. Ang halaga nito ay bilang **mura, mabilis, reference-free screen** na maaaring mag-flag ng pinakamasamang failures nang hindi nangangailangan ng GPU o API call.

### Code-Switching Detection

Ang code-switching sa MT output — kung saan gumagawa ang sistema ng mga salita sa source language sa halip na isalin ang mga ito — ay distinct failure mode mula sa hallucination. Karaniwan itong nangyayari kapag nakatagpo ang model ng salitang hindi nito maisalin at bumabalik sa pagkopya ng source.

Gumagamit ang aming code-switching detection plugin ng **Unicode block analysis** (pagtukoy ng characters mula sa script ng source language sa dapat ay target-language output) at **common-word lists** (pagtukoy ng high-frequency source-language words na lumilitaw na hindi naisalin). Para sa Cree, na gumagamit ng parehong SRO (Latin-based) at syllabics, nangangailangan ito ng pag-iingat — magkapareho ang Latin script ng English at SRO, kaya hindi sapat ang Unicode block analysis lamang.

Manipis ang academic literature sa code-switching detection sa MT kumpara sa hallucination detection. Karamihan ng gawain ay nakatuon sa code-switching sa *input* text (bilingual speakers na naghahalo ng wika) sa halip na sa *output* text (MT systems na nabibigong magsalin). Ang aming heuristic approach ay, sa aming kaalaman, hindi malayong nahuhuli sa anumang published state of the art para sa partikular na problemang ito.

---

## Bahagi 5: Ang Morphological Gap

### Ano ang Hindi Nakikita ng Umiiral na Metrics

Ito ang pangunahing argumento ng papel na ito, at nangangailangan ito ng konkretong demonstrasyon.

Isaalang-alang ang Plains Cree sentence pair:

| | Teksto |
|--|------|
| **Source (English)** | "I saw the man" |
| **Reference (Cree)** | *nikî-wâpamâw nâpêw* |
| **Hypothesis A** | *nâpêw nikî-wâpamâw* |
| **Hypothesis B** | *nikî-wâpamikow nâpêsis* |

Ang **Hypothesis A** ay perpektong salin — pareho ang mga salita sa ibang ayos, na grammatical sa Cree (free word order). Ang **Hypothesis B** ay nagsasabing "the boy was seen by me" — maling direksyon ng aksyon (*-ikow* ay inverse), maling referent (*nâpêsis* = "boy", hindi "man").

| Metric | Hypothesis A (tama) | Hypothesis B (mali) | Kaya ba nitong pag-ibahin ang mga ito? |
|--------|----------------------|---------------------|------------------------|
| BLEU | ~30% | ~20% | Bahagya lamang |
| chrF++ | ~65% | ~55% | Medyo |
| COMET | Hindi alam (walang Cree training data) | Hindi alam | Hindi maaasahan |
| **FST acceptance** | 100% | 100% | Hindi (parehong valid Cree) |
| **Linter** | EQUIVALENT (WORD_ORDER) | MISS | **Oo** |
| **Semantic validator** | VALID | WRONG | **Oo** |

Nagtagumpay ang linter at semantic validator kung saan nabigo ang BLEU, chrF++, at COMET — hindi dahil "mas mahusay na metrics" sila sa unibersal na diwa, kundi dahil may access sila sa *linguistic knowledge* na wala sa string-matching at neural metrics. Alam nila na may free word order ang Cree. Alam nila na magkaibang lemmas na may magkaibang argument structures ang *wâpamêw* at *wâpamikow*. Alam nila na magkaibang salita ang *nâpêw* at *nâpêsis*.

Nagmumula ang kaalamang ito sa FST (na nag-eencode ng morphological grammar), bilingual dictionary (na nagbibigay ng English glosses para sa bawat lemma), at manually-defined variant classes (na nag-eencode ng linguistically-grounded equivalence rules). Wala sa kaalamang ito ang available sa metric na itinuturing ang translation bilang string.

### Bakit Hindi Ito Natugunan ng Larangan

Hindi misteryo ang morphological gap sa MT evaluation. Alam ng larangan na umiiral ito. Structural ang mga dahilan kung bakit nagpapatuloy ito:

1. **Scale bias.** Inooptimize ng MT evaluation community ang metrics na gumagana sa lahat ng WMT language pairs. Gumagana ang FST-based metrics para sa ~30 languages. Gumagana ang COMET para sa 100+. Gumagana ang chrF++ para sa lahat ng wikang may writing system. Ginagantimpalaan ng community ang universality kaysa precision.

2. **Community silos.** Ang mga taong bumubuo ng FSTs (computational linguists sa UiT Tromsø, NRC Canada, University of Alberta) at ang mga taong bumubuo ng evaluation metrics (ML researchers sa Google, Unbabel, WMT) ay dumadalo sa magkakaibang conferences, naglalathala sa magkakaibang venues, at kumikilos sa ilalim ng magkakaibang incentive structures. Hindi pa nangyayari ang cross-pollination na kakailanganin upang bumuo ng FST-based evaluation metrics — hindi dahil sinubukan ito at nabigo, kundi dahil hindi kailanman nagtagpo ang communities.

3. **Coverage anxiety.** May kilalang false-rejection problems ang FSTs: maaaring tanggihan bilang invalid ang loanwords, neologisms, at proper nouns kahit ganap na acceptable ang mga ito. Kinakabahan dito ang researchers sa paggamit ng FSTs bilang metrics — pinapalaki ng false rejection ang error rate. Valid ang alalahanin ngunit quantifiable: straightforward ang pagsukat ng false rejection rate sa known-good text.

4. **Insufficient demand.** Napakakaunti ng bumubuo ng MT para sa polysynthetic languages, at ang mga gumagawa nito (ALT Lab, NRC, AmericasNLP participants) ay karaniwang gumagamit ng chrF++ dahil iyon ang umiiral. Walang concerted push mula sa low-resource MT community para sa morphology-aware evaluation, bahagya dahil maliit ang community at bahagya dahil ang pagbuo ng ganitong metrics ay nangangailangan ng expertise sa parehong NLP engineering at morphology ng partikular na target language.

5. **Ang neural metric assumption.** Ang namamayaning palagay mula 2020 ay sa kalaunan ay malulutas ng neural metrics ang morphological problem sa pamamagitan ng learned representations. Kung magsasanay kayo ng COMET sa sapat na data mula sa morphologically rich languages, ayon sa argumento, matututo itong hawakan ang morphological variation implicitly. Maaaring totoo ito para sa high-resource morphologically rich languages (Finnish, Turkish, Czech). Malamang hindi ito totoo para sa mga wikang halos zero ang representasyon sa training data.

---

## Bahagi 6: LYSS — Isang Linguistically-Grounded na Alternatibo

### Ang Binuo ng champollion: LYSS (Linguistically-informed Yield & Structural Scoring)

Ang evaluation harness ng champollion project ay nagpapatupad ng composite scoring framework na tinatawag na **LYSS** na pinagsasama ang standard metrics (chrF++, exact match) sa apat na kategorya ng linguistically-informed metrics. Ipinapakita ng pangalan ang pokus ng framework: pagsukat sa *yield* (gaano karaming kahulugan ang nakaliligtas sa proseso ng pagsasalin) sa pamamagitan ng *structural scoring* (deterministic, linguistically-grounded checks sa halip na learned embeddings).

#### 1. Morphological Validity Gate (GiellaLT FST Metric)

Ang pinakasimple at pinakamalawak na naaangkop na metric: ipasok ang bawat salita ng MT output sa GiellaLT finite-state morphological analyser para sa target language. Kung kayang i-parse ng FST ang isang salita (nagbabalik ng hindi bababa sa isang analysis), morphologically valid ang salita. Kung hindi, hindi umiiral ang salita sa target language — ito ay hallucinated word, morphological error, misspelling, o loanword na wala sa lexicon.

**Output:** `fst_validity_rate` (0.0–1.0, mas mataas = mas mabuti). Macro-average (mean ng per-entry rates) at micro-average (kabuuang valid words / kabuuang words).

**Dependencies:** `pyhfst` (Helsinki Finite-State Technology Python bindings), isang compiled `.hfstol` analyser file para sa target language.

**Extensibility:** Gumagana para sa anumang wikang may GiellaLT FST analyser — kasalukuyang ~30+ languages, pangunahing Sámi, Uralic, at indigenous Arctic languages.

**Relation to prior art:** Sinusubok ng MorphEval kung kaya ng isang sistema ang specific contrasts. Sinusubok ng FST metric kung binubuo ng totoong mga salita ang output ng sistema. Complementary ang mga ito: sinusubok ng MorphEval ang competence, sinusubok ng FST metric ang validity.

#### 2. Linguistic Equivalence Classes (CRK Linter)

Tinutugunan ng linter ang maaaring pinakatusong failure mode ng reference-based evaluation: **pagpaparusa sa mga tamang salin na naiiba sa reference**.

Ang Plains Cree linter (844 lines) ay nagpapatupad ng anim na **variant classes**, bawat isa ay nag-eencode ng linguistically-grounded equivalence rule:

- **WORD_ORDER**: May pragmatically free word order ang Cree (Wolfart, 1973 §3.2). Pareho ang kahulugan ng *nikî-wâpamâw nâpêw* at *nâpêw nikî-wâpamâw*. Bumubuo ang linter ng lahat ng permutations at sinusuri kung tumutugma ang hypothesis sa alinman.
- **ORTHOGRAPHIC**: May kilalang variation points ang Standard Roman Orthography — circumflex vs. macron (*â* vs. *ā*), hyphenation ng preverbs (*nikî-nipâw* vs. *nikî nipâw* vs. *nikînipâw*). Nino-normalize ng linter ang mga ito.
- **OPTIONAL_PARTICLE**: Maaaring naroon o wala ang ilang discourse particles (*mâka*, *êkwa*, *êwako*) nang hindi binabago ang core proposition. Sinusuri ng linter kung tumutugma ang hypothesis sa reference pagkatapos alisin ang particle.
- **LEMMA_SYNONYM**: May ilang Cree lemmas na interchangeable sa specific contexts. Gumagamit ito ng curated synonym list (hal., dialectal variants) at, kapag available ang FST, sinusuri kung nagbabahagi ang hypothesis at reference ng morphological analyses.
- **PROGRESSIVE_AMBIGUITY**: Maaaring isalin sa Cree ang English progressive forms ("is walking") gamit ang iba’t ibang constructions. Kinikilala ng linter ang mga ito bilang equivalent.
- **INCLUSIVE_EXCLUSIVE**: Tinutukoy ng Cree ang inclusive "we" (*ki-* prefix) mula sa exclusive "we" (*ni-* prefix) — isang distinction na pinagsasama ng English sa iisang pronoun. Kinikilala ng linter na maaaring tama ang alinmang form kapag ambiguous ang English source.

Gumagawa ang linter ng tatlong verdict: **EXACT** (tumutugma ang hypothesis sa reference), **EQUIVALENT** (naiiba ang hypothesis ngunit inuri bilang valid variant), o **MISS** (walang nahanap na match). Sa aggregate level, kinakalkula nito ang `equivalent_match_rate` — ang proportion ng translations na exact o equivalent.

**Relation to prior art:** Ang pinakamalapit na parallel ay **HyTER** (Dreyer & Marcu, NAACL-HLT 2012), na nag-eencode ng exponentially many valid translations bilang paraphrase networks at sumusukat ng edit distance sa pinakamalapit na valid form. Conceptually similar ang aming linter — nagtatakda ito ng hanay ng valid translations para sa bawat reference — ngunit gumagamit ng linguistically-defined transformation rules sa halip na paraphrase databases. Idinisenyo ang HyTER para sa English; walang nakabuo ng paraphrase networks para sa Cree. Ang aming variant classes ay, sa bisa, compact, rule-based approximation ng ginagawa ng HyTER gamit ang graphs.

Sa CheckList framework, gumagana ang aming variant classes bilang **invariance tests**: transformations na hindi dapat magbago ng evaluation verdict. Ang pagkakaiba ay karaniwang inilalapat ang CheckList tests sa *model*; inilalapat ang aming variant rules sa *metric*.

#### 3. Deterministic Semantic Validation (CRK Semantic Metric)

Nagtatangka ang semantic validator (792 lines) ng mas ambisyosong bagay: **deterministic meaning comparison** nang walang neural embeddings. Gumagana ito sa apat na stage:

1. **Morphological analysis**: Ipinapasa ang hypothesis at reference sa CRK FST analyser, na nagbabalik ng lemma at morphological features para sa bawat salita.
2. **Gloss resolution**: Hinahanap ang bawat lemma sa Cree–English dictionary (Wolvengrey, 2001) upang makuha ang English glosses.
3. **Content-word extraction**: Gamit ang English pipeline ng spaCy (`en_core_web_md`), fini-filter ang function words mula sa parehong English glosses at source text.
4. **Overlap scoring**: Tinutukoy ng content-word overlap sa pagitan ng glosses ng hypothesis at glosses ng reference ang semantic verdict.

Gumagawa ang validator ng categorical verdicts: **EXACT_MATCH**, **VALID** (magkaibang salita ngunit parehong kahulugan), **GRAMMAR_ISSUES** (tamang lemmas ngunit may sentence-level grammar problems — agreement, animacy, verb form), **PARTIAL** (may ilang kahulugang napreserba), **INCOMPLETE** (bahagyang nawawala ang kahulugan), **WRONG** (ibang kahulugan), o **NO_OUTPUT**.

**Relation to prior art:** Ito ay, sa bisa, isang **deterministic approximation ng semantic similarity computation ng COMET**. Kung gumagamit ang COMET ng learned cross-lingual embeddings upang tasahin kung pareho ang kahulugan ng dalawang pangungusap, gumagamit ang aming validator ng chain ng deterministic lookups: FST → dictionary → spaCy. Ang bentahe ay transparency (inspectable at deterministic ang bawat hakbang) at independence mula sa training data. Ang disbentahe ay brittleness: lubos na nakadepende ang kalidad ng assessment sa coverage ng FST at completeness ng dictionary.

Conceptually related ang lapit sa **MEANT** (Lo & Wu, 2011; Lo, 2017), na gumamit ng semantic role labelling upang tasahin kung napreserba ang "who did what to whom" structure sa translation. Mas coarse-grained ang aming lapit (content-word overlap sa halip na semantic roles) ngunit gumagana ito sa wikang walang SRL tools.

#### 4. Behavioral Detection Plugins (Hallucination, Code-Switching, Terminology)

Tatlong karagdagang plugin ang nagbibigay ng **behavioral quality signals** na kumukumplemento sa morphological metrics:

- **Hallucination detection** (259 lines): Apat na heuristic signals na weighted at pinagsama — length inflation (40%), repetition (30%), entity mismatch (20%), source echo (10%). Mura at reference-free screens ang mga ito na nakakahuli ng gross fabrication.
- **Code-switching detection** (~280 lines): Unicode block analysis plus common-word lists upang matukoy ang untranslated source-language tokens. Naglalabas ng `code_switching_rate` (0.0–1.0).
- **Terminology adherence** (199 lines): Sinusuri kung consistent na isinasalin ang specified glossary terms. Nagbabalik ng `terminology_adherence` (0.0–1.0) o None kung walang configured na glossary.

Tapat na ipinoposisyon ang mga plugin na ito bilang **baseline heuristic detectors**, hindi state-of-the-art. Ang halaga nito ay pagbibigay ng mura, mabilis, interpretable signals na maaaring kalkulahin kasabay ng mas sophisticated morphological metrics. Sa composite scoring framework, mababa ang weights ng mga ito (0.05 bawat isa).

### Matapat na Limitasyon

May makabuluhang limitations ang lapit na ito na kailangang kilalanin bago ang anumang claim ng novelty o utility:

1. **FST false rejection rate.** Tatanggihan ng FST ang valid words na wala sa lexicon nito — loanwords, neologisms, proper nouns, code-mixed terms. Pinapalaki nito ang morphological error rate. Hindi pa pormal na nasusukat ang false rejection rate sa representative corpus ng Cree text. Kung wala ang sukat na ito, hindi alam ang precision ng FST validity metric.

2. **Dictionary coverage.** Lubos na nakadepende ang kalidad ng semantic validator sa coverage ng Wolvengrey dictionary. Ang Cree words na wala sa dictionary ay walang glosses, na itinuturing ng validator bilang meaning gap. May humigit-kumulang 22,000 entries ang dictionary — substantial, ngunit hindi exhaustive.

3. **Variant class completeness.** Dinisenyo ang anim na variant classes ng linter batay sa linguistic literature at obserbasyon ng MT output patterns. Maaaring may karagdagang equivalence classes na hindi nahuhuli — dialectal variations, register differences, discourse-level synonyms. Walang formal process na tumitiyak ng completeness.

4. **Walang human correlation study.** Ang pinakakritikal na gap: walang nakapagsukat kung ang verdicts ng linter (EXACT/EQUIVALENT/MISS) o verdicts ng semantic validator ay nagko-correlate sa human judgments ng translation quality. Gumugugol ng taon ang neural metrics sa pagtatatag ng korelasyon sa human assessment (WMT shared tasks). Walang ganitong validation ang aming metrics.

5. **Language specificity.** Specific sa Plains Cree ang variant classes, synonym lists, at optional particle rules. Ang pag-port nito sa North Sámi, Inuktitut, o anumang ibang wika ay nangangailangan ng linguists na nakauunawa sa morphology, word order flexibility, at orthographic variation ng wikang iyon. Portable ang *framework*; hindi portable ang *rules*.

6. **Metric wiring gaps.** Sa kasalukuyang pagsulat, apat sa siyam na metrics sa composite scoring profile (semantic_score, morphological_accuracy, equivalent_match_rate, orthographic_accuracy) ay may incomplete o unclear plugin wiring sa arena harness. Epektibong kinakalkula ang composite score mula sa humigit-kumulang limang metrics na may redistributed weights.

### Ano ang Kakailanganin upang I-validate ang Lapit na Ito

Upang maging publishable ang gawaing ito — sa anumang venue, sa anumang antas ng academic seriousness — kakailanganin ang sumusunod na experiments:

1. **Human judgment correlation study.** Mangolekta ng human quality assessments para sa isang hanay ng English→Cree translations (ideally 200+ sentence pairs na tinasa ng 3+ bilingual speakers). Kalkulahin ang correlations sa pagitan ng human scores at bawat isa sa aming metrics. Ito ang nag-iisang pinakamahalagang validation. Kung wala ito, engineering artifacts ang metrics, hindi evaluation tools.

2. **FST false rejection rate measurement.** Patakbuhin ang FST analyser sa corpus ng known-good Cree text (hal., published Cree texts, validated parallel corpora) at sukatin kung ilang porsiyento ng valid words ang nare-reject. Kinukuwantipika nito ang precision ng FST validity metric.

3. **Second-language validation.** I-port ang FST validity metric sa ikalawang GiellaLT language (pinakamalamang North Sámi, na may pinakamatandang FST analyser sa GiellaLT ecosystem). Ipakita na gumagawa ang metric ng sensible results sa Sámi MT output. Vine-validate nito ang claim ng extensibility.

4. **Comparison with COMET.** Patakbuhin ang COMET sa parehong Cree data at ihambing ang scores nito sa aming metrics at sa human judgments. Kung gumagawa ang COMET ng meaningful scores para sa Cree (na duda kami, ngunit hindi pa nasusubok), kailangang talunin ito ng aming metrics upang maging kapaki-pakinabang. Kung gumagawa ang COMET ng noise (na inaasahan namin), vine-validate nito ang pangangailangan sa aming lapit.

5. **MorphEval diagnostic complement.** Bumuo ng maliit (50–100 contrasts) na MorphEval-style test suite para sa Plains Cree na tumatarget sa pinakanatatanging morphological features ng wika (obviative, inverse, conjunct/independent, inclusive/exclusive). Patakbuhin ang MT systems laban dito at ipakita na actionable ang diagnostic information.

6. **Wiring and integration audit.** Ayusin ang scoring profile wiring gaps na natukoy sa codebase inventory. Tiyakin na lahat ng siyam na composite metrics ay gumagawa ng values at tama ang pagkalkula ng aggregate score.

---

## Bahagi 7: Positioning at Future Work

### Saan Nakapuwesto ang LYSS sa Evaluation Landscape

Isang taxonomy ng MT evaluation approaches, tapat na ipinoposisyon:

| Dimension | String metrics (BLEU, chrF++) | Neural metrics (COMET, MetricX) | LLM-as-judge (GEMBA) | Diagnostic (MorphEval, CheckList) | **LYSS** |
|-----------|-------------------------------|---|----|-------|--------|
| Signal type | Surface overlap | Learned semantic similarity | Open-ended judgment | Targeted capability probes | Morphological validity + rule-based equivalence |
| Training data needed | Wala | Human judgments (libo-libo) | Pre-trained LLM | Linguist-designed test suites | FST + dictionary + variant rules |
| LRL applicability | Universal ngunit mahina | Limitado ng encoder coverage | Limitado ng LLM coverage | Limitado ng paglikha ng test suite | Limitado ng FST availability (~30 languages) |
| Reference needed | Oo | Oo (o source-only QE) | Optional | Oo (contrastive) | Oo (LYSS-eq/LYSS-sem) / Hindi (LYSS-fst) |
| Interpretability | Mababa (isang numero) | Mababa (isang numero) | Mataas (text rationale) | Mataas (pass/fail kada phenomenon) | Mataas (verdicts + variant classes) |

**Ang LYSS ay hindi**: kapalit ng COMET sa well-resourced languages, universal metric, o ang unang morphology-aware evaluation.

**Ang LYSS ay**: isang integrated framework na pinagsasama ang FST-based morphological validation sa standard metrics para sa partikular na kaso ng mga wikang kulang ang coverage ng neural metrics at umiiral ang rule-based tools (FSTs, dictionaries). Mayroon itong tatlong core components:
- **LYSS-fst** — Morphological validity sa pamamagitan ng FST (`fst_acceptance_rate`)
- **LYSS-eq** — Linguistic equivalence sa pamamagitan ng linter (`equivalent_match_rate`)
- **LYSS-sem** — Deterministic semantic validation (`semantic_score`)

**Pinalalawak ng LYSS**: ang core insight ng MorphEval (gumamit ng morphological tools para sa evaluation) mula diagnostic competence testing tungo sa continuous quality scoring.

**Kinukumplemento ng LYSS**: chrF++ (na nagbibigay ng partial credit para sa shared morphemes ngunit hindi makakatukoy ng equivalence), COMET (na gumagana sa semantic space ngunit kulang sa training data para sa LRL), at FUSE (na gumagamit ng feature engineering ngunit hindi morphological analysers).

**Ang pinakamalapit na prior art ay**: Hjerson (linguistic error classification) + HyTER (equivalence classes sa pamamagitan ng paraphrase networks) + naïve coverage metric ng Apertium (FST-based validity checking). Ang kontribusyon ng LYSS ay hindi iisang technique kundi ang integrasyon ng mga ideyang ito — partikular ang FST-based validity at rule-based equivalence — sa isang gumaganang evaluation harness para sa polysynthetic language.

### Integrating MorphEval

Complementary ang contrastive test suite methodology ng MorphEval at ang aming continuous scoring approach:

- **MorphEval** answers: "Kaya ba ng sistemang ito ang tense marking? Number agreement? Case assignment?"
- **Our FST metric** answers: "Gumawa ba ang sistemang ito ng totoong mga salita?"
- **Our linter** answers: "Equivalent ba ang salin na ito sa reference sa kabila ng surface differences?"
- **Our semantic validator** answers: "Tama ba ang kahulugan ng salin na ito?"

Open source ang MorphEval. Ang paglikha ng Plains Cree test suite ay mangangailangan ng linguist na magdisenyo ng contrastive pairs na sumasaklaw sa Cree-specific morphological contrasts (obviation, inverse marking, conjunct/independent order, inclusive/exclusive "we," preverb chains). Substantial ngunit bounded work ito — linggo, hindi buwan — at magbibigay ito ng diagnostic capability na wala pang ibang evaluation tool para sa Cree.

### Ang Tanong ng Extensibility

Aling iba pang mga wika ang maaaring gumamit ng lapit na ito? Ang pangunahing constraint ay FST availability. Nagbibigay ang GiellaLT infrastructure ng morphological analysers para sa 30+ languages, pangunahin sa tatlong pamilya:

- **Sámi languages** (North Sámi, Lule Sámi, South Sámi, Skolt Sámi, Inari Sámi): Mature FSTs na may malawak na coverage. North Sámi ang pinakamadaling i-port na target.
- **Uralic languages** (Finnish, Estonian, Komi, Erzya, Moksha): Well-developed analysers, bagaman maaaring hindi ganoon kaagarang kailangan ng Finnish at Estonian ang FST-based evaluation (mayroon silang mas maraming neural metric coverage).
- **Indigenous Arctic languages** (Inuktitut via Uqailaut, Greenlandic): Umiiral ang analysers ngunit nag-iiba ang coverage.
- **Other GiellaLT languages**: Faroese, Irish, Cornish, Livonian, at iba pa na may iba’t ibang antas ng FST maturity.

Sa labas ng GiellaLT, nagbibigay ang **Apertium** platform ng morphological analysers para sa humigit-kumulang 40+ language pairs. Ang **HFST** ecosystem (Helsinki Finite-State Technology) ang shared infrastructure na ginagamit ng parehong GiellaLT at Apertium, na nangangahulugang sa prinsipyo ay maaaring ikabit ang anumang Apertium analyser sa parehong FST validity metric.

Ang praktikal na constraint ay hindi FST availability kundi **variant class curation**. Nangangailangan ang equivalence rules ng linter ng linguistic expertise kada target language. Para sa North Sámi, mangangailangan ito ng pag-unawa sa Sámi word order flexibility, orthographic conventions, at dialectal variation. Para sa Inuktitut, mangangailangan ito ng pag-unawa sa polysynthetic morphology sa antas na maihahambing sa ginawa para sa Cree. Gayunman, maaaring i-deploy kaagad ang FST validity metric para sa anumang wikang may GiellaLT analyser — walang karagdagang linguistic work na kailangan.

### Tungo sa Isang Papel

Ang publikasyong batay sa gawaing ito ay pinakanatural na magta-target sa isa sa mga venue na ito:

- **WMT Metrics Shared Task** (co-located with EMNLP): Ang pinakadirektang venue. Mangangailangan ng pagpapatupad ng metrics bilang shared-task submission at evaluation sa WMT test sets — na kasalukuyang walang kasamang anumang polysynthetic language. Maaaring magsumite bilang "findings" paper o lumahok sa challenge sets subtask.
- **LREC-COLING** (Language Resources and Evaluation Conference): Natural fit para sa resource/tool paper na naglalarawan sa evaluation framework at linguistic resources na ginagamit nito (FSTs, dictionaries, variant rules).
- **ACL or NAACL** (main conference): Mangangailangan ng human correlation study at hindi bababa sa isang karagdagang wika upang maabot ang bar para sa main conference paper.
- **AmericasNLP workshop**: Ang pinakareceptive na audience para sa Indigenous language MT evaluation. Mas mababang publication bar, ngunit mataas ang impact sa target community.
- **ComputEL** (Computational Approaches to Endangered Languages): Focused venue para mismo sa ganitong uri ng gawain.

Anumang publikasyon ay mangangailangan ng co-authors na may expertise sa Cree linguistics (upang i-validate ang variant classes at bigyang-kahulugan ang results) at ideally bilingual Cree speakers (upang magbigay ng human quality assessments para sa correlation study). Hindi ito optional — ang papel tungkol sa Cree MT evaluation na isinulat nang ganap ng non-Cree-speakers ay, sa pinakamahusay, incomplete, at sa pinakamasama, pagpapatuloy ng extractive research dynamics na sinusubukang lampasan ng larangan.

---

## Appendix A: Metric Requirements Matrix

| Metric | Kailangan ba ng reference? | Kailangan ba ng source? | Trained model? | Language-specific resources? | Gumagana para sa LRL? |
|--------|-------------------|---------------|----------------|------------------------------|----------------|
| BLEU | Oo | Hindi | Hindi | Hindi | Mahina |
| chrF++ | Oo | Hindi | Hindi | Hindi | Mas mahusay kaysa BLEU |
| METEOR | Oo | Hindi | Hindi | Stemmer + WordNet | Kung umiiral lang ang resources |
| TER | Oo | Hindi | Hindi | Hindi | Pareho ng BLEU |
| BERTScore | Oo | Hindi | Oo (mBERT) | Hindi | Depende sa model coverage |
| BLEURT | Oo | Hindi | Oo (trained) | Hindi | Depende sa training data |
| COMET | Oo | Oo | Oo (XLM-R) | Hindi | Depende sa XLM-R coverage |
| CometKiwi | Hindi | Oo | Oo (XLM-R) | Hindi | Depende sa XLM-R coverage |
| GEMBA | Optional | Oo | Oo (LLM) | Hindi | Depende sa LLM coverage |
| **FST acceptance** | **Hindi** | **Hindi** | **Hindi** | **Oo (FST analyser)** | **Oo, kung may FST** |
| **CRK Linter** | **Oo** | **Hindi** | **Hindi** | **Oo (FST + variant rules)** | **Oo, kung may resources** |
| **CRK Semantic** | **Oo** | **Optional** | **Hindi** | **Oo (FST + dictionary + spaCy)** | **Oo, kung may resources** |
| Hallucination det. | Hindi | Oo | Hindi | Hindi | Oo |
| Code-switching det. | Optional | Oo | Hindi | Minimal | Oo |
| MorphEval | Oo (contrastive) | Oo | Hindi | Oo (test suite + analyser) | Kung may test suite lang |

## Appendix B: Mahahalagang Papel

| Citation | Venue | Relevance |
|----------|-------|-----------|
| Papineni et al. (2002). BLEU: a Method for Automatic Evaluation of Machine Translation | ACL 2002 | Ang metric na nagtakda sa larangan |
| Doddington (2002). Automatic Evaluation of Machine Translation Quality Using N-gram Co-Occurrence Statistics | HLT 2002 | Information-weighted n-gram matching |
| Banerjee & Lavie (2005). METEOR: An Automatic Metric for MT Evaluation | ACL 2005 Workshop | Stemming, synonyms, word alignment |
| Snover et al. (2006). A Study of Translation Edit Rate | AMTA 2006 | Edit distance na may phrase shifts |
| Popović & Ney (2011). Morphemes and POS tags for n-gram based evaluation metrics | WMT 2011 | Hjerson error classification |
| Dreyer & Marcu (2012). HyTER: Meaning-Equivalent Semantics for Translation Evaluation | NAACL-HLT 2012 | Equivalence classes sa pamamagitan ng paraphrase networks |
| Lommel et al. (2014). Multidimensional Quality Metrics | — | MQM error typology |
| Popović (2015). chrF: character n-gram F-score for automatic MT evaluation | WMT 2015 | Character-level evaluation |
| Popović (2017). chrF++: words helping character n-grams | WMT 2017 | Character + word n-gram evaluation |
| Burlot & Yvon (2017). Evaluating the Morphological Competence of Machine Translation Systems | WMT 2017 | Contrastive morphological test suites |
| Sennrich (2017). How Grammatical is Character-level Neural Machine Translation? | EACL 2017 | LingEval97 contrastive pairs |
| Isabelle, Cherry & Foster (2017). A Challenge Set Approach to Evaluating Machine Translation | EMNLP 2017 | Targeted structural divergence testing |
| Post (2018). A Call for Clarity in Reporting BLEU Scores | WMT 2018 | sacreBLEU standardisation |
| Reiter (2018). A Structured Review of the Validity of BLEU | Computational Linguistics | Meta-analysis ng korelasyon ng BLEU sa human judgment |
| Stanovsky, Smith & Zettlemoyer (2019). Evaluating Gender Bias in Machine Translation | ACL 2019 | WinoMT gender evaluation |
| Ribeiro et al. (2020). Beyond Accuracy: Behavioral Testing of NLP Models with CheckList | ACL 2020 (Best Paper) | Capability-based unit testing para sa NLP |
| Zhang et al. (2020). BERTScore: Evaluating Text Generation with BERT | ICLR 2020 | Embedding-based semantic similarity |
| Sellam et al. (2020). BLEURT: Learning Robust Metrics for Text Generation | ACL 2020 | Pre-trained + fine-tuned metric |
| Rei et al. (2020). COMET: A Neural Framework for MT Evaluation | EMNLP 2020 | Cross-lingual trilingual evaluation |
| Freitag et al. (2021). Results of the WMT 2021 Metrics Shared Task | WMT 2021 | MQM-based meta-evaluation |
| Thompson & Post (2020). PRISM: Automatic MT Evaluation via Zero-Shot Paraphrasing | EMNLP 2020 | Multilingual NMT bilang paraphrase scorer |
| Currey et al. (2022). MT-GenEval | EMNLP 2022 | Counterfactual gender accuracy |
| Amrhein et al. (2022). ACES: Translation Accuracy Challenge Sets | WMT 2022 | 68 phenomena, 146 language pairs |
| Kocmi & Federmann (2023). GEMBA: Large Language Models Are State-of-the-Art Evaluators | EAMT 2023 | LLM-as-evaluator |
| Guerreiro et al. (2024). xCOMET: Transparent MT Evaluation through Fine-grained Error Detection | TACL 2024 | Error span detection |
| Wang & Adelani (2024). AfriMTE and AfriCOMET | NAACL 2024 | Neural metrics para sa African languages |
| Juraska et al. (2024). MetricX-24 | WMT 2024 | mT5-based winning metric |

## Appendix C: Glossary ng Evaluation Terms

| Term | Definition |
|------|------------|
| **Adequacy** | Kung naipapahayag ng isang salin ang kahulugan ng source. |
| **Fluency** | Kung grammatical at natural ang isang salin sa target language. |
| **Direct Assessment (DA)** | Human evaluation method kung saan nire-rate ng annotators ang translations sa 0–100 scale. |
| **MQM** | Multidimensional Quality Metrics — error-span-based human evaluation na may typed severities. |
| **Quality Estimation (QE)** | Paghula ng translation quality nang walang reference translation. |
| **FST** | Finite-State Transducer — computational device na nag-eencode ng morphological rules ng isang wika. |
| **GiellaLT** | Infrastructure para sa rule-based language technology, pangunahin para sa Sámi at iba pang Arctic languages. |
| **HFST** | Helsinki Finite-State Technology — ang software framework na pinagbabatayan ng GiellaLT at Apertium. |
| **SRO** | Standard Roman Orthography — ang Latin-based writing system para sa Plains Cree. |
| **Syllabics** | Canadian Aboriginal Syllabics — isang abugida writing system na ginagamit para sa Cree at iba pang Algonquian languages. |
| **Polysynthetic** | Uri ng wika kung saan maaaring i-encode ng iisang salita ang katumbas ng buong English sentence sa pamamagitan ng malawak na affixation. |
| **Obviation** | Grammatical category sa Algonquian languages na nagtatangi sa pagitan ng dalawang third-person referents. |
| **Inverse** | Voice-like category sa Algonquian languages na nagmamarka na mas mataas ang patient kaysa agent sa animacy hierarchy. |
| **WMT** | Conference on Machine Translation — ang pangunahing venue para sa MT shared tasks at evaluation. |
| **Contrastive evaluation** | Pagsubok kung kaya ng isang sistema na makilala ang minimally-different inputs na nangangailangan ng magkaibang outputs. |
| **Challenge set** | Crafted test suite na tumatarget sa specific linguistic phenomena. |
| **Equivalence class** | Hanay ng magkakaibang surface forms na kumakatawan sa parehong kahulugan at dapat tumanggap ng parehong evaluation score. |