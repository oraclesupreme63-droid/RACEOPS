# RaceOps — Roadmap formal de aprendizaje técnico

## 1. Información del documento

- **Versión:** 1.0
- **Fecha:** 2026-10-24
- **Duración sugerida:** 24 semanas
- **Dedicación:** 6–8 horas por semana
- **Modalidad:** teoría breve, práctica en RaceOps y explicación propia
- **Objetivo:** comprender, modificar y defender técnicamente el sistema; no
  limitarse a copiar código.

Este itinerario acompaña el desarrollo. No es necesario terminarlo antes de
seguir programando: se estudia cada tema cuando RaceOps lo necesita.

## 2. Resultado esperado

Al terminar, el estudiante podrá:

1. explicar cómo una petición viaja desde HTTP hasta PostgreSQL y regresa;
2. desarrollar una API con Python, FastAPI, Pydantic y SQLAlchemy;
3. diseñar tablas, relaciones, transacciones y migraciones seguras;
4. utilizar Git, Docker, pruebas automatizadas y análisis estático;
5. implementar autenticación, RBAC y aislamiento por equipo;
6. diagnosticar errores mediante request IDs y logs estructurados;
7. traducir requisitos del negocio a reglas, código y pruebas;
8. entregar y demostrar un flujo vertical completo de RaceOps.

## 3. Método de estudio

Cada módulo utiliza el ciclo **Comprender → Observar → Practicar → Explicar →
Comprobar**:

1. **Comprender:** estudiar el concepto y responder las preguntas guía.
2. **Observar:** localizar el concepto dentro del código de RaceOps.
3. **Practicar:** realizar un ejercicio pequeño sin copiar la solución.
4. **Explicar:** describir con palabras propias qué sucede y por qué.
5. **Comprobar:** ejecutar pruebas o mostrar una evidencia reproducible.

Una técnica se considera aprendida cuando puedes:

- explicarla sin leer el código línea por línea;
- cambiar una parte pequeña sin romper el contrato;
- interpretar un fallo relacionado;
- escribir o ajustar una prueba que demuestre el comportamiento.

## 4. Rutina semanal sugerida

| Actividad | Tiempo |
|---|---:|
| Lectura o video técnico | 1.5 h |
| Recorrido por código existente | 1 h |
| Ejercicio aislado | 1.5 h |
| Trabajo guiado en RaceOps | 2–3 h |
| Explicación y notas propias | 30 min |
| Autoevaluación | 30 min |

No memorices comandos completos. Comprende qué entrada reciben, qué cambian y
cómo verificar el resultado.

## 5. Ruta de aprendizaje

### Etapa 0 — Herramientas y modelo mental

**Semanas:** 1–2  
**Relación con RaceOps:** Fase 5, bloques 1 y 2.

Aprender:

- terminal de PowerShell, rutas, procesos y variables de entorno;
- estructura de un proyecto y diferencia entre código, configuración y datos;
- entorno virtual de Python y administración de dependencias;
- Git: working tree, staging, commit, branch y diff;
- diferencia entre aplicación, servidor, API y base de datos.

Prácticas:

- activar `.venv` y ejecutar Python desde el repositorio;
- usar `git status`, `git diff` y `git log` y explicar sus diferencias;
- localizar `src/`, `tests/`, `docs/`, `migrations/` y la responsabilidad de
  cada directorio;
- dibujar el recorrido navegador → API → base de datos → respuesta.

Evidencia de dominio:

- levantar `/health` y explicar por qué no consulta PostgreSQL;
- describir qué archivos deberían y no deberían guardarse en Git.

### Etapa 1 — Python para backend

**Semanas:** 3–4  
**Relación con RaceOps:** todo el backend.

Aprender:

- tipos básicos, colecciones, condicionales, ciclos y funciones;
- módulos, paquetes e imports;
- clases, dataclasses, excepciones y context managers;
- type hints, `Protocol`, `Literal` y `ContextVar`;
- fundamentos de `async`/`await` sin intentar volver asíncrono todo el sistema.

Prácticas:

- crear funciones puras con tipos y casos de error;
- leer `config.py`, `health.py` y `request_context.py`;
- explicar qué diferencia existe entre devolver un valor y lanzar una excepción;
- provocar un error de mypy y corregir la causa.

