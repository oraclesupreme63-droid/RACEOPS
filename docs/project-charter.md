# Project Charter — RaceOps

## 1. Información del documento

- **Proyecto:** RaceOps
- **Concepto:** Motorsport Team Operations & Performance Management Platform
- **Versión:** 1.1
- **Estado:** Aprobado
- **Etapa actual:** Product Discovery
- **Responsable:** Por definir
- **Fecha:** Por definir

Esta versión reemplaza el Project Charter 1.0 e incorpora los hallazgos
de las entrevistas INT-001, INT-002 e INT-003.

## 2. Propósito

RaceOps busca ayudar a pequeños equipos de karting y grassroots
motorsport a conservar el contexto, las decisiones y los aprendizajes
producidos alrededor de sus sesiones.

La plataforma relacionará:

- experiencia y feedback del piloto;
- resultados de vueltas y sectores;
- condiciones de la sesión;
- observaciones del vehículo;
- análisis técnico;
- hipótesis;
- prioridades;
- acciones;
- resultados posteriores;
- mantenimiento e historial.

RaceOps no pretende reemplazar sistemas especializados de adquisición
o análisis de telemetría. Su propósito es administrar el contexto
operativo y técnico que existe alrededor de esas herramientas.

## 3. Problema investigado

Durante un evento de motorsport se genera información proveniente de
pilotos, ingenieros, mecánicos, sistemas de cronometraje y herramientas
de telemetría.

La evidencia obtenida hasta el momento indica que:

- el feedback del piloto y la telemetría se utilizan de forma complementaria;
- distintos roles necesitan diferentes niveles de información;
- algunas decisiones técnicas deben mantenerse confidenciales;
- el análisis debe convertirse en acciones concretas para la siguiente sesión;
- parte del conocimiento histórico puede quedar distribuido entre personas,
  archivos y herramientas;
- algunos equipos ya operan correctamente con sus sistemas actuales;
- agregar más software puede generar fricción si exige demasiado trabajo manual.

Por lo tanto, todavía no se afirma que todos los equipos necesiten
RaceOps. La existencia, frecuencia y gravedad del problema continuará
validándose mediante investigación.

## 4. Tesis del producto

RaceOps debe proporcionar:

> La información correcta, a la persona correcta, en el momento correcto
> y con suficiente contexto para tomar una decisión.

El valor principal del producto no será almacenar una gran cantidad de
datos, sino preservar el ciclo de razonamiento entre sesiones:

```text
Observación
    ↓
Hipótesis
    ↓
Acción
    ↓
Siguiente sesión
    ↓
Resultado
    ↓
Aprendizaje
```

## 5. Visión

Convertir RaceOps en una plataforma clara, rápida y confiable que permita
a pequeños equipos de motorsport comprender qué ocurrió durante una
sesión, qué decisiones se tomaron, cuáles fueron sus resultados y qué
debe recordarse para el futuro.

## 6. Propuesta de valor

RaceOps permitirá que un equipo relacione el feedback del piloto, los
resultados de rendimiento, las observaciones técnicas y las acciones
realizadas sin sustituir las herramientas especializadas que ya utiliza.

La plataforma deberá ayudar a responder:

1. ¿Qué ocurrió durante la sesión?
2. ¿Qué reportó el piloto?
3. ¿Qué mostraron los datos disponibles?
4. ¿Qué cambió en el vehículo?
5. ¿Qué problema fue identificado?
6. ¿Qué decisión tomó el equipo?
7. ¿Qué debe probarse en la siguiente sesión?
8. ¿La acción produjo una mejora?
9. ¿Qué debe recordar el equipo al regresar a esta pista?

## 7. Usuarios iniciales

### Team Manager

Necesita visibilidad general sobre eventos, pilotos, vehículos,
incidentes, sesiones y mantenimiento.

### Driver

Consulta sus sesiones, resultados, feedback y prioridades de mejora.
No obtiene acceso automático a configuraciones técnicas confidenciales.

### Engineer / Data Engineer

