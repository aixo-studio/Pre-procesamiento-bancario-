# Pendientes

## Abierto (en orden de prioridad)

1. **Frenar si el archivo trae más de una hoja.** Hoy se lee solo la primera,
   sin aviso. Pasó con un Galicia con una hoja "Gastos Bancarios" hecha a mano
   adelante de "Movimientos": se convirtieron 3 filas en vez de 500.
2. **Verificar el Galicia con un extracto bajado directo del banco.** El de la
   referencia fue guardado de nuevo desde Excel. Con este cambio quedó sin
   verificar contra la referencia (la copia disponible tenía dos hojas).
3. **Controlar que el libro del ERP sea de la cuenta del banco indicado.** Hoy
   no se controla. Se podría usar la columna "Cuenta" del libro.
4. **Control de saldos** (saldo final − saldo inicial) para detectar un
   extracto incompleto. El Supervielle trae la columna Saldo.
5. **Bancos con una sola columna de monto** (con signo, o importe + D/C).
   Necesita un cambio en el `motor/`. Esperar a tener un extracto real.
6. **Bancos con dos cuentas:** hoy hay una carpeta de salida por banco.

## Hecho

- 2026-10-26 — Rama `documento-unico`: cada corrida convierte un archivo
  (mes, banco, ruta y `--erp`). Las reglas pasan a `configuracion.toml`. Se
  sacan el recorrido de carpetas y el reconocimiento entre todos los
  documentos. Referencia de septiembre verificada en BBVA (extracto y libro),
  Supervielle (extracto y libro) y libro del Galicia.
