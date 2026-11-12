# RaceOps — Reporte del Bloque 9.2: cliente mínimo de validación

## Estado

- **Fecha:** 12 de noviembre de 2026
- **Resultado:** implementado y verificado; pendiente de aprobación del
  propietario
- **Siguiente bloque:** 9.3 — dataset y ensayo interno

## Entregado

- cliente web buildless servido por FastAPI en `/app/`;
- acceso mediante login real y selección de Team cuando corresponde;
- recorrido por contexto, feedback, análisis, acciones y aprendizaje;
- vistas y controles ajustados al Role, manteniendo el backend como autoridad;
- formularios breves, estados de carga, confirmaciones y errores seguros;
- layout responsive, navegación por teclado y regiones accesibles;
- token limitado a la pestaña mediante `sessionStorage`;
- assets incluidos en la distribución Python y sin dependencias externas;
- ADR-013 y pruebas automatizadas del punto de entrada y empaquetado.

## Decisiones

- **Respaldado:** se necesita una interfaz operable para medir usabilidad; la
  documentación OpenAPI sólo demuestra contratos técnicos.
- **Respaldado:** usar el mismo origen conserva la configuración de seguridad
  y reduce infraestructura durante la validación.
- **Parcialmente respaldado:** la interfaz responde a pantallas pequeñas y
  controles táctiles, pero todavía no ha sido probada por usuarios del nicho.
- **Hipótesis:** los estados y formularios son suficientemente claros bajo la
  presión de un fin de semana de carrera.
- **Rechazado:** duplicar reglas del dominio en JavaScript o convertir este
  prototipo en el frontend completo antes de obtener evidencia.

## Verificación técnica

- sintaxis JavaScript validada con Node;
- formato y lint con Ruff;
- tipos estáticos con mypy estricto;
- pruebas específicas del cliente y su empaquetado;
- construcción y health check del stack Docker;
- inspección visual del acceso, jerarquía, foco y consola del navegador;
- suite global: **220 pruebas aprobadas** en 104.68 s;
- cobertura total: **91.89 %**, superior al umbral de 90 %;
- stack Docker saludable, migración finalizada y respuestas `200` de
  `/health`, `/ready` y `/app/`.

## Alcance pendiente

El cliente aún no contiene cuentas ni datos para una demostración completa.
El Bloque 9.3 preparará un escenario anonimizado, cuentas locales por Role y
un ensayo interno antes de involucrar participantes.

## Punto de aprobación

Con aprobación comenzará el Bloque 9.3. No se usarán credenciales, telemetría
ni información personal reales para crear el escenario de prueba.
