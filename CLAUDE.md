# CLAUDE.md — Conciliación v3 (etapa 1: documentos a cuatro columnas)

Este archivo es para Claude. Define cómo trabaja Claude en este repo junto con
Matias, de Aixo Studio: él es el usuario, aprueba cada cambio y hace los
commits y los push.

## Qué es esta etapa y dónde termina

Un programa en Python, sin IA, que recibe un documento crudo (el extracto de
un banco o el libro del sistema financiero) y devuelve un Excel con cuatro
columnas: Fecha, Código, Descripción y Monto.

Es la etapa 1 de la conciliación bancaria. Termina cuando cada documento del
mes quedó convertido en la carpeta de salida. El cruce entre banco y sistema
NO va acá: es la etapa 2, en otro repo (en GitHub "Conciliador", carpeta local
"conciliacion v4"), que arranca leyendo lo que deja este. Si un pedido es
del cruce, frenar y avisar.

Las carpetas locales y los repos de GitHub no se llaman igual:

| Carpeta local     | Repo en GitHub                                             | Etapa                             |
|-------------------|------------------------------------------------------------|-----------------------------------|
| conciliacion v3   | https://github.com/aixo-studio/Pre-procesamiento-bancario- | 1 (este repo)                     |
| conciliacion v4   | https://github.com/aixo-studio/Conciliador                 | 2 (lee lo que deja este)          |

## Cómo se trabaja

- Claude trabaja solo sobre la carpeta local del repo, en la computadora del
  usuario: ahí lee, crea y edita los archivos. Nunca clona el repo ni trabaja
  sobre una copia (en la nube o en otro lugar). Si no tiene acceso a la
  carpeta local, frena y avisa.
- Claude puede correr lo que solo verifica, sin cambiar nada: pytest y leer
  archivos, para chequear su trabajo antes de pasarlo.
- Todo lo que genera, mueve o borra archivos fuera del código que Claude edita
  (conversiones reales, crear o mover carpetas de datos, el .venv) lo corre el
  usuario. Claude le pasa cada comando listo para copiar, con qué hace y qué
  tiene que mostrar en pantalla.
- Los commits y los push los hace siempre el usuario. Claude le pasa los
  comandos y nunca los corre.
- Antes de cada push, el primer comando es `git remote -v`. Tiene que mostrar
  `https://github.com/aixo-studio/Pre-procesamiento-bancario-.git` en las dos
  líneas (fetch y push). Si muestra otro repo (por ejemplo Conciliador), no se
  pushea: se frena y se revisa.
- Primero el plan: qué se va a hacer, por qué y cómo queda el resultado. Si hay
  más de una forma, mostrar las opciones con pros y contras. No se construye
  sin el OK del usuario.
- Nada se crea, modifica ni borra sin aprobación explícita. Un paso a la vez;
  no adelantarse. Si aparece algo que cambia el alcance, frenar y avisar.
- Se trabaja solo con lo que trae el documento. Si una regla necesita datos
  que no están en el archivo, se anota en PENDIENTES.md.
- Nunca tocar la carpeta "(NO TOCAR)".
- Explicar en lenguaje claro: el usuario está aprendiendo programación.

## Poder defender lo que se entrega

Este repo es para un cliente. La regla es la "defensa en el pizarrón": Matias
tiene que poder explicar en cualquier momento, sin abrir el código, cómo
funciona el sistema y defender las decisiones que se tomaron. No hace falta
recordar nombres de funciones ni detalles de implementación. Sí tiene que
poder responder con seguridad preguntas como:

- ¿Por qué se hizo X y no Y?
- ¿Qué pasa si llega un archivo equivocado o con datos mal cargados, por error
  o a propósito?
- ¿Cómo se guardan y se comparan los datos, y por qué así?
- ¿Dónde falla o puede fallar?

Para eso Claude:

1. **Antes de construir**, explica la decisión con sus alternativas, pros y
   contras, en lenguaje claro.
2. **Al terminar cada cambio**, entrega la defensa: cómo funciona en pocas
   líneas, qué se decidió y por qué, qué pasa con datos malos y dónde falla.
3. **Anota cada decisión en el README**, en la sección "Decisiones": qué se
   decidió, por qué, qué alternativa se descartó y sus límites conocidos. Así
   se puede defender meses después.
