---
sidebar_position: 4
title: "Contribuir Capacidad de Cómputo"
description: "Dona tus tokens: ejecuta barridos de evaluación comparativa abiertos desde la cola pública con tu propia clave de API y publica los resultados."
related:
  - label: "Agent Guide: Winning the Arena"
    to: /docs/getting-started/agent-guide
    kind: guide
  - label: "Cookbook: Coached LLM Prompting"
    to: /docs/tutorials/coached-llm-prompting
    kind: cookbook
  - label: "Cookbook: FST-Gated Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
  - label: "Method Interface & Dependency Classes"
    to: /docs/specifications/methods
    kind: spec
  - label: "Leaderboard Rules & Trust Tiers"
    to: /docs/leaderboard/rules
    kind: guide
---
# Contribuyendo Computación

> **La idea:** el tablero de clasificación tiene casillas vacías — combinaciones (par de idiomas, modelo, condición) que nadie ha medido. Mantenemos una cola pública de ellas. Usted ejecuta elementos con su propia clave de API, publica los reportes, y el mapa se completa. "Donar tokens" es una contribución real y citable a la evaluación de traducción automática de bajo recurso.

## La cola

La cola en vivo se publica en [champollion.dev/queue.json](https://champollion.dev/queue.json), y hay un visor de terminal sin instalación:

```bash
curl -fsSL champollion.dev/queue | bash
```

El visor solo *muestra* elementos abiertos y sus comandos exactos `mt-eval run` — nunca ejecuta nada ni gasta sus tokens. Cada elemento contiene:

- `run_command` — listo para copiar y pegar (obtiene el corpus, ejecuta el arnés)
- `est_cost_usd` y `est_basis` — ya sea el costo **observado** de nuestra propia ejecución de referencia de la misma (corpus, modelo), o una **extrapolación** del costo promedio por entrada del barrido de ese modelo × el número de entradas del corpus. La base se indica por elemento; su costo real depende de los precios del proveedor en tiempo de ejecución.
- `priority` — pares de idiomas sin cobertura primero, pares de menor recurso primero (el tamaño del corpus es el proxy), ingenuo antes que entrenado, modelo más económico primero.

**Sin bloqueo de reclamaciones — elija cualquier elemento abierto.** Dos personas ejecutando el mismo elemento es inofensivo por diseño: cada tarjeta de ejecución tiene huella digital (SHA-256 sobre hash de conjunto de datos + modelo + condición + indicación del sistema, [Especificación de Referencia §3.8](/docs/specifications/benchmark)), por lo que las ejecuciones idénticas se deduplicarán al publicar, y las replicaciones independientes de la misma configuración son evidencia útil, no desperdicio.

Los corpus en cola están divididos en desarrollo, con licencia CC-BY-family (derivados de Tatoeba), y marcados `do_not_train` — son conjuntos de evaluación, no datos de entrenamiento. Los corpus con licencia no comercial y los corpus en cuarentena se excluyen de la cola abierta.

## Configuración (una sola vez)

```bash
# 1. Install the harness (python3 + pipx, no sudo — read it first if you like)
curl -fsSL champollion.dev/harness | bash

# 2. Set your API key
export OPENROUTER_API_KEY="sk-or-..."     # or put it in a local .env file
```

### ¿Qué clave de proveedor?

El arnés enruta **todas** las llamadas de modelo a través de [OpenRouter](https://openrouter.ai/keys). Una `OPENROUTER_API_KEY` alcanza cada modelo en la alineación de la cola — modelos Anthropic Claude, OpenAI GPT y Google Gemini por igual — y el seguimiento de costos del arnés y las instantáneas de precios provienen de los mismos metadatos de OpenRouter, por lo que el costo de ejecución reportado coincide con lo que se facturó a su clave.

Si sus créditos están con Anthropic, OpenAI o Google directamente: el arnés **no** acepta actualmente claves de proveedor directo. El esquema de tarjeta de ejecución reserva un campo `api_provider` para el día en que lo haga, pero hoy cada ejecución del arnés es una ejecución de OpenRouter. Crear una cuenta de OpenRouter y financiarla (o adjuntar su propia cuenta de proveedor donde OpenRouter lo admita) es el camino soportado.

### La ruta rápida del agente

Si trabaja con Claude Code u otro agente de codificación, toda la contribución es un indicador:

```text
Install the Champollion mt-eval harness (curl -fsSL champollion.dev/harness | bash).
Fetch https://champollion.dev/queue.json and show me the top 3 open items.
Using my OpenRouter key (OPENROUTER_API_KEY), execute the run_command of the
item I pick, then run `mt-eval publish` on the generated report JSON and
show me the published run card.
```

## Nivel 1 — Ejecutar una referencia

Cada `run_command` del elemento de la cola es autónomo. Uno típico:

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/eng-yor-dev-v1.json
mt-eval run --corpus eng-yor-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Yoruba"
```

La ejecución imprime su costo total y escribe un registro de ejecución más un reporte puntuado en `eval/logs/`. Luego publique:

```bash
mt-eval publish eval/logs/harness/run_..._report.json
```

La publicación lo registra mediante OAuth (su nombre se convierte en la atribución del tablero de clasificación) e inserta la tarjeta de ejecución. Los envíos de la comunidad llegan al nivel de confianza **auto-evaluado** — claramente etiquetado como "enviado por la persona que lo ejecutó." Eso no es una degradación; es el modelo de confianza funcionando. La tarjeta de ejecución contiene todo lo necesario para que cualquiera re-ejecute su configuración exacta: hash del conjunto de datos, modelo, condición, la indicación del sistema completa, y costo. Los niveles elevados (verificación, validación de la comunidad) se otorgan por revisión — vea [Reglas del Tablero de Clasificación](/docs/leaderboard/rules).

## Nivel 2 — Crear indicaciones entrenadas

El arnés tiene soporte de primera clase para **entrenamiento**: reemplace la indicación del sistema ingenua con una que lleve conocimiento lingüístico real. Pase `--coaching-file` (o `--coaching "inline text"` para indicaciones cortas) y el arnés usa su texto como la indicación del sistema, registra el **texto completo más su SHA-256** en el bloque de procedencia del registro de ejecución, y etiqueta la condición de la ejecución como **`coached`** (a menos que establezca `--prompt` explícitamente) — por lo que la elaboración de indicaciones es un experimento reproducible y atribuible, dos archivos de entrenamiento diferentes nunca pueden confundirse entre sí, y las ejecuciones entrenadas nunca se confunden con líneas de base ingenuas en el tablero de clasificación.

Un ejemplo trabajado para feroés, usando hechos de tipología y entradas de glosario de la [tarjeta de idioma pública](https://champollion.dev/languages) del idioma:

```text title="coaching-fao.txt"
You are translating Danish into Faroese (føroyskt).

Grammar notes:
- Faroese is a North Germanic V2 language: the finite verb is the second
  constituent of a main clause.
- Nouns inflect for case (nominative, accusative, dative, genitive),
  gender (masculine, feminine, neuter), and number. Make adjectives and
  determiners agree.
- The skerping pattern applies before -gv/-ggj sequences; preserve
  standard orthography including ð (which is silent).

Glossary (use these exact equivalents):
- language -> mál
- island -> oyggj
- weather -> veður

Style: plain register, modern standard orthography. Output only the
Faroese translation, no commentary.
```

```bash
curl -fsSLO https://raw.githubusercontent.com/gamedaysuits/gds-mt-eval-harness/main/datasets/curated/dan-fao-dev-v1.json
mt-eval run --corpus dan-fao-dev-v1.json \
  --model anthropic/claude-haiku-4.5 \
  --target-lang "Faroese" \
  --coaching-file coaching-fao.txt
```

(Escriba su propio contenido de entrenamiento — los hechos anteriores ilustran la *forma*: algunas reglas gramaticales de alto impacto, un pequeño glosario de términos que el modelo interpreta mal, una instrucción de registro. Las tarjetas de idioma en [champollion.dev/languages](https://champollion.dev/languages) citan fuentes de tipología de las que puede extraer.)

Compare contra la línea de base ingenua con `mt-eval compare <naive_log> <coached_log>`, itere, y publique su mejor ejecución. La ejecución se publica con condición `coached` automáticamente; si desea que el tablero de clasificación muestre un método nombrado en lugar de la etiqueta genérica, adjunte una tarjeta de método cuando publique (el flujo de publicación ofrece un asistente). Superar la línea de base ingenua en un par de bajo recurso con nada más que ingeniería de indicaciones es un hallazgo genuino y publicable — vea el [libro de recetas completo de Indicaciones LLM Entrenadas](/docs/tutorials/coached-llm-prompting) para orientación de diseño.

## Nivel 3 — Construir un método

La contribución más ambiciosa: implementar el protocolo `TranslationMethod` (`translate(entries, config)`) y evaluar un sistema real, no solo una indicación. El arnés lo ejecuta mediante `--method <plugin-dir>` e incrusta su tarjeta de método en la tarjeta de ejecución. Patrones con libros de recetas trabajados:

- **[Tuberías con puerta FST](/docs/tutorials/fst-gated-pipeline)** — cada palabra candidata se verifica mediante un analizador morfológico; el LLM se regenera hasta que la puerta pase. Salida semi-determinista, garantizada por morfología.
- **[Generación aumentada por diccionario](/docs/tutorials/dictionary-augmented-llm)** — busque términos de origen en un léxico bilingüe en tiempo de traducción y restrinja la salida.
- [Modelos encadenados](/docs/tutorials/chained-models), [recuperación de pocos ejemplos](/docs/tutorials/few-shot-prompting), [traducción inversa](/docs/tutorials/back-translation), [híbridos basados en reglas](/docs/tutorials/rule-based-hybrid)…

Los métodos declaran una **clase de dependencia** (S/O/A1/A2/X — vea [la especificación de métodos](/docs/specifications/methods#method-validity-and-dependency-classes)) describiendo qué necesitan para ejecutarse y transferirse: una tubería autónoma es Clase S; una que llama a una API de diccionario con licencia en tiempo de ejecución es A2. Declare honestamente — la clase determina dónde su método puede competir, y los manifiestos se auditan.

## Por qué esto importa más allá del tablero de clasificación

Cada ejecución publicada es evidencia independiente sobre la calidad de la traducción automática para un par de idiomas que los proveedores comerciales no miden. La cola también funciona como un registro público de *demanda*: qué pares la comunidad considera que vale la pena medir, qué cobertura cuesta a los precios actuales de la API, y cuánto se extiende la computación donada. Cuando pedimos a agencias de financiamiento que financien barridos sistemáticos, esta cola y su tasa de llenado son la evidencia de demanda.