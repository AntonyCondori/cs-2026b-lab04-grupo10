from src.solicitudes.ia import crear_clasificador
from src.solicitudes.estados import Solicitud
from src.solicitudes.externos import LLMApiSimulada, WhatsAppSDK, MinamPuntosAPI
from src.solicitudes.puntos import (
    FabricaCalculadoras, CalculadoraPlastico, CalculadoraVidrio, MinamCartonAdapter
)
from src.solicitudes.decoradores import campanas_por_defecto
from src.solicitudes.eventos import PublicadorEventos, NotificadorWhatsApp, AuditoriaSolicitudes


class ServicioSolicitudes:
    def __init__(self, ia_api=None, ws_api=None, fabrica=None, campanas=None, publicador=None):
        self.ia = ia_api or LLMApiSimulada()
        self.clasificador = crear_clasificador(api=self.ia)
        self.whatsapp = ws_api or WhatsAppSDK()
        self.eventos = []

        if fabrica is None:
            self.fabrica = FabricaCalculadoras()
            self.fabrica.registrar("PLASTICO", CalculadoraPlastico)
            self.fabrica.registrar("VIDRIO", CalculadoraVidrio)
            self.fabrica.registrar("CARTON", lambda: MinamCartonAdapter(MinamPuntosAPI()))
        else:
            self.fabrica = fabrica

        self.campanas = campanas or campanas_por_defecto()

        if publicador is None:
            self.publicador = PublicadorEventos()
            self.publicador.suscribir("solicitud_completada", NotificadorWhatsApp(self.whatsapp, self.eventos))
            self.publicador.suscribir("solicitud_completada", AuditoriaSolicitudes(self.eventos))
        else:
            self.publicador = publicador

    def procesar_recojo(self, solicitud: Solicitud, campana: str = "NINGUNA") -> str:
        solicitud.iniciar()  # STATE: solo una solicitud PENDIENTE puede procesarse

        for intento in range(3):
            try:
                categoria = self.clasificador.clasificar(solicitud.descripcion_residuo)
                break
            except TimeoutError:
                if intento == 2:
                    solicitud.cancelar()  # STATE
                    return solicitud.estado

        calculadora = self.campanas.aplicar(campana, self.fabrica.crear(categoria))  # DECORATOR
        puntos = calculadora.calcular()

        solicitud.completar(puntos)  # STATE

        self.publicador.publicar("solicitud_completada", {  # OBSERVER
            "id": solicitud.id, "usuario": solicitud.usuario,
            "celular": solicitud.celular, "puntos": puntos})

        return solicitud.estado
