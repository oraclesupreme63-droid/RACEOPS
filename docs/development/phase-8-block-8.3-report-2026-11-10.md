# RaceOps — Reporte del Bloque 8.3: API y asignación

## 1. Estado

- **Fecha:** 10 de noviembre de 2026
- **Fase:** 8 — Session Learning Loop
- **Bloque:** 8.3 — API y asignación
- **Resultado:** implementado y verificado; pendiente de aprobación del propietario
- **Siguiente bloque:** 8.4 — Ciclo y bloqueo de resultados

## 2. Capacidad entregada

RaceOps ya permite crear, listar, consultar y editar una Session planificada
mediante `/api/v1/sessions`. El servidor deriva el Team de la identidad activa,
normaliza la fecha a UTC e impide que el cliente controle estados, timestamps o
propiedad.

La creación valida dentro de una sola transacción que Event, Driver y Vehicle
pertenezcan al Team; además exige Driver `ACTIVE` y Vehicle `READY`. Una
asignación inválida no deja escrituras parciales. Event queda inmutable dentro
de Session y los demás campos sólo pueden editarse mientras esté `PLANNED`.

## 3. Autorización y privacidad

Se añadió `READ_SESSIONS` de forma independiente de `WRITE_SESSIONS`:

- Administrator, Team Manager y Engineer pueden crear y editar;
- Mechanic tiene lectura del Team, sin escritura;
- Driver sólo consulta Sessions asignadas a su Driver Profile;
- Driver sólo puede leer Events y Vehicles relacionados por esas Sessions;
- recursos ajenos, de otro Team o no relacionados responden como no encontrados.

Esto aplica el principio de información correcta para la persona correcta sin
abrir el catálogo completo al piloto.

## 4. Consistencia histórica

Crear Session y cambiar la pista de Event bloquean la fila del Event dentro de
la transacción. Una vez que existe una Session, mover el Event a otro Track se
rechaza con `event_track_locked`; otros metadatos del Event siguen siendo
editables. Así la pista histórica se obtiene desde Event sin duplicarla en
Session y sin introducir una carrera de concurrencia.

## 5. Contrato y errores

Se publicaron los errores estables:

- `session_assignment_conflict` para Driver o Vehicle no elegible;
- `session_not_editable` para editar fuera de `PLANNED`;
- `event_track_locked` para mover un Event con Sessions;
- `resource_not_found` para recursos inexistentes, cruzados o no relacionados.

No existe DELETE ni comandos de ciclo todavía. Start, pause, resume, complete,
cancel y lock-results permanecen fuera de OpenAPI hasta el Bloque 8.4.

## 6. Evidencia de verificación

- 152 pruebas ejecutadas en la suite completa inicial: 150 aprobaron y dos
  pruebas antiguas detectaron correctamente el cambio del contrato de Driver;
- las expectativas antiguas se actualizaron a lista vacía y 404 por relación;
- 9 pruebas focalizadas posteriores aprobaron;
- cobertura total observada: 94.22 %, superior al mínimo de 90 %;
- Ruff, formato y mypy estricto aprobados;
- `alembic check` sin operaciones pendientes;
- Docker Compose válido y PostgreSQL local operativo.

GitHub Actions ejecutará nuevamente la suite completa limpia al publicar el
commit del bloque. Su resultado quedará como evidencia final del repositorio.

## 7. Punto de aprobación

Con aprobación comienza el Bloque 8.4. Allí se implementarán las transiciones
de actividad, timestamps server-side y el bloqueo independiente de resultados.
