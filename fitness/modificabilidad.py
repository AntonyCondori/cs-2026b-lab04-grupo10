"""Fitness function de modificabilidad (QA-01, iteración 1 de ADD).

Mide cuánto hay que tocar para incorporar una regla de puntos nueva (un material
o una campaña) en dos versiones del código:

  ANTES   -> src/solicitudes/antes/servicio.py (if/elif dentro de procesar_recojo)
  DESPUES -> servicio.py + arranque.py (Strategy, Factory por registro, Decorator)

Trabaja sobre una COPIA temporal del repositorio; el repositorio real no se modifica.

Uso:
    python -m fitness.modificabilidad           # imprime la tabla
    from fitness.modificabilidad import medir   # lo usa tests/test_fitness.py (FF-03)
"""
import difflib
import re
import shutil
import subprocess
import sys
import tempfile
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LOGICA = ["src/solicitudes/servicio.py", "src/solicitudes/estados.py",
          "src/solicitudes/puntos.py", "src/solicitudes/decoradores.py"]
ANTES = "src/solicitudes/antes/servicio.py"
ARRANQUE = "src/solicitudes/arranque.py"

METAL_PY = ("from src.solicitudes.puntos import CalculadoraPuntos\n\n\n"
            "class CalculadoraMetal(CalculadoraPuntos):\n"
            "    def calcular(self) -> int:\n"
            "        return 20\n")


def _leer(p):
    return Path(p).read_bytes().decode("utf-8")


def _escribir(p, texto):
    Path(p).write_bytes(texto.encode("utf-8"))


def _nl(texto):
    return "\r\n" if "\r\n" in texto else "\n"


def _insertar_antes(texto, ancla, nuevas):
    """Inserta `nuevas` (lista de líneas) justo antes de la primera línea que contiene `ancla`."""
    nl = _nl(texto)
    lineas = texto.split(nl)
    i = next(k for k, l in enumerate(lineas) if ancla in l)
    return nl.join(lineas[:i] + nuevas + lineas[i:])


def _insertar_despues(texto, ancla, nuevas):
    nl = _nl(texto)
    lineas = texto.split(nl)
    i = next(k for k, l in enumerate(lineas) if ancla in l)
    return nl.join(lineas[:i + 1] + nuevas + lineas[i + 1:])


def _lineas_anadidas(antes, despues):
    d = difflib.ndiff(antes.splitlines(), despues.splitlines())
    return sum(1 for x in d if x.startswith("+ "))


# --- parches ---------------------------------------------------------------
def _parche_antes_material(t):
    return _parche_elif(t, "VIDRIO", ['        elif categoria == "METAL":',
                                      '            puntos_base = 20'])


def _parche_elif(t, material, nuevas):
    nl = _nl(t)
    lineas = t.split(nl)
    # línea `puntos_base = 15` (VIDRIO): insertar después
    i = next(k for k, l in enumerate(lineas) if f'"{material}"' in l)
    return nl.join(lineas[:i + 2] + nuevas + lineas[i + 2:])


def _parche_antes_campana(t):
    nl = _nl(t)
    lineas = t.split(nl)
    i = next(k for k, l in enumerate(lineas) if '"DIA_TIERRA"' in l)
    nuevas = ['        elif campana == "FIESTAS_AQP":', '            puntos_base += 30']
    return nl.join(lineas[:i + 2] + nuevas + lineas[i + 2:])


def _parche_despues_material(t):
    t = _insertar_despues(t, "from src.solicitudes.servicio import",
                          ["from src.solicitudes.metal import CalculadoraMetal"])
    return _insertar_despues(t, '"""Registra aquí',
                             ['    servicio.fabrica.registrar("METAL", CalculadoraMetal)'])


def _parche_despues_campana(t):
    t = _insertar_despues(t, "from src.solicitudes.servicio import",
                          ["from src.solicitudes.decoradores import ConBonoFijo"])
    return _insertar_despues(t, '"""Registra aquí',
                             ['    servicio.campanas.registrar("FIESTAS_AQP", lambda c: ConBonoFijo(c, 30))'])


