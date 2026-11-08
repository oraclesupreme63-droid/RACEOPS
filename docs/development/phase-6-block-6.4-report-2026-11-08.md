# RaceOps — Reporte del Bloque 6.4: API de identidad

## 1. Estado

- **Fecha:** 8 de noviembre de 2026
- **Fase:** 6 — Identidad y autorización
- **Bloque:** 6.4 — API de identidad
- **Resultado:** Implementado y verificado; pendiente de aprobación
- **Siguiente bloque:** 6.5 — RBAC y aislamiento

## 2. Resultado implementado

RaceOps expone por primera vez el contrato HTTP de identidad:

```text
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

El login normaliza el email, verifica Argon2id, exige User, Membership y Team
activos, selecciona exactamente una Membership y emite un JWT breve. `/me`
valida el bearer token y vuelve a consultar la identidad actual en PostgreSQL.

## 3. Selección del Team

El comportamiento implementado conserva el contrato aprobado:

- una Membership activa sin `team_id`: se selecciona automáticamente;
- varias Memberships y `team_id` válido: se selecciona el Team solicitado;
- varias Memberships sin selección: `409 team_context_required`;
- Team ajeno, inexistente o inactivo: `401 invalid_credentials`;
- cero Memberships activas: `401 invalid_credentials`.

La respuesta `team_context_required` sólo aparece después de verificar email y
password. Expone exclusivamente `team_id` y nombre de los Teams autorizados;
no incluye Role, otros usuarios ni datos técnicos.

## 4. Protección contra enumeración y filtraciones

Email inexistente, password incorrecto, User inactivo, Membership inactiva,
Team inactivo y contexto inválido comparten el mismo problema público:

```json
{
  "title": "Invalid credentials",
  "status": 401,
  "code": "invalid_credentials",
  "detail": "The supplied credentials or team context are invalid."
}
```

Cuando el email no existe se ejecuta una verificación contra un hash Argon2id
ficticio para reducir diferencias de tiempo útiles para enumeración. El motivo
interno se registra sin email, password, hash ni cuerpo de la petición.

## 5. Identidad actual

`GET /api/v1/auth/me` devuelve:

- User: UUID, email y estado;
- Team: UUID, nombre y estado;
- Membership: UUID, Role y estado.

Nunca devuelve password, `password_hash`, parámetros Argon2id, JWT, `jti` ni
permisos internos. Un token ausente, vencido, manipulado o asociado a una
identidad desactivada produce `401 invalid_access_token` y
`WWW-Authenticate: Bearer`.

Role no se obtiene del token. Una modificación en PostgreSQL aparece en la
siguiente llamada a `/me` sin volver a iniciar sesión.

## 6. OpenAPI y errores

- ambos endpoints aparecen bajo `/api/v1/auth`;
- `/auth/me` declara autenticación HTTP Bearer con formato JWT;
- login documenta respuestas 401, 409 y 422;
- la extensión 409 documenta la lista mínima de Teams;
- los errores controlados utilizan `application/problem+json`;
- la validación no devuelve los valores rechazados.

## 7. Evidencia de verificación

Resultado local:

- 71 pruebas aprobadas;
- 94.35 % de cobertura, con mínimo obligatorio de 90 %;
- 12 escenarios nuevos en `tests/api/test_identity.py`;
- Ruff format y lint aprobados;
- mypy estricto aprobado en 44 archivos;
- `alembic check` sin operaciones nuevas;
- ninguna migración nueva: el esquema de 6.2 ya soporta este bloque.

Los escenarios HTTP comprueban:

1. login con una Membership y consulta posterior de `/me`;
2. solicitud y selección entre múltiples Teams;
3. seis causas de rechazo con una respuesta pública indistinguible;
4. token ausente, manipulado, vencido e identidad desactivada;
5. cambio de Role visible sin reemitir token;
6. ausencia de password, hash, JWT y `jti` en respuestas y logs;
7. contrato OpenAPI y esquema HTTP Bearer.

## 8. Archivos principales

- `src/raceops/iam/authentication.py`;
- `src/raceops/iam/schemas.py`;
- `src/raceops/iam/router.py`;
- `src/raceops/api/dependencies.py`;
- `src/raceops/api/errors.py`;
- `tests/api/test_identity.py`.

## 9. Límites conscientes

Este bloque todavía no implementa:

- permisos por operación;
- aislamiento de recursos pertenecientes a otros Teams;
- Visibility de contenido técnico;
- endpoints para invitar o administrar miembros;
- refresh token, recuperación de password, OAuth, SSO o MFA;
- frontend propio de autenticación.

Swagger permite verificar el contrato, pero no sustituye la interfaz web que
se consolidará más adelante.

## 10. Punto de aprobación

Al aprobar este bloque comienza 6.5:

1. actor autenticado reutilizable;
2. matriz de permisos de menor privilegio;
3. dependencias de autorización por Role;
4. aislamiento entre Teams con `404` seguro;
5. base de Visibility para módulos posteriores;
6. pruebas positivas y negativas por cada Role.
