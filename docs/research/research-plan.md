# Plan de investigación — RaceOps

## 1. Información del documento

- **Proyecto:** RaceOps
- **Versión:** 1.0
- **Estado:** Aprobado
- **Fase:** Investigación y validación
- **Fecha:** Por definir

## 2. Propósito

Este plan define cómo RaceOps investigará el trabajo real de pequeños
equipos de karting y grassroots motorsport.

La investigación deberá impedir que el producto se construya a partir de:

- preferencias personales;
- solicitudes aisladas;
- suposiciones;
- imitación de software profesional;
- respuestas influenciadas por preguntas dirigidas.

El propósito no es conseguir aprobación para RaceOps, sino determinar:

- qué problemas existen realmente;
- quién los experimenta;
- con qué frecuencia ocurren;
- qué consecuencias producen;
- cómo se resuelven actualmente;
- qué procesos no deben reemplazarse;
- si RaceOps puede aportar valor sin añadir demasiada fricción.

## 3. Estado inicial

Actualmente existen tres fuentes principales de investigación:

| ID | Participante | Contribución |
|---|---|---|
| INT-001 | Professional racing driver | Contexto de sesiones, roles, condiciones e información histórica |
| INT-002 | Motorsport data coach / AiM specialist | Contraevidencia, herramientas actuales y riesgo de carga administrativa |
| INT-003 | Driver with karting and formula experience | Feedback, análisis, prioridades y confidencialidad técnica |

Estas entrevistas representan señales iniciales. No prueban por sí solas
una necesidad universal ni validación de mercado.

## 4. Objetivos de investigación

### RO-001 — Comprender el flujo real

Describir qué ocurre desde que termina una sesión hasta que comienza la
siguiente.

### RO-002 — Identificar responsabilidades

Determinar quién registra, analiza, decide, ejecuta y consulta información.

### RO-003 — Identificar herramientas actuales

Comprender qué resuelven correctamente la telemetría, papel, hojas de
cálculo, mensajes y aplicaciones internas.

### RO-004 — Detectar pérdida de contexto

Buscar ejemplos concretos de información olvidada, fragmentada o difícil
de recuperar.

### RO-005 — Medir fricción

Identificar cuánto trabajo manual sería aceptable durante un evento.

### RO-006 — Comprender confidencialidad

Determinar qué información puede ver cada rol y qué debe mantenerse
restringido.

### RO-007 — Validar el ciclo de aprendizaje

Comprobar si los equipos relacionan observación, hipótesis, acción,
resultado y conclusión.

### RO-008 — Validar conocimiento histórico

Determinar si los equipos consultan información al regresar a una pista.

### RO-009 — Probar el flujo propuesto

Observar si usuarios reales comprenden y completan el flujo vertical de
RaceOps.

### RO-010 — Explorar viabilidad comercial

Investigar quién decide adquirir herramientas y qué resultado podría
justificar un gasto. Este objetivo será secundario hasta validar utilidad.

## 5. Preguntas de investigación

| ID | Pregunta |
|---|---|
| RQ-001 | ¿Qué sucede desde que termina una sesión hasta que inicia la siguiente? |
| RQ-002 | ¿Qué información produce cada rol? |
| RQ-003 | ¿Dónde se almacena actualmente esa información? |
| RQ-004 | ¿Quién es responsable de registrarla? |
| RQ-005 | ¿Qué información permanece solamente en conversaciones? |
| RQ-006 | ¿Qué información es difícil de recuperar posteriormente? |
| RQ-007 | ¿Qué herramientas funcionan suficientemente bien y no deben reemplazarse? |
| RQ-008 | ¿Qué información se registra más de una vez? |
| RQ-009 | ¿Qué información nunca se registra por falta de tiempo? |
| RQ-010 | ¿Cómo se convierte un análisis en acciones para la siguiente sesión? |
| RQ-011 | ¿Cómo se determina si una acción produjo una mejora? |
| RQ-012 | ¿Qué detalles no debe consultar un Driver? |
| RQ-013 | ¿Qué información debe permanecer restringida a ingeniería? |
| RQ-014 | ¿Qué consulta el equipo cuando regresa a una pista? |
| RQ-015 | ¿En qué momento podría utilizarse RaceOps sin interrumpir el trabajo? |
| RQ-016 | ¿Qué provocaría que el equipo abandonara la plataforma? |

## 6. Participantes objetivo

La investigación buscará perspectivas de:

- pilotos de karting;
- pilotos con experiencia en otras categorías;
- ingenieros;
- Data Engineers;
- especialistas en telemetría;
- mecánicos;
- coaches;
- Team Managers;
- responsables de pequeños equipos;
- organizadores o kartódromos cuando resulte relevante.

## 7. Cobertura deseada

Como objetivo inicial se buscarán entre 8 y 12 participantes, incluyendo
las entrevistas existentes.

Se intentará incluir al menos:

