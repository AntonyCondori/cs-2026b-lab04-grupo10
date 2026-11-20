# EcoRecicla AQP — Laboratorio 04: Fundamentos de arquitectura de software
Construcción de Software · EPIS-UNSA · 2026-B · Grupo 10

## Integrantes
| Nombre | Rol en el laboratorio |
|--------|-----------------------|
| Condori Caira Antony Beltran | Redactor de drivers y de ADR-001; responsable del README |
| Sencia Ale Bryan Daniel | Matriz de decisión y diagramador (Mermaid y PlantUML) |
| Yauli Merma Diego Raul | Redactor de ADR-002 y ADR-003; vista de despliegue y verificador de IA |

## Caso
EcoRecicla AQP es una plataforma para el recojo de residuos reciclables con recicladores formalizados en distritos de Arequipa. Los vecinos solicitan recojos y canjean puntos, los recicladores consultan su ruta del día y registran el peso recogido, y la municipalidad consulta reportes de toneladas recicladas. El MVP debe estar en producción en 1 mes con 3 desarrolladores (Node.js y PostgreSQL) y presupuesto bajo. El atributo de calidad crítico es la **modificabilidad**: incorporar un nuevo distrito o una nueva regla de puntos en ≤ 2 días-persona, sin modificar los demás módulos.

## Arquitectura elegida
```mermaid
flowchart TB
    VE["Vecino"]
    RE["Reciclador"]
    MU["Municipalidad"]
    subgraph APP["EcoRecicla AQP — Monolito modular (un solo despliegue)"]
        API["Capa de presentación: API REST + PWA"]
        M1["Identidad<br/>y distritos"]
        M2["Solicitudes<br/>de recojo"]
        M3["Rutas<br/>del día"]
        M4["Puntos<br/>y canjes"]
        M5["Reportes"]
        INF["Capa de infraestructura: repositorios y adaptadores externos"]
    end
    DB[("PostgreSQL<br/>(un esquema por módulo)")]
    MAP["Servicio de mapas<br/>y geocodificación"]
    VE & RE & MU --> API
    API --> M1 & M2 & M3 & M4 & M5
    M1 & M2 & M3 & M4 & M5 --> INF
    INF --> DB
    INF --> MAP
    classDef mod fill:#E8F5E9,stroke:#2E7D32,color:#000
    classDef ext fill:#F2F2F2,stroke:#7F7F7F,color:#000,stroke-dasharray: 4 3
    classDef usr fill:#FDEDEC,stroke:#C8310E,color:#000
    class M1,M2,M3,M4,M5 mod
    class MAP ext
    class VE,RE,MU usr
```

## Decisiones arquitectónicas
- [ADR-001: Estilo arquitectónico](docs/architecture/adr/001-estilo-arquitectonico.md)
- [ADR-002: Base de datos](docs/architecture/adr/002-base-de-datos.md)
- [ADR-003: PWA para el reciclador](docs/architecture/adr/003-pwa-reciclador.md)

## Reflexión sobre el uso de la IA (5–8 líneas)
Claude nos ayudó a estructurar los entregables, a redactar los borradores de drivers, matriz de decisión, ADR y README, y a repartir el trabajo entre los tres. Sus borradores incluyeron supuestos que no le habíamos dado (conectividad intermitente de los recicladores, aplicación de la Ley 29733 y uso de un servicio de mapas), que documentamos como supuestos S-01 a S-03 en `drivers.md`. Recalculamos los totales de la matriz con un script y comprobamos que la segunda mejor alternativa es el monolito en capas, no microservicios como en el ejemplo de la guía, por lo que la alternativa descartada que diagramamos es capas. La crítica adversarial señaló riesgos reales del monolito modular (erosión de límites, punto único de falla, duplicados por la sincronización sin conexión) y los incorporamos como mitigaciones en los ADR. Aprendimos que la IA propone, pero cada supuesto y cada cálculo debe contrastarse con nuestras restricciones: plazo de 1 mes, 3 desarrolladores y presupuesto bajo. El detalle está en la [bitácora de uso de IA](docs/architecture/bitacora-ia.md).


## Vista de despliegue (E6)

[Diagrama y reproducción](docs/architecture/diagramas/README.md). Se incluye una vista alternativa PlantUML porque no se pudo instalar Graphviz; el PNG adjunto se renderizó localmente con Pillow. El script también admite Python Diagrams, pendiente de ejecución con sus dependencias instaladas.

## Diseño UML (Lab 05)

