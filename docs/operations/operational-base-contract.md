# RaceOps — Contrato de la base operativa

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** contrato y persistencia aprobados; APIs de Driver y Vehicle implementadas
- **Alcance:** Driver, Vehicle, Track y Event
- **Fuera de alcance:** Session, resultados, telemetría y mantenimiento

## 2. Resultado buscado

La Fase 7 debe dejar disponibles los cuatro recursos mínimos que una Session
necesitará en la Fase 8. El contrato evita convertir RaceOps en un registro
administrativo pesado: sólo conserva identidad operativa, disponibilidad,
ownership e historia básica.

## 3. Clasificación de decisiones

| Decisión | Clasificación | Fundamento |
|---|---|---|
| Driver es distinto de User | Respaldada | Un piloto puede no tener credenciales y una cuenta no es un perfil deportivo |
| Driver inactivo conserva historia | Respaldada | RF-015, AC-005 y AC-008 |
| Sólo Vehicle `READY` es asignable | Respaldada | RF-019–RF-021 y AC-006 |
| Event y Track comparten Team | Respaldada | RF-027, RF-029 y AC-007 |
| No existe borrado físico normal | Parcialmente respaldada | RF-022, RF-030 y necesidad de trazabilidad |
| Identifier de Vehicle es único por Team | Hipótesis técnica | Evita ambigüedad operativa; deberá validarse con equipos |
| Estados de Event | Hipótesis de dominio | RF-028 pide estado, pero las entrevistas no validan un ciclo concreto |
| Track pertenece al Team | Decisión arquitectónica vigente | Simplifica ownership V1; no afirma que el circuito sea propiedad real del equipo |

Las hipótesis se implementan de forma pequeña y reversible. No se agregan
licencias, datos médicos, inventario, costos, categorías ni setup técnico.

## 4. Driver

### Datos mínimos

| Campo | Regla |
|---|---|
| `driver_id` | UUID generado por servidor |
| `team_id` | obligatorio; derivado del actor |
| `user_id` | opcional |
| `display_name` | obligatorio, recortado, 1–120 caracteres |
| `status` | `ACTIVE` o `INACTIVE`; inicia `ACTIVE` |
| timestamps | `created_at` y `updated_at` server-side en UTC |

### Reglas

- Driver puede existir sin User.
- Si existe `user_id`, User debe tener una Membership en el mismo Team.
- Un mismo User se vincula como máximo con un Driver dentro de cada Team. El
  mismo User puede representar perfiles separados en Teams distintos.
- Desactivar es reversible, impide asignaciones futuras y nunca elimina
  relaciones históricas.
- No existe endpoint `DELETE` normal.
- Un actor con Role Driver sólo consulta su perfil vinculado; sin vínculo no
  obtiene por aproximación otro Driver.

Este vínculo por Team refina el ERD conceptual para ser compatible con una
cuenta que tenga Memberships legítimas en varios equipos.

## 5. Vehicle

### Datos mínimos

| Campo | Regla |
|---|---|
| `vehicle_id` | UUID generado por servidor |
| `team_id` | obligatorio; derivado del actor |
| `identifier` | obligatorio, recortado, 1–80 caracteres, único por Team |
| `status` | `READY`, `MAINTENANCE`, `UNAVAILABLE` o `RETIRED`; inicia `READY` |
| timestamps | `created_at` y `updated_at` server-side en UTC |

### Reglas

- Sólo `READY` podrá utilizarse en una asignación nueva.
- `RETIRED` es terminal mediante el flujo normal.
- Cambiar a `READY` siempre es explícito; no se deriva de otra entidad.
- Un cambio inválido no modifica el Vehicle.
- No existe endpoint `DELETE` normal.

Transiciones aceptadas:

```text
READY       → MAINTENANCE | UNAVAILABLE | RETIRED
MAINTENANCE → READY | UNAVAILABLE | RETIRED
UNAVAILABLE → READY | MAINTENANCE | RETIRED
RETIRED     → ninguna
```

## 6. Track

### Datos mínimos

| Campo | Regla |
|---|---|
| `track_id` | UUID generado por servidor |
| `team_id` | obligatorio; derivado del actor |
| `name` | obligatorio, recortado, 1–160 caracteres |
| `location` | opcional, recortado, máximo 200 caracteres |
| timestamps | `created_at` y `updated_at` server-side en UTC |

No se exige layout, longitud, coordenadas, sectores ni información de
telemetría. Tracks con nombres parecidos no se fusionan automáticamente. No
existe borrado físico normal; archivado podrá añadirse si la práctica lo
justifica.

## 7. Event

### Datos mínimos

| Campo | Regla |
|---|---|
| `event_id` | UUID generado por servidor |
| `team_id` | obligatorio; derivado del actor |
| `track_id` | obligatorio; Track del mismo Team |
| `name` | obligatorio, recortado, 1–160 caracteres |
| `starts_on` | fecha obligatoria |
| `ends_on` | opcional; nunca anterior a `starts_on` |
| `description` | opcional, máximo 1000 caracteres |
| `status` | `PLANNED`, `ACTIVE`, `COMPLETED` o `CANCELLED`; inicia `PLANNED` |
| timestamps | `created_at` y `updated_at` server-side en UTC |

