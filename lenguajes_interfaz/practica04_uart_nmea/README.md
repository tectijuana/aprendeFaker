# Práctica LI-04 — Validador UART de tramas NMEA (GPS) en ARM64

**Materia:** Lenguajes de Interfaz · **Entorno:** AWS Academy, Ubuntu Server ARM64 (Graviton)

## Escenario del mundo real

Un receptor GPS transmite tramas `$GPGGA` por UART a 9600 baudios. El ruido de la
línea corrompe ~10 % de las tramas. Tu programa en assembly es el firmware receptor:
valida el checksum de cada trama y **solo deja pasar las válidas** — exactamente lo
que hace cualquier driver GPS real antes de confiar en una posición.

## Anatomía de una trama (ver `salida/layout.txt`)

```
$GPGGA,120000.00,3231.9828,N,11701.0967,W,1,06,2.3,82.6,M,-33.3,M,,*6E\r\n
│└──────────────────────────── cuerpo ──────────────────────────────┘│└┴─ checksum hex
└ inicio                                                    separador ┘   + CR LF
```

Checksum = **XOR de todos los bytes del cuerpo** (entre `$` y `*`, exclusive),
en 2 dígitos hex mayúsculos. En ARM64 el XOR es la instrucción `eor`.
Las coordenadas son un recorrido real alrededor del campus TecNM Tijuana.

## Pasos

```bash
# 1. Genera las tramas (desde la raíz del repo)
./aprendefaker.py uart --seed 2026 --n 40

# 2. Estudia una trama byte a byte
cat salida/layout.txt
xxd salida/tramas.nmea | head -5     # observa el 0d 0a al final de cada trama

# 3. Completa los TODO de plantilla.s y verifica
make verificar     # CORRECTO ✔ si tu salida es idéntica a esperado.txt
```

## Modo UART real (opcional, +20 %)

En AWS Academy no hay puerto serie físico; `socat` crea un par virtual:

```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0 &
# anota los dos /dev/pts/N que reporta, luego:
./programa < /dev/pts/A > salida.txt &     # tu firmware "escucha" la UART
cat salida/tramas.nmea > /dev/pts/B        # el "GPS" transmite
```

Tu binario no cambia: en Linux, leer una UART es el mismo `read` que leer stdin —
esa es la lección de diseño de esta práctica.

## Entregable

`plantilla.s` completo, captura de `make verificar` con `CORRECTO ✔`, y (para el
extra) captura del modo UART con `socat`.

## Preguntas de reflexión

1. La trama termina en `\r\n` (0x0D 0x0A). Si solo buscas `\n`, ¿tu salida pasa el
   `cmp`? ¿Por qué?
2. El generador daña UN bit de UN byte. ¿Puede una trama corrupta pasar el checksum
   XOR? ¿Y si se dañaran DOS bytes? (Pista: piensa qué detecta y qué no detecta XOR.)
3. Un GPS a 9600 baudios envía ~1 trama/s de ~70 bytes. ¿Qué fracción del ancho de
   banda usa? ¿Hasta cuántas tramas por segundo cabrían?
