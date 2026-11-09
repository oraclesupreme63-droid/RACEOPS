# RaceOps — Contrato del Session Learning Loop

## 1. Información

- **Versión:** 1.0
- **Fecha:** 9 de noviembre de 2026
- **Estado:** preparado para aprobación del Bloque 8.1
- **Alcance inmediato:** Session, asignación, ciclo de actividad y bloqueo de
  resultados
- **Alcance total de Fase 8:** cadena observación → hipótesis → acción → resultado

## 2. Propósito

Fase 8 debe probar la tesis central de RaceOps mediante un flujo completo, no
añadir módulos desconectados:

```text
Event
→ Session con Driver y Vehicle
→ Laps, Sectors y contexto disponible
→ Driver Feedback y Observations
→ Analysis e Hypotheses
→ hasta tres prioridades y Actions
→ siguiente Session
→ Outcome y conclusión
```

RaceOps conserva el razonamiento alrededor de la sesión; no reemplaza AiM,
MyChron, MoTeC ni adquiere telemetría en vivo.

## 3. Clasificación por evidencia

### Respaldado por evidencia

- feedback de Driver y datos disponibles son complementarios;
- el análisis debe terminar en pocas prioridades accionables;
- varios Roles consumen información distinta;
- la memoria histórica del Track puede tener valor;
- un flujo con demasiada captura manual puede fracasar.

### Parcialmente respaldado

- la información se fragmenta entre personas y herramientas en algunos
  equipos, pero no en todos;
- el ciclo exacto de Session y quién bloquea resultados varía por equipo;
- revalidar Driver y Vehicle justo antes de iniciar es una protección útil,
  pendiente de prueba con usuarios.

### Hipótesis reversibles

- `session_type` será texto normalizado, no un enum universal;
- una asignación podrá editarse solamente mientras Session esté `PLANNED`;
- el estado de Event no bloqueará captura retrospectiva de Session;
- no se impedirá preventivamente que un Vehicle aparezca en varias Sessions
  planificadas hasta observar una necesidad real de agenda o concurrencia.

### Rechazado para esta fase

- ingestión de telemetría en vivo;
- recomendaciones automáticas de IA;
- schema universal de canales;
- microservicios;
- logística, facturación o estrategia profesional de Fórmula.

## 4. Límite modular

El módulo `sessions` será propietario de:

- Session y sus dos estados;
- Lap y Sector;
- Condition Snapshot;
- Driver Feedback.

El módulo `learning` será propietario de Observation, Session Analysis,
Hypothesis, Priority, Action y Action Outcome. `learning` depende de Sessions;
Sessions no depende de `learning`.

## 5. Session mínima

| Campo | Regla |
|---|---|
| `session_id` | UUID generado por servidor |
| `team_id` | derivado de la Membership activa; nunca se acepta del body |
| `event_id` | Event existente del mismo Team; inmutable después de crear |
| `driver_id` | Driver activo del mismo Team |
| `vehicle_id` | Vehicle `READY` del mismo Team |
| `session_type` | texto recortado de 1–80 caracteres |
| `scheduled_at` | instante requerido con zona horaria, normalizado a UTC |
| `status` | inicia `PLANNED` |
| `results_status` | inicia `OPEN` |
| `started_at` | `null` hasta el primer inicio; server-side |
| `ended_at` | `null` hasta completar o cancelar; server-side |
| `results_locked_by_user_id` | actor que bloqueó; `null` mientras está abierto |
| `results_locked_at` | instante server-side del bloqueo |
| timestamps | `created_at` y `updated_at` server-side en UTC |

Track se obtiene mediante Event y permanece estable porque cambiar el Track
del Event queda prohibido desde que exista su primera Session. No se duplica
`track_id` dentro de Session.

## 6. Asignación atómica

Crear Session valida Event, Driver y Vehicle dentro de una sola transacción:

1. los tres recursos existen dentro del Team activo;
2. Driver está `ACTIVE`;
3. Vehicle está `READY`;
4. ningún dato se guarda si falla una validación;
5. la respuesta no confía en `team_id`, status ni timestamps del cliente.

Cambiar Driver, Vehicle, tipo o fecha sólo se permite en `PLANNED`. Cambiar una
asignación revalida elegibilidad. Iniciar también revalida Driver y Vehicle
para detectar indisponibilidad ocurrida después de planificar.

