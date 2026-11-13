# Requerimientos funcionales y no funcionales — RaceOps

## 1. Información del documento

- **Proyecto:** RaceOps
- **Versión:** 2.1
- **Estado:** Refinado por Gate G3; preparado para Gate G4
- **Etapa:** Ingeniería de requerimientos
- **Cobertura funcional:** RF-001 a RF-170
- **Fecha:** Por definir

### Cambios de versión 2.0

- Se incorporó la decisión condicional del Gate G1.
- El flujo Session Learning Loop se mantiene como núcleo P0 provisional.
- El módulo completo de mantenimiento cambió de P0 a P1.
- La disponibilidad mínima del vehículo permanece cubierta por RF-019 a
  RF-021, sin requerir el módulo de mantenimiento.
- Las funciones condicionadas continúan fuera del P0.

### Cambios de versión 2.1

- RF-112 y RF-118 permiten expresar la intención `NEXT_SESSION` sin exigir
  que la sesión objetivo ya haya sido creada.
- RF-124 aclara que `NOT_EVALUATED` se deriva de la ausencia de una
  evaluación; no se almacena como si fuera una conclusión técnica.
- Estos ajustes implementan decisiones aprobadas en el Gate G3 sin ampliar
  el alcance P0.

## 2. Propósito

Este documento consolida los requerimientos funcionales y no funcionales
refinados para RaceOps v1.0. Los casos de uso, matriz de permisos, criterios
de aceptación, backlog y trazabilidad se encuentran en `docs/requirements/`.

RaceOps deberá complementar las herramientas existentes de cronometraje y
telemetría. Su valor principal será conservar la relación entre evidencia,
feedback, análisis, decisiones, acciones y resultados posteriores.

## 3. Convenciones

### Prioridad

| Prioridad | Significado |
|---|---|
| P0 | Imprescindible para el flujo principal |
| P1 | Necesario para RaceOps v1.0 |
| P2 | Condicionado a evidencia y tiempo |
| P3 | Futuro o fuera de v1.0 |

### Fundamento

Las decisiones de producto se clasifican como:

- respaldadas por evidencia;
- parcialmente respaldadas;
- hipótesis;
- rechazadas o con evidencia insuficiente.

Los controles de seguridad, integridad y mantenibilidad pueden justificarse
como necesidades técnicas aunque no provengan directamente de entrevistas.

# 4. Requerimientos funcionales

## 4.1 Identidad, equipos y autorización

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-001 | El sistema permitirá que un usuario activo inicie sesión mediante credenciales válidas. | P0 | Necesidad técnica |
| RF-002 | El sistema rechazará credenciales incorrectas y usuarios desactivados sin revelar cuál dato fue incorrecto. | P0 | Seguridad |
| RF-003 | El sistema almacenará las contraseñas utilizando hashing seguro; nunca en texto plano. | P0 | Seguridad |
| RF-004 | El sistema mantendrá la pertenencia de cada usuario a un equipo y su rol dentro de ese contexto. | P0 | Parcialmente respaldado |
| RF-005 | El sistema autorizará cada operación en el servidor según el rol del usuario. | P0 | Respaldado |
| RF-006 | Un usuario no podrá acceder a recursos pertenecientes a otro equipo. | P0 | Seguridad |
| RF-007 | El sistema distinguirá información `TEAM`, `ROLE_RESTRICTED` y `ENGINEERING_CONFIDENTIAL`. | P0 | Respaldado |
| RF-008 | Un Driver no podrá consultar información clasificada como `ENGINEERING_CONFIDENTIAL`. | P0 | Respaldado |
| RF-009 | Administrator podrá gestionar usuarios, roles, equipos y configuración autorizada. | P1 | Parcialmente respaldado |
| RF-010 | Team Manager podrá gestionar la operación general de su equipo sin obtener automáticamente permisos globales. | P1 | Parcialmente respaldado |
| RF-011 | El sistema permitirá desactivar usuarios sin eliminar la información histórica relacionada con ellos. | P1 | Integridad histórica |
| RF-012 | Los recursos creados registrarán al menos fecha de creación, última actualización y equipo propietario. | P1 | Trazabilidad |

## 4.2 Pilotos

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-013 | Un usuario autorizado podrá registrar un piloto dentro de su equipo. | P0 | Habilitador del flujo |
| RF-014 | Un usuario autorizado podrá consultar y actualizar los datos permitidos de un piloto. | P0 | Habilitador del flujo |
| RF-015 | Un piloto podrá marcarse como activo o inactivo sin eliminar su historial. | P0 | Integridad histórica |
| RF-016 | Un piloto inactivo no podrá asignarse a una sesión nueva. | P0 | Regla de negocio |
| RF-017 | Un Driver sólo podrá acceder a su perfil y a la información que su rol tenga autorizada. | P0 | Respaldado |

