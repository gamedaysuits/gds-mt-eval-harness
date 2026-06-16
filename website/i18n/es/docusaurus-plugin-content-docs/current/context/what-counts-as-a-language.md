---
sidebar_position: 2
title: "¿Qué se considera un idioma aquí?"
---
# ¿Qué cuenta como un idioma aquí?

> **Resumen ejecutivo.** La Arena cataloga idiomas por ISO 639-3, evalúa idiomas individuales (no macrolenguajes), incluye lenguas de signos como los idiomas naturales que son, incluye lenguas construidas reconocidas por ISO, excluye lenguajes de programación, y muestra disputas taxonómicas sin tomar partido. Esta página explica cada decisión y qué significa para el ranking.

Cualquier proyecto que evalúe traducción en miles de idiomas debe responder una pregunta antigua y sorprendentemente difícil: ¿qué cuenta como un idioma? Los lingüistas saben desde hace mucho tiempo que la frontera entre "idioma" y "dialecto" es tanto social y política como estructural — la famosa frase que *"un idioma es un dialecto con ejército y marina"* fue popularizada por el lingüista yidis Max Weinreich en 1945 (la atribuyó a un miembro de la audiencia en una de sus conferencias). No podemos evadir la pregunta, así que aquí están nuestras respuestas y nuestro razonamiento.

---

## Las lenguas de signos son idiomas. Punto final.

Las lenguas de signos son idiomas naturales — con gramáticas completas, adquisición nativa por niños, y comunidades de hablantes vivos. Esto ha sido establecido en la lingüística desde la demostración de William Stokoe en 1960 de que la Lengua de Signos Americana tiene el mismo tipo de estructura interna que los idiomas hablados, y sesenta años de investigación desde entonces (Klima & Bellugi 1979; Sandler & Lillo-Martin 2006) solo han profundizado el punto. ISO 639-3 asigna códigos de idioma individuales a las lenguas de signos; Glottolog las cataloga junto con familias habladas. Nuestro catálogo incluye más de 160 de ellas, etiquetadas `modality: signed`.

Algunas son idiomas indígenas en peligro: la Lengua de Signos de las Llanuras Indias (`psd`), históricamente una importante lingua franca intertribal en América del Norte, está críticamente en peligro hoy (Davis 2010, *Hand Talk*). El peligro de extinción de lenguas de signos *es* peligro de extinción de idiomas indígenas, y está dentro de la misión de este proyecto.

**Una nota de alcance honesta.** La Arena actualmente evalúa traducción automática *basada en texto*. La TA de lenguas de signos — trabajando con video, gramática espacial, e idiomas que no tienen una forma escrita ampliamente adoptada — es un problema técnico diferente y en gran medida sin resolver (ver Yin et al. 2021, "Including Signed Languages in Natural Language Processing," ACL). Aún no lo servimos. Las entradas de lenguas de signos en nuestro catálogo dicen exactamente eso: **aún no servido — nunca "no es un idioma."**

## Hay dos modalidades. La escritura no es una de ellas.

Los idiomas vienen en dos modalidades primarias: **hablada** y **signada**. La escritura no es una tercera modalidad — es una tecnología superpuesta sobre un idioma, y la mayoría de los idiomas del mundo se arreglan sin una estandarizada. Por eso nuestras tarjetas de idioma rastrean la escritura por separado (qué sistemas de escritura usa un idioma, o si no tiene ortografía estandarizada) y la rastrean honestamente: para una plataforma de TA basada en texto, si un idioma está escrito es información crítica, no una nota al pie — y un idioma no escrito no es un idioma menor.

## Lenguas construidas: sí. Lenguajes de programación: no.

Seguimos la propia línea de ISO 639-3. El estándar admite una lengua construida solo si es un idioma completo, diseñado para comunicación humana, con una literatura y una comunidad que la ha transmitido a una segunda generación de usuarios — y explícitamente excluye lenguajes de programación de computadora. El Esperanto, con sus hablantes nativos, califica; Python no, porque nadie adquiere Python como primer idioma de sus padres. Nuestro catálogo incluye las dos docenas de lenguas construidas que ISO reconoce, tipificadas como tales, y ningún lenguaje de programación.

## Evaluamos idiomas individuales, no macrolenguajes

ISO 639-3 distingue *idiomas individuales* de *macrolenguajes* — códigos paraguas como `cre` (Cree), `ara` (Árabe), o `zho` (Chino) que cubren varios idiomas individuales estrechamente relacionados. La unidad de evaluación de la Arena es el **idioma individual**, por una razón operacional: los recursos de traducción son específicos de la variedad. Un analizador morfológico construido para Cree de las Llanuras (`crk`) no genera Cree de Moose (`crm`); un corpus de árabe egipcio dice poco sobre la calidad de un método en árabe marroquí. Una puntuación adjunta a un código de macrolenguaje sería una afirmación sobre variedades que nunca fueron realmente evaluadas — así que no lo hacemos.

Los macrolenguajes aún aparecen en el catálogo como **páginas hub**: navegación que vincula una identidad paraguas a sus miembros individuales, reflejando la propia observación de ISO de que ambos niveles de identidad son reales. Debajo del idioma individual, mostramos información de dialecto y linaje del árbol languoid de Glottolog (Hammarström & Forkel 2022), que modela familias, idiomas y dialectos como una jerarquía navegable.

## Cuando las autoridades no están de acuerdo, mostramos ambas

ISO 639-3 y Glottolog ocasionalmente dividen o agrupan diferente, y las comunidades a veces no están de acuerdo con ambas. No arbitramos. Las tarjetas de idioma llevan una affordance de *notas de taxonomía* que muestra el desacuerdo con fuentes, y la nomenclatura sigue a la comunidad dondequiera que la comunidad haya expresado una preferencia. Si una variedad es "un idioma" es, en última instancia, parcialmente una cuestión de identidad — y las preguntas de identidad pertenecen a las comunidades mismas, un principio que adoptamos de marcos de gobernanza de datos indígenas como OCAP®.

## Una dirección de investigación: evaluaciones como instrumento de medición

Una cosa que una arena como esta produce, casi como un subproducto, es un nuevo tipo de evidencia sobre qué tan cerca están realmente las variedades de idiomas *operacionalmente*. Si un único método de traducción, mantenido fijo, sirve varias variedades relacionadas con calidad desplegable, esas variedades se agrupan en la práctica; si demandan corpus separados y métodos separados, son operacionalmente distintas — sin importar lo que diga la política de nomenclatura. Esto se asemeja a tradiciones empíricas más antiguas, desde pruebas de inteligibilidad de texto grabado hasta medidas de distancia léxica automatizadas, con un giro fundamentado en despliegue.

Ofrecemos esto cuidadosamente, como una dirección de investigación en lugar de una afirmación. Los resultados de transferencia de métodos están confundidos por tamaño de corpus, dominio, ortografía y contaminación de datos de entrenamiento, y una agrupación siempre es relativa a un método y un umbral de calidad. Sobre todo: esta señal puede *informar* conversaciones sobre idioma y dialecto, pero nunca anula cómo una comunidad identifica su propio idioma.

---

## Referencias

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