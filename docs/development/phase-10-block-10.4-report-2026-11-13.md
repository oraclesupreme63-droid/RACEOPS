# Fase 10 — Reporte del Bloque 10.4

**Fecha:** 13 de noviembre de 2026

**Estado:** implementación y verificación dirigida terminadas; pendiente de
CI global y aprobación del propietario

## Resultado

RaceOps ya controla el ciclo de una intervención de mantenimiento sin mezclarlo
con la disponibilidad del Vehicle. Un registro abierto puede corregirse; al
iniciarse deja de ser editable y sólo puede terminar como completado o
cancelado.

## API implementada

- `PATCH /api/v1/maintenance-records/{maintenance_id}`;
- `POST /api/v1/maintenance-records/{maintenance_id}/start`;
- `POST /api/v1/maintenance-records/{maintenance_id}/complete`;
- `POST /api/v1/maintenance-records/{maintenance_id}/cancel`.

Completar exige una conclusión y cancelar exige un motivo. Ningún endpoint
acepta estado o timestamps elegidos por el cliente.

## Reglas protegidas

- sólo `OPEN` permite edición normal;
- `OPEN` puede iniciar, completarse directamente o cancelarse;
- `IN_PROGRESS` puede completarse o cancelarse;
- `COMPLETED` y `CANCELLED` son terminales;
- cada transición usa `SELECT ... FOR UPDATE`;
- recursos de otro Team continúan respondiendo 404;
- Administrator y Driver no obtienen escritura;
- completar o cancelar no cambia el estado del Vehicle.

## Errores estables

- `invalid_maintenance_status_transition` para comandos incompatibles;
- `maintenance_record_locked` para editar un registro terminal;
- `maintenance_responsible_conflict` para un responsable inválido.

## Verificación dirigida

- 17 pruebas unitarias de mantenimiento aprobadas;
- 12 pruebas HTTP de mantenimiento aprobadas contra PostgreSQL;
- prueba concurrente PostgreSQL aprobada: un solo comando terminal gana;
- 33 pruebas enfocadas aprobadas en conjunto;
- Ruff y MyPy aprobados sobre los archivos modificados;
- OpenAPI documenta PATCH y los tres comandos explícitos.

## Verificación global local

- 269 pruebas aprobadas;
- cobertura total de 92.10 % frente al mínimo de 90 %;
- Ruff format, Ruff check y MyPy estricto aprobados;
- `alembic check` sin operaciones pendientes.

La construcción y prueba de humo del contenedor corresponden a CI después del
commit del bloque.

## Límite conservado

Este bloque demuestra consistencia técnica, no uso real por equipos. Session,
Observation y Action todavía no pueden enlazarse mediante la API; esa cadena
causal corresponde al Bloque 10.5.

## Siguiente bloque condicionado

Con aprobación comienza 10.5 — cadena causal: validar y recuperar la relación
Session/Observation/Action/intervención sin permitir cruces de Team, Session o
Vehicle.
