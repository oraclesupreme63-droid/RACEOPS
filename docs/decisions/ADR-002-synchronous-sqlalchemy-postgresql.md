# ADR-002 — SQLAlchemy síncrono y PostgreSQL

- **Estado:** Aceptado
- **Fecha:** 2026-10-22

## Contexto

P0 consiste en operaciones CRUD transaccionales y análisis registrado por
usuarios. No incluye telemetría en vivo ni I/O masivo concurrente.

## Decisión

Usar PostgreSQL, SQLAlchemy 2.x síncrono y Psycopg 3. Cada petición o caso de
uso tendrá una Session no compartida y una transacción corta. Los endpoints
con base de datos serán síncronos para no bloquear un event loop.

## Consecuencias

- El modelo mental, debugging y manejo transaccional son simples.
- Integration tests utilizan PostgreSQL, no SQLite.
- No se mezcla acceso sync/async.
- Adoptar async requiere medición, necesidad concreta y un ADR posterior.

