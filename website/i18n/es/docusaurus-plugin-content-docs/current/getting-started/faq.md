---
sidebar_position: 2
title: "Preguntas frecuentes"
related:
  - label: "How It Works"
    to: /docs/how-it-works
    kind: doc
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Glossary"
    to: https://champollion.dev/glossary
    kind: glossary
    note: "Plain-language definitions for every technical term"
---
# Preguntas Frecuentes

> **Resumen Ejecutivo.** Respuestas a preguntas comunes sobre MT Eval Arena — cómo funciona la puntuación, qué se descalifica, cómo manejar idiomas sin FST, recomendaciones de modelos y parámetros, y el proceso de envío.

---

## Puntuación y Métricas

### ¿Qué métricas calcula el harness?

El harness calcula cinco métricas para Cree de las Llanuras (el idioma de referencia actual). Tres son agnósticas del idioma y funcionarán para cualquier idioma; dos actualmente dependen de complementos específicos de CRK y se generalizarán a medida que nos expandamos a más idiomas.

| Métrica | Escala | Qué Mide | Estado |
|---------|--------|---------|--------|
| **chrF++** | 0–100 | Superposición de n-gramas de caracteres entre traducciones predichas y de referencia. Mejor métrica de superficie para idiomas morfológicamente ricos. Utiliza la puntuación nativa de sacrebleu. | ✅ Todos los idiomas |
| **Coincidencia exacta** | 0.0–1.0 | Proporción de entradas donde la predicción coincide exactamente con la referencia después de la normalización. | ✅ Todos los idiomas |
| **Aceptación FST** | 0.0–1.0 | Proporción de palabras de salida aceptadas por un transductor de estados finitos (analizador morfológico). Solo se calcula cuando se proporciona un binario FST. | ✅ Todos los idiomas con FST |
| **Coincidencia equivalente** | 0.0–1.0 | Fracción de entradas que coinciden con la referencia o una variante aceptable — considerando orden de palabras, convención ortográfica y diferencias dialectales. | ⚡ CRK (generalizando) |
| **Puntuación semántica** | 0.0–1.0 | Puntuación de preservación de significado — ¿qué tan bien captura la traducción el significado previsto independientemente de la forma de superficie? | ⚡ CRK (generalizando) |