El ciclo de Event se mantiene deliberadamente simple:

```text
PLANNED → ACTIVE | COMPLETED | CANCELLED
ACTIVE  → COMPLETED | CANCELLED
COMPLETED y CANCELLED → terminales en V1
```

Permitir `PLANNED → COMPLETED` evita obligar a registrar en vivo el inicio de
un evento. Esta transición es una hipótesis de baja fricción que deberá
revisarse con uso real.

Cuando Event tenga una Session, cambiar su Track quedará prohibido. La regla
se materializará en Fase 8 porque aún no existe Session.

## 8. Ownership y autorización

- `team_id` nunca se acepta desde el body; se obtiene de CurrentIdentity.
- Un UUID de otro Team responde `404 resource_not_found`.
- Una capacidad ausente responde `403 insufficient_permissions`.
- Administrator y Team Manager administran los cuatro recursos.
- Engineer consulta Drivers/Vehicles y administra Tracks/Events.
- Mechanic consulta Drivers, Vehicles, Tracks y Events.
- Driver consulta únicamente su Driver, Vehicles y Events relacionados; como
  esas relaciones nacen con Session, en Fase 7 no se le concede por
  aproximación un listado general de Vehicles o Events. Track sí puede
  consultarse como catálogo del Team según la matriz vigente.
- Las lecturas se implementarán con permisos explícitos, relación y Team
  scope; `READ_HISTORY` no servirá para saltar esas comprobaciones.

Los permisos de lectura específicos se incorporarán junto con las APIs para
evitar reutilizar incorrectamente permisos administrativos.

## 9. Contrato HTTP futuro

Las colecciones vivirán bajo `/api/v1`:

```text
/drivers
/vehicles
/tracks
/events
```

Cada API ofrecerá sólo las operaciones aprobadas de crear, listar, consultar,
actualizar y ejecutar transiciones explícitas. Listados tendrán paginación
estable y filtrarán por Team antes de contar. No habrá CRUD genérico ni
respuesta que serialice `team_id` suministrado por el cliente como ownership.

Errores esperados:

| Situación | HTTP | Código estable |
|---|---:|---|
| token inválido | 401 | `invalid_access_token` |
| permiso ausente | 403 | `insufficient_permissions` |
| recurso inexistente o de otro Team | 404 | `resource_not_found` |
| identificador duplicado o transición inválida | 409 | código específico del recurso |
| body inválido | 422 | `REQUEST_VALIDATION_ERROR` |

## 10. Persistencia prevista

- cuatro tablas operativas con UUID, `team_id` y timestamps;
- FKs restrictivas para evitar pérdida histórica;
- enums PostgreSQL nombrados y migración reversible;
- unique `(team_id, user_id)` cuando Driver tenga User;
- unique `(team_id, identifier)` para Vehicle;
- constraint de fechas de Event;
- índices comenzando por `team_id` para consultas aisladas;
- servicios específicos sobre SQLAlchemy Session, sin repository genérico.

## 11. Criterios de aceptación del contrato

El diseño queda listo para persistencia cuando:

- cada campo existe por una regla o uso inmediato;
- Driver/User y Event/Track no pueden cruzar Teams;
- inactividad, disponibilidad y estados terminales son explícitos;
- ninguna operación normal borra historia;
- los límites de autorización tienen resultado HTTP definido;
- las hipótesis continúan identificadas como tales.

## 12. Límites conscientes

AC-005 y AC-006 se completarán de extremo a extremo al crear Session en Fase
8. Durante Fase 7 se probarán los estados y predicados de asignabilidad sin
crear una Session ficticia. Track inmutable después de la primera Session se
probará también en Fase 8.

## 13. Evidencia de implementación

El Bloque 7.2 materializa este contrato en cuatro modelos SQLAlchemy y la
revisión Alembic `20261108_0003_operations`. PostgreSQL aplica ownership por
Team, vínculos Driver/User y Event/Track del mismo Team, unicidad acotada,
fechas válidas y referencias históricas restrictivas. Las pruebas unitarias y
de integración cubren los constraints y el recorrido upgrade/downgrade de la
migración. El comportamiento HTTP permanece pendiente para Track y Event en
el Bloque 7.5.

El Bloque 7.3 implementa el contrato HTTP de Driver. Administrator y Team
Manager administran; Engineer y Mechanic consultan; Driver sólo recibe el
perfil vinculado con su User. Los listados filtran por Team y relación antes
de calcular `total`, no aceptan `team_id`, y los recursos ajenos comparten la
respuesta `404 resource_not_found`. Activar y desactivar son operaciones
explícitas e idempotentes; no existe endpoint de borrado.

El Bloque 7.4 implementa el contrato HTTP de Vehicle. Administrator y Team
Manager administran; Engineer y Mechanic consultan. El permiso de Driver se
mantiene denegado hasta que Session permita comprobar una relación real. La
API filtra por Team antes de contar, inicia cada Vehicle en `READY`, ejecuta
transiciones mediante comandos explícitos y rechaza cambios repetidos o desde
`RETIRED` sin modificar el registro. El predicado de asignabilidad confirma
que solamente `READY` podrá usarse en la Fase 8. No existe endpoint de borrado.
