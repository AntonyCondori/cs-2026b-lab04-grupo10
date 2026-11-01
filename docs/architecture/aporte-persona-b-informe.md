# Texto para incorporar al informe: Persona B

Estos apartados describen el prototipo ensayado y la revisión preparada. La evaluación cruzada no se considera cerrada hasta publicar la respuesta y la evaluación emitida con sus enlaces reales.

## Evaluación ATAM-lite recibida

Revisamos la evaluación del Grupo 01 registrada en el issue #24 y contrastamos sus observaciones con los drivers, el modelo C4 y el código. Aceptamos el riesgo de que una base de datos compartida facilite accesos entre módulos si no existen controles. En cambio, la supuesta saturación por mapas no se tomó como un fallo demostrado: no se adjuntaron mediciones y el alcance definido en R-06 utiliza mapas como enlace externo. Esta diferencia permitió detectar una contradicción entre los drivers y el C4 que debe corregirse antes de adoptar una solución.

Evidencia: captura del issue #24, tabla de respuestas de atam-lite.md y, cuando se publique, enlace del comentario de respuesta. No afirmar que ya fue respondido.

## Iteración 2 de ADD: confirmaciones sin duplicados

Seleccionamos QA-04, que exige que los reenvíos de una confirmación no repitan el recojo ni el abono. Comparamos confiar en State, guardar claves en memoria, utilizar unicidad transaccional y agregar una cola. Elegimos un registro persistente con una clave de idempotencia y una restricción por solicitud. El resultado se conserva para responder a las repeticiones y la confirmación se registra en la misma transacción que el abono.

Construimos un prototipo con SQLite para verificar la táctica sin cambiar todavía el servicio del proyecto. Se enviaron 100 confirmaciones con el mismo identificador, 10 de ellas concurrentes, y se descartaron 10 respuestas después del registro para representar pérdidas de acuse. Sin la táctica se obtuvieron 100 abonos y 99 duplicados; con la táctica se obtuvo un abono y ningún duplicado. También comprobamos conflictos de datos, recuperación al recrear el registro y reversión de las escrituras ante un fallo intermedio.

La suite de revisión aprobó 53 casos sobre la base indicada en los archivos de evidencia. Este resultado respalda QA-04 dentro del prototipo; no demuestra todavía el comportamiento de PostgreSQL ni de un servicio desplegado. El costo aceptado es más almacenamiento y coordinación de las escrituras a cambio de no duplicar los efectos ensayados.

Evidencia: captura de python -m fitness.disponibilidad y de python -m pytest -q. Insertar la tabla de resultados de add/iteracion-2.md.

## ADR-007 y riesgos

Documentamos la alternativa elegida, las descartadas, los resultados y los límites en el ADR-007. La matriz propone valoraciones de probabilidad e impacto de 1 a 5 y considera críticos los riesgos con puntuación igual o superior a 15. Se identificaron como críticos la duplicación de abonos y la exposición de datos entre distritos. El primero cuenta con evidencia de mitigación en el prototipo; el segundo corresponde a la iteración 3. Ambos requieren confirmar la solución al integrar el sistema.

Evidencia: captura de ADR-007 y figura docs/architecture/riesgos/matriz.png. Título: Matriz propuesta de probabilidad e impacto de EcoRecicla AQP.

## Bitácora

Se preparó el aporte de Persona B para consolidarlo en la bitácora compartida. Se registró la hipótesis descartada de que State bastaría para bloquear todos los reenvíos: al reconstruir dos objetos con el mismo identificador, ambos pudieron procesarse. La bitácora final debe reunir las interacciones reales de los tres integrantes y conservar las evidencias de las propuestas rechazadas.
