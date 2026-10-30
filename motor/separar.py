"""Paso 5b del proceso: separar los gastos bancarios del resto de los movimientos.

Solo para el extracto de un banco: el libro del ERP no tiene gastos bancarios.
Qué es gasto lo decide es_gasto(), con la lista de cada banco en configuracion.toml;
acá solo se reparten las filas.
"""
from motor.armar import Movimiento
from motor.configuracion import es_gasto


def separar_gastos(movimientos: list[Movimiento], reglas: dict) -> tuple[list[Movimiento], list[Movimiento]]:
    """Recibe los movimientos armados y las reglas del banco.
    Recorre las filas una sola vez y manda cada una a un solo lado: a gastos si
    su Código es gasto, a movimientos si no. Cada lado mantiene el orden del
    original. Devuelve las dos listas: movimientos (sin gastos) y gastos.
    """
    sin_gastos, gastos = [], []
    for movimiento in movimientos:
        # Cada fila va a una sola lista: así no se puede duplicar ni quedar afuera.
        if es_gasto(movimiento.codigo, reglas):
            gastos.append(movimiento)
        else:
            sin_gastos.append(movimiento)
    return sin_gastos, gastos
