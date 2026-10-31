from src.solicitudes.arranque import crear_servicio
from src.solicitudes.servicio import Solicitud


def test_arranque_crea_un_servicio_funcional():
    servicio = crear_servicio()
    solicitud = Solicitud(id=1, usuario="Ana", celular="999888777",
                          descripcion_residuo="botella de plastico")

    assert servicio.procesar_recojo(solicitud) == "COMPLETADO"
    assert solicitud.puntos_asignados == 10
