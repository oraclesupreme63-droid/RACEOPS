# RaceOps — Estrategia de seguridad

## 1. Información del documento

- **Versión:** 1.1
- **Estado:** Implementado hasta el alcance de Fase 6
- **Modelo inicial:** JWT + RBAC + ownership por Team + Visibility

## 2. Límites

RaceOps v1 utilizará controles simples y explícitos. No se construirá ABAC
genérico, proveedor de identidad propio ni multi-tenancy comercial. La
autorización real vive en el backend; ocultar un botón en frontend nunca es
un control suficiente.

## 3. Autenticación

- Passwords se almacenan con Argon2id mediante una biblioteca mantenida.
- Nunca se limita silenciosamente el password antes de aplicar el hash.
- Login devuelve un JWT de acceso firmado, con expiración breve configurable.
- Claims mínimos: `sub`, `mid`, `jti`, `iat` y `exp`. `mid` selecciona una
  TeamMembership; el token no contiene Role, Team ID, email, permisos ni datos
  técnicos.
- Cada petición resuelve en base de datos el User, TeamMembership y Team activos;
  así, desactivar una cuenta o cambiar un rol surte efecto sin esperar al
  vencimiento de un token largo.
- La API recibe `Authorization: Bearer`. El cliente web P0 mantiene el token
  sólo en memoria: no `localStorage` ni `sessionStorage`.
- No habrá refresh token en P0. Recargar la página puede requerir iniciar
  sesión otra vez; se reevaluará con usuarios antes de agregar complejidad.
- Logout P0 descarta el token del cliente. El servidor continúa verificando
  que el usuario y membership estén activos.
- Si un User tiene varias Memberships activas, login selecciona una por token;
  no existe token multi-Team ni cambio de contexto implícito en P0.

HTTPS será obligatorio fuera del entorno local. La clave JWT viene del
entorno, tiene suficiente entropía, no posee valor productivo predeterminado
y puede rotarse mediante un procedimiento documentado. En producción, el
arranque rechaza los marcadores conocidos y secretos JWT menores de 32
caracteres; la longitud es un mínimo defensivo y no sustituye la generación
aleatoria del secreto.

## 4. Autorización

Cada caso de uso verifica, en este orden:

1. identidad activa;
2. membership activo;
3. ownership del Team;
4. permiso del Role;
5. Visibility del recurso o campo;
6. estado e invariantes del dominio.

El Team se deriva del contexto autenticado, no de un `team_id` libre en el
body. Para recursos ajenos se devuelve `404`. Las consultas filtran antes de
contar o paginar. Los schemas de respuesta para Driver separan resumen
autorizado de detalle técnico confidencial.

## 5. Amenazas prioritarias

| Riesgo | Defensa inicial | Prueba requerida |
|---|---|---|
| IDOR entre Teams | filtro ownership en servicio/query | IDs válidos de otro Team devuelven 404 |
| Escalación de Role | role server-side y campos inmutables | Driver no ejecuta comandos técnicos |
| Fuga por serialización | DTO/schemas por audiencia | campos confidenciales ausentes |
| Mass assignment | create/update schemas explícitos | campo prohibido produce 422 |
| Fuerza bruta | respuesta genérica, logging seguro y rate limit antes de publicar | repetición no revela cuenta |
| Robo de token | HTTPS, TTL corto y memoria del cliente | token no aparece en logs/storage |
| Inyección | ORM parametrizado y validación | payloads no alteran consultas |
| Fuga por logs/errores | redacción y RFC 9457 | secretos nunca aparecen |
| Condición de carrera | transacción, locking/constraints | pruebas concurrentes |

## 6. Entrada y salida

- Pydantic valida tipos, longitudes y enums.
- SQLAlchemy usa parámetros; SQL textual requiere revisión y parámetros
  explícitos.
- Markdown o notas se devuelven como texto; el cliente debe escapar HTML.
- Uploads no pertenecen a P0. Las referencias de telemetría P1 no permiten
  rutas locales arbitrarias.
- CORS usa allowlist explícita por entorno; nunca wildcard con credenciales.
- La API aplica esa allowlist, limita métodos y encabezados admitidos y expone
  `X-Request-ID` al origen autorizado.
- OpenAPI de producción puede permanecer accesible sólo si no expone datos o
  mecanismos internos sensibles.

## 7. Secretos y dependencias

- `.env` real no se versiona; `.env.example` sólo documenta nombres.
- Ningún secreto aparece en imagen Docker, tests, ejemplos o logs.
- La aplicación falla al arrancar si falta configuración crítica.
- Dependencias se fijan mediante lockfile y se actualizan con revisión.
- Antes de una publicación se ejecuta análisis de vulnerabilidades de
  dependencias e imagen.

## 8. Operación segura

- Respuestas de login no distinguen usuario inexistente de password erróneo.
- Rate limiting de login es requisito antes de exposición pública; no exige
  Redis para el entorno de desarrollo.
- Headers seguros y TLS se configuran en aplicación/proxy de despliegue.
- Backups de datos reales se cifran y se prueba restauración.
- Incidentes se correlacionan mediante `request_id` sin capturar contenido
  confidencial.

## 9. Privacidad y minimización

V1 solicitará únicamente datos personales necesarios para identidad y
operación. No se almacenarán datos médicos, financieros ni información de
telemetría completa. Antes de usar datos reales se definirá consentimiento,
retención, exportación y eliminación conforme al contexto aplicable.

## 10. Referencias

- [FastAPI — OAuth2 with Password and JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [OWASP — Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [OWASP — Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

## 11. Estado de controles después de Fase 6

Implementados y probados:

- Argon2id, JWT breve y resolución server-side de identidad activa;
- RBAC de menor privilegio, ownership por Team y base de Visibility;
- errores y logs sin cuerpos, tokens ni mensajes internos;
- rechazo productivo de configuración de desarrollo o JWT débil;
- allowlist CORS explícita;
- ejecución del contenedor como usuario no root.

Antes de exponer RaceOps públicamente todavía se requieren rate limiting,
TLS/headers del proxy, lock de dependencias y análisis de vulnerabilidades de
dependencias e imagen. Son controles de publicación/robustez de Fase 13, no se
declaran cumplidos por el cierre de identidad.

