# RaceOps — Configuración y despliegue inicial

## 1. Información del documento

- **Versión:** 1.1
- **Estado:** Implementado hasta el alcance de Fase 6
- **Alcance:** desarrollo y primer entorno desplegable

## 2. Configuración

Pydantic Settings leerá configuración desde variables de entorno. Variables
iniciales:

| Variable | Propósito | Secreto |
|---|---|---|
| `RACEOPS_ENV` | local, test o production | No |
| `RACEOPS_DATABASE_URL` | conexión PostgreSQL | Sí |
| `RACEOPS_JWT_SECRET` | firma de access tokens | Sí |
| `RACEOPS_ACCESS_TOKEN_TTL_MINUTES` | expiración configurable | No |
| `RACEOPS_CORS_ORIGINS` | allowlist de orígenes | No |
| `RACEOPS_LOG_LEVEL` | nivel mínimo | No |

Los nombres pueden ajustarse durante la fundación, pero los principios no:

- settings tipados y centralizados;
- validación al arranque;
- sin secretos productivos por defecto;
- `.env.example` sin valores privados;
- test settings independientes.

En `production`, RaceOps rechaza las URLs de base de desarrollo conocidas,
los marcadores JWT documentales y cualquier secreto JWT menor de 32
caracteres. `RACEOPS_CORS_ORIGINS` se aplica como allowlist exacta; no activa
cookies y sólo admite los métodos y encabezados necesarios para la API.

## 3. Desarrollo local

Docker Compose tendrá sólo los servicios necesarios:

```text
api  → FastAPI/Uvicorn
db   → PostgreSQL
```

Alembic se ejecuta mediante un comando explícito antes de usar la API. El
modo reload es sólo local. Se documentarán comandos equivalentes para
iniciar, migrar, probar y detener.

## 4. Imagen

- Imagen basada en una versión fija y soportada de Python.
- Dependencias instaladas de manera reproducible.
- Proceso ejecutado como usuario no root.
- Código y dependencias necesarios, sin `.env`, tests ni credenciales.
- `CMD` explícito y señal de apagado manejada.
- Imagen inspeccionable por versión/commit cuando exista repositorio Git.

No se agregan Nginx, Redis, Celery, Kubernetes ni cloud services hasta que
un requisito los justifique.

## 5. Health y readiness

- `GET /health` confirma que el proceso responde y devuelve estado y versión
  sin información sensible.
- `GET /ready` comprueba que las dependencias necesarias, inicialmente
  PostgreSQL, permiten atender tráfico.
- Health no requiere autenticación y nunca muestra connection strings,
  nombres internos, stack traces o configuración.

## 6. Ambientes

| Ambiente | Datos | Debug | Objetivo |
|---|---|---|---|
| local | sintéticos | permitido | desarrollo |
| test | efímeros/sintéticos | capturado | CI y verificación |
| production/demo | autorizados | desactivado | demostración o uso controlado |

No se reutiliza una base ni secretos entre ambientes. La demo académica no
se describe como producción hasta contar con backups, TLS, rate limiting,
monitoring y procedimiento de recuperación probados.

## 7. Arranque y migración

Secuencia desplegable:

1. validar secretos y configuración;
2. comprobar respaldo cuando el cambio lo requiera;
3. aplicar migraciones como paso controlado;
4. iniciar nueva aplicación;
5. comprobar `/health` y `/ready`;
6. ejecutar smoke test del login y una lectura autorizada;
7. revertir aplicación si falla, sin improvisar downgrade destructivo.

## 8. Observabilidad mínima

- logs JSON a stdout;
- request IDs;
- estado de health/readiness;
- versión desplegada;
- señal visible de errores 5xx;
- métricas más amplias sólo cuando exista un entorno que las consuma.

## 9. Criterio para Fase 5

La fundación se considera ejecutable cuando una persona nueva puede, usando
instrucciones del repositorio:

- levantar PostgreSQL y API;
- aplicar migraciones;
- consultar `/health` y `/ready`;
- ejecutar toda la suite;
- apagar el entorno sin perder cambios de schema no documentados.