Evidencia de dominio:

- implementar una función pequeña con pruebas unitarias y tipos estrictos;
- explicar por qué RaceOps usa un `Protocol` para el health checker.

### Etapa 2 — Web, HTTP y diseño de API

**Semanas:** 5–6  
**Relación con RaceOps:** FastAPI, `/health`, `/ready` y `/api/v1`.

Aprender:

- cliente, servidor, DNS, puerto, URL y ciclo request/response;
- métodos HTTP y status codes;
- headers, query parameters, path parameters y JSON;
- REST, recursos, idempotencia y versionado;
- OpenAPI y separación entre contrato público e implementación.

Prácticas:

- consultar `/docs`, `/openapi.json`, `/health` y `/ready`;
- enviar una petición válida y otra inválida;
- identificar método, ruta, status, headers y body;
- explicar por qué `404`, `409` y `422` representan problemas diferentes.

Evidencia de dominio:

- diseñar en papel un endpoint sin programarlo;
- justificar su método, ruta, respuesta exitosa y errores posibles.

### Etapa 3 — FastAPI y Pydantic

**Semanas:** 7–8  
**Relación con RaceOps:** factoría de aplicación, routers y configuración.

Aprender:

- aplicación ASGI, routers, dependencias y lifespan;
- schemas de entrada y salida;
- validación, serialización y documentación automática;
- Pydantic Settings, `SecretStr` y configuración por entorno;
- middleware y handlers de excepciones.

Prácticas:

- seguir `create_app()` desde su configuración hasta el registro de rutas;
- agregar temporalmente una ruta de práctica con un schema;
- cambiar una restricción de validación y actualizar su prueba;
- comparar una dependencia real con un test double.

Evidencia de dominio:

- explicar por qué una aplicación no debe conectarse a PostgreSQL al importarse;
- demostrar cómo FastAPI transforma entrada inválida en un Problem Details.

### Etapa 4 — SQL y PostgreSQL

**Semanas:** 9–10  
**Relación con RaceOps:** almacenamiento de usuarios, equipos y sesiones.

Aprender:

- tabla, fila, columna, tipo de dato y `NULL`;
- llave primaria, llave foránea, índice y constraint;
- `SELECT`, `INSERT`, `UPDATE`, `DELETE` y `JOIN`;
- normalización básica;
- transacciones, commit, rollback y aislamiento;
- por qué el borrado físico no siempre es apropiado.

Prácticas:

- entrar a PostgreSQL dentro del contenedor;
- crear tablas de práctica fuera del schema de RaceOps;
- consultar relaciones con `JOIN`;
- provocar y explicar una violación de llave única y de llave foránea.

Evidencia de dominio:

- proponer las tablas mínimas para Team, User y Membership;
- explicar qué reglas pertenecen a PostgreSQL y cuáles al servicio de dominio.

### Etapa 5 — SQLAlchemy y transacciones

**Semanas:** 11–12  
**Relación con RaceOps:** `Base`, engine, Session y futuros modelos.

Aprender:

- diferencia entre driver, engine, connection y ORM Session;
- modelos declarativos y relaciones;
- unit of work y límites de transacción;
- carga de relaciones y problema N+1;
- por qué no deben existir commits implícitos dispersos.

Prácticas:

- recorrer `db/base.py` y `db/session.py`;
- mapear un par de entidades de práctica;
- guardar dos cambios en una transacción y forzar rollback;
- observar el SQL generado sin registrar credenciales.

Evidencia de dominio:

- explicar cuándo nace y termina una Session;
- escribir una prueba de integración que demuestre rollback.

### Etapa 6 — Migraciones con Alembic

**Semana:** 13  
**Relación con RaceOps:** revisión `20261024_0001` y futuras tablas.

Aprender:

- diferencia entre modelo ORM y schema real;
- revisión, `upgrade`, `downgrade`, `head` y línea base;
- autogeneración y por qué siempre debe revisarse;
- migraciones compatibles con datos ya existentes.

Prácticas:

- ejecutar `current`, `history`, `upgrade` y `downgrade`;
- leer la migración inicial y explicar por qué está vacía;
- crear una migración de práctica y revisar el SQL offline;
- restaurar la base a `head`.

