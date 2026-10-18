"""Antes de convertir: dónde están los archivos y qué documento es cada uno.

Los datos viven fuera del repo, en "conciliacion resultados/v3", al lado de la
carpeta del repo:
    input/<AAAA-MM>/<Banco>/    los crudos (los pone el usuario)
    output/<AAAA-MM>/<Banco>/   lo que escribe este repo

Cada archivo se reconoce por sus encabezados, nunca por su nombre.
"""
import importlib
from collections import Counter
from pathlib import Path

from motor.armar import Movimiento
from motor.leer import encontrar_tabla, leer_filas

# La carpeta de datos está al lado de la carpeta del repo.
CARPETA_DATOS = Path(__file__).resolve().parent.parent.parent / "conciliacion resultados" / "v3"

# Nombre de la carpeta de cada banco → su documento en documentos/.
BANCOS = {"BBVA": "banco_bbva", "Galicia": "banco_galicia", "Supervielle": "banco_supervielle"}

# El libro del sistema es el mismo documento para todos los bancos.
SISTEMA = "sistema_finnegans"


def cargar_reglas(documento: str):
    """Recibe el nombre de un documento (ej. banco_bbva). Devuelve su reglas.py."""
    return importlib.import_module(f"documentos.{documento}.reglas")


def es_excel(ruta: Path) -> bool:
    """Recibe una ruta. Devuelve True si es un Excel de datos. Los archivos ocultos
    y los temporales que deja Excel abierto ("~$...") no cuentan.
    """
    return (ruta.is_file() and ruta.suffix.lower() in (".xls", ".xlsx")
            and not ruta.name.startswith(("~$", ".")))


def reconocer_documento(filas: list[list], banco: str) -> str:
    """Recibe las filas de un archivo y el nombre de su carpeta de banco.
    Devuelve el documento cuyos encabezados encajan. Frena si no encaja ninguno,
    si encaja más de uno, o si es el extracto de otro banco.
    """
    encajan = []
    for documento in [*BANCOS.values(), SISTEMA]:
        # Solo se miran los encabezados; el resto de las reglas se controla al convertir.
        try:
            encontrar_tabla(filas, cargar_reglas(documento).ENCABEZADOS)
            encajan.append(documento)
        except ValueError:
            pass
    if not encajan:
        raise ValueError("no se reconoce: sus encabezados no coinciden con ningún documento.")
    if len(encajan) > 1:
        raise ValueError("coincide con más de un documento: " + ", ".join(encajan) + ".")
    documento = encajan[0]
    if documento != SISTEMA and documento != BANCOS[banco]:
        raise ValueError(f'es un extracto de {documento}, pero está en la carpeta "{banco}".')
    return documento


def revisar_carpeta(carpeta: Path) -> list[tuple[Path, str, list]]:
    """Recibe la carpeta de input de un banco. Lee y reconoce cada Excel.
    Devuelve, por archivo: su ruta, su documento y sus filas.
    Frena si el banco no es conocido o si no hay exactamente un extracto de ese
    banco y un libro del sistema.
    """
    banco = carpeta.name
    if banco not in BANCOS:
        raise ValueError(f'"{banco}" no es un banco conocido. Los conocidos son: {", ".join(BANCOS)}.')
    reconocidos = []
    for ruta in sorted(ruta for ruta in carpeta.iterdir() if es_excel(ruta)):
        # Un archivo dañado o que no es Excel de verdad no se puede abrir.
        try:
            filas = leer_filas(ruta)
        except Exception:
            raise ValueError(f"{ruta.name}: no se pudo abrir como Excel.") from None
        try:
            reconocidos.append((ruta, reconocer_documento(filas, banco), filas))
        except ValueError as error:
            raise ValueError(f"{ruta.name}: {error}") from None
    # Tiene que haber exactamente uno de cada.
    cantidades = Counter(documento for _, documento, _ in reconocidos)
    extractos, libros = cantidades[BANCOS[banco]], cantidades[SISTEMA]
    if (extractos, libros) != (1, 1):
        raise ValueError(f"tiene que haber 1 extracto del banco y 1 libro del sistema; "
                         f"hay {extractos} y {libros}.")
    return reconocidos


def ruta_salida(carpeta_salida: Path, documento: str, original: Path) -> Path:
    """Recibe la carpeta de output del banco, el documento y el archivo original.
    Devuelve dónde se guarda el resultado: "<documento> - <nombre del original>.xlsx".
    """
    return carpeta_salida / f"{documento} - {original.stem}.xlsx"


def borrar_salidas(carpeta_salida: Path, documento: str = "") -> list[str]:
    """Recibe la carpeta de output del banco y, si se indica, un documento.
    Borra los resultados anteriores (de ese documento, o todos) y devuelve sus nombres.
    Así nunca queda un resultado viejo mezclado con uno nuevo.
    """
    if not carpeta_salida.is_dir():
        return []
    borrados = []
    for ruta in sorted(carpeta_salida.glob(f"{documento} - *.xlsx" if documento else "*.xlsx")):
        ruta.unlink()
        borrados.append(ruta.name)
    return borrados


def fechas_fuera_del_mes(movimientos: list[Movimiento], mes: str) -> dict[str, int]:
    """Recibe los movimientos y el mes de la carpeta (AAAA-MM).
    Devuelve cuántas filas hay de cada otro mes, ej. {"2026-08": 3}. No saca ninguna.
    """
    otros = Counter(movimiento.fecha.strftime("%Y-%m") for movimiento in movimientos)
    otros.pop(mes, None)
    return dict(sorted(otros.items()))
