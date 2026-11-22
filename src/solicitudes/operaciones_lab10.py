"""Comportamiento inicial de los tres issues del laboratorio 10."""


class SaldoVecinos:
    def __init__(self):
        self.saldos = {}
        self.solicitudes_acreditadas = set()

    def actualizar(self, evento, datos):
        solicitud_id = datos["id"]
        if solicitud_id in self.solicitudes_acreditadas:
            return

        vecino = datos["usuario"]
        saldo_anterior = self.saldos.get(vecino, 0)
        self.saldos[vecino] = saldo_anterior + datos["puntos"]
        self.solicitudes_acreditadas.add(solicitud_id)


def seleccionar_para_ruta(solicitudes):
    from src.solicitudes.estados import Cancelado

    return [solicitud for solicitud in solicitudes if solicitud.estado != Cancelado.nombre]


def calcular_puntos_distrito(fabrica, material, distrito):
    from src.solicitudes.decoradores import ConBonoFijo

    calculadora = fabrica.crear(material)
    if material == "PLASTICO" and distrito == "D01":
        calculadora = ConBonoFijo(calculadora, 5)
    return calculadora.calcular()