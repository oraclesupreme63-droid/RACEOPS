# RaceOps — Checklist Fase 6: identidad y autorización

## Estado general

- **Fase:** en progreso
- **Última actualización:** 8 de noviembre de 2026
- **Gate objetivo:** G6 — Vertical Alpha, junto con Fases 7 y 8

## Bloques

### 6.1 — Contrato de identidad

- [x] Revisar RF-001–RF-012, AC-001–AC-004 y ADR-004.
- [x] Definir Team, User, TeamMembership y Role.
- [x] Resolver cardinalidad de Membership y contexto activo.
- [x] Definir login, `/auth/me` y errores estables.
- [x] Definir bootstrap administrativo sin registro público.
- [x] Registrar ADR-011 y ADR-012.
- [x] Actualizar documentos refinados por la decisión.
- [x] Aprobación del propietario.

### 6.2 — Persistencia

- [x] Enums y modelos SQLAlchemy.
- [x] Constraints, índices y timestamps.
- [x] Migración Alembic.
- [x] Pruebas de constraints.
- [x] Round-trip `upgrade → downgrade → upgrade`.
- [x] `alembic check` sin diferencias entre modelos y esquema.
- [x] Suite completa con cobertura superior al 90 %.
- [x] Aprobación del propietario.

### 6.3 — Credenciales y tokens

- [x] Argon2id y política de password.
- [x] Emisión y validación JWT.
- [x] Resolución server-side de identidad actual.
- [x] Casos válido, vencido, manipulado e inactivo.
- [x] Comando seguro de bootstrap.
- [x] Rollback transaccional ante conflicto.
- [x] Suite completa con cobertura superior al 90 %.
- [x] Aprobación del propietario.

### 6.4 — API de identidad

- [x] `POST /api/v1/auth/login`.
- [x] `GET /api/v1/auth/me`.
- [x] Selección segura entre múltiples Teams.
- [x] Schemas que excluyen credenciales y hashes.
- [x] OpenAPI y respuestas RFC 9457.
- [x] Pruebas HTTP positivas, negativas y de no filtración.
- [x] Suite completa con cobertura superior al 90 %.
- [x] Aprobación del propietario.

### 6.5 — RBAC y aislamiento

- [x] Contexto de actor reutilizable.
- [x] Políticas de menor privilegio.
- [x] Aislamiento entre Teams con `404` seguro.
- [x] Pruebas positivas y negativas por Role.
- [x] Base de Visibility para módulos posteriores.
- [x] Administrator sin acceso técnico confidencial por jerarquía.
- [x] Suite completa con cobertura superior al 90 %.
- [ ] Aprobación del propietario.

### 6.6 — Cierre

- [ ] Suite completa, cobertura, Ruff y mypy.
- [ ] Migraciones y contenedores.
- [ ] CI en verde.
- [ ] Trazabilidad y documentación actualizadas.
- [ ] Revisión de seguridad.
- [ ] Aprobación de Fase 6.

## Condición para avanzar

El Bloque 6.6 no comienza hasta aprobar el
[`reporte del Bloque 6.5`](phase-6-block-6.5-report-2026-11-08.md).

