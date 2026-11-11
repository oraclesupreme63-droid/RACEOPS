# RaceOps — Reporte del Bloque 8.6: Conditions

## 1. Estado

- **Fecha:** 11 de noviembre de 2026
- **Fase:** 8 — Session Learning Loop
- **Bloque:** 8.6 — Conditions
- **Resultado:** implementado y verificado; pendiente de aprobación del propietario
- **Siguiente bloque:** 8.7 — Driver Feedback

## 2. Capacidad entregada

RaceOps permite crear, consultar y actualizar un único Condition Snapshot por
Session. La captura es deliberadamente corta: temperaturas ambiente y de pista
con sus unidades, clima, condición general de pista y origen opcional.

Los campos desconocidos permanecen `null`. No se inventan ceros, no se exige
completar todos los campos y no existe dependencia meteorológica externa.

## 3. Integridad y autorización

- valor numérico y unidad aparecen juntos;
- un snapshot requiere al menos una condición conocida;
- Session–Team se protege con FK compuesta;
- existe como máximo un snapshot por Session;
- Administrator, Team Manager, Engineer y Mechanic escriben;
- todos los Roles leen, pero Driver sólo su Session asignada;
- no existe DELETE;
- Results `LOCKED` no se amplía a Conditions sin evidencia o requisito.

## 4. API

```text
POST  /api/v1/sessions/{session_id}/conditions
GET   /api/v1/sessions/{session_id}/conditions
PATCH /api/v1/sessions/{session_id}/conditions
```

Los conflictos públicos nuevos son `condition_snapshot_exists` e
`invalid_condition_snapshot`.

## 5. Verificación

- pruebas unitarias de modelo, validación y RBAC;
- pruebas HTTP con PostgreSQL para captura parcial, cambios y errores;
- lectura relacionada de Driver y escritura de Mechanic;
- migración `20261110_0006_conditions` reversible;
- Ruff y mypy estricto aprobados durante desarrollo;
- suite completa: **174 pruebas aprobadas**;
- cobertura total: **93.62 %**, superior al mínimo de 90 %;
- `alembic check`: sin operaciones nuevas pendientes;
- GitHub Actions hará la comprobación independiente y el smoke test del
  contenedor al publicar el commit.

## 6. Control de alcance

No se añadieron APIs meteorológicas, automatización, series temporales,
recomendaciones, telemetría ni campos específicos de una categoría. La
cardinalidad de un snapshot continúa como hipótesis reversible.

## 7. Punto de aprobación

Con aprobación comenzará el Bloque 8.7: Driver Feedback propio o comunicado,
autor separado del Driver experimentador y lectura restringida por relación.
