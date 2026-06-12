---
sidebar_position: 5
title: "Apoyar un idioma con pocos recursos"
related:
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "The first step for an uncovered language"
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
  - label: "Plains Cree, the trading card"
    to: https://champollion.dev/trading-cards?q=crk
    kind: card
    note: "The proof-of-concept language, as a card"
---
# Apoyar un idioma de recursos limitados

> **Resumen ejecutivo.** Una guía completa para construir traducción automática para idiomas de recursos limitados y polisintéticos. Cubre por qué estos idiomas son difíciles (complejidad morfológica, datos escasos, alucinación), recursos computacionales existentes (ALTLab FST, GiellaLT, Apertium, UniMorph, EdTeKLA), más de 10 estrategias de enfoque, el sistema de coaching de champollion y el ciclo de evaluación. Comience aquí si desea contribuir un método para un idioma desatendido.

:::info Estado: En desarrollo activo
El soporte para Plains Cree (nêhiyawêwin) está actualmente en desarrollo. Las herramientas, el arnés de evaluación y el leaderboard descritos aquí son reales y utilizables hoy, pero el pipeline de traducción de Cree aún no ha sido lanzado. Cuando lo sea, esto servirá como el modelo para otros idiomas polisintéticos y de recursos limitados con infraestructura FST.
:::

## El problema sin resolver

Google Translate admite ~130 idiomas. OMT-1600 de Meta (marzo de 2026) afirma cobertura para 1.600 — el sistema de MT más grande jamás publicado. Pero para los ~1.300 idiomas en sus niveles de recursos más bajos, la calidad está por debajo de umbrales utilizables, los datos de entrenamiento están dominados por texto bíblico, los pesos del modelo no están disponibles para descargar, y no hay evaluación independiente ni marco de gobernanza comunitaria. Para los ~5.400 idiomas restantes, ningún modelo preentrenado produce ningún resultado.

El panorama ha cambiado significativamente — Big Tech ahora está invirtiendo en cobertura de idiomas de recursos limitados. Pero la cobertura no es calidad, y la calidad sin verificación independiente no es confianza. Los idiomas de recursos limitados necesitan más que un modelo que afirme cubrirlos — necesitan evaluación independiente con validación morfológica, corpus curados por la comunidad y gobernanza que respete la soberanía.

**champollion fue construido para cambiar eso.**

