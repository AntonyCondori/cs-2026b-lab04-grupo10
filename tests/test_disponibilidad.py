from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from fitness.disponibilidad import RegistroConfirmaciones, simular


def test_qa04_cien_envios_diez_simultaneos():
    r = simular("idempotencia")
    assert r["confirmaciones"] == r["abonos"] == 1
    assert r["duplicados"] == 0
    assert r["puntos_totales"] == 10
    assert r["acuses_perdidos"] == 10
    assert r["respuestas_recibidas"] == 90
    assert r["resultado_original_reutilizado"]


def test_sin_tactica_evidencia_duplicados():
    r = simular("sin_tactica")
    assert r["confirmaciones"] == r["abonos"] == 100
    assert r["duplicados"] == 99
    assert r["puntos_totales"] == 1000
    assert not r["resultado_original_reutilizado"]


def test_reinicio_conserva_resultado(tmp_path):
    ruta = tmp_path / "registro.db"
    original = RegistroConfirmaciones(ruta).confirmar("recojo-1")
    reiniciado = RegistroConfirmaciones(ruta)
    assert reiniciado.confirmar("recojo-1") == original
    assert reiniciado.contar()["abonos"] == 1


@pytest.mark.parametrize("clave,solicitud,puntos", [
    ("recojo-1", 1, 99), ("recojo-1", 2, 10), ("otra-clave", 1, 10)
])
def test_conflicto_no_abona(tmp_path, clave, solicitud, puntos):
    registro = RegistroConfirmaciones(tmp_path / "registro.db")
    registro.confirmar("recojo-1")
    with pytest.raises(ValueError, match="Conflicto"):
        registro.confirmar(clave, solicitud, puntos)
    assert registro.contar()["abonos"] == 1


def test_fallo_intermedio_revierte_ambas_escrituras(tmp_path):
    registro = RegistroConfirmaciones(tmp_path / "registro.db")
    with pytest.raises(RuntimeError):
        registro.confirmar("recojo-1", fallo_antes_abono=True)
    assert registro.contar()["confirmaciones"] == 0
    assert registro.contar()["abonos"] == 0
    registro.confirmar("recojo-1")
    assert registro.contar()["abonos"] == 1


def test_solicitudes_distintas_se_conservan(tmp_path):
    registro = RegistroConfirmaciones(tmp_path / "registro.db")
    barrera = Barrier(10)

    def confirmar(i):
        barrera.wait(timeout=15)
        return registro.confirmar(f"recojo-{i}", solicitud=i)

    with ThreadPoolExecutor(max_workers=10) as ejecutor:
        resultados = list(ejecutor.map(confirmar, range(1, 11)))
    assert len({r["confirmacion"] for r in resultados}) == 10
    assert registro.contar()["abonos"] == 10
    assert registro.contar()["puntos_totales"] == 100
