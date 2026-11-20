"""Renderiza y guarda las respuestas originales de cada caso."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from urllib.request import Request, urlopen

DIRECTORIO = Path(__file__).resolve().parent
CAPTURADOR = DIRECTORIO.parent / "criterios" / "capturar_codex.py"


def capturar_ollama(modelo, entrada, salida, renderizado, cpu):
    opciones = {"temperature": 0, "num_predict": 512}
    if cpu:
        opciones.update(num_gpu=0, num_ctx=1024)
    solicitud = Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps({"model": modelo, "prompt": renderizado,
                         "stream": False, "options": opciones}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(solicitud, timeout=300) as respuesta:
        datos = json.load(respuesta)
    if not datos["done"]:
        raise RuntimeError(f"Ollama no terminó la respuesta para {entrada.name}.")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_bytes(datos["response"].encode("utf-8"))
    metadatos = {
        "proveedor": "Ollama local",
        "modelo": datos["model"],
        "fecha_utc": datos["created_at"],
        "opciones": opciones,
        "motivo_fin": datos.get("done_reason"),
        "entrada_sha256": hashlib.sha256(entrada.read_bytes()).hexdigest(),
        "respuesta_sha256": hashlib.sha256(salida.read_bytes()).hexdigest(),
    }
    salida.with_suffix(".metadata.json").write_text(
        json.dumps(metadatos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(f"{salida.parent.name}/{salida.name}: {datos.get('done_reason')}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", choices=("v1", "v2", "v3"))
    parser.add_argument("--seguridad", action="store_true")
    parser.add_argument("--ollama", metavar="MODELO", help="Usa un modelo local disponible en Ollama.")
    parser.add_argument('--cpu', action='store_true', help='Ejecuta Ollama sin GPU.')
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
        entrada.write_bytes(renderizado.encode("utf-8"))
        if args.ollama:
            capturar_ollama(args.ollama, entrada, salida, renderizado, args.cpu)
        else:
            subprocess.run([sys.executable, str(CAPTURADOR), str(entrada), str(salida)], check=True)


if __name__ == "__main__":
    main()