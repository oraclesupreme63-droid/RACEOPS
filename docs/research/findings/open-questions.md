# RaceOps — Preguntas abiertas y plan de validación

## 1. Información del documento

- **Versión:** 0.1
- **Estado:** Aprobado
- **Fuentes:** Research Plan, INT-001, INT-002, INT-003, Evidence Matrix y Assumptions Register
- **Propósito:** Identificar qué falta comprobar y cómo obtener evidencia útil.

## 2. Preguntas críticas sobre el problema

| ID | Pregunta abierta | Por qué importa |
|---|---|---|
| OQ-001 | ¿Cuándo fue la última vez que se perdió información importante? | Necesitamos un problema real, no solamente posible |
| OQ-002 | ¿Qué consecuencia produjo esa pérdida? | Permite medir gravedad |
| OQ-003 | ¿Con qué frecuencia sucede? | Diferencia un caso aislado de un patrón |
| OQ-004 | ¿Quién es responsable de registrar información? | Una plataforma sin responsable puede abandonarse |
| OQ-005 | ¿Qué funciona perfectamente con el proceso actual? | RaceOps no debe reemplazarlo |
| OQ-006 | ¿En qué momento exacto falla el proceso actual? | Define dónde intervenir |

## 3. Preguntas sobre el flujo posterior a la sesión

- ¿Qué sucede desde que el piloto baja del vehículo?
- ¿Quién habla primero?
- ¿Cuándo se revisa la telemetría?
- ¿Dónde queda registrado el feedback?
- ¿Quién identifica las causas posibles?
- ¿Quién decide una acción?
- ¿Cómo se comunica al mecánico?
- ¿Cómo se eligen las prioridades del piloto?
- ¿Cómo se comprueba si la decisión funcionó?
- ¿Qué sucede cuando la hipótesis era incorrecta?
- ¿Cuánto tiempo existe antes de la siguiente sesión?

## 4. Preguntas sobre roles y confidencialidad

- ¿Qué debe consultar cada rol?
- ¿Qué puede modificar?
- ¿Quién aprueba una decisión técnica?
- ¿Qué información no debería ver el piloto?
- ¿Qué información necesita el mecánico?
- ¿El Team Manager debe consultar configuraciones exactas?
- ¿Quién puede ver datos de todos los pilotos?
- ¿Qué información sería sensible si llegara a otro equipo?
- ¿Las reglas cambian entre categorías o equipos?

## 5. Preguntas sobre información y herramientas

- ¿Qué dispositivo registra la telemetría?
- ¿Qué software se utiliza para analizarla?
- ¿Qué formatos pueden exportarse?
- ¿El equipo puede exportar un formato estructurado o sólo PDF/impresión?
- ¿Qué autorización y términos permiten reutilizar cada fuente publicada?
- ¿Cómo se corrigen importaciones sin perder la referencia al original?
- ¿Qué información se registra fuera del logger?
- ¿Se utiliza papel, hojas de cálculo o mensajes?
- ¿Se captura alguna información más de una vez?
- ¿Preferirían adjuntar un archivo, enlazarlo o importarlo?
- ¿Cuáles son los datos mínimos necesarios para identificar una sesión?
- ¿Existe conexión a internet confiable en pista?
- ¿Qué debe poder funcionar sin conexión?

## 6. Preguntas sobre historial

- ¿Cómo encuentran información de una visita anterior?
- ¿Cuánto tardan en encontrarla?
- ¿Qué información desean recuperar?
- ¿Con qué frecuencia consultan sesiones antiguas?
- ¿Qué información suele olvidarse?
- ¿Qué información nunca se conserva?
- ¿Quién decide qué vale la pena guardar?

## 7. Preguntas sobre mantenimiento

- ¿Cómo se reporta actualmente una falla?
- ¿Cuándo una observación técnica se convierte en trabajo mecánico?
- ¿Quién confirma que el vehículo está disponible?
- ¿Cómo se registra lo que fue reparado?
- ¿Es necesario conectar la reparación con la sesión que originó el problema?
- ¿Mantenimiento debe estar en el primer flujo o puede esperar?

