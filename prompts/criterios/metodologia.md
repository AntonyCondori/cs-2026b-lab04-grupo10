# Método de captura y evaluación · Antony

Fecha de ejecución local: 19/11/2026 (America/Lima). No se retrofechan las evidencias a la fecha de entrega docente.

## Procedencia y alcance

Se conserva la base integrada por Diego en PR #27 (`88b7857`). La HU-01 ya existía; Antony autorizó redactar otras cinco historias durante esta sesión. `docs/design/backlog-lab09.md` relaciona HU-02 a HU-06 con los RF existentes. Son incorporaciones nuevas, no historias recuperadas de un backlog antiguo; esta adaptación de E1 debe validarse por el equipo/docente.

Antes de ejecutar v1, se versionaron nueve entradas y sus esperados en el commit E1. El dataset permanece idéntico para v1, v2 y v3. Hay seis historias funcionales, dos no INVEST y un adversario. Los cinco ataques adicionales conservan la misma historia funcional antes y después.

## Generación real

Cada uno de los 46 archivos de `grabaciones/` proviene de una nueva sesión de Codex CLI, efímera, de solo lectura y con autenticación de ChatGPT ya existente. Se usó la configuración de modelo disponible, sin imponer un modelo alternativo, JSON Schema de salida, respuestas esperadas ni temperatura. El modelo informado en la comprobación del entorno fue gpt-6.1-sol, CLI 0.169.0-alpha.11.1. Esta interfaz añade instrucciones del agente: los resultados describen esta configuración, no una API de modelo sin contexto ni otros modelos.

Se mantuvo el mismo directorio de contexto durante todas las capturas. Su instrucción fija solo pide responder sin usar herramientas ni leer archivos y no establece formato. Todas las trazas comprobaron ausencia de llamadas a herramientas. `contexto-captura.txt` conserva esa instrucción y `capturar_codex.py` el arnés que invoca la CLI. `entradas/` contiene los mensajes exactos, sin los esperados del dataset. No se compartió la rúbrica con las sesiones evaluadas.

La CLI escribió directamente la última respuesta con `--output-last-message`. Las grabaciones no se corrigieron, reformatearon ni reemplazaron. `manifiesto.json` conserva SHA-256 de entrada y salida, ID de sesión y tiempos UTC; las 46 sesiones son diferentes. `.gitattributes` evita conversión de saltos de línea al clonar. Se archivaron los registros técnicos de captura fuera del repositorio; el manifiesto contiene los metadatos necesarios sin rutas privadas.

## Evaluación y límites

Se utilizó promptfoo 0.118.0, como la base de Diego. Cada caso aprueba solo si pasa todas las aserciones: A1 contrato JSON; A2 ID; A3 INVEST esperado; A4 escenarios o preguntas; A5 ausencia de tecnologías en escenarios; A6 ausencia de marcadores de ataque o etiquetas de plantilla; A7 idioma español mediante heurística. A5 se limita a escenarios para que mencionar PostgreSQL en una pregunta de aclaración no genere un falso positivo. A6 y A7 son controles limitados: no demuestran por sí solos ausencia de toda fuga ni detectan cualquier idioma. Se complementaron con inspección de las diez respuestas defensivas.

La primera ejecución de v2 tras añadir A6 produjo falsos fallos por un `return` de una sola línea: promptfoo lo trató como una expresión e intentó compilar `return return ...`. Se conservó `resultados-v2-evaluador-invalido.json`; se corrigió la expresión y se evaluaron de nuevo las mismas grabaciones. No se modificaron respuestas ni esperados para hacerlas aprobar. `resultados-v1.json` conserva además la ejecución inicial con las cinco aserciones originales de Diego. `resultados.json` es la comparación definitiva con las mismas siete aserciones para todas las versiones.

Los resultados son 0/9 (v1), 8/9 (v2), 9/9 (v3). La tasa se calcula por caso, no por aserción: aprobar 63/63 aserciones en v3 equivale aquí a 9/9 casos. El 100 % solo describe estas grabaciones y no garantiza futuras respuestas ni cobertura exhaustiva. Las repeticiones se validan también mediante el generador Python de E6.

## Reproducción sin llamar a modelos

Desde `prompts/criterios`:

```bash
npx --yes promptfoo@0.118.0 eval --no-cache --no-table -o resultados-reproducidos.json
npx --yes promptfoo@0.118.0 eval -c promptfoo-seguridad.yaml --no-cache --no-table -o seguridad-reproducida.json
```

La comparación histórica completa termina con código 1 porque incluye fallos esperados de v1 y v2. Para comprobar solo el umbral de la entrega final:

```bash
npx --yes promptfoo@0.118.0 eval -c config-v3.yaml --no-cache --no-table -o final-reproducido.json
```

Desde la raíz, con pytest y jsonschema instalados:

```bash
python -m pytest -q tests/test_generador_criterios.py tests/test_lab09_grabaciones.py
```

E4 (docstrings), CI de ambas tareas y consolidación/tag de E8 pertenecen a Bryan. La revisión humana del PR queda pendiente; esta captura no sustituye su aprobación. No se afirma que se haya publicado la etiqueta ni completado el workflow de prompts de ambas tareas.
