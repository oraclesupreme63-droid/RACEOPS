# Registro de riesgos — RaceOps

## 1. Información del documento

- **Proyecto:** RaceOps
- **Versión:** 1.1
- **Estado:** Aprobado
- **Etapa:** Product Discovery
- **Fecha:** Por definir

## 2. Propósito

Este documento identifica los eventos inciertos que podrían afectar el
valor, alcance, seguridad, calidad o entrega de RaceOps.

Las puntuaciones representan una estimación de planificación, no una
medición estadística.

## 3. Escala

### Probabilidad

| Valor | Descripción |
|---:|---|
| 1 | Muy baja |
| 2 | Baja |
| 3 | Media |
| 4 | Alta |
| 5 | Muy alta |

### Impacto

| Valor | Descripción |
|---:|---|
| 1 | Mínimo |
| 2 | Menor |
| 3 | Moderado |
| 4 | Alto |
| 5 | Crítico |

### Nivel

```text
Puntuación = Probabilidad × Impacto
```

| Puntuación | Nivel |
|---:|---|
| 1–4 | Bajo |
| 5–9 | Medio |
| 10–16 | Alto |
| 17–25 | Crítico |

## 4. Riesgos de producto e investigación

| ID | Riesgo | P | I | Nivel | Responsable |
|---|---|---:|---:|---:|---|
| R-001 | El problema no resulta suficientemente frecuente o importante para justificar RaceOps. | 4 | 5 | 20 — Crítico | Product Lead |
| R-002 | Las conclusiones se basan en una muestra pequeña o poco diversa. | 4 | 4 | 16 — Alto | Research Lead |
| R-003 | Las preguntas de entrevista influyen en las respuestas de los participantes. | 3 | 4 | 12 — Alto | Research Lead |
| R-004 | Los usuarios dicen que utilizarían RaceOps, pero no lo usan en un flujo real. | 4 | 5 | 20 — Crítico | Product Lead |
| R-005 | RaceOps exige demasiada captura manual y añade más trabajo del que elimina. | 4 | 5 | 20 — Crítico | Product/UX |
| R-006 | El flujo diseñado no representa correctamente cómo trabajan distintos equipos o categorías. | 3 | 5 | 15 — Alto | Product Lead |
| R-007 | El modelo intenta generalizar métricas que varían según vehículo, pista o categoría. | 3 | 5 | 15 — Alto | Domain Lead |
| R-008 | El proyecto confunde una solicitud aislada con una necesidad general. | 3 | 4 | 12 — Alto | Product Lead |
| R-009 | Se intenta comercializar RaceOps antes de validar adopción y disposición a pagar. | 3 | 3 | 9 — Medio | Product Lead |

## 5. Riesgos de alcance y planificación

| ID | Riesgo | P | I | Nivel | Responsable |
|---|---|---:|---:|---:|---|
| R-010 | El alcance crece hacia telemetría profesional, IA, funciones en vivo o RaceOps Cloud. | 4 | 5 | 20 — Crítico | Project Lead |
| R-011 | La fecha de la feria se publica tarde y deja menos tiempo del esperado. | 4 | 4 | 16 — Alto | Project Lead |
| R-012 | La documentación consume tiempo sin producir un prototipo que pueda validarse. | 3 | 4 | 12 — Alto | Project Lead |
| R-013 | Se desarrollan varios módulos incompletos en lugar de un flujo vertical funcional. | 4 | 5 | 20 — Crítico | Project Lead |
| R-014 | Funcionalidades P2 comienzan antes de terminar requisitos P0. | 3 | 4 | 12 — Alto | Project Lead |
| R-015 | La dependencia de una sola persona retrasa desarrollo, pruebas o documentación. | 4 | 4 | 16 — Alto | Project Lead |

## 6. Riesgos técnicos y de dominio

| ID | Riesgo | P | I | Nivel | Responsable |
|---|---|---:|---:|---:|---|
| R-016 | El modelo de dominio resulta rígido o representa incorrectamente sesiones y acciones. | 3 | 5 | 15 — Alto | Domain Lead |
| R-017 | Las reglas de estados permiten transiciones inválidas. | 3 | 4 | 12 — Alto | Backend Lead |
| R-018 | La separación entre sesión completada y resultados bloqueados genera inconsistencias. | 3 | 4 | 12 — Alto | Domain/Backend |
| R-019 | La autorización revela información técnica confidencial al rol incorrecto. | 3 | 5 | 15 — Alto | Security Lead |
| R-020 | Un usuario accede a recursos pertenecientes a otro equipo. | 3 | 5 | 15 — Alto | Security Lead |
| R-021 | Búsquedas, conteos o reportes revelan indirectamente la existencia de información confidencial. | 3 | 5 | 15 — Alto | Security Lead |
| R-022 | El estado incorrecto de un vehículo permite asignarlo cuando no está disponible. | 3 | 5 | 15 — Alto | Backend/QA |
| R-023 | Eliminaciones o cambios destruyen la cadena histórica de evidencia. | 3 | 5 | 15 — Alto | Backend Lead |
| R-024 | La arquitectura incorpora patrones y capas que no aportan valor al MVP. | 3 | 4 | 12 — Alto | Architecture Lead |
| R-025 | Una tecnología necesaria requiere más aprendizaje del previsto. | 3 | 3 | 9 — Medio | Development Lead |

