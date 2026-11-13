# RaceOps — Invariantes del dominio

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G3
- **Propósito:** Declarar condiciones que nunca deben romperse

## 2. Ownership e identidad

| ID | Invariante | Protección esperada |
|---|---|---|
| INV-001 | Todo recurso operativo tiene `team_id` no nulo | Modelo y base de datos |
| INV-002 | Ninguna relación operativa cruza Teams | Dominio, aplicación y constraints cuando sea posible |
| INV-003 | TeamMembership activa referencia User y Team activos | Servicio de aplicación y FK |
| INV-004 | Cada TeamMembership tiene un rol principal y el par User/Team es único | Dominio y DB |
| INV-005 | Driver vinculado con User comparte Team | Dominio |
| INV-006 | Desactivación no elimina autoría histórica | Dominio y política de borrado |

## 3. Base operativa y Session

| ID | Invariante | Protección esperada |
|---|---|---|
| INV-007 | Driver asignado estaba activo al crear o cambiar asignación | Dominio |
| INV-008 | Vehicle asignado estaba `READY` al crear o cambiar asignación | Dominio |
| INV-009 | Event, Driver, Vehicle y Session comparten Team | Dominio y transacción |
| INV-010 | Event siempre tiene Track del mismo Team | Dominio y DB |
| INV-011 | Session nueva inicia `PLANNED` y resultados `OPEN` | Constructor de dominio |
| INV-012 | Session Status sólo usa transiciones permitidas | Aggregate Session |
| INV-013 | `started_at` existe si Session inició actividad | Aggregate Session |
| INV-014 | `ended_at` existe en `COMPLETED` o `CANCELLED` | Aggregate Session |
| INV-015 | Results `LOCKED` conserva actor y momento | Aggregate Session |

## 4. Resultados

| ID | Invariante | Protección esperada |
|---|---|---|
| INV-016 | No se agregan Laps/Sectors normalmente con Results `LOCKED` | Servicio de aplicación y dominio |
| INV-017 | Lap number es positivo y único por Session | Value validation y unique constraint |
| INV-018 | Lap Duration es positiva | Value Object y check constraint |
| INV-019 | Sector order es positivo y único por Lap | Value validation y unique constraint |
| INV-020 | Sector Duration es positiva | Value Object y check constraint |
| INV-021 | Sólo Laps elegibles forman métricas principales | Servicio de dominio y pruebas |
| INV-022 | Sin Laps elegibles no existe mejor vuelta ni promedio válido | Servicio de dominio |

## 5. Contexto y razonamiento

| ID | Invariante | Protección esperada |
|---|---|---|
| INV-023 | MeasuredValue presente tiene unidad | Value Object |
| INV-024 | Driver Feedback conserva Driver y author User | Dominio y DB |
| INV-025 | Driver autor sólo registra feedback de su Driver vinculado y Session asignada | Autorización y dominio |
| INV-026 | Observation referencia Session o Vehicle como mínimo | Dominio y check constraint |
| INV-027 | Hypothesis nueva inicia `PROPOSED` | Constructor de dominio |
| INV-028 | Hypothesis tiene causa y Confidence válidas | Value validation |
| INV-029 | Observation no cambia automáticamente Hypothesis | Separación de aggregates |

## 6. Decisiones y aprendizaje

| ID | Invariante | Protección esperada |
|---|---|---|
| INV-030 | Máximo tres Main Priorities por alcance objetivo | Transacción y constraint/lock apropiado |
| INV-031 | Rank de Main Priority está entre 1 y 3 y es único en su alcance | Dominio y DB |
| INV-032 | Priority/Action sin target Session declara `NEXT_SESSION` | Dominio |
| INV-033 | Action tiene Source Session y motivación | Dominio |
| INV-034 | Assignee User, si existe, pertenece al mismo Team | Dominio |
| INV-035 | Action `COMPLETED` no implica Outcome `IMPROVED` | Modelo separado |
| INV-036 | Action Outcome referencia Action y evaluation Session del mismo Team | Dominio y DB |
| INV-037 | Outcome `IMPROVED` identifica evidencia posterior | Dominio |
| INV-038 | Outcome no existe antes de vincular target/evaluation Session | Dominio |
| INV-039 | La cadena histórica no queda con referencias colgantes | FK y política de borrado |

## 7. Visibilidad

| ID | Invariante | Protección esperada |
|---|---|---|
| INV-040 | Visibility usa un nivel permitido | Value Object |
| INV-041 | `ROLE_RESTRICTED` tiene al menos un Role permitido | Value Object |
| INV-042 | Driver nunca recibe `ENGINEERING_CONFIDENTIAL` | Política y pruebas negativas |
| INV-043 | Administrator/Team Manager no lo recibe sólo por jerarquía | Política y pruebas negativas |
| INV-044 | Listados y conteos se calculan después del filtrado autorizado | Query layer |
| INV-045 | Una respuesta no serializa campos prohibidos | DTO/presenter y pruebas |

## 8. Historial y borrado

| ID | Invariante | Protección esperada |
|---|---|---|
| INV-046 | Recursos referenciados históricamente no se borran por operaciones normales | Política de archivo y FK |
| INV-047 | Una corrección sensible conserva actor, instante y motivo | Auditoría selectiva |
| INV-048 | Dato ausente no se transforma en cero | Tipos nullable y presentación |
| INV-049 | Fechas persistidas usan UTC | Infraestructura y pruebas |
| INV-050 | Métricas pueden reproducirse desde datos canónicos | Servicio de dominio y pruebas |

## 9. Mantenimiento

| ID | Invariante | Protección esperada |
|---|---|---|
| INV-051 | Maintenance Record, Vehicle, usuarios y contexto pertenecen al mismo Team | FKs compuestas y servicio |
| INV-052 | Maintenance Record nuevo inicia `OPEN` y `ROLE_RESTRICTED` | Modelo y DB |
| INV-053 | Estado terminal exige conclusión o motivo y timestamp coherentes | Dominio y checks DB |
| INV-054 | Completar intervención no cambia Vehicle a `READY` | Separación de servicios |
| INV-055 | Una relación causal opcional nunca se inventa | Servicio y campos nullable |

## 10. Estrategia de protección

Cada invariante deberá asignarse durante arquitectura a una o más capas:

- constructor o método del Aggregate;
- Value Object;
- servicio de dominio;
- servicio de aplicación;
- restricción de base de datos;
- política de autorización;
- DTO o serializer;
- prueba automatizada.

No se confiará exclusivamente en validaciones del frontend.

