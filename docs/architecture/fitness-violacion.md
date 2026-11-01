# E5.2 - Detección de degradación arquitectónica

- Fecha: 2026-10-31.
- Rama de prueba: `prueba/violacion`, creada desde `antony`.
- Commit base: `db0fd0ab07e840a07aa62b42630ad3b7b93fc608`.
- Python 3.12.14, import-linter 2.15 y pytest 9.2.0.
- Comando en cada ensayo: `lint-imports --no-cache`, con `PYTHONPATH=.`.

## Hallazgo inicial

Antes del ajuste, FF-01 pasó y FF-02 falló por `puntos -> externos`,
también alcanzable desde `decoradores -> puntos -> externos`.
Se retiraron el import de MinamPuntosAPI y la anotación del constructor;
la instancia se sigue inyectando desde servicio.py. Ambos contratos pasaron.

## Violación de FF-02

Se añadió temporalmente al final de eventos.py:

```python
from src.solicitudes.externos import WhatsAppSDK
```

Salida real, código de salida 1:

```text
Analyzed 12 files, 10 dependencies.
FF-01 Capas de solicitudes sin dependencias ascendentes KEPT
FF-02 Logica sin dependencias de externos BROKEN
Contracts: 1 kept, 1 broken.
src.solicitudes.eventos is not allowed to import src.solicitudes.externos:
- src.solicitudes.eventos -> src.solicitudes.externos (l.42)
```

Se retiró el import antes del segundo ensayo.

## Violación de FF-01

Se añadió temporalmente al final de estados.py:

```python
from src.solicitudes.servicio import ServicioSolicitudes
```

Salida real, código de salida 1:

```text
Analyzed 12 files, 10 dependencies.
FF-01 Capas de solicitudes sin dependencias ascendentes BROKEN
FF-02 Logica sin dependencias de externos BROKEN
Contracts: 0 kept, 2 broken.
src.solicitudes.estados is not allowed to import src.solicitudes.servicio:
- src.solicitudes.estados -> src.solicitudes.servicio (l.97)
src.solicitudes.estados is not allowed to import src.solicitudes.externos:
- src.solicitudes.estados -> src.solicitudes.servicio (l.97)
  src.solicitudes.servicio -> src.solicitudes.externos (l.3)
```

La dependencia ascendente también rompe FF-02 por la ruta indirecta.
No se ejecutó pytest mientras estuvo presente el ciclo deliberado.

## Restauración

Se retiró el segundo import. El diff de eventos.py y estados.py quedó
vacío y se volvió a antony, sin commits con las violaciones:

```text
FF-01 Capas de solicitudes sin dependencias ascendentes KEPT
FF-02 Logica sin dependencias de externos KEPT
Contracts: 2 kept, 0 broken.
```

La suite completa restaurada pasó con 59 pruebas.
