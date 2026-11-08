# RaceOps — Reporte del Bloque 6.5: RBAC y aislamiento

## 1. Estado

- **Fecha:** 8 de noviembre de 2026
- **Fase:** 6 — Identidad y autorización
- **Bloque:** 6.5 — RBAC y aislamiento
- **Resultado:** Implementado, verificado y aprobado por el propietario
- **Aprobación:** 8 de noviembre de 2026
- **Siguiente bloque:** 6.6 — Cierre de la Fase 6

## 2. Resultado implementado

RaceOps cuenta ahora con una capa de autorización reutilizable compuesta por:

- actor actual resuelto desde JWT y PostgreSQL;
- capacidades explícitas mediante `Permission`;
- asignación inmutable de capacidades para cada `Role`;
- denegación predeterminada;
- dependencia FastAPI `require_permission(...)`;
- validación de ownership por Team;
- políticas para los tres niveles de Visibility.

Autenticación responde quién es el actor. Autorización decide qué operación
puede intentar. Team, relación, Visibility e invariantes siguen siendo pasos
independientes y obligatorios.

## 3. Menor privilegio

Se definieron capacidades estables para membresías, configuración, Drivers,
Vehicles, Tracks, Events, Sessions, resultados, condiciones, feedback,
observaciones, análisis, prioridades, acciones, resultados e historial.

La asignación refleja la matriz aprobada. Ejemplos:

- sólo Administrator administra miembros;
- Administrator no puede escribir Analysis ni recibe ingeniería confidencial;
- Engineer puede escribir Analysis;
- Mechanic puede escribir Observation y acciones permitidas;
- Driver puede crear su feedback y actualizar acciones asignadas, pero la
  relación con el recurso deberá comprobarse adicionalmente.

Una capacidad no equivale a acceso universal. `READ_HISTORY`, por ejemplo,
continúa limitado por Team, relación y Visibility.

## 4. Aislamiento entre Teams

Un recurso con `team_id` diferente al Team activo produce el mismo resultado
que un recurso no disponible para el actor:

```text
404 resource_not_found
```

No se utiliza `403` para confirmar que el UUID pertenece a otro equipo. El
`403 insufficient_permissions` se reserva para un actor autenticado que puede
conocer la operación, pero cuyo Role carece de la capacidad requerida.

## 5. Visibility

La política implementa:

### TEAM

- miembro del mismo Team;
- Driver sólo cuando está relacionado con el recurso.

### ROLE_RESTRICTED

- Role incluido expresamente; o
- destinatario/actor relacionado.

### ENGINEERING_CONFIDENTIAL

- Engineer autorizado;
- Mechanic únicamente con autorización explícita;
- Administrator y Team Manager no reciben acceso por jerarquía;
- Driver nunca recibe el detalle en V1.

La evaluación devuelve un booleano para filtrar listados antes de contar o
paginar y ofrece una variante estricta que genera el resultado oculto.

## 6. Pruebas HTTP sin superficie ficticia

No se añadieron endpoints de negocio artificiales. Las pruebas montan rutas
temporales solamente dentro de pytest para comprobar la dependencia real de
FastAPI. Esas rutas no aparecen al ejecutar RaceOps ni en su OpenAPI.

Se verificó:

- Administrator permitido para administrar miembros;
- Team Manager, Engineer, Mechanic y Driver rechazados con `403`;
- configuración básica legible por los cinco Roles;
- cambio de Driver a Administrator efectivo con el mismo token;
- recurso del Team activo accesible;
- UUID de otro Team oculto mediante `404` sin datos del recurso.

## 7. Evidencia de verificación

Resultado local:

- 84 pruebas aprobadas;
- 94.42 % de cobertura, con mínimo obligatorio de 90 %;
- 11 pruebas unitarias nuevas de autorización;
- 2 escenarios HTTP nuevos contra PostgreSQL;
- Ruff format y lint aprobados;
- mypy estricto aprobado en 46 archivos;
- `alembic check` sin operaciones nuevas;
- no se modificó el esquema de base de datos.

## 8. Límites conscientes

La infraestructura de autorización está terminada, pero RaceOps todavía no
tiene Drivers, Vehicles, Events, Sessions, Analysis ni Actions persistidos.
Por ello:

- el aislamiento se probó con una ruta temporal y UUID de Team;
- el filtrado de `technical_detail` se integrará con Analysis en la Fase 8;
- ownership de Driver, destinatarios y responsables se probará con sus
  relaciones reales;
- no se afirma que AC-003 y AC-004 estén demostrados de extremo a extremo
  sobre recursos que aún no existen.

Esta frontera evita crear tablas o endpoints prematuros sólo para aparentar
que la aplicación está más avanzada.

## 9. Archivos principales

- `src/raceops/iam/authorization.py`;
- `src/raceops/api/dependencies.py`;
- `src/raceops/api/errors.py`;
- `tests/unit/iam/test_authorization.py`;
- `tests/api/test_identity.py`;
- `docs/requirements/permission-matrix.md`;
- `docs/domain/visibility-model.md`.

## 10. Punto de aprobación

Al aprobar este bloque comienza 6.6:

1. revisión integral de seguridad;
2. verificación final de migraciones y contenedores;
3. trazabilidad y documentación consolidada;
4. suite completa y CI;
5. evaluación de cierre de Fase 6;
6. preparación de la Fase 7 — base operativa.
