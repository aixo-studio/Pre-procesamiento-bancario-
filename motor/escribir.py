"""Pasos 4 y 5 del proceso: controlar que no se perdió nada y escribir el Excel."""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font

from motor.armar import Movimiento, a_centavos, es_ignorada, esta_vacia


def controlar(movimientos: list[Movimiento], columnas: dict, datos: list, reglas: dict) -> dict:
    """Recibe los movimientos armados y las filas originales.
    Vuelve a contar filas y a sumar créditos y débitos directo del original, y los
    compara con los movimientos. Si algo no cierra, frena con un error.
    Devuelve el resumen: filas, filas ignoradas, créditos, débitos y suma (en centavos).
    """
    con_datos = [(numero, fila) for numero, fila in datos if not esta_vacia(fila)]
    filas_original = [(numero, fila) for numero, fila in con_datos if not es_ignorada(fila, columnas, reglas)]
    ignoradas = len(con_datos) - len(filas_original)
    creditos = sum(abs(a_centavos(fila[columnas[reglas["credito"]]], numero)) for numero, fila in filas_original)
    debitos = sum(abs(a_centavos(fila[columnas[reglas["debito"]]], numero)) for numero, fila in filas_original)
    suma = sum(movimiento.monto_centavos for movimiento in movimientos)
    if len(movimientos) != len(filas_original):
        raise ValueError(f"Se perdieron filas: salida {len(movimientos)}, original {len(filas_original)}.")
    if suma != creditos - debitos:
        raise ValueError(f"La suma no cierra: salida {suma / 100}, original {(creditos - debitos) / 100}.")
    return {"filas": len(movimientos), "ignoradas": ignoradas,
            "creditos": creditos, "debitos": debitos, "suma": suma}


def escribir_excel(movimientos: list[Movimiento], ruta: Path) -> None:
    """Recibe los movimientos y la ruta donde guardar.
    Escribe un Excel con una sola hoja, "Movimientos": el encabezado y las
    cuatro columnas, con formato de fecha y de monto. El Código se escribe como
    texto, así "005" no se convierte en 5.
    """
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Movimientos"
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
    libro.save(ruta)
