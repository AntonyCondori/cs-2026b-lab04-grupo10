class LLMApiSimulada:
    """Simula un servicio de IA externo (ej. OpenAI o Claude)."""
    def __init__(self, fallas=0):
        self.fallas = fallas
        self.llamadas = 0

    def predecir_categoria(self, texto: str) -> dict:
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise TimeoutError("Conexión perdida con la IA")
        
        # Simulamos respuestas poco confiables de la IA
        texto_lower = texto.lower()
        if "botella" in texto_lower:
            return {"status": "ok", "result": "PLASTICO"}
        elif "bateria" in texto_lower:
            return {"status": "ok", "result": "PELIGROSO - S/ 50.00"} # IA inventando cosas
        return {"status": "ok", "result": "DESCONOCIDO"}

class WhatsAppSDK:
    """Simula un SDK de mensajería clásico."""
    def send(self, phone: str, message: str) -> bool:
        return True