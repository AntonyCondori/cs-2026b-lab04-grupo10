# Lab 08 - Aporte de Persona C a la bitácora

- Fecha: 2026-10-31. Herramienta: Codex.
- Solicitud: implementar las actividades C en antony, comprobarlas,
  hacer commits y abrir un PR; preparar un PDF para el informe.
- Propuesta: dos contratos de imports, pruebas de QA-01/04/03 y
  repositorio con contexto obligatorio de distrito.
- Verificación: 2 contratos KEPT; las violaciones temporales se
  detectaron y retiraron en prueba/violacion; 6 pruebas de fitness
  y 59 pruebas totales aprobadas. En QA-03 se denegaron 100 accesos
  cruzados y 100 escrituras ajenas, sin exponer filas ni cambiar puntos.
- Correcciones: cierre explícito de conexiones SQLite de B; FF-04 usa
  la estrategia real idempotencia. FF-03 no llama al medidor de A,
  porque este ejecuta pytest otra vez y produciría recursión.
- Decisión: incorporar la propuesta mediante PR. El aislamiento se
  demuestra en memoria; no se declaran implementados JWT, API ni RLS.

Este bloque corresponde a una interacción con varias propuestas.
B lo consolida en bitacora-ia.md. Las violaciones deliberadas no son
falsos positivos de IA; ese requisito necesita una respuesta real refutada.
