---
sidebar_position: 2
title: "Eval Harness v2.0"
related:
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "What the harness metrics feed into"
  - label: "Statistical Significance Testing"
    to: /docs/specifications/significance
    kind: spec
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: Translate 30 Languages"
    to: https://champollion.dev/docs/tutorials/translate-30-languages
    kind: champollion
    note: "Use the harness to audit registers in production"
---
# Eval Harness v2.0

> **Resumen Ejecutivo.** Esta página cubre la instalación, configuración y uso del arnés de evaluación de MT — la herramienta que compara métodos de traducción contra corpus estandarizados y produce tarjetas de ejecución puntuadas. Para definiciones canónicas de métricas, esquemas y protocolo de evaluación, consulte la [Especificación de Benchmark](/docs/specifications/benchmark).

El arnés ejecuta experimentos de traducción y produce tarjetas de ejecución. Maneja la construcción de indicaciones, llamadas a API, puntuación y serialización de resultados — usted proporciona el conjunto de datos y el modelo.

## Instalación

**Requisitos:** Python 3.10+

```bash
pip install sacrebleu aiohttp
```

Clone el repositorio del arnés:

```bash
git clone https://github.com/gamedaysuits/arena.git
cd arena
```

## Uso

```bash
mt-eval run --corpus path/to/dataset.json
```

Esto ejecuta cada entrada del corpus a través del modelo configurado (o complemento de método), puntúa los resultados y escribe un archivo JSON de tarjeta de ejecución en el directorio de salida.

## Banderas CLI

### `mt-eval run`

