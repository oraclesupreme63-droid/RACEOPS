# Roadmap del proyecto — RaceOps

## 1. Información del documento

- **Proyecto:** RaceOps
- **Versión:** 1.3
- **Estado:** Aprobado
- **Enfoque:** Research-driven development
- **Fecha objetivo:** Pendiente de publicación oficial
- **Fecha:** Por definir

## 2. Propósito

Este roadmap establece el orden de trabajo de RaceOps desde Product
Discovery hasta una posible evolución comercial.

Las fases se organizan mediante hitos y criterios de salida, no mediante
fechas ficticias. El calendario se añadirá cuando sea publicada la fecha
oficial de la feria.

## 3. Principios de ejecución

- Validar antes de expandir.
- Construir un flujo vertical antes que múltiples módulos incompletos.
- Mantener investigación, pruebas y documentación durante todo el proyecto.
- No comenzar funciones P2 mientras existan funciones P0 incompletas.
- No reemplazar herramientas profesionales de telemetría.
- Mantener una captura rápida y de baja fricción.
- Conservar evidencia, incertidumbre y confidencialidad.
- No afirmar adopción, rendimiento o valor comercial sin mediciones.

# 4. Roadmap por fases

## Fase 0 — Definición del proyecto

**Objetivo:** convertir la idea en una propuesta formal, limitada y
verificable.

**Entregables:**

- Project Charter;
- Product Vision;
- Problem Statement;
- Scope;
- Objectives;
- EDT / WBS;
- Preliminary Requirements;
- Risk Register;
- Roadmap.

**Criterio de salida:**

- todos los documentos existen;
- el alcance distingue P0–P3;
- las hipótesis están identificadas;
- se conoce qué no pertenece a v1.0.

**Estado:** Completada.

---

## Fase 1 — Investigación y validación

**Objetivo:** determinar si el problema ocurre realmente y bajo qué
condiciones.

**Actividades:**

- documentar INT-001, INT-002 e INT-003;
- continuar entrevistas con pilotos, ingenieros, mecánicos y managers;
- analizar herramientas actuales;
- registrar evidencia y contraevidencia;
- observar flujos reales cuando sea posible;
- probar la guía de validación;
- actualizar hipótesis.

**Entregables:**

- Research Plan;
- Interview Records;
- Competitor Analysis;
- Evidence Matrix;
- Assumptions Register;
- Validated Problems;
- Updated Problem Statement.

**Criterio de salida mínimo:**

- las entrevistas existentes están documentadas;
- evidencia y opinión están separadas;
- existe suficiente claridad para priorizar el primer flujo;
- las dudas pendientes están explícitas.

La investigación continuará durante el desarrollo.

**Estado:** Completada condicionalmente mediante Gate G1 el 22 de octubre
de 2026. La investigación continúa como actividad transversal.

---

## Fase 2 — Ingeniería de requerimientos

**Objetivo:** convertir los requerimientos preliminares en especificaciones
verificables.

**Actividades:**

- definir actores;
- crear matriz de roles y permisos;
- redactar casos de uso;
- crear historias de usuario;
- completar criterios de aceptación P0;
- priorizar backlog;
- crear matriz de trazabilidad;
- definir Definition of Ready y Definition of Done.

**Entregables:**

- Functional Requirements;
- Non-Functional Requirements;
- Use Cases;
- Permission Matrix;
- Acceptance Criteria;
- Prioritized Backlog;
- Traceability Matrix.

**Criterio de salida:**

- cada función P0 tiene actor, regla y criterio de aceptación;
- las responsabilidades de los roles están claras;
- los elementos condicionados no bloquean el MVP.

**Estado:** Completada condicionalmente mediante Gate G2 el 22 de octubre
de 2026.

---

## Fase 3 — Modelado del dominio

**Objetivo:** representar correctamente las operaciones y el aprendizaje
entre sesiones.

**Elementos principales:**

- Team;
- User;
- Driver;
- Vehicle;
- Track;
- Event;
- Session;
- Lap;
- Sector;
- SessionCondition;
- DriverFeedback;
- Observation;
- Analysis;
- Hypothesis;
- Priority;
- Action;
- ActionOutcome;
- MaintenanceRecord;
- TelemetryReference.

**Entregables:**

- Ubiquitous Language;
- Domain Model;
- ERD;
- State Diagrams;
- Business Rules;
- Invariants;
- Visibility Model.

