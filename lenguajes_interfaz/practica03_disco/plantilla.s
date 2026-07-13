// Práctica LI-03 — Padrón de nómina: registros binarios en disco (ARM64)
// Plantilla del alumno.
//
// Tu programa debe: 1) abrir salida/empleados.bin con la syscall openat,
//                   2) leer los registros de 32 bytes (layout en salida/layout.txt),
//                   3) encontrar el empleado ACTIVO (offset 28 == 1) con mayor
//                      salario (u32 en offset 24) — ¡ojo con la trampa!,
//                   4) escribir sus 32 bytes tal cual a stdout,
//                   5) cerrar el archivo y exit(0).
//
// Compilar y verificar:  make && make verificar

    .data
ruta:       .asciz "salida/empleados.bin"
registro:   .space 32            // registro en curso
mejor:      .space 32            // copia del mejor candidato hasta ahora

    .text
    .global _start

_start:
    // openat(AT_FDCWD, ruta, O_RDONLY)
    mov     x8, #56              // syscall openat
    mov     x0, #-100            // AT_FDCWD: ruta relativa al dir actual
    ldr     x1, =ruta
    mov     x2, #0               // O_RDONLY
    svc     #0
    // x0 = fd (negativo si falló — verifica y sal con exit(1) si es el caso)
    mov     x19, x0              // conserva el fd en un registro callee-saved

lazo_registros:
    // read(fd, registro, 32)
    mov     x8, #63
    mov     x0, x19
    ldr     x1, =registro
    mov     x2, #32
    svc     #0
    cbz     x0, reportar         // 0 bytes → fin de archivo

    // ------------------------------------------------------------------
    // TODO 1: carga activo (ldrb desde registro+28) — si es 0, ignora.
    // TODO 2: carga salario (ldr w desde registro+24) y compara SIN signo
    //         (b.hi) contra el mejor salario visto.
    // TODO 3: si supera al mejor: copia los 32 bytes de `registro` a `mejor`
    //         (4 pares ldp/stp de 16 bytes lo hacen en 4 instrucciones).
    // ------------------------------------------------------------------

    b       lazo_registros

reportar:
    // write(1, mejor, 32)
    mov     x8, #64
    mov     x0, #1
    ldr     x1, =mejor
    mov     x2, #32
    svc     #0

    // close(fd)
    mov     x8, #57
    mov     x0, x19
    svc     #0

    mov     x8, #93              // exit(0)
    mov     x0, #0
    svc     #0
