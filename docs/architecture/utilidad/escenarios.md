# Árbol de utilidad — EcoRecicla AQP 2.0

Crecimiento: de 3 a 12 distritos, cada uno con su propia regla de puntos y horario de recojo. Atributos críticos: modificabilidad y multitenencia. Restricciones vigentes: 1 mes, 3 desarrolladores, presupuesto bajo y monolito modular (ADR-001).

![Árbol de utilidad](arbol.png)

## Escenarios de seis partes

| ID | Atributo | Fuente | Estímulo | Entorno | Artefacto | Respuesta | Medida |
|---|---|---|---|---|---|---|---|
| QA-01 | Modificabilidad | Desarrollador del equipo | Incorporar una regla de puntos nueva (un material o una campaña) | Desarrollo, con la suite de regresión | Módulo Puntos (Strategy, Factory, Decorator) y punto de arranque | Registrar la regla sin cambiar el código de lógica existente | 0 archivos de lógica modificados, ≤ 15 líneas nuevas, 45 de 45 pruebas aprobadas |
| QA-02 | Modificabilidad | Municipalidad | Activar un distrito nuevo con su regla de puntos y su horario | Ensayo previo al despliegue | Identidad y distritos, Puntos y configuración | Configurar el distrito sin tocar otros módulos | ≤ 16 h-persona, 0 archivos modificados en otros módulos, 100 % de regresión |
| QA-03 | Seguridad | Usuario autenticado del distrito A | Consultar solicitudes y datos del distrito B | Operación normal con dos distritos de prueba | API, autorización y repositorios | Denegar sin exponer ni cambiar datos ajenos | 0 filas del distrito B en 100 de 100 intentos |
| QA-04 | Disponibilidad | Celular del reciclador con red inestable | Reenviar 100 veces la misma confirmación, 10 de ellas simultáneas | Operación normal con fallas intermitentes | Recolección y Puntos | Devolver el resultado original al duplicado | 1 recojo confirmado y 1 abono de puntos, 0 duplicados |
| QA-05 | Disponibilidad | Reciclador en zona sin señal | Registrar recojos sin conexión hasta 2 h | PWA en el celular (ADR-003) | PWA y sincronización | Guardar localmente y sincronizar al volver la señal | 100 % de los recojos sincronizados en ≤ 5 min tras recuperar la señal |
| QA-06 | Rendimiento | Reciclador | Consultar la ruta del día | Jornada con 12 distritos | Módulo Rutas y base de datos | Devolver la lista ordenada de paradas | p95 ≤ 1000 ms a 20 req/s (valores propuestos; calibrar) |

## Calificaciones (importancia para el negocio, dificultad técnica)

| ID | Calificación | Justificación |
|---|---|---|
| QA-01 | (H,M) | Es el atributo crítico del caso (R-04). El mecanismo del Lab 07 ya existe, pero faltaba un punto de arranque donde registrar reglas. |
| QA-02 | (H,H) | Es el detonante del crecimiento. El código actual no tiene el concepto de distrito, así que hay que diseñarlo. |
| QA-03 | (H,M) | Una fuga entre distritos rompe la confianza municipal. Es difícil de verificar, pero se resuelve con un filtro obligatorio. |
| QA-04 | (H,M) | Duplicar puntos afecta directamente a los vecinos (QA-02 de drivers.md). Hoy no hay protección contra duplicados. |
| QA-05 | (M,M) | Depende de la conectividad (supuesto S-01) y afecta a un solo rol. |
| QA-06 | (M,L) | drivers.md pide solo "carga moderada"; no hay medición del MVP que muestre un cuello de botella. |

## Corrección de una calificación de la IA

Al aplicar el Prompt IA 1, la IA calificó QA-05 (registrar recojos sin conexión) como (H,M), porque los recicladores trabajan en la calle y perder un recojo es costoso. El equipo lo bajó a (M,M) porque drivers.md no tiene ningún requisito ni escenario de operación sin conexión: la conectividad es un supuesto (S-01), no un requisito, y afecta a un solo rol.

## Cobertura

Los 4 atributos (modificabilidad, seguridad, disponibilidad, rendimiento) tienen al menos un escenario, y hay escenarios (H,H) o (H,M) en modificabilidad, seguridad y disponibilidad. Ninguna medida usa palabras como "rápido", "seguro" o "fácil".
