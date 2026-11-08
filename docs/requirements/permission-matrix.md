# RaceOps — Matriz de roles y permisos

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparada para Gate G2
- **Naturaleza:** Provisional y basada en menor privilegio
- **Actores:** Administrator, Team Manager, Engineer, Mechanic y Driver

## 2. Leyenda

| Símbolo | Significado |
|---|---|
| `M` | Administrar: crear, consultar, actualizar y ejecutar transiciones autorizadas |
| `C` | Crear |
| `R` | Consultar |
| `U` | Actualizar dentro de reglas de negocio |
| `O` | Solamente recursos propios, asignados o dirigidos al actor |
| `V` | Depende del nivel de visibilidad del registro |
| `—` | Denegado por defecto |

Todas las capacidades se limitan al equipo activo.

## 3. Matriz funcional P0

| Recurso u operación | Administrator | Team Manager | Engineer | Mechanic | Driver |
|---|---:|---:|---:|---:|---:|
| Usuarios y roles | `M` | `R` | — | — | `O:R` |
| Configuración del equipo | `M` | `R` | `R` | `R` | `R` |
| Pilotos | `M` | `M` | `R` | `R` | `O:R` |
| Vehículos y estado básico | `M` | `M` | `R` | `R` | `O:R` |
| Pistas | `M` | `M` | `C/R/U` | `R` | `R` |
| Eventos | `M` | `M` | `C/R/U` | `R` | `O:R` |
| Crear sesión y asignar recursos | `M` | `M` | `C/R/U` | `R` | `O:R` |
| Cambiar ciclo de vida de sesión | `M` | `M` | `U` | — | — |
| Registrar vueltas y sectores | `M` | `M` | `C/R/U` | `R` | `O:R` |
| Bloquear resultados | `M` | `U` | `U` | — | — |
| Registrar condiciones | `C/R/U` | `C/R/U` | `C/R/U` | `C/R/U` | `O:R` |
| Feedback propio | `V:R` | `V:R` | `V:R` | `V:R` | `O:C/R/U` |
| Feedback comunicado por Driver | `V:R` | `C/R` | `C/R/U` | `C/R` | `O:R` |
| Observaciones | `V:R` | `V:R` | `V:C/R/U` | `V:C/R/U` | `O,V:R` |
| Análisis e hipótesis | `V:R` | `V:R` | `V:M` | `V:R` | `O,V:R` |
| Crear prioridades | `V:R` | `V:C/R` | `V:C/R/U` | `V:R` | `O,V:R` |
| Consultar prioridades asignadas | `V:R` | `V:R` | `O,V:R` | `O,V:R` | `O,V:R` |
| Crear acciones | `V:R` | `V:C/R/U` | `V:C/R/U` | `V:C/R` | `O,V:R` |
| Actualizar acción asignada | `V:R` | `V:U` | `O,V:U` | `O,V:U` | `O,V:U` |
| Evaluar acción y conclusión | `V:R` | `V:C/R` | `V:C/R/U` | `V:C/R` | `O,V:R` |
| Resumen e historial | `V:R` | `V:R` | `V:R` | `V:R` | `O,V:R` |

Los permisos marcados para Administrator permiten operación administrativa
dentro del equipo, pero nunca anulan el filtrado de contenido confidencial.

## 4. Matriz de visibilidad

| Nivel | Administrator | Team Manager | Engineer | Mechanic | Driver |
|---|---:|---:|---:|---:|---:|
| `TEAM` | Sí | Sí | Sí | Sí | Sí, dentro de su alcance |
| `ROLE_RESTRICTED` | Sólo si figura como rol destinatario | Sólo si figura como rol destinatario | Según roles autorizados | Según roles autorizados | Sólo si está dirigido a Driver |
| `ENGINEERING_CONFIDENTIAL` | No por defecto | No por defecto | Sí | Sólo mediante autorización explícita | No |

## 5. Reglas de autorización

### PM-001 — Aislamiento de equipo

Si el recurso no pertenece al equipo activo, la operación se deniega aunque
el identificador sea válido.

### PM-002 — Menor privilegio

Una operación no incluida expresamente se considera denegada.

### PM-003 — Filtrado antes de serializar

Los campos y relaciones no autorizados se eliminan antes de producir la
respuesta. No basta con ocultarlos visualmente.

### PM-004 — No revelar existencia

Una búsqueda no revelará que existe un recurso confidencial cuando el actor
no tiene permiso para conocerlo.

### PM-005 — Alcance del Driver

El Driver sólo accede a sesiones que tenga asignadas, su propio feedback,
sus resultados autorizados y prioridades dirigidas a él.

### PM-006 — Administración sin lectura técnica

Administrator puede administrar cuentas sin acceder automáticamente al
contenido técnico confidencial.

### PM-007 — Separación entre ejecución y resultado

Completar una acción no autoriza declararla exitosa. La evaluación necesita
una sesión o evidencia posterior.

### PM-008 — Auditoría de cambios sensibles

Bloqueos, correcciones posteriores, cambios de rol y excepciones de acceso
registran actor y fecha; cuando corresponda también justificación.

## 6. Mantenimiento P1

| Operación | Administrator | Team Manager | Engineer | Mechanic | Driver |
|---|---:|---:|---:|---:|---:|
| Registrar mantenimiento | `R` | `C/R` | `C/R` | `M` | — |
| Cambiar a `MAINTENANCE` o `UNAVAILABLE` | `U` | `U` | `U` | `U` | — |
| Devolver a `READY` | `U` | `U` | `U` autorizado | `U` autorizado | — |
| Consultar historial | `V:R` | `V:R` | `V:R` | `V:R` | Resumen autorizado |

## 7. Decisiones provisionales

- V1 inicia con un rol principal por membresía; varios roles quedan como
  decisión de modelado pendiente.
- `ENGINEERING_CONFIDENTIAL` es inaccesible para Driver sin excepciones.
- Team Manager y Administrator no reciben acceso técnico confidencial por
  jerarquía organizacional.
- Engineer y Team Manager pueden bloquear resultados en la propuesta
  inicial; esto deberá validarse con equipos reales.

## 8. Casos negativos obligatorios

Las pruebas deberán comprobar, como mínimo:

- acceso cruzado entre equipos;
- Driver intentando consultar setup confidencial;
- usuario desactivado intentando iniciar sesión;
- recurso propio con rol insuficiente;
- recurso permitido que referencia contenido restringido;
- búsqueda que pudiera revelar identificadores confidenciales;
- modificación de resultados bloqueados;
- escalamiento de rol no autorizado.

## 9. Evidencia de implementación

La base ejecutable de esta matriz se implementó en el Bloque 6.5 mediante:

- `Permission` y asignaciones inmutables por `Role`;
- denegación predeterminada para capacidades no concedidas;
- dependencia FastAPI que devuelve el actor actual autorizado;
- separación entre `403 insufficient_permissions` y el `404` utilizado para
  ocultar recursos de otro Team;
- pruebas positivas y negativas para los cinco Roles.

Los permisos relacionados con ownership, Session, Driver y Action se
completarán al existir esos recursos. La tabla continúa siendo la fuente de
verdad; la implementación no convierte una capacidad general en autorización
para omitir relación, Visibility o invariantes del recurso.
