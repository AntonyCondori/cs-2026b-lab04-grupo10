"""Punto de arranque del módulo Solicitudes (ADR-006).

Aquí se registran las reglas de puntos y las campañas nuevas, una línea por
regla. Así servicio.py, estados.py, puntos.py y decoradores.py no se modifican.

Ejemplos (descomentar o copiar en registrar_reglas):
    servicio.fabrica.registrar("METAL", CalculadoraMetal)
    servicio.campanas.registrar("FIESTAS_AQP", lambda c: ConBonoFijo(c, 30))
"""
from src.solicitudes.dominio import SolicitarRecojoService
from src.solicitudes.gestion_recojo import GestionarRecojoService
from src.solicitudes.servicio import ServicioSolicitudes


def registrar_reglas(servicio: ServicioSolicitudes) -> None:
    """Registra aquí las reglas nuevas (una línea por regla)."""


def crear_servicio(**dependencias) -> ServicioSolicitudes:
    servicio = ServicioSolicitudes(**dependencias)
    registrar_reglas(servicio)
    return servicio


def crear_ciclo_postgres(
    dsn: str, distrito_autorizado: str, mapas, notificacion
) -> tuple[SolicitarRecojoService, GestionarRecojoService]:
    """Ensambla los servicios con el distrito del contexto autorizado por el servidor."""
    from src.solicitudes.repositorio_postgres import RepositorioSolicitudesPostgres

    repositorio = RepositorioSolicitudesPostgres(dsn, distrito_autorizado)
    fabrica = crear_servicio().fabrica

    def calcular_puntos(solicitud):
        return sum(fabrica.crear(detalle.tipo).calcular() for detalle in solicitud.detalles)

    return (
        SolicitarRecojoService(repositorio, mapas, notificacion),
        GestionarRecojoService(repositorio, calcular_puntos),
    )
