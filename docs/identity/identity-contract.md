# RaceOps — Contrato de identidad y autorización

## 1. Información del documento

- **Fase:** 6 — Identidad y autorización
- **Bloque:** 6.1 — Contrato de identidad
- **Versión:** 0.1
- **Estado:** Preparado para aprobación
- **Alcance:** P0; monolito modular; API `/api/v1`

Este documento fija el comportamiento que implementarán los bloques 6.2 a
6.6. Todavía no crea tablas, endpoints ni credenciales reales.

## 2. Evidencia y naturaleza de las decisiones

| Decisión | Clasificación | Justificación |
|---|---|---|
| Cinco roles iniciales | Respaldada por evidencia | Los participantes consumen y restringen información de manera diferente |
| RBAC y visibilidad server-side | Fuertemente respaldada | Parte del setup técnico no debe llegar automáticamente al Driver ni a roles administrativos |
| Equipo como frontera de ownership | Parcialmente respaldada + necesidad técnica | RaceOps se dirige a equipos pequeños, pero todavía no se valida como SaaS multi-tenant |
| Varias membresías por User | Hipótesis técnica controlada | Evita una restricción irreversible; P0 sigue operando en un solo Team por token |
| Bootstrap sin registro público | Necesidad técnica de alcance | Permite iniciar el sistema sin construir onboarding comercial no validado |
| JWT breve sin refresh token | Decisión de seguridad y simplicidad | Reduce estado y superficie de ataque durante el MVP |

Permitir varias membresías no afirma que el mercado lo necesite. El modelo lo
tolera con una restricción simple y la interfaz P0 no optimizará todavía el
cambio frecuente entre equipos.

## 3. Decisiones del contrato

1. No existe registro público en P0.
2. El primer `Administrator`, su `Team` y su `TeamMembership` se crean mediante
   un comando de bootstrap local.
3. Un `User` puede tener membresías activas en diferentes Teams.
4. Sólo puede existir una `TeamMembership` por par `(user_id, team_id)`.
5. Cada membresía tiene exactamente un rol principal.
6. Cada access token selecciona exactamente una membresía activa.
7. El token identifica al User y a la Membership, pero no contiene Role,
   permisos ni datos técnicos.
8. Cada petición protegida vuelve a consultar User, Membership, Team y Role en
   PostgreSQL.
9. El acceso se desactiva sin eliminar autoría ni relaciones históricas.
10. No hay refresh token, recuperación de password, OAuth externo ni ABAC en
    P0.

## 4. Modelo lógico

### 4.1 Team

| Campo | Tipo lógico | Regla |
|---|---|---|
| `team_id` | UUID | Generado por servidor; inmutable |
| `name` | string 1–120 | Obligatorio; se recorta espacio exterior |
| `status` | `ACTIVE`, `INACTIVE` | Inicia `ACTIVE` |
| `created_at` | instante UTC | Generado por servidor |
| `updated_at` | instante UTC | Generado por servidor |

### 4.2 User

| Campo | Tipo lógico | Regla |
|---|---|---|
| `user_id` | UUID | Generado por servidor; inmutable |
| `email` | email normalizado | Único globalmente; no distingue mayúsculas |
| `password_hash` | string | Argon2id; nunca se serializa |
| `status` | `ACTIVE`, `INACTIVE` | Inicia `ACTIVE` |
| `created_at` | instante UTC | Generado por servidor |
| `updated_at` | instante UTC | Generado por servidor |

El email se normaliza recortando espacios exteriores y convirtiéndolo a
minúsculas antes de comparar o persistir. Esta regla pragmática se documenta
para evitar identidades duplicadas por capitalización.

### 4.3 TeamMembership

| Campo | Tipo lógico | Regla |
|---|---|---|
| `membership_id` | UUID | Generado por servidor; inmutable |
| `user_id` | UUID FK | User existente |
| `team_id` | UUID FK | Team existente |
| `role` | Role | Un rol principal |
| `status` | `ACTIVE`, `INACTIVE` | Inicia `ACTIVE` |
| `created_at` | instante UTC | Generado por servidor |
| `updated_at` | instante UTC | Generado por servidor |

