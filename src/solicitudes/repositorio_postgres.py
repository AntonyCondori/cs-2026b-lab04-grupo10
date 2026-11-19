"""Persistencia de solicitudes para un distrito autorizado por la aplicación."""

from dataclasses import asdict

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from src.solicitudes.dominio import (
    Coordenadas, DetalleResiduo, Direccion, ErrorValidacion, EstadoSolicitud,
    Solicitud, SolicitudRepository,
)
from src.solicitudes.gestion_recojo import ConfirmacionRecojo


_SELECCION_SOLICITUD = """
    SELECT * FROM solicitudes_recojo WHERE distrito_id = %s AND solicitud_id = %s
"""


def _solicitud_desde_fila(fila):
    datos_direccion = fila["direccion"]
    coordenadas = datos_direccion["coordenadas"]
    return Solicitud(
        id=fila["solicitud_id"],
        vecino_id=fila["vecino_id"],
        direccion=Direccion(datos_direccion["texto"], Coordenadas(**coordenadas) if coordenadas else None),
        detalles=[DetalleResiduo(**detalle) for detalle in fila["detalles"]],
        estado=EstadoSolicitud(fila["estado"]),
        motivo_rechazo=fila["motivo_rechazo"],
        fecha_creacion=fila["fecha_creacion"],
        reciclador_id=fila["reciclador_id"],
        peso_real_kg=fila["peso_real_kg"],
        puntos=fila["puntos"],
    )


class RepositorioSolicitudesPostgres(SolicitudRepository):
    def __init__(self, dsn: str, distrito_autorizado: str):
        if not distrito_autorizado.strip():
            raise ValueError("Se requiere un distrito autorizado")
        self._dsn = dsn
        self._distrito_id = distrito_autorizado

    def _conexion(self):
        return psycopg.connect(self._dsn, row_factory=dict_row)

    def guardar(self, solicitud: Solicitud) -> None:
        with self._conexion() as conexion:
            conexion.execute(
                """INSERT INTO solicitudes_recojo (
                       distrito_id, solicitud_id, vecino_id, direccion, detalles, estado,
                       motivo_rechazo, fecha_creacion, reciclador_id, peso_real_kg, puntos
                   ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (self._distrito_id, solicitud.id, solicitud.vecino_id, Jsonb(asdict(solicitud.direccion)),
                 Jsonb([asdict(detalle) for detalle in solicitud.detalles]), solicitud.estado.value,
                 solicitud.motivo_rechazo, solicitud.fecha_creacion, solicitud.reciclador_id,
                 solicitud.peso_real_kg, solicitud.puntos),
            )

    def obtener(self, solicitud_id: str) -> Solicitud:
        with self._conexion() as conexion:
            return self._obtener(conexion, solicitud_id)

    def listar(self) -> list[Solicitud]:
        with self._conexion() as conexion:
            filas = conexion.execute(
                "SELECT * FROM solicitudes_recojo WHERE distrito_id = %s ORDER BY solicitud_id",
                (self._distrito_id,),
            ).fetchall()
        return [_solicitud_desde_fila(fila) for fila in filas]

    def _obtener(self, conexion, solicitud_id, *, para_actualizar=False):
        consulta = _SELECCION_SOLICITUD + " FOR UPDATE" if para_actualizar else _SELECCION_SOLICITUD
        fila = conexion.execute(consulta, (self._distrito_id, solicitud_id)).fetchone()
        if fila is None:
            raise PermissionError("Solicitud no disponible")
        return _solicitud_desde_fila(fila)

    def _guardar_estado(self, conexion, solicitud):
        conexion.execute(
            """UPDATE solicitudes_recojo SET estado = %s, reciclador_id = %s, peso_real_kg = %s, puntos = %s
               WHERE distrito_id = %s AND solicitud_id = %s""",
            (solicitud.estado.value, solicitud.reciclador_id, solicitud.peso_real_kg, solicitud.puntos,
             self._distrito_id, solicitud.id),
        )

    def actualizar(self, solicitud_id, operar) -> Solicitud:
        with self._conexion() as conexion:
            solicitud = self._obtener(conexion, solicitud_id, para_actualizar=True)
            operar(solicitud)
            self._guardar_estado(conexion, solicitud)
            return solicitud

    def confirmar(self, solicitud_id, clave, peso_kg, operar) -> ConfirmacionRecojo:
        with self._conexion() as conexion:
            solicitud = self._obtener(conexion, solicitud_id, para_actualizar=True)
            previo = conexion.execute(
                """SELECT c.clave, c.peso_kg, a.puntos
                   FROM confirmaciones_recojo AS c JOIN abonos_recojo AS a USING (distrito_id, solicitud_id)
                   WHERE c.distrito_id = %s AND c.solicitud_id = %s""",
                (self._distrito_id, solicitud_id),
            ).fetchone()
            if previo:
                if (previo["clave"], previo["peso_kg"]) != (clave, peso_kg):
                    raise ErrorValidacion("Conflicto con la confirmación existente")
                return ConfirmacionRecojo(solicitud_id, previo["peso_kg"], previo["puntos"])

            nuevo = conexion.execute(
                """INSERT INTO confirmaciones_recojo (distrito_id, solicitud_id, clave, peso_kg)
                   VALUES (%s, %s, %s, %s) ON CONFLICT (distrito_id, clave) DO NOTHING RETURNING clave""",
                (self._distrito_id, solicitud_id, clave, peso_kg),
            ).fetchone()
            if nuevo is None:
                raise ErrorValidacion("La clave ya corresponde a otra solicitud")

            puntos = operar(solicitud)
            self._guardar_estado(conexion, solicitud)
            conexion.execute(
                "INSERT INTO abonos_recojo (distrito_id, solicitud_id, puntos) VALUES (%s, %s, %s)",
                (self._distrito_id, solicitud_id, puntos),
            )
            return ConfirmacionRecojo(solicitud_id, peso_kg, puntos)
