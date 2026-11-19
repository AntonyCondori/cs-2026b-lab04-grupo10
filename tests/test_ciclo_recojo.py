import pytest

from src.solicitudes.dominio import (
    Coordenadas, DetalleResiduo, Direccion, ErrorValidacion, EstadoSolicitud,
    Solicitud, SolicitarRecojoService,
)


def nueva_solicitud():
    return Solicitud.crear("V01", Direccion("Dirección de prueba"), [
        DetalleResiduo("PLASTICO", "Botella para reciclar", 1.5),
    ])


def test_flujo_del_lab05_llega_a_puntos_acreditados():
    solicitud = nueva_solicitud()
    with pytest.raises(ErrorValidacion, match="geocodificada"):
        solicitud.marcar_pendiente()
    assert solicitud.estado is None

    solicitud.asignar_coordenadas(Coordenadas(-16.4, -71.5))
    solicitud.marcar_pendiente()
    with pytest.raises(ErrorValidacion, match="disponible"):
        solicitud.asignar("R01", disponible=False)
    assert solicitud.estado is EstadoSolicitud.PENDIENTE

    solicitud.asignar("R01")
    assert solicitud.estado is EstadoSolicitud.ASIGNADA
    solicitud.registrar_recojo()
    assert solicitud.estado is EstadoSolicitud.RECOGIDA

    with pytest.raises(ErrorValidacion, match="Pesaje inválido"):
        solicitud.registrar_pesaje(0)
    assert solicitud.estado is EstadoSolicitud.RECOGIDA
    assert solicitud.peso_real_kg is None

    solicitud.registrar_pesaje(1.25)
    assert solicitud.estado is EstadoSolicitud.PESADA
    with pytest.raises(ErrorValidacion, match="puntos"):
        solicitud.acreditar_puntos(-1)
    assert solicitud.estado is EstadoSolicitud.PESADA

    solicitud.acreditar_puntos(10)
    assert solicitud.estado is EstadoSolicitud.PUNTOS_ACREDITADOS
    assert solicitud.puntos == 10
    with pytest.raises(ErrorValidacion, match="PESADA"):
        solicitud.acreditar_puntos(20)
    assert solicitud.puntos == 10


def test_timeout_de_mapas_guarda_y_notifica_solicitud_rechazada():
    class MapasCaidos:
        def geocodificar(self, direccion):
            raise TimeoutError()

    class Repositorio:
        def guardar(self, solicitud):
            self.solicitud = solicitud

    class Notificaciones:
        def notificar_error_ubicacion(self, vecino_id, motivo):
            self.aviso = (vecino_id, motivo)

    servicio = SolicitarRecojoService(Repositorio(), MapasCaidos(), Notificaciones())
    solicitud = servicio.solicitar_recojo(
        "V01", "Dirección de prueba", [DetalleResiduo("PLASTICO", "Botella", 1.5)]
    )

    assert solicitud.estado is EstadoSolicitud.RECHAZADA
    assert servicio.repositorio.solicitud is solicitud
    assert servicio.notificacion.aviso == ("V01", solicitud.motivo_rechazo)
    with pytest.raises(ErrorValidacion):
        solicitud.marcar_pendiente()
    assert solicitud.estado is EstadoSolicitud.RECHAZADA