| Bandera | Requerida | Predeterminado | Descripción |
|---------|-----------|----------------|-------------|
| `--corpus` | ✅ | — | Ruta al archivo de corpus (`.json`, `.jsonl`, `.tsv`) |
| `--source-file` / `--reference-file` | — | — | Archivos de texto paralelo (FLORES+, formato WMT) |
| `-m, --model` | — | `gemini-pro` | Slug del modelo (nombre corto o ID completo de OpenRouter). Se resuelve mediante `shared/model-aliases.json`. Separado por comas para ejecuciones multimodelo |
| `-d, --dataset` | — | `all` | Filtro de conjunto de datos: `all`, nombre de segmento o rango de ID |
| `--ids` | — | — | ID de entradas separadas por comas para evaluar |
| `--source-lang` | — | `English` | Nombre del idioma de origen |
| `--target-lang` | — | — | Nombre del idioma de destino |
| `-p, --prompt` | — | `naive` | Versión de indicación (`naive`, `custom`, `champollion`) |
| `--coaching-file` | — | — | Ruta al archivo de texto de indicación de entrenamiento |
| `--coaching` | — | — | Texto de entrenamiento en línea (cadena entrecomillada) |
| `--method` | — | — | Ruta al directorio del complemento de método (contiene `method.json` + módulo Python) |
| `--method-card` | — | — | Ruta al JSON de tarjeta de método para metadatos de tabla de clasificación |
| `--fst-retries` | — | `0` | Número de intentos de reintento de FST (solo método LLM predeterminado) |
| `--skip-fst` | — | `false` | Omitir completamente la puerta de calidad de FST |
| `--tools` | — | `false` | Habilitar modo de llamada de herramientas |
| `--tools-list` | — | — | Nombres de herramientas separados por comas |
| `--max-tool-rounds` | — | `8` | Rondas máximas de llamada de herramientas por entrada |
| `--hooks` | — | — | Nombres de ganchos posteriores a la traducción |
| `--style-profile` | — | — | Ruta a un perfil de estilo JSON. Habilita métricas de consistencia de estilo de escritura (informativo — nunca parte de la puntuación compuesta; consulte [§ Métricas de estilo de escritura y registro](#métricas-de-estilo-de-escritura-y-registro-informativo)) |
| `-b, --batch-size` | — | `25` | Entradas por llamada a API |
| `-c, --concurrency` | — | `8` | Llamadas a API paralelas |
| `--max-tokens` | — | `32768` | Tokens máximos por llamada a API |
| `--temperature` | — | `0.0` | Temperatura de muestreo (0.0 = determinista) |
| `--no-cache` | — | `false` | Deshabilitar almacenamiento en caché de respuestas |
| `--cache-dir` | — | `eval/cache/harness` | Ruta del directorio de caché |
| `-o, --output-dir` | — | `eval/logs/harness` | Directorio de salida para tarjetas de ejecución y registros |
| `-n, --name` | — | — | Nombre de ejecución legible por humanos |
| `--dry-run` | — | `false` | Validar configuración sin realizar llamadas a API |
| `--champollion-config` | — | — | Ruta a `champollion.config.json` |
| `--champollion-cards-dir` | — | — | Directorio de tarjetas de idioma |
| `--target-lang-code` | — | — | Código de idioma BCP-47 |

### Otros Subcomandos

| Subcomando | Descripción |
|------------|-------------|
| `mt-eval test <log_path>` | Analizar un registro de ejecución completado |
| `mt-eval publish <report_path>` | Enviar una tarjeta de ejecución a la tabla de clasificación |
| `mt-eval compare <logs...>` | Comparar múltiples ejecuciones lado a lado |
| `mt-eval dashboard <logs...>` | Generar un panel HTML a partir de registros de ejecución |
| `mt-eval list models\|prompts\|datasets` | Listar recursos disponibles |
| `mt-eval export` | Empaquetar la configuración actual como un complemento de método champollion |
| `mt-eval export-config` | Exportar la MethodConfig resuelta (los 8 campos canónicos) como JSON |

### Ejemplos

```bash
# Run with defaults (gemini-pro alias → google/gemini-3.1-pro-preview, naive prompt)
mt-eval run --corpus data/edtekla-dev-v1.json

# Coached experiment with coaching file
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model google/gemini-3.1-pro \
  --coaching-file prompts/crk-coaching-v8.txt \
  --temperature 0.0

# Run a custom method plugin with FST retries
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --method ./methods/fst-gated-pipeline \
  --fst-retries 3
```

---

## Esquema de Tarjeta de Ejecución

Cada experimento produce una **tarjeta de ejecución** — un documento JSON independiente. La estructura de nivel superior:

```json
{
  "run_id": "uuid-v4",
  "harness_version": "2.0",
  "model_slug": "google/gemini-3.1-pro",
  "model_id": "gemini-3.1-pro-001",
  "condition": "baseline",
  "timestamp": "2026-06-01T03:22:41Z",
  "elapsed_seconds": 142.7,
  "dataset": { ... },
  "config": { ... },
  "method_card": { ... },
  "system_prompt_sha256": "abc123...",
  "system_prompt_used": "You are a translator...",
  "fingerprint": { ... },
  "scores": { ... },
  "totals": { ... },
  "environment": { ... },
  "results": [ ... ],
  "run_card_hash": "sha256-of-entire-card"
}
```

Consulte la [Especificación de Tarjeta de Ejecución](/docs/specifications/run-card) para el esquema completo con cada campo documentado.

:::info Esquema Autoritativo
La [Especificación de Benchmark](/docs/specifications/benchmark) es la única fuente de verdad para el esquema de tarjeta de ejecución. Para definiciones de métricas, pesos compuestos y niveles de calidad, consulte la [Especificación de Puntuación](/docs/specifications/scoring). Esta página documenta cómo usar el arnés; las especificaciones definen qué significan los resultados.
:::

### Bloques Clave

**`dataset`** — Identifica qué conjunto de datos se utilizó, incluido su hash de contenido para que los resultados estén vinculados a una versión específica:

```json
// Example using master_corpus.json (62 gold + 342 textbook = 404)
{
  "id": "edtekla-dev-v1",
  "version": "1.0",
  "language_pair": "EN→CRK",
  "sha256": "...",
  "entry_count": 404
}
```

**`scores`** — Métricas agregadas para la ejecución:

```json
// Counts reflect the dataset used (here: master_corpus.json, 404 entries)
{
  "total": 404,
  "exact_matches": 12,
  "exact_match_rate": 0.0968,
  "fst_accepted": 87,
  "fst_acceptance_rate": 0.7016,
  "chrf_plus_plus": 42.31,
  "errors": 0,
  "avg_latency_seconds": 1.15,
  "median_latency_seconds": 1.02,
  "p95_latency_seconds": 2.34,
  "by_difficulty": { ... },
  "by_provenance": { ... }
}
```

**`totals`** — Seguimiento de uso de tokens y costos:

```json
{
  "prompt_tokens": 48200,
  "completion_tokens": 3100,
  "reasoning_tokens": 0,
  "cached_tokens": 12000,
  "total_cost_usd": 0.42,
  "cost_per_entry_usd": 0.0034,
  "reasoning_ratio": 0.0
}
```

---

## Métricas de estilo de escritura y registro (informativo)

El arnés puede evaluar si las traducciones coinciden con un **registro** y **estilo de escritura** objetivo, mediante el complemento de métrica `WritingStyleConsistency` (`mt_eval_harness/plugins/writing_style.py`). Una traducción puede ser lingüísticamente correcta pero en el registro incorrecto — fraseología informal en un documento legal, texto estándar formal en copia de marketing — y las métricas de cadena no lo notarán. Estas métricas sí.

**Lo que se mide (por entrada):**

| Métrica | Escala | Significado |
|---------|--------|-------------|
| `style_register_match` | booleano | ¿La salida coincide con el registro esperado? El objetivo proviene del campo `register` de la entrada del corpus (consulte [Especificación de Benchmark §2.6](/docs/specifications/benchmark)) o de un perfil de estilo |
| `style_sentence_length_ratio` | flotante | Longitud promedio de oración predicha vs referencia (1.0 = coincidencia; divergencia = desviación de estilo) |
| `style_formality_score` | 0.0–1.0 | Presencia de marcadores formales/informales (pronombres T–V, contracciones, …) usando recursos de marcadores por idioma |

**Agregado:** `style_consistency_rate` — la fracción de entradas sin desajuste de registro detectado.

Habilite un objetivo personalizado con `--style-profile path/to/profile.json` (por ejemplo, un perfil de voz de marca); sin uno, el complemento recurre a los metadatos `register` de cada entrada del corpus donde esté presente.

:::caution Alcance Honesto
Estas métricas son **solo informativas** — nunca son parte de la puntuación compuesta, y la detección de formalidad se basa en marcadores (una heurística), no en un juicio aprendido. Trátelas como un detector de desviación para adherencia de registro, no como un veredicto sobre calidad de estilo.
:::

---

## Huella Digital vs Hash de Tarjeta de Ejecución

El arnés produce dos hashes distintos. Sirven para propósitos diferentes:

### Huella Digital

La **huella digital** responde: *"¿Podría reproducirse esta ejecución?"*

Genera un hash de la combinación de entradas que definen la configuración del experimento — no los resultados:

- SHA-256 del conjunto de datos
- Slug del modelo
- Etiqueta de condición
- SHA-256 del indicador del sistema
- Temperatura
- Versión del arnés

Dos ejecuciones con huellas digitales idénticas utilizaron la misma configuración. Sus resultados deben ser comparables (módulo no determinismo de API).

### Hash de Tarjeta de Ejecución

El **hash de tarjeta de ejecución** responde: *"¿Ha sido alterado este archivo de resultado específico?"*

Es el SHA-256 de todo el JSON de tarjeta de ejecución (excluyendo el campo `run_card_hash` en sí). Si algún campo cambia — una puntuación, una marca de tiempo, una única salida — el hash se rompe.

:::info Cuándo usar cuál
Use la **huella digital** para agrupar ejecuciones comparables (mismo experimento, diferentes ejecuciones). Use el **hash de tarjeta de ejecución** para verificar la integridad de un archivo de resultado específico.
:::

---

## Publicación en la Tabla de Clasificación

Después de completar una ejecución, use `mt-eval publish` para enviar la tarjeta de ejecución:

```bash
mt-eval publish eval/logs/harness/your-run-card.json
```

Si no se proporcionó `--method-card` durante la ejecución, `mt-eval publish` inicia un asistente interactivo (`method_card_wizard.py`) que lo guía a través de la descripción de su método (nombre, clase, herramientas utilizadas, etc.). La salida del asistente se incrusta en la tarjeta de ejecución antes del envío.

### Envío Manual

Las tarjetas de ejecución se guardan como archivos JSON en el directorio de salida. También puede enviar cualquier archivo de tarjeta de ejecución a través de la interfaz de usuario de la tabla de clasificación en [/leaderboard](https://champollion.dev/leaderboard), o a través de la API:

```bash
curl -X POST https://champollion.dev/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @eval/logs/harness/your-run-card.json
```

:::warning Validación de Tabla de Clasificación
La tabla de clasificación valida las tarjetas de ejecución enviadas contra el registro de conjuntos de datos. Los envíos que hacen referencia a conjuntos de datos desconocidos, o con un `run_card_hash` roto, se rechazan.
:::

:::danger NO ENTRENE con datos de evaluación
Si su método ha visto el conjunto de datos de evaluación durante el desarrollo — como datos de entrenamiento, ejemplos de pocos disparos, entradas de diccionario o material de ingeniería de indicaciones — su envío será **descalificado**. Consulte [Evaluación de MT](/docs/leaderboard/rules) para saber qué hace que un método sea bueno o malo.
:::

---

## Véase También

- [Evaluación de MT](/docs/leaderboard/rules) — descripción general, propuesta de valor de tabla de clasificación y orientación de método bueno/malo
- [Conjuntos de Datos de Evaluación](/docs/leaderboard/datasets) — formato de conjunto de datos, EDTeKLA, FLORES+
- [Especificación de Tarjeta de Ejecución](/docs/specifications/run-card) — el esquema JSON completo
- [Construcción de un Método](/docs/specifications/methods) — la interfaz de método para crear métodos evaluables
- [Tabla de Clasificación de Métodos](https://champollion.dev/leaderboard) — puntuaciones de benchmark en vivo
- [Especificación de Benchmark](/docs/specifications/benchmark) — protocolo de evaluación, formato de corpus, esquema de tarjeta de ejecución
- [Especificación de Puntuación](/docs/specifications/scoring) — SSOT para métricas, pesos compuestos y niveles de calidad