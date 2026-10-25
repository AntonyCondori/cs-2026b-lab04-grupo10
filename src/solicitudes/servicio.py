from src.solicitudes.antes.servicio import Solicitud
from src.solicitudes.externos import LLMApiSimulada, WhatsAppSDK, MinamPuntosAPI
from src.solicitudes.puntos import (
    FabricaCalculadoras, CalculadoraPlastico, CalculadoraVidrio, MinamCartonAdapter
)

class ServicioSolicitudes:
    def __init__(self, ia_api=None, ws_api=None, fabrica=None):
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

    def procesar_recojo(self, solicitud: Solicitud, campana: str = "NINGUNA") -> str:
        
        if solicitud.estado != "PENDIENTE":
            if solicitud.estado == "COMPLETADO":
                raise ValueError("La solicitud ya fue procesada")
            elif solicitud.estado == "CANCELADO":
                raise ValueError("No se puede procesar una solicitud cancelada")
            else:
                raise ValueError("Estado no válido")

        for intento in range(3):
            try:
                respuesta_ia = self.ia.predecir_categoria(solicitud.descripcion_residuo)
                categoria = respuesta_ia["result"]
                break
            except TimeoutError:
                if intento == 2:
                    solicitud.estado = "CANCELADO"
                    return solicitud.estado

        if "S/" in categoria or "PELIGROSO" in categoria:
            raise ValueError("Guardrail: La IA devolvió datos prohibidos o precios inventados")

        calculadora = self.fabrica.crear(categoria)
        puntos_base = calculadora.calcular()

        if campana == "RECICLA_VERANO":
            puntos_base *= 2
        elif campana == "DIA_TIERRA":
            puntos_base += 50

        solicitud.puntos_asignados = puntos_base
        solicitud.estado = "COMPLETADO"

        mensaje = f"Hola {solicitud.usuario}, ganaste {puntos_base} puntos por tu reciclaje."
        self.whatsapp.send(solicitud.celular, mensaje)
        self.eventos.append(f"whatsapp: {solicitud.celular}: {puntos_base} puntos")
        self.eventos.append(f"log_auditoria: Solicitud {solicitud.id} completada")

        return solicitud.estado