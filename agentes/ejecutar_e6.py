"""Demostración aislada del callback humano: no modifica src/ del repositorio."""
import argparse
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from agentes.agente.herramientas import Herramientas
from agentes.agente.modelos import ModeloGrabado
from agentes.agente.nucleo import Agente
from agentes.agente.politica import Politica, aprobar_edicion


RUTA = "src/ejemplo.py"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simular", action="store_true", help="Entradas programadas: inválida, n, s; no es aprobación humana real")
    parser.add_argument("--salida", type=Path, default=Path("agentes/trazas/e6"))
    args = parser.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    decisiones = [
        {"pensamiento": "Detectar un incumplimiento del contrato", "accion": "leer_archivo", "args": RUTA},
        {"pensamiento": "Comprobar la protección de pruebas", "accion": "editar_archivo", "args": {"ruta": "tests/test_issue_02.py", "antes": "a", "despues": "b"}},
        *[{"pensamiento": "Proponer una edición acotada y solicitar aprobación", "accion": "editar_archivo", "args": {"ruta": RUTA, "antes": "valor = 1\n", "despues": "valor = 2\n"}} for _ in range(2)],
        {"pensamiento": "Leer el resultado de las decisiones de autorización", "accion": "leer_archivo", "args": {"ruta": RUTA}},
        {"pensamiento": "Finalizar demostración de gobernanza", "final": "Fin de la demostración. Consulte las observaciones y el archivo final."},
    ]
    trayectoria = args.salida / "decisiones.json"
    trayectoria.write_text(json.dumps(decisiones, ensure_ascii=False, indent=2), encoding="utf-8")
    aprobaciones = []

    def aprobar_registrando(propuesta):
        permitido = aprobar_edicion(propuesta)
        aprobaciones.append({"ruta": propuesta["ruta"], "aprobada": permitido})
        return permitido

    with tempfile.TemporaryDirectory(prefix="ecorecicla-e6-") as temporal:
        raiz = Path(temporal)
        (raiz / "src").mkdir()
        (raiz / RUTA).write_text("valor = 1\n", encoding="utf-8")
        agente = Agente("ejecutor", ModeloGrabado(trayectoria), Herramientas(temporal),
                        Politica(max_pasos=6, aprobar_edicion=aprobar_registrando),
                        "Demostrar contrato, protección de tests y aprobación explícita; decisiones grabadas de Codex.",
                        args.salida / "ejecutor.jsonl")
        if args.simular:
            print("SIMULACIÓN: entradas programadas; no constituye aprobación de una persona.")
            entradas = iter(["quizá", "n", "s"])

            def entrada_simulada(prompt):
                respuesta = next(entradas)
                print(prompt + respuesta)
                return respuesta

            with patch("builtins.input", side_effect=entrada_simulada):
                agente.ejecutar()
        else:
            print("MODO HUMANO: responda n a la primera propuesta y s a la segunda para reproducir la evidencia.")
            agente.ejecutar()
        resultado = {"modo": "simulado" if args.simular else "humano", "aprobaciones": aprobaciones,
                     "contenido_final": (raiz / RUTA).read_text(encoding="utf-8")}
        (args.salida / "resultado.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
        for evento in agente.eventos:
            if evento["tipo"] == "accion":
                print(f"Paso {evento['paso']}: {evento['estado']} | {evento['observacion']}")
        print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