## 4.3 Vehículos

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-018 | Un usuario autorizado podrá registrar y actualizar vehículos de su equipo. | P0 | Habilitador del flujo |
| RF-019 | Cada vehículo tendrá un estado operativo. | P0 | Parcialmente respaldado |
| RF-020 | Los estados iniciales serán `READY`, `MAINTENANCE`, `UNAVAILABLE` y `RETIRED`, sujetos a validación durante el modelado. | P0 | Hipótesis de dominio |
| RF-021 | Un vehículo que no esté `READY` no podrá asignarse a una sesión nueva. | P0 | Regla de negocio |
| RF-022 | El sistema conservará el historial del vehículo aunque éste sea retirado. | P1 | Integridad histórica |
| RF-023 | Un usuario autorizado podrá consultar la disponibilidad y el historial permitido de un vehículo. | P1 | Parcialmente respaldado |

## 4.4 Pistas y eventos

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-024 | Un usuario autorizado podrá registrar y actualizar pistas. | P0 | Habilitador del flujo |
| RF-025 | Una pista conservará nombre, ubicación y metadata mínima necesaria. | P1 | Hipótesis de dominio |
| RF-026 | Un usuario autorizado podrá crear y actualizar eventos. | P0 | Habilitador del flujo |
| RF-027 | Un evento deberá relacionarse con una pista y un equipo. | P0 | Regla de negocio |
| RF-028 | Un evento conservará fechas, descripción y estado. | P1 | Habilitador del flujo |
| RF-029 | El sistema impedirá relacionar un evento con recursos pertenecientes a otro equipo. | P0 | Seguridad |
| RF-030 | Pilotos, vehículos, pistas y eventos referenciados históricamente no se eliminarán físicamente mediante las operaciones normales. | P1 | Trazabilidad |

## 4.5 Sesiones

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-031 | Un usuario autorizado podrá crear una sesión dentro de un evento de su equipo. | P0 | Flujo principal |
| RF-032 | La sesión conservará evento, pista, tipo, fecha y equipo propietario. | P0 | Contexto necesario |
| RF-033 | La sesión permitirá asignar un piloto activo y un vehículo disponible. | P0 | Flujo principal |
| RF-034 | El sistema rechazará pilotos inactivos, vehículos no disponibles y recursos de otro equipo. | P0 | Seguridad y negocio |
| RF-035 | La sesión tendrá un ciclo de vida con transiciones válidas. | P0 | Regla de negocio |
| RF-036 | Los estados candidatos serán `PLANNED`, `ACTIVE`, `PAUSED`, `COMPLETED` y `CANCELLED`. | P0 | Hipótesis de dominio |
| RF-037 | Sólo usuarios autorizados podrán iniciar, pausar, completar o cancelar una sesión. | P0 | Seguridad |
| RF-038 | El sistema registrará automáticamente las fechas reales de inicio y finalización cuando correspondan. | P1 | Trazabilidad |
| RF-039 | Una sesión cancelada conservará su historial y el motivo de cancelación. | P1 | Trazabilidad |
| RF-040 | El sistema distinguirá entre actividad completada y resultados bloqueados. | P0 | Flujo posterior |
| RF-041 | Un usuario autorizado podrá cargar resultados después de terminar la actividad mientras éstos no estén bloqueados. | P0 | Respaldado por el flujo real |
| RF-042 | Después de bloquear los resultados no podrán añadirse vueltas o sectores mediante el flujo normal. | P0 | Integridad |
| RF-043 | El bloqueo registrará usuario, fecha y hora. | P1 | Trazabilidad |
| RF-044 | Una corrección posterior al bloqueo requerirá autorización y una justificación. | P1 | Integridad histórica |

## 4.6 Vueltas

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-045 | Un usuario autorizado podrá registrar vueltas en una sesión cuyos resultados estén abiertos. | P0 | Flujo principal |
| RF-046 | Cada vuelta deberá tener un número positivo y único dentro de la sesión. | P0 | Integridad |
| RF-047 | El tiempo de vuelta deberá ser mayor que cero. | P0 | Regla de negocio |
| RF-048 | El sistema conservará la precisión disponible del tiempo registrado. | P1 | Calidad de datos |
| RF-049 | Cada vuelta podrá indicar su origen: manual, importado u otro origen autorizado. | P1 | Respaldado por artefacto público y trazabilidad |
| RF-050 | Una vuelta podrá clasificarse para indicar si es válida para estadísticas. | P0 | Análisis correcto |
| RF-051 | Las vueltas no elegibles no se incluirán en los cálculos principales. | P0 | Análisis correcto |
| RF-052 | El sistema permitirá conservar una vuelta inválida sin eliminarla del historial. | P1 | Evidencia histórica |
| RF-053 | La corrección de una vuelta conservará quién realizó el cambio, cuándo y por qué. | P1 | Trazabilidad |
| RF-054 | Una vuelta referenciada por análisis o acciones no se eliminará físicamente mediante operaciones normales. | P1 | Integridad histórica |

Clasificaciones candidatas de vuelta: `VALID`, `INVALID`, `OUT_LAP`,
`IN_LAP` e `INCOMPLETE`. Se validarán durante el modelado del dominio.

