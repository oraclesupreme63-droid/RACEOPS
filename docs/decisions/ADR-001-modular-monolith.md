# ADR-001 — Monolito modular

- **Estado:** Aceptado
- **Fecha:** 2026-10-22

## Contexto

RaceOps es un proyecto estudiantil con un primer flujo vertical todavía por
validar. Microservicios aumentarían despliegues, contratos distribuidos,
observabilidad y consistencia sin resolver un problema demostrado.

## Decisión

Construir una sola aplicación FastAPI y una sola base PostgreSQL, divididas
en módulos con ownership y dependencias explícitas.

## Consecuencias

- Casos de uso entre módulos comparten transacción cuando sea necesario.
- Despliegue y pruebas son más simples.
- Los límites se vigilan mediante estructura e imports, no mediante red.
- Sólo evidencia de escalamiento o autonomía operativa justificará separar
  un servicio.

