# RaceOps — Evaluación Gate G1: Problem Ready

## 1. Información del documento

- **Gate:** G1 — Problem Ready
- **Versión:** 0.1
- **Estado:** Aprobado condicionalmente
- **Fecha de evaluación:** 22 de octubre de 2026
- **Fase evaluada:** Fase 1 — Investigación y validación

## 2. Condición del gate

El roadmap define G1 como:

> Evidencia, contraevidencia e hipótesis registradas.

Pasar G1 no significa que RaceOps tenga validación de mercado. Significa
que existe claridad suficiente para especificar y probar un primer flujo
sin ocultar las incertidumbres actuales.

## 3. Comprobación de entregables

| Criterio | Evidencia | Resultado |
|---|---|---|
| Research Plan | `docs/research/research-plan.md` | Cumplido |
| Registros individuales | Archivo privado; política pública en `docs/research/interviews/README.md` | Cumplido con acceso restringido |
| Evidence Matrix | `docs/research/findings/evidence-matrix.md` | Cumplido |
| Assumptions Register | `docs/research/assumptions.md` | Cumplido |
| Contraevidencia representada | INT-002 y Evidence Matrix | Cumplido |
| Herramientas actuales investigadas | `docs/research/competitor-analysis.md` | Cumplido |
| Preguntas abiertas explícitas | `docs/research/findings/open-questions.md` | Cumplido |
| Estado de problemas | `docs/research/findings/validated-problems.md` | Cumplido |
| Problem Statement revisado | `docs/problem-statement.md`, versión 1.1 | Cumplido |
| Primer flujo identificado | Session Learning Loop | Cumplido provisionalmente |

## 4. Limitaciones abiertas

- Solamente existen tres entrevistas documentadas.
- Las fuentes disponibles son resúmenes, no transcripciones completas.
- No se observó directamente una sesión real.
- No se revisaron artefactos de trabajo reales.
- Faltan perspectivas directas de mecánicos y Team Managers.
- No existe prueba de usabilidad.
- No existe evidencia de adopción repetida.
- No existe validación comercial.

Estas limitaciones impiden declarar el producto validado, pero no impiden
especificar un flujo provisional y preparar su prueba.

## 5. Evaluación

| Dimensión | Estado |
|---|---|
| Claridad del problema | Suficiente para continuar, con lenguaje provisional |
| Separación entre evidencia e hipótesis | Adecuada |
| Contraevidencia | Incorporada |
| Delimitación frente a telemetría | Clara |
| Primer flujo | Identificado, todavía no probado |
| Cobertura de roles | Incompleta |
| Validación de uso | Pendiente |
| Validación de mercado | Pendiente |

## 6. Recomendación

**Resultado recomendado: APROBACIÓN CONDICIONAL.**

Esto permitiría avanzar a la Fase 2 — Ingeniería de requerimientos mientras
la investigación continúa en paralelo.

Condiciones:

1. El Session Learning Loop será un flujo para validar, no una verdad
   establecida.
2. Mantenimiento no formará parte del primer corte P0 salvo por referencias
   mínimas necesarias.
3. CSV, telemetría en vivo, IA, logística y funciones comerciales seguirán
   fuera del P0.
4. La matriz de permisos se considerará provisional hasta entrevistar roles
   faltantes.
5. Antes de declarar el MVP validado deberán realizarse pruebas con usuarios
   y sesiones repetidas.
6. La evidencia nueva podrá modificar requisitos y modelo de dominio.

## 7. Opciones de decisión

### Opción A — Aprobar G1 condicionalmente

Avanzar a Fase 2 y mantener la investigación como actividad transversal.

### Opción B — Mantener G1 abierto

No comenzar Fase 2 hasta conseguir entrevistas de mecánica, gestión e
ingeniería adicional.

### Opción C — Replantear RaceOps

Modificar el problema o el flujo principal antes de continuar.

## 8. Decisión registrada

- **Opción seleccionada:** Opción A — Aprobar G1 condicionalmente.
- **Fecha de decisión:** 22 de octubre de 2026.
- **Decisión del propietario:** Avanzar a Fase 2 y mantener la investigación
  como actividad transversal.
- **Condiciones:** Aceptadas según la sección 6 de este documento.

## 9. Resultado del gate

**G1 — PROBLEM READY: APROBADO CONDICIONALMENTE.**

RaceOps puede iniciar Ingeniería de requerimientos sin declarar validación
de mercado y conservando las hipótesis y limitaciones documentadas.
