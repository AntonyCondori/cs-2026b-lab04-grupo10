from abc import ABC, abstractmethod


class Guardrail(ABC):
    def __init__(self, siguiente=None):
        self.siguiente = siguiente

    def validar(self, categoria):
        self.comprobar(categoria)

        if self.siguiente is not None:
            self.siguiente.validar(categoria)

    @abstractmethod
    def comprobar(self, categoria):
        pass


class FormatoValido(Guardrail):
    def comprobar(self, categoria):
        if not isinstance(categoria, str) or not categoria.strip():
            raise ValueError("Guardrail: categoria vacia o formato invalido")


class SinPrecios(Guardrail):
    def comprobar(self, categoria):
        if "S/" in categoria.upper():
            raise ValueError("Guardrail: la IA incluyo un precio")


class SinPeligrosos(Guardrail):
    def comprobar(self, categoria):
        if "PELIGROSO" in categoria.upper():
            raise ValueError("Guardrail: residuo peligroso fuera del flujo comun")


def crear_guardrails():
    return FormatoValido(SinPrecios(SinPeligrosos()))
