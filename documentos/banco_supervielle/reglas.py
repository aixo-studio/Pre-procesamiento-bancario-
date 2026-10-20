"""Reglas del extracto del Supervielle. La explicación está en README.md, en esta carpeta."""

# La fila de encabezados de la tabla (es la primera fila del archivo).
ENCABEZADOS = ["Fecha", "Hora", "Concepto", "Detalle", "Débito", "Crédito", "Saldo"]

FECHA = "Fecha"
FORMATO_FECHA = "%d/%m/%Y"  # viene como texto: 30/09/2026
CODIGO = "Concepto"  # el tipo de movimiento, ej. Impuesto Débitos y Créditos/DB
DESCRIPCION = "Detalle"
CREDITO = "Crédito"
DEBITO = "Débito"  # viene en positivo; el motor lo pone negativo
