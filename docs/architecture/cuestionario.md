# Cuestionario - Lab 08

## Persona C - Pregunta 7

Una fitness function comprueba automáticamente una propiedad de la
arquitectura y permite detectar su degradación en cada Pull Request.

- FF-01 detecta dependencias hacia capas superiores del módulo.
- FF-02 detecta imports directos o indirectos de externos desde la lógica.
- FF-03 verifica una regla y una campaña nuevas, sus puntos y el límite
  de 15 líneas, sin modificar archivos de lógica durante la extensión.
- FF-04 detecta duplicación de abonos o falta de reutilización del resultado
  en el prototipo de 100 envíos, incluidos 10 simultáneos.
- FF-05 detecta exposición de filas ajenas en 100 consultas entre distritos.

Los controles adicionales comprueban acceso propio, rechazo de escrituras
cruzadas y contexto obligatorio. import-linter no analiza permisos SQL;
el prototipo en memoria no sustituye autorización ni RLS en producción.
