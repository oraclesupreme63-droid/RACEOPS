# ADR-006 — Auditoría selectiva, no event sourcing

- **Estado:** Aceptado
- **Fecha:** 2026-10-22

## Contexto

Algunas decisiones sensibles deben atribuirse, pero registrar cada cambio
como evento elevaría considerablemente la complejidad.

## Decisión

Mantener tablas de estado normales e `audit_entries` sólo para acciones
seleccionadas: roles, bloqueo/corrección de resultados, Visibility y cambios
operativos críticos. Una entrada crítica comparte la transacción del cambio.

## Consecuencias

- Existe trazabilidad donde aporta seguridad.
- El audit no reconstruye todo el sistema ni copia objetos completos.
- Agregar un evento auditado requiere justificar sensibilidad y retención.

