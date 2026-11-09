# RaceOps — Reporte del Bloque 7.1: contrato operativo

## 1. Estado

- **Fecha:** 8 de noviembre de 2026
- **Fase:** 7 — Base operativa
- **Bloque:** 7.1 — Contrato operativo
- **Resultado:** documentado; pendiente de aprobación del propietario
- **Siguiente bloque:** 7.2 — Persistencia operativa

## 2. Trabajo realizado

Se consolidaron RF-013–RF-030, AC-005–AC-008, BL-013–BL-016, el modelo de
dominio, invariantes, reglas y permisos para definir el mínimo implementable
de Driver, Vehicle, Track y Event.

El contrato resuelve:

- campos mínimos y longitudes;
- ownership por Team;
- Driver separado de User con vínculo opcional por Team;
- estados de Driver, Vehicle y Event;
- transiciones de Vehicle y Event;
- preservación histórica sin endpoints de borrado;
- permisos y errores HTTP esperados;
- constraints e índices que deberá producir la migración.

## 3. Decisiones importantes

- Driver no exige cuenta User.
- Un User puede vincular un Driver por Team, compatible con múltiples
  Memberships legítimas.
- Vehicle inicia `READY`; solamente `READY` será asignable y `RETIRED` es
  terminal.
- Track permanece mínimo, sin campos de telemetría.
- Event exige Track del mismo Team y fechas coherentes.
- El ciclo de Event se marca como hipótesis, no como verdad universal.
- No se crea `DELETE` normal para recursos operativos.

## 4. Control de alcance

No se programaron todavía tablas ni endpoints. Tampoco se adelantaron
Session, Maintenance, inventario, telemetría o detalles de setup. AC-005 y
AC-006 se completarán de extremo a extremo en Fase 8; en Fase 7 se prueba la
asignabilidad sin inventar una Session temporal.

## 5. Plan aprobado para Fase 7

1. 7.1 contrato operativo;
2. 7.2 persistencia y migración;
3. 7.3 API de Drivers;
4. 7.4 API de Vehicles;
5. 7.5 API de Tracks y Events;
6. 7.6 cierre y evidencia de `v0.2`.

## 6. Punto de aprobación

Al aprobar este reporte comienza el Bloque 7.2. Ese bloque será el inicio del
código de Fase 7: enums, modelos SQLAlchemy, constraints, migración Alembic y
pruebas de persistencia.
