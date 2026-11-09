# RaceOps — Reporte del Bloque 7.3: API de Drivers

## 1. Estado

- **Fecha:** 8 de noviembre de 2026
- **Fase:** 7 — Base operativa
- **Bloque:** 7.3 — API de Drivers
- **Resultado:** implementado y verificado; pendiente de aprobación del propietario
- **Siguiente bloque:** 7.4 — API de Vehicles

## 2. Resultado funcional

RaceOps ya ofrece el primer recurso operativo completo bajo `/api/v1`:

- crear Driver dentro del Team activo;
- listar con paginación estable y filtro por estado;
- consultar un Driver autorizado;
- actualizar nombre y vínculo opcional con User;
- activar y desactivar mediante acciones explícitas e idempotentes;
- conservar el registro sin endpoint DELETE.

El cliente nunca suministra ownership. `team_id` se deriva de
`CurrentIdentity` y está prohibido en el body y ausente de la respuesta.

## 3. Autorización y privacidad

Se incorporó `READ_DRIVERS` como permiso diferente de `MANAGE_DRIVERS`:

- Administrator y Team Manager administran y consultan;
- Engineer y Mechanic consultan Drivers del Team activo;
- Driver consulta exclusivamente el perfil cuyo `user_id` coincide con su
  identidad actual.

Los filtros de Team y relación se aplican antes del conteo y la paginación.
Un UUID inexistente, de otro Team o no relacionado con el Driver responde
`404 resource_not_found`. La API no revela nombres, conteos ni existencia de
pilotos ajenos.

## 4. Vínculo Driver/User

Un vínculo nuevo exige User y Membership activos en el mismo Team. RaceOps
rechaza User ajeno, inactivo o ya vinculado con el mismo problema estable:
HTTP 409 `driver_user_conflict`. Esto evita filtrar cuál de esas condiciones
ocurrió. Un PATCH con `user_id: null` desvincula sin borrar Driver ni User.

## 5. Corrección transversal de logging

La suite reveló que la configuración estándar de Alembic deshabilitaba
loggers existentes después de ejecutar una migración dentro del mismo proceso.
Alembic ahora conserva loggers externos y RaceOps reactiva de forma explícita
sólo su namespace. El handler estructurado resuelve el stdout activo al emitir,
lo que mantiene logs durante recargas y captura de pruebas sin retener streams
anteriores.

## 6. Evidencia de verificación

- 112 pruebas aprobadas;
- 95.32 % de cobertura total, superior al mínimo de 90 %;
- 9 pruebas HTTP específicas de Drivers;
- casos positivos y negativos para los cinco Roles;
- aislamiento entre Teams y alcance propio del Driver comprobados;
- Ruff format y lint aprobados;
- mypy estricto aprobado sobre 56 archivos fuente;
- `pip check` sin dependencias rotas;
- `alembic check` sin operaciones pendientes;
- stack Docker saludable, runtime UID `10001` y sin pytest;
- `/health` y `/ready` respondieron HTTP 200;
- OpenAPI del contenedor publicó `GET` y `POST /api/v1/drivers`.

## 7. Control de alcance

No se implementaron Vehicles, Tracks, Events, Sessions ni un frontend. La
regla que impide asignar un Driver inactivo se consumirá en Fase 8, cuando
exista Session; este bloque deja el estado y la API listos sin crear una
asignación ficticia.

## 8. Punto de aprobación

Al aprobar este reporte comienza el Bloque 7.4. Allí se implementará la API de
Vehicles con transiciones válidas, `RETIRED` terminal, `READY` como único
estado asignable, RBAC, aislamiento por Team y pruebas HTTP. Sin aprobación no
se inicia ese bloque.
