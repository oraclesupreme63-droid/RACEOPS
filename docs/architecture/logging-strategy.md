# RaceOps — Estrategia de logging y auditoría

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G4
- **Salida productiva:** JSON estructurado a `stdout`

## 2. Propósito

Los logs explican la salud y ejecución del sistema. La auditoría conserva
acciones de negocio sensibles. No son el mismo mecanismo y ninguno sustituye
las pruebas o el historial funcional.

## 3. Logging estructurado

Cada petición tendrá `request_id` y, cuando exista, un `trace_id`. Campos
base:

- `timestamp` UTC;
- `level`;
- `service` y `environment`;
- `request_id` / `trace_id`;
- método, plantilla de ruta y status HTTP;
- duración en milisegundos;
- identificadores de User y Team cuando sea seguro;
- nombre del evento y `error_code` cuando apliquen.

Se registrará la plantilla `/sessions/{id}`, no cada URL completa, para
evitar cardinalidad y exposición innecesarias.

## 4. Eventos relevantes

- arranque y cierre de la aplicación;
- resultado de health/readiness;
- autenticación fallida sin password ni token;
- denegación de autorización;
- error de validación resumido;
- transición de estado y resultado;
- conflicto de concurrencia;
- error inesperado con contexto técnico interno;
- latencia de petición y, sólo cuando sea necesario, consulta lenta.

## 5. Datos prohibidos

Nunca se registran:

- passwords o hashes;
- JWT, encabezado `Authorization` o cookies;
- secretos y connection strings;
- cuerpos completos de request/response;
- detalles confidenciales de setup;
- archivos o contenido de telemetría;
- datos personales innecesarios.

Los identificadores son preferibles a nombres libres. Los logs de desarrollo
también respetan estas reglas.

## 6. Niveles

| Nivel | Uso |
|---|---|
| DEBUG | diagnóstico local, desactivado normalmente en producción |
| INFO | ciclo de vida y operaciones exitosas relevantes |
| WARNING | entrada rechazada, auth fallida, conflicto recuperable |
| ERROR | operación fallida que requiere investigación |
| CRITICAL | servicio no puede continuar o existe riesgo de integridad |

Un `4xx` no es automáticamente un error del servidor. Los eventos repetidos
de seguridad pueden elevarse sin almacenar datos sensibles.

## 7. Auditoría de negocio

`audit_entries` conservará solamente acciones seleccionadas:

- cambio de Role o Membership;
- bloqueo de resultados;
- corrección excepcional de datos bloqueados;
- cambio de Visibility;
- cambio manual crítico de disponibilidad del Vehicle;
- liberación posterior a mantenimiento cuando se implemente P1.

Cada entrada contiene actor, Team, acción, tipo e ID del recurso, instante,
motivo cuando corresponda y metadatos mínimos no confidenciales. No se
almacena una copia indiscriminada del objeto ni se implementa event sourcing.

## 8. Fallos y retención

- Una audit entry requerida forma parte de la misma transacción del cambio.
- Un fallo del log de aplicación no debe corromper la operación principal.
- Desarrollo escribe a consola; la plataforma de despliegue administra
  recolección y rotación.
- La retención productiva se decidirá antes de recibir datos reales y se
  documentará según el entorno y las obligaciones aplicables.

## 9. Verificación

Las pruebas capturan logs para comprobar `request_id`, códigos de error y
redacción de secretos. Las acciones auditables comprueban atomicidad entre
cambio y audit entry.