## 4.7 Sectores

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-055 | Una vuelta podrá contener resultados de sectores cuando estén disponibles. | P0 | Respaldado por entrevistas y artefacto público |
| RF-056 | Cada sector tendrá un número u orden único dentro de la vuelta. | P0 | Integridad |
| RF-057 | El tiempo de un sector deberá ser mayor que cero. | P0 | Regla de negocio |
| RF-058 | La ausencia de sectores no impedirá registrar una vuelta completa. | P0 | Baja fricción |
| RF-059 | El sistema permitirá conservar sectores incompletos sin inventar valores faltantes. | P1 | Honestidad de datos |
| RF-060 | El número de sectores podrá variar según la pista o configuración utilizada. | P1 | Flexibilidad |
| RF-061 | El sistema no asumirá que la suma de sectores debe coincidir exactamente con el tiempo oficial de vuelta. | P1 | Variación de fuentes |
| RF-062 | Los sectores inválidos o incompletos no se utilizarán en comparaciones incompatibles. | P1 | Análisis correcto |

## 4.8 Métricas básicas

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-063 | El sistema calculará la mejor vuelta elegible de una sesión. | P0 | Respaldado por artefacto público |
| RF-064 | El sistema calculará el promedio de vueltas elegibles. | P0 | Respaldado |
| RF-065 | El sistema calculará la peor vuelta elegible. | P1 | Parcialmente respaldado |
| RF-066 | El sistema mostrará la cantidad total de vueltas y la cantidad utilizada en estadísticas. | P0 | Transparencia |
| RF-067 | El sistema calculará la desviación estándar poblacional de las vueltas elegibles como medida básica de consistencia y documentará su alcance. | P1 | Implementado; utilidad contextual pendiente |
| RF-068 | El sistema no mostrará una métrica como válida cuando no existan datos suficientes. | P0 | Honestidad de datos |
| RF-069 | Los cálculos deberán poder reproducirse a partir de los datos almacenados. | P0 | Trazabilidad |

## 4.9 Condiciones de la sesión

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-070 | Un usuario autorizado podrá registrar manualmente condiciones asociadas a una sesión. | P0 | Parcialmente respaldado; artefacto público aporta campos reales |
| RF-071 | Las condiciones podrán incluir temperatura ambiente, temperatura de pista, clima y condición general de la pista. | P1 | Respaldado por entrevistas y artefacto público |
| RF-072 | Los campos de condiciones serán opcionales cuando la información no esté disponible. | P0 | Baja fricción |
| RF-073 | Cada valor numérico deberá conservar su unidad de medida. | P0 | Integridad |
| RF-074 | Las condiciones representarán un snapshot relacionado con la sesión. | P1 | Contexto histórico |
| RF-075 | El sistema conservará el origen de las condiciones cuando sea conocido. | P1 | Respaldado por artefacto público y trazabilidad |
| RF-076 | RaceOps funcionará aunque no exista una integración meteorológica externa. | P0 | Resiliencia y alcance |
| RF-077 | La integración automática con clima será condicionada y no bloqueará el MVP. | P2 | Hipótesis |
| RF-078 | Los campos especializados variarán según categoría y no serán obligatorios universalmente. | P0 | Contraevidencia a esquema rígido |

## 4.10 Feedback del piloto

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-079 | Un Driver podrá registrar feedback en una sesión que tenga asignada. | P0 | Respaldado |
| RF-080 | Engineer y usuarios autorizados podrán registrar feedback comunicado verbalmente por el piloto. | P0 | Baja fricción |
| RF-081 | Cada feedback conservará sesión, autor, piloto y momento de registro. | P0 | Trazabilidad |
| RF-082 | Una sesión podrá contener varios elementos de feedback. | P0 | Flujo real |
| RF-083 | El feedback podrá asociarse opcionalmente con curva, zona, vuelta o sector. | P1 | Parcialmente respaldado |
| RF-084 | El feedback podrá indicar fase de conducción, descripción, severidad y confianza. | P1 | Hipótesis de dominio |
| RF-085 | Los campos especializados serán opcionales para permitir una captura rápida. | P0 | Baja fricción |
| RF-086 | El sistema distinguirá quién experimentó el problema y quién registró la información. | P0 | Trazabilidad |
| RF-087 | El Driver podrá consultar su feedback autorizado sin acceder a detalles confidenciales de ingeniería. | P0 | Respaldado |
| RF-088 | La ausencia de feedback no bloqueará el cierre administrativo de una sesión. | P1 | Evitar rigidez |

