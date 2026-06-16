---
sidebar_position: 3
title: "Conjuntos de Datos de Evaluación"
related:
  - label: "Corpus Design Framework"
    to: /docs/specifications/corpus-design
    kind: spec
    note: "How evaluation corpora are constructed"
  - label: "Cookbook: Corpus Creation"
    to: /docs/tutorials/corpus-creation
    kind: cookbook
    note: "Build a corpus for your language"
  - label: "Benchmark Specification"
    to: /docs/specifications/benchmark
    kind: spec
  - label: "What Counts as a Language Here?"
    to: /docs/context/what-counts-as-a-language
    kind: doc
---
# Conjuntos de Datos de Evaluación

> **Resumen Ejecutivo.** Esta página describe los conjuntos de datos de evaluación disponibles para evaluación comparativa, incluyendo el esquema de entrada del corpus, niveles de dificultad (1–5) y requisitos de procedencia. Actualmente disponibles: EDTeKLA Dev v1 (Plains Cree, 548 entradas totales: 486 de libro de texto + 62 estándar de oro) y FLORES+ Devtest (39 idiomas, 1,012 entradas cada uno).

Los conjuntos de datos son los objetivos fijos contra los que se ejecuta el arnés. Cada conjunto de datos es un archivo JSON que contiene pares origen→destino con referencias estándar de oro. El arnés califica los resultados del modelo contra estas referencias — nunca las modifica.

:::danger NO ENTRENE con datos de evaluación

⚠️ **Estos conjuntos de datos son solo para evaluación.** Los métodos entrenados, ajustados, solicitados con pocos ejemplos, o de otra manera expuestos a datos de evaluación producirán puntuaciones artificialmente infladas y serán **descalificados de la tabla de clasificación.**

Utilice corpus separados para entrenamiento. Los conjuntos de evaluación deben permanecer sin ser vistos por su modelo durante el desarrollo.
:::

---

## Formato del Conjunto de Datos

Cada conjunto de datos sigue el mismo esquema JSON:

```json
{
  "dataset": {
    "id": "dataset-slug",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "description": "Human-readable description of the dataset",
    "source_language": "en",
    "target_language": "crk",
    "created": "2025-05-01",
    "license": "CC-BY-NC-4.0",
    "provenance": ["gold_standard", "textbook"]
  },
  "entries": [
    {
      "id": 1,
      "source": "Hello",
      "reference": "tânisi",
      "difficulty": 1,
      "provenance": "gold_standard",
      "register": "conversational",
      "context": "greeting",
      "notes": "Common greeting, SRO orthography"
    }
  ]
}
```

:::info Esquema Canónico
La [Especificación de Evaluación Comparativa](/docs/specifications/benchmark) define el corpus canónico y el esquema de entrada. Esta página documenta los conjuntos de datos disponibles y cómo crear nuevos.
:::

### Bloque `dataset` de Nivel Superior

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `string` | Identificador único del conjunto de datos (utilizado en tarjetas de ejecución y tabla de clasificación) |
| `version` | `string` | Versión semántica. Incrementar esto invalida comparaciones previas de tarjetas de ejecución |
| `language_pair` | `string` | Etiqueta de visualización (p. ej., `EN→CRK`) |
| `description` | `string` | Opcional. Resumen legible por humanos |
| `source_language` | `string` | Código de idioma de origen BCP 47 |
| `target_language` | `string` | Código de idioma de destino BCP 47 |
| `created` | `string` | Fecha de creación ISO 8601 |
| `license` | `string` | Identificador de licencia SPDX |
| `provenance` | `string[]` | Lista de etiquetas de procedencia utilizadas en todas las entradas |

### Campos de Entrada

| Campo | Tipo | Requerido | Descripción |
|-------|------|----------|-------------|
| `id` | `integer` | ✅ | Identificador único de entrada dentro del corpus |
| `source` | `string` | ✅ | El texto de origen a traducir |
| `reference` | `string` | ✅ | La traducción de referencia estándar de oro |
| `difficulty` | `integer` | ✅ | Nivel de dificultad 1–5 (véase a continuación) |
| `provenance` | `string` | ✅ | Origen de esta entrada (p. ej., `gold_standard`, `textbook`, `elicited`) |
| `register` | `string` | ✅ | Nivel de registro/formalidad (p. ej., `conversational`, `formal`, `ceremonial`) |
| `context` | `string` | ✅ | Función comunicativa (p. ej., `greeting`, `declaration`, `instruction`) |
| `notes` | `string` | ❌ | Contexto opcional para revisores humanos |
| `morphological_analysis` | `string` | ❌ | Desglose morfológico estándar de oro |
| `variant_class` | `string` | ❌ | Etiqueta de clase que agrupa variantes de traducción aceptables |

---

## Conjuntos de Datos Disponibles

### Conjunto de Desarrollo EDTeKLA v1

El primer conjunto de datos de evaluación, construido para traducción de inglés→Plains Cree (SRO). Creado por el [grupo de investigación EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) de la Universidad de Alberta.

| Propiedad | Valor |
|----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Versión** | `1.0` |
| **Par de idiomas** | EN → CRK (Plains Cree, ortografía SRO) |
| **Cantidad de entradas** | 548 totales (486 de libro de texto + 62 estándar de oro). El corpus dev canónico es `textbook_dev.json` (436 entradas — la división dev completa del libro de texto de 486 totales: 436 dev + 50 prueba retenida) |
| **Distribución de dificultad** | Fácil, Medio, Difícil |
| **Procedencia** | `gold_standard` (verificado por hablantes), `textbook` (materiales educativos publicados) |
| **Licencia** | [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) |

