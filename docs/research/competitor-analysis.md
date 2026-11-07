# RaceOps — Análisis de competidores y alternativas

## 1. Información del documento

- **Versión:** 0.1
- **Estado:** Aprobado
- **Fecha de consulta de fuentes:** 6 de octubre de 2026
- **Fuentes:** Documentación oficial de AiM y MoTeC; INT-001, INT-002 e INT-003
- **Propósito:** Delimitar el espacio de RaceOps sin duplicar herramientas existentes.

## 2. Conclusión principal

RaceOps no debería competir contra las herramientas de telemetría en
adquisición, gráficas, mapas, video, canales matemáticos o comparación
avanzada de vueltas.

Su posible espacio es otro:

> Conservar quién reportó algo, qué se interpretó, qué decisión se tomó,
> quién debía actuar y qué ocurrió en la siguiente sesión.

Esta diferenciación todavía es una hipótesis que debe validarse con usuarios.

## 3. Herramientas especializadas

### 3.1 AiM RaceStudio 3

La documentación oficial muestra que RaceStudio 3 administra dispositivos
AiM, descarga datos y videos y permite analizarlos. Su módulo de análisis
ofrece, entre otras capacidades:

- organización de sesiones mediante colecciones;
- gráficas de canales;
- mapas de pista;
- comparación de vueltas y sectores;
- video sincronizado;
- canales matemáticos;
- reportes;
- comentarios de sesión;
- exportación de datos, incluyendo CSV.

**Fuentes oficiales:**

