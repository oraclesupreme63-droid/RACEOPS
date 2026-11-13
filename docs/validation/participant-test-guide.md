# Guía del facilitador — Prueba observada de RaceOps

## 1. Objetivo de esta ronda

Observar si una persona del dominio reconoce y completa el Session Learning
Loop con una fricción aceptable. No demostrar todas las funciones ni convencer
al participante de usar RaceOps.

## 2. Duración propuesta

| Parte | Tiempo máximo |
|---|---:|
| Bienvenida y consentimiento | 5 min |
| Flujo actual sin RaceOps | 7 min |
| Reacción al modelo | 5 min |
| Tareas observadas | 15 min |
| Cierre | 8 min |

Duración total objetivo: 30–40 minutos.

## 3. Preparación, 15 minutos antes

- [ ] Confirmar consentimiento y dispositivo.
- [ ] Arrancar API, base de datos y cliente web.
- [ ] Abrir `http://127.0.0.1:8000/app/`.
- [ ] Verificar que el escenario limpio `pilot-round-1` existe.
- [ ] Tener disponibles las cuentas de prueba del Role correspondiente.
- [ ] No compartir la contraseña fuera de la sesión.
- [ ] Copiar las dos plantillas a `validation-private/`.
- [ ] Asignar un ID anónimo; no usar nombre, correo o equipo.
- [ ] Preparar cronómetro y un canal alternativo por si falla la conexión.
- [ ] Cerrar pestañas, notificaciones o archivos con información ajena.

Si el escenario ya fue modificado por otra prueba, restaurarlo antes de
comenzar y registrar la versión utilizada.

## 4. Criterios para detener la sesión

Detener inmediatamente si:

- aparece información técnica, personal o comercial no autorizada;
- se muestra una credencial real;
- el participante retira el consentimiento;
- existe exposición de datos entre Roles;
- la aplicación pierde o corrompe información;
- continuar puede afectar un sistema o evento real.

Registrar el hecho sin copiar el contenido sensible. Un incidente de exposición
o pérdida de datos se clasifica como P0 y suspende nuevas sesiones hasta ser
reproducido y resuelto.

## 5. Apertura neutral

Leer:

> Gracias por participar. Estamos evaluando RaceOps, no tu desempeño. No hay
> una ruta que debas adivinar ni respuestas correctas. Intenta realizar las
> tareas como lo harías normalmente y, si puedes, di en voz alta qué esperas
> que ocurra. Durante la medición no te enseñaré dónde hacer clic; si necesitas
> ayuda, pídela y te daré la mínima necesaria después de registrarla.

Confirmar el consentimiento con la plantilla antes de continuar.

## 6. Contexto sin mostrar el producto

Pedir:

> Piensa en una sesión reciente. Cuéntame qué sucedió desde que terminó hasta
> que decidieron qué hacer en la siguiente salida.

Profundizar sólo con preguntas neutrales:

- ¿Quién intervino?
- ¿Dónde quedó registrada la información?
- ¿Qué herramienta utilizaron?
- ¿Qué se decidió y quién debía actuar?
- ¿Qué funcionó bien y no reemplazarías?

## 7. Reacción al modelo

Mostrar únicamente:

```text
Session → Feedback + Results + Observation
        → Analysis → Hypothesis → Priority → Action
        → Next Session → Outcome → Learning
```

Preguntar: ¿qué está equivocado?, ¿qué sobra?, ¿qué falta? y ¿quién sería
responsable de cada paso? No defender el diseño.

## 8. Tareas observadas

Dar una instrucción a la vez y comenzar el cronómetro al terminar de leerla.
Adaptar las tareas al Role sin revelar información que ese Role no debería ver.

1. **Driver:** “Terminaste la sesión. Registra lo que sentiste en T4: la parte
   trasera fue inestable al frenar; severidad media y confianza alta.”
2. **Engineer:** “Revisa los resultados y el feedback disponibles. Registra
   qué observas y una causa posible sin presentarla como certeza.”
3. **Engineer:** “Define hasta tres prioridades para la siguiente sesión y
   asigna una acción al Role que consideres responsable.”
4. **Responsable:** “Encuentra qué trabajo tienes que realizar antes o durante
   la siguiente sesión.”
5. **Engineer:** “Con el resultado de la siguiente sesión, registra si la acción
   mejoró, empeoró o no produjo un efecto medible, y qué aprendió el equipo.”
6. **Cualquier Role:** “Muéstrame qué información crees que puedes ver y cuál
   no debería estar disponible para tu Role.”

Si pide ayuda: registrar el momento, preguntar “¿qué esperabas encontrar?” y
dar sólo la pista mínima. No reiniciar el cronómetro.

## 9. Registro correcto

Durante la tarea anotar sólo conducta observable: clics, lectura, retrocesos,
errores, pausas, solicitudes de ayuda y campos omitidos. Después separar:

- **observación:** lo que hizo o dijo;
- **interpretación:** lo que podría significar;
- **solicitud:** preferencia expresada, todavía no requisito;
- **defecto:** comportamiento reproducible contra el resultado esperado.

No interpretar silencios, gestos o preferencias como validación de mercado.

## 10. Cierre

Preguntar:

- ¿Qué parte duplicó trabajo?
- ¿Qué campo eliminarías primero?
- ¿Qué información faltó para decidir?
- ¿Qué no confiarías a este sistema?
- ¿En qué momento real podrías usarlo y en cuál no?
- ¿Qué información no debería ver un Driver, Mechanic o Team Manager?

Preguntar si desea retirar alguna nota y si autoriza seguimiento. Agradecer sin
prometer cambios.

## 11. Después de la sesión

1. Cerrar la sesión y conservar las notas sólo en el directorio privado.
2. Eliminar nombres, contactos y referencias identificables innecesarias.
3. Registrar un P0 de inmediato; no esperar al análisis agregado.
4. No programar solicitudes aisladas.
5. Al completar la ronda, consolidar resultados por Role en el Bloque 9.5.

La adopción sólo podrá evaluarse si el participante vuelve voluntariamente a
un segundo ciclo; una opinión positiva no cuenta como adopción.
