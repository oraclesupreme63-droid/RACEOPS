# RaceOps — Trazabilidad de implementación de Fase 7

## 1. Alcance

Esta matriz conecta los requisitos de la base operativa con código y pruebas.
No afirma que el flujo de Session esté implementado: esa comprobación pertenece
a Fase 8.

| Alcance | Implementación principal | Evidencia de pruebas | Estado |
|---|---|---|---|
| RF-013–RF-017 / AC-005 / BL-013 | `drivers/models.py`, `services.py`, `router.py` | `test_drivers.py` y persistencia operativa | Implementado |
| RF-018–RF-023 / BL-014 | `vehicles/models.py`, `services.py`, `router.py` | `test_vehicles.py`, estados y aislamiento | Implementado |
| AC-006 | Predicado `Vehicle.is_assignable` y estados explícitos | pruebas unitarias y HTTP de transiciones | Parcial: rechazo al asignar se completa con Session en Fase 8 |
| RF-024–RF-025 / BL-015 | `tracks/models.py`, `services.py`, `router.py` | `test_tracks_events.py` | Implementado |
| RF-026–RF-030 / AC-007 / BL-016 | `events/models.py`, `services.py`, `router.py` | `test_tracks_events.py`, fechas, estados y Teams | Implementado |
| AC-008 | Sin endpoints DELETE; estados y constraints conservan historia | OpenAPI, API e integración | Implementado para los cuatro recursos |

## 2. Reglas transversales verificadas

- ownership siempre derivado de la Membership activa;
- consultas limitadas al Team activo y UUID ajenos ocultos con HTTP 404;
- RBAC deniega por defecto y cubre los cinco Roles;
- estados cambian mediante comandos explícitos, no por edición arbitraria;
- Driver sigue separado de User y su vínculo es opcional y del mismo Team;
- no existe borrado físico en la API normal;
- PostgreSQL aplica FKs, unicidad e invariantes críticas.

## 3. Evidencia de calidad

La suite final del Bloque 7.5 aprobó 136 pruebas con 94.84 % de cobertura.
Ruff, mypy, `alembic check`, el stack Docker y los smoke tests aprobaron. La
misma revisión pasó en
[GitHub Actions 42638867811](https://github.com/oraclesupreme63-droid/RACEOPS/actions/runs/42638867811).

## 4. Frontera pendiente

La asignación Event + Driver + Vehicle, el rechazo de Driver inactivo o Vehicle
no `READY` y el acceso relacionado de Driver requieren Session. Se prueban de
extremo a extremo en Fase 8 y no son una carencia del contrato de Fase 7.
