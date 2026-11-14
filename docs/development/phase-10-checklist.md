# RaceOps — Checklist Fase 10: mantenimiento relacionado

## Estado general

- **Fase:** preparación técnica; hipótesis P1
- **Inicio:** 13 de noviembre de 2026
- **Entrada técnica:** `v0.4.0 — Session Learning Loop`
- **Dependencia abierta:** validación externa de Fase 9
- **Objetivo:** conectar síntomas y acciones mecánicas con intervenciones e
  historial del Vehicle sin convertir RaceOps en un ERP
- **Entregable previsto:** `v0.5 — Maintenance`

El avance técnico de esta fase no valida adopción, usabilidad ni necesidad de
mercado. Se utilizarán datos sintéticos hasta disponer de información real
autorizada.

## Bloques

### 10.1 — Contrato y límites

- [x] Revisar RF-136–RF-151 y reglas BR-057–BR-059.
- [x] Clasificar evidencia, hipótesis y decisiones rechazadas.
- [x] Definir Maintenance Record mínimo, tipos y ciclo de estado.
- [x] Fijar relaciones opcionales con Session, Observation y Action.
- [x] Separar intervención de disponibilidad del Vehicle.
- [x] Definir RBAC, API, errores, integridad y criterios de aceptación.
- [x] Aprobación del propietario.

### 10.2 — Persistencia

- [x] Añadir enums y modelo `MaintenanceRecord`.
- [x] Proteger ownership mediante FKs compuestas por Team.
- [x] Añadir checks, índices y relaciones restrictivas.
- [x] Crear migración Alembic reversible.
- [x] Probar invariantes y round-trip.
- [x] Aprobación del propietario.

### 10.3 — Creación y consulta

- [x] Añadir permisos explícitos de mantenimiento.
- [x] Crear, listar y consultar registros del Team.
- [x] Aplicar filtros por Vehicle, tipo y estado antes del conteo.
- [x] Ocultar recursos ajenos como no encontrados.
- [x] Probar todos los Roles y aislamiento entre Teams.
- [ ] Aprobación del propietario.

### 10.4 — Ciclo de intervención

- [ ] Iniciar, completar y cancelar mediante comandos explícitos.
- [ ] Exigir notas de terminación o motivo de cancelación.
- [ ] Mantener estados terminales inmutables por la API normal.
- [ ] No cambiar automáticamente el Vehicle a `READY`.
- [ ] Probar transiciones, timestamps y concurrencia.
- [ ] Aprobación del propietario.

### 10.5 — Cadena causal

- [ ] Validar referencias opcionales a Session, Observation y Action.
- [ ] Rechazar relaciones entre Teams o Vehicles incompatibles.
- [ ] Exigir Action de tipo `MECHANICAL` cuando se relacione.
- [ ] Recuperar la cadena síntoma → acción → intervención.
- [ ] Aprobación del propietario.

### 10.6 — Disponibilidad segura

- [ ] Separar edición del Vehicle de sus cambios de disponibilidad.
- [ ] Permitir al Mechanic autorizado cambiar estado sin editar identidad.
- [ ] Conservar liberación a `READY` como comando explícito.
- [ ] Verificar bloqueo de nuevas asignaciones no `READY`.
- [ ] Registrar actor y momento de liberación según ADR-006.
- [ ] Aprobación del propietario.

### 10.7 — Historial por vehículo

- [ ] Exponer historial cronológico sin DELETE normal.
- [ ] Incluir relaciones autorizadas sin revelar recursos restringidos.
- [ ] Distinguir intervención completada de Vehicle liberado.
- [ ] Probar paginación y orden estable.
- [ ] Aprobación del propietario.

### 10.8 — Cliente mínimo

- [ ] Añadir vista de mantenimiento al cliente existente.
- [ ] Capturar sólo campos necesarios y usar valores predeterminados seguros.
- [ ] Mostrar estado de intervención y disponibilidad por separado.
- [ ] Permitir recorrer el flujo vertical sin Swagger.
- [ ] Aprobación del propietario.

### 10.9 — Escenario y regresión

- [ ] Ampliar el escenario sintético con síntoma e intervención.
- [ ] Ejecutar el flujo completo con cuentas por Role.
- [ ] Comprobar que una reparación no libera el Vehicle.
- [ ] Ejecutar pruebas globales una vez al cerrar el bloque.
- [ ] Aprobación del propietario.

### 10.10 — Cierre de Fase 10

- [ ] Actualizar dominio, requisitos, trazabilidad y runbook.
- [ ] Documentar limitaciones y evidencia pendiente.
- [ ] Evaluar Gate y versión `v0.5.0`.
- [ ] Aprobación de Fase 10.

## Condición para avanzar

Cada bloque requiere reglas y pruebas proporcionales a su riesgo. Ningún
resultado interno podrá elevar A-009 por encima de hipótesis sin observación
externa. Inventario, costos, alertas automáticas y mantenimiento por componentes
permanecen fuera de esta fase.