## 7. Riesgos de datos e integraciones

| ID | Riesgo | P | I | Nivel | Responsable |
|---|---|---:|---:|---:|---|
| R-026 | No se obtienen datos reales para validar y demostrar RaceOps. | 4 | 4 | 16 — Alto | Research Lead |
| R-027 | Los datos reales contienen duplicados, faltantes, unidades diferentes o timestamps incorrectos. | 4 | 4 | 16 — Alto | Data/Backend |
| R-028 | Los formatos CSV o de telemetría varían demasiado para una importación temprana. | 4 | 3 | 12 — Alto | Data Lead |
| R-029 | Una API externa falla, cambia o limita el acceso. | 3 | 3 | 9 — Medio | Backend Lead |
| R-030 | Se utilizan datos confidenciales sin autorización suficiente. | 2 | 5 | 10 — Alto | Research/Security |
| R-031 | Datos reales sensibles aparecen en pruebas, logs, repositorio o demostraciones. | 2 | 5 | 10 — Alto | Security Lead |

## 8. Riesgos de experiencia de usuario

| ID | Riesgo | P | I | Nivel | Responsable |
|---|---|---:|---:|---:|---|
| R-032 | Los formularios resultan demasiado largos durante un evento. | 4 | 5 | 20 — Crítico | Product/UX |
| R-033 | Los usuarios no comprenden términos, estados o clasificaciones utilizados por RaceOps. | 3 | 4 | 12 — Alto | UX/Domain |
| R-034 | La interfaz funciona en escritorio pero resulta incómoda desde un teléfono. | 3 | 4 | 12 — Alto | Frontend/UX |
| R-035 | Cada rol recibe demasiada información o no encuentra lo importante. | 3 | 5 | 15 — Alto | Product/UX |
| R-036 | El equipo abandona RaceOps porque duplica su herramienta actual. | 4 | 5 | 20 — Crítico | Product Lead |

## 9. Riesgos de calidad y entrega

| ID | Riesgo | P | I | Nivel | Responsable |
|---|---|---:|---:|---:|---|
| R-037 | Las reglas P0 no cuentan con pruebas suficientes. | 3 | 5 | 15 — Alto | QA/Backend |
| R-038 | La demostración falla por configuración, red o datos inconsistentes. | 3 | 5 | 15 — Alto | Project Lead |
| R-039 | El frontend y backend utilizan contratos incompatibles. | 3 | 4 | 12 — Alto | Development Lead |
| R-040 | Una migración daña o deja inconsistente la base de datos. | 2 | 5 | 10 — Alto | Backend Lead |
| R-041 | Se pierden código, documentación o datos de demostración. | 2 | 5 | 10 — Alto | Project Lead |
| R-042 | Se publican afirmaciones de seguridad, rendimiento o escalabilidad sin mediciones. | 2 | 4 | 8 — Medio | Project Lead |
| R-043 | Secretos o credenciales se incorporan accidentalmente al repositorio. | 2 | 5 | 10 — Alto | Security Lead |

## 10. Respuestas preventivas

### R-001, R-002, R-003 y R-004 — Validación insuficiente

- entrevistar distintos roles y categorías;
- preguntar por experiencias recientes y concretas;
- registrar contraevidencia;
- evitar preguntas dirigidas;
- realizar pruebas observadas con un prototipo;
- medir uso real y no solamente intención declarada.

**Contingencia:** reducir el mercado objetivo, cambiar el flujo principal o
detener módulos sin respaldo.

### R-005, R-032 y R-036 — Fricción y abandono

- utilizar formularios cortos;
- mantener campos especializados opcionales;
- usar valores predeterminados;
- completar asociaciones automáticamente;
- separar captura rápida de análisis posterior;
- medir tiempo, errores y necesidad de ayuda.

**Contingencia:** eliminar campos, permitir captura por otro rol o reducir
el flujo a la información que realmente se consulta.

### R-010, R-013 y R-014 — Crecimiento del alcance

