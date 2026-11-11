# RaceOps — Reporte del Bloque 8.8: Observations

## 1. Estado

- **Fecha:** 11 de noviembre de 2026
- **Fase:** 8 — Session Learning Loop
- **Bloque:** 8.8 — Observations
- **Resultado:** implementado, verificado y aprobado por el propietario
- **Siguiente bloque:** 8.9 — Analysis e Hypotheses

## 2. Capacidad entregada

RaceOps permite registrar hechos, síntomas o comportamientos observados y
asociarlos al menos con una Session o Vehicle del Team. La descripción es
obligatoria y la categoría es opcional. Cada registro conserva autor,
timestamps y un nivel de visibilidad explícito.

Observation vive en el módulo `learning`, que depende de `sessions` y
`operations` sin introducir una dependencia inversa.

## 3. Honestidad e integridad

- Observation no contiene `cause`, `confirmed` ni estado de Hypothesis;
- no crea ni modifica automáticamente una Hypothesis;
- requiere `session_id`, `vehicle_id` o ambos;
- las referencias compuestas protegen Session–Team y Vehicle–Team;
- el cliente no controla `team_id`, autor ni timestamps;
- contexto y visibilidad quedan inmutables en la API P0;
- no existe DELETE.

## 4. Autorización y visibilidad

- Engineer y Mechanic pueden crear y actualizar Observations visibles;
- sólo Engineer puede crear `ENGINEERING_CONFIDENTIAL`;
- Engineer lee `TEAM`, `ROLE_RESTRICTED` y `ENGINEERING_CONFIDENTIAL`;
- Team Manager y Mechanic leen `TEAM` y `ROLE_RESTRICTED`;
- Administrator lee únicamente `TEAM`, sin privilegio jerárquico adicional;
- Driver lee `TEAM` sólo cuando la Session o el Vehicle están relacionados;
- si existen Session y Vehicle, la Session concreta tiene precedencia para
  determinar la relación del Driver;
- filtrado y conteo ocurren antes de paginar.

## 5. API

```text
POST  /api/v1/observations
GET   /api/v1/observations
GET   /api/v1/observations/{observation_id}
PATCH /api/v1/observations/{observation_id}
```

El listado acepta filtros opcionales `session_id` y `vehicle_id`, además de
`limit` y `offset`.

## 6. Verificación

- pruebas unitarias de modelo, validación y RBAC;
- pruebas HTTP para Engineer, Mechanic, Team Manager, Administrator y Driver;
- pruebas de aislamiento entre Teams y referencias inválidas;
- pruebas de los tres niveles de visibilidad y conteos filtrados;
- prueba de precedencia Session sobre Vehicle para Driver;
- migración reversible `20261111_0008_observations`;
- Ruff format/check y mypy: aprobados;
- suite completa: **195 pruebas aprobadas**;
- cobertura total: **93.75 %**, superior al mínimo de 90 %;
- `alembic check`: sin operaciones nuevas pendientes;
- build y smoke test del contenedor: `/health`, `/ready`, OpenAPI y migración
  `20261111_0008_observations (head)` aprobados.

## 7. Clasificación de decisiones

- **Respaldado por evidencia:** observación asociada con Session/Vehicle,
  autoría, visibilidad y separación estricta entre observación y causa.
- **Parcialmente respaldado:** categoría opcional; permanece texto flexible y
  no un catálogo universal rígido.
- **Hipótesis conservadora:** Engineer y Mechanic pueden corregir evidencia
  visible; contexto y visibilidad permanecen inmutables en P0.
- **Rechazado en este bloque:** convertir una observación en incidente,
  hipótesis o causa confirmada automáticamente.

## 8. Control de alcance

No se añadieron incidentes, mantenimiento, enlaces a feedback/laps/sectors,
análisis, hipótesis, causalidad automática ni cambios de visibilidad auditados.
Esas capacidades permanecen fuera de P0 o en bloques posteriores.

## 9. Aprobación

El propietario aprobó el Bloque 8.8 y autorizó el inicio del Bloque 8.9:
Analysis e Hypotheses, manteniendo separados resumen autorizado, detalle
técnico, causa posible y confianza.