## 4.11 Observaciones técnicas

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-089 | Engineer y Mechanic podrán registrar observaciones asociadas a una sesión o vehículo según sus permisos. | P0 | Respaldado |
| RF-090 | Una observación podrá relacionarse con feedback, vuelta, sector o zona de pista. | P1 | Flujo contextual |
| RF-091 | Las observaciones podrán clasificarse como conducción, vehículo, neumáticos, mecánica, pista, ambiente u otra. | P1 | Hipótesis de dominio |
| RF-092 | Cada observación tendrá un nivel de visibilidad. | P0 | Respaldado |
| RF-093 | Una observación podrá marcarse como posible incidente o necesidad de inspección. | P1 | Relación operativa |
| RF-094 | Las observaciones conservarán autor y marcas de tiempo. | P0 | Trazabilidad |
| RF-095 | Una observación no se presentará automáticamente como una causa confirmada. | P0 | Honestidad |

## 4.12 Análisis e hipótesis

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-096 | Un Engineer autorizado podrá crear un análisis para una sesión. | P0 | Respaldado |
| RF-097 | El análisis podrá relacionar feedback, vueltas, sectores, condiciones y observaciones. | P0 | Tesis del producto |
| RF-098 | El análisis permitirá registrar dónde se perdió rendimiento. | P1 | Respaldado |
| RF-099 | El análisis permitirá formular una o más hipótesis. | P0 | Flujo principal |
| RF-100 | Cada hipótesis tendrá descripción, clasificación de causa y nivel de confianza. | P0 | Evitar falsa certeza |
| RF-101 | Las clasificaciones iniciales serán técnica del piloto, configuración, mecánica, neumáticos, pista/ambiente y desconocida. | P1 | Hipótesis de dominio |
| RF-102 | El nivel de confianza inicial podrá ser `LOW`, `MEDIUM` o `HIGH`. | P1 | Hipótesis de dominio |
| RF-103 | Una hipótesis podrá terminar como respaldada, parcialmente respaldada, rechazada o no concluyente. | P0 | Aprendizaje |
| RF-104 | RaceOps no convertirá automáticamente correlaciones en causas confirmadas. | P0 | Honestidad |
| RF-105 | Los detalles técnicos del análisis podrán marcarse como `ENGINEERING_CONFIDENTIAL`. | P0 | Respaldado |
| RF-106 | Un Driver podrá recibir una explicación autorizada sin obtener la configuración técnica confidencial. | P0 | Respaldado |
| RF-107 | El análisis conservará autor, fecha y última modificación. | P0 | Trazabilidad |

## 4.13 Prioridades

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-108 | Una sesión podrá generar prioridades para la siguiente sesión. | P0 | Respaldado |
| RF-109 | Las prioridades podrán dirigirse a Driver, Engineer o Mechanic. | P0 | Respaldado |
| RF-110 | El sistema permitirá destacar un máximo de tres prioridades principales por destinatario y sesión objetivo. | P0 | Parcialmente respaldado |
| RF-111 | Las notas adicionales no se presentarán como prioridades principales. | P1 | Claridad |
| RF-112 | Cada prioridad tendrá descripción, destinatario y sesión de origen. Podrá referenciar una sesión objetivo existente o declarar la intención `NEXT_SESSION` hasta que dicha sesión sea creada. | P0 | Trazabilidad |
| RF-113 | Las prioridades respetarán las reglas de visibilidad. | P0 | Confidencialidad |
| RF-114 | Una prioridad deberá ser concreta y accionable; no solamente una copia de métricas. | P1 | Valor del producto |

## 4.14 Acciones

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-115 | Una hipótesis o prioridad podrá producir una acción. | P0 | Flujo principal |
| RF-116 | La acción podrá clasificarse como conducción, ingeniería o mecánica. | P0 | Respaldado |
| RF-117 | La acción podrá asignarse a un usuario o rol responsable. | P0 | Responsabilidad |
| RF-118 | La acción conservará la sesión de origen. Podrá referenciar una sesión objetivo existente o declarar la intención `NEXT_SESSION` hasta que dicha sesión sea creada. | P0 | Trazabilidad |
| RF-119 | Los estados candidatos serán `PROPOSED`, `PLANNED`, `IN_PROGRESS`, `COMPLETED` y `CANCELLED`. | P1 | Hipótesis de dominio |
| RF-120 | Completar una acción no significará automáticamente que produjo una mejora. | P0 | Honestidad |
| RF-121 | Las acciones técnicas podrán tener detalles confidenciales y un resumen visible para el Driver. | P0 | Respaldado |
| RF-122 | Una acción cancelada conservará motivo e historial. | P1 | Trazabilidad |

## 4.15 Resultado y conclusión

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-123 | Una acción podrá evaluarse utilizando una sesión posterior. | P0 | Flujo principal |
| RF-124 | Una evaluación registrada podrá clasificarse como mejora, empeoramiento, sin cambio medible o no concluyente. Mientras no exista evaluación, el sistema mostrará el estado derivado `NOT_EVALUATED` sin crear un resultado ficticio. | P0 | Aprendizaje |
| RF-125 | La evaluación podrá incluir métricas, feedback y observaciones posteriores. | P0 | Evidencia |
| RF-126 | El sistema permitirá registrar una conclusión sin exigir certeza absoluta. | P0 | Honestidad |
| RF-127 | La conclusión podrá actualizar el estado de la hipótesis original. | P0 | Trazabilidad |
| RF-128 | El sistema conservará la relación completa entre observación, hipótesis, acción y resultado. | P0 | Valor central |
| RF-129 | Una acción no podrá marcarse como mejora sin indicar la sesión o evidencia utilizada. | P0 | Integridad |
| RF-130 | Los usuarios sólo podrán consultar conclusiones compatibles con sus permisos. | P0 | Confidencialidad |

