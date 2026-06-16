---
sidebar_position: 1
title: "Evaluación de Traducción Automática"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "How the composite score is computed"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Evaluation Datasets"
    to: /docs/leaderboard/datasets
    kind: doc
  - label: "Live Leaderboard"
    to: https://champollion.dev/leaderboard
    kind: leaderboard
    note: "The rules, applied"
---
# Evaluación de MT

> **Resumen Ejecutivo.** Esta página define los criterios de envío al leaderboard, las métricas de puntuación (chrF++, aceptación FST, coincidencia exacta, coincidencia equivalente, puntuación semántica), políticas anti-gaming, niveles de verificación y el flujo de envío. Los métodos que han sido expuestos a datos de evaluación serán descalificados.

champollion incluye un marco de evaluación de traducción automática diseñado para **benchmarking reproducible** de métodos de traducción — especialmente para idiomas de bajo recurso e indígenas donde los benchmarks estándar de MT no existen y las afirmaciones de calidad son difíciles de verificar.

---

## El Leaderboard

La pieza central es el **[Method Leaderboard](https://champollion.dev/leaderboard)** — un marcador en vivo respaldado por Supabase donde investigadores y miembros de la comunidad envían y comparan métodos de traducción con evaluación reproducible y con huella digital.

Cada envío incluye:

- **Pipeline con huella digital** — vinculado a un commit específico de Git y hash de configuración, para que los resultados se remitan al código exacto que los produjo
- **Dataset versionado** — con hash de contenido y versionado; las puntuaciones solo son comparables dentro de la misma versión del dataset
- **Métricas estandarizadas** — toda la puntuación se calcula mediante el arnés de evaluación compartido, eliminando diferencias de implementación
- **Niveles de confianza** — auto-benchmarked, GDS Verified o Community Validated
- **Seguimiento de costos** — costo de API por envío, para que los compromisos costo-calidad sean transparentes

El leaderboard actualmente rastrea cinco métricas. Tres funcionan para cualquier idioma; dos están disponibles para Plains Cree y se generalizarán a medida que expandamos:

| Métrica | Tipo | Qué Mide |
|---------|------|----------|
| **chrF++** | F-score de n-gramas de caracteres | Métrica de calidad primaria — correlaciona bien con el juicio humano, especialmente para idiomas morfológicamente ricos |
| **Exact Match** | Proporción de coincidencias perfectas | Precisión estricta — ¿con qué frecuencia la traducción es exactamente el estándar de oro? |
| **FST Acceptance** | Tasa de paso de puerta morfológica | Para métodos con verificación de transductor de estado finito — ¿qué proporción de salidas son morfológicamente válidas? |
| **Equivalent Match** | Tasa de variante aceptable | Fracción que coincide con la referencia o una variante aceptable (orden de palabras, convención ortográfica). Actualmente CRK; generalizando. |
| **Semantic Score** | Fidelidad semántica | Preservación de significado — ¿la traducción captura el significado previsto independientemente de la forma superficial? Actualmente CRK; generalizando. |

:::info Suite Completa de Métricas
La [Especificación de Puntuación](/docs/specifications/scoring) define el inventario completo de 19 métricas en 5 categorías, fórmula de puntuación compuesta, tablas de pesos y umbrales de nivel de calidad.
:::

**[→ Ver el leaderboard](https://champollion.dev/leaderboard)**

---

## Datasets Disponibles

### EDTeKLA Development Set v1

El primer dataset de evaluación, construido para traducción English→Plains Cree (SRO). Creado por el [grupo de investigación EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) de la Universidad de Alberta.

| Propiedad | Valor |
|-----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Par de idiomas** | EN → CRK (Plains Cree, ortografía SRO) |
| **Cantidad de entradas** | 404 (`master_corpus.json`: 62 oro + 342 libro de texto); 548 total disponibles |
| **Licencia** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |
| **Procedencia** | `gold_standard` (verificado por hablantes), `textbook` (materiales educativos publicados) |

### FLORES+ Devtest — Solo para Desarrollo

> [!WARNING]
> **FLORES+ está disponible para desarrollo y depuración pero NO se utiliza para evaluación oficial del leaderboard.** FLORES+ (originalmente Meta FLORES-200) es un dataset de benchmark ampliamente público que casi con certeza los LLMs fronterizos han sido entrenados con él. Las puntuaciones contra FLORES+ no reflejan de manera confiable la calidad de traducción del mundo real para métodos basados en LLM. Los métodos no-LLM (FST, basados en reglas, NMT fine-tuned) se ven menos afectados pero las puntuaciones de FLORES+ aún no se publican en el leaderboard.

Los fixtures de FLORES+ permanecen disponibles en `test/benchmark/fixtures/` para pruebas de humo del pipeline, validación entre idiomas y uso en desarrollo. La evaluación oficial utiliza corpus personalizados construidos a partir de texto escrito por humanos no disponible públicamente en forma paralela.

Consulte [Evaluation Datasets](/docs/leaderboard/datasets) para el esquema completo del dataset, niveles de dificultad y cómo crear el suyo.

:::danger NO ENTRENE con datos de evaluación

**Estos datasets son solo para evaluación.** Los métodos entrenados, fine-tuned, con few-shot-prompted o de otra manera expuestos a datos de evaluación producirán puntuaciones artificialmente infladas y serán **descalificados del leaderboard.**

Esto no es una sugerencia — es la regla más importante de la integridad de la evaluación. Utilice corpus separados para entrenamiento. Los conjuntos de evaluación deben permanecer invisibles para su modelo durante el desarrollo.

Si está utilizando datos de coaching o ejemplos few-shot, estos deben provenir de **fuentes completamente separadas**. Si tiene dudas, no los incluya.
:::

:::warning No-determinismo de LLM

Las salidas de LLM son no-deterministas. Las puntuaciones representan mediciones en un punto en el tiempo bajo versiones de modelo específicas y configuraciones de API. Los proveedores de modelos pueden actualizar pesos, estrategias de decodificación o filtros de seguridad en cualquier momento, lo que puede causar desviación de puntuación entre ejecuciones. El leaderboard registra el slug exacto del modelo y la marca de tiempo para cada envío.
:::

---

## Qué Hace un Buen Método

No todos los métodos son iguales. Aquí está lo que separa el trabajo riguroso de las puntuaciones infladas.

### Características de un método fuerte

- **Separación limpia de datos de entrenamiento y evaluación** — su método nunca ha visto el conjunto de evaluación durante el desarrollo, ajuste, ingeniería de prompts o selección de ejemplos few-shot
- **Reproducible** — alguien más puede clonar su repositorio, ejecutar el arnés y obtener las mismas puntuaciones (dentro de los límites de no-determinismo de LLM)
- **Documentado** — su [tarjeta de método](/docs/specifications/methods) describe qué hace su método, qué herramientas utiliza y cuáles son sus limitaciones
- **Honesto sobre el alcance** — si su método solo funciona para un par de idiomas, dígalo; si se degrada en ciertos patrones morfológicos, documente eso
- **Consciente de la comunidad** — para idiomas indígenas, su método respeta la soberanía de datos. Ha consultado con comunidades de idiomas o utilizado solo datos con licencia abierta

### Banderas rojas (lo que se descalifica)

| Bandera Roja | Por Qué Es un Problema |
|--------------|------------------------|
| Entrenamiento con datos de evaluación | Anula completamente el propósito de la evaluación. Las puntuaciones infladas engañan a todos. |
| Cherry-picking de resultados | Ejecutar 10 veces y enviar la mejor ejecución sin divulgar las otras |
| Post-procesamiento no divulgado | Arreglar manualmente las salidas antes de la puntuación |
| Datos de coaching contaminados | Usar ejemplos del conjunto de evaluación como prompts few-shot o entradas de diccionario |
| Afirmar disponibilidad comercial sin procedencia | Si su método utiliza datos CC BY-NC-SA, no está listo comercialmente |

### Niveles de verificación

Los niveles de verificación describen **quién validó el resultado** — separado de los niveles de calidad (Baseline → Fluent) definidos en la [Especificación de Puntuación, §5](/docs/specifications/scoring#5-quality-tiers), que describen qué significa la puntuación compuesta automatizada.

| Nivel | Significado | Cómo Obtenerlo |
|-------|-------------|----------------|
| **Self-benchmarked** | Usted ejecutó el arnés usted mismo y envió resultados | Abra un PR con su tarjeta de ejecución |
| **GDS Verified** | Los mantenedores de champollion reprodujeron sus resultados | Envíe su método como un plugin instalable |
| **Community Validated** | La organización de gobernanza ejecutó contra estándar de oro + revisión de comunidad | Envíe código del método a la organización de gobernanza |

---

## Cómo Enviar

1. **Construya su método** — consulte [Building a Method](/docs/specifications/methods) para la interfaz del método
2. **Ejecute el arnés** — consulte [Eval Harness](/docs/specifications/harness) para configuración y uso
3. **Genere una tarjeta de ejecución** — el arnés produce una tarjeta de ejecución JSON con sus puntuaciones, huella digital y metadatos
4. **Abra un PR** — envíe su tarjeta de ejecución al [repositorio del arnés de evaluación](https://github.com/gamedaysuits/arena)
5. **Aparezca en el leaderboard** — una vez fusionado, sus resultados aparecen en el [Method Leaderboard](https://champollion.dev/leaderboard)

---

## Direcciones Futuras

- **Ejecuciones de comparación de modelos exhaustivas** — evaluación sistemática de modelos fronterizos (GPT-4o, Claude, Gemini, etc.) en idiomas de champollion utilizando corpus de evaluación personalizados (no benchmarks públicos)
- **Más pares de idiomas** — Quechua, Inuktitut y otros idiomas de bajo recurso a medida que datasets verificados por la comunidad estén disponibles
- **Importación de datasets** — herramientas para convertir datasets de evaluación externos (WMT, Tatoeba, etc.) al formato de evaluación de champollion
- **Re-ejecuciones automatizadas** — detectar cambios de versión de modelo y re-ejecutar benchmarks para rastrear desviación de puntuación

---

## Véase También

- **[Method Leaderboard](https://champollion.dev/leaderboard)** — puntuaciones en vivo y envíos
- **[Eval Harness](/docs/specifications/harness)** — cómo ejecutar evaluaciones
- **[Evaluation Datasets](/docs/leaderboard/datasets)** — formato de dataset y datasets disponibles
- **[Building a Method](/docs/specifications/methods)** — especificación de interfaz del método
- **[Run Card Specification](/docs/specifications/run-card)** — esquema JSON de tarjeta de ejecución
- **[Benchmark Specification](/docs/specifications/benchmark)** — protocolo de evaluación, formato de corpus, soberanía
- **[Scoring Specification](/docs/specifications/scoring)** — SSOT para métricas, pesos compuestos y niveles de calidad