import pytest

from src.solicitudes.externos import LLMApiSimulada
from src.solicitudes.ia import ProveedorLLM, crear_clasificador
from src.solicitudes.servicio import ServicioSolicitudes, Solicitud


class ApiControlada:
    def __init__(self, respuesta):
        self.respuesta = respuesta
        self.llamadas = 0

    def predecir_categoria(self, descripcion):
        self.llamadas += 1
        return self.respuesta


def nueva_solicitud(identificador=1, descripcion="botella de plastico"):
    return Solicitud(
        id=identificador,
        usuario="Diego",
        celular="999888777",
        descripcion_residuo=descripcion,
    )


def test_clasificacion_valida():
    ia = crear_clasificador(api=LLMApiSimulada())

    assert ia.clasificar("botella de plastico") == "PLASTICO"


def test_cache_evitar_llamadas_repetidas():
    api = LLMApiSimulada()
    ia = crear_clasificador(api=api)

    assert ia.clasificar("botella") == "PLASTICO"
    assert ia.clasificar("botella") == "PLASTICO"
    assert api.llamadas == 1


@pytest.mark.parametrize("categoria, mensaje", [
    ("PLASTICO - S/ 50.00", "precio"),
    ("PELIGROSO", "peligroso"),
    ("", "formato"),
    (None, "formato"),
    (123, "formato"),
])
def test_guardrails_bloquean_salidas_invalidas(categoria, mensaje):
    api = ApiControlada({"status": "ok", "result": categoria})
    ia = crear_clasificador(api=api)

    with pytest.raises(ValueError, match=mensaje):
        ia.clasificar("residuo")


@pytest.mark.parametrize("respuesta", [
    None,
    [],
    {"status": "error", "result": "PLASTICO"},
    {"status": "ok"},
])
def test_rechaza_respuesta_mal_formada(respuesta):
    ia = crear_clasificador(api=ApiControlada(respuesta))

    with pytest.raises(ValueError, match="Guardrail"):
        ia.clasificar("residuo")


def test_cache_no_guarda_respuestas_rechazadas():
    api = ApiControlada({"status": "ok", "result": "PELIGROSO"})
    ia = crear_clasificador(api=api)

    for _ in range(2):
        with pytest.raises(ValueError, match="Guardrail"):
            ia.clasificar("residuo")

    assert api.llamadas == 2


def test_strategy_permite_otro_proveedor():
    class OtroProveedor(ProveedorLLM):
        def clasificar(self, descripcion):
            return "VIDRIO"

    ia = crear_clasificador(proveedor=OtroProveedor())

    assert ia.clasificar("frasco") == "VIDRIO"


def test_servicio_reutiliza_cache_entre_solicitudes():
    api = LLMApiSimulada()
    servicio = ServicioSolicitudes(ia_api=api)

    for identificador in (1, 2):
        solicitud = nueva_solicitud(identificador)

        assert servicio.procesar_recojo(solicitud) == "COMPLETADO"
        assert solicitud.puntos_asignados == 10

    assert api.llamadas == 1
    assert len(servicio.eventos) == 4


def test_reintentos_se_conservan():
    api = LLMApiSimulada(fallas=2)
    servicio = ServicioSolicitudes(ia_api=api)

    assert servicio.procesar_recojo(nueva_solicitud()) == "COMPLETADO"
    assert api.llamadas == 3


def test_tres_fallos_cancelan_solicitud():
    api = LLMApiSimulada(fallas=3)
    servicio = ServicioSolicitudes(ia_api=api)
    solicitud = nueva_solicitud()

    assert servicio.procesar_recojo(solicitud) == "CANCELADO"
    assert api.llamadas == 3
    assert solicitud.puntos_asignados == 0
    assert servicio.eventos == []


def test_guardrail_impide_puntos_y_notificaciones():
    servicio = ServicioSolicitudes()
    solicitud = nueva_solicitud(descripcion="bateria de auto")

    with pytest.raises(ValueError, match="Guardrail"):
        servicio.procesar_recojo(solicitud)

    assert solicitud.puntos_asignados == 0
    assert servicio.eventos == []
