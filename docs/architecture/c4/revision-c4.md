# Revisión del modelo C4 — EcoRecicla AQP

## Alcance

Se realizó una revisión inicial del modelo, comparando workspace.dsl
con inventario.md, el ADR-001 y paquetes.puml del Laboratorio 05.

Esta revisión debe contrastarse con la lista oficial del docente
antes de considerar terminado el ejercicio.

## Resultados de la revisión

| Criterio | Resultado | Evidencia u observación |
|---|---|---|
| Personas identificadas | Cumple | Se incluyen Vecino, Reciclador y Municipalidad. |
| Sistema principal identificado | Cumple | EcoRecicla AQP aparece como sistema de software. |
| Sistemas externos diferenciados | Cumple | Mapas y WhatsApp tienen la etiqueta Externo. |
| Contenedores con tecnologías | Cumple | Se declaran las dos aplicaciones, API, base de datos y optimizador, cada uno con tecnología. |
| Componentes coherentes con el Lab 05 | Cumple | Reportes, Rutas, Solicitudes, Puntos y Canjes, e Identidad y Distritos coinciden con paquetes.puml. |
| Dependencias entre componentes sin ciclos | Cumple | Las dependencias declaradas no forman ciclos; Identidad no depende de los demás módulos. |
| Inventario coherente con el modelo | Cumple | El inventario incluye los cinco componentes actuales. |
| Contexto comprensible para público no técnico | Ajustado en el modelo; pendiente de comprobar en la exportación | Se reemplazaron los nombres de adaptadores y puertos por descripciones de su propósito. |
| Vista dinámica con cuatro pasos | Cumple en el código | Incluye registro, geocodificación, almacenamiento y respuesta de confirmación. |
| Despliegue en un servidor | Cumple en el código | API, optimizador y PostgreSQL se ubican en un servidor de producción. |
| Validación y revisión de imágenes después de los ajustes | Pendiente | Se deben regenerar y comprobar las vistas afectadas. |

## Hallazgo principal

La exportación de contexto contiene las expresiones
“Llama al adaptador de MapasGeocodificacion” y
“Llama al puerto de Notificacion”.

Estas expresiones describen detalles internos y dificultan
la comprensión para una persona no técnica.

Se propone reemplazarlas por:

- Consulta la ubicación de la dirección.
- Envía notificaciones del recojo.

Estado: descripciones corregidas en workspace.dsl.
Queda pendiente validar el modelo y regenerar las vistas.

## Pendientes de cierre

- Contrastar los criterios con la lista oficial del docente.
- Corregir las descripciones técnicas identificadas.
- Ejecutar nuevamente la validación del modelo.
- Regenerar las exportaciones y las imágenes afectadas.
- Comprobar que las vistas sean legibles y coherentes.