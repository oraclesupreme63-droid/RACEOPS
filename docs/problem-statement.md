# Planteamiento del problema — RaceOps

## 1. Información del documento

- **Proyecto:** RaceOps
- **Versión:** 1.1
- **Estado:** Aprobado
- **Etapa:** Product Discovery
- **Evidencia considerada:** INT-001, INT-002 e INT-003
- **Fecha:** Por definir

## 2. Contexto

Durante un evento de karting o motorsport se genera información
proveniente de diferentes fuentes:

- feedback del piloto;
- tiempos de vuelta y sectores;
- telemetría;
- condiciones ambientales y de pista;
- observaciones del vehículo;
- decisiones de ingeniería;
- acciones mecánicas;
- mantenimiento;
- comunicación entre integrantes del equipo.

Las herramientas especializadas pueden resolver correctamente la
adquisición y el análisis de telemetría. Sin embargo, no necesariamente
conservan todo el contexto humano, operativo y técnico que conduce desde
una observación hasta una decisión y su resultado posterior.

## 3. Planteamiento actual del problema

Algunos pequeños equipos de karting y grassroots motorsport pueden tener
dificultades para conservar y recuperar el razonamiento completo que
conecta una sesión con la siguiente.

La información puede distribuirse entre personas, conversaciones,
papeles, notas y diferentes herramientas. Como consecuencia, puede
resultar difícil reconstruir:

- qué reportó el piloto;
- qué mostraron los datos disponibles;
- qué problema fue identificado;
- qué causa se consideró;
- qué decisión tomó el equipo;
- qué acción se realizó;
- qué ocurrió en la sesión siguiente;
- qué aprendizaje debe conservarse.

Este problema no se considera universalmente validado. La investigación
debe determinar en qué tipos de equipos ocurre, con qué frecuencia y qué
impacto produce.

## 4. Problema central

> Cuando la información, las decisiones y los resultados de una sesión no
> quedan relacionados de forma clara, un equipo puede perder contexto,
> repetir investigaciones, olvidar aprendizajes o tener dificultades para
> preparar la siguiente sesión y futuros regresos a una pista.

RaceOps investigará si una herramienta de baja fricción puede resolver
este problema sin duplicar innecesariamente el trabajo realizado en
sistemas existentes.

## 5. Problemas relacionados

### 5.1 Fragmentación contextual

El feedback, los datos, las observaciones y las decisiones pueden
encontrarse en lugares diferentes o permanecer en la memoria de personas
específicas.

**Estado:** Parcialmente respaldado.

### 5.2 Pérdida de trazabilidad

Puede no existir una relación explícita entre una observación, la
hipótesis formulada, la acción realizada y el resultado obtenido.

**Estado:** Parcialmente respaldado.

### 5.3 Conversión de análisis en acciones

Un equipo necesita transformar una gran cantidad de información en pocas
prioridades útiles para la siguiente sesión.

**Estado:** Parcialmente respaldado.

### 5.4 Visibilidad inadecuada

Los integrantes necesitan diferente información. Mostrar toda la
información a todos puede revelar configuraciones confidenciales o
generar ruido innecesario.

**Estado:** Respaldado por evidencia.

### 5.5 Conocimiento histórico

Al regresar a una pista puede resultar útil recuperar problemas,
condiciones, decisiones y soluciones anteriores.

**Estado:** Parcialmente respaldado.

### 5.6 Fricción administrativa

Una nueva plataforma puede convertirse en un problema si exige volver a
capturar información, completar formularios largos o duplicar procesos.

**Estado:** Respaldado como riesgo importante.

## 6. Síntesis pública de evidencia

Tres conversaciones de descubrimiento anonimizadas produjeron estas señales
consolidadas:

- una sesión puede necesitar más contexto que el tiempo por vuelta;
- feedback del piloto y datos disponibles pueden complementarse;
- diferentes roles participan y no todos necesitan la misma información;
- algunas conclusiones se convierten en pocas prioridades y acciones;
- parte de la información técnica puede requerir confidencialidad;
- conservar decisiones anteriores puede ayudar al regresar a una pista.

La síntesis también produjo contraevidencia importante:

- para coaching puro, la telemetría puede ser suficiente;
- algunos equipos ya cuentan con procesos que funcionan;
- organización y disciplina no se sustituyen con software;
- una plataforma adicional puede fracasar si aumenta el trabajo manual.

Los registros individuales se mantienen fuera del repositorio público. Esta
síntesis no incluye nombres, citas, equipos ni configuraciones técnicas.

## 7. Contraevidencia

La investigación no permite afirmar que:

