from src.solicitudes.estados import Solicitud
from src.solicitudes.operaciones_lab10 import seleccionar_para_ruta


def test_ruta_incluye_pendiente_y_excluye_cancelada():
    pendiente = Solicitud(201, "V01", "900000001", "Botella de plástico")
    cancelada = Solicitud(202, "V02", "900000002", "Envase de vidrio")
    cancelada.cancelar()

    ruta = seleccionar_para_ruta([pendiente, cancelada])

    assert [solicitud.id for solicitud in ruta] == [201]