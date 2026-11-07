# RaceOps — Backlog priorizado

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G2
- **Método:** Prioridad P0–P3, dependencias y cortes verticales
- **Regla:** No iniciar P1 mientras el flujo P0 correspondiente sea inestable

## 2. Orden de construcción

| Orden | Epic | Resultado verificable | Prioridad |
|---:|---|---|---:|
| 1 | EP-00 Fundación técnica | API, base de datos, migraciones, pruebas, Docker, CI y health | P0 técnico |
| 2 | EP-01 Identidad y aislamiento | Login, equipo, rol y denegaciones comprobadas | P0 |
| 3 | EP-02 Base operativa | Piloto, vehículo, pista y evento disponibles | P0 |
| 4 | EP-03 Sesión y resultados | Sesión válida, ciclo, vueltas, sectores y bloqueo | P0 |
| 5 | EP-04 Contexto y feedback | Condiciones opcionales, feedback y observaciones | P0 |
| 6 | EP-05 Análisis | Análisis, hipótesis, confianza y visibilidad | P0 |
| 7 | EP-06 Próxima sesión | Prioridades y acciones con responsable | P0 |
| 8 | EP-07 Resultado | Acción evaluada mediante sesión posterior | P0 |
| 9 | EP-08 Memoria operativa | Cadena recuperable y resumen filtrado | P0 |
| 10 | EP-09 Validación | Prueba con datos representativos y usuarios | P0 de validación |
| 11 | EP-10 Referencias externas | Referencia autorizada de telemetría | P1 |
| 12 | EP-11 Mantenimiento | Inspección, reparación, disponibilidad e historial | P1 |
| 13 | EP-12 Reportes ampliados | Evento, impresión y comparaciones | P1 |
| 14 | EP-13 Importación CSV | Validación y normalización de un formato comprobado | P2 |

## 3. Backlog P0

### EP-00 — Fundación técnica

| ID | Elemento | Dependencia | Criterio de salida |
|---|---|---|---|
| BL-001 | Estructura FastAPI modular | Ninguna | Aplicación inicia |
| BL-002 | PostgreSQL y SQLAlchemy | BL-001 | Conexión comprobada |
| BL-003 | Alembic | BL-002 | Migración reproducible |
| BL-004 | Pytest y pruebas de integración | BL-001 | Suite ejecutable |
| BL-005 | Docker Compose | BL-002 | Stack inicia documentadamente |
| BL-006 | Logging y formato de errores | BL-001 | Error trazable sin secretos |
| BL-007 | `GET /health` | BL-001 | Respuesta comprobada |
| BL-008 | CI | BL-004 | Verificaciones automáticas |

### EP-01 — Identidad y aislamiento

| ID | Elemento | Historias | RF | AC |
|---|---|---|---|---|
| BL-009 | Usuario, equipo y membresía | US-001, US-002 | RF-001–RF-006 | AC-001–AC-003 |
| BL-010 | Hash de contraseña y autenticación | US-001 | RF-001–RF-003 | AC-001, AC-002 |
| BL-011 | RBAC en servidor | US-002 | RF-004–RF-008 | AC-003, AC-004 |
| BL-012 | Visibilidad de contenido | US-002, US-017 | RF-007, RF-008 | AC-004 |

### EP-02 — Base operativa

| ID | Elemento | Historias | RF | AC |
|---|---|---|---|---|
| BL-013 | Pilotos y activación | US-003 | RF-013–RF-017 | AC-005, AC-008 |
| BL-014 | Vehículos y estado básico | US-004 | RF-018–RF-021 | AC-006, AC-008 |
| BL-015 | Pistas | US-005 | RF-024, RF-025 | AC-007 |
| BL-016 | Eventos | US-005 | RF-026–RF-029 | AC-007 |

### EP-03 — Sesión y resultados

| ID | Elemento | Historias | RF | AC |
|---|---|---|---|---|
| BL-017 | Crear sesión y asignar | US-006 | RF-031–RF-034 | AC-009, AC-010 |
| BL-018 | Ciclo de sesión | US-007 | RF-035–RF-041 | AC-011, AC-012 |
| BL-019 | Bloqueo de resultados | US-007 | RF-040–RF-042 | AC-012, AC-013 |
| BL-020 | Vueltas | US-008 | RF-045–RF-051 | AC-014, AC-016 |
| BL-021 | Sectores opcionales | US-008 | RF-055–RF-058 | AC-015 |
| BL-022 | Métricas básicas | US-008 | RF-063, RF-064, RF-066, RF-068, RF-069 | AC-016 |

