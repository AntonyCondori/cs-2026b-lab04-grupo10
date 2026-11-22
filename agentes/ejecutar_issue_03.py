import os
from pathlib import Path
import sys

from agentes.agente.herramientas import Herramientas
from agentes.agente.modelos import ModeloInteractivo
from agentes.agente.politica import Politica


def main():
    carpeta_agentes = Path(__file__).resolve().parent
    raiz = carpeta_agentes.parent

    # nucleo.py todavía importa el contrato mediante agente.contrato.
    sys.path.insert(0, str(carpeta_agentes))
    try:
        from agentes.agente.nucleo import Agente
    finally:
        sys.path.pop(0)

    # Las herramientas existentes lanzan las pruebas con el comando python.
    os.environ["PATH"] = os.pathsep.join(
        (str(Path(sys.executable).parent), os.environ.get("PATH", ""))
    )

    herramientas = Herramientas(str(raiz))
    modelo = ModeloInteractivo(carpeta_agentes / "trayectorias" / "issue_03.json")
    politica = Politica(max_pasos=15)
    politica.herramientas_permitidas.add("anotar")

    objetivo = (
        "Resuelve issues/ISSUE-03.md en EcoRecicla AQP. "
        "Lee el issue para identificar sus criterios de aceptación. "
        "Usa mapa_repo() para ubicarte y reproduce el fallo con "
        "python -m pytest -q tests/test_issue_03.py. "
        "Registra tus hipótesis y los archivos que ya revisaste con anotar(texto). "
        "Consulta tus notas con leer_notas() cuando necesites recuperar ese contexto. "
        "Investiga la causa y limita la corrección del código a src/. "
        "Verifica la corrección con la misma prueba de pytest y revisa el cambio con git diff. "
        "Resume la corrección y el resultado de la prueba al finalizar.\n"
        f"Herramientas disponibles: {herramientas.catalogo()}"
    )

    agente = Agente(
        nombre="ejecutor",
        modelo=modelo,
        herramientas=herramientas,
        politica=politica,
        objetivo=objetivo,
        traza_archivo=carpeta_agentes / "trazas" / "issue_03.jsonl",
    )
    print(agente.ejecutar())


if __name__ == "__main__":
    main()
