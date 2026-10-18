# Extracto del Galicia

## De dónde sale

Banca de empresas del Galicia → movimientos de la cuenta → exportar a Excel.
Llega como `.xlsx` con una hoja, "Movimientos".

Sin verificar: el archivo con el que se armó esto fue guardado de nuevo desde
Excel. Falta compararlo con uno bajado directo del banco (ver PENDIENTES.md).

## Cómo viene

- La primera fila son los encabezados; no hay títulos arriba ni saldo inicial.
- Un movimiento por fila, del primero al último día del mes.
- Columnas: Fecha · Descripción · Origen · Débitos · Créditos · Grupo de
  Conceptos · Concepto · Número de Terminal · Observaciones Cliente · Número
  de Comprobante · Leyendas Adicionales 1 a 4 · Tipo de Movimiento · Saldo.

## Cómo se convierte

| Salida      | Sale de             | Regla                                                     |
|-------------|---------------------|-----------------------------------------------------------|
| Fecha       | Fecha               | Viene como fecha real de Excel.                           |
| Concepto    | Concepto            | Tal cual: código y tipo de operación (`907268 - TRANSF INMED CP`). |
| Descripción | Descripción         | Tal cual (`Transf Inmed Cp`).                             |
| Monto       | Créditos y Débitos  | Crédito en positivo, débito en negativo.                  |

## Condiciones

- Débitos y Créditos vienen los dos en positivo, en columnas separadas; la que
  no corresponde viene en 0. El programa pone el débito en negativo.
- Cada fila tiene crédito o débito, uno solo. Si una fila trae los dos, o
  ninguno, el programa frena y dice qué fila es.
- En las comisiones por depósito de cheque, la Descripción trae el número de
  cheque pegado (`Com. Deposito De Cheque      475`). Se copia tal cual.
- No se usan: Origen, Grupo de Conceptos, Número de Terminal, Observaciones
  Cliente, Número de Comprobante, Leyendas Adicionales 1 a 4, Tipo de
  Movimiento y Saldo.

## Ejemplo (datos inventados)

Entra:

| Fecha      | Descripción     | Débitos | Créditos | Concepto                  |
|------------|-----------------|---------|----------|---------------------------|
| 01/09/2026 | Transf Inmed Cp | 150000  | 0        | 907268 - TRANSF INMED CP  |
| 02/09/2026 | Credito Prestamo| 0       | 800000   | 917133 - CREDITO PRESTAMO |

Sale:

| Fecha      | Concepto                  | Descripción      | Monto        |
|------------|---------------------------|------------------|--------------|
| 01/09/2026 | 907268 - TRANSF INMED CP  | Transf Inmed Cp  | −150.000,00  |
| 02/09/2026 | 917133 - CREDITO PRESTAMO | Credito Prestamo | 800.000,00   |