## 4.16 Referencias de telemetría

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-131 | Una sesión podrá conservar referencias a archivos o fuentes de telemetría. | P1 | Estrategia complementaria |
| RF-132 | La referencia podrá indicar sistema de origen, nombre, ubicación autorizada y notas. | P1 | Trazabilidad |
| RF-133 | RaceOps no necesitará interpretar el archivo para completar el flujo inicial. | P0 | Control de alcance |
| RF-134 | La importación y normalización de CSV será una función condicionada. | P2 | Evidencia insuficiente |
| RF-135 | RaceOps no realizará ingestión de telemetría en vivo durante v1.0. | P3 | Rechazado para V1 |

## 4.17 Mantenimiento

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-136 | Mechanic y usuarios autorizados podrán registrar mantenimiento para vehículos de su equipo. | P1 | Parcialmente respaldado |
| RF-137 | Cada registro conservará vehículo, tipo, descripción, responsable y fecha. | P1 | Trazabilidad |
| RF-138 | El mantenimiento podrá relacionarse con una sesión, observación, incidente o acción mecánica. | P1 | Valor contextual |
| RF-139 | El registro podrá indicar inspección, mantenimiento preventivo, reparación o reemplazo. | P1 | Hipótesis de dominio |
| RF-140 | Podrán registrarse opcionalmente horas de motor, kilometraje u otra referencia aplicable. | P1 | Flexibilidad |
| RF-141 | El sistema no exigirá métricas que no correspondan a la categoría o vehículo. | P1 | Evitar esquema rígido |
| RF-142 | Un usuario autorizado podrá cambiar un vehículo a `MAINTENANCE` o `UNAVAILABLE`. | P1 | Regla de negocio |
| RF-143 | Un vehículo no disponible no podrá asignarse a sesiones nuevas. | P1 | Regla crítica |
| RF-144 | Completar un registro de mantenimiento no cambiará automáticamente el vehículo a `READY`. | P1 | Seguridad operativa |
| RF-145 | Sólo un usuario autorizado podrá devolver un vehículo al estado `READY`. | P1 | Seguridad operativa |
| RF-146 | Una intervención realizada como consecuencia de una acción conservará la relación causal. | P1 | Valor central |
| RF-147 | Los registros históricos no podrán eliminarse mediante operaciones normales. | P1 | Trazabilidad |
| RF-148 | Una corrección deberá conservar autor, fecha y motivo. | P1 | Auditoría |
| RF-149 | El sistema mostrará el historial cronológico de mantenimiento del vehículo. | P1 | Parcialmente respaldado |
| RF-150 | Los intervalos y alertas automáticas de servicio serán configurables solamente si se validan. | P2 | Evidencia insuficiente |
| RF-151 | La gestión completa de inventario y refacciones queda fuera de v1.0. | P3 | Fuera de alcance |

## 4.18 Historial y memoria operativa

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-152 | Un usuario autorizado podrá consultar historial por pista, evento, sesión, piloto o vehículo. | P0 | Parcialmente respaldado |
| RF-153 | El historial mostrará la información en orden cronológico. | P0 | Usabilidad |
| RF-154 | Será posible recorrer observación, hipótesis, acción, resultado y conclusión. | P0 | Valor central |
| RF-155 | El historial conservará referencias a las sesiones de origen y evaluación. | P0 | Trazabilidad |
| RF-156 | Los filtros respetarán equipo, rol y nivel de visibilidad. | P0 | Seguridad |
| RF-157 | El sistema no revelará mediante búsquedas la existencia de recursos confidenciales no autorizados. | P0 | Seguridad |
| RF-158 | La desactivación de usuarios, pilotos o vehículos no eliminará su historia. | P0 | Integridad |
| RF-159 | Los resultados históricos indicarán cuando existan datos faltantes o no concluyentes. | P0 | Honestidad |
| RF-160 | Las búsquedas y listados históricos serán paginados cuando el volumen lo requiera. | P1 | Rendimiento |

## 4.19 Reportes

