# RaceOps — Reporte del Bloque 8.5: Laps, Sectors y métricas

## 1. Estado

- **Fecha:** 10 de noviembre de 2026
- **Fase:** 8 — Session Learning Loop
- **Bloque:** 8.5 — Laps, Sectors y métricas
- **Resultado:** implementado y verificado; pendiente de aprobación del propietario
- **Hito:** cierre técnico de `v0.3 — Sessions & Results`

## 2. Capacidad entregada

RaceOps permite capturar, consultar y corregir Laps y Sectors mientras los
resultados de Session estén abiertos. Las duraciones se guardan como enteros en
microsegundos; los Sectors son opcionales, variables y tienen orden explícito.
Crear una Lap con Sectors es atómico.

Cada Lap conserva origen y clasificación. Sólo `VALID` participa en mejor
vuelta, promedio y consistencia; las demás permanecen visibles y contadas sin
contaminar las métricas.

## 3. Seguridad e integridad

- Team se deriva de la Membership y se refuerza con FKs compuestas;
- lap number es único por Session y sector order por Lap;
- duraciones y órdenes deben ser positivos;
- todos los Roles pueden leer, pero Driver sólo sus Sessions asignadas;
- Administrator, Team Manager y Engineer escriben;
- `LOCKED` rechaza cualquier cambio con `results_locked`;
- no existe DELETE ni reapertura en P0.

## 4. Métricas

El promedio y la desviación estándar poblacional se calculan con aritmética
entera y redondeo de mitades hacia arriba. Con datos insuficientes se devuelve
`null`, no un cero engañoso. La fórmula y sus límites están publicados en el
[`contrato de resultados`](../sessions/lap-sector-results-contract.md).

## 5. Evidencia de verificación

- modelos, RBAC, cálculo y casos sin datos cubiertos por pruebas unitarias;
- flujo HTTP completo probado contra PostgreSQL;
- migración `20261110_0005_results` verificada en upgrade → downgrade → upgrade;
- conflictos de Lap/Sector, filtro de elegibilidad, alcance de Driver y bloqueo
  irreversible cubiertos;
- Ruff y mypy estricto aprobados;
- suite completa: **162 pruebas aprobadas**;
- cobertura total: **93.53 %**, superior al mínimo de 90 %;
- `alembic check`: sin operaciones nuevas pendientes;
- GitHub Actions hará la comprobación independiente y el smoke test del
  contenedor al publicar el commit.

## 6. Control de alcance

No se añadieron archivos de telemetría, CSV, canales configurables, streaming,
IA ni dashboards. El objetivo fue entregar el resultado mínimo que alimenta el
futuro ciclo de feedback → hipótesis → acción → resultado.

## 7. Punto de aprobación

Con aprobación se declara el hito `v0.3.0`, se publica su tag y comienza el
Bloque 8.6: Conditions parciales por Session. El tag permanece pendiente para
que identifique exactamente el cierre aprobado.
