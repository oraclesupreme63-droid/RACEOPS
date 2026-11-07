# RaceOps — Evaluación Gate G5: Foundation Running

## 1. Información

- **Fecha de evaluación:** 2026-11-07
- **Versión evaluada:** `v0.1 — Foundation`
- **Gate:** G5 — Foundation Running
- **Decisión:** Aprobado

## 2. Objetivo del gate

Confirmar que RaceOps tiene una fundación ejecutable, reproducible, observable
y protegida por verificaciones automáticas antes de implementar identidad y
reglas de negocio.

## 3. Evidencia

| Criterio | Evidencia | Resultado |
|---|---|---|
| API ejecutable | FastAPI inicia directa y contenerizada | Cumplido |
| PostgreSQL disponible | Compose health check y `/ready` | Cumplido |
| Migraciones | baseline, upgrade/downgrade/upgrade y `alembic check` | Cumplido |
| Health checks | `/health` y `/ready` con contratos probados | Cumplido |
| Errores seguros | RFC 9457, request ID y pruebas 404/405/422/500 | Cumplido |
| Observabilidad | logs JSON, correlación y redacción de secretos | Cumplido |
| Calidad | Ruff format, Ruff check y mypy sin errores | Cumplido |
| Pruebas | 22 aprobadas y cobertura superior al 90 % | Cumplido |
| Docker | imagen multi-stage, no root y sin dependencias dev | Cumplido |
| Compose | `db` → `migrate` → `api`, todos comprobados | Cumplido |
| Documentación | README, runbook, checklist y roadmap de aprendizaje | Cumplido |
| CI definida | jobs de calidad y smoke test en GitHub Actions | Cumplido |
| CI ejecutada en GitHub | jobs `quality` y `container` en la ejecución 42399043070 | Cumplido |

## 4. Validaciones realizadas

- `docker compose config --quiet`;
- `docker compose up -d --build --wait`;
- PostgreSQL y API en estado `healthy`;
- migración one-shot finalizada con código `0`;
- revisión Alembic `20261024_0001 (head)`;
- `alembic check`: sin operaciones nuevas detectadas;
- endpoints de health, readiness y OpenAPI consultados;
- runtime ejecutado con UID/GID `10001`;
- ausencia de pytest en la imagen productiva;
- 22 pruebas aprobadas;
- cobertura de referencia `90.75 %`;
- Ruff y mypy aprobados;
- workflow CI analizado localmente y comandos reproducidos;
- repositorio privado publicado en `oraclesupreme63-droid/RACEOPS`;
- ejecución [CI 42399043070](https://github.com/oraclesupreme63-droid/RACEOPS/actions/runs/42399043070)
  completada con los jobs `quality` y `container` en verde.

## 5. Condición verificada

La condición externa fue satisfecha el 7 de noviembre de 2026:

1. se aprobó el contenido de `v0.1 — Foundation`;
2. se creó el commit inicial y se publicó la rama `main`;
3. `origin` quedó conectado al repositorio privado de GitHub;
4. se corrigieron dos diferencias detectadas por el runner Linux: la ruta
   temporal de Pytest y la contaminación de variables de entorno;
5. los jobs `quality` y `container` terminaron correctamente;
6. el enlace y resultado quedaron registrados como evidencia.

Los dos fallos anteriores se conservaron en el historial de Actions y muestran
que el workflow detectó problemas reales antes de avanzar a Fase 6.

## 6. Riesgos residuales aceptados

- las dependencias utilizan rangos compatibles, no un lockfile completo;
- no existe despliegue productivo, HTTPS ni administración real de secretos;
- no se ha probado todavía autenticación, autorización o aislamiento por Team;
- la fundación no demuestra valor de producto sin el flujo vertical de sesión;
- las pruebas actuales usan datos sintéticos y contratos de infraestructura.

Estos riesgos pertenecen a fases posteriores o requieren una decisión de
publicación. No invalidan la fundación local.

## 7. Decisión

La Fase 5 está completa y puede presentarse como `v0.1 — Foundation`. G5 queda
**aprobado** con evidencia local y una ejecución real de CI en GitHub.

RaceOps puede comenzar la Fase 6 — Identidad y autorización.
