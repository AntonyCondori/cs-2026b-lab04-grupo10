# ADR-006: Mantener el mecanismo de reglas de puntos extensible y registrar las reglas en un punto de arranque

- Estado: Aceptado
- Fecha: 2026-10-31
- Decisores: Condori Caira Antony Beltran, Sencia Ale Bryan Daniel, Yauli Merma Diego Raul

## Contexto

EcoRecicla AQP pasa de 3 a 12 distritos, cada uno con su regla de puntos. El escenario QA-01 exige incorporar una regla nueva sin modificar el código de lógica existente (R-04), dentro de 1 mes, con 3 desarrolladores y presupuesto bajo (R-01, R-02, R-03). ADR-005 ya introdujo Strategy, Factory por registro y Decorator.

## Alternativas consideradas

1. Mantener `if/elif` en el servicio.
2. Strategy, Factory por registro y Decorator, con las reglas registradas en un punto de arranque.
3. Reglas como datos en PostgreSQL por distrito, material y vigencia.
4. Extraer Puntos como microservicio.

## Decisión

Usaremos la alternativa 2. Las reglas nuevas se registran en `src/solicitudes/arranque.py`, de modo que `servicio.py` no cambie. Rechazamos la alternativa 1 porque cada regla edita el método principal (complejidad C (14)) y la alternativa 4 porque viola el plazo, el equipo, el presupuesto y ADR-001. La alternativa 3 se evalúa en la iteración 3 (ADR-008), porque depende del concepto de distrito.

## Evidencia

Medición con `fitness/modificabilidad.py` sobre una copia del repositorio: agregar un material o una campaña modifica 1 archivo de lógica (2 líneas) en la versión inicial y 0 archivos de lógica en la versión actual (2 líneas en `arranque.py`), con 45 de 45 pruebas aprobadas. Detalle y supuestos en `docs/architecture/add/iteracion-1.md`.

## Consecuencias

- Positivas: una regla nueva es una clase o un registro, sin editar `procesar_recojo`; la medición se puede automatizar como fitness function (FF-03).
- Negativas / riesgos: más clases y archivos; la medida cuenta archivos y líneas, no horas-persona; las reglas por distrito aún no están resueltas.
- Mitigaciones: ADR-008 resuelve la dimensión de distrito; la fitness function de modificabilidad evita que alguien vuelva a poner reglas dentro del servicio.

## Aclaración sobre la tecnología

ADR-001 y el modelo C4 mencionan Node.js y dependency-cruiser, pero el código del repositorio está en Python. Para verificar los límites entre módulos se usa import-linter (equivalente en Python). Queda pendiente actualizar esas menciones o confirmar la tecnología definitiva.

## Corrección a ADR-005

ADR-005 indica que State y Observer están pendientes de integración, pero ya están integrados en `main` (`estados.py`, `eventos.py` y `servicio.py`).
