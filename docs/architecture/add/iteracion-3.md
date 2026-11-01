# Iteración 3 de ADD - Aislamiento por distrito (QA-03)

## 1. Revisar entradas
Se revisaron drivers.md, ADR-001, ADR-006, utilidad/escenarios.md
y atam-lite.md. EcoRecicla AQP crece de 3 a 12 distritos, con un VPS,
3 desarrolladores y un mes. El ATAM local registra R4 (P=3, I=5,
15 puntos) como crítico y pendiente de la Persona C. R2 trata accesos
SQL; los contratos de imports no analizan permisos ni consultas SQL.

## 2. Objetivo
QA-03 (H,M): un usuario autenticado del distrito A intenta consultar
datos del distrito B. Resultado: 0 filas ajenas en 100 de 100 intentos,
sin cambios no autorizados. El prototipo prueba ambos sentidos.

## 3. Elemento refinado
Acceso a solicitudes dentro del monolito. Se introduce distrito_id
en un registro mínimo y un contexto de distrito obligatorio para
el repositorio. No se modifica el dominio ni la API existentes.

## 4. Conceptos evaluados
- Base por distrito: mayor separación operacional, pero exige
  12 bases y coordinación de migraciones y respaldos. Rechazada
  para el plazo y presupuesto; no se midió su costo monetario.
- Esquema por distrito: separa nombres y permisos, pero multiplica
  migraciones y no evita errores de rol. Diferida.
- Tabla compartida, distrito_id y filtro obligatorio: permite
  centralizar el control. Elegida para el prototipo en memoria.
  Exige revisar cada acceso y confiar en un contexto autorizado.
- RLS de PostgreSQL: defensa adicional para el diseño futuro.
  No está implementada ni validada por estas pruebas en memoria.

## 5. Instanciar responsabilidades
Contexto contiene el distrito obtenido tras autenticar y autorizar
en el servidor; su construcción se simula en las pruebas.
FilaSolicitud conserva id, distrito_id y puntos como datos inmutables.
RepositorioDistrital exige contexto en listar, obtener y actualizar.
Las claves incluyen distrito e id: dos distritos pueden usar id=1.
El acceso cruzado y el recurso inexistente reciben el mismo error.
actualizar reutiliza obtener; una denegación no escribe datos.

## 6. Vistas y ADR
Flujo: identidad autorizada -> Contexto -> RepositorioDistrital
-> comprobar distrito -> devolver o actualizar únicamente datos propios.
Ver ADR-008. Enviar a A: agregar [QA-03] a Identidad y distritos,
Solicitudes y persistencia en C4. No hace falta un contenedor nuevo.
El diseño futuro debe conservar distrito_id en claves y relaciones,
y evaluar RLS con un rol de aplicación sin privilegios de bypass.

## 7. Analizar resultados
Comando: python -m fitness.aislamiento
- Sin filtro: 100 intentos, 0 denegados, 100 filas ajenas devueltas.
- Con filtro: 100 intentos, 100 denegados, 0 filas ajenas devueltas.
- Control: los dos distritos consultan su propia fila correctamente.
- Escritura: 100 intentos cruzados rechazados; puntos originales 10 y 20.
- Conjunto de C: 6 pruebas aprobadas; suite completa: 59 aprobadas
  en la rama antony con los ajustes documentados para puntos.py
  y el cierre de conexiones de fitness/disponibilidad.py.

La línea base sin filtro es experimental; no representa una fuga
medida en una API productiva. Los datos son sintéticos, con dos
distritos y contexto simulado, sin HTTP, JWT ni PostgreSQL.
QA-03 se cumple en el prototipo. R4 queda mitigado en este ensayo,
pero abierto para producción hasta integrar autorización y persistencia.

Trade-off: se acepta una base compartida y un filtro central que
debe aplicarse siempre, a cambio de menor complejidad operacional.
Riesgo: omitir un filtro o confiar en un distrito enviado por el cliente.
Mitigación: contexto autorizado, filtros obligatorios, pruebas de lectura
y escritura y futura verificación SQL/RLS. R2 no queda cerrado por
import-linter. QA-02 (16 horas-persona, reglas y horarios por distrito)
no se mide ni se declara cumplido con este prototipo.
