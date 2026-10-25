import pytest
from src.solicitudes.antes.servicio import Solicitud
from src.solicitudes.servicio import ServicioSolicitudes
from src.solicitudes.puntos import CalculadoraPuntos

class CalculadoraMetal(CalculadoraPuntos):
    """Nueva estrategia creada solo para la prueba."""
    def calcular(self) -> int:
        return 20

def test_open_closed_nuevo_material_sin_modificar_el_servicio():
    servicio = ServicioSolicitudes()
    
    servicio.fabrica.registrar("METAL", CalculadoraMetal)
    solicitud = Solicitud(id=2, usuario="Ana", celular="123", descripcion_residuo="latas de metal")
    
    servicio.ia.predecir_categoria = lambda desc: {"status": "ok", "result": "METAL"}
    servicio.procesar_recojo(solicitud)

    assert solicitud.puntos_asignados == 20