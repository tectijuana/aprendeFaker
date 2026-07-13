// Práctica LI-02 — Caja de kiosco: parseo y validación de stdin en ARM64
// Plantilla del alumno.
//
// Tu programa debe: 1) leer líneas de stdin (terminadas en \n),
//                   2) validar: puros dígitos '0'-'9', no vacía, valor ≤ 4294967295,
//                   3) acumular las válidas en 64 BITS (la suma total no cabe en 32),
//                   4) al EOF escribir UNA línea: "<validas> <suma>\n" en decimal,
//                   5) exit(0).
//
// Pistas clave:
//   - dígito: cmp w, #'0' / cmp w, #'9'  →  valor: sub w, w, #'0'
//   - acumular: madd x_val, x_val, x_diez, x_digito   (val = val*10 + d)
//   - overflow de 32 bits: si x_val > 0xFFFFFFFF la línea es inválida
//   - imprimir decimal: divide entre 10 con udiv/msub y arma los dígitos
//     de atrás hacia adelante en un buffer (el inverso de parsear).
//
// Compilar y verificar:  make && make verificar

    .data
buffer:     .space 4096
resultado:  .space 48            // aquí armas "<validas> <suma>\n"

    .text
    .global _start

_start:
lazo_lectura:
    // read(0, buffer, 4096)
    mov     x8, #63
    mov     x0, #0
    ldr     x1, =buffer
    mov     x2, #4096
    svc     #0
    cbz     x0, corte_de_caja    // EOF → reporta

    // ------------------------------------------------------------------
    // TODO 1: recorre los x0 bytes; cada '\n' cierra una línea.
    // TODO 2: valida y convierte la línea a número (ver pistas arriba).
    // TODO 3: si es válida: contador++ y suma (64 bits) += valor.
    // ------------------------------------------------------------------

    b       lazo_lectura

corte_de_caja:
    // ------------------------------------------------------------------
    // TODO 4: convierte contador y suma a decimal ASCII en `resultado`
    //         con el formato exacto "<validas> <suma>\n" y escríbelo:
    //         write(1, resultado, longitud)
    // ------------------------------------------------------------------

    mov     x8, #93              // exit(0)
    mov     x0, #0
    svc     #0
