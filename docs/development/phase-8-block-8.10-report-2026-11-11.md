# RaceOps — Reporte del Bloque 8.10: Priorities y Actions

## 1. Estado

- **Fecha:** 11 de noviembre de 2026
- **Fase:** 8 — Session Learning Loop
- **Bloque:** 8.10 — Priorities y Actions
- **Resultado:** implementado y verificado; pendiente de aprobación del propietario
- **Siguiente bloque:** 8.11 — Outcomes y siguiente Session

## 2. Capacidad entregada

RaceOps convierte el análisis en focos concretos y trabajo responsable sin
inventar una Session futura ni afirmar que una acción funcionó.

- Priority indica qué merece atención para Driver, Engineer o Mechanic;
- Action indica trabajo decidido, responsable y estado de ejecución;
- ambos pueden apuntar a una Session real posterior o conservar la intención
  `NEXT_SESSION` con `target_session_id` ausente;
- `COMPLETED` significa ejecutada, no mejorada ni evaluada.

## 3. Priorities

- conservan Session de origen, destinatario, objetivo, descripción y
  timestamps;
- pueden relacionarse con una Hypothesis de la misma Session;
- la motivación técnica se omite para audiencias no Engineering;
- una Main Priority usa rango 1, 2 o 3;
- PostgreSQL impide rangos principales duplicados para el mismo destinatario
  y alcance objetivo;
- rango 1–3 más unicidad garantiza un máximo de tres;
- una cuarta puede persistirse como nota `is_main = false`, sin rango;
- Engineer puede corregir texto o jerarquía; Team Manager puede crear y leer,
  pero no reescribir la prioridad técnica.

Para `NEXT_SESSION`, el alcance se ancla a la Session de origen. Para
`SPECIFIC_SESSION`, se ancla a la Session objetivo real. Esto permite aplicar
la restricción de tres de forma transaccional sin crear Sessions ficticias.

## 4. Actions

- conservan Session de origen, objetivo/intención, tipo, responsable y
  motivación;
- tipos: `DRIVING`, `ENGINEERING` y `MECHANICAL`;
- responsables: Driver, Engineer o Mechanic, por Role y opcionalmente User;
- el User responsable debe tener una membresía activa del mismo Team y Role;
- una Action puede originarse en Hypothesis, Priority o descripción explícita;
- `public_summary` se almacena separado de `confidential_detail`;
- sólo Engineer escribe y recibe `confidential_detail`;
- un Driver relacionado recibe el resumen público sin identificadores de
  Hypothesis/Priority ni contenido técnico;
- no existe DELETE ni Action Outcome en este bloque.

## 5. Ciclo de ejecución

```text
PROPOSED → PLANNED → IN_PROGRESS → COMPLETED
    └──────────┴──────────────→ CANCELLED
```

- responsable asignado, Engineer o Team Manager pueden ejecutar transiciones;
- completar desde un estado incorrecto devuelve conflicto 409;
- estados terminales no se reabren en P0;
- cancelar requiere y conserva un motivo;
- completar no crea Outcome, Conclusion ni cambia Hypothesis.

## 6. Autorización y visibilidad

- Engineer y Team Manager coordinan prioridades y acciones autorizadas;
- Mechanic consulta/actualiza Actions asignadas a su Role o User;
- Driver consulta sus Priorities y Actions asignadas o resúmenes públicos de
  su Session;
- Administrator no recibe contenido `ROLE_RESTRICTED` sólo por jerarquía;
- listados filtran por Team, Role, User y relación antes de contar/paginar;
- un UUID de otro Team o un User responsable inválido se oculta con 404.

## 7. API

```text
POST  /api/v1/sessions/{source_session_id}/priorities
GET   /api/v1/sessions/{source_session_id}/priorities
GET   /api/v1/priorities/{priority_id}
PATCH /api/v1/priorities/{priority_id}

POST  /api/v1/sessions/{source_session_id}/actions
GET   /api/v1/sessions/{source_session_id}/actions
GET   /api/v1/actions/{action_id}
POST  /api/v1/actions/{action_id}/plan
POST  /api/v1/actions/{action_id}/start
POST  /api/v1/actions/{action_id}/complete
POST  /api/v1/actions/{action_id}/cancel
```

## 8. Persistencia

La migración `20261111_0010_decisions` añade:

- tablas `priorities` y `actions`;
- enums `target_intent`, `action_type` y `action_status`;
- FKs compuestas por Team para Sessions, Hypotheses y Priorities;
- checks de objetivo, destinatario, motivación, cancelación y visibilidad;
- índice único parcial con `NULLS NOT DISTINCT` para Main Priorities;
- índices de origen, objetivo y responsable.

La migración se aplicó de forma no destructiva hasta `head`; `alembic check`
no detectó diferencias entre modelos y esquema.

## 9. Verificación

- Ruff format/check: aprobado;
- mypy estricto para `src` y `tests`: aprobado;
- pruebas HTTP de límite de tres, nota adicional, reordenamiento y objetivo:
  aprobadas;
- pruebas de visibilidad para Engineer, Team Manager, Mechanic, Driver y
  Administrator: aprobadas;
- pruebas de separación `public_summary`/`confidential_detail`: aprobadas;
- pruebas de transiciones válidas e inválidas: aprobadas;
- suite local completa no destructiva: **211 pruebas aprobadas**;
- cobertura total: **91.84 %**, superior al mínimo de 90 %;
- migración aplicada: `20261111_0010_decisions (head)`;
- `alembic check`: sin operaciones nuevas pendientes;
- imagen Docker reconstruida y contenedores API/PostgreSQL saludables;
- smoke test aprobado para `/health`, `/ready` y las ocho rutas nuevas.

## 10. Clasificación de decisiones

- **Respaldado por evidencia:** aproximadamente 1–3 prioridades accionables
  por destinatario.
- **Respaldado por evidencia:** acciones distintas para Driver, Engineering y
  Mechanic, con información adecuada por Role.
- **Respaldado por evidencia:** detalle confidencial separado del resumen
  comunicable al Driver.
- **Parcialmente respaldado:** el máximo rígido de tres y el catálogo de tipos;
  se mantienen revisables con nuevas entrevistas.
- **Hipótesis conservadora:** Engineer y Team Manager funcionan como
  coordinadores de ejecución; el responsable actualiza su trabajo asignado.
- **Rechazado:** crear una Session placeholder para representar “la próxima”.
- **Rechazado:** derivar mejora, Outcome o conclusión desde `COMPLETED`.

## 11. Contratiempos y deuda controlada

- La unicidad de Main Priorities usa una capacidad de PostgreSQL 15+; RaceOps
  ya fija PostgreSQL 18.6, por lo que no añade una dependencia nueva.
- La pertenencia User–Team–Role se valida transaccionalmente mediante
  TeamMembership; la tabla conserva además la FK al User global.
- P0 conserva estado actual, timestamps y motivo de cancelación, no un event
  log completo de cada transición.
- Las Actions `NEXT_SESSION` todavía no se vinculan ni evalúan: eso pertenece
  al Bloque 8.11.

## 12. Punto de aprobación

Con aprobación comenzará el Bloque 8.11. Allí se vinculará una Action con la
Session real de evaluación, se registrará `IMPROVED`, `WORSENED`,
`NO_MEASURABLE_EFFECT` o `INCONCLUSIVE`, y sólo entonces podrá concluirse una
Hypothesis con evidencia posterior.
