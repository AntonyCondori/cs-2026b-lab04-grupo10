# E6. Métricas y trade-off

## Herramienta y alcance

Se utilizó Radon 6.0.1 para medir complejidad ciclomática y líneas de código fuente (SLOC).

La medición inicial comprende src/solicitudes/antes/servicio.py.
La medición posterior comprende src/solicitudes/, excluyendo la carpeta antes/.

Las pruebas y la documentación no forman parte de las mediciones.

## Complejidad del servicio

| Método | Antes | Después |
|---|---:|---:|
| ServicioSolicitudes.procesar_recojo | C (14) | B (9) |
| ServicioSolicitudes.__init__ | A (3) | A (4) |

La complejidad de procesar_recojo disminuyó 5 puntos, equivalentes al 35,7 %.
El constructor aumentó un punto; por tanto, la mejora no fue uniforme en todos los métodos.

## Resumen de las ejecuciones

| Indicador | Antes | Después |
|---|---:|---:|
| Complejidad promedio reportada | B (7,00) | A (2,06) |
| Bloques analizados | 4 | 78 |
| SLOC del alcance ejecutado | 54 | 283 |
| SLOC de servicio.py | 54 | 48 |

Los bloques reportados por Radon incluyen clases, funciones y métodos.

Los promedios y los totales corresponden a alcances diferentes.
El promedio posterior incluye más bloques pequeños y código previo del proyecto.
Por ello, su descenso no demuestra por sí solo una mejora equivalente de todo el sistema.

## SLOC con alcance equiparado

Para comparar los totales se incluyen los módulos compartidos externos.py y dominio.py en ambos lados.
Estos archivos no fueron modificados durante E5.

| Archivo | Antes | Después |
|---|---:|---:|
| servicio.py de cada versión | 54 | 48 |
| externos.py, compartido | 22 | 22 |
| dominio.py, compartido | 124 | 124 |
| puntos.py, extraído durante el refactor | 0 | 26 |
| ia.py, añadido durante el refactor | 0 | 38 |
| guardrails.py, añadido durante el refactor | 0 | 25 |
| Total equiparado | 200 | 283 |

El total equiparado se obtiene sumando las SLOC de los archivos indicados.
El valor 0 significa que ese archivo separado no existía en la versión inicial.
El aumento fue de 83 SLOC, equivalente al 41,5 %.

## Análisis del trade-off

El método procesar_recojo pasó de complejidad 14 a 9 al delegar parte de sus responsabilidades.
La interfaz del proveedor permite cambiar la clasificación sin modificar el flujo de solicitudes.
La caché evita llamadas repetidas y la cadena de guardrails separa las validaciones de salida.
El costo fue agregar clases, archivos y 83 SLOC en el alcance equiparado.
El constructor aumentó de complejidad 3 a 4 y requiere configurar más dependencias.
La versión inicial habría sido suficiente para una demostración pequeña sin cambios previstos.
El refactor resulta útil si se incorporan nuevos proveedores, reglas de puntos o validaciones.

## Patrón rechazado

Se rechazó Abstract Factory porque el caso no requiere crear familias de objetos relacionados.
La fábrica por registro existente y la inyección de dependencias cubren las necesidades actuales.
Agregar Abstract Factory introduciría interfaces e indirección sin un beneficio concreto para este alcance.

## Evidencias

- mediciones/cc-antes.txt
- mediciones/cc-despues.txt
- mediciones/sloc-antes.txt
- mediciones/sloc-despues.txt

Las salidas completas contienen la complejidad por método y el detalle de SLOC por archivo.