# --- verificación de que la regla funciona -----------------------------------
_VERIF = {
    ("material", "antes"): """
from src.solicitudes.antes.servicio import ServicioSolicitudes, Solicitud
s = ServicioSolicitudes()
s.ia.predecir_categoria = lambda d: {"status": "ok", "result": "METAL"}
x = Solicitud(id=1, usuario="Ana", celular="1", descripcion_residuo="latas")
s.procesar_recojo(x)
print(x.puntos_asignados)
""",
    ("material", "despues"): """
from src.solicitudes.arranque import crear_servicio
from src.solicitudes.servicio import Solicitud
s = crear_servicio()
s.ia.predecir_categoria = lambda d: {"status": "ok", "result": "METAL"}
x = Solicitud(id=1, usuario="Ana", celular="1", descripcion_residuo="latas")
s.procesar_recojo(x)
print(x.puntos_asignados)
""",
    ("campana", "antes"): """
from src.solicitudes.antes.servicio import ServicioSolicitudes, Solicitud
s = ServicioSolicitudes()
x = Solicitud(id=1, usuario="Ana", celular="1", descripcion_residuo="botella")
s.procesar_recojo(x, campana="FIESTAS_AQP")
print(x.puntos_asignados)
""",
    ("campana", "despues"): """
from src.solicitudes.arranque import crear_servicio
from src.solicitudes.servicio import Solicitud
s = crear_servicio()
x = Solicitud(id=1, usuario="Ana", celular="1", descripcion_residuo="botella")
s.procesar_recojo(x, campana="FIESTAS_AQP")
print(x.puntos_asignados)
""",
}
_ESPERADO = {"material": "20", "campana": "40"}


def _ejecutar(cwd, *args, codigo=None):
    cmd = [sys.executable] + (["-c", codigo] if codigo else list(args))

    env = os.environ.copy()
    env["PYTHONPATH"] = str(cwd)

    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True
    )


def _medir_caso(caso, version):
    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / "repo"
        shutil.copytree(RAIZ, copia, ignore=shutil.ignore_patterns(
            ".git", "__pycache__", ".pytest_cache", "*.pyc"))
        originales = {r: _leer(copia / r) for r in LOGICA + [ANTES, ARRANQUE]}
        nuevos = 0
        lineas_nuevos = 0
        if version == "antes":
            f = ANTES
            parche = _parche_antes_material if caso == "material" else _parche_antes_campana
            _escribir(copia / f, parche(originales[f]))
        else:
            if caso == "material":
                _escribir(copia / "src/solicitudes/metal.py", METAL_PY)
                nuevos, lineas_nuevos = 1, len(METAL_PY.splitlines())
            parche = _parche_despues_material if caso == "material" else _parche_despues_campana
            _escribir(copia / ARRANQUE, parche(originales[ARRANQUE]))

        considerados = LOGICA + ([ANTES] if version == "antes" else [])
        modificados = [r for r in considerados if _leer(copia / r) != originales[r]]
        lineas_logica = sum(_lineas_anadidas(originales[r], _leer(copia / r)) for r in modificados)
        lineas_arranque = _lineas_anadidas(originales[ARRANQUE], _leer(copia / ARRANQUE))

        v = _ejecutar(copia, codigo=_VERIF[(caso, version)])
        funciona = v.returncode == 0 and v.stdout.strip() == _ESPERADO[caso]

        t = _ejecutar(copia, "-m", "pytest", "-q", "-p", "no:cacheprovider")
        m = re.search(r"(\d+) passed", t.stdout)
        pasadas = int(m.group(1)) if m else 0
        falladas = bool(re.search(r"\d+ failed|error", t.stdout))
        return {
            "caso": "Material nuevo (METAL, 20 puntos)" if caso == "material"
                    else "Campaña nueva (FIESTAS_AQP, +30)",
            "version": "Antes" if version == "antes" else "Después",
            "archivos_existentes_modificados": len(modificados),
            "lineas_en_modificados": lineas_logica,
            "archivos_nuevos": nuevos, "lineas_archivos_nuevos": lineas_nuevos,
            "lineas_arranque": lineas_arranque if version == "despues" else 0,
            "regla_funciona": funciona, "pruebas_ok": pasadas, "pruebas_fallan": falladas,
        }


def medir():
    return [_medir_caso(c, v) for c in ("material", "campana") for v in ("antes", "despues")]


def tabla_markdown(filas):
    enc = ("| Caso | Versión | Archivos de lógica modificados | Líneas añadidas en ellos "
           "| Archivos nuevos (líneas) | Líneas en `arranque.py` | Regla funciona | Pruebas |\n"
           "|---|---|---:|---:|---:|---:|---|---|")
    out = [enc]
    for r in filas:
        out.append(f"| {r['caso']} | {r['version']} | {r['archivos_existentes_modificados']} "
                   f"| {r['lineas_en_modificados']} | {r['archivos_nuevos']} ({r['lineas_archivos_nuevos']}) "
                   f"| {r['lineas_arranque']} | {'sí' if r['regla_funciona'] else 'NO'} "
                   f"| {r['pruebas_ok']} ok{' (HAY FALLAS)' if r['pruebas_fallan'] else ''} |")
    return "\n".join(out)


if __name__ == "__main__":
    filas = medir()
    print(tabla_markdown(filas))
    despues = [f for f in filas if f["version"] == "Después"]
    ok = all(f["archivos_existentes_modificados"] == 0 and f["regla_funciona"]
             and not f["pruebas_fallan"] for f in despues)
    print("\nQA-01:", "SE CUMPLE" if ok else "NO SE CUMPLE")
    sys.exit(0 if ok else 1)
