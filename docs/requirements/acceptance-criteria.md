# RaceOps — Criterios de aceptación P0

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G2
- **Formato:** Escenarios verificables estilo Given/When/Then
- **Cobertura:** Funciones P0 y restricciones no funcionales críticas

## 2. Identidad y autorización

### AC-001 — Inicio de sesión seguro

```gherkin
Given un usuario activo con credenciales válidas
When intenta iniciar sesión
Then RaceOps autentica al usuario
And establece su contexto de equipo y rol
And nunca devuelve la contraseña ni su hash
```

### AC-002 — Credenciales inválidas

```gherkin
Given credenciales incorrectas o un usuario desactivado
When se solicita iniciar sesión
Then RaceOps rechaza el acceso
And utiliza un mensaje que no revela qué dato falló
```

### AC-003 — Aislamiento entre equipos

```gherkin
Given un usuario autenticado del equipo A
And un recurso perteneciente al equipo B
When el usuario intenta consultar o modificar ese recurso
Then RaceOps deniega la operación
And no expone datos del recurso del equipo B
```

### AC-004 — Confidencialidad de ingeniería

```gherkin
Given un Driver autorizado para consultar su sesión
And un análisis con contenido ENGINEERING_CONFIDENTIAL
When el Driver consulta la sesión o su resumen
Then RaceOps muestra solamente el resumen autorizado
And no serializa el contenido confidencial
And no revela su existencia mediante filtros o conteos
```

## 3. Base operativa

### AC-005 — Piloto inactivo

```gherkin
Given un piloto con estado inactivo y con historial existente
When un usuario intenta asignarlo a una sesión nueva
Then RaceOps rechaza la asignación
And conserva accesible su historial autorizado
```

### AC-006 — Vehículo no disponible

```gherkin
Given un vehículo cuyo estado no es READY
When un usuario intenta asignarlo a una sesión nueva
Then RaceOps rechaza la asignación
And no modifica el vehículo ni crea una asignación parcial
```

### AC-007 — Evento válido

```gherkin
Given una pista y un equipo válidos
When un usuario autorizado crea un evento
Then el evento queda relacionado con esa pista y equipo
And no puede relacionarse con recursos de otro equipo
```

### AC-008 — Conservación histórica

```gherkin
Given un piloto, vehículo o usuario relacionado con historia
When es desactivado o retirado mediante el flujo normal
Then RaceOps impide su uso en nuevas asignaciones según corresponda
And conserva sus relaciones históricas
```

## 4. Sesiones y resultados

### AC-009 — Crear sesión válida

```gherkin
Given un evento del equipo, un piloto activo y un vehículo READY
When un usuario autorizado crea una sesión y los asigna
Then RaceOps crea la sesión en estado PLANNED
And conserva evento, pista, tipo, fecha y equipo propietario
```

### AC-010 — Rechazar recursos incompatibles

```gherkin
Given un piloto inactivo, un vehículo no disponible o un recurso de otro equipo
When se intenta crear o actualizar una asignación
Then RaceOps rechaza toda la operación
And no deja datos parciales
```

### AC-011 — Transiciones de sesión

```gherkin
Given una sesión existente
When un usuario autorizado solicita una transición permitida
Then RaceOps cambia el estado y registra las fechas correspondientes
But cuando la transición no está permitida RaceOps la rechaza
```

### AC-012 — Actividad completada con resultados abiertos

```gherkin
Given una sesión cuya actividad en pista terminó
And sus resultados todavía están abiertos
When un usuario autorizado registra vueltas o sectores
Then RaceOps acepta datos válidos
```

### AC-013 — Bloqueo de resultados

```gherkin
Given una sesión con resultados abiertos
When un usuario autorizado bloquea los resultados
Then RaceOps registra actor y momento del bloqueo
And rechaza nuevas vueltas o sectores mediante el flujo normal
```

### AC-014 — Vuelta válida

```gherkin
Given una sesión con resultados abiertos
When se registra una vuelta con número positivo único y duración mayor que cero
Then RaceOps conserva la vuelta y su elegibilidad estadística
But rechaza números duplicados o duraciones no positivas
```

### AC-015 — Sectores opcionales

```gherkin
Given una vuelta válida
When no existen resultados de sectores
Then RaceOps permite conservar la vuelta
But si existen sectores exige orden único y duración mayor que cero
```

### AC-016 — Métricas reproducibles

```gherkin
Given vueltas elegibles y no elegibles
When RaceOps calcula el resumen
Then utiliza solamente vueltas elegibles para mejor vuelta y promedio
And muestra el total de vueltas y las utilizadas
And con datos insuficientes no presenta una métrica como válida
```

## 5. Contexto y feedback

### AC-017 — Condiciones opcionales

```gherkin
Given una sesión existente
When un usuario autorizado conoce solamente algunas condiciones
Then puede registrar esos valores con sus unidades
And los campos desconocidos permanecen ausentes
And el flujo continúa sin integración meteorológica
```

### AC-018 — Feedback del Driver

```gherkin
Given un Driver asignado a una sesión
When registra una descripción válida sin campos especializados
Then RaceOps guarda el feedback
And conserva sesión, autor, piloto y momento
```

### AC-019 — Feedback comunicado verbalmente

