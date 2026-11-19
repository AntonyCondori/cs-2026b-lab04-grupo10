"""E4 - Patrón Observer: el servicio publica eventos y no conoce a los interesados."""
from abc import ABC, abstractmethod


class Suscriptor(ABC):
    @abstractmethod
    def actualizar(self, evento: str, datos: dict) -> None: ...


class PublicadorEventos:
    """Sujeto observable. Agregar un interesado = suscribirlo, sin tocar el servicio."""

    def __init__(self):
        self._suscriptores = {}

    def suscribir(self, evento: str, suscriptor: Suscriptor) -> None:
        self._suscriptores.setdefault(evento, []).append(suscriptor)

    def publicar(self, evento: str, datos: dict) -> None:
        for s in self._suscriptores.get(evento, []):
            s.actualizar(evento, datos)


class WhatsAppSDKAdapter:
    """Adapta el SDK existente al envío que consume el observador."""

    def __init__(self, sdk):
        self._sdk = sdk

    def enviar(self, destinatario: str, mensaje: str) -> bool:
        return self._sdk.send(destinatario, mensaje)


class NotificadorWhatsApp(Suscriptor):
    def __init__(self, mensajeria, bandeja: list):
        self._mensajeria = mensajeria
        self._bandeja = bandeja

    def actualizar(self, evento, datos):
        mensaje = f"Hola {datos['usuario']}, ganaste {datos['puntos']} puntos por tu reciclaje."
        self._mensajeria.enviar(datos["celular"], mensaje)
        self._bandeja.append(f"whatsapp: {datos['celular']}: {datos['puntos']} puntos")


class AuditoriaSolicitudes(Suscriptor):
    def __init__(self, bandeja: list):
        self._bandeja = bandeja

    def actualizar(self, evento, datos):
        self._bandeja.append(f"log_auditoria: Solicitud {datos['id']} completada")
