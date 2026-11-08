# RaceOps — Reporte del Bloque 6.3: credenciales y tokens

## 1. Estado

- **Fecha:** 8 de noviembre de 2026
- **Fase:** 6 — Identidad y autorización
- **Bloque:** 6.3 — Credenciales y tokens
- **Resultado:** Implementado, verificado y aprobado
- **Fecha de aprobación:** 8 de noviembre de 2026
- **Siguiente bloque:** 6.4 — API de identidad

## 2. Decisiones de seguridad

Se eligieron componentes mantenidos y compatibles con el stack actual:

- `pwdlib[argon2]` 0.3.x con `PasswordHash.recommended()` para Argon2id;
- PyJWT 2.x con firma `HS256`;
- access token de 15 minutos por defecto, configurable entre 5 y 60;
- claims mínimos `sub`, `mid`, `jti`, `iat` y `exp`;
- Role, Team, email y permisos no se copian al token.

Las versiones se acotaron por versión mayor/menor para recibir correcciones
compatibles sin aceptar cambios mayores implícitos. La selección sigue la guía
oficial de seguridad de FastAPI, la documentación de pwdlib y la validación de
claims de PyJWT.

Referencias:

- <https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/>;
- <https://frankie567.github.io/pwdlib/>;
- <https://pyjwt.readthedocs.io/en/latest/usage.html>.

## 3. Contraseñas

La política implementada acepta entre 12 y 128 caracteres Unicode. No exige
combinaciones artificiales de mayúsculas, números o símbolos y no trunca el
valor. Antes de persistir:

1. valida la longitud completa;
2. genera un hash Argon2id con salt;
3. descarta el texto plano al terminar el caso de uso.

La verificación rechaza de forma segura passwords fuera de política, hashes
desconocidos y valores incorrectos. Ningún schema, log ni argumento CLI recibe
el hash o el password.

## 4. Access token y resolución actual

El token selecciona exactamente un User y una TeamMembership. La validación:

1. restringe explícitamente el algoritmo permitido a `HS256`;
2. exige los cinco claims;
3. comprueba firma y vencimiento;
4. valida que `sub`, `mid` y `jti` sean UUID;
5. rechaza intervalos temporales incoherentes.

Después, PostgreSQL resuelve `Membership → User + Team + Role`. User,
Membership y Team deben continuar `ACTIVE`. Como Role se consulta en cada
petición, un cambio tiene efecto inmediato sin esperar a que venza el JWT.

## 5. Bootstrap administrativo

Comando:

```powershell
.\.venv\Scripts\python.exe -m raceops.iam.bootstrap_admin `
  --email admin@example.com `
  --team-name "Example Racing Team"
```

El comando:

- normaliza email y nombre del Team;
- pide y confirma el password con entrada oculta;
- no admite `--password`;
- crea Team, User y Membership `ADMINISTRATOR` en una transacción;
- revierte todo ante conflicto;
- registra únicamente los UUID creados y el resultado.

## 6. Evidencia de verificación

Resultado local final antes de documentación:

- 59 pruebas aprobadas;
- 93.13 % de cobertura, con mínimo obligatorio de 90 %;
- 13 pruebas PostgreSQL de integración en total;
- Ruff format y lint aprobados;
- mypy estricto aprobado en 40 archivos.

Los escenarios nuevos comprueban:

- hash Argon2id sin texto plano;
- password válido, incorrecto, corto, largo y Unicode;
- token válido, vencido, manipulado, incompleto y mal formado;
- rechazo individual al desactivar User, Membership o Team;
- cambio de Role visible en la siguiente resolución;
- referencias de User y Membership incongruentes;
- bootstrap exitoso;
- rollback completo del bootstrap ante email duplicado;
- password oculto y ausente de los argumentos CLI.

## 7. Límites conscientes

Este bloque todavía no implementa:

- `POST /api/v1/auth/login`;
- `GET /api/v1/auth/me`;
- selección HTTP entre varias membresías;
- respuestas RFC 9457 de autenticación;
- dependencias FastAPI de actor actual;
- políticas RBAC ni aislamiento de recursos;
- refresh tokens, recuperación de password, OAuth, SSO o MFA.

La implementación interna está lista para que el Bloque 6.4 exponga el
contrato HTTP sin duplicar reglas criptográficas o de identidad.

## 8. Archivos principales

- `src/raceops/iam/credentials.py`;
- `src/raceops/iam/tokens.py`;
- `src/raceops/iam/identity.py`;
- `src/raceops/iam/bootstrap_admin.py`;
- `tests/unit/iam/test_credentials.py`;
- `tests/unit/iam/test_tokens.py`;
- `tests/unit/iam/test_bootstrap_admin.py`;
- `tests/integration/test_identity_security.py`.

## 9. Punto de aprobación

Al aprobar este bloque comienza 6.4:

1. servicio de autenticación por email, password y contexto de Team;
2. `POST /api/v1/auth/login`;
3. `GET /api/v1/auth/me`;
4. schemas que nunca serializan credenciales ni hashes;
5. errores RFC 9457 estables y OpenAPI;
6. pruebas positivas, negativas y de no filtración.
