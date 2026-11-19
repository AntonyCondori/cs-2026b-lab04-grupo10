# Lab 09 · Entrega y responsables

La entrega del equipo se documenta en el README, los archivos de evaluación, los PR y la etiqueta. Cada responsable deja sus evidencias junto a su cambio.

## Primero · Diego

1. Integrar los dos commits de subsanación de los Labs 07 y 08 antes del Lab 09. Antony y Bryan pueden cerrar las revisiones, los ADR y las etiquetas de esos laboratorios.
2. Publicar el aporte de Lab 09 en un PR con `v1`: esquema, caso verificado `HU-01`, proveedor grabado, configuración de promptfoo y generador integrado. Bryan revisa este PR.
3. Ejecutar `python -m pytest -v tests/test_generador_criterios.py`. Dejar en el PR los resultados de aceptación y rechazo y el enlace a esta tabla. A partir de ahí Antony y Bryan pueden continuar.

| Actividad | Responsable | Entrega que debe quedar en el repositorio | Evidencia para verificarla |
|---|---|---|---|
| E1 · Contrato y dataset | Diego entrega la base. Antony completa. | `prompts/criterios/esquema.json` y `casos.yaml`. Recuperar otras cinco historias reales del backlog, incluir dos casos de borde o no INVEST y al menos uno adversario. Se necesitan ocho casos como mínimo. | ID, tipo y resultado esperado de cada caso antes de evaluar. |
| E2 · Línea base | Diego prepara `v1`, proveedor y aserciones. Antony graba y mide. | `v1.txt`, `promptfooconfig.yaml`, `proveedor_grabado.py`, respuestas originales en `grabaciones/v1/` y reporte. | Resultado exportado de promptfoo y tasa en el README. |
| E3 · Iteraciones | Antony | `v2.txt` y `v3.txt` con grabaciones sobre el mismo dataset. Cada cambio responde a un fallo. | Tasas y fallos por versión, diff del prompt y explicación si queda por debajo de 85 %. |
| E4 · Docstrings | Bryan Daniel | `prompts/docstrings/` con esquema, ocho casos o más, aserciones, versiones y grabaciones. | Cotejo de parámetros reales y documentados, otras tres aserciones o más, y tasas por versión. |
| E5 · Seguridad | Antony coordina. Bryan aporta los casos de docstrings. | Completar `prompts/seguridad/red-team.md` con cinco casos o más, grabaciones y defensas. | Resultado antes y después por caso y versión. |
| E6 · Integración | Diego | `src/solicitudes/generador_criterios.py` y `tests/test_generador_criterios.py`. Cargar una versión y validar la respuesta con el esquema compartido. | Aceptación de una salida válida y rechazo de texto libre, JSON fuera del esquema e ID incorrecto. |
| E7 · CI y observaciones | Bryan Daniel configura CI. Ambos completan los registros. | `.github/workflows/prompts.yml` para ambas tareas. Completar `prompts/bitacora-ia.md` y registrar tres ejecuciones en cada uno de tres casos. | Workflow enlazado, cinco interacciones reales con una sugerencia rechazada y comparación de las nueve ejecuciones. |
| E8 · Revisión y entrega | Antony y Bryan Daniel | Antony abre el PR de una iteración de criterios. Bryan abre el de una versión de docstrings. Bryan integra la tabla, el gráfico y las lecciones en el README, etiqueta `v0.9-prompts` y sube el enlace. | Tres PR con versión de prompt y revisión de otro integrante, gráfico, etiqueta y enlace de entrega. |

Bryan revisa los PR de Diego y Antony. Antony revisa el de Bryan. En cada PR, indicar actividad, versión, archivos, comando de verificación y resultado.

## Ejecutar la base de criterios

Las plantillas usan `{{id}}` y `{{historia}}`. En `casos.yaml`, cada caso también fija `invest_esperado` como booleano. Por cada versión que figure en `promptfooconfig.yaml`, guardar una respuesta original por ID en `prompts/criterios/grabaciones/<versión>/<id>.txt`. Un archivo faltante es un error de ejecución. Agregar `v2` y `v3` a la configuración cuando tengan sus grabaciones.

```bash
cd prompts/criterios
npx --yes promptfoo@0.118.0 eval --no-cache -o resultados.json
```

El esquema, las aserciones y la lectura de grabaciones se comprobaron localmente con una respuesta de prueba temporal. Para medir el laboratorio con promptfoo, usar el dataset completo y las respuestas reales del asistente.

## Reproducir una respuesta desde Python

Cuando exista una grabación real, ejecutar desde la raíz con el ID y el texto exacto del dataset:

```python
from pathlib import Path

from src.solicitudes.generador_criterios import GeneradorCriterios, ProveedorCriteriosGrabado

version = "v3"
id_historia = "HU-01"
historia = (
    "Como vecino, quiero solicitar el recojo de mis residuos reciclables desde la aplicación "
    "ingresando mi dirección y el detalle de mis residuos, para que un reciclador pueda asignar "
    "mi solicitud a su ruta diaria."
)
archivo = Path("prompts/criterios/grabaciones") / version / f"{id_historia}.txt"
generador = GeneradorCriterios(ProveedorCriteriosGrabado(archivo), version)
print(generador.generar(id_historia, historia))
```