Diseño detallado del módulo **Solicitudes de recojo** de EcoRecicla AQP (HU-01: *Solicitar el recojo de residuos reciclables*), coherente con el ADR-001 (monolito modular, puertos y adaptadores). Diagramas escritos como código (PlantUML y Mermaid).

### Máquina de estados de `Solicitud` (Mermaid)

```mermaid
stateDiagram-v2
    direction TB
    [*] --> PENDIENTE : marcarPendiente() [dirección geocodificada]
    [*] --> RECHAZADA : rechazar(motivo) [dirección inválida o mapas sin respuesta]
    PENDIENTE --> ASIGNADA : asignar(recicladorId) [reciclador disponible]
    ASIGNADA --> RECOGIDA : registrarRecojo() [residuos entregados]
    RECOGIDA --> PESADA : registrarPesaje(pesoKg) [pesoKg > 0]
    PESADA --> PUNTOS_ACREDITADOS : acreditarPuntos(puntos) [acreditación confirmada]
    PUNTOS_ACREDITADOS --> [*]
    RECHAZADA --> [*]
```

### Entregables

| Código | Entregable | Archivo | Imagen |
|---|---|---|---|
| E1 | Historia de usuario y diagrama de clases | [historia.md](docs/design/historia.md), [clases.puml](docs/design/clases.puml) | [E1_clases-solicitudes.png](docs/design/img/E1_clases-solicitudes.png) |
| E2 | Diagrama de secuencia | [secuencia-solicitar-recojo.puml](docs/design/secuencia-solicitar-recojo.puml) | [E2_secuencia-solicitar-recojo.png](docs/design/img/E2_secuencia-solicitar-recojo.png) |
| E3 | Máquina de estados | [estados-solicitud.mmd](docs/design/estados-solicitud.mmd) | [E3_estados-solicitud.png](docs/design/img/E3_estados-solicitud.png) |
| E4 | Diagrama de actividades | [actividades-ruta-diaria.puml](docs/design/actividades-ruta-diaria.puml) | [E4_actividades-ruta-diaria.png](docs/design/img/E4_actividades-ruta-diaria.png) |
| E5 | Diagrama de paquetes | [paquetes.puml](docs/design/paquetes.puml) | [E5_paquetes.png](docs/design/img/E5_paquetes.png) |
| E6 | Round-trip (código, ingeniería inversa, diferencias) | [src/solicitudes/](src/solicitudes/), [round-trip.md](docs/design/round-trip.md) | [classes_solicitudes.png](docs/design/img/classes_solicitudes.png) |
| E7 | Consistencia C1-C5 y bitácora de IA | [consistencia.md](docs/design/consistencia.md), [bitacora-ia.md](docs/design/bitacora-ia.md) | - |

### Reglas de consistencia verificadas

C1 (mensajes y operaciones), C2 (transiciones y operaciones), C3 (multiplicidades), C4 (paquetes sin ciclos, coherentes con el ADR-001) y C5 (nombres del dominio). Los hallazgos y falsos positivos de la revisión con IA están en [consistencia.md](docs/design/consistencia.md).

Etiqueta de entrega: `v0.5-diseno`.

## Modelo C4 — Laboratorio 06

Documentamos la arquitectura de EcoRecicla AQP mediante cinco vistas:
contexto, contenedores, componentes, dinámica y despliegue.

### Diagrama de contexto

![Contexto de EcoRecicla AQP](docs/architecture/c4/img/structurizr-Contexto.png)

La imagen corresponde a la exportación previa del equipo.
Las descripciones corregidas ya están en el modelo y las
exportaciones de texto; falta actualizar el PNG.

### Documentación

- [Modelo Structurizr DSL](docs/architecture/c4/workspace.dsl)
- [Inventario de elementos](docs/architecture/c4/inventario.md)
- [Revisión inicial del modelo](docs/architecture/c4/revision-c4.md)
- [Explicación no técnica](docs/architecture/c4/explicacion.md)
- [Bitácora de IA](docs/architecture/c4/bitacora-ia.md)
- [Comparación de herramientas](docs/architecture/c4/comparacion.md)

### Vistas

- [Contexto](docs/architecture/c4/img/structurizr-Contexto.png)
- [Contenedores](docs/architecture/c4/img/structurizr-Contenedores.png)
- [Componentes](docs/architecture/c4/img/structurizr-Componentes.png)
- [Dinámica: solicitar recojo](docs/architecture/c4/img/structurizr-SolicitarRecojo.png)
- [Despliegue](docs/architecture/c4/img/structurizr-Despliegue.png)

### Estado de entrega

