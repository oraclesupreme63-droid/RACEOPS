# Fase 10 — Reporte del Bloque 10.5

**Fecha:** 13 de noviembre de 2026

**Estado:** implementación y verificación enfocada terminadas; pendiente de
CI global y aprobación del propietario

## Resultado

RaceOps ya puede conservar y recuperar el contexto que llevó a una
intervención:

```text
Session → Observation → Mechanical Action → Maintenance Record
```

La cadena no se infiere. Cada referencia es opcional y sólo existe cuando un
usuario autorizado la proporciona expresamente.

## API implementada

- `POST /api/v1/maintenance-records` acepta `session_id`, `observation_id` y
  `action_id` opcionales;
- `GET /api/v1/maintenance-records` permite filtrar por `session_id` antes del
  conteo;
- `GET /api/v1/maintenance-records/{maintenance_id}/causal-chain` recupera los
  nodos explícitamente relacionados.

## Reglas protegidas

- toda referencia pertenece al Team activo y debe ser visible para el actor;
- Session, Observation y Action deben corresponder al Vehicle intervenido;
- si varios nodos aportan una Session, todos deben referirse a la misma;
- únicamente una Action `MECHANICAL` puede originar mantenimiento;
- las filas Session se bloquean durante validación y persistencia para evitar
  que cambie el Vehicle concurrentemente;
- un recurso extranjero se oculta como 404;
- una relación visible pero incompatible responde
  `maintenance_context_conflict`;
- cualquier fallo ocurre antes de insertar el Maintenance Record.

## Confidencialidad

El endpoint causal requiere `READ_MAINTENANCE`; Driver continúa excluido. La
Action se serializa con la proyección existente por Role, evitando revelar
detalle confidencial fuera de Engineering. Los filtros existentes de
Observation y Action se conservan y un nodo no visible se representa como
ausente, sin exponer su contenido.

## Verificación enfocada

- 18 pruebas unitarias de mantenimiento aprobadas;
- 14 pruebas HTTP de mantenimiento aprobadas contra PostgreSQL;
- 4 pruebas de persistencia y concurrencia aprobadas;
- 36 casos enfocados aprobados en total;
- Ruff y MyPy aprobados sobre los archivos modificados;
- OpenAPI documenta referencias, filtro y endpoint causal.

Durante una ejecución combinada, PostgreSQL local dejó de aceptar conexiones y
dos casos terminaron por `ConnectionTimeout`; el contenedor permaneció healthy
y ambos casos aprobaron al repetirse de forma aislada. No se observó fallo de
dominio ni escritura parcial. La suite global posterior no reprodujo el
incidente.

## Verificación global local

- 272 pruebas aprobadas;
- cobertura total de 92.21 % frente al mínimo de 90 %;
- Ruff format, Ruff check y MyPy estricto aprobados;
- `alembic check` sin operaciones pendientes;
- no se necesita una migración nueva porque las tres FKs opcionales existen
  desde el Bloque 10.2.

La construcción y prueba de humo del contenedor corresponden a CI después del
commit del bloque.

## Siguiente bloque condicionado

Con aprobación comienza 10.6 — disponibilidad segura: separar la capacidad de
editar un Vehicle de los comandos que lo retiran o liberan para pista y
registrar quién ejecuta la liberación.
