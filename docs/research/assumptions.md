# RaceOps — Registro de hipótesis y supuestos

## 1. Información del documento

- **Versión:** 0.1
- **Estado:** Aprobado
- **Fuentes:** INT-001, INT-002, INT-003 y matriz de evidencia v0.1
- **Propósito:** Evitar que una idea de producto sea tratada como una necesidad comprobada.

## 2. Registro consolidado

| ID | Hipótesis o supuesto | Estado | Impacto si es falso | Prioridad |
|---|---|---|---|---|
| A-001 | Algunos equipos tienen dificultades para conectar feedback, datos y decisiones | Parcialmente respaldado | Crítico | Alta |
| A-002 | Ver feedback y datos relacionados ayuda a analizar una sesión | Parcialmente respaldado | Alto | Alta |
| A-003 | Mostrar 1–3 prioridades es útil para el piloto | Hipótesis | Alto | Alta |
| A-004 | Registrar observación → hipótesis → acción → resultado es viable entre sesiones | Hipótesis | Crítico | Alta |
| A-005 | El historial por pista ayuda cuando el equipo regresa meses después | Hipótesis | Alto | Alta |
| A-006 | Los distintos roles requieren información y permisos diferentes | Parcialmente respaldado | Alto | Alta |
| A-007 | La configuración técnica necesita protección especial | Hipótesis importante | Alto | Alta |
| A-008 | Referenciar o importar datos será más práctico que capturarlos nuevamente | Señal técnica por artefacto público; preferencia no validada | Alto | Alta |
| A-009 | El mantenimiento debe relacionarse con la sesión desde el primer MVP | Evidencia insuficiente | Medio | Media |
| A-010 | El registro principal puede completarse en aproximadamente dos minutos | Hipótesis de usabilidad | Crítico | Alta |
| A-011 | Los equipos aceptarían modificar su proceso actual | Evidencia insuficiente | Crítico | Alta |
| A-012 | Existe disposición a pagar por RaceOps | Evidencia insuficiente | Alto comercialmente | Baja por ahora |
| A-013 | Un frontend web pequeño es suficiente para validar el MVP | Demostrado técnicamente; usabilidad externa pendiente | Medio | Media |
| A-014 | Las métricas deben ser configurables según vehículo y categoría | Parcialmente respaldado | Medio | Media |
| A-015 | La telemetría en vivo no es necesaria para demostrar el valor inicial | Parcialmente respaldado | Bajo | Alta |

## 3. Validación de hipótesis críticas

### A-001 — Existe un problema real

Preguntaremos por situaciones concretas:

- ¿Cuándo fue la última vez que faltó información?
- ¿Qué consecuencia produjo?
- ¿Cómo lo resolvieron?
- ¿Cuánto tiempo o trabajo adicional generó?
- ¿Ocurre repetidamente?

**Criterio:** buscar ejemplos reales en varios participantes, no opiniones
generales.

### A-003 — Entre una y tres prioridades

Mostraremos un resumen con muchas métricas y otro con tres acciones claras.

**Criterio:** el usuario debe poder explicar inmediatamente qué hará durante
la siguiente sesión.

### A-004 — Flujo de decisiones

Probaremos este flujo con un caso real o realista:

```text
Feedback
    ↓
Evidencia
    ↓
Hipótesis
    ↓
Acción
    ↓
Resultado
```

**Criterio:** el equipo debe comprenderlo sin explicación extensa y poder
completarlo sin duplicar trabajo.

### A-005 — Historial por pista

Pediremos al participante que encuentre información de una visita anterior
utilizando su proceso actual.

**Criterio:** observar si realmente consulta el historial, cuánto tarda y
qué información busca.

### A-006 y A-007 — Roles y confidencialidad

Preguntaremos a cada rol:

- ¿Qué necesita consultar?
- ¿Qué puede modificar?
- ¿Qué no debería ver?
- ¿Qué información sería peligrosa si se comparte?

**Criterio:** encontrar reglas repetidas entre varios equipos antes de
aumentar la complejidad de permisos.

### A-010 — Uso rápido

En una prueba de prototipo pediremos registrar:

- feedback del piloto;
- una observación;
- una hipótesis;
- una prioridad;
- una acción.

**Objetivo inicial de diseño:** completar la captura principal en dos minutos
o menos, sin asistencia y sin campos innecesarios.

Este objetivo es una meta de usabilidad, no un hecho validado.

### A-011 — Adopción

No preguntaremos únicamente «¿usarías RaceOps?». Observaremos si el usuario:

- completa el flujo;
- entiende su utilidad;
- solicita volver a utilizarlo;
- introduce datos reales;
- continúa utilizándolo sin recordatorios.

La intención verbal no será considerada evidencia suficiente de adopción.

## 4. Decisiones que podemos mantener

- RaceOps complementará la telemetría.
- V1 utilizará una arquitectura de monolito modular.
- Existirá RBAC desde el inicio.
- La captura deberá ser rápida.
- No habrá telemetría en vivo.
- No habrá recomendaciones automáticas mediante IA.
- No habrá gestión financiera ni logística completa.
- No construiremos un sistema complejo de suscripciones en V1.

## 5. Funciones que no deben darse por aprobadas todavía

- importación CSV específica de AiM;
- historial avanzado por pista;
- mantenimiento dentro del primer flujo vertical;
- configuraciones completamente personalizables;
- recomendaciones automáticas;
- dashboards extensos;
- comercialización mediante suscripción;
- integraciones con herramientas externas.

Estas ideas no se eliminan, pero permanecen como hipótesis hasta conseguir
evidencia suficiente.

## 6. Estados de decisión

Cada supuesto podrá avanzar entre estos estados:

```text
Sin evidencia
    ↓
Señal
    ↓
Patrón candidato
    ↓
Parcialmente respaldado
    ↓
Respaldado por evidencia
```

También podrá cambiar a:

- Rechazado;
- Evidencia insuficiente;
- Pospuesto.

## 7. Regla de actualización

El estado deberá modificarse únicamente cuando aparezca evidencia nueva:
entrevistas independientes, observación de un flujo real, revisión de
artefactos, pruebas de producto o uso real.

Una solicitud aislada no bastará para aprobar un módulo grande.
