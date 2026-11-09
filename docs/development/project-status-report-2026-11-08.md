# RaceOps — Informe de estado del proyecto

## 1. Corte ejecutivo

- **Fecha:** 8 de noviembre de 2026
- **Versión estable alcanzada:** `v0.1 — Foundation`
- **Versión en construcción:** `v0.2 — Operational Base`
- **Fase actual:** 7 — Base operativa
- **Bloque actual:** 7.4 implementado; pendiente de aprobación del propietario
- **Próximo bloque:** 7.5 — APIs de Tracks y Events
- **Bloqueador técnico actual:** ninguno

RaceOps ya es un backend ejecutable, no solamente documentación. Puede
autenticar una Membership activa, aplicar RBAC y aislamiento por Team, y
administrar Drivers y Vehicles mediante contratos HTTP probados. Tracks y
Events ya existen en PostgreSQL, pero todavía no tienen API pública.

No se asigna un porcentaje global artificial: las fases posteriores tienen
costos y evidencia muy distintos. En Fase 7 hay cuatro de seis bloques
técnicamente terminados; 7.1–7.3 están aprobados y 7.4 espera esta aprobación.

## 2. Qué funciona hoy

- FastAPI, PostgreSQL, SQLAlchemy, Alembic y Docker Compose;
- `/health`, `/ready`, `/docs` y OpenAPI;
- errores RFC 9457, request IDs y logging seguro;
- Teams, Users y Memberships por rol;
- bootstrap local de Administrator;
- login JWT con contexto de Team y `/auth/me`;
- RBAC de cinco roles y ocultamiento de recursos ajenos;
- Driver: crear, listar, consultar, actualizar, activar y desactivar;
- Vehicle: crear, listar, consultar, renombrar y cambiar disponibilidad;
- preservación histórica sin DELETE normal;
- CI, lint, tipos, cobertura, migraciones y smoke tests de contenedor.

## 3. Qué falta a corto plazo

### Para cerrar Fase 7 y `v0.2`

1. aprobar el Bloque 7.4;
2. construir y aprobar APIs de Tracks y Events en el Bloque 7.5;
3. ejecutar cierre completo, actualizar trazabilidad y evidenciar `v0.2` en
   el Bloque 7.6.

### Para tener el primer flujo útil de producto

La Fase 8 debe unir Event → Session → Driver + Vehicle → resultados → feedback
→ análisis → prioridades → acción → siguiente Session → outcome. Ese flujo
vertical es el núcleo de RaceOps y el requisito del Gate G6.

### Para declarar un MVP validado

- Fase 9: probar con datos y usuarios reales;
- Fase 10: mantenimiento conectado a síntomas y acciones;
- Fase 11: historial, reportes y comparación;
- Fase 12: frontend consolidado y de baja fricción;
- Fases 13–14: robustez, seguridad y medición de rendimiento;
- Fases 17–18: demo confiable y release `v1.0.0`.

Las Fases 15 y 16 son condicionadas: CSV o actualizaciones en vivo sólo
entran con evidencia. Las Fases 20–22 son posteriores a la feria y no deben
distraer al MVP.

## 4. Contratiempos y riesgos activos

### Sin bloqueo inmediato

No existe una falla funcional conocida que impida continuar. El stack local
está operativo y las pruebas específicas de Vehicle pasan con PostgreSQL.

### Riesgos de producto

- La necesidad está parcialmente validada, no universalmente demostrada. Hay
  tres entrevistas relevantes y contraevidencia de que equipos disciplinados
  ya funcionan con herramientas actuales.
- La unicidad del identificador de Vehicle y el ciclo exacto de Event siguen
  siendo hipótesis pequeñas y reversibles.
- Sin pruebas de uso reales no sabemos todavía si la captura será lo bastante
  rápida durante un fin de semana de carrera.

### Dependencias de alcance

- Driver no puede ver Vehicles relacionados hasta que Session exista; dar un
  catálogo completo ahora rompería la regla de mínimo privilegio.
- Las reglas «Driver activo» y «Vehicle READY» sólo podrán comprobarse de
  extremo a extremo en Fase 8.
- Aún no hay frontend; Swagger `/docs` es la interfaz técnica de prueba.
- No hay importación CSV, telemetría en vivo ni recomendaciones automáticas;
  están deliberadamente fuera del núcleo actual.

### Riesgos técnicos y operativos

- Las pruebas integradas son más lentas porque generan hashes Argon2 y datos
  aislados; esto protege realismo de seguridad, pero conviene optimizar
  factories si el tiempo de CI crece demasiado.
- La fecha oficial de la feria aún no está publicada, así que no existe un
  calendario confiable para convertir el roadmap en semanas.
- Existe un archivo local no rastreado llamado `tatus`. Su origen no está
  confirmado; permanece intacto y excluido de los commits hasta aclararlo.

## 5. Decisión recomendada

Mantener la dirección actual. La arquitectura sigue siendo un monolito
modular y el alcance de Vehicle es pequeño. Después de aprobar 7.4, conviene
cerrar Tracks/Events y pasar pronto a Fase 8: el valor de RaceOps no se valida
con más catálogos, sino con el ciclo completo de aprendizaje entre sesiones.
