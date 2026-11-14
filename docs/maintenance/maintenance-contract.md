# RaceOps — Contrato de mantenimiento relacionado

## 1. Información

- **Versión:** 0.1
- **Fecha:** 13 de noviembre de 2026
- **Estado:** propuesto; pendiente de aprobación del propietario
- **Fase:** 10 — Mantenimiento relacionado
- **Prioridad:** P1; hipótesis técnica reversible

## 2. Propósito

La primera porción de mantenimiento debe conservar una cadena operativa
pequeña y verificable:

```text
Session
→ Observation o Action mecánica
→ Maintenance Record
→ intervención completada
→ verificación humana
→ cambio explícito de disponibilidad del Vehicle
```

Una intervención completada significa que el trabajo registrado terminó. No
significa que el problema quedó resuelto, que el Vehicle mejoró ni que está
listo para volver a pista.

## 3. Clasificación por evidencia

### Parcialmente respaldado

- síntomas de una Session pueden conducir a investigación mecánica;
- preservar el contexto técnico puede ayudar a la memoria del equipo;
- distintos Roles necesitan información diferente;
- un Vehicle no disponible no debe asignarse a una Session nueva.

### Hipótesis

- los equipos pequeños utilizarán un registro estructurado de intervenciones;
- cuatro tipos de intervención cubren el primer flujo útil;
- relacionar Observation y Action con mantenimiento reduce información
  perdida;
- Team Manager, Engineer y Mechanic son los Roles adecuados para escribir;
- el historial cronológico aporta suficiente valor para justificar la captura.

### Contraevidencia y límites

- algunos equipos funcionan correctamente con papel, notas o herramientas
  existentes;
- software adicional puede aumentar trabajo administrativo;
- no existe todavía observación externa de este flujo en RaceOps;
- el dataset público de timing no contiene mantenimiento real.

### Rechazado para esta fase

- inventario de piezas o refacciones;
- costos, compras y proveedores;
- intervalos o alertas automáticas;
- mantenimiento predictivo o recomendaciones de IA;
- jerarquía universal de componentes;
- adjuntos, fotografías y archivos binarios;
- borrado normal de historia;
- estado adicional `LIMITED` sin evidencia.

## 4. Límite modular

El módulo `maintenance` será propietario de `MaintenanceRecord`, sus tipos,
estados, servicios, API y consultas cronológicas.

Puede depender de:

- `operations.Vehicle` como recurso obligatorio;
- `sessions.RaceSession` como contexto opcional;
- `learning.Observation` y `learning.Action` como origen opcional;
- `iam` para identidad, Team, Role y permisos.

`operations`, `sessions` y `learning` no dependerán del módulo
`maintenance`. La asignabilidad continúa siendo una regla de `operations` y
`sessions`; mantenimiento sólo solicita transiciones explícitas mediante el
servicio propietario de Vehicle.

## 5. Maintenance Record mínimo

| Campo | Regla inicial |
|---|---|
| `maintenance_id` | UUID generado por servidor |
| `team_id` | derivado de la Membership activa; nunca desde el body |
| `vehicle_id` | Vehicle existente del mismo Team; obligatorio |
| `responsible_user_id` | Membership activa del mismo Team; obligatorio |
| `session_id` | contexto opcional del mismo Team y Vehicle |
| `observation_id` | origen opcional compatible con Team y Vehicle |
| `action_id` | Action opcional de tipo `MECHANICAL` y Vehicle compatible |
| `maintenance_type` | vocabulario controlado definido en la sección 6 |
| `status` | inicia `OPEN` y sólo cambia mediante comandos |
| `description` | texto recortado de 1–2000 caracteres |
| `completion_notes` | requerido al completar; ausente en otros estados |
| `cancellation_reason` | requerido al cancelar; ausente en otros estados |
| `started_at` | fijado por servidor al iniciar; opcional |
| `completed_at` | fijado por servidor al completar; opcional |
| `cancelled_at` | fijado por servidor al cancelar; opcional |
| `created_by_user_id` | actor autenticado; fijado por servidor |
| `visibility_level` | fijo en `ROLE_RESTRICTED` durante la primera porción |
| timestamps | `created_at` y `updated_at` en UTC, server-side |

No se incluyen horas de motor, kilometraje, costo, piezas ni proveedor en la
primera porción. Añadir un campo requiere evidencia de uso y unidad claramente
definida.

## 6. Vocabularios controlados

### Maintenance Type

```text
INSPECTION
PREVENTIVE_SERVICE
REPAIR
REPLACEMENT
```

El tipo clasifica el trabajo; no afirma que resolvió el síntoma.

### Maintenance Status

```text
OPEN → IN_PROGRESS | COMPLETED | CANCELLED
IN_PROGRESS → COMPLETED | CANCELLED
COMPLETED y CANCELLED → terminales
```

