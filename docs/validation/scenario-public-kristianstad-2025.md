# RaceOps — Dataset público `phase-9-public-v1`

## Propósito

Ejecutar el Session Learning Loop con tiempos reales publicados de karting sin
atribuir al piloto o al equipo feedback, setups o decisiones que la fuente no
contiene.

Este dataset aporta evidencia factual de timing. No aporta evidencia de que
RaceOps sea fácil de usar, de que el equipo siguiera el proceso propuesto ni de
que una acción causara un cambio de rendimiento.

## Fuente

- **Publicador:** FIA Karting / Apex Timing.
- **Evento:** Mondokart.com FIA Karting World Championship, categoría OK.
- **Lugar y fecha:** Kristianstad, Suecia; 11–14 de septiembre de 2025.
- **Documento:** [Booklet OK publicado por FIA Karting](https://nocache.fiakarting.com/sites/default/files/xml_folder/2025/Kristianstad/Booklet_OK.pdf).
- **Secciones utilizadas:** Qualifying Heat D-F Results/Lap Time Analysis,
  Final Results documento 59.2 y Final Lap Time Analysis.
- **Fecha de consulta:** 13 de noviembre de 2026.

El documento marca Final Results como `OFFICIAL`. Las páginas de Lap Time
Analysis indican que son informativas y no tienen valor reglamentario. RaceOps
conserva esa distinción y no redistribuye el PDF.

## Minimización de identidad

La publicación identifica a los competidores. RaceOps no necesita conservar el
nombre para probar el flujo, por lo que el kart público número 27 se representa
como:

```text
Driver: Public Driver 027
Vehicle: PUBLIC-KART-027
```

La referencia al documento se conserva para auditoría, pero la base local no
presenta el nombre publicado como si fuera usuario de RaceOps.

## Sesiones incorporadas

| Campo | Session fuente | Session de comparación |
|---|---|---|
| Sesión | Qualifying Heat D-F | Final |
| Inicio publicado | 13/09/2025 14:28:46 CEST | 14/09/2025 13:58:51 CEST |
| Fin publicado | 13/09/2025 14:40:07 CEST | 14/09/2025 14:20:37 CEST |
| Clima | Scattered cloud | Scattered cloud |
| Aire | 21 °C | 18 °C |
| Pista | Dry | Dry |
| Vueltas del kart 27 | 13 | 25 |
| Mejor vuelta | 50.368 s | 50.348 s |

La diferencia de mejor vuelta es `-0.020 s`. No se interpreta automáticamente
como una mejora: cambió la Session, la temperatura ambiente y el contexto de
carrera, y no se publicaron feedback ni cambios de setup.

## Transformación reproducible

| Fuente publicada | RaceOps | Regla |
|---|---|---|
| Lap Time en segundos | `duration_us` | segundos × 1,000,000 |
| Sector 1–3 | tres `Sector` | mismo orden, estado `VALID` |
| Start Time | `started_at` | conservar CEST (`+02:00`) |
| End Time | `ended_at` | conservar CEST (`+02:00`) |
| Start Time | `scheduled_at` | adaptador explícito porque no hay horario planeado |
| Air | temperatura ambiente | unidad `C` |
| Track: Dry | condición de pista | texto `Dry` |
| nombre público | etiqueta seudónima | no persistir nombre en RaceOps |
| velocidad por vuelta | no importada | el modelo canónico todavía no la soporta |

La fuente versionada utilizada por el cargador es
`src/raceops/validation/scenario_public_kristianstad_2025.json`. No debe
sobrescribirse después de publicarse; cualquier corrección requiere una nueva
versión y una nota de procedencia.

## Separación entre hechos y ejercicio

### Hechos publicados

- evento, lugar y fechas;
- nombres de las sesiones;
- horas de inicio y fin;
- clima, temperatura ambiente y pista seca;
- tiempos de vuelta y de tres sectores.

### Datos sintéticos de entrenamiento

- Team y cuentas de RaceOps;
- etiqueta seudónima del Driver;
- feedback utilizado en el ejercicio;
- Analysis, Hypothesis, Priority y Action;
- conclusión del Outcome.

Cada texto de ejercicio indica que es sintético. No se afirma que el piloto,
Forza Racing o sus ingenieros hayan expresado o ejecutado esas decisiones.

## Crear una instancia local

Con PostgreSQL y migraciones activos:

```powershell
.\.venv\Scripts\python.exe -m raceops.validation.seed_scenario `
  --scenario-id public-kristianstad-1 `
  --dataset public-kristianstad-2025
```

El comando conserva las mismas protecciones del escenario sintético: sólo
`local`/`test`, contraseña solicitada sin argumento, hashes Argon2id, cuentas
por Role y rechazo de identificadores duplicados.

## Proceso completo en RaceOps

1. **Importación:** Engineer revisa las 13 vueltas y tres sectores de
   Qualifying Heat D-F.
2. **Contexto:** confirma 21 °C, pista seca y que no existe feedback publicado.
3. **Observación:** registra únicamente que la mejor vuelta publicada fue
   50.368 s y que falta contexto causal.
4. **Hypothesis:** utiliza `UNKNOWN` y confianza baja; no inventa un problema
   de conducción o setup.
5. **Priority:** solicita capturar feedback y el cambio autorizado de setup en
   una futura Session comparable.
6. **Action:** asigna a Engineer la captura de contexto; no ordena una
   reparación sin evidencia.
7. **Comparación:** revisa las 25 vueltas de la Final, con mejor vuelta de
   50.348 s y aire a 18 °C.
8. **Outcome:** registra `INCONCLUSIVE`; la diferencia de 0.020 s no demuestra
   efecto causal.
9. **Learning:** preserva que timing real sin feedback/setup permite describir
   qué ocurrió, pero no explicar por qué ocurrió.

## Validaciones automáticas

- 13 + 25 vueltas cargadas;
- tres sectores por vuelta;
- suma exacta de sectores igual al tiempo de cada vuelta;
- mejores vueltas iguales a la publicación;
- diferencia exacta de 20,000 microsegundos;
- 114 sectores persistidos en PostgreSQL;
- procedencia obligatoria y separación explícita de campos sintéticos.

## Limitación pendiente

El dataset permite una prueba técnica realista, no una prueba real de usuario.
Los Bloques 9.4–9.6 seguirán abiertos hasta observar participantes y, si existe
autorización, repetir el ciclo con feedback o decisiones reales del equipo.
