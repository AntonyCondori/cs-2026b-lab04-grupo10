"""Prototipo QA-04: reenvios de una confirmacion, con y sin idempotencia.

No reemplaza el servicio del dominio ni representa una prueba de PostgreSQL.
Cada solicitud usa una conexion propia a SQLite sobre el mismo archivo.
"""
import json
from contextlib import closing
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier


class RegistroConfirmaciones:
    def __init__(self, ruta, estrategia="idempotencia"):
        if estrategia not in {"sin_tactica", "idempotencia"}:
            raise ValueError("Estrategia no soportada")
        self.ruta = str(ruta)
        self.estrategia = estrategia
        with closing(sqlite3.connect(self.ruta)) as con, con:
            con.execute("PRAGMA foreign_keys=ON")
            con.execute("""CREATE TABLE IF NOT EXISTS confirmaciones (
                id INTEGER PRIMARY KEY, clave TEXT NOT NULL,
                solicitud INTEGER NOT NULL, puntos INTEGER NOT NULL)""")
            con.execute("""CREATE TABLE IF NOT EXISTS abonos (
                confirmacion INTEGER PRIMARY KEY REFERENCES confirmaciones(id),
                puntos INTEGER NOT NULL)""")
            if estrategia == "idempotencia":
                con.execute("CREATE UNIQUE INDEX IF NOT EXISTS clave_unica "
                            "ON confirmaciones(clave)")
                con.execute("CREATE UNIQUE INDEX IF NOT EXISTS solicitud_unica "
                            "ON confirmaciones(solicitud)")

    def confirmar(self, clave, solicitud=1, puntos=10, fallo_antes_abono=False):
        if not clave or puntos < 0:
            raise ValueError("Clave y puntos invalidos")
        con = sqlite3.connect(self.ruta, timeout=15)
        con.execute("PRAGMA foreign_keys=ON")
        try:
            # Reserva de escritura: comprobacion y abono dentro de una transaccion.
            con.execute("BEGIN IMMEDIATE")
            if self.estrategia == "idempotencia":
                fila = con.execute(
                    "SELECT id, clave, solicitud, puntos FROM confirmaciones "
                    "WHERE clave=? OR solicitud=?", (clave, solicitud)
                ).fetchone()
                if fila:
                    if fila[1:] != (clave, solicitud, puntos):
                        raise ValueError("Conflicto de clave o de solicitud")
                    con.commit()
                    return {"confirmacion": fila[0], "solicitud": fila[2],
                            "puntos": fila[3], "estado": "COMPLETADO"}
            cursor = con.execute(
                "INSERT INTO confirmaciones(clave, solicitud, puntos) VALUES(?,?,?)",
                (clave, solicitud, puntos),
            )
            identificador = cursor.lastrowid
            if fallo_antes_abono:
                raise RuntimeError("Fallo inyectado antes del abono")
            con.execute("INSERT INTO abonos(confirmacion, puntos) VALUES(?,?)",
                        (identificador, puntos))
            con.commit()
            return {"confirmacion": identificador, "solicitud": solicitud,
                    "puntos": puntos, "estado": "COMPLETADO"}
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def contar(self):
        with closing(sqlite3.connect(self.ruta)) as con, con:
            confirmaciones = con.execute("SELECT COUNT(*) FROM confirmaciones").fetchone()[0]
            abonos, puntos = con.execute(
                "SELECT COUNT(*), COALESCE(SUM(puntos),0) FROM abonos"
            ).fetchone()
        return {"confirmaciones": confirmaciones, "abonos": abonos,
                "puntos_totales": puntos, "duplicados": max(0, abonos - 1)}


def simular(estrategia, total=100, simultaneas=10, perder_cada=10):
    """total incluye reenvios; simultaneas llegan juntas, SQLite serializa escrituras.

Se descarta una respuesta ya confirmada cada perder_cada envios para modelar
perdidas de acuse. No se simulan caidas del VPS ni latencia real de red.
"""
    if total < 1 or not 1 <= simultaneas <= total or perder_cada < 1:
        raise ValueError("Parametros de simulacion invalidos")
    with TemporaryDirectory() as tmp:
        registro = RegistroConfirmaciones(Path(tmp) / "abonos.sqlite3", estrategia)
        barrera = Barrier(simultaneas)

        def enviar(indice):
            barrera.wait(timeout=15)
            return registro.confirmar("confirmacion-1")

        with ThreadPoolExecutor(max_workers=simultaneas) as ejecutor:
            respuestas = list(ejecutor.map(enviar, range(simultaneas)))
        for _ in range(total - simultaneas):
            respuestas.append(registro.confirmar("confirmacion-1"))

        recibidas = [r for i, r in enumerate(respuestas, 1) if i % perder_cada]
        resultado = registro.contar()
        resultado.update({"estrategia": estrategia, "envios": total,
                          "simultaneas": simultaneas,
                          "acuses_perdidos": total // perder_cada,
                          "respuestas_recibidas": len(recibidas),
                          "resultado_original_reutilizado": bool(recibidas) and
                          all(r == respuestas[0] for r in recibidas)})
        return resultado


if __name__ == "__main__":
    resultados = [simular(e) for e in ("sin_tactica", "idempotencia")]
    print(json.dumps(resultados, indent=2, ensure_ascii=False))
    protegido = resultados[1]
    cumple = (protegido["confirmaciones"] == protegido["abonos"] == 1
              and protegido["duplicados"] == 0
              and protegido["resultado_original_reutilizado"])
    print("QA-04:", "SE CUMPLE EN EL PROTOTIPO" if cumple else "NO SE CUMPLE")
    raise SystemExit(0 if cumple else 1)
