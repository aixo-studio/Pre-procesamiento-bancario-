"""Puerta de entrada: convierte los documentos de un mes a cuatro columnas.

Uso:
    python convertir.py 2026-09                         todo el mes
    python convertir.py 2026-09 BBVA                    un banco
    python convertir.py 2026-09 BBVA "banco BBVA.xls"   un solo archivo

Lee de  conciliacion resultados/v3/input/<mes>/<Banco>/
y deja  conciliacion resultados/v3/output/<mes>/<Banco>/<documento> - <original>.xlsx
Cada archivo se convierte por separado: si uno falla, los demás siguen.
"""
import re
import sys
from pathlib import Path

from motor.armar import armar_movimientos
from motor.carpetas import (CARPETA_DATOS, borrar_salidas, cargar_reglas, fechas_fuera_del_mes,
                            revisar_carpeta, ruta_salida)
from motor.escribir import controlar, escribir_excel
from motor.leer import encontrar_tabla


def pesos(centavos: int) -> str:
    """Recibe un importe en centavos. Lo devuelve como texto en formato argentino: 1.234.567,89"""
    return f"{centavos / 100:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def convertir_archivo(filas: list[list], documento: str):
    """Recibe las filas de un archivo y su documento. Encuentra la tabla, arma las
    cuatro columnas y controla filas y suma. Devuelve los movimientos y el resumen.
    Si algo no cierra, frena con un error.
    """
    reglas = cargar_reglas(documento)
    columnas, datos = encontrar_tabla(filas, reglas.ENCABEZADOS, getattr(reglas, "SEGUIDAS", None))
    movimientos = armar_movimientos(columnas, datos, reglas)
    return movimientos, controlar(movimientos, columnas, datos, reglas)


def convertir_banco(carpeta_entrada: Path, carpeta_salida: Path, mes: str,
                    solo_archivo: str = None) -> tuple[int, int]:
    """Recibe la carpeta de input de un banco, su carpeta de output y el mes.
    Convierte cada archivo por separado (o solo uno, si se indica) y muestra el resumen.
    Devuelve cuántos archivos se convirtieron y cuántos errores hubo.
    """
    banco = carpeta_entrada.name
    print(f"  {banco}")
    # Primero se revisa la carpeta entera: un extracto y un libro del sistema.
    try:
        reconocidos = revisar_carpeta(carpeta_entrada)
    except ValueError as error:
        print(f"    ✗ No se convirtió el banco: {error}")
        for nombre in borrar_salidas(carpeta_salida):
            print(f"      Se borró el resultado anterior: {nombre}")
        return 0, 1
    if solo_archivo:
        reconocidos = [archivo for archivo in reconocidos if archivo[0].name == solo_archivo]
        if not reconocidos:
            print(f'    ✗ No está el archivo "{solo_archivo}" en la carpeta.')
            return 0, 1
    convertidos = errores = 0
    for ruta, documento, filas in reconocidos:
        # Antes de escribir se borra el resultado anterior de este documento.
        borrados = borrar_salidas(carpeta_salida, documento)
        try:
            movimientos, resumen = convertir_archivo(filas, documento)
        except ValueError as error:
            print(f"    ✗ {documento:<18} {ruta.name}: no se generó. {error}")
            for nombre in borrados:
                print(f"      Se borró el resultado anterior: {nombre}")
            errores += 1
            continue
        carpeta_salida.mkdir(parents=True, exist_ok=True)
        escribir_excel(movimientos, ruta_salida(carpeta_salida, documento, ruta))
        ignoradas = f"({resumen['ignoradas']} ignorada{'s' if resumen['ignoradas'] != 1 else ''})" \
            if resumen["ignoradas"] else ""
        print(f"    ✓ {documento:<18} {resumen['filas']:>6} filas {ignoradas:<14} "
              f"{pesos(resumen['suma']):>18}   {ruta.name}")
        # Aviso de fechas de otro mes: no frena y no las saca.
        for otro_mes, cantidad in fechas_fuera_del_mes(movimientos, mes).items():
            print(f"      ⚠ {cantidad} fila{'s' if cantidad != 1 else ''} con fecha de {otro_mes}")
        convertidos += 1
    return convertidos, errores


def main() -> None:
    """Recibe desde la terminal el mes y, opcionalmente, el banco y el archivo.
    Convierte lo pedido y muestra el resumen. Si hubo errores, termina con error.
    """
    argumentos = sys.argv[1:]
    if not 1 <= len(argumentos) <= 3 or not re.fullmatch(r"\d{4}-\d{2}", argumentos[0]):
        sys.exit(__doc__)
    mes = argumentos[0]
    entrada_mes = CARPETA_DATOS / "input" / mes
    salida_mes = CARPETA_DATOS / "output" / mes
    if not entrada_mes.is_dir():
        sys.exit(f"No existe la carpeta {entrada_mes}")
    # Qué bancos convertir: el indicado o todas las carpetas del mes.
    if len(argumentos) >= 2:
        carpetas = [entrada_mes / argumentos[1]]
        if not carpetas[0].is_dir():
            sys.exit(f"No existe la carpeta {carpetas[0]}")
    else:
        carpetas = sorted(carpeta for carpeta in entrada_mes.iterdir() if carpeta.is_dir())
    solo_archivo = argumentos[2] if len(argumentos) == 3 else None
    print(mes)
    convertidos = errores = 0
    for carpeta in carpetas:
        hechos, fallados = convertir_banco(carpeta, salida_mes / carpeta.name, mes, solo_archivo)
        convertidos, errores = convertidos + hechos, errores + fallados
    print(f"\n{convertidos} archivo{'s' if convertidos != 1 else ''} convertido"
          f"{'s' if convertidos != 1 else ''}, {errores} con error.")
    if errores:
        sys.exit(1)


if __name__ == "__main__":
    main()
