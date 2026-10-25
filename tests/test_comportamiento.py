import pytest
import importlib
from src.solicitudes.externos import LLMApiSimulada

@pytest.fixture(params=["antes.servicio", "despues.servicio"])
def m(request):
    try:
        return importlib.import_module(f"src.solicitudes.{request.param}")
    except ModuleNotFoundError:
        pytest.skip(f"Módulo {request.param} no implementado aún")

def crear_solicitud(m, descripcion="botella de plastico", estado="PENDIENTE"):
    return m.Solicitud(id=1, usuario="Juan", celular="999888777", descripcion_residuo=descripcion, estado=estado)

def test_procesar_solicitud_exitosa_asigna_puntos_y_notifica(m):
    servicio = m.ServicioSolicitudes()
    solicitud = crear_solicitud(m)
    
    estado_final = servicio.procesar_recojo(solicitud)
    
    assert estado_final == "COMPLETADO"
    assert solicitud.puntos_asignados == 10
    assert len(servicio.eventos) == 2
    assert "whatsapp: 999888777: 10 puntos" in servicio.eventos

def test_campana_multiplica_puntos(m):
    servicio = m.ServicioSolicitudes()
    solicitud = crear_solicitud(m)
    
    servicio.procesar_recojo(solicitud, campana="RECICLA_VERANO")
    assert solicitud.puntos_asignados == 20

def test_estado_invalido_lanza_error(m):
    servicio = m.ServicioSolicitudes()
    solicitud = crear_solicitud(m, estado="COMPLETADO")
    
    with pytest.raises(ValueError, match="ya fue procesada"):
        servicio.procesar_recojo(solicitud)

def test_guardrail_bloquea_respuestas_peligrosas_de_ia(m):
    servicio = m.ServicioSolicitudes()
    solicitud = crear_solicitud(m, descripcion="bateria de auto")
    
    with pytest.raises(ValueError, match="Guardrail"):
        servicio.procesar_recojo(solicitud)

def test_reintenta_tras_caidas_de_ia(m):
    ia_inestable = LLMApiSimulada(fallas=2)
    servicio = m.ServicioSolicitudes(ia_api=ia_inestable)
    solicitud = crear_solicitud(m)
    
    estado = servicio.procesar_recojo(solicitud)
    
    assert estado == "COMPLETADO"
    assert ia_inestable.llamadas == 3