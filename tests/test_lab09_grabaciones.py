"""Evidencia real: integridad de capturas y reproducción por el generador de E6."""
import hashlib
import json
from pathlib import Path

import pytest

from src.solicitudes.generador_criterios import (
    DIRECTORIO_CRITERIOS as BASE,
    GeneradorCriterios,
    ProveedorCriteriosGrabado,
    SalidaInvalida,
)


CASOS = json.loads((BASE / 'dataset-congelado.json').read_text(encoding='utf-8'))


def test_grabaciones_originales_conservan_hash_y_sesion_independiente():
    manifiesto = json.loads((BASE / 'manifiesto.json').read_text(encoding='utf-8'))
    assert len(manifiesto) == 46
    assert len({m['sesion'] for m in manifiesto}) == 46
    for entrada in manifiesto:
        for archivo, campo in [('archivo', 'sha256'), ('entrada', 'prompt_sha256')]:
            assert hashlib.sha256((BASE / entrada[archivo]).read_bytes()).hexdigest() == entrada[campo]


@pytest.mark.parametrize('caso', CASOS, ids=[c['vars']['id'] for c in CASOS])
def test_generador_reproduce_caso_final_con_invest_esperado(caso):
    variables = caso['vars']
    archivo = BASE / 'grabaciones/v3' / (variables['id'] + '.txt')
    generado = GeneradorCriterios(ProveedorCriteriosGrabado(archivo), 'v3').generar(
        variables['id'], variables['historia'])
    assert generado['invest_ok'] is variables['invest_esperado']
    if generado['invest_ok']:
        tipos = {e['tipo'] for e in generado['escenarios']}
        assert 'exito' in tipos and tipos & {'error', 'borde'}
    else:
        assert generado['preguntas'] and not generado['escenarios']


def test_integracion_rechaza_linea_base_real_en_texto_libre():
    archivo = BASE / 'grabaciones/v1/HU-01.txt'
    with pytest.raises(SalidaInvalida, match='fuera de JSON'):
        GeneradorCriterios(ProveedorCriteriosGrabado(archivo), 'v1').generar('HU-01', CASOS[0]['vars']['historia'])


@pytest.mark.parametrize('repeticion', [1, 2, 3])
@pytest.mark.parametrize('id_historia, esperado', [('HU-01', True), ('HU-04', True), ('NI-01', False)])
def test_repeticiones_reales_se_validan_en_la_integracion(repeticion, id_historia, esperado):
    caso = next(c['vars'] for c in CASOS if c['vars']['id'] == id_historia)
    archivo = BASE / f'grabaciones/no-determinismo/r{repeticion}/{id_historia}.txt'
    salida = GeneradorCriterios(ProveedorCriteriosGrabado(archivo), 'v3').generar(id_historia, caso['historia'])
    assert salida['invest_ok'] is esperado