- tres perspectivas de pilotos;
- dos perspectivas técnicas o de ingeniería;
- dos perspectivas de mecánica u operación;
- una perspectiva de gestión de equipo.

Estas cantidades son objetivos de cobertura, no una garantía de
representatividad estadística.

Si no es posible alcanzar esta cobertura, se documentará la limitación y
no se presentarán las conclusiones como universales.

## 8. Métodos de investigación

### 8.1 Entrevistas semiestructuradas

Conversaciones guiadas por preguntas abiertas, permitiendo profundizar en
situaciones reales.

Duración sugerida:

- entre 20 y 30 minutos;
- o respuestas mediante mensajes y audios.

### 8.2 Reconstrucción de una sesión real

El participante describirá una sesión reciente desde que salió del
vehículo hasta la siguiente salida a pista.

Se buscarán hechos, herramientas, responsables y decisiones concretas.

### 8.3 Revisión de artefactos

Cuando exista permiso, podrán revisarse ejemplos anonimizados de:

- formatos;
- notas;
- reportes;
- hojas de cálculo;
- capturas;
- archivos exportados;
- estructura de datos.

No se copiarán configuraciones sensibles sin autorización explícita.

### 8.4 Observación contextual

Cuando sea posible, se observará una sesión o flujo real sin intervenir.

Se documentará:

- orden de actividades;
- responsables;
- herramientas;
- interrupciones;
- tiempo disponible;
- información que no se registra.

### 8.5 Pruebas de concepto

Antes de programar toda la plataforma se mostrarán:

- diagramas;
- wireframes;
- prototipos;
- ejemplos de reportes.

Se pedirá al participante que complete una tarea, no solamente que opine.

### 8.6 Pruebas de usabilidad

Cuando exista un prototipo funcional se observará:

- finalización de tareas;
- tiempo requerido;
- dudas;
- errores;
- campos ignorados;
- ayuda solicitada;
- abandono;
- comportamiento desde teléfono y computadora.

## 9. Oleadas de investigación

### Oleada 1 — Consolidación de evidencia existente

- documentar INT-001;
- documentar INT-002;
- documentar INT-003;
- separar hallazgos y contraevidencia;
- identificar preguntas sin respuesta.

### Oleada 2 — Cubrir roles faltantes

Priorizar entrevistas con:

- Mechanic;
- Team Manager;
- Engineer o Data Engineer;
- otro pequeño equipo independiente.

### Oleada 3 — Revisión del concepto

Mostrar únicamente el flujo principal:

```text
Sesión
  ↓
Resultados + feedback + observaciones
  ↓
Análisis e hipótesis
  ↓
Prioridades y acciones
  ↓
Siguiente sesión
  ↓
Resultado y conclusión
```

Preguntar qué está equivocado, qué falta y qué debe eliminarse.

### Oleada 4 — Prueba de prototipo

Solicitar tareas concretas sin explicar la interfaz.

Ejemplo:

> Registra que el piloto sintió inestabilidad trasera al frenar en T4 y
> crea una prioridad para la siguiente sesión.

### Oleada 5 — Prueba con sesión real

Cuando el producto lo permita:

- utilizar información real autorizada;
- observar la captura;
- comprobar si se consulta posteriormente;
- registrar abandono y uso repetido.

## 10. Estructura de una entrevista

### Apertura

1. Agradecer el tiempo.
2. Explicar que no se busca vender RaceOps.
3. Solicitar permiso para tomar notas.
4. Aclarar que no se necesita información confidencial.
5. Ofrecer anonimato.

### Exploración sin mostrar RaceOps

1. Pedir una experiencia reciente.
2. Reconstruir el flujo paso a paso.
3. Preguntar por herramientas.
4. Identificar quién registra información.
5. Buscar ejemplos de pérdida o recuperación.
6. Preguntar qué funciona correctamente.

### Revisión del flujo propuesto

1. Mostrar solamente el flujo vertical.
2. Preguntar qué está mal.
3. Preguntar qué sobra.
4. Preguntar quién realizaría cada acción.
5. Preguntar qué sería impráctico.
6. Preguntar qué información debe ser confidencial.

### Cierre

1. Resumir lo entendido.
2. Preguntar si la interpretación es correcta.
3. Solicitar permiso para un seguimiento.
4. Preguntar si conoce a otro perfil relevante.
5. Agradecer la colaboración.

## 11. Preguntas que deben evitarse

No preguntar:

- ¿Te gusta RaceOps?
- ¿No crees que RaceOps te ayudaría?
- ¿Pagarías por una plataforma que organiza todo?
- ¿Te parece buena esta funcionalidad?
- ¿No sería mejor centralizar la información?

Estas preguntas inducen respuestas positivas y producen evidencia débil.

En su lugar preguntar:

