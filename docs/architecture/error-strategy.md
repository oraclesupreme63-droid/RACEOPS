# RaceOps — Estrategia de errores

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G4
- **Formato HTTP:** RFC 9457 `application/problem+json`

## 2. Objetivo

Los errores deben ser útiles para el usuario y diagnosticables para el
equipo sin revelar SQL, stack traces, secretos, tokens ni información cuya
existencia sea confidencial.

## 3. Categorías internas

| Categoría | Ejemplo | HTTP habitual |
|---|---|---:|
| Authentication | token ausente, expirado o inválido | 401 |
| Authorization | rol sin permiso para un recurso visible | 403 |
| Not found / hidden | recurso inexistente o de otro Team | 404 |
| Input validation | campo o formato inválido | 422 |
| Business rule | transición o combinación inválida | 409 |
| Concurrency | estado cambió durante la operación | 409 |
| Unexpected | fallo no clasificado | 500 |

Las excepciones del dominio no dependerán de FastAPI. Un mapper en la capa
HTTP las convertirá al status y cuerpo correspondiente.

## 4. Contrato

Ejemplo:

```json
{
  "type": "https://raceops.local/problems/invalid-state-transition",
  "title": "Invalid state transition",
  "status": 409,
  "detail": "The session cannot be completed from its current state.",
  "instance": "/api/v1/sessions/3f.../commands/complete",
  "code": "SESSION_INVALID_STATE_TRANSITION",
  "trace_id": "01J...",
  "errors": []
}
```

- `code` es estable y consumible por el cliente.
- `detail` puede explicar una corrección segura, pero no revela internals.
- `trace_id` permite localizar el evento en logs.
- `errors` sólo aparece cuando existen errores por campo.
- El texto visible no es el contrato; el cliente decide su traducción.

## 5. Reglas de manejo

- La misma condición produce el mismo `code` en todos los endpoints.
- Un recurso de otro Team responde `404`, no `403`.
- Un duplicate predecible se valida y la unique constraint permanece como
  última defensa.
- Errores de integridad esperados se transforman; no se devuelve el mensaje
  bruto del driver de base de datos.
- Excepciones inesperadas se registran con stack trace sólo en el servidor y
  devuelven un problema genérico `500`.
- Una respuesta de error nunca confirma campos confidenciales.

## 6. Responsabilidad por capa

| Capa | Responsabilidad |
|---|---|
| Pydantic/API | forma, tipos y límites básicos |
| Servicio/política | permisos, estado, invariantes y conflictos |
| Persistencia | integridad y concurrencia final |
| Handler global | traducción segura, `trace_id` y logging |

## 7. Pruebas mínimas

- Cada `code` crítico cuenta con prueba de API.
- Se prueban explícitamente 401, 403, 404 oculto, 409, 422 y 500 seguro.
- Se comprueba que la respuesta no contiene SQL, stack trace, password hash,
  JWT ni detalle técnico confidencial.

## 8. Referencia

- [RFC 9457 — Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html)

