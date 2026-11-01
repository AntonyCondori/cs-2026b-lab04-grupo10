"""QA-03: prototipo de aislamiento por distrito, sin API ni SQL real."""
from dataclasses import dataclass, replace
import json


@dataclass(frozen=True)
class Contexto:
    # Se recibe del servidor tras autenticar y autorizar, no del formulario.
    distrito_id: str

    def __post_init__(self):
        if not self.distrito_id or not self.distrito_id.strip():
            raise ValueError("Falta contexto de distrito")


@dataclass(frozen=True)
class FilaSolicitud:
    id: int
    distrito_id: str
    puntos: int


class RepositorioDistrital:
    def __init__(self, filas):
        self._filas = {(f.distrito_id, f.id): f for f in filas}

    def listar(self, contexto):
        return [f for f in self._filas.values()
                if f.distrito_id == contexto.distrito_id]

    def obtener(self, contexto, distrito_consultado, solicitud_id):
        # No se devuelve ningun dato antes de comprobar el distrito.
        if distrito_consultado != contexto.distrito_id:
            raise PermissionError("Solicitud no disponible")
        fila = self._filas.get((contexto.distrito_id, solicitud_id))
        if fila is None:
            raise PermissionError("Solicitud no disponible")
        return fila

    def actualizar(self, contexto, distrito_consultado, solicitud_id, puntos):
        fila = self.obtener(contexto, distrito_consultado, solicitud_id)
        if puntos < 0:
            raise ValueError("Puntos invalidos")
        nueva = replace(fila, puntos=puntos)
        self._filas[(fila.distrito_id, fila.id)] = nueva
        return nueva


class RepositorioSinFiltro(RepositorioDistrital):
    """Linea base experimental insegura; no usar en la aplicacion."""
    def obtener(self, contexto, distrito_consultado, solicitud_id):
        return self._filas[(distrito_consultado, solicitud_id)]


def datos_prueba():
    return [FilaSolicitud(1, "D01", 10), FilaSolicitud(1, "D02", 20)]


def simular(estrategia="con_filtro", intentos=100):
    clases = {"sin_filtro": RepositorioSinFiltro,
              "con_filtro": RepositorioDistrital}
    if estrategia not in clases or intentos < 1:
        raise ValueError("Parametros invalidos")
    repo = clases[estrategia](datos_prueba())
    expuestas, denegados = 0, 0
    for i in range(intentos):
        propio, ajeno = ("D01", "D02") if i % 2 == 0 else ("D02", "D01")
        try:
            fila = repo.obtener(Contexto(propio), ajeno, 1)
            expuestas += int(fila.distrito_id != propio)
        except PermissionError:
            denegados += 1
    return {"intentos": intentos, "denegados": denegados,
            "filas_de_otro_distrito": expuestas}


if __name__ == "__main__":
    for estrategia in ("sin_filtro", "con_filtro"):
        print(estrategia, json.dumps(simular(estrategia)))
