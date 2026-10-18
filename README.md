# Conciliación v3 — documentos a cuatro columnas

Etapa 1 de la conciliación bancaria. Convierte cada documento del mes (el
extracto de un banco o el libro del sistema financiero) en un Excel con cuatro
columnas: **Fecha, Concepto, Descripción y Monto**. Crédito en positivo,
débito en negativo. Sin IA: todo son reglas fijas en código.

El cruce entre banco y sistema es la etapa 2 y va en otro repo
("conciliacion v4"), que lee los archivos que deja este.

## Dónde están los datos

Fuera del repo, en una carpeta al lado:

```
Documents/
  conciliacion v3/                  este repo
  conciliacion resultados/v3/
    input/<AAAA-MM>/<Banco>/        los crudos: un extracto y un libro del sistema
    output/<AAAA-MM>/<Banco>/       lo que escribe este repo
```

## Cómo se usa

La primera vez, en la terminal, dentro de esta carpeta:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Después, cada vez:

```
source .venv/bin/activate
python convertir.py 2026-09                         todo el mes
python convertir.py 2026-09 BBVA                    un banco
python convertir.py 2026-09 BBVA "extracto.xls"     un solo archivo
```

Cada archivo se convierte por separado y queda como
`output/<mes>/<Banco>/<documento> - <nombre del original>.xlsx`, con una sola
hoja, "Movimientos". En pantalla sale, por archivo, la cantidad de filas y la
suma, controladas contra el original. Si algo no cierra, ese archivo no se
genera, se borra su resultado anterior y se dice por qué; los demás siguen.

Para correr las pruebas: `pytest`

## Mapa de carpetas

```
convertir.py           la puerta de entrada: lo que se corre en la terminal
motor/                 lo que es igual para todos los documentos
  carpetas.py          dónde están los archivos y qué documento es cada uno
  leer.py              abre el Excel y encuentra la tabla
  armar.py             arma Fecha, Concepto, Descripción y Monto
  escribir.py          controla filas y suma, y escribe el Excel
documentos/            una carpeta por documento, cada una con:
  banco_bbva/            README.md  cómo viene y cómo se convierte (para personas)
  banco_galicia/         reglas.py  lo mismo, para el programa
  banco_supervielle/
  sistema_finnegans/     el libro del sistema (sirve para la cuenta de cualquier banco)
pruebas/               una prueba por documento y una de carpetas, con datos inventados
CLAUDE.md              cómo se trabaja en este repo
```

## Mapa del flujo

El camino de un archivo desde que se corre `python convertir.py 2026-09`
hasta que sale el Excel. Entre paréntesis, el archivo donde está cada función.

```
main()  (convertir.py)
│  Lee lo que escribiste en la terminal: el mes y, si los pusiste, el banco
│  y el archivo. Arma las rutas de input y output del mes.
│
└─► convertir_banco()  (convertir.py)        ← una vez por cada carpeta de banco
    │
    ├─► 1. revisar_carpeta()  (motor/carpetas.py)
    │      Revisa la carpeta del banco antes de convertir nada.
    │      ├─ es_excel()             deja solo los .xls y .xlsx (saltea ocultos y temporales)
    │      ├─ leer_filas()           (motor/leer.py) abre cada Excel y trae todas sus filas
    │      └─ reconocer_documento()  prueba los encabezados de los 4 documentos y se
    │           │                    queda con el único que encaja
    │           ├─ cargar_reglas()   trae el reglas.py de cada documento
    │           └─ encontrar_tabla() (motor/leer.py) busca la fila de encabezados
    │      Tiene que haber 1 extracto de ese banco y 1 libro del sistema.
    │      Si no ──► borrar_salidas() borra los resultados viejos del banco y sigue
    │                con el banco siguiente.
    │
    └─► Por cada uno de los 2 archivos:
        │
        ├─► 2. borrar_salidas()  (motor/carpetas.py)
        │      Borra el resultado anterior de ese documento, si existía.
        │
        ├─► 3. convertir_archivo()  (convertir.py)
        │      ├─ cargar_reglas()        trae el reglas.py del documento
        │      ├─ encontrar_tabla()      (motor/leer.py) ubica cada columna; si el
        │      │    │                    documento tiene SEGUIDAS (el libro del sistema),
        │      │    └─ buscar_seguidas() toma el Debe y Haber en pesos, no en dólares
        │      ├─ armar_movimientos()    (motor/armar.py) recorre fila por fila:
        │      │    ├─ esta_vacia()      saltea las filas vacías
        │      │    ├─ es_ignorada()     saltea las de IGNORAR (el "Saldo Inicial")
        │      │    ├─ a_centavos()      pasa crédito y débito a centavos enteros
        │      │    ├─ a_fecha()         pasa la fecha a fecha real
        │      │    └─ a_texto()         toma Concepto y Descripción tal cual
        │      │    → un Movimiento por fila: fecha, concepto, descripción, monto
        │      └─ controlar()            (motor/escribir.py) vuelve a contar filas y a
        │                                sumar desde el original; si no cierra, frena
        │      Si frena ──► no se escribe nada y se informa el error.
        │
        ├─► 4. ruta_salida() + escribir_excel()  (motor/carpetas.py, motor/escribir.py)
        │      Arma el nombre "<documento> - <original>.xlsx" y escribe la hoja
        │      "Movimientos" con las cuatro columnas.
        │
        └─► 5. fechas_fuera_del_mes()  (motor/carpetas.py)
               Cuenta filas con fecha de otro mes y lo avisa. No frena ni las saca.

Al final, main() muestra cuántos archivos se convirtieron y cuántos fallaron.
```

## Documentos disponibles

| Documento | Carpeta de banco | Estado |
|---|---|---|
| Extracto BBVA | `BBVA` | Funciona |
| Extracto Galicia | `Galicia` | Funciona |
| Extracto Supervielle | `Supervielle` | Funciona |
| Libro del sistema | cualquiera | Funciona |

## Agregar un documento

Crear una carpeta en `documentos/` con su `README.md` y su `reglas.py`, una
prueba en `pruebas/` y, si es un banco nuevo, sumarlo a la tabla `BANCOS` de
`motor/carpetas.py`. No hace falta tocar el resto del `motor/`; si hiciera
falta, primero se discute.