| ID | Requerimiento | Prioridad | Fundamento |
|---|---|---:|---|
| RF-161 | Un usuario autorizado podrá consultar un resumen de sesión. | P0 | Flujo principal |
| RF-162 | El resumen podrá incluir contexto, resultados, feedback, hallazgos, prioridades, acciones y conclusiones. | P0 | Valor central |
| RF-163 | Un usuario autorizado podrá consultar un resumen de evento compuesto por sus sesiones. | P1 | Utilidad operativa |
| RF-164 | El contenido del reporte se ajustará al rol y nivel de visibilidad del usuario. | P0 | Confidencialidad |
| RF-165 | Un reporte para Driver no incluirá detalles `ENGINEERING_CONFIDENTIAL`. | P0 | Respaldado |
| RF-166 | Las métricas del reporte deberán derivarse de datos almacenados y reproducibles. | P0 | Integridad |
| RF-167 | El reporte distinguirá información faltante de valores iguales a cero. | P0 | Honestidad |
| RF-168 | El reporte indicará fecha de generación y filtros aplicados. | P1 | Trazabilidad |
| RF-169 | Una vista imprimible será deseable para v1.0. | P1 | Utilidad |
| RF-170 | La exportación PDF avanzada será condicionada y no bloqueará el MVP. | P2 | Control de alcance |

# 5. Requisitos no funcionales

## 5.1 Seguridad

| ID | Requisito |
|---|---|
| RNF-SEC-001 | Las contraseñas se almacenarán mediante un algoritmo de hashing apropiado; nunca en texto plano. |
| RNF-SEC-002 | La autenticación y autorización se validarán en el servidor para cada operación protegida. |
| RNF-SEC-003 | Los tokens tendrán expiración y se firmarán utilizando secretos externos al código fuente. |
| RNF-SEC-004 | El sistema aplicará el principio de menor privilegio. |
| RNF-SEC-005 | Toda consulta de recursos verificará pertenencia al equipo correspondiente. |
| RNF-SEC-006 | Las respuestas de error no revelarán contraseñas, tokens, secretos, consultas SQL ni detalles internos. |
| RNF-SEC-007 | Toda entrada externa deberá validarse antes de utilizarse. |
| RNF-SEC-008 | La configuración CORS utilizará orígenes explícitamente autorizados. |
| RNF-SEC-009 | Los intentos fallidos de autenticación se registrarán sin almacenar credenciales. |
| RNF-SEC-010 | Se evaluará rate limiting para endpoints sensibles como login. |
| RNF-SEC-011 | Los datos `ENGINEERING_CONFIDENTIAL` contarán con pruebas específicas de acceso permitido y denegado. |
| RNF-SEC-012 | Los datos sensibles no se incluirán innecesariamente en logs. |

## 5.2 Integridad y confiabilidad

| ID | Requisito |
|---|---|
| RNF-REL-001 | Las operaciones que modifiquen varios datos relacionados deberán ejecutarse de forma transaccional. |
| RNF-REL-002 | Un error parcial no deberá dejar información en un estado inconsistente. |
| RNF-REL-003 | La base de datos utilizará restricciones para proteger relaciones e invariantes importantes. |
| RNF-REL-004 | El sistema no eliminará en cascada información histórica crítica de forma accidental. |
| RNF-REL-005 | Los errores esperados deberán producir respuestas consistentes y comprensibles. |
| RNF-REL-006 | El fallo de una integración opcional no impedirá utilizar el flujo principal. |
| RNF-REL-007 | Antes de cualquier uso real deberá documentarse una estrategia de respaldo y recuperación. |
| RNF-REL-008 | Las fechas se almacenarán de manera consistente y su zona horaria se tratará explícitamente. |
| RNF-REL-009 | Los datos importados conservarán una referencia suficiente a su procedencia y distinguirán campos publicados, transformados y sintéticos. |

## 5.3 Rendimiento

| ID | Requisito |
|---|---|
| RNF-PER-001 | Las operaciones comunes deberán responder sin retrasos que interrumpan el flujo de trabajo esperado. |
| RNF-PER-002 | Antes de publicar afirmaciones de rendimiento se definirá un escenario reproducible con datos y concurrencia representativos. |
| RNF-PER-003 | Se medirán latencia, throughput, consultas y errores durante la fase de rendimiento. |
| RNF-PER-004 | Los listados potencialmente grandes utilizarán paginación. |
| RNF-PER-005 | Las consultas históricas deberán evitar problemas conocidos como consultas N+1. |
| RNF-PER-006 | No se afirmará que RaceOps soporta determinada cantidad de usuarios hasta medirlo. |

Los objetivos numéricos de latencia y concurrencia se establecerán después
de crear un conjunto de datos representativo. No se inventarán cifras sin
una línea base.

## 5.4 Usabilidad y accesibilidad

| ID | Requisito |
|---|---|
| RNF-USA-001 | La interfaz deberá funcionar en computadora, tablet y teléfono mediante diseño responsive. |
| RNF-USA-002 | El feedback rápido deberá poder guardarse sin completar campos especializados opcionales. |
| RNF-USA-003 | Las asociaciones conocidas deberán completarse automáticamente cuando sea seguro. |
| RNF-USA-004 | Los formularios mostrarán únicamente campos relevantes para la tarea y el rol. |
| RNF-USA-005 | Los mensajes de error explicarán qué debe corregir el usuario sin exponer detalles técnicos. |
| RNF-USA-006 | Los estados no dependerán exclusivamente del color para comunicar su significado. |
| RNF-USA-007 | Los controles interactivos tendrán etiquetas comprensibles y navegación mediante teclado cuando corresponda. |
| RNF-USA-008 | Las acciones destructivas o difíciles de revertir requerirán confirmación. |
| RNF-USA-009 | Las tareas principales se probarán con usuarios antes de declararse fáciles de usar. |
| RNF-USA-010 | El sistema priorizará acciones y conclusiones sobre la presentación de métricas innecesarias. |