Restricciones:

- unicidad de `(user_id, team_id)`;
- una membresía `ACTIVE` exige User y Team activos;
- no existe borrado físico mediante el flujo normal;
- un cambio de Role no modifica historia creada anteriormente.

### 4.4 Role

Valores estables de API y persistencia:

- `ADMINISTRATOR`;
- `TEAM_MANAGER`;
- `ENGINEER`;
- `MECHANIC`;
- `DRIVER`.

El rol pertenece a la membresía, no al User global. Un mismo User podría ser
`ENGINEER` en un Team y `DRIVER` en otro.

## 5. Credenciales

- Password de 12 a 128 caracteres Unicode.
- Se permiten espacios y gestores de contraseñas.
- No se imponen reglas artificiales de mayúsculas, números o símbolos.
- Nunca se trunca silenciosamente.
- Se persiste únicamente el hash Argon2id con parámetros versionables.
- Password, hash y access token nunca aparecen en logs.

La verificación de contraseñas comprometidas y la recuperación de acceso no
pertenecen a P0; deberán decidirse antes de operar con usuarios reales fuera
de un entorno controlado.

## 6. Flujo de bootstrap

Comando previsto:

```text
python -m raceops.iam.bootstrap_admin --email <email> --team-name <name>
```

Reglas:

1. solicita el password de forma interactiva mediante entrada oculta;
2. crea Team, User y Membership `ADMINISTRATOR` en una sola transacción;
3. no acepta el password como argumento visible;
4. falla sin cambios parciales ante email o Team incompatible;
5. no imprime password, hash ni token;
6. registra únicamente identificadores no secretos y resultado.

El bootstrap no es un endpoint HTTP ni un sustituto de la futura gestión de
miembros por Administrator, clasificada P1.

## 7. Contrato de autenticación

### 7.1 Login

```text
POST /api/v1/auth/login
Content-Type: application/json
```

Request:

```json
{
  "email": "engineer@example.com",
  "password": "a-long-user-password",
  "team_id": "3bd43187-e6a8-4efa-a1ef-12d32c375023"
}
```

`team_id` es opcional cuando el User tiene exactamente una Membership activa.

Selección de contexto:

- cero membresías activas: rechazo genérico;
- una membresía activa y sin `team_id`: se selecciona automáticamente;
- varias membresías activas y `team_id` válido: se selecciona esa membresía;
- varias membresías y sin `team_id`: `409 team_context_required` después de
  validar correctamente las credenciales;
- `team_id` ajeno o inactivo: rechazo genérico, sin confirmar existencia.

Respuesta `200`:

```json
{
  "access_token": "<redacted>",
  "token_type": "bearer",
  "expires_in": 900
}
```

La respuesta no devuelve User, Membership ni Role; el cliente consulta
`/auth/me` como fuente autorizada.

### 7.2 Identidad actual

```text
GET /api/v1/auth/me
Authorization: Bearer <access-token>
```

Respuesta `200`:

```json
{
  "user": {
    "user_id": "8f23e131-9150-42bd-91fa-93d46100408e",
    "email": "engineer@example.com",
    "status": "ACTIVE"
  },
  "team": {
    "team_id": "3bd43187-e6a8-4efa-a1ef-12d32c375023",
    "name": "Example Racing Team",
    "status": "ACTIVE"
  },
  "membership": {
    "membership_id": "095a5072-ed71-4efa-98af-c012ed3b412f",
    "role": "ENGINEER",
    "status": "ACTIVE"
  }
}
```

Ninguna respuesta serializa `password`, `password_hash`, parámetros Argon2id,
`jti` ni permisos calculados internamente.

## 8. Contrato del access token

- formato JWT firmado;
- TTL configurable, 15 minutos por defecto y máximo 60;
- algoritmo y librería se fijarán en el Bloque 6.3;
- claims: `sub`, `mid`, `jti`, `iat`, `exp`;
- `sub`: `user_id`;
- `mid`: `membership_id` seleccionada;
- no contiene `role`, `team_id`, email, nombre ni permisos.

