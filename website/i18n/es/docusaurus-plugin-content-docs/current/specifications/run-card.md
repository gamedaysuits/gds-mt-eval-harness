---
sidebar_position: 4
title: "Especificación de Tarjeta de Ejecución"
---
# Especificación de Tarjeta de Ejecución

> **Resumen Ejecutivo.** La tarjeta de ejecución es la unidad atómica de evaluación comparativa — un documento JSON que registra la configuración completa, resultados por entrada y puntuaciones agregadas de una ejecución de evaluación. Esta página documenta el esquema, campos, mecanismo de huella digital y estructura de puntuaciones. Consulte la [Especificación de Evaluación Comparativa](/docs/specifications/benchmark) para definiciones canónicas.

La tarjeta de ejecución es el registro completo de una única ejecución de evaluación. Contiene todo lo necesario para entender, reproducir y verificar el experimento: configuración, puntuaciones, resultados individuales, uso de tokens y metadatos del entorno.

**Versión del esquema:** 2.0

:::info Esquema Autorizado
La [Especificación de Evaluación Comparativa](/docs/specifications/benchmark) es la fuente única de verdad para el esquema de tarjeta de ejecución. Para definiciones de métricas, pesos compuestos y niveles de calidad, consulte la [Especificación de Puntuación](/docs/specifications/scoring). Esta página documenta la implementación actual.
:::

---

## Campos de Nivel Superior

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `run_id` | `string` | UUID v4 generado al inicio de la ejecución |
| `harness_version` | `string` | Versión semántica del arnés que produjo esta tarjeta (p. ej., `2.0`) |
| `model_slug` | `string` | Slug del modelo utilizado para la ejecución (p. ej., `google/gemini-3.1-pro`) |
| `model_id` | `string` | Identificador del modelo resuelto devuelto por la API (p. ej., `gemini-3.1-pro-001`) |
| `condition` | `string` | Etiqueta del experimento (p. ej., `baseline`, `coached-v3`, `few-shot`) |
| `timestamp` | `string` | Marca de tiempo ISO 8601 UTC cuando se inició la ejecución |
| `elapsed_seconds` | `number` | Duración de reloj de pared de toda la ejecución |

```json
{
  "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "harness_version": "2.0",
  "model_slug": "google/gemini-3.1-pro",
  "model_id": "gemini-3.1-pro-001",
  "condition": "baseline",
  "timestamp": "2026-06-01T03:22:41Z",
  "elapsed_seconds": 142.7
}
```

---

## `dataset`

Identifica el conjunto de datos de evaluación y lo fija a una versión de contenido específica mediante SHA-256.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | `string` | Identificador del conjunto de datos (p. ej., `edtekla-dev-v1`) |
| `version` | `string` | Cadena de versión del conjunto de datos |
| `language_pair` | `string` | Etiqueta de visualización (p. ej., `EN→CRK`) |
| `sha256` | `string` | Hash SHA-256 del contenido del archivo del conjunto de datos. Garantiza los datos exactos utilizados |
| `entry_count` | `number` | Número de entradas en el conjunto de datos |

```json
// Example using master_corpus.json (62 gold + 342 textbook = 404)
{
  "dataset": {
    "id": "edtekla-dev-v1",
    "version": "1.0",
    "language_pair": "EN→CRK",
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "entry_count": 404
  }
}
```

---

## `config`

La configuración de API y procesamiento por lotes utilizada para esta ejecución.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `api_provider` | `string` | Nombre del proveedor de API (p. ej., `openrouter`) |
| `temperature` | `number` | Temperatura de muestreo |
| `max_tokens` | `number` | Tokens máximos por finalización |
| `batch_size` | `number` | Entradas por lote concurrente |
| `concurrency` | `number` | Solicitudes máximas de API en paralelo |
| `coaching_file` | `string` | Ruta al archivo de indicación de entrenamiento, si se utilizó |
| `method_path` | `string` | Ruta al directorio del complemento de método, si se utilizó |
| `fst_retries` | `number` | Número de intentos de reintento de FST |

```json
{
  "config": {
    "api_provider": "openrouter",
    "temperature": 0.0,
    "max_tokens": 32768,
    "batch_size": 25,
    "concurrency": 8
  }
}
```

:::info Las Tarjetas de Ejecución Publicadas Incluyen `method_config`
Cuando una tarjeta de ejecución se publica mediante `mt-eval publish`, `publish.py` inyecta un bloque `method_config` que contiene la MethodConfig canónica de 8 campos. Esto permite instalación sin fricción en el tablero de clasificación — cualquiera puede reproducir el método directamente desde la tarjeta publicada.

```json
{
  "method_config": {
    "model": "gemini-pro",
    "temperature": 0.0,
    "batchSize": 25,
    "register": "Formal Plains Cree. Use SRO orthography.",
    "coachingFile": "prompts/crk-coaching-v8.txt",
    "coachingPrompt": null,
    "promptContext": "champollion",
    "qualityTier": "verified"
  }
}
```

