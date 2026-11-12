# RaceOps — Architecture Decision Records

Los ADR conservan decisiones que afectan estructura, seguridad, datos o
alcance técnico. Una decisión aceptada no se reescribe para ocultar su
historia: un ADR posterior la sustituye cuando cambie la evidencia.

| ADR | Decisión | Estado |
|---|---|---|
| [ADR-001](ADR-001-modular-monolith.md) | Monolito modular | Aceptado |
| [ADR-002](ADR-002-synchronous-sqlalchemy-postgresql.md) | SQLAlchemy síncrono y PostgreSQL | Aceptado |
| [ADR-003](ADR-003-rest-api-problem-details.md) | REST `/api/v1` y RFC 9457 | Aceptado |
| [ADR-004](ADR-004-jwt-argon2id-rbac.md) | JWT, Argon2id y RBAC server-side | Aceptado |
| [ADR-005](ADR-005-no-telemetry-ingestion-p0.md) | Sin ingestión de telemetría en P0 | Aceptado |
| [ADR-006](ADR-006-selective-audit-no-event-sourcing.md) | Auditoría selectiva, no event sourcing | Aceptado |
| [ADR-007](ADR-007-authorized-response-schemas.md) | Visibilidad en consultas y schemas | Aceptado |
| [ADR-008](ADR-008-no-generic-repository.md) | Sin repository genérico | Aceptado |
| [ADR-009](ADR-009-backend-first-thin-client.md) | Backend-first y cliente web ligero | Aceptado |
| [ADR-010](ADR-010-integer-time-durations.md) | Duraciones enteras en microsegundos | Aceptado |
| [ADR-011](ADR-011-membership-scoped-access-token.md) | Access token limitado a una TeamMembership | Aceptado |
| [ADR-012](ADR-012-bootstrap-without-public-registration.md) | Bootstrap administrativo sin registro público | Aceptado |
| [ADR-013](ADR-013-buildless-validation-client.md) | Cliente de validación sin proceso de compilación | Aceptado |

Aceptados mediante Gate G4 el 22 de octubre de 2026.

ADR-011 y ADR-012 fueron aprobados al autorizar el avance al Bloque 6.2 el 8 de
noviembre de 2026.

ADR-013 fue aceptado al implementar el cliente mínimo del Bloque 9.2 el 12 de
noviembre de 2026.

