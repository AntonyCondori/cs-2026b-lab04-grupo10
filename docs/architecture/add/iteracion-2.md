# Iteración 2 de ADD: confirmaciones idempotentes (QA-04)

## 1. Revisar las entradas

- Base revisada: main a4b957a0fa305f901facac1c6c2e081014587c99.
- Árbol Lab08: QA-04 (H,M), 100 envíos de la misma confirmación, incluidos 10 simultáneos; 1 recojo confirmado, 1 abono, 0 duplicados y resultado original para el reenvío.
- Trazabilidad: QA-04 de utilidad/escenarios.md corresponde a EC-02 y RF-05 de drivers.md. Los identificadores QA del Lab04 y Lab08 no son equivalentes automáticamente.
- Restricciones: monolito modular, 1 mes, 3 desarrolladores y presupuesto bajo.
- State controla transiciones de un objeto, pero no una clave persistente compartida por todos los reenvíos.
- Evaluación recibida: issue #24, Grupo 01. Sus riesgos se analizan en atam-lite.md. No señaló expresamente duplicación de puntos: QA-04 se justifica por EC-02, sin atribuirle ese hallazgo al evaluador.

## 2. Establecer el objetivo

Atender QA-04, diferente de QA-01 utilizado en la iteración 1. Se aborda la fiabilidad/integridad de las confirmaciones, agrupada bajo disponibilidad en el árbol.

## 3. Elegir el elemento que se refinará

El límite transaccional entre registrar una confirmación de recojo y registrar su abono. Se construye un prototipo aislado, sin modificar ServicioSolicitudes ni los archivos de Persona A o C.

## 4. Elegir conceptos de diseño y evaluar alternativas

| Alternativa | Beneficio | Costo / límite | Decisión |
|---|---|---|---|
| Confiar en State y en el objeto actual | Menos infraestructura | Un objeto nuevo con el mismo ID puede procesarse de nuevo | Rechazada para QA-04 |
| Claves procesadas en memoria | Evita repeticiones en una instancia | Se pierde al reiniciar y no coordina varios procesos | Rechazada como solución persistente |
| Clave de idempotencia y unicidad por recojo, dentro de una transacción | Coordina solicitudes concurrentes y conserva el resultado | Índices, almacenamiento y contención de escrituras | Elegida para el prototipo |
| Cola con reintentos / outbox | Puede conservar trabajo pendiente y desacoplar entrega | Un reenvío de la cola también puede duplicarse; requiere consumidor idempotente | Complemento futuro para eventos externos, no sustituto de la unicidad |

No se necesitan microservicios para esta verificación.

## 5. Instanciar componentes y responsabilidades

- fitness/disponibilidad.py: RegistroConfirmaciones y simular(estrategia).
- RegistroConfirmaciones: dos tablas SQLite en un mismo archivo; confirmaciones y abonos se escriben en una única transacción.
- Modo protegido: restricciones únicas por clave de idempotencia y por ID de solicitud. BEGIN IMMEDIATE serializa comprobación y escritura.
- El reenvío con la misma clave y contenido devuelve la confirmación almacenada. Cambiar el contenido o la clave para el mismo recojo se rechaza sin otro abono.
- Cada petición abre su propia conexión. La protección no depende de un diccionario o lock de Python.
- tests/test_disponibilidad.py: 8 casos de prueba, incluidos concurrencia, recuperación al recrear el registro y rollback ante fallo entre las dos escrituras.

## 6. Registrar vistas y decisiones

Decisión: ADR-007, ../adr/007-confirmaciones-idempotentes.md.

Vista lógica: entrada de confirmación -> registro idempotente -> transacción que escribe confirmación y abono. El duplicado obtiene el resultado almacenado; no genera otra fila.

Para Persona A: conservar los contenedores existentes. Cuando se implemente en el servicio, describir en Solicitudes y Puntos el límite transaccional [QA-04] y la persistencia de claves. No introducir Redis, Kafka ni un contenedor SQLite productivo por este prototipo.

## 7. Analizar y verificar

Ejecución: python -m fitness.disponibilidad.

| Medida | Sin táctica | Con idempotencia |
|---|---:|---:|
| Envíos con el mismo ID y contenido | 100 | 100 |
| Peticiones liberadas simultáneamente | 10 | 10 |
| Acuses descartados después del commit | 10 | 10 |
| Confirmaciones almacenadas | 100 | 1 |
| Abonos almacenados | 100 | 1 |
| Abonos duplicados | 99 | 0 |
| Puntos totales, a 10 por abono | 1000 | 10 |
| Resultado original reutilizado | No | Sí |

53 pruebas aprobadas en el entorno de revisión: 45 previas y 8 casos nuevos. El número puede cambiar al integrar los aportes de Persona C.

QA-04 se cumple EN EL PROTOTIPO. No se afirma que ya se cumpla en el servicio desplegado.

### Supuestos y límites

- Una solicitud lógica, 100 envíos totales; 10 comienzan juntos y los otros 90 se envían secuencialmente.
- SQLite usa un archivo compartido y serializa escritores. Concurrencia de entrada no significa 10 escrituras simultáneas.
- Se descarta cada décimo acuse después del commit: 10 %. No se modela una distribución real de fallos de red ni se mide p95.
- La comparación reutiliza la misma carga y almacenamiento; el modo inicial omite la consulta de deduplicación y los índices únicos.
- La prueba de fallo intermedio valida rollback; la de recreación conserva el archivo. No se ejecutan cortes físicos de energía ni procesos independientes.
- El ID de solicitud se supone global. La iteración 3 debe resolver su relación con el distrito, sin permitir dos abonos del mismo recojo.
- No se prueba PostgreSQL, autorización, reglas versionadas ni entrega de WhatsApp exactamente una vez.
- Antes de producción se requieren integración con ServicioSolicitudes, pruebas en PostgreSQL, política de retención y resolución de fallos de notificación (outbox si corresponde).

### Trade-off aceptado

Se acepta persistir claves/resultados y serializar las escrituras del prototipo a cambio de no duplicar abonos en la carga ensayada. El costo de latencia y el volumen máximo soportado siguen sin medirse; no se atribuye una mejora de rendimiento.

## Contrato para Persona C

```python
from fitness.disponibilidad import simular

resultado = simular("idempotencia")
assert resultado["confirmaciones"] == 1
assert resultado["abonos"] == 1
assert resultado["duplicados"] == 0
assert resultado["resultado_original_reutilizado"]
```

Persona C puede usarlo como FF-04 en tests/test_fitness.py. Debe verificar también que simular("sin_tactica") detecte 99 duplicados para evitar una prueba que siempre apruebe.