Por ahora, mantenimiento continúa como parcialmente respaldado, no aprobado
automáticamente para el primer flujo vertical.

## 8. Preguntas sobre adopción

- ¿Quién decidiría utilizar RaceOps?
- ¿Quién tendría que introducir la información?
- ¿Quién recibiría el beneficio?
- ¿Qué impediría su uso durante una carrera?
- ¿Cuánto tiempo de captura sería aceptable?
- ¿Qué tendría que reemplazar para evitar duplicación?
- ¿Qué haría que el equipo lo abandonara?
- ¿Aceptarían probarlo durante varias sesiones reales?

No se preguntará solamente «¿lo usarías?». Se buscarán comportamiento y
compromiso real.

## 9. Plan de validación

### Ola 1 — Cubrir roles faltantes

Prioridad de reclutamiento:

1. Dos mecánicos o responsables de operación.
2. Un Team Manager o propietario de equipo pequeño.
3. Un ingeniero adicional.
4. Uno o dos pilotos adicionales de grassroots o karting.

Ya existen tres participantes, pero todavía hay poca evidencia directa de
mecánica y gestión del equipo.

### Ola 2 — Reconstruir casos reales

Cada participante deberá describir una sesión reciente y, si tiene
autorización, mostrar:

- notas;
- hojas;
- archivos;
- fotografías;
- reportes;
- estructura de carpetas;
- pantallas de sus herramientas.

No se copiará información confidencial. Se registrarán solamente la
estructura y el proceso.

### Ola 3 — Probar el concepto

Se presentará este escenario:

```text
El piloto reporta inestabilidad trasera al frenar en T4.
Los datos muestran una corrección de dirección.
Ingeniería sospecha una causa.
Se asigna una acción.
En la siguiente sesión se evalúa el resultado.
```

Se pedirá al participante:

1. registrar el feedback;
2. consultar los datos disponibles;
3. crear una hipótesis;
4. definir una prioridad;
5. asignar una acción;
6. registrar el resultado posterior.

### Ola 4 — Prueba de usabilidad

Objetivos iniciales:

- completar el registro principal en dos minutos o menos;
- realizarlo sin ayuda;
- no solicitar información innecesaria;
- identificar inmediatamente las próximas acciones;
- impedir que el piloto vea información restringida.

Son metas de prueba, no resultados ya demostrados.

### Ola 5 — Prueba en sesiones repetidas

Para obtener evidencia de adopción se necesitará utilizar RaceOps durante
al menos dos ciclos:

```text
Sesión inicial
    ↓
Análisis
    ↓
Acción
    ↓
Siguiente sesión
    ↓
Resultado
```

La prueba debe observar si los usuarios regresan al sistema sin depender
constantemente del creador del proyecto.

## 10. Umbrales orientativos

| Hipótesis | Evidencia buscada |
|---|---|
| A-001: existe un problema real | 2–3 casos independientes con consecuencias concretas |
| A-003: 1–3 prioridades son útiles | Usuarios identifican inmediatamente qué hacer después |
| A-004: el flujo es viable | Al menos 4 de 5 pruebas completadas sin asistencia |
| A-005: el historial aporta valor | Uso observado al buscar información anterior |
| A-006: se necesitan permisos | Reglas concretas repetidas entre varios roles |
| A-010: captura rápida | Flujo principal completado en aproximadamente dos minutos |
| A-011: existe adopción | Uso repetido en sesiones reales, no solamente intención verbal |

Estos números sirven para tomar decisiones en un proyecto estudiantil; no
representan validación estadística del mercado.

## 11. Estado de la Fase 1

Actualmente existen:

- tres entrevistas documentadas;
- una matriz de evidencia;
- un registro de hipótesis;
- contraevidencia;
- análisis de alternativas;
- un artefacto público de timing reproducido con procedencia;
- una dirección de producto delimitada.

Todavía falta evidencia de:

- mecánicos;
- Team Managers;
- uso real;
- artefactos reales;
- pruebas del flujo;
- adopción repetida.

La Fase 1 cuenta con suficiente estructura para evaluar el Gate G1, pero la
investigación deberá continuar durante requisitos, prototipos y desarrollo.
