# RaceOps — Mapeo de requisitos no funcionales

## 1. Información del documento

- **Versión:** 1.0
- **Estado:** Preparado para Gate G4
- **Cobertura:** 67 de 67 RNF con dirección arquitectónica

Este mapeo no afirma que los RNF ya estén implementados. Confirma que cada
grupo tiene una estrategia y una fase de verificación.

| Grupo | Cantidad | Dirección arquitectónica | Verificación principal |
|---|---:|---|---|
| RNF-SEC-001–012 | 12 | `security-strategy.md`, ADR-004 y ADR-007 | Fases 6 y 13 |
| RNF-REL-001–008 | 8 | `data-strategy.md`, `error-strategy.md`, ADR-002 y ADR-006 | Fases 5, 8 y 13 |
| RNF-PER-001–006 | 6 | paginación, queries explícitas y medición posterior | Fases 11 y 14 |
| RNF-USA-001–010 | 10 | cliente ligero, schemas por tarea y validación con usuarios | Fases 9 y 12 |
| RNF-COM-001–004 | 4 | REST JSON, formatos explícitos y núcleo sin integraciones | Fases 5, 8 y 12 |
| RNF-MAN-001–009 | 9 | monolito modular, Alembic, ADR y abstracción justificada | Desde Fase 5 |
| RNF-QUA-001–007 | 7 | `testing-strategy.md` y trazabilidad P0 | Desde Fase 5 |
| RNF-OBS-001–005 | 5 | `logging-strategy.md`, request IDs y health | Fases 5 y 14 |
| RNF-DEP-001–006 | 6 | `configuration-deployment.md` | Fases 5, 17 y 18 |
| **Total** | **67** | **Todos dirigidos** | **Implementación gradual** |

## 2. Aspectos deliberadamente diferidos

- No se fija un objetivo numérico de latencia o concurrencia sin escenario
  representativo; RNF-PER-002, 003 y 006 exigen medir antes de afirmar.
- Usabilidad y accesibilidad requieren cliente web y pruebas con personas;
  la arquitectura sólo evita bloquearlas.
- Backups, restauración, rate limiting y TLS deben probarse antes de uso real
  o exposición pública; documentarlos no equivale a haberlos operado.
- Compatibilidad de navegador se verifica cuando exista interfaz.

## 3. Regla de trazabilidad

Cuando un RNF se implemente, su prueba, configuración o evidencia reemplaza
la referencia de fase por una referencia concreta. Un RNF no puede marcarse
cumplido sólo porque exista este documento.

