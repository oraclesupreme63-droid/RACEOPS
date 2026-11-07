# RaceOps — Reglas de negocio

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G3
- **Alcance:** Reglas P0 y reglas P1 relevantes para preservar coherencia

## 2. Identidad, propiedad y autorización

### BR-001 — Equipo activo

Toda operación protegida necesita User y TeamMembership activos.

### BR-002 — Propiedad uniforme

Los recursos relacionados en una operación deben pertenecer al mismo Team.

### BR-003 — Autorización en servidor

La interfaz nunca constituye una frontera de seguridad. El caso de uso o
servicio de aplicación valida autorización antes de leer o modificar.

### BR-004 — Menor privilegio

Una capacidad no concedida expresamente se considera denegada.

### BR-005 — Rol principal V1

Cada TeamMembership activa tiene exactamente un Role principal en V1.

### BR-006 — Administración separada de contenido

Administrator puede gestionar acceso sin recibir automáticamente contenido
`ENGINEERING_CONFIDENTIAL`.

### BR-007 — Driver sin contenido confidencial

Driver nunca consulta `ENGINEERING_CONFIDENTIAL` en V1.

### BR-008 — Autoría histórica

Desactivar User o Membership no elimina ni reasigna registros que creó.

## 3. Base operativa

### BR-009 — Driver independiente de User

Un Driver puede existir sin credenciales. Si se vincula con User, ambos
deben pertenecer al mismo Team.

### BR-010 — Driver asignable

Sólo un Driver activo puede asignarse a una nueva Session.

### BR-011 — Vehicle asignable

Sólo un Vehicle `READY` puede asignarse a una nueva Session.

### BR-012 — Preservación operativa

Driver inactivo y Vehicle retirado continúan visibles en historia
autorizada.

### BR-013 — Track de Event

Event pertenece a un Track del mismo Team. El Track no cambia mediante el
flujo normal después de crear la primera Session del Event.

## 4. Session y resultados

### BR-014 — Creación de Session

Una Session nueva comienza `PLANNED` con resultados `OPEN`.

### BR-015 — Asignación atómica

Event, Driver y Vehicle se validan antes de crear Session. Si una validación
falla, no queda una Session parcial.

### BR-016 — Transición válida

Session Status sólo cambia según el diagrama aprobado.

### BR-017 — Inicio real

`started_at` se registra cuando Session pasa por primera vez a `ACTIVE`.

### BR-018 — Fin real

`ended_at` se registra al pasar a `COMPLETED` o `CANCELLED`.

### BR-019 — Actividad y bloqueo separados

`COMPLETED` no cambia automáticamente Results Status a `LOCKED`.

### BR-020 — Bloqueo permitido

Results Status puede pasar a `LOCKED` cuando Session está `COMPLETED` o
`CANCELLED` y el actor tiene permiso.

### BR-021 — Resultados bloqueados

No se crean ni modifican Laps o Sectors por el flujo normal cuando los
resultados están `LOCKED`.

### BR-022 — Corrección excepcional

Una corrección posterior al bloqueo es P1 y requiere permiso, motivo,
ActorStamp y conservación del valor anterior cuando corresponda.

## 5. Laps, Sectors y métricas

### BR-023 — Número de Lap

Lap number es positivo y único dentro de Session.

### BR-024 — Duration válida

Lap y Sector usan Duration positiva en una unidad interna exacta y
documentada.

### BR-025 — Sector opcional

Una Lap no necesita Sectors para existir.

### BR-026 — Orden de Sector

Sector order es positivo y único dentro de Lap.

### BR-027 — Elegibilidad

Sólo Laps elegibles participan en mejor vuelta y promedio.

### BR-028 — Transparencia de cálculo

El resumen muestra total de Laps y cantidad elegible.

### BR-029 — Datos insuficientes

Sin Laps elegibles, las métricas se presentan como no disponibles, no como
cero.

### BR-030 — Reproducibilidad

Las métricas derivan de valores canónicos almacenados y una fórmula
documentada.

## 6. Contexto, feedback y observaciones

### BR-031 — Contexto opcional

Ninguna condición especializada es obligatoria para completar P0.

### BR-032 — Valor y unidad

