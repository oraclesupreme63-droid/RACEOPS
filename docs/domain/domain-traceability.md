# RaceOps — Trazabilidad del dominio

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G3
- **Objetivo:** Conectar requisitos P0 con entidades, estados, reglas e invariantes

## 2. Matriz

| Área | Requisitos P0 | Entidades / VO | Reglas | Invariantes | Estado |
|---|---|---|---|---|---|
| Identidad y acceso | RF-001–RF-008 | Team, User, TeamMembership, Visibility | BR-001–BR-008 | INV-001–INV-006, INV-040–INV-045 | User/Membership |
| Pilotos | RF-013–RF-017 | Driver, User | BR-008–BR-010, BR-012 | INV-005–INV-007 | Driver |
| Vehículos | RF-018–RF-021 | Vehicle, Vehicle Status | BR-011, BR-012 | INV-008 | Vehicle |
| Pistas y eventos | RF-024, RF-026, RF-027, RF-029 | Track, Event | BR-002, BR-013 | INV-002, INV-010 | No requiere ciclo P0 adicional |
| Sesiones | RF-031–RF-037, RF-040–RF-042 | Session, SessionAssignment, ActorStamp | BR-014–BR-022 | INV-009–INV-016 | Session y Results |
| Vueltas | RF-045–RF-047, RF-050, RF-051 | Lap, Duration | BR-023, BR-024, BR-027 | INV-016–INV-018, INV-021 | Elegibilidad, no ciclo propio |
| Sectores | RF-055–RF-058 | Sector, Duration | BR-024–BR-026 | INV-019, INV-020 | No ciclo propio |
| Métricas | RF-063, RF-064, RF-066, RF-068, RF-069 | Proyección de Session Results | BR-027–BR-030 | INV-021, INV-022, INV-050 | Derivado |
| Condiciones | RF-070, RF-072, RF-073, RF-076, RF-078 | ConditionSnapshot, MeasuredValue | BR-031, BR-032 | INV-023, INV-048 | Snapshot |
| Feedback | RF-079–RF-082, RF-085–RF-087 | DriverFeedback, Visibility, ActorStamp | BR-033–BR-035 | INV-024, INV-025, INV-042 | Registro histórico |
| Observaciones | RF-089, RF-092, RF-094, RF-095 | Observation, Visibility | BR-036, BR-037 | INV-026, INV-029 | Registro histórico |
| Análisis e hipótesis | RF-096, RF-097, RF-099, RF-100, RF-103–RF-107 | SessionAnalysis, Hypothesis, Confidence | BR-038–BR-042 | INV-027–INV-029, INV-040–INV-045 | Hypothesis |
| Prioridades | RF-108–RF-110, RF-112, RF-113 | Priority, Visibility | BR-043–BR-045 | INV-030–INV-032 | Principal/no principal |
| Acciones | RF-115–RF-118, RF-120, RF-121 | Action, ActorStamp, Visibility | BR-045–BR-048 | INV-032–INV-035 | Action |
| Resultados | RF-123–RF-130 | ActionOutcome, Conclusion | BR-049–BR-052 | INV-036–INV-039 | Outcome + Hypothesis |
| Límite de telemetría | RF-133 | TelemetryReference P1 | El flujo P0 no interpreta archivos | Independencia de integraciones | No aplica |
| Historial | RF-152–RF-159 | Proyecciones filtradas | BR-052–BR-056 | INV-039, INV-044–INV-050 | Derivado |
| Reportes | RF-161, RF-162, RF-164–RF-167 | Authorized Summary | BR-053–BR-056 | INV-042–INV-045, INV-048, INV-050 | Derivado |

## 3. Cobertura de decisiones críticas

| Decisión | Representación de dominio |
|---|---|
| Finalizar Session no bloquea resultados | Dos máquinas de estado separadas |
| Driver y User no son equivalentes | Entidades separadas con vínculo opcional |
| Observación no es causa | Observation e Hypothesis separadas |
| Completar no significa mejorar | Action y ActionOutcome separados |
| Sin datos no es cero | Null/ausencia y MeasuredValue explícitos |
| Próxima Session puede no existir | `target_intent = NEXT_SESSION` y FK opcional |
| Centralizar no significa visibilidad universal | Visibility Model y Authorized Summary |
| Mantener historia sin event sourcing | FK, estados, archivo y auditoría selectiva |

## 4. Regla de cambio

Si una entidad, estado o invariante cambia, deben revisarse:

- requisitos relacionados;
- criterios de aceptación;
- matriz de permisos;
- ERD;
- migraciones futuras;
- pruebas afectadas;
- ADR cuando la decisión sea arquitectónicamente significativa.

