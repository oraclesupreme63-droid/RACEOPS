# RaceOps — Checklist Fase 9: validación con datos y usuarios

## Estado general

- **Fase:** en progreso
- **Inicio:** 12 de noviembre de 2026
- **Entrada:** `v0.4.0 — Session Learning Loop`, Gate G6 aprobado
- **Objetivo:** confrontar el flujo con datos representativos y conducta
  observada, sin confundir intención verbal con adopción
- **Entregables:** Validation Dataset, Usability Findings, Validation Report y
  Updated Requirements

## Bloques

### 9.1 — Contrato de validación

- [x] Separar validación de dominio, usabilidad y adopción.
- [x] Definir tareas, métricas, umbrales y reglas de decisión.
- [x] Definir consentimiento, anonimización y datos prohibidos.
- [x] Proteger registros privados mediante `.gitignore`.
- [x] Delimitar el cliente mínimo necesario para observar usuarios.
- [x] Aprobación del propietario.

### 9.2 — Cliente mínimo de validación

- [x] Elegir la tecnología mínima y registrar la decisión.
- [x] Implementar sólo el recorrido Session Learning Loop.
- [x] Usar la API y autorización reales; no duplicar reglas de negocio.
- [x] Permitir captura rápida desde computadora y teléfono.
- [x] Añadir estados de carga, error y confirmación suficientes para la prueba.
- [x] Pruebas técnicas al final del bloque.
- [x] Aprobación del propietario.

### 9.3 — Dataset y ensayo interno

- [x] Convertir un caso autorizado o representativo a datos anonimizados.
- [x] Incluir datos parciales, incertidumbre y orden no ideal.
- [x] Preparar cuentas locales por Role sin credenciales reales.
- [x] Ejecutar un ensayo completo y corregir bloqueos de la prueba.
- [x] Congelar escenario y versión de validación.
- [ ] Aprobación del propietario.

### 9.4 — Pruebas con participantes

- [ ] Obtener consentimiento antes de cada sesión.
- [ ] Observar tareas sin enseñar el flujo durante la medición.
- [ ] Registrar finalización, tiempo, errores, ayuda y campos ignorados.
- [ ] Separar observaciones, interpretaciones y solicitudes.
- [ ] Conservar registros individuales únicamente en archivo privado.
- [ ] Aprobación del propietario.

### 9.5 — Hallazgos y decisiones

- [ ] Consolidar evidencia y contraevidencia por Role.
- [ ] Clasificar A-001, A-003, A-004, A-006, A-007, A-010, A-011 y A-013.
- [ ] Priorizar fricciones por frecuencia, gravedad y relación con P0.
- [ ] Convertir defectos observados en pruebas de regresión.
- [ ] Actualizar requisitos, dominio, backlog y roadmap.
- [ ] Aprobación del propietario.

### 9.6 — Cierre de Fase 9

- [ ] Publicar síntesis anonimizada y Validation Report.
- [ ] Documentar límites de muestra y evidencia faltante.
- [ ] Decidir conservar, ajustar o rediseñar el flujo.
- [ ] Evaluar la entrada a Fase 10 sin aprobar mantenimiento por inercia.
- [ ] Aprobación de Fase 9.

## Condición para avanzar

El Bloque 9.1 debe aprobarse antes de programar el cliente de validación. No se
pedirán datos reales ni se invitarán participantes hasta disponer de un flujo
seguro, una tarea clara y un lugar privado para las notas.
