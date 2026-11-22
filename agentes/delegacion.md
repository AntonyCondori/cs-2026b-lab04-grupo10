# E6. Delegación progresiva en EcoRecicla AQP

## Decisión actual

Mantener al humano como **revisor**: el agente investiga, propone el fragmento antes/después,
la persona autoriza cada edición con `s` o `n`, y el equipo revisa la integración. El callback
`aprobar_edicion` se conecta a la política del ejecutor en `orquestador.py` y en la variante
democrática. El presupuesto es 12 pasos para el ejecutor, 8 por revisor y dos rondas.
No se conceden permisos para merge, push, despliegue ni acceso a credenciales.

| Rol humano | Permisos del agente en esa etapa | Responsabilidad humana | Evidencia para avanzar |
|---|---|---|---|
| Ejecutor | Leer issues y código; sugerir plan y parche; la persona ejecuta las modificaciones y pruebas. | Aplicar y comprobar cada acción. | Contratos válidos, diagnóstico reproducible de los tres issues, pruebas que fallan antes y pasan después y ausencia de accesos fuera del alcance. |
| Revisor (actual) | Investigar y ejecutar pruebas; proponer ediciones en src/ sujetas al callback; tests/ y rutas externas protegidos. | Aprobar/rechazar cada diff y aceptar el resultado final. | Varias tareas representativas sin correcciones humanas; pruebas completas y revisión sin errores de infraestructura; rechazos efectivos, límites respetados y evidencia de recuperación. |
| Colaborador | En un entorno aislado, editar automáticamente módulos autorizados de bajo impacto, conservando límites y revisión final. | Acordar alcance y criterios, resolver ambigüedades y revisar el PR. | Historial de calidad estable, cobertura de regresión y rutas adversarias, trazas completas, rollback comprobado y reducción medible de errores/costo. |
| Gobernador | Ejecutar tareas rutinarias de bajo riesgo bajo reglas predefinidas, con escalamiento por incertidumbre y auditoría. | Fijar políticas, monitorear y detener; aprobar operaciones de alto impacto. | Auditoría sostenida, métricas y alertas confiables, aislamiento reforzado y mecanismos de parada/recuperación probados. |

Las dos últimas etapas son una propuesta; no están habilitadas por este laboratorio.

## Mínimo privilegio por rol agéntico

- Planificador: sin herramientas de ejecución; entrega el plan.
- Ejecutor: en la variante democrática solo leer_archivo, editar_archivo, pruebas_issue y ver_cambios. Editar solo bajo src/, sin ../ ni rutas absolutas; callback previo a la escritura.
- Revisores: solo lectura, diff y pruebas prefijadas. No editar_archivo, anotar ni ejecutar_comando.
- La mayoría requiere 2/3, conserva las objeciones minoritarias y nunca sustituye la prueba de aceptación obligatoria.
- El orquestador interactivo original conserva sus herramientas de E5, pero se activó el callback de edición. Se quitó shell=True de la herramienta de comandos y se rechazan operadores de shell. Estas barreras son controles didácticos; pytest ejecuta código del repositorio y no constituye un aislamiento a nivel de sistema operativo.

## Evidencia reproducible

`python -m agentes.ejecutar_e6 --simular` produjo `trazas/e6/ejecutor.jsonl` y
`trazas/e6/resultado.json`. Se usaron respuestas **programadas** `quizá`, `n`, `s`:
entrada inválida repreguntada; primer parche denegado; segundo autorizado.
No se atribuye esta aprobación a Diego ni a otra persona. La traza muestra:

1. CONTRATO_INVALIDO: args fue un texto y no un objeto; no se llamó a la herramienta.
2. BLOQUEADO: intento de modificar tests/; no se consultó al callback.
3. BLOQUEADO: rechazo de la edición en src/; el archivo conserva valor = 1.
4. OBSERVANDO: la segunda edición se aplica tras s.
5. OBSERVANDO: la lectura muestra valor = 2.

La prueba `test_rechazo_no_modifica_y_siguiente_aprobacion_si` inspecciona el archivo
antes de ambas propuestas y confirma que el rechazo no escribió nada.
Para obtener evidencia humana real en una carpeta separada:

```bash
python -m agentes.ejecutar_e6 --salida agentes/trazas/e6_humano
```

Escribir `quizá`, luego `n` y finalmente `s`. No usar `--simular` en esa captura.
EOF e interrupción se interpretan como rechazo; no hay autorización por defecto.
La evidencia disponible no justifica pasar a colaborador: el revisor histórico aprobó
con errores de permisos y las nuevas corridas usan decisiones grabadas de un solo asistente.
