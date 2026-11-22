"""Herramientas del agente. Cada una es una función pequeña, con descripción y parámetros explícitos.
Todas operan DENTRO del directorio de trabajo (sandbox)."""
import ast
import shlex
import sys
import os
import pathlib, subprocess, re


class Herramientas:
    def __init__(self, raiz: str):
        self.raiz = pathlib.Path(raiz).resolve()

    # --- utilidades ---
    def _ruta(self, ruta: str) -> pathlib.Path:
        p = (self.raiz / ruta).resolve()
        if self.raiz not in p.parents and p != self.raiz:
            raise PermissionError(f"Ruta fuera del sandbox: {ruta}")
        return p

    def catalogo(self) -> dict:
        """Descripción de las herramientas que se envía al modelo (como en un MCP server)."""
        return {
            "listar_archivos": "listar_archivos(carpeta='.'): lista los archivos .py y .md",
            "leer_archivo": "leer_archivo(ruta): devuelve el contenido con números de línea",
            "buscar": "buscar(patron): busca una expresión regular en los archivos .py",
            "ejecutar_pruebas": "ejecutar_pruebas(): ejecuta pytest y devuelve el resumen",
            "editar_archivo": "editar_archivo(ruta, antes, despues): reemplaza un fragmento exacto (una sola vez)",
            "ver_cambios": "ver_cambios(): muestra el diff respecto de la versión original",
            "ejecutar_comando": "ejecutar_comando(comando): ejecuta un comando de shell (sujeto a la política)",
            "mapa_repo": (
                "mapa_repo(): analiza archivos Python con AST y devuelve un resumen por archivo "
                "con nombres de clases, firmas de funciones y números de línea, "
                "sin incluir el contenido completo de los archivos"
            ),
            "anotar": "anotar(texto): agrega una nota de hasta 500 caracteres",
            "leer_notas": "leer_notas(): devuelve el contenido de agentes/notas.md",
        }

    # --- herramientas ---
    def mapa_repo(self):
        mapa = []
        ignoradas = {".git", "__pycache__", ".venv", "venv", ".env", "env", "virtualenv"}
        tipos = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        for carpeta, subcarpetas, archivos in os.walk(self.raiz):
            base = pathlib.Path(carpeta)
            subcarpetas[:] = sorted(
                nombre for nombre in subcarpetas
                if nombre.casefold() not in ignoradas
                and not (base / nombre / "pyvenv.cfg").is_file()
            )
            for nombre in sorted(archivos):
                if not nombre.endswith(".py"):
                    continue
                ruta = (base / nombre).relative_to(self.raiz).as_posix()
                mapa.append(f"{ruta}:")
                try:
                    arbol = ast.parse(self._ruta(ruta).read_bytes(), filename=ruta)
                except SyntaxError as error:
                    mapa.append(f"  Error de sintaxis (línea {error.lineno}): {error.msg}")
                    continue
                except OSError as error:
                    mapa.append(f"  No se pudo leer: {error}")
                    continue
                simbolos = sorted(
                    (nodo for nodo in ast.walk(arbol) if isinstance(nodo, tipos)),
                    key=lambda nodo: nodo.lineno,
                )
                for nodo in simbolos:
                    if isinstance(nodo, ast.ClassDef):
                        simbolo = f"clase {nodo.name}"
                    else:
                        simbolo = f"función {nodo.name}({ast.unparse(nodo.args)})"
                    mapa.append(f"  {simbolo} (línea {nodo.lineno})")
        return "\n".join(mapa)

    def anotar(self, texto):
        nota = re.sub(r"\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]", " ", texto)[:500]
        ruta = self._ruta("agentes/notas.md")
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with ruta.open("a+b") as archivo:
            separador = b""
            if archivo.tell():
                archivo.seek(-1, os.SEEK_END)
                if archivo.read(1) != b"\n":
                    separador = b"\n"
            archivo.write(separador + f"{nota}\n".encode("utf-8"))
        return "OK: nota agregada"

    def leer_notas(self):
        try:
            return self._ruta("agentes/notas.md").read_text(encoding="utf-8")
        except FileNotFoundError:
            return ""

    def listar_archivos(self, carpeta="."):
        base = self._ruta(carpeta)
        return "\n".join(sorted(str(p.relative_to(self.raiz)) for p in base.rglob("*")
                                if p.suffix in (".py", ".md") and "__pycache__" not in p.parts))

    def leer_archivo(self, ruta):
        lineas = self._ruta(ruta).read_text(encoding="utf-8").splitlines()
        return "\n".join(f"{i:3d}| {l}" for i, l in enumerate(lineas, 1))

    def buscar(self, patron):
        rx, hallazgos = re.compile(patron), []
        for p in sorted(self.raiz.rglob("*.py")):
            for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if rx.search(l):
                    hallazgos.append(f"{p.relative_to(self.raiz)}:{i}: {l.strip()}")
        return "\n".join(hallazgos) or "(sin resultados)"

    def ejecutar_pruebas(self):
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"],
                           cwd=self.raiz, capture_output=True, text=True, timeout=120)
        salida = (r.stdout + r.stderr).strip().splitlines()
        fallos = [l for l in salida if l.startswith(("FAILED", "E "))][:6]
        return "\n".join(fallos + salida[-1:])

    def editar_archivo(self, ruta, antes, despues):
        p = self._ruta(ruta)
        texto = p.read_text(encoding="utf-8")
        if texto.count(antes) != 1:
            return f"ERROR: el fragmento aparece {texto.count(antes)} veces; debe aparecer exactamente 1"
        p.write_text(texto.replace(antes, despues), encoding="utf-8")
        return f"OK: {ruta} modificado"

    def ver_cambios(self, original="../trabajo_original"):
        import difflib
        base, salida = self._ruta_libre(original), []
        for p in sorted(self.raiz.rglob("*.py")):
            rel = p.relative_to(self.raiz); q = base / rel
            a = q.read_text(encoding="utf-8").splitlines() if q.exists() else []
            salida += difflib.unified_diff(a, p.read_text(encoding="utf-8").splitlines(),
                                           f"a/{rel}", f"b/{rel}", lineterm="", n=1)
        return "\n".join(salida) or "(sin cambios)"

    def _ruta_libre(self, ruta):
        return (self.raiz / ruta).resolve()

    def ejecutar_comando(self, comando):
        argumentos = shlex.split(comando)
        if argumentos and argumentos[0] == "python":
            argumentos[0] = sys.executable
        r = subprocess.run(argumentos, shell=False, cwd=self.raiz, capture_output=True, text=True, timeout=60)
        return (r.stdout + r.stderr).strip()[-2000:]
