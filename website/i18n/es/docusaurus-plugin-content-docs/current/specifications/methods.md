---
sidebar_position: 4
title: "Interfaz de Método"
related:
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
    note: "Put this interface on the leaderboard"
  - label: "Eval Harness v2.0"
    to: /docs/specifications/harness
    kind: spec
  - label: "Run Card Specification"
    to: /docs/specifications/run-card
    kind: spec
  - label: "Cookbook: FST-Gated Translation Pipeline"
    to: /docs/tutorials/fst-gated-pipeline
    kind: cookbook
    note: "A full method, built end-to-end"
---
# Interfaz de Método Compartida

> **Resumen Ejecutivo.** Esta página especifica el protocolo `TranslationMethod` que todos los métodos de Arena deben implementar, las seis clases de métodos (`raw-llm`, `coached-llm`, `pipeline`, `custom-plugin`, `api`, `human`), el formato de complemento de método, y las **clases de dependencia** (S/O/A1/A2/X) que determinan si un método puede ejecutarse en la zona de pruebas de evaluación y calificar para premios. Cualquier enfoque que implemente este protocolo puede ser evaluado; lo que depende determina dónde puede competir.

El arnés de evaluación y champollion comparten un concepto común de **método de traducción**. Un método es cualquier procedimiento que toma texto fuente y produce texto traducido — ya sea una llamada directa a LLM, una tubería de múltiples etapas, una API de terceros, o un traductor humano.

## Arquitectura

```
Method Plugin (v2 Spec)
├── method.json           ← Manifest (name, class, entry_point, dependencies, metadata)
├── method_card.json      ← Leaderboard description (what, not how)
├── pipeline.py           ← Python module implementing TranslationMethod
└── (optional helpers)    ← Additional Python modules
```

Se carga a través de `--method path/to/dir`. El arnés no descubre nada automáticamente.

## Dos Sistemas, Una Interfaz

| | Arnés de Evaluación | champollion |
|---|---|---|
| **Lenguaje** | Python | Node.js |
| **Punto de entrada** | `translate.py` | `translate.js` |
| **Interfaz** | protocolo `TranslationMethod` | configuración `methodPlugin` |
| **Propósito** | Evaluación por lotes con puntuación | Localización en vivo en dev/CI |
| **Salida** | Tarjeta de ejecución con métricas | Archivos de configuración regional traducidos |

Un método que admite ambos sistemas proporciona dos puntos de entrada — uno para cada tiempo de ejecución de lenguaje. La **tarjeta de método** es el puente: describe el método en un formato que ambos sistemas entienden.

## Tarjeta de Método

Una tarjeta de método describe *qué* es un método de traducción sin revelar detalles propietarios como el mensaje del sistema completo. Responde:

- ¿Qué clase de método es este? (LLM sin procesar, LLM entrenado, tubería, API, etc.)
- ¿Qué herramientas utiliza? (analizador FST, diccionario, etc.)
- ¿Es la implementación de código abierto?
- ¿Qué pares de idiomas admite?

