---
sidebar_position: 3
title: "Del Benchmark al Uso Diario: La Ruta de Edición Posterior"
slug: '/perspectives/from-benchmark-to-daily-use'
description: "Cómo un método de traducción evaluado en benchmark se convierte en un flujo de trabajo de traducción comunitaria: borrador automático, edición posterior por hablante fluido, texto publicado — con umbrales de calidad honestos en cada paso."
related:
  - label: "Deploy to Production"
    to: /docs/getting-started/deploy-to-production
    kind: guide
    note: "From proven method to live translation"
  - label: "Cookbook: Partial Translation (Human + Machine)"
    to: /docs/tutorials/partial-translation
    kind: cookbook
  - label: "Scoring Specification"
    to: /docs/specifications/scoring
    kind: spec
    note: "The quality thresholds behind the path"
  - label: "Translation Is Not Revitalization"
    to: /docs/perspectives/translation-is-not-revitalization
    kind: position
---
# Del Benchmark al Uso Diario: La Ruta de la Posedición

> **La versión corta.** Una puntuación en el ranking no es un producto. La ruta desde "este método obtiene 0.78" hasta "la oficina de la banda publica documentos en la lengua cada semana" pasa por exactamente un flujo de trabajo: la máquina produce un borrador, un hablante fluido lo corrige, y solo el texto corregido se publica. Cada umbral de calidad en nuestras especificaciones está calibrado para ese flujo de trabajo — no para la salida de máquina sin supervisión, que no respaldamos para ninguna lengua en esta plataforma.

A veces la gente pregunta cuándo un método de traducción será "lo suficientemente bueno para simplemente usarlo". Para las lenguas que esta Arena sirve, esa pregunta tiene una trampa. La respuesta honesta es que el estándar que vale la pena perseguir no es "lo suficientemente bueno para publicar sin revisar" — es **"lo suficientemente bueno que revisar un borrador sea mejor que traducir desde cero."** Ese estándar es mucho más bajo, es medible, y cruzarlo cambia lo que una oficina de traducción comunitaria puede producir en una semana.

---

## El flujo de trabajo, de principio a fin

```
 English source document
        │
        ▼
 Machine draft  ←  a benchmarked, community-owned method
        │
        ▼
 Fluent-speaker post-edit  ←  the human gate; nothing skips it
        │
        ▼
 Published text  ←  carries human approval, not a machine score
        │
        ▼
 (Optional, community-controlled) corrections become
 data that improves the next version of the method
```

Tres cosas a notar:

1. **La máquina nunca publica.** La unidad de salida es un borrador. El paso de corrección del hablante no es aseguramiento de calidad añadido al final — es el flujo de trabajo.
2. **El tiempo del hablante es el recurso que se optimiza.** Un método es mejor que otro método exactamente en la medida en que deja menos para que el hablante corrija. La investigación sobre posedición para lenguas bien dotadas de recursos encuentra consistentemente que es más rápida que traducir desde cero con calidad de TA moderada (Plitt & Masselot 2010; Green, Heer & Manning 2013, ambos citados con enlaces en [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization)). Si eso se sostiene para lenguas polisintéticas es precisamente lo que el benchmark existe para descubrir — lo tratamos como una hipótesis a verificar por lengua, no como una suposición.
3. **El ciclo de retroalimentación es de propiedad comunitaria.** Cada documento corregido es potencial dato de entrenamiento y coaching — y pertenece a la comunidad, para retroalimentar (o no) en sus términos bajo las reglas de [soberanía de datos](/docs/sovereignty/data-sovereignty). El mecanismo de retroalimentación es un objetivo de diseño de la plataforma, aún no una característica construida; véase [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections) para cómo se pretende que funcionen las correcciones y la procedencia.

## Qué significan los niveles de calidad para el uso real

El ranking califica métodos en un compuesto de métricas automatizadas ([Scoring Specification](/docs/specifications/scoring)), y las puntuaciones se asignan a niveles nombrados. Aquí está la traducción honesta de esos niveles a términos de uso diario:

| Nivel (compuesto) | Qué significa para la ruta de posedición |
|---|---|
| **Baseline** (0.00–0.30) | No utilizable para nada. La salida es en gran medida no la lengua objetivo. Útil solo como piso de investigación. |
| **Emerging** (0.30–0.50) | Aún no es una herramienta de borrador. Aparecen fragmentos correctos, pero un hablante gastaría más tiempo corrigiendo que escribiendo fresco. |
| **Functional** (0.50–0.70) | El primer nivel donde la posedición *podría* superar la traducción desde cero para textos fáciles — vale la pena pilotear con un hablante, no vale la pena depender de ello. Permanecen errores morfológicos frecuentes. |
| **Deployable** (0.70–0.85) | El nivel objetivo para el flujo de trabajo anterior: borradores donde la mayoría de la morfología es correcta y un hablante fluido puede corregir significativamente más rápido que retraducir. **"Deployable" significa deployable *en un flujo de trabajo de posedición* — nunca "publicar sin revisar."** |
| **Fluent** (0.85–1.00) | Aproximándose a traducción humana competente; errores raros y menores. El paso de revisión permanece — solo se vuelve más rápido. |

