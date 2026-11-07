# RaceOps — Arquitectura general

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G4
- **Estilo:** Monolito modular, API-first, backend-first

## 2. Vista de contexto

```mermaid
flowchart LR
    U[Usuarios por rol] -->|HTTPS| W[Cliente web ligero]
    W -->|JSON / REST| API[FastAPI /api/v1]
    API --> APP[Casos de uso y políticas]
    APP --> DOM[Reglas e invariantes]
    APP --> ORM[SQLAlchemy 2.x]
    ORM --> DB[(PostgreSQL)]
    MIG[Alembic] --> DB
    API --> OBS[Logs estructurados y health]
    TEST[Pytest + HTTPX/TestClient] --> API
```

El cliente web no contiene reglas de autorización confiables. Toda decisión
de seguridad se repite en el servidor.

## 3. Vista interna

```mermaid
flowchart TB
    HTTP[HTTP Request]
    MID[Middleware: request ID, logging, CORS]
    ROUTER[Router + Pydantic schemas]
    AUTH[Authentication + authorization dependencies]
    SERVICE[Application service / use case]
    POLICY[Domain policies and invariants]
    DATA[Explicit queries / repositories where useful]
    SA[SQLAlchemy Session]
    PG[(PostgreSQL)]
    VIEW[Role-aware response schema]
    ERR[RFC 9457 error mapper]

    HTTP --> MID --> ROUTER
    ROUTER --> AUTH
    AUTH --> SERVICE
    SERVICE --> POLICY
    SERVICE --> DATA --> SA --> PG
    SERVICE --> VIEW --> MID
    ROUTER -. exception .-> ERR --> MID
```

## 4. Flujo de escritura

1. Middleware asigna `request_id`.
2. El router valida sintaxis con Pydantic.
3. Autenticación resuelve User, TeamMembership y Role.
4. El servicio de aplicación carga recursos dentro del Team.
5. Las políticas verifican permisos, estado e invariantes.
6. La operación completa ocurre dentro de una transacción corta.
7. SQLAlchemy hace flush y PostgreSQL protege constraints.
8. El servicio confirma o revierte la transacción.
9. Un schema de salida autorizado filtra campos.
10. El log registra resultado sin contenido sensible.

## 5. Flujo de lectura

1. Se autentica y determina Team.
2. La consulta incluye ownership y restricciones de visibilidad.
3. El filtrado ocurre antes de conteo y paginación.
4. La proyección recupera sólo campos necesarios.
5. El schema de salida aplica la última defensa por campo.

## 6. Despliegue inicial

```mermaid
flowchart LR
    B[Browser] -->|HTTP dev / HTTPS deployed| A[RaceOps API]
    A --> P[(PostgreSQL)]
    A --> L[stdout structured logs]
```

En desarrollo, API y PostgreSQL se ejecutarán mediante Docker Compose. No
se agregan Redis, broker, workers, microservicios ni Kubernetes sin una
necesidad observada.

## 7. Referencias técnicas oficiales

- [FastAPI — Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [SQLAlchemy — Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Alembic — Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [RFC 9457 — Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html)

