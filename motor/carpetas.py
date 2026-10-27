"""Dónde se guardan los resultados: nombrarlos, borrar los viejos y avisar fechas de otro mes.

Los resultados viven fuera del repo, en "conciliacion resultados/v3/output",
al lado de la carpeta del repo:
    output/<AAAA-MM>/<carpeta del banco>/
"""
from collections import Counter
from pathlib import Path

from motor.armar import Movimiento

# La carpeta de datos está al lado de la carpeta del repo.
CARPETA_DATOS = Path(__file__).resolve().parent.parent.parent / "conciliacion resultados" / "v3"


def ruta_salida(carpeta_salida: Path, documento: str, original: Path) -> Path:
    """Recibe la carpeta de output del banco, el documento y el archivo original.
    Devuelve dónde se guarda el resultado: "<documento> - <nombre del original>.xlsx".
    """
    return carpeta_salida / f"{documento} - {original.stem}.xlsx"


def borrar_salidas(carpeta_salida: Path, documento: str) -> list[str]:
    """Recibe la carpeta de output del banco y un documento.
    Borra los resultados anteriores de ese documento y devuelve sus nombres.
    Así nunca queda un resultado viejo mezclado con uno nuevo.
    """
    if not carpeta_salida.is_dir():
        return []
    borrados = []
    for ruta in sorted(carpeta_salida.glob(f"{documento} - *.xlsx")):
        ruta.unlink()
        borrados.append(ruta.name)
    return borrados


def fechas_fuera_del_mes(movimientos: list[Movimiento], mes: str) -> dict[str, int]:
    """Recibe los movimientos y el mes indicado (AAAA-MM).
    Devuelve cuántas filas hay de cada otro mes, ej. {"2026-08": 3}. No saca ninguna.
    """
    otros = Counter(movimiento.fecha.strftime("%Y-%m") for movimiento in movimientos)
    otros.pop(mes, None)
    return dict(sorted(otros.items()))
