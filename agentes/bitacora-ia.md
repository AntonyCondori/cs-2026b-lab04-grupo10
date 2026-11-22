# E7. Bitácora de asistencia de IA — Lab 10

Las primeras entradas reconstruyen interacciones a partir de las decisiones y observaciones
conservadas por Antony y Daniel; no son una transcripción inventada de sus chats.
Las últimas corresponden al trabajo de Codex solicitado por Diego en esta sesión.

| N.º | Procedencia / solicitud | Propuesta o acción registrada | Evidencia y resultado | Decisión del equipo / límite |
|---|---|---|---|---|
| 1 | Antony, E2: investigar puntos duplicados | Leer Issue 01 y ejecutar su prueba antes de editar. | issue_01.jsonl, paso 3: pytest falla con 30 frente a 20. | Fallo real detectado por la aceptación; no se cambió el resultado esperado. |
| 2 | Antony, E2: corregir sin perder recojos distintos | Registrar solicitudes_acreditadas y omitir eventos repetidos. | issue_01.jsonl, pasos 5–7: edición, 1 passed y revisión de diff. | La solución conserva la suma de solicitudes diferentes. |
| 3 | Daniel, E4: ubicar código y guardar hipótesis | mapa_repo y anotar sobre el Issue 03. | issue_03.jsonl y notas.md; 11 acciones y 4328 caracteres registrados. | No afirmar ahorro: E2 usó 7 acciones y 2994 caracteres, resolviendo otro defecto. |
| 4 | Daniel, E5: excluir canceladas | El ejecutor reproduce, corrige el filtro y comprueba pytest. | ejecutor.jsonl: prueba focal pasa; suite inicial tiene errores de permisos y una repetición logra 107 passed, 4 skipped. | Reintento registrado; conservar ambos resultados. |
| 5 | Daniel, E5: pedir revisión separada | El revisor consulta diff y lanza la suite. | revisor.jsonl: PermissionError; el final dice APROBADO basándose además en la corrida del ejecutor. | Limitación detectada: no es una verificación independiente exitosa de toda la suite. |
| 6 | Diego solicita completar E6–E8 y el reto según ambos PDF | Codex identifica las secciones vacías y los cambios ya integrados en main. | PDF de Condori, reparto B2; merges locales #30 y #31; estado inicial limpio. | Continuar el trabajo previo y conservar sus trazas originales. |
| 7 | E6: aprobación explícita y errores | Codex implementa callback s/n, repregunta, rechazo por EOF y controles de rutas; ejecuta demostración aislada. | trazas/e6: contrato rechaza args texto, política bloquea tests y edición denegada; segunda edición se aplica. | Entradas simuladas declaradas; disponible modo humano para captura real. |
| 8 | Reto A: comparar uno y tres revisores | Codex escribe decisiones grabadas con focos de corrección, diseño y seguridad; ejecuta herramientas reales y añade puerta de pytest. | reto_uno/ y reto_tres/: misma siembra y parche, aceptación + casos adicionales pasan; mayoría 3/3. | No atribuir independencia a las grabaciones del mismo asistente ni inventar llamadas LLM. |
| 9 | E7–E8: consolidar métricas y completar entrega | Codex genera tabla desde JSONL, diagramas, ADR-010, README e informe con comandos de capturas. | consolidar.py; observacion.md; revision-integracion.md y validacion.txt. | Distinguir contexto registrado de contexto real, tag local de publicación remota y revisión local de aprobación en GitHub. |

Incidencia del entorno: no había pytest en python3 ni acceso DNS para instalar desde PyPI.
Se reutilizaron los paquetes ya presentes en `/home/diego/.venvs/ecorecicla-lab09`
copiándolos al entorno local `.venv`; no se modificó el entorno anterior.