## 5.5 Compatibilidad

| ID | Requisito |
|---|---|
| RNF-COM-001 | La aplicación será compatible con versiones modernas de Chrome, Edge y Firefox. |
| RNF-COM-002 | La API intercambiará datos utilizando JSON y convenciones documentadas. |
| RNF-COM-003 | La aplicación no dependerá de una integración externa para iniciar o completar el flujo principal. |
| RNF-COM-004 | Los formatos de fecha, duración y unidades estarán documentados. |

## 5.6 Mantenibilidad

| ID | Requisito |
|---|---|
| RNF-MAN-001 | El backend utilizará una arquitectura de monolito modular. |
| RNF-MAN-002 | Los módulos deberán mantener responsabilidades claras y dependencias controladas. |
| RNF-MAN-003 | El código Python utilizará type hints en las interfaces relevantes. |
| RNF-MAN-004 | Los cambios de base de datos se realizarán mediante migraciones versionadas. |
| RNF-MAN-005 | La lógica de negocio crítica no dependerá directamente de controladores HTTP. |
| RNF-MAN-006 | Los errores y respuestas seguirán un formato consistente. |
| RNF-MAN-007 | Las decisiones arquitectónicas importantes se documentarán mediante ADR. |
| RNF-MAN-008 | Las dependencias se mantendrán declaradas y con versiones controladas. |
| RNF-MAN-009 | No se aplicarán patrones adicionales si no resuelven un problema concreto. |

## 5.7 Pruebas y calidad

| ID | Requisito |
|---|---|
| RNF-QUA-001 | Cada regla de negocio P0 tendrá al menos una prueba automatizada. |
| RNF-QUA-002 | Los controles de autorización tendrán pruebas positivas y negativas. |
| RNF-QUA-003 | Los endpoints principales tendrán pruebas de integración. |
| RNF-QUA-004 | Los casos límite identificados se incorporarán a la suite de regresión. |
| RNF-QUA-005 | El pipeline de CI ejecutará verificaciones automáticas antes de integrar cambios. |
| RNF-QUA-006 | Una funcionalidad no se considerará terminada si sus pruebas críticas fallan. |
| RNF-QUA-007 | Los datos de prueba no contendrán información real sensible sin autorización. |

## 5.8 Observabilidad

| ID | Requisito |
|---|---|
| RNF-OBS-001 | La aplicación generará logs suficientes para diagnosticar errores importantes. |
| RNF-OBS-002 | Los logs incluirán contexto técnico útil sin exponer secretos. |
| RNF-OBS-003 | Los errores inesperados tendrán un identificador que facilite relacionar respuesta y log. |
| RNF-OBS-004 | El sistema ofrecerá un endpoint de salud. |
| RNF-OBS-005 | Las mediciones de rendimiento se conservarán como evidencia y no como afirmaciones sin respaldo. |

## 5.9 Despliegue y configuración

| ID | Requisito |
|---|---|
| RNF-DEP-001 | El sistema podrá ejecutarse mediante Docker y Docker Compose. |
| RNF-DEP-002 | La configuración específica del entorno se obtendrá mediante variables de entorno. |
| RNF-DEP-003 | El repositorio incluirá un archivo de ejemplo sin secretos reales. |
| RNF-DEP-004 | La instalación y ejecución estarán documentadas. |
| RNF-DEP-005 | Las migraciones podrán ejecutarse de manera reproducible. |
| RNF-DEP-006 | La versión demostrada en la feria deberá corresponder a una versión etiquetada del proyecto. |

# 6. Criterios de aceptación críticos preliminares

## 6.1 Aislamiento entre equipos

```gherkin
Scenario: Usuario intenta acceder a otro equipo
  Given un usuario autenticado perteneciente al Team A
  And existe un recurso perteneciente al Team B
  When intenta consultar el recurso
  Then el sistema rechaza la operación
  And no revela información del recurso
```

## 6.2 Confidencialidad de ingeniería

```gherkin
Scenario: Driver intenta consultar información confidencial
  Given un usuario con rol DRIVER
  And existe información ENGINEERING_CONFIDENTIAL
  When intenta consultarla
  Then el sistema rechaza la operación
  And no revela su existencia mediante mensajes o conteos
```

## 6.3 Vehículo no disponible

```gherkin
Scenario: Asignación de vehículo no disponible
  Given un vehículo con estado MAINTENANCE
  When un usuario intenta asignarlo a una sesión nueva
  Then el sistema rechaza la asignación
  And conserva el estado del vehículo
```

## 6.4 Resultados posteriores a la actividad

