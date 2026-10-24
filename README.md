# Conciliación v3 — documentos a cuatro columnas

Etapa 1 de la conciliación bancaria. Convierte cada documento del mes (el
extracto de un banco o el libro del sistema financiero) en un Excel con cuatro
columnas: **Fecha, Código, Descripción y Monto**. Crédito en positivo,
débito en negativo. Sin IA: todo son reglas fijas en código.

El cruce entre banco y sistema es la etapa 2 y va en otro repo
(en GitHub "Conciliador", carpeta local "conciliacion v4"), que lee los
archivos que deja este.

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
  armar.py             arma Fecha, Código, Descripción y Monto
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
        │      │    ├─ a_codigo()        toma el Código tal cual, como texto; si
        │      │    │                    viene como número, frena (perdió sus ceros)
        │      │    └─ a_texto()         toma la Descripción tal cual
        │      │    → un Movimiento por fila: fecha, código, descripción, monto
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

## Decisiones

Qué se decidió, por qué, qué se descartó y dónde puede fallar. Sirve para
defender el sistema sin abrir el código.

**1. Sin IA: todo con reglas fijas.**
Por qué: el mismo archivo da siempre el mismo resultado, y cada paso se puede
verificar y explicar. Se descartó: usar IA para leer los archivos (puede dar
resultados distintos y es difícil de auditar). Límite: si un banco cambia su
formato, el programa no se adapta solo; frena y hay que escribir la regla nueva.

**2. Cada archivo se reconoce por sus encabezados, no por su nombre.**
Por qué: el nombre lo pone una persona, cambia de un mes a otro y puede traer
el nombre del cliente. Se descartó: reconocer por nombre o pedir que se
indique a mano. Límite: si el banco renombra una columna, el archivo no se
reconoce y frena; nunca adivina.

**3. La tabla se busca por encabezados, no por número de fila.**
Por qué: los bancos agregan o sacan líneas de título arriba. Límite: se usa la
primera fila que tenga todos los encabezados esperados.

**4. Los montos se cuentan en centavos enteros.**
Por qué: los decimales en una computadora tienen errores mínimos; con enteros
la suma es exacta. Se descartó: sumar con decimales. La etapa 2 tiene que
hacer lo mismo al leer (está en el contrato del CLAUDE.md).

**5. Se controlan filas y suma contra el original; si no cierra, no se genera.**
Por qué: ninguna fila se puede perder en silencio. Límite importante: el
control compara contra el mismo archivo que entró. Si el banco entrega un
extracto al que le faltan días, el control da bien igual. Para detectarlo hace
falta un control de saldos (saldo final − saldo inicial), que todavía no está.

**6. Si un archivo falla, se borra su resultado anterior.**
Por qué: la etapa 2 nunca tiene que cruzar un resultado viejo creyendo que es
nuevo. Se descartó: dejar el viejo con un aviso. Límite: si se corre por error
un archivo malo, se pierde el resultado bueno anterior; se recupera volviendo
a correr el original correcto.

**7. En cada carpeta de banco va exactamente 1 extracto y 1 libro del sistema.**
Por qué: la etapa 2 cruza de a pares; con dos extractos no sabría cuál usar.
Límite: un banco con dos cuentas no entra en una sola carpeta, y hoy el nombre
de la carpeta tiene que ser el del banco (BBVA, Galicia, Supervielle).

**8. Las fechas de otro mes se avisan, pero no frenan ni se sacan.**
Por qué: pueden ser válidas (un movimiento del 31 registrado el 1); decidir qué
hacer con ellas no es de esta etapa. Límite: el aviso no detecta un mes
incompleto (ver la decisión 5).

**9. En el libro del sistema, el Debe y Haber en pesos se toman por su lugar.**
Por qué: el libro trae dos pares con el mismo nombre, uno en pesos y otro en
dólares. El de pesos es el que está entre Descripción y Documento. Se
descartó: tomar el primero que aparece. Límite: si el sistema cambia el orden
de esas columnas, el programa frena en vez de usar los dólares.

**10. El saldo inicial se ignora; si trae monto, frena.**
Por qué: no es un movimiento. Se reconoce por el texto "Saldo Inicial". Límite:
si el sistema cambia ese texto, la fila no se ignora y el programa frena
porque no tiene monto; no pasa en silencio.

**11. Las fechas se guardan como fecha real, no como texto.**
Por qué: un texto como "01/09/2026" se lee distinto según la configuración de
la computadora; una fecha real es la misma en cualquier lado.

**12. Los datos viven fuera del repo, en una carpeta al lado.**
Por qué: los archivos de un cliente nunca se suben a GitHub. Se descartó: una
ruta fija con el usuario de la computadora. Límite: el repo y "conciliacion
resultados" tienen que estar en la misma carpeta.

**13. Los gastos bancarios salen incluidos.**
Por qué: separarlos es trabajo de la etapa 2, con una lista por banco. Así esta
etapa entrega el documento entero y la suma cierra contra el original.

**14. La segunda columna es "Código", no "Concepto".**
Por qué: cada banco identifica sus gastos con una columna distinta (BBVA:
Codigo; Galicia: Grupo de Conceptos; Supervielle: Concepto; sistema: Tipo de
documento). Se toma el valor puro de esa columna, sin mezclar, con un nombre
igual para todos. Verificado con septiembre: con la lista de cada banco se
separan exactamente los gastos que se habían separado a mano (BBVA 836,
Galicia 387, Supervielle 89). Se descartó: el Concepto, que en el BBVA mezcla
el tipo con otros datos. Límites: en el BBVA el texto del Concepto (con el
CUIT o la referencia del cheque) ya no sale en el resultado. Si el Código
llega como número (por ejemplo, si alguien abrió y guardó el archivo en
Excel), "005" pudo quedar en 5: el archivo no se genera y se pide bajarlo de
nuevo del banco.

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
