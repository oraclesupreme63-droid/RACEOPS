# RaceOps — Estado de validación de problemas

## 1. Información del documento

- **Versión:** 0.1
- **Estado:** Preparado para Gate G1
- **Evidencia considerada:** INT-001, INT-002, INT-003, Evidence Matrix, Assumptions Register y Competitor Analysis
- **Propósito:** Determinar qué puede afirmarse, qué puede guiar provisionalmente el MVP y qué continúa sin demostrarse.

## 2. Advertencia de interpretación

El nombre de este documento no significa que RaceOps tenga validación de
mercado. Con tres entrevistas resumidas, sin observación directa ni prueba
de producto, ningún problema puede considerarse universalmente validado.

El documento distingue:

- afirmaciones suficientemente respaldadas para limitar el diseño;
- problemas parcialmente respaldados;
- hipótesis que deben probarse;
- ideas rechazadas o con evidencia insuficiente.

## 3. Afirmaciones que pueden limitar el diseño

### VC-001 — RaceOps no debe reemplazar la telemetría

Las entrevistas y la revisión de herramientas muestran que AiM RaceStudio,
MyChron y MoTeC ya cubren adquisición y análisis especializado.

- **Clasificación:** Respaldada por evidencia.
- **Consecuencia:** V1 no construirá adquisición, gráficas avanzadas,
  canales matemáticos ni telemetría en vivo.

### VC-002 — No todos los equipos necesitan otra plataforma

INT-002 aporta contraevidencia directa: algunos equipos funcionan
correctamente con herramientas y procesos existentes.

- **Clasificación:** Respaldada por evidencia como límite del mercado.
- **Consecuencia:** RaceOps no se presentará como necesidad universal.

### VC-003 — La carga administrativa es un riesgo crítico

Una solución que duplica la captura existente puede ser abandonada incluso
si técnicamente funciona.

- **Clasificación:** Respaldada por evidencia como riesgo.
- **Consecuencia:** La captura rápida y la eliminación de campos
  innecesarios serán restricciones del producto.

### VC-004 — La información no debe ser universalmente visible

INT-003 muestra que cierta configuración técnica puede mantenerse fuera de
la vista del piloto. INT-001 identifica distintos roles participantes.

- **Clasificación:** Parcialmente respaldada; impacto de seguridad alto.
- **Consecuencia:** V1 incluirá RBAC y reglas explícitas de visibilidad.

## 4. Problemas parcialmente respaldados

### VP-001 — El análisis de sesión puede requerir contexto adicional

INT-001 e INT-003 describen información más amplia que vueltas y sectores:
feedback, condiciones, observaciones y comportamiento del vehículo.

INT-002 limita la afirmación porque la telemetría puede ser suficiente para
coaching puro.

- **Estado:** Parcialmente respaldado.
- **Uso permitido:** Diseñar contexto opcional y breve.
- **No permite afirmar:** Que todos los equipos necesiten todos los campos.

### VP-002 — Los diferentes roles pueden necesitar información distinta

INT-001 identifica múltiples roles e INT-003 distingue entre la información
del piloto y la información técnica de ingeniería.

- **Estado:** Parcialmente respaldado.
- **Uso permitido:** Diseñar una matriz inicial de permisos.
- **Pendiente:** Entrevistas directas con mecánicos y Team Managers.

### VP-003 — El análisis puede convertirse en pocas acciones prioritarias

INT-003 describe la selección de aproximadamente tres áreas de mejora.
INT-001 menciona decisiones y ajustes entre sesiones.

- **Estado:** Parcialmente respaldado.
- **Uso permitido:** Probar una interfaz de una a tres prioridades.
- **No permite afirmar:** Que tres sea un límite universal.

### VP-004 — Parte del contexto puede quedar distribuida

INT-001 señala distribución entre personas, archivos y herramientas.
INT-002 advierte que utilizar varias herramientas no significa que el
proceso esté desorganizado.