Todos los campos utilizan **camelCase** y siguen el esquema MethodConfig canónico (consulte [Construcción de un Método](/docs/specifications/methods)).
:::

---

## `system_prompt_sha256` / `system_prompt_used`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `system_prompt_sha256` | `string` | Hash SHA-256 de la indicación del sistema. Incluido en la huella digital |
| `system_prompt_used` | `string` | El texto completo de la indicación del sistema enviado al modelo |

El hash de la indicación es parte de la [huella digital](#fingerprint) — dos ejecuciones con indicaciones diferentes tendrán huellas digitales diferentes incluso si todos los demás parámetros coinciden.

---

## `fingerprint`

Un identificador de reproducibilidad. Dos ejecuciones con huellas digitales idénticas utilizaron la misma configuración experimental.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `hash` | `string` | Hash SHA-256 de los componentes ordenados |
| `components` | `object` | Los valores de entrada que fueron procesados |

### Componentes de Huella Digital

| Componente | Descripción |
|-----------|-------------|
| `dataset_sha256` | Hash del archivo del conjunto de datos |
| `model_slug` | Modelo utilizado |
| `condition` | Etiqueta de condición del experimento |
| `system_prompt_sha256` | Hash de la indicación del sistema |
| `temperature` | Temperatura de muestreo |
| `harness_version` | Versión del arnés |

```json
{
  "fingerprint": {
    "hash": "7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
    "components": {
      "dataset_sha256": "e3b0c44298fc1c14...",
      "model_slug": "google/gemini-3.1-pro",
      "condition": "baseline",
      "system_prompt_sha256": "abc123...",
      "temperature": 0.0,
      "harness_version": "2.0"
    }
  }
}
```

:::info Huella Digital ≠ Hash de Tarjeta de Ejecución
La huella digital identifica la *configuración del experimento*. El `run_card_hash` verifica la *integridad del archivo de resultados*. Consulte [Huella Digital vs Hash de Tarjeta de Ejecución](/docs/specifications/harness#fingerprint-vs-run-card-hash) para más detalles.
:::

---

## `scores`

Métricas agregadas para toda la ejecución.

### Puntuaciones de Nivel Superior

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `total` | `number` | Total de entradas evaluadas |
| `exact_matches` | `number` | Entradas donde la salida coincidió exactamente con el estándar de oro |
| `exact_match_rate` | `number` | `exact_matches / total` (0.0–1.0) |
| `fst_accepted` | `number` | Entradas donde el analizador FST aceptó la salida |
| `fst_acceptance_rate` | `number` | `fst_accepted / total` (0.0–1.0). `null` si no se utilizó analizador FST |
| `chrf_plus_plus` | `number` | Puntuación chrF++ a nivel de corpus (0–100) |
| `errors` | `number` | Entradas que fallaron (error de API, tiempo de espera agotado, etc.) |
| `avg_latency_seconds` | `number` | Tiempo de respuesta promedio en todas las entradas |
| `median_latency_seconds` | `number` | Tiempo de respuesta mediano |
| `p95_latency_seconds` | `number` | Tiempo de respuesta del percentil 95 |

### `by_difficulty`

Puntuaciones desglosadas por nivel de dificultad. Cada clave (entero 1–5) contiene los mismos campos de métricas que las puntuaciones de nivel superior.

```json
{
  "by_difficulty": {
    "1": {
      "total": 20,
      "exact_matches": 8,
      "exact_match_rate": 0.40,
      "chrf_plus_plus": 68.2,
      "fst_accepted": 18,
      "fst_acceptance_rate": 0.90
    },
    "2": { ... },
    "3": { ... },
    "4": { ... },
    "5": { ... }
  }
}
```

### `by_provenance`

Puntuaciones desglosadas por procedencia de entrada. Cada clave (p. ej., `gold_standard`, `textbook`) contiene los mismos campos de métricas.

```json
{
  "by_provenance": {
    "gold_standard": {
      "total": 80,
      "exact_matches": 10,
      "exact_match_rate": 0.125,
      "chrf_plus_plus": 44.8
    },
    "textbook": { ... }
  }
}
```

---

## `totals`

Seguimiento de uso de tokens y costos para toda la ejecución.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `prompt_tokens` | `number` | Total de tokens de entrada en todas las llamadas de API |
| `completion_tokens` | `number` | Total de tokens de salida |
| `reasoning_tokens` | `number` | Tokens utilizados para razonamiento de cadena de pensamiento (dependiente del modelo, 0 para la mayoría de modelos) |
| `cached_tokens` | `number` | Tokens servidos desde la caché de indicación del proveedor |
| `total_cost_usd` | `number` | Costo total en USD (según lo informado por la API) |
| `cost_per_entry_usd` | `number` | `total_cost_usd / entry_count` |
| `reasoning_ratio` | `number` | `reasoning_tokens / completion_tokens` (0.0–1.0) |

```json
{
  "totals": {
    "prompt_tokens": 48200,
    "completion_tokens": 3100,
    "reasoning_tokens": 0,
    "cached_tokens": 12000,
    "total_cost_usd": 0.42,
    "cost_per_entry_usd": 0.0034,
    "reasoning_ratio": 0.0
  }
}
```

---

## `environment`

Metadatos del entorno de ejecución para reproducibilidad.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `harness_version` | `string` | Versión del arnés (refleja el `harness_version` de nivel superior) |
| `harness_git_commit` | `string` | SHA de confirmación de Git del arnés en tiempo de ejecución |
| `python_version` | `string` | Versión del intérprete de Python |
| `sacrebleu_version` | `string` | Versión de la biblioteca sacrebleu (utilizada para puntuación chrF++) |
| `os` | `string` | Identificador del sistema operativo |

```json
{
  "environment": {
    "harness_version": "2.0",
    "harness_git_commit": "a1b2c3d",
    "python_version": "3.11.9",
    "sacrebleu_version": "2.4.0",
    "os": "macOS-14.5-arm64"
  }
}
```

---

## `results[]`

La matriz de resultados por entrada. Un objeto por entrada del conjunto de datos, en orden de índice.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `entry_id` | `integer` | ID de esta entrada en el corpus (coincide con `entries[].id`) |
| `source` | `string` | El texto de origen que fue traducido |
| `reference` | `string` | La referencia estándar de oro del corpus |
| `predicted` | `string` | La salida real del método |
| `exact_match` | `boolean` | Si `predicted` coincide exactamente con `reference` después de la normalización |
| `entry_chrf` | `number` | Puntuación chrF++ a nivel de oración para esta entrada (0–100) |
| `fst_accepted` | `boolean \| null` | Si el analizador FST aceptó la salida. `null` si no se configuró analizador |
| `fst_analysis` | `string[]` | Cadenas de análisis FST para la salida (matriz vacía si no se analizó o fue rechazada) |
| `difficulty` | `integer` | Nivel de dificultad del corpus (1–5) |
| `provenance` | `string` | Etiqueta de procedencia del corpus |
| `latency_seconds` | `number` | Tiempo de respuesta para esta entrada individual |
| `usage` | `object` | Uso de tokens por entrada: `{ prompt_tokens, completion_tokens, reasoning_tokens }` |
| `error` | `string \| null` | Mensaje de error si esta entrada falló. `null` en caso de éxito |

```json
{
  "results": [
    {
      "entry_id": 1,
      "source": "Hello",
      "reference": "tânisi",
      "predicted": "tânisi",
      "exact_match": true,
      "entry_chrf": 100.0,
      "fst_accepted": true,
      "fst_analysis": ["tânisi+V+AI+Ind+2Sg"],
      "difficulty": 1,
      "provenance": "gold_standard",
      "latency_seconds": 0.82,
      "usage": {
        "prompt_tokens": 385,
        "completion_tokens": 12,
        "reasoning_tokens": 0
      },
      "error": null
    }
  ]
}
```

---

## `run_card_hash`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `run_card_hash` | `string` | Hash SHA-256 de toda la tarjeta de ejecución JSON, con el campo `run_card_hash` establecido en `""` durante el procesamiento |

Este es el sello de detección de manipulación. El tablero de clasificación recalcula este hash en la presentación y rechaza las tarjetas donde no coincide.

**Cálculo del hash:**

1. Serialice la tarjeta de ejecución a JSON con `run_card_hash` establecido en `""`
2. Calcule SHA-256 de la cadena serializada
3. Establezca `run_card_hash` en el resumen hexadecimal resultante

```python
import hashlib, json

card["run_card_hash"] = ""
card_json = json.dumps(card, sort_keys=True, ensure_ascii=False)
card["run_card_hash"] = hashlib.sha256(card_json.encode()).hexdigest()
```

:::info Análisis Detallado por Entrada
Las tarjetas de ejecución publicadas también rellenan la tabla `run_card_entries` de Supabase, que almacena resultados por entrada para análisis detallado en el tablero de clasificación. Esta tabla se rellena automáticamente durante `mt-eval publish`.
:::

---

## Véase También

- [Evaluación de MT](/docs/leaderboard/rules) — descripción general, valor del tablero de clasificación y orientación sobre métodos buenos/malos
- [Arnés de Evaluación](/docs/specifications/harness) — cómo ejecutar evaluaciones y generar tarjetas de ejecución
- [Conjuntos de Datos de Evaluación](/docs/leaderboard/datasets) — formato de conjunto de datos, EDTeKLA, FLORES+
- [Construcción de un Método](/docs/specifications/methods) — la interfaz de método y especificación de tarjeta de método
- [Tablero de Clasificación de Métodos](https://champollion.dev/leaderboard) — puntuaciones de evaluación comparativa en vivo
- [Especificación de Evaluación Comparativa](/docs/specifications/benchmark) — protocolo de evaluación, formato de corpus, esquema de tarjeta de ejecución
- [Especificación de Puntuación](/docs/specifications/scoring) — SSOT para métricas, pesos compuestos y niveles de calidad