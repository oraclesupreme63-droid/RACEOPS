# RaceOps — Evaluación Gate G4: Architecture Ready

## 1. Información del documento

- **Gate:** G4 — Architecture Ready
- **Versión:** 0.1
- **Estado:** Aprobado condicionalmente
- **Fecha de evaluación:** 22 de octubre de 2026
- **Fase evaluada:** Fase 4 — Diseño de arquitectura

## 2. Condición del gate

El roadmap permite aprobar G4 cuando:

- módulos y dependencias están definidos;
- existe estrategia de configuración, errores y pruebas;
- las decisiones técnicas importantes están justificadas.

La aprobación de este gate autoriza iniciar programación en Fase 5.

## 3. Resultado del diseño

| Elemento | Resultado |
|---|---:|
| Estilo de arquitectura | Monolito modular |
| Módulos P0 definidos | 6 más audit |
| Módulos P1 aislados | 2 |
| Estrategias técnicas | 7 |
| Guías estructurales/API | 4 |
| ADR propuestos | 10 |
| RNF con dirección arquitectónica | 67 de 67 |

## 4. Comprobación de entregables

| Entregable | Ubicación | Resultado |
|---|---|---|
| Architecture Diagram | `architecture-diagram.md` | Cumplido |
| Module Boundaries | `module-boundaries.md` | Cumplido |
| Project Structure | `project-structure.md` | Cumplido |
| API Guidelines | `api-guidelines.md` | Cumplido |
| Data Strategy | `data-strategy.md` | Cumplido |
| Error Strategy | `error-strategy.md` | Cumplido |
| Logging Strategy | `logging-strategy.md` | Cumplido |
| Testing Strategy | `testing-strategy.md` | Cumplido |
| Security Strategy | `security-strategy.md` | Cumplido |
| Configuration/Deployment | `configuration-deployment.md` | Cumplido |
| NFR Mapping | `nfr-mapping.md` | Cumplido |
| ADR iniciales | `docs/decisions/ADR-001` a `ADR-010` | Cumplido |

## 5. Verificaciones realizadas

- El flujo P0 cabe en una sola aplicación y transacción local.
- Los módulos tienen ownership de tablas y no forman ciclos.
- El acceso a datos no mezcla modelos síncronos y asíncronos.
- Las reglas de dominio no dependen de FastAPI.
- Ownership y Visibility se aplican antes de serializar, contar o paginar.
- Los errores de dominio tienen traducción HTTP estable y segura.
- Logs y auditoría tienen propósitos diferentes.
- Las pruebas incluyen dominio, PostgreSQL, API, aceptación, seguridad y
  concurrencia.
- Los 67 RNF tienen una dirección sin declararse falsamente implementados.
- No se añadieron servicios externos, telemetría en vivo ni patrones sin
  evidencia.

## 6. Decisiones que se aprobarían con G4

1. Usar un monolito modular FastAPI con una base PostgreSQL.
2. Usar SQLAlchemy 2.x síncrono y Psycopg 3; endpoints DB serán `def`.
3. Mantener una Session por petición/caso de uso y transacciones cortas.
4. Exponer REST JSON bajo `/api/v1` y RFC 9457 para errores.
5. Representar duraciones como enteros en microsegundos.
6. Usar JWT breve, Argon2id y verificación server-side de Membership/Role.
7. Mantener el token del cliente P0 en memoria, sin refresh token.
8. Aplicar RBAC, Team ownership y Visibility en consultas y respuestas.
9. Registrar auditoría selectiva sin event sourcing.
10. No crear un GenericRepository.
11. Mantener telemetría/CSV fuera de P0.
12. Construir backend-first y elegir el frontend después sin bloquear Fase 5.
13. Usar PostgreSQL real en pruebas de integración.
14. Limitar Docker Compose inicial a API y DB.

## 7. Riesgos y decisiones diferidas

- El frontend exacto permanece diferido hasta disponer de API y wireframes.
- La persistencia de login más allá de una recarga necesita validación de UX;
  P0 favorece seguridad y simplicidad.
- Los defaults de Visibility continúan sujetos a entrevistas con Managers,
  Engineers y Mechanics.
- El mecanismo exacto de locking se elegirá por aggregate al implementarlo.
- Objetivos numéricos de rendimiento requieren dataset y escenario medidos.
- Rate limiting, backups, TLS y retención deben estar operativos antes de
  exposición pública o datos reales.
- La carpeta actual aún no es un repositorio Git; Fase 5 debe inicializarlo o
  confirmar dónde se gestionará el control de versiones.

## 8. Recomendación

**Resultado recomendado: APROBACIÓN CONDICIONAL.**

La arquitectura es suficientemente concreta para iniciar la Fase 5 —
Fundación técnica, bajo estas condiciones:

1. La implementación respeta los ADR aceptados y actualiza el ADR si una
   decisión cambia.
2. Se comienza sólo por la fundación: configuración, API, DB, migraciones,
   logging, errores, tests, Docker y health.
3. No se implementan todavía módulos P1 ni el flujo vertical completo.
4. Seguridad y pruebas se incorporan desde el inicio, no al final.
5. Nueva evidencia puede cambiar requisitos mediante trazabilidad.

## 9. Opciones de decisión

### Opción A — Aprobar G4 condicionalmente

Aceptar ADR-001 a ADR-010, cerrar Fase 4 e iniciar programación de Fase 5.

### Opción B — Mantener G4 abierto

Refinar una o más decisiones antes de crear el proyecto ejecutable.

### Opción C — Rechazar la arquitectura

Replantear estilo, stack o límites antes de programar.

## 10. Decisión registrada

- **Opción seleccionada:** Opción A — Aprobar G4 condicionalmente.
- **Fecha de decisión:** 22 de octubre de 2026.
- **Decisión del propietario:** Cerrar Fase 4 e iniciar la programación de
  Fase 5 — Fundación técnica.
- **Condiciones:** Aceptadas según la sección 8.

## 11. Resultado del gate

**G4 — ARCHITECTURE READY: APROBADO CONDICIONALMENTE.**

La programación puede comenzar de manera incremental por la fundación
técnica. Cada bloque será presentado al propietario para revisión antes de
continuar con el siguiente.