```gherkin
Scenario: Cargar resultados después de terminar actividad
  Given una sesión con estado COMPLETED
  And sus resultados todavía no están bloqueados
  When un usuario autorizado registra una vuelta válida
  Then el sistema acepta la vuelta
```

```gherkin
Scenario: Resultados bloqueados
  Given una sesión con resultados bloqueados
  When un usuario intenta registrar una vuelta
  Then el sistema rechaza la operación
  And no modifica las estadísticas
```

## 6.5 Validación de resultados

```gherkin
Scenario: Tiempo negativo
  Given una sesión que acepta resultados
  When se intenta registrar una vuelta con tiempo menor o igual a cero
  Then el sistema rechaza la vuelta
  And devuelve un error de validación
```

```gherkin
Scenario: Vuelta no elegible
  Given una sesión con cuatro vueltas
  And una vuelta está marcada como INVALID
  When el sistema calcula la mejor vuelta y el promedio
  Then utiliza únicamente las vueltas elegibles
  And informa cuántas vueltas fueron excluidas
```

## 6.6 Feedback comunicado verbalmente

```gherkin
Scenario: Engineer registra feedback del piloto
  Given una sesión completada
  And un piloto comunica feedback verbalmente
  When un Engineer autorizado registra el feedback
  Then el sistema conserva al piloto como sujeto
  And conserva al Engineer como autor del registro
```

## 6.7 Prioridades principales

```gherkin
Scenario: Máximo de prioridades principales
  Given una sesión objetivo
  And existen tres prioridades principales para el Driver
  When se intenta destacar una cuarta prioridad
  Then el sistema rechaza marcarla como principal
  And permite conservarla como nota secundaria
```

## 6.8 Acción sin resultado

```gherkin
Scenario: Acción completada todavía no evaluada
  Given una acción con estado COMPLETED
  And todavía no existe una sesión posterior evaluada
  Then la acción permanece como no evaluada
  And el sistema no afirma que produjo una mejora
```

## 6.9 Evaluación de una acción

```gherkin
Scenario: Comparación con sesión posterior
  Given una hipótesis y una acción realizadas después de Session 1
  And existe Session 2
  When un Engineer compara los resultados
  Then puede clasificar el efecto observado
  And registrar la evidencia
  And actualizar la conclusión de la hipótesis
```

## 6.10 Mantenimiento originado por observación

```gherkin
Scenario: Observación produce reparación
  Given una observación de vibración asociada a una sesión
  And una investigación encuentra un problema mecánico
  When el Mechanic registra la reparación
  Then el mantenimiento queda relacionado con la observación
  And con el vehículo
  And puede recuperarse desde el historial
```

## 6.11 Disponibilidad después de reparación

```gherkin
Scenario: Reparación completada
  Given un vehículo con estado MAINTENANCE
  When se completa un registro de reparación
  Then el vehículo permanece en MAINTENANCE
  Until un usuario autorizado lo declare READY
```

## 6.12 Reporte adaptado al rol

```gherkin
Scenario: Driver consulta resumen de sesión
  Given una sesión con feedback, resultados y análisis confidencial
  When un Driver consulta su resumen
  Then puede ver resultados y prioridades autorizadas
  But no puede ver la configuración técnica
```

## 6.13 Fallo de integración opcional

```gherkin
Scenario: Servicio meteorológico no disponible
  Given que la integración meteorológica no responde
  When un usuario trabaja con una sesión
  Then puede completar el flujo principal
  And el sistema informa que el clima automático no está disponible
```

# 7. Decisiones preliminares relevantes

- Terminar la actividad en pista no significa bloquear inmediatamente los
  resultados; el equipo podrá cargar información posterior hasta bloquearla.
- RaceOps conservará vueltas inválidas o incompletas sin utilizarlas como si
  fueran datos válidos.
- Las hipótesis expresarán incertidumbre y no se convertirán automáticamente
  en causas confirmadas.
- Completar una acción no significa que produjo una mejora.
- El mantenimiento permanecerá dentro de v1.0, pero RaceOps no será un ERP.
- Completar una reparación no volverá automáticamente disponible al vehículo.
- El historial, las búsquedas y los reportes respetarán la confidencialidad.
- Las integraciones opcionales no impedirán completar el flujo principal.
- No se afirmará escalabilidad, facilidad de uso ni viabilidad comercial sin
  mediciones o pruebas observables.
- Los estados, clasificaciones y campos candidatos se confirmarán durante el
  modelado del dominio.

# 8. Próximo refinamiento

Durante Modelado del dominio deberán:

- definirse entidades, value objects y agregados;
- confirmarse estados y transiciones;
- expresarse invariantes sin depender de la interfaz;
- modelarse ownership, visibilidad y conservación histórica;
- resolverse la estrategia de roles múltiples o rol principal;
- vincular reglas de dominio con los RF y criterios de aceptación;
- mantener como hipótesis las métricas de usabilidad y rendimiento hasta
  obtener mediciones.
