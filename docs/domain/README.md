# RaceOps — Paquete de modelado del dominio

## Estado

Preparado para evaluación del Gate G3 — Domain Ready.

## Documentos

| Documento | Propósito |
|---|---|
| [`ubiquitous-language.md`](ubiquitous-language.md) | Vocabulario común y términos que no deben mezclarse |
| [`domain-model.md`](domain-model.md) | Entidades, objetos de valor, agregados y límites |
| [`erd.md`](erd.md) | Relaciones conceptuales P0 y extensión P1 |
| [`state-diagrams.md`](state-diagrams.md) | Ciclos de Session, Results, Vehicle, Action e Hypothesis |
| [`business-rules.md`](business-rules.md) | Reglas operativas BR-001 a BR-059 |
| [`invariants.md`](invariants.md) | Condiciones INV-001 a INV-050 que nunca deben romperse |
| [`visibility-model.md`](visibility-model.md) | Ownership, RBAC, relación y filtrado por campo |
| [`domain-traceability.md`](domain-traceability.md) | Relación de RF P0 con el modelo |
| [`gate-g3-assessment.md`](gate-g3-assessment.md) | Evaluación de salida de Fase 3 |

## Modelo resumido

```text
Team
  ├── Identity & Access
  ├── Operations
  └── Event → Session
                   ├── Results
                   ├── Feedback
                   ├── Observations
                   └── Analysis → Hypothesis
                                      ├── Priority
                                      └── Action → Outcome
```

## Decisiones principales

- Team es frontera de ownership, no SaaS multi-tenant comercial.
- V1 usa una Membership activa y un Role principal por User.
- Driver puede existir sin User.
- Session Status y Results Status son independientes.
- Lap es Aggregate Root y contiene Sectors.
- Action Status y Action Outcome son independientes.
- `NOT_EVALUATED` se deriva de la ausencia de Outcome.
- Priority y Action pueden señalar `NEXT_SESSION` antes de conocer la
  Session concreta.
- Mantenimiento y Telemetry Reference permanecen P1.
- No se usa event sourcing ni un motor ABAC genérico.
