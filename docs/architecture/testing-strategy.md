# RaceOps — Estrategia de pruebas

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G4
- **Herramientas:** pytest, HTTPX/TestClient y PostgreSQL

## 2. Principio

La calidad se medirá por reglas y riesgos cubiertos, no por un porcentaje de
coverage aislado. Cada requerimiento P0 debe terminar vinculado a al menos
una prueba ejecutable antes de considerar completo el flujo vertical.

## 3. Capas de prueba

| Capa | Alcance | Dependencias |
|---|---|---|
| Unit | estados, políticas, cálculos, visibilidad | ninguna externa |
| Integration | mappings, queries, constraints, transacciones, migraciones | PostgreSQL real |
| API | contrato HTTP, auth, errores, serialización | aplicación + PostgreSQL |
| Acceptance | flujo completo y criterios P0 | API pública |

Los unit tests serán numerosos y rápidos. Las pruebas de integración no
duplicarán toda regla pura, pero cubrirán aquello que sólo la base puede
garantizar.

## 4. Escenarios obligatorios

### Dominio

- cada transición válida e inválida de Session, Results y Action;
- máximo de tres Main Priorities por destinatario y sesión;
- una Action completada no crea automáticamente un ActionOutcome;
- `NOT_EVALUATED` se deriva cuando no existe resultado;
- referencias `NEXT_SESSION` pueden resolverse posteriormente;
- una Session bloqueada rechaza cambios protegidos.

### Seguridad y visibilidad

- cada permiso permitido y denegado relevante de la matriz;
- un Team no puede leer, modificar ni inferir recursos de otro;
- Driver no recibe detalle de ingeniería confidencial;
- conteo, filtros, reportes y errores no filtran registros ocultos;
- campos prohibidos son rechazados, no ignorados.

### Persistencia y concurrencia

- constraints, rollback y atomicidad;
- migración desde una base vacía hasta `head`;
- creación concurrente de prioridades no supera el máximo;
- dos transiciones competidoras no sobrescriben estado silenciosamente;
- una audit entry crítica se guarda junto con el cambio.

### API

- status, headers y schemas de éxito;
- contrato RFC 9457 para errores;
- timestamps UTC y duraciones en microsegundos;
- paginación autorizada y orden estable;
- OpenAPI no expone schemas internos o rutas duplicadas.

## 5. Datos y aislamiento

- Factories crean Teams y roles explícitos.
- Los ejemplos son sintéticos y deterministas.
- Cada prueba inicia con estado conocido y no depende del orden de ejecución.
- Integration tests utilizan una base exclusiva o schemas aislados y limpian
  mediante rollback/truncate controlado.
- No se usa la base de desarrollo ni información real para ejecutar tests.

## 6. Estructura

```text
tests/
├── unit/
├── integration/
├── api/
├── acceptance/
├── factories/
└── conftest.py
```

Los nombres describen conducta: `test_driver_cannot_read_confidential_detail`
es preferible a `test_permissions_3`.

## 7. Pipeline de integración continua

Orden inicial:

1. instalar dependencias desde lockfile;
2. lint y format check;
3. type check;
4. iniciar PostgreSQL de prueba;
5. aplicar migraciones;
6. ejecutar unit, integration, API y acceptance tests disponibles;
7. comprobar generación de OpenAPI;
8. construir imagen de aplicación.

No se permite merge si falla una prueba P0, migración o control de seguridad
obligatorio.

## 8. Definition of Done técnica

Un cambio no está terminado hasta que:

- su conducta feliz y sus rechazos importantes están probados;
- respeta ownership y visibilidad;
- una migración acompaña todo cambio persistente;
- el contrato y la trazabilidad se actualizan;
- no introduce warnings inesperados ni secretos en logs.

## 9. Evolución

Load testing, pruebas de restauración y pruebas de interfaz ampliarán esta
estrategia cuando exista el sistema correspondiente. No se inventarán metas
de rendimiento antes de contar con un escenario y dataset representativos.

