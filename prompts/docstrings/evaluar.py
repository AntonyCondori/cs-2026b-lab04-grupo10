"""Ejecuta Promptfoo sobre una versión congelada y verifica su informe."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import NamedTemporaryFile, TemporaryDirectory

DIRECTORIO = Path(__file__).resolve().parent
CRITERIOS = DIRECTORIO.parent / "criterios"


def evaluar(directorio, config, salida, total_esperado, umbral):
    salida.parent.mkdir(parents=True, exist_ok=True)
    npx = shutil.which("npx.cmd" if os.name == "nt" else "npx")
    if not npx:
        raise SystemExit("No se encontró npx.")
    entorno = dict(os.environ, PROMPTFOO_DISABLE_TELEMETRY="1",
                   PROMPTFOO_DISABLE_UPDATE="1", PYTHONIOENCODING="utf-8",
                   PROMPTFOO_PYTHON=sys.executable)
    with TemporaryDirectory(dir=salida.parent) as temporal:
        informe = Path(temporal) / "resultado.json"
        proceso = subprocess.run(
            [npx, "--yes", "promptfoo@0.118.0", "eval", "-c", str(config),
             "--no-cache", "--no-table", "-o", str(informe)],
            cwd=directorio, env=entorno, check=False,
        )
        if proceso.returncode not in (0, 1, 100) or not informe.is_file():
            raise SystemExit(f"Promptfoo no produjo un informe válido (código {proceso.returncode}).")

        stats = json.loads(informe.read_text(encoding="utf-8"))["results"]["stats"]
        aprobados = stats["successes"]
        total = aprobados + stats["failures"] + stats["errors"]
        if stats["errors"] or total != total_esperado:
            raise SystemExit(f"Informe incompleto: {total}/{total_esperado} casos, {stats['errors']} errores.")
        informe.replace(salida)
    tasa = 100 * aprobados / total
    print(f"{salida.name}: {aprobados}/{total} aprobados ({tasa:.2f} %)")
    if tasa < umbral:
        raise SystemExit(f"La tasa quedó por debajo del {umbral:g} %.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tarea", choices=("criterios", "docstrings"))
    parser.add_argument("version", choices=("v1", "v2", "v3"))
    parser.add_argument("--seguridad", action="store_true")
    parser.add_argument("--umbral", type=int, default=0)
    parser.add_argument("--salida", type=Path)
    args = parser.parse_args()
    if not 0 <= args.umbral <= 100:
        parser.error('El umbral debe estar entre 0 y 100.')
    if args.tarea == "criterios":
        if args.seguridad:
            parser.error("Usa promptfoo-seguridad.yaml para la evaluación defensiva de criterios.")
        if args.salida is None:
            parser.error("Indica --salida para conservar los informes históricos de criterios.")
        evaluar(CRITERIOS, f"config-{args.version}.yaml", args.salida.resolve(), 9, args.umbral)
        return



    config = json.loads((DIRECTORIO / "promptfooconfig.yaml").read_text(encoding="utf-8"))
    config["prompts"] = [f"file://{args.version}.txt"]
    archivo_casos = "casos-seguridad.yaml" if args.seguridad else "casos.yaml"
    config["tests"] = f"file://{archivo_casos}"
    casos = json.loads((DIRECTORIO / archivo_casos).read_text(encoding="utf-8"))
    faltantes = [
        caso["vars"]["id"] for caso in casos
        if not (DIRECTORIO / "grabaciones" / args.version / f"{caso['vars']['id']}.txt").is_file()
    ]
    if faltantes:
        raise SystemExit(f"Faltan grabaciones para {args.version}: {', '.join(faltantes)}.")
    prefijo = "seguridad-" if args.seguridad else ""
    salida = args.salida or DIRECTORIO / "resultados" / f"{prefijo}{args.version}.json"
    with NamedTemporaryFile(suffix=".yaml", dir=DIRECTORIO, delete=False,
                            mode="w", encoding="utf-8") as temporal:
        json.dump(config, temporal, ensure_ascii=False)
    try:
        evaluar(DIRECTORIO, Path(temporal.name), salida.resolve(), len(casos), args.umbral)
    finally:
        Path(temporal.name).unlink()


if __name__ == "__main__":
    main()