- Muéstrame qué ocurre después de una sesión.
- ¿Dónde queda esa información?
- ¿Quién la registra?
- ¿Cuándo fue la última vez que esto causó un problema?
- ¿Qué sucede si nadie lo escribe?
- ¿Cómo lo buscas meses después?
- ¿Qué no reemplazarías de tu proceso actual?
- ¿Qué parte de este flujo está equivocada?

## 12. Registro de entrevistas

Cada entrevista utilizará un identificador:

```text
INT-001
INT-002
INT-003
...
```

Cada registro incluirá:

- ID;
- fecha;
- rol;
- categoría o nivel;
- formato de entrevista;
- duración aproximada;
- consentimiento;
- contexto;
- flujo actual;
- herramientas;
- observaciones;
- problemas;
- contraevidencia;
- información confidencial;
- citas autorizadas;
- interpretación;
- hipótesis generadas;
- preguntas pendientes;
- próximos pasos.

## 13. Separación de información

Cada hallazgo distinguirá:

### Observación

Lo que el participante describió, mostró o hizo.

### Interpretación

Lo que creemos que puede significar.

### Hipótesis

Una explicación o decisión que todavía debe comprobarse.

Ejemplo:

```text
Observación:
El piloto comunica el feedback verbalmente al Engineer.

Interpretación:
El piloto puede no querer escribir durante el evento.

Hipótesis:
Una captura rápida realizada por Engineer podría reducir fricción.
```

## 14. Evaluación de evidencia

### Señal

Un participante menciona un comportamiento o problema.

### Candidato a patrón

Dos o tres participantes independientes describen un comportamiento
similar.

### Patrón con mayor respaldo

Cinco o más participantes de diferentes roles aportan evidencia
compatible.

### Evidencia observada

El comportamiento se observa en un flujo real.

### Evidencia de producto

El usuario completa una tarea con el prototipo o producto.

### Evidencia de adopción

El usuario regresa voluntariamente y utiliza RaceOps nuevamente.

La cantidad de entrevistas no sustituye la calidad, independencia,
recencia y comportamiento observado.

## 15. Clasificación de decisiones

Cada decisión relevante se clasificará como:

### Respaldada por evidencia

Existe evidencia directa, repetida u observada suficiente para continuar.

### Parcialmente respaldada

Existen señales consistentes, pero todavía hay dudas o poca cobertura.

### Hipótesis

La decisión parece razonable, pero todavía no cuenta con evidencia
suficiente.

### Rechazada o evidencia insuficiente

Existe contraevidencia, falta de utilidad o una relación costo-beneficio
desfavorable.

## 16. Reglas para cambiar el producto

Una entrevista no incorporará automáticamente una funcionalidad.

Antes de modificar el alcance se evaluará:

- independencia de la evidencia;
- frecuencia;
- consecuencia;
- rol afectado;
- solución actual;
- fricción añadida;
- relación con el flujo principal;
- complejidad;
- compatibilidad con v1.0.

Una función respaldada por una sola entrevista permanecerá normalmente
como hipótesis o P2.

Las obligaciones de seguridad e integridad no requieren demanda de
mercado para ser necesarias.

## 17. Privacidad y consentimiento

- No se solicitarán configuraciones técnicas sensibles.
- El participante podrá omitir cualquier pregunta.
- Las notas podrán anonimizarse.
- No se publicarán nombres sin autorización.
- Las citas textuales requerirán permiso.
- Los archivos proporcionados no se publicarán automáticamente.
- Los datos reales se reemplazarán por datos sintéticos cuando corresponda.
- Cualquier solicitud de eliminación será atendida.
- Los secretos comerciales no se almacenarán en el repositorio.

## 18. Estructura documental

```text
docs/research/
├── research-plan.md
├── interviews/
│   └── README.md (política pública; registros en archivo privado)
├── findings/
│   ├── evidence-matrix.md
│   ├── validated-problems.md
│   └── open-questions.md
├── assumptions.md
└── competitor-analysis.md
```

## 19. Criterios de salida de la Fase 1

La fase tendrá suficiente avance para continuar cuando:

- los registros individuales estén documentados en el archivo privado;
- la versión pública contenga únicamente una síntesis agregada;
- exista una matriz de evidencia;
- las hipótesis principales estén registradas;
- la contraevidencia esté representada;
- las herramientas actuales hayan sido investigadas;
- se identifique el flujo con mayor respaldo;
- las preguntas abiertas estén explícitas;
- el Problem Statement haya sido revisado;
- el Gate G1 — Problem Ready haya sido evaluado.

La investigación no terminará definitivamente al pasar de fase. Seguirá
activa durante prototipos y desarrollo.

## 20. Próximos pasos

1. Aprobar este plan.
2. Crear la estructura `docs/research/`.
3. Documentar INT-001.
4. Documentar INT-002.
5. Documentar INT-003.
6. Construir la matriz inicial de evidencia.
7. Identificar roles y preguntas faltantes.
8. Enviar la guía de validación a nuevos participantes.
