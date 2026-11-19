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

Adaptamos `LLMApiSimulada` y `WhatsAppSDK`, presentes en el commit de línea base
`313ab96`, a los contratos de clasificación y notificación. `MinamCartonAdapter`
usa el simulador de puntos añadido durante el refactor. Mantendremos la fábrica por registro FabricaCalculadoras
para incorporar calculadoras sin modificar el procesamiento principal.

Utilizamos Decorator para agregar caché, validación y reintentos al proveedor de IA.
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
- El proveedor reintenta hasta tres llamadas frente a `TimeoutError`. El servicio decide la cancelación del flujo de compatibilidad al agotar los intentos.
- Observer publica al completar el recojo del flujo de compatibilidad. La HU-01 de Lab 05 conserva su ciclo completo de seis estados de negocio.

## Evidencia y conclusión

Con Radon 6.0.1, `procesar_recojo` registra C (14) en la línea base, A (4) en `8e26afd` y A (2) en la subsanación. El constructor pasa de A (3) a B (6). Las SLOC del archivo `servicio.py` pasan de 54 a 45.

- Métricas: ../../design/patrones/metricas.md
- Evidencias: ../../design/patrones/mediciones/
- Diagramas: ../../design/patrones/
- Bitácora: ../../design/patrones/bitacora-ia.md
