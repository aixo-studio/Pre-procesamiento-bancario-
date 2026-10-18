"""Prueba del extracto del Supervielle con un archivo inventado que imita la forma del real."""
from datetime import date

import openpyxl

from documentos.banco_supervielle import reglas
from motor.armar import armar_movimientos
from motor.escribir import controlar
from motor.leer import encontrar_tabla, leer_filas


def test_convierte_a_cuatro_columnas(tmp_path):
    libro = openpyxl.Workbook()
    hoja = libro.active
    hoja.append(reglas.ENCABEZADOS)
    hoja.append(["30/09/2026", "07:28", "CRED BCA ELECTR INTERBANC EXEN", "CUENTAS PROPIAS", 0, 500000, 400000])
    hoja.append(["29/09/2026", "02:28", "Impuesto Débitos y Créditos/DB", None, 900, 0, -100000])
    hoja.append(["29/09/2026", "02:28", "Pago Cheque de Cámara Recibida", "Número Cheque: 101", 150000.25, 0, -99100])
    ruta = tmp_path / "extracto.xlsx"
    libro.save(ruta)

    columnas, datos = encontrar_tabla(leer_filas(ruta), reglas.ENCABEZADOS)
    movimientos = armar_movimientos(columnas, datos, reglas)
    resumen = controlar(movimientos, columnas, datos, reglas)

    assert [m.fecha for m in movimientos] == [date(2026, 9, 30), date(2026, 9, 29), date(2026, 9, 29)]
    assert [m.concepto for m in movimientos][2] == "Pago Cheque de Cámara Recibida"
    assert [m.descripcion for m in movimientos] == ["CUENTAS PROPIAS", "", "Número Cheque: 101"]
    assert [m.monto_centavos for m in movimientos] == [50000000, -90000, -15000025]
    assert resumen["filas"] == 3 and resumen["ignoradas"] == 0