No se cambia automáticamente el estado de Vehicle al iniciar Session. Esa
automatización no está respaldada y podría interferir con el flujo real del
equipo.

## 7. Estados independientes

### Session Status

```text
PLANNED → ACTIVE | CANCELLED
ACTIVE  → PAUSED | COMPLETED | CANCELLED
PAUSED  → ACTIVE | COMPLETED | CANCELLED
COMPLETED y CANCELLED → terminales
```

- el primer `PLANNED → ACTIVE` fija `started_at`;
- reanudar no reemplaza `started_at`;
- completar o cancelar fija `ended_at`;
- ninguna transición normal reabre estados terminales.

### Results Status

```text
OPEN → LOCKED
```

- completar Session no bloquea resultados automáticamente;
- el bloqueo sólo se permite con Session `COMPLETED` o `CANCELLED`;
- se conservan actor y momento;
- `LOCKED` rechazará nuevas Laps y Sectors por la API normal;
- correcciones posteriores pertenecen a P1 y quedan fuera de Fase 8 P0.

## 8. Autorización

| Operación | Administrator | Team Manager | Engineer | Mechanic | Driver |
|---|---:|---:|---:|---:|---:|
| Crear y editar Session planificada | Sí | Sí | Sí | No | No |
| Consultar Session | Team | Team | Team | Team | Sólo asignadas |
| Cambiar ciclo de actividad | Sí | Sí | Sí | No | No |
| Bloquear resultados | Sí | Sí | Sí | No | No |

Se añadirá `READ_SESSIONS` como permiso explícito. `WRITE_SESSIONS` no se
reutilizará para conceder lectura. Driver necesita un Driver Profile vinculado
a su User y sólo consulta Sessions con ese `driver_id`.

La misma relación habilitará lectura únicamente de Events y Vehicles asociados
para Driver; no se abrirán sus catálogos completos.

## 9. Contrato HTTP inicial

```text
POST  /api/v1/sessions
GET   /api/v1/sessions
GET   /api/v1/sessions/{session_id}
PATCH /api/v1/sessions/{session_id}

POST /api/v1/sessions/{session_id}/start
POST /api/v1/sessions/{session_id}/pause
POST /api/v1/sessions/{session_id}/resume
POST /api/v1/sessions/{session_id}/complete
POST /api/v1/sessions/{session_id}/cancel
POST /api/v1/sessions/{session_id}/lock-results
```

El listado acepta filtros explícitos por Event, Driver, Vehicle, Session Status
y Results Status, además de `limit`/`offset`. Team y relación se aplican antes
de calcular `total`. No existe DELETE.

## 10. Errores estables

| Situación | HTTP | Código |
|---|---:|---|
| permiso ausente | 403 | `insufficient_permissions` |
| recurso inexistente, ajeno o no relacionado | 404 | `resource_not_found` |
| Driver inactivo o Vehicle no READY | 409 | `session_assignment_conflict` |
| edición fuera de PLANNED | 409 | `session_not_editable` |
| transición de actividad inválida | 409 | `invalid_session_status_transition` |
| bloqueo inválido o repetido | 409 | `invalid_results_status_transition` |
| cambiar Track de Event con Sessions | 409 | `event_track_locked` |
| body inválido o campo prohibido | 422 | `REQUEST_VALIDATION_ERROR` |

## 11. Integridad y concurrencia

- FKs restrictivas conservan historia;
- referencias compuestas protegen pertenencia al Team cuando sea práctico;
- transiciones y edición leen el estado dentro de la misma transacción;
- creación de Session y cambio de Track bloquean la fila de Event para evitar
  una carrera que rompa la pista histórica;
- un error hace rollback completo;
- pruebas cubrirán todos los Roles, UUID de otro Team, estados inválidos y
  ausencia de escrituras parciales.

## 12. Criterio de aprobación

Este contrato está listo para persistencia cuando el propietario apruebe:

- campos mínimos y ausencia de campos sin uso inmediato;
- asignación y revalidación antes de iniciar;
- dos máquinas de estado independientes;
- límites de lectura del Driver;
- entregas pequeñas descritas en la checklist de Fase 8.
