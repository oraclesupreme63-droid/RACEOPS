# RaceOps — Guía de API

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G4
- **Estilo:** REST JSON sobre HTTP
- **Base path:** `/api/v1`

## 2. Recursos y rutas

- Sustantivos plurales en minúsculas: `/drivers`, `/vehicles`, `/events`.
- UUID como identificadores externos.
- Rutas anidadas sólo cuando expresan contexto útil:
  `/events/{event_id}/sessions` o `/sessions/{session_id}/laps`.
- Cada recurso conserva también una ruta canónica cuando sea necesaria.
- No se colocan Roles o Team IDs confiables dentro del body para decidir
  autorización; se derivan del actor autenticado y el contexto permitido.

## 3. Comandos de estado

Las transiciones no se realizan permitiendo escribir libremente el campo
`status`. Utilizan comandos explícitos:

```text
POST /api/v1/sessions/{id}/start
POST /api/v1/sessions/{id}/pause
POST /api/v1/sessions/{id}/resume
POST /api/v1/sessions/{id}/complete
POST /api/v1/sessions/{id}/cancel
POST /api/v1/sessions/{id}/lock-results
POST /api/v1/actions/{id}/complete
```

Esto hace visibles reglas, permisos y conflictos de estado.

## 4. Métodos y respuestas

| Operación | Método | Éxito típico |
|---|---|---:|
| Crear recurso | POST | `201 Created` + `Location` |
| Consultar | GET | `200 OK` |
| Reemplazo total poco frecuente | PUT | `200 OK` o `204 No Content` |
| Actualización parcial permitida | PATCH | `200 OK` |
| Comando de dominio | POST | `200 OK` o `204 No Content` |
| Desactivar/archivar | POST command o PATCH | `200 OK` |
| Borrado físico normal | No disponible | — |

## 5. Formatos

- Fechas: `YYYY-MM-DD`.
- Instantes: ISO 8601 en UTC con sufijo `Z`.
- Duraciones de vuelta y sector: entero en microsegundos mediante campos
  terminados en `_us`.
- Valores medidos: valor decimal y unidad explícita.
- Enums: strings estables en mayúsculas.
- Campos desconocidos o ausentes: `null` u omisión documentada; nunca cero
  inventado.
- JSON usa `snake_case` para mantener consistencia con Python.

## 6. Paginación y filtros

V1 utiliza `limit` y `offset`, de acuerdo con las APIs operativas ya
publicadas:

- `limit` tiene valor predeterminado 50 y máximo 100;
- `offset` inicia en 0;
- respuesta incluye `items`, `limit`, `offset` y `total`;
- `total` se calcula después de autorización;
- filtros se documentan y usan parámetros explícitos;
- orden predeterminado es estable e incluye desempate por ID.

Si el volumen real exige cursor pagination, se registrará como cambio
posterior, no como complejidad preventiva.

## 7. Errores y seguridad

- Errores usan `application/problem+json` según RFC 9457.
- `401` significa falta o invalidez de autenticación.
- `403` se usa cuando el actor puede conocer el recurso pero no ejecutar la
  operación.
- `404` se utiliza para recurso inexistente o cuya existencia no debe
  revelarse.
- `409` representa conflictos de estado, unicidad o concurrencia.
- `422` representa entrada sintácticamente válida en HTTP pero inválida para
  el schema.
- `500` nunca devuelve stack trace ni detalles internos.

## 8. Contratos de actualización

- Schemas de create y update son diferentes.
- Campos inmutables no aparecen en update.
- El servidor ignora nunca silenciosamente un campo prohibido; lo rechaza.
- Las respuestas se construyen con schemas específicos por audiencia cuando
  existen diferencias de confidencialidad.
- La API no devuelve ORM objects directamente.

## 9. Concurrencia

- Transiciones verifican el estado actual dentro de la transacción.
- Operaciones con límites, como tres Main Priorities, usan locking o una
  estrategia de constraint que evite carreras.
- Conflictos detectados producen `409` y no sobrescriben silenciosamente.
- Optimistic versioning se añadirá a aggregates con riesgo real de edición
  concurrente si las pruebas lo justifican.

## 10. OpenAPI

- FastAPI genera el documento OpenAPI.
- Cada endpoint declara resumen, descripción, responses y tags.
- Los errores de dominio documentan su `code` estable.
- Ejemplos no incluyen secretos ni datos reales.
- El OpenAPI generado se prueba para evitar rutas duplicadas o schemas
  accidentales.

## 11. Compatibilidad

- Cambios incompatibles requieren una versión nueva o migración documentada.
- Agregar campos opcionales es compatible.
- Cambiar significado, tipo o visibilidad de un campo requiere revisión.
- `/api/v1` no implica mantener indefinidamente múltiples versiones antes
  de que exista un consumidor real.

## 12. Referencia

- [RFC 9457 — Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html)
