"""Paso 3 del proceso: armar Fecha, Código, Descripción y Monto para cada fila.

Qué columna va a cada lugar lo dice configuracion.toml para cada documento; acá solo
están las reglas que son iguales para todos.
"""
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass
class Movimiento:
    """Una fila del resultado: las cuatro columnas de la salida."""
    fecha: date
    codigo: str  # el valor que identifica el tipo de movimiento, siempre como texto
    descripcion: str
    monto_centavos: int  # crédito positivo, débito negativo


def esta_vacia(fila: list) -> bool:
    """Recibe una fila. Devuelve True si todas sus celdas están vacías."""
    return all(celda is None or str(celda).strip() == "" for celda in fila)


def a_texto(valor) -> str:
    """Recibe el valor de una celda. Lo devuelve como texto, tal cual;
    una celda vacía queda como texto vacío.
    """
    return "" if valor is None else str(valor)


def a_codigo(valor, numero_fila: int) -> str:
    """Recibe el valor de la celda del Código (y el número de fila, para avisar si falla).
    Lo devuelve como texto, tal cual. Si viene como número, frena con un error:
    un código como "005" guardado como número queda en 5 y ya no coincide con
    nada. Rellenar los ceros sería adivinar.
    """
    if isinstance(valor, (int, float)):
        raise ValueError(f"Fila {numero_fila}: el Código viene como número ({valor!r}), no como texto; "
                         "los ceros de adelante se pudieron perder. Bajá el archivo de nuevo del banco, sin abrirlo y guardarlo en Excel.")
    return a_texto(valor)


def a_centavos(valor, numero_fila: int) -> int:
    """Recibe un importe (y el número de fila, para avisar si falla).
    Devuelve el importe en centavos enteros. Una celda vacía vale 0.
    Si el valor no es un número, frena con un error.
    """
    if valor is None or str(valor).strip() == "":
        return 0
    if isinstance(valor, (int, float)):
        # Decimal evita errores de redondeo al pasar a centavos.
        return int((Decimal(str(valor)) * 100).to_integral_value())
    raise ValueError(f"Fila {numero_fila}: importe que no se puede leer: {valor!r}")


def a_fecha(valor, formato, numero_fila: int) -> date:
    """Recibe una fecha y el formato del documento (y el número de fila, para avisar si falla).
    Acepta una fecha real de Excel o un texto con ese formato, y devuelve la fecha.
    Si no la puede leer, frena con un error.
    """
    if isinstance(valor, datetime):
        return valor.date()
    try:
        return datetime.strptime(str(valor).strip(), formato).date()
    except (TypeError, ValueError):
        raise ValueError(f"Fila {numero_fila}: fecha que no se puede leer: {valor!r}") from None


def es_ignorada(fila: list, columnas: dict, reglas: dict) -> bool:
    """Recibe una fila. Devuelve True si el documento la marca para ignorar
    ("ignorar" en configuracion.toml), como el "Saldo Inicial".
    """
    ignorar = reglas.get("ignorar", {})
    return any(a_texto(fila[columnas[columna]]).strip() == valor for columna, valor in ignorar.items())


def armar_movimientos(columnas: dict, datos: list, reglas: dict) -> list[Movimiento]:
    """Recibe las filas de la tabla y las reglas del documento.
    Devuelve la lista de movimientos con sus cuatro columnas.
    Saltea las filas vacías y las ignoradas; si una fila no se puede leer, frena con un error.
    """
    movimientos = []
    for numero_fila, fila in datos:
        if esta_vacia(fila):
            continue
        if es_ignorada(fila, columnas, reglas):
            # Una fila ignorada no puede llevar plata: si la lleva, algo está mal.
            if a_centavos(fila[columnas[reglas["credito"]]], numero_fila) or a_centavos(fila[columnas[reglas["debito"]]], numero_fila):
                raise ValueError(f"Fila {numero_fila}: es una fila a ignorar pero tiene monto.")
            continue
        credito = abs(a_centavos(fila[columnas[reglas["credito"]]], numero_fila))
        # Se toma el débito sin signo y se lo pone negativo, venga como venga del banco.
        debito = abs(a_centavos(fila[columnas[reglas["debito"]]], numero_fila))
        # Cada movimiento tiene que tener crédito o débito: uno solo, nunca los dos ni ninguno.
        if (credito == 0) == (debito == 0):
            raise ValueError(f"Fila {numero_fila}: tiene que tener crédito o débito, uno solo.")
        movimientos.append(Movimiento(
            fecha=a_fecha(fila[columnas[reglas["fecha"]]], reglas.get("formato_fecha"), numero_fila),
            codigo=a_codigo(fila[columnas[reglas["codigo"]]], numero_fila),
            descripcion=a_texto(fila[columnas[reglas["descripcion"]]]),
            monto_centavos=credito - debito,
        ))
    return movimientos
