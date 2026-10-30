# Conciliación v3 — documentos a cuatro columnas

Etapa 1 de la conciliación bancaria. Convierte un documento (el extracto de un
banco o el libro del ERP de esa cuenta) en un Excel con cuatro columnas:
**Fecha, Código, Descripción y Monto**. Crédito en positivo, débito en
negativo. Sin IA: todo son reglas fijas, escritas en `configuracion.toml`.

El cruce entre banco y sistema es la etapa 2 y va en otro repo
(en GitHub "Conciliador", carpeta local "conciliacion v4"), que lee los
archivos que deja este.

## Dónde están los datos

Los originales pueden estar en cualquier carpeta: cada corrida recibe la ruta
del archivo. Los resultados se guardan fuera del repo, en una carpeta al lado:

```
<carpeta que contiene el repo>/
  conciliacion v3/                         este repo
  conciliacion resultados/v3/
    output/<AAAA-MM>/<carpeta del banco>/  lo que escribe este repo
```

La carpeta de cada banco sale de `configuracion.toml`.

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
python convertir.py 2026-09 BBVA "ruta/extracto.xls"          el extracto del BBVA
python convertir.py 2026-09 BBVA "ruta/libro.xlsx" --erp      el libro del ERP de la cuenta BBVA
```

Cada corrida convierte un archivo: el mes, el banco, la ruta y, si es el libro
del ERP, `--erp`. El resultado queda como
`output/<mes>/<carpeta del banco>/<documento> - <nombre del original>.xlsx`,
El extracto de un banco sale con dos hojas: "Movimientos" (sin gastos
bancarios) y "Gastos bancarios". El libro del ERP sale con una sola,
"Movimientos". En pantalla sale la cantidad de filas y la suma, controladas
contra el original, y en un banco cuántas filas quedaron en cada hoja. Si algo no cierra, no se genera, se
borra el resultado anterior de ese documento y se dice por qué.

La UI llama a `convertir_documento()` (en `convertir.py`) con los mismos datos.

Para correr las pruebas: `python -m pytest` (así usa el Python del `.venv`
aunque haya otro instalado, por ejemplo el de conda).

## Mapa de carpetas

```
convertir.py           la puerta de entrada: la terminal y la función que llama la UI
configuracion.toml     las reglas de cada banco y del ERP (para el programa)
motor/                 lo que es igual para todos los documentos
  configuracion.py     trae del config las reglas y la carpeta, controla la lista de
                       gastos de cada banco y reconoce si un Código es gasto
  leer.py              abre el Excel y encuentra la tabla
  armar.py             arma Fecha, Código, Descripción y Monto
  separar.py           separa los gastos bancarios del resto (solo bancos)
  escribir.py          controla filas y suma, y escribe el Excel (una o dos hojas)
  carpetas.py          nombra el resultado, borra el viejo y avisa fechas de otro mes
documentos/            un README.md por documento: cómo viene y cómo se convierte (para personas)
  banco_bbva/
  banco_galicia/
  banco_supervielle/
  sistema_finnegans/     el libro del ERP (sirve para la cuenta de cualquier banco)
pruebas/               una prueba por documento, una de la entrada, una de los gastos,
                       una de la separación y una del control,
                       con datos inventados