Analiza sesiones, feedback, condiciones, datos disponibles, hipótesis,
acciones y comparaciones históricas.

### Mechanic

Consulta vehículos, síntomas, incidentes, acciones mecánicas,
mantenimiento e historial de componentes o servicios.

### Administrator

Administra usuarios, equipos, roles, permisos y configuración del sistema.

Estos usuarios y sus necesidades continuarán validándose.

## 8. Objetivo general

Diseñar, construir y validar un MVP web de RaceOps que permita a un
pequeño equipo registrar y consultar el ciclo completo entre dos sesiones:
resultados, feedback, análisis, hipótesis, acciones y efectos posteriores,
aplicando permisos por rol, reglas de negocio, pruebas y documentación.

## 9. Alcance de RaceOps v1.0

RaceOps v1.0 contempla:

- autenticación y autorización;
- equipos, usuarios y roles;
- pilotos;
- vehículos;
- pistas;
- eventos;
- sesiones;
- asignación de piloto y vehículo;
- resultados de vueltas y sectores;
- feedback del piloto;
- condiciones de pista y sesión;
- observaciones del vehículo;
- referencias o archivos de telemetría;
- análisis de sesión;
- causas o hipótesis con nivel de confianza;
- prioridades para la siguiente sesión;
- acciones de conducción, ingeniería o mecánica;
- evaluación del resultado de una acción;
- mantenimiento e historial del vehículo;
- consulta histórica por pista, evento, vehículo o piloto;
- visibilidad de información según el rol;
- reporte resumido de sesión o evento;
- interfaz web de baja fricción;
- pruebas y documentación.

## 10. Flujo vertical prioritario

Antes de ampliar el sistema, RaceOps deberá completar correctamente este
flujo:

1. Crear un evento.
2. Crear una sesión.
3. Asignar piloto y vehículo.
4. Registrar resultados de vueltas y sectores.
5. Registrar feedback del piloto.
6. Añadir condiciones y observaciones técnicas.
7. Analizar la sesión.
8. Registrar una hipótesis con nivel de confianza.
9. Definir entre una y tres prioridades.
10. Registrar una acción.
11. Ejecutar la siguiente sesión.
12. Comparar el resultado.
13. Clasificar la acción como mejora, empeoramiento o resultado no concluyente.
14. Conservar el aprendizaje en el historial.

Este flujo tiene prioridad sobre la creación simultánea de módulos
independientes.

## 11. Fuera del alcance de v1.0

RaceOps v1.0 no incluirá:

- reemplazo de AiM RaceStudio, MyChron o MoTeC;
- ingestión de telemetría en tiempo real;
- recomendaciones automáticas mediante inteligencia artificial;
- transcripción automática de radio;
- estrategia profesional de nivel Formula;
- gestión financiera avanzada;
- logística completa de viajes;
- ERP de inventario y refacciones;
- facturación;
- suscripciones;
- arquitectura SaaS multi-tenant comercial;
- aplicación móvil nativa;
- funciones comerciales de RaceOps Cloud.

La importación CSV se considerará después de validar formatos y archivos
reales. Inicialmente podrá registrarse información manualmente o mediante
referencias a archivos.

## 12. Principios del producto

RaceOps se desarrollará siguiendo estos principios:

- investigación antes de expansión;
- evidencia antes de afirmaciones;
- una experiencia vertical antes de múltiples módulos;
- mínima entrada manual;
- información visible solamente para usuarios autorizados;
- acciones útiles antes que dashboards extensos;
- reglas de negocio explícitas;
- arquitectura sencilla y mantenible;
- seguridad y pruebas desde el inicio;
- documentación continua;
- medición antes de afirmar capacidad o rendimiento.

## 13. Estrategia de visibilidad

RaceOps v1.0 utilizará RBAC y reglas explícitas de visibilidad.

Los niveles iniciales considerados son:

- **TEAM:** información visible para integrantes autorizados del equipo;
- **ROLE_RESTRICTED:** información visible únicamente para determinados roles;
- **ENGINEERING_CONFIDENTIAL:** información técnica restringida a ingeniería
  y usuarios administrativos autorizados.

