# E3 · Iteraciones justificadas

Responsable: Antony Condori. La base es `v1.txt` de Diego; no se modifica.

| Versión | Casos aprobados | Aserciones aprobadas | Fallo y cambio |
|---|---:|---:|---|
| v1 | 0/9 (0 %) | 9/63 | Las respuestas no son JSON del contrato. A1-A5 y A7 fallan; A6 por sí sola no valida el formato. |
| v2 | 8/9 (88,89 %) | 62/63 | Se explicitan rol, contexto, tarea, restricciones, ejemplo, formato y datos; few-shot funcional. Falla A3 en HU-01: se exige demasiado detalle para considerarla INVEST. |
| v3 | 9/9 (100 %) | 63/63 | Se precisa el criterio de INVEST: actor, acción, datos y beneficio verificable bastan para HU-01. Se añade ejemplo no INVEST, separación de datos no confiables, defensa de contrato e idioma y patrón Cognitive Verifier. |

Los nueve casos y las siete aserciones de la comparación definitiva son idénticos en todas las versiones. Ningún caso aprobado retrocede: v1→v2 gana ocho; v2→v3 gana HU-01 y mantiene los otros ocho. El few-shot muestra ejemplos; la comprobación de salida exige un resultado JSON, sin añadir una explicación del razonamiento.

La defensa de v3 explicita límites que v2 no documentaba. Los cinco ataques ya pasaban en v2 y siguieron pasando en v3: se registra un refuerzo preventivo, no una mejora medida de 0 a 100 %. La justificación experimental principal de v3 es el fallo A3/HU-01.

Evidencia: `resultados.json`, `resumen.json`, `grabaciones/`, `entradas/` y `manifiesto.json`. El reporte de A6 con sintaxis inválida se conserva por separado y no se usa para calcular la tabla.
