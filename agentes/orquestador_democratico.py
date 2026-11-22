"""Actor-crítico con uno o tres revisores, máximo dos rondas y pruebas obligatorias.

Modo grabado: decisiones redactadas por Codex y herramientas reales, sin llamadas
API ni revisores LLM independientes. Modo interactivo: intercambio con el asistente.
Cada ejecución siembra ISSUE-02 en una copia temporal; conserva intacto src/ original.
"""
import argparse
import difflib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from agentes.agente.herramientas import Herramientas
from agentes.agente.modelos import ModeloGrabado, ModeloInteractivo
from agentes.agente.nucleo import Agente
from agentes.agente.politica import Politica, aprobar_edicion

RUTA = "src/solicitudes/operaciones_lab10.py"
CORRECTO = '    from src.solicitudes.estados import Cancelado\n\n    return [solicitud for solicitud in solicitudes if solicitud.estado != Cancelado.nombre]'
DEFECTO = '    return list(solicitudes)'
FOCOS = {
    "correccion": "Verificar exclusión de canceladas, conservación de pendientes, orden y entrada vacía.",
    "diseno": "Verificar cambio acotado al selector y reutilización de Cancelado.nombre sin duplicar estados.",
    "seguridad": "Verificar protección de tests y permisos: el revisor no puede editar ni invocar shell.",
}


def contar_votos(veredictos):
    """Solo APROBADO o CAMBIOS: con explicación. Nunca se aprueba una abstención."""
    if len(veredictos) not in (1, 3):
        raise ValueError("Se requieren uno o tres votos")
    votos = []
    for texto in veredictos:
        if texto.startswith("APROBADO. ") and texto[len("APROBADO. "):].strip():
            votos.append(True)
        elif texto.startswith("CAMBIOS: ") and texto[len("CAMBIOS: "):].strip():
            votos.append(False)
        else:
            raise ValueError(f"Veredicto inválido: {texto!r}")
    return sum(votos) > len(votos) // 2


class HerramientasEvaluacion(Herramientas):
    def __init__(self, raiz, original):
        super().__init__(str(raiz))
        self.original = original

    def catalogo(self):
        return {**super().catalogo(),
                "pruebas_issue": "pruebas_issue(): pytest de aceptación y casos adicionales del Issue 02",
                "pruebas_politica": "pruebas_politica(): pytest de gobernanza E6"}

    def ver_cambios(self):
        return "\n".join(difflib.unified_diff(self.original.splitlines(),
            self._ruta(RUTA).read_text(encoding="utf-8").splitlines(),
            "a/" + RUTA, "b/" + RUTA, lineterm="")) or "(sin cambios)"

    def _pytest(self, rutas):
        resultado = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *rutas],
                                  cwd=self.raiz, capture_output=True, text=True, timeout=120)
        return f"exit={resultado.returncode}\n" + (resultado.stdout + resultado.stderr).strip()

    def pruebas_issue(self):
        return self._pytest(["tests/test_issue_02.py", "agentes/pruebas_agente/test_issue_02_adicional.py"])

    def pruebas_politica(self):
        return self._pytest(["agentes/pruebas_agente/test_politica_e6.py"])


def accion(nombre, args=None, pensamiento="Inspeccionar evidencia antes del veredicto"):
    return {"pensamiento": pensamiento, "accion": nombre, "args": args or {}}


def grabacion(rol):
    if rol == "planificador":
        return [{"pensamiento": "Plan acotado al criterio del Issue 02", "final": "Reproducir el defecto, filtrar Cancelado.nombre, verificar pytest y revisar diff."}]
    if rol == "ejecutor":
        return [accion("leer_archivo", {"ruta": "issues/ISSUE-02.md"}),
                accion("pruebas_issue"), accion("leer_archivo", {"ruta": RUTA}),
                accion("editar_archivo", {"ruta": RUTA, "antes": DEFECTO, "despues": CORRECTO}),
                accion("pruebas_issue"), accion("ver_cambios"),
                {"pensamiento": "Se ejecutaron la corrección y las comprobaciones; el orquestador verificará el resultado", "final": "Selector corregido; revisar observaciones de pytest y diff antes de votar."}]
    foco = rol.removeprefix("revisor_")
    decisiones = [accion("ver_cambios"), accion("leer_archivo", {"ruta": RUTA})]
    if foco == "correccion":
        decisiones.append(accion("pruebas_issue"))
    elif foco == "seguridad":
        decisiones.append(accion("pruebas_politica"))
    return decisiones + [{"pensamiento": FOCOS[foco], "final": f"APROBADO. {FOCOS[foco]} Evidencia en las acciones previas; aprobación sujeta al control automático de pytest."}]


class ModeloRevisionGrabada(ModeloGrabado):
    """El voto de reproducción se rechaza si su propia evidencia registra errores."""
    def decidir(self, historial):
        decision = super().decidir(historial)
        if "final" in decision:
            observaciones = [m["content"] for m in historial[1:] if m["role"] == "user"]
            if any("ERROR:" in o or ("exit=" in o and "exit=0\n" not in o) for o in observaciones):
                decision = {"pensamiento": "La evidencia no permite aprobar", "final": "CAMBIOS: La revisión obtuvo errores o pruebas fallidas; revisar las observaciones."}
        return decision


