# RaceOps — Reporte del Bloque 7.2: persistencia operativa

## 1. Estado

- **Fecha:** 8 de noviembre de 2026
- **Fase:** 7 — Base operativa
- **Bloque:** 7.2 — Persistencia operativa
- **Resultado:** aprobado por el propietario
- **Siguiente bloque:** 7.3 — API de Drivers

## 2. Trabajo realizado

Se materializó el contrato aprobado de Driver, Vehicle, Track y Event sin
adelantar Session ni crear endpoints prematuros. La implementación incluye:

- enums de estado estables para Driver, Vehicle y Event;
- cuatro modelos SQLAlchemy con UUID y timestamps server-side;
- ownership obligatorio por Team;
- unicidad de Driver/User y Vehicle/identifier dentro del Team;
- relaciones compuestas que impiden Driver/User y Event/Track entre Teams;
- fechas coherentes para Event;
- claves foráneas restrictivas que preservan el historial;
- revisión Alembic reversible `20261108_0003_operations`.

## 3. Reglas protegidas por PostgreSQL

La seguridad del dominio no depende sólo de que una futura API se comporte
bien. La base de datos rechaza estados fuera de los enums, texto obligatorio
vacío o sin normalizar, fechas invertidas, vínculos entre Teams y duplicados
que crearían ambigüedad operativa.

Track incluye la clave candidata `(track_id, team_id)` y Event la referencia
de forma compuesta. Driver usa la misma estrategia contra TeamMembership, por
lo que un User sólo puede enlazarse en un Team donde tenga Membership.

## 4. Evidencia de verificación local

- 101 pruebas aprobadas;
- 95.21 % de cobertura total, superior al mínimo de 90 %;
- 6 pruebas específicas de persistencia operacional en PostgreSQL;
- migración validada en recorrido upgrade → downgrade → upgrade;
- `alembic check`: ninguna operación nueva detectada;
- Ruff format y lint aprobados;
- mypy estricto aprobado sobre 51 archivos fuente;
- `pip check`: dependencias consistentes;
- imagen de producción reconstruida y stack Docker saludable;
- migración activa `20261108_0003_operations (head)` dentro del contenedor;
- runtime no-root con UID `10001`, sin pytest instalado;
- `/health`, `/ready` y `/openapi.json` respondieron HTTP 200.

## 5. Control de alcance

Este bloque no publica rutas `/drivers`, `/vehicles`, `/tracks` o `/events`.
Tampoco implementa transiciones de estado, asignaciones a Session, telemetría,
mantenimiento o recomendaciones. La persistencia queda lista para construir
la API de Drivers en una superficie pequeña y verificable.

## 6. Punto de aprobación

El propietario aprobó este reporte el 8 de noviembre de 2026. El Bloque 7.3
continuó con los casos de uso y endpoints de Driver, RBAC, aislamiento por
Team, vínculo opcional con User, activación/desactivación y pruebas HTTP.
