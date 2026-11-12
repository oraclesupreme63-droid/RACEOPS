# RaceOps — Reporte del Bloque 8.11: Outcomes y siguiente Session

## 1. Estado

- **Fecha:** 12 de noviembre de 2026
- **Fase:** 8 — Session Learning Loop
- **Bloque:** 8.11 — Outcomes y siguiente Session
- **Resultado:** implementado, verificado y aprobado por el propietario
- **Siguiente bloque:** 8.12 — Cierre de Fase 8 (`v0.4`)

## 2. Capacidad entregada

RaceOps ya conserva el resultado observado después de ejecutar una Action sin
confundir ejecución con mejora:

```text
Observation → Analysis → Hypothesis → Priority → Action
                                               ↓
                                  evaluation Session → Outcome
                                               ↓
                                    Hypothesis conclusion
```

La evaluación sólo existe para una Action `COMPLETED`, utiliza una Session
posterior real del mismo Team y conserva autor, clasificación, conclusión y
marcas de tiempo.

## 3. Resultado honesto

Las clasificaciones persistidas son:

- `IMPROVED`;
- `WORSENED`;
- `NO_MEASURABLE_EFFECT`;
- `INCONCLUSIVE`.

`NOT_EVALUATED` es exclusivamente una proyección de lectura cuando no existe
un Outcome. No forma parte del enum persistido ni crea una fila ficticia.

P0 conserva un único Outcome final por Action. Un segundo intento produce un
conflicto estable y no reemplaza la evidencia anterior.

## 4. Resolución de la siguiente Session

- una Action `NEXT_SESSION` se vincula a la `evaluation_session_id` real al
  crear su Outcome;
- `target_intent`, `target_session_id` y `target_scope_id` cambian juntos;
- cuando la Action nació desde una Priority `NEXT_SESSION`, la Priority se
  resuelve a la misma Session dentro de la misma transacción;
- una Action que ya apuntaba a una Session específica sólo puede evaluarse
  contra esa Session;
- la Session de evaluación debe ser posterior a la Session de origen;
- una Session de otro Team permanece oculta con 404.

## 5. Conclusiones e Hypothesis

El Outcome separa `public_conclusion` de `confidential_conclusion`.

- Team Manager y Mechanic sólo pueden registrar una conclusión pública;
- Mechanic únicamente puede evaluar trabajo mecánico asignado a su Role o
  User;
- sólo Engineer puede escribir o recibir conclusión confidencial;
- sólo Engineer puede concluir la Hypothesis relacionada;
- el estado debe salir explícitamente de `PROPOSED` hacia `SUPPORTED`,
  `PARTIALLY_SUPPORTED`, `REJECTED` o `INCONCLUSIVE`;
- RaceOps no deriva ese estado automáticamente desde la clasificación del
  Outcome ni desde una métrica aislada.

## 6. Visibilidad y cadena recuperable

`ActionOutcome` hereda el alcance visible de su Action y nunca amplía acceso.
La proyección de cadena permite recorrer los nodos autorizados:

- Engineer recibe Analysis, referencias de evidencia, Hypothesis, Priority,
  Action, Outcome y conclusión técnica;
- Team Manager recibe la Action y la evaluación pública, sin detalle de
  Engineering;
- Mechanic recibe únicamente cadenas de trabajo mecánico asignado;
- Driver relacionado recibe el resumen y conclusión públicos, sin Hypothesis,
  Analysis ni identificadores técnicos;
- Administrator no obtiene contenido `ROLE_RESTRICTED` sólo por jerarquía.

La prueba HTTP recorre explícitamente una referencia Observation → Analysis →
Hypothesis → Priority → Action → Outcome.

## 7. API

```text
POST /api/v1/actions/{action_id}/outcome
GET  /api/v1/actions/{action_id}/outcome
GET  /api/v1/actions/{action_id}/learning-chain
```

Las respuestas de Action incluyen `evaluation_status`. No existe `DELETE` ni
un endpoint P0 para reemplazar una evaluación histórica.

## 8. Persistencia

La migración `20261112_0011_outcomes` añade:

- tabla `action_outcomes`;
- enum PostgreSQL `action_outcome_classification`;
- FKs compuestas por Team hacia Action y evaluation Session;
- FK restrictiva al User autor;
- unicidad de un Outcome por Action;
- checks de conclusión, normalización y visibilidad;
- índice por Team y evaluation Session.

La migración se aplicó de forma no destructiva hasta `head` y `alembic check`
no detectó diferencias.

## 9. Verificación

- Ruff format/check: aprobado;
- mypy estricto para `src` y `tests`: aprobado;
- pruebas específicas de Outcomes y decisiones: **8 aprobadas**;
- suite local global no destructiva: **217 pruebas aprobadas**;
- cobertura total: **91.83 %**, superior al mínimo de 90 %;
- migración aplicada: `20261112_0011_outcomes (head)`;
- `alembic check`: sin operaciones pendientes;
- imagen de producción reconstruida;
- API y PostgreSQL saludables;
- `/health` devuelve `ok` y `/ready` devuelve `ready`;
- OpenAPI publica las tres operaciones nuevas sin rutas destructivas.

## 10. Clasificación de decisiones

- **Respaldado por evidencia:** comparar la Action con una Session posterior y
  conservar el efecto observado.
- **Respaldado por evidencia:** la conclusión puede mantener incertidumbre y
  no debe inferirse desde `COMPLETED`.
- **Respaldado por evidencia:** conclusiones públicas y detalle técnico deben
  respetar audiencias diferentes.
- **Parcialmente respaldado:** Team Manager y Mechanic pueden registrar
  Outcomes públicos dentro de su responsabilidad; debe validarse con usuarios.
- **Hipótesis conservadora:** un único Outcome final por Action en P0. La
  necesidad de revisiones múltiples permanece P1.
- **Rechazado:** persistir `NOT_EVALUATED` como si fuera evidencia.
- **Rechazado:** marcar automáticamente una Hypothesis como respaldada.

## 11. Contratiempos y deuda controlada

- Documentación antigua usaba `NO_MEASURABLE_CHANGE`; se normalizó al término
  aprobado `NO_MEASURABLE_EFFECT`.
- La cadena es una proyección por Action, no un buscador histórico completo por
  Track/Event/Driver/Vehicle; esos agregados pertenecen al cierre y evolución
  de History/Reporting.
- P0 conserva una evaluación final; revisiones sucesivas con historial propio
  no se implementan sin evidencia adicional.
- No hay recomendación automática ni interpretación de telemetría.

## 12. Aprobación

El propietario aprobó el Bloque 8.11 el 12 de noviembre de 2026. El Bloque
8.12 ejecuta y documenta el flujo vertical completo con un dataset sintético
representativo, la auditoría final de permisos y la evidencia `v0.4.0` para el
Gate G6 — Vertical Alpha.
