# ISSUE-02 — Una solicitud cancelada aparece en la planificación de la ruta

**Tipo:** defecto sembrado para el laboratorio.

**Observado:** al planificar la ruta con la solicitud 201 pendiente y la
solicitud 202 cancelada, el selector devuelve ambas como paradas.

**Esperado:** entre estas candidatas, la ruta debe contener únicamente
la solicitud 201. El reciclador no debe recibir una parada por el recojo
cancelado.

**Prueba que lo reproduce:**
`tests/test_issue_02.py::test_ruta_incluye_pendiente_y_excluye_cancelada`