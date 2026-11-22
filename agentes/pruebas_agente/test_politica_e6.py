"""Contratos de autorización y mínimo privilegio de E6."""
from unittest.mock import Mock

import pytest

from agentes.agente.herramientas import Herramientas
from agentes.agente.nucleo import Agente
from agentes.agente.politica import Politica, aprobar_edicion


@pytest.mark.parametrize("respuesta,esperado", [("s", True), (" S ", True), ("n", False), ("N", False)])
def test_aprobacion_explicita(monkeypatch, respuesta, esperado):
    monkeypatch.setattr("builtins.input", lambda _: respuesta)
    assert aprobar_edicion({"ruta": "src/a.py", "antes": "a", "despues": "b"}) is esperado


def test_repite_hasta_respuesta_valida(monkeypatch):
    entrada = Mock(side_effect=["", "si", "n"])
    monkeypatch.setattr("builtins.input", entrada)
    assert not aprobar_edicion({})
    assert entrada.call_count == 3


@pytest.mark.parametrize("error", [EOFError, KeyboardInterrupt])
def test_sin_respuesta_rechaza(monkeypatch, error):
    monkeypatch.setattr("builtins.input", Mock(side_effect=error))
    assert not aprobar_edicion({})


@pytest.mark.parametrize("ruta", ["tests/a.py", "./tests/a.py", "src/../tests/a.py", "/tmp/a.py", "agentes/a.py", "src/../../a.py", "tests\\a.py"])
def test_proteccion_precede_consulta_humana(ruta):
    callback = Mock(return_value=True)
    assert not Politica(aprobar_edicion=callback).evaluar("editar_archivo", {"ruta": ruta}, 1).permitido
    callback.assert_not_called()


@pytest.mark.parametrize("cmd", ["python -m pytest; touch archivo", "git diff && rm a", "git diff $(id)", "python -m pytest\necho x", "git status-extra", "bash -c id", 'git diff "'])
def test_comando_fuera_de_alcance_bloqueado(cmd):
    assert not Politica().evaluar("ejecutar_comando", {"comando": cmd}, 1).permitido


@pytest.mark.parametrize("cmd", ["python -m pytest -q tests/test_issue_02.py", "git diff", "git status --short", "radon cc src/ -s", "lint-imports --no-cache"])
def test_comandos_previstos_permitidos(cmd):
    assert Politica().evaluar("ejecutar_comando", {"comando": cmd}, 1).permitido


def test_revisor_sin_edicion_y_limite_antes_de_aprobar():
    callback = Mock(return_value=True)
    assert not Politica(herramientas_permitidas={"leer_archivo"}).evaluar("editar_archivo", {"ruta": "src/a.py"}, 1).permitido
    assert not Politica(max_pasos=1, aprobar_edicion=callback).evaluar("editar_archivo", {"ruta": "src/a.py"}, 2).permitido
    callback.assert_not_called()


def test_rechazo_no_modifica_y_siguiente_aprobacion_si(tmp_path):
    archivo = tmp_path / "src" / "a.py"
    archivo.parent.mkdir()
    archivo.write_text("valor = 1\n", encoding="utf-8")
    cambio = {"pensamiento": "Cambio controlado", "accion": "editar_archivo", "args": {"ruta": "src/a.py", "antes": "valor = 1", "despues": "valor = 2"}}
    modelo = Mock()
    modelo.decidir.side_effect = [cambio, cambio, {"pensamiento": "Fin", "final": "Hecho"}]
    contenidos = []

    def aprobar(args):
        contenidos.append(archivo.read_text(encoding="utf-8"))
        return len(contenidos) == 2

    agente = Agente("ejecutor", modelo, Herramientas(str(tmp_path)), Politica(aprobar_edicion=aprobar), "Objetivo", tmp_path / "traza.jsonl")
    agente.ejecutar()
    assert contenidos == ["valor = 1\n", "valor = 1\n"]
    assert archivo.read_text(encoding="utf-8") == "valor = 2\n"
    assert agente.eventos[1]["estado"] == "BLOQUEADO"
    assert agente.eventos[2]["estado"] == "OBSERVANDO"
