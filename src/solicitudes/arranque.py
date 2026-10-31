"""Punto de arranque del módulo Solicitudes (ADR-006).

Aquí se registran las reglas de puntos y las campañas nuevas, una línea por
regla. Así servicio.py, estados.py, puntos.py y decoradores.py no se modifican.

Ejemplos (descomentar o copiar en registrar_reglas):
    servicio.fabrica.registrar("METAL", CalculadoraMetal)
    servicio.campanas.registrar("FIESTAS_AQP", lambda c: ConBonoFijo(c, 30))
"""
from src.solicitudes.servicio import ServicioSolicitudes


def registrar_reglas(servicio: ServicioSolicitudes) -> None:
    """Registra aquí las reglas nuevas (una línea por regla)."""


def crear_servicio(**dependencias) -> ServicioSolicitudes:
    servicio = ServicioSolicitudes(**dependencias)
    registrar_reglas(servicio)
    return servicio
