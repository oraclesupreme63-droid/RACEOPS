# EDT / WBS — RaceOps

## 1. Información del documento

- **Proyecto:** RaceOps
- **Versión:** 1.1
- **Estado:** Aprobado
- **Etapa:** Product Discovery
- **Fecha:** Por definir

## 2. Propósito

Esta Estructura de Desglose del Trabajo divide RaceOps en paquetes
pequeños, verificables y orientados a entregables.

La EDT se concentra primero en validar el problema y después en construir
un flujo vertical completo entre sesiones.

No representa todavía un calendario. Las fechas se definirán cuando sea
publicada la fecha oficial de la feria.

## 3. Criterios de organización

Los paquetes se clasifican como:

- **Obligatorio:** necesario para RaceOps v1.0.
- **Condicionado:** se realiza solamente si existe evidencia y tiempo.
- **Futuro:** no pertenece a RaceOps v1.0.

## 4. Estructura de Desglose del Trabajo

```text
1.0 Dirección y control del proyecto
│
├── 1.1 Definición del proyecto
├── 1.2 Gestión del alcance
├── 1.3 Gestión de riesgos
├── 1.4 Gestión del backlog
├── 1.5 Seguimiento del progreso
├── 1.6 Devlog y evidencia
└── 1.7 Control de cambios

2.0 Investigación y validación
│
├── 2.1 Plan de investigación
├── 2.2 Guion de entrevistas
├── 2.3 Registro de participantes
├── 2.4 Realización de entrevistas
├── 2.5 Documentación de entrevistas
├── 2.6 Matriz de evidencia
├── 2.7 Registro de hipótesis
├── 2.8 Registro de contraevidencia
├── 2.9 Identificación de patrones
└── 2.10 Actualización del problema

3.0 Ingeniería de requerimientos
│
├── 3.1 Identificación de actores
├── 3.2 Casos de uso
├── 3.3 Requerimientos funcionales
├── 3.4 Requerimientos no funcionales
├── 3.5 Criterios de aceptación
├── 3.6 Matriz de roles y permisos
├── 3.7 Clasificación de visibilidad
├── 3.8 Priorización del backlog
├── 3.9 Matriz de trazabilidad
└── 3.10 Definition of Done

4.0 Modelado del dominio
│
├── 4.1 Lenguaje ubicuo
├── 4.2 Entidades y objetos de valor
├── 4.3 Relaciones y cardinalidades
├── 4.4 Ciclo de vida de eventos
├── 4.5 Ciclo de vida de sesiones
├── 4.6 Ciclo de vida de vehículos
├── 4.7 Ciclo de vida de acciones
├── 4.8 Reglas de negocio
├── 4.9 Casos límite
├── 4.10 Modelo de confidencialidad
└── 4.11 Diagrama entidad-relación

5.0 Diseño de arquitectura
│
├── 5.1 Arquitectura general
├── 5.2 Definición de módulos
├── 5.3 Diseño de persistencia
├── 5.4 Diseño de API
├── 5.5 Estrategia de configuración
├── 5.6 Estrategia de errores
├── 5.7 Estrategia de logging
├── 5.8 Estrategia de pruebas
├── 5.9 Estrategia de seguridad
└── 5.10 Architectural Decision Records

6.0 Fundación técnica
│
├── 6.1 Repositorio Git
├── 6.2 Estructura del backend
├── 6.3 Gestión de dependencias
├── 6.4 Variables de entorno
├── 6.5 FastAPI
├── 6.6 PostgreSQL
├── 6.7 SQLAlchemy
├── 6.8 Alembic y migraciones
├── 6.9 Health check
├── 6.10 Manejo base de errores
├── 6.11 Logging base
├── 6.12 Configuración de Pytest
├── 6.13 Docker y Docker Compose
└── 6.14 Integración continua

7.0 Identidad, equipos y autorización
│
├── 7.1 Modelo Team
├── 7.2 Modelo User
├── 7.3 Registro o creación de usuarios
├── 7.4 Login
├── 7.5 Hashing de contraseñas
├── 7.6 Tokens de acceso
├── 7.7 Roles
├── 7.8 Pertenencia a equipo
├── 7.9 Separación de recursos por equipo
├── 7.10 Reglas de visibilidad
└── 7.11 Pruebas de autorización

8.0 Datos operativos básicos
│
├── 8.1 Drivers
│   ├── 8.1.1 Crear
│   ├── 8.1.2 Consultar
│   ├── 8.1.3 Actualizar
│   └── 8.1.4 Activar o desactivar
│
├── 8.2 Vehicles
│   ├── 8.2.1 Crear
│   ├── 8.2.2 Consultar
│   ├── 8.2.3 Actualizar
│   ├── 8.2.4 Cambiar estado
│   └── 8.2.5 Controlar disponibilidad
│
├── 8.3 Tracks
│   ├── 8.3.1 Crear
│   ├── 8.3.2 Consultar
│   ├── 8.3.3 Actualizar
│   └── 8.3.4 Registrar metadata mínima
│
└── 8.4 Events
    ├── 8.4.1 Crear
    ├── 8.4.2 Consultar
    ├── 8.4.3 Actualizar
    ├── 8.4.4 Cambiar estado
    └── 8.4.5 Asociar pista y fechas

9.0 Flujo vertical entre sesiones
│
├── 9.1 Gestión de sesiones
│   ├── 9.1.1 Crear sesión
│   ├── 9.1.2 Asignar piloto
│   ├── 9.1.3 Asignar vehículo
│   ├── 9.1.4 Iniciar
│   ├── 9.1.5 Pausar
│   ├── 9.1.6 Completar
│   └── 9.1.7 Cancelar
│
├── 9.2 Resultados
│   ├── 9.2.1 Registrar vueltas
│   ├── 9.2.2 Registrar sectores
│   ├── 9.2.3 Validar tiempos
│   ├── 9.2.4 Calcular mejor vuelta
│   ├── 9.2.5 Calcular promedio
│   ├── 9.2.6 Calcular peor vuelta
│   └── 9.2.7 Calcular consistencia básica
│
├── 9.3 Contexto de sesión
│   ├── 9.3.1 Registrar condiciones ambientales
│   ├── 9.3.2 Registrar condiciones de pista
│   ├── 9.3.3 Registrar observaciones del vehículo
│   └── 9.3.4 Referenciar telemetría disponible
│
├── 9.4 Feedback del piloto
│   ├── 9.4.1 Registrar feedback
│   ├── 9.4.2 Asociar zona o curva
│   ├── 9.4.3 Clasificar fase de conducción
│   ├── 9.4.4 Registrar severidad
│   ├── 9.4.5 Registrar confianza
│   └── 9.4.6 Aplicar visibilidad
│
├── 9.5 Análisis de sesión
│   ├── 9.5.1 Registrar hallazgo
│   ├── 9.5.2 Relacionar evidencia
│   ├── 9.5.3 Formular hipótesis
│   ├── 9.5.4 Clasificar causa
│   ├── 9.5.5 Registrar confianza
│   └── 9.5.6 Proteger información confidencial
│
├── 9.6 Prioridades y acciones
│   ├── 9.6.1 Definir prioridades
│   ├── 9.6.2 Limitar prioridades principales
│   ├── 9.6.3 Asignar responsable
│   ├── 9.6.4 Definir sesión objetivo
│   ├── 9.6.5 Actualizar estado
│   └── 9.6.6 Aplicar visibilidad
│
├── 9.7 Evaluación posterior
│   ├── 9.7.1 Relacionar sesión posterior
│   ├── 9.7.2 Comparar resultados
│   ├── 9.7.3 Clasificar resultado
│   ├── 9.7.4 Registrar conclusión
│   └── 9.7.5 Conservar aprendizaje
│
└── 9.8 Historial
    ├── 9.8.1 Consulta por pista
    ├── 9.8.2 Consulta por evento
    ├── 9.8.3 Consulta por piloto
    ├── 9.8.4 Consulta por vehículo
    └── 9.8.5 Consulta por sesión

10.0 Mantenimiento
│
├── 10.1 Registro de mantenimiento
├── 10.2 Tipos de intervención
├── 10.3 Inspecciones
├── 10.4 Reparaciones
├── 10.5 Historial del vehículo
├── 10.6 Relación con observaciones
├── 10.7 Relación con incidentes
├── 10.8 Cambio de disponibilidad
├── 10.9 Bloqueo de asignaciones inválidas
└── 10.10 Pruebas de reglas de negocio

11.0 Reportes y consulta
│
├── 11.1 Resumen de sesión
├── 11.2 Resumen de evento
├── 11.3 Resultados principales
├── 11.4 Feedback y hallazgos
├── 11.5 Prioridades y acciones
├── 11.6 Conclusiones
└── 11.7 Visibilidad del reporte

12.0 Frontend y experiencia de usuario
│
├── 12.1 Sistema visual básico
├── 12.2 Login
├── 12.3 Navegación por rol
├── 12.4 Gestión operativa
├── 12.5 Flujo de sesión
├── 12.6 Captura rápida de feedback
├── 12.7 Análisis y acciones
├── 12.8 Comparación posterior
├── 12.9 Historial
├── 12.10 Mantenimiento
├── 12.11 Manejo visual de errores
├── 12.12 Diseño responsive
└── 12.13 Pruebas de usabilidad

13.0 Calidad y validación
│
├── 13.1 Pruebas unitarias
├── 13.2 Pruebas de integración
├── 13.3 Pruebas de API
├── 13.4 Pruebas de autorización
├── 13.5 Pruebas de reglas de negocio
├── 13.6 Pruebas de casos límite
├── 13.7 Pruebas de regresión
├── 13.8 Revisión de seguridad
├── 13.9 Pruebas de rendimiento
├── 13.10 Pruebas con usuarios
├── 13.11 Corrección de incidencias
└── 13.12 Reporte de validación

14.0 Preparación y lanzamiento
│
├── 14.1 Datos de demostración
├── 14.2 Guion de demostración
├── 14.3 Presentación
├── 14.4 Material visual
├── 14.5 Ensayos
├── 14.6 Demostración de respaldo
├── 14.7 Video
├── 14.8 README final
├── 14.9 Documentación técnica
├── 14.10 Documentación de usuario
├── 14.11 Changelog
├── 14.12 Release notes
└── 14.13 Release v1.0.0

15.0 Evidencia profesional
│
├── 15.1 Devlog
├── 15.2 Capturas y demostraciones
├── 15.3 Decisiones técnicas
├── 15.4 Resultados de pruebas
├── 15.5 Material de portafolio
└── 15.6 Publicaciones seleccionadas

16.0 Trabajo condicionado
│
├── 16.1 Importación CSV
├── 16.2 Integración meteorológica
├── 16.3 Archivos de telemetría
├── 16.4 Actualizaciones en vivo
├── 16.5 Leaderboard
├── 16.6 Alertas automáticas
├── 16.7 Comparaciones avanzadas
└── 16.8 Módulo independiente de incidentes

17.0 Evolución posterior a v1.0
│
├── 17.1 Validación posterior a la feria
├── 17.2 Validación comercial
├── 17.3 Decisión de producto
├── 17.4 Propuesta RaceOps Cloud
├── 17.5 Diseño multi-tenant
├── 17.6 Suscripciones y facturación
└── 17.7 Backlog comercial
```

