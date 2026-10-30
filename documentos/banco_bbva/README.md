# Extracto del BBVA

## De dónde sale

Banca de empresas del BBVA → Movimientos Históricos → exportar a Excel.
Llega como `.xls` (el formato viejo de Excel), con una sola hoja:
"Movimientos Históricos".

## Cómo viene

- Arriba hay unas filas de título (empresa, cuenta, sucursal, saldo y período)
  y una fila vacía. No son movimientos y se ignoran.
- Después viene la fila de encabezados y debajo un movimiento por fila.
- Columnas: Fecha · Fecha Valor · Concepto · Codigo · Número Documento ·
  Oficina · Crédito · Débito · Detalle. Al final hay una columna sin nombre
  que a veces dice "Saldo Disponible: …".

## Cómo se convierte

| Salida      | Sale de          | Regla                                                  |
|-------------|------------------|--------------------------------------------------------|
| Fecha       | Fecha            | Viene como texto `30-09-2026`; se pasa a fecha real.   |
| Código      | Codigo           | Tal cual, como texto y con sus ceros (`005`, `236`).   |
| Descripción | Detalle          | Tal cual. Muchas veces viene vacía y queda vacía.      |
| Monto       | Crédito y Débito | Crédito en positivo, débito en negativo.               |

**Por qué el Código sale de "Codigo" y no de "Concepto":** "Codigo" es un
número corto que identifica el tipo de movimiento (por ejemplo `236` es el
IVA) y alcanza solo para reconocer los gastos bancarios en la etapa 2. El
"Concepto" mezcla el tipo con otros datos (`TRANSFERENCI 20111111112` trae el
CUIT), así que no sirve para comparar contra una lista.

## Gastos bancarios

Son gasto las filas cuyo Código está en la lista `gastos` del BBVA en
`configuracion.toml`: 20 códigos (`015`, `030`, … `236` es el IVA, … `882`).
La lista la armó la persona que concilia. Se compara exacto, con los ceros.
Verificado con septiembre 2026: 836 filas. Salen en la hoja
"Gastos bancarios"; el resto queda en "Movimientos".

## Condiciones

- El débito ya viene con signo menos. El programa lo toma sin signo y lo pone
  negativo, así no depende de cómo venga.
- Cada fila tiene crédito o débito, uno solo. Si una fila trae los dos, o
  ninguno, el programa frena y dice qué fila es.
- "Codigo" tiene que venir como texto. Si viene como número (pasa si alguien
  abre el archivo en Excel y lo vuelve a guardar), `005` puede haber quedado
  en `5`: el programa frena y pide bajar el archivo de nuevo del banco.
- No se usan: Fecha Valor, Concepto, Número Documento, Oficina y la columna
  sin nombre. El texto del Concepto (con el CUIT o la referencia del cheque)
  no sale en el resultado.
- El número de cheque viene en "Número Documento" y no sale en el resultado.

## Ejemplo (datos inventados)

Entra:

| Fecha      | Concepto                     | Codigo | Crédito | Débito   | Detalle          |
|------------|------------------------------|--------|---------|----------|------------------|
| 30-09-2026 | CH/CLEAR.48  000000000001    | 005    |         | -150000  |                  |
| 29-09-2026 | TRANSFERENCI 20111111112     | 319    | 250000  |          | CTE 000011110001 |

Sale:

| Fecha      | Código | Descripción      | Monto        |
|------------|--------|------------------|--------------|
| 30/09/2026 | 005    |                  | −150.000,00  |
| 29/09/2026 | 319    | CTE 000011110001 | 250.000,00   |
