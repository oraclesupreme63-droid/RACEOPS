# RaceOps — Modelo del dominio

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G3
- **Enfoque:** Monolito modular; modelo independiente de FastAPI y SQLAlchemy
- **Prioridad:** Session Learning Loop P0

## 2. Principios de modelado

- El modelo expresa reglas del negocio, no formas de pantallas.
- `team_id` constituye la frontera de propiedad de los datos.
- Las referencias cruzadas siempre validan pertenencia al mismo Team.
- Se separa actividad de Session y bloqueo de resultados.
- Se separa ejecución de Action y efecto observado.
- Se conserva incertidumbre y ausencia de datos.
- No se utiliza event sourcing; la trazabilidad requerida se implementará
  mediante relaciones, marcas de tiempo y auditoría selectiva.
- Los módulos son límites dentro de un monolito, no microservicios.

## 3. Áreas del dominio

| Área | Responsabilidad | Prioridad |
|---|---|---:|
| Identity & Access | User, Team, Membership, Role y autorización | P0 |
| Operations | Driver, Vehicle, Track y Event | P0 |
| Sessions | Session, Lap, Sector, Conditions y Feedback | P0 |
| Learning | Observation, Analysis, Hypothesis, Priority, Action y Outcome | P0 |
| History & Reporting | Consultas filtradas y resúmenes | P0, lectura |
| Telemetry References | Referencias externas sin interpretación | P1 |
| Maintenance | Intervenciones e historial mecánico | P1 |

## 4. Entidades principales

### 4.1 Identity & Access

| Entidad | Identidad | Datos esenciales | Reglas principales |
|---|---|---|---|
| Team | `team_id` | nombre, estado | Propietario de recursos operativos |
| User | `user_id` | email normalizado, password hash, estado | Identidad autenticable; email único según estrategia técnica |
| TeamMembership | `membership_id` | user, team, role, estado | V1: una membresía activa y un rol principal por User |

### 4.2 Operations

| Entidad | Identidad | Datos esenciales | Reglas principales |
|---|---|---|---|
| Driver | `driver_id` | team, nombre, estado, user opcional | Puede existir sin User; inactivo no se asigna |
| Vehicle | `vehicle_id` | team, identificador, estado | Sólo `READY` se asigna a Session nueva |
| Track | `track_id` | team, nombre, ubicación opcional | Recurso mínimo, sin telemetría de pista |
| Event | `event_id` | team, track, nombre, fechas, estado | Track queda inmutable cuando existen Sessions |

### 4.3 Sessions

| Entidad | Identidad | Datos esenciales | Reglas principales |
|---|---|---|---|
| Session | `session_id` | team, event, driver, vehicle, tipo, fecha, status, results status | Asignaciones válidas; ciclos independientes |
| Lap | `lap_id` | team, session, número, duración, origen, elegibilidad | Número único por Session; duración positiva |
| Sector | `sector_id` | team, lap, orden, duración, validez | Orden único por Lap; opcional |
| ConditionSnapshot | `condition_id` | team, session, valores con unidades, origen | Cero o uno en P0; todos los campos contextuales son opcionales |
| DriverFeedback | `feedback_id` | team, session, driver, author, descripción, opcionales, visibility | Driver y autor se distinguen |

### 4.4 Learning

| Entidad | Identidad | Datos esenciales | Reglas principales |
|---|---|---|---|
| Observation | `observation_id` | team, session/vehicle, author, descripción, categoría, visibility | Al menos Session o Vehicle; nunca causa automática |
| SessionAnalysis | `analysis_id` | team, session, author, resumen autorizado, detalle técnico, visibility | Relaciona evidencia por identificadores autorizados |
| Hypothesis | `hypothesis_id` | team, analysis, descripción, causa, confidence, status, visibility | Inicia `PROPOSED`; cambios sustentados por Outcome/Conclusion |
| Priority | `priority_id` | team, source session, target session opcional, destinatario, rank, visibility | Máximo tres principales por destinatario y objetivo |
| Action | `action_id` | team, origen, target session opcional, tipo, responsable, status, visibility | `COMPLETED` no determina Outcome |
| ActionOutcome | `outcome_id` | team, action, evaluation session, clasificación, conclusión, author | `IMPROVED` requiere evidencia identificada |

### 4.5 P1

| Entidad | Identidad | Datos esenciales | Reglas principales |
|---|---|---|---|
| TelemetryReference | `telemetry_reference_id` | team, session, sistema, nombre, ubicación autorizada, notas | No implica lectura o importación |
| MaintenanceRecord | `maintenance_id` | team, vehicle, tipo, descripción, responsable, fecha | Puede relacionarse con Observation, Session o Action |

## 5. Objetos de valor

