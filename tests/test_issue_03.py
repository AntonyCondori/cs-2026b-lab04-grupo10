from src.solicitudes.arranque import crear_servicio
from src.solicitudes.operaciones_lab10 import calcular_puntos_distrito


def test_bono_de_plastico_solo_en_distrito_d01():
    fabrica = crear_servicio().fabrica

    puntos = {
        distrito: calcular_puntos_distrito(fabrica, "PLASTICO", distrito)
        for distrito in ("D01", "D02")
    }

    assert puntos == {"D01": 15, "D02": 10}