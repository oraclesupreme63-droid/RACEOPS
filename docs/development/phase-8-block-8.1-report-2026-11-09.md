# RaceOps — Reporte del Bloque 8.1: contrato del flujo vertical

## 1. Estado

- **Fecha:** 9 de noviembre de 2026
- **Fase:** 8 — Session Learning Loop
- **Bloque:** 8.1 — Contrato y secuencia
- **Resultado:** aprobado por el propietario
- **Siguiente bloque:** 8.2 — Persistencia de Session

## 2. Trabajo realizado

- se publicó el cierre aprobado de Fase 7 como tag `v0.2.0`;
- se revisaron requisitos, aceptación, casos de uso, estados e invariantes;
- se definió la Session mínima sin telemetría ni campos preventivos;
- se separó Session Status de Results Status;
- se fijaron asignación atómica, límites del Driver y errores estables;
- se dividió Fase 8 en doce bloques con `v0.3` y `v0.4` intermedios;
- se alinearon comandos HTTP y paginación con las APIs ya publicadas.

## 3. Decisiones principales

`session_type` permanece flexible. Event queda inmutable respecto a Track desde
su primera Session. Driver sólo ve Sessions asignadas y los Events/Vehicles
relacionados. Completar actividad no bloquea resultados, de modo que el equipo
puede cargar vueltas después de regresar a pits.

No se añaden reglas de agenda, telemetría en vivo, IA, archivos o frontend.

## 4. Calidad y pruebas

Este bloque cambia documentación y contrato, no código ejecutable. No se
repite localmente la suite completa de 136 pruebas. La CI del commit validará
que documentación y cambios de guía no alteraron el backend; la última suite
funcional y el tag `v0.2.0` permanecen verdes.

## 5. Aprobación

El propietario aprobó el contrato y autorizó el Bloque 8.2: enums, modelo
SQLAlchemy, constraints, migración Alembic y pruebas de persistencia. La API
permanece en un bloque separado para revisar primero la integridad.
