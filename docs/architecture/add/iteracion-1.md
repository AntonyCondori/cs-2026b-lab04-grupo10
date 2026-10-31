# Iteración 1 de ADD — Reglas de puntos extensibles (QA-01)

## Objetivo

Incorporar una regla de puntos nueva (material o campaña) sin modificar el código de lógica existente (QA-01, H,M). Se atiende antes que QA-02 (H,H) porque el escenario del distrito necesita primero un mecanismo estable de reglas; QA-03 se trata en la iteración 3.

## Entradas

- Drivers: R-01 (1 mes), R-02 (3 desarrolladores), R-03 (presupuesto bajo), R-04 (modificabilidad).
- ADR-001: monolito modular. ADR-005: Strategy, Factory por registro y Decorator.
- Código: `src/solicitudes/puntos.py`, `decoradores.py`, `servicio.py` y la versión inicial `antes/servicio.py`.

## Elemento refinado

Módulo Puntos dentro del monolito (componente "Módulo Puntos y Canjes" del C4) y su punto de arranque.

## Conceptos de diseño evaluados

| Concepto | Táctica | Qué mejora | Qué empeora | Decisión |
|---|---|---|---|---|
| Mantener `if/elif` en el servicio (versión `antes/`) | Ninguna | Menos archivos | Cada regla edita `procesar_recojo`, complejidad C (14) | Rechazada |
| Strategy, Factory por registro y Decorator para campañas (ADR-005), con punto de arranque | Reducir acoplamiento (puertos y adaptadores) | Una regla nueva es una clase o un registro | Más clases; hace falta un punto de arranque donde registrar | Aceptada |
| Reglas de puntos como datos en PostgreSQL, por distrito, material y vigencia | Configuración en base de datos | Cambios sin desplegar código (RF-07) | Más casos de prueba; errores de configuración | Diferida a la iteración 3 (ADR-008), porque depende del concepto de distrito |
| Extraer Puntos como microservicio | Escalar por separado | Despliegue independiente | Viola plazo, equipo y presupuesto (R-01, R-02, R-03) y el estilo de ADR-001 | Rechazada |

## Decisión

Mantener Strategy, Factory por registro y Decorator como mecanismo de extensión, y registrar las reglas nuevas en un punto de arranque (`src/solicitudes/arranque.py`, con su prueba `tests/test_arranque.py`). `servicio.py` no se modifica. La parte por distrito se resuelve en la iteración 3.

## Evidencia cuantitativa

Se midió con `fitness/modificabilidad.py` (`python -m fitness.modificabilidad`). El script copia el repositorio a una carpeta temporal, incorpora la regla en la versión ANTES (`antes/servicio.py`) y en la DESPUÉS (`servicio.py` + `arranque.py`), verifica que la regla funcione y ejecuta las 45 pruebas.

| Caso | Versión | Archivos de lógica modificados | Líneas añadidas en ellos | Archivos nuevos (líneas) | Líneas en `arranque.py` | Regla funciona | Pruebas |
|---|---|---:|---:|---:|---:|---|---|
| Material nuevo (METAL, 20 puntos) | Antes | 1 | 2 | 0 (0) | 0 | sí | 45 ok |
| Material nuevo (METAL, 20 puntos) | Después | 0 | 0 | 1 (6) | 2 | sí | 45 ok |
| Campaña nueva (FIESTAS_AQP, +30) | Antes | 1 | 2 | 0 (0) | 0 | sí | 45 ok |
| Campaña nueva (FIESTAS_AQP, +30) | Después | 0 | 0 | 0 (0) | 2 | sí | 45 ok |

Contexto del Lab 07: la complejidad de `procesar_recojo` bajó de C (14) a B (9) (`docs/design/patrones/metricas.md`).

## Supuestos de la medición

- Los archivos de lógica son `servicio.py`, `estados.py`, `puntos.py` y `decoradores.py`. `arranque.py` no se cuenta como modificado porque existe para editarse; sus líneas se reportan aparte.
- La medida es una aproximación del escenario: cuenta archivos y líneas, no horas-persona.
- La regla es un valor fijo por material o campaña; no incluye distrito, vigencia ni versiones (RF-07).
- Los parches de la versión "antes" son los cambios mínimos que haría un desarrollador en el `if/elif`.
- Si una regla nueva necesitara cambiar el flujo del servicio (y no solo su valor), el resultado "después" dejaría de valer.
- Las pruebas se ejecutan sobre la copia temporal; el repositorio del equipo no se modifica.

## ¿Se cumple el escenario?

Sí. Las tres medidas de QA-01 se cumplen: 0 archivos de lógica modificados, ≤ 15 líneas nuevas (8 en el caso del material: 6 en el archivo nuevo y 2 en el arranque; 2 en el de la campaña) y 45 de 45 pruebas aprobadas.

## Trade-off aceptado

Se acepta más estructura (clases y archivos, ver ADR-005) a cambio de que agregar una regla no toque el método principal. Con una sola regla la ganancia en líneas es pequeña (2 líneas antes frente a 8 después en el caso del material); el beneficio real es no editar `procesar_recojo`, que concentra la complejidad.

## Pendiente para la iteración 3

Reglas por distrito (QA-02) y aislamiento entre distritos (QA-03).
