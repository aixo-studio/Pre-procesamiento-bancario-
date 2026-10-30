# Pendientes

## Abierto (en orden de prioridad)

0. **Controlar que al separar queden las mismas filas, no solo la misma
   cantidad y suma.** Hoy, si al separar se perdiera una fila y se duplicara
   otra con el mismo monto, el control no lo vería. La separación no lo puede
   producir, así que por ahora queda como límite conocido (decisión 5).
0. **El Conciliador tiene que aceptar la segunda hoja.** Hoy rechaza los
   archivos con más de una hoja: con el APR-222 el extracto de un banco sale
   con dos. Va en el repo del Conciliador.
1. **Frenar si el archivo trae más de una hoja.** Hoy se lee solo la primera,
   sin aviso. Pasó con un Galicia con una hoja "Gastos Bancarios" hecha a mano
   adelante de "Movimientos": se convirtieron 3 filas en vez de 500.
2. **Verificar el Galicia con un extracto bajado directo del banco.** El de la
   referencia fue guardado de nuevo desde Excel. El 2026-10-27 se verificó la
   rama `documento-unico` con una copia de una sola hoja: da la referencia.
3. **Controlar que el libro del ERP sea de la cuenta del banco indicado.** Hoy
   no se controla. Se podría usar la columna "Cuenta" del libro.
4. **Control de saldos** (saldo final − saldo inicial) para detectar un
   extracto incompleto. El Supervielle trae la columna Saldo.
5. **Bancos con una sola columna de monto** (con signo, o importe + D/C).
   Necesita un cambio en el `motor/`. Esperar a tener un extracto real.
6. **Bancos con dos cuentas:** hoy hay una carpeta de salida por banco.

## Hecho

- 2026-10-30 — Rama `controlar-separacion` (APR-223): la separación pasa a
  hacerse antes del control, y el control compara el original contra lo
  armado y contra Movimientos + Gastos, en filas y suma, diciendo en qué paso
  falló. Verificado con septiembre: los resultados son idénticos a los del
  APR-222.
- 2026-10-30 — Rama `separar-gastos` (APR-222): el extracto de un banco sale
  con dos hojas, "Movimientos" y "Gastos bancarios" (siempre las dos); el
  libro del ERP con una. Verificado con septiembre: mismas filas que antes
  repartidas en las dos hojas, en orden, y la hoja de gastos igual a la
  separación a mano. Los libros del ERP, idénticos.
- 2026-10-28 — Rama `gastos-bancarios` (APR-219): cada banco tiene su lista
  `gastos` en `configuracion.toml`; se controla que no falte, no esté vacía
  y no tenga repetidos, y se reconoce un gasto comparando el Código exacto.
  Verificado con septiembre: BBVA 836, Galicia 387, Supervielle 89. La
  salida no cambia (los 6 resultados son idénticos a los anteriores).
- 2026-10-26 — Rama `documento-unico`: cada corrida convierte un archivo
  (mes, banco, ruta y `--erp`). Las reglas pasan a `configuracion.toml`. Se
  sacan el recorrido de carpetas y el reconocimiento entre todos los
  documentos. Referencia de septiembre verificada en BBVA (extracto y libro),
  Supervielle (extracto y libro) y libro del Galicia.
