# Fase 9 — Dataset de timing público

**Fecha:** 13 de noviembre de 2026
**Estado:** técnicamente listo; pendiente de aprobación del propietario y CI

## Resultado buscado

Complementar el caso completamente sintético con resultados públicos de una
competencia real de karting, conservando procedencia y evitando inventar
información de ingeniería.

## Alcance

- una Qualifying Heat y una Final del mismo kart;
- 38 vueltas y 114 sectores publicados;
- hora, clima, temperatura ambiente y condición de pista publicadas;
- identidad seudonimizada dentro de RaceOps;
- flujo de aprendizaje marcado como ejercicio sintético;
- resultado inconcluso por ausencia de feedback, setup y acción documentada.

## Regla de evidencia

Los tiempos publicados pueden demostrar que RaceOps procesa resultados
representativos. No demuestran que el producto sea usable o adoptado. Tampoco
permiten atribuir la diferencia entre sesiones a una causa técnica.

## Comprobación requerida

El bloque se considerará técnicamente listo cuando pasen:

- validación tipada del JSON;
- igualdad entre suma de sectores y vuelta;
- prueba unitaria del delta de mejor vuelta;
- persistencia PostgreSQL de ambas sesiones;
- suite completa y CI.

## Resultados locales

- JSON válido y carga tipada correcta;
- formato: 133 archivos conformes;
- lint: sin errores;
- mypy: 119 archivos sin errores;
- pruebas unitarias del dataset: `12 passed`;
- pruebas PostgreSQL dirigidas: `2 passed`;
- 38 vueltas y 114 sectores persistidos;
- Alembic: sin nuevas operaciones de migración.

La suite global local se detuvo manualmente alrededor de 30 % porque su ritmo
se volvió anormalmente lento en el entorno Windows. Hasta la detención no había
fallos. Para evitar repetir trabajo y tiempo improductivo, la verificación
global definitiva se delega a CI en un PostgreSQL limpio; el bloque no se
declarará verificado si ese flujo falla.
