# RaceOps — Protocolo de validación de Fase 9

## 1. Propósito

Determinar si el Session Learning Loop representa trabajo reconocible y puede
completarse con una fricción aceptable. La prueba no busca convencer al
participante ni confirmar que RaceOps es una revolución.

## 2. Tres preguntas distintas

| Nivel | Pregunta | Evidencia válida |
|---|---|---|
| Dominio | ¿El flujo y su lenguaje se parecen al trabajo real? | reconstrucción de casos, correcciones concretas y artefactos autorizados |
| Usabilidad | ¿La persona completa las tareas sin ayuda excesiva? | conducta observada, tiempo, errores, dudas y abandono |
| Adopción | ¿Regresa y lo utiliza nuevamente en otro ciclo? | uso repetido voluntario; no basta decir «sí lo usaría» |

Un resultado positivo en un nivel no valida automáticamente los demás.

## 3. Participantes

Primera ronda objetivo: cinco sesiones individuales, procurando incluir:

- dos Drivers;
- un Engineer, Data Engineer o Coach;
- un Mechanic;
- un Team Manager o propietario de equipo pequeño.

Los dos pilotos que ya colaboraron pueden participar, pero sus respuestas no
se contarán como dos roles técnicos. Si no se logra la cobertura, el informe
declarará la limitación y no generalizará los resultados.

## 4. Condiciones previas

Antes de una prueba deben existir:

- consentimiento para tomar notas;
- caso sintético o datos expresamente autorizados y anonimizados;
- aplicación local con cuentas de prueba, nunca credenciales del participante;
- versión y escenario congelados;
- cronómetro y hoja de observación;
- criterio para detener la sesión si aparece información sensible.

## 5. Secuencia de una sesión

### A. Contexto sin mostrar RaceOps

Pedir que reconstruya una sesión reciente: qué sucedió, quién habló, qué se
registró, qué herramienta se utilizó y cómo decidieron el siguiente paso.

### B. Reacción al modelo

Mostrar únicamente:

```text
Session → Feedback + Results + Observation
        → Analysis → Hypothesis → Priority → Action
        → Next Session → Outcome → Learning
```

Preguntar qué está equivocado, qué sobra, qué falta y quién sería responsable.

### C. Tareas observadas

1. Driver registra feedback de una Session terminada.
2. Engineer localiza resultados y feedback, documenta un hallazgo y propone
   una Hypothesis sin presentarla como certeza.
3. Engineer define hasta tres Priorities y una Action para el Role correcto.
4. Responsable identifica qué debe hacer en la siguiente Session.
5. Engineer registra el Outcome y explica qué quedó aprendido.
6. Participante distingue qué información debería o no ver cada Role.

No se explicará dónde hacer clic durante la medición. Si pide ayuda, se
registra el punto exacto y después se permite continuar.

### D. Cierre

Preguntar qué duplicó trabajo, qué campo eliminaría, qué información faltó,
qué no confiaría al sistema y en qué momento real podría o no utilizarlo.

## 6. Métricas

Por tarea se registran:

- resultado: completa sin ayuda, completa con ayuda, incompleta o abandonada;
- duración, como diagnóstico y no como calificación aislada;
- cantidad y tipo de ayudas;
- errores y recuperaciones;
- dudas de lenguaje;
- campos omitidos o información inventada para poder continuar;
- información que el participante se niega correctamente a registrar;
- comentarios espontáneos y contraevidencia.

## 7. Umbrales de decisión

| Hipótesis | Umbral orientativo | Decisión si no se alcanza |
|---|---|---|
| A-004, flujo viable | al menos 4 de 5 participantes completan el recorrido principal con ayuda mínima | simplificar o rediseñar antes de ampliar módulos |
| A-010, captura rápida | mediana cercana a 2 minutos para feedback + prioridad + Action, sin error crítico | reducir campos/pasos; no maquillar el tiempo |
| A-003, 1–3 prioridades | participantes pueden explicar inmediatamente el siguiente trabajo | revisar cantidad, lenguaje o presentación |
| A-006/A-007, permisos | reglas concretas repetidas y ausencia de exposición técnica | ajustar matriz de acceso antes de nuevos módulos |
| A-011, adopción | al menos un segundo ciclo voluntario con datos autorizados | mantener como evidencia insuficiente |
| A-013, cliente web | tareas posibles en teléfono y computadora sin bloqueo | reconsiderar interfaz, no el dominio automáticamente |

Estos umbrales sirven para decidir dentro de un proyecto estudiantil. No
representan validación estadística del mercado.

## 8. Clasificación de problemas

- **P0 crítico:** impide completar el flujo, pierde información o expone datos;
- **P1 importante:** causa error, ayuda repetida o duplicación considerable;
- **P2 mejora:** preferencia o fricción menor sin bloquear la tarea;
- **hipótesis:** solicitud aislada sin conducta o problema observado;
- **rechazada:** contradice evidencia o añade más costo que valor.

No se programará automáticamente cada comentario.

## 9. Cliente mínimo de validación

Swagger demuestra el contrato técnico, pero no permite medir usabilidad de
un Driver o Mechanic. El Bloque 9.2 construirá un cliente web estrecho para:

- entrar con cuentas locales de prueba;
- abrir una Session asignada;
- registrar Driver Feedback;
- revisar resultados y observaciones autorizadas;
- crear Analysis, Hypothesis, Priority y Action como Engineer;
- consultar la tarea asignada;
- registrar y leer Outcome y Learning Chain.

No incluirá dashboard general, mantenimiento, personalización visual avanzada,
telemetría en vivo ni funciones comerciales. Las reglas seguirán viviendo en
la API.

## 10. Privacidad y publicación

- el participante puede detenerse u omitir preguntas;
- no se copiará un setup técnico salvo autorización explícita y necesidad
  justificada;
- las citas textuales requieren permiso;
- las notas individuales permanecen privadas;
- el repositorio recibe sólo plantillas vacías y síntesis agregadas;
- una solicitud de eliminación se atiende eliminando el registro privado;
- los resultados negativos se conservan en la síntesis.

## 11. Regla de salida

Fase 9 no termina por alcanzar un número de entrevistas. Termina cuando existe
una prueba fuera del caso ideal, las fricciones principales están documentadas
y cada ajuste está priorizado como defecto, evidencia, hipótesis o rechazo.
