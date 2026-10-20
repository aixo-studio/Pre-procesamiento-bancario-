"""Reglas del libro del sistema financiero (Finnegans). Sirven para la cuenta de
cualquier banco. La explicación está en README.md, en esta carpeta."""

# La fila de encabezados de la tabla (es la primera fila del archivo).
ENCABEZADOS = ["Año - mes", "Codigo cuenta", "Cuenta", "Fecha", "Comprobante",
               "Descripción", "Debe", "Haber", "Documento", "Tipo de documento"]

FECHA = "Fecha"
FORMATO_FECHA = None  # viene como fecha real de Excel, no como texto
CODIGO = "Tipo de documento"  # ej. Orden de pago, Recibo de Cobranzas
DESCRIPCION = "Descripción"
CREDITO = "Debe"   # plata que entra al banco
DEBITO = "Haber"   # plata que sale del banco

# "Debe" y "Haber" aparecen dos veces: un par en pesos y otro en dólares.
# El de pesos es el que está entre Descripción y Documento. Si esas cuatro
# columnas no vienen juntas y en este orden, el programa frena.
SEGUIDAS = ["Descripción", "Debe", "Haber", "Documento"]

# Filas que no son movimientos. Si alguna tuviera monto, el programa frena.
IGNORAR = {"Documento": "Saldo Inicial"}
