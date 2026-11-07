# RaceOps — Matriz pública de evidencia

## 1. Información del documento

- **Versión:** 0.2 pública
- **Estado:** Aprobado
- **Fuentes:** tres conversaciones de descubrimiento anonimizadas
- **Privacidad:** registros individuales conservados en archivo privado
- **Propósito:** separar evidencia, contraevidencia e incertidumbre sin
  publicar información atribuible a participantes individuales

## 2. Síntesis consolidada

| Tema | Evidencia consolidada | Contraevidencia o límite | Evaluación actual |
|---|---|---|---|
| Telemetría y feedback | Pueden utilizarse de forma complementaria | La telemetría puede ser suficiente para coaching puro | Parcialmente respaldado |
| Contexto de sesión | Clima, vehículo, neumáticos y rendimiento pueden aportar contexto | La información necesaria cambia entre equipos | Parcialmente respaldado |
| Información fragmentada | Diferentes roles producen y consumen información | Usar varias herramientas no demuestra un problema | Hipótesis |
| Decisiones accionables | El análisis puede producir prioridades y acciones | Más software no garantiza mejores decisiones | Parcialmente respaldado |
| Prioridades limitadas | Reducir el análisis puede facilitar la siguiente sesión | El número exacto todavía no es un patrón validado | Hipótesis prioritaria |
| Historial por pista | Recuperar decisiones previas puede tener valor | No se observó uso repetido directamente | Hipótesis |
| Diferentes roles | Piloto, ingeniería y mecánica tienen necesidades distintas | Los procesos y límites varían entre equipos | Parcialmente respaldado |
| Confidencialidad técnica | Algunos datos pueden necesitar acceso restringido | Las reglas exactas requieren validación adicional | Hipótesis de alto impacto |
| Carga administrativa | La captura manual excesiva puede impedir adopción | No se midió todavía el tiempo aceptable | Riesgo respaldado |
| Mantenimiento conectado | Síntomas y causas mecánicas pueden relacionarse con sesiones | Evidencia insuficiente para priorizarlo en el primer flujo | Evidencia insuficiente |
| Adopción | No evaluada mediante uso repetido | Algunos equipos ya trabajan correctamente | Evidencia insuficiente |
| Disposición a pagar | No evaluada | No existe comprador validado | Evidencia insuficiente |

## 3. Patrones candidatos

### P-001 — La telemetría no debe reemplazarse

- **Clasificación:** Supported by evidence.
- **Decisión:** RaceOps registrará contexto, resultados y hallazgos asociados,
  pero no intentará sustituir AiM, RaceStudio, MyChron o MoTeC.

### P-002 — Feedback y datos pueden necesitar relacionarse

- **Clasificación:** Partially supported.
- **Decisión:** Mantener la relación en el flujo principal y permitir una
  captura breve u opcional según el equipo.

### P-003 — El análisis debe convertirse en una acción

- **Clasificación:** Partially supported.
- **Decisión provisional:**

```text
Observación
    ↓
Hipótesis
    ↓
Acción
    ↓
Resultado
```

El flujo deberá probarse con usuarios antes de considerarlo validado.

### P-004 — La plataforma debe minimizar el trabajo manual

- **Clasificación:** Supported by evidence as a product risk.
- **Decisión:** cada campo manual justificará qué decisión, comunicación o
  recuerdo ayuda a conservar.

### P-005 — Cada rol necesita distinta información

- **Clasificación:** Partially supported.
- **Decisión:** utilizar RBAC y reglas explícitas de visibilidad desde v1.

### P-006 — Parte de la información puede ser confidencial

- **Clasificación:** Hypothesis with significant security impact.
- **Decisión:** distinguir información del equipo, información restringida por
  rol e información técnica confidencial sin construir ABAC complejo.

## 4. Contraevidencia consolidada

La investigación contradice estas ideas:

- todos los equipos necesitan RaceOps;
- usar papel o varias aplicaciones significa desorganización;
- agregar funciones siempre aumenta el valor;
- RaceOps debe reemplazar herramientas de telemetría;
- todos los datos deben estar disponibles para todos;
- una entrevista demuestra una necesidad de mercado;
- una aplicación técnicamente avanzada será utilizada automáticamente.

## 5. Conclusión prudente

RaceOps puede investigar si un flujo ligero conserva el razonamiento entre
sesiones sin duplicar el trabajo que las herramientas actuales ya resuelven.
Todavía no existe evidencia suficiente para afirmar adopción, valor comercial
o utilidad universal.

Los detalles atribuibles a participantes no se publican. La trazabilidad
completa permanece en el repositorio privado de investigación.
