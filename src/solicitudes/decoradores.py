"""E4 - Patrón Decorator: las campañas envuelven a una CalculadoraPuntos
sin modificarla y se pueden apilar."""
from src.solicitudes.puntos import CalculadoraPuntos


class ConMultiplicador(CalculadoraPuntos):
    def __init__(self, interna: CalculadoraPuntos, factor: int):
        self._interna, self._factor = interna, factor

    def calcular(self) -> int:
        return self._interna.calcular() * self._factor


class ConBonoFijo(CalculadoraPuntos):
    def __init__(self, interna: CalculadoraPuntos, bono: int):
        self._interna, self._bono = interna, bono

    def calcular(self) -> int:
        return self._interna.calcular() + self._bono


class RegistroCampanas:
    """Registro (no global) de campañas: nombre -> función que decora."""

    def __init__(self):
        self._campanas = {}

    def registrar(self, nombre: str, decorar) -> None:
        self._campanas[nombre] = decorar

    def aplicar(self, nombre: str, calculadora: CalculadoraPuntos) -> CalculadoraPuntos:
        decorar = self._campanas.get(nombre)
        return decorar(calculadora) if decorar else calculadora  # "NINGUNA" o desconocida: sin cambios


def campanas_por_defecto() -> RegistroCampanas:
    r = RegistroCampanas()
    r.registrar("RECICLA_VERANO", lambda c: ConMultiplicador(c, 2))
    r.registrar("DIA_TIERRA", lambda c: ConBonoFijo(c, 50))
    return r
