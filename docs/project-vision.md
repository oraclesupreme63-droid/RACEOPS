# Visión del producto — RaceOps

## 1. Información del documento

- **Proyecto:** RaceOps
- **Versión:** 1.1
- **Estado:** Aprobado
- **Etapa:** Product Discovery
- **Fecha:** Por definir

Esta versión incorpora los hallazgos iniciales de INT-001, INT-002 e
INT-003 y reemplaza la visión centrada únicamente en centralizar datos.

## 2. Declaración de visión

RaceOps aspira a convertirse en una plataforma clara, rápida y confiable
que ayude a pequeños equipos de karting y grassroots motorsport a
preservar el contexto, las decisiones y los aprendizajes producidos entre
sesiones.

RaceOps deberá entregar:

> La información correcta, a la persona correcta, en el momento correcto
> y con suficiente contexto para tomar una decisión.

## 3. Propósito

El propósito de RaceOps es conservar la cadena de razonamiento que existe
alrededor de una sesión:

```text
Experiencia del piloto
        +
Resultados disponibles
        +
Condiciones de la sesión
        +
Observaciones técnicas
        ↓
Análisis
        ↓
Hipótesis
        ↓
Acción
        ↓
Resultado posterior
        ↓
Aprendizaje
```

La plataforma debe ayudar a transformar información dispersa en acciones
claras sin imponer una carga administrativa excesiva.

## 4. Posicionamiento

RaceOps está dirigido inicialmente a pequeños equipos de karting y
grassroots motorsport que necesiten mejorar la continuidad de su
información entre pilotos, ingenieros, mecánicos y responsables del equipo.

RaceOps no pretende reemplazar:

- AiM RaceStudio;
- MyChron;
- MoTeC;
- sistemas de adquisición de telemetría;
- dashboards del vehículo;
- software profesional del fabricante;
- experiencia y criterio de ingenieros, mecánicos o pilotos.

RaceOps complementará esas herramientas administrando el contexto
operativo, humano y técnico que existe alrededor de ellas.

## 5. Problema que buscamos validar

La investigación inicial indica que:

- una sesión produce más información que solamente tiempos por vuelta;
- el feedback del piloto y los datos deben compararse;
- diferentes integrantes participan en distintas partes del análisis;
- parte del conocimiento puede permanecer distribuido;
- algunos detalles técnicos deben mantenerse confidenciales;
- los hallazgos deben convertirse en pocas acciones claras;
- algunos equipos ya trabajan correctamente con sus herramientas actuales;
- una plataforma adicional puede fracasar si incrementa el trabajo manual.

Por ello, RaceOps no parte de la afirmación de que todos los equipos
necesitan una nueva plataforma.

El proyecto deberá demostrar en qué contextos el problema existe, con qué
frecuencia ocurre y si RaceOps puede resolverlo con menos fricción que las
alternativas actuales.

## 6. Propuesta de valor

Para pequeños equipos de karting y grassroots motorsport que necesitan
conservar el contexto técnico y operativo entre sesiones, RaceOps
relaciona feedback, resultados, observaciones, hipótesis, acciones y
conclusiones dentro de un mismo flujo.

A diferencia de una herramienta de telemetría, RaceOps no se concentra en
adquirir todos los canales del vehículo. Se concentra en ayudar al equipo
a comprender:

- qué ocurrió;
- por qué cree que ocurrió;
- qué decidió cambiar;
- quién necesita conocerlo;
- qué ocurrió después;
- qué debe recordarse en el futuro.

## 7. Experiencia deseada

Después de una sesión, el equipo debería poder utilizar RaceOps para:

1. consultar vueltas, sectores y condiciones relevantes;
2. registrar rápidamente el feedback del piloto;
3. añadir observaciones técnicas;
4. comparar el feedback con los datos disponibles;
5. formular una causa o hipótesis;
6. indicar el nivel de confianza;
7. definir pocas prioridades para la siguiente sesión;
8. asignar acciones de conducción, ingeniería o mecánica;
9. evaluar los resultados en la sesión siguiente;
10. conservar la conclusión en el historial.

Este flujo debe ser rápido y comprensible durante un fin de semana de
competencia.

## 8. Usuarios y valor esperado

### Team Manager

Obtiene visibilidad general de eventos, sesiones, pilotos, vehículos,
incidentes y mantenimiento sin necesidad de revisar todos los datos
técnicos.

### Driver

