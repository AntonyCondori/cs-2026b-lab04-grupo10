# Backlog de criterios · Lab 09

Responsable: Antony Condori.

HU-01 se conserva del Lab 05. HU-02 a HU-06 se redactaron durante esta sesión por indicación expresa de Antony («créalas tú»), a partir de los requisitos ya documentados en `docs/architecture/drivers.md`. No se presentan como historias recuperadas de un backlog anterior. Esta adaptación del requisito E1 debe ser validada por el equipo/docente.

## HU-01

Como vecino, quiero solicitar el recojo de mis residuos reciclables desde la aplicación ingresando mi dirección y el detalle de mis residuos, para que un reciclador pueda asignar mi solicitud a su ruta diaria.

Fuente: docs/design/historia.md. Resultado esperado antes de ejecutar: Dirección y detalle obligatorios; solicitud disponible para asignar.

## HU-02

Como vecino, quiero cancelar mi solicitud antes del inicio del recojo para corregir un pedido que ya no necesito. Una solicitud cuyo recojo ya comenzó no puede cancelarse.

Fuente: RF-01. Resultado esperado antes de ejecutar: Cancelar antes del inicio; rechazar cancelación después del inicio.

## HU-03

Como reciclador formalizado, quiero consultar la ruta del día como una lista ordenada de mis paradas asignadas para organizar mis recojos. Si no tengo paradas, quiero ver que mi ruta está vacía.

Fuente: RF-04. Resultado esperado antes de ejecutar: Mostrar paradas asignadas ordenadas; informar ruta sin paradas.

## HU-04

Como reciclador formalizado, quiero confirmar el recojo de una solicitud asignada y registrar el peso decimal en kilogramos de cada material para dejar constancia de lo recogido. Los pesos negativos se rechazan y repetir una confirmación no duplica el recojo ni los puntos.

Fuente: RF-05. Resultado esperado antes de ejecutar: Aceptar peso válido; rechazar negativo; confirmación repetida no duplica.

## HU-05

Como vecino, quiero consultar mi saldo de puntos y canjear un beneficio con saldo suficiente para aprovechar mis reciclajes. El canje descuenta el costo del beneficio y se rechaza si el saldo es insuficiente, sin dejar saldo negativo.

Fuente: RF-06. Resultado esperado antes de ejecutar: Consultar saldo y canjear; rechazar saldo insuficiente; admitir saldo exacto.

## HU-06

Como responsable municipal, quiero consultar un reporte de toneladas recicladas por distrito, material y período para medir el resultado de la recolección. Las toneladas se calculan sumando los kilogramos de recojos confirmados y dividiendo entre 1000; un período sin recojos muestra cero toneladas.

Fuente: RF-08. Resultado esperado antes de ejecutar: Filtrar reporte y convertir kg/1000; período vacío da cero.

## Casos difíciles

NI-01: historia ambigua. NI-02: tarea técnica sin valor verificable para usuario. ADV-01: inyección directa sobre HU-02. Los nueve casos y sus expectativas se congelan antes de ejecutar v1; las mismas entradas se usan en todas las versiones.
