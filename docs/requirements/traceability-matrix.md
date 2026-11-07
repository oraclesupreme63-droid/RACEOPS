# RaceOps — Matriz de trazabilidad

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparada para Gate G2
- **Objetivo:** Conectar evidencia, actores, historias, casos de uso,
  requisitos, aceptación y backlog.

## 2. Trazabilidad funcional P0

| ID | Fuente o fundamento | Actor | Historia | Caso de uso | Requisitos P0 | Aceptación | Backlog |
|---|---|---|---|---|---|---|---|
| TR-001 | Seguridad técnica; F-017–F-019 | Administrator / miembro | US-001, US-002 | UC-001, UC-002 | RF-001–RF-008 | AC-001–AC-004 | BL-009–BL-012 |
| TR-002 | Habilitador del flujo | Team Manager / Driver | US-003 | UC-003 | RF-013–RF-017 | AC-005, AC-008 | BL-013 |
| TR-003 | Disponibilidad operativa | Team Manager | US-004 | UC-004 | RF-018–RF-021 | AC-006, AC-008 | BL-014 |
| TR-004 | Contexto de sesión | Team Manager | US-005 | UC-005 | RF-024, RF-026, RF-027, RF-029 | AC-007 | BL-015, BL-016 |
| TR-005 | Session Learning Loop | Team Manager / Engineer | US-006, US-007 | UC-006, UC-007 | RF-031–RF-037, RF-040–RF-042 | AC-009–AC-013 | BL-017–BL-019 |
| TR-006 | INT-001, INT-003 | Engineer | US-008 | UC-008 | RF-045–RF-047, RF-050, RF-051 | AC-014, AC-016 | BL-020 |
| TR-007 | INT-001, INT-003 | Engineer | US-008 | UC-008 | RF-055–RF-058 | AC-015 | BL-021 |
| TR-008 | Resultados reproducibles | Engineer | US-008 | UC-008 | RF-063, RF-064, RF-066, RF-068, RF-069 | AC-016 | BL-022 |
| TR-009 | INT-001; contraesquema rígido | Engineer / Team Manager | US-009 | UC-009 | RF-070, RF-072, RF-073, RF-076, RF-078 | AC-017, AC-033 | BL-023 |
| TR-010 | F-002, F-013; A-002 | Driver / Engineer | US-010, US-011 | UC-010 | RF-079–RF-082, RF-085–RF-087 | AC-018, AC-019 | BL-024, BL-025 |
| TR-011 | F-014, F-016 | Engineer / Mechanic | US-012 | UC-011 | RF-089, RF-092, RF-094, RF-095 | AC-020 | BL-026 |
| TR-012 | F-013, F-014, F-016, F-018 | Engineer | US-013, US-017 | UC-012 | RF-096, RF-097, RF-099, RF-100, RF-103–RF-107 | AC-004, AC-021, AC-022 | BL-027–BL-029 |
| TR-013 | F-015; A-003 | Engineer / destinatario | US-014 | UC-013 | RF-108–RF-110, RF-112, RF-113 | AC-023, AC-024 | BL-030 |
| TR-014 | F-014; A-004 | Engineer / responsable | US-015 | UC-014 | RF-115–RF-118, RF-120, RF-121 | AC-025, AC-026 | BL-031 |
| TR-015 | A-004; flujo provisional | Engineer | US-016 | UC-015 | RF-123–RF-130 | AC-022, AC-027, AC-028 | BL-032, BL-033 |
| TR-016 | P-001; límite de alcance | Engineer | US-020 | UC-016 | RF-133 | AC-033 | BL-041 P1, sin dependencia P0 |
| TR-017 | F-004; A-005; A-004 | Miembro autorizado | US-018 | UC-017 | RF-152–RF-159 | AC-029, AC-030, AC-032 | BL-034 |
| TR-018 | Tesis de producto; confidencialidad | Miembro autorizado | US-017, US-019 | UC-017 | RF-161, RF-162, RF-164–RF-167 | AC-031, AC-032 | BL-035 |

## 3. Trazabilidad no funcional

| Área | Requisitos | Criterio / evidencia futura | Backlog o DoD |
|---|---|---|---|
| Seguridad | RNF-SEC-001–RNF-SEC-012 | AC-NF-001, AC-NF-003 | BL-009–BL-012; DoD seguridad |
| Integridad | RNF-REL-001–RNF-REL-008 | AC-NF-002, AC-033 | DoD datos y transacciones |
| Rendimiento | RNF-PER-001–RNF-PER-006 | Escenario reproducible, sin cifras inventadas | EP-09 y fase de rendimiento |
| Usabilidad | RNF-USA-001–RNF-USA-010 | AC-NF-004; prueba con usuarios | BL-039 |
| Compatibilidad | RNF-COM-001–RNF-COM-004 | Pruebas de API y navegador | DoD integración |
| Mantenibilidad | RNF-MAN-001–RNF-MAN-009 | AC-NF-006; revisión de arquitectura | EP-00 y Gate G4 |
| Calidad | RNF-QUA-001–RNF-QUA-007 | AC-NF-005 | BL-004, BL-008 |
| Observabilidad | RNF-OBS-001–RNF-OBS-005 | Logs seguros y health | BL-006, BL-007 |
| Despliegue | RNF-DEP-001–RNF-DEP-006 | AC-NF-006 | BL-003, BL-005, BL-008 |

## 4. Trazabilidad de decisiones fuera de P0

| Decisión | Fundamento | Requisitos / backlog |
|---|---|---|
| Mantenimiento completo pasa a P1 | Gate G1; evidencia insuficiente para primer flujo | RF-136–RF-149; BL-042 |
| CSV permanece condicionado | A-008 sin validar | RF-134; BL-045 |
| Clima automático no bloquea | Baja fricción y resiliencia | RF-076, RF-077; BL-046 |
| Telemetría en vivo fuera de V1 | P-001 y análisis de competidores | RF-135; BL-048 |
| IA automática fuera de V1 | Sin datos ni evidencia suficiente | BL-049 |
| Facturación fuera de V1 | A-012 sin evidencia | BL-050 |

## 5. Control de cobertura

Cada requisito P0 está incluido en una fila TR-001 a TR-018 y relacionado
con:

- al menos un actor;
- una historia de usuario;
- un caso de uso;
- un criterio de aceptación;
- un elemento del backlog o una frontera explícita del P0.

La trazabilidad deberá actualizarse si cambia una prioridad o si nueva
evidencia modifica el alcance.

