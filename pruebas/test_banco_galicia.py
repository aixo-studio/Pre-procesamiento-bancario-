"""Prueba del extracto del Galicia con un archivo inventado que imita la forma del real."""
from datetime import date, datetime

import openpyxl

from documentos.banco_galicia import reglas
from motor.armar import armar_movimientos
from motor.escribir import controlar
from motor.leer import encontrar_tabla, leer_filas


def fila(fecha, descripcion, debito, credito, concepto):
    """Arma una fila del extracto con las 16 columnas, completando las que no importan."""
    return [fecha, descripcion, None, debito, credito, "000000 - Grupo", concepto, None, None,
            None, "LEYENDA", None, None, None, "Imputado", 1000]


def test_convierte_a_cuatro_columnas(tmp_path):
    libro = openpyxl.Workbook()
    hoja = libro.active
    hoja.append(reglas.ENCABEZADOS)
    hoja.append(fila(datetime(2026, 9, 1), "Transf Inmed Cp", 150000, 0, "907268 - TRANSF INMED CP"))
    hoja.append(fila(datetime(2026, 9, 2), "Com. Deposito De Cheque      475", 1234.56, 0, "907188 - COM. DEPOSITO"))
    hoja.append(fila(datetime(2026, 9, 3), "Credito Prestamo", 0, 800000, "917133 - CREDITO PRESTAMO"))
    ruta = tmp_path / "extracto.xlsx"
    libro.save(ruta)

    columnas, datos = encontrar_tabla(leer_filas(ruta), reglas.ENCABEZADOS)
    movimientos = armar_movimientos(columnas, datos, reglas)
    resumen = controlar(movimientos, columnas, datos, reglas)

    assert [m.fecha for m in movimientos] == [date(2026, 9, 1), date(2026, 9, 2), date(2026, 9, 3)]
    assert movimientos[0].concepto == "907268 - TRANSF INMED CP"
    assert movimientos[1].descripcion == "Com. Deposito De Cheque      475"  # tal cual, con los espacios
    assert [m.monto_centavos for m in movimientos] == [-15000000, -123456, 80000000]
    assert resumen["filas"] == 3 and resumen["ignoradas"] == 0