- completar exige `completion_notes` y fija `completed_at`;
- cancelar exige `cancellation_reason` y fija `cancelled_at`;
- estados terminales no se reabren mediante la API normal;
- no existe DELETE;
- una corrección histórica futura deberá conservar actor, fecha y motivo.

## 7. Integridad de relaciones

Todas las referencias pertenecen al Team activo. Además:

1. si existe `session_id`, la Session utiliza el mismo Vehicle;
2. si Observation referencia Vehicle, debe coincidir;
3. si Observation referencia Session, esa Session debe utilizar el mismo
   Vehicle;
4. si existe `action_id`, Action debe ser `MECHANICAL`;
5. la Session origen de Action debe utilizar el mismo Vehicle;
6. referencias opcionales que se contradigan se rechazan de forma atómica;
7. ausencia de referencia no se sustituye por una relación inventada.

Las FKs compuestas protegerán Team ownership donde sea práctico. Las reglas
que atraviesan varias tablas se validarán dentro de una transacción.

## 8. Disponibilidad del Vehicle

Los estados vigentes permanecen:

```text
READY | MAINTENANCE | UNAVAILABLE | RETIRED
```

El estado de Maintenance Record y el estado del Vehicle son conceptos
independientes:

- crear o completar un registro no cambia el Vehicle automáticamente;
- marcar `MAINTENANCE`, `UNAVAILABLE` o `READY` requiere un comando explícito;
- sólo `READY` permite una asignación nueva;
- completar una reparación no autoriza inferir `READY`;
- `RETIRED` continúa terminal;
- cada liberación a `READY` conservará actor y momento mediante auditoría
  selectiva.

Esta separación permite capturar una inspección histórica sin retirar el
Vehicle y evita devolverlo accidentalmente a pista.

## 9. Autorización inicial

| Operación | Administrator | Team Manager | Engineer | Mechanic | Driver |
|---|---:|---:|---:|---:|---:|
| Leer mantenimiento | Sí | Sí | Sí | Sí | No |
| Crear registro | No | Sí | Sí | Sí | No |
| Actualizar registro abierto | No | Sí | Sí | Sí | No |
| Iniciar, completar o cancelar | No | Sí | Sí | Sí | No |
| Marcar `MAINTENANCE`/`UNAVAILABLE` | Sí | Sí | Sí | Sí | No |
| Liberar a `READY` | Sí | Sí | Sí | Sí | No |

Se crearán permisos explícitos `READ_MAINTENANCE`, `WRITE_MAINTENANCE` y
`CHANGE_VEHICLE_AVAILABILITY`. No se reutilizará `MANAGE_VEHICLES`, porque
editar el identificador y cambiar disponibilidad son capacidades distintas.

Driver puede conocer únicamente el estado autorizado del Vehicle asociado a
su Session; no recibe el historial técnico ni se revela su existencia mediante
conteos o errores.

## 10. Contrato HTTP propuesto

```text
POST  /api/v1/maintenance-records
GET   /api/v1/maintenance-records
GET   /api/v1/maintenance-records/{maintenance_id}
GET   /api/v1/maintenance-records/{maintenance_id}/causal-chain
PATCH /api/v1/maintenance-records/{maintenance_id}

POST /api/v1/maintenance-records/{maintenance_id}/start
POST /api/v1/maintenance-records/{maintenance_id}/complete
POST /api/v1/maintenance-records/{maintenance_id}/cancel

GET  /api/v1/vehicles/{vehicle_id}/maintenance-history
POST /api/v1/vehicles/{vehicle_id}/mark-maintenance
POST /api/v1/vehicles/{vehicle_id}/mark-unavailable
POST /api/v1/vehicles/{vehicle_id}/mark-ready
```

El listado podrá filtrar por `vehicle_id`, `maintenance_type`, `status`,
`session_id`, `limit` y `offset`. Team ownership y autorización se aplican
antes de calcular `total`.

Los tres endpoints existentes de estado de Vehicle conservarán su URL, pero
pasarán al permiso específico de disponibilidad.

## 11. Errores estables

| Situación | HTTP | Código |
|---|---:|---|
| permiso ausente | 403 | `insufficient_permissions` |
| recurso inexistente, ajeno o no visible | 404 | `resource_not_found` |
| Session, Observation o Action incompatible | 409 | `maintenance_context_conflict` |
| responsable no pertenece al Team | 409 | `maintenance_responsible_conflict` |
| transición de intervención inválida | 409 | `invalid_maintenance_status_transition` |
| edición de registro terminal | 409 | `maintenance_record_locked` |
| referencia a Action no mecánica | 409 | `maintenance_context_conflict` |
| transición de Vehicle inválida | 409 | `invalid_vehicle_status_transition` |
| body inválido o campo prohibido | 422 | `REQUEST_VALIDATION_ERROR` |

## 12. Flujo vertical de aceptación

