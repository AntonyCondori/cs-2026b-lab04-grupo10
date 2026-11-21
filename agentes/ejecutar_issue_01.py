from pathlib import Path

from agente.herramientas import Herramientas
from agente.modelos import ModeloInteractivo
from agente.nucleo import Agente
from agente.politica import Politica


def main():
    carpeta_agentes = Path(__file__).resolve().parent
    copia = carpeta_agentes.parent.parent / "ecorecicla-e2-trabajo"

    if not (copia / "issues" / "ISSUE-01.md").is_file():
        raise SystemExit(f"No se encontró issues/ISSUE-01.md en {copia}")

    herramientas = Herramientas(str(copia))
    modelo = ModeloInteractivo(carpeta_agentes / "trayectorias" / "issue_01.json")
    politica = Politica(max_pasos=12)

    objetivo = (
        "Resuelve issues/ISSUE-01.md en EcoRecicla AQP. "
        "Lee el issue y reproduce el fallo con "
        "python -m pytest -q tests/test_issue_01.py. "
        "Investiga la causa y corrige la acreditación duplicada. "
        "Dos recojos distintos del mismo vecino deben seguir sumando. "
        "Conserva las pruebas y limita los cambios al Issue 01. "
        "Al terminar, ejecuta la misma prueba y revisa el cambio con git diff.\n"
        f"Herramientas disponibles: {herramientas.catalogo()}"
    )

    agente = Agente(
        nombre="ejecutor",
        modelo=modelo,
        herramientas=herramientas,
        politica=politica,
        objetivo=objetivo,
        traza_archivo=carpeta_agentes / "trazas" / "issue_01.jsonl",
    )
    print(agente.ejecutar())


if __name__ == "__main__":
    main()