---
sidebar_position: 2
title: "Transferencia de Propiedad"
---
# Transferencia de Propiedad

> **Resumen Ejecutivo.** Cuando un método de traducción alcanza el nivel Deployable (puntuación compuesta ≥ 0.70) y aprueba la revisión comunitaria, la propiedad del código se transfiere del investigador a la organización de gobernanza indígena. Esta página documenta el pipeline de transferencia de cinco etapas, la alineación con OCAP®, y orientación para investigadores que desarrollan métodos para lenguas indígenas.

Cuando un método de traducción gana en el leaderboard de la Arena, ¿qué sucede con el código? Para lenguas indígenas y de recursos limitados, la respuesta no es "el investigador lo conserva". La respuesta es: **la comunidad es propietaria del mismo.**

---

## Cómo Funciona

La Arena implementa un pipeline claro desde la investigación hasta la propiedad comunitaria:

### 1. Desarrollo del Método
Un investigador, estudiante o desarrollador construye un método de traducción — un pipeline con compuerta FST, un LLM entrenado, un modelo ajustado, o cualquier otro enfoque. Lo desarrollan utilizando sus propios recursos.

### 2. Evaluación en la Arena
El método se evalúa mediante el [arnés de evaluación](/docs/specifications/harness). Cada envío se vincula a un commit específico de Git y versión de dataset. Las puntuaciones son reproducibles.

### 3. Revisión Comunitaria
Para métodos de lenguas indígenas, los resultados se revisan por trabajadores de lengua comunitarios y organizaciones de gobernanza. Una puntuación alta en el leaderboard demuestra que el método *funciona*; no demuestra que sea *apropiado*.

### 4. Transferencia de Código
Cuando un método alcanza el nivel **Deployable** (puntuación compuesta ≥ 0.70 contra la evaluación de estándar de oro) **y** aprueba la revisión comunitaria (validación humana):
- El investigador entrega el código fuente
- La propiedad legal se transfiere a la organización de gobernanza indígena (p. ej., un consejo tribal, autoridad de lengua, u organización Métis)
- La organización de gobernanza mantiene las claves de cifrado para los datasets de evaluación
- El método se convierte en un activo controlado por la comunidad

Consulte la [Especificación de Puntuación](/docs/specifications/scoring), §5 para definiciones de niveles de calidad y la [Especificación de Benchmark](/docs/specifications/benchmark), §8.3 para las condiciones completas de transferencia y §7 para la compuerta de validación humana.

### 5. Despliegue en Producción
El método se exporta como un plugin de [champollion](https://champollion.dev) y se despliega en la API de producción. La comunidad controla:
- Quién puede acceder al método
- Qué términos de precios se aplican
- Si el método puede utilizarse comercialmente
- Cuándo y cómo se actualiza el método

---

## Por Qué Esto Importa

La investigación tradicional en ML sigue un patrón extractivo:
1. El investigador recopila datos de una comunidad
2. El investigador entrena un modelo
3. El investigador publica un artículo
4. La comunidad no recibe nada

Este patrón ahora opera a escala industrial. OMT-1600 de Meta (marzo de 2026) entrenó modelos de traducción para 1,600 lenguas — incluyendo lenguas indígenas como Plains Cree — utilizando datos extraídos de la web y traducciones de la Biblia. Los modelos se entrenaron sin protocolos de consentimiento comunitario, los pesos no están actualmente disponibles para descargar, y las comunidades cuyas lenguas fueron modeladas no tienen participación en la propiedad, ningún rol de gobernanza, y ningún ingreso. El artículo es el producto. La comunidad es la fuente de datos.

La Arena invierte esto:
1. El investigador construye un método
2. La Arena lo valida contra corpus curados por la comunidad con métricas morfológicas
3. La comunidad recibe propiedad del código funcional
4. La comunidad genera ingresos por el uso de la API

**Esta es la diferencia fundamental entre Champollion y todos los demás esfuerzos de MT de LRL, incluyendo OMT-1600:** no solo producimos métodos para comunidades — transferimos propiedad de métodos *a* comunidades. El código, los pesos, la infraestructura de despliegue — todo se convierte en propiedad comunitaria. Esto no es un marco teórico — es el pipeline operacional para cada método de lengua indígena en la plataforma.

---

## Alineación con OCAP®

El proceso de transferencia de propiedad implementa directamente los [principios OCAP®](/docs/sovereignty/data-sovereignty):

| Principio | Implementación |
|---|---|
| **Ownership (Propiedad)** | La organización de gobernanza tiene título sobre el código del método y los pesos del modelo |
| **Control (Control)** | La organización de gobernanza controla los términos de despliegue, acceso y precios |
| **Access (Acceso)** | Los miembros de la comunidad acceden al método a través de la API de champollion o descarga directa |
| **Possession (Posesión)** | Los recursos lingüísticos (datos de entrenamiento, diccionarios, reglas FST) permanecen en infraestructura controlada por la comunidad mediante el método `api` |

---

## Para Investigadores

Si está desarrollando un método para una lengua indígena:

1. **Establezca una relación** con la comunidad de lengua antes de comenzar
2. **Utilice datos con licencia abierta** para desarrollo (no recursos restringidos a la comunidad)
3. **Documente la procedencia** en su [tarjeta de ejecución](/docs/specifications/run-card) — liste cada recurso, su licencia y origen
4. **Esté preparado para transferir** — si su método tiene éxito, el código pertenece a la comunidad, no a usted
5. **Esto es una característica, no una limitación** — su contribución es la arquitectura y técnica, que puede publicar y reutilizar. La contribución de la comunidad es el conocimiento lingüístico que lo hace funcionar para su lengua.

---

## Véase También

- [Soberanía de Datos](/docs/sovereignty/data-sovereignty) — principios OCAP, CARE y Te Mana Raraunga
- [El Modelo Económico](/docs/sovereignty/economic-model) — cómo la propiedad se convierte en ingresos
- [Apoye una Lengua de Recursos Limitados](/docs/community/low-resource-languages) — el contexto de investigación