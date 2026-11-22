import pytest
from agentes.orquestador_democratico import contar_votos

A = "APROBADO. Cumple el criterio"
C = "CAMBIOS: No conserva el orden"


@pytest.mark.parametrize("votos,resultado", [([A], True), ([C], False), ([A,A,C], True), ([C,A,C], False), ([A,A,A], True), ([C,C,C], False)])
def test_mayoria(votos, resultado):
    assert contar_votos(votos) is resultado


@pytest.mark.parametrize("votos", [[], [A,A], [A,A,"APROBADO"], [A,A,"CAMBIOS:"], [A,A,"APROBADOxyz"], [A,A,"APROBADO. "]])
def test_voto_invalido_no_aprueba(votos):
    with pytest.raises(ValueError):
        contar_votos(votos)


@pytest.mark.parametrize("observacion,aprobado", [("exit=0\n4 passed", True), ("exit=1\n1 failed", False), ("ERROR: PermissionError", False)])
def test_grabacion_no_aprueba_evidencia_fallida(tmp_path, observacion, aprobado):
    import json
    from agentes.orquestador_democratico import ModeloRevisionGrabada
    archivo = tmp_path / "decision.json"
    archivo.write_text(json.dumps([{"pensamiento": "Revisado", "final": A}]), encoding="utf-8")
    modelo = ModeloRevisionGrabada(archivo)
    decision = modelo.decidir([{"role": "user", "content": "objetivo"}, {"role": "user", "content": "Observación: " + observacion}])
    assert contar_votos([decision["final"]]) is aprobado
