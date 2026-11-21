# ISSUE-01 — Un evento repetido acredita dos veces el mismo recojo

**Tipo:** defecto sembrado para el laboratorio.

**Observado:** el vecino V01 completa el recojo 101 por 10 puntos.
Si el evento `solicitud_completada` se entrega dos veces, su saldo llega
a 20. Si después completa el recojo 102 por otros 10 puntos, termina con 30.

**Esperado:** el recojo 101 debe acreditarse una sola vez, aunque su evento
se repita. El recojo 102 sí debe sumar porque es una solicitud distinta.
Después de ambos recojos, V01 debe tener 20 puntos.

**Prueba que lo reproduce:**
`tests/test_issue_01.py::test_evento_repetido_acredita_una_vez_por_solicitud`