### EP-04 — Contexto y feedback

| ID | Elemento | Historias | RF | AC |
|---|---|---|---|---|
| BL-023 | Condiciones opcionales | US-009 | RF-070, RF-072, RF-073, RF-076, RF-078 | AC-017, AC-033 |
| BL-024 | Feedback del Driver | US-010 | RF-079, RF-081–RF-087 | AC-018 |
| BL-025 | Feedback verbal | US-011 | RF-080, RF-081, RF-086 | AC-019 |
| BL-026 | Observaciones | US-012 | RF-089, RF-092, RF-094, RF-095 | AC-020 |

### EP-05 — Análisis

| ID | Elemento | Historias | RF | AC |
|---|---|---|---|---|
| BL-027 | Análisis contextual | US-013 | RF-096, RF-097, RF-107 | AC-021 |
| BL-028 | Hipótesis y confianza | US-013 | RF-099, RF-100, RF-103, RF-104 | AC-021, AC-022 |
| BL-029 | Confidencialidad técnica | US-013, US-017 | RF-105, RF-106 | AC-004, AC-021 |

### EP-06 — Próxima sesión

| ID | Elemento | Historias | RF | AC |
|---|---|---|---|---|
| BL-030 | Prioridades | US-014 | RF-108–RF-110, RF-112, RF-113 | AC-023, AC-024 |
| BL-031 | Acciones y responsables | US-015 | RF-115–RF-118, RF-120, RF-121 | AC-025, AC-026 |

### EP-07 — Resultado

| ID | Elemento | Historias | RF | AC |
|---|---|---|---|---|
| BL-032 | Evaluación posterior | US-016 | RF-123–RF-130 | AC-027, AC-028 |
| BL-033 | Actualizar hipótesis desde conclusión | US-016 | RF-126–RF-128 | AC-022, AC-027 |

### EP-08 — Memoria operativa

| ID | Elemento | Historias | RF | AC |
|---|---|---|---|---|
| BL-034 | Cadena de aprendizaje | US-018 | RF-128, RF-152–RF-159 | AC-029, AC-030 |
| BL-035 | Resumen de sesión | US-017, US-019 | RF-161, RF-162, RF-164–RF-167 | AC-031, AC-032 |

### EP-09 — Validación

| ID | Elemento | Dependencia | Criterio de salida |
|---|---|---|---|
| BL-036 | Dataset representativo | EP-08 | Sin información sensible no autorizada |
| BL-037 | Prueba del flujo completo | BL-036 | Session Learning Loop completado |
| BL-038 | Prueba de permisos por rol | EP-08 | Casos positivos y negativos aprobados |
| BL-039 | Prueba de captura rápida | EP-04 | Tiempo y errores registrados |
| BL-040 | Dos ciclos de sesión | EP-07 | Acción y resultado recuperables |

## 4. Backlog no P0

| ID | Elemento | Prioridad | Condición de entrada |
|---|---|---:|---|
| BL-041 | Referencia de archivo/fuente de telemetría | P1 | Flujo P0 estable |
| BL-042 | Mantenimiento e historial mecánico | P1 | Validación con Mechanics |
| BL-043 | Resumen de evento | P1 | Resumen de sesión estable |
| BL-044 | Vista imprimible | P1 | Necesidad de presentación confirmada |
| BL-045 | Importación CSV | P2 | Archivo real, permiso y formato validados |
| BL-046 | Integración meteorológica | P2 | Evidencia de valor y resiliencia |
| BL-047 | Alertas de servicio | P2 | Mantenimiento usado y datos suficientes |
| BL-048 | Telemetría en vivo | P3 | Fuera de V1 |
| BL-049 | Recomendaciones automáticas con IA | P3 | Fuera de V1 |
| BL-050 | Suscripciones y facturación | P3 | Sólo tras validación comercial |

## 5. Reglas de prioridad

1. La prioridad no cambia por atractivo visual o dificultad técnica.
2. Seguridad, integridad y pruebas necesarias acompañan cada elemento.
3. Un P1 puede investigarse, pero no desplaza trabajo P0 incompleto.
4. Un P2 necesita evidencia y capacidad disponible.
5. EP-00 a EP-08 producen el primer flujo; EP-09 demuestra si puede usarse.
