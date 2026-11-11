# RaceOps — Reporte del Bloque 8.9: Analysis e Hypotheses

## 1. Estado

- **Fecha:** 11 de noviembre de 2026
- **Fase:** 8 — Session Learning Loop
- **Bloque:** 8.9 — Analysis e Hypotheses
- **Resultado:** implementado y verificado; pendiente de aprobación del propietario
- **Siguiente bloque:** 8.10 — Priorities y Actions

## 2. Capacidad entregada

RaceOps permite que Engineer documente el razonamiento técnico de una Session
sin presentarlo como certeza. Cada análisis requiere al menos una referencia a
evidencia existente de su contexto: Driver Feedback, Lap, Sector, Condition u
Observation. Una Observation sólo de Vehicle debe corresponder al Vehicle
asignado a la Session.

El detalle técnico y las Hypotheses permanecen
`ENGINEERING_CONFIDENTIAL`. El análisis puede contener además un resumen
autorizado, almacenado y serializado por separado para los demás Roles.

## 3. Contrato de Analysis

- conserva Team, Session, autor y timestamps server-side;
- exige detalle técnico y una o más referencias de evidencia únicas;
- valida la existencia, Team y relación con la Session de cada referencia;
- permite evidencia parcial sin inventar fuentes ausentes;
- mantiene evidencia, contexto, autor y visibilidad inmutables en P0;
- no expone DELETE;
- permite editar el detalle y retirar o sustituir el resumen autorizado.

Las referencias usan un tipo controlado y un UUID. La integridad polimórfica
se valida en el servicio antes de escribir; los recursos P0 referenciados no
tienen operación DELETE.

## 4. Contrato de Hypothesis

- requiere descripción, clasificación de causa y confianza;
- nace siempre en estado `PROPOSED` controlado por el servidor;
- utiliza las causas `DRIVER_TECHNIQUE`, `VEHICLE_SETUP`, `MECHANICAL`,
  `TIRES`, `TRACK_ENVIRONMENT` y `UNKNOWN`;
- utiliza confianza `LOW`, `MEDIUM` o `HIGH`;
- no puede declararse `SUPPORTED`, `PARTIALLY_SUPPORTED`, `REJECTED` o
  `INCONCLUSIVE` desde los endpoints de este bloque;
- las conclusiones se aplazan al Bloque 8.11, cuando exista evidencia de una
  Action evaluada en otra Session.

## 5. Autorización y no filtración

- sólo Engineer posee `WRITE_ANALYSIS` y accede al registro técnico completo;
- Administrator y Team Manager no heredan el detalle confidencial;
- todos los Roles poseen `READ_ANALYSIS_SUMMARIES`, sujeto a Team y relación;
- Driver sólo consulta resúmenes de sus Sessions asignadas;
- el endpoint autorizado devuelve únicamente texto y `updated_at`;
- no devuelve `analysis_id`, autor, evidencia, detalle técnico, Hypotheses,
  conteo total ni existencia de análisis que carecen de resumen autorizado;
- un recurso o evidencia de otro Team se oculta con 404.

## 6. API

```text
POST  /api/v1/sessions/{session_id}/analyses
GET   /api/v1/sessions/{session_id}/analyses
GET   /api/v1/sessions/{session_id}/analysis-summaries
GET   /api/v1/analyses/{analysis_id}
PATCH /api/v1/analyses/{analysis_id}

POST  /api/v1/analyses/{analysis_id}/hypotheses
GET   /api/v1/analyses/{analysis_id}/hypotheses
GET   /api/v1/hypotheses/{hypothesis_id}
PATCH /api/v1/hypotheses/{hypothesis_id}
```

## 7. Persistencia

La migración `20261111_0009_analysis` añade:

- `session_analyses`;
- `analysis_evidence_references`;
- `hypotheses`;
- enums de tipo de evidencia, causa, confianza y estado;
- FKs compuestas por Team, constraints de texto, confidencialidad e índices.

La base local fue actualizada de forma no destructiva hasta `head` y
`alembic check` no detectó diferencias. El round-trip destructivo completo se
reserva para PostgreSQL efímero de CI, evitando borrar datos locales.

## 8. Verificación

- Ruff format/check: aprobado;
- mypy estricto para `src` y `tests`: aprobado;
- prueba HTTP dirigida con los cinco tipos de evidencia: aprobada;
- pruebas negativas de Role, Team, relación de Driver y conclusión prematura:
  aprobadas;
- suite local completa no destructiva: **200 pruebas aprobadas**;
- cobertura total: **92.69 %**, superior al mínimo de 90 %;
- migración aplicada: `20261111_0009_analysis (head)`;
- `alembic check`: sin operaciones nuevas pendientes;
- imagen Docker reconstruida; contenedores API y PostgreSQL saludables;
- smoke test aprobado para `/health`, `/ready` y las cinco rutas OpenAPI del
  bloque.

## 9. Clasificación de decisiones

- **Respaldado por evidencia:** unir feedback, resultados, condiciones y
  observaciones para formular una explicación posible.
- **Respaldado por evidencia:** separar resumen autorizado y detalle técnico
  confidencial por audiencia.
- **Respaldado por evidencia:** causa, confianza y estado explícitos, sin falsa
  certeza.
- **Parcialmente respaldado:** catálogo inicial de seis causas; deberá
  revisarse con más equipos y categorías.
- **Hipótesis conservadora:** cualquier Engineer del Team puede corregir un
  análisis o Hypothesis propuesto; una auditoría de revisiones queda fuera de
  P0.
- **Rechazado:** inferir causalidad automáticamente o permitir que el cliente
  marque una Hypothesis como respaldada sin resultado posterior.

## 10. Contratiempos y deuda controlada

- La prueba local de downgrade hasta `base` eliminaría el esquema y por eso no
  se ejecutó sobre datos locales; CI la ejecutará en una base desechable.
- El vínculo polimórfico de evidencia depende de validación transaccional del
  servicio; no admite escritura directa confiable fuera de RaceOps.
- Aún no existe una Conclusion legítima: depende de Priorities, Actions y
  Outcomes en los Bloques 8.10–8.11.

## 11. Punto de aprobación

Con aprobación comenzará el Bloque 8.10: Priorities y Actions. Ese bloque
convertirá el análisis en un máximo de tres prioridades principales y en
acciones asignables, sin fingir que la próxima Session ya existe.
