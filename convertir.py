"""Puerta de entrada: limpia un documento y lo deja a cuatro columnas.

Uso:
    python convertir.py 2026-09 BBVA "extracto.xls"           el extracto del BBVA
    python convertir.py 2026-09 BBVA "libro.xlsx" --erp       el libro del ERP de la cuenta BBVA

Las reglas de cada banco y del ERP están en configuracion.toml.
El resultado queda en conciliacion resultados/v3/output/<mes>/<carpeta del banco>/
como "<documento> - <original>.xlsx".
"""
import re
import sys
from pathlib import Path

from motor.armar import armar_movimientos
from motor.carpetas import CARPETA_DATOS, borrar_salidas, fechas_fuera_del_mes, ruta_salida
from motor.configuracion import buscar_reglas_y_carpeta
from motor.escribir import controlar, escribir_excel
from motor.leer import encontrar_tabla, leer_filas
from motor.separar import separar_gastos


def pesos(centavos: int) -> str:
    """Recibe un importe en centavos. Lo devuelve como texto en formato argentino: 1.234.567,89"""
    return f"{centavos / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def limpiar_archivo(ruta_archivo: Path, reglas: dict, que_se_espera: str, es_erp: bool) -> tuple[list, list, dict]:
    """Recibe un archivo, sus reglas, qué documento se espera (para el error) y si es
    el libro del ERP. Lo abre, verifica sus encabezados, arma las cuatro columnas,
    separa los gastos bancarios (solo en el extracto de un banco) y controla todo
    contra el original. Devuelve los movimientos, los gastos (None en el ERP) y el
    resumen. Si algo no cierra, frena con un error.
    """
    # Un archivo que falta, está dañado o no es Excel de verdad no se puede abrir.
    try:
        filas = leer_filas(ruta_archivo)
    except Exception:
        raise ValueError("no se pudo abrir como Excel.") from None
    # Los encabezados confirman que el archivo es el documento que se indicó.
    try:
        columnas, datos = encontrar_tabla(filas, reglas["encabezados"], reglas.get("seguidas"))
    except ValueError as error:
        raise ValueError(f"no es {que_se_espera}. {error}") from None
    armados = armar_movimientos(columnas, datos, reglas)
    # El libro del ERP no tiene gastos bancarios: no se separa.
    if es_erp:
        return armados, None, controlar(armados, columnas, datos, reglas)
    # El extracto de un banco se separa antes de controlar, así el control revisa las dos hojas.
    movimientos, gastos = separar_gastos(armados, reglas)
    resumen = controlar(armados, columnas, datos, reglas, movimientos, gastos)
    resumen["movimientos"], resumen["gastos"] = len(movimientos), len(gastos)
    return movimientos, gastos, resumen


def convertir_documento(ruta_archivo: Path, banco: str, es_erp: bool, mes: str,
                        carpeta_output: Path = CARPETA_DATOS / "output") -> dict:
    """Recibe un archivo, su banco, si es el libro del ERP y el mes (AAAA-MM).
    Lo limpia con las reglas que le tocan, separa los gastos bancarios si es un
    extracto de banco y escribe el resultado en la carpeta de ese banco.
    Devuelve el resumen: filas, ignoradas, suma, ruta de salida, fechas de otro
    mes y, si es un banco, cuántas filas quedaron en cada hoja. Si algo falla,
    frena con un error y no deja resultado.
    """
    if not re.fullmatch(r"\d{4}-\d{2}", mes):
        raise ValueError(f'el mes "{mes}" tiene que tener la forma AAAA-MM.')
    reglas, carpeta_banco = buscar_reglas_y_carpeta(banco, es_erp)
    carpeta_salida = carpeta_output / mes / carpeta_banco
    # Primero se borra el resultado anterior: si la conversión falla, no queda uno viejo.
    borrados = borrar_salidas(carpeta_salida, reglas["documento"])
    que_se_espera = "el libro del ERP" if es_erp else f"un extracto de {banco}"
    try:
        movimientos, gastos, resumen = limpiar_archivo(ruta_archivo, reglas, que_se_espera, es_erp)
    except ValueError as error:
        aviso_borrados = "".join(f" Se borró el resultado anterior: {nombre}." for nombre in borrados)
        raise ValueError(f"{error}{aviso_borrados}") from None
    # Aviso de fechas de otro mes, sobre todas las filas (las dos hojas): no frena y no las saca.
    resumen["fuera_del_mes"] = fechas_fuera_del_mes(movimientos + (gastos or []), mes)
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    resumen["ruta_salida"] = ruta_salida(carpeta_salida, reglas["documento"], ruta_archivo)
    escribir_excel(movimientos, resumen["ruta_salida"], gastos)
    return resumen


def main() -> None:
    """Recibe desde la terminal el mes, el banco, el archivo y, si es el libro del ERP, --erp.
    Convierte el archivo y muestra el resumen. Si falla, termina con error.
    """
    argumentos = sys.argv[1:]
    es_erp = "--erp" in argumentos
    argumentos = [argumento for argumento in argumentos if argumento != "--erp"]
    if len(argumentos) != 3:
        sys.exit(__doc__)
    mes, banco, archivo = argumentos
    ruta_archivo = Path(archivo)
    try:
        resumen = convertir_documento(ruta_archivo, banco, es_erp, mes)
    except ValueError as error:
        sys.exit(f"✗ {ruta_archivo.name}: no se generó. {error}")
    ignoradas = f"({resumen['ignoradas']} ignorada{'s' if resumen['ignoradas'] != 1 else ''})" \
        if resumen["ignoradas"] else ""
    reparto = f"(Movimientos {resumen['movimientos']} · Gastos bancarios {resumen['gastos']})" \
        if "gastos" in resumen else ""
    print(f"✓ {resumen['filas']} filas {ignoradas} {pesos(resumen['suma'])} {reparto}")
    print(f"  {resumen['ruta_salida']}")
    for otro_mes, cantidad in resumen["fuera_del_mes"].items():
        print(f"  ⚠ {cantidad} fila{'s' if cantidad != 1 else ''} con fecha de {otro_mes}")


if __name__ == "__main__":
    main()
