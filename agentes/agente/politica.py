"""Guardrails: qué puede hacer el agente, cuántas veces y con qué aprobación."""
import difflib
import re
import shlex
from pathlib import PurePosixPath
from typing import Callable, Optional
from dataclasses import dataclass, field


def aprobar_edicion(args: dict) -> bool:
    """Solicita una decisión humana explícita; EOF o interrupción rechazan."""
    print(f"\nEdición propuesta: {args.get('ruta', '')}")
    print("".join(difflib.unified_diff(
        args.get("antes", "").splitlines(keepends=True),
        args.get("despues", "").splitlines(keepends=True),
        fromfile="antes", tofile="después")))
    while True:
        try:
            respuesta = input("¿Aprobar esta edición? [s/n]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("Sin aprobación explícita: edición rechazada.")
            return False
        if respuesta in {"s", "n"}:
            return respuesta == "s"
        print("Respuesta inválida. Escriba s o n.")


@dataclass
class Decision:
    permitido: bool
    motivo: str = ""


@dataclass
class Politica:
    herramientas_permitidas: set = field(default_factory=lambda: {
        "listar_archivos", "leer_archivo", "buscar", "ejecutar_pruebas", "editar_archivo", "ejecutar_comando",
        "mapa_repo", "leer_notas"})  # El ejecutor añade "anotar" a su propia instancia.
    comandos_permitidos: tuple = (r"^python -m pytest\b", r"^radon cc\b", r"^lint-imports\b", r"^git (status|diff)\b")
    rutas_protegidas: tuple = ("tests/",)          # el agente no puede "arreglar" las pruebas para que pasen
    max_pasos: int = 15
    aprobar_edicion: Optional[Callable[[dict], bool]] = None

    def evaluar(self, accion: str, args: dict, paso: int) -> Decision:
        if paso > self.max_pasos:
            return Decision(False, f"Se alcanzó el máximo de {self.max_pasos} pasos")
        if accion not in self.herramientas_permitidas:
            return Decision(False, f"Herramienta no permitida: {accion}")
        if accion == "ejecutar_comando":
            cmd = args.get("comando", "")
            # El catálogo no ofrece un shell general ni operadores de encadenamiento.
            try:
                partes = shlex.split(cmd)
            except ValueError:
                return Decision(False, "Comando mal formado")
            if (not partes or any(c in cmd for c in ";|&><`$\n\r")
                    or not any(re.fullmatch(p.replace(r"\b", r"(?:[ \t].*)?"), cmd)
                               for p in self.comandos_permitidos)):
                return Decision(False, f"Comando fuera de la lista permitida: {cmd!r}")
        if accion == "editar_archivo":
            ruta = args.get("ruta", "")
            normal = PurePosixPath(ruta.replace("\\", "/"))
            if (normal.is_absolute() or ".." in normal.parts
                    or not normal.parts or normal.parts[0] != "src"
                    or normal.as_posix().startswith(self.rutas_protegidas)):
                return Decision(False, f"Ruta protegida: {ruta}")
            if self.aprobar_edicion and not self.aprobar_edicion(args):
                return Decision(False, "El revisor humano rechazó la edición")
        return Decision(True)
