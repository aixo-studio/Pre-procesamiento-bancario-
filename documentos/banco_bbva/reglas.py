"""Reglas del extracto del BBVA. La explicación está en README.md, en esta carpeta."""

# La fila de encabezados de la tabla. Todo lo que está arriba son títulos.
ENCABEZADOS = ["Fecha", "Fecha Valor", "Concepto", "Codigo", "Número Documento",
               "Oficina", "Crédito", "Débito", "Detalle"]

FECHA = "Fecha"
FORMATO_FECHA = "%d-%m-%Y"  # viene como texto: 30-09-2026
CODIGO = "Codigo"  # el código del tipo de movimiento, ej. 236; viene como texto, con sus ceros
DESCRIPCION = "Detalle"
CREDITO = "Crédito"
DEBITO = "Débito"  # viene en negativo; el motor lo toma sin signo
