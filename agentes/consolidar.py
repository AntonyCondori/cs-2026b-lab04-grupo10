"""Genera métricas, observacion.md y diagramas a partir de los JSONL conservados."""
import json
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
AGENTES = RAIZ / "agentes"
TRAZAS = AGENTES / "trazas"


def cargar(rutas):
    return [json.loads(linea) for ruta in rutas for linea in ruta.read_text(encoding="utf-8").splitlines() if linea.strip()]


def medir(rutas):
    eventos = cargar(rutas)
    acciones = [e for e in eventos if e["tipo"] == "accion"]
    return {"decisiones": sum(e["tipo"] in {"accion", "final"} for e in eventos),
            "acciones": len(acciones),
            "rondas": max([int(p.stem.rsplit("_r", 1)[1]) if "_r" in p.stem and p.stem.rsplit("_r", 1)[1].isdigit() else 1 for p in rutas], default=0),
            "herramientas": sorted({e["accion"] for e in acciones if e["estado"] == "OBSERVANDO"}),
            "contrato": sum(e["estado"] == "CONTRATO_INVALIDO" for e in acciones),
            "bloqueos": sum(e["estado"] == "BLOQUEADO" for e in acciones),
            "limites": sum(e["estado"] == "LIMITE_ALCANZADO" for e in acciones),
            "contexto_registrado": sum(len(str(e["observacion"])[:600]) for e in acciones),
            "segundos": round(sum(max((e["t"] for e in eventos if e["agente"] == rol), default=0) for rol in {e["agente"] for e in eventos}), 3),
            "archivos": [p.relative_to(RAIZ).as_posix() for p in rutas]}