CLAUDE.md              cómo se trabaja en este repo
PENDIENTES.md          lo abierto y lo hecho
```

## Mapa del flujo

El camino de un archivo desde que se corre
`python convertir.py 2026-09 BBVA "extracto.xls"` hasta que sale el Excel.
Entre paréntesis, el archivo donde está cada función.

```
main()  (convertir.py)
│  Lee lo que escribiste en la terminal: mes, banco, archivo y si es --erp.
│  (La UI se salta este paso y llama directo a convertir_documento.)
│
└─► convertir_documento()  (convertir.py)
    │
    ├─► 1. Controla que el mes tenga la forma AAAA-MM.
    │
    ├─► 2. buscar_reglas_y_carpeta()  (motor/configuracion.py)
    │      Lee configuracion.toml. Si el banco no está, frena.
    │      Devuelve las reglas (las del ERP si es --erp, si no las del banco)
    │      y la carpeta de salida del banco.
    │      └─ controlar_gastos()  si es un extracto de banco, revisa su lista de
    │                             gastos; si falta, está vacía o tiene repetidos,
    │                             frena
    │
    ├─► 3. borrar_salidas()  (motor/carpetas.py)
    │      Borra el resultado anterior de ese documento, si existía.
    │
    ├─► 4. limpiar_archivo()  (convertir.py)
    │      ├─ leer_filas()           (motor/leer.py) abre el Excel y trae las filas
    │      │                         de la primera hoja; si no puede, frena
    │      ├─ encontrar_tabla()      (motor/leer.py) busca la fila con los encabezados
    │      │    │                    de las reglas; si no está, frena: el archivo no
    │      │    │                    es el documento que se indicó
    │      │    └─ buscar_seguidas() en el ERP, toma el Debe y Haber en pesos
    │      ├─ armar_movimientos()    (motor/armar.py) recorre fila por fila:
    │      │    ├─ esta_vacia()      saltea las filas vacías
    │      │    ├─ es_ignorada()     saltea las de "ignorar" (el "Saldo Inicial")
    │      │    ├─ a_centavos()      pasa crédito y débito a centavos enteros
    │      │    ├─ a_fecha()         pasa la fecha a fecha real
    │      │    ├─ a_codigo()        toma el Código tal cual, como texto; si
    │      │    │                    viene como número, frena (perdió sus ceros)
    │      │    └─ a_texto()         toma la Descripción tal cual
    │      │    → un Movimiento por fila: fecha, código, descripción, monto
    │      ├─ separar_gastos()       (motor/separar.py) solo en el extracto de un
    │      │                         banco: recorre las filas una vez y manda cada
    │      │                         una a un solo lado: a gastos si es_gasto()
    │      │                         (motor/configuracion.py) dice que sí, a
    │      │                         movimientos si no. Cada lado mantiene el orden
    │      │                         del original. Con --erp no se separa.
    │      └─ controlar()            (motor/escribir.py) cuenta filas y suma desde el
    │                                original y compara dos veces: contra lo armado
    │                                y contra movimientos + gastos. Si no cierra,
    │                                frena y dice en qué paso (al armar o al separar)
    │      Si frena ──► no se escribe nada y el error dice qué se borró.
    │
    ├─► 5. fechas_fuera_del_mes()  (motor/carpetas.py)
    │      Cuenta filas con fecha de otro mes, sobre las dos hojas juntas.
    │      No frena ni las saca.
    │
    └─► 6. ruta_salida() + escribir_excel()  (motor/carpetas.py, motor/escribir.py)
           Escribe "output/<mes>/<carpeta del banco>/<documento> - <original>.xlsx".
           escribir_hoja() escribe cada hoja con las cuatro columnas:
           "Movimientos" y, en un banco, "Gastos bancarios" (aunque esté vacía).

