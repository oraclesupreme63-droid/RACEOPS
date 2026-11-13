# RaceOps — Hallazgos del dataset público de Kristianstad

## Alcance

Estos hallazgos provienen del replay técnico de resultados públicos FIA
Karting/Apex Timing. Describen compatibilidad del dominio y comportamiento de
las métricas. No son una prueba de usabilidad, adopción ni proceso interno del
equipo publicado.

## Métricas reproducidas por RaceOps

RaceOps calcula mejor vuelta, promedio redondeado en microsegundos y desviación
estándar poblacional sobre vueltas `VALID`.

| Métrica | Qualifying Heat D-F | Final | Cambio Final − Heat |
|---|---:|---:|---:|
| Vueltas elegibles | 13 | 25 | +12 |
| Mejor vuelta | 50.368 s | 50.348 s | -0.020 s |
| Promedio | 51.162231 s | 51.233280 s | +0.071049 s |
| Consistencia | 0.887217 s | 1.252891 s | +0.365674 s |

La mejor vuelta es ligeramente menor en la Final, pero el promedio es mayor y
la dispersión también. Las sesiones tienen distinta temperatura ambiente,
duración y contexto competitivo. Por lo tanto, `IMPROVED` no está respaldado;
el Outcome correcto es `INCONCLUSIVE`.

## Hallazgos clasificados

### PUB-001 — El modelo acepta timing representativo

- **Evidencia:** artefacto público + prueba PostgreSQL.
- **Resultado:** 38 vueltas y 114 sectores se conservan con precisión de
  microsegundos, orden y zona horaria.
- **Clasificación:** respaldado técnicamente.

### PUB-002 — Las condiciones reales pueden ser parciales

- **Evidencia:** el documento publica aire, clima y pista seca, pero no
  temperatura de pista.
- **Resultado:** los campos opcionales evitan inventar el valor faltante.
- **Clasificación:** respaldado por artefacto público.

### PUB-003 — Una mejor vuelta aislada no significa mejora global

- **Evidencia:** mejor vuelta, promedio y consistencia cambian en direcciones
  diferentes.
- **Resultado:** se conserva el Outcome `INCONCLUSIVE`.
- **Clasificación:** contraevidencia a una conclusión automática.

### PUB-004 — El timing no explica por qué ocurrió

- **Evidencia:** la publicación no contiene feedback, setup ni acción del
  equipo.
- **Resultado:** causa `UNKNOWN` y confianza baja; no se inventa una causa.
- **Clasificación:** límite demostrado del artefacto, no validación de RaceOps.

### PUB-005 — La procedencia debe sobrevivir a la importación

- **Evidencia:** sin fuente no puede distinguirse un dato publicado de un dato
  creado para el ejercicio.
- **Resultado:** el Event persistido conserva el enlace a FIA Karting; cada
  vuelta se marca `IMPORTED` y los campos sintéticos se enumeran aparte.
- **Clasificación:** requisito de integridad respaldado.

### PUB-006 — Importar parece razonable, pero sigue sin validación de usuario

- **Evidencia:** una sola pareja de sesiones contiene 38 vueltas y 114
  sectores; capturarlos manualmente introduciría trabajo y riesgo de error.
- **Resultado:** A-008 avanza de hipótesis pura a señal técnica.
- **Clasificación:** parcialmente respaldado; falta observar preferencias y
  formatos disponibles en equipos reales.

## Decisiones

- Conservar el dataset como regresión representativa.
- No crear recomendaciones automáticas a partir de diferencias de tiempo.
- No construir todavía un scraper específico del PDF de FIA Karting.
- Mantener CSV/importadores específicos como trabajo condicionado a evidencia.
- No usar este artefacto para aprobar mantenimiento, usabilidad o adopción.
- Exigir procedencia suficiente para cualquier importación futura.

## Pendientes reales

- observar a Driver, Engineer y Mechanic utilizando el flujo;
- confirmar si el promedio y la consistencia ayudan a una decisión real;
- conocer formatos exportables y permisos de reutilización de cada equipo;
- probar un ciclo donde feedback, acción y resultado sí estén autorizados;
- observar un segundo uso voluntario para obtener evidencia de adopción.