- [RaceStudio 3 in Few Words](https://www.aim-sportline.com/docs/racestudio3/manual/html/racestudio3.html)
- [RaceStudio 3 Analysis](https://www.aim-sportline.com/docs/racestudio3/manual/html/analysis.html)

**Lo que resuelve bien:** análisis técnico y organización de datos producidos
por el ecosistema AiM.

**Lo que no se confirmó:** que gestione un flujo completo entre roles para
registrar feedback, hipótesis, responsables, acciones y resultados
posteriores. Que no aparezca en las páginas revisadas no demuestra que la
capacidad no exista.

**Decisión:** RaceOps no replicará sus gráficas ni su análisis técnico.

### 3.2 MyChron

MyChron6 es un dispositivo especializado en karting. Registra vueltas,
sectores, velocidad, RPM, temperaturas, posición, aceleraciones y otros
datos. También ofrece tiempo predictivo, delta contra una vuelta de
referencia y descarga de datos para analizarlos en RaceStudio 3.

**Fuente oficial:**

- [AiM MyChron6](https://aim-sportline.com/en/products/mychron6/index.htm)

**Lo que resuelve bien:** adquisición y presentación de información durante
la conducción.

**Relación con RaceOps:** MyChron no es solamente un competidor; puede ser
una fuente externa de resultados y telemetría.

**Decisión:** RaceOps no adquirirá datos directamente del vehículo en V1.

### 3.3 MoTeC i2

MoTeC i2 proporciona análisis mediante proyectos, hojas de trabajo,
gráficas, reportes, overlays, video sincronizado, canales matemáticos y
comparación de vueltas. También contempla setup sheets y exportación a CSV
y MATLAB.

**Fuente oficial:**

- [MoTeC i2](https://motec.com.au/products/i2)

**Lo que resuelve bien:** análisis profundo de rendimiento, chasis y motor.

**Lo que no se confirmó:** que administre el flujo operativo completo
propuesto para RaceOps ni permisos específicos para piloto, mecánico,
ingeniería y administración.

**Decisión:** RaceOps no intentará convertirse en una versión simplificada
de MoTeC i2.

## 4. Alternativas sin software especializado

### 4.1 Papel

**Ventajas potenciales:**

- rápido;
- económico;
- flexible;
- funciona sin conexión;
- conocido por el equipo.

**Posibles limitaciones:**

- búsqueda histórica;
- relación entre sesiones;
- acceso simultáneo;
- control de visibilidad;
- conservación y respaldo.

Estas limitaciones son inferencias. Deben observarse registros reales antes
de considerarlas problemas demostrados.

### 4.2 Hojas de cálculo y documentos compartidos

**Ventajas potenciales:**

- muy flexibles;
- familiares;
- fáciles de adaptar;
- de bajo costo;
- no requieren adoptar una plataforma especializada.

**Posibles limitaciones:**

- estructura inconsistente;
- duplicación;
- dificultad para relacionar entidades;
- permisos demasiado generales;
- seguimiento manual de acciones.

Todavía se necesita evidencia directa de equipos que utilicen este método.

### 4.3 Aplicaciones internas

INT-002 confirmó que algunos equipos desarrollan herramientas propias.

**Ventajas potenciales:**

- se ajustan al proceso particular;
- pueden integrarse con herramientas existentes;
- el equipo conserva control sobre sus datos.

**Riesgo para RaceOps:** una herramienta interna bien adaptada puede ser
superior a una plataforma genérica.

### 4.4 No cambiar nada

Esta puede ser la alternativa más fuerte.

Un equipo puede preferir:

- RaceStudio o MoTeC;
- una conversación después de la sesión;
- algunas notas;
- la experiencia de sus integrantes.

RaceOps tendrá que demostrar una mejora suficiente para justificar la nueva
captura de información.

## 5. Comparación estratégica

| Capacidad | RaceStudio/MyChron | MoTeC i2 | Papel/hojas | RaceOps propuesto |
|---|---:|---:|---:|---:|
| Adquisición de telemetría | Fuerte | Asociada con hardware MoTeC | No | Fuera de alcance |
| Análisis técnico profundo | Fuerte | Fuerte | Limitado | Fuera de alcance |
| Vueltas y sectores | Fuerte | Fuerte | Posible manualmente | Referencia o importación |
| Feedback estructurado del piloto | No confirmado | No confirmado | Posible | Propuesto |
| Hipótesis y nivel de confianza | No confirmado | No confirmado | Posible | Propuesto |
| Acción, responsable y resultado | No confirmado | No confirmado | Posible | Propuesto |
| Prioridades por rol | No confirmado | No confirmado | Posible | Propuesto |
| Confidencialidad por rol | No confirmado | No confirmado | Limitada | Propuesto con RBAC |
| Historial de razonamiento | Parcial mediante sesiones/notas | Parcial mediante proyectos/datos | Depende del equipo | Hipótesis central |
| Fricción adicional | Herramienta ya conocida | Herramienta ya conocida | Baja | Riesgo crítico |

«No confirmado» significa que no se encontró evidencia suficiente en las
fuentes revisadas; no significa que la capacidad definitivamente no exista.

## 6. Frontera propuesta para RaceOps

### 6.1 RaceOps sí administrará

- equipos y usuarios;
- eventos y sesiones;
- asignación de piloto y vehículo;
- contexto breve de la sesión;
- resultados de vueltas y sectores;
- feedback del piloto;
- observaciones;
- hipótesis y confianza;
- prioridades;
- acciones y responsables;
- resultado de la siguiente sesión;
- visibilidad según rol;
- consulta histórica.

### 6.2 RaceOps no administrará en V1

- configuración de dispositivos;
- adquisición desde sensores;
- telemetría en vivo;
- gráficas avanzadas de canales;
- canales matemáticos;
- análisis de suspensión;
- mapas técnicos;
- sincronización de video;
- sustitución de RaceStudio o MoTeC.

## 7. Estrategia de integración

### 7.1 V1

- registrar vueltas y sectores manualmente;
- adjuntar o referenciar archivos;
- asociar la referencia con una sesión;
- registrar solamente los hallazgos necesarios;
- permitir continuar aunque no exista telemetría.

### 7.2 Futuro, si se valida

```text
Archivo exportado
    ↓
Validación
    ↓
Normalización
    ↓
Asociación con sesión
    ↓
Vueltas y sectores
    ↓
Métricas seleccionadas
```

La importación CSV permanece como hipótesis. No se asumirá compatibilidad
universal entre versiones, dispositivos o formatos.

## 8. Posible diferenciador

RaceOps no buscará decir:

> «Analizamos mejor la telemetría».

Buscará comprobar si puede decir:

> «Ayudamos al equipo a recordar por qué tomó una decisión, quién actuó y
> si funcionó, sin reemplazar sus herramientas actuales».

## 9. Regla de actualización

Este análisis deberá actualizarse cuando se revisen nuevas herramientas,
se observen flujos reales o los participantes demuestren capacidades que no
aparecieron en la documentación consultada.