**Lo que prueba:**

- Saludos básicos y frases comunes
- Animacidad nominal y obviación
- Conjugación verbal entre personas y tiempos
- Construcciones locativas
- Paradigmas posesivos
- Estructuras de oraciones complejas

:::tip Estructura del corpus
La colección completa de EdTeKLA tiene 548 entradas curadas: 486 del corpus de libro de texto (436 dev + 50 retenidas) y 62 del estándar de oro itwêwina. El corpus dev canónico es `textbook_dev.json` con 436 entradas — la división dev completa del libro de texto. Cada entrada fue verificada por hablantes fluidos o extraída de libros de texto de idioma Cree publicados. Un conjunto de datos más pequeño y de alta calidad con estándares de oro verificados es más útil que uno grande y ruidoso — especialmente para un idioma de recursos limitados donde las traducciones "lo suficientemente cercanas" a menudo son morfológicamente inválidas.
:::

---

## Creación de un Nuevo Conjunto de Datos

Para crear un conjunto de datos para un nuevo par de idiomas o dominio:

### 1. Estructurar el JSON

Siga el esquema [Formato del Conjunto de Datos](#formato-del-conjunto-de-datos). Cada entrada debe tener `source`, `reference`, `difficulty`, `provenance`, `register`, y `context`.

### 2. Asignar un ID único

Utilice un slug descriptivo: `{project}-{split}-v{version}` (p. ej., `edtekla-dev-v1`, `quechua-test-v1`).

### 3. Verificar estándares de oro

Cada valor `reference` debe ser verificado por un hablante fluido o extraído de un recurso publicado y revisado por pares. Las referencias generadas por máquina anulan el propósito de la evaluación.

### 4. Establecer niveles de dificultad

Asigne a cada entrada un nivel de dificultad entero:

| Nivel | Descripción | Ejemplos |
|-------|-------------|----------|
| 1 — Vocabulario básico | Palabras individuales, saludos comunes, números | "hello" → "tânisi" |
| 2 — Oraciones simples | Sujeto-verbo o SVO, tiempo presente | "I see the dog" |
| 3 — Complejidad moderada | Tiempo pasado/futuro, posesivos, animacidad | "I saw his dog yesterday" |
| 4 — Morfología compleja | Obviación, voz pasiva, orden conjuntivo | "the woman whose son went to the store" |
| 5 — Avanzado | Multi-cláusula, registro formal, ceremonial, idiomático | Párrafo completo con tono apropiado al registro |

### 5. Etiquetar procedencia

Cada entrada debe indicar de dónde proviene. Etiquetas comunes:

- `gold_standard` — Verificado por hablantes fluidos
- `textbook` — De materiales educativos publicados
- `elicited` — Producido a través de sesiones de elicitación estructurada
- `corpus` — Extraído de un corpus paralelo

### 6. Validar el archivo

Ejecute el arnés contra su conjunto de datos con cualquier modelo para verificar que el JSON esté bien formado y todos los campos requeridos estén presentes:

```bash
python eval/baseline_experiment.py --dataset path/to/your-dataset.json
```

El arnés generará un error en campos faltantes, índices duplicados o violaciones de esquema.

### 7. Enviar para inclusión

Abra una solicitud de extracción contra el [repositorio del arnés de evaluación](https://github.com/gamedaysuits/arena) con su archivo de conjunto de datos en el directorio `data/`. Incluya documentación de su metodología de verificación y fuentes de procedencia.

---

## FLORES+ Devtest

Un evaluación comparativa multilingüe de cobertura amplia mantenida por la [Iniciativa de Datos de Idiomas Abiertos (OLDI)](https://huggingface.co/datasets/openlanguagedata/flores_plus). Utilizada para la evaluación comparativa de frontera multi-modelo de champollion.

| Propiedad | Valor |
|----------|-------|
| **ID** | `flores-plus-devtest` |
| **Pares de idiomas** | EN → 39 idiomas (todos los idiomas naturales registrados en champollion) |
| **Cantidad de entradas** | 1,012 oraciones por idioma |
| **Licencia** | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) |
| **Fuente** | Originalmente Meta FLORES-200, ahora mantenido por OLDI |
| **Ubicación** | Accesorios pre-extraídos en `test/benchmark/fixtures/` en el repositorio principal de champollion |

:::danger Solo para evaluación
FLORES+ está destinado únicamente a evaluación. Los curadores solicitan explícitamente que **no se utilice como datos de entrenamiento**. Asegúrese de que su contenido esté excluido de cualquier corpus de entrenamiento.
:::

---

## Véase También

- [Evaluación de TA](/docs/leaderboard/rules) — descripción general del marco de evaluación y tabla de clasificación
- [Arnés de Evaluación](/docs/specifications/harness) — cómo ejecutar evaluaciones contra estos conjuntos de datos
- [Especificación de Tarjeta de Ejecución](/docs/specifications/run-card) — el esquema JSON para registrar resultados
- [Tabla de Clasificación de Métodos](https://champollion.dev/leaderboard) — puntuaciones de evaluación comparativa en vivo
- [Proyecto EdTeKLA](https://spaces.facsci.ualberta.ca/edtekla/) — el grupo de investigación de la Universidad de Alberta detrás del conjunto de datos Cree