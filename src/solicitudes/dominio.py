"""Dominio del módulo Solicitudes de recojo (EcoRecicla AQP) - HU-01.

Esqueleto generado con IA a partir de docs/design/clases.puml (Prompt IA 2)
y revisado por el equipo. Los nombres de operaciones usan snake_case
(equivalencia con camelCase del diagrama documentada en round-trip.md, C5).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from math import isfinite
from uuid import uuid4


class EstadoSolicitud(Enum):
    PENDIENTE = "PENDIENTE"
    ASIGNADA = "ASIGNADA"
    RECOGIDA = "RECOGIDA"
    PESADA = "PESADA"
    PUNTOS_ACREDITADOS = "PUNTOS_ACREDITADOS"
    RECHAZADA = "RECHAZADA"


class ErrorValidacion(Exception):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class ErrorGeocodificacion(Exception):
    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


@dataclass
class Coordenadas:
    latitud: float
    longitud: float


@dataclass
class Direccion:
    texto: str
    coordenadas: Coordenadas | None = None  # 0..1 en el diagrama

    def esta_geocodificada(self) -> bool:
        return self.coordenadas is not None


@dataclass
class DetalleResiduo:
    tipo: str
    descripcion: str
    peso_kg: float

    def es_valido(self) -> bool:
        return bool(self.tipo) and self.peso_kg > 0


@dataclass
class Solicitud:
    vecino_id: str
    direccion: Direccion
    detalles: list[DetalleResiduo] = field(default_factory=list)  # 1..*
    # None = recién creada, aún sin estado (el diagrama no define estado inicial)
    estado: EstadoSolicitud | None = None
    motivo_rechazo: str | None = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid4()))
    # Atributos propuestos para cerrar C2 (ciclo de vida completo):
    reciclador_id: str | None = None
    peso_real_kg: float | None = None
    puntos: int | None = None

    @staticmethod
    def crear(vecino_id: str, direccion: Direccion,
              detalles: list[DetalleResiduo]) -> Solicitud:
        solicitud = Solicitud(vecino_id=vecino_id, direccion=direccion,
                              detalles=list(detalles))
        solicitud.validar_detalles()
        return solicitud

    def agregar_detalle(self, detalle: DetalleResiduo) -> None:
        self.detalles.append(detalle)

    def validar_detalles(self) -> None:
        # Criterio 3: lista vacía o peso 0 -> error de validación
        if not self.detalles or not all(d.es_valido() for d in self.detalles):
            raise ErrorValidacion("Debe ingresar al menos un residuo con peso mayor a 0")

    def asignar_coordenadas(self, coordenadas: Coordenadas) -> None:
        self.direccion.coordenadas = coordenadas

    def marcar_pendiente(self) -> None:
        _ESTADOS_CICLO[self.estado].marcar_pendiente(self)

    def rechazar(self, motivo: str) -> None:
        _ESTADOS_CICLO[self.estado].rechazar(self, motivo)

    def obtener_peso_total(self) -> float:
        return sum(d.peso_kg for d in self.detalles)

    def asignar(self, reciclador_id: str, *, disponible: bool = True) -> None:
        _ESTADOS_CICLO[self.estado].asignar(self, reciclador_id, disponible)

    def registrar_recojo(self) -> None:
        _ESTADOS_CICLO[self.estado].registrar_recojo(self)

    def registrar_pesaje(self, peso_kg: float) -> None:
        _ESTADOS_CICLO[self.estado].registrar_pesaje(self, peso_kg)

    def acreditar_puntos(self, puntos: int) -> None:
        _ESTADOS_CICLO[self.estado].acreditar_puntos(self, puntos)


class TransicionesSolicitud:
    """Por defecto, el estado actual impide todas las transiciones."""

    def marcar_pendiente(self, solicitud: Solicitud) -> None:
        raise ErrorValidacion("Solo una solicitud nueva puede quedar PENDIENTE")

    def rechazar(self, solicitud: Solicitud, motivo: str) -> None:
        raise ErrorValidacion("Solo una solicitud nueva puede rechazarse por ubicación")

    def asignar(self, solicitud: Solicitud, reciclador_id: str, disponible: bool) -> None:
        raise ErrorValidacion("Solo una solicitud PENDIENTE puede asignarse")

    def registrar_recojo(self, solicitud: Solicitud) -> None:
        raise ErrorValidacion("Solo una solicitud ASIGNADA puede recogerse")

    def registrar_pesaje(self, solicitud: Solicitud, peso_kg: float) -> None:
        raise ErrorValidacion("Solo una solicitud RECOGIDA puede pesarse")

    def acreditar_puntos(self, solicitud: Solicitud, puntos: int) -> None:
        raise ErrorValidacion("Solo una solicitud PESADA acredita puntos")


class NuevaSolicitud(TransicionesSolicitud):
    def marcar_pendiente(self, solicitud: Solicitud) -> None:
        if not solicitud.direccion.esta_geocodificada():
            raise ErrorValidacion("La dirección no está geocodificada")
        solicitud.estado = EstadoSolicitud.PENDIENTE

    def rechazar(self, solicitud: Solicitud, motivo: str) -> None:
        solicitud.estado = EstadoSolicitud.RECHAZADA
        solicitud.motivo_rechazo = motivo


class SolicitudPendiente(TransicionesSolicitud):
    def asignar(self, solicitud: Solicitud, reciclador_id: str, disponible: bool) -> None:
        if not disponible or not reciclador_id:
            raise ErrorValidacion("Se requiere un reciclador disponible")
        solicitud.reciclador_id = reciclador_id
        solicitud.estado = EstadoSolicitud.ASIGNADA


class SolicitudAsignada(TransicionesSolicitud):
    def registrar_recojo(self, solicitud: Solicitud) -> None:
        solicitud.estado = EstadoSolicitud.RECOGIDA


class SolicitudRecogida(TransicionesSolicitud):
    def registrar_pesaje(self, solicitud: Solicitud, peso_kg: float) -> None:
        if not isfinite(peso_kg) or peso_kg <= 0:
            raise ErrorValidacion("Pesaje inválido")
        solicitud.peso_real_kg = peso_kg
        solicitud.estado = EstadoSolicitud.PESADA


class SolicitudPesada(TransicionesSolicitud):
    def acreditar_puntos(self, solicitud: Solicitud, puntos: int) -> None:
        if puntos < 0:
            raise ErrorValidacion("Los puntos deben ser mayores o iguales a cero")
        solicitud.puntos = puntos
        solicitud.estado = EstadoSolicitud.PUNTOS_ACREDITADOS


_ESTADOS_CICLO = {
    None: NuevaSolicitud(),
    EstadoSolicitud.PENDIENTE: SolicitudPendiente(),
    EstadoSolicitud.ASIGNADA: SolicitudAsignada(),
    EstadoSolicitud.RECOGIDA: SolicitudRecogida(),
    EstadoSolicitud.PESADA: SolicitudPesada(),
    EstadoSolicitud.PUNTOS_ACREDITADOS: TransicionesSolicitud(),
    EstadoSolicitud.RECHAZADA: TransicionesSolicitud(),
}


# --------------------------- Puertos (interfaces) ---------------------------
class SolicitudRepository(ABC):
    @abstractmethod
    def guardar(self, solicitud: Solicitud) -> None: ...


class MapasGeocodificacionPort(ABC):
    @abstractmethod
    def geocodificar(self, direccion: str) -> Coordenadas: ...


class NotificacionPort(ABC):
    @abstractmethod
    def notificar_error_ubicacion(self, vecino_id: str, motivo: str) -> None: ...


# ------------------------------- Adaptador ---------------------------------
class GoogleMapsAdapter(MapasGeocodificacionPort):
    def geocodificar(self, direccion: str) -> Coordenadas:
        raise NotImplementedError("Integrar con la API de Google Maps")


# ---------------------------- Servicio de aplicación -----------------------
@dataclass
class SolicitarRecojoService:
    repositorio: SolicitudRepository
    mapas: MapasGeocodificacionPort
    notificacion: NotificacionPort

    def solicitar_recojo(self, vecino_id: str, texto_direccion: str,
                         detalles: list[DetalleResiduo]) -> Solicitud:
        direccion = Direccion(texto=texto_direccion)
        solicitud = Solicitud.crear(vecino_id, direccion, detalles)  # ErrorValidacion
        try:
            coordenadas = self.mapas.geocodificar(texto_direccion)
        except (ErrorGeocodificacion, TimeoutError):
            solicitud.rechazar("Dirección inválida")
            self.repositorio.guardar(solicitud)
            # En el diagrama de secuencia este mensaje es asíncrono (->>)
            self.notificacion.notificar_error_ubicacion(vecino_id, "Dirección inválida")
            return solicitud
        solicitud.asignar_coordenadas(coordenadas)
        solicitud.marcar_pendiente()
        self.repositorio.guardar(solicitud)
        return solicitud
