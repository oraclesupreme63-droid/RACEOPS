# RaceOps — Historias de usuario

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G2
- **Propósito:** Expresar el valor esperado sin sustituir requisitos ni reglas.

## 2. Identidad y seguridad

### US-001 — Acceso seguro

Como miembro activo del equipo, quiero iniciar sesión sin que los errores
revelen información sensible, para acceder únicamente a mis funciones.

**Prioridad:** P0. **Relacionados:** RF-001–RF-008.

### US-002 — Administración de acceso

Como Administrator, quiero gestionar membresías y roles sin recibir acceso
técnico innecesario, para mantener seguridad y separación de funciones.

**Prioridad:** P0/P1. **Relacionados:** RF-004–RF-012.

## 3. Base operativa

### US-003 — Pilotos disponibles

Como Team Manager, quiero activar o desactivar pilotos conservando su
historial, para evitar asignaciones inválidas sin perder información.

**Prioridad:** P0. **Relacionados:** RF-013–RF-017.

### US-004 — Vehículos disponibles

Como Team Manager, quiero conocer el estado operativo de un vehículo, para
asignar a sesión únicamente vehículos `READY`.

**Prioridad:** P0. **Relacionados:** RF-018–RF-023.

### US-005 — Eventos contextualizados

Como Team Manager, quiero crear un evento asociado con una pista, para
agrupar sesiones dentro del contexto correcto.

**Prioridad:** P0. **Relacionados:** RF-024–RF-030.

## 4. Sesión y resultados

### US-006 — Preparar una sesión

Como Team Manager o Engineer, quiero asignar un piloto activo y un vehículo
disponible, para preparar una sesión válida.

**Prioridad:** P0. **Relacionados:** RF-031–RF-034.

### US-007 — Separar actividad y resultados

Como Engineer, quiero cargar resultados después de terminar la actividad
en pista, para trabajar con el tiempo real disponible entre sesiones.

**Prioridad:** P0. **Relacionados:** RF-035–RF-044.

### US-008 — Registrar vueltas válidas

Como Engineer, quiero registrar vueltas y determinar cuáles participan en
estadísticas, para obtener métricas reproducibles.

**Prioridad:** P0. **Relacionados:** RF-045–RF-069.

### US-009 — Contexto opcional

Como Engineer, quiero registrar solamente las condiciones conocidas con su
unidad, para aportar contexto sin inventar ni exigir datos.

**Prioridad:** P0. **Relacionados:** RF-070–RF-078.

## 5. Feedback y análisis

### US-010 — Feedback propio

Como Driver, quiero registrar rápidamente lo que experimenté en mi sesión,
para que el equipo pueda compararlo con la evidencia disponible.

**Prioridad:** P0. **Relacionados:** RF-079, RF-081–RF-087.

### US-011 — Feedback verbal

Como Engineer, quiero registrar feedback comunicado verbalmente sin
atribuirme la experiencia del piloto, para reducir fricción y conservar el
origen correcto.

**Prioridad:** P0. **Relacionado:** RF-080, RF-081, RF-086.

### US-012 — Observación sin falsa certeza

Como Engineer o Mechanic, quiero registrar una observación sin convertirla
en causa confirmada, para preservar evidencia honesta.

**Prioridad:** P0. **Relacionados:** RF-089–RF-095.

### US-013 — Hipótesis con confianza

Como Engineer, quiero relacionar evidencia y formular una hipótesis con
nivel de confianza, para representar incertidumbre técnica.

**Prioridad:** P0. **Relacionados:** RF-096–RF-107.

## 6. Próxima sesión

### US-014 — Prioridades del Driver

Como Driver, quiero consultar pocas prioridades concretas para mi próxima
sesión, para saber en qué debo concentrarme.

**Prioridad:** P0. **Relacionados:** RF-108–RF-114.

### US-015 — Acción responsable

Como miembro responsable, quiero conocer y actualizar la acción que me fue
asignada, para que el equipo sepa qué se ejecutó.

**Prioridad:** P0. **Relacionados:** RF-115–RF-122.

### US-016 — Resultado separado de ejecución

Como Engineer, quiero evaluar una acción mediante una sesión posterior,
para distinguir «se hizo» de «funcionó».

**Prioridad:** P0. **Relacionados:** RF-123–RF-130.

## 7. Historial y confidencialidad

### US-017 — Resumen para Driver

Como Driver, quiero consultar mi sesión y prioridades sin detalles técnicos
confidenciales, para recibir información útil y segura.

**Prioridad:** P0. **Relacionados:** RF-087, RF-106, RF-121, RF-130,
RF-164–RF-167.

### US-018 — Cadena de aprendizaje

Como Engineer, quiero recorrer observación, hipótesis, acción y resultado,
para comprender qué se creyó y qué ocurrió después.

**Prioridad:** P0. **Relacionados:** RF-128, RF-152–RF-159.

### US-019 — Resumen de sesión

Como Team Manager, quiero una vista breve del contexto, resultados y
próximas acciones, para coordinar sin revisar todos los canales técnicos.

**Prioridad:** P0. **Relacionados:** RF-161–RF-167.

## 8. Historias no P0

### US-020 — Referencia de telemetría

Como Engineer, quiero asociar una referencia de telemetría con la sesión,
para encontrar la fuente original sin que RaceOps tenga que interpretarla.

**Prioridad:** P1. **Relacionados:** RF-131–RF-133.

### US-021 — Mantenimiento conectado

Como Mechanic, quiero relacionar una reparación con la observación que la
originó, para conservar la historia técnica del vehículo.

**Prioridad:** P1. **Relacionados:** RF-136–RF-149.

### US-022 — Importación CSV

Como Engineer, quiero evitar recapturar resultados que puedan importarse,
para reducir trabajo manual.

**Prioridad:** P2 condicionada. **Relacionado:** RF-134.

## 9. Criterio de valor

Una historia no se considera terminada solamente porque exista una
pantalla. Debe cumplir reglas, autorización, aceptación, pruebas y
trazabilidad correspondientes.
