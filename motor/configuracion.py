"""Antes de convertir: trae de configuracion.toml las reglas del documento a limpiar.

Cada banco tiene su sección (las reglas de su extracto, su carpeta de salida y
su lista de gastos bancarios); el libro del ERP tiene una sola sección, igual
para todas las cuentas, y no tiene gastos bancarios.
"""
import tomllib
from pathlib import Path

# El archivo de configuración está en la raíz del repo.
RUTA_CONFIGURACION = Path(__file__).resolve().parent.parent / "configuracion.toml"


def buscar_reglas_y_carpeta(banco: str, es_erp: bool) -> tuple[dict, str]:
    """Recibe el banco (ej. BBVA) y si el archivo es el libro del ERP.
    Devuelve las reglas para limpiarlo (las del ERP o las del extracto de ese
    banco) y la carpeta del banco donde va el resultado.
    Si el banco no está en la configuración, frena con un error.
    """
    with open(RUTA_CONFIGURACION, "rb") as archivo:
        configuracion = tomllib.load(archivo)
    bancos = configuracion["bancos"]
    # El banco se controla siempre, también para el ERP: de él sale la carpeta.
    if banco not in bancos:
        raise ValueError(f'"{banco}" no está en la configuración. Los configurados son: {", ".join(bancos)}.')
    reglas = configuracion["erp"] if es_erp else bancos[banco]
    # El extracto de un banco trae gastos bancarios: su lista se revisa antes de usarla.
    if not es_erp:
        controlar_gastos(banco, reglas)
    return reglas, bancos[banco]["carpeta"]


def controlar_gastos(banco: str, reglas: dict) -> None:
    """Recibe un banco y sus reglas. Controla que su lista de gastos esté bien
    cargada: que exista, que no esté vacía y que no tenga códigos repetidos.
    Si algo está mal, frena con un error que dice qué corregir.
    """
    gastos = reglas.get("gastos")
    # Sin lista, ese banco no reconocería ningún gasto y nadie se enteraría.
    if not isinstance(gastos, list) or not gastos:
        raise ValueError(f'a "{banco}" le falta la lista de gastos (o está vacía) en configuracion.toml.')
    # Un código repetido suele ser un error al tipear: puede faltar el que se quería agregar.
    repetidos = sorted({codigo for codigo in gastos if gastos.count(codigo) > 1})
    if repetidos:
        raise ValueError(f'en la lista de gastos de "{banco}" hay códigos repetidos: {", ".join(repetidos)}.')


def es_gasto(codigo: str, reglas: dict) -> bool:
    """Recibe el Código de una fila y las reglas de su banco.
    Devuelve True si ese Código está en la lista de gastos del banco.
    La comparación es exacta: "015" no es lo mismo que "15", ni "IVA" que "iva".
    """
    return codigo in reglas["gastos"]
