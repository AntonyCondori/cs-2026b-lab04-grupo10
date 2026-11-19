"""Operaciones de aplicación del ciclo de recojo después de registrar la solicitud."""

from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite
from typing import Protocol

from src.solicitudes.dominio import ErrorValidacion, EstadoSolicitud, Solicitud


@dataclass(frozen=True)
class ConfirmacionRecojo:
    solicitud_id: str
    peso_kg: float
    puntos: int


class RepositorioCicloRecojo(Protocol):
    def obtener(self, solicitud_id: str) -> Solicitud: ...

    def listar(self) -> list[Solicitud]: ...

    def actualizar(self, solicitud_id: str, operar: Callable[[Solicitud], None]) -> Solicitud: ...

    def confirmar(
        self, solicitud_id: str, clave: str, peso_kg: float, operar: Callable[[Solicitud], int]
    ) -> ConfirmacionRecojo: ...


@dataclass
class GestionarRecojoService:
    repositorio: RepositorioCicloRecojo
    calcular_puntos: Callable[[Solicitud], int]

    def obtener(self, solicitud_id: str) -> Solicitud:
        return self.repositorio.obtener(solicitud_id)

    def listar(self) -> list[Solicitud]:
        return self.repositorio.listar()

    def asignar(self, solicitud_id: str, reciclador_id: str, *, disponible: bool = True) -> Solicitud:
        return self.repositorio.actualizar(
            solicitud_id, lambda solicitud: solicitud.asignar(reciclador_id, disponible=disponible)
        )

    def registrar_recojo(self, solicitud_id: str) -> Solicitud:
        return self.repositorio.actualizar(solicitud_id, Solicitud.registrar_recojo)

    def registrar_pesaje(self, solicitud_id: str, peso_kg: float) -> Solicitud:
        return self.repositorio.actualizar(solicitud_id, lambda solicitud: solicitud.registrar_pesaje(peso_kg))

    def confirmar_recojo(self, solicitud_id: str, clave: str, peso_kg: float) -> ConfirmacionRecojo:
        if not clave.strip() or not isfinite(peso_kg) or peso_kg <= 0:
            raise ErrorValidacion("Se requiere una clave de confirmación y un peso válido")

        def acreditar(solicitud: Solicitud) -> int:
            if solicitud.estado is EstadoSolicitud.ASIGNADA:
                solicitud.registrar_recojo()
            if solicitud.estado is EstadoSolicitud.RECOGIDA:
                solicitud.registrar_pesaje(peso_kg)
            if solicitud.estado is not EstadoSolicitud.PESADA:
                raise ErrorValidacion("La solicitud debe estar lista para acreditar el pesaje")
            if solicitud.peso_real_kg != peso_kg:
                raise ErrorValidacion("El peso debe coincidir con el pesaje registrado")
            puntos = self.calcular_puntos(solicitud)
            solicitud.acreditar_puntos(puntos)
            return puntos

        return self.repositorio.confirmar(solicitud_id, clave, peso_kg, acreditar)
