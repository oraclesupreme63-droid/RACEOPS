# RaceOps — Contrato de Condition Snapshot

## Propósito

Condition Snapshot conserva el contexto ambiental conocido de una Session sin
convertir RaceOps en un servicio meteorológico ni obligar captura manual
excesiva. En P0 existe como máximo un snapshot por Session y todos sus datos
contextuales son opcionales.

Ausencia significa información desconocida; nunca se transforma en cero.

## Campos

| Campo | Regla |
|---|---|
| `ambient_temperature` | decimal opcional; requiere unidad |
| `ambient_temperature_unit` | texto explícito de hasta 24 caracteres |
| `track_temperature` | decimal opcional; requiere unidad |
| `track_temperature_unit` | texto explícito de hasta 24 caracteres |
| `weather` | descripción breve opcional |
| `track_condition` | condición general breve y opcional |
| `source` | origen opcional cuando sea conocido |

El sistema no impone Celsius, Fahrenheit ni otro catálogo universal. El par
valor–unidad conserva significado sin asumir la categoría. Al menos una
condición real debe estar presente; `source` por sí solo no crea un snapshot.

## Cardinalidad e integridad

- una Session puede tener cero o un Condition Snapshot;
- la FK compuesta Session–Team impide mezclar equipos;
- crear un segundo snapshot produce `409 condition_snapshot_exists`;
- una actualización que rompa un par valor–unidad o vacíe el snapshot produce
  `422 invalid_condition_snapshot`;
- no existe DELETE normal;
- las escrituras bloquean la Session para serializar creación y actualización.

Results `LOCKED` protege Laps y Sectors según RF-042. No bloquea Conditions
porque los requisitos no extienden esa regla al contexto ambiental. Esta
decisión queda explícita y podrá revisarse si entrevistas posteriores exigen
un cierre conjunto.

## Autorización

| Rol | Leer | Crear/actualizar |
|---|---:|---:|
| Administrator | Team | Sí |
| Team Manager | Team | Sí |
| Engineer | Team | Sí |
| Mechanic | Team | Sí |
| Driver | Sólo Session asignada | No |

La API usa permisos separados `READ_CONDITIONS` y `WRITE_CONDITIONS`. Un UUID
ajeno o una Session no relacionada se oculta como `404 resource_not_found`.

## API

```text
POST  /api/v1/sessions/{session_id}/conditions
GET   /api/v1/sessions/{session_id}/conditions
PATCH /api/v1/sessions/{session_id}/conditions
```

No existe dependencia de una integración externa. La captura manual funciona
con uno o varios campos conocidos y conserva los demás como `null`.

## Evidencia

- **Parcialmente respaldado:** temperatura, clima y estado de pista aportan
  contexto a la lectura de una Session.
- **Respaldado por baja fricción:** se capturan sólo valores conocidos.
- **Hipótesis:** un snapshot por Session es suficiente en P0.
- **Rechazado en este bloque:** clima automático, históricos meteorológicos,
  campos especializados universales y múltiples snapshots temporales.
