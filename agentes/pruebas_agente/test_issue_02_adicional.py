"""Casos adicionales del reto, sin modificar la aceptación escrita por el equipo."""
from src.solicitudes.estados import Solicitud
from src.solicitudes.operaciones_lab10 import seleccionar_para_ruta


def crear(numero, cancelada=False):
    solicitud = Solicitud(numero, "V01", "900000001", "Botella")
    if cancelada:
        solicitud.cancelar()
    return solicitud


def test_vacia():
    assert seleccionar_para_ruta([]) == []


def test_todas_canceladas():
    assert seleccionar_para_ruta([crear(1, True), crear(2, True)]) == []


def test_preserva_orden_identidad_y_no_modifica_entrada():
    entrada = [crear(3), crear(2, True), crear(1)]
    copia = entrada.copy()
    resultado = seleccionar_para_ruta(iter(entrada))
    assert resultado == [entrada[0], entrada[2]]
    assert resultado[0] is entrada[0]
    assert entrada == copia
