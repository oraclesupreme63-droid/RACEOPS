# RaceOps — Estructura del proyecto

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G4
- **Layout:** Paquete `src/`, monolito modular

## 2. Estructura propuesta

```text
RACEOPS/
├── pyproject.toml
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── migrations/
│   ├── env.py
│   └── versions/
├── src/
│   └── raceops/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── router.py
│       │   └── dependencies.py
│       ├── core/
│       │   ├── config.py
│       │   ├── errors.py
│       │   ├── logging.py
│       │   ├── security.py
│       │   └── clock.py
│       ├── db/
│       │   ├── base.py
│       │   ├── session.py
│       │   └── conventions.py
│       ├── shared/
│       │   ├── enums.py
│       │   ├── pagination.py
│       │   └── types.py
│       └── modules/
│           ├── iam/
│           ├── operations/
│           ├── sessions/
│           ├── learning/
│           ├── reporting/
│           ├── audit/
│           ├── telemetry_refs/
│           └── maintenance/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── api/
│   ├── acceptance/
│   ├── factories/
│   └── conftest.py
├── scripts/
└── docs/
```

Los módulos P1 no necesitan implementarse durante el primer corte, aunque
sus carpetas tampoco se crearán vacías por anticipado.

## 3. Estructura interna de un módulo

```text
modules/sessions/
├── __init__.py
├── api.py          # APIRouter y traducción HTTP
├── schemas.py      # modelos Pydantic de entrada/salida
├── models.py       # modelos SQLAlchemy propietarios
├── service.py      # casos de uso y transacciones coordinadas
├── policies.py     # reglas y autorización específica
├── queries.py      # consultas explícitas y proyecciones
└── domain.py       # value objects o lógica pura cuando aporta valor
```

No todos los módulos están obligados a tener todos los archivos. Se crean
cuando existe contenido real.

## 4. Responsabilidades por capa

### `api.py`

- declarar rutas y códigos HTTP;
- inyectar actor y DB Session;
- validar schemas;
- llamar un caso de uso;
- devolver DTO autorizados.

No contiene reglas de negocio ni queries SQL complejas.

### `schemas.py`

- contratos HTTP;
- validación sintáctica;
- separación entre create, update y read;
- exclusión explícita de campos confidenciales.

### `service.py`

- coordinar casos de uso;
- abrir el alcance lógico de transacción recibido;
- cargar aggregates;
- aplicar policies e invariantes;
- hacer flush/commit mediante el límite acordado.

### `models.py`

- mapeo relacional;
- constraints e índices;
- relaciones de persistencia;
- métodos simples ligados a estado cuando resulte claro.

### `domain.py`

- value objects;
- cálculos puros;
- máquinas de estado;
- reglas sin dependencia de HTTP.

### `queries.py`

- lectura filtrada;
- paginación;
- locking cuando sea necesario;
- proyecciones de reporting.

## 5. Configuración

- Pydantic Settings cargará variables de entorno.
- `.env` será sólo conveniencia local y nunca se versionará con secretos.
- `.env.example` contendrá nombres y valores no sensibles de ejemplo.
- La configuración se valida al iniciar; fallará rápidamente si falta un
  valor obligatorio.

## 6. Convenciones Python

- Python moderno compatible con dependencias seleccionadas en Fase 5.
- Type hints en interfaces relevantes.
- Nombres de archivos y símbolos en inglés; documentación de producto en
  español puede mantenerse.
- Enums y términos alineados con el lenguaje ubicuo.
- Imports absolutos desde `raceops`.
- No incluir lógica en `__init__.py`.
- Ningún singleton de SQLAlchemy Session.

## 7. Frontend

La fundación será backend-first. El cliente web será delgado y consumirá la
API documentada. La tecnología exacta se elegirá antes del primer prototipo
visual según tiempo y pruebas de uso; esa decisión no bloqueará EP-00 a
EP-03 ni modificará las reglas del servidor.

## 8. Decisión de acceso a datos

- SQLAlchemy 2.x operará en modo síncrono con Psycopg 3.
- Los endpoints que usen la base serán `def`, no `async def` con llamadas
  bloqueantes.
- Una Session se inyectará por petición/caso de uso y nunca será global.
- El servicio coordinará una transacción corta; los repositories no harán
  commits independientes.
- La decisión queda formalizada en ADR-002.


