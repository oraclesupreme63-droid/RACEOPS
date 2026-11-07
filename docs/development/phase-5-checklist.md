# RaceOps — Fase 5: checklist de fundación técnica

## Estado

- **Fase:** 5 — Fundación técnica
- **Gate de salida:** G5 — Foundation Running
- **Estado actual:** Fase 5 completada; G5 aprobado

## Bloques

| Bloque | Alcance | Estado |
|---|---|---|
| 1 | Git, `pyproject.toml`, archivos base y paquete `src/` | Aprobado |
| 2 | Aplicación FastAPI y `/health` | Aprobado |
| 3 | Configuración, PostgreSQL y `/ready` | Aprobado |
| 4 | PostgreSQL local, base declarativa, convenciones y Alembic | Aprobado |
| 5 | Errores RFC 9457, request ID y logging | Aprobado |
| 6 | Dockerfile y Docker Compose | Aprobado |
| 7 | Tests, calidad y CI | Aprobado |
| 8 | Documentación de ejecución y cierre G5 | Aprobado |

## Bloque 1 — Criterios de revisión

- el repositorio Git usa la rama `main`;
- Python requerido coincide con el entorno disponible;
- dependencias P0 de fundación están declaradas;
- secretos y entornos locales están ignorados;
- `.env.example` contiene únicamente valores de ejemplo;
- el layout `src/raceops` existe;
- no se crearon módulos de negocio antes de necesitarlos;
- `pyproject.toml` puede analizarse correctamente.

## Bloque 2 — Resultado para revisión

- `create_app()` construye la aplicación sin efectos externos;
- `app` expone la aplicación ASGI predeterminada para Uvicorn;
- `/health` comprueba únicamente vida del proceso;
- la respuesta contiene `status`, `service` y `version`;
- `/health` aparece en OpenAPI bajo el tag `system`;
- el router `/api/v1` queda reservado para negocio sin rutas ficticias;
- HTTPX prueba el contrato directamente contra la aplicación ASGI;
- Ruff, mypy y las dos pruebas HTTP pasan.

## Bloque 3 — Resultado para revisión

- Pydantic Settings carga variables `RACEOPS_*` y `.env` local;
- database URL y JWT secret utilizan `SecretStr`;
- valores conocidos de desarrollo se rechazan en producción;
- el engine usa Psycopg 3, `pool_pre_ping` y timeout corto;
- la session factory no crea Sessions globales ni hace commits implícitos;
- el checker ejecuta `SELECT 1` en una conexión corta;
- `/ready` devuelve `200`/`up` o `503`/`down` sin revelar errores internos;
- el engine se libera mediante el lifespan de FastAPI;
- seis pruebas sin red, Ruff y mypy pasaron durante la revisión del bloque;
- las cuatro pruebas HTTP que habían quedado pendientes se ejecutaron y
  aprobaron como parte de la validación completa del Bloque 4.

## Bloque 4 — Resultado para revisión

- Docker Compose ejecuta PostgreSQL 18.6 con health check y volumen persistente;
- el puerto de desarrollo `55432` evita interferir con el PostgreSQL local que
  ya ocupa `5432` en la máquina;
- la configuración de la aplicación, `.env.example` y Docker comparten el
  mismo contrato de conexión local;
- `Base` centraliza las convenciones deterministas para nombres de índices,
  llaves primarias, foráneas, únicas y restricciones check;
- Alembic obtiene la URL desde `Settings` y nunca guarda credenciales en
  `alembic.ini`;
- la revisión `20261024_0001` establece una línea base vacía e intencional antes
  de introducir entidades del dominio;
- `alembic upgrade head` se ejecutó correctamente contra PostgreSQL real;
- la revisión activa quedó en `20261024_0001 (head)`;
- la comprobación real de readiness ejecutó `SELECT 1` y devolvió `up`;
- la prueba de integración `upgrade → downgrade → upgrade` pasó y dejó la base
  nuevamente en `head`;
- la suite completa terminó con `12 passed` y 91 % de cobertura;
- Ruff format, Ruff check y mypy terminaron sin errores;
- el servicio PostgreSQL queda encendido para continuar el desarrollo y sus
  datos sobreviven a reinicios del contenedor.

## Bloque 5 — Resultado para revisión

- cada petición HTTP recibe un UUID de correlación y lo devuelve mediante
  `X-Request-ID`;
- un UUID entrante válido se conserva y un valor ausente o no confiable se
  reemplaza;
- el mismo identificador aparece como `trace_id` en respuestas de error y en
  los logs asociados;
- los errores `404`, `405`, `422` y los fallos inesperados usan RFC 9457 con
  `application/problem+json`, `code` estable e información pública segura;
- la validación por campo informa ubicación, código y mensaje, pero nunca
  replica el valor rechazado;