4. **No avanza** hasta que Matias confirme que puede defender lo nuevo.

Los comentarios en el código y el mapa del flujo siguen, como apoyo para
quien lea el repo, pero no son el objetivo.

Excepción: las pruebas de concepto, demos y experimentos no siguen esta regla.
Ahí manda la velocidad.

## Dónde están los datos

Los resultados viven fuera del repo, en una carpeta al lado de él:

    <carpeta que contiene el repo>/
      conciliacion v3/                          este repo
      conciliacion resultados/v3/
        input/<AAAA-MM>/                        los crudos, por costumbre (pueden estar en otro lado)
        output/<AAAA-MM>/<carpeta del banco>/   lo que escribe este repo

Cada corrida convierte un archivo. Recibe el mes, el banco, la ruta del
archivo y, si es el libro del ERP, `--erp`. Armar el par extracto + libro de
cada cuenta es responsabilidad de quien llama (la UI). El programa nunca
modifica un original.

Cómo se corre:

    python convertir.py 2026-09 BBVA "ruta/extracto.xls"         el extracto del BBVA
    python convertir.py 2026-09 BBVA "ruta/libro.xlsx" --erp     el libro del ERP de la cuenta BBVA

## Orden del repositorio

- `convertir.py` es la puerta de entrada: la terminal (`main`) y la función
  que llama la UI (`convertir_documento`). Recibe mes, banco, archivo y si es
  el ERP, convierte y devuelve el resumen.
- `configuracion.toml` tiene las reglas de cada documento: una sección por
  banco (reglas del extracto y carpeta de salida) y una para el ERP.
- `motor/` tiene lo que es igual para todos los documentos: traer las reglas
  del config, leer, armar las cuatro columnas, controlar y escribir. No lleva
  nada propio de un banco.
- `documentos/<documento>/README.md` explica cómo viene y cómo se convierte
  ese documento, para personas. Dice lo mismo que su sección del config; si
  no, está mal.
- Agregar un banco es agregar su sección en `configuracion.toml`, su README y
  su prueba. Si para eso hay que tocar el `motor/`, frenar y avisar.
- Cada archivo hace una sola cosa. Nada de archivos sueltos ni de código para
  necesidades que todavía no existen. Menos código es mejor.

## Verificación

- `python -m pytest` antes de cada commit (así usa el Python del `.venv` y no
  el de conda). Cada regla de un documento tiene su prueba.
- Al convertir archivos reales, mostrar el resumen de cada uno: filas,
  filas ignoradas y suma contra el original.
- Referencia fija: septiembre 2026 tiene que dar exactamente esto. Si un
  cambio la mueve, frenar y avisar antes de seguir.

      BBVA         extracto 1.445 filas  −30.550.126,57 | sistema 529 filas  362.494.482,03
      Galicia      extracto   500 filas      493.725,04 | sistema  99 filas  151.123.160,45
      Supervielle  extracto   172 filas      856.523,72 | sistema  65 filas   22.508.801,85
      (en cada libro del sistema se ignora 1 fila de "Saldo Inicial")

- Lo que no se comprobó se informa como "sin verificar". Nunca presentar como
  comprobado algo que no se comprobó.
- Al terminar: qué se cambió, qué se verificó y qué quedó pendiente.

## Reglas del producto

- Sin IA. Todo lo decide el código con reglas fijas.
- Cada documento sale entero, en una sola hoja "Movimientos", con los gastos
  bancarios incluidos. Separar gastos no es de esta etapa.
- Qué columna del original va a cada columna de la salida lo define la
  sección de cada documento en `configuracion.toml`, y nada más. No se agregan
  columnas a la Descripción.
- Quien llama dice qué es el archivo (el banco y si es el ERP), nunca el
  nombre del archivo. Si el banco no está en el config, o los encabezados no
  coinciden con las reglas de ese documento, el archivo no se convierte y se
  dice por qué.
- Ninguna fila se pierde en silencio. La cantidad de filas y la suma de Monto
  tienen que cerrar contra el original; si no cierran, no se genera el archivo
  y se dice por qué.
- Si un archivo no se puede convertir, se borra su salida anterior (si
  existía) y el resumen lo dice. Así la etapa 2 nunca cruza un resultado viejo.
