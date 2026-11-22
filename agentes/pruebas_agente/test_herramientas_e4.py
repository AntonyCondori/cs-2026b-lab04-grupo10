from agentes.agente.herramientas import Herramientas
from agentes.agente.politica import Politica


def test_mapa_repo_lista_simbolos_y_omite_directorios(tmp_path):
    modulo = tmp_path / "src" / "modulo.py"
    modulo.parent.mkdir()
    modulo.write_text(
        "# comentario\nclass Servicio:\n    def iniciar(self):\n        pass\n"
        "\nasync def consultar(a, b=2, *, activo=True):\n    pass\n",
        encoding="utf-8",
    )
    for nombre in (".git", "__pycache__", ".venv", "venv", "entorno"):
        carpeta = tmp_path / nombre
        carpeta.mkdir()
        (carpeta / "oculto.py").write_text("class Oculta: pass\n", encoding="utf-8")
    (tmp_path / "entorno" / "pyvenv.cfg").touch()

    mapa = Herramientas(str(tmp_path)).mapa_repo()

    assert mapa.splitlines() == [
        "src/modulo.py:",
        "  clase Servicio (línea 2)",
        "  función iniciar(self) (línea 3)",
        "  función consultar(a, b=2, *, activo=True) (línea 6)",
    ]


def test_mapa_repo_vacio(tmp_path):
    assert Herramientas(str(tmp_path)).mapa_repo() == ""


def test_mapa_repo_reporta_error_de_sintaxis_y_continua(tmp_path):
    (tmp_path / "invalido.py").write_text("def invalida(:\n", encoding="utf-8")
    (tmp_path / "valido.py").write_text("def valida(): pass\n", encoding="utf-8")

    mapa = Herramientas(str(tmp_path)).mapa_repo()

    assert "invalido.py:\n  Error de sintaxis (línea 1)" in mapa
    assert "valido.py:\n  función valida() (línea 1)" in mapa


def test_leer_notas_sin_archivo(tmp_path):
    assert Herramientas(str(tmp_path)).leer_notas() == ""
    assert not (tmp_path / "agentes").exists()


def test_anotar_crea_y_acumula_notas(tmp_path):
    herramientas = Herramientas(str(tmp_path))
    ruta = tmp_path / "agentes" / "notas.md"

    herramientas.anotar("Primera nota")
    assert ruta.read_text(encoding="utf-8") == "Primera nota\n"

    herramientas.anotar("Segunda nota")
    assert Herramientas(str(tmp_path)).leer_notas() == "Primera nota\nSegunda nota\n"


def test_anotar_normaliza_y_limita_la_longitud(tmp_path):
    herramientas = Herramientas(str(tmp_path))
    herramientas.anotar("A\r\nB\nC\r" + "á" * 500)

    assert herramientas.leer_notas() == "A B C " + "á" * 494 + "\n"


def test_anotar_separa_una_nota_previa_sin_salto_final(tmp_path):
    ruta = tmp_path / "agentes" / "notas.md"
    ruta.parent.mkdir()
    ruta.write_text("Nota previa", encoding="utf-8")
    herramientas = Herramientas(str(tmp_path))

    herramientas.anotar("Nota nueva")

    assert herramientas.leer_notas() == "Nota previa\nNota nueva\n"


def test_catalogo_registra_las_tres_herramientas(tmp_path):
    catalogo = Herramientas(str(tmp_path)).catalogo()

    assert catalogo["mapa_repo"].startswith("mapa_repo():")
    assert catalogo["anotar"].startswith("anotar(texto):")
    assert catalogo["leer_notas"].startswith("leer_notas():")


def test_politica_reserva_anotar_a_la_instancia_del_ejecutor():
    ejecutor = Politica()
    ejecutor.herramientas_permitidas.add("anotar")
    planificador = Politica()
    revisor = Politica()
    args = {"texto": "Nota"}

    assert ejecutor.evaluar("anotar", args, paso=1).permitido
    for politica in (planificador, revisor):
        decision = politica.evaluar("anotar", args, paso=1)
        assert not decision.permitido
        assert "Herramienta no permitida" in decision.motivo
    for politica in (ejecutor, planificador, revisor):
        assert politica.evaluar("mapa_repo", {}, paso=1).permitido
        assert politica.evaluar("leer_notas", {}, paso=1).permitido
