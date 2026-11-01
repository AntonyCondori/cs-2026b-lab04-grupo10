"""Matriz de valoraciones propuestas por el equipo; no son frecuencias medidas."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

riesgos = {"R1": (3, 4), "R2": (3, 4), "R3": (4, 4),
           "R4": (3, 5), "R5": (3, 4), "R6": (4, 3)}
datos = [[0 if p*i <= 3 else 1 if p*i <= 7 else 2 if p*i < 15 else 3
          for i in range(1, 6)] for p in range(1, 6)]
fig, ax = plt.subplots(figsize=(7.4, 6))
ax.imshow(datos, origin="lower", extent=(.5,5.5,.5,5.5),
          cmap=ListedColormap(["#dcfce7", "#fef3c7", "#fed7aa", "#fecaca"]),
          vmin=0, vmax=3)
for p in range(1,6):
    for i in range(1,6):
        ax.text(i-.38, p+.29, str(p*i), fontsize=8, color="#555555")
grupos = {}
for nombre, (p,i) in riesgos.items():
    grupos.setdefault((p,i), []).append(nombre)
for (p,i), nombres in grupos.items():
    ax.text(i,p,"\n".join(nombres),ha="center",va="center",weight="bold",fontsize=11)
ax.set(xticks=range(1,6), yticks=range(1,6), xlabel="Impacto (1 a 5)",
       ylabel="Probabilidad (1 a 5)", title="EcoRecicla AQP - Matriz de riesgos propuesta")
ax.set_xticks([.5,1.5,2.5,3.5,4.5,5.5], minor=True)
ax.set_yticks([.5,1.5,2.5,3.5,4.5,5.5], minor=True)
ax.grid(which="minor",color="white",linewidth=2)
ax.legend(handles=[Patch(color=c,label=l) for c,l in zip(
    ["#dcfce7","#fef3c7","#fed7aa","#fecaca"],
    ["Baja: 1-3","Media: 4-7","Alta: 8-14","Crítica: 15-25"])],
    loc="upper center",bbox_to_anchor=(.5,-.13),ncol=2,frameon=False)
fig.text(.5,.02,"Valoraciones del equipo; revisar al integrar B y C.",ha="center",fontsize=9)
fig.tight_layout(rect=(0,.07,1,1))
salida=Path(__file__).with_name("matriz.png")
fig.savefig(salida,dpi=180,bbox_inches="tight")
print(salida)