- todos los equipos sufran desorganización;
- todos necesiten una plataforma adicional;
- las herramientas actuales sean insuficientes;
- centralizar toda la información mejore automáticamente el trabajo;
- los equipos estén dispuestos a cambiar sus procesos;
- los usuarios acepten registrar manualmente muchos datos;
- exista disposición a pagar por RaceOps.

RaceOps debe coexistir con los procesos que ya funcionan y evitar
resolver problemas inexistentes.

## 8. Usuarios potencialmente afectados

### Driver

Puede necesitar recordar feedback, prioridades y evolución personal sin
recibir detalles técnicos confidenciales.

### Engineer / Data Engineer

Puede necesitar relacionar feedback, resultados, condiciones, hipótesis,
acciones y resultados posteriores.

### Mechanic

Puede necesitar conectar síntomas e incidentes con investigaciones,
reparaciones y disponibilidad del vehículo.

### Team Manager

Puede necesitar visibilidad general del estado operativo sin revisar
todos los canales técnicos.

### Administrator

Necesita controlar usuarios, roles, equipos y permisos.

Las necesidades de cada rol deberán confirmarse mediante más entrevistas
y pruebas.

## 9. Consecuencias potenciales

Si el problema existe y no se resuelve, pueden presentarse:

- pérdida de contexto entre sesiones;
- repetición de investigaciones;
- decisiones sin evidencia recuperable;
- aprendizajes que permanecen solamente en una persona;
- dificultad para comparar acciones y resultados;
- preparación deficiente al regresar a una pista;
- acceso excesivo o insuficiente a información;
- desconexión entre incidentes, mantenimiento y rendimiento.

La frecuencia y gravedad de estas consecuencias todavía deben medirse.

## 10. Trabajo que el usuario intenta realizar

La necesidad central se expresa de la siguiente manera:

> Cuando termina una sesión, quiero relacionar rápidamente lo que el
> piloto sintió, lo que mostraron los datos, lo que observó el equipo y
> lo que decidimos hacer, para preparar la siguiente sesión y conservar
> el aprendizaje para el futuro.

## 11. Pregunta de diseño

> ¿Cómo podríamos ayudar a un pequeño equipo de motorsport a preservar y
> recuperar el razonamiento entre sesiones, respetando la confidencialidad
> y sin aumentar significativamente su carga administrativa?

## 12. Respuesta propuesta

RaceOps propone un flujo que conecte:

```text
Evento
  ↓
Sesión
  ↓
Feedback + resultados + condiciones + observaciones
  ↓
Análisis
  ↓
Hipótesis
  ↓
Prioridades y acciones
  ↓
Siguiente sesión
  ↓
Resultado
  ↓
Conclusión e historial
```

Esta solución continúa siendo una hipótesis hasta probarse con usuarios
y flujos reales.

## 13. Supuestos pendientes

Deben validarse los siguientes supuestos:

- los equipos pierden información entre sesiones;
- reconstruir decisiones anteriores consume tiempo;
- el historial por pista aporta valor frecuente;
- el equipo aceptaría un flujo adicional si es suficientemente rápido;
- entre una y tres prioridades representan correctamente el trabajo real;
- la relación entre rendimiento y mantenimiento aporta valor;
- adjuntar o referenciar telemetría es suficiente para la primera versión;
- los niveles de visibilidad propuestos son comprensibles;
- los equipos utilizarían el sistema durante o entre sesiones.

## 14. Criterios de validación del problema

El problema obtendrá mayor respaldo si encontramos:

- el mismo patrón en participantes independientes;
- ejemplos recientes y concretos;
- evidencia de información perdida o difícil de recuperar;
- tiempo o trabajo adicional provocado por la fragmentación;
- decisiones que no pudieron reconstruirse;
- necesidad repetida de consultar información histórica;
- pruebas de que un prototipo reduce pasos o mejora claridad;
- uso voluntario del flujo durante una sesión real.

Las respuestas hipotéticas como “sí lo usaría” no serán suficientes por
sí solas.

## 15. Criterios de rechazo o cambio

RaceOps deberá reducir, cambiar o abandonar una funcionalidad si:

- duplica una herramienta existente sin aportar contexto adicional;
- exige más trabajo del valor que proporciona;
- los usuarios no pueden integrarla en su flujo real;
- sólo resulta relevante para un caso aislado;
- requiere infraestructura desproporcionada;
- intenta sustituir herramientas especializadas;
- no existe evidencia de que la información se consulte posteriormente.

## 16. Estado actual

El problema se considera:

> **Parcialmente validado y todavía en investigación.**

Existe evidencia suficiente para continuar Product Discovery y diseñar
un prototipo del flujo principal, pero no para afirmar que RaceOps tiene
validación de mercado o que todos los módulos propuestos son necesarios.
