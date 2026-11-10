# RaceOps — Reporte del Bloque 8.4: ciclo y bloqueo de resultados

## 1. Estado

- **Fecha:** 10 de noviembre de 2026
- **Fase:** 8 — Session Learning Loop
- **Bloque:** 8.4 — Ciclo y bloqueo de resultados
- **Resultado:** implementado y verificado; pendiente de aprobación del propietario
- **Siguiente bloque:** 8.5 — Laps, Sectors y métricas (`v0.3`)

## 2. Ciclo de actividad

Se añadieron comandos explícitos para `start`, `pause`, `resume`, `complete` y
`cancel`. Cada comando bloquea la fila de Session, valida el estado actual y
aplica una sola transición dentro de la transacción.

- `start` sólo acepta `PLANNED`, revalida Driver `ACTIVE` y Vehicle `READY`, y
  fija `started_at` con hora del servidor;
- `pause` sólo acepta `ACTIVE`;
- `resume` sólo acepta `PAUSED` y conserva el primer `started_at`;
- `complete` acepta `ACTIVE` o `PAUSED` y fija `ended_at`;
- `cancel` acepta cualquier estado no terminal y conserva si llegó a iniciar;
- `COMPLETED` y `CANCELLED` permanecen terminales.

No se cambia automáticamente el estado de Vehicle porque esa automatización no
está validada por evidencia del flujo real.

## 3. Ciclo de resultados

`lock-results` aplica la transición independiente `OPEN → LOCKED`. Sólo se
permite cuando la actividad está `COMPLETED` o `CANCELLED`. El servidor conserva
el User que bloqueó y el instante UTC. El bloqueo es irreversible en P0 y un
segundo intento se rechaza.

Completar o cancelar una Session no bloquea resultados automáticamente. Esto
permite capturar Laps y Sectors antes del cierre explícito del Bloque 8.5.

## 4. Autorización y errores

Los comandos reutilizan `WRITE_SESSIONS`: Administrator, Team Manager y
Engineer pueden ejecutarlos; Mechanic y Driver no. El aislamiento por Team
continúa ocultando recursos ajenos.

Se publicaron los conflictos:

- `invalid_session_status_transition` para un comando de actividad inválido;
- `invalid_results_status_transition` para bloqueo prematuro o repetido;
- `session_assignment_conflict` cuando la asignación dejó de ser elegible antes
  de iniciar.

## 5. Evidencia de verificación

- 19 pruebas focalizadas de API, persistencia y modelo aprobadas;
- se cubrieron todas las transiciones permitidas, estados terminales, bloqueo
  prematuro y repetido, actor/momento y revalidación sin mutación parcial;
- formato, Ruff y mypy estricto aprobados durante el desarrollo;
- la suite completa y el smoke test de contenedor se ejecutarán una vez en
  GitHub Actions al publicar el commit del bloque.

## 6. Control de alcance

No se añadieron Laps, Sectors, archivos de telemetría ni métricas. `LOCKED`
establece la regla que el Bloque 8.5 usará para rechazar escritura de resultados.
No existe reapertura o corrección administrativa en P0.

## 7. Punto de aprobación

Con aprobación comienza el Bloque 8.5: persistencia y API de Laps/Sectors,
duraciones enteras en microsegundos, métricas simples y respeto de Results
`LOCKED`. Ese bloque cerrará el entregable intermedio `v0.3`.
