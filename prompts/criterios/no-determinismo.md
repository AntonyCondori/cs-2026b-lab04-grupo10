# E7 · Nueve ejecuciones del mismo prompt

Se ejecutó v3 tres veces sobre cada uno de HU-01, HU-04 y NI-01, siempre con el mismo mensaje y contexto, en sesiones independientes. No se reprodujeron grabaciones para generar esta comparación. El manifiesto registra los nueve IDs de sesión y hashes de entrada idénticos por caso.

| Caso | INVEST en r1/r2/r3 | Escenarios r1/r2/r3 | Preguntas r1/r2/r3 | Respuestas textualmente diferentes |
|---|---|---|---|---:|
| HU-01 | true / true / true | 3 / 3 / 3 | 0 / 0 / 0 | 3/3 |
| HU-04 | true / true / true | 3 / 3 / 3 | 0 / 0 / 0 | 3/3 |
| NI-01 | false / false / false | 0 / 0 / 0 | 1 / 1 / 1 | 3/3 |

## Análisis en cinco líneas

1. Las tres respuestas de cada caso fueron distintas en texto, aunque las entradas y el prompt eran iguales.
2. HU-01 mantuvo INVEST verdadero y tres escenarios; cambiaron títulos y formulaciones del registro y de los datos faltantes.
3. HU-04 mantuvo INVEST verdadero y tres escenarios de peso válido, peso negativo y repetición sin duplicados, con cambios de redacción.
4. NI-01 mantuvo INVEST falso, cero escenarios y una pregunta; varió cómo pedir la acción concreta y el resultado observable.
5. Las nueve salidas cumplieron esquema e INVEST esperado en Python; las grabaciones estabilizan la regresión, pero deben complementarse con nuevas ejecuciones del modelo.

Archivos: `grabaciones/no-determinismo/r1/`, `r2/`, `r3/`, `no-determinismo.json` y `manifiesto.json`. Esta muestra pequeña no estima la variabilidad de otras historias ni de otros modelos. La temperatura no se fijó: se usó la configuración disponible del asistente.
