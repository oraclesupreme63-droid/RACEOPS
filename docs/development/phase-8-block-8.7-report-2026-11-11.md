# RaceOps — Reporte del Bloque 8.7: Driver Feedback

## 1. Estado

- **Fecha:** 11 de noviembre de 2026
- **Fase:** 8 — Session Learning Loop
- **Bloque:** 8.7 — Driver Feedback
- **Resultado:** implementado, verificado y aprobado por el propietario
- **Siguiente bloque:** 8.8 — Observations

## 2. Capacidad entregada

RaceOps permite registrar varios elementos de feedback por Session. El Driver
puede capturar rápidamente lo que experimentó y Engineer, Team Manager o
Mechanic pueden registrar feedback comunicado verbalmente. Sólo la descripción
es obligatoria; zona, fase de conducción, severidad y confianza son opcionales.

El sistema deriva el Driver desde la Session y el autor desde la identidad
autenticada. El cliente no puede elegir ni falsificar esos identificadores.

## 3. Integridad y autorización

- Session, Team y Driver se protegen con FKs compuestas;
- `driver_id` y `author_user_id` se conservan por separado;
- Driver sólo crea feedback en Sessions asignadas y sólo edita el suyo;
- una Session con feedback no puede reasignarse a otro Driver;
- Engineer puede crear y actualizar feedback comunicado;
- Team Manager y Engineer leen los registros de la Session;
- Driver afectado lee también lo capturado por el equipo;
- Mechanic puede leer únicamente lo que él mismo capturó;
- Administrator no recibe acceso por jerarquía a contenido restringido;
- la ausencia de feedback no bloquea el cierre de Session;
- no existe DELETE.

## 4. API

```text
POST  /api/v1/sessions/{session_id}/feedback
GET   /api/v1/sessions/{session_id}/feedback
GET   /api/v1/feedback/{feedback_id}
PATCH /api/v1/feedback/{feedback_id}
```

Los listados son paginados y ordenados de forma estable. La visibilidad de V1
queda fijada en `ROLE_RESTRICTED`; no se expone como campo editable al cliente.

## 5. Verificación

- pruebas unitarias del modelo, esquemas y permisos;
- pruebas HTTP reales para feedback propio y comunicado;
- pruebas de múltiples elementos, relación con Session y edición por autor;
- pruebas de lectura por Driver, Engineer, Team Manager, Mechanic y Administrator;
- rechazo de identidad falsificada y Session no asignada;
- migración reversible `20261111_0007_feedback`;
- Ruff format/check y mypy: aprobados;
- suite completa: **185 pruebas aprobadas**;
- cobertura total: **93.72 %**, superior al mínimo de 90 %;
- endurecimiento final de reasignación: **15 pruebas dirigidas aprobadas**;
- `alembic check`: sin operaciones nuevas pendientes;
- build y smoke test del contenedor: `/health`, `/ready`, OpenAPI y migración
  `20261111_0007_feedback (head)` aprobados.

## 6. Control de alcance

No se añadieron archivos de telemetría, recomendaciones automáticas, análisis,
hipótesis ni campos rígidos por categoría. Driver Feedback describe experiencia;
no afirma una causa técnica y no contiene detalles confidenciales de setup.

## 7. Aprobación

El propietario aprobó este bloque el 11 de noviembre de 2026. El trabajo
continuó con el Bloque 8.8.