- respetar prioridades P0–P3;
- terminar primero el flujo vertical;
- revisar cualquier cambio contra `scope.md`;
- no iniciar integraciones hasta estabilizar el núcleo;
- congelar funciones antes de la feria.

**Contingencia:** retirar funciones P2 y después P1 no críticas, conservando
seguridad, integridad y flujo vertical.

### R-011 y R-015 — Tiempo y capacidad

- definir hitos cuando se publique la fecha;
- trabajar en incrementos pequeños;
- mantener documentación reproducible;
- reservar tiempo para pruebas y demo;
- evitar trabajo simultáneo innecesario.

**Contingencia:** reducir el alcance a una demostración vertical estable.

### R-016, R-017 y R-018 — Modelo de dominio incorrecto

- validar lenguaje y estados con usuarios;
- crear diagramas de estados;
- documentar invariantes;
- probar transiciones;
- aplicar migraciones versionadas.

**Contingencia:** corregir el modelo mediante una migración y actualizar
trazabilidad antes de continuar funciones dependientes.

### R-019, R-020 y R-021 — Fallos de autorización

- validar permisos en el servidor;
- filtrar siempre por equipo;
- separar modelos de respuesta según visibilidad;
- probar accesos permitidos y denegados;
- revisar búsquedas, conteos, historiales y reportes.

**Contingencia:** revocar acceso, deshabilitar temporalmente el endpoint,
corregir la exposición y revisar recursos similares.

### R-022 y R-023 — Integridad operativa

- proteger estados con reglas de negocio;
- evitar eliminación física de historia;
- utilizar transacciones y restricciones;
- registrar autor, fecha y motivo de correcciones.

**Contingencia:** marcar el recurso como no disponible, restaurar desde
historial o respaldo y corregir la regla antes de reactivarlo.

### R-026, R-027 y R-028 — Datos reales

- solicitar datos anónimos y autorizados;
- conservar origen y unidades;
- validar duplicados, rangos y timestamps;
- diseñar importaciones solamente después de revisar archivos reales.

**Contingencia:** utilizar un dataset representativo claramente identificado
como simulado y documentar las limitaciones.

### R-029 — Dependencias externas

- mantener integraciones como opcionales;
- aplicar timeouts;
- manejar errores explícitamente;
- conservar entrada manual.

**Contingencia:** desactivar la integración sin bloquear el flujo central.

### R-030 y R-031 — Privacidad

- solicitar consentimiento;
- anonimizar ejemplos;
- no almacenar más información de la necesaria;
- utilizar datos sintéticos en pruebas;
- revisar archivos antes de publicar.

**Contingencia:** retirar los datos, rotar credenciales cuando corresponda
y notificar al responsable del proyecto.

### R-037, R-038 y R-039 — Calidad y demostración

- desarrollar pruebas junto con cada función;
- mantener contratos de API documentados;
- preparar datos estables;
- ensayar la demostración;
- preparar video y dataset de respaldo.

**Contingencia:** utilizar una versión etiquetada estable y ejecutar la
demostración de respaldo.

### R-040, R-041 y R-043 — Recuperación y secretos

- utilizar Git y repositorio remoto;
- probar migraciones;
- mantener respaldos;
- utilizar variables de entorno;
- excluir secretos mediante `.gitignore`;
- revisar cambios antes de publicarlos.

**Contingencia:** restaurar respaldo, revertir la migración cuando sea
seguro y rotar inmediatamente cualquier secreto expuesto.

## 11. Señales de alerta

El registro deberá revisarse inmediatamente cuando:

- una entrevista contradiga el flujo principal;
- varios usuarios rechacen la captura manual;
- una tarea no pueda completarse sin ayuda;
- comience trabajo P2 antes de terminar P0;
- se publique la fecha oficial de la feria;
- se obtenga el primer dataset real;
- cambie el modelo de dominio;
- ocurra un fallo de autorización;
- falle una migración;
- la demo no pueda ejecutarse de forma reproducible.

## 12. Riesgos prioritarios

Los riesgos que requieren vigilancia continua son:

1. `R-001` — problema insuficientemente relevante;
2. `R-004` — intención sin uso real;
3. `R-005` — exceso de captura manual;
4. `R-010` — crecimiento descontrolado del alcance;
5. `R-013` — módulos incompletos sin flujo vertical;
6. `R-032` — formularios imprácticos;
7. `R-036` — duplicación de herramientas existentes.

## 13. Revisión

El registro se revisará:

- después de cada entrevista relevante;
- al finalizar cada fase;
- antes de incorporar una función condicionada;
- después de una incidencia de seguridad o integridad;
- cuando se publique la fecha de la feria;
- antes de preparar `v1.0.0`.

Los nombres de responsable representan funciones. Una misma persona puede
cumplir varias funciones durante el proyecto.
