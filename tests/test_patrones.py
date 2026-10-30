import pytest
from src.solicitudes.estados import (
    Solicitud, Pendiente, Completado, Cancelado, EstadoDesconocido,
)
from src.solicitudes.servicio import ServicioSolicitudes
from src.solicitudes.puntos import CalculadoraPuntos, CalculadoraPlastico
from src.solicitudes.decoradores import (
    ConMultiplicador, ConBonoFijo, RegistroCampanas,
)
from src.solicitudes.eventos import PublicadorEventos, Suscriptor


def nueva_solicitud(descripcion="botella de plastico", estado="PENDIENTE"):
    return Solicitud(id=1, usuario="Juan", celular="999888777",
                     descripcion_residuo=descripcion, estado=estado)


# ---------------- E2: Strategy + Adapter + Factory ----------------
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


# ---------------- E3: State ----------------
def test_state_transicion_valida_pendiente_a_completado():
    s = nueva_solicitud()
    s.completar(10)
    assert s.estado == "COMPLETADO"
    assert s.puntos_asignados == 10


def test_state_transicion_valida_pendiente_a_cancelado():
    s = nueva_solicitud()
    s.cancelar()
    assert s.estado == "CANCELADO"


@pytest.mark.parametrize("estado, accion, args", [
    ("COMPLETADO", "completar", (10,)),
    ("COMPLETADO", "cancelar", ()),
    ("CANCELADO", "completar", (10,)),
    ("CANCELADO", "cancelar", ()),
])
def test_state_impide_transiciones_invalidas(estado, accion, args):
    s = nueva_solicitud(estado=estado)
    with pytest.raises(ValueError, match="No se puede"):
        getattr(s, accion)(*args)
    assert s.estado == estado  # una transición inválida no altera el estado


def test_state_no_se_puede_reprocesar_una_solicitud_completada():
    servicio = ServicioSolicitudes()
    s = nueva_solicitud()
    servicio.procesar_recojo(s)
    with pytest.raises(ValueError, match="ya fue procesada"):
        servicio.procesar_recojo(s)


def test_state_estado_desconocido_se_rechaza():
    s = nueva_solicitud(estado="ARCHIVADO")
    assert isinstance(s._estado, EstadoDesconocido)
    with pytest.raises(ValueError, match="Estado no válido"):
        s.iniciar()


def test_state_ia_caida_cancela_la_solicitud():
    class IACaida:
        def predecir_categoria(self, texto):
            raise TimeoutError("sin conexión")

    servicio = ServicioSolicitudes(ia_api=IACaida())
    s = nueva_solicitud()
    assert servicio.procesar_recojo(s) == "CANCELADO"
    assert servicio.eventos == []


# ---------------- E4: Observer ----------------
class SuscriptorEspia(Suscriptor):
    def __init__(self):
        self.recibidos = []

    def actualizar(self, evento, datos):
        self.recibidos.append((evento, datos["id"]))


def test_observer_nuevo_suscriptor_sin_tocar_el_servicio():
    servicio = ServicioSolicitudes()
    espia = SuscriptorEspia()
    servicio.publicador.suscribir("solicitud_completada", espia)

    servicio.procesar_recojo(nueva_solicitud())

    assert espia.recibidos == [("solicitud_completada", 1)]
    assert len(servicio.eventos) == 2  # WhatsApp y auditoría siguen funcionando


def test_observer_whatsapp_recibe_el_mensaje_correcto():
    class WhatsAppFalso:
        def __init__(self):
            self.enviados = []

        def send(self, phone, message):
            self.enviados.append((phone, message))
            return True

    ws = WhatsAppFalso()
    servicio = ServicioSolicitudes(ws_api=ws)
    servicio.procesar_recojo(nueva_solicitud())
    assert ws.enviados == [("999888777", "Hola Juan, ganaste 10 puntos por tu reciclaje.")]


def test_observer_no_notifica_si_la_solicitud_se_cancela():
    class IACaida:
        def predecir_categoria(self, texto):
            raise TimeoutError()

    servicio = ServicioSolicitudes(ia_api=IACaida())
    espia = SuscriptorEspia()
    servicio.publicador.suscribir("solicitud_completada", espia)
    servicio.procesar_recojo(nueva_solicitud())
    assert espia.recibidos == []


# ---------------- E4: Decorator ----------------
def test_decorator_campanas_se_pueden_apilar():
    calc = ConBonoFijo(ConMultiplicador(CalculadoraPlastico(), 2), 50)
    assert calc.calcular() == 70  # (10 * 2) + 50


def test_decorator_orden_de_aplicacion_importa():
    a = ConMultiplicador(ConBonoFijo(CalculadoraPlastico(), 50), 2)  # (10 + 50) * 2
    b = ConBonoFijo(ConMultiplicador(CalculadoraPlastico(), 2), 50)  # (10 * 2) + 50
    assert (a.calcular(), b.calcular()) == (120, 70)


def test_decorator_campana_nueva_sin_modificar_el_servicio():
    campanas = RegistroCampanas()
    campanas.registrar("TRIPLE", lambda c: ConMultiplicador(c, 3))
    servicio = ServicioSolicitudes(campanas=campanas)
    s = nueva_solicitud()
    servicio.procesar_recojo(s, campana="TRIPLE")
    assert s.puntos_asignados == 30


def test_decorator_campana_desconocida_no_cambia_los_puntos():
    servicio = ServicioSolicitudes()
    s = nueva_solicitud()
    servicio.procesar_recojo(s, campana="NO_EXISTE")
    assert s.puntos_asignados == 10