Pendiente: contrastar la lista oficial de revisión, actualizar las
imágenes afectadas, registrar la revisión cruzada de otro grupo
y crear la etiqueta v0.6-c4 sobre la versión final.

### Revisión cruzada

Revisamos la documentación C4 del Grupo 01 — CitaSalud Arequipa
y publicamos nuestras observaciones y sugerencias.

- [Issue de revisión cruzada](https://github.com/Diego-Schreiber/cs-2026b-lab04-grupo01/issues/2)

## Patrones de diseño (Lab 07)

Separamos el cálculo de puntos y la clasificación de residuos mediante
interfaces y composición. La IA y los servicios externos se simulan
durante las pruebas.

### Olores, patrones y pruebas

| Olor o necesidad | Patrón | Prueba |
|---|---|---|
| Reglas de puntos acopladas al servicio | Strategy | test_open_closed_nuevo_material_sin_modificar_el_servicio |
| Incorporar nuevas calculadoras | Fábrica por registro | test_open_closed_nuevo_material_sin_modificar_el_servicio |
| Adaptar la interfaz del simulador | Adapter | test_clasificacion_valida |
| Adaptar el SDK previo de WhatsApp | Adapter | test_observer_whatsapp_recibe_el_mensaje_correcto |
| Cambiar el proveedor de IA | Strategy | test_strategy_permite_otro_proveedor |
| Evitar llamadas repetidas | Decorator | test_cache_evitar_llamadas_repetidas |
| Reintentar tiempos de espera del proveedor | Decorator | test_agotar_reintentos_cancela_sin_abonar_ni_notificar |
| Separar las validaciones de salida | Chain of Responsibility | test_guardrails_bloquean_salidas_invalidas |
| Recorrer el ciclo completo del Lab 05 | State | test_flujo_del_lab05_llega_a_puntos_acreditados |

### Métricas

| Indicador (Radon 6.0.1) | Línea base | `main` revisada (`8e26afd`) | Subsanación |
|---|---:|---:|---:|
| Complejidad de `procesar_recojo` | C (14) | A (4) | A (2) |
| Complejidad del constructor | A (3) | B (6) | B (6) |
| SLOC de `servicio.py` | 54 | 45 | 45 |

Se miden los mismos métodos del servicio en los tres puntos. El código de reintentos pasó al proveedor de IA. Las SLOC de `servicio.py` miden el archivo en el que vive el servicio.

### Documentación

- [ADR-005](docs/architecture/adr/005-patrones-diseno.md)
- [Métricas y trade-off](docs/design/patrones/metricas.md)
- [Bitácora de IA](docs/design/patrones/bitacora-ia.md)
- [Strategy](docs/design/patrones/strategy.puml)
- [Adapter](docs/design/patrones/adapter.puml)
- [Fábrica por registro](docs/design/patrones/factory.puml)
- [Decorator](docs/design/patrones/decorator.puml)
- [Chain of Responsibility](docs/design/patrones/chain.puml)
- [State del Lab 05](docs/design/patrones/state.puml)
- [Diagrama de clases](docs/design/clases.puml)

### Ejecución de pruebas

Con el entorno virtual activado:

```bash
python -m pip install pytest jsonschema
python -m pytest -v
```

`tests/test_comportamiento.py` cubre ocho casos ejecutados contra ambas versiones (16 ejecuciones). `tests/test_ciclo_recojo.py` comprueba el flujo de la HU-01 y el rechazo por ubicación. Para cerrar la entrega, registrar aquí el enlace de revisión cruzada y publicar `v0.7-patrones` sobre el commit revisado.


## Diseño de la arquitectura (Lab 08)

![fitness-functions](https://github.com/AntonyCondori/cs-2026b-lab04-grupo10/actions/workflows/fitness.yml/badge.svg)

Diseñamos la arquitectura de EcoRecicla AQP para crecer de 3 a 12 distritos, con ADD en tres iteraciones, evaluación ATAM-lite cruzada y fitness functions en integración continua.

### Árbol de utilidad

![Árbol de utilidad](docs/architecture/utilidad/arbol.png)

Escenarios y calificaciones: [escenarios.md](docs/architecture/utilidad/escenarios.md).

### Iteraciones de ADD

| Iteración | Escenario | Táctica | Evidencia | ¿Cumple? |
|---|---|---|---|---|
| 1 | QA-01 Regla de puntos nueva sin modificar el servicio | Strategy, Factory por registro y Decorator, con punto de arranque | 0 archivos de lógica modificados frente a 1 en la versión inicial; 45 de 45 pruebas | Sí |
| 2 | QA-04 Confirmación idempotente | Unicidad por distrito, bloqueo por solicitud y transacción | 100 envíos, 10 concurrentes, 1 confirmación y 1 abono persistidos | Sí, en pruebas de integración con PostgreSQL 16.2 |
| 3 | QA-03 Aislamiento por distrito | Repositorio SQL vinculado al distrito autorizado | 100 lecturas y 100 escrituras cruzadas rechazadas. Los accesos propios siguieron disponibles | Sí, con el contexto de distrito suministrado por la aplicación |

### Documentación

- [ADR-006](docs/architecture/adr/006-reglas-de-puntos-extensibles.md)
- [ADR-007](docs/architecture/adr/007-confirmaciones-idempotentes.md)
- [ADR-008](docs/architecture/adr/008-aislamiento-por-distrito.md)
- Iteraciones de ADD: [1](docs/architecture/add/iteracion-1.md), [2](docs/architecture/add/iteracion-2.md) y [3](docs/architecture/add/iteracion-3.md)
- [Evaluación ATAM-lite](docs/architecture/atam-lite.md)
- [Borrador de evaluación emitida](docs/architecture/evaluacion-emitida-grupo01.md)
- [Bitácora de IA del Lab 08](docs/architecture/bitacora-lab08.md)
- [Integración y reproducción en PostgreSQL](docs/architecture/integracion-postgres.md)
- [Modelo C4 actualizado](docs/architecture/c4/workspace.dsl)

Pendientes de entrega: confirmar el destinatario y publicar la evaluación emitida; registrar la aprobación de los ADR-007 y ADR-008 en el PR; publicar `v0.8-arquitectura` sobre el commit revisado con el workflow aprobado.

## Prompt engineering (Lab 09)

La Tarea A genera criterios de aceptación para EcoRecicla AQP. Antony completa el dataset, la línea base, las iteraciones, cinco pruebas defensivas y nueve ejecuciones para observar variabilidad. La base de Diego está integrada en [PR #27](https://github.com/AntonyCondori/cs-2026b-lab04-grupo10/pull/27).

| Tarea | Versión | Casos aprobados | Tasa | Evidencia |
|---|---|---:|---:|---|
| A · Criterios | v1 | 0/9 | 0 % | [Comparación común](prompts/criterios/resultados.json) |
| A · Criterios | v2 | 8/9 | 88,89 % | [Comparación común](prompts/criterios/resultados.json) |
| A · Criterios | v3 | 9/9 | 100 % | [Reporte final](prompts/criterios/resultados-v3.json) |
| B · Docstrings | Pendiente de Bryan | — | — | Ciclo y CI de ambas tareas por completar |

![Aprobación por versión](prompts/criterios/tasas.svg)

Se mantuvieron los mismos nueve casos y siete aserciones en la comparación definitiva. Un caso aprueba cuando satisface todas las aserciones. v2 corrigió el formato; v3 corrigió el rechazo excesivo de HU-01 y añadió límites explícitos para tratar instrucciones incrustadas como datos. Ningún caso aprobado retrocedió. El 100 % corresponde a estas grabaciones y no garantiza toda salida futura.

HU-01 proviene del repositorio. Las otras cinco historias se redactaron ahora por indicación de Antony a partir de los RF documentados; no se presentan como recuperadas del antiguo backlog. Véase [procedencia de historias](docs/design/backlog-lab09.md). Hay dos historias no INVEST y un adversario adicional.

**Lecciones:** un contrato explícito corrigió el texto libre de v1; una decisión INVEST demasiado estricta también puede ser un fallo; el evaluador debe verificarse antes de interpretar sus tasas. Las cinco pruebas defensivas dieron 5/5 en v2 y 5/5 en v3, por lo que las defensas añadidas son un refuerzo sin mejora medida de tasa. Las tres repeticiones de cada caso cambiaron de redacción, conservando esquema y decisión INVEST.

**Reproducir la versión final:**

```bash
cd prompts/criterios
npx --yes promptfoo@0.118.0 eval -c config-v3.yaml --no-cache --no-table -o final-reproducido.json
npx --yes promptfoo@0.118.0 eval -c promptfoo-seguridad.yaml --no-cache --no-table -o seguridad-reproducida.json
```

La evaluación histórica completa (`npx --yes promptfoo@0.118.0 eval`) incluye v1 y v2 y termina con código 1 por sus fallos conocidos. Para CI de entrega debe comprobarse la versión final; Bryan incorporará también docstrings.

**Pruebas desde la raíz:**

```bash
python -m pip install pytest==9.2.0 jsonschema==4.26.0 import-linter==2.15
python -m pytest -q
```

Resultado local: 92 aprobadas y 4 omitidas (integración PostgreSQL sin DSN); 25 de las aprobadas corresponden al generador y las evidencias de Lab 09. Contratos de arquitectura: 2 conservados, 0 rotos. [Salida original de las pruebas](prompts/criterios/pruebas.txt).

- [Método de captura, límites y reproducción](prompts/criterios/metodologia.md)
- [Cambios de v1 a v3](prompts/criterios/iteraciones.md)
- [Casos y esperados congelados antes de evaluar](prompts/criterios/dataset-congelado.json)
- [46 grabaciones originales y hashes](prompts/criterios/manifiesto.json)
- [Seguridad: ataques y resultados antes/después](prompts/seguridad/red-team.md)
- [No determinismo: nueve ejecuciones y análisis en cinco líneas](prompts/criterios/no-determinismo.md)
- [Bitácora con interacciones reales y sugerencia rechazada](prompts/bitacora-ia.md)
- [Proceso y responsables de E1 a E8](docs/design/lab09-integracion.md)

Entrega a Bryan: revisar el PR de Antony y continuar con docstrings (E4), complementar E5, configurar el workflow `prompts.yml` para ambas tareas y consolidar E8, incluidos los PR revisados y la etiqueta `v0.9-prompts`. La revisión humana y esos entregables no se dan por completados en este aporte.


### Lab 09 · Consolidación de entrega

| Versión | Tarea A · Criterios | Tarea B · Docstrings |
|---|---:|---:|
| v1 | 0/9 (0,00 %) | Pendiente de ejecución en Promptfoo |
| v2 | 8/9 (88,89 %) | Pendiente de ejecución en Promptfoo |
| v3 | 9/9 (100,00 %) | Pendiente de ejecución en Promptfoo |

![Tasas de aprobación por versión](prompts/docstrings/tasas.svg)

El gráfico se regenera desde la raíz con `python prompts/docstrings/graficar.py`. Lee los informes de Promptfoo y marca las series pendientes cuando faltan informes.

**No determinismo en criterios.** Antony ejecutó v3 tres veces por caso. HU-01 y HU-04 conservaron INVEST verdadero y tres escenarios en cada ejecución. NI-01 conservó INVEST falso, cero escenarios y una pregunta. Las tres respuestas de cada caso difirieron en redacción. [Comparación y nueve ejecuciones](prompts/criterios/no-determinismo.md)

**Lecciones.** En criterios, el contrato explícito corrigió el formato libre y precisar el criterio INVEST resolvió el fallo restante. En docstrings, el esquema comprueba la estructura y las aserciones independientes cotejan la firma, el tipo de retorno y las excepciones. El contenido defensivo se prueba con variantes separadas del conjunto principal.

**Reproducción de docstrings.** Desde la raíz, con Ollama local, el modelo Qwen instalado y acceso al registro de npm, ejecutar por versión, en orden de v1 a v3:

```bash
python prompts/docstrings/capturar.py v1 --ollama qwen2.5:3b --cpu
python prompts/docstrings/evaluar.py docstrings v1
```

Para las entradas defensivas, añadir `--seguridad` a ambos comandos. Las grabaciones se preservan con las entradas y hashes. Un diagnóstico local con Python y JavaScript orientó los cambios en los prompts. La instalación de Promptfoo devolvió `EACCES`, así que las tasas de docstrings siguen pendientes. El workflow evalúa la v3 de ambas tareas con un umbral de 85 % y ejecuta pytest. Una grabación faltante hace fallar la evaluación.

- [PR #27 de Diego](https://github.com/AntonyCondori/cs-2026b-lab04-grupo10/pull/27)
- [PR #28 de Antony](https://github.com/AntonyCondori/cs-2026b-lab04-grupo10/pull/28)
- PR de Bryan: **[PENDIENTE_URL_PR_BRYAN]**
- Ejecución del workflow: **[PENDIENTE_URL_WORKFLOW]**
- Capturas y entrega: **[PENDIENTE_CAPTURAS]**, **[PENDIENTE_TAG_V0.9]**, **[PENDIENTE_URL_ENTREGA]**
- [Informes de criterios](prompts/criterios/resumen.json), [evaluación de docstrings](prompts/docstrings/promptfooconfig.yaml), [iteraciones y fallos observados](prompts/docstrings/iteraciones.md), [resultados defensivos](prompts/seguridad/red-team.md), [bitácora](prompts/bitacora-ia.md) y [workflow](.github/workflows/evaluar-prompts.yml).