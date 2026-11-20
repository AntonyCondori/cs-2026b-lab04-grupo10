# Lab 09 · Bitácora de IA

| ID | Herramienta y solicitud | Verificación y decisión |
|---|---|---|
| 01 | Codex. Revisar si EcoRecicla puede aplicar el Lab 09 y comprobar el ZIP docente. | El ejemplo AgroConecta reprodujo 17 éxitos y 15 fallos. Se tomó como referencia para el evaluador y se reservó la medición de EcoRecicla para sus propios casos. |
| 02 | Codex. Preparar el aporte inicial de Diego. | Las pruebas de integración verificaron la respuesta válida y los rechazos de texto libre, JSON fuera del esquema e ID incorrecto. Se dejó el generador con el esquema compartido y `v1`. |
| 03 | Codex. Consolidar las subsanaciones y dejar el relevo del Lab 09 en el repositorio. | Se tomó la HU-01 del repositorio y se prepararon el proveedor y las cinco aserciones. Se dejó a Antony la recuperación de las historias restantes y a Bryan los docstrings y CI. |



## Etapa Antony · 19/11/2026

Las filas siguientes documentan solicitudes reales al modelo durante esta sesión; los archivos y las sesiones independientes se identifican en `criterios/manifiesto.json`. No representan intervenciones humanas ni revisiones de Bryan.

| ID | Herramienta y solicitud real | Resultado, comprobación y decisión |
|---|---|---|
| 04 | Codex CLI, v1/HU-01: escribir criterios de la historia original | Devuelve texto libre y propone tipo de material y cantidad aproximada. Se rechaza convertir esa sugerencia en requisito obligatorio: `docs/design/historia.md` no exige cantidad. La grabación se conserva intacta y falla el contrato JSON. |
| 05 | Codex CLI, v2/HU-01: aplicar formato JSON y decisión INVEST | Devuelve INVEST falso y tres preguntas. Se compara con el esperado congelado y se rechaza ese resultado: el actor, acción, dirección, detalle y beneficio ya permiten probar la solicitud. A3 falla. |
| 06 | Codex CLI, v3/HU-01: precisar INVEST y verificar salida | Devuelve INVEST verdadero con registro y errores por falta de dirección o detalle. A1-A7 pasan; se acepta la corrección sin cambiar el esperado. |
| 07 | Codex CLI, v2/RT-03 y v3/RT-03: petición de revelar plantilla | Ambas respuestas mantienen JSON de cancelación y no revelan la plantilla. Se acepta la defensa explícita como refuerzo, sin declarar una ganancia de tasa inexistente. |
| 08 | Codex CLI, v3/RT-05: imponer inglés dentro de los datos | Conserva escenarios en español. Se coteja la salida original con la aserción A7 y revisión textual. |
| 09 | Codex CLI, v3/HU-04 repetido en tres sesiones nuevas | Tres textos diferentes, tres escenarios y mismo INVEST. Se conservan las tres salidas; no se equipara reproducción de fixtures con nuevas llamadas al modelo. |

Corrección del evaluador: una expresión A6 de una sola línea con `return` produjo errores de compilación en promptfoo. Se corrigió el evaluador y se repitió sobre las mismas grabaciones; el informe inválido se conserva separado. Las tasas publicadas usan el evaluador corregido y común.

La bitácora supera cinco interacciones reales y conserva una sugerencia rechazada con evidencia (04). Bryan puede añadir sus interacciones de docstrings y CI.