Al final, main() muestra filas, suma, el reparto entre las dos hojas (en un
banco), dónde quedó y el aviso de otro mes.
```

## Decisiones

Qué se decidió, por qué, qué se descartó y dónde puede fallar. Sirve para
defender el sistema sin abrir el código.

**1. Sin IA: todo con reglas fijas.**
Por qué: el mismo archivo da siempre el mismo resultado, y cada paso se puede
verificar y explicar. Se descartó: usar IA para leer los archivos (puede dar
resultados distintos y es difícil de auditar). Límite: si un banco cambia su
formato, el programa no se adapta solo; frena y hay que escribir la regla nueva.

**2. Quien llama dice qué es el archivo; los encabezados lo confirman.**
Cada corrida recibe el banco y si es el libro del ERP. Los encabezados del
archivo se comparan solo contra las reglas de ese documento. Por qué: es más
simple que adivinar entre todos los documentos y no tiene el caso de
"coincide con más de uno". El nombre del archivo nunca se usa: lo pone una
persona y cambia de un mes a otro. Se descartó (era lo anterior): probar los
encabezados de todos los documentos y quedarse con el que encaja. Límite: si
el banco renombra una columna, el archivo no se confirma y frena; nunca
adivina.

**3. La tabla se busca por encabezados, no por número de fila.**
Por qué: los bancos agregan o sacan líneas de título arriba. Límites: se usa la
primera fila que tenga todos los encabezados esperados, y solo se lee la
primera hoja. Si alguien agrega una hoja adelante con la misma tabla (pasó con
un Galicia con una hoja "Gastos Bancarios" hecha a mano), se convierte esa
hoja sin aviso (ver PENDIENTES.md).

**4. Los montos se cuentan en centavos enteros.**
Por qué: los decimales en una computadora tienen errores mínimos; con enteros
la suma es exacta. Se descartó: sumar con decimales. La etapa 2 tiene que
hacer lo mismo al leer (está en el contrato del CLAUDE.md).

**5. Se controlan filas y suma contra el original; si no cierra, no se genera.**
El original se cuenta y se suma directo de las filas del Excel, sin pasar por
el resto del programa, y se compara dos veces: contra lo armado (paso armar) y,
en un banco, contra Movimientos + Gastos bancarios (paso separar). En cada una
se miran filas y suma. Si algo no cierra, el error dice en qué paso falló. Es
una sola función de control, después de separar y antes de escribir.
Por qué: ninguna fila se puede perder en silencio, y si se pierde hay que
saber dónde. Se descartó: controlar solo al final contra las dos hojas (no
dice en qué paso falló) y un control aparte después de separar (compararía
contra lo armado y no contra el original, y repite el manejo de errores).
Límites: filas y suma no detectan que al separar se pierda una fila y se
duplique otra con el mismo monto (las dos cuentas dan igual). La separación
manda cada fila a un solo lado, así que no lo puede producir, pero el control
no lo vería. No detecta un gasto que no se separó (decisión 17). Límite
importante: el control compara contra el mismo archivo que entró. Si el banco entrega un
extracto al que le faltan días, el control da bien igual. Para detectarlo hace
falta un control de saldos (saldo final − saldo inicial), que todavía no está.

**6. Si un archivo falla, se borra su resultado anterior.**
Por qué: la etapa 2 nunca tiene que cruzar un resultado viejo creyendo que es
nuevo. Se descartó: dejar el viejo con un aviso. Límite: si se corre por error
un archivo malo, se pierde el resultado bueno anterior; se recupera volviendo
a correr el original correcto.

**7. Se convierte de a un archivo; armar el par extracto + libro es de la UI.**
Por qué: la entrada queda mínima (un archivo, su banco y si es ERP) y sirve
igual para la terminal y para la UI. Se descartó (era lo anterior): recorrer
la carpeta de cada banco y exigir 1 extracto y 1 libro. Límites: el programa
no controla que el libro del ERP sea de la cuenta de ese banco; si se lo pasa
con el banco equivocado, va a la carpeta equivocada sin aviso. Un banco con
dos cuentas todavía no tiene dónde ir: hay una carpeta de salida por banco.

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

**12. Los resultados viven fuera del repo, en una carpeta al lado.**
Por qué: los archivos de un cliente nunca se suben a GitHub. Se descartó: una
ruta fija con el usuario de la computadora. Límite: el repo y "conciliacion
resultados" tienen que estar en la misma carpeta. Los originales pueden estar
en cualquier lado.

**13. Los gastos bancarios se separan en esta etapa, en una hoja aparte.**
Se decidió el 2026-10-27; antes salían incluidos y los separaba la etapa 2.
Cómo se reconocen está en la decisión 16 y cómo se separan en la 17.

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

**15. Las reglas de todos los documentos están en un solo archivo: `configuracion.toml`.**
Una sección por banco (reglas del extracto y carpeta de salida) y una para el
ERP. Por qué: agregar un banco es agregar una sección, sin tocar código; el
`motor/` no tiene nada propio de un banco. Se eligió TOML porque se lee fácil,
admite comentarios y Python lo lee sin dependencias nuevas. Se descartó: un
`reglas.py` por documento más una tabla de bancos dentro del `motor/` (era lo
anterior: había que tocar dos lugares), JSON (no admite comentarios) y Python
(es código, no configuración). Límite: el motor solo sabe leer crédito y
débito en columnas separadas; un banco con una sola columna de monto
necesitaría un cambio en el `motor/`.

**16. Los gastos bancarios se reconocen con una lista por banco en `configuracion.toml`.**
Cada banco tiene una línea `gastos` con los valores del Código que son gasto.
Una fila es gasto si su Código está en esa lista, comparado exacto ("015" no
es "15", "IVA" no es "iva"). Funciona porque el Código de cada banco ya es la
columna con la que ese banco identifica sus gastos (decisión 14). Las listas
las armó la persona que concilia; verificado con septiembre: BBVA 836,
Galicia 387, Supervielle 89, igual que la separación a mano. El ERP no tiene
lista: no tiene gastos bancarios. Antes de usar la lista de un banco, el
programa frena si falta, si está vacía o si tiene un código repetido, para
que un error al editarla a mano no pase en silencio.
Por qué: la lista es de cada banco y cambia poco; en el mismo archivo que sus
otras reglas queda versionada en git y se revisa en un PR. Se descartó: un
archivo aparte (`bancos.json` en la etapa 2, era lo anterior: la información
de un banco quedaba en dos repos), reglas por texto ("si dice IMPUESTO") que
adivinan, e IA. Límites: un gasto con un código nuevo, que no está en la
lista, no se reconoce y queda como movimiento común; si el banco cambia cómo
escribe un código (un espacio, una mayúscula), pasa lo mismo. Cómo se separan:
decisión 17.

**17. El extracto de un banco sale con dos hojas: "Movimientos" y "Gastos bancarios".**
Después de armar las filas, cada una va a una sola hoja: a "Gastos bancarios"
si es gasto (decisión 16), a "Movimientos" si no. Se recorren una sola vez, así
una fila no puede quedar en las dos ni en ninguna, y cada hoja mantiene el
orden del original. Las dos hojas tienen las mismas cuatro columnas y el mismo
formato (las escribe la misma función). La hoja de gastos está siempre,
aunque en el mes no haya ninguno: así el archivo de un banco tiene siempre dos
hojas y la etapa 2 no tiene que adivinar. El libro del ERP sale con una sola
hoja: no tiene gastos bancarios. El aviso de fechas de otro mes cuenta todas
las filas, las dos hojas juntas.
Por qué: la etapa 2 cruza solo "Movimientos" y tiene los gastos aparte para el
control final; en un mismo archivo, la información de un banco queda junta.
Se descartó: una columna que marque cada fila (cambia las cuatro columnas del
contrato y obliga a la etapa 2 a filtrar), un archivo aparte para los gastos
(un banco quedaría en dos archivos) y no crear la hoja vacía (a veces una
hoja, a veces dos). Verificado con septiembre: Movimientos + Gastos tienen las
mismas filas que antes (BBVA 609 + 836, Galicia 113 + 387, Supervielle 83 +
89), y la hoja de gastos tiene exactamente las filas que la persona que
concilia separó a mano. Límites: un gasto con un código que no está en la
lista queda en "Movimientos", y el control lo da por bueno (las filas y la
suma cierran igual). Cambia el contrato:
el Conciliador tiene que aceptar la segunda hoja.

## Documentos disponibles

| Documento | Sección en configuracion.toml | Estado |
|---|---|---|
| Extracto BBVA | `bancos.BBVA` | Funciona |
| Extracto Galicia | `bancos.Galicia` | Funciona |
| Extracto Supervielle | `bancos.Supervielle` | Funciona |
| Libro del ERP | `erp` | Funciona (con el banco de su cuenta) |

## Agregar un banco

Agregar su sección `[bancos.<Banco>]` en `configuracion.toml`, su
`documentos/<documento>/README.md` y su prueba en `pruebas/`. No hace falta
tocar el `motor/`; si hiciera falta, primero se discute.
