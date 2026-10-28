"""Prueba de los gastos bancarios: que la lista de cada banco esté bien cargada
en configuracion.toml y que un Código se reconozca como gasto solo si coincide
exacto. Las listas de prueba son inventadas, salvo las del config real.
"""
import pytest

from motor.configuracion import buscar_reglas_y_carpeta, controlar_gastos, es_gasto


@pytest.mark.parametrize("banco", ["BBVA", "Galicia", "Supervielle"])
def test_cada_banco_del_config_tiene_su_lista_de_gastos(banco):
    # Si a un banco le faltara la lista, buscar sus reglas ya frenaría.
    reglas, _ = buscar_reglas_y_carpeta(banco, es_erp=False)
    assert reglas["gastos"]


def test_el_erp_no_necesita_lista_de_gastos():
    reglas, carpeta = buscar_reglas_y_carpeta("BBVA", es_erp=True)
    assert "gastos" not in reglas and carpeta == "BBVA"


def test_es_gasto_compara_exacto():
    reglas = {"gastos": ["015", "236", "IVA"]}
    assert es_gasto("236", reglas)
    assert es_gasto("015", reglas)
    assert es_gasto("IVA", reglas)
    # Parecido no alcanza: sin los ceros, otra mayúscula o un espacio de más, no es gasto.
    assert not es_gasto("15", reglas)
    assert not es_gasto("iva", reglas)
    assert not es_gasto("IVA ", reglas)
    assert not es_gasto("319", reglas)
    assert not es_gasto("", reglas)


def test_es_gasto_con_las_listas_reales():
    bbva, _ = buscar_reglas_y_carpeta("BBVA", es_erp=False)
    galicia, _ = buscar_reglas_y_carpeta("Galicia", es_erp=False)
    supervielle, _ = buscar_reglas_y_carpeta("Supervielle", es_erp=False)
    assert es_gasto("236", bbva) and not es_gasto("319", bbva)
    assert es_gasto("000901 - Impuestos", galicia) and not es_gasto("000905 - Transferencias", galicia)
    assert es_gasto("IVA", supervielle) and not es_gasto("Pago Cheque de Cámara Recibida", supervielle)


def test_frena_si_falta_la_lista():
    with pytest.raises(ValueError, match='a "Nuevo" le falta la lista de gastos'):
        controlar_gastos("Nuevo", {"codigo": "Codigo"})


def test_frena_si_la_lista_esta_vacia():
    with pytest.raises(ValueError, match='a "Nuevo" le falta la lista de gastos'):
        controlar_gastos("Nuevo", {"gastos": []})


def test_frena_si_hay_codigos_repetidos():
    with pytest.raises(ValueError, match="hay códigos repetidos: 015"):
        controlar_gastos("Nuevo", {"gastos": ["015", "030", "015"]})


def test_una_lista_bien_cargada_pasa():
    controlar_gastos("Nuevo", {"gastos": ["015", "030"]})
