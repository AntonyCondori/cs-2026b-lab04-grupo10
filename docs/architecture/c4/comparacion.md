# Comparación de herramientas y vistas (E4 y E6) - EcoRecicla AQP

## E4. Vista dinámica de C4 frente a la secuencia UML (`SolicitarRecojo`)

La secuencia UML del Lab 05 muestra detalles que la vista dinámica omite: las clases internas (`SolicitudController`, `SolicitarRecojoService`, `Direccion`, `Solicitud`), el `loop` de validación de cada detalle, el `break` con `ErrorValidacion` (422), el `alt` de geocodificación fallida (400) y la notificación asíncrona. La vista dinámica solo muestra 4 pasos del camino exitoso entre contenedores y componentes (POST, geocodificación, guardado y respuesta 201), con su protocolo. La secuencia UML sirve a los developers que implementan el módulo; la vista dinámica sirve a arquitectos y al equipo técnico para entender quién colabora con quién sin leer el código.

## E6. Escritura a mano (`contexto-manual.puml`) frente a modelo exportado (Structurizr)

| Criterio | A mano (C4-PlantUML) | Modelo exportado (Structurizr DSL) |
|---|---|---|
| Tiempo invertido | Unos 5 min (estimado) para escribir y renderizar 1 diagrama de contexto | Unos 10 s (estimado) para validar y exportar las 5 vistas, más la instalación única del CLI |
| Errores encontrados | Ninguno de sintaxis; el diagrama se renderizó a la primera | `validate` sin errores. Al revisar la exportación, el contexto salió con etiquetas técnicas ("Llama al adaptador de MapasGeocodificacion", "Llama al puerto de Notificacion") que no cumplen la lista de revisión de E1 |
| Cambia el nombre de un contenedor | Hay que editar cada archivo `.puml` donde aparezca y es fácil olvidar alguno | Se cambia el nombre en una línea de `workspace.dsl` y se regeneran las 5 vistas con `export` |
| Coherencia entre vistas | Depende de la disciplina del equipo | Garantizada: todas las vistas salen del mismo modelo |
| Descripciones (`Rel`) | Se escriben una vez por diagrama | Se declaran una vez y se reutilizan |

**Conclusión:** para un solo diagrama de contexto, escribir a mano es rápido; con 5 vistas que comparten elementos, modelar con Structurizr evita incoherencias y ahorra retrabajo.

## Hallazgos de la exportación

- Mermaid y C4-PlantUML exportaron las 5 vistas (Contexto, Contenedores, Componentes, SolicitarRecojo, Despliegue).
- La exportación a C4-PlantUML no aplica el color gris de la etiqueta "Externo": en el PNG, el Servicio de mapas y WhatsApp salen con el mismo azul que un sistema propio. En el modelo la etiqueta existe, pero el exportador no la traduce al color.
- En la vista de despliegue, el nodo Nginx aparece sin flechas porque el modelo no define relaciones para él.
- En las vistas de Contenedores y Despliegue, las flechas entre contenedores heredan la etiqueta de la primera relación entre componentes (por ejemplo "Inicia sesión" o "Lee"), porque el modelo solo define relaciones a nivel de componente.