"""Reglas del extracto del Galicia. La explicación está en README.md, en esta carpeta."""

# La fila de encabezados de la tabla (es la primera fila del archivo).
ENCABEZADOS = ["Fecha", "Descripción", "Origen", "Débitos", "Créditos", "Grupo de Conceptos",
               "Concepto", "Número de Terminal", "Observaciones Cliente", "Número de Comprobante",
               "Leyendas Adicionales 1", "Leyendas Adicionales 2", "Leyendas Adicionales 3",
               "Leyendas Adicionales 4", "Tipo de Movimiento", "Saldo"]

FECHA = "Fecha"
FORMATO_FECHA = None  # viene como fecha real de Excel, no como texto
CONCEPTO = "Concepto"
DESCRIPCION = "Descripción"
CREDITO = "Créditos"
DEBITO = "Débitos"  # viene en positivo; el motor lo pone negativo
