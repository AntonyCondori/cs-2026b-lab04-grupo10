# E6 · Métricas de la subsanación

Radon 6.0.1, con los mismos métodos en tres puntos de comparación. La línea base es `src/solicitudes/antes/servicio.py`. La columna intermedia mide `src/solicitudes/servicio.py` tal como estaba en `8e26afd`. La última mide la versión de esta subsanación.

| Indicador | Línea base | `8e26afd` | Subsanación |
|---|---:|---:|---:|
| Complejidad de `ServicioSolicitudes.procesar_recojo` | C (14) | A (4) | A (2) |
| Complejidad de `ServicioSolicitudes.__init__` | A (3) | B (6) | B (6) |
| SLOC del archivo del servicio | 54 | 45 | 45 |

El método principal reduce sus decisiones al delegar el estado, los guardrails y los reintentos. El constructor cuesta más que en la línea base porque configura dependencias y suscriptores. Las SLOC son del archivo indicado; los estados, decoradores y adaptadores tienen código en otros módulos. Las cifras históricas 6 y 9 atribuidas a `procesar_recojo` no corresponden a la medición de `8e26afd` ni a la subsanación.

Se mantiene la fábrica por registro para crear calculadoras. Abstract Factory requeriría familias de componentes que el caso actual no usa.

## Reproducción

```bash
python -m pip install radon==6.0.1
radon cc -s src/solicitudes/antes/servicio.py src/solicitudes/servicio.py
radon raw src/solicitudes/antes/servicio.py src/solicitudes/servicio.py
git show 8e26afd:src/solicitudes/servicio.py | radon cc -s -
git show 8e26afd:src/solicitudes/servicio.py | radon raw -
```

Salidas en [mediciones](mediciones/).
