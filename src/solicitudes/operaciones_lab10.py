"""Comportamiento inicial de los tres issues del laboratorio 10."""


class SaldoVecinos:
    def __init__(self):
        self.saldos = {}

    def actualizar(self, evento, datos):
        vecino = datos["usuario"]
        saldo_anterior = self.saldos.get(vecino, 0)
        self.saldos[vecino] = saldo_anterior + datos["puntos"]


def seleccionar_para_ruta(solicitudes):
    return list(solicitudes)


def calcular_puntos_distrito(fabrica, material, distrito):
    return fabrica.crear(material).calcular()