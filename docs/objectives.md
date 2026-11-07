# Objetivos del proyecto — RaceOps

## 1. Información del documento

- **Proyecto:** RaceOps
- **Versión:** 1.1
- **Estado:** Aprobado
- **Etapa:** Product Discovery
- **Fecha objetivo:** Pendiente de publicación oficial
- **Fecha:** Por definir

## 2. Propósito

Este documento define el objetivo general, el objetivo SMART provisional
y los objetivos específicos de RaceOps.

Los objetivos se basan en la investigación disponible y en el alcance
aprobado para RaceOps v1.0.

## 3. Objetivo general

Diseñar, desarrollar y validar un MVP web de RaceOps que permita a un
pequeño equipo de karting o grassroots motorsport conservar el contexto,
las decisiones y los aprendizajes producidos entre sesiones, relacionando
feedback, resultados, observaciones, hipótesis, acciones y conclusiones
con visibilidad adecuada para cada rol.

## 4. Objetivo SMART provisional

Antes de la fecha oficial de presentación en la feria, diseñar,
implementar, probar y documentar una versión funcional de RaceOps capaz
de completar el flujo vertical entre dos sesiones, desde el registro de
resultados y feedback hasta la evaluación de una acción y la conservación
del aprendizaje, aplicando autenticación, permisos por rol, reglas de
negocio, pruebas automatizadas y ejecución documentada mediante Docker.

La fecha exacta se incorporará cuando sea publicada oficialmente.

## 5. Descomposición SMART

### Specific — Específico

RaceOps se concentrará en un flujo verificable:

```text
Sesión
  ↓
Resultados + feedback + condiciones + observaciones
  ↓
Análisis e hipótesis
  ↓
Prioridades y acciones
  ↓
Siguiente sesión
  ↓
Comparación
  ↓
Conclusión e historial
```

No se medirá el avance únicamente por la creación de módulos o pantallas.

### Measurable — Medible

El objetivo se considerará cumplido cuando:

- el flujo vertical pueda ejecutarse de principio a fin;
- los cinco roles iniciales tengan permisos verificables;
- usuarios no autorizados no puedan consultar información restringida;
- un vehículo no disponible no pueda asignarse a una sesión;
- vueltas y sectores inválidos sean rechazados;
- las acciones puedan relacionarse con resultados posteriores;
- el aprendizaje pueda recuperarse desde el historial;
- todas las pruebas críticas definidas para el MVP estén aprobadas;
- el sistema pueda iniciarse siguiendo instrucciones documentadas;
- exista una demostración estable con datos reales o representativos.

### Achievable — Alcanzable

El proyecto utilizará:

- un monolito modular;
- una experiencia vertical prioritaria;
- tecnologías conocidas y documentadas;
- desarrollo incremental;
- alcance controlado;
- integraciones externas opcionales;
- entrada manual antes de automatizaciones complejas.

Las funcionalidades condicionadas no impedirán completar el MVP.

### Relevant — Relevante

El objetivo responde a señales obtenidas durante la investigación:

- feedback y datos se utilizan de forma complementaria;
- los análisis deben convertirse en acciones;
- diferentes roles necesitan diferente información;
- algunas decisiones técnicas son confidenciales;
- puede existir valor en conservar conocimiento histórico;
- una herramienta adicional debe minimizar la carga administrativa.

### Time-bound — Limitado en el tiempo

La entrega deberá completarse antes de la fecha oficial de la feria.

Mientras la fecha no haya sido publicada, este componente permanece
provisional y no se asignarán fechas ficticias.

## 6. Objetivos específicos según la Taxonomía de Bloom

### OE-01 — Comprender

Describir el flujo de trabajo posterior a una sesión e identificar cómo
participan pilotos, ingenieros, mecánicos y responsables del equipo.

**Evidencia esperada:**

- entrevistas documentadas;
- mapas de flujo;
- notas de investigación.

### OE-02 — Analizar

Analizar la información obtenida para distinguir problemas respaldados,
contraevidencia, hipótesis y solicitudes aisladas.

**Evidencia esperada:**

- matriz de evidencia;
- lista de supuestos;
- problemas validados;
- hallazgos actualizados.

### OE-03 — Evaluar

Evaluar las funcionalidades propuestas según evidencia, utilidad,
fricción, complejidad y relación con el flujo principal.

**Evidencia esperada:**

- backlog priorizado;
- funciones aceptadas, condicionadas o rechazadas;
- decisiones justificadas.

### OE-04 — Crear

Modelar el dominio de RaceOps mediante entidades, relaciones, estados,
reglas de negocio y niveles de visibilidad.

**Evidencia esperada:**

