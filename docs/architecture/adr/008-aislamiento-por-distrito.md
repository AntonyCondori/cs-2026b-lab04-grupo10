# ADR-008: Aislar solicitudes por distrito

- Estado: Propuesto para aprobación del equipo. Integración Python validada con PostgreSQL 16.2.
- Fecha: 2026-10-31
- Decisores: Equipo del Grupo 10, pendiente de aprobación

## Contexto
El crecimiento a 12 distritos exige no exponer información ajena.
QA-03 pide 0 filas de otro distrito en 100 intentos. atam-lite.md
registra R4 como crítico (3 x 5 = 15). Se mantienen el monolito,
un VPS, tres desarrolladores y el plazo de un mes.

## Alternativas consideradas
1. Una base por distrito: separación alta, más operación y respaldos.
2. Un esquema por distrito: más migraciones y configuración de roles.
3. Tabla compartida con distrito_id y filtro obligatorio por contexto.
4. PostgreSQL RLS como defensa adicional al integrar persistencia.

## Decisión
Proponemos la alternativa 3 y un repositorio que recibe siempre
el contexto del distrito autorizado por el servidor. No se aceptará
el distrito del formulario como autorización. Las claves incluyen
distrito e identificador. Se deniega el acceso cruzado antes de
devolver una fila; las escrituras usan la misma comprobación.

Se conserva el prototipo en `fitness/aislamiento.py`. El repositorio PostgreSQL enlazado a los servicios de alta y gestión filtra por distrito en cada lectura y escritura. RLS queda como defensa futura. Se mantiene la base compartida y se difiere el esquema por distrito.

## Evidencia
Con 100 intentos alternados entre D01 y D02, la línea base sin filtro
devuelve 100 filas ajenas; con filtro se deniegan 100 y se devuelven 0.
Se conservan accesos propios y se rechazan 100 escrituras cruzadas
sin alterar los puntos. Las seis pruebas de C pasaron; la regresión
completa pasó con 59 pruebas en la rama antony.
En PostgreSQL se rechazaron 100 lecturas y 100 intentos de confirmar un recojo ajeno. Cada distrito conservó acceso a sus registros. Ver [iteración 3](../add/iteracion-3.md) e [integración](../integracion-postgres.md).

## Consecuencias
- Positivas: control central, claves por distrito y verificación en CI.
- Negativas: el aislamiento depende del contexto y de cubrir todas
  las rutas de acceso; no hay separación física de datos.
- Riesgos: omitir filtro, falsificar el contexto o usar SQL sin control.
- Mitigaciones: obtener contexto del servidor, probar lectura/escritura
  y evaluar roles y RLS al integrar PostgreSQL. import-linter no revisa SQL.
- Trade-off aceptado: menor costo operacional y una base compartida
  a cambio de disciplina en filtros, permisos y pruebas.

## Alcance y aceptación
El servicio recibe el distrito autorizado desde el punto de arranque. La capa HTTP que autentica y obtiene el contexto, RLS y el tiempo de alta de distritos quedan pendientes. Registrar la aprobación del equipo y el enlace al PR antes de cambiar el estado a «Aceptado».
