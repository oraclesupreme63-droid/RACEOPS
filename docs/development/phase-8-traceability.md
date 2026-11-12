# RaceOps — Trazabilidad de implementación de Fase 8

## 1. Alcance

Esta matriz conecta el Session Learning Loop P0 con su implementación y sus
pruebas. La evidencia automatizada demuestra contratos, reglas y permisos; la
utilidad y facilidad de uso con personas reales se validan en Fase 9.

| Trazabilidad | Capacidad | Implementación principal | Evidencia principal | Estado |
|---|---|---|---|---|
| TR-005 / RF-031–RF-044 / AC-009–AC-013 / BL-017–BL-019 | Session, asignación, ciclo y bloqueo | `sessions/models.py`, `services.py`, `router.py` | `test_sessions.py`, `test_session_persistence.py` | Implementado |
| TR-006–TR-008 / RF-045–RF-069 / AC-014–AC-016 / BL-020–BL-022 | Laps, Sectors y métricas | `sessions/result_models.py`, `result_services.py`, `results_router.py` | `test_results.py`, pruebas de modelos y persistencia | Implementado |
| TR-009 / RF-070–RF-078 / AC-017 / BL-023 | Conditions parciales y explícitas | `sessions/condition_models.py`, `condition_services.py`, `conditions_router.py` | `test_conditions.py`, `test_condition_models.py` | Implementado |
| TR-010 / RF-079–RF-087 / AC-018–AC-019 / BL-024–BL-025 | Driver Feedback | `sessions/feedback_models.py`, `feedback_services.py`, `feedback_router.py` | `test_feedback.py`, `test_feedback_models.py` | Implementado |
| TR-011 / RF-089–RF-095 / AC-020 / BL-026 | Observations | `learning/observation_models.py`, `observation_services.py`, `observations_router.py` | `test_observations.py`, `test_observation_models.py` | Implementado |
| TR-012 / RF-096–RF-107 / AC-021–AC-022 / BL-027–BL-029 | Analysis e Hypotheses | `learning/analysis_models.py`, `analysis_services.py`, `analysis_router.py` | `test_analysis.py`, `test_analysis_models.py` | Implementado |
| TR-013–TR-014 / RF-108–RF-121 / AC-023–AC-026 / BL-030–BL-031 | Priorities y Actions | `learning/decision_models.py`, `decision_services.py`, `decisions_router.py` | `test_decisions.py`, `test_decision_models.py` | Implementado |
| TR-015 / RF-123–RF-130 / AC-027–AC-028 / BL-032–BL-033 | Outcome y conclusión | `learning/outcome_models.py`, `outcome_services.py`, `decisions_router.py` | `test_decisions.py`, `test_outcome_models.py` | Implementado |
| TR-017–TR-018 / RF-152–RF-167 / AC-029–AC-032 / BL-034–BL-035 | Historia recuperable y confidencialidad | proyección `learning-chain`, RBAC y Visibility | `test_session_learning_loop.py` y pruebas API por recurso | Implementado en el flujo P0 |

## 2. Flujo vertical verificado

`tests/acceptance/test_session_learning_loop.py` usa
`tests/fixtures/session_learning_loop_v0.4.json` para ejecutar por HTTP:

```text
Event → Session 1 → Results + Conditions + Feedback + Observation
      → Analysis → Hypothesis → Priority → Action
      → Session 2 → Outcome → Hypothesis conclusion → learning chain
```

El dataset es sintético, determinista, no contiene credenciales reales y no
requiere red ni servicios externos distintos del PostgreSQL local del proyecto.

## 3. Reglas transversales verificadas

- el Team se deriva de la Membership activa y los UUID ajenos se ocultan;
- Driver y Vehicle deben ser asignables y pertenecer al mismo Team;
- Results dejan de aceptar escritura al bloquearse;
- el análisis distingue evidencia, hipótesis, acción y resultado;
- completar una Action no implica que haya mejorado el resultado;
- la Hypothesis sólo cambia mediante una conclusión explícita;
- la visibilidad pública, restringida y confidencial se serializa por actor;
- el Driver relacionado no recibe detalle técnico confidencial;
- Administrator no obtiene contenido restringido por jerarquía implícita;
- no existe borrado físico del historial mediante la API P0.

## 4. Frontera de evidencia

La prueba demuestra que el flujo funciona de extremo a extremo y que la cadena
puede recuperarse seis meses después si la base se conserva. No demuestra que
el formulario sea rápido, que los equipos adopten el producto ni que las
clasificaciones coincidan con su lenguaje cotidiano. Esas preguntas quedan
explícitamente asignadas a Fase 9.