Se planean métricas adicionales: **precisión morfológica**, **detección de code-switching**, **adherencia a terminología** y **detección de alucinaciones**. Consulte [Especificación de Puntuación §2](/docs/specifications/scoring#2-metric-inventory) para el inventario completo de 19 métricas.

### ¿Cómo se calcula la puntuación compuesta?

La puntuación compuesta es un promedio ponderado de métricas disponibles, normalizado a una escala 0.0–1.0. Los pesos se definen en dos perfiles:

- **Perfil A** (idiomas con FST): 9 métricas, las métricas estructurales (FST + precisión morfológica) representan el 40% del peso compuesto
- **Perfil B** (idiomas sin FST): 8 métricas, semántica y chrF++ tienen igual peso superior

Cuando una métrica no está disponible, su peso se redistribuye proporcionalmente entre las métricas restantes. Esto significa que los puntos de referencia en etapa inicial (con solo chrF++ y coincidencia exacta disponibles) aún producen compuestos válidos — los pesos efectivos simplemente reflejan lo que está disponible.

**Las tablas de peso completas, reglas de normalización y justificación de exclusión están en [Especificación de Puntuación §4](/docs/specifications/scoring#4-composite-score).** El código del harness refleja estas tablas en `mt_eval_harness/scoring.py`. chrF++ se normaliza dividiendo por 100 antes de ponderarse; las tasas de code-switching y alucinaciones se invierten (menor = mejor).

### ¿Qué son los niveles de calidad?

Los niveles de calidad son etiquetas heurísticas asignadas a rangos de puntuación compuesta. Ayudan a comunicar qué significa una puntuación *prácticamente*:

| Nivel | Rango Compuesto | Interpretación |
|-------|-----------------|----------------|
| **Línea Base** | 0.00 – 0.30 | Por debajo de calidad útil. El método necesita mejora significativa. |
| **Emergente** | 0.30 – 0.50 | Muestra promesa. Algunas traducciones son correctas pero inconsistentes. |
| **Funcional** | 0.50 – 0.70 | Utilizable como referencia con revisión humana. No apto para despliegue sin revisar. |
| **Desplegable** | 0.70 – 0.85 | Listo para uso en producción con revisión periódica. Activa elegibilidad de transferencia de propiedad. |
| **Fluido** | 0.85 – 1.00 | Calidad casi nativa. Apto para despliegue sin supervisión. |

### ¿Cuál es la diferencia entre niveles de calidad y niveles de verificación?

**Los niveles de calidad** describen *qué significa la puntuación automatizada* (Línea Base → Fluido). **Los niveles de verificación** describen *quién validó el resultado*:

| Nivel de Verificación | Qué Significa |
|----------------------|---------------|
| **Auto-evaluado** | El remitente ejecutó el harness por sí mismo. Las puntuaciones son plausibles pero no verificadas. |
| **Verificado por GDS** | Un mantenedor reprodujo el resultado utilizando la configuración del método enviado. |
| **Validado por la Comunidad** | Hablantes bilingües revisaron las traducciones y confirmaron la calidad. |

Un método puede ser calidad "Desplegable" pero solo verificación "Auto-evaluado" — lo que significa que la puntuación se ve excelente pero nadie la ha confirmado independientemente.

---

## Envío y Descalificación

### ¿Qué hace que mi envío sea descalificado?

Su envío será rechazado o marcado si:

1. **Su método fue expuesto a datos de evaluación.** Si entrenó, ajustó, indicó con pocos ejemplos u otro uso de cualquier entrada del conjunto de datos de evaluación, sus puntuaciones están artificialmente infladas. Esto incluye usar las traducciones de referencia en su indicación.
2. **Su tarjeta de ejecución falla las verificaciones de integridad.** La huella digital debe coincidir con la configuración. Las tarjetas de ejecución alteradas se rechazan.
3. **Su método no implementa el protocolo TranslationMethod.** El harness espera `translate(entries, config) → results`. Las integraciones personalizadas que evitan el harness no se aceptan.

### ¿Puedo enviar múltiples veces?

Sí. El leaderboard rastrea todos los envíos. Puede iterar — ejecutar docenas de experimentos, enviar solo el mejor. Cada envío registra una huella digital única, por lo que no hay ambigüedad sobre qué ejecución produjo qué puntuación.

### ¿Cómo obtengo mi puntuación verificada?

1. **Auto-evaluado (automático):** Cada envío comienza aquí.
2. **Verificado por GDS:** Envíe su método como un paquete reproducible (código + configuración + datos de coaching). Un mantenedor lo ejecutará nuevamente contra el mismo conjunto de datos y confirmará que las puntuaciones coincidan.
3. **Validado por la Comunidad:** Para idiomas indígenas, esto requiere que hablantes bilingües revisen una muestra de traducciones. Esto no puede automatizarse — requiere participación comunitaria.

### ¿Está activa la API de envío?

Aún no. El punto final `https://mtevalarena.org/api/leaderboard/submit` es aspiracional. Los envíos actuales deben realizarse mediante solicitud de extracción al [repositorio del harness de evaluación](https://github.com/gamedaysuits/arena) con su JSON de tarjeta de ejecución en el directorio `results/`.

---

## Modelos y Parámetros

### ¿Qué modelo debo usar?

No hay un único mejor modelo — depende del par de idiomas, su presupuesto y su enfoque. Orientación general:

| Tipo de Idioma | Punto de Partida Recomendado | Por Qué |
|----------------|------------------------------|--------|
| **Alto recurso** (Francés, Español, Japonés) | `google/gemini-2.5-flash` o `gpt-4o-mini` | Rápido, económico, línea base sólida |
| **Bajo recurso con cobertura LLM** (Quechua, Yoruba) | `google/gemini-2.5-pro` o `anthropic/claude-sonnet-4` | Los modelos más grandes tienen mejor conocimiento latente |
| **Polisintético / muy bajo recurso** (Cree de las Llanuras, Inuktitut) | `google/gemini-2.5-pro` con coaching | Los datos de coaching importan más que la elección del modelo. OMT-1600 incluye algunos idiomas polisintéticos (p. ej., CRK en nivel R1) pero con tokenización BPE estándar — evalúelo como línea base en la Arena. |

El harness de evaluación utiliza OpenRouter, por lo que cualquier modelo disponible en OpenRouter puede ser evaluado. Ejecute `champollion models --method llm` para ver los modelos disponibles.

### ¿Qué temperatura debo usar?

Generalmente, menor es mejor para traducción:

| Temperatura | Efecto | Recomendado Para |
|-------------|--------|-----------------|
| **0.0 – 0.2** | Salida altamente determinista y consistente | Métodos de producción, evaluaciones finales |
| **0.3 – 0.5** | Alguna variación, ocasionalmente más creativo | Exploración, iteración temprana |
| **0.6+** | Alta variación, impredecible | No recomendado para evaluación de MT |

La temperatura se registra en la tarjeta de ejecución, por lo que diferentes temperaturas producen diferentes huellas digitales — se tratan como experimentos diferentes.

### ¿Ayudan los datos de coaching?

Sí, significativamente — para idiomas de bajo recurso. Los datos de coaching (reglas gramaticales, entradas de diccionario, notas de estilo) se inyectan en el indicador del sistema del LLM. Para Cree de las Llanuras, los métodos con coaching superan consistentemente a los métodos LLM sin procesar para idiomas polisintéticos porque los LLM de propósito general tienen exposición limitada a polisintéticos y sin conciencia morfológica. Incluso OMT-1600, que fue entrenado específicamente para CRK, utiliza tokenización BPE estándar que no puede representar la morfología polisintética estructuralmente. Los datos de coaching proporcionan el contexto lingüístico que el modelo carece.

Para idiomas de alto recurso (Francés, Español), el coaching tiene menos impacto porque el modelo ya tiene conocimiento de línea base sólido.

Consulte [Datos de Coaching](https://champollion.dev/docs/concepts/coaching-data) para la especificación completa.

---

## FST y Validación Morfológica

### ¿Qué pasa si no hay FST para mi idioma?

Muchos idiomas no tienen un transductor de estados finitos. Está bien — el harness funciona sin uno. La puntuación compuesta utiliza pesos del Perfil B (consulte [Especificación de Puntuación §4.3](/docs/specifications/scoring#43-weight-tables)) que desplazan el peso a métricas semánticas y de superficie. La aceptación FST se marca como `null` en la tarjeta de ejecución.

Los registros principales para FST existentes:

| Registro | Cobertura | URL |
|----------|-----------|-----|
| **GiellaLT** | Sámi, Cree, Inuktitut y otros idiomas árticos/subarticos | [giellalt.uit.no](https://giellalt.uit.no/) |
| **ALTLab** | Cree de las Llanuras, Cree de los Bosques, Ojibwe | [altlab.artsrn.ualberta.ca](https://altlab.artsrn.ualberta.ca/) |
| **Apertium** | ~60 pares de idiomas, principalmente europeos | [apertium.org](https://apertium.org/) |
| **UniMorph** | Paradigmas morfológicos para 150+ idiomas | [unimorph.github.io](https://unimorph.github.io/) |

### ¿Puedo construir un FST?

Sí, pero no es trivial. Un FST codifica las reglas morfológicas de un idioma — todas las formas de palabras válidas. Construir uno requiere conocimiento lingüístico profundo del idioma. Si tiene acceso a una gramática morfológica (p. ej., de un departamento de lingüística), puede compilarse en un FST utilizando herramientas como [HFST](https://hfst.github.io/) o [Foma](https://fomafst.github.io/).

### ¿Cómo funciona el gating FST en la práctica?

El pipeline con gating FST funciona así:

1. El LLM genera una traducción
2. Cada palabra en la salida se verifica contra el FST
3. Las palabras que el FST rechaza se marcan como morfológicamente inválidas
4. El método puede reintentar con retroalimentación ("la palabra X no es válida, intente de nuevo")
5. Después de reintentos, las palabras inválidas restantes se registran

La tasa de aceptación FST mide cuántas palabras pasan la validación. Consulte el [Tutorial de Pipeline con Gating FST](/docs/tutorials/fst-gated-pipeline) para un ejemplo completo trabajado.

---

## Datos y Conjuntos de Datos

### ¿Puedo contribuir un conjunto de datos para un nuevo idioma?

Sí. Requisitos mínimos de [Especificación de Referencia §11](/docs/specifications/benchmark#11-extending-to-new-languages):

- **50 entradas de estándar de oro** (fuente + traducción de referencia verificada)
- **30 entradas de desarrollo** (pueden superponerse con estándar de oro para corpus pequeños)
- **Consentimiento comunitario** (para idiomas indígenas, autorización explícita de un organismo de gobernanza)
- **Documentación de procedencia** (de dónde vinieron los datos, qué licencia se aplica)

Los nuevos conjuntos de datos abren nuevas pistas de leaderboard automáticamente. Consulte [Para Comunidades Lingüísticas](/docs/community/for-language-communities) para la guía del colaborador.

### ¿En qué formato debe estar mi conjunto de datos?

JSON con los nombres de campo canónicos:

```json
{
  "name": "my-language-dev-v1",
  "language_pair": "en-xxx",
  "segment": "development",
  "version": "1.0",
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "[translation in target language]",
      "difficulty": 1,
      "domain": "general"
    }
  ]
}
```

Consulte [Conjuntos de Datos](/docs/leaderboard/datasets) para el esquema completo y definiciones de nivel de dificultad.

---

## Soberanía y Propiedad

### ¿Quién es dueño de un método construido para un idioma indígena?

Para idiomas indígenas, los métodos que alcanzan el nivel Desplegable (compuesto ≥ 0.70) Y pasan la validación comunitaria activan el proceso de [transferencia de propiedad](/docs/sovereignty/ownership-transfer). La propiedad del código se transfiere del investigador a la organización de gobernanza de la comunidad lingüística.

El investigador retiene:
- Derechos de publicación (artículos académicos sobre el método)
- Crédito en el leaderboard
- El derecho de aplicar las mismas *técnicas* a otros idiomas

La organización de gobernanza obtiene:
- Propiedad total del código del método y datos de coaching
- Control sobre el despliegue (cuándo, dónde, cómo)
- Ingresos del uso de API (90% comunidad, 10% infraestructura)

### ¿Puedo usar champollion para idiomas no indígenas sin preocupaciones de soberanía?

Sí. Para idiomas estándar (Francés, Japonés, Español, etc.), no hay consideraciones de soberanía. Use champollion normalmente — traduzca, sincronice, publique como desee. El marco de soberanía se aplica específicamente a idiomas indígenas y gobernados por la comunidad donde los principios de gobernanza de datos (OCAP®, CARE, Te Mana Raraunga) requieren consideración especial.

---

## Véase También

- **[Cómo Funciona](https://champollion.dev/how-it-works)** — el explicador de solución completa
- **[Especificación de Puntuación](/docs/specifications/scoring)** — la SSOT para toda la lógica de puntuación (métricas, pesos, niveles)
- **[Especificación de Referencia](/docs/specifications/benchmark)** — protocolo de evaluación, formato de corpus, soberanía
- **[Enviar un Método](/docs/getting-started/submit-a-method)** — guía de inicio rápido paso a paso
- **[Reglas del Leaderboard](/docs/leaderboard/rules)** — criterios de envío
- **[Soberanía de Datos](/docs/sovereignty/data-sovereignty)** — OCAP®, CARE y obligaciones éticas