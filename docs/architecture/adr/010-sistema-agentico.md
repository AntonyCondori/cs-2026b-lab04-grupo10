# ADR-010: Sistema agéntico de mantenimiento de EcoRecicla AQP

- Estado: aceptado para el prototipo del Laboratorio 10.
- Alcance: diagnóstico y reparación de los tres issues; sin operación autónoma en producción.
- Base: guía Lab 10 y avances E1–E5 integrados por Antony y Daniel.

## Contexto

Los defectos afectan idempotencia de puntos, exclusión de solicitudes canceladas y bono por
distrito. Se requiere observar decisiones y resultados, validar contratos y limitar herramientas.
El caso de la ruta tiene una corrección local fácil de probar; multiplicar agentes tiene costo.
El revisor histórico aprobó pese a errores de permisos al ejecutar la suite, por lo que la
aprobación textual debe separarse de la evidencia de pruebas exitosas.

## Decisión

Usar un agente ReAct con estrategia intercambiable de modelo y máquina de estados:
DECIDIENDO → VALIDANDO_CONTRATO → EVALUANDO_POLITICA → EJECUTANDO → OBSERVANDO.
Un contrato inválido o bloqueo retorna como observación; una respuesta final termina.
El presupuesto finito limita las iteraciones incluso cuando hay errores de contrato.
Se conserva el comportamiento del núcleo: max_pasos + 1 oportunidades de decisión, para
admitir el final tras la última acción; una acción adicional se bloquea por límite.

Preferir agente único para correcciones pequeñas. Mantener actor-crítico como variante
comparativa: planificador sin herramientas, ejecutor con edición acotada y revisión de solo
lectura; máximo dos rondas. El reto democrático añade tres revisores de corrección, diseño y
seguridad, aprobación por mayoría estricta y una prueba de aceptación obligatoria exitosa.
Un voto mal formado no aprueba. Los errores de evidencia en las revisiones grabadas se
convierten en CAMBIOS. La ejecución de pytest, también en la puerta obligatoria, usa el
intérprete activo y no depende de un comando python global.

Herramientas: lectura, búsqueda, mapa AST, diff, pruebas, edición exacta y notas, con catálogo
filtrado por rol. En el reto se reduce al ejecutor a leer_archivo, editar_archivo, pruebas_issue,
ver_cambios; los revisores no reciben herramientas de edición ni shell. Las ediciones solo
pueden dirigirse a src/, sin rutas absolutas o componentes ..; se mantiene el sandbox de rutas.
Se elimina la ejecución shell=True del framework para evitar encadenamiento de comandos.

Memoria: historial de trabajo por rol; mapa_repo como índice estructural y notas.md como
pizarra persistente. No se incorporan embeddings ni base vectorial para tres defectos acotados.
Las notas no son automáticamente confiables ni se convierten en permisos.

Rol humano actual: revisor. aprobar_edicion muestra el fragmento antes/después y exige s/n;
respuesta inválida repregunta y EOF/interrupción rechazan. Callback activo en el ejecutor de
ambos orquestadores. El modo de reproducción con autorización programada se identifica
expresamente como simulado, y no constituye aprobación humana real.

Observabilidad: trazas JSONL por rol/ronda, decisiones JSON, votos y resultado agregado,
diffs y diagramas Mermaid/PNG generados. Consolidar métricas con definiciones reproducibles.
Se preservan las trazas originales y se separan las nuevas reproducciones en carpetas propias.

## Alternativas consideradas

1. Flujo fijo para todo: apropiado para la regla de selección y pruebas, insuficiente para investigar causas desconocidas.
2. Un agente sin contrato o aprobación: menor fricción, pero no permite controlar decisiones inválidas ni escritura inesperada.
3. Tres revisores siempre: más acciones y contexto; en este caso no encontraron otro defecto del selector y no justifican su costo habitual.
4. Autonomía de colaborador/gobernador: postergada hasta tener historial estable, revisión exitosa e independencia comprobada.
5. Proveedor LLM con API: opcional; las grabaciones permiten reproducir sin credenciales, pero no evaluar razonamiento autónomo ni diversidad real de modelos.

## Consecuencias

Los guardrails y pruebas hacen visibles los errores y permiten repetir el experimento.
La intervención humana añade espera y la coordinación democrática repite lecturas y diff.
La suma de observaciones truncadas no mide contexto completo ni tokens. El tiempo histórico
incluye interacción humana, mientras que el de las grabaciones mide ejecución local.
pytest ejecuta código del repositorio: el sandbox de rutas y el catálogo no sustituyen aislamiento
del sistema operativo. No se autoriza despliegue, acceso a secretos ni integración automática.
La publicación del tag y la entrega al Aula Virtual son pasos distintos de la preparación local.

## Evidencia

- agentes/delegacion.md, observacion.md y bitacora-ia.md.
- agentes/trazas/e6/, reto_uno/ y reto_tres/.
- agentes/pruebas_agente/test_politica_e6.py y test_democracia.py.
- agentes/revision-integracion.md y agentes/validacion.txt.
