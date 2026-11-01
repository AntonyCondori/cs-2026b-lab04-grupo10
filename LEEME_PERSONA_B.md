# Lab08: avance comprobable de Persona B

Base: main a4b957a0fa305f901facac1c6c2e081014587c99, después del PR #23 de Persona A.
No se modifican ServicioSolicitudes, README.md, workspace.dsl, fitness/modificabilidad.py ni archivos de Persona C.

## Instalar

1. Dentro del repositorio, revisa git status. Conserva y confirma tus cambios previos antes de cambiar de rama.
2. Ejecuta git fetch origin y git switch -c lab08/b-atam-iter2 origin/main.
3. Descomprime este ZIP en la raíz del repositorio. Sus rutas empiezan por fitness/, tests/ y docs/. Usa unzip -n para no reemplazar archivos que ya existan; si omite alguno de estos archivos, compara las versiones antes de continuar.
4. Activa .venv y ejecuta python -m pip install pytest matplotlib.

## Ejecutar

python -m fitness.disponibilidad
python -m pytest tests/test_disponibilidad.py -v
python -m pytest -q
python docs/architecture/riesgos/generar_matriz.py

Sobre la base revisada: 53 casos aprobados. Puede variar si C incorpora pruebas.

## Archivos

- fitness/disponibilidad.py: prototipo y función simular para FF-04.
- tests/test_disponibilidad.py: 8 casos.
- docs/architecture/add/iteracion-2.md: siete pasos, alternativas, resultados y límites.
- docs/architecture/adr/007-confirmaciones-idempotentes.md: ADR propuesto.
- docs/architecture/atam-lite.md: análisis interno y borrador de respuesta al issue #24; no publicado.
- docs/architecture/riesgos/: script y PNG de la matriz propuesta.
- docs/architecture/evidencias/iteracion-2/: resultados del entorno de revisión.
- docs/architecture/bitacora-lab08-b.md: aporte para añadir a la bitácora compartida; no son cinco interacciones nuevas.
- docs/architecture/aporte-persona-b-informe.md: texto y capturas para el informe.

## Consolidar bitácora sin reemplazar la anterior

Añade el contenido de docs/architecture/bitacora-lab08-b.md al final de docs/architecture/bitacora-ia.md UNA SOLA VEZ. Pide a A y C sus entradas reales de Lab08. No conviertas un solo diálogo en cinco interacciones ficticias.

## Entregar a Persona C

from fitness.disponibilidad import simular
r = simular("idempotencia")
assert r["confirmaciones"] == r["abonos"] == 1
assert r["duplicados"] == 0
assert r["resultado_original_reutilizado"]

El modo sin_tactica detecta 99 duplicados. C puede incorporar ambos controles a tests/test_fitness.py.
Antes de añadir estas pruebas, C debe revisar que fitness/modificabilidad.py no se invoque recursivamente al ejecutar pytest dentro de una copia. Conviene excluir .venv de esa copia y no fijar el total de regresión en 45.

## Pendientes que el ZIP no puede certificar

- Confirmar el repositorio asignado por el docente, evaluar su árbol e iteración 1 y publicar el issue saliente.
- Revisar con el equipo y publicar la respuesta al issue #24. Ningún comentario fue enviado por este avance.
- Completar cinco interacciones reales y un falso positivo de IA con su evidencia textual, si así lo exige el docente.
- Integrar PostgreSQL y el servicio antes de afirmar cumplimiento productivo de QA-04.
- Coordinar con A la fila de iteración 2, el enlace del ADR-007 y la coherencia R-06/C4.
- A/C deben cerrar el caso de distrito nuevo con regla Y horario, no solo el filtro de aislamiento.
- Revisar el workflow de C antes de aprobar el PR y crear la etiqueta final.
