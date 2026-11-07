# RaceOps — Evaluación Gate G3: Domain Ready

## 1. Información del documento

- **Gate:** G3 — Domain Ready
- **Versión:** 0.1
- **Estado:** Aprobado condicionalmente
- **Fecha de evaluación:** 22 de octubre de 2026
- **Fase evaluada:** Fase 3 — Modelado del dominio

## 2. Condición del gate

El roadmap permite aprobar G3 cuando:

- entidades y relaciones soportan el flujo vertical;
- los estados tienen transiciones válidas;
- la historia no se destruye;
- las reglas de confidencialidad pueden implementarse.

## 3. Resultado del modelado

| Elemento | Resultado |
|---|---:|
| Entidades P0 | 18 |
| Entidades P1 representadas | 2 |
| Objetos de valor principales | 6 |
| Agregados propuestos | 14 |
| Diagramas/ciclos de estado | 6 |
| Reglas de negocio | 59 |
| Invariantes | 50 |
| RF P0 trazados al dominio | 104 de 104 |

## 4. Comprobación de entregables

| Entregable | Ubicación | Resultado |
|---|---|---|
| Ubiquitous Language | `docs/domain/ubiquitous-language.md` | Cumplido |
| Domain Model | `docs/domain/domain-model.md` | Cumplido |
| ERD | `docs/domain/erd.md` | Cumplido conceptualmente |
| State Diagrams | `docs/domain/state-diagrams.md` | Cumplido |
| Business Rules | `docs/domain/business-rules.md` | Cumplido |
| Invariants | `docs/domain/invariants.md` | Cumplido |
| Visibility Model | `docs/domain/visibility-model.md` | Cumplido |
| Domain Traceability | `docs/domain/domain-traceability.md` | Cumplido |

## 5. Verificaciones realizadas

- BR-001 a BR-059 existen sin huecos.
- INV-001 a INV-050 existen sin huecos.
- Los 104 RF P0 están relacionados con elementos del dominio.
- Session Status y Results Status están separados.
- Action Status y Action Outcome están separados.
- `NOT_EVALUATED` se representa sin crear resultados ficticios.
- Los datos ausentes no se convierten en cero.
- Driver y User tienen identidades distintas.
- Todas las relaciones operativas están limitadas por Team Ownership.
- El historial utiliza conservación y auditoría selectiva, no event sourcing.
- La confidencialidad contempla filtrado de registros, campos, búsquedas y
  conteos.

## 6. Decisiones que se aprobarían con G3

1. Team será la frontera de ownership, sin implementar todavía SaaS
   multi-tenant comercial.
2. V1 comenzará con una TeamMembership activa y un Role principal por User.
3. Driver será una entidad separada y podrá existir sin User.
4. Event conservará su Track; no cambiará normalmente después de crear
   Sessions.
5. Session tendrá dos ciclos: actividad y bloqueo de resultados.
6. Lap será Aggregate Root y Sector permanecerá dentro de Lap.
7. P0 tendrá como máximo un Condition Snapshot por Session.
8. Observation, Hypothesis y causa confirmada permanecerán separadas.
9. Priority y Action podrán apuntar a `NEXT_SESSION` antes de que exista la
   Session concreta; esto refina RF-112 y RF-118.
10. Action `COMPLETED` y Outcome `IMPROVED` seguirán separados.
11. `NOT_EVALUATED` será un estado derivado cuando no exista Outcome.
12. El detalle técnico y el resumen autorizado se almacenarán separados.
13. Los valores predeterminados de visibilidad serán conservadores.
14. Maintenance Record y Telemetry Reference permanecerán P1.

## 7. Riesgos y preguntas abiertas

- Nuevas entrevistas pueden exigir varios Roles o Teams por User.
- La cardinalidad de Condition Snapshot podría aumentar después de pruebas.
- Puede ser necesario limitar Action a un Outcome final o permitir varias
  evaluaciones; el modelo acepta varias sin obligarlas.
- Los defaults de Visibility necesitan validación con Team Managers,
  Engineers y Mechanics.
- La implementación de constraints compuestos por Team se definirá en
  arquitectura.
- Los detalles de auditoría y almacenamiento de roles restringidos todavía
  no son decisiones físicas.

## 8. Recomendación

**Resultado recomendado: APROBACIÓN CONDICIONAL.**

El dominio es suficientemente explícito para iniciar Fase 4 — Diseño de
arquitectura, bajo estas condiciones:

1. Las decisiones físicas de base de datos no contradicen los invariantes.
2. Las dudas abiertas no se resuelven agregando complejidad sin evidencia.
3. La arquitectura mantiene un monolito modular.
4. La autorización se aplica en servidor y antes de serializar.
5. Cualquier cambio de requisitos actualiza la trazabilidad.
6. La aprobación de G3 todavía no autoriza programación; ésta comienza
   después de aprobar G4.

## 9. Opciones de decisión

### Opción A — Aprobar G3 condicionalmente

Avanzar a Fase 4 con las decisiones y condiciones anteriores.

### Opción B — Mantener G3 abierto

Refinar entidades, estados, permisos o reglas antes de arquitectura.

### Opción C — Rechazar el modelo

Replantear el flujo o sus conceptos principales.

## 10. Decisión registrada

- **Opción seleccionada:** Opción A — Aprobar G3 condicionalmente.
- **Fecha de decisión:** 22 de octubre de 2026.
- **Decisión del propietario:** Avanzar a Fase 4 — Diseño de arquitectura.
- **Condiciones:** Aceptadas según la sección 8.

## 11. Resultado del gate

**G3 — DOMAIN READY: APROBADO CONDICIONALMENTE.**

El modelo del dominio puede utilizarse para definir arquitectura y
persistencia sin tratar las hipótesis abiertas como hechos universales.
