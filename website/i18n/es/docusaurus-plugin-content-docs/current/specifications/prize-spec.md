---
sidebar_position: 8
title: "Especificación del Premio"
slug: '/specifications/prizes'
related:
  - label: "How Speakers Get Paid"
    to: /docs/perspectives/how-speakers-get-paid
    kind: position
    note: "The plain-language version of these numbers"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "MT Evaluation Rules"
    to: /docs/leaderboard/rules
    kind: doc
  - label: "Submit a Method"
    to: /docs/getting-started/submit-a-method
    kind: guide
---
# Especificación de Premios

> **Propósito.** Este documento define la estructura del fondo de premios, las condiciones de umbral, el proceso de reclamación y las reglas para MT Eval Arena. Especifica exactamente qué significa "capaz de traducción automática" en términos medibles, y bajo qué condiciones se libera el dinero del premio. Este documento hace referencia a SCORING_SPEC para definiciones de métricas y BENCHMARK_SPEC para protocolo de evaluación — no las duplica.
>
> **Estado:** EN VIVO. El Founder's Prize (§2.1) está financiado y activo.
>
> Última actualización: 2026-06-04

---

## 1. Filosofía

### 1.1 Los Premios Recompensan Avances, No Participación

El dinero del premio se libera solo cuando un método demuestra lograr un umbral de capacidad definido. No hay premios por participación, premios para subcampeones o pagos de consolación. Si nadie supera la barra, nadie recibe pago. Esto es intencional — significa que los patrocinadores solo pagan por resultados que realmente funcionan.

### 1.2 La Validación Comunitaria Es Innegociable

Las métricas automatizadas son aproximaciones (SCORING_SPEC §1.1). Un método puede obtener buenas puntuaciones en chrF++ y aceptación FST mientras produce resultados que ningún hablante aceptaría. **Cada reclamación de premio requiere validación comunitaria** — hablantes bilingües deben confirmar que el resultado es utilizable. Esta es la puerta de validación humana (BENCHMARK_SPEC §7).

### 1.3 La Transferencia de Propiedad Es Parte del Acuerdo

Los métodos que reclaman un premio están sujetos a la cláusula de transferencia de propiedad (BENCHMARK_SPEC §8.3). El desarrollador conserva los derechos de atribución y publicación. La organización de gobernanza obtiene el derecho de usar, modificar, distribuir y monetizar el método para su idioma. Esto no es una penalización — es el punto. El dinero del premio financia la creación de tecnología que pertenece a la comunidad de hablantes.

### 1.4 Prevención de Manipulación

Los umbrales de premios se definen contra **evaluación de estándar de oro** (conjunto de prueba secreto, ejecutado por la organización de gobernanza en sandbox). Los desarrolladores nunca ven los datos de prueba. Esto se aplica arquitectónicamente — no es una política que dependa del honor. Véase BENCHMARK_SPEC §8.2.

### 1.5 Licencias de Corpus: Los Corpus No Comerciales Se Mantienen Fuera de la Pista de Premios

Algunos corpus utilizados durante el desarrollo del método llevan licencias no comerciales — por ejemplo, el corpus EdTeKLA Cree Language Textbook es **CC BY-NC-SA 4.0**. Estos corpus son **solo para la pista de investigación/desarrollo**:

1. **Los corpus de estándar de oro de premios no deben incrustar contenido de corpus con licencia NC.** Los segmentos de prueba de estándar de oro son originales encargados por la comunidad (véase Corpus Partnership Strategy) — creados por humanos para el premio, con derechos aclarados para evaluación e implementación comercial desde el inicio.
2. **Un método que reclama un premio no debe incrustar contenido de corpus con licencia NC** (p. ej., como datos de entrenamiento, ejemplos incrustados o tablas de búsqueda). El método transferido está destinado a implementación comercial por la organización de gobernanza (BENCHMARK_SPEC §8.3, Method Submission Agreement §6); el contenido con licencia NC dentro de él contaminaría esa implementación.
3. **Los desarrolladores pueden usar libremente corpus con licencia NC para desarrollar y autoevaluar** — para eso es la pista de desarrollo. La restricción se aplica a lo que se envía y lo que se implementa, no a cómo un desarrollador aprende.

### 1.6 Clases de Dependencia Controlan la Elegibilidad de Premios

