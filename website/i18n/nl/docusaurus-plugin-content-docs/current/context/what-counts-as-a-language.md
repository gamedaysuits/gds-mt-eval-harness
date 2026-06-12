---
sidebar_position: 2
title: "Wat telt hier als een taal?"
---
# Wat telt hier als een taal?

> **Samenvatting.** De Arena catalogiseert talen op basis van ISO 639-3, benchmarkt individuele talen (geen macrotaalkoepels), beschouwt gebarentalen als de natuurlijke talen die ze zijn, neemt door ISO erkende kunsttalen op, sluit programmeertalen uit en geeft taxonomische meningsverschillen weer zonder partij te kiezen. Deze pagina legt elke keuze uit en wat die betekent voor het leaderboard.

Elk project dat vertaling over duizenden talen benchmarkt, moet een oud en verrassend moeilijk vraagstuk beantwoorden: wat telt als een taal? Taalkundigen weten al lang dat de grens tussen "taal" en "dialect" even goed sociaal en politiek als structureel van aard is — de beroemde uitspraak dat *"een taal een dialect is met een leger en een marine"* werd gepopulariseerd door de Jiddische taalkundige Max Weinreich in 1945 (hij schreef die toe aan een toehoorder tijdens een van zijn lezingen). We kunnen de vraag niet ontwijken, dus hier zijn onze antwoorden en onze redenering.

---

## Gebarentalen zijn talen. Punt.

Gebarentalen zijn natuurlijke talen — met volledige grammatica's, moedertaalverwerving door kinderen en levende taalgemeenschappen. Dit staat vast in de taalkunde sinds William Stokoe in 1960 aantoonde dat American Sign Language dezelfde interne structuur heeft als gesproken talen, en zestig jaar onderzoek sindsdien (Klima & Bellugi 1979; Sandler & Lillo-Martin 2006) heeft dat alleen maar verder onderbouwd. ISO 639-3 kent gebarentalen individuele taalcodes toe; Glottolog catalogiseert ze naast gesproken taalfamilies. Onze catalogus bevat er meer dan 160, getagd als `modality: signed`.

Sommige zijn bedreigde inheemse talen: Plains Indian Sign Language (`psd`), van oudsher een belangrijke intertribale lingua franca in Noord-Amerika, is tegenwoordig kritiek bedreigd (Davis 2010, *Hand Talk*). Bedreiging van gebarentalen *is* bedreiging van inheemse talen, en dat valt binnen de missie van dit project.

**Een eerlijke noot over reikwijdte.** De Arena benchmarkt momenteel *tekstgebaseerde* machinale vertaling. Machinale vertaling van gebarentalen — waarbij gewerkt wordt met video, ruimtelijke grammatica en talen zonder een breed geadopteerde geschreven vorm — is een ander en grotendeels onopgelost technisch probleem (zie Yin et al. 2021, "Including Signed Languages in Natural Language Processing," ACL). We ondersteunen dit nog niet. Vermeldingen van gebarentalen in onze catalogus vermelden dat expliciet: **nog niet ondersteund — nooit "geen taal."**

## Er zijn twee modaliteiten. Schrijven is er geen van.

Talen kennen twee primaire modaliteiten: **gesproken** en **gebaarde**. Schrijven is geen derde modaliteit — het is een technologie die bovenop een taal is aangebracht, en de meeste talen ter wereld redden het zonder een gestandaardiseerde schrijfwijze. Daarom registreren onze taalkaarten schrijven afzonderlijk (welke schriften een taal gebruikt, of dat er geen gestandaardiseerde orthografie bestaat) en doen dat eerlijk: voor een tekstgebaseerd MT-platform is het al dan niet geschreven zijn van een taal cruciale informatie, geen voetnoot — en een ongeschreven taal is geen mindere taal.

## Kunsttalen: opgenomen. Programmeertalen: uitgesloten.

We volgen de eigen lijn van ISO 639-3. De standaard neemt een kunsttaal alleen op als het een volledige taal is, ontworpen voor menselijke communicatie, met een literatuur en een gemeenschap die haar heeft doorgegeven aan een tweede generatie gebruikers — en sluit computerprogrammeertalen uitdrukkelijk uit. Esperanto, met zijn moedertaalsprekers, voldoet hieraan; Python niet, omdat niemand Python als eerste taal van zijn ouders verwerft. Onze catalogus bevat de twee dozijn kunsttalen die ISO erkent, als zodanig getypeerd, en geen programmeertalen.

## We benchmarken individuele talen, geen koepels