No se implementará un sistema ABAC complejo durante v1.0.

## 14. Criterios de éxito

RaceOps v1.0 será exitoso si permite:

- completar el flujo vertical prioritario;
- relacionar feedback, rendimiento, análisis, acciones y resultados;
- limitar correctamente la información según el rol;
- recuperar el historial de una pista o sesión;
- registrar información sin formularios innecesariamente largos;
- evitar operaciones inválidas mediante reglas de negocio;
- ejecutar los flujos principales con pruebas automatizadas;
- utilizar datos reales o razonablemente representativos;
- realizar una demostración estable;
- documentar la instalación, arquitectura, API y decisiones relevantes.

El éxito no se medirá por la cantidad de funcionalidades.

## 15. Evidencia y supuestos

### Respaldado por evidencia

- El feedback del piloto y los datos se complementan.
- Los roles requieren diferente información.
- Parte de la información técnica es confidencial.
- El análisis debe producir prioridades o acciones.
- RaceOps debe complementar herramientas existentes.

### Parcialmente respaldado

- La información se fragmenta entre personas y herramientas.
- El historial por pista puede aportar valor.
- La relación entre sesiones y mantenimiento puede aportar valor.
- Entre una y tres prioridades pueden facilitar la siguiente sesión.

### Hipótesis pendientes

- Los equipos adoptarían RaceOps dentro de su flujo real.
- RaceOps reduciría tiempo o errores de forma medible.
- Existe disposición a pagar.
- La importación CSV es suficientemente común.
- Las condiciones meteorológicas automáticas justifican una integración.

### Rechazado o insuficiente

- Todos los equipos necesitan RaceOps.
- Centralizar significa que todos deben ver toda la información.
- RaceOps debe reemplazar herramientas de telemetría.
- La telemetría en tiempo real es necesaria para v1.0.
- Un dashboard vistoso es más importante que el flujo de decisiones.

## 16. Restricciones

- tiempo académico limitado;
- acceso limitado a equipos y datos reales;
- formatos de telemetría diferentes;
- información técnica potencialmente confidencial;
- dependencia de la disponibilidad de entrevistados;
- riesgo de aumentar el trabajo administrativo;
- necesidad de mantener el MVP técnicamente manejable.

## 17. Riesgos principales

- construir a partir de pocas entrevistas;
- convertir señales aisladas en conclusiones generales;
- diseñar formularios con demasiados campos;
- crear un modelo rígido que no funcione en distintas categorías;
- ampliar el alcance hacia telemetría profesional;
- implementar permisos excesivamente complejos;
- depender de datos que no pueden obtenerse;
- no demostrar una mejora frente al flujo actual;
- intentar construir todos los módulos al mismo tiempo.

## 18. Enfoque técnico inicial

RaceOps utilizará inicialmente:

- Python;
- FastAPI;
- PostgreSQL;
- SQLAlchemy;
- Alembic;
- Pydantic;
- Pytest;
- JWT;
- password hashing;
- RBAC;
- Docker;
- Git y GitHub.

La arquitectura será un monolito modular.

Las decisiones importantes se documentarán mediante ADR cuando
corresponda.

## 19. Enfoque de investigación

Cada entrevista deberá registrar:

- rol y categoría del participante;
- flujo de trabajo actual;
- herramientas utilizadas;
- quién registra la información;
- cuándo se registra;
- quién puede verla;
- qué información se pierde;
- qué información se conserva;
- qué genera fricción;
- qué funciona correctamente;
- qué herramientas no reemplazarían.

Una entrevista representa una señal, no una verdad universal.

## 20. Aprobación

La aprobación de esta versión autoriza:

- continuar la investigación;
- actualizar la visión y el planteamiento del problema;
- rediseñar los requerimientos preliminares;
- modelar el nuevo flujo vertical;
- mantener la implementación detenida hasta alcanzar suficiente claridad
  sobre el dominio y los criterios de aceptación.

Cualquier cambio importante deberá relacionarse con evidencia, una
hipótesis explícita o una decisión documentada.