Toda evaluación de premios ocurre en un sandbox (§1.4), y los métodos ganadores se transfieren a la organización de gobernanza (§1.3). Ambos hechos imponen la misma restricción: **todo de lo que depende un método debe ser algo que el desarrollador tenga derecho a poner en el sandbox y transmitir a la comunidad.** Cada envío declara una clase de dependencia — definida en la [especificación de interfaz de método](/docs/specifications/methods#method-validity-and-dependency-classes), con términos de admisibilidad en Method Submission Agreement §2.6 — y la elegibilidad sigue la clase:

| Clase de dependencia | ¿Elegible para premio? | Condiciones |
|------------------|----------------|------------|
| **S** — autónomo | ✅ Sí | Ninguna más allá de las condiciones de umbral en §2 |
| **O** — abierto externo (p. ej., FST AGPL reflejado en envío) | ✅ Sí | Artefactos fijados e incluidos en el envío; las licencias permiten transferencia comunitaria; términos copyleft preservados (la comunidad recibe los mismos derechos que la licencia otorga a todos) |
| **A1** — inferencia LLM sustituible | ⚠️ Condicional | Modelo declarado, fijado y sustituible (debe ejecutarse contra un modelo de peso abierto alojado por la comunidad); evaluación enrutada a través de la puerta de entrada LLM del sandbox (🔲 planeado — los métodos A1 no pueden producir puntuaciones de estándar de oro hasta que la puerta esté operativa); la transferencia transmite la receta completa (indicaciones, entrenamiento, código), no el modelo |
| **A2** — API de servicio/datos externos no sustituibles | ❌ Aún no | Inelegible hasta que el titular de derechos otorgue permisos de inclusión en sandbox y transferencia. Permitido en la tabla de clasificación abierta con una bandera visible de "dependencia externa" |
| **X** — contenido incluido sin derechos | ❌ Nunca | Inadmisible en todas las pistas |

La clase de un método es la clase más restrictiva entre sus dependencias declaradas. Las dependencias no declaradas de cualquier clase son descalificantes (§5).

---

## 2. Fondos de Premios Activos

### 2.1 El Founder's Prize — EN→Plains Cree (nêhiyawêwin)

| Campo | Valor |
|-------|-------|
| **Fondo de premios** | **$10,000 CAD** |
| **Par de idiomas** | Inglés → Plains Cree (EN→CRK) |
| **Financiado por** | Fundador del proyecto Champollion |
| **Estado** | **ACTIVO** — aceptando envíos |
| **Se abre** | Cuando el corpus de estándar de oro y la organización de gobernanza estén en su lugar |
| **Vence** | Sin vencimiento. El premio permanece activo hasta ser reclamado o explícitamente retirado. |

#### Condiciones de Umbral

Un método reclama el Founder's Prize cumpliendo **TODAS** las siguientes condiciones simultáneamente:

| # | Condición | Métrica | Umbral | Justificación |
|---|-----------|--------|-----------|-----------|
| 1 | **Puntuación compuesta** | `composite` (SCORING_SPEC §4) | **≥ 0.80** | Entre Implementable (0.70) y Fluido (0.85). Requiere alta calidad en todas las dimensiones de métrica — no solo validez morfológica. |
| 2 | **Aceptación FST** | `fst_acceptance_rate` (SCORING_SPEC §2.2) | **≥ 0.99 (99%+)** | Efectivamente todas las palabras de salida deben ser formas morfológicamente válidas reconocidas por el FST de GiellaLT. La tolerancia del 1% representa casos límite (nombres propios, neologismos, préstamos) que el FST puede legítimamente no cubrir. Esta es la puerta de control de calidad definitiva para MT polisintética — si el FST rechaza más del 1% de palabras, el método está produciendo formas que no existen en el idioma. Todo el punto de este premio es comprar un sistema que no mutile las cosas. |
| 3 | **chrF++** | `chrf_plus_plus` (SCORING_SPEC §2.1) | **≥ 55.0** | La superposición de n-gramas de caracteres debe exceder 55 en la escala 0–100. Asegura similitud a nivel de superficie con traducciones de referencia, no solo validez morfológica. |
| 4 | **Validación comunitaria** | Revisión humana (BENCHMARK_SPEC §7) | **≥ 70% "aceptable" o "excelente"** | Una muestra estratificada de salidas (≥30 entradas en niveles de dificultad 2–5) es revisada por ≥2 hablantes bilingües de CRK. Al menos el 70% de las entradas revisadas debe recibir una calificación de "aceptable" o "excelente". |
| 5 | **Evaluación de estándar de oro** | Ejecución en sandbox (BENCHMARK_SPEC §8.2) | **Requerida** | Todas las métricas automatizadas deben calcularse contra el segmento de corpus `gold_standard`, ejecutado por la organización de gobernanza en un entorno aislado. Las puntuaciones del conjunto de desarrollo no cuentan. |
| 6 | **Reproducibilidad** | Coincidencia de huella digital (BENCHMARK_SPEC §3.8) | **±2%** | La organización de gobernanza debe poder re-ejecutar el método y lograr puntuaciones dentro de ±2% de la tarjeta de ejecución enviada. |

> **¿Por qué 99+% FST?** El problema central en la traducción automática para idiomas polisintéticos es la alucinación — los LLM producen cadenas que *parecen* el idioma objetivo pero son morfológicamente inválidas. Un método que produce 95% de salida válida aún tiene 5% de palabras fabricadas — ruido inaceptable para cualquier uso en producción. El umbral de 99%+ exige alucinación casi nula mientras permite el caso raro (un nombre propio que el FST no conoce, un neologismo legítimo). Si un método no puede lograr aceptación FST de 99%+, no ha resuelto el problema.
>
> **¿Por qué 0.80 compuesto?** Esto se sitúa entre Implementable (0.70) y Fluido (0.85). Un método en 0.80 con aceptación FST de 99%+ produce salida donde prácticamente cada palabra es una palabra Cree real *y* la calidad general de la traducción es alta en dimensiones de superficie, estructura y semántica. La puerta de validación comunitaria (condición #4) asegura que esto no sea solo juego de métricas — los hablantes deben confirmar que la salida es genuinamente utilizable.

#### Qué Significa Este Umbral en la Práctica

En compuesto ≥ 0.80 con FST ≥ 0.99 y chrF++ ≥ 55, un hablante bilingüe típicamente vería:

- **Prácticamente cada** palabra de salida es una palabra Cree real (FST valida 99%+ — formas alucinadas casi nulas)
- Las categorías gramaticales principales (persona, número, tiempo) son correctas en la mayoría de entradas
- El orden de palabras es generalmente natural
- El significado se preserva confiablemente
- Los errores restantes son errores de idioma real (inflexión incorrecta, obvención incorrecta, desajustes de animacidad) — no palabras fabricadas
- Un hablante fluido podría usar la salida como un borrador de alta calidad y corregirlo significativamente más rápido que traducir desde cero

Este es un sistema que **no mutila el idioma.** Puede no ser perfecto, pero cada palabra que produce es una palabra real. Ese es el umbral mínimo para traducción automática respetuosa de un idioma polisintético.

---

## 3. Proceso de Reclamación de Premio

### 3.1 Envío

1. El desarrollador envía su método completo y ejecutable a la organización de gobernanza:
   - Todo el código fuente
   - Todas las dependencias (datos de entrenamiento, diccionarios, configuraciones FST, indicaciones)
   - Instrucciones de instalación y ejecución
   - Un README describiendo el enfoque del método
   - Una tarjeta de ejecución del conjunto de desarrollo mostrando puntuaciones aproximadas (para preselección)

2. El desarrollador firma los términos de participación, incluyendo:
   - Cláusula de transferencia de propiedad (BENCHMARK_SPEC §8.3)
   - Declaración de no entrenamiento en datos de evaluación
   - Compromiso de reproducibilidad

### 3.2 Evaluación

1. La organización de gobernanza instala y ejecuta el método en un arnés aislado contra el corpus `gold_standard`
2. Se calculan las métricas automatizadas (compuesto, FST, chrF++, etc.)
3. Si se cumplen los umbrales automatizados (condiciones 1–3), la organización de gobernanza procede a revisión comunitaria
4. Si los umbrales automatizados NO se cumplen, el desarrollador recibe puntuaciones y retroalimentación. No se activa revisión comunitaria.

### 3.3 Revisión Comunitaria

1. Una muestra estratificada de salidas (≥30 entradas, cubriendo niveles de dificultad 2–5) se presenta a hablantes bilingües
2. Mínimo 2 revisores independientes califican cada entrada
3. Escala de calificación: **rechazar** / **esencia** / **aceptable** / **excelente**
4. Si ≥70% de las entradas reciben "aceptable" o "excelente" de ambos revisores, la validación comunitaria pasa

### 3.4 Pago

1. Se cumplen las 6 condiciones
2. La organización de gobernanza confirma el resultado
3. El premio se paga dentro de 30 días de la confirmación
4. La propiedad del método se transfiere según BENCHMARK_SPEC §8.3
5. El resultado se publica en la tabla de clasificación con nivel de verificación "Community Validated"

### 3.5 Envíos Múltiples

- El mismo desarrollador/equipo puede enviar múltiples veces
- Cada envío se evalúa independientemente
- Si un método se mejora y se re-envía, solo la tarjeta de ejecución más reciente cuenta
- El premio se otorga al **primer** método que supera todos los umbrales — no se divide

### 3.6 Envíos de Equipo

- Los equipos y pares de Ancianos-jóvenes son elegibles
- La distribución del premio dentro de un equipo es responsabilidad del equipo
- Todos los miembros del equipo deben firmar los términos de participación
- La atribución en la tabla de clasificación lista todos los miembros del equipo

---

## 4. Fondos de Premios Futuros

El Founder's Prize es la semilla. Fondos de premios adicionales son financiados por patrocinadores. Cada nuevo fondo de premios se documenta como una nueva subsección de §2 con su propio:

- Cantidad y moneda del premio
- Par de idiomas
- Atribución del patrocinador
- Condiciones de umbral (que pueden diferir del Founder's Prize)
- Fecha de vencimiento (si la hay)
- Cualquier condición especial

### 4.1 Plantilla de Premio de Patrocinador

Los patrocinadores financian fondos de premios en cualquier cantidad. Niveles sugeridos:

| Nivel | Cantidad | Umbral Sugerido |
|------|--------|---------------------|
| **Semilla** | $5,000–$15,000 | Implementable (compuesto ≥ 0.70) + validación comunitaria |
| **Avance** | $25,000–$50,000 | Fluido (compuesto ≥ 0.85) + validación comunitaria |
| **Gran Premio** | $100,000+ | Fluido + cobertura de múltiples registros + integración de implementación |

Los patrocinadores también pueden financiar:
- **Recompensas de mejora** — pago fijo por cada mejora de 5 puntos en chrF++ sobre el mejor actual
- **Premios de registro** — premios separados para registros específicos (formal, ceremonial, educativo)
- **Premios de velocidad** — mejor puntuación ajustada por costo (SCORING_SPEC §6.3)

### 4.2 Depósito en Garantía de Fondo de Premios

Todos los fondos de premios se mantienen en depósito en garantía (administrados por el proyecto o un fideicomisario designado) hasta que se cumplan las condiciones de umbral. Si un premio vence sin ser reclamado, los fondos se devuelven al patrocinador o se redirigen a un nuevo fondo de premios a discreción del patrocinador.

---

## 5. Descalificación

Un envío se descalifica si:

1. **Entrenamiento en datos de evaluación.** El método fue expuesto a entradas de corpus `gold_standard` o `held_out`. (Prevenido arquitectónicamente por ejecución aislada — pero si se encuentra evidencia de contaminación, el resultado se anula.)
2. **No reproducible.** La organización de gobernanza no puede reproducir puntuaciones dentro de ±2%.
3. **Dependencias no declaradas o inelegibles.** El método requiere acceso en tiempo de ejecución a servicios externos más allá de lo que su manifiesto de dependencia declara, o su clase de dependencia efectiva es A2 o X (§1.6). La inferencia LLM de Clase A1 declarada enrutada a través de la puerta de entrada de evaluación es permitida; cualquier otra dependencia de red en tiempo de ejecución — y cualquier dependencia no declarada de cualquier clase — es descalificante.
4. **Términos de participación no firmados.** Todos los miembros del equipo deben aceptar la transferencia de propiedad.
5. **Manipulación detectada.** La salida está optimizada para la métrica en lugar de calidad de traducción (detectada por revisión comunitaria y/o verificaciones anti-manipulación según BENCHMARK_SPEC §9.3).

---

## 6. Relación con Otras Especificaciones

| Este Documento | Referencias | Para |
|--------------|-----------|-----|
| §2 condiciones de umbral | SCORING_SPEC §4 (compuesto), §2.1–2.2 (métricas), §5 (niveles) | Definiciones de métricas y escala |
| §2 validación comunitaria | BENCHMARK_SPEC §7 | Protocolo de revisión humana |
| §3 ejecución en sandbox | BENCHMARK_SPEC §8.2 | Mecanismo de soberanía |
| §3 transferencia de propiedad | BENCHMARK_SPEC §8.3 | Términos de transferencia de IP |
| §1.6 clases de dependencia | Especificación de interfaz de método; Method Submission Agreement §2.6; BENCHMARK_SPEC §8.6 | Definiciones de clase, términos de admisibilidad, política de red de sandbox |
| §4 premios ajustados por costo | SCORING_SPEC §6.3 | Fórmula ajustada por costo |

---

## 7. Sincronización Código–Especificación

### 7.1 Fuente Canónica

Este documento (`arena/website/docs/specifications/prize-spec.md`) es la fuente canónica para:
- Definiciones de fondo de premios (§2)
- Condiciones de umbral (§2.x)
- Proceso de reclamación (§3)
- Reglas de descalificación (§5)

### 7.2 Requisitos de Implementación

Cuando se activa un fondo de premios:
1. La interfaz de usuario de la tabla de clasificación debe mostrar premios activos y sus condiciones de umbral
2. Las tarjetas de ejecución que cumplen umbrales automatizados (condiciones 1–3) deben marcarse para revisión comunitaria
3. El campo `quality_tier` en el esquema de tarjeta de ejecución ya captura el nivel ("implementable", "fluido")
4. No se necesitan cambios de código nuevos en el arnés — la especificación de premios es una capa de política sobre puntuación existente

---

*Las estructuras de premios deben ser compatibles con términos de transferencia de propiedad. El ganador puede reclamar el premio, pero el método se convierte en propiedad de la organización de gobernanza si alcanza el nivel Implementable. Esto es intencional — el premio financia la creación de tecnología que pertenece a la comunidad de hablantes.*