El [Leaderboard de métodos](https://champollion.dev/leaderboard) es un desafío abierto: construya el mejor método de traducción para un idioma desatendido, pruébelo con evaluación reproducible y reclame la puntuación superior. Cualquiera en el mundo puede contribuir — lingüistas, investigadores de ML, trabajadores de idiomas comunitarios, estudiantes, aficionados. El problema no está resuelto. La infraestructura está aquí. El leaderboard está esperando.

---

## Por qué esto es difícil: Morfología polisintética

La mayoría de los sistemas de MT comerciales fueron diseñados para idiomas como inglés, francés y chino — idiomas donde las palabras son relativamente cortas y las oraciones se construyen a partir de tokens discretos. Pero muchos idiomas indígenas, incluido Plains Cree, son **polisintéticos**: una sola palabra puede codificar lo que el inglés expresa como una oración completa.

### El ejemplo de Cree

Considere la palabra de Plains Cree:

> **ê-kî-nitawi-kîskinwahamâkosiyân**
> *"cuando fui a la escuela"*

Esa es **una palabra**. Codifica tiempo (pasado), dirección (ir a), la raíz (aprender), voz (pasiva/reflexiva) y persona (primera singular). Un LLM entrenado predominantemente en inglés no tiene intuición para este tipo de densidad morfológica.

Los desafíos se multiplican:

| Desafío | Qué significa |
|---------|---------------|
| **Complejidad morfológica** | Una sola raíz verbal puede generar miles de formas inflexionadas válidas a través de prefijación, sufijación y circunfijación |
| **Distinción animado/inanimado** | Los sustantivos son gramaticalmente animados o inanimados — esto afecta la conjugación verbal, demostrativos y pluralización. La clasificación no siempre sigue la animacidad biológica (*askiy* "tierra" es animado; *maskisin* "zapato" también es animado) |
| **Obviación** | Las referencias de tercera persona se clasifican por proximidad/relevancia. La distinción "proximal" y "obviativo" no tiene equivalente en inglés |
| **Datos de entrenamiento escasos** | Los LLM han visto muy poco texto de Plains Cree. Lo que han visto puede mezclar dialectos (dialecto Y, dialecto TH) u ortografías (SRO vs. silábicos) |
| **Línea base comercial débil** | OMT-1600 incluye CRK en el nivel R1 (Recursos muy limitados) con entrenamiento en dominio bíblico y tokenización BPE estándar. Google Translate no admite Cree. La evaluación independiente con métricas morfológicas es lo que hace que estas líneas base sean significativas. |

La traducción de idiomas polisintéticos sigue siendo un **problema de investigación abierto** — OMT-1600 incluye idiomas polisintéticos pero utiliza tokenización BPE estándar (vocabulario de 256K) sin conciencia morfológica, lo que significa que destruye palabras composicionales en fragmentos de bytes sin sentido.

---

## Trabajo previo: Cómo las personas han abordado esto

### El FST de ALTLab

El recurso computacional más significativo para Plains Cree es el **transductor de estado finito (FST)** desarrollado por el [Alberta Language Technology Lab (ALTLab)](https://altlab.artsrn.ualberta.ca/) en la Universidad de Alberta, en colaboración con [Giellatekno](https://giellatekno.uit.no/) en UiT The Arctic University of Norway.

El FST de ALTLab es un **analizador y generador morfológico**: dada una palabra Cree inflexionada, puede descomponerla en su raíz y etiquetas gramaticales, y dada una raíz más etiquetas, puede generar la forma inflexionada correcta. Esto es determinista — sin red neuronal, sin alucinación, sin probabilidad. Si el FST acepta una palabra, esa palabra es morfológicamente válida en Cree.

Por eso el leaderboard de champollion rastrea la **Tasa de aceptación de FST** como métrica. Un método de traducción que produce palabras que el FST rechaza está produciendo Cree morfológicamente inválido — independientemente de lo que diga la puntuación de chrF++.

**Recursos clave de ALTLab:**
- [itwêwina](https://itwewina.altlab.app/) — un diccionario inteligente de Plains Cree–inglés impulsado por el FST
- [Morphodict](https://github.com/UAlbertaALTLab/morphodict) — plataforma de diccionario de código abierto consciente de la morfología
- [crk-db](https://github.com/UAlbertaALTLab/crk-db) — base de datos léxica de Plains Cree
- [21st Century Tools for Indigenous Languages](https://21c.tools/) — el contexto del proyecto más amplio

### Registros globales de FST y morfología

Plains Cree no es el único idioma con infraestructura FST de alta calidad. Si desea desarrollar pipelines de traducción para otros idiomas de recursos limitados o morfológicamente complejos, puede aprovechar estos centros globales establecidos:

* **[GiellaLT / Giellatekno](https://giellalt.github.io/) (UiT The Arctic University of Norway):** El repositorio más grande de analizadores y generadores morfológicos FST de código abierto, cubriendo más de 100 idiomas. Las áreas de enfoque incluyen idiomas Sámi (`sme`, `smj`, `sma`, etc.), idiomas urálicos (Komi, Erzya, Udmurt, etc.) y otros idiomas minoritarios/indígenas. Albergan corpus de texto procesado público (`corpus-xxx`) en su [Organización de GitHub](https://github.com/giellalt/).
* **[El Proyecto Apertium](https://www.apertium.org/):** Una plataforma de traducción automática basada en reglas de código abierto. Apertium mantiene analizadores morfológicos FST altamente optimizados (usando `lttoolbox` y `hfst`) y diccionarios bilingües para docenas de idiomas, incluido un conjunto grande de idiomas túrquicos (kazajo, tártaro, kirguís, etc.) e idiomas europeos minoritarios. Todos los recursos son públicos en [GitHub de Apertium](https://github.com/apertium).
* **[UniMorph (Morfología Universal)](https://unimorph.github.io/):** Un proyecto colaborativo que proporciona paradigmas morfológicos estandarizados para más de 150 idiomas. El conjunto de datos se aloja en Hugging Face en [unimorph/universal_morphologies](https://huggingface.co/datasets/unimorph/universal_morphologies). Si un binario FST compilado no está disponible para un idioma, las tablas de UniMorph se pueden usar como una puerta de búsqueda de base de datos estática.
* **[Consejo Nacional de Investigación de Canadá (NRC)](https://nrc-digital-repository.canada.ca/):** Ofrece herramientas para idiomas indígenas canadienses, incluido el analizador morfológico FST **Uqailaut** Inuktitut y el masivo **Corpus paralelo de Hansard de Nunavut** (1,3M pares de oraciones alineadas inglés-inuktitut).

### El corpus EdTeKLA

El [grupo de investigación EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) (también en UAlberta) ha reunido un corpus de idioma Plains Cree a partir de materiales educativos, transcripciones de audio y fuentes comunitarias. El conjunto de datos de evaluación de champollion [EDTeKLA Dev v1](/docs/leaderboard/datasets) se deriva de este trabajo, licenciado bajo [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

### Otros enfoques que las personas han probado o podrían probar

El leaderboard es agnóstico respecto al método. Aquí hay estrategias que se han explorado o propuesto para MT de recursos limitados, cualquiera de las cuales podría ser enviada:

| Enfoque | Cómo funciona | Ventajas | Desventajas |
|---------|--------------|----------|-------------|
| **[Prompting de LLM entrenado](/docs/tutorials/coached-llm-prompting)** | Inyecte reglas gramaticales, diccionarios y pares de ejemplo en el prompt del sistema | Rápido de iterar, no se necesita entrenamiento | El techo de calidad está limitado por el conocimiento base del LLM |
| **[Prompting de pocos ejemplos](/docs/tutorials/few-shot-prompting)** | Incluya traducciones verificadas como ejemplos en contexto | Bueno para estilo consistente | Ventana de contexto pequeña; los ejemplos NO deben provenir de datos de evaluación |
| **[Pipeline con puerta FST](/docs/tutorials/fst-gated-pipeline)** | LLM genera → FST valida → rechaza y reintenta morfología inválida | Garantiza validez morfológica | Requiere infraestructura FST; los bucles de reintento agregan latencia y costo |
| **[Búsqueda en diccionario + LLM](/docs/tutorials/dictionary-augmented-llm)** | Force términos conocidos de un diccionario bilingüe, deje que el LLM maneje el resto | Reduce alucinación para términos conocidos | La cobertura del diccionario siempre es incompleta |
| **[Modelo ajustado](/docs/tutorials/fine-tuned-model)** | Ajuste un modelo abierto (Llama, Mistral) en texto paralelo — solo no en los datos de evaluación | Potencialmente la más alta calidad | Requiere corpus paralelo (escaso); costoso; riesgo de sobreajuste |
| **[Modelos encadenados](/docs/tutorials/chained-models)** | El modelo A genera traducción aproximada → El modelo B post-edita → El modelo C califica | Puede combinar fortalezas especializadas | Complejo; lento; costoso |
| **[Híbrido basado en reglas + LLM](/docs/tutorials/rule-based-hybrid)** | Use reglas lingüísticas para patrones conocidos, LLM para todo lo demás | Preciso donde se aplican las reglas | Requiere experiencia lingüística profunda |
| **[Aumento de back-translation](/docs/tutorials/back-translation)** | Genere datos paralelos sintéticos traduciendo Cree→inglés, luego entrene en la inversa | Expande datos de entrenamiento económicamente | Amplifica errores del modelo existente |
| **[Enfoque evolutivo](/docs/tutorials/evolutionary-approach)** | Genere traducciones candidatas, califíquelas, mute los mejores desempeños, repita | Puede descubrir soluciones novedosas; paralelizable | Computacionalmente costoso; necesita una buena función de aptitud |
| **[Traducción parcial](/docs/tutorials/partial-translation)** | Traduzca manualmente una muestra representativa, pruebe que su método coincida con su estilo en ella, luego traduzca automáticamente el volumen restante | Combina calidad humana con escala de máquina | Requiere esfuerzo humano inicial |
| **JSON manual / calificación de examen** | Construya manualmente un archivo JSON de conjunto de datos para probar respuestas de estudiantes en un examen de idioma, o califique un lote de traducciones humanas contra un estándar de oro | Cero ML requerido; funciona para educación y QA | No se escala a necesidades de traducción continua |

### Es solo JSON

El arnés toma JSON como entrada y produce JSON como salida. El [formato del conjunto de datos](/docs/leaderboard/datasets) es simple:

```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

Puede construir esto a mano. Puede exportarlo desde una hoja de cálculo. Puede generarlo a partir de un corpus. Un maestro de idiomas podría usarlo para calificar traducciones de estudiantes. Una agencia de traducción podría usarlo para comparar freelancers. Un laboratorio de investigación podría usarlo para comparar arquitecturas de modelos. El arnés no le importa de dónde vino el JSON — simplemente lo califica.

Y debido a que el marco de implementación de producción toma la misma interfaz de complemento, un método que se desempeña bien en el arnés se implementa en su sitio web con un cambio de configuración. **Pruébelo y úselo.**

Las posibilidades son genuinamente infinitas. **Si tiene una idea, constrúyala, ejecute el arnés y envíe sus puntuaciones.**

---

## Cómo champollion encaja

champollion proporciona la capa de infraestructura — usted aporta el método.

### El sistema de coaching

El método `llm-coached` de champollion le permite inyectar conocimiento lingüístico directamente en el prompt del LLM:

```json title=".champollion/coaching/crk.json"
{
  "grammar_rules": [
    "Plains Cree is polysynthetic — a single word can express what English needs a full sentence for",
    "Animate/inanimate noun distinction affects verb conjugation, demonstratives, and pluralization",
    "Use SRO (Standard Roman Orthography) as the working script — syllabic conversion is handled by the deterministic converter",
    "Obviation: when two third-person referents appear, the less salient one takes obviative marking (-a suffix on nouns, -iyiwa on verbs)"
  ],
  "dictionary": {
    "home": "kīwēwin",
    "settings": "isi-nākatohkēwin",
    "search": "nānātawāpahtam",
    "welcome": "tānisi",
    "dashboard": "kīskinwahamākēwin-māsinahikan"
  },
  "style_notes": "Use formal register appropriate for educational and community contexts. Preserve English technical terms in parentheses when no Cree equivalent exists or is widely accepted."
}
```

Los datos de coaching se inyectan en cada prompt del LLM para el par `en:crk`, dando al modelo contexto lingüístico estructurado que de otro modo no tendría. Vea [Datos de coaching](https://champollion.dev/docs/concepts/coaching-data) para la especificación completa.

### Registros

El registro es parte del prompt del sistema que dirige el tono, la formalidad y las convenciones ortográficas. champollion viene con un registro de Plains Cree:

```
nêhiyawêwin (Plains Cree). Use SRO (Standard Roman Orthography) as the working
script. Output will be converted to Syllabics via deterministic converter.
Professional register appropriate for educational and community contexts.
```

Puede anular esto en su configuración para experimentar con diferentes estrategias de prompting:

```json title="champollion.config.json"
{
  "languages": {
    "crk": {
      "register": "Casual Plains Cree (Y-dialect). Use SRO. Prefer everyday vocabulary over formal or archaic terms. Address the reader directly."
    }
  }
}
```

Los registros diferentes producen estilos de traducción diferentes — y puntuaciones diferentes en el leaderboard. Cada envío registra el registro exacto y el prompt del sistema utilizado (como un hash SHA-256 en la [tarjeta de ejecución](/docs/specifications/run-card)), por lo que los experimentos son reproducibles.

### Conversión de escritura

Plains Cree se escribe en dos escrituras: **Ortografía romana estándar (SRO)** y **Silábicos aborígenes canadienses**. El pipeline de champollion:

1. LLM traduce a SRO (basado en latín, que los LLM manejan mejor)
2. La puerta de calidad valida la salida de SRO
3. El convertidor determinista transforma SRO → Silábicos
4. El texto convertido se escribe en disco

El convertidor maneja todos los diacríticos de SRO (ê, î, ô, â para vocales largas) y los asigna a los caracteres silábicos correctos. Vea [Convertidores de escritura](https://champollion.dev/docs/concepts/script-converters) para detalles técnicos.

### El ciclo de evaluación

El [arnés de evaluación](/docs/specifications/harness) ejecuta su método contra el conjunto de datos de evaluación y produce una [tarjeta de ejecución](/docs/specifications/run-card) calificada:

```bash
# Clone the harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install -e .

# Run a baseline experiment
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --model google/gemini-2.5-pro \
  --condition coached-v7

# Run with FST validation (if you have an FST binary)
python eval/baseline_experiment.py \
  --dataset data/edtekla-dev-v1.json \
  --fst-analyzer ./bin/crk-analyzer \
  --condition fst-gated-v1
```

La bandera `--condition` es una etiqueta que usted elige. Aparece en el leaderboard para que las personas puedan ver qué estrategia de prompt utilizó. El arnés registra el prompt del sistema completo en la tarjeta de ejecución, por lo que su enfoque exacto es reproducible.

:::tip Experimente libremente, envíe lo mejor
El arnés está diseñado para iteración rápida. Ejecute docenas de experimentos con diferentes modelos, datos de coaching, registros y condiciones. Solo envíe al leaderboard cuando tenga algo de lo que esté orgulloso.
:::

---

## Principios OCAP

champollion está diseñado para apoyar la soberanía de datos indígenas. Los [principios OCAP](https://fnigc.ca/ocap-training/) (Propiedad, Control, Acceso, Posesión) guían cómo abordamos la tecnología de idiomas para comunidades indígenas:

| Principio | Cómo champollion lo apoya |
|-----------|--------------------------|
| **Propiedad** | Las comunidades de idiomas poseen sus datos lingüísticos. champollion nunca se comunica con el hogar ni transmite datos a nuestros servidores |
| **Control** | El [método de API](https://champollion.dev/docs/guides/serving-a-method) permite que las comunidades alberguen su propio pipeline de traducción — proporcionamos la interfaz, ellos controlan la implementación |
| **Acceso** | Las comunidades deciden quién puede usar su método. La API puede estar protegida detrás de autenticación |
| **Posesión** | Todos los datos de traducción permanecen en el sistema de archivos de su proyecto. El [sistema de procedencia](https://champollion.dev/docs/concepts/security) rastrea de dónde vino cada traducción |

La arquitectura de complementos significa que una comunidad puede construir un método que incorpore conocimiento sagrado o restringido internamente, exponer solo la API de traducción y mantener control total sobre sus recursos lingüísticos.

---

## La visión: Qué viene después

Plains Cree es el primer objetivo. Una vez que el pipeline sea validado y la comunidad esté satisfecha con la calidad, la misma arquitectura se extiende a otros idiomas polisintéticos con infraestructura FST:

- **Otros idiomas algonquianos**: Woods Cree, Swampy Cree, Ojibwe, Blackfoot
- **Idiomas inuit**: Inuktitut, Inuinnaqtun (que también usan escrituras silábicas)
- **Otras familias de idiomas**: cualquier idioma con un analizador FST puede usar el pipeline con puerta FST

El leaderboard tiene alcance de par de idiomas. A medida que nuevos conjuntos de datos de evaluación son contribuidos por comunidades de idiomas, nuevas pistas de leaderboard se abren automáticamente.

**Esta es una invitación abierta.** Si trabaja con un idioma de recursos limitados — como investigador, miembro de la comunidad, estudiante o simplemente alguien que se preocupa — champollion le proporciona las herramientas para construir algo real, medirlo honestamente y compartirlo con el mundo. El [Leaderboard de métodos](https://champollion.dev/leaderboard) está esperando su envío.

---

## Véase también

- **[Leaderboard de métodos](https://champollion.dev/leaderboard)** — envíe sus puntuaciones y vea cómo se comparan los métodos
- **[Evaluación de MT](/docs/leaderboard/rules)** — qué hace un buen método, qué se descalifica
- **[Arnés de evaluación](/docs/specifications/harness)** — cómo ejecutar experimentos
- **[Conjuntos de datos de evaluación](/docs/leaderboard/datasets)** — EDTeKLA Dev v1 y FLORES+
- **[Datos de coaching](https://champollion.dev/docs/concepts/coaching-data)** — cómo estructurar conocimiento lingüístico para el LLM
- **[Convertidores de escritura](https://champollion.dev/docs/concepts/script-converters)** — el pipeline SRO→Silábicos
- **[Servir un método vía API](https://champollion.dev/docs/guides/serving-a-method)** — alojamiento de traducción controlada por la comunidad
- **[ALTLab](https://altlab.artsrn.ualberta.ca/)** — el Alberta Language Technology Lab
- **[EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/)** — el grupo de investigación Educational Technology, Knowledge & Language
- **[Diccionario itwêwina](https://itwewina.altlab.app/)** — diccionario de Plains Cree–inglés impulsado por FST