Evidencia de dominio:

- explicar cómo cambiar una columna sin perder datos;
- demostrar un round-trip de migraciones mediante pytest.

### Etapa 7 — Docker y configuración reproducible

**Semana:** 14  
**Relación con RaceOps:** PostgreSQL en Compose y Bloque 6.

Aprender:

- imagen, contenedor, volumen, red, puerto y health check;
- diferencia entre Dockerfile y Docker Compose;
- configuración mediante variables de entorno;
- persistencia y diferencia entre detener y eliminar;
- separación entre secretos de desarrollo y producción.

Prácticas:

- levantar, inspeccionar y detener `db` sin borrar el volumen;
- explicar el mapeo `55432:5432`;
- construir la futura imagen de la API;
- comprobar comunicación API–PostgreSQL dentro de la red de Compose.

Evidencia de dominio:

- levantar RaceOps desde un entorno limpio usando instrucciones documentadas;
- explicar dónde viven el código, el contenedor y los datos persistentes.

### Etapa 8 — Errores, observabilidad y seguridad básica

**Semanas:** 15–16  
**Relación con RaceOps:** Bloque 5.

Aprender:

- RFC 9457 Problem Details;
- diferencia entre error esperado e inesperado;
- request ID, trace ID, logs estructurados y niveles;
- filtración de secretos y datos personales;
- principios de mínimo privilegio y defensa en profundidad.

Prácticas:

- provocar `404`, `405`, `422` y `500`;
- relacionar `X-Request-ID`, `trace_id` y el evento JSON;
- leer `errors.py`, `middleware.py` y `logging.py`;
- intentar filtrar un valor secreto y comprobar que una prueba lo impide.

Evidencia de dominio:

- diagnosticar un fallo usando sólo el `trace_id`;
- explicar por qué el frontend usa `code` y no analiza el texto de `detail`.

### Etapa 9 — Pruebas y calidad

**Semanas:** 17–18  
**Relación con RaceOps:** pytest, HTTPX, Ruff, mypy y futura CI.

Aprender:

- pirámide de pruebas y diferencia entre unit, integration, API y acceptance;
- patrón Arrange–Act–Assert;
- fixtures, parametrización y test doubles;
- cobertura como indicador, no como objetivo aislado;
- lint, formato, tipos y pipeline de integración continua.

Prácticas:

- ejecutar una prueba individual y toda la suite;
- leer un traceback desde la primera causa útil;
- romper deliberadamente un contrato y observar qué prueba falla;
- escribir una prueba antes de una modificación pequeña.

Evidencia de dominio:

- elegir correctamente el nivel de prueba para una regla dada;
- lograr que la verificación local y CI produzcan el mismo resultado.

### Etapa 10 — Autenticación, autorización y RBAC

**Semanas:** 19–20  
**Relación con RaceOps:** Fase 6.

Aprender:

- hashing de password frente a cifrado;
- autenticación, autorización, access token y expiración;
- JWT y sus límites;
- Team Membership, Role y permisos;
- aislamiento por equipo y respuesta `404` para recursos ocultos.

Prácticas:

- modelar User, Team, Membership y Role;
- probar login correcto e incorrecto sin revelar si una cuenta existe;
- construir una matriz rol–acción;
- intentar acceso entre equipos y demostrar que se bloquea.

Evidencia de dominio:

- explicar todo el flujo login → token → actor → permiso → recurso;
- demostrar mediante pruebas que Driver no ve configuración confidencial.

### Etapa 11 — Dominio y reglas de RaceOps

**Semanas:** 21–22  
**Relación con RaceOps:** Fases 7 y 8.

Aprender:

- entidad, value object, aggregate e invariante;
- diferencia entre validación de forma y regla de negocio;
- service layer y límites de módulo;
- estados y transiciones explícitas;
- diseño guiado por evidencia del usuario.

Prácticas:

- modelar Event, Session, Driver y Vehicle;
- definir quién puede iniciar, completar o bloquear una Session;
- implementar el límite de 1–3 prioridades principales;
- mantener Driver Feedback separado de hallazgos confidenciales.

Evidencia de dominio:

- señalar dónde vive cada regla y justificar la decisión;
- convertir un hallazgo de entrevista en requisito, prueba y comportamiento.

### Etapa 12 — Flujo vertical, entrega y validación

**Semanas:** 23–24  
**Relación con RaceOps:** Fases 8, 9 y posteriores.

Aprender:

- integración de capas sin crear dependencias circulares;
- flujo vertical frente a acumulación de módulos inconexos;
- CI, despliegue, configuración y observación básica;
- prueba de usabilidad y medición con usuarios reales;
- diferencia entre software funcional y producto validado.

Prácticas:

- completar Event → Session → Feedback → Analysis → Action → Result;
- cargar datos realistas con permiso;
- ejecutar una demostración reproducible;
- observar a un usuario sin explicarle cada pantalla;
- registrar fricciones, tiempo, errores y decisiones de producto.

Evidencia de dominio:

- presentar el flujo completo y responder preguntas técnicas;
- demostrar con evidencia qué problema resuelve y qué sigue siendo hipótesis.

## 6. Mapa entre conocimientos y código actual

| Conocimiento | Archivo principal |
|---|---|
| Factoría FastAPI y lifespan | `src/raceops/main.py` |
| Configuración tipada | `src/raceops/core/config.py` |
| Contexto por petición | `src/raceops/core/request_context.py` |
| Logs JSON seguros | `src/raceops/core/logging.py` |
| Middleware HTTP | `src/raceops/api/middleware.py` |
| Problem Details | `src/raceops/api/errors.py` |
| Health y readiness | `src/raceops/api/health.py` |
| Engine y Sessions | `src/raceops/db/session.py` |
| Base declarativa | `src/raceops/db/base.py` |
| Migraciones | `migrations/` |
| PostgreSQL local | `docker-compose.yml` |
| Pruebas | `tests/` |

## 7. Autoevaluación por módulo

Usa esta escala antes de considerar terminado un tema:

| Nivel | Evidencia |
|---|---|
| 0 — Desconocido | No puedo definir el concepto. |
| 1 — Reconozco | Puedo identificarlo cuando lo veo. |
| 2 — Explico | Puedo describir su propósito y recorrido. |
| 3 — Aplico | Puedo modificarlo con pruebas y diagnosticar fallos. |
| 4 — Defiendo | Puedo justificar la decisión, sus riesgos y alternativas. |

El objetivo mínimo antes de avanzar no es nivel 4 en todo. Se requiere nivel 3
en el tema central del bloque y al menos nivel 2 en sus dependencias.

## 8. Preguntas para revisar cada bloque de código

Antes de aprobar un bloque, responde:

1. ¿Qué problema resuelve?
2. ¿Qué entrada recibe y qué salida produce?
3. ¿Qué archivo es responsable y por qué?
4. ¿Qué puede fallar?
5. ¿Qué información no debe exponerse?
6. ¿Qué prueba demuestra el comportamiento?
7. ¿Cómo lo ejecuto manualmente?
8. ¿Cómo sabría que debo rediseñarlo?

Si una respuesta no está clara, el bloque puede funcionar técnicamente pero
todavía no se considera comprendido.

## 9. Referencias oficiales

- [Tutorial oficial de Python](https://docs.python.org/3/tutorial/)
- [Libro oficial Pro Git](https://git-scm.com/book/en/v2)
- [Tutorial oficial de FastAPI](https://fastapi.tiangolo.com/tutorial/)
- [Documentación de Pydantic](https://docs.pydantic.dev/latest/)
- [Tutorial de PostgreSQL](https://www.postgresql.org/docs/current/tutorial.html)
- [Tutorial de SQLAlchemy](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Tutorial de Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Introducción oficial a Docker](https://docs.docker.com/get-started/)
- [Introducción oficial a pytest](https://docs.pytest.org/en/stable/getting-started.html)
- [OWASP API Security Top 10](https://owasp.org/API-Security/)

## 10. Próxima acción recomendada

Mientras continúa el Bloque 6, comenzar con las etapas 0 y 1. La primera
revisión guiada debe consistir en explicar `create_app()` y ejecutar por cuenta
propia `/health`, `/ready` y una prueba unitaria. Después se avanza a HTTP,
FastAPI y PostgreSQL siguiendo el orden de este documento.