1. Engineer registra una Observation de vibración en una Session.
2. Mechanic recibe una Action `MECHANICAL` para inspeccionar el Vehicle.
3. Mechanic crea un Maintenance Record `INSPECTION` relacionado.
4. Un actor autorizado marca el Vehicle como `MAINTENANCE`.
5. Mechanic inicia y completa la intervención con una conclusión breve.
6. El Vehicle permanece `MAINTENANCE`.
7. Un actor autorizado verifica el estado y ejecuta `mark-ready`.
8. El historial recupera Observation, Action e intervención en orden.
9. Una Session nueva sólo acepta el Vehicle después de quedar `READY`.

La prueba también cubrirá referencias de otro Team, vínculos incompatibles,
Action no mecánica, transiciones repetidas y ausencia de escrituras parciales.

## 13. Criterio de aprobación

El contrato queda listo para persistencia cuando el propietario apruebe:

- cuatro tipos y cuatro estados sin campos de ERP;
- relaciones causales opcionales, nunca inventadas;
- separación entre intervención y disponibilidad;
- exclusión de Driver del historial técnico;
- permisos específicos de mantenimiento y disponibilidad;
- entregas pequeñas de la checklist de Fase 10.

## 14. Evidencia de persistencia

El Bloque 10.2 materializó `MaintenanceRecord` y la revisión
`20261113_0012_maintenance` con:

- enums privados `maintenance_type` y `maintenance_status`;
- ownership compuesto para Vehicle, responsable, creador y contexto opcional;
- checks de texto, estado, timestamps y visibilidad;
- cinco índices de consulta por Team;
- historial restrictivo sin cascadas destructivas;
- migración reversible validada en CI efímero;
- pruebas PostgreSQL que confirman defaults, contexto y rechazo entre Teams.

La consistencia semántica entre Vehicle, Session, Observation y Action se
validará en servicios durante el Bloque 10.5. Las FKs actuales garantizan
pertenencia al Team, pero deliberadamente no simulan reglas entre tablas que
PostgreSQL no puede expresar mediante un `CHECK` local.

## 15. Evidencia de creación y consulta

El Bloque 10.3 expuso únicamente la frontera mínima autorizada:

- `READ_MAINTENANCE` para Administrator, Team Manager, Engineer y Mechanic;
- `WRITE_MAINTENANCE` para Team Manager, Engineer y Mechanic;
- creación sin campos de ownership, lifecycle, visibilidad o contexto causal;
- responsable con User y Membership activos dentro del Team;
- listados filtrables por Vehicle, tipo y estado antes del conteo;
- detalle y listados que ocultan recursos de otros Teams;
- Driver sin acceso al módulo técnico.

Las transiciones, edición y referencias causales se incorporaron de forma
incremental en los Bloques 10.4 y 10.5.

## 16. Evidencia del ciclo de intervención

El Bloque 10.4 implementa la máquina de estados acordada mediante comandos
explícitos:

- `OPEN → IN_PROGRESS`, `COMPLETED` o `CANCELLED`;
- `IN_PROGRESS → COMPLETED` o `CANCELLED`;
- `COMPLETED` y `CANCELLED` son terminales;
- `PATCH` sólo permite responsable, tipo y descripción mientras está `OPEN`;
- completar exige `completion_notes` y cancelar exige `cancellation_reason`;
- los timestamps se generan en el servidor;
- cada decisión de transición bloquea la fila en PostgreSQL;
- una intervención completada nunca cambia por sí sola la disponibilidad del
  Vehicle.

Una prueba concurrente ejecuta completar y cancelar contra el mismo registro.
El bloqueo serializa ambos comandos: exactamente uno persiste y el segundo
recibe `invalid_maintenance_status_transition`, sin estado híbrido ni escritura
parcial. En ese punto, las relaciones causales permanecían reservadas para el
Bloque 10.5.

## 17. Evidencia de la cadena causal

El Bloque 10.5 permite proporcionar `session_id`, `observation_id` y
`action_id` al crear una intervención. Las referencias siguen siendo
opcionales y no se derivan a partir de otras tablas.

La validación transaccional exige:

- recursos visibles y pertenecientes al Team activo;
- la misma Session cuando más de una referencia aporta contexto temporal;
- el mismo Vehicle en Session, Observation, Action e intervención;
- una Action clasificada exclusivamente como `MECHANICAL`;
- bloqueo de las filas Session mientras se decide y persiste la relación;
- ausencia total de escritura si cualquier nodo es incompatible.

`GET /api/v1/maintenance-records/{maintenance_id}/causal-chain` recupera sólo
los nodos almacenados explícitamente. La representación de Action reutiliza
la proyección por Role, por lo que el detalle confidencial continúa reservado
a Engineering. Los filtros existentes de Observation y Action también se
aplican: un nodo no visible se omite sin revelar su contenido. Driver permanece
fuera de toda la API de mantenimiento.

El listado acepta además `session_id` y aplica el filtro antes del conteo. Las
pruebas cubren referencias extranjeras, Vehicle incompatible, Action no
mecánica, Sessions contradictorias, autorización y ausencia de escrituras
parciales.
