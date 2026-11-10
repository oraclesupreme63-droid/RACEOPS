# RaceOps — Informe de estado del proyecto

## 1. Corte ejecutivo

- **Fecha:** 10 de noviembre de 2026
- **Versión alcanzada:** `v0.2.0 — Operational Base`, publicada
- **Fase actual:** 8 — Session Learning Loop
- **Bloque actual:** 8.5 — Laps, Sectors y métricas; espera aprobación
- **Bloqueador técnico actual:** ninguno

RaceOps ya es un backend ejecutable con identidad, permisos y cuatro recursos
operativos completos: Drivers, Vehicles, Tracks y Events. La Fase 7 fue
aprobada y publicada. La Fase 8 ya cuenta con contrato, persistencia y primera
API de Session, sus ciclos de estado y resultados de vuelta verificados. No se
asigna un porcentaje global artificial porque las fases futuras tienen alcances
y validaciones diferentes.

## 2. Estado por etapa

| Etapa | Estado |
|---|---|
| Fases 0–4 | Definición, investigación inicial, requisitos, dominio y arquitectura aprobados; la investigación continúa |
| Fase 5 | Fundación técnica completada; Gate G5 aprobado |
| Fase 6 | Identidad y autorización completadas y aprobadas |
| Fase 7 | Completada, aprobada y publicada como `v0.2.0` |
| Fase 8 | Bloques 8.1–8.4 aprobados; Bloque 8.5 pendiente de aprobación |
| Gate G6 | Pendiente hasta completar el flujo entre sesiones |

## 3. Qué funciona hoy

- FastAPI, PostgreSQL, SQLAlchemy, Alembic, Docker Compose y CI;
- health, readiness, Swagger/OpenAPI, errores RFC 9457 y logs seguros;
- Teams, Users, Memberships, login JWT, cinco Roles y aislamiento por Team;
- Drivers con vínculo opcional a User, activación y desactivación;
- Vehicles con disponibilidad y estados explícitos;
- Tracks y Events con fechas, filtros y ciclo de estado;
- Session planificada con API, asignación atómica, RBAC y filtros relacionados;
- Driver consulta sólo sus Sessions, Events y Vehicles asociados;
- Event no puede cambiar de Track después de tener su primera Session;
- Session puede iniciar, pausar, reanudar, completar o cancelar con timestamps;
- resultados terminales pueden bloquearse preservando actor y momento;
- Laps y Sectors permiten captura y consulta con duraciones en microsegundos;
- métricas excluyen vueltas no válidas y no inventan datos insuficientes;
- resultados bloqueados rechazan toda corrección normal;
- 162 pruebas registradas; CI exige al menos 90 % de cobertura;
- preservación de datos: no hay DELETE normal para estos recursos.

## 4. Qué falta

### Próximo objetivo: Conditions

Tras aprobar y publicar `v0.3.0`, el Bloque 8.6 añadirá un snapshot opcional de
condiciones por Session, con unidades explícitas y datos parciales. Después
continuará el flujo Event → Session → resultados → feedback → análisis →
acciones → siguiente Session → conclusión.

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
- El acceso relacionado de Driver ya funciona; todavía debe probarse con
  usuarios reales para confirmar que la información expuesta sea suficiente.
- Las pruebas locales completas tardan varios minutos por Argon2 y PostgreSQL;
  por eficiencia se ejecutan al cierre de cada bloque y CI las confirma.
- La fecha oficial de la feria sigue sin publicarse.
- El archivo no rastreado `tatus` tiene origen desconocido; no se ha tocado.

## 6. Recomendación

Mantener la dirección. No conviene añadir más catálogos ni importar telemetría
completa. Tras aprobar este cierre, el trabajo debe aportar el contexto mínimo
de la Session y avanzar hacia observación → hipótesis → acción → resultado.
