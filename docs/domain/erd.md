# RaceOps — Modelo entidad–relación conceptual

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G3
- **Nivel:** Conceptual; tipos físicos e índices se definirán en arquitectura
- **Cobertura:** P0 con extensión P1 separada

## 2. ERD P0

```mermaid
erDiagram
    TEAM ||--o{ TEAM_MEMBERSHIP : has
    USER ||--o{ TEAM_MEMBERSHIP : joins
    TEAM ||--o{ DRIVER : owns
    USER o|--o| DRIVER : may_link
    TEAM ||--o{ VEHICLE : owns
    TEAM ||--o{ TRACK : owns
    TEAM ||--o{ EVENT : owns
    TRACK ||--o{ EVENT : hosts
    EVENT ||--o{ SESSION : contains
    DRIVER ||--o{ SESSION : drives
    VEHICLE ||--o{ SESSION : assigned_to
    SESSION ||--o{ LAP : records
    LAP ||--o{ SECTOR : contains
    SESSION ||--o| CONDITION_SNAPSHOT : contextualizes
    SESSION ||--o{ DRIVER_FEEDBACK : receives
    DRIVER ||--o{ DRIVER_FEEDBACK : experiences
    USER ||--o{ DRIVER_FEEDBACK : authors
    SESSION o|--o{ OBSERVATION : has
    VEHICLE o|--o{ OBSERVATION : concerns
    USER ||--o{ OBSERVATION : authors
    SESSION ||--o{ SESSION_ANALYSIS : analyzed_by
    USER ||--o{ SESSION_ANALYSIS : authors
    SESSION_ANALYSIS ||--o{ HYPOTHESIS : proposes
    SESSION ||--o{ PRIORITY : originates
    SESSION o|--o{ PRIORITY : targets
    HYPOTHESIS o|--o{ PRIORITY : motivates
    SESSION ||--o{ ACTION : originates
    SESSION o|--o{ ACTION : targets
    HYPOTHESIS o|--o{ ACTION : motivates
    PRIORITY o|--o{ ACTION : produces
    USER o|--o{ ACTION : assigned_to
    ACTION ||--o{ ACTION_OUTCOME : evaluated_by
    SESSION ||--o{ ACTION_OUTCOME : supplies_evidence
    USER ||--o{ ACTION_OUTCOME : authors

    TEAM {
        uuid team_id PK
        string name
        string status
    }

    USER {
        uuid user_id PK
        string email
        string password_hash
        string status
        datetime created_at
    }

    TEAM_MEMBERSHIP {
        uuid membership_id PK
        uuid team_id FK
        uuid user_id FK
        string primary_role
        string status
    }

    DRIVER {
        uuid driver_id PK
        uuid team_id FK
        uuid user_id FK_nullable
        string display_name
        boolean is_active
    }

    VEHICLE {
        uuid vehicle_id PK
        uuid team_id FK
        string identifier
        string status
    }

    TRACK {
        uuid track_id PK
        uuid team_id FK
        string name
        string location_nullable
    }

    EVENT {
        uuid event_id PK
        uuid team_id FK
        uuid track_id FK
        string name
        date starts_on
        date ends_on_nullable
        string status
    }

    SESSION {
        uuid session_id PK
        uuid team_id FK
        uuid event_id FK
        uuid driver_id FK
        uuid vehicle_id FK
        string session_type
        datetime scheduled_at
        datetime started_at_nullable
        datetime ended_at_nullable
        string status
        string results_status
        uuid results_locked_by_user_id_nullable FK
        datetime results_locked_at_nullable
    }

    LAP {
        uuid lap_id PK
        uuid team_id FK
        uuid session_id FK
        int lap_number
        bigint duration_internal
        string source
        boolean is_eligible
    }

    SECTOR {
        uuid sector_id PK
        uuid team_id FK
        uuid lap_id FK
        int sector_order
        bigint duration_internal
        string validity
    }

    CONDITION_SNAPSHOT {
        uuid condition_id PK
        uuid team_id FK
        uuid session_id FK
        decimal ambient_temperature_nullable
        string ambient_temperature_unit_nullable
        decimal track_temperature_nullable
        string track_temperature_unit_nullable
        string weather_nullable
        string track_condition_nullable
        string source_nullable
    }

    DRIVER_FEEDBACK {
        uuid feedback_id PK
        uuid team_id FK
        uuid session_id FK
        uuid driver_id FK
        uuid author_user_id FK
        string description
        string corner_or_zone_nullable
        string driving_phase_nullable
        string severity_nullable
        string confidence_nullable
        string visibility_level
        datetime created_at
    }

    OBSERVATION {
        uuid observation_id PK
        uuid team_id FK
        uuid session_id FK_nullable
        uuid vehicle_id FK_nullable
        uuid author_user_id FK
        string description
        string category_nullable
        string visibility_level
        datetime created_at
    }

    SESSION_ANALYSIS {
        uuid analysis_id PK
        uuid team_id FK
        uuid session_id FK
        uuid author_user_id FK
        string authorized_summary_nullable
        string technical_detail
        string visibility_level
        datetime created_at
        datetime updated_at
    }

    HYPOTHESIS {
        uuid hypothesis_id PK
        uuid team_id FK
        uuid analysis_id FK
        string description
        string cause_classification
        string confidence
        string status
        string visibility_level
    }

    PRIORITY {
        uuid priority_id PK
        uuid team_id FK
        uuid source_session_id FK
        uuid target_session_id FK_nullable
        uuid hypothesis_id FK_nullable
        string target_intent
        string recipient_role
        uuid recipient_user_id_nullable
        string description
        boolean is_main
        int rank_nullable
        string visibility_level
    }

    ACTION {
        uuid action_id PK
        uuid team_id FK
        uuid source_session_id FK
        uuid target_session_id FK_nullable
        uuid hypothesis_id FK_nullable
        uuid priority_id FK_nullable
        uuid assignee_user_id FK_nullable
        string assignee_role
        string target_intent
        string action_type
        string status
        string public_summary_nullable
        string confidential_detail_nullable
        string visibility_level
    }

    ACTION_OUTCOME {
        uuid outcome_id PK
        uuid team_id FK
        uuid action_id FK
        uuid evaluation_session_id FK
        uuid author_user_id FK
        string classification
        string conclusion
        datetime created_at
    }
```

