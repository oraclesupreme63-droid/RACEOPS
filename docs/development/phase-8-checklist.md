# RaceOps — Checklist Fase 8: Session Learning Loop

## Estado general

- **Fase:** en progreso
- **Última actualización:** 10 de noviembre de 2026
- **Entregables intermedios:** `v0.3 — Sessions & Results`
- **Entregable final:** `v0.4 — Session Learning Loop`
- **Gate objetivo:** G6 — Vertical Alpha

## Bloques

### 8.1 — Contrato y secuencia

- [x] Revisar RF-031–RF-130, AC-009–AC-028 y BL-017–BL-033.
- [x] Fijar Session mínima, asignación y dos ciclos de estado.
- [x] Definir autorización, relación del Driver y errores.
- [x] Delimitar `sessions` y `learning`.
- [x] Clasificar decisiones por evidencia.
- [x] Dividir la fase en entregas verificables.
- [x] Aprobación del propietario.

### 8.2 — Persistencia de Session

- [x] Enums y modelo Session.
- [x] FKs, constraints e índices por Team.
- [x] Migración reversible.
- [x] Pruebas de invariantes y round-trip.
- [x] `alembic check` sin diferencias.
- [x] Aprobación del propietario.

### 8.3 — API y asignación

- [x] Crear, listar, consultar y editar Session planificada.
- [x] Asignación atómica y revalidación.
- [x] `READ_SESSIONS`, RBAC y alcance del Driver.
- [x] Completar acceso relacionado de Driver a Event y Vehicle.
- [x] Bloquear cambio de Track cuando Event tenga Session.
- [x] Pruebas HTTP y entre Teams.
- [ ] Aprobación del propietario.

### 8.4 — Ciclo y bloqueo de resultados

- [ ] Start, pause, resume, complete y cancel.
- [ ] Timestamps server-side.
- [ ] Results `OPEN → LOCKED` con actor y momento.
- [ ] Conflictos y estados terminales.
- [ ] Pruebas de todas las transiciones.
- [ ] Aprobación del propietario.

### 8.5 — Laps, Sectors y métricas (`v0.3`)

- [ ] Persistencia y API de Laps.
- [ ] Sectors opcionales y ordenados.
- [ ] Duraciones enteras en microsegundos.
- [ ] Elegibilidad, mejor vuelta, promedio y consistencia.
- [ ] Bloqueo de escritura con Results `LOCKED`.
- [ ] Evidencia y tag `v0.3.0`.
- [ ] Aprobación del propietario.

### 8.6 — Conditions

- [ ] Snapshot opcional por Session.
- [ ] Valores conocidos con unidades explícitas.
- [ ] Captura breve y permisos.
- [ ] Pruebas con datos parciales.
- [ ] Aprobación del propietario.

### 8.7 — Driver Feedback

- [ ] Feedback propio y comunicado.
- [ ] Autor y Driver experimentador separados.
- [ ] Alcance por Session y visibilidad.
- [ ] Pruebas de relación y Roles.
- [ ] Aprobación del propietario.

### 8.8 — Observations

- [ ] Observación asociada con Session o Vehicle.
- [ ] Categoría y visibilidad sin convertirla en causa.
- [ ] Engineer/Mechanic y lectura autorizada.
- [ ] Pruebas de confidencialidad.
- [ ] Aprobación del propietario.

### 8.9 — Analysis e Hypotheses

- [ ] Análisis autorizado y detalle técnico separado.
- [ ] Hipótesis, causa, confianza y estado.
- [ ] Permisos de Engineering.
- [ ] Pruebas de serialización por audiencia.
- [ ] Aprobación del propietario.

### 8.10 — Priorities y Actions

- [ ] Prioridades por destinatario y máximo tres principales.
- [ ] Acciones con responsable y motivación.
- [ ] Intención `NEXT_SESSION` sin crear Session ficticia.
- [ ] Estados y permisos por responsable.
- [ ] Aprobación del propietario.

### 8.11 — Outcomes y siguiente Session

- [ ] Vincular Action con Session de evaluación.
- [ ] Resultado `IMPROVED`, `WORSENED` o `NO_MEASURABLE_EFFECT`.
- [ ] Conclusión de Hypothesis sin falsa certeza.
- [ ] Recuperar cadena completa de aprendizaje.
- [ ] Aprobación del propietario.

### 8.12 — Cierre de Fase 8 (`v0.4`)

- [ ] Prueba end-to-end del flujo vertical.
- [ ] Suite, cobertura, tipos, migraciones y Docker.
- [ ] Validación de confidencialidad por Role.
- [ ] Trazabilidad y documentación actualizadas.
- [ ] Evidencia `v0.4.0` y evaluación de Gate G6.
- [ ] Aprobación de Fase 8.

## Condición para avanzar

El Bloque 8.3 está técnicamente completo y espera aprobación en su
[`reporte`](phase-8-block-8.3-report-2026-11-10.md). El ciclo de actividad y el
bloqueo de resultados no comienzan antes de aprobar esta primera API. Cada
bloque funcional termina con una sola verificación completa y su punto de
aprobación.
