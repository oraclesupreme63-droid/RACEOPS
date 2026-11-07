# RaceOps — Lenguaje ubicuo

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G3
- **Propósito:** Utilizar los mismos términos en investigación, requisitos,
  código, API, base de datos y conversación con usuarios.

## 2. Organización e identidad

### Team

Unidad propietaria de información en RaceOps. Todo recurso operativo debe
pertenecer a un Team. En V1 no representa todavía un tenant comercial.

### User

Identidad que puede autenticarse. Un User no es automáticamente un Driver.

### Team Membership

Relación que concede a un User acceso a un Team y un rol principal. V1
permite una membresía activa y un rol principal por usuario; esta
restricción puede revisarse con evidencia.

### Role

Conjunto de responsabilidades autorizadas: Administrator, Team Manager,
Engineer, Mechanic o Driver.

### Driver

Perfil deportivo de una persona que participa en sesiones. Puede existir
sin una cuenta User. Cuando tiene acceso, puede vincularse a un User.

## 3. Operación

### Vehicle

Unidad de competición administrada por el equipo. Tiene estado operativo y
conserva historia aunque deje de utilizarse.

### Vehicle Status

Estado que determina disponibilidad: `READY`, `MAINTENANCE`,
`UNAVAILABLE` o `RETIRED`. Sólo `READY` permite una asignación nueva.

### Track

Circuito o pista donde ocurre un Event. V1 almacena información mínima y no
pretende sustituir las bases de pistas de sistemas de telemetría.

### Event

Contexto de trabajo relacionado con un Team, una Track y un periodo. Agrupa
una o más Sessions.

### Session

Actividad en pista asociada con un Event, Driver y Vehicle. «Session» nunca
significa sesión HTTP o token de autenticación en el lenguaje del dominio.

### Session Status

Estado de la actividad: `PLANNED`, `ACTIVE`, `PAUSED`, `COMPLETED` o
`CANCELLED`.

### Results Status

Estado independiente que indica si los resultados de una Session continúan
`OPEN` o están `LOCKED`.

**Regla lingüística:** «Completar la sesión» termina la actividad en pista;
«bloquear resultados» impide la captura normal posterior. No son sinónimos.

## 4. Resultados y contexto

### Lap

Resultado temporal de una vuelta dentro de una Session. Tiene número único,
duración positiva, origen y elegibilidad estadística.

### Eligible Lap

Lap autorizada para cálculos principales. Una vuelta puede conservarse en
el historial aunque no sea elegible.

### Sector

Resultado temporal opcional de una sección de una Lap. Su ausencia no
invalida automáticamente la vuelta completa.

### Condition Snapshot

Conjunto opcional de condiciones conocidas para una Session: clima,
temperatura ambiente, temperatura de pista u otra condición autorizada. Un
dato desconocido permanece ausente; no se representa como cero.

### Telemetry Reference

Referencia a una fuente o archivo externo asociado con una Session. En V1
no implica que RaceOps pueda interpretar su contenido.

## 5. Experiencia, evidencia y razonamiento

### Driver Feedback

Descripción de lo que el Driver experimentó. Distingue al Driver que lo
experimentó del User que lo registró.

### Observation

Hecho, síntoma o comportamiento registrado por un miembro autorizado. Una
Observation no es automáticamente una causa.

### Session Analysis

Síntesis realizada por ingeniería que relaciona información disponible de
una Session.

### Hypothesis

Explicación posible de una Observation o pérdida de rendimiento. Tiene
clasificación, confianza y estado de evaluación. No equivale a un hecho.

### Confidence

Grado de confianza declarado: `LOW`, `MEDIUM` o `HIGH`. No representa una
probabilidad calculada.

### Hypothesis Status

Estado del aprendizaje: `PROPOSED`, `SUPPORTED`, `PARTIALLY_SUPPORTED`,
`REJECTED` o `INCONCLUSIVE`.

## 6. Decisión y aprendizaje

### Priority

Enfoque concreto para un destinatario en la siguiente Session. Una
Priority indica qué merece atención; no necesariamente describe trabajo
que deba ejecutarse.

### Main Priority

Priority destacada. Se permiten hasta tres por destinatario y Session
objetivo. Otras notas no se presentan como prioridades principales.

### Action

Trabajo decidido para Driver, Engineer o Mechanic. Tiene responsable,
estado, Session de origen y objetivo.

### Action Status

Estado de ejecución: `PROPOSED`, `PLANNED`, `IN_PROGRESS`, `COMPLETED` o
`CANCELLED`.

### Action Outcome

Evaluación registrada de lo ocurrido después de ejecutar una Action:
`IMPROVED`, `WORSENED`, `NO_MEASURABLE_CHANGE` o `INCONCLUSIVE`.

`NOT_EVALUATED` es el estado derivado que se muestra cuando todavía no
existe Action Outcome; no se crea un resultado ficticio para representar
ausencia de evaluación.

**Regla lingüística:** Action `COMPLETED` significa «se ejecutó»; Outcome
`IMPROVED` significa «existe evidencia de mejora». No son equivalentes.

### Conclusion

Explicación breve del aprendizaje obtenido al evaluar una Action. Puede
mantener incertidumbre.

### Session Learning Loop

Flujo central que conecta Session, información disponible, razonamiento,
decisión y resultado posterior.

## 7. Acceso y conservación

### Visibility Level

Clasificación de acceso de un registro o contenido:

- `TEAM`;
- `ROLE_RESTRICTED`;
- `ENGINEERING_CONFIDENTIAL`.

### Authorized Summary

Explicación visible para un rol sin incluir contenido que no está autorizado
a consultar.

### Team Ownership

Regla por la cual todo recurso operativo pertenece a un Team y nunca puede
relacionarse con recursos de otro equipo.

### Historical Preservation

Conservación de relaciones aunque User, Driver o Vehicle dejen de estar
activos. No implica event sourcing ni conservar cada cambio de todos los
campos.

### Deactivation

Acción reversible que impide uso futuro sin eliminar historia.

### Retirement

Estado de Vehicle que impide nuevas asignaciones y normalmente se considera
terminal.

## 8. Términos reservados para P1 o futuro

### Maintenance Record — P1

Registro de inspección, mantenimiento, reparación o reemplazo relacionado
con un Vehicle.

### Incident

No es una entidad independiente en P0. Una Observation puede marcar una
necesidad de inspección; un módulo separado requiere más evidencia.

### Telemetry Import — P2

Proceso de validar y normalizar un formato externo. No debe confundirse con
Telemetry Reference.

## 9. Términos que deben evitarse sin precisión

- «Problema confirmado» cuando solamente existe una Observation.
- «Funcionó» cuando la Action sólo está `COMPLETED`.
- «Sin datos» representado como cero.
- «Todos pueden verlo» sin especificar Visibility Level.
- «Historial» sin indicar por pista, evento, sesión, piloto o vehículo.
- «Telemetría» para referirse a resultados manuales o referencias externas.
- «Usuario» cuando se quiere decir Driver.

