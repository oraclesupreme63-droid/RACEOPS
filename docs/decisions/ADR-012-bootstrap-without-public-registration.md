# ADR-012 — Bootstrap administrativo sin registro público

- **Estado:** Propuesto para aprobación
- **Fecha:** 2026-11-07

## Contexto

RaceOps necesita una primera identidad administrativa para ejecutar y probar
el MVP. No existe evidencia que justifique registro público, invitaciones,
verificación de email, recuperación de cuenta o onboarding SaaS.

Crear esos flujos antes del Session Learning Loop aumentaría alcance y riesgo
sin validar el producto principal.

## Decisión

P0 no ofrecerá registro público. Un comando local creará el primer Team, User
y TeamMembership `ADMINISTRATOR` dentro de una sola transacción.

El comando solicitará el password mediante entrada oculta y no lo aceptará
como argumento visible. No imprimirá credenciales, hashes ni tokens. La futura
gestión HTTP de usuarios, estados y roles permanece P1 y requerirá autorización
de Administrator.

## Consecuencias

- El entorno puede inicializarse de forma reproducible y segura.
- El MVP no depende de servicios de email ni flujos de invitación.
- La creación inicial requiere acceso autorizado al entorno de ejecución.
- Antes de uso comercial deberá existir un onboarding y recuperación de acceso
  explícitamente diseñados y probados.

## Alternativas descartadas

- **Endpoint público de registro:** crea superficie de abuso y decisiones SaaS
  todavía no validadas.
- **Usuario administrativo hardcoded:** expondría credenciales y rompería la
  configuración por entorno.
- **Insertar filas manualmente:** evita reglas, hashing y atomicidad de la
  aplicación.

