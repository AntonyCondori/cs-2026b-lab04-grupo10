from src.solicitudes.eventos import PublicadorEventos
from src.solicitudes.operaciones_lab10 import SaldoVecinos


def test_evento_repetido_acredita_una_vez_por_solicitud():
    publicador = PublicadorEventos()
    saldo = SaldoVecinos()
    publicador.suscribir("solicitud_completada", saldo)

    primer_recojo = {"id": 101, "usuario": "V01", "puntos": 10}
    segundo_recojo = {"id": 102, "usuario": "V01", "puntos": 10}

    publicador.publicar("solicitud_completada", primer_recojo)
    publicador.publicar("solicitud_completada", primer_recojo)
    publicador.publicar("solicitud_completada", segundo_recojo)

    assert saldo.saldos["V01"] == 20