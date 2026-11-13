# RaceOps — Reporte del Bloque 9.3: dataset y ensayo interno

## Estado

- **Fecha:** 13 de noviembre de 2026
- **Resultado:** implementado y ensayado; pendiente de aprobación del
  propietario
- **Siguiente bloque:** 9.4 — pruebas con participantes

## Entregado

- dataset sintético congelado como `phase-9-v1`;
- loader tipado que valida el dataset antes de escribir datos;
- comando local transaccional para crear cinco cuentas por Role;
- contraseña solicitada de forma interactiva y producción bloqueada;
- dos Sessions con condiciones, vueltas y sectores no ideales;
- instancia `round-1` utilizada para el ensayo interno;
- instancia limpia `pilot-round-1` reservada para participantes;
- pruebas unitarias e integración PostgreSQL del generador;
- guía reproducible del escenario y sus preguntas abiertas.

## Ensayo realizado

Desde `/app/` se ejecutó:

```text
Driver Feedback
→ Observation
→ Analysis + evidence
→ Hypothesis MEDIUM
→ Driver/Mechanic Priorities
→ Mechanical Action
→ Mechanic execution
→ INCONCLUSIVE Outcome
→ authorized Learning Chain
```

El flujo se completó con Driver, Engineer y Mechanic. Finalmente se abrió la
cadena como Engineer y como Driver para comprobar que el segundo no recibiera
razonamiento ni conclusiones confidenciales.

## Clasificación

- **Respaldado técnicamente:** el recorrido vertical puede completarse desde
  el cliente contra la API real y conserva su historial.
- **Respaldado técnicamente:** las proyecciones por Role impiden que Driver
  reciba Analysis, Hypothesis y detalle confidencial.
- **Parcialmente respaldado:** los datos incompletos y la incertidumbre se
  representan sin bloquear el flujo.
- **Hipótesis:** las transiciones de una Action ayudan a coordinar sin añadir
  demasiada fricción.
- **Hipótesis:** Mechanic puede necesitar un resumen compartido del feedback
  del Driver; no se ampliaron permisos sin observar a ese Role.
- **No validado todavía:** velocidad, comprensión y uso sin ayuda por personas
  del nicho.

## Contratiempos y correcciones

- El ensayo automatizado de clics necesitó esperar cada recarga antes de la
  siguiente transición; el flujo humano no quedó bloqueado.
- No se encontró un P0 ni exposición de datos.
- Se evitó convertir la ausencia de feedback visible para Mechanic en un
  cambio inmediato: queda como pregunta explícita para la observación.

## Verificación técnica

- **231 pruebas aprobadas** en 84.19 s;
- cobertura total **91.66 %**, superior al umbral de 90 %;
- Ruff, mypy estricto y sintaxis JavaScript aprobados;
- dataset presente dentro de la distribución y la imagen Docker;
- migración finalizada, servicios saludables y respuestas `200` de
  `/health`, `/ready` y `/app/`.

## Punto de aprobación

Con aprobación comenzará el Bloque 9.4. Antes de cada sesión se confirmará el
consentimiento; no se usarán datos ni credenciales reales y las notas
individuales permanecerán fuera de Git.
