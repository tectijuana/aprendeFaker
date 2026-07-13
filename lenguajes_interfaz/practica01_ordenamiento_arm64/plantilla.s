// Práctica 01 — Ordenamiento de enteros de 32 bits en ARM64 (AArch64)
// Plantilla del alumno. Se ensambla junto con salida/datos.s, que exporta:
//   arreglo  — n enteros de 32 bits CON signo
//   longitud — un .word con n
//
// Tu programa debe: 1) ordenar `arreglo` en memoria, ascendente,
//                   2) escribir el arreglo ordenado (crudo) a stdout,
//                   3) terminar con código de salida 0.
//
// Compilar y verificar:  make && make verificar

    .text
    .global _start

_start:
    // Cargar dirección del arreglo y su longitud.
    ldr     x0, =arreglo        // x0 = &arreglo
    ldr     x1, =longitud
    ldr     w1, [x1]            // w1 = n

    // ------------------------------------------------------------------
    // TODO: ordena los w1 enteros de 32 bits que empiezan en [x0].
    // Sugerencia: burbuja con dos lazos; carga con ldr wX, [x0, offset]
    // y compara CON SIGNO (cmp + b.le / b.gt — NO b.ls / b.hi).
    // ------------------------------------------------------------------

    // Escribir el arreglo (ya ordenado) a stdout: write(1, arreglo, n*4).
    mov     x8, #64             // syscall write (AArch64)
    mov     x0, #1              // fd 1 = stdout
    ldr     x1, =arreglo        // buffer
    ldr     x2, =longitud
    ldr     w2, [x2]
    lsl     x2, x2, #2          // bytes = n * 4
    svc     #0

    // exit(0)
    mov     x8, #93             // syscall exit (AArch64)
    mov     x0, #0
    svc     #0