**Criterio de salida:**

- las entidades y relaciones soportan el flujo vertical;
- los estados tienen transiciones válidas;
- la historia no se destruye;
- las reglas de confidencialidad pueden implementarse.

**Estado:** Completada condicionalmente mediante Gate G3 el 22 de octubre
de 2026.

---

## Fase 4 — Diseño de arquitectura

**Objetivo:** definir cómo construir RaceOps sin sobreingeniería.

**Decisiones iniciales:**

```text
Frontend
   ↓
REST API / FastAPI
   ↓
Business Logic
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

**Enfoque:** monolito modular.

**Entregables:**

- Architecture Diagram;
- Module Boundaries;
- Project Structure;
- API Guidelines;
- Error Strategy;
- Logging Strategy;
- Testing Strategy;
- Security Strategy;
- ADR iniciales.

**Criterio de salida:**

- los módulos y dependencias están definidos;
- existe una estrategia para configuración, errores y pruebas;
- las decisiones técnicas importantes están justificadas.

**Hito:** después de aprobar esta fase comienza la programación.

**Estado:** Completada condicionalmente mediante Gate G4 el 22 de octubre
de 2026.

---

## Fase 5 — Fundación técnica

**Objetivo:** crear una base ejecutable y comprobable.

**Estado:** completada el 7 de noviembre de 2026. Gate G5 aprobado con una
ejecución real de los jobs de calidad y contenedores en GitHub Actions.

**Incluye:**

- Python y FastAPI;
- configuración por entorno;
- PostgreSQL;
- SQLAlchemy;
- Alembic;
- logging;
- errores base;
- Pytest;
- Docker Compose;
- integración continua;
- `GET /health`.

**Entregable:** `v0.1 — Foundation`.

**Criterio de salida:**

- la aplicación inicia mediante instrucciones documentadas;
- PostgreSQL y migraciones funcionan;
- `/health` responde;
- las pruebas se ejecutan en CI.

---

## Fase 6 — Identidad y autorización

**Objetivo:** implementar usuarios, equipos, autenticación y permisos.

**Incluye:**

- User;
- Team;
- login;
- password hashing;
- JWT;
- roles;
- pertenencia al equipo;
- RBAC;
- niveles de visibilidad;
- aislamiento entre equipos.

**Criterio de salida:**

- accesos permitidos funcionan;
- accesos denegados cuentan con pruebas;
- un equipo no puede consultar recursos de otro.

**Estado:** Completada y aprobada el 8 de noviembre de 2026.

---

## Fase 7 — Base operativa

**Objetivo:** construir los datos mínimos que necesita el flujo principal.

**Incluye:**

- Drivers;
- Vehicles;
- Tracks;
- Events;
- disponibilidad;
- activación y desactivación;
- historial básico.

**Entregable:** `v0.2 — Operational Base`.

**Criterio de salida:**

- pueden crearse los recursos necesarios para una sesión;
- los recursos inactivos o no disponibles son rechazados correctamente.

**Estado:** Completada, aprobada y publicada como `v0.2.0` el 9 de noviembre
de 2026. La validación de asignación completa ocurre en Fase 8, cuando exista
Session.

---

## Fase 8 — Flujo vertical de sesiones

**Objetivo:** completar la primera experiencia central de RaceOps.

**Flujo:**

```text
Evento
↓
Sesión
↓
Vueltas y sectores
↓
Feedback
↓
Observaciones
↓
Análisis e hipótesis
↓
Prioridades y acciones
↓
Siguiente sesión
↓
Resultado y conclusión
```

**Entregable:** `v0.4 — Session Learning Loop`.

**Criterio de salida:**

- el flujo puede ejecutarse de principio a fin;
- se aplican permisos;
- las reglas P0 tienen pruebas;
- puede recuperarse la cadena de aprendizaje.

Este hito tiene prioridad sobre cualquier integración externa.

**Estado:** Completada y aprobada el 12 de noviembre de 2026. El flujo vertical
y su auditoría final se publican como `v0.4.0`. Gate G6 — Vertical Alpha está
aprobado y Fase 9 queda habilitada.

---

## Fase 9 — Validación con datos y usuarios

**Objetivo:** confrontar el flujo construido con información real o
representativa.

**Estado:** En progreso. El Bloque 9.1 define protocolo, privacidad, métricas,
umbrales y límites de evidencia antes de construir el cliente mínimo de
validación o invitar participantes.

**Actividades:**

- utilizar una sesión real cuando exista autorización;
- probar captura de feedback;
- observar usuarios utilizando el flujo;
- medir dudas, errores y campos ignorados;
- probar datos incompletos y fuera de orden;
- actualizar requisitos y dominio.

**Entregables:**

- Validation Dataset;
- Usability Findings;
- Validation Report;
- Updated Requirements.

**Criterio de salida:**

- el flujo fue probado fuera de ejemplos ideales;
- las fricciones principales están documentadas;
- los ajustes necesarios fueron priorizados.

---

## Fase 10 — Mantenimiento relacionado

**Objetivo:** conectar observaciones y acciones mecánicas con el historial
del vehículo.

**Incluye:**

- MaintenanceRecord;
- inspecciones;
- reparaciones;
- relación con sesiones y observaciones;
- disponibilidad del vehículo;
- historial cronológico.

**Entregable:** `v0.5 — Maintenance`.

**Criterio de salida:**

- una observación puede terminar en una reparación trazable;
- un vehículo no disponible no puede asignarse;
- una reparación no lo devuelve automáticamente a `READY`.

---

## Fase 11 — Historial, reportes y analítica

**Objetivo:** recuperar y comparar aprendizajes anteriores.

**Incluye:**

- historial por pista;
- historial por vehículo;
- historial por piloto;
- resumen de sesión;
- resumen de evento;
- mejor vuelta;
- promedio;
- consistencia;
- comparación entre sesiones.

**Entregable:** `v0.6 — History & Reports`.

**Criterio de salida:**

- el equipo puede responder qué ocurrió, qué cambió y qué pasó después;
- los reportes respetan confidencialidad;
- las métricas son reproducibles.

---

## Fase 12 — Frontend y experiencia consolidada

**Objetivo:** integrar una interfaz clara y de baja fricción.

El frontend se desarrollará gradualmente desde las fases anteriores. Esta
fase consolidará:

- navegación por rol;
- captura rápida;
- flujo de sesión;
- análisis y acciones;
- mantenimiento;
- historial;
- manejo visual de errores;
- diseño responsive;
- accesibilidad básica.

**Criterio de salida:**

- las tareas principales pueden completarse sin ayuda;
- la interfaz funciona en teléfono y computadora;
- los formularios no exigen datos irrelevantes.

---

## Fase 13 — Robustez y seguridad

**Objetivo:** intentar romper RaceOps antes de la feria.

**Incluye:**

- duplicados;
- estados inválidos;
- accesos no autorizados;
- sesiones bloqueadas;
- datos incompletos;
- errores de base de datos;
- regresión;
- revisión de secretos;
- CORS;
- ownership;
- exposición indirecta.

**Criterio de salida:**

- no existen defectos críticos conocidos;
- las reglas P0 pasan;
- los controles de autorización fueron revisados.

---

## Fase 14 — Rendimiento

**Objetivo:** medir el comportamiento de RaceOps.

**Incluye:**

- escenario reproducible;
- dataset representativo;
- latencia;
- throughput;
- concurrencia;
- consultas;
- cuellos de botella.

**Criterio de salida:**

- existe un reporte con mediciones;
- cualquier afirmación de capacidad está respaldada;
- las optimizaciones responden a problemas observados.

---

## Fase 15 — Funciones condicionadas

**Objetivo:** incorporar únicamente mejoras respaldadas por evidencia y
tiempo disponible.

Candidatos:

- importación CSV;
- integración meteorológica;
- almacenamiento de archivos;
- alertas automáticas;
- comparaciones avanzadas;
- incidentes como módulo independiente.

**Criterio de entrada:**

- flujo P0 estable;
- pruebas aprobadas;
- evidencia suficiente;
- tiempo disponible.

Esta fase puede omitirse sin impedir RaceOps v1.0.

---

## Fase 16 — Operaciones en vivo condicionadas

**Objetivo:** evaluar actualizaciones inmediatas solamente si aportan valor.

Candidatos:

- WebSocket o SSE;
- actualizaciones de vuelta;
- estado de sesión;
- leaderboard.

La telemetría en vivo continúa fuera de v1.0.

**Criterio de entrada:** evidencia clara y núcleo completamente estable.

---

## Fase 17 — Preparación para la feria

**Objetivo:** construir una demostración confiable.

**Incluye:**

- dataset estable;
- guion;
- presentación;
- ensayos;
- fallback;
- video;
- material visual;
- revisión de UI;
- congelamiento de funciones.

**Entregable:** `v0.9 — Fair Candidate`.

**Criterio de salida:**

- la demo se ejecuta de forma reproducible;
- existe una alternativa sin conexión;
- el discurso explica problema, evidencia, solución y resultado.

---

## Fase 18 — RaceOps v1.0

**Objetivo:** publicar una versión estable.

**Incluye:**

- código etiquetado;
- pruebas;
- CI;
- Docker;
- documentación;
- screenshots;
- changelog;
- release notes;
- video;
- roadmap posterior.

**Entregable:** `v1.0.0 — Fair Release`.

---

## Fase 19 — Portafolio y evidencia pública

**Objetivo:** convertir el proyecto en evidencia profesional.

**Incluye:**

- README;
- arquitectura;
- ADR;
- pruebas;
- decisiones;
- devlog;
- capturas;
- demostraciones;
- publicaciones seleccionadas.

No se publicarán datos sensibles ni afirmaciones sin respaldo.

---

## Fase 20 — Validación posterior a la feria

**Objetivo:** observar si RaceOps tiene utilidad fuera del entorno
académico.

**Incluye:**

- pruebas con equipos;
- entrevistas posteriores;
- uso repetido;
- análisis de abandono;
- priorización basada en conducta.

---

## Fase 21 — Validación comercial

**Objetivo:** decidir si existe fundamento para un producto comercial.

**Evaluar:**

- frecuencia del problema;
- impacto;
- adopción;
- disposición a pagar;
- comprador;
- alternativas;
- costo de operación.

RaceOps sólo avanzará si existe evidencia suficiente.

---

## Fase 22 — RaceOps Cloud

**Objetivo:** diseñar una posible versión SaaS.

Posibles capacidades:

- multi-tenancy comercial;
- suscripciones;
- facturación;
- recuperación de contraseña;
- correo;
- auditoría;
- backups;
- monitoring;
- soporte.

Esta fase no pertenece a RaceOps v1.0.

# 5. Versiones previstas

| Versión | Contenido |
|---|---|
| `v0.1` | Fundación técnica |
| `v0.2` | Identidad y base operativa |
| `v0.3` | Sesiones, vueltas y sectores |
| `v0.4` | Flujo completo de aprendizaje |
| `v0.5` | Mantenimiento |
| `v0.6` | Historial, reportes y analítica |
| `v0.7` | Validación y correcciones |
| `v0.8` | Mejoras condicionadas |
| `v0.9` | Candidato para la feria |
| `v1.0.0` | Release estable |

Una versión podrá cambiar de contenido si la evidencia obliga a modificar
el producto.

# 6. Puertas de control

| Gate | Condición |
|---|---|
| G0 — Definition Ready | Documentos de Fase 0 aprobados |
| G1 — Problem Ready | Evidencia, contraevidencia e hipótesis registradas |
| G2 — Requirements Ready | P0, permisos y criterios de aceptación aprobados |
| G3 — Domain Ready | Entidades, estados y reglas críticas aprobadas |
| G4 — Architecture Ready | Estructura y decisiones técnicas aprobadas |
| G5 — Foundation Running | API, DB, migraciones, Docker, tests y CI funcionando |
| G6 — Vertical Alpha | Flujo entre sesiones completo |
| G7 — Validated MVP | Flujo probado con datos y usuarios |
| G8 — Fair Candidate | Demo estable y funciones congeladas |
| G9 — Release | `v1.0.0` publicado |

# 7. Actividades transversales

Durante todas las fases se mantendrán:

- investigación;
- gestión de riesgos;
- pruebas;
- seguridad;
- documentación;
- devlog;
- control de versiones;
- revisión de alcance;
- evidencia;
- preparación gradual del portafolio.

# 8. Calendario pendiente

Cuando se publique la fecha oficial de la feria se añadirán:

- fechas de inicio y cierre por fase;
- duración de iteraciones;
- reservas para correcciones;
- fecha de congelamiento;
- fecha de `v0.9`;
- fecha de `v1.0.0`.

La ausencia de fecha no autoriza ampliar el alcance ni comenzar funciones
condicionadas.
