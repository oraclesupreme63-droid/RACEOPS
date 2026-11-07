# RaceOps — Modelo de visibilidad

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G3
- **Enfoque:** RBAC con ownership, relación y reglas explícitas
- **Fuera de alcance:** Motor ABAC genérico

## 2. Objetivo

Entregar la información necesaria sin asumir que centralización significa
visibilidad universal.

## 3. Orden de decisión

Toda lectura o modificación sigue esta secuencia:

```text
1. ¿El User está autenticado y activo?
        ↓
2. ¿Tiene TeamMembership activa?
        ↓
3. ¿El recurso pertenece al mismo Team?
        ↓
4. ¿Su Role permite la operación?
        ↓
5. ¿La relación con el recurso lo permite?
        ↓
6. ¿Visibility permite leer el registro?
        ↓
7. ¿Qué campos deben filtrarse?
        ↓
8. Ejecutar o denegar sin filtrar existencia
```

Superar un paso no omite los siguientes.

## 4. Niveles

### TEAM

Disponible para miembros activos del Team, sujeto a alcance funcional. Un
Driver no obtiene por ello datos de otros pilotos.

### ROLE_RESTRICTED

Disponible únicamente para Roles o destinatarios declarados. Requiere una
lista no vacía de Roles permitidos.

### ENGINEERING_CONFIDENTIAL

Disponible para Engineer autorizado. Administrator y Team Manager no lo
reciben automáticamente. Driver nunca lo recibe en V1.

## 5. Relación con el recurso

Además del Role:

- Driver necesita estar vinculado al Driver Profile y asignado a Session;
- responsable de Action puede consultar y actualizar su Action autorizada;
- destinatario de Priority puede consultarla;
- autoría no concede acceso perpetuo si cambia la pertenencia al Team;
- acceso a Session no concede acceso automático a todos sus registros.

## 6. Valores predeterminados propuestos

| Información | Visibilidad predeterminada | Observación |
|---|---|---|
| Metadata de Event/Session | `TEAM` | Driver sólo dentro de su alcance |
| Laps y Sectors | `TEAM` | Driver sólo propios/autorizados |
| Conditions | `TEAM` | Sin detalles restringidos adicionales |
| Driver Feedback | `ROLE_RESTRICTED` | Driver afectado, Engineer y Team Manager |
| Observation | `ROLE_RESTRICTED` | Engineer, Mechanic y Team Manager por defecto |
| Session Analysis technical detail | `ENGINEERING_CONFIDENTIAL` | Resumen autorizado separado |
| Hypothesis técnica | `ENGINEERING_CONFIDENTIAL` | Puede generarse resumen autorizado |
| Priority | `ROLE_RESTRICTED` | Destinatario y coordinadores autorizados |
| Action | `ROLE_RESTRICTED` | Responsable y coordinadores autorizados |
| Action confidential detail | `ENGINEERING_CONFIDENTIAL` | `public_summary` separado |
| Action Outcome | Hereda protección de Action y evidencia | Nunca amplía acceso automáticamente |
| Maintenance Record P1 | `ROLE_RESTRICTED` | Mechanic, Engineer y Team Manager autorizados |

Estos valores son conservadores y provisionales. Nueva investigación puede
ajustarlos sin eliminar las garantías mínimas.

## 7. Seguridad por campo

Cuando un registro combina información para públicos diferentes se separan
campos:

| Registro | Campo compartible | Campo restringido |
|---|---|---|
| Session Analysis | `authorized_summary` | `technical_detail` |
| Action | `public_summary` | `confidential_detail` |
| Report | datos autorizados | elementos omitidos antes de serializar |

No se enviará el campo restringido al cliente para después ocultarlo con
CSS o lógica de interfaz.

## 8. Lectura y escritura son permisos distintos

- Poder consultar no implica poder modificar.
- Ser destinatario de Priority no permite editar su origen técnico.
- Responsable de Action puede actualizar ejecución, no necesariamente
  editar Hypothesis.
- Driver puede crear feedback propio, no editar análisis de Engineer.
- Administrator puede cambiar Role, no leer contenido técnico por defecto.

## 9. Listados, búsquedas y reportes

- El filtrado ocurre antes de paginar y contar resultados visibles.
- Los conteos no incluyen registros invisibles para el actor.
- Un identificador conocido no evita la autorización.
- Un recurso no autorizado utiliza una respuesta que no confirme su
  existencia cuando corresponda.
- Exportaciones y vistas imprimibles aplican las mismas políticas.
- El historial de una entidad desactivada continúa filtrado.

## 10. Cambios de visibilidad

Cambiar Visibility es una operación sensible:

- requiere permiso explícito;
- no puede asignar `ENGINEERING_CONFIDENTIAL` a Driver;
- registra actor y momento;
- reducir visibilidad no borra historia;
- ampliar visibilidad obliga a validar que los campos compartidos no
  contengan secretos técnicos.

## 11. Pruebas obligatorias

Para cada recurso protegido se probará:

1. actor permitido;
2. Role incorrecto;
3. Team diferente;
4. Driver no asignado;
5. Visibility incompatible;
6. serialización sin campos restringidos;
7. listado, conteo y búsqueda;
8. modificación no autorizada;
9. acceso tras desactivación;
10. reporte adaptado al rol.

## 12. Limitaciones conscientes

V1 no incluye:

- políticas creadas libremente por usuarios;
- expresiones ABAC arbitrarias;
- permisos por cada campo configurables desde UI;
- compartición pública;
- enlaces anónimos;
- acceso entre Teams.

Estas exclusiones mantienen implementable y auditable la seguridad inicial.