- modelo de dominio;
- diagrama entidad-relación;
- diagramas de estados;
- catálogo de reglas de negocio.

### OE-05 — Crear

Diseñar una arquitectura de monolito modular que separe identidad,
operaciones, sesiones, análisis, mantenimiento e historial.

**Evidencia esperada:**

- diagrama de arquitectura;
- estructura del proyecto;
- ADR;
- lineamientos de API.

### OE-06 — Aplicar

Implementar autenticación, autorización y separación de información
según equipo, rol y nivel de visibilidad.

**Evidencia esperada:**

- endpoints protegidos;
- reglas de autorización;
- pruebas de acceso permitido y denegado.

### OE-07 — Aplicar

Implementar el flujo vertical prioritario entre dos sesiones.

**Evidencia esperada:**

- creación de eventos y sesiones;
- registro de resultados y feedback;
- análisis e hipótesis;
- prioridades y acciones;
- comparación posterior;
- conclusión recuperable.

### OE-08 — Analizar

Calcular y presentar métricas básicas que ayuden a comparar sesiones sin
pretender sustituir herramientas profesionales de telemetría.

**Evidencia esperada:**

- mejor vuelta;
- promedio;
- peor vuelta;
- cantidad de vueltas;
- consistencia;
- comparación entre sesiones.

### OE-09 — Evaluar

Verificar la seguridad, integridad, usabilidad y robustez del sistema
mediante pruebas y revisión de casos límite.

**Evidencia esperada:**

- pruebas unitarias;
- pruebas de integración;
- pruebas de API;
- pruebas de reglas de negocio;
- pruebas de autorización;
- registro y corrección de incidencias.

### OE-10 — Crear

Construir una demostración estable que comunique el problema, la solución,
el funcionamiento y la evidencia del proyecto.

**Evidencia esperada:**

- aplicación funcional;
- datos de demostración;
- presentación;
- documentación;
- video o demostración de respaldo;
- release `v1.0.0`.

## 7. Objetivos de investigación

Durante Product Discovery se buscará:

- identificar patrones repetidos entre participantes independientes;
- documentar contraevidencia;
- observar flujos reales cuando sea posible;
- medir la cantidad de captura manual aceptable;
- identificar información confidencial;
- conocer qué herramientas actuales funcionan correctamente;
- probar el flujo principal con usuarios;
- determinar si RaceOps aporta claridad sin añadir demasiada fricción.

## 8. Objetivos técnicos

RaceOps deberá:

- utilizar migraciones de base de datos;
- validar toda entrada externa;
- manejar errores de forma consistente;
- evitar exposición de información sensible;
- mantener separación entre responsabilidades;
- incluir type hints;
- registrar eventos técnicos relevantes;
- ejecutar pruebas automáticamente;
- poder iniciarse mediante Docker;
- mantener documentación actualizada.

## 9. Objetivos que no se persiguen en v1.0

RaceOps v1.0 no tiene como objetivo:

- reemplazar software de telemetría;
- soportar todas las categorías de motorsport;
- generar recomendaciones automáticas mediante IA;
- procesar telemetría en tiempo real;
- convertirse inmediatamente en SaaS;
- demostrar disposición comercial a pagar;
- afirmar escalabilidad sin mediciones;
- maximizar la cantidad de funciones.

## 10. Indicadores de cumplimiento

| Indicador | Criterio |
|---|---|
| Flujo vertical | Puede completarse de principio a fin |
| Control de acceso | Los casos permitidos y denegados funcionan |
| Reglas críticas | Cuentan con pruebas automatizadas |
| Historial | El aprendizaje de una sesión puede recuperarse |
| Instalación | Puede ejecutarse siguiendo la documentación |
| Demostración | Funciona con datos reales o representativos |
| Documentación | Refleja el comportamiento de la versión entregada |
| Evidencia | Las decisiones importantes indican su respaldo |

## 11. Indicadores todavía no definidos

No se establecerán cifras sin una línea base para:

- tiempo ahorrado;
- reducción de errores;
- frecuencia de uso;
- cantidad ideal de campos;
- usuarios concurrentes soportados;
- disposición a pagar;
- mejora deportiva atribuible a RaceOps.

Estas métricas solamente se definirán después de obtener datos
observables.

## 12. Actualización temporal pendiente

Cuando se publique la fecha oficial de la feria se actualizarán:

- la fecha objetivo;
- los hitos;
- el calendario de versiones;
- la reserva para pruebas;
- la fecha de congelamiento de funcionalidades;
- la fecha de `v1.0.0`.

La ausencia temporal de una fecha oficial no autoriza ampliar el alcance.
