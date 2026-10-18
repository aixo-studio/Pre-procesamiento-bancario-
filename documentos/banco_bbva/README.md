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
| Concepto    | Concepto         | Tal cual.                                              |
| Descripción | Detalle          | Tal cual. Muchas veces viene vacía y queda vacía.      |
| Monto       | Crédito y Débito | Crédito en positivo, débito en negativo.               |

## Condiciones

- El débito ya viene con signo menos. El programa lo toma sin signo y lo pone
  negativo, así no depende de cómo venga.
- Cada fila tiene crédito o débito, uno solo. Si una fila trae los dos, o
  ninguno, el programa frena y dice qué fila es.
- No se usan: Fecha Valor, Codigo, Número Documento, Oficina y la columna sin
  nombre.
- El número de cheque viene en "Número Documento" y no sale en el resultado.

## Ejemplo (datos inventados)

Entra:

| Fecha      | Concepto                     | Número Documento | Crédito | Débito   | Detalle          |
|------------|------------------------------|------------------|---------|----------|------------------|
| 30-09-2026 | CH/CLEAR.48  000000000001    | 90000001         |         | -150000  |                  |
| 29-09-2026 | TRANSFERENCI 20111111112     |                  | 250000  |          | CTE 000011110001 |

Sale:

| Fecha      | Concepto                     | Descripción      | Monto        |
|------------|------------------------------|------------------|--------------|
| 30/09/2026 | CH/CLEAR.48  000000000001    |                  | −150.000,00  |
| 29/09/2026 | TRANSFERENCI 20111111112     | CTE 000011110001 | 250.000,00   |
