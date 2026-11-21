from agentes.agente.contrato import validar_decision
from agentes.agente.herramientas import Herramientas


def test_rechaza_herramienta_inventada_para_acreditar_puntos(tmp_path):
    catalogo = Herramientas(str(tmp_path)).catalogo()
    decision = {
        "pensamiento": "Acreditar el recojo 101 al vecino V01.",
        "accion": "acreditar_puntos",
        "args": {"solicitud_id": 101, "vecino": "V01"},
    }

    valida, motivo = validar_decision(decision, catalogo)

    assert valida is False
    assert "herramienta desconocida" in motivo


def test_rechaza_ruta_del_issue_enviada_como_texto(tmp_path):
    catalogo = Herramientas(str(tmp_path)).catalogo()
    decision = {
        "pensamiento": "Leer el criterio de aceptación del Issue 01.",
        "accion": "leer_archivo",
        "args": "issues/ISSUE-01.md",
    }

    valida, motivo = validar_decision(decision, catalogo)

    assert valida is False
    assert "'args' debe ser un objeto JSON" in motivo


def test_rechaza_ejecutar_prueba_y_finalizar_en_la_misma_decision(tmp_path):
    catalogo = Herramientas(str(tmp_path)).catalogo()
    decision = {
        "pensamiento": "Verificar la corrección del saldo de V01.",
        "accion": "ejecutar_comando",
        "args": {"comando": "python -m pytest -q tests/test_issue_01.py"},
        "final": "El Issue 01 está resuelto.",
    }

    valida, motivo = validar_decision(decision, catalogo)

    assert valida is False
    assert "'accion' o 'final', pero no ambos" in motivo