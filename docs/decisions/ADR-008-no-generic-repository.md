# ADR-008 — Sin repository genérico

- **Estado:** Aceptado
- **Fecha:** 2026-10-22

## Contexto

Un wrapper CRUD universal sobre SQLAlchemy ocultaría capacidades útiles sin
representar lenguaje o reglas del dominio.

## Decisión

Servicios simples pueden usar la Session inyectada. Se crean repositories o
query objects específicos sólo para consultas reutilizadas, locking,
persistencia compleja o proyecciones de reporting.

## Consecuencias

- Menos abstracciones y archivos ceremoniales.
- Las consultas importantes permanecen nombradas y probables.
- Si aparece duplicación estable, se extrae después con evidencia.