ISO 639-3 maakt onderscheid tussen *individuele talen* en *macrotalen* — koepelcodes zoals `cre` (Cree), `ara` (Arabisch) of `zho` (Chinees) die meerdere nauw verwante individuele talen omvatten. De benchmarkeenheid van de Arena is de **individuele taal**, om een operationele reden: vertaalbronnen zijn varieteitspecifiek. Een morfologische analysator gebouwd voor Plains Cree (`crk`) genereert geen Moose Cree (`crm`); een corpus van Egyptisch Arabisch zegt weinig over de kwaliteit van een methode in Marokkaans Arabisch. Een score gekoppeld aan een koepelcode zou een bewering zijn over variëteiten die nooit daadwerkelijk zijn geëvalueerd — dus dat doen we niet.

Macrotalen verschijnen nog steeds in de catalogus als **hubpagina's**: navigatie die een koepelidentiteit koppelt aan de individuele leden ervan, overeenkomstig de eigen observatie van ISO dat beide niveaus van identiteit reëel zijn. Onder de individuele taal tonen we dialect- en afstammingsinformatie uit de languoid-boom van Glottolog (Hammarström & Forkel 2022), die families, talen en dialecten modelleert als één navigeerbare hiërarchie.

## Wanneer de autoriteiten het oneens zijn, tonen we beide

ISO 639-3 en Glottolog splitsen of groeperen soms anders, en gemeenschappen zijn het soms met beide oneens. Wij oordelen niet. Taalkaarten bevatten een *taxonomische noten*-functie die het meningsverschil met bronnen weergeeft, en de naamgeving volgt de gemeenschap waar die een voorkeur heeft uitgesproken. Of een variëteit "een taal" is, is uiteindelijk deels een kwestie van identiteit — en identiteitsvragen behoren toe aan de gemeenschappen zelf, een principe dat we overnemen uit inheemse gegevensbeheerframeworks zoals OCAP®.

## Een onderzoeksrichting: benchmarks als meetinstrument

Iets wat een arena als deze bijna als bijproduct oplevert, is een nieuw soort bewijs over hoe dicht taalvariëteiten operationeel werkelijk bij elkaar liggen. Als één vertaalmethode, ongewijzigd gehouden, meerdere verwante variëteiten op inzetbare kwaliteit bedient, clusteren die variëteiten in de praktijk; als ze afzonderlijke corpora en afzonderlijke methoden vereisen, zijn ze operationeel onderscheiden — wat de naamgevingspolitiek ook zegt. Dit lijkt op oudere empirische tradities, van intelligibiliteitstests met opgenomen teksten tot geautomatiseerde lexicale-afstandsmaten, met een op inzet gerichte invalshoek.

We bieden dit voorzichtig aan, als onderzoeksrichting en niet als bewering. Resultaten van methodetransfer worden beïnvloed door corpusomvang, domein, orthografie en contaminatie van trainingsdata, en een clustering is altijd relatief ten opzichte van een methode en een kwaliteitsdrempel. Bovenal geldt: dit signaal kan gesprekken over taal en dialect *informeren*, maar overstijgt nooit de manier waarop een gemeenschap haar eigen taal identificeert.

---

## Referenties

- Davis, Jeffrey E. (2010). *Hand Talk: Sign Language among American Indian Nations.* Cambridge University Press.
- Dryer, Matthew S. & Martin Haspelmath, eds. (2013). *The World Atlas of Language Structures Online.* https://wals.info
- Hammarström, Harald & Robert Forkel (2022). "Glottocodes: Identifiers Linking Families, Languages and Dialects to Comprehensive Reference Information." *Semantic Web* 13(6).
- Haugen, Einar (1966). "Dialect, Language, Nation." *American Anthropologist* 68(4).
- ISO 639-3 Registration Authority. "Scope of denotation" and "Types of individual languages." https://iso639-3.sil.org/about/scope · https://iso639-3.sil.org/about/types
- Klima, Edward S. & Ursula Bellugi (1979). *The Signs of Language.* Harvard University Press.
- Sandler, Wendy & Diane Lillo-Martin (2006). *Sign Language and Linguistic Universals.* Cambridge University Press.
- Stokoe, William C. (1960). *Sign Language Structure.* Studies in Linguistics, Occasional Papers 8.
- Weinreich, Max (1945). "Der YIVO un di problemen fun undzer tsayt." *YIVO Bleter* 25(1).
- Yin, Kayo, Amit Moryossef, Julie Hochgesang, Yoav Goldberg & Malihe Alikhani (2021). "Including Signed Languages in Natural Language Processing." *Proc. ACL-IJCNLP 2021.* https://aclanthology.org/2021.acl-long.570/
- First Nations Information Governance Centre. *The First Nations Principles of OCAP®.* https://fnigc.ca/ocap-training/