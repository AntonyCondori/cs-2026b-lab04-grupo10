# ADR-007: Confirmación y abono idempotentes en una transacción

- Estado: Propuesto; táctica validada en prototipo, pendiente de revisión e integración productiva.
- Fecha: 2026-10-31
- Proponente: Yauli Merma Diego Raul (Persona B).
- Decisores: equipo del Grupo 10, pendiente de revisión.

## Contexto

QA-04 (Lab08), derivado de RF-05 y EC-02, exige que 100 envíos de la misma confirmación, con 10 simultáneos, produzcan un recojo y un abono. El cliente puede perder el acuse después de completarse la operación y reenviar el mismo comando.

State evita repetir una transición sobre el mismo objeto, pero no mantiene un registro compartido y persistente para objetos reconstruidos en otras peticiones.

## Alternativas consideradas

1. Confiar solo en State: no deduplica distintas instancias con el mismo identificador.
2. Guardar las claves en memoria: se pierden al reiniciar y no coordinan réplicas.
3. Persistir clave y resultado, aplicar unicidad por clave y por recojo, y confirmar el abono dentro de una transacción.
4. Añadir cola/outbox: útil para entrega de eventos, pero una cola no elimina por sí sola los duplicados.

## Decisión

Proponemos la alternativa 3 sin cambiar el monolito modular. El prototipo SQLite guarda confirmación y abono de forma atómica. Los reenvíos válidos obtienen el resultado almacenado; los conflictos de clave o contenido se rechazan.

La integración productiva deberá implementar el mismo contrato en PostgreSQL. No se incorpora SQLite como tecnología de producción ni se modifica ServicioSolicitudes en este avance.

## Evidencia

En fitness/disponibilidad.py, con 100 envíos y 10 concurrentes: sin táctica se generan 100 abonos y 99 duplicados; con la táctica se genera 1 abono y 0 duplicados. Se descartan 10 acuses después del commit. Los duplicados devuelven el resultado original.

La suite de revisión aprobó 53 casos: 45 previos y 8 nuevos. Se verificaron conflictos, rollback y conservación del resultado al recrear el registro usando el mismo archivo.

## Consecuencias

- Positivas: deduplicación persistente y resultado estable en el prototipo; confirmación y abono se revierten juntos ante el fallo inyectado.
- Negativas: almacenamiento adicional, gestión de claves y contención de escritura.
- Límites: no hay integración productiva, benchmark de PostgreSQL ni garantía sobre notificaciones externas. La retención y el alcance de IDs por distrito deben definirse antes del despliegue.
- Trabajo posterior: Persona C automatiza FF-04; Persona A actualiza C4/README con el estado de prototipo y el vínculo QA-04. El equipo valida la transacción real y la estrategia de eventos antes de aceptar el ADR para producción.

## Referencias internas

- [Iteración 2 y supuestos](../add/iteracion-2.md)
- [Escenarios](../utilidad/escenarios.md)
- [ATAM-lite](../atam-lite.md)
- [Resultados](../evidencias/iteracion-2/resultados.txt)
