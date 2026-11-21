# Lienzo de diseño del agente de mantenimiento de EcoRecicla AQP

El agente ayuda al equipo a resolver issues del módulo de solicitudes.
Recibe un issue y una prueba que lo reproduce. El equipo considera resuelto
el caso cuando pasa la prueba de aceptación y siguen pasando las pruebas
previas del comportamiento afectado.

| Decisión | Elección | Justificación para EcoRecicla AQP |
|---|---|---|
| 1. ¿Agente o flujo de trabajo? | Agente para investigar la acreditación duplicada. Flujo fijo para ejecutar las pruebas y para filtrar solicitudes por estado. | Para investigar el saldo duplicado hay que decidir qué revisar según lo observado en el publicador y sus suscriptores. En cambio, seleccionar solicitudes pendientes y comprobar el resultado con pytest tiene pasos conocidos. |
| 2. Arquetipo | ReAct para el Issue 01, flujo determinista para el Issue 02 y planificador-ejecutor para el Issue 03. | En el primero, cada lectura orienta la siguiente acción. En el segundo basta aplicar el criterio de estado. En el tercero se puede planificar la incorporación de la regla distrital y verificar por separado el distrito con bono y el distrito de control. |
| 3. Herramientas | Listar, buscar y leer archivos, editar el código autorizado, ejecutar pytest y revisar el diff. | Permiten seguir el recorrido de una acreditación, modificar el componente responsable y comprobar el resultado contra el criterio de aceptación. |
| 4. Memoria | Historial de corto plazo por issue con el objetivo, las acciones, los archivos consultados y los resultados de pytest. | El agente necesita recordar qué hipótesis ya comprobó y cuál fue el último fallo. Cada issue puede investigarse con su propio historial. |
| 5. Coordinación | Un agente para la primera ejecución. Para la etapa multiagente, un gestor organiza la tarea, un ejecutor propone cambios y un crítico revisa el diff y las pruebas. | El Issue 01 permite observar las decisiones de un solo agente. En la etapa coordinada, una revisión independiente puede detectar una solución que evita el duplicado, pero también descarta recojos legítimos. |
| 6. Rol humano | Un integrante valida la regla de negocio, revisa la evidencia y aprueba el pull request. | El equipo debe confirmar qué identifica una acreditación única y en qué distrito corresponde un bono antes de integrar el cambio. |
| 7. Control | Validar las decisiones con el contrato, limitar las herramientas por rol y fijar presupuestos de 12 pasos por agente y 2 rondas de revisión. | El contrato detecta decisiones mal formadas. Los permisos acotan los cambios y los límites detienen una investigación que repite acciones sin resolver el fallo. |