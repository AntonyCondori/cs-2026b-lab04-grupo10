# Lab 08 · Bitácora para incorporar al informe

| ID | Herramienta y solicitud | Verificación | Decisión |
|---|---|---|---|
| B-01 | ChatGPT. Revisar la guía y desarrollar el aporte de Persona B para QA-04. | En el prototipo de 100 envíos se reprodujeron 99 duplicados sin táctica y 0 con idempotencia. Se comprobó que State solo no deduplica objetos reconstruidos. | Proponer ADR-007 y conservar salidas de la simulación. [Registro](bitacora-lab08-b.md) |
| C-01 | Codex. Implementar y verificar el aporte de Persona C. | Dos contratos de imports, seis fitness de calidad y 59 pruebas aprobadas. Se reprodujo una violación deliberada y se corrigió. | Integrar el aporte al repositorio y señalar el alcance en memoria. [Registro](aporte-ia-c.md) |
| REV-01 | Codex. Revisar qué estaba implementado en el repositorio antes del Lab 09. | Se reprodujeron los prototipos y se localizaron filas sin completar en el README y la etiqueta anunciada sin publicar. | Subsanar la documentación y distinguir resultados de laboratorio y despliegue. |
| SUB-01 | Codex. Subsanar las observaciones de los Labs 07 y 08. | PostgreSQL 16.2 ejecutó 71 pruebas, incluidas idempotencia, aislamiento, conflictos y rollback del servicio. En el Grupo 01 `pytest -q tests/test_fitness.py` encontró dos fixtures de entorno ausentes. | Preparar la integración y el borrador de evaluación emitida. Dejar la aceptación y el enlace de publicación sujetos a revisión. |
| CIERRE-01 | Codex. Consolidar las subsanaciones con el aporte inicial del Lab 09. | Se aplicó el commit del generador después de los dos commits de subsanación. El conjunto conservó las pruebas del servicio y del repositorio PostgreSQL. | Dejar la evidencia en el repositorio para que el equipo cierre PR y etiquetas. |

La discusión de State como única defensa se documenta como hipótesis descartada en [B-01](bitacora-lab08-b.md).
