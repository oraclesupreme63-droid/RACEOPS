# RaceOps — Informe de estado del proyecto

## 1. Información del informe

- **Fecha de corte:** 7 de noviembre de 2026
- **Versión técnica actual:** `v0.1 — Foundation`
- **Última fase completada:** Fase 5 — Fundación técnica
- **Fase en progreso:** Fase 6 — Identidad y autorización
- **Bloque actual:** 6.1 — contrato preparado para aprobación
- **Repositorio:** `oraclesupreme63-droid/RACEOPS`
- **Estado de publicación:** versión pública sin registros individuales;
  investigación completa preservada en repositorio privado

## 2. Resumen ejecutivo

RaceOps ya cuenta con una fundación backend ejecutable, reproducible y
verificada tanto en la máquina de desarrollo como en GitHub Actions. API,
PostgreSQL, migraciones, manejo de errores, logging, pruebas y contenedores
funcionan de forma integrada.

La Fase 6 ya inició. El Bloque 6.1 definió el contrato de identidad, el
bootstrap administrativo, el contexto de Team por token y los contratos HTTP;
la persistencia todavía no comenzó porque requiere aprobación del propietario.

Gate G5 — Foundation Running quedó aprobado mediante la ejecución
[CI 42399043070](https://github.com/oraclesupreme63-droid/RACEOPS/actions/runs/42399043070).
Los jobs de calidad y de contenedores terminaron correctamente.

Esto no significa que el producto RaceOps esté completo. La versión actual no
incluye todavía usuarios, login, equipos, pilotos, vehículos, eventos,
sesiones ni el Session Learning Loop. Lo construido reduce el riesgo técnico
y permite comenzar las funciones del producto sobre una base comprobada.

No se asigna un porcentaje artificial de avance: completar seis fases de
preparación y fundación no equivale a completar el mismo porcentaje del
producto funcional.

## 3. Resultado disponible actualmente

### 3.1 Aplicación e infraestructura

- aplicación FastAPI mediante `create_app()`;
- endpoints `/health`, `/ready`, `/docs` y `/openapi.json`;
- configuración tipada y separada por entorno;
- PostgreSQL 18.6;
- SQLAlchemy 2.x y Psycopg 3;
- Alembic con revisión base `20261024_0001`;
- errores seguros con RFC 9457;
- correlación mediante `X-Request-ID`;
- logging JSON sin bodies, tokens ni secretos;
- Dockerfile multi-stage con usuario no privilegiado;
- Docker Compose con servicios `db`, `migrate` y `api`;
- GitHub Actions para calidad y smoke test del contenedor.

### 3.2 Verificación

- 22 pruebas aprobadas;
- cobertura total `90.75 %` con mínimo obligatorio de 90 %;
- Ruff format y lint aprobados;
- mypy aprobado;
- `alembic check` sin migraciones faltantes;
- migración `upgrade → downgrade → upgrade` probada;
- imagen productiva sin pytest;
- runtime con UID/GID `10001`;
- jobs `Python quality and tests` y `Container smoke test` aprobados en Linux.

### 3.3 Documentación

Se encuentran documentados:

- definición, visión, alcance y objetivos;
- investigación, evidencia, contraevidencia e hipótesis;
- requerimientos, casos de uso y criterios de aceptación;
- permisos y visibilidad;
- modelo de dominio, invariantes y estados;
- arquitectura y ADR;
- riesgos y roadmap;
- ejecución local, aprendizaje y cierre de Gate G5.

## 4. Estado de gates

| Gate | Resultado actual | Observación |
|---|---|---|
| G0 — Definition Ready | Aprobado | Definición y alcance disponibles |
| G1 — Problem Ready | Aprobado condicionalmente | La investigación continúa durante el proyecto |
| G2 — Requirements Ready | Aprobado condicionalmente | Requisitos P0 listos; cambiarán con evidencia |
| G3 — Domain Ready | Aprobado condicionalmente | Modelo suficiente para programar, no definitivo |
| G4 — Architecture Ready | Aprobado condicionalmente | Arquitectura modular monolítica seleccionada |
| G5 — Foundation Running | Aprobado | CI real y stack local verificados |
| G6 — Vertical Alpha | Pendiente | Requiere Fases 6–8 |
| G7 — Validated MVP | Pendiente | Requiere pruebas con datos y usuarios |
| G8 — Fair Candidate | Pendiente | Requiere demo estable y alcance congelado |
| G9 — Release | Pendiente | Requiere `v1.0.0` publicado |

Las aprobaciones condicionales no bloquean la programación. Conservan abiertas
las hipótesis que sólo pueden resolverse mediante usuarios y datos reales.

## 5. Estado de la evidencia de producto

### Respaldado por evidencia

- una sesión necesita más contexto que una lista de tiempos;
- feedback del piloto y datos disponibles son complementarios;
- diferentes roles necesitan información distinta;
- parte de la información técnica debe ser confidencial;
- las decisiones deben producir prioridades y acciones concretas;
- una herramienta con captura excesiva puede ser rechazada.

### Parcialmente respaldado

- fragmentación de información entre personas y herramientas;
- valor de recuperar conocimiento al regresar a una pista;
- necesidad de conectar observaciones, acciones y resultados;
- utilidad de mantenimiento conectado con sesiones.

### Hipótesis pendientes

- frecuencia e impacto económico del problema;
- adopción repetida por equipos pequeños;
- disposición a pagar y comprador real;
- formatos de importación prioritarios;
- necesidad de logística, presupuesto o comunicación en vivo.

### Fuera de v1 salvo nueva evidencia

- telemetría en tiempo real;
- sustitución de AiM, MyChron o MoTeC;
- recomendaciones automáticas de conducción mediante IA;
- transcripción de radio;
- ERP de inventario;
- facturación y complejidad SaaS comercial.

## 6. Trabajo pendiente por horizonte

### Núcleo obligatorio del MVP

1. **Fase 6 — Identidad y autorización:** User, Team, TeamMembership, login,
   Argon2id, JWT, RBAC y aislamiento entre equipos.
2. **Fase 7 — Base operativa:** Drivers, Vehicles, Tracks y Events.
3. **Fase 8 — Flujo vertical:** Session, laps, sectors, feedback,
   observaciones, análisis, hipótesis, prioridades, acciones y resultados.
4. **Fase 9 — Validación:** datos representativos y pruebas con usuarios.

Estas cuatro fases tienen prioridad absoluta. Sin ellas RaceOps es una
fundación técnica, no un producto demostrable.

### Expansión relacionada

- Fase 10: mantenimiento conectado con observaciones y vehículos;
- Fase 11: historial, reportes y analítica reproducible;
- Fase 12: experiencia web consolidada y responsive;
- Fase 13: robustez, autorización negativa y seguridad;
- Fase 14: medición de rendimiento.

### Funciones condicionadas por evidencia

- Fase 15: CSV, clima, archivos y alertas;
- Fase 16: actualizaciones inmediatas mediante SSE o WebSocket.

### Entrega y evolución

- Fases 17–19: preparación de feria, `v1.0.0` y portafolio;
- Fases 20–22: validación posterior, decisión comercial y posible cloud.

## 7. Plan propuesto para Fase 6

### Bloque 6.1 — Contrato de identidad

- **Estado:** preparado para aprobación.
- se confirmaron `User`, `Team`, `TeamMembership` y `Role`;
- el primer Administrator se crea mediante bootstrap transaccional;
- un User puede tener una Membership por Team y el token selecciona una;
- se definieron login, identidad actual y errores;
- se registraron ADR-011 y ADR-012 como propuestas.

### Bloque 6.2 — Persistencia

- modelos SQLAlchemy y enums;
- restricciones de unicidad y estado;
- migración Alembic;
- pruebas de constraints y round-trip de migraciones.

### Bloque 6.3 — Credenciales y tokens

- Argon2id para passwords;
- JWT de acceso breve;
- claims mínimos;
- validación de usuario y membresía actuales en PostgreSQL;
- pruebas de token válido, vencido, manipulado y usuario desactivado.

### Bloque 6.4 — API de identidad

- login;
- consulta de identidad actual;
- selección o contexto de Team cuando corresponda;
- respuestas que nunca serializan password ni hash.

### Bloque 6.5 — RBAC y aislamiento

- dependencias de autenticación y autorización;
- política de menor privilegio;
- denegación entre Teams sin revelar existencia;
- pruebas positivas y negativas por rol;
- base reutilizable para recursos de Fase 7.

### Bloque 6.6 — Cierre técnico

- documentación OpenAPI;
- actualización de matrices de trazabilidad;
- suite completa y CI;
- revisión de seguridad;
- aprobación antes de comenzar recursos operativos.

## 8. Decisiones propuestas en el Bloque 6.1

1. **Provisionamiento inicial recomendado:** no ofrecer registro público en
   v1; crear el primer Administrator mediante un comando de bootstrap y dejar
   la gestión de usuarios dentro del equipo para una API posterior.
2. **Múltiples equipos recomendado:** permitir múltiples TeamMembership en el
   modelo, pero operar una sola membresía activa por contexto de petición.
3. **Tokens recomendado:** access token breve sin refresh token en P0, conforme
   a ADR-004.
4. **Frontend recomendado:** mantener el cliente mínimo; validar primero los
   contratos mediante OpenAPI y pruebas HTTP.

Estas decisiones ya están materializadas en
`docs/identity/identity-contract.md`, pero siguen pendientes de aprobación del
propietario antes de comenzar modelos y migraciones.

## 9. Publicación del repositorio

La publicación se separó en dos repositorios:

1. `RACEOPS-research`, privado, conserva los registros y la trazabilidad
   completa de Product Discovery;
2. `RACEOPS`, público, contiene código, arquitectura, decisiones y una síntesis
   agregada sin registros atribuibles a participantes individuales.

La versión pública no incluye nombres, citas, contactos, equipos ni
configuraciones técnicas de participantes. Esta separación permite mostrar el
trabajo de ingeniería sin convertir la visibilidad de GitHub en permiso para
publicar investigación.

## 10. Conclusión

RaceOps avanza por el camino correcto: la solución sigue enfocada en preservar
el razonamiento operativo alrededor de una sesión y no en reemplazar software
profesional de telemetría. La prioridad inmediata es implementar identidad y
aislamiento de equipos de forma comprobable, seguida por una base operativa y
un flujo vertical completo.

El siguiente punto de aprobación es el contrato del Bloque 6.1.
