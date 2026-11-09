# RaceOps — Checklist Fase 7: base operativa

## Estado general

- **Fase:** cierre técnico completo; pendiente de aprobación final
- **Última actualización:** 9 de noviembre de 2026
- **Entregable:** `v0.2 — Operational Base`
- **Gate objetivo:** G6 — Vertical Alpha, junto con Fase 8

## Bloques

### 7.1 — Contrato operativo

- [x] Revisar RF-013–RF-030, AC-005–AC-008 y BL-013–BL-016.
- [x] Definir el mínimo de Driver, Vehicle, Track y Event.
- [x] Resolver Driver separado de User y vínculo opcional por Team.
- [x] Definir estados y preservación histórica.
- [x] Definir ownership, permisos y errores esperados.
- [x] Clasificar decisiones por nivel de evidencia.
- [x] Aprobación del propietario.

### 7.2 — Persistencia operativa

- [x] Enums y modelos SQLAlchemy.
- [x] Constraints, índices y FKs de Team.
- [x] Migración Alembic.
- [x] Validación de vínculos Driver/User y Event/Track.
- [x] Pruebas de constraints y round-trip de migración.
- [x] `alembic check` sin diferencias.
- [x] Aprobación del propietario.

### 7.3 — API de Drivers

- [x] Crear, consultar, listar y actualizar Driver.
- [x] Activar y desactivar sin borrado físico.
- [x] Vínculo opcional con User autorizado del mismo Team.
- [x] RBAC, aislamiento y alcance propio del Driver.
- [x] Pruebas HTTP positivas, negativas y entre Teams.
- [x] Aprobación del propietario.

### 7.4 — API de Vehicles

- [x] Crear, consultar, listar y actualizar Vehicle.
- [x] Transiciones explícitas de Vehicle Status.
- [x] `RETIRED` terminal y sólo `READY` asignable.
- [x] RBAC y aislamiento entre Teams.
- [x] Pruebas HTTP y de transiciones.
- [x] Aprobación del propietario.

### 7.5 — API de Tracks y Events

- [x] Crear, consultar, listar y actualizar Track.
- [x] Crear, consultar, listar y actualizar Event.
- [x] Track y Event obligatoriamente del mismo Team.
- [x] Fechas y estado de Event válidos.
- [x] Sin borrado físico mediante la API normal.
- [x] RBAC y pruebas entre Teams.
- [x] Aprobación del propietario.

### 7.6 — Cierre

- [x] Suite completa y cobertura superior al 90 %.
- [x] Ruff, mypy, migraciones y contenedores.
- [x] CI en verde.
- [x] Trazabilidad y documentación actualizadas.
- [x] Evidencia de `v0.2 — Operational Base`; el tag espera aprobación final.
- [ ] Aprobación de Fase 7.

## Condición para avanzar

Los seis bloques están técnicamente completos. La evidencia se resume en el
[`reporte de cierre`](phase-7-block-7.6-report-2026-11-09.md). No se crea el
tag `v0.2.0` ni se inicia la Fase 8 hasta recibir la aprobación final del
propietario.
