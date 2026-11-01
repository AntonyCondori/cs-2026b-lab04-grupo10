from hashlib import sha256
from pathlib import Path

import pytest

from fitness.aislamiento import (
    Contexto, RepositorioDistrital, datos_prueba, simular as simular_aislamiento,
)
from fitness.disponibilidad import simular as simular_reenvios
from src.solicitudes.servicio import ServicioSolicitudes, Solicitud
from src.solicitudes.puntos import CalculadoraPuntos
from src.solicitudes.decoradores import ConBonoFijo


RAIZ = Path(__file__).resolve().parents[1]
LOGICA = ("servicio.py", "estados.py", "puntos.py", "decoradores.py")


def hashes_logica():
    return {nombre: sha256((RAIZ / "src/solicitudes" / nombre).read_bytes())
            .hexdigest() for nombre in LOGICA}


def test_ff03_regla_y_campana_sin_cambiar_logica():
    antes = hashes_logica()
    servicio = ServicioSolicitudes()
    extension = '''class CalculadoraMetal(CalculadoraPuntos):
    def calcular(self):
        return 20
servicio.fabrica.registrar("METAL", CalculadoraMetal)
servicio.campanas.registrar("FIESTAS_AQP", lambda c: ConBonoFijo(c, 30))
'''
    # Solo ejecuta este literal de prueba, nunca codigo de un usuario.
    exec(extension, {"CalculadoraPuntos": CalculadoraPuntos,
                     "ConBonoFijo": ConBonoFijo, "servicio": servicio})
    servicio.ia.predecir_categoria = lambda _: {"status": "ok", "result": "METAL"}
    for identificador, campana, esperado in (
        (101, "NINGUNA", 20), (102, "FIESTAS_AQP", 50)
    ):
        solicitud = Solicitud(identificador, "Prueba", "000", "metal")
        assert servicio.procesar_recojo(solicitud, campana) == "COMPLETADO"
        assert solicitud.puntos_asignados == esperado
    # Cinco lineas de extension y dos imports de sus dependencias.
    assert len(extension.splitlines()) + 2 <= 15
    assert hashes_logica() == antes


def test_ff04_un_abono_en_cien_envios():
    resultado = simular_reenvios("idempotencia")
    assert resultado["envios"] == 100
    assert resultado["simultaneas"] == 10
    assert resultado["confirmaciones"] == resultado["abonos"] == 1
    assert resultado["duplicados"] == 0
    assert resultado["puntos_totales"] == 10
    assert resultado["resultado_original_reutilizado"]


def test_ff05_cien_accesos_cruzados_sin_filas_ajenas():
    resultado = simular_aislamiento("con_filtro")
    assert resultado["intentos"] == resultado["denegados"] == 100
    assert resultado["filas_de_otro_distrito"] == 0
    assert simular_aislamiento("sin_filtro")["filas_de_otro_distrito"] == 100


def test_aislamiento_permite_datos_propios_en_ambos_distritos():
    repo = RepositorioDistrital(datos_prueba())
    for distrito, puntos in (("D01", 10), ("D02", 20)):
        contexto = Contexto(distrito)
        filas = repo.listar(contexto)
        assert len(filas) == 1
        assert filas[0].distrito_id == distrito
        assert repo.obtener(contexto, distrito, 1).puntos == puntos


def test_escritura_cruzada_no_cambia_datos():
    repo = RepositorioDistrital(datos_prueba())
    for i in range(100):
        propio, ajeno = ("D01", "D02") if i % 2 == 0 else ("D02", "D01")
        with pytest.raises(PermissionError):
            repo.actualizar(Contexto(propio), ajeno, 1, 999)
    assert repo.obtener(Contexto("D01"), "D01", 1).puntos == 10
    assert repo.obtener(Contexto("D02"), "D02", 1).puntos == 20


def test_sin_contexto_y_recurso_inexistente_se_rechazan():
    with pytest.raises(ValueError):
        Contexto("")
    repo = RepositorioDistrital(datos_prueba())
    with pytest.raises(PermissionError):
        repo.obtener(Contexto("D01"), "D01", 999)