Consulte la [Especificación de Tarjeta de Método](/docs/specifications/methods#method-card) para el esquema JSON completo.

### Ejemplo

```json
{
  "method_id": "fst-gated-v8",
  "name": "FST-Gated Coached Translation v8",
  "class": "pipeline",
  "description": "LLM translation with morphological validation. Failed words are retried with FST feedback.",
  "author": "Curtis Forbes",
  "tools_used": ["HFST morphological analyzer", "Wolvengrey dictionary"],
  "open_source": false,
  "dependency_class": "A2",
  "supported_pairs": ["eng>crk"]
}
```

El campo `dependency_class` resume lo que el método necesita para ejecutarse y transferirse — consulte [Validez de Método y Clases de Dependencia](#method-validity-and-dependency-classes) a continuación.

### Clases de Método

| Clase | Descripción |
|-------|-------------|
| `raw-llm` | Llamada directa a LLM con instrucción mínima |
| `coached-llm` | LLM con mensaje estructurado, ejemplos, restricciones |
| `pipeline` | Tubería de múltiples etapas con componentes determinísticos |
| `custom-plugin` | Proceso externo que implementa el protocolo `TranslationMethod` |
| `api` | API de traducción de terceros (Google Translate, DeepL, etc.) |
| `human` | Traducción humana (para establecer líneas de base) |

## Validez de Método y Clases de Dependencia

Un método es tan ejecutable, y tan transferible, como su dependencia menos disponible. Dos mecanismos de Arena dependen de saber exactamente qué necesita un método:

1. **Evaluación en zona de pruebas** ([Especificación de Evaluación §8.2](/docs/specifications/benchmark)) — las puntuaciones de oro estándar oficial provienen de una zona de pruebas cuya política de red es **negación por defecto**. Un método que requiere silenciosamente un servicio externo no puede producir una puntuación oficial.
2. **Transferencia de premios** ([Especificación de Premios](/docs/specifications/prizes)) — los métodos ganadores de premios se transfieren a la organización de gobernanza de la comunidad de idiomas. Un método que agrupa contenido que el remitente no tenía derecho a incluir no puede transferirse legalmente. El remitente debe poseer (o se le debe otorgar) los derechos de todo en la caja.

Para hacer ambas verificaciones mecánicas en lugar de ad hoc, cada método declara una **clase de dependencia**, derivada de un **manifiesto de dependencia** en `method.json`.

> **Nota sobre nomenclatura.** *Clase de método* (§arriba: `raw-llm`, `pipeline`, …) describe *cómo traduce un método*. *Clase de dependencia* (esta sección) describe *qué necesita un método para ejecutarse y transferirse*. Son ejes independientes: un método `pipeline` puede ser cualquier clase de dependencia.

### Las Cinco Clases de Dependencia

| Clase | Nombre | Definición | ¿Ejecutable en zona de pruebas? | ¿Elegible para premio? |
|-------|--------|-----------|--------------------------------|----------------------|
| **S** | Autónomo | Todo el código, datos, modelos y pesos se envían dentro del directorio del método, bajo licencias que permiten redistribución y transferencia comunitaria. | ✅ Sí, tal cual | ✅ Sí |
| **O** | Externo abierto | Depende de artefactos alojados externamente bajo licencias abiertas que permiten redistribución (incluidas licencias copyleft como AGPL) — por ejemplo, un FST descargado en tiempo de instalación. | ✅ Sí — los artefactos se fijan y se **reflejan en el envío** | ✅ Sí, con condiciones de compatibilidad de licencia: los términos copyleft se preservan a través de la transferencia, y la comunidad recibe los mismos derechos que la licencia otorga a todos |
| **A1** | Dependiente de API, sustituible | Requiere inferencia de LLM en tiempo de ejecución, donde el modelo es **configuración sustituible** — cualquier modelo suficientemente capaz puede insertarse. El valor del método reside en sus mensajes, datos de entrenamiento y código, no en el modelo de ningún proveedor. | ⚠️ Solo a través de la **puerta de enlace de LLM** que la especificación de zona de pruebas define (🔲 planeado — ver abajo) | ⚠️ Condicional — ver abajo |
| **A2** | Dependiente de API, no sustituible | Requiere llamadas en tiempo de ejecución a una API de datos o servicio externo que no puede reflejarse o sustituirse — típicamente porque el contenido servido es propietario o sin licencia (por ejemplo, una API de diccionario cuyo diccionario subyacente no tiene licencia pública). | ❌ No — la dependencia no puede existir en la zona de pruebas sin permiso del titular de derechos | ❌ No hasta que el titular de derechos otorgue permisos de **inclusión en zona de pruebas** y **transferencia**. Permitido en el marcador abierto (segmento de desarrollo) con una bandera **"dependencia externa"** visible |
| **X** | Cerrado | Agrupa contenido que el remitente no tiene derecho a redistribuir — conjuntos de datos sin licencia, contenido propietario raspado, componentes incompatibles con licencia. | ❌ | ❌ Inadmisible en todos los carriles. Agrupar contenido sin derechos es una violación de licencia independientemente de dónde se ejecute el método |

**Clase efectiva.** La clase de dependencia de un método es la clase *más restrictiva* entre todas sus dependencias declaradas, en el orden S < O < A1 < A2 < X. Un diccionario sin licencia hace que una tubería por lo demás autónoma sea Clase A2 (si se accede en tiempo de ejecución) o Clase X (si se agrupa sin derechos).

### La Distinción A1/A2: Sustituibilidad

La mayoría de los métodos llaman a LLM. Arena no pretende lo contrario — pero distingue dos tipos muy diferentes de dependencia de API:

- **A1 (sustituible):** La API proporciona inferencia de LLM de mercancía. El identificador del modelo es configuración: el método debe ejecutarse de extremo a extremo contra cualquier punto final de inferencia compatible, incluido un modelo de peso abierto alojado en la comunidad. La calidad de salida puede diferir entre modelos — ese es el riesgo del desarrollador, y las puntuaciones oficiales están vinculadas al modelo fijado utilizado en la evaluación. Un método que depende de **estado del lado del proveedor** (un ajuste fino alojado solo en el proveedor, almacenes de archivos del proveedor, asistentes específicos del proveedor) *no* es sustituible: ese estado no puede extraerse, por lo que la dependencia es A2 a menos que los pesos o datos subyacentes se incluyan en el envío.
- **A2 (no sustituible):** La API sirve algo único — típicamente datos propietarios o sin licencia. Ningún punto final alternativo puede proporcionarlo, y el contenido no puede reflejarse en la zona de pruebas sin permiso del titular de derechos. El método funciona en el marcador abierto (marcado), pero no puede producir puntuaciones oficiales de zona de pruebas o calificar para premios hasta que existan permisos.

**Lo que una transferencia de premio A1 realmente transmite.** La comunidad no recibe el modelo — nadie puede transferir los pesos de Anthropic, Google u OpenAI. La transferencia cubre la receta completa *alrededor* del modelo: todos los mensajes, datos de entrenamiento, código de tubería, lógica de reintentos, configuración y requisitos de modelo documentados. Porque el modelo es sustituible por construcción, la comunidad puede apuntar el método transferido a cualquier proveedor que elija — o a un modelo de peso abierto en su propio hardware — sin la participación del desarrollador. La receta es propiedad; el motor se alquila y es reemplazable.

### Manifiesto de Dependencia (`method.json`)

Cada método declara sus dependencias en el manifiesto `method.json`. Cada entrada registra qué es el artefacto, de dónde viene, qué licencia lo cubre y cómo el método lo accede:

```json
{
  "name": "FST-Gated Coached Translation v8",
  "method_id": "fst-gated-v8",
  "class": "pipeline",
  "entry_point": "pipeline:PipelineMethod",
  "supported_pairs": ["eng>crk"],
  "dependency_class": "A2",
  "dependencies": [
    {
      "id": "giellalt-lang-crk-fst",
      "kind": "software",
      "license": "AGPL-3.0-or-later",
      "access": "mirrored",
      "source": "https://github.com/giellalt/lang-crk",
      "pin": "sha256:3f1a…",
      "redistributable": true,
      "transferable": true
    },
    {
      "id": "llm-inference",
      "kind": "model",
      "license": "proprietary",
      "access": "gateway",
      "source": "openrouter:google/gemini-2.5-flash",
      "substitutable": true,
      "redistributable": false,
      "transferable": false,
      "notes": "Any compatible chat-completions endpoint works; the model slug is configuration."
    },
    {
      "id": "crk-dictionary-api",
      "kind": "service",
      "license": "none",
      "access": "external-api",
      "source": "https://itwewina.altlab.app/",
      "redistributable": false,
      "transferable": false,
      "notes": "Dictionary content has no public license; runtime lookups only. Class A2 until the rights holders grant permission."
    }
  ]
}
```

| Campo | Requerido | Descripción |
|-------|-----------|-------------|
| `id` | ✅ | Identificador estable para la dependencia |
| `kind` | ✅ | `data`, `model`, `software`, o `service` |
| `license` | ✅ | Identificador SPDX, `proprietary`, o `none`. `none` significa que no existe licencia pública — se trata como todos los derechos reservados |
| `access` | ✅ | `bundled` (se envía en el directorio del método), `mirrored` (se obtiene en la instalación, se fija, se incluye en el envío), `gateway` (inferencia de LLM en tiempo de ejecución a través de la puerta de enlace de evaluación), `external-api` (cualquier otra llamada de red en tiempo de ejecución) |
| `source` | ✅ | URL canónica o identificador `provider:slug` |
| `pin` | para `mirrored` | Versión, confirmación o hash de contenido que fija el artefacto exacto |
| `substitutable` | para `gateway`/`external-api` | Si cualquier punto final compatible puede servir esta dependencia |
| `redistributable` | ✅ | Si la licencia permite redistribuir el artefacto |
| `transferable` | ✅ | Si el artefacto (o derechos sobre él) puede transferirse a una comunidad bajo términos de transferencia de premio |
| `notes` | ❌ | Contexto de forma libre |

**Derivación de clase.** Cada dependencia contribuye una clase; la `dependency_class` del método es la más restrictiva:

| Perfil de dependencia | Contribuye |
|----------------------|-----------|
| `bundled` + licencia permite redistribución y transferencia | S |
| `mirrored` + licencia abierta que permite redistribución (copyleft incluido) | O |
| `gateway` + `substitutable: true` (inferencia de LLM) | A1 |
| `external-api`, o `gateway` con `substitutable: false` | A2 |
| `bundled` + `license: none` o licencia incompatible con redistribución | X |

La `dependency_class` declarada debe coincidir con la clase que el arnés deriva del manifiesto. Una discrepancia es un error de validación.

Un método sin **ninguna** dependencia externa declara `"dependency_class": "S"` y `"dependencies": []`. La matriz vacía es una declaración afirmativa, auditada como cualquier otra.

### Cómo Se Verifica la Validez

Tres capas, de la más barata a la más autorizada:

1. **Auditoría de manifiesto.** El arnés deriva la clase efectiva del manifiesto y rechaza discrepancias. Los revisores verifican cada dependencia declarada contra su licencia y fuente declaradas — una dependencia declarada `redistributable: true` cuya licencia ascendente dice lo contrario falla la revisión.
2. **Análisis estático.** El código enviado se escanea en busca de llamadas de red, descargas dinámicas y acceso al sistema de archivos que el manifiesto no contabiliza. Una dependencia *no declarada* encontrada en la revisión es motivo de rechazo independientemente de qué clase habría sido — el manifiesto debe ser completo, no solo preciso.
3. **Política de red de zona de pruebas.** La especificación de zona de pruebas requiere **negación por defecto de salida**: los contenedores de método no obtienen acceso de red a menos que una ruta esté explícitamente en la lista de permitidos. La única ruta de salida que la especificación define es la **puerta de enlace de LLM** — un proxy de inferencia operado por la infraestructura de evaluación, restringido a una lista de permitidos explícita de modelos fijados, con cada solicitud y respuesta registrada para auditoría posterior a la ejecución. Cualquier cosa que no esté en la lista de permitidos falla en la capa de red, no en la capa de política. Consulte [Especificación de Evaluación §8.6](/docs/specifications/benchmark) para la política de red y el diseño de la puerta de enlace.

> 🔲 **Planeado.** La zona de pruebas y su puerta de enlace de LLM están especificadas pero aún no se han construido. Hasta que la puerta de enlace sea operativa, solo los métodos de Clase S y Clase O pueden evaluarse en la zona de pruebas; los métodos de Clase A1 son elegibles para premios *en principio* pero aún no pueden producir puntuaciones de oro estándar oficial. Esta página describe lo que la especificación requiere, no lo que actualmente se ejecuta.

### Visualización del Marcador

- El marcador muestra la clase de dependencia de cada método junto con su distintivo de clase de método.
- Los métodos de Clase A2 en el marcador abierto llevan una bandera **"dependencia externa"** visible: sus puntuaciones dependen de un servicio de terceros que puede cambiar o desaparecer, y actualmente no son elegibles para premios.
- Los métodos de Clase X no se enumeran.

## Arnés de Evaluación: Protocolo TranslationMethod

El arnés de evaluación utiliza tipificación estructural de Python (`Protocol`) para complementos. Cualquier clase con la firma de método correcta funciona — no se requiere herencia:

```python
class MyMethod:
    async def translate(self, entries: list[dict], config: RunConfig) -> list[dict]:
        results = []
        for entry in entries:
            translation = await self.do_translation(entry["source"])
            results.append({
                "id": entry["id"],
                "predicted": translation,
                "latency_s": 0.5,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0},
                "error": None,
                "tool_calls": [],
                "tool_call_count": 0,
                "metadata": {},
            })
        return results
```

Consulte el [Protocolo de Complemento](/docs/specifications/methods#eval-harness-translationmethod-protocol) para documentación completa incluyendo ejemplos de envoltura para métodos que no son Python.

## champollion: Configuración methodPlugin

En champollion, los métodos se registran por par de idiomas en `champollion.config.json`:

```json
{
  "version": 3,
  "pairs": {
    "en:crk": {
      "methodPlugin": "crk-coached-v1"
    }
  }
}
```

Consulte la [Especificación de Complemento](https://champollion.dev/docs/reference/plugin-spec) para la interfaz del lado de champollion.

## Integración del Marcador

Cuando una tarjeta de método se adjunta a una ejecución (a través de `--method-card`), se incrusta en la tarjeta de ejecución y se muestra en el marcador:

```bash
# Run with method card attached
mt-eval run \
  --method path/to/my-method \
  --corpus data/edtekla-dev-v1.json \
  --method-card method_card.json

# Publish to the leaderboard
mt-eval publish eval/logs/harness/your-run-card.json
```

Si no se proporcionó `--method-card`, `mt-eval publish` inicia un asistente interactivo que lo guía a través de la descripción de su método.

El marcador muestra:
- **Distintivo de clase** — indicador visual (por ejemplo, "pipeline", "coached-llm")
- **Clase de dependencia** — S/O/A1/A2 (consulte [Validez de Método y Clases de Dependencia](#method-validity-and-dependency-classes)); los métodos A2 llevan una bandera "dependencia externa"
- **Nombre del método** — de la tarjeta de método
- **Herramientas utilizadas** — enumeradas de la tarjeta de método
- **Indicador de código abierto**

Cuando no se adjunta ninguna tarjeta de método, el marcador muestra configuración nativa del arnés (modelo, versión de mensaje, temperatura, herramientas habilitadas).

:::danger NO ENTRENE con datos de evaluación
Los métodos cuyo proceso de desarrollo incluyó exposición al conjunto de datos de evaluación — como datos de entrenamiento, ejemplos de pocos disparos, entradas de diccionario o material de ajuste de mensaje — serán **descalificados** del marcador. Consulte [Evaluación de MT](/docs/leaderboard/rules) para lo que distingue un buen método de uno malo.
:::

---

## Véase También

- [Evaluación de MT](/docs/leaderboard/rules) — descripción general, valor del marcador y orientación de método bueno/malo
- [Arnés de Evaluación](/docs/specifications/harness) — cómo ejecutar evaluaciones
- [Conjuntos de Datos de Evaluación](/docs/leaderboard/datasets) — conjuntos de datos disponibles (EDTeKLA, FLORES+)
- [Especificación de Tarjeta de Ejecución](/docs/specifications/run-card) — esquema JSON de tarjeta de ejecución
- [Especificación de Complemento](https://champollion.dev/docs/reference/plugin-spec) — interfaz de complemento del lado de champollion
- [Marcador de Método](https://champollion.dev/leaderboard) — puntuaciones de evaluación en vivo
- [Especificación de Evaluación](/docs/specifications/benchmark) — protocolo de evaluación, formato de corpus, esquema de tarjeta de ejecución
- [Especificación de Puntuación](/docs/specifications/scoring) — SSOT para métricas, pesos compuestos y niveles de calidad