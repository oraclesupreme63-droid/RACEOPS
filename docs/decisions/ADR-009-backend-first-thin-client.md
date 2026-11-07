# ADR-009 — Backend-first y cliente web ligero

- **Estado:** Aceptado
- **Fecha:** 2026-10-22

## Contexto

El riesgo principal es validar reglas, utilidad y confidencialidad. Elegir
ahora un frontend complejo puede retrasar el flujo central.

## Decisión

Construir primero API, dominio y pruebas. El frontend será el cliente web más
pequeño capaz de operar el MVP y consumirá OpenAPI. La tecnología exacta se
elige cuando existan los primeros endpoints y wireframes del flujo.

## Consecuencias

- La Fase 5 no queda bloqueada por un framework de interfaz.
- Las reglas nunca residen exclusivamente en el cliente.
- La elección futura debe considerar móvil, formularios rápidos y habilidad
  disponible, no popularidad.

