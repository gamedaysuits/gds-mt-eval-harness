---
sidebar_position: 7
title: "Soberanía de Datos"
description: "Principios OCAP, CARE y Māori Data Sovereignty para traducción de lenguas indígenas. Por qué el consentimiento comunitario es anterior a la implementación."
related:
  - label: "Ownership Transfer"
    to: /docs/sovereignty/ownership-transfer
    kind: doc
    note: "How control of language data moves to communities"
  - label: "The Economic Model"
    to: /docs/sovereignty/economic-model
    kind: doc
  - label: "Reporting Errors and Owning Corrections"
    to: /docs/perspectives/reporting-errors-and-owning-corrections
    kind: position
  - label: "For Language Communities"
    to: /docs/community/for-language-communities
    kind: doc
---
# Soberanía de Datos

> **Resumen Ejecutivo.** Esta página explica los principios de soberanía de datos OCAP®, CARE y Te Mana Raraunga, y qué significan para desarrolladores que construyen métodos de traducción para lenguas indígenas. Cubre cuándo se requiere consentimiento comunitario, cómo la arquitectura del método `api` de champollion respalda la soberanía de datos, y las obligaciones éticas de cualquiera que trabaje con datos lingüísticos indígenas.

La traducción automática para lenguas indígenas plantea preguntas que no existen para el francés o el japonés. ¿Quién es dueño de los datos de entrenamiento? ¿Quién controla cómo habla un modelo de lenguaje? ¿Quién decide si una traducción es lo suficientemente buena para publicar?

**La respuesta siempre es la comunidad.**

champollion está construido para respaldar esto. El método `api` mantiene todos los recursos lingüísticos del lado del servidor bajo control comunitario. El sistema de plugins separa el método de la herramienta. Pero la herramienta no puede imponer ética — esta página explica los principios que debe seguir.

---

## Principios OCAP®