Dos reglas de honestidad estructural se sitúan encima de esta tabla, directamente de la [Benchmark Specification §5 y §7](/docs/specifications/benchmark#5-quality-tiers):

- **Los niveles automatizados son etiquetas provisionales, no veredictos.** Son nominaciones para revisión humana. Los umbrales serán recalibrados conforme se acumulan datos de validación de hablantes, y pueden ubicarse diferentemente para diferentes lenguas.
- **Ningún método puede reclamar Deployable o superior sin revisión comunitaria.** Una muestra estratificada de su salida va a hablantes bilingües, quienes califican cada traducción como *rechazar / gist / aceptable / excelente*. La organización de gobernanza — no el ranking — decide si el método avanza.

Para comparación, el umbral del [Founder's Prize](/docs/specifications/prizes) (compuesto ≥ 0.80, ≥99% palabras morfológicamente válidas, ≥70% hablantes calificando aceptable-o-mejor) describe un método cuyos errores restantes son *errores de lengua real* — inflexión incorrecta, no palabras fabricadas. Eso es lo que "un borrador que vale la pena el tiempo de un hablante" se ve en números.

## De un método ganador a una oficina funcional

Supongamos que un método cruza esas puertas. Los pasos restantes son organizacionales, y están especificados en lugar de improvisados:

1. **La propiedad se transfiere.** El código del método se convierte en propiedad de la organización de gobernanza de la comunidad — el desarrollador mantiene derechos de atribución y publicación ([Ownership Transfer](/docs/sovereignty/ownership-transfer)).
2. **El método se convierte en un servicio.** Se empaqueta como un plugin y se sirve a través de la plataforma de despliegue, con la comunidad controlando acceso, precios y usos permitidos ([Deploy to Production](/docs/getting-started/deploy-to-production)).
3. **Los traductores lo conectan a su día.** Una oficina de traducción apunta su flujo de trabajo de documentos existente al API del método: texto fuente adentro, borrador afuera, posedición, publicación. El texto publicado lleva el nombre y autoridad del traductor — la máquina es una herramienta en su escritorio, como un diccionario.
4. **Los ingresos siguen al uso.** Desarrolladores externos que usan el método pagan tasas medidas, y el 90% de esos ingresos fluyen a la organización de gobernanza ([The Economic Model](/docs/sovereignty/economic-model)) — que puede financiar más horas de traductor, cerrando el ciclo.

## Dónde está esto hoy

Claramente: la ruta completa está especificada de principio a fin, y parcialmente construida. El arnés de evaluación, métricas, tarjetas de ejecución y ranking público existen; el corpus de desarrollo de Plains Cree y un premio activo existen; la plataforma de despliegue existe. La interfaz de revisión comunitaria, la caja de arena de evaluación y el ciclo de retroalimentación de texto corregido están especificados pero aún no operacionales — las especificaciones los marcan como planeados, y nosotros también. Ningún método ha completado aún el viaje completo desde benchmark hasta uso diario comunitario. Ese viaje es la definición de éxito del proyecto, que es exactamente por qué no lo reclamaremos temprano.

---

## Qué significa esto para usted

:::info Si es miembro de la comunidad
Una insignia "Deployable" en un ranking nunca significa que una máquina publicará en su lengua sin supervisión — significa que un generador de borradores puede estar listo para *audicionarse* para sus traductores, en sus términos, con sus hablantes como jueces (pagados — véase [How Speakers Get Paid](/docs/perspectives/how-speakers-get-paid)). Si su comunidad ejecuta una oficina de traducción, la pregunta relevante a traernos es: "¿cómo se vería un piloto, y quién revisa la salida?"
:::

:::info Si es investigador
El marco de posedición cambia lo que vale la pena medir: tiempo-a-texto-aceptable con un hablante en el ciclo, no solo puntuación compuesta. Las métricas de la Arena son proxies para eso ([Scoring Specification §1](/docs/specifications/scoring)), y estudios de posedición por lengua para lenguas morfológicamente complejas son una brecha de investigación abierta que esta infraestructura está diseñada para apoyar.
:::

:::info Si es constructor
Optimice para el editor, no para la métrica. Un método que produce palabras reales con inflexiones ocasionalmente incorrectas es corregible en segundos por un hablante; un método que alucina formas plausibles envenena todo el flujo de trabajo — que es por qué la validez morfológica está tan fuertemente controlada aquí. Comience en [Submit a Method](/docs/getting-started/submit-a-method), y lea la [Method Interface](/docs/specifications/methods) para lo que eventualmente entregará si gana.
:::

## Véase también

- [Translation Is Not Revitalization](/docs/perspectives/translation-is-not-revitalization) — por qué la puerta humana es el punto, no una limitación
- [Reporting Errors and Owning Corrections](/docs/perspectives/reporting-errors-and-owning-corrections) — qué sucede cuando el texto publicado es incorrecto de todas formas
- [Benchmark Specification §7](/docs/specifications/benchmark#7-human-validation) — la puerta de validación humana, formalmente