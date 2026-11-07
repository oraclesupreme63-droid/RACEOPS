# Alcance del producto — RaceOps

## 1. Información del documento

- **Proyecto:** RaceOps
- **Versión:** 1.2
- **Estado:** Refinado para Gate G2
- **Etapa:** Ingeniería de requerimientos
- **Fecha:** Por definir

## 2. Propósito

Este documento establece los límites de RaceOps v1.0.

Su objetivo es evitar que el proyecto crezca sin control y asegurar que
el desarrollo se concentre en un flujo útil, verificable y respaldado por
la investigación.

## 3. Objetivo del alcance

RaceOps v1.0 permitirá a un pequeño equipo de karting o grassroots
motorsport conservar el ciclo de aprendizaje entre sesiones:

```text
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

El sistema complementará las herramientas existentes de cronometraje y
telemetría. No intentará sustituirlas.

## 4. Alcance funcional obligatorio

### 4.1 Identidad y acceso

RaceOps incluirá:

- registro o creación controlada de usuarios;
- inicio y cierre de sesión;
- almacenamiento seguro de contraseñas;
- autenticación mediante tokens;
- roles;
- permisos;
- pertenencia a un equipo;
- separación de información entre equipos;
- reglas explícitas de visibilidad.

Roles iniciales:

- Administrator;
- Team Manager;
- Engineer / Data Engineer;
- Mechanic;
- Driver.

La separación por equipo en v1.0 es un requisito de seguridad. No implica
construir todavía una plataforma SaaS comercial multi-tenant.

### 4.2 Datos operativos básicos

RaceOps permitirá administrar la información mínima necesaria de:

- equipos;
- usuarios;
- pilotos;
- vehículos;
- pistas;
- eventos;
- sesiones.

Estos módulos existirán para soportar el flujo principal y no como CRUD
aislados sin propósito.

### 4.3 Sesiones

Una sesión podrá relacionarse con:

- evento;
- pista;
- piloto;
- vehículo;
- tipo de sesión;
- fecha y horario;
- estado;
- condiciones;
- resultados;
- feedback;
- observaciones;
- análisis;
- acciones;
- sesión posterior utilizada para comparar resultados.

Estados iniciales candidatos:

- `PLANNED`;
- `ACTIVE`;
- `PAUSED`;
- `COMPLETED`;
- `CANCELLED`.

Los estados definitivos se validarán durante el modelado del dominio.

### 4.4 Resultados de rendimiento

RaceOps permitirá registrar inicialmente:

- número de vuelta;
- tiempo de vuelta;
- tiempos de sectores cuando estén disponibles;
- mejor vuelta;
- promedio;
- peor vuelta;
- cantidad de vueltas;
- medidas básicas de consistencia.

Los resultados podrán introducirse manualmente durante la primera
iteración.

RaceOps no almacenará todos los canales posibles de telemetría dentro de
un esquema universal.

### 4.5 Feedback del piloto

El piloto o un usuario autorizado podrá registrar feedback asociado a una
sesión.

El feedback podrá incluir:

- zona o curva;
- fase de conducción;
- descripción;
- severidad;
- nivel de confianza;
- momento de registro.

Ejemplo:

```text
Curva: T4
Fase: Entrada
Feedback: Inestabilidad trasera durante el frenado
Severidad: Media
Confianza: Alta
```

La estructura definitiva deberá evitar formularios largos.

### 4.6 Condiciones y observaciones

Una sesión podrá conservar:

- temperatura ambiente;
- temperatura de pista cuando esté disponible;
- condición climática;
- condición general de pista;
- observaciones del vehículo;
- notas técnicas autorizadas.

Podrán existir datos opcionales como:

- presión de neumáticos;
- temperatura de neumáticos;
- temperatura del motor;
- presión de aceite;
- RPM;
- stagger;
- observaciones de frenos.

Estos datos no serán obligatorios para todas las categorías.

### 4.7 Análisis e hipótesis

Un usuario autorizado podrá registrar:

- área donde se perdió rendimiento;
- evidencia considerada;
- causa sospechada;
- clasificación de la causa;
- nivel de confianza;
- notas técnicas;
- visibilidad de la información.

Clasificaciones iniciales:

- técnica del piloto;
- configuración del vehículo;
- problema mecánico;
- neumáticos;
- pista o ambiente;
- desconocido.

Una hipótesis no deberá presentarse como un hecho confirmado.

### 4.8 Prioridades y acciones

RaceOps permitirá definir entre una y tres prioridades principales para
la siguiente sesión.

Las prioridades o acciones podrán dirigirse a:

- Driver;
- Engineer;
- Mechanic.

Cada acción deberá indicar:

- descripción;
- responsable;
- sesión de origen;
- sesión objetivo;
- estado;
- visibilidad;
- resultado posterior.

### 4.9 Resultado y aprendizaje

Después de una sesión posterior, una acción podrá clasificarse como:

- mejora observada;
- empeoramiento observado;
- sin cambio medible;
- resultado no concluyente;
- no evaluada.

El equipo podrá registrar una conclusión y conservarla en el historial.

### 4.10 Mantenimiento

**Prioridad refinada:** P1. Este módulo pertenece al alcance de RaceOps
v1.0, pero no al primer corte P0 aprobado condicionalmente en G1. La
disponibilidad básica del vehículo sí permanece en P0.

RaceOps permitirá:

- registrar intervenciones;
- consultar el historial de un vehículo;
- registrar inspecciones y reparaciones;
- relacionar mantenimiento con incidentes u observaciones;
- cambiar la disponibilidad del vehículo;
- impedir que un vehículo no disponible sea asignado a una sesión.

El mantenimiento avanzado por componentes e inventario no será
obligatorio para la primera iteración.

### 4.11 Historial

Los usuarios autorizados podrán consultar información anterior por:

- pista;
- evento;
- sesión;
- piloto;
- vehículo.

El historial deberá permitir recuperar:

- feedback;
- observaciones;
- hipótesis;
- acciones;
- resultados;
- conclusiones;
- mantenimiento relacionado.

### 4.12 Reportes

RaceOps v1.0 incluirá un reporte resumido de sesión o evento con:

- contexto;
- resultados principales;
- feedback;
- hallazgos;
- prioridades;
- acciones;
- conclusiones.

La exportación avanzada a múltiples formatos no es obligatoria para el
primer MVP.

## 5. Visibilidad y confidencialidad

RaceOps utilizará inicialmente tres niveles:

### TEAM

Información disponible para integrantes autorizados del equipo.

### ROLE_RESTRICTED

Información disponible solamente para roles específicos.

### ENGINEERING_CONFIDENTIAL

Información técnica disponible para Engineer y usuarios administrativos
expresamente autorizados.

V1 utilizará RBAC y reglas explícitas. No se construirá un motor complejo
de permisos ABAC.

## 6. Experiencia de usuario incluida

La interfaz deberá:

- funcionar en navegadores modernos;
- adaptarse a computadora y dispositivos móviles;
- presentar vistas según el rol;
- minimizar pasos y captura manual;
- utilizar valores predeterminados cuando sea seguro;
- completar asociaciones conocidas automáticamente;
- permitir acciones rápidas;
- evitar formularios con campos irrelevantes;
- mostrar claramente errores y estados.

El diseño visual deberá ser consistente y funcional, pero no se
priorizarán animaciones o personalizaciones avanzadas.

## 7. Alcance técnico

RaceOps v1.0 incluirá:

- API REST con FastAPI;
- PostgreSQL;
- SQLAlchemy;
- Alembic;
- Pydantic;
- autenticación y RBAC;
- validación de entrada;
- manejo consistente de errores;
- logging;
- pruebas automatizadas;
- Docker y Docker Compose;
- documentación de API;
- integración continua;
- frontend web;
- instrucciones de instalación y ejecución.

La arquitectura será un monolito modular.

## 8. Funcionalidades condicionadas a evidencia y tiempo

Las siguientes funcionalidades no pertenecen al núcleo obligatorio.
Solamente se implementarán si el flujo principal está estable y existe
evidencia suficiente:

- importación CSV;
- integración automática con clima;
- archivos de telemetría almacenados por RaceOps;
- actualizaciones mediante WebSocket o SSE;
- dashboard de sesión en vivo;
- leaderboard en vivo;
- métricas configurables avanzadas;
- comparación avanzada entre pilotos;
- comparación avanzada entre vehículos;
- alertas automáticas de mantenimiento;
- importación desde sistemas de cronometraje;
- incidentes como módulo independiente.

La falta de estas funciones no impedirá declarar completo el primer MVP.

## 9. Fuera del alcance de RaceOps v1.0

No se incluirán:

- reemplazo de AiM RaceStudio;
- reemplazo de MyChron;
- reemplazo de MoTeC;
- adquisición directa de telemetría en tiempo real;
- análisis completo de canales de telemetría;
- recomendaciones automáticas de conducción mediante IA;
- decisiones automáticas de configuración;
- transcripción de radio;
- estrategia profesional de carrera;
- logística completa;
- gestión financiera avanzada;
- facturación;
- suscripciones;
- inventario ERP;
- aplicación móvil nativa;
- arquitectura comercial multi-tenant;
- RaceOps Cloud;
- soporte para todas las categorías de motorsport.

## 10. Alcance de investigación

Durante el desarrollo continuará la investigación con:

- pilotos;
- ingenieros;
- especialistas en datos;
- mecánicos;
- coaches;
- Team Managers;
- organizadores cuando resulte relevante.

La investigación buscará confirmar:

- frecuencia del problema;
- consecuencias observables;
- flujo real posterior a una sesión;
- información que debe conservarse;
- información confidencial;
- herramientas actuales;
- fricciones existentes;
- disposición para utilizar otro sistema;
- cantidad aceptable de captura manual.

## 11. Restricciones

El alcance está condicionado por:

- tiempo académico disponible;
- acceso a usuarios y datos reales;
- confidencialidad de datos técnicos;
- variedad entre categorías y vehículos;
- formatos diferentes de telemetría;
- experiencia técnica del equipo de desarrollo;
- estabilidad necesaria para la feria.

## 12. Prioridades del proyecto

En caso de falta de tiempo, se conservará este orden:

1. Flujo completo entre dos sesiones.
2. Seguridad y visibilidad por rol.
3. Reglas de negocio e integridad.
4. Pruebas automatizadas.
5. Historial y recuperación de decisiones.
6. Experiencia de baja fricción.
7. Mantenimiento relacionado con sesiones.
8. Reportes.
9. Importaciones e integraciones.
10. Funciones en vivo y mejoras visuales.

## 13. Criterios de aceptación del alcance

El alcance principal estará completo cuando sea posible demostrar:

1. Un usuario autorizado crea un evento y una sesión.
2. Asigna un piloto y un vehículo disponibles.
3. Registra vueltas y sectores válidos.
4. El piloto registra feedback.
5. Ingeniería añade observaciones y una hipótesis.
6. Se definen prioridades y acciones.
7. Se crea o utiliza una sesión posterior.
8. Se comparan los resultados.
9. Se registra una conclusión.
10. El aprendizaje puede recuperarse desde el historial.
11. Un usuario no autorizado no puede consultar información confidencial.
12. Un vehículo no disponible no puede participar.
13. Los flujos principales cuentan con pruebas automatizadas.
14. La aplicación puede ejecutarse mediante instrucciones documentadas.

## 14. Control de cambios

Una funcionalidad nueva solamente podrá entrar al alcance cuando:

- exista evidencia suficiente;
- apoye directamente el flujo principal;
- tenga prioridad frente al trabajo pendiente;
- pueda implementarse y probarse dentro del tiempo disponible;
- no duplique innecesariamente herramientas existentes.

Toda propuesta se clasificará como:

- respaldada por evidencia;
- parcialmente respaldada;
- hipótesis;
- rechazada o con evidencia insuficiente.

## 15. Resultado esperado

RaceOps v1.0 no será evaluado por la cantidad de módulos construidos.

Será evaluado por su capacidad para conservar de manera rápida, segura y
comprensible la relación entre:

```text
Experiencia
+ Evidencia
+ Análisis
+ Decisión
+ Acción
+ Resultado
= Aprendizaje trazable
```
