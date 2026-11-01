## Lab08: aporte de Persona B para consolidar en bitacora-ia.md

Esta sección registra una interacción de trabajo con varias verificaciones. No se cuentan las verificaciones como cinco conversaciones distintas. Deben incorporarse las entradas reales de Persona A y Persona C hasta cumplir las cinco interacciones de la guía.

| Interacción | Herramienta | Solicitud | Propuesta y verificación | Decisión |
|---|---|---|---|---|
| B-01 | ChatGPT | Revisar guía, reparto, repositorio y continuar Persona B | Se eligió QA-04 y se comparó State, caché en memoria, unicidad transaccional y cola/outbox. Se ejecutó un prototipo con 100 envíos, 10 simultáneos y 10 acuses descartados; sin táctica: 99 duplicados; protegida: 0. La suite aprobó 53 casos. Se contrastó el issue #24 con R-06 y C4. | Preparar ADR-007 y un prototipo; mantener E3 pendiente de publicación y confirmación del grupo asignado. |

### Hipótesis descartada y evidencia

Se evaluó la hipótesis de que State bastaría para bloquear los duplicados. Se refutó al reconstruir dos objetos Solicitud con el mismo id=1: ambos terminaron COMPLETADO, sumaron 20 puntos entre sus atributos y se registraron 4 eventos. No existe un ledger productivo que permita afirmar dos abonos bancarios reales; la prueba demuestra repetición del procesamiento y de sus efectos simulados.

También se refutó la afirmación del issue #24 como fallo observado de saturación por mapas: no aporta pruebas de p95, HTTP 500 ni pérdida. El C4 contiene la dependencia, pero R-06 la excluye del alcance obligatorio. Se acepta la inconsistencia y el riesgo condicionado, no una saturación medida.

La guía pide un falso positivo de IA refutado. La hipótesis State es la hipótesis de análisis descartada en esta sesión; no debe atribuirse a una salida textual de otra herramienta. Si el docente exige una propuesta textual previa, conservar el prompt y la respuesta reales de una revisión adversaria y contrastarlos antes de dar ese requisito por cerrado.
