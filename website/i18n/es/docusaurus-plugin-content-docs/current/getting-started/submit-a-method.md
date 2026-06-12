---
sidebar_position: 1
title: "Enviar un Método"
related:
  - label: "Method Interface"
    to: /docs/specifications/methods
    kind: spec
    note: "The contract your method implements"
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
    note: "What every published run must disclose"
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Cookbook: Few-Shot Prompting"
    to: /docs/tutorials/few-shot-prompting
    kind: cookbook
    note: "The fastest first method to submit"
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
---
# Enviar un Método

> **Resumen Ejecutivo.** Una guía paso a paso para enviar su primer benchmark al ranking. Clone el harness, ejecútelo contra un conjunto de datos, revise su tarjeta de ejecución y envíela. Toma 10 minutos si tiene una clave API.

Esta guía lo acompaña a través del envío de su primer benchmark al ranking de MT Eval Arena.

---

## Requisitos Previos

- **Python 3.10+**
- **Una clave API de OpenRouter** (o equivalente para su proveedor de modelo)
- **Un método de traducción** — cualquier cosa que produzca traducciones a partir de un texto fuente

```bash
# Clone the eval harness
git clone https://github.com/gamedaysuits/arena.git
cd arena
pip install sacrebleu aiohttp
```

---

## Paso 1: Ejecutar el Harness

El harness califica su método contra un conjunto de datos estandarizado:

```bash
mt-eval run \
  --corpus data/edtekla-dev-v1.json \
  --model gemini-pro \
  --condition your-method-name \
  --temperature 0.2
```

| Bandera | Qué Hace |
|---|---|
| `--corpus` | Ruta al corpus de evaluación (`.json`, `.jsonl`, `.tsv`) |
| `--model` | Slug del modelo — alias corto (p. ej. `gemini-pro`) o ID completo de OpenRouter |
| `--condition` | Etiqueta para su método (aparece en el ranking) |
| `--temperature` | Temperatura de muestreo (menor = más determinista) |
| `--fst-retries` | Opcional: número de intentos de reintento FST |
| `--submit` | Enviar automáticamente la tarjeta de ejecución al ranking |

El harness produce una **tarjeta de ejecución** — un archivo JSON independiente con sus puntuaciones, el hash del conjunto de datos, el slug del modelo y una huella digital criptográfica que vincula los resultados a la configuración exacta del experimento.

---

## Paso 2: Revisar Su Tarjeta de Ejecución

Las tarjetas de ejecución se guardan en `results/`. Inspeccione la suya antes de enviarla:

```bash
cat results/your-run-card.json | python -m json.tool
```

Campos clave a verificar:
- `scores.chrf_plus_plus` — su métrica de calidad principal
- `scores.exact_match_rate` — proporción de traducciones perfectas
- `scores.fst_acceptance_rate` — validez morfológica (si se utilizó FST)
- `totals.total_cost_usd` — cuál fue el costo de la ejecución
- `fingerprint` — el hash de reproducibilidad del experimento

Consulte la [Especificación de Tarjeta de Ejecución](/docs/specifications/run-card) para el esquema completo.

---

## Paso 3: Enviar

### Envío automático

Si pasó `--submit` al ejecutar el harness, su tarjeta de ejecución ya fue cargada.

### Envío manual

Envíe cualquier tarjeta de ejecución a través de la API:

```bash
curl -X POST https://mtevalarena.org/api/leaderboard/submit \
  -H "Content-Type: application/json" \
  -d @results/your-run-card.json
```

O cargue a través de la [Interfaz del Ranking](https://champollion.dev/leaderboard).

---

## Qué Sucede Después

1. Su envío se valida (hash del conjunto de datos, integridad de la tarjeta de ejecución)
2. Los resultados aparecen en el ranking como **Auto-evaluado** (nivel de confianza 1)
3. Para obtener el estado **GDS Verificado**, envíe su método como un complemento instalable para que los mantenedores puedan reproducir sus resultados
4. Para métodos de lenguas indígenas: si su método llega a la cima, comienza el proceso de [transferencia de propiedad](/docs/sovereignty/ownership-transfer)

---

## Véase También

- [Uso del Harness](/docs/specifications/harness) — referencia completa de CLI
- [Reglas del Ranking](/docs/leaderboard/rules) — criterios de envío y políticas contra manipulación
- [Construir un Método](/docs/specifications/methods) — el protocolo TranslationMethod
- [Conjuntos de Datos](/docs/leaderboard/datasets) — conjuntos de datos de evaluación disponibles