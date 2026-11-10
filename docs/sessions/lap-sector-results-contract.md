# RaceOps — Contrato de Laps, Sectors y métricas

## Propósito y alcance

Este contrato materializa el primer dato de rendimiento de RaceOps sin
convertir la plataforma en un sistema de adquisición de telemetría. Una Lap es
el resultado canónico de una vuelta dentro de una Session. Sus Sectors son
opcionales y variables porque distintas pistas y categorías usan divisiones
diferentes.

No se importan canales en vivo, no se obliga a que los Sectors sumen la Lap y
no se generan recomendaciones automáticas.

## Modelo

### Lap

- `lap_number`: entero positivo y único dentro de Session;
- `duration_us`: entero positivo en microsegundos;
- `source`: `MANUAL`, `IMPORTED` u `OTHER`;
- `classification`: `VALID`, `INVALID`, `OUT_LAP`, `IN_LAP` o `INCOMPLETE`;
- sólo `VALID` participa en métricas principales.

### Sector

- pertenece a una sola Lap;
- `sector_order` es positivo y único dentro de la Lap;
- `duration_us` es positivo y usa microsegundos;
- `status`: `VALID`, `INVALID` o `INCOMPLETE`;
- la cantidad es variable y puede ser cero.

Las referencias compuestas Session–Team y Lap–Team impiden mezclar datos entre
equipos. No existe DELETE normal para preservar historia.

## Métricas reproducibles

El resumen cuenta todas las Laps, pero calcula rendimiento exclusivamente con
las clasificadas `VALID`:

- mejor vuelta: duración mínima elegible;
- promedio: media aritmética redondeada al microsegundo más cercano, con
  mitades hacia arriba;
- consistencia: desviación estándar poblacional de las duraciones elegibles,
  redondeada de igual forma;
- con cero vueltas elegibles, mejor vuelta, promedio y consistencia son `null`;
- con una vuelta elegible, consistencia es `null` porque no hay variación
  suficiente que comparar.

Los cálculos se realizan con enteros para evitar resultados dependientes de
punto flotante. Esta métrica de consistencia es una decisión P0 explícita y
podrá revisarse con evidencia de usuarios.

## Autorización y cierre

`READ_RESULTS` permite leer a todos los Roles del Team. Driver sólo lee
resultados de Sessions a las que está asignado mediante su Driver Profile.

`WRITE_RESULTS` corresponde a Administrator, Team Manager y Engineer.
Mechanic y Driver no escriben Laps ni Sectors en P0. Cada escritura bloquea la
fila de Session y comprueba `results_status`; cuando es `LOCKED`, se responde
`409 results_locked` sin cambios parciales.

## API

```text
POST  /api/v1/sessions/{session_id}/laps
GET   /api/v1/sessions/{session_id}/laps
GET   /api/v1/sessions/{session_id}/results-summary
GET   /api/v1/laps/{lap_id}
PATCH /api/v1/laps/{lap_id}
POST  /api/v1/laps/{lap_id}/sectors
GET   /api/v1/laps/{lap_id}/sectors
GET   /api/v1/sectors/{sector_id}
PATCH /api/v1/sectors/{sector_id}
```

Crear una Lap puede incluir Sectors y se confirma como una sola transacción.
Los listados conservan orden estable. Los conflictos públicos son
`lap_number_conflict`, `sector_order_conflict` y `results_locked`.

## Clasificación de decisiones

- **Respaldado por evidencia:** registrar vuelta/sectores y conservar contexto
  alrededor de las herramientas de telemetría.
- **Parcialmente respaldado:** utilidad de métricas simples para todos los
  equipos.
- **Hipótesis:** clasificación universal mínima y desviación estándar como
  lectura de consistencia.
- **Rechazado en v0.3:** schema universal de telemetría, ingestión en vivo,
  inferencias automáticas y edición después del bloqueo.
