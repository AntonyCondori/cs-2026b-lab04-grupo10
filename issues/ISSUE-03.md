# ISSUE-03 — El cálculo de puntos ignora el bono distrital de plástico

**Tipo:** regla de negocio propuesta para el laboratorio.

**Observado:** un recojo de plástico otorga 10 puntos tanto en D01 como
en D02 porque el cálculo solo considera el material.

**Esperado:** para plástico, D01 recibe los 10 puntos base más un bono
de 5, para un total de 15. D02 conserva los 10 puntos base.

**Prueba que lo reproduce:**
`tests/test_issue_03.py::test_bono_de_plastico_solo_en_distrito_d01`