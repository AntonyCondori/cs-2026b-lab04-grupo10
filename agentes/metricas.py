"""Resume las métricas de una o más trazas JSONL del agente."""

import argparse
import json
from pathlib import Path


def resumir_traza(ruta: Path) -> dict:
    acciones = bloqueados = invalidos = contexto = 0
    paso_final = None
    herramientas_usadas = set()

    with ruta.open(encoding="utf-8") as archivo:
        for linea in archivo:
            if not linea.strip():
                continue
            evento = json.loads(linea)
            if evento["tipo"] == "final":
                paso_final = evento["paso"]
            if evento["tipo"] == "accion":
                acciones += 1
                contexto += len(evento["observacion"][:600])
                estado = evento["estado"]
                bloqueados += estado == "BLOQUEADO"
                invalidos += estado == "CONTRATO_INVALIDO"
                if estado == "OBSERVANDO":
                    herramientas_usadas.add(evento["accion"])

    return {
        "Acciones": acciones,
        "Paso del final": paso_final if paso_final is not None else "sin final",
        "Eventos BLOQUEADO": bloqueados,
        "Eventos CONTRATO_INVALIDO": invalidos,
        "Contexto final (caracteres)": contexto,
        "Usó mapa_repo": "sí" if "mapa_repo" in herramientas_usadas else "no",
        "Usó anotar": "sí" if "anotar" in herramientas_usadas else "no",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trazas", nargs="+", type=Path, help="Archivos JSONL de agentes/trazas")
    args = parser.parse_args()
    carpeta_trazas = Path(__file__).resolve().parent / "trazas"

    for entrada in args.trazas:
        ruta = carpeta_trazas / entrada if entrada.parent == Path(".") else entrada
        try:
            metricas = resumir_traza(ruta)
        except (OSError, json.JSONDecodeError) as error:
            parser.exit(1, f"{ruta}: {error}\n")
        print(ruta.name)
        for etiqueta, valor in metricas.items():
            print(f"  {etiqueta}: {valor}")


if __name__ == "__main__":
    main()
