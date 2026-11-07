# RaceOps — Casos de uso

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G2
- **Alcance:** P0 completo y referencias P1–P3

## 2. Convenciones

- Los recursos siempre pertenecen a un equipo.
- «Autorizado» significa que se cumplen equipo, rol, relación con el
  recurso y visibilidad.
- Los flujos P1–P3 no bloquean el primer corte P0.

## 3. Catálogo

| ID | Caso de uso | Actor principal | Prioridad | RF relacionados |
|---|---|---|---:|---|
| UC-001 | Iniciar sesión | Miembro del equipo | P0 | RF-001–RF-003 |
| UC-002 | Administrar membresías y roles | Administrator | P0/P1 | RF-004–RF-012 |
| UC-003 | Administrar pilotos | Team Manager | P0 | RF-013–RF-017 |
| UC-004 | Administrar vehículos y disponibilidad | Team Manager | P0 | RF-018–RF-023 |
| UC-005 | Administrar pistas y eventos | Team Manager | P0 | RF-024–RF-030 |
| UC-006 | Crear sesión y asignar recursos | Team Manager / Engineer | P0 | RF-031–RF-034 |
| UC-007 | Gestionar ciclo de sesión y resultados | Team Manager / Engineer | P0 | RF-035–RF-044 |
| UC-008 | Registrar vueltas, sectores y métricas | Engineer | P0 | RF-045–RF-069 |
| UC-009 | Registrar condiciones | Engineer / Team Manager | P0 | RF-070–RF-078 |
| UC-010 | Registrar feedback del piloto | Driver / Engineer | P0 | RF-079–RF-088 |
| UC-011 | Registrar observaciones | Engineer / Mechanic | P0 | RF-089–RF-095 |
| UC-012 | Analizar y formular hipótesis | Engineer | P0 | RF-096–RF-107 |
| UC-013 | Definir prioridades | Engineer | P0 | RF-108–RF-114 |
| UC-014 | Crear y ejecutar acciones | Engineer / responsable | P0 | RF-115–RF-122 |
| UC-015 | Evaluar una acción | Engineer | P0 | RF-123–RF-130 |
| UC-016 | Referenciar telemetría | Engineer | P1/P2 | RF-131–RF-135 |
| UC-017 | Consultar historial y resumen | Miembro autorizado | P0/P1 | RF-152–RF-170 |
| UC-018 | Gestionar mantenimiento | Mechanic | P1 | RF-136–RF-151 |
| UC-019 | Completar el Session Learning Loop | Equipo | P0 | RF-031–RF-130, RF-152–RF-167 |

## 4. Casos de uso detallados

### UC-001 — Iniciar sesión

**Actor:** Miembro activo del equipo.

**Precondiciones:** La cuenta existe, está activa y tiene una membresía
válida.

**Flujo principal:**

1. El actor proporciona sus credenciales.
2. RaceOps verifica la contraseña almacenada mediante hash seguro.
3. RaceOps verifica el estado del usuario y sus membresías.
4. Si existe una sola membresía activa, RaceOps la selecciona; si existen
   varias, exige seleccionar el Team autorizado.
5. RaceOps crea un token limitado a la membresía elegida.

**Alternativas:** Credenciales incorrectas, identidad inactiva o Team no
autorizado producen una respuesta genérica y no revelan qué dato falló. Con
credenciales válidas y varias membresías sin selección, RaceOps solicita el
contexto de Team sin emitir todavía un token.

**Postcondición:** El actor puede operar únicamente dentro de su equipo y
permisos.

### UC-006 — Crear sesión y asignar recursos

**Actor:** Team Manager o Engineer autorizado.

**Precondiciones:** Existen un evento, un piloto activo y un vehículo
`READY`, todos del mismo equipo.

**Flujo principal:**

1. El actor selecciona el evento.
2. Indica tipo y fecha de la sesión.
3. Asigna piloto y vehículo.
4. RaceOps verifica pertenencia, actividad y disponibilidad.
5. RaceOps crea la sesión en `PLANNED`.

**Alternativas:**

- piloto inactivo;
- vehículo no disponible;
- recurso perteneciente a otro equipo;
- usuario sin permiso.

En todos los casos RaceOps rechaza la operación sin crear una sesión
parcial.

### UC-007 — Gestionar sesión y resultados

**Actor:** Team Manager o Engineer autorizado.

**Precondición:** Existe una sesión del equipo.

**Flujo principal:**

1. El actor inicia la sesión.
2. RaceOps registra la hora real de inicio.
3. El actor completa la actividad en pista.
4. RaceOps permite cargar resultados mientras estén abiertos.
5. El actor bloquea los resultados.
6. RaceOps registra quién y cuándo realizó el bloqueo.

