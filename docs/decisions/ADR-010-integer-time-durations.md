# ADR-010 — Duraciones enteras en microsegundos

- **Estado:** Aceptado
- **Fecha:** 2026-10-22

## Contexto

Vueltas y sectores requieren comparación exacta. Los valores binarios de
punto flotante pueden introducir diferencias artificiales.

## Decisión

Representar duraciones como enteros de microsegundos en dominio, API y base
de datos. La presentación formatea el valor sin modificar la fuente.

## Consecuencias

- Orden, resta y agregación son deterministas.
- Los campos de API terminan en `_us` para hacer visible la unidad.
- Importadores futuros normalizan su precisión en el límite de entrada.

