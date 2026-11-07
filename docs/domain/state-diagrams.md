# RaceOps — Diagramas de estado

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G3
- **Propósito:** Definir transiciones normales y evitar estados ambiguos

## 2. Session Status

```mermaid
stateDiagram-v2
    [*] --> PLANNED: crear
    PLANNED --> ACTIVE: iniciar
    PLANNED --> CANCELLED: cancelar
    ACTIVE --> PAUSED: pausar
    PAUSED --> ACTIVE: reanudar
    ACTIVE --> COMPLETED: terminar actividad
    PAUSED --> COMPLETED: terminar actividad
    ACTIVE --> CANCELLED: cancelar
    PAUSED --> CANCELLED: cancelar
    COMPLETED --> [*]
    CANCELLED --> [*]
```

Reglas:

- sólo actores autorizados cambian el estado;
- `started_at` se fija al primer paso a `ACTIVE`;
- `ended_at` se fija al pasar a `COMPLETED` o `CANCELLED`;
- `COMPLETED` y `CANCELLED` no se reabren mediante el flujo normal;
- una corrección excepcional futura requiere autorización y auditoría.

## 3. Results Status

```mermaid
stateDiagram-v2
    [*] --> OPEN: crear Session
    OPEN --> LOCKED: bloquear resultados
    LOCKED --> [*]
```

Reglas:

- el estado es independiente de Session Status;
- una Session `COMPLETED` puede conservar resultados `OPEN`;
- el bloqueo normal sólo ocurre después de `COMPLETED` o `CANCELLED`;
- `LOCKED` rechaza nuevas Laps y Sectors por el flujo normal;
- quien bloquea y cuándo quedan registrados;
- una corrección posterior es P1 y necesita motivo y permiso.

## 4. Vehicle Status

```mermaid
stateDiagram-v2
    [*] --> READY
    READY --> MAINTENANCE: retirar para intervención
    READY --> UNAVAILABLE: declarar no disponible
    READY --> RETIRED: retirar definitivamente
    MAINTENANCE --> READY: liberar explícitamente
    MAINTENANCE --> UNAVAILABLE: falla pendiente
    MAINTENANCE --> RETIRED: retirar
    UNAVAILABLE --> READY: liberar explícitamente
    UNAVAILABLE --> MAINTENANCE: iniciar intervención
    UNAVAILABLE --> RETIRED: retirar
    RETIRED --> [*]
```

Reglas:

- sólo `READY` permite una nueva Session;
- terminar Maintenance Record no produce `READY` automáticamente;
- `RETIRED` es terminal mediante el flujo normal;
- las transiciones de mantenimiento son P1, mientras la validación de
  disponibilidad para asignación permanece P0.

## 5. Action Status

```mermaid
stateDiagram-v2
    [*] --> PROPOSED
    PROPOSED --> PLANNED: aceptar
    PROPOSED --> CANCELLED: descartar
    PLANNED --> IN_PROGRESS: iniciar
    PLANNED --> CANCELLED: cancelar
    IN_PROGRESS --> COMPLETED: terminar ejecución
    IN_PROGRESS --> CANCELLED: cancelar con motivo
    COMPLETED --> [*]
    CANCELLED --> [*]
```

Reglas:

- el responsable o un coordinador autorizado actualiza ejecución;
- `COMPLETED` no crea automáticamente un Action Outcome;
- la evaluación puede permanecer `NOT_EVALUATED`.

## 6. Hypothesis Status

```mermaid
stateDiagram-v2
    [*] --> PROPOSED
    PROPOSED --> SUPPORTED: evidencia posterior
    PROPOSED --> PARTIALLY_SUPPORTED: evidencia mixta
    PROPOSED --> REJECTED: evidencia contraria
    PROPOSED --> INCONCLUSIVE: evidencia insuficiente
    SUPPORTED --> [*]
    PARTIALLY_SUPPORTED --> [*]
    REJECTED --> [*]
    INCONCLUSIVE --> [*]
```

Una evaluación posterior adicional puede revisar un estado evaluado, pero
debe conservar la conclusión anterior y registrar nueva evidencia. La
implementación de revisiones completas puede permanecer P1; P0 conserva al
menos la evaluación vigente y su relación.

## 7. User y Membership

```mermaid
stateDiagram-v2
    [*] --> ACTIVE
    ACTIVE --> INACTIVE: desactivar
    INACTIVE --> ACTIVE: reactivar autorizado
```

Desactivar acceso no elimina autoría histórica.

## 8. Driver

```mermaid
stateDiagram-v2
    [*] --> ACTIVE
    ACTIVE --> INACTIVE: desactivar
    INACTIVE --> ACTIVE: reactivar
```

Un Driver inactivo conserva historia, pero no puede asignarse a una nueva
Session.

## 9. Estados que no deben combinarse

- Session Status no reemplaza Results Status.
- Action Status no reemplaza Action Outcome.
- Vehicle Status no se deriva automáticamente del último Maintenance Record.
- Hypothesis Status no se deriva automáticamente de una sola métrica.