**Alternativas:** Una transición inválida o una escritura posterior al
bloqueo se rechaza. Una corrección excepcional es P1 y requiere permiso y
justificación.

### UC-010 — Registrar feedback

**Actores:** Driver o Engineer autorizado.

**Precondición:** El Driver está asignado a la sesión.

**Flujo principal Driver:**

1. El Driver abre su sesión.
2. Registra una descripción breve.
3. Añade opcionalmente zona, fase, severidad o confianza.
4. RaceOps registra autor, piloto y momento.

**Flujo alterno:** Engineer registra feedback comunicado verbalmente. El
sistema conserva por separado quién lo experimentó y quién lo capturó.

**Postcondición:** El feedback queda disponible según visibilidad sin
exponer detalles confidenciales.

### UC-012 — Analizar y formular hipótesis

**Actor:** Engineer autorizado.

**Precondición:** Existe una sesión con al menos una fuente contextual
disponible; no es obligatorio que todas estén presentes.

**Flujo principal:**

1. El Engineer consulta feedback, resultados, condiciones y observaciones.
2. Registra un análisis.
3. Formula una hipótesis con clasificación de causa y confianza.
4. Selecciona el nivel de visibilidad.
5. RaceOps conserva autor y fechas.

**Regla:** Una observación o correlación nunca se convierte automáticamente
en causa confirmada.

### UC-013 — Definir prioridades

**Actor:** Engineer autorizado.

**Precondiciones:** Existe una sesión de origen y, cuando sea conocida, una
sesión objetivo.

**Flujo principal:**

1. El actor redacta una prioridad concreta.
2. Selecciona destinatario: Driver, Engineer o Mechanic.
3. Relaciona origen y objetivo.
4. RaceOps permite destacar hasta tres prioridades principales para la
   combinación destinatario/sesión objetivo.

**Alternativa:** Una cuarta prioridad puede conservarse como nota, pero no
como prioridad principal.

### UC-014 — Crear y ejecutar una acción

**Actores:** Engineer, Team Manager o responsable autorizado.

**Flujo principal:**

1. Se crea una acción desde una hipótesis o prioridad.
2. Se clasifica como conducción, ingeniería o mecánica.
3. Se asigna un responsable.
4. El responsable actualiza su progreso.
5. Marca la acción como completada cuando la ejecución termina.

**Regla:** `COMPLETED` describe ejecución, no mejora demostrada.

### UC-015 — Evaluar una acción

**Actor:** Engineer autorizado.

**Precondiciones:** Existe una acción y una sesión posterior o evidencia
adecuada.

**Flujo principal:**

1. El actor selecciona la acción y evidencia posterior.
2. Clasifica el resultado como mejora, empeoramiento, sin cambio medible,
   no concluyente o no evaluado.
3. Registra una conclusión con el nivel de certeza disponible.
4. Actualiza, cuando corresponda, el estado de la hipótesis.
5. RaceOps conserva la cadena completa.

**Alternativa:** Sin evidencia posterior, la acción puede permanecer
completada pero no evaluada.

### UC-017 — Consultar historial y resumen

**Actor:** Miembro autorizado.

**Precondición:** Existen registros compatibles con su equipo y permisos.

**Flujo principal:**

1. El actor abre una sesión o utiliza un filtro autorizado.
2. RaceOps recupera contexto, resultados y cadena de aprendizaje.
3. Filtra campos y registros según rol, asignación y visibilidad.
4. Distingue datos ausentes de valores iguales a cero.
5. Presenta métricas reproducibles y origen de la información.

**Alternativa:** Si el actor no tiene acceso, RaceOps no revela la existencia
del recurso confidencial.

## 5. Flujo integrado UC-019

```text
UC-006 Crear sesión
    ↓
UC-007 Ejecutar y completar actividad
    ↓
UC-008 Registrar resultados
    +
UC-009 Condiciones opcionales
    +
UC-010 Feedback
    +
UC-011 Observaciones
    ↓
UC-012 Análisis e hipótesis
    ↓
UC-013 Prioridades
    +
UC-014 Acciones
    ↓
Nueva UC-006/UC-007
    ↓
UC-015 Resultado y conclusión
    ↓
UC-017 Historial y resumen
```

## 6. Regla de alcance

UC-019 debe poder completarse sin:

- integración meteorológica;
- importación CSV;
- telemetría en vivo;
- módulo de mantenimiento;
- IA;
- exportación PDF;
- facturación.

