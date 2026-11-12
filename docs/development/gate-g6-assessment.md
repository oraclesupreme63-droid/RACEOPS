# RaceOps — Evaluación Gate G6: Vertical Alpha

## 1. Información

- **Fecha de evaluación técnica:** 12 de noviembre de 2026
- **Versión evaluada:** candidato `v0.4.0 — Session Learning Loop`
- **Gate:** G6 — Vertical Alpha
- **Decisión:** técnicamente satisfecho; pendiente de aprobación del propietario

## 2. Objetivo del gate

Confirmar que RaceOps puede ejecutar su primer flujo de valor completo, aplicar
los permisos P0 y recuperar la cadena de razonamiento antes de probar el
producto con usuarios y datos autorizados.

## 3. Evidencia

| Criterio de salida | Evidencia | Resultado |
|---|---|---|
| Flujo de principio a fin | prueba HTTP con dos Sessions y dataset `v0.4` | Cumplido |
| Permisos aplicados | vistas Engineer, Driver, Team Manager, Mechanic y Administrator | Cumplido |
| Reglas P0 probadas | pruebas unitarias, API, integración y aceptación | Cumplido |
| Cadena recuperable | endpoint `learning-chain` desde Action hasta Outcome | Cumplido |
| Dataset reproducible | JSON sintético, determinista y sin datos sensibles | Cumplido |
| Ejecución offline | sólo aplicación y PostgreSQL locales | Cumplido |
| Calidad técnica | Ruff, mypy, 218 pruebas y 91.88 % de cobertura local | Cumplido localmente; CI pendiente |
| Migraciones y contenedores | `head`, `alembic check`, imagen `0.4.0`, health y readiness | Cumplido localmente; round-trip en CI pendiente |

## 4. Límites aceptados

- no se ingiere telemetría en vivo ni se reemplaza AiM, MyChron o MoTeC;
- las métricas se limitan a resultados y contexto seleccionados;
- el historial P0 se recupera por Action, no ofrece búsqueda inteligente;
- no existen recomendaciones automáticas ni afirmaciones de causalidad;
- la usabilidad, adopción y lenguaje del nicho aún no están validados;
- la primera validación externa se hará en Fase 9 con consentimiento y datos
  representativos o autorizados.

## 5. Decisión de publicación

El código puede prepararse como candidato `v0.4.0`, pero el tag no se publica
hasta completar la verificación global y recibir aprobación explícita del
propietario. Esa aprobación cerrará Fase 8 y habilitará Fase 9; no convertirá
las hipótesis de adopción en hechos.
