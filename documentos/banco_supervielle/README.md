# Extracto del Supervielle

## De dónde sale

Banca de empresas del Supervielle → movimientos de la cuenta → exportar a
Excel. Llega como `.xlsx` con una hoja, "Supervielle". El nombre del archivo
trae la cuenta y la fecha de descarga (`Movimientos_Supervielle_<cuenta>_<fecha>.xlsx`).

## Cómo viene

- La primera fila son los encabezados; no hay títulos arriba ni saldo inicial.
- Un movimiento por fila, del más nuevo al más viejo.
- Columnas: Fecha · Hora · Concepto · Detalle · Débito · Crédito · Saldo.

## Cómo se convierte

| Salida      | Sale de          | Regla                                                |
|-------------|------------------|------------------------------------------------------|
| Fecha       | Fecha            | Viene como texto `30/09/2026`; se pasa a fecha real. |
| Concepto    | Concepto         | Tal cual (`Pago Cheque de Cámara Recibida`).         |
| Descripción | Detalle          | Tal cual (`Número Cheque: 2075`). Puede venir vacía. |
| Monto       | Crédito y Débito | Crédito en positivo, débito en negativo.             |

## Condiciones

- Débito y Crédito vienen los dos en positivo, en columnas separadas; la que no
  corresponde viene en 0. El programa pone el débito en negativo.
- Cada fila tiene crédito o débito, uno solo. Si una fila trae los dos, o
  ninguno, el programa frena y dice qué fila es.
- El Detalle viene vacío en el impuesto a los débitos y créditos y en algunos
  cargos del banco.
- El número de cheque queda en la Descripción ("Número Cheque: 2075").
- No se usan: Hora y Saldo. El Saldo se va a usar para el control de saldos
  (ver PENDIENTES.md).

## Ejemplo (datos inventados)

Entra:

| Fecha      | Hora  | Concepto                       | Detalle            | Débito | Crédito |
|------------|-------|--------------------------------|--------------------|--------|---------|
| 30/09/2026 | 07:28 | CRED BCA ELECTR INTERBANC EXEN | CUENTAS PROPIAS    | 0      | 500000  |
| 29/09/2026 | 02:28 | Pago Cheque de Cámara Recibida | Número Cheque: 101 | 150000 | 0       |

Sale:

| Fecha      | Concepto                       | Descripción        | Monto        |
|------------|--------------------------------|--------------------|--------------|
| 30/09/2026 | CRED BCA ELECTR INTERBANC EXEN | CUENTAS PROPIAS    | 500.000,00   |
| 29/09/2026 | Pago Cheque de Cámara Recibida | Número Cheque: 101 | −150.000,00  |
