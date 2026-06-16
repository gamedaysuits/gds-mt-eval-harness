---
sidebar_position: 7
title: "Marco de Diseño de Corpus"
---
# Marco de Diseño de Corpus de Evaluación

> **Versión:** 1.0  
> **Estado:** Borrador  
> **Propósito:** Una metodología sistemática para construir corpus de evaluación que produzcan evaluaciones de calidad de traducción válidas, confiables y lingüísticamente significativas. Esta es la fuente de verdad sobre cómo se diseñan, construyen y mantienen los conjuntos de datos de evaluación de Champollion.

---

## 1. Principios de Diseño

### 1.1 — ¿Por Qué No Benchmarks Públicos?

Los corpus paralelos públicos (FLORES+, Tatoeba, conjuntos de prueba WMT, OPUS) están disponibles para desarrollo y depuración pero están **excluidos de la evaluación oficial del ranking**. La razón es directa:

**Contaminación.** Los LLMs fronterizos se entrenan en enormes recopilaciones web. Cualquier texto paralelo que haya existido públicamente — especialmente en conjuntos de datos de referencia curados y ampliamente citados — probablemente está en sus datos de entrenamiento. Cuando evalúa GPT-4o en FLORES+ y obtiene 85 chrF++, no puede distinguir "el modelo es bueno traduciendo" de "el modelo memorizó estos pares de oraciones específicos." Esta no es una preocupación teórica — [la investigación ha demostrado](https://arxiv.org/abs/2311.04850) efectos de contaminación medibles en benchmarks de traducción automática.

Para Champollion, esto es crítico porque:
- Nuestro ranking compara principalmente métodos basados en LLM
- Nuestra propuesta de valor es *evaluación honesta y rigurosa*
- Nuestros usuarios objetivo (comunidades lingüísticas) toman decisiones de implementación basadas en estas puntuaciones

### 1.2 — Requisitos Centrales

Todo corpus de evaluación de Champollion debe satisfacer:

| Requisito | Justificación |
|-----------|---------------|
| **Autoría humana** | Sin datos sintéticos. Todo el texto fuente y las traducciones de referencia deben ser escritos por humanos. Los LLMs pueden asistir con alineación y formato pero nunca generar contenido. |
| **No disponible públicamente en forma paralela** | El texto fuente puede ser público; las traducciones de referencia pueden ser públicas; pero el *emparejamiento* específico no debe existir como un corpus paralelo descargable. |
| **Proveniencia rastreada** | Cada entrada debe tener origen documentado: documento fuente, traductor, licencia, fecha. |
| **Informada lingüísticamente** | La cobertura debe guiarse por características tipológicas, no por muestreo aleatorio. |
| **Estratificada por dominio** | Las entradas deben abarcar dominios definidos con representación controlada. |
| **Clasificada por dificultad** | Las entradas deben asignarse a niveles de dificultad (1–5) basados en complejidad estructural. |
| **Controlada por versión** | Las versiones del corpus tienen hash de contenido. Las puntuaciones solo son comparables dentro de la misma versión. |
| **Revisable por la comunidad** | Las traducciones de referencia deben ser revisables por miembros de la comunidad lingüística. |

---

## 2. Selección de Texto Fuente

### 2.1 — Taxonomía de Dominios

Champollion evalúa traducción para **contextos de implementación práctica**, no ejercicios académicos. La taxonomía de dominios refleja tipos de texto del mundo real que encuentran los usuarios de traducción:

| Dominio | Código | Descripción | Fuentes de Ejemplo |
|---------|--------|-------------|-------------------|
| **Interfaz de Software** | `ui` | Etiquetas de botones, elementos de menú, mensajes de error, información sobre herramientas, flujos de incorporación | Cadenas de aplicaciones de código abierto, portales de documentación |
| **Oficial/Administrativo** | `admin` | Documentos gubernamentales, avisos legales, formularios, declaraciones de política | Publicaciones gubernamentales públicas, documentos municipales |
| **Educativo** | `edu` | Contenido de libros de texto, materiales de lecciones, texto instructivo | Materiales educativos publicados, guías de enseñanza |
| **Narrativo/Literario** | `lit` | Historias, textos culturales, transcripciones de historia oral | Libros publicados, archivos culturales (con permiso) |
| **Conversacional** | `conv` | Diálogo, intercambios tipo chat, comunicación escrita informal | Corpus de diálogo publicados, guiones, transcripciones de entrevistas |
| **Técnico** | `tech` | Documentación de API, archivos README, especificaciones técnicas | Documentación de proyectos de código abierto |
| **Salud/Médico** | `health` | Información médica dirigida a pacientes, mensajería de salud pública | Publicaciones de salud gubernamentales |
| **Noticias/Periodístico** | `news` | Artículos de noticias, comunicados de prensa, asuntos actuales | Periódicos comunitarios, medios indígenas |

### 2.2 — Distribución de Dominios

Un corpus de evaluación estándar debe apuntar a la siguiente distribución. Los porcentajes exactos pueden variar según el par de idiomas basándose en qué tipos de texto son más relevantes para la comunidad objetivo:

| Dominio | % Objetivo | Justificación |
|---------|-----------|---------------|
| Interfaz de Software | 25% | Contexto de implementación principal para usuarios de CLI de champollion |
| Oficial/Administrativo | 15% | Traducción de alto riesgo con implicaciones legales |
| Educativo | 15% | Caso de uso central para revitalización lingüística |
| Narrativo/Literario | 10% | Prueba de matiz cultural y registro literario |
| Conversacional | 10% | Prueba de registro informal y patrones de habla natural |
| Técnico | 10% | Prueba de precisión y consistencia terminológica |
| Salud/Médico | 10% | Alto riesgo, prueba de vocabulario específico del dominio |
| Noticias/Periodístico | 5% | Prueba de vocabulario contemporáneo y registro neutral |

### 2.3 — Criterios de Selección de Fuente

Al seleccionar textos fuente para un nuevo corpus:

1. **Compatibilidad de licencia.** El texto fuente debe estar bajo una licencia que permita su uso en un corpus de evaluación. Prefiera CC BY, CC BY-SA, o dominio público. Documente la licencia.

2. **Actualidad.** Prefiera textos publicados en los últimos 10 años. El idioma evoluciona — especialmente vocabulario alrededor de tecnología, gobierno y medicina.

3. **Diversidad de registro.** Dentro de cada dominio, busque textos en diferentes niveles de formalidad. Un comunicado de prensa gubernamental (formal) y una publicación de redes sociales gubernamentales (informal) son ambos dominio `admin` pero registros diferentes.

4. **Relevancia cultural.** Para idiomas indígenas y minoritarios, priorice textos que importen a la comunidad — documentos de gestión de tierras, materiales educativos en el idioma, textos de preservación cultural — sobre textos que simplemente existan en forma paralela.

5. **Sin fuentes traducidas por máquina.** Si un documento "paralelo" fue creado ejecutando el original a través de Google Translate y luego editándolo, NO es aceptable como traducción de referencia. La referencia debe ser una traducción humana independiente.

---

## 3. Sistema de Niveles de Dificultad

### 3.1 — Definiciones de Nivel

Cada entrada se asigna a un nivel de dificultad (1–5) basado en la complejidad estructural del *texto fuente*, no la dificultad de traducción (que varía según el método).

| Nivel | Etiqueta | Características Estructurales |
|-------|----------|------------------------------|
| 1 | **Elemental** | Oraciones simples. Cláusula única. Tiempo presente. Vocabulario común. Sin idiomas. Sin estructuras incrustadas. |
| 2 | **Intermedio** | Oraciones compuestas. Dos cláusulas unidas por conjunción. Tiempo pasado/futuro. Algo de vocabulario de dominio. |
| 3 | **Avanzado** | Oraciones complejas. Cláusulas subordinadas, cláusulas relativas. Tiempos mixtos. Terminología específica del dominio. Voz pasiva. |
| 4 | **Experto** | Múltiples cláusulas incrustadas. Registro legal/técnico. Estructuras condicionales. Conceptos abstractos. Referencias culturales. |
| 5 | **Extremo** | Prosa densa con múltiples desafíos simultáneos: subordinación anidada, referencia de pronombre ambigua, idiomas culturales, registro mixto, vocabulario raro. |

### 3.2 — Factores de Dificultad Informados Lingüísticamente

Más allá de la complejidad estructural, la dificultad se modula por **distancia tipológica** entre el idioma fuente y objetivo. Estos factores se extraen de características tipológicas WALS y datos de clasificación de la tarjeta de idioma:

| Factor | Baja Dificultad | Alta Dificultad |
|--------|-----------------|-----------------|
| **Orden de palabras** | Mismo orden básico (p. ej., SVO→SVO) | Orden básico diferente (p. ej., SVO→SOV) |
| **Tipo morfológico** | Tipo similar (p. ej., analítico→analítico) | Tipo diferente (p. ej., analítico→polisintético) |
| **Género gramatical** | Mismo sistema o sin género | Fuente sin género, objetivo con género complejo |
| **Honorífico/registro** | Sin marcado de registro | Objetivo con sistema de registro complejo (p. ej., japonés, coreano) |
| **Escritura** | Misma escritura | Escritura diferente (transliteración requerida) |
| **Animacidad** | Sin distinción de animacidad | Objetivo con acuerdo basado en animacidad (p. ej., Cree) |
| **Evidencialidad** | Sin evidencialidad | Objetivo marca fuente de información gramaticalmente |

### 3.3 — Distribución de Nivel

Un corpus estándar debe tener aproximadamente:

| Nivel | % Objetivo | Justificación |
|-------|-----------|---------------|
| 1 | 15% | Establece línea base — incluso métodos malos deberían manejar estos |
| 2 | 25% | Traducción práctica de pan y mantequilla |
| 3 | 30% | Donde las diferencias de calidad del método se hacen visibles |
| 4 | 20% | Separa métodos buenos de excelentes |
| 5 | 10% | Prueba de techo — muy pocos métodos manejarán estos bien |

---

## 4. Calidad de Traducción de Referencia

### 4.1 — Requisitos del Traductor

Las traducciones de referencia deben ser producidas por humanos que sean:

1. **Hablantes fluidos** del idioma objetivo (L1 o equivalente)
2. **Alfabetizados** en idioma fuente e idioma objetivo
3. **Conscientes del dominio** para el dominio del texto (traductor médico para textos de salud, etc.)
4. **Independientes** — el traductor no debe tener acceso a ninguna salida de traducción automática para el mismo texto durante la traducción

### 4.2 — Instrucciones de Traducción

Todo traductor recibe instrucciones que incluyen:

- El **registro** a usar (formal, conversacional, etc.)
- La **audiencia objetivo** (público general, especialistas, niños, etc.)
- Cualquier **convención terminológica** específica de la comunidad lingüística
- Instrucción explícita: "Traduzca el significado, no las palabras. Una traducción que suene natural es más valiosa que una literal."

### 4.3 — Aseguramiento de Calidad

1. **Traducción dual.** Idealmente, cada entrada tiene dos traducciones de referencia independientes de diferentes traductores. Donde esto no sea factible, priorice traducción dual para Niveles 4–5.

2. **Revisión comunitaria.** Las traducciones de referencia deben ser revisadas por al menos un hablante adicional que no produjo la traducción.

3. **Variantes aceptables.** Para cada referencia, documente variantes aceptables conocidas (orden de palabras, convenciones ortográficas, formas dialectales). Estas alimentan la métrica `equivalent_match_rate`.

### 4.4 — Qué Hace una Mala Referencia

| Problema | Por Qué Invalida la Evaluación |
|----------|-------------------------------|
| Traducida por máquina y luego editada | La edición preserva estructura de traducción automática; penaliza métodos que producen traducciones más naturales |
| Traducida por un aprendiz, no un hablante fluido | La referencia puede contener errores que penalicen salida de traducción automática correcta |
| Demasiado literal | Las traducciones naturales puntúan mal contra referencias literales |
| Interpretación única válida para fuente ambigua | Penaliza interpretaciones alternativas válidas |

---

## 5. Prevención de Contaminación

### 5.1 — Modelo de Amenaza de Contaminación

| Amenaza | Descripción | Mitigación |
|---------|-------------|-----------|
| **Superposición de datos de entrenamiento** | LLMs entrenados en el corpus paralelo | No publique el corpus paralelo públicamente |
| **Fuga de pocos ejemplos** | El autor del método usa entradas de evaluación como ejemplos de pocos disparos | Verificación de huella digital: las entradas en el prompt se detectan y se marcan |
| **Contaminación indirecta** | El texto fuente existe en datos de entrenamiento de LLM (monolingüe) | Aceptable — se espera texto fuente monolingüe. El *emparejamiento* debe ser novedoso. |
| **Contaminación de multitud** | Los revisores comunitarios comparten entradas públicamente | Los términos de licencia prohíben redistribución del corpus paralelo |

### 5.2 — Niveles de Secreto del Corpus

| Nivel | Visibilidad | Uso |
|-------|-------------|-----|
| **Conjunto de desarrollo público** | Completamente público | Desarrollo de método, depuración, pruebas de regresión. Las puntuaciones NO se publican en el ranking. |
| **Conjunto de evaluación retenido** | Texto fuente visible, referencias secretas | Evaluación oficial del ranking. Los métodos reciben texto fuente y devuelven traducciones; la puntuación ocurre del lado del servidor. Las referencias nunca se exponen al método. |
| **Conjunto de estándar de oro** | Completamente secreto, controlado por la comunidad | Evaluación validada por la comunidad. Gestionado por organización de gobernanza. Usado para verificación de nivel "Validado por la Comunidad". |

### 5.3 — Política de Rotación

Los corpus de evaluación deben **rotarse** periódicamente:

1. Después de que un corpus haya estado en uso durante 12 meses, comience a construir un reemplazo
2. Retire el corpus antiguo al estado de "conjunto de desarrollo" (público)
3. Promueva el nuevo corpus a estado de "conjunto de evaluación retenido"
4. Esto previene contaminación gradual a través de optimización iterativa contra un objetivo fijo

---

## 6. Flujo de Trabajo de Construcción de Corpus

### 6.1 — Proceso Paso a Paso

```
Step 1: Language Pair Selection
    └─ Identify target language, read language card
    └─ Review typological features (WALS), contact influences, scripts
    └─ Identify which difficulty factors apply

Step 2: Source Text Curation
    └─ Identify candidate source documents per domain
    └─ Verify licenses
    └─ Extract candidate sentences/segments
    └─ Classify by domain and preliminary difficulty tier

Step 3: Segment Selection
    └─ Sample segments to match domain distribution (§2.2)
    └─ Sample segments to match difficulty distribution (§3.3)
    └─ Ensure linguistic phenomenon coverage (§6.2)
    └─ Target minimum corpus size (§6.3)

Step 4: Reference Translation
    └─ Assign segments to qualified translators
    └─ Provide translation brief
    └─ Collect translations
    └─ Dual-translate Tier 4–5 entries

Step 5: Quality Assurance
    └─ Community review of references
    └─ Document acceptable variants
    └─ Flag and resolve disagreements

Step 6: Metadata & Packaging
    └─ Assign final difficulty tiers
    └─ Add provenance metadata per entry
    └─ Content-hash the corpus for versioning
    └─ Package as corpus JSON per harness spec

Step 7: Registration
    └─ Register in Supabase datasets table
    └─ Add to ATTRIBUTION.md if new sources used
    └─ Document in arena website
```

### 6.2 — Cobertura de Fenómenos Lingüísticos

Todo corpus debe incluir entradas que prueben fenómenos lingüísticos específicos relevantes para el par de idiomas. Estos se extraen de los campos `linguisticChallenges` y `contactInfluences` de la tarjeta de idioma:

**Fenómenos universales (todos los pares de idiomas):**
- Resolución de pronombre (antecedentes ambiguos)
- Negación (simple, doble, alcance)
- Cuantificadores (todos, algunos, ninguno, la mayoría)
- Expresiones temporales (fechas relativas, duraciones)
- Entidades nombradas (personas, lugares, organizaciones)
- Números y medidas
- Listas y enumeración

**Fenómenos específicos del par (de la tarjeta de idioma):**
- Para objetivos polisintéticos: morfología verbal compleja, incorporación
- Para objetivos con género: acuerdo de género, referencia neutra/inclusiva
- Para objetivos SOV: verbos finales de cláusula, posposiciones
- Para idiomas tonales: distinciones de significado dependientes del tono
- Para idiomas honoríficos: marcadores de registro, contexto social
- Para idiomas de contacto: límites de cambio de código, integración de préstamos

### 6.3 — Tamaño Mínimo de Corpus

La confiabilidad estadística requiere conteos mínimos de entradas. Estos se basan en requisitos de intervalo de confianza bootstrap pareado (de `significance.py`):

| Propósito | Entradas Mínimas | Recomendado |
|-----------|-----------------|-------------|
| Conjunto de desarrollo | 50 | 100–200 |
| Conjunto de evaluación retenido | 100 | 200–500 |
| Conjunto de estándar de oro | 200 | 500+ |
| Mínimo por dominio | 10 | 25+ |
| Mínimo por nivel | 10 | 20+ |

**¿Por qué 100 mínimo para evaluación?** Con menos de ~100 entradas, las pruebas de significancia bootstrap pareadas (1.000 remuestreos) no pueden detectar confiablemente diferencias menores a ~5 puntos chrF++. Con 200+ entradas, podemos detectar diferencias de ~2 puntos a p<0,05.

---

## 7. Formato JSON de Corpus

Cada entrada del corpus sigue la especificación del arnés:

```json
{
  "id": "edtekla-dev-v1-042",
  "source": "The school board will meet on Tuesday to discuss the new curriculum.",
  "reference": "ᑭᓯᑭᓄᐦᐊᒫᑐᐏᓐ ᑲ ᐃᔑ ᐱᒥᐸᔨᐦᑕᐦᒃ ᑭᔅᑭᓄᐦᐊᒫᑐᐏᓇ ᐁ ᐃᔑ ᒫᒥᑐᓀᔨᐦᑕᐦᒃ ᐅᔥᑭ ᑭᔅᑭᓄᐦᐊᒫᑫᐏᓂᔭ ᓂᔓ ᑭᔑᑲᐤ",
  "acceptable_variants": [
    "ᑭᔅᑭᓄᐦᐊᒫᑐᐏᓐ ᓂᔓ ᑭᔑᑲᐤ ᑲ ᐃᔑ ᒫᒥᑐᓀᔨᐦᑕᐦᒃ ᐅᔥᑭ ᑭᔅᑭᓄᐦᐊᒫᑫᐏᓂᔭ"
  ],
  "domain": "edu",
  "difficulty": 3,
  "phenomena": ["temporal_expression", "named_entity", "future_tense"],
  "provenance": {
    "source_doc": "EdTeKLA Module 4, Unit 7",
    "source_license": "CC BY-NC-SA 4.0",
    "translator": "anonymous-speaker-001",
    "translator_qualification": "L1 Plains Cree, certified translator",
    "translation_date": "2025-11-15",
    "reviewer": "anonymous-speaker-002",
    "review_date": "2025-12-01"
  }
}
```

---

## 8. Medidas Anti-Juego

### 8.1 — Integridad del Corpus

| Medida | Implementación |
|--------|----------------|
| **Hash de contenido** | Versión del corpus = SHA-256 de IDs de entrada ordenados + referencias. Cualquier modificación produce una nueva versión. |
| **Huella digital de entrada** | Cada entrada tiene un ID derivado del contenido. Si alguien envía resultados contra un corpus modificado, la huella digital no coincidirá. |
| **Aplicación retenida** | Para evaluación oficial, los métodos reciben SOLO texto fuente. Las referencias nunca se exponen. La puntuación ocurre del lado del servidor. |
| **Cronograma de rotación** | Los corpus rotan anualmente para prevenir optimización a largo plazo contra un objetivo fijo. |

### 8.2 — Integridad de Envío

| Medida | Implementación |
|--------|----------------|
| **Huella digital determinista** | La configuración de ejecución (modelo, temperatura, prompt, versión de corpus) se codifica. Las configuraciones idénticas producen huellas digitales idénticas. |
| **Detección de selección selectiva** | Los remitentes deben divulgar todas las ejecuciones, no solo la mejor. Múltiples envíos con la misma huella digital se marcan. |
| **Verificación de contaminación** | Si las entradas de evaluación aparecen textualmente en el prompt o datos de entrenamiento del método, el envío se descalifica. |

---

## 9. Corpus Existentes

### 9.1 — Conjunto de Desarrollo EDTeKLA v1

| Propiedad | Valor |
|-----------|-------|
| **ID** | `edtekla-dev-v1` |
| **Par** | EN → CRK (Cree de las Llanuras, SRO) |
| **Entradas** | 404 (`master_corpus.json`: 62 oro + 342 libro de texto); 548 total disponibles |
| **Dominios** | Educativo (100%) |
| **Niveles** | 1–5 (distribución TBD por auditoría de entrada) |
| **Licencia** | CC BY-NC-SA 4.0 |
| **Estado** | Conjunto de desarrollo (público) |

**Limitaciones:** Dominio único (solo educativo). Sin estratificación de dominio. Las asignaciones de nivel pueden necesitar auditoría. El tamaño pequeño del corpus limita el poder estadístico para pruebas de significancia.

### 9.2 — Corpus Planeados

| Corpus | Par | Estado | Propietario |
|--------|-----|--------|-------------|
| Corpus personalizado EN → TL (Filipino) | EN → TL | Planeado | Propietario del proyecto |
| Conjunto retenido EN → CRK | EN → CRK | Futuro (necesita socio comunitario) | Organización de gobernanza comunitaria |

---

## 10. Integración de Tarjeta de Idioma

El marco del corpus se integra con el sistema de tarjeta de idioma:

1. **Selección de dominio** se informa por `linguisticChallenges` de la tarjeta — si un idioma tiene desafíos únicos (polisintesis, tono, animacidad), el corpus debe incluir entradas que los prueben.

2. **Calibración de dificultad** usa `classification` de la tarjeta — la distancia tipológica entre familias fuente y objetivo afecta qué constituye "difícil".

3. **Cobertura de registro** usa `registers` de la tarjeta — si un idioma tiene registros definidos (formal-filipino, taglish-profesional, taglish-casual), el corpus debe incluir entradas en cada nivel de registro.

4. **Prueba de influencia de contacto** usa `contactInfluences` de la tarjeta — para idiomas con capas de préstamos pesadas (Filipino: español + inglés + árabe), incluya entradas que prueben si los métodos manejan correctamente los préstamos vs. sobre-traducirlos.

5. **Manejo de escritura** usa `scripts[]` de la tarjeta — para idiomas multi-escritura (serbio: cirílico + latino), incluya entradas que prueben selección correcta de escritura.

---

## Referencias

- **Especificación de Puntuación de Champollion** — define todas las métricas, pesos compuestos, niveles de calidad
- **Especificación de Benchmark de Champollion** — protocolo de evaluación, formato de corpus, soberanía de datos
- **WALS** (Atlas Mundial de Estructuras Lingüísticas) — base de datos de características tipológicas
- **Glottolog** — fuente de verdad de clasificación de idiomas
- **ISO 639-3** — estándar de identificación de idiomas
- **EdTeKLA** — fuente del primer corpus de evaluación

---

*Este documento es una especificación viva. Actualícelo a medida que se construyan nuevos corpus y se aprendan lecciones.*