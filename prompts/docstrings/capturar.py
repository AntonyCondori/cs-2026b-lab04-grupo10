"""Renderiza cada entrada y reutiliza la captura original de Codex del equipo."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

DIRECTORIO = Path(__file__).resolve().parent
CAPTURADOR = DIRECTORIO.parent / "criterios" / "capturar_codex.py"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", choices=("v1", "v2", "v3"))
    parser.add_argument("--seguridad", action="store_true")
    args = parser.parse_args()
    plantilla = (DIRECTORIO / f"{args.version}.txt").read_text(encoding="utf-8")
    nombre = "casos-seguridad.yaml" if args.seguridad else "casos.yaml"
    casos = json.loads((DIRECTORIO / nombre).read_text(encoding="utf-8"))
    entradas = DIRECTORIO / "entradas" / args.version
    entradas.mkdir(parents=True, exist_ok=True)
    for caso in casos:
        variables = caso["vars"]
        archivo = f"{variables['id']}.txt"
        entrada = entradas / archivo
        salida = DIRECTORIO / "grabaciones" / args.version / archivo
        renderizado = plantilla.replace("{{codigo}}", variables["codigo"])
        if salida.exists():
            if entrada.read_text(encoding="utf-8") != renderizado:
                raise SystemExit(f"La entrada cambió para la grabación {salida}.")
            continue
        entrada.write_text(renderizado, encoding="utf-8")
        subprocess.run([sys.executable, str(CAPTURADOR), str(entrada), str(salida)], check=True)


if __name__ == "__main__":
    main()