En cada petición se resuelve `mid → Membership → User + Team + Role` y se
comprueba que las tres entidades continúen activas. Así, desactivar acceso o
cambiar Role surte efecto inmediato sin esperar al vencimiento.

## 9. Orden de autorización

Toda operación protegida verifica:

1. bearer token presente, firmado y no vencido;
2. User activo y coincidente con `sub`;
3. Membership activa y coincidente con `mid` y User;
4. Team activo;
5. permiso del Role;
6. ownership del recurso dentro del Team activo;
7. Visibility y relación específica con el recurso;
8. invariantes del caso de uso.

Un identificador externo nunca selecciona el Team autorizado por sí mismo.
El `team_id` de recursos se deriva del actor resuelto y se valida en servidor.

## 10. Errores estables

Todos utilizan `application/problem+json`.

| HTTP | `code` | Uso |
|---:|---|---|
| 401 | `invalid_credentials` | Login incorrecto, User/Team/Membership inactivo o contexto solicitado inválido |
| 409 | `team_context_required` | Credenciales válidas con varias membresías y sin selección |
| 401 | `invalid_access_token` | Token ausente, vencido, manipulado o identidad actualmente inactiva |
| 403 | `insufficient_permissions` | Actor autenticado conoce el recurso pero su Role no permite la operación |
| 404 | `resource_not_found` | Recurso inexistente o perteneciente a otro Team |
| 409 | `identity_conflict` | Conflicto de unicidad o transición de estado |
| 422 | `validation_error` | Payload fuera del contrato |

Las respuestas `401` incluyen `WWW-Authenticate: Bearer` cuando corresponda.
`invalid_credentials` usa siempre el mismo título y detalle visible.

Cuando `team_context_required` sea necesario, la respuesta podrá incluir una
lista mínima de Teams activos (`team_id`, `name`) porque las credenciales ya
fueron validadas. Nunca incluye Role ni datos de otros usuarios.

## 11. Logging y auditoría

Se registra sin secretos:

- login exitoso: `user_id`, `membership_id`, `team_id`, `request_id`;
- login fallido: email pseudonimizado o hash operacional, motivo interno no
  expuesto y `request_id`;
- cambio de Role o estado: actor, objetivo, valor anterior/nuevo e instante;
- bootstrap: IDs creados y resultado.

No se registra password, hash, JWT, header `Authorization` ni body completo de
login.

## 12. Escenarios obligatorios de prueba

1. Login válido con una membresía.
2. Login válido seleccionando una de varias membresías.
3. Varias membresías sin selección producen `team_context_required`.
4. Password incorrecto, email inexistente y User inactivo son indistinguibles
   externamente.
5. Token válido, vencido y manipulado.
6. Token cuyo User, Membership o Team fue desactivado.
7. Cambio de Role efectivo en la petición siguiente.
8. ID válido de otro Team produce `404` sin fuga de datos.
9. Driver no obtiene contenido `ENGINEERING_CONFIDENTIAL`.
10. Ningún schema ni log contiene password, hash o token.
11. Bootstrap exitoso y rollback completo ante conflicto.
12. Migración `upgrade → downgrade → upgrade` conserva el contrato físico.

## 13. Fuera del Bloque 6.1

- modelos SQLAlchemy y migración Alembic;
- implementación Argon2id y JWT;
- routers y dependencias FastAPI;
- API P1 para crear, desactivar o cambiar roles de miembros;
- recuperación o cambio de password;
- refresh tokens y revocación individual de `jti`;
- OAuth, SSO, MFA, invitaciones y registro público;
- frontend de login.

## 14. Punto de aprobación

Al aprobar este contrato se autoriza comenzar el Bloque 6.2:

- enums y modelos SQLAlchemy;
- constraints e índices;
- migración Alembic;
- pruebas de persistencia y migraciones.

Los parámetros criptográficos y la librería JWT se confirmarán en el Bloque
6.3 sin cambiar el comportamiento público aquí definido.

