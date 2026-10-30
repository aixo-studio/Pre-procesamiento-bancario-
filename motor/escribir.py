"""Pasos 6 y 7 del proceso: controlar que no se perdió nada y escribir el Excel.

El extracto de un banco sale con dos hojas, "Movimientos" y "Gastos bancarios";
el libro del ERP, solo con "Movimientos". Las dos hojas tienen el mismo formato.
"""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from motor.armar import Movimiento, a_centavos, es_ignorada, esta_vacia


def controlar(armados: list[Movimiento], columnas: dict, datos: list, reglas: dict,
              movimientos: list[Movimiento] = None, gastos: list[Movimiento] = None) -> dict:
    """Recibe las filas armadas, las filas originales y, si es un extracto de banco,
    los movimientos y los gastos ya separados. Cuenta filas y suma créditos y
    débitos directo del original, y lo compara dos veces: contra lo armado (paso
    armar) y contra movimientos + gastos (paso separar). Sin separación (el libro
    del ERP), todo lo armado cuenta como movimientos. Si algo no cierra, frena
    con un error que dice en qué paso.
    Devuelve el resumen: filas, filas ignoradas, créditos, débitos y suma (en centavos).
    """
    if movimientos is None:
        movimientos, gastos = armados, []
    con_datos = [(numero, fila) for numero, fila in datos if not esta_vacia(fila)]
    filas_original = [(numero, fila) for numero, fila in con_datos if not es_ignorada(fila, columnas, reglas)]
    ignoradas = len(con_datos) - len(filas_original)
    creditos = sum(abs(a_centavos(fila[columnas[reglas["credito"]]], numero)) for numero, fila in filas_original)
    debitos = sum(abs(a_centavos(fila[columnas[reglas["debito"]]], numero)) for numero, fila in filas_original)
    suma_original = creditos - debitos
    # Paso armar: lo armado tiene que dar lo mismo que el original.
    suma = sumar(armados)
    if len(armados) != len(filas_original):
        raise ValueError(f"Se perdieron filas al armar: armadas {len(armados)}, original {len(filas_original)}.")
    if suma != suma_original:
        raise ValueError(f"La suma no cierra al armar: armado {suma / 100}, original {suma_original / 100}.")
    # Paso separar: las dos hojas juntas tienen que dar lo mismo que el original.
    # Mirar filas y suma juntas atrapa también una fila perdida y otra duplicada con el mismo monto.
    filas_separadas = len(movimientos) + len(gastos)
    if filas_separadas != len(filas_original):
        raise ValueError(f"Se perdieron filas al separar: Movimientos {len(movimientos)} + Gastos {len(gastos)} = "
                         f"{filas_separadas}, original {len(filas_original)}.")
    if sumar(movimientos) + sumar(gastos) != suma_original:
        raise ValueError(f"La suma no cierra al separar: Movimientos {sumar(movimientos) / 100} + "
                         f"Gastos {sumar(gastos) / 100}, original {suma_original / 100}.")
    return {"filas": len(armados), "ignoradas": ignoradas,
            "creditos": creditos, "debitos": debitos, "suma": suma}


def sumar(movimientos: list[Movimiento]) -> int:
    """Recibe una lista de movimientos. Devuelve la suma de sus montos, en centavos."""
    return sum(movimiento.monto_centavos for movimiento in movimientos)


def escribir_excel(movimientos: list[Movimiento], ruta: Path, gastos: list[Movimiento] = None) -> None:
    """Recibe los movimientos, la ruta donde guardar y, si es un extracto de banco,
    los gastos bancarios. Escribe la hoja "Movimientos" y, si hay lista de gastos
    (aunque esté vacía), la hoja "Gastos bancarios". Sin lista (el libro del ERP)
    queda una sola hoja.
    """
    libro = Workbook()
    libro.active.title = "Movimientos"
    escribir_hoja(libro.active, movimientos)
    # El extracto de un banco tiene siempre las dos hojas, aunque en el mes no haya gastos.
    if gastos is not None:
        escribir_hoja(libro.create_sheet("Gastos bancarios"), gastos)
    libro.save(ruta)


def escribir_hoja(hoja, movimientos: list[Movimiento]) -> None:
    """Recibe una hoja vacía y sus movimientos. Escribe el encabezado y las
    cuatro columnas, con formato de fecha y de monto. El Código se escribe como
    texto, así "005" no se convierte en 5. Se usa igual para las dos hojas.
    """
    # Encabezado en negrita.
    hoja.append(["Fecha", "Código", "Descripción", "Monto"])
    for celda in hoja[1]:
        celda.font = Font(bold=True)
    for movimiento in movimientos:
        hoja.append([movimiento.fecha, movimiento.codigo, movimiento.descripcion,
                     movimiento.monto_centavos / 100])
    # Formato: fecha dd/mm/aaaa y monto con separador de miles y dos decimales.
    for fecha, _, _, monto in hoja.iter_rows(min_row=2):
        fecha.number_format = "DD/MM/YYYY"
        monto.number_format = "#,##0.00"
    for letra, ancho in zip("ABCD", (12, 34, 50, 18)):
        hoja.column_dimensions[letra].width = ancho
    hoja.freeze_panes = "A2"  # el encabezado queda fijo al bajar
