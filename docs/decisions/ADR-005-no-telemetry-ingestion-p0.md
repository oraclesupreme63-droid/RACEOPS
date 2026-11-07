# ADR-005 — Sin ingestión de telemetría en P0

- **Estado:** Aceptado
- **Fecha:** 2026-10-22

## Contexto

RaceOps complementa AiM, MyChron y MoTeC. La evidencia favorece conectar
feedback, contexto, decisiones y resultados, no reemplazar adquisición o
análisis profesional.

## Decisión

P0 permite registrar vueltas y sectores de forma controlada. Referencias a
archivos son P1 e importación CSV permanece condicionada. No habrá ingestión
en vivo, parsing universal ni almacenamiento de canales en P0.

## Consecuencias

- El equipo puede validar el aprendizaje entre sesiones antes de integrar.
- Se evita diseñar un schema universal falso.
- Una integración futura necesita muestras reales, permiso y formatos
  observados.