## 5. Prioridad de los paquetes

### Obligatorios para v1.0

- 1.0 Dirección y control;
- 2.0 Investigación y validación;
- 3.0 Ingeniería de requerimientos;
- 4.0 Modelado del dominio;
- 5.0 Diseño de arquitectura;
- 6.0 Fundación técnica;
- 7.0 Identidad y autorización;
- 8.0 Datos operativos;
- 9.0 Flujo vertical;
- 10.0 Mantenimiento básico;
- 11.0 Reportes;
- 12.0 Frontend;
- 13.0 Calidad;
- 14.0 Preparación y lanzamiento;
- 15.0 Evidencia profesional.

### Condicionados

- 16.0 Trabajo condicionado.

### Fuera de v1.0

- 17.0 Evolución posterior.

## 6. Dependencias principales

| Paquete | Depende principalmente de |
|---|---|
| Requerimientos | Investigación y alcance |
| Modelo del dominio | Requerimientos |
| Arquitectura | Dominio y requisitos no funcionales |
| Fundación técnica | Arquitectura |
| Autenticación | Fundación técnica y matriz de permisos |
| Datos operativos | Fundación técnica y dominio |
| Flujo vertical | Datos operativos, autorización y reglas |
| Mantenimiento | Vehículos, sesiones y observaciones |
| Frontend | Contratos de API y flujos aprobados |
| Calidad final | Implementación y criterios de aceptación |
| Release | Calidad, documentación y demo |

La investigación, las pruebas y la documentación continuarán durante
todo el proyecto; no se ejecutarán únicamente al final.

## 7. Criterio de finalización de un paquete

Un paquete se considerará terminado cuando:

- su entregable existe;
- cumple los criterios de aceptación;
- respeta las reglas de negocio;
- incluye validaciones;
- maneja errores relevantes;
- tiene pruebas cuando corresponde;
- actualiza la documentación;
- pasa integración continua;
- cuenta con evidencia de revisión.

## 8. Control de la EDT

Agregar un paquete nuevo requerirá:

1. identificar la evidencia que lo respalda;
2. determinar si pertenece a v1.0;
3. revisar dependencias;
4. evaluar impacto en tiempo y riesgo;
5. actualizar alcance, backlog y trazabilidad;
6. aprobar el cambio antes de implementarlo.

La EDT se actualizará cuando cambie el alcance aprobado, no para registrar
cada pequeño detalle de implementación.
