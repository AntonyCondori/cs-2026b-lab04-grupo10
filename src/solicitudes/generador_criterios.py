"""Generación de criterios de aceptación con salida validada."""

import json
import re
from pathlib import Path

from jsonschema import ValidationError
from jsonschema.validators import validator_for

from src.solicitudes.ia import ProveedorGeneracionLLM


DIRECTORIO_CRITERIOS = Path(__file__).resolve().parents[2] / "prompts" / "criterios"
VARIABLE_PLANTILLA = re.compile(r"\{\{(id|historia)\}\}")


class SalidaInvalida(ValueError):
    """La respuesta generada no puede usarse como criterios de aceptación."""


class ProveedorCriteriosGrabado:
    """Reproduce una respuesta guardada para una versión y un caso concretos."""

    def __init__(self, archivo: Path) -> None:
        self._archivo = archivo

    def completar(self, prompt: str) -> str:
        return self._archivo.read_text(encoding="utf-8")


class GeneradorCriterios:
    def __init__(
        self,
        proveedor: ProveedorGeneracionLLM,
        version: str,
        directorio: Path = DIRECTORIO_CRITERIOS,
    ) -> None:
        if not re.fullmatch(r"v[0-9]+(?:\.[0-9]+)*", version):
            raise ValueError("La versión debe tener un formato como v1 o v3.1")

        self._proveedor = proveedor
        self._version = version
        self._plantilla = (directorio / f"{version}.txt").read_text(encoding="utf-8")
        esquema = json.loads((directorio / "esquema.json").read_text(encoding="utf-8"))
        clase_validador = validator_for(esquema)
        clase_validador.check_schema(esquema)
        self._validador = clase_validador(esquema)

    def generar(self, id_historia: str, historia: str) -> dict[str, object]:
        valores = {"id": id_historia, "historia": historia}
        prompt = VARIABLE_PLANTILLA.sub(lambda campo: valores[campo[1]], self._plantilla)
        respuesta = self._proveedor.completar(prompt)

        if not isinstance(respuesta, str):
            raise SalidaInvalida(f"{self._version}/{id_historia}: se esperaba una respuesta de texto")

        try:
            criterios = json.loads(respuesta)
        except json.JSONDecodeError as error:
            raise SalidaInvalida(f"{self._version}/{id_historia}: respuesta fuera de JSON") from error

        try:
            self._validador.validate(criterios)
        except ValidationError:
            raise SalidaInvalida(f"{self._version}/{id_historia}: respuesta fuera del esquema") from None

        if not isinstance(criterios, dict) or criterios.get("historia_id") != id_historia:
            raise SalidaInvalida(f"{self._version}/{id_historia}: ID de historia incorrecto")

        return criterios
