import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from uuid import uuid4

import pytest

from src.solicitudes.arranque import crear_ciclo_postgres
from src.solicitudes.dominio import Coordenadas, DetalleResiduo, ErrorValidacion, EstadoSolicitud


@pytest.fixture
def postgres():
    dsn = os.environ.get("ECORECICLA_POSTGRES_DSN")
    if not dsn:
        pytest.skip("Configura ECORECICLA_POSTGRES_DSN con una base de pruebas PostgreSQL")

    import psycopg
    from psycopg import sql
    from psycopg.conninfo import make_conninfo

    esquema = "recojos_" + uuid4().hex
    with psycopg.connect(dsn, autocommit=True) as admin:
        admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(esquema)))
        dsn_aislado = make_conninfo(dsn, options=f"-c search_path={esquema}")
        try:
            migracion = Path("src/solicitudes/sql/001_solicitudes.sql").read_text(encoding="utf-8")
            with psycopg.connect(dsn_aislado) as conexion:
                conexion.execute(migracion)
            yield dsn_aislado
        finally:
            admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(esquema)))


def servicios(dsn, distrito="D01"):
    class MapasFijos:
        def geocodificar(self, direccion):
            return Coordenadas(-16.4, -71.5)

    return crear_ciclo_postgres(dsn, distrito, MapasFijos(), None)


def registrar(alta, gestion, vecino="V01"):
    solicitud = alta.solicitar_recojo(vecino, "Dirección de prueba", [
        DetalleResiduo("PLASTICO", "Botella", 1.5),
    ])
    gestion.asignar(solicitud.id, "R01")
    return solicitud.id


def filas_confirmadas(dsn):
    import psycopg

    with psycopg.connect(dsn) as conexion:
        return conexion.execute(
            "SELECT (SELECT COUNT(*) FROM confirmaciones_recojo), "
            "(SELECT COUNT(*) FROM abonos_recojo)"
        ).fetchone()


def test_100_envios_concurrentes_y_secuenciales_acreditan_una_sola_vez(postgres):
    alta, gestion = servicios(postgres)
    solicitud_id = registrar(alta, gestion)
    juntos = Barrier(10, timeout=15)

    def confirmar(_):
        juntos.wait()
        return gestion.confirmar_recojo(solicitud_id, "recojo-1", 1.5)

    with ThreadPoolExecutor(max_workers=10) as ejecutor:
        primeros = list(ejecutor.map(confirmar, range(10)))
    _, gestion_nueva = servicios(postgres)
    reenvios = [gestion_nueva.confirmar_recojo(solicitud_id, "recojo-1", 1.5) for _ in range(90)]

    assert len(set(primeros + reenvios)) == 1
    assert filas_confirmadas(postgres) == (1, 1)
    assert primeros[0].puntos == 10
    assert gestion.obtener(solicitud_id).estado is EstadoSolicitud.PUNTOS_ACREDITADOS


def test_rechaza_100_lecturas_y_100_escrituras_cruzadas(postgres):
    alta_a, gestion_a = servicios(postgres, "D01")
    alta_b, gestion_b = servicios(postgres, "D02")
    id_a = registrar(alta_a, gestion_a, "V01")
    id_b = registrar(alta_b, gestion_b, "V02")

    for intento in range(100):
        gestion, id_ajeno = (gestion_a, id_b) if intento % 2 == 0 else (gestion_b, id_a)
        with pytest.raises(PermissionError, match="Solicitud no disponible"):
            gestion.obtener(id_ajeno)
        with pytest.raises(PermissionError, match="Solicitud no disponible"):
            gestion.confirmar_recojo(id_ajeno, "intento-cruzado", 1.5)

    assert [s.id for s in gestion_a.listar()] == [id_a]
    assert [s.id for s in gestion_b.listar()] == [id_b]
    assert gestion_a.obtener(id_a).estado is EstadoSolicitud.ASIGNADA
    assert gestion_b.obtener(id_b).estado is EstadoSolicitud.ASIGNADA
    assert filas_confirmadas(postgres) == (0, 0)


def test_conflictos_de_clave_peso_y_solicitud(postgres):
    alta, gestion = servicios(postgres)
    id_a = registrar(alta, gestion)
    id_b = registrar(alta, gestion)
    gestion.confirmar_recojo(id_a, "clave-1", 1.5)

    with pytest.raises(ErrorValidacion, match="Conflicto"):
        gestion.confirmar_recojo(id_a, "clave-1", 2)
    with pytest.raises(ErrorValidacion, match="Conflicto"):
        gestion.confirmar_recojo(id_a, "clave-2", 1.5)
    with pytest.raises(ErrorValidacion, match="otra solicitud"):
        gestion.confirmar_recojo(id_b, "clave-1", 1.5)

    alta_otro, gestion_otro = servicios(postgres, "D02")
    id_otro = registrar(alta_otro, gestion_otro)
    assert gestion_otro.confirmar_recojo(id_otro, "clave-1", 1.5).puntos == 10
    assert filas_confirmadas(postgres) == (2, 2)


def test_error_al_insertar_abono_revierte_la_operacion_completa(postgres):
    import psycopg

    alta, gestion = servicios(postgres)
    solicitud_id = registrar(alta, gestion)
    gestion.registrar_recojo(solicitud_id)
    gestion.registrar_pesaje(solicitud_id, 1.5)

    with psycopg.connect(postgres) as conexion:
        conexion.execute("ALTER TABLE abonos_recojo ADD CONSTRAINT fallo_abono CHECK (puntos < 10)")
    with pytest.raises(psycopg.errors.CheckViolation):
        gestion.confirmar_recojo(solicitud_id, "clave-1", 1.5)

    assert filas_confirmadas(postgres) == (0, 0)
    assert gestion.obtener(solicitud_id).estado is EstadoSolicitud.PESADA
    assert gestion.obtener(solicitud_id).puntos is None

    with psycopg.connect(postgres) as conexion:
        conexion.execute("ALTER TABLE abonos_recojo DROP CONSTRAINT fallo_abono")
    assert gestion.confirmar_recojo(solicitud_id, "clave-1", 1.5).puntos == 10
    assert filas_confirmadas(postgres) == (1, 1)
