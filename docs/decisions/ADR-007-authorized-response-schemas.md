# ADR-007 — Consultas y respuestas autorizadas

- **Estado:** Aceptado
- **Fecha:** 2026-10-22

## Contexto

Un Driver puede conocer una dirección de trabajo, pero no necesariamente la
configuración exacta. Filtrar sólo en el frontend expondría datos.

## Decisión

Aplicar ownership y Visibility en las consultas antes de conteo/paginación y
usar DTO/schemas de salida por audiencia. Separar resumen autorizado y
detalle confidencial en el modelo cuando ambos tengan consumidores distintos.

## Consecuencias

- La API no serializa ORM objects directamente.
- Las pruebas negativas son parte del criterio de terminado.
- Puede existir duplicación pequeña de schemas a cambio de límites claros.

