# RaceOps — Paquete de arquitectura

## Estado

Preparado para evaluación del Gate G4 — Architecture Ready.

## Documentos

| Documento | Propósito |
|---|---|
| [`architecture-diagram.md`](architecture-diagram.md) | Contexto, componentes y flujo de petición |
| [`module-boundaries.md`](module-boundaries.md) | Responsabilidad, ownership y dependencias de módulos |
| [`project-structure.md`](project-structure.md) | Layout de código y responsabilidades por capa |
| [`api-guidelines.md`](api-guidelines.md) | Contrato HTTP, formatos, comandos y paginación |
| [`data-strategy.md`](data-strategy.md) | Persistencia, transacciones, tipos y migraciones |
| [`error-strategy.md`](error-strategy.md) | Taxonomía y contrato RFC 9457 |
| [`logging-strategy.md`](logging-strategy.md) | Logs seguros y auditoría selectiva |
| [`testing-strategy.md`](testing-strategy.md) | Capas, escenarios y pipeline de pruebas |
| [`security-strategy.md`](security-strategy.md) | Autenticación, autorización y amenazas |
| [`configuration-deployment.md`](configuration-deployment.md) | Entornos, Docker, health y despliegue |
| [`nfr-mapping.md`](nfr-mapping.md) | Dirección arquitectónica de los 67 RNF |
| [`gate-g4-assessment.md`](gate-g4-assessment.md) | Evaluación de salida de Fase 4 |

Los ADR se encuentran en [`../decisions/`](../decisions/README.md).

## Resumen de la solución

```text
Cliente web ligero
        ↓ HTTPS / JSON
FastAPI REST /api/v1
        ↓
Casos de uso + políticas de dominio
        ↓
SQLAlchemy 2.x síncrono
        ↓
PostgreSQL
```

## Decisiones centrales

- Monolito modular, no microservicios.
- Backend-first, sin adelantar una tecnología de frontend.
- PostgreSQL y SQLAlchemy síncrono; una Session por petición/caso de uso.
- REST versionado y errores RFC 9457.
- JWT breve, Argon2id, RBAC, Team ownership y Visibility server-side.
- Respuestas autorizadas antes de serializar.
- Auditoría selectiva, no event sourcing.
- Sin repository genérico, Redis, workers o telemetría en vivo en P0.
- Pruebas de integración contra PostgreSQL real.
- Docker Compose mínimo: API y DB.