Una condición numérica presente conserva una unidad compatible. Un valor
ausente no necesita unidad.

### BR-033 — Feedback asignado

Driver sólo registra feedback propio en una Session que tenga asignada.

### BR-034 — Experiencia y captura

Driver Feedback conserva por separado `driver_id` y `author_user_id`.

### BR-035 — Captura breve

Descripción, Session, Driver y autor bastan para feedback P0; campos de
zona, fase, severidad y confianza son opcionales.

### BR-036 — Observation relacionada

Observation se relaciona al menos con Session o Vehicle del mismo Team.

### BR-037 — Sin causalidad automática

Observation no actualiza por sí sola Hypothesis Status ni se presenta como
causa confirmada.

## 7. Análisis e hipótesis

### BR-038 — Autor de análisis

Sólo Engineer autorizado crea o modifica Session Analysis en P0.

### BR-039 — Evidencia parcial válida

El análisis puede realizarse con información incompleta; nunca inventa las
fuentes ausentes.

### BR-040 — Hypothesis explícita

Cada Hypothesis necesita descripción, causa, Confidence y estado inicial
`PROPOSED`.

### BR-041 — Cambio sustentado

Hypothesis Status cambia desde `PROPOSED` mediante una Conclusion vinculada
a evidencia posterior o una revisión autorizada.

### BR-042 — Explicación autorizada

El detalle técnico y el resumen autorizado se almacenan separadamente
cuando deban mostrarse a públicos distintos.

## 8. Prioridades, acciones y resultados

### BR-043 — Prioridad concreta

Priority describe un enfoque accionable, no una copia automática de
métricas.

### BR-044 — Límite de principales

Existen como máximo tres Main Priorities activas por destinatario y Session
objetivo o intención `NEXT_SESSION`.

### BR-045 — Objetivo pendiente

Priority o Action puede usar `NEXT_SESSION` sin `target_session_id`; debe
vincularse a una Session real antes de crear Action Outcome.

### BR-046 — Origen de Action

Action tiene Source Session y al menos una motivación: Hypothesis, Priority
o descripción autorizada explícita.

### BR-047 — Responsable

Action indica Role responsable y, opcionalmente, User responsable del mismo
Team.

### BR-048 — Ejecución independiente

Action Status `COMPLETED` no crea ni clasifica Action Outcome.

### BR-049 — Outcome con evidencia

Action Outcome necesita una evaluation Session del mismo Team.

### BR-050 — Mejora sustentada

Outcome `IMPROVED` no puede guardarse sin identificar Session o evidencia
posterior autorizada.

### BR-051 — Incertidumbre permitida

Outcome y Conclusion pueden permanecer `INCONCLUSIVE`. Cuando no existe
Outcome, la Action se presenta como `NOT_EVALUATED` sin crear un resultado
ficticio.

### BR-052 — Cadena preservada

No se elimina normalmente ningún elemento que rompa Observation →
Hypothesis → Action → Outcome.

## 9. Historia y reportes

### BR-053 — Filtrado acumulativo

Una consulta aplica Team Ownership, Role, relación con el recurso y
Visibility antes de devolver registros o conteos.

### BR-054 — Resumen por rol

Dos usuarios pueden recibir contenidos diferentes para la misma Session.

### BR-055 — Ausencia explícita

Reportes distinguen dato ausente, cero, no concluyente y no evaluado.

### BR-056 — No revelar existencia

Filtros, errores y conteos no revelan recursos confidenciales no
autorizados.

## 10. P1 Maintenance

### BR-057 — Intervención no libera Vehicle

Completar Maintenance Record no cambia Vehicle a `READY` automáticamente.

### BR-058 — Liberación explícita

El cambio a `READY` requiere un actor autorizado y se registra por separado.

### BR-059 — Relación causal opcional

Maintenance Record puede relacionarse con Session, Observation o Action,
pero no inventa una relación cuando se desconoce.

## 11. Evolución de reglas

Una regla cambia mediante:

1. evidencia o necesidad técnica documentada;
2. actualización del requisito relacionado;
3. actualización de aceptación y trazabilidad;
4. revisión de invariantes y migraciones afectadas;
5. decisión registrada cuando el impacto sea material.

