# RaceOps — Actores del sistema

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G2
- **Fase:** Ingeniería de requerimientos
- **Base:** Gate G1 aprobado condicionalmente

## 2. Propósito

Definir quién interactúa con RaceOps, qué resultado busca y cuáles son sus
límites. Los actores describen responsabilidades de producto; no equivalen
necesariamente a tablas de base de datos.

## 3. Principios

- Todo actor humano autenticado pertenece a un equipo.
- Una operación se evalúa por equipo, rol, relación con el recurso y nivel
  de visibilidad.
- Tener acceso administrativo no concede automáticamente acceso a contenido
  técnico confidencial.
- Los permisos se aplican en el servidor, no solamente en la interfaz.
- La matriz es provisional hasta entrevistar directamente a Team Managers y
  Mechanics.

## 4. Actores humanos

### ACT-001 — Administrator

**Objetivo:** mantener identidad, membresías, roles y configuración básica
del equipo.

**Responsabilidades:**

- gestionar usuarios y roles autorizados;
- activar o desactivar accesos;
- mantener configuración del equipo;
- apoyar la administración de datos maestros.

**Límite:** no obtiene automáticamente acceso al contenido
`ENGINEERING_CONFIDENTIAL` por administrar cuentas.

### ACT-002 — Team Manager

**Objetivo:** coordinar eventos, recursos y estado general de la operación.

**Responsabilidades:**

- gestionar pilotos, vehículos, pistas y eventos;
- crear o supervisar sesiones;
- consultar estado general, acciones e incidentes permitidos;
- verificar que existen responsables y próximos pasos.

**Límite:** no necesita automáticamente canales de telemetría ni detalles
de setup confidencial.

### ACT-003 — Engineer / Data Engineer

**Objetivo:** relacionar feedback, resultados y observaciones para formular
hipótesis y decidir acciones.

**Responsabilidades:**

- registrar o revisar resultados de sesión;
- registrar feedback comunicado verbalmente;
- crear observaciones, análisis e hipótesis;
- definir prioridades y acciones;
- evaluar resultados en sesiones posteriores;
- manejar contenido técnico confidencial autorizado.

### ACT-004 — Mechanic

**Objetivo:** conocer síntomas y acciones mecánicas que le corresponden.

**Responsabilidades P0:**

- consultar sesiones, vehículos y acciones autorizadas;
- registrar observaciones técnicas o mecánicas;
- actualizar acciones que tenga asignadas.

**Responsabilidades P1:**

- registrar inspecciones, reparaciones y mantenimiento;
- cambiar estados operativos cuando esté autorizado;
- consultar historial de mantenimiento.

La separación P0/P1 procede de la condición aprobada en G1.

### ACT-005 — Driver

**Objetivo:** registrar lo experimentado y consultar información útil para
su siguiente sesión.

**Responsabilidades:**

- consultar sus sesiones asignadas;
- registrar feedback propio;
- consultar vueltas, sectores y resúmenes autorizados;
- consultar sus prioridades;
- aportar evidencia posterior cuando corresponda.

**Límite:** no puede consultar información
`ENGINEERING_CONFIDENTIAL` ni datos de otros pilotos sin autorización.

## 5. Actores técnicos

### ACT-006 — Cliente web

Consume la API en nombre de un usuario autenticado. No es una frontera de
seguridad: el servidor vuelve a validar todos los permisos.

### ACT-007 — Reloj del sistema

Proporciona marcas de tiempo para inicio, finalización, bloqueo, creación y
modificación. Durante pruebas deberá ser sustituible o controlable.

### ACT-008 — Fuente externa de resultados

Representa un archivo o sistema externo referenciado por una sesión.

- En P0 no necesita integración automática.
- En P1 puede conservarse una referencia o adjunto autorizado.
- La importación y normalización CSV permanece P2.

## 6. Actor fuera del alcance inicial

### Visitante público

RaceOps V1 no requiere perfiles públicos, resultados públicos ni acceso
anónimo a información del equipo.

## 7. Reglas comunes

1. Un actor solamente opera sobre recursos del equipo activo.
2. El acceso a un recurso no implica acceso a todas sus relaciones.
3. Un Driver queda limitado a sus asignaciones y contenido autorizado.
4. Engineer es el actor principal de análisis e hipótesis.
5. Mechanic es el actor principal de observaciones mecánicas y, en P1, de
   mantenimiento.
6. Team Manager coordina operación, no sustituye automáticamente a
   ingeniería.
7. Administrator gestiona acceso, no obtiene privilegios técnicos por
   defecto.
8. Toda excepción deberá ser explícita, verificable y auditable.

## 8. Dudas pendientes

- ¿Un usuario podrá acumular varios roles dentro del mismo equipo?
- ¿Quién puede bloquear resultados: Team Manager, Engineer o ambos?
- ¿Quién puede devolver un vehículo a `READY` en cada tipo de equipo?
- ¿Qué observaciones necesita consultar el Driver?
- ¿El Team Manager puede consultar setup confidencial mediante permiso
  adicional?

Estas preguntas no bloquean G2 si las reglas conservadoras de menor
privilegio se mantienen como valor predeterminado.

