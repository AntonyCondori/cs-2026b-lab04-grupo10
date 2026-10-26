from abc import ABC, abstractmethod

from src.solicitudes.guardrails import crear_guardrails


class ProveedorLLM(ABC):
    @abstractmethod
    def clasificar(self, descripcion: str) -> str:
        pass


class LLMSimuladoAdapter(ProveedorLLM):
    def __init__(self, api):
        self.api = api

    def clasificar(self, descripcion):
        respuesta = self.api.predecir_categoria(descripcion)

        if not isinstance(respuesta, dict) or respuesta.get("status") != "ok":
            raise ValueError("Guardrail: respuesta del proveedor invalida")

        return respuesta.get("result")


class ConGuardrails(ProveedorLLM):
    def __init__(self, interno, cadena):
        self.interno = interno
        self.cadena = cadena

    def clasificar(self, descripcion):
        categoria = self.interno.clasificar(descripcion)
        self.cadena.validar(categoria)
        return categoria


class ConCache(ProveedorLLM):
    def __init__(self, interno):
        self.interno = interno
        self.cache = {}

    def clasificar(self, descripcion):
        if descripcion not in self.cache:
            self.cache[descripcion] = self.interno.clasificar(descripcion)

        return self.cache[descripcion]


def crear_clasificador(api=None, proveedor=None):
    if proveedor is None:
        if api is None:
            raise ValueError("Debe indicar una API o un proveedor")

        proveedor = LLMSimuladoAdapter(api)

    return ConCache(
        ConGuardrails(proveedor, crear_guardrails())
    )
