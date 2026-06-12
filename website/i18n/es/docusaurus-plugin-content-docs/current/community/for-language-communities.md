---
sidebar_position: 1
title: "Para Comunidades Lingüísticas"
---
# Para Comunidades Lingüísticas

> **Resumen Ejecutivo.** Una guía para hablantes de lenguas indígenas y de recursos limitados que explica cómo contribuir a la Arena (traducciones de referencia, revisión de traducciones, datos de entrenamiento) y qué recibe la comunidad a cambio (propiedad del código, ingresos por API, control total de la implementación). No se requieren conocimientos de programación.

No necesita ser programador para contribuir a la Arena. Si habla una lengua indígena o de recursos limitados, usted es la persona más importante en este ecosistema.

---

## Lo Que Necesitamos De Usted

### Traducciones de referencia

Necesitamos pares de traducciones curadas para evaluación — inglés de un lado, su lengua del otro. Estos se convierten en la "clave de respuestas" contra la cual se califican todos los métodos de traducción.

Puede crearlos a partir de:
- **Materiales educativos** — ejercicios de libros de texto, planes de lección, hojas de trabajo
- **Documentos comunitarios** — actas de reuniones, boletines, anuncios
- **Frases cotidianas** — cadenas de interfaz de usuario, etiquetas de aplicaciones, expresiones comunes
- **Contenido cultural** — historias, canciones o descripciones (con los permisos apropiados)

El formato es JSON simple:
```json
{
  "entries": [
    { "id": 1, "source": "Hello", "reference": "tânisi" },
    { "id": 2, "source": "Thank you", "reference": "kinanâskomitin" }
  ]
}
```

### Revisión de traducciones

Cada método que afirma producir traducciones funcionales necesita validación humana. Los hablantes bilingües revisan los resultados y nos dicen si la computadora lo hizo bien — y más importante aún, *por qué* lo hizo mal.

### Datos de entrenamiento

Reglas gramaticales, entradas de diccionario, patrones morfológicos — estos son los recursos lingüísticos que hacen que los métodos de traducción funcionen. Su conocimiento de cómo funciona su lengua es irreemplazable por cualquier modelo de IA.

---

## Lo Que Recibe A Cambio

### Propiedad

Cuando se construye un método de traducción para su lengua y se valida en la Arena, la [propiedad se transfiere](/docs/sovereignty/ownership-transfer) a la organización de gobernanza de su comunidad. Usted es propietario del código, los pesos del modelo y la implementación.

### Ingresos

Cuando los desarrolladores utilizan el método de su lengua a través de la API de champollion, su comunidad recibe [el 90% de los ingresos por API](/docs/sovereignty/economic-model). El 10% restante cubre los costos de infraestructura.

### Control

Su organización de gobernanza controla:
- Quién puede acceder al método
- Si puede usarse comercialmente
- Qué términos de precios se aplican
- Cuándo y cómo se actualiza
- Qué datos se utilizan para desarrollo futuro

---

## Cómo Involucrarse

1. **Comuníquese con nosotros** — Abra un problema en el [repositorio de Arena](https://github.com/gamedaysuits/arena) o envíe un correo electrónico a los mantenedores
2. **Describa su lengua** — ¿A qué familia pertenece? ¿Cuántos hablantes tiene? ¿Qué sistemas de escritura se utilizan? ¿Qué recursos computacionales existen (FST, diccionarios, corpus)?
3. **Comience en pequeño** — Incluso 50 pares de traducciones curadas son suficientes para crear un conjunto de datos de evaluación y abrir una nueva pista en el leaderboard
4. **Conéctenos con la gobernanza** — ¿Quién en su comunidad tiene autoridad sobre datos y tecnología lingüística? El modelo de soberanía de la Arena requiere un socio de gobernanza

---

## Soberanía de Datos

Sus datos lingüísticos son suyos. La Arena se construye sobre los [principios OCAP®](/docs/sovereignty/data-sovereignty):

- Nunca recopilamos ni almacenamos sus datos lingüísticos en nuestros servidores
- Los métodos de traducción utilizan la arquitectura `api` — todos los datos de entrenamiento, diccionarios y reglas gramaticales permanecen en la infraestructura que usted controla
- Usted decide quién puede desarrollar métodos para su lengua
- Las puntuaciones del leaderboard prueban que un método funciona; no otorgan permiso para implementarlo

---

## Véase También

- [Soberanía de Datos](/docs/sovereignty/data-sovereignty) — el marco completo OCAP, CARE y Te Mana Raraunga
- [Transferencia de Propiedad](/docs/sovereignty/ownership-transfer) — qué sucede cuando un método gana
- [El Modelo Económico](/docs/sovereignty/economic-model) — cómo las puntuaciones se convierten en ingresos
- [Apoye una Lengua de Recursos Limitados](/docs/community/low-resource-languages) — contexto técnico para investigadores que trabajan junto con comunidades