- **Estado:** Parcialmente respaldado con contraevidencia.
- **Uso permitido:** Investigar casos concretos y diseñar sin asumir que
  centralizar siempre es mejor.

## 5. Hipótesis centrales todavía no demostradas

### VH-001 — La cadena completa aporta valor

```text
Observación
    ↓
Hipótesis
    ↓
Acción
    ↓
Resultado
```

La evidencia respalda partes del flujo, pero no se observó su registro
completo ni su uso repetido.

- **Estado:** Hipótesis prioritaria.
- **Prueba:** Prototipo y dos ciclos de sesión.

### VH-002 — El historial por pista mejora la preparación

INT-001 aporta una señal de conservación de información para regresar a una
pista, pero no se observó una búsqueda real.

- **Estado:** Hipótesis.
- **Prueba:** Pedir al usuario recuperar una sesión anterior.

### VH-003 — RaceOps puede usarse en aproximadamente dos minutos

El tiempo es un objetivo de diseño derivado del riesgo de fricción.

- **Estado:** Hipótesis de usabilidad.
- **Prueba:** Medición con prototipo, sin asistencia.

### VH-004 — Los equipos cambiarán su proceso

No existe evidencia de adopción ni uso real.

- **Estado:** Evidencia insuficiente.
- **Prueba:** Piloto voluntario durante varias sesiones.

### VH-005 — Existe disposición a pagar

No existe evidencia comercial.

- **Estado:** Evidencia insuficiente.
- **Decisión:** Posponer hasta después de validar utilidad y adopción.

## 6. Áreas con evidencia insuficiente para el primer flujo

| Área | Estado | Decisión actual |
|---|---|---|
| Mantenimiento completo | Evidencia insuficiente para el primer flujo | Posponer a una fase posterior |
| Importación CSV de AiM | Hipótesis técnica y de uso | Posponer hasta revisar archivos reales |
| Historial avanzado por pista | Hipótesis | Probar primero una consulta básica |
| Gestión financiera | Evidencia insuficiente | Fuera de V1 |
| Logística completa | Evidencia insuficiente | Fuera de V1 |
| Telemetría en vivo | No justificada | Fuera de V1 |
| Recomendaciones automáticas con IA | No justificadas | Fuera de V1 |
| Suscripciones y facturación | Sin evidencia comercial | Fuera de V1 |

## 7. Problema provisional para el MVP

> Algunos pequeños equipos de karting y grassroots motorsport pueden tener
> dificultades para conservar y recuperar el razonamiento que conecta el
> feedback, la evidencia disponible, una decisión y su resultado entre
> sesiones. RaceOps investigará si un flujo breve y con visibilidad por rol
> puede preservar esa cadena sin duplicar el trabajo de telemetría.

Las expresiones «algunos» y «pueden» son deliberadas. La evidencia actual
no permite generalizar.

## 8. Primer flujo recomendado

```text
Crear evento y sesión
        ↓
Asignar piloto y vehículo
        ↓
Registrar o referenciar resultados
        ↓
Capturar feedback breve
        ↓
Registrar observación e hipótesis
        ↓
Definir 1–3 prioridades y una acción
        ↓
Relacionar la siguiente sesión
        ↓
Registrar resultado y conclusión
```

Este flujo es un objeto de validación, no una solución confirmada.

## 9. Deuda de investigación

Antes de afirmar que el MVP está validado se necesitan:

- entrevistas con mecánicos;
- entrevista con Team Manager o propietario de equipo;
- perspectiva adicional de ingeniería;
- revisión autorizada de artefactos reales;
- prueba del flujo con usuarios;
- medición de tiempo y errores;
- al menos dos ciclos de sesión;
- evidencia de consulta histórica;
- evidencia de adopción voluntaria.

## 10. Resultado

Existe claridad suficiente para convertir el flujo provisional en
requisitos comprobables y en un prototipo futuro, siempre que:

- no se declare validación de mercado;
- la investigación continúe;
- las funciones no respaldadas permanezcan fuera del P0;
- el alcance pueda cambiar si aparece evidencia contradictoria.

