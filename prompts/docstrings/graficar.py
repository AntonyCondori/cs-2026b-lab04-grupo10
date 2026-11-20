"""Genera el gráfico de tasas con los informes de Promptfoo guardados."""
import json
from pathlib import Path

CARPETA = Path(__file__).resolve().parent


def tasa(archivo):
    if not archivo.is_file():
        return None
    s = json.loads(archivo.read_text(encoding="utf-8"))["results"]["stats"]
    total = s["successes"] + s["failures"] + s["errors"]
    if not total or s["errors"]:
        raise ValueError(f"Informe inválido: {archivo}")
    return 100 * s["successes"] / total


def main():
    partes = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 286" role="img" aria-labelledby="titulo">',
        '<title id="titulo">Tasas de aprobación por versión de prompt</title>',
        '<rect width="640" height="286" fill="#f8fafc"/>',
        '<g font-family="sans-serif" font-size="14" fill="#172535">',
        '<text x="24" y="30" font-size="20" font-weight="bold">Aprobación por versión</text>',
    ]
    for i, version in enumerate(("v1", "v2", "v3")):
        y = 63 + i * 65
        partes.append(f'<text x="24" y="{y + 20}">{version}</text>')
        for j, (archivo, color) in enumerate((
            (CARPETA.parent / "criterios" / f"resultados-{version}.json", "#177d60"),
            (CARPETA / "resultados" / f"{version}.json", "#245ebb"),
        )):
            valor = tasa(archivo)
            fila = y + j * 22
            partes.append(f'<rect x="70" y="{fila}" width="430" height="16" rx="3" fill="#e2e8f0"/>')
            if valor is not None:
                ancho = 430 * valor / 100
                partes.append(f'<rect x="70" y="{fila}" width="{ancho:.2f}" height="16" rx="3" fill="{color}"/>')
            etiqueta = "Pendiente" if valor is None else f"{valor:.2f} %".replace(".", ",")
            partes.append(f'<text x="514" y="{fila + 13}">{etiqueta}</text>')
    partes.extend((
        '<circle cx="33" cy="258" r="6" fill="#177d60"/><text x="46" y="263">Criterios</text>',
        '<circle cx="145" cy="258" r="6" fill="#245ebb"/><text x="158" y="263">Docstrings</text>',
        '</g></svg>',
    ))
    (CARPETA / "tasas.svg").write_text("\n".join(partes) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()