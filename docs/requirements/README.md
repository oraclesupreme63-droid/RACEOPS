# RaceOps — Paquete de Ingeniería de requerimientos

## Estado

Preparado para evaluación del Gate G2 — Requirements Ready.

## Documentos

| Documento | Función |
|---|---|
| [`../preliminary-requirements.md`](../preliminary-requirements.md) | Catálogo canónico de 170 RF y 67 RNF; refinado como versión 2.0 |
| [`actors.md`](actors.md) | Actores, responsabilidades y límites |
| [`permission-matrix.md`](permission-matrix.md) | Operaciones permitidas y visibilidad por rol |
| [`use-cases.md`](use-cases.md) | 19 casos de uso y flujo integrado |
| [`user-stories.md`](user-stories.md) | 22 historias orientadas a valor |
| [`acceptance-criteria.md`](acceptance-criteria.md) | 33 escenarios funcionales y 6 criterios no funcionales |
| [`prioritized-backlog.md`](prioritized-backlog.md) | 50 elementos ordenados por dependencias y prioridad |
| [`traceability-matrix.md`](traceability-matrix.md) | Relación evidencia–actor–historia–RF–AC–backlog |
| [`definition-of-ready-done.md`](definition-of-ready-done.md) | Condiciones para iniciar y terminar trabajo |
| [`gate-g2-assessment.md`](gate-g2-assessment.md) | Evaluación de salida de la Fase 2 |

## Resumen de alcance

| Prioridad | Cantidad de RF | Significado |
|---:|---:|---|
| P0 | 104 | Reglas y funciones imprescindibles para el flujo principal |
| P1 | 60 | Necesarias para RaceOps v1.0, pero no para el primer corte |
| P2 | 4 | Condicionadas a evidencia y tiempo |
| P3 | 2 | Fuera de V1 o futuras |

Los 104 RF P0 no representan 104 pantallas ni 104 funcionalidades grandes.
Incluyen validaciones, restricciones, reglas de integridad y controles de
seguridad agrupados en 35 elementos funcionales P0 del backlog, además de
fundación y validación.

## Decisiones importantes

- La autorización se aplica en servidor.
- Administrator no obtiene acceso técnico confidencial automáticamente.
- Driver nunca consulta `ENGINEERING_CONFIDENTIAL`.
- Mantenimiento completo es P1.
- El flujo P0 funciona sin integraciones externas.
- Completar una acción no significa que mejoró el resultado.
- Toda afirmación de facilidad, rendimiento o adopción necesita medición.