| Value Object | Contenido | Regla |
|---|---|---|
| Duration | entero en unidad interna documentada | Siempre positiva para Lap y Sector; nunca `float` binario como fuente canónica |
| MeasuredValue | valor decimal + unidad | Unidad obligatoria cuando existe valor |
| Visibility | nivel + roles autorizados cuando aplique | `ROLE_RESTRICTED` necesita al menos un rol |
| Confidence | `LOW`, `MEDIUM`, `HIGH` | No es probabilidad calculada |
| SessionAssignment | driver + vehicle | Mismo Team, Driver activo, Vehicle `READY` al asignar |
| ActorStamp | user + instante | Autoría explícita para cambios relevantes |

## 6. Agregados propuestos

| Aggregate Root | Contenido controlado | Invariantes protegidos |
|---|---|---|
| Team | configuración del equipo | propiedad e identidad del equipo |
| User | credenciales y estado | autenticación segura |
| TeamMembership | rol y estado | una membresía activa/rol principal en V1 |
| Driver | perfil y actividad | preservación histórica |
| Vehicle | identidad y estado | disponibilidad y transiciones |
| Track | datos mínimos | ownership |
| Event | pista y periodo | misma propiedad; pista inmutable con Sessions |
| Session | asignación, status, results status y marcas de tiempo | transiciones y bloqueo |
| Lap | sectores de esa vuelta | unicidad y duración |
| DriverFeedback | contenido y autoría | relación Driver/Session válida |
| Observation | contenido y visibilidad | no falsa causalidad |
| SessionAnalysis | Hypotheses del análisis | confianza, estado y visibilidad |
| Priority | destinatario y jerarquía | máximo de principales |
| Action | ejecución y Outcomes | separar ejecución y efecto |
| MaintenanceRecord | intervención P1 | historia y disponibilidad explícita |

Lap se modela como Aggregate Root independiente de Session para evitar que
una Session con muchas vueltas se convierta en un agregado grande. Sector
permanece dentro del agregado Lap.

## 7. Relaciones esenciales

```text
Team
├── TeamMembership ── User
├── Driver ── optional User
├── Vehicle
├── Track
└── Event ── Track
    └── Session ── Driver + Vehicle
        ├── Lap ── Sector
        ├── ConditionSnapshot
        ├── DriverFeedback
        ├── Observation
        └── SessionAnalysis ── Hypothesis
              ├── Priority ── target Session
              └── Action ── target Session
                    └── ActionOutcome ── evaluation Session
```

Las relaciones no conceden acceso automáticamente. Toda lectura aplica el
Visibility Model.

## 8. Sesión objetivo todavía no creada

Priority y Action pueden definirse antes de crear la siguiente Session.
Por ello se propone:

- `target_session_id` opcional;
- `target_intent = NEXT_SESSION` mientras no exista una Session concreta;
- obligación de vincular la Session real antes de evaluar un Outcome.

Esto refina RF-112 y RF-118, que originalmente exigían una Session objetivo
desde el registro inicial. La alternativa obligaría al equipo a crear una
Session anticipadamente y añadiría fricción sin evidencia.

## 9. Decisiones de identidad e historial

- Driver no hereda de User ni User de Driver.
- Desactivar un User no elimina su autoría histórica.
- Desactivar un Driver impide nuevas asignaciones, no consultas históricas.
- `created_at` y `updated_at` se guardan en UTC.
- Las correcciones sensibles conservan ActorStamp y motivo.
- Los registros históricos se archivan o desactivan; no se eliminan por el
  flujo normal.

## 10. Decisiones de cálculo

- La mejor vuelta es el mínimo de Duration entre Laps elegibles.
- El promedio usa solamente Laps elegibles y documenta el redondeo.
- La cantidad total y la cantidad elegible se muestran por separado.
- Con cero vueltas elegibles, mejor vuelta y promedio son «no disponibles».
- Las métricas se calculan desde datos canónicos almacenados.

## 11. Fuera del modelo P0

- canales de telemetría;
- señales de alta frecuencia;
- mapas de trazada;
- archivos propietarios interpretados;
- inventario de partes;
- costos y facturación;
- logística de viajes;
- recomendaciones automáticas;
- transcripción de radio;
- multi-tenancy SaaS comercial.

## 12. Preguntas para validar durante implementación

- ¿Un User necesita múltiples Memberships activas?
- ¿Priority y Action requieren un destinatario User además del Role?
- ¿Debe existir más de un ConditionSnapshot por Session?
- ¿Una Action necesita varias evaluaciones o sólo un Outcome final?
- ¿Qué transiciones excepcionales requieren auditoría reforzada?

Estas preguntas no justifican aumentar el P0 antes de observar una
necesidad real.
