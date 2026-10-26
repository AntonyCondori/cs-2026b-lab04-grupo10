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
                respuesta_ia = self.ia.predecir_categoria(solicitud.descripcion_residuo)
                categoria = respuesta_ia["result"]
                break
            except TimeoutError:
                if intento == 2:
                    solicitud.cancelar()
                    return solicitud.estado

        if "S/" in categoria or "PELIGROSO" in categoria:
            raise ValueError("Guardrail: La IA devolvió datos prohibidos o precios inventados")

        calculadora = self.campanas.aplicar(campana, self.fabrica.crear(categoria))  # DECORATOR
        puntos = calculadora.calcular()

        solicitud.completar(puntos)  # STATE

        self.publicador.publicar("solicitud_completada", {  # OBSERVER
            "id": solicitud.id, "usuario": solicitud.usuario,
            "celular": solicitud.celular, "puntos": puntos})

        return solicitud.estado
