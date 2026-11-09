# RaceOps — Reporte del Bloque 7.5: API de Tracks y Events

## 1. Estado

- **Fecha:** 9 de noviembre de 2026
- **Fase:** 7 — Base operativa
- **Bloque:** 7.5 — API de Tracks y Events
- **Resultado:** implementado, verificado y aprobado por el propietario
- **Siguiente bloque:** 7.6 — Cierre de Fase 7 y evidencia de `v0.2`

## 2. Resultado funcional

RaceOps ya permite crear, listar, consultar y actualizar el catálogo mínimo de
Tracks. Un Track conserva nombre, ubicación opcional y ownership derivado del
Team activo; no intenta modelar layouts, sectores ni telemetría.

También permite crear, listar, consultar y actualizar Events. Cada Event exige
un Track del mismo Team, nombre, fecha inicial y un rango válido. Estado y
ownership no se aceptan desde el cliente. Los listados filtran por estado y
Track después de aplicar el alcance del Team.

El ciclo de Event es explícito:

```text
PLANNED → ACTIVE | COMPLETED | CANCELLED
ACTIVE  → COMPLETED | CANCELLED
COMPLETED y CANCELLED → terminales
```

Una transición repetida o terminal responde HTTP 409
`invalid_event_status_transition` sin modificar el Event. Se conserva
`PLANNED → COMPLETED` para no obligar al equipo a registrar el inicio en vivo.

## 3. Autorización

- todos los Roles consultan Tracks del Team activo;
- Administrator, Team Manager y Engineer administran Tracks y Events;
- Mechanic consulta Tracks y Events;
- Driver consulta Tracks, pero no Events hasta que Fase 8 pueda comprobar una
  relación mediante Session.

Un UUID ajeno o un Track ajeno utilizado al crear o actualizar Event responde
`404 resource_not_found`. No existen endpoints DELETE.

## 4. Evidencia de verificación

- 136 pruebas aprobadas en la única suite completa del bloque;
- 94.84 % de cobertura total, superior al mínimo de 90 %;
- 8 pruebas HTTP específicas aprobadas contra PostgreSQL;
- cinco Roles, fechas, filtros, estados y aislamiento entre Teams cubiertos;
- Ruff y mypy estricto aprobados;
- `alembic check` sin operaciones pendientes y dependencias sanas;
- no se modificó el esquema de persistencia;
- stack Docker saludable, migración en `20261108_0003_operations (head)`;
- runtime con UID `10001`, sin pytest, y siete rutas Track/Event en OpenAPI;
- `/health` y `/ready` respondieron HTTP 200.

La verificación completa también pasó en
[GitHub Actions, ejecución 42638867811](https://github.com/oraclesupreme63-droid/RACEOPS/actions/runs/42638867811).

## 5. Control de alcance

No se implementaron Sessions, sectores, layouts, coordenadas, archivos de
telemetría ni frontend. Cambiar el Track de un Event sigue permitido mientras
no existe Session; la inmovilidad después de la primera Session se aplicará en
Fase 8. El ciclo de Event continúa marcado como hipótesis de dominio revisable.

## 6. Aprobación

El propietario aprobó este bloque y autorizó el Bloque 7.6. Ese bloque no
agrega funciones: ejecuta el cierre integral de la Fase 7, actualiza
trazabilidad y prepara la evidencia de `v0.2 — Operational Base` antes de
iniciar Fase 8.
