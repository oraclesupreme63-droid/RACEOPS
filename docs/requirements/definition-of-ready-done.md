# RaceOps — Definition of Ready y Definition of Done

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G2
- **Aplicación:** Elementos de backlog, historias y cambios de alcance

## 2. Definition of Ready — DoR

Un elemento puede entrar a implementación cuando:

- [ ] tiene identificador, título y resultado esperado;
- [ ] pertenece a una prioridad P0–P3;
- [ ] tiene actor principal;
- [ ] está relacionado con requisito o decisión técnica;
- [ ] cuenta con criterios de aceptación verificables;
- [ ] se conocen precondiciones y reglas principales;
- [ ] se identificaron dependencias;
- [ ] se conocen permisos y nivel de visibilidad aplicables;
- [ ] los estados y términos utilizados están definidos o marcados para
      modelado;
- [ ] los casos negativos importantes están descritos;
- [ ] no depende de una función fuera de alcance;
- [ ] las dudas que podrían cambiar sustancialmente la solución están
      resueltas o explícitamente aceptadas como hipótesis;
- [ ] su tamaño permite terminarlo y probarlo dentro de una iteración
      razonable, o fue dividido;
- [ ] no introduce datos reales sensibles sin consentimiento.

### Un elemento no está Ready si

- se justifica solamente porque «se vería bien»;
- no tiene usuario o resultado identificable;
- requiere telemetría en vivo, IA, facturación o integración no aprobada;
- mezcla varios módulos que pueden entregarse separadamente;
- la autorización queda delegada únicamente al frontend;
- depende de un dato cuyo origen no está definido.

## 3. Definition of Done — DoD general

Un elemento se considera terminado cuando:

- [ ] cumple todos sus criterios de aceptación;
- [ ] respeta reglas de negocio e invariantes;
- [ ] aplica autorización en el servidor;
- [ ] comprueba aislamiento entre equipos cuando corresponda;
- [ ] filtra información según visibilidad;
- [ ] incluye pruebas automatizadas positivas y negativas proporcionales al
      riesgo;
- [ ] las pruebas existentes continúan aprobadas;
- [ ] maneja errores esperados mediante el formato común;
- [ ] no expone secretos ni información sensible en respuestas o logs;
- [ ] las operaciones relacionadas son atómicas;
- [ ] las migraciones necesarias existen y son reproducibles;
- [ ] la documentación afectada fue actualizada;
- [ ] la trazabilidad requisito–aceptación–prueba está actualizada;
- [ ] el código cumple formato, análisis estático y type hints acordados;
- [ ] CI aprueba las verificaciones configuradas;
- [ ] no se amplió silenciosamente el alcance;
- [ ] puede demostrarse con datos sintéticos o autorizados.

## 4. DoD para endpoints

Además del DoD general:

- [ ] contrato de entrada y salida documentado;
- [ ] validación de entrada;
- [ ] estados HTTP y errores consistentes;
- [ ] prueba de integración del camino principal;
- [ ] prueba de recurso inexistente;
- [ ] prueba de permiso insuficiente;
- [ ] prueba de recurso perteneciente a otro equipo;
- [ ] paginación para colecciones potencialmente grandes;
- [ ] no existen campos internos o confidenciales serializados por accidente.

## 5. DoD para reglas P0

Además del DoD general:

- [ ] existe al menos una prueba automatizada de aceptación;
- [ ] se prueban límites e invariantes relevantes;
- [ ] si la regla deniega algo, existe una prueba negativa;
- [ ] si modifica varias entidades, se prueba rollback ante fallo;
- [ ] el criterio puede rastrearse hasta un RF y un AC.

## 6. DoD para seguridad

- [ ] no se almacenan contraseñas en texto plano;
- [ ] secretos fuera del repositorio;
- [ ] tokens con expiración;
- [ ] CORS con orígenes explícitos;
- [ ] errores sin información interna;
- [ ] logs sin credenciales, tokens o contenido confidencial innecesario;
- [ ] permisos comprobados con casos permitidos y denegados;
- [ ] búsquedas y conteos no revelan recursos confidenciales;
- [ ] cambios de rol y operaciones sensibles quedan auditados.

## 7. DoD para una versión demostrable

- [ ] versión identificable mediante tag o número;
- [ ] instrucciones de inicio comprobadas;
- [ ] Docker Compose funciona desde un entorno limpio compatible;
- [ ] migraciones se aplican correctamente;
- [ ] `GET /health` responde;
- [ ] dataset de demostración reproducible;
- [ ] ninguna credencial real está incluida;
- [ ] flujo prometido puede ejecutarse de principio a fin;
- [ ] existe alternativa de demostración sin conexión externa;
- [ ] limitaciones y funciones no incluidas están documentadas.

## 8. Excepciones

Una excepción a DoR o DoD debe indicar:

- motivo;
- riesgo;
- responsable;
- fecha o condición de resolución;
- impacto en el gate correspondiente.

«Funciona en mi equipo» o «se arreglará después» no constituyen evidencia
de finalización.
