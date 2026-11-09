# RaceOps — Informe de estado del proyecto

## 1. Corte ejecutivo

- **Fecha:** 9 de noviembre de 2026
- **Versión alcanzada:** `v0.2.0 — Operational Base`, publicada
- **Fase actual:** 8 — Session Learning Loop
- **Bloque actual:** 8.2 — Persistencia de Session implementada; espera aprobación
- **Bloqueador técnico actual:** ninguno

RaceOps ya es un backend ejecutable con identidad, permisos y cuatro recursos
operativos completos: Drivers, Vehicles, Tracks y Events. La Fase 7 fue
aprobada y publicada. La Fase 8 ya cuenta con contrato aprobado y persistencia
de Session verificada, todavía sin API. No se asigna un porcentaje global
artificial porque las fases futuras tienen alcances y validaciones diferentes.

## 2. Estado por etapa

| Etapa | Estado |
|---|---|
| Fases 0–4 | Definición, investigación inicial, requisitos, dominio y arquitectura aprobados; la investigación continúa |
| Fase 5 | Fundación técnica completada; Gate G5 aprobado |
| Fase 6 | Identidad y autorización completadas y aprobadas |
| Fase 7 | Completada, aprobada y publicada como `v0.2.0` |
| Fase 8 | Contrato aprobado; Bloque 8.2 implementado y pendiente de aprobación |
| Gate G6 | Pendiente hasta completar el flujo entre sesiones |

## 3. Qué funciona hoy

- FastAPI, PostgreSQL, SQLAlchemy, Alembic, Docker Compose y CI;
- health, readiness, Swagger/OpenAPI, errores RFC 9457 y logs seguros;
- Teams, Users, Memberships, login JWT, cinco Roles y aislamiento por Team;
- Drivers con vínculo opcional a User, activación y desactivación;
- Vehicles con disponibilidad y estados explícitos;
- Tracks y Events con fechas, filtros y ciclo de estado;
- Session persistida con asignación protegida por Team, estados independientes
  y bloqueo coherente de resultados;
- 145 pruebas, 94.95 % de cobertura y controles estáticos en verde;
- preservación de datos: no hay DELETE normal para estos recursos.

## 4. Qué falta

### Próximo objetivo: API de Session

Tras aprobar la persistencia, el Bloque 8.3 implementará crear, listar,
consultar y editar Sessions planificadas, asignación atómica, RBAC, alcance del
Driver y bloqueo del Track de Event. Después continuará el flujo Event →
Session → resultados → feedback → análisis → acciones → siguiente Session →
conclusión.

### Después del flujo central

- Fase 9: probarlo con datos y usuarios reales;
- Fase 10: mantenimiento conectado a síntomas y acciones;
- Fase 11: historial, reportes y comparación;
- Fase 12: frontend consolidado y de baja fricción;
- Fases 13–14: robustez, seguridad y rendimiento medido;
- Fases 17–18: demo confiable y publicación `v1.0.0`.

CSV y operaciones en vivo de Fases 15–16 siguen condicionadas por evidencia.
La validación comercial y RaceOps Cloud pertenecen a Fases 20–22, después de
la feria.

## 5. Contratiempos y riesgos

- El problema es real para algunos entrevistados, pero la adopción todavía no
  está demostrada; hay contraevidencia válida.
- Swagger es la interfaz de prueba actual; todavía no existe frontend de uso
  cotidiano.
- El acceso relacionado de Driver a Vehicle y Event ya puede sustentarse en la
  tabla Session, pero no se expondrá hasta aplicar los filtros HTTP del Bloque
  8.3.
- Las pruebas locales completas tardan varios minutos por Argon2 y PostgreSQL;
  por eficiencia se ejecutan al cierre de cada bloque y CI las confirma.
- La fecha oficial de la feria sigue sin publicarse.
- El archivo no rastreado `tatus` tiene origen desconocido; no se ha tocado.

## 6. Recomendación

Mantener la dirección. No conviene añadir más catálogos. Tras aprobar este
cierre, el trabajo debe concentrarse en una primera versión vertical y pequeña
de Session, demostrando la cadena observación → hipótesis → acción → resultado.