Consulta sus resultados, feedback y prioridades de mejora sin acceder
automáticamente a configuraciones técnicas confidenciales.

### Engineer / Data Engineer

Relaciona feedback, condiciones, resultados, observaciones, hipótesis,
acciones y comparaciones históricas.

### Mechanic

Consulta síntomas, incidentes, acciones mecánicas, mantenimiento y
disponibilidad del vehículo.

### Administrator

Gestiona usuarios, equipos, roles, permisos y configuración.

## 9. Principios de experiencia

RaceOps debe ser:

- **Rápido:** las acciones frecuentes deben requerir pocos pasos.
- **Claro:** cada usuario debe identificar rápidamente lo que necesita.
- **Contextual:** los datos deben estar relacionados con una sesión.
- **Accionable:** el análisis debe terminar en decisiones o prioridades.
- **Trazable:** debe ser posible conocer qué se decidió y qué ocurrió después.
- **Confidencial:** no todos los usuarios deben ver todos los detalles.
- **Configurable:** las métricas varían entre vehículos y categorías.
- **Honesto:** una hipótesis no debe presentarse como una certeza.
- **Complementario:** debe respetar las herramientas que ya funcionan.

## 10. Principios de diseño

Para reducir fricción se preferirán:

- valores predeterminados;
- plantillas;
- acciones rápidas;
- opciones seleccionables;
- asociaciones automáticas;
- marcas de tiempo automáticas;
- reutilización de información anterior;
- notas breves;
- formularios adaptados al rol;
- campos configurables cuando exista variación real.

Cada campo manual deberá justificar qué decisión permite tomar o qué
información ayuda a preservar.

## 11. Visibilidad y confidencialidad

Centralizar información no significa que todos puedan verla.

RaceOps deberá distinguir inicialmente:

- información general del equipo;
- información restringida según el rol;
- información técnica confidencial para ingeniería.

Ejemplo:

```text
Driver:
"El equipo trabaja en mejorar la estabilidad trasera."

Engineer:
Configuración exacta y análisis técnico utilizado para investigarla.
```

La primera versión utilizará RBAC y reglas explícitas de visibilidad.

## 12. Visión de RaceOps v1.0

RaceOps v1.0 deberá demostrar un flujo completo entre dos sesiones:

```text
Sesión inicial
    ↓
Feedback y resultados
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

La versión deberá incluir los datos maestros y controles necesarios para
soportar ese flujo, pero no intentará reproducir una plataforma profesional
de telemetría.

## 13. Inteligencia histórica

RaceOps deberá permitir recuperar evidencia histórica para responder:

- ¿qué ocurrió la última vez en esta pista?;
- ¿qué reportó el piloto?;
- ¿qué problema se investigó?;
- ¿qué acciones se realizaron?;
- ¿qué acción produjo una mejora?;
- ¿qué problemas mecánicos aparecieron?;
- ¿qué conclusiones siguen siendo relevantes?

RaceOps v1.0 recuperará información y evidencia. No generará
recomendaciones automáticas presentándose como un ingeniero virtual.

## 14. Visión futura

Después de la feria, RaceOps deberá probarse con usuarios reales.

Solamente con evidencia suficiente se evaluarán:

- importaciones más avanzadas;
- integraciones con sistemas externos;
- automatización adicional;
- funciones en vivo;
- recomendaciones basadas en datos;
- producto comercial;
- RaceOps Cloud;
- arquitectura multi-tenant;
- suscripciones y facturación.

Estas posibilidades no deben distraer el desarrollo del flujo principal.

## 15. Medición del éxito

RaceOps no se medirá principalmente por su cantidad de pantallas,
entidades o funciones.

Se evaluará por la capacidad de ayudar al equipo a responder rápidamente:

1. ¿Qué ocurrió?
2. ¿Qué evidencia tenemos?
3. ¿Por qué creemos que ocurrió?
4. ¿Qué decidimos hacer?
5. ¿Quién necesita conocerlo?
6. ¿Qué ocurrió en la siguiente sesión?
7. ¿Podemos encontrar esta información meses después?

Si RaceOps no puede responder estas preguntas con claridad, su conjunto
de funciones deberá revisarse.

## 16. North Star del producto

La medida principal de valor será:

> Sesiones que terminan con un aprendizaje trazable: evidencia, hipótesis,
> acción, resultado y conclusión.

Durante Product Discovery deberán definirse métricas verificables para
evaluar este resultado sin inventar objetivos numéricos antes de contar
con datos suficientes.
