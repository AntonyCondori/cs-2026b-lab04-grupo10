import os
from pathlib import Path
import subprocess
import sys

from agentes.agente.herramientas import Herramientas
from agentes.agente.modelos import ModeloInteractivo
from agentes.agente.politica import Politica


OBJETIVO_ISSUE = (
    "Resuelve issues/ISSUE-02.md en EcoRecicla AQP: la ruta incluye solicitudes canceladas. "
    "Lee el issue para identificar sus criterios de aceptación. "
    "Usa mapa_repo() para ubicarte y reproduce el fallo con "
    "python -m pytest -q tests/test_issue_02.py. "
    "Registra tus hipótesis y los archivos que ya revisaste con anotar(texto). "
    "Consulta tus notas con leer_notas() cuando necesites recuperar ese contexto. "
    "Investiga la causa y limita la corrección del código a src/. "
    "Verifica la corrección con la misma prueba de pytest y revisa el cambio con git diff. "
    "Resume la corrección y el resultado de la prueba al finalizar."
)


class ModeloPorRol(ModeloInteractivo):
    def __init__(self, grabar_en, etiqueta):
        super().__init__(grabar_en)
        self.etiqueta = etiqueta

    def decidir(self, historial):
        print(f"\n===== ROL ACTIVO: {self.etiqueta} =====")
        return super().decidir(historial)


class HerramientasRevision(Herramientas):
    def ver_cambios(self):
        resultado = subprocess.run(
            ["git", "--no-pager", "diff", "--no-ext-diff", "--no-textconv", "HEAD", "--"],
            cwd=self.raiz,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            timeout=60,
        )
        return resultado.stdout or "(sin cambios)"


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
    herramientas_revision = HerramientasRevision(str(raiz))
    politica_ejecutor = Politica(max_pasos=12)
    politica_ejecutor.herramientas_permitidas.add("anotar")
    politica_revisor = Politica(
        herramientas_permitidas={"ver_cambios", "leer_archivo", "buscar", "ejecutar_pruebas"},
        max_pasos=8,
    )

    def ejecutar_rol(rol, objetivo, herramientas_rol, politica, ronda=1):
        nombre_archivo = rol if ronda == 1 else f"{rol}_r{ronda}"
        catalogo = {
            nombre: firma for nombre, firma in herramientas_rol.catalogo().items()
            if nombre in politica.herramientas_permitidas
        }
        agente = Agente(
            nombre=rol,
            modelo=ModeloPorRol(
                carpeta_agentes / "trayectorias" / f"{nombre_archivo}.json",
                f"{rol} (ronda {ronda})",
            ),
            herramientas=herramientas_rol,
            politica=politica,
            objetivo=f"{objetivo}\nHerramientas disponibles: {catalogo}",
            traza_archivo=carpeta_agentes / "trazas" / f"{nombre_archivo}.jsonl",
        )
        respuesta = agente.ejecutar().strip()
        if agente.eventos[-1]["tipo"] != "final" or not respuesta:
            raise SystemExit(f"{rol} terminó sin una respuesta final válida.")
        return respuesta

    plan = ejecutar_rol(
        "planificador",
        "Propón un plan para issues/ISSUE-02.md: la ruta incluye solicitudes canceladas. "
        "Describe los pasos para investigar, corregir en src/ y verificar con pytest. "
        "Entrega el plan en el campo final.",
        herramientas,
        Politica(herramientas_permitidas=set(), max_pasos=3),
    )

    cambios = ""
    for ronda in (1, 2):
        objetivo_ejecutor = f"{OBJETIVO_ISSUE}\nPlan del planificador:\n{plan}"
        if cambios:
            objetivo_ejecutor += (
                f"\nCambios solicitados por el revisor:\n{cambios}\n"
                "Continúa desde el estado actual del código y atiende estas observaciones."
            )
        resumen = ejecutar_rol(
            "ejecutor", objetivo_ejecutor, herramientas, politica_ejecutor, ronda
        )
        veredicto = ejecutar_rol(
            "revisor",
            "Revisa la corrección de issues/ISSUE-02.md. Comprueba que la ruta excluya "
            "las solicitudes canceladas. Inspecciona el diff con ver_cambios() y ejecuta "
            "las pruebas con ejecutar_pruebas(). El campo final debe comenzar con APROBADO "
            "si la corrección es adecuada o con CAMBIOS: y el motivo si requiere ajustes.\n"
            f"Resumen del ejecutor:\n{resumen}",
            herramientas_revision,
            politica_revisor,
            ronda,
        )
        print(f"\nVeredicto de la ronda {ronda}: {veredicto}")
        if veredicto.split(maxsplit=1)[0].rstrip(":") == "APROBADO":
            return
        if not veredicto.startswith("CAMBIOS:") or not veredicto[len("CAMBIOS:"):].strip():
            raise SystemExit("El revisor debe responder APROBADO o CAMBIOS: seguido del motivo.")
        cambios = veredicto[len("CAMBIOS:"):].strip()

    raise SystemExit("Se completaron dos rondas. La revisión sigue solicitando cambios.")


if __name__ == "__main__":
    main()
