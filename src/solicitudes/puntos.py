from abc import ABC, abstractmethod

# 1. STRATEGY (Puerto/Interfaz común)
class CalculadoraPuntos(ABC):
    @abstractmethod
    def calcular(self) -> int:
        pass

# Estrategias locales (Plástico y Vidrio)
class CalculadoraPlastico(CalculadoraPuntos):
    def calcular(self) -> int:
        return 10

class CalculadoraVidrio(CalculadoraPuntos):
    def calcular(self) -> int:
        return 15

# 2. ADAPTER (Traduce la API externa del MINAM a nuestra interfaz CalculadoraPuntos)
class MinamCartonAdapter(CalculadoraPuntos):
    def __init__(self, api):
        self._api = api

    def calcular(self) -> int:
        return self._api.consultar_puntos("carton")

# 3. FACTORY (Registro dinámico para instanciar la estrategia adecuada)
class FabricaCalculadoras:
    def __init__(self):
        self._creadores = {}

    def registrar(self, categoria: str, creador):
        self._creadores[categoria] = creador

    def crear(self, categoria: str) -> CalculadoraPuntos:
        if categoria not in self._creadores:
            raise ValueError(f"Categoría no soportada: {categoria}")
        return self._creadores[categoria]()
