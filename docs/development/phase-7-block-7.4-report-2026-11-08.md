# RaceOps — Reporte del Bloque 7.4: API de Vehicles

## 1. Estado

- **Fecha:** 8 de noviembre de 2026
- **Fase:** 7 — Base operativa
- **Bloque:** 7.4 — API de Vehicles
- **Resultado:** implementado y verificado; pendiente de aprobación del propietario
- **Siguiente bloque:** 7.5 — API de Tracks y Events

## 2. Resultado funcional

RaceOps permite crear, listar, consultar y renombrar Vehicles dentro del Team
activo. Cada Vehicle inicia en `READY` y cambia mediante cuatro comandos
explícitos: marcar listo, en mantenimiento, no disponible o retirado. No hay
PATCH genérico de estado ni endpoint DELETE.

El ciclo aplicado es:

```text
READY       → MAINTENANCE | UNAVAILABLE | RETIRED
MAINTENANCE → READY | UNAVAILABLE | RETIRED
UNAVAILABLE → READY | MAINTENANCE | RETIRED
RETIRED     → ninguna
```

Un cambio repetido o prohibido responde HTTP 409
`invalid_vehicle_status_transition` y conserva el estado anterior. La regla
de asignabilidad está lista para Fase 8: únicamente `READY` devuelve verdadero.

## 3. Autorización y ownership

Se incorporó `READ_VEHICLES` separado de `MANAGE_VEHICLES`:

- Administrator y Team Manager administran y consultan;
- Engineer y Mechanic consultan Vehicles del Team activo;
- Driver no recibe acceso general mientras Session no permita comprobar una
  relación real con el Vehicle.

`team_id` se deriva del token, nunca del body. Los listados filtran por Team
antes de contar y un UUID ajeno responde `404 resource_not_found`. El cliente
tampoco puede imponer el estado inicial.

## 4. Identidad y conflictos

El identificador se recorta, admite de 1 a 80 caracteres y es único dentro
de cada Team. El mismo texto puede existir legítimamente en otro Team. Un
duplicado local responde HTTP 409 `vehicle_identifier_conflict`. Esta
unicidad continúa clasificada como hipótesis técnica y deberá revisarse con
equipos reales.

## 5. Evidencia de verificación

- 127 pruebas aprobadas en la suite completa;
- una prueba auxiliar de logging se separó de la nueva ruta real y la suite
  completa volvió a ejecutarse sin fallos;
- 10 pruebas HTTP específicas de Vehicles aprobadas contra PostgreSQL;
- matriz completa de transiciones y asignabilidad comprobadas;
- cinco Roles, aislamiento entre Teams y errores seguros cubiertos;
- 95.65 % de cobertura total, superior al 90 %;
- Ruff y mypy estricto aprobados;
- `alembic check` sin operaciones pendientes y dependencias sanas;
- stack Docker saludable, migración en `20261108_0003_operations (head)`;
- runtime con UID `10001`, sin pytest, y seis rutas Vehicle en OpenAPI;
- `/health` y `/ready` respondieron HTTP 200.

El enlace de CI se incorporará al publicar el commit.

## 6. Control de alcance

No se implementó Maintenance Record, inventario, setup técnico, Session ni
frontend. Marcar `MAINTENANCE` sólo expresa disponibilidad; no crea una orden
de trabajo. La asignación real Driver/Vehicle queda para Fase 8 y el historial
de mantenimiento para Fase 10.

## 7. Punto de aprobación

Este bloque queda listo para revisión del propietario una vez que la suite
final y CI estén verdes. Con aprobación comienza el Bloque 7.5: APIs de Tracks
y Events, vínculo obligatorio dentro del mismo Team, fechas y estados válidos.
