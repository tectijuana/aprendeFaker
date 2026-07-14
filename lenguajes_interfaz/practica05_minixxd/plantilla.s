// Práctica LI-05 — Mini-xxd: volcado hex de stdin en ARM64 (AArch64)
// Plantilla del alumno.
//
// Formato de cada línea (EXACTO — el cmp no perdona):
//   "00000000: 3c a3 34 72 d7 fb e1 7a 01 29 38 93 32 e6 05 fb\n"
//   offset de 8 hex minúsculas, ": ", hasta 16 bytes "xx" separados por UN
//   espacio, SIN espacio final, '\n'. La última línea puede ser corta.
//
// Pistas:
//   - nibble → ascii: tabla "0123456789abcdef" e indexar con and #0xF
//   - arma cada línea completa en `linea` y haz UN write por línea
//   - el offset es de 32 bits: 8 nibbles, del más al menos significativo
//
// Compilar y verificar:  make && make verificar

    .data
hexdig:     .ascii "0123456789abcdef"
buffer:     .space 4096
linea:      .space 64             // "xxxxxxxx: " + 16*3 bytes caben de sobra

    .text
    .global _start

_start:
    mov     x20, #0               // offset acumulado

lazo_lectura:
    // read(0, buffer, 4096)
    mov     x8, #63
    mov     x0, #0
    ldr     x1, =buffer
    mov     x2, #4096
    svc     #0
    cbz     x0, fin

    // ------------------------------------------------------------------
    // TODO 1: por cada grupo de 16 bytes (o los que resten): convierte el
    //         offset x20 a 8 dígitos hex en `linea`, agrega ": ".
    // TODO 2: por cada byte: dos nibbles vía `hexdig`, y un espacio SOLO
    //         si no es el último byte de la línea.
    // TODO 3: agrega '\n', write(1, linea, longitud), avanza x20.
    // ------------------------------------------------------------------

    b       lazo_lectura

fin:
    mov     x8, #93
    mov     x0, #0
    svc     #0
