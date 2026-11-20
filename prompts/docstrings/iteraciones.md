# Lab 09 · Iteraciones de docstrings

La captura se hizo con Qwen 2.5 3B en Ollama, CPU y temperatura 0. Los hashes de cada entrada y respuesta están en los metadatos de las grabaciones. El diagnóstico local cargó la respuesta con Python, validó el esquema con jsonschema y ejecutó las expresiones de la configuración con Node.js. Promptfoo devolvió EACCES en la instalación, por lo que las tasas oficiales y la comprobación de umbral se mantienen pendientes.

| Versión | Hallazgo observado | Cambio |
|---|---|---|
| v1 | DOC-01 devolvió Markdown, claves distintas, una nota y una excepción hipotética. B1–B4 fallaron en el diagnóstico. | v2 enumeró las claves, prohibió Markdown y notas, y fijó los tipos esperados. |
| v2 | DOC-01, DOC-04 y DOC-05 devolvieron el retorno sin la estructura exigida. Fallaron B1 y B3. | v3 mostró el objeto completo como ejemplo, exigió un objeto de retorno incluso para tipos simples y añadió defensas frente a instrucciones incrustadas. |

## Fallos que persisten en v3

- DOC-01 y DOC-06 generaron JSON inválido por errores de cierre o delimitadores. La plantilla ayudó con la estructura del retorno, pero el modelo aún genera texto sin un decodificador JSON restringido.
- DOC-02 y DOC-07 devolvieron una lista con una cadena vacía en lugar de una lista vacía para excepciones. Una causa posible es la interpretación de un marcador de relleno como elemento de la lista.
- DOC-08 falló el cotejo de parámetros y excepciones. El parámetro variádico y las excepciones hipotéticas de la llamada delegada requieren una distinción más explícita entre la firma y el comportamiento inferido.

Las grabaciones se conservan completas, incluidos estos fallos. El workflow aplica un mínimo de 85 % a la v3 de cada tarea.