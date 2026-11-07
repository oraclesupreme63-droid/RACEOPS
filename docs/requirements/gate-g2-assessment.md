# RaceOps — Evaluación Gate G2: Requirements Ready

## 1. Información del documento

- **Gate:** G2 — Requirements Ready
- **Versión:** 0.1
- **Estado:** Aprobado condicionalmente
- **Fecha de evaluación:** 22 de octubre de 2026
- **Fase evaluada:** Fase 2 — Ingeniería de requerimientos

## 2. Condición del gate

El roadmap define que G2 puede aprobarse cuando:

- cada función P0 tiene actor, regla y criterio de aceptación;
- las responsabilidades de los roles están claras;
- los elementos condicionados no bloquean el MVP.

## 3. Resultado del refinamiento

| Artefacto | Resultado |
|---|---:|
| Requisitos funcionales | 170 |
| Requisitos P0 | 104 |
| Requisitos P1 | 60 |
| Requisitos P2 | 4 |
| Requisitos P3 | 2 |
| Requisitos no funcionales | 67 |
| Actores | 5 humanos y 3 técnicos |
| Casos de uso | 19 |
| Historias de usuario | 22 |
| Criterios funcionales | 33 |
| Criterios no funcionales agrupados | 6 |
| Elementos de backlog | 50 |
| Cobertura trazable de RF P0 | 104 de 104 |

## 4. Comprobación de entregables

| Entregable | Ubicación | Resultado |
|---|---|---|
| Functional Requirements | `docs/preliminary-requirements.md`, versión 2.0 | Cumplido |
| Non-Functional Requirements | Mismo catálogo, sección 5 | Cumplido |
| Actores | `docs/requirements/actors.md` | Cumplido |
| Permission Matrix | `docs/requirements/permission-matrix.md` | Cumplido provisionalmente |
| Use Cases | `docs/requirements/use-cases.md` | Cumplido |
| User Stories | `docs/requirements/user-stories.md` | Cumplido |
| Acceptance Criteria | `docs/requirements/acceptance-criteria.md` | Cumplido |
| Prioritized Backlog | `docs/requirements/prioritized-backlog.md` | Cumplido |
| Traceability Matrix | `docs/requirements/traceability-matrix.md` | Cumplido |
| Definition of Ready / Done | `docs/requirements/definition-of-ready-done.md` | Cumplido |

## 5. Verificaciones realizadas

- Los RF mantienen numeración continua RF-001 a RF-170.
- La distribución es 104 P0, 60 P1, 4 P2 y 2 P3.
- Existen 67 RNF con identificadores únicos.
- Los 104 RF P0 aparecen en la matriz de trazabilidad.
- Cada grupo P0 tiene actor, historia, caso de uso, aceptación y backlog.
- Mantenimiento RF-136 a RF-149 fue retirado del P0 y permanece P1.
- El flujo P0 no depende de CSV, clima externo, telemetría en vivo, IA,
  mantenimiento completo ni facturación.

## 6. Decisiones que se aprobarían con G2

1. Usar cinco roles iniciales: Administrator, Team Manager, Engineer,
   Mechanic y Driver.
2. Aplicar menor privilegio y aislamiento estricto entre equipos.
3. No conceder a Administrator o Team Manager acceso automático a
   `ENGINEERING_CONFIDENTIAL`.
4. Prohibir siempre ese nivel al Driver.
5. Mantener un rol principal por membresía durante el modelado inicial;
   varios roles quedan como cuestión abierta.
6. Mantener el Session Learning Loop como núcleo P0 provisional.
7. Tratar mantenimiento completo como P1.
8. Utilizar los criterios de aceptación y backlog como base de las fases
   siguientes.

## 7. Riesgos abiertos

- No se entrevistó directamente a Team Managers ni Mechanics.
- La matriz de permisos puede cambiar con evidencia nueva.
- El máximo de tres prioridades procede principalmente de INT-003.
- El flujo completo todavía no fue probado con usuarios.
- Algunos estados y enumeraciones son candidatos y deberán validarse en el
  modelado del dominio.
- La cantidad de reglas P0 exige implementación incremental rigurosa.

## 8. Recomendación

**Resultado recomendado: APROBACIÓN CONDICIONAL.**

La especificación es suficiente para iniciar la Fase 3 — Modelado del
dominio, con estas condiciones:

1. Los permisos se consideran conservadores y provisionales.
2. Nueva evidencia puede modificar requisitos mediante trazabilidad y
   control de cambios.
3. Los estados candidatos no se consideran definitivos hasta modelar
   invariantes y transiciones.
4. La aprobación no autoriza todavía comenzar programación.
5. La programación continúa prevista después de aprobar G4 — Architecture
   Ready.

## 9. Opciones de decisión

### Opción A — Aprobar G2 condicionalmente

Avanzar a Fase 3 con las condiciones anteriores.

### Opción B — Mantener G2 abierto

Refinar requisitos antes de comenzar el modelo del dominio.

### Opción C — Rechazar el paquete

Replantear roles, prioridades o flujo principal.

## 10. Decisión registrada

- **Opción seleccionada:** Opción A — Aprobar G2 condicionalmente.
- **Fecha de decisión:** 22 de octubre de 2026.
- **Decisión del propietario:** Avanzar a Fase 3 — Modelado del dominio.
- **Condiciones:** Aceptadas según la sección 8.

## 11. Resultado del gate

**G2 — REQUIREMENTS READY: APROBADO CONDICIONALMENTE.**

Los requisitos pueden utilizarse para modelar el dominio manteniendo las
reglas provisionales y la investigación activa.
