# RaceOps — Reporte del Bloque 6.2: persistencia de identidad

## 1. Estado

- **Fecha:** 8 de noviembre de 2026
- **Fase:** 6 — Identidad y autorización
- **Bloque:** 6.2 — Persistencia
- **Resultado:** Implementado y verificado; pendiente de aprobación
- **Siguiente bloque:** 6.3 — Credenciales y tokens

## 2. Resultado implementado

Se agregó el módulo interno `iam` con:

- `IdentityStatus`: `ACTIVE`, `INACTIVE`;
- `Role`: `ADMINISTRATOR`, `TEAM_MANAGER`, `ENGINEER`, `MECHANIC`, `DRIVER`;
- modelos SQLAlchemy `Team`, `User` y `TeamMembership`;
- UUID generados por la aplicación;
- `created_at` y `updated_at` con timestamps UTC respaldados por PostgreSQL;
- relaciones bidireccionales sin cascada de borrado histórico.

## 3. Integridad persistida

La revisión Alembic `20261108_0002_identity` crea:

- tablas `teams`, `users` y `team_memberships`;
- enums nativos `identity_status` y `team_role`;
- email globalmente único, normalizado y limitado a 254 caracteres;
- password hash obligatorio y no vacío, todavía sin implementar hashing;
- unicidad `(user_id, team_id)`;
- índice de búsqueda por `team_id`;
- FK con `ON DELETE RESTRICT` para preservar historia;
- defaults `ACTIVE` y timestamps de servidor.

Un User puede tener Memberships en Teams diferentes, pero no dos Memberships
para el mismo Team.

La regla «Membership activa requiere User y Team activos» no se implementó
mediante trigger ni un `CHECK` inválido entre tablas. Las FK protegen existencia
y el servicio de aplicación validará estados dentro de la transacción en los
siguientes bloques.

## 4. Migración

Cadena actual:

```text
20261024_0001
    ↓
20261108_0002_identity
```

El downgrade elimina primero memberships, después users y teams, y finalmente
los tipos enum. El round-trip completo quedó probado contra PostgreSQL 18.6.

## 5. Pruebas y evidencia

Resultado local final:

- 31 pruebas aprobadas;
- 91.94 % de cobertura, con mínimo obligatorio de 90 %;
- 5 pruebas PostgreSQL de integración aprobadas;
- Ruff format y lint aprobados;
- mypy estricto aprobado en 31 archivos;
- `alembic check`: sin nuevas operaciones detectadas;
- migración `upgrade → downgrade → upgrade` aprobada.

Las pruebas cubren:

- valores estables de enums;
- tablas, columnas, defaults, constraints, índices y FK;
- un User con Memberships en dos Teams;
- rechazo de email no normalizado;
- rechazo de email duplicado;
- rechazo de Membership duplicada dentro del mismo Team;
- rechazo del borrado de User o Team referenciado por una Membership;
- reversibilidad completa de migraciones.

## 6. Límites conscientes

Este bloque todavía no incluye:

- hash Argon2id real;
- emisión o validación JWT;
- resolución de identidad activa;
- comando de bootstrap;
- login, `/auth/me` o RBAC;
- creación de usuarios mediante API.

Los valores parecidos a hashes utilizados en integración son placeholders; no
se presentan como credenciales seguras.

## 7. Archivos principales

- `src/raceops/iam/enums.py`;
- `src/raceops/iam/models.py`;
- `src/raceops/db/base.py`;
- `migrations/versions/20261108_0002_identity_persistence.py`;
- `tests/unit/iam/test_models.py`;
- `tests/integration/test_identity_persistence.py`;
- `tests/integration/test_migrations.py`.

## 8. Punto de aprobación

Al aprobar este bloque comienza 6.3:

1. selección de bibliotecas mantenidas para Argon2id y JWT;
2. servicio de password sin truncamiento ni exposición;
3. emisión de access tokens breves con `sub`, `mid`, `jti`, `iat`, `exp`;
4. resolución server-side de User, Membership, Team y Role activos;
5. comando transaccional de bootstrap;
6. pruebas de token válido, vencido, manipulado e identidad inactiva.

