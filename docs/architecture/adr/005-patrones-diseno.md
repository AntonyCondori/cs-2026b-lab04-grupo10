# ADR-005: Patrones para el cálculo de puntos y la clasificación de residuos

- Estado: Propuesto
- Fecha: 2026-10-25
- Decisores: Equipo del Grupo 10; pendiente de revisión cruzada.

## Contexto

El servicio de solicitudes concentraba clasificación de residuos, validaciones,
cálculo de puntos, campañas y notificaciones.

Esta concentración dificultaba sustituir el proveedor de IA y agregar nuevas
reglas sin modificar el método principal. El laboratorio utiliza servicios
simulados para ejecutar las pruebas sin claves ni conexiones externas.

## Alternativas consideradas

1. Mantener toda la lógica en el servicio.
2. Separar las variaciones mediante interfaces, adaptadores y composición.
3. Incorporar Abstract Factory para construir familias de componentes.

## Decisión

Usaremos Strategy para las reglas de puntos y los proveedores de clasificación.

Adaptaremos las interfaces externas mediante LLMSimuladoAdapter y
MinamCartonAdapter. Mantendremos la fábrica por registro FabricaCalculadoras
para incorporar calculadoras sin modificar el procesamiento principal.

Utilizaremos Decorator para agregar caché y validación al proveedor de IA.
La cadena de guardrails revisará el formato, los precios expresados con S/
y las respuestas que contengan PELIGROSO.

Rechazamos Abstract Factory porque no existen familias de productos
relacionados que justifiquen su complejidad. La fábrica por registro y
la inyección de dependencias cubren el alcance actual.

## Consecuencias

### Positivas

- Podemos sustituir el proveedor de clasificación mediante una interfaz.
- Podemos registrar nuevas calculadoras de puntos.
- Las descripciones repetidas reutilizan resultados válidos de la caché.
- Las respuestas rechazadas se bloquean antes de asignar puntos o notificar.
- Las responsabilidades extraídas cuentan con pruebas específicas.

### Negativas y limitaciones

- Aumenta la cantidad de clases, archivos y relaciones.
- La caché vive en memoria y no incorpora caducidad ni límite de tamaño.
- Los guardrails implementados son controles básicos; no garantizan que toda
  clasificación aceptada sea correcta.
- Los reintentos permanecen en el servicio.
- State y Observer están pendientes de integración en esta rama.

## Evidencia y conclusión

En el estado medido, procesar_recojo pasó de complejidad C (14) a B (9).
El constructor pasó de A (3) a A (4).

Las SLOC con alcance equiparado aumentaron de 200 a 283.
El refactor redujo la complejidad del método principal a cambio de más
código y configuración. Esta decisión resulta útil ante nuevos proveedores,
reglas de puntos y validaciones; una demostración pequeña podría conservar
la versión inicial.

Las métricas deberán actualizarse si la integración pendiente modifica el código.

- Métricas: ../../design/patrones/metricas.md
- Evidencias: ../../design/patrones/mediciones/
- Diagramas: ../../design/patrones/
- Bitácora: ../../design/patrones/bitacora-ia.md