- El saldo inicial no es un movimiento: se saca siempre. Si un documento lo
  trae, se indica en su sección del config (`ignorar`) y el resumen lo informa.
- Si un archivo trae filas con fecha fuera del mes indicado, el resumen
  avisa cuántas y de qué mes. No frena y no las saca.
- El archivo original nunca se modifica.
- Los archivos reales de un cliente nunca se suben al repo. Las pruebas usan
  datos inventados. Ningún nombre de cliente en el código ni en la
  documentación.

## La salida es el contrato con la etapa 2

El repo de la etapa 2 (Conciliador, carpeta "conciliacion v4") lee estos
archivos tal como salen. Cualquier cambio
en esta lista rompe ese repo: antes de hacerlo, frenar y avisar.

- Carpeta: `conciliacion resultados/v3/output/<AAAA-MM>/<Banco>/` (la
  `carpeta` de cada banco en `configuracion.toml`: BBVA, Galicia, Supervielle).
- En cada carpeta de banco del output hay un archivo del banco y uno del
  sistema (que los dos estén lo asegura quien llama, la UI).
- Nombre: `<documento> - <nombre del original sin extensión>.xlsx`, donde
  `<documento>` es el `documento` de su sección del config (`banco_bbva`,
  `banco_galicia`, `banco_supervielle`, `sistema_finnegans`). Así la etapa 2
  sabe cuál es el banco y cuál el sistema.
- Una sola hoja, "Movimientos".
- Fila 1, el encabezado: Fecha · Código · Descripción · Monto, igual en los
  cuatro documentos. Debajo, un movimiento por fila, en el orden del original.
- El Código es el valor puro de la columna que identifica el tipo de
  movimiento en cada documento, sin mezclar nada. La etapa 2 lo usa para
  reconocer los gastos bancarios con una lista por banco:

      banco_bbva          Codigo               ej. 236
      banco_galicia       Grupo de Conceptos   ej. 000901 - Impuestos
      banco_supervielle   Concepto             ej. Impuesto Débitos y Créditos/DB
      sistema_finnegans   Tipo de documento    ej. Orden de pago

- Fecha: fecha real de Excel. Código y Descripción: texto (puede estar vacío).
  El Código sale tal cual, con sus ceros adelante ("005", nunca 5); si en el
  original viene como número, el archivo no se genera. Monto: número en pesos
  con dos decimales; si es redondo (sin centavos) queda guardado como entero,
  por ejemplo 250000 en vez de 250000.00, con el mismo valor. Crédito
  positivo, débito negativo. En el sistema, Debe (entra al banco) es positivo
  y Haber negativo.
- El texto del Concepto del BBVA y del Galicia ya no sale (cambio del
  2026-10-20, commit 306da11). Si la etapa 2 lo necesita, se pide un cambio de
  contrato.
- Al leer el Monto, la etapa 2 lo pasa a centavos enteros redondeando, y
  compara y suma en centavos: un decimal leído de un Excel puede venir con
  un error mínimo (1500000.2499999 en vez de 1500000.25).

## Código

- Python 3. Dependencias mínimas: `openpyxl`, `xlrd` y `pytest`.
- Nombres en español, completos y sin abreviaturas: funciones y variables en
  `snake_case`, clases en `PascalCase`, constantes en `MAYUSCULAS`.
- Los montos se controlan en centavos enteros, para que la suma no falle por
  decimales.
- Comentarios en español, cortos, que expliquen el por qué.
- Todo tiene arriba una descripción breve de lo que hace, en lenguaje simple,
  para que se entienda sin saber programar:
  - cada archivo empieza diciendo qué hace y en qué paso del proceso está;
  - cada función tiene arriba una o dos líneas: qué recibe, qué hace y qué
    devuelve;
  - cada bloque que no se entiende solo tiene arriba una línea que lo explica.
  No se comenta línea por línea lo que ya se lee en el código.

## Documentación

- README.md: qué es, cómo se usa, el mapa de carpetas, el mapa del flujo y las
  decisiones.
- documentos/<documento>/README.md: cómo viene ese documento y cómo se convierte.
- PENDIENTES.md: lo abierto, en orden de prioridad, y lo hecho con su fecha.
- No dejar documentación desactualizada. Distinguir lo hecho de lo propuesto.
