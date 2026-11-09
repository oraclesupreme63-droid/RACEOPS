# RaceOps — Checklist Fase 7: base operativa

## Estado general

- **Fase:** en progreso
- **Última actualización:** 8 de noviembre de 2026
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
- [ ] Aprobación del propietario.

### 7.2 — Persistencia operativa

- [ ] Enums y modelos SQLAlchemy.
- [ ] Constraints, índices y FKs de Team.
- [ ] Migración Alembic.
- [ ] Validación de vínculos Driver/User y Event/Track.
- [ ] Pruebas de constraints y round-trip de migración.
- [ ] `alembic check` sin diferencias.
- [ ] Aprobación del propietario.

### 7.3 — API de Drivers

- [ ] Crear, consultar, listar y actualizar Driver.
- [ ] Activar y desactivar sin borrado físico.
- [ ] Vínculo opcional con User autorizado del mismo Team.
- [ ] RBAC, aislamiento y alcance propio del Driver.
- [ ] Pruebas HTTP positivas, negativas y entre Teams.
- [ ] Aprobación del propietario.

### 7.4 — API de Vehicles

- [ ] Crear, consultar, listar y actualizar Vehicle.
- [ ] Transiciones explícitas de Vehicle Status.
- [ ] `RETIRED` terminal y sólo `READY` asignable.
- [ ] RBAC y aislamiento entre Teams.
- [ ] Pruebas HTTP y de transiciones.
- [ ] Aprobación del propietario.

### 7.5 — API de Tracks y Events

- [ ] Crear, consultar, listar y actualizar Track.
- [ ] Crear, consultar, listar y actualizar Event.
- [ ] Track y Event obligatoriamente del mismo Team.
- [ ] Fechas y estado de Event válidos.
- [ ] Sin borrado físico mediante la API normal.
- [ ] RBAC y pruebas entre Teams.
- [ ] Aprobación del propietario.

### 7.6 — Cierre

- [ ] Suite completa y cobertura superior al 90 %.
- [ ] Ruff, mypy, migraciones y contenedores.
- [ ] CI en verde.
- [ ] Trazabilidad y documentación actualizadas.
- [ ] Tag o evidencia de `v0.2 — Operational Base` según estado del release.
- [ ] Aprobación de Fase 7.

## Condición para avanzar

El Bloque 7.2 no comienza hasta aprobar el
[`reporte del Bloque 7.1`](phase-7-block-7.1-report-2026-11-08.md). Cada API
se construye sobre persistencia aprobada y no se inicia la Fase 8 hasta cerrar
esta checklist.
