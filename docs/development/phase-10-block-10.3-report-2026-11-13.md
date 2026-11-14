# Fase 10 — Reporte del Bloque 10.3

**Fecha:** 13 de noviembre de 2026

**Estado:** aprobado por el propietario; CI global aprobada

## Resultado

RaceOps ya permite crear, listar y consultar mantenimiento mediante la API
real. La frontera es deliberadamente mínima: no acepta estado, Team,
visibilidad, timestamps ni relaciones causales controladas por el cliente.

## Permisos

| Role | Leer | Crear |
|---|---:|---:|
| Administrator | Sí | No |
| Team Manager | Sí | Sí |
| Engineer | Sí | Sí |
| Mechanic | Sí | Sí |
| Driver | No | No |

## Implementación

- permisos `READ_MAINTENANCE` y `WRITE_MAINTENANCE`;
- schemas Pydantic con `extra="forbid"` y texto normalizado;
- `POST /api/v1/maintenance-records`;
- `GET /api/v1/maintenance-records`;
- `GET /api/v1/maintenance-records/{maintenance_id}`;
- filtros por Vehicle, tipo y estado antes del conteo;
- responsable con User y Membership activos en el Team;
- respuestas sin `team_id` ni `visibility_level`;
- logging estructurado de creación.

## Límites deliberados

- no existe PATCH;
- no existen comandos `start`, `complete` o `cancel`;
- Session, Observation y Action no se aceptan todavía;
- crear un registro no cambia disponibilidad del Vehicle.

## Verificación dirigida

- 19 pruebas unitarias relacionadas aprobadas;
- 8 pruebas HTTP PostgreSQL aprobadas;
- Ruff, MyPy y `git diff --check` aprobados;
- OpenAPI expone sólo colección `GET/POST` y detalle `GET`.

## Siguiente bloque condicionado

El propietario aprobó el bloque. El commit `da32f78` superó la ejecución CI
`43532136973` con 255 pruebas, cobertura de 92.00 %, migraciones y contenedor
saludable. Continúa 10.4 — ciclo de intervención.
