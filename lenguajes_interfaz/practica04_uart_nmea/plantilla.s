// Práctica LI-04 — Validador de tramas NMEA (GPS) en ARM64 (AArch64)
// Plantilla del alumno.
//
// Tu programa debe: 1) leer tramas de stdin (una por línea, terminadas en \r\n),
//                   2) calcular el XOR de los bytes entre '$' y '*' (exclusive),
//                   3) compararlo con los 2 dígitos hex declarados tras '*',
//                   4) escribir a stdout SOLO las tramas válidas (completas, con \r\n),
//                   5) terminar con exit(0) al llegar EOF (read devuelve 0).
//
// Compilar y verificar:  make && make verificar
// Con UART virtual:      ver README (socat crea el par /dev/pts/N)

    .data
buffer:     .space 4096          // llegan bytes crudos; puede haber varias tramas
linea:      .space 128           // arma aquí la trama en curso

    .text
    .global _start

_start:
lazo_lectura:
    // read(0, buffer, 4096)
    mov     x8, #63              // syscall read
    mov     x0, #0               // fd 0 = stdin (o el pty de la UART)
    ldr     x1, =buffer
    mov     x2, #4096
    svc     #0
    cbz     x0, fin              // read devolvió 0 → EOF

    // ------------------------------------------------------------------
    // TODO 1: recorre los x0 bytes recibidos armando líneas en `linea`
    //         (una trama termina en 0x0D 0x0A — DOS bytes).
    // TODO 2: por cada línea completa, calcula el checksum:
    //         cs = 0; por cada byte entre '$' y '*': eor w_cs, w_cs, w_byte
    // TODO 3: convierte los 2 caracteres hex tras '*' a un número
    //         ('0'-'9' resta 0x30; 'A'-'F' resta 0x37) y compara con cs.
    // TODO 4: si coincide, escribe la trama completa con write(1, linea, len).
    // ------------------------------------------------------------------

    b       lazo_lectura

fin:
    mov     x8, #93              // syscall exit
    mov     x0, #0
    svc     #0
