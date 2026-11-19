# Lab 09 · Integración y pendientes del Grupo 10

## E6 · Generador de criterios

`src/solicitudes/generador_criterios.py` carga la plantilla de la versión solicitada y valida la respuesta con el JSON Schema de la Tarea A. También verifica que `historia_id` coincida con la historia solicitada. Los proveedores de generación implementan `completar(prompt)`. El proveedor grabado permite ejecutar la integración sin API y reutilizar las grabaciones de los evals.

La generación de criterios es una herramienta para el equipo de desarrollo. El puerto de clasificación del Lab 07 sigue atendiendo el procesamiento de recojos.

### Pruebas

Desde la raíz del repositorio:

```bash
python -m pip install pytest jsonschema
python -m pytest -q tests/test_generador_criterios.py
python -m pytest -q
```

Las pruebas usan ejemplos locales para verificar la carga de versión, la interpolación, una respuesta válida y tres rechazos: texto libre, JSON fuera del esquema e ID incorrecto. Las tasas del laboratorio se obtienen con las ejecuciones de promptfoo sobre las grabaciones del equipo.

### Conectar los artefactos de la Tarea A

Esta rama incluye el contrato inicial `prompts/criterios/esquema.json` y el prompt de línea base `v1.txt`. Colocar las siguientes plantillas en esa misma carpeta y las grabaciones en `prompts/criterios/grabaciones/<versión>/<id>.txt`. Las plantillas usan `{{id}}` y `{{historia}}`, y el contrato incluye `historia_id`. Una vez que el equipo grabe las respuestas, se puede reproducir un caso así. Sustituir la versión, el ID y el texto por los registrados en el dataset.

```python
from pathlib import Path

from src.solicitudes.generador_criterios import GeneradorCriterios, ProveedorCriteriosGrabado

version = "v3"
id_historia = "HU-01"
historia = "Como vecino, quiero solicitar el recojo de mis residuos reciclables."
archivo = Path("prompts/criterios/grabaciones") / version / f"{id_historia}.txt"
generador = GeneradorCriterios(ProveedorCriteriosGrabado(archivo), version)
criterios = generador.generar(id_historia, historia)
print(criterios)
```

## Relevo de tareas

| Responsable | Trabajo pendiente | Evidencias para el informe |
|---|---|---|
| Antony | E1–E3 de la Tarea A. Recuperar las seis historias del backlog, fijar el contrato y los casos, y evaluar la línea base y las dos iteraciones. Coordinar E5 una vez disponibles las versiones finales de ambas tareas. | Tabla de tasas, fallos por caso, cambios de prompt y comparación antes/después en `prompts/seguridad/red-team.md`. |
| Bryan Daniel | E4 de docstrings, E7 de CI y consolidación E8. Configurar CI para ambas tareas y completar el README y la etiqueta cuando estén los resultados. | Contrato de docstrings, cotejo de parámetros contra sus firmas reales, resultados del workflow, gráfico y enlace a `v0.9-prompts`. |
| Diego | E6, esquema inicial y prompt `v1` preparados en esta rama. | Pruebas de integración y explicación del puerto de generación, de la validación y del rechazo de respuestas. |

Para E7, registrar tres ejecuciones por cada uno de los tres casos elegidos y consolidar al menos cinco interacciones en la bitácora, con una sugerencia rechazada y su evidencia. Para E8, cada integrante debe presentar una versión de prompt en un PR que revise otro compañero. Esta rama incluye `v1`; su tasa se mide cuando estén completas las grabaciones de la línea base.
