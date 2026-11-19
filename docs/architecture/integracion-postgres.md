# Lab 08 · Solicitudes, confirmaciones y abonos en PostgreSQL

`crear_ciclo_postgres` ensambla `SolicitarRecojoService` para el alta y `GestionarRecojoService` para consultar, asignar, pesar y confirmar. Ambos comparten `RepositorioSolicitudesPostgres`. El punto de arranque recibe el distrito del contexto autorizado por la aplicación. La creación, el listado y las operaciones sobre una solicitud se restringen a ese distrito.

La confirmación reserva la fila, coteja los datos de un reenvío y guarda la transición, confirmación y abono en una sola transacción. La clave es única por distrito y una solicitud admite un solo abono. Los puntos se calculan con la fábrica y las reglas vigentes por tipo de residuo. Para el caso de laboratorio, el pesaje real se registra como un único total por solicitud.

| Verificación local con PostgreSQL 16.2 | Resultado |
|---|---|
| QA-04: 100 envíos, 10 concurrentes | 1 confirmación, 1 abono y el mismo resultado en los reenvíos, incluso al reconstruir el servicio |
| QA-03: 100 lecturas y 100 escrituras cruzadas | 200 operaciones rechazadas. Los listados y las consultas propias conservaron sus resultados. |
| Conflictos | Se rechazó otra clave para la misma solicitud, el cambio de peso y el reuso de la clave en otra solicitud del mismo distrito. Otro distrito conservó su propio espacio de claves. |
| Falla al insertar el abono | Se revirtieron confirmación y transición. La solicitud quedó `PESADA` y pudo reintentarse. |
| Regresión | 71 pruebas aprobadas con PostgreSQL y 2 contratos de imports aprobados |

## Reproducción y capturas

Con una base PostgreSQL de pruebas, desde la raíz del repositorio:

```bash
python -m pip install 'pytest==9.2.0' 'psycopg[binary]==3.3.9' 'import-linter==2.15'
export ECORECICLA_POSTGRES_DSN='postgresql://usuario:clave@localhost:5432/ecorecicla_test'
python -m pytest -v tests/test_recojo_postgres.py
python -m pytest -q
lint-imports --no-cache
```

La suite crea un esquema temporal por prueba y aplica `src/solicitudes/sql/001_solicitudes.sql`. Si se usa una base destinada a la aplicación, aplicar esa migración mediante `psql "$ECORECICLA_POSTGRES_DSN" -v ON_ERROR_STOP=1 -f src/solicitudes/sql/001_solicitudes.sql`.

Para el informe, capturar los cuatro resultados del módulo PostgreSQL y el resumen de regresión. Adjuntar el enlace del job `postgres` del PR cuando GitHub Actions lo ejecute. Las pruebas cubren los servicios Python y PostgreSQL. La autenticación HTTP, RLS y el despliegue de la arquitectura objetivo siguen pendientes.
