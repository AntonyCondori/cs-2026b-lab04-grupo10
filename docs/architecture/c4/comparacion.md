# Comparación de herramientas y vistas (E4 y E6) - EcoRecicla AQP

## E4. Vista dinámica de C4 frente a la secuencia UML (`SolicitarRecojo`)

La secuencia UML del Lab 05 muestra detalles que la vista dinámica omite: las clases internas (`SolicitudController`, `SolicitarRecojoService`, `Direccion`, `Solicitud`), el `loop` de validación de cada detalle, el `break` con `ErrorValidacion` (422), el `alt` de geocodificación fallida (400) y la notificación asíncrona. La vista dinámica solo muestra 4 pasos del camino exitoso entre contenedores y componentes (POST, geocodificación, guardado y respuesta 201), con su protocolo. La secuencia UML sirve a los developers que implementan el módulo; la vista dinámica sirve a arquitectos y al equipo técnico para entender quién colabora con quién sin leer el código.

## E6. Escritura a mano (`contexto-manual.puml`) frente a modelo exportado (Structurizr)

| Criterio | A mano (C4-PlantUML) | Modelo exportado (Structurizr DSL) |
|---|---|---|
| Tiempo invertido | [COMPLETAR: minutos que tardó Daniel] | [COMPLETAR: minutos de validar + exportar + renderizar] |
| Errores encontrados | [COMPLETAR: ej. `Rel` con identificador mal escrito, sin leyenda, etc.] | [COMPLETAR: ej. identificadores inexistentes que `validate` detectó] |
| Cambia el nombre de un contenedor | Hay que editar cada archivo `.puml` donde aparezca y es fácil olvidar alguno | Se cambia el nombre en una línea de `workspace.dsl` y se regeneran las 5 vistas con `export` |
| Coherencia entre vistas | Depende de la disciplina del equipo | Garantizada: todas las vistas salen del mismo modelo |
| Descripciones (`Rel`) | Se escriben una vez por diagrama | Se declaran una vez y se reutilizan |

**Conclusión:** para un solo diagrama de contexto, escribir a mano es rápido; con 5 vistas que comparten elementos, modelar con Structurizr evita incoherencias y ahorra retrabajo.

## Hallazgos de la exportación

- Mermaid y C4-PlantUML exportaron las 5 vistas (Contexto, Contenedores, Componentes, SolicitarRecojo, Despliegue).
- La exportación a C4-PlantUML no aplica el color gris de la etiqueta "Externo"; los sistemas externos salen con el azul de sistema. [VERIFICAR en tu render]
- En la vista de despliegue, el nodo Nginx aparece sin flechas porque el modelo no define relaciones para él.
