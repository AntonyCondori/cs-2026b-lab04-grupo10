"""E3 - Patrón State para el ciclo de vida de la solicitud de recojo.

La clase base PROHÍBE todas las transiciones; cada estado concreto redefine
solo las que están permitidas. Una transición inválida es imposible por
construcción (no hay if/elif sobre el nombre del estado).

Máquina de estados del flujo `procesar_recojo`:

    PENDIENTE --completar(puntos)--> COMPLETADO
    PENDIENTE --cancelar()---------> CANCELADO
"""


class EstadoSolicitud:
    nombre = "?"
    mensaje_iniciar = "Estado no válido"

    def iniciar(self, solicitud):
        """Valida que la solicitud pueda procesarse."""
        raise ValueError(self.mensaje_iniciar)

    def completar(self, solicitud, puntos: int):
        raise ValueError(f"No se puede completar una solicitud {self.nombre}")

    def cancelar(self, solicitud):
        raise ValueError(f"No se puede cancelar una solicitud {self.nombre}")


class Pendiente(EstadoSolicitud):
    nombre = "PENDIENTE"

    def iniciar(self, solicitud):
        return None  # única situación en la que se puede procesar

    def completar(self, solicitud, puntos: int):
        solicitud.puntos_asignados = puntos
        solicitud.cambiar_a(Completado())

    def cancelar(self, solicitud):
        solicitud.cambiar_a(Cancelado())


class Completado(EstadoSolicitud):
    nombre = "COMPLETADO"
    mensaje_iniciar = "La solicitud ya fue procesada"


class Cancelado(EstadoSolicitud):
    nombre = "CANCELADO"
    mensaje_iniciar = "No se puede procesar una solicitud cancelada"


class EstadoDesconocido(EstadoSolicitud):
    """Cualquier nombre de estado que no esté en el diagrama."""

    def __init__(self, nombre: str):
        self.nombre = nombre


_ESTADOS = {e.nombre: e for e in (Pendiente, Completado, Cancelado)}


def estado_desde_nombre(nombre: str) -> EstadoSolicitud:
    clase = _ESTADOS.get(nombre)
    return clase() if clase else EstadoDesconocido(nombre)


class Solicitud:
    """Contexto del patrón State: delega el comportamiento en su estado."""

    def __init__(self, id: int, usuario: str, celular: str,
                 descripcion_residuo: str, estado: str = "PENDIENTE",
                 puntos_asignados: int = 0):
        self.id = id
        self.usuario = usuario
        self.celular = celular
        self.descripcion_residuo = descripcion_residuo
        self.puntos_asignados = puntos_asignados
        self._estado = estado_desde_nombre(estado)

    @property
    def estado(self) -> str:
        return self._estado.nombre

    def cambiar_a(self, nuevo: EstadoSolicitud) -> None:
        self._estado = nuevo

    def iniciar(self) -> None:
        self._estado.iniciar(self)

    def completar(self, puntos: int) -> None:
        self._estado.completar(self, puntos)

    def cancelar(self) -> None:
        self._estado.cancelar(self)
