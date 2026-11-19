import json

import pytest

from src.solicitudes.generador_criterios import (
    DIRECTORIO_CRITERIOS,
    GeneradorCriterios,
    ProveedorCriteriosGrabado,
    SalidaInvalida,
)


RESPUESTA_VALIDA = {
    "historia_id": "HU-01",
    "invest_ok": False,
    "preguntas": ["¿Qué datos debe ingresar el vecino?"],
    "escenarios": [],
}


@pytest.fixture
def directorio_criterios(tmp_path):
    esquema = (DIRECTORIO_CRITERIOS / "esquema.json").read_text(encoding="utf-8")
    (tmp_path / "esquema.json").write_text(esquema, encoding="utf-8")
    (tmp_path / "v1.txt").write_text("Historia {{id}}:\n{{historia}}", encoding="utf-8")
    (tmp_path / "v3.1.txt").write_text("Evalúa {{id}}.\n<datos>{{historia}}</datos>", encoding="utf-8")
    return tmp_path


def test_acepta_respuesta_grabada_valida(tmp_path):
    grabacion = tmp_path / "HU-01.txt"
    grabacion.write_text(json.dumps(RESPUESTA_VALIDA), encoding="utf-8")
    generador = GeneradorCriterios(ProveedorCriteriosGrabado(grabacion), "v1")

    assert generador.generar("HU-01", "Como vecino, quiero solicitar un recojo.") == RESPUESTA_VALIDA


@pytest.mark.parametrize(
    ("texto", "error"),
    [
        ("No hay una respuesta en JSON.", "fuera de JSON"),
        (json.dumps(dict(RESPUESTA_VALIDA, invest_ok="false")), "fuera del esquema"),
        (json.dumps(dict(RESPUESTA_VALIDA, historia_id="HU-02")), "ID de historia incorrecto"),
    ],
)
def test_rechaza_respuesta_grabada_invalida(tmp_path, texto, error):
    grabacion = tmp_path / "HU-01.txt"
    grabacion.write_text(texto, encoding="utf-8")
    generador = GeneradorCriterios(ProveedorCriteriosGrabado(grabacion), "v1")

    with pytest.raises(SalidaInvalida, match=error):
        generador.generar("HU-01", "Como vecino, quiero solicitar un recojo.")


def test_carga_version_y_conserva_los_datos_de_la_historia(directorio_criterios):
    class ProveedorEspia:
        def completar(self, prompt):
            self.prompt = prompt
            return json.dumps(RESPUESTA_VALIDA)

    proveedor = ProveedorEspia()
    generador = GeneradorCriterios(proveedor, "v3.1", directorio_criterios)

    generador.generar("HU-01", "Historial con la etiqueta {{id}}.")

    assert proveedor.prompt == "Evalúa HU-01.\n<datos>Historial con la etiqueta {{id}}.</datos>"
