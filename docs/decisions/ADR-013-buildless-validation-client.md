# ADR-013 — Cliente de validación sin proceso de compilación

- **Estado:** Aceptado
- **Fecha:** 2026-11-12

## Contexto

La Fase 9 necesita observar a usuarios realizando el Session Learning Loop.
Swagger permite verificar contratos HTTP, pero no la claridad, velocidad ni
fricción del recorrido por Role. Construir ahora una aplicación frontend
completa introduciría dependencias y decisiones que pertenecen a la Fase 12.

## Decisión

Implementar un cliente web delgado con HTML, CSS y JavaScript nativos,
empaquetado dentro de RaceOps y servido por el mismo proceso FastAPI bajo
`/app/`.

El cliente:

- consume exclusivamente la API y autorización reales;
- conserva el access token sólo en `sessionStorage`;
- adapta controles y contenido al Role sin asumir autoridad de seguridad;
- cubre únicamente el Session Learning Loop que será validado;
- funciona en computadora y teléfono sin un proceso Node adicional.

## Consecuencias

- La prueba local requiere un solo origen, un solo contenedor de aplicación y
  ningún ajuste CORS adicional.
- Las reglas de negocio y confidencialidad permanecen en el backend.
- El cliente puede reemplazarse en la Fase 12 sin migrar lógica de dominio.
- No se incorporan todavía enrutado avanzado, estado global, diseño completo
  del producto ni una estrategia de frontend para producción.

## Evidencia y límites

- **Respaldado:** la API y el flujo vertical ya cuentan con pruebas de
  aceptación; el cliente puede tratarlos como fuente de verdad.
- **Parcialmente respaldado:** un diseño responsive reduce la barrera para
  pruebas móviles, pero su facilidad real debe observarse con participantes.
- **Hipótesis:** el cliente es suficientemente rápido y claro para operar
  entre sesiones. El Bloque 9.4 deberá confirmarlo o rechazarlo.