**OCAP** (Ownership, Control, Access, Possession — Propiedad, Control, Acceso, Posesión) es un conjunto de principios desarrollados por el [First Nations Information Governance Centre](https://fnigc.ca/ocap-training/) (FNIGC) que establecen cómo los datos de las Primeras Naciones deben ser recopilados, protegidos, utilizados y compartidos.

| Principio | Qué Significa para la Traducción |
|-----------|----------------------------------|
| **Propiedad** | La comunidad es dueña de sus datos lingüísticos — diccionarios, gramáticas, textos paralelos, archivos de entrenamiento y cualquier traducción producida a partir de ellos. |
| **Control** | La comunidad controla cómo se utilizan sus datos lingüísticos, quién tiene acceso y qué métodos de traducción son aceptables. |
| **Acceso** | Los miembros de la comunidad tienen derecho a acceder y gestionar sus propios recursos lingüísticos independientemente de dónde estén almacenados. |
| **Posesión** | Los datos físicos (archivos de entrenamiento, diccionarios, pesos del modelo) deben residir en infraestructura que la comunidad controla — no en la nube de un tercero. |

### Qué significa OCAP en la práctica

- **No publique traducciones** de una lengua indígena sin autorización explícita de la comunidad.
- **No entrene modelos** con datos lingüísticos proporcionados por la comunidad sin un acuerdo de compartición de datos.
- **No raspe** recursos lingüísticos comunitarios de sitios web, redes sociales o materiales educativos.
- **Use el método `api`** para que los prompts, datos de entrenamiento y diccionarios permanezcan en servidores controlados por la comunidad. El método `api` de champollion es un "tubo tonto" — envía claves y recibe traducciones. Toda la propiedad intelectual lingüística permanece del lado del servidor.
- **Documente la procedencia** — el campo `provenance` en el [manifiesto del plugin](https://champollion.dev/docs/reference/plugin-spec) debe listar cada recurso utilizado, su licencia y su origen.

:::warning OCAP® es una marca registrada
OCAP® es una marca registrada del First Nations Information Governance Centre. Se aplica específicamente a las Primeras Naciones en Canadá. Los principios tienen relevancia más amplia, pero la marca registrada y la autoridad de gobernanza pertenecen a FNIGC.
:::

---

## Principios CARE

Los **Principios CARE para la Gobernanza de Datos Indígenas** fueron desarrollados por la [Global Indigenous Data Alliance](https://www.gida-global.org/care) (GIDA) como complemento a los principios FAIR. FAIR dice que los datos deben ser Findable (Localizables), Accessible (Accesibles), Interoperable (Interoperables) y Reusable (Reutilizables). CARE dice que eso no es suficiente — la gobernanza de datos también debe centrar los derechos indígenas.

| Principio | Aplicación |
|-----------|-----------|
| **Beneficio Colectivo** | Las herramientas de traducción deben beneficiar primero a la comunidad lingüística. Las puntuaciones en el ranking son un medio para mejorar métodos, no para extraer valor comercial de lenguas comunitarias. |
| **Autoridad para Controlar** | Las comunidades tienen la autoridad para gobernar cómo se recopilan, utilizan y comparten sus datos lingüísticos. Una puntuación alta en el ranking no otorga permiso para publicar traducciones. |
| **Responsabilidad** | Los investigadores y desarrolladores que trabajan con datos lingüísticos indígenas tienen la responsabilidad de construir relaciones, obtener consentimiento y compartir beneficios. |
| **Ética** | Los derechos y el bienestar de los pueblos indígenas deben ser la preocupación principal. Los métodos de traducción deben desarrollarse *con* las comunidades, no *sobre* ellas. |

---

## Te Mana Raraunga — Soberanía de Datos Māori

**Te Mana Raraunga** es la [Māori Data Sovereignty Network](https://www.temanararaunga.maori.nz/). Afirma que los datos Māori — incluyendo datos lingüísticos — son un taonga (tesoro) sujeto a los principios del Tratado de Waitangi y tikanga Māori (ley consuetudinaria Māori).

Principios clave:

| Principio | Significado |
|-----------|-----------|
| **Rangatiratanga** (Autoridad) | Los Māori tienen un derecho inherente a ejercer autoridad sobre sus datos, incluyendo datos lingüísticos. |
| **Whakapapa** (Relaciones) | Los datos tienen orígenes y conexiones. Los datos lingüísticos llevan las relaciones y conocimientos de las personas que los crearon. |
| **Whanaungatanga** (Obligaciones) | Quienes poseen o procesan datos Māori tienen obligaciones recíprocas con las comunidades de las que provienen. |
| **Kotahitanga** (Beneficio colectivo) | Los datos Māori deben utilizarse para el beneficio colectivo de los Māori. |
| **Manaakitanga** (Reciprocidad) | El uso de datos Māori debe implicar cuidado, respeto y reciprocidad. |
| **Kaitiakitanga** (Guardianía) | Los guardianes de datos tienen el deber de proteger los datos y asegurar que se utilicen apropiadamente. |

Estos principios se aplican a te reo Māori (la lengua Māori) y a cualquier trabajo computacional que implique datos de la lengua Māori.

---

## Qué Significa Esto para Usuarios de champollion

### Para lenguas estándar (francés, japonés, español...)

Use champollion normalmente. Estas lenguas tienen grandes corpus disponibles públicamente, APIs de traducción establecidas y sin preocupaciones de soberanía. Traduzca, sincronice y publique como desee.

### Para lenguas indígenas y de bajo recurso

La situación es fundamentalmente diferente:

1. **Obtenga consentimiento primero.** Antes de construir un método de traducción para una lengua indígena, establezca una relación con la comunidad. Un método construido sin participación comunitaria — sin importar cuán técnicamente impresionante sea — no debe ser publicado o distribuido.

2. **Use el método `api`.** Aloje el pipeline de traducción en infraestructura controlada por la comunidad. El método `api` en champollion está diseñado para esto: envía claves y recibe traducciones sin exponer los prompts, diccionarios o datos de entrenamiento que hacen que el método funcione.

    ```json title="Community-controlled setup"
    {
      "pairs": {
        "en:crk": {
          "method": "api",
          "endpoint": "https://api.community-server.example/translate"
        }
      }
    }
    ```

3. **Documente todo.** Use el campo `provenance` en su manifiesto de plugin para listar cada recurso, su licencia y si fue proporcionado con consentimiento comunitario.

4. **Las puntuaciones no son licencias.** Una puntuación alta en el ranking prueba que un método funciona bien técnicamente. No otorga permiso para publicar traducciones, distribuir el plugin o comercializar el método. La comunidad decide.

5. **Comparta el método, no los datos.** Si desarrolla una técnica que funciona bien (p. ej., "LLM con puerta FST y prompts entrenados"), comparta la *arquitectura* y el *enfoque* en el ranking. La comunidad retiene control sobre los datos lingüísticos que la hacen funcionar para su lengua específica.

---

## El Método `api` y la Soberanía

El [método de traducción](https://champollion.dev/docs/guides/translation-methods) `api` existe específicamente para respaldar la soberanía de datos. Aquí está el por qué:

| Aspecto | Otros Métodos | Método `api` |
|--------|--------------|-------------|
| **Dónde viven los prompts** | En archivos de configuración de champollion (visibles para todos los desarrolladores) | En el servidor de la comunidad (privado) |
| **Dónde viven los datos de entrenamiento** | En directorio `.champollion/coaching/` (comprometido a git) | En el servidor de la comunidad (privado) |
| **Dónde viven los diccionarios** | En el directorio del plugin (distribuido con el plugin) | En el servidor de la comunidad (privado) |
| **Quién controla el pipeline** | Quien ejecute `champollion sync` | La comunidad que opera la API |
| **Qué ve champollion** | Todo | Claves adentro, traducciones afuera |

El método `api` es una opción arquitectónica deliberada. Es un "tubo tonto" porque la propiedad intelectual — el conocimiento lingüístico, las reglas gramaticales, los ejemplos de entrenamiento cuidadosamente curados — pertenece a la comunidad, no a la herramienta.

Vea [Serving a Method via API](https://champollion.dev/docs/guides/serving-a-method) para detalles de implementación.

---

## Caso de Estudio: OMT-1600 y Soberanía de Datos

OMT-1600 de Meta (marzo de 2026) proporciona un ejemplo concreto de por qué la soberanía de datos importa para lenguas indígenas. OMT-1600 entrenó modelos de traducción para 1.600 lenguas usando:

- **CC-2000-Web**: Texto monolingüe raspado de la web de 2.000+ languoides — recopilado sin consentimiento comunitario
- **Traducciones de la Biblia**: Textos religiosos utilizados como datos de entrenamiento paralelo y evaluación para las lenguas de menor recurso
- **MeDLEy**: Bitext manualmente curado — pero sin cumplimiento documentado de OCAP® o CARE
- **Datos sintéticos retrotraducidos**: ~270 millones de oraciones paralelas sintéticas generadas por los propios modelos

Para lenguas indígenas como Plains Cree (CRK), esto significa:

| Principio | Práctica de OMT-1600 | Impacto |
|-----------|-------------------|--------|
| **Propiedad** | Meta es dueña de los modelos y decide cómo liberarlos | La comunidad no tiene participación en la propiedad de cómo se modela su lengua |
| **Control** | Meta controla la selección de datos de entrenamiento, arquitectura del modelo y cronograma de lanzamiento | La comunidad no tiene participación en qué datos se utilizan o cómo se representa la lengua |
| **Acceso** | Los pesos del modelo no están disponibles actualmente — "no se liberaron debido a factores fuera del control de los autores" | La comunidad no puede acceder, inspeccionar o modificar el modelo que habla su lengua |
| **Posesión** | Todos los datos y modelos residen en infraestructura de Meta | La comunidad no puede alojar, auditar o eliminar los datos utilizados para entrenar el modelo |

OMT-1600 es un logro de investigación. También es un ejemplo de práctica de datos extractiva: datos lingüísticos fueron recopilados de la web y textos religiosos, procesados en un modelo y publicados como un artículo — todo sin participación comunitaria, consentimiento o compartición de beneficios.

**Este es exactamente el patrón que la arquitectura de soberanía de champollion previene.** El método `api` mantiene la propiedad intelectual lingüística en servidores controlados por la comunidad. Los corpus de evaluación se proporcionan con consentimiento comunitario y se almacenan bajo custodia de claves comunitarias. Los métodos ganadores de premios se transfieren a propiedad comunitaria. La diferencia no es técnica — es ética y estructural.

:::note OMT-1600 no es únicamente culpable
Este patrón — raspado de web seguido de entrenamiento de modelos sin consentimiento comunitario — es práctica estándar en investigación de PNL multilingüe masiva. OMT-1600 es un caso de estudio por su escala (1.600 lenguas) y recencia (marzo de 2026), no porque sea únicamente extractiva. La misma crítica se aplica a NLLB-200, los esfuerzos multilingües de Google y la mayoría de investigación de MT a gran escala.
:::

---

## Lecturas Adicionales

- [First Nations Information Governance Centre — OCAP®](https://fnigc.ca/ocap-training/)
- [Global Indigenous Data Alliance — CARE Principles](https://www.gida-global.org/care)
- [Te Mana Raraunga — Māori Data Sovereignty Network](https://www.temanararaunga.maori.nz/)
- [USIDSN — United States Indigenous Data Sovereignty Network](https://usindigenousdata.org/)

---

## Véase También

- [Support a Low-Resource Language](/docs/community/low-resource-languages) — la guía técnica con contexto OCAP
- [Translation Methods](https://champollion.dev/docs/guides/translation-methods) — el método `api` y cómo protege la propiedad intelectual
- [Serving a Method via API](https://champollion.dev/docs/guides/serving-a-method) — alojamiento de un pipeline controlado por la comunidad
- [Plugin Specification](https://champollion.dev/docs/reference/plugin-spec) — el campo `provenance` para atribución de recursos
- [Cookbook: FST-Gated Pipeline](/docs/tutorials/fst-gated-pipeline) — construcción de un pipeline que una comunidad puede auto-alojar