- los fallos inesperados devuelven un `500` genérico y el servidor conserva
  tipo de excepción y ubicaciones del stack sin registrar su mensaje;
- los logs de aplicación son JSON a `stdout` e incluyen timestamp UTC, nivel,
  servicio, entorno, evento, request ID, método, plantilla de ruta, status y
  duración;
- el logger usa una lista explícita de campos: no serializa bodies, query
  strings, tokens, cookies, secretos ni extras arbitrarios;
- las rutas se registran como plantilla y no con identificadores concretos;
- arranque y cierre de la aplicación generan eventos estructurados;
- Alembic y su prueba de integración ahora comparten el timeout corto de
  conexión, por lo que una base detenida falla rápido;
- la suite completa terminó con `22 passed` y 91 % de cobertura;
- Ruff format, Ruff check y mypy terminaron sin errores.

## Bloque 6 — Resultado para revisión

- un Dockerfile multi-stage construye el wheel de RaceOps separado de la
  imagen final de ejecución;
- la imagen final instala únicamente dependencias productivas y se verificó
  que pytest no está presente;
- la API se ejecuta como usuario no privilegiado `raceops` con UID/GID 10001;
- `.dockerignore` utiliza una lista permitida y excluye `.env`, Git, tests,
  documentación, entornos virtuales y archivos ajenos a la imagen;
- Compose define `db`, `migrate` y `api` con responsabilidades separadas;
- `migrate` espera a que PostgreSQL esté saludable, ejecuta Alembic y termina
  con código 0;
- `api` arranca solamente después de una migración exitosa;
- los servicios se comunican por el nombre interno `db` y PostgreSQL no usa el
  puerto del host dentro de la red de Compose;
- API y PostgreSQL se publican únicamente en `127.0.0.1` durante desarrollo;
- el health check de la API usa la biblioteca estándar de Python y no agrega
  herramientas innecesarias a la imagen;
- los accesos repetitivos del health check se registran en DEBUG para evitar
  ruido en los logs INFO;
- `docker compose config --quiet` validó la configuración;
- `docker compose up -d --wait` dejó `db` y `api` saludables;
- `/health`, `/ready` y `/openapi.json` respondieron desde la API contenerizada;
- Alembic reportó `20261024_0001 (head)` desde el contenedor;
- la suite completa mantuvo `22 passed` y 91 % de cobertura;
- Ruff format, Ruff check y mypy terminaron sin errores.

## Bloque 7 — Resultado para revisión

- `.github/workflows/ci.yml` responde a push sobre `main`, pull requests y
  ejecución manual;
- el token del workflow tiene únicamente permiso `contents: read`;
- la concurrencia cancela una ejecución anterior de la misma referencia para
  no gastar minutos validando código obsoleto;
- el job `quality` usa Python 3.12 y caché de pip basada en `pyproject.toml`;
- PostgreSQL 18.6 se crea como service container aislado para las pruebas;
- CI ejecuta Ruff format, Ruff check, mypy y las pruebas unitarias, API e
  integración;
- la cobertura mínima exigida es 90 % y el proyecto mantiene 91 %;
- `alembic check` falla si los modelos cambian sin una migración y actualmente
  reporta `No new upgrade operations detected`;
- el job `container` sólo comienza después de aprobar el job de Python;
- el smoke test valida Compose, construye la imagen, levanta el stack, consulta
  health/readiness/OpenAPI y comprueba usuario no root y ausencia de pytest;
- ante un fallo se imprimen estado y logs de los contenedores;
- la limpieza destructiva del volumen está limitada al runner efímero de CI y
  se ejecuta incluso cuando falla una comprobación;
- el YAML se analizó correctamente y ambos jobs fueron reconocidos;
- la ejecución real [CI 42399043070](https://github.com/oraclesupreme63-droid/RACEOPS/actions/runs/42399043070)
  aprobó los jobs de calidad y contenedores en el runner Linux.

## Bloque 8 — Resultado para revisión

- README contiene arranque Docker, desarrollo directo, endpoints, logs,
  pruebas y comportamiento de CI;
- `runbook.md` centraliza operación, verificación, detención segura y solución
  de problemas frecuentes;
- el runbook distingue explícitamente detener contenedores de eliminar el
  volumen persistente;
- `gate-g5-assessment.md` relaciona cada criterio con evidencia verificable;
- el roadmap refleja que la implementación local de Fase 5 está completa;
- G5 se evaluó primero de forma condicional y después se cerró con evidencia;
- la condición pendiente se resolvió mediante una ejecución real de CI;
- el repositorio privado quedó publicado y conectado mediante `origin`.

## Criterio de Gate G5

API, PostgreSQL, migraciones, Docker, tests y health checks funcionan mediante
instrucciones reproducibles. El workflow fue validado localmente y mediante
una ejecución verde real en GitHub. G5 queda aprobado.

