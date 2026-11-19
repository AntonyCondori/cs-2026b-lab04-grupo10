"""Reproduce una respuesta de promptfoo por versión y caso."""

import re
from pathlib import Path


GRABACIONES = Path(__file__).resolve().parent / "grabaciones"


def call_api(prompt, options, context):
    etiqueta = context["prompt"]["label"]
    version = re.search(r"(?:^|[/\\])(v[0-9]+(?:\.[0-9]+)*)\.txt(?=[:\s]|$)", etiqueta)
    caso = context["vars"].get("id", "")
    if not version or not re.fullmatch(r"[A-Za-z0-9_-]+", caso):
        return {"error": "La evaluación necesita una versión de prompt y un ID de caso válidos"}

    archivo = GRABACIONES / version[1] / f"{caso}.txt"
    try:
        return {"output": archivo.read_text(encoding="utf-8")}
    except FileNotFoundError:
        return {"error": f"Falta grabación para {version[1]}/{caso}"}