def ejecutar(raiz, salida, modo, revisores, simulacion):
    salida.mkdir(parents=True, exist_ok=True)
    for carpeta in ("trazas", "decisiones"):
        (salida / carpeta).mkdir(exist_ok=True)
    original = (raiz / RUTA).read_text(encoding="utf-8")
    h = HerramientasEvaluacion(raiz, original)
    permiso_revision = {"ver_cambios", "leer_archivo", "pruebas_issue", "pruebas_politica"}
    politica_ejecutor = Politica(herramientas_permitidas={"leer_archivo", "editar_archivo", "pruebas_issue", "ver_cambios"},
                                 max_pasos=12, aprobar_edicion=(lambda propuesta: True) if simulacion else aprobar_edicion)
    politicas = {"planificador": Politica(herramientas_permitidas=set(), max_pasos=3),
                 "ejecutor": politica_ejecutor,
                 **{f"revisor_{foco}": Politica(herramientas_permitidas=permiso_revision.copy(), max_pasos=8) for foco in FOCOS}}
    resumen_rondas = []

    def correr(rol, ronda, objetivo):
        nombre = f"{rol}_r{ronda}"
        archivo = salida / "decisiones" / f"{nombre}.json"
        if modo == "grabado":
            archivo.write_text(json.dumps(grabacion(rol), ensure_ascii=False, indent=2), encoding="utf-8")
            modelo = ModeloRevisionGrabada(archivo) if rol.startswith("revisor_") else ModeloGrabado(archivo)
        else:
            modelo = ModeloInteractivo(archivo)
        catalogo = {k: v for k, v in h.catalogo().items() if k in politicas[rol].herramientas_permitidas}
        agente = Agente(rol, modelo, h, politicas[rol], objetivo + f"\nCatálogo permitido: {catalogo}", salida / "trazas" / f"{nombre}.jsonl")
        texto = agente.ejecutar()
        if agente.eventos[-1]["tipo"] != "final":
            raise RuntimeError(f"{rol}: presupuesto agotado sin respuesta final")
        print(f"{nombre}: {texto}")
        return texto

    plan = correr("planificador", 1, "Planifique el arreglo de issues/ISSUE-02.md sin usar herramientas.")
    cambios = ""
    for ronda in (1, 2):
        resumen = correr("ejecutor", ronda, f"Resuelva issues/ISSUE-02.md solo en src/. Plan: {plan}. Observaciones previas: {cambios}")
        focos = list(FOCOS) if revisores == "tres" else ["correccion"]
        votos = {foco: correr(f"revisor_{foco}", ronda,
                    f"{FOCOS[foco]} Revise diff y pruebas. Responda APROBADO. seguido de justificación o CAMBIOS: seguido de motivos. Resumen: {resumen}") for foco in focos}
        # La mayoría no reemplaza la prueba de aceptación: un error de infraestructura tampoco aprueba.
        prueba = h.pruebas_issue()
        aprobada = contar_votos(list(votos.values())) and prueba.startswith("exit=0\n")
        resumen_rondas.append({"ronda": ronda, "votos": votos, "prueba_obligatoria": prueba, "aprobada": aprobada})
        (salida / f"diff_r{ronda}.patch").write_text(h.ver_cambios(), encoding="utf-8")
        if aprobada:
            break
        cambios = json.dumps(resumen_rondas[-1], ensure_ascii=False)
    resultado = {"modo": modo, "aprobacion_edicion": "simulada" if simulacion else "humana",
                 "revisores": revisores, "rondas": resumen_rondas,
                 "aprobada": resumen_rondas[-1]["aprobada"],
                 "limitacion": "Las decisiones grabadas provienen de un mismo asistente; no prueban independencia entre modelos."}
    (salida / "resultado.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return resultado["aprobada"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modo", choices=["interactivo", "grabado"], default="interactivo")
    parser.add_argument("--revisores", choices=["uno", "tres"], default="tres")
    parser.add_argument("--simular-aprobacion", action="store_true", help="Solo laboratorio: registra la autorización como simulada")
    parser.add_argument("--salida", type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    salida = (args.salida or repo / "agentes" / "trazas" / f"reto_{args.revisores}").resolve()
    if (salida / "resultado.json").exists():
        raise SystemExit("La salida ya contiene una corrida. Use --salida con otra carpeta para conservar la evidencia.")
    with tempfile.TemporaryDirectory(prefix="ecorecicla-reto-") as temporal:
        copia = Path(temporal) / "repo"
        shutil.copytree(repo, copia, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", "trazas"))
        p = copia / RUTA
        texto = p.read_text(encoding="utf-8")
        if texto.count(CORRECTO) != 1:
            raise SystemExit("No se encontró el selector esperado; no se sembrará el defecto.")
        p.write_text(texto.replace(CORRECTO, DEFECTO), encoding="utf-8")
        if not ejecutar(copia, salida, args.modo, args.revisores, args.simular_aprobacion):
            raise SystemExit("No aprobado tras dos rondas.")


if __name__ == "__main__":
    main()