```gherkin
Given un Driver que comunicó feedback a un Engineer autorizado
When el Engineer lo registra
Then RaceOps identifica al Driver como quien lo experimentó
And al Engineer como quien lo capturó
```

### AC-020 — Observación honesta

```gherkin
Given una sesión o vehículo del equipo
When un Engineer o Mechanic autorizado registra una observación
Then RaceOps conserva autor, marcas de tiempo y visibilidad
And no presenta la observación como causa confirmada
```

## 6. Análisis, prioridades y acciones

### AC-021 — Hipótesis con incertidumbre

```gherkin
Given una sesión con una o más fuentes contextuales
When un Engineer autorizado crea un análisis y una hipótesis
Then puede relacionar la evidencia disponible
And registra descripción, clasificación y confianza
And puede marcar detalles como ENGINEERING_CONFIDENTIAL
```

### AC-022 — Estado de hipótesis

```gherkin
Given una hipótesis existente
When se registra una conclusión sustentada
Then su estado puede quedar respaldado, parcialmente respaldado, rechazado o no concluyente
And RaceOps conserva el vínculo con la evidencia
```

### AC-023 — Máximo de prioridades principales

```gherkin
Given tres prioridades principales para un destinatario y sesión objetivo
When se intenta destacar una cuarta
Then RaceOps impide marcarla como principal
And permite conservarla como nota no principal cuando esté autorizada
```

### AC-024 — Prioridad accionable y visible

```gherkin
Given una prioridad creada desde una sesión
When se guarda
Then conserva descripción, destinatario, sesión de origen y sesión objetivo
And solamente es visible para actores autorizados
```

### AC-025 — Acción con responsable

```gherkin
Given una hipótesis o prioridad
When un usuario autorizado crea una acción
Then define clasificación, responsable, origen y objetivo
And el responsable autorizado puede actualizar su ejecución
```

### AC-026 — Completar no significa mejorar

```gherkin
Given una acción ejecutada
When el responsable la marca COMPLETED
Then RaceOps registra que fue realizada
And no la clasifica automáticamente como mejora
```

## 7. Resultado, historia y reportes

### AC-027 — Evaluación con evidencia posterior

```gherkin
Given una acción y una sesión posterior
When un Engineer autorizado evalúa el resultado
Then puede registrar mejora, empeoramiento, sin cambio medible, no concluyente o no evaluado
And conserva la sesión o evidencia utilizada
And permite una conclusión sin exigir certeza absoluta
```

### AC-028 — Impedir mejora sin evidencia

```gherkin
Given una acción sin sesión ni evidencia posterior indicada
When se intenta clasificar como mejora
Then RaceOps rechaza la clasificación
And permite mantener la acción como no evaluada
```

### AC-029 — Cadena recuperable

```gherkin
Given una observación relacionada con hipótesis, acción y resultado
When un usuario autorizado consulta el historial
Then RaceOps permite recorrer la cadena completa en orden comprensible
And conserva sesiones de origen y evaluación
```

### AC-030 — Historial filtrado

```gherkin
Given resultados históricos con distintos niveles de visibilidad
When un usuario consulta por pista, evento, sesión, piloto o vehículo
Then RaceOps devuelve solamente registros autorizados
And no revela recursos confidenciales excluidos
```

### AC-031 — Resumen adaptado al rol

```gherkin
Given una misma sesión con información general y confidencial
When un Engineer y un Driver consultan su resumen
Then cada uno recibe el contenido permitido por su rol y relación
And el resumen del Driver excluye ENGINEERING_CONFIDENTIAL
```

### AC-032 — Ausente no significa cero

```gherkin
Given una métrica que no fue registrada
When se genera un historial o resumen
Then RaceOps la representa como ausente o no disponible
And no como el valor numérico cero
```

### AC-033 — Flujo independiente de integraciones

```gherkin
Given que no existen clima externo, importación CSV ni interpretación de telemetría
When el equipo completa el Session Learning Loop
Then todos los pasos P0 permanecen disponibles
```

## 8. Criterios no funcionales críticos

### AC-NF-001 — Autorización probada

Cada operación protegida tendrá pruebas positivas, negativas, entre equipos
y de contenido `ENGINEERING_CONFIDENTIAL`.

### AC-NF-002 — Atomicidad

Una operación fallida que modifique varios datos no dejará registros
parciales o relaciones inconsistentes.

### AC-NF-003 — Errores seguros

Los errores esperados usarán un formato consistente y no expondrán secretos,
SQL, tokens ni detalles internos.

### AC-NF-004 — Captura breve

El feedback podrá guardarse sin campos especializados. La meta de completar
la captura principal en dos minutos se medirá con usuarios y no se declarará
cumplida antes de esa prueba.

### AC-NF-005 — Calidad automatizada

Cada regla P0 contará con prueba automatizada; los endpoints principales
tendrán pruebas de integración y CI rechazará fallos críticos.

### AC-NF-006 — Operación reproducible

La aplicación utilizará configuración externa, migraciones versionadas,
Docker Compose, documentación de ejecución y un endpoint de salud.

## 9. Regla de aprobación

Un criterio solamente se considera cumplido cuando existe evidencia de
prueba. Una implementación visual o una demostración manual no sustituye
las pruebas de reglas, integridad y autorización.

