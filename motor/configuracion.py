"""Antes de convertir: trae de configuracion.toml las reglas del documento a limpiar.

Cada banco tiene su sección (las reglas de su extracto y su carpeta de salida);
el libro del ERP tiene una sola sección, igual para todas las cuentas.
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
    return reglas, bancos[banco]["carpeta"]
