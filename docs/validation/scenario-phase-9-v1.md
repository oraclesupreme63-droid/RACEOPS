# RaceOps — Escenario de validación `phase-9-v1`

## Propósito

Proporcionar un caso sintético, reproducible y deliberadamente imperfecto
para probar el Session Learning Loop sin solicitar datos privados de un equipo.
No representa evidencia de adopción ni un caso real anonimizado.

## Caso congelado

- pista y equipo ficticios;
- Driver ficticio `Alex Synthetic`;
- Practice 1 como Session fuente y Practice 2 como evaluación;
- temperatura de pista desconocida en la Session fuente;
- una vuelta de salida, dos vueltas válidas y una vuelta inválida más rápida;
- sectores ausentes e incompletos;
- presión trasera derecha no preservada;
- resultado esperado del ensayo: `INCONCLUSIVE`, no mejora atribuida.

La fuente versionada es
`src/raceops/validation/scenario_v1.json`. Cambiar su contenido requiere una
nueva versión; no se reescribe `phase-9-v1` después de iniciar pruebas con
participantes.

## Crear una instancia local

Con PostgreSQL y las migraciones activos:

```powershell
.\.venv\Scripts\python.exe -m raceops.validation.seed_scenario `
  --scenario-id pilot-round-2
```

El comando:

- funciona únicamente con `RACEOPS_ENV=local` o `test`;
- solicita y confirma una contraseña compartida sin aceptarla como argumento;
- almacena únicamente hashes Argon2id;
- crea una Team nueva y cinco cuentas locales;
- rechaza un `scenario-id` ya utilizado y nunca sobrescribe datos.

Patrón de cuentas:

```text
administrator.<scenario-id>@raceops.local
team-manager.<scenario-id>@raceops.local
engineer.<scenario-id>@raceops.local
mechanic.<scenario-id>@raceops.local
driver.<scenario-id>@raceops.local
```

La contraseña no se guarda en Git ni debe corresponder a una contraseña real
del participante.

## Instancias locales del Bloque 9.3

| Instancia | Estado | Uso |
|---|---|---|
| `round-1` | completada | ensayo interno de extremo a extremo |
| `pilot-round-1` | limpia y congelada | primera ronda observada |

Estas instancias viven sólo en el PostgreSQL local. Los identificadores y la
contraseña no forman parte del dataset versionado.

## Secuencia de ensayo

1. Driver abre Practice 1 y registra feedback con incertidumbre explícita.
2. Engineer registra observación, selecciona evidencia y crea Analysis.
3. Engineer propone una Hypothesis con confianza media.
4. Engineer crea prioridades para Driver y Mechanic, y una Action mecánica.
5. Mechanic planifica, inicia y completa la Action asignada.
6. Engineer compara Practice 2 y registra un Outcome inconcluso.
7. Engineer y Driver abren la Learning Chain y comparan sus proyecciones.

## Resultado del ensayo interno

El 13 de noviembre de 2026 se completó el recorrido desde el cliente web sin
errores críticos ni pérdida de información. Se comprobó que:

- la vuelta inválida no altera la mejor vuelta elegible;
- los datos desconocidos aparecen como ausentes, no inventados;
- la Hypothesis puede permanecer inconclusa;
- Mechanic puede ejecutar el trabajo asignado;
- Driver recibe Action y conclusión pública, pero no Analysis, Hypothesis ni
  detalles confidenciales de Ingeniería.

## Preguntas abiertas para participantes

- Un Mechanic sólo ve feedback que él mismo haya registrado; debe observarse
  si necesita un resumen explícito del síntoma del Driver.
- Debe medirse si las transiciones `Planificar → Iniciar → Completar` añaden
  claridad o fricción durante un fin de semana real.
- Debe verificarse si la diferencia entre vuelta inválida y vuelta elegible es
  suficientemente visible sin explicación.

Estas preguntas son evidencia pendiente, no defectos confirmados.
