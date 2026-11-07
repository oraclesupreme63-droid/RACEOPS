# ADR-004 — JWT, Argon2id y RBAC server-side

- **Estado:** Aceptado
- **Fecha:** 2026-10-22

## Contexto

RaceOps necesita autenticación y diferencias claras entre Administrator,
Team Manager, Engineer, Mechanic y Driver sin construir un sistema de
identidad o ABAC complejo.

## Decisión

Hashear passwords con Argon2id. Emitir access JWT de vida breve y claims
mínimos. En cada petición verificar User, Membership y Role actuales en la
base. Autorizar mediante RBAC, ownership por Team y Visibility server-side.
El cliente P0 conserva el access token sólo en memoria y no usa refresh.

## Consecuencias

- Un cambio de rol o desactivación tiene efecto inmediato al validar DB.
- Recargar el cliente puede requerir nuevo login en P0.
- No se almacenan tokens en Web Storage.
- Persistencia de sesión o identidad externa requieren una decisión futura.

