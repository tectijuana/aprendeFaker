// Práctica LI-06 — Búsqueda binaria de seriales en ARM64 (AArch64)
// Plantilla del alumno. Se ensambla junto con salida/datos.s, que exporta:
//   catalogo     200 u64 ORDENADOS ascendente
//   n_catalogo   u64
//   busquedas    24 u64 a consultar (1/3 no existen)
//   n_busquedas  u64
//
// Por cada serial de `busquedas`: búsqueda BINARIA en `catalogo` y
// write(1, &resultado, 8) donde resultado = índice (u64) o
// 0xFFFFFFFFFFFFFFFF si no existe. Luego exit(0).
//
// Pistas:
//   - lazo binario: izq=0, der=n-1; medio=(izq+der)/2 (lsr #1)
//   - elemento: ldr x, [x_base, x_medio, lsl #3]   (¡8 bytes por entrada!)
//   - compara SIN signo: b.hi / b.lo (los seriales usan los 64 bits)
//   - "no encontrado": mov x, #-1  (es 0xFFFF... en complemento a dos)
//
// Compilar y verificar:  make && make verificar

    .data
resultado:  .space 8

    .text
    .global _start

_start:
    ldr     x21, =busquedas
    ldr     x22, =n_busquedas
    ldr     x22, [x22]           // x22 = cuántas consultas
    mov     x23, #0              // consulta actual

lazo_consultas:
    cmp     x23, x22
    b.eq    fin
    ldr     x24, [x21, x23, lsl #3]   // x24 = serial buscado

    // ------------------------------------------------------------------
    // TODO: búsqueda binaria de x24 en `catalogo` (n_catalogo entradas).
    //       Deja el índice (o -1) en x0 y guárdalo en `resultado`.
    // ------------------------------------------------------------------

    // write(1, resultado, 8)
    ldr     x1, =resultado
    str     x0, [x1]
    mov     x8, #64
    mov     x0, #1
    mov     x2, #8
    svc     #0

    add     x23, x23, #1
    b       lazo_consultas

fin:
    mov     x8, #93
    mov     x0, #0
    svc     #0
