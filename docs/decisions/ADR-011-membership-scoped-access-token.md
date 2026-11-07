# ADR-011 — Access token limitado a una TeamMembership

- **Estado:** Propuesto para aprobación
- **Fecha:** 2026-11-07
- **Refina:** ADR-004

## Contexto

El modelo inicial restringía V1 a una Membership activa por User. Esa
restricción simplificaba el contexto, pero mezclaba la identidad global con la
participación del mismo User en Teams distintos y obligaría a duplicar cuentas
si aparece esa necesidad.

RaceOps todavía no tiene evidencia suficiente para construir una experiencia
multi-Team sofisticada. Sí necesita que cada petición opere dentro de una sola
frontera de ownership verificable.

## Decisión

Un User podrá tener una TeamMembership por Team y varias membresías activas en
Teams diferentes. Cada Membership conserva exactamente un Role principal.

Cada access token representará una sola Membership seleccionada e incluirá
`sub`, `mid`, `jti`, `iat` y `exp`. No incluirá Role, Team ID, email ni
permisos. El servidor resolverá Membership, User, Team y Role actuales en la
base de datos para cada petición.

Cuando haya una sola Membership activa, login la seleccionará automáticamente.
Con varias, el cliente deberá indicar `team_id`; no habrá endpoint de cambio de
Team ni token multi-Team en P0.

## Consecuencias

- Cambios de Role y desactivaciones tienen efecto inmediato.
- No se duplican cuentas para representar participación en otro Team.
- El modelo tolera una hipótesis futura sin convertirla en una UX compleja.
- Cambiar de Team requiere obtener otro token en P0.
- Las consultas continúan limitadas a un Team por petición.
- La migración debe imponer unicidad `(user_id, team_id)`.

## Alternativas descartadas

- **Una sola Membership activa por User:** simple, pero convierte una hipótesis
  temprana en una restricción de identidad global.
- **Todos los Teams y Roles dentro del JWT:** roles obsoletos hasta vencimiento
  y mayor impacto ante robo del token.
- **Header de Team sin contexto firmado:** exige resolver ambigüedad en cada
  petición y aumenta el riesgo de usar el selector como autorización.

