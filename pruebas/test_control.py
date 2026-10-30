"""Prueba del control: lo armado y las dos hojas (movimientos + gastos) se comparan
contra el original, en filas y en suma, y si algo no cierra el error dice en qué
paso falló. Se rompen las listas a propósito. Todo con datos inventados.
"""
from dataclasses import replace

import pytest

from motor.armar import armar_movimientos
from motor.configuracion import buscar_reglas_y_carpeta
from motor.escribir import controlar
from motor.separar import separar_gastos

ENCABEZADO_BBVA = ["Fecha", "Fecha Valor", "Concepto", "Codigo", "Número Documento",
                   "Oficina", "Crédito", "Débito", "Detalle"]
REGLAS, _ = buscar_reglas_y_carpeta("BBVA", es_erp=False)
COLUMNAS = {nombre: posicion for posicion, nombre in enumerate(ENCABEZADO_BBVA)}
# Un extracto inventado: 319 y 005 son movimientos; 236 y 015 son gastos (lista real del BBVA).
DATOS = [(numero, ["30-09-2026", "30-09-2026", "X", codigo, "", "OF", credito, debito, ""])
         for numero, (codigo, credito, debito) in enumerate(
             [("319", 2500, ""), ("236", "", -12.5), ("005", "", -1500), ("015", "", -12.5)], start=2)]


def armar_y_separar():
    """Arma el extracto inventado y lo separa. Devuelve lo armado, movimientos y gastos."""
    armados = armar_movimientos(COLUMNAS, DATOS, REGLAS)
    return (armados, *separar_gastos(armados, REGLAS))


def test_todo_bien_pasa():
    armados, movimientos, gastos = armar_y_separar()
    resumen = controlar(armados, COLUMNAS, DATOS, REGLAS, movimientos, gastos)
    assert resumen["filas"] == 4 and resumen["suma"] == 250000 - 1250 - 150000 - 1250


def test_sin_separar_funciona_como_antes():
    # El libro del ERP no se separa: todo lo armado cuenta como movimientos.
    armados, _, _ = armar_y_separar()
    assert controlar(armados, COLUMNAS, DATOS, REGLAS)["filas"] == 4


def test_frena_si_se_pierde_una_fila_al_armar():
    armados, movimientos, gastos = armar_y_separar()
    with pytest.raises(ValueError, match="Se perdieron filas al armar: armadas 3, original 4"):
        controlar(armados[:-1], COLUMNAS, DATOS, REGLAS, movimientos, gastos)


def test_frena_si_se_pierde_una_fila_al_separar():
    armados, movimientos, gastos = armar_y_separar()
    with pytest.raises(ValueError, match=r"Se perdieron filas al separar: Movimientos 2 \+ Gastos 1 = 3, original 4"):
        controlar(armados, COLUMNAS, DATOS, REGLAS, movimientos, gastos[:-1])


def test_frena_si_una_fila_queda_en_las_dos_hojas():
    armados, movimientos, gastos = armar_y_separar()
    with pytest.raises(ValueError, match="Se perdieron filas al separar"):
        controlar(armados, COLUMNAS, DATOS, REGLAS, movimientos + [gastos[0]], gastos)


def test_frena_si_se_duplica_una_fila_al_separar():
    armados, movimientos, gastos = armar_y_separar()
    with pytest.raises(ValueError, match="Se perdieron filas al separar"):
        controlar(armados, COLUMNAS, DATOS, REGLAS, movimientos, gastos + [gastos[0]])


def test_frena_si_cambia_un_monto_al_separar():
    armados, movimientos, gastos = armar_y_separar()
    cambiado = [replace(gastos[0], monto_centavos=gastos[0].monto_centavos - 1)] + gastos[1:]
    with pytest.raises(ValueError, match="La suma no cierra al separar"):
        controlar(armados, COLUMNAS, DATOS, REGLAS, movimientos, cambiado)


def test_frena_si_cambia_un_monto_al_armar():
    armados, movimientos, gastos = armar_y_separar()
    cambiado = [replace(armados[0], monto_centavos=armados[0].monto_centavos + 1)] + armados[1:]
    with pytest.raises(ValueError, match="La suma no cierra al armar"):
        controlar(cambiado, COLUMNAS, DATOS, REGLAS, movimientos, gastos)