def tabla(mediciones):
    filas = ["| Ejecución | Decisiones (incl. final) | Acciones | Rondas | Contrato inválido | Bloqueos | Límite | Contexto registrado (car.) | Tiempo (s) |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for nombre, m in mediciones.items():
        filas.append(f"| {nombre} | {m['decisiones']} | {m['acciones']} | {m['rondas']} | {m['contrato']} | {m['bloqueos']} | {m['limites']} | {m['contexto_registrado']} | {m['segundos']} |")
    return "\n".join(filas)


def diagrama(eventos, nombre):
    nodos = [(e, f"n{i}") for i, e in enumerate(eventos) if e["tipo"] in {"accion", "final"}]
    mermaid = ['flowchart TD']
    dot = ['digraph trayectoria {', 'rankdir=TB; bgcolor="white"; node [shape=box, style="rounded,filled", fillcolor="#eef4fb", fontname="DejaVu Sans", fontsize=12];']
    anterior = None
    for evento, nodo in nodos:
        titulo = evento['agente'] + " | " + str(evento['paso']) + " | " + evento['estado']
        detalle = evento.get('accion', evento.get('texto', ''))[:75]
        etiqueta = titulo + "\n" + detalle
        mermaid.append(f"    {nodo}[{json.dumps(etiqueta.replace(chr(10), ' / '), ensure_ascii=False)}]")
        dot.append(f'{nodo} [label={json.dumps(etiqueta, ensure_ascii=False)}];')
        if anterior:
            mermaid.append(f"    {anterior} --> {nodo}")
            dot.append(f'{anterior} -> {nodo};')
        anterior = nodo
    dot.append('}')
    (TRAZAS / f"{nombre}.mmd").write_text("\n".join(mermaid) + "\n", encoding="utf-8")
    fuente = TRAZAS / f"{nombre}.dot"
    fuente.write_text("\n".join(dot), encoding="utf-8")
    subprocess.run(["dot", "-Tpng", str(fuente), "-o", str(TRAZAS / f"{nombre}.png")], check=True)


def main():
    grupos = {
        "Issue 01 · E2 histórico": [TRAZAS / "issue_01.jsonl"],
        "Issue 03 · E4 histórico": [TRAZAS / "issue_03.jsonl"],
        "Issue 02 · E5 actor-crítico histórico": [TRAZAS / f"{rol}.jsonl" for rol in ("planificador", "ejecutor", "revisor")],
        "E6 · simulación de aprobación": [TRAZAS / "e6" / "ejecutor.jsonl"],
    }
    for variante in ("uno", "tres"):
        grupos[f"Issue 02 · reto {variante} (grabado)"] = sorted((TRAZAS / f"reto_{variante}" / "trazas").glob("*.jsonl"))
    medidas = {nombre: medir(rutas) for nombre, rutas in grupos.items()}
    (TRAZAS / "metricas-consolidadas.json").write_text(json.dumps(medidas, ensure_ascii=False, indent=2), encoding="utf-8")
    diagrama(cargar(grupos["E6 · simulación de aprobación"]), "gobernanza_e6")
    democracia = TRAZAS / "reto_tres" / "trazas"
    orden = [democracia / f"{rol}_r1.jsonl" for rol in ("planificador", "ejecutor", "revisor_correccion", "revisor_diseno", "revisor_seguridad")]
    diagrama(cargar(orden), "democracia")
    texto = '''# E7. Observación del sistema agéntico — EcoRecicla AQP

Las primeras tres filas provienen de las trazas originales del equipo. Las corridas nuevas
usan decisiones grabadas escritas por Codex y ejecutan herramientas reales en copias temporales.
Las aprobaciones de las evidencias nuevas son simuladas y se identifican en resultado.json.
No se hicieron llamadas a un proveedor LLM ni se midieron tokens o costo monetario.

## Métricas reproducibles

''' + tabla(medidas) + '''

## Definiciones y límites de la comparación

- Una decisión corresponde a un evento accion o final. Las acciones incluyen intentos bloqueados y contratos inválidos; el objetivo inicial no cuenta.
- Las decisiones del actor-crítico se suman por rol; no se confunde el paso local final con los pasos de todo el sistema.
- Rondas significa rondas de ejecución/revisión; para el agente único se registra una ejecución.
- Contexto registrado es la suma de caracteres de observacion, truncada por el núcleo a 600 por evento. No es el contexto completo enviado al modelo (faltan objetivo, decisiones y observaciones completas). Se conserva el criterio empleado por Daniel para compararlo.
- Tiempo: suma de duración final de cada rol por archivo. Incluye espera humana en las trazas históricas y no la incluye en las reproducciones; no permite comparar velocidad de LLM.
- BLOQUEADO, CONTRATO_INVALIDO y LIMITE_ALCANZADO se cuentan por separado.
- El PDF reporta para el Issue 02 con agente único 10 acciones, 3640 caracteres y 158,291 s. Su JSONL no está en este clon; esos valores son referencia documental, no medición recalculada. La comparación controlada nueva sí conserva todas las trazas de uno y tres revisores.
- E2 y E4 resuelven defectos distintos; sus diferencias no aíslan el efecto de la memoria.

## Herramientas por ejecución

'''
    for nombre, medida in medidas.items():
        texto += f"- **{nombre}**: " + ", ".join(f"`{x}`" for x in medida["herramientas"]) + ".\n"
    uno = medidas["Issue 02 · reto uno (grabado)"]
    tres = medidas["Issue 02 · reto tres (grabado)"]
    texto += f'''
## Comparación del reto democrático

Ambas variantes nuevas parten del mismo selector defectuoso, aplican la misma corrección y
verifican la misma aceptación y tres casos adicionales: entrada vacía, todas canceladas,
orden/identidad y conservación de la entrada. En ambos casos la prueba obligatoria pasó.
Un revisor registró {uno['acciones']} acciones y tres revisores {tres['acciones']};
el incremento es {(tres['acciones']/uno['acciones']-1)*100:.1f} %.
El contexto registrado pasó de {uno['contexto_registrado']} a {tres['contexto_registrado']} caracteres
({(tres['contexto_registrado']/uno['contexto_registrado']-1)*100:.1f} % más).
La votación del caso de tres revisores fue unánime, 3/3, en una ronda.
El revisor de diseño inspeccionó el alcance y la reutilización del estado; seguridad ejecutó
las pruebas de gobernanza. Ninguno descubrió otro defecto del selector. Los casos adicionales
los escribió Codex al preparar el experimento, no fueron un descubrimiento autónomo de los revisores.
La reproducción muestra el costo de coordinación y el funcionamiento de la mayoría; al provenir
las decisiones de un mismo asistente no demuestra independencia entre tres LLM.
Para este defecto acotado, el revisor único sigue siendo suficiente.

## Incidentes observados

1. Issue 01: pytest detectó 30 puntos en lugar de 20 antes de la corrección.
2. Issue 02 histórico: el ejecutor y el revisor tuvieron PermissionError en pytest; el ejecutor logró otra corrida, pero el revisor aprobó sin una verificación propia completa exitosa. Su aprobación no se presenta como una suite verde independiente.
3. E6: args de tipo texto fue rechazado por contrato; el intento de editar tests fue bloqueado; una edición rechazada no se ejecutó; otra aprobada sí se ejecutó. Las entradas fueron programadas para probar el callback.
4. Los controles de comandos del framework aceptaban prefijos y usaban shell=True. Se quitaron los operadores de shell y la ejecución por shell; se probaron rutas con ../ y variantes de tests/.

## Trayectorias generadas automáticamente

![Aprobación y bloqueos de E6](trazas/gobernanza_e6.png)

![Reto de tres revisores](trazas/democracia.png)

Fuentes editables: trazas/gobernanza_e6.mmd y trazas/democracia.mmd; las imágenes se generan
con Graphviz desde los mismos eventos JSONL. Regeneración: `python -m agentes.consolidar`.
'''
    (AGENTES / "observacion.md").write_text(texto, encoding="utf-8")
    print(tabla(medidas))


if __name__ == "__main__":
    main()
