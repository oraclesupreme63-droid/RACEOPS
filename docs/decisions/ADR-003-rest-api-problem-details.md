# ADR-003 — REST `/api/v1` y Problem Details

- **Estado:** Aceptado
- **Fecha:** 2026-10-22

## Contexto

El frontend necesita un contrato estable y los errores deben ser
interpretables sin acoplarse a excepciones internas.

## Decisión

Exponer JSON REST bajo `/api/v1`. Usar recursos para datos y endpoints
`/commands/...` para transiciones. Los errores seguirán RFC 9457 con un
`code` estable de RaceOps.

## Consecuencias

- OpenAPI documenta el contrato.
- Transiciones y permisos permanecen explícitos.
- El cliente no analiza mensajes humanos para reaccionar.
- No se introduce GraphQL porque no existe necesidad validada.

