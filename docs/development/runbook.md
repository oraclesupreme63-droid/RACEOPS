# RaceOps — Runbook de desarrollo local

## 1. Información del documento

- **Versión:** 1.0
- **Fecha:** 2026-11-04
- **Alcance:** `v0.1 — Foundation`
- **Plataforma principal:** Windows 11 con PowerShell y Docker Desktop

Este documento explica cómo iniciar, verificar, observar y detener RaceOps sin
eliminar accidentalmente su base de datos local.

## 2. Prerrequisitos

- Git;
- Docker Desktop con Docker Compose;
- Python 3.12 o posterior compatible, sólo para desarrollo fuera de Docker;
- puertos locales `8000` y `55432` disponibles.

Todos los comandos se ejecutan desde la raíz del repositorio. En la máquina
actual se puede llegar a ella con:

```powershell
cd "ruta\donde\se\clono\RACEOPS"
```

Después de clonar o mover el proyecto, sustituir la ruta de ejemplo por su
ubicación real.

## 3. Arranque recomendado

Abrir Docker Desktop y esperar a que el motor esté listo. Después ejecutar:

```powershell
docker compose up -d --build --wait
docker compose ps -a
```

Estado esperado:

| Servicio | Estado esperado | Significado |
|---|---|---|
| `db` | `healthy` | PostgreSQL acepta conexiones |
| `migrate` | `Exited (0)` | Alembic terminó correctamente |
| `api` | `healthy` | FastAPI responde a `/health` |

`migrate` no es un servidor permanente. Su salida con código cero es el
resultado correcto de un trabajo de una sola ejecución.

## 4. Verificación funcional

Abrir en el navegador:

- `http://127.0.0.1:8000/health` — vida del proceso;
- `http://127.0.0.1:8000/ready` — disponibilidad de PostgreSQL;
- `http://127.0.0.1:8000/docs` — interfaz OpenAPI;
- `http://127.0.0.1:8000/openapi.json` — contrato generado.

Resultado esperado de readiness:

```json
{
  "status": "ready",
  "service": "raceops-api",
  "database": "up",
  "version": "0.3.0"
}
```

## 5. Logs y diagnóstico básico

Ver logs de la API:

```powershell
docker compose logs -f api
```

Ver migraciones:

```powershell
docker compose logs migrate
docker compose exec -T api python -m alembic current
```

Ver todos los servicios sin seguir la salida:

```powershell
docker compose ps -a
docker compose logs --tail 100
```

Presionar `Ctrl + C` deja de seguir los logs, pero no detiene los contenedores.

## 6. Detener y reanudar

Detener sin borrar datos:

```powershell
docker compose stop
```

Reanudar respetando health checks y migraciones:

```powershell
docker compose up -d --wait
```

No utilizar `docker compose down --volumes` salvo que se haya decidido borrar
intencionalmente toda la base local. El volumen es la persistencia de
PostgreSQL y no debe eliminarse como método normal de solución de problemas.

## 7. Desarrollo directo con Python

Para utilizar recarga automática y herramientas de desarrollo:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
docker compose up -d --wait db
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn raceops.main:app --reload
```

En este modo, la API se ejecuta en Windows y se conecta a PostgreSQL mediante
`localhost:55432`.

## 8. Verificación de calidad

Con PostgreSQL disponible:

```powershell
.\.venv\Scripts\python.exe -m ruff format --check src tests migrations
.\.venv\Scripts\python.exe -m ruff check src tests migrations
.\.venv\Scripts\python.exe -m mypy src tests
$env:RACEOPS_RUN_DB_TESTS = "1"
.\.venv\Scripts\python.exe -m pytest --cov=raceops --cov-report=term-missing --cov-fail-under=90
.\.venv\Scripts\python.exe -m alembic check
Remove-Item Env:RACEOPS_RUN_DB_TESTS
```

El resultado de referencia de Foundation es 22 pruebas aprobadas y cobertura
superior al 90 %.

## 9. Problemas frecuentes

### Docker no responde

Síntoma: error relacionado con `dockerDesktopLinuxEngine` o imposibilidad de
conectar con el daemon.

Acción:

1. abrir Docker Desktop;
2. esperar a que el motor indique que está listo;
3. ejecutar `docker compose ps -a`;
4. repetir `docker compose up -d --wait`.

### Puerto ocupado

Síntoma: Docker no puede publicar `8000` o `55432`.

Acción: identificar primero el proceso que utiliza el puerto. No detener ni
eliminar otro PostgreSQL sin confirmar que pertenece a RaceOps. Los puertos se
pueden cambiar en `.env` mediante `RACEOPS_API_PORT` y `POSTGRES_PORT`.

### `migrate` aparece detenido

`Exited (0)` es éxito. Cualquier código distinto de cero requiere revisar:

```powershell
docker compose logs migrate
```

### `/health` funciona pero `/ready` devuelve 503

La API está viva, pero PostgreSQL no está disponible. Revisar:

```powershell
docker compose ps -a
docker compose logs --tail 100 db
```

### Error de autenticación de PostgreSQL

Confirmar que `.env`, `RACEOPS_DATABASE_URL` y las variables `POSTGRES_*`
correspondan al mismo entorno. No imprimir contraseñas en tickets, capturas o
logs. Un volumen creado con credenciales anteriores conserva su configuración;
no debe borrarse sin evaluar primero sus datos.

### La API está `unhealthy`

Revisar en orden:

```powershell
docker compose logs migrate
docker compose logs --tail 100 api
docker compose exec -T api python -m alembic current
```

No intentar ocultar el fallo aumentando reintentos antes de conocer la causa.

## 10. Límites actuales

Foundation demuestra infraestructura y calidad técnica. Todavía no incluye
usuarios, autenticación, equipos, pilotos, vehículos, eventos, sesiones ni el
Session Learning Loop. Esos módulos comienzan en las fases 6–8.
