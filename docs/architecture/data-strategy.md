# RaceOps — Estrategia de datos

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G4
- **Motor:** PostgreSQL
- **Acceso:** SQLAlchemy 2.x síncrono
- **Migraciones:** Alembic

## 2. Decisión principal

RaceOps utilizará una sola base PostgreSQL y un monolito modular. La carga
inicial es transaccional y no incluye telemetría en vivo; por ello se elige
SQLAlchemy síncrono con Psycopg 3. No se mezclará acceso síncrono y asíncrono.

Los endpoints que consulten la base serán funciones síncronas (`def`). Una
sesión SQLAlchemy se abrirá por petición o caso de uso, se mantendrá durante
una transacción corta y nunca se compartirá entre peticiones o tareas
concurrentes.

## 3. Transacciones

- El límite transaccional pertenece al caso de uso, no al repository.
- El servicio hace `flush` cuando necesita detectar constraints antes del
  final y confirma una sola vez.
- Cualquier excepción revierte toda la operación.
- Los módulos internos pueden participar en la misma transacción.
- No se mantiene una transacción abierta durante llamadas externas.
- La lectura, autorización y escritura que protegen una invariante ocurren
  dentro del mismo límite transaccional.

Los comandos con riesgo de carrera, como crear la tercera prioridad o
cambiar un estado, bloquearán el aggregate necesario o utilizarán una
constraint equivalente. Un conflicto válido se traducirá a HTTP `409`.

## 4. Tipos y representación

| Concepto | Representación propuesta |
|---|---|
| Identificador público | UUID generado por la aplicación |
| Instante | `timestamp with time zone`, normalizado a UTC |
| Fecha local | `date` |
| Duración | `bigint` en microsegundos |
| Medición | `numeric` más unidad explícita |
| Estado/categoría | enum estable o constraint documentada |
| Texto breve | longitud máxima declarada |
| Nota | texto con límite validado por aplicación |

Un valor desconocido será `NULL` cuando el dominio lo permita. Nunca se
usará cero para representar ausencia de información.

## 5. Integridad

- Foreign keys protegen relaciones obligatorias.
- Unique constraints protegen identidades naturales cuando sean estables.
- Check constraints protegen rangos y combinaciones simples.
- `team_id` acompaña a los aggregates que pertenecen al equipo.
- Cuando sea práctico, claves y constraints compuestas impedirán relacionar
  registros de equipos diferentes.
- Reglas complejas permanecen en políticas de dominio y se prueban.

La aplicación filtra por Team antes de devolver o modificar datos. La base
de datos es una defensa adicional, no el único control de autorización.

## 6. Ciclo de vida

No habrá soft delete universal. Se utilizarán estados de negocio como
`ACTIVE`, `INACTIVE`, `CANCELLED`, `LOCKED` o `UNAVAILABLE` cuando tengan
significado. Los datos que forman la cadena de aprendizaje no se borrarán
mediante endpoints normales.

Las correcciones excepcionales de información bloqueada requerirán permiso,
motivo y audit entry.

## 7. Migraciones

- Alembic será la única vía normal de cambio de schema.
- `autogenerate` produce un borrador que siempre se revisa manualmente.
- Cada migración debe poder aplicarse sobre una base vacía y sobre la
  revisión anterior.
- No se modifican migraciones que ya hayan sido compartidas o aplicadas.
- Los downgrades se implementarán cuando sean seguros; cambios destructivos
  requieren respaldo y procedimiento documentado.
- El arranque de producción no ejecutará cambios destructivos implícitos.

## 8. Índices y consultas

Se crearán índices para foreign keys y patrones P0 conocidos, por ejemplo:

- recursos por `team_id`;
- Sessions por Event, Track, Driver, Vehicle y fecha;
- Laps por Session y número de vuelta;
- Actions por sesión de origen, sesión objetivo y estado;
- historial por Track y fecha.

Los índices adicionales se basarán en consultas observadas con `EXPLAIN`, no
en optimización preventiva.

## 9. Datos de prueba y respaldo

- Unit tests no requieren base de datos.
- Integration y acceptance tests usan PostgreSQL, no SQLite, para conservar
  semántica de constraints, locking y tipos.
- Factories generan datos sintéticos sin copiar información confidencial.
- Seeds de demostración se separan de migraciones y de datos reales.
- Antes de utilizar información real se definirá respaldo, restauración y
  retención; hasta entonces el entorno es de desarrollo, no un sistema de
  registro confiable.

## 10. Referencias

- [SQLAlchemy — Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Alembic — Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