## 3. Extensión P1

```mermaid
erDiagram
    TEAM ||--o{ TELEMETRY_REFERENCE : owns
    SESSION ||--o{ TELEMETRY_REFERENCE : references
    TEAM ||--o{ MAINTENANCE_RECORD : owns
    VEHICLE ||--o{ MAINTENANCE_RECORD : receives
    SESSION o|--o{ MAINTENANCE_RECORD : may_origin
    OBSERVATION o|--o{ MAINTENANCE_RECORD : may_origin
    ACTION o|--o{ MAINTENANCE_RECORD : may_origin
    USER ||--o{ MAINTENANCE_RECORD : responsible

    TELEMETRY_REFERENCE {
        uuid telemetry_reference_id PK
        uuid team_id FK
        uuid session_id FK
        string source_system
        string display_name
        string authorized_location
        string notes_nullable
    }

    MAINTENANCE_RECORD {
        uuid maintenance_id PK
        uuid team_id FK
        uuid vehicle_id FK
        uuid responsible_user_id FK
        uuid session_id FK_nullable
        uuid observation_id FK_nullable
        uuid action_id FK_nullable
        string maintenance_type
        string description
        datetime performed_at
        string visibility_level
    }
```

## 4. Restricciones conceptuales

1. Todas las FK entre recursos operativos deben conservar el mismo
   `team_id`.
2. `(session_id, lap_number)` es único.
3. `(lap_id, sector_order)` es único.
4. `ConditionSnapshot.session_id` es único en P0.
5. `duration_internal > 0` para Lap y Sector.
6. `ROLE_RESTRICTED` exige al menos un rol autorizado, aunque su forma de
   persistencia se decidirá en arquitectura.
7. Una Observation debe relacionarse al menos con Session o Vehicle.
8. Un Outcome necesita Action y evaluation Session del mismo Team.
9. `IMPROVED` requiere referencia a evidencia posterior.
10. La combinación usada para limitar Main Priorities debe poder aplicarse
    transaccionalmente.

## 5. Decisiones pendientes de persistencia

- almacenamiento exacto de roles permitidos por registro;
- unidad interna de Duration;
- normalización de MeasuredValue;
- auditoría como tablas propias o columnas selectivas;
- estrategia para impedir futuras FK cruzadas entre Team. Session ya utiliza
  claves compuestas para Event, Driver y Vehicle; cada módulo posterior deberá
  elegir la misma protección o justificar otra equivalente.

Estas decisiones pertenecen principalmente a Fase 4 y no cambian el modelo
conceptual.

